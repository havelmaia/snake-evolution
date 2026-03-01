import pygame

class SoundManager:
    def __init__(self):
        self.enabled = True
        self.current_music = None
        
        try:
            # === EFEITOS SONOROS ===
            self.eat = pygame.mixer.Sound('assets/sounds/eat.ogg')# COMIDA NORMAL
            self.special = pygame.mixer.Sound('assets/sounds/special.ogg') # COMIDA ESPECIAL
            self.gameover = pygame.mixer.Sound('assets/sounds/gameover.ogg') # GAME OVER
            
            self.eat.set_volume(0.5)
            self.special.set_volume(0.6)
            self.gameover.set_volume(0.8)
            
        except Exception as e:
            print(f"Aviso: Não foi possível carregar os efeitos sonoros. Erro: {e}")
            self.enabled = False

    def play_eat(self):
        if self.enabled:
            self.eat.play()

    def play_special(self):
        if self.enabled:
            self.special.play()

    def play_gameover(self):
        if self.enabled:
            self.gameover.play()

    # === MÚSICAS DE FUNDO ===
    def play_menu_music(self):
        if not self.enabled or self.current_music == "menu":
            return
        try:
            pygame.mixer.music.load('assets/sounds/menu_bgm.ogg')# MÚSICA DE FUNDO DE MENUS
            pygame.mixer.music.set_volume(0.3)
            pygame.mixer.music.play(-1)
            self.current_music = "menu"
        except Exception as e:
            print(f"Aviso: Música do menu não encontrada. {e}")

    def play_game_music(self):
        if not self.enabled or self.current_music == "game":
            return
        try:
            pygame.mixer.music.load('assets/sounds/game_bgm.ogg') # MÚSICA DE FUNDO EM JOGO
            pygame.mixer.music.set_volume(0.4)
            pygame.mixer.music.play(-1)
            self.current_music = "game"
        except Exception as e:
            print(f"Aviso: Música do jogo não encontrada. {e}")
            
    def stop_music(self):
        if self.enabled:
            pygame.mixer.music.stop()
            self.current_music = None