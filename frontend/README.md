# Ma Sói Online — Frontend

## Chạy local

```bash
cd frontend
npm install
echo "VITE_API_BASE=http://localhost:8000" > .env
npm run dev
```

Mặc định chạy ở http://localhost:5173, gọi backend tại http://localhost:8000
(sửa trong `.env` nếu khác).

## Build production

```bash
npm run build   # output vào dist/
npm run preview # xem thử bản build
```

## Đã hoàn thành

- Login / Register / Lobby / Room (phòng chờ) / Game (màn chơi chính)
- Theme đúng palette 10 màu + font Times New Roman + background ảnh theo `07_ui.md`
- Zustand store xử lý toàn bộ WebSocket event types từ `06_websocket.md`
- Seat circle (click để chọn mục tiêu đêm/vote), chat feed hợp nhất (chat + banner
  hệ thống + kênh người chết + vote counter in-place), mention highlight client-side,
  timer 2 chế độ (đồng hồ/progress bar, lưu localStorage), animation lật role +
  fade người chết + overlay tối ban đêm (Framer Motion)
- Đã test qua Playwright: Login → Register → Lobby render đúng, gọi API thật thành công

## Chưa làm / cần kiểm tra thêm

- Chưa test trực quan màn Room và Game thật kỹ (do giới hạn thời gian sandbox lúc
  build, không phải do lỗi code — build/lint đều sạch)
- Chưa có màn hình Settings riêng cho timer mode (hiện bấm trực tiếp vào đồng hồ
  để đổi mode)
- Halfbreed/Grandmother/RedHood chưa có UI hiển thị đặc biệt (dùng chung
  RoleCard mặc định)
- Resume game sau khi mất kết nối (RESUME_GAME event) — BE đã có field liên
  quan nhưng FE chưa xử lý event RESUME_AVAILABLE/GAME_STATE_SYNC
