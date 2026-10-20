import json

import pytest
from test_core import sample

from mystery_ledger.cli import main
from mystery_ledger.core import LedgerError, validate


@pytest.mark.parametrize(
    "change, message",
    [
        (lambda data: data.update(version=True), "version 1"),
        (lambda data: data.update(title=[]), "title"),
        (lambda data: data.update(milestones=[" "]), "milestones"),
        (lambda data: data["mysteries"][0].update(id=" "), "IDs"),
        (lambda data: data["mysteries"][0].update(title=" "), "title"),
        (lambda data: data["mysteries"][0].update(resolution=["spoiler"]), "must be text"),
        (lambda data: data["mysteries"][0].update(resolution=True), "must be text"),
        (lambda data: data["mysteries"][0].update(resolution=" "), "needs a resolution"),
    ],
)
def test_invalid_structured_text_is_actionable(change, message):
    data = sample()
    change(data)
    with pytest.raises(LedgerError, match=message):
        validate(data)


def test_cli_rejects_nontext_resolution_before_html_output(tmp_path, capsys):
    data = sample()
    data["mysteries"][0]["resolution"] = ["bad"]
    source = tmp_path / "ledger.json"
    source.write_text(json.dumps(data), encoding="utf-8")
    output = tmp_path / "editor.html"
    assert main([str(source), "--format", "html", "--output", str(output)]) == 2
    assert "resolution must be text" in capsys.readouterr().err
    assert not output.exists()


def test_output_parent_error_is_actionable_and_source_is_unchanged(tmp_path, capsys):
    source = tmp_path / "ledger.json"
    source.write_text(json.dumps(sample()), encoding="utf-8")
    original = source.read_bytes()
    parent = tmp_path / "file"
    parent.write_text("keep", encoding="utf-8")
    assert main([str(source), "--output", str(parent / "report.md")]) == 2
    assert "error:" in capsys.readouterr().err
    assert source.read_bytes() == original
    assert parent.read_text() == "keep"


def test_output_created_by_another_writer_is_preserved(tmp_path, monkeypatch, capsys):
    source = tmp_path / "ledger.json"
    source.write_text(json.dumps(sample()), encoding="utf-8")
    output = tmp_path / "report.md"
    original_open = type(output).open
    inserted = False

    def concurrent_open(path, mode="r", *args, **kwargs):
        nonlocal inserted
        if path == output and not inserted:
            inserted = True
            with original_open(path, "w", encoding="utf-8") as stream:
                stream.write("another writer")
        return original_open(path, mode, *args, **kwargs)

    monkeypatch.setattr(type(output), "open", concurrent_open)
    assert main([str(source), "--output", str(output)]) == 2
    assert output.read_text() == "another writer"
    assert "already exists" in capsys.readouterr().err
