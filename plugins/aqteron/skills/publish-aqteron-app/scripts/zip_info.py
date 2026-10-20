#!/usr/bin/env python3
"""Inspect one local ZIP and report only its filename, byte count and SHA-256."""
import argparse
import hashlib
import json
import os
import pathlib
import sys
import zipfile

MAX_BYTES = 10 * 1024 * 1024


def inspect_zip(path):
    path = pathlib.Path(path)
    with path.open("rb") as source:
        before = os.fstat(source.fileno())
        if not 0 < before.st_size <= MAX_BYTES:
            raise ValueError("ZIP must contain 1..10485760 bytes")
        if not zipfile.is_zipfile(source):
            raise ValueError("input is not a ZIP archive")
        source.seek(0)
        digest = hashlib.sha256()
        count = 0
        for block in iter(lambda: source.read(1024 * 1024), b""):
            count += len(block)
            if count > MAX_BYTES:
                raise ValueError("ZIP changed during inspection")
            digest.update(block)
        after = os.fstat(source.fileno())
        if (count != before.st_size or after.st_size != before.st_size
                or after.st_mtime_ns != before.st_mtime_ns):
            raise ValueError("ZIP changed during inspection")
    return {"filename": path.name, "size_bytes": count, "sha256": digest.hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("zip_path", type=pathlib.Path)
    args = parser.parse_args()
    try:
        result = inspect_zip(args.zip_path)
    except (OSError, ValueError):
        # Do not print archive bytes, absolute paths or a raw exception.
        print("Input must be an unchanged ZIP containing 1..10485760 bytes", file=sys.stderr)
        return 2
    print(json.dumps(result, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
