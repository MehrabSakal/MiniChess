"""
Tests for Last Move Visualization and Match Replay Feature
"""
import os
import pytest

# Use headless video driver for testing
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
from config import TEAM_BLUE, TEAM_RED, SCREEN_WIDTH, SCREEN_HEIGHT
from game.game_engine import GameEngine
from game.game_state import GameState, Move
from game.piece import Piece, KING, ROOK, PAWN
from ui.board_renderer import BoardRenderer
from ui.result_screen import ResultScreen
from ui.game_screen import GameScreen
from modes.human_vs_human import HumanvsHumanMode


@pytest.fixture(scope="module")
def pygame_setup():
    pygame.init()
    surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    yield surface
    pygame.quit()


def test_engine_records_last_move_and_history():
    engine = GameEngine()
    engine.start_new_match()
    assert len(engine.history_states) == 0

    # Get legal moves for blue
    legal_moves = engine.state.get_all_legal_moves()
    assert len(legal_moves) > 0
    move1 = legal_moves[0]

    engine.execute_move(move1)
    assert len(engine.history_states) == 1
    assert engine.state.last_move is not None
    assert engine.state.last_move.start_pos == move1.start_pos
    assert engine.state.last_move.end_pos == move1.end_pos


def test_board_renderer_renders_last_move_and_arrow(pygame_setup):
    surface = pygame_setup
    engine = GameEngine()
    engine.start_new_match()

    legal_moves = engine.state.get_all_legal_moves()
    move = legal_moves[0]
    engine.execute_move(move)

    renderer = BoardRenderer(origin_x=508, origin_y=35, tile_size=86)
    # Should render without throwing exceptions
    renderer.render(surface, engine.state)


def test_result_screen_buttons_and_events(pygame_setup):
    surface = pygame_setup
    screen = ResultScreen()
    state = GameState()
    state.is_game_over = True
    state.winner = "blue"
    state.victory_reason = "King Captured"
    state.last_move = Move(
        start_pos=(1, 1),
        end_pos=(0, 1),
        piece=Piece(ROOK, "blue", 1, 1),
        captured_piece=Piece(KING, "red", 0, 1)
    )

    # Render should succeed cleanly
    screen.render(surface, state, match_duration=42.5)

    # Click on "▶ REPLAY OF THE GAME"
    click_replay = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": screen.btn_replay.center})
    res_replay = screen.handle_event(click_replay)
    assert res_replay == "replay"

    # Click on "⌂ RETURN TO MAIN MENU"
    click_menu = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": screen.btn_menu.center})
    res_menu = screen.handle_event(click_menu)
    assert res_menu == "menu"

    # Keyboard shortcut 'r' or Return
    key_r = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_r})
    assert screen.handle_event(key_r) == "replay"

    key_esc = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_ESCAPE})
    assert screen.handle_event(key_esc) == "menu"


def test_game_screen_replay_mode_workflow(pygame_setup):
    surface = pygame_setup
    engine = GameEngine()
    engine.start_new_match()

    # Play two moves
    m1 = engine.state.get_all_legal_moves()[0]
    engine.execute_move(m1)
    m2 = engine.state.get_all_legal_moves()[0]
    engine.execute_move(m2)

    controller = HumanvsHumanMode(engine)
    game_screen = GameScreen(engine, controller, mode_name="human_vs_human")

    # Start Replay
    assert not game_screen.is_replay_mode
    game_screen.start_replay()
    assert game_screen.is_replay_mode
    assert len(game_screen.replay_states) == 3  # Initial + move 1 + move 2
    assert game_screen.replay_index == 0
    assert game_screen.replay_auto_playing

    # Step forward
    game_screen.replay_step_next()
    assert game_screen.replay_index == 1

    game_screen.replay_step_next()
    assert game_screen.replay_index == 2

    # Step back
    game_screen.replay_step_prev()
    assert game_screen.replay_index == 1

    # Render during replay
    game_screen.render(surface)

    # Click Replay Control Button: "play" toggles auto-play
    click_play = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": game_screen.replay_buttons["play"].center})
    game_screen.handle_event(click_play)

    # Click Replay Menu Button: exits replay and returns "menu"
    click_menu = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": game_screen.replay_buttons["menu"].center})
    action = game_screen.handle_event(click_menu)
    assert action == "menu"
    assert not game_screen.is_replay_mode
