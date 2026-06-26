---
module_id: KE-2846
status: active
title: phase_gate_check.py 逻辑
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# phase_gate_check.py 逻辑

phase_gate_check.py 逻辑
```python
class PhaseGateChecker:
    def __init__(self, manifest_path: str):
        self.manifest = yaml.safe_load(open(manifest_path))

    def check_phase(self, phase: str) -> GateStatus:
        required_tasks = self.manifest["phases"][phase]["tasks"]
        statuses = {tid: self._get_status(tid) for tid in required_tasks}
        all_done = all(s == "Done" for s in statuses.values())
        return GateStatus(phase, all_done, statuses)

    def next_phase_allowed(self, current_phase: str) -> bool:
        # Check all current Phase tasks Done
```
