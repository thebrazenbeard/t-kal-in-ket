"""CLI remains a clearly labeled scripted demonstration, not a live quorum."""
import pathlib
import subprocess
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]

class DemonstrationTests(unittest.TestCase):
    def test_cli_still_runs_without_claiming_independent_peer_execution(self):
        result = subprocess.run([sys.executable, "-m", "tkik.cli"],
                                cwd=ROOT, capture_output=True, text=True,
                                timeout=20)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("REFINE", result.stdout)
        self.assertIn("Demonstration", result.stdout)

if __name__ == "__main__":
    unittest.main()
