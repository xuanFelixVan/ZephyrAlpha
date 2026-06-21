---
module_id: KE-2089
status: active
title: 3.2 Gate 判定接口
category: module_blueprint
---

# 3.2 Gate 判定接口

3.2 Gate 判定接口

```python
class GateResult:
    gate_id: str          # "G0"~"G7" | "G1"~"G5" (KMS) | "GATE-18"
    status: GateStatus    # PASS | PASS_WITH_WARNINGS | FAIL | CRITICAL_FAIL
    reasons: list[str]    # 失败原因
    affected_tasks: list[str]  # 受影响的任务 ID
    timestamp: datetime
```
