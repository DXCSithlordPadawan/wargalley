# 📖 War Galley: User Guide (v1.0)

Welcome to the command deck. This guide will take you from a basic rower to a Fleet Admiral.

---

## ## 1. Interface & Controls
The game is played on an **Axial Hex Grid**. Your primary interactions occur through the **Command Console** and the **Mouse**.



* **Selection:** Click a vessel to view its **Unit Card** and available **Movement Points (MP)**.
* **Movement:** * **Forward:** Move one hex in the direction of the prow.
    * **Rotate:** Turn 60° clockwise or counter-clockwise (Costs 1 MP).
    * **Backing:** Move one hex backward (Costs 2 MP).
* **Combat:** Right-click an adjacent enemy to initiate a **Ram** or **Boarding Action**.

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

## ## 6. Windows Setup

### Prerequisites
* [Python 3.11+](https://www.python.org/downloads/) — check **"Add Python to PATH"** during install.
* [Podman Desktop](https://podman-desktop.io/) **or** [Docker Desktop](https://www.docker.com/products/docker-desktop/) for container orchestration.
* Install Python dependencies from a terminal: `pip install -r requirements.txt`

### Launching the Game on Windows

**Command Prompt:**
```bat
launch_game.bat
```

**PowerShell (recommended):**
```powershell
.\launch_game.ps1
```
If you see a script execution policy error, run this once:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## ## 7. Troubleshooting & Support
If the game fails to launch:
1.  Ensure **Podman** or **Docker** is running.
2.  Verify you ran the asset generation script to generate the ship graphics: `python src/asset_gen.py` on Windows, or `python3 src/asset_gen.py` on Linux/macOS.
3.  Check the `analytics/` folder for logs if the server crashes.
4.  **Windows only:** Confirm `python` is on your `PATH` by running `python --version` in a terminal.