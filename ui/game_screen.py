"""
Chaos Chess - Main Tactical Arena Game Screen
"""
import os
import pygame
from typing import Optional, Tuple, List, Dict, Any
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    ROWS, COLS,
    KING, QUEEN, ROOK, BISHOP, KNIGHT, PAWN,
    TEAM_RED, TEAM_BLUE,
    COLOR_BG_DARK, COLOR_PANEL_BG, COLOR_PANEL_BORDER, COLOR_PANEL_HEADER,
    COLOR_RED_PRIMARY, COLOR_BLUE_PRIMARY,
    COLOR_TEXT_WHITE, COLOR_TEXT_GOLD, COLOR_TEXT_MUTED,
    ABILITY_ROYAL_SHIELD, ABILITY_DOUBLE_STRIKE, ABILITY_FORTRESS,
    ABILITY_MAGIC_STEP, ABILITY_SUPER_JUMP, ABILITY_SACRIFICE,
    ABILITY_COSTS, PIECE_ABILITIES,
    ASSETS_DIR
)
from game.game_engine import GameEngine
from game.movement import Move
from game.piece import Piece
from ui.board_renderer import BoardRenderer
from ui.ai_panel import AIPanel
from ui.particles import ParticleSystem
from ui.sound_manager import SoundManager
from game.special_abilities import SpecialAbilityManager


class GameScreen:
    """Manages the interactive HUD, board rendering, user input, and mode updates."""

    def __init__(self, engine: GameEngine, mode_controller: Any, mode_name: str = "ai_vs_human"):
        self.engine = engine
        self.mode_controller = mode_controller
        self.mode_name = mode_name

        # Board layout: centered 7x4 tactical board
        # Board width = 4 * 86 = 344. Center = 1360 // 2 = 680. Origin_x = 680 - 172 = 508.
        # Board height = 7 * 86 = 602. Origin_y = 35.
        self.board_renderer = BoardRenderer(origin_x=508, origin_y=35, tile_size=86)
        self.particle_sys = ParticleSystem()
        self.sound_mgr = SoundManager.get_instance()

        # Side Panels
        # Left Panel (Red): x=20, y=35, w=300, h=602
        self.red_panel_rect = pygame.Rect(20, 35, 300, 602)
        self.red_ai_panel = AIPanel(pygame.Rect(20, 240, 300, 397), title="RED TELEMETRY")

        # Right Panel (Blue): x=1040, y=35, w=300, h=602
        self.blue_panel_rect = pygame.Rect(1040, 35, 300, 602)
        self.blue_ai_panel = AIPanel(pygame.Rect(1040, 240, 300, 397), title="BLUE TELEMETRY")

        # Bottom HUD: x=20, y=650, w=1320, h=102
        self.bottom_panel_rect = pygame.Rect(20, 650, 1320, 102)

        # Interaction state
        self.selected_pos: Optional[Tuple[int, int]] = None
        self.selected_piece_legal_moves: List[Move] = []
        self.active_ability_filter: Optional[str] = None
        self.hovered_tooltip: Optional[str] = None
        pts = self.engine.team_material_points.get(TEAM_BLUE, 0)
        self.event_banner_timer = 4.0
        self.event_banner_text = f"CSP BALANCED MATCH: IDENTICAL PIECES & EQUAL POINTS ({pts:,} PTS)" if pts > 0 else "CSP BALANCED MATCH: IDENTICAL ARMIES & EQUAL POINTS"

        # Background
        self.bg_image: Optional[pygame.Surface] = None
        self._load_background()

        # Fonts
        self.font_title = pygame.font.SysFont("segoeui", 18, bold=True)
        self.font_body = pygame.font.SysFont("segoeui", 13)
        self.font_small = pygame.font.SysFont("segoeui", 11)
        self.font_mono = pygame.font.SysFont("consolas", 12)

        # Buttons mapping
        self.buttons: Dict[str, pygame.Rect] = {}
        self._init_buttons()

        # Speed multiplier for AI vs AI
        self.speed_multiplier = 1.0

    def _load_background(self) -> None:
        bg_path = os.path.join(ASSETS_DIR, "images", "backgrounds", "arena_tavern.jpg")
        if os.path.exists(bg_path):
            try:
                raw = pygame.image.load(bg_path).convert()
                # Scale to screen size with dark ambient tint
                scaled = pygame.transform.smoothscale(raw, (SCREEN_WIDTH, SCREEN_HEIGHT))
                dark_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                dark_overlay.fill((10, 12, 18, 190))
                scaled.blit(dark_overlay, (0, 0))
                self.bg_image = scaled
            except Exception:
                self.bg_image = None

    def _init_buttons(self) -> None:
        """Sets up action and special ability buttons."""
        # Action controls on right side of bottom panel
        bx = self.bottom_panel_rect.right - 90
        by = self.bottom_panel_rect.y + 12
        btn_w, btn_h = 78, 36

        self.buttons["menu"] = pygame.Rect(bx, by, btn_w, btn_h)
        self.buttons["restart"] = pygame.Rect(bx - 88, by, btn_w, btn_h)
        self.buttons["step"] = pygame.Rect(bx - 176, by, btn_w, btn_h)
        self.buttons["pause"] = pygame.Rect(bx - 264, by, btn_w, btn_h)
        self.buttons["undo"] = pygame.Rect(bx - 352, by, btn_w, btn_h)

        # Special Ability buttons on left side of bottom panel
        ab_list = [
            (ABILITY_ROYAL_SHIELD, 3, KING),
            (ABILITY_DOUBLE_STRIKE, 4, QUEEN),
            (ABILITY_FORTRESS, 3, ROOK),
            (ABILITY_MAGIC_STEP, 2, BISHOP),
            (ABILITY_SUPER_JUMP, 3, KNIGHT),
            (ABILITY_SACRIFICE, 2, PAWN)
        ]
        ab_x = self.bottom_panel_rect.x + 12
        ab_y = self.bottom_panel_rect.y + 42
        ab_w = 120
        ab_h = 48

        for name, cost, p_type in ab_list:
            btn_key = f"ability_{name}"
            self.buttons[btn_key] = pygame.Rect(ab_x, ab_y, ab_w, ab_h)
            ab_x += ab_w + 10

    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        """Processes mouse clicks and keyboard shortcuts. Returns action command if any."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos

            # 1. Check Button Clicks
            for name, rect in self.buttons.items():
                if rect.collidepoint(mx, my):
                    return self._on_button_clicked(name)

            # 2. Check Board Clicks
            sq = self.board_renderer.get_square_at_pixel(mx, my)
            if sq is not None:
                self._handle_board_click(sq[0], sq[1])

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                return self._on_button_clicked("pause")
            elif event.key == pygame.K_s:
                return self._on_button_clicked("step")
            elif event.key == pygame.K_u:
                return self._on_button_clicked("undo")
            elif event.key == pygame.K_ESCAPE:
                return "menu"

        return None

    def _on_button_clicked(self, name: str) -> Optional[str]:
        if name == "menu":
            return "menu"
        elif name == "restart":
            self.engine.start_new_match()
            self.selected_pos = None
            self.selected_piece_legal_moves = []
            pts = self.engine.team_material_points.get(TEAM_BLUE, 0)
            self.event_banner_text = f"CSP GENERATOR: FRESH BALANCED ARMIES ({pts:,} PTS EACH)" if pts > 0 else "CSP GENERATOR: FRESH BALANCED ARMIES DEPLOYED"
            self.event_banner_timer = 3.5
            self.sound_mgr.play("ability")
            return None
        elif name == "pause":
            if hasattr(self.mode_controller, "toggle_pause"):
                self.mode_controller.toggle_pause()
            else:
                self.engine.is_paused = not self.engine.is_paused
            return None
        elif name == "step":
            if hasattr(self.mode_controller, "request_step"):
                self.mode_controller.request_step()
            return None
        elif name == "undo":
            if self.mode_name != "ai_vs_ai":
                self.engine.undo_last_move()
                self.selected_pos = None
                self.selected_piece_legal_moves = []
                self.sound_mgr.play("move")
            return None
        elif name.startswith("ability_"):
            ab_name = name.replace("ability_", "")
            self._toggle_ability_targeting(ab_name)
            return None
        return None

    def _toggle_ability_targeting(self, ab_name: str) -> None:
        """Filters legal moves to trigger chosen special ability."""
        if self.selected_pos is None:
            # Auto-select the friendly piece that has this ability if available
            cur_team = self.engine.state.current_turn
            p_type = next((k for k, v in PIECE_ABILITIES.items() if v == ab_name), None)
            if p_type:
                candidates = [
                    p for p in self.engine.state.get_team_pieces(cur_team)
                    if p.piece_type == p_type and p.can_use_ability()
                ]
                if candidates:
                    p = candidates[0]
                    self.selected_pos = (p.row, p.col)
                    all_moves = self.engine.state.get_all_legal_moves()
                    self.selected_piece_legal_moves = [
                        m for m in all_moves
                        if m.start_pos == self.selected_pos and m.is_special_ability and m.ability_name == ab_name
                    ]
                    self.sound_mgr.play("ability")
                    return

        # If already selected, filter to ability moves
        if self.selected_pos:
            all_moves = self.engine.state.get_all_legal_moves()
            ab_moves = [
                m for m in all_moves
                if m.start_pos == self.selected_pos and m.is_special_ability and m.ability_name == ab_name
            ]
            if ab_moves:
                self.selected_piece_legal_moves = ab_moves
                self.sound_mgr.play("ability")

    def _handle_board_click(self, r: int, c: int) -> None:
        # Check if human can move
        is_human = True
        if self.mode_name == "ai_vs_ai":
            is_human = False
        elif self.mode_name == "ai_vs_human":
            is_human = self.mode_controller.is_human_turn()

        if not is_human:
            return

        current_team = self.engine.state.current_turn
        clicked_piece = self.engine.state.board.get_piece(r, c)

        # 1. If clicking a legal target for previously selected piece:
        if self.selected_pos is not None:
            matching_move = next(
                (m for m in self.selected_piece_legal_moves if m.end_pos == (r, c)),
                None
            )
            if matching_move:
                # Execute move
                self._execute_player_move(matching_move)
                self.selected_pos = None
                self.selected_piece_legal_moves = []
                return

        # 2. If clicking own piece, select it
        if clicked_piece and clicked_piece.team == current_team:
            self.selected_pos = (r, c)
            all_moves = self.engine.state.get_all_legal_moves()
            self.selected_piece_legal_moves = [m for m in all_moves if m.start_pos == (r, c)]
            self.sound_mgr.play("move")
        else:
            self.selected_pos = None
            self.selected_piece_legal_moves = []

    def _execute_player_move(self, move: Move) -> None:
        # Spawn visual particles & audio
        if move.is_special_ability:
            px, py = self.board_renderer.get_pixel_pos(*move.end_pos)
            self.particle_sys.spawn_ability_magic(px + 43, py + 43)
            self.sound_mgr.play("ability")
        elif move.is_capture:
            px, py = self.board_renderer.get_pixel_pos(*move.end_pos)
            self.particle_sys.spawn_capture_burst(px + 43, py + 43, move.piece.team)
            self.sound_mgr.play("capture")
        else:
            self.sound_mgr.play("move")

        self.board_renderer.trigger_move_animation(move)
        self.engine.execute_move(move)

    def update(self, dt: float) -> None:
        """Updates game mode loop, AI thinking, animations, and particles."""
        self.particle_sys.update(dt)

        # Check for arena event announcement
        if self.engine.state.battlefield_mgr.last_event_announcement:
            self.event_banner_text = self.engine.state.battlefield_mgr.last_event_announcement
            self.event_banner_timer = 4.0
            self.engine.state.battlefield_mgr.last_event_announcement = None
            self.sound_mgr.play("event")

        if self.event_banner_timer > 0:
            self.event_banner_timer -= dt

        # Update mode controller (runs AI if applicable)
        if hasattr(self.mode_controller, "update"):
            executed_move = self.mode_controller.update()
            if executed_move:
                self.board_renderer.trigger_move_animation(executed_move)
                if executed_move.is_special_ability:
                    self.sound_mgr.play("ability")
                elif executed_move.is_capture:
                    self.sound_mgr.play("capture")
                else:
                    self.sound_mgr.play("move")

    def render(self, surface: pygame.Surface) -> None:
        """Full frame rendering of the tactical battle arena."""
        # 1. Background
        if self.bg_image:
            surface.blit(self.bg_image, (0, 0))
        else:
            surface.fill(COLOR_BG_DARK)

        # 2. Render Left Panel (Red Army)
        self._render_army_panel(surface, TEAM_RED, self.red_panel_rect)

        # 3. Render Right Panel (Blue Army)
        self._render_army_panel(surface, TEAM_BLUE, self.blue_panel_rect)

        # 4. Render Center 7x4 Board
        mx, my = pygame.mouse.get_pos()
        hovered_sq = self.board_renderer.get_square_at_pixel(mx, my)

        self.board_renderer.render(
            surface,
            self.engine.state,
            selected_pos=self.selected_pos,
            legal_moves=self.selected_piece_legal_moves,
            last_move=self.engine.state.last_move,
            hovered_pos=hovered_sq
        )

        # 5. Render Particle System
        self.particle_sys.draw(surface)

        # 6. Render Bottom Action & Abilities HUD
        self._render_bottom_hud(surface)

        # 7. Render Floating Event Announcements / Victory Banner
        self._render_floating_announcements(surface)

        # 8. Render Mouse Hover Tooltip for Pieces
        self._render_piece_hover_tooltip(surface, mx, my, hovered_sq)

    def _render_army_panel(self, surface: pygame.Surface, team: str, rect: pygame.Rect) -> None:
        """Draws team banner, energy crystals, captured piece rack, and AI telemetry."""
        pygame.draw.rect(surface, COLOR_PANEL_BG, rect, border_radius=8)
        border_col = COLOR_RED_PRIMARY if team == TEAM_RED else COLOR_BLUE_PRIMARY
        pygame.draw.rect(surface, border_col, rect, width=2, border_radius=8)

        # Header banner
        header_rect = pygame.Rect(rect.x, rect.y, rect.width, 42)
        pygame.draw.rect(surface, COLOR_PANEL_HEADER, header_rect, border_top_left_radius=8, border_top_right_radius=8)

        name = "RED LEGION" if team == TEAM_RED else "BLUE VANGUARD"
        lbl = self.font_title.render(name, True, (255, 120, 130) if team == TEAM_RED else (120, 210, 255))
        surface.blit(lbl, (rect.x + 14, rect.y + 8))

        # Energy crystal bar
        energy = self.engine.state.energy_system.get_energy(team)
        lbl_en = self.font_body.render(f"ENERGY: {energy} / 10 EP", True, COLOR_TEXT_GOLD)
        surface.blit(lbl_en, (rect.x + 14, rect.y + 50))

        # 10 Energy crystal pips
        pip_w = 23
        pip_h = 14
        start_x = rect.x + 14
        pip_y = rect.y + 74

        for i in range(10):
            p_rect = pygame.Rect(start_x + i * (pip_w + 4), pip_y, pip_w, pip_h)
            if i < energy:
                # Filled glowing crystal
                fill_col = (255, 50, 80) if team == TEAM_RED else (0, 200, 255)
                pygame.draw.rect(surface, fill_col, p_rect, border_radius=3)
                pygame.draw.rect(surface, (255, 255, 255), p_rect, width=1, border_radius=3)
            else:
                # Empty slot
                pygame.draw.rect(surface, (35, 40, 55), p_rect, border_radius=3)
                pygame.draw.rect(surface, (60, 70, 90), p_rect, width=1, border_radius=3)

        # Domination progress
        dom_turns = self.engine.state.red_consecutive_domination if team == TEAM_RED else self.engine.state.blue_consecutive_domination
        lbl_dom = self.font_small.render(f"Domination Streak: {dom_turns} / 3 turns", True, (180, 190, 210))
        surface.blit(lbl_dom, (rect.x + 14, rect.y + 96))

        # CSP Generated Roster Composition & Equal Points
        roster = self.engine.csp_roster_summary.get(team, {})
        if roster:
            parts = []
            order = [(KING, "K"), (QUEEN, "Q"), (ROOK, "R"), (BISHOP, "B"), (KNIGHT, "N"), (PAWN, "P")]
            for p_t, letter in order:
                cnt = roster.get(p_t, 0)
                if cnt > 0:
                    parts.append(f"{letter}:{cnt}")
            roster_str = " ".join(parts)
            lbl_csp_tag = self.font_small.render("CSP ROSTER:", True, COLOR_TEXT_GOLD)
            lbl_roster = self.font_small.render(roster_str, True, (220, 230, 255))
            surface.blit(lbl_csp_tag, (rect.x + 14, rect.y + 114))
            surface.blit(lbl_roster, (rect.x + 88, rect.y + 114))

            # Total points (Strictly equal for both teams)
            pts = self.engine.team_material_points.get(team, 0)
            lbl_pts_tag = self.font_small.render("TOTAL POINTS:", True, (130, 210, 255))
            lbl_pts_val = self.font_small.render(f"{pts:,} PTS  [EQUAL]", True, (46, 204, 113))
            surface.blit(lbl_pts_tag, (rect.x + 14, rect.y + 130))
            surface.blit(lbl_pts_val, (rect.x + 104, rect.y + 130))

        # Captured pieces rack
        lbl_cap = self.font_small.render("CAPTURED OPPONENTS:", True, COLOR_TEXT_MUTED)
        surface.blit(lbl_cap, (rect.x + 14, rect.y + 150))

        captured = self.engine.state.captured_pieces[team]
        cx = rect.x + 14
        cy = rect.y + 168
        for p in captured[:8]:
            key = f"{p.team}_{p.piece_type}"
            spr = self.board_renderer.piece_images.get(key)
            if spr:
                mini = pygame.transform.smoothscale(spr, (24, 24))
                surface.blit(mini, (cx, cy))
                cx += 28
                if cx > rect.right - 35:
                    cx = rect.x + 14
                    cy += 28

        # Render AI Telemetry console inside side panel
        if team == TEAM_RED:
            metrics = getattr(self.mode_controller, "red_metrics", self.engine.last_ai_metrics if self.engine.state.current_turn == TEAM_RED else None)
            is_active = (self.engine.state.current_turn == TEAM_RED and not self.engine.state.is_game_over)
            self.red_ai_panel.render(surface, metrics, team=TEAM_RED, is_active=is_active)
        else:
            metrics = getattr(self.mode_controller, "blue_metrics", self.engine.last_ai_metrics if self.engine.state.current_turn == TEAM_BLUE else None)
            is_active = (self.engine.state.current_turn == TEAM_BLUE and not self.engine.state.is_game_over)
            self.blue_ai_panel.render(surface, metrics, team=TEAM_BLUE, is_active=is_active)

    def _render_bottom_hud(self, surface: pygame.Surface) -> None:
        """Renders action buttons, turn status, and special abilities bar."""
        pygame.draw.rect(surface, COLOR_PANEL_BG, self.bottom_panel_rect, border_radius=8)
        pygame.draw.rect(surface, COLOR_PANEL_BORDER, self.bottom_panel_rect, width=2, border_radius=8)

        # Turn indicator banner
        turn_team = self.engine.state.current_turn
        team_name = "RED LEGION" if turn_team == TEAM_RED else "BLUE VANGUARD"
        team_col = (255, 100, 110) if turn_team == TEAM_RED else (100, 210, 255)
        lbl_turn = self.font_title.render(f"TURN {self.engine.state.turn_count} — {team_name}'S TURN", True, team_col)
        surface.blit(lbl_turn, (self.bottom_panel_rect.x + 14, self.bottom_panel_rect.y + 10))

        # Action Buttons
        for name, rect in self.buttons.items():
            if name.startswith("ability_"):
                self._render_ability_button(surface, name, rect)
            else:
                self._render_action_button(surface, name, rect)

    def _render_action_button(self, surface: pygame.Surface, name: str, rect: pygame.Rect) -> None:
        mouse_pos = pygame.mouse.get_pos()
        hovered = rect.collidepoint(mouse_pos)

        col_bg = (55, 65, 90) if hovered else (35, 42, 60)
        pygame.draw.rect(surface, col_bg, rect, border_radius=6)
        pygame.draw.rect(surface, (100, 120, 160) if hovered else (60, 75, 100), rect, width=1, border_radius=6)

        labels = {
            "menu": "MENU",
            "restart": "RESTART",
            "step": "STEP",
            "pause": "RESUME" if getattr(self.mode_controller, "is_paused", False) else "PAUSE",
            "undo": "UNDO"
        }
        text = labels.get(name, name.upper())
        txt_surf = self.font_body.render(text, True, COLOR_TEXT_WHITE)
        surface.blit(txt_surf, (rect.centerx - txt_surf.get_width() // 2, rect.centery - txt_surf.get_height() // 2))

    def _render_ability_button(self, surface: pygame.Surface, btn_key: str, rect: pygame.Rect) -> None:
        ab_name = btn_key.replace("ability_", "")
        cost = ABILITY_COSTS.get(ab_name, 0)
        cur_team = self.engine.state.current_turn
        cur_energy = self.engine.state.energy_system.get_energy(cur_team)
        can_afford = (cur_energy >= cost)

        mouse_pos = pygame.mouse.get_pos()
        hovered = rect.collidepoint(mouse_pos)

        # Style
        if can_afford:
            bg_col = (70, 45, 95) if hovered else (45, 30, 65)
            border_col = (180, 120, 240) if hovered else (120, 70, 170)
            txt_col = COLOR_TEXT_WHITE
        else:
            bg_col = (25, 25, 35)
            border_col = (50, 50, 65)
            txt_col = (110, 115, 130)

        pygame.draw.rect(surface, bg_col, rect, border_radius=5)
        pygame.draw.rect(surface, border_col, rect, width=1, border_radius=5)

        # Label + Cost
        lbl_name = self.font_small.render(ab_name, True, txt_col)
        lbl_cost = self.font_small.render(f"{cost} EP", True, COLOR_TEXT_GOLD if can_afford else (120, 110, 80))
        surface.blit(lbl_name, (rect.x + 8, rect.y + 6))
        surface.blit(lbl_cost, (rect.x + 8, rect.y + 24))

        if hovered:
            # Draw ability tooltip
            desc = SpecialAbilityManager.get_ability_description(ab_name)
            self._draw_tooltip(surface, desc, rect.x, rect.y - 45)

    def _draw_tooltip(self, surface: pygame.Surface, text: str, x: int, y: int) -> None:
        font = self.font_small
        w, h = font.size(text)
        tip_rect = pygame.Rect(x, y, w + 16, h + 10)
        pygame.draw.rect(surface, (15, 18, 25), tip_rect, border_radius=4)
        pygame.draw.rect(surface, (120, 100, 180), tip_rect, width=1, border_radius=4)
        surface.blit(font.render(text, True, (230, 230, 245)), (x + 8, y + 5))

    def _render_floating_announcements(self, surface: pygame.Surface) -> None:
        """Displays battlefield event popups and game over modal triggers."""
        if self.event_banner_timer > 0 and self.event_banner_text:
            font = self.font_title
            w, h = font.size(self.event_banner_text)
            cx = SCREEN_WIDTH // 2
            banner_rect = pygame.Rect(cx - w // 2 - 20, 10, w + 40, h + 16)

            pygame.draw.rect(surface, (30, 25, 45), banner_rect, border_radius=8)
            pygame.draw.rect(surface, (255, 215, 0), banner_rect, width=2, border_radius=8)

            txt_surf = font.render(self.event_banner_text, True, (255, 230, 120))
            surface.blit(txt_surf, (cx - w // 2, 18))

    def _render_piece_hover_tooltip(
        self,
        surface: pygame.Surface,
        mx: int,
        my: int,
        hovered_sq: Optional[Tuple[int, int]]
    ) -> None:
        """Displays an informative tactical card when hovering over any piece on the board."""
        if not hovered_sq:
            return

        r, c = hovered_sq
        piece = self.engine.state.board.get_piece(r, c)
        if not piece:
            return

        # Prepare details
        team_name = "RED LEGION" if piece.team == TEAM_RED else "BLUE VANGUARD"
        team_col = (255, 110, 125) if piece.team == TEAM_RED else (100, 215, 255)
        border_col = COLOR_RED_PRIMARY if piece.team == TEAM_RED else COLOR_BLUE_PRIMARY

        movement_rules = {
            KING: "Moves 1 square in any of the 8 directions.",
            QUEEN: "Moves any distance along straight & diagonal rays.",
            ROOK: "Moves any distance horizontally or vertically.",
            BISHOP: "Moves any distance along diagonal angles.",
            KNIGHT: "L-shaped jump (2x1) • Vaults over intervening obstacles.",
            PAWN: "Advances 1 square forward • Captures diagonally • Promotes on back row."
        }

        ab_name = piece.special_ability
        ab_cost = ABILITY_COSTS.get(ab_name, 0)
        ab_status = "[READY]" if piece.can_use_ability() else "[USED]"
        ab_status_col = (46, 204, 113) if piece.can_use_ability() else (140, 145, 160)

        # Build lines
        title_text = f"{team_name} — {piece.piece_type.upper()}"
        move_text = movement_rules.get(piece.piece_type, "")
        ability_text = f"Special: {ab_name} ({ab_cost} EP)  {ab_status}"
        value_text = f"Tactical Material Value: {piece.value} pts"

        font_head = pygame.font.SysFont("segoeui", 14, bold=True)
        font_sub = pygame.font.SysFont("segoeui", 12)
        font_small = pygame.font.SysFont("segoeui", 11)

        # Card layout dimensions
        card_w = 320
        card_h = 118
        if piece.shielded or piece.frozen_turns > 0:
            card_h += 22

        # Position clamped to screen
        tx = mx + 16
        ty = my - 20
        if tx + card_w > SCREEN_WIDTH - 20:
            tx = mx - card_w - 16
        if ty + card_h > SCREEN_HEIGHT - 20:
            ty = SCREEN_HEIGHT - card_h - 20
        if ty < 20:
            ty = 20

        tip_rect = pygame.Rect(tx, ty, card_w, card_h)

        # Drop shadow
        shadow_rect = pygame.Rect(tx + 4, ty + 4, card_w, card_h)
        pygame.draw.rect(surface, (10, 12, 16), shadow_rect, border_radius=8)

        # Card body
        pygame.draw.rect(surface, (20, 24, 36), tip_rect, border_radius=8)
        pygame.draw.rect(surface, border_col, tip_rect, width=2, border_radius=8)

        # Header bar
        head_rect = pygame.Rect(tx, ty, card_w, 28)
        pygame.draw.rect(surface, (30, 36, 52), head_rect, border_top_left_radius=8, border_top_right_radius=8)
        surface.blit(font_head.render(title_text, True, team_col), (tx + 12, ty + 4))

        # Content lines
        cur_y = ty + 34
        surface.blit(font_small.render(value_text, True, (160, 175, 200)), (tx + 12, cur_y))
        cur_y += 18

        surface.blit(font_sub.render(move_text, True, COLOR_TEXT_WHITE), (tx + 12, cur_y))
        cur_y += 20

        # Ability Line
        ab_surf = font_sub.render(f"Special: {ab_name} ({ab_cost} EP)", True, COLOR_TEXT_GOLD)
        surface.blit(ab_surf, (tx + 12, cur_y))
        stat_surf = font_sub.render(ab_status, True, ab_status_col)
        surface.blit(stat_surf, (tx + 16 + ab_surf.get_width(), cur_y))
        cur_y += 22

        # Status modifiers if shielded or frozen
        if piece.shielded:
            shield_surf = font_small.render("🛡️ PROTECTED: Divine shield active (absorbs next capture)", True, (255, 225, 100))
            surface.blit(shield_surf, (tx + 12, cur_y))
            cur_y += 18
        elif piece.frozen_turns > 0:
            frozen_surf = font_small.render(f"❄️ FROZEN: Movement immobilized for {piece.frozen_turns} turn(s)", True, (120, 230, 255))
            surface.blit(frozen_surf, (tx + 12, cur_y))
            cur_y += 18

