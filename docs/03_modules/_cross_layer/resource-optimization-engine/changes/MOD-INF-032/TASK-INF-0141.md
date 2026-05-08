---
task_id: "TASK-INF-0141"
module_id: "MOD-INF-032"
title: "资源优化引擎 Phase 3 —— 守护线程统一接入（6 个模块注册到 DaemonRegistry）"
doc_type: task_card
status: Backlog
version: "0.1.0"
priority: P1
created_by: "agent_decomposer"
created_date: "2026-05-08"
task_type: implementation
phase: scaffold
blueprint_section: "§11 Phase 3 + §7.1 守护线程注册表 + §14 降级矩阵"
estimated_tokens: 4000
estimated_time_minutes: 60
owner_signal_required: false
depends_on:
  - "TASK-INF-0139"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\resource-optimization-engine\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\lifecycle\\resource_optimization_engine.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\feedback_loop\\scheduler.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\drift_detector\\resource_guard.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\self_monitor.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\writer.py"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\feedback_loop\\scheduler.py"
    desc: "修改：注册 fle-scheduler 到 DaemonRegistry"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\drift_detector\\resource_guard.py"
    desc: "修改：注册 resource-guard 到 DaemonRegistry"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\self_monitor.py"
    desc: "修改：注册 self-monitor 到 DaemonRegistry"
acceptance_criteria:
  - "AC-01: FLE-Scheduler 在 start() 中调用 ResourceOptimizationEngine.register_daemon('fle-scheduler', start, stop, priority=5)"
  - "AC-02: ResourceGuard 在启动时注册，priority=3"
  - "AC-03: SelfMonitor 在 start_scheduler() 中注册，priority=5"
  - "AC-04: 所有守护线程通过 DaemonRegistry 注册后 status() 显示全部 RUNNING"
  - "AC-05: EMERGENCY 压力时 stop_low_priority(min_priority=5) 能按优先级停止守护线程"
  - "AC-06: 停止操作幂等——重复调用 stop() 不报错"
  - "AC-07: 恢复顺序：先启依赖方，再启被依赖方"
rollback_instructions: "恢复 6 个守护线程模块的原始启动逻辑，移除 register_daemon 调用"
context_assembly_manifest:
  primary:
    - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\resource-optimization-engine\\blueprint.md#L847-L867 (§11 Phase 3)"
    - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\resource-optimization-engine\\blueprint.md#L645-L680 (§7.1 守护线程注册表)"
  fallback:
    - "D:\\ZephyrAlpha\\src\\zephyr\\feedback_loop\\scheduler.py"
    - "D:\\ZephyrAlpha\\src\\zephyr\\drift_detector\\resource_guard.py"
assigned_agent: any
tags: [resource-optimization, daemon-registry, integration, scaffold]
---

# TASK-INF-0141: 资源优化引擎 Phase 3 — 守护线程统一接入

## 1. 任务目标

将 6 个守护线程模块统一接入 DaemonRegistry，实现从"各自轮询"到"统一调度"的架构转变。每个守护线程在启动时注册到 ResourceOptimizationEngine，由引擎统一管理启停和优先级。

## 2. 背景

蓝图 §11 Phase 3 定义了守护线程统一接入。当前各守护线程独立启动，无法统一查询/停止/监控。统一注册后，EMERGENCY 压力时可按优先级停止低优先级守护线程释放资源。

## 3. 实施步骤

### Step 1: 修改 scheduler.py
- 在 start() 方法中添加 register_daemon("fle-scheduler", self.start, self.stop, priority=5)

### Step 2: 修改 resource_guard.py
- 在 guard_loop() 启动时注册 register_daemon("resource-guard", start, stop, priority=3)

### Step 3: 修改 self_monitor.py
- 在 start_scheduler() 中注册 register_daemon("self-monitor", start, stop, priority=5)

### Step 4: 验证集成
- 启动所有守护线程后 status() 显示全部 RUNNING
- EMERGENCY 压力时 stop_low_priority 正确停止

## 4. 产出物清单

| # | 文件 | 状态 |
|---|------|:---:|
| 1 | `src/zephyr/feedback_loop/scheduler.py` | 修改 |
| 2 | `src/zephyr/drift_detector/resource_guard.py` | 修改 |
| 3 | `src/zephyr/audit_trail/self_monitor.py` | 修改 |

## 5. 验收标准

| # | 验收项 | 验证方法 |
|---|--------|---------|
| 1 | 所有守护线程注册到 DaemonRegistry | status() 检查 |
| 2 | EMERGENCY 时自动停止低优先级 | 模拟 EMERGENCY 压力 |
| 3 | 停止操作幂等 | 重复调用 stop() |
