"""Summarize observed test outcomes; never equate unit tests with photo quality."""
from pathlib import Path
import re, os
root = Path("results")
rows = {}
for filename in ("engine-tests.txt", "ui-tests.txt"):
    path = root / filename
    content = path.read_text(errors="replace") if path.exists() else ""
    rows[filename] = (content, re.findall(r"test result: .*", content))
groups = {
    "Xóa mụn / bảo vệ môi và mắt": ("ai_auto_retouch::", "auto_blemish::"),
    "Son môi / mặt nạ viền môi": ("ai_lipstick::",),
    "Màu, preset, HSL, tăng nét, hiệu ứng": ("photo_ai_effects::", "auto_adjust::"),
    "Pipeline tự động / hoàn tác": ("auto_workflow::",),
    "Giao diện Studio": ("photo_ai_studio", "empty_workspace_tests::"),
}
lines = ["# Báo cáo kiểm thử PhotoAI", "", "Commit: " + os.environ.get("GITHUB_SHA", "unknown"),
         "", "Kết quả dưới đây lấy từ nhật ký thực thi. Kiểm thử tổng hợp không xác nhận chất lượng chỉnh chân dung thật.", ""]
for filename, (content, summaries) in rows.items():
    lines += ["## " + filename, "", *(summaries or ["Chưa có kết quả kết thúc; không xác nhận đạt."]), ""]
lines += ["## Theo nhóm chức năng", "", "| Nhóm | Đạt | Lỗi | Bỏ qua |", "|---|---:|---:|---:|"]
all_tests = []
for content, _ in rows.values():
    all_tests += re.findall(r"^test (\S+) \.\.\. (ok|FAILED|ignored)\b", content, re.M)
for title, needles in groups.items():
    statuses = [status for name, status in all_tests if any(n in name for n in needles)]
    lines.append(f"| {title} | {statuses.count('ok')} | {statuses.count('FAILED')} | {statuses.count('ignored')} |")
lines += ["", "Các nhóm chỉ thống kê bài có tên phù hợp; số 0 không có nghĩa chức năng đã đạt.",
          "", "## Chưa chứng nhận", "",
          "- Chất lượng xóa mụn, giữ texture da, son môi trên ảnh thật nhiều điều kiện ánh sáng.",
          "- So sánh giao diện chạy thật với mẫu đã duyệt; thao tác trên MacBook 13 inch.",
          "- AI đổi quần áo, đổi nền, xóa người và tạo ảnh chưa có mô hình tích hợp.",
          "- 120 lựa chọn màu là biến thể của các look, không phải 120 LUT độc lập.",
          "- Cài đặt, mở ứng dụng và xuất ảnh hoàn chỉnh trên máy người dùng.",
          "", "Gói ứng dụng nếu được tạo chỉ là bản kiểm thử nội bộ; chưa phải bản phát hành."]
(root / "BAO-CAO-KIEM-THU.md").write_text("\n".join(lines) + "\n")
summary = os.environ.get("GITHUB_STEP_SUMMARY")
if summary:
    with open(summary, "a") as out:
        out.write("\n".join(lines) + "\n")
