---
task_id: "TASK-INF-0025"
source_blueprint: "MOD-INF-015"
source_section: "蓝图 §13 施工进度 + §15 施工指导手册"

title: "执行施工指导手册：§15.1-15.4 逐子系统详细施工步骤 + Phase 二期执行"
description: |
  将蓝图 §15 的施工指导手册落地实现：
  1. Phase 一期（当前）：metrics/logs/traces/ai_behavior 四个核心子系统 30天 warm-up
  2. Phase 二期：profiles/health/alerts/schema/archive 五个卫星子系统
  3. 各子系统按照 §15.1-§15.4 的 7 步流程实现：
     Step1-读蓝图 / Step2-数据模型 Pydantic / Step3-核心采集器 / Step4-存储flush / Step5-共享基础设施集成 /
     Step6-监控验证(Meta-metrics) / Step7-FeatureFlag 守护（非P0→OFF）
  4. 施工规范：Pydantic V2 / config 无硬编码 / UTF-8 / 全部 async 或 thread-safe / 自检 tool read type-checkverification
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\system-telemetry\\blueprint.md"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\construction.py"
    description: "施工进度追踪器——Phase 1/2 里程碑 + 子系统完成状态"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\construction.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\**\\*.py"

applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "Pydantic V2 强制——禁止 dataclass"
  - module_id: "PS-STD-011"
    section: "MTH-013"
    reason: "路径合规创建"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\system-telemetry\\blueprint.md"
    reason: "§13——Phase 1/2 里程碑 + §15——7 步施工流程 + 施工规范(7 条)"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
estimated_tokens: 6000
timeout_minutes: 25

acceptance_criteria:
  - "Phase 一期 4 子系统: metrics/logs/traces/ai_behavior 全部标记为 completed"
  - "Phase 二期 5 子系统: profiles/health/alerts/schema/archive 全部标记为 completed"
  - "每个子系统实现遵循 7 步施工流程"
  - "无 Pydantic dataclass / 无 config 硬编码 / 全部 UTF-8"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\l12_system_telemetry\construction.py

depends_on:
  - "TASK-INF-0012"
  - "TASK-INF-0015"
  - "TASK-INF-0016"
  - "TASK-INF-0018"
  - "TASK-INF-0019"
  - "TASK-INF-0020"
  - "TASK-INF-0021"
  - "TASK-INF-0022"
  - "TASK-INF-0023"
blocked_by: []
status: "created"

tags_fn:
  - "observability"
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

# TASK-INF-0025: 施工指导手册执行 + 进度追踪

## 目标
执行蓝图 §15 施工指导手册，实现两 Phase 九子系统全部落地，确保施工规范覆盖。

## 执行步骤

### 读
- 蓝图 §13 + §15：Phase 规划 + 7 步施工流程 + 6 施工规范

### 做
1. construction.py：Phase 里程碑 + 子系统状态追踪器
2. 按 7 步流程校验每个子系统实现完整性

### 产
- construction.py

### 检
```python
from zephyr.l12_system_telemetry.construction import ConstructionTracker
ct = ConstructionTracker()
assert ct.phase1_complete and ct.phase2_complete
```

## 验收标准
| # | 指标 | 目标 |
|---|------|------|
| 1 | phase1 | 4 subsystems complete |
| 2 | phase2 | 5 subsystems complete |
| 3 | compliance | 7-step flow adhered |
| 4 | rules | no dataclass/hardcode |
