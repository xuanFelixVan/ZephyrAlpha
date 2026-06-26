---
module_id: KE-2863
status: active
title: Python 实现
category: module_blueprint
ttl: permanent
---

# Python 实现

Python 实现

```python
class G7DeliveryGate(Gate):
    def check_all(self, task_dict: dict) -> GateResult:
        violations = []
        # Step 1: AC 全部通过
        ac_list = task_dict.get("acceptance_criteria", [])
        if any("FAILED" in str(ac) or "SKIPPED" in str(ac) for ac in ac_list):
            violations.append("G7-STEP1: Not all AC passed")
        # Step 2: ZALP 零错误
        if task_dict.get("zalp_error_count", 0) != 0:
            violations.append("G7-STEP2: ZALP errors remain")
        # Step 3: 双轨一致
        md_fields = {k: task_dict.get(k) for k in ["task_id","status","priority","severity","effort_estimated","closed_at"]}
        repo_fields = task_dict.get("task_repo_fields", {})
        if md_fields != repo_fields:
            violations.append(f"G7-STEP3: Dual-track mismatch: md={md_fields}, repo={repo_fields}")
        if violations:
            return GateResult(status=GateStatus.BLOCKED, gate_level="G7", violations=violations)
        return GateResult(status=GateStatus.PASSED, gate_level="G7")
```
