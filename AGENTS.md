# AGENTS.md — Instructions & Context for AI Coding Assistants

> **Notice for AI Agents:** Read this file to instantly understand the architecture, tech stack, game mechanics, and coding conventions of Werewolf Online without reading the entire repository.

---

## 1. Project Overview & Architecture

**Werewolf Online** is a real-time multiplayer social deduction game (Werewolf / Mafia) where human players connect to game rooms via web browsers or Android app using room codes.

- **Host:** A regular player who sits at a seat, configures scenarios, and starts the match. No separate admin role.
- **Core Loop:** Night Actions (simultaneous, max 60s) $\rightarrow$ Day Discussion (5 min, early skip enabled after 3m) $\rightarrow$ Voting (max 60s) $\rightarrow$ Repeat until win condition met.

### Tech Stack
- **Backend (`/backend`):** FastAPI (Python), WebSocket (real-time), Cloudflare D1 (SQLite database), bcrypt + JWT.
- **Frontend (`/frontend`):** React 18 + Vite, TailwindCSS, Zustand (global state), Cloudflare Pages.
- **Android (`/android`):** Kotlin, Jetpack Compose, Android Studio.
- **Infrastructure:** Render (FastAPI hosting), Cloudflare Workers (Cron keep-alive ping).

---

## 2. Core Architecture Rules

1. **Backend as Source of Truth:** Secret roles are sent via WebSocket exclusively to the target player's device. The backend maintains the authoritative `GameState`. Frontend renders events and never accesses other players' roles.
2. **Server Overload Protection:** `room_manager.py` checks CPU (<85%) and memory (<80%) before accepting connections or creating rooms.
3. **State Persistence:** Game state snapshots are saved to Cloudflare D1 at phase ends, allowing hosts to resume after server restarts.
4. **Mention Highlighting:** `@seat_id` or display name mentions are parsed entirely client-side via React hooks (`useMentionHighlight.js`).

---

## 3. Code Style & Conventions (`design/09_code_style.md`)

### Language Rules
- **UI text, messages, toasts, banners:** Vietnamese.
- **Code (variables, functions, classes, modules):** English.
- **Code comments:** English.
- **Design & documentation docs:** Vietnamese.

### Comments
- **Minimize comments.** Good code is self-documenting.
- **Do not** write file summaries, full docstrings for every function, or state-the-obvious comments.
- **Do** write 1-line comments for complex/non-obvious logic explaining *why*, not *what*.

### Function Separation
- **Single Responsibility:** 1 function = 1 job. Avoid functions that mix validation, DB queries, and WebSocket broadcasting.
- Keep functions concise (~30-40 lines max).

### Naming & Conventions
- **Python:** `snake_case` for variables/functions, `PascalCase` for classes, `UPPER_SNAKE_CASE` for constants. File names: `snake_case.py`.
- **JavaScript/React:** `camelCase` for variables/functions, `PascalCase` for components (`.jsx`), custom hooks start with `use`.
- **No abbreviations:** Use clear names (`can_accept_connection()` instead of `chk_conn()`).

---

## 4. Key File Structure Quick Reference

```
WereWolf/
├── backend/              # Python FastAPI backend
│   ├── main.py           # FastAPI entrypoint
│   ├── game.py           # GameState & round loop
│   ├── resolver.py       # Night action & death resolution
│   ├── vote.py           # Voting logic
│   ├── room_manager.py   # Room creation & load check
│   ├── roles/            # Role implementations
│   └── ws/               # WebSocket router & events
├── frontend/             # React + Vite web client
│   └── src/
│       ├── store/        # Zustand state stores
│       ├── hooks/        # Custom React hooks (WS, timer, mention)
│       └── components/   # Game UI, chat, phase overlays
├── android/              # Native Android App (Kotlin / Jetpack Compose)
└── design/               # Detailed design specifications (00 to 09)
```

## 5. Commit and Git

* DO NOT commit changes automatically.
* Only commit when the user explicitly asks you to commit.
* If the user does not explicitly request a commit, make the required changes and stop.
* Never create a commit as part of another task unless explicitly instructed.