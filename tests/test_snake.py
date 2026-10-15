import pytest

from game.snake import Direction, SnakeGame


def test_snake_moves_forward():
    game = SnakeGame(seed=1)

    state = game.step(Direction.RIGHT)

    assert state.snake == [(5, 4), (4, 4), (3, 4)]
    assert state.steps == 1


def test_wall_collision_ends_game():
    game = SnakeGame(width=4, height=4, seed=1)

    state = game.step(Direction.RIGHT)
    state = game.step(Direction.RIGHT)

    assert state.alive is False


def test_body_collision_ends_game():
    game = SnakeGame(seed=1)
    game._snake = [(3, 3), (3, 2), (2, 2), (2, 3), (2, 4)]
    game._direction = Direction.DOWN

    state = game.step(Direction.LEFT)

    assert state.alive is False


def test_eating_food_grows_snake_and_increases_score():
    game = SnakeGame(seed=1)
    game._food = (5, 4)

    state = game.step(Direction.RIGHT)

    assert state.score == 1
    assert len(state.snake) == 4
    assert state.food not in state.snake


def test_valid_moves_excludes_wall_body_and_reverse():
    game = SnakeGame(width=5, height=5, seed=1)
    game._snake = [(4, 2), (3, 2), (3, 3), (4, 3)]
    game._direction = Direction.UP

    assert game.valid_moves() == ["UP"]


def test_board_rejects_dimensions_too_small_for_initial_snake():
    with pytest.raises(ValueError, match="at least 4x2"):
        SnakeGame(width=3, height=3)
