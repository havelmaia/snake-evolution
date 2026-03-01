import sys
import os


def resource_path(relative_path):
    """Retorna o caminho correto para assets, funciona tanto em dev quanto empacotado."""
    if getattr(sys, 'frozen', False):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, relative_path)


def user_data_path(filename):
    """Retorna caminho para dados do usuário (settings, saves)."""
    if getattr(sys, 'frozen', False):
        # Empacotado: usa pasta do executável
        base = os.path.dirname(sys.executable)
    else:
        # Dev: usa raiz do projeto
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, filename)


# TELA

CELL_SIZE = 32
GRID_COLS = 24
GRID_ROWS = 16

# Borda decorativa ao redor do grid (em células)
BORDER_SIZE = 2

# Área jogável em pixels
SCREEN_WIDTH = CELL_SIZE * GRID_COLS
SCREEN_HEIGHT = CELL_SIZE * GRID_ROWS

# Header
HEADER_HEIGHT = 56

# Janela total = grid + borda + header
BORDER_PX = BORDER_SIZE * CELL_SIZE
WINDOW_WIDTH = SCREEN_WIDTH + BORDER_PX * 2
WINDOW_HEIGHT = SCREEN_HEIGHT + BORDER_PX * 2 + HEADER_HEIGHT

# Offset do grid (onde começa a área jogável)
GRID_OFFSET_X = BORDER_PX
GRID_OFFSET_Y = HEADER_HEIGHT + BORDER_PX

FPS = 60

# CORES

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

GRID_LIGHT = (170, 215, 81)
GRID_DARK  = (162, 209, 73)
HEADER_COLOR = (74, 117, 44)
HEADER_SHADOW = (55, 90, 30)

# Borda / terreno
BORDER_COLOR     = (140, 100, 50)
BORDER_DARK      = (110, 75,  35)
BORDER_GRASS     = (100, 170, 50)
BORDER_GRASS_ALT = (85,  150, 40)

SNAKE_HEAD_COLOR  = (100, 120, 220)
SNAKE_BODY_COLOR  = (100, 120, 220)
SNAKE_BODY_ALT    = (85,  100, 195)
SNAKE_BOOST_HEAD  = (80,  180, 255)
SNAKE_BOOST_BODY  = (60,  150, 240)
SNAKE_BOOST_ALT   = (50,  130, 210)

FRUIT_COLOR        = (255, 60,  60)
FRUIT_GLOW         = (255, 120, 120)
FRUIT_GOLDEN_COLOR = (255, 215, 0)
FRUIT_GOLDEN_GLOW  = (255, 235, 100)
FRUIT_SPEED_COLOR  = (130, 40,  160)
FRUIT_SPEED_GLOW   = (180, 100, 210)
FRUIT_POISON_COLOR = (50, 220, 50) 
FRUIT_POISON_GLOW  = (120, 255, 120)

TEXT_COLOR      = (255, 255, 255)
TEXT_SECONDARY  = (200, 230, 160)
SCORE_COLOR     = (255, 255, 255)

TITLE_COLOR     = (255, 255, 255)
TITLE_GLOW      = (200, 230, 160)

GAMEOVER_COLOR  = (220, 50, 50)
GAMEOVER_GLOW   = (140, 20, 20)

# JOGO

SNAKE_SPEED            = 6
SPEED_INCREMENT        = 1
MAX_SPEED              = 16
SPEED_BOOST_AMOUNT     = 5
SPEED_BOOST_DURATION   = 80

POINTS_NORMAL = 10
POINTS_GOLDEN = 50
POINTS_SPEED  = 20
POINTS_POISON = 30

SPECIAL_FRUIT_INTERVAL = 30
SPECIAL_FRUIT_CHANCE   = 0.8
SPECIAL_FRUIT_LIFETIME = 300

# PARTÍCULAS

PARTICLE_COUNT    = 12
PARTICLE_SPEED    = 3.0
PARTICLE_LIFETIME = 25
PARTICLE_SIZE     = 4

# DIREÇÕES

DIR_UP    = (0, -1)
DIR_DOWN  = (0,  1)
DIR_LEFT  = (-1, 0)
DIR_RIGHT = (1,  0)

# SPRITES

SPRITE_CELL = 32
SPRITE_PATH = resource_path("assets/sprites/snake.png")
FRUIT_SPRITE_PATH = resource_path("assets/sprites/fruits.png")
DECO_SPRITE_PATH = resource_path("assets/sprites/decorations.png")

SFX_EAT      = resource_path("assets/sounds/eat.ogg")
SFX_SPECIAL   = resource_path("assets/sounds/special.ogg")
SFX_GAMEOVER  = resource_path("assets/sounds/gameover.ogg")
SFX_SPEED     = resource_path("assets/sounds/speed.ogg")
SFX_POISON    = resource_path("assets/sounds/poison.ogg")
BGM_MENU      = resource_path("assets/sounds/menu_bgm.ogg")
BGM_GAME      = resource_path("assets/sounds/game_bgm.ogg")

FONT_TITLE = resource_path("assets/fonts/PressStart2P.ttf")
FONT_BODY  = resource_path("assets/fonts/Silkscreen.ttf")
FONT_BOLD  = resource_path("assets/fonts/Silkscreen-Bold.ttf")

SPR_HEAD_RIGHT  = 0
SPR_HEAD_LEFT   = 1
SPR_HEAD_UP     = 2
SPR_HEAD_DOWN   = 3
SPR_BODY_H      = 4
SPR_BODY_V      = 5
SPR_CORNER_BL   = 6
SPR_CORNER_BR   = 7
SPR_CORNER_TL   = 8
SPR_CORNER_TR   = 9
SPR_TAIL_RIGHT  = 10
SPR_TAIL_LEFT   = 11
SPR_TAIL_UP     = 12
SPR_TAIL_DOWN   = 13
