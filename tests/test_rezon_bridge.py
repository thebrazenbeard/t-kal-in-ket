"""Adversarial regression checks for Rezon Collective V1 snapshot import."""
import copy
from hashlib import sha256
import json
import unittest

from tkik.core import Case, Review, Challenge, ProtocolError
from tkik.rezon_bridge import RezonBridgeError, assess_snapshot


def canonical(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"))


def snapshot():
    agents = ["bridge", "logic", "pragmatism"]
    contributions = []
    for agent in agents:
        contributions.append({
            "contribution_id": f"answer:{agent}", "agent_id": agent,
            "kind": "answer", "content": f"First answer from {agent}",
            "source_refs": (), "target_ids": (),
        })
    for agent, peer in zip(agents, agents[1:] + agents[:1]):
        contributions.append({
            "contribution_id": f"review:{agent}", "agent_id": agent,
            "kind": "review", "content": f"Challenge by {agent}",
            "source_refs": (), "target_ids": (f"answer:{peer}",),
        })
    digest = sha256(canonical({
        "episode_id": "test-episode", "prompt": "Is the claim falsifiable?",
        "agents": agents, "contributions": contributions
    }).encode("utf-8")).hexdigest()
    def view(c):
        return {"id": c["contribution_id"], "agent_id": c["agent_id"],
                "kind": c["kind"], "content": c["content"],
                "source_refs": list(c["source_refs"]),
                "target_ids": list(c["target_ids"])}
    return {
        "episode_id": "test-episode", "prompt": "Is the claim falsifiable?",
        "agents": agents,
        "answers": [view(c) for c in contributions if c["kind"] == "answer"],
        "reviews": [view(c) for c in contributions if c["kind"] == "review"],
        "syntheses": [{"input_digest": digest, "content": "Candidate only",
                       "is_current": True}],
        "missing_agents": [], "complete": True, "input_digest": digest,
    }


class BridgeTests(unittest.TestCase):
    def test_complete_snapshot_is_not_origin_verified(self):
        result = assess_snapshot(snapshot())
        self.assertEqual(result.phase, "REVIEWED_UNVERIFIED")
        self.assertEqual(result.review_count, 3)
        self.assertFalse(result.origin_verified)

    def test_edited_answer_rejected_even_if_claimed_complete(self):
        changed = snapshot()
        changed["answers"][0]["content"] += " tampered"
        with self.assertRaisesRegex(RezonBridgeError, "digest mismatch"):
            assess_snapshot(changed)

    def test_fabricated_completion_rejected(self):
        changed = snapshot()
        changed["answers"].pop()
        with self.assertRaises(RezonBridgeError):
            assess_snapshot(changed)

    def test_duplicate_and_self_review_rejected(self):
        changed = snapshot()
        changed["reviews"][0]["target_ids"] = ["answer:bridge"]
        with self.assertRaisesRegex(RezonBridgeError, "self-target"):
            assess_snapshot(changed)

    def test_stale_synthesis_cannot_claim_current(self):
        changed = snapshot()
        changed["syntheses"][0]["input_digest"] = "0" * 64
        with self.assertRaisesRegex(RezonBridgeError, "stale/current"):
            assess_snapshot(changed)
        changed["syntheses"][0]["is_current"] = False
        self.assertEqual(assess_snapshot(changed).current_synthesis_count, 0)

    def test_review_not_proof_of_qualification(self):
        assessed = assess_snapshot(snapshot())
        case = Case("c", "H", "not H", "proposer")
        with self.assertRaises(ProtocolError):
            case.determine("SUSTAIN", assessed.phase)

    def test_missing_reviews_are_distinguished(self):
        changed = snapshot()
        changed["reviews"] = []
        changed["syntheses"] = []
        changed["input_digest"] = _digest_from(changed)
        result = assess_snapshot(changed)
        self.assertEqual(result.phase, "AWAITING_REVIEWS")
        self.assertEqual(len(result.missing_reviews), 3)

    def test_partial_challenge_can_be_reopened_and_resolved(self):
        c = Case("c", "H", "not H", "proposer")
        for lens in ("purist_logic", "pragmatism", "bridge"):
            c.add_review(Review(lens, lens, "finding", "objection"))
        c.ask(Challenge("q", "bridge", "method", "What controls?"))
        c.resolve("q", "PARTLY_ANSWERED", "One control supplied")
        with self.assertRaises(ProtocolError):
            c.ask(Challenge("next", "bridge", "sample", "Sample size?"))
        c.resolve("q", "ANSWERED", "Full controls and sample provided")
        c.ask(Challenge("next", "bridge", "sample", "Sample size?"))
        c.resolve("next", "CONCEDED", "Sample too small")
        c.determine("REFINE", "Revise sampling plan")

    def test_no_silent_cross_examination_bypass(self):
        c = Case("c", "H", "not H", "proposer")
        for lens in ("purist_logic", "pragmatism", "bridge"):
            c.add_review(Review(lens, lens, "finding", "objection"))
        with self.assertRaises(ProtocolError):
            c.determine("SUSTAIN", "all three reviewed but no exchange")
        c.determine("REFINE", "More tests needed")
        self.assertEqual(c.state, "CLOSED")

    def test_partial_or_unresolved_must_be_revisited_before_next_attack(self):
        c = Case("c", "H", "not H", "proposer")
        c.ask(Challenge("first", "bridge", "scope", "Which scope?"))
        c.resolve("first", "UNRESOLVED")
        with self.assertRaises(ProtocolError):
            c.ask(Challenge("second", "bridge", "scope", "Next?"))
        c.resolve("first", "CONCEDED", "No usable scope supplied")
        c.ask(Challenge("second", "bridge", "scope", "Next?"))

    def test_no_preloaded_case_state_or_forged_verdict(self):
        for fields in (
            {"state": "CLOSED", "verdict": "SUSTAIN", "rationale": "forged"},
            {"verdict": "SUSTAIN", "rationale": "forged"},
            {"reviews": {"purist_logic": Review("purist_logic", "x", "x", "x")}},
            {"challenges": [Challenge("q", "bridge", "x", "x")]},
        ):
            with self.subTest(fields=fields):
                with self.assertRaises(ProtocolError):
                    Case("c", "H", "not H", "proposer", **fields)

    def test_chair_must_not_withdraw_for_proposer(self):
        c = Case("c", "H", "not H", "proposer")
        for lens in ("purist_logic", "pragmatism", "bridge"):
            c.add_review(Review(lens, lens, "finding", "objection"))
        with self.assertRaises(ProtocolError):
            c.determine("WITHDRAW", "chair decides")
        c.withdraw("proposer retracts claim")
        self.assertEqual(c.state, "WITHDRAWN")


def _digest_from(s):
    rows = []
    for kind in ("answers", "reviews"):
        for item in s[kind]:
            rows.append({
                "contribution_id": item["id"], "agent_id": item["agent_id"],
                "kind": item["kind"], "content": item["content"],
                "source_refs": item["source_refs"],
                "target_ids": item["target_ids"],
            })
    return sha256(canonical({
        "episode_id": s["episode_id"], "prompt": s["prompt"],
        "agents": s["agents"], "contributions": rows
    }).encode("utf-8")).hexdigest()


if __name__ == "__main__":
    unittest.main()
