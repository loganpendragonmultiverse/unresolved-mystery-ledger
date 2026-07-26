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
    if entry.get("status") not in STATES:
        raise LedgerError(f"Mystery {identifier} has an invalid status.")
    if entry["status"] == "resolved" and not entry.get("resolution"):
        raise LedgerError(f"Resolved mystery {identifier} needs a resolution.")
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


def report(ledger: dict[str, Any], *, through: str | None = None) -> dict[str, Any]:
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
                value for value in entry.get(field, []) if milestones.index(value["at"]) <= limit
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
    return {
        "title": ledger.get("title", "Mystery ledger"),
        "through": milestones[limit],
        "counts": counts,
        "mysteries": visible,
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
    return "\n".join(lines).rstrip() + "\n"
