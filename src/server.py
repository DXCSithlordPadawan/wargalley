import os
import sys
import logging

from flask import Flask, render_template_string, request
from flask_socketio import SocketIO, emit, join_room, leave_room

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

# In-memory game state (room_id -> state dict)
_rooms: dict = {}

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
</body>
</html>
"""


@app.route("/")
def index():
    return render_template_string(_INDEX_HTML)


@app.route("/health")
def health():
    return {"status": "ok"}, 200


# ---------------------------------------------------------------------------
# SocketIO events
# ---------------------------------------------------------------------------

@socketio.on("connect")
def on_connect():
    log.info("Client connected: %s", request.sid)


@socketio.on("disconnect")
def on_disconnect():
    log.info("Client disconnected")


@socketio.on("join_room")
def on_join_room(data: dict):
    room = data.get("room", "default")
    join_room(room)
    if room not in _rooms:
        _rooms[room] = {"vessels": [], "turn": 0}
    emit("room_state", _rooms[room], room=room)
    log.info("Client joined room '%s'", room)


@socketio.on("leave_room")
def on_leave_room(data: dict):
    room = data.get("room", "default")
    leave_room(room)
    log.info("Client left room '%s'", room)


@socketio.on("sync_state")
def on_sync_state(data: dict):
    """Broadcast updated game state to all clients in a room."""
    room = data.get("room", "default")
    state = data.get("state", {})
    _rooms[room] = state
    emit("room_state", state, room=room)
    log.info("State synced for room '%s' (turn %s)", room, state.get("turn"))


@socketio.on("player_action")
def on_player_action(data: dict):
    """Receive a player command and acknowledge it."""
    room = data.get("room", "default")
    action = data.get("action")
    vessel_id = data.get("vessel_id")
    log.info("Action '%s' on vessel '%s' in room '%s'", action, vessel_id, room)
    emit("action_ack", {"vessel_id": vessel_id, "action": action, "status": "queued"})


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 5000))
    log.info("War Galley server starting on %s:%d", host, port)
    socketio.run(app, host=host, port=port, debug=False)
