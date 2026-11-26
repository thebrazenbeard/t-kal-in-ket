import unittest
from tkik.live import LiveQuorum, LiveError

class LiveTests(unittest.TestCase):
    def setup_case(self):
        q = LiveQuorum("case", ["one", "two", "three"], "chair")
        for seat in q.seats:
            q.admit(seat, "ready:" + seat)
        q.open("chair")
        q.propose("one", "claim", "benefit", "simpler", "falsifier", "source")
        return q

    def test_admission(self):
        q = LiveQuorum("case", ["one", "two"], "chair")
        q.admit("one", "r1")
        with self.assertRaises(LiveError): q.open("chair")
        with self.assertRaises(LiveError): q.admit("one", "r2")

    def test_passive_and_wrong_floor(self):
        q = self.setup_case()
        with self.assertRaises(LiveError): q.advance("two", "KEEP", "agree")
        with self.assertRaises(LiveError): q.examine("three", "EVIDENCE", "t", "f", "s")
        with self.assertRaises(LiveError): q.examine("two", "AGREE", "t", "f", "s")

    def test_defense_required(self):
        q = self.setup_case()
        q.examine("two", "ATTACK", "premise", "counterpoint", "source")
        with self.assertRaises(LiveError): q.advance("two", "KEEP", "skip")
        q.ask("two", "one", "why?")
        with self.assertRaises(LiveError): q.defend("three", "fake", "r")
        with self.assertRaises(LiveError): q.close("chair", "SUSTAIN", "early")
        q.defend("one", "answer", "r")
        q.resolve("two", "PARTLY_ANSWERED", "needs clarification")
        self.assertEqual(q.frontier()["floor"], "one")
        q.defend("one", "clarification", "r2")
        q.resolve("two", "ANSWERED", "resolved")
        q.advance("two", "KEEP", "reason")
        self.assertEqual(q.floor, "three")

    def test_repeated_and_completion(self):
        q = self.setup_case()
        q.examine("two", "EVIDENCE", "target", "finding", "s1")
        q.advance("two", "KEEP", "reason")
        with self.assertRaises(LiveError): q.examine("three", "EVIDENCE", " TARGET ", "Finding", "s2")
        q.examine("three", "COUNTEREXAMPLE", "other", "new", "s2")
        q.advance("three", "KEEP", "reason")
        q.close("chair", "SUSTAIN", "scope")
        self.assertEqual(q.verdict, "SUSTAIN")

    def test_revision_and_withdraw(self):
        q = self.setup_case()
        q.examine("two", "REFINEMENT", "target", "new", "s")
        q.advance("two", "REFINE", "reason", "narrow claim")
        q.examine("three", "EVIDENCE", "other", "new", "s")
        q.advance("three", "KEEP", "reason")
        with self.assertRaises(LiveError): q.close("chair", "SUSTAIN", "unreviewed")
        with self.assertRaises(LiveError): q.withdraw("chair", "not proposer")
        q.close("chair", "REFINE", "needs new case")
        q = self.setup_case()
        q.withdraw("one", "no benefit")
        q.close("chair", "WITHDRAW", "conceded")
