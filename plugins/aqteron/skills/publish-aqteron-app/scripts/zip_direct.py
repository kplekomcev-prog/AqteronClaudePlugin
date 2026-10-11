#!/usr/bin/env python3
"""Upload one local ZIP using an Aqteron transfer capability; never follow redirects."""
import argparse
import hashlib
import http.client
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
GUIDE = "https://aqteron.com/cabinet/?connect=1&provider=claude"

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

def upload(path, url, ticket):
    parsed = urllib.parse.urlsplit(url)
    match = re.fullmatch(r"/api/ai/zip-transfer/browser/([0-9a-f-]{36})/file", parsed.path, re.I)
    if (parsed.scheme != "https" or parsed.hostname != "aqteron.com" or parsed.port is not None
            or parsed.username or parsed.password or parsed.query or parsed.fragment or not match):
        raise ValueError("Upload URL must be the exact Aqteron HTTPS capability URL")
    transfer = str(uuid.UUID(match[1]))
    if not re.fullmatch(r"[A-Za-z0-9_-]{43}", ticket):
        raise ValueError("Use direct_upload.upload_ticket from begin_app_zip_upload")
    size = path.stat().st_size
    if not 0 < size <= MAX_BYTES or not zipfile.is_zipfile(path):
        raise ValueError("Input must be a ZIP containing 1..10485760 bytes")
    data = path.read_bytes()
    if len(data) != size:
        raise ValueError("ZIP changed during preparation")
    checksum = hashlib.sha256(data).hexdigest()
    request = urllib.request.Request(url, data=data, method="PUT", headers={
        "Content-Type": "application/zip", "X-Aqteron-Upload-Ticket": ticket,
        "Accept": "application/json", "User-Agent": "Aqteron-Claude-ZIP/0.1.8"})
    with urllib.request.build_opener(NoRedirect()).open(request, timeout=120) as response:
        result = json.loads(response.read(16384))
    if (result.get("transfer_id") != transfer or result.get("received_bytes") != size
            or result.get("sha256") != checksum or result.get("status") != "receiving"):
        raise ValueError("Server did not acknowledge the exact transfer, byte count and SHA-256")
    return {"transfer_id": transfer, "received_bytes": size, "sha256": checksum,
            "status": "received_pending_validation"}

def failure(code, **extra):
    # No raw exception, response body, capability URL or credential is logged.
    print(json.dumps({"status": "failed", "error": code, **extra}, separators=(",", ":")), file=sys.stderr)
    return 2

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("zip_path", type=pathlib.Path)
    parser.add_argument("--upload-url", required=True)
    parser.add_argument("--upload-ticket", required=True)
    args = parser.parse_args()
    try:
        result = upload(args.zip_path, args.upload_url, args.upload_ticket)
    except urllib.error.HTTPError as exc:
        try:
            body = exc.read(2048).decode("utf-8", "replace")
        except TimeoutError:
            return failure("network_timeout")
        except (OSError, ValueError, http.client.HTTPException):
            return failure("http_upload_failed", http_status=exc.code)
        try:
            parsed = json.loads(body)
        except ValueError:
            parsed = None
        if isinstance(parsed, dict):
            allowed = {"upload_ticket_invalid", "invalid_token", "insufficient_scope", "rate_limited",
                       "upload_already_completed", "upload_transfer_started", "upload_transfer_busy",
                       "upload_content_type_invalid", "upload_size_mismatch", "checksum_mismatch",
                       "upload_connection_lost", "invalid_origin", "operation_failed"}
            code = parsed.get("error")
            if not isinstance(code, str) or code not in allowed:
                code = "http_upload_failed"
            return failure(code, http_status=exc.code)
        if exc.code == 403 and any(x in body.lower() for x in ("host not allowed", "allowlist", "egress")):
            return failure("network_egress_blocked", setup_guide=GUIDE)
        return failure("http_upload_failed", http_status=exc.code)
    except urllib.error.URLError as exc:
        if isinstance(exc.reason, TimeoutError):
            return failure("network_timeout")
        reason = str(exc.reason).lower()
        blocked = "host not allowed" in reason or "allowlist" in reason or "tunnel connection failed: 403" in reason
        return failure("network_egress_blocked" if blocked else "network_transfer_failed", setup_guide=GUIDE)
    except TimeoutError:
        return failure("network_timeout")
    except (OSError, ValueError, TypeError, AttributeError, http.client.HTTPException):
        return failure("zip_or_receipt_invalid")
    print(json.dumps(result, separators=(",", ":")))
    return 0

if __name__ == "__main__":
    sys.exit(main())
