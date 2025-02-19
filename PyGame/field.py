import time
import random

import pygame


class Field:  # Класс для поля.
    def __init__(self):  # Инициализирует игровое поле, загружает текстуры и генерирует поле.
        self.rows = 15
        self.cols = 15
        self.cell_size = 40
        self.grid, self.base_position = self.generate_field(rows=15, cols=15)
        self.textures = self.load_textures()
        self.base_rect = pygame.Rect(self.base_position[1] * self.cell_size, self.base_position[0] * self.cell_size,
                                     self.cell_size, self.cell_size)
        self.water_textures = ["textures/water1.png", "textures/water2.png", "textures/water3.png"]
        self.current_water_index = 0
        self.last_water_update = time.time()

    @staticmethod
    def load_textures():  # Загружает текстуры для всех элементов поля.
        return {
            "background": pygame.image.load("textures/fon.png"),
            "wall": pygame.image.load("textures/wall1.png"),
            "wall2": pygame.image.load("textures/wall2.png"),
            "wall3": pygame.image.load("textures/wall3.png"),
            "wall4": pygame.image.load("textures/wall4.png"),
            "unbreakable_wall": pygame.image.load("textures/unbreakable.png"),
            "grass": pygame.image.load("textures/grass.png"),
            "base": pygame.image.load("textures/emblem.png"),
            "water": pygame.image.load("textures/water1.png"),
        }

    @staticmethod
    def generate_field(rows, cols):  # Генерирует игровое поле с базой, стенами, водой и травой.
        field = []
        for row in range(rows):
            line = []
            for col in range(cols):
                if row == 0 or row == rows - 1 or col == 0 or col == cols - 1:
                    line.append({"type": "unbreakable_wall", "durability": -1})
                else:
                    tile = random.choices(
                        [None, {"type": "grass", "durability": 0}, {"type": "wall", "durability": 4}],
                        weights=[70, 15, 15]
                    )[0]
                    line.append(tile)
            field.append(line)

        base_row, base_col = rows - 2, cols // 2

        for dr in range(-2, 3):
            for dc in range(-2, 3):
                r, c = base_row + dr, base_col + dc
                if 0 <= r < rows and 0 <= c < cols:
                    field[r][c] = None

        protection_scheme = [
            (-1, -1, "wall"), (-1, 0, "wall"), (-1, 1, "wall"),
            (0, -1, "wall"), (0, 1, "wall"),
            (1, -1, "unbreakable_wall"), (1, 0, "unbreakable_wall"), (1, 1, "unbreakable_wall"),
            (2, -1, "unbreakable_wall"), (2, 0, "unbreakable_wall"), (2, 1, "unbreakable_wall"),
        ]
        for dr, dc, tile_type in protection_scheme:
            r, c = base_row + dr, base_col + dc
            if 0 <= r < rows and 0 <= c < cols:
                if tile_type == "wall":
                    field[r][c] = {"type": "wall", "durability": 4}
                elif tile_type == "unbreakable_wall":
                    field[r][c] = {"type": "unbreakable_wall", "durability": -1}

        field[base_row][base_col] = {"type": "base", "durability": -1}

        field[base_row + 1][base_col - 2] = {"type": "unbreakable_wall", "durability": -1}
        field[base_row + 1][base_col + 2] = {"type": "unbreakable_wall", "durability": -1}

        water_tiles = 0
        while water_tiles < 6:
            row = random.randint(1, rows - 2)
            col = random.randint(1, cols - 2)

            if (row <= 3 and any(field[r][col] and field[r][col]["type"] == "unbreakable_wall" for r in range(0, 3))) or \
                    field[row][col] is not None or \
                    (base_row - 2 <= row <= base_row + 2 and base_col - 2 <= col <= base_col + 2):
                continue

            field[row][col] = {"type": "water", "durability": -2}
            water_tiles += 1

        unbreakable = 0
        while unbreakable < 6:
            row = random.randint(1, rows - 2)
            col = random.randint(1, cols - 2)
            if field[row][col] is None and not (
                    base_row - 2 <= row <= base_row + 2 and base_col - 2 <= col <= base_col + 2):
                field[row][col] = {"type": "unbreakable_wall", "durability": -1}
                unbreakable += 1

        return field, [base_row, base_col]

    def draw(self, screen):  # Отображает игровое поле на экране.
        for row_idx, row in enumerate(self.grid):
            for col_idx, tile in enumerate(row):
                x, y = col_idx * self.cell_size, row_idx * self.cell_size
                screen.blit(self.textures["background"], (x, y))

        for row_idx, row in enumerate(self.grid):
            for col_idx, tile in enumerate(row):
                if tile and tile["type"] and tile["type"] != "grass":
                    x, y = col_idx * self.cell_size, row_idx * self.cell_size
                    screen.blit(self.textures[tile["type"]], (x, y))

        for row_idx, row in enumerate(self.grid):
            for col_idx, tile in enumerate(row):
                if tile and tile["type"] == "grass":
                    x, y = col_idx * self.cell_size, row_idx * self.cell_size
                    screen.blit(self.textures["grass"], (x, y))

    @staticmethod
    def draw_interface(screen, lives, enemy_tanks, enemies_killed, lives_lost, total_points, current_points,
                       overlay_y):  # Отображает интерфейс.
        pygame.draw.rect(screen, (0, 0, 0), (600, 0, 200, 600))

        enemy_icon = pygame.image.load("textures/mini_tank.png")
        life_icon = pygame.image.load("textures/life.png")

        for i in range(enemy_tanks):
            x = 610 + (i % 9) * 20
            y = 10 + (i // 9) * 20
            screen.blit(enemy_icon, (x, y))

        for i in range(lives):
            x = 610 + (i % 9) * 20
            y = 570 - (i // 9) * 20
            screen.blit(life_icon, (x, y))

        rows_of_lives = (lives + 8) // 9
        shift_up = max(0, rows_of_lives - 2) * 20

        text_y = 500 - shift_up
        points_y = 520 - shift_up

        font = pygame.font.SysFont("Arial", 16)

        text_surface = font.render("Общее количество очков:", True, (255, 255, 255))
        points_surface = font.render(str(total_points), True, (255, 255, 255))
        screen.blit(text_surface, (610, text_y))
        screen.blit(points_surface, (610, points_y))

        if overlay_y == 0:
            enemies_killed_text = font.render(f"Убито врагов: {enemies_killed}", True, (255, 255, 255))
            screen.blit(enemies_killed_text, (610, text_y - 120))

            lives_lost_text = font.render(f"Потерянно жизней: {lives_lost}", True, (255, 255, 255))
            screen.blit(lives_lost_text, (610, text_y - 80))

            current_points_text = font.render(f"Получено очков: {current_points}", True, (255, 255, 255))
            screen.blit(current_points_text, (610, text_y - 40))

    def draw_grass(self, screen):  # Отображает траву на поле.
        for row_idx, row in enumerate(self.grid):
            for col_idx, tile in enumerate(row):
                if tile and "type" in tile and tile["type"] == "grass":
                    x, y = col_idx * self.cell_size, row_idx * self.cell_size
                    screen.blit(self.textures["grass"], (x, y))
