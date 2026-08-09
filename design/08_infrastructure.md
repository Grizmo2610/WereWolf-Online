# 08 - Infrastructure

## 1. Hosting

| Thành phần | Host | Gói |
|---|---|---|
| Backend (FastAPI) | Render | Free (512MB RAM, 0.1 vCPU) |
| Frontend (React build) | Cloudflare Pages | Free |
| Database (D1) | Cloudflare | Free |
| Keep-alive Worker | Cloudflare Workers | Free |

**Giới hạn thực tế với Render free:**
- Spin down sau 15 phút không có HTTP request → giải quyết bằng CF Worker ping (§2).
- Restart bất ngờ mất RAM state → giải quyết bằng game snapshot vào D1 (xem `03_game_engine.md` §9).
- Phù hợp cho 1 phòng, tối đa ~20 người cùng lúc. CPU 0.1 vCPU đủ cho use case này.

---

## 2. Cloudflare Worker — Keep-alive ping

### Vấn đề
Render free spin down sau 15 phút không có HTTP request. WebSocket connection đang mở **không tính** là activity — giữa ván chơi server vẫn có thể ngủ và WebSocket đứt.

### Giải pháp
CF Worker Cron chạy mỗi **10 phút**, gọi `GET /health` trên Render.

```javascript
// keep_alive/worker.js
export default {
  async scheduled(event, env, ctx) {
    const res = await fetch(env.BACKEND_URL + "/health");
    if (!res.ok) console.error("Health check failed:", res.status);
  },
};
```

```toml
# keep_alive/wrangler.toml
name = "masoi-keepalive"
main = "worker.js"
compatibility_date = "2024-01-01"

[triggers]
crons = ["*/10 * * * *"]

[vars]
BACKEND_URL = "https://your-app.onrender.com"
```

`/health` endpoint trên BE:
```python
@app.get("/health")
async def health():
    return {"status": "ok"}
```

### Giới hạn
CF Worker free: 100,000 request/ngày. Ping 10 phút/lần = ~144/ngày — trong giới hạn free.

---

## 3. Load check

`room_manager.py` kiểm tra tài nguyên server trước mỗi lần tạo phòng hoặc join:

```python
import psutil

def can_accept_connection() -> bool:
    ram_ok = psutil.virtual_memory().percent < 80
    cpu_ok = psutil.cpu_percent(interval=0.1) < 85
    return ram_ok and cpu_ok
```

Ngưỡng 80% RAM và 85% CPU để giữ buffer an toàn — không để server chạy đến giới hạn mới từ chối.

Nếu `False` → trả về event `SERVER_OVERLOAD` (xem §4). Không raise exception, không crash.

---

## 4. Thông báo quá tải

Khi `can_accept_connection()` trả `False`, server gửi `SERVER_OVERLOAD` event với message:

> *"Server đang thở hổn hển vì dev chưa nạp thẻ 💸 Vui lòng thử lại sau vài phút — đang cố thuyết phục con server tội nghiệp này gắng thêm một chút nữa 🙏"*

Variant ngắn (toast):
> *"Dev đang broke nên server chỉ có vậy thôi 🥲 Thử lại sau nhé!"*

FE hiển thị dưới dạng toast/modal — không redirect, không crash. Người dùng thử lại sau.

---

## 5. Logging

Mọi event quan trọng ghi ra **stdout** và **file** `backend/logs/YYYY-MM-DD.log` đồng thời.

### Format

```
[HH:MM:SS] [LEVEL] [context] message
```

Ví dụ:
```
[21:03:11] [INFO ] === ĐÊM 1 ===
[21:03:44] [INFO ] [seat_7/bao_ve99] NIGHT_ACTION role=guard target=seat_5
[21:04:02] [INFO ] EVENT player_dead seat=5 cause=wolf_bite
[21:05:00] [INFO ] === NGÀY 1 - THẢO LUẬN ===
[21:05:31] [INFO ] [seat_1/minh_dep] SPEAK channel=public "ghế 3 nói mâu thuẫn"
[21:07:22] [INFO ] EVENT skip_discussion votes=5/9
[21:08:25] [INFO ] EVENT player_lynched seat=3 votes=5/9
[21:08:26] [WARN ] EVENT game_end winner=villagers
```

### Level

| Level | Dùng cho |
|---|---|
| `DEBUG` | Raw WebSocket payload, D1 query params |
| `INFO` | Phase boundaries, action, speech, event |
| `WARN` | Server overload từ chối, AFK timeout, game cancelled |
| `ERROR` | D1 connection fail, JWT invalid, snapshot decrypt fail |

Console mặc định `INFO` trở lên. File log capture tất cả kể cả `DEBUG`.

### Nội dung log theo loại

| Nội dung | Chat công khai | File log |
|---|---|---|
| Lời nói ngày | ✅ | ✅ |
| Hành động đêm (target + role) | ❌ (chỉ kết quả) | ✅ |
| Kết quả vote (ai bỏ cho ai) | ✅ (sau khi kết thúc phase) | ✅ |
| Phase boundaries | ✅ (banner) | ✅ |
| Người chết + nguyên nhân | ✅ (nếu public) | ✅ |
| Dead chat | ❌ | ✅ |
