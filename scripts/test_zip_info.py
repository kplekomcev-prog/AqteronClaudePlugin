import hashlib
import importlib.util
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest
import zipfile
from types import SimpleNamespace
from unittest.mock import patch

MODULE = pathlib.Path(__file__).resolve().parents[1] / "plugins/aqteron/skills/publish-aqteron-app/scripts/zip_info.py"
spec = importlib.util.spec_from_file_location("zip_info", MODULE)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class ZipInfoTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = pathlib.Path(self.tmp.name) / "app.zip"
        self.private_content = b"PRIVATE_ARCHIVE_CONTENT_MUST_NOT_BE_PRINTED"
        with zipfile.ZipFile(self.path, "w") as archive:
            archive.writestr("index.html", self.private_content)

    def tearDown(self):
        self.tmp.cleanup()

    def cli(self, *extra):
        return subprocess.run([sys.executable, str(MODULE), str(self.path), *extra],
                              capture_output=True, text=True, check=False)

    def test_only_metadata_for_exact_local_bytes(self):
        data = self.path.read_bytes()
        self.assertEqual(m.inspect_zip(self.path), {
            "filename": "app.zip", "size_bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
        })

    def test_cli_returns_one_metadata_object_without_archive_content(self):
        result = self.cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertEqual(json.loads(result.stdout), m.inspect_zip(self.path))
        self.assertNotIn(self.private_content.decode(), result.stdout)
        self.assertNotIn(str(self.path), result.stdout)
        self.assertEqual(len(result.stdout.splitlines()), 1)

    def test_old_chunk_arguments_are_rejected(self):
        result = self.cli("--transfer-id", "00000000-0000-0000-0000-000000000001", "--chunk-index", "0")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("unrecognized arguments", result.stderr)

    def test_empty_nonzip_and_oversize_inputs_are_rejected(self):
        for kind in ("empty", "nonzip", "oversize"):
            with self.subTest(kind=kind):
                with self.path.open("wb") as target:
                    if kind == "nonzip":
                        target.write(self.private_content)
                    elif kind == "oversize":
                        target.truncate(m.MAX_BYTES + 1)
                with self.assertRaises(ValueError):
                    m.inspect_zip(self.path)
                result = self.cli()
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, "")
                self.assertNotIn(self.private_content.decode(), result.stderr)

    def test_exact_ten_mib_zip_is_accepted(self):
        with zipfile.ZipFile(self.path, "w", compression=zipfile.ZIP_STORED) as archive:
            archive.writestr("index.html", b"")
        overhead = self.path.stat().st_size
        with zipfile.ZipFile(self.path, "w", compression=zipfile.ZIP_STORED) as archive:
            archive.writestr("index.html", b"x" * (m.MAX_BYTES - overhead))
        self.assertEqual(self.path.stat().st_size, m.MAX_BYTES)
        self.assertEqual(m.inspect_zip(self.path)["size_bytes"], m.MAX_BYTES)

    def test_modified_file_is_rejected(self):
        before = self.path.stat()
        changed = SimpleNamespace(st_size=before.st_size, st_mtime_ns=before.st_mtime_ns + 1)
        with patch.object(m.os, "fstat", side_effect=[before, changed]):
            with self.assertRaisesRegex(ValueError, "changed"):
                m.inspect_zip(self.path)

    def test_read_error_does_not_expose_private_path(self):
        self.path = pathlib.Path(self.tmp.name) / "PRIVATE_MISSING_PATH.zip"
        result = self.cli()
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertNotIn(str(self.path), result.stderr)
        self.assertNotIn("PRIVATE_MISSING_PATH", result.stderr)


if __name__ == "__main__":
    unittest.main()
