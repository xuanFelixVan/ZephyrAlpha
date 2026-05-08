---
module_id: KE-module_blu-2_4_lineage__d-019-13-000
title: 2.4 Lineage (D-019-13)
category: module_blueprint
---

# 2.4 Lineage (D-019-13)

2.4 Lineage (D-019-13)

```python
class SkillLineage:
    def record(self, entity_type: str, entity_id: str, parent_entity: str):
        self.chain.append(LineageNode(entity_type, entity_id, parent_entity, timestamp=now()))
        # Blueprint → FactoryAgent → Skill → Session → Artifact
```
