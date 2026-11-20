"""
Chaos Chess - Unmistakable Iconic Chess Piece Generator
Generates bold, highly recognizable tactical chess piece sprites with unmistakable silhouettes,
3D volumetric lighting, and clear faction & letter crest badges.
"""
import math
import os
from PIL import Image, ImageDraw, ImageFilter

SIZE = 300
FINAL_SIZE = 150

def draw_letter(draw: ImageDraw.Draw, letter: str, cx: int, cy: int, size: int, col: tuple, width: int = 4):
    """Draws clean, bold procedural vector letters for piece badge identification."""
    h = size
    w = int(size * 0.72)
    x1 = cx - w // 2
    x2 = cx + w // 2
    y1 = cy - h // 2
    y2 = cy + h // 2
    ym = cy

    if letter == "K":
        draw.line([(x1, y1), (x1, y2)], fill=col, width=width)
        draw.line([(x2, y1), (x1, ym)], fill=col, width=width)
        draw.line([(x1, ym), (x2, y2)], fill=col, width=width)
    elif letter == "Q":
        draw.ellipse([x1, y1, x2, y2], outline=col, width=width)
        draw.line([(cx, ym + 2), (x2 + 4, y2 + 4)], fill=col, width=width + 1)
    elif letter == "R":
        draw.line([(x1, y1), (x1, y2)], fill=col, width=width)
        draw.arc([x1 - 2, y1, x2 + 2, ym + 2], start=270, end=90, fill=col, width=width)
        draw.line([(x1, y1), (cx, y1)], fill=col, width=width)
        draw.line([(x1, ym), (cx, ym)], fill=col, width=width)
        draw.line([(cx, ym), (x2, y2)], fill=col, width=width)
    elif letter == "B":
        draw.line([(x1, y1), (x1, y2)], fill=col, width=width)
        draw.arc([x1 - 2, y1, x2, ym + 1], start=270, end=90, fill=col, width=width)
        draw.arc([x1 - 2, ym - 1, x2 + 2, y2], start=270, end=90, fill=col, width=width)
        draw.line([(x1, y1), (cx - 2, y1)], fill=col, width=width)
        draw.line([(x1, ym), (cx - 2, ym)], fill=col, width=width)
        draw.line([(x1, y2), (cx - 2, y2)], fill=col, width=width)
    elif letter == "N":
        draw.line([(x1, y1), (x1, y2)], fill=col, width=width)
        draw.line([(x1, y1), (x2, y2)], fill=col, width=width)
        draw.line([(x2, y1), (x2, y2)], fill=col, width=width)
    elif letter == "P":
        draw.line([(x1, y1), (x1, y2)], fill=col, width=width)
        draw.arc([x1 - 2, y1, x2 + 2, ym + 2], start=270, end=90, fill=col, width=width)
        draw.line([(x1, y1), (cx, y1)], fill=col, width=width)
        draw.line([(x1, ym), (cx, ym)], fill=col, width=width)


def render_recognizable_piece(team: str, piece_type: str, output_path: str):
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    cx = SIZE // 2

    # High-contrast, vibrant tactical palettes
    if team == "red":
        glow_color = (255, 30, 70, 180)
        core_primary = (225, 30, 55, 255)
        core_shadow = (120, 10, 25, 255)
        core_highlight = (255, 120, 140, 255)
        gold_trim = (255, 215, 60, 255)
        gold_shadow = (180, 130, 20, 255)
        letter_color = (255, 240, 180, 255)
        outline_color = (255, 235, 160, 255)
        badge_bg = (50, 12, 20, 255)
    else:
        glow_color = (0, 190, 255, 180)
        core_primary = (15, 140, 245, 255)
        core_shadow = (8, 60, 140, 255)
        core_highlight = (140, 225, 255, 255)
        gold_trim = (255, 215, 60, 255)
        gold_shadow = (180, 130, 20, 255)
        letter_color = (210, 245, 255, 255)
        outline_color = (200, 240, 255, 255)
        badge_bg = (10, 25, 55, 255)

    # 1. Outer Atmospheric Silhouette Glow
    glow_layer = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    g_draw = ImageDraw.Draw(glow_layer)
    g_draw.ellipse([cx - 75, 40, cx + 75, 250], fill=glow_color)
    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(radius=10))
    img.alpha_composite(glow_layer)

    # 2. Main Silhouette Drawing Canvas
    char_layer = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(char_layer)

    letter_code = piece_type[0].upper()
    if piece_type == "knight":
        letter_code = "N"

    # =========================================================================
    # PIECE SILHOUETTES
    # =========================================================================
    if piece_type == "king":
        # 👑 KING: Large Regal Imperial Arched Crown with prominent Golden Cross
        base_top = 228
        # Shoulders / Royal Robe
        robe_poly = [
            (cx - 56, base_top),
            (cx - 52, 142),
            (cx - 30, 128),
            (cx + 30, 128),
            (cx + 52, 142),
            (cx + 56, base_top)
        ]
        draw.polygon(robe_poly, fill=core_primary, outline=outline_color, width=4)
        # Gold collar ermine trim
        draw.polygon([(cx - 30, 128), (cx + 30, 128), (cx, 168)], fill=gold_trim, outline=gold_shadow, width=2)

        # Crown Headband
        draw.rounded_rectangle([cx - 52, 108, cx + 52, 132], radius=4, fill=gold_trim, outline=outline_color, width=3)
        for gx in [-34, -17, 0, 17, 34]:
            draw.ellipse([cx + gx - 4, 114, cx + gx + 4, 124], fill=core_shadow)

        # Arched Crown Domes & Spikes
        crown_pts = [
            (cx - 50, 108),
            (cx - 46, 68),   # Left outer spike
            (cx - 28, 86),
            (cx, 60),        # Center apex
            (cx + 28, 86),
            (cx + 46, 68),   # Right outer spike
            (cx + 50, 108)
        ]
        draw.polygon(crown_pts, fill=core_primary, outline=outline_color, width=4)
        # Crown arched ribs
        draw.arc([cx - 44, 60, cx, 115], start=180, end=360, fill=gold_trim, width=3)
        draw.arc([cx, 60, cx + 44, 115], start=180, end=360, fill=gold_trim, width=3)

        # Golden Cross on King's Crown (Massive and bold!)
        cross_y = 48
        draw.rectangle([cx - 6, cross_y - 24, cx + 6, cross_y + 14], fill=gold_trim, outline=outline_color, width=2)
        draw.rectangle([cx - 20, cross_y - 12, cx + 20, cross_y], fill=gold_trim, outline=outline_color, width=2)
        draw.ellipse([cx - 4, cross_y - 8, cx + 4, cross_y], fill=(255, 255, 255))

    elif piece_type == "queen":
        # 👸 QUEEN: Flared 5-Spike Coronet with Pearls on each tip
        base_top = 228
        # Hourglass dress
        dress_pts = [
            (cx - 50, base_top),
            (cx - 44, 175),
            (cx - 24, 142),
            (cx + 24, 142),
            (cx + 44, 175),
            (cx + 50, base_top)
        ]
        draw.polygon(dress_pts, fill=core_primary, outline=outline_color, width=4)
        # Gold Corset
        draw.polygon([(cx - 24, 142), (cx + 24, 142), (cx + 18, 185), (cx - 18, 185)], fill=gold_trim, outline=gold_shadow, width=2)

        # Coronet Base Band
        draw.rounded_rectangle([cx - 44, 126, cx + 44, 144], radius=3, fill=gold_trim, outline=outline_color, width=2)

        # 5 Flared Coronet Spikes
        tiara_poly = [
            (cx - 44, 126),
            (cx - 46, 78),   # Spike 1
            (cx - 24, 98),
            (cx - 20, 62),   # Spike 2
            (cx, 90),
            (cx, 44),        # Center Spike 3
            (cx, 90),
            (cx + 20, 62),   # Spike 4
            (cx + 24, 98),
            (cx + 46, 78),   # Spike 5
            (cx + 44, 126)
        ]
        draw.polygon(tiara_poly, fill=core_primary, outline=outline_color, width=4)

        # 5 Radiant Circular Pearls on tips
        pearl_coords = [
            (cx - 46, 76, 7),
            (cx - 20, 60, 8),
            (cx, 42, 10),
            (cx + 20, 60, 8),
            (cx + 46, 76, 7)
        ]
        for px, py, pr in pearl_coords:
            draw.ellipse([px - pr, py - pr, px + pr, py + pr], fill=gold_trim, outline=outline_color, width=2)
            draw.ellipse([px - pr//2, py - pr//2, px, py], fill=(255, 255, 255))

    elif piece_type == "rook":
        # 🏰 ROOK: Fortified Medieval Castle Tower with 4 Square Crenellations
        base_top = 228
        # Straight vertical walls
        tower_rect = [cx - 44, 98, cx + 44, base_top]
        draw.rectangle(tower_rect, fill=core_primary, outline=outline_color, width=4)

        # Horizontal Stone Brick Lines
        for by in [130, 160, 190]:
            draw.line([(cx - 42, by), (cx + 42, by)], fill=core_shadow, width=2)
        draw.line([(cx - 15, 100), (cx - 15, 130)], fill=core_shadow, width=2)
        draw.line([(cx + 15, 100), (cx + 15, 130)], fill=core_shadow, width=2)
        draw.line([(cx, 130), (cx, 160)], fill=core_shadow, width=2)
        draw.line([(cx - 22, 160), (cx - 22, 190)], fill=core_shadow, width=2)
        draw.line([(cx + 22, 160), (cx + 22, 190)], fill=core_shadow, width=2)

        # Central Arrow Slit Window
        draw.rounded_rectangle([cx - 5, 138, cx + 5, 172], radius=3, fill=gold_trim, outline=core_shadow, width=2)

        # Arched Castle Gate / Portcullis at Base
        draw.rounded_rectangle([cx - 18, 194, cx + 18, base_top], radius=6, fill=core_shadow, outline=gold_trim, width=3)
        draw.line([(cx - 8, 196), (cx - 8, base_top)], fill=gold_trim, width=2)
        draw.line([(cx + 8, 196), (cx + 8, base_top)], fill=gold_trim, width=2)

        # Cornice Rim below battlements
        draw.rounded_rectangle([cx - 50, 86, cx + 50, 100], radius=3, fill=gold_trim, outline=outline_color, width=3)

        # 4 Prominent Square Battlements / Crenellations
        # Left tooth
        draw.rectangle([cx - 48, 54, cx - 26, 86], fill=core_primary, outline=outline_color, width=3)
        # Center gap: [cx - 26 to cx - 14] is open
        # Center tooth 1
        draw.rectangle([cx - 14, 54, cx + 14, 86], fill=core_primary, outline=outline_color, width=3)
        # Center gap: [cx + 14 to cx + 26] is open
        # Right tooth
        draw.rectangle([cx + 26, 54, cx + 48, 86], fill=core_primary, outline=outline_color, width=3)

    elif piece_type == "bishop":
        # 🧙 BISHOP: Iconic Mitre with deep diagonal cross cut & top ball
        base_top = 228
        # Vestment Body
        body_poly = [
            (cx - 44, base_top),
            (cx - 36, 175),
            (cx - 18, 155),
            (cx + 18, 155),
            (cx + 36, 175),
            (cx + 44, base_top)
        ]
        draw.polygon(body_poly, fill=core_primary, outline=outline_color, width=4)

        # Collar Ring
        draw.rounded_rectangle([cx - 28, 152, cx + 28, 166], radius=3, fill=gold_trim, outline=outline_color, width=2)

        # Pointed Oval Mitre Hat
        mitre_poly = [
            (cx, 62),          # Mitre point
            (cx + 40, 115),
            (cx + 36, 154),
            (cx - 36, 154),
            (cx - 40, 115)
        ]
        draw.polygon(mitre_poly, fill=core_primary, outline=outline_color, width=4)

        # Iconic Diagonal Cleft / Slit
        draw.line([(cx + 10, 80), (cx - 26, 138)], fill=core_shadow, width=5)
        draw.line([(cx + 10, 80), (cx - 26, 138)], fill=(25, 10, 18), width=3)

        # Sacred Gold Cross on front
        cross_cx = cx + 8
        cross_cy = 120
        draw.rectangle([cross_cx - 4, cross_cy - 16, cross_cx + 4, cross_cy + 16], fill=gold_trim, outline=outline_color, width=1)
        draw.rectangle([cross_cx - 12, cross_cy - 6, cross_cx + 12, cross_cy + 4], fill=gold_trim, outline=outline_color, width=1)

        # Top Round Finial Pearl
        draw.ellipse([cx - 9, 46, cx + 9, 64], fill=gold_trim, outline=outline_color, width=2)
        draw.ellipse([cx - 4, 49, cx + 1, 54], fill=(255, 255, 255))

    elif piece_type == "knight":
        # ♞ KNIGHT: Iconic Rearing Horse / Steed Head Profile
        base_top = 228
        horse_poly = [
            (cx - 40, base_top),
            (cx - 48, 185),
            (cx - 56, 145),   # Back of neck
            (cx - 42, 95),
            (cx - 24, 60),    # Left ear
            (cx - 16, 78),
            (cx - 6, 62),     # Right ear
            (cx + 8, 76),
            (cx + 32, 94),    # Forehead
            (cx + 58, 122),   # Muzzle / Snout
            (cx + 56, 136),   # Lower jaw
            (cx + 38, 142),   # Chin
            (cx + 26, 158),   # Throat
            (cx + 38, 185),   # Chest
            (cx + 42, base_top)
        ]
        draw.polygon(horse_poly, fill=core_primary, outline=outline_color, width=4)

        # Mane Scallops
        for my in [95, 125, 155, 185]:
            draw.polygon([(cx - 40, my), (cx - 58, my + 15), (cx - 46, my + 30)], fill=gold_trim, outline=gold_shadow, width=2)

        # Horse Armored Bridle & Collar
        draw.line([(cx + 32, 94), (cx + 38, 142)], fill=gold_trim, width=3)
        draw.line([(cx - 10, 115), (cx + 50, 130)], fill=gold_trim, width=3)

        # Glowing Eye
        draw.ellipse([cx + 12, 100, cx + 24, 114], fill=gold_trim, outline=outline_color, width=2)
        draw.ellipse([cx + 15, 103, cx + 21, 109], fill=(255, 255, 255))

        # Nostril
        draw.ellipse([cx + 46, 124, cx + 52, 132], fill=core_shadow)

    elif piece_type == "pawn":
        # ♟ PAWN: Classic Spherical Head, Collar Ring, Conical Body (Compact height!)
        base_top = 228
        # Conical Body (starts lower than officers for instant height recognition!)
        body_pts = [
            (cx - 42, base_top),
            (cx - 22, 148),
            (cx + 22, 148),
            (cx + 42, base_top)
        ]
        draw.polygon(body_pts, fill=core_primary, outline=outline_color, width=4)

        # Center Crest Stud
        draw.ellipse([cx - 10, 172, cx + 10, 192], fill=gold_trim, outline=outline_color, width=2)

        # Neck Collar Disc
        draw.rounded_rectangle([cx - 30, 138, cx + 30, 152], radius=4, fill=gold_trim, outline=outline_color, width=2)

        # Big Spherical Head (Pure chess pawn sphere!)
        head_radius = 28
        head_cy = 112
        draw.ellipse(
            [cx - head_radius, head_cy - head_radius, cx + head_radius, head_cy + head_radius],
            fill=core_primary, outline=outline_color, width=4
        )
        # Specular 3D ball glint
        draw.ellipse([cx - 14, head_cy - 18, cx - 2, head_cy - 6], fill=(255, 255, 255, 220))

    # =========================================================================
    # 3. 3D PEDESTAL BASE & UNMISTAKABLE LETTER BADGE
    # =========================================================================
    # Pedestal rim
    draw.rounded_rectangle([cx - 62, 224, cx + 62, 244], radius=6, fill=gold_trim, outline=gold_shadow, width=3)
    draw.ellipse([cx - 68, 235, cx + 68, 268], fill=badge_bg, outline=gold_trim, width=3)

    # Glowing Circular Center Badge
    badge_r = 18
    badge_cy = 250
    draw.ellipse([cx - badge_r, badge_cy - badge_r, cx + badge_r, badge_cy + badge_r], fill=badge_bg, outline=gold_trim, width=2)

    # Draw the Bold Letter: K, Q, R, B, N, P
    draw_letter(draw, letter_code, cx, badge_cy, size=18, col=letter_color, width=3)

    # 4. Composite and Scale
    img.alpha_composite(char_layer)
    final_img = img.resize((FINAL_SIZE, FINAL_SIZE), resample=Image.Resampling.LANCZOS)
    final_img.save(output_path, "PNG")

def generate_all():
    out_dir = "assets/images/pieces"
    os.makedirs(out_dir, exist_ok=True)
    for team in ["red", "blue"]:
        for p_type in ["king", "queen", "rook", "bishop", "knight", "pawn"]:
            path = os.path.join(out_dir, f"{team}_{p_type}.png")
            render_recognizable_piece(team, p_type, path)
            print(f"Generated unmistakable: {team}_{p_type}.png")

if __name__ == "__main__":
    generate_all()

