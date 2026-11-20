"""
Chaos Chess - Fuzzy Logic Strategic Evaluation System
"""
import time
from typing import Optional, Tuple, Dict, Any, List
from config import ROWS, COLS, KING, TEAM_RED, TEAM_BLUE
from game.game_state import GameState
from game.movement import Move, get_piece_standard_moves
from game.victory import VictoryChecker


def trimf(x: float, a: float, b: float, c: float) -> float:
    """Triangular fuzzy membership function."""
    if x <= a or x >= c:
        return 0.0
    if a < x <= b:
        return (x - a) / (b - a) if b != a else 1.0
    if b < x < c:
        return (c - x) / (c - b) if c != b else 1.0
    return 0.0


def trapmf(x: float, a: float, b: float, c: float, d: float) -> float:
    """Trapezoidal fuzzy membership function."""
    if x <= a or x >= d:
        return 0.0
    if a < x <= b:
        return (x - a) / (b - a) if b != a else 1.0
    if b <= x <= c:
        return 1.0
    if c < x < d:
        return (d - x) / (d - c) if d != c else 1.0
    return 0.0


class FuzzyTacticalEvaluator:
    """
    Fuzzy inference system modeling tactical uncertainty:
    King Danger, Enemy Threats, Piece Protection, Board Control, and Material Advantage.
    """

    def evaluate_state(self, game_state: GameState, team: str) -> Tuple[float, Dict[str, float]]:
        """
        Fuzzifies game state variables, fires fuzzy tactical rules,
        and returns a defuzzified strategic score.
        """
        opp_team = TEAM_BLUE if team == TEAM_RED else TEAM_RED

        # 1. Measure Crisp Inputs
        # King Danger (0 to 100): attacks directly targeting King and immediate surrounding squares
        king = next((p for p in game_state.get_team_pieces(team) if p.piece_type == KING), None)
        king_danger = 0.0
        if king:
            # Check how many enemy attacks threaten King's square or adjacent
            opp_moves = game_state.get_all_legal_moves(opp_team)
            for m in opp_moves:
                if m.end_pos == (king.row, king.col):
                    king_danger += 45.0
                elif abs(m.end_pos[0] - king.row) <= 1 and abs(m.end_pos[1] - king.col) <= 1:
                    king_danger += 12.0
            if king.shielded:
                king_danger = max(0.0, king_danger - 35.0)
        king_danger = min(100.0, king_danger)

        # Enemy Threats (0 to 10): count of friendly pieces currently attacked
        threatened_count = 0
        friendly_pieces = game_state.get_team_pieces(team)
        friendly_squares = {(p.row, p.col): p for p in friendly_pieces}
        opp_moves = game_state.get_all_legal_moves(opp_team)
        attacked_squares = {m.end_pos for m in opp_moves}
        for sq, p in friendly_squares.items():
            if sq in attacked_squares and not p.shielded:
                threatened_count += 1

        # Piece Protection (0 to 8): how many friendly pieces are shielded or defended
        protected_count = sum(1 for p in friendly_pieces if p.shielded)

        # Board Control (0 to 28): squares dominated
        red_ctrl, blue_ctrl = VictoryChecker.calculate_board_control(game_state)
        ctrl_val = red_ctrl if team == TEAM_RED else blue_ctrl

        # Material Balance (-1500 to +1500)
        team_mat = sum(p.value for p in friendly_pieces)
        opp_mat = sum(p.value for p in game_state.get_team_pieces(opp_team))
        mat_balance = team_mat - opp_mat

        # 2. Fuzzification (Membership degrees)
        # King Danger: Safe [0, 0, 30], Threatened [20, 50, 75], Critical [60, 100, 100]
        kd_safe = trapmf(king_danger, -1, 0, 15, 35)
        kd_threatened = trimf(king_danger, 20, 50, 75)
        kd_critical = trapmf(king_danger, 60, 80, 100, 101)

        # Threat Level: Low [0, 0, 2], Moderate [1, 3, 5], High [4, 7, 10]
        th_low = trapmf(threatened_count, -1, 0, 1, 3)
        th_mod = trimf(threatened_count, 1, 3, 5)
        th_high = trapmf(threatened_count, 3, 5, 10, 11)

        # Board Control: Weak [0, 0, 8, 12], Contested [9, 14, 18], Dominant [15, 20, 28, 28]
        bc_weak = trapmf(ctrl_val, -1, 0, 8, 12)
        bc_contested = trimf(ctrl_val, 9, 14, 18)
        bc_dominant = trapmf(ctrl_val, 15, 20, 28, 29)

        # Material: Deficit [-1500, -800, -200], Even [-400, 0, 400], Surplus [200, 800, 1500]
        mb_deficit = trapmf(mat_balance, -2000, -1500, -600, -100)
        mb_even = trimf(mat_balance, -300, 0, 300)
        mb_surplus = trapmf(mat_balance, 100, 600, 2000, 2500)

        # 3. Rule Evaluation & Defuzzification (Weighted Centroid)
        # Output consequences:
        # Emergency Defense: -80
        # Defensive Consolidate: -30
        # Balanced: 0
        # Tactical Advance: +40
        # Dominant Victory Push: +90

        rules = [
            (kd_critical, -90.0),
            (min(kd_safe, bc_dominant, mb_surplus), 90.0),
            (min(th_high, mb_deficit), -60.0),
            (min(bc_dominant, kd_safe), 60.0),
            (min(kd_threatened, th_mod), -25.0),
            (min(mb_surplus, th_low), 50.0),
            (min(mb_even, bc_contested), 10.0),
        ]

        total_weight = sum(w for w, _ in rules)
        if total_weight > 0.0001:
            crisp_score = sum(w * out for w, out in rules) / total_weight
        else:
            crisp_score = 0.0

        # Scale by material and tactical base
        total_eval = crisp_score * 5.0 + mat_balance * 0.5 + ctrl_val * 4.0

        fuzzy_breakdown = {
            "king_danger": round(king_danger, 1),
            "threatened_units": threatened_count,
            "board_control": ctrl_val,
            "material_balance": mat_balance,
            "fuzzy_strategic_score": round(crisp_score, 2)
        }
        return total_eval, fuzzy_breakdown


class FuzzyLogicSearcher:
    """AI Searcher driven by Fuzzy Logic Inference Engine."""

    def __init__(self, time_limit_sec: float = 1.5):
        self.time_limit = time_limit_sec
        self.evaluator = FuzzyTacticalEvaluator()
        self.nodes_explored = 0

    def search(self, game_state: GameState, team: str) -> Tuple[Optional[Move], Dict[str, Any]]:
        start_time = time.time()
        self.nodes_explored = 0

        legal_moves = game_state.get_all_legal_moves(team)
        if not legal_moves:
            return None, {"nodes_explored": 0, "execution_time_ms": 0.0, "eval_score": 0.0}

        best_move = legal_moves[0]
        best_score = -float('inf')
        best_breakdown = {}

        for move in legal_moves:
            cloned = game_state.clone()
            cloned.apply_move(move)
            self.nodes_explored += 1

            score, breakdown = self.evaluator.evaluate_state(cloned, team)
            if score > best_score:
                best_score = score
                best_move = move
                best_breakdown = breakdown

            if time.time() - start_time > self.time_limit:
                break

        elapsed_ms = (time.time() - start_time) * 1000.0
        metrics = {
            "algorithm": "Fuzzy Logic",
            "selected_move": best_move.notation(),
            "search_depth": 1,
            "nodes_explored": self.nodes_explored,
            "nodes_pruned": 0,
            "eval_score": round(best_score, 1),
            "execution_time_ms": round(elapsed_ms, 2),
            "fuzzy_metrics": best_breakdown,
            "reasoning": f"Fuzzy Rules defuzzified KD={best_breakdown.get('king_danger', 0)} into strategic score {best_breakdown.get('fuzzy_strategic_score', 0)}."
        }
        return best_move, metrics

