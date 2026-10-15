import csv
import json

import main


def test_benchmark_writes_reproducible_json(monkeypatch, tmp_path):
    monkeypatch.setattr(
        main,
        "decide_move",
        lambda board, score, steps, valid, **kwargs: (valid[0], "test"),
    )
    output = tmp_path / "results.json"

    main.benchmark(4, 1, seed=10, max_steps=3, output=output)

    results = json.loads(output.read_text(encoding="utf-8"))
    assert results[0]["seed"] == 10
    assert results[0]["board_size"] == 4
    assert results[0]["model"] == main.DEFAULT_MODEL
    assert results[0]["status"] in {"game_over", "max_steps"}


def test_write_results_supports_csv(tmp_path):
    output = tmp_path / "results.csv"
    result = {"game": 1, "score": 2}

    main.write_results([result], output)

    with output.open(newline="", encoding="utf-8") as file:
        assert list(csv.DictReader(file)) == [{"game": "1", "score": "2"}]
