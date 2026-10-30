# PhotoAI Studio v0.7.18.4 — hồ sơ chuẩn bị phát hành

> TRẠNG THÁI: RELEASE CANDIDATE / HOLD — bản kiểm thử nội bộ. Chưa công bố bản chính thức.

## Tài khoản và nguồn
- Repository: https://github.com/vanthat545-sudo/photoai
- Nhánh kiểm thử: `ci/macos-v07184`
- Nguồn gốc: `PhotoAI-Studio-v0.7.18.4-Mac-Finder-TEST.zip`, các bản vá UI và retouch, cùng mã kiểm thử trong `ci/`.
- Mục tiêu: macOS Apple Silicon (M1), ứng dụng `.app` độc lập.

## Kết quả đã xác minh
- [x] GitHub Actions `PhotoAI macOS M1 validation` thành công tại https://github.com/vanthat545-sudo/photoai/actions/runs/41025441660 (build macOS arm64, unit tests, ảnh giao diện thực từ renderer, gói ứng dụng thử nghiệm).
- [x] Kiểm thử ứng dụng đóng gói tối thiểu (nhập PNG/JPEG, preset, undo, xuất, khởi động) từng đạt tại https://github.com/vanthat545-sudo/photoai/actions/runs/41025333487.
- [x] Xác định lỗi CI mới nhất: runner dùng Python 3.14, `scikit-image==0.25.2` không cài đặt được.
- [x] Chỉnh workflow để dùng Python 3.12 và artifact từ run 41025441660.
- [ ] Lượt kiểm thử đóng gói mới sau sửa Python phải đạt đầy đủ; đối chiếu chính xác log và kết quả trước khi đánh dấu.
- [ ] Kiểm thử mở/cài bản `.app` trên MacBook M1 thực tế.

## Kiểm thử sản phẩm bắt buộc trước khi phát hành chính thức
- [ ] Kiểm thử xóa mụn trên bộ ảnh chân dung thật; không làm thay đổi mắt, môi; giữ texture và không lem biên.
- [ ] Đánh giá bằng mắt ảnh trước/sau; unit tests không chứng minh chất lượng retouch.
- [ ] Xác nhận AI Router nổi, thu gọn, kéo thả và đủ 3 tab đúng giao diện đã duyệt.
- [ ] Với mỗi nút Router: chạy pipeline thực hoặc hiển thị rõ chưa hỗ trợ, báo thành công/thất bại chính xác.
- [ ] Phân loại preset độc lập và các biến thể màu, không quảng bá nhầm 120 LUT riêng biệt.
- [ ] Xác nhận icon app đã duyệt trong Finder, Dock và Launchpad; icon Router nội bộ là riêng biệt.
- [ ] Xác nhận update không xóa ảnh, preset cá nhân, dự án và cấu hình trước đây.
- [ ] Kiểm tra xuất PNG/JPG chất lượng gốc, hoàn tác, trạng thái lỗi và lưu đường dẫn dự án.
- [ ] Tính năng chưa có backend/mô hình AI thực (thay trang phục, đổi nền, xóa người, tạo ảnh) phải được ghi rõ hoặc vô hiệu hóa, không quảng bá là hoàn thiện.
- [ ] Kiểm tra đóng gói, code signature, Gatekeeper/notarization nếu phát hành đại trà; không dùng tên bản thử nghiệm như bản chính thức.
- [ ] Đặt artifact bền vững trong GitHub Releases khi thực sự đủ điều kiện; workflow artifacts chỉ lưu 14 ngày.

## Quy tắc phát hành
- Không công bố bản chính thức, không đánh dấu 100% và không gửi file cài như bản hoàn chỉnh nếu các mục bắt buộc chưa qua kiểm thử.
- Nếu cần đưa ra cho cá nhân thử nghiệm sớm, gắn rõ nhãn **TEST/RC** và chưa đạt nghiệm thu.
