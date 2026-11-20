"""
Unit tests for Victory Conditions
"""
import pytest
from config import (
    KING, QUEEN, ROOK, PAWN,
    TEAM_RED, TEAM_BLUE,
    VICTORY_ROYAL, VICTORY_ELIMINATION
)
from game.board import Board
from game.piece import Piece
from game.game_state import GameState
from game.movement import Move
from game.victory import VictoryChecker


def test_royal_victory():
    """Capturing enemy King triggers Royal Victory."""
    state = GameState()
    # Red King at (0, 1), Blue Queen at (1, 1)
    red_king = Piece(KING, TEAM_RED, 0, 1)
    blue_queen = Piece(QUEEN, TEAM_BLUE, 1, 1)
    state.board.set_piece(0, 1, red_king)
    state.board.set_piece(1, 1, blue_queen)
    # Also add Blue King to ensure Blue is alive
    state.board.set_piece(6, 2, Piece(KING, TEAM_BLUE, 6, 2))

    state.current_turn = TEAM_BLUE
    capture_move = Move((1, 1), (0, 1), blue_queen, captured_piece=red_king)
    state.apply_move(capture_move)

    assert state.is_game_over
    assert state.winner == TEAM_BLUE
    assert state.victory_reason == VICTORY_ROYAL


def test_elimination_victory():
    """Eliminating all opposing pieces triggers Elimination Victory."""
    state = GameState()
    # Red pawn at (0, 0), Blue Rook at (1, 0)
    red_pawn = Piece(PAWN, TEAM_RED, 0, 0)
    blue_rook = Piece(ROOK, TEAM_BLUE, 1, 0)
    state.board.set_piece(0, 0, red_pawn)
    state.board.set_piece(1, 0, blue_rook)

    state.current_turn = TEAM_BLUE
    capture_move = Move((1, 0), (0, 0), blue_rook, captured_piece=red_pawn)
    state.apply_move(capture_move)

    assert state.is_game_over
    assert state.winner == TEAM_BLUE


def test_shield_blocks_capture():
    """A shielded piece survives attack, shield breaks."""
    state = GameState()
    red_king = Piece(KING, TEAM_RED, 0, 1)
    red_king.apply_shield("royal_shield")
    blue_queen = Piece(QUEEN, TEAM_BLUE, 1, 1)
    state.board.set_piece(0, 1, red_king)
    state.board.set_piece(1, 1, blue_queen)
    state.board.set_piece(6, 2, Piece(KING, TEAM_BLUE, 6, 2))

    state.current_turn = TEAM_BLUE
    capture_move = Move((1, 1), (0, 1), blue_queen, captured_piece=red_king)
    state.apply_move(capture_move)

    # King should still be alive on board, but shield broken!
    king_check = state.board.get_piece(0, 1)
    assert king_check is not None
    assert king_check.piece_type == KING
    assert not king_check.shielded
    assert not state.is_game_over


def test_no_domination_victory():
    """Dominating squares does NOT trigger match termination; domination victory is disabled."""
    state = GameState()
    # Blue has full army controlling board; Red has lone King in safe corner
    state.board.set_piece(0, 0, Piece(KING, TEAM_RED, 0, 0))
    state.board.set_piece(6, 3, Piece(KING, TEAM_BLUE, 6, 3))
    state.board.set_piece(3, 1, Piece(QUEEN, TEAM_BLUE, 3, 1))
    state.board.set_piece(3, 2, Piece(ROOK, TEAM_BLUE, 3, 2))
    state.board.set_piece(4, 1, Piece(ROOK, TEAM_BLUE, 4, 1))

    # Artificially set domination counters high
    state.blue_consecutive_domination = 10
    state.red_consecutive_domination = 10

    over, winner, reason = VictoryChecker.check_victory(state)
    assert not over
    assert winner is None
    assert reason is None

