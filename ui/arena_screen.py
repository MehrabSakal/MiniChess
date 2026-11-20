"""
Chaos Chess - AI Algorithm Arena & Benchmark Lab
"""
import io
import time
import pygame
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from typing import Optional, Tuple, Dict, Any, List
from config import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_TEXT_GOLD, COLOR_TEXT_WHITE, COLOR_PANEL_BG
from ai.ai_controller import ALL_ALGORITHMS, AIController
from game.game_state import GameState
from ui.sound_manager import SoundManager


class ArenaScreen:
    """Dedicated benchmarking arena to compare AI algorithm metrics with Matplotlib charts."""

    def __init__(self):
        self.sound_mgr = SoundManager.get_instance()
        self.algorithms = list(ALL_ALGORITHMS)
        self.red_algo_idx = 5   # Alpha-Beta
        self.blue_algo_idx = 3  # MCTS

        # Benchmark results cache
        self.results: Dict[str, Dict[str, Any]] = {}
        self.chart_surface: Optional[pygame.Surface] = None
        self.is_running_benchmark = False
        self.benchmark_status = "Ready to simulate algorithm comparison."

        # Fonts
        self.font_title = pygame.font.SysFont("georgia", 32, bold=True)
        self.font_header = pygame.font.SysFont("segoeui", 16, bold=True)
        self.font_body = pygame.font.SysFont("segoeui", 14)
        self.font_small = pygame.font.SysFont("segoeui", 12)
        self.font_mono = pygame.font.SysFont("consolas", 13)

        # UI Layout
        self.back_button = pygame.Rect(40, 35, 100, 38)
        self.red_cycle_btn = pygame.Rect(180, 105, 340, 42)
        self.blue_cycle_btn = pygame.Rect(560, 105, 340, 42)
        self.run_btn = pygame.Rect(940, 105, 180, 42)
        self.launch_match_btn = pygame.Rect(1140, 105, 180, 42)

        # Generate initial default chart
        self._run_quick_benchmark()

    def handle_event(self, event: pygame.event.Event) -> Optional[Tuple[str, Dict]]:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos

            if self.back_button.collidepoint(mx, my):
                self.sound_mgr.play("move")
                return ("menu", {})

            elif self.red_cycle_btn.collidepoint(mx, my):
                self.red_algo_idx = (self.red_algo_idx + 1) % len(self.algorithms)
                self.sound_mgr.play("move")

            elif self.blue_cycle_btn.collidepoint(mx, my):
                self.blue_algo_idx = (self.blue_algo_idx + 1) % len(self.algorithms)
                self.sound_mgr.play("move")

            elif self.run_btn.collidepoint(mx, my):
                self.sound_mgr.play("ability")
                self._run_quick_benchmark()

            elif self.launch_match_btn.collidepoint(mx, my):
                self.sound_mgr.play("ability")
                params = {
                    "red_algo": self.algorithms[self.red_algo_idx],
                    "blue_algo": self.algorithms[self.blue_algo_idx]
                }
                return ("ai_vs_ai", params)

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return ("menu", {})

        return None

    def _run_quick_benchmark(self) -> None:
        """Runs test decisions for both selected algorithms and builds comparison chart."""
        algo_red = self.algorithms[self.red_algo_idx]
        algo_blue = self.algorithms[self.blue_algo_idx]

        state = GameState()
        state.board.setup_standard_board()

        ai_red = AIController(algo_red, team="red")
        ai_blue = AIController(algo_blue, team="blue")

        # Sample Red move
        t0 = time.time()
        _, m_red = ai_red.choose_move(state)
        time_red = (time.time() - t0) * 1000.0

        # Sample Blue move
        state.current_turn = "blue"
        t1 = time.time()
        _, m_blue = ai_blue.choose_move(state)
        time_blue = (time.time() - t1) * 1000.0

        self.results = {
            algo_red: {
                "time_ms": round(time_red, 2),
                "nodes": m_red.get("nodes_explored", 0),
                "pruned": m_red.get("nodes_pruned", 0),
                "eval": m_red.get("eval_score", 0.0),
                "team": "Red Legion"
            },
            algo_blue: {
                "time_ms": round(time_blue, 2),
                "nodes": m_blue.get("nodes_explored", 0),
                "pruned": m_blue.get("nodes_pruned", 0),
                "eval": m_blue.get("eval_score", 0.0),
                "team": "Blue Vanguard"
            }
        }
        self.benchmark_status = f"Benchmarked: {algo_red} vs {algo_blue} successfully."
        self._generate_matplotlib_chart(algo_red, algo_blue)

    def _generate_matplotlib_chart(self, red_name: str, blue_name: str) -> None:
        """Creates a modern dual-bar performance chart using Matplotlib and converts to Pygame surface."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.2, 3.8), facecolor="#181c28")

        for ax in (ax1, ax2):
            ax.set_facecolor("#121520")
            ax.tick_params(colors="#cbd5e1", labelsize=8)
            ax.spines["bottom"].set_color("#475569")
            ax.spines["top"].set_color("#475569")
            ax.spines["left"].set_color("#475569")
            ax.spines["right"].set_color("#475569")

        # 1. Execution Time Comparison
        times = [self.results[red_name]["time_ms"], self.results[blue_name]["time_ms"]]
        labels = [f"Red:\n{red_name[:12]}", f"Blue:\n{blue_name[:12]}"]
        bars1 = ax1.bar(labels, times, color=["#ef4444", "#38bdf8"], width=0.55)
        ax1.set_title("Execution Time (ms)", color="#f8fafc", fontsize=11, fontweight="bold")
        for bar in bars1:
            yval = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width() / 2, yval + max(times)*0.02, f"{round(yval, 1)}ms",
                     ha="center", va="bottom", color="#f8fafc", fontsize=8)

        # 2. Nodes Explored & Pruned Comparison
        nodes = [self.results[red_name]["nodes"], self.results[blue_name]["nodes"]]
        pruned = [self.results[red_name]["pruned"], self.results[blue_name]["pruned"]]
        x_indices = [0, 1]
        width = 0.35
        ax2.bar([x - width/2 for x in x_indices], nodes, width=width, label="Explored", color="#fbbf24")
        ax2.bar([x + width/2 for x in x_indices], pruned, width=width, label="Pruned", color="#a855f7")
        ax2.set_xticks(x_indices)
        ax2.set_xticklabels(labels)
        ax2.set_title("Search Nodes & Pruning", color="#f8fafc", fontsize=11, fontweight="bold")
        ax2.legend(facecolor="#1e2230", edgecolor="#475569", labelcolor="#f8fafc", fontsize=8)

        fig.tight_layout()

        # Render to Pygame Surface
        canvas = fig.canvas
        canvas.draw()
        rgba_buffer = canvas.buffer_rgba()
        size = canvas.get_width_height()
        raw_surf = pygame.image.frombuffer(rgba_buffer, size, "RGBA")
        self.chart_surface = raw_surf
        plt.close(fig)

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((16, 18, 27))
        mouse_pos = pygame.mouse.get_pos()

        # Back Button
        b_hover = self.back_button.collidepoint(mouse_pos)
        pygame.draw.rect(surface, (45, 55, 75) if b_hover else (30, 36, 50), self.back_button, border_radius=6)
        pygame.draw.rect(surface, (90, 110, 140), self.back_button, width=1, border_radius=6)
        lbl_b = self.font_body.render("← BACK", True, COLOR_TEXT_WHITE)
        surface.blit(lbl_b, (self.back_button.centerx - lbl_b.get_width() // 2, self.back_button.centery - lbl_b.get_height() // 2))

        # Title
        t_surf = self.font_title.render("AI ALGORITHM ARENA & BENCHMARK LAB", True, COLOR_TEXT_GOLD)
        surface.blit(t_surf, (180, 35))

        # Algorithm Selection Controls
        # Red Cycle Button
        red_algo = self.algorithms[self.red_algo_idx]
        r_hover = self.red_cycle_btn.collidepoint(mouse_pos)
        pygame.draw.rect(surface, (55, 30, 40) if r_hover else (38, 22, 30), self.red_cycle_btn, border_radius=6)
        pygame.draw.rect(surface, (235, 70, 90), self.red_cycle_btn, width=2 if r_hover else 1, border_radius=6)
        lbl_r = self.font_body.render(f"Red: {red_algo} ▾", True, (255, 160, 175))
        surface.blit(lbl_r, (self.red_cycle_btn.x + 14, self.red_cycle_btn.centery - lbl_r.get_height() // 2))

        # Blue Cycle Button
        blue_algo = self.algorithms[self.blue_algo_idx]
        b_hov = self.blue_cycle_btn.collidepoint(mouse_pos)
        pygame.draw.rect(surface, (30, 45, 65) if b_hov else (20, 32, 48), self.blue_cycle_btn, border_radius=6)
        pygame.draw.rect(surface, (60, 180, 245), self.blue_cycle_btn, width=2 if b_hov else 1, border_radius=6)
        lbl_bl = self.font_body.render(f"Blue: {blue_algo} ▾", True, (160, 215, 255))
        surface.blit(lbl_bl, (self.blue_cycle_btn.x + 14, self.blue_cycle_btn.centery - lbl_bl.get_height() // 2))

        # Run Benchmark Button
        run_hov = self.run_btn.collidepoint(mouse_pos)
        pygame.draw.rect(surface, (70, 55, 25) if run_hov else (45, 36, 18), self.run_btn, border_radius=6)
        pygame.draw.rect(surface, (255, 215, 0), self.run_btn, width=2 if run_hov else 1, border_radius=6)
        lbl_run = self.font_body.render("BENCHMARK", True, COLOR_TEXT_GOLD)
        surface.blit(lbl_run, (self.run_btn.centerx - lbl_run.get_width() // 2, self.run_btn.centery - lbl_run.get_height() // 2))

        # Launch Visual Match Button
        l_hov = self.launch_match_btn.collidepoint(mouse_pos)
        pygame.draw.rect(surface, (45, 65, 40) if l_hov else (28, 45, 28), self.launch_match_btn, border_radius=6)
        pygame.draw.rect(surface, (46, 204, 113), self.launch_match_btn, width=2 if l_hov else 1, border_radius=6)
        lbl_l = self.font_body.render("START MATCH ⚔️", True, (160, 255, 180))
        surface.blit(lbl_l, (self.launch_match_btn.centerx - lbl_l.get_width() // 2, self.launch_match_btn.centery - lbl_l.get_height() // 2))

        # Status text
        lbl_stat = self.font_small.render(self.benchmark_status, True, (160, 175, 200))
        surface.blit(lbl_stat, (180, 155))

        # Comparison Table Card (Left Side)
        table_rect = pygame.Rect(40, 190, 540, 520)
        pygame.draw.rect(surface, COLOR_PANEL_BG, table_rect, border_radius=10)
        pygame.draw.rect(surface, (60, 70, 95), table_rect, width=1, border_radius=10)

        # Table Header
        h_rect = pygame.Rect(table_rect.x, table_rect.y, table_rect.width, 42)
        pygame.draw.rect(surface, (30, 36, 52), h_rect, border_top_left_radius=10, border_top_right_radius=10)
        lbl_tbl = self.font_header.render("PERFORMANCE TELEMETRY COMPARISON", True, COLOR_TEXT_WHITE)
        surface.blit(lbl_tbl, (table_rect.x + 16, table_rect.y + 10))

        # Table Rows
        cur_y = table_rect.y + 60
        for name in [red_algo, blue_algo]:
            data = self.results.get(name, {})
            team_lbl = data.get("team", "")
            team_col = (255, 120, 130) if "Red" in team_lbl else (120, 210, 255)

            # Row container
            row_box = pygame.Rect(table_rect.x + 16, cur_y, table_rect.width - 32, 200)
            pygame.draw.rect(surface, (20, 24, 34), row_box, border_radius=6)
            pygame.draw.rect(surface, team_col, row_box, width=1, border_radius=6)

            title_row = self.font_header.render(f"{team_lbl}: {name}", True, team_col)
            surface.blit(title_row, (row_box.x + 12, row_box.y + 10))

            items = [
                ("Execution Time:", f"{data.get('time_ms', 0.0)} ms"),
                ("Nodes Explored:", f"{data.get('nodes', 0):,}"),
                ("Nodes Pruned:", f"{data.get('pruned', 0):,}"),
                ("Static Eval Score:", f"{data.get('eval', 0.0)}"),
                ("Pruning Efficiency:", f"{round(data.get('pruned', 0) / max(1, data.get('nodes', 1) + data.get('pruned', 0)) * 100, 1)}%")
            ]

            iy = row_box.y + 40
            for k, v in items:
                surface.blit(self.font_body.render(k, True, (160, 170, 190)), (row_box.x + 16, iy))
                surface.blit(self.font_mono.render(v, True, COLOR_TEXT_WHITE), (row_box.right - 140, iy))
                iy += 28

            cur_y += 225

        # Matplotlib Chart Display Card (Right Side)
        chart_card_rect = pygame.Rect(600, 190, 720, 520)
        pygame.draw.rect(surface, COLOR_PANEL_BG, chart_card_rect, border_radius=10)
        pygame.draw.rect(surface, (60, 70, 95), chart_card_rect, width=1, border_radius=10)

        c_header = pygame.Rect(chart_card_rect.x, chart_card_rect.y, chart_card_rect.width, 42)
        pygame.draw.rect(surface, (30, 36, 52), c_header, border_top_left_radius=10, border_top_right_radius=10)
        lbl_c = self.font_header.render("LIVE MATPLOTLIB BENCHMARK VISUALIZATION", True, COLOR_TEXT_GOLD)
        surface.blit(lbl_c, (chart_card_rect.x + 16, chart_card_rect.y + 10))

        if self.chart_surface:
            # Center chart in card
            cx = chart_card_rect.centerx - self.chart_surface.get_width() // 2
            cy = chart_card_rect.y + 55
            surface.blit(self.chart_surface, (cx, cy))
