---
task_id: TASK-INF-0109
status: planned
priority: P1
severity: high
module_id: MOD-INF-007
phase: 1
category: implementation
effort_estimated: 2h
effort_actual: null
assigned_to: null
reviewer: null
approver: null
source_section: §5.3
reference_docs:
  - D:\ZephyrAlpha\docs\03_modules\_cross_layer\gate-engine\blueprint.md
upstream_files:
  - D:\ZephyrAlpha\src\zephyr\gates\gate_result.py
  - D:\ZephyrAlpha\src\zephyr\gates\circuit_breaker.py
downstream_outputs:
  - D:\ZephyrAlpha\src\zephyr\gates\task_gates\g4_tracking.py
  - D:\ZephyrAlpha\src\zephyr\gates\task_gates\g5_error.py
  - D:\ZephyrAlpha\src\zephyr\gates\task_gates\g6_artifact.py
acceptance_criteria:
  - "AC1: G4_GATE_YAML gate_name='Task-G4: Execution Tracking'、gate_level='G4'、required_context=['task_id','event_type']、check_method='inject_tracking_event'"
  - "AC2: G5_GATE_YAML gate_name='Task-G5: Error Circuit Breaker'、gate_level='G5'、required_context=['task_id','model','error_log']、check_method='check_circuit_breaker'、trigger='3 consecutive failures'"
  - "AC3: G6_GATE_YAML gate_name='Task-G6: Artifact Integrity'、gate_level='G6'、required_context=['downstream_outputs']、check_method='verify_downstream_outputs'、min_file_size_bytes=1"
  - "AC4: G4→MetadataRegistry.tracking_event 注入（G4通过时才发），G5→CircuitBreaker集成、G6→文件路径对照+文件>0字节"
rollback_instructions:
  - "g4_tracking.py/g5_error.py/g6_artifact.py→空桩→check_all() 返回 GateResult.PASSED；CircuitBreaker 引用移除"
created_at: 2026-05-06T23:43:00Z
updated_at: 2026-05-06T23:43:00Z
closed_at: null
dependencies:
  - TASK-INF-0102
  - TASK-INF-0104
  - TASK-INF-0105
blocked_by: [TASK-INF-0102, TASK-INF-0104, TASK-INF-0105]
blocks: []
tags: [gate-engine, G4, G5, G6, during-execution]
version: 1.0.0
change_log: "v1.0.0 (2026-05-06): 初始创建，基于 blueprint.md §5.3 v1.4.3"
context_assembly_manifest:
  documents:
    - D:\ZephyrAlpha\docs\03_modules\_cross_layer\gate-engine\blueprint.md
  sections: ["§5.3 G4-G6 执行中门控"]
  keywords: [G4, G5, G6, tracking, circuit-breaker, artifact, execution]
  ai_reads_for_inference: true
---

# TASK-INF-0109: G4-G6 执行中门控结构化 YAML 规则落地

## 背景与动机

G4-G6 是任务执行中的门控（blueprint.md §5.3）：G4 记录追踪事件、G5 集成 CircuitBreaker 熔断、G6 验证产物完整性。三道门在任务执行过程中陆续触发。

## 实施计划

### G4: Execution Tracking

```yaml
gate_name: "Task-G4: Execution Tracking"
gate_level: "G4"
required_context: ["task_id", "event_type"]
check_method: "inject_tracking_event"
```

实现：调用 `MetadataRegistry.inject_tracking_event(task_id=..., event_type="gate_passed", details={"gate_level":"G4"})`。

### G5: Error Circuit Breaker

```yaml
gate_name: "Task-G5: Error Circuit Breaker"
gate_level: "G5"
required_context: ["task_id", "model", "error_log"]
check_method: "check_circuit_breaker"
trigger: "3 consecutive failures"
```

实现：检查 `CircuitBreaker.is_open(model)` → OPEN→BLOCKED；record_failure/record_success 交由上游 (e.g., script runner) 调用。

### G6: Artifact Integrity

```yaml
gate_name: "Task-G6: Artifact Integrity"
gate_level: "G6"
required_context: ["downstream_outputs"]
check_method: "verify_downstream_outputs"
min_file_size_bytes: 1
```

实现：遍历 `task_dict["downstream_outputs"]` → 文件 exists + size>0 → 缺或空→BLOCKED。

## 回退方案

三文件→空桩→`check_all()` 返回 `GateResult.PASSED`。

## 验收标准

| # | 标准 |
|---|------|
| AC1 | G4 YAML 含 gate_name/level/context/method |
| AC2 | G5 YAML 含 trigger: "3 consecutive failures" |
| AC3 | G6 YAML 含 min_file_size_bytes: 1 |
| AC4 | G5 正确集成 CircuitBreaker 状态查询 |
