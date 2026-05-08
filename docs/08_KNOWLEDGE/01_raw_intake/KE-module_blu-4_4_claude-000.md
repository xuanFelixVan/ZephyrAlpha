---
module_id: KE-module_blu-4_4_claude-000
title: 4.4 Claude 救援触发记录
category: module_blueprint
---

# 4.4 Claude 救援触发记录

4.4 Claude 救援触发记录

```python
class ClaudeRescueTrigger(BaseModel):
    triggered: bool
    reason: str
    deepseek_failure_count: int
    glm_rejection_count: int
    is_owner_critical: bool
    has_security_tag: bool
    is_experimental: bool
```
