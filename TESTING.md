# Testing

Run `ruff format --check .`, `ruff check .`, `mypy src`, `pytest`, and `python -m build`. CI also audits dependencies and runs the supported OS/Python matrix.

## 1.1.0 regression acceptance

Run the complete existing suite plus the new regression fixtures. Confirm the documented command produces the selected output, malformed input remains actionable, and source files remain unchanged. Add a local mystery editor, chapter timeline, clue-to-promise links and author-controlled stale-thread/orphan-clue review.

## 1.2.0 acceptance

Exercise the optional input with the full regression suite, including validation, inclusive boundaries, deterministic ordering and legacy default behavior. Use `--compare-from "Chapter 1" --through "Chapter 2" --format json` to compare two explicit inclusive milestone snapshots. JSON or Markdown lists newly visible mysteries, clues, promises and resolutions with before/after status counts and stable per-kind totals. Equal boundaries give no new items; reversed or unknown boundaries are rejected. Events in newly visible mysteries are included only if visible at the end boundary. This compares authored visibility within one supplied ledger, not historical edits or inferred narrative history. HTML editing remains the single-snapshot workflow.


Newly visible resolved legacy entries without resolved_at (or with null) include their resolution text in newly_visible.resolutions, with at: null and date_status: undated. Markdown labels these resolutions Undated. This records visibility by the end snapshot without asserting an exact resolution date. Already-visible undated resolutions are not counted again; legacy single-snapshot reports and timelines are unchanged.

## 1.2.2 regression acceptance

Exercise malformed structured text, report-write errors, concurrent output creation and source immutability. Verify installed wheel and source-distribution imports, run the full suite with the unchanged 90% combined statement/branch coverage gate, and exercise the documented commands outside the source tree.

Before release, require the unchanged portfolio archive binding to match every source/test/doc/example/license/metadata member, then verify installed documentation and examples under `share/doc/unresolved-mystery-ledger` against tracked source bytes.
