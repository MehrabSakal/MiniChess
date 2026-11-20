"""
Unit tests for piece movement and board geometry
"""
import pytest
from config import (
    ROWS, COLS,
    KING, QUEEN, ROOK, BISHOP, KNIGHT, PAWN,
    TEAM_RED, TEAM_BLUE
)
from game.board import Board
from game.piece import Piece
from game.movement import get_piece_standard_moves, Move, is_in_bounds
from game.game_state import GameState


def test_board_dimensions():
    """Verify exact 7 rows x 4 cols geometry and 8 pieces per team."""
    board = Board()
    assert board.rows == 7
    assert board.cols == 4
    assert len(board.grid) == 7
    assert len(board.grid[0]) == 4

    board.setup_standard_board()
    red_pieces = board.get_team_pieces(TEAM_RED)
    blue_pieces = board.get_team_pieces(TEAM_BLUE)

    assert len(red_pieces) == 8
    assert len(blue_pieces) == 8
    assert len(board.get_all_pieces()) == 16

    # Verify rows 2, 3, 4 are empty
    for r in (2, 3, 4):
        for c in range(4):
            assert board.get_piece(r, c) is None


def test_knight_jumping():
    """Knight can jump over obstacles."""
    board = Board()
    knight = Piece(KNIGHT, TEAM_BLUE, 5, 1)
    board.set_piece(5, 1, knight)
    # Surround knight with friendly pawns
    board.set_piece(4, 1, Piece(PAWN, TEAM_BLUE, 4, 1))
    board.set_piece(5, 2, Piece(PAWN, TEAM_BLUE, 5, 2))

    moves = get_piece_standard_moves(knight, board.grid)
    end_positions = [m.end_pos for m in moves]
    # Possible knight moves from (5,1): (3,0), (3,2), (4,3), (6,3) if in bounds
    assert (3, 0) in end_positions
    assert (3, 2) in end_positions


def test_pawn_forward_and_capture():
    """Pawns move forward 1 square, capture diagonally forward."""
    board = Board()
    red_pawn = Piece(PAWN, TEAM_RED, 1, 1)
    board.set_piece(1, 1, red_pawn)

    # Empty target forward
    moves = get_piece_standard_moves(red_pawn, board.grid)
    assert len(moves) == 1
    assert moves[0].end_pos == (2, 1)
    assert not moves[0].is_capture

    # Add enemy diagonal target
    enemy = Piece(PAWN, TEAM_BLUE, 2, 2)
    board.set_piece(2, 2, enemy)
    moves = get_piece_standard_moves(red_pawn, board.grid)
    end_positions = [m.end_pos for m in moves]
    assert (2, 1) in end_positions
    assert (2, 2) in end_positions


def test_pawn_promotion():
    """Blue pawn reaching row 0 gets promoted to Queen."""
    state = GameState()
    blue_pawn = Piece(PAWN, TEAM_BLUE, 1, 0)
    state.board.set_piece(1, 0, blue_pawn)
    state.current_turn = TEAM_BLUE

    move = Move((1, 0), (0, 0), blue_pawn, is_promotion=True, promoted_to=QUEEN)
    state.apply_move(move)

    promoted_piece = state.board.get_piece(0, 0)
    assert promoted_piece is not None
    assert promoted_piece.piece_type == QUEEN

