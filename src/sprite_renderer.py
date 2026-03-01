import pygame
from .config import (
    CELL_SIZE, GRID_OFFSET_X, GRID_OFFSET_Y, SPRITE_CELL, SPRITE_PATH,
    SPR_HEAD_RIGHT, SPR_HEAD_LEFT, SPR_HEAD_UP, SPR_HEAD_DOWN,
    SPR_BODY_H, SPR_BODY_V,
    SPR_CORNER_BL, SPR_CORNER_BR, SPR_CORNER_TL, SPR_CORNER_TR,
    SPR_TAIL_RIGHT, SPR_TAIL_LEFT, SPR_TAIL_UP, SPR_TAIL_DOWN,
    DIR_RIGHT, DIR_LEFT, DIR_UP, DIR_DOWN,
)

SHEET_COLS = 4


def _load_sprites():
    try:
        sheet = pygame.image.load(SPRITE_PATH).convert_alpha()
    except (pygame.error, FileNotFoundError):
        return None

    sprites = []
    rows = sheet.get_height() // SPRITE_CELL
    cols = sheet.get_width() // SPRITE_CELL

    for row in range(rows):
        for col in range(cols):
            rect = pygame.Rect(col * SPRITE_CELL, row * SPRITE_CELL, SPRITE_CELL, SPRITE_CELL)
            s = pygame.Surface((SPRITE_CELL, SPRITE_CELL), pygame.SRCALPHA)
            s.blit(sheet, (0, 0), rect)
            scaled = pygame.transform.scale(s, (CELL_SIZE, CELL_SIZE))
            sprites.append(scaled)

    return sprites


def _make_boost_sprites(sprites):
    result = []
    for sprite in sprites:
        tinted = sprite.copy()
        tinted.fill((80, 160, 255, 0), special_flags=pygame.BLEND_RGB_ADD)
        result.append(tinted)
    return result


HEAD_MAP = {
    DIR_RIGHT: SPR_HEAD_RIGHT,
    DIR_LEFT:  SPR_HEAD_LEFT,
    DIR_UP:    SPR_HEAD_UP,
    DIR_DOWN:  SPR_HEAD_DOWN,
}

TAIL_MAP = {
    DIR_RIGHT: SPR_TAIL_LEFT,
    DIR_LEFT:  SPR_TAIL_RIGHT,
    DIR_UP:    SPR_TAIL_DOWN,
    DIR_DOWN:  SPR_TAIL_UP,
}


def _corner_index(prev_pos, curr_pos, next_pos):
    dx1 = prev_pos[0] - curr_pos[0]
    dy1 = prev_pos[1] - curr_pos[1]
    dx2 = next_pos[0] - curr_pos[0]
    dy2 = next_pos[1] - curr_pos[1]

    sx = dx1 + dx2
    sy = dy1 + dy2

    if sx > 0 and sy > 0:
        return SPR_CORNER_BR
    elif sx > 0 and sy < 0:
        return SPR_CORNER_TR
    elif sx < 0 and sy > 0:
        return SPR_CORNER_BL
    elif sx < 0 and sy < 0:
        return SPR_CORNER_TL

    return SPR_BODY_H


class SnakeSpriteRenderer:
    def __init__(self):
        self.sprites = _load_sprites()
        self.boost_sprites = _make_boost_sprites(self.sprites) if self.sprites else None

    def _get(self, index, boost=False):
        pool = self.boost_sprites if (boost and self.boost_sprites) else self.sprites
        if index >= len(pool):
            return pool[0]
        return pool[index]

    def draw(self, screen, body, direction, speed_boost):
        if not self.sprites or len(body) == 0:
            return

        for i, pos in enumerate(body):
            px = pos[0] * CELL_SIZE + GRID_OFFSET_X
            py = pos[1] * CELL_SIZE + GRID_OFFSET_Y

            if i == 0:
                idx = HEAD_MAP[direction]

            elif i == len(body) - 1:
                dx = body[i - 1][0] - body[i][0]
                dy = body[i - 1][1] - body[i][1]
                idx = TAIL_MAP.get((dx, dy), SPR_TAIL_LEFT)

            else:
                prev = body[i - 1]
                next_ = body[i + 1]

                dx_prev = prev[0] - pos[0]
                dx_next = next_[0] - pos[0]
                dy_prev = prev[1] - pos[1]
                dy_next = next_[1] - pos[1]

                if dy_prev == 0 and dy_next == 0:
                    idx = SPR_BODY_H
                elif dx_prev == 0 and dx_next == 0:
                    idx = SPR_BODY_V
                else:
                    idx = _corner_index(prev, pos, next_)

            screen.blit(self._get(idx, speed_boost), (px, py))
