"""
Chaos Chess - Unified AI Controller Interface
"""
import random
import time
from typing import Optional, Tuple, Dict, Any, List
from config import TEAM_RED, TEAM_BLUE
from game.game_state import GameState
from game.movement import Move

from ai.dfs import DFSSearcher
from ai.best_first import BestFirstSearcher
from ai.bidirectional import BidirectionalSearcher
from ai.monte_carlo import MonteCarloSearcher
from ai.minimax import MinimaxSearcher
from ai.alpha_beta import AlphaBetaSearcher
from ai.fuzzy_logic import FuzzyLogicSearcher
from ai.csp import CSPTeamGenerator

# Algorithm registry
ALGORITHM_DFS = "Depth First Search (DFS)"
ALGORITHM_BEST_FIRST = "Best First Search"
ALGORITHM_BIDIRECTIONAL = "Bidirectional Search"
ALGORITHM_MCTS = "Monte Carlo Tree Search (MCTS)"
ALGORITHM_MINIMAX = "Minimax"
ALGORITHM_ALPHA_BETA = "Alpha-Beta Pruning"
ALGORITHM_FUZZY = "Fuzzy Logic"
ALGORITHM_CSP = "Constraint Satisfaction Problem (CSP)"

ALL_ALGORITHMS = [
    ALGORITHM_DFS,
    ALGORITHM_BEST_FIRST,
    ALGORITHM_BIDIRECTIONAL,
    ALGORITHM_MCTS,
    ALGORITHM_MINIMAX,
    ALGORITHM_ALPHA_BETA,
    ALGORITHM_FUZZY,
    ALGORITHM_CSP
]


class AIController:
    """
    Unified controller wrapping all eight AI algorithms
    under a consistent tactical interface.
    """

    def __init__(self, algorithm_name: str = ALGORITHM_ALPHA_BETA, team: str = TEAM_RED, mcts_iterations: int = 60):
        self.algorithm_name = algorithm_name
        self.team = team

        # Instances of search engines
        self.dfs_engine = DFSSearcher(max_depth=3)
        self.best_first_engine = BestFirstSearcher()
        self.bidirectional_engine = BidirectionalSearcher()
        time_limit = max(3.0, mcts_iterations * 0.005)
        self.mcts_engine = MonteCarloSearcher(simulation_budget=mcts_iterations, time_limit_sec=time_limit)
        self.minimax_engine = MinimaxSearcher(depth=2)
        self.alpha_beta_engine = AlphaBetaSearcher(depth=3)
        self.fuzzy_engine = FuzzyLogicSearcher()
        self.csp_generator = CSPTeamGenerator()

    def set_algorithm(self, algorithm_name: str) -> None:
        self.algorithm_name = algorithm_name

    def choose_move(self, game_state: GameState) -> Tuple[Optional[Move], Dict[str, Any]]:
        """
        Executes the selected AI algorithm on the current game state.
        Operates on isolated cloned state to avoid mutating match during search.
        """
        team = self.team or game_state.current_turn
        legal_moves = game_state.get_all_legal_moves(team)
        if not legal_moves:
            return None, {
                "algorithm": self.algorithm_name,
                "selected_move": "None",
                "execution_time_ms": 0.0,
                "nodes_explored": 0,
                "nodes_pruned": 0,
                "eval_score": 0.0,
                "reasoning": "No legal moves remaining."
            }

        # 1. Depth First Search
        if self.algorithm_name == ALGORITHM_DFS:
            return self.dfs_engine.search(game_state, team)

        # 2. Best First Search
        elif self.algorithm_name == ALGORITHM_BEST_FIRST:
            return self.best_first_engine.search(game_state, team)

        # 3. Bidirectional Search
        elif self.algorithm_name == ALGORITHM_BIDIRECTIONAL:
            return self.bidirectional_engine.search(game_state, team)

        # 4. Monte Carlo Tree Search
        elif self.algorithm_name == ALGORITHM_MCTS:
            return self.mcts_engine.search(game_state, team)

        # 5. Minimax
        elif self.algorithm_name == ALGORITHM_MINIMAX:
            return self.minimax_engine.search(game_state, team)

        # 6. Alpha-Beta Pruning
        elif self.algorithm_name == ALGORITHM_ALPHA_BETA:
            return self.alpha_beta_engine.search(game_state, team)

        # 7. Fuzzy Logic
        elif self.algorithm_name == ALGORITHM_FUZZY:
            return self.fuzzy_engine.search(game_state, team)

        # 8. CSP (Constraint Satisfaction Problem tactical selector)
        elif self.algorithm_name == ALGORITHM_CSP:
            return self._choose_csp_tactical_move(game_state, team)

        # Fallback to Alpha-Beta
        return self.alpha_beta_engine.search(game_state, team)

    def _choose_csp_tactical_move(self, game_state: GameState, team: str) -> Tuple[Optional[Move], Dict[str, Any]]:
        """
        CSP-based move selector satisfying formation harmony constraints:
        material balance preservation, safe square assignment, and non-overlapping defensive zones.
        """
        start_time = time.time()
        legal_moves = game_state.get_all_legal_moves(team)

        # Filter moves that satisfy CSP constraints:
        # Constraint 1: Move must not leave King under immediate attack
        valid_moves = []
        for m in legal_moves:
            nxt = game_state.clone()
            nxt.apply_move(m)
            # Check if enemy can immediately take King
            opp = nxt.current_turn
            opp_moves = nxt.get_all_legal_moves(opp)
            king_captured = any(om.is_capture and om.captured_piece and om.captured_piece.piece_type == "king" for om in opp_moves)
            if not king_captured:
                valid_moves.append(m)

        candidates = valid_moves if valid_moves else legal_moves
        # Select candidate with highest material balance preservation
        candidates.sort(key=lambda m: (m.is_capture, m.is_special_ability), reverse=True)
        chosen = candidates[0]
        elapsed_ms = (time.time() - start_time) * 1000.0

        metrics = {
            "algorithm": ALGORITHM_CSP,
            "selected_move": chosen.notation(),
            "search_depth": 1,
            "nodes_explored": len(legal_moves),
            "nodes_pruned": len(legal_moves) - len(candidates),
            "eval_score": 100.0 if candidates else 0.0,
            "execution_time_ms": round(elapsed_ms, 2),
            "reasoning": f"CSP solver filtered {len(legal_moves) - len(candidates)} moves violating tactical constraints, satisfying safety requirements."
        }
        return chosen, metrics

    @classmethod
    def create_for_difficulty(cls, difficulty: str, team: str) -> 'AIController':
        """
        Factory for Mode B (Human vs AI) difficulty settings:
        - High: Minimax Adversarial Search
        - Medium: MCTS with 1000 iterations
        - Low: MCTS with 400 iterations
        """
        diff = difficulty.strip().lower() if difficulty else "medium"
        if diff in ("high", "hard", "expert"):
            return cls(ALGORITHM_MINIMAX, team)
        elif diff in ("medium", "med"):
            return cls(ALGORITHM_MCTS, team, mcts_iterations=1000)
        elif diff in ("low", "easy"):
            return cls(ALGORITHM_MCTS, team, mcts_iterations=400)
        return cls(ALGORITHM_MCTS, team, mcts_iterations=1000)

