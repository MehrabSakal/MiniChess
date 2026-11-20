"""
Integration tests verifying all screens, mode controllers, and game transitions
"""
import os
import pytest

# Use headless video driver for testing
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
from config import TEAM_RED, TEAM_BLUE
from game.game_engine import GameEngine
from modes.ai_vs_ai import AIvsAIMode
from modes.ai_vs_human import AIvsHumanMode
from modes.human_vs_human import HumanvsHumanMode
from ui.menu import MainMenu
from ui.mode_select import ModeSelectScreen
from ui.difficulty_select import DifficultySelectScreen
from ui.game_screen import GameScreen
from ui.arena_screen import ArenaScreen
from ui.how_to_play import HowToPlayScreen
from ui.settings import SettingsScreen
from ui.result_screen import ResultScreen
from ai.ai_controller import AIController, ALGORITHM_MINIMAX, ALGORITHM_MCTS
from main import ChaosChessApp


@pytest.fixture(scope="module")
def pygame_setup():
    pygame.init()
    surface = pygame.display.set_mode((1360, 768))
    yield surface
    pygame.quit()


def test_main_menu_render(pygame_setup):
    surface = pygame_setup
    menu = MainMenu()
    menu.update(0.016)
    menu.render(surface)


def test_mode_select_render(pygame_setup):
    surface = pygame_setup
    screen = ModeSelectScreen()
    screen.render(surface)


def test_arena_screen_benchmark_and_render(pygame_setup):
    surface = pygame_setup
    arena = ArenaScreen()
    arena.render(surface)
    assert arena.chart_surface is not None


def test_how_to_play_render_all_tabs(pygame_setup):
    surface = pygame_setup
    screen = HowToPlayScreen()
    for idx in range(len(screen.tabs)):
        screen.active_tab_idx = idx
        screen.render(surface)


def test_settings_screen_render(pygame_setup):
    surface = pygame_setup
    screen = SettingsScreen()
    screen.render(surface)


def test_ai_vs_ai_mode_execution(pygame_setup):
    surface = pygame_setup
    engine = GameEngine()
    engine.start_new_match()
    controller = AIvsAIMode(engine, move_delay_ms=0)
    game_screen = GameScreen(engine, controller, mode_name="ai_vs_ai")

    # Force step through 2 turns
    controller.request_step()
    controller.update()
    game_screen.render(surface)

    controller.request_step()
    controller.update()
    game_screen.render(surface)

    assert len(engine.state.move_history) >= 1


def test_ai_vs_human_mode_execution(pygame_setup):
    surface = pygame_setup
    engine = GameEngine()
    engine.start_new_match()
    controller = AIvsHumanMode(engine, human_team=TEAM_BLUE, difficulty="Easy", ai_delay_ms=0)
    game_screen = GameScreen(engine, controller, mode_name="ai_vs_human")

    # Blue is human. Execute a valid move.
    legal_moves = engine.get_legal_moves()
    assert len(legal_moves) > 0
    engine.execute_move(legal_moves[0])

    # Now it's Red's turn (AI). Trigger AI step.
    controller.update()
    game_screen.render(surface)


def test_human_vs_human_mode_execution(pygame_setup):
    surface = pygame_setup
    engine = GameEngine()
    engine.start_new_match()
    controller = HumanvsHumanMode(engine)
    game_screen = GameScreen(engine, controller, mode_name="human_vs_human")

    # Move 1 (Blue)
    m1 = engine.get_legal_moves()[0]
    engine.execute_move(m1)

    # Move 2 (Red)
    m2 = engine.get_legal_moves()[0]
    engine.execute_move(m2)

    game_screen.render(surface)
    assert len(engine.state.move_history) == 2

    # Test Undo
    assert engine.undo_last_move()
    assert len(engine.state.move_history) == 1


def test_result_screen_render(pygame_setup):
    surface = pygame_setup
    engine = GameEngine()
    engine.start_new_match()
    engine.state.is_game_over = True
    engine.state.winner = "blue"
    engine.state.victory_reason = "Royal Victory"

    res = ResultScreen()
    res.render(surface, engine.state, match_duration=42.5)


def test_piece_hover_tooltip(pygame_setup):
    surface = pygame_setup
    engine = GameEngine()
    engine.start_new_match()
    controller = HumanvsHumanMode(engine)
    game_screen = GameScreen(engine, controller, mode_name="human_vs_human")

    # Hover over Blue King at (6, 2)
    px, py = game_screen.board_renderer.get_pixel_pos(6, 2)
    game_screen._render_piece_hover_tooltip(surface, px + 20, py + 20, (6, 2))

    # Hover over Red Queen at (0, 1)
    px, py = game_screen.board_renderer.get_pixel_pos(0, 1)
    game_screen._render_piece_hover_tooltip(surface, px + 20, py + 20, (0, 1))

    # Hover over empty square (3, 1)
    game_screen._render_piece_hover_tooltip(surface, 500, 300, (3, 1))


def test_difficulty_selection_screen_render(pygame_setup):
    surface = pygame_setup
    diff_screen = DifficultySelectScreen()
    diff_screen.render(surface)
    assert "High" in diff_screen.cards
    assert "Medium" in diff_screen.cards
    assert "Low" in diff_screen.cards


def test_difficulty_ai_controller_configurations():
    # High -> Minimax
    ai_high = AIController.create_for_difficulty("High", TEAM_RED)
    assert ai_high.algorithm_name == ALGORITHM_MINIMAX

    # Medium -> MCTS with 1000 iterations
    ai_med = AIController.create_for_difficulty("Medium", TEAM_RED)
    assert ai_med.algorithm_name == ALGORITHM_MCTS
    assert ai_med.mcts_engine.simulation_budget == 1000

    # Low -> MCTS with 400 iterations
    ai_low = AIController.create_for_difficulty("Low", TEAM_RED)
    assert ai_low.algorithm_name == ALGORITHM_MCTS
    assert ai_low.mcts_engine.simulation_budget == 400


def test_mode_select_transitions_to_difficulty_select():
    screen = ModeSelectScreen()
    rect = screen.cards["ai_vs_human"]
    ev = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": (rect.centerx, rect.centery)})
    result = screen.handle_event(ev)
    assert result is not None
    assert result[0] == "difficulty_select"


def test_app_flow_human_vs_ai_difficulty(pygame_setup):
    app = ChaosChessApp()
    app.current_state = "mode_select"

    # Click AI vs Human
    rect = app.mode_select_screen.cards["ai_vs_human"]
    ev = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": (rect.centerx, rect.centery)})
    app._handle_event(ev)
    assert app.current_state == "difficulty_select"

    # Select High Difficulty on Difficulty Screen
    rect_high = app.difficulty_select_screen.cards["High"]
    ev_high = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": (rect_high.centerx, rect_high.centery)})
    app._handle_event(ev_high)
    assert app.current_state == "game"
    assert app.last_mode_name == "ai_vs_human"
    assert app.last_mode_params["difficulty"] == "High"
    assert app.game_screen.mode_controller.ai.algorithm_name == ALGORITHM_MINIMAX

