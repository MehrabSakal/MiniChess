"""
Chaos Chess - Live AI Thinking & Telemetry Console
"""
import pygame
from typing import Dict, Any, Optional
from config import (
    COLOR_PANEL_BG, COLOR_PANEL_BORDER, COLOR_PANEL_HEADER,
    COLOR_TEXT_WHITE, COLOR_TEXT_GOLD, COLOR_TEXT_MUTED,
    COLOR_TEXT_RED, COLOR_TEXT_BLUE,
    COLOR_RED_PRIMARY, COLOR_BLUE_PRIMARY
)


class AIPanel:
    """Renders the AI decision-making telemetry panel."""

    def __init__(self, rect: pygame.Rect, title: str = "AI TELEMETRY"):
        self.rect = rect
        self.title = title

    def render(
        self,
        surface: pygame.Surface,
        metrics: Optional[Dict[str, Any]] = None,
        team: str = "red",
        is_active: bool = False
    ) -> None:
        # Base container
        pygame.draw.rect(surface, COLOR_PANEL_BG, self.rect, border_radius=8)
        border_col = (200, 70, 90) if team == "red" else (60, 160, 240)
        border_width = 2 if is_active else 1
        pygame.draw.rect(surface, border_col if is_active else COLOR_PANEL_BORDER, self.rect, width=border_width, border_radius=8)

        # Header bar
        header_rect = pygame.Rect(self.rect.x, self.rect.y, self.rect.width, 34)
        pygame.draw.rect(surface, COLOR_PANEL_HEADER, header_rect, border_top_left_radius=8, border_top_right_radius=8)

        font_header = pygame.font.SysFont("segoeui", 14, bold=True)
        font_body = pygame.font.SysFont("segoeui", 12)
        font_mono = pygame.font.SysFont("consolas", 12)

        team_color = COLOR_TEXT_RED if team == "red" else COLOR_TEXT_BLUE
        header_text = font_header.render(self.title, True, team_color)
        surface.blit(header_text, (self.rect.x + 12, self.rect.y + 7))

        # Status pulse
        status_txt = "THINKING..." if is_active else "IDLE"
        status_col = (255, 215, 0) if is_active else (120, 130, 150)
        status_surf = font_header.render(status_txt, True, status_col)
        surface.blit(status_surf, (self.rect.right - status_surf.get_width() - 12, self.rect.y + 7))

        if not metrics:
            placeholder = font_body.render("Awaiting tactical move...", True, COLOR_TEXT_MUTED)
            surface.blit(placeholder, (self.rect.x + 14, self.rect.y + 50))
            return

        # Metrics layout
        y_cursor = self.rect.y + 44
        line_height = 20

        algo_name = metrics.get("algorithm", "Unknown AI")
        lbl_algo = font_header.render(f"{algo_name}", True, COLOR_TEXT_GOLD)
        surface.blit(lbl_algo, (self.rect.x + 12, y_cursor))
        y_cursor += line_height + 4

        # Key stats table
        stats = [
            ("Move:", metrics.get("selected_move", "None")),
            ("Eval Score:", f"{metrics.get('eval_score', 0.0)}"),
            ("Search Depth:", f"{metrics.get('search_depth', '-') }"),
            ("Explored Nodes:", f"{metrics.get('nodes_explored', 0):,}"),
            ("Pruned Nodes:", f"{metrics.get('nodes_pruned', 0):,}"),
            ("Compute Time:", f"{metrics.get('execution_time_ms', 0.0)} ms")
        ]

        if "mcts_simulations" in metrics:
            stats.append(("MCTS Rollouts:", f"{metrics['mcts_simulations']}"))

        for k, v in stats:
            lbl_k = font_body.render(k, True, COLOR_TEXT_MUTED)
            lbl_v = font_mono.render(v, True, COLOR_TEXT_WHITE)
            surface.blit(lbl_k, (self.rect.x + 14, y_cursor))
            surface.blit(lbl_v, (self.rect.right - lbl_v.get_width() - 14, y_cursor))
            y_cursor += line_height

        # Eval Gauge Bar
        y_cursor += 4
        bar_w = self.rect.width - 28
        bar_h = 10
        bar_rect = pygame.Rect(self.rect.x + 14, y_cursor, bar_w, bar_h)
        pygame.draw.rect(surface, (40, 45, 60), bar_rect, border_radius=4)

        # Center line
        mid_x = bar_rect.x + bar_w // 2
        pygame.draw.line(surface, (120, 130, 150), (mid_x, bar_rect.y), (mid_x, bar_rect.bottom), 2)

        # Fill relative to score (-500 to +500 clamped)
        eval_val = metrics.get("eval_score", 0.0)
        norm_val = max(-1.0, min(1.0, eval_val / 500.0))
        if norm_val > 0:
            fill_w = int((bar_w // 2) * norm_val)
            fill_rect = pygame.Rect(mid_x, bar_rect.y, fill_w, bar_h)
            pygame.draw.rect(surface, (46, 204, 113), fill_rect, border_radius=3)
        elif norm_val < 0:
            fill_w = int((bar_w // 2) * abs(norm_val))
            fill_rect = pygame.Rect(mid_x - fill_w, bar_rect.y, fill_w, bar_h)
            pygame.draw.rect(surface, (231, 76, 60), fill_rect, border_radius=3)

        y_cursor += bar_h + 8

        # Tactical Reasoning box
        reasoning = metrics.get("reasoning", "")
        if reasoning:
            box_rect = pygame.Rect(self.rect.x + 12, y_cursor, self.rect.width - 24, self.rect.bottom - y_cursor - 10)
            pygame.draw.rect(surface, (18, 20, 28), box_rect, border_radius=5)
            pygame.draw.rect(surface, (45, 50, 70), box_rect, width=1, border_radius=5)

            self._render_wrapped_text(surface, reasoning, box_rect.x + 8, box_rect.y + 6, box_rect.width - 16, font_body)

    def _render_wrapped_text(self, surface: pygame.Surface, text: str, x: int, y: int, max_w: int, font: pygame.font.Font) -> None:
        words = text.split(" ")
        line = ""
        cur_y = y

        for word in words:
            test_line = line + word + " "
            if font.size(test_line)[0] > max_w:
                surface.blit(font.render(line, True, (210, 215, 230)), (x, cur_y))
                line = word + " "
                cur_y += 16
            else:
                line = test_line

        if line:
            surface.blit(font.render(line, True, (210, 215, 230)), (x, cur_y))

