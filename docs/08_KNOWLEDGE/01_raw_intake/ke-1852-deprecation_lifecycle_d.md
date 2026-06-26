---
module_id: KE-1761
status: active
title: 2.2 Deprecation Lifecycle (D-019-11)
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 2.2 Deprecation Lifecycle (D-019-11)

2.2 Deprecation Lifecycle (D-019-11)

```python
class SkillLifecycle:
    STATES = ["active", "deprecated", "retired", "removed"]

    def transition(self, skill_id: str, to_state: str):
        valid_transitions = {
            "active": ["deprecated"],
            "deprecated": ["active", "retired"],
            "retired": ["removed"],
        }
        assert to_state in valid_transitions[self.get_state(skill_id)]
```
