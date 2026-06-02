"""
Ben 10 Run - ENHANCED EDITION
Classic Ben 10 Theme · Detailed Alien Sprites · Vilgax & Cars · Synthesized Sounds

Made by Nishchal Soni
"""

import pygame
import random
import sys
import math
import numpy as np

# ─── Init ─────────────────────────────────────────────────────────────────────
pygame.init()

SOUND_OK = False
try:
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.mixer.init()
    SOUND_OK = True
except pygame.error:
    print("Warning: Audio unavailable. Running silently.")

WIDTH, HEIGHT = 960, 600
FPS = 60
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ben 10 Run – Enhanced Edition")
clock = pygame.time.Clock()

# ─── Colours ──────────────────────────────────────────────────────────────────
BLACK   = (0,   0,   0)
WHITE   = (255, 255, 255)
GREEN   = (0,   200,  50)
DARK_G  = (0,   120,  30)
GREY    = (80,  80,  80)
DGREY   = (40,  40,  40)
LGREY   = (160, 160, 160)
YELLOW  = (255, 220,  0)
RED     = (220,  30,  30)
DARK_R  = (140,  10,  10)
ORANGE  = (255, 140,  0)
PURPLE  = (130,   0, 200)
CYAN    = (0,   220, 220)
BLUE    = (30,   80, 200)
PINK    = (255,  80, 160)
GOLD    = (255, 200,   0)
NEON_G  = (57,  255,  20)
BROWN   = (120,  70,  20)
SKIN    = (220, 180, 130)
TEAL    = (0,   160, 140)
SILVER  = (200, 200, 215)
DARK_P  = (60,    0,  90)

import os

def load_high_score():
    if os.path.exists("highscore.txt"):
        with open("highscore.txt", "r") as f:
            try:
                return int(f.read())
            except ValueError:
                return 0
    return 0

def save_high_score(score):
    with open("highscore.txt", "w") as f:
        f.write(str(score))

# ─── Fonts ────────────────────────────────────────────────────────────────────
try:
    font_big   = pygame.font.SysFont("couriernew", 52, bold=True)
    font_med   = pygame.font.SysFont("couriernew", 30, bold=True)
    font_small = pygame.font.SysFont("couriernew", 22)
    font_xs    = pygame.font.SysFont("couriernew", 17)
except Exception:
    font_big = font_med = font_small = font_xs = pygame.font.Font(None, 30)


# ═══════════════════════════════════════════════════════════════════════════════
#  SOUND SYNTHESIS
# ═══════════════════════════════════════════════════════════════════════════════
def make_sound(freq=440, duration=0.12, wave="sine", vol=0.4, decay=True):
    """Generate a pygame Sound from a waveform."""
    if not SOUND_OK:
        return None
    rate = 44100
    n    = int(rate * duration)
    t    = np.linspace(0, duration, n, False)
    if wave == "sine":
        data = np.sin(2 * np.pi * freq * t)
    elif wave == "square":
        data = np.sign(np.sin(2 * np.pi * freq * t))
    elif wave == "sawtooth":
        data = 2 * (t * freq - np.floor(t * freq + 0.5))
    elif wave == "noise":
        data = np.random.uniform(-1, 1, n)
    else:
        data = np.sin(2 * np.pi * freq * t)

    if decay:
        env = np.linspace(1, 0, n)
        data = data * env

    data = (data * vol * 32767).astype(np.int16)
    data = np.column_stack([data, data])  # stereo
    snd  = pygame.sndarray.make_sound(data)
    return snd


def make_sweep(f0, f1, duration=0.15, vol=0.35):
    if not SOUND_OK:
        return None
    rate = 44100
    n    = int(rate * duration)
    t    = np.linspace(0, duration, n, False)
    freq = np.linspace(f0, f1, n)
    data = np.sin(2 * np.pi * np.cumsum(freq) / rate)
    env  = np.linspace(1, 0, n)
    data = (data * env * vol * 32767).astype(np.int16)
    data = np.column_stack([data, data])  # stereo
    return pygame.sndarray.make_sound(data)


def make_chord(freqs, duration=0.3, vol=0.25):
    if not SOUND_OK:
        return None
    rate = 44100
    n    = int(rate * duration)
    t    = np.linspace(0, duration, n, False)
    data = sum(np.sin(2 * np.pi * f * t) for f in freqs) / len(freqs)
    env  = np.concatenate([np.linspace(0, 1, n//8), np.linspace(1, 0, n - n//8)])
    data = (data * env * vol * 32767).astype(np.int16)
    data = np.column_stack([data, data])  # stereo
    return pygame.sndarray.make_sound(data)


# Pre-bake all sounds at startup
SFX = {}
if SOUND_OK:
    SFX["jump"]      = make_sweep(300, 700, 0.18, 0.4)
    SFX["land"]      = make_sound(180, 0.08, "noise", 0.3)
    SFX["coin"]      = make_chord([880, 1100, 1320], 0.18, 0.35)
    SFX["hit"]       = make_sound(120, 0.25, "square", 0.45)
    SFX["shield"]    = make_sweep(1000, 400, 0.22, 0.35)
    SFX["transform"] = make_sweep(400, 1600, 0.35, 0.45)
    SFX["slide"]     = make_sound(250, 0.10, "sawtooth", 0.2)
    SFX["die"]       = make_sweep(800, 100, 0.55, 0.4)
    SFX["menu_blip"] = make_sound(660, 0.08, "sine", 0.3)

def play(name):
    snd = SFX.get(name)
    if snd:
        snd.play()


# ═══════════════════════════════════════════════════════════════════════════════
#  ALIEN DEFINITIONS
# ═══════════════════════════════════════════════════════════════════════════════
ALIENS = [
    {"name": "BEN",         "color": (60,160,60),   "eye": YELLOW,      "power": "Human",        "speed_bonus": 0,  "jump_bonus": 0},
    {"name": "HEATBLAST",   "color": (210, 70,  5),  "eye": YELLOW,      "power": "Fire Shield",  "speed_bonus": 2,  "jump_bonus": 0},
    {"name": "FOUR ARMS",   "color": (180, 25, 25),  "eye": YELLOW,      "power": "Super Punch",  "speed_bonus": 0,  "jump_bonus": 2},
    {"name": "DIAMONDHEAD", "color": (80, 190,165),  "eye": (0,  0,  0), "power": "Crystal",      "speed_bonus": 1,  "jump_bonus": 1},
    {"name": "XLR8",        "color": (20,  20,170),  "eye": YELLOW,      "power": "Speed Dash",   "speed_bonus": 5,  "jump_bonus": 0},
    {"name": "GHOSTFREAK",  "color": (200,200,225),  "eye": (60, 0,100), "power": "Phase",        "speed_bonus": 0,  "jump_bonus": 3},
    {"name": "UPGRADE",     "color": (15, 170, 15),  "eye": (0,255,80),  "power": "Tech Boost",   "speed_bonus": 3,  "jump_bonus": 1},
]

# ─── SCENES ───────────────────────────────────────────────────────────────────
SCENES = [
    {"name": "Bellwood City",   "sky": [(25,110,195),(140,205,255)], "ground": (55,55,55),  "accent": YELLOW},
    {"name": "Mt. Rushmore",    "sky": [(75,115,155),(175,200,220)], "ground": (95,75,55),  "accent": ORANGE},
    {"name": "Null Void",       "sky": [(18,0,38),  (75,0,115)],     "ground": (55,0,75),   "accent": PURPLE},
    {"name": "Galactic Forest", "sky": [(5,18,5),   (18,55,18)],     "ground": (18,55,18),  "accent": NEON_G},
    {"name": "Alien City",      "sky": [(5,5,38),   (18,18,95)],     "ground": (28,28,55),  "accent": CYAN},
]


# ═══════════════════════════════════════════════════════════════════════════════
#  DRAWING HELPERS
# ═══════════════════════════════════════════════════════════════════════════════
def draw_omnitrix(surf, x, y, r=14, col=NEON_G):
    pygame.draw.circle(surf, (15, 15, 15), (x, y), r)
    pygame.draw.circle(surf, col, (x, y), r, 3)
    pygame.draw.ellipse(surf, col, (x - r//2, y - r//4, r, r//2))
    # small highlight
    pygame.draw.circle(surf, WHITE, (x - r//4, y - r//4), max(1, r//6))


def lerp_color(c1, c2, t):
    return tuple(int(c1[i] * (1-t) + c2[i] * t) for i in range(3))


def draw_rect_outline(surf, col, rect, width=2, radius=4):
    pygame.draw.rect(surf, col, rect, border_radius=radius)
    pygame.draw.rect(surf, WHITE, rect, width, border_radius=radius)


# ═══════════════════════════════════════════════════════════════════════════════
#  ALIEN SPRITES  — detailed, classic-accurate pixel art style
# ═══════════════════════════════════════════════════════════════════════════════

def draw_ben(surf, cx, cy, frame):
    """Ben Tennyson – green jacket, jeans, white shirt, Omnitrix."""
    # ── shoes ──
    pygame.draw.ellipse(surf, (20,20,20), (cx-16, cy+68, 16, 9))
    pygame.draw.ellipse(surf, (20,20,20), (cx+2,  cy+68, 16, 9))
    # ── jeans (legs) ──
    leg = int(math.sin(frame * 0.35) * 9)
    pygame.draw.rect(surf, (40, 80,160), (cx-15, cy+42, 12, 28+leg))
    pygame.draw.rect(surf, (40, 80,160), (cx+3,  cy+42, 12, 28-leg))
    # ── torso / green jacket ──
    pygame.draw.rect(surf, (50,140,50), (cx-17, cy+8, 34, 36))
    # white shirt stripe
    pygame.draw.rect(surf, WHITE, (cx-5, cy+8, 10, 20))
    # jacket collar
    pygame.draw.polygon(surf, (30,110,30), [(cx-17,cy+8),(cx-8,cy+22),(cx-17,cy+28)])
    pygame.draw.polygon(surf, (30,110,30), [(cx+17,cy+8),(cx+8,cy+22),(cx+17,cy+28)])
    # ── omnitrix ──
    draw_omnitrix(surf, cx, cy+26, 9, NEON_G)
    # ── arms ──
    arm = int(math.sin(frame * 0.35) * 13)
    pygame.draw.rect(surf, (50,140,50), (cx-28, cy+10+arm, 12, 26))
    pygame.draw.rect(surf, (50,140,50), (cx+16, cy+10-arm, 12, 26))
    pygame.draw.rect(surf, SKIN, (cx-28, cy+34+arm, 12, 8))
    pygame.draw.rect(surf, SKIN, (cx+16, cy+34-arm, 12, 8))
    # ── head ──
    pygame.draw.ellipse(surf, SKIN, (cx-15, cy-20, 30, 30))
    # hair (dark brown)
    pygame.draw.ellipse(surf, (50,30,10), (cx-15, cy-20, 30, 18))
    # ── eyes ──
    pygame.draw.ellipse(surf, WHITE, (cx-10, cy-12, 9, 7))
    pygame.draw.ellipse(surf, WHITE, (cx+1,  cy-12, 9, 7))
    pygame.draw.circle(surf, (30,100,200), (cx-6,  cy-10), 3)
    pygame.draw.circle(surf, (30,100,200), (cx+5,  cy-10), 3)
    pygame.draw.circle(surf, BLACK, (cx-6, cy-10), 2)
    pygame.draw.circle(surf, BLACK, (cx+5, cy-10), 2)
    # ── mouth ──
    pygame.draw.arc(surf, (160,80,60), (cx-6, cy-4, 12, 7), math.pi, 2*math.pi, 2)


def draw_heatblast(surf, cx, cy, frame):
    """Heatblast – lava body, fire crown, rocky shoulders."""
    # flame glow behind
    glow_r = 40 + int(math.sin(frame*0.18)*5)
    glow_surf = pygame.Surface((glow_r*2, glow_r*2), pygame.SRCALPHA)
    pygame.draw.circle(glow_surf, (255,80,0,55), (glow_r, glow_r), glow_r)
    surf.blit(glow_surf, (cx - glow_r, cy + 5 - glow_r))

    leg = int(math.sin(frame*0.35)*9)
    # legs (lava)
    pygame.draw.rect(surf, (180,40,0),  (cx-15, cy+42, 12, 26+leg))
    pygame.draw.rect(surf, (180,40,0),  (cx+3,  cy+42, 12, 26-leg))
    # feet
    pygame.draw.ellipse(surf, (100,20,0), (cx-16, cy+66+leg, 15, 8))
    pygame.draw.ellipse(surf, (100,20,0), (cx+2,  cy+66-leg, 15, 8))
    # body
    pygame.draw.ellipse(surf, (210,70,5), (cx-18, cy+6, 36, 38))
    # lava cracks on body
    pygame.draw.line(surf, YELLOW, (cx-10, cy+12), (cx-5, cy+22), 2)
    pygame.draw.line(surf, YELLOW, (cx+8,  cy+16), (cx+4,  cy+28), 2)
    # arms
    arm = int(math.sin(frame*0.35)*13)
    pygame.draw.rect(surf, (200,60,0), (cx-28, cy+10+arm, 12, 28))
    pygame.draw.rect(surf, (200,60,0), (cx+16, cy+10-arm, 12, 28))
    # head (rocky/lava)
    pygame.draw.ellipse(surf, (180,45,0), (cx-16, cy-20, 32, 32))
    pygame.draw.ellipse(surf, (220,80,10), (cx-12, cy-16, 24, 24))
    # eyes (bright yellow)
    pygame.draw.ellipse(surf, YELLOW, (cx-10, cy-12, 10, 8))
    pygame.draw.ellipse(surf, YELLOW, (cx+1,  cy-12, 10, 8))
    pygame.draw.ellipse(surf, (255,200,0), (cx-8, cy-11, 7, 5))
    pygame.draw.ellipse(surf, (255,200,0), (cx+2, cy-11, 7, 5))
    # flame crown
    for i in range(5):
        fx = cx - 18 + i * 9
        fh = random.randint(10, 22)
        fc = lerp_color(RED, YELLOW, random.random())
        pygame.draw.ellipse(surf, fc, (fx - 4, cy - 30 - fh, 9, fh+4))
    # shoulder rocks
    pygame.draw.ellipse(surf, (120,40,0), (cx-30, cy+5, 16, 12))
    pygame.draw.ellipse(surf, (120,40,0), (cx+14, cy+5, 16, 12))
    # omnitrix
    draw_omnitrix(surf, cx, cy+22, 9, NEON_G)


def draw_four_arms(surf, cx, cy, frame):
    """Four Arms – big red alien, four arms, black stripes."""
    leg = int(math.sin(frame*0.35)*9)
    # thick legs
    pygame.draw.rect(surf, (160,20,20), (cx-18, cy+42, 16, 28+leg))
    pygame.draw.rect(surf, (160,20,20), (cx+2,  cy+42, 16, 28-leg))
    pygame.draw.ellipse(surf, (100,10,10), (cx-19, cy+68+leg, 18, 10))
    pygame.draw.ellipse(surf, (100,10,10), (cx+1,  cy+68-leg, 18, 10))
    # wide body
    pygame.draw.ellipse(surf, (175,22,22), (cx-24, cy+4, 48, 42))
    # black stripe
    pygame.draw.rect(surf, BLACK, (cx-12, cy+14, 24, 6))
    # omnitrix
    draw_omnitrix(surf, cx, cy+22, 10, NEON_G)
    # four arms
    arm = int(math.sin(frame*0.35)*13)
    # upper pair
    pygame.draw.rect(surf, (160,20,20), (cx-38, cy+8+arm,  14, 30))
    pygame.draw.rect(surf, (160,20,20), (cx+24, cy+8-arm,  14, 30))
    # lower pair
    pygame.draw.rect(surf, (160,20,20), (cx-36, cy+32-arm, 13, 24))
    pygame.draw.rect(surf, (160,20,20), (cx+23, cy+32+arm, 13, 24))
    # fists
    for ox, oy in [(-38, 36+arm), (24, 36-arm), (-36, 54-arm), (23, 54+arm)]:
        pygame.draw.ellipse(surf, (120,10,10), (cx+ox, cy+oy, 15, 12))
    # big head
    pygame.draw.ellipse(surf, (175,22,22), (cx-20, cy-22, 40, 36))
    # yellow eyes (4 eyes)
    for ex in [-12, -4, 4, 12]:
        pygame.draw.ellipse(surf, YELLOW, (cx+ex-3, cy-14, 6, 7))
        pygame.draw.ellipse(surf, BLACK,  (cx+ex-2, cy-13, 4, 5))
    # black head stripes
    pygame.draw.line(surf, BLACK, (cx-18, cy-8), (cx+18, cy-8), 3)
    pygame.draw.line(surf, BLACK, (cx-18, cy-2), (cx+18, cy-2), 3)


def draw_diamondhead(surf, cx, cy, frame):
    """Diamondhead – crystal faceted body, sharp head shard."""
    leg = int(math.sin(frame*0.35)*9)
    pygame.draw.rect(surf, TEAL, (cx-14, cy+42, 12, 26+leg))
    pygame.draw.rect(surf, TEAL, (cx+2,  cy+42, 12, 26-leg))
    pygame.draw.ellipse(surf, (0,120,100), (cx-15, cy+66+leg, 15, 9))
    pygame.draw.ellipse(surf, (0,120,100), (cx+2,  cy+66-leg, 15, 9))
    # body – faceted diamond polygon
    body_pts = [(cx, cy+4),(cx+22,cy+14),(cx+18,cy+46),(cx-18,cy+46),(cx-22,cy+14)]
    pygame.draw.polygon(surf, TEAL, body_pts)
    pygame.draw.polygon(surf, CYAN, body_pts, 2)
    # facet lines for 3-D look
    pygame.draw.line(surf, CYAN, (cx, cy+4), (cx, cy+46), 1)
    pygame.draw.line(surf, CYAN, (cx, cy+25),(cx+22,cy+14), 1)
    pygame.draw.line(surf, CYAN, (cx, cy+25),(cx-22,cy+14), 1)
    # omnitrix
    draw_omnitrix(surf, cx, cy+28, 9, NEON_G)
    # arms
    arm = int(math.sin(frame*0.35)*13)
    pygame.draw.rect(surf, TEAL, (cx-30, cy+12+arm, 12, 24))
    pygame.draw.rect(surf, TEAL, (cx+18, cy+12-arm, 12, 24))
    # crystal shard hands
    pygame.draw.polygon(surf, CYAN, [(cx-30, cy+34+arm),(cx-24,cy+34+arm),(cx-28,cy+44+arm)])
    pygame.draw.polygon(surf, CYAN, [(cx+18, cy+34-arm),(cx+24,cy+34-arm),(cx+22,cy+44-arm)])
    # faceted head
    head_pts = [(cx, cy-26),(cx+14,cy-16),(cx+14,cy-4),(cx-14,cy-4),(cx-14,cy-16)]
    pygame.draw.polygon(surf, TEAL, head_pts)
    pygame.draw.polygon(surf, CYAN, head_pts, 2)
    # crystal spike on top
    pygame.draw.polygon(surf, CYAN, [(cx, cy-36),(cx-8, cy-22),(cx+8, cy-22)])
    pygame.draw.polygon(surf, WHITE,[(cx, cy-36),(cx-4, cy-28),(cx+4, cy-28)], 1)
    # eyes
    pygame.draw.ellipse(surf, BLACK, (cx-9, cy-14, 9, 7))
    pygame.draw.ellipse(surf, BLACK, (cx+1, cy-14, 9, 7))
    pygame.draw.circle(surf, (0,200,180), (cx-5, cy-11), 2)
    pygame.draw.circle(surf, (0,200,180), (cx+5, cy-11), 2)


def draw_xlr8(surf, cx, cy, frame):
    """XLR8 – sleek blue raptor, visor helmet, tail, speed trails."""
    # speed trail
    for i in range(5):
        alpha = 180 - i * 35
        trail_x = cx - 20 - i * 14
        trail_col = (20, 80+i*10, 200)
        pygame.draw.ellipse(surf, trail_col, (trail_x, cy+20, 18-i*2, 8-i))
    # tail
    tail_pts = [(cx+2, cy+45),(cx+8, cy+58),(cx+20, cy+65),(cx+30, cy+60)]
    pygame.draw.lines(surf, (20,20,160), False, tail_pts, 5)
    leg = int(math.sin(frame*0.35)*9)
    # slim legs (digitigrade)
    pygame.draw.polygon(surf, (20,20,170), [(cx-14,cy+42),(cx-8,cy+42),(cx-4,cy+60+leg),(cx-16,cy+58+leg)])
    pygame.draw.polygon(surf, (20,20,170), [(cx+4,cy+42),(cx+14,cy+42),(cx+16,cy+60-leg),(cx+4,cy+58-leg)])
    # claws
    for dx in [-14, 2]:
        pygame.draw.polygon(surf, BLACK, [(cx+dx, cy+70),(cx+dx+5,cy+70),(cx+dx+3,cy+78)])
    # slim body
    pygame.draw.ellipse(surf, (25,25,175), (cx-16, cy+8, 32, 36))
    # omnitrix
    draw_omnitrix(surf, cx, cy+24, 9, NEON_G)
    # arms
    arm = int(math.sin(frame*0.35)*13)
    pygame.draw.rect(surf, (20,20,170), (cx-26, cy+10+arm, 10, 22))
    pygame.draw.rect(surf, (20,20,170), (cx+16, cy+10-arm, 10, 22))
    # head with visor helmet
    pygame.draw.ellipse(surf, (20,20,160), (cx-14, cy-20, 28, 28))
    # helmet top ridge
    pygame.draw.ellipse(surf, (10,10,100), (cx-14, cy-20, 28, 16))
    # visor
    pygame.draw.ellipse(surf, CYAN, (cx-11, cy-14, 22, 10))
    pygame.draw.ellipse(surf, (100,230,255), (cx-9, cy-13, 18, 7))


def draw_ghostfreak(surf, cx, cy, frame):
    """Ghostfreak – translucent ghost, wispy tail, single cyclopean eye."""
    # ghost glow
    glow_surf = pygame.Surface((80, 80), pygame.SRCALPHA)
    pygame.draw.ellipse(glow_surf, (180,180,220,40), (0,0,80,80))
    surf.blit(glow_surf, (cx-40, cy-10))
    # wispy tail instead of legs
    t_off = math.sin(frame*0.12)*8
    tail_pts = [(cx,cy+45),(cx+int(t_off),cy+60),(cx-int(t_off),cy+72),(cx+int(t_off*0.5),cy+84)]
    pygame.draw.lines(surf, (160,160,200), False, tail_pts, 7)
    pygame.draw.lines(surf, (210,210,240), False, tail_pts, 3)
    # body (semi-transparent effect: lighter outline)
    pygame.draw.ellipse(surf, (185,185,215), (cx-17, cy+5, 34, 38))
    pygame.draw.ellipse(surf, (220,220,240), (cx-17, cy+5, 34, 38), 2)
    # dark strip across body
    pygame.draw.rect(surf, (30,0,50), (cx-16, cy+14, 32, 12))
    pygame.draw.rect(surf, (80,0,120), (cx-16, cy+14, 32, 12), 1)
    # omnitrix
    draw_omnitrix(surf, cx, cy+24, 9, NEON_G)
    # arms (wispy)
    arm = int(math.sin(frame*0.35)*13)
    arm_col = (185,185,215)
    pygame.draw.rect(surf, arm_col, (cx-26, cy+10+arm, 10, 22))
    pygame.draw.rect(surf, arm_col, (cx+16, cy+10-arm, 10, 22))
    # head
    pygame.draw.ellipse(surf, (195,195,225), (cx-15, cy-20, 30, 30))
    pygame.draw.ellipse(surf, (220,220,240), (cx-15, cy-20, 30, 30), 2)
    # single large eye
    pygame.draw.ellipse(surf, (60,0,100), (cx-9, cy-14, 18, 14))
    pygame.draw.ellipse(surf, (120,0,180), (cx-7, cy-12, 14, 10))
    pygame.draw.ellipse(surf, WHITE, (cx-4, cy-10, 8, 6))
    pygame.draw.circle(surf, BLACK, (cx, cy-8), 3)
    pygame.draw.circle(surf, WHITE, (cx+1, cy-10), 1)


def draw_upgrade(surf, cx, cy, frame):
    """Upgrade – living machine, circuit lines, glowing green eye."""
    leg = int(math.sin(frame*0.35)*9)
    pygame.draw.rect(surf, (10,130,10), (cx-14, cy+42, 12, 26+leg))
    pygame.draw.rect(surf, (10,130,10), (cx+2,  cy+42, 12, 26-leg))
    pygame.draw.rect(surf, (5,80,5), (cx-15, cy+66+leg, 14, 9))
    pygame.draw.rect(surf, (5,80,5), (cx+2,  cy+66-leg, 14, 9))
    # body
    pygame.draw.ellipse(surf, (10,130,10), (cx-18, cy+5, 36, 38))
    # circuit lines on body
    pygame.draw.line(surf, NEON_G, (cx-18, cy+12), (cx+18, cy+12), 2)
    pygame.draw.line(surf, NEON_G, (cx-18, cy+26), (cx+18, cy+26), 2)
    pygame.draw.line(surf, NEON_G, (cx-18, cy+38), (cx+18, cy+38), 2)
    pygame.draw.line(surf, NEON_G, (cx-8, cy+5), (cx-8, cy+43), 2)
    pygame.draw.line(surf, NEON_G, (cx+8, cy+5), (cx+8, cy+43), 2)
    # node dots
    for nx, ny in [(-8,12),(-8,26),(-8,38),(8,12),(8,26),(8,38)]:
        pygame.draw.circle(surf, (0,255,80), (cx+nx, cy+ny), 3)
    # omnitrix
    draw_omnitrix(surf, cx, cy+22, 9, NEON_G)
    # arms
    arm = int(math.sin(frame*0.35)*13)
    pygame.draw.rect(surf, (10,130,10), (cx-28, cy+10+arm, 12, 26))
    pygame.draw.rect(surf, (10,130,10), (cx+16, cy+10-arm, 12, 26))
    pygame.draw.line(surf, NEON_G, (cx-28, cy+20+arm), (cx-16, cy+20+arm), 2)
    pygame.draw.line(surf, NEON_G, (cx+16, cy+20-arm), (cx+28, cy+20-arm), 2)
    # head – round with circuit face
    pygame.draw.ellipse(surf, (10,130,10), (cx-16, cy-22, 32, 30))
    # circuit lines on head
    pygame.draw.line(surf, NEON_G, (cx-16, cy-10), (cx+16, cy-10), 2)
    pygame.draw.line(surf, NEON_G, (cx-16, cy-4),  (cx+16, cy-4),  2)
    # single glowing eye
    pygame.draw.ellipse(surf, (0,200,50), (cx-6, cy-16, 12, 9))
    pygame.draw.ellipse(surf, NEON_G,    (cx-4, cy-15,  8,  6))
    pygame.draw.circle(surf, WHITE, (cx, cy-13), 2)


ALIEN_DRAW_FNS = [draw_ben, draw_heatblast, draw_four_arms, draw_diamondhead,
                  draw_xlr8, draw_ghostfreak, draw_upgrade]


def draw_character(surf, alien_idx, x, y, frame, shield=False, sliding=False):
    idx = alien_idx % len(ALIENS)
    bob = int(math.sin(frame * 0.18) * 3)
    cx  = int(x + 25)
    cy  = int(y + bob)

    if sliding:
        # squash transform
        cy += 30

    if shield:
        r = 48 + int(math.sin(frame*0.22)*4)
        shield_surf = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
        pygame.draw.circle(shield_surf, (57,255,20,60), (r,r), r)
        pygame.draw.circle(shield_surf, (57,255,20,120),(r,r), r, 3)
        surf.blit(shield_surf, (cx-r, cy+20-r))

    ALIEN_DRAW_FNS[idx](surf, cx, cy, frame)


# ═══════════════════════════════════════════════════════════════════════════════
#  OBSTACLE SPRITES — Vilgax, Cars, Drone, Cultist, Fire
# ═══════════════════════════════════════════════════════════════════════════════

def draw_vilgax(surf, ox, oy, frame):
    """Vilgax – tall green alien warlord with red eyes and tentacle face."""
    # cape
    pygame.draw.polygon(surf, (80,0,0),  [(ox+20,oy+10),(ox+48,oy+70),(ox-8,oy+70)])
    # body armour
    pygame.draw.rect(surf, (30,70,30), (ox+2, oy+18, 36, 42))
    pygame.draw.rect(surf, (50,100,50),(ox+2, oy+18, 36, 42), 2)
    # armour details
    pygame.draw.rect(surf, (0,50,0), (ox+10, oy+22, 20, 10))
    pygame.draw.line(surf, (0,200,80),(ox+10,oy+26),(ox+30,oy+26),2)
    # belt
    pygame.draw.rect(surf, (100,20,20),(ox+2, oy+56, 36, 6))
    # legs
    pygame.draw.rect(surf, (20,55,20),(ox+4,  oy+62, 13, 22))
    pygame.draw.rect(surf, (20,55,20),(ox+23, oy+62, 13, 22))
    pygame.draw.rect(surf, (10,30,10),(ox+3,  oy+82, 15, 7))
    pygame.draw.rect(surf, (10,30,10),(ox+22, oy+82, 15, 7))
    # shoulders (spiky)
    pygame.draw.polygon(surf, (50,100,50),[(ox-6,oy+18),(ox+8,oy+10),(ox+8,oy+28)])
    pygame.draw.polygon(surf, (50,100,50),[(ox+46,oy+18),(ox+32,oy+10),(ox+32,oy+28)])
    # arms
    arm = int(math.sin(frame*0.08)*8)
    pygame.draw.rect(surf, (30,70,30),(ox-8,  oy+22+arm, 12, 26))
    pygame.draw.rect(surf, (30,70,30),(ox+36, oy+22-arm, 12, 26))
    # head
    pygame.draw.ellipse(surf, (30,80,30),(ox+4, oy-4, 32, 28))
    # tentacles on face
    for i in range(4):
        tx = ox + 8 + i * 8
        ty = oy + 24
        tip_y = ty + 10 + int(math.sin(frame*0.15 + i)*4)
        pygame.draw.line(surf, (0,50,0),(tx, ty),(tx-2+i, tip_y), 3)
    # red eyes
    pygame.draw.ellipse(surf, RED, (ox+8,  oy+2, 10, 7))
    pygame.draw.ellipse(surf, RED, (ox+22, oy+2, 10, 7))
    pygame.draw.ellipse(surf, (255,80,80),(ox+10, oy+3, 6, 4))
    pygame.draw.ellipse(surf, (255,80,80),(ox+24, oy+3, 6, 4))
    # forehead ridge
    pygame.draw.rect(surf, (20,60,20),(ox+4, oy-4, 32, 8))
    pygame.draw.line(surf, (0,180,60),(ox+4, oy+1),(ox+36,oy+1),2)


def draw_car(surf, ox, oy, col=(200,20,20)):
    """Bellwood-style muscle car / sedan."""
    # shadow
    pygame.draw.ellipse(surf, (20,20,20,80), (ox-4, oy+34, 72, 10))
    # body lower
    pygame.draw.rect(surf, col,         (ox, oy+14, 64, 24), border_radius=4)
    # body upper (cabin)
    pygame.draw.rect(surf, lerp_color(col,(30,30,30),0.3), (ox+8, oy+2, 44, 16), border_radius=6)
    # windshield
    pygame.draw.rect(surf, (120,200,240),(ox+10, oy+4, 18, 12), border_radius=2)
    # rear window
    pygame.draw.rect(surf, (120,200,240),(ox+36, oy+4, 14, 12), border_radius=2)
    # headlights
    pygame.draw.rect(surf, YELLOW,  (ox+56, oy+16, 8, 6), border_radius=2)
    pygame.draw.rect(surf, (255,255,180),(ox+57,oy+17, 6, 4), border_radius=1)
    # taillights
    pygame.draw.rect(surf, RED,     (ox, oy+16, 7, 6), border_radius=2)
    # bumpers
    pygame.draw.rect(surf, SILVER,  (ox+58, oy+26, 8, 5), border_radius=2)
    pygame.draw.rect(surf, SILVER,  (ox,    oy+26, 8, 5), border_radius=2)
    # wheels
    for wx in [ox+8, ox+46]:
        pygame.draw.circle(surf, (20,20,20), (wx, oy+36), 12)
        pygame.draw.circle(surf, LGREY,      (wx, oy+36), 9)
        pygame.draw.circle(surf, (80,80,80), (wx, oy+36), 5)
        pygame.draw.circle(surf, SILVER,     (wx, oy+36), 2)
    # grill lines
    for i in range(3):
        pygame.draw.line(surf, lerp_color(col,(255,255,255),0.3),
                         (ox+58, oy+17+i*3),(ox+62, oy+17+i*3), 1)


def draw_drone(surf, ox, oy, frame):
    """Alien surveillance drone – hovering."""
    hover = int(math.sin(frame*0.22)*5)
    dy    = oy + hover
    # glow beneath
    glow = pygame.Surface((50,20), pygame.SRCALPHA)
    pygame.draw.ellipse(glow, (0,200,255,50),(0,0,50,20))
    surf.blit(glow, (ox-8, dy+20))
    # body
    pygame.draw.ellipse(surf, (40,40,80), (ox, dy, 36, 18))
    pygame.draw.ellipse(surf, CYAN,       (ox, dy, 36, 18), 2)
    # dome
    pygame.draw.ellipse(surf, (80,80,140),(ox+6, dy-8, 24, 14))
    pygame.draw.ellipse(surf, CYAN,       (ox+6, dy-8, 24, 14), 1)
    # rotors
    ang = (frame * 18) % 360
    for i in range(4):
        a   = math.radians(ang + i*90)
        rx  = int(ox + 18 + math.cos(a)*20)
        ry  = int(dy +  4 + math.sin(a)*5)
        pygame.draw.line(surf, LGREY, (ox+18, dy+4), (rx, ry), 2)
        pygame.draw.circle(surf, GREY, (rx, ry), 4)
    # eye sensor
    pygame.draw.circle(surf, RED, (ox+18, dy+5), 5)
    pygame.draw.circle(surf, (255,80,80),(ox+18, dy+5), 3)


def draw_cultist(surf, ox, oy, frame):
    """Forever Knight cultist in armour."""
    leg = int(math.sin(frame*0.15)*6)
    # legs
    pygame.draw.rect(surf, (60,60,80),(ox+4,  oy+52, 10, 20+leg))
    pygame.draw.rect(surf, (60,60,80),(ox+20, oy+52, 10, 20-leg))
    pygame.draw.rect(surf, (40,40,60),(ox+3,  oy+70+leg, 12, 7))
    pygame.draw.rect(surf, (40,40,60),(ox+19, oy+70-leg, 12, 7))
    # body armour
    pygame.draw.rect(surf, (80,80,110),(ox+2, oy+16, 32, 38))
    pygame.draw.rect(surf, SILVER,     (ox+2, oy+16, 32, 38), 2)
    # cross emblem
    pygame.draw.rect(surf, YELLOW, (ox+15, oy+22,  5, 14))
    pygame.draw.rect(surf, YELLOW, (ox+10, oy+26, 15,  5))
    # arms
    arm = int(math.sin(frame*0.15)*10)
    pygame.draw.rect(surf, (80,80,110),(ox-8, oy+18+arm, 12, 22))
    pygame.draw.rect(surf, (80,80,110),(ox+32,oy+18-arm, 12, 22))
    # sword in right hand
    pygame.draw.rect(surf, SILVER, (ox+36, oy+10-arm, 4, 38))
    pygame.draw.rect(surf, GOLD,   (ox+28, oy+18-arm, 20,  4))
    # helmet
    pygame.draw.ellipse(surf, (70,70,100),(ox+4, oy-6, 28, 26))
    pygame.draw.rect(surf, (50,50,80),    (ox+4, oy+4,  28, 12))
    # visor slit
    pygame.draw.rect(surf, (20,20,20),(ox+6,  oy+5, 24, 5))
    pygame.draw.rect(surf, RED,       (ox+8,  oy+6, 20, 3))


def draw_fire_orb(surf, ox, oy, frame):
    """Spinning fire hazard."""
    for i in range(6):
        a  = math.radians(frame * 5 + i * 60)
        fx = int(ox + 18 + math.cos(a) * 14)
        fy = int(oy + 18 + math.sin(a) * 14)
        fc = lerp_color(RED, YELLOW, (i/6 + frame*0.05) % 1.0)
        pygame.draw.circle(surf, fc, (fx, fy), 8 - i)
    pygame.draw.circle(surf, ORANGE, (ox+18, oy+18), 12)
    pygame.draw.circle(surf, YELLOW, (ox+18, oy+18), 7)
    pygame.draw.circle(surf, WHITE,  (ox+18, oy+18), 3)


# ═══════════════════════════════════════════════════════════════════════════════
#  BACKGROUND
# ═══════════════════════════════════════════════════════════════════════════════
def draw_background(surf, scene_idx, scroll, stars):
    sc   = SCENES[scene_idx]
    c1, c2 = sc["sky"]

    # gradient sky (every 2 pixels for speed)
    for row in range(0, HEIGHT, 2):
        t = row / HEIGHT
        r = int(c1[0]*(1-t)+c2[0]*t)
        g = int(c1[1]*(1-t)+c2[1]*t)
        b = int(c1[2]*(1-t)+c2[2]*t)
        pygame.draw.line(surf, (r,g,b), (0,row),(WIDTH,row+1))

    # parallax stars
    for sx, sy, ss in stars:
        sx2 = (sx - scroll * 0.08) % WIDTH
        pygame.draw.circle(surf, WHITE, (int(sx2), sy), ss)

    gc = sc["ground"]
    ac = sc["accent"]
    gx = int(scroll * 0.5) % max(1, WIDTH)

    if scene_idx == 0:  # Bellwood city
        for bx in range(-1, WIDTH//110+2):
            bw = 75 + ((bx*37) % 38)
            bh = 85 + ((bx*73) % 145)
            rx = bx*110 - gx % 110
            pygame.draw.rect(surf, DGREY,  (rx, HEIGHT-200-bh, bw, bh))
            pygame.draw.rect(surf, GREY,   (rx, HEIGHT-200-bh, bw, bh), 2)
            # roof water tower
            pygame.draw.rect(surf, BROWN, (rx+bw//2-6, HEIGHT-200-bh-18, 12, 18))
            pygame.draw.ellipse(surf, BROWN,(rx+bw//2-10, HEIGHT-200-bh-22, 20, 10))
            for wy in range(bh//30):
                for wx in range(bw//24):
                    lit = (bx+wy+wx) % 3 != 0
                    col = YELLOW if lit else (20,18,5)
                    pygame.draw.rect(surf, col, (rx+5+wx*24, HEIGHT-194-bh+wy*30, 13, 15))

    elif scene_idx == 1:  # Mt Rushmore
        for mx in range(-1, WIDTH//190+2):
            rx = mx*190 - gx % 190
            pts = [(rx,HEIGHT-200),(rx+95,HEIGHT-345),(rx+190,HEIGHT-200)]
            pygame.draw.polygon(surf, (95,75,55), pts)
            pygame.draw.polygon(surf, (75,55,35), pts, 2)
            # snow cap
            pygame.draw.polygon(surf, WHITE, [(rx+70,HEIGHT-300),(rx+95,HEIGHT-345),(rx+120,HEIGHT-300)])

    elif scene_idx == 2:  # Null Void
        t_now = pygame.time.get_ticks() / 1000
        for rx2 in range(-1, WIDTH//140+2):
            rrx = rx2*140 - gx % 140
            ry  = HEIGHT - 300 + int(math.sin(t_now + rx2*0.8)*20)
            pygame.draw.ellipse(surf, (75,0,95), (rrx, ry, 115, 38))
            pygame.draw.ellipse(surf, PURPLE,    (rrx, ry, 115, 38), 2)

    elif scene_idx == 3:  # Galactic Forest
        for tx in range(-1, WIDTH//85+2):
            rx = tx*85 - gx % 85
            trunk_col = (55,28,8)
            pygame.draw.rect(surf, trunk_col, (rx+28, HEIGHT-250, 18, 85))
            pygame.draw.circle(surf, DARK_G,  (rx+37, HEIGHT-265), 48)
            pygame.draw.circle(surf, (0,160,40),(rx+37,HEIGHT-275), 28)
            # bioluminescent dots
            for _ in range(4):
                dx = random.randint(-25,25)
                dy = random.randint(-30,10)
                pygame.draw.circle(surf, NEON_G, (rx+37+dx, HEIGHT-265+dy), 2)

    elif scene_idx == 4:  # Alien city neon
        for bx in range(-1, WIDTH//95+2):
            bh = 95 + ((bx*53) % 125)
            rx = bx*95 - gx % 95
            pygame.draw.rect(surf, (8,8,45), (rx, HEIGHT-200-bh, 78, bh))
            pygame.draw.rect(surf, ac,       (rx, HEIGHT-200-bh, 78, bh), 2)
            # antenna
            pygame.draw.line(surf, ac, (rx+39, HEIGHT-200-bh),(rx+39,HEIGHT-200-bh-18),3)
            pygame.draw.circle(surf, ac,(rx+39, HEIGHT-200-bh-18), 4)
            # neon window strips
            for wy in range(bh//28):
                stripe_col = lerp_color(CYAN, PURPLE, (bx+wy)*0.17 % 1.0)
                pygame.draw.rect(surf, stripe_col,(rx+4, HEIGHT-196-bh+wy*28, 70, 8))

    # ground slab
    pygame.draw.rect(surf, gc, (0, HEIGHT-200, WIDTH, 200))
    # ground accent line
    pygame.draw.rect(surf, ac, (0, HEIGHT-200, WIDTH, 4))
    # lane dashes
    lane_scroll = int(scroll) % 80
    for lx in range(-80, WIDTH+80, 80):
        for lane in [1, 2]:
            lxp = lx - lane_scroll
            pygame.draw.rect(surf, (160,160,160), (lxp, HEIGHT-200+50+lane*30, 48, 5))


# ═══════════════════════════════════════════════════════════════════════════════
#  OBSTACLE CLASS
# ═══════════════════════════════════════════════════════════════════════════════
CAR_COLOURS = [(200,20,20),(20,80,200),(200,140,0),(20,140,20),(160,0,160)]

class Obstacle:
    TYPES = [
        {"w":44,"h":92,"label":"Vilgax",   "draw":"vilgax"},
        {"w":64,"h":38,"label":"Car",      "draw":"car"},
        {"w":36,"h":78,"label":"Cultist",  "draw":"cultist"},
        {"w":36,"h":36,"label":"Fire",     "draw":"fire"},
        {"w":36,"h":30,"label":"Drone",    "draw":"drone"},
    ]

    def __init__(self, lane, speed):
        self.lane  = lane
        self.x     = float(WIDTH + 60)
        self.speed = speed
        self.frame = 0
        t          = random.choice(self.TYPES)
        self.w     = t["w"]
        self.h     = t["h"]
        self.label = t["label"]
        self.kind  = t["draw"]
        self.car_col = random.choice(CAR_COLOURS)
        self.y     = HEIGHT - 200 - self.h

    def update(self):
        self.x    -= self.speed
        self.frame += 1

    def draw(self, surf):
        ox, oy = int(self.x), int(self.y)
        if self.kind == "vilgax":
            draw_vilgax(surf, ox, oy, self.frame)
        elif self.kind == "car":
            draw_car(surf, ox, oy, self.car_col)
        elif self.kind == "cultist":
            draw_cultist(surf, ox, oy, self.frame)
        elif self.kind == "fire":
            draw_fire_orb(surf, ox, oy, self.frame)
        elif self.kind == "drone":
            draw_drone(surf, ox, oy, self.frame)
        # label
        lbl = font_xs.render(self.label, True, WHITE)
        surf.blit(lbl, (ox + self.w//2 - lbl.get_width()//2, oy - 19))

    def rect(self):
        return pygame.Rect(int(self.x)+5, int(self.y)+5, self.w-10, self.h-10)


# ═══════════════════════════════════════════════════════════════════════════════
#  COIN
# ═══════════════════════════════════════════════════════════════════════════════
class Coin:
    def __init__(self, x, speed):
        self.x     = float(x)
        self.y     = HEIGHT - 200 - random.randint(40, 120)
        self.speed = speed
        self.r     = 10
        self.t     = 0

    def update(self):
        self.x -= self.speed
        self.t  += 1

    def draw(self, surf):
        bob = int(math.sin(self.t * 0.15) * 4)
        cx, cy = int(self.x), self.y + bob
        # outer glow
        glow_surf = pygame.Surface((32,32), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (255,200,0,60),(16,16),14)
        surf.blit(glow_surf, (cx-16, cy-16))
        pygame.draw.circle(surf, GOLD,   (cx, cy), self.r)
        pygame.draw.circle(surf, YELLOW, (cx, cy), self.r-3)
        draw_omnitrix(surf, cx, cy, 5, NEON_G)

    def rect(self):
        return pygame.Rect(int(self.x)-self.r, self.y-self.r, self.r*2, self.r*2)


# ═══════════════════════════════════════════════════════════════════════════════
#  PARTICLE
# ═══════════════════════════════════════════════════════════════════════════════
class Particle:
    def __init__(self, x, y, col, fast=False):
        speed = 2.5 if fast else 1.5
        self.x   = float(x);  self.y   = float(y)
        self.vx  = random.uniform(-4, 4) * speed
        self.vy  = random.uniform(-7, 0) * speed
        self.col = col
        self.life= random.randint(22, 45)
        self.max = self.life

    def update(self):
        self.x  += self.vx
        self.y  += self.vy
        self.vy += 0.32
        self.life -= 1

    def draw(self, surf):
        if self.life > 0:
            alpha = int(255 * self.life / self.max)
            r = max(1, self.life // 7)
            p_surf = pygame.Surface((r*2+2, r*2+2), pygame.SRCALPHA)
            pygame.draw.circle(p_surf, (*self.col, alpha), (r+1,r+1), r)
            surf.blit(p_surf, (int(self.x)-r, int(self.y)-r))


# ═══════════════════════════════════════════════════════════════════════════════
#  HUD
# ═══════════════════════════════════════════════════════════════════════════════
def draw_hud(surf, score, coins, lives, alien_idx, scene_name, transform_cd, shield_time):
    # top bar
    bar = pygame.Surface((WIDTH, 62), pygame.SRCALPHA)
    pygame.draw.rect(bar, (0,0,0,190), (0,0,WIDTH,62))
    surf.blit(bar, (0,0))
    pygame.draw.line(surf, NEON_G, (0,62),(WIDTH,62),2)

    sc_txt = font_med.render(f"SCORE: {score:07d}", True, YELLOW)
    surf.blit(sc_txt, (10, 10))

    pygame.draw.circle(surf, GOLD,  (310, 31), 12)
    pygame.draw.circle(surf, YELLOW,(310, 31), 9)
    coin_txt = font_med.render(f"x{coins}", True, GOLD)
    surf.blit(coin_txt, (328, 15))

    for i in range(lives):
        draw_omnitrix(surf, WIDTH-30-i*38, 31, 13, NEON_G)

    a  = ALIENS[alien_idx % len(ALIENS)]
    at = font_small.render(a["name"], True, a["color"])
    surf.blit(at, (WIDTH//2 - at.get_width()//2, 7))
    pt = font_xs.render(a["power"], True, WHITE)
    surf.blit(pt, (WIDTH//2 - pt.get_width()//2, 36))

    # transform bar
    bar_w = 170
    bx = WIDTH//2 - bar_w//2
    pygame.draw.rect(surf, DGREY, (bx, HEIGHT-30, bar_w, 18), border_radius=9)
    fill = int(bar_w * (1 - transform_cd/180)) if transform_cd > 0 else bar_w
    fill_col = NEON_G if transform_cd == 0 else lerp_color(RED, ORANGE, transform_cd/180)
    pygame.draw.rect(surf, fill_col, (bx, HEIGHT-30, fill, 18), border_radius=9)
    pygame.draw.rect(surf, WHITE,    (bx, HEIGHT-30, bar_w, 18), 2, border_radius=9)
    label = "OMNITRIX READY!" if transform_cd == 0 else "RECHARGING..."
    cd_lbl = font_xs.render(label, True, WHITE)
    surf.blit(cd_lbl, (bx + bar_w//2 - cd_lbl.get_width()//2, HEIGHT-28))

    sl = font_xs.render(f"📍 {scene_name}", True, WHITE)
    surf.blit(sl, (10, HEIGHT-26))

    if shield_time > 0:
        sh_txt = font_xs.render(f"⚡ SHIELD {shield_time//FPS+1}s", True, CYAN)
        surf.blit(sh_txt, (WIDTH-160, 66))


# ═══════════════════════════════════════════════════════════════════════════════
#  SCREENS
# ═══════════════════════════════════════════════════════════════════════════════
STARS = [(random.randint(0,WIDTH), random.randint(0,HEIGHT//2), random.randint(1,2))
         for _ in range(140)]


def screen_menu(surf, frame):
    surf.fill((4, 4, 18))
    for sx, sy, ss in STARS:
        blink = int(math.sin(frame*0.04 + sx*0.05)*127+128)
        pygame.draw.circle(surf, (blink,blink,blink),(sx,sy),ss)

    draw_omnitrix(surf, WIDTH//2, 75, 38, NEON_G)

    glow = abs(math.sin(frame * 0.04))
    t_col = (int(57+198*glow), int(255*glow), int(20*glow))
    t1 = font_big.render("BEN 10  RUN", True, t_col)
    surf.blit(t1, (WIDTH//2 - t1.get_width()//2, 125))

    t2 = font_small.render("Classic Universe", True, (140,195,140))
    surf.blit(t2, (WIDTH//2 - t2.get_width()//2, 185))

    t_credit = font_xs.render("Made by Nishchal Soni", True, (100, 200, 100))
    surf.blit(t_credit, (WIDTH//2 - t_credit.get_width()//2, 215))

    lines = [
        ("SPACE / ↑",  "Jump"),
        ("S / ↓",      "Slide"),
        ("A / ←",      "Lane Left"),
        ("D / →",      "Lane Right"),
        ("T",          "Transform Alien"),
    ]
    for i, (key, desc) in enumerate(lines):
        k = font_xs.render(key,  True, NEON_G)
        d = font_xs.render(desc, True, WHITE)
        surf.blit(k, (WIDTH//2 - 140, 245 + i*26))
        surf.blit(d, (WIDTH//2 - 10,  245 + i*26))

    pulse = abs(math.sin(frame*0.07))
    flash_col = lerp_color(YELLOW, WHITE, pulse)
    t3 = font_med.render("[ SPACE ]  START", True, flash_col)
    surf.blit(t3, (WIDTH//2 - t3.get_width()//2, HEIGHT - 78))
    pygame.display.flip()


def screen_game_over(surf, score, coins, best):
    surf.fill((4, 4, 18))
    for _ in range(70):
        pygame.draw.circle(surf, WHITE,
            (random.randint(0,WIDTH), random.randint(0,HEIGHT//2)),
            random.randint(1,2))

    draw_omnitrix(surf, WIDTH//2, HEIGHT//2-130, 65, RED)

    t1 = font_big.render("GAME OVER", True, RED)
    t2 = font_med.render(f"Score:  {score:07d}", True, YELLOW)
    t3 = font_med.render(f"Coins:  {coins}",    True, GOLD)
    t4 = font_med.render(f"Best:   {best:07d}", True, NEON_G)
    t5 = font_small.render("[ SPACE ] Play Again   [ ESC ] Quit", True, WHITE)

    surf.blit(t1, (WIDTH//2-t1.get_width()//2, HEIGHT//2-62))
    surf.blit(t2, (WIDTH//2-t2.get_width()//2, HEIGHT//2+10))
    surf.blit(t3, (WIDTH//2-t3.get_width()//2, HEIGHT//2+48))
    surf.blit(t4, (WIDTH//2-t4.get_width()//2, HEIGHT//2+88))
    surf.blit(t5, (WIDTH//2-t5.get_width()//2, HEIGHT//2+148))
    pygame.display.flip()


# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN GAME LOOP
# ═══════════════════════════════════════════════════════════════════════════════
def game():
    LANE_X = [160, 480, 800]
    LANE_Y  = HEIGHT - 200

    lane       = 1
    player_x   = float(LANE_X[lane])
    player_y   = float(LANE_Y - 105)
    vy         = 0.0
    on_ground  = True
    sliding    = False
    slide_timer= 0

    alien_idx      = 0
    transform_cd   = 0
    transform_flash= 0
    shield_time    = 0

    lives      = 3
    score      = 0
    coins      = 0
    frame      = 0
    scroll     = 0.0
    speed      = 6.0

    scene_idx  = 0
    scene_dist = 0

    obstacles  = []
    coin_list  = []
    particles  = []

    obs_timer  = 0
    coin_timer = 0
    invincible = 0

    running = True
    while running:
        clock.tick(FPS)
        frame += 1

        # ── input ──────────────────────────────────────────────────────────
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return "quit", 0, 0

            if ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_a, pygame.K_LEFT):
                    lane = max(0, lane-1)
                if ev.key in (pygame.K_d, pygame.K_RIGHT):
                    lane = min(2, lane+1)
                if ev.key in (pygame.K_SPACE, pygame.K_UP) and on_ground:
                    bonus = ALIENS[alien_idx % len(ALIENS)]["jump_bonus"]
                    vy    = -(17 + bonus * 1.6)
                    on_ground = False
                    play("jump")
                if ev.key in (pygame.K_s, pygame.K_DOWN):
                    sliding     = True
                    slide_timer = 36
                    play("slide")
                if ev.key == pygame.K_t and transform_cd == 0:
                    alien_idx     = (alien_idx + 1) % len(ALIENS)
                    transform_cd  = 180
                    transform_flash=22
                    if ALIENS[alien_idx]["name"] == "GHOSTFREAK":
                        shield_time = 5 * FPS
                    particles += [Particle(player_x+25, player_y+20,
                                           ALIENS[alien_idx]["color"], fast=True) for _ in range(35)]
                    play("transform")

        # ── physics ────────────────────────────────────────────────────────
        target_x  = float(LANE_X[lane])
        player_x += (target_x - player_x) * 0.22

        if not on_ground:
            vy      += 0.72
            player_y += vy
            if player_y >= LANE_Y - 105:
                player_y  = LANE_Y - 105
                on_ground = True
                vy        = 0
                play("land")

        if sliding:
            slide_timer -= 1
            if slide_timer <= 0:
                sliding = False

        # ── speed & scene ──────────────────────────────────────────────────
        base_speed  = 6 + score // 900
        alien_bonus = ALIENS[alien_idx % len(ALIENS)]["speed_bonus"]
        speed       = min(base_speed + alien_bonus, 22)

        scroll     += speed
        scene_dist += speed
        if scene_dist > 12500:
            scene_dist = 0
            scene_idx  = (scene_idx + 1) % len(SCENES)

        score += int(speed * 0.15)

        # ── cooldowns ──────────────────────────────────────────────────────
        if transform_cd    > 0: transform_cd    -= 1
        if transform_flash > 0: transform_flash -= 1
        if shield_time     > 0: shield_time     -= 1
        if invincible      > 0: invincible      -= 1

        # ── spawn obstacles ────────────────────────────────────────────────
        obs_timer -= 1
        if obs_timer <= 0:
            obs_timer = random.randint(52, 115)
            for _ in range(random.randint(1, 2)):
                ol = random.randint(0, 2)
                obstacles.append(Obstacle(ol, speed))

        # ── spawn coins ────────────────────────────────────────────────────
        coin_timer -= 1
        if coin_timer <= 0:
            coin_timer = random.randint(28, 58)
            cx2 = WIDTH + 30
            for _ in range(random.randint(3, 6)):
                coin_list.append(Coin(cx2, speed))
                cx2 += 46

        # ── update ─────────────────────────────────────────────────────────
        for ob in obstacles: ob.update()
        for co in coin_list: co.update()
        for p  in particles: p.update()

        obstacles = [o for o in obstacles if o.x > -120]
        coin_list = [c for c in coin_list if c.x > -30]
        particles = [p for p in particles if p.life > 0]

        # ── collision ──────────────────────────────────────────────────────
        ph    = 58 if not sliding else 28
        py_off= 32 if sliding else 0
        prect = pygame.Rect(int(player_x)+6, int(player_y)+py_off, 38, ph)

        for ob in obstacles[:]:
            if prect.colliderect(ob.rect()) and invincible == 0:
                if shield_time > 0:
                    shield_time = 0
                    particles += [Particle(ob.x+ob.w//2, ob.y+ob.h//2, CYAN, fast=True) for _ in range(28)]
                    obstacles.remove(ob)
                    play("shield")
                else:
                    lives     -= 1
                    invincible = 95
                    particles += [Particle(player_x+25, player_y+20, RED, fast=True) for _ in range(22)]
                    play("hit")
                    if lives <= 0:
                        play("die")
                        return "dead", score, coins
                break

        for co in coin_list[:]:
            if prect.colliderect(co.rect()):
                coins += 1
                score += 50
                particles += [Particle(co.x, co.y, GOLD) for _ in range(9)]
                coin_list.remove(co)
                play("coin")

        # ── draw ───────────────────────────────────────────────────────────
        draw_background(screen, scene_idx, scroll, STARS)

        for p  in particles:  p.draw(screen)
        for ob in obstacles:  ob.draw(screen)
        for co in coin_list:  co.draw(screen)

        # transform flash ring
        if transform_flash > 0 and transform_flash % 4 < 2:
            r = 55 - transform_flash
            t_surf = pygame.Surface((r*2+4, r*2+4), pygame.SRCALPHA)
            pygame.draw.circle(t_surf, (*NEON_G, 180), (r+2,r+2), r, 4)
            screen.blit(t_surf, (int(player_x+25)-r-2, int(player_y+20)-r-2))

        # character (blink when invincible)
        if invincible == 0 or invincible % 6 < 3:
            draw_character(screen, alien_idx, player_x, player_y, frame,
                           shield=(shield_time>0), sliding=sliding)

        draw_hud(screen, score, coins, lives, alien_idx,
                 SCENES[scene_idx]["name"], transform_cd, shield_time)

        pygame.display.flip()

    return "quit", score, coins


# ═══════════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════
def main():
    best = load_high_score()
    state = "menu"
    frame = 0

    while True:
        frame += 1
        if state == "menu":
            screen_menu(screen, frame)
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_ESCAPE:
                        pygame.quit(); sys.exit()
                    if ev.key == pygame.K_SPACE:
                        play("menu_blip")
                        state = "play"
            clock.tick(FPS)

        

        elif state == "play":
            result, score, coins = game()
            best  = max(best, score)
            save_high_score(best)
            if result == "quit":
                pygame.quit(); sys.exit()
            state      = "over"
            last_score = score
            last_coins = coins

        elif state == "over":
            screen_game_over(screen, last_score, last_coins, best)
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_ESCAPE:
                        pygame.quit(); sys.exit()
                    if ev.key == pygame.K_SPACE:
                        play("menu_blip")
                        state = "play"
            clock.tick(FPS)


if __name__ == "__main__":
    main()
