"""
Chaos Chess - Human vs Human Local Match Controller
"""
from typing import Optional
from game.game_engine import GameEngine
from game.movement import Move


class HumanvsHumanMode:
    """Manages local two-player hotseat gameplay on the same machine."""

    def __init__(self, engine: GameEngine):
        self.engine = engine

    def is_human_turn(self) -> bool:
        return not self.engine.state.is_game_over

    def make_move(self, move: Move) -> bool:
        if self.engine.state.is_game_over:
            return False
        return self.engine.execute_move(move)

    def undo_move(self) -> bool:
        return self.engine.undo_last_move()

