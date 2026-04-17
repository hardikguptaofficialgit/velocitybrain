#!/usr/bin/env python3
import json
from pathlib import Path

root = Path('skills')
all_skills = [json.loads(p.read_text(encoding='utf-8')) for p in root.rglob('*.json')]
print(f"skills={len(all_skills)}")
for s in sorted(all_skills, key=lambda x: x['skill_key'])[:5]:
    print(s['skill_key'])
