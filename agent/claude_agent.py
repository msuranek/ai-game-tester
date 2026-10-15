"""
Claude agent that decides the next Snake move.
Uses Claude Haiku for a fast game loop.
"""

import os
import re
from pathlib import Path

import anthropic
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

SYSTEM_PROMPT = """You are playing Snake. Board: H=head S=body F=food .=empty

Respond in this exact format:
REASON: <one short sentence why>
MOVE: <UP|DOWN|LEFT|RIGHT>"""
DEFAULT_MODEL = "claude-haiku-4-5-20251001"
DIRECTIONS = ("UP", "DOWN", "LEFT", "RIGHT")


def parse_response(text: str, valid_moves: list[str]) -> tuple[str, str]:
    """Parse a model response and always return a currently valid move."""
    if not valid_moves:
        raise ValueError("valid_moves must not be empty")

    reason = ""
    candidate = None
    for line in text.splitlines():
        label, separator, value = line.partition(":")
        if not separator:
            continue
        if label.strip().upper() == "REASON":
            reason = value.strip()
        elif label.strip().upper() == "MOVE":
            parsed = value.strip().upper()
            if parsed in DIRECTIONS:
                candidate = parsed

    if candidate in valid_moves:
        return candidate, reason or text.strip()

    # Tolerate less structured answers, but never select an unsafe move.
    upper_text = text.upper()
    for move in valid_moves:
        if re.search(rf"\b{re.escape(move)}\b", upper_text):
            return move, reason or text.strip()

    return valid_moves[0], f"(fallback) {text.strip()}"


def decide_move(
    board: str,
    score: int,
    steps: int,
    valid_moves: list[str],
    *,
    model: str = DEFAULT_MODEL,
    system_prompt: str = SYSTEM_PROMPT,
) -> tuple[str, str]:
    """
    Ask Claude to pick the next move.
    Returns (move, reasoning) where reasoning is Claude's explanation.
    """
    prompt = (
        f"Step: {steps} | Score: {score} | Valid moves: {', '.join(valid_moves)}\n\n"
        f"{board}\n\n"
        f"Your move:"
    )

    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    response = client.messages.create(
        model=model,
        max_tokens=60,
        system=system_prompt,
        messages=[{"role": "user", "content": prompt}],
    )

    text = response.content[0].text.strip()

    return parse_response(text, valid_moves)
