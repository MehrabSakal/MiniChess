"""
Chaos Chess - Settings Configuration Screen
"""
import json
import pygame
from typing import Optional, Dict, Any
from config import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_TEXT_GOLD, COLOR_TEXT_WHITE, COLOR_PANEL_BG, SETTINGS_FILE
from ui.sound_manager import SoundManager


class SettingsScreen:
    """Configures battlefield events, turn limits, AI speed, and audio."""

    def __init__(self):
        self.sound_mgr = SoundManager.get_instance()
        self.font_title = pygame.font.SysFont("georgia", 32, bold=True)
        self.font_header = pygame.font.SysFont("segoeui", 16, bold=True)
        self.font_body = pygame.font.SysFont("segoeui", 14)

        self.back_button = pygame.Rect(40, 35, 100, 38)
        self.save_button = pygame.Rect(SCREEN_WIDTH - 160, 35, 120, 38)

        # Settings model
        self.settings = self._load_settings()

        # Options
        self.freq_options = [4, 6, 8, 12]
        self.turn_limit_options = [50, 75, 100, 150]
        self.ai_delay_options = [100, 300, 500, 800]

        # UI Clickable rectangles
        self.rect_events_toggle = pygame.Rect(450, 130, 120, 36)
        self.freq_rects = [pygame.Rect(450 + i * 85, 195, 75, 36) for i in range(4)]
        self.turn_rects = [pygame.Rect(450 + i * 85, 260, 75, 36) for i in range(4)]
        self.delay_rects = [pygame.Rect(450 + i * 85, 325, 75, 36) for i in range(4)]
        self.rect_sound_toggle = pygame.Rect(450, 390, 120, 36)
        self.vol_rects = [pygame.Rect(450 + i * 85, 455, 75, 36) for i in range(4)]
        self.rect_csp_toggle = pygame.Rect(450, 520, 170, 36)

        self.status_msg = "Settings loaded."

    def _load_settings(self) -> Dict[str, Any]:
        try:
            with open(SETTINGS_FILE, "r") as f:
                data = json.load(f)
                if "use_csp_armies" not in data:
                    data["use_csp_armies"] = True
                return data
        except Exception:
            return {
                "random_events_enabled": True,
                "event_frequency_turns": 8,
                "turn_limit": 100,
                "sound_enabled": True,
                "sound_volume": 0.7,
                "ai_move_delay_ms": 300,
                "use_csp_armies": True
            }

    def _save_settings(self) -> None:
        try:
            with open(SETTINGS_FILE, "w") as f:
                json.dump(self.settings, f, indent=2)
            self.status_msg = "Settings saved successfully!"
        except Exception:
            self.status_msg = "Failed to save settings."

    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos

            if self.back_button.collidepoint(mx, my):
                self.sound_mgr.play("move")
                return "menu"

            if self.save_button.collidepoint(mx, my):
                self._save_settings()
                self.sound_mgr.play("ability")
                return None

            # Events Toggle
            if self.rect_events_toggle.collidepoint(mx, my):
                self.settings["random_events_enabled"] = not self.settings.get("random_events_enabled", True)
                self.sound_mgr.play("move")

            # Frequency
            for i, r in enumerate(self.freq_rects):
                if r.collidepoint(mx, my):
                    self.settings["event_frequency_turns"] = self.freq_options[i]
                    self.sound_mgr.play("move")

            # Turn Limit
            for i, r in enumerate(self.turn_rects):
                if r.collidepoint(mx, my):
                    self.settings["turn_limit"] = self.turn_limit_options[i]
                    self.sound_mgr.play("move")

            # AI Delay
            for i, r in enumerate(self.delay_rects):
                if r.collidepoint(mx, my):
                    self.settings["ai_move_delay_ms"] = self.ai_delay_options[i]
                    self.sound_mgr.play("move")

            # Sound Toggle
            if self.rect_sound_toggle.collidepoint(mx, my):
                self.settings["sound_enabled"] = not self.settings.get("sound_enabled", True)
                self.sound_mgr.sound_enabled = self.settings["sound_enabled"]
                self.sound_mgr.play("move")

            # Volume
            vol_levels = [0.25, 0.5, 0.75, 1.0]
            for i, r in enumerate(self.vol_rects):
                if r.collidepoint(mx, my):
                    self.settings["sound_volume"] = vol_levels[i]
                    self.sound_mgr.set_volume(vol_levels[i])
                    self.sound_mgr.play("move")

            # CSP Army Randomization Toggle
            if self.rect_csp_toggle.collidepoint(mx, my):
                self.settings["use_csp_armies"] = not self.settings.get("use_csp_armies", True)
                self.sound_mgr.play("move")

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

        # Save Button
        s_hover = self.save_button.collidepoint(mouse_pos)
        pygame.draw.rect(surface, (45, 65, 45) if s_hover else (28, 45, 28), self.save_button, border_radius=6)
        pygame.draw.rect(surface, (46, 204, 113), self.save_button, width=1, border_radius=6)
        lbl_s = self.font_body.render("SAVE", True, (160, 255, 180))
        surface.blit(lbl_s, (self.save_button.centerx - lbl_s.get_width() // 2, self.save_button.centery - lbl_s.get_height() // 2))

        # Title
        t_surf = self.font_title.render("GAME & SIMULATION SETTINGS", True, COLOR_TEXT_GOLD)
        surface.blit(t_surf, (180, 35))

        # Panel Container
        panel_rect = pygame.Rect(40, 95, SCREEN_WIDTH - 80, 610)
        pygame.draw.rect(surface, COLOR_PANEL_BG, panel_rect, border_radius=10)
        pygame.draw.rect(surface, (60, 70, 95), panel_rect, width=1, border_radius=10)

        # Labels
        lx = 80
        items = [
            ("Random Battlefield Events:", 135),
            ("Event Frequency (Turns):", 200),
            ("Match Turn Limit:", 265),
            ("AI Move Delay (ms):", 330),
            ("Master Audio:", 395),
            ("Sound Effects Volume:", 460),
            ("CSP Army Randomization:", 525)
        ]
        for text, y in items:
            lbl = self.font_header.render(text, True, COLOR_TEXT_WHITE)
            surface.blit(lbl, (lx, y))

        # 1. Events Toggle Button
        ev_on = self.settings.get("random_events_enabled", True)
        pygame.draw.rect(surface, (35, 65, 40) if ev_on else (65, 30, 35), self.rect_events_toggle, border_radius=6)
        pygame.draw.rect(surface, (46, 204, 113) if ev_on else (231, 76, 60), self.rect_events_toggle, width=1, border_radius=6)
        lbl_ev = self.font_body.render("ENABLED" if ev_on else "DISABLED", True, COLOR_TEXT_WHITE)
        surface.blit(lbl_ev, (self.rect_events_toggle.centerx - lbl_ev.get_width() // 2, self.rect_events_toggle.centery - lbl_ev.get_height() // 2))

        # 2. Frequency Buttons
        cur_freq = self.settings.get("event_frequency_turns", 8)
        for i, (val, rect) in enumerate(zip(self.freq_options, self.freq_rects)):
            is_sel = (val == cur_freq)
            pygame.draw.rect(surface, (55, 65, 95) if is_sel else (25, 30, 45), rect, border_radius=6)
            pygame.draw.rect(surface, COLOR_TEXT_GOLD if is_sel else (60, 70, 90), rect, width=2 if is_sel else 1, border_radius=6)
            txt = self.font_body.render(f"Every {val}", True, COLOR_TEXT_GOLD if is_sel else COLOR_TEXT_WHITE)
            surface.blit(txt, (rect.centerx - txt.get_width() // 2, rect.centery - txt.get_height() // 2))

        # 3. Turn Limit Buttons
        cur_lim = self.settings.get("turn_limit", 100)
        for i, (val, rect) in enumerate(zip(self.turn_limit_options, self.turn_rects)):
            is_sel = (val == cur_lim)
            pygame.draw.rect(surface, (55, 65, 95) if is_sel else (25, 30, 45), rect, border_radius=6)
            pygame.draw.rect(surface, COLOR_TEXT_GOLD if is_sel else (60, 70, 90), rect, width=2 if is_sel else 1, border_radius=6)
            txt = self.font_body.render(f"{val} Turns", True, COLOR_TEXT_GOLD if is_sel else COLOR_TEXT_WHITE)
            surface.blit(txt, (rect.centerx - txt.get_width() // 2, rect.centery - txt.get_height() // 2))

        # 4. AI Delay Buttons
        cur_delay = self.settings.get("ai_move_delay_ms", 300)
        for i, (val, rect) in enumerate(zip(self.ai_delay_options, self.delay_rects)):
            is_sel = (val == cur_delay)
            pygame.draw.rect(surface, (55, 65, 95) if is_sel else (25, 30, 45), rect, border_radius=6)
            pygame.draw.rect(surface, COLOR_TEXT_GOLD if is_sel else (60, 70, 90), rect, width=2 if is_sel else 1, border_radius=6)
            txt = self.font_body.render(f"{val} ms", True, COLOR_TEXT_GOLD if is_sel else COLOR_TEXT_WHITE)
            surface.blit(txt, (rect.centerx - txt.get_width() // 2, rect.centery - txt.get_height() // 2))

        # 5. Audio Toggle
        snd_on = self.settings.get("sound_enabled", True)
        pygame.draw.rect(surface, (35, 65, 40) if snd_on else (65, 30, 35), self.rect_sound_toggle, border_radius=6)
        pygame.draw.rect(surface, (46, 204, 113) if snd_on else (231, 76, 60), self.rect_sound_toggle, width=1, border_radius=6)
        lbl_snd = self.font_body.render("MUTED" if not snd_on else "ON", True, COLOR_TEXT_WHITE)
        surface.blit(lbl_snd, (self.rect_sound_toggle.centerx - lbl_snd.get_width() // 2, self.rect_sound_toggle.centery - lbl_snd.get_height() // 2))

        # 6. Volume Levels
        cur_vol = self.settings.get("sound_volume", 0.7)
        vol_levels = [0.25, 0.5, 0.75, 1.0]
        vol_labels = ["25%", "50%", "75%", "100%"]
        for i, (lvl, rect) in enumerate(zip(vol_levels, self.vol_rects)):
            is_sel = (abs(lvl - cur_vol) < 0.15)
            pygame.draw.rect(surface, (55, 65, 95) if is_sel else (25, 30, 45), rect, border_radius=6)
            pygame.draw.rect(surface, COLOR_TEXT_GOLD if is_sel else (60, 70, 90), rect, width=2 if is_sel else 1, border_radius=6)
            txt = self.font_body.render(vol_labels[i], True, COLOR_TEXT_GOLD if is_sel else COLOR_TEXT_WHITE)
            surface.blit(txt, (rect.centerx - txt.get_width() // 2, rect.centery - txt.get_height() // 2))

        # 7. CSP Army Randomization Toggle
        csp_on = self.settings.get("use_csp_armies", True)
        pygame.draw.rect(surface, (35, 65, 40) if csp_on else (65, 30, 35), self.rect_csp_toggle, border_radius=6)
        pygame.draw.rect(surface, (46, 204, 113) if csp_on else (231, 76, 60), self.rect_csp_toggle, width=1, border_radius=6)
        lbl_csp = self.font_body.render("RANDOM (CSP)" if csp_on else "STANDARD FIXED", True, COLOR_TEXT_WHITE)
        surface.blit(lbl_csp, (self.rect_csp_toggle.centerx - lbl_csp.get_width() // 2, self.rect_csp_toggle.centery - lbl_csp.get_height() // 2))

        # Status footer
        lbl_msg = self.font_body.render(self.status_msg, True, (160, 200, 255))
        surface.blit(lbl_msg, (lx, 580))

