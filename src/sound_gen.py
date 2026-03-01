import pygame
from .config import SFX_EAT, SFX_SPECIAL, SFX_GAMEOVER, SFX_SPEED, SFX_POISON, BGM_MENU, BGM_GAME


class SoundManager:
    def __init__(self):
        self.enabled = True
        self.sfx_enabled = True
        self.music_enabled = True
        self.current_music = None
        self.sfx_volume = 0.8
        self.music_volume = 0.8

        try:
            self.eat = pygame.mixer.Sound(SFX_EAT)
            self.special = pygame.mixer.Sound(SFX_SPECIAL)
            self.gameover = pygame.mixer.Sound(SFX_GAMEOVER)
            self.speed = pygame.mixer.Sound(SFX_SPEED)
            self.poison = pygame.mixer.Sound(SFX_POISON)

            self._apply_sfx_volume()
        except Exception as e:
            print(f"Aviso: Não foi possível carregar os efeitos sonoros. Erro: {e}")
            self.enabled = False

    def _apply_sfx_volume(self):
        if not self.enabled:
            return
        self.eat.set_volume(self.sfx_volume * 0.3)
        self.special.set_volume(self.sfx_volume * 0.4)
        self.gameover.set_volume(self.sfx_volume * 0.5)
        self.speed.set_volume(self.sfx_volume * 0.4)
        self.poison.set_volume(self.sfx_volume * 0.5)

    def set_sfx_volume(self, volume):
        self.sfx_volume = max(0.0, min(1.0, volume))
        self._apply_sfx_volume()

    def set_music_volume(self, volume):
        self.music_volume = max(0.0, min(1.0, volume))
        if self.current_music:
            pygame.mixer.music.set_volume(self.music_volume * 0.25)

    def set_sfx_enabled(self, enabled):
        self.sfx_enabled = enabled

    def set_music_enabled(self, enabled):
        self.music_enabled = enabled
        if not enabled:
            self.stop_music()

    def play_eat(self):
        if self.enabled and self.sfx_enabled:
            self.eat.play()

    def play_special(self):
        if self.enabled and self.sfx_enabled:
            self.special.play()

    #Som das uvas
    def play_speed(self):
        if self.enabled:
            self.speed.play()

    def play_gameover(self):
        if self.enabled and self.sfx_enabled:
            self.gameover.play()

    def play_menu_music(self):
        if not self.enabled or not self.music_enabled or self.current_music == "menu":
            return
        try:
            pygame.mixer.music.load(BGM_MENU)
            pygame.mixer.music.set_volume(self.music_volume * 0.25)
            pygame.mixer.music.play(-1)
            self.current_music = "menu"
        except Exception as e:
            print(f"Aviso: Música do menu não encontrada. {e}")

    def play_game_music(self):
        if not self.enabled or not self.music_enabled or self.current_music == "game":
            return
        try:
            pygame.mixer.music.load(BGM_GAME)
            pygame.mixer.music.set_volume(self.music_volume * 0.25)
            pygame.mixer.music.play(-1)
            self.current_music = "game"
        except Exception as e:
            print(f"Aviso: Música do jogo não encontrada. {e}")

    def play_poison(self):
        if self.enabled and self.sfx_enabled:
            self.poison.play()

    def stop_music(self):
        if self.enabled:
            pygame.mixer.music.stop()
            self.current_music = None
