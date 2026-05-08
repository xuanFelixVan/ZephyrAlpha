---
module_id: KE-module_blu-2_2-000
title: 2.2 零上下文启动
category: module_blueprint
---

# 2.2 零上下文启动

2.2 零上下文启动

```python
class ContextOptimizer:
    def warm_start(self, session_count: int):
        if session_count <= 3:
            return self._load_onboarding_skill()
        return None

    def progressive_context_build(self, task_description: str):
        """从零上下文开始，按需加载，避免一次性加载全部 Skill metadata"""
        ...
```
