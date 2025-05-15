import pygame as pg
import random

pg.init()
W, H = 480, 640
display = pg.display.set_mode((W, H))

GRAVITY = 1
JUMP = -30
PLATFORM_WIDTH = 105
MIN_GAP = 90
MAX_GAP = 180
score = 0
font_name = pg.font.match_font('Comic Sans', True, False)
font = pg.font.Font(font_name, 36)

def draw_text(text: str, x, y):
    score_text = font.render(text, True, (0, 0, 0))
    display.blit(score_text, (x, y))


class Sprite(pg.sprite.Sprite):
    def __init__(self, x, y, image_path):
        super().__init__()
        self.image = pg.image.load(image_path)
        self.rect = self.image.get_rect(center=(x, y))
        self.dead = False
    
    def update(self):
        super().update()
        
    def draw(self):
        display.blit(self.image, self.rect)
        
    def kill(self):
        self.dead = True
        super().kill()

class Player(Sprite):
    def __init__(self):
        super().__init__(W // 2, H // 2, 'img/doodle_left.png')
        self.image_left = self.image
        self.image_right = pg.transform.flip(self.image, True, False)
        self.speed = 0


    def update(self):
        if self.dead:
            return
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT]:
            self.rect.x -= 5
            self.image = self.image_left
        if keys[pg.K_RIGHT]:
            self.rect.x += 5
            self.image = self.image_right

        if self.rect.left > W:
            self.rect.left = 0
        if self.rect.right < 0:
            self.rect.right = W
        self.speed += GRAVITY
        self.rect.y += self.speed

    def draw(self):
        if self.dead:
            self.rect.y = H // 2
        else:
            display.blit(self.image, self.rect)

class BaseBonus(Sprite):
    def __init__(self, image_path, plat: 'BasePlatform'):
        img = pg.image.load(image_path)
        w = img.get_width()
        h = img.get_height()
        rect = plat.rect
        x = random.randint(rect.left + w // 2, rect.right - w // 2)
        y = rect.top - h // 2
        super().__init__(x, y, image_path)
        self.platform = plat
        self.dx = self.rect.x - self.platform.rect.x

    def on_collision(self, player):
        global score
        score += 1000
        self.kill()

    def update(self):
        self.rect.x = self.platform.rect.x + self.dx
        if self.platform.dead:
            self.kill()

class Spring(BaseBonus):
    def __init__(self, plat):
        super().__init__('img/spring.png', plat)

    def on_collision(self, player):
        player.speed = -50
        self.image = pg.image.load('img/spring_1.png')

class Hat(BaseBonus):
    def __init__(self, plat: 'BasePlatform'):
        super().__init__('img/hat_0.png', plat)
        self.image_left = pg.image.load("img/hat_left.png")
        self.image_right = pg.transform.flip(self.image_left, True, False)
        
    def update(self):
        super().update()
        
    def on_collision(self, player: Player):
        super().on_collision(player)

class Jetpack(BaseBonus):
    def __init__(self, plat: 'BasePlatform'):
        super().__init__('img/jetpack_0.png', plat)
        self.image_right = pg.transform.flip(self.image, True, False)
        self.image_left = self.image
        
    def on_collision(self, player: Player):
        super().on_collision(player)

class BasePlatform(Sprite):
    def on_collision(self, player):
        player.speed = JUMP

    def update(self):
        if self.rect.top > H:
            self.kill()

    def attach_bonus(self):
        if random.randint(0, 100) > 50:
            Bonus = random.choice([Spring, Hat, Jetpack])
            obj = Bonus(self)
            platforms.add(obj)

class NormalPlatform(BasePlatform):
    def __init__(self, x, y):
        super().__init__(x, y, 'img/green.png')

class SpringPlatform(BasePlatform):
    def __init__(self, x, y):
        super().__init__(x, y, 'img/purple.png')

    def on_collision(self, player):
        player.speed = 1.3 * JUMP

class BreakablePlatform(BasePlatform):
    def __init__(self, x, y):
        super().__init__(x, y, 'img/red.png')

    def on_collision(self, player):
        player.speed = JUMP
        self.kill()

class MovingPlatform(BasePlatform):
    def __init__(self, x, y):
        super().__init__(x, y, 'img/blue.png')
        self.direction = random.choice([-1, 1])
        self.speed = 3

    def update(self):
        super().update()
        self.rect.x += self.speed * self.direction
        if self.rect.right > W or self.rect.left < 0:
            self.direction *= -1

platforms = pg.sprite.Group()

def spawn_platform():
    platform = platforms.sprites()[-1]
    y = platform.rect.y - random.randint(MIN_GAP, MAX_GAP)
    x = random.randint(0, W - PLATFORM_WIDTH)
    types = [
        MovingPlatform, BreakablePlatform, SpringPlatform,
        NormalPlatform
    ]
    Plat = random.choice(types)
    platform = Plat(x, y)
    platform.attach_bonus()
    platforms.add(platform)

def is_top_collision(player: Player, platform: BasePlatform):
    if player.rect.colliderect(platform.rect):
        if player.speed > 0:
            if player.rect.bottom < platform.rect.bottom:
                platform.on_collision(player)

platform = NormalPlatform(W // 2 - PLATFORM_WIDTH // 2, H - 50)
platforms.add(platform)

doodle = Player()

def main():
    while True:
        #1
        for e in pg.event.get():
            if e.type == pg.QUIT:
                return
        #2
        doodle.update()
        platforms.update()
        if len(platforms) < 25:
            spawn_platform()
        pg.sprite.spritecollide(doodle, platforms, False, collided=is_top_collision)
        if doodle.speed < 0 and doodle.rect.bottom < H / 2:
            doodle.rect.y -= doodle.speed
            global score
            score += 1
            for platform in platforms:
                platform.rect.y -= doodle.speed
        #3
        display.fill('white')
        platforms.draw(display)
        doodle.draw()
        pg.display.update()
        pg.time.delay(1000 // 60)

if __name__ == '__main__':
    main()
