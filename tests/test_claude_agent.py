import pytest

from agent.claude_agent import parse_response


def test_parse_structured_response():
    text = "REASON: Food is above.\nMOVE: UP"

    assert parse_response(text, ["UP", "LEFT"]) == ("UP", "Food is above.")


def test_parse_unstructured_response():
    move, reasoning = parse_response("I would go left now.", ["UP", "LEFT"])

    assert move == "LEFT"
    assert reasoning == "I would go left now."


def test_invalid_model_move_falls_back_to_safe_move():
    move, reasoning = parse_response("REASON: Go down.\nMOVE: DOWN", ["LEFT"])

    assert move == "LEFT"
    assert reasoning.startswith("(fallback)")


def test_parser_requires_at_least_one_valid_move():
    with pytest.raises(ValueError, match="must not be empty"):
        parse_response("MOVE: UP", [])
