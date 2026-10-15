import copy
import json

import pytest
from test_core import sample

from mystery_ledger.cli import main
from mystery_ledger.core import LedgerError, compare_snapshots


def test_inclusive_boundaries_future_exclusion_counts_and_no_mutation():
    data = sample()
    data["mysteries"][0]["promises"] = [{"at": "c2", "text": "Promise"}]
    data["mysteries"].append(
        {"id": "FUTURE", "title": "FUTURE", "introduced": "c3", "status": "open"}
    )
    before = copy.deepcopy(data)
    r = compare_snapshots(data, start="c1", end="c2")
    assert r["newly_visible_counts"] == {
        "mysteries": 0,
        "clues": 1,
        "promises": 1,
        "resolutions": 0,
    }
    assert "FUTURE" not in json.dumps(r)
    assert r["before_counts"] == r["after_counts"]
    assert data == before
    assert compare_snapshots(data, start="c2", end="c3")["newly_visible_counts"]["resolutions"] == 1
    assert not any(compare_snapshots(data, start="c2", end="c2")["newly_visible_counts"].values())
    assert (
        compare_snapshots(data, start="c1", end="c3")["newly_visible"]["mysteries"][0]["id"]
        == "FUTURE"
    )


@pytest.mark.parametrize("start,end", [("c3", "c1"), ("missing", "c2"), ("c1", "missing")])
def test_invalid_comparisons(start, end):
    with pytest.raises(LedgerError):
        compare_snapshots(sample(), start=start, end=end)


def test_cli(tmp_path, capsys):
    p = tmp_path / "source.json"
    p.write_text(json.dumps(sample()))
    assert main([str(p), "--compare-from", "c1", "--through", "c2", "--format", "json"]) == 0
    assert json.loads(capsys.readouterr().out)["newly_visible_counts"]["clues"] == 1
    assert main([str(p), "--compare-from", "c1", "--through", "c2"]) == 0
    assert "snapshot comparison" in capsys.readouterr().out
    assert main([str(p), "--compare-from", "c1"]) == 2
    assert main([str(p), "--compare-from", "c1", "--through", "c2", "--format", "html"]) == 2
