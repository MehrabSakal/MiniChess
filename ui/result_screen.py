"""
Chaos Chess - Match Result & Victory Screen
"""
import pygame
from typing import Optional, Dict, Any
from config import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_TEXT_GOLD, COLOR_TEXT_WHITE, COLOR_PANEL_BG
from ui.sound_manager import SoundManager


class ResultScreen:
    """Displays victory modal, victory reason, match statistics, winning move, and action options."""

    def __init__(self):
        self.sound_mgr = SoundManager.get_instance()
        self.font_title = pygame.font.SysFont("georgia", 36, bold=True)
        self.font_header = pygame.font.SysFont("segoeui", 17, bold=True)
        self.font_body = pygame.font.SysFont("segoeui", 13)
        self.font_btn = pygame.font.SysFont("segoeui", 14, bold=True)
        self.font_mono = pygame.font.SysFont("consolas", 13, bold=True)

        # Modal Container
        modal_w, modal_h = 620, 520
        cx = SCREEN_WIDTH // 2
        cy = SCREEN_HEIGHT // 2
        self.modal_rect = pygame.Rect(cx - modal_w // 2, cy - modal_h // 2, modal_w, modal_h)

        # 2 Required Action Buttons
        btn_w, btn_h = 240, 48
        by = self.modal_rect.bottom - 70
        self.btn_replay = pygame.Rect(cx - btn_w - 15, by, btn_w, btn_h)
        self.btn_menu = pygame.Rect(cx + 15, by, btn_w, btn_h)

    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            if self.btn_replay.collidepoint(mx, my):
                self.sound_mgr.play("ability")
                return "replay"
            elif self.btn_menu.collidepoint(mx, my):
                self.sound_mgr.play("move")
                return "menu"

        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_r):
                return "replay"
            elif event.key == pygame.K_ESCAPE:
                return "menu"

        return None

    def render(self, surface: pygame.Surface, game_state, match_duration: float = 0.0) -> None:
        # Darkened modal backdrop
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((8, 10, 16, 215))
        surface.blit(overlay, (0, 0))

        # Modal Card
        pygame.draw.rect(surface, (20, 24, 36), self.modal_rect, border_radius=14)
        border_col = (255, 215, 0)
        if game_state.winner == "red":
            border_col = (235, 70, 90)
        elif game_state.winner == "blue":
            border_col = (60, 180, 245)
        pygame.draw.rect(surface, border_col, self.modal_rect, width=3, border_radius=14)

        # Winner Announcement
        winner = game_state.winner
        if winner == "red":
            title_text = "RED LEGION VICTORIOUS!"
            title_col = (255, 100, 115)
        elif winner == "blue":
            title_text = "BLUE VANGUARD WINS!"
            title_col = (100, 210, 255)
        else:
            title_text = "MATCH CONCLUDED: DRAW"
            title_col = COLOR_TEXT_GOLD

        t_surf = self.font_title.render(title_text, True, title_col)
        surface.blit(t_surf, (self.modal_rect.centerx - t_surf.get_width() // 2, self.modal_rect.y + 26))

        # Victory Condition Badge
        reason = game_state.victory_reason or "Combat Decided"
        r_surf = self.font_header.render(f"★ {reason.upper()} ★", True, COLOR_TEXT_GOLD)
        surface.blit(r_surf, (self.modal_rect.centerx - r_surf.get_width() // 2, self.modal_rect.y + 76))

        # Last / Winning Move Display Box
        last_m = game_state.last_move
        move_card = pygame.Rect(self.modal_rect.x + 35, self.modal_rect.y + 112, self.modal_rect.width - 70, 42)
        pygame.draw.rect(surface, (28, 34, 50), move_card, border_radius=6)
        pygame.draw.rect(surface, (0, 210, 255), move_card, width=1, border_radius=6)

        lbl_lm_tag = self.font_header.render("LAST MOVE:", True, COLOR_TEXT_GOLD)
        lm_str = last_m.notation() if last_m else "Match Concluded by Turn Limit"
        lbl_lm_val = self.font_mono.render(lm_str, True, (220, 245, 255))
        surface.blit(lbl_lm_tag, (move_card.x + 14, move_card.y + 10))
        surface.blit(lbl_lm_val, (move_card.x + 130, move_card.y + 11))

        # Divider
        pygame.draw.line(
            surface, (55, 65, 85),
            (self.modal_rect.x + 35, self.modal_rect.y + 168),
            (self.modal_rect.right - 35, self.modal_rect.y + 168),
            1
        )

        # Match Telemetry Stats
        stats = [
            ("Total Match Turns:", f"{game_state.turn_count}"),
            ("Total Moves Executed:", f"{len(game_state.move_history)}"),
            ("Match Duration:", f"{round(match_duration, 1)} seconds"),
            ("Red Army Captures:", f"{len(game_state.captured_pieces['red'])} pieces"),
            ("Blue Army Captures:", f"{len(game_state.captured_pieces['blue'])} pieces"),
            ("Red Consecutive Domination:", f"{game_state.red_consecutive_domination} turns"),
            ("Blue Consecutive Domination:", f"{game_state.blue_consecutive_domination} turns"),
        ]

        sy = self.modal_rect.y + 182
        for label, val in stats:
            lbl_surf = self.font_body.render(label, True, (160, 175, 200))
            val_surf = self.font_body.render(val, True, COLOR_TEXT_WHITE)
            surface.blit(lbl_surf, (self.modal_rect.x + 45, sy))
            surface.blit(val_surf, (self.modal_rect.right - val_surf.get_width() - 45, sy))
            sy += 24

        # Buttons
        mouse_pos = pygame.mouse.get_pos()

        # 1. Replay of the Game Button
        rep_hover = self.btn_replay.collidepoint(mouse_pos)
        pygame.draw.rect(surface, (25, 75, 95) if rep_hover else (18, 50, 68), self.btn_replay, border_radius=8)
        pygame.draw.rect(surface, (0, 220, 255), self.btn_replay, width=2 if rep_hover else 1, border_radius=8)
        rep_txt = self.font_btn.render("▶ REPLAY OF THE GAME", True, (180, 245, 255))
        surface.blit(rep_txt, (self.btn_replay.centerx - rep_txt.get_width() // 2, self.btn_replay.centery - rep_txt.get_height() // 2))

        # 2. Return to Main Menu Button
        m_hover = self.btn_menu.collidepoint(mouse_pos)
        pygame.draw.rect(surface, (55, 65, 85) if m_hover else (35, 42, 58), self.btn_menu, border_radius=8)
        pygame.draw.rect(surface, (120, 140, 180), self.btn_menu, width=2 if m_hover else 1, border_radius=8)
        m_txt = self.font_btn.render("⌂ RETURN TO MAIN MENU", True, COLOR_TEXT_WHITE)
        surface.blit(m_txt, (self.btn_menu.centerx - m_txt.get_width() // 2, self.btn_menu.centery - m_txt.get_height() // 2))
