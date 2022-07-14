import random
from math import sin, cos, radians, degrees, atan2
from operator import attrgetter
from typing import Union

import pygame.event

from config import WIDTH, HEIGHT, Globals
from constants import *
from utils import *


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
        self.rect_list = []
        self.surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.surf.fill('blue')

    @property
    def pos(self):
        return self.x, self.y

    @property
    def rect(self):
        return pygame.Rect(self.x - self.size // 2, self.y - self.size // 2, self.size, self.size)

    def update(self, events: list[pygame.event.Event]):
        speed = 7
        v = pygame.Vector2(0, 0)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RSHIFT] or keys[pygame.K_LSHIFT]:
            speed *= 3
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            v.x -= 1
            # self.x -= speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            v.x += 1
            # self.x += speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            v.y -= 1
            # self.y -= speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            v.y += 1
            # self.y += speed
        if v.length() > 0:
            v = v.normalize() * speed
        else:
            v *= speed
        if v.length() != 0:
            self.x += v.x
            self.y += v.y
            if len(self.rect_list) < 20:
                self.rect_list.append([self.x, self.y, 255])
        offset = 5 + self.size // 2

        self.x = clamp(self.x, offset, WIDTH - offset)
        self.y = clamp(self.y, offset, HEIGHT - offset)

    def draw(self, surf: pygame.Surface):
        rect = self.rect
        self.rect_list = [i for i in self.rect_list if i[2] > 1]
        for i in self.rect_list:
            i[2] -= 35
            i[2] = clamp(i[2], 0, 255)
            color = [0, 0, i[2]]
            self.surf.set_alpha(i[2])
            # pygame.draw.rect(surf, '#00AAFF', (i[0], i[1], 10, 10))
            # pygame.draw.rect(surf, color, (i[0] - self.size // 2, i[1] - self.size // 2, self.size, self.size))
            surf.blit(self.surf, self.surf.get_rect(center=i[0:2]))
        pygame.draw.rect(surf, 'blue', rect)


class PointBullet(BaseObject):
    def __init__(self, x=WIDTH // 2, y=HEIGHT // 2, dx=1.0, dy=1.0, r=5, color='red'):
        super().__init__()
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.speed = 2
        self.r = r
        self.color = color

    @property
    def rect(self):
        return pygame.Rect(self.x - self.r // 2, self.y - self.r // 2, self.r * 2, self.r * 2).inflate(-2, -2)

    def check_collision(self, player: 'Player'):
        return player.rect.inflate(-5, -5).colliderect(self.rect)

    def update(self, events: list[pygame.event.Event]):
        self.x += self.dx * self.speed
        self.y += self.dy * self.speed

        if not ((0 <= self.x <= WIDTH) and (0 <= self.y <= HEIGHT)):
            self.alive = False

    def draw(self, surf: pygame.Surface):
        pygame.draw.circle(surf, 'white', (self.x, self.y), self.r)
        pygame.draw.circle(surf, self.color, (self.x, self.y), self.r, 2 if self.r > 3 else 1)


class PointSpreadBullet(BaseObject):
    def __init__(self, pos=(WIDTH // 2, HEIGHT // 2), target_pos=(WIDTH // 2, HEIGHT // 2)):
        super().__init__()
        self.pos = pygame.Vector2(pos)
        self.target_pos = pygame.Vector2(target_pos)
        self.r = 0

    def update(self, events: list[pygame.event.Event]):
        self.r += 0.15
        self.r = clamp(self.r, 0, 10)
        _dx = (self.target_pos - self.pos)
        # self.pos += dx / 20
        if _dx.length() < 3:
            self.pos = self.target_pos
        else:
            self.pos += _dx / 20
        if self.pos == self.target_pos:
            _bullets = []
            speed = 3
            offset = random.randint(-15, 15)
            for i in range(offset, 360 + offset, 30):
                dx = cos(radians(i)) * speed
                dy = sin(radians(i)) * speed
                _bullets.append(PointBullet(self.pos.x, self.pos.y, dx, dy, r=3))
            self.object_manager.add_multiple(_bullets)
            self.alive = False

    def draw(self, surf: pygame.Surface):
        color = random.choice(['white', 'red'])
        pygame.draw.circle(surf, color, self.pos, self.r)


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

    def check_collision(self, player: 'Player'):
        return player.rect.clipline(*self.points)

    @property
    def points(self):
        return (self.x, self.y), (self.x + self.length * self.dx, self.y + self.length * self.dy)

    def update(self, events: list[pygame.event.Event]):
        # if self.move:
        #     self.x += self.dx * self.speed
        #     self.y += self.dy * self.speed
        if self.timer.tick:
            self.alive = False

    def draw(self, surf: pygame.Surface):
        pygame.draw.line(surf, 'white', *self.points)


class LineBullet1(BaseObject):
    def __init__(self, x=WIDTH // 2, y=HEIGHT // 2, dx=1.0, dy=1.0, length=10, speed=1):
        super().__init__()
        self.x = x
        self.y = y
        self.speed = speed
        self.dx = dx
        self.dy = dy
        self.length = length
        # self.timer = Timer(10)

    @property
    def points(self):
        return (self.x, self.y), (self.x + self.length * self.dx, self.y + self.length * self.dy)

    def check_collision(self, player: 'Player'):
        return player.rect.clipline(*self.points)

    def update(self, events: list[pygame.event.Event]):
        self.x += self.dx * self.speed
        self.y += self.dy * self.speed
        # if self.timer.tick:
        #     self.alive = Falsed
        if not pygame.Rect(0, 0, WIDTH, HEIGHT).inflate(50, 50).collidepoint(self.x, self.y):
            self.alive = False

    def draw(self, surf: pygame.Surface):
        points = self.points
        pygame.draw.line(surf, 'blue', points[0], points[1], 5)
        pygame.draw.line(surf, 'white', points[0], points[1], 2)


class LineBullet2(BaseObject):
    VEL = 0.1
    LENGTH = 50
    COLOUR = "RED"
    BORDER_COLOUR = "WHITE"

    def __init__(self, c_pos, _dir):
        super().__init__()
        self.c_pos = c_pos
        self._dir = _dir
        self.pos1 = pygame.Vector2(self.c_pos)
        self.pos2 = self.c_pos + self._dir * self.LENGTH

    def update(self, events: list[pygame.event.Event]):
        self.pos1 += self._dir * self.VEL
        self.pos2 += self._dir * self.VEL

    def draw(self, surf: pygame.Surface):
        pygame.draw.line(surf, self.COLOUR, self.pos1, self.pos2, width=4)
        pygame.draw.circle(surf, self.BORDER_COLOUR, self.pos2, 10)
        pygame.draw.circle(surf, self.COLOUR, self.pos2, 8)


class LineSpreadBullet(BaseObject):
    def __init__(self, pos=(WIDTH // 2, HEIGHT // 2), target_pos=(WIDTH // 2, HEIGHT // 2)):
        super().__init__()
        self.pos = pygame.Vector2(pos)
        self.target_pos = pygame.Vector2(target_pos)

    def update(self, events: list[pygame.event.Event]):
        _dx = (self.target_pos - self.pos)
        # self.pos += dx / 20
        if _dx.length() < 3:
            self.pos = self.target_pos
        else:
            self.pos += _dx / 20
        if self.pos == self.target_pos:
            _bullets = []
            speed = 3
            offset = random.randint(-15, 15)
            for i in range(offset, 360 + offset, 30):
                dx = cos(radians(i)) * speed
                dy = sin(radians(i)) * speed
                _bullets.append(LineBullet1(self.pos.x, self.pos.y, dx, dy, speed=3))
            self.object_manager.add_multiple(_bullets)
            self.alive = False

    def draw(self, surf: pygame.Surface):
        color = random.choice(['white', 'blue'])
        try:
            pygame.draw.line(surf, color, self.pos, self.pos + (self.target_pos - self.pos).normalize() * 10, 2)
        except ValueError:
            pygame.draw.circle(surf, color, self.pos, 1)


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


class PointEnemy(Enemy):
    def __init__(self, x=WIDTH // 2, y=HEIGHT // 2):
        super().__init__()
        self.x = x
        self.y = y
        self.r = 10
        self.phase = 0
        self.phase_timer = Timer(5)
        self.bullet_timer = Timer(0.5)
        self.z = 1
        self.offset = 0

        def get_all_range(step=0, offset=0):
            return range(offset, 360 + offset, step)

        def get_one_by_one_range_list(initial_time=0.0, dt=0.1, step=1, offset=0, vel=1.0):
            _list = [[initial_time + dt * i, [i], vel] for i in get_all_range(step=step, offset=offset)]
            return _list

        def get_one_by_one_together_list(initial_time=0.0, dt=0.1, step=1, offset=1, vel=1.0, beats=1):
            _list = []
            for i in range(beats):
                a = [initial_time + dt * i, get_all_range(step, offset * i), vel]
                _list.append(a)
            return _list

        def get_range_list(initial_time=0.0, dt=0.1, step=0, offset=0, vel=1.0, beats=1):
            _list = [[initial_time + dt * j, [i for i in get_all_range(step=step, offset=offset * j)], vel] for j in range(beats)]
            return _list

        self.launching_patterns = [
            # [0.1, [225, 135, 45, -45]],
            [0.1, get_all_range(90, 45)],
            [2, get_all_range(90, 0)],
            [3.7, get_all_range(90, 45)],
            [5.3, get_all_range(90, 0)],
            [7.5, get_all_range(90, 45)],
            [9, get_all_range(90, 0)],
            [11, get_all_range(90, 45)],
            [13, get_all_range(90, 0)],

            *get_one_by_one_range_list(14, dt=0.001, step=8, vel=3),
            *get_range_list(15, dt=0.9, step=30, offset=5, vel=1, beats=8),
            *get_range_list(22, dt=1, step=15, offset=5, vel=1, beats=7),
            *get_range_list(29.5, dt=0.4, step=30, offset=0, vel=3, beats=1),
            *get_one_by_one_range_list(30.5, dt=0.002, step=20, vel=2),
            *get_range_list(32, dt=0.4, step=30, offset=0, vel=3, beats=1),
            *get_one_by_one_range_list(32.5, dt=0.002, step=20, vel=2),
            *get_range_list(33.5, dt=0.4, step=30, offset=0, vel=3, beats=1),
            *get_one_by_one_range_list(34.5, dt=0.002, step=20, vel=2),
            *get_range_list(35, dt=0.4, step=30, offset=10, vel=3, beats=6),

            *get_range_list(35.5, dt=1, step=45, offset=25, vel=3, beats=9),

            # *get_ony_by_one_together_list(44, dt=0.01, step=10, offset=10, vel=1, directions=5),
            *get_one_by_one_together_list(44, dt=0.1, step=45, offset=5, vel=3, beats=60),

            *get_one_by_one_together_list(51.5, dt=0.1, step=45, offset=-5, vel=3, beats=60),

            [88, 'move'],

            *get_range_list(88, dt=1, step=90, offset=25, vel=2, beats=8),

            [96, get_all_range(30, 10), 3],
            *get_one_by_one_range_list(97, dt=0.002, step=360 // 10, offset=5, vel=3),

            [97.75, get_all_range(30, 10), 3],
            *get_one_by_one_range_list(98.75, dt=0.002, step=360 // 10, offset=5, vel=3.25),

            [99.5, get_all_range(30, 10), 3],
            *get_one_by_one_range_list(100.5, dt=0.002, step=360 // 10, offset=5, vel=3.5),

            [101.25, get_all_range(30, 10), 3],
            *get_one_by_one_range_list(102.25, dt=0.002, step=360 // 10, offset=5, vel=4),

            # *get_one_by_one_range_list(112, dt=0.002, step=360 // 10, offset=5, vel=4),

            *get_range_list(118, 0.9, 30, 10, vel=3, beats=9),
            *get_one_by_one_range_list(126.5, dt=0.002, step=360 // 10, offset=5, vel=4),

            [127.5, get_all_range(30, 10), 3],
            *get_one_by_one_range_list(128.25, dt=0.002, step=360 // 10, offset=5, vel=4),

            [129.5, get_all_range(30, 10), 3],
            *get_one_by_one_range_list(130.25, dt=0.002, step=360 // 10, offset=5, vel=4),

            [131.5, get_all_range(30, 10), 3],
            *get_one_by_one_range_list(132.25, dt=0.002, step=360 // 10, offset=5, vel=4),

            *get_range_list(initial_time=133.5, dt=1.75, step=30, offset=10, vel=5, beats=8),

            *get_range_list(147, 1, 45, 15, 3, 5),

            [1000, 'all'],
            [1000, 'all'],
            # [1000, 'all'],
            # [1000, 'all'],
            # [1000, 'all'],
            # [1000, 'all'],
            # [1000, 'all'],
            # [1000, 'all'],
            # [1000, 'all'],
            # [1000, 'all'],
            # [1000, 'all'],
            # [1000, 'all'],
            # [1000, 'all'],
            # [1000, 'all'],
            # [1000, 'all'],
            # [1000, 'all'],
            # [1000, 'all'],
            # [1000, 'all'],
            # [1000, 'all'],
            # [1000, 'all'],
            # [1000, 'all'],
            # [1000, 'all'],
            # [1000, 'all'],
            # [1000, 'all'],
            # [1000, 'all'],
        ]
        self.current_timestamp = 0

        def get_enemies_list(_time=0.0, _dt=0.0, _type='a', beats=1):
            if _type == 'a':
                return [[
                    _time + i * _dt,
                    PointSpreadBullet,
                    [self.pos, self.pos, self.pos, self.pos],
                    [(WIDTH / 4, HEIGHT / 4), (WIDTH * 3 / 4, HEIGHT / 4), (WIDTH * 3 / 4, HEIGHT * 3 / 4), (WIDTH / 4, HEIGHT * 3 / 4)]
                ] for i in range(beats)]
            elif _type == 'b':
                return [[
                    _time + i * _dt,
                    PointSpreadBullet,
                    [self.pos, self.pos, self.pos, self.pos],
                    [(WIDTH / 2, HEIGHT / 4), (WIDTH * 3 / 4, HEIGHT / 2), (WIDTH / 2, HEIGHT * 3 / 4), (WIDTH / 4, HEIGHT / 2)]
                ] for i in range(beats)]
            elif _type == 'c':
                return [[
                    _time + i * _dt,
                    PointSpreadBullet,
                    [self.pos] * 8,
                    [(WIDTH / 4, HEIGHT / 4), (WIDTH * 3 / 4, HEIGHT / 4), (WIDTH * 3 / 4, HEIGHT * 3 / 4), (WIDTH / 4, HEIGHT * 3 / 4),
                     (WIDTH / 2, HEIGHT / 4), (WIDTH * 3 / 4, HEIGHT / 2), (WIDTH / 2, HEIGHT * 3 / 4), (WIDTH / 4, HEIGHT / 2)]
                ] for i in range(beats)]
            else:
                return []

        def get_enemy_list_beats(initial_time=0.0, dt=0.002, _type='bottom', count=2):
            if _type == 'top':
                return [
                    [
                        initial_time + i * dt,
                        PointSpreadBullet,
                        [self.pos],
                        [(WIDTH * (i + 1) / (count + 1), 50)]
                    ] for i in range(count)
                ]
            elif _type == 'bottom':
                return [
                    [
                        initial_time + i * dt,
                        PointSpreadBullet,
                        [self.pos],
                        [(WIDTH * (i + 1) / (count + 1), HEIGHT - 25)]
                    ] for i in range(count)
                ]
            elif _type == 'left':
                return [
                    [
                        initial_time + i * dt,
                        PointSpreadBullet,
                        [self.pos],
                        [(25, HEIGHT * (i + 1) / (count + 1))]
                    ] for i in range(count)
                ]
            elif _type == 'right':
                return [
                    [
                        initial_time + i * dt,
                        PointSpreadBullet,
                        [self.pos],
                        [(WIDTH - 25, HEIGHT * (i + 1) / (count + 1))]
                    ] for i in range(count)
                ]
            else:
                return []

        self.enemy_launch_patterns = [
            # [timestamp, enemy_type, [pos_list], [target_pos_list]]
            *get_enemies_list(59, _dt=1.8, _type='a', beats=4),
            *get_enemies_list(59 + 1.8 * 4 + 0.1, _dt=1.8, _type='b', beats=4),
            *get_enemies_list(74, _dt=1.8, _type='c', beats=8),

            [
                103,
                PointSpreadBullet,
                [self.pos] * 3,
                [(WIDTH / 4, HEIGHT / 4), (WIDTH / 2, HEIGHT / 4), (WIDTH * 3 / 4, HEIGHT / 4)]
            ],
            [
                105,
                PointSpreadBullet,
                [self.pos] * 3,
                [(WIDTH / 4, HEIGHT * 3 / 4), (WIDTH / 2, HEIGHT * 3 / 4), (WIDTH * 3 / 4, HEIGHT * 3 / 4)]
            ],
            [
                107,
                PointSpreadBullet,
                [self.pos] * 3,
                [(WIDTH / 4, HEIGHT / 4), (WIDTH / 4, HEIGHT / 2), (WIDTH / 4, HEIGHT * 3 / 4)]
            ],
            [
                109,
                PointSpreadBullet,
                [self.pos] * 3,
                [(WIDTH * 3 / 4, HEIGHT / 4), (WIDTH * 3 / 4, HEIGHT / 2), (WIDTH * 3 / 4, HEIGHT * 3 / 4)]
            ],

            *get_enemy_list_beats(112, dt=0.1, _type='top', count=7),

            *get_enemy_list_beats(113.7, dt=0.1, _type='bottom', count=7),

            *get_enemy_list_beats(115.4, dt=0.1, _type='left', count=7),

            *get_enemy_list_beats(117.1, dt=0.1, _type='right', count=7),
        ]
        self.current_enemy_timestamp = 0

        self.k = 0
        self.k1 = 0

    @property
    def pos(self):
        return self.x, self.y

    def use_ai(self, player: 'Player'):
        super().use_ai(player)
        self.r *= 0.95
        self.x += math.sin(time.time() * self.k) * self.k1
        self.y += math.cos(time.time() * self.k) * self.k1
        self.r = clamp(self.r, 10, 20)
        # if self.phase_timer.tick:
        #     self.phase += 1
        _bullets = []
        _enemies = []
        # try:
        #     if Globals.get(ELAPSED_TIME_FOR_SOUNDTRACK) > Globals.get(TOTAL_DURATION_OF_SOUNDTRACK):
        #         print(Globals.get(ELAPSED_TIME_FOR_SOUNDTRACK), Globals.get(TOTAL_DURATION_OF_SOUNDTRACK), 'yooooooooooo')
        #         self.alive = False
        # except TypeError:
        #     pass
        try:
            if Globals.get(ELAPSED_TIME_FOR_SOUNDTRACK) > self.launching_patterns[self.current_timestamp][0]:
                if self.launching_patterns[self.current_timestamp][1] == 'all':
                    for i in range(0, 360, 30):
                        dx = cos(radians(i))
                        dy = sin(radians(i))
                        try:
                            v = self.launching_patterns[self.current_timestamp][2]
                            dx *= v
                            dy *= v
                        except IndexError:
                            pass
                        _bullets.append(
                            PointBullet(self.x, self.y, dx, dy)
                        )
                else:
                    if self.launching_patterns[self.current_timestamp][1] == 'move':
                        self.k = 5
                        self.k1 = 2
                    else:
                        for i in self.launching_patterns[self.current_timestamp][1]:
                            dx = cos(radians(i))
                            dy = sin(radians(i))
                            try:
                                v = self.launching_patterns[self.current_timestamp][2]
                                dx *= v
                                dy *= v
                            except IndexError:
                                pass
                            _bullets.append(
                                PointBullet(self.x, self.y, dx, dy)
                            )
                self.current_timestamp += 1
                _c = 0
                # print(Globals.get(ELAPSED_TIME_FOR_SOUNDTRACK))
                for i in self.launching_patterns:
                    if Globals.get(ELAPSED_TIME_FOR_SOUNDTRACK) > i[0]:
                        _c += 1
                        continue
                    else:
                        # _c = self.launching_patterns.index(i)
                        break
                # if self.current_timestamp != _c:
                #     _bullets.clear()
                self.current_timestamp = _c
        except IndexError:
            pass

        if _bullets:
            self.object_manager.add_multiple(_bullets)
            self.r = 20

        # print(self.current_enemy_timestamp)
        try:
            curr = self.enemy_launch_patterns[self.current_enemy_timestamp]
            if Globals.get(ELAPSED_TIME_FOR_SOUNDTRACK) > curr[0]:
                for i in range(len(curr[2])):
                    pos = curr[2][i]
                    target_pos = curr[3][i]
                    _enemies.append(
                        curr[1](pos, target_pos)
                    )
                self.current_enemy_timestamp += 1
                _c = 0
                for i in self.enemy_launch_patterns:
                    if Globals.get(ELAPSED_TIME_FOR_SOUNDTRACK) > i[0]:
                        _c += 1
                        continue
                    else:
                        # _c = self.enemy_launch_patterns.index(i)
                        break
                if self.current_enemy_timestamp != _c:
                    _enemies.clear()
                self.current_enemy_timestamp = _c
        except IndexError:
            pass

        if _enemies:
            self.object_manager.add_multiple(_enemies)
            self.r = 20

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

        self.k = 0
        self.k1 = 0

        def get_one_by_one(initial_time=0.0, dt=1.0, offset=1, vel=3, beats=1, _type=LineBullet1, initial_offset=0):
            # _offset = random.randint(-10, 10)
            _offset = initial_offset
            return [
                [initial_time + i * dt, _type, [_offset + (i * offset) % 360], vel] for i in range(beats)
            ]

        def get_range_one_by_one(initial_time=0.0, dt=1.0, step=1, offset=1, vel=3, beats=1, _type=LineBullet1):
            return [
                [initial_time + i * dt, _type, range(offset * i, 360 + offset * i, step), vel] for i in range(beats)
            ]

        self.launching_patterns = [
            # [1, LineBullet1, [10, 20, 30], 3],
            *get_one_by_one(0, 0.4, offset=20, vel=5, beats=15),
            *get_one_by_one(6, 0.05, offset=20, vel=5, beats=19),
            *get_one_by_one(7, 0.4, offset=20, vel=5, beats=15),
            *get_one_by_one(13, 0.05, offset=20, vel=5, beats=19),

            *get_range_one_by_one(13, 0.425, step=30, offset=10, vel=5, beats=17),

            *get_one_by_one(19.5, 0.05, offset=20, vel=5, beats=19),

            *get_range_one_by_one(17, 0.425, step=30, offset=10, vel=5, beats=24),

            *get_one_by_one(26.5, 0.05, offset=20, vel=5, beats=19),

            *get_range_one_by_one(34, 0.4, step=30, offset=10, vel=5, beats=5),

            *get_one_by_one(36, 0.025, offset=20, vel=5, beats=10, initial_offset=0),
            *get_one_by_one(37.5, 0.025, offset=20, vel=5, beats=10, initial_offset=180),

            *get_one_by_one(42.5, 0.025, offset=20, vel=5, beats=10, initial_offset=0),
            *get_one_by_one(44.5, 0.025, offset=20, vel=5, beats=10, initial_offset=180),

            [47.75, None, 'line_ray'],
            [48, None, 'line_ray'],
            [49, None, 'line_ray'],

            *get_one_by_one(49.5, 0.025, offset=20, vel=5, beats=10, initial_offset=0),

            [51, None, 'line_ray'],

            *get_one_by_one(51.0, 0.025, offset=20, vel=5, beats=10, initial_offset=180),

            [52.5, None, 'line_ray'],

            *get_range_one_by_one(55, 0.4, step=30, offset=10, vel=5, beats=15),

            [61.5, None, 'line_ray'],
            [63.5, None, 'line_ray'],
            [65, None, 'line_ray'],
            [66.75, None, 'line_ray'],

            *get_range_one_by_one(68.5, 0.4, step=30, offset=10, vel=5, beats=4),

            [75, None, 'move'],

            *get_range_one_by_one(95.9, 0.425, step=45, offset=10, vel=5, beats=15),
            *get_range_one_by_one(102.3, 0.425, step=15, offset=10, vel=5, beats=1),
        ]

        # self.launching_patterns.clear()

        def get_enemy_list_beats(initial_time=0.0, dt=0.002, _type='bottom', count=2):
            if _type == 'top':
                return [
                    [
                        initial_time + i * dt,
                        LineSpreadBullet,
                        [self.pos],
                        [(WIDTH * (i + 1) / (count + 1), 25)]
                    ] for i in range(count)
                ]
            elif _type == 'bottom':
                return [
                    [
                        initial_time + i * dt,
                        LineSpreadBullet,
                        [self.pos],
                        [(WIDTH * (i + 1) / (count + 1), HEIGHT - 25)]
                    ] for i in range(count)
                ]
            elif _type == 'left':
                return [
                    [
                        initial_time + i * dt,
                        LineSpreadBullet,
                        [self.pos],
                        [(25, HEIGHT * (i + 1) / (count + 1))]
                    ] for i in range(count)
                ]
            elif _type == 'right':
                return [
                    [
                        initial_time + i * dt,
                        LineSpreadBullet,
                        [self.pos],
                        [(WIDTH - 25, HEIGHT * (i + 1) / (count + 1))]
                    ] for i in range(count)
                ]
            else:
                return []

        self.enemy_launch_patterns = [
            [27.5, LineSpreadBullet, [self.pos], [(150, 150)]],
            [29, LineSpreadBullet, [self.pos], [(WIDTH - 150, 150)]],

            *get_enemy_list_beats(31, dt=0.1, _type='top', count=5),
            # *get_enemy_list_beats(33, dt=0.1, _type='bottom', count=5),
            # *get_enemy_list_beats(35, dt=0.1, _type='left', count=5),
            *get_enemy_list_beats(38, dt=0.1, _type='bottom', count=5),

            *get_enemy_list_beats(40, dt=0.1, _type='left', count=5),
            *get_enemy_list_beats(42, dt=0.1, _type='right', count=5),

            *get_enemy_list_beats(43.5, dt=0.1, _type='top', count=2),
            *get_enemy_list_beats(44.5, dt=0.1, _type='bottom', count=2),

            *get_enemy_list_beats(69.5, dt=0.1, _type='bottom', count=2),
            *get_enemy_list_beats(71, dt=0.4, _type='top', count=7),

            *get_enemy_list_beats(74, dt=0.4, _type='bottom', count=7),

            *get_enemy_list_beats(77, dt=0.4, _type='left', count=7),

            *get_enemy_list_beats(80, dt=0.4, _type='right', count=7),

            *get_enemy_list_beats(83, dt=0.2, _type='top', count=10),
            *get_enemy_list_beats(85.5, dt=0.2, _type='bottom', count=10),
            *get_enemy_list_beats(88, dt=0.2, _type='left', count=10),
            *get_enemy_list_beats(90.5, dt=0.2, _type='right', count=10),
        ]

        self.current_enemy_timestamp = 0
        self.current_timestamp = 0

    @property
    def pos(self):
        return self.x, self.y

    def launch_ray(self, player: Player = None):
        if player:
            self.object_manager.add(
                LineRay(self.x, self.y, player.x, player.y)
            )

    def use_ai(self, player: 'Player'):
        super().use_ai(player)
        self.r *= 0.95
        self.x += math.sin(time.time() * self.k) * self.k1
        self.y += math.cos(time.time() * self.k) * self.k1
        self.r = clamp(self.r, 10, 20)
        # if self.phase_timer.tick:
        #     self.phase += 1
        _bullets = []
        _enemies = []
        try:
            if Globals.get(ELAPSED_TIME_FOR_SOUNDTRACK) > self.launching_patterns[self.current_timestamp][0]:
                if self.launching_patterns[self.current_timestamp][2] == 'all':
                    for i in range(0, 360, 30):
                        dx = cos(radians(i))
                        dy = sin(radians(i))
                        try:
                            v = self.launching_patterns[self.current_timestamp][2]
                            dx *= v
                            dy *= v
                        except IndexError:
                            pass
                        _bullets.append(
                            self.launching_patterns[self.current_timestamp][1](self.x, self.y, dx, dy)
                        )
                else:
                    if self.launching_patterns[self.current_timestamp][2] == 'move':
                        self.k = 5
                        self.k1 = 2
                    elif self.launching_patterns[self.current_timestamp][2] == 'line_ray':
                        self.launch_ray(player)
                    else:
                        for i in self.launching_patterns[self.current_timestamp][2]:
                            dx = cos(radians(i))
                            dy = sin(radians(i))
                            try:
                                v = self.launching_patterns[self.current_timestamp][3]
                                dx *= v
                                dy *= v
                            except IndexError:
                                pass
                            _bullets.append(
                                self.launching_patterns[self.current_timestamp][1](self.x, self.y, dx, dy, length=15, speed=1)
                                # LineBullet2((self.x, self.y), pygame.Vector2(1, 1))
                            )
                self.current_timestamp += 1
                _c = 0
                # print(Globals.get(ELAPSED_TIME_FOR_SOUNDTRACK))
                for i in self.launching_patterns:
                    if Globals.get(ELAPSED_TIME_FOR_SOUNDTRACK) > i[0]:
                        _c += 1
                        continue
                    else:
                        # _c = self.launching_patterns.index(i)
                        break
                # if self.current_timestamp != _c:
                #     _bullets.clear()
                self.current_timestamp = _c
        except IndexError:
            pass

        if _bullets:
            self.object_manager.add_multiple(_bullets)
            self.r = 20

        # print(self.current_enemy_timestamp)
        try:
            curr = self.enemy_launch_patterns[self.current_enemy_timestamp]
            if Globals.get(ELAPSED_TIME_FOR_SOUNDTRACK) > curr[0]:
                for i in range(len(curr[2])):
                    pos = curr[2][i]
                    target_pos = curr[3][i]
                    _enemies.append(
                        curr[1](pos, target_pos)
                    )
                self.current_enemy_timestamp += 1
                _c = 0
                for i in self.enemy_launch_patterns:
                    if Globals.get(ELAPSED_TIME_FOR_SOUNDTRACK) > i[0]:
                        _c += 1
                        continue
                    else:
                        # _c = self.enemy_launch_patterns.index(i)
                        break
                if self.current_enemy_timestamp != _c:
                    _enemies.clear()
                self.current_enemy_timestamp = _c
        except IndexError:
            pass

        if _enemies:
            self.object_manager.add_multiple(_enemies)
            self.r = 20

    def update(self, events: list[pygame.event.Event]):
        pass

    def draw(self, surf: pygame.Surface):
        pygame.draw.circle(surf, 'white', (self.x, self.y), self.r)
        pygame.draw.circle(surf, 'blue', (self.x, self.y), self.r, 2)


class QuadrilateralEnemy(Enemy):
    pass


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


class TriangleBullet1(BaseObject):
    def __init__(self, x=WIDTH // 2, y=HEIGHT // 2, dx=1.0, dy=1.0, speed=1.0, length=15):
        super().__init__()
        self.x = x
        self.y = y
        self.angle = math.degrees(math.atan2(dy, dx)) + 90
        self.length = length
        self.dx = dx * speed
        self.dy = dy * speed

    def check_collision(self, player: 'Player'):
        points = get_triangle(self.length, self.pos, self.angle)
        for i in range(len(points)):
            if player.rect.clipline(points[i % 3], points[(i + 1) % 3]):
                return True
        return False

    @property
    def pos(self):
        return self.x, self.y

    def update(self, events: list[pygame.event.Event]):
        self.x += self.dx
        self.y += self.dy

    def draw(self, surf: pygame.Surface):
        draw_triangle(surf, self.pos, length=self.length, angle=self.angle)
        draw_triangle(surf, self.pos, color=(255, 0, 0), length=self.length, angle=self.angle, width=2)


class TriangleLauncherOneTime(BaseObject):
    def __init__(self, pos, target_pos, length=15):
        super().__init__()
        self.pos = pygame.Vector2(pos)
        self.target_pos = pygame.Vector2(target_pos)
        self.angle = 0
        self.length = length

    def update(self, events: list[pygame.event.Event]):
        self.angle += 10
        self.angle %= 360
        _dx = (self.target_pos - self.pos)
        if _dx.length() < 3:
            self.pos = self.target_pos
        else:
            self.pos += _dx / 20
        if self.pos == self.target_pos:
            _bullets = []
            speed = 3
            offset = random.randint(-15, 15)
            for i in range(offset, 360 + offset, 30):
                dx = cos(radians(i)) * speed
                dy = sin(radians(i)) * speed
                _bullets.append(TriangleBullet1(self.pos.x, self.pos.y, dx, dy, length=10, speed=3))
            self.object_manager.add_multiple(_bullets)
            self.alive = False

    def draw(self, surf: pygame.Surface):
        draw_triangle(surf, self.pos, color=random.choice(['red', 'white']), length=self.length, angle=self.angle)
        # draw_triangle(surf, self.pos, color=(255, 0, 0), length=self.length, angle=self.angle, width=2)


class TriangleEnemy(Enemy):
    def __init__(self):
        super().__init__()
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.angle = 0
        self.done = False
        self.length = 50
        self.r = 50
        self.z = 1
        self.max_r = 35
        self.min_r = 20

        def get_triangle_beats(initial_time, dt=1.0, step=30, offset=10, speed=1.0, beats=1):
            return [
                [initial_time + i * dt, TriangleBullet1, range(offset * i, 360 + offset * i, step), speed] for i in range(beats)
            ]

        def get_one_by_one(initial_time, dt=1.0, step=30, speed=1.0, beats=1, offset_range=0):
            offset = random.randint(-offset_range, offset_range)
            return [
                [initial_time + i * dt, TriangleBullet1, [step * i + offset], speed] for i in range(beats)
            ]

        def get_all_range(step=0, offset=0):
            return range(offset, 360 + offset, step)

        def get_one_by_one_together_list(initial_time=0.0, dt=0.1, step=1, offset=1, vel=1.0, beats=1):
            _list = []
            for i in range(beats):
                a = [initial_time + dt * i, TriangleBullet1, get_all_range(step, offset * i), vel]
                _list.append(a)
            return _list

        self.launching_patterns = [
            # [1, TriangleBullet1, [1, 2, 3], 3],
            *get_triangle_beats(0, dt=0.9, step=45, offset=30, speed=3, beats=2),
            *get_triangle_beats(2, dt=0.9, step=45, offset=30, speed=3, beats=2),
            *get_triangle_beats(4, dt=0.9, step=45, offset=30, speed=3, beats=2),
            *get_triangle_beats(6, dt=0.9, step=45, offset=30, speed=3, beats=2),
            *get_triangle_beats(8, dt=0.9, step=30, offset=30, speed=3, beats=2),
            *get_triangle_beats(10, dt=0.9, step=30, offset=30, speed=3, beats=2),
            *get_triangle_beats(12, dt=0.9, step=45, offset=30, speed=3, beats=2),
            *get_triangle_beats(14, dt=0.9, step=45, offset=30, speed=3, beats=2),

            [16, TriangleBullet1, [-90], 5],
            [16.75, TriangleBullet1, [30], 6],
            [16.9, TriangleBullet1, [150], 6],

            *get_one_by_one(17.5, dt=0.05, step=30, speed=3, beats=10),

            [19, TriangleBullet1, 'all', 5],

            *get_one_by_one(20, dt=0.02, step=20, speed=7, beats=42, offset_range=15),
            *get_one_by_one(22, dt=0.02, step=20, speed=7, beats=42, offset_range=15),
            *get_one_by_one(24, dt=0.02, step=20, speed=7, beats=42, offset_range=15),
            *get_one_by_one(26, dt=0.02, step=20, speed=7, beats=42, offset_range=15),
            *get_one_by_one(28, dt=0.02, step=20, speed=7, beats=42, offset_range=15),
            *get_one_by_one(30, dt=0.02, step=20, speed=7, beats=42, offset_range=15),

            *get_one_by_one(32, dt=0.02, step=-20, speed=7, beats=42, offset_range=15),
            *get_one_by_one(34, dt=0.02, step=-20, speed=7, beats=42, offset_range=15),
            *get_one_by_one(36, dt=0.02, step=-20, speed=7, beats=42, offset_range=15),
            *get_one_by_one(38, dt=0.02, step=-20, speed=7, beats=42, offset_range=15),

            [48, None, 'rotate'],

            [50, TriangleBullet1, 'all', 5],
            [52, TriangleBullet1, 'all', 5],
            [54, TriangleBullet1, 'all', 5],
            [56, TriangleBullet1, 'all', 5],

            [56.25, None, 'rotate faster'],

            [58, TriangleBullet1, 'all', 7],
            [60, TriangleBullet1, 'all', 7],
            [62, TriangleBullet1, 'all', 7],
            [64, TriangleBullet1, 'all', 7],
            [66, TriangleBullet1, 'all', 7],

            # *get_one_by_one(67, dt=0.02, step=20, speed=5, beats=20, offset_range=15),
            *get_one_by_one_together_list(68, dt=0.1, step=120, offset=10, vel=5, beats=70),

            # [75, TriangleBullet1, 'all', 7],
            [76, TriangleBullet1, 'all', 7],
            [77, TriangleBullet1, 'all', 7],

        ]

        # self.launching_patterns.clear()

        def get_enemy_launchers_one_by_one(initial_time, dt, _type='top', count=2):
            offset = 50
            if _type == 'top':
                return [
                    [
                        initial_time + i * dt,
                        TriangleLauncherOneTime,
                        [self.pos],
                        [(WIDTH * (i + 1) / (count + 1), offset)]
                    ] for i in range(count)
                ]
            elif _type == 'bottom':
                return [
                    [
                        initial_time + i * dt,
                        TriangleLauncherOneTime,
                        [self.pos],
                        [(WIDTH * (i + 1) / (count + 1), HEIGHT - offset)]
                    ] for i in range(count)
                ]
            elif _type == 'left':
                return [
                    [
                        initial_time + i * dt,
                        TriangleLauncherOneTime,
                        [self.pos],
                        [(offset, HEIGHT * (i + 1) / (count + 1))]
                    ] for i in range(count)
                ]
            elif _type == 'right':
                return [
                    [
                        initial_time + i * dt,
                        TriangleLauncherOneTime,
                        [self.pos],
                        [(WIDTH - offset, HEIGHT * (i + 1) / (count + 1))]
                    ] for i in range(count)
                ]
            else:
                return []

        self.enemy_launch_patterns = [
            # [1, TriangleLauncherOneTime, [(0, 0)], [(150, 150)]],
            # [5, TriangleLauncherOneTime, [(0, 0)], [(150, 150)]],
            *get_enemy_launchers_one_by_one(40, 0.2, 'top', 5),
            *get_enemy_launchers_one_by_one(42, 0.2, 'bottom', 5),
            *get_enemy_launchers_one_by_one(44, 0.2, 'left', 5),
            *get_enemy_launchers_one_by_one(46, 0.2, 'right', 5),

        ]

        self.current_enemy_timestamp = 0
        self.current_timestamp = 0

        self.angle_k = 0

    @property
    def pos(self):
        return self.x, self.y

    @property
    def points(self):
        return get_triangle(self.length, self.pos, self.angle)

    def use_ai(self, player: 'Player'):
        self.length *= 0.95
        self.length = clamp(self.length, 25, 50)
        self.r *= 0.95
        self.r = clamp(self.r, self.min_r, self.max_r)
        self.angle += self.angle_k
        self.angle %= 360

        _bullets = []
        _enemies = []
        try:
            if Globals.get(ELAPSED_TIME_FOR_SOUNDTRACK) > self.launching_patterns[self.current_timestamp][0]:
                if self.launching_patterns[self.current_timestamp][2] == 'all':
                    for i in [0, 120, 240]:
                        i = i - 90 + self.angle
                        dx = cos(radians(i))
                        dy = sin(radians(i))
                        try:
                            v = self.launching_patterns[self.current_timestamp][3]
                            dx *= v
                            dy *= v
                        except IndexError:
                            pass
                        _bullets.append(
                            self.launching_patterns[self.current_timestamp][1](self.x, self.y, dx, dy)
                        )
                else:
                    if self.launching_patterns[self.current_timestamp][2] == 'rotate':
                        self.angle_k = 1
                        # self.k = 5
                        # self.k1 = 2
                    elif self.launching_patterns[self.current_timestamp][2] == 'rotate faster':
                        self.angle_k += 2
                    else:
                        for i in self.launching_patterns[self.current_timestamp][2]:
                            # i = self.angle + 120 * (i - 1) - 90
                            # i += self.angle
                            dx = cos(radians(i))
                            dy = sin(radians(i))
                            try:
                                v = self.launching_patterns[self.current_timestamp][3]
                                dx *= v
                                dy *= v
                            except IndexError:
                                pass
                            _bullets.append(
                                self.launching_patterns[self.current_timestamp][1](self.x, self.y, dx, dy, length=10)
                                # LineBullet2((self.x, self.y), pygame.Vector2(1, 1))
                            )
                self.current_timestamp += 1
                _c = 0
                # print(Globals.get(ELAPSED_TIME_FOR_SOUNDTRACK))
                for i in self.launching_patterns:
                    if Globals.get(ELAPSED_TIME_FOR_SOUNDTRACK) > i[0]:
                        _c += 1
                        continue
                    else:
                        # _c = self.launching_patterns.index(i)
                        break
                # if self.current_timestamp != _c:
                #     _bullets.clear()
                self.current_timestamp = _c
        except IndexError:
            pass

        if _bullets:
            self.object_manager.add_multiple(_bullets)
            self.length = 50
            self.r = self.max_r

        # print(self.current_enemy_timestamp)
        try:
            curr = self.enemy_launch_patterns[self.current_enemy_timestamp]
            if Globals.get(ELAPSED_TIME_FOR_SOUNDTRACK) > curr[0]:
                for i in range(len(curr[2])):
                    pos = curr[2][i]
                    target_pos = curr[3][i]
                    _enemies.append(
                        curr[1](pos, target_pos)
                    )
                self.current_enemy_timestamp += 1
                _c = 0
                for i in self.enemy_launch_patterns:
                    if Globals.get(ELAPSED_TIME_FOR_SOUNDTRACK) > i[0]:
                        _c += 1
                        continue
                    else:
                        # _c = self.enemy_launch_patterns.index(i)
                        break
                if self.current_enemy_timestamp != _c:
                    _enemies.clear()
                self.current_enemy_timestamp = _c
        except IndexError:
            pass

        if _enemies:
            self.object_manager.add_multiple(_enemies)
            self.length = 50
            self.r = self.max_r

    def draw(self, surf: pygame.Surface):
        # pygame.draw.circle(surf, 'white', self.pos, self.r)
        # pygame.draw.circle(surf, 'red', self.pos, self.r, 2)
        draw_triangle(surf, self.pos, length=self.length, angle=self.angle)
        draw_triangle(surf, self.pos, color=(255, 0, 0), length=self.length, angle=self.angle, width=3)


class ObjectManager:
    def __init__(self):
        self.objects: list[BaseObject] = []
        self._to_add: list[BaseObject] = []
        self.player = None
        self.player_pos = [0, 0]
        self.collision_enabled = True

    def get_object_count(self, instance):
        c = 0
        for i in self.objects:
            if type(i) == instance:
                c += 1
        return c

    def clear_only_objects(self):
        self._to_add.clear()
        self.objects.clear()

    def clear(self):
        self._to_add.clear()
        self.objects.clear()
        if self.player:
            self.player_pos = [self.player.x, self.player.y]
        self.player = None

    def init(self):
        self.clear()
        if not self.player:
            self.player = Player(WIDTH // 2, HEIGHT // 2 + 150)
        else:
            self.player = Player(*self.player_pos)

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
            # TODO collisions
            if self.collision_enabled:
                if i.check_collision(self.player):
                    self.player.alive = False
            if isinstance(i, Enemy):
                i.use_ai(self.player)
            else:
                i.update(events)
        if self.player:
            self.player.update(events)

    def draw(self, surf: pygame.Surface):
        for i in self.objects:
            i.draw(surf)
        if self.player:
            self.player.draw(surf)
