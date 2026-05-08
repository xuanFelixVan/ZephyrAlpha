---
task_id: "TASK-INF-0111"
source_blueprint: "MOD-INF-006"
source_section: "蓝图 §4.1 约束 #31 + 盲点 #26/#27/#28/#29/#30/#40"

title: "实现架构完整性——M模块插件化 + 自诊断 + 蓝图-代码同步 + 降级运行"
description: |
  实现 M 模块插件化——通过 pipeline-module-registry.yaml 的 enabled_modules 字段精细控制启停（约束 #31）。
  任务系统自诊断——health_check() 检查 SQLite 连通性 / task_repo 版本 / 异常任务数。
  蓝图-代码同步校验——检查 blueprint.md 声明的源码路径与磁盘文件一致性。
  降级运行——task_repo 不可用时的降级行为（文件模式兜底）。
  突破门槛最小值——max_parallel ≥ 3 实现串行/并行混合调度。
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\models.py"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\governance\\pipeline\\pipeline-module-registry.yaml"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\healthcheck.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\core\\healthcheck.py"
    description: "HealthCheck——SQLite连通性 + task_repo版本 + 异常任务数"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\core\\sync\\blueprint_code_sync.py"
    description: "BlueprintCodeSync——蓝图声明 vs 磁盘一致性检查"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\healthcheck.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\sync\\blueprint_code_sync.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"

applicable_rules:
  - module_id: "MOD-INF-006"
    section: "§4.1 约束 #9(MTH-013)/#31"
    reason: "路径合规 + M模块插件化"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"
    reason: "§4.1 约束 #31 + 盲点 #26-#30"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 10000
timeout_minutes: 30

acceptance_criteria:
  - "health_check() 返回 SQLite状态/task_repo版本/异常任务数"
  - "蓝图-代码同步——漏声明/多余声明 输出 diff 报告"
  - "M模块控制——enabled_modules 可过滤 PipelineOrchestrator 执行"
  - "降级运行——task_repo 不可用时 notifier→退化为文件模式"

rollback_instructions: |
  1. 移除 healthcheck.py 和 blueprint_code_sync.py
  2. 移除 M模块过滤逻辑

depends_on: ["TASK-INF-0102"]
blocked_by: []

status: "created"

tags_fn:
  - "infra"
  - "architecture"
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

# 实现架构完整性

## 目标

1. M模块插件化——按 enabled_modules 动态启停
2. 自诊断——任务系统健康检查
3. 蓝图-代码同步——声明与实现一致性
4. 降级运行——不可用时的兜底策略
5. 突破门槛——max_parallel ≥ 3

## 触发条件

- TASK-INF-0102 完成

## 执行步骤

### 做
1. HealthCheck 实现
2. BlueprintCodeSync 实现
3. M 模块启停控制

### 产
- healthcheck.py + blueprint_code_sync.py

### 检
```bash
python -m zephyr.cli.task health
```

## 验收标准

| # | 指标 | 目标 |
|---|------|------|
| 1 | build | import 无错误 |
| 2 | test | 健康检查 / 同步检测 / 插件化 均有测试 |
| 3 | lint | 0 errors |
