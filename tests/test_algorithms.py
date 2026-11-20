"""
Unit tests for all 8 AI Algorithms
"""
import pytest
from config import TEAM_RED, TEAM_BLUE
from game.board import Board
from game.game_state import GameState
from ai.ai_controller import (
    AIController,
    ALL_ALGORITHMS,
    ALGORITHM_DFS,
    ALGORITHM_BEST_FIRST,
    ALGORITHM_BIDIRECTIONAL,
    ALGORITHM_MCTS,
    ALGORITHM_MINIMAX,
    ALGORITHM_ALPHA_BETA,
    ALGORITHM_FUZZY,
    ALGORITHM_CSP
)


@pytest.mark.parametrize("algo_name", ALL_ALGORITHMS)
def test_all_eight_algorithms_produce_legal_moves(algo_name):
    """Verify every single one of the 8 algorithms is functional and returns a valid move."""
    state = GameState()
    state.board.setup_standard_board()
    state.current_turn = TEAM_BLUE

    controller = AIController(algorithm_name=algo_name, team=TEAM_BLUE)
    move, metrics = controller.choose_move(state)

    assert move is not None, f"Algorithm {algo_name} returned None move!"
    assert metrics is not None
    assert "algorithm" in metrics
    assert "execution_time_ms" in metrics
    assert "nodes_explored" in metrics
    assert "eval_score" in metrics

    # Verify move is in legal moves
    legal_moves = state.get_all_legal_moves(TEAM_BLUE)
    assert any(
        m.start_pos == move.start_pos and m.end_pos == move.end_pos for m in legal_moves
    ), f"Algorithm {algo_name} returned illegal move {move.notation()}!"

