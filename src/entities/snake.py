from ..config import (
    GRID_COLS, GRID_ROWS, DIR_RIGHT
)
from ..sprite_renderer import SnakeSpriteRenderer


class Snake:
    def __init__(self):
        self._renderer = SnakeSpriteRenderer()
        self.reset()

    def reset(self):
        center_x = GRID_COLS // 2
        center_y = GRID_ROWS // 2

        self.body = [
            (center_x, center_y),
            (center_x - 1, center_y),
            (center_x - 2, center_y),
        ]
        self.direction = DIR_RIGHT
        self.growing = 0
        self.speed_boost = False
        self.boost_timer = 0

    @property
    def head(self):
        return self.body[0]

    def set_direction(self, new_direction):
        opposite = (-self.direction[0], -self.direction[1])
        if new_direction != opposite:
            self.direction = new_direction

    def move(self):
        head_x, head_y = self.head
        new_head = (head_x + self.direction[0], head_y + self.direction[1])
        self.body.insert(0, new_head)

        if self.growing > 0:
            self.growing -= 1
        else:
            self.body.pop()

        if self.speed_boost:
            self.boost_timer -= 1
            if self.boost_timer <= 0:
                self.speed_boost = False

    def grow(self, amount=1):
        self.growing += amount

    def shrink(self, amount=1):
        # Regra fatal: Se tiver só 1 segmento (a cabeça), o veneno mata!
        if len(self.body) <= 1:
            return False 

        # Arranca 'amount' pedaços do final da lista (o rabo)
        for _ in range(amount):
            if len(self.body) > 1:
                self.body.pop()

        # Zera qualquer crescimento que estava pendente para evitar bugs
        self.growing = 0

        return True  # Retorna True para avisar que ela sobreviveu

    def activate_boost(self, duration):
        self.speed_boost = True
        self.boost_timer = duration

    def hit_wall(self):
        x, y = self.head
        return x < 0 or x >= GRID_COLS or y < 0 or y >= GRID_ROWS

    def hit_self(self):
        return self.head in self.body[1:]

    def draw(self, screen):
        self._renderer.draw(screen, self.body, self.direction, self.speed_boost)

    def __len__(self):
        return len(self.body)
