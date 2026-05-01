"""
Claude agent that decides the next Snake move.
Uses claude-haiku for speed and low cost (~$0.001 per full game).
"""

import os
from pathlib import Path
import anthropic
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """You are playing Snake. Board: H=head S=body F=food .=empty

Respond in this exact format:
REASON: <one short sentence why>
MOVE: <UP|DOWN|LEFT|RIGHT>"""


def decide_move(board: str, score: int, steps: int, valid_moves: list[str]) -> tuple[str, str]:
    """
    Ask Claude to pick the next move.
    Returns (move, reasoning) where reasoning is Claude's explanation.
    """
    prompt = (
        f"Step: {steps} | Score: {score} | Valid moves: {', '.join(valid_moves)}\n\n"
        f"{board}\n\n"
        f"Your move:"
    )

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=60,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )

    text = response.content[0].text.strip()

    reason = ""
    move = None
    for line in text.splitlines():
        if line.startswith("REASON:"):
            reason = line.split(":", 1)[1].strip()
        elif line.startswith("MOVE:"):
            candidate = line.split(":", 1)[1].strip().upper()
            if candidate in ["UP", "DOWN", "LEFT", "RIGHT"]:
                move = candidate

    if move:
        return move, reason or text

    # Fallback: hledej směr kdekoliv v textu
    for m in ["UP", "DOWN", "LEFT", "RIGHT"]:
        if m in text.upper():
            return m, reason or text

    return valid_moves[0], f"(fallback) {text}"
