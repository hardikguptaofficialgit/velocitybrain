<p align="center">
  <img src="https://raw.githubusercontent.com/hardikguptaofficialgit/velocitybrain/2555e6ca7880bf9e1ab291d2253ac3b23b115e82/docs/assets/velocity-brain-logo.svg" alt="Velocity Brain logo" width="600" />
</p>

<p align="center">
  CLI-native. API-capable. MCP-ready.
</p>

## Velocity Brain

Your AI agent is capable but incomplete. Velocity Brain gives it a real brain.

Velocity Brain is a local-first memory and execution runtime for agents. It stores memory in Postgres, retrieves internal context before action, and runs deterministic workflows through CLI, API, and MCP interfaces.

Core value:
- Brain-first retrieval before action
- Persistent memory and timeline model
- JSON skillpack for planning, execution, enrichment, and maintenance
- MCP tools for compatible clients
- Policy gates and auditability for destructive actions

## What Velocity Brain Does

Velocity Brain detects signals, performs brain-first lookup, ingests content, enriches entities, manages tasks, schedules cron jobs, generates reports, and supports connector-backed automations.

It ensures:

* Memory is accessed before action
* Information is structured and retrievable
* Citations and compiled truth stay consistent
* Tasks and automations run reliably
* MCP clients can call the same runtime tools

## Core System Capabilities

**Signal Detection & Thought Capture**
A lightweight intent layer routes requests into ingestion, query, planning, execution, or maintenance flows. The agent loop preserves the original signal, captures entities, and writes back useful memory.

**Brain-First Lookup Protocol**
All main workflows begin with internal retrieval. The runtime prefers existing knowledge before synthesis or execution, which keeps results consistent with prior memory.

**Content & Media Ingestion**
The shipped CLI supports inline text, files, and Org-mode ingestion. The skill library also includes manifests for article, PDF, video, audio, and OCR-style workflows.

**Entity Enrichment**
Entities are stored as structured pages with timeline evidence, compiled truth, and relationship data.

**Task & Cron Management**
The runtime includes deterministic job execution, background scheduler hooks, and job queue storage for repeatable operational workflows.

**Connector-Backed Automations**
Execution adapters cover email, calendar, messaging, and Google Workspace style actions. Destructive operations stay policy-gated.

## Intelligence & Routing Layer

**RESOLVER-style Skill Dispatch**
Requests are matched to the right skill or workflow from the JSON skill registry. The router and agent loop use intent, keywords, and internal retrieval to decide what happens next.

The current categories are:

* Always-on
* Brain operations
* Ingestion
* Thinking
* Operational

## Identity & System Configuration

**Identity Spec Layer**
`identity.spec.json` sits above the runtime defaults and describes the agent identity and policy posture.

**Identity Outputs**
The project supports identity and policy-oriented outputs through the existing identity spec service and access-control services.

## Access Control

Out-of-the-box access control includes:

* Full
* Work
* Family
* None

Destructive MCP tools are policy-gated, and the runtime also supports signed access tokens and encrypted legacy-plan storage.

## Operational Standards

Velocity Brain applies a shared set of operational rules:

* Brain-first lookup discipline
* Citation and confidence requirements in query output
* Deterministic action execution
* Test-before-bulk safeguards for sync and mutation flows
* Audit logging for high-risk events

## Skill System

Velocity Brain includes **65** JSON-defined skills, each with:

* Metadata fields for name, version, category, and triggers
* Defined workflow steps
* Validation rules
* Standardized output structure

All skills are:

* Loaded from `skills/**/*.json`
* Available through the `skills` CLI and MCP toolset
* Extensible without changing the router for every new capability

## Conformance & Architecture

* Skills follow a unified manifest shape
* Legacy behavior is being consolidated into reusable skills
* Ingestion, query, execution, and maintenance remain separated by workflow
* The runtime is built to stay deterministic and auditable

## Setup & Runtime

* Fully working brain in about 30 minutes on a local machine
* Database initialization is automated through the provided schema bootstrap
* Minimal configuration is required beyond Postgres and environment variables
* The system becomes operational immediately after setup checks pass

## Outcome

Velocity Brain turns an AI agent into a continuously improving system that:

* Thinks before responding
* Remembers context
* Organizes knowledge automatically
* Executes tasks reliably
* Improves over time without supervision

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
velocitybrain openclaw
velocitybrain status
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

- OpenClaw / Gemini CLI / Cline / Antigravity / any MCP-capable client:
Use the same `mcpServers` JSON config in that client's MCP settings.

Turnkey setup assets are available in:

- `integrations/mcp/claude-code/mcpServers.velocitybrain.json`
- `integrations/mcp/openclaw/mcpServers.velocitybrain.json`
- `scripts/setup_mcp_plugin.ps1`

One-command plugin setup:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/setup_mcp_plugin.ps1 -Client claude
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/setup_mcp_plugin.ps1 -Client openclaw
```

If `velocitybrain` is not on PATH, resolve to absolute executable path:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/setup_mcp_plugin.ps1 -Client claude -UseAbsoluteCommandPath
```

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
- Docs pages list: `GET /v1/docs/pages`
- Docs page content: `GET /v1/docs/page/{slug}`
- Retrieval eval: `POST /v1/eval/query`
- Audit viewer: `GET /v1/audit/recent`
- OpenClaw profile: `GET /v1/openclaw/profile`
- OpenClaw capabilities: `GET /v1/openclaw/capabilities`
- Runtime status: `GET /v1/runtime/status`

OpenClaw profile export command:

```powershell
velocitybrain openclaw
```

Unified runtime status command:

```powershell
velocitybrain status
```

## Guide App

The built-in guide at `http://localhost:8080/guide` now includes:

- Live API status (`/v1/healthz`)
- Docs page count (`/v1/docs/pages`)
- OpenClaw capability summary (`/v1/openclaw/capabilities`)
- Recent audit snapshot (`/v1/audit/recent`)

The guide uses a flat, brand-aligned color language (solid panels with orange accent), with no glow or gradient-heavy treatment.

## Retrieval Quality

Velocity Brain now includes a retrieval evaluation harness for measuring precision@k, recall@k, groundedness, and hallucination risk.

- API endpoint: `POST /v1/eval/query`
- Benchmark dataset: `data/retrieval_benchmark.json`
- Benchmark runner: `scripts/retrieval_benchmark.py`

## Security and Reliability Improvements

- Runtime identity spec layer (`identity.spec.json`) above `AGENTS.md`
- Workspace-bounded file reads for ingestion by default
- Policy enforcement for destructive MCP tools
- Audit trail for destructive MCP approvals and denials
- FastAPI lifespan startup handler (no deprecation warning)
- Sync dry-run is non-mutating and supports multiple repositories
- Configurable embedding provider/model/dimension/router
- DB connect/lock/statement timeout controls
- Org-mode ingestion support and sync discovery
- Evaluation metrics endpoint (`precision@k`, `recall@k`, latency)
- Encrypted legacy-plan storage and token-based access primitives

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
python -m pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple velocitybrain==0.10.0
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
- `docs/CLIENT_INTEGRATIONS.md`
- `docs/NEXT_LEVEL.md`

## Reference Links

- Claude Code MCP docs: https://docs.claude.com/en/docs/claude-code/mcp
- Gemini CLI MCP docs: https://google-gemini.github.io/gemini-cli/docs/tools/mcp-server.html
- OpenAI Codex MCP docs: https://developers.openai.com/codex/mcp
- Cline MCP docs: https://docs.cline.bot/mcp/mcp-overview

## License

MIT
