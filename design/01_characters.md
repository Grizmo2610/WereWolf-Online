# 01 - Nhân vật (Role)

Ba phe: Dân làng, Sói, Trung lập. Mỗi role map tới một subclass `Role` trong `backend/roles/`. Tên tiếng Việt giữ nguyên song song với tiếng Anh — văn bản trong game hiển thị tiếng Việt.

---

## Phe Dân làng (`backend/roles/villagers.py`)

| Role | Tên tiếng Việt | Mô tả |
|---|---|---|
| Villager | Dân thường | Không có kỹ năng đặc biệt. Chỉ thảo luận và bỏ phiếu. |
| Seer | Tiên Tri | Mỗi đêm chọn 1 người, biết được phe của họ. |
| Apprentice Seer | Tiên Tri Tập Sự | Ngủ yên cho đến khi Tiên Tri thật chết — kế thừa kỹ năng của Tiên Tri. |
| Mystic Seer | Tiên Tri Bí Ẩn | Phiên bản mạnh hơn: biết đúng role, không chỉ phe. |
| Clairvoyant | Ngoại Cảm | Mỗi đêm chọn 2 người, biết 2 người đó có cùng phe không (không biết phe nào). |
| Detective | Thám Tử | Dùng một lần: biết mục tiêu (hoặc láng giềng sống gần nhất) có phải Sói không. |
| Ghost | Hồn Ma | Chết đêm 1; có thể nhìn thấy kênh chat người chết; được nói đúng 1 từ mỗi ngày trong kênh công khai. |
| Guard | Bảo Vệ | Mỗi đêm bảo vệ 1 người khỏi bị Sói giết. Không được chọn cùng người 2 đêm liên tiếp. |
| Priest | Mục Sư | Dùng một lần: làm mục tiêu miễn nhiễm hoàn toàn với đòn Sói (các nguyên nhân chết khác vẫn áp dụng). |
| Witch | Phù Thủy | 1 bình cứu + 1 bình độc, mỗi bình dùng một lần trong cả ván. |
| Hunter | Thợ Săn | Mỗi đêm đánh dấu 1 mục tiêu; nếu Hunter chết, mục tiêu đã đánh dấu chết theo. |
| Huntress | Nữ Thợ Săn | Dùng một lần: giết 1 người bất kỳ lúc nào trong đêm. |
| Plague Bearer | Người Bị Bệnh | Nếu bị Sói giết, Sói bị "lây bệnh" và bỏ qua lượt giết đêm tiếp theo. |
| Cupid | Cupid | Chỉ đêm 1: liên kết 2 người thành cặp đôi — người này chết thì người kia chết theo, bất kể phe. |
| Terrorist | Khủng Bố | Khi chết, 2 người ngồi cạnh (theo thứ tự ghế) cũng chết theo. |
| Halfbreed | Con Lai | Dân làng thật, nhưng Tiên Tri điều tra thấy là Sói. |
| Cursed | Kẻ Bị Nguyền | Dân làng bình thường; nếu bị Sói cắn, chuyển thành Sói thay vì chết. |
| Clone | Nhân Bản | Đêm 1 chọn mục tiêu; nếu mục tiêu chết, kế thừa role của họ. |
| Grandmother | Bà Ngoại | Dân làng bình thường, được ghép cặp với Khăn Đỏ. |
| Red Hood | Khăn Đỏ | Sau khi Bà Ngoại chết, mỗi đêm biết được danh tính của 1 con Sói. |
| Twins (×2) | Song Sinh | Nhận ra nhau từ đêm 1; thắng riêng nếu là cặp sống sót cuối cùng. |
| Sorcerer | Pháp Sư | Mỗi đêm im lặng hóa 1 người — hôm sau người đó không được nói (vẫn được bỏ phiếu). |
| Old Hag | Mụ Già | Mỗi đêm buộc 1 người nghỉ ngày tiếp theo (không nói, không bỏ phiếu). |
| Prince | Hoàng Tử | Miễn nhiễm với lần bỏ phiếu trục xuất đầu tiên — bị lật bài công khai thay vì chết. |
| Tough Youth | Thanh Niên Cứng | Nếu bị Sói cắn, chết chậm hơn 1 đêm thay vì ngay lập tức. |
| Gambler | Con Bạc | Mỗi đêm (trừ đêm 1): nhắm ngẫu nhiên 1 người — nếu là Sói người đó chết; nếu không, Gambler chết. |
| Drunkard | Bợm Nhậu | Dân làng bình thường; từ đêm 2 có xác suất ngẫu nhiên "tỉnh rượu" và nhận role mới ngẫu nhiên. |

---

## Phe Sói (`backend/roles/wolves.py`)

| Role | Tên tiếng Việt | Mô tả |
|---|---|---|
| Werewolf | Sói | Thấy đồng đội Sói từ đêm 1. Mỗi đêm cùng vote chọn 1 mục tiêu cắn. |
| Alpha Wolf | Sói Đầu Đàn | Một lần/ván: chuyển mục tiêu thành Sói thay vì giết; vô hiệu nếu mục tiêu đang được bảo vệ. |
| Wolf Cub | Sói Con | Khi chết, ngày hôm sau được phép trục xuất 2 người thay vì 1. |
| Lone Wolf | Sói Cô Độc | Hoạt động như Sói thường nhưng có điều kiện thắng riêng: là con Sói cuối cùng còn sống. |
| Vegetarian Wolf | Sói Ăn Chay | Không tham gia vote giết; vẫn thắng cùng phe Sói. |
| Wolf Seer | Sói Tiên Tri | Sói có kỹ năng điều tra phe như Tiên Tri. |
| Medium | Bà Đồng | Không thức cùng đàn; bí mật theo dõi Tiên Tri — trở thành Sói Tiên Tri nếu Tiên Tri thật chết. |

---

## Phe Trung lập (`backend/roles/neutral.py`)

| Role | Tên tiếng Việt | Mô tả |
|---|---|---|
| Fool | Kẻ Chán Đời | Thắng một mình nếu bị trục xuất bằng vote (chỉ nguyên nhân đó mới tính). |
| Solo Killer | Sát Nhân Đơn Độc | Giết 1 người/đêm (không phải Sói); thắng khi là người sống sót duy nhất. |
| Cult Leader | Chủ Giáo Phái | Mỗi đêm chiêu mộ 1 người vào giáo phái; thắng khi tất cả người sống đều là thành viên. |
| Vampire | Ma Cà Rồng | Hút máu 1 người/đêm — cái chết chỉ được công bố sau khi cuộc họp ngày hôm sau kết thúc; vẫn có thể được cứu. |
| Saboteur | Kẻ Phá Rối | Dùng một lần: hoán đổi role của 2 người ngẫu nhiên. |

---

## Ghi chú triển khai

### Role metadata (định nghĩa trong `base.py`)

Mỗi role định nghĩa các thuộc tính sau trên class:

```python
@dataclass
class RoleMeta:
    id: str                  # VD: "werewolf", "seer"
    display_name_vi: str     # Tên tiếng Việt
    faction: Faction         # VILLAGER | WOLF | NEUTRAL
    acts_at_night: bool      # Có hành động đêm không
    first_night_only: bool   # Chỉ hành động đêm 1
    max_uses: int | None     # None = không giới hạn
    priority: int            # Thứ tự resolve (thấp hơn = trước)
    can_target_self: bool    # Có thể tự nhắm vào mình không
    can_target_dead: bool    # Có thể nhắm người chết không
```

### Player.role_state

State thay đổi theo từng người (số bình còn lại, mục tiêu đang theo dõi, đêm cuối bảo vệ ai...) lưu trên `Player.role_state: dict`, không bao giờ lưu trên class `Role` — vì một class có thể share cho nhiều người (VD: nhiều Sói).

### Sói nhận dạng nhau trên UI

Khi đêm bắt đầu, Sói nhận được danh sách `wolf_seat_ids` qua WebSocket (private). FE render tên các ghế Sói với **màu đỏ + nền tối** thay vì trắng bình thường — chỉ client của người Sói nhận được payload này. Sói không thể chọn chính mình hoặc Sói khác làm mục tiêu vote đêm (FE disable + BE validate).

### Reveal role khi chết

Host cấu hình `reveal_on_death: bool` trước khi bắt đầu ván:
- `true` → khi người chơi chết, BE broadcast role của họ kèm event `PLAYER_DEAD`
- `false` → chỉ broadcast tên + nguyên nhân chết; role ẩn đến khi ván kết thúc

### Tooltip mô tả role trong UI phòng chờ

Khi Host cấu hình danh sách role, mỗi role hiển thị tooltip với: tên, phe, mô tả ngắn, các ràng buộc quan trọng (VD: "Không được bảo vệ cùng người 2 đêm liên tiếp"). Dữ liệu tooltip lấy từ `RoleMeta`, không hardcode trên FE.
