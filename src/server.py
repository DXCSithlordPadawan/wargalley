"""
War Galley Digital Engine — Flask-SocketIO Server
==================================================
Manages game rooms, broadcasts state, and (in vs_computer mode) resolves
AI turns via AdmiralAI after each player action.

Room state schema:
    {
        "vessels": list[dict],   # all vessels for this room
        "turn":    int,          # current turn number
        "mode":    str,          # "vs_computer" | "vs_player"
    }
"""

import copy
import os
import sys
import logging

from flask import Flask, render_template_string, request
from flask_socketio import SocketIO, emit, join_room, leave_room

from ai_minimax import AdmiralAI

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------
os.makedirs("analytics", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(os.path.join("analytics", "server.log")),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# App configuration
# ---------------------------------------------------------------------------
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", os.urandom(32))
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

# In-memory game state: room_id -> state dict
_rooms: dict = {}

# Shared AdmiralAI instance (depth configurable via env var).
_AI_DEPTH: int = int(os.environ.get("AI_DEPTH", "3"))
_admiral: AdmiralAI = AdmiralAI(depth=_AI_DEPTH)
log.info("AdmiralAI initialised at depth=%d", _AI_DEPTH)

# ---------------------------------------------------------------------------
# HTTP routes
# ---------------------------------------------------------------------------

_INDEX_HTML = """
<!DOCTYPE html>
<html>
<head><title>War Galley — Lobby</title></head>
<body>
  <h1>⚓ War Galley Digital Engine</h1>
  <p>Connect via the Pygame client at <strong>ws://localhost:5000</strong>.</p>
  <p>Current rooms: {{ room_count }}</p>
</body>
</html>
"""


@app.route("/")
def index():
    return render_template_string(_INDEX_HTML, room_count=len(_rooms))


@app.route("/health")
def health():
    return {"status": "ok", "rooms": len(_rooms)}, 200


# ---------------------------------------------------------------------------
# SocketIO events
# ---------------------------------------------------------------------------


@socketio.on("connect")
def on_connect() -> None:
    log.info("Client connected: %s", request.sid)


@socketio.on("disconnect")
def on_disconnect() -> None:
    log.info("Client disconnected: %s", request.sid)


@socketio.on("join_room")
def on_join_room(data: dict) -> None:
    """Client joins a room.

    Payload fields:
        room    (str)  : room identifier (default "default").
        mode    (str)  : "vs_computer" | "vs_player" (default "vs_player").
        vessels (list) : optional initial vessel list sent by the client
                         when starting a vs_computer game.
    """
    room = _sanitise_room_name(data.get("room", "default"))
    mode = data.get("mode", "vs_player")
    if mode not in ("vs_computer", "vs_player"):
        log.warning("Unknown mode '%s' from client — defaulting to vs_player", mode)
        mode = "vs_player"

    join_room(room)

    if room not in _rooms:
        # Initialise new room; accept vessel list and environment from client.
        initial_vessels = data.get("vessels", [])
        environment = data.get("environment", {})
        map_size = data.get("map_size", [22, 25])
        _rooms[room] = {
            "vessels": initial_vessels if isinstance(initial_vessels, list) else [],
            "turn": 0,
            "mode": mode,
            "environment": environment if isinstance(environment, dict) else {},
            "map_size": map_size if isinstance(map_size, list) and len(map_size) == 2 else [22, 25],
        }
        log.info(
            "Room '%s' created: mode=%s, %d vessel(s)",
            room,
            mode,
            len(_rooms[room]["vessels"]),
        )
    else:
        # Room already exists — update mode if the caller re-joins with one.
        _rooms[room]["mode"] = mode

    emit("room_state", _rooms[room], room=room)
    log.info("Client joined room '%s' (mode=%s)", room, mode)


@socketio.on("leave_room")
def on_leave_room(data: dict) -> None:
    room = _sanitise_room_name(data.get("room", "default"))
    leave_room(room)
    log.info("Client left room '%s'", room)


@socketio.on("sync_state")
def on_sync_state(data: dict) -> None:
    """Broadcast updated game state to all clients in a room."""
    room = _sanitise_room_name(data.get("room", "default"))
    state = data.get("state", {})
    if not isinstance(state, dict):
        log.warning("sync_state received non-dict state — ignoring")
        return
    _rooms[room] = state
    emit("room_state", state, room=room)
    log.info("State synced for room '%s' (turn %s)", room, state.get("turn"))


@socketio.on("player_action")
def on_player_action(data: dict) -> None:
    """Receive a player command, acknowledge it, then trigger AI if applicable.

    Payload fields:
        room      (str) : room identifier.
        action    (str) : action name (e.g. "ram", "move_forward", "hold").
        vessel_id (str) : ID of the acting vessel.
    """
    room = _sanitise_room_name(data.get("room", "default"))
    action = data.get("action")
    vessel_id = data.get("vessel_id")

    log.info(
        "Action '%s' on vessel '%s' in room '%s'", action, vessel_id, room
    )

    # Acknowledge the player's action immediately.
    emit("action_ack", {"vessel_id": vessel_id, "action": action, "status": "queued"})

    # Apply the player action to room state (advance turn counter).
    room_state = _rooms.get(room)
    if room_state is None:
        log.warning("player_action for unknown room '%s' — ignoring", room)
        return

    room_state["turn"] = room_state.get("turn", 0) + 1

    # Build move dict, forwarding target_pos for move_to actions.
    player_move: dict = {"vessel_id": vessel_id, "action": action}
    if action == "move_to":
        player_move["target_pos"] = data.get("target_pos")

    # Apply the player's own move to room state.
    _apply_move_to_state(room_state, player_move)

    # ── AI turn (vs_computer only) ─────────────────────────────────────
    if room_state.get("mode") == "vs_computer":
        try:
            ai_move = _admiral.get_best_move(copy.deepcopy(room_state))
            log.info("AI move selected for room '%s': %s", room, ai_move)
            _apply_move_to_state(room_state, ai_move)
            room_state["turn"] = room_state.get("turn", 0) + 1
        except Exception as exc:  # noqa: BLE001 — never crash on AI error
            log.error("AdmiralAI error in room '%s': %s", room, exc)

    # Broadcast updated state to all clients in the room.
    emit("room_state", room_state, room=room)


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

_MAX_ROOM_NAME_LENGTH: int = 64


def _sanitise_room_name(name: str) -> str:
    """Return a safe room name, stripping control characters and capping length."""
    sanitised = "".join(ch for ch in str(name) if ch.isprintable())
    return sanitised[:_MAX_ROOM_NAME_LENGTH] or "default"


def _apply_move_to_state(state: dict, move: dict) -> None:
    """Apply a move dict to the room state in-place.

    Supported actions:
        move_to       — teleport vessel to a specific [q, r] hex (blocked if occupied).
        move_forward  — advance vessel one hex in its current facing.
        move_backward — retreat one hex opposite to current facing (costs 2 MP;
                         not permitted if oars are Disabled).
        turn_left     — rotate facing one step counter-clockwise (facing - 1 mod 6).
        turn_right    — rotate facing one step clockwise (facing + 1 mod 6).
        ram           — apply ram damage to the nearest enemy vessel.
        hold / pass   — no-op.

    Mutates the live room state directly so clients receive the result.
    """
    vessel_id = move.get("vessel_id")
    action = move.get("action", "hold")

    acting = next(
        (v for v in state.get("vessels", []) if v.get("id") == vessel_id),
        None,
    )
    if acting is None:
        return

    if action == "move_to":
        target_pos = move.get("target_pos")
        if isinstance(target_pos, list) and len(target_pos) == 2:
            # Ensure no other vessel occupies the target hex.
            occupied = {
                (v["pos"][0], v["pos"][1])
                for v in state.get("vessels", [])
                if isinstance(v.get("pos"), list) and v.get("id") != vessel_id
            }
            tq, tr = int(target_pos[0]), int(target_pos[1])
            if (tq, tr) not in occupied:
                acting["pos"] = [tq, tr]
                log.info("Vessel '%s' moved to [%d, %d]", vessel_id, tq, tr)
            else:
                log.info(
                    "Vessel '%s' move_to [%d, %d] blocked — hex occupied",
                    vessel_id, tq, tr,
                )
        else:
            log.warning("move_to for '%s' missing valid target_pos", vessel_id)

    elif action == "move_forward":
        _move_vessel_forward(acting)

    elif action == "move_backward":
        if acting.get("oars") == "Disabled":
            log.info(
                "Vessel '%s' cannot back — oars disabled", vessel_id
            )
        else:
            _move_vessel_backward(acting)

    elif action == "turn_left":
        acting["facing"] = (acting.get("facing", 0) - 1) % 6
        log.info("Vessel '%s' turned left — new facing %d", vessel_id, acting["facing"])

    elif action == "turn_right":
        acting["facing"] = (acting.get("facing", 0) + 1) % 6
        log.info("Vessel '%s' turned right — new facing %d", vessel_id, acting["facing"])

    elif action == "ram":
        target, dist = _find_nearest_enemy_with_distance(acting, state.get("vessels", []))
        if target is not None and dist <= 1:
            multiplier = acting.get("ram_multiplier", 1.0)
            damage = int(10 * multiplier)
            target["hull"] = max(0, target.get("hull", 0) - damage)
            if damage > 0:
                target["oars"] = "Disabled"
            log.info(
                "Ram: '%s' hit '%s' for %d damage (dist=%.1f)",
                vessel_id,
                target.get("id"),
                damage,
                dist,
            )
        else:
            log.info(
                "Ram: '%s' out of range (nearest enemy dist=%.1f)",
                vessel_id,
                dist if target is not None else -1,
            )


_HEX_DIRECTIONS: tuple[tuple[int, int], ...] = (
    (1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)
)

_SUNK_THRESHOLD: int = 0


def _move_vessel_forward(vessel: dict) -> None:
    """Advance vessel one hex in its current facing direction."""
    facing = vessel.get("facing", 0) % 6
    dq, dr = _HEX_DIRECTIONS[facing]
    pos = vessel.get("pos", [0, 0])
    vessel["pos"] = [pos[0] + dq, pos[1] + dr]


def _move_vessel_backward(vessel: dict) -> None:
    """Retreat vessel one hex opposite to its current facing direction."""
    facing = (vessel.get("facing", 0) + 3) % 6  # opposite facing
    dq, dr = _HEX_DIRECTIONS[facing]
    pos = vessel.get("pos", [0, 0])
    vessel["pos"] = [pos[0] + dq, pos[1] + dr]


def _find_nearest_enemy_with_distance(
    acting: dict, vessels: list[dict]
) -> tuple:
    """Return (nearest living enemy vessel, hex distance) or (None, inf)."""
    side = acting.get("side")
    aq, ar = acting.get("pos", [0, 0])
    nearest = None
    min_dist: float = float("inf")
    for candidate in vessels:
        if candidate.get("side") == side:
            continue
        if candidate.get("hull", 0) <= _SUNK_THRESHOLD:
            continue
        cq, cr = candidate.get("pos", [0, 0])
        dist = (abs(aq - cq) + abs(aq + ar - cq - cr) + abs(ar - cr)) / 2
        if dist < min_dist:
            min_dist = dist
            nearest = candidate
    return nearest, min_dist


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 5000))
    log.info("War Galley server starting on %s:%d", host, port)
    socketio.run(app, host=host, port=port, debug=False)
