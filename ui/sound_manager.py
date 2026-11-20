"""
Chaos Chess - Safe Audio & Sound Effects Manager
"""
import os
import pygame
from typing import Dict, Optional
from config import ASSETS_DIR


class SoundManager:
    """Manages tactical audio cues with fallback if sound hardware is absent."""

    _instance: Optional['SoundManager'] = None

    def __init__(self):
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.sound_enabled: bool = True
        self.volume: float = 0.7
        self._init_mixer()

    @classmethod
    def get_instance(cls) -> 'SoundManager':
        if cls._instance is None:
            cls._instance = SoundManager()
        return cls._instance

    def _init_mixer(self) -> None:
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            self._load_sounds()
        except Exception:
            self.sound_enabled = False

    def _load_sounds(self) -> None:
        sounds_dir = os.path.join(ASSETS_DIR, "sounds")
        sound_files = ["move", "capture", "shield", "ability", "event", "victory"]

        for name in sound_files:
            path = os.path.join(sounds_dir, f"{name}.wav")
            if os.path.exists(path):
                try:
                    s = pygame.mixer.Sound(path)
                    s.set_volume(self.volume)
                    self.sounds[name] = s
                except Exception:
                    pass

    def play(self, sound_name: str) -> None:
        if not self.sound_enabled:
            return
        snd = self.sounds.get(sound_name)
        if snd:
            try:
                snd.play()
            except Exception:
                pass

    def set_volume(self, volume: float) -> None:
        self.volume = max(0.0, min(1.0, volume))
        for snd in self.sounds.values():
            try:
                snd.set_volume(self.volume)
            except Exception:
                pass

    def toggle_sound(self) -> bool:
        self.sound_enabled = not self.sound_enabled
        return self.sound_enabled

