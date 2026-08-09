# Changelog — Werewolf Online

Tất cả các thay đổi đáng chú ý của dự án **Werewolf Online** sẽ được ghi lại trong file này.

Phiên bản tuân theo [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.1.0-beta] — 2026-08-10

### 🚀 Tính Năng Mới & Cốt Lõi (Core Features)
- **Hệ thống Phòng & Quản lý Trò chơi (Room & Game Management):**
  - Khởi tạo hệ thống phòng chơi thời gian thực với FastAPI và WebSocket router (`/backend/ws/router.py`).
  - Xây dựng cơ chế vòng lặp trò chơi (`game.py`, `game_runner.py`) quản lý tự động các pha: Đêm (Night Actions) $\rightarrow$ Thảo luận ngày (Day Discussion) $\rightarrow$ Bỏ phiếu (Voting) $\rightarrow$ Tổng kết pha.
  - Tích hợp bộ bảo vệ quá tải server (`room_manager.py`) kiểm tra tài nguyên CPU (<85%) và RAM (<80%) trước khi tiếp nhận kết nối/tạo phòng.
- **Hệ thống Vai trò (Roles Engine):**
  - Hoàn thiện module phân vai và kỹ năng ban đầu cho Sói (Werewolves), Tiên Tri (Seer), Bảo Vệ (Bodyguard), Phù Thủy (Witch) và Dân Làng (Villagers).
  - Xây dựng cơ chế giải quyết hành động đêm (`resolver.py`) và kiểm tra điều kiện thắng thua.
- **Giao Diện Người Dùng (React Web Frontend):**
  - Xây dựng giao diện sảnh chờ (Lobby), phòng chơi (Room), và màn hình trận đấu trực tiếp (Game) với TailwindCSS.
  - Thiết kế các thành phần tương tác: Vòng tròn ghế ngồi (`SeatCircle`), Thẻ vai trò (`RoleCard`), Bảng hành động đêm (`NightActionPanel`), Khung chat (`ChatPanel`), Đếm ngược thời gian (`Timer`, `useGameTimer`) và Phủ trạng thái pha (`PhaseOverlay`).
  - Hỗ trợ làm nổi bật từ khóa/mention tên người chơi (`useMentionHighlight.js`).
- **Ứng Dụng Di Động Android:**
  - Khởi tạo kiến trúc cơ bản ứng dụng native trên Android sử dụng Kotlin và Jetpack Compose.
- **Xác thực & Cơ sở dữ liệu:**
  - Thiết lập hệ thống đăng ký/đăng nhập với JWT và mã hóa mật khẩu bcrypt (`/backend/auth/`).
  - Cấu hình schema cơ sở dữ liệu SQLite / Cloudflare D1 (`/backend/db/schema.sql`).

### 📚 Tài Liệu & Tiêu Chuẩn
- Xây dựng bộ tài liệu thiết kế toàn diện từ `00_overview_and_architecture.md` đến `09_code_style.md` trong thư mục `design/`.
- Thiết lập quy chuẩn mã nguồn, quy tắc ngôn ngữ (UI tiếng Việt, code tiếng Anh, tài liệu tiếng Việt).
