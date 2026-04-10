import pygame
import random
import math
import sys

pygame.init()

screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Human Extinction JUICE FINAL")
clock = pygame.time.Clock()

# ---------------- PLAYER ----------------
x, y = 400, 300
size = 50

# ---------------- GAME ----------------
wave = 1
xp = 0
game_mode = "WAVES"

font = pygame.font.SysFont(None, 28)

# ---------------- FX ----------------
juice_mode = True
shake = 0
rainbow_timer = 0

trail = []
slash_fx = []
slash_marks = []

# ---------------- ENTITIES ----------------
humans = []

# ---------------- BOSS ----------------
boss_hp = 30
boss_max_hp = 30
boss_x = 400
boss_y = 200
boss_vx = 0
boss_vy = 0
boss_phase = 1

in_boss = False
boss_alive = False

# ---------------- NEW SYSTEMS ----------------
kill_count = 0
final_boss = False
game_won = False


# ---------------- UTILS ----------------
def clamp(v, mn, mx):
    return max(mn, min(mx, v))


def spawn_humans(n):
    humans.clear()
    for _ in range(n):
        humans.append({
            "x": random.randint(50, 750),
            "y": random.randint(50, 550),
            "vx": 0,
            "vy": 0,
            "speed": 1.5,
            "type": random.choice(["rusher", "orbiter", "shooter"]),
            "angle": random.uniform(0, math.pi * 2)
        })


def spawn_slash(x, y):
    for _ in range(10):
        a = random.uniform(0, math.pi * 2)
        s = random.uniform(2, 4)
        slash_fx.append([x, y, math.cos(a) * s, math.sin(a) * s, 12])


def start_boss():
    global in_boss, boss_alive, boss_hp, boss_x, boss_y, boss_vx, boss_vy, boss_phase

    in_boss = True
    boss_alive = True
    boss_hp = boss_max_hp
    boss_phase = 1

    humans.clear()

    boss_x = random.randint(120, 680)
    boss_y = random.randint(120, 420)
    boss_vx = 0
    boss_vy = 0


def draw_boss_hp_bar(surface):
    if not in_boss:
        return

    x = 250
    y = 18
    w = 300
    h = 16

    pygame.draw.rect(surface, (60, 0, 0), (x, y, w, h), border_radius=6)

    ratio = max(0, min(1, boss_hp / boss_max_hp))

    pygame.draw.rect(
        surface,
        (255, 0, 140),
        (x, y, int(w * ratio), h),
        border_radius=6
    )

    pygame.draw.rect(surface, (180, 0, 255), (x, y, w, h), 2, border_radius=6)


def bounce_to_center(h):
    cx, cy = 400, 300

    if h["x"] < 30:
        h["x"] = 30
        h["vx"] *= -0.6
    elif h["x"] > 770:
        h["x"] = 770
        h["vx"] *= -0.6

    if h["y"] < 30:
        h["y"] = 30
        h["vy"] *= -0.6
    elif h["y"] > 570:
        h["y"] = 570
        h["vy"] *= -0.6

    dx = cx - h["x"]
    dy = cy - h["y"]

    h["vx"] += dx * 0.0015
    h["vy"] += dy * 0.0015

    h["vx"] *= 0.90
    h["vy"] *= 0.90


# ---------------- INIT ----------------
spawn_humans(6)

running = True
while running:
    clock.tick(60)

    if game_won:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        continue

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.FINGERDOWN:
            tx = event.x * 800
            ty = event.y * 600
            x += (tx - x) * 0.15
            y += (ty - y) * 0.15

        elif event.type == pygame.FINGERMOTION:
            tx = event.x * 800
            ty = event.y * 600
            x += (tx - x) * 0.15
            y += (ty - y) * 0.15

    # ---------------- PLAYER ----------------
    keys = pygame.key.get_pressed()
    speed = 5 if juice_mode else 4

    if keys[pygame.K_LEFT]:
        x -= speed
    if keys[pygame.K_RIGHT]:
        x += speed
    if keys[pygame.K_UP]:
        y -= speed
    if keys[pygame.K_DOWN]:
        y += speed

    if pygame.mouse.get_pressed()[0]:
        mx, my = pygame.mouse.get_pos()
        x += (mx - x) * 0.12
        y += (my - y) * 0.12

    x = clamp(x, 0, 750)
    y = clamp(y, 0, 550)

    # ---------------- TRAIL ----------------
    trail.append((x, y))
    if len(trail) > 14:
        trail.pop(0)

    # ---------------- WAVE FIX (ONLY CHANGE HERE) ----------------
    if not in_boss and len(humans) == 0:
        wave += 1

        if wave >= 20:
            wave = 20
            start_boss()
        else:
            # 🔥 LONGER WAVES ONLY CHANGE
            spawn_humans(6 + (wave * 3))

    # ---------------- HUMANS ----------------
    if not in_boss:
        for h in humans:
            dx, dy = x - h["x"], y - h["y"]
            d = math.sqrt(dx * dx + dy * dy) or 1

            if h["type"] == "rusher":
                h["vx"] = dx / d * (h["speed"] + 1)
                h["vy"] = dy / d * (h["speed"] + 1)

            elif h["type"] == "orbiter":
                h["angle"] += 0.04
                r = 60
                tx = x + math.cos(h["angle"]) * r
                ty = y + math.sin(h["angle"]) * r
                h["x"] += (tx - h["x"]) * 0.15
                h["y"] += (ty - h["y"]) * 0.15

            elif h["type"] == "shooter":
                if d < 220:
                    h["vx"] -= dx / d * h["speed"]
                    h["vy"] -= dy / d * h["speed"]

            if d < 70:
                h["vx"] += (h["x"] - x) * 0.04
                h["vy"] += (h["y"] - y) * 0.04

            h["x"] += h["vx"]
            h["y"] += h["vy"]

            h["vx"] *= 0.88
            h["vy"] *= 0.88

            bounce_to_center(h)

    # ---------------- ATTACKS ----------------
    for h in humans[:]:
        if math.dist((x, y), (h["x"], h["y"])) < 45:
            humans.remove(h)
            xp += 1
            kill_count += 1
            spawn_slash(h["x"], h["y"])
            shake = 10
            rainbow_timer = 12

    # ---------------- FINAL BOSS ----------------
    if kill_count >= 10 and not final_boss:
        final_boss = True
        start_boss()

    # ---------------- BOSS ----------------
    if in_boss and boss_alive:
        if math.dist((x, y), (boss_x, boss_y)) < 80:
            boss_hp -= 1

        dx = x - boss_x
        dy = y - boss_y
        dist = math.sqrt(dx * dx + dy * dy) or 1

        if boss_hp < 20:
            boss_phase = 2
        if boss_hp < 10:
            boss_phase = 3

        speed = 0.05 if not final_boss else 0.09

        if boss_phase == 1:
            boss_vx += dx / dist * speed
            boss_vy += dy / dist * speed
        elif boss_phase == 2:
            boss_vx += math.cos(pygame.time.get_ticks() * 0.003) * 0.5
            boss_vy += math.sin(pygame.time.get_ticks() * 0.003) * 0.5
        else:
            boss_vx += dx / dist * speed * 1.3
            boss_vy += dy / dist * speed * 1.3

        boss_x += boss_vx
        boss_y += boss_vy

        boss_vx *= 0.92
        boss_vy *= 0.92

    # ---------------- WIN ----------------
    if in_boss and boss_hp <= 0:
        if final_boss:
            game_won = True
            in_boss = False
        else:
            boss_max_hp += 15
            start_boss()
            shake = 20
            rainbow_timer = 20

    # ---------------- DRAW ----------------
    offset_x = offset_y = 0
    if juice_mode and shake > 0:
        offset_x = random.randint(-int(shake), int(shake))
        offset_y = random.randint(-int(shake), int(shake))
        shake *= 0.80

    temp = pygame.Surface((800, 600))

    if in_boss:
        temp.fill((40, 0, 60))
        overlay = pygame.Surface((800, 600))
        overlay.set_alpha(70)
        overlay.fill((180, 0, 40))
        temp.blit(overlay, (0, 0))
    else:
        temp.fill((12, 12, 28))

    for i, p in enumerate(trail):
        pygame.draw.circle(temp, (255, 70, 120), (int(p[0]), int(p[1])), i // 2 + 2)

    for s in slash_fx[:]:
        s[0] += s[2]
        s[1] += s[3]
        s[4] -= 1
        pygame.draw.circle(temp, (255, 200, 200), (int(s[0]), int(s[1])), 3)
        if s[4] <= 0:
            slash_marks.append([s[0], s[1]])
            slash_fx.remove(s)

    for m in slash_marks:
        pygame.draw.circle(temp, (120, 0, 0), (int(m[0]), int(m[1])), 5)

    if not in_boss:
        t = pygame.time.get_ticks()
        for h in humans:
            pulse = 2 + int(2 * math.sin(t * 0.01))

            col = (255, 80, 80) if h["type"] == "rusher" else (80, 120, 255) if h["type"] == "orbiter" else (80, 255, 120)

            pygame.draw.rect(temp, col,
                             (h["x"] - pulse, h["y"] - pulse, 22 + pulse * 2, 22 + pulse * 2),
                             border_radius=4)

            pygame.draw.circle(temp, (0, 0, 0), (int(h["x"] + 6), int(h["y"] + 8)), 2)
            pygame.draw.circle(temp, (0, 0, 0), (int(h["x"] + 14), int(h["y"] + 8)), 2)

    if in_boss and boss_alive:
        pulse = 6 + int(3 * math.sin(pygame.time.get_ticks() * 0.02))

        pygame.draw.rect(temp,
                         (255, 0, 140) if not final_boss else (255, 220, 0),
                         (boss_x - pulse, boss_y - pulse, 60 + pulse * 2, 60 + pulse * 2),
                         border_radius=10)

        pygame.draw.rect(temp, (255, 0, 140), (boss_x, boss_y, 60, 60), border_radius=8)

        pygame.draw.circle(temp, (0, 0, 0), (int(boss_x + 18), int(boss_y + 22)), 4)
        pygame.draw.circle(temp, (0, 0, 0), (int(boss_x + 42), int(boss_y + 22)), 4)

    pulse = 3 + int(2 * math.sin(pygame.time.get_ticks() * 0.03))

    pygame.draw.rect(temp, (255, 40, 80),
                     (x - pulse, y - pulse, size + pulse * 2, size + pulse * 2),
                     border_radius=6)

    pygame.draw.rect(temp, (255, 120, 140), (x, y, size, size))

    pygame.draw.line(temp, (255, 255, 255),
                     (x + size // 2, y + 8),
                     (x + size // 2, y + size - 8),
                     2)

    ui = font.render(f"MODE: {game_mode} | WAVE: {wave} | XP: {xp}", True, (255, 255, 255))
    temp.blit(ui, (10, 10))

    draw_boss_hp_bar(temp)

    if game_won:
        win = font.render("🎥 YOU WIN !!! 🎥", True, (255, 255, 0))
        temp.blit(win, (250, 280))

    if rainbow_timer > 0:
        rainbow_timer -= 1
        tt = pygame.time.get_ticks() * 0.01
        flash = pygame.Surface((800, 600))
        flash.set_alpha(70)
        flash.fill((
            int(127 + 127 * math.sin(tt)),
            int(127 + 127 * math.sin(tt + 2)),
            int(127 + 127 * math.sin(tt + 4))
        ))
        temp.blit(flash, (0, 0))

    screen.blit(temp, (offset_x, offset_y))
    pygame.display.update()

pygame.quit()
sys.exit()