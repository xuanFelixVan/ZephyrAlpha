---
task_id: "TASK-INF-0029"
source_blueprint: "MOD-INF-015"
source_section: "蓝图 §21 后果（拆除 + 废墟） + §22 变更记录"

title: "实现 Telemetry 模块拆除后果清单 + 变更记录维护 + 版本管理"
description: |
  1. 拆除后果清单（蓝图 §21）：
     - 1 个模块会受影响：模块内 metrics/logs/traces/ai_behavior 四个 API 调用点全部失效
     - 代价：全部返回 None（不崩溃） + shutdown() 返回 success(无数据 flush) + FLE 失去所有模块级别可观测信号
     - 零废墟要求：不留下孤儿数据库文件
  2. 变更记录（蓝图 §22）：
     - v1.0 初始版本记录
     - 后续 operation/truncation/rename 均在 §22 中记录
     - 每次变更标记 caller（human/AI）+ session_id + hash
  3. 版本回滚：每次变更可追溯到上一版本
priority: "P2"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\system-telemetry\\blueprint.md"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\decommission.py"
    description: "拆除后果清单验证器——模块拆除时自动销毁数据库/清理孤儿文件"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\versioning.py"
    description: "变更记录管理器——每次变更写入 §22 + 版本回滚支持"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\decommission.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\versioning.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\system-telemetry\\blueprint.md"

applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "Pydantic V2"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\system-telemetry\\blueprint.md"
    reason: "§21——拆除影响表 + 废墟清单 + 原地复活代价表 + §22——变更记录 v1.0 + 格式规范"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
estimated_tokens: 5000
timeout_minutes: 20

acceptance_criteria:
  - "decommission()→清理 telemetry_meta 表 + telemetry_* 表 → 确认无孤儿文件"
  - "const_vars: 永不写数据库"
  - "FLE et audit trail: 失去 data_freshness / data_quality_score 实时信号"
  - "versioning()→记录变更到 §22 格式 {caller}/{session_id}/{hash6}"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\l12_system_telemetry\decommission.py
  2. 删除 D:\ZephyrAlpha\src\zephyr\l12_system_telemetry\versioning.py

depends_on:
  - "TASK-INF-0001"
blocked_by: []
status: "created"

tags_fn:
  - "observability"
  - "governance"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "MOD-INF-015"

completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---

# TASK-INF-0029: 拆除后果 + 变更记录 + 版本管理

## 目标
实现模块拆除时的零废墟清理 + §22 变更记录的自动化维护。

## 执行步骤

### 读
- 蓝图 §21：拆除影响/废墟/复活代价 + §22：变更记录格式

### 做
1. decommission.py：拆除时清理所有 telemetry_* 表 + 数据目录
2. versioning.py：变更记录自动化——写入 §22 格式变更条目

### 检
```python
from zephyr.l12_system_telemetry.decommission import decommission
result = decommission(test_mode=True)
assert result.orphan_files == 0
```

## 验收标准
| # | 指标 | 目标 |
|---|------|------|
| 1 | decommission | zero orphan files |
| 2 | change_log | caller+session_id+hash recorded |
| 3 | rollback | version reversibility |
