"""
Chaos Chess - Victory and Termination Rules
"""
from typing import Optional, Tuple, List
from config import (
    ROWS, COLS, TOTAL_SQUARES,
    KING, TEAM_RED, TEAM_BLUE,
    VICTORY_ROYAL, VICTORY_ELIMINATION, VICTORY_DRAW,
    DEFAULT_TURN_LIMIT
)
from game.movement import get_piece_standard_moves


class VictoryChecker:
    """Evaluates all game end and victory conditions on a game state."""

    @staticmethod
    def calculate_board_control(game_state) -> Tuple[int, int]:
        """
        Calculate square control for (Red, Blue) over all 28 board squares.
        A square is controlled by team T if it exerts strictly more tactical influence 
        (presence + legal attack/move threats) on that square than the opponent.
        """
        red_influence = [[0 for _ in range(COLS)] for _ in range(ROWS)]
        blue_influence = [[0 for _ in range(COLS)] for _ in range(ROWS)]

        # 1. Piece presence
        for r in range(ROWS):
            for c in range(COLS):
                p = game_state.board[r][c]
                if p:
                    if p.team == TEAM_RED:
                        red_influence[r][c] += 2
                    else:
                        blue_influence[r][c] += 2

        # 2. Movement threats
        for p in game_state.get_alive_pieces():
            moves = get_piece_standard_moves(p, game_state.board.grid)
            for m in moves:
                tr, tc = m.end_pos
                if p.team == TEAM_RED:
                    red_influence[tr][tc] += 1
                else:
                    blue_influence[tr][tc] += 1

        red_controlled = 0
        blue_controlled = 0

        for r in range(ROWS):
            for c in range(COLS):
                if red_influence[r][c] > blue_influence[r][c]:
                    red_controlled += 1
                elif blue_influence[r][c] > red_influence[r][c]:
                    blue_controlled += 1

        return red_controlled, blue_controlled

    @classmethod
    def check_victory(
        cls,
        game_state,
        turn_limit: int = DEFAULT_TURN_LIMIT
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Evaluates whether match is over.
        Prioritizes:
        1. Royal Victory (Capture King)
        2. Elimination Victory (All opposing pieces eliminated)
        3. Turn Limit Reached (Points Lead or Draw)
        4. Stalemate (No Legal Moves)
        """
        red_pieces = game_state.get_team_pieces(TEAM_RED)
        blue_pieces = game_state.get_team_pieces(TEAM_BLUE)

        red_king_alive = any(p.piece_type == KING for p in red_pieces)
        blue_king_alive = any(p.piece_type == KING for p in blue_pieces)

        # 1. Royal Victory: If one team's King is captured while opponent has King/pieces alive
        if not red_king_alive and blue_king_alive:
            return True, TEAM_BLUE, VICTORY_ROYAL
        if not blue_king_alive and red_king_alive:
            return True, TEAM_RED, VICTORY_ROYAL

        # 2. Elimination Victory: check if an entire team is eliminated
        if len(red_pieces) == 0 and len(blue_pieces) == 0:
            return True, None, VICTORY_DRAW
        if len(red_pieces) == 0:
            return True, TEAM_BLUE, VICTORY_ELIMINATION
        if len(blue_pieces) == 0:
            return True, TEAM_RED, VICTORY_ELIMINATION

        # 3. Turn Limit Reached
        if game_state.turn_count >= turn_limit:
            red_val = sum(p.value for p in red_pieces)
            blue_val = sum(p.value for p in blue_pieces)
            if red_val > blue_val:
                return True, TEAM_RED, f"{VICTORY_DRAW} (Red Points Lead)"
            elif blue_val > red_val:
                return True, TEAM_BLUE, f"{VICTORY_DRAW} (Blue Points Lead)"
            return True, None, VICTORY_DRAW

        # 4. Stalemate: Current player has no legal moves
        current_moves = game_state.get_all_legal_moves()
        if len(current_moves) == 0:
            opp = TEAM_BLUE if game_state.current_turn == TEAM_RED else TEAM_RED
            return True, opp, "Stalemate / No Legal Moves"

        return False, None, None
