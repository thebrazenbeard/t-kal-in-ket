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

    def test_no_inference_attestation_or_abstained_label(self):
        result = advisory("A", "B", lambda a, b: (1, 1, 1))
        self.assertIsNone(result.get("label"))
        self.assertIs(result.get("execution_attested"), False)
        self.assertNotIn("model", result)

    def test_boolean_and_unbounded_scores_rejected(self):
        with self.assertRaises(ValueError):
            advisory("A", "B", lambda a, b: (True, 0, 0))
        read = []
        def scores(a, b):
            for i in range(64):
                read.append(i)
                yield 1
        with self.assertRaises(ValueError):
            advisory("A", "B", scores)
        self.assertEqual(len(read), 4)

    def test_invalid_frames_rejected_before_loading(self):
        import io
        from tkik.advocate import main
        valid = '{"premise":"A","claim":"B"}'
        frames = ('{"premise":"A","premise":"B","claim":"C"}',
                  valid.ljust(32769) + 'junk')
        for frame in frames:
            with self.subTest(), patch("sys.stdin", io.StringIO(frame)), patch(
                "sys.argv", ["advocate", "--model-dir", ".", "--worker-hostname", "worker"]
            ), patch("tkik.advocate.local_scorer", return_value=lambda a, b: (1, 0, 0)) as loader, patch("sys.stdout", io.StringIO()), patch("sys.stderr", io.StringIO()):
                self.assertEqual(main(), 2)
                loader.assert_not_called()

    def test_loader_rejects_unverified_snapshot_before_import(self):
        import builtins
        import tkik.advocate as advocate
        names = ("config.json", "added_tokens.json", "special_tokens_map.json",
                 "spm.model", "tokenizer.json", "tokenizer_config.json")
        values = {name: name.encode() for name in names}
        values["model.safetensors"] = b"weights"
        digests = {name: hashlib.sha256(values[name]).hexdigest() for name in names}
        original_import = builtins.__import__
        def stop_at_loader(name, *args, **kwargs):
            if name == "torch":
                raise AssertionError("reached model loader")
            return original_import(name, *args, **kwargs)
        for mode in ("missing", "tampered", "extra", "valid"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as folder:
                root = Path(folder)
                for name, value in values.items():
                    (root / name).write_bytes(value)
                if mode == "missing":
                    (root / "config.json").unlink()
                elif mode == "tampered":
                    (root / "tokenizer.json").write_bytes(b"changed")
                elif mode == "extra":
                    (root / "adapter_config.json").write_bytes(b"{}")
                else:
                    (root / ".cache").mkdir()
                with patch.object(advocate, "SNAPSHOT_SHA256", digests, create=True), patch.object(
                    advocate, "WEIGHTS_SHA256", hashlib.sha256(values["model.safetensors"]).hexdigest()
                ), patch.object(advocate, "require_worker"), patch("builtins.__import__", side_effect=stop_at_loader):
                    if mode == "valid":
                        with self.assertRaisesRegex(AssertionError, "reached model loader"):
                            advocate.local_scorer(root, "worker")
                    else:
                        with self.assertRaisesRegex(ValueError, "snapshot"):
                            advocate.local_scorer(root, "worker")
