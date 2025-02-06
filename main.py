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
    "background": pygame.image.load("textures/fon.png"),
    "wall": pygame.image.load("textures/wall1.png"),
    "wall2": pygame.image.load("textures/wall2.png"),
    "wall3": pygame.image.load("textures/wall3.png"),
    "wall4": pygame.image.load("textures/wall4.png"),
    "unbreakable_wall": pygame.image.load("textures/unbreakable.png"),
    "grass": pygame.image.load("textures/grass.png"),
    "base": pygame.image.load("textures/emblem.png"),
    "water": pygame.image.load("textures/water1.png"),
    "water2": pygame.image.load("textures/water2.png"),
    "water3": pygame.image.load("textures/water3.png"),
    "player_tower_up": pygame.image.load("textures/tower_up.png"),
    "player_tower_down": pygame.image.load("textures/tower_down.png"),
    "player_tower_left": pygame.image.load("textures/tower_left.png"),
    "player_tower_right": pygame.image.load("textures/tower_right.png"),
    "player_tank_up": pygame.image.load("textures/tank1_up.png"),
    "player_tank_down": pygame.image.load("textures/tank1_down.png"),
    "player_tank_left": pygame.image.load("textures/tank1_left.png"),
    "player_tank_right": pygame.image.load("textures/tank1_right.png"),
    "enemy_tank_up": pygame.image.load("textures/tank2_up.png"),
    "enemy_tank_down": pygame.image.load("textures/tank2_down.png"),
    "enemy_tank_left": pygame.image.load("textures/tank2_left.png"),
    "enemy_tank_right": pygame.image.load("textures/tank2_right.png"),
    "player_tank_up2": pygame.image.load("textures/tank1_up2.png"),
    "player_tank_down2": pygame.image.load("textures/tank1_down2.png"),
    "player_tank_left2": pygame.image.load("textures/tank1_left2.png"),
    "player_tank_right2": pygame.image.load("textures/tank1_right2.png"),
    "enemy_tank_up2": pygame.image.load("textures/tank2_up2.png"),
    "enemy_tank_down2": pygame.image.load("textures/tank2_down2.png"),
    "enemy_tank_left2": pygame.image.load("textures/tank2_left2.png"),
    "enemy_tank_right2": pygame.image.load("textures/tank2_right2.png"),
    "enemy_icon": pygame.image.load("textures/mini_tank.png"),
    "life_icon": pygame.image.load("textures/life.png"),
    "bullet_up": pygame.image.load("textures/bullet_up.png"),
    "bullet_down": pygame.image.load("textures/bullet_down.png"),
    "bullet_left": pygame.image.load("textures/bullet_left.png"),
    "bullet_right": pygame.image.load("textures/bullet_right.png"),
    "enemy_bullet_up": pygame.image.load("textures/enemy_bullet_up.png"),
    "enemy_bullet_down": pygame.image.load("textures/enemy_bullet_down.png"),
    "enemy_bullet_left": pygame.image.load("textures/enemy_bullet_left.png"),
    "enemy_bullet_right": pygame.image.load("textures/enemy_bullet_right.png"),
    "fon_lose": pygame.image.load("textures/game_over_lose.png"),
    "fon_win": pygame.image.load("textures/game_over_win.png"),
    "exit": pygame.image.load("textures/quit.png"),
    "again": pygame.image.load("textures/again.png"),
    "continue": pygame.image.load("textures/cont.png"),
}

TEXTURES["enemy_icon"] = pygame.transform.scale(TEXTURES["enemy_icon"], (20, 20))
TEXTURES["life_icon"] = pygame.transform.scale(TEXTURES["life_icon"], (20, 20))

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Battle City Remake")


def generate_field(rows, cols):
    import random

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

    return field, [base_row, base_col - 2]


def draw_field(field, player_pos, player_direction, tower_direction, enemies):
    for row_idx, row in enumerate(field):
        for col_idx, tile in enumerate(row):
            x, y = col_idx * CELL_SIZE, row_idx * CELL_SIZE
            screen.blit(TEXTURES["background"], (x, y))

    for row_idx, row in enumerate(field):
        for col_idx, tile in enumerate(row):
            if tile and tile["type"] and tile["type"] != "grass":
                x, y = col_idx * CELL_SIZE, row_idx * CELL_SIZE
                screen.blit(TEXTURES[tile["type"]], (x, y))


    tank_x, tank_y = player_pos[1] * CELL_SIZE, player_pos[0] * CELL_SIZE
    screen.blit(TEXTURES[player_direction], (tank_x, tank_y))

    tower_x = tank_x + CELL_SIZE // 45
    tower_y = tank_y + CELL_SIZE // 45
    screen.blit(TEXTURES[tower_direction], (tower_x, tower_y))

    for enemy in enemies:
        enemy_texture = TEXTURES[enemy["texture"]].copy()
        if is_in_grass(enemy["x"], enemy["y"], field):
            enemy_texture.set_alpha(150)
        screen.blit(enemy_texture, (enemy["x"], enemy["y"]))



def draw_interface(lives, enemy_tanks):
    pygame.draw.rect(screen, BLACK, (FIELD_WIDTH, 0, SCREEN_WIDTH - FIELD_WIDTH, SCREEN_HEIGHT))

    for i in range(enemy_tanks):
        x = FIELD_WIDTH + 10 + (i % 2) * 20
        y = 10 + (i // 2) * 20
        screen.blit(TEXTURES["enemy_icon"], (x, y))

    for i in range(lives):
        x = 610 + i * 20
        y = SCREEN_HEIGHT - 30
        screen.blit(TEXTURES["life_icon"], (x, y))


def spawn_enemy(field, enemies, player_pos):
    directions = {
        (-1, 0): "enemy_tank_left",
        (1, 0): "enemy_tank_right",
        (0, -1): "enemy_tank_up",
        (0, 1): "enemy_tank_down",
    }

    max_attempts = 100
    attempts = 0

    while attempts < max_attempts:
        row = random.randint(0, 2)
        col = random.randint(1, len(field[0]) - 2)

        enemy_rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)

        if field[row][col] and field[row][col]["type"] in ["water", "water2", "water3", "unbreakable_wall", "wall", "wall2", "wall3",
                                                           "wall4"]:
            attempts += 1
            continue

        if any(enemy_rect.colliderect(pygame.Rect(e["x"], e["y"], CELL_SIZE, CELL_SIZE)) for e in enemies):
            attempts += 1
            continue

        valid_spawn = True
        for r in range(max(0, row - 1), min(len(field), row + 2)):
            for c in range(max(0, col - 1), min(len(field[0]), col + 2)):
                if field[r][c] and field[r][c]["type"] in ["water", "water2", "water3", "unbreakable_wall", "wall", "wall2", "wall3",
                                                           "wall4"]:
                    valid_spawn = False

        if not valid_spawn:
            attempts += 1
            continue

        player_x, player_y = player_pos[1] * CELL_SIZE, player_pos[0] * CELL_SIZE
        player_rect = pygame.Rect(player_x, player_y, CELL_SIZE, CELL_SIZE)
        if enemy_rect.colliderect(player_rect):
            attempts += 1
            continue

        direction = random.choice(list(directions.keys()))
        return {
            "row": row,
            "col": col,
            "direction": direction,
            "texture": directions[direction],
            "x": col * CELL_SIZE,
            "y": row * CELL_SIZE,
            "speed": 3,
            "move_timer": random.uniform(2, 5),
            "change_dir_timer": time.time() + 5,
        }

    return None


def move_enemy(enemy, field, enemies, player_pos, emblem_rect, delta_time):
    directions = {
        (-1, 0): "enemy_tank_left",
        (1, 0): "enemy_tank_right",
        (0, -1): "enemy_tank_up",
        (0, 1): "enemy_tank_down",
    }

    current_time = time.time()

    if "direction" not in enemy:
        enemy["direction"] = random.choice(list(directions.keys()))

    if time.time() % 0.2 < 0.1:
        enemy["texture"] = directions[enemy["direction"]] + "2"
    else:
        enemy["texture"] = directions[enemy["direction"]]

    if enemy.get("stuck_time") and current_time >= enemy["stuck_time"]:
        enemy["direction"] = random.choice(list(directions.keys()))
        enemy["texture"] = directions[enemy["direction"]]
        if time.time() % 0.2 < 0.1:
            enemy["texture"] += "2"
        enemy["stuck_time"] = None
        enemy["change_dir_timer"] = current_time + 5

    if current_time >= enemy.get("change_dir_timer", 0):
        enemy["direction"] = random.choice(list(directions.keys()))
        enemy["texture"] = directions[enemy["direction"]]
        if time.time() % 0.2 < 0.1:
            enemy["texture"] += "2"
        enemy["change_dir_timer"] = current_time + 5

    dx, dy = enemy["direction"]
    enemy_in_grass = is_in_grass(enemy["x"], enemy["y"], field)

    current_enemy_speed = 1.5 if enemy_in_grass else enemy["speed"]

    move_distance = current_enemy_speed * delta_time

    new_x = enemy["x"] + dx * move_distance
    new_y = enemy["y"] + dy * move_distance

    if not is_enemy_collision(enemy, new_x, new_y, enemies, player_pos, field, emblem_rect):
        enemy["x"], enemy["y"] = new_x, new_y
        enemy["row"] = int(enemy["y"] // CELL_SIZE)
        enemy["col"] = int(enemy["x"] // CELL_SIZE)
        enemy["stuck_time"] = None
    else:
        if enemy.get("stuck_time") is None:
            enemy["stuck_time"] = current_time + 1


def is_enemy_collision(enemy, enemy_x, enemy_y, enemies, player_pos, field, emblem_rect, tolerance=1):
    enemy_rect = pygame.Rect(enemy_x, enemy_y, CELL_SIZE, CELL_SIZE)

    if (enemy_x < 0 or enemy_x >= FIELD_WIDTH - CELL_SIZE or
            enemy_y < 0 or enemy_y >= FIELD_HEIGHT - CELL_SIZE):
        return True

    for other_enemy in enemies:
        if other_enemy is enemy:
            continue
        other_rect = pygame.Rect(other_enemy["x"], other_enemy["y"], CELL_SIZE, CELL_SIZE)
        if enemy_rect.colliderect(other_rect):
            return True

    player_x, player_y = player_pos[1] * CELL_SIZE, player_pos[0] * CELL_SIZE
    player_rect = pygame.Rect(player_x, player_y, CELL_SIZE, CELL_SIZE)
    if enemy_rect.colliderect(player_rect):
        return True

    if enemy_rect.colliderect(emblem_rect):
        return True

    for row_idx, row in enumerate(field):
        for col_idx, tile in enumerate(row):
            if tile and tile["type"] not in ["grass", "base"]:
                tile_rect = pygame.Rect(col_idx * CELL_SIZE, row_idx * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                if enemy_rect.colliderect(tile_rect):
                    if (abs(enemy_rect.left - tile_rect.right) <= tolerance or
                            abs(enemy_rect.right - tile_rect.left) <= tolerance or
                            abs(enemy_rect.top - tile_rect.bottom) <= tolerance or
                            abs(enemy_rect.bottom - tile_rect.top) <= tolerance):
                        continue
                    return True

    return False


def is_in_grass(x, y, field):
    tank_rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)

    for row in range(len(field)):
        for col in range(len(field[row])):
            tile = field[row][col]
            if tile and tile["type"] == "grass":
                grass_rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                if tank_rect.colliderect(grass_rect):
                    return True
    return False


def main():
    running = True
    clock = pygame.time.Clock()
    rows, cols = FIELD_HEIGHT // CELL_SIZE, FIELD_WIDTH // CELL_SIZE
    field, player_pos = generate_field(rows, cols)
    lives = 3
    max_enemy_on_field = 3
    enemies = []
    enemy_spawn_timer = 2
    last_spawn_time = time.time()
    tank_speed = 10
    player_direction = "player_tank_up"
    tolerance = 1
    game_over = False
    enemy_bullets = {}
    enemy_next_shot = {}
    player_bullets = []
    animation_state = False
    tower_direction = "player_tower_up"

    enemy_tanks = 1
    base_enemy_speed = 3.0

    current_enemy_tanks = enemy_tanks
    current_enemy_speed = base_enemy_speed

    game_over_screen_active = False
    game_over_result_texture = None
    overlay_y = -FIELD_HEIGHT

    directions_map = {
        "player_tower_up": (0, -1, "bullet_up"),
        "player_tower_down": (0, 1, "bullet_down"),
        "player_tower_left": (-1, 0, "bullet_left"),
        "player_tower_right": (1, 0, "bullet_right"),
    }

    water_textures = ["textures/water1.png", "textures/water2.png", "textures/water3.png"]
    current_water_index = 0
    last_water_update = time.time()

    base_row, base_col = rows - 2, cols // 2
    emblem_rect = pygame.Rect(base_col * CELL_SIZE, base_row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
    player_rect = pygame.Rect(player_pos[1] * CELL_SIZE, player_pos[0] * CELL_SIZE, CELL_SIZE, CELL_SIZE)

    def enemy_fire(enemy):
        bullet_x = enemy["x"] + CELL_SIZE // 2
        bullet_y = enemy["y"] + CELL_SIZE // 2

        direction_map = {
            (0, -1): ("enemy_bullet_up", (0, -1)),
            (0, 1): ("enemy_bullet_down", (0, 1)),
            (-1, 0): ("enemy_bullet_left", (-1, 0)),
            (1, 0): ("enemy_bullet_right", (1, 0)),
        }

        bullet_texture, bullet_direction = direction_map.get(enemy["direction"], ("enemy_bullet_up", (0, -1)))

        return {
            "x": bullet_x,
            "y": bullet_y,
            "direction": bullet_direction,
            "shooter": "enemy",
            "texture": bullet_texture
        }

    def move_bullet(bullet, emblem_rect, player_rect, enemies, player_pos, field):
        step_x, step_y = bullet["direction"]

        for _ in range(10):
            bullet["x"] += step_x
            bullet["y"] += step_y

            if handle_bullet_collision(bullet["x"], bullet["y"], bullet, emblem_rect, player_rect, enemies, player_pos,
                                       field):
                return True

        return False

    def update_enemy_shooting(enemies, enemy_bullets, enemy_next_shot, emblem_rect, player_rect, player_pos):
        current_time = time.time()

        for enemy in enemies:
            enemy_id = id(enemy)

            if enemy_id not in enemy_next_shot:
                enemy_next_shot[enemy_id] = current_time

            if enemy_id not in enemy_bullets:
                enemy_bullets[enemy_id] = []

            if current_time >= enemy_next_shot[enemy_id]:
                new_bullet = enemy_fire(enemy)
                enemy_bullets[enemy_id].append(new_bullet)
                enemy_next_shot[enemy_id] = current_time + 2.0

        for enemy_id in list(enemy_bullets.keys()):
            enemy_bullets[enemy_id] = [bullet for bullet in enemy_bullets[enemy_id]
                                       if not move_bullet(bullet, emblem_rect, player_rect, enemies, player_pos, field)]

    def handle_bullet_collision(bullet_x, bullet_y, bullet, emblem_rect, player_rect, enemies, player_pos, field):
        nonlocal lives, enemy_tanks, player_direction, tower_direction, game_over, game_over_result_texture

        if bullet is None:
            return False

        bullet_rect = pygame.Rect(bullet_x, bullet_y, CELL_SIZE // 2, CELL_SIZE // 2)

        if bullet.get("shooter") == "enemy":
            if bullet_rect.colliderect(player_rect):
                lives -= 1

                player_pos[0] = rows - 2
                player_pos[1] = (cols // 2) - 2

                player_rect.x = player_pos[1] * CELL_SIZE
                player_rect.y = player_pos[0] * CELL_SIZE

                player_direction = "player_tank_up"
                tower_direction = "player_tower_up"

                return True

        for enemy in enemies[:]:
            enemy_rect = pygame.Rect(enemy["x"], enemy["y"], CELL_SIZE, CELL_SIZE)
            if bullet.get("shooter") == "player" and bullet_rect.colliderect(enemy_rect):
                enemies.remove(enemy)
                enemy_tanks -= 1
                return True

        col = int(bullet_x // CELL_SIZE)
        row = int(bullet_y // CELL_SIZE)

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

            if bullet_rect.colliderect(emblem_rect):
                game_over = True
                game_over_result_texture = TEXTURES["fon_lose"]

        return False

    def is_collision(new_pos, enemies, emblem_rect):
        tank_x = new_pos[1] * CELL_SIZE
        tank_y = new_pos[0] * CELL_SIZE
        tank_rect = pygame.Rect(tank_x, tank_y, CELL_SIZE, CELL_SIZE)

        for enemy in enemies:
            enemy_x = enemy["x"]
            enemy_y = enemy["y"]
            enemy_rect = pygame.Rect(enemy_x, enemy_y, CELL_SIZE, CELL_SIZE)
            if tank_rect.colliderect(enemy_rect):
                return True

        for row_idx, row in enumerate(field):
            for col_idx, tile in enumerate(row):
                if tile and tile["type"] not in ["grass", "base", "water"]:
                    tile_rect = pygame.Rect(
                        col_idx * CELL_SIZE, row_idx * CELL_SIZE, CELL_SIZE, CELL_SIZE
                    )
                    if tank_rect.colliderect(tile_rect):
                        if abs(tank_rect.left - tile_rect.right) <= tolerance or \
                                abs(tank_rect.right - tile_rect.left) <= tolerance or \
                                abs(tank_rect.top - tile_rect.bottom) <= tolerance or \
                                abs(tank_rect.bottom - tile_rect.top) <= tolerance:
                            continue
                        return True

        if tank_rect.colliderect(emblem_rect):
            return True

        return False

    def check_water_collision(player_pos, field):
        tank_rect = pygame.Rect(player_pos[1] * CELL_SIZE, player_pos[0] * CELL_SIZE, CELL_SIZE, CELL_SIZE)

        overlap_threshold = CELL_SIZE * 0.5

        for row_idx, row in enumerate(field):
            for col_idx, tile in enumerate(row):
                if tile and tile["type"] == "water":
                    water_rect = pygame.Rect(col_idx * CELL_SIZE, row_idx * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                    if tank_rect.colliderect(water_rect):
                        intersection = tank_rect.clip(water_rect)
                        if intersection.width * intersection.height >= overlap_threshold * overlap_threshold:
                            return True
        return False

    def reset_game_state():
        nonlocal game_over, game_over_screen_active, overlay_y, enemies, enemy_tanks, lives, player_pos, player_direction, tower_direction, player_bullets, enemy_bullets, enemy_next_shot, last_spawn_time

        game_over = False
        game_over_screen_active = False
        overlay_y = -FIELD_HEIGHT
        enemies.clear()
        enemy_tanks = current_enemy_tanks
        lives = 3
        player_pos = [rows - 2, (cols // 2) - 2]
        player_direction = "player_tank_up"
        tower_direction = "player_tower_up"
        player_bullets = []
        enemy_bullets = {}
        enemy_next_shot = {}
        last_spawn_time = time.time()

        field, player_pos = generate_field(rows, cols)

    while running:
        if game_over and not game_over_screen_active:
            game_over_screen_active = True
            if enemy_tanks == 0:
                game_over_result_texture = TEXTURES["fon_win"]
            else:
                game_over_result_texture = TEXTURES["fon_lose"]
            overlay_y = -FIELD_HEIGHT

        if game_over_screen_active:
            if overlay_y < 0:
                overlay_y += CELL_SIZE // 20
                if overlay_y >= 0:
                    overlay_y = 0

            screen.fill(BLACK)
            draw_field(field, player_pos, player_direction, tower_direction, enemies)
            draw_interface(lives, enemy_tanks)
            screen.blit(game_over_result_texture, (0, overlay_y))

            if overlay_y == 0:
                if enemy_tanks == 0:
                    screen.blit(TEXTURES["continue"], (SCREEN_WIDTH // 2 + 215, SCREEN_HEIGHT // 2 - 60))

                screen.blit(TEXTURES["again"], (SCREEN_WIDTH // 2 + 215, SCREEN_HEIGHT // 2))
                screen.blit(TEXTURES["exit"], (SCREEN_WIDTH // 2 + 215, SCREEN_HEIGHT // 2 + 60))

                mouse_x, mouse_y = pygame.mouse.get_pos()
                click = pygame.mouse.get_pressed()

                btn_continue = pygame.Rect(SCREEN_WIDTH // 2 + 215, SCREEN_HEIGHT // 2 - 60, 100, 40)
                btn_again = pygame.Rect(SCREEN_WIDTH // 2 + 215, SCREEN_HEIGHT // 2, 100, 40)
                btn_exit = pygame.Rect(SCREEN_WIDTH // 2 + 215, SCREEN_HEIGHT // 2 + 60, 100, 40)

                if click[0]:
                    if btn_continue.collidepoint(mouse_x, mouse_y):
                        current_enemy_tanks += 1
                        current_enemy_speed += 0.1
                        reset_game_state()

                    elif btn_again.collidepoint(mouse_x, mouse_y):
                        current_enemy_tanks = enemy_tanks
                        current_enemy_speed = base_enemy_speed
                        main()

                    elif btn_exit.collidepoint(mouse_x, mouse_y):
                        pygame.quit()
                        exit()

            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            continue

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if len(player_bullets) > 0:
                    continue

                tank_x = int(player_pos[1] * CELL_SIZE)
                tank_y = int(player_pos[0] * CELL_SIZE)
                base_direction = tower_direction.replace("2", "")

                new_bullet = {
                    "x": tank_x + CELL_SIZE // 2,
                    "y": tank_y + CELL_SIZE // 2,
                    "direction": directions_map[base_direction][:2],
                    "texture": directions_map[base_direction][2],
                    "shooter": "player",
                }
                player_bullets.append(new_bullet)

        if time.time() - last_water_update >= 0.3:
            current_water_index = (current_water_index + 1) % len(water_textures)
            TEXTURES["water"] = pygame.image.load(water_textures[current_water_index])
            last_water_update = time.time()

        keys = pygame.key.get_pressed()
        dx, dy = 0, 0

        player_in_grass = is_in_grass(player_pos[1] * CELL_SIZE, player_pos[0] * CELL_SIZE, field)

        current_tank_speed = 1.5 if player_in_grass else tank_speed

        if keys[pygame.K_w]:
            dy = -current_tank_speed
            animation_state = not animation_state
            player_direction = "player_tank_up2" if animation_state else "player_tank_up"

        elif keys[pygame.K_a]:
            dx = -current_tank_speed
            animation_state = not animation_state
            player_direction = "player_tank_left2" if animation_state else "player_tank_left"

        elif keys[pygame.K_s]:
            dy = current_tank_speed
            animation_state = not animation_state
            player_direction = "player_tank_down2" if animation_state else "player_tank_down"

        elif keys[pygame.K_d]:
            dx = current_tank_speed
            animation_state = not animation_state
            player_direction = "player_tank_right2" if animation_state else "player_tank_right"

        if keys[pygame.K_UP]:
            tower_direction = "player_tower_up"
        elif keys[pygame.K_DOWN]:
            tower_direction = "player_tower_down"
        elif keys[pygame.K_LEFT]:
            tower_direction = "player_tower_left"
        elif keys[pygame.K_RIGHT]:
            tower_direction = "player_tower_right"

        new_pos = [player_pos[0] + dy / CELL_SIZE, player_pos[1] + dx / CELL_SIZE]
        if not is_collision(new_pos, enemies, emblem_rect):
            player_pos[0] += dy / CELL_SIZE
            player_pos[1] += dx / CELL_SIZE

        update_enemy_shooting(enemies, enemy_bullets, enemy_next_shot, emblem_rect, player_rect, player_pos)

        current_time = time.time()
        if len(enemies) < max_enemy_on_field and (current_time - last_spawn_time >= enemy_spawn_timer):
            spawn_success = False
            attempts = 0
            while not spawn_success and attempts < 100:
                row = random.randint(1, 3)
                col = random.randint(1, cols - 2)

                if field[row][col] is None or \
                        (field[row][col]["type"] == "grass") or \
                        (field[row][col]["type"] == "water"):
                    enemies.append({
                        "row": row,
                        "col": col,
                        "x": col * CELL_SIZE,
                        "y": row * CELL_SIZE,
                        "speed": current_enemy_speed,
                    })

                    last_spawn_time = current_time
                    spawn_success = True
                attempts += 1

        for enemy in enemies:
            move_enemy(enemy, field, enemies, player_pos, emblem_rect, delta_time=1)

        player_rect.x = player_pos[1] * CELL_SIZE
        player_rect.y = player_pos[0] * CELL_SIZE

        player_bullets = [bullet for bullet in player_bullets
                          if not move_bullet(bullet, emblem_rect, player_rect, enemies, player_pos, field)]

        enemy_bullets = {enemy_id: [bullet for bullet in bullets
                                    if not move_bullet(bullet, emblem_rect, player_rect, enemies, player_pos, field)]
                         for enemy_id, bullets in enemy_bullets.items()}

        screen.fill(WHITE)
        draw_field(field, player_pos, player_direction, tower_direction, enemies)
        draw_interface(lives, enemy_tanks)

        for bullets in enemy_bullets.values():
            for bullet in bullets:
                screen.blit(TEXTURES[bullet["texture"]], (bullet["x"], bullet["y"]))

        for bullet in player_bullets:
            screen.blit(TEXTURES[bullet["texture"]], (bullet["x"], bullet["y"]))

        for enemy in enemies:
            screen.blit(TEXTURES[enemy["texture"]], (enemy["x"], enemy["y"]))

        # Отрисовка травы после врагов
        for row_idx, row in enumerate(field):
            for col_idx, tile in enumerate(row):
                if tile and tile["type"] == "grass":
                    x, y = col_idx * CELL_SIZE, row_idx * CELL_SIZE
                    screen.blit(TEXTURES["grass"], (x, y))

        if check_water_collision(player_pos, field):
            lives -= 1
            player_pos = [rows - 2, (cols // 2) - 2]
            player_direction = "player_tank_up"
            tower_direction = "player_tower_up"

        if enemy_tanks == 0:
            game_over = True

        if lives == 0 or player_rect.colliderect(emblem_rect):
            game_over = True

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    exit()

if __name__ == "__main__":
    main()
