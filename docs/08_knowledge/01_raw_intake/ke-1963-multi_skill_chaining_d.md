---
module_id: KE-1872
status: active
title: 2.3 Multi-Skill Chaining (D-019-08)
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 2.3 Multi-Skill Chaining (D-019-08)

2.3 Multi-Skill Chaining (D-019-08)

```python
class SkillChainManager:
    MAX_DEPTH = 3

    def can_chain(self, skill_a: str, skill_b: str) -> bool:
        if self._chain_depth >= self.MAX_DEPTH:
            return False
        return not self._detects_cycle(skill_a, skill_b)

    def manage_fragmentation(self, active_skills: list):
        if len(active_skills) > 3:
            old_skill = active_skills[0]
            self._compact_and_unload(old_skill)
```
