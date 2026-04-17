import json
from pathlib import Path


class SkillRegistry:
    def __init__(self, skills_root: str = 'skills'):
        self.skills_root = Path(skills_root)

    def list_skills(self) -> list[dict]:
        out = []
        for fp in self.skills_root.rglob('*.json'):
            try:
                out.append(json.loads(fp.read_text(encoding='utf-8')))
            except Exception:
                continue
        return sorted(out, key=lambda x: (x.get('category', ''), x.get('name', '')))

    def resolve(self, intent: str) -> list[dict]:
        q = intent.lower()
        matches = []
        for s in self.list_skills():
            triggers = ' '.join(s.get('trigger_conditions', [])) if isinstance(s.get('trigger_conditions'), list) else ''
            if any(t in q for t in triggers.lower().split()):
                matches.append(s)
        return matches[:8]
