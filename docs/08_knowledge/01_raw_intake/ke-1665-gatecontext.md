---
module_id: KE-1575
status: active
title: 17.3 GateContext — 上下文传播
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 17.3 GateContext — 上下文传播

17.3 GateContext — 上下文传播

当前上下文散落在`check.params`中。需标准化`GateContext`：

```python
@dataclass
class GateContext:
    task_id: str
    task_type: str
    priority: str
    assigned_model: str
    target_module_id: str
    module_blueprint_version: str
    module_dependencies: list[str]
    session_id: str
    blueprint_reads: list[str]     # 本次session已读蓝图
    tool_calls_made: list[str]
    recent_gate_results: dict[str, GateResult]
    circuit_breaker_states: dict[str, str]
    capability_level: str          # AI能力等级
    global_token_usage: int

    def serialize(self) -> dict: ...
    @classmethod
    def from_task_and_session(cls, task, session) -> GateContext: ...
```
