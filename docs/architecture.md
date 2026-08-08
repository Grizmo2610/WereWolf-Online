# System Architecture — Werewolf Online

## 1. Overview & Core Loop

**Werewolf Online** is a real-time multiplayer social deduction game (Werewolf / Mafia) where players join rooms via room codes using web browsers or the Android mobile app.

- **Host (Room Creator):** Sits at a seat and plays along with everyone else. Manages game setup, scenario configuration, and starts the match.
- **Core Loop:** 
  $$\text{Night Actions (simultaneous, max 60s)} \rightarrow \text{Day Discussion (5 min, early vote enabled after 3m)} \rightarrow \text{Voting (max 60s)} \rightarrow \text{Repeat}$$

---

## 2. Technology Stack

### Backend (`/backend`)
- **FastAPI (Python):** High-performance asynchronous web framework handling REST endpoints and real-time WebSocket connections.
- **Cloudflare D1 (SQLite-compatible):** Serverless SQL database storing user accounts, game history, and state snapshots.
- **bcrypt & JWT:** Secure password hashing and httpOnly session cookies for authentication.

### Frontend (`/frontend`)
- **React 18 + Vite:** Component-based UI and blazing fast builds.
- **TailwindCSS:** Responsive mobile-first styling.
- **Zustand:** Lightweight global state management for game states and WebSocket events.
- **Cloudflare Pages:** High-performance static hosting for the React web client.

### Android App (`/android`)
- **Kotlin & Jetpack Compose:** Native Android mobile client built in Android Studio.

### Infrastructure
- **Render Free Tier:** Hosts the FastAPI backend service (512MB RAM, 0.1 vCPU).
- **Cloudflare Worker (Cron):** Pings `/health` every 10 minutes to prevent Render free tier spin-down.

---

## 3. Key Architecture Decisions

### 3.1 Backend as Single Source of Truth
Private role information is transmitted via WebSocket exclusively to the target player's device. The backend maintains the authoritative `GameState`. Frontend clients only render received events and never have visibility into other players' secret roles.

### 3.2 Server Overload Protection (`room_manager.py`)
To prevent crashes on resource-constrained free tiers, resource checks are performed before accepting connections or creating rooms:
```python
import psutil

def can_accept_connection() -> bool:
    return (
        psutil.virtual_memory().percent < 80 and
        psutil.cpu_percent(interval=0.1) < 85
    )
```

### 3.3 Game State Persistence & Resume
Game states are snapshotted into Cloudflare D1 at the end of every phase (encrypted with AES-256). In case of server restarts, hosts can reconnect and resume the match seamlessly.

### 3.4 Client-Side Mention Highlighting
Mention parsing and highlighting (`@seat_id` or display name) are handled entirely on the frontend via custom React hooks (`useMentionHighlight.js`) without backend overhead.
