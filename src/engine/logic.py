import math

class GalleyEngine:
    def __init__(self, wind_dir=0, tide_dir=3):
        self.wind_dir = wind_dir  # 0-5
        self.tide_dir = tide_dir

    def get_move_cost(self, vessel, action):
        """Calculates MP cost based on wind and facing."""
        base_cost = 1
        # Heading into wind penalty
        if vessel['facing'] == (self.wind_dir + 3) % 6:
            base_cost += 1
        # Tail-wind bonus
        elif vessel['facing'] == self.wind_dir:
            base_cost = 0.5 
        return base_cost

    def resolve_ram(self, attacker, defender, angle):
        """Calculates damage based on GMT War Galley tables."""
        # Angle: 0=Head-on, 1=Flank, 2=Stern/Rake
        base_dmg = attacker['ram_multiplier'] * 20
        if angle == 2: # Rake
            return {"hull": base_dmg * 0.5, "oars": "Disabled"}
        return {"hull": base_dmg * (1.5 if angle == 1 else 1.0), "oars": "Intact"}