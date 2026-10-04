# Aqteron for Claude

Create, validate, publish and update applications in your own [Aqteron](https://aqteron.com) account from Claude. This repository contains only the client plugin and a Claude Code marketplace. Aqteron's server is hosted remotely.

**Preview 0.1.4.** Server-side OAuth, ZIP transfer, publication/update checks and the Aqteron specialist workflow are supported. For application creation or modification, Claude must obtain specialist instructions for planning, design, implementation and verification before packaging or publishing. This is not an Anthropic directory listing or endorsement.

## Install in Claude

1. Open the [installation guide](https://aqteron.com/cabinet/connections/claude?lang=en) and use the current plugin ZIP `aqteron-claude-0.1.4.zip`.
2. In Claude, open **Customize → Plugins → Add → Upload plugin**, and upload the ZIP.
3. In the plugin's **Connectors** tab, choose **Aqteron → Connect**. Sign in on Aqteron and authorize access to your own account.
4. Start a **new conversation** after updating the plugin and ask: **Show my apps in Aqteron.**

[Русская инструкция](https://aqteron.com/cabinet/connections/claude?lang=ru) · [Guide français](https://aqteron.com/cabinet/connections/claude?lang=fr)

Plugin availability depends on your Claude account and organization settings. Creating and transferring a ZIP requires code execution and file access. If plugin upload is unavailable, use a custom connector with `https://aqteron.com/mcp`, or use Claude Code.

## Install in Claude Code

```sh
claude plugin marketplace add kplekomcev-prog/AqteronClaudePlugin
claude plugin install aqteron@aqteron
```

Start Claude Code and use `/mcp` to connect Aqteron. Each user signs into their own account. No API key or shared credential is included in this repository.

## What it does

The workflow fetches current Aqteron instructions and the task-specific specialist plan before coding. When `specialistWorkflow.requiredBeforeCoding` is true, Claude calls `get_specialist_instructions` at planning, design, implementation and verification stages, executes applicable acceptance checks on the exact build, then generates a compatible app ZIP, uploads the actual file bytes, checks validation and publishes only when the user asks.

If a Claude session has a stale MCP tool catalog without `get_specialist_instructions`, the skill tries the documented `specialist_request` fallback. If that schema is stale too, the plugin blocks generation until the connector/session is refreshed instead of silently skipping specialist preparation.

Updates target an app owned by the signed-in user. A completed upload alone does not publish the app. The current ZIP limit is 10 MiB; smaller apps are more practical for chunked transfer.

You can revoke access in [AI connections](https://aqteron.com/cabinet/connections/ai). Existing published apps remain available after disconnection. Published app links are accessible to anyone who has the link; do not embed private credentials or personal source material in public app files.

## Data handling and support

The plugin declares one remote service: `https://aqteron.com/mcp`. It provides platform instructions and, after OAuth authorization, your app metadata, ZIP uploads and publication results. The included Python helper reads a ZIP locally and emits chunks; it contains no network client. The plugin has no separate telemetry endpoint. Claude's own data processing is governed by your agreement with Anthropic.

For setup problems, see the installation guide. Report reproducible non-sensitive issues in this repository. Never post passwords, tokens, cookies, private app ZIPs or user data in public issues. Aqteron is operated by EIREEN Tech (France). Read the [privacy policy](https://aqteron.com/privacy), also available in [Russian](https://aqteron.com/privacy?lang=ru) and [French](https://aqteron.com/privacy?lang=fr). For support, privacy requests or non-public security reports, email [contact@aqteron.com](mailto:contact@aqteron.com).

## Release integrity

- Package: `aqteron-claude-0.1.4.zip`
- Size: **9,666 bytes; six files.**
- SHA-256: `09c50484b85c530a85514454a2bbf87d2fc7a87f534fbbbf342b9fb9925f38b5`
- MCP endpoint: `https://aqteron.com/mcp`
- Plugin path for directory submission: `plugins/aqteron`.
- Marketplace name: `aqteron`.

The plugin retains its original `UNLICENSED` designation. No additional open-source license is granted by this distribution.

[Support](https://aqteron.com/support) · [Terms of service](https://aqteron.com/terms)
