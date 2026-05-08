---
task_id: "TASK-INF-0010"
source_blueprint: "MOD-INF-015"
source_section: "蓝图 §3d 配置热更新机制"

title: "实现 Telemetry 配置热更新：EventBus 驱动 + 各子系统 on_config_change 回调"
description: |
  基于 shared/flags.py 的文件监听 + shared/observer.EventBus 发布 CONFIG_CHANGE 事件，实现零重启热更新：
  1. 订阅 shared/observer.EventBus CONFIG_CHANGE 事件
  2. 各子系统实现 on_config_change(event) 回调：
     metrics: 采样率/rate limit/cardinality threshold
     logs: log_level_override
     traces: 采样策略参数
     profiles: 开关
     alerts: cost_alert_threshold_usd/burn rate 窗口
     archive: TTL/auto_cleanup
  3. 热更新支持矩阵（7 项 ✅ + 3 项例外）
  4. 失败保持当前配置不回退
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\system-telemetry\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\flags.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\observer.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\hot_reload.py"
    description: "热更新管理器——订阅 EventBus + 分发到各子系统 on_config_change 回调"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\hot_reload.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\flags.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\observer.py"

applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "Pydantic V2"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\system-telemetry\\blueprint.md"
    reason: "§3d——热更新订阅流程 + 支持矩阵（9 项）+ AI 施工约定（4 条）"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 5000
timeout_minutes: 20

acceptance_criteria:
  - "HotReloadManager 订阅 EventBus CONFIG_CHANGE 事件"
  - "config/flags.yaml 变更 → on_config_change 被触发"
  - "6 个子系统回调均已注册"
  - "热更新失败 → 保持当前配置 + 记录错误日志"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\l12_system_telemetry\hot_reload.py

depends_on:
  - "TASK-INF-0004"
  - "TASK-INF-0009"
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

# TASK-INF-0010: 实现 Telemetry 配置热更新

## 目标
实现零重启配置热更新，所有 Telemetry 配置参数变更即时生效，支持 7 项可热更新配置。

## 触发条件
- TASK-INF-0004（FeatureFlags）、TASK-INF-0009（门面类）通过

## 执行步骤

### 读
- 蓝图 §3d：订阅流程、支持矩阵、AI 施工约定

### 做
1. 创建 HotReloadManager：订阅 EventBus、分发到各子系统回调
2. 实现按子系统分类的配置更新逻辑

### 产
- hot_reload.py

### 检
```bash
python -c "from zephyr.l12_system_telemetry.hot_reload import HotReloadManager; print('OK')"
```

## 验收标准
| # | 指标 | 目标 |
|---|------|------|
| 1 | subscribe | CONFIG_CHANGE 事件可被订阅 |
| 2 | callback | 6 个子系统回调均已注册 |
| 3 | fail-safe | 更新失败保持当前配置 |
