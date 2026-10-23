"""Read-only verification of Rezon CollectiveSnapshot.to_dict() payloads.

Bound to Rezon Collective V1 as inspected at
thebrazenbeard/rezon@72e9ec97e39eb0f0cfed0e62c5252f027b25ecb9,
src/rezon/collective.py. This verifies structural/digest consistency,
NOT the origin of a host, a provider response, or evidence truth.

This module never connects to Rezon, invokes models, or promotes verdicts.
"""
from dataclasses import dataclass
from hashlib import sha256
import json
import re


class RezonBridgeError(ValueError):
    pass


_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,63}\Z")
_HEX = re.compile(r"[0-9a-f]{64}\Z")


def _canonical(payload):
    return json.dumps(payload, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False)


def _nonempty(value):
    return type(value) is str and bool(value.strip())


def _assert(condition, message):
    if not condition:
        raise RezonBridgeError(message)


@dataclass(frozen=True)
class CollectiveAssessment:
    episode_id: str
    input_digest: str
    answer_count: int
    review_count: int
    missing_agents: tuple[str, ...]
    missing_reviews: tuple[str, ...]
    current_synthesis_count: int
    phase: str
    origin_verified: bool = False
    # Rezon's digest is an integrity consistency check, not a signature.


def assess_snapshot(snapshot: dict) -> CollectiveAssessment:
    """Validate Rezon's public snapshot shape without trusting its assertions.

    A structurally valid assessment is *not* a TKIK Review or a permission
    to call Case.determine(). A separate mapping and provenance approval
    remain required.
    """
    _assert(type(snapshot) is dict, "snapshot must be object")
    required = ("episode_id", "prompt", "agents", "answers", "reviews",
                "syntheses", "missing_agents", "complete", "input_digest")
    _assert(all(k in snapshot for k in required), "missing snapshot field")
    episode = snapshot["episode_id"]
    agents = snapshot["agents"]
    _assert(_nonempty(episode) and _nonempty(snapshot["prompt"]),
            "episode and prompt required")
    _assert(type(agents) is list and 1 <= len(agents) <= 32,
            "agent roster invalid")
    _assert(all(type(a) is str and _ID.fullmatch(a) for a in agents),
            "agent id invalid")
    _assert(len(agents) == len(set(agents)), "duplicate agent")
    _assert(type(snapshot["complete"]) is bool, "complete flag invalid")
    digest = snapshot["input_digest"]
    _assert(type(digest) is str and _HEX.fullmatch(digest), "digest invalid")
    _assert(type(snapshot["answers"]) is list and
            type(snapshot["reviews"]) is list, "contributions must be lists")
    contributions = []
    by_kind = {"answer": set(), "review": set()}
    answer_ids = set()
    for kind, field in (("answer", "answers"), ("review", "reviews")):
        for item in snapshot[field]:
            _assert(type(item) is dict, "invalid contribution")
            keys = ("id", "agent_id", "kind", "content", "source_refs", "target_ids")
            _assert(all(k in item for k in keys), "missing contribution field")
            agent = item["agent_id"]
            _assert(agent in agents and type(agent) is str,
                    "contributor outside roster")
            _assert(item["kind"] == kind and item["id"] == f"{kind}:{agent}",
                    "contribution identity mismatch")
            _assert(agent not in by_kind[kind], "duplicate contribution")
            by_kind[kind].add(agent)
            _assert(_nonempty(item["content"]) and len(item["content"]) <= 32768,
                    "invalid contribution text")
            refs, targets = item["source_refs"], item["target_ids"]
            _assert(type(refs) is list and type(targets) is list,
                    "invalid references")
            for label, values in (("source", refs), ("target", targets)):
                _assert(len(values) <= 32 and
                        all(type(v) is str and 0 < len(v) <= 1024 for v in values) and
                        len(values) == len(set(values)),
                        f"invalid {label} references")
            if kind == "answer":
                _assert(not targets, "answer must not target peers")
                answer_ids.add(item["id"])
            contributions.append({
                "contribution_id": item["id"], "agent_id": agent,
                "kind": kind, "content": item["content"],
                "source_refs": refs, "target_ids": targets,
            })
    _assert(contributions == sorted(contributions,
                                    key=lambda row: (row["kind"], row["agent_id"])),
            "noncanonical contribution ordering")
    for review in snapshot["reviews"]:
        _assert(bool(review["target_ids"]) and
                set(review["target_ids"]).issubset(answer_ids),
                "review must target an existing answer")
        _assert(f"answer:{review['agent_id']}" not in review["target_ids"],
                "self-target review does not count")
    missing = tuple(a for a in agents if a not in by_kind["answer"])
    _assert(type(snapshot["missing_agents"]) is list and
            tuple(snapshot["missing_agents"]) == missing,
            "missing-agent list mismatch")
    _assert(snapshot["complete"] == (not missing), "complete flag mismatch")
    basis = {
        "episode_id": episode, "prompt": snapshot["prompt"],
        "agents": agents, "contributions": contributions
    }
    actual = sha256(_canonical(basis).encode("utf-8")).hexdigest()
    _assert(digest == actual, "snapshot digest mismatch")
    syntheses = snapshot["syntheses"]
    _assert(type(syntheses) is list, "invalid syntheses")
    current = 0
    for item in syntheses:
        _assert(type(item) is dict and "input_digest" in item and
                "is_current" in item and "content" in item, "invalid synthesis")
        _assert(type(item["input_digest"]) is str and
                _HEX.fullmatch(item["input_digest"]), "invalid synthesis digest")
        should_current = item["input_digest"] == digest
        _assert(type(item["is_current"]) is bool and
                item["is_current"] == should_current,
                "stale/current synthesis flag mismatch")
        if should_current:
            current += 1
    missing_reviews = tuple(a for a in agents if a not in by_kind["review"])
    phase = ("AWAITING_ANSWERS" if missing else
             "AWAITING_REVIEWS" if missing_reviews else
             "REVIEWED_UNVERIFIED")
    return CollectiveAssessment(
        episode_id=episode, input_digest=digest,
        answer_count=len(by_kind["answer"]), review_count=len(by_kind["review"]),
        missing_agents=missing, missing_reviews=missing_reviews,
        current_synthesis_count=current, phase=phase,
    )
