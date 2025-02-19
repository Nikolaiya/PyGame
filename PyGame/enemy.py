import time
import random

import pygame

from bullet import Bullet


class Enemy:  # Класс для врагов.
    def __init__(self, field):  # Инициализирует врага и задает начальные параметры.
        self.field = field
        self.position = None
        self.rect = None
        self.speed = 3
        self.direction = random.choice([(0, -1), (0, 1), (-1, 0), (1, 0)])
        self.textures = self.load_textures()
        self.texture = self.get_texture()
        self.move_timer = random.uniform(2, 5)
        self.change_dir_timer = time.time() + 5
        self.stuck_time = None
        self.bullet_active = False
        self.last_shot_time = time.time()
        self.shoot_interval = 2

    @staticmethod
    def load_textures():  # Загружает текстуры для вражеского танка.
        return {
            (0, -1): ["enemy_tank_up", "enemy_tank_up2"],
            (0, 1): ["enemy_tank_down", "enemy_tank_down2"],
            (-1, 0): ["enemy_tank_left", "enemy_tank_left2"],
            (1, 0): ["enemy_tank_right", "enemy_tank_right2"],
        }

    def spawn_enemy(self, enemies, player_rect):  # Появление врагов на поле избегая столкновений.
        max_attempts = 100
        attempts = 0

        while attempts < max_attempts:
            row = random.randint(0, 2)
            col = random.randint(1, self.field.cols - 2)
            enemy_rect = pygame.Rect(col * 40, row * 40, 40, 40)

            if self.is_valid_spawn(row, col, enemy_rect, enemies, player_rect):
                return [row, col], enemy_rect

            attempts += 1

        return None, None

    def is_valid_spawn(self, row, col, enemy_rect, enemies,
                       player_rect):  # Проверяет можно ли появится врагу в указанной позиции.
        if self.field.grid[row][col] and self.field.grid[row][col]["type"] in ["wall", "unbreakable_wall", "water"]:
            return False

        if any(enemy_rect.colliderect(pygame.Rect(e.rect.x, e.rect.y, 40, 40)) for e in enemies):
            return False

        if enemy_rect.colliderect(player_rect):
            return False

        return True

    def get_texture(self):  # Возвращает текущую текстуру врага для анимации.
        base_texture = self.textures[self.direction][0]
        return base_texture + "2" if time.time() % 0.2 < 0.1 else base_texture

    def move(self, enemies, player_rect):  # Обрабатывает движение врага и изменение в направления.
        current_time = time.time()

        if self.stuck_time and current_time >= self.stuck_time:
            self.direction = random.choice(list(self.textures.keys()))
            self.stuck_time = None
            self.change_dir_timer = current_time + 5

        if current_time >= self.change_dir_timer:
            self.direction = random.choice(list(self.textures.keys()))
            self.change_dir_timer = current_time + 5

        dx, dy = self.direction
        move_distance = self.speed

        enemy_in_grass = self.is_in_grass()
        current_speed = 1.5 if enemy_in_grass else move_distance

        new_x = self.rect.x + dx * current_speed
        new_y = self.rect.y + dy * current_speed

        if not self.is_collision(new_x, new_y, enemies, player_rect):
            self.rect.x, self.rect.y = new_x, new_y
            self.position = [self.rect.y // 40, self.rect.x // 40]
            self.stuck_time = None
        else:
            if self.stuck_time is None:
                self.stuck_time = current_time + 1

    def fire(self, enemy_bullets):  # Стреляет пулей, если прошлая пуля исчезла.
        current_time = time.time()
        if current_time - self.last_shot_time >= self.shoot_interval and not self.bullet_active:
            tank_x = self.rect.x
            tank_y = self.rect.y

            direction_map = {
                (0, -1): (0, -5, "enemy_bullet_up", tank_x + 20 - 5, tank_y - 5),
                (0, 1): (0, 5, "enemy_bullet_down", tank_x + 20 - 5, tank_y + 40 - 15),
                (-1, 0): (-5, 0, "enemy_bullet_left", tank_x - 5, tank_y + 20 - 5),
                (1, 0): (5, 0, "enemy_bullet_right", tank_x + 40 - 15, tank_y + 20 - 5),
            }

            bullet_dx, bullet_dy, bullet_texture, bullet_x, bullet_y = direction_map.get(
                self.direction, (0, -5, "enemy_bullet_up", tank_x + 20 - 5, tank_y - 5)
            )

            bullet = Bullet(bullet_x, bullet_y, (bullet_dx, bullet_dy), bullet_texture, "enemy")
            enemy_bullets.append(bullet)
            self.bullet_active = True
            self.last_shot_time = current_time
            self.shoot_interval = 2.0

    def is_collision(self, x, y, enemies, player_rect):  # Проверяет столкновения врага с другими объектами.
        tolerance = 3

        enemy_rect = pygame.Rect(x + 1, y + 1, 38, 38)

        if enemy_rect.colliderect(player_rect):
            intersection = enemy_rect.clip(player_rect)
            if intersection.width > tolerance or intersection.height > tolerance:
                return True

        for enemy in enemies:
            if enemy is not self:
                other_rect = pygame.Rect(enemy.rect.x + 1, enemy.rect.y + 1, 38, 38)
                if enemy_rect.colliderect(other_rect):
                    intersection = enemy_rect.clip(other_rect)
                    if intersection.width > tolerance or intersection.height > tolerance:
                        return True

        for row_idx, row in enumerate(self.field.grid):
            for col_idx, tile in enumerate(row):
                if tile and tile["type"] not in ["grass", "base"]:
                    tile_rect = pygame.Rect(col_idx * 40, row_idx * 40, 40, 40)
                    if enemy_rect.colliderect(tile_rect):
                        intersection = enemy_rect.clip(tile_rect)
                        if intersection.width > tolerance or intersection.height > tolerance:
                            return True

        return False

    def is_in_grass(self):  # Проверяет, находится ли враг в траве.
        enemy_rect = pygame.Rect(self.rect.x, self.rect.y, 40, 40)

        for row in range(len(self.field.grid)):
            for col in range(len(self.field.grid[row])):
                tile = self.field.grid[row][col]
                if tile and tile["type"] == "grass":
                    grass_rect = pygame.Rect(col * 40, row * 40, 40, 40)
                    if enemy_rect.colliderect(grass_rect):
                        return True
        return False

    def draw(self, screen):  # Отображает врага на экране.
        screen.blit(pygame.image.load(f"textures/{self.get_texture()}.png"), (self.rect.x, self.rect.y))
