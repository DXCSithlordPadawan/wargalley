# 📜 War Galley: Official Rules of Engagement

This document defines the mathematical and logical constraints of the simulation engine.

---

## ## 1. Movement & Facing
The game uses an **Axial Hex Coordinate System**. Every vessel has a **Facing** (0-5) corresponding to the hex edges.



### **Movement Point (MP) Costs**
* **Forward (1 Hex):** 1 MP (Modified by Wind).
* **Rotate (60°):** 1 MP.
* **Backing (1 Hex):** 2 MP (Cannot be done if Oars are disabled).
* **Oar Rake:** 2 MP + movement into an adjacent hex alongside an enemy.

### **Environmental Modifiers**
* **Headwind:** Facing within 60° of the wind source increases all Forward MP costs by +1.
* **Tailwind:** Facing directly away from the wind source reduces Forward MP costs to 0.5.
* **Tide Drift:** At the end of the turn, all non-grappled ships move 1 hex in the `tide_dir`. If this causes a collision with terrain, the ship takes 50 Hull Damage.

---

## ## 2. Combat Resolution

### **Ramming Physics**
Damage is calculated using the formula:  
$$Damage = (Vessel_{Mass} \times Velocity_{Modifier}) \times Angle_{Multiplier}$$

| Angle | Description | Multiplier |
| :--- | :--- | :--- |
| **0° (Head-On)** | Prow to Prow | 1.0x to both |
| **60° (Oblique)** | Prow to Bow-Quarter | 1.2x to Defender |
| **90°+ (Flank)** | Prow to Beam/Hull | 2.0x to Defender |

### **Boarding & Grappling**
1.  **Initiation:** Only vessels with the `corvus` or `grapple` trait can initiate a lock.
2.  **Calculation:** The winner is determined by `(Marine_Count + Leader_Bonus) * d10`.
3.  **Result:** If the attacker wins by >50%, the ship is **Captured**. If not, the ships remain **Grappled** and cannot move until the next turn's melee.

---

## ## 3. Vessel Traits & Special Abilities
* **Corvus (Rome):** Automatically attempts a grapple on any collision. Attacker gets +2 to Boarding.
* **Reinforced Oars (Carthage):** 50% chance to ignore "Oars Disabled" results from enemy rakes.
* **Artillery (Successors):** Can attack targets up to 3 hexes away. Success is based on `1/Distance`.
* **Fire Baskets (Rhodes):** If rammed, the attacker has a 20% chance of catching fire.

---

## ## 4. Damage & Sinking
* **Hull < 50%:** MP reduced by 1.
* **Hull < 25%:** Vessel is "Waterlogged"; cannot rotate, only drift.
* **Hull = 0:** Vessel is removed from the board (Sunk).

---

## ## 5. Win Conditions
* **Annihilation:** Sink or capture all enemy vessels.
* **Flagship Kill:** Sinking the vessel with the `admiral` trait triggers an immediate morale check; remaining enemy ships may flee.
* **Objective:** In specific scenarios (e.g., Salamis), moving a Flagship to a designated "Exit Hex" results in victory.