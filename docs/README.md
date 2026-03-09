# ⚓ War Galley Digital Engine (v1.2.0)

A high-fidelity, hex-axial naval strategy simulation based on the Hellenistic and Punic eras. Built for secure, networked tactical play and advanced AI engagement.



## ## 1. System Overview
* **Engine:** Python-based axial hex logic ($q, r$ coordinate system).
* **Networking:** Flask-SocketIO with Room-based Lobby isolation.
* **Orchestration:** Optional Podman-Compose / Docker Compose (CIS Level 2 Hardened) *or* standalone native Python.
* **Intelligence:** Minimax Admiral AI (alpha-beta pruned; depth configurable via `AI_DEPTH` env var).
* **Visuals:** Procedural 2D Miniature Generation via Pillow (`asset_gen.py`).

## ## 2. Core Mechanics
* **Wind & Tide:** Dynamic MP modifiers based on vessel facing.
* **Ramming:** Calculated via the GMT table ($angle \times strength$).
* **Boarding:** Roman-exclusive **Corvus** trait for locked melee combat.
* **Artillery:** Ranged stone-thrower mechanics for heavy Successor ships.



## ## 3. Quick Start

Three deployment modes are supported. Choose whichever suits your environment.

---

### Mode 1 — Native Python (Linux / macOS / Windows)

No container runtime required — runs the Flask server directly with Python.

**Linux / macOS:**
```bash
chmod +x launch_game.bash
./launch_game.bash
```

**Windows — Command Prompt:**
```bat
launch_game.bat
```

**Windows — PowerShell (recommended):**
```powershell
.\launch_game.ps1
```
> If you receive an execution policy error, run:
> `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

**Prerequisites:** [Python 3.11+](https://www.python.org/downloads/) with "Add Python to PATH" checked. No container runtime needed.

---

### Mode 2 — Container (Podman or Docker)

Runs the server inside a hardened, rootless container (CIS Level 2).

**Linux / macOS:**
```bash
chmod +x launch_game.bash
./launch_game.bash --container
```

**Windows — Command Prompt:**
```bat
deploy_container.bat
```

**Windows — PowerShell:**
```powershell
.\deploy_container.ps1
```

**Prerequisites:** [Podman Desktop](https://podman-desktop.io/) **or** [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running.

---

### Mode 3 — Standalone Windows Executable (no Python or container required)

Packages the server as a self-contained `wargalley.exe` via PyInstaller. Build once on a machine that has Python, then distribute the `dist\wargalley\` folder to any Windows PC.

**Command Prompt:**
```bat
build_windows.bat
```

**PowerShell:**
```powershell
.\build_windows.ps1
```

Run `dist\wargalley\wargalley.exe` — no Python, no Docker, no Podman needed.

---

After launching by any mode, open a **second terminal** and start the Pygame client:

```bash
# Linux / macOS
python3 src/client.py

# Windows
python src\client.py
```

The client connects to `http://localhost:5000` by default. To point it at a different host or port, set the `SERVER_URL` environment variable:

```bash
SERVER_URL=http://192.168.1.10:5000 python3 src/client.py
```

To join a named room instead of the `default` room, set the `ROOM` variable:

```bash
ROOM=battle1 python3 src/client.py
```

## ## 4. In-Game Controls

### Action Console (bottom of screen)

| Button | Action | Condition |
| :--- | :--- | :--- |
| **Turn L** | Rotate vessel 60° counter-clockwise | Vessel selected |
| **Move** | Advance one hex forward | Vessel selected |
| **Back** | Retreat one hex backward | Vessel selected; Oars Intact |
| **Turn R** | Rotate vessel 60° clockwise | Vessel selected |
| **Ram** | Ram nearest enemy vessel | Adjacent enemy (≤ 1 hex) |
| **Board** | Initiate boarding action | Vessel selected |
| **Pass** | End turn, no action | Vessel selected |

### Click-to-Move

With a vessel selected, hover over any empty hex — it highlights green. Click it to move the selected vessel directly to that hex.

### Keyboard Controls

| Key | Action |
| :--- | :--- |
| **ESC** | Quit the client |
| **R** | Re-sync game state from server |
| **+ / =** or **Numpad +** | Zoom in |
| **-** or **Numpad -** | Zoom out |
| **Ctrl + Mouse Wheel** | Zoom in / out |
| **Mouse Wheel** | Scroll board vertically |
| **Arrow Keys** | Scroll board in any direction |

## ## 5. Security & Compliance
* **NIST 800-53:** Full audit logging for combat and administrative actions.
* **FIPS 140-3:** Deterministic server-side RNG seeding.
* **CIS Level 2:** Resource-constrained, non-root Podman/Docker containers (Mode 2 only).