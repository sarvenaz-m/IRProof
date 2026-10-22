import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("irproof", Path(__file__).resolve().parents[2] / "scripts/irproof.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def summary(correct=0, incorrect=0, failed=0, errors=0):
    return f"Summary:\n  {correct} correct transformations\n  {incorrect} incorrect transformations\n  {failed} failed-to-prove transformations\n  {errors} Alive2 errors\n"


class VerdictTests(unittest.TestCase):
    def check(self, output, expected, code=0, timeout=False):
        status, reason = module.classify({"stdout": output, "stderr": "", "exitCode": code, "timedOut": timeout})
        self.assertEqual(status, expected)
        self.assertTrue(reason)

    def test_complete_single_proof(self):
        self.check(summary(correct=1), "proved")

    def test_exit_success_does_not_mean_proof(self):
        self.check("", "error")

    def test_zero_matches_is_not_vacuous_success(self):
        self.check(summary(), "error")

    def test_counterexample_can_have_zero_exit_code(self):
        self.check(summary(incorrect=1), "refuted")

    def test_partial_success_is_unknown(self):
        self.check(summary(correct=1, failed=1), "unknown")

    def test_timeout_after_success_is_unknown(self):
        self.check(summary(correct=1), "unknown", timeout=True)

    def test_crash_after_success_is_error(self):
        self.check(summary(correct=1), "error", code=-11)

    def test_nonzero_exit_after_success_is_error(self):
        self.check(summary(correct=1), "error", code=1)

    def test_unsupported_is_unknown(self):
        self.check("ERROR: Unsupported instruction atomicrmw\n" + summary(errors=1), "unknown", code=1)

    def test_syntax_error_is_error(self):
        self.check("error: expected type\n" + summary(errors=1), "error", code=1)

    def test_multiple_proofs_need_explicit_accounting(self):
        self.check(summary(correct=2), "error")

    def test_success_phrase_without_summary_is_error(self):
        self.check("Transformation seems to be correct!", "error")


if __name__ == "__main__":
    unittest.main()
