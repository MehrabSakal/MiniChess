"""
Unit tests for CSP Team Generator
"""
import pytest
from config import KING, TEAM_RED, TEAM_BLUE, PIECE_VALUES
from ai.csp import CSPTeamGenerator


def test_csp_team_generation_constraints():
    generator = CSPTeamGenerator(seed=42)

    for team in (TEAM_RED, TEAM_BLUE):
        solution = generator.solve_team(team)

        # 1. Exactly 8 pieces
        assert len(solution) == 8

        # 2. Exactly one King
        kings = [p for p in solution if p[2] == KING]
        assert len(kings) == 1

        # 3. Squares are distinct
        squares = {(r, c) for r, c, _ in solution}
        assert len(squares) == 8

        # 4. Correct starting rows
        target_rows = {0, 1} if team == TEAM_RED else {5, 6}
        for r, c, _ in solution:
            assert r in target_rows
            assert 0 <= c < 4

        # 5. Material balance
        total_mat = sum(PIECE_VALUES[p_type] for _, _, p_type in solution)
        assert 21000 <= total_mat <= 23000


def test_csp_balanced_board_creation():
    generator = CSPTeamGenerator(seed=123)
    board = generator.generate_balanced_board()

    assert len(board.get_team_pieces(TEAM_RED)) == 8
    assert len(board.get_team_pieces(TEAM_BLUE)) == 8
    assert len(board.get_all_pieces()) == 16


def test_csp_identical_pieces_and_equal_points():
    """Verifies both teams get the exact same pieces and 100% equal total points."""
    generator = CSPTeamGenerator()
    for _ in range(5):
        board = generator.generate_balanced_board(symmetric=True)
        red_pieces = sorted([p.piece_type for p in board.get_team_pieces(TEAM_RED)])
        blue_pieces = sorted([p.piece_type for p in board.get_team_pieces(TEAM_BLUE)])
        assert red_pieces == blue_pieces

        red_pts = sum(p.value for p in board.get_team_pieces(TEAM_RED))
        blue_pts = sum(p.value for p in board.get_team_pieces(TEAM_BLUE))
        assert red_pts == blue_pts

