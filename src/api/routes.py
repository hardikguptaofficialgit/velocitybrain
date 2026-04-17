import uuid

from fastapi import APIRouter

from src.models.api import EvalQueryRequest
from src.services.compliance_service import ComplianceService
from src.services.evaluation_service import EvaluationService
from src.services.openclaw_profile import build_openclaw_profile
from src.services.runtime_status import build_runtime_status

router = APIRouter(prefix='/v1')
evaluation = EvaluationService()
compliance = ComplianceService()

@router.get('/healthz')
def healthz():
    return {'ok': True}


@router.post('/eval/query')
def eval_query(payload: EvalQueryRequest):
    result = evaluation.eval_query(payload.question, payload.expected_slugs, k=payload.k, org_key=payload.org_key)
    return {
        **result,
        'type_distribution': dict(result['type_distribution']),
        'trace_id': f'eval-{uuid.uuid4()}',
    }


@router.get('/audit/recent')
def recent_audit(limit: int = 100):
    result = compliance.recent_audit(limit=limit)
    return {
        **result,
        'trace_id': f'audit-{uuid.uuid4()}',
    }


@router.get('/openclaw/profile')
def openclaw_profile():
    profile = build_openclaw_profile()
    return {
        **profile,
        'trace_id': f'openclaw-{uuid.uuid4()}',
    }


@router.get('/openclaw/capabilities')
def openclaw_capabilities():
    profile = build_openclaw_profile()
    capabilities = profile['capabilities']
    return {
        'name': profile['name'],
        'client': profile['client'],
        'tool_count': capabilities['tool_count'],
        'skill_count': capabilities['skill_count'],
        'skill_categories': capabilities['skill_categories'],
        'recommended_smoke_flow': profile['recommended_smoke_flow'],
        'trace_id': f'openclaw-{uuid.uuid4()}',
    }


@router.get('/runtime/status')
def runtime_status(audit_limit: int = 5):
    status = build_runtime_status(audit_limit=audit_limit)
    return {
        **status,
        'trace_id': f'status-{uuid.uuid4()}',
    }
