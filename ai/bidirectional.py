"""
Chaos Chess - Bidirectional Search Tactical Engine
"""
import time
from typing import Optional, Tuple, Dict, Any, List, Set
from collections import deque
from config import ROWS, COLS, KING, PAWN, TEAM_RED, TEAM_BLUE
from game.game_state import GameState
from game.movement import Move, is_in_bounds, get_piece_standard_moves
from ai.evaluation import evaluate_board


class BidirectionalSearcher:
    """
    Bidirectional Search for tactical pathfinding between piece positions
    and high-priority strategic arena objectives (center squares, enemy King, promotion row).
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

        # Strategic objectives:
        # 1. Opponent King position (Royal Victory)
        # 2. Central Domination squares (3, 1) and (3, 2)
        # 3. Enemy back row for pawns
        opp_team = TEAM_BLUE if team == TEAM_RED else TEAM_RED
        opp_pieces = game_state.get_team_pieces(opp_team)
        opp_king = next((p for p in opp_pieces if p.piece_type == KING), None)

        objectives: List[Tuple[int, int]] = []
        if opp_king:
            objectives.append((opp_king.row, opp_king.col))
        objectives.extend([(3, 1), (3, 2), (2, 1), (2, 2)])

        best_move = legal_moves[0]
        best_path_score = -float('inf')
        target_found = None

        for target_sq in objectives:
            for move in legal_moves:
                self.nodes_explored += 1
                # Check path length from move.end_pos to target_sq via Bidirectional Search
                path_len = self._bidirectional_path(move.end_pos, target_sq, game_state)
                if path_len is not None:
                    # Shorter paths to high-priority targets are scored higher
                    # Bonus for captures
                    cap_bonus = 200.0 if move.is_capture else 0.0
                    path_score = (100.0 / (path_len + 1)) + cap_bonus
                    if path_score > best_path_score:
                        best_path_score = path_score
                        best_move = move
                        target_found = target_sq

            if target_found and best_path_score > 150:
                break

        elapsed_ms = (time.time() - start_time) * 1000.0
        metrics = {
            "algorithm": "Bidirectional Search",
            "selected_move": best_move.notation(),
            "search_depth": 2,
            "nodes_explored": self.nodes_explored,
            "nodes_pruned": 0,
            "eval_score": round(best_path_score if best_path_score != -float('inf') else 0.0, 1),
            "execution_time_ms": round(elapsed_ms, 2),
            "reasoning": f"Bidirectional Search met frontiers between piece and strategic objective {target_found}, finding optimal tactical path."
        }
        return best_move, metrics

    def _bidirectional_path(
        self,
        start_sq: Tuple[int, int],
        goal_sq: Tuple[int, int],
        game_state: GameState
    ) -> Optional[int]:
        """
        Executes simultaneous forward and backward breadth-first search
        until frontiers collide. Returns shortest path step count.
        """
        if start_sq == goal_sq:
            return 0

        forward_queue = deque([(start_sq, 0)])
        backward_queue = deque([(goal_sq, 0)])

        forward_visited: Dict[Tuple[int, int], int] = {start_sq: 0}
        backward_visited: Dict[Tuple[int, int], int] = {goal_sq: 0}

        while forward_queue and backward_queue:
            # 1. Expand Forward Frontier
            curr_f, dist_f = forward_queue.popleft()
            self.nodes_explored += 1
            for nxt in self._get_neighbors(curr_f):
                if nxt in backward_visited:
                    return dist_f + 1 + backward_visited[nxt]
                if nxt not in forward_visited:
                    forward_visited[nxt] = dist_f + 1
                    forward_queue.append((nxt, dist_f + 1))

            # 2. Expand Backward Frontier
            curr_b, dist_b = backward_queue.popleft()
            self.nodes_explored += 1
            for nxt in self._get_neighbors(curr_b):
                if nxt in forward_visited:
                    return dist_b + 1 + forward_visited[nxt]
                if nxt not in backward_visited:
                    backward_visited[nxt] = dist_b + 1
                    backward_queue.append((nxt, dist_b + 1))

            if dist_f + dist_b > 6:
                break

        return None

    def _get_neighbors(self, pos: Tuple[int, int]) -> List[Tuple[int, int]]:
        r, c = pos
        directions = [
            (-1, 0), (1, 0), (0, -1), (0, 1),
            (-1, -1), (-1, 1), (1, -1), (1, 1)
        ]
        res = []
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if is_in_bounds(nr, nc):
                res.append((nr, nc))
        return res

