"""Validation and deterministic reporting for fiction mystery ledgers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

STATES = {"open", "resolved", "intentionally_open"}


class LedgerError(ValueError):
    """Raised for invalid ledger data."""


def load_ledger(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise LedgerError(f"Could not read ledger: {exc}") from exc
    return validate(payload)


def validate(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict) or payload.get("version") != 1:
        raise LedgerError("Ledger must be a version 1 JSON object.")
    milestones = payload.get("milestones")
    entries = payload.get("mysteries")
    if (
        not isinstance(milestones, list)
        or not milestones
        or not all(isinstance(x, str) and x for x in milestones)
    ):
        raise LedgerError("milestones must be a non-empty list of names.")
    if len(milestones) != len(set(milestones)):
        raise LedgerError("milestone names must be unique.")
    if not isinstance(entries, list):
        raise LedgerError("mysteries must be a list.")
    ids: set[str] = set()
    for entry in entries:
        _validate_entry(entry, milestones, ids)
    return payload


def _validate_entry(entry: Any, milestones: list[str], ids: set[str]) -> None:
    if not isinstance(entry, dict):
        raise LedgerError("Each mystery must be an object.")
    identifier = entry.get("id")
    if not isinstance(identifier, str) or not identifier or identifier in ids:
        raise LedgerError("Mystery IDs must be non-empty and unique.")
    ids.add(identifier)
    if not isinstance(entry.get("title"), str) or not entry["title"]:
        raise LedgerError(f"Mystery {identifier} needs a title.")
    if entry.get("introduced") not in milestones:
        raise LedgerError(f"Mystery {identifier} has an unknown introduced milestone.")
    if not isinstance(entry.get("status"), str) or entry.get("status") not in STATES:
        raise LedgerError(f"Mystery {identifier} has an invalid status.")
    if entry["status"] == "resolved" and not entry.get("resolution"):
        raise LedgerError(f"Resolved mystery {identifier} needs a resolution.")
    if entry.get("resolved_at") is not None and entry["resolved_at"] not in milestones:
        raise LedgerError(f"Mystery {identifier} has an unknown resolution milestone.")
    for field in ("clues", "promises"):
        values = entry.get(field, [])
        if not isinstance(values, list):
            raise LedgerError(f"Mystery {identifier} {field} must be a list.")
        for item in values:
            if (
                not isinstance(item, dict)
                or item.get("at") not in milestones
                or not isinstance(item.get("text"), str)
            ):
                raise LedgerError(f"Mystery {identifier} has an invalid {field} item.")
        item_ids = [item["id"] for item in values if "id" in item]
        if not all(isinstance(value, str) and value for value in item_ids) or len(item_ids) != len(
            set(item_ids)
        ):
            raise LedgerError(f"Mystery {identifier} {field} IDs must be unique text.")
    promise_ids = {item["id"] for item in entry.get("promises", []) if "id" in item}
    for clue in entry.get("clues", []):
        links = clue.get("promise_ids", [])
        if not isinstance(links, list) or not all(
            isinstance(value, str) and value in promise_ids for value in links
        ):
            raise LedgerError(f"Mystery {identifier} clue links must reference its promise IDs.")


def report(
    ledger: dict[str, Any], *, through: str | None = None, stale_after: int = 3
) -> dict[str, Any]:
    if not isinstance(stale_after, int) or isinstance(stale_after, bool) or stale_after < 1:
        raise LedgerError("stale_after must be a positive milestone count")
    milestones = ledger["milestones"]
    if through is not None and through not in milestones:
        raise LedgerError(f"Unknown milestone: {through}")
    limit = milestones.index(through) if through else len(milestones) - 1
    visible = []
    for entry in ledger["mysteries"]:
        if milestones.index(entry["introduced"]) > limit:
            continue
        item = dict(entry)
        for field in ("clues", "promises"):
            item[field] = [
                dict(value)
                for value in entry.get(field, [])
                if milestones.index(value["at"]) <= limit
            ]
        if (
            entry.get("resolved_at") in milestones
            and milestones.index(entry["resolved_at"]) > limit
        ):
            item["status"] = "open"
            item["resolution"] = None
            item["resolved_at"] = None
        visible.append(item)
    counts = {state: sum(item["status"] == state for item in visible) for state in sorted(STATES)}
    timeline: list[dict[str, Any]] = []
    stale = []
    orphan_clues = []
    for item in visible:
        events = [{"at": item["introduced"], "kind": "introduction", "text": item["title"]}]
        for field in ("clues", "promises"):
            events.extend(
                {"at": entry["at"], "kind": field[:-1], "text": entry["text"]}
                for entry in item[field]
            )
        if item["status"] == "resolved" and item.get("resolved_at"):
            events.append(
                {
                    "at": item["resolved_at"],
                    "kind": "resolution",
                    "text": item.get("resolution", ""),
                }
            )
        timeline.extend({**event, "mystery_id": item["id"]} for event in events)
        last = max(milestones.index(event["at"]) for event in events)
        if item["status"] == "open" and limit - last >= stale_after:
            stale.append({"id": item["id"], "milestones_since_advance": limit - last})
        visible_promises = {promise["id"] for promise in item["promises"] if "id" in promise}
        for index, clue in enumerate(item["clues"]):
            clue["promise_ids"] = [
                key for key in clue.get("promise_ids", []) if key in visible_promises
            ]
            if not clue["promise_ids"]:
                orphan_clues.append(
                    {
                        "mystery_id": item["id"],
                        "clue_index": index,
                        "meaning": "No explicit link to a visible promise; author review only.",
                    }
                )
    timeline.sort(key=lambda event: milestones.index(event["at"]))
    return {
        "version": 1,
        "milestones": milestones[: limit + 1],
        "title": ledger.get("title", "Mystery ledger"),
        "through": milestones[limit],
        "counts": counts,
        "mysteries": visible,
        "timeline": timeline,
        "long_unadvanced": stale,
        "orphan_clues": orphan_clues,
    }


def markdown(payload: dict[str, Any]) -> str:
    lines = [f"# {payload['title']}", "", f"Through: **{payload['through']}**", ""]
    for state in ("open", "resolved", "intentionally_open"):
        lines.extend([f"## {state.replace('_', ' ').title()} ({payload['counts'][state]})", ""])
        matching = [item for item in payload["mysteries"] if item["status"] == state]
        if not matching:
            lines.extend(["_None._", ""])
        for item in matching:
            lines.extend(
                [f"### {item['title']} (`{item['id']}`)", f"Introduced: {item['introduced']}", ""]
            )
            for clue in item.get("clues", []):
                lines.append(f"- Clue at {clue['at']}: {clue['text']}")
            for promise in item.get("promises", []):
                lines.append(f"- Promise at {promise['at']}: {promise['text']}")
            if item.get("resolution"):
                lines.append(f"- Resolution: {item['resolution']}")
            lines.append("")
    lines.extend(["## Chapter timeline", ""])
    lines.extend(
        f"- {event['at']}: {event['kind']} ({event['mystery_id']}) — {event['text']}"
        for event in payload["timeline"]
    )
    lines.extend(
        [
            "",
            "## Author review",
            "",
            f"Long-unadvanced open threads: {len(payload['long_unadvanced'])}",
            f"Clues without explicit visible promise links: {len(payload['orphan_clues'])}",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"
