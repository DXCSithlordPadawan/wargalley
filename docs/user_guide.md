# 📖 War Galley: User Guide (v1.2)

Welcome to the command deck. This guide will take you from a basic rower to a Fleet Admiral.

---

## ## 1. Interface & Controls

The game is played on an **Axial Hex Grid** displayed in the left/centre portion of the screen. The right panel shows the **Fleet Roster**. The bottom panel is the **Action Console**.

### Screen Layout

| Region | Description |
| :--- | :--- |
| **Top bar** | Room name, current turn, vessel count, game mode |
| **Hex board** | Main play area — click to select vessels or choose move targets |
| **Fleet roster** (right) | All vessels with HP and oar status |
| **Action console** (bottom) | Vessel selector and action buttons |
| **Hint bar** (very bottom) | Keyboard shortcut reminder |

### Selecting a Vessel

You can select one of your vessels in two ways:
- **Click its token** on the hex board.
- **Click its name button** in the vessel selector on the left of the action console.

The selected vessel is highlighted with a gold ring on the board and a highlighted button in the selector.

### Moving a Vessel

With a vessel selected you have two ways to move it:

**Option A — Action buttons (step-by-step):**

| Button | Action | Rules |
| :--- | :--- | :--- |
| **Turn L** | Rotate 60° counter-clockwise | Always available |
| **Move** | Advance one hex forward | Always available |
| **Back** | Retreat one hex backward | Blocked if Oars Disabled |
| **Turn R** | Rotate 60° clockwise | Always available |
| **Ram** | Ram nearest enemy | Enemy must be adjacent (≤ 1 hex) |
| **Board** | Initiate boarding action | Requires `corvus` or `grapple` trait |
| **Pass** | End turn without moving | Always available |

**Option B — Click-to-move (direct hex targeting):**

1. Select a vessel using either method above.
2. Hover over any empty hex on the board — it will highlight green.
3. Click the highlighted hex to move the vessel directly to that position.

The vessel cannot be moved to a hex already occupied by another vessel.

### Facing Arrow

Each vessel token shows a white arrow indicating its current facing direction. Facings are numbered 0–5 clockwise starting from East. Turn L/R buttons rotate one step (60°) per click.

### Oars Disabled

If a vessel's oars are disabled (shown in the Fleet Roster), the **Back** button is blocked. Oars can be disabled by a ram hit from an adjacent enemy.

---

## ## 2. Understanding the "Wind Gauge"
Navigation is not just about rowing; it is about the environment. The Wind and Tide directly impact your MP efficiency.

* **With the Wind:** If moving in the direction of the wind vector, movement is **0.5 MP** per hex.
* **Against the Wind:** If facing into the wind, movement is **2.0 MP** per hex.
* **Tide:** At the end of every turn, all vessels are "drifted" one hex in the direction of the tide unless anchored or grappled.

---

## ## 3. Combat Mechanics
Success in the ancient world is determined by the **Angle of Impact**.



| Action | Ideal Condition | Result |
| :--- | :--- | :--- |
| **Prow Ram** | Head-on ($0^{\circ}$) | High hull damage to both; potential for "Stuck" state. |
| **Flank Ram** | Side-on ($60^{\circ}-120^{\circ}$) | Massive hull damage to defender; safe for attacker. |
| **Oar Rake** | Passing Stern-to-Stem | Disables enemy oars; reduces enemy MP to 0 for 2 turns. |
| **Boarding** | Grappled (Corvus) | Uses **Marine** count to seize the ship instead of sinking it. |

---

## ## 4. The Fleet Builder (Point-Buy)
Before the battle, you must spend your **Talents** (Budget) to assemble your task force.



1.  **Select Nation:** Choose from Rome, Carthage, or the Successors.
2.  **Analyze Unit Cards:** Hover over ships to see traits like `corvus` or `artillery`.
3.  **Balance your Fleet:** Don't spend all your talents on one **Deceres**; a swarm of **Triremes** can rake its oars and leave it helpless.

---

## ## 5. AI Difficulty Tiers
The engine uses three levels of logic to challenge you:
* **Level 1 (Seeker):** Aggressive and predictable; always moves toward the nearest target.
* **Level 2 (Tactical):** Understands flanking; will try to avoid head-on collisions.
* **Level 3 (Admiral):** Uses **Minimax** search. It will bait you into bottlenecks and use the wind to stay out of your reach.

---

## ## 6. Deployment Setup

War Galley supports three deployment modes. Choose the one that best fits your environment.

---

### Mode 1 — Native Python (Windows, Linux, macOS)

Run the server directly with Python — no container runtime needed.

#### Prerequisites
* [Python 3.11+](https://www.python.org/downloads/) — check **"Add Python to PATH"** during install.

#### Launching

**Windows — Command Prompt:**
```bat
launch_game.bat
```

**Windows — PowerShell (recommended):**
```powershell
.\launch_game.ps1
```
If you see a script execution policy error, run this once:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Linux / macOS:**
```bash
chmod +x launch_game.bash
./launch_game.bash
```

---

### Mode 2 — Container (Podman or Docker)

Runs the server inside a hardened, rootless container (CIS Level 2). Suitable for server deployments or when a consistent, isolated environment is required.

#### Prerequisites
* [Podman Desktop](https://podman-desktop.io/) **or** [Docker Desktop](https://www.docker.com/products/docker-desktop/) — installed and running.

#### Launching

**Windows — Command Prompt:**
```bat
deploy_container.bat
```

**Windows — PowerShell:**
```powershell
.\deploy_container.ps1
```

**Linux / macOS:**
```bash
./launch_game.bash --container
```

---

### Mode 3 — Standalone Windows Executable (no Python or container required)

Build a self-contained `wargalley.exe` on any Windows machine that has Python installed. The resulting executable can be distributed and run on Windows PCs with **no Python, no container runtime, and no virtual environment** needed.

**Command Prompt:**
```bat
build_windows.bat
```

**PowerShell:**
```powershell
.\build_windows.ps1
```

The compiled executable is placed in `dist\wargalley\wargalley.exe`. Copy the entire `dist\wargalley\` folder to the target machine and run `wargalley.exe`.

---

## ## 7. Connecting as a Client

Once the server is running (using any of the deployment modes above), open a **second terminal** and launch the Pygame client:

**Linux / macOS:**
```bash
python3 src/client.py
```

**Windows — Command Prompt:**
```bat
python src\client.py
```

**Windows — PowerShell:**
```powershell
python src\client.py
```

The client will open a Pygame window, connect to the server, and join the `default` room automatically.

### Connecting to a Different Host or Port

If the server is running on a different machine or port, set the `SERVER_URL` environment variable before starting the client:

**Linux / macOS:**
```bash
SERVER_URL=http://192.168.1.10:5000 python3 src/client.py
```

**Windows — PowerShell:**
```powershell
$env:SERVER_URL = "http://192.168.1.10:5000"
python src\client.py
```

### Joining a Named Room

Multiple games can run on the same server using different room names. Set the `ROOM` variable to join a specific room (default: `default`):

```bash
ROOM=battle1 python3 src/client.py
```

### Client Keyboard Controls

| Key | Action |
| :--- | :--- |
| **ESC** | Quit the client |
| **R** | Re-sync game state from the server |
| **+ / =** or **Numpad +** | Zoom in |
| **-** or **Numpad -** | Zoom out |
| **Ctrl + Mouse Wheel** | Zoom in / out |
| **Mouse Wheel** | Scroll the board vertically |
| **Arrow Keys** | Scroll the board in any direction |
| **Click vessel token** | Select vessel |
| **Click empty hex** (vessel selected) | Move selected vessel to that hex |

### Scrollbar

Horizontal and vertical scrollbars appear at the edges of the hex board area. You can drag the thumb with the mouse to pan the board.

---

## ## 8. Troubleshooting & Support
If the game fails to launch:
1.  Verify you ran the asset generation script to generate the ship graphics: `python src/asset_gen.py` on Windows, or `python3 src/asset_gen.py` on Linux/macOS.
2.  Check the `analytics/` folder for server logs if the server crashes.
3.  **Mode 1 / Windows:** Confirm `python` is on your `PATH` by running `python --version` in a terminal.
4.  **Mode 2 / Container:** Ensure Podman or Docker is running before executing the deploy script.
5.  **Mode 3 / Standalone:** Ensure the full `dist\wargalley\` folder is present next to `wargalley.exe`; do not move the executable out of that folder.
6.  **Client cannot connect:** Verify the server is running (`curl http://localhost:5000/health` should return `{"status":"ok"}`). Check that no firewall is blocking port 5000. If the server is on another machine, ensure `SERVER_URL` is set correctly.