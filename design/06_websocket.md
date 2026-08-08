# 06 - WebSocket Events

## 1. Tổng quan

Mọi giao tiếp realtime giữa server và client đều qua WebSocket. Endpoint: `ws://{host}/ws/{room_code}`.

Tất cả event có shape thống nhất:
```json
{ "type": "EVENT_TYPE", "payload": { ... } }
```

Event types định nghĩa trong `backend/ws/events.py` như string constants — dùng chung cho cả BE (broadcast) và FE (switch/case). FE import types từ `frontend/src/config/wsEvents.js`.

---

## 2. Server → Client

### Phòng chờ

| Event | Gửi tới | Payload |
|---|---|---|
| `ROOM_UPDATE` | Broadcast phòng | `players: [{seat_id, display_name, is_ready}]`, `host_seat_id` |
| `SERVER_OVERLOAD` | 1 người (đang join) | `message: string` |

### Bắt đầu ván

| Event | Gửi tới | Payload |
|---|---|---|
| `GAME_START` | Broadcast | `total_players`, `role_counts`, `faction_counts`, `timing_rules`, `role_descriptions` |
| `ROLE_ASSIGNED` | Riêng tư (1 người) | `role_id`, `role_meta`, `ally_info` (đồng đội nếu có) |
| `WOLF_SEATS` | Riêng tư (Sói) | `wolf_seat_ids: int[]` |

### Phase & timing

| Event | Gửi tới | Payload |
|---|---|---|
| `PHASE_CHANGE` | Broadcast | `phase`, `round`, `duration_seconds`, `started_at` (ISO 8601) |
| `NIGHT_ACTION_REQUEST` | Riêng tư (người có action) | `action_type`, `valid_targets: int[]`, `can_change: true` |

### Chat & speech

| Event | Gửi tới | Payload |
|---|---|---|
| `PLAYER_SPEAK` | Broadcast (người sống) | `seat_id`, `display_name`, `text`, `channel: 'public'` |
| `DEAD_CHAT` | Chỉ người chết | `seat_id`, `display_name`, `text`, `channel: 'dead'` |

### Vote

| Event | Gửi tới | Payload |
|---|---|---|
| `VOTE_UPDATE` | Broadcast | `counts: { seat_id: vote_count }`, `total_voted`, `total_eligible` |
| `SKIP_VOTE_UPDATE` | Broadcast | `skip_count`, `required` (>50% người sống) |

### Kết quả phase & game

| Event | Gửi tới | Payload |
|---|---|---|
| `PHASE_RESULT` | Broadcast | `deaths: [{seat_id, display_name, cause, role?}]`, `no_kill: bool` |
| `GAME_END` | Broadcast | `winner_faction`, `all_roles: [{seat_id, display_name, role_id}]` |

### Kết nối & host

| Event | Gửi tới | Payload |
|---|---|---|
| `PLAYER_DISCONNECTED` | Broadcast | `seat_id`, `afk_countdown_seconds: 30` |
| `PLAYER_RECONNECTED` | Broadcast | `seat_id` |
| `HOST_TRANSFERRED` | Broadcast | `new_host_seat_id` |
| `RESUME_AVAILABLE` | Riêng tư (Host) | `room_code`, `snapshot_phase`, `round_number` |
| `GAME_STATE_SYNC` | Riêng tư (người reconnect) | `phase`, `round`, `alive_seats`, `public_history`, `time_remaining_seconds` |

---

## 3. Client → Server

### Phòng chờ

| Event | Gửi khi | Payload |
|---|---|---|
| `READY` | Nhấn Sẵn sàng | — |
| `START_GAME` | Host bắt đầu | — |

### Ban đêm

| Event | Gửi khi | Payload |
|---|---|---|
| `NIGHT_ACTION` | Submit hành động đêm | `target_seat: int` |
| `CHANGE_NIGHT_ACTION` | Đổi lại trước khi hết 60s | `target_seat: int` |
| `WOLF_VOTE` | Sói vote mục tiêu | `target_seat: int` |
| `CHANGE_WOLF_VOTE` | Sói đổi vote | `target_seat: int` |

### Ban ngày

| Event | Gửi khi | Payload |
|---|---|---|
| `DAY_SPEAK` | Gửi tin chat | `text: string`, `channel: 'public' \| 'dead'` |
| `SKIP_DISCUSSION` | Nhấn "Bỏ qua thảo luận" | — |

### Bỏ phiếu

| Event | Gửi khi | Payload |
|---|---|---|
| `VOTE` | Bỏ phiếu trục xuất | `target_seat: int \| null` (null = phiếu trắng) |
| `CHANGE_VOTE` | Đổi phiếu trước khi hết 60s | `target_seat: int \| null` |

### Misc

| Event | Gửi khi | Payload |
|---|---|---|
| `RESUME_GAME` | Host nhấn Resume | — |

---

## 4. Validation

Mọi event nhận từ client đều được **validate phía BE** trước khi xử lý:
- Đúng phase (VD: `WOLF_VOTE` chỉ hợp lệ trong phase đêm).
- Đúng người gửi (VD: `WOLF_VOTE` chỉ hợp lệ từ người có role Sói).
- Target hợp lệ (VD: không vote chính mình, không vote người chết, Sói không vote Sói khác).
- Người đã chết không được gửi `DAY_SPEAK` channel `public`.

FE cũng disable các action không hợp lệ để tránh gửi nhầm — nhưng BE là lớp validation cuối cùng, không tin tưởng hoàn toàn vào FE.
