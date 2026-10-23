"""Read-only CLI for structural inspection of Rezon Collective V1 snapshots.

No network calls, model execution, state writes, or provenance promotion.
An embedded SHA-256 digest is consistency evidence, never host attestation.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import sys

from .rezon_bridge import RezonBridgeError, assess_snapshot

SCHEMA = "tkik.rezon_snapshot_inspection.v1"
MAX_INPUT_BYTES = 1_048_576


class InvalidSnapshot(ValueError):
    pass


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise InvalidSnapshot("duplicate JSON key")
        result[key] = value
    return result


def _invalid_constant(_value):
    raise InvalidSnapshot("non-standard JSON number")


def inspect_bytes(raw: bytes) -> dict:
    """Return only nonsecret metadata; never trust labels as independent identity."""
    if type(raw) is not bytes or len(raw) > MAX_INPUT_BYTES:
        raise InvalidSnapshot("invalid input size")
    try:
        snapshot = json.loads(
            raw.decode("utf-8"), object_pairs_hook=_unique_object,
            parse_constant=_invalid_constant,
        )
        result = assess_snapshot(snapshot)
    except (UnicodeError, ValueError, TypeError, RecursionError, OverflowError) as exc:
        raise InvalidSnapshot("invalid or inconsistent Rezon snapshot") from None
    return {
        "schema": SCHEMA,
        "structural_check": "PASS",
        "phase": result.phase,
        "episode_id": result.episode_id,
        "input_digest": result.input_digest,
        "answer_count": result.answer_count,
        "review_count": result.review_count,
        "current_synthesis_count": result.current_synthesis_count,
        "missing_agents": list(result.missing_agents),
        "missing_reviews": list(result.missing_reviews),
        "origin_verified": False,
        "independence_verified": False,
        "authority": "NONE",
        "sustain_authorized": False,
    }


def main(argv=None, *, stdin=None, stdout=None) -> int:
    parser = argparse.ArgumentParser(
        description="Inspect a Rezon Collective V1 exported JSON snapshot (read-only)"
    )
    parser.add_argument("snapshot", help="UTF-8 JSON path or - for stdin")
    parser.add_argument(
        "--require-reviewed", action="store_true",
        help="exit 3 unless every enrolled worker answered and reviewed",
    )
    args = parser.parse_args(argv)
    out = sys.stdout if stdout is None else stdout
    source = sys.stdin.buffer if stdin is None else stdin
    try:
        if args.snapshot == "-":
            data = source.read(MAX_INPUT_BYTES + 1)
        else:
            with Path(args.snapshot).open("rb") as handle:
                data = handle.read(MAX_INPUT_BYTES + 1)
        report = inspect_bytes(data)
    except (OSError, InvalidSnapshot):
        print(json.dumps({
            "schema": SCHEMA, "structural_check": "FAIL",
            "error": "invalid_or_unreadable_snapshot", "authority": "NONE",
        }, sort_keys=True), file=out)
        return 2
    print(json.dumps(report, ensure_ascii=True, sort_keys=True), file=out)
    if args.require_reviewed and report["phase"] != "REVIEWED_UNVERIFIED":
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
