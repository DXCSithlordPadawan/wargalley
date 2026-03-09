"""
ai_minimax.py — AdmiralAI: Minimax engine for War Galley single-player mode.
=============================================================================
Provides the AdmiralAI class which uses alpha-beta pruned minimax search to
select the best action for the computer-controlled fleet ('AI' side).

Public API (used by server.py):
    ai = AdmiralAI(depth=3)
    move = ai.get_best_move(room_state)   # returns {"vessel_id": ..., "action": ...}

Vessel dict schema (from scenario YAML / room state):
    {
        "id":             str,
        "name":           str,       # display name
        "side":           str,       # "AI" | "player"
        "hull":           int,       # hit points remaining (0 = sunk)
        "marines":        int,       # boarding strength
        "ram_multiplier": float,     # damage multiplier for ram actions
        "facing":         int,       # 0-5 hex facing
        "pos":            [int, int],# [q, r] hex coordinates
        "traits":         list[str], # e.g. ["corvus", "ram_master"]
        "oars":           str,       # "Intact" | "Disabled"
    }
"""

import copy
import logging
from typing import Optional

log = logging.getLogger(__name__)

# Actions the AI can issue per vessel.
_POSSIBLE_ACTIONS: tuple[str, ...] = ("move_forward", "ram", "hold")

# Minimum hull threshold below which a vessel is considered combat-ineffective.
_SUNK_THRESHOLD: int = 0


class AdmiralAI:
    """Alpha-beta pruned minimax AI for the War Galley engine.

    Args:
        depth: Search depth.  Higher values are stronger but slower.
               Recommended: 1=Easy, 3=Normal (default), 5=Hard.
    """

    def __init__(self, depth: int = 3) -> None:
        if depth < 1:
            raise ValueError(f"depth must be >= 1, got {depth}")
        self.depth = depth

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_best_move(self, state: dict) -> dict:
        """Return the best move for the AI side.

        Iterates over all possible AI moves, runs minimax for each, and
        returns the move dict with the highest evaluation score.

        Returns:
            {"vessel_id": str, "action": str}  — the chosen move.
            Returns {"vessel_id": None, "action": "hold"} if no AI vessels
            are alive (caller should treat this as a no-op).
        """
        best_score: float = float("-inf")
        best_move: dict = {"vessel_id": None, "action": "hold"}

        for move in self.get_possible_moves(state, "AI"):
            simulated = self.simulate(state, move)
            score = self.minimax(
                simulated,
                depth=self.depth - 1,
                alpha=float("-inf"),
                beta=float("inf"),
                maximizing=False,  # Next ply is the player minimising
            )
            if score > best_score:
                best_score = score
                best_move = move

        log.info(
            "AdmiralAI selected move: %s (score=%.2f)",
            best_move,
            best_score,
        )
        return best_move

    # ------------------------------------------------------------------
    # Minimax core
    # ------------------------------------------------------------------

    def minimax(
        self,
        state: dict,
        depth: int,
        alpha: float,
        beta: float,
        maximizing: bool,
    ) -> float:
        """Recursive alpha-beta minimax search.

        Args:
            state:      Current room state snapshot.
            depth:      Remaining search depth.
            alpha:      Best score the maximising player can guarantee.
            beta:       Best score the minimising player can guarantee.
            maximizing: True when it is the AI's turn to maximise.

        Returns:
            Heuristic evaluation score for the given state.
        """
        if depth == 0 or self.is_terminal(state):
            return self.evaluate(state)

        if maximizing:
            max_eval: float = float("-inf")
            for move in self.get_possible_moves(state, "AI"):
                child_state = self.simulate(state, move)
                score = self.minimax(child_state, depth - 1, alpha, beta, False)
                max_eval = max(max_eval, score)
                alpha = max(alpha, score)
                if beta <= alpha:
                    break  # Beta cut-off
            return max_eval
        else:
            min_eval: float = float("inf")
            for move in self.get_possible_moves(state, "player"):
                child_state = self.simulate(state, move)
                score = self.minimax(child_state, depth - 1, alpha, beta, True)
                min_eval = min(min_eval, score)
                beta = min(beta, score)
                if beta <= alpha:
                    break  # Alpha cut-off
            return min_eval

    # ------------------------------------------------------------------
    # Heuristic evaluation
    # ------------------------------------------------------------------

    def evaluate(self, state: dict) -> float:
        """Score a state from the AI's perspective.

        Positive = good for AI; negative = good for player.
        Accounts for hull integrity, marines, and oar status.
        """
        score: float = 0.0
        for vessel in state.get("vessels", []):
            multiplier = 1.0 if vessel.get("side") == "AI" else -1.0
            hull = max(0, vessel.get("hull", 0))
            marines = max(0, vessel.get("marines", 0))
            oar_bonus = 0.0 if vessel.get("oars") == "Disabled" else 5.0
            score += (hull + marines * 0.5 + oar_bonus) * multiplier
        return score

    # ------------------------------------------------------------------
    # Terminal condition
    # ------------------------------------------------------------------

    def is_terminal(self, state: dict) -> bool:
        """Return True when one or both sides have no surviving vessels.

        A vessel is considered sunk when hull <= _SUNK_THRESHOLD.
        """
        vessels = state.get("vessels", [])
        ai_alive = any(
            v.get("side") == "AI" and v.get("hull", 0) > _SUNK_THRESHOLD
            for v in vessels
        )
        player_alive = any(
            v.get("side") == "player" and v.get("hull", 0) > _SUNK_THRESHOLD
            for v in vessels
        )
        return not ai_alive or not player_alive

    # ------------------------------------------------------------------
    # Move generation
    # ------------------------------------------------------------------

    def get_possible_moves(self, state: dict, side: str) -> list[dict]:
        """Return a list of possible moves for all living vessels on the
        given side.

        Each move is a dict:  {"vessel_id": str, "action": str}

        Only vessels with hull > _SUNK_THRESHOLD are included.
        Vessels with disabled oars cannot use "move_forward".
        """
        moves: list[dict] = []
        for vessel in state.get("vessels", []):
            if vessel.get("side") != side:
                continue
            if vessel.get("hull", 0) <= _SUNK_THRESHOLD:
                continue  # Sunk — no actions available

            oars_ok = vessel.get("oars", "Intact") != "Disabled"
            _, nearest_dist = _find_nearest_enemy(vessel, state.get("vessels", []))
            for action in _POSSIBLE_ACTIONS:
                if action == "move_forward" and not oars_ok:
                    continue  # Cannot move without oars
                if action == "ram" and nearest_dist > 1:
                    continue  # Enemy not adjacent — ram would have no effect
                moves.append({"vessel_id": vessel["id"], "action": action})

        return moves

    # ------------------------------------------------------------------
    # State simulation
    # ------------------------------------------------------------------

    def simulate(self, state: dict, move: dict) -> dict:
        """Apply *move* to a deep copy of *state* and return the result.

        Handles three action types:
        - "move_forward": advances the vessel one hex in its current facing.
        - "ram":          applies ram damage to the nearest enemy vessel.
        - "hold":         no-op; vessel stays in place.

        This is intentionally lightweight — full physics resolution
        (wind, tide, angle bonuses) is the role of GalleyEngine and is
        reserved for the actual game turn processor.  The AI simulation
        uses simplified damage to keep search depth practical.
        """
        new_state = copy.deepcopy(state)
        vessel_id = move.get("vessel_id")
        action = move.get("action", "hold")

        # Locate the acting vessel in the copied state.
        acting: Optional[dict] = next(
            (v for v in new_state.get("vessels", []) if v.get("id") == vessel_id),
            None,
        )
        if acting is None:
            return new_state  # Vessel not found — return unchanged state

        if action == "move_forward":
            _apply_move_forward(acting)

        elif action == "ram":
            target, dist = _find_nearest_enemy(acting, new_state.get("vessels", []))
            if target is not None:
                _apply_ram(acting, target, dist)

        # "hold" — deliberate no-op; vessel stays in place.

        # Increment turn counter so deeper plies reflect advancing turns.
        new_state["turn"] = new_state.get("turn", 0) + 1
        return new_state


# ---------------------------------------------------------------------------
# Private simulation helpers (module-level, not part of AdmiralAI interface)
# ---------------------------------------------------------------------------

# Axial hex direction vectors (facing 0-5, flat-top orientation).
_HEX_DIRECTIONS: tuple[tuple[int, int], ...] = (
    (1, 0),   # 0 — East
    (1, -1),  # 1 — North-East
    (0, -1),  # 2 — North-West
    (-1, 0),  # 3 — West
    (-1, 1),  # 4 — South-West
    (0, 1),   # 5 — South-East
)

# Simplified ram damage used during AI search (avoids importing GalleyEngine).
_RAM_BASE_DAMAGE: int = 10


def _apply_move_forward(vessel: dict) -> None:
    """Move vessel one hex in the direction of its current facing."""
    facing = vessel.get("facing", 0) % 6
    dq, dr = _HEX_DIRECTIONS[facing]
    pos = vessel.get("pos", [0, 0])
    vessel["pos"] = [pos[0] + dq, pos[1] + dr]


def _find_nearest_enemy(acting: dict, vessels: list[dict]) -> tuple:
    """Return (closest enemy vessel, hex distance) or (None, inf)."""
    side = acting.get("side")
    aq, ar = acting.get("pos", [0, 0])
    nearest: Optional[dict] = None
    min_dist: float = float("inf")

    for candidate in vessels:
        if candidate.get("side") == side:
            continue  # Same side — skip
        if candidate.get("hull", 0) <= _SUNK_THRESHOLD:
            continue  # Already sunk — skip
        cq, cr = candidate.get("pos", [0, 0])
        # Axial hex distance formula.
        dist = (abs(aq - cq) + abs(aq + ar - cq - cr) + abs(ar - cr)) / 2
        if dist < min_dist:
            min_dist = dist
            nearest = candidate

    return nearest, min_dist


def _apply_ram(attacker: dict, defender: dict, dist: float) -> None:
    """Apply simplified ram damage to the defender in the AI simulation.

    Only deals damage when the defender is adjacent (dist <= 1).
    """
    if dist > 1:
        return  # Out of range — no effect
    multiplier = attacker.get("ram_multiplier", 1.0)
    damage = int(_RAM_BASE_DAMAGE * multiplier)
    defender["hull"] = max(0, defender.get("hull", 0) - damage)
    # Disable oars on a successful ram hit (simplified — no angle calculation).
    if damage > 0:
        defender["oars"] = "Disabled"
