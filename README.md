# Werewolf Online (Sói Già Online)

A full-stack multiplayer social deduction game (Werewolf / Mafia) featuring a high-performance Python backend, a modern React web frontend, and a native Android mobile client.

## Architecture Overview

- **Backend (`/backend`):** Python (FastAPI / WebSockets) handling real-time game logic, rooms, state management, and authentication.
- **Frontend (`/frontend`):** React (Vite / Tailwind CSS) providing a responsive web interface for players and hosts.
- **Android App (`/android`):** Native Android application built with Kotlin and Jetpack Compose / Android Studio for mobile users.
- **Design Docs (`/design`):** Comprehensive specifications including architecture, game engine, database schema, WebSocket protocols, authentication, UI/UX, and infrastructure.

## Project Structure

```
WereWolf/
├── backend/          # Python backend service
├── frontend/         # React web client
├── android/          # Android Studio mobile application
├── design/           # System design & architecture documents
├── .gitignore
├── LICENSE
└── README.md
```

## Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+ & npm / yarn
- Android Studio (Flamingo or newer) with Android SDK

### Backend Setup
```bash
cd backend
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Unix/macOS:
# source venv/bin/activate
pip install -r requirements.txt
python main.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Android Setup
Open the `android/` directory in **Android Studio**, let Gradle sync dependencies, and run the app on an emulator or physical device.

## License

This project is licensed under the [MIT License](LICENSE).
