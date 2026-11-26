import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tkik.advocate import advisory, require_worker, verify_weights


class AdvocateTests(unittest.TestCase):
    def test_contradiction_is_advisory_only(self):
        result = advisory("The door is open.", "The door is shut.", lambda a, b: (8, 0, 0))
        self.assertEqual(result["advice"], "REVIEW_POSSIBLE_CONTRADICTION")
        self.assertEqual(result["authority"], "NONE")
        self.assertIs(result["effect"], False)
        self.assertEqual(result["claim_sha256"], hashlib.sha256(b"The door is shut.").hexdigest())

    def test_neutral_does_not_mean_false(self):
        self.assertEqual(advisory("A", "B", lambda a, b: (0, 0, 8))["advice"],
                         "INSUFFICIENT_TEXTUAL_SUPPORT")

    def test_entailment_not_truth(self):
        self.assertEqual(advisory("A", "A", lambda a, b: (0, 8, 0))["advice"],
                         "TEXTUAL_SUPPORT_ONLY")

    def test_ambiguous_abstains(self):
        self.assertEqual(advisory("A", "B", lambda a, b: (1, 1, 1))["advice"], "ABSTAIN")

    def test_invalid_scores_refused(self):
        for scores in ((1, 2), (1, 2, float("nan")), (1, 2, float("inf"))):
            with self.subTest(scores=scores), self.assertRaises(ValueError):
                advisory("A", "B", lambda a, b: scores)

    def test_blank_or_oversized_evidence_refused(self):
        for text in ("", " ", "x" * 4001):
            with self.subTest(text=text[:10]), self.assertRaises(ValueError):
                advisory(text, "B", lambda a, b: self.fail("must not score"))

    def test_worker_mismatch_refused(self):
        with patch("tkik.advocate.socket.gethostname", return_value="approved"):
            require_worker("APPROVED")
            with self.assertRaises(RuntimeError):
                require_worker("other")

    def test_weight_digest_required(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "model.safetensors"
            path.write_bytes(b"synthetic")
            with self.assertRaises(ValueError):
                verify_weights(folder)
            with patch("tkik.advocate.WEIGHTS_SHA256", hashlib.sha256(b"synthetic").hexdigest()):
                verify_weights(folder)
