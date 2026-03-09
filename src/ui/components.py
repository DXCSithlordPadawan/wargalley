"""
ui/components.py — Pygame UI components for War Galley Digital Engine.
=======================================================================
Provides FleetUI with five rendering primitives:
  - draw_unit_card()    : renders a vessel stat card on screen.
  - draw_menu()         : renders the pre-game mode selection screen.
                          Returns the chosen mode string or None each frame.
  - draw_hex_board()    : renders the axial hex grid with vessel tokens.
                          Returns a vessel ID if a token was clicked, else None.
  - draw_action_panel() : renders the in-game action panel for turn input.
                          Returns an action dict when a button is clicked,
                          or None each frame.
  - draw_exit_button()  : renders an Exit button; returns True when clicked.
"""

import math
from typing import Optional

import pygame

# ---------------------------------------------------------------------------
# Colour constants shared by all components
# ---------------------------------------------------------------------------
NAVY_BLUE = (10, 20, 60)
SAND = (240, 230, 200)
WHITE = (255, 255, 255)
CRIMSON = (180, 30, 30)
DARK_RED = (120, 0, 0)
GOLD = (212, 175, 55)
LIGHT_GREY = (180, 180, 180)
BTN_HOVER = (60, 90, 140)
BTN_NORMAL = (30, 50, 100)
BTN_BORDER = (212, 175, 55)

# Hex board colours
HEX_FILL   = (20, 50, 90)      # empty hex interior
HEX_EDGE   = (50, 90, 140)     # hex border
HEX_WATER  = (15, 35, 75)      # alternate water shade
HEX_HOVER  = (40, 100, 60)     # empty hex hover highlight (move target)
HEX_HOVER_EDGE = (80, 200, 120) # border for hovered move-target hex
TOKEN_PLAYER = (60, 160, 80)   # player vessel token
TOKEN_AI     = (180, 60, 60)   # AI vessel token
TOKEN_SEL    = (212, 175, 55)  # selected vessel highlight

# Flat-top hex geometry: axial [q, r] → pixel (x, y).
# Board is rendered in a fixed region; these constants are recalculated
# inside draw_hex_board() but kept here for reference.
_HEX_SIZE: int = 28            # pixel radius of each hexagon

# Six axial facing directions (flat-top, matching server/AI convention).
_HEX_DIRS: tuple[tuple[int, int], ...] = (
    (1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)
)

# Facing arrow end-point offsets (unit vectors scaled to token radius).
_FACING_ANGLES: tuple[float, ...] = (
    0.0,          # 0 — East
    -math.pi / 3, # 1 — NE
    -2 * math.pi / 3,  # 2 — NW
    math.pi,      # 3 — West
    2 * math.pi / 3,   # 4 — SW
    math.pi / 3,  # 5 — SE
)


class FleetUI:
    """Collection of Pygame rendering helpers for the War Galley UI."""

    # ------------------------------------------------------------------
    # Unit card
    # ------------------------------------------------------------------

    def draw_unit_card(
        self,
        screen: pygame.Surface,
        data: dict,
        pos: tuple[int, int],
    ) -> None:
        """Render a parchment-style vessel stat card.

        Args:
            screen: The active Pygame display surface.
            data:   Vessel dict (must contain 'name' and 'traits' keys).
            pos:    (x, y) top-left pixel position for the card.
        """
        rect = pygame.Rect(pos[0], pos[1], 250, 300)
        pygame.draw.rect(screen, SAND, rect)
        pygame.draw.rect(screen, DARK_RED, rect, 2)  # Border

        font = pygame.font.SysFont("Georgia", 20)
        title = font.render(data.get("name", "Unknown"), True, (0, 0, 0))
        screen.blit(title, (pos[0] + 10, pos[1] + 10))

        y_offset = 50
        for trait in data.get("traits", []):
            trait_surf = font.render(f"• {trait.upper()}", True, CRIMSON)
            screen.blit(trait_surf, (pos[0] + 10, pos[1] + y_offset))
            y_offset += 30

    # ------------------------------------------------------------------
    # Pre-game mode selection menu
    # ------------------------------------------------------------------

    def draw_menu(
        self,
        screen: pygame.Surface,
        clock: pygame.time.Clock,
    ) -> Optional[str]:
        """Render the game mode selection screen for one frame.

        Should be called in a loop until a non-None value is returned.

        Args:
            screen: The active Pygame display surface.
            clock:  The Pygame clock (used only to read mouse position;
                    tick() is called by the caller's loop).

        Returns:
            "vs_computer" if the player chose Single Player.
            "vs_player"   if the player chose Two Player (networked).
            None          if no button has been clicked yet.
        """
        width, height = screen.get_size()
        screen.fill(NAVY_BLUE)

        title_font = pygame.font.SysFont("Georgia", 48, bold=True)
        sub_font = pygame.font.SysFont("Georgia", 22)
        btn_font = pygame.font.SysFont("Georgia", 26, bold=True)

        # ── Title ──────────────────────────────────────────────────────
        title_surf = title_font.render("⚓ War Galley", True, GOLD)
        title_rect = title_surf.get_rect(center=(width // 2, height // 4))
        screen.blit(title_surf, title_rect)

        subtitle_surf = sub_font.render("Select Game Mode", True, SAND)
        subtitle_rect = subtitle_surf.get_rect(center=(width // 2, height // 4 + 60))
        screen.blit(subtitle_surf, subtitle_rect)

        # ── Buttons ────────────────────────────────────────────────────
        btn_w, btn_h = 320, 70
        btn_gap = 30
        centre_y = height // 2 + 20

        vs_cpu_rect = pygame.Rect(0, 0, btn_w, btn_h)
        vs_cpu_rect.center = (width // 2, centre_y)

        vs_player_rect = pygame.Rect(0, 0, btn_w, btn_h)
        vs_player_rect.center = (width // 2, centre_y + btn_h + btn_gap)

        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]

        for rect, label, mode in (
            (vs_cpu_rect, "Single Player (vs Computer)", "vs_computer"),
            (vs_player_rect, "Two Player (vs Player)", "vs_player"),
        ):
            hovered = rect.collidepoint(mouse_pos)
            bg_colour = BTN_HOVER if hovered else BTN_NORMAL
            pygame.draw.rect(screen, bg_colour, rect, border_radius=8)
            pygame.draw.rect(screen, BTN_BORDER, rect, 2, border_radius=8)

            label_surf = btn_font.render(label, True, WHITE)
            label_rect = label_surf.get_rect(center=rect.center)
            screen.blit(label_surf, label_rect)

            if hovered and mouse_clicked:
                return mode

        # ── Footer hint ────────────────────────────────────────────────
        hint_surf = sub_font.render("ESC — quit", True, LIGHT_GREY)
        hint_rect = hint_surf.get_rect(center=(width // 2, height - 40))
        screen.blit(hint_surf, hint_rect)

        return None  # No selection yet

    # ------------------------------------------------------------------
    # Scenario selection menu
    # ------------------------------------------------------------------

    def draw_scenario_menu(
        self,
        screen: pygame.Surface,
        scenarios: list[dict],
    ) -> Optional[dict]:
        """Render a scenario selection screen for one frame.

        Should be called in a loop until a non-None value is returned.

        Args:
            screen:    The active Pygame display surface.
            scenarios: List of scenario dicts, each with keys:
                         'name' (str)  — human-readable name from YAML.
                         'path' (str)  — source file path (for display only).
                         'data' (dict) — raw parsed YAML content.

        Returns:
            The chosen scenario dict (with 'name', 'path', 'data') when the
            player clicks one, or a sentinel dict ``{'name': 'Default',
            'path': '', 'data': None}`` when they choose to skip, or None
            if no selection has been made yet this frame.
        """
        width, height = screen.get_size()
        screen.fill(NAVY_BLUE)

        title_font = pygame.font.SysFont("Georgia", 40, bold=True)
        sub_font   = pygame.font.SysFont("Georgia", 20)
        btn_font   = pygame.font.SysFont("Georgia", 22, bold=True)
        info_font  = pygame.font.SysFont("Georgia", 15)

        # ── Title ─────────────────────────────────────────────────
        title_surf = title_font.render("⚓ Select Scenario", True, GOLD)
        title_rect = title_surf.get_rect(center=(width // 2, 60))
        screen.blit(title_surf, title_rect)

        sub_surf = sub_font.render(
            "Choose a historical battle or use the default fleet.",
            True, SAND,
        )
        sub_rect = sub_surf.get_rect(center=(width // 2, 105))
        screen.blit(sub_surf, sub_rect)

        mouse_pos    = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]

        btn_w, btn_h = min(560, width - 80), 64
        btn_gap      = 12
        start_y      = 140
        centre_x     = width // 2

        # ── Scenario buttons ────────────────────────────────────────
        for scenario in scenarios:
            rect = pygame.Rect(0, 0, btn_w, btn_h)
            rect.centerx = centre_x
            rect.y = start_y

            # Only render if on screen.
            if rect.bottom > height - 80:
                break

            hovered = rect.collidepoint(mouse_pos)
            bg = BTN_HOVER if hovered else BTN_NORMAL
            pygame.draw.rect(screen, bg, rect, border_radius=8)
            pygame.draw.rect(screen, BTN_BORDER, rect, 2, border_radius=8)

            # Scenario name.
            name_surf = btn_font.render(scenario["name"], True, WHITE)
            name_rect = name_surf.get_rect(midleft=(rect.x + 16, rect.y + 22))
            screen.blit(name_surf, name_rect)

            # File path hint.
            hint = info_font.render(
                scenario["path"], True, LIGHT_GREY
            )
            screen.blit(hint, (rect.x + 16, rect.y + 42))

            if hovered and mouse_clicked:
                return scenario

            start_y += btn_h + btn_gap

        # ── "Use Default Fleet" button ───────────────────────────
        default_rect = pygame.Rect(0, 0, btn_w, 50)
        default_rect.centerx = centre_x
        default_rect.bottom  = height - 50

        hovered_def = default_rect.collidepoint(mouse_pos)
        bg_def = (50, 80, 50) if hovered_def else (30, 55, 30)
        pygame.draw.rect(screen, bg_def, default_rect, border_radius=8)
        pygame.draw.rect(screen, BTN_BORDER, default_rect, 2, border_radius=8)
        def_surf = btn_font.render("Use Default Fleet", True, WHITE)
        def_rect = def_surf.get_rect(center=default_rect.center)
        screen.blit(def_surf, def_rect)

        if hovered_def and mouse_clicked:
            return {"name": "Default", "path": "", "data": None}

        return None  # No selection yet

    # ------------------------------------------------------------------
    # Wind / tide indicator
    # ------------------------------------------------------------------

    def draw_wind_tide_indicator(
        self,
        screen: pygame.Surface,
        environment: dict,
    ) -> None:
        """Render a compact wind and tide compass in the top-left board corner.

        The indicator is drawn as a small filled circle with one or two arrows:
          - A white arrow for wind direction (always shown if wind_strength > 0).
          - A cyan arrow for tide direction (shown when tide_dir is present).
        Facing indices follow the same convention as vessels:
          0=East, 1=NE, 2=NW, 3=West, 4=SW, 5=SE.

        Args:
            screen:      Active Pygame display surface.
            environment: Dict from game_state['environment'].  May be empty.
        """
        if not environment:
            return

        wind_dir      = environment.get("wind_dir")
        wind_strength = environment.get("wind_strength", 0)
        tide_dir      = environment.get("tide_dir")

        # Nothing to show.
        if wind_dir is None and tide_dir is None:
            return

        # Compass position — top-left area of the board.
        cx, cy = 54, 90
        radius = 22

        bg_surf = pygame.Surface((radius * 2 + 20, radius * 2 + 60), pygame.SRCALPHA)
        bg_surf.fill((0, 0, 0, 0))
        screen.blit(bg_surf, (cx - radius - 10, cy - radius - 10))

        # Background disc.
        pygame.draw.circle(screen, (20, 35, 70), (cx, cy), radius)
        pygame.draw.circle(screen, GOLD, (cx, cy), radius, 1)

        font_small = pygame.font.SysFont("Georgia", 11, bold=True)

        # ── Wind arrow (white) ────────────────────────────────────────
        if wind_dir is not None and wind_strength > 0:
            angle = _FACING_ANGLES[int(wind_dir) % 6]
            wx = int(cx + (radius - 4) * math.cos(angle))
            wy = int(cy - (radius - 4) * math.sin(angle))
            pygame.draw.line(screen, WHITE, (cx, cy), (wx, wy), 3)
            # Arrow head.
            head_angle_l = angle + math.radians(140)
            head_angle_r = angle - math.radians(140)
            head_len = 7
            pygame.draw.line(
                screen, WHITE, (wx, wy),
                (int(wx + head_len * math.cos(head_angle_l)),
                 int(wy - head_len * math.sin(head_angle_l))), 2
            )
            pygame.draw.line(
                screen, WHITE, (wx, wy),
                (int(wx + head_len * math.cos(head_angle_r)),
                 int(wy - head_len * math.sin(head_angle_r))), 2
            )
            # Wind strength label.
            w_label = font_small.render(f"W{wind_strength}", True, WHITE)
            screen.blit(w_label, (cx - radius, cy + radius + 4))

        # ── Tide arrow (cyan, dashed appearance via two segments) ─────
        if tide_dir is not None:
            t_angle = _FACING_ANGLES[int(tide_dir) % 6]
            CYAN = (0, 210, 220)
            # Draw a shorter, inner arrow to distinguish from wind.
            inner = radius - 10
            tx = int(cx + inner * math.cos(t_angle))
            ty = int(cy - inner * math.sin(t_angle))
            pygame.draw.line(screen, CYAN, (cx, cy), (tx, ty), 2)
            head_angle_l = t_angle + math.radians(140)
            head_angle_r = t_angle - math.radians(140)
            head_len = 5
            pygame.draw.line(
                screen, CYAN, (tx, ty),
                (int(tx + head_len * math.cos(head_angle_l)),
                 int(ty - head_len * math.sin(head_angle_l))), 2
            )
            pygame.draw.line(
                screen, CYAN, (tx, ty),
                (int(tx + head_len * math.cos(head_angle_r)),
                 int(ty - head_len * math.sin(head_angle_r))), 2
            )
            t_label = font_small.render("Tide", True, CYAN)
            screen.blit(t_label, (cx - radius, cy + radius + 18))

        # ── Cardinal labels (N / S / E / W) ──────────────────────────
        for label, lx, ly in (
            ("N", cx,            cy - radius - 9),
            ("S", cx,            cy + radius + 1),
            ("E", cx + radius + 2, cy - 6),
            ("W", cx - radius - 9, cy - 6),
        ):
            surf = font_small.render(label, True, LIGHT_GREY)
            screen.blit(surf, (lx, ly))

    # ------------------------------------------------------------------
    # Hex board
    # ------------------------------------------------------------------

    def draw_hex_board(
        self,
        screen: pygame.Surface,
        vessels: list,
        selected_vessel_id: Optional[str],
        board_cols: int = 22,
        board_rows: int = 25,
        hex_size: int = _HEX_SIZE,
        origin: tuple[int, int] = (10, 48),
        roster_x: int = 724,
    ) -> Optional[dict]:
        """Render a flat-top axial hex grid with vessel tokens.

        Draws every hex cell in the board_cols × board_rows area, then
        overlays a coloured circle token for each vessel positioned on a
        visible hex.

        Returns one of:
          {"type": "vessel", "vessel_id": str}  — player clicked a vessel token.
          {"type": "hex",    "q": int, "r": int} — player clicked an empty hex
                                                    while a vessel is selected.
          None — nothing actionable was clicked this frame.

        When a vessel is selected, empty hexes are highlighted on hover to
        indicate they are valid move targets.

        Args:
            screen:             Active Pygame display surface.
            vessels:            List of vessel dicts from game_state.
            selected_vessel_id: Currently selected vessel ID, or None.
            board_cols:         Axial q range [0, board_cols) to render.
            board_rows:         Axial r range [0, board_rows) to render.
            hex_size:           Maximum pixel radius; auto-clamped to fit.
            origin:             (x, y) pixel offset of axial [0, 0].

        Returns:
            dict or None as described above.
        """
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]
        result: Optional[dict] = None   # return value built during iteration

        w, h = screen.get_size()

        # ── Auto-scale hex_size to fit the full axial grid within the board
        # area (left of the roster panel, below the status bar).
        # board area width  = roster_x - origin_x - small margin
        # board area height = screen height - origin_y - action panel - hint bar
        board_area_w = roster_x - origin[0] - 4
        board_area_h = h - origin[1] - 150  # leave room for action panel

        # Flat-top pixel span for board_cols columns:
        #   width  ~= hex_size * 1.5 * board_cols
        # Pointy-row pixel span for board_rows rows (flat-top):
        #   height ~= hex_size * sqrt(3) * board_rows
        max_size_w = int(board_area_w / (1.5 * board_cols))
        max_size_h = int(board_area_h / (math.sqrt(3) * board_rows))
        hex_size = max(6, min(hex_size, max_size_w, max_size_h))

        # Pre-build a lookup: (q, r) -> vessel for fast per-hex access.
        vessel_at: dict[tuple[int, int], dict] = {
            (v["pos"][0], v["pos"][1]): v
            for v in vessels
            if isinstance(v.get("pos"), list) and len(v["pos"]) >= 2
        }

        ox, oy = origin
        lbl_font = pygame.font.SysFont("Georgia", 11, bold=True)

        # ── Draw all hexes ────────────────────────────────────────────
        for q in range(board_cols):
            for r in range(board_rows):
                cx, cy = self._axial_to_pixel(q, r, hex_size, ox, oy)

                # Skip hexes whose centres fall outside the screen.
                if not (0 < cx < w and 0 < cy < h):
                    continue

                corners = self._hex_corners(cx, cy, hex_size)
                vessel = vessel_at.get((q, r))

                # ── Hex hover highlight (empty hex + vessel selected) ──
                mouse_in_hex = False
                if selected_vessel_id is not None and vessel is None:
                    # Point-in-polygon test using pygame.draw + get_at would
                    # be expensive; use bounding-circle approximation instead.
                    dx_h = mouse_pos[0] - cx
                    dy_h = mouse_pos[1] - cy
                    # A hex is fully enclosed in a circle of radius hex_size.
                    if dx_h * dx_h + dy_h * dy_h <= hex_size * hex_size:
                        mouse_in_hex = True

                # Base fill colour.
                if mouse_in_hex:
                    fill = HEX_HOVER
                    edge = HEX_HOVER_EDGE
                else:
                    fill = HEX_WATER if (q + r) % 2 == 0 else HEX_FILL
                    edge = HEX_EDGE

                pygame.draw.polygon(screen, fill, corners)
                pygame.draw.polygon(screen, edge, corners, 1)

                # Hex click: empty hex while a vessel is selected.
                if mouse_in_hex and mouse_clicked and vessel is None:
                    result = {"type": "hex", "q": q, "r": r}

                # ── Vessel token ──────────────────────────────────────
                if vessel is None:
                    continue

                vid = vessel.get("id", "")
                side = vessel.get("side", "")
                is_selected = vid == selected_vessel_id
                token_r = max(4, hex_size - 6)

                # Outer selection ring.
                if is_selected:
                    pygame.draw.circle(
                        screen, TOKEN_SEL, (cx, cy), token_r + 4, 3
                    )

                # Token fill.
                token_colour = TOKEN_PLAYER if side == "player" else TOKEN_AI
                pygame.draw.circle(screen, token_colour, (cx, cy), token_r)
                pygame.draw.circle(screen, WHITE, (cx, cy), token_r, 1)

                # Facing arrow.
                facing = vessel.get("facing", 0) % 6
                angle = _FACING_ANGLES[facing]
                arrow_len = token_r - 3
                ax = int(cx + arrow_len * math.cos(angle))
                ay = int(cy - arrow_len * math.sin(angle))
                pygame.draw.line(screen, WHITE, (cx, cy), (ax, ay), 2)

                # Vessel initial label.
                name = vessel.get("name", "?")
                initials = "".join(word[0] for word in name.split()[:2]).upper()
                lbl = lbl_font.render(initials, True, WHITE)
                lbl_rect = lbl.get_rect(center=(cx, cy + token_r + 9))
                if 0 < lbl_rect.right < w and 0 < lbl_rect.bottom < h:
                    screen.blit(lbl, lbl_rect)

                # HP bar.
                max_hull = 60
                hull_pct = max(0.0, min(1.0, vessel.get("hull", 0) / max_hull))
                bar_w = token_r * 2
                bar_x = cx - token_r
                bar_y = cy + token_r + 19
                if 0 < bar_y < h:
                    pygame.draw.rect(screen, CRIMSON, (bar_x, bar_y, bar_w, 4))
                    pygame.draw.rect(
                        screen, (60, 200, 60),
                        (bar_x, bar_y, int(bar_w * hull_pct), 4)
                    )

                # Vessel token click.
                dx = mouse_pos[0] - cx
                dy = mouse_pos[1] - cy
                if dx * dx + dy * dy <= token_r * token_r and mouse_clicked:
                    result = {"type": "vessel", "vessel_id": vid}

        return result

    # ------------------------------------------------------------------
    # Hex geometry helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _axial_to_pixel(
        q: int,
        r: int,
        size: int,
        ox: int,
        oy: int,
    ) -> tuple[int, int]:
        """Convert flat-top axial hex coordinates to pixel centre.

        Formula (flat-top):
            x = size * (3/2 * q)
            y = size * (sqrt(3)/2 * q  +  sqrt(3) * r)
        """
        x = ox + int(size * 1.5 * q)
        y = oy + int(size * (math.sqrt(3) / 2 * q + math.sqrt(3) * r))
        return x, y

    @staticmethod
    def _hex_corners(
        cx: int,
        cy: int,
        size: int,
    ) -> list[tuple[int, int]]:
        """Return the six pixel corner coordinates for a flat-top hexagon."""
        corners = []
        for i in range(6):
            angle_deg = 60 * i           # flat-top: 0, 60, 120 …
            angle_rad = math.radians(angle_deg)
            corners.append((
                int(cx + size * math.cos(angle_rad)),
                int(cy + size * math.sin(angle_rad)),
            ))
        return corners

    # ------------------------------------------------------------------
    # In-game action panel (turn input)
    # ------------------------------------------------------------------

    def draw_action_panel(
        self,
        screen: pygame.Surface,
        vessels: list,
        selected_vessel_id: Optional[str],
    ) -> Optional[dict]:
        """Render the action panel for the current player's turn.

        Displays a row of action buttons (Move, Ram, Board, Pass) and a
        simple vessel selector.  Returns an action dict when the player
        clicks a button, otherwise None.

        Args:
            screen:             The active Pygame display surface.
            vessels:            List of vessel dicts from the current game
                                state (used to populate the selector).
            selected_vessel_id: The vessel ID currently selected, or None.

        Returns:
            dict with keys 'action' and 'vessel_id' when an action button
            is clicked, or None if nothing was clicked this frame.
        """
        width, height = screen.get_size()
        panel_h = 110
        panel_y = height - panel_h - 36  # sit above the controls hint
        panel_rect = pygame.Rect(0, panel_y, width, panel_h)

        # Semi-transparent panel background
        panel_surf = pygame.Surface((width, panel_h), pygame.SRCALPHA)
        panel_surf.fill((10, 20, 60, 210))
        screen.blit(panel_surf, (0, panel_y))
        pygame.draw.line(screen, GOLD, (0, panel_y), (width, panel_y), 1)

        btn_font = pygame.font.SysFont("Georgia", 18, bold=True)
        label_font = pygame.font.SysFont("Georgia", 16)

        # ── Vessel selector ────────────────────────────────────────────
        player_vessels = [
            v for v in vessels if v.get("side") == "player"
        ]
        sel_x = 20
        sel_y = panel_y + 10
        sel_label = label_font.render("Select vessel:", True, SAND)
        screen.blit(sel_label, (sel_x, sel_y))

        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]

        vessel_btn_w, vessel_btn_h = 160, 28
        for idx, vessel in enumerate(player_vessels[:4]):
            vr = pygame.Rect(
                sel_x, sel_y + 24 + idx * (vessel_btn_h + 4),
                vessel_btn_w, vessel_btn_h,
            )
            is_selected = vessel.get("id") == selected_vessel_id
            bg = BTN_HOVER if (is_selected or vr.collidepoint(mouse_pos)) else BTN_NORMAL
            pygame.draw.rect(screen, bg, vr, border_radius=4)
            pygame.draw.rect(screen, BTN_BORDER, vr, 1, border_radius=4)
            name_surf = label_font.render(
                vessel.get("name", vessel.get("id", "?")), True, WHITE
            )
            screen.blit(name_surf, (vr.x + 6, vr.y + 5))
            # Vessel selection click is returned as a special action type
            # so the caller can update selected_vessel_id.
            if vr.collidepoint(mouse_pos) and mouse_clicked:
                return {"action": "select", "vessel_id": vessel.get("id")}

        # ── Action buttons ─────────────────────────────────────────────
        actions = [
            ("Turn L",  "turn_left"),
            ("Move",    "move_forward"),
            ("Back",    "move_backward"),
            ("Turn R",  "turn_right"),
            ("Ram",     "ram"),
            ("Board",   "board"),
            ("Pass",    "pass"),
        ]
        act_btn_w, act_btn_h = 80, 44
        act_gap = 14
        total_w = len(actions) * act_btn_w + (len(actions) - 1) * act_gap
        act_start_x = (width - total_w) // 2
        act_y = panel_y + (panel_h - act_btn_h) // 2

        for i, (label, action_key) in enumerate(actions):
            ar = pygame.Rect(
                act_start_x + i * (act_btn_w + act_gap),
                act_y,
                act_btn_w,
                act_btn_h,
            )
            hovered = ar.collidepoint(mouse_pos)
            # Disable action buttons when no vessel is selected
            active = selected_vessel_id is not None
            if not active:
                bg = (20, 30, 60)  # dimmed
                border = LIGHT_GREY
            else:
                bg = BTN_HOVER if hovered else BTN_NORMAL
                border = BTN_BORDER
            pygame.draw.rect(screen, bg, ar, border_radius=6)
            pygame.draw.rect(screen, border, ar, 2, border_radius=6)
            lbl_surf = btn_font.render(label, True, WHITE if active else LIGHT_GREY)
            lbl_rect = lbl_surf.get_rect(center=ar.center)
            screen.blit(lbl_surf, lbl_rect)

            if hovered and mouse_clicked and active:
                return {"action": action_key, "vessel_id": selected_vessel_id}

        return None  # No action this frame

    # ------------------------------------------------------------------
    # Exit button
    # ------------------------------------------------------------------

    def draw_exit_button(
        self,
        screen: pygame.Surface,
    ) -> bool:
        """Render a clickable Exit button in the bottom-right corner.

        Args:
            screen: The active Pygame display surface.

        Returns:
            True if the button was clicked this frame, False otherwise.
        """
        btn_font = pygame.font.SysFont("Georgia", 18, bold=True)
        btn_w, btn_h = 90, 26
        width, height = screen.get_size()
        rect = pygame.Rect(width - btn_w - 12, height - btn_h - 4, btn_w, btn_h)

        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]
        hovered = rect.collidepoint(mouse_pos)

        bg = CRIMSON if hovered else DARK_RED
        pygame.draw.rect(screen, bg, rect, border_radius=5)
        pygame.draw.rect(screen, GOLD, rect, 1, border_radius=5)

        lbl = btn_font.render("Exit", True, WHITE)
        lbl_rect = lbl.get_rect(center=rect.center)
        screen.blit(lbl, lbl_rect)

        return bool(hovered and mouse_clicked)
