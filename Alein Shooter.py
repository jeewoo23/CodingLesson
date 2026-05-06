import pygame, random, math, sys, json, os

# --- 1. SETUP ---
pygame.init()
WIDTH, HEIGHT = 1100, 850
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("NEON FLEET: V15.2 - 20 SHIPS")
clock = pygame.time.Clock()

SAVE_PATH = "neon_fleet_data.json"
BLUE, RED, GREEN, PURPLE, ORANGE, GOLD = (0, 150, 255), (255, 50, 50), (50, 255, 100), (200, 0, 255), (255, 150, 0), (255, 215, 0)
WHITE, DARK, GRAY = (255, 255, 255), (5, 5, 20), (40, 40, 60)
f_main, f_pts = pygame.font.SysFont("Consolas", 14), pygame.font.SysFont("Impact", 32)

# --- 2. HELPERS ---
def save_game(data):
    try:
        with open(SAVE_PATH, "w") as f:
            json.dump({"pts": data.pts, "wave": data.wave, "unlocked": data.unlocked, "ship_id": data.ship_id}, f)
    except: pass

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, color, dmg, speed=-22):
        super().__init__()
        self.image = pygame.Surface((10, 40), pygame.SRCALPHA)
        pygame.draw.line(self.image, color, (5, 0), (5, 40), 4)
        self.rect = self.image.get_rect(centerx=x, bottom=y)
        self.damage, self.speed = dmg, speed
    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0 or self.rect.top > HEIGHT: self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, wave):
        super().__init__()
        self.hp = 300 + (wave * 120); self.max_hp = self.hp
        self.val = 1500; self.vx = random.uniform(-2, 2)
        self.image = pygame.Surface((60, 60), pygame.SRCALPHA)
        pygame.draw.rect(self.image, RED, (10, 20, 40, 20), 2)
        pygame.draw.polygon(self.image, RED, [(30, 60), (10, 40), (50, 40)], 1)
        self.rect = self.image.get_rect(center=(random.randint(100, WIDTH-100), random.randint(-600, -50)))
        self.stunned = 0
    def update(self, rockets):
        if self.stunned > 0: self.stunned -= 1; return
        self.rect.x += self.vx
        if self.rect.y < 200: self.rect.y += 2
        if self.rect.left < 50 or self.rect.right > WIDTH-50: self.vx *= -1
        if random.random() < 0.005: rockets.add(Projectile(self.rect.centerx, self.rect.bottom, RED, 10, 8))
    def draw_hp(self, surf):
        pygame.draw.rect(surf, GRAY, (self.rect.x, self.rect.y - 10, 60, 6))
        pygame.draw.rect(surf, RED, (self.rect.x, self.rect.y - 10, (self.hp/self.max_hp)*60, 6))

class GameData:
    def __init__(self):
        self.pts, self.state, self.wave, self.hp = 0, "HOME", 1, 100
        self.ship_id, self.ls, self.abi_cd = "STARTER", 0, 0
        self.abi_name, self.abi_timer, self.shake = "", 0, 0
        self.names = ["STARTER", "SABRE", "LONG NIGHT", "PILLAR", "SPIRIT", "VANGUARD", "RELIANT", "ORION", "DAEDALUS", "INFINITY", "SERENITY", "ENTERPRISE", "NORMANDY", "ISHIMURA", "BEBOP", "GALACTICA", "RAZORBACK", "ROCINANTE", "SULAKO", "PROMETHEUS"]
        self.abis = ["FLARE", "DASH", "CLOAK", "REPAIR", "WALL", "DOUBLE", "STUN", "VOLLEY", "WINGS", "SHOCK", "LEAF", "WARP", "OVERLOAD", "MAGNET", "JAZZ", "FLAK", "G-FORCE", "PDC", "NUKE", "TURRET"]
        self.unlocked = {n: (n == "STARTER") for n in self.names}
        self.ships = {}
        for i, n in enumerate(self.names):
            # Procedural textures for 20 ships
            surf = pygame.Surface((70, 70), pygame.SRCALPHA)
            color = [BLUE, GREEN, PURPLE, GOLD, ORANGE][i % 5]
            pts = [(35, 10), (10, 60), (35, 45), (60, 60)] # Base ship
            if i > 5: pts = [(35, 5), (5, 40), (15, 65), (55, 65), (65, 40)] # Heavy ship
            if i > 12: pts = [(35, 0), (0, 30), (10, 70), (35, 50), (60, 70), (70, 30)] # Titan ship
            pygame.draw.polygon(surf, color, pts, 2)
            
            self.ships[n] = {
                "dmg": 40 + (i * 20), "rate": 300 - (i * 10), "cost": int(5000 * (1.35**i)), 
                "c": color, "abi": self.abis[i], "img": surf
            }
        self.stars = [[random.randint(0, WIDTH), random.randint(0, HEIGHT), random.uniform(1, 4)] for _ in range(80)]

data = GameData()
aliens, bullets, rockets = pygame.sprite.Group(), pygame.sprite.Group(), pygame.sprite.Group()

def draw_btn(txt, x, y, w, h, c, clicked):
    r = pygame.Rect(x, y, w, h); hov = r.collidepoint(pygame.mouse.get_pos())
    pygame.draw.rect(screen, WHITE if hov else c, r, 2)
    t = f_main.render(txt, True, WHITE); screen.blit(t, (x+(w-t.get_width())//2, y+(h-t.get_height())//2))
    return hov and clicked

# --- 3. MAIN LOOP ---
px, py = WIDTH//2, HEIGHT-100
while True:
    now = pygame.time.get_ticks()
    clicked = False
    offset = [random.randint(-data.shake, data.shake) for _ in range(2)] if data.shake > 0 else [0,0]
    if data.shake > 0: data.shake -= 1

    screen.fill(DARK)
    for event in pygame.event.get():
        if event.type == pygame.QUIT: save_game(data); pygame.quit(); sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN: clicked = True
        if event.type == pygame.KEYDOWN and event.key == pygame.K_LSHIFT:
            if now > data.abi_cd:
                data.shake = 15; data.abi_timer = now + 1200
                sc = data.ships[data.ship_id]; data.abi_name = sc["abi"]
                if sc["abi"] == "FLARE": rockets.empty()
                if sc["abi"] == "STUN": [setattr(a, 'stunned', 180) for a in aliens]
                if sc["abi"] == "REPAIR": data.hp = min(100, data.hp + 30)
                if sc["abi"] == "NUKE": [setattr(a, 'hp', a.hp - 1000) for a in aliens]
                data.abi_cd = now + 6000

    for s in data.stars:
        s[1] += s[2]; screen.set_at((int(s[0]), int(s[1])), (100, 100, 100))
        if s[1] > HEIGHT: s[1], s[0] = 0, random.randint(0, WIDTH)

    if data.state == "HOME":
        screen.blit(f_pts.render("NEON FLEET: MASTERY", True, WHITE), (WIDTH//2-140, 250))
        if draw_btn("ENGAGE", 450, 350, 200, 50, GREEN, clicked):
            data.state, data.hp = "FIGHT", 100
            aliens.empty(); [aliens.add(Enemy(data.wave)) for _ in range(5 + data.wave)]
        if draw_btn("HANGAR", 450, 420, 200, 50, BLUE, clicked): data.state = "HANGAR"

    elif data.state == "HANGAR":
        sy = 40
        for i, n in enumerate(data.names):
            sc = data.ships[n]
            # Column 1 (0-9) Column 2 (10-19)
            bx = 100 if i < 10 else 600
            by = sy + (i % 10) * 70
            if not data.unlocked[n]:
                if draw_btn(f"BUY {n} (${sc['cost']:,})", bx, by, 400, 35, GOLD, clicked) and data.pts >= sc['cost']:
                    data.pts -= sc['cost']; data.unlocked[n] = True
            else:
                c = GREEN if data.ship_id == n else BLUE
                if draw_btn(f"USE {n} [{sc['abi']}]", bx, by, 400, 35, c, clicked): data.ship_id = n
        if draw_btn("EXIT", 450, 780, 200, 40, RED, clicked): data.state = "HOME"

    elif data.state == "FIGHT":
        k = pygame.key.get_pressed()
        px = max(50, min(WIDTH-50, px + (k[pygame.K_RIGHT] - k[pygame.K_LEFT]) * 12))
        sc = data.ships[data.ship_id]
        if k[pygame.K_SPACE] and now - data.ls > sc['rate']:
            bullets.add(Projectile(px, py-30, sc['c'], sc['dmg'])); data.ls = now

        aliens.update(rockets); bullets.update(); rockets.update()
        for b in bullets:
            hits = pygame.sprite.spritecollide(b, aliens, False)
            for a in hits:
                a.hp -= b.damage; b.kill()
                if a.hp <= 0: data.pts += a.val; a.kill()
        
        for r in rockets:
            if r.rect.colliderect(pygame.Rect(px-25, py-25, 50, 50)): data.hp -= 15; r.kill(); data.shake = 10
        
        if len(aliens) == 0: data.wave += 1; data.state = "HOME"
        if data.hp <= 0: data.state, data.wave = "HOME", 1

        screen.blit(sc['img'], (px-35+offset[0], py-35+offset[1]))
        bullets.draw(screen); rockets.draw(screen)
        for a in aliens: a.draw_hp(screen); screen.blit(a.image, a.rect)
        
        pygame.draw.rect(screen, GRAY, (WIDTH//2-100, HEIGHT-40, 200, 12))
        pygame.draw.rect(screen, GREEN, (WIDTH//2-100, HEIGHT-40, data.hp*2, 12))
        if now < data.abi_timer:
            m = f_pts.render(data.abi_name, True, GOLD)
            screen.blit(m, (WIDTH//2-m.get_width()//2, HEIGHT//2))

    screen.blit(f_pts.render(f"${data.pts:,}", True, GOLD), (20, 20))
    pygame.display.flip(); clock.tick(60)
