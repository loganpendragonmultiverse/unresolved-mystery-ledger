import copy
import json

import pytest

from mystery_ledger.cli import main
from mystery_ledger.core import LedgerError, report, validate
from mystery_ledger.editor import render_html


def ledger():
    return {
        "version": 1,
        "title": "Test",
        "milestones": ["One", "Two", "Three", "Four", "Five"],
        "mysteries": [
            {
                "id": "door",
                "title": "Door",
                "introduced": "One",
                "status": "open",
                "promises": [{"id": "open-door", "at": "One", "text": "Open it"}],
                "clues": [{"id": "key", "at": "Two", "text": "Key", "promise_ids": ["open-door"]}],
            }
        ],
    }


def test_linked_timeline_staleness_and_source_preservation(tmp_path, capsys) -> None:
    data = ledger()
    original = copy.deepcopy(data)
    result = report(validate(data), stale_after=3)
    assert result["long_unadvanced"] == [{"id": "door", "milestones_since_advance": 3}]
    assert not result["orphan_clues"]
    assert [event["kind"] for event in result["timeline"]] == ["introduction", "promise", "clue"]
    assert data == original
    data["mysteries"][0]["clues"][0]["promise_ids"] = []
    assert len(report(data)["orphan_clues"]) == 1
    source = tmp_path / "ledger.json"
    source.write_text(json.dumps(data))
    assert main([str(source), "--format", "html"]) == 0
    assert "Add mystery" in capsys.readouterr().out


def test_boundary_hides_future_links_and_resolution() -> None:
    data = ledger()
    entry = data["mysteries"][0]
    entry["promises"][0]["at"] = "Five"
    entry.update(status="resolved", resolved_at="Five", resolution="FUTURE_RESOLUTION")
    original = copy.deepcopy(data)
    limited = report(validate(data), through="Two")
    assert "FUTURE_RESOLUTION" not in render_html(limited)
    assert not limited["mysteries"][0]["clues"][0]["promise_ids"]
    assert data == original
    assert report(data)["timeline"][-1]["kind"] == "resolution"


@pytest.mark.parametrize(
    "change",
    [
        {"resolved_at": "missing"},
        {"status": []},
        {
            "promises": [
                {"id": "x", "at": "One", "text": "A"},
                {"id": "x", "at": "Two", "text": "B"},
            ]
        },
        {"clues": [{"at": "One", "text": "A", "promise_ids": ["missing"]}]},
    ],
)
def test_invalid_link_contract(change) -> None:
    data = ledger()
    data["mysteries"][0].update(change)
    with pytest.raises(LedgerError):
        validate(data)


def test_invalid_staleness() -> None:
    with pytest.raises(LedgerError):
        report(ledger(), stale_after=0)
