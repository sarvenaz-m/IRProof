"""Exercise source preparation without downloading or compiling dependencies."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile


ROOT = Path(__file__).resolve().parents[2]


class BootstrapSourceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="irproof-bootstrap-")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.project = self.base / "checkout"
        scripts = self.project / "scripts"
        scripts.mkdir(parents=True)
        self.script = scripts / "bootstrap_alive2.py"
        shutil.copyfile(ROOT / "scripts/bootstrap_alive2.py", self.script)
        subprocess.run(["git", "init", "--quiet", str(self.project)], check=True)
        self.parent_file = self.project / "example.txt"
        self.parent_file.write_text("parent file\n")

        self.archive = self.base / "source.zip"
        with zipfile.ZipFile(self.archive, "w") as archive:
            archive.writestr("pinned-source/example.txt", "before\n")
        patch = self.project / "compat.patch"
        patch.write_text(
            "diff --git a/example.txt b/example.txt\n"
            "--- a/example.txt\n"
            "+++ b/example.txt\n"
            "@@ -1 +1 @@\n"
            "-before\n"
            "+after\n"
        )
        lock = {"alive2": {
            "revision": "0" * 40,
            "archiveSha256": hashlib.sha256(self.archive.read_bytes()).hexdigest(),
            "patch": patch.name,
            "patchSha256": hashlib.sha256(patch.read_bytes()).hexdigest(),
        }}
        (self.project / "toolchain.lock.json").write_text(json.dumps(lock))

    def prepare(self, prefix):
        return subprocess.run(
            [sys.executable, str(self.script), "--source-only",
             "--llvm-dir", str(self.base / "unused-llvm"),
             "--prefix", str(prefix), "--archive", str(self.archive)],
            cwd=self.project, capture_output=True, text=True,
        )

    def test_applies_patch_inside_parent_git_checkout(self):
        prefix = self.project / "build-tools"
        result = self.prepare(prefix)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual((prefix / "alive2-src/example.txt").read_text(), "after\n")
        self.assertEqual(self.parent_file.read_text(), "parent file\n")
        self.assertTrue((prefix / "alive2-src/.irproof-source.json").is_file())

    def test_source_outside_checkout_can_be_reused(self):
        prefix = self.base / "standalone"
        for _ in range(2):
            result = self.prepare(prefix)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual((prefix / "alive2-src/example.txt").read_text(), "after\n")

    def test_rejects_cached_source_with_unapplied_patch(self):
        prefix = self.project / "build-tools"
        result = self.prepare(prefix)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        (prefix / "alive2-src/example.txt").write_text("before\n")
        result = self.prepare(prefix)
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("Prepared pinned source", result.stdout)


if __name__ == "__main__":
    unittest.main()
