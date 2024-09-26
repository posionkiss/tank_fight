import copy
import random

import pygame

from utils import *


def init_wall(wallList):
    for i in range(21):
        for j in range(11):
            if random.random() > 0.8 or i == 0 or i == 20 or j == 0 or j == 10:
                wall = Wall(i, j, canvas)
                wallList.add(wall)

    return wallList


def start_game(player0Score, player1Score, round, gameRound):
    if round > gameRound:
        return player0Score, player1Score
    clock = pygame.time.Clock()
    # pygame.key.set_repeat(5, 60)
    canvas.fill((0, 0, 0))  # 背景为黑色
    wallList = Group()
    wallList = init_wall(wallList)
    tank0 = Tank('source/tank_body0.png',  # 坦克源文件
                 canvas,  # 画布
                 random.randint(0, 599),  # 随机初始坐标
                 random.randint(0, 599),
                 4,  # 速度
                 wallList, 0)  # 所属的坦克对象
    tank1 = Tank('source/tank_body1.png',
                 canvas,
                 random.randint(0, 599),
                 random.randint(0, 599),
                 4,
                 wallList, 1)
    tankGroup = TankGroup()  # 坦克对象组
    tankGroup.add(tank0)
    tankGroup.add(tank1)

    # 玩家0和1 的炮弹设置：初始为普通炮弹，最多4发，速度为4
    # bulletGroup = pygame.sprite.Group()
    interval = 100  # 炮弹发射的最短间隙
    maxBulletNum = 4
    bulletGroup = BulletGroup(maxBulletNum, interval=interval)
    maxDistance = 300
    speed = 4.5
    for i in range(maxBulletNum):
        bulletGroup.add(
            Bullet('source/bullet0.png',
                   canvas,
                   speed,
                   tank0,
                   wallList,
                   tankGroup,
                   i * interval,
                   maxDistance, interval))
    for i in range(maxBulletNum):
        bulletGroup.add(
            Bullet('source/bullet1.png',
                   canvas,
                   speed,
                   tank1,
                   wallList,
                   tankGroup,
                   i * interval,
                   maxDistance, interval))
    tank0.init_bullet(bulletGroup)
    tank1.init_bullet(bulletGroup)
    tankGroup.init_bullet(bulletGroup)

    kamui = Kamui(canvas, wallList, tankGroup)
    bulletAcc = BulletAcc(canvas, wallList, tankGroup)
    exit = False
    while not exit:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit = True
        canvas.fill((0, 0, 0))
        wallList.update()
        res = tankGroup.update()
        kamui.update()
        bulletAcc.update()
        player0ScoreText.blit(canvas)
        player1ScoreText.blit(canvas)
        pygame.display.update(bg.get_rect())
        clock.tick(30)
        if res[0]:
            player0ScoreText.update_text(f'玩家0 分数：{player0Score + 1}')
            player0Score, player1Score = start_game(player0Score + 1, player1Score, round + 1, gameRound)
            exit = True
        elif res[1]:
            player1ScoreText.update_text(f'玩家1 分数：{player1Score + 1}')
            player0Score, player1Score = start_game(player0Score, player1Score + 1, round + 1, gameRound)
            exit = True
    return player0Score, player1Score


win_size = (900, 1050)

pygame.init()

# 画布设置
canvas = pygame.display.set_mode(win_size, pygame.RESIZABLE)
pygame.display.set_caption('Board')

# 背景加载
bg = pygame.image.load('source/background.png')
canvas.blit(bg, dest=(0, 0))
mask = pygame.image.load('source/background.png')
mask = mask.convert_alpha(mask)

# 字体加载
font1 = pygame.font.Font('source/STXINWEI.TTF', 25)  # 小字字体
font2 = pygame.font.Font('source/STHUPO.TTF', 50)  # 标题字体

# 文本加载
title = Text('坦克大战', 'source/STHUPO.TTF', 50,
             (200, 200, 200),
             (0, 0, 0),
             (win_size[0] / 2, win_size[1] / 2 - 150))
title.blit(canvas)

start = Text('开始游戏', 'source/STXINWEI.TTF', 25,
             (200, 200, 200),
             (0, 0, 0),
             (win_size[0] / 2, win_size[1] / 2 + 150))
start.blit(canvas)
player0ScoreText = Text('玩家0 分数：0', 'source/STXINWEI.TTF', 20,
                        (200, 200, 200),
                        (0, 0, 0),
                        (win_size[0] / 2 - 100, win_size[1] - 75))
player1ScoreText = Text('玩家1 分数：0', 'source/STXINWEI.TTF', 20,
                        (200, 200, 200),
                        (0, 0, 0),
                        (win_size[0] / 2 + 100, win_size[1] - 75))
player0WinText = Text('玩家1 胜利！', 'source/STXINWEI.TTF', 60,
                      (200, 200, 200),
                      (0, 0, 0),
                      (win_size[0] / 2, win_size[1] / 2))
player1WinText = Text('玩家1 胜利！', 'source/STXINWEI.TTF', 60,
                      (200, 200, 200),
                      (0, 0, 0),
                      (win_size[0] / 2, win_size[1] / 2))
gameRound = 7
exit = False

while not exit:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit = True
        sign = click(event, start)
        if sign:
            player0Score, player1Score = start_game(0, 0, 1, gameRound)  # 游戏中
            canvas.blit(mask, dest=(0, 0))
            if player0Score > player1Score:
                player0WinText.blit(canvas)
            else:
                player1WinText.blit(canvas)
            break
    pygame.display.update(bg.get_rect())
