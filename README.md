# Aqteron for Claude · 0.1.8

Create, validate, publish and update applications in your own [Aqteron](https://aqteron.com) account from Claude. This repository contains the client plugin and Claude Code marketplace. The remote service is `https://aqteron.com/mcp`.

## Install and connect

1. Open the [cabinet setup guide](https://aqteron.com/cabinet/?connect=1&provider=claude), choose Claude and download `aqteron-claude-0.1.8.zip`.
2. In Claude, open Customize → Plugins → Add → Upload plugin. Select the ZIP.
3. In the plugin’s Connectors tab, choose Aqteron → Connect, sign into your own Aqteron account and authorize access.
4. In Settings → Capabilities, enable code execution/file creation and network egress, and add `aqteron.com` to allowed domains. Team/Enterprise owners set this in Organization settings → Capabilities.
5. Open a new conversation and ask Claude to show your Aqteron apps. The cabinet has complete instructions for plugin discovery, custom connectors, automatic ZIP uploads and troubleshooting in seven languages.

Plugin availability depends on your Claude account and organization settings. The directory listing is not required: the Aqteron-hosted ZIP and Claude Code marketplace remain available.

## Claude Code

```sh
claude plugin marketplace add kplekomcev-prog/AqteronClaudePlugin
claude plugin install aqteron@aqteron
```

Use `/mcp` to sign into Aqteron. Each person uses their own account; no shared credentials are packaged.

## File transfer

Claude obtains an account-bound short-lived capability through MCP, sends the real ZIP bytes with one HTTPS PUT and calls complete to validate. The maximum ZIP size is 10 MiB. Publication happens only within the user’s requested scope. A real Claude 10 MiB direct transfer and validation were verified on 2026-10-11; this release also checks receipts and refuses redirects in its helper.

When Claude blocks sandbox egress, the plugin provides the cabinet network instructions and a temporary Aqteron browser upload link. That fallback requires the user to download and select the ZIP; it is not automatic. It never silently replaces a large file upload with hundreds of model-mediated Base64 calls.

For updates, the workflow retrieves the retained source ZIP, verifies its size and SHA-256, preserves unrelated features and rechecks the current active version before uploading. See the [plugin README](plugins/aqteron/README.md) for the specialist workflow and data handling.

## Support and distribution

[Support](https://aqteron.com/support) · [Privacy](https://aqteron.com/privacy) · [Terms](https://aqteron.com/terms) · [contact@aqteron.com](mailto:contact@aqteron.com)

Aqteron is operated by EIREEN Tech (France). Do not include credentials, private application ZIPs or user data in public issues. This distribution remains UNLICENSED; no additional open-source license is granted.
