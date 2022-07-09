import random

import pygame.event
from utils import clamp, map_to_range, Timer
from config import WIDTH, HEIGHT
from operator import attrgetter
from math import sin, cos, radians, degrees, atan2
from typing import Union


class BaseObject:
    def __init__(self):
        self.alive = True
        self.z = 0
        self.object_manager: Union[ObjectManager, None] = None

    def update(self, events: list[pygame.event.Event]):
        pass

    def draw(self, surf: pygame.Surface):
        pass

    def check_collision(self, player: 'Player'):
        pass


class Enemy(BaseObject):
    def use_ai(self, player: 'Player'):
        if not player:
            return


class Player(BaseObject):
    def __init__(self, x=WIDTH // 2, y=HEIGHT // 2 + 150):
        super().__init__()
        self.x = x
        self.y = y
        self.size = 15
        self.z = 1

    def update(self, events: list[pygame.event.Event]):
        speed = 5
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.y -= speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.y += speed

        offset = 5 + self.size // 2

        self.x = clamp(self.x, offset, WIDTH - offset)
        self.y = clamp(self.y, offset, HEIGHT - offset)

    def draw(self, surf: pygame.Surface):
        pygame.draw.rect(surf, 'blue', (self.x - self.size // 2, self.y - self.size // 2, self.size, self.size))


class PointBullet(BaseObject):
    def __init__(self, x=WIDTH // 2, y=HEIGHT // 2, dx=1.0, dy=1.0):
        super().__init__()
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.speed = 2
        self.r = 5

    def update(self, events: list[pygame.event.Event]):
        self.x += self.dx * self.speed
        self.y += self.dy * self.speed

        if not ((0 <= self.x <= WIDTH) and (0 <= self.y <= HEIGHT)):
            self.alive = False

    def draw(self, surf: pygame.Surface):
        pygame.draw.circle(surf, 'white', (self.x, self.y), self.r)
        pygame.draw.circle(surf, 'red', (self.x, self.y), self.r, 2)


class LineBullet(BaseObject):
    def __init__(self, x=WIDTH // 2, y=HEIGHT // 2, dx=1.0, dy=1.0):
        super().__init__()
        self.x = x
        self.y = y
        self.speed = 1
        self.dx = dx
        self.dy = dy
        self.length = WIDTH
        self.timer = Timer(1)

    def update(self, events: list[pygame.event.Event]):
        # self.x += self.dx * self.speed
        # self.y += self.dy * self.speed
        if self.timer.tick:
            self.alive = False

    def draw(self, surf: pygame.Surface):
        pygame.draw.line(surf, 'white', (self.x, self.y), (self.x + self.length * self.dx, self.y + self.length * self.dy))


class LineRay(BaseObject):
    def __init__(self, x=WIDTH // 2, y=HEIGHT // 2, player_x=0, player_y=0):
        super().__init__()
        self.x = x
        self.y = y
        self.angle = degrees(atan2(player_y - self.y, player_x - self.x))
        self.length = 0
        self.timer = Timer(3)
        self.ray_timer = Timer(0.01)
        self.offset = 30
        self.t = Timer(2)
        self.k = random.choice([-1, 1])
        self.angle_offset = self.angle + self.offset * self.k
        self.original_angle_offset = self.angle_offset
        self.done = False

    def update(self, events: list[pygame.event.Event]):
        # self.x += self.dx * self.speed
        # self.y += self.dy * self.speed

        self.length += 10 if not self.done else -10

        if self.length > WIDTH:
            self.length = WIDTH
        if self.length < 0:
            self.length = 0
            self.alive = False

        if self.timer.tick:
            self.done = True

        if abs(self.original_angle_offset - self.angle_offset) >= self.offset * 2:
            self.done = True

        if not self.done and self.length >= WIDTH:
            self.angle_offset -= self.k * 2
            if self.ray_timer.tick:
                dx = cos(radians(self.angle_offset))
                dy = sin(radians(self.angle_offset))
                self.object_manager.add(
                    LineBullet(self.x, self.y, dx, dy)
                )

        # if not ((0 <= self.x <= WIDTH) and (0 <= self.y <= HEIGHT)):
        #     self.alive = False

    def draw(self, surf: pygame.Surface):
        for i in (self.angle - self.offset, self.angle + self.offset):
            dx = cos(radians(i))
            dy = sin(radians(i))
            if not self.done:
                pygame.draw.line(surf, 'red',
                                 (self.x, self.y),
                                 (self.x + dx * self.length, self.y + dy * self.length), 5)
                # pygame.draw.line(surf, 'white',
                #                  (self.x, self.y),
                #                  (self.x + dx * self.length, self.y + dy * self.length), 1)
            else:
                pygame.draw.line(surf, 'red', (self.x + dx * (WIDTH - self.length), self.y + dy * (WIDTH - self.length)),
                                 (self.x + dx * WIDTH, self.y + dy * WIDTH), 3)


class BulletEnemy(Enemy):
    def __init__(self, x=WIDTH // 2, y=HEIGHT // 2):
        super().__init__()
        self.x = x
        self.y = y
        self.r = 10
        self.phase = 5
        self.phase_timer = Timer(5)
        self.bullet_timer = Timer(0.5)
        self.z = 1
        self.offset = 0

    def use_ai(self, player: 'Player'):
        super().use_ai(player)
        if self.phase_timer.tick:
            self.phase += 1
        _bullets = []
        if self.phase >= 6:
            if self.alive:
                self.alive = False
                # self.object_manager.add(
                #     LineEnemy(self.x, self.y)
                # )
            return
        if self.phase % 2 == 0:
            self.phase_timer.timeout = 5
            if self.phase == 0:
                if self.bullet_timer.tick:
                    for i in range(0, 360, 30):
                        dx = cos(radians(i))
                        dy = sin(radians(i))
                        _bullets.append(
                            PointBullet(self.x, self.y, dx, dy)
                        )
            elif self.phase == 2:
                if self.bullet_timer.tick:
                    for i in range(0, 360, 15):
                        dx = cos(radians(i))
                        dy = sin(radians(i))
                        _bullets.append(
                            PointBullet(self.x, self.y, dx, dy)
                        )
            elif self.phase == 4:
                self.bullet_timer.timeout = 0.1
                if self.bullet_timer.tick:
                    self.offset += 10
                    self.offset %= 360
                    for i in range(self.offset, 360 + self.offset, 90):
                        dx = cos(radians(i))
                        dy = sin(radians(i))
                        _bullets.append(
                            PointBullet(self.x, self.y, dx, dy)
                        )
        else:
            self.phase_timer.timeout = 2

        self.object_manager.add_multiple(_bullets)

    def draw(self, surf: pygame.Surface):
        pygame.draw.circle(surf, 'white', (self.x, self.y), self.r)
        pygame.draw.circle(surf, 'red', (self.x, self.y), self.r, 2)


class LineEnemy(Enemy):
    def __init__(self, x=WIDTH // 2, y=HEIGHT // 2):
        super().__init__()
        self.x = x
        self.y = y
        self.r = 10
        self.phase = 0
        self.phase_timer = Timer(10)
        self.bullet_timer = Timer(0.5)
        self.ray_timer = Timer(0)
        self.z = 1
        self.offset = 0

    def launch_ray(self, player: Player = None):
        # player = None
        # for i in self.object_manager.objects:
        #     if isinstance(i, Player):
        #         player = i
        if player:
            self.object_manager.add(
                LineRay(self.x, self.y, player.x, player.y)
            )

    def use_ai(self, player: 'Player'):
        super().use_ai(player)
        if self.phase_timer.tick:
            self.phase += 1
        if self.ray_timer.timeout == 0:
            self.ray_timer.timeout = 1
            self.launch_ray(player)
        _bullets = []
        if self.phase == 0:
            if self.ray_timer.tick:
                self.launch_ray(player)
        self.object_manager.add_multiple(_bullets)

    def update(self, events: list[pygame.event.Event]):
        pass

    def draw(self, surf: pygame.Surface):
        pygame.draw.circle(surf, 'white', (self.x, self.y), self.r)
        pygame.draw.circle(surf, 'red', (self.x, self.y), self.r, 2)


class PointClicked(BaseObject):
    def __init__(self, x, y, initial_r=0):
        super().__init__()
        self.x = x
        self.y = y
        self.r = initial_r

    def update(self, events: list[pygame.event.Event]):
        self.r += 5
        if self.r > 100:
            self.r = 100
            self.alive = False
        # self.r = clamp(self.r, 0, 100)

    def draw(self, surf: pygame.Surface):
        if self.r >= 0:
            pygame.draw.circle(surf, 'white', (self.x, self.y), self.r, 10 - self.r // 10 + 1)


class ObjectManager:
    def __init__(self):
        self.objects: list[BaseObject] = []
        self._to_add: list[BaseObject] = []
        self.player = None

    def get_object_count(self, instance):
        c = 0
        for i in self.objects:
            if type(i) == instance:
                c += 1
        return c

    def clear(self):
        self._to_add.clear()
        self.objects.clear()
        self.player = None

    def init(self):
        self.clear()
        self.player = Player(WIDTH // 2, HEIGHT // 2 + 150)

    def add(self, _object: BaseObject):
        _object.object_manager = self
        self._to_add.append(_object)

    def add_multiple(self, _objects: list[BaseObject]):
        for i in _objects:
            self.add(i)

    def update(self, events: list[pygame.event.Event]):
        if self._to_add:
            self.objects.extend(self._to_add)
            self._to_add.clear()
        self.objects = [i for i in self.objects if i.alive]
        self.objects.sort(key=attrgetter('z'))
        # print(self.objects)
        # print(self.get_object_count(Player))
        for i in self.objects:
            # i.update(events)
            i.check_collision(self.player)
            if isinstance(i, Enemy):
                i.use_ai(self.player)
            else:
                i.update(events)
        if self.player:
            self.player.update(events)

    def draw(self, surf: pygame.Surface):
        if self.player:
            self.player.draw(surf)
        for i in self.objects:
            i.draw(surf)
