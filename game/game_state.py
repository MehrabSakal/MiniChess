"""
Chaos Chess - Game State Model
"""
from typing import List, Optional, Tuple, Dict, Any
from config import (
    ROWS, COLS,
    KING, QUEEN, ROOK, BISHOP, KNIGHT, PAWN,
    TEAM_RED, TEAM_BLUE,
    ABILITY_ROYAL_SHIELD, ABILITY_DOUBLE_STRIKE, ABILITY_FORTRESS,
    ABILITY_MAGIC_STEP, ABILITY_SUPER_JUMP, ABILITY_SACRIFICE,
    ABILITY_COSTS,
    DOMINATION_SQUARES_REQUIRED, DEFAULT_TURN_LIMIT
)
from game.piece import Piece
from game.board import Board
from game.movement import Move, get_piece_standard_moves, get_piece_ability_moves, is_in_bounds
from game.energy_system import EnergySystem
from game.battlefield import BattlefieldManager
from game.victory import VictoryChecker


class GameState:
    """Complete, self-contained snapshot of the match."""

    def __init__(self, board: Optional[Board] = None):
        self.board: Board = board or Board()
        self.current_turn: str = TEAM_BLUE  # Blue moves first by convention
        self.energy_system: EnergySystem = EnergySystem()
        self.battlefield_mgr: BattlefieldManager = BattlefieldManager()
        
        # Match statistics
        self.move_history: List[Move] = []
        self.captured_pieces: Dict[str, List[Piece]] = {
            TEAM_RED: [],   # Pieces captured BY red
            TEAM_BLUE: []   # Pieces captured BY blue
        }
        self.turn_count: int = 1
        self.ability_used_this_turn: bool = False
        
        # Domination tracking
        self.red_consecutive_domination: int = 0
        self.blue_consecutive_domination: int = 0
        
        # Termination
        self.is_game_over: bool = False
        self.winner: Optional[str] = None
        self.victory_reason: Optional[str] = None
        self.last_move: Optional[Move] = None

    def get_alive_pieces(self) -> List[Piece]:
        return self.board.get_all_pieces()

    def get_team_pieces(self, team: str) -> List[Piece]:
        return self.board.get_team_pieces(team)

    def get_opponent_team(self, team: Optional[str] = None) -> str:
        t = team or self.current_turn
        return TEAM_RED if t == TEAM_BLUE else TEAM_BLUE

    def get_all_legal_moves(self, team: Optional[str] = None) -> List[Move]:
        """Returns all legal moves for current team (or specified team)."""
        active_team = team or self.current_turn
        moves: List[Move] = []
        team_pieces = self.get_team_pieces(active_team)
        current_energy = self.energy_system.get_energy(active_team)

        for p in team_pieces:
            # 1. Standard moves
            std_moves = get_piece_standard_moves(p, self.board.grid)
            moves.extend(std_moves)

            # 2. Ability moves (if team hasn't used an ability yet this turn)
            if not self.ability_used_this_turn:
                ab_moves = get_piece_ability_moves(
                    p, self.board.grid, current_energy, self.ability_used_this_turn
                )
                moves.extend(ab_moves)

        return moves

    def apply_move(self, move: Move) -> 'GameState':
        """
        Executes a move or ability action on this state, updates energy,
        battlefield effects, domination counters, and evaluates victory.
        Safely operates on self.board pieces to prevent mutating foreign states.
        """
        if self.is_game_over:
            return self

        r1, c1 = move.start_pos
        actor = self.board.get_piece(r1, c1)
        if not actor:
            return self

        team = actor.team
        self.last_move = move
        self.move_history.append(move)

        # 1. Handle Special Abilities
        if move.is_special_ability:
            self.ability_used_this_turn = True
            cost = ABILITY_COSTS.get(move.ability_name, 0)
            self.energy_system.spend(team, cost)
            actor.mark_ability_used()

            if move.ability_name == ABILITY_ROYAL_SHIELD:
                actor.apply_shield("royal_shield")

            elif move.ability_name == ABILITY_FORTRESS:
                if move.ability_target_pos:
                    tr, tc = move.ability_target_pos
                    ally = self.board.get_piece(tr, tc)
                    if ally and ally.team == team:
                        ally.apply_shield("fortress")

            elif move.ability_name == ABILITY_SACRIFICE:
                if move.ability_target_pos:
                    tr, tc = move.ability_target_pos
                    ally = self.board.get_piece(tr, tc)
                    if ally and ally.team == team:
                        ally.apply_shield("sacrifice")
                # Remove sacrificing pawn from board
                self.board.remove_piece(r1, c1)

            elif move.ability_name in (ABILITY_MAGIC_STEP, ABILITY_SUPER_JUMP):
                self._execute_movement_and_capture(move, actor)

            elif move.ability_name == ABILITY_DOUBLE_STRIKE:
                self._execute_movement_and_capture(move, actor)
                # Auto-check if Queen can strike a second enemy adjacent to landing spot
                self._execute_secondary_strike(actor)

        # 2. Handle Standard Moves
        else:
            self._execute_movement_and_capture(move, actor)

        # 3. Check Pawn Promotion
        dest_piece = self.board.get_piece(move.end_pos[0], move.end_pos[1])
        if move.is_promotion and dest_piece:
            if dest_piece.piece_type == PAWN:
                dest_piece.piece_type = move.promoted_to or QUEEN

        # 4. Update Battlefield Environmental Effects
        self.battlefield_mgr.on_turn_end(self)
        self.battlefield_mgr.check_and_trigger_event(self.turn_count, self)

        # 5. Decrement frozen turns for pieces of next player
        next_team = self.get_opponent_team(team)
        for p in self.get_team_pieces(next_team):
            if p.frozen_turns > 0:
                p.frozen_turns -= 1

        # 6. Update Domination Counters
        red_ctrl, blue_ctrl = VictoryChecker.calculate_board_control(self)
        if red_ctrl >= DOMINATION_SQUARES_REQUIRED:
            self.red_consecutive_domination += 1
        else:
            self.red_consecutive_domination = 0

        if blue_ctrl >= DOMINATION_SQUARES_REQUIRED:
            self.blue_consecutive_domination += 1
        else:
            self.blue_consecutive_domination = 0

        # 7. Advance Turn
        self.current_turn = next_team
        self.ability_used_this_turn = False
        self.turn_count += 1

        # 8. Evaluate Victory Conditions
        over, winner, reason = VictoryChecker.check_victory(self)
        if over:
            self.is_game_over = True
            self.winner = winner
            self.victory_reason = reason

        return self

    def _execute_movement_and_capture(self, move: Move, actor: Piece) -> None:
        """Internal helper for standard movement and capture resolution."""
        r1, c1 = move.start_pos
        r2, c2 = move.end_pos
        team = actor.team

        # If start and end are same, no movement needed
        if (r1, c1) == (r2, c2):
            return

        target = self.board.get_piece(r2, c2)

        # Shield defense check
        if target is not None and target.team != team:
            if target.shielded:
                # Attack is absorbed by shield! Defender survives, shield shatters!
                target.break_shield()
                # Attacker is repelled and remains at starting position
                return

            # Target is captured!
            captured = self.board.remove_piece(r2, c2)
            self.captured_pieces[team].append(captured)
            self.energy_system.award_capture(team, captured.piece_type)

        # Move the piece on self.board
        self.board.move_piece((r1, c1), (r2, c2))

    def _execute_secondary_strike(self, queen_piece: Piece) -> None:
        """Checks for an adjacent enemy to strike as part of Double Strike."""
        r, c = queen_piece.row, queen_piece.col
        team = queen_piece.team
        adjacents = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1)
        ]
        for dr, dc in adjacents:
            nr, nc = r + dr, c + dc
            if is_in_bounds(nr, nc):
                target = self.board.get_piece(nr, nc)
                if target is not None and target.team != team:
                    if target.shielded:
                        target.break_shield()
                    else:
                        captured = self.board.remove_piece(nr, nc)
                        self.captured_pieces[team].append(captured)
                        self.energy_system.award_capture(team, captured.piece_type)
                    break

    def clone(self) -> 'GameState':
        """Deep copy of the entire game state for lookahead simulations."""
        new_state = GameState(board=self.board.clone())
        new_state.current_turn = self.current_turn
        new_state.energy_system = self.energy_system.clone()
        new_state.battlefield_mgr = self.battlefield_mgr.clone()
        new_state.move_history = list(self.move_history)
        new_state.captured_pieces = {
            TEAM_RED: list(self.captured_pieces[TEAM_RED]),
            TEAM_BLUE: list(self.captured_pieces[TEAM_BLUE])
        }
        new_state.turn_count = self.turn_count
        new_state.ability_used_this_turn = self.ability_used_this_turn
        new_state.red_consecutive_domination = self.red_consecutive_domination
        new_state.blue_consecutive_domination = self.blue_consecutive_domination
        new_state.is_game_over = self.is_game_over
        new_state.winner = self.winner
        new_state.victory_reason = self.victory_reason
        new_state.last_move = self.last_move
        return new_state

    def hash_key(self) -> str:
        """Compact string representation for transposition and repetition checking."""
        parts = []
        for r in range(ROWS):
            row_str = ""
            for c in range(COLS):
                p = self.board.grid[r][c]
                if p is None:
                    row_str += "."
                else:
                    s = f"{p.team[0]}{p.piece_type[0]}"
                    if p.shielded:
                        s += "s"
                    row_str += s
            parts.append(row_str)
        parts.append(self.current_turn)
        parts.append(f"R:{self.energy_system.get_energy(TEAM_RED)}")
        parts.append(f"B:{self.energy_system.get_energy(TEAM_BLUE)}")
        return "|".join(parts)
