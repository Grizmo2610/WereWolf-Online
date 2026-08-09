# 05 - Database (Cloudflare D1)

## 1. Tổng quan

Storage dùng **Cloudflare D1** — SQLite-compatible, truy cập từ backend Python qua HTTP REST API. Không dùng ORM, chỉ raw SQL qua `D1Client`.

---

## 2. Kết nối — `d1_client.py`

```
POST https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/d1/database/{DB_ID}/query
Authorization: Bearer {API_TOKEN}
Content-Type: application/json
Body: { "sql": "...", "params": [...] }
```

Cấu hình từ `.env`: `D1_ACCOUNT_ID`, `D1_DATABASE_ID`, `D1_API_TOKEN`.

### Interface

```python
class D1Client:
    async def execute(self, sql: str, params: list = []) -> dict
        # INSERT / UPDATE / DELETE

    async def query(self, sql: str, params: list = []) -> list[dict]
        # SELECT — trả list of row dicts

    async def execute_batch(self, statements: list[dict]) -> list
        # Multi-statement, dùng cho các thao tác cần atomic
        # statements = [{"sql": "...", "params": [...]}, ...]
```

**Quan trọng:** Mọi query đều dùng parameterized statements (`?` placeholder). Không bao giờ format string SQL trực tiếp — SQL injection prevention.

---

## 3. Schema

### `users`
```sql
CREATE TABLE users (
    id            TEXT PRIMARY KEY,   -- UUID v4
    username      TEXT UNIQUE NOT NULL,
    display_name  TEXT NOT NULL,      -- fallback về username nếu để trống khi đăng ký
    password_hash TEXT NOT NULL,
    created_at    TEXT NOT NULL       -- ISO 8601
);
```

### `game_records`
```sql
CREATE TABLE game_records (
    id              TEXT PRIMARY KEY,
    room_code       TEXT NOT NULL,
    scenario_id     TEXT NOT NULL,
    total_players   INTEGER NOT NULL,
    started_at      TEXT NOT NULL,
    ended_at        TEXT,
    winner_faction  TEXT,             -- 'villagers'|'wolves'|'neutral'|'cancelled'
    status          TEXT NOT NULL,    -- 'in_progress'|'finished'|'cancelled'
    reveal_on_death INTEGER NOT NULL  -- 0|1
);
```

### `player_records`
```sql
CREATE TABLE player_records (
    id                TEXT PRIMARY KEY,
    game_id           TEXT NOT NULL REFERENCES game_records(id),
    user_id           TEXT NOT NULL REFERENCES users(id),
    seat_id           INTEGER NOT NULL,
    role_id           TEXT NOT NULL,
    alive_until_round INTEGER,        -- NULL nếu sống đến cuối ván
    eliminated_by     TEXT            -- 'wolf_bite'|'lynch'|'witch_poison'|...
);
```

### `round_logs`
```sql
CREATE TABLE round_logs (
    id              TEXT PRIMARY KEY,
    game_id         TEXT NOT NULL REFERENCES game_records(id),
    round_number    INTEGER NOT NULL,
    phase           TEXT NOT NULL,    -- 'night'|'discussion'|'vote'
    summary_public  TEXT              -- VD: "Đêm 2: ghế 3 bị cắn chết"
);
```

### `speech_logs`
```sql
CREATE TABLE speech_logs (
    id           TEXT PRIMARY KEY,
    game_id      TEXT NOT NULL,
    round_id     TEXT NOT NULL,
    user_id      TEXT NOT NULL,
    seat_id      INTEGER NOT NULL,
    channel      TEXT NOT NULL,       -- 'public'|'dead'
    spoken_text  TEXT NOT NULL,
    timestamp    TEXT NOT NULL
);
```

### `action_logs`
```sql
CREATE TABLE action_logs (
    id           TEXT PRIMARY KEY,
    game_id      TEXT NOT NULL,
    round_id     TEXT NOT NULL,
    user_id      TEXT NOT NULL,
    action_type  TEXT NOT NULL,       -- 'night_action'|'vote'|'wolf_vote'|'skip_vote'
    target_seat  INTEGER,             -- NULL nếu phiếu trắng hoặc không hành động
    timestamp    TEXT NOT NULL
);
```

### `game_snapshots`
```sql
CREATE TABLE game_snapshots (
    id               TEXT PRIMARY KEY,
    game_id          TEXT NOT NULL REFERENCES game_records(id),
    room_code        TEXT NOT NULL,
    round_number     INTEGER NOT NULL,
    phase            TEXT NOT NULL,   -- 'night_resolved'|'discussion_end'|'vote_end'
    state_encrypted  TEXT NOT NULL,   -- JSON encrypt AES-256
    saved_at         TEXT NOT NULL
);
```

### `api_keys` *(placeholder — chưa dùng)*
```sql
CREATE TABLE api_keys (
    id            TEXT PRIMARY KEY,
    provider_name TEXT NOT NULL,
    key_value     TEXT NOT NULL,
    alias         TEXT,
    is_active     INTEGER DEFAULT 1,
    is_exhausted  INTEGER DEFAULT 0,
    last_used_at  TEXT,
    added_at      TEXT NOT NULL
);
```

---

## 4. Index

```sql
CREATE INDEX idx_snapshots_room ON game_snapshots(room_code, saved_at DESC);
CREATE INDEX idx_speech_game    ON speech_logs(game_id, round_id);
CREATE INDEX idx_action_game    ON action_logs(game_id, round_id);
CREATE INDEX idx_player_game    ON player_records(game_id);
```

---

## 5. Snapshot retention

Giữ tối đa **3 checkpoint gần nhất** mỗi ván. Sau mỗi lần ghi snapshot mới, xóa các snapshot cũ hơn của cùng `game_id` nếu tổng số > 3. Dùng `execute_batch` để ghi mới + xóa cũ trong một lần gọi API.
