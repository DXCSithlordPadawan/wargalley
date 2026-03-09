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
**Prerequisites:**
* [Python 3.11+](https://www.python.org/downloads/) (ensure "Add Python to PATH" is checked during installation)
* [Podman Desktop](https://podman-desktop.io/) **or** [Docker Desktop](https://www.docker.com/products/docker-desktop/)
* Install Python dependencies: `pip install -r requirements.txt`

**Command Prompt:**
1.  **Initialize Environment:**
    ```bat
    launch_game.bat
    ```

**PowerShell (recommended):**
1.  **Initialize Environment:**
    ```powershell
    .\launch_game.ps1
    ```
    > If you receive an execution policy error, run:
    > `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

2.  **Access Lobby:**
    Connect to `http://localhost:5000` via the Pygame client.

## ## 4. Security & Compliance
* **NIST 800-53:** Full audit logging for combat and administrative actions.
* **FIPS 140-3:** Deterministic server-side RNG seeding.
* **CIS Level 2:** Resource-constrained, non-root Podman containers.