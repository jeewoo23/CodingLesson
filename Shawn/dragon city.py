#!/usr/bin/env python3
"""
Dragon City  -  Pygame Edition
Run with:  python dragon_city_pygame.py
Requires:  pip install pygame
"""

import pygame, sys, json, os, random, math
from dataclasses import dataclass, field, asdict
from typing import Optional, Callable

pygame.init()

# ───────────────────────────────────────────────
#  WINDOW & FPS
# ───────────────────────────────────────────────
W, H   = 960, 640
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Dragon City")
clock  = pygame.time.Clock()
FPS    = 60
SAVE_FILE = "dragon_city_save.json"

# ───────────────────────────────────────────────
#  COLOURS
# ───────────────────────────────────────────────
BG      = ( 12,   8,  22)
PANEL   = ( 22,  16,  38)
CARD    = ( 30,  22,  50)
BORDER  = ( 60,  45,  90)
GOLD    = (255, 200,  50)
WHITE   = (235, 228, 255)
LGRAY   = (170, 160, 190)
GRAY    = (110, 100, 130)
DGRAY   = ( 55,  48,  72)
RED     = (220,  60,  50)
GREEN   = ( 60, 200, 100)
BLUE    = ( 70, 130, 225)
PURPLE  = (120,  60, 200)
ORANGE  = (255, 140,  30)
CYAN    = ( 80, 210, 220)
YELLOW  = (255, 220,  60)
DARK_RED= (140,  30,  20)

ELEM_C = {
    "Fire":     (220,  80,  40),
    "Water":    ( 60, 130, 220),
    "Nature":   ( 70, 190,  80),
    "Electric": (240, 210,  40),
    "Ice":      (100, 210, 240),
    "Terra":    (190, 130,  60),
    "Dark":     (130,  70, 200),
    "Light":    (240, 225, 120),
    "Metal":    (160, 160, 180),
    "Dragon":   (220,  50,  80),
}

RARITY_C = {
    "Common":    (180, 175, 195),
    "Uncommon":  ( 70, 200, 100),
    "Rare":      ( 70, 130, 230),
    "Epic":      (160,  80, 230),
    "Legendary": (255, 200,  50),
}

# ───────────────────────────────────────────────
#  FONTS
# ───────────────────────────────────────────────
F_TITLE = pygame.font.SysFont("Georgia",    38, bold=True)
F_H1    = pygame.font.SysFont("Georgia",    26, bold=True)
F_H2    = pygame.font.SysFont("Verdana",    19, bold=True)
F_BODY  = pygame.font.SysFont("Verdana",    15)
F_SMALL = pygame.font.SysFont("Verdana",    12)
F_TINY  = pygame.font.SysFont("Verdana",    11)

# ───────────────────────────────────────────────
#  GAME DATA
# ───────────────────────────────────────────────
ELEMENTS = {
    "Fire":     {"strong": ["Nature","Ice"],       "weak": ["Water","Terra"]},
    "Water":    {"strong": ["Fire","Terra"],        "weak": ["Nature","Electric"]},
    "Nature":   {"strong": ["Water","Terra"],       "weak": ["Fire","Ice"]},
    "Electric": {"strong": ["Water","Metal"],       "weak": ["Terra","Dark"]},
    "Ice":      {"strong": ["Nature","Water"],      "weak": ["Fire","Metal"]},
    "Terra":    {"strong": ["Electric","Fire"],     "weak": ["Water","Nature"]},
    "Dark":     {"strong": ["Electric","Light"],    "weak": ["Light","Fire"]},
    "Light":    {"strong": ["Dark","Ice"],          "weak": ["Dark","Electric"]},
    "Metal":    {"strong": ["Ice","Light"],         "weak": ["Electric","Fire"]},
    "Dragon":   {"strong": ["Dragon"],              "weak": ["Dragon"]},
}

DRAGONS = {
    "Flamejet":    {"elems":["Fire"],             "rarity":"Common",    "hp":100,"atk":30,"df":15},
    "Aqua":        {"elems":["Water"],            "rarity":"Common",    "hp":110,"atk":25,"df":20},
    "Treeling":    {"elems":["Nature"],           "rarity":"Common",    "hp":105,"atk":27,"df":18},
    "Sparky":      {"elems":["Electric"],         "rarity":"Common",    "hp": 95,"atk":35,"df":12},
    "Frosty":      {"elems":["Ice"],              "rarity":"Common",    "hp":100,"atk":28,"df":20},
    "Rocko":       {"elems":["Terra"],            "rarity":"Common",    "hp":120,"atk":22,"df":25},
    "Steamwing":   {"elems":["Fire","Water"],     "rarity":"Uncommon",  "hp":130,"atk":40,"df":25},
    "Thornfire":   {"elems":["Fire","Nature"],    "rarity":"Uncommon",  "hp":125,"atk":42,"df":22},
    "Voltfin":     {"elems":["Electric","Water"], "rarity":"Uncommon",  "hp":128,"atk":45,"df":20},
    "Glacierback": {"elems":["Ice","Terra"],      "rarity":"Uncommon",  "hp":140,"atk":35,"df":30},
    "Shadowleaf":  {"elems":["Dark","Nature"],    "rarity":"Uncommon",  "hp":122,"atk":48,"df":18},
    "Sunbeam":     {"elems":["Light","Fire"],     "rarity":"Uncommon",  "hp":126,"atk":44,"df":24},
    "Stormdrake":  {"elems":["Electric","Dark"],  "rarity":"Rare",      "hp":160,"atk":60,"df":35},
    "Ironscale":   {"elems":["Metal","Terra"],    "rarity":"Rare",      "hp":175,"atk":50,"df":50},
    "Abyssfire":   {"elems":["Dark","Fire"],      "rarity":"Rare",      "hp":155,"atk":65,"df":30},
    "Frozenlight": {"elems":["Ice","Light"],      "rarity":"Rare",      "hp":158,"atk":58,"df":38},
    "Galaxywing":  {"elems":["Dragon","Dark"],    "rarity":"Epic",      "hp":220,"atk":85,"df":55},
    "Titanflame":  {"elems":["Dragon","Fire"],    "rarity":"Epic",      "hp":230,"atk":90,"df":50},
    "Draco Prime": {"elems":["Dragon"],           "rarity":"Legendary", "hp":300,"atk":110,"df":70},
}

BREEDING = {
    frozenset(["Fire","Water"]):     "Steamwing",
    frozenset(["Fire","Nature"]):    "Thornfire",
    frozenset(["Electric","Water"]): "Voltfin",
    frozenset(["Ice","Terra"]):      "Glacierback",
    frozenset(["Dark","Nature"]):    "Shadowleaf",
    frozenset(["Light","Fire"]):     "Sunbeam",
    frozenset(["Electric","Dark"]):  "Stormdrake",
    frozenset(["Metal","Terra"]):    "Ironscale",
    frozenset(["Dark","Fire"]):      "Abyssfire",
    frozenset(["Ice","Light"]):      "Frozenlight",
    frozenset(["Dragon","Dark"]):    "Galaxywing",
    frozenset(["Dragon","Fire"]):    "Titanflame",
}

SHOP_ITEMS = [
    ("Flamejet",   80),  ("Aqua",       80),  ("Treeling",   80),
    ("Sparky",     90),  ("Frosty",     90),  ("Rocko",      90),
    ("Stormdrake", 300), ("Ironscale",  350), ("Draco Prime",800),
]

ARENAS = [
    {"name":"Beginner's Isle",   "min_lv":1,  "pool":["Flamejet","Aqua","Treeling"],          "gold_mult":1.0},
    {"name":"Warrior's Plateau", "min_lv":3,  "pool":["Sparky","Frosty","Steamwing"],          "gold_mult":1.5},
    {"name":"Champion's Summit", "min_lv":6,  "pool":["Stormdrake","Ironscale","Abyssfire"],   "gold_mult":2.5},
    {"name":"Legendary Lair",    "min_lv":10, "pool":["Galaxywing","Titanflame","Draco Prime"],"gold_mult":4.0},
]

# ───────────────────────────────────────────────
#  DATA CLASSES
# ───────────────────────────────────────────────
@dataclass
class Dragon:
    name: str
    template: str
    level: int = 1
    xp: int = 0
    hp: int = 0
    max_hp: int = 0

    def __post_init__(self):
        if self.max_hp == 0:
            self.recalc()

    def recalc(self):
        m = 1 + (self.level-1)*0.12
        self.max_hp = int(DRAGONS[self.template]["hp"] * m)
        self.hp = self.max_hp

    @property
    def atk(self): return int(DRAGONS[self.template]["atk"] * (1+(self.level-1)*0.10))
    @property
    def df(self):  return int(DRAGONS[self.template]["df"]  * (1+(self.level-1)*0.10))
    @property
    def elements(self): return DRAGONS[self.template]["elems"]
    @property
    def rarity(self):   return DRAGONS[self.template]["rarity"]
    @property
    def primary_elem(self): return self.elements[0]
    def xp_need(self): return self.level * 50
    def is_alive(self): return self.hp > 0

    def add_xp(self, amt):
        self.xp += amt
        leveled = False
        while self.xp >= self.xp_need() and self.level < 20:
            self.xp -= self.xp_need()
            self.level += 1
            self.recalc()
            leveled = True
        return leveled

@dataclass
class GameState:
    player_name: str = "Trainer"
    gold: int = 500
    gems: int = 10
    dragons: list = field(default_factory=list)
    breeding_slots: list = field(default_factory=list)
    day: int = 1
    battles_won: int = 0
    habitats: dict = field(default_factory=lambda: {"Fire":1,"Water":1,"Nature":1})

    def save(self):
        d = asdict(self)
        d["dragons"] = [asdict(dr) for dr in self.dragons]
        with open(SAVE_FILE,"w") as f: json.dump(d,f,indent=2)

    @staticmethod
    def load():
        if not os.path.exists(SAVE_FILE): return None
        try:
            with open(SAVE_FILE) as f: d = json.load(f)
            gs = GameState(
                player_name = d.get("player_name","Trainer"),
                gold        = d.get("gold",500),
                gems        = d.get("gems",10),
                breeding_slots = d.get("breeding_slots",[]),
                day         = d.get("day",1),
                battles_won = d.get("battles_won",0),
                habitats    = d.get("habitats",{"Fire":1,"Water":1,"Nature":1}),
            )
            gs.dragons = []
            for dr in d.get("dragons",[]):
                try:
                    known = {k:dr[k] for k in ("name","template","level","xp","hp","max_hp") if k in dr}
                    gs.dragons.append(Dragon(**known))
                except Exception: pass
            return gs
        except Exception: return None

# ───────────────────────────────────────────────
#  UI HELPERS
# ───────────────────────────────────────────────
def rrect(surf, color, rect, r=10, border=0, border_color=None):
    pygame.draw.rect(surf, color, rect, border_radius=r)
    if border and border_color:
        pygame.draw.rect(surf, border_color, rect, border, border_radius=r)

def txt(surf, text, x, y, font=F_BODY, color=WHITE, anchor="topleft"):
    s = font.render(str(text), True, color)
    r = s.get_rect()
    setattr(r, anchor, (x, y))
    surf.blit(s, r)
    return r

def hbar(surf, x, y, w, h, val, maxval, col_full=GREEN, col_empty=DGRAY):
    pygame.draw.rect(surf, col_empty, (x,y,w,h), border_radius=4)
    if maxval > 0:
        filled = max(0, int(w * val / maxval))
        if filled > 0:
            pygame.draw.rect(surf, col_full, (x,y,filled,h), border_radius=4)

def elem_badge(surf, x, y, elem, size=18):
    c = ELEM_C.get(elem, GRAY)
    pygame.draw.circle(surf, c, (x+size//2, y+size//2), size//2)
    pygame.draw.circle(surf, WHITE, (x+size//2, y+size//2), size//2, 1)
    s = F_TINY.render(elem[:3], True, WHITE)
    surf.blit(s, s.get_rect(center=(x+size//2, y+size//2)))

def star_row(surf, x, y, rarity):
    n = {"Common":1,"Uncommon":2,"Rare":3,"Epic":4,"Legendary":5}[rarity]
    c = RARITY_C[rarity]
    for i in range(5):
        col = c if i < n else DGRAY
        txt(surf, "★", x+i*14, y, F_SMALL, col)

def _pc(base, delta):
    return tuple(max(0, min(255, v + delta)) for v in base)

def _blend(a, b, t):
    return tuple(int(a[i]*(1-t)+b[i]*t) for i in range(3))

def draw_dragon_shape(surf, cx, cy, size, elem, level=1):
    """
    High-quality front-facing dragon.
    Layers: glow → tail → wings (membrane + spars + claws) →
            body (scales) → neck → head → snout+teeth → horns+crest →
            legs+claws → eyes → element VFX → outline pass → level badge.
    """
    s  = size
    c  = ELEM_C.get(elem, GRAY)
    cd = _pc(c, -80)    # dark shade
    cm = _pc(c, -35)    # mid shade
    cl = _pc(c,  75)    # light shade
    cb = _blend(c, (240,230,210), 0.55)  # warm belly
    cw = _pc(c, 110)    # wing highlight / horn

    # ─── 0. AMBIENT GLOW ────────────────────────────────────────────
    if s >= 28:
        gs = s * 6
        glow = pygame.Surface((gs, gs), pygame.SRCALPHA)
        for rad, alpha in [(int(s*2.5),12),(int(s*1.8),20),(int(s*1.2),30),(int(s*0.7),45)]:
            pygame.draw.circle(glow, (*c, alpha), (gs//2, gs//2), rad)
        surf.blit(glow, (cx - gs//2, cy - gs//2))

    # ─── 1. TAIL (behind body) ──────────────────────────────────────
    tx, ty = cx + int(s*0.20), cy + int(s*0.30)
    tail_pts = [
        (tx,                   ty),
        (cx + int(s*0.80),     cy + int(s*0.55)),
        (cx + int(s*1.30),     cy + int(s*0.40)),
        (cx + int(s*1.60),     cy + int(s*0.65)),
        (cx + int(s*1.45),     cy + int(s*0.88)),
        (cx + int(s*1.10),     cy + int(s*0.72)),
        (cx + int(s*0.68),     cy + int(s*0.62)),
        (tx + int(s*0.10),     ty + int(s*0.15)),
    ]
    pygame.draw.polygon(surf, cd, tail_pts)
    pygame.draw.polygon(surf, cm, tail_pts, max(1,s//28))
    # Tail spike/diamond tip
    tip = [
        (cx+int(s*1.45), cy+int(s*0.88)),
        (cx+int(s*1.75), cy+int(s*1.00)),
        (cx+int(s*1.55), cy+int(s*0.65)),
    ]
    pygame.draw.polygon(surf, cl, tip)
    pygame.draw.polygon(surf, cw, tip, max(1,s//30))

    # ─── 2. WINGS ───────────────────────────────────────────────────
    wr_y = cy - int(s*0.10)    # wing root y
    wr_xl = cx - int(s*0.22)   # left root x
    wr_xr = cx + int(s*0.22)   # right root x

    def draw_wing(root_x, sign):
        """sign = -1 (left) or +1 (right)."""
        tip1x = root_x + sign * int(s*1.40)
        tip1y = wr_y   - int(s*0.95)
        mid1x = root_x + sign * int(s*1.10)
        mid1y = wr_y   - int(s*0.30)
        bot1x = root_x + sign * int(s*0.75)
        bot1y = wr_y   + int(s*0.22)

        membrane = [
            (root_x,  wr_y - int(s*0.05)),
            (tip1x,   tip1y),
            (mid1x,   mid1y),
            (bot1x,   bot1y),
            (root_x,  wr_y + int(s*0.18)),
        ]
        pygame.draw.polygon(surf, cd, membrane)

        # Spar bones
        sw = max(1, s//16)
        pygame.draw.line(surf, cm,  (root_x, wr_y), (tip1x, tip1y), sw+1)
        pygame.draw.line(surf, cm,  (root_x, wr_y), (mid1x, mid1y), sw)
        pygame.draw.line(surf, cm,  (root_x, wr_y), (bot1x, bot1y), sw)
        # Cross-membrane lines (texture)
        if s >= 30:
            for t2 in (0.35, 0.65):
                ax = int(root_x*(1-t2) + tip1x*t2)
                ay = int(wr_y*(1-t2)   + tip1y*t2)
                bx = int(root_x*(1-t2) + mid1x*t2)
                by = int(wr_y*(1-t2)   + mid1y*t2)
                pygame.draw.line(surf, _pc(cd, 20), (ax, ay), (bx, by), max(1,s//30))
        # Wing claw at tip
        if s >= 32:
            claw_tip = (tip1x + sign*int(s*0.12), tip1y - int(s*0.10))
            pygame.draw.line(surf, cw, (tip1x, tip1y), claw_tip, max(1,s//22))

        # Thin bright outline
        pygame.draw.polygon(surf, cm, membrane, max(1,s//25))

    draw_wing(wr_xl, -1)
    draw_wing(wr_xr, +1)

    # ─── 3. BODY ────────────────────────────────────────────────────
    bw = int(s * 0.62)
    bh = int(s * 0.78)
    body_rect = pygame.Rect(cx - bw//2, cy - bh//3, bw, bh)
    pygame.draw.ellipse(surf, c, body_rect)

    # Belly gradient (lighter inner ellipse)
    belly_rect = pygame.Rect(cx - bw//3, cy - bh//5, bw*2//3, bh*3//5)
    pygame.draw.ellipse(surf, cb, belly_rect)

    # Scale rows (arc-shaped scales)
    if s >= 30:
        sc = max(2, s//13)
        for row in range(4):
            n_scales = 3 + row
            y_off = int(-bh//4 + row * bh//5)
            x_off = (row % 2) * sc
            for k in range(n_scales):
                sx2 = cx - bw//3 + x_off + k * int(bw*0.55/max(1,n_scales-1))
                sy2 = cy + y_off
                # Arc scale
                pygame.draw.arc(surf, cd,
                                (sx2-sc, sy2-sc//2, sc*2, sc),
                                math.pi*0.1, math.pi*0.9, max(1, s//26))
    elif s >= 18:
        for row in range(2):
            for k in range(3):
                sx2 = cx - bw//4 + k*(bw//3)
                sy2 = cy - bh//8 + row*(bh//5)
                pygame.draw.circle(surf, cd, (sx2, sy2), max(1,s//14), 1)

    # Dorsal spikes along spine
    spike_count = 5 if s >= 35 else 3
    for i in range(spike_count):
        frac = i / max(1, spike_count-1)
        spx = int(cx - bw*0.18 + frac*bw*0.36)
        spy = int(cy - bh//3 - s*0.06 + frac*(-bh//3 - (-bh//3))*0)
        spy = cy - bh//3
        sh  = max(3, int(s*0.14*(1 - frac*0.35)))
        spike_pts = [
            (spx - max(2,s//22), spy),
            (spx,                spy - sh),
            (spx + max(2,s//22), spy),
        ]
        pygame.draw.polygon(surf, cl, spike_pts)
        pygame.draw.polygon(surf, cw, spike_pts, 1)

    # ─── 4. LEGS & CLAWS ────────────────────────────────────────────
    leg_w = max(2, s//9)
    claw_l = max(3, s//8)
    for sign, lx_off in ((-1, -bw//3), (+1, bw//3)):
        lx = cx + lx_off
        knee_y = cy + int(bh*0.38)
        foot_y = cy + int(bh*0.60)
        # Upper leg
        pygame.draw.line(surf, cm, (lx, cy+bh//4), (lx+sign*int(s*0.08), knee_y), leg_w)
        # Lower leg
        pygame.draw.line(surf, cm, (lx+sign*int(s*0.08), knee_y), (lx, foot_y), leg_w-1)
        # Claws
        for dx in (-claw_l, 0, claw_l):
            pygame.draw.line(surf, cl,
                             (lx, foot_y),
                             (lx+dx, foot_y+claw_l+3), max(1,leg_w-1))

    # ─── 5. NECK ────────────────────────────────────────────────────
    nw = max(3, s//5)
    neck_pts = [
        (cx - nw,      cy - bh//3),
        (cx - nw//2,   cy - int(s*0.88)),
        (cx + nw//2,   cy - int(s*0.88)),
        (cx + nw,      cy - bh//3),
    ]
    pygame.draw.polygon(surf, c, neck_pts)
    # Neck scales
    if s >= 32:
        for i in range(3):
            ny = cy - bh//3 - i*(int(s*0.18))
            pygame.draw.arc(surf, cd, (cx-nw+2, ny-4, (nw-2)*2, 8),
                            math.pi*0.1, math.pi*0.9, max(1,s//30))

    # ─── 6. HEAD ────────────────────────────────────────────────────
    hcx = cx
    hcy = cy - int(s*1.08)
    hw  = int(s*0.56)
    hh  = int(s*0.44)
    pygame.draw.ellipse(surf, c, (hcx-hw//2, hcy-hh//2, hw, hh))
    # Cheek highlights
    if s >= 28:
        pygame.draw.ellipse(surf, _pc(c,30),
                            (hcx-hw//3, hcy-hh//3, hw//3, hh//3))

    # Snout / muzzle (front-facing → juts downward)
    snout_pts = [
        (hcx - hw//3,     hcy + hh//5),
        (hcx - hw//4,     hcy + hh//2 + hh//4),
        (hcx + hw//4,     hcy + hh//2 + hh//4),
        (hcx + hw//3,     hcy + hh//5),
    ]
    pygame.draw.polygon(surf, cm, snout_pts)
    # Nostrils
    if s >= 24:
        for nx_off in (-hw//7, hw//7):
            pygame.draw.circle(surf, cd,
                               (hcx+nx_off, hcy+hh//3), max(1,s//28))

    # Teeth (lower jaw)
    if s >= 32:
        tooth_y = hcy + hh//2 + hh//5
        for tx_off in (-hw//5, 0, hw//5):
            tooth = [
                (hcx+tx_off-max(2,s//28), tooth_y),
                (hcx+tx_off,              tooth_y + max(3,s//16)),
                (hcx+tx_off+max(2,s//28), tooth_y),
            ]
            pygame.draw.polygon(surf, (230,225,215), tooth)
        # Jaw outline
        pygame.draw.line(surf, cd,
                         (hcx-hw//3, hcy+hh//5),
                         (hcx+hw//3, hcy+hh//5), max(1,s//28))

    # ─── 7. HORNS & HEAD CREST ──────────────────────────────────────
    horn_h = max(5, s//3)
    horn_w = max(2, s//14)
    for sign in (-1, +1):
        hx_base = hcx + sign * hw//4
        # Main horn
        horn = [
            (hx_base - horn_w,    hcy - hh//2),
            (hx_base + sign*horn_w*2, hcy - hh//2 - int(horn_h*1.15)),
            (hx_base + horn_w,    hcy - hh//3),
        ]
        pygame.draw.polygon(surf, cl, horn)
        pygame.draw.polygon(surf, cw, horn, 1)
        # Secondary mini-horn
        if s >= 30:
            mh = [
                (hx_base + sign*hw//8 - horn_w//2,  hcy - hh//2 + 2),
                (hx_base + sign*(hw//8+horn_w*3),    hcy - hh//2 - horn_h//2),
                (hx_base + sign*hw//8 + horn_w//2,  hcy - hh//3 + 2),
            ]
            pygame.draw.polygon(surf, cm, mh)

    # Frill / head crest spikes
    if s >= 36:
        for i, spx_frac in enumerate((-0.28, -0.10, 0.10, 0.28)):
            fsp_x = int(hcx + spx_frac*hw)
            fsp_y = hcy - hh//2
            fsh   = max(3, int(s*0.10 - abs(spx_frac)*s*0.06))
            fspike = [(fsp_x-2, fsp_y),(fsp_x, fsp_y-fsh),(fsp_x+2, fsp_y)]
            pygame.draw.polygon(surf, cl, fspike)

    # ─── 8. EYES ────────────────────────────────────────────────────
    eye_r = max(3, s//9)
    for sign in (-1, +1):
        ex = hcx + sign * hw//4
        ey = hcy - hh//8
        # Outer glow ring
        if s >= 30:
            pygame.draw.circle(surf, _pc(YELLOW,30), (ex,ey), eye_r+2)
        # Iris
        pygame.draw.circle(surf, YELLOW, (ex,ey), eye_r)
        # Pupil (vertical slit)
        pygame.draw.ellipse(surf, (5,2,0),
                            (ex - max(1,eye_r//4), ey - max(2,eye_r*2//3),
                             max(2,eye_r//2),      max(4,eye_r*4//3)))
        # Shine
        pygame.draw.circle(surf, WHITE,
                           (ex + max(1,eye_r//3), ey - max(1,eye_r//3)),
                           max(1, eye_r//3))

    # ─── 9. ELEMENT VFX ─────────────────────────────────────────────
    if s >= 38:
        vfx_x = cx
        vfx_y = cy - bh//3 - int(s*0.25)

        if elem == "Fire":
            for i in range(6):
                ang  = math.radians(-90 + (i-2.5)*22)
                base = (vfx_x + int(math.cos(ang)*s*0.12),
                        vfx_y + int(math.sin(ang)*s*0.12) + int(s*0.08))
                fh   = int(s*0.22 + i%2*s*0.08)
                tip2 = (base[0] + int(math.cos(ang)*4), base[1] - fh)
                pts  = [
                    (base[0]-3, base[1]),
                    tip2,
                    (base[0]+3, base[1]),
                ]
                inner_c = _blend(YELLOW, c, 0.4) if i%2==0 else c
                pygame.draw.polygon(surf, inner_c, pts)

        elif elem == "Water":
            for i in range(4):
                ang = math.radians(i*90)
                wx  = vfx_x + int(math.cos(ang)*int(s*0.28))
                wy  = vfx_y + int(math.sin(ang)*int(s*0.28))
                pygame.draw.circle(surf, _pc(c,80), (wx,wy), max(3,s//14), 2)

        elif elem == "Electric":
            pts = []
            for i in range(6):
                fx = vfx_x - int(s*0.20) + i*int(s*0.08)
                fy = vfx_y + (-1 if i%2==0 else 1)*int(s*0.14)
                pts.append((fx,fy))
            if len(pts) >= 2:
                pygame.draw.lines(surf, YELLOW,  False, pts, max(2,s//22))
                pygame.draw.lines(surf, WHITE,   False, pts, max(1,s//36))

        elif elem == "Ice":
            for ang_deg in range(0,360,60):
                ang = math.radians(ang_deg)
                x1  = vfx_x + int(math.cos(ang)*int(s*0.28))
                y1  = vfx_y + int(math.sin(ang)*int(s*0.28))
                pygame.draw.line(surf, cl,    (vfx_x,vfx_y),(x1,y1), max(2,s//22))
                pygame.draw.line(surf, WHITE, (vfx_x,vfx_y),(x1,y1), max(1,s//40))
                pygame.draw.circle(surf, WHITE, (x1,y1), max(2,s//20))

        elif elem == "Nature":
            for i in range(5):
                ang = math.radians(-90 + i*45)
                lx2 = vfx_x + int(math.cos(ang)*int(s*0.28))
                ly2 = vfx_y + int(math.sin(ang)*int(s*0.28))
                pygame.draw.line(surf, cl, (vfx_x,vfx_y), (lx2,ly2), max(2,s//22))
                leaf = [
                    (lx2,              ly2-max(3,s//14)),
                    (lx2+max(3,s//14), ly2),
                    (lx2,              ly2+max(3,s//14)),
                    (lx2-max(3,s//14), ly2),
                ]
                pygame.draw.polygon(surf, cl, leaf)

        elif elem == "Dark":
            for i in range(3):
                r2 = int(s*(0.25+i*0.10))
                a2 = 50 - i*12
                if a2 > 0:
                    gsurf = pygame.Surface((r2*2+4,r2*2+4), pygame.SRCALPHA)
                    pygame.draw.circle(gsurf, (*cd, a2), (r2+2,r2+2), r2)
                    surf.blit(gsurf, (vfx_x-r2-2, vfx_y-r2-2))
            for ang_deg in range(0,360,72):
                ang = math.radians(ang_deg)
                dx2 = vfx_x + int(math.cos(ang)*int(s*0.30))
                dy2 = vfx_y + int(math.sin(ang)*int(s*0.30))
                pygame.draw.line(surf, cm, (vfx_x,vfx_y),(dx2,dy2), max(1,s//32))

        elif elem == "Light":
            for ang_deg in range(0,360,45):
                ang  = math.radians(ang_deg)
                r_in = int(s*0.12)
                r_out= int(s*0.30)
                x1   = vfx_x + int(math.cos(ang)*r_in)
                y1   = vfx_y + int(math.sin(ang)*r_in)
                x2   = vfx_x + int(math.cos(ang)*r_out)
                y2   = vfx_y + int(math.sin(ang)*r_out)
                pygame.draw.line(surf, YELLOW, (x1,y1),(x2,y2), max(2,s//22))
            pygame.draw.circle(surf, WHITE, (vfx_x,vfx_y), max(4,s//12))

        elif elem == "Metal":
            for i in range(4):
                ang  = math.radians(i*90+45)
                x1   = vfx_x + int(math.cos(ang)*int(s*0.28))
                y1   = vfx_y + int(math.sin(ang)*int(s*0.28))
                pygame.draw.line(surf, cl, (vfx_x,vfx_y),(x1,y1), max(3,s//18))
            pygame.draw.circle(surf, _pc(cl,40), (vfx_x,vfx_y), max(4,s//13))
            pygame.draw.circle(surf, cd, (vfx_x,vfx_y), max(4,s//13), 2)

        elif elem == "Dragon":
            for i in range(5):
                ang  = math.radians(-90 + i*72)
                x1   = vfx_x + int(math.cos(ang)*int(s*0.32))
                y1   = vfx_y + int(math.sin(ang)*int(s*0.32))
                pygame.draw.line(surf, cl,   (vfx_x,vfx_y),(x1,y1), max(2,s//20))
                pygame.draw.line(surf, GOLD, (vfx_x,vfx_y),(x1,y1), max(1,s//35))
            pygame.draw.circle(surf, GOLD,  (vfx_x,vfx_y), max(4,s//11))
            pygame.draw.circle(surf, WHITE, (vfx_x,vfx_y), max(2,s//20))

        elif elem == "Terra":
            for i in range(5):
                ang = math.radians(-90 + i*72)
                rx  = vfx_x + int(math.cos(ang)*int(s*0.28))
                ry  = vfx_y + int(math.sin(ang)*int(s*0.28))
                rock = [
                    (rx-max(3,s//16), ry),
                    (rx,              ry-max(4,s//13)),
                    (rx+max(3,s//16), ry),
                    (rx,              ry+max(3,s//16)),
                ]
                pygame.draw.polygon(surf, cl, rock)
                pygame.draw.polygon(surf, cd, rock, 1)

    # ─── 10. OUTLINE PASS ───────────────────────────────────────────
    if s >= 28:
        ow = max(1, s//36)
        # Body outline
        pygame.draw.ellipse(surf, cd, body_rect, ow)
        # Head outline
        pygame.draw.ellipse(surf, cd, (hcx-hw//2, hcy-hh//2, hw, hh), ow)

    # ─── 11. LEVEL BADGE ────────────────────────────────────────────
    if level > 0:
        bx = cx + int(s*0.68)
        by = cy + int(s*0.52)
        br = max(8, s//5)
        pygame.draw.circle(surf, (20,12,2), (bx,by), br+3)
        pygame.draw.circle(surf, GOLD,      (bx,by), br)
        pygame.draw.circle(surf, cw,        (bx,by), br, 2)
        lv_s = F_TINY.render(str(level), True, (10,6,0))
        surf.blit(lv_s, lv_s.get_rect(center=(bx, by)))

# ───────────────────────────────────────────────
#  BUTTON CLASS
# ───────────────────────────────────────────────
class Btn:
    def __init__(self, x, y, w, h, label, color=PURPLE, tcolor=WHITE, font=F_BODY):
        self.rect   = pygame.Rect(x, y, w, h)
        self.label  = label
        self.color  = color
        self.tcolor = tcolor
        self.font   = font
        self.hov_c  = tuple(min(255,v+40) for v in color)
        self.active = True

    def draw(self, surf, mpos):
        if not self.active:
            rrect(surf, DGRAY, self.rect, 8, 1, BORDER)
            s = self.font.render(self.label, True, GRAY)
            surf.blit(s, s.get_rect(center=self.rect.center))
            return False
        hov = self.rect.collidepoint(mpos)
        rrect(surf, self.hov_c if hov else self.color, self.rect, 8, 1, BORDER)
        s = self.font.render(self.label, True, self.tcolor)
        surf.blit(s, s.get_rect(center=self.rect.center))
        return hov

    def hit(self, ev, mpos):
        return (self.active and ev.type == pygame.MOUSEBUTTONDOWN
                and ev.button == 1 and self.rect.collidepoint(mpos))

# ───────────────────────────────────────────────
#  APP STATE
# ───────────────────────────────────────────────
class App:
    def __init__(self):
        self.gs: Optional[GameState] = None
        self.screen = "splash"          # current screen
        self.scroll = 0
        self.msg = ""
        self.msg_timer = 0
        self.msg_color = GREEN
        # New-game inputs
        self.input_name = ""
        self.input_active = False
        self.starter_choice = -1
        # Battle state
        self.battle = {}
        self.battle_log = []
        self.battle_anim = 0           # shake timer
        self.battle_done = False
        # Breeding
        self.breed_select = []
        # Name-a-dragon dialog
        self.naming = None             # template name being named
        self.naming_text = ""
        self.naming_active = False
        # Scroll targets
        self.scroll_max = 0

    def notify(self, msg, color=GREEN):
        self.msg = msg
        self.msg_timer = 180
        self.msg_color = color

    def go(self, screen):
        self.screen = screen
        self.scroll = 0
        self.battle_log = []
        self.breed_select = []

# ───────────────────────────────────────────────
#  DRAW HEADER
# ───────────────────────────────────────────────
def draw_header(app: App):
    gs = app.gs
    rrect(screen, PANEL, (0,0,W,54), 0)
    pygame.draw.line(screen, BORDER, (0,54),(W,54), 1)
    txt(screen, "DRAGON CITY", 16, 12, F_H1, GOLD)
    # Stats on the right
    info = f"Day {gs.day}   Gold: {gs.gold}   Gems: {gs.gems}   Dragons: {len(gs.dragons)}   Wins: {gs.battles_won}"
    txt(screen, info, W-16, 18, F_BODY, LGRAY, "midright")

def draw_notification(app: App):
    if app.msg_timer > 0:
        alpha = min(255, app.msg_timer * 4)
        s = F_H2.render(app.msg, True, app.msg_color)
        r = s.get_rect(center=(W//2, H-36))
        bg = pygame.Surface((r.w+24, r.h+12), pygame.SRCALPHA)
        bg.fill((0,0,0,160))
        screen.blit(bg, (r.x-12, r.y-6))
        screen.blit(s, r)
        app.msg_timer -= 1

def draw_back_btn(app: App, dest="main_menu"):
    btn = Btn(16, 60, 90, 30, "< Back", DGRAY, LGRAY, F_SMALL)
    btn.draw(screen, pygame.mouse.get_pos())
    return btn

# ───────────────────────────────────────────────
#  SPLASH / MAIN MENU
# ───────────────────────────────────────────────
def draw_splash(app: App):
    screen.fill(BG)
    # Background dragon silhouettes
    for i,pos in enumerate([(200,320),(760,350),(480,400)]):
        s = 60 + i*20
        elems = ["Fire","Water","Dragon"]
        draw_dragon_shape(screen, pos[0], pos[1], s, elems[i])

    # Title
    txt(screen, "DRAGON CITY", W//2, 100, F_TITLE, GOLD, "midtop")
    txt(screen, "Collect  *  Breed  *  Battle", W//2, 155, F_H2, LGRAY, "midtop")

    mpos = pygame.mouse.get_pos()
    btns = []
    gs = GameState.load()
    if gs:
        b1 = Btn(W//2-110, 230, 220, 46, "Continue Game", GREEN)
        b2 = Btn(W//2-110, 290, 220, 46, "New Game",      PURPLE)
        btns = [b1, b2]
    else:
        b1 = Btn(W//2-110, 250, 220, 46, "New Game", PURPLE)
        btns = [b1]
    b_quit = Btn(W//2-110, H-80, 220, 40, "Quit", DARK_RED, WHITE, F_BODY)
    for b in btns: b.draw(screen, mpos)
    b_quit.draw(screen, mpos)
    txt(screen, "Press any button to begin", W//2, H-26, F_SMALL, GRAY, "midbottom")
    return btns, b_quit, gs is not None

# ───────────────────────────────────────────────
#  NEW GAME SCREEN
# ───────────────────────────────────────────────
def draw_new_game(app: App):
    screen.fill(BG)
    txt(screen, "NEW GAME", W//2, 30, F_TITLE, GOLD, "midtop")

    # Name input
    txt(screen, "Trainer Name:", 200, 100, F_H2, WHITE)
    inp_rect = pygame.Rect(200, 130, 560, 40)
    rrect(screen, CARD, inp_rect, 8, 2, GOLD if app.input_active else BORDER)
    txt(screen, app.input_name + ("|" if app.input_active else ""), 212, 142, F_BODY, WHITE)

    # Starter choice
    txt(screen, "Choose Your Starter Dragon:", W//2, 195, F_H2, WHITE, "midtop")
    starters = ["Flamejet","Aqua","Treeling"]
    mpos = pygame.mouse.get_pos()
    cards = []
    for i, name in enumerate(starters):
        cx = 180 + i*200
        cy = 280
        r = pygame.Rect(cx-70, cy-20, 140, 160)
        sel = app.starter_choice == i
        rrect(screen, CARD, r, 10, 3, GOLD if sel else BORDER)
        t = DRAGONS[name]
        e = t["elems"][0]
        draw_dragon_shape(screen, cx, cy+30, 40, e)
        txt(screen, name, cx, cy+90, F_H2, RARITY_C[t["rarity"]], "midtop")
        txt(screen, "/".join(t["elems"]), cx, cy+114, F_SMALL, ELEM_C[e], "midtop")
        txt(screen, f"HP:{t['hp']} ATK:{t['atk']}", cx, cy+132, F_SMALL, LGRAY, "midtop")
        cards.append(r)

    # Start button
    start = Btn(W//2-90, 490, 180, 44, "Start!", GREEN)
    start.active = (len(app.input_name) > 0 and app.starter_choice >= 0)
    start.draw(screen, mpos)
    return cards, start

# ───────────────────────────────────────────────
#  MAIN MENU
# ───────────────────────────────────────────────
def draw_main_menu(app: App):
    screen.fill(BG)
    draw_header(app)

    # Big dragon art
    draw_dragon_shape(screen, W//2, 300, 80, "Dragon")

    mpos = pygame.mouse.get_pos()
    buttons = []
    labels = [
        ("My Dragons",   "collection",  BLUE),
        ("Battle",       "battle_arena",RED),
        ("Breeding Den", "breeding",    PURPLE),
        ("Dragon Shop",  "shop",        ORANGE),
        ("Next Day",     "daily",       GREEN),
        ("Save Game",    "save",        DGRAY),
    ]
    cols = 3
    bw, bh, gap = 200, 50, 16
    start_x = W//2 - (cols*(bw+gap)-gap)//2
    for i,(label, dest, color) in enumerate(labels):
        col_i = i % cols
        row_i = i // cols
        x = start_x + col_i*(bw+gap)
        y = 420 + row_i*(bh+gap)
        b = Btn(x, y, bw, bh, label, color)
        b.draw(screen, mpos)
        buttons.append((b, dest))

    draw_notification(app)
    return buttons

# ───────────────────────────────────────────────
#  COLLECTION SCREEN
# ───────────────────────────────────────────────
CARD_W, CARD_H = 280, 170
CARD_COLS = 3
CARD_GAP  = 12
CARDS_TOP = 100

def draw_collection(app: App):
    screen.fill(BG)
    draw_header(app)
    back = draw_back_btn(app)
    txt(screen, "MY DRAGONS", W//2, 64, F_H1, GOLD, "midtop")

    gs = app.gs
    mpos = pygame.mouse.get_pos()

    if not gs.dragons:
        txt(screen, "No dragons yet! Visit the Shop.", W//2, 300, F_H2, GRAY, "midtop")
        draw_notification(app)
        return back, []

    total_w = CARD_COLS * CARD_W + (CARD_COLS-1)*CARD_GAP
    start_x = (W - total_w) // 2

    card_btns = []
    visible_area = H - CARDS_TOP - 30
    for i, dr in enumerate(gs.dragons):
        row = i // CARD_COLS
        col_i = i % CARD_COLS
        x = start_x + col_i * (CARD_W + CARD_GAP)
        y = CARDS_TOP + row * (CARD_H + CARD_GAP) - app.scroll

        if y + CARD_H < CARDS_TOP or y > H: continue

        r = pygame.Rect(x, y, CARD_W, CARD_H)
        rrect(screen, CARD, r, 10, 2, RARITY_C[dr.rarity])

        # Dragon art
        draw_dragon_shape(screen, x+40, y+CARD_H//2, 30, dr.primary_elem, dr.level)

        # Info
        ix = x + 82
        txt(screen, dr.name, ix, y+10, F_H2, WHITE)
        star_row(screen, ix, y+35, dr.rarity)
        elems = " / ".join(dr.elements)
        txt(screen, elems, ix, y+52, F_SMALL, ELEM_C[dr.primary_elem])

        # HP bar
        txt(screen, "HP", ix, y+70, F_TINY, LGRAY)
        hbar(screen, ix+22, y+74, 160, 10, dr.hp, dr.max_hp, GREEN, DGRAY)
        txt(screen, f"{dr.hp}/{dr.max_hp}", ix+186, y+70, F_TINY, LGRAY)

        # Stats
        txt(screen, f"Lv.{dr.level}  XP:{dr.xp}/{dr.xp_need()}", ix, y+90, F_SMALL, CYAN)
        txt(screen, f"ATK:{dr.atk}  DEF:{dr.df}", ix, y+108, F_SMALL, LGRAY)

        card_btns.append((r, i))

    # Scroll limits
    rows = math.ceil(len(gs.dragons) / CARD_COLS)
    app.scroll_max = max(0, rows*(CARD_H+CARD_GAP) - visible_area + CARDS_TOP)

    # Heal all button
    heal = Btn(W-130, 60, 114, 30, "Heal All (50g)", GREEN, WHITE, F_SMALL)
    heal.draw(screen, mpos)

    draw_notification(app)
    return back, heal

# ───────────────────────────────────────────────
#  SHOP SCREEN
# ───────────────────────────────────────────────
def draw_shop(app: App):
    screen.fill(BG)
    draw_header(app)
    back = draw_back_btn(app)
    txt(screen, "DRAGON SHOP", W//2, 64, F_H1, GOLD, "midtop")

    mpos = pygame.mouse.get_pos()
    buy_btns = []
    cols = 3
    item_w, item_h, gap = 270, 160, 14
    total_w = cols*item_w + (cols-1)*gap
    sx = (W - total_w)//2

    for i, (name, price) in enumerate(SHOP_ITEMS):
        col_i = i % cols
        row_i = i // cols
        x = sx + col_i*(item_w+gap)
        y = 100 + row_i*(item_h+gap) - app.scroll
        if y+item_h < 90 or y > H: continue

        t = DRAGONS[name]
        r = pygame.Rect(x,y,item_w,item_h)
        rrect(screen, CARD, r, 10, 2, RARITY_C[t["rarity"]])

        draw_dragon_shape(screen, x+38, y+item_h//2, 28, t["elems"][0])

        ix = x+76
        txt(screen, name, ix, y+10, F_H2, WHITE)
        star_row(screen, ix, y+34, t["rarity"])
        txt(screen, "/".join(t["elems"]), ix, y+52, F_SMALL, ELEM_C[t["elems"][0]])
        txt(screen, f"HP:{t['hp']}  ATK:{t['atk']}  DEF:{t['df']}", ix, y+70, F_TINY, LGRAY)

        affordable = app.gs.gold >= price
        b = Btn(x+item_w//2-50, y+item_h-38, 100, 28,
                f"Buy {price}g", GREEN if affordable else DGRAY, WHITE, F_SMALL)
        b.active = affordable
        b.draw(screen, mpos)
        buy_btns.append((b, name, price))

    rows = math.ceil(len(SHOP_ITEMS)/cols)
    app.scroll_max = max(0, rows*(item_h+gap) - (H-100))

    draw_notification(app)
    return back, buy_btns

# ───────────────────────────────────────────────
#  BATTLE ARENA SELECT
# ───────────────────────────────────────────────
def draw_battle_arena(app: App):
    screen.fill(BG)
    draw_header(app)
    back = draw_back_btn(app)
    txt(screen, "BATTLE ARENAS", W//2, 64, F_H1, GOLD, "midtop")

    mpos = pygame.mouse.get_pos()
    arena_btns = []
    for i, arena in enumerate(ARENAS):
        y = 110 + i*120
        r = pygame.Rect(120, y, W-240, 100)
        eligible = [d for d in app.gs.dragons if d.level >= arena["min_lv"]]
        locked = not eligible
        border = DGRAY if locked else RARITY_C["Rare"]
        rrect(screen, CARD, r, 10, 2, border)

        txt(screen, arena["name"], 150, y+12, F_H2, GRAY if locked else WHITE)
        txt(screen, f"Min Level: {arena['min_lv']}   Reward: x{arena['gold_mult']:.1f}", 150, y+36, F_BODY, LGRAY)
        txt(screen, "Enemies: " + ", ".join(arena["pool"]), 150, y+58, F_SMALL, GRAY)

        if locked:
            txt(screen, "LOCKED", W-200, y+40, F_H2, RED, "midtop")
        else:
            b = Btn(W-230, y+30, 100, 36, "Enter!", RED)
            b.draw(screen, mpos)
            arena_btns.append((b, i))

    draw_notification(app)
    return back, arena_btns

# ───────────────────────────────────────────────
#  DRAGON PICKER OVERLAY (for battle/breeding)
# ───────────────────────────────────────────────
def draw_dragon_picker(app, title="Choose a Dragon", exclude_idx=-1):
    """Returns list of (button, dragon_index)."""
    rrect(screen, PANEL, (100, 80, W-200, H-160), 14, 2, BORDER)
    txt(screen, title, W//2, 100, F_H1, GOLD, "midtop")
    mpos = pygame.mouse.get_pos()
    pick_btns = []
    for i, dr in enumerate(app.gs.dragons):
        if i == exclude_idx: continue
        y = 145 + i*56 - app.scroll
        if y < 120 or y > H-80: continue
        r = pygame.Rect(130, y, W-260, 48)
        rrect(screen, CARD, r, 8, 1, RARITY_C[dr.rarity])
        draw_dragon_shape(screen, 165, y+24, 18, dr.primary_elem, dr.level)
        txt(screen, dr.name, 192, y+6, F_H2, WHITE)
        txt(screen, f"Lv.{dr.level}  HP:{dr.hp}/{dr.max_hp}  ATK:{dr.atk}  DEF:{dr.df}", 192, y+28, F_SMALL, LGRAY)
        b = Btn(W-240, y+8, 80, 32, "Select", BLUE, WHITE, F_SMALL)
        b.draw(screen, mpos)
        pick_btns.append((b, i))
    app.scroll_max = max(0, len(app.gs.dragons)*56 - (H-300))
    cancel = Btn(W//2-60, H-130, 120, 36, "Cancel", DARK_RED)
    cancel.draw(screen, mpos)
    return pick_btns, cancel

# ───────────────────────────────────────────────
#  BATTLE FIGHT SCREEN
# ───────────────────────────────────────────────
def draw_battle_fight(app: App):
    b = app.battle
    if not b: return None, None, None

    player_dr: Dragon = b["player"]
    enemy_dr:  Dragon = b["enemy"]
    phase = b.get("phase","pick_action")

    # ── Arena backdrop: gradient ground ──────────────────────────────
    for row in range(H):
        t = row / H
        rc = (int(8+t*18), int(5+t*12), int(18+t*28))
        pygame.draw.line(screen, rc, (0,row),(W,row))
    # Ground line
    pygame.draw.line(screen, _pc(BORDER,20), (0,310),(W,310), 2)
    # Ground shadow gradient
    for i in range(18):
        alpha = 60 - i*3
        pygame.draw.line(screen, (0,0,0), (0,311+i),(W,311+i))

    # ── Enemy side (top-right, size 72, facing left) ──────────────────
    ex, ey = 680, 160
    # Ground shadow ellipse
    shadow = pygame.Surface((160,30), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow, (0,0,0,60), (0,0,160,30))
    screen.blit(shadow, (ex-80, ey+90))

    # Red flash when enemy is hit
    if app.battle_anim > 0 and b.get("last_hit") == "enemy":
        flash = pygame.Surface((200,200), pygame.SRCALPHA)
        flash.fill((255,60,60, min(180, app.battle_anim*14)))
        screen.blit(flash, (ex-100, ey-100))

    draw_dragon_shape(screen, ex, ey, 72, enemy_dr.primary_elem, enemy_dr.level)
    txt(screen, enemy_dr.name, ex, ey-115, F_H1, RED, "midtop")
    star_row(screen, ex-35, ey-93, enemy_dr.rarity)
    # HP bar with border
    rrect(screen, DGRAY, (ex-82, ey+82, 164, 18), 5)
    hp_w = max(0, int(160*(enemy_dr.hp/enemy_dr.max_hp)))
    if hp_w: rrect(screen, RED,  (ex-80, ey+84, hp_w, 14), 4)
    txt(screen, f"{enemy_dr.hp}/{enemy_dr.max_hp}", ex, ey+104, F_SMALL, LGRAY, "midtop")

    # ── Player side (bottom-left, size 72) ────────────────────────────
    px, py = 260, 380
    shake_x = random.randint(-4,4) if app.battle_anim > 0 and b.get("last_hit")=="player" else 0
    shake_y = random.randint(-2,2) if app.battle_anim > 0 and b.get("last_hit")=="player" else 0

    # Ground shadow
    shadow2 = pygame.Surface((160,30), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow2, (0,0,0,60), (0,0,160,30))
    screen.blit(shadow2, (px-80, py+90))

    # Blue flash when player is hit
    if app.battle_anim > 0 and b.get("last_hit") == "player":
        flash2 = pygame.Surface((200,200), pygame.SRCALPHA)
        flash2.fill((60,120,255, min(160, app.battle_anim*12)))
        screen.blit(flash2, (px+shake_x-100, py+shake_y-100))

    draw_dragon_shape(screen, px+shake_x, py+shake_y, 72, player_dr.primary_elem, player_dr.level)
    txt(screen, player_dr.name, px, py-115, F_H1, CYAN, "midtop")
    star_row(screen, px-35, py-93, player_dr.rarity)
    rrect(screen, DGRAY, (px-82, py+82, 164, 18), 5)
    phw = max(0, int(160*(player_dr.hp/player_dr.max_hp)))
    hp_col = GREEN if player_dr.hp > player_dr.max_hp*0.5 else ORANGE if player_dr.hp > player_dr.max_hp*0.25 else RED
    if phw: rrect(screen, hp_col, (px-80, py+84, phw, 14), 4)
    txt(screen, f"{player_dr.hp}/{player_dr.max_hp}", px, py+104, F_SMALL, LGRAY, "midtop")
    txt(screen, f"Lv.{player_dr.level}  ATK:{player_dr.atk}  DEF:{player_dr.df}", px, py+118, F_TINY, LGRAY, "midtop")

    if app.battle_anim > 0:
        app.battle_anim -= 1

    # ── Battle log (center strip) ─────────────────────────────────────
    log_r = pygame.Rect(W//2-210, 200, 420, 170)
    log_surf = pygame.Surface((420,170), pygame.SRCALPHA)
    log_surf.fill((8,5,18,210))
    screen.blit(log_surf, (W//2-210, 200))
    pygame.draw.rect(screen, BORDER, log_r, 1, border_radius=10)
    for i, line in enumerate(app.battle_log[-5:]):
        txt(screen, line["text"], W//2, 210+i*30, F_SMALL, line.get("color",LGRAY), "midtop")

    mpos = pygame.mouse.get_pos()
    atk_btn = flee_btn = skip_btn = None

    if phase == "pick_action" and player_dr.is_alive() and enemy_dr.is_alive():
        txt(screen, "Choose your action:", W//2, H-140, F_H2, WHITE, "midtop")
        atk_btn  = Btn(W//2-310, H-100, 180, 42, "Attack",  RED)
        skip_btn = Btn(W//2- 90, H-100, 180, 42, "Skip",    DGRAY)
        flee_btn = Btn(W//2+110, H-100, 180, 42, "Flee",    DARK_RED)
        for b2 in (atk_btn,skip_btn,flee_btn): b2.draw(screen, mpos)

    elif phase == "result":
        won = b.get("won", False)
        msg = "VICTORY!" if won else "DEFEATED..."
        col = GOLD if won else RED
        txt(screen, msg, W//2, H-120, F_TITLE, col, "midtop")
        if won:
            txt(screen, f"+{b['xp_gain']} XP  +{b['gold_gain']} Gold", W//2, H-76, F_H2, GREEN, "midtop")
        cont = Btn(W//2-80, H-50, 160, 38, "Continue", PURPLE)
        cont.draw(screen, mpos)
        return atk_btn, flee_btn, cont


    draw_notification(app)
    return atk_btn, flee_btn, skip_btn

def battle_attack(app: App):
    b = app.battle
    pd: Dragon = b["player"]
    ed: Dragon = b["enemy"]

    # Player attacks enemy
    base = max(1, pd.atk - ed.df//2) + random.randint(-4,8)
    mult = 1.0
    note = ""
    for ae in pd.elements:
        for de in ed.elements:
            if de in ELEMENTS[ae]["strong"]:
                mult = max(mult,1.5); note="SUPER EFFECTIVE!"
            elif de in ELEMENTS[ae]["weak"]:
                mult = min(mult,0.6); note="Not very effective"
    crit = random.random()<0.1
    if crit: mult *= 1.5; note = "CRITICAL! " + note
    dmg = max(1,int(base*mult))
    ed.hp = max(0, ed.hp-dmg)
    app.battle_log.append({"text":f"You dealt {dmg} dmg! {note}", "color":GREEN if mult>=1.0 else GRAY})
    app.battle_anim = 14
    b["last_hit"] = "enemy"

    if not ed.is_alive():
        _battle_end(app, won=True); return

    # Enemy attacks player
    ebase = max(1, ed.atk - pd.df//2) + random.randint(-4,8)
    emult = 1.0
    for ae in ed.elements:
        for de in pd.elements:
            if de in ELEMENTS[ae]["strong"]: emult = max(emult,1.5)
            elif de in ELEMENTS[ae]["weak"]: emult = min(emult,0.6)
    edmg = max(1,int(ebase*emult))
    pd.hp = max(0, pd.hp-edmg)
    app.battle_log.append({"text":f"Enemy dealt {edmg} dmg!", "color":RED})
    b["last_hit"] = "player"

    if not pd.is_alive():
        _battle_end(app, won=False)

def _battle_end(app: App, won: bool):
    b = app.battle
    b["phase"] = "result"
    b["won"] = won
    if won:
        pd: Dragon = b["player"]
        xp = 20 + b["enemy"].level*5
        gold = int((30 + b["enemy"].level*10) * b["arena"]["gold_mult"])
        leveled = pd.add_xp(xp)
        app.gs.gold += gold
        app.gs.battles_won += 1
        b["xp_gain"] = xp
        b["gold_gain"] = gold
        if leveled:
            app.notify(f"{pd.name} leveled up to Lv.{pd.level}!", GOLD)
        # Tick breeding
        for s in app.gs.breeding_slots:
            s["turns_left"] = max(0, s["turns_left"]-1)
    else:
        b["xp_gain"] = b["gold_gain"] = 0

# ───────────────────────────────────────────────
#  BREEDING SCREEN
# ───────────────────────────────────────────────
def draw_breeding(app: App):
    screen.fill(BG)
    draw_header(app)
    back = draw_back_btn(app)
    txt(screen, "BREEDING DEN", W//2, 64, F_H1, GOLD, "midtop")

    gs = app.gs
    mpos = pygame.mouse.get_pos()

    # Queue
    y = 100
    txt(screen, "Breeding Queue:", 120, y, F_H2, WHITE)
    y += 28
    ready_btns = []
    if not gs.breeding_slots:
        txt(screen, "Empty — breed two dragons below!", 140, y, F_BODY, GRAY)
        y += 26
    for i, slot in enumerate(gs.breeding_slots):
        t = DRAGONS[slot["template"]]
        sr = pygame.Rect(120, y, W-240, 44)
        rrect(screen, CARD, sr, 8, 1, RARITY_C[t["rarity"]])
        draw_dragon_shape(screen, 152, y+22, 15, t["elems"][0])
        txt(screen, slot["template"], 178, y+6, F_H2, WHITE)
        if slot["turns_left"] <= 0:
            txt(screen, "READY TO HATCH!", 178, y+26, F_SMALL, GREEN)
            hatch_b = Btn(W-240, y+6, 100, 32, "Hatch!", GOLD, (10,10,10), F_SMALL)
            hatch_b.draw(screen, mpos)
            ready_btns.append((hatch_b, i))
        else:
            txt(screen, f"{slot['turns_left']} battle(s) remaining", 178, y+26, F_SMALL, LGRAY)
        y += 52

    # Breed button
    y = max(y+10, 300)
    txt(screen, "Select 2 dragons to breed  (costs 100 Gold):", 120, y, F_H2, WHITE)
    y += 30
    breed_btns = []
    for i, dr in enumerate(gs.dragons):
        br = pygame.Rect(120, y, W-350, 44)
        selected = i in app.breed_select
        rrect(screen, CARD if not selected else (40,30,70), br, 8, 2,
              GOLD if selected else BORDER)
        draw_dragon_shape(screen, 152, y+22, 15, dr.primary_elem, dr.level)
        txt(screen, dr.name, 178, y+6, F_H2, WHITE)
        txt(screen, f"Lv.{dr.level} | {'/'.join(dr.elements)}", 178, y+26, F_SMALL, LGRAY)
        sel_b = Btn(W-216, y+8, 80, 28,
                    "Deselect" if selected else "Select",
                    GOLD if selected else BLUE, WHITE if not selected else (10,10,10), F_SMALL)
        sel_b.draw(screen, mpos)
        breed_btns.append((sel_b, i))
        y += 52

    breed_go = Btn(W//2-90, H-60, 180, 40, "Breed! (100g)", PURPLE)
    breed_go.active = len(app.breed_select)==2 and gs.gold>=100
    breed_go.draw(screen, mpos)

    app.scroll_max = max(0, y - (H-80))
    draw_notification(app)
    return back, ready_btns, breed_btns, breed_go

# ───────────────────────────────────────────────
#  NAME DIALOG
# ───────────────────────────────────────────────
def draw_name_dialog(app: App):
    rrect(screen, PANEL, (W//2-200, H//2-80, 400, 160), 12, 2, GOLD)
    txt(screen, f"Name your {app.naming}:", W//2, H//2-60, F_H2, WHITE, "midtop")
    inp_r = pygame.Rect(W//2-160, H//2-20, 320, 38)
    rrect(screen, CARD, inp_r, 8, 2, GOLD if app.naming_active else BORDER)
    txt(screen, app.naming_text + "|", W//2-148, H//2-8, F_BODY, WHITE)
    mpos = pygame.mouse.get_pos()
    ok = Btn(W//2-90, H//2+50, 80, 32, "OK", GREEN, WHITE, F_SMALL)
    skip_b = Btn(W//2+10, H//2+50, 80, 32, "Default", DGRAY, LGRAY, F_SMALL)
    ok.draw(screen, mpos)
    skip_b.draw(screen, mpos)
    return ok, skip_b

# ───────────────────────────────────────────────
#  DAILY
# ───────────────────────────────────────────────
def draw_daily(app: App):
    screen.fill(BG)
    gs = app.gs
    income = sum(gs.habitats.values())*50
    gs.gold += income
    gs.day += 1
    for s in gs.breeding_slots:
        s["turns_left"] = max(0, s["turns_left"]-1)
    ready = sum(1 for s in gs.breeding_slots if s["turns_left"]<=0)

    txt(screen, f"Day {gs.day} Begins!", W//2, 200, F_TITLE, GOLD, "midtop")
    txt(screen, f"+{income} Gold collected from habitats!", W//2, 280, F_H1, GREEN, "midtop")
    if ready:
        txt(screen, f"{ready} egg(s) ready to hatch in the Breeding Den!", W//2, 330, F_H2, CYAN, "midtop")
    mpos = pygame.mouse.get_pos()
    b = Btn(W//2-90, 420, 180, 44, "Continue", PURPLE)
    b.draw(screen, mpos)
    return b

# ───────────────────────────────────────────────
#  MAIN LOOP
# ───────────────────────────────────────────────
def main():
    app = App()
    app.screen = "splash"
    running = True

    # Pre-load buttons for the current frame
    frame_btns = {}

    while running:
        clock.tick(FPS)
        mpos = pygame.mouse.get_pos()
        events = pygame.event.get()

        for ev in events:
            if ev.type == pygame.QUIT:
                if app.gs: app.gs.save()
                pygame.quit(); sys.exit()

            # Global scroll
            if ev.type == pygame.MOUSEWHEEL:
                app.scroll = max(0, min(app.scroll_max, app.scroll - ev.y*30))

            # ── SPLASH ──
            if app.screen == "splash":
                btns, b_quit, has_save = frame_btns.get("splash",([], None, False))
                if b_quit and b_quit.hit(ev, mpos):
                    pygame.quit(); sys.exit()
                for i, b in enumerate(btns):
                    if b.hit(ev, mpos):
                        if has_save and i == 0:
                            app.gs = GameState.load()
                            app.go("main_menu")
                        else:
                            app.go("new_game")
                            app.input_name = ""
                            app.input_active = True
                            app.starter_choice = -1

            # ── NEW GAME ──
            elif app.screen == "new_game":
                cards, start_btn = frame_btns.get("new_game", ([], None))
                if ev.type == pygame.MOUSEBUTTONDOWN:
                    inp_r = pygame.Rect(200,130,560,40)
                    app.input_active = inp_r.collidepoint(mpos)
                    for i, r in enumerate(cards):
                        if r.collidepoint(mpos):
                            app.starter_choice = i
                if ev.type == pygame.KEYDOWN and app.input_active:
                    if ev.key == pygame.K_BACKSPACE:
                        app.input_name = app.input_name[:-1]
                    elif ev.key == pygame.K_RETURN:
                        app.input_active = False
                    elif len(app.input_name) < 20:
                        app.input_name += ev.unicode
                if start_btn and start_btn.hit(ev, mpos):
                    gs = GameState(player_name=app.input_name.strip() or "Trainer")
                    starters = ["Flamejet","Aqua","Treeling"]
                    sn = starters[app.starter_choice]
                    gs.dragons.append(Dragon(name=sn, template=sn))
                    app.gs = gs
                    gs.save()
                    app.notify(f"Welcome, {gs.player_name}! Your adventure begins!")
                    app.go("main_menu")

            # ── MAIN MENU ──
            elif app.screen == "main_menu":
                for b, dest in frame_btns.get("main_menu", []):
                    if b.hit(ev, mpos):
                        if dest == "save":
                            app.gs.save()
                            app.notify("Game saved!")
                        elif dest == "daily":
                            app.go("daily")
                        else:
                            app.go(dest)

            # ── COLLECTION ──
            elif app.screen == "collection":
                back, heal = frame_btns.get("collection",(None,None))
                if back and back.hit(ev, mpos): app.go("main_menu")
                if heal and heal.hit(ev, mpos):
                    if app.gs.gold >= 50:
                        app.gs.gold -= 50
                        for d in app.gs.dragons: d.recalc()
                        app.notify("All dragons healed!")
                    else:
                        app.notify("Not enough gold!", RED)

            # ── SHOP ──
            elif app.screen == "shop":
                back, buy_btns = frame_btns.get("shop",(None,[]))
                if back and back.hit(ev, mpos): app.go("main_menu")
                for b, name, price in buy_btns:
                    if b.hit(ev, mpos):
                        if app.gs.gold >= price:
                            app.gs.gold -= price
                            app.naming = name
                            app.naming_text = ""
                            app.naming_active = True
                        else:
                            app.notify("Not enough gold!", RED)

            # ── BATTLE ARENA ──
            elif app.screen == "battle_arena":
                back, arena_btns = frame_btns.get("battle_arena",(None,[]))
                if back and back.hit(ev, mpos): app.go("main_menu")
                for b, ai in arena_btns:
                    if b.hit(ev, mpos):
                        arena = ARENAS[ai]
                        eligible = [d for d in app.gs.dragons if d.level >= arena["min_lv"]]
                        if eligible:
                            pd = random.choice(eligible)
                            pd.recalc()  # full HP
                            en = DRAGONS[random.choice(arena["pool"])]
                            en_lv = random.randint(arena["min_lv"], arena["min_lv"]+3)
                            enemy = Dragon(name=random.choice(arena["pool"]),
                                           template=random.choice(arena["pool"]))
                            enemy.level = en_lv; enemy.recalc()
                            app.battle = {
                                "player": pd, "enemy": enemy,
                                "arena": arena, "phase": "pick_action"
                            }
                            app.battle_log = [{"text":f"{pd.name} vs {enemy.name}!", "color":YELLOW}]
                            app.go("battle_fight")

            # ── BATTLE FIGHT ──
            elif app.screen == "battle_fight":
                atk_btn, flee_btn, third_btn = frame_btns.get("battle_fight",(None,None,None))
                phase = app.battle.get("phase","")
                if phase == "pick_action":
                    if atk_btn and atk_btn.hit(ev, mpos):
                        battle_attack(app)
                    elif flee_btn and flee_btn.hit(ev, mpos):
                        app.notify("You fled!", ORANGE)
                        app.go("battle_arena")
                    elif third_btn and third_btn.hit(ev, mpos):  # skip
                        # Enemy attacks only
                        ed = app.battle["enemy"]; pd = app.battle["player"]
                        edmg = max(1, ed.atk - pd.df//2 + random.randint(-4,8))
                        pd.hp = max(0,pd.hp-edmg)
                        app.battle_log.append({"text":f"You skipped. Enemy dealt {edmg}!", "color":RED})
                        if not pd.is_alive(): _battle_end(app, won=False)
                elif phase == "result":
                    if third_btn and third_btn.hit(ev, mpos):  # Continue btn
                        app.go("main_menu")

            # ── BREEDING ──
            elif app.screen == "breeding":
                back, ready_btns, breed_btns, breed_go = frame_btns.get("breeding",(None,[],[],None))
                if back and back.hit(ev, mpos): app.go("main_menu")
                for b, i in ready_btns:
                    if b.hit(ev, mpos):
                        slot = app.gs.breeding_slots[i]
                        app.naming = slot["template"]
                        app.naming_text = ""
                        app.naming_active = True
                        app._hatch_idx = i
                for b, i in breed_btns:
                    if b.hit(ev, mpos):
                        if i in app.breed_select:
                            app.breed_select.remove(i)
                        elif len(app.breed_select) < 2:
                            app.breed_select.append(i)
                if breed_go and breed_go.hit(ev, mpos):
                    if len(app.breed_select) == 2 and app.gs.gold >= 100:
                        d1 = app.gs.dragons[app.breed_select[0]]
                        d2 = app.gs.dragons[app.breed_select[1]]
                        key = frozenset([d1.primary_elem, d2.primary_elem])
                        result = BREEDING.get(key, random.choice([d1.template, d2.template]))
                        turns = 3 if DRAGONS[result]["rarity"] in ("Common","Uncommon") else 5
                        app.gs.gold -= 100
                        app.gs.breeding_slots.append({"template":result,"turns_left":turns})
                        app.breed_select = []
                        app.notify(f"Breeding {result}! Ready in {turns} battles.", CYAN)

            # ── DAILY ──
            elif app.screen == "daily":
                b = frame_btns.get("daily")
                if b and b.hit(ev, mpos): app.go("main_menu")

            # ── NAMING DIALOG ──
            if app.naming:
                ok, skip_b = frame_btns.get("naming",(None,None))
                if ev.type == pygame.KEYDOWN and app.naming_active:
                    if ev.key == pygame.K_BACKSPACE:
                        app.naming_text = app.naming_text[:-1]
                    elif ev.key == pygame.K_RETURN:
                        pass
                    elif len(app.naming_text) < 20:
                        app.naming_text += ev.unicode
                if ev.type == pygame.MOUSEBUTTONDOWN:
                    app.naming_active = True
                def finish_naming(name):
                    tname = app.naming
                    # Check if hatching from breeding
                    if hasattr(app,"_hatch_idx"):
                        app.gs.breeding_slots.pop(app._hatch_idx)
                        del app._hatch_idx
                    dr = Dragon(name=name or tname, template=tname)
                    app.gs.dragons.append(dr)
                    app.notify(f"{dr.name} joined your team!", GOLD)
                    app.naming = None
                if ok and ok.hit(ev, mpos):
                    finish_naming(app.naming_text.strip())
                if skip_b and skip_b.hit(ev, mpos):
                    finish_naming("")

        # ─────────────────────────────────────────
        #  DRAW
        # ─────────────────────────────────────────
        screen.fill(BG)

        if app.screen == "splash":
            result = draw_splash(app)
            frame_btns["splash"] = result

        elif app.screen == "new_game":
            result = draw_new_game(app)
            frame_btns["new_game"] = result

        elif app.screen == "main_menu":
            result = draw_main_menu(app)
            frame_btns["main_menu"] = result

        elif app.screen == "collection":
            result = draw_collection(app)
            frame_btns["collection"] = result

        elif app.screen == "shop":
            result = draw_shop(app)
            frame_btns["shop"] = result

        elif app.screen == "battle_arena":
            result = draw_battle_arena(app)
            frame_btns["battle_arena"] = result

        elif app.screen == "battle_fight":
            result = draw_battle_fight(app)
            frame_btns["battle_fight"] = result

        elif app.screen == "breeding":
            result = draw_breeding(app)
            frame_btns["breeding"] = result

        elif app.screen == "daily":
            result = draw_daily(app)
            frame_btns["daily"] = result

        # Naming dialog (overlay)
        if app.naming:
            result = draw_name_dialog(app)
            frame_btns["naming"] = result

        pygame.display.flip()

if __name__ == "__main__":
    main()
