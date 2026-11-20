"""
Chaos Chess - Tactical Heuristic Evaluation Engine
"""
from typing import Dict, List, Tuple
from config import (
    ROWS, COLS,
    KING, QUEEN, ROOK, BISHOP, KNIGHT, PAWN,
    TEAM_RED, TEAM_BLUE, PIECE_VALUES
)
from game.movement import get_piece_standard_moves

# Positional Piece-Square Tables optimized for 7 rows x 4 columns board
# Rows 0-6, Cols 0-3. Higher values = more advantageous square.

PAWN_TABLE_BLUE = [
    [100, 100, 100, 100],  # Row 0 (Promotion!)
    [50,  60,  60,  50],   # Row 1
    [20,  30,  30,  20],   # Row 2
    [10,  20,  20,  10],   # Row 3 (Arena Center)
    [ 5,  10,  10,   5],   # Row 4
    [ 0,   0,   0,   0],   # Row 5 (Starting front)
    [ 0,   0,   0,   0],   # Row 6 (Starting back)
]

# For Red, the board is mirrored vertically
PAWN_TABLE_RED = list(reversed(PAWN_TABLE_BLUE))

KNIGHT_TABLE = [
    [-10, -5, -5, -10],
    [ -5, 10, 10,  -5],
    [  0, 20, 20,   0],
    [  5, 25, 25,   5],
    [  0, 20, 20,   0],
    [ -5, 10, 10,  -5],
    [-10, -5, -5, -10],
]

KING_SAFETY_TABLE_BLUE = [
    [-40, -40, -40, -40],
    [-20, -20, -20, -20],
    [-10, -10, -10, -10],
    [  0,   0,   0,   0],
    [ 10,  10,  10,  10],
    [ 20,  20,  20,  20],
    [ 30,  35,  35,  30],  # King is safest on back row
]

KING_SAFETY_TABLE_RED = list(reversed(KING_SAFETY_TABLE_BLUE))


def evaluate_board(game_state, perspective_team: str) -> float:
    """
    Comprehensive heuristic evaluation function.
    Returns positive score if perspective_team is winning, negative if losing.
    """
    if game_state.is_game_over:
        if game_state.winner == perspective_team:
            return 100000.0
        elif game_state.winner is not None:
            return -100000.0
        else:
            return 0.0

    score = 0.0
    opponent_team = TEAM_BLUE if perspective_team == TEAM_RED else TEAM_RED

    red_material = 0
    blue_material = 0
    red_pos_bonus = 0
    blue_pos_bonus = 0

    red_king_pos = None
    blue_king_pos = None

    for p in game_state.get_alive_pieces():
        val = p.value
        r, c = p.row, p.col

        # Positional bonuses
        pos_val = 0
        if p.piece_type == PAWN:
            pos_val = PAWN_TABLE_RED[r][c] if p.team == TEAM_RED else PAWN_TABLE_BLUE[r][c]
        elif p.piece_type == KNIGHT:
            pos_val = KNIGHT_TABLE[r][c]
        elif p.piece_type == KING:
            pos_val = KING_SAFETY_TABLE_RED[r][c] if p.team == TEAM_RED else KING_SAFETY_TABLE_BLUE[r][c]
            if p.team == TEAM_RED:
                red_king_pos = (r, c)
            else:
                blue_king_pos = (r, c)
        elif p.piece_type == QUEEN:
            # Queen favors active center control
            if 1 <= r <= 5 and 1 <= c <= 2:
                pos_val = 20

        # Shield defense bonus
        if p.shielded:
            pos_val += 40

        if p.team == TEAM_RED:
            red_material += val
            red_pos_bonus += pos_val
        else:
            blue_material += val
            blue_pos_bonus += pos_val

    # Material & position delta
    if perspective_team == TEAM_RED:
        score += (red_material - blue_material)
        score += (red_pos_bonus - blue_pos_bonus)
    else:
        score += (blue_material - red_material)
        score += (blue_pos_bonus - red_pos_bonus)

    # Energy difference
    p_energy = game_state.energy_system.get_energy(perspective_team)
    o_energy = game_state.energy_system.get_energy(opponent_team)
    score += (p_energy - o_energy) * 15.0

    # Mobility & Board Control
    p_moves = len(game_state.get_all_legal_moves(perspective_team))
    o_moves = len(game_state.get_all_legal_moves(opponent_team))
    score += (p_moves - o_moves) * 4.0

    # Domination streak bonus
    if perspective_team == TEAM_RED:
        score += game_state.red_consecutive_domination * 50.0
        score -= game_state.blue_consecutive_domination * 50.0
    else:
        score += game_state.blue_consecutive_domination * 50.0
        score -= game_state.red_consecutive_domination * 50.0

    return score

