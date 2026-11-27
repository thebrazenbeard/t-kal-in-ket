import unittest
from tkik.core import Case, Review, Evidence, Challenge, ProtocolError


def case():
    return Case("c", "Intervention improves held-out accuracy",
                "No accuracy improvement on preregistered tasks", "person")


class ProtocolTests(unittest.TestCase):
    def test_required_fields(self):
        with self.assertRaises(ProtocolError):
            Case("", "claim", "falsifier", "proposer")

    def test_no_determination_without_all_three(self):
        c = case()
        with self.assertRaises(ProtocolError):
            c.determine("SUSTAIN", "because")

    def test_each_lens_once(self):
        c = case()
        r = Review("purist_logic", "reviewer", "finding", "attack")
        c.add_review(r)
        with self.assertRaises(ProtocolError):
            c.add_review(r)

    def test_one_challenge_per_exchange(self):
        c = case()
        c.ask(Challenge("q1", "bridge", "premise", "why?"))
        with self.assertRaises(ProtocolError):
            c.ask(Challenge("q2", "bridge", "method", "how?"))

    def test_unanswered_attack_not_concession(self):
        c = case()
        for lens in ("purist_logic", "pragmatism", "bridge"):
            c.add_review(Review(lens, lens, "finding", "challenge"))
        c.ask(Challenge("q", "bridge", "method", "how?"))
        with self.assertRaises(ProtocolError):
            c.determine("SUSTAIN", "logic")
        c.resolve("q", "ANSWERED", "Documented protocol")
        c.determine("REFINE", "More evidence needed")
        self.assertEqual(c.state, "CLOSED")

    def test_partial_answer_blocks(self):
        c = case()
        for lens in ("purist_logic", "pragmatism", "bridge"):
            c.add_review(Review(lens, lens, "finding", "challenge"))
        c.ask(Challenge("q", "bridge", "method", "how?"))
        c.resolve("q", "PARTLY_ANSWERED", "Incomplete")
        with self.assertRaises(ProtocolError):
            c.determine("SUSTAIN", "logic")

    def test_evidence_requires_source(self):
        c = case()
        with self.assertRaises(ProtocolError):
            c.add_evidence(Evidence("e", "x", "", "test", "unknown", "unknown"))

    def test_withdraw_without_reviews(self):
        c = case()
        c.withdraw("proposer retracts claim")
        self.assertEqual(c.state, "WITHDRAWN")
        with self.assertRaises(ProtocolError):
            c.add_review(Review("bridge", "x", "x", "x"))

    def test_zero_attack_refine_requires_explicit_waiver(self):
        c = case()
        for lens in ("purist_logic", "pragmatism", "bridge"):
            c.add_review(Review(lens, lens, "finding", "challenge"))
        with self.assertRaisesRegex(ProtocolError, "zero-challenge"):
            c.determine("REFINE", "More evidence is needed")
        c.waive_cross_examination("No material attack could be framed within the case scope")
        self.assertEqual(
            c.cross_examination_waiver_reason,
            "No material attack could be framed within the case scope",
        )
        c.determine("REFINE", "More evidence is needed")
        self.assertEqual(c.verdict, "REFINE")

    def test_zero_attack_waiver_requires_a_nonempty_reason(self):
        c = case()
        with self.assertRaises(ProtocolError):
            c.waive_cross_examination("  ")

    def test_zero_attack_waiver_cannot_be_reused_or_followed_by_an_attack(self):
        c = case()
        c.waive_cross_examination("No material attack could be framed")
        with self.assertRaisesRegex(ProtocolError, "already recorded"):
            c.waive_cross_examination("Replacement reason")
        with self.assertRaisesRegex(ProtocolError, "waiver"):
            c.ask(Challenge("late", "bridge", "scope", "What changed?"))

    def test_zero_attack_waiver_cannot_be_recorded_after_any_attack(self):
        c = case()
        c.ask(Challenge("q", "bridge", "scope", "What changed?"))
        c.resolve("q", "SKIPPED")
        with self.assertRaisesRegex(ProtocolError, "before any challenge"):
            c.waive_cross_examination("No further attack")

    def test_zero_attack_waiver_does_not_bypass_sustain_exchange(self):
        c = case()
        for lens in ("purist_logic", "pragmatism", "bridge"):
            c.add_review(Review(lens, lens, "finding", "challenge"))
        c.waive_cross_examination("Zero-attack REFINE only")
        with self.assertRaisesRegex(ProtocolError, "SUSTAIN requires peer cross-examination"):
            c.determine("SUSTAIN", "Supported")

    def test_sustain_still_requires_and_accepts_the_three_lens_exchange(self):
        c = case()
        for lens in ("purist_logic", "pragmatism", "bridge"):
            c.add_review(Review(lens, lens, "finding", "challenge"))
        exchanges = (
            ("purist_logic", "pragmatism", "q1"),
            ("pragmatism", "bridge", "q2"),
            ("bridge", "purist_logic", "q3"),
        )
        for source, target, identifier in exchanges:
            c.ask(Challenge(
                identifier, source, "the method", "What evidence supports this?",
                respondent_lens=target,
            ))
            c.resolve(
                identifier, "ANSWERED", "The cited evidence supports this within scope",
                defender_id=target,
            )
        c.determine("SUSTAIN", "All three lenses exchanged attributed answers")
        self.assertEqual(c.verdict, "SUSTAIN")

    def test_zero_attack_waiver_freezes_the_proposition(self):
        c = case()
        c.waive_cross_examination("No material attack could be framed")
        c.hypothesis = "A different proposition"
        with self.assertRaisesRegex(ProtocolError, "frozen proposition changed"):
            c.add_review(Review("purist_logic", "logic", "finding", "challenge"))

    def test_partly_answered_attack_cannot_be_replaced_by_zero_attack_waiver(self):
        c = case()
        for lens in ("purist_logic", "pragmatism", "bridge"):
            c.add_review(Review(lens, lens, "finding", "challenge"))
        c.ask(Challenge("q", "bridge", "scope", "What changed?"))
        c.resolve("q", "PARTLY_ANSWERED", "The response did not resolve the issue")
        with self.assertRaisesRegex(ProtocolError, "before any challenge"):
            c.waive_cross_examination("No material attack")
        with self.assertRaisesRegex(ProtocolError, "unresolved cross-examination"):
            c.determine("REFINE", "More evidence needed")


if __name__ == "__main__":
    unittest.main()
