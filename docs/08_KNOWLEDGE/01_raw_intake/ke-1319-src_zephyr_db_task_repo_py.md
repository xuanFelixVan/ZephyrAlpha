---
module_id: KE-1231
status: active
title: src/zephyr/db/task_repo.py:447-463
category: governance
---

# src/zephyr/db/task_repo.py:447-463

src/zephyr/db/task_repo.py:447-463
if to_status == TaskStatus.IN_PROGRESS and self._enable_gate:
    gate_result = self._gate_engine.evaluate(task_obj, _STARTUP_GATE_ID)
    if not gate_result.passed:
        raise GateViolationError(gate_result)
```

当前已接入 **G1（PENDING→IN_PROGRESS）** 一处。
