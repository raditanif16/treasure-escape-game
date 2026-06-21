import random
import math
from pygame import Rect

WIDTH = 1000
HEIGHT = 600
GROUND_Y = 500

game_state = "menu"
sound_enabled = True
music_started = False

current_level = 1
max_levels = 3

global_timer = 0
mouse_x, mouse_y = 0, 0

shake_timer = 0

start_button = Rect(300, 200, 400, 60)
sound_button = Rect(200, 290, 600, 60)
exit_button = Rect(300, 380, 400, 60)

platforms = []
enemies = []
treasure = Actor("chest")

class Cloud:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(20, 200)
        self.speed = random.uniform(0.2, 0.8)
        self.w = random.randint(60, 120)
        self.h = random.randint(20, 40)

    def update(self):
        self.x -= self.speed
        if self.x < -self.w - 20:
            self.x = WIDTH + 20
            self.y = random.randint(20, 200)

    def draw(self, color):
        screen.draw.filled_rect(Rect(self.x, self.y, self.w, self.h), color)
        screen.draw.filled_rect(Rect(self.x + 15, self.y - 15, self.w - 30, self.h + 30), color)

class Confetti:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(-HEIGHT, 0)
        self.speed = random.uniform(2, 5)
        self.color = random.choice([(255,0,0), (0,255,0), (0,150,255), (255,255,0), (255,0,255)])

    def update(self):
        self.y += self.speed
        self.x += math.sin(self.y * 0.05) * 2
        if self.y > HEIGHT:
            self.y = random.randint(-50, -10)
            self.x = random.randint(0, WIDTH)

    def draw(self):
        screen.draw.filled_rect(Rect(self.x, self.y, 6, 6), self.color)

clouds_list = [Cloud() for _ in range(6)]
confetti_list = [Confetti() for _ in range(80)]
        
class Player:
    def __init__(self):
        self.actor = Actor("player_idle1")
        self.actor.bottomleft = (50, GROUND_Y)
        
        self.speed = 5
        self.velocity_y = 0
        self.gravity = 0.5  
        self.jump_power = -14 
        self.on_ground = True
        
        self.idle_frames = ["player_idle1", "player_idle2"]
        self.run_frames = ["player_run1", "player_run2"]
        self.frame = 0
        self.timer = 0
        self.is_moving = False

    def move(self):
        self.is_moving = False
        old_y = self.actor.bottom

        if keyboard.left:
            self.actor.x -= self.speed
            self.is_moving = True
        if keyboard.right:
            self.actor.x += self.speed
            self.is_moving = True

        if self.actor.left < 0: self.actor.left = 0
        if self.actor.right > WIDTH: self.actor.right = WIDTH

        if (keyboard.space or keyboard.up) and self.on_ground:
            if sound_enabled:
                try: sounds.jump.play()
                except: pass
            self.velocity_y = self.jump_power
            self.on_ground = False

        self.velocity_y += self.gravity
        self.actor.y += self.velocity_y
        self.on_ground = False

        if self.actor.bottom >= GROUND_Y:
            self.actor.bottom = GROUND_Y
            self.velocity_y = 0
            self.on_ground = True

        if self.velocity_y > 0:
            for plat in platforms:
                if self.actor.colliderect(plat) and old_y <= plat.top:

                    self.actor.bottom = plat.top
                    self.velocity_y = 0
                    self.on_ground = True

    def animate(self):
        self.timer += 1
        if self.timer < 8: return
        self.timer = 0
        self.frame += 1
        
        if self.is_moving:
            self.actor.image = self.run_frames[self.frame % len(self.run_frames)]
        else:
            self.actor.image = self.idle_frames[self.frame % len(self.idle_frames)]

    def draw(self):
        self.actor.draw()

class Enemy:
    def __init__(self, x, y, speed):
        self.actor = Actor("enemy_run1")
        self.actor.bottom = y
        self.actor.x = x
        self.speed = speed
        self.direction = random.choice([-1, 1])
        self.idle_frames = ["enemy_idle1", "enemy_idle2"]
        self.run_frames = ["enemy_run1", "enemy_run2"]
        self.frame = 0
        self.anim_timer = 0
        self.state = "moving" 
        self.state_timer = random.randint(60, 120)

    def update(self):
        self.state_timer -= 1
        if self.state_timer <= 0:
            if self.state == "moving":
                self.state = "idle"
                self.state_timer = random.randint(40, 80)
            else:
                self.state = "moving"
                self.direction *= -1
                self.state_timer = random.randint(60, 150)

        if self.state == "moving":
            self.actor.x += self.speed * self.direction
            if self.actor.x > WIDTH - 50 or self.actor.x < 50:
                self.direction *= -1

    def animate(self):
        self.anim_timer += 1
        if self.anim_timer < 10: return
        self.anim_timer = 0
        self.frame += 1
        
        if self.state == "moving":
            self.actor.image = self.run_frames[self.frame % len(self.run_frames)]
        else:
            self.actor.image = self.idle_frames[self.frame % len(self.idle_frames)]

    def draw(self):
        self.actor.draw()

player = Player()

def load_level(level):
    global platforms, enemies
    
    player.actor.bottomleft = (50, GROUND_Y)
    player.velocity_y = 0
    player.actor.image = "player_idle1"
    
    if level == 1:
        platforms = [Rect(150, 380, 150, 20), Rect(400, 280, 150, 20), Rect(650, 180, 150, 20), Rect(850, 100, 120, 20)]
        enemies = [Enemy(300, GROUND_Y, 2), Enemy(600, GROUND_Y, 2), Enemy(850, GROUND_Y, 2)]
        treasure.bottomleft = (880, platforms[3].top)
        
    elif level == 2:
        platforms = [
            Rect(200, 400, 180, 20), # Pijakan 1 (Kiri)
            Rect(500, 300, 180, 20), # Pijakan 2 (Kanan)
            Rect(200, 200, 180, 20), # Pijakan 3 (Kiri)
            Rect(500, 100, 180, 20)  # Pijakan 4 (Kanan)
        ]
        enemies = [Enemy(350, GROUND_Y, 2), Enemy(650, GROUND_Y, 2), Enemy(850, GROUND_Y, 2)]
        treasure.bottomleft = (550, platforms[3].top)
        
    elif level == 3:
        platforms = [Rect(150, 400, 130, 20), Rect(350, 320, 130, 20), Rect(550, 240, 130, 20), Rect(750, 160, 130, 20), Rect(900, 80, 100, 20)]
        enemies = [Enemy(300, GROUND_Y, 2.5), Enemy(550, GROUND_Y, 2.5), Enemy(800, GROUND_Y, 2.5)]
        treasure.bottomleft = (920, platforms[4].top)

def reset_game():
    global current_level
    current_level = 1
    load_level(current_level)

def update():
    global game_state, global_timer, current_level, shake_timer

    global_timer += 0.05
    if shake_timer > 0:
        shake_timer -= 1
        
    for cloud in clouds_list:
        cloud.update()

    if game_state == "win":
        for c in confetti_list:
            c.update()

    if game_state != "play":
        return

    player.move()
    player.animate()

    for enemy in enemies:
        enemy.update()
        enemy.animate()

        if player.actor.colliderect(enemy.actor):
            game_state = "game_over"
            shake_timer = 15
            if sound_enabled:
                music.stop()
                try: 
                    sounds.hit.play()
                    music.play("gameover")
                except: pass
            return

    if player.actor.colliderect(treasure) and game_state == "play":
        if current_level < max_levels:
            current_level += 1
            load_level(current_level)
            if sound_enabled:
                try: sounds.coin.play()
                except: pass
        else:
            game_state = "win"
            if sound_enabled:
                music.stop()
                try:
                    sounds.win.play()
                    music.play("winner")
                except: pass

def draw():
    global music_started

    if game_state == "menu" and sound_enabled and not music_started:
        try: music.play("mainmenu")
        except: pass
        music_started = True
        
    screen.clear()

    offset_x = 0
    offset_y = 0

    if shake_timer > 0:
        offset_x = random.randint(-5, 5)
        offset_y = random.randint(-5, 5)

    screen.surface.scroll(offset_x, offset_y)

    if game_state == "menu":
        draw_menu()
    elif game_state == "play":
        draw_game()
    elif game_state == "game_over":
        draw_message(
            "GAME OVER",
            (180, 50, 50)
        )
    elif game_state == "win":
        draw_message(
            "YOU WIN!",
            (50, 160, 80)
        )

def draw_custom_button(rect, text, normal_color, hover_color, font_size):
    is_hovered = rect.collidepoint(mouse_x, mouse_y)
    y_offset = -4 if is_hovered else 0
    current_color = hover_color if is_hovered else normal_color
    
    screen.draw.filled_rect(Rect(rect.x + 6, rect.y + 6, rect.w, rect.h), (20, 20, 30))
    button_body = Rect(rect.x, rect.y + y_offset, rect.w, rect.h)
    screen.draw.filled_rect(button_body, current_color)
    screen.draw.rect(button_body, (255, 255, 255))
    screen.draw.text(text, center=button_body.center, fontsize=font_size, color="white", owidth=1.5, ocolor="black")

def draw_menu():
    screen.fill((43, 45, 66)) 
    for cloud in clouds_list:
        cloud.draw((60, 65, 90))

    title_y = 100 + math.sin(global_timer * 2) * 10
    screen.draw.text("TREASURE ESCAPE", center=(WIDTH//2, title_y), fontsize=75, color=(255, 215, 0), owidth=4, ocolor=(139, 0, 0))

    draw_custom_button(start_button, "Mulai Permainan", (239, 35, 60), (255, 80, 100), 40)
    sound_color = (42, 157, 143) if sound_enabled else (141, 153, 174)
    sound_hover = (60, 190, 175) if sound_enabled else (170, 180, 200)
    draw_custom_button(sound_button, "Aktifkan/Nonaktifkan Musik dan Suara", sound_color, sound_hover, 30)
    draw_custom_button(exit_button, "Keluar", (141, 153, 174), (170, 180, 200), 40)

def draw_game():
    if current_level == 1:
        bg_color = (142, 202, 230) # Pagi
        cloud_color = (255, 255, 255)
    elif current_level == 2:
        bg_color = (255, 170, 90)  # Senja
        cloud_color = (255, 220, 180)
    else:
        bg_color = (20, 30, 60)    # Malam
        cloud_color = (50, 60, 90)

    screen.fill(bg_color)
    for cloud in clouds_list:
        cloud.draw(cloud_color)

    screen.draw.text(f"LEVEL {current_level}", topleft=(20, 20), fontsize=40, color="white", owidth=2, ocolor="black")
    
    screen.draw.text(
        f"{current_level}/{max_levels}",
        topright=(970, 20),
        fontsize=35,
        color="white",
        owidth=2,
        ocolor="black"
    )

    screen.draw.filled_rect(Rect(0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y), (33, 158, 188))
    screen.draw.filled_rect(Rect(0, GROUND_Y, WIDTH, 10), (2, 48, 71)) 

    for plat in platforms:
        screen.draw.filled_rect(plat, (251, 133, 0))
        screen.draw.filled_rect(Rect(plat.x, plat.y, plat.w, 5), (255, 183, 3))
        screen.draw.rect(plat, (0, 0, 0))

    treasure.draw()
    for enemy in enemies:
        enemy.draw()
    player.draw()

def draw_message(title, bg_color):
    screen.fill(bg_color)
    
    if game_state == "win":
        for c in confetti_list:
            c.draw()

    pulse_color_val = int(180 + 75 * math.sin(global_timer * 4))
    pulse_color = (pulse_color_val, pulse_color_val, pulse_color_val // 2)

    screen.draw.text(title, center=(WIDTH // 2, HEIGHT // 2 - 30), fontsize=90, color="white", owidth=4, ocolor="black")
    screen.draw.text("Klik dimana saja untuk kembali ke Menu", center=(WIDTH // 2, HEIGHT // 2 + 50), fontsize=40, color=pulse_color, owidth=1.5, ocolor="black")

def on_mouse_move(pos):
    global mouse_x, mouse_y
    mouse_x, mouse_y = pos

def on_mouse_down(pos):
    global game_state, sound_enabled, music_started

    if game_state == "menu":
        if start_button.collidepoint(pos):
            if sound_enabled:
                try: sounds.click.play()
                except: pass
            music.stop()
            music_started = False
            if sound_enabled:
                try: music.play("gameplay")
                except: pass
            reset_game()
            game_state = "play"

        elif sound_button.collidepoint(pos):
            sound_enabled = not sound_enabled
            if not sound_enabled:
                music.stop()
                music_started = False
            else:
                try:
                    sounds.click.play()
                    music.play("mainmenu")
                except: pass
                music_started = True

        elif exit_button.collidepoint(pos):
            exit()

    elif game_state in ("game_over", "win"):
        music.stop()
        music_started = False
        game_state = "menu"