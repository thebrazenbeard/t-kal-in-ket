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


if __name__ == "__main__":
    unittest.main()
