#!/usr/bin/env python3
"""Reproduce the reviewed 0.1.0 ZIP with Python's standard library."""
import argparse
import hashlib
import pathlib
import zipfile

EXPECTED = "e0d3d885398625268b800343f171cf2c5a31d08f4859f350f256d0d6abf940cf"
FILES = [".claude-plugin/plugin.json", ".mcp.json", "README.md", "skills/publish-aqteron-app/SKILL.md", "skills/publish-aqteron-app/scripts/zip_chunks.py"]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=pathlib.Path)
    args = parser.parse_args()
    source = pathlib.Path(__file__).resolve().parents[1] / "plugins" / "aqteron"
    assert not args.output.exists(), "Refusing to overwrite an existing artifact"
    assert sorted(str(p.relative_to(source)) for p in source.rglob("*") if p.is_file()) == FILES
    with zipfile.ZipFile(args.output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for relative in FILES:
            info = zipfile.ZipInfo("aqteron-claude/" + relative, (2026, 9, 27, 0, 0, 0))
            info.external_attr = 0o100644 << 16
            archive.writestr(info, (source / relative).read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=6)
    actual = hashlib.sha256(args.output.read_bytes()).hexdigest()
    if actual != EXPECTED:
        raise SystemExit("Archive hash changed: " + actual + ". Review the sources or compression runtime before publishing.")
    print(actual + "  " + str(args.output))

if __name__ == "__main__":
    main()
