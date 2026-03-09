# Project Governance & Access Control (RACI)

This document outlines the roles and responsibilities for the War Galley Digital Engine, ensuring compliance with **CIS Level 2** organizational standards.

## ## 1. RACI Matrix

| Task / Deliverable | Developer | Game Host | Player | System (AI) |
| :--- | :---: | :---: | :---: | :---: |
| **Scenario Logic (YAML)** | **R** | **A** | **I** | - |
| **Asset Generation** | **C** | **A** | - | **R** |
| **Network Security** | **R/A** | **I** | - | **R** |
| **Turn Execution** | **I** | **A** | **R** | **R** |
| **AI Strategy (Lvl 3)** | **R/A** | **I** | **I** | **R** |
| **Audit Log Rotation** | **C** | **A** | - | **R** |

**Legend:**
* **R (Responsible):** Performs the work.
* **A (Accountable):** Final decision-maker and owner.
* **C (Consulted):** Two-way communication for expertise.
* **I (Informed):** Kept up-to-date on progress.

## ## 2. Role-Based Access Control (RBAC)



### **A. Admin (Game Host)**
* Authorized to select scenarios and set global **Talent Budget**.
* Authorized to modify Environment (Wind/Tide) variables.
* Access to server-side logs for AAR reporting.

### **B. Player**
* Permission to join rooms and select factions.
* Restricted to move/attack commands for their own `VesselID` only.
* Access to the **Fleet Builder UI**.

### **C. Spectator**
* Read-only access to the WebSocket `sync_state` stream.
* No command execution authority.