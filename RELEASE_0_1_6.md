# Aqteron for Claude 0.1.6

Released: 2026-10-05

## Purpose

Make the installable Claude plugin package fully English for Anthropic Directory presentation while preserving the existing Aqteron MCP workflow.

## Changes

- Convert the plugin README from Russian to English.
- Convert the plugin manifest description from Russian to English.
- Preserve the retained-source existing-app update flow from 0.1.5.
- Preserve the mandatory Aqteron specialist workflow.
- Preserve OAuth, MCP endpoint, resumable ZIP upload and publication behavior.
- Verify that all six files in the installable package contain no Cyrillic characters.

## Artifact

- File: `aqteron-claude-0.1.6.zip`
- Size: 9,322 bytes
- Files: 6
- SHA-256: `80db2c2ae4442f84b6eb2f936dbc860c5b4057c4bdac4b063c2e12e83c8a0852`

Validated archive root:

- `.claude-plugin/icon.svg`
- `.claude-plugin/plugin.json`
- `.mcp.json`
- `README.md`
- `skills/publish-aqteron-app/SKILL.md`
- `skills/publish-aqteron-app/scripts/zip_chunks.py`

MCP endpoint remains `https://aqteron.com/mcp`.
