"""
Chaos Chess - Depth First Search (DFS) Tactical Engine
"""
import time
from typing import Optional, Tuple, Dict, Any, List
from config import TEAM_RED, TEAM_BLUE
from game.game_state import GameState
from game.movement import Move
from ai.evaluation import evaluate_board


class DFSSearcher:
    """
    Depth-First Search for bounded tactical exploration,
    escape-route analysis, and multi-step threat resolution.
    """

    def __init__(self, max_depth: int = 3, time_limit_sec: float = 1.5):
        self.max_depth = max_depth
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
        best_score = -float('inf')

        # Prioritize captures and evasions in DFS order
        legal_moves.sort(key=lambda m: (m.is_capture, m.is_special_ability), reverse=True)

        for move in legal_moves:
            cloned = game_state.clone()
            cloned.apply_move(move)
            self.nodes_explored += 1

            score = self._dfs_explore(cloned, depth=1, current_team=cloned.current_turn, root_team=team)

            if score > best_score:
                best_score = score
                best_move = move

            if time.time() - self.start_time > self.time_limit:
                break

        elapsed_ms = (time.time() - self.start_time) * 1000.0
        metrics = {
            "algorithm": "Depth First Search (DFS)",
            "selected_move": best_move.notation() if best_move else "None",
            "search_depth": self.max_depth,
            "nodes_explored": self.nodes_explored,
            "nodes_pruned": 0,
            "eval_score": round(best_score, 1),
            "execution_time_ms": round(elapsed_ms, 2),
            "reasoning": f"DFS deeply explored tactical lines up to depth {self.max_depth}, visiting {self.nodes_explored} tactical positions."
        }
        return best_move, metrics

    def _dfs_explore(self, state: GameState, depth: int, current_team: str, root_team: str) -> float:
        self.nodes_explored += 1

        if depth >= self.max_depth or state.is_game_over or (time.time() - self.start_time > self.time_limit):
            return evaluate_board(state, root_team)

        moves = state.get_all_legal_moves(current_team)
        if not moves:
            return evaluate_board(state, root_team)

        # In bounded DFS tactical exploration, evaluate path payoff
        if current_team == root_team:
            max_val = -float('inf')
            for m in moves:
                next_state = state.clone()
                next_state.apply_move(m)
                val = self._dfs_explore(next_state, depth + 1, next_state.current_turn, root_team)
                if val > max_val:
                    max_val = val
            return max_val
        else:
            min_val = float('inf')
            for m in moves:
                next_state = state.clone()
                next_state.apply_move(m)
                val = self._dfs_explore(next_state, depth + 1, next_state.current_turn, root_team)
                if val < min_val:
                    min_val = val
            return min_val

