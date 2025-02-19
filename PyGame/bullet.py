import pygame


class Bullet:  # Класс для пули.
    def __init__(self, x, y, direction, texture, shooter):  # Инициализирует пулю и задает начальные параметры.
        self.x = x
        self.y = y
        self.dx, self.dy = direction
        self.texture = pygame.image.load(f"textures/{texture}.png")
        self.shooter = shooter
        self.speed = 1
        self.rect = pygame.Rect(self.x, self.y, 10, 10)
        self.active = True

    def move(self, field, enemies, player_rect, game):  # Обновляет позицию пули и проверяет столкновения.
        if not self.active:
            return True

        for _ in range(10):
            future_rect = pygame.Rect(self.x + self.dx, self.y + self.dy, 10, 10)

            if self.handle_collision(field, enemies, player_rect, future_rect, game):
                self.active = False
                return True

            self.x += self.dx // abs(self.dx) if self.dx != 0 else 0
            self.y += self.dy // abs(self.dy) if self.dy != 0 else 0
            self.rect.topleft = (self.x, self.y)

        return False

    def handle_collision(self, field, enemies, player_rect, bullet_rect,
                         game):  # Обрабатывает столкновения пули с врагами, стенами, базой и игроком.
        if self.shooter == "player":
            for enemy in enemies[:]:
                enemy_rect = pygame.Rect(enemy.rect.x, enemy.rect.y, 40, 40)
                if bullet_rect.colliderect(enemy_rect):
                    enemies.remove(enemy)
                    game.enemy_tanks -= 1
                    game.enemies_killed += 1
                    game.current_points += 10
                    return True

        if self.shooter == "enemy" and bullet_rect.colliderect(player_rect):
            game.lives -= 1
            game.lives_lost += 1
            game.lost_due_to_enemy += 1
            game.current_points -= 5

            if game.lives > 0:
                game.player.position = [game.field.base_position[0], game.field.base_position[1] - 2]
                game.player.rect.x = game.player.position[1] * 40
                game.player.rect.y = game.player.position[0] * 40
                game.player.direction = "player_tank_up"
                game.player.tower_direction = "player_tower_up"
            else:
                game.game_over = True
                game.game_over_result_texture = game.textures["fon_lose"]
                game.update_stats()
            return True

        col = int(bullet_rect.x // 40)
        row = int(bullet_rect.y // 40)

        if 0 <= row < len(field) and 0 <= col < len(field[0]):
            tile = field[row][col]
            if tile and tile["type"] in ["wall", "wall2", "wall3", "wall4"]:
                tile["durability"] -= 1
                if tile["durability"] == 3:
                    tile["type"] = "wall2"
                elif tile["durability"] == 2:
                    tile["type"] = "wall3"
                elif tile["durability"] == 1:
                    tile["type"] = "wall4"
                elif tile["durability"] <= 0:
                    field[row][col] = None
                return True

            if tile and tile["type"] == "unbreakable_wall":
                return True

        if bullet_rect.colliderect(game.field.base_rect):
            game.game_over = True
            game.game_over_result_texture = game.textures["fon_lose"]

            game.game_result = "lose"
            game.lose_reason = "base_destroyed"

            game.current_points -= 15
            game.update_stats()

            game.save_game_session()
            return True

        return False

    def draw(self, screen):  # Отображает пулю на экране.
        if self.active:
            screen.blit(self.texture, (self.x, self.y))
