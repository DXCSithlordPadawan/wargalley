# ⚓ War Galley Digital Engine (v1.0.0)

A high-fidelity, hex-axial naval strategy simulation based on the Hellenistic and Punic eras. Built for secure, networked tactical play and advanced AI engagement.



## ## 1. System Overview
* **Engine:** Python-based axial hex logic ($q, r$ coordinate system).
* **Networking:** Flask-SocketIO with Room-based Lobby isolation.
* **Orchestration:** Podman-Compose (Rootless, CIS Level 2 Hardened).
* **Intelligence:** 3-Tiered AI (Heuristic, Tactical, and Minimax Admiral).
* **Visuals:** Procedural 2D Miniature Generation via Pillow (`asset_gen.py`).

## ## 2. Core Mechanics
* **Wind & Tide:** Dynamic MP modifiers based on vessel facing.
* **Ramming:** Calculated via the GMT table ($angle \times strength$).
* **Boarding:** Roman-exclusive **Corvus** trait for locked melee combat.
* **Artillery:** Ranged stone-thrower mechanics for heavy Successor ships.



## ## 3. Quick Start

### Linux / macOS
1.  **Initialize Environment:**
    ```bash
    chmod +x launch_game.bash
    ./launch_game.bash
    ```
2.  **Access Lobby:**
    Connect to `http://localhost:5000` via the Pygame client.

### Windows

War Galley supports two modes on Windows: running from Python or as a fully standalone `.exe` (no Python or container runtime required).

#### Option A — Run with Python (requires Python 3.11+)

**Prerequisites:**
* [Python 3.11+](https://www.python.org/downloads/) (ensure "Add Python to PATH" is checked during installation)
* No container runtime (Podman / Docker) needed.

**Command Prompt:**
```bat
launch_game.bat
```

**PowerShell (recommended):**
```powershell
.\launch_game.ps1
```
> If you receive an execution policy error, run:
> `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

#### Option B — Standalone Executable (no Python or container required)

Build a self-contained `wargalley.exe` using PyInstaller (only needs to be done once on a machine that has Python):

**Command Prompt:**
```bat
build_windows.bat
```

**PowerShell:**
```powershell
.\build_windows.ps1
```

The compiled executable will be placed in `dist\wargalley\wargalley.exe`. Copy the entire `dist\wargalley\` folder to any Windows PC and run `wargalley.exe` — no Python or container runtime required.

2.  **Access Lobby:**
    Connect to `http://localhost:5000` via the Pygame client.

## ## 4. Security & Compliance
* **NIST 800-53:** Full audit logging for combat and administrative actions.
* **FIPS 140-3:** Deterministic server-side RNG seeding.
* **CIS Level 2:** Resource-constrained, non-root Podman containers.