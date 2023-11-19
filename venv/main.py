import pygame
import time
import random

#set fonts
pygame.font.init()

# window variables
WIDTH, HEIGHT = 1000,700
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Halo Space Invaders')

# Load images
BACKGROUND = pygame.transform.scale(pygame.image.load('images/background.png'), (WIDTH, HEIGHT))
PLAYER = pygame.transform.scale(pygame.image.load('images/chief.png'), (70, 70))
BULLET = pygame.transform.rotate(pygame.transform.scale(pygame.image.load('images/bullet.png'), (40, 40)), -90)
GRUNT = pygame.transform.scale(pygame.image.load('images/grunt.png'), (60, 60))
ELITE_SWORD = pygame.transform.scale(pygame.image.load('images/elite1.png'), (70, 70))
ELITE_GUN = pygame.transform.scale(pygame.image.load('images/elite2.png'), (70, 70))
RED_LASER = pygame.transform.rotate(pygame.transform.scale(pygame.image.load('images/red.png'), (10, 30)), 90)
BLUE_LASER = pygame.transform.rotate(pygame.transform.scale(pygame.image.load('images/blue.png'), (10, 30)), 90)
GREEN_LASER = pygame.transform.rotate(pygame.transform.scale(pygame.image.load('images/green.png'), (10, 30)), 90)
BACKGROUND_START = pygame.transform.scale(pygame.image.load('images/background_start.png'), (WIDTH, HEIGHT))
PAUSE_SCREEN = pygame.transform.scale(pygame.image.load('images/pause.png'), (WIDTH, HEIGHT))
GAME_OVER_SCREEN = pygame.transform.scale(pygame.image.load('images/game_over.png'), (WIDTH, HEIGHT))

# load sounds
pygame.mixer.init()
pygame.mixer.music.load('audio/bg1.mp3')
pygame.mixer.music.set_volume(0.2)
start_voice = pygame.mixer.Sound('audio/start.mp3')
start_voice.set_volume(0.7)
game_over_voice = pygame.mixer.Sound('audio/game_over.mp3')
game_over_voice.set_volume(0.7)
shot_voice = pygame.mixer.Sound('audio/shot.mp3')
shot_voice.set_volume(0.09)
impact_voice = pygame.mixer.Sound('audio/impact.mp3')
impact_voice.set_volume(0.3)
enemy_hit_noise = pygame.mixer.Sound('audio/enemy_hit.mp3')
enemy_hit_noise.set_volume(0.3)
level_up_noise = pygame.mixer.Sound('audio/level_up.mp3')
level_up_noise.set_volume(0.3)
player_hit_noise = pygame.mixer.Sound('audio/player_hit.mp3')
player_hit_noise.set_volume(0.3)
wall_reached_noise = pygame.mixer.Sound('audio/wall_reached.mp3')
wall_reached_noise.set_volume(0.3)
game_over_sound = pygame.mixer.Sound('audio/game_over_sound.mp3')
game_over_sound.set_volume(0.3)

pygame.mixer.music.play()

class Projectile:
    def __init__(self, x, y, image):
        self.x = x
        self.y = y
        self.image = image
        self.mask = pygame.mask.from_surface(self.image)

    def draw(self, window):
        window.blit(self.image, (self.x, self.y))

    def move(self, speed):
        self.x += speed

    def off_screen(self, width):
        return not (0 < self.x <= width)
    
    def collision(self, target):
        return collide(self, target)
    

def collide(object1, object2):
    gap_x = object2.x - object1.x
    gap_y = object2.y - object1.y
    return object1.mask.overlap(object2.mask, (gap_x, gap_y)) != None


class Charactor:
    COOLDOWN = 20
    def __init__(self, x, y, health:100):
        self.x = x
        self.y = y
        self.health = health
        self.image = None
        self.shot = None
        self.shots = []
        self.cooldown_time = 0

    def draw(self, window):
        window.blit(self.image, (self.x, self.y))
        for shot in self.shots:
            shot.draw(window)


    def move_shots(self, speed, target):
        self.cooldown()
        for shot in self.shots:
            shot.move(speed)
            if shot.off_screen(WIDTH):
                self.shots.remove(shot)
            elif shot.collision(target):
                target.health -= 10
                if target.health <= 0:
                    target.lives -=1
                    target.health = 100
                player_hit_noise.play()
                self.shots.remove(shot)

    def cooldown(self):
        if self.cooldown_time >= self.COOLDOWN:
            self.cooldown_time = 0
        elif self.cooldown_time > 0:
            self.cooldown_time += 1


    def shoot(self):
        if self.cooldown_time == 0:
            next_shot = Projectile(self.x, self.y, self.shot)
            self.shots.append(next_shot)
            self.cooldown_time = 1

class Player(Charactor):
    def __init__(self, x, y, health: 100):
        super().__init__(x, y, health)
        self.image = PLAYER
        self.shot = BULLET
        self.mask = pygame.mask.from_surface(self.image)
        self.max_health = health
        self.lives = 4


    def move_shots(self, speed, targets):
        self.cooldown()
        for shot in self.shots:
            shot.move(speed)
            if shot.off_screen(WIDTH):
                self.shots.remove(shot)
            else:
                for target in targets:
                    if shot.collision(target):
                        targets.remove(target)
                        self.shots.remove(shot)
                        enemy_hit_noise.play()

    def health_bar(self, window):
        pygame.draw.rect(window, (255,0,0),
                         (self.x, self.y + self.image.get_height() + 5, self.image.get_width(), 10))
        pygame.draw.rect(window, (0,255,0),
                         (self.x, self.y + self.image.get_height() + 5, (self.image.get_width()*self.health/self.max_health), 10))

    def draw(self, window):
        super().draw(window)
        self.health_bar(window)


class Enemy(Charactor):
    UNITS = {'grunt': (GRUNT, RED_LASER),
     'sword': (ELITE_SWORD, BLUE_LASER),
     'gunner': (ELITE_GUN, GREEN_LASER)
     }
    
    def __init__(self, x, y, unit, health: 100):
        super().__init__(x, y, health)
        self.image, self.shot = self.UNITS[unit]
        self.mask = pygame.mask.from_surface(self.image)

    def move(self, speed):
        self.x -= speed


def main_loop():
    framerate = 60
    timer = pygame.time.Clock()
    running = True
    level = 0
    #lives = 4
    main_text = pygame.font.SysFont('fonts/font.ttf', 40, True, False)
    player_speed = 5
    player = Player(100,600, health= 100)
    enemies = []
    enemy_speed = 1
    wave_size = 0
    projectile_speed = 7
    game_over = False
    total_enemies = []

    def score(score):
        score_text = main_text.render('SCORE: ' + str(score), True, (0,255,0))
        WINDOW.blit(score_text, [(WIDTH/2 - score_text.get_width()/2),230])

    
    def update_window():
        WINDOW.blit(BACKGROUND, (0, 0))
        lives_text = main_text.render(f'LIVES: {player.lives}', True, (0,255,0))
        level_text = main_text.render(f'LEVEL: {level}', True, (0,255,0))
        WINDOW.blit(lives_text,(10, 10))
        WINDOW.blit(level_text,(870, 10))
        player.draw(WINDOW) 
        for enemy in enemies:
            enemy.draw(WINDOW)

        pygame.display.update()

    def pause():
        paused = True
        pygame.mixer.music.pause()
        while paused:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.QUIT()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        paused = False
                        pygame.mixer.music.unpause()
                    elif event.key == pygame.K_r:
                        running = False
                        start_menu()
            WINDOW.blit(PAUSE_SCREEN, (0,0))
            pygame.display.update()
            timer.tick(5)

    def score_cal(level):
        a=0
        b=0
        for i in range(1,(level+1)):
            a += 5
            b += a
        final_score = b - (len(enemies))
        final_score = final_score*100
        return final_score

    def END():
        game_over = True
        pygame.mixer.music.pause()
        while game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        quit()
                    elif event.key == pygame.K_r:
                        running = False
                        pygame.mixer.music.play()
                        start_menu()
            WINDOW.blit(GAME_OVER_SCREEN, (0,0))
            score(score_cal(level))
            pygame.display.update()
            timer.tick(5)
    
    while running:
        timer.tick(framerate)
        update_window()

        if player.lives <= 0:
            game_over_voice.play()
            game_over_sound.play()
            END()

        if len(enemies) == 0:
            level+=1
            level_up_noise.play()
            wave_size +=5
            for i in range(wave_size):
                enemy = Enemy(random.randrange(WIDTH + 100, WIDTH + 1000), 
                              random.randrange(100, HEIGHT - 100), 
                              random.choice(['grunt', 'sword', 'gunner']), health= 100)
                enemies.append(enemy)
                total_enemies.append(1)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.QUIT()

        active_keys = pygame.key.get_pressed()
        if active_keys[pygame.K_a] and (player.x - player_speed) > 0:
            player.x -= player_speed
        if active_keys[pygame.K_d] and (player.x + player_speed + 73) < WIDTH:
            player.x += player_speed
        if active_keys[pygame.K_w] and (player.y - player_speed) > 0:
            player.y -= player_speed
        if active_keys[pygame.K_s] and (player.y + player_speed + 80) < HEIGHT:
            player.y += player_speed
        if active_keys[pygame.K_SPACE]:
            player.shoot()
            shot_voice.play()
        if active_keys[pygame.K_1]:
            pygame.mixer.music.load('audio/bg1.mp3')
            pygame.mixer.music.play()
        if active_keys[pygame.K_2]:
            pygame.mixer.music.load('audio/bg2.mp3')
            pygame.mixer.music.play()
        if active_keys[pygame.K_3]:
            pygame.mixer.music.load('audio/bg3.mp3')
            pygame.mixer.music.play()
        if active_keys[pygame.K_4]:
            pygame.mixer.music.load('audio/bg4.mp3')
            pygame.mixer.music.play()
        if active_keys[pygame.K_5]:
            pygame.mixer.music.load('audio/bg5.mp3')
            pygame.mixer.music.play()
        if active_keys[pygame.K_6]:
            pygame.mixer.music.load('audio/bg6.mp3')
            pygame.mixer.music.play()
        if active_keys[pygame.K_7]:
            pygame.mixer.music.load('audio/bg7.mp3')
            pygame.mixer.music.play()
        if active_keys[pygame.K_8]:
            pygame.mixer.music.load('audio/bg8.mp3')
            pygame.mixer.music.play()
        if active_keys[pygame.K_9]:
            pygame.mixer.music.load('audio/bg9.mp3')
            pygame.mixer.music.play()
        if active_keys[pygame.K_ESCAPE]:
            pause()     

        for enemy in enemies:
            enemy.move(enemy_speed)
            enemy.move_shots(-projectile_speed, player)
            if random.randrange(0, 180) == 1:
                enemy.shoot()
            if collide(enemy, player):
                player.health -= 10
                if player.health <= 0:
                    player.lives -=1
                    player.health = 100 
                enemies.remove(enemy)
                impact_voice.play()
            elif enemy.x <= 0:
                player.lives -= 1
                enemies.remove(enemy)
                wall_reached_noise.play()
        player.move_shots(projectile_speed, enemies)
    pygame.quit()                 

def start_menu():
    running = True
    while running:
        WINDOW.blit(BACKGROUND_START, (0,0))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                start_voice.play()
                main_loop()
        
    pygame.quit()

start_menu()