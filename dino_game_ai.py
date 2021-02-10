import os
import random
import neat
import pygame

pygame.font.init()

WIN_WIDTH = 600
WIN_HEIGHT = 300

SPEED_MODIFIER = 1
GEN = -1

DINO_IMGS = [pygame.image.load(os.path.join("dinoAssets", "trex1.png")),
             pygame.image.load(os.path.join("dinoAssets", "trex2.png")),
             pygame.image.load(os.path.join("dinoAssets", "trex3.png"))]
BASE_IMG = pygame.image.load(os.path.join("dinoAssets", "base.png"))
CACTUS_IMGS = [pygame.image.load(os.path.join("dinoAssets", "cactus-1.png")),
               pygame.image.load(os.path.join("dinoAssets", "cactus-2.png")),
               pygame.image.load(os.path.join("dinoAssets", "cactus-3.png"))]
# pygame.image.load(os.path.join("dinoAssets", "cactus-4.png"))]


STAT_FONT = pygame.font.SysFont("Arial", 25, 2)
LEFT_FONT = pygame.font.SysFont("Arial", 20, 1)


class Dino:
    IMGS = DINO_IMGS
    ANIMATION_TIME = 5

    def __init__(self):
        self.x = 60
        self.y = 210
        self.tick_count = 0
        self.vel = 7.25
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

            if SPEED_MODIFIER < 2.5:
                self.y += force * (SPEED_MODIFIER / 2)
                self.vel -= (0.5 + (SPEED_MODIFIER / 20))
            else:
                self.y += force
                self.vel -= (0.5 + (SPEED_MODIFIER / 20))

            if self.y >= base.y:
                self.y = 208
                self.vel = 7.25
                self.isJump = False

    def move(self):
        self.tick_count += 1

        d = self.vel * self.tick_count + 1.5 * self.tick_count ** 2

        if d >= 16:
            d = 16

        if d < 0:
            d -= 2

        self.y = self.y + d

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


def draw_window(win, dinos, base, cacti, score, gen, alive):
    win.fill((255, 255, 255))

    base.draw(win)

    for cactus in cacti:
        cactus.draw(win)

    text = STAT_FONT.render("Score: " + str(score), 1, (55, 55, 55))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))

    text2 = LEFT_FONT.render("Gen: " + str(gen), 1, (55, 55, 55))
    win.blit(text2, (10, 10))

    text3 = LEFT_FONT.render("Alive: " + str(alive), 1, (55, 55, 55))
    win.blit(text3, (10, 40))

    for dino in dinos:
        dino.draw(win)

    pygame.display.update()


def main(genomes, config):
    global SPEED_MODIFIER
    global GEN
    GEN += 1

    score = 0
    count = 0

    nets = []
    ge = []
    dinos = []

    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        dinos.append(Dino())
        g.fitness = 0
        ge.append(g)

    base = Base(200 + DINO_IMGS[0].get_height())
    cacti = [Cactus(500)]

    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()

    run = True
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        cactus_ind = 0
        if len(dinos) > 0:
            if len(cacti) > 1 and dinos[0].x > cacti[0].x + cacti[0].img.get_width():
                cactus_ind = 1
        else:
            SPEED_MODIFIER = 1
            run = False

        for x, dino in enumerate(dinos):
            ge[x].fitness += 0.05

            output = nets[x].activate((dino.x, abs(dino.x - cacti[cactus_ind].x), abs(dino.y - cacti[cactus_ind].y), cacti[cactus_ind].img.get_width()))

            if output[0] > 0.5:
                dino.jump()

        add_cactus = False
        rem = []
        for cactus in cacti:
            for x, dino in enumerate(dinos):
                if cactus.collide(dino):
                    ge[x].fitness -= 1
                    dinos.pop(x)
                    nets.pop(x)
                    ge.pop(x)

                if not cactus.passed and dino.x + dino.img.get_width() > cactus.x + cactus.img.get_width():
                    cactus.passed = True
                    score += 10

                if cactus.x + cactus.img.get_width() < 0 and len(cacti) < 3:
                    add_cactus = True

                if cactus.x + cactus.img.get_width() < 0:
                    rem.append(cactus)

            cactus.move()

        if add_cactus:
            for g in ge:
                g.fitness += 1.25
            cacti.append(Cactus(random.randint(600, 850)))
            if len(cacti) == 2:
                cacti.pop(0)

        '''if len(cacti) > 3 and len(rem) > 5:
            for r in rem:
                if r.x + r.img.get_width() < 0:
                    cacti.remove(r)
        '''

        if count % 30 == 0:
            SPEED_MODIFIER += 0.1

        base.move()
        for dino in dinos:
            dino.update(base)

        score += 1
        count += 1
        draw_window(win, dinos, base, cacti, score, GEN, len(dinos))


def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_path)

    p = neat.Population(config)

    # adds optional statistics to console
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(main, 50)


if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run(config_path)
