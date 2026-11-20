"""
Chaos Chess - Mode Selection Screen
"""
import pygame
from typing import Optional, Tuple, Dict
from config import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_TEXT_GOLD, COLOR_TEXT_WHITE, COLOR_PANEL_BG
from ui.sound_manager import SoundManager


class ModeSelectScreen:
    """Screen offering three game modes: AI vs AI, AI vs Human, Human vs Human."""

    def __init__(self):
        self.sound_mgr = SoundManager.get_instance()
        self.font_title = pygame.font.SysFont("georgia", 36, bold=True)
        self.font_card_title = pygame.font.SysFont("segoeui", 22, bold=True)
        self.font_body = pygame.font.SysFont("segoeui", 14)
        self.font_small = pygame.font.SysFont("segoeui", 12)

        # 3 Cards Layout
        card_w, card_h = 360, 420
        spacing = 40
        total_w = card_w * 3 + spacing * 2
        start_x = (SCREEN_WIDTH - total_w) // 2
        card_y = 170

        self.cards = {
            "ai_vs_ai": pygame.Rect(start_x, card_y, card_w, card_h),
            "ai_vs_human": pygame.Rect(start_x + card_w + spacing, card_y, card_w, card_h),
            "human_vs_human": pygame.Rect(start_x + (card_w + spacing) * 2, card_y, card_w, card_h)
        }

        # Back button
        self.back_button = pygame.Rect(40, 40, 110, 40)

        # Difficulty setting for AI vs Human
        self.difficulty_options = ["Easy", "Medium", "Hard", "Expert"]
        self.selected_difficulty_idx = 1  # Medium

        # AI vs AI algorithm picks
        from ai.ai_controller import ALL_ALGORITHMS, ALGORITHM_ALPHA_BETA, ALGORITHM_MCTS
        self.all_algorithms = ALL_ALGORITHMS
        self.red_algo_idx = 5   # Alpha-Beta
        self.blue_algo_idx = 3  # MCTS

    def handle_event(self, event: pygame.event.Event) -> Optional[Tuple[str, Dict]]:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos

            if self.back_button.collidepoint(mx, my):
                self.sound_mgr.play("move")
                return ("menu", {})

            for mode_key, rect in self.cards.items():
                if rect.collidepoint(mx, my):
                    self.sound_mgr.play("ability")
                    if mode_key == "ai_vs_human":
                        return ("difficulty_select", {})
                    elif mode_key == "ai_vs_ai":
                        return ("ai_vs_ai_select", {})
                    else:
                        return (mode_key, {})

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return ("menu", {})

        return None

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((16, 18, 27))

        # Title
        title_surf = self.font_title.render("SELECT COMBAT MODE", True, COLOR_TEXT_GOLD)
        surface.blit(title_surf, (SCREEN_WIDTH // 2 - title_surf.get_width() // 2, 60))

        # Back button
        mouse_pos = pygame.mouse.get_pos()
        b_hover = self.back_button.collidepoint(mouse_pos)
        pygame.draw.rect(surface, (45, 55, 75) if b_hover else (30, 36, 50), self.back_button, border_radius=6)
        pygame.draw.rect(surface, (90, 110, 140), self.back_button, width=1, border_radius=6)
        back_txt = self.font_body.render("← BACK", True, COLOR_TEXT_WHITE)
        surface.blit(back_txt, (self.back_button.centerx - back_txt.get_width() // 2, self.back_button.centery - back_txt.get_height() // 2))

        # Cards Data
        card_data = [
            ("ai_vs_ai", "AI vs AI", "AUTONOMOUS ARENA", [
                "• Red and Blue commanded by distinct AI models.",
                "• Select Minimax, Alpha-Beta, or MCTS with custom iterations.",
                "• Real-time search telemetry & metrics visualization."
            ], (235, 70, 90)),
            ("ai_vs_human", "AI vs Human", "TACTICAL CHALLENGE", [
                "• Command your army against an intelligent AI.",
                "• 3 Modes: High (Minimax), Medium (MCTS 1000), Low (MCTS 400).",
                "• Click to select AI tactical difficulty interface."
            ], (60, 180, 245)),
            ("human_vs_human", "Human vs Human", "LOCAL HOTSEAT", [
                "• Two-player local match on the same computer.",
                "• Full special abilities & dynamic energy systems.",
                "• Move history and undo support."
            ], (180, 110, 245))
        ]

        for key, title, subtitle, bullets, accent_col in card_data:
            rect = self.cards[key]
            hovered = rect.collidepoint(mouse_pos)

            # Card Background
            bg_col = (30, 35, 50) if hovered else (22, 26, 38)
            pygame.draw.rect(surface, bg_col, rect, border_radius=12)
            border_w = 3 if hovered else 1
            pygame.draw.rect(surface, accent_col if hovered else (60, 70, 90), rect, width=border_w, border_radius=12)

            # Card Header
            header_rect = pygame.Rect(rect.x, rect.y, rect.width, 60)
            pygame.draw.rect(surface, (28, 32, 48), header_rect, border_top_left_radius=12, border_top_right_radius=12)
            lbl_title = self.font_card_title.render(title, True, accent_col)
            surface.blit(lbl_title, (rect.x + 20, rect.y + 14))

            # Subtitle
            lbl_sub = self.font_small.render(subtitle, True, (160, 175, 200))
            surface.blit(lbl_sub, (rect.x + 20, rect.y + 75))

            # Bullets
            cur_y = rect.y + 115
            for bullet in bullets:
                b_surf = self.font_body.render(bullet, True, (215, 220, 235))
                surface.blit(b_surf, (rect.x + 20, cur_y))
                cur_y += 32

            # Bottom Launch prompt
            launch_rect = pygame.Rect(rect.x + 20, rect.bottom - 60, rect.width - 40, 42)
            l_bg = accent_col if hovered else (40, 48, 68)
            pygame.draw.rect(surface, l_bg, launch_rect, border_radius=6)
            l_txt = self.font_card_title.render("SELECT MODE", True, (15, 18, 25) if hovered else COLOR_TEXT_WHITE)
            surface.blit(l_txt, (launch_rect.centerx - l_txt.get_width() // 2, launch_rect.centery - l_txt.get_height() // 2))

