"""
Chaos Chess - Standard Minimax Adversarial Search
"""
import time
from typing import Optional, Tuple, Dict, Any
from config import TEAM_RED, TEAM_BLUE
from game.game_state import GameState
from game.movement import Move
from ai.evaluation import evaluate_board


class MinimaxSearcher:
    """
    Classic Minimax adversarial tree search without pruning,
    exploring full minimax trees up to configured search depth.
    """

    def __init__(self, depth: int = 2, time_limit_sec: float = 1.5):
        self.depth = depth
        self.time_limit = time_limit_sec
        self.nodes_explored = 0
        self.start_time = 0.0

    def search(self, game_state: GameState, team: str) -> Tuple[Optional[Move], Dict[str, Any]]:
        self.nodes_explored = 0
        self.start_time = time.time()

        legal_moves = game_state.get_all_legal_moves(team)
        if not legal_moves:
            return None, {"nodes_explored": 0, "execution_time_ms": 0.0, "eval_score": 0.0}

        best_move = legal_moves[0]
        best_val = -float('inf')

        for move in legal_moves:
            cloned = game_state.clone()
            cloned.apply_move(move)
            self.nodes_explored += 1

            val = self._minimax(cloned, depth=self.depth - 1, is_maximizing=False, root_team=team)
            if val > best_val:
                best_val = val
                best_move = move

            if time.time() - self.start_time > self.time_limit:
                break

        elapsed_ms = (time.time() - self.start_time) * 1000.0
        metrics = {
            "algorithm": "Minimax",
            "selected_move": best_move.notation(),
            "search_depth": self.depth,
            "nodes_explored": self.nodes_explored,
            "nodes_pruned": 0,
            "eval_score": round(best_val, 1),
            "execution_time_ms": round(elapsed_ms, 2),
            "reasoning": f"Minimax comprehensively evaluated {self.nodes_explored} branch states up to depth {self.depth}."
        }
        return best_move, metrics

    def _minimax(self, state: GameState, depth: int, is_maximizing: bool, root_team: str) -> float:
        self.nodes_explored += 1

        if depth <= 0 or state.is_game_over or (time.time() - self.start_time > self.time_limit):
            return evaluate_board(state, root_team)

        moves = state.get_all_legal_moves()
        if not moves:
            return evaluate_board(state, root_team)

        if is_maximizing:
            max_eval = -float('inf')
            for m in moves:
                next_st = state.clone()
                next_st.apply_move(m)
                ev = self._minimax(next_st, depth - 1, False, root_team)
                max_eval = max(max_eval, ev)
            return max_eval
        else:
            min_eval = float('inf')
            for m in moves:
                next_st = state.clone()
                next_st.apply_move(m)
                ev = self._minimax(next_st, depth - 1, True, root_team)
                min_eval = min(min_eval, ev)
            return min_eval

