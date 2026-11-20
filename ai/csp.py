"""
Chaos Chess - Constraint Satisfaction Problem (CSP) Team Generator
"""
import random
from typing import List, Dict, Tuple, Optional
from config import (
    ROWS, COLS,
    KING, QUEEN, ROOK, BISHOP, KNIGHT, PAWN,
    TEAM_RED, TEAM_BLUE, PIECE_VALUES
)
from game.piece import Piece
from game.board import Board


class CSPTeamGenerator:
    """
    CSP with Backtracking, Forward Checking and Variable Ordering (MRV)
    to generate fair, balanced, and diverse tactical starting armies.
    """

    # Domain piece constraints
    PIECE_LIMITS = {
        KING: (1, 1),      # Exactly 1 King
        QUEEN: (0, 1),     # Max 1 Queen
        ROOK: (1, 2),      # 1 to 2 Rooks
        BISHOP: (1, 2),    # 1 to 2 Bishops
        KNIGHT: (1, 3),    # 1 to 3 Knights
        PAWN: (2, 4)       # 2 to 4 Pawns
    }

    TARGET_MATERIAL_MIN = 21700
    TARGET_MATERIAL_MAX = 22600

    def __init__(self, seed: Optional[int] = None):
        if seed is not None:
            random.seed(seed)

    def solve_team(self, team: str) -> List[Tuple[int, int, str]]:
        """
        Solves CSP for 8 positions on assigned two rows.
        For Red: rows 0 (back) and 1 (front).
        For Blue: rows 6 (back) and 5 (front).
        Returns: list of (row, col, piece_type) tuples.
        """
        back_row = 0 if team == TEAM_RED else 6
        front_row = 1 if team == TEAM_RED else 5

        back_squares = [(back_row, c) for c in range(COLS)]
        front_squares = [(front_row, c) for c in range(COLS)]
        random.shuffle(back_squares)
        random.shuffle(front_squares)
        squares = back_squares + front_squares
        assert len(squares) == 8

        # Backtracking solver
        solution = self._backtrack(
            assignment={},
            remaining_squares=list(squares),
            piece_counts={k: 0 for k in self.PIECE_LIMITS.keys()},
            current_material=0,
            team=team
        )

        if solution:
            return [(r, c, p_type) for (r, c), p_type in solution.items()]
        else:
            # Fallback standard
            return self._fallback_standard(team)

    def _backtrack(
        self,
        assignment: Dict[Tuple[int, int], str],
        remaining_squares: List[Tuple[int, int]],
        piece_counts: Dict[str, int],
        current_material: int,
        team: str
    ) -> Optional[Dict[Tuple[int, int], str]]:
        # Base case: all 8 squares assigned
        if not remaining_squares:
            # Check complete constraints
            if piece_counts[KING] == 1 and self.TARGET_MATERIAL_MIN <= current_material <= self.TARGET_MATERIAL_MAX:
                return assignment
            return None

        # Pick next square (MRV / Backtracking variable ordering)
        sq = remaining_squares[0]
        rest = remaining_squares[1:]
        squares_left = len(rest) + 1

        # Domain options for this square
        domain = [KING, QUEEN, ROOK, BISHOP, KNIGHT, PAWN]
        random.shuffle(domain)

        # Forward checking heuristics:
        # Pawns go on the front row (row 1 for Red, row 5 for Blue)
        # King and Queen go on the back row (row 0 for Red, row 6 for Blue)
        is_front_row = (sq[0] == 1 if team == TEAM_RED else sq[0] == 5)

        for p_type in domain:
            min_cnt, max_cnt = self.PIECE_LIMITS[p_type]
            
            # Constraint 1: Piece count upper limit
            if piece_counts[p_type] >= max_cnt:
                continue

            # Constraint 2: Must place King before running out of squares
            if piece_counts[KING] == 0 and squares_left == 1 and p_type != KING:
                continue

            # Constraint 3: King and Queen must be protected on the back row
            if is_front_row and p_type in (KING, QUEEN):
                continue

            # Constraint 4: Pawns must be on the front row to advance into arena
            if not is_front_row and p_type == PAWN:
                continue

            # Forward check material sum bounds
            new_mat = current_material + PIECE_VALUES[p_type]
            max_possible_remaining = (squares_left - 1) * PIECE_VALUES[QUEEN]
            min_possible_remaining = (squares_left - 1) * PIECE_VALUES[PAWN]
            if new_mat + min_possible_remaining > self.TARGET_MATERIAL_MAX:
                continue
            if new_mat + max_possible_remaining < self.TARGET_MATERIAL_MIN and piece_counts[KING] > 0:
                continue

            # Assign
            assignment[sq] = p_type
            piece_counts[p_type] += 1

            # Recurse
            res = self._backtrack(assignment, rest, piece_counts, new_mat, team)
            if res is not None:
                return res

            # Backtrack
            del assignment[sq]
            piece_counts[p_type] -= 1

        return None

    def _fallback_standard(self, team: str) -> List[Tuple[int, int, str]]:
        back_row = 0 if team == TEAM_RED else 6
        front_row = 1 if team == TEAM_RED else 5
        return [
            (back_row, 0, ROOK), (back_row, 1, QUEEN), (back_row, 2, KING), (back_row, 3, BISHOP),
            (front_row, 0, KNIGHT), (front_row, 1, PAWN), (front_row, 2, PAWN), (front_row, 3, KNIGHT)
        ]

    def generate_balanced_board(self, symmetric: bool = True) -> Board:
        """
        Constructs a new 7x4 Board using CSP solutions for both teams.
        When symmetric=True (default), both players get the EXACT same piece set
        and identical total point values, mirrored on rows 5 and 6 for 100% fair play.
        """
        board = Board()
        red_setup = self.solve_team(TEAM_RED)

        if symmetric:
            # Blue receives the identical piece set and point values, mirrored on rows 5 and 6
            # Row 0 (Red back) -> Row 6 (Blue back)
            # Row 1 (Red front) -> Row 5 (Blue front)
            # Column c is preserved so pieces face directly across the board
            blue_setup = [(6 - r, c, p_type) for r, c, p_type in red_setup]
        else:
            blue_setup = self.solve_team(TEAM_BLUE)

        for r, c, p_type in red_setup:
            board.set_piece(r, c, Piece(p_type, TEAM_RED, r, c))

        for r, c, p_type in blue_setup:
            board.set_piece(r, c, Piece(p_type, TEAM_BLUE, r, c))

        return board

