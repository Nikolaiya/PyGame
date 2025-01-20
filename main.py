import pygame
import random
import time

pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FIELD_WIDTH, FIELD_HEIGHT = 600, 600
CELL_SIZE = 40
FPS = 10

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

TEXTURES = {
    "background": pygame.image.load("fon.png"),
    "wall": pygame.image.load("steni1.png"),
    "wall2": pygame.image.load("steni2.png"),
    "wall3": pygame.image.load("steni3.png"),
    "wall4": pygame.image.load("steni4.png"),
    "unbreakable_wall": pygame.image.load("neraz.png"),
    "grass": pygame.image.load("trava.png"),
    "base": pygame.image.load("gerb.png"),
    "player_tank_up": pygame.image.load("tank1_up.png"),
    "player_tank_down": pygame.image.load("tank1_down.png"),
    "player_tank_left": pygame.image.load("tank1_left.png"),
    "player_tank_right": pygame.image.load("tank1_right.png"),
    "enemy_tank": pygame.image.load("tank2.png"),
    "enemy_icon": pygame.image.load("minitank.png"),
    "life_icon": pygame.image.load("serdce.png"),
    "bullet_up": pygame.image.load("bullet_up.png"),
    "bullet_down": pygame.image.load("bullet_down.png"),
    "bullet_left": pygame.image.load("bullet_left.png"),
    "bullet_right": pygame.image.load("bullet_right.png"),
}

TEXTURES["enemy_icon"] = pygame.transform.scale(TEXTURES["enemy_icon"], (20, 20))
TEXTURES["life_icon"] = pygame.transform.scale(TEXTURES["life_icon"], (20, 20))

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Battle City Remake")

FIRE_COOLDOWN = 0.5


def generate_field(rows, cols):
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
                if field[r][c] and field[r][c]["type"] != "unbreakable_wall":
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

    return field, [base_row, base_col - 2]


def draw_field(field, player_pos, player_direction):
    for row_idx, row in enumerate(field):
        for col_idx, tile in enumerate(row):
            x, y = col_idx * CELL_SIZE, row_idx * CELL_SIZE
            screen.blit(TEXTURES["background"], (x, y))

            if tile and tile["type"] != "grass":
                if tile["type"] in TEXTURES:
                    screen.blit(TEXTURES[tile["type"]], (x, y))

    tank_x, tank_y = player_pos[1] * CELL_SIZE, player_pos[0] * CELL_SIZE
    screen.blit(TEXTURES[player_direction], (tank_x, tank_y))

    for row_idx, row in enumerate(field):
        for col_idx, tile in enumerate(row):
            if tile and tile["type"] == "grass":
                x, y = col_idx * CELL_SIZE, row_idx * CELL_SIZE
                screen.blit(TEXTURES["grass"], (x, y))


def draw_interface(lives, enemy_tanks):
    pygame.draw.rect(screen, BLACK, (FIELD_WIDTH, 0, SCREEN_WIDTH - FIELD_WIDTH, SCREEN_HEIGHT))
    for i in range(enemy_tanks):
        x = FIELD_WIDTH + 10 + (i % 2) * 20
        y = 10 + (i // 2) * 20
        screen.blit(TEXTURES["enemy_icon"], (x, y))
    for i in range(lives):
        x = 10 + i * 20
        y = SCREEN_HEIGHT - 30
        screen.blit(TEXTURES["life_icon"], (x, y))


def main():
    clock = pygame.time.Clock()
    rows, cols = FIELD_HEIGHT // CELL_SIZE, FIELD_WIDTH // CELL_SIZE
    field, player_pos = generate_field(rows, cols)
    lives = 3
    enemy_tanks = 20
    bullet = None
    last_shot_time = 0
    tank_speed = 1
    player_direction = "player_tank_up"

    directions_map = {
        "player_tank_up": (0, -1, "bullet_up"),
        "player_tank_down": (0, 1, "bullet_down"),
        "player_tank_left": (-1, 0, "bullet_left"),
        "player_tank_right": (1, 0, "bullet_right"),
    }

    def handle_bullet_collision(bullet_x, bullet_y):
        nonlocal enemies, enemy_tanks
        col = bullet_x // CELL_SIZE
        row = bullet_y // CELL_SIZE

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

            elif tile and tile["type"] == "unbreakable_wall":
                return True

            for enemy in enemies:
                if enemy["row"] == row and enemy["col"] == col:
                    enemies.remove(enemy)
                    enemy_tanks -= 1
                    if enemy_tanks > 0 and len(enemies) == 0:
                        spawn_enemy()

                    return True

        return False

    enemies = []
    last_spawn_time = time.time()

    def spawn_enemy():
        nonlocal enemies
        if len(enemies) < 5 and enemy_tanks > 0:
            while True:
                row = random.randint(0, 2)
                col = random.randint(0, cols - 1)
                if field[row][col] is None and [row, col] != player_pos:
                    enemies.append({"row": row, "col": col})
                    break

    spawn_enemy()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                current_time = time.time()
                if bullet is None and current_time - last_shot_time >= FIRE_COOLDOWN:
                    tank_x, tank_y = player_pos[1] * CELL_SIZE, player_pos[0] * CELL_SIZE
                    direction = directions_map[player_direction]
                    bullet = {
                        "x": tank_x + CELL_SIZE // 2,
                        "y": tank_y + CELL_SIZE // 2,
                        "direction": direction[:2],
                        "texture": direction[2],
                    }
                    last_shot_time = current_time

        if enemy_tanks <= 0:
            running = False

        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_w]:
            dy = -tank_speed
            player_direction = "player_tank_up"
        elif keys[pygame.K_a]:
            dx = -tank_speed
            player_direction = "player_tank_left"
        elif keys[pygame.K_s]:
            dy = tank_speed
            player_direction = "player_tank_down"
        elif keys[pygame.K_d]:
            dx = tank_speed
            player_direction = "player_tank_right"

        new_pos = [player_pos[0] + dy, player_pos[1] + dx]
        if 0 <= new_pos[0] < rows and 0 <= new_pos[1] < cols:
            tile = field[new_pos[0]][new_pos[1]]
            if not tile or tile["type"] in ["grass", "base"]:
                collision_with_enemy = False
                for enemy in enemies:
                    if enemy["row"] == new_pos[0] and enemy["col"] == new_pos[1]:
                        collision_with_enemy = True
                        break

                if not collision_with_enemy:
                    player_pos = new_pos

        if bullet:
            bullet["x"] += bullet["direction"][0] * 10
            bullet["y"] += bullet["direction"][1] * 10
            if handle_bullet_collision(bullet["x"], bullet["y"]):
                bullet = None
            elif bullet["x"] < 0 or bullet["x"] > FIELD_WIDTH or bullet["y"] < 0 or bullet["y"] > FIELD_HEIGHT:
                bullet = None

        if time.time() - last_spawn_time >= 10:
            spawn_enemy()
            last_spawn_time = time.time()

        screen.fill(WHITE)
        draw_field(field, player_pos, player_direction)
        draw_interface(lives, enemy_tanks)

        if bullet:
            screen.blit(TEXTURES[bullet["texture"]], (bullet["x"], bullet["y"]))

        for enemy in enemies:
            x, y = enemy["col"] * CELL_SIZE, enemy["row"] * CELL_SIZE
            screen.blit(TEXTURES["enemy_tank"], (x, y))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
