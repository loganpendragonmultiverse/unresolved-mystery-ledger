import json
from pathlib import Path

import pytest

from mystery_ledger.cli import main
from mystery_ledger.core import LedgerError, markdown, report, validate


def sample() -> dict:
    return {
        "version": 1,
        "title": "Novel",
        "milestones": ["c1", "c2", "c3"],
        "mysteries": [
            {
                "id": "door",
                "title": "Locked door",
                "introduced": "c1",
                "status": "resolved",
                "clues": [{"at": "c2", "text": "Brass key"}],
                "promises": [],
                "resolution": "Key opens it",
                "resolved_at": "c3",
            }
        ],
    }


def test_spoiler_boundary_hides_future_resolution() -> None:
    result = report(validate(sample()), through="c2")
    assert result["mysteries"][0]["status"] == "open"
    assert result["mysteries"][0]["resolution"] is None


def test_full_report_and_markdown() -> None:
    result = report(validate(sample()))
    assert result["counts"]["resolved"] == 1
    assert "Brass key" in markdown(result)


@pytest.mark.parametrize(
    "change,message",
    [
        ({"version": 2}, "version 1"),
        ({"milestones": []}, "milestones"),
        ({"mysteries": "bad"}, "mysteries"),
    ],
)
def test_rejects_invalid_roots(change: dict, message: str) -> None:
    payload = sample()
    payload.update(change)
    with pytest.raises(LedgerError, match=message):
        validate(payload)


def test_rejects_invalid_entries() -> None:
    payload = sample()
    payload["mysteries"][0]["status"] = "maybe"
    with pytest.raises(LedgerError, match="invalid status"):
        validate(payload)


def test_cli_json_and_refuses_overwrite(tmp_path: Path, capsys) -> None:  # type: ignore[no-untyped-def]
    source = tmp_path / "ledger.json"
    source.write_text(json.dumps(sample()), encoding="utf-8")
    target = tmp_path / "report.json"
    assert main([str(source), "--format", "json", "--output", str(target)]) == 0
    assert json.loads(target.read_text())["counts"]["resolved"] == 1
    assert main([str(source), "--output", str(target)]) == 2
    assert "already exists" in capsys.readouterr().err


def test_unknown_boundary_is_rejected() -> None:
    with pytest.raises(LedgerError, match="Unknown"):
        report(validate(sample()), through="c9")


def test_entry_validation_edges() -> None:
    cases = []
    duplicate_milestones = sample()
    duplicate_milestones["milestones"] = ["c1", "c1"]
    cases.append((duplicate_milestones, "unique"))
    non_object = sample()
    non_object["mysteries"] = ["bad"]
    cases.append((non_object, "object"))
    no_title = sample()
    no_title["mysteries"][0]["title"] = ""
    cases.append((no_title, "title"))
    unknown_intro = sample()
    unknown_intro["mysteries"][0]["introduced"] = "c9"
    cases.append((unknown_intro, "introduced"))
    no_resolution = sample()
    no_resolution["mysteries"][0]["resolution"] = ""
    cases.append((no_resolution, "resolution"))
    invalid_clues = sample()
    invalid_clues["mysteries"][0]["clues"] = "bad"
    cases.append((invalid_clues, "clues"))
    invalid_clue = sample()
    invalid_clue["mysteries"][0]["clues"] = [{"at": "c9", "text": "x"}]
    cases.append((invalid_clue, "invalid clues"))
    for payload, message in cases:
        with pytest.raises(LedgerError, match=message):
            validate(payload)


def test_cli_stdout_and_read_error(tmp_path: Path, capsys) -> None:  # type: ignore[no-untyped-def]
    source = tmp_path / "ledger.json"
    source.write_text(json.dumps(sample()), encoding="utf-8")
    assert main([str(source), "--through", "c1"]) == 0
    assert "Locked door" in capsys.readouterr().out
    assert main([str(tmp_path / "missing.json")]) == 2
    assert "Could not read" in capsys.readouterr().err
