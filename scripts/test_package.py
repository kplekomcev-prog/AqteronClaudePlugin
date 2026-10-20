import hashlib
import importlib.util
import json
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/package_plugin.py"
spec = importlib.util.spec_from_file_location("package_plugin", SCRIPT)
package = importlib.util.module_from_spec(spec)
spec.loader.exec_module(package)


class PackageTests(unittest.TestCase):
    def test_distributed_package_has_only_whole_file_upload_components(self):
        with tempfile.TemporaryDirectory() as directory:
            output = pathlib.Path(directory) / "release.zip"
            result = subprocess.run([sys.executable, str(SCRIPT), str(output)],
                                    capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertRegex(package.EXPECTED_SHA256, r"^[0-9a-f]{64}$")
            self.assertEqual(hashlib.sha256(output.read_bytes()).hexdigest(), package.EXPECTED_SHA256)
            with zipfile.ZipFile(output) as archive:
                self.assertIsNone(archive.testzip())
                files = {name: archive.read(name) for name in archive.namelist()}
                self.assertEqual(len(files), 7)
                self.assertTrue(all(name.startswith("aqteron-claude/") and ".." not in pathlib.PurePosixPath(name).parts for name in files))
                self.assertFalse(any("zip_chunks" in name for name in files))
                manifest = json.loads(files["aqteron-claude/.claude-plugin/plugin.json"])
                self.assertEqual((manifest["name"], manifest["version"]), ("aqteron", "0.1.9"))
                mcp = json.loads(files["aqteron-claude/.mcp.json"])
                self.assertEqual(mcp, {"mcpServers": {"aqteron": {"type": "http", "url": "https://aqteron.com/mcp"}}})
                for name, content in files.items():
                    self.assertNotIn(b"append_app_zip_chunk", content, name)
                    self.assertNotIn(b"zip_chunks.py", content, name)
                    if name.endswith((".md", ".json", ".py")):
                        self.assertIsNone(re.search(r"[\u0400-\u04FF]", content.decode()), name)
                skill = files["aqteron-claude/skills/publish-aqteron-app/SKILL.md"].decode()
                for required in ("begin_app_zip_upload", "complete_app_zip_upload", "get_app_source_zip", "get_app_source_chunk", "scripts/zip_info.py", "scripts/zip_direct.py"):
                    self.assertIn(required, skill)
                self.assertNotIn("Legacy fallback: MCP chunks", skill)
                helper = "aqteron-claude/skills/publish-aqteron-app/scripts/zip_info.py"
                extracted = pathlib.Path(directory) / "zip_info.py"
                extracted.write_bytes(files[helper])
                inspected = subprocess.run([sys.executable, str(extracted), str(output)], capture_output=True, text=True, check=False)
                self.assertEqual(inspected.returncode, 0, inspected.stderr)
                self.assertEqual(json.loads(inspected.stdout), {"filename": "release.zip", "size_bytes": output.stat().st_size, "sha256": package.EXPECTED_SHA256})

    def test_reintroduced_legacy_helper_is_rejected_by_packaging(self):
        with tempfile.TemporaryDirectory() as directory:
            copy = pathlib.Path(directory)
            shutil.copytree(ROOT / "plugins", copy / "plugins", ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
            (copy / "scripts").mkdir()
            shutil.copyfile(SCRIPT, copy / "scripts/package_plugin.py")
            (copy / "plugins/aqteron/skills/publish-aqteron-app/scripts/zip_chunks.py").write_text("legacy upload must not return\n")
            output = copy / "unexpected.zip"
            result = subprocess.run([sys.executable, str(copy / "scripts/package_plugin.py"), str(output)], capture_output=True, text=True, check=False)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
