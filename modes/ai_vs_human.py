"""
Chaos Chess - AI vs Human Mode Controller
"""
import time
from typing import Optional, Dict, Any, Tuple
from config import TEAM_RED, TEAM_BLUE
from game.game_engine import GameEngine
from game.movement import Move
from ai.ai_controller import AIController


class AIvsHumanMode:
    """Manages match between a human player and an AI opponent."""

    def __init__(
        self,
        engine: GameEngine,
        human_team: str = TEAM_BLUE,
        difficulty: str = "Medium",
        ai_delay_ms: int = 350
    ):
        self.engine = engine
        self.human_team = human_team
        self.ai_team = TEAM_RED if human_team == TEAM_BLUE else TEAM_BLUE
        self.difficulty = difficulty
        self.ai_delay_ms = ai_delay_ms
        self.ai = AIController.create_for_difficulty(difficulty, self.ai_team)
        self.ai_metrics: Dict[str, Any] = {}
        self.ai_turn_start: Optional[float] = None

    def is_human_turn(self) -> bool:
        return self.engine.state.current_turn == self.human_team and not self.engine.state.is_game_over

    def update(self) -> Optional[Move]:
        """Runs the AI turn if active."""
        if self.engine.state.is_game_over or self.is_human_turn():
            self.ai_turn_start = None
            return None

        now = time.time()
        if self.ai_turn_start is None:
            self.ai_turn_start = now
            return None

        if (now - self.ai_turn_start) * 1000.0 < self.ai_delay_ms:
            return None

        # Execute AI move
        self.ai_turn_start = None
        move, metrics = self.ai.choose_move(self.engine.state)
        self.ai_metrics = metrics
        self.engine.last_ai_metrics = metrics

        if move:
            self.engine.execute_move(move)
            return move

        return None

