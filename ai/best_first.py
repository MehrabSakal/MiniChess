"""
Chaos Chess - Best First Search (Greedy Heuristic Search)
"""
import time
import heapq
from typing import Optional, Tuple, Dict, Any, List
from config import KING, QUEEN, ROOK, BISHOP, KNIGHT, PAWN, PIECE_VALUES
from game.game_state import GameState
from game.movement import Move, get_piece_standard_moves
from ai.evaluation import evaluate_board


class BestFirstSearcher:
    """
    Best-First Search ranking possible moves by a heuristic evaluation function,
    prioritizing captures, King safety, center control, piece defense, and energy gains.
    """

    def __init__(self, time_limit_sec: float = 1.5):
        self.time_limit = time_limit_sec
        self.nodes_explored = 0

    def search(self, game_state: GameState, team: str) -> Tuple[Optional[Move], Dict[str, Any]]:
        start_time = time.time()
        self.nodes_explored = 0

        legal_moves = game_state.get_all_legal_moves(team)
        if not legal_moves:
            return None, {"nodes_explored": 0, "execution_time_ms": 0.0, "eval_score": 0.0}

        # Priority queue storing (-heuristic_score, tiebreaker, move, resulting_state)
        pq: List[Tuple[float, int, Move]] = []

        counter = 0
        for move in legal_moves:
            cloned = game_state.clone()
            cloned.apply_move(move)
            self.nodes_explored += 1

            h_score = self._compute_move_heuristic(move, game_state, cloned, team)
            heapq.heappush(pq, (-h_score, counter, move))
            counter += 1

        # Pop the best heuristic move
        best_neg_score, _, best_move = heapq.heappop(pq)
        best_score = -best_neg_score

        elapsed_ms = (time.time() - start_time) * 1000.0
        metrics = {
            "algorithm": "Best First Search",
            "selected_move": best_move.notation(),
            "search_depth": 1,
            "nodes_explored": self.nodes_explored,
            "nodes_pruned": 0,
            "eval_score": round(best_score, 1),
            "execution_time_ms": round(elapsed_ms, 2),
            "reasoning": f"Best First Search selected highest heuristic score ({round(best_score, 1)}) prioritizing captures, safety, and center control."
        }
        return best_move, metrics

    def _compute_move_heuristic(
        self,
        move: Move,
        prev_state: GameState,
        post_state: GameState,
        team: str
    ) -> float:
        """
        Calculates move-specific priority heuristic:
        - Captures: award captured piece material
        - King protection
        - Center control (rows 2, 3, 4, cols 1, 2)
        - Special ability impact
        - Positional board evaluation
        """
        score = 0.0

        # 1. Capture bonus
        if move.is_capture and move.captured_piece:
            cap_val = move.captured_piece.value
            score += cap_val * 1.5

        # 2. King defense / evasion
        if move.piece.piece_type == KING:
            score += 40.0
            if move.is_special_ability:  # Royal shield
                score += 300.0

        # 3. Center square control
        r, c = move.end_pos
        if 2 <= r <= 4 and 1 <= c <= 2:
            score += 60.0

        # 4. Special abilities
        if move.is_special_ability:
            score += 120.0

        # 5. Global post-state evaluation
        global_eval = evaluate_board(post_state, team)
        score += global_eval * 0.2

        return score

