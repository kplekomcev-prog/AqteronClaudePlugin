#!/usr/bin/env python3
"""Send a verified local Aqteron ZIP to a one-hour upload ticket over HTTPS."""
import argparse
import hashlib
import json
import pathlib
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid
import zipfile

MAX_BYTES = 10 * 1024 * 1024


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("zip_path", type=pathlib.Path)
    parser.add_argument("--upload-url", required=True)
    parser.add_argument("--upload-key", required=True, help="The same idempotency key supplied to begin_app_zip_upload")
    args = parser.parse_args()
    parsed = urllib.parse.urlsplit(args.upload_url)
    if (parsed.scheme != "https" or parsed.hostname != "aqteron.com" or parsed.port is not None or
            parsed.username or parsed.password or parsed.query or parsed.fragment or
            not re.fullmatch(r"/api/ai/zip-transfer/[0-9a-fA-F-]{36}", parsed.path)):
        parser.error("Upload URL must be an exact Aqteron HTTPS ticket URL")
    try:
        uuid.UUID(parsed.path.rsplit("/", 1)[1])
    except ValueError:
        parser.error("Invalid upload transfer UUID")
    if not re.fullmatch(r"[A-Za-z0-9_-]{8,128}", args.upload_key):
        parser.error("Invalid upload key")
    size = args.zip_path.stat().st_size
    if not 0 < size <= MAX_BYTES or not zipfile.is_zipfile(args.zip_path):
        parser.error("Input must be a valid ZIP containing 1..10485760 bytes")
    data = args.zip_path.read_bytes()
    checksum = hashlib.sha256(data).hexdigest()
    req = urllib.request.Request(args.upload_url, data=data, method="PUT", headers={
        "Content-Type": "application/zip", "X-Aqteron-Upload-Key": args.upload_key,
        "Accept": "application/json", "User-Agent": "Aqteron-Claude-ZIP/0.1.7"})
    try:
        with urllib.request.urlopen(req, timeout=120) as response:
            result = json.loads(response.read(16384))
    except urllib.error.HTTPError as exc:
        body = exc.read(2048).decode("utf-8", "replace")
        if exc.code == 403 and ("host not allowed" in body.lower() or "allowlist" in body.lower()):
            print("Claude sandbox blocked outbound PUT. Allow aqteron.com with PUT in the environment's egress policy.", file=sys.stderr)
        else:
            try:
                code = json.loads(body).get("error", "http_upload_failed")
            except ValueError:
                code = "http_upload_failed"
            print("Aqteron ZIP upload failed: HTTP %d (%s)" % (exc.code, code), file=sys.stderr)
        sys.exit(2)
    except (urllib.error.URLError, TimeoutError):
        print("ZIP network transfer failed; verify cloud egress allows HTTPS PUT to aqteron.com.", file=sys.stderr)
        sys.exit(2)
    if (result.get("received_bytes") != size or result.get("sha256") != checksum or result.get("status") != "receiving"):
        print("Aqteron did not acknowledge the exact expected ZIP bytes", file=sys.stderr)
        sys.exit(3)
    print(json.dumps({"transfer_id": result["transfer_id"], "received_bytes": size,
                      "sha256": checksum, "status": "received_pending_validation"}, separators=(",", ":")))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError) as exc:
        print("ZIP upload client error: " + str(exc), file=sys.stderr)
        sys.exit(1)
