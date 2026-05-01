"""
Snake game logic — no display, pure state machine.
The board is rendered as ASCII for the Claude agent.
"""

import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Direction(Enum):
    UP = "UP"
    DOWN = "DOWN"
    LEFT = "LEFT"
    RIGHT = "RIGHT"


OPPOSITES = {
    Direction.UP: Direction.DOWN,
    Direction.DOWN: Direction.UP,
    Direction.LEFT: Direction.RIGHT,
    Direction.RIGHT: Direction.LEFT,
}

MOVES = {
    Direction.UP: (0, -1),
    Direction.DOWN: (0, 1),
    Direction.LEFT: (-1, 0),
    Direction.RIGHT: (1, 0),
}


@dataclass
class GameState:
    snake: list[tuple[int, int]]
    food: tuple[int, int]
    direction: Direction
    score: int
    alive: bool
    width: int
    height: int
    steps: int


class SnakeGame:
    def __init__(self, width: int = 8, height: int = 8):
        self.width = width
        self.height = height
        self._reset()

    def _reset(self):
        cx, cy = self.width // 2, self.height // 2
        self._snake = [(cx, cy), (cx - 1, cy), (cx - 2, cy)]
        self._direction = Direction.RIGHT
        self._score = 0
        self._alive = True
        self._steps = 0
        self._food = self._place_food()

    def _place_food(self) -> tuple[int, int]:
        occupied = set(self._snake)
        empty = [
            (x, y)
            for x in range(self.width)
            for y in range(self.height)
            if (x, y) not in occupied
        ]
        return random.choice(empty) if empty else (0, 0)

    @property
    def state(self) -> GameState:
        return GameState(
            snake=list(self._snake),
            food=self._food,
            direction=self._direction,
            score=self._score,
            alive=self._alive,
            width=self.width,
            height=self.height,
            steps=self._steps,
        )

    def valid_moves(self) -> list[str]:
        """Returns directions that won't immediately kill the snake."""
        result = []
        for d in Direction:
            if d == OPPOSITES[self._direction]:
                continue
            dx, dy = MOVES[d]
            nx, ny = self._snake[0][0] + dx, self._snake[0][1] + dy
            if 0 <= nx < self.width and 0 <= ny < self.height:
                if (nx, ny) not in set(self._snake[:-1]):
                    result.append(d.value)
        return result or [d.value for d in Direction if d != OPPOSITES[self._direction]]

    def step(self, direction: Direction) -> GameState:
        if not self._alive:
            return self.state

        # Ignore 180° turns
        if direction == OPPOSITES[self._direction]:
            direction = self._direction

        self._direction = direction
        self._steps += 1

        dx, dy = MOVES[direction]
        hx, hy = self._snake[0]
        nx, ny = hx + dx, hy + dy

        # Wall collision
        if not (0 <= nx < self.width and 0 <= ny < self.height):
            self._alive = False
            return self.state

        # Self collision (exclude tail which will move away)
        if (nx, ny) in set(self._snake[:-1]):
            self._alive = False
            return self.state

        self._snake.insert(0, (nx, ny))

        if (nx, ny) == self._food:
            self._score += 1
        else:
            self._snake.pop()

        if (nx, ny) == self._food:
            self._food = self._place_food()

        return self.state

    def render(self, show_coords: bool = False) -> str:
        """Render board as ASCII for the Claude agent."""
        board = [['.' for _ in range(self.width)] for _ in range(self.height)]

        for x, y in self._snake[1:]:
            board[y][x] = 'S'

        hx, hy = self._snake[0]
        board[hy][hx] = 'H'

        fx, fy = self._food
        board[fy][fx] = 'F'

        rows = [' '.join(row) for row in board]

        if show_coords:
            rows = [f"{str(i).rjust(2)} {row}" for i, row in enumerate(rows)]

        return '\n'.join(rows)
