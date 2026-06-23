---
doc_type: domain_architecture_doc
title: D-TRADING 交易运营架构文档
version: "1.0"
status: active
date: 2026-06-23
owner: auto-generator
ttl: permanent
---

# D-TRADING 交易运营架构文档

> 本文档由 generate_domain_doc.py 从 depgraph.db 自动生成
> 最后更新: 2026-06-23 13:28:28
> 数据源: depgraph.db nodes表 + edges表

## 域概览

| 属性 | 值 |
|------|-----|
| 域ID | D-TRADING |
| 域名称 | 交易运营 |
| 架构层 | L2_domain |
| 模块总数 | 249 |
| 设计态模块 | 89 |
| 原型态模块 | 138 |
| 生产态模块 | 16 |
| 容量 | 16/150 (正常) |
| 描述 | 交易会话、交易接口、交易日志、交易复盘。交易运营中枢。合规检查由D-GOV-ENFORCEMENT门禁层执行。 |

## 模块清单

共 249 个模块（按路径排序，最多显示前 200 个）

| 模块路径 | 蓝图ID | 构建状态 | 设计成熟度 | 入度 | 出度 |
|---------|--------|---------|-----------|:---:|:---:|
| D-TRADING/7 Architecture Decisions 架构决策7项 |  | design_only | design | 0 | 0 |
| D-TRADING/A-Share Pre-Market Standardized Workflow A股盘前标准化工作流 |  | design_only | design | 0 | 0 |
| D-TRADING/Annual Statistics 年度统计 |  | design_only | design | 0 | 0 |
| D-TRADING/Approval Flow 审批流 |  | design_only | design | 0 | 0 |
| D-TRADING/Approval Token Verification 审批令牌验证 |  | design_only | design | 0 | 0 |
| D-TRADING/Autonomy Core Dependency Edge 自治核心依赖边 |  | design_only | design | 0 | 0 |
| D-TRADING/Cash Flow Manager 现金流管理器 |  | design_only | design | 0 | 0 |
| D-TRADING/Cash Management 资金与现金管理 |  | design_only | design | 0 | 0 |
| D-TRADING/Chase High Prevention 踏空追高防范 |  | design_only | design | 0 | 0 |
| D-TRADING/Closed Loop Optimization 15 Dimensions 闭环优化15维度 |  | design_only | design | 0 | 0 |
| D-TRADING/Config Signature Verification 配置签名验证 |  | design_only | design | 0 | 0 |
| D-TRADING/CorporateActionAdjusted 公司行为调整 |  | design_only | design | 0 | 0 |
| D-TRADING/Cross Layer Runtime Architecture 横切层运行时架构 |  | design_only | design | 0 | 0 |
| D-TRADING/D-TRADING |  | design_only | design | 0 | 0 |
| D-TRADING/DORA ICT Event Report DORA ICT事件报告 |  | design_only | design | 0 | 0 |
| D-TRADING/Data Degradation Processing 数据降级处理 |  | design_only | design | 0 | 0 |
| D-TRADING/Data Signature Verification 数据签名验证 |  | design_only | design | 0 | 0 |
| D-TRADING/Deterministic Validation 确定性校验 |  | design_only | design | 0 | 0 |
| D-TRADING/EOD Processor日终处理器 |  | design_only | design | 0 | 0 |
| D-TRADING/End-of-Day Processor 日终处理器 |  | design_only | design | 0 | 0 |
| D-TRADING/Execution Core Dependency Edge 执行核心依赖边 |  | design_only | design | 0 | 0 |
| D-TRADING/Fee PnL Data 费率PnL数据 |  | design_only | design | 0 | 0 |
| D-TRADING/GOV-TRD-001 单票持仓集中度规则 |  | design_only | design | 0 | 0 |
| D-TRADING/Gift Declaration Form Engine 礼品申报表引擎 |  | design_only | design | 0 | 0 |
| D-TRADING/Global State Aggregator 全局状态聚合器 |  | design_only | design | 0 | 0 |
| D-TRADING/Hard Boundary Constraints 硬边界约束 |  | design_only | design | 0 | 0 |
| D-TRADING/Infra Runtime Dependency Edge 基础设施运行时依赖边 |  | design_only | design | 0 | 0 |
| D-TRADING/Intraday Instant Reaction Decision Engine 盘中即时反应决策引擎 |  | design_only | design | 0 | 0 |
| D-TRADING/Intraday PnL Monitor 日内盈亏监控 |  | design_only | design | 0 | 0 |
| D-TRADING/Intraday Trading Agent 日内交易代理 |  | design_only | design | 0 | 0 |
| D-TRADING/L0 L1 L2 Data Flow Artery L0→L1→L2数据流主动脉 |  | design_only | design | 0 | 0 |
| D-TRADING/L2数据流主动脉 |  | design_only | design | 0 | 0 |
| D-TRADING/LP-020 Trading Operations Domain Substitute 交易运营域替代 |  | design_only | design | 0 | 0 |
| D-TRADING/Log Signature 日志签名 |  | design_only | design | 0 | 0 |
| D-TRADING/Loss Revenge Prevention 亏损报复防范 |  | design_only | design | 0 | 0 |
| D-TRADING/Margin Calculator保证金计算器 |  | design_only | design | 0 | 0 |
| D-TRADING/MarginAccount 保证金账户 |  | design_only | design | 0 | 0 |
| D-TRADING/MarginUnavailable 保证金不可用 |  | design_only | design | 0 | 0 |
| D-TRADING/MarginWarning 保证金预警 |  | design_only | design | 0 | 0 |
| D-TRADING/Market Data 行情数据 |  | design_only | design | 0 | 0 |
| D-TRADING/MultiAccountAllocated 多账户分配完成 |  | design_only | design | 0 | 0 |
| D-TRADING/Order Status 订单状态 |  | design_only | design | 0 | 0 |
| D-TRADING/Portfolio Core Dependency Edge 组合核心依赖边 |  | design_only | design | 0 | 0 |
| D-TRADING/Position Accountant持仓会计 |  | design_only | design | 0 | 0 |
| D-TRADING/Position Accounting 持仓会计 |  | design_only | design | 0 | 0 |
| D-TRADING/Position Data 持仓数据 |  | design_only | design | 0 | 0 |
| D-TRADING/Post-Market Review 盘后复盘 |  | design_only | design | 0 | 0 |
| D-TRADING/Pre-Market Checker盘前检查器 |  | design_only | design | 0 | 0 |
| D-TRADING/Pre-Market Review 盘前复核 |  | design_only | design | 0 | 0 |
| D-TRADING/Process-Level Isolation 进程级隔离 |  | design_only | design | 0 | 0 |
| D-TRADING/Profit Pride Warning 盈利骄傲警告 |  | design_only | design | 0 | 0 |
| D-TRADING/Reconciliation Engine对账引擎 |  | design_only | design | 0 | 0 |
| D-TRADING/ReconciliationCompleted 对账完成 |  | design_only | design | 0 | 0 |
| D-TRADING/Reference Data Manager 参考数据管理 |  | design_only | design | 0 | 0 |
| D-TRADING/Reporting Dependency Edge 报告域依赖边 |  | design_only | design | 0 | 0 |
| D-TRADING/Risk Dependency Edge 风控依赖边 |  | design_only | design | 0 | 0 |
| D-TRADING/Settlement Manager结算管理器 |  | design_only | design | 0 | 0 |
| D-TRADING/Settlement Reconciliation 结算与对账 |  | design_only | design | 0 | 0 |
| D-TRADING/SettlementCompleted 结算完成 |  | design_only | design | 0 | 0 |
| D-TRADING/SettlementRecord 结算记录 |  | design_only | design | 0 | 0 |
| D-TRADING/Signature Chain 签名链 |  | design_only | design | 0 | 0 |
| D-TRADING/Strategy Capacity Academic Framework 策略容量学术框架 |  | design_only | design | 0 | 0 |
| D-TRADING/Strategy Parameters 策略参数 |  | design_only | design | 0 | 0 |
| D-TRADING/Trader 交易员角色 |  | design_only | design | 0 | 0 |
| D-TRADING/Trading Calendar Engine交易日历引擎 |  | design_only | design | 0 | 0 |
| D-TRADING/Trading Cost Analyzer交易成本分析 |  | design_only | design | 0 | 0 |
| D-TRADING/Trading Operations Data 交易运营数据 |  | design_only | design | 0 | 0 |
| D-TRADING/Trading Operations Domain 交易运营域 |  | design_only | design | 0 | 0 |
| D-TRADING/Trading Order 交易指令 |  | design_only | design | 0 | 0 |
| D-TRADING/TradingOrder 交易订单 |  | design_only | design | 0 | 0 |
| D-TRADING/Trapped Position Adding Prevention 被套补仓防范 |  | design_only | design | 0 | 0 |
| D-TRADING/Treasury Manager 资金管理器 |  | design_only | design | 0 | 0 |
| D-TRADING/WeChat Interaction Hub 微信交互中心 |  | design_only | design | 0 | 0 |
| D-TRADING/miniQMT Connection Credential miniQMT连接凭证 |  | design_only | design | 0 | 0 |
| D-TRADING/不做高频交易 No High-Frequency Trading |  | design_only | design | 0 | 0 |
| D-TRADING/交易决策约束 Trading Decision Constraints |  | design_only | design | 0 | 0 |
| D-TRADING/交易决策防漂移契约 Contract |  | design_only | design | 0 | 0 |
| D-TRADING/交易域规则目录 Trading Domain Rule Catalog |  | design_only | design | 0 | 0 |
| D-TRADING/交易执行流程 Execution Workflow |  | design_only | design | 0 | 0 |
| D-TRADING/交易运营 Trading Operations |  | design_only | design | 0 | 0 |
| D-TRADING/延迟归因器 Latency Attributor |  | design_only | design | 0 | 0 |
| D-TRADING/延迟预算分配器 Latency Budget Allocator |  | design_only | design | 0 | 0 |
| D-TRADING/架构决策引用 Architecture Decision Reference |  | design_only | design | 0 | 0 |
| D-TRADING/禁止AI自主执行大额下单 No AI Auto-Execute Large Order |  | design_only | design | 0 | 0 |
| D-TRADING/禁止非交易时段提交订单 Order |  | design_only | design | 0 | 0 |
| D-TRADING/纳秒级关键路径分析器 Nanosecond Critical Path Analyzer |  | design_only | design | 0 | 0 |
| src/zephyr/trading/__init__.py | MOD-TRADING | draft | production | 200 | 0 |
| src/zephyr/trading/__init___from_orches.py | MOD-INF-035 | draft | prototype | 0 | 1 |
| src/zephyr/trading/__main__.py | MOD-INF-035 | draft | prototype | 0 | 1 |
| src/zephyr/trading/_extensions/__init__.py | MOD-TRADING | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/trading/action_dispatcher.py | MOD-INF-035 | draft | prototype | 0 | 1 |
| src/zephyr/trading/admission_controller.py | MOD-INF-033 | draft | prototype | 0 | 1 |
| src/zephyr/trading/ai_audit_logger.py | MOD-INF-035 | draft | prototype | 0 | 1 |
| src/zephyr/trading/api/__init__.py | MOD-TRADING | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/trading/auto_dispatcher.py | MOD-INF-039 | draft | prototype | 0 | 3 |
| src/zephyr/trading/auto_integrator.py | MOD-INF-035 | draft | prototype | 0 | 1 |
| src/zephyr/trading/auto_runtime_core.py | MOD-INF-035 | draft | prototype | 0 | 17 |
| src/zephyr/trading/auto_task_generator.py | MOD-INF-035 | draft | prototype | 0 | 1 |
| src/zephyr/trading/autopilot.py | SRC-193 | draft | prototype | 0 | 3 |
| src/zephyr/trading/boot_cron_jobs.py | MOD-INF-035 | draft | prototype | 0 | 7 |
| src/zephyr/trading/boot_hooks.py | MOD-INF-035 | draft | prototype | 0 | 9 |
| src/zephyr/trading/capability_card.py | MOD-INF-035 | draft | prototype | 0 | 1 |
| src/zephyr/trading/capability_registry.py | MOD-INF-035 | draft | prototype | 0 | 1 |
| src/zephyr/trading/capability_sync.py | MOD-INF-035 | draft | prototype | 0 | 1 |
| src/zephyr/trading/circadian_scheduler.py | MOD-INF-035 | draft | prototype | 0 | 14 |
| src/zephyr/trading/conductor.py | SRC-194 | draft | prototype | 0 | 4 |
| src/zephyr/trading/core/__init__.py | MOD-TRADING | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/trading/dream_cycle.py | MOD-INF-035 | draft | prototype | 0 | 1 |
| src/zephyr/trading/feedback_loop.py | MOD-INF-035 | draft | prototype | 0 | 1 |
| src/zephyr/trading/finalizer.py | MOD-INF-035 | draft | prototype | 0 | 1 |
| src/zephyr/trading/gpu_consensus_scheduler.py | MOD-INF-033 | draft | prototype | 0 | 1 |
| src/zephyr/trading/gpu_monitor.py | MOD-INF-032 | draft | prototype | 0 | 1 |
| src/zephyr/trading/health_monitor.py | MOD-INF-035 | draft | prototype | 0 | 3 |
| src/zephyr/trading/ide_health_daemon.py | MOD-INF-032 | draft | prototype | 0 | 3 |
| src/zephyr/trading/infrastructure/__init__.py | MOD-TRADING | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/trading/integration_registry.py | MOD-INF-035 | draft | prototype | 0 | 1 |
| src/zephyr/trading/lifecycle_manager.py | MOD-INF-035 | draft | prototype | 0 | 11 |
| src/zephyr/trading/models/__init__.py | MOD-TRADING | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/trading/module_onboarding_scanner.py | MOD-INF-035 | draft | prototype | 0 | 1 |
| src/zephyr/trading/night_shift_queue.py | MOD-INF-035 | draft | prototype | 0 | 1 |
| src/zephyr/trading/orchestrator/__init__.py | MOD-INF-039 | draft | prototype | 43 | 1 |
| src/zephyr/trading/orchestrator/agent_health_monitor.py | MOD-INF-039 | draft | prototype | 0 | 3 |
| src/zephyr/trading/orchestrator/agent_orchestrator.py | MOD-INF-039 | draft | prototype | 0 | 6 |
| src/zephyr/trading/orchestrator/agent_quality.py | MOD-INF-039 | draft | prototype | 0 | 1 |
| src/zephyr/trading/orchestrator/alert_handler.py | MOD-MASTER-001 | draft | prototype | 0 | 8 |
| src/zephyr/trading/orchestrator/autonomy_guard.py | MOD-INF-039 | draft | prototype | 0 | 1 |
| src/zephyr/trading/orchestrator/backup_manager.py | MOD-INF-039 | draft | prototype | 0 | 1 |
| src/zephyr/trading/orchestrator/batch_orchestrator.py | MOD-INF-039 | draft | prototype | 0 | 3 |
| src/zephyr/trading/orchestrator/benchmark_runner.py | MOD-INF-039 | draft | prototype | 0 | 1 |
| src/zephyr/trading/orchestrator/blind_spot_closure.py | MOD-INF-039 | draft | prototype | 0 | 1 |
| src/zephyr/trading/orchestrator/blueprint_health.py | MOD-INF-039 | draft | prototype | 0 | 1 |
| src/zephyr/trading/orchestrator/blueprint_scorer.py | MOD-INF-039 | draft | prototype | 0 | 1 |
| src/zephyr/trading/orchestrator/bulkhead_manager.py | MOD-INF-039 | draft | prototype | 0 | 1 |
| src/zephyr/trading/orchestrator/canary_manager.py | MOD-INF-039 | draft | prototype | 0 | 1 |
| src/zephyr/trading/orchestrator/capacity_budget.py | MOD-INF-039 | draft | prototype | 0 | 1 |
| src/zephyr/trading/orchestrator/chaos_engine.py | MOD-INF-039 | draft | prototype | 0 | 1 |
| src/zephyr/trading/orchestrator/chaos_hooks.py | MOD-INF-039 | draft | prototype | 0 | 2 |
| src/zephyr/trading/orchestrator/config_manager.py | MOD-INF-039 | draft | prototype | 0 | 1 |
| src/zephyr/trading/orchestrator/construction_guide.py | MOD-INF-039 | draft | prototype | 0 | 1 |
| src/zephyr/trading/orchestrator/context_bridge.py | MOD-MASTER-001 | draft | prototype | 0 | 2 |
| src/zephyr/trading/orchestrator/contract_registry.py | MOD-INF-039 | draft | prototype | 0 | 1 |
| src/zephyr/trading/orchestrator/contract_router.py | MOD-INF-039 | draft | prototype | 0 | 1 |
| src/zephyr/trading/orchestrator/core/__init__.py | MOD-INF-002 | draft | prototype | 0 | 1 |
| src/zephyr/trading/orchestrator/core/agent_orchestrator.py | MOD-INF-002 | draft | prototype | 0 | 4 |
| src/zephyr/trading/orchestrator/core/task_queue.py | MOD-INF-002 | draft | prototype | 0 | 1 |
| src/zephyr/trading/orchestrator/core/trigger_router.py | MOD-INF-002 | draft | prototype | 1 | 2 |
| src/zephyr/trading/orchestrator/core/wave_generator.py | MOD-INF-002 | draft | prototype | 0 | 1 |
| src/zephyr/trading/orchestrator/data_lifecycle.py | MOD-INF-039 | draft | prototype | 0 | 1 |
| src/zephyr/trading/orchestrator/deferred_queue.py | MOD-INF-039 | draft | prototype | 0 | 1 |
| src/zephyr/trading/orchestrator/degrade_cascade.py | MOD-INF-039 | draft | prototype | 0 | 1 |
| src/zephyr/trading/orchestrator/dependency_lock.py | MOD-INF-039 | draft | prototype | 0 | 1 |
| src/zephyr/trading/orchestrator/design_decisions.py | MOD-INF-039 | draft | prototype | 0 | 1 |
| src/zephyr/trading/orchestrator/disk_guard.py | MOD-INF-039 | draft | prototype | 0 | 1 |
| src/zephyr/trading/orchestrator/dlq_manager.py | MOD-INF-039 | draft | prototype | 0 | 1 |
| src/zephyr/trading/orchestrator/failure_matcher.py | MOD-INF-039 | draft | prototype | 0 | 1 |
| src/zephyr/trading/orchestrator/fault_types.py | MOD-INF-039 | draft | prototype | 0 | 1 |
| src/zephyr/trading/orchestrator/feature_flag.py | MOD-INF-039 | draft | prototype | 0 | 1 |
| src/zephyr/trading/orchestrator/file_task_mapper.py | MOD-INF-039 | draft | prototype | 0 | 4 |
| src/zephyr/trading/orchestrator/finding_bridge.py | MOD-INF-039 | draft | prototype | 0 | 3 |
| src/zephyr/trading/orchestrator/hallucination_detector.py | MOD-INF-039 | draft | prototype | 0 | 2 |
| src/zephyr/trading/orchestrator/housekeeping.py | MOD-INF-039 | draft | prototype | 0 | 1 |
| src/zephyr/trading/orchestrator/incident_postmortem.py | MOD-INF-039 | draft | prototype | 0 | 1 |
| src/zephyr/trading/orchestrator/ke_quality.py | MOD-INF-039 | draft | prototype | 0 | 1 |
| src/zephyr/trading/orchestrator/knowledge_freshness.py | MOD-INF-039 | draft | prototype | 0 | 1 |
| src/zephyr/trading/orchestrator/lean_scanner.py | MOD-INF-039 | draft | prototype | 0 | 1 |
| src/zephyr/trading/orchestrator/memory_writer.py | MOD-MASTER-001 | draft | prototype | 0 | 2 |
| src/zephyr/trading/orchestrator/model_registry.py | MOD-INF-039 | draft | prototype | 0 | 1 |
| src/zephyr/trading/orchestrator/network_partition.py | MOD-INF-039 | draft | prototype | 0 | 1 |
| src/zephyr/trading/orchestrator/path_index.py | MOD-INF-039 | draft | prototype | 0 | 1 |
| src/zephyr/trading/orchestrator/phase_executor.py | MOD-INF-039 | draft | prototype | 0 | 1 |
| src/zephyr/trading/orchestrator/prompt_version.py | MOD-INF-039 | draft | prototype | 0 | 1 |
| src/zephyr/trading/orchestrator/reconciliation_loop.py | MOD-INF-039 | draft | prototype | 0 | 1 |
| src/zephyr/trading/orchestrator/resilience/__init__.py | MOD-INF-039 | draft | prototype | 0 | 2 |
| src/zephyr/trading/orchestrator/resilience/deferred_queue.py | MOD-INF-039 | draft | prototype | 1 | 1 |
| src/zephyr/trading/orchestrator/resilience/failure_matcher.py | MOD-INF-039 | draft | prototype | 1 | 1 |
| src/zephyr/trading/orchestrator/resilience/hallucination_detector.py | MOD-INF-039 | draft | prototype | 0 | 2 |
| src/zephyr/trading/orchestrator/resilience/rollback_manager.py | MOD-INF-039 | draft | prototype | 0 | 2 |
| src/zephyr/trading/orchestrator/risk_registry.py | MOD-INF-039 | draft | prototype | 0 | 1 |
| src/zephyr/trading/orchestrator/rollback_manager.py | MOD-INF-039 | draft | prototype | 0 | 2 |
| src/zephyr/trading/orchestrator/rolling_upgrade.py | MOD-INF-039 | draft | prototype | 0 | 1 |
| src/zephyr/trading/orchestrator/schema_migration.py | MOD-INF-039 | draft | prototype | 0 | 1 |
| src/zephyr/trading/orchestrator/script_runner.py | MOD-MASTER-001 | draft | prototype | 0 | 1 |
| src/zephyr/trading/orchestrator/session_conflict.py | MOD-INF-039 | draft | prototype | 0 | 1 |
| src/zephyr/trading/orchestrator/session_handoff.py | MOD-INF-039 | draft | prototype | 0 | 1 |
| src/zephyr/trading/orchestrator/session_manager.py | MOD-INF-039 | draft | prototype | 0 | 1 |
| src/zephyr/trading/orchestrator/stability_guard.py | MOD-INF-039 | draft | prototype | 0 | 1 |
| src/zephyr/trading/orchestrator/startup_sequencer.py | MOD-INF-039 | draft | prototype | 0 | 1 |
| src/zephyr/trading/orchestrator/state/__init__.py | MOD-INF-039 | draft | prototype | 0 | 1 |
| src/zephyr/trading/orchestrator/state/agent_health_monitor.py | MOD-INF-039 | draft | prototype | 0 | 3 |
| src/zephyr/trading/orchestrator/state/file_task_mapper.py | MOD-INF-039 | draft | prototype | 0 | 4 |
| src/zephyr/trading/orchestrator/state/session_manager.py | MOD-INF-039 | draft | prototype | 1 | 0 |
| src/zephyr/trading/orchestrator/state/state_synchronizer.py | MOD-INF-039 | draft | prototype | 0 | 4 |
| src/zephyr/trading/orchestrator/state_propagation.py | MOD-INF-039 | draft | prototype | 0 | 1 |
| src/zephyr/trading/orchestrator/state_synchronizer.py | MOD-INF-039 | draft | prototype | 0 | 4 |
| src/zephyr/trading/orchestrator/system_transfer.py | MOD-INF-039 | draft | prototype | 0 | 1 |
| src/zephyr/trading/orchestrator/task_queue.py | MOD-INF-039 | draft | prototype | 0 | 1 |
| src/zephyr/trading/orchestrator/teardown_manager.py | MOD-INF-039 | draft | prototype | 0 | 1 |
| src/zephyr/trading/orchestrator/trigger_router.py | MOD-INF-039 | draft | prototype | 0 | 3 |
| src/zephyr/trading/orchestrator/version_manifest.py | MOD-INF-039 | draft | prototype | 0 | 1 |
| src/zephyr/trading/orchestrator/wave_generator.py | MOD-INF-039 | draft | prototype | 0 | 1 |

> (仅显示前 200 个模块，共 249 个)

## 跨域依赖

### 本域依赖的其他域（出边）

| 目标域 | 依赖数 | 依赖类型 |
|--------|:---:|---------|
| D-INTEGRATION | 55 | import_depends |
| D-SHARED | 43 | contract,import_depends |
| D-GOVERNANCE | 36 | import_depends,runtime,contract |
| D-SECURITY | 12 | import_depends |
| D-INFRA_RUNTIME | 7 | import_depends,contract,event,data |
| D-GOV_AUDIT | 7 | import_depends |
| D-INTELLIGENCE | 6 | import_depends |
| D-GOV_RULE | 4 | import_depends,contract |
| D-EX_SOR | 4 | domain_dependency,event,config_depends,data |
| D-DATA_ENG | 4 | data,config_depends,contract |
| D-OPS | 3 | import_depends,runtime |
| D-AUTONOMY_CORE | 3 | import_depends |
| D-GOV_DRIFT | 2 | import_depends |
| D-BEHAVIORAL_AUDIT | 1 | import_depends |

### 依赖本域的其他域（入边）

| 源域 | 依赖数 | 依赖类型 |
|------|:---:|---------|
| D-GOVERNANCE | 248 | import_depends,test_depends,data,contract,event,config_depends |
| D-RISK | 30 | contract,import_depends,config_depends,event,data |
| D-SECURITY | 23 | import_depends,contract,config_depends,data,event |
| D-AUTONOMY_CORE | 17 | contract,event,data,config_depends |
| D-COMPLIANCE | 16 | event,data,contract,config_depends |
| D-SIGNAL_FUNDAMENTAL | 15 | import_depends |
| D-SIGNAL | 14 | import_depends,event,contract,config_depends,data |
| D-INFRA_OPS | 12 | data,contract,event |
| D-REPORTING | 11 | import_depends,event,contract |
| D-OPS | 10 | import_depends,contract,data,config_depends |
| D-INTEGRATION | 10 | import_depends,event,contract,data,config_depends |
| D-MKT_DATA | 8 | config_depends,contract,data |
| D-POSITION | 7 | domain_dependency,data,contract,event |
| D-EX_CORE | 7 | import_depends,contract,data |
| D-ML_TRAIN | 6 | contract,import_depends,event |
| D-FACTOR | 5 | contract,event,data |
| D-CROSS_ASSET | 5 | contract,import_depends |
| D-PF_CORE | 4 | import_depends,data,event,contract |
| D-PF_ALLOC | 4 | import_depends,contract,data |
| D-FRONTEND | 4 | event,config_depends,contract |
| D-INTELLIGENCE | 3 | import_depends,event |
| D-SIMULATION | 2 | data,event |
| D-ML_SERVE | 2 | contract,config_depends |
| D-KNOWLEDGE | 2 | contract,data |
| D-AUTONOMY_PERM | 2 | config_depends,contract |
| D-ALT_DATA | 2 | contract,event |
| D-GOV_AUDIT | 1 | import_depends |
| D-DATA_SEC | 1 | event |
| D-DATA_GOV | 1 | config_depends |

## 域内依赖图

详见 [d_trading_dependency.mmd](d_trading_dependency.mmd)
