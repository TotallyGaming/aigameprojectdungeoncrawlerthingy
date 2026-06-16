import random
import math

# --- Window ---
WIDTH = 800
HEIGHT = 600
TITLE = "Dungeon Crawler"

TILE = 32  # pixels per tile
COLS = 25
ROWS = 18

# --- Colours ---
BLACK      = (0,   0,   0)
DARK_GREY  = (20,  20,  30)
MID_GREY   = (50,  50,  70)
LIGHT_GREY = (160, 160, 180)
WHITE      = (240, 240, 255)
GOLD       = (255, 200,  50)
RED        = (200,  40,  40)
BRIGHT_RED = (255,  80,  80)
GREEN      = (60,  180,  60)
BRIGHT_GREEN=(100, 255, 100)
BLUE       = (60,  120, 220)
CYAN       = (80,  220, 220)
PURPLE     = (160,  60, 200)
ORANGE     = (220, 130,  30)
DARK_GREEN = (20,   80,  20)
BROWN      = (100,  60,  20)
YELLOW     = (255, 230,  80)

# --- Tile types ---
WALL  = 0
FLOOR = 1
DOOR  = 2
STAIR = 3
CHEST = 4

title_timer = 0
def update():
    global title_timer
    title_timer += 1

# ── Dungeon generator ──────────────────────────────────────────────────────────
def generate_dungeon(level):
    grid = [[WALL] * COLS for _ in range(ROWS)]
    rooms = []

    attempts = 0
    while len(rooms) < 6 and attempts < 200:
        attempts += 1
        rw = random.randint(4, 9)
        rh = random.randint(3, 7)
        rx = random.randint(1, COLS - rw - 1)
        ry = random.randint(1, ROWS - rh - 1)

        # Check overlap (with 1-tile gap)
        overlaps = False
        for room in rooms:
            if (rx < room[0] + room[2] + 2 and rx + rw + 1 > room[0] and
                    ry < room[1] + room[3] + 2 and ry + rh + 1 > room[1]):
                overlaps = True
                break
        if overlaps:
            continue

        for y in range(ry, ry + rh):
            for x in range(rx, rx + rw):
                grid[y][x] = FLOOR
        rooms.append((rx, ry, rw, rh))

    # Connect rooms with corridors
    random.shuffle(rooms)
    for i in range(len(rooms) - 1):
        x1 = rooms[i][0] + rooms[i][2] // 2
        y1 = rooms[i][1] + rooms[i][3] // 2
        x2 = rooms[i+1][0] + rooms[i+1][2] // 2
        y2 = rooms[i+1][1] + rooms[i+1][3] // 2
        # L-shaped corridor
        if random.random() < 0.5:
            for x in range(min(x1,x2), max(x1,x2)+1):
                grid[y1][x] = FLOOR
            for y in range(min(y1,y2), max(y1,y2)+1):
                grid[y][x2] = FLOOR
        else:
            for y in range(min(y1,y2), max(y1,y2)+1):
                grid[y][x1] = FLOOR
            for x in range(min(x1,x2), max(x1,x2)+1):
                grid[y2][x] = FLOOR

    # Place staircase in last room
    lr = rooms[-1]
    sx = lr[0] + lr[2] // 2
    sy = lr[1] + lr[3] // 2
    grid[sy][sx] = STAIR

    # Place chests in random rooms
    chests = []
    for room in rooms[1:-1]:
        if random.random() < 0.5:
            cx = room[0] + random.randint(1, room[2]-2)
            cy = room[1] + random.randint(1, room[3]-2)
            if grid[cy][cx] == FLOOR:
                grid[cy][cx] = CHEST
                chests.append((cx, cy))

    # Monsters: more & tougher per level
    monsters = []
    enemy_count = 3 + level * 2
    floor_tiles = [(x, y) for y in range(ROWS) for x in range(COLS)
                  if grid[y][x] == FLOOR]
    spawn_pool = [t for t in floor_tiles
                  if t != (rooms[0][0]+1, rooms[0][1]+1)]  # avoid start room

    for _ in range(min(enemy_count, len(spawn_pool))):
        pos = random.choice(spawn_pool)
        spawn_pool.remove(pos)
        kind = random.choices(
            ['goblin', 'skeleton', 'orc', 'troll'],
            weights=[4, 3, 2, max(1, level-2)],
            k=1
        )[0]
        hp_bonus = level * 3
        monsters.append({
            'x': pos[0], 'y': pos[1],
            'kind': kind,
            'hp': {'goblin':8,'skeleton':12,'orc':18,'troll':30}[kind] + hp_bonus,
            'max_hp': {'goblin':8,'skeleton':12,'orc':18,'troll':30}[kind] + hp_bonus,
            'atk': {'goblin':3,'skeleton':4,'orc':6,'troll':10}[kind] + level,
            'alive': True,
            'move_timer': 0,
        })

    # Player start: first room centre
    fr = rooms[0]
    px = fr[0] + fr[2] // 2
    py = fr[1] + fr[3] // 2

    return grid, monsters, (px, py), (sx, sy), chests


# ── Game state ─────────────────────────────────────────────────────────────────
def new_game():
    global player, dungeon_level, message_log, game_state, opened_chests
    dungeon_level = 1
    player = {
        'x': 0, 'y': 0,
        'hp': 30, 'max_hp': 30,
        'atk': 5,
        'gold': 0,
        'xp': 0, 'level': 1,
        'xp_next': 20,
    }
    message_log = ["Welcome, brave adventurer!", "Find the stairs to go deeper…"]
    opened_chests = set()
    game_state = 'play'
    load_level()

def load_level():
    global grid, monsters, stairs_pos, chests, opened_chests
    opened_chests = set()
    grid, monsters, (player['x'], player['y']), stairs_pos, chests = generate_dungeon(dungeon_level)
    log(f"Dungeon level {dungeon_level} — good luck!")

def log(msg):
    message_log.append(msg)
    if len(message_log) > 6:
        message_log.pop(0)

# Initialise
game_state = 'title'
player = {}
dungeon_level = 1
message_log = []
grid = []
monsters = []
stairs_pos = (0,0)
chests = []
opened_chests = set()

# ── Movement / combat ──────────────────────────────────────────────────────────
def try_move(dx, dy):
    global game_state, dungeon_level
    nx = player['x'] + dx
    ny = player['y'] + dy
    if not (0 <= nx < COLS and 0 <= ny < ROWS):
        return
    tile = grid[ny][nx]
    if tile == WALL:
        return

    # Attack monster?
    for m in monsters:
        if m['alive'] and m['x'] == nx and m['y'] == ny:
            dmg = max(1, player['atk'] + random.randint(-1, 2))
            m['hp'] -= dmg
            if m['hp'] <= 0:
                m['alive'] = False
                xp = {'goblin':5,'skeleton':8,'orc':12,'troll':20}[m['kind']]
                player['xp'] += xp
                gold = random.randint(1, 4) * dungeon_level
                player['gold'] += gold
                log(f"Killed {m['kind']}! +{xp} XP, +{gold} gold")
                check_levelup()
            else:
                log(f"Hit {m['kind']} for {dmg} dmg. ({m['hp']}/{m['max_hp']} HP)")
            return  # don't move into monster

    # Move
    player['x'] = nx
    player['y'] = ny

    if tile == CHEST and (nx, ny) not in opened_chests:
        opened_chests.add((nx, ny))
        gold = random.randint(5, 15) * dungeon_level
        heal = random.randint(3, 8)
        player['gold'] += gold
        player['hp'] = min(player['max_hp'], player['hp'] + heal)
        log(f"Chest! +{gold} gold, +{heal} HP restored.")

    if tile == STAIR:
        dungeon_level += 1
        load_level()
        log(f"Descended to level {dungeon_level}!")
        if dungeon_level % 3 == 0:
            player['max_hp'] += 5
            player['hp'] = min(player['max_hp'], player['hp'] + 5)
            log("You feel stronger! Max HP +5")

def check_levelup():
    while player['xp'] >= player['xp_next']:
        player['level'] += 1
        player['xp'] -= player['xp_next']
        player['xp_next'] = int(player['xp_next'] * 1.6)
        player['atk'] += 2
        player['max_hp'] += 8
        player['hp'] = min(player['max_hp'], player['hp'] + 8)
        log(f"LEVEL UP → Lv{player['level']}! ATK+2, HP+8")

def monster_turn():
    for m in monsters:
        if not m['alive']:
            continue
        # Simple chase: step toward player
        dx = 0 if player['x'] == m['x'] else (1 if player['x'] > m['x'] else -1)
        dy = 0 if player['y'] == m['y'] else (1 if player['y'] > m['y'] else -1)
        dist = abs(player['x'] - m['x']) + abs(player['y'] - m['y'])

        if dist == 1:
            # Attack
            dmg = max(1, m['atk'] + random.randint(-1, 2))
            player['hp'] -= dmg
            log(f"{m['kind'].capitalize()} hits you for {dmg} dmg!")
            if player['hp'] <= 0:
                player['hp'] = 0
                return 'dead'
        elif dist <= 8:
            # Move toward player (prefer axis with bigger gap)
            moved = False
            steps = [(dx, 0), (0, dy), (dx, dy)] if abs(player['x']-m['x']) >= abs(player['y']-m['y']) else [(0, dy), (dx, 0), (dx, dy)]
            for sdx, sdy in steps:
                if sdx == 0 and sdy == 0:
                    continue
                nx2, ny2 = m['x'] + sdx, m['y'] + sdy
                if (0 <= nx2 < COLS and 0 <= ny2 < ROWS and
                        grid[ny2][nx2] != WALL and
                        not any(o['alive'] and o['x']==nx2 and o['y']==ny2 for o in monsters if o is not m) and
                        not (nx2 == player['x'] and ny2 == player['y'])):
                    m['x'], m['y'] = nx2, ny2
                    moved = True
                    break
    return None

# ── Drawing helpers ────────────────────────────────────────────────────────────
MONSTER_COLOURS = {
    'goblin':   (80,  160,  60),
    'skeleton': (200, 200, 210),
    'orc':      (100, 140,  40),
    'troll':    (80,   80, 140),
}
MONSTER_LETTERS = {'goblin':'g','skeleton':'s','orc':'o','troll':'T'}

def draw_tile(screen, tx, ty, tile, chest_open):
    px_x = tx * TILE
    px_y = ty * TILE
    if tile == WALL:
        screen.draw.filled_rect(Rect(px_x, px_y, TILE, TILE), (30, 25, 40))
        # Stone texture lines
        screen.draw.rect(Rect(px_x+1, px_y+1, TILE-2, TILE-2), (50, 42, 65))
    elif tile == FLOOR:
        screen.draw.filled_rect(Rect(px_x, px_y, TILE, TILE), (45, 38, 55))
        # subtle dot
        screen.draw.filled_rect(Rect(px_x+15, px_y+15, 2, 2), (55, 48, 68))
    elif tile == STAIR:
        screen.draw.filled_rect(Rect(px_x, px_y, TILE, TILE), (45, 38, 55))
        screen.draw.filled_rect(Rect(px_x+4, px_y+4, TILE-8, TILE-8), (60, 180, 140))
        screen.draw.text('▼', (px_x+8, px_y+7), color=WHITE, fontsize=18)
    elif tile == CHEST:
        screen.draw.filled_rect(Rect(px_x, px_y, TILE, TILE), (45, 38, 55))
        colour = MID_GREY if chest_open else GOLD
        screen.draw.filled_rect(Rect(px_x+5, px_y+8, TILE-10, TILE-14), colour)
        screen.draw.rect(Rect(px_x+5, px_y+8, TILE-10, TILE-14), BROWN)

def draw_hp_bar(screen, x, y, w, h, cur, mx, col_fill, col_bg):
    screen.draw.filled_rect(Rect(x, y, w, h), col_bg)
    fill = int(w * max(0, cur) / max(1, mx))
    if fill:
        screen.draw.filled_rect(Rect(x, y, fill, h), col_fill)
    screen.draw.rect(Rect(x, y, w, h), LIGHT_GREY)

# ── Pygame Zero hooks ──────────────────────────────────────────────────────────
def draw():
    screen.fill(DARK_GREY)

    if game_state == 'title':
        draw_title()
    elif game_state == 'play':
        draw_play()
    elif game_state == 'dead':
        draw_dead()
    elif game_state == 'win':
        draw_win()

def draw_title():
    screen.draw.filled_rect(Rect(0, 0, WIDTH, HEIGHT), (10, 8, 18))
    # Decorative border
    screen.draw.rect(Rect(20, 20, WIDTH-40, HEIGHT-40), (80, 60, 120))
    screen.draw.rect(Rect(24, 24, WIDTH-48, HEIGHT-48), (50, 38, 75))

    screen.draw.text("DUNGEON CRAWLER", center=(WIDTH//2, 130),
                    color=GOLD, fontsize=52)
    screen.draw.text("A Roguelike Adventure", center=(WIDTH//2, 185),
                    color=LIGHT_GREY, fontsize=24)

    # ASCII art dungeon
    art = [
    "+---------------+",
    "| X  @  *  *   |",
    "|      v       |",
    "+---------------+"
]
    for i, line in enumerate(art):
        screen.draw.text(line, center=(WIDTH//2, 250 + i*26),
                        color=(100, 180, 120), fontsize=20)

    screen.draw.text("Controls", center=(WIDTH//2, 380), color=GOLD, fontsize=20)
    controls = ["Arrow keys / WASD — Move & Attack",
                "Walk into enemies to attack",
                "Walk into stairs (▼) to descend",
                "Walk into chests to open them"]
    for i, c in enumerate(controls):
        screen.draw.text(c, center=(WIDTH//2, 410 + i*24),
                        color=LIGHT_GREY, fontsize=17)

    pulse = 0.5 + 0.5 * math.sin(title_timer / 20)
    col = (int(180+75*pulse), int(180+75*pulse), 80)
    screen.draw.text("Press ENTER to begin", center=(WIDTH//2, 545),
                    color=col, fontsize=22)

def draw_play():
    # Dungeon tiles
    for ty in range(ROWS):
        for tx in range(COLS):
            tile = grid[ty][tx]
            draw_tile(screen, tx, ty, tile, (tx,ty) in opened_chests)

    # Monsters
    for m in monsters:
        if not m['alive']:
            continue
        mx2 = m['x'] * TILE
        my2 = m['y'] * TILE
        col = MONSTER_COLOURS[m['kind']]
        screen.draw.filled_rect(Rect(mx2+4, my2+4, TILE-8, TILE-8), col)
        letter = MONSTER_LETTERS[m['kind']]
        screen.draw.text(letter, (mx2+10, my2+8), color=WHITE, fontsize=16)
        # mini HP bar
        draw_hp_bar(screen, mx2+2, my2+1, TILE-4, 4, m['hp'], m['max_hp'],
                    BRIGHT_RED, (80,20,20))

    # Player
    px2 = player['x'] * TILE
    py2 = player['y'] * TILE
    screen.draw.filled_rect(Rect(px2+3, py2+3, TILE-6, TILE-6), BLUE)
    screen.draw.text('@', (px2+9, py2+8), color=WHITE, fontsize=16)

    # HUD panel at bottom (2 rows)
    hud_y = ROWS * TILE
    hud_h = HEIGHT - hud_y
    screen.draw.filled_rect(Rect(0, hud_y, WIDTH, hud_h), (15, 12, 25))
    screen.draw.line((0, hud_y), (WIDTH, hud_y), (80, 60, 120))

    # Stats row
    sy2 = hud_y + 6
    screen.draw.text(f"Lv{player['level']}", (10, sy2), color=GOLD, fontsize=17)
    draw_hp_bar(screen, 70, sy2+2, 120, 13, player['hp'], player['max_hp'],
                BRIGHT_RED, (60,15,15))
    screen.draw.text(f"{player['hp']}/{player['max_hp']}",
                    (196, sy2), color=WHITE, fontsize=15)
    screen.draw.text(f"ATK:{player['atk']}", (270, sy2), color=CYAN, fontsize=16)
    screen.draw.text(f"XP:{player['xp']}/{player['xp_next']}",
                    (345, sy2), color=BRIGHT_GREEN, fontsize=16)
    screen.draw.text(f"Gold:{player['gold']}",
                    (490, sy2), color=GOLD, fontsize=16)
    screen.draw.text(f"Floor:{dungeon_level}",
                    (600, sy2), color=PURPLE, fontsize=16)

    alive_count = sum(1 for m in monsters if m['alive'])
    screen.draw.text(f"Enemies:{alive_count}",
                    (690, sy2), color=BRIGHT_RED, fontsize=16)

    # Message log
    log_y = hud_y + 26
    for i, msg in enumerate(message_log[-4:]):
        alpha = 130 + 30 * i
        col_msg = (alpha, alpha, min(255, alpha+30))
        screen.draw.text(msg, (8, log_y + i * 19), color=col_msg, fontsize=15)

    # Legend
    screen.draw.text("▼=Stairs  ■=Chest  @=You  g=Goblin s=Skeleton o=Orc T=Troll",
                    (8, HEIGHT - 18), color=(90,85,110), fontsize=13)

def draw_dead():
    screen.fill((10, 5, 10))
    screen.draw.text("YOU DIED", center=(WIDTH//2, 180), color=RED, fontsize=64)
    screen.draw.text(f"Reached floor {dungeon_level}  •  Level {player['level']}",
                    center=(WIDTH//2, 270), color=LIGHT_GREY, fontsize=24)
    screen.draw.text(f"Gold collected: {player['gold']}",
                    center=(WIDTH//2, 310), color=GOLD, fontsize=22)
    screen.draw.text("Press ENTER to try again", center=(WIDTH//2, 400),
                    color=WHITE, fontsize=22)

def draw_win():
    screen.fill((5, 10, 5))
    screen.draw.text("VICTORY!", center=(WIDTH//2, 180), color=GOLD, fontsize=64)
    screen.draw.text("You conquered all 10 dungeon floors!",
                    center=(WIDTH//2, 270), color=WHITE, fontsize=24)
    screen.draw.text(f"Final Level: {player['level']}  •  Gold: {player['gold']}",
                    center=(WIDTH//2, 320), color=GOLD, fontsize=22)
    screen.draw.text("Press ENTER to play again", center=(WIDTH//2, 420),
                    color=LIGHT_GREY, fontsize=22)


def on_key_down(key):
    global game_state
    if game_state == 'title':
        if key == keys.RETURN or key == keys.KP_ENTER:
            new_game()
        return

    if game_state in ('dead', 'win'):
        if key == keys.RETURN or key == keys.KP_ENTER:
            game_state = 'title'
        return

    if game_state != 'play':
        return

    dx, dy = 0, 0
    if key in (keys.UP, keys.W):      dy = -1
    elif key in (keys.DOWN, keys.S):  dy =  1
    elif key in (keys.LEFT, keys.A):  dx = -1
    elif key in (keys.RIGHT, keys.D): dx =  1
    else:
        return

    try_move(dx, dy)

    if player['hp'] <= 0:
        game_state = 'dead'
        log("You have been slain…")
        return

    result = monster_turn()
    if result == 'dead':
        game_state = 'dead'

    if dungeon_level > 10:
        game_state = 'win'


def update():
    pass  # All logic is event-driven
