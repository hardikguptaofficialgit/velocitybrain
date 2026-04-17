from __future__ import annotations

from src.services.skill_registry import SkillRegistry


def build_openclaw_profile() -> dict:
    skills = SkillRegistry('skills').list_skills()
    tool_names = [
        'ingest_text',
        'query',
        'run_agent',
        'sync_brain',
        'put_page',
        'delete_page',
        'google_workspace_action',
        'get_identity_spec',
        'list_skills',
        'healthz',
    ]
    return {
        'name': 'velocitybrain',
        'client': 'openclaw',
        'server': {
            'command': 'velocitybrain',
            'args': ['serve', 'mcp'],
        },
        'defaults': {
            'destructive_tools_allowed': False,
            'preferred_modes': ['healthz', 'list_skills', 'query', 'run_agent'],
            'traceability': True,
        },
        'capabilities': {
            'tool_count': len(tool_names),
            'tools': tool_names,
            'skill_count': len(skills),
            'skill_categories': sorted({skill.get('category', 'uncategorized') for skill in skills}),
        },
        'recommended_smoke_flow': [
            'healthz',
            'list_skills',
            'query',
            'run_agent',
        ],
    }
