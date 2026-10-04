# Aqteron for Claude 0.1.4

Released: 2026-10-04

## Purpose

Align the Claude plugin with Aqteron's production specialist workflow.

## Changes

- Require `get_app_instructions` before application creation or modification.
- When the returned workflow requires specialists, fetch `get_specialist_instructions` for planning, design, implementation and verification.
- Read the selected specialist prompts, deliverables and acceptance checks.
- Require evidence for applicable checks on the exact packaged build.
- Add a stale MCP schema guard: try the `specialist_request` fallback; if both routes are unavailable, stop generation instead of silently skipping specialists.
- Preserve the existing OAuth endpoint and resumable ZIP chunk-transfer workflow.

## Artifact

- File: `aqteron-claude-0.1.4.zip`
- Size: 9,666 bytes
- Files: 6
- SHA-256: `09c50484b85c530a85514454a2bbf87d2fc7a87f534fbbbf342b9fb9925f38b5`

Validated archive root:

- `.claude-plugin/icon.svg`
- `.claude-plugin/plugin.json`
- `.mcp.json`
- `README.md`
- `skills/publish-aqteron-app/SKILL.md`
- `skills/publish-aqteron-app/scripts/zip_chunks.py`

The bundled `zip_chunks.py` successfully inspected the exact release artifact and independently reported the same size and SHA-256.
