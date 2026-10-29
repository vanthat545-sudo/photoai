"""Build an internal standalone app without changing any installed application."""
import os, plistlib, shutil, subprocess
from pathlib import Path
source = Path(os.environ["SOURCE"])
app = Path("results/PhotoAI-Retouch-Validation.app")
mac = app / "Contents/MacOS"
res = app / "Contents/Resources"
mac.mkdir(parents=True, exist_ok=True)
res.mkdir(parents=True, exist_ok=True)
for name in ("photocraft", "PhotoAIVision"):
    target = mac / name
    shutil.copy2(source / "target/debug" / name, target)
    target.chmod(0o755)
shutil.copy2(source / "assets/app-icon/PhotoAI-Pro.icns", res / "PhotoAI-Pro.icns")
info = dict(CFBundleExecutable="photocraft", CFBundleIdentifier="local.photoai.retouch.validation",
            CFBundleName="PhotoAI Retouch Validation", CFBundleDisplayName="PhotoAI Retouch Validation",
            CFBundleShortVersionString="0.7.18.4", CFBundleVersion="4", CFBundlePackageType="APPL",
            CFBundleIconFile="PhotoAI-Pro.icns", LSMinimumSystemVersion="11.0", NSHighResolutionCapable=True)
with (app / "Contents/Info.plist").open("wb") as out:
    plistlib.dump(info, out)
for target in (mac / "PhotoAIVision", mac / "photocraft", app):
    subprocess.run(["codesign", "--force", "--sign", "-", str(target)], check=True)
subprocess.run(["codesign", "--verify", "--strict", "--deep", str(app)], check=True)
subprocess.run(["ditto", "-c", "-k", "--sequesterRsrc", "--keepParent", str(app),
                "results/PhotoAI-Retouch-Validation-Mac-ARM64.zip"], check=True)
shutil.rmtree(app)
