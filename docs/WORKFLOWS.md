# Workflows

This document summarizes core workflow patterns currently supported by Velocity Brain.

## 1) Ingestion Workflow

- Input: note, transcript, or textual signal
- Parse likely entities
- Upsert entity page (compiled truth)
- Append immutable timeline event
- Optionally trigger enrichment follow-up

## 2) Query Workflow

- Input: question (for example, "What do I know about X?")
- Perform hybrid retrieval from internal memory
- Rank and synthesize top results
- Return answer with confidence and references

## 3) Enrichment Workflow

- Identify thin or stale entities
- Gather additional evidence from approved sources/processes
- Update compiled truth snapshot
- Append timeline evidence and relationship updates

## 4) Execution Workflow

- Input: execution-oriented signal
- Classify intent as execution/planning/query/ingestion
- Build action plan
- Execute action adapters/workflows
- Log outcomes and write memory updates

## 5) Background Optimization Workflow

- Run scheduled maintenance cycles
- Perform deduplication and consistency checks
- Repair broken links/citations where applicable
- Generate and persist operational insights
- Record job health in optimization tracking

## Workflow Design Rules

- Internal memory retrieval precedes external reasoning.
- All significant actions should be auditable.
- Write paths should preserve timeline immutability.
- Long-running maintenance should be idempotent.
