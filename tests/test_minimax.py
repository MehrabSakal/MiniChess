"""
Unit tests for Minimax and Alpha-Beta Pruning
"""
import pytest
from config import TEAM_RED, TEAM_BLUE
from game.board import Board
from game.game_state import GameState
from ai.minimax import MinimaxSearcher
from ai.alpha_beta import AlphaBetaSearcher


def test_minimax_and_alpha_beta_consistency():
    state = GameState()
    state.board.setup_standard_board()
    state.current_turn = TEAM_BLUE

    minimax = MinimaxSearcher(depth=2)
    alpha_beta = AlphaBetaSearcher(depth=2)

    move_mm, metrics_mm = minimax.search(state, TEAM_BLUE)
    move_ab, metrics_ab = alpha_beta.search(state, TEAM_BLUE)

    assert move_mm is not None
    assert move_ab is not None
    assert metrics_mm["nodes_explored"] > 0
    assert metrics_ab["nodes_explored"] > 0
    # Alpha-beta should typically explore fewer or equal nodes
    assert metrics_ab["nodes_explored"] <= metrics_mm["nodes_explored"] + 5

