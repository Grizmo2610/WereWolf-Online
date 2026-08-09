# 03 - Game Engine

## 1. Ngôn ngữ

Mọi văn bản hiển thị trong game bằng **tiếng Việt**. Tên biến, class, function trong code dùng tiếng Anh.

---

## 2. Vòng đời một ván

```
Tạo phòng → Chờ người vào → Cấu hình kịch bản → Tất cả sẵn sàng → Bắt đầu
    → Phân role (riêng tư)
    → Game-start info block (công khai)
    → [Đêm → Sáng (công bố kết quả đêm) → Ngày (Thảo luận → Bỏ phiếu)] × N
    → Kết thúc (công bố phe thắng, reveal toàn bộ role)
```

### Phân role

- Hệ thống gán role ngẫu nhiên cho tất cả người chơi.
- Role gửi **riêng tư** qua WebSocket (`ROLE_ASSIGNED`) đến đúng thiết bị của người đó.
- Ngay sau khi phân role, gửi tiếp các thông tin "nhận dạng đồng đội" riêng tư:
  - Sói nhận `wolf_seat_ids` — danh sách ghế của tất cả Sói trong ván.
  - Song Sinh nhận `twin_seat_id` — ghế của người kia.
  - Cupid nhận xác nhận đã liên kết cặp đôi nào (đêm 1).
  - Bà Ngoại / Khăn Đỏ nhận `pair_seat_id`.
- Người chơi thấy màn hình **lật bài** (card flip animation) reveal role của mình trước khi vào đêm 1.

### Game-start info block

Sau khi phân role, trước Đêm 1, hệ thống post 1 block thông tin công khai vào chat feed:

```
=== BẮT ĐẦU VÁN ===
Tổng người chơi: 9
Phân bố role: Sói ×2, Tiên Tri ×1, Bảo Vệ ×1, Phù Thủy ×1, Thợ Săn ×1, Dân thường ×3
Phân bố phe: Dân làng ×7, Sói ×2
Thời gian thảo luận: 5 phút (vote sớm khả dụng sau 3 phút)
Thời gian bỏ phiếu: 60 giây
Mô tả role trong ván: [danh sách động từ RoleMeta]
```

---

## 3. Phase Đêm

### 3.1 Tổng quan

- Thời gian tối đa: **60 giây** (cấu hình được, 30–120 giây).
- Tất cả người chơi có hành động đêm hành động **đồng thời** — không tuần tự, không có round-robin.
- **Không có chat** trong phase đêm cho người sống. Người chết vẫn thấy kênh chat người chết (xem §6).
- Hết 60 giây → server tự động resolve tất cả action đã submit; ai chưa submit = bỏ qua lượt (không có hành động).
- Không kết thúc sớm dù tất cả đã submit — chờ đủ 60 giây để tránh lộ thông tin (nếu đêm kết thúc ngay sau khi Tiên Tri submit, những người quan sát có thể suy luận Tiên Tri đã hành động xong).

### 3.2 Giao diện hành động đêm

Khi phase đêm bắt đầu, người chơi thấy màn hình tối (overlay đêm). Người có hành động đêm thấy thêm **modal hành động riêng tư** xuất hiện trên thiết bị của họ:

- Danh sách mục tiêu hợp lệ (đã lọc theo luật role: không vote chính mình, không vote người chết, v.v.).
- Nút xác nhận. Có thể **thay đổi lựa chọn** bất kỳ lúc nào trước khi hết 60 giây.
- Sau khi confirm lần đầu: nút chuyển thành "Đã chọn: [tên]" + nút "Đổi lại" — tránh confirm nhầm.

Người không có hành động đêm chỉ thấy màn hình chờ với timer.

### 3.3 Vote đêm của Sói

Sói là role duy nhất có hành động đêm dạng **vote nhóm**:

- Mỗi con Sói thấy danh sách người sống, **tô màu đỏ** các ghế Sói khác (để phân biệt đồng đội).
- Sói không thể chọn chính mình hoặc Sói khác làm mục tiêu (FE disable option + BE validate lại).
- Mỗi Sói submit vote độc lập. Server tổng hợp: **mục tiêu nhiều phiếu nhất bị cắn**. Hòa giữa các mục tiêu → không ai bị cắn đêm đó.
- Sói không có kênh chat đêm — chỉ vote, không nói chuyện.

### 3.4 Thứ tự resolve (Night Order)

`night_order.py` chia hai tầng, xử lý tuần tự sau khi thu thập đủ action:

```
Tầng 0 — Phe Sói (luôn đi trước):
  Werewolf / Alpha Wolf / Wolf Cub / Wolf Seer / Medium / ...

Tầng 1 — Tất cả còn lại (theo ActionPriority):
  Cupid (đêm 1) → Guard → Priest → Seer-type → Witch cứu
  → Witch độc → Huntress → Vampire → Gambler → Sorcerer → Old Hag → ...
```

Trong cùng tầng 1, thứ tự resolve quan trọng với các action có tương tác (VD: Guard phải resolve trước Wolf bite để biết ai được bảo vệ trước khi tính ai chết).

**Ví dụ logic resolve:**

```python
# resolver.py — logic cốt lõi (không phải code đầy đủ)
def resolve_night(game_state, submitted_actions):
    protected = set()
    kills = set()
    
    # Tầng 0: Sói vote
    wolf_target = tally_wolf_votes(submitted_actions)
    
    # Tầng 1: Guard bảo vệ trước
    for action in tier1_actions_by_priority(submitted_actions):
        if action.type == "guard":
            protected.add(action.target)
        elif action.type == "wolf_bite" and wolf_target not in protected:
            kills.add(wolf_target)
        # ... các action khác
    
    return apply_deaths(game_state, kills)
```

### 3.5 Counter-effects sau resolve

Sau khi tính danh sách chết, xử lý tiếp các hiệu ứng phụ:
- **Plague Bearer** chết bởi Sói → set `wolf_infection = True` (Sói bỏ qua đêm tiếp).
- **Hunter** chết → mục tiêu đang đánh dấu chết theo.
- **Terrorist** chết → 2 ghế cạnh chết theo.
- **Tough Youth** bị cắn → không chết ngay, set `pending_death = next_night`.
- **Cursed** bị cắn → không chết, chuyển phe Sói.
- **Cupid cặp đôi** — một người chết → người kia chết theo.

---

## 4. Phase Sáng (công bố kết quả đêm)

Sau khi resolve xong, server broadcast kết quả ra chat feed công khai:

- Danh sách người chết đêm qua + nguyên nhân (nếu nguyên nhân được tiết lộ theo luật kịch bản).
- Nếu `reveal_on_death = true` → kèm role của người chết.
- Nếu không có ai chết → "Đêm qua bình yên, không có ai chết."
- Nếu Sói bị nhiễm bệnh (Plague Bearer) → không thông báo lý do, chỉ thấy không có ai chết.

---

## 5. Phase Ngày — Thảo luận

### 5.1 Timing

```
0:00 ─────────────────── 3:00 ──────────────── 5:00
│                          │                     │
│   Chat mở, tự do         │  Nút "Bỏ qua"       │  Hết giờ
│   (tất cả người sống)    │  hiện ra             │  → sang Vote
│                          │                     │
```

- **0–3 phút:** Chat tự do. Nút vote sớm chưa hiển thị.
- **Sau 3 phút:** Nút **"Bỏ qua thảo luận"** xuất hiện cho tất cả người sống.
- **Vote sớm:** Nếu **> 50% người sống** nhấn "Bỏ qua" → kết thúc thảo luận ngay, chuyển sang Vote. Counter realtime: "Bỏ qua: 4/9".
- **Hết 5 phút:** Tự động chuyển sang Vote dù chưa đủ người bỏ qua.
- Host có thể kết thúc sớm bất kỳ lúc nào (không cần đủ 50%).

### 5.2 Luật chat ngày

- Chỉ người **còn sống** mới được gửi tin nhắn trong chat chung.
- Người bị **Pháp Sư** im lặng hóa: ô nhập chat bị disable, hiển thị "Bạn đang bị im lặng hôm nay."
- Người bị **Mụ Già** phạt: ô nhập chat bị disable + không được bỏ phiếu.
- **Người chết:** không được chat chung, nhưng thấy toàn bộ chat chung và có kênh chat riêng của người chết (xem §6).

---

## 6. Kênh chat người chết

### 6.1 Cơ chế

Một kênh chat song song tồn tại suốt cả ván, chỉ hiển thị cho người đã chết. Cùng cửa sổ chat với người sống nhưng được tách bằng visual divider rõ ràng:

```
┌─────────────────────────────────────┐
│  [Chat chung — người sống thấy]     │
│  minh99: "tôi nghi ghế 3"           │
│  an_oi: "3 ơi giải thích đi"        │
│                                      │
│ ─────── 💀 Chỉ người chết thấy ──── │  ← chỉ render cho người chết
│  [Ghế 5 - nam_dep]: "tôi bị oan :(" │
│  [Ghế 7 - hoa]: "tôi cũng vậy"      │
│                                      │
│  [Ô nhập — chỉ active nếu đã chết]  │
└─────────────────────────────────────┘
```

Người sống **không thấy divider và kênh bên dưới** — FE chỉ render phần đó nếu `currentUser.is_alive === false`.

### 6.2 Luật chat người chết

- Người chết **không được** gửi tin vào chat chung.
- Người chết **có thể** gửi tin vào kênh người chết — chỉ người chết khác đọc được.
- **Ban đêm:** Kênh chat người chết **vẫn mở** — đây là thời gian duy nhất người chết có thể chat (người sống thì không được chat đêm). Kênh này không hiển thị với người sống ở bất kỳ thời điểm nào.
- **Hồn Ma (Ghost):** Ngoại lệ đặc biệt — chết đêm 1 nhưng được phép gửi **đúng 1 từ** mỗi ngày vào chat chung. FE enforce giới hạn này: sau khi đã dùng 1 từ trong ngày, ô nhập của Ghost bị disable đến hôm sau.

### 6.3 Lý do thiết kế kênh chung

Thay vì tách thành 2 tab/cửa sổ riêng biệt, gộp vào 1 feed với divider giúp:
- Người chết vẫn theo dõi được toàn bộ diễn biến game (context đầy đủ).
- Không phải chuyển qua lại giữa tab.
- Phần dưới divider không gây nhầm lẫn với người sống vì FE không render nó với họ.

---

## 7. Phase Ngày — Bỏ phiếu

### 7.1 Cơ chế

- Thời gian tối đa: **60 giây** (cấu hình được).
- Mỗi người chọn 1 mục tiêu để trục xuất, hoặc **phiếu trắng**.
- Có thể **thay đổi phiếu** bất kỳ lúc nào trong 60 giây.
- Hết giờ hoặc tất cả đã vote → tính kết quả.
- **Kết quả:** người nhiều phiếu nhất bị trục xuất. **Hòa = không ai bị trục xuất.**
- Kết quả vote (ai bỏ cho ai, số phiếu) broadcast công khai ngay sau khi phase kết thúc.

### 7.2 Live vote counter

Trong phase vote, chat feed hiển thị counter cập nhật in-place:

```
⚖️ Đang bỏ phiếu... (7/9 đã vote)
   Ghế 3: ████░░  4 phiếu
   Ghế 5: ██░░░░  2 phiếu
   Trắng: █░░░░░  1 phiếu
```

Counter update mỗi khi có người vote (qua WebSocket event `VOTE_UPDATE`). Không hiển thị **ai** bỏ phiếu cho **ai** cho đến khi phase kết thúc — chỉ hiện tổng số phiếu mỗi mục tiêu.

### 7.3 Ảnh hưởng role lên vote

| Role | Ảnh hưởng |
|---|---|
| Hoàng Tử | Lần đầu bị vote trục xuất: không chết, lật bài công khai thay vào. Miễn nhiễm hết hiệu lực từ lần thứ 2. |
| Sói Con | Nếu bị trục xuất: ngày hôm sau được trục xuất 2 người thay vì 1. |
| Mụ Già | Nạn nhân không được bỏ phiếu ngày đó (ô vote bị disable). |
| Pháp Sư | Nạn nhân không được nói nhưng vẫn được bỏ phiếu. |
| Kẻ Chán Đời | Nếu bị trục xuất bằng vote → thắng ngay lập tức (không chết theo nghĩa thông thường). |

---

## 8. Điều kiện thắng

Kiểm tra sau **mỗi event chết** (không chờ hết phase):

| Phe | Điều kiện thắng mặc định |
|---|---|
| Sói | Số Sói ≥ số Dân làng còn sống |
| Dân làng | Tất cả Sói chết |
| Kẻ Chán Đời | Bị trục xuất bằng vote |
| Sát Nhân Đơn Độc | Là người sống sót duy nhất |
| Chủ Giáo Phái | Tất cả người sống đều trong giáo phái |
| Sói Cô Độc | Là con Sói duy nhất còn sống |
| Cặp đôi (Cupid) | Là cặp sống sót cuối cùng (override thắng phe khác) |

Khi ván kết thúc: broadcast `GAME_END` với phe thắng + reveal **toàn bộ role** của tất cả người chơi (bất kể cài đặt `reveal_on_death`).

---

## 9. Game state persistence & Resume

### 9.1 Vấn đề

Backend chạy Render free tier — có thể restart bất ngờ (deploy, crash, maintenance). Toàn bộ `GameState` trong RAM sẽ mất. Giải pháp: snapshot vào D1 tại các điểm chốt.

### 9.2 Thời điểm lưu (3 checkpoint/vòng)

```
Đêm resolve xong      → checkpoint "night_resolved"
Thảo luận kết thúc    → checkpoint "discussion_end"
Vote kết thúc         → checkpoint "vote_end"
```

Không lưu liên tục để tránh write quá nhiều vào D1 free tier.

### 9.3 Nội dung snapshot

Snapshot chứa toàn bộ thông tin cần thiết để rebuild `GameState`:

```python
@dataclass
class GameSnapshot:
    game_id: str
    room_code: str
    round_number: int
    phase: str                  # 'night_resolved' | 'discussion_end' | 'vote_end'
    players: list[PlayerState]
    # PlayerState: user_id, seat_id, role_id, role_state, is_alive, is_afk
    pending_effects: list       # Tough Youth delay, Vampire reveal delay, ...
    wolf_infection_active: bool
    scenario_id: str
    scenario_custom_rules: dict
    reveal_on_death: bool
    saved_at: str
```

Snapshot **encrypt AES-256** trước khi ghi vào D1 (key từ `.env`) vì chứa role của tất cả người chơi.

### 9.4 Resume flow

```
Server restart
  → Load snapshot gần nhất (ORDER BY saved_at DESC LIMIT 1)
  → Giải mã, rebuild GameState trong RAM
  → WebSocket endpoint mở lại, chờ reconnect
  → Người chơi vào lại /game/{room_code} → tự reconnect nếu JWT còn hợp lệ
  → Khi Host reconnect → thấy banner "Ván đang tạm dừng" + nút [Resume]
  → Host nhấn Resume → broadcast PHASE_CHANGE, ván tiếp tục từ checkpoint
```

**Quy tắc:**
- Chỉ Host thấy nút Resume. Nếu Host không reconnect trong 5 phút → quyền Host chuyển sang người tiếp theo đã kết nối.
- Người chơi reconnect nhận lại: role của bản thân (private), full public history (từ `round_logs` + `speech_logs`), phase hiện tại + thời gian còn lại.
- Nếu < 50% người reconnect sau 5 phút → hủy ván, ghi `status = 'cancelled'`.

### 9.5 Schema bổ sung

```sql
CREATE TABLE game_snapshots (
    id               TEXT PRIMARY KEY,
    game_id          TEXT NOT NULL REFERENCES game_records(id),
    room_code        TEXT NOT NULL,
    round_number     INTEGER NOT NULL,
    phase            TEXT NOT NULL,
    state_encrypted  TEXT NOT NULL,
    saved_at         TEXT NOT NULL
);

CREATE INDEX idx_snapshots_room ON game_snapshots(room_code, saved_at DESC);
```

Giữ tối đa 3 checkpoint gần nhất mỗi ván, xóa checkpoint cũ hơn định kỳ.

---

## 10. Xử lý mất kết nối

- Mất kết nối → server chờ **30 giây** trước khi đánh dấu AFK.
- Trong 30 giây: người chơi có thể reconnect và tiếp tục, game không dừng.
- Sau 30 giây: ghế đánh dấu AFK. Hành động đêm bỏ qua, vote ngày bỏ qua.
- Host mất kết nối > 30 giây: quyền Host tự động chuyển sang người tiếp theo đang kết nối.
- < 50% người kết nối trong 5 phút: game tạm dừng → chờ thêm 5 phút → hủy ván nếu không đủ người.
