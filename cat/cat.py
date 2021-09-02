import pygame
from glob import glob
import sys
import os
import time


pygame.init()
screen = pygame.display.set_mode((400, 600))
main_dir = os.path.split(os.path.abspath(__file__))[0]

class Cat:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.list = [
            pygame.image.load(f).convert_alpha() for f in glob(os.path.join(main_dir, "cat/Walk*.png"))[1:]
        ]
        self.list_idle = [pygame.image.load(f).convert_alpha() for f in glob(os.path.join(main_dir,"cat/Idle*.png"))[1:]]
        self.counter = 0
        self.image = self.list[0]
        self.dir = ""
        self.prov = ""

    def update(self):
        self.counter += .1
        if self.counter >= len(self.list):
            self.counter = 0
        if self.dir == "right":
            self.image = self.list[int(self.counter)]
            self.prov = self.dir
        if self.dir == "left":
            self.image = pygame.transform.flip(self.list[int(self.counter)], True, False)
            self.prov = self.dir
        if self.dir == "":
            if self.counter >= len(self.list_idle):
                self.counter = 0
            if self.prov == "right":
                self.image = self.list_idle[int(self.counter)]
            else:
                self.image = pygame.transform.flip(self.list_idle[int(self.counter)], True, False)

        screen.blit(self.image, (self.x, self.y))

cat = Cat(100, 100)
clock = pygame.time.Clock()

time_end = time.time() + 10

while True:
    if (time.time() < time_end):
        screen.fill((128, 255, 128))

        if cat.dir != "":
            if cat.dir == "right":
                cat.x += 1
            if cat.dir == "left":
                cat.x -= 1

        if pygame.event.get(pygame.QUIT):
            break
        # for event in pygame.event.get():
        #     if event.type == pygame.KEYDOWN:
        #         if event.key == pygame.K_ESCAPE:
        #             pygame.quit()
        #         if event.key == pygame.K_RIGHT:
        #             cat.dir = "right"
        #         if event.key == pygame.K_LEFT:
        #             cat.dir = "left"
        #     if event.type == pygame.KEYUP:
        #         cat.dir = ""
        cat.dir = ""


        cat.update()

        pygame.display.update()
        clock.tick(180)
    else:
        screen.fill((128, 255, 128))

        if cat.dir != "":
            if cat.dir == "right":
                cat.x += 1
            if cat.dir == "left":
                cat.x -= 1

        if pygame.event.get(pygame.QUIT):
            break
        # for event in pygame.event.get():
        #     if event.type == pygame.KEYDOWN:
        #         if event.key == pygame.K_ESCAPE:
        #             pygame.quit()
        #         if event.key == pygame.K_RIGHT:
        #             cat.dir = "right"
        #         if event.key == pygame.K_LEFT:
        #             cat.dir = "left"
        #     if event.type == pygame.KEYUP:
        #         cat.dir = ""
        cat.dir = "right"


        cat.update()

        pygame.display.update()
        clock.tick(180)

pygame.quit()