"""
War Galley Digital Engine — Pygame Client
==========================================
Connects to the Flask-SocketIO server and presents the interactive game UI.

Usage:
    python3 src/client.py                      # connect to http://localhost:5000
    SERVER_URL=http://192.168.1.10:5000 python3 src/client.py
    ROOM=battle1 python3 src/client.py
"""

import os
import sys
import logging

import socketio
import pygame

from ui.components import FleetUI

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
SERVER_URL: str = os.environ.get("SERVER_URL", "http://localhost:5000")
ROOM: str = os.environ.get("ROOM", "default")

SCREEN_W: int = 1024
SCREEN_H: int = 768
FPS: int = 30

# Colour palette
NAVY_BLUE = (10, 20, 60)
SAND = (240, 230, 200)
WHITE = (255, 255, 255)
CRIMSON = (180, 30, 30)
LIGHT_GREY = (180, 180, 180)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Shared state (updated by SocketIO callbacks)
# ---------------------------------------------------------------------------
game_state: dict = {"vessels": [], "turn": 0}
_ack_message: str = ""

# ---------------------------------------------------------------------------
# SocketIO client
# ---------------------------------------------------------------------------
sio = socketio.Client(logger=False, engineio_logger=False)


@sio.event
def connect() -> None:
    log.info("Connected to War Galley server at %s", SERVER_URL)
    sio.emit("join_room", {"room": ROOM})


@sio.event
def disconnect() -> None:
    log.info("Disconnected from server.")


@sio.on("room_state")
def on_room_state(data: dict) -> None:
    global game_state
    game_state = data
    log.info("Room state received: turn %s, %d vessel(s)", data.get("turn"), len(data.get("vessels", [])))


@sio.on("action_ack")
def on_action_ack(data: dict) -> None:
    global _ack_message
    _ack_message = f"Action '{data.get('action')}' on vessel '{data.get('vessel_id')}' → {data.get('status')}"
    log.info("Action acknowledged: %s", data)


# ---------------------------------------------------------------------------
# Pygame rendering helpers
# ---------------------------------------------------------------------------

def _draw_status_bar(screen: pygame.Surface, font: pygame.font.Font) -> None:
    """Render room name, current turn, and vessel count at the top of the screen."""
    vessels = game_state.get("vessels", [])
    text = font.render(
        f"Room: {ROOM}   |   Turn: {game_state.get('turn', 0)}   |   Vessels: {len(vessels)}",
        True,
        WHITE,
    )
    screen.blit(text, (20, 16))


def _draw_vessel_list(screen: pygame.Surface, font: pygame.font.Font, fleet_ui: FleetUI) -> None:
    """List active vessels; draw the first vessel's Unit Card if available."""
    vessels = game_state.get("vessels", [])
    if not vessels:
        msg = font.render("Waiting for vessels to join the room…", True, SAND)
        screen.blit(msg, (20, 80))
        return

    # Draw Unit Cards for up to 3 vessels across the top area
    for idx, vessel in enumerate(vessels[:3]):
        fleet_ui.draw_unit_card(screen, vessel, (20 + idx * 270, 80))

    # List remaining vessel names below
    y = 420
    label = font.render("Fleet roster:", True, SAND)
    screen.blit(label, (20, y))
    y += 28
    for vessel in vessels:
        row = font.render(f"  • {vessel.get('name', '?')}  (HP {vessel.get('hull', '?')})", True, WHITE)
        screen.blit(row, (20, y))
        y += 24
        if y > SCREEN_H - 80:
            break


def _draw_ack_banner(screen: pygame.Surface, small_font: pygame.font.Font) -> None:
    """Show the most recent action acknowledgement in the status bar area."""
    if _ack_message:
        surf = small_font.render(_ack_message, True, CRIMSON)
        screen.blit(surf, (20, SCREEN_H - 52))


def _draw_controls(screen: pygame.Surface, small_font: pygame.font.Font) -> None:
    """Print a one-line control reference at the bottom of the screen."""
    hint = small_font.render(
        "ESC — quit   |   R — request state refresh",
        True,
        LIGHT_GREY,
    )
    screen.blit(hint, (20, SCREEN_H - 28))


# ---------------------------------------------------------------------------
# Main game loop
# ---------------------------------------------------------------------------

def run() -> None:
    """Initialise Pygame, connect to the server, and run the event loop."""
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("⚓ War Galley Digital Engine")
    clock = pygame.time.Clock()

    font = pygame.font.SysFont("Georgia", 20)
    small_font = pygame.font.SysFont("Georgia", 16)
    fleet_ui = FleetUI()

    # Attempt server connection -----------------------------------------------
    try:
        log.info("Connecting to %s …", SERVER_URL)
        sio.connect(SERVER_URL, transports=["websocket", "polling"])
    except ConnectionRefusedError:
        log.error(
            "Connection refused — is the server running at %s? "
            "Start it with: python3 src/server.py",
            SERVER_URL,
        )
        pygame.quit()
        sys.exit(1)
    except TimeoutError:
        log.error(
            "Connection timed out while reaching %s — check the SERVER_URL and your network.",
            SERVER_URL,
        )
        pygame.quit()
        sys.exit(1)
    except Exception as exc:  # noqa: BLE001
        log.error(
            "Could not connect to server at %s — %s. "
            "Verify the server is running and SERVER_URL is correct.",
            SERVER_URL,
            exc,
        )
        pygame.quit()
        sys.exit(1)

    # Event loop --------------------------------------------------------------
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r and sio.connected:
                    # Re-emit join_room so the server re-broadcasts the current
                    # room state (the server always emits room_state on join).
                    sio.emit("join_room", {"room": ROOM})

        screen.fill(NAVY_BLUE)
        _draw_status_bar(screen, font)
        _draw_vessel_list(screen, font, fleet_ui)
        _draw_ack_banner(screen, small_font)
        _draw_controls(screen, small_font)
        pygame.display.flip()
        clock.tick(FPS)

    sio.disconnect()
    pygame.quit()


if __name__ == "__main__":
    run()
