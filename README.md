# Unresolved Mystery Ledger

[![CI](https://github.com/loganpendragonmultiverse/unresolved-mystery-ledger/actions/workflows/ci.yml/badge.svg)](https://github.com/loganpendragonmultiverse/unresolved-mystery-ledger/actions/workflows/ci.yml)

Unresolved Mystery Ledger is a local command-line tool for tracking mysteries, clues, narrative promises, resolutions, and intentionally open threads in long-form fiction. Its milestone filter can generate a spoiler-controlled report as of a chosen chapter or scene.

## Three-minute start

Requires Python 3.10 or newer.

```bash
python -m pip install .
mystery-ledger examples/novel.json
mystery-ledger examples/novel.json --through "Chapter 2" --format json
```

The input is versioned JSON with an ordered `milestones` list and `mysteries`. Each mystery has a unique ID, title, introduction milestone, status, and optional clue/promise records. Resolved entries require a resolution; future resolutions are hidden when `--through` selects an earlier milestone.

Use `--output report.md` to write a new report. Existing files are refused. Without `--output`, results go to standard output.

## Output and privacy

Markdown groups entries into open, resolved, and intentionally open sections. JSON preserves the same filtered structure and counts. Everything runs locally; there is no network access, telemetry, AI service, or manuscript upload.

## Limitations

- The tool validates supplied structured notes; it does not extract mysteries from prose.
- Milestone order comes from the input list and is not inferred from chapter names.
- A spoiler boundary hides future clues, promises, and resolutions but cannot audit spoilers inside user-written text.
- Input JSON may contain sensitive plot details; store and share it accordingly.

## Development and maintenance

Run `python -m pip install -e ".[dev]"`, then `ruff format --check .`, `ruff check .`, `pytest`, and `python -m build`. Contributions are accepted through reviewed pull requests. Version 1.0.0 is feature-complete for the documented structured-ledger scope; maintenance prioritizes deterministic output, validation, and backward compatibility.

See [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md), and [SUPPORT.md](SUPPORT.md). Licensed under the [MIT License](LICENSE).

## More open-source projects

This project is part of the [Logan Pendragon Forge open-source collection](https://www.loganpendragonforge.com/open-source/).
