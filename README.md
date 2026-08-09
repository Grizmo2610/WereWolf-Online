<!-- Improved compatibility of back to top link -->

<a id="readme-top"></a>

[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![project\_license][license-shield]][license-url]

<br />
<div align="center">
  <a href="https://github.com/Grizmo2610/WereWolf-Online">
    <img src="images/Werewolf-logo.png" alt="Logo" width="80" height="80">
  </a>

<h3 align="center">Werewolf Online (Sói Già Online)</h3>

  <p align="center">
    Real-time multiplayer social deduction party game — Werewolf / Mafia
    <br />
    <a href="design/00_overview_and_architecture.md"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/Grizmo2610/WereWolf-Online">View Demo</a>
    &middot;
    <a href="https://github.com/Grizmo2610/WereWolf-Online/issues/new?labels=bug&template=bug-report.md">Report Bug</a>
    &middot;
    <a href="https://github.com/Grizmo2610/WereWolf-Online/issues/new?labels=enhancement&template=feature-request.md">Request Feature</a>
  </p>
</div>

---

## About The Project

[![Product Name Screen Shot][product-screenshot]](https://github.com/Grizmo2610/WereWolf-Online)

**Werewolf Online** is a real-time multiplayer social deduction party game where villagers and werewolves battle in real-time. Players are assigned secret roles, engage in discussions, and vote to eliminate suspected werewolves before night falls and claims another victim.

The project features a robust multi-platform architecture:
1. **Python Backend (`/backend`)**: High-performance FastAPI & WebSocket server managing game rooms, state transitions, and rules with server overload protection.
2. **React Web Frontend (`/frontend`)**: Modern web client built with Vite and Tailwind CSS for seamless browser play.
3. **Android Mobile App (`/android`)**: Native Android application built with Kotlin and Jetpack Compose.
4. **Design Specifications (`/design`)**: Comprehensive system design documents covering architecture, game engine, database, WebSocket protocols, authentication, and UI/UX.

### Core Features

* **Real-time Multiplayer**: Powered by Python WebSockets for instant synchronization across devices.
* **Role Management**: Villagers, Werewolves, Seer, Bodyguard, Witch, and more.
* **Day & Night Cycles**: Automated phase transitions with timer indicators and voting logic.
* **Server Overload Protection**: `room_manager.py` verifies CPU (<85%) and memory (<80%) thresholds before accepting room creations or connections.
* **Cross-Platform Support**: Accessible via web browsers and native Android application.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## Documentation

Explore the system design and architecture documents:
* 🏛️ [Overview & Architecture](design/00_overview_and_architecture.md)
* 🐺 [Characters & Roles](design/01_characters.md)
* 📜 [Scenarios & Rules](design/02_scenarios.md)
* ⚙️ [Game Engine](design/03_game_engine.md)
* 🔐 [Authentication](design/04_auth.md)
* 🗄️ [Database Schema](design/05_database.md)
* 🔌 [WebSocket Protocol](design/06_websocket.md)
* 🎨 [UI/UX Design](design/07_ui.md)
* ☁️ [Infrastructure](design/08_infrastructure.md)
* 📝 [Code Style](design/09_code_style.md)
* 📋 [Changelog](CHANGELOG.md)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## Built With

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-0.100%2B-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/WebSocket-Realtime-orange?style=for-the-badge" />
  <img src="https://img.shields.io/badge/React-18%2B-61DAFB?style=for-the-badge&logo=react&logoColor=white" />
  <img src="https://img.shields.io/badge/Vite-Frontend-646CFF?style=for-the-badge&logo=vite&logoColor=white" />
  <img src="https://img.shields.io/badge/Kotlin-Android-7F52FF?style=for-the-badge&logo=kotlin&logoColor=white" />
  <img src="https://img.shields.io/badge/TailwindCSS-Styling-38Bdf8?style=for-the-badge&logo=tailwindcss&logoColor=white" />
</p>

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## Getting Started & Installation

### Prerequisites

* Python 3.10+
* Node.js 18+ & npm / yarn
* Android Studio (Flamingo or newer) with Android SDK

### 1. Clone the Repository

```sh
git clone https://github.com/Grizmo2610/WereWolf-Online.git
```

2. Open the project folder

```sh
cd WereWolf-Online
```

### 2. Run the Backend (Python FastAPI)

```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
# source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

### 3. Run the Frontend (React Web Client)

```bash
cd frontend
npm install
echo "VITE_API_BASE=http://localhost:8000" > .env
npm run dev
```

### 4. Run the Android App

Open the `android/` directory in **Android Studio**, wait for Gradle sync to complete, and run the app on an emulator or physical device.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## Usage

### Game Flow

1. **Host Setup** — Host creates a room, configures scenarios and roles.
2. **Joining** — Players join via room code and take seats.
3. **Night Phase** — Secret night actions (Werewolves hunt, Seer inspects, Bodyguard protects, Witch heals/poisons).
4. **Day Phase** — Discussion and player debate (with early skip support).
5. **Voting** — Players vote to eliminate a suspected werewolf.
6. **Victory Condition** — Game repeats until all werewolves are eliminated (Villagers win) or werewolves equal/outnumber villagers (Werewolves win).

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## Roadmap

* [x] System architecture and design documentation
* [x] Python backend & WebSocket game engine setup
* [x] React web frontend skeleton & state stores
* [x] Android Studio mobile app structure
* [x] Full role ability implementation (Seer, Witch, Guard, etc.)
* [x] User authentication & statistics tracking
* [ ] Polished UI/UX animations and sound effects
* [ ] Production cloud deployment (Render + Cloudflare Pages)

See the [open issues](https://github.com/Grizmo2610/WereWolf-Online/issues) for a full list of proposed features and known issues.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## Contributing

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

### Top Contributors:

<a href="https://github.com/Grizmo2610/WereWolf-Online/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=Grizmo2610/WereWolf-Online" />
</a>

---

## License

Distributed under the MIT License. See [LICENSE](LICENSE) for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## Contact

Grizmo2610 - [hoangtuantu893@gmail.com](mailto:hoangtuantu893@gmail.com)

Project Link: [https://github.com/Grizmo2610/WereWolf-Online](https://github.com/Grizmo2610/WereWolf-Online)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## Acknowledgments

* Classic Werewolf / Mafia party game rules
* FastAPI & Python ecosystem
* React & Android developer communities

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

[contributors-shield]: https://img.shields.io/github/contributors/Grizmo2610/WereWolf-Online.svg?style=for-the-badge
[contributors-url]: https://github.com/Grizmo2610/WereWolf-Online/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/Grizmo2610/WereWolf-Online.svg?style=for-the-badge
[forks-url]: https://github.com/Grizmo2610/WereWolf-Online/network/members
[stars-shield]: https://img.shields.io/github/stars/Grizmo2610/WereWolf-Online.svg?style=for-the-badge
[stars-url]: https://github.com/Grizmo2610/WereWolf-Online/stargazers
[issues-shield]: https://img.shields.io/github/issues/Grizmo2610/WereWolf-Online.svg?style=for-the-badge
[issues-url]: https://github.com/Grizmo2610/WereWolf-Online/issues
[license-shield]: https://img.shields.io/github/license/Grizmo2610/WereWolf-Online.svg?style=for-the-badge
[license-url]: https://github.com/Grizmo2610/WereWolf-Online/blob/main/LICENSE
[product-screenshot]: images/screenshot.png
