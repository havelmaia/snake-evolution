import pygame
import sys
import random
import math
import json
import os

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
    user_data_path,
)
from src.entities import Snake, Fruit, FruitType
from src.entities.fruit import _load_fruit_sprites
from src.particles import ParticleSystem
from src.decorations import BorderDecorations
from src.sound_gen import SoundManager
from src.menu_snake import MenuSnake


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

        self.font_small = pygame.font.Font(FONT_BODY, 18)
        self.font_medium = pygame.font.Font(FONT_BOLD, 24)
        self.font_large = pygame.font.Font(FONT_TITLE, 32)
        self.font_title = pygame.font.Font(FONT_TITLE, 38)
        self.font_subtitle = pygame.font.Font(FONT_BOLD, 18)

        self.snake = Snake()
        self.fruits = []
        self.particles = ParticleSystem()
        self.decorations = BorderDecorations()
        self.sounds = SoundManager()
        self.menu_snake = MenuSnake()

        self.score = 0
        self.high_score = 0
        self.fruits_eaten = {FruitType.NORMAL: 0, FruitType.GOLDEN: 0, FruitType.SPEED: 0}
        self.header_fruit_sprites = None
        self.state = STATE_MENU
        self.move_timer = 0
        self.special_timer = 0

        # ===== TEMPO (para animações nos MENUS) =====
        self.dt = 0.0
        self.dt_ms = 0
        self.t = 0.0

        # ===== ESTADO: MENU START =====
        self.menu_enter_t = 0.0
        self.menu_type_t = 0.0

        # ===== ESTADO: GAME OVER =====
        self.go_enter_t = 0.0
        self.go_score_display = 0
        self.go_burst_done = False

        # ===== PARTICULAS PIXEL (só overlays/menu) =====
        self.ui_pixels = []
        self.panel_scan = self._build_panel_scanlines(560, 460)

        # ====== MENU UI ======
        self.menu_page = "main"   # "main" | "settings" | "controls" | "audio"
        self.menu_index = 0
        self.paused_game = False

        # ====== SETTINGS (carrega/salva) ======
        self.settings_path = user_data_path("settings.json")
        self.settings = {
            "control_scheme": "both",  # "arrows" | "wasd" | "both"
            "sfx_enabled": True,
            "music_enabled": True,
            "sfx_volume": 0.8,     # 0..1
            "music_volume": 0.8,   # 0..1
        }
        self._load_settings()
        self._apply_audio_settings()

        # >>> SOM DO SEU AMIGO (menu music) <<<
        self._music_menu()

    # ======================================================
    # SETTINGS
    # ======================================================

    def _load_settings(self):
        try:
            if os.path.exists(self.settings_path):
                with open(self.settings_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    self.high_score = data.pop("high_score", 0)
                    self.settings.update(data)
        except Exception:
            pass

    def _save_settings(self):
        try:
            data = {**self.settings, "high_score": self.high_score}
            with open(self.settings_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def _apply_audio_settings(self):
        self.sounds.set_sfx_volume(float(self.settings.get("sfx_volume", 0.8)))
        self.sounds.set_music_volume(float(self.settings.get("music_volume", 0.8)))
        self.sounds.set_sfx_enabled(self.settings.get("sfx_enabled", True))
        self.sounds.set_music_enabled(self.settings.get("music_enabled", True))

    # ======================================================
    # SOM (integração com o código do seu amigo)
    # ======================================================

    def _music_menu(self):
        self.sounds.play_menu_music()

    def _music_game(self):
        self.sounds.play_game_music()

    def _music_stop(self):
        self.sounds.stop_music()

    # ======================================================
    # HELPERS VISUAIS
    # ======================================================

    def _clamp01(self, x):
        return 0.0 if x < 0.0 else 1.0 if x > 1.0 else x

    def _ease_out_back(self, t, s=1.70158):
        t = self._clamp01(t)
        t -= 1.0
        return 1.0 + (s + 1.0) * (t * t * t) + s * (t * t)

    def _draw_overlay(self, alpha=180):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, alpha))
        self.screen.blit(overlay, (0, 0))

    def _draw_text_with_glow(self, text, font, color, glow_color, center, glow_offset=2, glow_alpha=60):
        glow = font.render(text, True, glow_color).convert_alpha()
        glow.set_alpha(glow_alpha)
        for dx, dy in [(-glow_offset, 0), (glow_offset, 0), (0, -glow_offset), (0, glow_offset)]:
            rect = glow.get_rect(center=(center[0] + dx, center[1] + dy))
            self.screen.blit(glow, rect)

        rendered = font.render(text, True, color)
        self.screen.blit(rendered, rendered.get_rect(center=center))

    def _build_panel_scanlines(self, w, h):
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        for y in range(0, h, 2):
            pygame.draw.line(surf, (0, 0, 0, 22), (0, y), (w, y))
        return surf

    def _blit_panel_scanlines(self, x, y, w, h, alpha):
        sub = self.panel_scan.subsurface((0, 0, w, h))
        sub.set_alpha(alpha)
        self.screen.blit(sub, (x, y))

    def _render_fit(self, text, primary_font, fallback_font, color, max_width):
        surf = primary_font.render(text, True, color).convert_alpha()
        if surf.get_width() <= max_width:
            return surf

        surf2 = fallback_font.render(text, True, color).convert_alpha()
        if surf2.get_width() <= max_width:
            return surf2

        scale = max_width / max(1, surf2.get_width())
        new_w = max(1, int(surf2.get_width() * scale))
        new_h = max(1, int(surf2.get_height() * scale))
        return pygame.transform.scale(surf2, (new_w, new_h))

    # ===== partículas pixel (overlay/menu) =====
    def _spawn_ui_pixels(self, rect, amount=18, burst=False):
        x, y, w, h = rect
        for _ in range(amount):
            px = random.uniform(x + 12, x + w - 12)
            py = random.uniform(y + 12, y + h - 12)

            if burst:
                ang = random.uniform(0, math.tau)
                spd = random.uniform(90, 220)
                vx = math.cos(ang) * spd
                vy = math.sin(ang) * spd
                life = random.uniform(0.35, 0.8)
            else:
                vx = random.uniform(-18, 18)
                vy = random.uniform(-40, -15)
                life = random.uniform(0.9, 1.8)

            size = random.choice([2, 2, 3])
            color = random.choice([
                (140, 255, 120),
                (100, 180, 60),
                (255, 215, 0),
                (180, 100, 210),
            ])

            self.ui_pixels.append({
                "x": px, "y": py,
                "vx": vx, "vy": vy,
                "life": life, "max": life,
                "s": size,
                "c": color,
                "g": 260 if burst else 60
            })

    def _update_ui_pixels(self):
        if not self.ui_pixels:
            return
        alive = []
        for p in self.ui_pixels:
            p["life"] -= self.dt
            if p["life"] <= 0:
                continue
            p["vy"] += p["g"] * self.dt
            p["x"] += p["vx"] * self.dt
            p["y"] += p["vy"] * self.dt
            alive.append(p)
        self.ui_pixels = alive

    def _draw_ui_pixels(self):
        for p in self.ui_pixels:
            a = int(255 * (p["life"] / p["max"]))
            s = p["s"]
            surf = pygame.Surface((s, s), pygame.SRCALPHA)
            surf.fill((p["c"][0], p["c"][1], p["c"][2], a))
            self.screen.blit(surf, (int(p["x"]), int(p["y"])))

    # ======================================================
    # MENU (itens/ações)
    # ======================================================

    def _current_menu_items(self):
        if self.menu_page == "main":
            if self.paused_game:
                return ["Continuar", "Recomeçar", "Configurações", "Sair"]
            return ["Começar", "Configurações", "Sair"]
        if self.menu_page == "settings":
            return ["Controles", "Sons", "Voltar"]
        if self.menu_page == "controls":
            scheme = self.settings.get("control_scheme", "both")
            return [
                f"Setas {'✓' if scheme=='arrows' else ''}",
                f"WASD {'✓' if scheme=='wasd' else ''}",
                f"Ambos {'✓' if scheme=='both' else ''}",
                "Voltar"
            ]
        if self.menu_page == "audio":
            sfx_on = self.settings.get("sfx_enabled", True)
            mus_on = self.settings.get("music_enabled", True)
            sfxv = int(round(self.settings.get("sfx_volume", 0.8) * 10))
            musv = int(round(self.settings.get("music_volume", 0.8) * 10))
            return [
                f"Efeitos sonoros: {'ON' if sfx_on else 'OFF'}",
                f"Música: {'ON' if mus_on else 'OFF'}",
                f"Volume SFX: {sfxv}/10",
                f"Volume Música: {musv}/10",
                "Voltar"
            ]
        return ["Voltar"]

    def _menu_activate(self, label):
        if self.menu_page == "main":
            if label.startswith("Continuar"):
                self.state = STATE_PLAYING
                self.paused_game = False
                self._music_game()
                return
            if label.startswith("Começar") or label.startswith("Recomeçar"):
                self.paused_game = False
                self.start_game()
                return
            if label.startswith("Configurações"):
                self.menu_page = "settings"
                self.menu_index = 0
                return
            if label.startswith("Sair"):
                pygame.quit()
                sys.exit()

        if self.menu_page == "settings":
            if label.startswith("Controles"):
                self.menu_page = "controls"
                self.menu_index = 0
                return
            if label.startswith("Sons"):
                self.menu_page = "audio"
                self.menu_index = 0
                return
            if label.startswith("Voltar"):
                self.menu_page = "main"
                self.menu_index = 0
                return

        if self.menu_page == "controls":
            if label.startswith("Setas"):
                self.settings["control_scheme"] = "arrows"
                self._save_settings()
                return
            if label.startswith("WASD"):
                self.settings["control_scheme"] = "wasd"
                self._save_settings()
                return
            if label.startswith("Ambos"):
                self.settings["control_scheme"] = "both"
                self._save_settings()
                return
            if label.startswith("Voltar"):
                self.menu_page = "settings"
                self.menu_index = 0
                return

        if self.menu_page == "audio":
            if label.startswith("Efeitos sonoros"):
                self.settings["sfx_enabled"] = not self.settings.get("sfx_enabled", True)
                self._apply_audio_settings()
                self._save_settings()
                return
            if label.startswith("Música"):
                self.settings["music_enabled"] = not self.settings.get("music_enabled", True)
                self._apply_audio_settings()
                self._save_settings()
                if self.settings["music_enabled"]:
                    if self.state == STATE_MENU:
                        self._music_menu()
                    elif self.state == STATE_PLAYING:
                        self._music_game()
                return
            if label.startswith("Voltar"):
                self.menu_page = "settings"
                self.menu_index = 0
                return

    def _menu_back(self):
        if self.menu_page == "main":
            if self.paused_game:
                self.state = STATE_PLAYING
                self.paused_game = False
                self._music_game()
            return
        if self.menu_page == "settings":
            self.menu_page = "main"
            self.menu_index = 0
            return
        if self.menu_page in ("controls", "audio"):
            self.menu_page = "settings"
            self.menu_index = 0
            return
        self.menu_page = "main"
        self.menu_index = 0

    def _audio_adjust(self, direction):
        if self.menu_index == 2:  # Volume SFX
            v = float(self.settings.get("sfx_volume", 0.8))
            v = max(0.0, min(1.0, v + direction * 0.1))
            self.settings["sfx_volume"] = v
            self.sounds.set_sfx_volume(v)
            self._save_settings()

        elif self.menu_index == 3:  # Volume Música
            v = float(self.settings.get("music_volume", 0.8))
            v = max(0.0, min(1.0, v + direction * 0.1))
            self.settings["music_volume"] = v
            self.sounds.set_music_volume(v)
            self._save_settings()

    # ======================================================
    # CONTROLE DE ESTADO
    # ======================================================

    def _enter_menu(self, page="main"):
        self.state = STATE_MENU
        self.menu_page = page
        self.menu_index = 0
        self.menu_enter_t = 0.0
        self.menu_type_t = 0.0
        self.paused_game = False
        self.ui_pixels.clear()
        self._music_menu()

    def _pause_to_menu(self):
        self.state = STATE_MENU
        self.menu_page = "main"
        self.menu_index = 0
        self.menu_enter_t = 0.0
        self.menu_type_t = 0.0
        self.paused_game = True
        self.ui_pixels.clear()
        self._music_menu()

    def start_game(self):
        self.snake.reset()
        self.fruits.clear()
        self.particles.clear()
        self.score = 0
        self.fruits_eaten = {FruitType.NORMAL: 0, FruitType.GOLDEN: 0, FruitType.SPEED: 0}
        self.move_timer = 0
        self.special_timer = 0
        self.state = STATE_PLAYING
        self._spawn_fruit(FruitType.NORMAL)
        self._music_game()

    def game_over(self):
        self.state = STATE_GAME_OVER
        if self.score > self.high_score:
            self.high_score = self.score
            self._save_settings()

        self.go_enter_t = 0.0
        self.go_score_display = 0
        self.go_burst_done = False

        self._music_stop()
        self.sounds.play_gameover()

    # ======================================================
    # FRUTAS / VELOCIDADE
    # ======================================================

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

    def get_speed(self):
        speed = SNAKE_SPEED + (self.score // 50) * SPEED_INCREMENT
        if self.snake.speed_boost:
            speed += SPEED_BOOST_AMOUNT
        return min(speed, MAX_SPEED)

    def get_move_interval(self):
        return 1000 // self.get_speed()

    # ======================================================
    # EVENTOS
    # ======================================================

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
        items = self._current_menu_items()
        n = len(items)

        if key in (pygame.K_UP, pygame.K_w):
            self.menu_index = (self.menu_index - 1) % n
            return
        if key in (pygame.K_DOWN, pygame.K_s):
            self.menu_index = (self.menu_index + 1) % n
            return

        if self.menu_page == "audio":
            if key in (pygame.K_LEFT, pygame.K_a):
                self._audio_adjust(-1)
                return
            if key in (pygame.K_RIGHT, pygame.K_d):
                self._audio_adjust(+1)
                return

        if key in (pygame.K_RETURN, pygame.K_SPACE):
            self._menu_activate(items[self.menu_index])
            return

        if key == pygame.K_ESCAPE:
            self._menu_back()
            return

    def _handle_playing_input(self, key):
        scheme = self.settings.get("control_scheme", "both")
        allow_arrows = scheme in ("arrows", "both")
        allow_wasd = scheme in ("wasd", "both")

        direction_map = {}
        if allow_arrows:
            direction_map.update({
                pygame.K_UP: DIR_UP,
                pygame.K_DOWN: DIR_DOWN,
                pygame.K_LEFT: DIR_LEFT,
                pygame.K_RIGHT: DIR_RIGHT,
            })
        if allow_wasd:
            direction_map.update({
                pygame.K_w: DIR_UP,
                pygame.K_s: DIR_DOWN,
                pygame.K_a: DIR_LEFT,
                pygame.K_d: DIR_RIGHT,
            })

        if key in direction_map:
            self.snake.set_direction(direction_map[key])
        elif key in (pygame.K_SPACE, pygame.K_ESCAPE):
            self._pause_to_menu()

    def _handle_gameover_input(self, key):
        if key in (pygame.K_RETURN, pygame.K_SPACE):
            self.start_game()
        elif key == pygame.K_ESCAPE:
            self._enter_menu("main")

    def _handle_paused_input(self, key):
        if key in (pygame.K_SPACE, pygame.K_RETURN):
            self.state = STATE_PLAYING
        elif key == pygame.K_ESCAPE:
            self._enter_menu("main")

    # ======================================================
    # UPDATE
    # ======================================================

    def update(self):
        self.particles.update()

        if self.state in (STATE_MENU, STATE_GAME_OVER):
            self._update_ui_pixels()

        if self.state == STATE_MENU:
            self.menu_enter_t += self.dt
            self.menu_type_t += self.dt
            self.menu_snake.update()
            return

        if self.state == STATE_GAME_OVER:
            self.go_enter_t += self.dt
            if self.go_score_display < self.score:
                step = max(1, int(220 * self.dt + self.score * 0.02))
                self.go_score_display = min(self.score, self.go_score_display + step)
            return

        if self.state != STATE_PLAYING:
            return

        self.move_timer += self.dt_ms
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
                self.fruits_eaten[fruit.fruit_type] += 1
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

    # ======================================================
    # DRAW
    # ======================================================

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

        # Contadores de frutas no centro
        if self.header_fruit_sprites is None:
            sprites = _load_fruit_sprites()
            if sprites:
                self.header_fruit_sprites = [
                    pygame.transform.scale(s, (20, 20)) for s in sprites
                ]
            else:
                self.header_fruit_sprites = []

        icon_size = 20
        gap = 6
        fruit_order = [FruitType.NORMAL, FruitType.GOLDEN, FruitType.SPEED]
        counts = [str(self.fruits_eaten[ft]) for ft in fruit_order]
        count_surfs = [self.font_small.render(c, True, SCORE_COLOR) for c in counts]

        # Calcular largura total: (icone + gap + numero) * 3 + espaço entre grupos
        group_gap = 16
        total_w = 0
        for cs in count_surfs:
            total_w += icon_size + gap + cs.get_width()
        total_w += group_gap * (len(fruit_order) - 1)

        cx = WINDOW_WIDTH // 2 - total_w // 2
        cy = HEADER_HEIGHT // 2

        for i, ft in enumerate(fruit_order):
            if self.header_fruit_sprites and i < len(self.header_fruit_sprites):
                self.screen.blit(self.header_fruit_sprites[i], (cx, cy - icon_size // 2))
            cx += icon_size + gap
            self.screen.blit(count_surfs[i], count_surfs[i].get_rect(midleft=(cx, cy)))
            cx += count_surfs[i].get_width() + group_gap

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

    # ======================================================
    # MENU DRAW (layout corrigido)
    # ======================================================

    def _draw_menu_title(self, cx, title_y):
        full_title = "SNAKE"
        chars = int(self.menu_type_t / 0.07)
        shown = full_title[:min(len(full_title), chars)]
        cursor_on = int(self.t * 6) % 2 == 0
        if len(shown) < len(full_title) and cursor_on:
            shown = shown + "█"

        palette = [
            (255, 255, 255),
            (140, 255, 120),
            (100, 180, 60),
            (255, 215, 0),
            (180, 100, 210),
            (80, 180, 255),
            (255, 90, 90),
        ]
        idx = int(self.t * 20) % len(palette)
        title_color = palette[idx]
        evo_color = palette[(idx + 2) % len(palette)]
        glow_color = palette[(idx + 1) % len(palette)]

        shake_strength = 2
        sx = int(math.sin(self.t * 35) * shake_strength) + random.randint(-1, 1)
        sy = int(math.sin(self.t * 28) * shake_strength) + random.randint(-1, 1)

        glow_pulse = int(55 + (math.sin(self.t * 9.0) + 1.0) * 35)

        self._draw_text_with_glow(
            shown, self.font_title,
            title_color, glow_color,
            (cx + sx, title_y + sy),
            glow_offset=3,
            glow_alpha=glow_pulse
        )

        self._draw_text_with_glow(
            "EVOLUTION", self.font_medium,
            evo_color, glow_color,
            (cx - sx, title_y + 46 + sy),
            glow_offset=2,
            glow_alpha=int(glow_pulse * 0.7)
        )

    def _draw_menu(self):
        self.screen.fill(BORDER_COLOR)
        self.decorations.draw(self.screen)
        self._draw_grid()

        self.menu_snake.draw(self.screen, alpha=80)
        self._draw_overlay(110)

        cx, cy = WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2

        intro_t = self._clamp01(self.menu_enter_t / 0.70)
        intro = self._ease_out_back(intro_t)
        drop = int((1.0 - intro) * 72)

        panel_w, panel_h = 560, 420
        px = cx - panel_w // 2
        py = cy - panel_h // 2 + drop
        panel_rect = (px, py, panel_w, panel_h)

        if random.random() < 0.08:
            self._spawn_ui_pixels(panel_rect, amount=2, burst=False)

        panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        pygame.draw.rect(panel, (20, 30, 15, 210), (0, 0, panel_w, panel_h), border_radius=16)
        pygame.draw.rect(panel, (100, 180, 60, 130), (0, 0, panel_w, panel_h), width=2, border_radius=16)
        self.screen.blit(panel, (px, py))
        self._blit_panel_scanlines(px, py, panel_w, panel_h, alpha=26)

        # layout interno
        pad_x = 28
        pad_top = 18
        pad_bottom = 14
        footer_h = 38
        title_h = 100
        subtitle_h = 32

        inner_left = px + pad_x
        inner_right = px + panel_w - pad_x
        inner_w = inner_right - inner_left

        title_y = py + pad_top + 18
        self._draw_menu_title(cx, title_y)

        page_name = {
            "main": "",
            "settings": "Configurações",
            "controls": "Controles",
            "audio": "Sons",
        }.get(self.menu_page, "")
        if page_name:
            subtitle = self.font_subtitle.render(page_name, True, TEXT_SECONDARY)
            self.screen.blit(subtitle, subtitle.get_rect(center=(cx, py + title_h + subtitle_h // 2)))

        items_top = py + title_h + (subtitle_h if page_name else 0)
        items_bottom = py + panel_h - footer_h - pad_bottom
        items_h = max(10, items_bottom - items_top)

        items = self._current_menu_items()
        n = len(items)

        line_h = 34
        gap = 8
        needed = n * line_h + (n - 1) * gap
        if needed > items_h:
            gap = max(4, gap - int((needed - items_h) / max(1, n)))
            needed = n * line_h + (n - 1) * gap
            if needed > items_h:
                line_h = max(30, line_h - int((needed - items_h) / max(1, n)))
                needed = n * line_h + (n - 1) * gap

        start_y = items_top + (items_h - needed) // 2 + line_h // 2

        for i, label in enumerate(items):
            y = start_y + i * (line_h + gap)
            selected = (i == self.menu_index)

            if selected:
                w = min(420, inner_w)
                h = line_h + 6
                hx = cx - w // 2
                hy = y - h // 2
                hi = pygame.Surface((w, h), pygame.SRCALPHA)
                hi.fill((140, 255, 120, 32))
                pygame.draw.rect(hi, (140, 255, 120, 90), (0, 0, w, h), 2, border_radius=10)
                self.screen.blit(hi, (hx, hy))

            color = TEXT_COLOR if selected else TEXT_SECONDARY
            surf = self._render_fit(label, self.font_medium, self.font_small, color, max_width=int(inner_w * 0.92))
            rect = surf.get_rect(center=(cx, y))
            self.screen.blit(surf, rect)

        footer_cy = py + panel_h - footer_h // 2
        hints = []
        if self.menu_page == "audio":
            hints = ["W/S Navegar", "A/D Ajustar", "ENTER Confirmar"]
        elif self.menu_page == "main" and not self.paused_game:
            hints = ["W/S Navegar", "ENTER Confirmar"]
        else:
            hints = ["W/S Navegar", "ENTER Confirmar", "ESC Voltar"]

        hint_text = "   ".join(hints)
        hint_surf = self._render_fit(hint_text, self.font_small, self.font_small, TEXT_SECONDARY, max_width=int(inner_w * 0.95))
        self.screen.blit(hint_surf, hint_surf.get_rect(center=(cx, footer_cy)))

        self._draw_ui_pixels()

    # ======================================================
    # GAME OVER
    # ======================================================

    def _draw_gameover_overlay(self):
        self._draw_overlay(200)
        cx, cy = WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2

        panel_rect = (cx - 240, cy - 170, 480, 340)
        if not self.go_burst_done:
            self._spawn_ui_pixels(panel_rect, amount=42, burst=True)
            self.go_burst_done = True

        glitch_phase = self.go_enter_t < 0.45
        ox = oy = 0
        if glitch_phase:
            strength = int(6 - self.go_enter_t * 10)
            strength = max(2, strength)
            ox = random.randint(-strength, strength)
            oy = random.randint(-strength, strength)

        glow_pulse = int(60 + (math.sin(self.t * 2.5) + 1.0) * 20)

        if glitch_phase:
            self._draw_text_with_glow("GAME OVER", self.font_large,
                                      GAMEOVER_COLOR, GAMEOVER_GLOW,
                                      (cx + ox - 6, cy - 80 + oy), 3, glow_alpha=35)
            self._draw_text_with_glow("GAME OVER", self.font_large,
                                      GAMEOVER_COLOR, GAMEOVER_GLOW,
                                      (cx + ox + 6, cy - 80 + oy), 3, glow_alpha=35)

        self._draw_text_with_glow("GAME OVER", self.font_large,
                                  GAMEOVER_COLOR, GAMEOVER_GLOW,
                                  (cx + ox, cy - 80 + oy), 3, glow_alpha=glow_pulse)

        score_text = self.font_medium.render(f"Pontuacao: {self.go_score_display}", True, TEXT_COLOR)
        self.screen.blit(score_text, score_text.get_rect(center=(cx, cy)))

        if self.score >= self.high_score and self.score > 0:
            pulse = abs(math.sin(self.t * 3.2)) * 0.35 + 0.65
            record_text = self.font_medium.render("Novo Recorde!", True, SCORE_COLOR).convert_alpha()
            record_text.set_alpha(int(255 * pulse))
            self.screen.blit(record_text, record_text.get_rect(center=(cx, cy + 50)))
        elif self.high_score > 0:
            hs_text = self.font_small.render(f"Recorde: {self.high_score}", True, TEXT_SECONDARY)
            self.screen.blit(hs_text, hs_text.get_rect(center=(cx, cy + 50)))

        restart = self.font_small.render("ENTER para jogar novamente", True, TEXT_COLOR)
        self.screen.blit(restart, restart.get_rect(center=(cx, cy + 120)))

        menu_text = self.font_small.render("ESC para voltar ao menu", True, TEXT_SECONDARY)
        self.screen.blit(menu_text, menu_text.get_rect(center=(cx, cy + 150)))

        self._draw_ui_pixels()
        self.particles.draw(self.screen)

    def _draw_pause_overlay(self):
        self._draw_overlay(150)
        cx, cy = WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2
        self._draw_text_with_glow("PAUSADO", self.font_large, TEXT_COLOR, TEXT_SECONDARY, (cx, cy - 30))
        resume = self.font_small.render("P ou ENTER para continuar", True, TEXT_SECONDARY)
        self.screen.blit(resume, resume.get_rect(center=(cx, cy + 30)))

    # ======================================================
    # LOOP PRINCIPAL
    # ======================================================

    def run(self):
        running = True
        while running:
            self.dt_ms = self.clock.tick(FPS)
            self.dt = self.dt_ms / 1000.0
            self.t += self.dt

            running = self.handle_events()
            self.update()
            self.draw()

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()