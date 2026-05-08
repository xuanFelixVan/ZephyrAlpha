---
task_id: TASK-MOD-INF-001-0015
module_id: MOD-INF-001
title: "第三轮盲点审计关闭：盲点 #26 至 #38（§22 v2.4.0 补充——新增 M-31~M-35）"
doc_type: task_card
status: done
priority: P1
layer: L01
layer_name: infrastructure
functional_domain: observability
owner: ZephyrAlpha-Owner
assignee: AI-GLM-5.1
created_by: AI-GLM-5.1
created_at: 2026-05-07T03:03:00+08:00
valid_from: 2026-05-07
ttl: permanent
belongs_to: MOD-INF-001
dependencies:
  - TASK-MOD-INF-001-0005
  - TASK-MOD-INF-001-0007
  - TASK-MOD-INF-001-0010
  - TASK-MOD-INF-001-0014
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\capacity-assurance\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\capacity_assurance\\kill_switch.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\capacity_assurance\\disaster_recovery.py"
downstream_outputs:
  - "D:\\ZephyrAlpha\\src\\zephyr\\capacity_assurance\\modules\\startup_guard.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\capacity_assurance\\modules\\cold_start_estimator.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\capacity_assurance\\modules\\graceful_shutdown.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\capacity_assurance\\modules\\time_partitioned_slo.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\capacity_assurance\\modules\\observer_effect_compensator.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\capacity_assurance\\modules\\hawthorne_blind.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\capacity_assurance\\modules\\config_reload_semantic.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\capacity_assurance\\modules\\capacity_testing_harness.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\capacity_assurance\\modules\\dr_drill_scheduler.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\capacity_assurance\\modules\\winfs_defense.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\capacity_assurance\\modules\\cliff_detector.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\capacity_assurance\\modules\\sunk_cost_intervention.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\capacity_assurance\\modules\\multi_model_vendor_risk.py"
acceptance_criteria:
  - "#26 启动序列未保护窗口: StartupGuard（M-31）+ load_order.yaml + boot_SLO"
  - "#27 Day-0 冷启动: ColdStartEstimator（人工标注初始budget）"
  - "#28 优雅关机: GracefulShutdown（M-32, SIGTERM handler + 1750ms 快照）"
  - "#29 时间分区容量模式: TimePartitionedSLO（09:00-22:00/22:00-09:00）"
  - "#30 容量监控污染SLI: ObserverEffectCompensator（M-33, 观测开销扣除）"
  - "#31 AI霍桑效应: HawthorneBlind（监控数据与AI可见信息分离）"
  - "#32 配置热重载语义缺失: ConfigReloadSemantic"
  - "#33 容量装置不可测试: CapacityTestingHarness（test_live_kill_switch等）"
  - "#34 DR演练从未执行: DRDrillScheduler（Mock DR + 季度记分卡）"
  - "#35 Windows FS物理约束: WinFSDefense（MAX_PATH/句柄数/非法字符保护）"
  - "#36 容量悬崖: CliffDetector（M-34, 非线性退化+性能陡降阈值检测）"
  - "#37 沉没成本陷阱: SunkCostIntervention（M-35, 项目级AI任务干预）"
  - "#38 多模型厂商风险: MultiModelVendorRisk + 逃生策略"
rollback_instructions:
  - "13个模块独立部署，逐个删除不影响核心"
context_assembly_manifest:
  - source: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\capacity-assurance\\blueprint.md"
    sections: ["§22 第三轮盲点审计 #26-#38", "M-31~M-35 模块定义"]
    purpose: "提取 13 个 v2.4.0 盲点及对应代码骨架"
tags:
  - capacity-assurance
  - blind-spots
  - round-3
  - BS-026-to-BS-038
phase: phase_2_enhance
estimated_effort_minutes: 300
ai_autonomy: AI-Modifiable
governance_layer: GOV-P1
runtime_plane: RP-3
---

# 第三轮盲点审计关闭：盲点 #26 至 #38

## 1. 任务来源

从蓝图 §22 "第三轮盲点审计" 提取（13个盲点 #26-#38），对照 AWS Well-Architected Framework（Reliability Pillar REL-7/8/9）、Google SRE Workbook §20（Graceful Degradation）、Meta Production Engineering（Chaos Engineering）、NIST SP 800-53（IR-4）。蓝图定义 M-31~M-35 五个模块。

## 2. 盲点清单与关闭映射

| 盲点 | 蓝图原文标题 | 本质 | 关闭方式 |
|------|------------|------|---------|
| #26 | 启动序列中的未保护窗口 | capacity_assurance 是最后一个加载的模块 → systemd启动（t=0）其他模块不受保护5-15s | StartupGuard（M-31）：bootstrapping_start/end marker + boot_SLO "自启动起的SLO达标时间≤ 30s" |
| #27 | Day-0冷启动 | 新系统上线零历史数据 → 容量预测完全失效→ 切换为极端保守策略 | ColdStartEstimator：7天观察期期内budget=人工标注的初始值 × 0.5 |
| #28 | 优雅关机状态丢失 | ctrl+C杀进程 → SLI状态未保存 → 下一次启动SLO历史清零 | GracefulShutdown（M-32）：SIGTERM handler + state.json write（1750ms 保存 deadline） |
| #29 | 时间分区容量模式 | API延迟 p50=200ms(夜间)/p50=800ms(日间) → 按全天段统一SLI 掩盖业务时间 | TimePartitionedSLO：09:00-22:00（tight）/22:00-09:00（relaxed by 2×） |
| #30 | 容量监控污染SLI | 监控系统自身插入 5-15% CPU/RAM → 无法区分"监控消耗" vs "业务消耗" | ObserverEffectCompensator（M-33）：subtract observer_overhead from total |
| #31 | AI霍桑效应 | AI知道自己被监控 → 产生防御性代码（更多的assert/error_handler/try/except）→30%系统污染 | HawthorneBlind：监控数据与AI 可见信息分离（"现实" / "AI感知" 双轨数据源） |
| #32 | 配置热重载语义缺失 | start_policy.py 改了 from warm_start → cold_start → 前一个正在执行的任务并未终止 | ConfigReloadSemantic：延迟生效型 / 即时生效型双模式 |
| #33 | 容量装置不可测试 | Kill Switch→prod_only, Error Budget→time-dependent, 容量预测→需要30天数据 → 常规pytest无法覆盖 | CapacityTestingHarness：环境模拟器（fake_clock/BurnRate/故障驱动器）+专项覆盖率≥ 85% |
| #34 | DR演练从未执行 | DR 策略定义了但从未演练 → DR恢复 267秒是"理论值"而非"实测值" | DRDrillScheduler：Mock DR（每周） + 季度真实DR（3天 micro_launch） + DR记分卡 |
| #35 | Windows FS物理约束 | MAX_PATH 260chars切断db path → Ability path traverse 失败 | WinFSDefense：句柄数追踪/非法字符容器化路径/Magic Volume 限制 |
| #36 | 容量悬崖 | CPU 50%→70% latency 平滑上升→80% latency 呈指数崩溃 | CliffDetector（M-34）：3维（CPU/MEM/TOKEN）×二阶导数 × 斜率>1 → pre_empt 撤离 |
| #37 | 沉没成本陷阱 | task 执行至77% → 触发了 500$ token → 应中断但AI非理性坚持 | SunkCostIntervention（M-35）：项目级AI任务sunk_check + 大于sunk_limit强制intervene |
| #38 | 多模型厂商风险 | GLM+DeepSeek 均从单一认证token通道 → 一切换厂商会有5-8天申请等待 | MultiModelVendorRisk：alternate_provider（dual_provider:GLM/DeepSeek配置 × vendor_switch_time≤ 10min） |

## 3. 施工内容

### 3.1 #26: StartupGuard (M-31)

文件：`D:\ZephyrAlpha\src\\zephyr\\shared\\startup_guard.py`

实现 `StartupGuard` 类（蓝图 L2728-2814）：
- `load_order.yaml`：声明 capacity_assurance 应在其他27个模块之前加载
- `mark_bootstrapping_start()` / `mark_bootstrapping_end()`：启动完成标记
- `check_module_protection(module_id) -> bool`：启动过程中其他模块调用ca → 返回CODE_RED（暂停调用直到ca完成启动）
- boot_SLO: "自启动起 SLO 达标时间 ≤ 30s"，Burn Rate × 2 权重

### 3.2 #27: ColdStartEstimator

文件：`D:\ZephyrAlpha\src\\zephyr\\shared\\cold_start_estimator.py`

实现 `ColdStartEstimator` 类（蓝图 L2816-2865）：
- `is_cold_start() -> bool`：判断是否为冷启动（< 7天历史数据）
- initial_budget = `MIN(owner_manual_label × 0.5, 1000req/min)`
- 7天后自动退出观察期，切换为预算自动校准
- 蓝图 L2823-2860 算法完整实现

### 3.3 #28: GracefulShutdown (M-32)

文件：`D:\ZephyrAlpha\src\\zephyr\\shared\\graceful_shutdown.py`

实现 `GracefulShutdown` 类（蓝图 L2866-2935）：
- `register_signal_handlers()`：注册 SIGTERM/SIGINT
- `save_state_snapshot(path=".audit_cache/shutdown_state.json")`：1750ms deadline 内保存
- `restore_on_boot()`：启动时恢复上次状态
- 蓝图 L2880-2935 代码完整实现

### 3.4 #30: ObserverEffectCompensator (M-33)

文件：`D:\ZephyrAlpha\src\\zephyr\\shared\\observer_effect_compensator.py`

实现 `ObserverEffectCompensator` 类（蓝图 L3003-3050）：
- `estimate_observer_overhead() -> dict`：测量 OTel SDK + AlertManager + 所有模块的自我消耗
- `apply_compensation(raw_sli_data) -> dict`：从原始SLI数据中扣除观测开销
- 蓝图 L3017-3048 算法完整实现

### 3.5 #36: CliffDetector (M-34)

文件：`D:\ZephyrAlpha\src\\zephyr\\shared\\cliff_detector.py`

实现 `CliffDetector` 类（蓝图 L3347-3411）：
- 三维检测：CPU/MEM/TOKEN × 二阶导数（acceleration）
- `compute_cliff_proximity() -> float`：0→1 近悬崖度
- `pre_empt_evacuate()`：撤离 = 渐进降低 AI 吞吐量
- 蓝图 L3347-3411 算法完整实现

### 3.6 #37: SunkCostIntervention (M-35)

文件：`D:\ZephyrAlpha\src\\zephyr\\shared\\sunk_cost_intervention.py`

实现 `SunkCostIntervention` 类（蓝图 L3416-3467）：
- `check_sunk_limit(task: TaskContext) -> bool`：判断任务是否触发沉没成本门槛
- `intervene(task_id, reason) -> InterventionResult`：中止/暂停/降级
- 蓝图 L3428-3467 干预逻辑完整实现

### 3.7 #31: HawthorneBlind

文件：`D:\ZephyrAlpha\src\\zephyr\\shared\\hawthorne_blind.py`

实现 `HawthorneBlind` 类（蓝图 L3051-3110）：
- 双轨数据源架构：`reality_track`（真实度量，用于SLO评估）vs `ai_visible_track`（AI可访问的降采样净化版）
- `filter_visible_metrics(raw_data) -> dict`：剔除敏感监控信息

### 3.8 #32: ConfigReloadSemantic

文件：`D:\ZephyrAlpha\src\\zephyr\\shared\\config_reload_semantic.py`

实现 `ConfigReloadSemantic` 类（蓝图 L3114-3144）：
- 两种生效模式：`deferred_生效`（等待当前任务完成）/ `immediate_生效`（强制终止当前任务）
- `apply_config_change(config_path, mode) -> bool`

### 3.9 #33: CapacityTestingHarness

文件：`D:\ZephyrAlpha\src\\zephyr\\shared\\capacity_testing_harness.py`

实现 `CapacityTestingHarness` 类（蓝图 L3148-3242）：
- `FakeClock`：模拟时序依赖
- `BurnRateDriver`：可编程 Burn Rate 生成器
- `FaultInjector`：注入 SQLite 写锁、文件系统满、网络断连
- 专项测试最低覆盖率 85%
- 蓝图 L3219-3242 测试清单完整实现

### 3.10 #34: DRDrillScheduler

文件：`D:\ZephyrAlpha\src\\zephyr\\shared\\dr_drill_scheduler.py`

实现 `DRDrillScheduler` 类（蓝图 L3246-3306）：
- `schedule_weekly_mock_drill()`：模拟 DR（无实际数据损失）
- `schedule_quarterly_live_drill()`：3天 micro_launch 真实DR
- `generate_dr_scorecard() -> dict`：DR记分卡（RPO/RTO 实际值 vs 目标值）

### 3.11 #35: WinFSDefense

文件：`D:\ZephyrAlpha\src\\zephyr\\shared\\winfs_defense.py`

实现 `WinFSDefense` 类（蓝图 L3308-3345）：
- `validate_path_length(path, max_chars=255)`：路径截断检测
- `check_handle_count()`：句柄泄漏追踪
- `sanitize_filename(name)`：过滤 Windows 非法字符
- `check_volume_space(path)`：Magic Volume 磁盘空间监控

### 3.12 #29: TimePartitionedSLO

文件：`D:\ZephyrAlpha\src\\zephyr\\shared\\time_partitioned_slo.py`

实现 `TimePartitionedSLO` 类（蓝图 L2956-3000）：
- 两时段分隔：`09:00-22:00`（tight: latency_target × 1.0）/ `22:00-09:00`（relaxed: × 2.0）
- `get_current_partition() -> TimePartition`
- `evaluate_slo(metric_value, partition)`：分区评估

### 3.13 #38: MultiModelVendorRisk

文件：`D:\ZephyrAlpha\src\\zephyr\\shared\\multi_model_vendor_risk.py`

实现 `MultiModelVendorRisk` 类（蓝图 L3471-3514）：
- `register_alternate_provider(primary, alternate)`
- `check_vendor_health() -> VendorStatus`
- `execute_vendor_switch(to_provider) -> bool`：切换时间 ≤ 10min
- 逃生策略：dual_provider GLM/DeepSeek 配置

## 4. 验收标准

1. StartupGuard：其他模块在 ca 完成启动前调用 → CODE_RED 阻止
2. ColdStartEstimator：冷启动期 budget ≤ 1000req/min
3. GracefulShutdown：SIGTERM → state.json 写入 < 2s
4. CliffDetector：模拟 CPU 从 70%→85% 斜率 > 1 → 撤离触发
5. SunkCostIntervention：task 500$ 触发 $200 limit → 干预执行
6. DRDrillScheduler：季度记分卡有实测 RTO/RPO
7. CapacityTestingHarness：专项测试覆盖率 ≥ 85%
8. 13 个盲点全部关闭
