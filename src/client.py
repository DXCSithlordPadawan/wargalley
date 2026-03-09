"""
War Galley Digital Engine — Pygame Client
==========================================
Connects to the Flask-SocketIO server and presents the interactive game UI.

Usage:
    python3 src/client.py                      # connect to http://localhost:5000
    SERVER_URL=http://192.168.1.10:5000 python3 src/client.py
    ROOM=battle1 python3 src/client.py

Game modes (selected at launch via the menu screen):
    vs_computer  — single-player; the server drives the AI opponent.
    vs_player    — two-player networked game via a shared room.
"""

import os
import sys
import logging
from pathlib import Path
from typing import Optional

import socketio
import pygame
import yaml

from ui.components import FleetUI

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
SERVER_URL: str = os.environ.get("SERVER_URL", "http://localhost:5000")
ROOM: str = os.environ.get("ROOM", "default")

# Initial window size — user may resize freely after launch.
_INIT_W: int = 1024
_INIT_H: int = 680
FPS: int = 30

# Right-panel width (fleet roster + unit card).  Derived at runtime from
# window width as:  roster_x = window_w - ROSTER_PANEL_W
ROSTER_PANEL_W: int = 294

# Colour palette
NAVY_BLUE = (10, 20, 60)
SAND = (240, 230, 200)
WHITE = (255, 255, 255)
CRIMSON = (180, 30, 30)
LIGHT_GREY = (180, 180, 180)
GOLD = (212, 175, 55)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Default starter fleet used when launching a vs_computer single-player game.
# The server will own this state; the client sends it once on join.
# Vessel schema mirrors the scenario YAML format.
# ---------------------------------------------------------------------------
_DEFAULT_PLAYER_FLEET: list[dict] = [
    {
        "id": "pl_01",
        "name": "Roman Flagship",
        "side": "player",
        "type": "Quinquereme",
        "hull": 60,
        "marines": 60,
        "ram_multiplier": 1.0,
        "facing": 3,
        "pos": [10, 10],
        "traits": ["corvus"],
        "oars": "Intact",
    },
    {
        "id": "pl_02",
        "name": "Roman Escort",
        "side": "player",
        "type": "Trireme",
        "hull": 40,
        "marines": 30,
        "ram_multiplier": 0.9,
        "facing": 3,
        "pos": [8, 10],
        "traits": ["agile"],
        "oars": "Intact",
    },
]

_DEFAULT_AI_FLEET: list[dict] = [
    {
        "id": "ai_01",
        "name": "Carthage Flagship",
        "side": "AI",
        "type": "Quinquereme",
        "hull": 60,
        "marines": 50,
        "ram_multiplier": 1.2,
        "facing": 0,
        "pos": [10, 20],
        "traits": ["ram_master", "reinforced_oars"],
        "oars": "Intact",
    },
    {
        "id": "ai_02",
        "name": "Carthage Raider",
        "side": "AI",
        "type": "Trireme",
        "hull": 40,
        "marines": 25,
        "ram_multiplier": 1.1,
        "facing": 0,
        "pos": [12, 20],
        "traits": ["reinforced_oars"],
        "oars": "Intact",
    },
]

# ---------------------------------------------------------------------------
# Shared state (updated by SocketIO callbacks)
# ---------------------------------------------------------------------------
game_state: dict = {"vessels": [], "turn": 0, "mode": "vs_player"}
_ack_message: str = ""

# Currently selected vessel ID for the action panel (updated in game loop)
_selected_vessel_id: Optional[str] = None

# Viewport state: zoom level and scroll offset for the hex board.
# hex_size = base size * zoom; scroll is pixel offset of board origin.
_zoom: float = 1.0
_ZOOM_MIN: float = 0.4
_ZOOM_MAX: float = 3.0
_ZOOM_STEP: float = 0.15
_BASE_HEX_SIZE: int = 28   # matches _HEX_SIZE in components.py
_scroll_x: int = 0
_scroll_y: int = 0
_SCROLL_STEP: int = 20

# Scrollbar drag state.
_drag_hbar: bool = False   # dragging the horizontal scrollbar
_drag_vbar: bool = False   # dragging the vertical scrollbar
_drag_start_mouse: int = 0 # mouse coord at drag start
_drag_start_scroll: int = 0  # scroll value at drag start

# ---------------------------------------------------------------------------
# SocketIO client
# ---------------------------------------------------------------------------
sio = socketio.Client(logger=False, engineio_logger=False)


@sio.event
def connect() -> None:
    log.info("Connected to War Galley server at %s", SERVER_URL)
    # join_room is called explicitly after mode selection — not here —
    # because we need the mode value captured from the menu.


@sio.event
def disconnect() -> None:
    log.info("Disconnected from server.")


@sio.on("room_state")
def on_room_state(data: dict) -> None:
    global game_state
    game_state = data
    log.info(
        "Room state received: turn %s, %d vessel(s), mode=%s",
        data.get("turn"),
        len(data.get("vessels", [])),
        data.get("mode"),
    )


@sio.on("action_ack")
def on_action_ack(data: dict) -> None:
    global _ack_message
    _ack_message = (
        f"Action '{data.get('action')}' on vessel "
        f"'{data.get('vessel_id')}' → {data.get('status')}"
    )
    log.info("Action acknowledged: %s", data)


# ---------------------------------------------------------------------------
# Pygame rendering helpers
# ---------------------------------------------------------------------------


def _draw_status_bar(screen: pygame.Surface, font: pygame.font.Font) -> None:
    """Render room name, current turn, vessel count, and game mode."""
    vessels = game_state.get("vessels", [])
    mode_label = (
        "vs Computer"
        if game_state.get("mode") == "vs_computer"
        else "vs Player"
    )
    text = font.render(
        f"Room: {ROOM}  |  Turn: {game_state.get('turn', 0)}"
        f"  |  Vessels: {len(vessels)}  |  {mode_label}",
        True,
        WHITE,
    )
    screen.blit(text, (20, 16))


def _draw_vessel_list(
    screen: pygame.Surface,
    font: pygame.font.Font,
    roster_x: int,
    w: int,
    h: int,
) -> None:
    """Render a compact fleet roster in the right-hand panel.

    Args:
        screen:   Active display surface.
        font:     Base font for the roster title.
        roster_x: X pixel position where the roster panel starts.
        w, h:     Current window dimensions.
    """
    vessels = game_state.get("vessels", [])
    small_font = pygame.font.SysFont("Georgia", 15)

    # Panel background strip.
    panel_w = w - roster_x + 6
    panel_h = h - 80
    panel_surf = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
    panel_surf.fill((10, 20, 60, 180))
    screen.blit(panel_surf, (roster_x - 6, 44))

    if not vessels:
        msg = small_font.render("Waiting for vessels…", True, SAND)
        screen.blit(msg, (roster_x, 52))
        return

    label = font.render("Fleet Roster", True, GOLD)
    screen.blit(label, (roster_x, 48))

    y = 76
    for vessel in vessels:
        side = vessel.get("side", "?")
        colour = (100, 220, 120) if side == "player" else (220, 100, 100)
        name_surf = small_font.render(
            f"● {vessel.get('name', '?')}", True, colour
        )
        screen.blit(name_surf, (roster_x, y))
        y += 18
        detail = small_font.render(
            f"   HP {vessel.get('hull', '?')}  "
            f"Oars: {vessel.get('oars', '?')}",
            True,
            LIGHT_GREY,
        )
        screen.blit(detail, (roster_x, y))
        y += 22
        if y > h - 160:
            break


def _draw_ack_banner(
    screen: pygame.Surface, small_font: pygame.font.Font
) -> None:
    """Show the most recent action acknowledgement."""
    if _ack_message:
        _h = screen.get_height()
        surf = small_font.render(_ack_message, True, CRIMSON)
        screen.blit(surf, (20, _h - 52))


def _draw_controls(
    screen: pygame.Surface, small_font: pygame.font.Font
) -> None:
    """Print a one-line control reference at the bottom of the screen."""
    _h = screen.get_height()
    hint = small_font.render(
        "ESC/Exit — quit   |   R — refresh   |   +/- or Ctrl+Wheel — zoom   |   Arrows/Wheel — scroll",
        True,
        LIGHT_GREY,
    )
    screen.blit(hint, (20, _h - 28))


# ---------------------------------------------------------------------------
# Scrollbar helpers
# ---------------------------------------------------------------------------

# Scrollbar geometry constants.
_SB_THICK: int = 12        # scrollbar track thickness in pixels
_SB_MIN_THUMB: int = 20    # minimum thumb length in pixels


def _board_pixel_size(
    zoom: float,
    board_cols: int = 22,
    board_rows: int = 25,
) -> tuple[int, int]:
    """Return the total pixel width and height of the hex board at the given zoom."""
    size = max(6, int(_BASE_HEX_SIZE * zoom))
    pw = int(size * 1.5 * board_cols)
    ph = int(size * 1.732 * board_rows)  # sqrt(3) ≈ 1.732
    return pw, ph


def _clamp_scroll(
    sx: int,
    sy: int,
    zoom: float,
    roster_x: int,
    h: int,
    board_cols: int = 22,
    board_rows: int = 25,
) -> tuple[int, int]:
    """Clamp scroll offsets so the board cannot be scrolled completely off screen."""
    board_w, board_h = _board_pixel_size(zoom, board_cols, board_rows)
    view_w = roster_x - 10
    view_h = h - 44 - _SB_THICK - 150  # status bar + action panel
    max_sx = max(0, board_w - view_w)
    max_sy = max(0, board_h - view_h)
    return max(0, min(sx, max_sx)), max(0, min(sy, max_sy))


def _draw_scrollbars(
    screen: pygame.Surface,
    zoom: float,
    scroll_x: int,
    scroll_y: int,
    roster_x: int,
    h: int,
    board_cols: int = 22,
    board_rows: int = 25,
) -> tuple[pygame.Rect, pygame.Rect]:
    """Draw horizontal and vertical scrollbars for the hex board area.

    Returns (h_thumb_rect, v_thumb_rect) for drag hit-testing by the caller.
    """
    board_w, board_h = _board_pixel_size(zoom, board_cols, board_rows)
    view_x0 = 10
    view_y0 = 44
    view_w = roster_x - view_x0 - _SB_THICK
    view_h = h - view_y0 - _SB_THICK - 150

    track_col = (30, 40, 70)
    thumb_col = (90, 120, 180)

    # ── Horizontal scrollbar ──────────────────────────────────────
    h_track = pygame.Rect(view_x0, view_y0 + view_h, view_w, _SB_THICK)
    pygame.draw.rect(screen, track_col, h_track)

    if board_w > view_w:
        h_ratio = view_w / board_w
        h_thumb_w = max(_SB_MIN_THUMB, int(view_w * h_ratio))
        h_thumb_x = view_x0 + int((view_w - h_thumb_w) * scroll_x / max(1, board_w - view_w))
        h_thumb = pygame.Rect(h_thumb_x, view_y0 + view_h, h_thumb_w, _SB_THICK)
    else:
        h_thumb = pygame.Rect(view_x0, view_y0 + view_h, view_w, _SB_THICK)
    pygame.draw.rect(screen, thumb_col, h_thumb, border_radius=3)

    # ── Vertical scrollbar ───────────────────────────────────────
    v_track = pygame.Rect(view_x0 + view_w, view_y0, _SB_THICK, view_h)
    pygame.draw.rect(screen, track_col, v_track)

    if board_h > view_h:
        v_ratio = view_h / board_h
        v_thumb_h = max(_SB_MIN_THUMB, int(view_h * v_ratio))
        v_thumb_y = view_y0 + int((view_h - v_thumb_h) * scroll_y / max(1, board_h - view_h))
        v_thumb = pygame.Rect(view_x0 + view_w, v_thumb_y, _SB_THICK, v_thumb_h)
    else:
        v_thumb = pygame.Rect(view_x0 + view_w, view_y0, _SB_THICK, view_h)
    pygame.draw.rect(screen, thumb_col, v_thumb, border_radius=3)

    return h_thumb, v_thumb


# ---------------------------------------------------------------------------
# Scenario loading helpers
# ---------------------------------------------------------------------------

# Resolve the scenarios directory relative to this file so the client works
# regardless of the current working directory.
_SCENARIOS_DIR: Path = Path(__file__).parent.parent / "scenarios"

# Vessel stat defaults applied when the YAML omits a field.
_VESSEL_DEFAULTS: dict = {
    "hull": 40,
    "marines": 30,
    "ram_multiplier": 1.0,
    "oars": "Intact",
    "traits": [],
}


def _load_scenarios() -> list[dict]:
    """Scan the scenarios directory and return a list of parsed scenario dicts.

    Each entry has keys:
        'name' (str)  — human-readable scenario name from the YAML.
        'path' (str)  — relative file path (for display in the UI).
        'data' (dict) — full parsed YAML content.

    Files that cannot be parsed are skipped with a warning log.
    Returns an empty list if the directory does not exist.
    """
    if not _SCENARIOS_DIR.is_dir():
        log.warning("Scenarios directory not found: %s", _SCENARIOS_DIR)
        return []

    scenarios: list[dict] = []
    for fpath in sorted(_SCENARIOS_DIR.glob("*.y*ml")):
        try:
            with fpath.open(encoding="utf-8") as fh:
                raw = yaml.safe_load(fh)
            if not isinstance(raw, dict) or "scenario" not in raw:
                log.warning("Skipping %s: missing 'scenario' key", fpath.name)
                continue
            name = raw["scenario"].get("name", fpath.stem)
            scenarios.append({
                "name": name,
                "path": str(fpath.relative_to(_SCENARIOS_DIR.parent)),
                "data": raw,
            })
            log.info("Loaded scenario '%s' from %s", name, fpath.name)
        except (yaml.YAMLError, OSError) as exc:
            log.warning("Could not load scenario %s: %s", fpath.name, exc)

    return scenarios


def _normalise_scenario_vessels(scenario_data: dict) -> list[dict]:
    """Convert a parsed scenario YAML into a flat vessel list for the server.

    The first faction in the YAML becomes side='player'; subsequent factions
    become side='AI'.  Missing vessel fields are filled with ``_VESSEL_DEFAULTS``.

    Args:
        scenario_data: Full parsed YAML dict (must have 'scenario.factions').

    Returns:
        List of vessel dicts in the server schema, or an empty list on error.
    """
    try:
        factions: list[dict] = scenario_data["scenario"]["factions"]
    except (KeyError, TypeError):
        log.warning("Scenario has no factions; falling back to default fleet.")
        return []

    vessels: list[dict] = []
    for faction_idx, faction in enumerate(factions):
        side = "player" if faction_idx == 0 else "AI"
        faction_id = faction.get("id", f"faction_{faction_idx}")
        for vessel_raw in faction.get("vessels", []):
            vessel: dict = dict(_VESSEL_DEFAULTS)   # start with defaults
            vessel.update({
                "id":             vessel_raw.get("id", f"{faction_id}_{len(vessels)}"),
                "name":           vessel_raw.get("name",
                                                  vessel_raw.get("id", "Unknown")),
                "side":           side,
                "type":           vessel_raw.get("type", "Trireme"),
                "hull":           vessel_raw.get("hull", _VESSEL_DEFAULTS["hull"]),
                "marines":        vessel_raw.get("marines", _VESSEL_DEFAULTS["marines"]),
                "ram_multiplier": vessel_raw.get("ram_multiplier",
                                                  _VESSEL_DEFAULTS["ram_multiplier"]),
                "facing":         vessel_raw.get("facing", 0),
                "pos":            list(vessel_raw.get("pos", [5, 5])),
                "traits":         list(vessel_raw.get("traits", [])),
                "oars":           vessel_raw.get("oars", _VESSEL_DEFAULTS["oars"]),
            })
            vessels.append(vessel)

    log.info(
        "Normalised %d vessels from scenario '%s'",
        len(vessels),
        scenario_data["scenario"].get("name", "?"),
    )
    return vessels


# ---------------------------------------------------------------------------
# Menu phase
# ---------------------------------------------------------------------------


def _run_menu(
    screen: pygame.Surface,
    clock: pygame.time.Clock,
    fleet_ui: FleetUI,
) -> Optional[str]:
    """Run the mode selection screen until the player picks a mode or quits.

    Returns:
        "vs_computer" | "vs_player", or None if the player quit.
    """
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return None

        mode = fleet_ui.draw_menu(screen, clock)
        pygame.display.flip()
        clock.tick(FPS)

        if mode is not None:
            log.info("Game mode selected: %s", mode)
            return mode


# ---------------------------------------------------------------------------
# Main game loop
# ---------------------------------------------------------------------------


def run() -> None:
    """Initialise Pygame, show the mode menu, connect, and run the game loop."""
    pygame.init()
    screen = pygame.display.set_mode(
        (_INIT_W, _INIT_H), pygame.RESIZABLE
    )
    pygame.display.set_caption("⚓ War Galley Digital Engine")
    clock = pygame.time.Clock()

    font = pygame.font.SysFont("Georgia", 20)
    small_font = pygame.font.SysFont("Georgia", 16)
    fleet_ui = FleetUI()

    # ── Phase 1: Mode selection menu ──────────────────────────────────
    selected_mode = _run_menu(screen, clock, fleet_ui)
    if selected_mode is None:
        # Player closed the window or pressed ESC on the menu.
        pygame.quit()
        sys.exit(0)

    # ── Phase 2: Scenario selection ───────────────────────────────────
    available_scenarios = _load_scenarios()
    selected_scenario: Optional[dict] = None

    if available_scenarios:
        while selected_scenario is None:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit(0)
            selected_scenario = fleet_ui.draw_scenario_menu(
                screen, available_scenarios
            )
            pygame.display.flip()
            clock.tick(FPS)
        log.info("Scenario selected: %s", selected_scenario["name"])
    else:
        selected_scenario = {"name": "Default", "path": "", "data": None}
        log.info("No scenarios found; using default fleet.")

    # ── Phase 3: Connect to server ────────────────────────────────────
    try:
        log.info("Connecting to %s ...", SERVER_URL)
        sio.connect(SERVER_URL, transports=["websocket", "polling"])
    except ConnectionRefusedError:
        log.error(
            "Connection refused - is the server running at %s? "
            "Start it with: python3 src/server.py",
            SERVER_URL,
        )
        pygame.quit()
        sys.exit(1)
    except TimeoutError:
        log.error(
            "Connection timed out while reaching %s - check SERVER_URL and network.",
            SERVER_URL,
        )
        pygame.quit()
        sys.exit(1)
    except Exception as exc:  # noqa: BLE001
        log.error(
            "Could not connect to server at %s - %s. "
            "Verify the server is running and SERVER_URL is correct.",
            SERVER_URL,
            exc,
        )
        pygame.quit()
        sys.exit(1)

    # Build vessel list, environment and map_size from the chosen scenario,
    # or fall back to safe defaults.
    scenario_data = selected_scenario.get("data")
    if scenario_data is not None:
        scenario_block = scenario_data.get("scenario", {})
        initial_vessels: list[dict] = _normalise_scenario_vessels(scenario_data)
        environment: dict = scenario_block.get("environment", {})
        map_size: list[int] = list(scenario_block.get("map_size", [22, 25]))
        # Ensure board is at least as wide/tall as the defined ship positions.
        if initial_vessels:
            max_q = max(v["pos"][0] for v in initial_vessels) + 5
            max_r = max(v["pos"][1] for v in initial_vessels) + 5
            map_size[0] = max(map_size[0], max_q)
            map_size[1] = max(map_size[1], max_r)
    elif selected_mode == "vs_computer":
        initial_vessels = _DEFAULT_PLAYER_FLEET + _DEFAULT_AI_FLEET
        environment = {"wind_dir": 0, "wind_strength": 0}
        map_size = [22, 25]
    else:
        initial_vessels = []
        environment = {}
        map_size = [22, 25]

    sio.emit(
        "join_room",
        {
            "room": ROOM,
            "mode": selected_mode,
            "vessels": initial_vessels,
            "environment": environment,
            "map_size": map_size,
        },
    )
    log.info("Joined room '%s' in mode '%s'", ROOM, selected_mode)

    # ── Phase 4: Game loop ────────────────────────────────────────────
    global _selected_vessel_id, _zoom, _scroll_x, _scroll_y
    global _drag_hbar, _drag_vbar, _drag_start_mouse, _drag_start_scroll

    running = True
    while running:
        w, h = screen.get_size()
        roster_x = w - ROSTER_PANEL_W

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.VIDEORESIZE:
                # Re-clamp scroll so board stays in view after resize.
                _scroll_x, _scroll_y = _clamp_scroll(
                    _scroll_x, _scroll_y, _zoom, roster_x, h
                )

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r and sio.connected:
                    sio.emit("join_room", {"room": ROOM, "mode": selected_mode})
                # Zoom: + / = to zoom in, - to zoom out
                elif event.key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
                    _zoom = min(_ZOOM_MAX, round(_zoom + _ZOOM_STEP, 2))
                    _scroll_x, _scroll_y = _clamp_scroll(
                        _scroll_x, _scroll_y, _zoom, roster_x, h
                    )
                elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    _zoom = max(_ZOOM_MIN, round(_zoom - _ZOOM_STEP, 2))
                    _scroll_x, _scroll_y = _clamp_scroll(
                        _scroll_x, _scroll_y, _zoom, roster_x, h
                    )
                # Arrow-key scroll
                elif event.key == pygame.K_LEFT:
                    _scroll_x, _scroll_y = _clamp_scroll(
                        _scroll_x - _SCROLL_STEP, _scroll_y, _zoom, roster_x, h
                    )
                elif event.key == pygame.K_RIGHT:
                    _scroll_x, _scroll_y = _clamp_scroll(
                        _scroll_x + _SCROLL_STEP, _scroll_y, _zoom, roster_x, h
                    )
                elif event.key == pygame.K_UP:
                    _scroll_x, _scroll_y = _clamp_scroll(
                        _scroll_x, _scroll_y - _SCROLL_STEP, _zoom, roster_x, h
                    )
                elif event.key == pygame.K_DOWN:
                    _scroll_x, _scroll_y = _clamp_scroll(
                        _scroll_x, _scroll_y + _SCROLL_STEP, _zoom, roster_x, h
                    )

            elif event.type == pygame.MOUSEWHEEL:
                mods = pygame.key.get_mods()
                if mods & pygame.KMOD_CTRL:
                    _zoom = max(_ZOOM_MIN, min(_ZOOM_MAX,
                                round(_zoom + _ZOOM_STEP * event.y, 2)))
                    _scroll_x, _scroll_y = _clamp_scroll(
                        _scroll_x, _scroll_y, _zoom, roster_x, h
                    )
                else:
                    _scroll_x, _scroll_y = _clamp_scroll(
                        _scroll_x - _SCROLL_STEP * event.x,
                        _scroll_y - _SCROLL_STEP * event.y,
                        _zoom, roster_x, h,
                    )

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if hasattr(run, "_h_thumb") and run._h_thumb.collidepoint(event.pos):
                    _drag_hbar = True
                    _drag_start_mouse = event.pos[0]
                    _drag_start_scroll = _scroll_x
                elif hasattr(run, "_v_thumb") and run._v_thumb.collidepoint(event.pos):
                    _drag_vbar = True
                    _drag_start_mouse = event.pos[1]
                    _drag_start_scroll = _scroll_y

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                _drag_hbar = False
                _drag_vbar = False

            elif event.type == pygame.MOUSEMOTION:
                board_w, board_h = _board_pixel_size(_zoom)
                view_w = roster_x - 10 - _SB_THICK
                view_h = h - 44 - _SB_THICK - 150
                if _drag_hbar and board_w > view_w:
                    delta = event.pos[0] - _drag_start_mouse
                    ratio = delta / max(1, view_w - _SB_MIN_THUMB)
                    _scroll_x = _drag_start_scroll + int(ratio * (board_w - view_w))
                    _scroll_x, _scroll_y = _clamp_scroll(
                        _scroll_x, _scroll_y, _zoom, roster_x, h
                    )
                if _drag_vbar and board_h > view_h:
                    delta = event.pos[1] - _drag_start_mouse
                    ratio = delta / max(1, view_h - _SB_MIN_THUMB)
                    _scroll_y = _drag_start_scroll + int(ratio * (board_h - view_h))
                    _scroll_x, _scroll_y = _clamp_scroll(
                        _scroll_x, _scroll_y, _zoom, roster_x, h
                    )

        screen.fill(NAVY_BLUE)
        _draw_status_bar(screen, font)

        vessels = game_state.get("vessels", [])

        # Derive hex_size and board origin from current zoom and scroll.
        current_hex_size = max(6, int(_BASE_HEX_SIZE * _zoom))
        board_origin = (10 - _scroll_x, 44 - _scroll_y)

        # Board grid dimensions from server state (set when room was created).
        map_cols, map_rows = game_state.get("map_size", [22, 25])
        map_cols = max(22, int(map_cols))
        map_rows = max(25, int(map_rows))

        # ── Hex board ─────────────────────────────────────────────────
        board_click = fleet_ui.draw_hex_board(
            screen, vessels, _selected_vessel_id,
            board_cols=map_cols,
            board_rows=map_rows,
            hex_size=current_hex_size,
            origin=board_origin,
            roster_x=roster_x,
        )
        if board_click is not None:
            if board_click["type"] == "vessel":
                _selected_vessel_id = board_click["vessel_id"]
                log.info("Vessel selected via board click: %s", _selected_vessel_id)
            elif board_click["type"] == "hex" and _selected_vessel_id and sio.connected:
                sio.emit("player_action", {
                    "room": ROOM,
                    "action": "move_to",
                    "vessel_id": _selected_vessel_id,
                    "target_pos": [board_click["q"], board_click["r"]],
                })
                log.info(
                    "move_to [%d, %d] emitted for vessel %s",
                    board_click["q"], board_click["r"], _selected_vessel_id,
                )

        # ── Wind / tide indicator ──────────────────────────────────
        env = game_state.get("environment", {})
        fleet_ui.draw_wind_tide_indicator(screen, env)

        # ── Scrollbars ────────────────────────────────────────────────
        run._h_thumb, run._v_thumb = _draw_scrollbars(
            screen, _zoom, _scroll_x, _scroll_y, roster_x, h,
            board_cols=map_cols, board_rows=map_rows,
        )

        # ── Right panel: Fleet roster + unit card ─────────────────────
        _draw_vessel_list(screen, font, roster_x, w, h)

        # Unit card for the currently selected vessel.
        if _selected_vessel_id:
            sel_vessel = next(
                (v for v in vessels if v.get("id") == _selected_vessel_id),
                None,
            )
            if sel_vessel is not None:
                card_x = roster_x + 4
                card_y = h - 300
                fleet_ui.draw_unit_card(screen, sel_vessel, (card_x, card_y))

        _draw_ack_banner(screen, small_font)
        _draw_controls(screen, small_font)

        # ── Action panel ──────────────────────────────────────────────
        panel_result = fleet_ui.draw_action_panel(
            screen, vessels, _selected_vessel_id
        )
        if panel_result is not None:
            if panel_result["action"] == "select":
                _selected_vessel_id = panel_result["vessel_id"]
                log.info("Vessel selected: %s", _selected_vessel_id)
            elif sio.connected:
                sio.emit("player_action", {
                    "room": ROOM,
                    "action": panel_result["action"],
                    "vessel_id": panel_result["vessel_id"],
                })
                log.info(
                    "Player action emitted: %s on %s",
                    panel_result["action"],
                    panel_result["vessel_id"],
                )

        # ── Exit button ───────────────────────────────────────────────
        if fleet_ui.draw_exit_button(screen):
            running = False

        pygame.display.flip()
        clock.tick(FPS)

    sio.disconnect()
    pygame.quit()


if __name__ == "__main__":
    run()
