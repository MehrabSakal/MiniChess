"""
Chaos Chess - AI vs AI Mode Controller
"""
import time
from typing import Optional, Dict, Any, Tuple
from config import TEAM_RED, TEAM_BLUE
from game.game_engine import GameEngine
from game.movement import Move
from ai.ai_controller import AIController, ALGORITHM_ALPHA_BETA, ALGORITHM_MCTS


class AIvsAIMode:
    """Manages an autonomous tactical match between two AI algorithms."""

    def __init__(
        self,
        engine: GameEngine,
        red_algorithm: str = ALGORITHM_ALPHA_BETA,
        blue_algorithm: str = ALGORITHM_MCTS,
        move_delay_ms: int = 400,
        red_mcts_iterations: int = 1000,
        blue_mcts_iterations: int = 1000
    ):
        self.engine = engine
        self.red_ai = AIController(red_algorithm, team=TEAM_RED, mcts_iterations=red_mcts_iterations)
        self.blue_ai = AIController(blue_algorithm, team=TEAM_BLUE, mcts_iterations=blue_mcts_iterations)
        self.move_delay_ms = move_delay_ms
        self.last_move_timestamp = time.time()
        self.is_paused = False
        self.step_requested = False

        # Latest AI telemetry
        self.red_metrics: Dict[str, Any] = {}
        self.blue_metrics: Dict[str, Any] = {}

    def update(self) -> Optional[Move]:
        """
        Executes one AI turn when the delay timer elapses or step is requested.
        Returns the Move executed, or None.
        """
        if self.engine.state.is_game_over:
            return None

        now = time.time()
        elapsed_ms = (now - self.last_move_timestamp) * 1000.0

        if not self.step_requested and (self.is_paused or elapsed_ms < self.move_delay_ms):
            return None

        self.step_requested = False
        self.last_move_timestamp = now

        current_team = self.engine.state.current_turn
        active_ai = self.red_ai if current_team == TEAM_RED else self.blue_ai

        move, metrics = active_ai.choose_move(self.engine.state)

        if current_team == TEAM_RED:
            self.red_metrics = metrics
        else:
            self.blue_metrics = metrics

        self.engine.last_ai_metrics = metrics

        if move:
            self.engine.execute_move(move)
            return move

        return None

    def toggle_pause(self) -> bool:
        self.is_paused = not self.is_paused
        return self.is_paused

    def request_step(self) -> None:
        self.step_requested = True

