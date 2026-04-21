import sys
import pygame as pg
import json
import os

CAPTION = "Echoes of the Forgotten Throne"

# Window size constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
LIGHT_GRAY = (192, 192, 192)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)


class Button:

    def __init__(self, x, y, width, height, text, text_color=WHITE,
                 normal_color=DARK_GRAY, hover_color=GRAY, font=None):
        self.rect = pg.Rect(x, y, width, height)
        self.text = text
        self.text_color = text_color
        self.normal_color = normal_color
        self.hover_color = hover_color
        self.is_hovered = False
        self.font = font

    def draw(self, screen, surface):
        color = self.hover_color if self.is_hovered else self.normal_color
        pg.draw.rect(screen, color, self.rect)
        pg.draw.rect(screen, WHITE, self.rect, 2)

        text_surface = surface.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        return self.is_hovered

    def is_clicked(self, event):
        return (
                event.type == pg.MOUSEBUTTONDOWN
                and event.button == 1
                and self.rect.collidepoint(event.pos)
        )


class Game:

    def __init__(self):
        pg.init()
        pg.mixer.init()

        self.screen = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pg.display.set_caption(CAPTION)
        self.fonts = self.load_fonts()
        self.title_font = self.get_font('huge')
        self.menu_font = self.get_font('large')
        self.small_font = self.get_font('small')

        self.state = "menu"
        self.running = True

        self.player_x = WINDOW_WIDTH // 2
        self.player_y = WINDOW_HEIGHT // 2
        self.settings = self.load_settings()
        self.player_speed = self.settings.get("player_speed", 5)
        self.moving_to_target = False

        self.create_speed_slider()
        self.create_menu_buttons()

        # Запускаем музыку главного меню при старте
        self.load_and_play_music()

    def load_fonts(self):
        fonts = {}
        fonts_dir = os.path.join('assets', 'fonts')

        if not os.path.exists(fonts_dir):
            os.makedirs(fonts_dir)
            print(f"Создана папка: {fonts_dir}")
            print("ПОЛОЖИ СЮДА ФАЙЛЫ ШРИФТОВ!")

        font_files = []
        if os.path.exists(fonts_dir):
            for file in os.listdir(fonts_dir):
                if file.endswith(('.ttf', '.otf')):
                    font_files.append(file)

        for font_file in font_files:
            font_path = os.path.join(fonts_dir, font_file)
            font_name = os.path.splitext(font_file)[0]

            try:
                fonts[font_name] = {
                    'small': pg.font.Font(font_path, 16),
                    'medium': pg.font.Font(font_path, 24),
                    'large': pg.font.Font(font_path, 36),
                    'huge': pg.font.Font(font_path, 48),
                }
                print(f"Font loaded: {font_file}")
            except Exception as e:
                print(f"Error loading font {font_file}: {e}")

        if not fonts:
            print("No fonts found in assets/fonts. Using default pygame font.")
            fonts['default'] = {
                'small': pg.font.Font(None, 16),
                'medium': pg.font.Font(None, 24),
                'large': pg.font.Font(None, 36),
                'huge': pg.font.Font(None, 48),
            }
        return fonts

    def get_font(self, size='medium', font_name=None):
        if font_name is None:
            font_name = list(self.fonts.keys())[0]
        if font_name not in self.fonts:
            font_name = 'default'
        return self.fonts[font_name].get(size, self.fonts[font_name]['medium'])

    def load_settings(self):
        settings_path = "config/settings.json"
        default_settings = {"player_speed": 2}

        try:
            os.makedirs("config", exist_ok=True)
            if not os.path.exists(settings_path):
                with open(settings_path, 'w', encoding='utf-8') as f:
                    json.dump(default_settings, f, indent=2)
                return default_settings
            with open(settings_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading settings: {e}")
            return default_settings

    def save_settings(self):
        settings_path = "config/settings.json"
        try:
            with open(settings_path, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def create_speed_slider(self):
        self.speed_slider = {
            "rect": pg.Rect(WINDOW_WIDTH // 2 - 150, 250, 300, 10),
            "handle_rect": pg.Rect(0, 0, 20, 30),
            "min_value": 1,
            "max_value": 10,
            "value": self.player_speed,
            "dragging": False
        }
        self.update_slider_handle()

    def update_slider_handle(self):
        slider = self.speed_slider
        value_range = slider["max_value"] - slider["min_value"]
        pos_ratio = (slider["value"] - slider["min_value"]) / value_range
        handle_x = slider["rect"].x + (slider["rect"].width * pos_ratio) - 10
        slider["handle_rect"].x = handle_x
        slider["handle_rect"].centery = slider["rect"].centery

    def create_menu_buttons(self):
        button_width = 300
        button_height = 60
        start_x = WINDOW_WIDTH // 2 - button_width // 2
        start_y = 250
        spacing = 80

        self.menu_buttons = {
            "new_game": Button(start_x, start_y, button_width, button_height,
                               "Новая игра", GREEN, DARK_GRAY, GRAY),
            "continue": Button(start_x, start_y + spacing, button_width, button_height,
                               "Продолжить", WHITE, DARK_GRAY, GRAY),
            "options": Button(start_x, start_y + spacing * 2, button_width, button_height,
                              "Настройки", BLUE, DARK_GRAY, GRAY),
            "exit": Button(start_x, start_y + spacing * 3, button_width, button_height,
                           "Выход", RED, DARK_GRAY, GRAY)
        }

        back_button_width = 200
        back_button_height = 50
        self.back_button = Button(
            WINDOW_WIDTH // 2 - back_button_width // 2,
            WINDOW_HEIGHT - 100,
            back_button_width,
            back_button_height,
            "Назад",
            WHITE,
            DARK_GRAY,
            GRAY
        )

    # ------------------- МУЗЫКА -------------------
    def load_and_play_music(self):
        """Загружает и запускает фоновую музыку главного меню."""
        if pg.mixer.music.get_busy():
            return

        music_path = os.path.join('assets', 'sound', 'menu_theme.wav')
        try:
            if os.path.exists(music_path):
                pg.mixer.music.load(music_path)
                pg.mixer.music.set_volume(0.5)
                pg.mixer.music.play(-1)
                print("Музыка меню запущена")
            else:
                print(f"Файл музыки меню не найден: {music_path}")
        except pg.error as e:
            print(f"Ошибка загрузки музыки меню: {e}")

    def load_and_play_game_music(self):
        """Загружает и запускает музыку для игрового процесса."""
        if pg.mixer.music.get_busy():
            return

        music_path = os.path.join('assets', 'sound', 'game_theme.wav')
        try:
            if os.path.exists(music_path):
                pg.mixer.music.load(music_path)
                pg.mixer.music.set_volume(0.4)
                pg.mixer.music.play(-1)
                print("Игровая музыка запущена")
            else:
                print(f"Файл игровой музыки не найден: {music_path}")
        except pg.error as e:
            print(f"Ошибка загрузки игровой музыки: {e}")

    def stop_music(self):
        """Останавливает музыку, если она играет."""
        if pg.mixer.music.get_busy():
            pg.mixer.music.stop()
            print("Музыка остановлена")
    # ------------------------------------------------

    def handle_menu_events(self, event):
        if event.type == pg.MOUSEMOTION:
            for button in self.menu_buttons.values():
                button.check_hover(event.pos)

        elif event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.menu_buttons["new_game"].is_clicked(event):
                    self.stop_music()
                    self.state = "game"
                    self.load_and_play_game_music()
                elif self.menu_buttons["continue"].is_clicked(event):
                    self.stop_music()
                    self.state = "game"
                    self.load_and_play_game_music()
                elif self.menu_buttons["options"].is_clicked(event):
                    self.state = "options"
                elif self.menu_buttons["exit"].is_clicked(event):
                    self.running = False

    def handle_options_events(self, event):
        if event.type == pg.MOUSEMOTION:
            self.back_button.check_hover(event.pos)
            if self.speed_slider["dragging"]:
                self.update_slider_value(event.pos[0])

        elif event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_pos = event.pos
                if self.back_button.is_clicked(event):
                    self.save_settings()
                    self.state = "menu"
                    self.load_and_play_music()
                elif self.speed_slider["handle_rect"].collidepoint(mouse_pos):
                    self.speed_slider["dragging"] = True
                elif self.speed_slider["rect"].collidepoint(mouse_pos):
                    self.update_slider_value(mouse_pos[0])
                    self.speed_slider["dragging"] = True

        elif event.type == pg.MOUSEBUTTONUP:
            if event.button == 1:
                self.speed_slider["dragging"] = False

    def update_slider_value(self, mouse_x):
        slider = self.speed_slider
        mouse_x = max(slider["rect"].left, min(mouse_x, slider["rect"].right))
        pos_ratio = (mouse_x - slider["rect"].left) / slider["rect"].width
        value_range = slider["max_value"] - slider["min_value"]
        new_value = slider["min_value"] + (value_range * pos_ratio)
        slider["value"] = round(new_value)
        self.player_speed = slider["value"]
        self.settings["player_speed"] = slider["value"]
        self.update_slider_handle()

    def handle_game_events(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                self.state = "menu"
                self.stop_music()
                self.load_and_play_music()
            elif event.key == pg.K_SPACE:
                self.moving_to_target = False

        elif event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.target_x, self.target_y = event.pos
                self.moving_to_target = True
            elif event.button == 3:
                self.player_x, self.player_y = event.pos
                self.moving_to_target = False

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False

            if self.state == "menu":
                self.handle_menu_events(event)
            elif self.state == "options":
                self.handle_options_events(event)
            elif self.state == "game":
                self.handle_game_events(event)

    def update_game(self):
        keys = pg.key.get_pressed()
        moved = False

        if keys[pg.K_LEFT] or keys[pg.K_a]:
            self.player_x -= self.player_speed
            moved = True
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.player_x += self.player_speed
            moved = True
        if keys[pg.K_UP] or keys[pg.K_w]:
            self.player_y -= self.player_speed
            moved = True
        if keys[pg.K_DOWN] or keys[pg.K_s]:
            self.player_y += self.player_speed
            moved = True

        if moved:
            self.moving_to_target = False

        if self.moving_to_target:
            dx = self.target_x - self.player_x
            dy = self.target_y - self.player_y
            distance = (dx ** 2 + dy ** 2) ** 0.5

            if distance < self.player_speed:
                self.player_x = self.target_x
                self.player_y = self.target_y
                self.moving_to_target = False
            else:
                self.player_x += (dx / distance) * self.player_speed
                self.player_y += (dy / distance) * self.player_speed

        self.player_x = max(10, min(self.player_x, WINDOW_WIDTH - 10))
        self.player_y = max(10, min(self.player_y, WINDOW_HEIGHT - 10))

    def draw_menu(self):
        self.screen.fill(BLACK)

        title1 = self.title_font.render("PythonRL", True, GREEN)
        title2 = self.title_font.render("Echoes of the Forgotten Throne", True, PURPLE)

        title1_rect = title1.get_rect(center=(WINDOW_WIDTH // 2, 100))
        title2_rect = title2.get_rect(center=(WINDOW_WIDTH // 2, 160))

        self.screen.blit(title1, title1_rect)
        self.screen.blit(title2, title2_rect)

        for button in self.menu_buttons.values():
            button.draw(self.screen, self.menu_font)

        version_text = self.small_font.render("v0.1.0 Alpha", True, GRAY)
        self.screen.blit(version_text, (WINDOW_WIDTH - 150, WINDOW_HEIGHT - 30))

    def draw_options(self):
        self.screen.fill(BLACK)

        title = self.title_font.render("Настройки", True, BLUE)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 80))
        self.screen.blit(title, title_rect)

        speed_label = self.menu_font.render("Скорость игрока:", True, WHITE)
        label_rect = speed_label.get_rect(center=(WINDOW_WIDTH // 2, 200))
        self.screen.blit(speed_label, label_rect)

        speed_value = self.menu_font.render(
            str(self.speed_slider["value"]),
            True,
            YELLOW
        )
        value_rect = speed_value.get_rect(
            center=(WINDOW_WIDTH // 2 + 200, 200)
        )
        self.screen.blit(speed_value, value_rect)

        slider = self.speed_slider

        pg.draw.rect(self.screen, GRAY, slider["rect"])
        pg.draw.rect(self.screen, WHITE, slider["rect"], 2)

        filled_width = (slider["value"] - slider["min_value"]) / (slider["max_value"] - slider["min_value"])
        filled_rect = pg.Rect(
            slider["rect"].x,
            slider["rect"].y,
            slider["rect"].width * filled_width,
            slider["rect"].height
        )
        pg.draw.rect(self.screen, GREEN, filled_rect)

        handle_color = YELLOW if slider["dragging"] else WHITE
        pg.draw.rect(self.screen, handle_color, slider["handle_rect"])
        pg.draw.rect(self.screen, DARK_GRAY, slider["handle_rect"], 2)

        min_text = self.small_font.render(str(slider["min_value"]), True, GRAY)
        max_text = self.small_font.render(str(slider["max_value"]), True, GRAY)

        min_rect = min_text.get_rect(
            midright=(slider["rect"].left - 10, slider["rect"].centery)
        )
        max_rect = max_text.get_rect(
            midleft=(slider["rect"].right + 10, slider["rect"].centery)
        )

        self.screen.blit(min_text, min_rect)
        self.screen.blit(max_text, max_rect)

        hint = self.small_font.render("Перетаскивайте для изменения", True, LIGHT_GRAY)
        hint_rect = hint.get_rect(center=(WINDOW_WIDTH // 2, 320))
        self.screen.blit(hint, hint_rect)

        self.back_button.draw(self.screen, self.menu_font)

    def draw_game(self):
        self.screen.fill(BLACK)

        if self.moving_to_target:
            pg.draw.circle(self.screen, YELLOW,
                           (int(self.target_x), int(self.target_y)), 8, 2)
            pg.draw.line(self.screen, YELLOW,
                         (self.player_x, self.player_y),
                         (self.target_x, self.target_y), 1)

        pg.draw.circle(self.screen, GREEN,
                       (int(self.player_x), int(self.player_y)), 10)
        pg.draw.circle(self.screen, WHITE,
                       (int(self.player_x), int(self.player_y)), 10, 2)

        texts = [
            "ESC - menu",
            "WASD/Arrows - movement",
            "LMB - move to cursor",
            "RMB - teleport to cursor",
            "SPACE - stop movement"
        ]

        y_offset = 10
        for text in texts:
            rendered = self.small_font.render(text, True, WHITE)
            self.screen.blit(rendered, (10, y_offset))
            y_offset += 25

    def draw(self):
        if self.state == "menu":
            self.draw_menu()
        elif self.state == "options":
            self.draw_options()
        elif self.state == "game":
            self.update_game()
            self.draw_game()
        pg.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            if self.state == "game":
                self.update_game()
            self.draw()
        pg.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
