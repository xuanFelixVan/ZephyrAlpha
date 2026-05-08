---
task_id: "TASK-INF-0143"
module_id: "MOD-INF-032"
title: "资源优化引擎 Phase 5 —— 自愈闭环 + 配置管理 + EventBus/Audit 集成"
doc_type: task_card
status: Backlog
version: "0.1.0"
priority: P1
created_by: "agent_decomposer"
created_date: "2026-05-08"
task_type: implementation
phase: scaffold
blueprint_section: "§11 Phase 5 + §15 全系统集成契约 + §17 自动化运维 + §18 配置管理"
estimated_tokens: 6000
estimated_time_minutes: 120
owner_signal_required: false
depends_on:
  - "TASK-INF-0139"
  - "TASK-INF-0140"
  - "TASK-INF-0141"
  - "TASK-INF-0142"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\resource-optimization-engine\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\lifecycle\\resource_optimization_engine.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\event_bus.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\writer.py"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\config\\resource_optimization.yaml"
    desc: "配置文件——压力阈值/调度频率/缓存参数/进程池参数/断路器参数/滞后参数"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\lifecycle\\resource_optimization_engine.py"
    desc: "修改：添加配置热加载 + 自愈闭环 + EventBus + Audit 集成"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\resource_optimization\\test_self_healing.py"
    desc: "自愈闭环单元测试"
acceptance_criteria:
  - "AC-01: resource_optimization.yaml 存在且所有参数有明确默认值"
  - "AC-02: 配置热加载——文件 mtime 变化后下一个监控周期生效，5 秒内"
  - "AC-03: 自愈闭环——检测→诊断→优化→验证 ≤60 秒"
  - "AC-04: 背压机制——优化速度跟不上恶化速度时触发 EMERGENCY"
  - "AC-05: EventBus 发布 resource.pressure.changed 事件（含 pressure_level + snapshot）"
  - "AC-06: 每个优化动作写入 Audit Trail（actor/strategy/pressure_before/after/memory_before/after/quality_preserved）"
  - "AC-07: 优化历史持久化到 SQLite（跨 session 保留）"
  - "AC-08: 蓝图施工状态更新——Phase 1-5 标记为 completed"
rollback_instructions: "删除 resource_optimization.yaml，移除 EventBus/Audit 集成代码和自愈逻辑，恢复引擎到 Phase 4 状态"
context_assembly_manifest:
  primary:
    - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\resource-optimization-engine\\blueprint.md#L900-L927 (§11 Phase 5)"
    - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\resource-optimization-engine\\blueprint.md#L1356-L1403 (§18 配置管理)"
    - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\resource-optimization-engine\\blueprint.md#L1300-L1340 (§17 自动化运维)"
  fallback:
    - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\event_bus.py"
    - "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\writer.py"
assigned_agent: any
tags: [resource-optimization, self-healing, config-management, eventbus, audit, scaffold]
---

# TASK-INF-0143: 资源优化引擎 Phase 5 — 自愈闭环 + 配置管理 + 集成

## 1. 任务目标

创建配置文件 `resource_optimization.yaml`，实现配置热加载、自愈闭环（检测→诊断→优化→验证 ≤60 秒）、背压机制、EventBus 事件发布、Audit Trail 审计记录、优化历史 SQLite 持久化。

## 2. 背景

蓝图 §11 Phase 5 是资源优化引擎的闭环阶段——从"被动优化"升级为"主动自愈"。配置管理让所有参数可调，EventBus/Audit 集成让优化动作可观测可追溯，自愈闭环让系统在无人干预下自动恢复。

## 3. 实施步骤

### Step 1: 创建 resource_optimization.yaml
- 压力阈值：memory_warning=75, memory_critical=85, memory_emergency=95
- 调度频率：normal=30s, warning=60s, critical=120s, emergency=暂停
- 缓存参数：max_entries=1000, ttl=300s
- 进程池参数：max_processes=30, zombie_check_interval=60s
- 断路器参数：failure_threshold=3, recovery_timeout=30s
- 滞后参数：hysteresis_percent=10, cooldown_seconds=60

### Step 2: 实现配置热加载
- 文件 mtime 监控：每 30 秒检查一次
- 变更检测：mtime 变化 → 重新加载配置
- 生效策略：下一个监控周期开始时使用新配置

### Step 3: 实现自愈闭环
- 检测：_monitor_loop() 发现压力异常
- 诊断：_classify_pressure() 确定级别
- 优化：optimize() 执行策略
- 验证：优化后再次 snapshot() 确认效果
- 失败回滚：验证失败 → 断路器计数 + 告警

### Step 4: EventBus 集成
- 发布 resource.pressure.changed 事件

### Step 5: Audit Trail 集成
- 每个优化动作写入审计记录

### Step 6: 优化历史 SQLite 持久化

### Step 7: 编写单元测试

## 4. 产出物清单

| # | 文件 | 状态 |
|---|------|:---:|
| 1 | `config/resource_optimization.yaml` | 新建 |
| 2 | `src/zephyr/shared/lifecycle/resource_optimization_engine.py` | 修改 |
| 3 | `tests/unit/resource_optimization/test_self_healing.py` | 新建 |

## 5. 验收标准

| # | 验收项 | 验证方法 |
|---|--------|---------|
| 1 | 配置文件存在且参数完整 | 检查所有字段 |
| 2 | 配置热加载 5 秒内生效 | 修改配置 → 观察生效 |
| 3 | 自愈闭环 ≤60 秒 | 模拟内存泄漏 |
| 4 | EventBus 事件发布 | 事件消费者验证 |
| 5 | 优化动作可审计 | Audit Trail 查询 |
