#!/usr/bin/env python3
"""Inspect a real ZIP or emit exactly one standard MCP chunk argument object."""
import argparse
import base64
import hashlib
import json
import pathlib
import sys
import uuid
import zipfile

CHUNK_BYTES = 24576
MAX_BYTES = 10 * 1024 * 1024


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("zip_path", type=pathlib.Path)
    parser.add_argument("--transfer-id", type=uuid.UUID)
    parser.add_argument("--chunk-index", type=int)
    args = parser.parse_args()
    size = args.zip_path.stat().st_size
    if not 0 < size <= MAX_BYTES:
        parser.error("ZIP must contain 1..10485760 bytes")
    if not zipfile.is_zipfile(args.zip_path):
        parser.error("input is not a ZIP archive")
    if (args.transfer_id is None) != (args.chunk_index is None):
        parser.error("--transfer-id and --chunk-index must be supplied together")
    if args.chunk_index is None:
        digest = hashlib.sha256()
        with args.zip_path.open("rb") as source:
            for block in iter(lambda: source.read(1024 * 1024), b""):
                digest.update(block)
        result = {"filename": args.zip_path.name, "size_bytes": size, "sha256": digest.hexdigest(),
                  "chunk_bytes": CHUNK_BYTES, "chunk_count": (size + CHUNK_BYTES - 1) // CHUNK_BYTES}
    else:
        if args.chunk_index < 0 or args.chunk_index * CHUNK_BYTES >= size:
            parser.error("chunk index is outside the file")
        with args.zip_path.open("rb") as source:
            source.seek(args.chunk_index * CHUNK_BYTES)
            data = source.read(CHUNK_BYTES)
        result = {"transfer_id": str(args.transfer_id), "chunk_index": args.chunk_index,
                  "data_base64": base64.b64encode(data).decode("ascii")}
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
