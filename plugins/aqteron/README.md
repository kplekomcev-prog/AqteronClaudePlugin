# Aqteron for Claude · 0.1.8

Aqteron lets Claude create, validate, publish and update applications in your Aqteron account. Claude reads the current platform instructions and capabilities through MCP, builds a ZIP package, validates it with Aqteron and publishes only when you ask.

Version 0.1.8 makes one direct binary PUT the default ZIP transfer and includes a clear setup guide and manual fallback when Claude blocks outbound file transfer. Source-safe updates and the existing publication scope are preserved.

## Install in Claude

1. Open **Customize → Plugins → Add → Upload plugin** and select `aqteron-claude-0.1.8.zip`.
2. Open the plugin's **Connectors** tab, choose **Aqteron**, and select **Connect**. The MCP server is `https://aqteron.com/mcp`.
3. Sign in to your Aqteron account and authorize access. Enter your password only on Aqteron.
4. Start a new Claude conversation after updating the plugin. A simple first request is: **Show my apps in Aqteron.**

Plugin upload availability depends on your Claude account and organization settings. If plugin upload is unavailable, you can add a custom connector using the same MCP endpoint. Creating and transferring ZIP files also requires code execution and file access in Claude.

## Enable automatic file transfer once

- Personal account: open Settings > Capabilities, enable Code execution and file creation and Allow network egress, add `aqteron.com` in Additional allowed domains, and save. Package-manager-only access without this domain is insufficient.
- Team/Enterprise: an organization owner enables these capabilities and adds `aqteron.com` under Organization settings > Capabilities. Each member connects their own Aqteron account.
- Start a new conversation after installation or a settings change. Ask Claude to create a small counter, upload its ZIP automatically and validate it without publishing.

These network settings belong to the account or organization. Installing the plugin does not change them for all users. The [step-by-step cabinet guide](https://aqteron.com/cabinet/?connect=1&provider=claude) includes installation, connector setup, file transfer and troubleshooting in seven languages.

## Claude Code

Install from the Aqteron marketplace:

```sh
claude plugin marketplace add kplekomcev-prog/AqteronClaudePlugin
claude plugin install aqteron@aqteron
```

Then use `/mcp` to connect Aqteron and complete OAuth sign-in.

## Specialist workflow

For application creation or code updates, Claude first reads `get_app_instructions` and follows the returned Aqteron specialist workflow.

When specialist preparation is required, Claude obtains task-specific instructions for:

1. planning
2. design
3. implementation
4. verification

Applicable acceptance checks must be run against the exact packaged build before transfer. Missing tests must be reported as not run rather than treated as passed.

## Update an existing application

For an existing Aqteron application, Claude should use retained source instead of rebuilding the application from memory.

The normal update flow is:

1. Call `list_apps` and identify the intended owned app and its current `active_version_id`.
2. Call `list_app_versions` and select the active version unless you explicitly requested another retained version.
3. Call `get_app_source_zip` for that version. It returns source metadata and the first ZIP chunk.
4. While `next_chunk_index` is not null, call `get_app_source_chunk` sequentially.
5. Decode and concatenate the chunks in order.
6. Verify the reconstructed ZIP byte size and SHA-256 against the server metadata.
7. Unpack the verified source ZIP, preserve unrelated behavior, assets, data compatibility and package identity, then implement only the requested changes.
8. Re-read the app immediately before upload. If the active version changed, stop and reconcile instead of overwriting a newer update.
9. Upload the new package in update mode with the freshly observed `expected_version_id`.

If the current Claude session does not expose `list_app_versions`, `get_app_source_zip` or `get_app_source_chunk`, treat its MCP tool catalog as stale. Refresh or reconnect Aqteron, or start a new Claude session. Do not reconstruct an existing application from memory when retained source is available.

## ZIP transfer and publication

The preferred transport is an OAuth-authorized `begin_app_zip_upload`, followed by one HTTPS PUT to the returned short-lived `direct_upload.url` using the returned `direct_upload.upload_ticket` and the included `zip_direct.py` helper. The random, short-lived ticket is distinct from the logical idempotency key and bound to the account’s active OAuth grant. The server checks its exact 10 MiB ceiling and SHA-256. Claude then calls `complete_app_zip_upload` to validate and `deploy_app` to publish only when instructed.

The binary PUT from code execution requires the Claude sandbox to allow HTTPS PUT to aqteron.com. The remote MCP connection does not grant sandbox network access.

On a blocked outbound request, Claude provides the cabinet setup guide and can return the short-lived `browser_upload.url` provided by Aqteron. Download the exact ZIP in Claude, open that link and select the ZIP. The browser uploads the whole file and validates it; Claude can then retrieve the result and publish only within your original request. This route requires manual file selection and does not establish an automatic Claude attachment bridge. Keep the private link in the requesting conversation; it expires after at most 15 minutes.

Legacy sequential MCP chunks remain supported for clients without an appropriate whole-file path. A 10 MiB ZIP needs 427 chunk calls, so this is not a practical default when the model must transcribe every chunk.

## Security and data handling

The plugin contains no Aqteron password, API key or shared account token.

The only remote MCP service declared by the plugin is:

`https://aqteron.com/mcp`

After OAuth authorization, Aqteron can provide the connected user's application metadata, retained version/source metadata, ZIP validation results and publication results. The bundled chunk helper reads local ZIP files and emits chunk data; the default direct helper sends the selected archive only to an exact Aqteron HTTPS upload ticket after the user has authorized the MCP transfer.

Published application links can be accessible to anyone who has the link. Do not include passwords, tokens or private source material in public application assets.

Access can be revoked from Aqteron's AI connections settings. Revoking the connector does not delete already published applications.

## Privacy, support and legal

Aqteron is operated by **EIREEN Tech**, SAS, 102 628 047 R.C.S. Paris, 122 rue Amelot, 75011 Paris, France.

- [Privacy policy](https://aqteron.com/privacy)
- [Terms of service](https://aqteron.com/terms)
- [Support](https://aqteron.com/support)
- Support and privacy contact: [contact@aqteron.com](mailto:contact@aqteron.com)
- [English installation guide](https://aqteron.com/cabinet/connections/claude?lang=en)
- [Russian installation guide](https://aqteron.com/cabinet/connections/claude?lang=ru)
- [French installation guide](https://aqteron.com/cabinet/connections/claude?lang=fr)

## Distribution

This package is distributed for installation through Claude and the Aqteron Claude Code marketplace. It retains its `UNLICENSED` designation; no additional open-source license is granted by this package.

