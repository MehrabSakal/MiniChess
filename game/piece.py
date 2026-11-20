"""
Chaos Chess - Piece Model
"""
import uuid
from typing import Optional, Dict, Any
from config import (
    KING, QUEEN, ROOK, BISHOP, KNIGHT, PAWN,
    TEAM_RED, TEAM_BLUE, PIECE_VALUES, PIECE_ABILITIES
)


class Piece:
    """Represents a game piece with tactical attributes and ability states."""
    
    def __init__(
        self,
        piece_type: str,
        team: str,
        row: int,
        col: int,
        piece_id: Optional[str] = None
    ):
        self.piece_type = piece_type
        self.team = team
        self.row = row
        self.col = col
        self.id = piece_id or f"{team}_{piece_type}_{uuid.uuid4().hex[:6]}"
        
        # State tracking
        self.has_moved: bool = False
        self.ability_used: bool = False   # Each piece can use ability once per match
        self.shielded: bool = False       # Protects from 1 capture
        self.shield_source: Optional[str] = None
        self.frozen_turns: int = 0        # Battlefield event status (Frozen Ground)
        
    @property
    def value(self) -> int:
        """Heuristic value of the piece."""
        return PIECE_VALUES.get(self.piece_type, 100)
        
    @property
    def special_ability(self) -> str:
        """Name of this piece's special ability."""
        return PIECE_ABILITIES.get(self.piece_type, "")

    @property
    def pos(self) -> tuple[int, int]:
        return (self.row, self.col)

    def set_pos(self, row: int, col: int) -> None:
        self.row = row
        self.col = col
        self.has_moved = True

    def can_use_ability(self) -> bool:
        """Check if this piece is eligible to use its unique ability."""
        return not self.ability_used and self.frozen_turns <= 0

    def mark_ability_used(self) -> None:
        self.ability_used = True

    def apply_shield(self, source: str = "shield") -> None:
        self.shielded = True
        self.shield_source = source

    def break_shield(self) -> bool:
        """Removes shield if active. Returns True if shield was consumed."""
        if self.shielded:
            self.shielded = False
            self.shield_source = None
            return True
        return False

    def clone(self) -> 'Piece':
        """Deep copy for AI search simulations."""
        p = Piece(self.piece_type, self.team, self.row, self.col, self.id)
        p.has_moved = self.has_moved
        p.ability_used = self.ability_used
        p.shielded = self.shielded
        p.shield_source = self.shield_source
        p.frozen_turns = self.frozen_turns
        return p

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.piece_type,
            "team": self.team,
            "row": self.row,
            "col": self.col,
            "id": self.id,
            "has_moved": self.has_moved,
            "ability_used": self.ability_used,
            "shielded": self.shielded,
            "shield_source": self.shield_source,
            "frozen_turns": self.frozen_turns
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Piece':
        p = cls(data["type"], data["team"], data["row"], data["col"], data["id"])
        p.has_moved = data.get("has_moved", False)
        p.ability_used = data.get("ability_used", False)
        p.shielded = data.get("shielded", False)
        p.shield_source = data.get("shield_source")
        p.frozen_turns = data.get("frozen_turns", 0)
        return p

    def __repr__(self) -> str:
        s = f"[{self.team[:1].upper()}:{self.piece_type[:2].upper()}"
        if self.shielded:
            s += "(S)"
        s += "]"
        return s

