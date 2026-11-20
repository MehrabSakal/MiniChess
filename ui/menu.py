"""
Chaos Chess - Main Menu Screen
"""
import os
import math
import random
import pygame
from typing import Optional, Dict
from config import SCREEN_WIDTH, SCREEN_HEIGHT, ASSETS_DIR, COLOR_TEXT_GOLD, COLOR_TEXT_WHITE
from ui.sound_manager import SoundManager
from ui.particles import ParticleSystem


class MainMenu:
    """Main Menu screen with fantasy tavern backdrop, particle embers, and navigation."""

    def __init__(self):
        self.sound_mgr = SoundManager.get_instance()
        self.particle_sys = ParticleSystem()
        self.bg_image: Optional[pygame.Surface] = None
        self._load_background()

        # Fonts
        self.font_title = pygame.font.SysFont("georgia", 64, bold=True)
        self.font_subtitle = pygame.font.SysFont("segoeui", 18, bold=True)
        self.font_btn = pygame.font.SysFont("segoeui", 20, bold=True)
        self.font_footer = pygame.font.SysFont("segoeui", 12)

        # Buttons
        cx = SCREEN_WIDTH // 2
        btn_w, btn_h = 320, 54
        start_y = 310
        spacing = 70

        self.buttons = {
            "play": pygame.Rect(cx - btn_w // 2, start_y, btn_w, btn_h),
            "arena": pygame.Rect(cx - btn_w // 2, start_y + spacing, btn_w, btn_h),
            "how_to_play": pygame.Rect(cx - btn_w // 2, start_y + spacing * 2, btn_w, btn_h),
            "settings": pygame.Rect(cx - btn_w // 2, start_y + spacing * 3, btn_w, btn_h),
            "exit": pygame.Rect(cx - btn_w // 2, start_y + spacing * 4, btn_w, btn_h),
        }

        self.time_phase = 0.0

    def _load_background(self) -> None:
        bg_path = os.path.join(ASSETS_DIR, "images", "backgrounds", "arena_tavern.jpg")
        if os.path.exists(bg_path):
            try:
                raw = pygame.image.load(bg_path).convert()
                scaled = pygame.transform.smoothscale(raw, (SCREEN_WIDTH, SCREEN_HEIGHT))
                dark_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                dark_overlay.fill((12, 14, 22, 180))
                scaled.blit(dark_overlay, (0, 0))
                self.bg_image = scaled
            except Exception:
                self.bg_image = None

    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            for name, rect in self.buttons.items():
                if rect.collidepoint(mx, my):
                    self.sound_mgr.play("move")
                    return name
        return None

    def update(self, dt: float) -> None:
        self.time_phase += dt
        self.particle_sys.update(dt)

        # Ambient floating embers
        if random.random() < 0.25:
            x = random.uniform(50, SCREEN_WIDTH - 50)
            y = SCREEN_HEIGHT + 10
            vx = random.uniform(-15, 15)
            vy = random.uniform(-40, -100)
            col = random.choice([(255, 180, 50), (255, 120, 40), (255, 230, 100)])
            from ui.particles import Particle
            self.particle_sys.particles.append(Particle(x, y, vx, vy, col, radius=random.uniform(1.5, 3.5), lifetime=3.5))

    def render(self, surface: pygame.Surface) -> None:
        if self.bg_image:
            surface.blit(self.bg_image, (0, 0))
        else:
            surface.fill((16, 18, 27))

        self.particle_sys.draw(surface)

        # Grand Title
        cx = SCREEN_WIDTH // 2
        title_y = 100

        # Title shadow & glow
        pulse = math.sin(self.time_phase * 2.0) * 10
        title_surf = self.font_title.render("CHAOS CHESS", True, (255, 215, 60))
        shadow_surf = self.font_title.render("CHAOS CHESS", True, (30, 20, 10))

        surface.blit(shadow_surf, (cx - title_surf.get_width() // 2 + 4, title_y + 4))
        surface.blit(title_surf, (cx - title_surf.get_width() // 2, title_y))

        # Subtitle
        sub_text = "AN AI-POWERED TACTICAL ARENA GAME"
        sub_surf = self.font_subtitle.render(sub_text, True, (160, 200, 255))
        surface.blit(sub_surf, (cx - sub_surf.get_width() // 2, title_y + 80))

        # Decorative sword divider line
        line_w = 420
        pygame.draw.line(surface, (120, 140, 180), (cx - line_w // 2, title_y + 115), (cx + line_w // 2, title_y + 115), 2)
        pygame.draw.circle(surface, (255, 215, 0), (cx, title_y + 115), 5)

        # Buttons
        mouse_pos = pygame.mouse.get_pos()
        labels = {
            "play": "PLAY GAME",
            "arena": "AI ALGORITHM ARENA",
            "how_to_play": "HOW TO PLAY",
            "settings": "SETTINGS",
            "exit": "EXIT ARENA"
        }

        for name, rect in self.buttons.items():
            hovered = rect.collidepoint(mouse_pos)
            bg_col = (45, 55, 80) if hovered else (28, 32, 46)
            border_col = (255, 215, 0) if hovered else (70, 85, 115)
            border_w = 2 if hovered else 1

            pygame.draw.rect(surface, bg_col, rect, border_radius=8)
            pygame.draw.rect(surface, border_col, rect, width=border_w, border_radius=8)

            txt_col = (255, 240, 160) if hovered else COLOR_TEXT_WHITE
            text = labels.get(name, name.upper())
            txt_surf = self.font_btn.render(text, True, txt_col)
            surface.blit(txt_surf, (rect.centerx - txt_surf.get_width() // 2, rect.centery - txt_surf.get_height() // 2))

        # Footer
        footer = self.font_footer.render("7x4 Tactical Battlefield • 8 AI Algorithms • Dynamic Energy & Events", True, (120, 130, 150))
        surface.blit(footer, (cx - footer.get_width() // 2, SCREEN_HEIGHT - 35))

