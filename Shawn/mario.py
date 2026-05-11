import pygame
import sys
import math
import random

pygame.init()

# ── Constants ──────────────────────────────────────────────────────────────────
WIDTH, HEIGHT = 900, 550
FPS = 60
GRAVITY = 0.55
JUMP_FORCE = -13
PLAYER_SPEED = 4
TILE = 40

# Palette
SKY       = (107, 196, 255)
SUN       = (255, 220, 50)
GROUND_T  = (139, 90, 43)
GROUND_B  = (101, 67, 33)
GRASS     = (80, 200, 80)
BRICK_A   = (196, 100, 48)
BRICK_B   = (160, 72, 28)
QBLOCK_A  = (240, 180, 40)
QBLOCK_B  = (200, 140, 20)
COIN_C    = (255, 215, 0)
PIPE_A    = (0, 180, 80)
PIPE_B    = (0, 130, 50)
MARIO_R   = (220, 50, 50)
MARIO_S   = (245, 210, 160)
MARIO_B   = (60, 80, 200)
MARIO_H   = (80, 50, 20)
ENEMY_C   = (160, 90, 30)
ENEMY_F   = (220, 140, 60)
FLAG_C    = (60, 200, 80)
FLAG_P    = (180, 180, 180)
HUD_BG    = (0, 0, 0, 160)
WHITE     = (255, 255, 255)
BLACK     = (0, 0, 0)
RED       = (220, 40, 40)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Super Mario Bros")
clock = pygame.time.Clock()

font_big   = pygame.font.SysFont("Arial", 36, bold=True)
font_med   = pygame.font.SysFont("Arial", 24, bold=True)
font_small = pygame.font.SysFont("Arial", 18, bold=True)

# ── Helper ─────────────────────────────────────────────────────────────────────
def draw_text(surf, text, font, color, x, y, center=False):
    img = font.render(text, True, color)
    if center:
        x -= img.get_width() // 2
    surf.blit(img, (x, y))

# ── Level data (tile map) ──────────────────────────────────────────────────────
# G=ground, B=brick, Q=question, P=pipe, C=coin, E=enemy, F=flag, ' '=air
LEVEL = [
    "                                                                                              F",
    "                                                                                              F",
    "                                                                                              F",
    "                                                                                              F",
    "                                                                                              F",
    "                                                                                             PF",
    "                                                                                             PF",
    "        BBB         Q   Q                                     BBB            BBB             PF",
    "                                     BBBB                                                   PF",
    "   Q          Q          Q                    E         E              Q                    PF",
    "                                                                                             PF",
    "GGGGGGGGGGGGG   GGGGGGGGGGGGGG   GGGGGGGGGGGGGGGGGGG   GGGGGGG   GGGGGGGGGGGGGGGGGGGGGGGGGGGG",
    "GGGGGGGGGGGGG   GGGGGGGGGGGGGG   GGGGGGGGGGGGGGGGGGG   GGGGGGG   GGGGGGGGGGGGGGGGGGGGGGGGGGGG",
]

LEVEL_W = len(LEVEL[0])
LEVEL_H = len(LEVEL)

COINS_ROW = 9   # row where Q blocks and coins sit
COIN_ANIM_DURATION = 40  # frames

# ── Camera ─────────────────────────────────────────────────────────────────────
class Camera:
    def __init__(self):
        self.offset_x = 0

    def update(self, player_x):
        target = player_x - WIDTH // 3
        self.offset_x += (target - self.offset_x) * 0.12
        self.offset_x = max(0, min(self.offset_x, LEVEL_W * TILE - WIDTH))

    def apply(self, x):
        return x - self.offset_x

# ── Tile ───────────────────────────────────────────────────────────────────────
class Tile:
    def __init__(self, tx, ty, kind):
        self.rect = pygame.Rect(tx * TILE, ty * TILE, TILE, TILE)
        self.kind = kind          # 'G','B','Q','P','C'
        self.hit = False          # for Q blocks
        self.coin_anim = 0        # frames remaining for coin pop animation

    def draw(self, surf, cam):
        rx = cam.apply(self.rect.x)
        ry = self.rect.y
        if rx > WIDTH or rx + TILE < 0:
            return
        r = pygame.Rect(rx, ry, TILE, TILE)

        if self.kind == 'G':
            pygame.draw.rect(surf, GRASS, (rx, ry, TILE, 6))
            pygame.draw.rect(surf, GROUND_T, (rx, ry+6, TILE, TILE-6))
            pygame.draw.line(surf, GROUND_B, (rx, ry+TILE-1), (rx+TILE, ry+TILE-1), 2)

        elif self.kind == 'B':
            pygame.draw.rect(surf, BRICK_A, r)
            pygame.draw.line(surf, BRICK_B, (rx, ry+TILE//2), (rx+TILE, ry+TILE//2), 2)
            pygame.draw.line(surf, BRICK_B, (rx+TILE//2, ry), (rx+TILE//2, ry+TILE//2), 2)
            pygame.draw.line(surf, BRICK_B, (rx+TILE//4, ry+TILE//2), (rx+TILE//4, ry+TILE), 2)
            pygame.draw.line(surf, BRICK_B, (rx+3*TILE//4, ry+TILE//2), (rx+3*TILE//4, ry+TILE), 2)

        elif self.kind == 'Q':
            c1 = QBLOCK_A if not self.hit else (160, 120, 80)
            c2 = QBLOCK_B if not self.hit else (120, 90, 60)
            pygame.draw.rect(surf, c1, r)
            pygame.draw.rect(surf, c2, r, 3)
            if not self.hit:
                draw_text(surf, "?", font_med, BLACK, rx + 11, ry + 8)

        elif self.kind == 'P':
            body = pygame.Rect(rx+4, ry, TILE-8, TILE)
            pygame.draw.rect(surf, PIPE_A, body)
            pygame.draw.rect(surf, PIPE_B, body, 3)
            cap = pygame.Rect(rx, ry, TILE, 10)
            pygame.draw.rect(surf, PIPE_A, cap)
            pygame.draw.rect(surf, PIPE_B, cap, 3)

        # Coin pop animation
        if self.coin_anim > 0:
            prog = 1 - self.coin_anim / COIN_ANIM_DURATION
            cy = int(ry - 20 - prog * 30)
            pygame.draw.circle(surf, COIN_C, (rx + TILE//2, cy), 8)
            pygame.draw.circle(surf, WHITE, (rx + TILE//2 - 2, cy - 2), 3)
            self.coin_anim -= 1

# ── Coin (free-floating) ───────────────────────────────────────────────────────
class Coin:
    def __init__(self, tx, ty):
        self.rect = pygame.Rect(tx*TILE + 8, ty*TILE + 4, TILE-16, TILE-8)
        self.anim = 0
        self.collected = False

    def draw(self, surf, cam):
        if self.collected:
            return
        rx = cam.apply(self.rect.x)
        ry = self.rect.y + int(math.sin(self.anim * 0.1) * 4)
        self.anim += 1
        pygame.draw.ellipse(surf, COIN_C, (rx, ry, self.rect.w, self.rect.h))
        pygame.draw.ellipse(surf, WHITE, (rx+3, ry+3, self.rect.w//3, self.rect.h-6))

# ── Enemy ──────────────────────────────────────────────────────────────────────
class Enemy:
    SIZE = 34

    def __init__(self, tx, ty):
        self.rect = pygame.Rect(tx*TILE + 3, ty*TILE + TILE - self.SIZE, self.SIZE, self.SIZE)
        self.vx = -1.2
        self.vy = 0
        self.alive = True
        self.squish = False
        self.squish_timer = 0
        self.anim = 0

    def update(self, tiles):
        if self.squish:
            self.squish_timer -= 1
            if self.squish_timer <= 0:
                self.alive = False
            return

        self.vy += GRAVITY
        self.rect.x += int(self.vx)
        self._collide_x(tiles)
        self.rect.y += int(self.vy)
        self._collide_y(tiles)
        self.anim += 1

    def _collide_x(self, tiles):
        for t in tiles:
            if t.kind in ('G','B','Q','P') and self.rect.colliderect(t.rect):
                self.vx = -self.vx
                if self.vx < 0:
                    self.rect.right = t.rect.left
                else:
                    self.rect.left = t.rect.right

    def _collide_y(self, tiles):
        for t in tiles:
            if t.kind in ('G','B','Q','P') and self.rect.colliderect(t.rect):
                if self.vy > 0:
                    self.rect.bottom = t.rect.top
                    self.vy = 0
                else:
                    self.rect.top = t.rect.bottom
                    self.vy = 0

    def draw(self, surf, cam):
        rx = cam.apply(self.rect.x)
        ry = self.rect.y
        if rx > WIDTH or rx + self.SIZE < 0:
            return
        if self.squish:
            pygame.draw.ellipse(surf, ENEMY_C, (rx, ry+24, self.SIZE, 10))
            return
        # Body
        pygame.draw.ellipse(surf, ENEMY_C, (rx, ry, self.SIZE, self.SIZE))
        # Face
        pygame.draw.circle(surf, ENEMY_F, (int(rx + self.SIZE*0.35), int(ry + self.SIZE*0.35)), 8)
        pygame.draw.circle(surf, ENEMY_F, (int(rx + self.SIZE*0.65), int(ry + self.SIZE*0.35)), 8)
        pygame.draw.circle(surf, BLACK, (int(rx + self.SIZE*0.35), int(ry + self.SIZE*0.37)), 4)
        pygame.draw.circle(surf, BLACK, (int(rx + self.SIZE*0.65), int(ry + self.SIZE*0.37)), 4)
        # Angry brows
        pygame.draw.line(surf, BLACK, (int(rx+6), int(ry+10)), (int(rx+16), int(ry+14)), 3)
        pygame.draw.line(surf, BLACK, (int(rx+self.SIZE-6), int(ry+10)), (int(rx+self.SIZE-16), int(ry+14)), 3)
        # Feet
        leg_off = int(math.sin(self.anim * 0.25) * 5)
        pygame.draw.ellipse(surf, ENEMY_C, (rx-2, ry+self.SIZE-8+leg_off, 12, 10))
        pygame.draw.ellipse(surf, ENEMY_C, (rx+self.SIZE-10, ry+self.SIZE-8-leg_off, 12, 10))

# ── Flag ───────────────────────────────────────────────────────────────────────
class Flag:
    def __init__(self, tx):
        self.x = tx * TILE + TILE//2
        self.pole_top = 1 * TILE
        self.pole_bot = 11 * TILE
        self.flag_y = 2 * TILE
        self.touched = False
        self.anim = 0

    def update(self):
        self.anim += 1
        if self.touched and self.flag_y < self.pole_bot - TILE:
            self.flag_y += 3

    def draw(self, surf, cam):
        rx = int(cam.apply(self.x))
        pygame.draw.line(surf, FLAG_P, (rx, self.pole_top), (rx, self.pole_bot), 5)
        # Waving flag
        pts = []
        for i in range(5):
            wave = int(math.sin(self.anim * 0.1 + i * 0.8) * 4)
            pts.append((rx + i*6 + wave, self.flag_y + i*2))
        for i in range(4, -1, -1):
            wave = int(math.sin(self.anim * 0.1 + i * 0.8) * 4)
            pts.append((rx + i*6 + wave, self.flag_y + 22 + i*2))
        if len(pts) >= 3:
            pygame.draw.polygon(surf, FLAG_C, pts)
        # Ball on top
        pygame.draw.circle(surf, COIN_C, (rx, self.pole_top), 6)

# ── Player ─────────────────────────────────────────────────────────────────────
class Player:
    W, H = 28, 36

    def __init__(self, tx, ty):
        self.rect = pygame.Rect(tx*TILE, ty*TILE - self.H, self.W, self.H)
        self.vx = 0
        self.vy = 0
        self.on_ground = False
        self.facing = 1
        self.anim = 0
        self.alive = True
        self.dead_timer = 0
        self.win = False
        self.win_timer = 0

    def update(self, keys, tiles, enemies, coins, flag):
        if not self.alive:
            self.dead_timer -= 1
            self.vy += 0.4
            self.rect.y += int(self.vy)
            return

        if self.win:
            self.win_timer += 1
            return

        # Horizontal movement
        self.vx = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vx = -PLAYER_SPEED
            self.facing = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vx = PLAYER_SPEED
            self.facing = 1

        # Jump
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]) and self.on_ground:
            self.vy = JUMP_FORCE
            self.on_ground = False

        self.vy += GRAVITY
        self.vy = min(self.vy, 15)

        # Move X
        self.rect.x += int(self.vx)
        self._collide_x(tiles)

        # Move Y
        self.on_ground = False
        self.rect.y += int(self.vy)
        self._collide_y(tiles)

        # Clamp left
        if self.rect.x < 0:
            self.rect.x = 0

        # Fall into pit
        if self.rect.top > HEIGHT + 50:
            self.alive = False
            self.dead_timer = 60

        # Enemy collision
        for e in enemies:
            if not e.alive or e.squish:
                continue
            if self.rect.colliderect(e.rect):
                # Stomp from above
                if self.vy > 0 and self.rect.bottom < e.rect.centery + 12:
                    e.squish = True
                    e.squish_timer = 30
                    self.vy = -8
                else:
                    self.alive = False
                    self.vy = -10
                    self.dead_timer = 80

        # Coin pickup
        for c in coins:
            if not c.collected and self.rect.colliderect(c.rect):
                c.collected = True

        # Flag
        if self.rect.centerx >= flag.x - 10 and not flag.touched:
            flag.touched = True
            self.win = True

        self.anim += 1

    def _collide_x(self, tiles):
        for t in tiles:
            if t.kind not in ('G','B','Q','P'):
                continue
            if self.rect.colliderect(t.rect):
                if self.vx > 0:
                    self.rect.right = t.rect.left
                elif self.vx < 0:
                    self.rect.left = t.rect.right

    def _collide_y(self, tiles):
        for t in tiles:
            if t.kind not in ('G','B','Q','P'):
                continue
            if self.rect.colliderect(t.rect):
                if self.vy > 0:
                    self.rect.bottom = t.rect.top
                    self.vy = 0
                    self.on_ground = True
                elif self.vy < 0:
                    self.rect.top = t.rect.bottom
                    self.vy = 0
                    # Hit block from below
                    if t.kind == 'Q' and not t.hit:
                        t.hit = True
                        t.coin_anim = COIN_ANIM_DURATION

    def draw(self, surf, cam):
        rx = cam.apply(self.rect.x)
        ry = self.rect.y
        if not self.alive:
            # Ghost / dead spin
            angle = self.dead_timer * 15
            s = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
            self._draw_body(s, 0, 0)
            rot = pygame.transform.rotate(s, angle)
            surf.blit(rot, (rx - (rot.get_width()-self.W)//2, ry))
            return
        self._draw_body(surf, rx, ry)

    def _draw_body(self, surf, rx, ry):
        fl = self.facing
        # Hat / hair
        pygame.draw.rect(surf, MARIO_R, (rx+2, ry, self.W-4, 12))
        # Face
        pygame.draw.rect(surf, MARIO_S, (rx+2, ry+10, self.W-4, 14))
        # Eyes
        ex = rx + (16 if fl > 0 else 6)
        pygame.draw.circle(surf, BLACK, (int(ex), int(ry+15)), 3)
        # Moustache
        pygame.draw.line(surf, MARIO_H, (rx+4, ry+20), (rx+self.W-4, ry+20), 3)
        # Body (overalls)
        pygame.draw.rect(surf, MARIO_B, (rx, ry+24, self.W, 14))
        # Legs animation
        if self.on_ground and (self.vx != 0):
            leg = int(math.sin(self.anim * 0.35) * 5)
        else:
            leg = 0
        pygame.draw.rect(surf, MARIO_B, (rx+1, ry+self.H-8+leg, 10, 8))
        pygame.draw.rect(surf, MARIO_B, (rx+self.W-11, ry+self.H-8-leg, 10, 8))
        # Shoes
        pygame.draw.rect(surf, BLACK, (rx, ry+self.H-4+leg, 12, 4))
        pygame.draw.rect(surf, BLACK, (rx+self.W-12, ry+self.H-4-leg, 12, 4))

# ── Build level ────────────────────────────────────────────────────────────────
def build_level():
    tiles, enemies, coins = [], [], []
    player_start = (2, 10)
    flag = None

    for ty, row in enumerate(LEVEL):
        for tx, ch in enumerate(row):
            if ch == 'G':
                tiles.append(Tile(tx, ty, 'G'))
            elif ch == 'B':
                tiles.append(Tile(tx, ty, 'B'))
            elif ch == 'Q':
                tiles.append(Tile(tx, ty, 'Q'))
            elif ch == 'P':
                tiles.append(Tile(tx, ty, 'P'))
            elif ch == 'C':
                coins.append(Coin(tx, ty))
            elif ch == 'E':
                enemies.append(Enemy(tx, ty))
            elif ch == 'F' and flag is None:
                flag = Flag(tx)

    return tiles, enemies, coins, player_start, flag

# ── Background decorations ─────────────────────────────────────────────────────
CLOUDS = [(random.randint(0, LEVEL_W*TILE), random.randint(20, 100)) for _ in range(14)]
HILLS  = [(i*180, HEIGHT - TILE*2 - random.randint(20, 70)) for i in range(LEVEL_W*TILE//180 + 2)]

def draw_bg(surf, cam):
    surf.fill(SKY)
    # Sun
    pygame.draw.circle(surf, SUN, (WIDTH-80, 60), 38)

    # Hills
    for hx, hy in HILLS:
        rx = cam.apply(hx)
        if -120 < rx < WIDTH + 120:
            pygame.draw.ellipse(surf, (80, 190, 80), (rx-60, hy, 120, 60))

    # Clouds (parallax ×0.4)
    for cx, cy in CLOUDS:
        rx = cx - cam.offset_x * 0.4
        if -120 < rx < WIDTH + 120:
            pygame.draw.ellipse(surf, WHITE, (rx, cy, 80, 36))
            pygame.draw.ellipse(surf, WHITE, (rx+20, cy-14, 50, 32))
            pygame.draw.ellipse(surf, WHITE, (rx+40, cy-4, 60, 28))

# ── HUD ────────────────────────────────────────────────────────────────────────
def draw_hud(surf, score, lives):
    pygame.draw.rect(surf, (0,0,0), (0, 0, WIDTH, 44))
    draw_text(surf, f"SCORE  {score:06d}", font_med, WHITE, 20, 10)
    draw_text(surf, "SUPER MARIO", font_med, COIN_C, WIDTH//2, 10, center=True)
    draw_text(surf, f"LIVES ♥ {lives}", font_med, RED, WIDTH-180, 10)

# ── Screens ────────────────────────────────────────────────────────────────────
def title_screen():
    waiting = True
    t = 0
    while waiting:
        t += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                waiting = False
        screen.fill(SKY)
        pygame.draw.circle(screen, SUN, (WIDTH-100, 80), 50)
        draw_text(screen, "SUPER MARIO BROS", font_big, BLACK, WIDTH//2+2, 152, center=True)
        draw_text(screen, "SUPER MARIO  BROS", font_big, MARIO_R, WIDTH//2, 150, center=True)
        col = WHITE if (t//20)%2 else COIN_C
        draw_text(screen, "PRESS ANY KEY TO START", font_med, col, WIDTH//2, 230, center=True)
        draw_text(screen, "ARROW KEYS / WASD  +  SPACE to jump", font_small, WHITE, WIDTH//2, 290, center=True)
        draw_text(screen, "Stomp enemies from above!", font_small, (200,255,200), WIDTH//2, 320, center=True)
        pygame.display.flip()
        clock.tick(FPS)

def game_over_screen(win, score):
    waiting = True
    t = 0
    while waiting:
        t += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                return
        screen.fill((20,10,40) if not win else (20,60,20))
        msg = "YOU WIN! 🎉" if win else "GAME OVER"
        col = COIN_C if win else RED
        draw_text(screen, msg, font_big, col, WIDTH//2, 180, center=True)
        draw_text(screen, f"SCORE: {score:06d}", font_med, WHITE, WIDTH//2, 240, center=True)
        blink = WHITE if (t//20)%2 else (150,150,150)
        draw_text(screen, "PRESS ANY KEY TO PLAY AGAIN", font_med, blink, WIDTH//2, 300, center=True)
        pygame.display.flip()
        clock.tick(FPS)

# ── Main game loop ─────────────────────────────────────────────────────────────
def run_game():
    tiles, enemies, coins, (px, py), flag = build_level()
    player = Player(px, py)
    cam = Camera()
    score = 0
    lives = 3
    respawn_timer = 0
    coin_count = 0

    running = True
    while running:
        dt = clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return False

        keys = pygame.key.get_pressed()

        # Count coins before
        prev_coins = sum(1 for c in coins if c.collected)

        player.update(keys, tiles, enemies, coins, flag)
        for e in enemies:
            e.update(tiles)
        flag.update()

        # Score for coins
        new_coins = sum(1 for c in coins if c.collected)
        score += (new_coins - prev_coins) * 100

        # Score for stomps
        for e in enemies:
            if e.squish and e.squish_timer == 29:
                score += 200

        # Camera
        cam.update(player.rect.centerx)

        # Respawn
        if not player.alive:
            if respawn_timer == 0:
                respawn_timer = player.dead_timer + 10
            respawn_timer -= 1
            if respawn_timer <= 0:
                lives -= 1
                if lives <= 0:
                    return True   # game over, not win
                tiles, enemies, coins, (px, py), flag = build_level()
                player = Player(px, py)
                cam = Camera()
                respawn_timer = 0

        # Win
        if player.win and player.win_timer > 120:
            return True, True  # signal win

        # ── Draw ──
        draw_bg(screen, cam)

        for t in tiles:
            t.draw(screen, cam)
        for c in coins:
            c.draw(screen, cam)
        flag.draw(screen, cam)
        for e in enemies:
            e.draw(screen, cam)
        player.draw(screen, cam)

        draw_hud(screen, score, lives)

        pygame.display.flip()

    return False, False

# ── Entry ──────────────────────────────────────────────────────────────────────
def main():
    title_screen()
    while True:
        result = run_game()
        win = isinstance(result, tuple) and len(result) > 1 and result[1]
        score_val = 0
        game_over_screen(win, score_val)

if __name__ == "__main__":
    main()