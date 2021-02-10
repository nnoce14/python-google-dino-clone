import os
import random
import pygame

pygame.font.init()

WIN_WIDTH = 600
WIN_HEIGHT = 300

SPEED_MODIFIER = 1

DINO_IMGS = [pygame.image.load(os.path.join("dinoAssets", "trex1.png")),
             pygame.image.load(os.path.join("dinoAssets", "trex2.png")),
             pygame.image.load(os.path.join("dinoAssets", "trex3.png"))]
BASE_IMG = pygame.image.load(os.path.join("dinoAssets", "base.png"))
CACTUS_IMGS = [pygame.image.load(os.path.join("dinoAssets", "cactus-1.png")),
               pygame.image.load(os.path.join("dinoAssets", "cactus-2.png")),
               pygame.image.load(os.path.join("dinoAssets", "cactus-3.png"))]

STAT_FONT = pygame.font.SysFont("Arial", 30)

GO_FONT = pygame.font.SysFont("Arial", 50)


class Dino:
    IMGS = DINO_IMGS
    ANIMATION_TIME = 5

    def __init__(self, y):
        self.x = 60
        self.y = y
        self.tick_count = 0
        self.vel = 6
        self.isJump = False
        self.height = self.y
        self.index = 0
        self.img = self.IMGS[0]
        self.ANIMATION_TIME = 3
        self.jump_count = 10
        # self.dead_img = pygame.image.load(os.path.join("dinoAssets", "dino-dead.png"))

    def jump(self):
        self.isJump = True

    def update(self, base):
        if self.isJump:
            if self.vel <= 0:
                force = (0.5 * (self.vel * self.vel))
            else:
                force = -(0.5 * (self.vel * self.vel))

            self.y += force
            self.vel -= 0.5

            if self.y >= base.y:
                self.y = 208
                self.vel = 6
                self.isJump = False


    def draw(self, win):
        self.index += 1

        if self.index < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.index < self.ANIMATION_TIME * 2:
            self.img = self.IMGS[1]
        elif self.index < self.ANIMATION_TIME * 3:
            self.img = self.IMGS[2]
        elif self.index < self.ANIMATION_TIME * 4:
            self.img = self.IMGS[1]
        elif self.index == self.ANIMATION_TIME * 4 + 1:
            self.img = self.IMGS[0]
            self.index = 0

        win.blit(self.img, (self.x, self.y))

    def get_mask(self):
        return pygame.mask.from_surface(self.img)


class Base:
    VEL = 5
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        self.x1 -= self.VEL * SPEED_MODIFIER
        self.x2 -= self.VEL * SPEED_MODIFIER

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))


class Cactus:
    VEL = 5

    def __init__(self, x):
        self.img = CACTUS_IMGS[self.pick_img()]
        self.passed = False
        self.x = x
        self.y = 210 + DINO_IMGS[0].get_height() - self.img.get_height()
        self.height = 0

    def pick_img(self):
        rand = random.randint(1, len(CACTUS_IMGS))
        return rand - 1

    def move(self):
        self.x -= self.VEL * SPEED_MODIFIER

    def draw(self, win):
        win.blit(self.img, (self.x, self.y))

    def collide(self, dino):
        dino_mask = dino.get_mask()
        cactus_mask = pygame.mask.from_surface(self.img)

        offset = (round(self.x - dino.x), round(self.y - dino.y))

        point = dino_mask.overlap(cactus_mask, offset)

        if point:
            return True

        return False


def draw_window(win, dino, base, cacti, score):
    win.fill((255, 255,  255))

    base.draw(win)

    for cactus in cacti:
        cactus.draw(win)

    text = STAT_FONT.render("Score: " + str(score), 1, (55, 55, 55))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))

    dino.draw(win)

    pygame.display.update()


def main():
    global SPEED_MODIFIER

    score = 0
    count = 0

    base = Base(200 + DINO_IMGS[0].get_height())

    cacti = [Cactus((random.randint(400, 550)))]

    d = Dino(208)

    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()

    run = True
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                d.jump()

        add_cactus = False
        rem = []
        for cactus in cacti:
            if cactus.collide(d):
                run = False

            if not cactus.passed and d.x > cactus.x + cactus.img.get_width():
                cactus.passed = True
                score += 10

            if cactus.x < 250 and len(cacti) < 2:
                add_cactus = True

            if cactus.x + cactus.img.get_width() < 0:
                rem.append(cactus)

            cactus.move()

        if add_cactus:
            cacti.append(Cactus(random.randint(650, 850)))

        for r in rem:
            cacti.remove(r)

        if count % 60 == 0:
            SPEED_MODIFIER += 0.1


        base.move()
        d.update(base)

        score += 1
        count += 1

        draw_window(win, d, base, cacti, score)

    while True:
        clock.tick(15)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
        win.blit(d.IMGS[0], (d.x, d.y))
        win.blit(base.IMG, (base.x1, base.y))
        for cactus in cacti:
            win.blit(cactus.img, (cactus.x, cactus.y))
        pygame.display.update()

        game_over_text = GO_FONT.render("Game Over", 1, (55, 55, 55))
        win.blit(game_over_text, (WIN_WIDTH / 2 - 105, WIN_HEIGHT / 2 - 50))


main()
# pygame.quit()
