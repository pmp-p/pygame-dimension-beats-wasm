import random
import sys

from objects import *
from sounds import SoundManager
from subtitles import SubtitleManager, Subtitle, get_typed_subtitles
from transition import TransitionManager


class Menu:
    """
    Base signature for all menus
    """

    def __init__(self, manager: 'MenuManager', name='menu'):
        self.manager = manager
        self.name = name
        self.background = 'black'
        self.manager.subtitle_manager.clear()
        self.manager.object_manager.clear()
        Globals.set(PREVIOUS_LEVEL, Globals.get(CURRENT_LEVEL))
        Globals.set(CURRENT_LEVEL, self.name)

    def reset(self):
        self.__init__(self.manager, self.name)

    def update(self, events: list[pygame.event.Event]):
        pass

    def draw(self, surf: pygame.Surface):
        surf.fill(self.background)
        pygame.draw.rect(surf, 'white', surf.get_rect().inflate(-20, -200).move(0, 100 - 10), 3)
        # pygame.draw.rect(surf, 'white', surf.get_rect().inflate(-20, -HEIGHT + 170).move(0, -HEIGHT // 2 + 95), 3)
        surf.blit(text(self.name, size=100, aliased=False), (50, 50))


class Home(Menu):
    def __init__(self, manager: 'MenuManager', name='menu'):
        super().__init__(manager, name)
        self.options = [
            'quit', 'help', 'settings', 'credits', 'play'
        ]
        self.manager.transition_manager.set_transition('fade')

        self.actions = [
            lambda: self.manager.switch_mode('quit'),
            lambda: self.manager.switch_mode('help', transition=True),
            lambda: self.manager.switch_mode('settings', transition=True),
            lambda: self.manager.switch_mode('credits', transition=True),
            lambda: self.manager.switch_mode('level-select', transition=True)
        ]
        self.selected = 0

    def update(self, events: list[pygame.event.Event]):
        # self.manager.switch_mode('credits')
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_DOWN:
                    self.selected += 1
                    self.selected %= len(self.options)
                    self.manager.sound_manager.play_sound('ping')
                if e.key == pygame.K_UP:
                    self.selected -= 1
                    self.selected %= len(self.options)
                    self.manager.sound_manager.play_sound('ping')
                if e.key == pygame.K_RETURN or e.key == pygame.K_KP_ENTER:
                    try:
                        self.manager.transition_manager.set_transition('fade')
                        self.actions[self.selected]()
                    except IndexError:
                        pass
                        # self.manager.switch_mode('game', reset=True, transition=False)

    def draw(self, surf: pygame.Surface):
        super().draw(surf)
        for i in range(len(self.options)):
            y = 200 + i * 75
            surf.blit(text(self.options[i], 50, 'orange' if i == self.selected else 'white'), (100, y))


class LevelSelect(Menu):
    def __init__(self, manager: 'MenuManager', name='menu'):
        super().__init__(manager, name)
        self.options = [
            'point', 'line', 'triangle'
        ]
        self.manager.transition_manager.set_transition('fade')

        self.selected = 0

    def play(self):
        Globals.set(FIRST_TIME_PLAYED, True)
        Globals.set(UPCOMING_LEVEL, self.options[self.selected])
        self.manager.transition_manager.set_transition('fade')
        self.manager.switch_mode('level-intro', transition=True)

    def update(self, events: list[pygame.event.Event]):
        # self.manager.switch_mode('credits')
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_DOWN:
                    self.selected += 1
                    self.selected %= len(self.options)
                    self.manager.sound_manager.play_sound('ping')
                if e.key == pygame.K_UP:
                    self.selected -= 1
                    self.selected %= len(self.options)
                    self.manager.sound_manager.play_sound('ping')
                if e.key == pygame.K_RETURN or e.key == pygame.K_KP_ENTER:
                    try:
                        self.manager.transition_manager.set_transition('fade')
                        self.play()
                    except IndexError:
                        pass

    def draw(self, surf: pygame.Surface):
        surf.fill(self.background)
        pygame.draw.rect(surf, 'white', surf.get_rect().inflate(-20, -200).move(0, 100 - 10), 3)
        surf.blit(text("Select Level", size=100, aliased=False), (50, 50))
        for i in range(len(self.options)):
            y = 200 + i * 75
            surf.blit(text(self.options[i], 50, 'orange' if i == self.selected else 'white'), (100, y))


class Credits(Menu):
    def __init__(self, manager: 'MenuManager', name='menu'):
        super().__init__(manager, name)
        self.options = [
            'spooky', 'mrpoly', 'captain', 'tank king', "pygame"
        ]
        self.credits = [
            'He made amazing soundtracks!', 'we used their cool soundtrack!', 'programmed random stuff', 'programmed other random stuff',
            "obviously!"
        ]
        self.manager.transition_manager.set_transition('fade')

        self.actions = [
            lambda: self.link('https://okno.itch.io'),
            lambda: self.link('https://opengameart.org/users/mrpoly'),
            lambda: self.link(''),
            lambda: self.link('https://tank-king.itch.io'),
        ]
        self.selected = 0
        self.display_credits()

    def display_credits(self, _credits=None):
        if not _credits:
            _credits = self.credits[self.selected]
        self.manager.subtitle_manager.clear()
        for i in get_typed_subtitles(_credits, _time=99, pos=(WIDTH // 2, HEIGHT - 50)):
            self.manager.subtitle_manager.add(i)

    def link(self, _link):
        if _link:
            try:
                import webbrowser
                webbrowser.open(_link)
                self.display_credits('Link opened in Browser')
            except Exception as e:
                print(e)
                self.display_credits('An Error Occurred')
        else:
            self.display_credits('No contact info for this person')

    def update(self, events: list[pygame.event.Event]):
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_DOWN:
                    self.selected += 1
                    self.selected %= len(self.options)
                    self.manager.sound_manager.play_sound('ping')
                    self.display_credits()
                if e.key == pygame.K_UP:
                    self.selected -= 1
                    self.selected %= len(self.options)
                    self.manager.sound_manager.play_sound('ping')
                    self.display_credits()
                if e.key == pygame.K_RETURN or e.key == pygame.K_KP_ENTER:
                    try:
                        self.manager.transition_manager.set_transition('fade')
                        self.actions[self.selected]()
                    except IndexError:
                        self.manager.switch_mode('game', reset=True, transition=False)

    def draw(self, surf: pygame.Surface):
        super().draw(surf)
        for i in range(len(self.options)):
            y = 200 + i * 60
            surf.blit(text(self.options[i], 50, 'orange' if i == self.selected else 'white'), (100, y))


class Quit(Menu):
    def __init__(self, manager, name):
        super().__init__(manager, name)
        if Globals.get(FIRST_TIME_PLAYED):
            sys.exit(0)
        else:
            _text = random.choice(
                [
                    'Play The Game First Idiot!',
                    'First Play The Game You Noob!',
                    'Just Play The Game!',
                    'Select the Play option idiot!',
                    'not until you play you noob!',
                    'you need to play at least once',
                    'find a way other than playing',
                ]
            )

            for i in range(len(_text)):
                self.manager.subtitle_manager.add(
                    Subtitle(
                        ''.join(_text[0:i + 1]),
                        time=0.05 if i != len(_text) - 1 else 2
                    )
                )

    def update(self, events: list[pygame.event.Event]):
        manager = self.manager.subtitle_manager
        if not manager.subtitles and not manager.current_subtitle:
            self.manager.switch_mode('home', reset=False, transition=True)

    def draw(self, surf: pygame.Surface):
        super().draw(surf)


class Help(Menu):
    def draw(self, surf: pygame.Surface):
        _text = [
            'WASD or arrows to move',
            'hold shift to move faster',
            'e to toggle difficulty',
            'f to toggle fullscreen',
            'escape to go back'
        ]
        super().draw(surf)
        t = text('We dont do that here but...', size=35)
        surf.blit(t, t.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50)))
        y = HEIGHT // 2
        for i in _text:
            t = text(i, size=25)
            surf.blit(t, t.get_rect(center=(WIDTH // 2, y)))
            y += 50


class Intro(Menu):
    def __init__(self, manager: 'MenuManager', name='menu'):
        super().__init__(manager, name)
        _text = [
            'What is Dimensions ?',
            'Some another random line',
            'One more',
            'yea one more',
            'XDXD'
        ]
        _subtitles = []
        for i in _text:
            # _subtitles.append(Subtitle(i, 1))
            for j in get_typed_subtitles(i, 1):
                self.manager.subtitle_manager.add(j)

    def update(self, events: list[pygame.event.Event]):
        pass

    def draw(self, surf: pygame.Surface):
        surf.fill(self.background)


class LevelIntro(Menu):
    def __init__(self, manager: 'MenuManager', name='menu'):
        super().__init__(manager, name)
        self.upcoming_level = Globals.get(UPCOMING_LEVEL)
        if not self.upcoming_level:
            self.upcoming_level = 'undefined'

        self.callback = None

        # def callback():
        #     self.callback = True
        #     self.manager.subtitle_manager.add(Subtitle(self.upcoming_level, 3, 50))

        # self.manager.subtitle_manager.add(
        #     Subtitle(self.upcoming_level, 3, 50, callback=callback)
        # )
        self.text = text(self.upcoming_level, size=50)
        self.timer = Timer(3)

    def update(self, events: list[pygame.event.Event]):
        if self.timer.tick:
            self.callback = True
        if self.callback:
            Globals.set(UPCOMING_LEVEL, '')
            self.manager.transition_manager.set_transition('fade')
            self.manager.switch_mode(self.upcoming_level, transition=True)
            self.callback = None

    def draw(self, surf: pygame.Surface):
        surf.fill(self.background)
        surf.blit(self.text, self.text.get_rect(center=(WIDTH // 2, HEIGHT // 2)))


class Retry(Menu):
    def __init__(self, manager: 'MenuManager', name='menu'):
        super().__init__(manager, name)
        message = Globals.get(RETRY_MESSAGE) or ''
        # self.manager.subtitle_manager.add(
        #     Subtitle(message + '', time='inf', pos=(WIDTH // 2, 100))
        # )
        for i in get_typed_subtitles(message, _time='inf', pos=(WIDTH // 2, 150), callback=lambda: Globals.set(RETRY_MESSAGE, '')):
            self.manager.subtitle_manager.add(i)
        self.input_enabled = True
        self.message = 'Retry ?'
        self.options = ['Yes', 'No']

        def go_prev():
            self.manager.transition_manager.set_transition('fade')
            self.manager.switch_mode(Globals.get(PREVIOUS_LEVEL), transition=True)

        def go_main_menu():
            self.manager.transition_manager.set_transition('fade')
            self.manager.switch_mode('home', transition=True)

        self.actions = [go_prev, go_main_menu]
        self.selected = 0

    def update(self, events: list[pygame.event.Event]):
        if Globals.get(RETRY_MESSAGE) == '':
            self.input_enabled = True
        if self.input_enabled:
            for e in events:
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_LEFT:
                        self.selected -= 1
                        self.selected %= len(self.options)
                    if e.key == pygame.K_RIGHT:
                        self.selected += 1
                        self.selected %= len(self.options)
                    if e.key == pygame.K_RETURN:
                        try:
                            self.manager.subtitle_manager.clear()
                            self.actions[self.selected]()
                        except IndexError:
                            pass

    def draw(self, surf: pygame.Surface):
        surf.fill(self.background)
        t = text(self.message)
        surf.blit(t, t.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
        x1 = WIDTH / 4
        x2 = WIDTH * 3 / 4
        t = text(self.options[0], color='orange' if self.selected == 0 else 'white')
        surf.blit(t, t.get_rect(center=(x1, HEIGHT // 2 + 150)))
        t = text(self.options[1], color='orange' if self.selected == 1 else 'white')
        surf.blit(t, t.get_rect(center=(x2, HEIGHT // 2 + 150)))


class PointEnemyScene(Menu):
    def __init__(self, manager: 'MenuManager', name='menu'):
        super().__init__(manager, name)
        self.manager.object_manager.init()
        self.manager.object_manager.add(PointEnemy())
        # self.manager.object_manager.add(PointSpreadBullet(target_pos=(WIDTH // 2, 150)))
        self.manager.sound_manager.stop()
        self.manager.sound_manager.play('points', start=0)
        self.theme_color = 'red'

    def update(self, events: list[pygame.event.Event]):
        try:
            if not self.manager.object_manager.player.alive:
                # print(self.name)
                # self.reset()
                Globals.set(RETRY_MESSAGE, 'Press E to play in easy mode')
                self.manager.transition_manager.set_transition(random.choice(['square', 'circle']))
                self.manager.switch_mode('retry', reset=True, transition=True)
                self.manager.sound_manager.fade(500)
            try:
                if Globals.get(ELAPSED_TIME_FOR_SOUNDTRACK) > Globals.get(TOTAL_DURATION_OF_SOUNDTRACK):
                    Globals.set(UPCOMING_LEVEL, 'line')
                    self.manager.transition_manager.set_transition('fade')
                    self.manager.switch_mode('level-intro', transition=True)
            except TypeError:
                pass
        except AttributeError:
            pass
        # if not self.manager.object_manager.objects:
        #     self.manager.switch_mode('line')

    def draw(self, surf: pygame.Surface):
        surf.fill(self.background)
        length = 400
        total_time = self.manager.sound_manager.total_length
        if total_time == 0:
            total_time = length
        try:
            t = self.manager.sound_manager.elapsed_time
            t = map_to_range(t, 0, total_time, 0, length)
            pygame.draw.rect(surf, '#00AAFF', (WIDTH // 2 - length // 2, 20, t, 10))
            pygame.draw.rect(surf, '#FFFFFF', (WIDTH // 2 - length // 2, 20, length, 10), 2)
        except ZeroDivisionError:
            pass
        # surf.blit(text(self.manager.sound_manager.elapsed_time.__str__()), (0, 0))


class LineEnemyScene(Menu):
    def __init__(self, manager: 'MenuManager', name='menu'):
        super().__init__(manager, name)
        self.manager.object_manager.init()
        self.manager.object_manager.add(LineEnemy())
        self.manager.sound_manager.stop()
        self.manager.sound_manager.play('lines', start=0)
        self.theme_color = 'blue'
        # self.background = (0, 0, 5)

    def update(self, events: list[pygame.event.Event]):
        try:
            if not self.manager.object_manager.player.alive:
                Globals.set(RETRY_MESSAGE, 'Press E to play in easy mode')
                self.manager.transition_manager.set_transition(random.choice(['square', 'circle']))
                self.manager.switch_mode('retry', reset=True, transition=True)
                self.manager.sound_manager.fade(500)
        except AttributeError:
            pass
        try:
            if Globals.get(ELAPSED_TIME_FOR_SOUNDTRACK) > Globals.get(TOTAL_DURATION_OF_SOUNDTRACK):
                Globals.set(UPCOMING_LEVEL, 'triangle')
                self.manager.transition_manager.set_transition('fade')
                self.manager.switch_mode('level-intro', transition=True)
        except TypeError:
            pass

    def draw(self, surf: pygame.Surface):
        surf.fill(self.background)
        length = 400
        total_time = self.manager.sound_manager.total_length
        if total_time == 0:
            total_time = length
        # print(total_time)
        try:
            t = self.manager.sound_manager.elapsed_time
            t = map_to_range(t, 0, total_time, 0, length)
            pygame.draw.rect(surf, '#0055FF', (WIDTH // 2 - length // 2, 20, t, 10))
            pygame.draw.rect(surf, '#FFFFFF', (WIDTH // 2 - length // 2, 20, length, 10), 2)
        except ZeroDivisionError:
            pass
        # surf.blit(text(self.manager.sound_manager.elapsed_time.__str__()), (0, 0))


class TriangleEnemyScene(Menu):
    def __init__(self, manager: 'MenuManager', name='menu'):
        super().__init__(manager, name)
        self.manager.object_manager.init()
        self.manager.object_manager.add(TriangleEnemy())
        self.manager.sound_manager.stop()
        self.manager.sound_manager.play('triangles', start=0)

    def update(self, events: list[pygame.event.Event]):
        try:
            if not self.manager.object_manager.player.alive:
                Globals.set(RETRY_MESSAGE, 'Press E to play in easy mode')
                self.manager.transition_manager.set_transition(random.choice(['square', 'circle']))
                self.manager.switch_mode('retry', reset=True, transition=True)
                self.manager.sound_manager.fade(500)
        except AttributeError:
            pass
        try:
            if Globals.get(ELAPSED_TIME_FOR_SOUNDTRACK) > Globals.get(TOTAL_DURATION_OF_SOUNDTRACK):
                self.manager.transition_manager.set_transition('fade')
                self.manager.switch_mode('credits', transition=True)
        except TypeError:
            pass
        try:
            if Globals.get(ELAPSED_TIME_FOR_SOUNDTRACK) > Globals.get(TOTAL_DURATION_OF_SOUNDTRACK) - 0.5:
                self.manager.sound_manager.fade(500)
        except TypeError:
            pass

    def draw(self, surf: pygame.Surface):
        surf.fill(self.background)
        length = 400
        total_time = self.manager.sound_manager.total_length
        if total_time == 0:
            total_time = length
        # print(total_time)
        try:
            t = self.manager.sound_manager.elapsed_time
            t = map_to_range(t, 0, total_time, 0, length)
            pygame.draw.rect(surf, '#0055FF', (WIDTH // 2 - length // 2, 20, t, 10))
            pygame.draw.rect(surf, '#FFFFFF', (WIDTH // 2 - length // 2, 20, length, 10), 2)
        except ZeroDivisionError:
            pass
        # surf.blit(text(self.manager.sound_manager.elapsed_time.__str__()), (0, 0))


class QuadrilateralEnemyScene(Menu):
    def __init__(self, manager: 'MenuManager', name='menu'):
        super().__init__(manager, name)
        self.manager.object_manager.init()
        self.manager.object_manager.add(LineEnemy())

    def update(self, events: list[pygame.event.Event]):
        if not self.manager.object_manager.objects:
            self.manager.switch_mode('home')

    def draw(self, surf: pygame.Surface):
        surf.fill(self.background)


class Settings(Menu):
    G_ACC = (0, 10)
    PIN_RAD = 10
    PIN_BORDER_WIDTH = 2
    PIN_COLOR = "BROWN"
    PIN_HOVER_COLOR = "BLUE"
    PIN_CLICK_COLOR = "GREEN"
    PIN_BORDER_COLOR = "WHITE"
    CREDIT_TEXT_GAP = 40
    CREDIT_TEXT_POSY = 150

    def __init__(self, manager, name):
        super().__init__(manager, name)
        self.notice_acc = pygame.Vector2(self.G_ACC)
        self.notice_vel = pygame.Vector2(0, 0)
        self.notice_pos = pygame.Vector2(WIDTH // 2, HEIGHT // 2)
        self.notice_rect = pygame.Rect((0, 0), (2.2 * WIDTH // 3, 2.2 * HEIGHT // 3))
        self.text = text("Under Maintenance!")
        self.text_rect = self.text.get_rect()
        self.text_rect.center = self.notice_rect.center = self.notice_pos
        self.credit_texts = [
            text("You found the Easter Egg!", 30),
            text("Thank You for trying out the game!", 30),
            text("If you liked playing this", 30),
            text("Please Rate Us for the jam!", 30),
        ]
        self.credit_text_rects = [
            self.credit_texts[i].get_rect(
                center=(self.notice_pos.x, self.CREDIT_TEXT_POSY + self.CREDIT_TEXT_GAP * i)
            ) for i in range(len(self.credit_texts))
        ]
        # self.image = pygame.transform.scale(pygame.image.load("logo.png"), (200, 200))
        self.image = load_image(os.path.join(ASSETS, 'images', 'logo.png'), scale=0.3)
        self.image_rect = self.image.get_rect(center=(self.notice_pos.x, 400))
        self.pins = [
            self.notice_rect.topleft,
            self.notice_rect.topright,
            self.notice_rect.bottomleft,
            self.notice_rect.bottomright
        ]
        self.pin_state = [0, 0, 0, 0]  # 1 -> hover, 2 -> clicked
        self.pin_to_del: Union[int, None] = None

    def update(self, events: list[pygame.event.Event]):
        dt = 0.16
        if self.pin_to_del is not None:
            v = self.pins[self.pin_to_del]
            self.pins.pop(self.pin_to_del)
            self.pin_state.pop(self.pin_to_del)
            self.pin_to_del = None
            self.manager.object_manager.add(PointClicked(*v))

        if len(self.pins) == 0 and self.notice_rect.top <= WIDTH:
            self.notice_vel += self.notice_acc * dt
            self.notice_pos += self.notice_vel * dt
            self.text_rect.center = self.notice_rect.center = self.notice_pos

        for ev in events:
            if ev.type == pygame.MOUSEMOTION:
                for i in range(len(self.pins)):
                    if pygame.Vector2(self.pins[i]).distance_squared_to(pygame.mouse.get_pos()) <= self.PIN_RAD ** 2:
                        self.pin_state[i] = 1
                    else:
                        self.pin_state[i] = 0

            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                for i in range(len(self.pins)):
                    if pygame.Vector2(self.pins[i]).distance_squared_to(pygame.mouse.get_pos()) <= self.PIN_RAD ** 2:
                        self.pin_state[i] = 2
                        self.pin_to_del = i

    def draw(self, surf: pygame.Surface):
        surf.fill(0)
        surf.blit(self.image, self.image_rect)
        for i in range(len(self.credit_texts)):
            surf.blit(self.credit_texts[i], self.credit_text_rects[i])
        if self.notice_rect.top <= WIDTH:
            pygame.draw.rect(surf, "BLACK", self.notice_rect)
            pygame.draw.rect(surf, "WHITE", self.notice_rect, width=2)
            surf.blit(self.text, self.text_rect)
        for i in range(len(self.pins)):
            pygame.draw.circle(surf, self.PIN_BORDER_COLOR, self.pins[i], self.PIN_RAD + self.PIN_BORDER_WIDTH)
            if self.pin_state[i] == 0:
                pygame.draw.circle(surf, self.PIN_COLOR, self.pins[i], self.PIN_RAD)
            if self.pin_state[i] == 1:
                pygame.draw.circle(surf, self.PIN_HOVER_COLOR, self.pins[i], self.PIN_RAD)
            if self.pin_state[i] == 2:
                pygame.draw.circle(surf, self.PIN_CLICK_COLOR, self.pins[i], self.PIN_RAD)


class MenuManager:
    # TODO implement StackBasedGameLoop

    def __init__(self):
        self.to_switch = 'none'  # to switch menu after transition
        self.to_reset = False
        self.transition_manager: TransitionManager = TransitionManager()
        self.subtitle_manager: SubtitleManager = SubtitleManager()
        self.object_manager: ObjectManager = ObjectManager()
        self.sound_manager = SoundManager()
        self.menus = {
            'home': Home(self, 'home'),
            'intro': Intro(self, 'intro'),
            'quit': Quit(self, 'quit'),
            'help': Help(self, 'help'),
            'settings': Settings(self, 'settings'),
            'credits': Credits(self, 'credits'),

            'level-select': LevelSelect(self, 'level-select'),
            'level-intro': LevelIntro(self, 'level-intro'),
            'retry': Retry(self, 'retry'),

            'point': PointEnemyScene(self, 'point'),
            'line': LineEnemyScene(self, 'line'),
            'triangle': TriangleEnemyScene(self, 'triangle')
        }
        self.subtitle_manager.clear()
        self.object_manager.clear()
        self.mode = 'home'  # initial mode
        self.menu = self.menus[self.mode]
        self.sound_manager.stop()
        self.menu.reset()

    def reset(self):
        self.__init__()

    def switch_mode(self, mode, reset=True, transition=False):
        if mode in self.menus:
            self.object_manager.clear()
            self.subtitle_manager.clear()
            if transition:
                self.to_switch = mode
                self.to_reset = reset
                self.transition_manager.close()
            else:
                self.mode = mode
                self.menu = self.menus[self.mode]
                if reset:
                    self.menu.reset()
            # self.subtitle_manager.clear()

    def update(self, events: list[pygame.event.Event]):
        # print(self.transition_manager.transition.k)
        for e in events:
            # if e.type == pygame.MOUSEBUTTONDOWN:
            #     if e.button == 1:
            #         self.object_manager.add(
            #             PointClicked(*pygame.mouse.get_pos())
            #         )
            if e.type == pygame.KEYDOWN:
                # if e.key == pygame.K_SPACE:
                #     self.sound_manager.toggle_pause()
                # if e.key == pygame.K_r:
                #     self.menu.reset()
                if e.key == pygame.K_e:
                    self.object_manager.collision_enabled = not self.object_manager.collision_enabled
                    subtitle = ('pro' if self.object_manager.collision_enabled else 'noob')
                    # self.subtitle_manager.add(
                    #     Subtitle(f'{subtitle} Mode Enabled', 2, )
                    # )
                    for i in get_typed_subtitles(f'{subtitle} Mode Entered', pos=(WIDTH // 2, HEIGHT - 50)):
                        self.subtitle_manager.add(i)
                if e.key == pygame.K_KP_PLUS:
                    self.sound_manager.skip_to(self.sound_manager.elapsed_time + 10)
                # if e.key == pygame.K_KP_MINUS:
                #     self.sound_manager.skip_to(self.sound_manager.elapsed_time - 10)
                # self.sound_manager.reset()
        # print(self.sound_manager.elapsed_time)
        if self.to_switch != 'none':
            if self.transition_manager.transition.status == 'closed':
                self.switch_mode(self.to_switch, self.to_reset, transition=False)
                self.to_switch = 'none'
                self.to_reset = False
                self.transition_manager.open()
        self.menu.update(events)
        self.object_manager.update(events)
        self.transition_manager.update(events)
        self.subtitle_manager.update()

    def draw(self, surf: pygame.Surface):
        self.menu.draw(surf)
        self.object_manager.draw(surf)
        self.transition_manager.draw(surf)
        self.subtitle_manager.draw(surf)
        self.sound_manager.update_time()
        # surf.blit(text(Globals.get(ELAPSED_TIME_FOR_SOUNDTRACK).__str__(), color='white'), (0, 150))
        # surf.blit(text(self.transition_manager.transition.status, color='black'), (0, 0))
