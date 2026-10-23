"""Offline inspection behavior and adversarial input cases."""
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from tkik.inspect_rezon import (
    MAX_INPUT_BYTES, InvalidSnapshot, inspect_bytes, main,
)
from test_rezon_bridge import snapshot, _digest_from


def encoded(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True).encode("utf-8")


class InspectTests(unittest.TestCase):
    def test_valid_snapshot_never_claims_independent_model_or_authority(self):
        doc = inspect_bytes(encoded(snapshot()))
        self.assertEqual(doc["phase"], "REVIEWED_UNVERIFIED")
        self.assertEqual(doc["structural_check"], "PASS")
        self.assertEqual(doc["authority"], "NONE")
        self.assertFalse(doc["independence_verified"])
        self.assertFalse(doc["origin_verified"])
        self.assertFalse(doc["sustain_authorized"])

    def test_real_command_path_and_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "record.json"
            p.write_bytes(encoded(snapshot()))
            result = subprocess.run(
                [sys.executable, "-m", "tkik.inspect_rezon", str(p),
                 "--require-reviewed"], capture_output=True, text=True,
                timeout=10, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(report["review_count"], 3)
            self.assertEqual(report["authority"], "NONE")
            self.assertFalse(report["origin_verified"])

    def test_noncompleted_snapshot_exits_three_without_false_proof(self):
        item = snapshot()
        item["reviews"] = []
        item["syntheses"] = []
        item["input_digest"] = _digest_from(item)
        output = io.StringIO()
        ret = main(["-", "--require-reviewed"],
                   stdin=io.BytesIO(encoded(item)), stdout=output)
        self.assertEqual(ret, 3)
        self.assertEqual(json.loads(output.getvalue())["phase"], "AWAITING_REVIEWS")

    def test_invalid_digest_does_not_echo_sensitive_input(self):
        item = snapshot()
        item["answers"][0]["content"] = "PRIVATE_SECRET_SENTINEL"
        output = io.StringIO()
        ret = main(["-"], stdin=io.BytesIO(encoded(item)), stdout=output)
        self.assertEqual(ret, 2)
        self.assertEqual(json.loads(output.getvalue())["structural_check"], "FAIL")
        self.assertNotIn("PRIVATE_SECRET_SENTINEL", output.getvalue())

    def test_duplicate_key_rejected_before_digest_check(self):
        raw = encoded(snapshot())
        self.assertIn(b'"input_digest"', raw)
        dup = raw[:-1] + b', "input_digest":"'+b'0'*64+b'"}'
        with self.assertRaises(InvalidSnapshot):
            inspect_bytes(dup)

    def test_nonstandard_number_and_invalid_utf8(self):
        for raw in (b'{"value":NaN}', b'\xff\xfe'):
            with self.subTest(raw=raw):
                with self.assertRaises(InvalidSnapshot):
                    inspect_bytes(raw)

    def test_one_megabyte_ceiling(self):
        with self.assertRaises(InvalidSnapshot):
            inspect_bytes(b"x" * (MAX_INPUT_BYTES + 1))

    def test_wrong_nested_type_uses_controlled_failure(self):
        item = snapshot()
        item["answers"][0]["agent_id"] = {"not": "a string"}
        output = io.StringIO()
        self.assertEqual(main(["-"], stdin=io.BytesIO(encoded(item)),
                              stdout=output), 2)
        self.assertEqual(json.loads(output.getvalue())["error"],
                         "invalid_or_unreadable_snapshot")

    def test_unavailable_path_fails_closed(self):
        output = io.StringIO()
        ret = main(["/no_such_snapshot_path_tkik_2026.json"], stdout=output)
        self.assertEqual(ret, 2)
        self.assertEqual(json.loads(output.getvalue())["authority"], "NONE")


if __name__ == "__main__":
    unittest.main()
