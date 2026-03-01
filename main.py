import pygame
import sys
import random
import math

from src.config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, FPS, CELL_SIZE,
    HEADER_COLOR, HEADER_HEIGHT,
    GRID_LIGHT, GRID_DARK,
    GRID_COLS, GRID_ROWS,
    GRID_OFFSET_X, GRID_OFFSET_Y,
    BORDER_COLOR,
    SNAKE_SPEED, SPEED_INCREMENT, MAX_SPEED, SPEED_BOOST_AMOUNT, SPEED_BOOST_DURATION,
    POINTS_NORMAL,
    SPECIAL_FRUIT_INTERVAL, SPECIAL_FRUIT_CHANCE,
    DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT,
    TEXT_COLOR, TEXT_SECONDARY, SCORE_COLOR,
    TITLE_COLOR, TITLE_GLOW, GAMEOVER_COLOR, GAMEOVER_GLOW,
    FRUIT_COLOR, FRUIT_GOLDEN_COLOR, FRUIT_SPEED_COLOR,
    FONT_TITLE, FONT_BODY, FONT_BOLD,
)
from src.entities import Snake, Fruit, FruitType
from src.particles import ParticleSystem
from src.decorations import BorderDecorations
from src.sound_gen import SoundManager
from src.menu_snake import MenuSnake
from src.entities.fruit import _load_fruit_sprites


STATE_MENU = "menu"
STATE_PLAYING = "playing"
STATE_GAME_OVER = "game_over"
STATE_PAUSED = "paused"


class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()

        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Snake Evolution")
        self.clock = pygame.time.Clock()

        self.font_small = pygame.font.Font(FONT_BODY, 20)
        self.font_medium = pygame.font.Font(FONT_BOLD, 28)
        self.font_large = pygame.font.Font(FONT_TITLE, 32)
        self.font_title = pygame.font.Font(FONT_TITLE, 42)

        self.snake = Snake()
        self.fruits = []
        self.particles = ParticleSystem()
        self.decorations = BorderDecorations()
        self.sounds = SoundManager()
        self.menu_snake = MenuSnake()

        self.score = 0
        self.high_score = 0
        self.state = STATE_MENU
        self.move_timer = 0
        self.special_timer = 0
        self.sounds.play_menu_music()

    # === CONTROLE DE ESTADO ===

    def start_game(self):
        self.snake.reset()
        self.fruits.clear()
        self.particles.clear()
        self.score = 0
        self.move_timer = 0
        self.special_timer = 0
        self.state = STATE_PLAYING
        self._spawn_fruit(FruitType.NORMAL)
        self.sounds.play_game_music()

    def game_over(self):
        self.state = STATE_GAME_OVER
        if self.score > self.high_score:
            self.high_score = self.score
        self.sounds.stop_music()
        self.sounds.play_gameover()

    # === FRUTAS ===

    def _get_occupied(self):
        occupied = set(self.snake.body)
        for f in self.fruits:
            occupied.add(f.position)
        return occupied

    def _spawn_fruit(self, fruit_type):
        fruit = Fruit(fruit_type)
        fruit.spawn(self._get_occupied())
        self.fruits.append(fruit)

    def _has_normal_fruit(self):
        return any(f.fruit_type == FruitType.NORMAL for f in self.fruits)

    # === VELOCIDADE ===

    def get_speed(self):
        speed = SNAKE_SPEED + (self.score // 50) * SPEED_INCREMENT
        if self.snake.speed_boost:
            speed += SPEED_BOOST_AMOUNT
        return min(speed, MAX_SPEED)

    def get_move_interval(self):
        return 1000 // self.get_speed()

    # === EVENTOS ===

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if self.state == STATE_MENU:
                    self._handle_menu_input(event.key)
                elif self.state == STATE_PLAYING:
                    self._handle_playing_input(event.key)
                elif self.state == STATE_GAME_OVER:
                    self._handle_gameover_input(event.key)
                elif self.state == STATE_PAUSED:
                    self._handle_paused_input(event.key)
        return True

    def _handle_menu_input(self, key):
        if key in (pygame.K_RETURN, pygame.K_SPACE):
            self.start_game()
        elif key == pygame.K_ESCAPE:
            pygame.quit()
            sys.exit()

    def _handle_playing_input(self, key):
        direction_map = {
            pygame.K_UP: DIR_UP, pygame.K_w: DIR_UP,
            pygame.K_DOWN: DIR_DOWN, pygame.K_s: DIR_DOWN,
            pygame.K_LEFT: DIR_LEFT, pygame.K_a: DIR_LEFT,
            pygame.K_RIGHT: DIR_RIGHT, pygame.K_d: DIR_RIGHT,
        }
        if key in direction_map:
            self.snake.set_direction(direction_map[key])
        elif key == pygame.K_p:
            self.state = STATE_PAUSED
        elif key == pygame.K_ESCAPE:
            self.state = STATE_MENU
            self.sounds.play_menu_music()

    def _handle_gameover_input(self, key):
        if key in (pygame.K_RETURN, pygame.K_SPACE):
            self.start_game()
        elif key == pygame.K_ESCAPE:
            self.state = STATE_MENU
            self.sounds.play_menu_music()

    def _handle_paused_input(self, key):
        if key in (pygame.K_p, pygame.K_RETURN, pygame.K_SPACE):
            self.state = STATE_PLAYING
        elif key == pygame.K_ESCAPE:
            self.state = STATE_MENU
            self.sounds.play_menu_music()

    # === UPDATE ===

    def update(self):
        self.particles.update()

        if self.state == STATE_MENU:
            self.menu_snake.update()
            return

        if self.state != STATE_PLAYING:
            return

        self.move_timer += self.clock.get_time()
        if self.move_timer < self.get_move_interval():
            return
        self.move_timer = 0

        self.snake.move()

        if self.snake.hit_wall() or self.snake.hit_self():
            self.game_over()
            return

        head = self.snake.head
        for fruit in self.fruits[:]:
            if head == fruit.position:
                self.score += fruit.points
                self.snake.grow(fruit.growth)
                self.particles.emit(fruit.position[0], fruit.position[1], fruit.color)

                if fruit.fruit_type == FruitType.SPEED:
                    self.snake.activate_boost(SPEED_BOOST_DURATION)
                    self.sounds.play_special()
                elif fruit.fruit_type == FruitType.GOLDEN:
                    self.sounds.play_special()
                else:
                    self.sounds.play_eat()

                self.fruits.remove(fruit)
                if fruit.fruit_type == FruitType.NORMAL:
                    self._spawn_fruit(FruitType.NORMAL)
                break

        self.fruits = [f for f in self.fruits if not f.is_expired()]

        if not self._has_normal_fruit():
            self._spawn_fruit(FruitType.NORMAL)

        self.special_timer += 1
        if self.special_timer >= SPECIAL_FRUIT_INTERVAL:
            self.special_timer = 0
            if random.random() < SPECIAL_FRUIT_CHANCE:
                special = random.choice([FruitType.GOLDEN, FruitType.SPEED])
                self._spawn_fruit(special)

    # === DESENHO ===

    def draw(self):
        if self.state == STATE_MENU:
            self._draw_menu()
        elif self.state == STATE_PLAYING:
            self._draw_playing()
        elif self.state == STATE_GAME_OVER:
            self._draw_playing()
            self._draw_gameover_overlay()
        elif self.state == STATE_PAUSED:
            self._draw_playing()
            self._draw_pause_overlay()

        pygame.display.flip()

    def _draw_grid(self):
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                color = GRID_LIGHT if (row + col) % 2 == 0 else GRID_DARK
                pygame.draw.rect(
                    self.screen, color,
                    (GRID_OFFSET_X + col * CELL_SIZE,
                     GRID_OFFSET_Y + row * CELL_SIZE,
                     CELL_SIZE, CELL_SIZE)
                )

    def _draw_header(self):
        pygame.draw.rect(self.screen, HEADER_COLOR, (0, 0, WINDOW_WIDTH, HEADER_HEIGHT))
        pygame.draw.line(self.screen, SCORE_COLOR, (0, HEADER_HEIGHT - 1), (WINDOW_WIDTH, HEADER_HEIGHT - 1), 2)

        text = self.font_small.render(f"PONTOS  {self.score}", True, SCORE_COLOR)
        self.screen.blit(text, text.get_rect(midleft=(20, HEADER_HEIGHT // 2)))

        size_text = self.font_small.render(f"TAMANHO  {len(self.snake)}", True, TEXT_SECONDARY)
        self.screen.blit(size_text, size_text.get_rect(center=(WINDOW_WIDTH // 2, HEADER_HEIGHT // 2)))

        if self.snake.speed_boost:
            boost_text = self.font_small.render("BOOST!", True, (80, 180, 255))
            self.screen.blit(boost_text, boost_text.get_rect(midright=(WINDOW_WIDTH - 20, HEADER_HEIGHT // 2)))
        elif self.high_score > 0:
            hs_text = self.font_small.render(f"RECORDE  {self.high_score}", True, TEXT_SECONDARY)
            self.screen.blit(hs_text, hs_text.get_rect(midright=(WINDOW_WIDTH - 20, HEADER_HEIGHT // 2)))

    def _draw_playing(self):
        self.screen.fill(BORDER_COLOR)
        self.decorations.draw(self.screen)
        self._draw_grid()
        self._draw_header()

        for fruit in self.fruits:
            fruit.draw(self.screen)

        self.snake.draw(self.screen)
        self.particles.draw(self.screen)

    def _draw_text_with_glow(self, text, font, color, glow_color, center, glow_offset=2):
        glow = font.render(text, True, glow_color)
        for dx, dy in [(-glow_offset, 0), (glow_offset, 0), (0, -glow_offset), (0, glow_offset)]:
            rect = glow.get_rect(center=(center[0] + dx, center[1] + dy))
            glow.set_alpha(60)
            self.screen.blit(glow, rect)

        rendered = font.render(text, True, color)
        self.screen.blit(rendered, rendered.get_rect(center=center))

    def _draw_menu(self):
        # Fundo: grid + borda decorativa (mesmo visual do jogo)
        self.screen.fill(BORDER_COLOR)
        self.decorations.draw(self.screen)
        self._draw_grid()

        # Cobra silhueta no fundo
        self.menu_snake.draw(self.screen, alpha=80)

        # Escurecer levemente o fundo para destacar o painel
        self._draw_overlay(100)

        t = pygame.time.get_ticks() / 1000.0
        cx, cy = WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2

        # Painel central semi-transparente
        panel_w, panel_h = 500, 380
        panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        pygame.draw.rect(panel, (20, 30, 15, 200), (0, 0, panel_w, panel_h), border_radius=16)
        pygame.draw.rect(panel, (100, 180, 60, 120), (0, 0, panel_w, panel_h), width=2, border_radius=16)
        self.screen.blit(panel, (cx - panel_w // 2, cy - panel_h // 2))

        # Título
        self._draw_text_with_glow(
            "SNAKE", self.font_title,
            TITLE_COLOR, TITLE_GLOW,
            (cx, cy - 140), 3
        )
        self._draw_text_with_glow(
            "EVOLUTION", self.font_medium,
            TEXT_SECONDARY, (100, 180, 60),
            (cx, cy - 95), 2
        )

        # Recorde
        if self.high_score > 0:
            hs = self.font_small.render(f"Recorde: {self.high_score}", True, SCORE_COLOR)
            self.screen.blit(hs, hs.get_rect(center=(cx, cy - 55)))

        # "Pressione ENTER" com pulsação
        pulse = abs(math.sin(t * 2)) * 0.4 + 0.6
        start_text = self.font_medium.render("Pressione ENTER", True, TEXT_COLOR)
        start_text.set_alpha(int(255 * pulse))
        self.screen.blit(start_text, start_text.get_rect(center=(cx, cy - 10)))

        # Controles
        controls_text = self.font_small.render("WASD / Setas   |   P = Pausar", True, TEXT_SECONDARY)
        self.screen.blit(controls_text, controls_text.get_rect(center=(cx, cy + 35)))

        # Legenda de frutas com sprites
        fruit_sprites = _load_fruit_sprites()
        fruits_info = [
            (0, FRUIT_COLOR, f"+{POINTS_NORMAL} pts", TEXT_COLOR),
            (1, FRUIT_GOLDEN_COLOR, "+50 pts (rara)", (255, 215, 0)),
            (2, FRUIT_SPEED_COLOR, "+20 pts + speed", (180, 100, 210)),
        ]
        legend_y = cy + 75
        for i, (spr_idx, fallback_color, text, text_color) in enumerate(fruits_info):
            y = legend_y + i * 36
            icon_x = cx - 150

            if fruit_sprites and spr_idx < len(fruit_sprites):
                icon = pygame.transform.scale(fruit_sprites[spr_idx], (24, 24))
                self.screen.blit(icon, (icon_x - 12, y - 12))
            else:
                pygame.draw.circle(self.screen, fallback_color, (icon_x, y), 8)

            label = self.font_small.render(text, True, text_color)
            self.screen.blit(label, (icon_x + 20, y - 10))

    def _draw_overlay(self, alpha=180):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, alpha))
        self.screen.blit(overlay, (0, 0))

    def _draw_gameover_overlay(self):
        self._draw_overlay(200)
        cx, cy = WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2

        self._draw_text_with_glow("GAME OVER", self.font_large,
                                  GAMEOVER_COLOR, GAMEOVER_GLOW, (cx, cy - 80), 3)

        score_text = self.font_medium.render(f"Pontuacao: {self.score}", True, TEXT_COLOR)
        self.screen.blit(score_text, score_text.get_rect(center=(cx, cy)))

        if self.score >= self.high_score and self.score > 0:
            t = pygame.time.get_ticks() / 1000.0
            pulse = abs(math.sin(t * 3)) * 0.3 + 0.7
            record_text = self.font_medium.render("Novo Recorde!", True, SCORE_COLOR)
            record_text.set_alpha(int(255 * pulse))
            self.screen.blit(record_text, record_text.get_rect(center=(cx, cy + 50)))
        elif self.high_score > 0:
            hs_text = self.font_small.render(f"Recorde: {self.high_score}", True, TEXT_SECONDARY)
            self.screen.blit(hs_text, hs_text.get_rect(center=(cx, cy + 50)))

        restart = self.font_small.render("ENTER para jogar novamente", True, TEXT_COLOR)
        self.screen.blit(restart, restart.get_rect(center=(cx, cy + 120)))

        menu_text = self.font_small.render("ESC para voltar ao menu", True, TEXT_SECONDARY)
        self.screen.blit(menu_text, menu_text.get_rect(center=(cx, cy + 150)))

        self.particles.draw(self.screen)

    def _draw_pause_overlay(self):
        self._draw_overlay(150)
        cx, cy = WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2

        self._draw_text_with_glow("PAUSADO", self.font_large, TEXT_COLOR, TEXT_SECONDARY, (cx, cy - 30))

        resume = self.font_small.render("P ou ENTER para continuar", True, TEXT_SECONDARY)
        self.screen.blit(resume, resume.get_rect(center=(cx, cy + 30)))

    # === LOOP PRINCIPAL ===

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
