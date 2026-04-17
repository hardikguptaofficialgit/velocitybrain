# Client Integrations Guide

This guide shows how to connect Velocity Brain to MCP-capable clients and how to verify the connection reliably.

## Integration Model

- Velocity Brain runs as an MCP server process.
- Your client CLI (Claude Code, Codex CLI, Gemini CLI, Cline) is the MCP client.
- The client launches `velocitybrain serve mcp` and calls tools like `query`, `ingest_text`, and `run_agent`.

## Prerequisites

1. Activate the project virtual environment.
2. Ensure DB is running if you want memory-backed query and run behavior.
3. Ensure `velocitybrain about` and `velocitybrain doctor` succeed.

## MCP Server Command

Preferred command:

```powershell
velocitybrain serve mcp
```

If `velocitybrain` is not on PATH, use the full executable path:

```powershell
C:/Path/To/venv/Scripts/velocitybrain.exe serve mcp
```

## Claude Code CLI

### Add server

```powershell
claude mcp add velocitybrain -- velocitybrain serve mcp
```

If path spaces cause parsing issues on Windows, add through a wrapper script that launches the same command.

### Verify

```powershell
claude mcp list
```

Expected: `velocitybrain` should be connected.

### Smoke prompts

- Use velocitybrain `healthz` and show raw result.
- Query velocitybrain for "What do I know about Jane Doe?"
- Run agent for "Prepare me for meeting with Jane Doe tomorrow"

## OpenAI Codex CLI

### Add server

```powershell
codex mcp add velocitybrain -- velocitybrain serve mcp
```

### Verify

Use Codex MCP listing command in your installed version, then run a tool call prompt against `query`.

## Gemini CLI

Use Gemini CLI MCP config and register the same server command:

```json
{
  "mcpServers": {
    "velocitybrain": {
      "command": "velocitybrain",
      "args": ["serve", "mcp"]
    }
  }
}
```

## Cline

Add Velocity Brain in Cline MCP settings with the same stdio command.

## Plugin Notes

Velocity Brain itself already acts as the MCP plugin/tool provider. In client UIs, it appears under MCP/Plugins/Tools depending on the client terminology.

## Available MCP Tools

- `ingest_text`
- `query`
- `run_agent`
- `sync_brain` (policy gated)
- `put_page` (policy gated)
- `delete_page` (policy gated)
- `google_workspace_action`
- `get_identity_spec`
- `list_skills`
- `healthz`

## Troubleshooting

### Failed to connect

- Confirm command works directly in terminal.
- Confirm the client uses the same executable and venv.
- Reinstall editable package if repo path changed:

```powershell
python -m pip install -e .
```

### Query says DB unavailable

- Start Postgres:

```powershell
docker compose up db -d
```

- Load schema:

```powershell
docker compose exec -T db psql -U velocity -d velocitybrain -f /docker-entrypoint-initdb.d/01-schema.sql
```

- Recheck:

```powershell
velocitybrain doctor
```

### Destructive tool blocked

This is expected by default. Enable policy only when needed using runtime approval and env policy settings.

## Recommended Validation Flow

1. `velocitybrain doctor`
2. `velocitybrain ingest --source note --content "Met Jane Doe from Acme"`
3. `velocitybrain query "What do I know about Jane Doe?"`
4. Client MCP `healthz` call
5. Client MCP `query` call
