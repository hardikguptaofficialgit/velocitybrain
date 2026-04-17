# MCP Plugin Templates

This folder contains ready-to-use Velocity Brain MCP plugin templates for clients.

## Files

- `claude-code/mcpServers.velocitybrain.json`
- `openclaw/mcpServers.velocitybrain.json`

## One-command setup

Use the setup script to register plugins automatically.

### Claude Code

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/setup_mcp_plugin.ps1 -Client claude
```

### OpenClaw

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/setup_mcp_plugin.ps1 -Client openclaw
```

If your client cannot resolve `velocitybrain` on PATH, use absolute command resolution:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/setup_mcp_plugin.ps1 -Client claude -UseAbsoluteCommandPath
```

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/setup_mcp_plugin.ps1 -Client openclaw -UseAbsoluteCommandPath
```

## Verify both integrations

Run one command to verify:

- MCP server handshake and `healthz` tool call
- Claude registration (`claude mcp list`) when Claude CLI is installed
- OpenClaw config entry for `velocitybrain`

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify_mcp_integrations.ps1
```

If your OpenClaw config path is custom:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify_mcp_integrations.ps1 -OpenClawConfigPath "C:/path/to/openclaw/mcp.json"
```
