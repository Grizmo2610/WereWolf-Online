# 02 - Kịch bản

## Cơ chế tùy chỉnh kịch bản

### Số người chơi không cố định

Mỗi kịch bản **không khóa cứng** số người. Thay vào đó định nghĩa:

| Thuộc tính | Ý nghĩa |
|---|---|
| `suggested_players` | Số người gợi ý — hiển thị nổi bật trong UI |
| `min_players` | Tối thiểu để ván có thể bắt đầu |
| `max_players` | Tối đa cho phép |
| `base_roles` | Danh sách role ứng với `suggested_players` |
| `fill_strategy` | Cách tự động đề xuất thêm role khi tăng số người |

Host điều chỉnh số ghế trong khoảng `[min_players, max_players]`. Khi thay đổi số người, `ScenarioFiller` tự động **đề xuất** danh sách role mới — Host luôn có thể override thủ công từng role.

### Chỉnh sửa role thủ công

Trong màn Room Settings, Host có thể:
- **Thêm** bất kỳ role từ danh sách toàn bộ role (chia theo phe, có tooltip mô tả)
- **Xóa** role khỏi danh sách
- **Xem cảnh báo** realtime nếu cấu hình mất cân bằng:
  - Không có Sói
  - Sói chiếm > 40% tổng ghế
  - Role xung đột (VD: có cả Tiên Tri và Tiên Tri Bí Ẩn)
  - Số ghế < `min_players`

UI hiển thị thống kê realtime: tổng số role, số theo từng phe, số ghế còn trống (chưa có role).

### Cài đặt bổ sung của Host (áp dụng cho mọi kịch bản)

| Cài đặt | Giá trị mặc định | Khoảng cho phép |
|---|---|---|
| Thời gian thảo luận ngày | 5 phút | 2–10 phút |
| Thời gian có thể vote sớm | Sau 3 phút | Sau 1 phút đến hết thời gian |
| Thời gian bỏ phiếu ngày | 60 giây | 30–120 giây |
| Thời gian hành động đêm | 60 giây | 30–120 giây |
| Reveal role khi chết | Tắt | Bật/Tắt |

---

## Danh sách kịch bản có sẵn

### Classic

**Gợi ý:** 9 người · **Khoảng hợp lệ:** 6–15 người

**Role gốc (9 người):** 2 Sói, Tiên Tri, Bảo Vệ, Phù Thủy, Thợ Săn, 3 Dân thường.

Kịch bản cơ bản, cân bằng tốt, phù hợp người mới. `fill_strategy: PROPORTIONAL` — khi tăng người, thêm Dân thường và Sói theo tỉ lệ, sau đó bổ sung role hỗ trợ.

*Gợi ý tùy chỉnh: hoán 1 Dân thường lấy Con Lai để thêm misdirection đầu ván.*

---

### Fairy-Tale Village

**Gợi ý:** 12 người · **Khoảng hợp lệ:** 9–16 người

**Role gốc (12 người):** Nền Classic mở rộng + Bà Ngoại + Khăn Đỏ (2 ghế riêng, nhận ra nhau từ đêm 1).

Bà Ngoại và Khăn Đỏ gán ngẫu nhiên, không công bố ai nhận role này. `fill_strategy: PROPORTIONAL`, giữ cặp Bà Ngoại/Khăn Đỏ khi điều chỉnh số người.

*Gợi ý tùy chỉnh: thêm Hoàng Tử hoặc Cupid để đậm chất cổ tích.*

---

### Mystery Village

**Gợi ý:** 9 người · **Khoảng hợp lệ:** 7–12 người

**Role gốc (9 người):** Dân thường, Bảo Vệ, Phù Thủy, Thợ Săn, Pháp Sư. **Không có Sói, không có role điều tra.**

Mỗi đêm hệ thống âm thầm chọn 1 "nạn nhân ảo" (vẫn chịu tác động Guard/Witch). Dân làng thắng nếu có người công khai tuyên bố đúng bản chất kịch bản trước khi chỉ còn 2 người sống.

*Lưu ý: `fill_strategy: VILLAGER_FIRST` — không tự động thêm Sói khi tăng người.*

---

### Massacre Village

**Gợi ý:** 20 người · **Khoảng hợp lệ:** 15–24 người

**Role gốc (20 người):** Mọi người đều có role có kỹ năng sát thương (Sói, Khủng Bố, Con Bạc, Ma Cà Rồng, Chủ Giáo Phái, Cupid...).

**Luật đặc biệt:** người chơi không được hỏi trực tiếp role của nhau — chỉ Tiên Tri và Thợ Săn được phép công khai nói role mình. Luật này hiển thị như reminder ở đầu mỗi phase thảo luận.

---

### Twin Villages

**Gợi ý:** 20 người · **Khoảng hợp lệ:** 16–26 người

**Role gốc (20 người):** Chia ngẫu nhiên thành 2 làng độc lập, không tương tác chéo.

**Luật đặc biệt:**
- Mỗi ngày 1 người có thể xin chuyển làng (tối đa 2 lần/người); làng nhận biểu quyết chấp nhận/từ chối.
- Dân thắng nếu tiêu diệt hết Sói **và** đông hơn làng còn lại.
- Nếu toàn bộ Sói từ 1 làng di cư sang làng kia, làng bị bỏ trống thắng ngay.

*Gợi ý: cố ý chia Song Sinh sang 2 làng khác nhau.*

---

### Chaos Slums

**Gợi ý:** 12 người · **Khoảng hợp lệ:** 9–16 người

**Role gốc (12 người):** Bợm Nhậu, Con Bạc, Thám Tử, Kẻ Chán Đời + nền tối thiểu (Sói, Tiên Tri, Bảo Vệ).

Chủ đề không tin tưởng, thông tin nhiễu. `fill_strategy: THEMATIC` — ưu tiên thêm role có yếu tố ngẫu nhiên hoặc gây nhiễu thông tin.

*Gợi ý: Mụ Già, Kẻ Phá Rối, Sói Cô Độc.*

---

### Medieval Village

**Gợi ý:** 16 người · **Khoảng hợp lệ:** 12–20 người

**Role gốc (16 người):** Không có Sói. Thay bằng số lượng Phù Thủy phe Ác tương đương — **không biết nhau**. Phù Thủy phe Dân nhận 2 bình. Không có role tâm linh/ma thuật.

**Cơ chế hành động đêm của Phù Thủy Ác** — Host chọn 1 trong 3 option khi cấu hình:
1. Hệ thống chọn ngẫu nhiên 1 Phù Thủy Ác hành động mỗi đêm.
2. Mỗi người vote mục tiêu độc lập; hệ thống thực hiện mục tiêu nhiều phiếu nhất.
3. Mỗi người hành động hoàn toàn độc lập, có thể tạo nhiều nạn nhân/đêm.

---

### Full Chaos

**Gợi ý:** 20 người · **Khoảng hợp lệ:** 10–30 người

**Role gốc:** Gán ngẫu nhiên hoàn toàn. `fill_strategy: RANDOM`.

*Gợi ý: vẫn nên đặt sàn/trần số Sói (tối thiểu 2, tối đa 40% tổng ghế).*

---

## Schema `Scenario`

```python
@dataclass
class Scenario:
    id: str
    name: str
    suggested_players: int
    min_players: int
    max_players: int
    base_roles: list[str]           # role IDs cho suggested_players
    fill_strategy: FillStrategy     # PROPORTIONAL | VILLAGER_FIRST | THEMATIC | RANDOM
    custom_rules: dict              # luật đặc biệt của kịch bản
    win_condition_fn: Callable      # hàm kiểm tra điều kiện thắng
    allow_role_edit: bool = True
```

`ScenarioFiller.fill(scenario, target_count) -> list[str]` trả về danh sách role đề xuất. Host xem đề xuất này và chỉnh sửa trước khi bắt đầu.

### FillStrategy.PROPORTIONAL — thuật toán

1. Tính tỉ lệ phe gốc từ `base_roles` (VD: 7 Dân / 2 Sói = 3.5:1).
2. Với mỗi người tăng thêm: thêm Sói nếu tỉ lệ hiện tại > tỉ lệ gốc, ngược lại thêm Dân thường.
3. Sau khi đủ số người: nếu còn ghế Dân thường "trống chức năng", đề xuất thay bằng role hỗ trợ phù hợp chủ đề kịch bản.
4. Không bao giờ tự động thêm role Trung lập — Host phải thêm thủ công.
