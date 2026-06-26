---
module_id: KE-1688
status: active
title: 2.10 CT-ORC-GATE-001：任务系统 → 门控引擎 — 任务执行前后门禁判定
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 2.10 CT-ORC-GATE-001：任务系统 → 门控引擎 — 任务执行前后门禁判定

2.10 CT-ORC-GATE-001：任务系统 → 门控引擎 — 任务执行前后门禁判定

```yaml
contract: CT-ORC-GATE-001
title: "任务生命周期的G0-G7门禁判定"
systems:
  - role: producer
    name: orchestrator
    path: "src/zephyr/orchestrator/"
    blueprint: "MOD-TASK_SYSTEM"
  - role: consumer
    name: gate_engine
    path: "src/zephyr/gates/"
    blueprint: "MOD-GATE_ENGINE"

data_flow:
  direction: bidirectional
  orc_to_gate:
    trigger: "TaskCard 状态迁移到 PENDING → 进入 G0 判定"
    payload: "TaskCard 完整28字段"
    gating_sequence:
      - gate: G0
        at: "任务进入 TODO 前"
        checks: ["priority_valid", "assignee_exists", "deadline_future"]
        on_fail: "回退到 DRAFT"
      - gate: G1
        at: "任务进入 IN_PROGRESS 前"
        checks: ["context_built", "dependencies_met"]
        on_fail: "BLOCKED + 等待依赖"
      - gate: G7
        at: "任务标记 COMPLETED 前"
        checks: ["all_findings_resolved", "output_validated"]
        on_fail: "REVIEW_REQUIRED + FLE记录"
  gate_to_orc:
    response: "PASS | FAIL | PASS_WITH_WARNINGS | CRITICAL_FAIL"
    response_detail: "{ gate_id, violations[], suggestions[] }"
    action: "Orc 根据 response 更新 TaskCard.status"

design_rationale: >
  G0-G7不是全局门（区别于GATE-18 pre-commit），而是任务粒度门。
  每个TaskCard在其生命周期中依次通过G0→G1→...→G7，
  任何一个FAIL都会阻断任务流转，直到violation被消除。

ai_prompt: >
  你是CT-ORC-GATE-001的AI agent。当TaskCard状态迁移需要门禁判定时：
  (1) G0(进入TODO前)→校验priority_valid+assignee_exists+deadline_future→FAIL退回DRAFT；
  (2) G1(进入IN_PROGRESS前)→校验context_built+dependencies_met→FAIL进入BLOCKED等待依赖；
  (3) G7(标记COMPLETED前)→校验all_findings_resolved+output_validated→FAIL进入REVIEW_REQUIRED；
  (4) status迁移必须遵循DRAFT→TODO→IN_PROGRESS→REVIEW→COMPLETED，不允许跳步（AP6）；
  (5) 返回的response必须包含violations[]+suggestions[]——不要只返回PASS/FAIL而不给原因；
  (6) 不要为"加速流程"而手动修改response绕过门禁。

telemetry:
  metrics:
    - {name: "task_gate_pass_count", type: counter, labels: [gate_id, response]}
    - {name: "task_gate_violation_count", type: counter, labels: [gate_id, violation_type]}
    - {name: "task_gate_latency_ms", type: histogram, buckets: [1,5,10,50,100]}
    - {name: "task_status_transition_invalid", type: counter}
  traces:
    required_spans: ["gate_g0_check", "gate_g1_check", "gate_g7_check"]
```
