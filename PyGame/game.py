import time
import sqlite3

import pygame

from field import Field
from player import Player
from enemy import Enemy
from database import Database


class Game:  # Основной класс игры.
    def __init__(self):  # Инициализирует игру, создает объекты поля, игрока, врагов и базы данных.
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Battle City Remake")
        self.clock = pygame.time.Clock()
        self.running = True
        self.fps = 10
        self.field_width = 600
        self.field_height = 600
        self.cell_size = 40
        self.field = None
        self.player = None
        self.enemies = []
        self.player_bullets = []
        self.enemy_bullets = {}
        self.game_over = False
        self.game_over_screen_active = False
        self.overlay_y = -600
        self.lives = 3
        self.max_enemy_on_field = 5
        self.last_spawn_time = time.time()
        self.enemy_tanks = 20
        self.enemy_speed = 3.0
        self.next_level_enemy_tanks = 1
        self.game_over_result_texture = None
        self.textures = self.load_textures()
        self.init_game()
        self.enemies_killed = 0
        self.lives_lost = 0
        self.lost_due_to_enemy = 0
        self.lost_due_to_water = 0
        self.game_result = None
        self.lose_reason = None
        self.stats_updated = False
        self.total_points = 0
        self.current_points = 0

        self.db = Database()
        self.total_points = self.db.load_total_points()

    def load_total_points(self):  # Загружает общее количество очков из базы данных.
        conn = sqlite3.connect('game_stats.db')
        cursor = conn.cursor()
        cursor.execute('SELECT всего_очков FROM overall_stats')
        result = cursor.fetchone()
        if result:
            self.total_points = result[0]
        conn.close()

    def save_game_session(self):  # Сохраняет статистику игровой сессии в базу данных.
        self.db.save_game_session(self.enemies_killed, self.lives_lost, self.lost_due_to_enemy, self.lost_due_to_water,
                                  self.game_result, self.lose_reason)
        self.db.update_total_points(self.total_points)

    def update_stats(self):  # Обновляет статистику игры при её завершении.
        if self.game_over and not self.stats_updated:

            if self.lives <= 0:
                self.game_result = "lose"
                self.lose_reason = "no_lives"
                self.current_points -= 15
            elif self.enemy_tanks == 0:
                self.game_result = "win"
                self.current_points += 20

            if self.current_points < 0:
                self.total_points += self.current_points
            else:
                self.total_points += self.current_points

            if self.total_points < 0:
                self.total_points = 0

            self.save_game_session()
            self.stats_updated = True

    @staticmethod
    def load_textures():  # Загружает текстуры для игры.
        return {
            "background": pygame.image.load("textures/fon.png"),
            "fon_lose": pygame.image.load("textures/game_over_lose.png"),
            "fon_win": pygame.image.load("textures/game_over_win.png"),
            "exit": pygame.image.load("textures/quit.png"),
            "again": pygame.image.load("textures/again.png"),
            "continue": pygame.image.load("textures/cont.png"),
        }

    def init_game(self):  # Инициализирует игровое поле и игрока.
        self.field = Field()
        self.player = Player(self.field)

    def handle_events(self):  # Обработка событий.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.player.shoot(self.player_bullets)

    def update(self):  # Обновляет состояние игры.
        self.player.move(self.enemies)

        if self.player.check_water_collision():
            self.lives -= 1
            self.lives_lost += 1
            self.lost_due_to_water += 1
            self.current_points -= 5
            self.update_stats()
            if self.current_points < 0:
                self.current_points = 0
            if self.lives > 0:
                self.player.position = [self.field.base_position[0], self.field.base_position[1] - 2]
                self.player.rect.x = self.player.position[1] * 40
                self.player.rect.y = self.player.position[0] * 40
                self.player.direction = "player_tank_up"
                self.player.tower_direction = "player_tower_up"
                self.current_points -= 5
            else:
                self.game_over = True
                self.game_over_result_texture = self.textures["fon_lose"]
                self.update_stats()

        for enemy in self.enemies:
            enemy.move(self.enemies, self.player.rect)
            enemy.fire(self.enemy_bullets.setdefault(id(enemy), []))

        self.update_bullets()
        self.spawn_enemies()
        self.check_game_over()

        if time.time() - self.field.last_water_update >= 0.3:
            self.field.current_water_index = (self.field.current_water_index + 1) % len(self.field.water_textures)
            self.field.textures["water"] = pygame.image.load(self.field.water_textures[self.field.current_water_index])
            self.field.last_water_update = time.time()

    def update_bullets(self):  # Обновляет состояние пуль игрока и врагов.
        self.player_bullets = [bullet for bullet in self.player_bullets if
                               not bullet.move(self.field.grid, self.enemies, self.player.rect, self)]
        self.player.update_bullet_status(self.player_bullets)

        for enemy_id, bullets in self.enemy_bullets.items():
            if isinstance(bullets, list):
                new_bullets = []
                for bullet in bullets:
                    if not bullet.move(self.field.grid, self.enemies, self.player.rect, self):
                        new_bullets.append(bullet)
                self.enemy_bullets[enemy_id] = new_bullets

                if not new_bullets:
                    for enemy in self.enemies:
                        if id(enemy) == enemy_id:
                            enemy.bullet_active = False

    def spawn_enemies(self):  # Появление врагов на поле.
        if len(self.enemies) == 0 and self.enemy_tanks > 0:
            new_enemy = Enemy(self.field)
            position, rect = new_enemy.spawn_enemy(self.enemies, self.player.rect)

            if position and rect:
                new_enemy.position = position
                new_enemy.rect = rect
                self.enemies.append(new_enemy)

            self.last_spawn_time = time.time()
            return

        if len(self.enemies) < self.max_enemy_on_field and len(self.enemies) < self.enemy_tanks:
            if self.last_spawn_time is None:
                self.last_spawn_time = time.time()

            if time.time() - self.last_spawn_time >= 5:
                new_enemy = Enemy(self.field)
                position, rect = new_enemy.spawn_enemy(self.enemies, self.player.rect)

                if position and rect:
                    new_enemy.position = position
                    new_enemy.rect = rect
                    self.enemies.append(new_enemy)

                self.last_spawn_time = None

    def check_game_over(self):  # Проверяет условия завершения игры,
        if self.lives <= 0:
            self.game_over = True
            self.game_over_result_texture = self.textures["fon_lose"]
            self.update_stats()
        elif self.enemy_tanks == 0:
            self.game_over = True
            self.game_over_result_texture = self.textures["fon_win"]
            self.update_stats()
        else:
            all_enemy_bullets = []
            for bullets in self.enemy_bullets.values():
                all_enemy_bullets.extend(bullets)

    def render(self):  # Отрисовка всех объектов на экране.
        self.screen.fill((255, 255, 255))

        self.field.draw(self.screen)

        self.player.draw(self.screen)

        for enemy in self.enemies:
            enemy.draw(self.screen)

        for bullet in self.player_bullets:
            bullet.draw(self.screen)
        for bullets in self.enemy_bullets.values():
            for bullet in bullets:
                bullet.draw(self.screen)

        self.field.draw_interface(self.screen, self.lives, self.enemy_tanks, self.enemies_killed, self.lives_lost,
                                  self.total_points, self.current_points, self.overlay_y)

        self.field.draw_grass(self.screen)

        pygame.display.flip()

    def full_restart(self):  # Полностью перезапускает игру.
        self.overlay_y = -600
        self.game_over = False
        self.running = True
        self.stats_updated = False

        self.field = self.field.generate_field(self.field_height // self.cell_size,
                                               self.field_width // self.cell_size)

        self.lives = 3
        self.enemies = []
        self.player_bullets = []
        self.enemy_bullets = {}
        self.player.direction = "player_tank_up"
        self.player.tower_direction = "player_tower_up"

        self.current_points = 0
        self.enemies_killed = 0
        self.lives_lost = 0

        self.last_spawn_time = time.time()
        self.init_game()

    def game_over_screen(self):  # Отображает экран завершения игры.

        while self.overlay_y < 0:
            self.overlay_y += 2
            self.render_game_over()
            pygame.time.delay(10)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return

        self.overlay_y = 0
        self.handle_game_over_events()

    def render_game_over(self):  # Отображает экран завершения игры.
        self.screen.blit(self.game_over_result_texture, (0, self.overlay_y))

        self.field.draw_interface(self.screen, self.lives, self.enemy_tanks, self.enemies_killed, self.lives_lost,
                                  self.total_points, self.current_points, self.overlay_y)

        if self.overlay_y == 0:
            if self.enemy_tanks == 0:
                self.screen.blit(self.textures["continue"], (615, 180))

            self.screen.blit(self.textures["again"], (615, 240))
            self.screen.blit(self.textures["exit"], (615, 300))

        pygame.display.flip()

    def handle_game_over_events(self):  # Обрабатывает события на экране завершения игры.
        while True:
            self.render_game_over()

            mouse_x, mouse_y = pygame.mouse.get_pos()
            click = pygame.mouse.get_pressed()

            btn_continue = pygame.Rect(615, 180, 100, 40)
            btn_again = pygame.Rect(615, 240, 100, 40)
            btn_exit = pygame.Rect(615, 300, 100, 40)

            if click[0]:
                if self.enemy_tanks == 0 and btn_continue.collidepoint(mouse_x, mouse_y):
                    self.next_level_enemy_tanks += 1
                    self.enemy_tanks = self.next_level_enemy_tanks
                    self.enemy_speed += 0.1
                    self.reset_game_state()
                    self.init_game()
                    return

                elif btn_again.collidepoint(mouse_x, mouse_y):
                    self.enemy_tanks = 1
                    self.next_level_enemy_tanks = 1
                    self.enemy_speed = 3.0
                    self.full_restart()
                    return

                elif btn_exit.collidepoint(mouse_x, mouse_y):
                    self.running = False
                    return

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return

    def reset_game_state(self):  # Сбрасывает состояние игры для нового уровня.
        self.overlay_y = -600
        self.game_over = False
        self.running = True
        self.player_bullets = []
        self.enemy_bullets = {}
        self.enemies = []
        self.lives = 3

        self.enemies_killed = 0
        self.lives_lost = 0
        self.current_points = 0
        self.stats_updated = False

    def run(self):  # Основной игровой цикл, управляющий обновлением и отображением.
        while self.running:
            self.handle_events()
            if not self.game_over:
                self.update()
                self.render()
            else:
                self.game_over_screen()
            self.clock.tick(self.fps)
        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()
