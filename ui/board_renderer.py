"""
Chaos Chess - 7x4 Board Renderer & Animation System
"""
import math
import os
import pygame
from typing import Optional, Tuple, List, Dict
from config import (
    ROWS, COLS,
    KING, QUEEN, ROOK, BISHOP, KNIGHT, PAWN,
    TEAM_RED, TEAM_BLUE,
    COLOR_TILE_LIGHT, COLOR_TILE_DARK, COLOR_TILE_BORDER, COLOR_TILE_RUNE,
    COLOR_HIGHLIGHT_SELECT, COLOR_HIGHLIGHT_MOVE, COLOR_HIGHLIGHT_ATTACK,
    COLOR_HIGHLIGHT_ABILITY, COLOR_HIGHLIGHT_LAST_MOVE,
    COLOR_RED_PRIMARY, COLOR_BLUE_PRIMARY,
    EVENT_THUNDERSTORM, EVENT_FROZEN_GROUND, EVENT_HEALING_ZONE,
    EVENT_FOG_OF_WAR, EVENT_EARTHQUAKE,
    ASSETS_DIR
)
from game.board import Board
from game.piece import Piece
from game.movement import Move


class PieceAnimation:
    """Handles smooth interpolation for pieces sliding between squares."""
    def __init__(self, piece: Piece, start_px: Tuple[int, int], end_px: Tuple[int, int], duration: float = 0.22):
        self.piece = piece
        self.start_px = start_px
        self.end_px = end_px
        self.duration = duration
        self.elapsed = 0.0
        self.is_finished = False

    def update(self, dt: float) -> Tuple[int, int]:
        self.elapsed += dt
        t = min(1.0, self.elapsed / self.duration)
        # Smooth ease-in-out curve
        t_smooth = t * t * (3.0 - 2.0 * t)
        cx = int(self.start_px[0] + (self.end_px[0] - self.start_px[0]) * t_smooth)
        cy = int(self.start_px[1] + (self.end_px[1] - self.start_px[1]) * t_smooth)
        if t >= 1.0:
            self.is_finished = True
        return (cx, cy)


class BoardRenderer:
    """Renders the 7x4 tactical arena with highlights, atmospheric effects, and animations."""

    def __init__(self, origin_x: int, origin_y: int, tile_size: int = 86):
        self.origin_x = origin_x
        self.origin_y = origin_y
        self.tile_size = tile_size
        self.board_width = COLS * tile_size
        self.board_height = ROWS * tile_size

        self.piece_images: Dict[str, pygame.Surface] = {}
        self.animations: List[PieceAnimation] = []
        self._load_piece_sprites()
        self.pulse_phase = 0.0

    def _load_piece_sprites(self) -> None:
        """Loads and pre-scales piece PNG sprites."""
        target_size = int(self.tile_size * 0.96)
        pieces_dir = os.path.join(ASSETS_DIR, "images", "pieces")

        for team in [TEAM_RED, TEAM_BLUE]:
            for p_type in [KING, QUEEN, ROOK, BISHOP, KNIGHT, PAWN]:
                key = f"{team}_{p_type}"
                path = os.path.join(pieces_dir, f"{key}.png")
                if os.path.exists(path):
                    surf = pygame.image.load(path).convert_alpha()
                    surf = pygame.transform.smoothscale(surf, (target_size, target_size))
                    self.piece_images[key] = surf

    def get_pixel_pos(self, row: int, col: int) -> Tuple[int, int]:
        """Calculates top-left pixel coordinates for a square (row, col)."""
        x = self.origin_x + col * self.tile_size
        y = self.origin_y + row * self.tile_size
        return (x, y)

    def get_square_at_pixel(self, px: int, py: int) -> Optional[Tuple[int, int]]:
        """Converts screen mouse coordinates to board (row, col)."""
        col = (px - self.origin_x) // self.tile_size
        row = (py - self.origin_y) // self.tile_size
        if 0 <= row < ROWS and 0 <= col < COLS:
            return (row, col)
        return None

    def trigger_move_animation(self, move: Move) -> None:
        """Starts a slide animation for the moving piece."""
        r1, c1 = move.start_pos
        r2, c2 = move.end_pos
        p1 = self.get_pixel_pos(r1, c1)
        p2 = self.get_pixel_pos(r2, c2)
        offset = int(self.tile_size * 0.06)
        anim = PieceAnimation(
            move.piece,
            (p1[0] + offset, p1[1] + offset),
            (p2[0] + offset, p2[1] + offset)
        )
        self.animations.append(anim)

    def update_animations(self, dt: float) -> None:
        self.pulse_phase = (self.pulse_phase + dt * 4.0) % (2 * math.pi)
        self.animations = [a for a in self.animations if not a.is_finished]

    def render(
        self,
        surface: pygame.Surface,
        game_state,
        selected_pos: Optional[Tuple[int, int]] = None,
        legal_moves: Optional[List[Move]] = None,
        last_move: Optional[Move] = None,
        hovered_pos: Optional[Tuple[int, int]] = None,
        dt: float = 0.016
    ) -> None:
        """Main rendering entry for the 7x4 board arena."""
        self.update_animations(dt)

        # 1. Outer Arena Board Frame
        frame_rect = pygame.Rect(
            self.origin_x - 14,
            self.origin_y - 14,
            self.board_width + 28,
            self.board_height + 28
        )
        # Deep stone bezel
        pygame.draw.rect(surface, (20, 24, 34), frame_rect, border_radius=12)
        pygame.draw.rect(surface, (70, 80, 105), frame_rect, width=3, border_radius=12)
        # Inner golden rune rim
        inner_rim = pygame.Rect(
            self.origin_x - 6,
            self.origin_y - 6,
            self.board_width + 12,
            self.board_height + 12
        )
        pygame.draw.rect(surface, (180, 150, 70), inner_rim, width=2, border_radius=8)

        # 2. Render Board Squares
        font_coord = pygame.font.SysFont("segoeui", 14, bold=True)
        col_names = ["A", "B", "C", "D"]

        for r in range(ROWS):
            for c in range(COLS):
                sq_rect = pygame.Rect(
                    self.origin_x + c * self.tile_size,
                    self.origin_y + r * self.tile_size,
                    self.tile_size,
                    self.tile_size
                )
                # Alternating checker pattern
                is_light = (r + c) % 2 == 0
                tile_color = COLOR_TILE_LIGHT if is_light else COLOR_TILE_DARK
                pygame.draw.rect(surface, tile_color, sq_rect)
                pygame.draw.rect(surface, COLOR_TILE_BORDER, sq_rect, width=1)

                # Tile center tactical rune
                cx = sq_rect.centerx
                cy = sq_rect.centery
                rune_radius = 8
                pygame.draw.circle(surface, COLOR_TILE_RUNE, (cx, cy), rune_radius, width=1)

                # Environmental Hazard Overlays
                effects = game_state.battlefield_mgr.get_effects_at(r, c)
                for eff in effects:
                    self._render_hazard_overlay(surface, sq_rect, eff.effect_type)

        # 3. Square Coordinate Labels
        for c in range(COLS):
            lbl = font_coord.render(col_names[c], True, (170, 180, 205))
            surface.blit(lbl, (self.origin_x + c * self.tile_size + self.tile_size // 2 - 5, self.origin_y - 28))
            surface.blit(lbl, (self.origin_x + c * self.tile_size + self.tile_size // 2 - 5, self.origin_y + self.board_height + 12))

        for r in range(ROWS):
            lbl = font_coord.render(str(ROWS - r), True, (170, 180, 205))
            surface.blit(lbl, (self.origin_x - 26, self.origin_y + r * self.tile_size + self.tile_size // 2 - 8))
            surface.blit(lbl, (self.origin_x + self.board_width + 12, self.origin_y + r * self.tile_size + self.tile_size // 2 - 8))

        # 4. Highlight Last Move
        if last_move:
            self._render_last_move_highlight(surface, last_move)

        # 4.5 Highlight Mouse Hovered Square
        if hovered_pos and hovered_pos != selected_pos:
            hr, hc = hovered_pos
            hov_rect = pygame.Rect(
                self.origin_x + hc * self.tile_size,
                self.origin_y + hr * self.tile_size,
                self.tile_size,
                self.tile_size
            )
            h_surf = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)
            pygame.draw.rect(h_surf, (255, 255, 255, 25), h_surf.get_rect(), border_radius=6)
            pygame.draw.rect(h_surf, (160, 220, 255, 180), h_surf.get_rect(), width=2, border_radius=6)
            surface.blit(h_surf, hov_rect)

        # 5. Highlight Selected Piece & Legal Moves
        if selected_pos:
            sr, sc = selected_pos
            sel_rect = pygame.Rect(
                self.origin_x + sc * self.tile_size,
                self.origin_y + sr * self.tile_size,
                self.tile_size,
                self.tile_size
            )
            # Pulsing golden highlight
            glow_alpha = int(170 + 60 * math.sin(self.pulse_phase))
            sel_surf = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)
            pygame.draw.rect(sel_surf, (*COLOR_HIGHLIGHT_SELECT[:3], glow_alpha), sel_surf.get_rect(), border_radius=6)
            pygame.draw.rect(sel_surf, (255, 235, 120, 250), sel_surf.get_rect(), width=3, border_radius=6)
            surface.blit(sel_surf, sel_rect)

        # Render Legal Target Highlights
        if legal_moves:
            for m in legal_moves:
                tr, tc = m.end_pos
                tgt_rect = pygame.Rect(
                    self.origin_x + tc * self.tile_size,
                    self.origin_y + tr * self.tile_size,
                    self.tile_size,
                    self.tile_size
                )
                self._render_move_target_highlight(surface, tgt_rect, m)

        # 6. Render Pieces
        animated_pieces = {a.piece.id: a for a in self.animations}
        target_size = int(self.tile_size * 0.96)
        offset_x = (self.tile_size - target_size) // 2
        offset_y = (self.tile_size - target_size) // 2

        for p in game_state.get_alive_pieces():
            if p.id in animated_pieces:
                # Handled by animated pass
                continue

            px, py = self.get_pixel_pos(p.row, p.col)
            # Gentle organic idle breathing
            bob = math.sin(self.pulse_phase + (p.row * 1.6 + p.col * 2.1)) * 2.2
            draw_x = px + offset_x
            draw_y = py + offset_y + int(bob)

            # Draw tactical corner brackets at the tile base
            self._draw_tactical_tile_brackets(surface, px, py, p.team, is_selected=(selected_pos == (p.row, p.col)))

            self._draw_single_piece(surface, p, draw_x, draw_y, is_selected=(selected_pos == (p.row, p.col)))

        # Draw currently animating pieces
        for anim in self.animations:
            cur_x, cur_y = anim.update(dt)
            self._draw_single_piece(surface, anim.piece, cur_x, cur_y)

    def _draw_tactical_tile_brackets(self, surface: pygame.Surface, px: int, py: int, team: str, is_selected: bool = False) -> None:
        """Draws glowing tactical corner brackets and base rune matching the arena aesthetic."""
        bracket_col = (255, 65, 95) if team == TEAM_RED else (30, 200, 255)
        if is_selected:
            bracket_col = (255, 230, 80)

        # Soft base radial glow
        base_glow = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)
        cx, cy = self.tile_size // 2, self.tile_size // 2
        glow_alpha = 45 if not is_selected else 85
        pygame.draw.ellipse(base_glow, (*bracket_col[:3], glow_alpha), (cx - 30, cy + 12, 60, 24))
        surface.blit(base_glow, (px, py))

        # Corner bracket line length & inset
        b_len = 12
        inset = 6
        x1, y1 = px + inset, py + inset
        x2, y2 = px + self.tile_size - inset, py + self.tile_size - inset
        width = 3 if is_selected else 2

        # Top-Left ┌
        pygame.draw.lines(surface, bracket_col, False, [(x1 + b_len, y1), (x1, y1), (x1, y1 + b_len)], width)
        # Top-Right ┐
        pygame.draw.lines(surface, bracket_col, False, [(x2 - b_len, y1), (x2, y1), (x2, y1 + b_len)], width)
        # Bottom-Left └
        pygame.draw.lines(surface, bracket_col, False, [(x1 + b_len, y2), (x1, y2), (x1, y2 - b_len)], width)
        # Bottom-Right ┘
        pygame.draw.lines(surface, bracket_col, False, [(x2 - b_len, y2), (x2, y2), (x2, y2 - b_len)], width)

        # If selected, draw glowing tactical targeting reticle at feet
        if is_selected:
            reticle_r = 28
            rot_a = self.pulse_phase * 2.0
            pygame.draw.circle(surface, (255, 230, 80), (px + cx, py + cy + 18), reticle_r, width=1)
            # 4 Rotating tick marks
            for i in range(4):
                angle = rot_a + i * (math.pi / 2)
                tx1 = (px + cx) + int(math.cos(angle) * (reticle_r - 4))
                ty1 = (py + cy + 18) + int(math.sin(angle) * (reticle_r - 4))
                tx2 = (px + cx) + int(math.cos(angle) * (reticle_r + 4))
                ty2 = (py + cy + 18) + int(math.sin(angle) * (reticle_r + 4))
                pygame.draw.line(surface, (255, 240, 120), (tx1, ty1), (tx2, ty2), 2)

    def _draw_single_piece(self, surface: pygame.Surface, piece: Piece, px: int, py: int, is_selected: bool = False) -> None:
        """Draws piece sprite with team halo, status auras, and shield rings."""
        key = f"{piece.team}_{piece.piece_type}"
        sprite = self.piece_images.get(key)
        if sprite:
            surface.blit(sprite, (px, py))

        # Ability Ready Spark (Small golden star pip if ability is still available)
        if piece.can_use_ability():
            pip_x = px + int(self.tile_size * 0.78)
            pip_y = py + int(self.tile_size * 0.12)
            pulse_pip = 3 + int(math.sin(self.pulse_phase * 3.0))
            pygame.draw.circle(surface, (255, 215, 0), (pip_x, pip_y), pulse_pip)
            pygame.draw.circle(surface, (255, 255, 255), (pip_x, pip_y), 1)

        # Celestial Rotating Shield Ring (Royal Shield / Fortress / Sacrifice)
        if piece.shielded:
            cx = px + int(self.tile_size * 0.48)
            cy = py + int(self.tile_size * 0.48)
            shield_radius = int(self.tile_size * 0.44)
            pulse_r = shield_radius + int(2 * math.sin(self.pulse_phase * 2.5))

            # Outer celestial energy ring
            pygame.draw.circle(surface, (255, 220, 80), (cx, cy), pulse_r, width=3)
            pygame.draw.circle(surface, (255, 255, 220), (cx, cy), pulse_r - 2, width=1)

            # Orbiting shield power nodes
            for i in range(3):
                orb_angle = self.pulse_phase * 2.0 + i * (2 * math.pi / 3)
                ox = cx + int(math.cos(orb_angle) * pulse_r)
                oy = cy + int(math.sin(orb_angle) * pulse_r)
                pygame.draw.circle(surface, (255, 235, 120), (ox, oy), 4)
                pygame.draw.circle(surface, (255, 255, 255), (ox, oy), 2)

        # Frozen Ice Shards (Frozen Ground effect)
        if piece.frozen_turns > 0:
            cx = px + int(self.tile_size * 0.48)
            cy = py + int(self.tile_size * 0.48)
            pygame.draw.circle(surface, (120, 230, 255), (cx, cy), int(self.tile_size * 0.40), width=2)
            # Spiked ice crystal lines
            for i in range(6):
                ang = i * (math.pi / 3)
                ix1 = cx + int(math.cos(ang) * 22)
                iy1 = cy + int(math.sin(ang) * 22)
                ix2 = cx + int(math.cos(ang) * 36)
                iy2 = cy + int(math.sin(ang) * 36)
                pygame.draw.line(surface, (180, 245, 255), (ix1, iy1), (ix2, iy2), 2)

    def _render_move_target_highlight(self, surface: pygame.Surface, rect: pygame.Rect, move: Move) -> None:
        """Draws distinct markers for move, capture, or ability."""
        hl_surf = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)
        cx, cy = rect.width // 2, rect.height // 2

        if move.is_special_ability:
            # Arcane violet diamond
            points = [(cx, 12), (rect.width - 12, cy), (cx, rect.height - 12), (12, cy)]
            pygame.draw.polygon(hl_surf, COLOR_HIGHLIGHT_ABILITY, points)
            pygame.draw.polygon(hl_surf, (230, 180, 255, 250), points, width=2)
        elif move.is_capture:
            # Crimson attack ring
            pygame.draw.circle(hl_surf, COLOR_HIGHLIGHT_ATTACK, (cx, cy), 18)
            pygame.draw.circle(hl_surf, (255, 120, 120, 255), (cx, cy), 18, width=3)
        else:
            # Emerald move dot
            pygame.draw.circle(hl_surf, COLOR_HIGHLIGHT_MOVE, (cx, cy), 11)
            pygame.draw.circle(hl_surf, (160, 255, 180, 220), (cx, cy), 11, width=2)

        surface.blit(hl_surf, rect)

    def _render_last_move_highlight(self, surface: pygame.Surface, move: Move) -> None:
        """Highlights origin and destination tiles of the last move with a glowing directional vector."""
        r1, c1 = move.start_pos
        r2, c2 = move.end_pos
        p1 = self.get_pixel_pos(r1, c1)
        p2 = self.get_pixel_pos(r2, c2)
        rect1 = pygame.Rect(p1[0], p1[1], self.tile_size, self.tile_size)
        rect2 = pygame.Rect(p2[0], p2[1], self.tile_size, self.tile_size)

        # 1. Origin Tile Highlight (Warm amber halo)
        s1 = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)
        pygame.draw.rect(s1, (255, 200, 60, 65), s1.get_rect(), border_radius=6)
        pygame.draw.rect(s1, (255, 215, 80, 200), s1.get_rect(), width=2, border_radius=6)
        surface.blit(s1, rect1)

        # 2. Destination Tile Highlight (Pulsing electric cyan halo)
        alpha = int(95 + 45 * math.sin(self.pulse_phase))
        s2 = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)
        pygame.draw.rect(s2, (0, 200, 255, alpha), s2.get_rect(), border_radius=6)
        pygame.draw.rect(s2, (80, 235, 255, 240), s2.get_rect(), width=3, border_radius=6)
        surface.blit(s2, rect2)

        # 3. Directional Vector Arrow Connecting Start and End Squares
        c1_pt = (rect1.centerx, rect1.centery)
        c2_pt = (rect2.centerx, rect2.centery)
        dx = c2_pt[0] - c1_pt[0]
        dy = c2_pt[1] - c1_pt[1]
        dist = math.hypot(dx, dy)
        if dist > 8:
            angle = math.atan2(dy, dx)
            arrow_len = 14
            target_pt = (int(c2_pt[0] - 10 * math.cos(angle)), int(c2_pt[1] - 10 * math.sin(angle)))
            start_pt = (int(c1_pt[0] + 10 * math.cos(angle)), int(c1_pt[1] + 10 * math.sin(angle)))

            # Glowing vector line
            pygame.draw.line(surface, (0, 220, 255, 220), start_pt, target_pt, 3)
            # Arrow head
            p_left = (
                int(target_pt[0] - arrow_len * math.cos(angle - 0.45)),
                int(target_pt[1] - arrow_len * math.sin(angle - 0.45))
            )
            p_right = (
                int(target_pt[0] - arrow_len * math.cos(angle + 0.45)),
                int(target_pt[1] - arrow_len * math.sin(angle + 0.45))
            )
            pygame.draw.polygon(surface, (0, 230, 255, 240), [target_pt, p_left, p_right])

    def _render_hazard_overlay(self, surface: pygame.Surface, rect: pygame.Rect, effect_type: str) -> None:
        """Draws visual battlefield event effects on tiles."""
        s = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)
        if effect_type == EVENT_THUNDERSTORM:
            # Crackling electrical arcs
            pygame.draw.rect(s, (255, 230, 50, 70), s.get_rect())
            pygame.draw.line(s, (255, 255, 150), (10, 10), (rect.width - 15, rect.height - 10), 2)
            pygame.draw.line(s, (255, 255, 200), (rect.width - 20, 15), (15, rect.height - 15), 1)
        elif effect_type == EVENT_FROZEN_GROUND:
            # Glacial ice sheen
            pygame.draw.rect(s, (100, 210, 255, 80), s.get_rect())
            pygame.draw.circle(s, (180, 240, 255, 120), (rect.width // 2, rect.height // 2), 24, width=2)
        elif effect_type == EVENT_HEALING_ZONE:
            # Emerald sanctuary
            pygame.draw.rect(s, (46, 204, 113, 70), s.get_rect())
            pygame.draw.circle(s, (120, 255, 170, 160), (rect.width // 2, rect.height // 2), 20, width=2)
        elif effect_type == EVENT_FOG_OF_WAR:
            # Gray mist
            pygame.draw.rect(s, (180, 190, 210, 110), s.get_rect())
        elif effect_type == EVENT_EARTHQUAKE:
            # Cracked fissure
            pygame.draw.line(s, (230, 120, 40, 180), (12, 12), (rect.width // 2, rect.height // 2), 3)
            pygame.draw.line(s, (230, 120, 40, 180), (rect.width // 2, rect.height // 2), (rect.width - 10, rect.height - 15), 3)

        surface.blit(s, rect)

