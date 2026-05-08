---
task_id: "TASK-INF-0223"
source_blueprint: "MOD-INF-020"
source_section: "蓝图 §5.2 蓝图漂移检测（决策 D-020-06）+ §2.13 跨 IDE 一致性（决策 D-020-19）"

title: "实现蓝图漂移检测器 + 跨 IDE 一致性交叉验证"
description: |
  实现 `src/zephyr/audit_trail/drift.py` 中的 `DriftDetector` 蓝图漂移检测器：
  - compare(): 单条目对比蓝图约束 → 漂移检测（unauthorized_op/skipped_check/immutable_violation）
  - batch_compare(): 批量漂移检测 → 生成 DriftReport
  - 漂移来源跟踪：(a) AI 跳过蓝图检查项 (b) AI 执行了未授权操作 (c) AI 修改了 immutable 文件
  
  实现 `src/zephyr/audit_trail/cross_ide.py` 中的 `CrossIDEConsistencyChecker`：
  - find_conflicts(): 扫描所有 IDE JSONL → (task_id, action_type, file_path, lamport_clock窗口) 匹配同一操作
  - merge_consensus(): 多 IDE 视角合并——多数一致 → 可信
  - 矛盾严重度: low/high/critical → 不一致 > 0 → P1 alert
  落地 D-020-06 + D-020-19。覆盖风险 R8/R15。覆盖盲点 B18。
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\audit-trail\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\drift.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\cross_ide.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\models.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\drift.py"
    description: "DriftDetector 类 + DriftResult/DriftReport 模型"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\cross_ide.py"
    description: "CrossIDEConsistencyChecker 类 + ConsistencyConflict 模型"
  - path: "D:\\ZephyrAlpha\\tests\\audit_trail\\test_drift.py"
    description: "漂移检测测试——3种漂移类型模拟"
  - path: "D:\\ZephyrAlpha\\tests\\audit_trail\\test_cross_ide.py"
    description: "跨IDE一致性测试——冲突检测+共识合并"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\drift.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\cross_ide.py"
  - "D:\\ZephyrAlpha\\tests\\audit_trail\\test_drift.py"
  - "D:\\ZephyrAlpha\\tests\\audit_trail\\test_cross_ide.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\**\\*.py"

applicable_rules:
  - module_id: "GOV-CMP-002"
    section: "AUD-002"
    reason: "漂移检测告警规则"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\audit-trail\\blueprint.md"
    reason: "§5.2——DriftDetector + §2.13 CrossIDE + D-020-06/19"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 10000
timeout_minutes: 60

acceptance_criteria:
  - "unauthorized_op 检测：AI 操作了蓝图未授权的文件 → drift_severity=high"
  - "skipped_check 检测：AI 未执行蓝图规定的检查项 → drift_severity=medium"
  - "immutable_violation 检测：AI 修改了 immutable 文件 → drift_severity=critical"
  - "CrossIDE: TRAE 记录'成功' vs Cursor 记录'失败' → 冲突检测 critical"
  - "CrossIDE: 3 个 IDE 中 2 个一致 → merge_consensus 选多数"
  - "10 份蓝图覆盖漂移检测（scaffold验收标准）"
  - "漂移检测集成到 anomaly pipeline——drift_severity=critical → P0 block"

rollback_instructions: |
  1. 删除 drift.py / cross_ide.py 内容
  2. 删除 test_drift.py / test_cross_ide.py

depends_on:
  - "TASK-INF-0209"
  - "TASK-INF-0222"
blocked_by: []

status: "created"

tags_fn:
  - "infra"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "experimental"
tags_mo:
  - "MOD-INF-020"

completed_gates: []
blocked_gates: {}

artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "semi_autonomous"
autonomy_checklist: []
---
