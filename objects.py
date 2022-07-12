import random

import pygame.event
from utils import clamp, map_to_range, Timer
from config import WIDTH, HEIGHT, Globals
from operator import attrgetter
from math import sin, cos, radians, degrees, atan2
from typing import Union
from constants import *

import json


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
    def __init__(self, x=WIDTH // 2, y=HEIGHT // 2, dx=1.0, dy=1.0):
        super().__init__()
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.speed = 2
        self.r = 5

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

        def get_one_by_one_range_list(initial_time=0.0, dt=0.1, step=1, offset=0, vel=1):
            _list = [[initial_time + dt * i, [i], vel] for i in get_all_range(step=step, offset=offset)]
            # print(_list)
            return _list

        def get_ony_by_one_together_list1(initial_time=0.0, dt=0.1, step=1, offset=0, vel=1, directions=1):
            # _list = [[initial_time + dt * i, [j for j in range(i, 360 + i, 360 // directions)], vel] for i in get_all_range(step=step, offset=offset)]
            # return _list
            _list = []
            # for i in range()

        def get_one_by_one_together_list(initial_time=0.0, dt=0.1, step=1, offset=1, vel=1, beats=1):
            _list = []
            for i in range(beats):
                a = [initial_time + dt * i, get_all_range(step, offset * i), vel]
                _list.append(a)
            return _list

        def get_range_list(initial_time=0.0, dt=0.1, step=0, offset=0, vel=1, beats=1):
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
            *get_one_by_one_together_list(44, dt=0.1, step=45, offset=5, vel=2, beats=60),

            *get_one_by_one_together_list(51.5, dt=0.1, step=45, offset=-5, vel=2, beats=60),
        ]
        self.current_timestamp = 0

        # self.object_launchers

    def use_ai(self, player: 'Player'):
        super().use_ai(player)
        if self.phase_timer.tick:
            self.phase += 1
        _bullets = []
        if self.phase >= 6:
            if self.alive:
                self.alive = False
            return
        # self.phase = 0
        if self.phase % 2 == 0:
            self.phase_timer.timeout = 5
            if self.phase == 0:
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
                        print(Globals.get(ELAPSED_TIME_FOR_SOUNDTRACK))
                        for i in self.launching_patterns:
                            if Globals.get(ELAPSED_TIME_FOR_SOUNDTRACK) > i[0]:
                                continue
                            else:
                                _c = self.launching_patterns.index(i)
                                break
                        self.current_timestamp = _c
                except IndexError:
                    pass

                # if self.bullet_timer.tick:
                #     for i in range(0, 360, 30):
                #         dx = cos(radians(i))
                #         dy = sin(radians(i))
                #         _bullets.append(
                #             PointBullet(self.x, self.y, dx, dy)
                #         )
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


# TODO


class TriangleBullet(BaseObject):
    COLOUR = "RED"
    BORDER_COLOUR = "WHITE"
    SIDE_LENGTH = 10
    BORDER_WIDTH = 2

    def __init__(self, c_pos, enemy_dir, vel, angular_vel):
        super().__init__()
        self.c_pos = c_pos
        self._dir = enemy_dir.rotate(90)
        self.vel = vel
        self.angular_vel = angular_vel
        self.vers = []
        self.generate_vertices()

    def generate_vertices(self):
        vec1 = pygame.Vector2(0, -self.SIDE_LENGTH)
        vec2 = pygame.Vector2(0, -self.SIDE_LENGTH - self.BORDER_WIDTH)
        self.vers = [
            vec1,
            vec1.rotate(120),
            vec1.rotate(240),
            vec2,
            vec2.rotate(120),
            vec2.rotate(240),
        ]

    def update(self, events: list[pygame.event.Event]):
        for vec in self.vers:
            vec.rotate_ip(self.angular_vel)
            vec.xy += self._dir * self.vel

    def draw(self, surf: pygame.Surface):
        pygame.draw.polygon(surf, self.BORDER_COLOUR, [self.c_pos + vec for vec in self.vers[3:]])
        pygame.draw.polygon(surf, self.COLOUR, [self.c_pos + vec for vec in self.vers[:3]])


class TriangleEnemy(Enemy):
    ANGULAR_VEL = 5
    VEL = 5
    COLOUR = "RED"
    BORDER_COLOUR = "WHITE"
    SIDE_LENGTH = 40
    BORDER_WIDTH = 5

    def __init__(self):
        super().__init__()
        self.path_vers = []
        self.screen_centre = pygame.Vector2(WIDTH // 2, HEIGHT // 2)
        self.c_pos = pygame.Vector2(self.screen_centre)
        self.phase = 0
        self.phase_timer = Timer(10)
        self.bullet_timer = Timer(0.5)
        self.vers = self.generate_vertices(self.SIDE_LENGTH, self.BORDER_WIDTH)
        self.launched_triangles = []
        self.path_target = 0
        self.max_bullets = 20

    @staticmethod
    def generate_vertices(side_length, border_width):
        vec1 = pygame.Vector2(0, -side_length)
        vec2 = pygame.Vector2(0, -side_length - border_width)
        vers = [
            vec1,
            vec1.rotate(120),
            vec1.rotate(240),
            vec2,
            vec2.rotate(120),
            vec2.rotate(240),
        ]
        return vers

    def use_ai(self, player: 'Player'):
        super().use_ai(player)
        for vec in self.vers:
            vec.rotate_ip(self.ANGULAR_VEL)

        if self.phase_timer.tick:
            self.phase += 1
            if self.phase > 2:
                self.phase = 0
            if self.phase == 2:
                self.path_vers = self.generate_vertices(200, 0)[:3]
                self.max_bullets = 1000
            else:
                self.max_bullets = 20
                self.c_pos = pygame.Vector2(self.screen_centre)

            for bullets in self.launched_triangles:
                bullets.alive = False
            self.launched_triangles = []

        if self.bullet_timer.tick:
            if len(self.launched_triangles) < self.max_bullets:
                for vec in self.vers[:3]:
                    if self.phase == 0:
                        temp = TriangleBullet(self.c_pos + vec, vec, 0.3, 2)
                    elif self.phase == 1:
                        temp = TriangleBullet(self.c_pos + vec, vec, 0.3, 5)
                    elif self.phase == 2:
                        temp = TriangleBullet(self.c_pos + vec, vec, 0.3, 0)
                    else:
                        temp = TriangleBullet(self.c_pos + vec, vec, 0.3, 0)
                    self.object_manager.add(
                        temp
                    )
                    self.launched_triangles.append(temp)

        if self.phase == 2:
            self.c_pos.move_towards_ip(self.screen_centre + self.path_vers[self.path_target], self.VEL)
            if self.c_pos == self.screen_centre + self.path_vers[self.path_target]:
                self.path_target += 1
                if self.path_target > 2:
                    self.path_target = 0

    def update(self, events: list[pygame.event.Event]):
        pass

    def draw(self, surf: pygame.Surface):
        pygame.draw.polygon(surf, self.BORDER_COLOUR, [self.c_pos + vec for vec in self.vers[3:]])
        pygame.draw.polygon(surf, self.COLOUR, [self.c_pos + vec for vec in self.vers[:3]])


# TODO


class ObjectManager:
    def __init__(self):
        self.objects: list[BaseObject] = []
        self._to_add: list[BaseObject] = []
        self.player = None
        self.player_pos = [0, 0]

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
            # if i.check_collision(self.player):
            #     self.player.alive = False
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
