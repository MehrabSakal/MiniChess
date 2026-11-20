"""
Chaos Chess - Battlefield Events System
"""
import random
from typing import List, Dict, Any, Tuple, Optional
from config import (
    ROWS, COLS,
    EVENT_THUNDERSTORM, EVENT_FROZEN_GROUND, EVENT_HEALING_ZONE,
    EVENT_FOG_OF_WAR, EVENT_EARTHQUAKE, EVENT_ENERGY_BOOST,
    ALL_EVENTS
)


class BattlefieldTileEffect:
    """Represents a temporary environmental status on a specific board tile."""
    
    def __init__(self, effect_type: str, row: int, col: int, duration_turns: int, description: str = ""):
        self.effect_type = effect_type
        self.row = row
        self.col = col
        self.duration_turns = duration_turns
        self.description = description

    @property
    def pos(self) -> Tuple[int, int]:
        return (self.row, self.col)

    def tick(self) -> bool:
        """Decrements duration. Returns True if effect has expired."""
        self.duration_turns -= 1
        return self.duration_turns <= 0

    def clone(self) -> 'BattlefieldTileEffect':
        return BattlefieldTileEffect(
            self.effect_type, self.row, self.col, self.duration_turns, self.description
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.effect_type,
            "row": self.row,
            "col": self.col,
            "duration": self.duration_turns,
            "desc": self.description
        }


class BattlefieldManager:
    """Manages dynamic arena events and environmental hazards."""

    def __init__(self, enabled: bool = True, event_frequency: int = 8):
        self.enabled = enabled
        self.event_frequency = event_frequency
        self.active_effects: List[BattlefieldTileEffect] = []
        self.last_event_announcement: Optional[str] = None
        self.last_event_turn: int = 0

    def check_and_trigger_event(self, turn_number: int, game_state) -> Optional[str]:
        """Periodically trigger an arena event if enabled."""
        if not self.enabled:
            return None

        # Check turn frequency
        if turn_number > 0 and turn_number % self.event_frequency == 0 and turn_number != self.last_event_turn:
            self.last_event_turn = turn_number
            chosen_event = random.choice(ALL_EVENTS)
            message = self.execute_event(chosen_event, game_state)
            self.last_event_announcement = message
            return message

        return None

    def execute_event(self, event_name: str, game_state) -> str:
        """Apply an environmental event to the board and state."""
        message = ""

        if event_name == EVENT_THUNDERSTORM:
            # Strikes 2 random tiles
            targets = self._get_random_positions(2)
            for r, c in targets:
                self.active_effects.append(BattlefieldTileEffect(
                    EVENT_THUNDERSTORM, r, c, duration_turns=1,
                    description="Lightning strike! Units standing here lose shields or become stunned."
                ))
                p = game_state.board[r][c]
                if p:
                    if p.shielded:
                        p.break_shield()
                    else:
                        p.frozen_turns = max(p.frozen_turns, 1)
            message = f"⚡ THUNDERSTORM struck the battlefield at {[(r, c) for r, c in targets]}!"

        elif event_name == EVENT_FROZEN_GROUND:
            # 2 tiles turn into frozen ice for 2 turns
            targets = self._get_random_positions(2)
            for r, c in targets:
                self.active_effects.append(BattlefieldTileEffect(
                    EVENT_FROZEN_GROUND, r, c, duration_turns=2,
                    description="Glacial frost! Movement is restricted."
                ))
                p = game_state.board[r][c]
                if p:
                    p.frozen_turns = max(p.frozen_turns, 1)
            message = f"❄️ FROZEN GROUND: Glacial frost covers tiles {[(r, c) for r, c in targets]}!"

        elif event_name == EVENT_HEALING_ZONE:
            # 2 tiles become glowing sanctuary runes for 3 turns
            targets = self._get_random_positions(2)
            for r, c in targets:
                self.active_effects.append(BattlefieldTileEffect(
                    EVENT_HEALING_ZONE, r, c, duration_turns=3,
                    description="Sanctuary rune! Units entering receive a protective shield."
                ))
                p = game_state.board[r][c]
                if p and not p.shielded:
                    p.apply_shield(source="healing_zone")
            message = f"✨ HEALING ZONE: Divine sanctuary runes appear at {[(r, c) for r, c in targets]}!"

        elif event_name == EVENT_FOG_OF_WAR:
            # Fog engulfs middle rows for 2 turns
            for c in range(COLS):
                self.active_effects.append(BattlefieldTileEffect(
                    EVENT_FOG_OF_WAR, 3, c, duration_turns=2,
                    description="Thick mist shrouds the arena center."
                ))
            message = "🌫️ FOG OF WAR: Dense mist blankets row 3!"

        elif event_name == EVENT_EARTHQUAKE:
            # Shakes 2 tiles, making them hazardous for 2 turns
            targets = self._get_random_positions(2)
            for r, c in targets:
                self.active_effects.append(BattlefieldTileEffect(
                    EVENT_EARTHQUAKE, r, c, duration_turns=2,
                    description="Cracked fissure! Tile is temporarily unstable."
                ))
            message = f"🌋 EARTHQUAKE: Ground fissures erupt at {[(r, c) for r, c in targets]}!"

        elif event_name == EVENT_ENERGY_BOOST:
            # Both teams surge with +2 energy
            red_gained = game_state.energy_system.add_energy("red", 2)
            blue_gained = game_state.energy_system.add_energy("blue", 2)
            message = f"⚡ ENERGY SURGE: Mystic ley lines bestow +2 Energy to both armies!"

        return message

    def on_turn_end(self, game_state) -> None:
        """Advance durations and clean up expired effects."""
        remaining: List[BattlefieldTileEffect] = []
        for effect in self.active_effects:
            if not effect.tick():
                remaining.append(effect)
        self.active_effects = remaining

    def get_effects_at(self, row: int, col: int) -> List[BattlefieldTileEffect]:
        return [eff for eff in self.active_effects if eff.row == row and eff.col == col]

    def is_tile_frozen(self, row: int, col: int) -> bool:
        return any(eff.effect_type == EVENT_FROZEN_GROUND for eff in self.get_effects_at(row, col))

    def _get_random_positions(self, count: int) -> List[Tuple[int, int]]:
        all_squares = [(r, c) for r in range(ROWS) for c in range(COLS)]
        return random.sample(all_squares, min(count, len(all_squares)))

    def clone(self) -> 'BattlefieldManager':
        mgr = BattlefieldManager(self.enabled, self.event_frequency)
        mgr.active_effects = [eff.clone() for eff in self.active_effects]
        mgr.last_event_announcement = self.last_event_announcement
        mgr.last_event_turn = self.last_event_turn
        return mgr

