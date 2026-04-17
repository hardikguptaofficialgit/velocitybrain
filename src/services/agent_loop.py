from datetime import datetime, timezone
import uuid
from psycopg.types.json import Json
from src.core.db import get_conn
from src.services.memory_engine import MemoryEngine
from src.services.retrieval_engine import RetrievalEngine
from src.services.execution_engine import ExecutionEngine


class AgentLoop:
    def __init__(self):
        self.memory = MemoryEngine()
        self.retrieval = RetrievalEngine()
        self.execution = ExecutionEngine()

    def _detect_intent(self, signal: str) -> str:
        s = signal.lower()
        if any(k in s for k in ['prepare', 'meeting', 'brief']):
            return 'planning'
        if any(k in s for k in ['execute', 'send', 'schedule']):
            return 'execution'
        if any(k in s for k in ['what do i know', 'summarize', 'patterns']):
            return 'query'
        return 'ingestion'

    def _plan(self, intent: str, signal: str, context: list[dict]) -> list[dict]:
        if intent == 'execution':
            return [
                {'step': 'review_context', 'action_type': 'analyze', 'payload': {'context_hits': len(context)}},
                {'step': 'execute_workflow', 'action_type': 'workflow.run', 'payload': {'signal': signal}},
            ]
        if intent == 'planning':
            return [
                {'step': 'collect_briefing_context', 'action_type': 'query.aggregate', 'payload': {'signal': signal}},
                {'step': 'create_briefing', 'action_type': 'briefing.generate', 'payload': {'signal': signal}},
            ]
        return [
            {'step': 'memory_writeback', 'action_type': 'memory.update', 'payload': {'signal': signal}}
        ]

    def _attention_score(self, signal: str, context_hits: int) -> float:
        s = signal.lower()
        urgency_tokens = ['urgent', 'asap', 'today', 'deadline', 'risk']
        urgency = 0.15 if any(t in s for t in urgency_tokens) else 0.0
        base = 0.45 + min(0.35, context_hits * 0.04)
        return round(min(0.95, base + urgency), 3)

    def _persist_run(self, run: dict) -> None:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO agent_runs (run_id, signal, intent, plan, execution_log, status, confidence, created_at, completed_at)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,NOW(),NOW())
                    RETURNING id
                    """,
                    (
                        run['run_id'],
                        run['signal'],
                        run['intent'],
                        Json(run['plan']),
                        Json(run['actions']),
                        run['status'],
                        run['confidence'],
                    ),
                )
                run_pk = cur.fetchone()['id']
                for action in run['actions']:
                    cur.execute(
                        """
                        INSERT INTO execution_actions (run_id, action_type, action_payload, status, result)
                        VALUES (%s,%s,%s,%s,%s)
                        """,
                        (
                            run_pk,
                            action.get('action_type', 'unknown'),
                            Json(action.get('payload', {})),
                            action.get('status', 'unknown'),
                            Json(action),
                        ),
                    )
                conn.commit()

    def run(self, signal: str) -> dict:
        run_id = str(uuid.uuid4())
        trace_id = str(uuid.uuid4())
        intent = self._detect_intent(signal)
        context = self.retrieval.hybrid_search(signal, limit=8)
        plan = self._plan(intent, signal, context)
        actions = self.execution.execute(plan)

        memory_updates = []
        if intent in {'ingestion', 'planning', 'query'}:
            memory_updates.append(self.memory.upsert_from_text('agent-loop', signal))

        attention = self._attention_score(signal, len(context))
        confidence = max(0.4, round((0.6 if context else 0.45) + attention * 0.35, 3))
        reasoning = f'Intent={intent}. Queried internal brain first ({len(context)} hits) before action.'
        output = {
            'run_id': run_id,
            'signal': signal,
            'status': 'completed',
            'intent': intent,
            'plan': plan,
            'actions': actions,
            'memory_updates': memory_updates,
            'confidence': confidence,
            'attention_score': attention,
            'reasoning_summary': reasoning,
            'references': [{'type': 'entity', 'slug': x['slug']} for x in context],
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'trace_id': trace_id,
        }
        self._persist_run(output)
        return output
