import pygame
import os 
import random
import math
import numpy as np

pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
pygame.font.init()

Width, Height = 600, 700
Window = pygame.display.set_mode((Width, Height))
pygame.display.set_caption("Space Invaders")

clock = pygame.time.Clock()
FPS = 60

# ═══════════════════════════════════════════════════════════════════
# COLORS
# ═══════════════════════════════════════════════════════════════════
C_WHITE = (240, 240, 255)
C_GOLD = (255, 215, 80)
C_RED = (255, 60, 60)
C_GREEN = (60, 255, 120)
C_CYAN = (80, 200, 255)
C_YELLOW = (255, 220, 50)

# ═══════════════════════════════════════════════════════════════════
# AUDIO
# ═══════════════════════════════════════════════════════════════════

def generate_sound(freq, duration, volume=0.25, wave_type='square'):
    sample_rate = 44100
    samples = int(sample_rate * duration)
    t = np.linspace(0, duration, samples, False)
    if wave_type == 'square':
        wave = np.sign(np.sin(2 * np.pi * freq * t))
    elif wave_type == 'sine':
        wave = np.sin(2 * np.pi * freq * t)
    elif wave_type == 'sawtooth':
        wave = 2 * (t * freq - np.floor(t * freq + 0.5))
    elif wave_type == 'noise':
        wave = np.random.uniform(-1, 1, samples)
    else:
        wave = np.sign(np.sin(2 * np.pi * freq * t))
    fade_samples = min(int(sample_rate * 0.03), samples // 5)
    env = np.ones(samples)
    env[:fade_samples] = np.linspace(0, 1, fade_samples)
    env[-fade_samples:] = np.linspace(1, 0, fade_samples)
    wave = wave * env
    audio = (wave * volume * 32767).astype(np.int16)
    return pygame.sndarray.make_sound(np.column_stack((audio, audio)))

SND_SHOOT = generate_sound(800, 0.12, 0.12, 'square')
SND_EXPLOSION = generate_sound(200, 0.25, 0.2, 'sawtooth')
SND_HIT = generate_sound(400, 0.08, 0.1, 'square')
SND_POWERUP = generate_sound(1200, 0.25, 0.12, 'sine')
SND_LEVEL_UP = generate_sound(600, 0.4, 0.18, 'square')
SND_LOST = generate_sound(150, 0.6, 0.18, 'sawtooth')
SND_SHIELD = generate_sound(900, 0.15, 0.1, 'sine')
SND_COMBO = generate_sound(1500, 0.12, 0.08, 'sine')

# Menu music
sample_rate = 44100
bpm = 100
beat_dur = 60 / bpm
total_beats = 16
duration = beat_dur * total_beats
samples = int(sample_rate * duration)
t = np.linspace(0, duration, samples, False)
bass = np.zeros(samples)
spb = int(sample_rate * beat_dur)
bass_notes = [110, 110, 130.81, 110, 164.81, 196, 164.81, 130.81] * 2
for beat, freq in enumerate(bass_notes):
    start = beat * spb
    end = min((beat + 1) * spb, samples)
    bt = t[start:end] - t[start]
    bw = np.sign(np.sin(2 * np.pi * freq * bt))
    bass[start:end] = bw * np.exp(-bt * 10) * 0.3
melody = np.zeros(samples)
mel_notes = [0, 523, 0, 659, 784, 0, 659, 523, 0, 440, 523, 0, 659, 784, 880, 784]
for beat, freq in enumerate(mel_notes):
    if freq == 0: continue
    start = beat * spb
    end = min((beat + 1) * spb, samples)
    bt = t[start:end] - t[start]
    mw = np.sign(np.sin(2 * np.pi * freq * bt))
    melody[start:end] = mw * np.exp(-bt * 8) * 0.12
hihat = np.zeros(samples)
for beat in range(total_beats):
    start = beat * spb
    end = min(start + int(sample_rate * 0.03), samples)
    noise = np.random.uniform(-1, 1, end - start)
    env = np.exp(-np.linspace(0, 1, end - start) * 20)
    hihat[start:end] = noise * env * 0.05
menu_audio = np.tanh((bass + melody + hihat) * 1.2) / 1.2
menu_audio = (menu_audio * 0.18 * 32767).astype(np.int16)
SND_MENU_MUSIC = pygame.sndarray.make_sound(np.column_stack((menu_audio, menu_audio)))

# ═══════════════════════════════════════════════════════════════════
# FONTS
# ═══════════════════════════════════════════════════════════════════
try:
    main_font = pygame.font.Font("assests/Debrosee-ALPnL.ttf", 32)
    lost_font = pygame.font.Font("assests/Debrosee-ALPnL.ttf", 55)
    title_font = pygame.font.Font("assests/Debrosee-ALPnL.ttf", 55)
    credit_font = pygame.font.Font("assests/Debrosee-ALPnL.ttf", 22)
except FileNotFoundError:
    main_font = pygame.font.SysFont("segoeui", 32)
    lost_font = pygame.font.SysFont("segoeui", 55, bold=True)
    title_font = pygame.font.SysFont("segoeui", 55, bold=True)
    credit_font = pygame.font.SysFont("segoeui", 22)

number_font = pygame.font.SysFont("segoeui", 32, bold=True)
combo_font = pygame.font.SysFont("segoeui", 26, bold=True)
wave_font = pygame.font.SysFont("segoeui", 44, bold=True)

# ═══════════════════════════════════════════════════════════════════
# ASSETS
# ═══════════════════════════════════════════════════════════════════

def load_img(path, size=None):
    try:
        img = pygame.image.load(os.path.join(path))
        if size:
            img = pygame.transform.scale(img, size)
        return img
    except:
        s = pygame.Surface(size or (50, 50), pygame.SRCALPHA)
        pygame.draw.rect(s, (100, 100, 150), s.get_rect(), border_radius=5)
        return s

ENEMY_W, ENEMY_H = 70, 40
player_ship = load_img("assests/pixel_ship_yellow.png")
cyan_ship = pygame.transform.scale(load_img("assests/alien-cyan.png"), (ENEMY_W, ENEMY_H))
magenta_ship = pygame.transform.scale(load_img("assests/alien-magenta.png"), (ENEMY_W, ENEMY_H))
yellow_ship = pygame.transform.scale(load_img("assests/alien-yellow.png"), (ENEMY_W, ENEMY_H))
plain_ship = pygame.transform.scale(load_img("assests/alien.png"), (ENEMY_W, ENEMY_H))

shield_img = pygame.transform.scale(load_img("assests/shield_powerup.png"), (25, 25))
rapid_img = pygame.transform.scale(load_img("assests/bolt_powerup.png"), (25, 25))
heart_img = pygame.transform.scale(load_img("assests/heart.png"), (30, 30))

red_laser = load_img("assests/pixel_laser_red.png")
blue_laser = load_img("assests/pixel_laser_blue.png")
green_laser = load_img("assests/pixel_laser_green.png")
yellow_laser = load_img("assests/pixel_laser_yellow.png")

BG = pygame.transform.scale(load_img("assests/background-black.png"), (Width + 100, Height + 100))

# ═══════════════════════════════════════════════════════════════════
# PARTICLES
# ═══════════════════════════════════════════════════════════════════

class Particle:
    def __init__(self, x, y, color, vx, vy, radius, life=None, glow=False):
        self.x = x
        self.y = y
        self.color = color
        self.vx = vx
        self.vy = vy
        self.radius = radius
        self.max_radius = radius
        self.life = life or int(radius * 10)
        self.max_life = self.life
        self.glow = glow
        self.trail = []

    def update(self):
        self.trail.append((self.x, self.y, self.radius))
        if len(self.trail) > 5:
            self.trail.pop(0)
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.98
        self.vy *= 0.98
        self.life -= 1
        self.radius = max(0, self.max_radius * (self.life / self.max_life))

    def draw(self, surf):
        if self.life <= 0 or self.radius <= 0:
            return
        ratio = self.life / self.max_life
        alpha = int(255 * ratio)
        for i, (tx, ty, tr) in enumerate(self.trail):
            t_ratio = i / len(self.trail)
            t_alpha = int(alpha * t_ratio * 0.4)
            t_r = max(1, int(tr * t_ratio * 0.5))
            if t_alpha > 0:
                s = pygame.Surface((t_r * 2 + 2, t_r * 2 + 2), pygame.SRCALPHA)
                pygame.draw.circle(s, (*self.color, t_alpha), (t_r + 1, t_r + 1), t_r)
                surf.blit(s, (int(tx) - t_r, int(ty) - t_r))
        if self.glow:
            glow_r = int(self.radius * 3)
            glow = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow, (*self.color, alpha // 4), (glow_r, glow_r), glow_r)
            surf.blit(glow, (int(self.x) - glow_r, int(self.y) - glow_r))
        r = max(1, int(self.radius))
        s = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, alpha), (r + 1, r + 1), r)
        surf.blit(s, (int(self.x) - r, int(self.y) - r))

class FloatingText:
    def __init__(self, x, y, text, color, size=24):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.alpha = 255
        self.font = pygame.font.SysFont("segoeui", size, bold=True)
        self.vel_y = -2

    def update(self):
        self.y += self.vel_y
        self.alpha -= 5

    def draw(self, surf):
        if self.alpha > 0:
            text_surf = self.font.render(self.text, True, self.color)
            text_surf.set_alpha(self.alpha)
            surf.blit(text_surf, (self.x - text_surf.get_width() // 2, self.y))

class StarField:
    def __init__(self, count=100):
        self.stars = []
        for _ in range(count):
            self.stars.append({
                'x': random.uniform(0, Width),
                'y': random.uniform(0, Height),
                'size': random.uniform(0.5, 2),
                'speed': random.uniform(0.3, 1.5),
                'brightness': random.randint(80, 200),
                'phase': random.uniform(0, math.tau),
            })

    def update(self, t):
        for star in self.stars:
            star['y'] += star['speed']
            if star['y'] > Height + 5:
                star['y'] = -5
                star['x'] = random.uniform(0, Width)
            star['phase'] += 0.02

    def draw(self, surf, t):
        for star in self.stars:
            twinkle = 0.6 + 0.4 * abs(math.sin(star['phase'] + t * 0.03))
            alpha = int(star['brightness'] * twinkle)
            s = pygame.Surface((4, 4), pygame.SRCALPHA)
            pygame.draw.circle(s, (255, 255, 255, alpha), (2, 2), int(star['size']))
            surf.blit(s, (int(star['x']) - 2, int(star['y']) - 2))

class ScreenShake:
    def __init__(self):
        self.intensity = 0
        self.duration = 0

    def trigger(self, intensity=5, duration=10):
        self.intensity = intensity
        self.duration = duration

    def update(self):
        if self.duration > 0:
            self.duration -= 1
            self.intensity *= 0.9
            if self.duration <= 0:
                self.intensity = 0

    def get_offset(self):
        if self.intensity <= 0:
            return (0, 0)
        return (random.randint(-int(self.intensity), int(self.intensity)),
                random.randint(-int(self.intensity), int(self.intensity)))

# ═══════════════════════════════════════════════════════════════════
# GAME CLASSES
# ═══════════════════════════════════════════════════════════════════

def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    try:
        return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None
    except:
        return False

class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        try:
            self.mask = pygame.mask.from_surface(self.img)
        except:
            self.mask = None

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return self.y > height or self.y < -50

    def collision(self, obj):
        return collide(self, obj)

    def draw(self, surf):
        surf.blit(self.img, (self.x, self.y))
        glow = pygame.Surface((self.img.get_width() + 8, self.img.get_height() + 8), pygame.SRCALPHA)
        pygame.draw.ellipse(glow, (255, 255, 100, 30), glow.get_rect())
        surf.blit(glow, (self.x - 4, self.y - 4))

class Ship:
    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cooldown = 0
        self.max_cooldown = 30

    def move_lasers(self, vel, obj):
        self.cooldown = max(0, self.cooldown - 1)
        for laser in self.lasers[:]:
            laser.move(vel)
            if laser.off_screen(Height):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def shoot(self):
        if self.cooldown <= 0:
            laser = Laser(self.x + self.get_width() // 2 - self.laser_img.get_width() // 2, 
                         self.y, self.laser_img)
            self.lasers.append(laser)
            self.cooldown = self.max_cooldown
            return True
        self.cooldown = max(0, self.cooldown - 1)
        return False

    def get_width(self):
        return self.ship_img.get_width() if self.ship_img else 50

    def get_height(self):
        return self.ship_img.get_height() if self.ship_img else 50

    def draw(self, surf):
        surf.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(surf)

class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = player_ship
        self.laser_img = yellow_laser
        try:
            self.mask = pygame.mask.from_surface(self.ship_img)
        except:
            self.mask = None
        self.max_health = health
        self.default_cooldown = 15
        self.max_cooldown = 15
        self.rapid_fire_expiry = 0
        self.shield_active = False
        self.shield_health = 0
        self.score = 0
        self.combo = 0
        self.combo_timer = 0
        self.weapon_level = 1

    def move_lasers(self, vel, enemies, powerups, particles, texts, shake):
        self.cooldown = max(0, self.cooldown - 1)
        for laser in self.lasers[:]:
            laser.move(vel)
            if laser.off_screen(Height):
                self.lasers.remove(laser)
            else:
                for enemy in enemies[:]:
                    if laser.collision(enemy):
                        self.combo += 1
                        self.combo_timer = 60
                        points = 10 * self.combo
                        self.score += points

                        if self.combo > 1:
                            texts.append(FloatingText(enemy.x + enemy.get_width() // 2, 
                                       enemy.y, f"x{self.combo}!", C_GOLD, 22))
                            if self.combo % 5 == 0:
                                SND_COMBO.play()

                        texts.append(FloatingText(enemy.x + enemy.get_width() // 2, 
                                   enemy.y - 20, f"+{points}", C_WHITE, 20))

                        color_map = {
                            "red": (255, 50, 150),
                            "green": (100, 255, 100),
                            "blue": (50, 200, 255),
                            "yellow": (255, 255, 50)
                        }
                        exp_color = color_map.get(enemy.color, C_WHITE)
                        for _ in range(20):
                            particles.append(Particle(
                                enemy.x + enemy.get_width() / 2,
                                enemy.y + enemy.get_height() / 2,
                                exp_color,
                                random.uniform(-5, 5),
                                random.uniform(-5, 5),
                                random.uniform(2, 6),
                                glow=True
                            ))

                        shake.trigger(4, 8)
                        SND_EXPLOSION.play()

                        if random.random() < 0.25:
                            roll = random.randint(1, 100)
                            if roll <= 5:
                                ptype = "extra_life"
                            elif roll <= 45:
                                ptype = "shield"
                            else:
                                ptype = "rapid_fire"
                            powerups.append(Powerup(enemy.x + enemy.get_width() // 2 - 12, 
                                                   enemy.y, ptype))

                        enemies.remove(enemy)
                        if laser in self.lasers:
                            self.lasers.remove(laser)
                        break

    def shoot(self, particles_list):
        if self.cooldown <= 0:
            SND_SHOOT.play()
            for _ in range(3):
                particles_list.append(Particle(
                    self.x + self.get_width() // 2 + random.randint(-5, 5),
                    self.y + self.get_height(),
                    (255, 200, 50),
                    random.uniform(-0.5, 0.5),
                    random.uniform(1, 3),
                    random.uniform(1, 3),
                    glow=True
                ))

            if self.weapon_level == 1:
                laser = Laser(self.x + self.get_width() // 2 - self.laser_img.get_width() // 2,
                             self.y, self.laser_img)
                self.lasers.append(laser)
            elif self.weapon_level == 2:
                for offset in [-15, 15]:
                    laser = Laser(self.x + self.get_width() // 2 - self.laser_img.get_width() // 2 + offset,
                                 self.y, self.laser_img)
                    self.lasers.append(laser)
            else:
                for offset in [-20, 0, 20]:
                    laser = Laser(self.x + self.get_width() // 2 - self.laser_img.get_width() // 2 + offset,
                                 self.y, self.laser_img)
                    self.lasers.append(laser)

            self.cooldown = self.max_cooldown
            return True
        self.cooldown = max(0, self.cooldown - 1)
        return False

    def draw(self, surf):
        super().draw(surf)
        self.draw_healthbar(surf)
        if self.shield_active and self.shield_health > 0:
            self.draw_shield(surf)

    def draw_healthbar(self, surf):
        bar_w = self.ship_img.get_width()
        bar_h = 8
        bar_y = self.y + self.ship_img.get_height() + 8
        pygame.draw.rect(surf, (60, 20, 20), (self.x - 1, bar_y - 1, bar_w + 2, bar_h + 2), border_radius=4)
        health_w = int(bar_w * (self.health / self.max_health))
        health_color = (60, 255, 120) if self.health > 50 else (255, 200, 50) if self.health > 25 else (255, 60, 60)
        pygame.draw.rect(surf, health_color, (self.x, bar_y, health_w, bar_h), border_radius=4)
        glow = pygame.Surface((bar_w + 4, bar_h + 4), pygame.SRCALPHA)
        pygame.draw.rect(glow, (*health_color, 40), glow.get_rect(), border_radius=5)
        surf.blit(glow, (self.x - 2, bar_y - 2))

    def draw_shield(self, surf):
        shield_r = max(self.get_width(), self.get_height()) // 2 + 15
        shield_surf = pygame.Surface((shield_r * 2 + 4, shield_r * 2 + 4), pygame.SRCALPHA)
        alpha = int(80 + 40 * math.sin(pygame.time.get_ticks() * 0.005))
        pygame.draw.circle(shield_surf, (80, 200, 255, alpha), 
                          (shield_r + 2, shield_r + 2), shield_r, 2)
        pygame.draw.circle(shield_surf, (80, 200, 255, alpha // 3), 
                          (shield_r + 2, shield_r + 2), shield_r - 5)
        surf.blit(shield_surf, (self.x + self.get_width() // 2 - shield_r - 2,
                                self.y + self.get_height() // 2 - shield_r - 2))

class Enemy(Ship):
    color_map = {
        "red": (magenta_ship, red_laser, 2.7),
        "green": (plain_ship, green_laser, 1.7),
        "blue": (cyan_ship, blue_laser, 1.0),
        "yellow": (yellow_ship, yellow_laser, 2.0)
    }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img, self.vel = self.color_map[color]
        try:
            self.mask = pygame.mask.from_surface(self.ship_img)
        except:
            self.mask = None
        self.color = color
        self.max_cooldown = random.randint(80, 150)
        self.cooldown = random.randint(0, self.max_cooldown)
        self.wobble = random.uniform(0, math.tau)
        self.wobble_speed = random.uniform(0.02, 0.05)

    def move(self, vel):
        self.y += vel
        self.wobble += self.wobble_speed
        self.x += math.sin(self.wobble) * 0.5

    def shoot(self):
        if self.cooldown <= 0:
            laser = Laser(self.x + self.get_width() // 2 - self.laser_img.get_width() // 2,
                         self.y + self.get_height(), self.laser_img)
            self.lasers.append(laser)
            self.cooldown = self.max_cooldown
        else:
            self.cooldown -= 1

    def draw(self, surf):
        super().draw(surf)
        glow = pygame.Surface((self.get_width() + 16, self.get_height() + 16), pygame.SRCALPHA)
        color_map = {"red": (255, 50, 150), "green": (100, 255, 100), 
                    "blue": (50, 200, 255), "yellow": (255, 255, 50)}
        glow_color = color_map.get(self.color, (100, 100, 100))
        pygame.draw.ellipse(glow, (*glow_color, 25), glow.get_rect())
        surf.blit(glow, (self.x - 8, self.y - 8))

class Boss(Enemy):
    def __init__(self, x, y, level):
        super().__init__(x, y, "red", health=200 + level * 50)
        self.ship_img = pygame.transform.scale(magenta_ship, (120, 70))
        try:
            self.mask = pygame.mask.from_surface(self.ship_img)
        except:
            self.mask = None
        self.vel = 0.8
        self.max_cooldown = 30
        self.phase = 0
        self.direction = 1

    def move(self, vel):
        self.x += self.vel * self.direction
        if self.x <= 20 or self.x >= Width - self.get_width() - 20:
            self.direction *= -1
        self.phase += 0.03
        self.y = 50 + math.sin(self.phase) * 30

    def shoot(self):
        if self.cooldown <= 0:
            for offset in [-30, 0, 30]:
                laser = Laser(self.x + self.get_width() // 2 - self.laser_img.get_width() // 2 + offset,
                             self.y + self.get_height(), self.laser_img)
                self.lasers.append(laser)
            self.cooldown = self.max_cooldown
        else:
            self.cooldown -= 1

class Powerup:
    def __init__(self, x, y, ptype):
        self.x = x
        self.y = y
        self.type = ptype
        self.img = shield_img if ptype == "shield" else rapid_img if ptype == "rapid_fire" else heart_img
        self.width = self.img.get_width()
        self.height = self.img.get_height()
        self.phase = random.uniform(0, math.tau)

    def move(self, vel):
        self.y += vel
        self.phase += 0.05
        self.x += math.sin(self.phase) * 0.5

    def draw(self, surf):
        glow = pygame.Surface((40, 40), pygame.SRCALPHA)
        color = {"shield": (80, 200, 255), "rapid_fire": (255, 200, 50), "extra_life": (255, 80, 80)}
        c = color.get(self.type, C_WHITE)
        pygame.draw.circle(glow, (*c, 40), (20, 20), 18)
        surf.blit(glow, (self.x - 20 + self.width // 2, self.y - 20 + self.height // 2))
        surf.blit(self.img, (self.x, self.y))

    def collision(self, obj):
        return (self.x + self.width > obj.x and self.x < obj.x + obj.get_width() and
                self.y + self.height > obj.y and self.y < obj.y + obj.get_height())

# ═══════════════════════════════════════════════════════════════════
# DRAW FUNCTIONS
# ═══════════════════════════════════════════════════════════════════

def draw_lives(surf, lives):
    for i in range(lives):
        x = 10 + i * 35
        y = 10
        glow = pygame.Surface((34, 34), pygame.SRCALPHA)
        pygame.draw.circle(glow, (255, 80, 80, 40), (17, 17), 15)
        surf.blit(glow, (x - 2, y - 2))
        surf.blit(heart_img, (x, y))

def draw_level(surf, level):
    word = main_font.render("LEVEL", True, C_WHITE)
    num = number_font.render(str(level), True, C_GOLD)
    total_w = word.get_width() + num.get_width() + 5
    start_x = Width - total_w - 15
    surf.blit(word, (start_x, 10))
    surf.blit(num, (start_x + word.get_width() + 5, 8))

def draw_score(surf, score, combo):
    score_text = main_font.render(f"Score: {score}", True, C_WHITE)
    surf.blit(score_text, (15, 45))
    if combo > 1:
        combo_text = combo_font.render(f"COMBO x{combo}", True, C_GOLD)
        pulse = abs(math.sin(pygame.time.get_ticks() * 0.008))
        glow_surf = combo_font.render(f"COMBO x{combo}", True, C_GOLD)
        glow_surf.set_alpha(int(100 * pulse))
        surf.blit(glow_surf, (15, 75))
        surf.blit(combo_text, (15, 75))

def draw_wave_announcement(surf, level, t):
    if t < 120:
        progress = min(1.0, t / 30)
        if t > 90:
            progress = max(0, 1.0 - (t - 90) / 30)
        alpha = int(255 * progress)
        wave_text = wave_font.render(f"WAVE {level}", True, C_GOLD)
        wave_text.set_alpha(alpha)
        glow = wave_font.render(f"WAVE {level}", True, C_GOLD)
        glow.set_alpha(alpha // 3)
        for offset in range(3, 0, -1):
            surf.blit(glow, (Width // 2 - glow.get_width() // 2 + offset, 
                            Height // 2 - 100 + offset))
        surf.blit(wave_text, (Width // 2 - wave_text.get_width() // 2, Height // 2 - 100))

def draw_lost(surf, score, level):
    overlay = pygame.Surface((Width, Height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    surf.blit(overlay, (0, 0))
    lost_label = lost_font.render("GAME OVER", True, C_RED)
    score_label = main_font.render(f"Final Score: {score}", True, C_WHITE)
    level_label = main_font.render(f"Reached Level: {level}", True, C_GOLD)
    restart_label = main_font.render("Press ENTER to restart", True, C_WHITE)
    surf.blit(lost_label, (Width // 2 - lost_label.get_width() // 2, 250))
    surf.blit(score_label, (Width // 2 - score_label.get_width() // 2, 330))
    surf.blit(level_label, (Width // 2 - level_label.get_width() // 2, 370))
    surf.blit(restart_label, (Width // 2 - restart_label.get_width() // 2, 430))

def draw_shield_bar(surf, player):
    if player.shield_active and player.shield_health > 0:
        bar_w = 120
        bar_h = 6
        x = Width // 2 - bar_w // 2
        y = Height - 30
        pygame.draw.rect(surf, (20, 40, 60), (x - 1, y - 1, bar_w + 2, bar_h + 2), border_radius=3)
        shield_w = int(bar_w * (player.shield_health / 100))
        pygame.draw.rect(surf, (80, 200, 255), (x, y, shield_w, bar_h), border_radius=3)
        label = main_font.render("SHIELD", True, (80, 200, 255))
        label.set_alpha(150)
        surf.blit(label, (x + bar_w // 2 - label.get_width() // 2, y - 22))

# ═══════════════════════════════════════════════════════════════════
# MAIN GAME
# ═══════════════════════════════════════════════════════════════════

def main():
    run = True
    level = 0
    lives = 5
    score = 0

    enemies = []
    powerups = []
    particles = []
    texts = []
    shake = ScreenShake()
    starfield = StarField(120)

    wave_length = 5
    enemy_vel = 1
    player_vel = 5
    laser_vel = 6
    powerup_vel = 2

    player = Player(250, 520)

    lost = False
    lost_count = 0
    wave_timer = 0
    bg_y = 0

    # Try file-based music first, fallback to procedural
    try:
        pygame.mixer.music.load(os.path.join("assests/background_music.mp3"))
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
    except:
        SND_MENU_MUSIC.stop()

    def redraw_window():
        nonlocal bg_y
        parallax_x = (Width / 2 - player.x) * 0.08
        parallax_y = (Height / 2 - player.y) * 0.08
        draw_x = int(parallax_x - 50)
        draw_y = int(bg_y + parallax_y - 50)

        Window.blit(BG, (draw_x, draw_y))
        Window.blit(BG, (draw_x, draw_y - BG.get_height() + 10))

        starfield.update(pygame.time.get_ticks() // 16)
        starfield.draw(Window, pygame.time.get_ticks() // 16)

        ox, oy = shake.get_offset()

        for enemy in enemies:
            enemy.draw(Window)
        for powerup in powerups:
            powerup.draw(Window)
        for p in particles:
            p.draw(Window)
        for text in texts:
            text.draw(Window)

        if not lost:
            player.draw(Window)

        draw_lives(Window, lives)
        draw_level(Window, level)
        draw_score(Window, score, player.combo)
        draw_shield_bar(Window, player)
        draw_wave_announcement(Window, level, wave_timer)

        if lost:
            draw_lost(Window, score, level)

        pygame.display.update()

    while run:
        clock.tick(FPS)
        bg_y += 0.5
        if bg_y >= BG.get_height() - 10:
            bg_y = 0
        wave_timer += 1
        shake.update()

        if player.combo_timer > 0:
            player.combo_timer -= 1
        else:
            player.combo = 0

        redraw_window()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1
            if lost_count == 1:
                SND_LOST.play()

        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        run = False
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            return True
                continue

        if len(enemies) == 0:
            level += 1
            wave_length += 4
            wave_timer = 0
            SND_LEVEL_UP.play()
            texts.append(FloatingText(Width // 2, Height // 2, f"WAVE {level}!", C_GOLD, 40))

            if level % 5 == 0:
                enemies.append(Boss(Width // 2 - 60, 50, level))

            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, Width - 120),
                             random.randrange(-1500 - level * 100, -100),
                             random.choice(["blue", "green", "yellow", "red"]))
                enemies.append(enemy)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - player_vel > 0:
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < Width:
            player.x += player_vel
        if keys[pygame.K_w] and player.y - player_vel > 0:
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + player_vel + player.get_height() < Height:
            player.y += player_vel

        if keys[pygame.K_SPACE]:
            if player.shoot(particles):
                for _ in range(3):
                    particles.append(Particle(
                        player.x + player.get_width() // 2 + random.randint(-5, 5),
                        player.y + player.get_height(),
                        (255, 200, 50),
                        random.uniform(-0.5, 0.5),
                        random.uniform(1, 3),
                        random.uniform(1, 3),
                        glow=True
                    ))

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, max(30, 120 - level * 3)) == 1:
                enemy.shoot()

            if collide(enemy, player):
                if player.shield_active and player.shield_health > 0:
                    player.shield_health -= 20
                    if player.shield_health <= 0:
                        player.shield_active = False
                    enemies.remove(enemy)
                    SND_HIT.play()
                    shake.trigger(3, 6)
                else:
                    player.health -= 15
                    enemies.remove(enemy)
                    SND_HIT.play()
                    shake.trigger(5, 10)
                    for _ in range(10):
                        particles.append(Particle(
                            player.x + player.get_width() // 2,
                            player.y + player.get_height() // 2,
                            (255, 100, 100),
                            random.uniform(-3, 3),
                            random.uniform(-3, 3),
                            random.uniform(2, 5),
                            glow=True
                        ))
                    if player.health <= 0:
                        lives -= 1
                        player.health = player.max_health
                        player.shield_active = False
                        player.shield_health = 0
                        texts.append(FloatingText(player.x, player.y, "-1 LIFE", C_RED, 30))

            elif enemy.y + enemy.get_height() > Height:
                lives -= 1
                enemies.remove(enemy)
                texts.append(FloatingText(Width // 2, Height // 2, "ENEMY ESCAPED!", C_RED, 28))

        player.move_lasers(-laser_vel, enemies, powerups, particles, texts, shake)

        for powerup in powerups[:]:
            powerup.move(powerup_vel)
            if powerup.y > Height:
                powerups.remove(powerup)
            elif powerup.collision(player):
                SND_POWERUP.play()
                if powerup.type == "shield":
                    player.shield_active = True
                    player.shield_health = 100
                    texts.append(FloatingText(player.x, player.y - 30, "SHIELD UP!", (80, 200, 255), 26))
                    SND_SHIELD.play()
                elif powerup.type == "extra_life":
                    if lives < 5:
                        lives += 1
                    texts.append(FloatingText(player.x, player.y - 30, "+1 LIFE", C_RED, 26))
                elif powerup.type == "rapid_fire":
                    player.max_cooldown = max(5, player.max_cooldown - 3)
                    player.rapid_fire_expiry = pygame.time.get_ticks() + 8000
                    texts.append(FloatingText(player.x, player.y - 30, "RAPID FIRE!", C_YELLOW, 26))
                    if player.max_cooldown <= 8 and player.weapon_level < 3:
                        player.weapon_level += 1
                        player.max_cooldown = player.default_cooldown
                        texts.append(FloatingText(player.x, player.y - 60, 
                                   f"WEAPON LVL {player.weapon_level}!", C_GOLD, 30))
                powerups.remove(powerup)

        if player.rapid_fire_expiry > 0:
            if pygame.time.get_ticks() >= player.rapid_fire_expiry:
                player.max_cooldown = player.default_cooldown
                player.rapid_fire_expiry = 0

        for particle in particles[:]:
            particle.update()
            if particle.life <= 0 or particle.radius <= 0:
                particles.remove(particle)

        for text in texts[:]:
            text.update()
            if text.alpha <= 0:
                texts.remove(text)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                return False

    return False

# ═══════════════════════════════════════════════════════════════════
# MAIN MENU
# ═══════════════════════════════════════════════════════════════════

def main_menu():
    # Try file-based menu music first, fallback to procedural
    try:
        pygame.mixer.music.load(os.path.join("assests/menu_music.mp3"))
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
    except:
        SND_MENU_MUSIC.play(-1)

    try:
        rotated_ship = pygame.transform.rotate(player_ship, 315)
    except:
        rotated_ship = pygame.Surface((50, 50))
        rotated_ship.fill((255, 255, 0))

    starfield = StarField(80)
    particles = []

    fade_surface = pygame.Surface((Width, Height))
    fade_surface.fill((0, 0, 0))
    alpha = 255
    title_pulse = 0

    run = True
    while run:
        clock.tick(FPS)
        title_pulse += 0.03

        Window.blit(BG, (0, 0))
        starfield.update(pygame.time.get_ticks() // 16)
        starfield.draw(Window, pygame.time.get_ticks() // 16)

        if random.random() < 0.1:
            particles.append(Particle(
                random.randint(0, Width), Height + 10,
                random.choice([(80, 200, 255), (255, 100, 180), (120, 255, 140)]),
                random.uniform(-0.3, 0.3), random.uniform(-0.5, -2),
                random.uniform(1, 3), glow=True
            ))

        for p in particles[:]:
            p.update()
            p.draw(Window)
            if p.life <= 0:
                particles.remove(p)

        game_label = title_font.render("SPACE INVADERS", True, C_WHITE)
        glow_intensity = int(30 + 20 * abs(math.sin(title_pulse)))
        for offset in range(4, 0, -1):
            glow = title_font.render("SPACE INVADERS", True, C_CYAN)
            glow.set_alpha(glow_intensity // offset)
            Window.blit(glow, (Width // 2 - glow.get_width() // 2 + offset, 100 + offset))
        Window.blit(game_label, (Width // 2 - game_label.get_width() // 2, 100))

        credit_label = credit_font.render("by Sasa", True, (180, 180, 200))
        Window.blit(credit_label, (Width // 2 - credit_label.get_width() // 2, 170))

        ship_x = Width // 2 - rotated_ship.get_width() // 2
        ship_y = 220 + int(math.sin(title_pulse * 1.5) * 8)
        Window.blit(rotated_ship, (ship_x, ship_y))

        blink = abs(math.sin(title_pulse * 2))
        if blink > 0.3:
            start_label = main_font.render("CLICK TO START", True, C_GOLD)
            start_label.set_alpha(int(200 + 55 * blink))
            Window.blit(start_label, (Width // 2 - start_label.get_width() // 2, 400))

        controls = main_font.render("WASD to move  |  SPACE to shoot", True, (120, 120, 140))
        controls.set_alpha(150)
        Window.blit(controls, (Width // 2 - controls.get_width() // 2, 460))

        if alpha > 0:
            fade_surface.set_alpha(alpha)
            Window.blit(fade_surface, (0, 0))
            alpha -= 3

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                try:
                    pygame.mixer.music.fadeout(500)
                except:
                    SND_MENU_MUSIC.fadeout(500)
                restart = True
                while restart:
                    restart = main()
                try:
                    pygame.mixer.music.play(-1)
                except:
                    SND_MENU_MUSIC.play(-1)
                alpha = 100

    pygame.quit()

if __name__ == "__main__":
    main_menu()
