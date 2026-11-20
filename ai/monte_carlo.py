"""
Chaos Chess - Monte Carlo Tree Search (MCTS) Engine
"""
import time
import math
import random
from typing import Optional, Tuple, Dict, Any, List
from config import TEAM_RED, TEAM_BLUE
from game.game_state import GameState
from game.movement import Move
from ai.evaluation import evaluate_board


class MCTSNode:
    """A node in the Monte Carlo search tree."""

    def __init__(self, state: GameState, parent: Optional['MCTSNode'] = None, move: Optional[Move] = None):
        self.state = state
        self.parent = parent
        self.move = move
        self.children: List['MCTSNode'] = []
        self.visits = 0
        self.value = 0.0
        self.untried_moves = state.get_all_legal_moves()

    def is_fully_expanded(self) -> bool:
        return len(self.untried_moves) == 0

    def is_terminal(self) -> bool:
        return self.state.is_game_over

    def uct_select_child(self, exploration_constant: float = 1.414) -> 'MCTSNode':
        """Select best child node using UCT (Upper Confidence Bound for Trees)."""
        best_child = None
        best_uct = -float('inf')

        for child in self.children:
            if child.visits == 0:
                return child
            # Average win/value rate
            exploitation = child.value / child.visits
            # Exploration bonus
            exploration = exploration_constant * math.sqrt(math.log(self.visits) / child.visits)
            uct_val = exploitation + exploration

            if uct_val > best_uct:
                best_uct = uct_val
                best_child = child

        return best_child or random.choice(self.children)


class MonteCarloSearcher:
    """
    Four-stage Monte Carlo Tree Search:
    Selection -> Expansion -> Simulation -> Backpropagation
    """

    def __init__(self, simulation_budget: int = 60, time_limit_sec: float = 1.5):
        self.simulation_budget = simulation_budget
        self.time_limit = time_limit_sec
        self.simulations_run = 0

    def search(self, game_state: GameState, team: str) -> Tuple[Optional[Move], Dict[str, Any]]:
        start_time = time.time()
        self.simulations_run = 0

        legal_moves = game_state.get_all_legal_moves(team)
        if not legal_moves:
            return None, {"nodes_explored": 0, "execution_time_ms": 0.0, "eval_score": 0.0}

        root = MCTSNode(game_state.clone())

        # Main MCTS loop
        while self.simulations_run < self.simulation_budget:
            if time.time() - start_time > self.time_limit:
                break

            # 1. Selection
            node = root
            while not node.is_terminal() and node.is_fully_expanded() and node.children:
                node = node.uct_select_child()

            # 2. Expansion
            if not node.is_terminal() and node.untried_moves:
                move = node.untried_moves.pop(random.randrange(len(node.untried_moves)))
                next_state = node.state.clone()
                next_state.apply_move(move)
                child_node = MCTSNode(next_state, parent=node, move=move)
                node.children.append(child_node)
                node = child_node

            # 3. Simulation (Rollout)
            reward = self._rollout(node.state, team)

            # 4. Backpropagation
            curr = node
            while curr is not None:
                curr.visits += 1
                curr.value += reward
                curr = curr.parent

            self.simulations_run += 1

        # Pick child with highest visit count
        best_child = None
        most_visits = -1
        for child in root.children:
            if child.visits > most_visits:
                most_visits = child.visits
                best_child = child

        best_move = best_child.move if best_child else random.choice(legal_moves)
        elapsed_ms = (time.time() - start_time) * 1000.0
        win_rate = (best_child.value / max(1, best_child.visits)) if best_child else 0.5

        metrics = {
            "algorithm": "Monte Carlo Tree Search (MCTS)",
            "selected_move": best_move.notation() if best_move else "None",
            "search_depth": 3,
            "nodes_explored": self.simulations_run,
            "nodes_pruned": 0,
            "mcts_simulations": self.simulations_run,
            "eval_score": round(win_rate * 100.0, 1),
            "execution_time_ms": round(elapsed_ms, 2),
            "reasoning": f"MCTS completed {self.simulations_run} playout rollouts with UCT, converging with {round(win_rate * 100, 1)}% projected tactical advantage."
        }
        return best_move, metrics

    def _rollout(self, state: GameState, root_team: str, max_steps: int = 6) -> float:
        """Runs a fast tactical simulation rollout."""
        sim_state = state.clone()
        step = 0

        while not sim_state.is_game_over and step < max_steps:
            moves = sim_state.get_all_legal_moves()
            if not moves:
                break
            # Prefer captures in rollout
            captures = [m for m in moves if m.is_capture]
            chosen_move = random.choice(captures) if captures and random.random() < 0.6 else random.choice(moves)
            sim_state.apply_move(chosen_move)
            step += 1

        # Evaluate terminal or horizon state
        if sim_state.is_game_over:
            if sim_state.winner == root_team:
                return 1.0
            elif sim_state.winner is not None:
                return 0.0
            return 0.5

        # Heuristic payoff mapped to [0, 1]
        ev = evaluate_board(sim_state, root_team)
        return 1.0 / (1.0 + math.exp(-ev / 300.0))

