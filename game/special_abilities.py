"""
Chaos Chess - Special Abilities Engine
"""
from typing import Optional, List, Tuple
from config import (
    ABILITY_ROYAL_SHIELD, ABILITY_DOUBLE_STRIKE, ABILITY_FORTRESS,
    ABILITY_MAGIC_STEP, ABILITY_SUPER_JUMP, ABILITY_SACRIFICE,
    ABILITY_COSTS, ROWS, COLS
)
from game.piece import Piece


class SpecialAbilityManager:
    """Handles execution and rule validation for piece special abilities."""

    @staticmethod
    def get_ability_description(ability_name: str) -> str:
        descriptions = {
            ABILITY_ROYAL_SHIELD: "Royal Shield (Cost 3 EP): Envelops King in a holy aura, nullifying the next capture attempt.",
            ABILITY_DOUBLE_STRIKE: "Double Strike (Cost 4 EP): Allows the Queen to execute a devastating second capture in the same turn.",
            ABILITY_FORTRESS: "Fortress (Cost 3 EP): Projects an impenetrable defensive barrier onto an adjacent allied unit.",
            ABILITY_MAGIC_STEP: "Magic Step (Cost 2 EP): Phases diagonally through obstacles to strike or reposition.",
            ABILITY_SUPER_JUMP: "Super Jump (Cost 3 EP): Vaults across the battlefield with an extended 3-step aerial leap.",
            ABILITY_SACRIFICE: "Sacrifice (Cost 2 EP): Sacrifices this brave pawn to bestow a permanent shield upon an adjacent ally."
        }
        return descriptions.get(ability_name, "Special tactical ability.")

    @staticmethod
    def get_cost(ability_name: str) -> int:
        return ABILITY_COSTS.get(ability_name, 0)

