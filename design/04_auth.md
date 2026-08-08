# 04 - Xác thực & Session

## 1. Tổng quan

Xác thực dùng **username + password**. Không có OAuth, không có email. Session lưu trong cookie httpOnly chứa JWT.

Toàn bộ logic xác thực nằm trong `backend/auth/`:
- `router.py` — định nghĩa các route HTTP
- `service.py` — business logic (hash, JWT)
- `dependencies.py` — FastAPI dependency cho các route cần xác thực

---

## 2. Đăng ký (`POST /auth/register`)

### Form fields

| Field | Bắt buộc | Ràng buộc |
|---|---|---|
| `username` | ✅ | 3–20 ký tự, chỉ chữ/số/gạch dưới, unique trong DB |
| `display_name` | ❌ | Nếu điền: tối thiểu 3 ký tự, không được là thuần số. Để trống → dùng username |
| `password` | ✅ | Tối thiểu 6 ký tự |

### Xử lý display name

```python
# auth/service.py
display_name = data.display_name.strip()
if not display_name:
    display_name = data.username
elif display_name.isdigit():
    raise ValueError("Display name cannot be purely numeric")
```

Lý do không cho display name thuần số: mention detection trên FE dùng số ghế để detect — display name là số sẽ gây false positive (xem `07_ui.md` §4).

### Flow

1. Validate input (format + unique username).
2. Hash password bằng **bcrypt** cost factor 12.
3. Tạo UUID v4 cho `user_id`.
4. Insert vào bảng `users` trong D1.
5. Tạo JWT và ghi cookie — tự động đăng nhập sau khi đăng ký thành công.

---

## 3. Đăng nhập (`POST /auth/login`)

1. Lookup `username` trong D1.
2. Verify password với bcrypt hash.
3. Tạo **JWT** với payload:
   ```json
   { "user_id": "...", "username": "...", "display_name": "...", "exp": "<7 ngày>" }
   ```
4. Ghi vào **cookie httpOnly** tên `session_token`:
   - `HttpOnly: true`
   - `SameSite: Strict`
   - `Secure: true` trên production, `false` trên localhost

---

## 4. Đăng xuất (`POST /auth/logout`)

Xóa cookie phía client bằng cách set `expires` về quá khứ. Không cần blacklist token ở phiên bản này — JWT hết hạn tự nhiên sau 7 ngày.

---

## 5. Dependency `get_current_user`

```python
# auth/dependencies.py
async def get_current_user(request: Request) -> User:
    token = request.cookies.get("session_token")
    if not token:
        raise HTTPException(status_code=401)
    payload = verify_jwt(token)  # raise HTTPException 401 nếu expired/invalid
    return User(**payload)
```

Dùng `Depends(get_current_user)` cho mọi route và WebSocket endpoint cần xác thực. Route không cần auth (login, register, health) không dùng dependency này.

---

## 6. Display name trong game

- **Ghế ngồi** hiển thị: `display_name`
- **Chat bubble** hiển thị: `[Ghế X - display_name]: "..."`
- **Username** chỉ dùng để đăng nhập, không bao giờ hiển thị công khai trong game
- Người chơi không thể đổi display name sau khi đã đăng ký (ít nhất ở phiên bản này)
