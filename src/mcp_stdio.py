import json
import sys
import traceback
import uuid
from typing import Any

from src.plugins.core_connectors import CoreConnectors
from src.services.agent_loop import AgentLoop
from src.services.identity_spec import IdentitySpecService
from src.services.memory_engine import MemoryEngine
from src.services.policy_engine import PolicyEngine
from src.services.retrieval_engine import RetrievalEngine
from src.services.response_style import ALLOWED_RESPONSE_STYLES, apply_response_style
from src.services.skill_registry import SkillRegistry
from src.services.sync_service import SyncService


class VelocityBrainMCPServer:
    def __init__(self):
        self.memory = MemoryEngine()
        self.retrieval = RetrievalEngine()
        self.agent = AgentLoop()
        self.skills = SkillRegistry('skills')
        self.policy = PolicyEngine()
        self.sync = SyncService()
        self.identity = IdentitySpecService()
        self.connectors = CoreConnectors()

    def _read_message(self) -> dict[str, Any] | None:
        header = sys.stdin.buffer.readline()
        if not header:
            return None

        if header.startswith(b'Content-Length:'):
            content_length = int(header.split(b':', 1)[1].strip())
            while True:
                line = sys.stdin.buffer.readline()
                if not line:
                    return None
                if line in (b'\r\n', b'\n'):
                    break
            payload = sys.stdin.buffer.read(content_length)
            if not payload:
                return None
            return json.loads(payload.decode('utf-8'))

        line = header.decode('utf-8').strip()
        if not line:
            return None
        return json.loads(line)

    def _write_message(self, payload: dict[str, Any]) -> None:
        print(json.dumps(payload), flush=True)

    def _ok(self, req_id: Any, result: Any) -> dict[str, Any]:
        return {'jsonrpc': '2.0', 'id': req_id, 'result': result}

    def _err(self, req_id: Any, code: int, message: str) -> dict[str, Any]:
        return {'jsonrpc': '2.0', 'id': req_id, 'error': {'code': code, 'message': message}}

    def _trace_result(self, name: str, result: Any) -> Any:
        if isinstance(result, dict):
            traced = dict(result)
            traced.setdefault('trace_id', f'{name}-{uuid.uuid4()}')
            traced.setdefault('tool', name)
            return traced
        return {'result': result, 'trace_id': f'{name}-{uuid.uuid4()}', 'tool': name}

    def _tool_list(self) -> dict[str, Any]:
        return {
            'tools': [
                {
                    'name': 'ingest_text',
                    'description': 'Store text into Velocity Brain memory.',
                    'inputSchema': {
                        'type': 'object',
                        'properties': {
                            'source': {'type': 'string'},
                            'content': {'type': 'string'},
                            'access_level': {'type': 'string'},
                        },
                        'required': ['source', 'content'],
                    },
                },
                {
                    'name': 'query',
                    'description': 'Hybrid query against Velocity Brain memory.',
                    'inputSchema': {
                        'type': 'object',
                        'properties': {
                            'question': {'type': 'string'},
                            'limit': {'type': 'integer'},
                            'response_style': {'type': 'string', 'enum': sorted(ALLOWED_RESPONSE_STYLES)},
                        },
                        'required': ['question'],
                    },
                },
                {
                    'name': 'run_agent',
                    'description': 'Run the detect->retrieve->reason->execute loop.',
                    'inputSchema': {
                        'type': 'object',
                        'properties': {
                            'signal': {'type': 'string'},
                            'response_style': {'type': 'string', 'enum': sorted(ALLOWED_RESPONSE_STYLES)},
                        },
                        'required': ['signal'],
                    },
                },
                {
                    'name': 'sync_brain',
                    'description': 'Sync one or more repositories (destructive-policy gated).',
                    'inputSchema': {
                        'type': 'object',
                        'properties': {
                            'repos': {'type': 'array', 'items': {'type': 'string'}},
                            'dry_run': {'type': 'boolean'},
                            'approve': {'type': 'boolean'},
                        },
                    },
                },
                {
                    'name': 'put_page',
                    'description': 'Reserved mutating operation (policy-gated).',
                    'inputSchema': {'type': 'object', 'properties': {'approve': {'type': 'boolean'}}},
                },
                {
                    'name': 'delete_page',
                    'description': 'Reserved destructive operation (policy-gated).',
                    'inputSchema': {'type': 'object', 'properties': {'approve': {'type': 'boolean'}}},
                },
                {
                    'name': 'google_workspace_action',
                    'description': 'Unified Google integration action router.',
                    'inputSchema': {
                        'type': 'object',
                        'properties': {
                            'action': {'type': 'string'},
                            'payload': {'type': 'object'},
                        },
                        'required': ['action'],
                    },
                },
                {
                    'name': 'get_identity_spec',
                    'description': 'Return runtime identity specification.',
                    'inputSchema': {'type': 'object', 'properties': {}},
                },
                {
                    'name': 'list_skills',
                    'description': 'List installed skills.',
                    'inputSchema': {'type': 'object', 'properties': {}},
                },
                {
                    'name': 'healthz',
                    'description': 'Return basic process health.',
                    'inputSchema': {'type': 'object', 'properties': {}},
                },
            ]
        }

    def _tool_call(self, name: str, arguments: dict[str, Any]) -> Any:
        if name in {'delete_page', 'put_page', 'sync_brain'}:
            self.policy.check_tool_call(name, arguments)

        if name == 'ingest_text':
            return self._trace_result(name, self.memory.upsert_from_text(
                source=arguments['source'],
                content=arguments['content'],
                access_level=arguments.get('access_level', 'private'),
            ))

        if name == 'query':
            question = arguments['question']
            limit = int(arguments.get('limit', 10))
            response_style = arguments.get('response_style', 'normal')
            hits = self.retrieval.hybrid_search(question, limit=limit)
            if not hits:
                return self._trace_result(name, apply_response_style({
                    'answer': 'The internal brain does not currently contain sufficient data for this question.',
                    'confidence': 0.22,
                    'references': [],
                    'reasoning_summary': 'Brain-first lookup completed with zero hits. No hallucinated answer returned.',
                }, response_style))

            top = hits[0]
            return self._trace_result(name, apply_response_style({
                'answer': f"{top['title']}: {top['compiled_truth_md'][:400]}",
                'confidence': float(top['confidence']),
                'references': [{'type': 'entity', 'slug': h['slug'], 'title': h['title']} for h in hits],
                'reasoning_summary': f'Hybrid retrieval returned {len(hits)} internal matches; top-ranked entity used for synthesis.',
            }, response_style))

        if name == 'run_agent':
            output = self.agent.run(arguments['signal'])
            response_style = arguments.get('response_style', 'normal')
            return self._trace_result(name, apply_response_style(output, response_style))

        if name == 'sync_brain':
            repos = arguments.get('repos') or []
            dry_run = bool(arguments.get('dry_run', True))
            return self._trace_result(name, self.sync.full_sync(repos=repos, dry_run=dry_run))

        if name == 'put_page':
            return self._trace_result(name, {'status': 'blocked', 'reason': 'tool not implemented; policy gate active'})

        if name == 'delete_page':
            return self._trace_result(name, {'status': 'blocked', 'reason': 'tool not implemented; policy gate active'})

        if name == 'google_workspace_action':
            return self._trace_result(name, self.connectors.google_workspace(arguments['action'], arguments.get('payload', {})))

        if name == 'get_identity_spec':
            return self._trace_result(name, self.identity.get())

        if name == 'list_skills':
            data = self.skills.list_skills()
            return self._trace_result(name, {'count': len(data), 'skills': data})

        if name == 'healthz':
            return self._trace_result(name, {'ok': True, 'service': 'velocitybrain-mcp'})

        raise ValueError(f'unknown tool: {name}')

    def run(self) -> None:
        while True:
            try:
                req = self._read_message()
            except EOFError:
                return
            except Exception:
                return

            if not req:
                continue

            req_id = req.get('id')
            method = req.get('method')
            params = req.get('params', {})

            if method == 'initialize':
                self._write_message(
                    self._ok(
                        req_id,
                        {
                            'protocolVersion': '2024-11-05',
                            'serverInfo': {'name': 'velocitybrain', 'version': '1.1.0'},
                            'capabilities': {'tools': {}},
                        },
                    )
                )
                continue

            if method == 'tools/list':
                self._write_message(self._ok(req_id, self._tool_list()))
                continue

            if method == 'tools/call':
                try:
                    name = params.get('name')
                    args = params.get('arguments', {})
                    result = self._tool_call(name, args)
                    self._write_message(self._ok(req_id, {'content': [{'type': 'text', 'text': json.dumps(result)}]}))
                except Exception as exc:
                    self._write_message(self._err(req_id, -32000, str(exc)))
                continue

            if method == 'shutdown':
                self._write_message(self._ok(req_id, {}))
                return

            if method == 'exit':
                return

            self._write_message(self._err(req_id, -32601, f'method not found: {method}'))


# Backward-compat alias
VelocityXMCPServer = VelocityBrainMCPServer


def main() -> int:
    try:
        VelocityBrainMCPServer().run()
        return 0
    except Exception:
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
