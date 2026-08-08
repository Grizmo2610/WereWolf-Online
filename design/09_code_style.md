# 09 - Code Style

## 1. Ngôn ngữ

| Ngữ cảnh | Ngôn ngữ |
|---|---|
| Giao tiếp với người dùng (UI text, thông báo, toast, banner) | Tiếng Việt |
| Code: tên biến, hàm, class, file, module | Tiếng Anh |
| Comment trong code | Tiếng Anh |
| Tài liệu thiết kế (các file .md này) | Tiếng Việt |

---

## 2. Comment

**Nguyên tắc: tối thiểu hóa.** Code tốt tự giải thích được. Comment chỉ xuất hiện khi thực sự cần.

**Không cần:**
- Summary đầu file
- Docstring đầy đủ cho từng function
- Comment giải thích code đơn giản ("increment counter by 1")
- Comment lặp lại tên hàm ("this function handles login")

**Nên có:**
- Comment ngắn 1 dòng cho hàm **dài và phức tạp** — giải thích *tại sao*, không phải *cái gì*
- Comment cho logic không hiển nhiên (VD: lý do dùng lookbehind regex, lý do chờ đủ 60s dù đã submit)
- `# TODO:` hoặc `# FIXME:` khi có điểm cần quay lại

**Ví dụ đúng:**
```python
# wait full 60s even if all submitted — early end leaks timing info
await asyncio.sleep(remaining)

def resolve_night(game_state, actions):
    # tier 0 (wolves) always resolves before tier 1
    ...
```

**Ví dụ sai:**
```python
# This function resolves the night phase actions
def resolve_night(game_state, actions):
    # Get the wolf votes from actions
    wolf_votes = get_wolf_votes(actions)
    # Count the votes
    target = count_votes(wolf_votes)
```

---

## 3. Tách hàm

**Nguyên tắc: 1 hàm làm 1 việc.**

- Hàm không làm quá nhiều việc cùng lúc — nếu cần mô tả hàm bằng "và", đó là dấu hiệu cần tách.
- Không có hàm vừa validate input, vừa query DB, vừa gửi WebSocket event.
- Hàm dài hơn ~30–40 dòng nên xem lại xem có tách được không.

**Ví dụ cấu trúc đúng (`resolver.py`):**

```python
def resolve_night(game_state, actions):
    protected = collect_protected(actions)
    kills = collect_kills(actions, protected)
    kills = apply_counter_effects(game_state, kills)
    return apply_deaths(game_state, kills)

def collect_protected(actions): ...
def collect_kills(actions, protected): ...
def apply_counter_effects(game_state, kills): ...
def apply_deaths(game_state, kills): ...
```

Mỗi hàm nhỏ có thể test độc lập, dễ đọc, dễ sửa.

---

## 4. Đặt tên

**Rõ ràng hơn ngắn gọn.** Không dùng tên viết tắt mơ hồ.

```python
# Sai
def chk_conn(): ...
usr = get_u(uid)
res = proc(d)

# Đúng
def can_accept_connection(): ...
user = get_user(user_id)
result = process_action(data)
```

**Convention:**
- Python: `snake_case` cho biến/hàm, `PascalCase` cho class.
- JavaScript/React: `camelCase` cho biến/hàm, `PascalCase` cho component.
- Hằng số: `UPPER_SNAKE_CASE` ở cả hai.
- File Python: `snake_case.py`. File React component: `PascalCase.jsx`. File hook/util: `camelCase.js`.

---

## 5. Cấu trúc file

- Không có summary/description ở đầu file.
- Import sắp xếp theo nhóm: stdlib → third-party → local. Mỗi nhóm cách nhau 1 dòng trống.
- Các hàm/class liên quan nhau đặt gần nhau trong file.
- Nếu một file bắt đầu cảm thấy dài (> ~200 dòng), xem xét tách module.

---

## 6. Một số quy tắc cụ thể

**Python:**
- Dùng type hint cho function signature — không cần annotation ở mọi nơi, nhưng signature hàm public nên có.
- Dùng `dataclass` cho data container, không dùng dict thuần khi có schema cố định.
- Không catch exception quá rộng (`except Exception`) trừ ở top-level error handler.

**React/JavaScript:**
- Mỗi component trong file riêng.
- Không put business logic trong component — logic vào hook hoặc store.
- Tránh `useEffect` với dependency array phức tạp — nếu cần, tách ra hook riêng.
- Không truyền quá 3–4 props xuống nhiều tầng — dùng store (Zustand) thay vì prop drilling.

**Chung:**
- Không commit code có `console.log` debug còn sót.
- Magic number → đặt thành hằng có tên rõ ràng.
  ```python
  # Sai
  await asyncio.sleep(30)
  
  # Đúng
  AFK_TIMEOUT_SECONDS = 30
  await asyncio.sleep(AFK_TIMEOUT_SECONDS)
  ```
