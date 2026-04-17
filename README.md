# Velocity Brain

<p align="center">
  <img src="/guide/static/assets/velocity-brain-logo.svg" alt="Velocity Brain logo" width="760" />
</p>

<p align="center">
  CLI-native. API-capable. MCP-ready.
</p>

## What Is Velocity Brain

Velocity Brain is a local-first memory and execution runtime for agents. It stores memory in Postgres, retrieves internal context, and runs deterministic workflows.

Core value:
- Brain-first retrieval before action
- Persistent memory and timeline model
- Agent-loop runtime for planning and execution
- MCP tools for multiple MCP-compatible clients

## Install

From PyPI:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install velocitybrain
```

From local repo (dev mode):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -e .
```

## Quick Start (Local)

### 1) Configure environment

```powershell
Copy-Item .env.example .env
```

### 2) Start and initialize database

```powershell
docker compose up db -d
docker compose exec -T db psql -U velocity -d velocitybrain -f /docker-entrypoint-initdb.d/01-schema.sql
```

### 3) Validate setup

```powershell
velocitybrain init
velocitybrain doctor
```

### 4) Core workflows

```powershell
velocitybrain ingest --source note --content "Met Jane Doe from Acme and discussed GTM"
velocitybrain query "What do I know about Jane Doe?"
velocitybrain run "Prepare me for meeting with Jane Doe tomorrow"
```

## How Answers Work Today

`velocitybrain query` and `velocitybrain run` do not call Claude/OpenAI/Gemini APIs by default.

- `query`: keyword + hybrid retrieval from internal memory tables
- `run`: intent detection + deterministic plan + simulated execution + local writeback

When connected through MCP, external clients (Claude Code/Codex/etc.) call these tools, but Velocity Brain itself remains local-first.

## CLI Reference

```powershell
velocitybrain about
velocitybrain init --bootstrap-schema
velocitybrain doctor
velocitybrain ingest --source note --content "..."
velocitybrain ingest --source notes --org-file ./notes/daily.org
velocitybrain query "..."
velocitybrain run "..."
velocitybrain sync --repo .
velocitybrain sync --repo C:/repo-a --repo C:/repo-b --apply
velocitybrain identity
velocitybrain serve api --host 0.0.0.0 --port 8080 --reload
velocitybrain serve mcp
```

Output controls:

```powershell
velocitybrain --json query "What changed this week?"
velocitybrain --color about
velocitybrain --no-color about
```

## Plugin Setup (MCP)

Velocity Brain acts as an MCP server process. One server config works across clients.

Start MCP server manually:

```powershell
velocitybrain serve mcp
```

Generic MCP config:

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

If PATH lookup fails, use full executable path:

```json
{
  "mcpServers": {
    "velocitybrain": {
      "command": "C:/Path/To/Python/Scripts/velocitybrain.exe",
      "args": ["serve", "mcp"]
    }
  }
}
```

Client-specific examples:
- Claude Code CLI:

```powershell
claude mcp add velocitybrain -- velocitybrain serve mcp
```

- OpenAI Codex CLI:

```powershell
codex mcp add velocitybrain -- velocitybrain serve mcp
```

- Gemini CLI / Cline / Antigravity / any MCP-capable client:
Use the same `mcpServers` JSON config in that client's MCP settings.

Available MCP tools:
- `ingest_text`
- `query`
- `run_agent`
- `sync_brain` (policy-gated)
- `put_page` (policy-gated)
- `delete_page` (policy-gated)
- `google_workspace_action`
- `get_identity_spec`
- `list_skills`
- `healthz`

## API Usage

Start API:

```powershell
velocitybrain serve api --host 0.0.0.0 --port 8080 --reload
```

Main endpoints:
- Health: `GET /v1/healthz`
- Docs: `http://localhost:8080/docs`
- Guide app: `http://localhost:8080/guide`
- Org ingest: `POST /v1/ingest/org`
- Eval query: `POST /v1/eval/query`
- Identity spec: `GET /v1/identity/spec`
- Sync full: `POST /v1/sync/full`
- Access token: `POST /v1/access/token`
- Legacy plan: `POST /v1/legacy/plan`, `GET /v1/legacy/plan/{owner}`
- Docs pages list: `GET /v1/docs/pages`
- Docs page content: `GET /v1/docs/page/{slug}`

## Security and Reliability Improvements

- Runtime identity spec layer (`identity.spec.json`) above `AGENTS.md`
- Workspace-bounded file reads for ingestion by default
- Policy enforcement for destructive MCP tools
- Sync dry-run is non-mutating and supports multiple repositories
- Configurable embedding provider/model/dimension/router
- DB connect/lock/statement timeout controls
- Org-mode ingestion support and sync discovery
- Evaluation metrics endpoint (`precision@k`, `recall@k`, latency)
- Encrypted digital-legacy storage and token-based access primitives

Key env flags in `.env.example`:
- `EMBEDDING_PROVIDER`, `EMBEDDING_MODEL`, `MODEL_ROUTER`, `EMBED_DIM`
- `MCP_ALLOW_DESTRUCTIVE_TOOLS`
- `ALLOW_UNSAFE_FILE_READS`
- `WORKSPACE_ROOT`
- `IDENTITY_SPEC_PATH`

## Publish to PyPI

### 1) Prepare release metadata

```powershell
python -m pip install --upgrade build twine
```

- Bump `version` in `pyproject.toml` for each release.
- Keep project name as `velocitybrain`.

### 2) Build clean artifacts

```powershell
Remove-Item -Recurse -Force dist,build,*.egg-info -ErrorAction SilentlyContinue
python -m build
```

### 3) Validate artifacts

```powershell
python -m twine check dist/*
```

### 4) Upload to TestPyPI (recommended first)

```powershell
$env:TWINE_USERNAME="__token__"
python -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*
```

Validate in clean venv:

```powershell
python -m venv .venv-test
.\.venv-test\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple velocitybrain==0.1.0
velocitybrain about
```

### 5) Upload to PyPI

```powershell
$env:TWINE_USERNAME="__token__"
python -m twine upload --repository-url https://upload.pypi.org/legacy/ dist/*
```

### 6) Verify from PyPI

```powershell
python -m pip install --upgrade velocitybrain
velocitybrain about
```

Token safety notes:
- Never commit tokens.
- Do not persist tokens using `setx` on shared machines.
- If a token is exposed in chat/logs, revoke immediately and issue a new token.

## Testing

```powershell
python -m pytest -q
```

## Backward Compatibility

Legacy commands still work:
- `velocityx ...`
- `python velocityx.py ...`

## Documentation

- `docs/ARCHITECTURE.md`
- `docs/FOLDER_STRUCTURE.md`
- `docs/DB_SCHEMA.md`
- `docs/API_DESIGN.md`
- `docs/SKILL_SYSTEM.md`
- `docs/AGENT_LOOP.md`
- `docs/WORKFLOWS.md`

## Reference Links

- Claude Code MCP docs: https://docs.claude.com/en/docs/claude-code/mcp
- Gemini CLI MCP docs: https://google-gemini.github.io/gemini-cli/docs/tools/mcp-server.html
- OpenAI Codex MCP docs: https://developers.openai.com/codex/mcp
- Cline MCP docs: https://docs.cline.bot/mcp/mcp-overview

## License

MIT
