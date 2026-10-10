#!/usr/bin/env python3
"""Build a reproducible Aqteron for Claude 0.1.7 plugin archive."""
import argparse
import hashlib
import pathlib
import zipfile

VERSION = "0.1.7"
EXPECTED_SHA256 = None  # Pinned to an exact checksum after release-candidate CI.
ROOT = pathlib.Path(__file__).resolve().parents[1] / "plugins" / "aqteron"
FILES = sorted([
    ".claude-plugin/icon.svg",
    ".claude-plugin/plugin.json",
    ".mcp.json",
    "README.md",
    "skills/publish-aqteron-app/SKILL.md",
    "skills/publish-aqteron-app/scripts/zip_chunks.py",
    "skills/publish-aqteron-app/scripts/zip_direct.py",
])

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=pathlib.Path)
    args = parser.parse_args()
    assert not args.output.exists(), "Refusing to overwrite an existing artifact"
    actual_files = sorted(str(p.relative_to(ROOT)) for p in ROOT.rglob("*")
                          if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc")
    assert actual_files == FILES, (actual_files, FILES)
    with zipfile.ZipFile(args.output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for relative in FILES:
            info = zipfile.ZipInfo("aqteron-claude/" + relative, (2026, 10, 10, 0, 0, 0))
            info.external_attr = 0o100644 << 16
            archive.writestr(info, (ROOT / relative).read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=6)
    actual = hashlib.sha256(args.output.read_bytes()).hexdigest()
    if EXPECTED_SHA256 is not None and actual != EXPECTED_SHA256:
        raise SystemExit("Archive SHA-256 mismatch: " + actual)
    with zipfile.ZipFile(args.output) as archive:
        assert archive.testzip() is None, "Archive CRC error"
        assert len(archive.namelist()) == len(FILES)
        manifest = archive.read("aqteron-claude/.claude-plugin/plugin.json").decode("utf-8")
        assert '"version": "' + VERSION + '"' in manifest
    print(actual + "  " + str(args.output))

if __name__ == "__main__":
    main()
