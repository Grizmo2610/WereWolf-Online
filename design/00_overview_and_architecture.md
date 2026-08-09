# 00 - Tổng quan & Kiến trúc

## 1. Dự án là gì

Một web app chơi Ma Sói (Werewolf/Mafia) nhiều người thật qua Internet. Mỗi người dùng thiết bị riêng (điện thoại hoặc máy tính), đăng nhập bằng tài khoản cá nhân, và kết nối vào cùng phòng chơi bằng mã phòng.

**Người tạo phòng (Host)** cũng là người chơi — họ cấu hình kịch bản, điều chỉnh số lượng người và role, rồi khởi động ván. Các người chơi còn lại nhập mã phòng để tham gia. Host ngồi vào ghế và chơi cùng, không có "Admin đứng ngoài điều phối".

**Core loop:** Đêm (các role hành động đồng thời, tối đa 60 giây) → Ngày (thảo luận 5 phút, vote sớm khả dụng sau 3 phút) → Bỏ phiếu (tối đa 60 giây) → lặp lại cho đến khi một phe đạt điều kiện thắng.

**AI Agent (bot):** Chưa ưu tiên trong phiên bản này. Kiến trúc giữ lại phần cơ sở để tích hợp sau, nhưng mọi ghế đều do người thật ngồi.

Tài liệu chi tiết theo từng mảng:
- `01_characters.md` — danh sách đầy đủ các role
- `02_scenarios.md` — danh sách kịch bản + cơ chế tùy chỉnh
- `03_game_engine.md` — luật chơi, timing, vote, thắng/thua, persistence
- `04_auth_storage_ui.md` — xác thực, database, WebSocket events, UI/UX

---

## 2. Tech stack

### Backend
- **FastAPI** (Python) — single process, WebSocket realtime
- **Cloudflare D1** (SQLite-compatible) — lưu tài khoản, lịch sử ván, snapshot
- **bcrypt + JWT** — xác thực, session cookie httpOnly

### Frontend
- **React + Vite** — component-based UI, client-side routing
- **TailwindCSS** — styling, mobile-first responsive
- **Framer Motion** — animation (phase transition, reveal role, người chết)
- **Zustand** — global state (game state, WebSocket events)
- **React Query** — fetch API (auth, room config)
- **Cloudflare Pages** — static host cho React build

### Infrastructure
- **Render free tier** — host FastAPI backend (512MB RAM, 0.1 vCPU)
- **Cloudflare Worker (Cron)** — ping `/health` mỗi 10 phút để giữ Render tỉnh

---

## 3. Cấu trúc thư mục

```
werewolf/
├── keep_alive/                     # CF Worker giữ Render tỉnh
│   ├── worker.js
│   └── wrangler.toml
│
├── backend/
│   ├── .env                        # runtime config (không chứa key nhạy cảm)
│   ├── .env.example
│   ├── requirements.txt
│   ├── config/
│   │   └── settings.py             # load .env, cấu hình D1 endpoint
│   ├── main.py                     # FastAPI entrypoint
│   ├── db/
│   │   ├── d1_client.py            # HTTP client gọi Cloudflare D1 REST API
│   │   └── models.py               # dataclass/schema cho từng bảng
│   ├── auth/
│   │   ├── router.py               # POST /auth/register, /auth/login, /auth/logout
│   │   ├── service.py              # bcrypt hash, JWT tạo/verify
│   │   └── dependencies.py         # get_current_user dependency
│   ├── enums.py
│   ├── seat.py
│   ├── player.py
│   ├── game.py                     # GameState, vòng lặp đêm/ngày
│   ├── resolver.py                 # giải quyết action đêm, xác định ai chết
│   ├── vote.py                     # logic bỏ phiếu, xử lý hòa, skip vote sớm
│   ├── scenarios.py                # Scenario, ScenarioFiller
│   ├── room_manager.py             # tạo/tìm/xóa phòng, load check
│   ├── roles/
│   │   ├── base.py
│   │   ├── villagers.py
│   │   ├── wolves.py
│   │   └── neutral.py
│   ├── ws/
│   │   ├── router.py               # WebSocket endpoint /ws/{room_code}
│   │   ├── events.py               # định nghĩa các loại event
│   │   └── broadcaster.py          # gửi event tới toàn phòng hoặc 1 người
│   └── logs/
│       └── YYYY-MM-DD.log
│
└── frontend/
    ├── src/
    │   ├── main.jsx
    │   ├── App.jsx                  # React Router v6
    │   ├── store/
    │   │   ├── gameStore.js         # Zustand — game state
    │   │   └── authStore.js         # Zustand — user session
    │   ├── hooks/
    │   │   ├── useWebSocket.js      # WS connect, auto-reconnect, dispatch to store
    │   │   ├── useGameTimer.js      # Countdown timer sync với server
    │   │   └── useMentionHighlight.js  # Detect mention trong chat (client-side)
    │   ├── pages/
    │   │   ├── LoginPage.jsx
    │   │   ├── RegisterPage.jsx
    │   │   ├── LobbyPage.jsx
    │   │   ├── RoomPage.jsx         # Phòng chờ + cấu hình
    │   │   └── GamePage.jsx
    │   ├── components/
    │   │   ├── game/
    │   │   │   ├── SeatCircle.jsx
    │   │   │   ├── SeatAvatar.jsx
    │   │   │   ├── RoleCard.jsx         # Card flip animation
    │   │   │   ├── PhaseOverlay.jsx     # Transition đêm/ngày
    │   │   │   └── NightActionModal.jsx # Hành động đêm (riêng tư)
    │   │   ├── chat/
    │   │   │   ├── ChatPanel.jsx
    │   │   │   ├── ChatBubble.jsx       # Highlight nếu bị mention
    │   │   │   ├── SystemBanner.jsx     # Sự kiện hệ thống
    │   │   │   └── VoteCounter.jsx      # Live counter in-place
    │   │   └── ui/
    │   │       ├── Timer.jsx
    │   │       ├── Button.jsx
    │   │       └── OverloadBanner.jsx   # Thông báo server quá tải
    │   └── config/
    │       ├── theme.js             # CSS variables
    │       └── wsEvents.js          # Enum event types
    ├── public/
    ├── index.html
    ├── vite.config.js
    ├── tailwind.config.js
    └── package.json
```

---

## 4. Quyết định kiến trúc quan trọng

### 4.1 Role gửi riêng tư, BE là source of truth

Role của mỗi người chỉ gửi qua WebSocket đến đúng thiết bị đó. BE giữ toàn bộ GameState — FE chỉ nhận event và render, không bao giờ nhận payload chứa role người khác. F12 chỉ thấy đúng thông tin người đó được phép biết.

### 4.2 Host = người chơi có quyền cấu hình

Host tạo phòng, ngồi vào ghế, chơi cùng. Họ có thêm quyền cấu hình kịch bản, điều chỉnh role, kick người chưa sẵn sàng, bắt đầu ván, resume sau server restart, kết thúc sớm thảo luận. Sau khi ván bắt đầu, Host không có thông tin đặc quyền hơn người khác.

### 4.3 Load check trước khi cho join

`room_manager.py` kiểm tra RAM + CPU trước mỗi lần tạo phòng hoặc join:

```python
import psutil

def can_accept_connection() -> bool:
    return (
        psutil.virtual_memory().percent < 80 and
        psutil.cpu_percent(interval=0.1) < 85
    )
```

Nếu vượt ngưỡng → trả về thông báo hài hước thay vì để server crash. Xem `04_auth_storage_ui.md` §6 cho nội dung thông báo.

### 4.4 Game state persistence vào D1

Snapshot GameState sau mỗi phase (cuối đêm, cuối thảo luận, cuối vote), encrypt AES-256 trước khi ghi. Khi server restart, Host reconnect và thấy nút Resume. Chi tiết tại `03_game_engine.md` §8.

### 4.5 Cloudflare Worker keep-alive

Worker Cron ping `/health` mỗi 10 phút để Render free tier không spin down giữa ván. Chi tiết tại `04_auth_storage_ui.md` §9.

### 4.6 Display name tách khỏi username

Đăng ký điền thêm `display_name` (để trống = dùng username). Trong game chỉ hiển thị `display_name`. Username chỉ dùng để đăng nhập, không bao giờ hiển thị công khai.

### 4.7 Mention highlight — client-side hoàn toàn

`useMentionHighlight.js` detect xem một tin nhắn có nhắc đến người chơi hiện tại không (theo số ghế hoặc display name). Xử lý hoàn toàn trên FE, không cần backend. Chi tiết tại `04_auth_storage_ui.md` §8.
