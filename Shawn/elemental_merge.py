"""
╔══════════════════════════════════════════════════╗
║           E L E M E N T A L   M E R G E          ║
║  Drop elements — match two of the same to merge  ║
║  into the next element.  How high can you go?    ║
╚══════════════════════════════════════════════════╝

Controls
────────
  Mouse move   → aim drop position
  Left click   → drop current element
  R            → restart
  ESC          → quit

Requirements: pip install pygame
Run:          python elemental_merge.py
"""

import pygame
import math
import random
import sys

# ── Bootstrap ─────────────────────────────────────────────────────────────────
pygame.init()

# ── Layout constants ──────────────────────────────────────────────────────────
SW, SH       = 640, 760          # screen size
GX, GY       = 10, 120           # game area origin
GW, GH       = 400, 600          # game area size
WALL         = 5                 # wall / floor thickness
DANGER_Y     = GY + 55           # balls above this line → game-over check

# Right-panel geometry
PX           = GX + GW + 10      # panel x
PW           = SW - PX - 8       # panel width

FPS          = 60
GRAVITY      = 0.38
DAMPING      = 0.42              # energy kept on floor/wall bounce
FRICTION     = 0.988             # per-frame horizontal friction

# ── Element table ─────────────────────────────────────────────────────────────
# (name, radius, body_color, icon_emoji_fallback, score_value)
ELEMENTS = [
    ("Spark",    18, (255, 220,  45), "✦",   1),
    ("Ember",    24, (255, 145,  30), "🔥",   3),
    ("Fire",     30, (255,  55,  20), "🔥",   6),
    ("Steam",    37, (200, 205, 255), "💨",  10),
    ("Cloud",    44, (170, 185, 230), "☁",  15),
    ("Water",    51, ( 30, 130, 255), "💧",  21),
    ("Ice",      58, (155, 235, 255), "❄",  28),
    ("Earth",    65, ( 85, 165,  60), "🌍",  36),
    ("Lava",     72, (225,  70,  20), "🌋",  45),
    ("Crystal",  79, (205,  90, 255), "💎",  55),
    ("Cosmos",   88, ( 55,  10, 210), "🌌", 100),
]
MAX_IDX = len(ELEMENTS) - 1

# Max index that can be spawned at the top (only small elements drop in)
MAX_SPAWN = 4

# ── Palette ───────────────────────────────────────────────────────────────────
BG_COL      = (11, 13, 26)
PANEL_COL   = (19, 23, 42)
WALL_COL    = (55, 65, 110)
DANGER_COL  = (120,  20,  20)
TEXT_COL    = (215, 220, 255)
SCORE_COL   = (255, 215,  50)
BEST_COL    = (200, 175,  90)
MERGE_COL   = (255, 255, 100)
GUIDE_COL   = (55,  65, 100)
OVER_COL    = (255,  70,  70)
BTN_COL     = ( 60,  80, 160)
BTN_HOV     = ( 90, 120, 210)

# ── Fonts ─────────────────────────────────────────────────────────────────────
F_XL  = pygame.font.SysFont("Segoe UI", 36, bold=True)
F_LG  = pygame.font.SysFont("Segoe UI", 26, bold=True)
F_MD  = pygame.font.SysFont("Segoe UI", 18, bold=True)
F_SM  = pygame.font.SysFont("Segoe UI", 13)
F_XS  = pygame.font.SysFont("Segoe UI", 11)

screen = pygame.display.set_mode((SW, SH))
pygame.display.set_caption("Elemental Merge")
clock  = pygame.time.Clock()

# ── Helper ────────────────────────────────────────────────────────────────────

def lerp_color(a, b, t):
    return tuple(int(a[i] + (b[i]-a[i])*t) for i in range(3))

def draw_glow(surf, color, cx, cy, radius, strength=60):
    for step in range(3, 0, -1):
        r = radius + step * 5
        alpha = strength // step
        s = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*color[:3], alpha), (r, r), r)
        surf.blit(s, (cx - r, cy - r), special_flags=pygame.BLEND_RGBA_ADD)

def draw_circle_3d(surf, color, cx, cy, radius, border=2):
    """Draw a circle with a subtle 3-D shading effect."""
    pygame.draw.circle(surf, color, (cx, cy), radius)
    # bright top-left highlight
    hi_col = tuple(min(255, c + 70) for c in color)
    pygame.draw.circle(surf, hi_col,
                       (cx - radius//4, cy - radius//4),
                       max(3, radius // 3))
    # dark border
    dk_col = tuple(max(0, c - 55) for c in color)
    pygame.draw.circle(surf, dk_col, (cx, cy), radius, border)

# ── Particle ──────────────────────────────────────────────────────────────────

class Particle:
    __slots__ = ("x", "y", "vx", "vy", "life", "color", "size")

    def __init__(self, x, y, color):
        self.x, self.y = float(x), float(y)
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(0.8, 4.5)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life  = 1.0
        self.color = color
        self.size  = random.randint(2, 6)

    def update(self):
        self.x   += self.vx
        self.y   += self.vy
        self.vy  += 0.12
        self.vx  *= 0.96
        self.life -= 0.045
        return self.life > 0

    def draw(self, surf):
        col = tuple(min(255, c + 80) for c in self.color)
        r = max(1, int(self.size * self.life))
        pygame.draw.circle(surf, col, (int(self.x), int(self.y)), r)

# ── Ball ──────────────────────────────────────────────────────────────────────

class Ball:
    def __init__(self, x, y, idx):
        self.x   = float(x)
        self.y   = float(y)
        self.vx  = 0.0
        self.vy  = 0.0
        self.idx = idx
        name, self.r, self.color, _, self.pts = ELEMENTS[idx]
        self.name        = name
        self.flash       = 0     # merge-flash timer (frames)
        self.age         = 0     # frames alive (skip early collisions)

    # ── physics step ─────────────────────────────────────────────────────────
    def update(self):
        self.vy = min(self.vy + GRAVITY, 20)
        self.x += self.vx
        self.y += self.vy
        self.vx *= FRICTION
        self.age += 1
        if self.flash > 0:
            self.flash -= 1

        # Floor
        floor = GY + GH - self.r
        if self.y >= floor:
            self.y   = floor
            self.vy *= -DAMPING
            self.vx *= 0.82
            if abs(self.vy) < 0.5:
                self.vy = 0

        # Left / right walls
        l = GX + WALL + self.r
        r = GX + GW - WALL - self.r
        if self.x < l:
            self.x   = l
            self.vx *= -0.45
        elif self.x > r:
            self.x   = r
            self.vx *= -0.45

    # ── drawing ──────────────────────────────────────────────────────────────
    def draw(self, surf):
        cx, cy = int(self.x), int(self.y)
        col = self.color

        # Glow for high-tier elements
        if self.idx >= 7:
            draw_glow(surf, col, cx, cy, self.r, strength=50)

        # Flash white on merge
        if self.flash > 0:
            t = self.flash / 12
            col = lerp_color(self.color, (255, 255, 255), t * 0.7)

        draw_circle_3d(surf, col, cx, cy, self.r)

        # Element name label
        lbl = F_XS.render(self.name, True, (255, 255, 255))
        surf.blit(lbl, (cx - lbl.get_width()//2, cy - lbl.get_height()//2))

# ── Floating score popup ──────────────────────────────────────────────────────

class ScorePop:
    def __init__(self, text, x, y):
        self.text  = text
        self.x     = float(x)
        self.y     = float(y)
        self.timer = 55

    def update(self):
        self.y     -= 0.7
        self.timer -= 1
        return self.timer > 0

    def draw(self, surf):
        alpha = min(255, self.timer * 5)
        col   = tuple(int(MERGE_COL[i] * alpha / 255) for i in range(3))
        t = F_MD.render(self.text, True, col)
        surf.blit(t, (int(self.x) - t.get_width()//2, int(self.y)))

# ── Main game ─────────────────────────────────────────────────────────────────

class Game:
    def __init__(self):
        self.high_score = 0
        self.reset()

    def reset(self):
        self.balls       : list[Ball]      = []
        self.particles   : list[Particle]  = []
        self.pops        : list[ScorePop]  = []
        self.score       = 0
        self.over        = False
        self.cooldown    = 0          # frames until next drop allowed
        self.aim_x       = GX + GW//2
        # First two elements
        self.cur  = random.randint(0, MAX_SPAWN)
        self.nxt  = random.randint(0, MAX_SPAWN)

    # ── drop ─────────────────────────────────────────────────────────────────
    def drop(self, mouse_x):
        if self.cooldown > 0 or self.over:
            return
        r   = ELEMENTS[self.cur][1]
        x   = max(GX + WALL + r, min(mouse_x, GX + GW - WALL - r))
        b   = Ball(x, GY + r + 2, self.cur)
        b.vy = 3.0
        self.balls.append(b)
        self.cur      = self.nxt
        self.nxt      = random.randint(0, MAX_SPAWN)
        self.cooldown = 32

    # ── collision + merge ─────────────────────────────────────────────────────
    def _collide(self):
        balls     = self.balls
        n         = len(balls)
        dead      = set()
        new_balls = []

        for i in range(n):
            for j in range(i + 1, n):
                if i in dead or j in dead:
                    continue
                a, b   = balls[i], balls[j]
                dx     = b.x - a.x
                dy     = b.y - a.y
                dist   = math.hypot(dx, dy) or 1e-6
                min_d  = a.r + b.r

                if dist >= min_d:
                    continue

                # ── Merge ────────────────────────────────────────────────────
                if a.idx == b.idx and a.idx < MAX_IDX and a.age > 8 and b.age > 8:
                    dead.add(i)
                    dead.add(j)
                    mx, my    = (a.x + b.x) / 2, (a.y + b.y) / 2
                    nb        = Ball(mx, my, a.idx + 1)
                    nb.vx     = (a.vx + b.vx) * 0.25
                    nb.vy     = (a.vy + b.vy) * 0.25 - 1.5
                    nb.flash  = 12
                    new_balls.append(nb)

                    pts = ELEMENTS[a.idx + 1][4]
                    self.score     += pts
                    self.high_score = max(self.high_score, self.score)

                    for _ in range(14):
                        self.particles.append(Particle(mx, my, ELEMENTS[a.idx+1][2]))
                    self.pops.append(ScorePop(f"+{pts}", mx, my - nb.r - 8))

                # ── Push-apart ───────────────────────────────────────────────
                else:
                    nx, ny  = dx / dist, dy / dist
                    overlap = (min_d - dist) * 0.52
                    a.x -= nx * overlap
                    a.y -= ny * overlap
                    b.x += nx * overlap
                    b.y += ny * overlap

                    # Elastic impulse
                    rel  = (a.vx - b.vx) * nx + (a.vy - b.vy) * ny
                    if rel > 0:
                        imp  = rel * 0.48
                        a.vx -= imp * nx;  a.vy -= imp * ny
                        b.vx += imp * nx;  b.vy += imp * ny

        self.balls = [b for i, b in enumerate(balls) if i not in dead] + new_balls

    # ── game-over check ───────────────────────────────────────────────────────
    def _check_over(self):
        for b in self.balls:
            if b.y - b.r < DANGER_Y and abs(b.vy) < 0.4 and abs(b.vx) < 0.4:
                self.over = True
                return

    # ── update ───────────────────────────────────────────────────────────────
    def update(self):
        if self.over:
            return
        if self.cooldown > 0:
            self.cooldown -= 1

        for b in self.balls:
            b.update()

        # Multiple collision passes for stability
        for _ in range(4):
            self._collide()

        self.particles = [p for p in self.particles if p.update()]
        self.pops      = [p for p in self.pops      if p.update()]
        self._check_over()

    # ── draw ─────────────────────────────────────────────────────────────────
    def draw(self, mouse_x):
        screen.fill(BG_COL)
        self._draw_header()
        self._draw_right_panel()
        self._draw_game_area(mouse_x)
        if self.over:
            self._draw_game_over()
        pygame.display.flip()

    # ── header (score bar) ────────────────────────────────────────────────────
    def _draw_header(self):
        pygame.draw.rect(screen, PANEL_COL, (0, 0, SW, GY - 4))
        pygame.draw.line(screen, WALL_COL, (0, GY - 4), (SW, GY - 4), 2)

        # Title
        title = F_LG.render("ELEMENTAL MERGE", True, (200, 180, 255))
        screen.blit(title, (GX, 10))

        # Score
        sc_lbl = F_SM.render("SCORE", True, TEXT_COL)
        screen.blit(sc_lbl, (GX, 50))
        sc_val = F_XL.render(str(self.score), True, SCORE_COL)
        screen.blit(sc_val, (GX, 63))

        # Best
        bs_lbl = F_SM.render("BEST", True, TEXT_COL)
        screen.blit(bs_lbl, (GX + 160, 50))
        bs_val = F_LG.render(str(self.high_score), True, BEST_COL)
        screen.blit(bs_val, (GX + 160, 63))

        # Next element preview
        nxt_lbl = F_SM.render("NEXT", True, TEXT_COL)
        screen.blit(nxt_lbl, (GX + 310, 15))
        name, nr, nc, _, _ = ELEMENTS[self.nxt]
        draw_circle_3d(screen, nc, GX + 310 + nr + 6, GY - 28, nr)
        nl = F_XS.render(name, True, (255,255,255))
        screen.blit(nl, (GX + 310 + nr + 6 - nl.get_width()//2,
                         GY - 28 - nl.get_height()//2))

    # ── right panel ──────────────────────────────────────────────────────────
    def _draw_right_panel(self):
        pygame.draw.rect(screen, PANEL_COL, (PX, GY, PW, GH))
        pygame.draw.rect(screen, WALL_COL,  (PX, GY, PW, GH), 2)

        hdr = F_SM.render("ELEMENTS", True, TEXT_COL)
        screen.blit(hdr, (PX + PW//2 - hdr.get_width()//2, GY + 8))

        row_h = (GH - 30) // len(ELEMENTS)
        for i, (name, r, color, _, pts) in enumerate(ELEMENTS):
            ry = GY + 28 + i * row_h
            cx = PX + 18
            rr = min(r, 14)
            draw_circle_3d(screen, color, cx, ry + rr, rr, border=1)
            nt = F_XS.render(name, True, TEXT_COL)
            screen.blit(nt, (PX + 36, ry + rr - nt.get_height()//2))
            pt = F_XS.render(f"+{pts}", True, SCORE_COL)
            screen.blit(pt, (PX + PW - pt.get_width() - 4,
                             ry + rr - pt.get_height()//2))

        # Controls hint
        hint_y = GY + GH + 8
        for line in ["[Click] Drop", "[R] Restart", "[ESC] Quit"]:
            t = F_XS.render(line, True, (120, 130, 170))
            screen.blit(t, (PX + 4, hint_y))
            hint_y += 14

    # ── game area ─────────────────────────────────────────────────────────────
    def _draw_game_area(self, mouse_x):
        # Background
        pygame.draw.rect(screen, (18, 21, 38),
                         (GX, GY, GW, GH))

        # Danger line
        pygame.draw.line(screen, DANGER_COL,
                         (GX + WALL, DANGER_Y),
                         (GX + GW - WALL, DANGER_Y), 1)
        dlbl = F_XS.render("DANGER", True, DANGER_COL)
        screen.blit(dlbl, (GX + WALL + 4, DANGER_Y - 13))

        # Balls
        for b in self.balls:
            b.draw(screen)

        # Particles
        for p in self.particles:
            p.draw(screen)

        # Score pops
        for pop in self.pops:
            pop.draw(screen)

        # Drop guide + preview
        if not self.over and self.cooldown == 0:
            r  = ELEMENTS[self.cur][1]
            ax = max(GX + WALL + r, min(mouse_x, GX + GW - WALL - r))
            # Dashed guide line
            y = GY + WALL
            while y < GY + GH - WALL:
                pygame.draw.line(screen, GUIDE_COL,
                                 (ax, y), (ax, min(y + 9, GY + GH - WALL)), 1)
                y += 16
            # Ghost ball at top
            col = ELEMENTS[self.cur][2]
            draw_circle_3d(screen, col, ax, GY - r - 4, r, border=1)
            gl = F_XS.render(ELEMENTS[self.cur][0], True, (255,255,255))
            screen.blit(gl, (ax - gl.get_width()//2, GY - r - 4 - gl.get_height()//2))

        # Border last (draws over any overflow)
        pygame.draw.rect(screen, WALL_COL, (GX, GY, GW, GH), WALL)

    # ── game-over overlay ─────────────────────────────────────────────────────
    def _draw_game_over(self):
        ov = pygame.Surface((GW, GH), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 175))
        screen.blit(ov, (GX, GY))

        cy = GY + GH // 2
        t1 = F_XL.render("GAME OVER", True, OVER_COL)
        screen.blit(t1, (GX + GW//2 - t1.get_width()//2, cy - 70))

        t2 = F_LG.render(f"Score: {self.score}", True, SCORE_COL)
        screen.blit(t2, (GX + GW//2 - t2.get_width()//2, cy - 15))

        t3 = F_MD.render(f"Best:  {self.high_score}", True, BEST_COL)
        screen.blit(t3, (GX + GW//2 - t3.get_width()//2, cy + 25))

        # Restart button
        btn = pygame.Rect(GX + GW//2 - 70, cy + 70, 140, 40)
        mpos = pygame.mouse.get_pos()
        col  = BTN_HOV if btn.collidepoint(mpos) else BTN_COL
        pygame.draw.rect(screen, col, btn, border_radius=8)
        rt = F_MD.render("RESTART  [R]", True, (220, 230, 255))
        screen.blit(rt, (btn.centerx - rt.get_width()//2,
                         btn.centery - rt.get_height()//2))

# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    game = Game()

    while True:
        mouse_x = pygame.mouse.get_pos()[0]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_r:
                    game.reset()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if game.over:
                    # Click on restart button
                    btn = pygame.Rect(GX + GW//2 - 70,
                                      GY + GH//2 + 70, 140, 40)
                    if btn.collidepoint(event.pos):
                        game.reset()
                else:
                    game.drop(event.pos[0])

        game.update()
        game.draw(mouse_x)
        clock.tick(FPS)


if __name__ == "__main__":
    main()
