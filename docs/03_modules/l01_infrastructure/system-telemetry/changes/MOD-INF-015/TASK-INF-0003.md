---
task_id: "TASK-INF-0003"
source_blueprint: "MOD-INF-015"
source_section: "蓝图 §2d 多环境隔离"

title: "实现多环境遥测数据隔离：dev/staging/prod 三级物理隔离与环境感知行为差异"
description: |
  实现多环境遥测隔离机制：
  1. 所有遥测数据 MUST 携带 environment 标签（dev/staging/prod）
  2. 数据目录按环境物理隔离：data/telemetry/{dev,staging,prod}/
  3. 各环境 TTL 差异化（14/30/90 天）
  4. 环境感知行为差异：profiling 开关、trace 采样率、日志级别、FLE 异常检测、告警通知
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\system-telemetry\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\logging.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\environment.py"
    description: "环境管理器：Environment 枚举 + 环境检测 + 行为差异决策表"
  - path: "D:\\ZephyrAlpha\\data\\telemetry\\dev\\"
    description: "dev 环境数据目录结构"
  - path: "D:\\ZephyrAlpha\\data\\telemetry\\staging\\"
    description: "staging 环境数据目录结构"
  - path: "D:\\ZephyrAlpha\\data\\telemetry\\prod\\"
    description: "prod 环境数据目录结构"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\environment.py"
  - "D:\\ZephyrAlpha\\data\\telemetry\\**"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\**\\*.py"

applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "Pydantic V2"
  - module_id: "PS-STD-011"
    section: "MTH-013"
    reason: "路径合规创建"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\system-telemetry\\blueprint.md"
    reason: "§2d——环境标签/路径隔离/行为差异表"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
estimated_tokens: 5000
timeout_minutes: 20

acceptance_criteria:
  - "Environment 枚举三值 dev/staging/prod 可用"
  - "data/telemetry/{dev,staging,prod}/ 三级目录已创建"
  - "环境感知行为差异决策表可查询（profiling/trace采样率/日志级别/FLE/告警）"
  - "环境标签自动注入到所有 MetricPoint/Log/Span"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\l12_system_telemetry\environment.py
  2. 删除 D:\ZephyrAlpha\data\telemetry\dev\ / staging\ / prod\ 目录（如仅含空目录）

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

# TASK-INF-0003: 实现多环境遥测数据隔离

## 目标
实现 dev/staging/prod 三级环境物理隔离，确保 dev 的低质量数据不污染 prod 告警，各环境有独立的 TTL 和行为差异策略。

## 触发条件
- TASK-INF-0001 通过
- shared/logging.py 可用

## 执行步骤

### 读
- 蓝图 §2d：环境标签定义、路径隔离结构、行为差异矩阵

### 做
1. 创建 `environment.py`：Environment 枚举（DEV/STAGING/PROD），环境检测函数，行为差异决策表
2. 创建三个环境的数据目录结构
3. 实现环境标签自动注入逻辑

### 产
- environment.py + 三个数据目录

### 检
```bash
python -c "from zephyr.l12_system_telemetry.environment import Environment; assert len(list(Environment)) == 3; print('OK')"
```

## 验收标准
| # | 指标 | 目标 |
|---|------|------|
| 1 | build | environment.py 可成功 import |
| 2 | files | 三级目录存在于 data/telemetry/ |
| 3 | lint | 0 errors |

## 风险与缓解
| 风险 | 缓解 |
|------|------|
| dev 数据流量远超预期 | 环境 TTL 差异化 + cost budget 降级策略 |
