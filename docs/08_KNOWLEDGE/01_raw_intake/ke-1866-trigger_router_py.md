---
module_id: KE-1775
status: active
title: 2.2 trigger_router.py 实现
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 2.2 trigger_router.py 实现

2.2 trigger_router.py 实现

```python
from typing import Optional, Tuple
from enum import Enum


class ConstructionStage(str, Enum):
    IDEA = "想法/草稿"
    PRE_AUDIT = "审计（施工前）"
    BLUEPRINT = "蓝图/设计"
    CONSTRUCTION = "施工/实现"
    VERIFICATION = "验收/验证"
    POST_AUDIT = "审计（施工后）"


class TriggerRouter:
    STAGE_ROUTING = {
        ConstructionStage.IDEA: {"role": "architect", "domain_default": "master-blueprint"},
        ConstructionStage.PRE_AUDIT: {"role": "governor", "domain_default": "gate-engine"},
        ConstructionStage.BLUEPRINT: {"role": "architect", "domain_match": "topic"},
        ConstructionStage.CONSTRUCTION: {"role": "implementer", "domain_match": "module"},
        ConstructionStage.VERIFICATION: {"role": "governor", "domain_match": "module"},
        ConstructionStage.POST_AUDIT: {"role": "governor", "domain_default": "drift-detector"},
    }

    TASK_ROUTING = {
        "database|migration|sql|atm": {"domain": "database-specialist", "role": "implementer"},
        "mcp server|tool|protocol": {"domain": "mcp-specialist", "role": "implementer"},
        "context|pipeline": {"domain": "context-specialist", "role": "implementer"},
        "feedback|loop": {"domain": "feedback-specialist", "role": "implementer"},
        "gate|rule|policy": {"domain": "gate-specialist", "role": "governor"},
        "permission|rbac": {"domain": "agent-specialist", "role": "governor"},
        "blueprint": {"domain": "master-blueprint", "role": "architect"},
        "audit|compliance|governance": {"domain": "drift-detector", "role": "governor"},
        "knowledge|ke": {"domain": "knowledge-specialist", "role": "implementer"},
    }

    DEFAULT = {"role": "implementer", "domain_default": None}

    def route(self, stage: Optional[ConstructionStage], task_description: str) -> Tuple[str, str]:
        ...
```
