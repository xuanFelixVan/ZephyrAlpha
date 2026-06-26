---
module_id: KE-2013---resume-000
status: active
title: 3. preempt_check / resume
category: module_blueprint
ttl: permanent
---

# 3. preempt_check / resume

3. preempt_check / resume

```python
def preempt_check(task_card: TaskCard, active_dispatches: dict[str, ModuleResult]) -> PreemptionRecord|None:
    """如果新任务优先级更高→选择最低优先级活跃任务→挂起"""

def resume(task_id: str) -> PipelineResult:
    """从 savepoint 恢复到挂起时的 module_progress→继续执行剩余模块"""
```
