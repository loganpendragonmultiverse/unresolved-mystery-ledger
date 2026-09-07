# Development

Use the Python package in src and the pytest regression suite. CI must pass before release.

## 1.1.0 improvement session

Add a local mystery editor, chapter timeline, clue-to-promise links and author-controlled stale-thread/orphan-clue review.

The editor changes local mystery records, clues, promises and optional resolution milestones, then downloads a new version 1 input. Clues and promises may have unique IDs; a clue's `promise_ids` explicitly links promises within that mystery. `--stale-after` sets the positive chapter-gap threshold for unadvanced open threads. Orphan clues mean no explicit visible promise link, not a narrative error. The timeline includes introductions, visible clues/promises and authored resolutions. Spoiler boundaries exclude future content and links; an editor generated at a boundary contains only those visible records. Re-run the CLI to validate downloaded edits and regenerate reports. Source ledgers remain unchanged.

Local formatting, lint, strict types and regression tests pass. Public release completion requires the protected CI/CodeQL matrix, tagged artifacts and matching Forge catalog/detail deployment.
