#!/usr/bin/env python3
"""
AI Game Tester — Claude plays Snake in the terminal.

Usage:
  python main.py                # default 8x8, 0.3s delay
  python main.py --size 16      # bigger board
  python main.py --delay 0.1    # faster
  python main.py --verbose      # show Claude's reasoning
  python main.py --no-display   # headless, just final score
"""

import argparse
import csv
import json
import sys
import time
from pathlib import Path

from agent.claude_agent import DEFAULT_MODEL, SYSTEM_PROMPT, decide_move
from game.snake import Direction, SnakeGame


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


def write_results(results: list[dict], output: Path) -> None:
    """Write benchmark results as JSON or CSV based on the file extension."""
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.suffix.lower() == ".json":
        output.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    elif output.suffix.lower() == ".csv":
        with output.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
    else:
        raise ValueError("Output file must use .json or .csv")


def benchmark(
    size: int,
    games: int,
    *,
    seed: int | None = None,
    max_steps: int = 1_000,
    output: Path | None = None,
    model: str = DEFAULT_MODEL,
    system_prompt: str = SYSTEM_PROMPT,
):
    """Run N games headless and print stats."""
    import statistics

    scores = []
    steps_list = []
    results = []

    print(f"Running {games} games on {size}x{size} board...\n")

    for i in range(1, games + 1):
        game_seed = seed + i - 1 if seed is not None else None
        game = SnakeGame(width=size, height=size, seed=game_seed)
        state = game.state
        start = time.time()

        print(f"  Game {i:>3}: ", end="", flush=True)

        while state.alive and state.steps < max_steps:
            board = game.render()
            valid = game.valid_moves()
            move, _ = decide_move(
                board,
                state.score,
                state.steps,
                valid,
                model=model,
                system_prompt=system_prompt,
            )
            state = game.step(Direction[move])
            print(".", end="", flush=True)

        elapsed = time.time() - start
        status = "game_over" if not state.alive else "max_steps"
        scores.append(state.score)
        steps_list.append(state.steps)
        results.append(
            {
                "game": i,
                "seed": game_seed,
                "model": model,
                "board_size": size,
                "score": state.score,
                "steps": state.steps,
                "status": status,
                "duration_seconds": round(elapsed, 3),
            }
        )
        print(
            f"  score={state.score}  steps={state.steps}  "
            f"status={status}  time={elapsed:.1f}s"
        )

    print(f"\n{'='*40}")
    print(f"  Games played : {games}")
    print(f"  Avg score    : {statistics.mean(scores):.2f}")
    print(f"  Best score   : {max(scores)}")
    print(f"  Worst score  : {min(scores)}")
    print(f"  Avg steps    : {statistics.mean(steps_list):.0f}")
    print(f"{'='*40}")
    if output:
        write_results(results, output)
        print(f"  Results saved: {output}")


def main():
    parser = argparse.ArgumentParser(description="Claude plays Snake")
    parser.add_argument("--size", type=int, default=8, help="Board size (default: 8)")
    parser.add_argument(
        "--delay", type=float, default=0.3, help="Seconds between moves (default: 0.3)"
    )
    parser.add_argument("--verbose", action="store_true", help="Show Claude's reasoning")
    parser.add_argument(
        "--no-display", action="store_true", help="Headless mode, print final score only"
    )
    parser.add_argument("--benchmark", type=int, metavar="N", help="Run N games and print stats")
    parser.add_argument("--seed", type=int, help="Base random seed for reproducible benchmarks")
    parser.add_argument(
        "--max-steps", type=int, default=1_000, help="Maximum steps per benchmark game"
    )
    parser.add_argument("--output", type=Path, help="Save benchmark results to .json or .csv")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Anthropic model ID")
    parser.add_argument("--prompt-file", type=Path, help="Use a custom system prompt from a file")
    args = parser.parse_args()

    try:
        if args.benchmark:
            system_prompt = (
                args.prompt_file.read_text(encoding="utf-8")
                if args.prompt_file
                else SYSTEM_PROMPT
            )
            benchmark(
                args.size,
                args.benchmark,
                seed=args.seed,
                max_steps=args.max_steps,
                output=args.output,
                model=args.model,
                system_prompt=system_prompt,
            )
        else:
            if args.seed is not None or args.output or args.prompt_file:
                parser.error("--seed, --output and --prompt-file require --benchmark")
            run(args.size, args.delay, args.verbose, args.no_display)
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
