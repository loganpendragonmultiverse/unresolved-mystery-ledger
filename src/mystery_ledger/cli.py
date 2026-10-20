"""Command-line interface."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path

from .core import LedgerError, compare_snapshots, comparison_markdown, load_ledger, markdown, report
from .editor import render_html


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="mystery-ledger")
    parser.add_argument("ledger", type=Path)
    parser.add_argument("--through")
    parser.add_argument(
        "--compare-from", help="Compare an explicit earlier milestone with --through"
    )
    parser.add_argument("--format", choices=("markdown", "json", "html"), default="markdown")
    parser.add_argument("--stale-after", type=int, default=3)
    parser.add_argument("--output", type=Path)
    try:
        args = parser.parse_args(argv)
        ledger = load_ledger(args.ledger)
        if args.compare_from is not None:
            if args.through is None or args.format == "html":
                raise LedgerError("--compare-from requires --through and JSON or Markdown output.")
            result = compare_snapshots(
                ledger,
                start=args.compare_from,
                end=args.through,
                stale_after=args.stale_after,
            )
        else:
            result = report(ledger, through=args.through, stale_after=args.stale_after)
        rendered = (
            json.dumps(result, indent=2) + "\n"
            if args.format == "json"
            else comparison_markdown(result)
            if args.compare_from is not None
            else markdown(result)
        )
        if args.format == "html":
            rendered = render_html(result)
        if args.output:
            if args.output.is_symlink():
                raise LedgerError(f"Output already exists: {args.output}")
            args.output.parent.mkdir(parents=True, exist_ok=True)
            try:
                with args.output.open("x", encoding="utf-8") as stream:
                    stream.write(rendered)
            except FileExistsError as exc:
                raise LedgerError(f"Output already exists: {args.output}") from exc
            print(args.output.resolve())
        else:
            print(rendered, end="")
        return 0
    except (LedgerError, OSError, UnicodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
