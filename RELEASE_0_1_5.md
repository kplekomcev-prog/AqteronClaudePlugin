# Aqteron for Claude 0.1.5

Released: 2026-10-05

## Purpose

Enable Claude to safely update existing Aqteron applications from the exact retained source package instead of reconstructing them from memory.

## Changes

- Add the existing-app update flow based on `list_app_versions`, `get_app_source_zip` and `get_app_source_chunk`.
- Reconstruct retained ZIPs from ordered standard-base64 chunks and verify exact byte size and SHA-256 before editing.
- Recheck the active application version immediately before upload to avoid overwriting a newer update.
- Stop existing-app updates when the Claude session exposes a stale MCP catalog without the new version/source tools.
- Preserve the mandatory Aqteron specialist workflow from 0.1.4.
- Preserve the existing OAuth endpoint and resumable ZIP upload workflow.

## Artifact

- File: `aqteron-claude-0.1.5.zip`
- Size: 10,599 bytes
- Files: 6
- SHA-256: `1dd04e21152e40138fd576ffc3ca7582dfd51ec532afdca1a01640e18c2f021b`

Validated archive root:

- `.claude-plugin/icon.svg`
- `.claude-plugin/plugin.json`
- `.mcp.json`
- `README.md`
- `skills/publish-aqteron-app/SKILL.md`
- `skills/publish-aqteron-app/scripts/zip_chunks.py`

MCP endpoint remains `https://aqteron.com/mcp`.
