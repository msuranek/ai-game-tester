#!/usr/bin/env python3
"""
AI Game Tester — Claude plays Snake in the terminal.

Usage:
  python main.py                # default 12x12, 0.3s delay
  python main.py --size 16      # bigger board
  python main.py --delay 0.1    # faster
  python main.py --verbose      # show Claude's reasoning
  python main.py --no-display   # headless, just final score
"""

import argparse
import sys
import time

from game.snake import Direction, SnakeGame
from agent.claude_agent import decide_move


def clear():
    sys.stdout.write("\033[H\033[J")
    sys.stdout.flush()


def render_hud(state, move: str, verbose: bool, reasoning: str) -> str:
    lines = [
        f"  Score: {state.score}   Steps: {state.steps}   Last move: {move}",
    ]
    if verbose and reasoning:
        lines.append(f"  Claude: {reasoning}")
    return "\n".join(lines)


def run(size: int, delay: float, verbose: bool, no_display: bool):
    game = SnakeGame(width=size, height=size)
    state = game.state
    last_move = "—"
    last_reasoning = ""

    print("Claude is playing Snake...\n")
    if not no_display:
        time.sleep(0.5)

    while state.alive:
        board = game.render()
        valid = game.valid_moves()

        if not no_display:
            clear()
            print(render_hud(state, last_move, verbose, last_reasoning))
            print()
            print(board)
            print()

        move, reasoning = decide_move(board, state.score, state.steps, valid)
        last_move = move
        last_reasoning = reasoning

        state = game.step(Direction[move])

        if not no_display:
            time.sleep(delay)

    # Final state
    if not no_display:
        clear()
        print(render_hud(state, last_move, verbose, last_reasoning))
        print()
        print(game.render())
        print()

    print(f"  Game Over! Final score: {state.score} in {state.steps} steps.")


def benchmark(size: int, games: int):
    """Run N games headless and print stats."""
    import statistics

    scores = []
    steps_list = []

    print(f"Running {games} games on {size}x{size} board...\n")

    for i in range(1, games + 1):
        game = SnakeGame(width=size, height=size)
        state = game.state
        start = time.time()

        print(f"  Game {i:>3}: ", end="", flush=True)

        while state.alive:
            board = game.render()
            valid = game.valid_moves()
            move, _ = decide_move(board, state.score, state.steps, valid)
            state = game.step(Direction[move])
            print(".", end="", flush=True)

        elapsed = time.time() - start
        scores.append(state.score)
        steps_list.append(state.steps)
        print(f"  score={state.score}  steps={state.steps}  time={elapsed:.1f}s")

    print(f"\n{'='*40}")
    print(f"  Games played : {games}")
    print(f"  Avg score    : {statistics.mean(scores):.2f}")
    print(f"  Best score   : {max(scores)}")
    print(f"  Worst score  : {min(scores)}")
    print(f"  Avg steps    : {statistics.mean(steps_list):.0f}")
    print(f"{'='*40}")


def main():
    parser = argparse.ArgumentParser(description="Claude plays Snake")
    parser.add_argument("--size", type=int, default=8, help="Board size (default: 8)")
    parser.add_argument("--delay", type=float, default=0.3, help="Seconds between moves (default: 0.3)")
    parser.add_argument("--verbose", action="store_true", help="Show Claude's reasoning")
    parser.add_argument("--no-display", action="store_true", help="Headless mode, print final score only")
    parser.add_argument("--benchmark", type=int, metavar="N", help="Run N games and print stats")
    args = parser.parse_args()

    try:
        if args.benchmark:
            benchmark(args.size, args.benchmark)
        else:
            run(args.size, args.delay, args.verbose, args.no_display)
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
