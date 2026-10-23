"""Mandatory cross-review evidence for a scoped SUSTAIN determination.

Scripted objects test protocol invariants; they are not genuine model receipts.
"""
import unittest
from tkik.core import Case, Challenge, Review, ProtocolError

LENSES = ("purist_logic", "pragmatism", "bridge")
IDS = {"purist_logic": "reviewer-A", "pragmatism": "reviewer-B", "bridge": "reviewer-C"}

def panel():
    c = Case("case-peer", "A held-out intervention improved the model.",
             "Held-out performance fails to improve.", "challenger")
    for lens in LENSES:
        c.add_review(Review(lens, IDS[lens], "Finding", "Objection"))
    return c

class LiveQuorumTests(unittest.TestCase):
    def test_same_reviewer_cannot_occupy_three_lenses(self):
        c = Case("c", "hypothesis", "falsifier", "challenger")
        c.add_review(Review("purist_logic", "one-person", "f", "o"))
        with self.assertRaisesRegex(ProtocolError, "reviewer identity already"):
            c.add_review(Review("pragmatism", "one-person", "f", "o"))

    def test_sustain_cannot_pass_with_three_role_labels_but_no_dialogue(self):
        c = panel()
        with self.assertRaisesRegex(ProtocolError, "peer cross-examination"):
            c.determine("SUSTAIN", "Three role labels agree")

    def test_peer_challenge_must_target_another_reviewed_lens(self):
        c = panel()
        with self.assertRaisesRegex(ProtocolError, "different reviewed peer"):
            c.ask(Challenge("self", "purist_logic", "premise", "why?", respondent_lens="purist_logic"))
        with self.assertRaisesRegex(ProtocolError, "different reviewed peer"):
            c.ask(Challenge("unknown", "purist_logic", "premise", "why?", respondent_lens="outsider"))

    def test_peer_response_must_be_attributed_to_the_targeted_reviewer(self):
        c = panel()
        c.ask(Challenge("q1", "purist_logic", "method", "Why this sample?", respondent_lens="pragmatism"))
        with self.assertRaisesRegex(ProtocolError, "target reviewer"):
            c.resolve("q1", "ANSWERED", "A response", defender_id="reviewer-A")
        with self.assertRaisesRegex(ProtocolError, "target reviewer"):
            c.resolve("q1", "ANSWERED", "An unattributed response")
        c.resolve("q1", "ANSWERED", "Valid defense", defender_id="reviewer-B")

    def test_single_exchange_or_waiver_cannot_substitute_for_a_quorum_dialogue(self):
        c = panel()
        c.ask(Challenge("q1", "purist_logic", "method", "Explain", respondent_lens="pragmatism"))
        c.resolve("q1", "WAIVED")
        with self.assertRaisesRegex(ProtocolError, "peer cross-examination"):
            c.determine("SUSTAIN", "Waived questions imply certainty")

    def test_three_distinct_peer_rebuttals_permit_scoped_sustain(self):
        c = panel()
        edges = (("purist_logic", "pragmatism"), ("pragmatism", "bridge"),
                 ("bridge", "purist_logic"))
        for index, (challenger, respondent) in enumerate(edges):
            case_id = f"q-{index}"
            c.ask(Challenge(case_id, challenger, "premise", f"Objection {index}",
                            respondent_lens=respondent))
            c.resolve(case_id, "ANSWERED", f"Evidence-bound answer {index}",
                      defender_id=IDS[respondent])
        c.determine("SUSTAIN", "Three answered peer objections; only within specified scope")
        self.assertEqual(c.verdict, "SUSTAIN")

    def test_refine_and_withdraw_remain_possible_without_synthetic_peer_evidence(self):
        c = panel()
        c.determine("REFINE", "Insufficient grounds; do not claim qualified dialogue")
        self.assertEqual(c.verdict, "REFINE")
        separate = Case("c", "h", "f", "p")
        separate.withdraw("Challenger retracts claim")
        self.assertEqual(separate.verdict, "WITHDRAW")


if __name__ == "__main__":
    unittest.main()
