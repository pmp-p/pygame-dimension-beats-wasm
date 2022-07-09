import pygame

from config import WIDTH, HEIGHT


class Transition:
    def __init__(self):
        self.surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self._status = 'ready'
        self.k = 0
        self.multiplier = 1
        self.size = 0

    def get_size(self) -> int:
        # returns size of first element in matrix
        # for checking status
        raise NotImplementedError('get_size method not implemented yet')

    @property
    def status(self):
        if self.size == 0:
            raise NotImplementedError('size should not be 0')
        if self.k == 0:
            return 'ready'
        elif self.k > 0:
            if self.get_size() >= self.size:
                return 'closed'
            else:
                return 'closing'
        elif self.k < 0:
            if self.get_size() <= 0:
                return 'open'
            else:
                return 'opening'
        else:
            return 'unknown'

    def start(self):
        self.k = self.multiplier

    def stop(self):
        self.k = 0

    def update(self):
        pass

    def draw(self, surf: pygame.Surface):
        surf.blit(self.surf, (0, 0))


class SquareTransition(Transition):
    def __init__(self):
        super().__init__()
        self.size = 75
        self.multiplier = 1
        self.squares = [
            [0 for _ in range(WIDTH // self.size + 1)] for _ in range(HEIGHT // self.size + 1)
        ]

    def get_size(self) -> int:
        return self.squares[0][0]

    def update(self):
        for row in range(len(self.squares)):
            for col in range(len(self.squares[row])):
                self.squares[row][col] += self.k
                if self.squares[row][col] > self.size:
                    self.squares[row][col] = self.size
                if self.squares[row][col] < 0:
                    self.squares[row][col] = 0

    def draw(self, surf: pygame.Surface):
        for row in range(len(self.squares)):
            for col in range(len(self.squares[row])):
                size = self.squares[row][col]
                pygame.draw.rect(surf, 'black', (col * self.size + self.size // 2 - size // 2, row * self.size + self.size // 2 - size // 2, size, size))


class CircleTransition(Transition):
    def __init__(self):
        super().__init__()
        self.size = 75
        self.multiplier = 1
        self.circles = [
            [0 for _ in range(WIDTH // self.size + 1)] for _ in range(HEIGHT // self.size + 1)
        ]

    def get_size(self) -> int:
        return self.circles[0][0]

    def update(self):
        for row in range(len(self.circles)):
            for col in range(len(self.circles[row])):
                self.circles[row][col] += self.k
                if self.circles[row][col] > self.size:
                    self.circles[row][col] = self.size
                if self.circles[row][col] < 0:
                    self.circles[row][col] = 0

    def draw(self, surf: pygame.Surface):
        for row in range(len(self.circles)):
            for col in range(len(self.circles[row])):
                size = self.circles[row][col]
                pygame.draw.circle(surf, 'black', (col * self.size, row * self.size), size)


class TransitionManager:
    def __init__(self):
        self.transition: Transition = SquareTransition()
        self.transitions = {
            'square': SquareTransition,
            'circle': CircleTransition,
        }

    def close(self):
        self.transition.k = self.transition.multiplier

    def open(self):
        self.transition.k = -self.transition.multiplier

    def set_transition(self, transition):
        if transition in self.transitions:
            self.transition = self.transitions[transition]()

    def update(self, events: list[pygame.event.Event]):
        self.transition.update()
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_p:
                    self.transition.k *= -1
                if e.key == pygame.K_r:
                    self.transition.start()

    def draw(self, surf: pygame.Surface):
        self.transition.draw(surf)
