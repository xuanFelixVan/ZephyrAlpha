---
task_id: "TASK-INF-0126"
source_blueprint: "MOD-INF-006"
source_section: "蓝图 §9 已知风险与缓解（33项）"

title: "实现风险缓解——33项已知风险的逐项缓解措施"
description: |
  逐一实现蓝图 §9 中 33 项已知风险的缓解措施。
  R1-R33：从上下文污染到断裂变更风险。
  优先缓解 P0 级别风险——R3/AI误解设计意图、R4/执行时路径漂移、R5/无限循环执行浪费。
  次级缓解 P1/P2 级别风险。
  缓解验证——每个缓解措施有对应的检查器或门禁校验。
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\models.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\lifecycle\\task_lifecycle_manager.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\reliability\\circuit_breaker.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\reliability\\context_guard.py"

downstream_outputs:
  - path: "D:\ZephyrAlpha\src\zephyr\l01_infrastructure\code_dedup_engine\risk_mitigator.py"
    description: "RiskMitigation——33项风险缓解措施注册表 + 检查器"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\risk\\risk_mitigation.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"

applicable_rules:
  - module_id: "MOD-INF-006"
    section: "§9"
    reason: "已知风险与缓解 33项全部——SSoT"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"
    reason: "§9 33项风险完整列表 + 缓解措施"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M3"
  - "M4"
  - "M9"
estimated_tokens: 25000
timeout_minutes: 90

acceptance_criteria:
  - "33项风险悉数登记——R1-R33 均有对应缓解措施 + 检查器"
  - "P0 风险3项：R27/蓝图内容陈旧过时、R28/任务对蓝图的100%覆盖承诺、R29/1人+AI维护复杂性"
  - "P1 风险9项：R9/R10/R11/R13/R18/R22/R23/R24/R25/R30/R31/R32/R33"
  - "P2 风险17项：R1/R2/R3/R4/R5/R6/R7/R8/R12/R14/R15/R16/R17/R19/R20/R21/R26"
  - "每项缓解措施在相关模块中有代码实现或配置文件硬约束"
  - "缓解措施可在不用盲目增加代码复杂度的情况下执行"
  - "已缓解风险条目有对应的回归测试"

rollback_instructions: |
  1. 移除 risk_mitigation.py
  2. 移除关联模块中的风险检查代码

depends_on: ["TASK-INF-0102", "TASK-INF-0106", "TASK-INF-0108"]
blocked_by: []

status: "done"

tags_fn:
  - "infra"
  - "risk"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "MOD-INF-006"

completed_gates: []
blocked_gates: {}

artifact_paths: []
audit_findings: []
ke_entries: []

ai_autonomy_level: "supervised"
autonomy_checklist: []
---

# 实现风险缓解——33项风险逐项缓解

## 目标

实现蓝图 §9 中全部 33 项已知风险的缓解措施：
- P0（3项）：R27/R28/R29
- P1（9项）：R9/R10/R11/R13/R18/R22/R23/R24/R25/R30/R31/R32/R33
- P2（17项）：R1/R2/R3/R4/R5/R6/R7/R8/R12/R14/R15/R16/R17/R19/R20/R21/R26

## 触发条件

- TASK-INF-0102/0106/0108 完成

## 执行步骤

### 读
- 蓝图 §9 完整 33 项风险列表

### 做
1. 实现 RiskMitigation 注册表——33项风险→缓解措施映射
2. 对每项风险：
   - 实现对应的代码检查器或门禁约束
   - P0 风险必须硬阻塞 income
   - 已缓解项回归测试

### 产
- risk_mitigation.py

### 检
```python
rm = RiskMitigation()
for risk_id in range(1, 34):
    assert rm.has_mitigation(f"R{risk_id}")
```

## 验收标准

| # | 指标 | 目标 |
|---|------|------|
| 1 | build | import 无错误 |
| 2 | test | 33项均有测试 |
| 3 | coverage | 风险覆盖 100% |

## 风险与缓解

| 风险 | 缓解 |
|------|------|
| 缓解措施过度——增加不必要复杂度 | 按优先级分级：P0硬阻塞/P1软检查/P2仅记录 |
