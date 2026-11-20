"""
Chaos Chess - Advanced Fantasy Piece Sprite Generator
Generates high-definition, 3D-shaded, tactical miniature piece sprites with rich lighting,
pedestals, weapons, and faction-specific energy fx.
"""
import math
import os
from PIL import Image, ImageDraw, ImageFilter

SIZE = 280
FINAL_SIZE = 140

def create_radial_gradient(size, inner_color, outer_color, center_ratio=(0.5, 0.5), radius_mult=0.5):
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    cx, cy = int(size[0] * center_ratio[0]), int(size[1] * center_ratio[1])
    max_r = int(min(size) * radius_mult)
    
    for r in range(max_r, 0, -2):
        factor = r / max_r
        # Interpolate RGBA
        col = tuple(int(inner_color[i] * (1 - factor) + outer_color[i] * factor) for i in range(4))
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)
    return img

def render_piece_sprite(team: str, piece_type: str, output_path: str):
    # Base canvas
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    cx, cy = SIZE // 2, SIZE // 2

    # Faction Palette
    if team == "red":
        theme_glow = (255, 40, 80, 160)
        theme_rim = (255, 120, 150, 240)
        theme_bright = (255, 60, 90, 255)
        armor_dark = (35, 15, 22, 255)
        armor_mid = (70, 25, 38, 255)
        armor_light = (130, 45, 65, 255)
        metal_shadow = (25, 18, 24, 255)
        metal_highlight = (245, 180, 195, 255)
        rune_glow = (255, 80, 110, 255)
        gold_trim = (245, 190, 60, 255)
        gem_color = (255, 20, 50, 255)
    else:
        theme_glow = (30, 180, 255, 160)
        theme_rim = (120, 220, 255, 240)
        theme_bright = (0, 200, 255, 255)
        armor_dark = (15, 25, 45, 255)
        armor_mid = (25, 45, 85, 255)
        armor_light = (45, 90, 160, 255)
        metal_shadow = (18, 22, 35, 255)
        metal_highlight = (180, 230, 255, 255)
        rune_glow = (60, 220, 255, 255)
        gold_trim = (255, 210, 70, 255)
        gem_color = (0, 240, 255, 255)

    # -------------------------------------------------------------
    # 1. GROUND SHADOW & AMBIENT PEDESTAL GLOW
    # -------------------------------------------------------------
    shadow_layer = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    s_draw = ImageDraw.Draw(shadow_layer)
    # Drop shadow below pedestal
    s_draw.ellipse([cx - 85, cy + 65, cx + 85, cy + 115], fill=(5, 8, 14, 180))
    # Soft ambient faction glow behind piece
    s_draw.ellipse([cx - 75, cy - 70, cx + 75, cy + 80], fill=theme_glow)
    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(radius=8))
    img.alpha_composite(shadow_layer)

    # -------------------------------------------------------------
    # 2. 3D TACTICAL PEDESTAL PLINTH
    # -------------------------------------------------------------
    ped_layer = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    p_draw = ImageDraw.Draw(ped_layer)

    base_y = cy + 78
    # Lower bevel base
    p_draw.ellipse([cx - 80, base_y - 18, cx + 80, base_y + 18], fill=armor_dark, outline=metal_shadow, width=3)
    p_draw.ellipse([cx - 74, base_y - 15, cx + 74, base_y + 15], fill=armor_mid)

    # Stepped upper plinth
    p_draw.ellipse([cx - 68, base_y - 24, cx + 68, base_y + 8], fill=metal_shadow)
    p_draw.ellipse([cx - 64, base_y - 23, cx + 64, base_y + 6], fill=armor_dark, outline=gold_trim, width=2)
    # Runic inlay ring
    p_draw.ellipse([cx - 56, base_y - 20, cx + 56, base_y + 3], fill=armor_mid, outline=rune_glow, width=2)

    # Tactical corner brackets (just like in the reference UI image!)
    bracket_col = theme_bright
    bw = 6
    # Left bracket
    p_draw.line([(cx - 78, base_y - 8), (cx - 86, base_y - 8), (cx - 86, base_y + 8), (cx - 78, base_y + 8)], fill=bracket_col, width=3)
    # Right bracket
    p_draw.line([(cx + 78, base_y - 8), (cx + 86, base_y - 8), (cx + 86, base_y + 8), (cx + 78, base_y + 8)], fill=bracket_col, width=3)
    # Top/Front marker
    p_draw.polygon([(cx - 6, base_y + 16), (cx + 6, base_y + 16), (cx, base_y + 24)], fill=gold_trim)

    img.alpha_composite(ped_layer)

    # -------------------------------------------------------------
    # 3. CHARACTER MINIATURE RENDERING
    # -------------------------------------------------------------
    char_layer = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    c_draw = ImageDraw.Draw(char_layer)

    if piece_type == "king":
        # =========================================================
        # KING: High Fantasy Armored Monarch with Regal Mantle & Sword
        # =========================================================
        # 1. Flowing Royal Cape (Mantle)
        cape_pts = [
            (cx - 55, cy + 68),
            (cx - 52, cy - 20),
            (cx - 36, cy - 35),
            (cx + 36, cy - 35),
            (cx + 52, cy - 20),
            (cx + 55, cy + 68),
            (cx + 35, cy + 60),
            (cx, cy + 65),
            (cx - 35, cy + 60)
        ]
        c_draw.polygon(cape_pts, fill=armor_dark, outline=theme_rim, width=2)
        # Cape inner velvet
        c_draw.polygon([(cx - 48, cy + 62), (cx - 34, cy - 25), (cx + 34, cy - 25), (cx + 48, cy + 62)], fill=armor_mid)

        # 2. Armored Body Cuirass
        body_pts = [
            (cx - 32, cy + 56),
            (cx - 28, cy - 15),
            (cx + 28, cy - 15),
            (cx + 32, cy + 56),
            (cx, cy + 62)
        ]
        c_draw.polygon(body_pts, fill=armor_light, outline=gold_trim, width=3)
        # Chest Lion Emblem
        c_draw.ellipse([cx - 14, cy, cx + 14, cy + 28], fill=gold_trim, outline=gem_color, width=2)
        c_draw.rectangle([cx - 3, cy + 6, cx + 3, cy + 22], fill=gem_color)
        c_draw.rectangle([cx - 9, cy + 11, cx + 9, cy + 17], fill=gem_color)

        # 3. Heavy Gilded Pauldrons (Shoulders)
        # Left Pauldron
        c_draw.polygon([(cx - 28, cy - 30), (cx - 56, cy - 20), (cx - 50, cy + 12), (cx - 24, cy - 5)], fill=armor_light, outline=gold_trim, width=3)
        c_draw.ellipse([cx - 52, cy - 16, cx - 36, cy + 2], fill=gold_trim)
        # Right Pauldron
        c_draw.polygon([(cx + 28, cy - 30), (cx + 56, cy - 20), (cx + 50, cy + 12), (cx + 24, cy - 5)], fill=armor_light, outline=gold_trim, width=3)
        c_draw.ellipse([cx + 36, cy - 16, cx + 52, cy + 2], fill=gold_trim)

        # 4. King's Holy Broadsword (planted vertically in front)
        blade_x = cx
        # Blade tip to hilt
        c_draw.polygon([(blade_x, cy + 64), (blade_x - 6, cy + 10), (blade_x + 6, cy + 10)], fill=(235, 240, 255), outline=metal_shadow, width=1)
        c_draw.line([(blade_x, cy + 10), (blade_x, cy + 60)], fill=rune_glow, width=2)
        # Crossguard
        c_draw.rectangle([blade_x - 22, cy + 8, blade_x + 22, cy + 14], fill=gold_trim, outline=metal_shadow, width=1)
        c_draw.ellipse([blade_x - 4, cy + 7, blade_x + 4, cy + 15], fill=gem_color)
        # Hilt & Pommel
        c_draw.rectangle([blade_x - 4, cy - 2, blade_x + 4, cy + 8], fill=metal_shadow)
        c_draw.ellipse([blade_x - 6, cy - 8, blade_x + 6, cy - 2], fill=gold_trim)

        # 5. Monarch Head & Beard/Visor
        c_draw.ellipse([cx - 18, cy - 42, cx + 18, cy - 10], fill=armor_dark, outline=gold_trim, width=2)
        # Glowing eye slit / visor
        c_draw.rectangle([cx - 10, cy - 28, cx + 10, cy - 23], fill=rune_glow)

        # 6. Radiant Crown of Kings
        crown_poly = [
            (cx - 28, cy - 32),
            (cx - 32, cy - 65),
            (cx - 18, cy - 48),
            (cx, cy - 74),       # High central spire
            (cx + 18, cy - 48),
            (cx + 32, cy - 65),
            (cx + 28, cy - 32)
        ]
        c_draw.polygon(crown_poly, fill=gold_trim, outline=metal_shadow, width=2)
        c_draw.rectangle([cx - 28, cy - 36, cx + 28, cy - 26], fill=gold_trim, outline=gem_color, width=2)
        # Crown Jewels
        for jx in [-20, 0, 20]:
            c_draw.ellipse([cx + jx - 4, cy - 34, cx + jx + 4, cy - 28], fill=gem_color)
        # Holy Cross finial atop king
        c_draw.rectangle([cx - 3, cy - 88, cx + 3, cy - 72], fill=gold_trim)
        c_draw.rectangle([cx - 10, cy - 83, cx + 10, cy - 77], fill=gold_trim)
        c_draw.ellipse([cx - 4, cy - 82, cx + 4, cy - 78], fill=rune_glow)

    elif piece_type == "queen":
        # =========================================================
        # QUEEN: Majestic Battle Empress & Arcane Sorceress
        # =========================================================
        # 1. Flowing Ethereal Cloak & Wings
        c_draw.polygon([(cx - 52, cy + 68), (cx - 48, cy - 15), (cx + 48, cy - 15), (cx + 52, cy + 68)], fill=armor_dark, outline=theme_rim, width=2)
        # Winged Pauldrons
        c_draw.polygon([(cx - 26, cy - 26), (cx - 58, cy - 38), (cx - 44, cy + 6), (cx - 22, cy - 2)], fill=armor_light, outline=gold_trim, width=2)
        c_draw.polygon([(cx + 26, cy - 26), (cx + 58, cy - 38), (cx + 44, cy + 6), (cx + 22, cy - 2)], fill=armor_light, outline=gold_trim, width=2)

        # 2. Corset & Gilded Gown
        c_draw.polygon([(cx - 24, cy - 12), (cx + 24, cy - 12), (cx + 34, cy + 64), (cx - 34, cy + 64)], fill=armor_mid, outline=gold_trim, width=3)
        # Arcane Heart Sigil
        c_draw.polygon([(cx, cy + 4), (cx + 12, cy + 18), (cx, cy + 32), (cx - 12, cy + 18)], fill=rune_glow, outline=gold_trim, width=2)

        # 3. Head & Mask/Visor
        c_draw.ellipse([cx - 16, cy - 42, cx + 16, cy - 14], fill=armor_dark, outline=gold_trim, width=2)
        c_draw.line([(cx - 9, cy - 26), (cx + 9, cy - 26)], fill=rune_glow, width=3)

        # 4. Radiant Multi-Point Diadem Tiara
        tiara_poly = [
            (cx - 24, cy - 34),
            (cx - 28, cy - 62),
            (cx - 14, cy - 48),
            (cx, cy - 72),
            (cx + 14, cy - 48),
            (cx + 28, cy - 62),
            (cx + 24, cy - 34)
        ]
        c_draw.polygon(tiara_poly, fill=gold_trim, outline=metal_shadow, width=2)
        c_draw.ellipse([cx - 6, cy - 58, cx + 6, cy - 46], fill=gem_color, outline=gold_trim, width=2)

        # 5. Arcane Scepter (Held on right side with orbiting magic orb)
        scep_x = cx + 42
        c_draw.line([(scep_x, cy + 62), (scep_x, cy - 45)], fill=gold_trim, width=4)
        # Scepter Head
        c_draw.ellipse([scep_x - 14, cy - 64, scep_x + 14, cy - 36], fill=armor_mid, outline=gold_trim, width=2)
        # Glowing Arcane Floating Core
        c_draw.ellipse([scep_x - 9, cy - 58, scep_x + 9, cy - 42], fill=rune_glow)
        c_draw.ellipse([scep_x - 4, cy - 53, scep_x + 4, cy - 47], fill=(255, 255, 255))
        # Orbital energy rings
        c_draw.ellipse([scep_x - 18, cy - 55, scep_x + 18, cy - 45], fill=None, outline=theme_bright, width=2)

    elif piece_type == "rook":
        # =========================================================
        # ROOK: Fortified Citadel Golem & Heavy Tower Shield
        # =========================================================
        # 1. Colossal Stone & Iron Torso
        c_draw.polygon([(cx - 44, cy + 65), (cx - 40, cy - 20), (cx + 40, cy - 20), (cx + 44, cy + 65)], fill=armor_dark, outline=gold_trim, width=3)
        # Stone brick inlays
        c_draw.rectangle([cx - 30, cy + 10, cx + 30, cy + 45], fill=armor_mid, outline=metal_shadow, width=2)
        c_draw.line([(cx, cy + 10), (cx, cy + 45)], fill=metal_shadow, width=2)

        # 2. Castle Battlement Turrets (Crenellations) atop shoulders
        c_draw.rectangle([cx - 44, cy - 42, cx + 44, cy - 18], fill=armor_light, outline=gold_trim, width=2)
        # Embrasures (Castle gaps)
        for gx in [-32, -8, 16]:
            c_draw.rectangle([cx + gx, cy - 44, cx + gx + 16, cy - 30], fill=armor_dark, outline=gold_trim, width=2)

        # 3. Heavy Iron Golem Visor
        c_draw.rounded_rectangle([cx - 22, cy - 16, cx + 22, cy + 2], radius=4, fill=metal_shadow, outline=gold_trim, width=2)
        c_draw.rectangle([cx - 14, cy - 9, cx + 14, cy - 5], fill=rune_glow)

        # 4. Colossal Tower Shield (Held on left)
        sh_pts = [
            (cx - 65, cy - 30),
            (cx - 32, cy - 30),
            (cx - 32, cy + 45),
            (cx - 48, cy + 66),
            (cx - 65, cy + 45)
        ]
        c_draw.polygon(sh_pts, fill=armor_light, outline=gold_trim, width=3)
        c_draw.rectangle([cx - 56, cy - 15, cx - 40, cy + 30], fill=armor_dark)
        c_draw.line([(cx - 48, cy - 24), (cx - 48, cy + 50)], fill=rune_glow, width=3)

        # 5. Heavy Spiked War Hammer (Right hand)
        hm_x = cx + 50
        c_draw.line([(hm_x - 10, cy + 62), (hm_x, cy - 25)], fill=gold_trim, width=4)
        c_draw.rectangle([hm_x - 12, cy - 36, hm_x + 18, cy - 18], fill=armor_light, outline=metal_shadow, width=2)
        c_draw.polygon([(hm_x + 18, cy - 32), (hm_x + 28, cy - 27), (hm_x + 18, cy - 22)], fill=gold_trim)

    elif piece_type == "bishop":
        # =========================================================
        # BISHOP: Mystic Inquisitor / High Battle Mage
        # =========================================================
        # 1. Flowing Mystical Cowl & Cleric Robes
        c_draw.polygon([(cx - 40, cy + 66), (cx - 32, cy - 10), (cx + 32, cy - 10), (cx + 40, cy + 66)], fill=armor_dark, outline=theme_rim, width=2)
        # Sacred Cleric Stole
        c_draw.polygon([(cx - 16, cy - 8), (cx - 12, cy + 66), (cx + 12, cy + 66), (cx + 16, cy - 8)], fill=armor_mid, outline=gold_trim, width=2)
        for ry in [cy + 10, cy + 32, cy + 52]:
            c_draw.rectangle([cx - 8, ry - 3, cx + 8, ry + 3], fill=rune_glow)

        # 2. Deep Mystical Hood with Shadowed Face
        c_draw.polygon([(cx, cy - 58), (cx + 26, cy - 20), (cx - 26, cy - 20)], fill=armor_dark, outline=gold_trim, width=2)
        # Piercing Glowing Eyes in the Darkness
        c_draw.ellipse([cx - 12, cy - 30, cx - 4, cy - 24], fill=rune_glow)
        c_draw.ellipse([cx + 4, cy - 30, cx + 12, cy - 24], fill=rune_glow)

        # 3. Gilded Mitre Finial
        mitre_pts = [
            (cx, cy - 76),
            (cx + 20, cy - 42),
            (cx - 20, cy - 42)
        ]
        c_draw.polygon(mitre_pts, fill=armor_light, outline=gold_trim, width=2)
        # Sacred Slit Cross
        c_draw.rectangle([cx - 2, cy - 65, cx + 2, cy - 48], fill=gold_trim)
        c_draw.rectangle([cx - 8, cy - 58, cx + 8, cy - 54], fill=gold_trim)
        c_draw.ellipse([cx - 4, cy - 82, cx + 4, cy - 74], fill=gem_color, outline=gold_trim, width=1)

        # 4. Pastoral Bishop Crosier Staff (Left Hand)
        cros_x = cx - 45
        c_draw.line([(cros_x, cy + 65), (cros_x, cy - 40)], fill=gold_trim, width=4)
        # Curved Shepherd's Crook
        c_draw.arc([cros_x - 18, cy - 66, cros_x + 18, cy - 30], start=180, end=360, fill=gold_trim, width=5)
        c_draw.ellipse([cros_x - 4, cy - 55, cros_x + 4, cy - 47], fill=gem_color)

        # 5. Levitating Spell Tome (Right Hand)
        tm_x, tm_y = cx + 42, cy + 15
        c_draw.polygon([(tm_x - 18, tm_y - 12), (tm_x, tm_y - 4), (tm_x + 18, tm_y - 12), (tm_x + 18, tm_y + 16), (tm_x, tm_y + 24), (tm_x - 18, tm_y + 16)], fill=armor_light, outline=gold_trim, width=2)
        c_draw.ellipse([tm_x - 8, tm_y, tm_x + 8, tm_y + 12], fill=rune_glow)

    elif piece_type == "knight":
        # =========================================================
        # KNIGHT: Armored Champion Warhorse & Dragon Steed
        # =========================================================
        # 1. Armored Torso / Caparison
        c_draw.polygon([(cx - 36, cy + 66), (cx - 28, cy + 18), (cx + 36, cy + 18), (cx + 42, cy + 66)], fill=armor_dark, outline=gold_trim, width=3)
        c_draw.ellipse([cx - 15, cy + 28, cx + 20, cy + 54], fill=armor_mid, outline=rune_glow, width=2)

        # 2. Sleek Rearing Armored Horse Head
        steed_pts = [
            (cx - 32, cy + 24),
            (cx - 26, cy - 10),
            (cx - 36, cy - 28),
            (cx - 24, cy - 52),  # Ear tip
            (cx - 8, cy - 40),
            (cx + 8, cy - 58),   # Plumed crest top
            (cx + 26, cy - 42),
            (cx + 42, cy - 18),  # Armored Muzzle
            (cx + 30, cy + 4),   # Chin
            (cx + 18, cy + 12),  # Throat
            (cx + 24, cy + 32)
        ]
        c_draw.polygon(steed_pts, fill=armor_light, outline=gold_trim, width=3)

        # Chamfron (Steed faceplate armor)
        c_draw.polygon([(cx - 12, cy - 35), (cx + 18, cy - 40), (cx + 34, cy - 18), (cx + 6, cy - 12)], fill=armor_dark, outline=gold_trim, width=2)
        # Fiery/Icy Visor Eye
        c_draw.ellipse([cx + 10, cy - 30, cx + 22, cy - 20], fill=gem_color, outline=rune_glow, width=2)

        # 3. Crested Mane / Knight Plume
        plume_pts = [
            (cx - 12, cy - 48),
            (cx - 2, cy - 74),
            (cx + 10, cy - 56),
            (cx + 20, cy - 68),
            (cx + 24, cy - 44)
        ]
        c_draw.polygon(plume_pts, fill=theme_bright, outline=gold_trim, width=2)

        # 4. Crossed Heavy Cavalry Jousting Lance
        c_draw.line([(cx - 56, cy + 60), (cx + 56, cy - 65)], fill=gold_trim, width=4)
        # Lance Vamplate (Hand guard)
        c_draw.polygon([(cx - 18, cy + 26), (cx - 2, cy + 12), (cx - 10, cy + 4)], fill=armor_dark, outline=gold_trim, width=2)
        # Steel Lance Tip
        c_draw.polygon([(cx + 54, cy - 62), (cx + 68, cy - 78), (cx + 44, cy - 70)], fill=(240, 245, 255), outline=metal_shadow, width=1)

    elif piece_type == "pawn":
        # =========================================================
        # PAWN: Resolute Vanguard Warrior / Legionary Foot Soldier
        # =========================================================
        # 1. Chainmail & Leather Cuirass
        c_draw.polygon([(cx - 30, cy + 66), (cx - 22, cy + 5), (cx + 22, cy + 5), (cx + 30, cy + 66)], fill=armor_dark, outline=theme_rim, width=2)
        # Crossed chest harness straps
        c_draw.line([(cx - 20, cy + 10), (cx + 20, cy + 55)], fill=gold_trim, width=3)
        c_draw.line([(cx + 20, cy + 10), (cx - 20, cy + 55)], fill=gold_trim, width=3)

        # 2. Vanguard Spiked Heater Shield (Left hand)
        sh_pts = [
            (cx - 50, cy - 5),
            (cx - 16, cy - 5),
            (cx - 16, cy + 42),
            (cx - 33, cy + 65),
            (cx - 50, cy + 42)
        ]
        c_draw.polygon(sh_pts, fill=armor_light, outline=gold_trim, width=3)
        # Faction crest on shield
        c_draw.ellipse([cx - 40, cy + 12, cx - 26, cy + 34], fill=gem_color, outline=rune_glow, width=2)
        c_draw.polygon([(cx - 33, cy + 8), (cx - 28, cy + 22), (cx - 38, cy + 22)], fill=gold_trim)

        # 3. Broadsword (Right hand)
        c_draw.line([(cx + 36, cy + 62), (cx + 36, cy - 25)], fill=(235, 240, 255), width=4)
        c_draw.line([(cx + 36, cy - 25), (cx + 36, cy + 30)], fill=rune_glow, width=2)
        # Crossguard
        c_draw.rectangle([cx + 24, cy + 26, cx + 48, cy + 32], fill=gold_trim)

        # 4. Legionnaire Battle Helm
        c_draw.ellipse([cx - 18, cy - 35, cx + 18, cy - 4], fill=armor_light, outline=gold_trim, width=2)
        # Nasal Bar & T-Visor
        c_draw.rectangle([cx - 12, cy - 24, cx + 12, cy - 18], fill=rune_glow)
        c_draw.rectangle([cx - 3, cy - 24, cx + 3, cy - 10], fill=gold_trim)
        # Spiked Helm Finial / Crest
        c_draw.polygon([(cx - 14, cy - 33), (cx, cy - 54), (cx + 14, cy - 33)], fill=theme_bright, outline=gold_trim, width=2)
        c_draw.ellipse([cx - 4, cy - 58, cx + 4, cy - 50], fill=gem_color)

    # -------------------------------------------------------------
    # 4. VOLUMETRIC RIM LIGHT & SPECULAR SHINE
    # -------------------------------------------------------------
    # Rim light pass
    rim_layer = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    r_draw = ImageDraw.Draw(rim_layer)
    # Highlight top-left specular edges
    r_draw.ellipse([cx - 22, cy - 45, cx - 12, cy - 35], fill=(255, 255, 255, 140))
    rim_layer = rim_layer.filter(ImageFilter.GaussianBlur(radius=1))
    char_layer.alpha_composite(rim_layer)

    img.alpha_composite(char_layer)

    # Downsample cleanly with Lanczos anti-aliasing
    final_img = img.resize((FINAL_SIZE, FINAL_SIZE), resample=Image.Resampling.LANCZOS)
    final_img.save(output_path, "PNG")

def generate_all():
    out_dir = "assets/images/pieces"
    os.makedirs(out_dir, exist_ok=True)
    for team in ["red", "blue"]:
        for p_type in ["king", "queen", "rook", "bishop", "knight", "pawn"]:
            path = os.path.join(out_dir, f"{team}_{p_type}.png")
            render_piece_sprite(team, p_type, path)
            print(f"Rendered: {team}_{p_type}")

if __name__ == "__main__":
    generate_all()

