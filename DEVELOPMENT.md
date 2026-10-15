# Development

Use the Python package in src and the pytest regression suite. CI must pass before release.

## 1.1.0 improvement session

Add a local mystery editor, chapter timeline, clue-to-promise links and author-controlled stale-thread/orphan-clue review.

The editor changes local mystery records, clues, promises and optional resolution milestones, then downloads a new version 1 input. Clues and promises may have unique IDs; a clue's `promise_ids` explicitly links promises within that mystery. `--stale-after` sets the positive chapter-gap threshold for unadvanced open threads. Orphan clues mean no explicit visible promise link, not a narrative error. The timeline includes introductions, visible clues/promises and authored resolutions. Spoiler boundaries exclude future content and links; an editor generated at a boundary contains only those visible records. Re-run the CLI to validate downloaded edits and regenerate reports. Source ledgers remain unchanged.

Local formatting, lint, strict types and regression tests pass. Public release completion requires the protected CI/CodeQL matrix, tagged artifacts and matching Forge catalog/detail deployment.

## 1.2.0 candidate

Use `--compare-from "Chapter 1" --through "Chapter 2" --format json` to compare two explicit inclusive milestone snapshots. JSON or Markdown lists newly visible mysteries, clues, promises and resolutions with before/after status counts and stable per-kind totals. Equal boundaries give no new items; reversed or unknown boundaries are rejected. Events in newly visible mysteries are included only if visible at the end boundary. This compares authored visibility within one supplied ledger, not historical edits or inferred narrative history. HTML editing remains the single-snapshot workflow.
