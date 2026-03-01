import pygame
import random
from enum import Enum, auto
from ..config import (
    CELL_SIZE, GRID_OFFSET_X, GRID_OFFSET_Y, GRID_COLS, GRID_ROWS,
    FRUIT_COLOR, FRUIT_GLOW,
    FRUIT_GOLDEN_COLOR, FRUIT_GOLDEN_GLOW,
    FRUIT_SPEED_COLOR, FRUIT_SPEED_GLOW,
    POINTS_NORMAL, POINTS_GOLDEN, POINTS_SPEED,
    FRUIT_POISON_COLOR, FRUIT_POISON_GLOW,
    POINTS_NORMAL, POINTS_GOLDEN, POINTS_SPEED, POINTS_POISON,
    SPECIAL_FRUIT_LIFETIME,
    FRUIT_SPRITE_PATH, SPRITE_CELL,
)


class FruitType(Enum):
    NORMAL = auto()
    GOLDEN = auto()
    SPEED = auto()
    POISON = auto()


FRUIT_CONFIG = {
    FruitType.NORMAL: {
        "color": FRUIT_COLOR,
        "glow": FRUIT_GLOW,
        "points": POINTS_NORMAL,
        "growth": 1,
        "lifetime": 0,
        "sprite_index": 0,
    },
    FruitType.GOLDEN: {
        "color": FRUIT_GOLDEN_COLOR,
        "glow": FRUIT_GOLDEN_GLOW,
        "points": POINTS_GOLDEN,
        "growth": 2,
        "lifetime": SPECIAL_FRUIT_LIFETIME,
        "sprite_index": 1,
    },
    FruitType.SPEED: {
        "color": FRUIT_SPEED_COLOR,
        "glow": FRUIT_SPEED_GLOW,
        "points": POINTS_SPEED,
        "growth": 1,
        "lifetime": SPECIAL_FRUIT_LIFETIME,
        "sprite_index": 2,
    },

    FruitType.POISON: {
        "color": FRUIT_POISON_COLOR,
        "glow": FRUIT_POISON_GLOW,
        "points": POINTS_POISON,
        "growth": 0,  # A gente vai tirar tamanho na cobra, não na fruta!
        "lifetime": SPECIAL_FRUIT_LIFETIME,
        "sprite_index": 3, # Se não tiver um 4º sprite, ele usa a cor verde
    },
}

# Sprites compartilhados entre todas as instâncias
_fruit_sprites = None


def _load_fruit_sprites():
    global _fruit_sprites
    if _fruit_sprites is not None:
        return _fruit_sprites

    try:
        sheet = pygame.image.load(FRUIT_SPRITE_PATH).convert_alpha()
        _fruit_sprites = []
        cols = sheet.get_width() // SPRITE_CELL
        for i in range(cols):
            rect = pygame.Rect(i * SPRITE_CELL, 0, SPRITE_CELL, SPRITE_CELL)
            s = pygame.Surface((SPRITE_CELL, SPRITE_CELL), pygame.SRCALPHA)
            s.blit(sheet, (0, 0), rect)
            scaled = pygame.transform.scale(s, (CELL_SIZE, CELL_SIZE))
            _fruit_sprites.append(scaled)
    except (pygame.error, FileNotFoundError):
        _fruit_sprites = []

    return _fruit_sprites


class Fruit:
    def __init__(self, fruit_type=FruitType.NORMAL):
        self.fruit_type = fruit_type
        self.position = (0, 0)
        self.spawn_time = 0

        config = FRUIT_CONFIG[fruit_type]
        self.color = config["color"]
        self.glow_color = config["glow"]
        self.points = config["points"]
        self.growth = config["growth"]
        self.lifetime = config["lifetime"]
        self.sprite_index = config["sprite_index"]

    def spawn(self, occupied):
        while True:
            x = random.randint(0, GRID_COLS - 1)
            y = random.randint(0, GRID_ROWS - 1)
            if (x, y) not in occupied:
                self.position = (x, y)
                self.spawn_time = pygame.time.get_ticks()
                break

    def is_expired(self):
        if self.lifetime == 0:
            return False
        elapsed = pygame.time.get_ticks() - self.spawn_time
        return elapsed > self.lifetime * 16

    def draw(self, screen):
        if self.lifetime > 0:
            elapsed = pygame.time.get_ticks() - self.spawn_time
            remaining = self.lifetime * 16 - elapsed
            if remaining < 2000 and (pygame.time.get_ticks() // 150) % 2 == 0:
                return

        px = self.position[0] * CELL_SIZE + GRID_OFFSET_X
        py = self.position[1] * CELL_SIZE + GRID_OFFSET_Y

        # Glow pulsante
        pulse = abs(pygame.time.get_ticks() % 1000 - 500) / 500.0
        glow_r = int(CELL_SIZE // 2 + 3 * pulse)
        glow_s = pygame.Surface((glow_r * 2 + 4, glow_r * 2 + 4), pygame.SRCALPHA)
        cx, cy = glow_r + 2, glow_r + 2
        pygame.draw.circle(glow_s, (*self.glow_color, 50), (cx, cy), glow_r)
        screen.blit(glow_s, (px + CELL_SIZE // 2 - cx, py + CELL_SIZE // 2 - cy))

        # Sprite ou fallback para círculo
        sprites = _load_fruit_sprites()
        if sprites and self.sprite_index < len(sprites):
            # Efeito de leve bounce
            bounce = int(2 * pulse)
            screen.blit(sprites[self.sprite_index], (px, py - bounce))
        else:
            center = (px + CELL_SIZE // 2, py + CELL_SIZE // 2)
            pygame.draw.circle(screen, self.color, center, CELL_SIZE // 2 - 2)
