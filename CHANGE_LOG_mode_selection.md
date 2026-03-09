# War Galley — Change Log

---

## v1.2.0 — 2026-03-09: Movement, Turning, Hex Click-to-Move & Bug Fixes

### New Features

| Feature | Files Changed |
| :--- | :--- |
| **Turn Left / Turn Right** buttons in action console | `ui/components.py`, `server.py` |
| **Move Backward (Back)** button | `ui/components.py`, `server.py` |
| **Click-to-move**: select vessel then click any empty hex to move directly to it | `ui/components.py`, `client.py`, `server.py` |
| Empty hex **hover highlight** (green) when a vessel is selected | `ui/components.py` |
| Zoom in/out via keyboard (`+`/`-`) and `Ctrl+Mouse Wheel` | `client.py` |
| Board scroll via Arrow Keys, Mouse Wheel, and draggable scrollbars | `client.py` |

### Bug Fixes

| Bug | Root Cause | Fix | File |
| :--- | :--- | :--- | :--- |
| Ships could not turn | No turn actions existed anywhere | Added `turn_left`/`turn_right` to action panel and server handler | `components.py`, `server.py` |
| Oars disabled immediately, enemy ships far away | `_apply_ram()` and server ram branch applied oar damage with no proximity check; AI always chose ram | Added `dist <= 1` gate in both server and AI simulation; AI `get_possible_moves()` only offers ram when adjacent | `server.py`, `ai_minimax.py` |
| `move_to` action had no effect | `on_player_action` built move dict without forwarding `target_pos` from the SocketIO payload | Forward `target_pos` into `player_move` dict when `action == "move_to"` | `server.py` |
| `_move_vessel_backward()` caused `NameError` | Function was called but never defined | Added `_move_vessel_backward()` helper | `server.py` |

### Action Panel — Final Button Order

`Turn L` · `Move` · `Back` · `Turn R` · `Ram` · `Board` · `Pass`

### Server — Supported Actions (complete list)

| Action | Effect |
| :--- | :--- |
| `move_to` | Teleport vessel to target `[q, r]` hex (blocked if occupied) |
| `move_forward` | Advance one hex in current facing direction |
| `move_backward` | Retreat one hex opposite to facing (blocked if Oars Disabled) |
| `turn_left` | Rotate facing one step counter-clockwise (`facing - 1 mod 6`) |
| `turn_right` | Rotate facing one step clockwise (`facing + 1 mod 6`) |
| `ram` | Deal damage to nearest adjacent enemy (distance ≤ 1 hex) |
| `hold` / `pass` | No-op |

---

## v1.0.0 — Game Mode Selection

**Date:** 2026-03-09  
**Status:** Complete — awaiting manual copy to `C:\wargalley\src\`

---

## Files Changed

| Destination | Source Output | Change Summary |
|---|---|---|
| `src/ai_minimax.py` | `outputs/ai_minimax.py` | Completed all stubs; added `get_best_move()` |
| `src/ui/components.py` | `outputs/components.py` | Added `draw_menu()` |
| `src/client.py` | `outputs/client.py` | Added menu phase + mode-aware `join_room` + default fleets |
| `src/server.py` | `outputs/server.py` | Stores mode/vessels; triggers AI after player action |

---

## Gaps Filled

1. **`is_terminal()`** — implemented: returns True when either side has no vessels with hull > 0.
2. **`get_possible_moves()`** — implemented: returns move dicts for all living vessels; respects disabled oars.
3. **`simulate()`** — implemented: deep copy + forward/ram/hold logic with axial hex maths.
4. **Minimax minimize branch** — fixed: was returning `float('inf')` with no iteration; now fully evaluates player moves.
5. **`get_best_move()`** — new public method; the only entry point `server.py` calls.
6. **Vessel initialisation** — default 2v2 fleets (Roman vs Carthage) seeded by client on `vs_computer` launch.
7. **AI depth configurable** — server reads `AI_DEPTH` env var (default 3); supports Easy=1, Normal=3, Hard=5.
8. **Input sanitisation** — `_sanitise_room_name()` on server strips non-printable chars, caps at 64 chars.

---

## How to Deploy

Copy the four output files to their correct locations in `C:\wargalley\src\`:

```
outputs\ai_minimax.py   →  C:\wargalley\src\ai_minimax.py
outputs\components.py   →  C:\wargalley\src\ui\components.py
outputs\client.py       →  C:\wargalley\src\client.py
outputs\server.py       →  C:\wargalley\src\server.py
```

Then launch as normal:

```powershell
# Terminal 1 — Server
python src\server.py

# Terminal 2 — Client
python src\client.py
```

The menu appears on client launch. Select **Single Player (vs Computer)** or **Two Player (vs Player)**.

---

## Env Vars

| Variable | Default | Effect |
|---|---|---|
| `AI_DEPTH` | `3` | Minimax search depth (1=Easy, 3=Normal, 5=Hard) |
| `SERVER_URL` | `http://localhost:5000` | Server address for the client |
| `ROOM` | `default` | Room name to join |
| `SECRET_KEY` | random | Flask session key |
