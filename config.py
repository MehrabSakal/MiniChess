"""
Chaos Chess - Game Configuration and Constants
"""
import os

# Window & Display
SCREEN_WIDTH = 1360
SCREEN_HEIGHT = 768
FPS = 60
WINDOW_TITLE = "CHAOS CHESS — Tactical Arena"

# Board Dimensions (EXACT REQUIREMENT: 7 rows x 4 columns)
ROWS = 7
COLS = 4
TOTAL_SQUARES = ROWS * COLS  # 28

# Teams
TEAM_RED = 'red'    # Top team (Rows 0 and 1)
TEAM_BLUE = 'blue'  # Bottom team (Rows 5 and 6)

# Piece Types
KING = 'king'
QUEEN = 'queen'
ROOK = 'rook'
BISHOP = 'bishop'
KNIGHT = 'knight'
PAWN = 'pawn'

PIECE_TYPES = [KING, QUEEN, ROOK, BISHOP, KNIGHT, PAWN]

# Standard Material / Heuristic Values
PIECE_VALUES = {
    PAWN: 100,
    KNIGHT: 320,
    BISHOP: 330,
    ROOK: 500,
    QUEEN: 900,
    KING: 20000
}

# Energy Settings
STARTING_ENERGY = 5
MAX_ENERGY = 10

# Energy awarded on capturing opponent piece
ENERGY_REWARDS = {
    PAWN: 1,
    KNIGHT: 2,
    BISHOP: 2,
    ROOK: 3,
    QUEEN: 4,
    KING: 5
}

# Special Abilities and Energy Costs
ABILITY_ROYAL_SHIELD = "Royal Shield"
ABILITY_DOUBLE_STRIKE = "Double Strike"
ABILITY_FORTRESS = "Fortress"
ABILITY_MAGIC_STEP = "Magic Step"
ABILITY_SUPER_JUMP = "Super Jump"
ABILITY_SACRIFICE = "Sacrifice"

ABILITY_COSTS = {
    ABILITY_ROYAL_SHIELD: 3,
    ABILITY_DOUBLE_STRIKE: 4,
    ABILITY_FORTRESS: 3,
    ABILITY_MAGIC_STEP: 2,
    ABILITY_SUPER_JUMP: 3,
    ABILITY_SACRIFICE: 2
}

PIECE_ABILITIES = {
    KING: ABILITY_ROYAL_SHIELD,
    QUEEN: ABILITY_DOUBLE_STRIKE,
    ROOK: ABILITY_FORTRESS,
    BISHOP: ABILITY_MAGIC_STEP,
    KNIGHT: ABILITY_SUPER_JUMP,
    PAWN: ABILITY_SACRIFICE
}

# Battlefield Events
EVENT_THUNDERSTORM = "Thunderstorm"
EVENT_FROZEN_GROUND = "Frozen Ground"
EVENT_HEALING_ZONE = "Healing Zone"
EVENT_FOG_OF_WAR = "Fog of War"
EVENT_EARTHQUAKE = "Earthquake"
EVENT_ENERGY_BOOST = "Energy Boost"

ALL_EVENTS = [
    EVENT_THUNDERSTORM,
    EVENT_FROZEN_GROUND,
    EVENT_HEALING_ZONE,
    EVENT_FOG_OF_WAR,
    EVENT_EARTHQUAKE,
    EVENT_ENERGY_BOOST
]

# Victory Conditions
VICTORY_ROYAL = "Royal Victory"           # Enemy King captured
VICTORY_DOMINATION = "Domination Victory" # Control >= 15 squares for 3 turns
VICTORY_ELIMINATION = "Elimination Victory" # All enemy pieces eliminated
VICTORY_DRAW = "Draw (Turn Limit / Repetition)"

DEFAULT_TURN_LIMIT = 100
DOMINATION_SQUARES_REQUIRED = 15
DOMINATION_TURNS_REQUIRED = 3

# Visual Color Palette (RGB)
COLOR_BG_DARK = (16, 18, 27)
COLOR_PANEL_BG = (24, 28, 40)
COLOR_PANEL_BORDER = (45, 55, 75)
COLOR_PANEL_HEADER = (34, 40, 58)

# Team Colors
COLOR_RED_PRIMARY = (235, 57, 75)
COLOR_RED_GLOW = (255, 80, 100)
COLOR_RED_DARK = (140, 20, 35)

COLOR_BLUE_PRIMARY = (33, 150, 243)
COLOR_BLUE_GLOW = (79, 195, 247)
COLOR_BLUE_DARK = (13, 71, 161)

# Board Tile Colors
COLOR_TILE_LIGHT = (48, 54, 70)
COLOR_TILE_DARK = (32, 36, 48)
COLOR_TILE_BORDER = (65, 75, 98)
COLOR_TILE_RUNE = (85, 95, 125)

# Highlight Colors
COLOR_HIGHLIGHT_SELECT = (255, 215, 0, 180)     # Gold
COLOR_HIGHLIGHT_MOVE = (46, 204, 113, 170)      # Neon Emerald Green
COLOR_HIGHLIGHT_ATTACK = (231, 76, 60, 200)     # Crimson Red
COLOR_HIGHLIGHT_ABILITY = (175, 82, 222, 190)   # Arcane Purple
COLOR_HIGHLIGHT_LAST_MOVE = (0, 180, 216, 120)  # Cyan tint

# Text Colors
COLOR_TEXT_WHITE = (245, 245, 250)
COLOR_TEXT_GOLD = (255, 215, 0)
COLOR_TEXT_MUTED = (160, 165, 185)
COLOR_TEXT_RED = (255, 107, 107)
COLOR_TEXT_BLUE = (100, 210, 255)

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
DATA_DIR = os.path.join(BASE_DIR, "data")
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")
MATCH_HISTORY_FILE = os.path.join(DATA_DIR, "match_history.json")

