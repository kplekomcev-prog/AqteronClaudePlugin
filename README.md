# Aqteron for Claude

Create, validate, publish and update applications in your own [Aqteron](https://aqteron.com) account from Claude. This repository contains the installable client plugin and Claude Code marketplace; Aqteron's MCP server is hosted remotely.

**Preview 0.1.6.** Server-side OAuth, ZIP transfer, publication/update checks and the Aqteron specialist workflow are supported. Retained application versions and exact source ZIPs can be retrieved before updating an existing app. The installable plugin package is now fully English for Anthropic Directory presentation.

## Install in Claude

1. Open the [installation guide](https://aqteron.com/cabinet/connections/claude?lang=en) and use the current plugin ZIP `aqteron-claude-0.1.6.zip`.
2. In Claude, open **Customize → Plugins → Add → Upload plugin**, and upload the ZIP.
3. In the plugin's **Connectors** tab, choose **Aqteron → Connect**. Sign in on Aqteron and authorize access to your own account.
4. Start a **new conversation** after updating the plugin and ask: **Show my apps in Aqteron.** For an existing app, you can then ask Claude to show its retained versions before editing.

[Russian installation guide](https://aqteron.com/cabinet/connections/claude?lang=ru) · [French installation guide](https://aqteron.com/cabinet/connections/claude?lang=fr)

Plugin availability depends on your Claude account and organization settings. Creating and transferring a ZIP requires code execution and file access. If plugin upload is unavailable, use a custom connector with `https://aqteron.com/mcp`, or use Claude Code.

## Install in Claude Code

```sh
claude plugin marketplace add kplekomcev-prog/AqteronClaudePlugin
claude plugin install aqteron@aqteron
```

Start Claude Code and use `/mcp` to connect Aqteron. Each user signs into their own account. No API key or shared credential is included in this repository.

## What it does

The workflow fetches current Aqteron instructions and the task-specific specialist plan before coding. When `specialistWorkflow.requiredBeforeCoding` is true, Claude calls `get_specialist_instructions` at planning, design, implementation and verification stages, executes applicable acceptance checks on the exact build, then generates a compatible app ZIP, uploads the actual file bytes, checks validation and publishes only when the user asks.

For existing apps, Claude first reads `list_app_versions`, reconstructs the exact retained source ZIP with `get_app_source_zip` and `get_app_source_chunk`, verifies size and SHA-256, then edits that source instead of rebuilding from memory. Before upload it rechecks the active version to protect against overwriting a newer update.

If a Claude session has a stale MCP tool catalog, the plugin stops at the affected workflow and asks for a refresh/reconnect or a new session instead of silently skipping required specialist or source-retrieval steps.

A completed upload alone does not publish the app. The current ZIP limit is 10 MiB; smaller apps are more practical for chunked transfer.

You can revoke access in [AI connections](https://aqteron.com/cabinet/connections/ai). Existing published apps remain available after disconnection.

## Data handling and support

The plugin declares one remote service: `https://aqteron.com/mcp`. It provides platform instructions and, after OAuth authorization, your app metadata, retained version/source metadata, ZIP uploads and publication results. The included Python helper reads a ZIP locally and emits chunks; it contains no network client. The plugin has no separate telemetry endpoint. Claude's own data processing is governed by your agreement with Anthropic.

For setup problems, see the installation guide. Report reproducible non-sensitive issues in this repository. Never post passwords, tokens, cookies, private app ZIPs or user data in public issues. Aqteron is operated by EIREEN Tech (France). Read the [privacy policy](https://aqteron.com/privacy). For support, privacy requests or non-public security reports, email [contact@aqteron.com](mailto:contact@aqteron.com).

## Release integrity

- Package: `aqteron-claude-0.1.6.zip`
- Size: **9,322 bytes; six files.**
- SHA-256: `80db2c2ae4442f84b6eb2f936dbc860c5b4057c4bdac4b063c2e12e83c8a0852`
- MCP endpoint: `https://aqteron.com/mcp`
- Plugin path: `plugins/aqteron`
- Marketplace name: `aqteron`

The plugin retains its original `UNLICENSED` designation. No additional open-source license is granted by this distribution.

[Support](https://aqteron.com/support) · [Terms of service](https://aqteron.com/terms)
