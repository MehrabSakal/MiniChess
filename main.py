"""
Chaos Chess - Main Application Entry Point
"""
import sys
import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, WINDOW_TITLE
from game.game_engine import GameEngine
from modes.ai_vs_ai import AIvsAIMode
from modes.ai_vs_human import AIvsHumanMode
from modes.human_vs_human import HumanvsHumanMode
from ui.menu import MainMenu
from ui.mode_select import ModeSelectScreen
from ui.difficulty_select import DifficultySelectScreen
from ui.ai_select import AISelectScreen
from ui.game_screen import GameScreen
from ui.arena_screen import ArenaScreen
from ui.how_to_play import HowToPlayScreen
from ui.settings import SettingsScreen
from ui.result_screen import ResultScreen
from ui.sound_manager import SoundManager

# Screen state constants
STATE_MENU = "menu"
STATE_MODE_SELECT = "mode_select"
STATE_DIFFICULTY_SELECT = "difficulty_select"
STATE_AI_VS_AI_SELECT = "ai_vs_ai_select"
STATE_GAME = "game"
STATE_ARENA = "arena"
STATE_HOW_TO_PLAY = "how_to_play"
STATE_SETTINGS = "settings"


class ChaosChessApp:
    """Master application controller managing scenes, transitions, and main game loop."""

    def __init__(self):
        pygame.init()
        pygame.display.set_caption(WINDOW_TITLE)

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.is_running = True

        # Shared Engine
        self.engine = GameEngine()
        self.sound_mgr = SoundManager.get_instance()

        # Scene instances
        self.menu_screen = MainMenu()
        self.mode_select_screen = ModeSelectScreen()
        self.difficulty_select_screen = DifficultySelectScreen()
        self.ai_select_screen = AISelectScreen()
        self.arena_screen = ArenaScreen()
        self.how_to_play_screen = HowToPlayScreen()
        self.settings_screen = SettingsScreen()
        self.result_screen = ResultScreen()

        # Game scene state
        self.game_screen: GameScreen = None
        self.current_state = STATE_MENU

        # Active match configuration cache
        self.last_mode_name = "ai_vs_human"
        self.last_mode_params = {"difficulty": "Medium"}

    def run(self) -> None:
        """Main game loop."""
        while self.is_running:
            dt = self.clock.tick(FPS) / 1000.0

            # 1. Event Handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_running = False
                    break
                self._handle_event(event)

            if not self.is_running:
                break

            # 2. Scene Updates
            self._update(dt)

            # 3. Scene Rendering
            self._render()

            pygame.display.flip()

        pygame.quit()
        sys.exit(0)

    def _handle_event(self, event: pygame.event.Event) -> None:
        # Check if Game Over result screen modal is active
        if self.current_state == STATE_GAME and self.engine.state.is_game_over:
            res_action = self.result_screen.handle_event(event)
            if res_action == "play_again":
                self._start_match(self.last_mode_name, self.last_mode_params)
                return
            elif res_action == "menu":
                self.current_state = STATE_MENU
                return

        # Regular Scene Event Routing
        if self.current_state == STATE_MENU:
            action = self.menu_screen.handle_event(event)
            if action == "play":
                self.current_state = STATE_MODE_SELECT
            elif action == "arena":
                self.current_state = STATE_ARENA
            elif action == "how_to_play":
                self.current_state = STATE_HOW_TO_PLAY
            elif action == "settings":
                self.current_state = STATE_SETTINGS
            elif action == "exit":
                self.is_running = False

        elif self.current_state == STATE_MODE_SELECT:
            res = self.mode_select_screen.handle_event(event)
            if res:
                mode_key, params = res
                if mode_key == "menu":
                    self.current_state = STATE_MENU
                elif mode_key == "difficulty_select":
                    self.current_state = STATE_DIFFICULTY_SELECT
                elif mode_key in ("ai_vs_ai_select", "ai_vs_ai"):
                    self.current_state = STATE_AI_VS_AI_SELECT
                else:
                    self._start_match(mode_key, params)

        elif self.current_state == STATE_AI_VS_AI_SELECT:
            res = self.ai_select_screen.handle_event(event)
            if res:
                action, params = res
                if action in ("mode_select", "menu"):
                    self.current_state = STATE_MODE_SELECT
                elif action == "ai_vs_ai":
                    self._start_match("ai_vs_ai", params)

        elif self.current_state == STATE_DIFFICULTY_SELECT:
            res = self.difficulty_select_screen.handle_event(event)
            if res:
                action, params = res
                if action in ("mode_select", "menu"):
                    self.current_state = STATE_MODE_SELECT
                elif action == "ai_vs_human":
                    self._start_match("ai_vs_human", params)

        elif self.current_state == STATE_GAME:
            action = self.game_screen.handle_event(event)
            if action == "menu":
                self.current_state = STATE_MENU

        elif self.current_state == STATE_ARENA:
            res = self.arena_screen.handle_event(event)
            if res:
                action, params = res
                if action == "menu":
                    self.current_state = STATE_MENU
                elif action == "ai_vs_ai":
                    self._start_match("ai_vs_ai", params)

        elif self.current_state == STATE_HOW_TO_PLAY:
            action = self.how_to_play_screen.handle_event(event)
            if action == "menu":
                self.current_state = STATE_MENU

        elif self.current_state == STATE_SETTINGS:
            action = self.settings_screen.handle_event(event)
            if action == "menu":
                self.current_state = STATE_MENU

    def _start_match(self, mode_name: str, params: dict) -> None:
        """Initializes a new match with the chosen controller and parameters."""
        self.last_mode_name = mode_name
        self.last_mode_params = params

        # Reload settings in engine
        self.engine.settings = self.settings_screen.settings
        self.engine.start_new_match()

        if mode_name == "ai_vs_ai":
            red_algo = params.get("red_algo", "Alpha-Beta Pruning")
            blue_algo = params.get("blue_algo", "Monte Carlo Tree Search (MCTS)")
            red_iter = params.get("red_mcts_iter", 1000)
            blue_iter = params.get("blue_mcts_iter", 1000)
            delay = params.get("delay_ms", self.engine.settings.get("ai_move_delay_ms", 350))
            controller = AIvsAIMode(
                self.engine,
                red_algorithm=red_algo,
                blue_algorithm=blue_algo,
                move_delay_ms=delay,
                red_mcts_iterations=red_iter,
                blue_mcts_iterations=blue_iter
            )

        elif mode_name == "ai_vs_human":
            diff = params.get("difficulty", "Medium")
            delay = self.engine.settings.get("ai_move_delay_ms", 300)
            controller = AIvsHumanMode(self.engine, human_team="blue", difficulty=diff, ai_delay_ms=delay)

        else:  # human_vs_human
            controller = HumanvsHumanMode(self.engine)

        self.game_screen = GameScreen(self.engine, controller, mode_name=mode_name)
        self.current_state = STATE_GAME
        self.sound_mgr.play("ability")

    def _update(self, dt: float) -> None:
        if self.current_state == STATE_MENU:
            self.menu_screen.update(dt)
        elif self.current_state == STATE_GAME and self.game_screen:
            self.game_screen.update(dt)

    def _render(self) -> None:
        if self.current_state == STATE_MENU:
            self.menu_screen.render(self.screen)
        elif self.current_state == STATE_MODE_SELECT:
            self.mode_select_screen.render(self.screen)
        elif self.current_state == STATE_AI_VS_AI_SELECT:
            self.ai_select_screen.render(self.screen)
        elif self.current_state == STATE_DIFFICULTY_SELECT:
            self.difficulty_select_screen.render(self.screen)
        elif self.current_state == STATE_GAME and self.game_screen:
            self.game_screen.render(self.screen)
            # Render game over modal if match has ended
            if self.engine.state.is_game_over:
                self.result_screen.render(self.screen, self.engine.state, self.engine.total_match_duration)
        elif self.current_state == STATE_ARENA:
            self.arena_screen.render(self.screen)
        elif self.current_state == STATE_HOW_TO_PLAY:
            self.how_to_play_screen.render(self.screen)
        elif self.current_state == STATE_SETTINGS:
            self.settings_screen.render(self.screen)


if __name__ == "__main__":
    app = ChaosChessApp()
    app.run()

