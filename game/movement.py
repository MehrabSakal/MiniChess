"""
Chaos Chess - Movement Rules and Move Representation
"""
from typing import List, Tuple, Optional, Any
from config import (
    ROWS, COLS,
    KING, QUEEN, ROOK, BISHOP, KNIGHT, PAWN,
    TEAM_RED, TEAM_BLUE,
    ABILITY_ROYAL_SHIELD, ABILITY_DOUBLE_STRIKE, ABILITY_FORTRESS,
    ABILITY_MAGIC_STEP, ABILITY_SUPER_JUMP, ABILITY_SACRIFICE,
    ABILITY_COSTS
)
from game.piece import Piece


class Move:
    """Represents a discrete tactical move or special ability action."""
    
    def __init__(
        self,
        start_pos: Tuple[int, int],
        end_pos: Tuple[int, int],
        piece: Piece,
        captured_piece: Optional[Piece] = None,
        is_promotion: bool = False,
        promoted_to: str = QUEEN,
        is_special_ability: bool = False,
        ability_name: Optional[str] = None,
        ability_target_pos: Optional[Tuple[int, int]] = None,
        secondary_move: Optional['Move'] = None
    ):
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.piece = piece
        self.captured_piece = captured_piece
        self.is_promotion = is_promotion
        self.promoted_to = promoted_to
        self.is_special_ability = is_special_ability
        self.ability_name = ability_name
        self.ability_target_pos = ability_target_pos
        self.secondary_move = secondary_move
        
    @property
    def is_capture(self) -> bool:
        return self.captured_piece is not None

    def notation(self) -> str:
        """Readable notation, e.g. 'N c1->b3' or 'P a2->a3 (Promo Q)' or '[Ability] K: Royal Shield'"""
        col_letters = "abcd"
        r1, c1 = self.start_pos
        r2, c2 = self.end_pos
        start_sq = f"{col_letters[c1]}{ROWS - r1}"
        end_sq = f"{col_letters[c2]}{ROWS - r2}"
        
        piece_char = self.piece.piece_type[0].upper()
        if self.piece.piece_type == KNIGHT:
            piece_char = 'N'
            
        if self.is_special_ability:
            if self.ability_target_pos:
                tr, tc = self.ability_target_pos
                tgt_sq = f"{col_letters[tc]}{ROWS - tr}"
                return f"[{self.ability_name}] {piece_char}@{start_sq} -> {tgt_sq}"
            return f"[{self.ability_name}] {piece_char}@{start_sq}->{end_sq}"
            
        action = "x" if self.captured_piece else "->"
        s = f"{piece_char} {start_sq}{action}{end_sq}"
        if self.is_promotion:
            s += f"={self.promoted_to[0].upper()}"
        return s

    def __repr__(self) -> str:
        return f"<Move {self.notation()}>"

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Move):
            return False
        return (
            self.start_pos == other.start_pos and
            self.end_pos == other.end_pos and
            self.is_special_ability == other.is_special_ability and
            self.ability_name == other.ability_name and
            self.ability_target_pos == other.ability_target_pos
        )


def is_in_bounds(row: int, col: int) -> bool:
    """Check if coordinates fall within 7 rows x 4 cols."""
    return 0 <= row < ROWS and 0 <= col < COLS


def get_piece_standard_moves(piece: Piece, board: List[List[Optional[Piece]]]) -> List[Move]:
    """Calculate all standard legal moves for a given piece on the board."""
    if piece.frozen_turns > 0:
        return []
        
    moves: List[Move] = []
    r, c = piece.row, piece.col
    team = piece.team

    # 1. KING (1 square any direction)
    if piece.piece_type == KING:
        directions = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1)
        ]
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if is_in_bounds(nr, nc):
                target = board[nr][nc]
                if target is None:
                    moves.append(Move((r, c), (nr, nc), piece))
                elif target.team != team:
                    moves.append(Move((r, c), (nr, nc), piece, captured_piece=target))

    # 2. QUEEN (Straight and diagonal rays)
    elif piece.piece_type == QUEEN:
        directions = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1)
        ]
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            while is_in_bounds(nr, nc):
                target = board[nr][nc]
                if target is None:
                    moves.append(Move((r, c), (nr, nc), piece))
                elif target.team != team:
                    moves.append(Move((r, c), (nr, nc), piece, captured_piece=target))
                    break
                else:
                    break
                nr += dr
                nc += dc

    # 3. ROOK (Straight rays)
    elif piece.piece_type == ROOK:
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            while is_in_bounds(nr, nc):
                target = board[nr][nc]
                if target is None:
                    moves.append(Move((r, c), (nr, nc), piece))
                elif target.team != team:
                    moves.append(Move((r, c), (nr, nc), piece, captured_piece=target))
                    break
                else:
                    break
                nr += dr
                nc += dc

    # 4. BISHOP (Diagonal rays)
    elif piece.piece_type == BISHOP:
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            while is_in_bounds(nr, nc):
                target = board[nr][nc]
                if target is None:
                    moves.append(Move((r, c), (nr, nc), piece))
                elif target.team != team:
                    moves.append(Move((r, c), (nr, nc), piece, captured_piece=target))
                    break
                else:
                    break
                nr += dr
                nc += dc

    # 5. KNIGHT (L-shaped jumps)
    elif piece.piece_type == KNIGHT:
        offsets = [
            (-2, -1), (-2, 1),
            (-1, -2), (-1, 2),
            (1, -2),  (1, 2),
            (2, -1),  (2, 1)
        ]
        for dr, dc in offsets:
            nr, nc = r + dr, c + dc
            if is_in_bounds(nr, nc):
                target = board[nr][nc]
                if target is None:
                    moves.append(Move((r, c), (nr, nc), piece))
                elif target.team != team:
                    moves.append(Move((r, c), (nr, nc), piece, captured_piece=target))

    # 6. PAWN (Forward move, diagonal capture, promotion)
    elif piece.piece_type == PAWN:
        forward_dr = 1 if team == TEAM_RED else -1
        promo_row = 6 if team == TEAM_RED else 0

        # Step forward
        nr = r + forward_dr
        nc = c
        if is_in_bounds(nr, nc) and board[nr][nc] is None:
            is_promo = (nr == promo_row)
            moves.append(Move((r, c), (nr, nc), piece, is_promotion=is_promo))

        # Diagonal captures
        for dc in (-1, 1):
            nr = r + forward_dr
            nc = c + dc
            if is_in_bounds(nr, nc):
                target = board[nr][nc]
                if target is not None and target.team != team:
                    is_promo = (nr == promo_row)
                    moves.append(Move((r, c), (nr, nc), piece, captured_piece=target, is_promotion=is_promo))

    return moves


def get_piece_ability_moves(
    piece: Piece,
    board: List[List[Optional[Piece]]],
    current_energy: int,
    ability_used_this_turn: bool = False
) -> List[Move]:
    """
    Generate special ability moves for a piece if energy and conditions allow.
    """
    if ability_used_this_turn or not piece.can_use_ability():
        return []

    cost = ABILITY_COSTS.get(piece.special_ability, 99)
    if current_energy < cost:
        return []

    r, c = piece.row, piece.col
    team = piece.team
    moves: List[Move] = []

    # KING: Royal Shield
    # Protects King from next capture. Self-activation in place.
    if piece.piece_type == KING and not piece.shielded:
        moves.append(Move(
            start_pos=(r, c),
            end_pos=(r, c),
            piece=piece,
            is_special_ability=True,
            ability_name=ABILITY_ROYAL_SHIELD
        ))

    # QUEEN: Double Strike
    # Any capture by the Queen can trigger Double Strike, which allows striking a second enemy piece.
    elif piece.piece_type == QUEEN:
        # Check standard captures; each capture can be upgraded to Double Strike
        directions = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1)
        ]
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            while is_in_bounds(nr, nc):
                target = board[nr][nc]
                if target is None:
                    pass
                elif target.team != team:
                    # Found first capture target. Check if there are other adjacent enemies from target pos
                    moves.append(Move(
                        start_pos=(r, c),
                        end_pos=(nr, nc),
                        piece=piece,
                        captured_piece=target,
                        is_special_ability=True,
                        ability_name=ABILITY_DOUBLE_STRIKE
                    ))
                    break
                else:
                    break
                nr += dr
                nc += dc

    # ROOK: Fortress
    # Protects an adjacent friendly piece with a shield
    elif piece.piece_type == ROOK:
        adjacents = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1)
        ]
        for dr, dc in adjacents:
            nr, nc = r + dr, c + dc
            if is_in_bounds(nr, nc):
                target = board[nr][nc]
                if target is not None and target.team == team and not target.shielded:
                    moves.append(Move(
                        start_pos=(r, c),
                        end_pos=(r, c),
                        piece=piece,
                        is_special_ability=True,
                        ability_name=ABILITY_FORTRESS,
                        ability_target_pos=(nr, nc)
                    ))

    # BISHOP: Magic Step
    # Special diagonal teleport: can jump diagonally 2 squares, phasing over any intermediate piece!
    elif piece.piece_type == BISHOP:
        diag_offsets = [(-2, -2), (-2, 2), (2, -2), (2, 2)]
        for dr, dc in diag_offsets:
            nr, nc = r + dr, c + dc
            if is_in_bounds(nr, nc):
                target = board[nr][nc]
                if target is None:
                    moves.append(Move(
                        start_pos=(r, c),
                        end_pos=(nr, nc),
                        piece=piece,
                        is_special_ability=True,
                        ability_name=ABILITY_MAGIC_STEP
                    ))
                elif target.team != team:
                    moves.append(Move(
                        start_pos=(r, c),
                        end_pos=(nr, nc),
                        piece=piece,
                        captured_piece=target,
                        is_special_ability=True,
                        ability_name=ABILITY_MAGIC_STEP
                    ))

    # KNIGHT: Super Jump
    # Extended 3-step jump: (3, 1), (3, -1), (-3, 1), (-3, -1), (1, 3), (1, -3), (-1, 3), (-1, -3)
    elif piece.piece_type == KNIGHT:
        super_offsets = [
            (-3, -1), (-3, 1),
            (-1, -3), (-1, 3),
            (1, -3),  (1, 3),
            (3, -1),  (3, 1)
        ]
        for dr, dc in super_offsets:
            nr, nc = r + dr, c + dc
            if is_in_bounds(nr, nc):
                target = board[nr][nc]
                if target is None:
                    moves.append(Move(
                        start_pos=(r, c),
                        end_pos=(nr, nc),
                        piece=piece,
                        is_special_ability=True,
                        ability_name=ABILITY_SUPER_JUMP
                    ))
                elif target.team != team:
                    moves.append(Move(
                        start_pos=(r, c),
                        end_pos=(nr, nc),
                        piece=piece,
                        captured_piece=target,
                        is_special_ability=True,
                        ability_name=ABILITY_SUPER_JUMP
                    ))

    # PAWN: Sacrifice
    # Sacrifices itself to grant a permanent Fortress shield to an adjacent friendly piece
    elif piece.piece_type == PAWN:
        adjacents = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1)
        ]
        for dr, dc in adjacents:
            nr, nc = r + dr, c + dc
            if is_in_bounds(nr, nc):
                target = board[nr][nc]
                if target is not None and target.team == team and not target.shielded:
                    moves.append(Move(
                        start_pos=(r, c),
                        end_pos=(nr, nc),
                        piece=piece,
                        is_special_ability=True,
                        ability_name=ABILITY_SACRIFICE,
                        ability_target_pos=(nr, nc)
                    ))

    return moves

