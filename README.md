# CHAOS CHESS — An AI-Powered Tactical Arena Game

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Pygame](https://img.shields.io/badge/Pygame-2.6.1-green.svg)](https://www.pygame.org/)
[![Tests](https://img.shields.io/badge/Tests-27%20Passed-brightgreen.svg)]()

**Chaos Chess** is a fantasy tactical battle arena combining chess-inspired gameplay, dynamic energy mechanics, unique unit special abilities, environmental hazards, and **eight distinct Artificial Intelligence algorithms** integrated into a desktop game built in Python and Pygame.

---

## ⚔️ Key Features

- **7 Rows × 4 Columns Tactical Battlefield**: 28 total squares. Red Legion occupies rows 0 & 1; Blue Vanguard occupies rows 5 & 6. The 3 middle rows form the central contest arena.
- **6 Chess-Inspired Piece Types**: King, Queen, Rook, Bishop, Knight, and Pawn with bold, iconic chess silhouettes, gold beveling, engraved identification letter crests (`K`, `Q`, `R`, `B`, `N`, `P`), tactical movement, and pawn promotion.
- **Interactive Mouse Hover Inspection**: Hovering your cursor over any unit on the board instantly illuminates the tile and displays a tactical tooltip showing the unit's full name, team, role, movement rules, material value, and special ability status.
- **Dynamic Energy & Special Abilities**:
  - Teams start with 5 Energy Points (EP), max 10 EP.
  - Capturing opponents rewards energy (+1 Pawn, +2 Knight/Bishop, +3 Rook, +4 Queen).
  - **King — Royal Shield (3 EP)**: Nullifies the next enemy capture attempt.
  - **Queen — Double Strike (4 EP)**: Grants a devastating second capture on the same turn.
  - **Rook — Fortress (3 EP)**: Projects a defensive barrier onto an adjacent ally.
  - **Bishop — Magic Step (2 EP)**: Phases diagonally through obstacles to reposition or strike.
  - **Knight — Super Jump (3 EP)**: Vaults across the battlefield with an extended 3-step aerial leap.
  - **Pawn — Sacrifice (2 EP)**: Sacrifices itself to bestow a permanent shield upon an adjacent ally.
  - Each unit can use its ability once per match. Max 1 special ability per team per turn.
- **Dynamic Battlefield Events**:
  - *Thunderstorm*: Random lightning strikes stunning units or shattering shields.
  - *Frozen Ground*: Glacial frost immobilizing units on affected squares.
  - *Healing Zone*: Divine sanctuary runes granting protective shields.
  - *Fog of War*: Mist shrouding the central rows.
  - *Earthquake*: Fissures fracturing the arena floor.
  - *Energy Boost*: Leyline surges granting both armies +2 Energy.
- **3 Distinct Victory Conditions**:
  1. *Royal Victory*: Assassinate the opposing army's King.
  2. *Elimination Victory*: Annihilate all opposing pieces.
  3. *Turn Limit / Draw*: Turn limit exhaustion (100 turns default).
- **3 Gameplay Modes**:
  - **AI vs AI**: Select any 2 algorithms and observe autonomous matches with real-time telemetry.
  - **Human vs AI**: Dedicated difficulty interface with 3 modes:
    - **High**: Minimax Adversarial Search (Full game-tree evaluation).
    - **Medium**: Monte Carlo Tree Search (MCTS with 1000 iterations).
    - **Low**: Monte Carlo Tree Search (MCTS with 400 iterations).
  - **Human vs Human**: Local two-player hotseat match with move history and undo support.
- **AI Algorithm Arena & Benchmark Lab**: Compare any 2 algorithms side-by-side with live Matplotlib performance charts (Execution Time, Nodes Explored, Nodes Pruned, Efficiency).

---

## 🧠 All Eight AI Algorithms Implemented

1. **Depth First Search (DFS)** (`ai/dfs.py`): Bounded multi-step tactical lookahead, threat detection, and escape-route exploration.
2. **Best First Search** (`ai/best_first.py`): Heuristic priority queue search ranking moves by capture value, King defense, center control, and energy payoff.
3. **Bidirectional Search** (`ai/bidirectional.py`): Simultaneous forward and backward pathfinding toward key arena objectives (center squares and enemy King).
4. **Monte Carlo Tree Search (MCTS)** (`ai/monte_carlo.py`): 4-stage search (Selection via UCT, Expansion, Rollout Simulation, Backpropagation).
5. **Minimax** (`ai/minimax.py`): Classic adversarial tree search alternating maximizing and minimizing turns.
6. **Alpha-Beta Pruning** (`ai/alpha_beta.py`): Optimized adversarial lookahead with move ordering (captures and abilities first) to maximize branch pruning.
7. **Fuzzy Logic** (`ai/fuzzy_logic.py`): Multi-variable fuzzy inference system evaluating King Danger, Enemy Threats, Piece Protection, Board Control, and Material Balance using triangular/trapezoidal membership functions and defuzzification.
8. **Constraint Satisfaction Problem (CSP)** (`ai/csp.py`): Backtracking search with Forward Checking and MRV variable ordering to generate valid, fair, balanced starting army formations.

---

## 📁 Project Structure

```text
ChaosChess/
├── main.py                     # Master application & scene manager
├── config.py                   # Constants, board geometry (7x4), colors, rules
├── requirements.txt            # Python dependencies
│
├── assets/
│   ├── images/
│   │   ├── pieces/             # 12 custom high-detail piece sprites (Red & Blue)
│   │   └── backgrounds/        # Atmospheric tavern battle arena background
│   └── sounds/                 # Procedurally generated tactical sound effects
│
├── game/
│   ├── board.py                # 7x4 Board grid representation
│   ├── piece.py                # Piece model with shield, frozen, & ability states
│   ├── movement.py             # Movement validation & special ability moves
│   ├── game_state.py           # Self-contained match state & cloning
│   ├── game_engine.py          # Match lifecycle, history logging, and undo
│   ├── special_abilities.py    # Ability rules and descriptions
│   ├── energy_system.py        # Energy point tracking and capture rewards
│   ├── battlefield.py          # Dynamic environmental hazards manager
│   └── victory.py              # Royal, Domination, Elimination, and Draw rules
│
├── ai/
│   ├── csp.py                  # Algorithm 8: CSP Team Generator
│   ├── dfs.py                  # Algorithm 1: Depth First Search
│   ├── best_first.py           # Algorithm 2: Best First Search
│   ├── bidirectional.py        # Algorithm 3: Bidirectional Search
│   ├── monte_carlo.py          # Algorithm 4: Monte Carlo Tree Search
│   ├── minimax.py              # Algorithm 5: Minimax Adversarial Search
│   ├── alpha_beta.py           # Algorithm 6: Alpha-Beta Pruning
│   ├── fuzzy_logic.py          # Algorithm 7: Fuzzy Logic Evaluator
│   ├── evaluation.py           # Tactical heuristic & piece-square tables
│   └── ai_controller.py        # Unified interface wrapping all 8 algorithms
│
├── ui/
│   ├── menu.py                 # Main Menu with animated embers
│   ├── mode_select.py          # Mode Selection screen
│   ├── difficulty_select.py    # Dedicated Difficulty Selection (High, Medium, Low)
│   ├── game_screen.py          # Main arena HUD, panels, ability bar, controls
│   ├── board_renderer.py       # 7x4 Board renderer, tile runes, smooth animations
│   ├── ai_panel.py             # Real-time AI thinking console & gauge
│   ├── arena_screen.py         # Algorithm benchmark lab with Matplotlib charts
│   ├── how_to_play.py          # Multi-tab tactical codex & manual
│   ├── settings.py             # Interactive settings configuration
│   ├── result_screen.py        # Victory / match statistics modal
│   ├── sound_manager.py        # Safe audio playback system
│   └── particles.py            # Tactical spark, burst, and shield particles
│
├── modes/
│   ├── ai_vs_ai.py             # Autonomous AI vs AI controller
│   ├── ai_vs_human.py          # Human vs AI controller
│   └── human_vs_human.py       # Local hotseat 2-player controller
│
├── data/
│   ├── settings.json           # User settings persistence
│   └── match_history.json      # Match records & performance logging
│
└── tests/
    ├── test_csp.py             # Unit tests for CSP solver
    ├── test_movement.py        # Unit tests for 7x4 board movement & promotion
    ├── test_victory.py         # Unit tests for victory conditions & shields
    ├── test_minimax.py         # Unit tests for Minimax & Alpha-Beta
    ├── test_algorithms.py      # Unit tests for all 8 AI algorithms
    └── test_integration.py     # End-to-end integration tests for all screens
```

---

## 🚀 Installation & Running

### 1. Requirements
Ensure Python 3.10+ is installed:
```bash
python --version
```

Install dependencies:
```bash
pip install -r requirements.txt
```

### 2. Launching the Game
Start Chaos Chess by running:
```bash
python main.py
```

### 3. Running Unit & Integration Tests
Execute the comprehensive test suite (27 automated tests):
```bash
python -m pytest tests/
```

---

## 🎮 Controls

- **Left Mouse Click**:
  - Click any friendly piece to view legal moves (emerald dots) and attack targets (crimson rings).
  - Click a target square to execute movement.
  - Click any Special Ability button in the bottom HUD to activate ability targeting mode.
- **Spacebar**: Toggle Pause / Resume.
- **S**: Step 1 turn forward (AI vs AI mode).
- **U**: Undo last move (AI vs Human or Human vs Human mode).
- **Escape**: Return to Main Menu.

