"""
Chaos Chess - Energy System
"""
from typing import Dict
from config import (
    STARTING_ENERGY, MAX_ENERGY, ENERGY_REWARDS,
    TEAM_RED, TEAM_BLUE
)


class EnergySystem:
    """Manages tactical energy for Red and Blue teams."""

    def __init__(self, starting_energy: int = STARTING_ENERGY, max_energy: int = MAX_ENERGY):
        self.max_energy = max_energy
        self.energy: Dict[str, int] = {
            TEAM_RED: starting_energy,
            TEAM_BLUE: starting_energy
        }

    def get_energy(self, team: str) -> int:
        return self.energy.get(team, 0)

    def can_afford(self, team: str, cost: int) -> bool:
        return self.energy.get(team, 0) >= cost

    def spend(self, team: str, cost: int) -> bool:
        """Spends energy if available. Returns True on success."""
        if self.can_afford(team, cost):
            self.energy[team] -= cost
            return True
        return False

    def add_energy(self, team: str, amount: int) -> int:
        """Adds energy up to max_energy. Returns actual amount added."""
        old = self.energy.get(team, 0)
        new_val = min(self.max_energy, old + amount)
        self.energy[team] = new_val
        return new_val - old

    def award_capture(self, team: str, captured_piece_type: str) -> int:
        """Award energy for capturing an enemy piece."""
        amount = ENERGY_REWARDS.get(captured_piece_type, 1)
        return self.add_energy(team, amount)

    def clone(self) -> 'EnergySystem':
        clone_sys = EnergySystem(self.energy[TEAM_RED], self.max_energy)
        clone_sys.energy[TEAM_BLUE] = self.energy[TEAM_BLUE]
        return clone_sys

    def to_dict(self) -> Dict[str, int]:
        return {
            TEAM_RED: self.energy[TEAM_RED],
            TEAM_BLUE: self.energy[TEAM_BLUE]
        }

    def from_dict(self, data: Dict[str, int]) -> None:
        self.energy[TEAM_RED] = data.get(TEAM_RED, STARTING_ENERGY)
        self.energy[TEAM_BLUE] = data.get(TEAM_BLUE, STARTING_ENERGY)

