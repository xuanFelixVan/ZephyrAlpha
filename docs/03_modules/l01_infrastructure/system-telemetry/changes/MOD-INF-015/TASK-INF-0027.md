---
task_id: "TASK-INF-0027"
source_blueprint: "MOD-INF-015"
source_section: "蓝图 §16 已实现代码路径索�?+ §17 输出文件目录 + §18 集成目标 + §19 需要更新的相关文件"

title: "实现 Telemetry 路径索引维护 + 输出目录创建 + 集成目标落地 + 关联文件更新"
description: |
  1. §16 代码路径索引维护�?     - 将每个新创建�?.py 文件注册�?§16.1-16.4（metrics/logs/traces/ai_behavior 四层 + 根包索引�?     - 标记每个文件的状态（待创�?已实�?已验�?需修复/蓝图不一致）
  2. §17 输出文件目录创建�?     - data/telemetry/(dev|staging|prod)/metrics/
     - data/telemetry/(dev|staging|prod)/logs/
     - data/telemetry/(dev|staging|prod)/traces/
     - data/telemetry/(dev|staging|prod)/ai_behavior/
     - data/telemetry/(dev|staging|prod)/archive/
     - data/telemetry/(dev|staging|prod)/profiles/pprof
     - data/telemetry/(dev|staging|prod)/dlq/
     - data/telemetry/(dev|staging|prod)/meta/
     - data/dashboards/
     - ADR 记录（construction_progress.md/ai_autonomy_checklist.md�?  3. §18 集成目标对接�?     - 主控 launcher.py（l01�?     - ModuleManager（l01�?     - shared/lifecycle（l00�?     - shared/logging（l00�?     - shared/flags（l00�?     - shared/contracts/telemetry_emitter（l00�?  4. §19 需要更新的文件�?     - docs/00_project_profile/field_definitions.yaml——MetricPoint/Span/Log/AIBehaviorEvent 字段声明
     - docs/00_project_profile/interface_registry.yaml——CTR-P1-013/CTR-TRACE-001/CTR-BP-001/002/003
     - config/flags.yaml——telemetry.* 8 flags
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\system-telemetry\\blueprint.md"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\data\\telemetry\\dev\\metrics\\"
    description: "dev metrics 输出目录"
  - path: "D:\\ZephyrAlpha\\data\\telemetry\\staging\\metrics\\"
    description: "staging 输出目录"
  - path: "D:\\ZephyrAlpha\\data\\telemetry\\prod\\metrics\\"
    description: "prod 输出目录"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\path_index.py"
    description: "自动化路径索引——�?6 代码路径索引的自动化维护脚本"

allowed_touch:
  - "D:\\ZephyrAlpha\\data\\telemetry\\**"
  - "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\path_index.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\**\\*.py"

applicable_rules:
  - module_id: "PS-STD-011"
    section: "MTH-013"
    reason: "路径合规"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\system-telemetry\\blueprint.md"
    reason: "§16—�? 层代码路径索�?+ 根包索引�?+ §17—�?1 项输出目录清�?+ §18—�? 集成目标 + §19—�? 需更新文件"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
estimated_tokens: 6000
timeout_minutes: 25

acceptance_criteria:
  - "all 9 data/telemetry/{env}/* 子目录已创建"
  - "path_index.py 可自动扫描并对比 §16 清单"
  - "§18 全部 6 个集成目标均已对接验�?
  - "§19 全部 3 个需更新文件已更�?

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\data\telemetry\ 下本次新建的空子目录
  2. 删除 D:\ZephyrAlpha\src\zephyr\l12_system_telemetry\path_index.py
  3. 还原 §19 修改的文件（git checkout�?
depends_on:
  - "TASK-INF-0001"
  - "TASK-INF-0003"
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

# TASK-INF-0027: 路径索引 + 输出目录 + 集成 + 文件更新

## 目标
维护 §16 代码路径索引、创�?§17 输出目录、对�?§18 集成目标、更�?§19 关联文件�?
## 执行步骤

### �?- 蓝图 §16-§19：路径索引表 + 输出目录清单 + 集成目标 + 需更新文件

### �?1. 创建全部 data/telemetry/{env}/* 子目�?2. 实现 path_index.py 自动化扫�?3. 验证 6 个集成目�?4. 更新 3 个关联文�?
### 检
```python
from zephyr.l12_system_telemetry.path_index import PathIndexer
```

## 验收标准
| # | 指标 | 目标 |
|---|------|------|
| 1 | dirs | all output dirs created |
| 2 | index | automation working |
| 3 | integration | 6 targets verified |
| 4 | updates | 3 files updated |
