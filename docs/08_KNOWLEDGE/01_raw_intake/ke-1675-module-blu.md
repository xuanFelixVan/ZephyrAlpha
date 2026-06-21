---
module_id: KE-1585
status: active
title: 18.3 门禁模拟器
category: module_blueprint
---

# 18.3 门禁模拟器

18.3 门禁模拟器

```python
class GateSimulator:
    """门禁全链路模拟——不写SQLite/不改状态/不触发事件"""

    def simulate_all(self, task: Task, session_context: dict) -> SimulationReport:
        """返回全部已注册门禁的模拟判定——PASS/FAIL预测+fix_hint+severity+耗时"""

@dataclass
class SimulationReport:
    task_id: str
    total_gates: int
    passed: int
    blocked: int
    warnings: int
    results: dict[str, GateResult]
    summary: str          # "7/10 PASS, 2 BLOCKED, 1 WARNING"
    fix_checklist: list[str]  # 按优先级排序的修复步骤清单
    @property
    def would_pass_all(self) -> bool: ...
```

---
