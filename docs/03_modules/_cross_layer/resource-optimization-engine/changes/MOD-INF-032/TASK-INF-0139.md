---
task_id: "TASK-INF-0139"
module_id: "MOD-INF-032"
title: "资源优化引擎 Phase 1 —— 统一调度引擎核心（MAPE-K 主循环 + 压力状态机 + 断路器）"
doc_type: task_card
status: Backlog
version: "0.1.0"
priority: P0
created_by: "agent_decomposer"
created_date: "2026-05-08"
task_type: implementation
phase: scaffold
blueprint_section: "§3 (接口契约) + §12 (MAPE-K) + §13 (压力状态机) + §3.2 (数据模型)"
estimated_tokens: 8000
estimated_time_minutes: 120
owner_signal_required: false
depends_on: []
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\resource-optimization-engine\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\lifecycle\\daemon_registry.py"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\lifecycle\\resource_optimization_engine.py"
    desc: "资源优化引擎主类——MAPE-K 循环 + 压力状态机 + 断路器 + 双策略引擎"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\resource_optimization\\test_engine.py"
    desc: "单元测试——快照采集 + 压力分级 + 状态机 + 断路器 + 策略执行"
acceptance_criteria:
  - "AC-01: ResourceOptimizationEngine 单例模式——全局唯一实例"
  - "AC-02: snapshot() 返回 ResourceSnapshot，包含 CPU/内存/磁盘/进程/线程 9 个指标，缺失字段降级为 0 而非 None"
  - "AC-03: _classify_pressure() 覆盖 NORMAL/WARNING/CRITICAL/EMERGENCY 四级，阈值与蓝图 §4 一致"
  - "AC-04: 压力状态机含滞后机制——升级需连续 2 次确认，降级需冷却 60 秒，1 小时抖动 >3 次自动加宽滞后区间"
  - "AC-05: 断路器 CLOSED/OPEN/HALF_OPEN 三态——3 次失败后熔断，30 秒后半开，半开时 1 次成功即恢复"
  - "AC-06: 防御策略引擎——EMERGENCY 时 stop_low_priority(min_priority=5)，CRITICAL 时 stop_low_priority(min_priority=2)"
  - "AC-07: 优化策略引擎——7 种 OptimizationStrategy 枚举，Phase 1 实现 SCHEDULE_ADAPT 和 MEMORY_COMPACT 骨架"
  - "AC-08: optimize() 统一调度——断路器检查 → 策略执行 → 结果记录 → 知识层更新"
  - "AC-09: health_check() 返回引擎运行状态 + 监控循环存活 + 各子系统健康"
  - "AC-10: _monitor_loop() 30 秒循环可启停，CPU 开销 < 1%"
  - "AC-11: 所有 Pydantic V2 数据模型——ResourceSnapshot/OptimizationRecord/OptimizationResult/PressureState/HealthCheckResult"
  - "AC-12: 现有 DaemonRegistry 不被破坏——新引擎包装而非替换"
rollback_instructions: "删除 resource_optimization_engine.py 和 test_engine.py。DaemonRegistry 保持不变，系统回退到原有监控逻辑"
context_assembly_manifest:
  primary:
    - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\resource-optimization-engine\\blueprint.md#L291-L555 (§3 接口契约)"
    - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\resource-optimization-engine\\blueprint.md#L999-L1050 (§12 MAPE-K 详细设计)"
    - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\resource-optimization-engine\\blueprint.md#L1051-L1100 (§13 压力状态机)"
  fallback:
    - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\lifecycle\\daemon_registry.py"
assigned_agent: any
tags: [resource-optimization, mape-k, pressure-state-machine, circuit-breaker, core-engine, scaffold]
---

# TASK-INF-0139: 资源优化引擎 Phase 1 — 统一调度引擎核心

## 1. 任务目标

创建 `ResourceOptimizationEngine` 核心类——MAPE-K 循环驱动的资源监控、分析、优化与自愈系统主引擎。包含压力状态机（滞后+冷却）、断路器模式、双策略引擎（防御+优化）、Pydantic V2 数据模型。在现有 `DaemonRegistry` 基础上包装升级，不破坏已有功能。

## 2. 背景

蓝图 §11 Phase 1 定义了统一调度引擎——从各自轮询到统一调度的架构转变。现有 `daemon_registry.py` 已实现基础监控（snapshot_resources + _classify_pressure + _monitor_loop + stop_low_priority），但缺少：磁盘 I/O 指标、压力状态机滞后机制、断路器、优化策略引擎、Pydantic 数据模型、health_check。本任务在 `daemon_registry.py` 之上创建新文件 `resource_optimization_engine.py`，包装并增强现有功能。

## 3. 实施步骤

### Step 1: 创建 Pydantic V2 数据模型
- PressureLevel(str, Enum): normal/warning/critical/emergency
- OptimizationStrategy(str, Enum): 7 种策略
- DefensiveStrategy(str, Enum): 4 种防御策略
- CircuitBreakerState(str, Enum): closed/open/half_open
- ResourceSnapshot(BaseModel): 9 个指标 + pressure 字段
- OptimizationRecord(BaseModel): 优化动作完整记录
- OptimizationResult(BaseModel): 优化执行结果
- PressureState(BaseModel): 状态机当前状态
- HealthCheckResult(BaseModel): 健康检查结果
- CacheStats/ProcessPoolStats/DegradationMatrix: 占位模型

### Step 2: 实现 ResourceOptimizationEngine 单例
- `__new__` 单例模式
- 构造函数初始化：压力状态机、断路器、策略注册表、回调列表
- 包装 DaemonRegistry 的 register/start/stop 方法

### Step 3: 实现 snapshot() 增强版
- 复用 DaemonRegistry.snapshot_resources() 的 CPU/内存/进程指标
- 新增磁盘 I/O 指标（disk_io_read_mb_s, disk_io_write_mb_s, disk_free_gb）
- 返回 Pydantic ResourceSnapshot

### Step 4: 实现压力状态机
- _classify_pressure(): 四级分级（复用 DaemonRegistry 逻辑 + 新增 CPU EMERGENCY 阈值）
- _transition_pressure(): 升级需连续 confirmation_count=2 次确认
- 冷却期：降级后 60 秒内不再次降级
- 防抖动：1 小时内转换 >3 次自动加宽滞后区间

### Step 5: 实现断路器
- CircuitBreaker 类：failure_threshold=3, recovery_timeout=30s, half_open_max_calls=1
- optimize() 前检查断路器状态
- 策略执行失败 → 断路器计数 +1
- 半开状态 → 允许 1 次试探调用

### Step 6: 实现双策略引擎
- 防御引擎：EMERGENCY → stop_low_priority(5) + emergency_gc; CRITICAL → stop_low_priority(2) + reduce_frequency
- 优化引擎：7 种策略骨架，Phase 1 实现 SCHEDULE_ADAPT 和 MEMORY_COMPACT
- optimize() 统一调度：断路器检查 → 策略执行 → 结果记录

### Step 7: 实现 health_check() 和 get_pressure_state()

### Step 8: 实现 _monitor_loop() 增强版
- 复用 DaemonRegistry 的监控线程逻辑
- 新增：压力状态机转换、断路器状态更新、on_pressure 回调触发

### Step 9: 编写单元测试
- test_snapshot: 验证 9 个指标采集（mock psutil）
- test_pressure_classification: 四级分级 + 阈值边界
- test_pressure_state_machine: 升级确认 + 冷却期 + 防抖动
- test_circuit_breaker: 三态转换 + 熔断 + 半开恢复
- test_defensive_strategy: EMERGENCY/CRITICAL 停止策略
- test_optimize: 策略执行 + 结果记录
- test_health_check: 各状态组合

## 4. 产出物清单

| # | 文件 | 状态 |
|---|------|:---:|
| 1 | `src/zephyr/shared/lifecycle/resource_optimization_engine.py` | 新建 |
| 2 | `tests/unit/resource_optimization/test_engine.py` | 新建 |

## 5. 验收标准

| # | 验收项 | 验证方法 |
|---|--------|---------|
| 1 | snapshot() 返回 9 个指标 | 运行测试，所有字段非 None |
| 2 | 压力分级覆盖 4 级 | 边界值测试 |
| 3 | 状态机滞后机制 | 连续 2 次确认才升级 |
| 4 | 断路器三态转换 | 3 次失败熔断 + 30s 半开 |
| 5 | 监控循环 CPU < 1% | 运行 5 分钟观察 |
| 6 | DaemonRegistry 不被破坏 | 原有测试仍通过 |
