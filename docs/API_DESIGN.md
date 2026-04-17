# API Design

Velocity Brain exposes REST APIs under `/v1` and keeps business logic in service modules.

## Endpoint Catalog

### Ingestion

- `POST /v1/ingest/text`
- `POST /v1/ingest/multimodal`

### Query + Context

- `POST /v1/query`
- `GET /v1/query/timeline-changes/{slug}?days=N`
- `GET /v1/entity/{slug}`
- `GET /v1/graph/entity/{slug}`

### Agent Runtime

- `POST /v1/agent/run`
- `POST /v1/agents/collaborate`
- `POST /v1/command`

### Decision Intelligence

- `POST /v1/predict`
- `POST /v1/simulate`
- `POST /v1/decide`

### Skills + Workflow + Sync

- `GET /v1/skills`
- `POST /v1/execute/workflow`
- `POST /v1/sync/push`
- `POST /v1/sync/pull`

### Operations

- `GET /v1/dashboard/summary`
- `GET /v1/healthz`

## Response Contract

Intelligence responses are expected to provide:

- `answer`
- `confidence`
- `references`
- `reasoning_summary`

If internal context is insufficient, endpoints should return an explicit insufficiency response rather than fabricating content.

## API Principles

- Thin routes, service-oriented implementation
- Brain-first retrieval for agentic tasks
- Explainability included by default
- Backward-compatible evolution of request/response schemas

## Local Docs URL

When running `velocitybrain serve`, OpenAPI docs are available at:
- `http://localhost:8080/docs`
