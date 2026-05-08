---
task_id: "TASK-INF-0004"
source_blueprint: "MOD-INF-015"
source_section: "蓝图 §2e FeatureFlag 控制矩阵"

title: "实现 Telemetry FeatureFlag 控制矩阵：8 个特性开关 + AI 施工约定"
description: |
  对接 shared/flags.py 的 FeatureFlag 三态机制，实现 Telemetry 专属的 8 个特性开关：
  enable_profiling / debug_full_sampling / cost_alert_threshold_usd / log_level_override / 
  enable_ai_behavior_tracking / cardinality_strict_mode / archive_auto_cleanup / enable_slo_postmortem。
  所有开关默认 OFF（除 enable_ai_behavior_tracking 默认 ON），人工在 config/flags.yaml 启用后生效。
  AI 施工约定：新增功能 MUST 创建对应 flag（初始 OFF），禁止 AI 自行修改 FlagState。
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\system-telemetry\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\flags.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\config\\flags.yaml"
    description: "FeatureFlag 定义——添加 telemetry.* 8 个 flags"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\flags.py"
    description: "Telemetry FeatureFlag 客户端——封装 shared/flags 的 Telemetry 专用接口"

allowed_touch:
  - "D:\\ZephyrAlpha\\config\\flags.yaml"
  - "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\flags.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\flags.py"

applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "Pydantic V2"
  - module_id: "PS-STD-011"
    section: "MTH-013"
    reason: "路径合规创建"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\system-telemetry\\blueprint.md"
    reason: "§2e——8 个 FeatureFlag 定义/默认值/影响子系统 + AI 施工约定"
  - file_path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\flags.py"
    reason: "shared/flags.py FeatureFlag 三态机制——Telemetry 基于此构建"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
estimated_tokens: 5000
timeout_minutes: 20

acceptance_criteria:
  - "config/flags.yaml 包含全部 8 个 telemetry.* flags"
  - "Telemetry 各子系统可通过 telemetry.flags 查询 flag 状态"
  - "默认值：enable_ai_behavior_tracking=ON，其余 7 个=OFF"
  - "AI 施工约定已编码为运行时检查（禁止 AI 修改 FlagState）"

rollback_instructions: |
  1. 从 config/flags.yaml 中移除 telemetry.* 段
  2. 删除 D:\ZephyrAlpha\src\zephyr\l12_system_telemetry\flags.py

depends_on:
  - "TASK-INF-0001"
blocked_by: []
status: "created"

tags_fn:
  - "observability"
  - "infra"
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

# TASK-INF-0004: 实现 Telemetry FeatureFlag 控制矩阵

## 目标
基于 shared/flags.py 实现 Telemetry 专属 8 个特性开关，确保所有实验性/资源敏感功能被 FeatureFlag 守护，AI 新增功能初始 OFF。

## 触发条件
- TASK-INF-0001 通过
- shared/flags.py 可用

## 执行步骤

### 读
- 蓝图 §2e：8 个 Flag Key、默认值、影响子系统、AI 施工约定
- shared/flags.py：FeatureFlag 三态 API

### 做
1. 在 config/flags.yaml 中注册 8 个 telemetry.* flags
2. 创建 telemetry/flags.py，封装 shared/flags 为 Telemetry 专用接口
3. 实现 AI 施工约定运行时检查

### 产
- config/flags.yaml（修改）+ telemetry/flags.py

### 检
```bash
python -c "from zephyr.l12_system_telemetry.flags import TelemetryFlags; tf = TelemetryFlags(); print(tf.is_enabled('telemetry.enable_ai_behavior_tracking'))"
```

## 验收标准
| # | 指标 | 目标 |
|---|------|------|
| 1 | files | 8 个 flags 在 config/flags.yaml 中定义 |
| 2 | build | telemetry/flags.py 可 import |
