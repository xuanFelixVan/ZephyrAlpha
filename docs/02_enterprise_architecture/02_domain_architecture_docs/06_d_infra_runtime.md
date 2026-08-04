---
doc_type: architecture_view
title: D_INFRA_RUNTIME 运行时集成架构文档
version: "1.0"
status: active
date: 2026-08-04
owner: auto-generator
ttl: permanent
---

# 06_d_infra_runtime / 运行时集成域 / Runtime Integration

> **功能简介 / Overview**: 运行时集成，负责组件生命周期编排、启动钩子和运行时上下文管理

> **文档作用 / Purpose**: 展示 运行时集成（D_INFRA_RUNTIME）功能域的域内依赖关系、跨域依赖关系，模块信息（成熟度/中英文名/大白话/文件路径）内嵌于 Mermaid 节点，供架构审查和域治理参考。

> 本文档由 generate_domain_doc.py 从 depgraph (PostgreSQL) 自动生成
> 数据源: depgraph (PostgreSQL) nodes表 + edges表

> **[可缩放 HTML 版 / Zoomable HTML](http://localhost:8765/docs/02_enterprise_architecture/02_domain_architecture_docs/_zoomable_html/06_d_infra_runtime.html)** — Ctrl+滚轮缩放 ｜ 双击重置 ｜ Ctrl+Shift+D 切换拖动/选择模式

## 域基本信息 / Domain Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 编号 | 06 | Number | 06 |
| 域ID | D_INFRA_RUNTIME | Domain ID | D_INFRA_RUNTIME |
| 域名称 | 运行时集成 | Domain Name | Runtime Integration |
| 层级 | L0 基础设施层 | Layer | L0 Infrastructure |
| 模块数 | 172 | Module Count | 172 |
| 域内依赖 | 160 | Internal Dependencies | 160 |
| 跨域入边 | 85 | Cross-domain Incoming | 85 |
| 跨域出边 | 231 | Cross-domain Outgoing | 231 |
| 设计态模块 | 1 | Design Modules | 1 |
| 生产态模块 | 171 | Production Modules | 171 |
| 容量 | 171/150 (超容) | Capacity | 171/150 (超容) |
| 描述 | 三层运行时编排(L1 Trae/L2 Local/L3 API) | Description | 三层运行时编排(L1 Trae/L2 Local/L3 API) |

## 域内依赖图 / Internal Dependency Diagram

> 依赖图内嵌在本文档中，IDE 可直接渲染；网页版可 Ctrl+滚轮缩放 + 拖动平移查看细节。
>
> **图例说明 / Legend**：
> - 🟦 **蓝色 = 运营态模块**（production，已上线运行）
> - 🟧 **橙色虚线 = 设计态模块**（design，蓝图阶段，代码未写）
> - **实线箭头 = 运营态依赖**（已生效的依赖关系）
> - **虚线箭头 = 非运营态依赖**（计划中/验证中的依赖关系）

### 全景图（全部模块，颜色区分运营态/设计态）

> 展示全部 172 个模块（生产态 171 + 设计态 1），含跨域依赖外部节点。节点含成熟度+名称+大白话/简介+文件路径。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    docs_01_policies_and_standards_registry_catalogs_infrastructure_registry_yaml_INFRA_DB_001["catalogs/infrastructure_registry<br/>infrastructure_registry的INFRA-DB-001条目模块<br/>文件: catalogs<br/>/infrastructure_registry.yaml#INFRA-DB-001<br/>(生产态 / production)"]
    docs_01_policies_and_standards_registry_catalogs_infrastructure_registry_yaml_INFRA_DB_002["catalogs/infrastructure_registry<br/>infrastructure_registry的INFRA-DB-002条目模块<br/>文件: catalogs<br/>/infrastructure_registry.yaml#INFRA-DB-002<br/>(生产态 / production)"]
    docs_01_policies_and_standards_registry_catalogs_infrastructure_registry_yaml_INFRA_DB_003["catalogs/infrastructure_registry<br/>infrastructure_registry的INFRA-DB-003条目模块<br/>文件: catalogs<br/>/infrastructure_registry.yaml#INFRA-DB-003<br/>(生产态 / production)"]
    docs_01_policies_and_standards_registry_catalogs_infrastructure_registry_yaml_INFRA_DB_006["catalogs/infrastructure_registry<br/>infrastructure_registry的INFRA-DB-006条目模块<br/>文件: catalogs<br/>/infrastructure_registry.yaml#INFRA-DB-006<br/>(生产态 / production)"]
    docs_03_modules_cross_layer_agent_orchestrator_blueprint_md["agent_orchestrator/blueprint<br/>agent_orchestrator模块蓝图文档，描述该模块的设计<br/>意图和架构决策<br/>⛔ 基础设施运行时域，设计已就绪，等待开发排期<br/>文件: agent_orchestrator/blueprint.md<br/>(设计态 / design)"]
    src_zephyr_infrastructure_asset_inventory_main_py["asset_inventory/__main__<br/>Asset Inventory CLI — MOD-INF-026 蓝图 §31<br/>文件: asset_inventory/__main__.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_asset_inventory_lifecycle_py["asset_inventory/lifecycle<br/>AssetLifecycle — MOD-INF-026 L5<br/>ITIL生命周期自动化管理器<br/>文件: asset_inventory/lifecycle.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_asset_inventory_mcp_server_py["asset_inventory/mcp_server<br/>AssetInventory MCP Server — MOD-INF-026 蓝图 §21<br/>文件: asset_inventory/mcp_server.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_asset_inventory_metadata_py["asset_inventory/metadata<br/>基础设施/asset inventory包的metadata模块<br/>文件: asset_inventory/metadata.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_asset_inventory_trust_anchor_py["asset_inventory/trust_anchor<br/>基础设施/asset inventory包的trust_anchor模块<br/>文件: asset_inventory/trust_anchor.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_auto_diagnostics_py["infrastructure/auto_diagnostics<br/>RI-12 AutoDiagnostics — 自动诊断引擎<br/>文件: infrastructure/auto_diagnostics.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_auto_fix_engine_main_py["auto_fix_engine/__main__<br/>基础设施/auto fix engine包的main__模块<br/>文件: auto_fix_engine/__main__.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_auto_fix_engine_alignment_syncer_py["auto_fix_engine/alignment_syncer<br/>基础设施/auto fix engine包的alignment_syncer模块<br/>文件: auto_fix_engine/alignment_syncer.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_auto_fix_engine_all_completer_py["auto_fix_engine/all_completer<br/>基础设施/auto fix engine包的all_completer模块<br/>文件: auto_fix_engine/all_completer.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_auto_fix_engine_config_fixer_py["auto_fix_engine/config_fixer<br/>基础设施/auto fix engine包的config_fixer模块<br/>文件: auto_fix_engine/config_fixer.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_auto_fix_engine_dedup_extractor_py["auto_fix_engine/dedup_extractor<br/>基础设施/auto fix engine包的dedup_extractor模块<br/>文件: auto_fix_engine/dedup_extractor.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_auto_fix_engine_dep_version_fixer_py["auto_fix_engine/dep_version_fixer<br/>基础设施/auto fix<br/>engine包的dep_version_fixer模块<br/>文件: auto_fix_engine/dep_version_fixer.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_auto_fix_engine_drift_fixer_py["auto_fix_engine/drift_fixer<br/>基础设施/auto fix engine包的drift_fixer模块<br/>文件: auto_fix_engine/drift_fixer.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_auto_fix_engine_event_hooks_py["auto_fix_engine/event_hooks<br/>基础设施/auto fix engine包的event_hooks模块<br/>文件: auto_fix_engine/event_hooks.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_auto_fix_engine_fix_diff_py["auto_fix_engine/fix_diff<br/>基础设施/auto fix engine包的fix_diff模块<br/>文件: auto_fix_engine/fix_diff.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_auto_fix_engine_fix_scheduler_py["auto_fix_engine/fix_scheduler<br/>基础设施/auto fix engine包的fix_scheduler模块<br/>文件: auto_fix_engine/fix_scheduler.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_auto_fix_engine_import_fixer_py["auto_fix_engine/import_fixer<br/>基础设施/auto fix engine包的import_fixer模块<br/>文件: auto_fix_engine/import_fixer.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_auto_fix_engine_interrupt_guard_py["auto_fix_engine/interrupt_guard<br/>基础设施/auto fix engine包的interrupt_guard模块<br/>文件: auto_fix_engine/interrupt_guard.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_auto_fix_engine_llm_fix_adapter_py["auto_fix_engine/llm_fix_adapter<br/>基础设施/auto fix engine包的llm_fix_adapter模块<br/>文件: auto_fix_engine/llm_fix_adapter.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_auto_fix_engine_scaffold_registrar_py["auto_fix_engine/scaffold_registrar<br/>基础设施/auto fix<br/>engine包的scaffold_registrar模块<br/>文件: auto_fix_engine/scaffold_registrar.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_auto_fix_engine_self_heal_agent_py["auto_fix_engine/self_heal_agent<br/>基础设施/auto fix engine包的self_heal_agent模块<br/>文件: auto_fix_engine/self_heal_agent.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_auto_fix_engine_state_machine_py["auto_fix_engine/state_machine<br/>基础设施/auto fix engine包的state_machine模块<br/>文件: auto_fix_engine/state_machine.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_auto_fix_engine_zombie_cleaner_py["auto_fix_engine/zombie_cleaner<br/>基础设施/auto fix engine包的zombie_cleaner模块<br/>文件: auto_fix_engine/zombie_cleaner.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_blueprint_code_sync_py["infrastructure/blueprint_code_sync<br/>Blueprint-Code Sync — 蓝图-代码索引同步验证。<br/>文件: infrastructure/blueprint_code_sync.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_budget_enforcement_init_py["infrastructure/budget_enforcement 包入口<br/>budget_enforcement 包聚合层。<br/>文件: budget_enforcement/__init__.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_capacity_assurance_budget_forecaster_py["capacity_assurance/budget_forecaster<br/>budget_forecaster.py — Token 预算预测<br/>(DD120-extra, TASK-020)<br/>文件: capacity_assurance/budget_forecaster.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_capacity_assurance_contracts_contract_bus_py["contracts/contract_bus<br/>ContractBus loader —<br/>加载全部44条容量保障契约的Pydantic v2 Schema<br/>（DD-9三批...<br/>文件: contracts/contract_bus.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_capacity_assurance_cross_module_integration_py["capacity_assurance/cross_module_integration<br/>Cross-module integration — CT-1~CT-4<br/>跨模块集成契约实现（对标蓝图 §17）.<br/>文件: capacity_assurance<br/>/cross_module_integration.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_capacity_assurance_host_resource_governor_py["capacity_assurance/host_resource_governor<br/>host_resource_governor.py — 主机资源治理 (B17,<br/>DD91, TASK-017)<br/>文件: capacity_assurance<br/>/host_resource_governor.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_capacity_assurance_kill_switch_py["capacity_assurance/kill_switch<br/>kill_switch.py -- safety circuit breaker<br/>(DD110, TASK-019).<br/>文件: capacity_assurance/kill_switch.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_capacity_assurance_risk_mitigation_py["capacity_assurance/risk_mitigation<br/>Risk mitigation — R1~R16 全量风险缓解实现<br/>（对标蓝图 §14 风险与缓解 + 多轮盲...<br/>文件: capacity_assurance/risk_mitigation.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_capacity_assurance_schema_py["capacity_assurance/schema<br/>SchemaManager — 容量保障体系数据库 Schema 管理器<br/>文件: capacity_assurance/schema.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_capacity_assurance_sli_instrumentation_py["capacity_assurance/sli_instrumentation<br/>SLI instrumentation — SLI采集插桩点（对标蓝图<br/>§13 SLI Registry CAP-001~CAP-...<br/>文件: capacity_assurance/sli_instrumentation.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_capacity_assurance_tech_stack_py["capacity_assurance/tech_stack<br/>TechStackValidator — 技术栈可用性校验器<br/>文件: capacity_assurance/tech_stack.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_capacity_assurance_token_budget_py["capacity_assurance/token_budget<br/>token_budget.py — Token 估算工具 SSoT<br/>文件: capacity_assurance/token_budget.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_cost_tracker_py["infrastructure/cost_tracker<br/>RI-15 CostTracker — 成本追踪器<br/>文件: infrastructure/cost_tracker.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_dry_run_simulator_py["infrastructure/dry_run_simulator<br/>RI-14 DryRunSimulator — 干运行模拟器<br/>文件: infrastructure/dry_run_simulator.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_event_bus_upgrade_py["infrastructure/event_bus_upgrade<br/>DEPRECATED: 此文件已废弃。<br/>文件: infrastructure/event_bus_upgrade.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_event_store_py["infrastructure/event_store<br/>RI-13 EventStore — 事件存储<br/>文件: infrastructure/event_store.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_events_event_store_py["events/event_store<br/>Event Store — 事件持久化存储。<br/>文件: events/event_store.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_finding_task_bridge_py["infrastructure/finding_task_bridge<br/>Finding->TaskCard 桥接器<br/>文件: infrastructure/finding_task_bridge.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_git_batcher_py["infrastructure/git_batcher<br/>git_batcher.py — Git 命令批量化工具<br/>（ARCH-GIT-CALL-BUDGET P2.2，2026-07-19）<br/>文件: infrastructure/git_batcher.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_h1_redis_hot_init_py["infrastructure/h1_redis_hot 包入口<br/>H1 Redis 热缓存模块——盘中实盘/模拟盘 <5ms<br/>因子截面在线存储（DD-11-01）。<br/>文件: h1_redis_hot/__init__.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_h1_redis_hot_h1_cqrs_projectors_py["h1_redis_hot/h1_cqrs_projectors<br/>H1CqrsProjectors — 事件→Redis 物化视图投影器。<br/>文件: h1_redis_hot/h1_cqrs_projectors.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_h1_redis_hot_h1_integration_py["h1_redis_hot/h1_integration<br/>H1 Redis 集成适配器——连接 D-FACTOR/SIGNAL/RISK<br/>与 H1 热缓存。<br/>文件: h1_redis_hot/h1_integration.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_health_monitor_health_aggregator_py["health_monitor/health_aggregator<br/>全系统健康聚合 — check_all_systems()<br/>文件: health_monitor/health_aggregator.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_hooks_event_hook_py["hooks/event_hook<br/>EventHook — 声明式任务系统事件订阅<br/>文件: hooks/event_hook.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_impact_impact_propagator_py["impact/impact_propagator<br/>Impact Propagator — 变更影响传播分析。<br/>文件: impact/impact_propagator.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_impact_llm_impact_analyzer_py["impact/llm_impact_analyzer<br/>LLM Impact Analyzer — 语义影响分析器。<br/>文件: impact/llm_impact_analyzer.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_infrastructure_base_py["infrastructure/infrastructure_base<br/>基础设施 — Infrastructure Layer Skeleton<br/>文件: infrastructure/infrastructure_base.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_kill_switch_sim_py["infrastructure/kill_switch_sim<br/>Kill Switch T0 Hardware Simulator<br/>文件: infrastructure/kill_switch_sim.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_lifecycle_scope_guard_py["lifecycle/scope_guard<br/>Scope Guard — 范围蔓延检测与阻断。<br/>文件: lifecycle/scope_guard.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_lifecycle_task_lifecycle_manager_py["lifecycle/task_lifecycle_manager<br/>Task Lifecycle Manager — G0-G7<br/>任务生命周期门禁。<br/>文件: lifecycle/task_lifecycle_manager.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_observability_trace_decorator_py["observability/trace_decorator<br/>基础设施/observability包的trace_decorator模块<br/>文件: observability/trace_decorator.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_pipeline_backpressure_manager_py["pipeline/backpressure_manager<br/>Pipeline — Backpressure Manager<br/>文件: pipeline/backpressure_manager.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_pipeline_circuit_breaker_manager_py["pipeline/circuit_breaker_manager<br/>CircuitBreakerManager -- standalone circuit<br/>breaker manager (Netflix Hystrix ...<br/>文件: pipeline/circuit_breaker_manager.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_pipeline_cost_tracker_py["pipeline/cost_tracker<br/>CostTracker —— LLM 调用成本追踪器（SRC-0025）<br/>文件: pipeline/cost_tracker.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_pipeline_dead_letter_queue_py["pipeline/dead_letter_queue<br/>DeadLetterQueue — 死信队列<br/>文件: pipeline/dead_letter_queue.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_pipeline_llm_gateway_py["pipeline/llm_gateway<br/>MOD-INF-019: Agent Spec — LLM Gateway<br/>文件: pipeline/llm_gateway.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_pipeline_pipeline_agent_bridge_py["pipeline/pipeline_agent_bridge<br/>Pipeline -> Agent Bridge — 双编排器桥接层<br/>文件: pipeline/pipeline_agent_bridge.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_pipeline_pipeline_lock_py["pipeline/pipeline_lock<br/>Pipeline Lock — 双管线并发锁<br/>文件: pipeline/pipeline_lock.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_pipeline_pipeline_roadmap_py["pipeline/pipeline_roadmap<br/>Pipeline 未来版本路线图——v0.10.0 -> v0.12.0<br/>规划骨架。<br/>文件: pipeline/pipeline_roadmap.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_pipeline_preemption_manager_py["pipeline/preemption_manager<br/>PreemptionManager -- 优先级抢占管理器<br/>文件: pipeline/preemption_manager.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_pipeline_routing_plugins_py["pipeline/routing_plugins<br/>Pipeline Routing Plugin System — K8s Scheduling<br/>Framework 对标<br/>文件: pipeline/routing_plugins.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_pydantic_v2_migrator_py["infrastructure/pydantic_v2_migrator<br/>M-15 PydanticV2Migrator — Pydantic V2 迁移工具<br/>文件: infrastructure/pydantic_v2_migrator.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_quality_quality_monitor_py["quality/quality_monitor<br/>Quality Monitor — 生成代码质量门禁。<br/>文件: quality/quality_monitor.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_reliability_circuit_breaker_py["reliability/circuit_breaker<br/>Circuit Breaker — 熔断器：连续失败 -> OPEN -><br/>暂停执行。<br/>文件: reliability/circuit_breaker.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_reliability_context_guard_py["reliability/context_guard<br/>Context Guard — 上下文契约守卫。<br/>文件: reliability/context_guard.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_runtime_concurrency_guard_py["runtime/concurrency_guard<br/>concurrency_guard — 回滚操作并发安全守卫。<br/>文件: runtime/concurrency_guard.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_runtime_sandbox_enforcer_py["runtime/sandbox_enforcer<br/>SandboxEnforcer — Agent 沙盒隔离。<br/>文件: runtime/sandbox_enforcer.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_runtime_startup_shutdown_py["runtime/startup_shutdown<br/>基础设施/运行时包的startup_shutdown模块<br/>文件: runtime/startup_shutdown.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_script_system_finding_py["script_system/finding<br/>Finding Schema — 审计发现标准化数据模型<br/>文件: script_system/finding.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_script_system_gate_bridge_py["script_system/gate_bridge<br/>Script->Gate 门禁桥接器 — submit_findings()<br/>生产者<br/>文件: script_system/gate_bridge.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_system_telemetry_auto_bootstrap_py["system_telemetry/auto_bootstrap<br/>auto_bootstrap — 全自动遥测注入钩子<br/>（MOD-INF-015 v2.1.0）<br/>文件: system_telemetry/auto_bootstrap.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_system_telemetry_logs_init_py["system_telemetry/logs 包入口<br/>logs — 结构化日志流（structlog + JSONL +<br/>trace注入）（D_SYSTEM_TELEMETRY）<br/>文件: logs/__init__.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_system_telemetry_metrics_bridge_py["system_telemetry/metrics_bridge<br/>TELE->FLE 指标桥接 — emit_metrics() 生产者<br/>文件: system_telemetry/metrics_bridge.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_warm_hot_gate_py["infrastructure/warm_hot_gate<br/>M-14 WarmHotGate — Warm->Hot 阻断门<br/>文件: infrastructure/warm_hot_gate.py<br/>(生产态 / production)"]
    src_zephyr_shared_lifecycle_hooks_py["lifecycle/hooks<br/>hooks.py —— 模块生命周期钩子（Phase 2 新增 /<br/>盲点 B8 修复）<br/>文件: lifecycle/hooks.py<br/>(生产态 / production)"]
    src_zephyr_trading_action_dispatcher_py["trading/action_dispatcher<br/>ActionDispatcher --- 大脑的'手' v2.0 (Phase 2)<br/>文件: trading/action_dispatcher.py<br/>(生产态 / production)"]
    src_zephyr_trading_auto_task_generator_py["trading/auto_task_generator<br/>AutoTaskGenerator — 自动任务生成器<br/>文件: trading/auto_task_generator.py<br/>(生产态 / production)"]
    src_zephyr_trading_ports_py["trading/ports<br/>Protocol-based interface layer for<br/>runtime->pipeline dependency abstraction.<br/>文件: trading/ports.py<br/>(生产态 / production)"]
    src_zephyr_trading_staging_area_py["trading/staging_area<br/>StagingArea —<br/>多AI并发草稿写入+提交+冲突检测模块<br/>（CT-SESSION-CONFLICT-002）<br/>文件: trading/staging_area.py<br/>(生产态 / production)"]
    src_zephyr_trading_task_gate_py["trading/task_gate<br/>TaskGate --- 任务门控<br/>文件: trading/task_gate.py<br/>(生产态 / production)"]
    src_zephyr_trading_windows_service_py["trading/windows_service<br/>WindowsService — Windows Service 包装器<br/>文件: trading/windows_service.py<br/>(生产态 / production)"]
    src_zephyr_trading_zombie_scanner_py["trading/zombie_scanner<br/>zombie_scanner.py — 僵尸 Python<br/>进程检测与自动处置<br/>文件: trading/zombie_scanner.py<br/>(生产态 / production)"]
    tests_zephyr_data_test_tick_redis_cache_py["data/test_tick_redis_cache<br/>TickRedisCache 单元测试——tick→Redis<br/>tick:{symbol}:latest 双写器。<br/>文件: data/test_tick_redis_cache.py<br/>(生产态 / production)"]
    tests_zephyr_runtime_test_intraday_main_py["runtime/test_intraday_main<br/>IntradayRuntime 盘中编排器单元测试。<br/>文件: runtime/test_intraday_main.py<br/>(生产态 / production)"]
    docs_01_policies_and_standards_registry_catalogs_infrastructure_registry_yaml_INFRA_DB_001 ~~~ docs_01_policies_and_standards_registry_catalogs_infrastructure_registry_yaml_INFRA_DB_002
    docs_01_policies_and_standards_registry_catalogs_infrastructure_registry_yaml_INFRA_DB_002 ~~~ docs_01_policies_and_standards_registry_catalogs_infrastructure_registry_yaml_INFRA_DB_003
    docs_01_policies_and_standards_registry_catalogs_infrastructure_registry_yaml_INFRA_DB_003 ~~~ docs_01_policies_and_standards_registry_catalogs_infrastructure_registry_yaml_INFRA_DB_006
    docs_01_policies_and_standards_registry_catalogs_infrastructure_registry_yaml_INFRA_DB_006 ~~~ docs_03_modules_cross_layer_agent_orchestrator_blueprint_md
    docs_03_modules_cross_layer_agent_orchestrator_blueprint_md ~~~ src_zephyr_infrastructure_asset_inventory_main_py
    src_zephyr_infrastructure_asset_inventory_main_py ~~~ src_zephyr_infrastructure_asset_inventory_lifecycle_py
    src_zephyr_infrastructure_asset_inventory_lifecycle_py ~~~ src_zephyr_infrastructure_asset_inventory_mcp_server_py
    src_zephyr_infrastructure_asset_inventory_mcp_server_py ~~~ src_zephyr_infrastructure_asset_inventory_metadata_py
    src_zephyr_infrastructure_asset_inventory_metadata_py ~~~ src_zephyr_infrastructure_asset_inventory_trust_anchor_py
    src_zephyr_infrastructure_asset_inventory_trust_anchor_py ~~~ src_zephyr_infrastructure_auto_diagnostics_py
    src_zephyr_infrastructure_auto_diagnostics_py ~~~ src_zephyr_infrastructure_auto_fix_engine_main_py
    src_zephyr_infrastructure_auto_fix_engine_main_py ~~~ src_zephyr_infrastructure_auto_fix_engine_alignment_syncer_py
    src_zephyr_infrastructure_auto_fix_engine_alignment_syncer_py ~~~ src_zephyr_infrastructure_auto_fix_engine_all_completer_py
    src_zephyr_infrastructure_auto_fix_engine_all_completer_py ~~~ src_zephyr_infrastructure_auto_fix_engine_config_fixer_py
    src_zephyr_infrastructure_auto_fix_engine_config_fixer_py ~~~ src_zephyr_infrastructure_auto_fix_engine_dedup_extractor_py
    src_zephyr_infrastructure_auto_fix_engine_dedup_extractor_py ~~~ src_zephyr_infrastructure_auto_fix_engine_dep_version_fixer_py
    src_zephyr_infrastructure_auto_fix_engine_dep_version_fixer_py ~~~ src_zephyr_infrastructure_auto_fix_engine_drift_fixer_py
    src_zephyr_infrastructure_auto_fix_engine_drift_fixer_py ~~~ src_zephyr_infrastructure_auto_fix_engine_event_hooks_py
    src_zephyr_infrastructure_auto_fix_engine_event_hooks_py ~~~ src_zephyr_infrastructure_auto_fix_engine_fix_diff_py
    src_zephyr_infrastructure_auto_fix_engine_fix_diff_py ~~~ src_zephyr_infrastructure_auto_fix_engine_fix_scheduler_py
    src_zephyr_infrastructure_auto_fix_engine_fix_scheduler_py ~~~ src_zephyr_infrastructure_auto_fix_engine_import_fixer_py
    src_zephyr_infrastructure_auto_fix_engine_import_fixer_py ~~~ src_zephyr_infrastructure_auto_fix_engine_interrupt_guard_py
    src_zephyr_infrastructure_auto_fix_engine_interrupt_guard_py ~~~ src_zephyr_infrastructure_auto_fix_engine_llm_fix_adapter_py
    src_zephyr_infrastructure_auto_fix_engine_llm_fix_adapter_py ~~~ src_zephyr_infrastructure_auto_fix_engine_scaffold_registrar_py
    src_zephyr_infrastructure_auto_fix_engine_scaffold_registrar_py ~~~ src_zephyr_infrastructure_auto_fix_engine_self_heal_agent_py
    src_zephyr_infrastructure_auto_fix_engine_self_heal_agent_py ~~~ src_zephyr_infrastructure_auto_fix_engine_state_machine_py
    src_zephyr_infrastructure_auto_fix_engine_state_machine_py ~~~ src_zephyr_infrastructure_auto_fix_engine_zombie_cleaner_py
    src_zephyr_infrastructure_auto_fix_engine_zombie_cleaner_py ~~~ src_zephyr_infrastructure_blueprint_code_sync_py
    src_zephyr_infrastructure_blueprint_code_sync_py ~~~ src_zephyr_infrastructure_budget_enforcement_init_py
    src_zephyr_infrastructure_budget_enforcement_init_py ~~~ src_zephyr_infrastructure_capacity_assurance_budget_forecaster_py
    src_zephyr_infrastructure_capacity_assurance_budget_forecaster_py ~~~ src_zephyr_infrastructure_capacity_assurance_contracts_contract_bus_py
    src_zephyr_infrastructure_capacity_assurance_contracts_contract_bus_py ~~~ src_zephyr_infrastructure_capacity_assurance_cross_module_integration_py
    src_zephyr_infrastructure_capacity_assurance_cross_module_integration_py ~~~ src_zephyr_infrastructure_capacity_assurance_host_resource_governor_py
    src_zephyr_infrastructure_capacity_assurance_host_resource_governor_py ~~~ src_zephyr_infrastructure_capacity_assurance_kill_switch_py
    src_zephyr_infrastructure_capacity_assurance_kill_switch_py ~~~ src_zephyr_infrastructure_capacity_assurance_risk_mitigation_py
    src_zephyr_infrastructure_capacity_assurance_risk_mitigation_py ~~~ src_zephyr_infrastructure_capacity_assurance_schema_py
    src_zephyr_infrastructure_capacity_assurance_schema_py ~~~ src_zephyr_infrastructure_capacity_assurance_sli_instrumentation_py
    src_zephyr_infrastructure_capacity_assurance_sli_instrumentation_py ~~~ src_zephyr_infrastructure_capacity_assurance_tech_stack_py
    src_zephyr_infrastructure_capacity_assurance_tech_stack_py ~~~ src_zephyr_infrastructure_capacity_assurance_token_budget_py
    src_zephyr_infrastructure_capacity_assurance_token_budget_py ~~~ src_zephyr_infrastructure_cost_tracker_py
    src_zephyr_infrastructure_cost_tracker_py ~~~ src_zephyr_infrastructure_dry_run_simulator_py
    src_zephyr_infrastructure_dry_run_simulator_py ~~~ src_zephyr_infrastructure_event_bus_upgrade_py
    src_zephyr_infrastructure_event_bus_upgrade_py ~~~ src_zephyr_infrastructure_event_store_py
    src_zephyr_infrastructure_event_store_py ~~~ src_zephyr_infrastructure_events_event_store_py
    src_zephyr_infrastructure_events_event_store_py ~~~ src_zephyr_infrastructure_finding_task_bridge_py
    src_zephyr_infrastructure_finding_task_bridge_py ~~~ src_zephyr_infrastructure_git_batcher_py
    src_zephyr_infrastructure_git_batcher_py ~~~ src_zephyr_infrastructure_h1_redis_hot_init_py
    src_zephyr_infrastructure_h1_redis_hot_init_py ~~~ src_zephyr_infrastructure_h1_redis_hot_h1_cqrs_projectors_py
    src_zephyr_infrastructure_h1_redis_hot_h1_cqrs_projectors_py ~~~ src_zephyr_infrastructure_h1_redis_hot_h1_integration_py
    src_zephyr_infrastructure_h1_redis_hot_h1_integration_py ~~~ src_zephyr_infrastructure_health_monitor_health_aggregator_py
    src_zephyr_infrastructure_health_monitor_health_aggregator_py ~~~ src_zephyr_infrastructure_hooks_event_hook_py
    src_zephyr_infrastructure_hooks_event_hook_py ~~~ src_zephyr_infrastructure_impact_impact_propagator_py
    src_zephyr_infrastructure_impact_impact_propagator_py ~~~ src_zephyr_infrastructure_impact_llm_impact_analyzer_py
    src_zephyr_infrastructure_impact_llm_impact_analyzer_py ~~~ src_zephyr_infrastructure_infrastructure_base_py
    src_zephyr_infrastructure_infrastructure_base_py ~~~ src_zephyr_infrastructure_kill_switch_sim_py
    src_zephyr_infrastructure_kill_switch_sim_py ~~~ src_zephyr_infrastructure_lifecycle_scope_guard_py
    src_zephyr_infrastructure_lifecycle_scope_guard_py ~~~ src_zephyr_infrastructure_lifecycle_task_lifecycle_manager_py
    src_zephyr_infrastructure_lifecycle_task_lifecycle_manager_py ~~~ src_zephyr_infrastructure_observability_trace_decorator_py
    src_zephyr_infrastructure_observability_trace_decorator_py ~~~ src_zephyr_infrastructure_pipeline_backpressure_manager_py
    src_zephyr_infrastructure_pipeline_backpressure_manager_py ~~~ src_zephyr_infrastructure_pipeline_circuit_breaker_manager_py
    src_zephyr_infrastructure_pipeline_circuit_breaker_manager_py ~~~ src_zephyr_infrastructure_pipeline_cost_tracker_py
    src_zephyr_infrastructure_pipeline_cost_tracker_py ~~~ src_zephyr_infrastructure_pipeline_dead_letter_queue_py
    src_zephyr_infrastructure_pipeline_dead_letter_queue_py ~~~ src_zephyr_infrastructure_pipeline_llm_gateway_py
    src_zephyr_infrastructure_pipeline_llm_gateway_py ~~~ src_zephyr_infrastructure_pipeline_pipeline_agent_bridge_py
    src_zephyr_infrastructure_pipeline_pipeline_agent_bridge_py ~~~ src_zephyr_infrastructure_pipeline_pipeline_lock_py
    src_zephyr_infrastructure_pipeline_pipeline_lock_py ~~~ src_zephyr_infrastructure_pipeline_pipeline_roadmap_py
    src_zephyr_infrastructure_pipeline_pipeline_roadmap_py ~~~ src_zephyr_infrastructure_pipeline_preemption_manager_py
    src_zephyr_infrastructure_pipeline_preemption_manager_py ~~~ src_zephyr_infrastructure_pipeline_routing_plugins_py
    src_zephyr_infrastructure_pipeline_routing_plugins_py ~~~ src_zephyr_infrastructure_pydantic_v2_migrator_py
    src_zephyr_infrastructure_pydantic_v2_migrator_py ~~~ src_zephyr_infrastructure_quality_quality_monitor_py
    src_zephyr_infrastructure_quality_quality_monitor_py ~~~ src_zephyr_infrastructure_reliability_circuit_breaker_py
    src_zephyr_infrastructure_reliability_circuit_breaker_py ~~~ src_zephyr_infrastructure_reliability_context_guard_py
    src_zephyr_infrastructure_reliability_context_guard_py ~~~ src_zephyr_infrastructure_runtime_concurrency_guard_py
    src_zephyr_infrastructure_runtime_concurrency_guard_py ~~~ src_zephyr_infrastructure_runtime_sandbox_enforcer_py
    src_zephyr_infrastructure_runtime_sandbox_enforcer_py ~~~ src_zephyr_infrastructure_runtime_startup_shutdown_py
    src_zephyr_infrastructure_runtime_startup_shutdown_py ~~~ src_zephyr_infrastructure_script_system_finding_py
    src_zephyr_infrastructure_script_system_finding_py ~~~ src_zephyr_infrastructure_script_system_gate_bridge_py
    src_zephyr_infrastructure_script_system_gate_bridge_py ~~~ src_zephyr_infrastructure_system_telemetry_auto_bootstrap_py
    src_zephyr_infrastructure_system_telemetry_auto_bootstrap_py ~~~ src_zephyr_infrastructure_system_telemetry_logs_init_py
    src_zephyr_infrastructure_system_telemetry_logs_init_py ~~~ src_zephyr_infrastructure_system_telemetry_metrics_bridge_py
    src_zephyr_infrastructure_system_telemetry_metrics_bridge_py ~~~ src_zephyr_infrastructure_warm_hot_gate_py
    src_zephyr_infrastructure_warm_hot_gate_py ~~~ src_zephyr_shared_lifecycle_hooks_py
    src_zephyr_shared_lifecycle_hooks_py ~~~ src_zephyr_trading_action_dispatcher_py
    src_zephyr_trading_action_dispatcher_py ~~~ src_zephyr_trading_auto_task_generator_py
    src_zephyr_trading_auto_task_generator_py ~~~ src_zephyr_trading_ports_py
    src_zephyr_trading_ports_py ~~~ src_zephyr_trading_staging_area_py
    src_zephyr_trading_staging_area_py ~~~ src_zephyr_trading_task_gate_py
    src_zephyr_trading_task_gate_py ~~~ src_zephyr_trading_windows_service_py
    src_zephyr_trading_windows_service_py ~~~ src_zephyr_trading_zombie_scanner_py
    src_zephyr_trading_zombie_scanner_py ~~~ tests_zephyr_data_test_tick_redis_cache_py
    tests_zephyr_data_test_tick_redis_cache_py ~~~ tests_zephyr_runtime_test_intraday_main_py
    src_zephyr_infrastructure_asset_inventory_classifier_py["asset_inventory/classifier<br/>AssetClassifier — MOD-INF-026 L2 资产自动分类器<br/>文件: asset_inventory/classifier.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_asset_inventory_dashboard_py["asset_inventory/dashboard<br/>AssetDashboard — MOD-INF-026<br/>资产健康仪表盘生成器<br/>文件: asset_inventory/dashboard.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_asset_inventory_dependency_py["asset_inventory/dependency<br/>MOD-INF-026 §18 — 资产依赖图。<br/>文件: asset_inventory/dependency.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_asset_inventory_index_generator_py["asset_inventory/index_generator<br/>UnifiedAssetIndex — MOD-INF-026 L3<br/>统一资产索引生成器<br/>文件: asset_inventory/index_generator.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_asset_inventory_reconciler_py["asset_inventory/reconciler<br/>ReconciliationEngine — MOD-INF-026 L4 注册表 vs<br/>磁盘对账引擎<br/>文件: asset_inventory/reconciler.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_asset_inventory_registry_adapter_py["asset_inventory/registry_adapter<br/>MOD-INF-026 §17 — 24<br/>个异构注册表统一解析适配器。<br/>文件: asset_inventory/registry_adapter.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_asset_inventory_scanner_py["asset_inventory/scanner<br/>AssetDiscoveryScanner — MOD-INF-026 L1<br/>全量文件系统扫描器<br/>文件: asset_inventory/scanner.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_asset_inventory_telemetry_py["asset_inventory/telemetry<br/>AssetInventoryTelemetry — MOD-INF-026 自监控指标<br/>文件: asset_inventory/telemetry.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_auto_fix_engine_engine_py["auto_fix_engine/engine<br/>基础设施/auto fix engine包的engine模块<br/>文件: auto_fix_engine/engine.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_budget_enforcement_rbac_bridge_py["budget_enforcement/rbac_bridge<br/>budget_enforcement.rbac_bridge — 基础设施层<br/>RBAC 桥接适配器。<br/>文件: budget_enforcement/rbac_bridge.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_capacity_assurance_contracts_batch1_infra_py["contracts/batch1_infra<br/>Batch1 基础设施层契约 — 15条 Pydantic v2<br/>Schema（SLO/Error Budget/Token Budg...<br/>文件: contracts/batch1_infra.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_capacity_assurance_contracts_batch3_integration_py["contracts/batch3_integration<br/>Batch3 集成层契约 — 14条 Pydantic v2 Schema<br/>（OTel/W3C/跨模块CT-1~4/DR/容量预...<br/>文件: contracts/batch3_integration.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_config_validator_py["infrastructure/config_validator<br/>M-12 ConfigValidator — 配置参数校验器<br/>文件: infrastructure/config_validator.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_contract_tester_py["infrastructure/contract_tester<br/>M-11 ContractTester — 契约测试框架<br/>文件: infrastructure/contract_tester.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_h1_redis_hot_h1_redis_reader_py["h1_redis_hot/h1_redis_reader<br/>H1RedisReader — 决策引擎 <5ms 在线特征查询。<br/>文件: h1_redis_hot/h1_redis_reader.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_h1_redis_hot_h1_redis_writer_py["h1_redis_hot/h1_redis_writer<br/>H1RedisWriter — D-FACTOR Engine 每 3 秒截面写入<br/>Redis（PIPELINE 模式）。<br/>文件: h1_redis_hot/h1_redis_writer.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_pipeline_backpressure_types_py["pipeline/backpressure_types<br/>backpressure_types.py - Pipeline backpressure<br/>signal data types<br/>文件: pipeline/backpressure_types.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_pipeline_ct_pipe_routing_py["pipeline/ct_pipe_routing<br/>CT-PIPE-ORC-001 — TaskCard -> 管线入口节点路由<br/>文件: pipeline/ct_pipe_routing.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_pipeline_model_router_py["pipeline/model_router<br/>ModelRouter — 模型路由与降级链管理<br/>文件: pipeline/model_router.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_queue_task_scheduler_py["queue/task_scheduler<br/>Task Scheduler — 任务调度器。<br/>文件: queue/task_scheduler.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_system_telemetry_budget_telemetry_bridge_py["system_telemetry/_budget_telemetry_bridge<br/>基础设施/system<br/>telemetry包的budget_telemetry_bridge模块<br/>文件: system_telemetry<br/>/_budget_telemetry_bridge.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_system_telemetry_contract_metrics_py["system_telemetry/contract_metrics<br/>ZephyrAlpha — system-telemetry<br/>/contract_metrics.py<br/>文件: system_telemetry/contract_metrics.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_system_telemetry_metrics_blueprint_metrics_py["metrics/blueprint_metrics<br/>blueprint_metrics — 蓝图使用追踪 instrumentation<br/>文件: metrics/blueprint_metrics.py<br/>(生产态 / production)"]
    src_zephyr_runtime_intraday_main_py["runtime/intraday_main<br/>盘中运行时编排器——单进程串起 tick_subscriber +<br/>IntradayFactorLoop。<br/>文件: runtime/intraday_main.py<br/>(生产态 / production)"]
    src_zephyr_trading_main_py["trading/__main__<br/>python -m zephyr.trading — AutoRuntime Core 入口<br/>文件: trading/__main__.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_asset_inventory_classifier_py ~~~ src_zephyr_infrastructure_asset_inventory_dashboard_py
    src_zephyr_infrastructure_asset_inventory_dashboard_py ~~~ src_zephyr_infrastructure_asset_inventory_dependency_py
    src_zephyr_infrastructure_asset_inventory_dependency_py ~~~ src_zephyr_infrastructure_asset_inventory_index_generator_py
    src_zephyr_infrastructure_asset_inventory_index_generator_py ~~~ src_zephyr_infrastructure_asset_inventory_reconciler_py
    src_zephyr_infrastructure_asset_inventory_reconciler_py ~~~ src_zephyr_infrastructure_asset_inventory_registry_adapter_py
    src_zephyr_infrastructure_asset_inventory_registry_adapter_py ~~~ src_zephyr_infrastructure_asset_inventory_scanner_py
    src_zephyr_infrastructure_asset_inventory_scanner_py ~~~ src_zephyr_infrastructure_asset_inventory_telemetry_py
    src_zephyr_infrastructure_asset_inventory_telemetry_py ~~~ src_zephyr_infrastructure_auto_fix_engine_engine_py
    src_zephyr_infrastructure_auto_fix_engine_engine_py ~~~ src_zephyr_infrastructure_budget_enforcement_rbac_bridge_py
    src_zephyr_infrastructure_budget_enforcement_rbac_bridge_py ~~~ src_zephyr_infrastructure_capacity_assurance_contracts_batch1_infra_py
    src_zephyr_infrastructure_capacity_assurance_contracts_batch1_infra_py ~~~ src_zephyr_infrastructure_capacity_assurance_contracts_batch3_integration_py
    src_zephyr_infrastructure_capacity_assurance_contracts_batch3_integration_py ~~~ src_zephyr_infrastructure_config_validator_py
    src_zephyr_infrastructure_config_validator_py ~~~ src_zephyr_infrastructure_contract_tester_py
    src_zephyr_infrastructure_contract_tester_py ~~~ src_zephyr_infrastructure_h1_redis_hot_h1_redis_reader_py
    src_zephyr_infrastructure_h1_redis_hot_h1_redis_reader_py ~~~ src_zephyr_infrastructure_h1_redis_hot_h1_redis_writer_py
    src_zephyr_infrastructure_h1_redis_hot_h1_redis_writer_py ~~~ src_zephyr_infrastructure_pipeline_backpressure_types_py
    src_zephyr_infrastructure_pipeline_backpressure_types_py ~~~ src_zephyr_infrastructure_pipeline_ct_pipe_routing_py
    src_zephyr_infrastructure_pipeline_ct_pipe_routing_py ~~~ src_zephyr_infrastructure_pipeline_model_router_py
    src_zephyr_infrastructure_pipeline_model_router_py ~~~ src_zephyr_infrastructure_queue_task_scheduler_py
    src_zephyr_infrastructure_queue_task_scheduler_py ~~~ src_zephyr_infrastructure_system_telemetry_budget_telemetry_bridge_py
    src_zephyr_infrastructure_system_telemetry_budget_telemetry_bridge_py ~~~ src_zephyr_infrastructure_system_telemetry_contract_metrics_py
    src_zephyr_infrastructure_system_telemetry_contract_metrics_py ~~~ src_zephyr_infrastructure_system_telemetry_metrics_blueprint_metrics_py
    src_zephyr_infrastructure_system_telemetry_metrics_blueprint_metrics_py ~~~ src_zephyr_runtime_intraday_main_py
    src_zephyr_runtime_intraday_main_py ~~~ src_zephyr_trading_main_py
    src_zephyr_data_tick_redis_cache_py["data/tick_redis_cache<br/>tick → Redis tick:{symbol}:latest 双写器<br/>（D-DATA → H1 集成适配器）。<br/>文件: data/tick_redis_cache.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_asset_inventory_models_py["asset_inventory/models<br/>AssetInventoryModels — MOD-INF-026 Pydantic V2<br/>共享数据模型<br/>文件: asset_inventory/models.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_auto_fix_engine_batch_fixer_py["auto_fix_engine/batch_fixer<br/>基础设施/auto fix engine包的batch_fixer模块<br/>文件: auto_fix_engine/batch_fixer.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_auto_fix_engine_compliance_auditor_py["auto_fix_engine/compliance_auditor<br/>基础设施/auto fix<br/>engine包的compliance_auditor模块<br/>文件: auto_fix_engine/compliance_auditor.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_auto_fix_engine_escalation_bridge_py["auto_fix_engine/escalation_bridge<br/>基础设施/auto fix<br/>engine包的escalation_bridge模块<br/>文件: auto_fix_engine/escalation_bridge.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_auto_fix_engine_fix_health_check_py["auto_fix_engine/fix_health_check<br/>基础设施/auto fix engine包的fix_health_check模块<br/>文件: auto_fix_engine/fix_health_check.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_auto_fix_engine_fix_pattern_miner_py["auto_fix_engine/fix_pattern_miner<br/>基础设施/auto fix<br/>engine包的fix_pattern_miner模块<br/>文件: auto_fix_engine/fix_pattern_miner.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_auto_fix_engine_fix_report_py["auto_fix_engine/fix_report<br/>基础设施/auto fix engine包的fix_report模块<br/>文件: auto_fix_engine/fix_report.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_auto_fix_engine_fix_safety_py["auto_fix_engine/fix_safety<br/>基础设施/auto fix engine包的fix_safety模块<br/>文件: auto_fix_engine/fix_safety.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_auto_fix_engine_shadow_workspace_py["auto_fix_engine/shadow_workspace<br/>基础设施/auto fix engine包的shadow_workspace模块<br/>文件: auto_fix_engine/shadow_workspace.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_database_service_py["infrastructure/database_service<br/>DatabaseService:<br/>统一管理数据库的连接池、生命周期、健康检查<br/>文件: infrastructure/database_service.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_pipeline_models_py["pipeline/models<br/>Pipeline 数据模型<br/>文件: pipeline/models.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_system_telemetry_facade_py["system_telemetry/facade<br/>Telemetry — 系统遥测门面类（MOD-INF-015 v2.1.0）<br/>文件: system_telemetry/facade.py<br/>(生产态 / production)"]
    src_zephyr_trading_auto_runtime_core_py["trading/auto_runtime_core<br/>AutoRuntimeCore — 三层运行时运营中心（系统大脑）<br/>文件: trading/auto_runtime_core.py<br/>(生产态 / production)"]
    src_zephyr_data_tick_redis_cache_py ~~~ src_zephyr_infrastructure_asset_inventory_models_py
    src_zephyr_infrastructure_asset_inventory_models_py ~~~ src_zephyr_infrastructure_auto_fix_engine_batch_fixer_py
    src_zephyr_infrastructure_auto_fix_engine_batch_fixer_py ~~~ src_zephyr_infrastructure_auto_fix_engine_compliance_auditor_py
    src_zephyr_infrastructure_auto_fix_engine_compliance_auditor_py ~~~ src_zephyr_infrastructure_auto_fix_engine_escalation_bridge_py
    src_zephyr_infrastructure_auto_fix_engine_escalation_bridge_py ~~~ src_zephyr_infrastructure_auto_fix_engine_fix_health_check_py
    src_zephyr_infrastructure_auto_fix_engine_fix_health_check_py ~~~ src_zephyr_infrastructure_auto_fix_engine_fix_pattern_miner_py
    src_zephyr_infrastructure_auto_fix_engine_fix_pattern_miner_py ~~~ src_zephyr_infrastructure_auto_fix_engine_fix_report_py
    src_zephyr_infrastructure_auto_fix_engine_fix_report_py ~~~ src_zephyr_infrastructure_auto_fix_engine_fix_safety_py
    src_zephyr_infrastructure_auto_fix_engine_fix_safety_py ~~~ src_zephyr_infrastructure_auto_fix_engine_shadow_workspace_py
    src_zephyr_infrastructure_auto_fix_engine_shadow_workspace_py ~~~ src_zephyr_infrastructure_database_service_py
    src_zephyr_infrastructure_database_service_py ~~~ src_zephyr_infrastructure_pipeline_models_py
    src_zephyr_infrastructure_pipeline_models_py ~~~ src_zephyr_infrastructure_system_telemetry_facade_py
    src_zephyr_infrastructure_system_telemetry_facade_py ~~~ src_zephyr_trading_auto_runtime_core_py
    src_zephyr_infrastructure_auto_fix_engine_fix_budget_py["auto_fix_engine/fix_budget<br/>基础设施/auto fix engine包的fix_budget模块<br/>文件: auto_fix_engine/fix_budget.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_auto_fix_engine_fix_reliability_py["auto_fix_engine/fix_reliability<br/>基础设施/auto fix engine包的fix_reliability模块<br/>文件: auto_fix_engine/fix_reliability.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_file_watcher_py["infrastructure/file_watcher<br/>基础设施包的file_watcher模块<br/>文件: infrastructure/file_watcher.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_h1_redis_hot_h1_redis_schema_py["h1_redis_hot/h1_redis_schema<br/>H1 Redis 热缓存 Key Schema（DDL-as-Code）。<br/>文件: h1_redis_hot/h1_redis_schema.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_queue_task_queue_py["queue/task_queue<br/>Task Queue — 后台任务队列 + 自动 Dispatch。<br/>文件: queue/task_queue.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_redis_config_py["infrastructure/redis_config<br/>Redis 连接配置单真源加载器（H1 业务热缓存<br/>INFRA-DB-007）。<br/>文件: infrastructure/redis_config.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_system_telemetry_ai_behavior_event_sink_py["ai_behavior/event_sink<br/>遥测 · ai_behavior/event_sink — AI<br/>行为遥测事件管道。<br/>文件: ai_behavior/event_sink.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_system_telemetry_archive_cold_stub_py["archive/cold_stub<br/>遥测 · archive/cold_stub — 冷存储归档管道。<br/>文件: archive/cold_stub.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_system_telemetry_traces_span_stub_py["traces/span_stub<br/>遥测 · traces/span_stub — W3C TraceContext<br/>分布式追踪管道。<br/>文件: traces/span_stub.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_system_telemetry_watchdog_py["system_telemetry/watchdog<br/>三冗余 Watchdog（CT-WATCHDOG-001）——互检+Panic<br/>Mode+Dead Man's Switch。<br/>文件: system_telemetry/watchdog.py<br/>(生产态 / production)"]
    src_zephyr_trading_auto_integrator_py["trading/auto_integrator<br/>AutoIntegrator — 自动接入器<br/>文件: trading/auto_integrator.py<br/>(生产态 / production)"]
    src_zephyr_trading_boot_hooks_py["trading/boot_hooks<br/>交易包的boot_hooks模块<br/>文件: trading/boot_hooks.py<br/>(生产态 / production)"]
    src_zephyr_trading_capability_sync_py["trading/capability_sync<br/>交易包的capability_sync模块<br/>文件: trading/capability_sync.py<br/>(生产态 / production)"]
    src_zephyr_trading_lifecycle_manager_py["trading/lifecycle_manager<br/>交易包的lifecycle_manager模块<br/>文件: trading/lifecycle_manager.py<br/>(生产态 / production)"]
    src_zephyr_trading_status_dashboard_py["trading/status_dashboard<br/>StatusDashboard — 实时状态面板<br/>文件: trading/status_dashboard.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_auto_fix_engine_fix_budget_py ~~~ src_zephyr_infrastructure_auto_fix_engine_fix_reliability_py
    src_zephyr_infrastructure_auto_fix_engine_fix_reliability_py ~~~ src_zephyr_infrastructure_file_watcher_py
    src_zephyr_infrastructure_file_watcher_py ~~~ src_zephyr_infrastructure_h1_redis_hot_h1_redis_schema_py
    src_zephyr_infrastructure_h1_redis_hot_h1_redis_schema_py ~~~ src_zephyr_infrastructure_queue_task_queue_py
    src_zephyr_infrastructure_queue_task_queue_py ~~~ src_zephyr_infrastructure_redis_config_py
    src_zephyr_infrastructure_redis_config_py ~~~ src_zephyr_infrastructure_system_telemetry_ai_behavior_event_sink_py
    src_zephyr_infrastructure_system_telemetry_ai_behavior_event_sink_py ~~~ src_zephyr_infrastructure_system_telemetry_archive_cold_stub_py
    src_zephyr_infrastructure_system_telemetry_archive_cold_stub_py ~~~ src_zephyr_infrastructure_system_telemetry_traces_span_stub_py
    src_zephyr_infrastructure_system_telemetry_traces_span_stub_py ~~~ src_zephyr_infrastructure_system_telemetry_watchdog_py
    src_zephyr_infrastructure_system_telemetry_watchdog_py ~~~ src_zephyr_trading_auto_integrator_py
    src_zephyr_trading_auto_integrator_py ~~~ src_zephyr_trading_boot_hooks_py
    src_zephyr_trading_boot_hooks_py ~~~ src_zephyr_trading_capability_sync_py
    src_zephyr_trading_capability_sync_py ~~~ src_zephyr_trading_lifecycle_manager_py
    src_zephyr_trading_lifecycle_manager_py ~~~ src_zephyr_trading_status_dashboard_py
    src_zephyr_infrastructure_auto_fix_engine_models_py["auto_fix_engine/models<br/>基础设施/auto fix engine包的models模块<br/>文件: auto_fix_engine/models.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_observability_notifier_py["observability/notifier<br/>Notifier — 多渠道 Owner 通知。<br/>文件: observability/notifier.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_runtime_gate_coordinator_py["runtime/gate_coordinator<br/>Rollback->Gate 协调器 — freeze_all / thaw_all<br/>文件: runtime/gate_coordinator.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_sla_sla_monitor_py["sla/sla_monitor<br/>SLA Monitor — 服务等级协议 (SLA) 监控 RTO/RPO。<br/>文件: sla/sla_monitor.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_system_telemetry_health_aggregator_py["system_telemetry/health_aggregator<br/>健康聚合器（Health Aggregator）<br/>文件: system_telemetry/health_aggregator.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_system_telemetry_logs_structured_sink_py["logs/structured_sink<br/>结构化日志管道（D_SYSTEM_TELEMETRY）<br/>文件: logs/structured_sink.py<br/>(生产态 / production)"]
    src_zephyr_trading_ai_audit_logger_py["trading/ai_audit_logger<br/>AiAuditLogger — AI 行为审计日志<br/>文件: trading/ai_audit_logger.py<br/>(生产态 / production)"]
    src_zephyr_trading_dream_cycle_py["trading/dream_cycle<br/>DreamCycle — 知识固化引擎<br/>文件: trading/dream_cycle.py<br/>(生产态 / production)"]
    src_zephyr_trading_finalizer_py["trading/finalizer<br/>Finalizer — 优雅清理器<br/>文件: trading/finalizer.py<br/>(生产态 / production)"]
    src_zephyr_trading_health_monitor_py["trading/health_monitor<br/>HealthMonitor — 健康监控 + 自愈<br/>文件: trading/health_monitor.py<br/>(生产态 / production)"]
    src_zephyr_trading_integration_registry_py["trading/integration_registry<br/>IntegrationRegistry — 集成注册表<br/>文件: trading/integration_registry.py<br/>(生产态 / production)"]
    src_zephyr_trading_night_shift_queue_py["trading/night_shift_queue<br/>NightShiftQueue — 夜班登记表持久化<br/>文件: trading/night_shift_queue.py<br/>(生产态 / production)"]
    src_zephyr_trading_orphan_detector_py["trading/orphan_detector<br/>OrphanDetector — 孤儿检测器<br/>文件: trading/orphan_detector.py<br/>(生产态 / production)"]
    src_zephyr_trading_runtime_config_py["trading/runtime_config<br/>交易包的runtime_config模块<br/>文件: trading/runtime_config.py<br/>(生产态 / production)"]
    src_zephyr_trading_stop_gate_py["trading/stop_gate<br/>StopGate — 质量闸门<br/>文件: trading/stop_gate.py<br/>(生产态 / production)"]
    src_zephyr_trading_work_orchestrator_py["trading/work_orchestrator<br/>交易包的work_orchestrator模块<br/>文件: trading/work_orchestrator.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_auto_fix_engine_models_py ~~~ src_zephyr_infrastructure_observability_notifier_py
    src_zephyr_infrastructure_observability_notifier_py ~~~ src_zephyr_infrastructure_runtime_gate_coordinator_py
    src_zephyr_infrastructure_runtime_gate_coordinator_py ~~~ src_zephyr_infrastructure_sla_sla_monitor_py
    src_zephyr_infrastructure_sla_sla_monitor_py ~~~ src_zephyr_infrastructure_system_telemetry_health_aggregator_py
    src_zephyr_infrastructure_system_telemetry_health_aggregator_py ~~~ src_zephyr_infrastructure_system_telemetry_logs_structured_sink_py
    src_zephyr_infrastructure_system_telemetry_logs_structured_sink_py ~~~ src_zephyr_trading_ai_audit_logger_py
    src_zephyr_trading_ai_audit_logger_py ~~~ src_zephyr_trading_dream_cycle_py
    src_zephyr_trading_dream_cycle_py ~~~ src_zephyr_trading_finalizer_py
    src_zephyr_trading_finalizer_py ~~~ src_zephyr_trading_health_monitor_py
    src_zephyr_trading_health_monitor_py ~~~ src_zephyr_trading_integration_registry_py
    src_zephyr_trading_integration_registry_py ~~~ src_zephyr_trading_night_shift_queue_py
    src_zephyr_trading_night_shift_queue_py ~~~ src_zephyr_trading_orphan_detector_py
    src_zephyr_trading_orphan_detector_py ~~~ src_zephyr_trading_runtime_config_py
    src_zephyr_trading_runtime_config_py ~~~ src_zephyr_trading_stop_gate_py
    src_zephyr_trading_stop_gate_py ~~~ src_zephyr_trading_work_orchestrator_py
    src_zephyr_infrastructure_system_telemetry_trace_bridge_py["system_telemetry/_trace_bridge<br/>基础设施/system telemetry包的trace_bridge模块<br/>文件: system_telemetry/_trace_bridge.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_system_telemetry_health_probes_py["system_telemetry/health_probes<br/>三态健康探针协议（Health Probes —<br/>CT-HEALTH-001）<br/>文件: system_telemetry/health_probes.py<br/>(生产态 / production)"]
    src_zephyr_trading_module_onboarding_scanner_py["trading/module_onboarding_scanner<br/>ModuleOnboardingScanner — 模块接入扫描器<br/>文件: trading/module_onboarding_scanner.py<br/>(生产态 / production)"]
    src_zephyr_trading_resource_optimization_py["trading/resource_optimization<br/>resource_optimization.py - MAPE-K autonomic<br/>resource optimization engine<br/>文件: trading/resource_optimization.py<br/>(生产态 / production)"]
    src_zephyr_trading_work_dag_py["trading/work_dag<br/>WorkDAG + WorkItem — 工作编排数据模型<br/>文件: trading/work_dag.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_system_telemetry_trace_bridge_py ~~~ src_zephyr_infrastructure_system_telemetry_health_probes_py
    src_zephyr_infrastructure_system_telemetry_health_probes_py ~~~ src_zephyr_trading_module_onboarding_scanner_py
    src_zephyr_trading_module_onboarding_scanner_py ~~~ src_zephyr_trading_resource_optimization_py
    src_zephyr_trading_resource_optimization_py ~~~ src_zephyr_trading_work_dag_py
    src_zephyr_shared_lifecycle_daemon_registry_py["lifecycle/daemon_registry<br/>daemon_registry.py - unified daemon thread<br/>registry + resource guardian<br/>文件: lifecycle/daemon_registry.py<br/>(生产态 / production)"]
    src_zephyr_shared_lifecycle_lazy_loader_py["lifecycle/lazy_loader<br/>lazy_loader.py - Lazy module loading registry<br/>文件: lifecycle/lazy_loader.py<br/>(生产态 / production)"]
    src_zephyr_shared_lifecycle_resource_optimization_models_py["lifecycle/resource_optimization_models<br/>models.py - Pydantic data models for resource<br/>optimization engine<br/>文件: lifecycle/resource_optimization_models.py<br/>(生产态 / production)"]
    src_zephyr_trading_capability_registry_py["trading/capability_registry<br/>CapabilityRegistry — 能力注册中心<br/>文件: trading/capability_registry.py<br/>(生产态 / production)"]
    src_zephyr_shared_lifecycle_daemon_registry_py ~~~ src_zephyr_shared_lifecycle_lazy_loader_py
    src_zephyr_shared_lifecycle_lazy_loader_py ~~~ src_zephyr_shared_lifecycle_resource_optimization_models_py
    src_zephyr_shared_lifecycle_resource_optimization_models_py ~~~ src_zephyr_trading_capability_registry_py
    src_zephyr_trading_capability_card_py["trading/capability_card<br/>CapabilityCard — 能力卡片数据模型<br/>文件: trading/capability_card.py<br/>(生产态 / production)"]
    src_zephyr_data_tick_redis_cache_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_h1_redis_hot_h1_redis_schema_py
    src_zephyr_infrastructure_database_service_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_redis_config_py
    src_zephyr_infrastructure_warm_hot_gate_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_config_validator_py
    src_zephyr_infrastructure_warm_hot_gate_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_contract_tester_py
    src_zephyr_infrastructure_asset_inventory_dashboard_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_asset_inventory_models_py
    src_zephyr_infrastructure_asset_inventory_classifier_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_asset_inventory_models_py
    src_zephyr_infrastructure_asset_inventory_index_generator_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_asset_inventory_models_py
    src_zephyr_infrastructure_asset_inventory_lifecycle_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_asset_inventory_models_py
    src_zephyr_infrastructure_asset_inventory_reconciler_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_asset_inventory_models_py
    src_zephyr_infrastructure_asset_inventory_telemetry_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_system_telemetry_facade_py
    src_zephyr_infrastructure_asset_inventory_registry_adapter_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_asset_inventory_models_py
    src_zephyr_infrastructure_asset_inventory_scanner_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_asset_inventory_models_py
    src_zephyr_infrastructure_auto_fix_engine_alignment_syncer_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_asset_inventory_main_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_asset_inventory_dashboard_py
    src_zephyr_infrastructure_asset_inventory_main_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_asset_inventory_classifier_py
    src_zephyr_infrastructure_asset_inventory_main_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_asset_inventory_dependency_py
    src_zephyr_infrastructure_asset_inventory_main_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_asset_inventory_index_generator_py
    src_zephyr_infrastructure_asset_inventory_main_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_asset_inventory_reconciler_py
    src_zephyr_infrastructure_asset_inventory_main_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_asset_inventory_telemetry_py
    src_zephyr_infrastructure_asset_inventory_main_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_asset_inventory_registry_adapter_py
    src_zephyr_infrastructure_asset_inventory_main_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_asset_inventory_models_py
    src_zephyr_infrastructure_asset_inventory_main_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_asset_inventory_scanner_py
    src_zephyr_infrastructure_auto_fix_engine_batch_fixer_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_fix_budget_py
    src_zephyr_infrastructure_auto_fix_engine_batch_fixer_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_fix_reliability_py
    src_zephyr_infrastructure_auto_fix_engine_batch_fixer_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_drift_fixer_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_all_completer_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_dedup_extractor_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_compliance_auditor_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_escalation_bridge_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_config_fixer_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_fix_budget_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_dep_version_fixer_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_fix_diff_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_engine_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_batch_fixer_py
    src_zephyr_infrastructure_auto_fix_engine_engine_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_compliance_auditor_py
    src_zephyr_infrastructure_auto_fix_engine_engine_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_escalation_bridge_py
    src_zephyr_infrastructure_auto_fix_engine_engine_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_fix_budget_py
    src_zephyr_infrastructure_auto_fix_engine_engine_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_fix_health_check_py
    src_zephyr_infrastructure_auto_fix_engine_engine_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_fix_reliability_py
    src_zephyr_infrastructure_auto_fix_engine_engine_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_fix_pattern_miner_py
    src_zephyr_infrastructure_auto_fix_engine_engine_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_fix_report_py
    src_zephyr_infrastructure_auto_fix_engine_engine_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_engine_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_fix_safety_py
    src_zephyr_infrastructure_auto_fix_engine_engine_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_shadow_workspace_py
    src_zephyr_infrastructure_auto_fix_engine_event_hooks_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_engine_py
    src_zephyr_infrastructure_auto_fix_engine_event_hooks_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_fix_health_check_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_fix_reliability_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_fix_pattern_miner_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_scaffold_registrar_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_fix_scheduler_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_fix_report_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_fix_safety_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_llm_fix_adapter_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_llm_fix_adapter_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_fix_safety_py
    src_zephyr_infrastructure_auto_fix_engine_import_fixer_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_shadow_workspace_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_zombie_cleaner_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_self_heal_agent_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_main_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_engine_py
    src_zephyr_infrastructure_budget_enforcement_init_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_budget_enforcement_rbac_bridge_py
    src_zephyr_infrastructure_capacity_assurance_contracts_contract_bus_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_capacity_assurance_contracts_batch3_integration_py
    src_zephyr_infrastructure_capacity_assurance_contracts_contract_bus_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_capacity_assurance_contracts_batch1_infra_py
    src_zephyr_infrastructure_h1_redis_hot_h1_integration_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_h1_redis_hot_h1_redis_reader_py
    src_zephyr_infrastructure_h1_redis_hot_h1_integration_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_h1_redis_hot_h1_redis_writer_py
    src_zephyr_infrastructure_h1_redis_hot_h1_cqrs_projectors_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_h1_redis_hot_h1_redis_schema_py
    src_zephyr_infrastructure_h1_redis_hot_h1_redis_reader_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_h1_redis_hot_h1_redis_schema_py
    src_zephyr_infrastructure_h1_redis_hot_h1_redis_writer_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_h1_redis_hot_h1_redis_schema_py
    src_zephyr_infrastructure_pipeline_backpressure_manager_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_pipeline_backpressure_types_py
    src_zephyr_infrastructure_pipeline_circuit_breaker_manager_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_pipeline_models_py
    src_zephyr_infrastructure_pipeline_cost_tracker_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_pipeline_model_router_py
    src_zephyr_infrastructure_pipeline_cost_tracker_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_pipeline_models_py
    src_zephyr_infrastructure_pipeline_dead_letter_queue_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_pipeline_models_py
    src_zephyr_infrastructure_pipeline_ct_pipe_routing_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_pipeline_models_py
    src_zephyr_infrastructure_pipeline_pipeline_agent_bridge_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_pipeline_models_py
    src_zephyr_infrastructure_pipeline_routing_plugins_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_pipeline_ct_pipe_routing_py
    src_zephyr_infrastructure_pipeline_routing_plugins_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_pipeline_models_py
    src_zephyr_infrastructure_pipeline_preemption_manager_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_pipeline_models_py
    src_zephyr_infrastructure_system_telemetry_facade_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_system_telemetry_health_aggregator_py
    src_zephyr_infrastructure_system_telemetry_facade_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_system_telemetry_watchdog_py
    src_zephyr_infrastructure_system_telemetry_facade_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_system_telemetry_ai_behavior_event_sink_py
    src_zephyr_infrastructure_system_telemetry_facade_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_system_telemetry_archive_cold_stub_py
    src_zephyr_infrastructure_system_telemetry_facade_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_system_telemetry_traces_span_stub_py
    src_zephyr_infrastructure_system_telemetry_auto_bootstrap_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_system_telemetry_contract_metrics_py
    src_zephyr_infrastructure_system_telemetry_auto_bootstrap_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_system_telemetry_facade_py
    src_zephyr_infrastructure_system_telemetry_auto_bootstrap_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_system_telemetry_budget_telemetry_bridge_py
    src_zephyr_infrastructure_system_telemetry_auto_bootstrap_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_system_telemetry_metrics_blueprint_metrics_py
    src_zephyr_infrastructure_system_telemetry_health_aggregator_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_system_telemetry_health_probes_py
    src_zephyr_infrastructure_system_telemetry_ai_behavior_event_sink_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_system_telemetry_logs_structured_sink_py
    src_zephyr_infrastructure_system_telemetry_logs_init_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_system_telemetry_logs_structured_sink_py
    src_zephyr_infrastructure_system_telemetry_traces_span_stub_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_system_telemetry_trace_bridge_py
    src_zephyr_infrastructure_system_telemetry_logs_structured_sink_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_system_telemetry_trace_bridge_py
    src_zephyr_runtime_intraday_main_py -->|导入依赖 / import_depends| src_zephyr_data_tick_redis_cache_py
    src_zephyr_runtime_intraday_main_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_database_service_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_file_watcher_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_queue_task_queue_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_trading_ai_audit_logger_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_trading_auto_integrator_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_trading_capability_registry_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_trading_boot_hooks_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_trading_dream_cycle_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_trading_capability_sync_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_trading_health_monitor_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_trading_finalizer_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_trading_module_onboarding_scanner_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_trading_night_shift_queue_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_trading_integration_registry_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_trading_orphan_detector_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_trading_lifecycle_manager_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_trading_resource_optimization_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_trading_runtime_config_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_trading_status_dashboard_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_trading_stop_gate_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_trading_work_dag_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_trading_work_orchestrator_py
    src_zephyr_trading_action_dispatcher_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_queue_task_scheduler_py
    src_zephyr_trading_auto_integrator_py -->|导入依赖 / import_depends| src_zephyr_trading_capability_card_py
    src_zephyr_trading_auto_integrator_py -->|导入依赖 / import_depends| src_zephyr_trading_capability_registry_py
    src_zephyr_trading_auto_integrator_py -->|导入依赖 / import_depends| src_zephyr_trading_module_onboarding_scanner_py
    src_zephyr_trading_capability_registry_py -->|导入依赖 / import_depends| src_zephyr_trading_capability_card_py
    src_zephyr_trading_boot_hooks_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_observability_notifier_py
    src_zephyr_trading_boot_hooks_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_runtime_gate_coordinator_py
    src_zephyr_trading_boot_hooks_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_sla_sla_monitor_py
    src_zephyr_trading_boot_hooks_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_system_telemetry_health_aggregator_py
    src_zephyr_trading_boot_hooks_py -->|导入依赖 / import_depends| src_zephyr_trading_finalizer_py
    src_zephyr_trading_capability_sync_py -->|导入依赖 / import_depends| src_zephyr_trading_capability_card_py
    src_zephyr_trading_capability_sync_py -->|导入依赖 / import_depends| src_zephyr_trading_capability_registry_py
    src_zephyr_trading_health_monitor_py -->|导入依赖 / import_depends| src_zephyr_trading_resource_optimization_py
    src_zephyr_trading_module_onboarding_scanner_py -->|导入依赖 / import_depends| src_zephyr_trading_capability_registry_py
    src_zephyr_trading_orphan_detector_py -->|导入依赖 / import_depends| src_zephyr_trading_capability_registry_py
    src_zephyr_trading_orphan_detector_py -->|导入依赖 / import_depends| src_zephyr_trading_module_onboarding_scanner_py
    src_zephyr_trading_lifecycle_manager_py -->|导入依赖 / import_depends| src_zephyr_trading_ai_audit_logger_py
    src_zephyr_trading_lifecycle_manager_py -->|导入依赖 / import_depends| src_zephyr_trading_capability_registry_py
    src_zephyr_trading_lifecycle_manager_py -->|导入依赖 / import_depends| src_zephyr_trading_dream_cycle_py
    src_zephyr_trading_lifecycle_manager_py -->|导入依赖 / import_depends| src_zephyr_trading_health_monitor_py
    src_zephyr_trading_lifecycle_manager_py -->|导入依赖 / import_depends| src_zephyr_trading_finalizer_py
    src_zephyr_trading_lifecycle_manager_py -->|导入依赖 / import_depends| src_zephyr_trading_night_shift_queue_py
    src_zephyr_trading_lifecycle_manager_py -->|导入依赖 / import_depends| src_zephyr_trading_integration_registry_py
    src_zephyr_trading_lifecycle_manager_py -->|导入依赖 / import_depends| src_zephyr_trading_runtime_config_py
    src_zephyr_trading_lifecycle_manager_py -->|导入依赖 / import_depends| src_zephyr_trading_stop_gate_py
    src_zephyr_trading_lifecycle_manager_py -->|导入依赖 / import_depends| src_zephyr_trading_work_orchestrator_py
    src_zephyr_trading_resource_optimization_py -->|导入依赖 / import_depends| src_zephyr_shared_lifecycle_daemon_registry_py
    src_zephyr_trading_resource_optimization_py -->|导入依赖 / import_depends| src_zephyr_shared_lifecycle_lazy_loader_py
    src_zephyr_trading_resource_optimization_py -->|导入依赖 / import_depends| src_zephyr_shared_lifecycle_resource_optimization_models_py
    src_zephyr_trading_status_dashboard_py -->|导入依赖 / import_depends| src_zephyr_trading_capability_registry_py
    src_zephyr_trading_status_dashboard_py -->|导入依赖 / import_depends| src_zephyr_trading_health_monitor_py
    src_zephyr_trading_status_dashboard_py -->|导入依赖 / import_depends| src_zephyr_trading_night_shift_queue_py
    src_zephyr_trading_status_dashboard_py -->|导入依赖 / import_depends| src_zephyr_trading_orphan_detector_py
    src_zephyr_trading_status_dashboard_py -->|导入依赖 / import_depends| src_zephyr_trading_work_orchestrator_py
    src_zephyr_trading_windows_service_py -->|导入依赖 / import_depends| src_zephyr_trading_auto_runtime_core_py
    src_zephyr_trading_windows_service_py -->|导入依赖 / import_depends| src_zephyr_trading_runtime_config_py
    src_zephyr_trading_windows_service_py -->|导入依赖 / import_depends| src_zephyr_trading_main_py
    src_zephyr_trading_main_py -->|导入依赖 / import_depends| src_zephyr_trading_auto_runtime_core_py
    src_zephyr_trading_main_py -->|导入依赖 / import_depends| src_zephyr_trading_runtime_config_py
    src_zephyr_trading_work_orchestrator_py -->|导入依赖 / import_depends| src_zephyr_trading_capability_registry_py
    src_zephyr_trading_work_orchestrator_py -->|导入依赖 / import_depends| src_zephyr_trading_work_dag_py
    tests_zephyr_data_test_tick_redis_cache_py -->|测试依赖 / test_depends| src_zephyr_data_tick_redis_cache_py
    tests_zephyr_data_test_tick_redis_cache_py -->|测试依赖 / test_depends| src_zephyr_infrastructure_h1_redis_hot_h1_redis_schema_py
    tests_zephyr_runtime_test_intraday_main_py -->|测试依赖 / test_depends| src_zephyr_runtime_intraday_main_py
    D_GOV_OPS_RESILIENCE["运维弹性治理<br/>运维弹性治理，负责运维治理、安全治理、弹性治理和<br/>升级协议<br/>Ops Resilience Governance<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_infrastructure_system_telemetry_auto_bootstrap_py -->|导入依赖 / import_depends| D_GOV_OPS_RESILIENCE
    D_SHARED["共享服务<br/>共享服务，负责跨域共享的工具、协议和基础服务<br/>Shared Services<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_trading_health_monitor_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_infrastructure_auto_fix_engine_llm_fix_adapter_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_trading_work_orchestrator_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_trading_work_orchestrator_py -->|导入依赖 / import_depends| D_SHARED
    D_INTELLIGENCE["上下文管理<br/>上下文管理，负责 AI<br/>上下文窗口管理、记忆检索和上下文压缩<br/>Context Management<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| D_INTELLIGENCE
    D_GOVERNANCE["生命周期管理<br/>生命周期管理，负责蓝图/模块<br/>/任务的声明周期管理和元数据治理<br/>Lifecycle Management<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_infrastructure_database_service_py -->|导入依赖 / import_depends| D_GOVERNANCE
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| D_SHARED
    D_SECURITY["对抗验证<br/>对抗验证，负责系统安全对抗测试、漏洞扫描和攻防验<br/>证<br/>Adversarial Validation<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_trading_boot_hooks_py -->|导入依赖 / import_depends| D_SECURITY
    src_zephyr_infrastructure_observability_notifier_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_infrastructure_event_bus_upgrade_py -->|导入依赖 / import_depends| D_SHARED
    D_INTEGRATION["管线路由<br/>管线路由，负责跨域数据流路由、管道编排和集成适配<br/>Pipeline Routing<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_trading_auto_task_generator_py -->|导入依赖 / import_depends| D_INTEGRATION
    src_zephyr_infrastructure_file_watcher_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_trading_auto_task_generator_py -->|导入依赖 / import_depends| D_SHARED
    D_INTEGRATION -->|导入依赖 / import_depends| src_zephyr_infrastructure_pipeline_models_py
    D_GOV_SCRIPTS["脚本治理<br/>脚本治理，负责脚本生命周期管理和脚本质量门禁<br/>Script Governance<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    D_GOV_SCRIPTS -->|导入依赖 / import_depends| src_zephyr_infrastructure_finding_task_bridge_py
    D_GOV_SCRIPTS -->|导入依赖 / import_depends| src_zephyr_infrastructure_system_telemetry_metrics_blueprint_metrics_py
    D_GOV_SCRIPTS -->|导入依赖 / import_depends| src_zephyr_infrastructure_script_system_finding_py
    D_ORCHESTRATOR["代理编排器<br/>代理编排器，负责 Agent<br/>任务全生命周期：任务入队、调度、沙箱执行、幻觉检<br/>测和收尾归档<br/>Agent Orchestrator<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    D_ORCHESTRATOR -->|导入依赖 / import_depends| src_zephyr_infrastructure_script_system_gate_bridge_py
    D_INFRA_RECOVERY["回滚恢复<br/>回滚恢复，负责系统故障时的状态回滚、事务补偿和恢<br/>复编排<br/>Rollback Recovery<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    D_INFRA_RECOVERY -->|导入依赖 / import_depends| src_zephyr_infrastructure_runtime_concurrency_guard_py
    D_FEEDBACK_LOOP["反馈循环引擎<br/>反馈循环引擎，负责系统自我改进闭环：异常检测、根<br/>因诊断、自动修复和自我进化<br/>Feedback Loop Engine<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    D_FEEDBACK_LOOP -->|导入依赖 / import_depends| src_zephyr_infrastructure_system_telemetry_metrics_bridge_py
    D_FEEDBACK_LOOP -->|导入依赖 / import_depends| src_zephyr_infrastructure_system_telemetry_metrics_bridge_py
    D_AUTONOMY_CORE["自治核心<br/>自治核心，负责 AI 自治决策、目标分解和执行编排<br/>Autonomy Core<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    D_AUTONOMY_CORE -->|测试依赖 / test_depends| src_zephyr_infrastructure_pipeline_models_py
    D_INTEGRATION -->|导入依赖 / import_depends| src_zephyr_infrastructure_pipeline_pipeline_lock_py
    D_INTEGRATION -->|导入依赖 / import_depends| src_zephyr_infrastructure_pipeline_preemption_manager_py
    D_INTEGRATION -->|导入依赖 / import_depends| src_zephyr_trading_resource_optimization_py
    D_GOVERNANCE -->|导入依赖 / import_depends| src_zephyr_infrastructure_database_service_py
    D_INTEGRATION -->|导入依赖 / import_depends| src_zephyr_infrastructure_pipeline_cost_tracker_py
    D_INTEGRATION -->|导入依赖 / import_depends| src_zephyr_infrastructure_pipeline_dead_letter_queue_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class docs_01_policies_and_standards_registry_catalogs_infrastructure_registry_yaml_INFRA_DB_001,docs_01_policies_and_standards_registry_catalogs_infrastructure_registry_yaml_INFRA_DB_002,docs_01_policies_and_standards_registry_catalogs_infrastructure_registry_yaml_INFRA_DB_003,docs_01_policies_and_standards_registry_catalogs_infrastructure_registry_yaml_INFRA_DB_006,src_zephyr_data_tick_redis_cache_py,src_zephyr_infrastructure_asset_inventory_main_py,src_zephyr_infrastructure_asset_inventory_classifier_py,src_zephyr_infrastructure_asset_inventory_dashboard_py,src_zephyr_infrastructure_asset_inventory_dependency_py,src_zephyr_infrastructure_asset_inventory_index_generator_py,src_zephyr_infrastructure_asset_inventory_lifecycle_py,src_zephyr_infrastructure_asset_inventory_mcp_server_py,src_zephyr_infrastructure_asset_inventory_metadata_py,src_zephyr_infrastructure_asset_inventory_models_py,src_zephyr_infrastructure_asset_inventory_reconciler_py,src_zephyr_infrastructure_asset_inventory_registry_adapter_py,src_zephyr_infrastructure_asset_inventory_scanner_py,src_zephyr_infrastructure_asset_inventory_telemetry_py,src_zephyr_infrastructure_asset_inventory_trust_anchor_py,src_zephyr_infrastructure_auto_diagnostics_py,src_zephyr_infrastructure_auto_fix_engine_main_py,src_zephyr_infrastructure_auto_fix_engine_alignment_syncer_py,src_zephyr_infrastructure_auto_fix_engine_all_completer_py,src_zephyr_infrastructure_auto_fix_engine_batch_fixer_py,src_zephyr_infrastructure_auto_fix_engine_compliance_auditor_py,src_zephyr_infrastructure_auto_fix_engine_config_fixer_py,src_zephyr_infrastructure_auto_fix_engine_dedup_extractor_py,src_zephyr_infrastructure_auto_fix_engine_dep_version_fixer_py,src_zephyr_infrastructure_auto_fix_engine_drift_fixer_py,src_zephyr_infrastructure_auto_fix_engine_engine_py,src_zephyr_infrastructure_auto_fix_engine_escalation_bridge_py,src_zephyr_infrastructure_auto_fix_engine_event_hooks_py,src_zephyr_infrastructure_auto_fix_engine_fix_budget_py,src_zephyr_infrastructure_auto_fix_engine_fix_diff_py,src_zephyr_infrastructure_auto_fix_engine_fix_health_check_py,src_zephyr_infrastructure_auto_fix_engine_fix_pattern_miner_py,src_zephyr_infrastructure_auto_fix_engine_fix_reliability_py,src_zephyr_infrastructure_auto_fix_engine_fix_report_py,src_zephyr_infrastructure_auto_fix_engine_fix_safety_py,src_zephyr_infrastructure_auto_fix_engine_fix_scheduler_py,src_zephyr_infrastructure_auto_fix_engine_import_fixer_py,src_zephyr_infrastructure_auto_fix_engine_interrupt_guard_py,src_zephyr_infrastructure_auto_fix_engine_llm_fix_adapter_py,src_zephyr_infrastructure_auto_fix_engine_models_py,src_zephyr_infrastructure_auto_fix_engine_scaffold_registrar_py,src_zephyr_infrastructure_auto_fix_engine_self_heal_agent_py,src_zephyr_infrastructure_auto_fix_engine_shadow_workspace_py,src_zephyr_infrastructure_auto_fix_engine_state_machine_py,src_zephyr_infrastructure_auto_fix_engine_zombie_cleaner_py,src_zephyr_infrastructure_blueprint_code_sync_py,src_zephyr_infrastructure_budget_enforcement_init_py,src_zephyr_infrastructure_budget_enforcement_rbac_bridge_py,src_zephyr_infrastructure_capacity_assurance_budget_forecaster_py,src_zephyr_infrastructure_capacity_assurance_contracts_batch1_infra_py,src_zephyr_infrastructure_capacity_assurance_contracts_batch3_integration_py,src_zephyr_infrastructure_capacity_assurance_contracts_contract_bus_py,src_zephyr_infrastructure_capacity_assurance_cross_module_integration_py,src_zephyr_infrastructure_capacity_assurance_host_resource_governor_py,src_zephyr_infrastructure_capacity_assurance_kill_switch_py,src_zephyr_infrastructure_capacity_assurance_risk_mitigation_py,src_zephyr_infrastructure_capacity_assurance_schema_py,src_zephyr_infrastructure_capacity_assurance_sli_instrumentation_py,src_zephyr_infrastructure_capacity_assurance_tech_stack_py,src_zephyr_infrastructure_capacity_assurance_token_budget_py,src_zephyr_infrastructure_config_validator_py,src_zephyr_infrastructure_contract_tester_py,src_zephyr_infrastructure_cost_tracker_py,src_zephyr_infrastructure_database_service_py,src_zephyr_infrastructure_dry_run_simulator_py,src_zephyr_infrastructure_event_bus_upgrade_py,src_zephyr_infrastructure_event_store_py,src_zephyr_infrastructure_events_event_store_py,src_zephyr_infrastructure_file_watcher_py,src_zephyr_infrastructure_finding_task_bridge_py,src_zephyr_infrastructure_git_batcher_py,src_zephyr_infrastructure_h1_redis_hot_init_py,src_zephyr_infrastructure_h1_redis_hot_h1_cqrs_projectors_py,src_zephyr_infrastructure_h1_redis_hot_h1_integration_py,src_zephyr_infrastructure_h1_redis_hot_h1_redis_reader_py,src_zephyr_infrastructure_h1_redis_hot_h1_redis_schema_py,src_zephyr_infrastructure_h1_redis_hot_h1_redis_writer_py,src_zephyr_infrastructure_health_monitor_health_aggregator_py,src_zephyr_infrastructure_hooks_event_hook_py,src_zephyr_infrastructure_impact_impact_propagator_py,src_zephyr_infrastructure_impact_llm_impact_analyzer_py,src_zephyr_infrastructure_infrastructure_base_py,src_zephyr_infrastructure_kill_switch_sim_py,src_zephyr_infrastructure_lifecycle_scope_guard_py,src_zephyr_infrastructure_lifecycle_task_lifecycle_manager_py,src_zephyr_infrastructure_observability_notifier_py,src_zephyr_infrastructure_observability_trace_decorator_py,src_zephyr_infrastructure_pipeline_backpressure_manager_py,src_zephyr_infrastructure_pipeline_backpressure_types_py,src_zephyr_infrastructure_pipeline_circuit_breaker_manager_py,src_zephyr_infrastructure_pipeline_cost_tracker_py,src_zephyr_infrastructure_pipeline_ct_pipe_routing_py,src_zephyr_infrastructure_pipeline_dead_letter_queue_py,src_zephyr_infrastructure_pipeline_llm_gateway_py,src_zephyr_infrastructure_pipeline_model_router_py,src_zephyr_infrastructure_pipeline_models_py,src_zephyr_infrastructure_pipeline_pipeline_agent_bridge_py,src_zephyr_infrastructure_pipeline_pipeline_lock_py,src_zephyr_infrastructure_pipeline_pipeline_roadmap_py,src_zephyr_infrastructure_pipeline_preemption_manager_py,src_zephyr_infrastructure_pipeline_routing_plugins_py,src_zephyr_infrastructure_pydantic_v2_migrator_py,src_zephyr_infrastructure_quality_quality_monitor_py,src_zephyr_infrastructure_queue_task_queue_py,src_zephyr_infrastructure_queue_task_scheduler_py,src_zephyr_infrastructure_redis_config_py,src_zephyr_infrastructure_reliability_circuit_breaker_py,src_zephyr_infrastructure_reliability_context_guard_py,src_zephyr_infrastructure_runtime_concurrency_guard_py,src_zephyr_infrastructure_runtime_gate_coordinator_py,src_zephyr_infrastructure_runtime_sandbox_enforcer_py,src_zephyr_infrastructure_runtime_startup_shutdown_py,src_zephyr_infrastructure_script_system_finding_py,src_zephyr_infrastructure_script_system_gate_bridge_py,src_zephyr_infrastructure_sla_sla_monitor_py,src_zephyr_infrastructure_system_telemetry_budget_telemetry_bridge_py,src_zephyr_infrastructure_system_telemetry_trace_bridge_py,src_zephyr_infrastructure_system_telemetry_ai_behavior_event_sink_py,src_zephyr_infrastructure_system_telemetry_archive_cold_stub_py,src_zephyr_infrastructure_system_telemetry_auto_bootstrap_py,src_zephyr_infrastructure_system_telemetry_contract_metrics_py,src_zephyr_infrastructure_system_telemetry_facade_py,src_zephyr_infrastructure_system_telemetry_health_aggregator_py,src_zephyr_infrastructure_system_telemetry_health_probes_py,src_zephyr_infrastructure_system_telemetry_logs_init_py,src_zephyr_infrastructure_system_telemetry_logs_structured_sink_py,src_zephyr_infrastructure_system_telemetry_metrics_blueprint_metrics_py,src_zephyr_infrastructure_system_telemetry_metrics_bridge_py,src_zephyr_infrastructure_system_telemetry_traces_span_stub_py,src_zephyr_infrastructure_system_telemetry_watchdog_py,src_zephyr_infrastructure_warm_hot_gate_py,src_zephyr_runtime_intraday_main_py,src_zephyr_shared_lifecycle_daemon_registry_py,src_zephyr_shared_lifecycle_hooks_py,src_zephyr_shared_lifecycle_lazy_loader_py,src_zephyr_shared_lifecycle_resource_optimization_models_py,src_zephyr_trading_main_py,src_zephyr_trading_action_dispatcher_py,src_zephyr_trading_ai_audit_logger_py,src_zephyr_trading_auto_integrator_py,src_zephyr_trading_auto_runtime_core_py,src_zephyr_trading_auto_task_generator_py,src_zephyr_trading_boot_hooks_py,src_zephyr_trading_capability_card_py,src_zephyr_trading_capability_registry_py,src_zephyr_trading_capability_sync_py,src_zephyr_trading_dream_cycle_py,src_zephyr_trading_finalizer_py,src_zephyr_trading_health_monitor_py,src_zephyr_trading_integration_registry_py,src_zephyr_trading_lifecycle_manager_py,src_zephyr_trading_module_onboarding_scanner_py,src_zephyr_trading_night_shift_queue_py,src_zephyr_trading_orphan_detector_py,src_zephyr_trading_ports_py,src_zephyr_trading_resource_optimization_py,src_zephyr_trading_runtime_config_py,src_zephyr_trading_staging_area_py,src_zephyr_trading_status_dashboard_py,src_zephyr_trading_stop_gate_py,src_zephyr_trading_task_gate_py,src_zephyr_trading_windows_service_py,src_zephyr_trading_work_dag_py,src_zephyr_trading_work_orchestrator_py,src_zephyr_trading_zombie_scanner_py,tests_zephyr_data_test_tick_redis_cache_py,tests_zephyr_runtime_test_intraday_main_py production
    class docs_03_modules_cross_layer_agent_orchestrator_blueprint_md design
    class D_GOV_OPS_RESILIENCE,D_SHARED,D_INTELLIGENCE,D_GOVERNANCE,D_SECURITY,D_INTEGRATION,D_GOV_SCRIPTS,D_ORCHESTRATOR,D_INFRA_RECOVERY,D_FEEDBACK_LOOP,D_AUTONOMY_CORE external_prod
```

### 运营态的图（仅 design_maturity=production 的模块和域内依赖）

> 仅展示已上线运行的模块（共 171 个），不含跨域外部节点。跨域依赖见下方跨域依赖章节。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    docs_01_policies_and_standards_registry_catalogs_infrastructure_registry_yaml_INFRA_DB_001["catalogs/infrastructure_registry<br/>infrastructure_registry的INFRA-DB-001条目模块<br/>文件: catalogs<br/>/infrastructure_registry.yaml#INFRA-DB-001<br/>(生产态 / production)"]
    docs_01_policies_and_standards_registry_catalogs_infrastructure_registry_yaml_INFRA_DB_002["catalogs/infrastructure_registry<br/>infrastructure_registry的INFRA-DB-002条目模块<br/>文件: catalogs<br/>/infrastructure_registry.yaml#INFRA-DB-002<br/>(生产态 / production)"]
    docs_01_policies_and_standards_registry_catalogs_infrastructure_registry_yaml_INFRA_DB_003["catalogs/infrastructure_registry<br/>infrastructure_registry的INFRA-DB-003条目模块<br/>文件: catalogs<br/>/infrastructure_registry.yaml#INFRA-DB-003<br/>(生产态 / production)"]
    docs_01_policies_and_standards_registry_catalogs_infrastructure_registry_yaml_INFRA_DB_006["catalogs/infrastructure_registry<br/>infrastructure_registry的INFRA-DB-006条目模块<br/>文件: catalogs<br/>/infrastructure_registry.yaml#INFRA-DB-006<br/>(生产态 / production)"]
    src_zephyr_infrastructure_asset_inventory_main_py["asset_inventory/__main__<br/>Asset Inventory CLI — MOD-INF-026 蓝图 §31<br/>文件: asset_inventory/__main__.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_asset_inventory_lifecycle_py["asset_inventory/lifecycle<br/>AssetLifecycle — MOD-INF-026 L5<br/>ITIL生命周期自动化管理器<br/>文件: asset_inventory/lifecycle.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_asset_inventory_mcp_server_py["asset_inventory/mcp_server<br/>AssetInventory MCP Server — MOD-INF-026 蓝图 §21<br/>文件: asset_inventory/mcp_server.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_asset_inventory_metadata_py["asset_inventory/metadata<br/>基础设施/asset inventory包的metadata模块<br/>文件: asset_inventory/metadata.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_asset_inventory_trust_anchor_py["asset_inventory/trust_anchor<br/>基础设施/asset inventory包的trust_anchor模块<br/>文件: asset_inventory/trust_anchor.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_auto_diagnostics_py["infrastructure/auto_diagnostics<br/>RI-12 AutoDiagnostics — 自动诊断引擎<br/>文件: infrastructure/auto_diagnostics.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_auto_fix_engine_main_py["auto_fix_engine/__main__<br/>基础设施/auto fix engine包的main__模块<br/>文件: auto_fix_engine/__main__.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_auto_fix_engine_alignment_syncer_py["auto_fix_engine/alignment_syncer<br/>基础设施/auto fix engine包的alignment_syncer模块<br/>文件: auto_fix_engine/alignment_syncer.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_auto_fix_engine_all_completer_py["auto_fix_engine/all_completer<br/>基础设施/auto fix engine包的all_completer模块<br/>文件: auto_fix_engine/all_completer.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_auto_fix_engine_config_fixer_py["auto_fix_engine/config_fixer<br/>基础设施/auto fix engine包的config_fixer模块<br/>文件: auto_fix_engine/config_fixer.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_auto_fix_engine_dedup_extractor_py["auto_fix_engine/dedup_extractor<br/>基础设施/auto fix engine包的dedup_extractor模块<br/>文件: auto_fix_engine/dedup_extractor.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_auto_fix_engine_dep_version_fixer_py["auto_fix_engine/dep_version_fixer<br/>基础设施/auto fix<br/>engine包的dep_version_fixer模块<br/>文件: auto_fix_engine/dep_version_fixer.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_auto_fix_engine_drift_fixer_py["auto_fix_engine/drift_fixer<br/>基础设施/auto fix engine包的drift_fixer模块<br/>文件: auto_fix_engine/drift_fixer.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_auto_fix_engine_event_hooks_py["auto_fix_engine/event_hooks<br/>基础设施/auto fix engine包的event_hooks模块<br/>文件: auto_fix_engine/event_hooks.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_auto_fix_engine_fix_diff_py["auto_fix_engine/fix_diff<br/>基础设施/auto fix engine包的fix_diff模块<br/>文件: auto_fix_engine/fix_diff.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_auto_fix_engine_fix_scheduler_py["auto_fix_engine/fix_scheduler<br/>基础设施/auto fix engine包的fix_scheduler模块<br/>文件: auto_fix_engine/fix_scheduler.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_auto_fix_engine_import_fixer_py["auto_fix_engine/import_fixer<br/>基础设施/auto fix engine包的import_fixer模块<br/>文件: auto_fix_engine/import_fixer.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_auto_fix_engine_interrupt_guard_py["auto_fix_engine/interrupt_guard<br/>基础设施/auto fix engine包的interrupt_guard模块<br/>文件: auto_fix_engine/interrupt_guard.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_auto_fix_engine_llm_fix_adapter_py["auto_fix_engine/llm_fix_adapter<br/>基础设施/auto fix engine包的llm_fix_adapter模块<br/>文件: auto_fix_engine/llm_fix_adapter.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_auto_fix_engine_scaffold_registrar_py["auto_fix_engine/scaffold_registrar<br/>基础设施/auto fix<br/>engine包的scaffold_registrar模块<br/>文件: auto_fix_engine/scaffold_registrar.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_auto_fix_engine_self_heal_agent_py["auto_fix_engine/self_heal_agent<br/>基础设施/auto fix engine包的self_heal_agent模块<br/>文件: auto_fix_engine/self_heal_agent.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_auto_fix_engine_state_machine_py["auto_fix_engine/state_machine<br/>基础设施/auto fix engine包的state_machine模块<br/>文件: auto_fix_engine/state_machine.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_auto_fix_engine_zombie_cleaner_py["auto_fix_engine/zombie_cleaner<br/>基础设施/auto fix engine包的zombie_cleaner模块<br/>文件: auto_fix_engine/zombie_cleaner.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_blueprint_code_sync_py["infrastructure/blueprint_code_sync<br/>Blueprint-Code Sync — 蓝图-代码索引同步验证。<br/>文件: infrastructure/blueprint_code_sync.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_budget_enforcement_init_py["infrastructure/budget_enforcement 包入口<br/>budget_enforcement 包聚合层。<br/>文件: budget_enforcement/__init__.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_capacity_assurance_budget_forecaster_py["capacity_assurance/budget_forecaster<br/>budget_forecaster.py — Token 预算预测<br/>(DD120-extra, TASK-020)<br/>文件: capacity_assurance/budget_forecaster.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_capacity_assurance_contracts_contract_bus_py["contracts/contract_bus<br/>ContractBus loader —<br/>加载全部44条容量保障契约的Pydantic v2 Schema<br/>（DD-9三批...<br/>文件: contracts/contract_bus.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_capacity_assurance_cross_module_integration_py["capacity_assurance/cross_module_integration<br/>Cross-module integration — CT-1~CT-4<br/>跨模块集成契约实现（对标蓝图 §17）.<br/>文件: capacity_assurance<br/>/cross_module_integration.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_capacity_assurance_host_resource_governor_py["capacity_assurance/host_resource_governor<br/>host_resource_governor.py — 主机资源治理 (B17,<br/>DD91, TASK-017)<br/>文件: capacity_assurance<br/>/host_resource_governor.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_capacity_assurance_kill_switch_py["capacity_assurance/kill_switch<br/>kill_switch.py -- safety circuit breaker<br/>(DD110, TASK-019).<br/>文件: capacity_assurance/kill_switch.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_capacity_assurance_risk_mitigation_py["capacity_assurance/risk_mitigation<br/>Risk mitigation — R1~R16 全量风险缓解实现<br/>（对标蓝图 §14 风险与缓解 + 多轮盲...<br/>文件: capacity_assurance/risk_mitigation.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_capacity_assurance_schema_py["capacity_assurance/schema<br/>SchemaManager — 容量保障体系数据库 Schema 管理器<br/>文件: capacity_assurance/schema.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_capacity_assurance_sli_instrumentation_py["capacity_assurance/sli_instrumentation<br/>SLI instrumentation — SLI采集插桩点（对标蓝图<br/>§13 SLI Registry CAP-001~CAP-...<br/>文件: capacity_assurance/sli_instrumentation.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_capacity_assurance_tech_stack_py["capacity_assurance/tech_stack<br/>TechStackValidator — 技术栈可用性校验器<br/>文件: capacity_assurance/tech_stack.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_capacity_assurance_token_budget_py["capacity_assurance/token_budget<br/>token_budget.py — Token 估算工具 SSoT<br/>文件: capacity_assurance/token_budget.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_cost_tracker_py["infrastructure/cost_tracker<br/>RI-15 CostTracker — 成本追踪器<br/>文件: infrastructure/cost_tracker.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_dry_run_simulator_py["infrastructure/dry_run_simulator<br/>RI-14 DryRunSimulator — 干运行模拟器<br/>文件: infrastructure/dry_run_simulator.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_event_bus_upgrade_py["infrastructure/event_bus_upgrade<br/>DEPRECATED: 此文件已废弃。<br/>文件: infrastructure/event_bus_upgrade.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_event_store_py["infrastructure/event_store<br/>RI-13 EventStore — 事件存储<br/>文件: infrastructure/event_store.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_events_event_store_py["events/event_store<br/>Event Store — 事件持久化存储。<br/>文件: events/event_store.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_finding_task_bridge_py["infrastructure/finding_task_bridge<br/>Finding->TaskCard 桥接器<br/>文件: infrastructure/finding_task_bridge.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_git_batcher_py["infrastructure/git_batcher<br/>git_batcher.py — Git 命令批量化工具<br/>（ARCH-GIT-CALL-BUDGET P2.2，2026-07-19）<br/>文件: infrastructure/git_batcher.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_h1_redis_hot_init_py["infrastructure/h1_redis_hot 包入口<br/>H1 Redis 热缓存模块——盘中实盘/模拟盘 <5ms<br/>因子截面在线存储（DD-11-01）。<br/>文件: h1_redis_hot/__init__.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_h1_redis_hot_h1_cqrs_projectors_py["h1_redis_hot/h1_cqrs_projectors<br/>H1CqrsProjectors — 事件→Redis 物化视图投影器。<br/>文件: h1_redis_hot/h1_cqrs_projectors.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_h1_redis_hot_h1_integration_py["h1_redis_hot/h1_integration<br/>H1 Redis 集成适配器——连接 D-FACTOR/SIGNAL/RISK<br/>与 H1 热缓存。<br/>文件: h1_redis_hot/h1_integration.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_health_monitor_health_aggregator_py["health_monitor/health_aggregator<br/>全系统健康聚合 — check_all_systems()<br/>文件: health_monitor/health_aggregator.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_hooks_event_hook_py["hooks/event_hook<br/>EventHook — 声明式任务系统事件订阅<br/>文件: hooks/event_hook.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_impact_impact_propagator_py["impact/impact_propagator<br/>Impact Propagator — 变更影响传播分析。<br/>文件: impact/impact_propagator.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_impact_llm_impact_analyzer_py["impact/llm_impact_analyzer<br/>LLM Impact Analyzer — 语义影响分析器。<br/>文件: impact/llm_impact_analyzer.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_infrastructure_base_py["infrastructure/infrastructure_base<br/>基础设施 — Infrastructure Layer Skeleton<br/>文件: infrastructure/infrastructure_base.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_kill_switch_sim_py["infrastructure/kill_switch_sim<br/>Kill Switch T0 Hardware Simulator<br/>文件: infrastructure/kill_switch_sim.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_lifecycle_scope_guard_py["lifecycle/scope_guard<br/>Scope Guard — 范围蔓延检测与阻断。<br/>文件: lifecycle/scope_guard.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_lifecycle_task_lifecycle_manager_py["lifecycle/task_lifecycle_manager<br/>Task Lifecycle Manager — G0-G7<br/>任务生命周期门禁。<br/>文件: lifecycle/task_lifecycle_manager.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_observability_trace_decorator_py["observability/trace_decorator<br/>基础设施/observability包的trace_decorator模块<br/>文件: observability/trace_decorator.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_pipeline_backpressure_manager_py["pipeline/backpressure_manager<br/>Pipeline — Backpressure Manager<br/>文件: pipeline/backpressure_manager.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_pipeline_circuit_breaker_manager_py["pipeline/circuit_breaker_manager<br/>CircuitBreakerManager -- standalone circuit<br/>breaker manager (Netflix Hystrix ...<br/>文件: pipeline/circuit_breaker_manager.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_pipeline_cost_tracker_py["pipeline/cost_tracker<br/>CostTracker —— LLM 调用成本追踪器（SRC-0025）<br/>文件: pipeline/cost_tracker.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_pipeline_dead_letter_queue_py["pipeline/dead_letter_queue<br/>DeadLetterQueue — 死信队列<br/>文件: pipeline/dead_letter_queue.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_pipeline_llm_gateway_py["pipeline/llm_gateway<br/>MOD-INF-019: Agent Spec — LLM Gateway<br/>文件: pipeline/llm_gateway.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_pipeline_pipeline_agent_bridge_py["pipeline/pipeline_agent_bridge<br/>Pipeline -> Agent Bridge — 双编排器桥接层<br/>文件: pipeline/pipeline_agent_bridge.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_pipeline_pipeline_lock_py["pipeline/pipeline_lock<br/>Pipeline Lock — 双管线并发锁<br/>文件: pipeline/pipeline_lock.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_pipeline_pipeline_roadmap_py["pipeline/pipeline_roadmap<br/>Pipeline 未来版本路线图——v0.10.0 -> v0.12.0<br/>规划骨架。<br/>文件: pipeline/pipeline_roadmap.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_pipeline_preemption_manager_py["pipeline/preemption_manager<br/>PreemptionManager -- 优先级抢占管理器<br/>文件: pipeline/preemption_manager.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_pipeline_routing_plugins_py["pipeline/routing_plugins<br/>Pipeline Routing Plugin System — K8s Scheduling<br/>Framework 对标<br/>文件: pipeline/routing_plugins.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_pydantic_v2_migrator_py["infrastructure/pydantic_v2_migrator<br/>M-15 PydanticV2Migrator — Pydantic V2 迁移工具<br/>文件: infrastructure/pydantic_v2_migrator.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_quality_quality_monitor_py["quality/quality_monitor<br/>Quality Monitor — 生成代码质量门禁。<br/>文件: quality/quality_monitor.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_reliability_circuit_breaker_py["reliability/circuit_breaker<br/>Circuit Breaker — 熔断器：连续失败 -> OPEN -><br/>暂停执行。<br/>文件: reliability/circuit_breaker.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_reliability_context_guard_py["reliability/context_guard<br/>Context Guard — 上下文契约守卫。<br/>文件: reliability/context_guard.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_runtime_concurrency_guard_py["runtime/concurrency_guard<br/>concurrency_guard — 回滚操作并发安全守卫。<br/>文件: runtime/concurrency_guard.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_runtime_sandbox_enforcer_py["runtime/sandbox_enforcer<br/>SandboxEnforcer — Agent 沙盒隔离。<br/>文件: runtime/sandbox_enforcer.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_runtime_startup_shutdown_py["runtime/startup_shutdown<br/>基础设施/运行时包的startup_shutdown模块<br/>文件: runtime/startup_shutdown.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_script_system_finding_py["script_system/finding<br/>Finding Schema — 审计发现标准化数据模型<br/>文件: script_system/finding.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_script_system_gate_bridge_py["script_system/gate_bridge<br/>Script->Gate 门禁桥接器 — submit_findings()<br/>生产者<br/>文件: script_system/gate_bridge.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_system_telemetry_auto_bootstrap_py["system_telemetry/auto_bootstrap<br/>auto_bootstrap — 全自动遥测注入钩子<br/>（MOD-INF-015 v2.1.0）<br/>文件: system_telemetry/auto_bootstrap.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_system_telemetry_logs_init_py["system_telemetry/logs 包入口<br/>logs — 结构化日志流（structlog + JSONL +<br/>trace注入）（D_SYSTEM_TELEMETRY）<br/>文件: logs/__init__.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_system_telemetry_metrics_bridge_py["system_telemetry/metrics_bridge<br/>TELE->FLE 指标桥接 — emit_metrics() 生产者<br/>文件: system_telemetry/metrics_bridge.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_warm_hot_gate_py["infrastructure/warm_hot_gate<br/>M-14 WarmHotGate — Warm->Hot 阻断门<br/>文件: infrastructure/warm_hot_gate.py<br/>(生产态 / production)"]
    src_zephyr_shared_lifecycle_hooks_py["lifecycle/hooks<br/>hooks.py —— 模块生命周期钩子（Phase 2 新增 /<br/>盲点 B8 修复）<br/>文件: lifecycle/hooks.py<br/>(生产态 / production)"]
    src_zephyr_trading_action_dispatcher_py["trading/action_dispatcher<br/>ActionDispatcher --- 大脑的'手' v2.0 (Phase 2)<br/>文件: trading/action_dispatcher.py<br/>(生产态 / production)"]
    src_zephyr_trading_auto_task_generator_py["trading/auto_task_generator<br/>AutoTaskGenerator — 自动任务生成器<br/>文件: trading/auto_task_generator.py<br/>(生产态 / production)"]
    src_zephyr_trading_ports_py["trading/ports<br/>Protocol-based interface layer for<br/>runtime->pipeline dependency abstraction.<br/>文件: trading/ports.py<br/>(生产态 / production)"]
    src_zephyr_trading_staging_area_py["trading/staging_area<br/>StagingArea —<br/>多AI并发草稿写入+提交+冲突检测模块<br/>（CT-SESSION-CONFLICT-002）<br/>文件: trading/staging_area.py<br/>(生产态 / production)"]
    src_zephyr_trading_task_gate_py["trading/task_gate<br/>TaskGate --- 任务门控<br/>文件: trading/task_gate.py<br/>(生产态 / production)"]
    src_zephyr_trading_windows_service_py["trading/windows_service<br/>WindowsService — Windows Service 包装器<br/>文件: trading/windows_service.py<br/>(生产态 / production)"]
    src_zephyr_trading_zombie_scanner_py["trading/zombie_scanner<br/>zombie_scanner.py — 僵尸 Python<br/>进程检测与自动处置<br/>文件: trading/zombie_scanner.py<br/>(生产态 / production)"]
    tests_zephyr_data_test_tick_redis_cache_py["data/test_tick_redis_cache<br/>TickRedisCache 单元测试——tick→Redis<br/>tick:{symbol}:latest 双写器。<br/>文件: data/test_tick_redis_cache.py<br/>(生产态 / production)"]
    tests_zephyr_runtime_test_intraday_main_py["runtime/test_intraday_main<br/>IntradayRuntime 盘中编排器单元测试。<br/>文件: runtime/test_intraday_main.py<br/>(生产态 / production)"]
    docs_01_policies_and_standards_registry_catalogs_infrastructure_registry_yaml_INFRA_DB_001 ~~~ docs_01_policies_and_standards_registry_catalogs_infrastructure_registry_yaml_INFRA_DB_002
    docs_01_policies_and_standards_registry_catalogs_infrastructure_registry_yaml_INFRA_DB_002 ~~~ docs_01_policies_and_standards_registry_catalogs_infrastructure_registry_yaml_INFRA_DB_003
    docs_01_policies_and_standards_registry_catalogs_infrastructure_registry_yaml_INFRA_DB_003 ~~~ docs_01_policies_and_standards_registry_catalogs_infrastructure_registry_yaml_INFRA_DB_006
    docs_01_policies_and_standards_registry_catalogs_infrastructure_registry_yaml_INFRA_DB_006 ~~~ src_zephyr_infrastructure_asset_inventory_main_py
    src_zephyr_infrastructure_asset_inventory_main_py ~~~ src_zephyr_infrastructure_asset_inventory_lifecycle_py
    src_zephyr_infrastructure_asset_inventory_lifecycle_py ~~~ src_zephyr_infrastructure_asset_inventory_mcp_server_py
    src_zephyr_infrastructure_asset_inventory_mcp_server_py ~~~ src_zephyr_infrastructure_asset_inventory_metadata_py
    src_zephyr_infrastructure_asset_inventory_metadata_py ~~~ src_zephyr_infrastructure_asset_inventory_trust_anchor_py
    src_zephyr_infrastructure_asset_inventory_trust_anchor_py ~~~ src_zephyr_infrastructure_auto_diagnostics_py
    src_zephyr_infrastructure_auto_diagnostics_py ~~~ src_zephyr_infrastructure_auto_fix_engine_main_py
    src_zephyr_infrastructure_auto_fix_engine_main_py ~~~ src_zephyr_infrastructure_auto_fix_engine_alignment_syncer_py
    src_zephyr_infrastructure_auto_fix_engine_alignment_syncer_py ~~~ src_zephyr_infrastructure_auto_fix_engine_all_completer_py
    src_zephyr_infrastructure_auto_fix_engine_all_completer_py ~~~ src_zephyr_infrastructure_auto_fix_engine_config_fixer_py
    src_zephyr_infrastructure_auto_fix_engine_config_fixer_py ~~~ src_zephyr_infrastructure_auto_fix_engine_dedup_extractor_py
    src_zephyr_infrastructure_auto_fix_engine_dedup_extractor_py ~~~ src_zephyr_infrastructure_auto_fix_engine_dep_version_fixer_py
    src_zephyr_infrastructure_auto_fix_engine_dep_version_fixer_py ~~~ src_zephyr_infrastructure_auto_fix_engine_drift_fixer_py
    src_zephyr_infrastructure_auto_fix_engine_drift_fixer_py ~~~ src_zephyr_infrastructure_auto_fix_engine_event_hooks_py
    src_zephyr_infrastructure_auto_fix_engine_event_hooks_py ~~~ src_zephyr_infrastructure_auto_fix_engine_fix_diff_py
    src_zephyr_infrastructure_auto_fix_engine_fix_diff_py ~~~ src_zephyr_infrastructure_auto_fix_engine_fix_scheduler_py
    src_zephyr_infrastructure_auto_fix_engine_fix_scheduler_py ~~~ src_zephyr_infrastructure_auto_fix_engine_import_fixer_py
    src_zephyr_infrastructure_auto_fix_engine_import_fixer_py ~~~ src_zephyr_infrastructure_auto_fix_engine_interrupt_guard_py
    src_zephyr_infrastructure_auto_fix_engine_interrupt_guard_py ~~~ src_zephyr_infrastructure_auto_fix_engine_llm_fix_adapter_py
    src_zephyr_infrastructure_auto_fix_engine_llm_fix_adapter_py ~~~ src_zephyr_infrastructure_auto_fix_engine_scaffold_registrar_py
    src_zephyr_infrastructure_auto_fix_engine_scaffold_registrar_py ~~~ src_zephyr_infrastructure_auto_fix_engine_self_heal_agent_py
    src_zephyr_infrastructure_auto_fix_engine_self_heal_agent_py ~~~ src_zephyr_infrastructure_auto_fix_engine_state_machine_py
    src_zephyr_infrastructure_auto_fix_engine_state_machine_py ~~~ src_zephyr_infrastructure_auto_fix_engine_zombie_cleaner_py
    src_zephyr_infrastructure_auto_fix_engine_zombie_cleaner_py ~~~ src_zephyr_infrastructure_blueprint_code_sync_py
    src_zephyr_infrastructure_blueprint_code_sync_py ~~~ src_zephyr_infrastructure_budget_enforcement_init_py
    src_zephyr_infrastructure_budget_enforcement_init_py ~~~ src_zephyr_infrastructure_capacity_assurance_budget_forecaster_py
    src_zephyr_infrastructure_capacity_assurance_budget_forecaster_py ~~~ src_zephyr_infrastructure_capacity_assurance_contracts_contract_bus_py
    src_zephyr_infrastructure_capacity_assurance_contracts_contract_bus_py ~~~ src_zephyr_infrastructure_capacity_assurance_cross_module_integration_py
    src_zephyr_infrastructure_capacity_assurance_cross_module_integration_py ~~~ src_zephyr_infrastructure_capacity_assurance_host_resource_governor_py
    src_zephyr_infrastructure_capacity_assurance_host_resource_governor_py ~~~ src_zephyr_infrastructure_capacity_assurance_kill_switch_py
    src_zephyr_infrastructure_capacity_assurance_kill_switch_py ~~~ src_zephyr_infrastructure_capacity_assurance_risk_mitigation_py
    src_zephyr_infrastructure_capacity_assurance_risk_mitigation_py ~~~ src_zephyr_infrastructure_capacity_assurance_schema_py
    src_zephyr_infrastructure_capacity_assurance_schema_py ~~~ src_zephyr_infrastructure_capacity_assurance_sli_instrumentation_py
    src_zephyr_infrastructure_capacity_assurance_sli_instrumentation_py ~~~ src_zephyr_infrastructure_capacity_assurance_tech_stack_py
    src_zephyr_infrastructure_capacity_assurance_tech_stack_py ~~~ src_zephyr_infrastructure_capacity_assurance_token_budget_py
    src_zephyr_infrastructure_capacity_assurance_token_budget_py ~~~ src_zephyr_infrastructure_cost_tracker_py
    src_zephyr_infrastructure_cost_tracker_py ~~~ src_zephyr_infrastructure_dry_run_simulator_py
    src_zephyr_infrastructure_dry_run_simulator_py ~~~ src_zephyr_infrastructure_event_bus_upgrade_py
    src_zephyr_infrastructure_event_bus_upgrade_py ~~~ src_zephyr_infrastructure_event_store_py
    src_zephyr_infrastructure_event_store_py ~~~ src_zephyr_infrastructure_events_event_store_py
    src_zephyr_infrastructure_events_event_store_py ~~~ src_zephyr_infrastructure_finding_task_bridge_py
    src_zephyr_infrastructure_finding_task_bridge_py ~~~ src_zephyr_infrastructure_git_batcher_py
    src_zephyr_infrastructure_git_batcher_py ~~~ src_zephyr_infrastructure_h1_redis_hot_init_py
    src_zephyr_infrastructure_h1_redis_hot_init_py ~~~ src_zephyr_infrastructure_h1_redis_hot_h1_cqrs_projectors_py
    src_zephyr_infrastructure_h1_redis_hot_h1_cqrs_projectors_py ~~~ src_zephyr_infrastructure_h1_redis_hot_h1_integration_py
    src_zephyr_infrastructure_h1_redis_hot_h1_integration_py ~~~ src_zephyr_infrastructure_health_monitor_health_aggregator_py
    src_zephyr_infrastructure_health_monitor_health_aggregator_py ~~~ src_zephyr_infrastructure_hooks_event_hook_py
    src_zephyr_infrastructure_hooks_event_hook_py ~~~ src_zephyr_infrastructure_impact_impact_propagator_py
    src_zephyr_infrastructure_impact_impact_propagator_py ~~~ src_zephyr_infrastructure_impact_llm_impact_analyzer_py
    src_zephyr_infrastructure_impact_llm_impact_analyzer_py ~~~ src_zephyr_infrastructure_infrastructure_base_py
    src_zephyr_infrastructure_infrastructure_base_py ~~~ src_zephyr_infrastructure_kill_switch_sim_py
    src_zephyr_infrastructure_kill_switch_sim_py ~~~ src_zephyr_infrastructure_lifecycle_scope_guard_py
    src_zephyr_infrastructure_lifecycle_scope_guard_py ~~~ src_zephyr_infrastructure_lifecycle_task_lifecycle_manager_py
    src_zephyr_infrastructure_lifecycle_task_lifecycle_manager_py ~~~ src_zephyr_infrastructure_observability_trace_decorator_py
    src_zephyr_infrastructure_observability_trace_decorator_py ~~~ src_zephyr_infrastructure_pipeline_backpressure_manager_py
    src_zephyr_infrastructure_pipeline_backpressure_manager_py ~~~ src_zephyr_infrastructure_pipeline_circuit_breaker_manager_py
    src_zephyr_infrastructure_pipeline_circuit_breaker_manager_py ~~~ src_zephyr_infrastructure_pipeline_cost_tracker_py
    src_zephyr_infrastructure_pipeline_cost_tracker_py ~~~ src_zephyr_infrastructure_pipeline_dead_letter_queue_py
    src_zephyr_infrastructure_pipeline_dead_letter_queue_py ~~~ src_zephyr_infrastructure_pipeline_llm_gateway_py
    src_zephyr_infrastructure_pipeline_llm_gateway_py ~~~ src_zephyr_infrastructure_pipeline_pipeline_agent_bridge_py
    src_zephyr_infrastructure_pipeline_pipeline_agent_bridge_py ~~~ src_zephyr_infrastructure_pipeline_pipeline_lock_py
    src_zephyr_infrastructure_pipeline_pipeline_lock_py ~~~ src_zephyr_infrastructure_pipeline_pipeline_roadmap_py
    src_zephyr_infrastructure_pipeline_pipeline_roadmap_py ~~~ src_zephyr_infrastructure_pipeline_preemption_manager_py
    src_zephyr_infrastructure_pipeline_preemption_manager_py ~~~ src_zephyr_infrastructure_pipeline_routing_plugins_py
    src_zephyr_infrastructure_pipeline_routing_plugins_py ~~~ src_zephyr_infrastructure_pydantic_v2_migrator_py
    src_zephyr_infrastructure_pydantic_v2_migrator_py ~~~ src_zephyr_infrastructure_quality_quality_monitor_py
    src_zephyr_infrastructure_quality_quality_monitor_py ~~~ src_zephyr_infrastructure_reliability_circuit_breaker_py
    src_zephyr_infrastructure_reliability_circuit_breaker_py ~~~ src_zephyr_infrastructure_reliability_context_guard_py
    src_zephyr_infrastructure_reliability_context_guard_py ~~~ src_zephyr_infrastructure_runtime_concurrency_guard_py
    src_zephyr_infrastructure_runtime_concurrency_guard_py ~~~ src_zephyr_infrastructure_runtime_sandbox_enforcer_py
    src_zephyr_infrastructure_runtime_sandbox_enforcer_py ~~~ src_zephyr_infrastructure_runtime_startup_shutdown_py
    src_zephyr_infrastructure_runtime_startup_shutdown_py ~~~ src_zephyr_infrastructure_script_system_finding_py
    src_zephyr_infrastructure_script_system_finding_py ~~~ src_zephyr_infrastructure_script_system_gate_bridge_py
    src_zephyr_infrastructure_script_system_gate_bridge_py ~~~ src_zephyr_infrastructure_system_telemetry_auto_bootstrap_py
    src_zephyr_infrastructure_system_telemetry_auto_bootstrap_py ~~~ src_zephyr_infrastructure_system_telemetry_logs_init_py
    src_zephyr_infrastructure_system_telemetry_logs_init_py ~~~ src_zephyr_infrastructure_system_telemetry_metrics_bridge_py
    src_zephyr_infrastructure_system_telemetry_metrics_bridge_py ~~~ src_zephyr_infrastructure_warm_hot_gate_py
    src_zephyr_infrastructure_warm_hot_gate_py ~~~ src_zephyr_shared_lifecycle_hooks_py
    src_zephyr_shared_lifecycle_hooks_py ~~~ src_zephyr_trading_action_dispatcher_py
    src_zephyr_trading_action_dispatcher_py ~~~ src_zephyr_trading_auto_task_generator_py
    src_zephyr_trading_auto_task_generator_py ~~~ src_zephyr_trading_ports_py
    src_zephyr_trading_ports_py ~~~ src_zephyr_trading_staging_area_py
    src_zephyr_trading_staging_area_py ~~~ src_zephyr_trading_task_gate_py
    src_zephyr_trading_task_gate_py ~~~ src_zephyr_trading_windows_service_py
    src_zephyr_trading_windows_service_py ~~~ src_zephyr_trading_zombie_scanner_py
    src_zephyr_trading_zombie_scanner_py ~~~ tests_zephyr_data_test_tick_redis_cache_py
    tests_zephyr_data_test_tick_redis_cache_py ~~~ tests_zephyr_runtime_test_intraday_main_py
    src_zephyr_infrastructure_asset_inventory_classifier_py["asset_inventory/classifier<br/>AssetClassifier — MOD-INF-026 L2 资产自动分类器<br/>文件: asset_inventory/classifier.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_asset_inventory_dashboard_py["asset_inventory/dashboard<br/>AssetDashboard — MOD-INF-026<br/>资产健康仪表盘生成器<br/>文件: asset_inventory/dashboard.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_asset_inventory_dependency_py["asset_inventory/dependency<br/>MOD-INF-026 §18 — 资产依赖图。<br/>文件: asset_inventory/dependency.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_asset_inventory_index_generator_py["asset_inventory/index_generator<br/>UnifiedAssetIndex — MOD-INF-026 L3<br/>统一资产索引生成器<br/>文件: asset_inventory/index_generator.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_asset_inventory_reconciler_py["asset_inventory/reconciler<br/>ReconciliationEngine — MOD-INF-026 L4 注册表 vs<br/>磁盘对账引擎<br/>文件: asset_inventory/reconciler.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_asset_inventory_registry_adapter_py["asset_inventory/registry_adapter<br/>MOD-INF-026 §17 — 24<br/>个异构注册表统一解析适配器。<br/>文件: asset_inventory/registry_adapter.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_asset_inventory_scanner_py["asset_inventory/scanner<br/>AssetDiscoveryScanner — MOD-INF-026 L1<br/>全量文件系统扫描器<br/>文件: asset_inventory/scanner.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_asset_inventory_telemetry_py["asset_inventory/telemetry<br/>AssetInventoryTelemetry — MOD-INF-026 自监控指标<br/>文件: asset_inventory/telemetry.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_auto_fix_engine_engine_py["auto_fix_engine/engine<br/>基础设施/auto fix engine包的engine模块<br/>文件: auto_fix_engine/engine.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_budget_enforcement_rbac_bridge_py["budget_enforcement/rbac_bridge<br/>budget_enforcement.rbac_bridge — 基础设施层<br/>RBAC 桥接适配器。<br/>文件: budget_enforcement/rbac_bridge.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_capacity_assurance_contracts_batch1_infra_py["contracts/batch1_infra<br/>Batch1 基础设施层契约 — 15条 Pydantic v2<br/>Schema（SLO/Error Budget/Token Budg...<br/>文件: contracts/batch1_infra.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_capacity_assurance_contracts_batch3_integration_py["contracts/batch3_integration<br/>Batch3 集成层契约 — 14条 Pydantic v2 Schema<br/>（OTel/W3C/跨模块CT-1~4/DR/容量预...<br/>文件: contracts/batch3_integration.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_config_validator_py["infrastructure/config_validator<br/>M-12 ConfigValidator — 配置参数校验器<br/>文件: infrastructure/config_validator.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_contract_tester_py["infrastructure/contract_tester<br/>M-11 ContractTester — 契约测试框架<br/>文件: infrastructure/contract_tester.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_h1_redis_hot_h1_redis_reader_py["h1_redis_hot/h1_redis_reader<br/>H1RedisReader — 决策引擎 <5ms 在线特征查询。<br/>文件: h1_redis_hot/h1_redis_reader.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_h1_redis_hot_h1_redis_writer_py["h1_redis_hot/h1_redis_writer<br/>H1RedisWriter — D-FACTOR Engine 每 3 秒截面写入<br/>Redis（PIPELINE 模式）。<br/>文件: h1_redis_hot/h1_redis_writer.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_pipeline_backpressure_types_py["pipeline/backpressure_types<br/>backpressure_types.py - Pipeline backpressure<br/>signal data types<br/>文件: pipeline/backpressure_types.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_pipeline_ct_pipe_routing_py["pipeline/ct_pipe_routing<br/>CT-PIPE-ORC-001 — TaskCard -> 管线入口节点路由<br/>文件: pipeline/ct_pipe_routing.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_pipeline_model_router_py["pipeline/model_router<br/>ModelRouter — 模型路由与降级链管理<br/>文件: pipeline/model_router.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_queue_task_scheduler_py["queue/task_scheduler<br/>Task Scheduler — 任务调度器。<br/>文件: queue/task_scheduler.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_system_telemetry_budget_telemetry_bridge_py["system_telemetry/_budget_telemetry_bridge<br/>基础设施/system<br/>telemetry包的budget_telemetry_bridge模块<br/>文件: system_telemetry<br/>/_budget_telemetry_bridge.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_system_telemetry_contract_metrics_py["system_telemetry/contract_metrics<br/>ZephyrAlpha — system-telemetry<br/>/contract_metrics.py<br/>文件: system_telemetry/contract_metrics.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_system_telemetry_metrics_blueprint_metrics_py["metrics/blueprint_metrics<br/>blueprint_metrics — 蓝图使用追踪 instrumentation<br/>文件: metrics/blueprint_metrics.py<br/>(生产态 / production)"]
    src_zephyr_runtime_intraday_main_py["runtime/intraday_main<br/>盘中运行时编排器——单进程串起 tick_subscriber +<br/>IntradayFactorLoop。<br/>文件: runtime/intraday_main.py<br/>(生产态 / production)"]
    src_zephyr_trading_main_py["trading/__main__<br/>python -m zephyr.trading — AutoRuntime Core 入口<br/>文件: trading/__main__.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_asset_inventory_classifier_py ~~~ src_zephyr_infrastructure_asset_inventory_dashboard_py
    src_zephyr_infrastructure_asset_inventory_dashboard_py ~~~ src_zephyr_infrastructure_asset_inventory_dependency_py
    src_zephyr_infrastructure_asset_inventory_dependency_py ~~~ src_zephyr_infrastructure_asset_inventory_index_generator_py
    src_zephyr_infrastructure_asset_inventory_index_generator_py ~~~ src_zephyr_infrastructure_asset_inventory_reconciler_py
    src_zephyr_infrastructure_asset_inventory_reconciler_py ~~~ src_zephyr_infrastructure_asset_inventory_registry_adapter_py
    src_zephyr_infrastructure_asset_inventory_registry_adapter_py ~~~ src_zephyr_infrastructure_asset_inventory_scanner_py
    src_zephyr_infrastructure_asset_inventory_scanner_py ~~~ src_zephyr_infrastructure_asset_inventory_telemetry_py
    src_zephyr_infrastructure_asset_inventory_telemetry_py ~~~ src_zephyr_infrastructure_auto_fix_engine_engine_py
    src_zephyr_infrastructure_auto_fix_engine_engine_py ~~~ src_zephyr_infrastructure_budget_enforcement_rbac_bridge_py
    src_zephyr_infrastructure_budget_enforcement_rbac_bridge_py ~~~ src_zephyr_infrastructure_capacity_assurance_contracts_batch1_infra_py
    src_zephyr_infrastructure_capacity_assurance_contracts_batch1_infra_py ~~~ src_zephyr_infrastructure_capacity_assurance_contracts_batch3_integration_py
    src_zephyr_infrastructure_capacity_assurance_contracts_batch3_integration_py ~~~ src_zephyr_infrastructure_config_validator_py
    src_zephyr_infrastructure_config_validator_py ~~~ src_zephyr_infrastructure_contract_tester_py
    src_zephyr_infrastructure_contract_tester_py ~~~ src_zephyr_infrastructure_h1_redis_hot_h1_redis_reader_py
    src_zephyr_infrastructure_h1_redis_hot_h1_redis_reader_py ~~~ src_zephyr_infrastructure_h1_redis_hot_h1_redis_writer_py
    src_zephyr_infrastructure_h1_redis_hot_h1_redis_writer_py ~~~ src_zephyr_infrastructure_pipeline_backpressure_types_py
    src_zephyr_infrastructure_pipeline_backpressure_types_py ~~~ src_zephyr_infrastructure_pipeline_ct_pipe_routing_py
    src_zephyr_infrastructure_pipeline_ct_pipe_routing_py ~~~ src_zephyr_infrastructure_pipeline_model_router_py
    src_zephyr_infrastructure_pipeline_model_router_py ~~~ src_zephyr_infrastructure_queue_task_scheduler_py
    src_zephyr_infrastructure_queue_task_scheduler_py ~~~ src_zephyr_infrastructure_system_telemetry_budget_telemetry_bridge_py
    src_zephyr_infrastructure_system_telemetry_budget_telemetry_bridge_py ~~~ src_zephyr_infrastructure_system_telemetry_contract_metrics_py
    src_zephyr_infrastructure_system_telemetry_contract_metrics_py ~~~ src_zephyr_infrastructure_system_telemetry_metrics_blueprint_metrics_py
    src_zephyr_infrastructure_system_telemetry_metrics_blueprint_metrics_py ~~~ src_zephyr_runtime_intraday_main_py
    src_zephyr_runtime_intraday_main_py ~~~ src_zephyr_trading_main_py
    src_zephyr_data_tick_redis_cache_py["data/tick_redis_cache<br/>tick → Redis tick:{symbol}:latest 双写器<br/>（D-DATA → H1 集成适配器）。<br/>文件: data/tick_redis_cache.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_asset_inventory_models_py["asset_inventory/models<br/>AssetInventoryModels — MOD-INF-026 Pydantic V2<br/>共享数据模型<br/>文件: asset_inventory/models.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_auto_fix_engine_batch_fixer_py["auto_fix_engine/batch_fixer<br/>基础设施/auto fix engine包的batch_fixer模块<br/>文件: auto_fix_engine/batch_fixer.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_auto_fix_engine_compliance_auditor_py["auto_fix_engine/compliance_auditor<br/>基础设施/auto fix<br/>engine包的compliance_auditor模块<br/>文件: auto_fix_engine/compliance_auditor.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_auto_fix_engine_escalation_bridge_py["auto_fix_engine/escalation_bridge<br/>基础设施/auto fix<br/>engine包的escalation_bridge模块<br/>文件: auto_fix_engine/escalation_bridge.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_auto_fix_engine_fix_health_check_py["auto_fix_engine/fix_health_check<br/>基础设施/auto fix engine包的fix_health_check模块<br/>文件: auto_fix_engine/fix_health_check.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_auto_fix_engine_fix_pattern_miner_py["auto_fix_engine/fix_pattern_miner<br/>基础设施/auto fix<br/>engine包的fix_pattern_miner模块<br/>文件: auto_fix_engine/fix_pattern_miner.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_auto_fix_engine_fix_report_py["auto_fix_engine/fix_report<br/>基础设施/auto fix engine包的fix_report模块<br/>文件: auto_fix_engine/fix_report.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_auto_fix_engine_fix_safety_py["auto_fix_engine/fix_safety<br/>基础设施/auto fix engine包的fix_safety模块<br/>文件: auto_fix_engine/fix_safety.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_auto_fix_engine_shadow_workspace_py["auto_fix_engine/shadow_workspace<br/>基础设施/auto fix engine包的shadow_workspace模块<br/>文件: auto_fix_engine/shadow_workspace.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_database_service_py["infrastructure/database_service<br/>DatabaseService:<br/>统一管理数据库的连接池、生命周期、健康检查<br/>文件: infrastructure/database_service.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_pipeline_models_py["pipeline/models<br/>Pipeline 数据模型<br/>文件: pipeline/models.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_system_telemetry_facade_py["system_telemetry/facade<br/>Telemetry — 系统遥测门面类（MOD-INF-015 v2.1.0）<br/>文件: system_telemetry/facade.py<br/>(生产态 / production)"]
    src_zephyr_trading_auto_runtime_core_py["trading/auto_runtime_core<br/>AutoRuntimeCore — 三层运行时运营中心（系统大脑）<br/>文件: trading/auto_runtime_core.py<br/>(生产态 / production)"]
    src_zephyr_data_tick_redis_cache_py ~~~ src_zephyr_infrastructure_asset_inventory_models_py
    src_zephyr_infrastructure_asset_inventory_models_py ~~~ src_zephyr_infrastructure_auto_fix_engine_batch_fixer_py
    src_zephyr_infrastructure_auto_fix_engine_batch_fixer_py ~~~ src_zephyr_infrastructure_auto_fix_engine_compliance_auditor_py
    src_zephyr_infrastructure_auto_fix_engine_compliance_auditor_py ~~~ src_zephyr_infrastructure_auto_fix_engine_escalation_bridge_py
    src_zephyr_infrastructure_auto_fix_engine_escalation_bridge_py ~~~ src_zephyr_infrastructure_auto_fix_engine_fix_health_check_py
    src_zephyr_infrastructure_auto_fix_engine_fix_health_check_py ~~~ src_zephyr_infrastructure_auto_fix_engine_fix_pattern_miner_py
    src_zephyr_infrastructure_auto_fix_engine_fix_pattern_miner_py ~~~ src_zephyr_infrastructure_auto_fix_engine_fix_report_py
    src_zephyr_infrastructure_auto_fix_engine_fix_report_py ~~~ src_zephyr_infrastructure_auto_fix_engine_fix_safety_py
    src_zephyr_infrastructure_auto_fix_engine_fix_safety_py ~~~ src_zephyr_infrastructure_auto_fix_engine_shadow_workspace_py
    src_zephyr_infrastructure_auto_fix_engine_shadow_workspace_py ~~~ src_zephyr_infrastructure_database_service_py
    src_zephyr_infrastructure_database_service_py ~~~ src_zephyr_infrastructure_pipeline_models_py
    src_zephyr_infrastructure_pipeline_models_py ~~~ src_zephyr_infrastructure_system_telemetry_facade_py
    src_zephyr_infrastructure_system_telemetry_facade_py ~~~ src_zephyr_trading_auto_runtime_core_py
    src_zephyr_infrastructure_auto_fix_engine_fix_budget_py["auto_fix_engine/fix_budget<br/>基础设施/auto fix engine包的fix_budget模块<br/>文件: auto_fix_engine/fix_budget.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_auto_fix_engine_fix_reliability_py["auto_fix_engine/fix_reliability<br/>基础设施/auto fix engine包的fix_reliability模块<br/>文件: auto_fix_engine/fix_reliability.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_file_watcher_py["infrastructure/file_watcher<br/>基础设施包的file_watcher模块<br/>文件: infrastructure/file_watcher.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_h1_redis_hot_h1_redis_schema_py["h1_redis_hot/h1_redis_schema<br/>H1 Redis 热缓存 Key Schema（DDL-as-Code）。<br/>文件: h1_redis_hot/h1_redis_schema.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_queue_task_queue_py["queue/task_queue<br/>Task Queue — 后台任务队列 + 自动 Dispatch。<br/>文件: queue/task_queue.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_redis_config_py["infrastructure/redis_config<br/>Redis 连接配置单真源加载器（H1 业务热缓存<br/>INFRA-DB-007）。<br/>文件: infrastructure/redis_config.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_system_telemetry_ai_behavior_event_sink_py["ai_behavior/event_sink<br/>遥测 · ai_behavior/event_sink — AI<br/>行为遥测事件管道。<br/>文件: ai_behavior/event_sink.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_system_telemetry_archive_cold_stub_py["archive/cold_stub<br/>遥测 · archive/cold_stub — 冷存储归档管道。<br/>文件: archive/cold_stub.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_system_telemetry_traces_span_stub_py["traces/span_stub<br/>遥测 · traces/span_stub — W3C TraceContext<br/>分布式追踪管道。<br/>文件: traces/span_stub.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_system_telemetry_watchdog_py["system_telemetry/watchdog<br/>三冗余 Watchdog（CT-WATCHDOG-001）——互检+Panic<br/>Mode+Dead Man's Switch。<br/>文件: system_telemetry/watchdog.py<br/>(生产态 / production)"]
    src_zephyr_trading_auto_integrator_py["trading/auto_integrator<br/>AutoIntegrator — 自动接入器<br/>文件: trading/auto_integrator.py<br/>(生产态 / production)"]
    src_zephyr_trading_boot_hooks_py["trading/boot_hooks<br/>交易包的boot_hooks模块<br/>文件: trading/boot_hooks.py<br/>(生产态 / production)"]
    src_zephyr_trading_capability_sync_py["trading/capability_sync<br/>交易包的capability_sync模块<br/>文件: trading/capability_sync.py<br/>(生产态 / production)"]
    src_zephyr_trading_lifecycle_manager_py["trading/lifecycle_manager<br/>交易包的lifecycle_manager模块<br/>文件: trading/lifecycle_manager.py<br/>(生产态 / production)"]
    src_zephyr_trading_status_dashboard_py["trading/status_dashboard<br/>StatusDashboard — 实时状态面板<br/>文件: trading/status_dashboard.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_auto_fix_engine_fix_budget_py ~~~ src_zephyr_infrastructure_auto_fix_engine_fix_reliability_py
    src_zephyr_infrastructure_auto_fix_engine_fix_reliability_py ~~~ src_zephyr_infrastructure_file_watcher_py
    src_zephyr_infrastructure_file_watcher_py ~~~ src_zephyr_infrastructure_h1_redis_hot_h1_redis_schema_py
    src_zephyr_infrastructure_h1_redis_hot_h1_redis_schema_py ~~~ src_zephyr_infrastructure_queue_task_queue_py
    src_zephyr_infrastructure_queue_task_queue_py ~~~ src_zephyr_infrastructure_redis_config_py
    src_zephyr_infrastructure_redis_config_py ~~~ src_zephyr_infrastructure_system_telemetry_ai_behavior_event_sink_py
    src_zephyr_infrastructure_system_telemetry_ai_behavior_event_sink_py ~~~ src_zephyr_infrastructure_system_telemetry_archive_cold_stub_py
    src_zephyr_infrastructure_system_telemetry_archive_cold_stub_py ~~~ src_zephyr_infrastructure_system_telemetry_traces_span_stub_py
    src_zephyr_infrastructure_system_telemetry_traces_span_stub_py ~~~ src_zephyr_infrastructure_system_telemetry_watchdog_py
    src_zephyr_infrastructure_system_telemetry_watchdog_py ~~~ src_zephyr_trading_auto_integrator_py
    src_zephyr_trading_auto_integrator_py ~~~ src_zephyr_trading_boot_hooks_py
    src_zephyr_trading_boot_hooks_py ~~~ src_zephyr_trading_capability_sync_py
    src_zephyr_trading_capability_sync_py ~~~ src_zephyr_trading_lifecycle_manager_py
    src_zephyr_trading_lifecycle_manager_py ~~~ src_zephyr_trading_status_dashboard_py
    src_zephyr_infrastructure_auto_fix_engine_models_py["auto_fix_engine/models<br/>基础设施/auto fix engine包的models模块<br/>文件: auto_fix_engine/models.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_observability_notifier_py["observability/notifier<br/>Notifier — 多渠道 Owner 通知。<br/>文件: observability/notifier.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_runtime_gate_coordinator_py["runtime/gate_coordinator<br/>Rollback->Gate 协调器 — freeze_all / thaw_all<br/>文件: runtime/gate_coordinator.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_sla_sla_monitor_py["sla/sla_monitor<br/>SLA Monitor — 服务等级协议 (SLA) 监控 RTO/RPO。<br/>文件: sla/sla_monitor.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_system_telemetry_health_aggregator_py["system_telemetry/health_aggregator<br/>健康聚合器（Health Aggregator）<br/>文件: system_telemetry/health_aggregator.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_system_telemetry_logs_structured_sink_py["logs/structured_sink<br/>结构化日志管道（D_SYSTEM_TELEMETRY）<br/>文件: logs/structured_sink.py<br/>(生产态 / production)"]
    src_zephyr_trading_ai_audit_logger_py["trading/ai_audit_logger<br/>AiAuditLogger — AI 行为审计日志<br/>文件: trading/ai_audit_logger.py<br/>(生产态 / production)"]
    src_zephyr_trading_dream_cycle_py["trading/dream_cycle<br/>DreamCycle — 知识固化引擎<br/>文件: trading/dream_cycle.py<br/>(生产态 / production)"]
    src_zephyr_trading_finalizer_py["trading/finalizer<br/>Finalizer — 优雅清理器<br/>文件: trading/finalizer.py<br/>(生产态 / production)"]
    src_zephyr_trading_health_monitor_py["trading/health_monitor<br/>HealthMonitor — 健康监控 + 自愈<br/>文件: trading/health_monitor.py<br/>(生产态 / production)"]
    src_zephyr_trading_integration_registry_py["trading/integration_registry<br/>IntegrationRegistry — 集成注册表<br/>文件: trading/integration_registry.py<br/>(生产态 / production)"]
    src_zephyr_trading_night_shift_queue_py["trading/night_shift_queue<br/>NightShiftQueue — 夜班登记表持久化<br/>文件: trading/night_shift_queue.py<br/>(生产态 / production)"]
    src_zephyr_trading_orphan_detector_py["trading/orphan_detector<br/>OrphanDetector — 孤儿检测器<br/>文件: trading/orphan_detector.py<br/>(生产态 / production)"]
    src_zephyr_trading_runtime_config_py["trading/runtime_config<br/>交易包的runtime_config模块<br/>文件: trading/runtime_config.py<br/>(生产态 / production)"]
    src_zephyr_trading_stop_gate_py["trading/stop_gate<br/>StopGate — 质量闸门<br/>文件: trading/stop_gate.py<br/>(生产态 / production)"]
    src_zephyr_trading_work_orchestrator_py["trading/work_orchestrator<br/>交易包的work_orchestrator模块<br/>文件: trading/work_orchestrator.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_auto_fix_engine_models_py ~~~ src_zephyr_infrastructure_observability_notifier_py
    src_zephyr_infrastructure_observability_notifier_py ~~~ src_zephyr_infrastructure_runtime_gate_coordinator_py
    src_zephyr_infrastructure_runtime_gate_coordinator_py ~~~ src_zephyr_infrastructure_sla_sla_monitor_py
    src_zephyr_infrastructure_sla_sla_monitor_py ~~~ src_zephyr_infrastructure_system_telemetry_health_aggregator_py
    src_zephyr_infrastructure_system_telemetry_health_aggregator_py ~~~ src_zephyr_infrastructure_system_telemetry_logs_structured_sink_py
    src_zephyr_infrastructure_system_telemetry_logs_structured_sink_py ~~~ src_zephyr_trading_ai_audit_logger_py
    src_zephyr_trading_ai_audit_logger_py ~~~ src_zephyr_trading_dream_cycle_py
    src_zephyr_trading_dream_cycle_py ~~~ src_zephyr_trading_finalizer_py
    src_zephyr_trading_finalizer_py ~~~ src_zephyr_trading_health_monitor_py
    src_zephyr_trading_health_monitor_py ~~~ src_zephyr_trading_integration_registry_py
    src_zephyr_trading_integration_registry_py ~~~ src_zephyr_trading_night_shift_queue_py
    src_zephyr_trading_night_shift_queue_py ~~~ src_zephyr_trading_orphan_detector_py
    src_zephyr_trading_orphan_detector_py ~~~ src_zephyr_trading_runtime_config_py
    src_zephyr_trading_runtime_config_py ~~~ src_zephyr_trading_stop_gate_py
    src_zephyr_trading_stop_gate_py ~~~ src_zephyr_trading_work_orchestrator_py
    src_zephyr_infrastructure_system_telemetry_trace_bridge_py["system_telemetry/_trace_bridge<br/>基础设施/system telemetry包的trace_bridge模块<br/>文件: system_telemetry/_trace_bridge.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_system_telemetry_health_probes_py["system_telemetry/health_probes<br/>三态健康探针协议（Health Probes —<br/>CT-HEALTH-001）<br/>文件: system_telemetry/health_probes.py<br/>(生产态 / production)"]
    src_zephyr_trading_module_onboarding_scanner_py["trading/module_onboarding_scanner<br/>ModuleOnboardingScanner — 模块接入扫描器<br/>文件: trading/module_onboarding_scanner.py<br/>(生产态 / production)"]
    src_zephyr_trading_resource_optimization_py["trading/resource_optimization<br/>resource_optimization.py - MAPE-K autonomic<br/>resource optimization engine<br/>文件: trading/resource_optimization.py<br/>(生产态 / production)"]
    src_zephyr_trading_work_dag_py["trading/work_dag<br/>WorkDAG + WorkItem — 工作编排数据模型<br/>文件: trading/work_dag.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_system_telemetry_trace_bridge_py ~~~ src_zephyr_infrastructure_system_telemetry_health_probes_py
    src_zephyr_infrastructure_system_telemetry_health_probes_py ~~~ src_zephyr_trading_module_onboarding_scanner_py
    src_zephyr_trading_module_onboarding_scanner_py ~~~ src_zephyr_trading_resource_optimization_py
    src_zephyr_trading_resource_optimization_py ~~~ src_zephyr_trading_work_dag_py
    src_zephyr_shared_lifecycle_daemon_registry_py["lifecycle/daemon_registry<br/>daemon_registry.py - unified daemon thread<br/>registry + resource guardian<br/>文件: lifecycle/daemon_registry.py<br/>(生产态 / production)"]
    src_zephyr_shared_lifecycle_lazy_loader_py["lifecycle/lazy_loader<br/>lazy_loader.py - Lazy module loading registry<br/>文件: lifecycle/lazy_loader.py<br/>(生产态 / production)"]
    src_zephyr_shared_lifecycle_resource_optimization_models_py["lifecycle/resource_optimization_models<br/>models.py - Pydantic data models for resource<br/>optimization engine<br/>文件: lifecycle/resource_optimization_models.py<br/>(生产态 / production)"]
    src_zephyr_trading_capability_registry_py["trading/capability_registry<br/>CapabilityRegistry — 能力注册中心<br/>文件: trading/capability_registry.py<br/>(生产态 / production)"]
    src_zephyr_shared_lifecycle_daemon_registry_py ~~~ src_zephyr_shared_lifecycle_lazy_loader_py
    src_zephyr_shared_lifecycle_lazy_loader_py ~~~ src_zephyr_shared_lifecycle_resource_optimization_models_py
    src_zephyr_shared_lifecycle_resource_optimization_models_py ~~~ src_zephyr_trading_capability_registry_py
    src_zephyr_trading_capability_card_py["trading/capability_card<br/>CapabilityCard — 能力卡片数据模型<br/>文件: trading/capability_card.py<br/>(生产态 / production)"]
    src_zephyr_data_tick_redis_cache_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_h1_redis_hot_h1_redis_schema_py
    src_zephyr_infrastructure_database_service_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_redis_config_py
    src_zephyr_infrastructure_warm_hot_gate_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_config_validator_py
    src_zephyr_infrastructure_warm_hot_gate_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_contract_tester_py
    src_zephyr_infrastructure_asset_inventory_dashboard_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_asset_inventory_models_py
    src_zephyr_infrastructure_asset_inventory_classifier_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_asset_inventory_models_py
    src_zephyr_infrastructure_asset_inventory_index_generator_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_asset_inventory_models_py
    src_zephyr_infrastructure_asset_inventory_lifecycle_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_asset_inventory_models_py
    src_zephyr_infrastructure_asset_inventory_reconciler_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_asset_inventory_models_py
    src_zephyr_infrastructure_asset_inventory_telemetry_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_system_telemetry_facade_py
    src_zephyr_infrastructure_asset_inventory_registry_adapter_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_asset_inventory_models_py
    src_zephyr_infrastructure_asset_inventory_scanner_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_asset_inventory_models_py
    src_zephyr_infrastructure_auto_fix_engine_alignment_syncer_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_asset_inventory_main_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_asset_inventory_dashboard_py
    src_zephyr_infrastructure_asset_inventory_main_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_asset_inventory_classifier_py
    src_zephyr_infrastructure_asset_inventory_main_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_asset_inventory_dependency_py
    src_zephyr_infrastructure_asset_inventory_main_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_asset_inventory_index_generator_py
    src_zephyr_infrastructure_asset_inventory_main_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_asset_inventory_reconciler_py
    src_zephyr_infrastructure_asset_inventory_main_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_asset_inventory_telemetry_py
    src_zephyr_infrastructure_asset_inventory_main_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_asset_inventory_registry_adapter_py
    src_zephyr_infrastructure_asset_inventory_main_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_asset_inventory_models_py
    src_zephyr_infrastructure_asset_inventory_main_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_asset_inventory_scanner_py
    src_zephyr_infrastructure_auto_fix_engine_batch_fixer_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_fix_budget_py
    src_zephyr_infrastructure_auto_fix_engine_batch_fixer_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_fix_reliability_py
    src_zephyr_infrastructure_auto_fix_engine_batch_fixer_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_drift_fixer_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_all_completer_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_dedup_extractor_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_compliance_auditor_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_escalation_bridge_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_config_fixer_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_fix_budget_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_dep_version_fixer_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_fix_diff_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_engine_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_batch_fixer_py
    src_zephyr_infrastructure_auto_fix_engine_engine_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_compliance_auditor_py
    src_zephyr_infrastructure_auto_fix_engine_engine_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_escalation_bridge_py
    src_zephyr_infrastructure_auto_fix_engine_engine_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_fix_budget_py
    src_zephyr_infrastructure_auto_fix_engine_engine_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_fix_health_check_py
    src_zephyr_infrastructure_auto_fix_engine_engine_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_fix_reliability_py
    src_zephyr_infrastructure_auto_fix_engine_engine_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_fix_pattern_miner_py
    src_zephyr_infrastructure_auto_fix_engine_engine_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_fix_report_py
    src_zephyr_infrastructure_auto_fix_engine_engine_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_engine_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_fix_safety_py
    src_zephyr_infrastructure_auto_fix_engine_engine_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_shadow_workspace_py
    src_zephyr_infrastructure_auto_fix_engine_event_hooks_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_engine_py
    src_zephyr_infrastructure_auto_fix_engine_event_hooks_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_fix_health_check_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_fix_reliability_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_fix_pattern_miner_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_scaffold_registrar_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_fix_scheduler_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_fix_report_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_fix_safety_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_llm_fix_adapter_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_llm_fix_adapter_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_fix_safety_py
    src_zephyr_infrastructure_auto_fix_engine_import_fixer_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_shadow_workspace_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_zombie_cleaner_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_self_heal_agent_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_main_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_engine_py
    src_zephyr_infrastructure_budget_enforcement_init_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_budget_enforcement_rbac_bridge_py
    src_zephyr_infrastructure_capacity_assurance_contracts_contract_bus_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_capacity_assurance_contracts_batch3_integration_py
    src_zephyr_infrastructure_capacity_assurance_contracts_contract_bus_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_capacity_assurance_contracts_batch1_infra_py
    src_zephyr_infrastructure_h1_redis_hot_h1_integration_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_h1_redis_hot_h1_redis_reader_py
    src_zephyr_infrastructure_h1_redis_hot_h1_integration_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_h1_redis_hot_h1_redis_writer_py
    src_zephyr_infrastructure_h1_redis_hot_h1_cqrs_projectors_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_h1_redis_hot_h1_redis_schema_py
    src_zephyr_infrastructure_h1_redis_hot_h1_redis_reader_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_h1_redis_hot_h1_redis_schema_py
    src_zephyr_infrastructure_h1_redis_hot_h1_redis_writer_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_h1_redis_hot_h1_redis_schema_py
    src_zephyr_infrastructure_pipeline_backpressure_manager_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_pipeline_backpressure_types_py
    src_zephyr_infrastructure_pipeline_circuit_breaker_manager_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_pipeline_models_py
    src_zephyr_infrastructure_pipeline_cost_tracker_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_pipeline_model_router_py
    src_zephyr_infrastructure_pipeline_cost_tracker_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_pipeline_models_py
    src_zephyr_infrastructure_pipeline_dead_letter_queue_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_pipeline_models_py
    src_zephyr_infrastructure_pipeline_ct_pipe_routing_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_pipeline_models_py
    src_zephyr_infrastructure_pipeline_pipeline_agent_bridge_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_pipeline_models_py
    src_zephyr_infrastructure_pipeline_routing_plugins_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_pipeline_ct_pipe_routing_py
    src_zephyr_infrastructure_pipeline_routing_plugins_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_pipeline_models_py
    src_zephyr_infrastructure_pipeline_preemption_manager_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_pipeline_models_py
    src_zephyr_infrastructure_system_telemetry_facade_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_system_telemetry_health_aggregator_py
    src_zephyr_infrastructure_system_telemetry_facade_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_system_telemetry_watchdog_py
    src_zephyr_infrastructure_system_telemetry_facade_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_system_telemetry_ai_behavior_event_sink_py
    src_zephyr_infrastructure_system_telemetry_facade_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_system_telemetry_archive_cold_stub_py
    src_zephyr_infrastructure_system_telemetry_facade_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_system_telemetry_traces_span_stub_py
    src_zephyr_infrastructure_system_telemetry_auto_bootstrap_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_system_telemetry_contract_metrics_py
    src_zephyr_infrastructure_system_telemetry_auto_bootstrap_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_system_telemetry_facade_py
    src_zephyr_infrastructure_system_telemetry_auto_bootstrap_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_system_telemetry_budget_telemetry_bridge_py
    src_zephyr_infrastructure_system_telemetry_auto_bootstrap_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_system_telemetry_metrics_blueprint_metrics_py
    src_zephyr_infrastructure_system_telemetry_health_aggregator_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_system_telemetry_health_probes_py
    src_zephyr_infrastructure_system_telemetry_ai_behavior_event_sink_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_system_telemetry_logs_structured_sink_py
    src_zephyr_infrastructure_system_telemetry_logs_init_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_system_telemetry_logs_structured_sink_py
    src_zephyr_infrastructure_system_telemetry_traces_span_stub_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_system_telemetry_trace_bridge_py
    src_zephyr_infrastructure_system_telemetry_logs_structured_sink_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_system_telemetry_trace_bridge_py
    src_zephyr_runtime_intraday_main_py -->|导入依赖 / import_depends| src_zephyr_data_tick_redis_cache_py
    src_zephyr_runtime_intraday_main_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_database_service_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_file_watcher_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_queue_task_queue_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_trading_ai_audit_logger_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_trading_auto_integrator_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_trading_capability_registry_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_trading_boot_hooks_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_trading_dream_cycle_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_trading_capability_sync_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_trading_health_monitor_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_trading_finalizer_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_trading_module_onboarding_scanner_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_trading_night_shift_queue_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_trading_integration_registry_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_trading_orphan_detector_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_trading_lifecycle_manager_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_trading_resource_optimization_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_trading_runtime_config_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_trading_status_dashboard_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_trading_stop_gate_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_trading_work_dag_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_trading_work_orchestrator_py
    src_zephyr_trading_action_dispatcher_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_queue_task_scheduler_py
    src_zephyr_trading_auto_integrator_py -->|导入依赖 / import_depends| src_zephyr_trading_capability_card_py
    src_zephyr_trading_auto_integrator_py -->|导入依赖 / import_depends| src_zephyr_trading_capability_registry_py
    src_zephyr_trading_auto_integrator_py -->|导入依赖 / import_depends| src_zephyr_trading_module_onboarding_scanner_py
    src_zephyr_trading_capability_registry_py -->|导入依赖 / import_depends| src_zephyr_trading_capability_card_py
    src_zephyr_trading_boot_hooks_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_observability_notifier_py
    src_zephyr_trading_boot_hooks_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_runtime_gate_coordinator_py
    src_zephyr_trading_boot_hooks_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_sla_sla_monitor_py
    src_zephyr_trading_boot_hooks_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_system_telemetry_health_aggregator_py
    src_zephyr_trading_boot_hooks_py -->|导入依赖 / import_depends| src_zephyr_trading_finalizer_py
    src_zephyr_trading_capability_sync_py -->|导入依赖 / import_depends| src_zephyr_trading_capability_card_py
    src_zephyr_trading_capability_sync_py -->|导入依赖 / import_depends| src_zephyr_trading_capability_registry_py
    src_zephyr_trading_health_monitor_py -->|导入依赖 / import_depends| src_zephyr_trading_resource_optimization_py
    src_zephyr_trading_module_onboarding_scanner_py -->|导入依赖 / import_depends| src_zephyr_trading_capability_registry_py
    src_zephyr_trading_orphan_detector_py -->|导入依赖 / import_depends| src_zephyr_trading_capability_registry_py
    src_zephyr_trading_orphan_detector_py -->|导入依赖 / import_depends| src_zephyr_trading_module_onboarding_scanner_py
    src_zephyr_trading_lifecycle_manager_py -->|导入依赖 / import_depends| src_zephyr_trading_ai_audit_logger_py
    src_zephyr_trading_lifecycle_manager_py -->|导入依赖 / import_depends| src_zephyr_trading_capability_registry_py
    src_zephyr_trading_lifecycle_manager_py -->|导入依赖 / import_depends| src_zephyr_trading_dream_cycle_py
    src_zephyr_trading_lifecycle_manager_py -->|导入依赖 / import_depends| src_zephyr_trading_health_monitor_py
    src_zephyr_trading_lifecycle_manager_py -->|导入依赖 / import_depends| src_zephyr_trading_finalizer_py
    src_zephyr_trading_lifecycle_manager_py -->|导入依赖 / import_depends| src_zephyr_trading_night_shift_queue_py
    src_zephyr_trading_lifecycle_manager_py -->|导入依赖 / import_depends| src_zephyr_trading_integration_registry_py
    src_zephyr_trading_lifecycle_manager_py -->|导入依赖 / import_depends| src_zephyr_trading_runtime_config_py
    src_zephyr_trading_lifecycle_manager_py -->|导入依赖 / import_depends| src_zephyr_trading_stop_gate_py
    src_zephyr_trading_lifecycle_manager_py -->|导入依赖 / import_depends| src_zephyr_trading_work_orchestrator_py
    src_zephyr_trading_resource_optimization_py -->|导入依赖 / import_depends| src_zephyr_shared_lifecycle_daemon_registry_py
    src_zephyr_trading_resource_optimization_py -->|导入依赖 / import_depends| src_zephyr_shared_lifecycle_lazy_loader_py
    src_zephyr_trading_resource_optimization_py -->|导入依赖 / import_depends| src_zephyr_shared_lifecycle_resource_optimization_models_py
    src_zephyr_trading_status_dashboard_py -->|导入依赖 / import_depends| src_zephyr_trading_capability_registry_py
    src_zephyr_trading_status_dashboard_py -->|导入依赖 / import_depends| src_zephyr_trading_health_monitor_py
    src_zephyr_trading_status_dashboard_py -->|导入依赖 / import_depends| src_zephyr_trading_night_shift_queue_py
    src_zephyr_trading_status_dashboard_py -->|导入依赖 / import_depends| src_zephyr_trading_orphan_detector_py
    src_zephyr_trading_status_dashboard_py -->|导入依赖 / import_depends| src_zephyr_trading_work_orchestrator_py
    src_zephyr_trading_windows_service_py -->|导入依赖 / import_depends| src_zephyr_trading_auto_runtime_core_py
    src_zephyr_trading_windows_service_py -->|导入依赖 / import_depends| src_zephyr_trading_runtime_config_py
    src_zephyr_trading_windows_service_py -->|导入依赖 / import_depends| src_zephyr_trading_main_py
    src_zephyr_trading_main_py -->|导入依赖 / import_depends| src_zephyr_trading_auto_runtime_core_py
    src_zephyr_trading_main_py -->|导入依赖 / import_depends| src_zephyr_trading_runtime_config_py
    src_zephyr_trading_work_orchestrator_py -->|导入依赖 / import_depends| src_zephyr_trading_capability_registry_py
    src_zephyr_trading_work_orchestrator_py -->|导入依赖 / import_depends| src_zephyr_trading_work_dag_py
    tests_zephyr_data_test_tick_redis_cache_py -->|测试依赖 / test_depends| src_zephyr_data_tick_redis_cache_py
    tests_zephyr_data_test_tick_redis_cache_py -->|测试依赖 / test_depends| src_zephyr_infrastructure_h1_redis_hot_h1_redis_schema_py
    tests_zephyr_runtime_test_intraday_main_py -->|测试依赖 / test_depends| src_zephyr_runtime_intraday_main_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class docs_01_policies_and_standards_registry_catalogs_infrastructure_registry_yaml_INFRA_DB_001,docs_01_policies_and_standards_registry_catalogs_infrastructure_registry_yaml_INFRA_DB_002,docs_01_policies_and_standards_registry_catalogs_infrastructure_registry_yaml_INFRA_DB_003,docs_01_policies_and_standards_registry_catalogs_infrastructure_registry_yaml_INFRA_DB_006,src_zephyr_data_tick_redis_cache_py,src_zephyr_infrastructure_asset_inventory_main_py,src_zephyr_infrastructure_asset_inventory_classifier_py,src_zephyr_infrastructure_asset_inventory_dashboard_py,src_zephyr_infrastructure_asset_inventory_dependency_py,src_zephyr_infrastructure_asset_inventory_index_generator_py,src_zephyr_infrastructure_asset_inventory_lifecycle_py,src_zephyr_infrastructure_asset_inventory_mcp_server_py,src_zephyr_infrastructure_asset_inventory_metadata_py,src_zephyr_infrastructure_asset_inventory_models_py,src_zephyr_infrastructure_asset_inventory_reconciler_py,src_zephyr_infrastructure_asset_inventory_registry_adapter_py,src_zephyr_infrastructure_asset_inventory_scanner_py,src_zephyr_infrastructure_asset_inventory_telemetry_py,src_zephyr_infrastructure_asset_inventory_trust_anchor_py,src_zephyr_infrastructure_auto_diagnostics_py,src_zephyr_infrastructure_auto_fix_engine_main_py,src_zephyr_infrastructure_auto_fix_engine_alignment_syncer_py,src_zephyr_infrastructure_auto_fix_engine_all_completer_py,src_zephyr_infrastructure_auto_fix_engine_batch_fixer_py,src_zephyr_infrastructure_auto_fix_engine_compliance_auditor_py,src_zephyr_infrastructure_auto_fix_engine_config_fixer_py,src_zephyr_infrastructure_auto_fix_engine_dedup_extractor_py,src_zephyr_infrastructure_auto_fix_engine_dep_version_fixer_py,src_zephyr_infrastructure_auto_fix_engine_drift_fixer_py,src_zephyr_infrastructure_auto_fix_engine_engine_py,src_zephyr_infrastructure_auto_fix_engine_escalation_bridge_py,src_zephyr_infrastructure_auto_fix_engine_event_hooks_py,src_zephyr_infrastructure_auto_fix_engine_fix_budget_py,src_zephyr_infrastructure_auto_fix_engine_fix_diff_py,src_zephyr_infrastructure_auto_fix_engine_fix_health_check_py,src_zephyr_infrastructure_auto_fix_engine_fix_pattern_miner_py,src_zephyr_infrastructure_auto_fix_engine_fix_reliability_py,src_zephyr_infrastructure_auto_fix_engine_fix_report_py,src_zephyr_infrastructure_auto_fix_engine_fix_safety_py,src_zephyr_infrastructure_auto_fix_engine_fix_scheduler_py,src_zephyr_infrastructure_auto_fix_engine_import_fixer_py,src_zephyr_infrastructure_auto_fix_engine_interrupt_guard_py,src_zephyr_infrastructure_auto_fix_engine_llm_fix_adapter_py,src_zephyr_infrastructure_auto_fix_engine_models_py,src_zephyr_infrastructure_auto_fix_engine_scaffold_registrar_py,src_zephyr_infrastructure_auto_fix_engine_self_heal_agent_py,src_zephyr_infrastructure_auto_fix_engine_shadow_workspace_py,src_zephyr_infrastructure_auto_fix_engine_state_machine_py,src_zephyr_infrastructure_auto_fix_engine_zombie_cleaner_py,src_zephyr_infrastructure_blueprint_code_sync_py,src_zephyr_infrastructure_budget_enforcement_init_py,src_zephyr_infrastructure_budget_enforcement_rbac_bridge_py,src_zephyr_infrastructure_capacity_assurance_budget_forecaster_py,src_zephyr_infrastructure_capacity_assurance_contracts_batch1_infra_py,src_zephyr_infrastructure_capacity_assurance_contracts_batch3_integration_py,src_zephyr_infrastructure_capacity_assurance_contracts_contract_bus_py,src_zephyr_infrastructure_capacity_assurance_cross_module_integration_py,src_zephyr_infrastructure_capacity_assurance_host_resource_governor_py,src_zephyr_infrastructure_capacity_assurance_kill_switch_py,src_zephyr_infrastructure_capacity_assurance_risk_mitigation_py,src_zephyr_infrastructure_capacity_assurance_schema_py,src_zephyr_infrastructure_capacity_assurance_sli_instrumentation_py,src_zephyr_infrastructure_capacity_assurance_tech_stack_py,src_zephyr_infrastructure_capacity_assurance_token_budget_py,src_zephyr_infrastructure_config_validator_py,src_zephyr_infrastructure_contract_tester_py,src_zephyr_infrastructure_cost_tracker_py,src_zephyr_infrastructure_database_service_py,src_zephyr_infrastructure_dry_run_simulator_py,src_zephyr_infrastructure_event_bus_upgrade_py,src_zephyr_infrastructure_event_store_py,src_zephyr_infrastructure_events_event_store_py,src_zephyr_infrastructure_file_watcher_py,src_zephyr_infrastructure_finding_task_bridge_py,src_zephyr_infrastructure_git_batcher_py,src_zephyr_infrastructure_h1_redis_hot_init_py,src_zephyr_infrastructure_h1_redis_hot_h1_cqrs_projectors_py,src_zephyr_infrastructure_h1_redis_hot_h1_integration_py,src_zephyr_infrastructure_h1_redis_hot_h1_redis_reader_py,src_zephyr_infrastructure_h1_redis_hot_h1_redis_schema_py,src_zephyr_infrastructure_h1_redis_hot_h1_redis_writer_py,src_zephyr_infrastructure_health_monitor_health_aggregator_py,src_zephyr_infrastructure_hooks_event_hook_py,src_zephyr_infrastructure_impact_impact_propagator_py,src_zephyr_infrastructure_impact_llm_impact_analyzer_py,src_zephyr_infrastructure_infrastructure_base_py,src_zephyr_infrastructure_kill_switch_sim_py,src_zephyr_infrastructure_lifecycle_scope_guard_py,src_zephyr_infrastructure_lifecycle_task_lifecycle_manager_py,src_zephyr_infrastructure_observability_notifier_py,src_zephyr_infrastructure_observability_trace_decorator_py,src_zephyr_infrastructure_pipeline_backpressure_manager_py,src_zephyr_infrastructure_pipeline_backpressure_types_py,src_zephyr_infrastructure_pipeline_circuit_breaker_manager_py,src_zephyr_infrastructure_pipeline_cost_tracker_py,src_zephyr_infrastructure_pipeline_ct_pipe_routing_py,src_zephyr_infrastructure_pipeline_dead_letter_queue_py,src_zephyr_infrastructure_pipeline_llm_gateway_py,src_zephyr_infrastructure_pipeline_model_router_py,src_zephyr_infrastructure_pipeline_models_py,src_zephyr_infrastructure_pipeline_pipeline_agent_bridge_py,src_zephyr_infrastructure_pipeline_pipeline_lock_py,src_zephyr_infrastructure_pipeline_pipeline_roadmap_py,src_zephyr_infrastructure_pipeline_preemption_manager_py,src_zephyr_infrastructure_pipeline_routing_plugins_py,src_zephyr_infrastructure_pydantic_v2_migrator_py,src_zephyr_infrastructure_quality_quality_monitor_py,src_zephyr_infrastructure_queue_task_queue_py,src_zephyr_infrastructure_queue_task_scheduler_py,src_zephyr_infrastructure_redis_config_py,src_zephyr_infrastructure_reliability_circuit_breaker_py,src_zephyr_infrastructure_reliability_context_guard_py,src_zephyr_infrastructure_runtime_concurrency_guard_py,src_zephyr_infrastructure_runtime_gate_coordinator_py,src_zephyr_infrastructure_runtime_sandbox_enforcer_py,src_zephyr_infrastructure_runtime_startup_shutdown_py,src_zephyr_infrastructure_script_system_finding_py,src_zephyr_infrastructure_script_system_gate_bridge_py,src_zephyr_infrastructure_sla_sla_monitor_py,src_zephyr_infrastructure_system_telemetry_budget_telemetry_bridge_py,src_zephyr_infrastructure_system_telemetry_trace_bridge_py,src_zephyr_infrastructure_system_telemetry_ai_behavior_event_sink_py,src_zephyr_infrastructure_system_telemetry_archive_cold_stub_py,src_zephyr_infrastructure_system_telemetry_auto_bootstrap_py,src_zephyr_infrastructure_system_telemetry_contract_metrics_py,src_zephyr_infrastructure_system_telemetry_facade_py,src_zephyr_infrastructure_system_telemetry_health_aggregator_py,src_zephyr_infrastructure_system_telemetry_health_probes_py,src_zephyr_infrastructure_system_telemetry_logs_init_py,src_zephyr_infrastructure_system_telemetry_logs_structured_sink_py,src_zephyr_infrastructure_system_telemetry_metrics_blueprint_metrics_py,src_zephyr_infrastructure_system_telemetry_metrics_bridge_py,src_zephyr_infrastructure_system_telemetry_traces_span_stub_py,src_zephyr_infrastructure_system_telemetry_watchdog_py,src_zephyr_infrastructure_warm_hot_gate_py,src_zephyr_runtime_intraday_main_py,src_zephyr_shared_lifecycle_daemon_registry_py,src_zephyr_shared_lifecycle_hooks_py,src_zephyr_shared_lifecycle_lazy_loader_py,src_zephyr_shared_lifecycle_resource_optimization_models_py,src_zephyr_trading_main_py,src_zephyr_trading_action_dispatcher_py,src_zephyr_trading_ai_audit_logger_py,src_zephyr_trading_auto_integrator_py,src_zephyr_trading_auto_runtime_core_py,src_zephyr_trading_auto_task_generator_py,src_zephyr_trading_boot_hooks_py,src_zephyr_trading_capability_card_py,src_zephyr_trading_capability_registry_py,src_zephyr_trading_capability_sync_py,src_zephyr_trading_dream_cycle_py,src_zephyr_trading_finalizer_py,src_zephyr_trading_health_monitor_py,src_zephyr_trading_integration_registry_py,src_zephyr_trading_lifecycle_manager_py,src_zephyr_trading_module_onboarding_scanner_py,src_zephyr_trading_night_shift_queue_py,src_zephyr_trading_orphan_detector_py,src_zephyr_trading_ports_py,src_zephyr_trading_resource_optimization_py,src_zephyr_trading_runtime_config_py,src_zephyr_trading_staging_area_py,src_zephyr_trading_status_dashboard_py,src_zephyr_trading_stop_gate_py,src_zephyr_trading_task_gate_py,src_zephyr_trading_windows_service_py,src_zephyr_trading_work_dag_py,src_zephyr_trading_work_orchestrator_py,src_zephyr_trading_zombie_scanner_py,tests_zephyr_data_test_tick_redis_cache_py,tests_zephyr_runtime_test_intraday_main_py production
```

### 设计态的图（仅 design_maturity=design 的模块和域内依赖）

> 仅展示蓝图阶段、代码未写的设计态模块（共 1 个），不含跨域外部节点。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    docs_03_modules_cross_layer_agent_orchestrator_blueprint_md["agent_orchestrator/blueprint<br/>agent_orchestrator模块蓝图文档，描述该模块的设计<br/>意图和架构决策<br/>⛔ 基础设施运行时域，设计已就绪，等待开发排期<br/>文件: agent_orchestrator/blueprint.md<br/>(设计态 / design)"]
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class docs_03_modules_cross_layer_agent_orchestrator_blueprint_md design
```

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

| # | 本域模块 / Source Module | → | 外部域-目标模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | trading/boot_hooks.py | → | D_AUTONOMY_CORE 自治核心: 技能freshness扩展 / MOD-INF-019: Agent Spec — Skill Fres... | 导入依赖 / import_depends |
| 2 | trading/boot_hooks.py | → | D_AUTONOMY_CORE 自治核心: 技能生命周期 / MOD-INF-019: Agent Spec — Skill Lifecycle... | 导入依赖 / import_depends |
| 3 | DatabaseService: 统一管理数据库的连接池、生命周期、健康检... | → | D_DATA 数据接入层: ch配置 / ch_config (data/ch_config.py) | 导入依赖 / import_depends |
| 4 | 盘中运行时编排器——单进程串起 tick_subscriber + Intraday... | → | D_DATA 数据接入层: 告警管理（MOD-L00-004 §6.5 失败重试与告警 + §8 可观测性... | 导入依赖 / import_depends |
| 5 | 盘中运行时编排器——单进程串起 tick_subscriber + Intraday... | → | D_DATA 数据接入层: 逐笔订阅器 / tick_subscriber (data/tick_subscriber.py) | 导入依赖 / import_depends |
| 6 | 盘中运行时编排器——单进程串起 tick_subscriber + Intraday... | → | D_DATA 数据接入层: A 股交易日历守卫（MOD-L00-004）。 / trading_calendar (dat... | 导入依赖 / import_depends |
| 7 | TickRedisCache 单元测试——tick→Redis tick:{symbol}:late... | → | D_DATA 数据接入层: 逐笔订阅器 / tick_subscriber (data/tick_subscriber.py) | 测试依赖 / test_depends |
| 8 | 盘中运行时编排器——单进程串起 tick_subscriber + Intraday... | → | D_FACTOR 因子: 盘中因子调度循环——3秒拉 tick → DataFrame → DagExecuto... | 导入依赖 / import_depends |
| 9 | 盘中运行时编排器——单进程串起 tick_subscriber + Intraday... | → | D_FACTOR 因子: 盘中横截面因子 / intraday_snapshot_factors (factor/intrad... | 导入依赖 / import_depends |
| 10 | AutoRuntimeCore — 三层运行时运营中心（系统大脑） (tradin... | → | D_FEEDBACK_LOOP 反馈循环引擎: 包入口 / Feedback Loop Engine — MOD-FEEDBACK_LOOP. (feed... | 导入依赖 / import_depends |
| 11 | AutoRuntimeCore — 三层运行时运营中心（系统大脑） (tradin... | → | D_FEEDBACK_LOOP 反馈循环引擎: 调度器 / scheduler (feedback_loop/scheduler.py) | 导入依赖 / import_depends |
| 12 | trading/lifecycle_manager.py | → | D_FEEDBACK_LOOP 反馈循环引擎: 包入口 / Feedback Loop Engine — MOD-FEEDBACK_LOOP. (feed... | 导入依赖 / import_depends |
| 13 | AssetDashboard — MOD-INF-026 资产健康仪表盘生成器 (asset... | → | D_GOVERNANCE 生命周期管理: 依赖图模式 / depgraph_schema (governance/depgraph_schema.py) | 导入依赖 / import_depends |
| 14 | auto_fix_engine/escalation_bridge.py | → | D_GOVERNANCE 生命周期管理: 适配器 / adapter (services/adapter.py) | 导入依赖 / import_depends |
| 15 | budget_enforcement.rbac_bridge — 基础设施层 RBAC 桥接适... | → | D_GOVERNANCE 生命周期管理: RBAC桥接 / rbac_bridge (agent_spec/rbac_bridge.py) | 导入依赖 / import_depends |
| 16 | ContractBus loader — 加载全部44条容量保障契约的Pydantic ... | → | D_GOVERNANCE 生命周期管理: batch2治理 / batch2_governance (contracts/batch2_governan... | 导入依赖 / import_depends |
| 17 | DatabaseService: 统一管理数据库的连接池、生命周期、健康检... | → | D_GOVERNANCE 生命周期管理: 依赖图模式 / depgraph_schema (governance/depgraph_schema.py) | 导入依赖 / import_depends |
| 18 | DatabaseService: 统一管理数据库的连接池、生命周期、健康检... | → | D_GOVERNANCE 生命周期管理: sqlite结构 / sqlite_schema (persistence/sqlite_schema.py) | 导入依赖 / import_depends |
| 19 | PreemptionManager -- 优先级抢占管理器 (pipeline/preemptio... | → | D_GOVERNANCE 生命周期管理: 任务repo / task_repo (persistence/task_repo.py) | 导入依赖 / import_depends |
| 20 | AutoRuntimeCore — 三层运行时运营中心（系统大脑） (tradin... | → | D_GOVERNANCE 生命周期管理: 模型路由器 / model_router (intelligence_governance/model_... | 导入依赖 / import_depends |
| 21 | AutoRuntimeCore — 三层运行时运营中心（系统大脑） (tradin... | → | D_GOVERNANCE 生命周期管理: 任务repo / task_repo (persistence/task_repo.py) | 导入依赖 / import_depends |
| 22 | AutoRuntimeCore — 三层运行时运营中心（系统大脑） (tradin... | → | D_GOVERNANCE 生命周期管理: 适配器 / adapter (services/adapter.py) | 导入依赖 / import_depends |
| 23 | trading/boot_hooks.py | → | D_GOVERNANCE 生命周期管理: 任务repo / task_repo (persistence/task_repo.py) | 导入依赖 / import_depends |
| 24 | resource_optimization.py - MAPE-K autonomic resource opti... | → | D_GOVERNANCE 生命周期管理: 容量治理循环 / capacity_governance_loop (capacity_governa... | 导入依赖 / import_depends |
| 25 | AssetLifecycle — MOD-INF-026 L5 ITIL生命周期自动化管理器... | → | D_GOV_AUDIT 审计追踪: 不可变审计写入器——JSONL 追加 + SHA-256 哈 / writer (gov... | 导入依赖 / import_depends |
| 26 | auto_fix_engine/engine.py | → | D_GOV_AUDIT 审计追踪: 发现模型 / finding_model (gov_audit/finding_model.py) | 导入依赖 / import_depends |
| 27 | resource_optimization.py - MAPE-K autonomic resource opti... | → | D_GOV_AUDIT 审计追踪: 写入核心审计链——治本（裁定#18 G7 + 5.37.1） / bridge (g... | 导入依赖 / import_depends |
| 28 | auto_fix_engine/state_machine.py | → | D_GOV_DRIFT 漂移检测: Drift Detector 数据模型 — drift_models.py (gov_drift/dri... | 导入依赖 / import_depends |
| 29 | ZephyrAlpha — system-telemetry/contract_metrics.py (syst... | → | D_GOV_DRIFT 漂移检测: contract_drift_detector — 契约漂移检测器。 (gov_drift/co... | 导入依赖 / import_depends |
| 30 | trading/lifecycle_manager.py | → | D_GOV_DRIFT 漂移检测: gov_audit/self_monitor.py | 导入依赖 / import_depends |
| 31 | auto_bootstrap — 全自动遥测注入钩子（MOD-INF-015 v2.1.0... | → | D_GOV_OPS_RESILIENCE 运维弹性治理: Phase Manager — ZephyrAlpha 施工阶段门控引擎. (ops_gover... | 导入依赖 / import_depends |
| 32 | AutoRuntimeCore — 三层运行时运营中心（系统大脑） (tradin... | → | D_GOV_OPS_RESILIENCE 运维弹性治理: Coldstart Manager — v0.7.0 冷启动管理器: escalation rule... | 导入依赖 / import_depends |
| 33 | trading/boot_hooks.py | → | D_GOV_OPS_RESILIENCE 运维弹性治理: F5BootIntegration — F5 自动启动/关闭集成 (MOD-INF-022 §... | 导入依赖 / import_depends |
| 34 | trading/boot_hooks.py | → | D_GOV_OPS_RESILIENCE 运维弹性治理: F5ShutdownManager — F5 自动关闭/状态持久化/信号处理 (MOD... | 导入依赖 / import_depends |
| 35 | budget_enforcement 包聚合层。 (budget_enforcement/__init_... | → | D_GOV_REPAIR 治理修复: financial_governance/budget_enforcement.py | 导入依赖 / import_depends |
| 36 | Task Lifecycle Manager — G0-G7 任务生命周期门禁。 (lifec... | → | D_GOV_RULE 规则治理: 任务类型定义 / Task Types (rule_enforcement/task_types.py) | 导入依赖 / import_depends |
| 37 | AutoRuntimeCore — 三层运行时运营中心（系统大脑） (tradin... | → | D_GOV_RULE 规则治理: 三方对齐门禁 / Triple Alignment (rule_enforcement/triple_... | 导入依赖 / import_depends |
| 38 | trading/boot_hooks.py | → | D_GOV_RULE 规则治理: 三方对齐门禁 / Triple Alignment (rule_enforcement/triple_... | 导入依赖 / import_depends |
| 39 | trading/work_orchestrator.py | → | D_GOV_RULE 规则治理: 任务类型定义 / Task Types (rule_enforcement/task_types.py) | 导入依赖 / import_depends |
| 40 | trading/boot_hooks.py | → | D_GOV_SCRIPTS 脚本治理: reconcile_generators.py — 生成器自动触发统一编排器 (gove... | 导入依赖 / import_depends |
| 41 | HealthMonitor — 健康监控 + 自愈 (trading/health_monitor.py) | → | D_INFRASTRUCTURE 跨层契约基础设施: contracts/telemetry_emitter.py | 导入依赖 / import_depends |
| 42 | AutoRuntimeCore — 三层运行时运营中心（系统大脑） (tradin... | → | D_INFRA_A2A A2A通信: A2A Card Registry — 全局 Agent Card 注册单例 (a2a_protoc... | 导入依赖 / import_depends |
| 43 | AutoRuntimeCore — 三层运行时运营中心（系统大脑） (tradin... | → | D_INFRA_A2A A2A通信: A2A 协议网关 — Agent 间请求分发与协议转换 (layer3_coordi... | 导入依赖 / import_depends |
| 44 | trading/capability_sync.py | → | D_INFRA_A2A A2A通信: A2A Registry — Agent Card 注册与发现 (layer1_discovery/a... | 导入依赖 / import_depends |
| 45 | trading/boot_hooks.py | → | D_INFRA_RECOVERY 回滚恢复: RollbackBootIntegration — 回滚系统自动启动/关闭集成 (MOD... | 导入依赖 / import_depends |
| 46 | DEPRECATED: 此文件已废弃。 (infrastructure/event_bus_upgr... | → | D_INTEGRATION 管线路由: EventBus 升级策略引擎 (events/upgrade_strategy.py) | 导入依赖 / import_depends |
| 47 | AutoRuntimeCore — 三层运行时运营中心（系统大脑） (tradin... | → | D_INTEGRATION 管线路由: EmbeddingRouter — MOD-INF-011 双嵌入维度路由 (local_mode... | 导入依赖 / import_depends |
| 48 | AutoRuntimeCore — 三层运行时运营中心（系统大脑） (tradin... | → | D_INTEGRATION 管线路由: LocalModelScheduler — L2 本地模型 24/7 调度循环 (local_m... | 导入依赖 / import_depends |
| 49 | AutoRuntimeCore — 三层运行时运营中心（系统大脑） (tradin... | → | D_INTEGRATION 管线路由: OllamaChat — 通过 Ollama HTTP API 进行本地 LLM 推理 (loc... | 导入依赖 / import_depends |
| 50 | AutoRuntimeCore — 三层运行时运营中心（系统大脑） (tradin... | → | D_INTEGRATION 管线路由: PipelineOrchestrator — M1-M11 管线协调器 (integration/pi... | 导入依赖 / import_depends |
| 51 | AutoRuntimeCore — 三层运行时运营中心（系统大脑） (tradin... | → | D_INTEGRATION 管线路由: InProcessVectorMemory — MOD-INF-011 VMS 统一入口 (vector... | 导入依赖 / import_depends |
| 52 | AutoTaskGenerator — 自动任务生成器 (trading/auto_task_ge... | → | D_INTEGRATION 管线路由: LocalModelScheduler — L2 本地模型 24/7 调度循环 (local_m... | 导入依赖 / import_depends |
| 53 | trading/runtime_config.py | → | D_INTEGRATION 管线路由: contracts/runtime_types.py | 导入依赖 / import_depends |
| 54 | AutoRuntimeCore — 三层运行时运营中心（系统大脑） (tradin... | → | D_INTELLIGENCE 上下文管理: Results Writer — 持久化 benchmark 结果，支持历史对比（漂... | 导入依赖 / import_depends |
| 55 | AutoRuntimeCore — 三层运行时运营中心（系统大脑） (tradin... | → | D_INTELLIGENCE 上下文管理: ModelTaskMatrix — 任务×模型性能学习引擎 (model_profilin... | 导入依赖 / import_depends |
| 56 | TaskGate --- 任务门控 (trading/task_gate.py) | → | D_INTELLIGENCE 上下文管理: CapabilityPassport --- AI 模型能力护照 (model_profiling/c... | 导入依赖 / import_depends |
| 57 | trading/boot_hooks.py | → | D_OPS 反馈循环: Budget Enforcer core engine — MOD-INF-024 (ops_governanc... | 导入依赖 / import_depends |
| 58 | trading/boot_hooks.py | → | D_ORCHESTRATOR 代理编排器: Orc->VMS 记忆写入器 (execution/memory_writer.py) | 导入依赖 / import_depends |
| 59 | AutoRuntimeCore — 三层运行时运营中心（系统大脑） (tradin... | → | D_SECURITY 对抗验证: GenesisBootstrap — RBAC系统启动引导器. (access_control/g... | 导入依赖 / import_depends |
| 60 | trading/boot_hooks.py | → | D_SECURITY 对抗验证: GenesisBootstrap — RBAC系统启动引导器. (access_control/g... | 导入依赖 / import_depends |
| 61 | trading/boot_hooks.py | → | D_SECURITY 对抗验证: KillSwitch — 熔断器. (access_control/kill_switch.py) | 导入依赖 / import_depends |
| 62 | trading/boot_hooks.py | → | D_SECURITY 对抗验证: NonRepudiation — 不可抵赖性审计签名. (access_control/non... | 导入依赖 / import_depends |
| 63 | trading/boot_hooks.py | → | D_SECURITY 对抗验证: CommitTrigger — 事件驱动红蓝对抗触发器 (MOD-INF-030). (a... | 导入依赖 / import_depends |
| 64 | Asset Inventory CLI — MOD-INF-026 蓝图 §31 (asset_inven... | → | D_SHARED 共享服务: process_pool.py - Shared process pool for MCP servers and... | 导入依赖 / import_depends |
| 65 | Asset Inventory CLI — MOD-INF-026 蓝图 §31 (asset_inven... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 66 | Asset Inventory CLI — MOD-INF-026 蓝图 §31 (asset_inven... | → | D_SHARED 共享服务: serialization.py —— 统一序列化/反序列化基础设施（Phase ... | 导入依赖 / import_depends |
| 67 | AssetClassifier — MOD-INF-026 L2 资产自动分类器 (asset_i... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 68 | AssetDashboard — MOD-INF-026 资产健康仪表盘生成器 (asset... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 69 | UnifiedAssetIndex — MOD-INF-026 L3 统一资产索引生成器 (a... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 70 | AssetLifecycle — MOD-INF-026 L5 ITIL生命周期自动化管理器... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 71 | AssetInventory MCP Server — MOD-INF-026 蓝图 §21 (asset... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 72 | asset_inventory/metadata.py | → | D_SHARED 共享服务: process_pool.py - Shared process pool for MCP servers and... | 导入依赖 / import_depends |
| 73 | ReconciliationEngine — MOD-INF-026 L4 注册表 vs 磁盘对账... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 74 | MOD-INF-026 §17 — 24 个异构注册表统一解析适配器。 (asse... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 75 | MOD-INF-026 §17 — 24 个异构注册表统一解析适配器。 (asse... | → | D_SHARED 共享服务: SQLite 连接工厂真源（SSoT） (io/sqlite_factory.py) | 导入依赖 / import_depends |
| 76 | AssetDiscoveryScanner — MOD-INF-026 L1 全量文件系统扫描... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 77 | AssetInventoryTelemetry — MOD-INF-026 自监控指标 (asset_... | → | D_SHARED 共享服务: secrets.py —— Secrets 管理抽象（Phase 7 新增 | 盲点 B12... | 导入依赖 / import_depends |
| 78 | asset_inventory/trust_anchor.py | → | D_SHARED 共享服务: process_pool.py - Shared process pool for MCP servers and... | 导入依赖 / import_depends |
| 79 | asset_inventory/trust_anchor.py | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 80 | auto_fix_engine/alignment_syncer.py | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 81 | auto_fix_engine/all_completer.py | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 82 | auto_fix_engine/compliance_auditor.py | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 83 | auto_fix_engine/compliance_auditor.py | → | D_SHARED 共享服务: SQLite 连接工厂真源（SSoT） (io/sqlite_factory.py) | 导入依赖 / import_depends |
| 84 | auto_fix_engine/config_fixer.py | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 85 | auto_fix_engine/dedup_extractor.py | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 86 | auto_fix_engine/dep_version_fixer.py | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 87 | auto_fix_engine/drift_fixer.py | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 88 | auto_fix_engine/event_hooks.py | → | D_SHARED 共享服务: EventBus — 事件总线（带背压控制）(M-07) (shared/event_bu... | 导入依赖 / import_depends |
| 89 | auto_fix_engine/fix_budget.py | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 90 | auto_fix_engine/fix_budget.py | → | D_SHARED 共享服务: SQLite 连接工厂真源（SSoT） (io/sqlite_factory.py) | 导入依赖 / import_depends |
| 91 | auto_fix_engine/fix_health_check.py | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 92 | auto_fix_engine/fix_health_check.py | → | D_SHARED 共享服务: SQLite 连接工厂真源（SSoT） (io/sqlite_factory.py) | 导入依赖 / import_depends |
| 93 | auto_fix_engine/fix_pattern_miner.py | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 94 | auto_fix_engine/fix_pattern_miner.py | → | D_SHARED 共享服务: SQLite 连接工厂真源（SSoT） (io/sqlite_factory.py) | 导入依赖 / import_depends |
| 95 | auto_fix_engine/fix_reliability.py | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 96 | auto_fix_engine/fix_reliability.py | → | D_SHARED 共享服务: SQLite 连接工厂真源（SSoT） (io/sqlite_factory.py) | 导入依赖 / import_depends |
| 97 | auto_fix_engine/fix_safety.py | → | D_SHARED 共享服务: process_pool.py - Shared process pool for MCP servers and... | 导入依赖 / import_depends |
| 98 | auto_fix_engine/fix_safety.py | → | D_SHARED 共享服务: file_utils.py —— 安全文件操作工具（Phase 3 新增 | 盲点 ... | 导入依赖 / import_depends |
| 99 | auto_fix_engine/import_fixer.py | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 100 | auto_fix_engine/interrupt_guard.py | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 101 | auto_fix_engine/llm_fix_adapter.py | → | D_SHARED 共享服务: LLMGatewayProtocol — LLM 网关抽象接口 (contracts/llm_gat... | 导入依赖 / import_depends |
| 102 | auto_fix_engine/scaffold_registrar.py | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 103 | auto_fix_engine/shadow_workspace.py | → | D_SHARED 共享服务: process_pool.py - Shared process pool for MCP servers and... | 导入依赖 / import_depends |
| 104 | auto_fix_engine/shadow_workspace.py | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 105 | auto_fix_engine/zombie_cleaner.py | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 106 | Risk mitigation — R1~R16 全量风险缓解实现（对标蓝图 §14... | → | D_SHARED 共享服务: SQLite 连接工厂真源（SSoT） (io/sqlite_factory.py) | 导入依赖 / import_depends |
| 107 | SchemaManager — 容量保障体系数据库 Schema 管理器 (capaci... | → | D_SHARED 共享服务: SQLite 连接工厂真源（SSoT） (io/sqlite_factory.py) | 导入依赖 / import_depends |
| 108 | RI-15 CostTracker — 成本追踪器 (infrastructure/cost_trac... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 109 | RI-15 CostTracker — 成本追踪器 (infrastructure/cost_trac... | → | D_SHARED 共享服务: SQLite 连接工厂真源（SSoT） (io/sqlite_factory.py) | 导入依赖 / import_depends |
| 110 | DatabaseService: 统一管理数据库的连接池、生命周期、健康检... | → | D_SHARED 共享服务: DatabaseCRUDMixin: 共享的 governance.db + depgraph CRUD ... | 导入依赖 / import_depends |
| 111 | DatabaseService: 统一管理数据库的连接池、生命周期、健康检... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 112 | DEPRECATED: 此文件已废弃。 (infrastructure/event_bus_upgr... | → | D_SHARED 共享服务: EventBus 升级策略引擎 (events/upgrade_strategy.py) | 导入依赖 / import_depends |
| 113 | RI-13 EventStore — 事件存储 (infrastructure/event_store.py) | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 114 | RI-13 EventStore — 事件存储 (infrastructure/event_store.py) | → | D_SHARED 共享服务: SQLite 连接工厂真源（SSoT） (io/sqlite_factory.py) | 导入依赖 / import_depends |
| 115 | RI-13 EventStore — 事件存储 (infrastructure/event_store.py) | → | D_SHARED 共享服务: time_utils.py —— 时间/日期工具（Phase 9 新增 | 盲点 B19... | 导入依赖 / import_depends |
| 116 | Event Store — 事件持久化存储。 (events/event_store.py) | → | D_SHARED 共享服务: EventBus — 事件总线（带背压控制）(M-07) (shared/event_bu... | 导入依赖 / import_depends |
| 117 | Event Store — 事件持久化存储。 (events/event_store.py) | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 118 | infrastructure/file_watcher.py | → | D_SHARED 共享服务: ZephyrAlpha 蓝图拆解器 (blueprint_tools/blueprint_decompo... | 导入依赖 / import_depends |
| 119 | infrastructure/file_watcher.py | → | D_SHARED 共享服务: EventBus — 事件总线（带背压控制）(M-07) (shared/event_bu... | 导入依赖 / import_depends |
| 120 | infrastructure/file_watcher.py | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 121 | infrastructure/file_watcher.py | → | D_SHARED 共享服务: registry — 运行时 DI 容器 (protocols/registry.py) | 导入依赖 / import_depends |
| 122 | Finding->TaskCard 桥接器 (infrastructure/finding_task_bri... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 123 | Finding->TaskCard 桥接器 (infrastructure/finding_task_bri... | → | D_SHARED 共享服务: registry — 运行时 DI 容器 (protocols/registry.py) | 导入依赖 / import_depends |
| 124 | Finding->TaskCard 桥接器 (infrastructure/finding_task_bri... | → | D_SHARED 共享服务: schema/schemas.py | 导入依赖 / import_depends |
| 125 | Finding->TaskCard 桥接器 (infrastructure/finding_task_bri... | → | D_SHARED 共享服务: task_types — 任务系统核心类型 re-export 层 (schema/task_... | 导入依赖 / import_depends |
| 126 | git_batcher.py — Git 命令批量化工具（ARCH-GIT-CALL-BUDGE... | → | D_SHARED 共享服务: process_pool.py - Shared process pool for MCP servers and... | 导入依赖 / import_depends |
| 127 | Kill Switch T0 Hardware Simulator (infrastructure/kill_sw... | → | D_SHARED 共享服务: time_utils.py —— 时间/日期工具（Phase 9 新增 | 盲点 B19... | 导入依赖 / import_depends |
| 128 | Notifier — 多渠道 Owner 通知。 (observability/notifier.py) | → | D_SHARED 共享服务: EventBus — 事件总线（带背压控制）(M-07) (shared/event_bu... | 导入依赖 / import_depends |
| 129 | Notifier — 多渠道 Owner 通知。 (observability/notifier.py) | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 130 | observability/trace_decorator.py | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 131 | backpressure_types.py - Pipeline backpressure signal data... | → | D_SHARED 共享服务: core/trace_context.py | 导入依赖 / import_depends |
| 132 | CT-PIPE-ORC-001 — TaskCard -> 管线入口节点路由 (pipeline... | → | D_SHARED 共享服务: ZephyrAlpha 任务系统核心数据模型 (foundation/models.py) | 导入依赖 / import_depends |
| 133 | CT-PIPE-ORC-001 — TaskCard -> 管线入口节点路由 (pipeline... | → | D_SHARED 共享服务: yaml_utils.py — vocabulary YAML 加载公共工具（SSoT 真源... | 导入依赖 / import_depends |
| 134 | CT-PIPE-ORC-001 — TaskCard -> 管线入口节点路由 (pipeline... | → | D_SHARED 共享服务: schema/schemas.py | 导入依赖 / import_depends |
| 135 | MOD-INF-019: Agent Spec — LLM Gateway (pipeline/llm_gate... | → | D_SHARED 共享服务: constants.py —— 共享枚举 & 常量集中 re-export（Single S... | 导入依赖 / import_depends |
| 136 | MOD-INF-019: Agent Spec — LLM Gateway (pipeline/llm_gate... | → | D_SHARED 共享服务: foundation/env.py | 导入依赖 / import_depends |
| 137 | MOD-INF-019: Agent Spec — LLM Gateway (pipeline/llm_gate... | → | D_SHARED 共享服务: secrets.py —— Secrets 管理抽象（Phase 7 新增 | 盲点 B12... | 导入依赖 / import_depends |
| 138 | MOD-INF-019: Agent Spec — LLM Gateway (pipeline/llm_gate... | → | D_SHARED 共享服务: async_utils.py — async/sync 边界桥接（5.12.8 修复） (uti... | 导入依赖 / import_depends |
| 139 | ModelRouter — 模型路由与降级链管理 (pipeline/model_route... | → | D_SHARED 共享服务: ZephyrAlpha 任务系统核心数据模型 (foundation/models.py) | 导入依赖 / import_depends |
| 140 | Pipeline 数据模型 (pipeline/models.py) | → | D_SHARED 共享服务: schema/schemas.py | 导入依赖 / import_depends |
| 141 | Pipeline 数据模型 (pipeline/models.py) | → | D_SHARED 共享服务: time_utils.py —— 时间/日期工具（Phase 9 新增 | 盲点 B19... | 导入依赖 / import_depends |
| 142 | Pipeline Lock — 双管线并发锁 (pipeline/pipeline_lock.py) | → | D_SHARED 共享服务: lock.py —— 分布式锁抽象（Phase 10 新增 | 盲点 B23 修复... | 导入依赖 / import_depends |
| 143 | PreemptionManager -- 优先级抢占管理器 (pipeline/preemptio... | → | D_SHARED 共享服务: serialization.py —— 统一序列化/反序列化基础设施（Phase ... | 导入依赖 / import_depends |
| 144 | PreemptionManager -- 优先级抢占管理器 (pipeline/preemptio... | → | D_SHARED 共享服务: task_types — 任务系统核心类型 re-export 层 (schema/task_... | 导入依赖 / import_depends |
| 145 | PreemptionManager -- 优先级抢占管理器 (pipeline/preemptio... | → | D_SHARED 共享服务: time_utils.py —— 时间/日期工具（Phase 9 新增 | 盲点 B19... | 导入依赖 / import_depends |
| 146 | Pipeline Routing Plugin System — K8s Scheduling Framewor... | → | D_SHARED 共享服务: yaml_utils.py — vocabulary YAML 加载公共工具（SSoT 真源... | 导入依赖 / import_depends |
| 147 | Task Queue — 后台任务队列 + 自动 Dispatch。 (queue/task_... | → | D_SHARED 共享服务: EventBus — 事件总线（带背压控制）(M-07) (shared/event_bu... | 导入依赖 / import_depends |
| 148 | Task Queue — 后台任务队列 + 自动 Dispatch。 (queue/task_... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 149 | Task Scheduler — 任务调度器。 (queue/task_scheduler.py) | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 150 | Redis 连接配置单真源加载器（H1 业务热缓存 INFRA-DB-007）... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 151 | Redis 连接配置单真源加载器（H1 业务热缓存 INFRA-DB-007）... | → | D_SHARED 共享服务: secrets.py —— Secrets 管理抽象（Phase 7 新增 | 盲点 B12... | 导入依赖 / import_depends |
| 152 | Finding Schema — 审计发现标准化数据模型 (script_system/f... | → | D_SHARED 共享服务: schema/schemas.py | 导入依赖 / import_depends |
| 153 | SLA Monitor — 服务等级协议 (SLA) 监控 RTO/RPO。 (sla/sla... | → | D_SHARED 共享服务: EventBus — 事件总线（带背压控制）(M-07) (shared/event_bu... | 导入依赖 / import_depends |
| 154 | SLA Monitor — 服务等级协议 (SLA) 监控 RTO/RPO。 (sla/sla... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 155 | 遥测 · archive/cold_stub — 冷存储归档管道。 (archive/co... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 156 | auto_bootstrap — 全自动遥测注入钩子（MOD-INF-015 v2.1.0... | → | D_SHARED 共享服务: serialization.py —— 统一序列化/反序列化基础设施（Phase ... | 导入依赖 / import_depends |
| 157 | auto_bootstrap — 全自动遥测注入钩子（MOD-INF-015 v2.1.0... | → | D_SHARED 共享服务: SessionContinuity — Session 交接包自动生成与恢复 (sessio... | 导入依赖 / import_depends |
| 158 | Telemetry — 系统遥测门面类（MOD-INF-015 v2.1.0） (system... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 159 | Telemetry — 系统遥测门面类（MOD-INF-015 v2.1.0） (system... | → | D_SHARED 共享服务: serialization.py —— 统一序列化/反序列化基础设施（Phase ... | 导入依赖 / import_depends |
| 160 | 健康聚合器（Health Aggregator） (system_telemetry/health_... | → | D_SHARED 共享服务: EventBus — 事件总线（带背压控制）(M-07) (shared/event_bu... | 导入依赖 / import_depends |
| 161 | 三态健康探针协议（Health Probes — CT-HEALTH-001） (syste... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 162 | blueprint_metrics — 蓝图使用追踪 instrumentation (metric... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 163 | TELE->FLE 指标桥接 — emit_metrics() 生产者 (system_telem... | → | D_SHARED 共享服务: registry — 运行时 DI 容器 (protocols/registry.py) | 导入依赖 / import_depends |
| 164 | 遥测 · traces/span_stub — W3C TraceContext 分布式追踪管... | → | D_SHARED 共享服务: logging.py —— ZephyrAlpha 结构化日志系统（Structured JS... | 导入依赖 / import_depends |
| 165 | 三冗余 Watchdog（CT-WATCHDOG-001）——互检+Panic Mode+Dea... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 166 | ActionDispatcher --- 大脑的"手" v2.0 (Phase 2) (trading/a... | → | D_SHARED 共享服务: process_pool.py - Shared process pool for MCP servers and... | 导入依赖 / import_depends |
| 167 | ActionDispatcher --- 大脑的"手" v2.0 (Phase 2) (trading/a... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 168 | ActionDispatcher --- 大脑的"手" v2.0 (Phase 2) (trading/a... | → | D_SHARED 共享服务: serialization.py —— 统一序列化/反序列化基础设施（Phase ... | 导入依赖 / import_depends |
| 169 | ActionDispatcher --- 大脑的"手" v2.0 (Phase 2) (trading/a... | → | D_SHARED 共享服务: task_types — 任务系统核心类型 re-export 层 (schema/task_... | 导入依赖 / import_depends |
| 170 | AiAuditLogger — AI 行为审计日志 (trading/ai_audit_logger.py) | → | D_SHARED 共享服务: serialization.py —— 统一序列化/反序列化基础设施（Phase ... | 导入依赖 / import_depends |
| 171 | AiAuditLogger — AI 行为审计日志 (trading/ai_audit_logger.py) | → | D_SHARED 共享服务: schema/schemas.py | 导入依赖 / import_depends |
| 172 | AiAuditLogger — AI 行为审计日志 (trading/ai_audit_logger.py) | → | D_SHARED 共享服务: time_utils.py —— 时间/日期工具（Phase 9 新增 | 盲点 B19... | 导入依赖 / import_depends |
| 173 | AutoIntegrator — 自动接入器 (trading/auto_integrator.py) | → | D_SHARED 共享服务: time_utils.py —— 时间/日期工具（Phase 9 新增 | 盲点 B19... | 导入依赖 / import_depends |
| 174 | AutoRuntimeCore — 三层运行时运营中心（系统大脑） (tradin... | → | D_SHARED 共享服务: core/system_configuration.py | 导入依赖 / import_depends |
| 175 | AutoRuntimeCore — 三层运行时运营中心（系统大脑） (tradin... | → | D_SHARED 共享服务: TaskRepositoryProtocol — TaskRepository 的 Protocol 接口... | 导入依赖 / import_depends |
| 176 | AutoRuntimeCore — 三层运行时运营中心（系统大脑） (tradin... | → | D_SHARED 共享服务: EventBus — 事件总线（带背压控制）(M-07) (shared/event_bu... | 导入依赖 / import_depends |
| 177 | AutoRuntimeCore — 三层运行时运营中心（系统大脑） (tradin... | → | D_SHARED 共享服务: constants.py —— 共享枚举 & 常量集中 re-export（Single S... | 导入依赖 / import_depends |
| 178 | AutoRuntimeCore — 三层运行时运营中心（系统大脑） (tradin... | → | D_SHARED 共享服务: process_pool.py - Shared process pool for MCP servers and... | 导入依赖 / import_depends |
| 179 | AutoRuntimeCore — 三层运行时运营中心（系统大脑） (tradin... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 180 | AutoRuntimeCore — 三层运行时运营中心（系统大脑） (tradin... | → | D_SHARED 共享服务: A2A Registry and Agent Card contracts — discovery and id... | 导入依赖 / import_depends |
| 181 | AutoTaskGenerator — 自动任务生成器 (trading/auto_task_ge... | → | D_SHARED 共享服务: EventBus — 事件总线（带背压控制）(M-07) (shared/event_bu... | 导入依赖 / import_depends |
| 182 | AutoTaskGenerator — 自动任务生成器 (trading/auto_task_ge... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 183 | trading/boot_hooks.py | → | D_SHARED 共享服务: TaskRepositoryProtocol — TaskRepository 的 Protocol 接口... | 导入依赖 / import_depends |
| 184 | trading/boot_hooks.py | → | D_SHARED 共享服务: EventBus — 事件总线（带背压控制）(M-07) (shared/event_bu... | 导入依赖 / import_depends |
| 185 | trading/boot_hooks.py | → | D_SHARED 共享服务: constants.py —— 共享枚举 & 常量集中 re-export（Single S... | 导入依赖 / import_depends |
| 186 | trading/boot_hooks.py | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 187 | trading/boot_hooks.py | → | D_SHARED 共享服务: health.py —— ZephyrAlpha 聚合健康检查 (lifecycle/health.py) | 导入依赖 / import_depends |
| 188 | trading/boot_hooks.py | → | D_SHARED 共享服务: CT-HEALTH-001: System-wide Health Discovery Registration.... | 导入依赖 / import_depends |
| 189 | trading/boot_hooks.py | → | D_SHARED 共享服务: lifecycle/healthcheck_service.py | 导入依赖 / import_depends |
| 190 | trading/boot_hooks.py | → | D_SHARED 共享服务: lifecycle/longevity_monitor.py | 导入依赖 / import_depends |
| 191 | trading/boot_hooks.py | → | D_SHARED 共享服务: Autonomy Monitor — AI 自主等级监控与降级。 (maintenance/... | 导入依赖 / import_depends |
| 192 | trading/boot_hooks.py | → | D_SHARED 共享服务: metrics.py —— 轻量级 Metrics 收集基础设施（Phase 9 新增... | 导入依赖 / import_depends |
| 193 | CapabilityCard — 能力卡片数据模型 (trading/capability_ca... | → | D_SHARED 共享服务: schema/schemas.py | 导入依赖 / import_depends |
| 194 | CapabilityCard — 能力卡片数据模型 (trading/capability_ca... | → | D_SHARED 共享服务: time_utils.py —— 时间/日期工具（Phase 9 新增 | 盲点 B19... | 导入依赖 / import_depends |
| 195 | CapabilityRegistry — 能力注册中心 (trading/capability_re... | → | D_SHARED 共享服务: serialization.py —— 统一序列化/反序列化基础设施（Phase ... | 导入依赖 / import_depends |
| 196 | DreamCycle — 知识固化引擎 (trading/dream_cycle.py) | → | D_SHARED 共享服务: schema/schemas.py | 导入依赖 / import_depends |
| 197 | DreamCycle — 知识固化引擎 (trading/dream_cycle.py) | → | D_SHARED 共享服务: time_utils.py —— 时间/日期工具（Phase 9 新增 | 盲点 B19... | 导入依赖 / import_depends |
| 198 | Finalizer — 优雅清理器 (trading/finalizer.py) | → | D_SHARED 共享服务: health.py —— ZephyrAlpha 聚合健康检查 (lifecycle/health.py) | 导入依赖 / import_depends |
| 199 | Finalizer — 优雅清理器 (trading/finalizer.py) | → | D_SHARED 共享服务: metrics.py —— 轻量级 Metrics 收集基础设施（Phase 9 新增... | 导入依赖 / import_depends |
| 200 | HealthMonitor — 健康监控 + 自愈 (trading/health_monitor.py) | → | D_SHARED 共享服务: EventBus — 事件总线（带背压控制）(M-07) (shared/event_bu... | 导入依赖 / import_depends |
| 201 | HealthMonitor — 健康监控 + 自愈 (trading/health_monitor.py) | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 202 | HealthMonitor — 健康监控 + 自愈 (trading/health_monitor.py) | → | D_SHARED 共享服务: lifecycle/healthcheck_service.py | 导入依赖 / import_depends |
| 203 | HealthMonitor — 健康监控 + 自愈 (trading/health_monitor.py) | → | D_SHARED 共享服务: lifecycle/longevity_monitor.py | 导入依赖 / import_depends |
| 204 | HealthMonitor — 健康监控 + 自愈 (trading/health_monitor.py) | → | D_SHARED 共享服务: metrics.py —— 轻量级 Metrics 收集基础设施（Phase 9 新增... | 导入依赖 / import_depends |
| 205 | HealthMonitor — 健康监控 + 自愈 (trading/health_monitor.py) | → | D_SHARED 共享服务: schema/schemas.py | 导入依赖 / import_depends |
| 206 | HealthMonitor — 健康监控 + 自愈 (trading/health_monitor.py) | → | D_SHARED 共享服务: time_utils.py —— 时间/日期工具（Phase 9 新增 | 盲点 B19... | 导入依赖 / import_depends |
| 207 | IntegrationRegistry — 集成注册表 (trading/integration_re... | → | D_SHARED 共享服务: schema/schemas.py | 导入依赖 / import_depends |
| 208 | trading/lifecycle_manager.py | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 209 | NightShiftQueue — 夜班登记表持久化 (trading/night_shift_... | → | D_SHARED 共享服务: serialization.py —— 统一序列化/反序列化基础设施（Phase ... | 导入依赖 / import_depends |
| 210 | NightShiftQueue — 夜班登记表持久化 (trading/night_shift_... | → | D_SHARED 共享服务: schema/schemas.py | 导入依赖 / import_depends |
| 211 | NightShiftQueue — 夜班登记表持久化 (trading/night_shift_... | → | D_SHARED 共享服务: time_utils.py —— 时间/日期工具（Phase 9 新增 | 盲点 B19... | 导入依赖 / import_depends |
| 212 | Protocol-based interface layer for runtime->pipeline depe... | → | D_SHARED 共享服务: task_types — 任务系统核心类型 re-export 层 (schema/task_... | 导入依赖 / import_depends |
| 213 | resource_optimization.py - MAPE-K autonomic resource opti... | → | D_SHARED 共享服务: capacity_governance/capacity_calibrator.py | 导入依赖 / import_depends |
| 214 | resource_optimization.py - MAPE-K autonomic resource opti... | → | D_SHARED 共享服务: capacity_governance/capacity_digital_twin.py | 导入依赖 / import_depends |
| 215 | resource_optimization.py - MAPE-K autonomic resource opti... | → | D_SHARED 共享服务: capacity_governance/capacity_fingerprint.py | 导入依赖 / import_depends |
| 216 | resource_optimization.py - MAPE-K autonomic resource opti... | → | D_SHARED 共享服务: capacity_governance/capacity_runbook_generator.py | 导入依赖 / import_depends |
| 217 | resource_optimization.py - MAPE-K autonomic resource opti... | → | D_SHARED 共享服务: capacity_governance/model_capacity_probe.py | 导入依赖 / import_depends |
| 218 | resource_optimization.py - MAPE-K autonomic resource opti... | → | D_SHARED 共享服务: EventBus — 事件总线（带背压控制）(M-07) (shared/event_bu... | 导入依赖 / import_depends |
| 219 | resource_optimization.py - MAPE-K autonomic resource opti... | → | D_SHARED 共享服务: process_pool.py - Shared process pool for MCP servers and... | 导入依赖 / import_depends |
| 220 | resource_optimization.py - MAPE-K autonomic resource opti... | → | D_SHARED 共享服务: io_cache.py - File-level I/O cache with LRU eviction (io/... | 导入依赖 / import_depends |
| 221 | StagingArea — 多AI并发草稿写入+提交+冲突检测模块（CT-SES... | → | D_SHARED 共享服务: lock.py —— 分布式锁抽象（Phase 10 新增 | 盲点 B23 修复... | 导入依赖 / import_depends |
| 222 | StatusDashboard — 实时状态面板 (trading/status_dashboard.py) | → | D_SHARED 共享服务: time_utils.py —— 时间/日期工具（Phase 9 新增 | 盲点 B19... | 导入依赖 / import_depends |
| 223 | StopGate — 质量闸门 (trading/stop_gate.py) | → | D_SHARED 共享服务: time_utils.py —— 时间/日期工具（Phase 9 新增 | 盲点 B19... | 导入依赖 / import_depends |
| 224 | WindowsService — Windows Service 包装器 (trading/windows... | → | D_SHARED 共享服务: process_pool.py - Shared process pool for MCP servers and... | 导入依赖 / import_depends |
| 225 | WorkDAG + WorkItem — 工作编排数据模型 (trading/work_dag.py) | → | D_SHARED 共享服务: schema/schemas.py | 导入依赖 / import_depends |
| 226 | trading/work_orchestrator.py | → | D_SHARED 共享服务: serialization.py —— 统一序列化/反序列化基础设施（Phase ... | 导入依赖 / import_depends |
| 227 | trading/work_orchestrator.py | → | D_SHARED 共享服务: time_utils.py —— 时间/日期工具（Phase 9 新增 | 盲点 B19... | 导入依赖 / import_depends |
| 228 | zombie_scanner.py — 僵尸 Python 进程检测与自动处置 (trad... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 229 | trading/boot_hooks.py | → | D_TRADING 交易运营: ide_health_daemon.py — TRAE IDE 幽灵窗口守护线程 (tradin... | 导入依赖 / import_depends |
| 230 | resource_optimization.py - MAPE-K autonomic resource opti... | → | D_TRADING 交易运营: gpu_monitor.py — NVIDIA GPU 状态采集器 (trading/gpu_moni... | 导入依赖 / import_depends |
| 231 | resource_optimization.py - MAPE-K autonomic resource opti... | → | D_TRADING 交易运营: ide_health_daemon.py — TRAE IDE 幽灵窗口守护线程 (tradin... | 导入依赖 / import_depends |

### 依赖本域的其他域（入边）/ Depended By

| # | 外部域-源模块 / Source Module | → | 本域模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | D_AUTONOMY_CORE 自治核心: 上下文assembler / context_assembler (context/context_asse... | → | token_budget.py — Token 估算工具 SSoT (capacity_assuranc... | 导入依赖 / import_depends |
| 2 | D_AUTONOMY_CORE 自治核心: 上下文预算 / TruncationStrategy — TruncationStrategy (co... | → | token_budget.py — Token 估算工具 SSoT (capacity_assuranc... | 导入依赖 / import_depends |
| 3 | D_AUTONOMY_CORE 自治核心: 上下文预算追踪器 / ContextBudgetTracker: token budget man... | → | token_budget.py — Token 估算工具 SSoT (capacity_assuranc... | 导入依赖 / import_depends |
| 4 | D_AUTONOMY_CORE 自治核心: 上下文injector / ContextInjector: retrieve and inject rel... | → | token_budget.py — Token 估算工具 SSoT (capacity_assuranc... | 导入依赖 / import_depends |
| 5 | D_AUTONOMY_CORE 自治核心: 上下文管线 / context_pipeline (context/context_pipeline.py) | → | token_budget.py — Token 估算工具 SSoT (capacity_assuranc... | 导入依赖 / import_depends |
| 6 | D_AUTONOMY_CORE 自治核心: 上下文管线自动 / context_pipeline_auto (context/context_p... | → | kill_switch.py -- safety circuit breaker (DD110, TASK-019... | 导入依赖 / import_depends |
| 7 | D_AUTONOMY_CORE 自治核心: 提示注册表 / prompt_registry (autonomy_core/prompt_regist... | → | token_budget.py — Token 估算工具 SSoT (capacity_assuranc... | 导入依赖 / import_depends |
| 8 | D_AUTONOMY_CORE 自治核心: 测试自动运行时端到端 / test_auto_runtime_e2e (automation/... | → | AutoRuntimeCore — 三层运行时运营中心（系统大脑） (tradin... | 测试依赖 / test_depends |
| 9 | D_AUTONOMY_CORE 自治核心: 测试自动运行时端到端 / test_auto_runtime_e2e (automation/... | → | CapabilityRegistry — 能力注册中心 (trading/capability_re... | 测试依赖 / test_depends |
| 10 | D_AUTONOMY_CORE 自治核心: 测试自动运行时端到端 / test_auto_runtime_e2e (automation/... | → | DreamCycle — 知识固化引擎 (trading/dream_cycle.py) | 测试依赖 / test_depends |
| 11 | D_AUTONOMY_CORE 自治核心: 测试自动运行时端到端 / test_auto_runtime_e2e (automation/... | → | HealthMonitor — 健康监控 + 自愈 (trading/health_monitor.py) | 测试依赖 / test_depends |
| 12 | D_AUTONOMY_CORE 自治核心: 测试自动运行时端到端 / test_auto_runtime_e2e (automation/... | → | trading/runtime_config.py | 测试依赖 / test_depends |
| 13 | D_AUTONOMY_CORE 自治核心: 测试自动运行时端到端 / test_auto_runtime_e2e (automation/... | → | WorkDAG + WorkItem — 工作编排数据模型 (trading/work_dag.py) | 测试依赖 / test_depends |
| 14 | D_AUTONOMY_CORE 自治核心: 测试自动运行时端到端 / test_auto_runtime_e2e (automation/... | → | trading/work_orchestrator.py | 测试依赖 / test_depends |
| 15 | D_AUTONOMY_CORE 自治核心: F14 管线编排/反馈环 — 红蓝对抗端到端极端测试 / test_f14_... | → | Pipeline — Backpressure Manager (pipeline/backpressure_m... | 测试依赖 / test_depends |
| 16 | D_AUTONOMY_CORE 自治核心: F14 管线编排/反馈环 — 红蓝对抗端到端极端测试 / test_f14_... | → | backpressure_types.py - Pipeline backpressure signal data... | 测试依赖 / test_depends |
| 17 | D_AUTONOMY_CORE 自治核心: F14 管线编排/反馈环 — 红蓝对抗端到端极端测试 / test_f14_... | → | DeadLetterQueue — 死信队列 (pipeline/dead_letter_queue.py) | 测试依赖 / test_depends |
| 18 | D_AUTONOMY_CORE 自治核心: F14 管线编排/反馈环 — 红蓝对抗端到端极端测试 / test_f14_... | → | Pipeline 数据模型 (pipeline/models.py) | 测试依赖 / test_depends |
| 19 | D_AUTONOMY_CORE 自治核心: F1 自动驾驶/运行时大脑 — 红蓝对抗端到端极端测试 / test_f... | → | DreamCycle — 知识固化引擎 (trading/dream_cycle.py) | 测试依赖 / test_depends |
| 20 | D_AUTONOMY_CORE 自治核心: F1 自动驾驶/运行时大脑 — 红蓝对抗端到端极端测试 / test_f... | → | HealthMonitor — 健康监控 + 自愈 (trading/health_monitor.py) | 测试依赖 / test_depends |
| 21 | D_AUTONOMY_CORE 自治核心: F1 自动驾驶/运行时大脑 — 红蓝对抗端到端极端测试 / test_f... | → | WorkDAG + WorkItem — 工作编排数据模型 (trading/work_dag.py) | 测试依赖 / test_depends |
| 22 | D_AUTONOMY_CORE 自治核心: F1 自动驾驶/运行时大脑 — 红蓝对抗端到端极端测试 / test_f... | → | trading/work_orchestrator.py | 测试依赖 / test_depends |
| 23 | D_BACKTEST 回测: 数据处理器 / data_handler (core/data_handler.py) | → | DatabaseService: 统一管理数据库的连接池、生命周期、健康检... | 导入依赖 / import_depends |
| 24 | D_COMPLIANCE 合规: 包入口 / __init__ (behavioral_auditor/__init__.py) | → | auto_fix_engine/state_machine.py | 导入依赖 / import_depends |
| 25 | D_FACTOR 因子: 盘中因子调度循环——3秒拉 tick → DataFrame → DagExecuto... | → | H1 Redis 集成适配器——连接 D-FACTOR/SIGNAL/RISK 与 H1 热... | 导入依赖 / import_depends |
| 26 | D_FACTOR 因子: 盘中因子调度循环——3秒拉 tick → DataFrame → DagExecuto... | → | H1 Redis 热缓存 Key Schema（DDL-as-Code）。 (h1_redis_hot... | 导入依赖 / import_depends |
| 27 | D_FEEDBACK_LOOP 反馈循环引擎: 背压桥接 / backpressure_bridge (feedback_loop/backpressur... | → | Pipeline — Backpressure Manager (pipeline/backpressure_m... | 导入依赖 / import_depends |
| 28 | D_FEEDBACK_LOOP 反馈循环引擎: db写入器 / db_writer (feedback_loop/db_writer.py) | → | TELE->FLE 指标桥接 — emit_metrics() 生产者 (system_telem... | 导入依赖 / import_depends |
| 29 | D_FEEDBACK_LOOP 反馈循环引擎: 调度器 / scheduler (feedback_loop/scheduler.py) | → | TELE->FLE 指标桥接 — emit_metrics() 生产者 (system_telem... | 导入依赖 / import_depends |
| 30 | D_GOVERNANCE 生命周期管理: 启动brain / start_brain (construction/start_brain.py) | → | AutoRuntimeCore — 三层运行时运营中心（系统大脑） (tradin... | 导入依赖 / import_depends |
| 31 | D_GOVERNANCE 生命周期管理: 启动brain / start_brain (construction/start_brain.py) | → | AutoTaskGenerator — 自动任务生成器 (trading/auto_task_ge... | 导入依赖 / import_depends |
| 32 | D_GOVERNANCE 生命周期管理: Git守卫 / git_guard (scripts/git_guard.py) | → | concurrency_guard — 回滚操作并发安全守卫。 (runtime/conc... | 导入依赖 / import_depends |
| 33 | D_GOVERNANCE 生命周期管理: postcheckout守卫 / post_checkout_guard (scripts/post_chec... | → | concurrency_guard — 回滚操作并发安全守卫。 (runtime/conc... | 导入依赖 / import_depends |
| 34 | D_GOVERNANCE 生命周期管理: 上下文预算 / context_budget (context_governance/context_b... | → | token_budget.py — Token 估算工具 SSoT (capacity_assuranc... | 导入依赖 / import_depends |
| 35 | D_GOVERNANCE 生命周期管理: miniqmt提供器 / miniqmt_provider (data_governance/miniqmt... | → | DatabaseService: 统一管理数据库的连接池、生命周期、健康检... | 导入依赖 / import_depends |
| 36 | D_GOVERNANCE 生命周期管理: 自基准 / self_benchmark (intelligence_governance/self_ben... | → | AssetDiscoveryScanner — MOD-INF-026 L1 全量文件系统扫描... | 导入依赖 / import_depends |
| 37 | D_GOVERNANCE 生命周期管理: 数据库服务 / database_service (persistence/database_servi... | → | DatabaseService: 统一管理数据库的连接池、生命周期、健康检... | 导入依赖 / import_depends |
| 38 | D_GOVERNANCE 生命周期管理: code_quality/test_code_dedup_engine.py | → | AssetInventoryModels — MOD-INF-026 Pydantic V2 共享数据... | 测试依赖 / test_depends |
| 39 | D_GOVERNANCE 生命周期管理: code_quality/test_code_dedup_engine.py | → | AssetDiscoveryScanner — MOD-INF-026 L1 全量文件系统扫描... | 测试依赖 / test_depends |
| 40 | D_GOVERNANCE 生命周期管理: code-dedup-engine 红队对抗测试 — MOD-INF-017. (code_qual... | → | AssetDiscoveryScanner — MOD-INF-026 L1 全量文件系统扫描... | 测试依赖 / test_depends |
| 41 | D_GOVERNANCE 生命周期管理: lifecycle/test_startup_shutdown.py | → | runtime/startup_shutdown.py | 测试依赖 / test_depends |
| 42 | D_GOVERNANCE 生命周期管理: security/test_sandbox_enforcer.py | → | SandboxEnforcer — Agent 沙盒隔离。 (runtime/sandbox_enfo... | 测试依赖 / test_depends |
| 43 | D_GOVERNANCE 生命周期管理: 测试并发守卫redblue / test_concurrency_guard_red_blue (ro... | → | concurrency_guard — 回滚操作并发安全守卫。 (runtime/conc... | 测试依赖 / test_depends |
| 44 | D_GOV_AUDIT 审计追踪: 工作区hygiene对账器 / workspace_hygiene_reconciler (audit... | → | git_batcher.py — Git 命令批量化工具（ARCH-GIT-CALL-BUDGE... | 导入依赖 / import_depends |
| 45 | D_GOV_CODE_QUALITY 代码质量治理: 命令行 / cli (code_dedup/cli.py) | → | AssetDiscoveryScanner — MOD-INF-026 L1 全量文件系统扫描... | 导入依赖 / import_depends |
| 46 | D_GOV_ENFORCEMENT 规则执行: session_worktree.py — AI 对话 worktree 物理隔离 helper（... | → | git_batcher.py — Git 命令批量化工具（ARCH-GIT-CALL-BUDGE... | 导入依赖 / import_depends |
| 47 | D_GOV_OPS_RESILIENCE 运维弹性治理: Circuit Breaker — MOD-INF-022 (resilience_governance/cir... | → | Circuit Breaker — 熔断器：连续失败 -> OPEN -> 暂停执行。... | 导入依赖 / import_depends |
| 48 | D_GOV_RULE 规则治理: 任务完成门禁 / Task Completion Gate (rule_enforcement/tas... | → | Task Lifecycle Manager — G0-G7 任务生命周期门禁。 (lifec... | 导入依赖 / import_depends |
| 49 | D_GOV_SCRIPTS 脚本治理: session_simulator — 30 个模拟开发 session 的蓝图读取事件... | → | blueprint_metrics — 蓝图使用追踪 instrumentation (metric... | 导入依赖 / import_depends |
| 50 | D_GOV_SCRIPTS 脚本治理: base.py — 审计脚本基类 (_shared/base.py) | → | Finding Schema — 审计发现标准化数据模型 (script_system/f... | 导入依赖 / import_depends |
| 51 | D_GOV_SCRIPTS 脚本治理: check_registry_consistency — 跨登记表一致性校验。 (d3_me... | → | Finding Schema — 审计发现标准化数据模型 (script_system/f... | 导入依赖 / import_depends |
| 52 | D_GOV_SCRIPTS 脚本治理: finding_state_machine.py — Finding 全生命周期状态机 (met... | → | Finding Schema — 审计发现标准化数据模型 (script_system/f... | 导入依赖 / import_depends |
| 53 | D_GOV_SCRIPTS 脚本治理: validate_emergency_bypass_log.py — 应急绕过审计脚本 (met... | → | Finding Schema — 审计发现标准化数据模型 (script_system/f... | 导入依赖 / import_depends |
| 54 | D_GOV_SCRIPTS 脚本治理: run_all.py — 脚本系统统一入口脚本 (governance/run_all.py) | → | Finding->TaskCard 桥接器 (infrastructure/finding_task_bri... | 导入依赖 / import_depends |
| 55 | D_GOV_SCRIPTS 脚本治理: run_all.py — 脚本系统统一入口脚本 (governance/run_all.py) | → | Finding Schema — 审计发现标准化数据模型 (script_system/f... | 导入依赖 / import_depends |
| 56 | D_INFRA_RECOVERY 回滚恢复: RollbackExecutor — 回滚执行器核心封装。 (rollback/rollba... | → | concurrency_guard — 回滚操作并发安全守卫。 (runtime/conc... | 导入依赖 / import_depends |
| 57 | D_INTEGRATION 管线路由: LocalModelScheduler — L2 本地模型 24/7 调度循环 (local_m... | → | resource_optimization.py - MAPE-K autonomic resource opti... | 导入依赖 / import_depends |
| 58 | D_INTEGRATION 管线路由: ZephyrAlpha MCP Telemetry Server — 系统可观测性 MCP 接口... | → | Telemetry — 系统遥测门面类（MOD-INF-015 v2.1.0） (system... | 导入依赖 / import_depends |
| 59 | D_INTEGRATION 管线路由: PipelineOrchestrator — M1-M11 管线协调器 (integration/pi... | → | CircuitBreakerManager -- standalone circuit breaker manag... | 导入依赖 / import_depends |
| 60 | D_INTEGRATION 管线路由: PipelineOrchestrator — M1-M11 管线协调器 (integration/pi... | → | CostTracker —— LLM 调用成本追踪器（SRC-0025） (pipeline... | 导入依赖 / import_depends |
| 61 | D_INTEGRATION 管线路由: PipelineOrchestrator — M1-M11 管线协调器 (integration/pi... | → | CT-PIPE-ORC-001 — TaskCard -> 管线入口节点路由 (pipeline... | 导入依赖 / import_depends |
| 62 | D_INTEGRATION 管线路由: PipelineOrchestrator — M1-M11 管线协调器 (integration/pi... | → | DeadLetterQueue — 死信队列 (pipeline/dead_letter_queue.py) | 导入依赖 / import_depends |
| 63 | D_INTEGRATION 管线路由: PipelineOrchestrator — M1-M11 管线协调器 (integration/pi... | → | ModelRouter — 模型路由与降级链管理 (pipeline/model_route... | 导入依赖 / import_depends |
| 64 | D_INTEGRATION 管线路由: PipelineOrchestrator — M1-M11 管线协调器 (integration/pi... | → | Pipeline 数据模型 (pipeline/models.py) | 导入依赖 / import_depends |
| 65 | D_INTEGRATION 管线路由: PipelineOrchestrator — M1-M11 管线协调器 (integration/pi... | → | Pipeline -> Agent Bridge — 双编排器桥接层 (pipeline/pipe... | 导入依赖 / import_depends |
| 66 | D_INTEGRATION 管线路由: PipelineOrchestrator — M1-M11 管线协调器 (integration/pi... | → | Pipeline Lock — 双管线并发锁 (pipeline/pipeline_lock.py) | 导入依赖 / import_depends |
| 67 | D_INTEGRATION 管线路由: PipelineOrchestrator — M1-M11 管线协调器 (integration/pi... | → | PreemptionManager -- 优先级抢占管理器 (pipeline/preemptio... | 导入依赖 / import_depends |
| 68 | D_INTEGRATION 管线路由: PipelineOrchestrator — M1-M11 管线协调器 (integration/pi... | → | Pipeline Routing Plugin System — K8s Scheduling Framewor... | 导入依赖 / import_depends |
| 69 | D_INTEGRATION 管线路由: PipelineOrchestrator — M1-M11 管线协调器 (integration/pi... | → | hooks.py —— 模块生命周期钩子（Phase 2 新增 | 盲点 B8 修... | 导入依赖 / import_depends |
| 70 | D_INTELLIGENCE 上下文管理: ModelTaskMatrix — 任务×模型性能学习引擎 (pipeline_routi... | → | Pipeline 数据模型 (pipeline/models.py) | 导入依赖 / import_depends |
| 71 | D_ORCHESTRATOR 代理编排器: AgentOrchestrator · 多角色 Agent 路由、工具链编排与健康... | → | token_budget.py — Token 估算工具 SSoT (capacity_assuranc... | 导入依赖 / import_depends |
| 72 | D_ORCHESTRATOR 代理编排器: Orc->Script 脚本执行器 — run_audit() 生产者 (execution/s... | → | Script->Gate 门禁桥接器 — submit_findings() 生产者 (scri... | 导入依赖 / import_depends |
| 73 | D_SECURITY 对抗验证: orphan_judge/mcp_integration.py | → | AssetInventory MCP Server — MOD-INF-026 蓝图 §21 (asset... | 导入依赖 / import_depends |
| 74 | D_SECURITY 对抗验证: [INVARIANTS] 蓝图 §4 文件清单与代码双向对齐 (orphan_judg... | → | CapabilityRegistry — 能力注册中心 (trading/capability_re... | 导入依赖 / import_depends |
| 75 | D_SECURITY 对抗验证: [INVARIANTS] 蓝图 §4 文件清单与代码双向对齐 (orphan_judg... | → | ModuleOnboardingScanner — 模块接入扫描器 (trading/module... | 导入依赖 / import_depends |
| 76 | D_SHARED 共享服务: ProcessLifecycleGateway — 进程生命周期统一入口 (infra/pr... | → | daemon_registry.py - unified daemon thread registry + res... | 导入依赖 / import_depends |
| 77 | D_SHARED 共享服务: process_pool.py - Shared process pool for MCP servers and... | → | models.py - Pydantic data models for resource optimizatio... | 导入依赖 / import_depends |
| 78 | D_SHARED 共享服务: io_cache.py - File-level I/O cache with LRU eviction (io/... | → | models.py - Pydantic data models for resource optimizatio... | 导入依赖 / import_depends |
| 79 | D_SHARED 共享服务: health.py —— ZephyrAlpha 聚合健康检查 (lifecycle/health.py) | → | hooks.py —— 模块生命周期钩子（Phase 2 新增 | 盲点 B8 修... | 导入依赖 / import_depends |
| 80 | D_TRADING 交易运营: action_dispatcher/__init__.py | → | Task Scheduler — 任务调度器。 (queue/task_scheduler.py) | 导入依赖 / import_depends |
| 81 | D_TRADING 交易运营: 注释注解写入器（从 ActionDispatcher._annotate_py_file/_ta... | → | ActionDispatcher --- 大脑的"手" v2.0 (Phase 2) (trading/a... | 导入依赖 / import_depends |
| 82 | D_TRADING 交易运营: 审计日志写入器（从 ActionDispatcher._write_triage_log 提... | → | ActionDispatcher --- 大脑的"手" v2.0 (Phase 2) (trading/a... | 导入依赖 / import_depends |
| 83 | D_TRADING 交易运营: 文件生命周期管理器（从 ActionDispatcher._create_file / _d... | → | ActionDispatcher --- 大脑的"手" v2.0 (Phase 2) (trading/a... | 导入依赖 / import_depends |
| 84 | D_TRADING 交易运营: 搜索替换引擎（从 ActionDispatcher._search_replace_file 及... | → | ActionDispatcher --- 大脑的"手" v2.0 (Phase 2) (trading/a... | 导入依赖 / import_depends |
| 85 | D_TRADING 交易运营: ide_health_daemon.py — TRAE IDE 幽灵窗口守护线程 (tradin... | → | daemon_registry.py - unified daemon thread registry + res... | 导入依赖 / import_depends |

### 跨域依赖图 / Cross-domain Dependency Diagram

> 本域与 25 个外部域直接连接（出边 231 条 + 入边 85 条 = 316 条）。只显示直接连接的域，不展开具体节点。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
graph LR
    D_INFRA_RUNTIME["D_INFRA_RUNTIME<br/>运行时集成"]
    D_SHARED["D_SHARED<br/>共享服务"]
    D_GOVERNANCE["D_GOVERNANCE<br/>生命周期管理"]
    D_INTEGRATION["D_INTEGRATION<br/>管线路由"]
    D_SECURITY["D_SECURITY<br/>对抗验证"]
    D_DATA["D_DATA<br/>数据接入层"]
    D_GOV_RULE["D_GOV_RULE<br/>规则治理"]
    D_GOV_OPS_RESILIENCE["D_GOV_OPS_RESILIENCE<br/>运维弹性治理"]
    D_INFRA_A2A["D_INFRA_A2A<br/>A2A通信"]
    D_FEEDBACK_LOOP["D_FEEDBACK_LOOP<br/>反馈循环引擎"]
    D_GOV_AUDIT["D_GOV_AUDIT<br/>审计追踪"]
    D_GOV_DRIFT["D_GOV_DRIFT<br/>漂移检测"]
    D_TRADING["D_TRADING<br/>交易运营"]
    D_INTELLIGENCE["D_INTELLIGENCE<br/>上下文管理"]
    D_AUTONOMY_CORE["D_AUTONOMY_CORE<br/>自治核心"]
    D_FACTOR["D_FACTOR<br/>因子"]
    D_INFRA_RECOVERY["D_INFRA_RECOVERY<br/>回滚恢复"]
    D_OPS["D_OPS<br/>反馈循环"]
    D_ORCHESTRATOR["D_ORCHESTRATOR<br/>代理编排器"]
    D_INFRASTRUCTURE["D_INFRASTRUCTURE<br/>跨层契约基础设施"]
    D_GOV_SCRIPTS["D_GOV_SCRIPTS<br/>脚本治理"]
    D_GOV_REPAIR["D_GOV_REPAIR<br/>治理修复"]
    D_COMPLIANCE["D_COMPLIANCE<br/>合规"]
    D_BACKTEST["D_BACKTEST<br/>回测"]
    D_GOV_CODE_QUALITY["D_GOV_CODE_QUALITY<br/>代码质量治理"]
    D_GOV_ENFORCEMENT["D_GOV_ENFORCEMENT<br/>规则执行"]
    D_INFRA_RUNTIME -->|165条 导入依赖 / import_depends| D_SHARED
    D_INFRA_RUNTIME -->|12条 导入依赖 / import_depends| D_GOVERNANCE
    D_INFRA_RUNTIME -->|8条 导入依赖 / import_depends| D_INTEGRATION
    D_INFRA_RUNTIME -->|5条 导入依赖 / import_depends| D_SECURITY
    D_INFRA_RUNTIME -->|5条 导入依赖 / import_depends, 测试依赖 / test_depends| D_DATA
    D_INFRA_RUNTIME -->|4条 导入依赖 / import_depends| D_GOV_RULE
    D_INFRA_RUNTIME -->|4条 导入依赖 / import_depends| D_GOV_OPS_RESILIENCE
    D_INFRA_RUNTIME -->|3条 导入依赖 / import_depends| D_INFRA_A2A
    D_INFRA_RUNTIME -->|3条 导入依赖 / import_depends| D_FEEDBACK_LOOP
    D_INFRA_RUNTIME -->|3条 导入依赖 / import_depends| D_GOV_AUDIT
    D_INFRA_RUNTIME -->|3条 导入依赖 / import_depends| D_GOV_DRIFT
    D_INFRA_RUNTIME -->|3条 导入依赖 / import_depends| D_TRADING
    D_INFRA_RUNTIME -->|3条 导入依赖 / import_depends| D_INTELLIGENCE
    D_INFRA_RUNTIME -->|2条 导入依赖 / import_depends| D_AUTONOMY_CORE
    D_INFRA_RUNTIME -->|2条 导入依赖 / import_depends| D_FACTOR
    D_INFRA_RUNTIME -->|1条 导入依赖 / import_depends| D_INFRA_RECOVERY
    D_INFRA_RUNTIME -->|1条 导入依赖 / import_depends| D_OPS
    D_INFRA_RUNTIME -->|1条 导入依赖 / import_depends| D_ORCHESTRATOR
    D_INFRA_RUNTIME -->|1条 导入依赖 / import_depends| D_INFRASTRUCTURE
    D_INFRA_RUNTIME -->|1条 导入依赖 / import_depends| D_GOV_SCRIPTS
    D_INFRA_RUNTIME -->|1条 导入依赖 / import_depends| D_GOV_REPAIR
    D_AUTONOMY_CORE -->|22条 导入依赖 / import_depends, 测试依赖 / test_depends| D_INFRA_RUNTIME
    D_GOVERNANCE -->|14条 导入依赖 / import_depends, 测试依赖 / test_depends| D_INFRA_RUNTIME
    D_INTEGRATION -->|13条 导入依赖 / import_depends| D_INFRA_RUNTIME
    D_GOV_SCRIPTS -->|7条 导入依赖 / import_depends| D_INFRA_RUNTIME
    D_TRADING -->|6条 导入依赖 / import_depends| D_INFRA_RUNTIME
    D_SHARED -->|4条 导入依赖 / import_depends| D_INFRA_RUNTIME
    D_SECURITY -->|3条 导入依赖 / import_depends| D_INFRA_RUNTIME
    D_FEEDBACK_LOOP -->|3条 导入依赖 / import_depends| D_INFRA_RUNTIME
    D_FACTOR -->|2条 导入依赖 / import_depends| D_INFRA_RUNTIME
    D_ORCHESTRATOR -->|2条 导入依赖 / import_depends| D_INFRA_RUNTIME
    D_GOV_RULE -->|1条 导入依赖 / import_depends| D_INFRA_RUNTIME
    D_INFRA_RECOVERY -->|1条 导入依赖 / import_depends| D_INFRA_RUNTIME
    D_COMPLIANCE -->|1条 导入依赖 / import_depends| D_INFRA_RUNTIME
    D_INTELLIGENCE -->|1条 导入依赖 / import_depends| D_INFRA_RUNTIME
    D_BACKTEST -->|1条 导入依赖 / import_depends| D_INFRA_RUNTIME
    D_GOV_AUDIT -->|1条 导入依赖 / import_depends| D_INFRA_RUNTIME
    D_GOV_CODE_QUALITY -->|1条 导入依赖 / import_depends| D_INFRA_RUNTIME
    D_GOV_ENFORCEMENT -->|1条 导入依赖 / import_depends| D_INFRA_RUNTIME
    D_GOV_OPS_RESILIENCE -->|1条 导入依赖 / import_depends| D_INFRA_RUNTIME
```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph (PostgreSQL)` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_doc.py`（G2+G10 合并）
- **维护方式 / Maintenance**: 自动生成，全景图更新时刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}.md`，如 `16_d_trading.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[unknown]`=未知
