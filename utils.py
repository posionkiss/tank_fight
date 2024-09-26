import math
import random
import time

import pygame


# from main import canvas


# font1 = pygame.font.Font('source/STXINWEI.TTF', 25)  # 小字字体
# font2 = pygame.font.Font('source/STHUPO.TTF', 50)  # 标题字体
# title = font2.render('坦克大战', True, (127, 127, 127), (255, 255, 255))
# titleRect = title.get_rect()
# titleRect.center = (300, 200)
# canvas.blit(title, titleRect)
class Text:
    def __init__(self, content, fontName, size, textColor, filtColor, pos):
        self.font = pygame.font.Font(fontName, size)
        self.text = self.font.render(content, True, textColor, filtColor)
        self.textRect = self.text.get_rect()
        self.pos = pos
        self.textRect.center = pos
        self.textColor = textColor
        self.filtColor = filtColor

    def blit(self, canvas):
        canvas.blit(self.text, self.textRect)

    def update_text(self, content):
        self.text = self.font.render(content, True, self.textColor, self.filtColor)
        self.textRect = self.text.get_rect(center=self.pos)


class Tool(pygame.sprite.Sprite):  # 场景内的小道具，定时出现，一段时间后消失
    def __init__(self, path, canvas, wallList, tankGroup, interval=50, holdOnTime=200):
        super(Tool, self).__init__()
        self.image = pygame.image.load(path)
        self.rect = self.image.get_rect()
        initX, initY = random.randint(0, 600), random.randint(0, 600)
        self.rect.center = (
            initX + int(self.image.get_size()[0] / 2), initY + int(self.image.get_size()[1] / 2))
        self.wallList = wallList
        self.tankGroup = tankGroup
        self.reset_pos()
        self.visible = False
        self.intervalMean = interval
        self.holdOnTimeMean = holdOnTime
        self.reset()
        self.canvas = canvas

    def reset_pos(self):
        self.initX = int(random.random() * 600)
        self.initY = int(random.random() * 600)
        self.rect.center = (
            int(self.initX + self.image.get_size()[0] / 2), int(self.initY + self.image.get_size()[1] / 2))
        while self.check_collide():
            self.initX = random.random() * 600
            self.initY = random.random() * 600
            self.rect.center = (
                int(self.initX + self.image.get_size()[0] / 2), int(self.initY + self.image.get_size()[1] / 2))

    def reset(self):
        # self.clock1 = pygame.time.get_ticks()
        self.interval = self.intervalMean + random.randint(-50, 50)
        self.holdOnTime = self.holdOnTimeMean + random.randint(-20, 20)
        self.reset_pos()

    def check_collide(self):
        for wall in self.wallList.objList:
            if pygame.sprite.collide_mask(self, wall):
                return True
        return False

    def check_tank_collide(self):
        for tank in self.tankGroup:
            if pygame.sprite.collide_mask(self, tank):
                self.reset()
                return True, tank
        return False, None

    def update(self):
        if self.interval <= 0:
            if self.holdOnTime > 0:
                self.canvas.blit(self.image, self.rect)
                self.check_tank_collide()
                self.holdOnTime -= 1
            else:
                self.reset()
        else:
            self.interval -= 1


class Tank(pygame.sprite.Sprite):
    def __init__(self, imgPath, canvas, initX, initY, speed, wallList, player):
        super(Tank, self).__init__()
        self.image = pygame.image.load(imgPath)
        # alphaImage = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
        # alphaImage.fill((0, 0, 0, 100))
        self.oriImage = self.image
        self.rect = self.image.get_rect()
        self.initX = initX
        self.initY = initY
        self.rect.center = (
            self.initX + int(self.oriImage.get_size()[0] / 2), self.initY + int(self.oriImage.get_size()[1] / 2))
        while self.check_collide(wallList):
            self.initX = random.random() * 600
            self.initY = random.random() * 600
            self.rect.center = (
                int(self.initX + self.oriImage.get_size()[0] / 2), int(self.initY + self.oriImage.get_size()[1] / 2))

        self.rotAngle = 0
        self.canvas = canvas
        self.speed = speed
        self.gun = Gun(f'source/gun{player}.png', canvas, initX, initY - 7, self.rect.center, self.speed, player)
        self.dir = 1
        self.wallList = wallList
        self.player = player

        self.kamui = False  # 道具一特殊效果所需的变量
        self.alpha = 200
        self.alphaDir = -15
        self.kamuiSign = False
        self.kamuiClock0 = None
        self.kamuiClock1 = None
        self.kamuiHoldOnTime = 2000

        self.bulletAcc = False
        self.bulletAccSign = False
        self.bulletAccHoldOnTime = 2000

    def init_bullet(self, bulletGroup):
        self.bulletGroup = bulletGroup

    def update(self):
        if self.check_bullet_collide():
            return True
        pressed = pygame.key.get_pressed()
        self.gun.locked = False
        if not self.player and pressed[pygame.K_UP] or self.player and pressed[pygame.K_w]:
            self.dir = 1
            self.forward_backward(self.dir)
        elif not self.player and pressed[pygame.K_DOWN] or self.player and pressed[pygame.K_s]:
            self.dir = -1
            self.forward_backward(self.dir)
        if not self.player and pressed[pygame.K_LEFT] or self.player and pressed[pygame.K_a]:
            self.rotate(0) if pressed[pygame.K_DOWN] else self.rotate(1)
        elif not self.player and pressed[pygame.K_RIGHT] or self.player and pressed[pygame.K_d]:
            self.rotate(1) if pressed[pygame.K_DOWN] else self.rotate(0)
        self.canvas.blit(self.image, self.rect)
        self.gun.update(self.rect.center)
        return False

    def rotate(self, dir):
        self.rotAngle += 5 if dir else -5
        image = pygame.transform.rotate(self.oriImage, self.rotAngle)
        self.rect = image.get_rect(center=self.rect.center)
        self.gun.rotAngle = self.rotAngle
        if self.check_collide(self.wallList):
            self.rect = self.image.get_rect(center=self.rect.center)
            self.gun.locked = True
            self.rotAngle -= 5 if dir else -5
            return
        self.image = image
        self.rect = self.image.get_rect(center=self.rect.center)

    def forward_backward(self, dir, sign=1):
        assert dir == 1 or dir == -1
        centerX = self.rect.center[0]
        centerY = self.rect.center[1]
        c = self.rect.center
        self.gun.rotAngle = self.rotAngle
        if self.rotAngle == 0:
            center = (centerX, centerY - self.speed * dir)
        else:
            center = (centerX - math.sin(math.pi / (180 / self.rotAngle)) * self.speed * dir * sign,
                      centerY - math.cos(math.pi / (180 / self.rotAngle)) * self.speed * dir * sign)
        self.rect.center = center
        if self.check_collide(wallList=self.wallList):
            self.gun.locked = True
            self.rect.center = c

    def check_collide(self, wallList):
        for wall in wallList.objList:
            if pygame.sprite.collide_mask(self, wall):
                return True
        return False

    def check_bullet_collide(self):
        if self.kamuiSign:
            self.update_alpha()
            self.kamuiClock1 = pygame.time.get_ticks()
            if self.kamuiClock1 - self.kamuiClock0 >= self.kamuiHoldOnTime:
                self.disable_kamui()
        for bullet in self.bulletGroup.updateList:
            if pygame.sprite.collide_mask(self, bullet) and bullet.sign == 0:
                if self.kamui:
                    if not self.kamuiSign:
                        self.kamuiClock0 = pygame.time.get_ticks()
                    self.kamuiSign = True
                    return False
                return True
        return False

    def update_alpha(self):
        if self.alpha >= 220 or self.alpha <= 50:
            self.alphaDir *= -1
        self.alpha += self.alphaDir
        self.image.set_alpha(self.alpha)
        self.oriImage.set_alpha(self.alpha)
        self.gun.image.set_alpha(self.alpha)
        self.gun.oriImage.set_alpha(self.alpha)

    def enable_kamui(self):
        self.kamui = True

    def disable_kamui(self):
        self.kamui = False
        self.kamuiSign = False
        self.image.set_alpha(255)
        self.oriImage.set_alpha(255)
        self.gun.image.set_alpha(255)
        self.gun.oriImage.set_alpha(255)
        self.alpha = 200
        self.alphaDir = -1
        self.kamuiClock0 = None
        self.kamuiClock1 = None

    def enable_bullet_acc(self):
        self.bulletAcc = True
        self.update_bullet_speed(3, 1)

    def disable_bullet_acc(self):
        self.bulletAcc = False
        self.bulletAccSign = False
        self.update_bullet_speed(3, 0)

    def update_bullet_speed(self, coeff, enable):
        ind = 4 if self.player else 0
        for i in range(4):
            self.bulletGroup.objList[ind].speed *= coeff if enable else 1/coeff
            ind += 1


class BulletAcc(Tool):
    def __init__(self, canvas, wallList, tankGroup, path='source/bullet_acc.png', effectiveTime=10000):
        super(BulletAcc, self).__init__(path, canvas, wallList, tankGroup)
        self.clock0 = None
        self.clock1 = None
        self.effectiveTime = effectiveTime
        self.updateTank = None

    def update(self):
        if self.interval <= 0 and self.updateTank is None:
            if self.holdOnTime > 0:
                self.canvas.blit(self.image, self.rect)
                sign, tank = self.check_tank_collide()
                if sign:
                    tank.enable_bullet_acc()
                    self.clock0 = pygame.time.get_ticks()
                    self.updateTank = tank
                    return
                self.holdOnTime -= 1
            else:
                self.reset()
        elif self.updateTank is not None:
            self.clock1 = pygame.time.get_ticks()
            if self.clock1 - self.clock0 >= self.effectiveTime:
                if not self.updateTank.bulletAccSign:
                    self.updateTank.disable_bullet_acc()
                    self.reset()
                elif not self.updateTank.kamui:
                    self.reset()
        else:
            self.interval -= 1

    def reset(self):
        self.interval = self.intervalMean + random.randint(-50, 50)
        self.holdOnTime = self.holdOnTimeMean + random.randint(-20, 20)
        self.reset_pos()
        self.updateTank = None


class Gun(pygame.sprite.Sprite):
    def __init__(self, imgPath, canvas, initX, initY, tankcenter, speed, player):
        super(Gun, self).__init__()
        self.image = pygame.image.load(imgPath).convert_alpha()
        self.oriImage = self.image
        self.rect = self.image.get_rect()
        self.initX = initX
        self.initY = initY
        self.rect.center = (
            self.initX + int(self.oriImage.get_size()[0] / 2),
            self.initY + int(self.oriImage.get_size()[1] / 2) - 5)
        self.rotAngle = 0
        self.canvas = canvas
        self.bias = 7
        if self.rotAngle == 0:  # 调整枪管的位置
            self.rect.center = (tankcenter[0], tankcenter[1] - self.bias)
        else:
            self.rect.center = (tankcenter[0] - math.sin(math.pi / (180 / self.rotAngle)) * self.bias,
                                tankcenter[1] - math.cos(math.pi / (180 / self.rotAngle)) * self.bias)
        self.speed = speed
        self.locked = False
        self.dir = 1
        self.player = player

    def update(self, tankcenter):
        pressed = pygame.key.get_pressed()
        if not self.player and pressed[pygame.K_UP] or self.player and pressed[pygame.K_w]:
            self.dir = 1
            self.forward_backward(self.dir)
        elif not self.player and pressed[pygame.K_DOWN] or self.player and pressed[pygame.K_s]:
            self.dir = -1
            self.forward_backward(self.dir)
        if not self.player and pressed[pygame.K_LEFT] or self.player and pressed[pygame.K_a]:
            self.rotate(0, tankcenter) if pressed[pygame.K_DOWN] else self.rotate(1, tankcenter)
        elif not self.player and pressed[pygame.K_RIGHT] or self.player and pressed[pygame.K_d]:
            self.rotate(1, tankcenter) if pressed[pygame.K_DOWN] else self.rotate(0, tankcenter)
        self.canvas.blit(self.image, self.rect)

    def rotate(self, dir, tankcenter):
        image = pygame.transform.rotate(self.oriImage, self.rotAngle)
        self.rect = image.get_rect(center=self.rect.center)
        if self.locked:
            self.rect = self.image.get_rect(center=self.rect.center)
            self.locked = False
            return
        if self.rotAngle == 0:  # pygame不支持指定中心点的旋转,所以旋转后,需要额外调整枪管的位置
            self.rect.center = (tankcenter[0], tankcenter[1] - self.bias)
        else:
            self.rect.center = (tankcenter[0] - math.sin(math.pi / (180 / self.rotAngle)) * self.bias,
                                tankcenter[1] - math.cos(math.pi / (180 / self.rotAngle)) * self.bias)
        self.rect = self.image.get_rect(center=self.rect.center)
        self.image = image
        self.rect = self.image.get_rect(center=self.rect.center)

    def forward_backward(self, dir, sign=1):
        assert dir == 1 or dir == -1
        centerX = self.rect.center[0]
        centerY = self.rect.center[1]
        c = self.rect.center
        if self.rotAngle == 0:
            center = (centerX, centerY - self.speed * dir)
        else:
            center = (centerX - math.sin(math.pi / (180 / self.rotAngle)) * self.speed * dir * sign,
                      centerY - math.cos(math.pi / (180 / self.rotAngle)) * self.speed * dir * sign)
        self.rect.center = center
        if self.locked:
            self.rect.center = c
            self.locked = False


class Wall(pygame.sprite.Sprite):
    def __init__(self, row, ind, canvas):
        super(Wall, self).__init__()
        self.canvas = canvas
        self.image = pygame.image.load('source/wall.png')
        if row % 2:
            self.horizontal = False
            self.image = pygame.transform.rotate(self.image, 90)
            self.rect = self.image.get_rect()
            self.rect.center = (90 * ind, 90 * (row // 2) + 45)
            return
        else:
            self.horizontal = True
            self.angle = 180
            self.rect = self.image.get_rect()
            self.rect.center = (90 * ind + 45, 90 * row // 2)
        self.canvas.blit(self.image, self.rect)
        return

    def update(self):
        self.canvas.blit(self.image, self.rect)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, imgPath, canvas, speed, tank, wallList, tankGroup, seq, maxDistance, interval):
        super(Bullet, self).__init__()
        self.tank = tank
        self.image = pygame.image.load(imgPath).convert_alpha()
        self.rect = self.image.get_rect()
        self.reset_pos()
        self.canvas = canvas
        self.speed = speed
        self.tankGroup = tankGroup
        self.dir = 1
        self.wallList = wallList
        self.rotAngle = 0
        self.sign = 1
        self.endurance = maxDistance  # 炮弹最大路程（以帧为单位）
        self.dist = 0  # 炮弹实际路程
        self.interval = interval

    def reset_pos(self):
        self.rotAngle = self.tank.rotAngle
        if self.rotAngle == 0:  # 调整炮弹的起始位置
            self.rect.center = (self.tank.rect.center[0], self.tank.rect.center[1] - 17)
        else:
            self.rect.center = (self.tank.rect.center[0] - math.sin(math.pi / (180 / self.rotAngle)) * 17,
                                self.tank.rect.center[1] - math.cos(math.pi / (180 / self.rotAngle)) * 17)

    def update(self):
        if self.dist == self.endurance:
            self.reset()
            return False
        self.forward_backward(1)
        self.canvas.blit(self.image, self.rect)
        self.dist += 1
        return True

    def forward_backward(self, dir, sign=1):
        if self.sign:
            self.reset_pos()
            self.rotAngle = self.tank.rotAngle
            self.sign = 0
        assert dir == 1 or dir == -1
        centerX = self.rect.center[0]
        centerY = self.rect.center[1]
        if self.rotAngle == 0:
            self.rect.center = (centerX, centerY - self.speed * dir)
        else:
            self.rect.center = (centerX - math.sin(math.pi / (180 / self.rotAngle)) * self.speed * dir * sign,
                                centerY - math.cos(math.pi / (180 / self.rotAngle)) * self.speed * dir * sign)
        collided, horizontal = self.check_collide(self.wallList, (centerX, centerY), self.rect.center)
        if collided:
            self.change_rotangle(horizontal, centerX, centerY)
            self.rect.center = (centerX, centerY)
            return

    def change_rotangle(self, horizontal, centerX, centerY):
        signX = -1 < centerX - int(centerX / 60 + 0.5) * 60 <= 1
        signY = -1 < centerY - int(centerY / 60 + 0.5) * 60 <= 1
        if horizontal and not signY:
            self.rotAngle = 180 - self.rotAngle if self.rotAngle > 0 else -180 - self.rotAngle
            return
        elif horizontal and signY:
            self.rotAngle = -self.rotAngle
            return
        if not horizontal and not signX:
            self.rotAngle = -self.rotAngle
            return
        elif not horizontal and signX:
            self.rotAngle = 180 - self.rotAngle if self.rotAngle > 0 else -180 - self.rotAngle

    def check_collide(self, wallList, oldCenter, newCenter):
        width = abs(newCenter[0] - oldCenter[0])  # 构造表示子弹在相邻帧之间位移的矩形
        height = abs(newCenter[1] - oldCenter[1])
        rect = pygame.Rect(min(oldCenter[0], newCenter[0]),
                           min(oldCenter[1], newCenter[1]),
                           1 if width == 0 else width,
                           1 if height == 0 else height, )
        for wall in wallList.objList:
            if wall.rect.colliderect(rect):
                return True, wall.horizontal
        return False, 0

    def reset(self):
        self.sign = 1
        self.dist = 0
        # self.shootSignal = self.expectedSeq
        # self.reset_pos()
        # self.rect = self.image.get_rect(center=self.tank.rect.center)


class Kamui(Tool):
    def __init__(self, canvas, wallList, tankGroup, path='source/kamui.png', effectiveTime=20000):
        super(Kamui, self).__init__(path, canvas, wallList, tankGroup)
        self.clock0 = None
        self.clock1 = None
        self.effectiveTime = effectiveTime
        self.updateTank = None

    def update(self):
        if self.interval <= 0 and self.updateTank is None:
            if self.holdOnTime > 0:
                self.canvas.blit(self.image, self.rect)
                sign, tank = self.check_tank_collide()
                if sign:
                    tank.enable_kamui()
                    self.clock0 = pygame.time.get_ticks()
                    self.updateTank = tank
                    return
                self.holdOnTime -= 1
            else:
                self.reset()
        elif self.updateTank is not None:
            self.clock1 = pygame.time.get_ticks()
            if self.clock1 - self.clock0 >= self.effectiveTime:
                if not self.updateTank.kamuiSign:
                    self.updateTank.disable_kamui()
                    self.reset()
                elif not self.updateTank.kamui:
                    self.reset()
        else:
            self.interval -= 1

    def reset(self):
        self.interval = self.intervalMean + random.randint(-50, 50)
        self.holdOnTime = self.holdOnTimeMean + random.randint(-20, 20)
        self.reset_pos()
        self.updateTank = None


class Group:  # 自定义的组，存放实例以批量化操作
    def __init__(self, num=1):
        self.num = num
        self.objList = []

    def add(self, tank):
        self.objList.append(tank)

    def update(self):
        for tank in self.objList:
            tank.update()


class TankGroup(pygame.sprite.Group):
    def update(self, *args, **kwargs):
        res = []
        for tank in self:
            res.append(tank.update())
        self.bulletGroup.update()
        return res

    def init_bullet(self, bulletGroup):
        self.bulletGroup = bulletGroup


class BulletGroup(Group):
    def __init__(self, bulletNum, interval=500):
        super(BulletGroup, self).__init__()
        self.bulletNum = bulletNum
        self.ind0 = 0
        self.ind1 = bulletNum
        self.reset_clock(0)
        self.reset_clock(1)
        self.clock2 = None
        self.interval = interval
        self.updateList0 = []
        self.updateList1 = []
        self.updateList = []
        self.sign = False
        self.bulletCapacity0 = bulletNum
        self.bulletCapacity1 = bulletNum
        self.realBulletCapacity0 = bulletNum
        self.realBulletCapacity1 = bulletNum

    def update(self):
        self.clock2 = pygame.time.get_ticks()
        pressed = pygame.key.get_pressed()
        if self.clock2 - self.clock0 >= self.interval:
            if pressed[pygame.K_SPACE]:
                if self.realBulletCapacity0 > 0:
                    self.updateList0.append(self.objList[self.ind0])
                    self.update_ind(0)
                    self.realBulletCapacity0 -= 1
                    self.reset_clock(0)
        if self.clock2 - self.clock1 >= self.interval:
            if pressed[pygame.K_1]:
                if self.realBulletCapacity1 > 0:
                    self.updateList1.append(self.objList[self.ind1])
                    self.update_ind(1)
                    self.realBulletCapacity1 -= 1
                    self.reset_clock(1)
        self.updateList = self.updateList0 + self.updateList1
        length = len(self.updateList0)
        for i in range(length):
            sign = self.updateList0[length - i - 1].update()
            if not sign:
                self.realBulletCapacity0 += 1
                self.updateList0.pop(length - i - 1)
        length = len(self.updateList1)
        for i in range(length):
            sign = self.updateList1[length - i - 1].update()
            if not sign:
                self.realBulletCapacity1 += 1
                self.updateList1.pop(length - i - 1)

    def update_ind(self, sign):
        if not sign:
            self.ind0 = self.ind0 + 1 if self.ind0 < self.bulletNum - 1 else 0
        else:
            self.ind1 = self.ind1 + 1 if self.ind1 < 2 * self.bulletNum - 1 else self.bulletNum

    def reset_clock(self, sign):
        if not sign:
            self.clock0 = pygame.time.get_ticks()
        else:
            self.clock1 = pygame.time.get_ticks()


def click(event, clickedObj):
    if event.type == pygame.MOUSEBUTTONUP:  # 鼠标按钮抬起事件
        mousePos = pygame.mouse.get_pos()
        bottom_left = clickedObj.textRect.bottomleft
        top_right = clickedObj.textRect.topright
        return bottom_left[0] <= mousePos[0] <= top_right[0] and \
            top_right[1] <= mousePos[1] <= bottom_left[1]
    return False
