import pygame
import math
import random
import subprocess
import sys
import os
import numpy as np

pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

W, H = 900, 600
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Sasa's Arcade")

clock = pygame.time.Clock()
FPS = 60

# ═══════════════════════════════════════════════════════════════════
# COLOR PALETTE
# ═══════════════════════════════════════════════════════════════════
C_BG      = (8,   8,  18)
C_PANEL   = (16, 16,  32)
C_BORDER  = (50, 50,  90)
C_WHITE   = (240, 240, 255)
C_DIM     = (130, 130, 160)
C_GOLD    = (255, 215,  80)
C_SHADOW  = (0, 0, 0, 120)

# ═══════════════════════════════════════════════════════════════════
# AUDIO ENGINE
# ═══════════════════════════════════════════════════════════════════

def generate_tone(freq, duration, volume=0.25, fade=True, wave_type='square'):
    sample_rate = 44100
    samples = int(sample_rate * duration)
    t = np.linspace(0, duration, samples, False)

    if wave_type == 'square':
        wave = np.sign(np.sin(2 * np.pi * freq * t))
    elif wave_type == 'sawtooth':
        wave = 2 * (t * freq - np.floor(t * freq + 0.5))
    elif wave_type == 'sine':
        wave = np.sin(2 * np.pi * freq * t)
    elif wave_type == 'triangle':
        wave = 2 * np.abs(2 * (t * freq - np.floor(t * freq + 0.5))) - 1
    elif wave_type == 'noise':
        wave = np.random.uniform(-1, 1, samples)
    else:
        wave = np.sign(np.sin(2 * np.pi * freq * t))

    if fade:
        fade_samples = min(int(sample_rate * 0.05), samples // 4)
        fade_in = np.linspace(0, 1, fade_samples)
        fade_out = np.linspace(1, 0, fade_samples)
        envelope = np.ones(samples)
        envelope[:fade_samples] = fade_in
        envelope[-fade_samples:] = fade_out
        wave = wave * envelope

    audio = (wave * volume * 32767).astype(np.int16)
    stereo = np.column_stack((audio, audio))
    return pygame.sndarray.make_sound(stereo)

def generate_hover_sound():
    return generate_tone(1200, 0.06, volume=0.12, wave_type='sine')

def generate_select_sound():
    sample_rate = 44100
    duration = 0.25
    samples = int(sample_rate * duration)
    t = np.linspace(0, duration, samples, False)
    freqs = [880, 1100, 1320]
    wave = np.zeros(samples)
    for i, freq in enumerate(freqs):
        start = int(samples * i / 3)
        end = int(samples * (i + 1) / 3)
        seg_t = t[start:end] - t[start]
        seg_wave = np.sin(2 * np.pi * freq * seg_t)
        fade = int(len(seg_wave) * 0.2)
        envelope = np.ones(len(seg_wave))
        envelope[:fade] = np.linspace(0, 1, fade)
        envelope[-fade:] = np.linspace(1, 0, fade)
        wave[start:end] = seg_wave * envelope
    audio = (wave * 0.2 * 32767).astype(np.int16)
    stereo = np.column_stack((audio, audio))
    return pygame.sndarray.make_sound(stereo)

def generate_launch_sound():
    sample_rate = 44100
    duration = 1.0
    samples = int(sample_rate * duration)
    t = np.linspace(0, duration, samples, False)
    sweep_freq = np.linspace(300, 1000, samples)
    sweep = np.sin(2 * np.pi * sweep_freq * t)
    harmonic = 0.25 * np.sin(2 * np.pi * sweep_freq * 2 * t)
    env = np.ones(samples)
    env[:int(samples*0.08)] = np.linspace(0, 1, int(samples*0.08))
    env[int(samples*0.85):] = np.linspace(1, 0, samples - int(samples*0.85))
    wave = (sweep + harmonic) * env
    audio = (wave * 0.25 * 32767).astype(np.int16)
    stereo = np.column_stack((audio, audio))
    return pygame.sndarray.make_sound(stereo)

def generate_menu_music():
    sample_rate = 44100
    bpm = 110
    beat_duration = 60 / bpm
    total_beats = 16
    duration = beat_duration * total_beats
    samples = int(sample_rate * duration)
    t = np.linspace(0, duration, samples, False)

    bass_notes = [110, 110, 130.81, 110, 164.81, 110, 130.81, 110,
                  110, 110, 130.81, 110, 164.81, 196.00, 164.81, 130.81]

    bass = np.zeros(samples)
    samples_per_beat = int(sample_rate * beat_duration)

    for beat, freq in enumerate(bass_notes):
        start = beat * samples_per_beat
        end = min((beat + 1) * samples_per_beat, samples)
        beat_t = t[start:end] - t[start]
        beat_wave = np.sign(np.sin(2 * np.pi * freq * beat_t))
        env = np.exp(-beat_t * 10)
        bass[start:end] = beat_wave * env * 0.35

    melody_notes = [0, 0, 440, 0, 493.88, 0, 523.25, 0,
                    0, 440, 0, 493.88, 523.25, 659.25, 523.25, 493.88]
    melody = np.zeros(samples)

    for beat, freq in enumerate(melody_notes):
        if freq == 0:
            continue
        start = beat * samples_per_beat
        end = min((beat + 1) * samples_per_beat, samples)
        beat_t = t[start:end] - t[start]
        wave = np.sign(np.sin(2 * np.pi * freq * beat_t))
        wave += 0.3 * np.sign(np.sin(2 * np.pi * freq * 1.005 * beat_t))
        env = np.exp(-beat_t * 8)
        melody[start:end] = wave * env * 0.15

    hihat = np.zeros(samples)
    for beat in range(total_beats):
        start = beat * samples_per_beat
        end = min(start + int(sample_rate * 0.04), samples)
        noise = np.random.uniform(-1, 1, end - start)
        env = np.exp(-np.linspace(0, 1, end - start) * 18)
        hihat[start:end] = noise * env * 0.06

    combined = bass + melody + hihat
    combined = np.tanh(combined * 1.2) / 1.2

    audio = (combined * 0.2 * 32767).astype(np.int16)
    stereo = np.column_stack((audio, audio))
    return pygame.sndarray.make_sound(stereo)

hover_sound = generate_hover_sound()
select_sound = generate_select_sound()
launch_sound = generate_launch_sound()
menu_music = generate_menu_music()

music_playing = False

def play_menu_music():
    global music_playing
    if not music_playing:
        menu_music.play(-1)
        music_playing = True

def stop_menu_music():
    global music_playing
    menu_music.stop()
    music_playing = False

# ═══════════════════════════════════════════════════════════════════
# GAME THEMES
# ═══════════════════════════════════════════════════════════════════

GAME_THEMES = [
    {
        "title":   "Space Invaders",
        "tag":     "SHOOTER",
        "desc":    ["Defend Earth from", "waves of alien ships"],
        "file":    "space_invaders.py",
        "accent":  (80, 200, 255),
        "dim":     (20,  55,  80),
        "icon_fn": "_draw_icon_space",
    },
    {
        "title":   "Ping Pong",
        "tag":     "SPORTS",
        "desc":    ["Two players, one", "ball – first to 7 wins"],
        "file":    "ping_pong.py",
        "accent":  (255, 100, 180),
        "dim":     (70,  20,  55),
        "icon_fn": "_draw_icon_pong",
    },
    {
        "title":   "Tetris",
        "tag":     "PUZZLE",
        "desc":    ["Stack falling blocks", "and clear the board"],
        "file":    "tetris.py",
        "accent":  (120, 255, 140),
        "dim":     (20,  65,  25),
        "icon_fn": "_draw_icon_tetris",
    },
]

# ═══════════════════════════════════════════════════════════════════
# FONTS
# ═══════════════════════════════════════════════════════════════════

def _font(size, bold=False):
    return pygame.font.SysFont(
        "Segoe UI" if sys.platform == "win32" else "DejaVuSans",
        size,
        bold=bold
    )

F_HUGE    = _font(64, bold=True)
F_TITLE   = _font(22, bold=True)
F_TAG     = _font(11, bold=True)
F_DESC    = _font(14)
F_SUB     = _font(13)
F_CREDIT  = _font(13)
F_HINT    = _font(12)
F_MASSIVE = _font(80, bold=True)

# ═══════════════════════════════════════════════════════════════════
# ENHANCED STARS — with parallax depth
# ═══════════════════════════════════════════════════════════════════

class Star:
    def __init__(self):
        self.reset(birth=True)

    def reset(self, birth=False):
        self.x   = random.uniform(0, W)
        self.y   = random.uniform(0, H) if birth else -2.0
        self.spd = random.uniform(0.15, 0.7)
        self.r   = random.uniform(0.5, 1.8)
        self.a   = random.randint(80, 200)
        self.twinkle_phase = random.uniform(0, math.tau)
        self.twinkle_speed = random.uniform(0.02, 0.08)

    def update(self, t):
        self.y += self.spd
        self.twinkle_phase += self.twinkle_speed
        if self.y > H + 4:
            self.reset()

    def draw(self, surf, t):
        twinkle = abs(math.sin(self.twinkle_phase + t * 0.02))
        alpha = int(self.a * (0.6 + 0.4 * twinkle))
        s = pygame.Surface((4, 4), pygame.SRCALPHA)
        pygame.draw.circle(s, (255, 255, 255, alpha), (2, 2), int(self.r))
        surf.blit(s, (int(self.x) - 2, int(self.y) - 2))

stars = [Star() for _ in range(200)]

# ═══════════════════════════════════════════════════════════════════
# ENHANCED BURSTS — with glow and trails
# ═══════════════════════════════════════════════════════════════════

class Burst:
    def __init__(self, x, y, colour, size_mult=1.0):
        self.x, self.y   = x, y
        angle            = random.uniform(0, math.tau)
        spd              = random.uniform(1.5, 6.0) * size_mult
        self.vx          = math.cos(angle) * spd
        self.vy          = math.sin(angle) * spd
        self.life        = random.randint(30, 60)
        self.max_life    = self.life
        self.r           = random.uniform(2, 5) * size_mult
        self.col         = colour
        self.trail       = []

    def update(self):
        self.trail.append((self.x, self.y))
        if len(self.trail) > 5:
            self.trail.pop(0)
        self.x  += self.vx
        self.y  += self.vy
        self.vy += 0.12
        self.life -= 1

    def draw(self, surf):
        if self.life <= 0:
            return
        ratio = self.life / self.max_life
        alpha = int(255 * ratio)

        # Trail
        for i, (tx, ty) in enumerate(self.trail):
            t_ratio = i / len(self.trail)
            t_alpha = int(alpha * t_ratio * 0.5)
            t_r = max(1, int(self.r * t_ratio * 0.5))
            if t_alpha > 0:
                s = pygame.Surface((t_r * 2 + 2, t_r * 2 + 2), pygame.SRCALPHA)
                pygame.draw.circle(s, (*self.col, t_alpha), (t_r + 1, t_r + 1), t_r)
                surf.blit(s, (int(tx) - t_r, int(ty) - t_r))

        # Glow
        glow_r = max(1, int(self.r * 2 * ratio))
        glow = pygame.Surface((glow_r * 2 + 2, glow_r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*self.col, alpha // 3), (glow_r + 1, glow_r + 1), glow_r)
        surf.blit(glow, (int(self.x) - glow_r, int(self.y) - glow_r))

        # Core
        rad = max(1, int(self.r * ratio))
        s = pygame.Surface((rad * 2 + 2, rad * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.col, alpha), (rad + 1, rad + 1), rad)
        surf.blit(s, (int(self.x) - rad, int(self.y) - rad))

bursts = []

# ═══════════════════════════════════════════════════════════════════
# FLOATING PARTICLES — ambient background effect
# ═══════════════════════════════════════════════════════════════════

class FloatingParticle:
    def __init__(self):
        self.x = random.uniform(0, W)
        self.y = random.uniform(0, H)
        self.vx = random.uniform(-0.3, 0.3)
        self.vy = random.uniform(-0.3, 0.3)
        self.r = random.uniform(1, 3)
        self.alpha = random.randint(20, 60)
        self.phase = random.uniform(0, math.tau)
        self.speed = random.uniform(0.01, 0.03)

    def update(self, t):
        self.x += self.vx
        self.y += self.vy
        self.phase += self.speed
        self.alpha = int(40 + 20 * math.sin(self.phase + t * 0.01))
        if self.x < -10: self.x = W + 10
        if self.x > W + 10: self.x = -10
        if self.y < -10: self.y = H + 10
        if self.y > H + 10: self.y = -10

    def draw(self, surf):
        s = pygame.Surface((6, 6), pygame.SRCALPHA)
        pygame.draw.circle(s, (200, 200, 255, self.alpha), (3, 3), int(self.r))
        surf.blit(s, (int(self.x) - 3, int(self.y) - 3))

float_particles = [FloatingParticle() for _ in range(50)]

# ═══════════════════════════════════════════════════════════════════
# ICONS
# ═══════════════════════════════════════════════════════════════════

def _draw_icon_space(surf, cx, cy, accent, t):
    pts = [(cx, cy - 22), (cx - 14, cy + 12), (cx, cy + 6), (cx + 14, cy + 12)]
    pygame.draw.polygon(surf, accent, pts)
    pygame.draw.polygon(surf, C_WHITE, pts, 1)
    flicker = int(abs(math.sin(t * 0.1)) * 6)
    eg = pygame.Surface((8, 10 + flicker), pygame.SRCALPHA)
    eg.fill((255, 160, 40, 120))
    surf.blit(eg, (cx - 4, cy + 10))
    pygame.draw.rect(surf, (255, 255, 100), (cx - 1, cy - 38, 3, 12))
    for ax, ay in [(-28, -18), (0, -18), (28, -18), (-18, -4), (18, -4)]:
        pygame.draw.ellipse(surf, accent, (cx + ax - 6, cy + ay - 4, 12, 8))
        pygame.draw.circle(surf, C_BG, (cx + ax - 3, cy + ay - 1), 2)
        pygame.draw.circle(surf, C_BG, (cx + ax + 3, cy + ay - 1), 2)

def _draw_icon_pong(surf, cx, cy, accent, t):
    left, right, top, bot = cx - 50, cx + 50, cy - 32, cy + 32
    pygame.draw.line(surf, C_BORDER, (left, top),  (right, top),  1)
    pygame.draw.line(surf, C_BORDER, (left, bot),  (right, bot),  1)
    for dy in range(0, 64, 10):
        pygame.draw.line(surf, (*C_BORDER, 100), (cx, top + dy), (cx, min(top + dy + 5, bot)), 1)
    period, phase = 120, t % 120
    x_range = (right - 8) - (left + 8)
    norm_x  = abs((phase / (period / 2)) - 1.0)
    bx      = left + 8 + norm_x * x_range
    by = max(top + 6, min(bot - 6, cy + math.sin(t * 0.11) * 22))
    lpad_y = max(top + 14, min(bot - 14, cy + math.sin(t * 0.11 - 0.4) * 18))
    rpad_y = max(top + 14, min(bot - 14, cy + math.sin(t * 0.11) * 18))
    PADDLE_H, PADDLE_W = 28, 5
    near_left, near_right = bx < left + 22, bx > right - 22
    lp_col = (140, 180, 255) if near_left else (80, 110, 200)
    pygame.draw.rect(surf, lp_col, (left + 2, int(lpad_y) - PADDLE_H // 2, PADDLE_W, PADDLE_H), border_radius=3)
    rp_col = accent if near_right else tuple(max(0, c - 60) for c in accent)
    pygame.draw.rect(surf, rp_col, (right - 7, int(rpad_y) - PADDLE_H // 2, PADDLE_W, PADDLE_H), border_radius=3)
    pygame.draw.circle(surf, C_WHITE, (int(bx), int(by)), 5)
    trail_x = int(bx - math.copysign(8, math.cos(t * math.pi / (period / 2))))
    ts = pygame.Surface((6, 6), pygame.SRCALPHA)
    pygame.draw.circle(ts, (*C_WHITE, 60), (3, 3), 3)
    surf.blit(ts, (trail_x - 3, int(by) - 3))

def _draw_icon_tetris(surf, cx, cy, accent, t):
    S, COLS, ROWS = 10, 5, 6
    wx, wy = cx - (COLS * S) // 2, cy - (ROWS * S) // 2
    pygame.draw.line(surf, C_BORDER, (wx - 2, wy),           (wx - 2, wy + ROWS * S), 1)
    pygame.draw.line(surf, C_BORDER, (wx + COLS * S + 1, wy),(wx + COLS * S + 1, wy + ROWS * S), 1)
    pygame.draw.line(surf, C_BORDER, (wx - 2, wy + ROWS * S),(wx + COLS * S + 1, wy + ROWS * S), 1)
    stack = [
        [(255, 80, 80), (255, 80, 80), (255, 200, 40), (255, 200, 40), (100, 180, 255)],
        [(100, 180, 255), None, (120, 255, 140), (255, 80, 80), (255, 80, 80)],
        [None, (255, 200, 40), (255, 200, 40), (120, 255, 140), None],
    ]
    for row_i, row in enumerate(stack):
        y_pos = wy + (ROWS - len(stack) + row_i) * S
        for col_i, col in enumerate(row):
            if col:
                pygame.draw.rect(surf, col, (wx + col_i * S + 1, y_pos + 1, S - 2, S - 2), border_radius=2)
    fall_period = 90
    fall_phase  = t % fall_period
    fall_row    = int(fall_phase / fall_period * (ROWS - 3))
    l_piece  = [(0, 0), (0, 1), (0, 2), (1, 2)]
    fall_col = accent
    flashing    = fall_phase > fall_period - 8
    flash_alpha = int(255 * (fall_phase - (fall_period - 8)) / 8) if flashing else 0
    for dc, dr in l_piece:
        bx = wx + 1 * S + dc * S + 1
        by = wy + fall_row * S + dr * S + 1
        if by < wy + ROWS * S - S * 3:
            col_draw = (
                min(255, fall_col[0] + flash_alpha),
                min(255, fall_col[1] + flash_alpha),
                min(255, fall_col[2] + flash_alpha),
            )
            pygame.draw.rect(surf, col_draw, (bx, by, S - 2, S - 2), border_radius=2)
            ghost_by = wy + (ROWS - 3) * S + dr * S + 1
            gs = pygame.Surface((S - 2, S - 2), pygame.SRCALPHA)
            gs.fill((*fall_col, 40))
            surf.blit(gs, (bx, ghost_by))

ICON_FNS = {
    "_draw_icon_space":  _draw_icon_space,
    "_draw_icon_pong":   _draw_icon_pong,
    "_draw_icon_tetris": _draw_icon_tetris,
}

CARD_W, CARD_H = 220, 300
CARD_GAP       = 24
TOTAL_W        = CARD_W * 3 + CARD_GAP * 2
CARDS_X        = (W - TOTAL_W) // 2
CARDS_Y        = 170

def card_rect(i):
    return pygame.Rect(CARDS_X + i * (CARD_W + CARD_GAP), CARDS_Y, CARD_W, CARD_H)

def draw_card(surf, rect, accent, dim, hover, selected, t):
    r = rect

    # Soft shadow
    for shadow_offset in range(8, 0, -2):
        sh = pygame.Surface((r.w + shadow_offset * 2, r.h + shadow_offset * 2), pygame.SRCALPHA)
        alpha = max(0, min(255, 15 - shadow_offset * 2))
        pygame.draw.rect(sh, (0, 0, 0, alpha), sh.get_rect(), border_radius=18)
        surf.blit(sh, (r.x - shadow_offset, r.y + shadow_offset))

    bg_col = (22 + hover * 8, 22 + hover * 8, 40 + hover * 10)
    pygame.draw.rect(surf, bg_col, r, border_radius=14)

    # Top accent strip
    strip = pygame.Surface((r.w, 4), pygame.SRCALPHA)
    strip.fill((*accent, 220 if selected else 140))
    surf.blit(strip, (r.x, r.y))

    # Animated glow border
    glow_a = 180 + int(math.sin(t * 0.06) * 40) if selected else (120 if hover else 60)
    border_col = (*accent, glow_a) if (selected or hover) else (*C_BORDER, 120)
    bs = pygame.Surface((r.w + 4, r.h + 4), pygame.SRCALPHA)
    pygame.draw.rect(bs, border_col, bs.get_rect(), width=2, border_radius=15)
    surf.blit(bs, (r.x - 2, r.y - 2))

    # Icon zone with subtle gradient
    icon_zone = pygame.Surface((r.w - 16, 130), pygame.SRCALPHA)
    icon_zone.fill((*dim, 100))
    surf.blit(icon_zone, (r.x + 8, r.y + 8))

def blit_text(surf, font, text, colour, cx, y, alpha=255):
    img = font.render(text, True, colour)
    if alpha < 255:
        img.set_alpha(alpha)
    surf.blit(img, (cx - img.get_width() // 2, y))

def launch_game(idx):
    game_file = GAME_THEMES[idx]["file"]
    if not os.path.exists(game_file):
        return
    global screen
    stop_menu_music()
    pygame.display.quit()
    subprocess.run([sys.executable, game_file])
    pygame.display.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Sasa's Arcade")
    pygame.event.clear()
    play_menu_music()

def fade_out(surface, colour=(0, 0, 0), steps=30):
    overlay = pygame.Surface((W, H))
    overlay.fill(colour)
    for i in range(steps):
        overlay.set_alpha(int(255 * i / steps))
        surface.blit(overlay, (0, 0))
        pygame.display.flip()
        clock.tick(FPS)

def fade_in(surface, colour=(0, 0, 0), steps=30):
    overlay = pygame.Surface((W, H))
    overlay.fill(colour)
    for i in range(steps, -1, -1):
        overlay.set_alpha(int(255 * i / steps))
        surface.blit(overlay, (0, 0))
        pygame.display.flip()
        clock.tick(FPS)

# ═══════════════════════════════════════════════════════════════════
# THEME-SPECIFIC CINEMATIC TRANSITIONS
# ═══════════════════════════════════════════════════════════════════

def _draw_space_theme(screen, frame, accent, cx, cy):
    if frame > 5 and frame < 80:
        num_streaks = min(30, frame)
        for i in range(num_streaks):
            angle = (i / num_streaks) * math.tau + frame * 0.02
            dist = (frame - 5) * 4 + i * 3
            sx = cx + math.cos(angle) * dist
            sy = cy + math.sin(angle) * dist
            if 0 < sx < W and 0 < sy < H:
                length = min(20, frame // 3)
                ex = sx + math.cos(angle) * length
                ey = sy + math.sin(angle) * length
                alpha = max(0, 200 - frame * 2)
                pygame.draw.line(screen, (*accent, alpha), (sx, sy), (ex, ey), 1)

        if frame > 30:
            for i in range(5):
                angle = (i / 5) * math.tau + frame * 0.03
                orbit_r = 100 + (frame - 30) * 3
                ax = cx + math.cos(angle) * orbit_r
                ay = cy + math.sin(angle) * orbit_r * 0.6
                if 0 < ax < W and 0 < ay < H:
                    alpha = min(200, (frame - 30) * 4)
                    s = pygame.Surface((14, 10), pygame.SRCALPHA)
                    pygame.draw.ellipse(s, (*accent, alpha), (0, 0, 14, 8))
                    pygame.draw.circle(s, (0, 0, 0, alpha), (4, 4), 2)
                    pygame.draw.circle(s, (0, 0, 0, alpha), (10, 4), 2)
                    screen.blit(s, (int(ax) - 7, int(ay) - 5))

def _draw_pong_theme(screen, frame, accent, cx, cy):
    if frame > 10 and frame < 90:
        ball_progress = (frame - 10) / 60
        bx = cx + math.sin(ball_progress * math.pi * 4) * (W // 2 - 50)
        by = cy + math.cos(ball_progress * math.pi * 3) * (H // 2 - 50)
        alpha = min(255, frame * 3)

        for trail_i in range(1, 6):
            t_progress = ball_progress - trail_i * 0.02
            if t_progress > 0:
                tx = cx + math.sin(t_progress * math.pi * 4) * (W // 2 - 50)
                ty = cy + math.cos(t_progress * math.pi * 3) * (H // 2 - 50)
                t_alpha = max(0, alpha - trail_i * 30)
                tr = max(1, 4 - trail_i)
                s = pygame.Surface((tr * 2 + 2, tr * 2 + 2), pygame.SRCALPHA)
                pygame.draw.circle(s, (*accent, t_alpha), (tr + 1, tr + 1), tr)
                screen.blit(s, (int(tx) - tr, int(ty) - tr))

        pygame.draw.circle(screen, C_WHITE, (int(bx), int(by)), 5)

        if frame > 25:
            paddle_alpha = min(200, (frame - 25) * 5)
            left_y = cy + math.sin(frame * 0.08) * 80
            right_y = cy + math.cos(frame * 0.08) * 80

            lp = pygame.Surface((8, 50), pygame.SRCALPHA)
            lp.fill((*accent, paddle_alpha))
            screen.blit(lp, (60, int(left_y) - 25))

            rp = pygame.Surface((8, 50), pygame.SRCALPHA)
            rp.fill((*accent, paddle_alpha))
            screen.blit(rp, (W - 68, int(right_y) - 25))

        if frame > 15:
            dash_alpha = min(100, (frame - 15) * 3)
            for dy in range(0, H, 20):
                pygame.draw.line(screen, (*C_WHITE, dash_alpha), (W // 2, dy), (W // 2, dy + 10), 1)

def _draw_tetris_theme(screen, frame, accent, cx, cy):
    if frame > 8 and frame < 85:
        grid_alpha = min(60, (frame - 8) * 2)
        for gx in range(0, W, 40):
            pygame.draw.line(screen, (*accent, grid_alpha), (gx, 0), (gx, H), 1)
        for gy in range(0, H, 40):
            pygame.draw.line(screen, (*accent, grid_alpha), (0, gy), (W, gy), 1)

        colors = [(80, 200, 255), (255, 200, 40), (120, 255, 140),
                  (255, 100, 100), (180, 100, 255), (255, 160, 40)]

        for i in range(min(8, frame // 5)):
            bx = (i * 97 + cx) % (W - 100) + 50
            fall_progress = ((frame - 8 - i * 5) % 50) / 50
            by = -20 + fall_progress * (H + 40)
            color = colors[i % len(colors)]
            size = 18
            alpha = min(200, 255 - abs(fall_progress - 0.5) * 300)

            if alpha > 0:
                s = pygame.Surface((size + 4, size + 4), pygame.SRCALPHA)
                pygame.draw.rect(s, (*color, alpha), (2, 2, size, size), border_radius=2)
                pygame.draw.rect(s, (min(255, color[0] + 50), min(255, color[1] + 50), 
                    min(255, color[2] + 50), alpha), (2, 2, size, 3), border_radius=2)
                screen.blit(s, (int(bx) - size // 2 - 2, int(by) - size // 2 - 2))

        if frame > 20:
            board_alpha = min(150, (frame - 20) * 4)
            board_rect = pygame.Rect(W // 2 - 160, 40, 320, H - 80)
            pygame.draw.rect(screen, (*accent, board_alpha // 3), board_rect, 2, border_radius=4)


def run_cinematic_transition(confirm_idx, t):
    game = GAME_THEMES[confirm_idx]
    accent = game["accent"]
    cx = card_rect(confirm_idx).centerx
    cy = card_rect(confirm_idx).centery

    stop_menu_music()
    launch_sound.play()

    anim_frames = 140

    for frame in range(anim_frames):
        clock.tick(FPS)

        screen.fill(C_BG)
        _draw_bg(t + frame)
        _draw_stars(t + frame)

        progress = frame / 60
        if progress > 1:
            progress = 1
        eased_progress = 1 - (1 - progress) ** 3

        max_radius = int(math.hypot(W, H))
        current_radius = int(max_radius * eased_progress)

        pygame.draw.circle(screen, accent, (cx, cy), current_radius)

        if confirm_idx == 0:
            _draw_space_theme(screen, frame, accent, cx, cy)
        elif confirm_idx == 1:
            _draw_pong_theme(screen, frame, accent, cx, cy)
        elif confirm_idx == 2:
            _draw_tetris_theme(screen, frame, accent, cx, cy)

        if frame > 20:
            text_progress = min(1.0, (frame - 20) / 40.0)
            text_alpha = int(255 * text_progress)
            y_offset = int((1.0 - text_progress) * 40)

            blit_text(screen, F_MASSIVE, game["title"].upper(), C_WHITE, 
                      W // 2, H // 2 - 60 + y_offset, text_alpha)
            blit_text(screen, F_TITLE, f"INITIALIZING {game['tag']}...", 
                      (255, 255, 255), W // 2, H // 2 + 30 + y_offset, text_alpha)

        pygame.display.flip()

    fade_out(screen, colour=accent, steps=20)
    fade_out(screen, colour=(0, 0, 0), steps=10)

# ═══════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════

def main():
    selected   = 0
    hover      = -1
    t          = 0
    intro_fade = 60
    confirm    = None
    confirm_t  = 0
    last_hover = -1

    play_menu_music()
    fade_in(screen, steps=40)

    running = True
    while running:
        clock.tick(FPS)
        t += 1

        prev_selected = selected
        prev_hover    = hover

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    selected = (selected - 1) % 3
                    select_sound.play()
                elif event.key == pygame.K_RIGHT:
                    selected = (selected + 1) % 3
                    select_sound.play()
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    confirm, confirm_t = selected, t

            elif event.type == pygame.MOUSEMOTION:
                mx, my = event.pos
                hover  = next((i for i in range(3) if card_rect(i).collidepoint(mx, my)), -1)

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                for i in range(3):
                    if card_rect(i).collidepoint(mx, my):
                        if selected == i:
                            confirm, confirm_t = i, t
                        else:
                            selected = i
                            select_sound.play()

        if (selected != prev_selected) or (hover != -1 and hover != prev_hover):
            hover_sound.play()

        if confirm is not None and t - confirm_t > 5:
            accent = GAME_THEMES[confirm]["accent"]
            cx = card_rect(confirm).centerx
            cy = card_rect(confirm).centery

            for _ in range(60):
                bursts.append(Burst(cx, cy, accent))

            for _ in range(10):
                screen.fill(C_BG)
                _draw_bg(t)
                flash = pygame.Surface((W, H), pygame.SRCALPHA)
                flash.fill((*accent, 20))
                screen.blit(flash, (0, 0))
                pygame.display.flip()
                clock.tick(FPS)

            run_cinematic_transition(confirm, t)
            launch_game(confirm)
            confirm = None
            play_menu_music()
            fade_in(screen, steps=30)

        if intro_fade > 0:
            intro_fade -= 1

        screen.fill(C_BG)
        _draw_bg(t)
        _draw_stars(t)
        _draw_float_particles(t)
        _draw_title(t, intro_fade)
        _draw_cards(selected, hover, t)
        _draw_bursts()
        _draw_hint(selected)
        _draw_footer()

        pygame.display.flip()

    stop_menu_music()
    pygame.quit()

def _draw_bg(t):
    for r_size in range(300, 50, -40):
        alpha = max(0, 12 - (300 - r_size) // 20)
        s = pygame.Surface((r_size * 2, r_size * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (30, 20, 70, alpha), (r_size, r_size), r_size)
        screen.blit(s, (W // 2 - r_size, H // 2 - r_size))

def _draw_stars(t):
    star_surf = pygame.Surface((W, H), pygame.SRCALPHA)
    for star in stars:
        star.update(t)
        star.draw(star_surf, t)
    screen.blit(star_surf, (0, 0))

def _draw_float_particles(t):
    for p in float_particles:
        p.update(t)
        p.draw(screen)

def _draw_title(t, intro_fade):
    alpha    = 255 if intro_fade == 0 else int(255 * (60 - intro_fade) / 60)
    lbl1     = F_HUGE.render("SASA'S", True, C_WHITE)
    shimmer  = int(abs(math.sin(t * 0.03)) * 30)
    col2     = (min(255, C_GOLD[0] + shimmer), min(255, C_GOLD[1] + shimmer // 2), C_GOLD[2])
    lbl2     = F_HUGE.render("ARCADE", True, col2)

    gap      = 14
    total_w  = lbl1.get_width() + gap + lbl2.get_width()
    start_x  = W // 2 - total_w // 2
    y        = 28

    lbl1.set_alpha(alpha)
    lbl2.set_alpha(alpha)
    screen.blit(lbl1, (start_x, y))
    screen.blit(lbl2, (start_x + lbl1.get_width() + gap, y))

    uw     = min(total_w + 40, W - 80)
    ux     = W // 2 - uw // 2
    line_y = y + lbl1.get_height() + 6
    pygame.draw.line(screen, (*C_GOLD, alpha), (ux, line_y), (ux + uw, line_y), 1)
    blit_text(screen, F_SUB, "Choose your game", C_DIM, W // 2, line_y + 8, alpha)

def _draw_cards(selected, hover, t):
    for i, game in enumerate(GAME_THEMES):
        r      = card_rect(i)
        is_sel = (i == selected)
        is_hov = (i == hover)
        accent = game["accent"]
        dim    = game["dim"]

        lift = (int(abs(math.sin(t * 0.05)) * 4) + 4) if is_sel else (3 if is_hov else 0)
        r    = r.move(0, -lift)

        draw_card(screen, r, accent, dim, is_hov, is_sel, t)
        ICON_FNS[game["icon_fn"]](screen, r.x + CARD_W // 2, r.y + 74, accent, t)

        pygame.draw.line(screen, (*accent, 60), (r.x + 12, r.y + 148), (r.x + CARD_W - 12, r.y + 148), 1)

        tag_surf = F_TAG.render(game["tag"], True, accent)
        tag_bg   = pygame.Surface((tag_surf.get_width() + 16, 18), pygame.SRCALPHA)
        tag_bg.fill((*accent, 30))
        screen.blit(tag_bg, (r.x + CARD_W // 2 - tag_bg.get_width() // 2, r.y + 155))
        blit_text(screen, F_TAG, game["tag"], accent, r.x + CARD_W // 2, r.y + 157)

        blit_text(screen, F_TITLE, game["title"], C_WHITE, r.x + CARD_W // 2, r.y + 180)
        for li, line in enumerate(game["desc"]):
            blit_text(screen, F_DESC, line, C_DIM, r.x + CARD_W // 2, r.y + 212 + li * 20)

        btn_y    = r.y + CARD_H - 46
        btn_rect = pygame.Rect(r.x + 20, btn_y, CARD_W - 40, 32)
        bs       = pygame.Surface((btn_rect.w, btn_rect.h), pygame.SRCALPHA)
        bs.fill((*accent, 50) if is_sel else (40, 40, 70, 200))
        screen.blit(bs, btn_rect.topleft)
        pygame.draw.rect(screen, accent if is_sel else C_BORDER, btn_rect, width=1, border_radius=6)
        blit_text(screen, F_TAG, "PLAY" if is_sel else "SELECT",
                  C_WHITE if is_sel else C_DIM, r.x + CARD_W // 2, btn_y + 9)

def _draw_bursts():
    burst_surf = pygame.Surface((W, H), pygame.SRCALPHA)
    for b in bursts[:]:
        b.update()
        b.draw(burst_surf)
        if b.life <= 0:
            bursts.remove(b)
    screen.blit(burst_surf, (0, 0))

def _draw_hint(selected):
    game_file = GAME_THEMES[selected]["file"]
    if not os.path.exists(game_file):
        msg = f"'{game_file}' not found — place it in the same folder"
        col = (255, 100, 80)
    else:
        msg = "Press ENTER / SPACE or click PLAY to launch"
        col = C_DIM
    blit_text(screen, F_HINT, msg, col, W // 2, H - 56)

def _draw_footer():
    blit_text(screen, F_CREDIT, "Made by Sasa  •  Use arrow keys or mouse", C_DIM, W // 2, H - 30)

if __name__ == "__main__":
    main()
