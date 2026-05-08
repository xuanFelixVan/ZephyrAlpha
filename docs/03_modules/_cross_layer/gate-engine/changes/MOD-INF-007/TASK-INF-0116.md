---
task_id: TASK-INF-0116
status: planned
priority: P0
severity: critical
module_id: MOD-INF-007
phase: 1
category: risk-mitigation
effort_estimated: 3h
effort_actual: null
assigned_to: null
reviewer: null
approver: null
source_section: §9
reference_docs:
  - D:\ZephyrAlpha\docs\03_modules\_cross_layer\gate-engine\blueprint.md
upstream_files:
  - D:\ZephyrAlpha\src\zephyr\gates\circuit_breaker.py
  - D:\ZephyrAlpha\src\zephyr\gates\gate_engine.py
downstream_outputs:
  - D:\ZephyrAlpha\src\zephyr\gates\circuit_breaker.py
  - D:\ZephyrAlpha\src\zephyr\gates\gate_engine.py
acceptance_criteria:
  - "AC-R1: 模块耦合→AOP 切面解除：GateEngine.evaluate_all 不感知任何具体 Gate 的 internals，门控组合 = 传入 gate_chain 参数"
  - "AC-R2: 门控自身故障→MetaCircuitBreaker（DD11）全局熔断——如果 GateEngine 本身连续 3 次内部故障→Switch 到 bypass 模式"
  - "AC-R3: DeepSeek幻觉→3连续fail→CircuitBreaker OPEN→fallback to 备选模型(GOV-AI-002)"
  - "AC-R4: G7 交付质量→G7D 深 buffer 门控（§30）——auto‑scan 最低质量标准 →动态 BLOCKED"
rollback_instructions:
  - "R1→回退耦合至 evaluate_all 内部 hardcode 全部 gates；R2→移除MetaCircuitBreaker、bypass权限=0；R3→ds v4不可用、no failover；R4→G7D buf被跳过"
created_at: 2026-05-06T23:50:00Z
updated_at: 2026-05-06T23:50:00Z
closed_at: null
dependencies:
  - TASK-INF-0101
  - TASK-INF-0102
  - TASK-INF-0105
blocked_by: [TASK-INF-0101, TASK-INF-0105]
blocks: []
tags: [gate-engine, R1, R2, R3, R4, risk-mitigation, coupling, meta-circuit, hallucination, delivery-quality]
version: 1.0.0
change_log: "v1.0.0 (2026-05-06): 基于 blueprint.md §9 风险与缓解 v1.4.3"
context_assembly_manifest:
  documents:
    - D:\ZephyrAlpha\docs\03_modules\_cross_layer\gate-engine\blueprint.md
  sections: ["§9 风险与缓解"]
  keywords: [R1, R2, R3, R4, risk, mitigation, coupling, failure, hallucination, quality]
  ai_reads_for_inference: true
---

# TASK-INF-0116: R1-R4 风险缓解实现

## 背景

blueprint.md §9 定义了 gate-engine 的 4 条风险：R1 模块间耦合、R2 门控自身故障、R3 DeepSeek 幻觉、R4 G7 交付质量不足。

## 实施

- **R1:** GateEngine 接受 `gate_chain` 参数→通过依赖反转解耦。任何一个 Gate 新增只需注册到 gate_chain。
- **R2:** MetaCircuitBreaker（DD11）监控 GateEngine 自身健康。3次内部异常→bypass模式（所有 gate 返回 PASSED + alert）。
- **R3:** CircuitBreaker 已在 TASK-INF-0105 实现。扩展到fallbackModel(GOV-AI-002)。
- **R4:** G7D 深度交付buffer→§30 Deep Compliance 门控。

## 验收

见 AC-R1~AC-R4。
