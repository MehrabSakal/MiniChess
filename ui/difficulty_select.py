"""
Chaos Chess - Difficulty Selection Screen (Human vs AI)
Provides selection between:
- High: Minimax Adversarial Search
- Medium: Monte Carlo Tree Search (MCTS) with 1000 iterations
- Low: Monte Carlo Tree Search (MCTS) with 400 iterations
"""
import pygame
from typing import Optional, Tuple, Dict, Any
from config import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_TEXT_GOLD, COLOR_TEXT_WHITE, COLOR_PANEL_BG
from ui.sound_manager import SoundManager


class DifficultySelectScreen:
    """Dedicated interface allowing the player to select game difficulty for Human vs AI."""

    def __init__(self):
        self.sound_mgr = SoundManager.get_instance()
        self.font_title = pygame.font.SysFont("georgia", 36, bold=True)
        self.font_subtitle = pygame.font.SysFont("segoeui", 15)
        self.font_card_title = pygame.font.SysFont("segoeui", 26, bold=True)
        self.font_badge = pygame.font.SysFont("segoeui", 13, bold=True)
        self.font_body = pygame.font.SysFont("segoeui", 14)
        self.font_small = pygame.font.SysFont("segoeui", 12)
        self.font_btn = pygame.font.SysFont("segoeui", 15, bold=True)

        # Back button
        self.back_button = pygame.Rect(40, 40, 150, 40)

        # 3 Difficulty Cards Layout
        card_w, card_h = 360, 460
        spacing = 40
        total_w = card_w * 3 + spacing * 2
        start_x = (SCREEN_WIDTH - total_w) // 2
        card_y = 160

        self.cards = {
            "Low": pygame.Rect(start_x, card_y, card_w, card_h),
            "Medium": pygame.Rect(start_x + card_w + spacing, card_y, card_w, card_h),
            "High": pygame.Rect(start_x + (card_w + spacing) * 2, card_y, card_w, card_h)
        }

    def handle_event(self, event: pygame.event.Event) -> Optional[Tuple[str, Dict[str, Any]]]:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos

            if self.back_button.collidepoint(mx, my):
                self.sound_mgr.play("move")
                return ("mode_select", {})

            for diff_key, rect in self.cards.items():
                if rect.collidepoint(mx, my):
                    self.sound_mgr.play("ability")
                    params = {"difficulty": diff_key}
                    return ("ai_vs_human", params)

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return ("mode_select", {})
            elif event.key == pygame.K_1 or event.key == pygame.K_l:
                return ("ai_vs_human", {"difficulty": "Low"})
            elif event.key == pygame.K_2 or event.key == pygame.K_m:
                return ("ai_vs_human", {"difficulty": "Medium"})
            elif event.key == pygame.K_3 or event.key == pygame.K_h:
                return ("ai_vs_human", {"difficulty": "High"})

        return None

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((16, 18, 27))
        mouse_pos = pygame.mouse.get_pos()

        # Back Button
        b_hover = self.back_button.collidepoint(mouse_pos)
        pygame.draw.rect(surface, (45, 55, 75) if b_hover else (30, 36, 50), self.back_button, border_radius=6)
        pygame.draw.rect(surface, (90, 110, 140), self.back_button, width=1, border_radius=6)
        back_txt = self.font_body.render("← BACK TO MODES", True, COLOR_TEXT_WHITE)
        surface.blit(back_txt, (self.back_button.centerx - back_txt.get_width() // 2, self.back_button.centery - back_txt.get_height() // 2))

        # Title & Subtitle
        title_surf = self.font_title.render("SELECT AI DIFFICULTY", True, COLOR_TEXT_GOLD)
        surface.blit(title_surf, (SCREEN_WIDTH // 2 - title_surf.get_width() // 2, 50))

        sub_surf = self.font_subtitle.render("Choose the tactical computational depth and search algorithm for your AI opponent", True, (160, 180, 210))
        surface.blit(sub_surf, (SCREEN_WIDTH // 2 - sub_surf.get_width() // 2, 100))

        # Card Specifications
        cards_data = [
            ("Low", "LOW", "CASUAL TACTICIAN", "MCTS • 400 ITERATIONS", [
                "• AI Engine: Monte Carlo Tree Search",
                "• Playout Budget: 400 Simulations",
                "• Fast tactical lookahead with UCT",
                "• Balanced for accessible, casual gameplay",
                "• Natural human-like exploratory variance"
            ], (46, 204, 113), "START LOW (400 MCTS)"),

            ("Medium", "MEDIUM", "SEASONED STRATEGIST", "MCTS • 1000 ITERATIONS", [
                "• AI Engine: Monte Carlo Tree Search",
                "• Playout Budget: 1000 Simulations",
                "• Deep stochastic tactical convergence",
                "• Strong positional control & threat foresight",
                "• Active, calculated special ability usage"
            ], (243, 156, 18), "START MEDIUM (1000 MCTS)"),

            ("High", "HIGH", "GRANDMASTER ARENA", "MINIMAX ADVERSARIAL", [
                "• AI Engine: Minimax Adversarial Search",
                "• Strategy: Exhaustive Game Tree Search",
                "• Complete adversarial tree evaluation",
                "• Evaluates all counter-attacks & defenses",
                "• Relentless, optimal tactical pressure"
            ], (231, 76, 60), "START HIGH (MINIMAX)")
        ]

        for key, title, subtitle, algo_badge, bullets, accent_col, btn_label in cards_data:
            rect = self.cards[key]
            hovered = rect.collidepoint(mouse_pos)

            # Card Container
            bg_col = (28, 34, 48) if hovered else (20, 24, 34)
            pygame.draw.rect(surface, bg_col, rect, border_radius=12)
            border_w = 3 if hovered else 1
            pygame.draw.rect(surface, accent_col if hovered else (55, 65, 85), rect, width=border_w, border_radius=12)

            # Card Header Bar
            header_rect = pygame.Rect(rect.x, rect.y, rect.width, 70)
            pygame.draw.rect(surface, (28, 32, 46), header_rect, border_top_left_radius=12, border_top_right_radius=12)

            # Title
            lbl_title = self.font_card_title.render(title, True, accent_col)
            surface.blit(lbl_title, (rect.x + 20, rect.y + 10))

            # Subtitle
            lbl_sub = self.font_small.render(subtitle, True, (160, 175, 200))
            surface.blit(lbl_sub, (rect.x + 20, rect.y + 44))

            # Algorithm Badge Box
            badge_rect = pygame.Rect(rect.x + 20, rect.y + 82, rect.width - 40, 32)
            pygame.draw.rect(surface, (18, 22, 32), badge_rect, border_radius=6)
            pygame.draw.rect(surface, accent_col, badge_rect, width=1, border_radius=6)
            badge_surf = self.font_badge.render(algo_badge, True, accent_col)
            surface.blit(badge_surf, (badge_rect.centerx - badge_surf.get_width() // 2, badge_rect.centery - badge_surf.get_height() // 2))

            # Bullets
            cur_y = rect.y + 135
            for bullet in bullets:
                b_surf = self.font_body.render(bullet, True, (215, 220, 235))
                surface.blit(b_surf, (rect.x + 20, cur_y))
                cur_y += 34

            # Bottom Launch Button
            btn_rect = pygame.Rect(rect.x + 20, rect.bottom - 60, rect.width - 40, 44)
            b_bg = accent_col if hovered else (38, 46, 65)
            pygame.draw.rect(surface, b_bg, btn_rect, border_radius=8)
            btn_txt = self.font_btn.render(btn_label, True, (15, 18, 25) if hovered else COLOR_TEXT_WHITE)
            surface.blit(btn_txt, (btn_rect.centerx - btn_txt.get_width() // 2, btn_rect.centery - btn_txt.get_height() // 2))
