import pygame
import os
import math

CELL = 32
H = CELL // 2

# Paleta cobra
DARK  = (60,  70, 170)
MID   = (90, 110, 210)
LIGHT = (140, 160, 250)
EYE_W = (240, 245, 255)
EYE_P = (30,  30,  80)

PAD = 5


def surf(size=CELL):
    s = pygame.Surface((size, size), pygame.SRCALPHA)
    return s


# =========================================================================
# COBRA
# =========================================================================

def draw_head_right():
    s = surf()
    pygame.draw.rect(s, DARK, (0, PAD - 1, H, CELL - PAD * 2 + 2))
    pygame.draw.ellipse(s, DARK, (H - 6, PAD - 1, H + 2, CELL - PAD * 2 + 2))
    pygame.draw.rect(s, MID, (0, PAD + 1, H, CELL - PAD * 2 - 2))
    pygame.draw.ellipse(s, MID, (H - 4, PAD + 1, H, CELL - PAD * 2 - 2))
    for ey in (H - 5, H + 5):
        pygame.draw.circle(s, EYE_W, (CELL - 9, ey), 4)
        pygame.draw.circle(s, EYE_P, (CELL - 8, ey), 2)
    return s


def draw_head(direction):
    s = draw_head_right()
    rotations = {"right": 0, "left": 180, "up": 90, "down": -90}
    return pygame.transform.rotate(s, rotations[direction])


def draw_body_h():
    s = surf()
    pygame.draw.rect(s, DARK, (0, PAD - 1, CELL, CELL - PAD * 2 + 2))
    pygame.draw.rect(s, MID,  (0, PAD + 1, CELL, CELL - PAD * 2 - 2))
    pygame.draw.rect(s, LIGHT, (0, PAD + 2, CELL, 4))
    return s


def draw_body_v():
    s = surf()
    pygame.draw.rect(s, DARK, (PAD - 1, 0, CELL - PAD * 2 + 2, CELL))
    pygame.draw.rect(s, MID,  (PAD + 1, 0, CELL - PAD * 2 - 2, CELL))
    pygame.draw.rect(s, LIGHT, (PAD + 2, 0, 4, CELL))
    return s


def draw_corner(corner):
    s = surf()
    centers = {"tl": (0, 0), "tr": (CELL, 0), "bl": (0, CELL), "br": (CELL, CELL)}
    cx, cy = centers[corner]
    r_out = CELL - PAD + 1
    r_mid = CELL - PAD - 1
    angles = {"tl": (0, math.pi/2), "tr": (math.pi/2, math.pi),
              "bl": (-math.pi/2, 0), "br": (math.pi, 3*math.pi/2)}
    a0, a1 = angles[corner]
    steps = 20

    def arc(r, s0, s1, n):
        return [(cx + math.cos(s0 + (s1-s0)*i/n) * r,
                 cy + math.sin(s0 + (s1-s0)*i/n) * r) for i in range(n+1)]

    outer, inner = arc(r_out, a0, a1, steps), arc(PAD-1, a0, a1, steps)
    inner.reverse()
    if len(outer) >= 3:
        pygame.draw.polygon(s, DARK, outer + inner)
    outer2, inner2 = arc(r_mid, a0, a1, steps), arc(PAD+1, a0, a1, steps)
    inner2.reverse()
    if len(outer2) >= 3:
        pygame.draw.polygon(s, MID, outer2 + inner2)
    return s


def draw_tail_right():
    s = surf()
    w = CELL - PAD * 2 + 2
    pygame.draw.rect(s, DARK, (0, PAD - 1, H, w))
    pygame.draw.rect(s, MID,  (0, PAD + 1, H, w - 4))
    pygame.draw.ellipse(s, DARK, (H - 6, PAD - 1, H + 2, w))
    pygame.draw.ellipse(s, MID,  (H - 4, PAD + 1, H, w - 4))
    return s


def draw_tail(direction):
    s = draw_tail_right()
    rotations = {"right": 0, "left": 180, "up": 90, "down": -90}
    return pygame.transform.rotate(s, rotations[direction])


def generate_snake():
    sprites = [
        draw_head("right"), draw_head("left"), draw_head("up"), draw_head("down"),
        draw_body_h(), draw_body_v(),
        draw_corner("bl"), draw_corner("br"), draw_corner("tl"), draw_corner("tr"),
        draw_tail("right"), draw_tail("left"), draw_tail("up"), draw_tail("down"),
    ]
    return save_sheet(sprites, 4, "assets/sprites/snake.png", "cobra")


# =========================================================================
# FRUTAS
# =========================================================================

def draw_apple():
    """Maçã vermelha cartoon (fruta normal)."""
    s = surf()
    # Corpo da maçã
    pygame.draw.ellipse(s, (180, 20, 20), (3, 8, 26, 22))       # Sombra
    pygame.draw.ellipse(s, (230, 40, 40), (4, 6, 24, 22))       # Corpo escuro
    pygame.draw.ellipse(s, (255, 60, 60), (5, 7, 22, 20))       # Corpo principal
    pygame.draw.ellipse(s, (255, 120, 100), (8, 9, 10, 8))      # Brilho

    # Talo
    pygame.draw.line(s, (100, 70, 30), (H, 7), (H + 1, 2), 2)
    # Folha
    pygame.draw.ellipse(s, (80, 180, 50), (H + 1, 1, 8, 5))
    pygame.draw.ellipse(s, (100, 210, 70), (H + 2, 2, 6, 3))
    return s


def draw_pineapple():

    s = surf()
    cx = H

    # Corpo do abacaxi (oval amarelo/laranja)
    pygame.draw.ellipse(s, (180, 120, 10), (7, 12, 19, 20))       # Sombra
    pygame.draw.ellipse(s, (220, 170, 20), (8, 11, 17, 19))       # Corpo escuro
    pygame.draw.ellipse(s, (255, 200, 40), (9, 12, 15, 17))       # Corpo principal

    # Textura losango do abacaxi
    for row in range(3):
        for col in range(2):
            lx = 12 + col * 6 + (row % 2) * 3
            ly = 15 + row * 5
            pygame.draw.line(s, (200, 150, 20), (lx, ly), (lx + 3, ly + 3), 1)
            pygame.draw.line(s, (200, 150, 20), (lx + 3, ly), (lx, ly + 3), 1)

    # Brilho
    pygame.draw.ellipse(s, (255, 235, 120), (11, 14, 5, 4))

    # Coroa de folhas
    pygame.draw.polygon(s, (40, 140, 30), [(cx - 1, 12), (cx - 5, 2), (cx - 3, 10)])
    pygame.draw.polygon(s, (60, 170, 40), [(cx, 12), (cx, 1), (cx + 2, 10)])
    pygame.draw.polygon(s, (40, 140, 30), [(cx + 1, 12), (cx + 5, 3), (cx + 3, 10)])
    pygame.draw.polygon(s, (80, 190, 50), [(cx - 3, 11), (cx - 7, 5), (cx - 4, 10)])
    pygame.draw.polygon(s, (80, 190, 50), [(cx + 3, 11), (cx + 7, 5), (cx + 4, 10)])
    return s


def draw_grapes():
   
    s = surf()
    cx = H

    grape_color = (130, 40, 160)
    grape_dark = (100, 25, 130)
    grape_light = (180, 100, 210)

    # Cacho: 3 fileiras de uvas (pirâmide invertida)
    positions = [
        (cx - 6, 14), (cx, 12), (cx + 6, 14),   # Topo: 3 uvas
        (cx - 3, 20), (cx + 3, 20),               # Meio: 2 uvas
        (cx, 26),                                   # Baixo: 1 uva
    ]

    for x, y in positions:
        pygame.draw.circle(s, grape_dark, (x + 1, y + 1), 5)    # Sombra
        pygame.draw.circle(s, grape_color, (x, y), 5)            # Corpo
        pygame.draw.circle(s, grape_light, (x - 1, y - 2), 2)   # Brilho

    # Talo
    pygame.draw.line(s, (80, 50, 20), (cx, 12), (cx, 4), 2)
    # Folha
    pygame.draw.ellipse(s, (60, 160, 40), (cx, 2, 8, 5))
    pygame.draw.ellipse(s, (80, 190, 60), (cx + 1, 3, 6, 3))
    return s


def generate_fruits():
    sprites = [draw_apple(), draw_pineapple(), draw_grapes()]
    return save_sheet(sprites, 3, "assets/sprites/fruits.png", "frutas")


# =========================================================================
# DECORAÇÕES
# =========================================================================

def draw_rock_1():
    """Pedra grande"""
    s = surf()
    # Forma irregular de pedra
    pts = [(6, 28), (3, 18), (8, 8), (18, 5), (26, 10), (28, 22), (22, 28)]
    pygame.draw.polygon(s, (100, 90, 80), pts)   # Sombra
    pts2 = [(7, 27), (4, 17), (9, 8), (18, 6), (25, 10), (27, 21), (21, 27)]
    pygame.draw.polygon(s, (140, 130, 115), pts2)  # Corpo
    pygame.draw.polygon(s, (120, 110, 95), pts2, 2) # Contorno
    # Brilho
    pygame.draw.polygon(s, (170, 160, 145), [(9, 14), (14, 9), (20, 9), (16, 16)])
    return s


def draw_rock_2():
    """Pedra pequena"""
    s = surf()
    pts = [(8, 26), (6, 16), (14, 10), (24, 12), (26, 22), (18, 26)]
    pygame.draw.polygon(s, (90, 85, 75), pts)
    pts2 = [(9, 25), (7, 16), (14, 11), (23, 13), (25, 21), (17, 25)]
    pygame.draw.polygon(s, (130, 125, 110), pts2)
    pygame.draw.polygon(s, (110, 105, 90), pts2, 2)
    pygame.draw.polygon(s, (160, 155, 140), [(10, 18), (14, 13), (19, 14), (15, 19)])
    return s


def draw_tree():

    s = surf()
    # Tronco
    pygame.draw.rect(s, (100, 70, 30), (13, 18, 6, 12))
    pygame.draw.rect(s, (120, 85, 40), (14, 18, 4, 12))
    # Copa (3 círculos sobrepostos)
    pygame.draw.circle(s, (40, 120, 30), (10, 14), 9)
    pygame.draw.circle(s, (40, 120, 30), (22, 14), 9)
    pygame.draw.circle(s, (40, 120, 30), (16, 8), 9)
    # Copa mais clara por cima
    pygame.draw.circle(s, (60, 160, 50), (10, 13), 7)
    pygame.draw.circle(s, (60, 160, 50), (22, 13), 7)
    pygame.draw.circle(s, (60, 160, 50), (16, 7), 7)
    # Brilho
    pygame.draw.circle(s, (90, 190, 70), (12, 8), 3)
    return s


def draw_bush():
    """Arbusto/moita"""
    s = surf()
    # Forma arredondada
    pygame.draw.ellipse(s, (40, 130, 35), (2, 10, 28, 20))
    pygame.draw.ellipse(s, (60, 165, 50), (4, 11, 24, 17))
    # Detalhes de folhas (círculos menores)
    pygame.draw.circle(s, (50, 145, 40), (8, 15), 6)
    pygame.draw.circle(s, (50, 145, 40), (24, 15), 6)
    pygame.draw.circle(s, (50, 145, 40), (16, 11), 7)
    # Verde mais claro
    pygame.draw.circle(s, (80, 185, 65), (8, 14), 4)
    pygame.draw.circle(s, (80, 185, 65), (24, 14), 4)
    pygame.draw.circle(s, (80, 185, 65), (16, 10), 5)
    # Brilho
    pygame.draw.circle(s, (110, 210, 90), (13, 10), 2)
    return s


def draw_flowers():

    s = surf()
    # Caule
    pygame.draw.line(s, (60, 140, 40), (10, 26), (10, 16), 2)
    pygame.draw.line(s, (60, 140, 40), (22, 24), (22, 14), 2)
    # Flor 1 (rosa)
    for angle in range(0, 360, 72):
        px = int(10 + math.cos(math.radians(angle)) * 4)
        py = int(14 + math.sin(math.radians(angle)) * 4)
        pygame.draw.circle(s, (255, 150, 180), (px, py), 3)
    pygame.draw.circle(s, (255, 230, 100), (10, 14), 2)
    # Flor 2 (amarela)
    for angle in range(0, 360, 72):
        px = int(22 + math.cos(math.radians(angle)) * 3)
        py = int(12 + math.sin(math.radians(angle)) * 3)
        pygame.draw.circle(s, (255, 240, 100), (px, py), 2)
    pygame.draw.circle(s, (200, 120, 50), (22, 12), 2)
    return s


def draw_grass_tuft():
    """Tufo de grama alta"""
    s = surf()
    blades = [(8, -12), (12, -15), (16, -13), (20, -10), (24, -14)]
    for bx, by in blades:
        pygame.draw.line(s, (70, 150, 40), (bx, 28), (bx + by // 4, 28 + by), 2)
        pygame.draw.line(s, (90, 180, 60), (bx + 1, 28), (bx + by // 4 + 1, 28 + by), 1)
    return s


def generate_decorations():
    sprites = [
        draw_rock_1(), draw_rock_2(), draw_tree(),
        draw_bush(), draw_flowers(), draw_grass_tuft(),
    ]
    return save_sheet(sprites, 6, "assets/sprites/decorations.png", "decorações")


# =========================================================================
# UTILITÁRIO
# =========================================================================

def save_sheet(sprites, cols, path, name):
    rows = (len(sprites) + cols - 1) // cols
    sheet = pygame.Surface((cols * CELL, rows * CELL), pygame.SRCALPHA)
    for i, sprite in enumerate(sprites):
        sheet.blit(sprite, ((i % cols) * CELL, (i // cols) * CELL))
    pygame.image.save(sheet, path)
    print(f"  {name}: {path} ({len(sprites)} sprites)")
    return sheet


def main():
    pygame.init()
    pygame.display.set_mode((1, 1), pygame.NOFRAME)
    os.makedirs("assets/sprites", exist_ok=True)

    print("Gerando sprites...")
    generate_snake()
    generate_fruits()
    generate_decorations()
    print("Pronto!")

    pygame.quit()


if __name__ == "__main__":
    main()
