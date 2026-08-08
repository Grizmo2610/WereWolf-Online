# REST API & WebSocket Reference — Werewolf Online

## 1. REST API (Authentication & Rooms)

Base URL: `https://api.werewolf-online.example/api` (or `http://localhost:8000/api`)

### Auth Endpoints
- `POST /auth/register` — Register a new account (`username`, `display_name`, `password`).
- `POST /auth/login` — Authenticate and receive httpOnly JWT session cookie.
- `POST /auth/logout` — Clear session.

### Room Management
- `POST /rooms` — Create a new game room.
- `GET /rooms/{room_code}` — Get room status and player list.

---

## 2. WebSocket Protocol

Endpoint: `ws://{host}/ws/{room_code}`

All WebSocket messages follow a strict JSON schema:
```json
{ "type": "EVENT_TYPE", "payload": { ... } }
```

### Server → Client Events

#### Lobby & Setup
- `ROOM_UPDATE`: Broadcasts current player seats, display names, ready status, and host seat ID.
- `SERVER_OVERLOAD`: Sent to newly connecting users when server resource usage exceeds thresholds.

#### Game Start & Roles
- `GAME_START`: Broadcasts total players, role counts, faction counts, and timing rules.
- `ROLE_ASSIGNED` (Private): Sends player's secret role, meta information, and ally info.
- `WOLF_SEATS` (Private): Sent to werewolf players with fellow wolf seat IDs.

#### Phase & Timing
- `PHASE_CHANGE`: Broadcasts current phase (`night`, `day`, `vote`), round number, and duration.
- `NIGHT_ACTION_REQUEST` (Private): Sent to players with active night abilities (`valid_targets`, `action_type`).

#### Chat & Communication
- `PLAYER_SPEAK`: Broadcasts public speech during day discussion.
- `DEAD_CHAT`: Broadcasts messages within the deceased chat channel.

#### Voting
- `VOTE_UPDATE`: Live vote tally broadcast (`counts`, `total_voted`, `total_eligible`).
- `SKIP_VOTE_UPDATE`: Broadcasts early discussion skip votes.

#### Game End & Reconnection
- `PHASE_RESULT`: Announces deaths, causes, and revealed roles at the end of a phase.
- `GAME_END`: Declares winning faction and reveals all player roles.
- `RESUME_AVAILABLE` (Private to Host): Notifies host that a previous game snapshot can be resumed.
- `GAME_STATE_SYNC` (Private): Restores game state upon player reconnection.

---

### Client → Server Events

- `READY`: Mark player as ready in lobby.
- `START_GAME` (Host only): Launch the match.
- `NIGHT_ACTION` / `CHANGE_NIGHT_ACTION`: Submit or update night target.
- `WOLF_VOTE` / `CHANGE_WOLF_VOTE`: Werewolf coordination vote.
- `DAY_SPEAK`: Send public or dead channel chat message.
- `SKIP_DISCUSSION`: Request early discussion skip.
- `VOTE` / `CHANGE_VOTE`: Cast or change exile vote during voting phase.
- `RESUME_GAME`: Host command to restore saved game snapshot.

---

## 3. Validation Rules
The backend validates every incoming client event:
- **Phase Validation:** Actions are strictly restricted to their valid phase (e.g., `WOLF_VOTE` only during night).
- **Role Permissions:** Actions verified against sender's assigned role.
- **Target Validity:** Self-targeting prevention, dead player restrictions, and faction targeting rules.
