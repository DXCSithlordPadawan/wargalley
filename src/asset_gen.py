import os
from PIL import Image, ImageDraw

# Project Directory Structure
ASSET_PATH = "assets/"
if not os.path.exists(ASSET_PATH):
    os.makedirs(ASSET_PATH)

def create_galley_sprite(name, color, size=(128, 64)):
    """Generates a top-down wooden galley with faction-colored oars."""
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 1. Hull (Dark Wood)
    hull_shape = [(10, 32), (30, 10), (100, 10), (118, 32), (100, 54), (30, 54)]
    draw.polygon(hull_shape, fill=(101, 67, 33), outline=(60, 40, 20))

    # 2. Faction Deck/Banner
    draw.rectangle([40, 20, 90, 44], fill=color, outline=(0, 0, 0))

    # 3. Oars (Procedural lines)
    for x in range(35, 95, 8):
        # Left Oars
        draw.line([(x, 10), (x - 5, 2)], fill=(200, 200, 200), width=2)
        # Right Oars
        draw.line([(x, 54), (x - 5, 62)], fill=(200, 200, 200), width=2)

    # 4. Ram (Bronze)
    draw.polygon([(118, 32), (126, 28), (126, 36)], fill=(205, 127, 50))

    img.save(f"{ASSET_PATH}{name}.png")
    print(f"Generated: {ASSET_PATH}{name}.png")

def create_terrain_hex(name, color):
    """Generates 128x128 hex tiles for islands or reefs."""
    img = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Hexagon Math
    points = [
        (64, 0), (128, 32), (128, 96), (64, 128), (0, 96), (0, 32)
    ]
    draw.polygon(points, fill=color, outline=(0, 0, 0))
    img.save(f"{ASSET_PATH}{name}.png")
    print(f"Generated: {ASSET_PATH}{name}.png")

if __name__ == "__main__":
    # Generate Faction Fleets
    create_galley_sprite("rome_trireme", (139, 0, 0))      # Roman Crimson
    create_galley_sprite("carthage_trireme", (218, 165, 32)) # Punic Gold
    create_galley_sprite("successor_deceres", (75, 0, 130))  # Hellenistic Purple
    
    # Generate Terrain
    create_terrain_hex("hex_island", (194, 178, 128))      # Sand/Rock
    create_terrain_hex("hex_sea", (0, 105, 148))           # Deep Water
    
    print("\n--- Visual Assets Commissioned ---")