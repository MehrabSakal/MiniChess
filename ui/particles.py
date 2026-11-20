"""
Chaos Chess - Particle Effects System
"""
import random
import math
import pygame
from typing import List, Tuple


class Particle:
    """Individual visual particle with velocity, color, and life cycle."""

    def __init__(
        self,
        x: float,
        y: float,
        vx: float,
        vy: float,
        color: Tuple[int, int, int],
        radius: float = 3.0,
        lifetime: float = 0.5,
        fade: bool = True
    ):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.radius = radius
        self.max_life = lifetime
        self.life = lifetime
        self.fade = fade

    def update(self, dt: float) -> bool:
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.life -= dt
        return self.life > 0.0

    def draw(self, surface: pygame.Surface) -> None:
        if self.life <= 0:
            return
        alpha = int(255 * (self.life / self.max_life)) if self.fade else 255
        rad = max(1, int(self.radius * (self.life / self.max_life)))
        s = pygame.Surface((rad * 2 + 2, rad * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, alpha), (rad + 1, rad + 1), rad)
        surface.blit(s, (int(self.x - rad), int(self.y - rad)))


class ParticleSystem:
    """Manages tactical particle bursts, sparks, and atmospheric motes."""

    def __init__(self):
        self.particles: List[Particle] = []

    def update(self, dt: float) -> None:
        self.particles = [p for p in self.particles if p.update(dt)]

    def draw(self, surface: pygame.Surface) -> None:
        for p in self.particles:
            p.draw(surface)

    def spawn_capture_burst(self, x: float, y: float, team: str) -> None:
        """Explosion of sparks on piece capture."""
        base_color = (255, 60, 90) if team == "red" else (40, 200, 255)
        for _ in range(24):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(60, 240)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            life = random.uniform(0.3, 0.7)
            col = random.choice([base_color, (255, 230, 100), (255, 255, 255)])
            self.particles.append(Particle(x, y, vx, vy, col, radius=random.uniform(2, 4.5), lifetime=life))

    def spawn_shield_burst(self, x: float, y: float) -> None:
        """Golden crystalline shards when shield breaks."""
        for _ in range(18):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(40, 180)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            self.particles.append(Particle(
                x, y, vx, vy, (255, 220, 80), radius=random.uniform(2.5, 4.0), lifetime=0.45
            ))

    def spawn_ability_magic(self, x: float, y: float) -> None:
        """Arcane purple magic aura particles."""
        for _ in range(20):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(30, 120)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            self.particles.append(Particle(
                x, y, vx, vy, (180, 80, 255), radius=random.uniform(2, 4), lifetime=0.5
            ))

