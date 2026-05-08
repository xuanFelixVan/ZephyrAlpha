---
task_id: TASK-INF-0115
status: planned
priority: P0
severity: critical
module_id: MOD-INF-007
phase: 1
category: integration
effort_estimated: 2h
effort_actual: null
assigned_to: null
reviewer: null
approver: null
source_section: §8.2、CT-ORC-GATE-001
reference_docs:
  - D:\ZephyrAlpha\docs\03_modules\_cross_layer\gate-engine\blueprint.md
  - D:\ZephyrAlpha\tool_contracts.yaml
upstream_files:
  - D:\ZephyrAlpha\src\zephyr\gates\gate_engine.py
  - D:\ZephyrAlpha\src\zephyr\orchestration\orchestrator.py
downstream_outputs:
  - D:\ZephyrAlpha\src\zephyr\gates\gate_engine.py
acceptance_criteria:
  - "AC1: Orchestrator 在执行 `task: run` 之前调用 GateEngine.evaluate_all(task_dict, task_gates_chain)——G0-G7按序执行—— CT-ORC-GATE-001满足"
  - "AC2: BLOCKED (硬/软) 阻止 Orchestrator 进入执行→任务状态=? blocked_goal: code_not_eval_until_pass"
  - "AC3: SOFT_BLOCKED→Orchestrator记录warning(emit to telemetry)但允许执行→符合DD-ORC容许"
  - "AC4: CT-ORC-GATE-001在高负载下不显著降级Orchestrator吞吐——GateEngine p95 延时<100ms（每个gate）"
rollback_instructions:
  - "移除 Orchestrator→GateEngine 的调用点 → 任务恢复为无门控直接执行"
  - "检查 counterfactual: 运行Orchestrator集成测试 → 确认 GateEngine 不再参与"
created_at: 2026-05-06T23:49:00Z
updated_at: 2026-05-06T23:49:00Z
closed_at: null
dependencies:
  - TASK-INF-0101
  - TASK-INF-0102
  - TASK-INF-0106
blocked_by: [TASK-INF-0101, TASK-INF-0102, TASK-INF-0106]
blocks: [TASK-INF-0122]
tags: [gate-engine, CT-ORC-GATE-001, integration, orchestrator, 《royal_walkthrough》]
version: 1.0.0
change_log: "v1.0.0 (2026-05-06): 基于 blueprint.md §8.2 CT-ORC-GATE-001 v1.4.3"
context_assembly_manifest:
  documents:
    - D:\ZephyrAlpha\docs\03_modules\_cross_layer\gate-engine\blueprint.md
  sections: ["§8.2 CT-ORC-GATE-001"]
  keywords: [CT-ORC-GATE-001, orchestrator, integration, task-run, AOP, gate-chain]
  ai_reads_for_inference: true
---

# TASK-INF-0115: CT-ORC-GATE-001 集成——Orchestrator 与 GateEngine 对接

## 背景

CT-ORC-GATE-001 定义了 Orchestrator（任务编排器）在执行任务前 MUST 通过 GateEngine G0-G7 门控链的契约（blueprint.md §8.2）。这是 gate-engine 作为"裁判系统"的强制介入点——任何绕过门控直接执行的任务 = 违规。

## 实施计划

在 `orchestrator.py` 的 `execute(task_id)` 方法中：

```python
from zephyr.gates.gate_engine import GateEngine
from zephyr.gates.task_gates import (
    G0EntryGate, G1PreExecGate, G2ResourceGate, G3EnvGate,
    G4TrackingGate, G5ErrorGate, G6ArtifactGate, G7DeliveryGate
)

class Orchestrator:
    def __init__(self):
        self.gate_engine = GateEngine()
        self.task_gate_chain = [
            G0EntryGate(), G1PreExecGate(), G2ResourceGate(),
            G3EnvGate(), G4TrackingGate(), G5ErrorGate(),
            G6ArtifactGate(), G7DeliveryGate()
        ]

    def execute(self, task_id: str) -> None:
        task_dict = self.task_repo.load(task_id)
        result = self.gate_engine.evaluate_all(task_dict, self.task_gate_chain)
        if result.status == GateStatus.BLOCKED:
            self._reject(task_id, result)
            return
        if result.status == GateStatus.SOFT_BLOCKED:
            self._emit_warning(task_id, result)
        self._run(task_id)
```

## 回退方案

1. 移除 `orchestrator.py` 中 GateEngine 调用
2. 恢复 `execute()` 为直接 `self._run(task_id)`
3. 运行集成测试确认 GateEngine 不再参与

## 验收标准

| # | 标准 |
|---|------|
| AC1 | Orchestrator.execute → GateEngine.evaluate_all → 顺序 gate chain |
| AC2 | BLOCKED → 拒绝执行，任务.status = blocked |
| AC3 | SOFT_BLOCKED → 允许执行 + emit warning 到 telemetry |
| AC4 | p95 延时 <100ms/gate（非阻塞性性能） |
