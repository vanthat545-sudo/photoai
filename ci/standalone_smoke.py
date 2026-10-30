"""Exercise the packaged Mac application, not a separately built test binary.

Synthetic image checks verify plumbing and undo, not portrait retouch quality.
"""
import hashlib
import json
import os
from pathlib import Path
import secrets
import socket
import struct
import subprocess
import sys
import time
import zlib


def fixture(path):
    def chunk(kind, data):
        return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind + data))
    width, height = 256, 192
    rows = b''.join(b'\0' + bytes(v for x in range(width) for v in (x, y, (x+y)//2, 255)) for y in range(height))
    path.write_bytes(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(rows)) + chunk(b'IEND', b''))


def main():
    app = Path(sys.argv[1]).resolve()
    root = Path('results/smoke').resolve()
    root.mkdir(parents=True, exist_ok=True)
    fixture(root / 'input.png')
    binary = app / 'Contents/MacOS/photocraft'
    helper = app / 'Contents/MacOS/PhotoAIVision'
    subprocess.run(['codesign', '--verify', '--strict', '--deep', str(app)], check=True)
    checks = []
    bad = subprocess.run([str(helper)], input=b'bad', capture_output=True, timeout=15)
    assert bad.returncode != 0 and json.loads(bad.stdout).get('error'), 'Vision must reject malformed pixels'
    checks.append('Vision rejects invalid image input')
    token = secrets.token_hex(32)
    with socket.socket() as reserve:
        reserve.bind(('127.0.0.1', 0))
        port = reserve.getsockname()[1]
    env = dict(os.environ, PHOTOCRAFT_CONFIG_DIR=str(root / 'config'))
    log = (root / 'app.log').open('wb')
    process = subprocess.Popen([str(binary), '--safe-gpu', '--control', str(port), '--control-token', token,
                                '--automation-read-root', str(root), '--automation-write-root', str(root)],
                               env=env, stdout=log, stderr=subprocess.STDOUT)
    connection = None
    try:
        deadline = time.monotonic() + 60
        while time.monotonic() < deadline:
            if process.poll() is not None:
                raise RuntimeError('Packaged application exited before startup')
            try:
                connection = socket.create_connection(('127.0.0.1', port), timeout=2)
                break
            except OSError:
                time.sleep(0.5)
        if connection is None:
            raise TimeoutError('Packaged application did not start in 60 seconds')
        connection.settimeout(65)
        stream = connection.makefile('rwb')
        request_id = 0

        def call(method, params=None, expected=True):
            nonlocal request_id
            request_id += 1
            stream.write((json.dumps(dict(id=request_id, method=method, params=params or {})) + '\n').encode())
            stream.flush()
            reply = json.loads(stream.readline())
            assert reply.get('id') == request_id and reply.get('ok') is expected, f'{method}: {reply}'
            return reply.get('result') if expected else reply

        def command(name, params=None, expected=True):
            return call('engine.execute', dict(command=name, params=params or {}), expected)

        def save(name):
            call('app.save', dict(path=name))
            data = (root / name).read_bytes()
            assert len(data) > 100, 'Export is empty'
            return hashlib.sha256(data).hexdigest()

        call('auth', dict(token=token))
        call('ui.inspect')
        checks.append('Packaged app starts and responds')
        call('app.open', dict(path='input.png'))
        baseline = save('baseline.png')
        checks.append('PNG import and export')
        command('paint.photoAiEffects', dict(effect='preset', preset='warm', strength=70, target='pixels'))
        changed = save('warm.png')
        assert changed != baseline, 'Preset did not change exported pixels'
        command('edit.undo')
        assert save('undo.png') == baseline, 'Undo did not restore exported image'
        checks.append('Warm preset changes pixels; undo restores exact PNG')
        command('paint.photoAiEffects', dict(effect='preset', preset='invalid-look', strength=70), expected=False)
        assert save('invalid-unchanged.png') == baseline, 'Rejected command modified image'
        checks.append('Invalid preset reports failure without modifying image')
        no_face = command('paint.aiAutoRetouch')
        assert no_face.get('faces') == 0 and no_face.get('noChange') is True, 'No-face retouch must report no change'
        (root / 'no-face-response.json').write_text(json.dumps(no_face, ensure_ascii=False, indent=2))
        assert save('no-face-unchanged.png') == baseline, 'No-face retouch modified image'
        checks.append('Retouch reports no face and no change without modifying pixels')
        save('export.jpg')
        assert (root / 'export.jpg').read_bytes().startswith(b'\xff\xd8'), 'JPEG signature missing'
        call('app.open', dict(path='export.jpg'))
        checks.append('JPEG export and reimport')
        call('ui.screenshot', dict(path='running-app.png'))
        checks.append('Capture actual running native app')
        call('app.quit')
        assert process.wait(timeout=20) == 0, 'Application did not exit cleanly'
        checks.append('Clean app shutdown')
    finally:
        if connection:
            connection.close()
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
        log.close()
        (root / 'checks.json').write_text(json.dumps(checks, ensure_ascii=False, indent=2))
    print(json.dumps(dict(passed=checks, scope='Synthetic smoke test; portrait quality remains unverified'), indent=2))


if __name__ == '__main__':
    main()
