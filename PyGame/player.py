import pygame

from bullet import Bullet


class Player:  # Класс для игрока.
    def __init__(self, field):  # Инициализирует игрока и задает начальные параметры.
        self.field = field
        self.position = [field.rows - 2, (field.cols // 2) - 2]
        self.direction = "player_tank_up"
        self.tower_direction = "player_tower_up"
        self.speed = 3
        self.animation_state = False
        self.rect = pygame.Rect(self.position[1] * 40, self.position[0] * 40, 40, 40)
        self.textures = self.load_textures()
        self.bullet_active = False
        self.directions_map = {
            "player_tower_up": (0, -10, "bullet_up"),
            "player_tower_down": (0, 10, "bullet_down"),
            "player_tower_left": (-10, 0, "bullet_left"),
            "player_tower_right": (10, 0, "bullet_right"),
        }

    @staticmethod
    def load_textures():  # Загружает текстуры для танка и башни игрока.
        return {
            "player_tank_up": pygame.image.load("textures/tank1_up.png"),
            "player_tank_down": pygame.image.load("textures/tank1_down.png"),
            "player_tank_left": pygame.image.load("textures/tank1_left.png"),
            "player_tank_right": pygame.image.load("textures/tank1_right.png"),
            "player_tank_up2": pygame.image.load("textures/tank1_up2.png"),
            "player_tank_down2": pygame.image.load("textures/tank1_down2.png"),
            "player_tank_left2": pygame.image.load("textures/tank1_left2.png"),
            "player_tank_right2": pygame.image.load("textures/tank1_right2.png"),
            "player_tower_up": pygame.image.load("textures/tower_up.png"),
            "player_tower_down": pygame.image.load("textures/tower_down.png"),
            "player_tower_left": pygame.image.load("textures/tower_left.png"),
            "player_tower_right": pygame.image.load("textures/tower_right.png"),
        }

    def move(self, enemies):  # Обрабатывает движение игрока и изменение направления.
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        player_in_grass = self.is_in_grass()
        current_speed = 1.5 if player_in_grass else self.speed

        if keys[pygame.K_w]:
            dy = -current_speed
            self.animation_state = not self.animation_state
            self.direction = "player_tank_up2" if self.animation_state else "player_tank_up"

        elif keys[pygame.K_a]:
            dx = -current_speed
            self.animation_state = not self.animation_state
            self.direction = "player_tank_left2" if self.animation_state else "player_tank_left"

        elif keys[pygame.K_s]:
            dy = current_speed
            self.animation_state = not self.animation_state
            self.direction = "player_tank_down2" if self.animation_state else "player_tank_down"

        elif keys[pygame.K_d]:
            dx = current_speed
            self.animation_state = not self.animation_state
            self.direction = "player_tank_right2" if self.animation_state else "player_tank_right"

        if keys[pygame.K_UP]:
            self.tower_direction = "player_tower_up"
        elif keys[pygame.K_DOWN]:
            self.tower_direction = "player_tower_down"
        elif keys[pygame.K_LEFT]:
            self.tower_direction = "player_tower_left"
        elif keys[pygame.K_RIGHT]:
            self.tower_direction = "player_tower_right"

        new_pos = [self.position[0] + dy / 40, self.position[1] + dx / 40]
        if not self.is_collision(new_pos, enemies):
            self.position[0] += dy / 40
            self.position[1] += dx / 40
            self.rect.x = self.position[1] * 40
            self.rect.y = self.position[0] * 40

    def shoot(self, bullets):  # Стреляет пулей, если прошлая пуля исчезла.
        if self.bullet_active:
            return

        tank_x = self.position[1] * 40
        tank_y = self.position[0] * 40
        base_direction = self.tower_direction.replace("2", "")

        bullet_x, bullet_y = tank_x, tank_y
        if base_direction == "player_tower_up":
            bullet_x = tank_x + 20 - 5
            bullet_y = tank_y - 5
        elif base_direction == "player_tower_down":
            bullet_x = tank_x + 20 - 5
            bullet_y = tank_y + 40 - 15
        elif base_direction == "player_tower_left":
            bullet_x = tank_x - 5
            bullet_y = tank_y + 20 - 5
        elif base_direction == "player_tower_right":
            bullet_x = tank_x + 40 - 15
            bullet_y = tank_y + 20 - 5

        bullet = Bullet(bullet_x, bullet_y, self.directions_map[base_direction][:2],
                        self.directions_map[base_direction][2], "player")
        bullets.append(bullet)
        self.bullet_active = True

    def update_bullet_status(self, bullets):  # Обновляет статус пули игрока.
        self.bullet_active = any(b.active for b in bullets)

    def is_collision(self, new_pos, enemies):  # Проверяет столкновения игрока с другими объектами.
        tolerance = 3

        tank_rect = pygame.Rect(new_pos[1] * 40 + 1, new_pos[0] * 40 + 1, 38, 38)

        if tank_rect.colliderect(self.field.base_rect):
            return True

        for enemy in enemies:
            enemy_rect = pygame.Rect(enemy.rect.x + 1, enemy.rect.y + 1, 38, 38)
            if tank_rect.colliderect(enemy_rect):
                intersection = tank_rect.clip(enemy_rect)
                if intersection.width > tolerance or intersection.height > tolerance:
                    return True

        dx = (new_pos[1] * 40) - self.rect.x
        dy = (new_pos[0] * 40) - self.rect.y

        for row_idx, row in enumerate(self.field.grid):
            for col_idx, tile in enumerate(row):
                if tile and tile["type"] not in ["grass", "base", "water", "empty"]:
                    tile_rect = pygame.Rect(col_idx * 40, row_idx * 40, 40, 40)

                    if tank_rect.colliderect(tile_rect):
                        intersection = tank_rect.clip(tile_rect)

                        if dx != 0 and intersection.width > tolerance:
                            return True

                        if dy != 0 and intersection.height > tolerance:
                            return True

        return False

    def is_in_grass(self):  # Проверяет, находится ли игрок в траве.
        tank_rect = pygame.Rect(self.position[1] * 40, self.position[0] * 40, 40, 40)

        for row in range(len(self.field.grid)):
            for col in range(len(self.field.grid[row])):
                tile = self.field.grid[row][col]
                if tile and tile["type"] == "grass":
                    grass_rect = pygame.Rect(col * 40, row * 40, 40, 40)
                    if tank_rect.colliderect(grass_rect):
                        return True
        return False

    def check_water_collision(self):  # Проверяет столкновение игрока с водой.
        tank_rect = pygame.Rect(self.position[1] * 40, self.position[0] * 40, 40, 40)
        overlap_threshold = 20

        for row_idx, row in enumerate(self.field.grid):
            for col_idx, tile in enumerate(row):
                if tile and tile["type"] == "water":
                    water_rect = pygame.Rect(col_idx * 40, row_idx * 40, 40, 40)
                    if tank_rect.colliderect(water_rect):
                        intersection = tank_rect.clip(water_rect)
                        if intersection.width * intersection.height >= overlap_threshold ** 2:
                            return True
        return False

    def draw(self, screen):  # Отображает игрока на экране.
        tank_x, tank_y = self.position[1] * 40, self.position[0] * 40
        screen.blit(self.textures[self.direction], (tank_x, tank_y))
        screen.blit(self.textures[self.tower_direction], (tank_x, tank_y))
