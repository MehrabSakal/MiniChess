"""
Chaos Chess - How to Play & Tactical Guide
"""
import pygame
from typing import Optional, Dict
from config import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_TEXT_GOLD, COLOR_TEXT_WHITE, COLOR_PANEL_BG
from ui.sound_manager import SoundManager


class HowToPlayScreen:
    """Multi-tab educational guide for Chaos Chess rules, abilities, events, and AI."""

    def __init__(self):
        self.sound_mgr = SoundManager.get_instance()
        self.font_title = pygame.font.SysFont("georgia", 32, bold=True)
        self.font_tab = pygame.font.SysFont("segoeui", 14, bold=True)
        self.font_heading = pygame.font.SysFont("segoeui", 18, bold=True)
        self.font_body = pygame.font.SysFont("segoeui", 13)

        self.back_button = pygame.Rect(40, 35, 100, 38)
        self.tabs = ["Board & Movement", "Energy & Abilities", "Battlefield Events", "Victory Conditions", "AI Algorithms"]
        self.active_tab_idx = 0

        # Tabs Layout
        tab_w = 210
        tab_h = 42
        start_x = 180
        self.tab_rects = []
        for i, t in enumerate(self.tabs):
            self.tab_rects.append(pygame.Rect(start_x + i * (tab_w + 10), 95, tab_w, tab_h))

        self.content_rect = pygame.Rect(40, 150, SCREEN_WIDTH - 80, 560)

    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos

            if self.back_button.collidepoint(mx, my):
                self.sound_mgr.play("move")
                return "menu"

            for i, rect in enumerate(self.tab_rects):
                if rect.collidepoint(mx, my):
                    self.active_tab_idx = i
                    self.sound_mgr.play("move")
                    return None

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "menu"

        return None

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((16, 18, 27))
        mouse_pos = pygame.mouse.get_pos()

        # Back Button
        b_hover = self.back_button.collidepoint(mouse_pos)
        pygame.draw.rect(surface, (45, 55, 75) if b_hover else (30, 36, 50), self.back_button, border_radius=6)
        pygame.draw.rect(surface, (90, 110, 140), self.back_button, width=1, border_radius=6)
        lbl_b = self.font_body.render("← BACK", True, COLOR_TEXT_WHITE)
        surface.blit(lbl_b, (self.back_button.centerx - lbl_b.get_width() // 2, self.back_button.centery - lbl_b.get_height() // 2))

        # Title
        t_surf = self.font_title.render("TACTICAL CODEX & FIELD MANUAL", True, COLOR_TEXT_GOLD)
        surface.blit(t_surf, (180, 35))

        # Tabs
        for i, (tab_name, rect) in enumerate(zip(self.tabs, self.tab_rects)):
            is_active = (i == self.active_tab_idx)
            t_hover = rect.collidepoint(mouse_pos)

            bg_col = (50, 60, 85) if is_active else ((40, 48, 68) if t_hover else (24, 28, 40))
            border_col = COLOR_TEXT_GOLD if is_active else (65, 75, 100)

            pygame.draw.rect(surface, bg_col, rect, border_top_left_radius=8, border_top_right_radius=8)
            pygame.draw.rect(surface, border_col, rect, width=2 if is_active else 1, border_top_left_radius=8, border_top_right_radius=8)

            txt_col = COLOR_TEXT_GOLD if is_active else ((240, 240, 255) if t_hover else (160, 170, 190))
            lbl_t = self.font_tab.render(tab_name, True, txt_col)
            surface.blit(lbl_t, (rect.centerx - lbl_t.get_width() // 2, rect.centery - lbl_t.get_height() // 2))

        # Content Box
        pygame.draw.rect(surface, COLOR_PANEL_BG, self.content_rect, border_radius=10)
        pygame.draw.rect(surface, (60, 70, 95), self.content_rect, width=1, border_radius=10)

        # Tab Content Rendering
        self._render_active_tab_content(surface)

    def _render_active_tab_content(self, surface: pygame.Surface) -> None:
        idx = self.active_tab_idx
        cx = self.content_rect.x + 30
        cy = self.content_rect.y + 25

        if idx == 0:
            # Board & Movement
            lines = [
                ("THE 7 ROWS x 4 COLUMNS TACTICAL BATTLEFIELD", COLOR_TEXT_GOLD, True),
                ("Chaos Chess is played on a compact, high-intensity 7x4 battlefield with exactly 28 squares.", COLOR_TEXT_WHITE, False),
                ("Red Legion starts on Rows 0 & 1 (top); Blue Vanguard starts on Rows 5 & 6 (bottom).", (200, 210, 230), False),
                ("Rows 2, 3, and 4 form the dynamic central arena where domination battles take place.", (200, 210, 230), False),
                ("", COLOR_TEXT_WHITE, False),
                ("SIX TACTICAL PIECE TYPES", COLOR_TEXT_GOLD, True),
                ("• KING: Moves 1 square in any direction. Has exactly one Royal Shield ability per match.", COLOR_TEXT_WHITE, False),
                ("• QUEEN: Any distance horizontally, vertically, or diagonally. Possesses Double Strike.", COLOR_TEXT_WHITE, False),
                ("• ROOK: Any distance along straight cardinal lines (horizontal / vertical). Bestows Fortress.", COLOR_TEXT_WHITE, False),
                ("• BISHOP: Any distance along diagonal angles. Executes Magic Step teleport hops.", COLOR_TEXT_WHITE, False),
                ("• KNIGHT: Classical L-shaped leaps (2x1). Can jump over intervening obstacles. Executes Super Jump.", COLOR_TEXT_WHITE, False),
                ("• PAWN: Advances 1 square forward; captures diagonally forward. Promotes to Queen on back row! Can Sacrifice.", COLOR_TEXT_WHITE, False),
            ]
        elif idx == 1:
            # Energy & Abilities
            lines = [
                ("DYNAMIC ENERGY SYSTEM (EP)", COLOR_TEXT_GOLD, True),
                ("Both teams begin the match with 5 Energy Points (Max: 10 EP).", COLOR_TEXT_WHITE, False),
                ("Capturing enemy pieces awards tactical energy based on their classification:", COLOR_TEXT_WHITE, False),
                ("  - Pawn: +1 EP   |   Knight / Bishop: +2 EP   |   Rook: +3 EP   |   Queen: +4 EP", (255, 230, 120), False),
                ("Each piece may activate its special ability once per match. Max 1 ability per team per turn.", (200, 210, 230), False),
                ("", COLOR_TEXT_WHITE, False),
                ("SPECIAL ABILITY ARSENAL", COLOR_TEXT_GOLD, True),
                ("• Royal Shield (King - Cost 3 EP): Envelops King in a holy aura, nullifying the next capture attempt.", COLOR_TEXT_WHITE, False),
                ("• Double Strike (Queen - Cost 4 EP): Upon capturing an enemy, Queen strikes an adjacent target.", COLOR_TEXT_WHITE, False),
                ("• Fortress (Rook - Cost 3 EP): Projects an impenetrable defensive barrier onto an adjacent allied unit.", COLOR_TEXT_WHITE, False),
                ("• Magic Step (Bishop - Cost 2 EP): Phases diagonally through obstacles to strike or reposition.", COLOR_TEXT_WHITE, False),
                ("• Super Jump (Knight - Cost 3 EP): Vaults across the battlefield with an extended 3-step aerial leap.", COLOR_TEXT_WHITE, False),
                ("• Sacrifice (Pawn - Cost 2 EP): Sacrifices itself to bestow a permanent shield upon an adjacent ally.", COLOR_TEXT_WHITE, False)
            ]
        elif idx == 2:
            # Battlefield Events
            lines = [
                ("DYNAMIC ARENA ENVIRONMENTAL HAZARDS", COLOR_TEXT_GOLD, True),
                ("Every few turns, the arena leylines surge, triggering unpredictable environmental events:", COLOR_TEXT_WHITE, False),
                ("", COLOR_TEXT_WHITE, False),
                ("• ⚡ THUNDERSTORM: Lightning strikes random tiles, stunning unshielded units and shattering shields.", COLOR_TEXT_WHITE, False),
                ("• ❄️ FROZEN GROUND: Glacial ice coats tiles for 2 turns; units cannot move until ice thaws.", COLOR_TEXT_WHITE, False),
                ("• ✨ HEALING ZONE: Divine sanctuary runes emerge on 2 tiles. Allied units stepping in gain shields.", COLOR_TEXT_WHITE, False),
                ("• 🌫️ FOG OF WAR: Dense mystical mist blankets the center rows, disrupting tactical visibility.", COLOR_TEXT_WHITE, False),
                ("• 🌋 EARTHQUAKE: Massive fissures crack center tiles, creating hazardous terrain.", COLOR_TEXT_WHITE, False),
                ("• ⚡ ENERGY SURGE: Mystic ley lines bestow an immediate +2 Energy boost to armies.", COLOR_TEXT_WHITE, False),
                ("", COLOR_TEXT_WHITE, False),
                ("Battlefield events can be toggled on/off or adjusted in the Settings menu.", (180, 200, 220), False)
            ]
        elif idx == 3:
            # Victory Conditions
            lines = [
                ("FOUR PATHWAYS TO VICTORY", COLOR_TEXT_GOLD, True),
                ("Matches are evaluated continuously by the engine across four distinct victory conditions:", COLOR_TEXT_WHITE, False),
                ("", COLOR_TEXT_WHITE, False),
                ("1. ROYAL VICTORY: Assassinate the opposing army's King. Immediate match termination.", (255, 120, 130), False),
                ("2. DOMINATION VICTORY: Exert tactical control over at least 15 of the 28 squares for 3 consecutive turns.", (255, 215, 60), False),
                ("3. ELIMINATION VICTORY: Completely eliminate every opposing unit on the board.", (120, 220, 255), False),
                ("4. TURN LIMIT / TIE-BREAKER: Reaching the turn limit (default 100) triggers point evaluation or draw.", (180, 190, 210), False),
                ("", COLOR_TEXT_WHITE, False),
                ("Square control is computed from both direct piece presence and legal movement threat influence.", COLOR_TEXT_WHITE, False)
            ]
        elif idx == 4:
            # AI Algorithms
            lines = [
                ("EIGHT ARTIFICIAL INTELLIGENCE ENGINES", COLOR_TEXT_GOLD, True),
                ("Chaos Chess features eight separate, academically rigorous AI algorithms:", COLOR_TEXT_WHITE, False),
                ("1. Depth First Search (DFS): Deep bounded tactical lookahead, threat detection, escape paths.", COLOR_TEXT_WHITE, False),
                ("2. Best First Search: Heuristic priority queue ranking captures, King safety, center dominance.", COLOR_TEXT_WHITE, False),
                ("3. Bidirectional Search: Simultaneous forward/backward pathfinding toward central domination objectives.", COLOR_TEXT_WHITE, False),
                ("4. Monte Carlo Tree Search (MCTS): 4-stage UCT selection, expansion, random rollout simulation, and backpropagation.", COLOR_TEXT_WHITE, False),
                ("5. Minimax: Complete adversarial game tree exploration with heuristic leaf evaluation.", COLOR_TEXT_WHITE, False),
                ("6. Alpha-Beta Pruning: Optimized adversarial search with move ordering to prune redundant subtrees.", COLOR_TEXT_WHITE, False),
                ("7. Fuzzy Logic: Multi-variable fuzzy inference system (King danger, threats, protection, control).", COLOR_TEXT_WHITE, False),
                ("8. Constraint Satisfaction Problem (CSP): Backtracking search with Forward Checking generating fair starting armies.", COLOR_TEXT_WHITE, False),
            ]

        for text, col, is_header in lines:
            font = self.font_heading if is_header else self.font_body
            surf = font.render(text, True, col)
            surface.blit(surf, (cx, cy))
            cy += 30 if is_header else 22

