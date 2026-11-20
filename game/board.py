"""
Chaos Chess - 7x4 Board Model
"""
from typing import List, Optional, Tuple, Dict
from config import ROWS, COLS, TEAM_RED, TEAM_BLUE, KING, QUEEN, ROOK, BISHOP, KNIGHT, PAWN
from game.piece import Piece


class Board:
    """Represents the 7 rows x 4 columns tactical battlefield."""

    def __init__(self):
        # EXACT REQUIREMENT: 7 rows x 4 columns
        self.rows = ROWS
        self.cols = COLS
        self.grid: List[List[Optional[Piece]]] = [
            [None for _ in range(self.cols)] for _ in range(self.rows)
        ]

    def __getitem__(self, row: int) -> List[Optional[Piece]]:
        return self.grid[row]

    def get_piece(self, row: int, col: int) -> Optional[Piece]:
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.grid[row][col]
        return None

    def set_piece(self, row: int, col: int, piece: Optional[Piece]) -> None:
        if 0 <= row < self.rows and 0 <= col < self.cols:
            self.grid[row][col] = piece
            if piece is not None:
                piece.row = row
                piece.col = col

    def remove_piece(self, row: int, col: int) -> Optional[Piece]:
        p = self.get_piece(row, col)
        if p is not None:
            self.grid[row][col] = None
        return p

    def move_piece(self, start_pos: Tuple[int, int], end_pos: Tuple[int, int]) -> Optional[Piece]:
        """Move piece from start_pos to end_pos, returning any captured piece."""
        r1, c1 = start_pos
        r2, c2 = end_pos
        piece = self.remove_piece(r1, c1)
        if piece is None:
            return None
        captured = self.remove_piece(r2, c2)
        self.set_piece(r2, c2, piece)
        return captured

    def get_all_pieces(self) -> List[Piece]:
        pieces = []
        for r in range(self.rows):
            for c in range(self.cols):
                p = self.grid[r][c]
                if p is not None:
                    pieces.append(p)
        return pieces

    def get_team_pieces(self, team: str) -> List[Piece]:
        return [p for p in self.get_all_pieces() if p.team == team]

    def setup_standard_board(self) -> None:
        """
        Initializes the standard balanced starting arrangement:
        Red on Rows 0 and 1, Blue on Rows 5 and 6.
        Rows 2, 3, 4 are empty. Exactly 8 pieces per team.
        """
        # Clear grid
        self.grid = [[None for _ in range(self.cols)] for _ in range(self.rows)]

        # Red Team (Rows 0 and 1)
        # Row 0: Rook, Queen, King, Bishop
        self.set_piece(0, 0, Piece(ROOK, TEAM_RED, 0, 0, "red_rook_1"))
        self.set_piece(0, 1, Piece(QUEEN, TEAM_RED, 0, 1, "red_queen_1"))
        self.set_piece(0, 2, Piece(KING, TEAM_RED, 0, 2, "red_king_1"))
        self.set_piece(0, 3, Piece(BISHOP, TEAM_RED, 0, 3, "red_bishop_1"))

        # Row 1: Knight, Pawn, Pawn, Knight
        self.set_piece(1, 0, Piece(KNIGHT, TEAM_RED, 1, 0, "red_knight_1"))
        self.set_piece(1, 1, Piece(PAWN, TEAM_RED, 1, 1, "red_pawn_1"))
        self.set_piece(1, 2, Piece(PAWN, TEAM_RED, 1, 2, "red_pawn_2"))
        self.set_piece(1, 3, Piece(KNIGHT, TEAM_RED, 1, 3, "red_knight_2"))

        # Blue Team (Rows 5 and 6)
        # Row 5: Knight, Pawn, Pawn, Knight
        self.set_piece(5, 0, Piece(KNIGHT, TEAM_BLUE, 5, 0, "blue_knight_1"))
        self.set_piece(5, 1, Piece(PAWN, TEAM_BLUE, 5, 1, "blue_pawn_1"))
        self.set_piece(5, 2, Piece(PAWN, TEAM_BLUE, 5, 2, "blue_pawn_2"))
        self.set_piece(5, 3, Piece(KNIGHT, TEAM_BLUE, 5, 3, "blue_knight_2"))

        # Row 6: Rook, Queen, King, Bishop
        self.set_piece(6, 0, Piece(ROOK, TEAM_BLUE, 6, 0, "blue_rook_1"))
        self.set_piece(6, 1, Piece(QUEEN, TEAM_BLUE, 6, 1, "blue_queen_1"))
        self.set_piece(6, 2, Piece(KING, TEAM_BLUE, 6, 2, "blue_king_1"))
        self.set_piece(6, 3, Piece(BISHOP, TEAM_BLUE, 6, 3, "blue_bishop_1"))

    def clone(self) -> 'Board':
        new_board = Board()
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] is not None:
                    new_board.grid[r][c] = self.grid[r][c].clone()
        return new_board

