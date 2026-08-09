<a id="readme-top"></a>

<div align="center">
  <a href="https://github.com/Grizmo2610/WereWolf-Online">
    <img src="frontend/src/assets/images/Werewolf-logo.png" alt="Logo" width="80" height="80">
  </a>

<h3 align="center">Werewolf Online (Sói Già Online)</h3>

  <p align="center">
    Trò chơi Ma Sói trực tuyến thời gian thực (Real-time Multiplayer Social Deduction Party Game)
    <br />
    <a href="design/00_overview_and_architecture.md"><strong>Khám phá tài liệu thiết kế »</strong></a>
    <br />
    <br />
    <a href="https://github.com/Grizmo2610/WereWolf-Online">Xem Demo</a>
    &middot;
    <a href="https://github.com/Grizmo2610/WereWolf-Online/issues">Báo lỗi</a>
    &middot;
    <a href="https://github.com/Grizmo2610/WereWolf-Online/issues">Đề xuất tính năng</a>
  </p>
</div>

---

## 📖 Giới Thiệu Dự Án

**Werewolf Online** là tựa game Ma Sói trực tuyến đa nền tảng thời gian thực, nơi người chơi vào vai dân làng hoặc bầy sói tham gia suy luận, biện luận và bỏ phiếu loại trừ thế lực hắc ám.

Dự án được xây dựng với kiến trúc hiện đại và tách biệt rõ ràng:
1. **Backend (`/backend`)**: FastAPI (Python) & WebSocket server hiệu năng cao quản lý phòng chơi, vòng lặp trò chơi và phân quyền bảo mật.
2. **Frontend (`/frontend`)**: Giao diện web hiện đại xây dựng bằng React 18, Vite, Tailwind CSS và Zustand state management.
3. **Android App (`/android`)**: Ứng dụng di động native viết bằng Kotlin và Jetpack Compose.
4. **Tài liệu thiết kế (`/design`)**: Bộ tài liệu đặc tả chi tiết từ kiến trúc hệ thống, cơ chế game, database, giao thức WebSocket cho đến UI/UX.

---

## ✨ Tính Năng Chính

* **Đa người chơi thời gian thực (Real-time Multiplayer):** Đồng bộ hóa tức thì các hành động đêm, thảo luận ngày và bỏ phiếu qua WebSocket.
* **Hệ thống Vai trò phong phú:** Sói, Tiên Tri, Bảo Vệ, Phù Thủy, Dân Làng và các vai trò đặc biệt khác.
* **Chu kỳ Ngày / Đêm tự động:** Chuyển đổi pha mượt mà với bộ đếm thời gian (timer bounds) và cơ chế bỏ phiếu linh hoạt.
* **Bảo vệ Quá tải Server (`room_manager.py`):** Kiểm tra tài nguyên CPU (<85%) và RAM (<80%) trước khi cho phép tạo phòng hoặc kết nối mới.
* **Đa nền tảng:** Hỗ trợ trình duyệt web và ứng dụng Android.

---

## 📚 Tài Liệu Hệ Thống

Toàn bộ tài liệu thiết kế chi tiết nằm trong thư mục `design/`:
* 🏛️ [Tổng quan & Kiến trúc](design/00_overview_and_architecture.md)
* 🐺 [Nhân vật & Vai trò](design/01_characters.md)
* 📜 [Kịch bản & Luật chơi](design/02_scenarios.md)
* ⚙️ [Động cơ Trò chơi (Game Engine)](design/03_game_engine.md)
* 🔐 [Xác thực & Bảo mật (Auth)](design/04_auth.md)
* 🗄️ [Cấu trúc Cơ sở dữ liệu](design/05_database.md)
* 🔌 [Giao thức WebSocket](design/06_websocket.md)
* 🎨 [Thiết kế UI/UX](design/07_ui.md)
* ☁️ [Hạ tầng & Triển khai (Infrastructure)](design/08_infrastructure.md)
* 📝 [Quy chuẩn Mã nguồn (Code Style)](design/09_code_style.md)

---

## 🚀 Hướng Dẫn Cài Đặt & Chạy Ứng Dụng

### Yêu Cầu Hệ Thống
* Python 3.10+
* Node.js 18+ & npm / yarn
* Android Studio (Flamingo hoặc mới hơn) kèm Android SDK (nếu chạy bản Android)

### 1. Clone Kho Mã Nguồn
```bash
git clone https://github.com/Grizmo2610/WereWolf-Online.git
cd WereWolf-Online
```

### 2. Chạy Backend (Python FastAPI)
Mở terminal tại thư mục gốc và chạy các lệnh sau:
```bash
cd backend
python -m venv venv

# Trên Windows (PowerShell/CMD):
venv\Scripts\activate

# Trên macOS / Linux:
# source venv/bin/activate

# Cài đặt thư viện phụ thuộc
pip install -r requirements.txt

# Khởi động server FastAPI (chạy port 8000)
python -m uvicorn main:app --reload --port 8000
```
Server backend sẽ chạy tại: `http://localhost:8000` (Tài liệu API Swagger tại `http://localhost:8000/docs`).

### 3. Chạy Frontend (React Web Client)
Mở một terminal mới và chạy các lệnh sau:
```bash
cd frontend

# Cài đặt các gói npm
npm install

# Tạo file cấu hình môi trường (.env)
echo "VITE_API_BASE=http://localhost:8000" > .env

# Chạy ứng dụng web ở chế độ phát triển (Development)
npm run dev
```
Ứng dụng web sẽ chạy tại: `http://localhost:5173` (hoặc cổng hiển thị trên terminal).

### 4. Chạy Ứng Dụng Android
1. Mở phần mềm **Android Studio**.
2. Chọn **Open** và dẫn tới thư mục `android/` trong dự án.
3. Đợi Gradle đồng bộ hóa xong (Gradle Sync).
4. Kết nối thiết bị Android thật hoặc khởi động Android Emulator (API 24+).
5. Nhấn nút **Run** (▶) để biên dịch và chạy ứng dụng trên thiết bị.

---

## 🛠️ Công Nghệ Sử Dụng

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-0.100%2B-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/WebSocket-Realtime-orange?style=for-the-badge" />
  <img src="https://img.shields.io/badge/React-18%2B-61DAFB?style=for-the-badge&logo=react&logoColor=white" />
  <img src="https://img.shields.io/badge/Vite-Frontend-646CFF?style=for-the-badge&logo=vite&logoColor=white" />
  <img src="https://img.shields.io/badge/Kotlin-Android-7F52FF?style=for-the-badge&logo=kotlin&logoColor=white" />
  <img src="https://img.shields.io/badge/TailwindCSS-Styling-38Bdf8?style=for-the-badge&logo=tailwindcss&logoColor=white" />
</p>

---

## 📄 Giấy Phép
Phân phối dưới giấy phép MIT. Xem file [LICENSE](LICENSE) để biết thêm chi tiết.

## 👥 Tác Giả & Liên Hệ
* **Grizmo2610** - [GitHub Profile](https://github.com/Grizmo2610)
* Link dự án: [https://github.com/Grizmo2610/WereWolf-Online](https://github.com/Grizmo2610/WereWolf-Online)
