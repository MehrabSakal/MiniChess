"""
Chaos Chess - AI vs AI Algorithm Configuration Screen
Allows players to configure Red and Blue AI algorithms independently:
- Minimax
- Alpha-Beta Pruning
- Monte Carlo Tree Search (MCTS) with configurable iterations (400, 1000, 2000)
- Best First Search, DFS, and Fuzzy Logic
"""
import pygame
from typing import Optional, Tuple, Dict, Any, List
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    COLOR_TEXT_GOLD, COLOR_TEXT_WHITE, COLOR_TEXT_MUTED,
    COLOR_RED_PRIMARY, COLOR_BLUE_PRIMARY, COLOR_PANEL_BG
)
from ai.ai_controller import (
    ALGORITHM_MINIMAX, ALGORITHM_ALPHA_BETA, ALGORITHM_MCTS,
    ALGORITHM_BEST_FIRST, ALGORITHM_DFS, ALGORITHM_FUZZY
)
from ui.sound_manager import SoundManager


class AISelectScreen:
    """Configurator screen to select algorithms and parameters for AI vs AI combat."""

    def __init__(self):
        self.sound_mgr = SoundManager.get_instance()

        # Fonts
        self.font_title = pygame.font.SysFont("georgia", 34, bold=True)
        self.font_subtitle = pygame.font.SysFont("segoeui", 14)
        self.font_header = pygame.font.SysFont("segoeui", 18, bold=True)
        self.font_body = pygame.font.SysFont("segoeui", 13)
        self.font_btn = pygame.font.SysFont("segoeui", 13, bold=True)
        self.font_small = pygame.font.SysFont("segoeui", 11)

        # Algorithm choices
        self.algorithms: List[str] = [
            ALGORITHM_MINIMAX,
            ALGORITHM_ALPHA_BETA,
            ALGORITHM_MCTS,
            ALGORITHM_BEST_FIRST,
            ALGORITHM_DFS,
            ALGORITHM_FUZZY
        ]

        # Iteration budgets for MCTS
        self.iteration_options = [400, 1000, 2000]

        # Delay options
        self.speed_options = [("FAST (150ms)", 150), ("NORMAL (350ms)", 350), ("SLOW (650ms)", 650)]
        self.selected_speed_idx = 1

        # Current selections
        self.red_algo_idx = 1       # Alpha-Beta Pruning
        self.red_mcts_iter = 1000
        self.blue_algo_idx = 2      # MCTS
        self.blue_mcts_iter = 1000

        # UI Positioning
        self.back_button = pygame.Rect(40, 35, 140, 38)
        self.launch_button = pygame.Rect(SCREEN_WIDTH // 2 - 160, 680, 320, 50)

        # Team Panels: Left (Red) and Right (Blue)
        panel_w = 580
        panel_h = 515
        panel_y = 125
        self.red_panel_rect = pygame.Rect(70, panel_y, panel_w, panel_h)
        self.blue_panel_rect = pygame.Rect(710, panel_y, panel_w, panel_h)

        # Speed presets at bottom left
        self.speed_rects = [
            pygame.Rect(80 + i * 135, 688, 125, 34) for i in range(3)
        ]

        # Descriptions
        self.descriptions = {
            ALGORITHM_MINIMAX: (
                "Adversarial Game Tree Search",
                "Calculates all potential moves recursively to Depth 2. Assumes optimal counterplay by the opponent to guarantee the highest minimax value.",
                "Tactical, defensive, mathematically sound"
            ),
            ALGORITHM_ALPHA_BETA: (
                "Optimized Minimax Lookahead",
                "Explores Depth 3 while pruning mathematically irrelevant subtrees using Alpha/Beta bounds. Searches up to 75% fewer nodes with identical accuracy.",
                "Fast, deep foresight, optimal tactical pressure"
            ),
            ALGORITHM_MCTS: (
                "Monte Carlo Tree Search with UCT",
                "Executes stochastic simulation playouts to forecast game progression without relying on static heuristics. Balances exploration & exploitation via UCT.",
                "Statistical intuition, strategic depth, adaptive"
            ),
            ALGORITHM_BEST_FIRST: (
                "Heuristic Priority Queue Search",
                "Evaluates immediate moves using greedy tactical scoring (piece values, King safety, square control). Attacks high-value targets aggressively.",
                "Greedy, rapid, opportunistic attack style"
            ),
            ALGORITHM_DFS: (
                "Bounded Depth First Search",
                "Explores deep tactical lines branch-by-branch down to Depth 3. Ideal for escape path tracing and long tactical verification.",
                "Laser-focused, narrow deep lines, bold"
            ),
            ALGORITHM_FUZZY: (
                "Fuzzy Logic Threat Inference",
                "Evaluates battlefield tension using continuous membership curves (Low/Medium/High King Danger, Board Threat). Emulates human gut feeling.",
                "Intuitive, dynamic aggression, resilient"
            )
        }

    def _get_algo_buttons(self, panel_rect: pygame.Rect) -> List[Tuple[str, pygame.Rect]]:
        """Returns button rects for the 6 algorithm choices inside a team panel."""
        buttons = []
        bx = panel_rect.x + 20
        bw = (panel_rect.width - 50) // 2
        bh = 38
        y_start = panel_rect.y + 60

        # Row 0: Minimax, Alpha-Beta
        buttons.append((ALGORITHM_MINIMAX, pygame.Rect(bx, y_start, bw, bh)))
        buttons.append((ALGORITHM_ALPHA_BETA, pygame.Rect(bx + bw + 10, y_start, bw, bh)))

        # Row 1: MCTS (prominent wide or top row), Best First
        buttons.append((ALGORITHM_MCTS, pygame.Rect(bx, y_start + 48, bw, bh)))
        buttons.append((ALGORITHM_BEST_FIRST, pygame.Rect(bx + bw + 10, y_start + 48, bw, bh)))

        # Row 2: DFS, Fuzzy Logic
        buttons.append((ALGORITHM_DFS, pygame.Rect(bx, y_start + 96, bw, bh)))
        buttons.append((ALGORITHM_FUZZY, pygame.Rect(bx + bw + 10, y_start + 96, bw, bh)))

        return buttons

    def _get_iter_buttons(self, panel_rect: pygame.Rect) -> List[Tuple[int, pygame.Rect]]:
        """Returns buttons for MCTS iteration budget."""
        bx = panel_rect.x + 20
        bw = (panel_rect.width - 60) // 3
        bh = 34
        by = panel_rect.y + 225
        return [
            (val, pygame.Rect(bx + i * (bw + 10), by, bw, bh))
            for i, val in enumerate(self.iteration_options)
        ]

    def handle_event(self, event: pygame.event.Event) -> Optional[Tuple[str, Dict[str, Any]]]:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos

            # Back button
            if self.back_button.collidepoint(mx, my):
                self.sound_mgr.play("move")
                return ("mode_select", {})

            # Launch battle
            if self.launch_button.collidepoint(mx, my):
                self.sound_mgr.play("ability")
                params = {
                    "red_algo": self.algorithms[self.red_algo_idx],
                    "red_mcts_iter": self.red_mcts_iter,
                    "blue_algo": self.algorithms[self.blue_algo_idx],
                    "blue_mcts_iter": self.blue_mcts_iter,
                    "delay_ms": self.speed_options[self.selected_speed_idx][1]
                }
                return ("ai_vs_ai", params)

            # Speed Presets
            for i, rect in enumerate(self.speed_rects):
                if rect.collidepoint(mx, my):
                    self.selected_speed_idx = i
                    self.sound_mgr.play("move")
                    return None

            # Red Panel Algorithm Buttons
            red_btns = self._get_algo_buttons(self.red_panel_rect)
            for idx, (algo_name, rect) in enumerate(red_btns):
                if rect.collidepoint(mx, my):
                    self.red_algo_idx = idx
                    self.sound_mgr.play("move")
                    return None

            # Red Panel Iteration Buttons (if MCTS selected)
            if self.algorithms[self.red_algo_idx] == ALGORITHM_MCTS:
                for val, rect in self._get_iter_buttons(self.red_panel_rect):
                    if rect.collidepoint(mx, my):
                        self.red_mcts_iter = val
                        self.sound_mgr.play("move")
                        return None

            # Blue Panel Algorithm Buttons
            blue_btns = self._get_algo_buttons(self.blue_panel_rect)
            for idx, (algo_name, rect) in enumerate(blue_btns):
                if rect.collidepoint(mx, my):
                    self.blue_algo_idx = idx
                    self.sound_mgr.play("move")
                    return None

            # Blue Panel Iteration Buttons (if MCTS selected)
            if self.algorithms[self.blue_algo_idx] == ALGORITHM_MCTS:
                for val, rect in self._get_iter_buttons(self.blue_panel_rect):
                    if rect.collidepoint(mx, my):
                        self.blue_mcts_iter = val
                        self.sound_mgr.play("move")
                        return None

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return ("mode_select", {})
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                params = {
                    "red_algo": self.algorithms[self.red_algo_idx],
                    "red_mcts_iter": self.red_mcts_iter,
                    "blue_algo": self.algorithms[self.blue_algo_idx],
                    "blue_mcts_iter": self.blue_mcts_iter,
                    "delay_ms": self.speed_options[self.selected_speed_idx][1]
                }
                return ("ai_vs_ai", params)

        return None

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((16, 18, 27))
        mouse_pos = pygame.mouse.get_pos()

        # 1. Back Button
        b_hover = self.back_button.collidepoint(mouse_pos)
        pygame.draw.rect(surface, (45, 55, 75) if b_hover else (30, 36, 50), self.back_button, border_radius=6)
        pygame.draw.rect(surface, (90, 110, 140), self.back_button, width=1, border_radius=6)
        back_txt = self.font_body.render("← BACK TO MODES", True, COLOR_TEXT_WHITE)
        surface.blit(back_txt, (self.back_button.centerx - back_txt.get_width() // 2, self.back_button.centery - back_txt.get_height() // 2))

        # 2. Title & Subtitle
        title_surf = self.font_title.render("AI VS AI COMBAT CONFIGURATOR", True, COLOR_TEXT_GOLD)
        surface.blit(title_surf, (SCREEN_WIDTH // 2 - title_surf.get_width() // 2, 35))

        sub_surf = self.font_subtitle.render("Select algorithm and parameters for Red Legion and Blue Vanguard to battle autonomously", True, (160, 180, 210))
        surface.blit(sub_surf, (SCREEN_WIDTH // 2 - sub_surf.get_width() // 2, 85))

        # 3. Render Red Config Panel
        self._render_team_panel(surface, "red", self.red_panel_rect, self.red_algo_idx, self.red_mcts_iter)

        # 4. Render Blue Config Panel
        self._render_team_panel(surface, "blue", self.blue_panel_rect, self.blue_algo_idx, self.blue_mcts_iter)

        # 5. Speed presets
        lbl_spd = self.font_body.render("SIMULATION SPEED:", True, (160, 175, 200))
        surface.blit(lbl_spd, (80, 665))
        for i, ((txt, _), rect) in enumerate(zip(self.speed_options, self.speed_rects)):
            is_sel = (i == self.selected_speed_idx)
            h = rect.collidepoint(mouse_pos)
            col_bg = (55, 65, 95) if is_sel else ((40, 48, 70) if h else (25, 30, 45))
            pygame.draw.rect(surface, col_bg, rect, border_radius=5)
            pygame.draw.rect(surface, COLOR_TEXT_GOLD if is_sel else (60, 70, 90), rect, width=2 if is_sel else 1, border_radius=5)
            t_surf = self.font_small.render(txt, True, COLOR_TEXT_GOLD if is_sel else COLOR_TEXT_WHITE)
            surface.blit(t_surf, (rect.centerx - t_surf.get_width() // 2, rect.centery - t_surf.get_height() // 2))

        # 6. Launch Battle Button
        l_hover = self.launch_button.collidepoint(mouse_pos)
        col_l_bg = (180, 50, 60) if l_hover else (140, 35, 45)
        pygame.draw.rect(surface, col_l_bg, self.launch_button, border_radius=8)
        pygame.draw.rect(surface, (255, 215, 0), self.launch_button, width=2, border_radius=8)
        btn_txt = self.font_header.render("⚔ LAUNCH AI VS AI BATTLE ⚔", True, (255, 240, 180))
        surface.blit(btn_txt, (self.launch_button.centerx - btn_txt.get_width() // 2, self.launch_button.centery - btn_txt.get_height() // 2))

    def _render_team_panel(
        self,
        surface: pygame.Surface,
        team: str,
        panel_rect: pygame.Rect,
        selected_algo_idx: int,
        selected_mcts_iter: int
    ) -> None:
        mouse_pos = pygame.mouse.get_pos()
        theme_col = (255, 100, 110) if team == "red" else (100, 210, 255)
        border_col = COLOR_RED_PRIMARY if team == "red" else COLOR_BLUE_PRIMARY

        # Panel Base
        pygame.draw.rect(surface, COLOR_PANEL_BG, panel_rect, border_radius=10)
        pygame.draw.rect(surface, border_col, panel_rect, width=2, border_radius=10)

        # Header Bar
        head_rect = pygame.Rect(panel_rect.x, panel_rect.y, panel_rect.width, 45)
        pygame.draw.rect(surface, (30, 25, 40) if team == "red" else (22, 32, 48), head_rect, border_top_left_radius=10, border_top_right_radius=10)
        team_title = "RED LEGION — AI COMMANDER" if team == "red" else "BLUE VANGUARD — AI COMMANDER"
        lbl_head = self.font_header.render(team_title, True, theme_col)
        surface.blit(lbl_head, (panel_rect.x + 20, panel_rect.y + 10))

        # Algorithm Buttons
        algo_btns = self._get_algo_buttons(panel_rect)
        for idx, (algo_name, rect) in enumerate(algo_btns):
            is_selected = (idx == selected_algo_idx)
            is_hovered = rect.collidepoint(mouse_pos)

            if is_selected:
                bg = (120, 35, 45) if team == "red" else (25, 80, 130)
                b_color = (255, 215, 0)
                t_color = (255, 245, 200)
            else:
                bg = (40, 48, 65) if is_hovered else (26, 32, 45)
                b_color = (80, 95, 125) if is_hovered else (45, 55, 75)
                t_color = COLOR_TEXT_WHITE if is_hovered else COLOR_TEXT_MUTED

            pygame.draw.rect(surface, bg, rect, border_radius=6)
            pygame.draw.rect(surface, b_color, rect, width=2 if is_selected else 1, border_radius=6)

            # Short display label
            short_name = algo_name.replace("Monte Carlo Tree Search (MCTS)", "MCTS").replace("Constraint Satisfaction Problem (CSP)", "CSP")
            txt_surf = self.font_btn.render(short_name, True, t_color)
            surface.blit(txt_surf, (rect.centerx - txt_surf.get_width() // 2, rect.centery - txt_surf.get_height() // 2))

        # Iteration Selector (if MCTS selected)
        active_algo = self.algorithms[selected_algo_idx]
        if active_algo == ALGORITHM_MCTS:
            lbl_iter = self.font_body.render("MCTS SIMULATION BUDGET (ITERATIONS):", True, COLOR_TEXT_GOLD)
            surface.blit(lbl_iter, (panel_rect.x + 20, panel_rect.y + 204))

            for val, rect in self._get_iter_buttons(panel_rect):
                is_sel = (val == selected_mcts_iter)
                is_hov = rect.collidepoint(mouse_pos)
                col_bg = (100, 35, 45) if (team == "red" and is_sel) else ((20, 80, 130) if (team == "blue" and is_sel) else ((45, 55, 75) if is_hov else (28, 35, 50)))
                pygame.draw.rect(surface, col_bg, rect, border_radius=5)
                pygame.draw.rect(surface, (255, 215, 0) if is_sel else (70, 85, 110), rect, width=2 if is_sel else 1, border_radius=5)
                i_txt = self.font_btn.render(f"{val} Iterations", True, (255, 230, 150) if is_sel else COLOR_TEXT_WHITE)
                surface.blit(i_txt, (rect.centerx - i_txt.get_width() // 2, rect.centery - i_txt.get_height() // 2))

        # Algorithm Details Card
        info_y = panel_rect.y + (285 if active_algo == ALGORITHM_MCTS else 225)
        info_h = panel_rect.bottom - info_y - 20
        info_rect = pygame.Rect(panel_rect.x + 20, info_y, panel_rect.width - 40, info_h)
        pygame.draw.rect(surface, (20, 24, 35), info_rect, border_radius=8)
        pygame.draw.rect(surface, (45, 55, 75), info_rect, width=1, border_radius=8)

        meta = self.descriptions.get(active_algo, ("Algorithm Details", "Executes tactical evaluation.", "Standard"))
        head_text = f"ACTIVE: {active_algo.upper()}"
        if active_algo == ALGORITHM_MCTS:
            head_text += f" ({selected_mcts_iter} ROULLOUTS)"

        lbl_i_head = self.font_btn.render(head_text, True, theme_col)
        surface.blit(lbl_i_head, (info_rect.x + 15, info_rect.y + 12))

        lbl_i_sub = self.font_small.render(f"Class: {meta[0]}", True, COLOR_TEXT_GOLD)
        surface.blit(lbl_i_sub, (info_rect.x + 15, info_rect.y + 34))

        # Word wrap description
        desc_words = meta[1].split()
        lines = []
        cur_line = []
        for w in desc_words:
            test_line = " ".join(cur_line + [w])
            if self.font_body.size(test_line)[0] < info_rect.width - 30:
                cur_line.append(w)
            else:
                lines.append(" ".join(cur_line))
                cur_line = [w]
        if cur_line:
            lines.append(" ".join(cur_line))

        dy = info_rect.y + 58
        for line in lines:
            surface.blit(self.font_body.render(line, True, (200, 210, 230)), (info_rect.x + 15, dy))
            dy += 20

        # Characteristic badge
        badge_y = info_rect.bottom - 32
        lbl_trait = self.font_small.render(f"Playstyle: {meta[2]}", True, (130, 210, 255))
        surface.blit(lbl_trait, (info_rect.x + 15, badge_y))
