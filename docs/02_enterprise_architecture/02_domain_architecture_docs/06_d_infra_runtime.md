---
doc_type: architecture_view
title: D_INFRA_RUNTIME 运行时集成架构文档
version: "1.0"
status: active
date: 2026-08-01
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
| 模块数 | 161 | Module Count | 161 |
| 域内依赖 | 148 | Internal Dependencies | 148 |
| 跨域入边 | 78 | Cross-domain Incoming | 78 |
| 跨域出边 | 222 | Cross-domain Outgoing | 222 |
| 设计态模块 | 1 | Design Modules | 1 |
| 生产态模块 | 160 | Production Modules | 160 |
| 容量 | 160/150 (超容) | Capacity | 160/150 (超容) |
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

> 展示全部 161 个模块（生产态 160 + 设计态 1），含跨域依赖外部节点。节点含成熟度+名称+大白话/简介+文件路径。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    docs_01_policies_and_standards_registry_catalogs_infrastructure_registry_yaml_INFRA_DB_001["(生产态 / production) 基础设施注册表 / infrastructure_registry<br/>基础设施注册表，基础设施的注册表，登记和查询已注册的条目。<br/>文件: catalogs/infrastructure_registry.yaml#INFRA-DB-001"]
    docs_01_policies_and_standards_registry_catalogs_infrastructure_registry_yaml_INFRA_DB_002["(生产态 / production) 基础设施注册表 / infrastructure_registry<br/>基础设施注册表，基础设施的注册表，登记和查询已注册的条目。<br/>文件: catalogs/infrastructure_registry.yaml#INFRA-DB-002"]
    docs_01_policies_and_standards_registry_catalogs_infrastructure_registry_yaml_INFRA_DB_003["(生产态 / production) 基础设施注册表 / infrastructure_registry<br/>基础设施注册表，基础设施的注册表，登记和查询已注册的条目。<br/>文件: catalogs/infrastructure_registry.yaml#INFRA-DB-003"]
    docs_01_policies_and_standards_registry_catalogs_infrastructure_registry_yaml_INFRA_DB_006["(生产态 / production) 基础设施注册表 / infrastructure_registry<br/>基础设施注册表，基础设施的注册表，登记和查询已注册的条目。<br/>文件: catalogs/infrastructure_registry.yaml#INFRA-DB-006"]
    docs_03_modules_cross_layer_agent_orchestrator_blueprint_md["(设计态 / design) 蓝图 / blueprint<br/>蓝图，编排器的功能模块。<br/>文件: agent_orchestrator/blueprint.md"]
    src_zephyr_infrastructure_asset_inventory_main_py["(生产态 / production) Asset Inventory CLI — MOD-INF-026 蓝图 §31 / __main__<br/>Asset Inventory CLI — MOD-INF-026 蓝图 §31<br/>文件: asset_inventory/__main__.py"]
    src_zephyr_infrastructure_asset_inventory_lifecycle_py["(生产态 / production) AssetLifecycle — MOD-INF-026 L5 ITIL生命周期 / lifecycle<br/>AssetLifecycle — MOD-INF-026 L5 ITIL生命周期自动化管理器<br/>文件: asset_inventory/lifecycle.py"]
    src_zephyr_infrastructure_asset_inventory_mcp_server_py["(生产态 / production) AssetInventory MCP Server — MOD-INF-026  / mcp_server<br/>AssetInventory MCP Server — MOD-INF-026 蓝图 §21<br/>文件: asset_inventory/mcp_server.py"]
    src_zephyr_infrastructure_asset_inventory_metadata_py["(生产态 / production) 多 IDE 规则文件生成器——从 asset-invento / metadata<br/>多 IDE 规则文件生成器——从 asset-inventory 配置生成。<br/>文件: asset_inventory/metadata.py"]
    src_zephyr_infrastructure_asset_inventory_trust_anchor_py["(生产态 / production) 旁路状态——对标 K8s Admission Webhook / trust_anchor<br/>旁路状态——对标 K8s Admission Webhook 的 emergency bypass。<br/>文件: asset_inventory/trust_anchor.py"]
    src_zephyr_infrastructure_auto_diagnostics_py["(生产态 / production) RI-12 AutoDiagnostics — 自动诊断引擎 / auto_diagnostics<br/>RI-12 AutoDiagnostics — 自动诊断引擎<br/>文件: infrastructure/auto_diagnostics.py"]
    src_zephyr_infrastructure_auto_fix_engine_main_py["(生产态 / production) 主入口 / __main__<br/>引擎的命令行入口，可以直接 python -m 跑起来执行主流程。<br/>文件: auto_fix_engine/__main__.py"]
    src_zephyr_infrastructure_auto_fix_engine_alignment_syncer_py["(生产态 / production) alignmentsyncer / alignment_syncer<br/>alignmentsyncer，提供扫描、修复、校验、回滚等功能，是引擎的组成部分<br/>文件: auto_fix_engine/alignment_syncer.py"]
    src_zephyr_infrastructure_auto_fix_engine_all_completer_py["(生产态 / production) allcompleter / all_completer<br/>allcompleter，提供解析all、提取公共symbols、扫描、修复等功能，是引擎的组成部分<br/>文件: auto_fix_engine/all_completer.py"]
    src_zephyr_infrastructure_auto_fix_engine_config_fixer_py["(生产态 / production) 配置修复器 / config_fixer<br/>配置修复器，管理配置项的读取和校验，主要提供修复trailingwhitespace、修复tabs、修复合并conflicts、扫描等功能，是引擎的组成部分<br/>文件: auto_fix_engine/config_fixer.py"]
    src_zephyr_infrastructure_auto_fix_engine_dedup_extractor_py["(生产态 / production) 去重extractor / dedup_extractor<br/>去重extractor，提供归一化代码、最小occurrences、最小occurrences、扫描等功能，是引擎的组成部分<br/>文件: auto_fix_engine/dedup_extractor.py"]
    src_zephyr_infrastructure_auto_fix_engine_dep_version_fixer_py["(生产态 / production) dep版本修复器 / dep_version_fixer<br/>dep版本修复器，主要提供ishigher、扫描、修复等功能，供engine.py使用<br/>文件: auto_fix_engine/dep_version_fixer.py"]
    src_zephyr_infrastructure_auto_fix_engine_drift_fixer_py["(生产态 / production) 漂移修复器 / drift_fixer<br/>漂移修复器，提供扫描、修复、校验、回滚等功能，是引擎的组成部分<br/>文件: auto_fix_engine/drift_fixer.py"]
    src_zephyr_infrastructure_auto_fix_engine_event_hooks_py["(生产态 / production) 订阅 EventBusBackpressure 的 drif / event_hooks<br/>订阅 EventBusBackpressure 的 drift_detected / validation_result 事件。<br/>文件: auto_fix_engine/event_hooks.py"]
    src_zephyr_infrastructure_auto_fix_engine_fix_diff_py["(生产态 / production) 修复差异 / fix_diff<br/>修复差异，提供compute、computetext、reverse等功能，是引擎的组成部分<br/>文件: auto_fix_engine/fix_diff.py"]
    src_zephyr_infrastructure_auto_fix_engine_fix_scheduler_py["(生产态 / production) 修复调度器 / fix_scheduler<br/>修复调度器，引擎的调度器，按时间或优先级安排任务执行。<br/>文件: auto_fix_engine/fix_scheduler.py"]
    src_zephyr_infrastructure_auto_fix_engine_import_fixer_py["(生产态 / production) 导入修复器 / import_fixer<br/>导入修复器，主要提供try修复模块、扫描、修复等功能，供engine.py使用<br/>文件: auto_fix_engine/import_fixer.py"]
    src_zephyr_infrastructure_auto_fix_engine_interrupt_guard_py["(生产态 / production) 中断守卫 / interrupt_guard<br/>中断守卫，拦截不合规的操作，主要提供waldir、waldir、数据库路径、数据库路径等功能，是引擎的组成部分<br/>文件: auto_fix_engine/interrupt_guard.py"]
    src_zephyr_infrastructure_auto_fix_engine_llm_fix_adapter_py["(生产态 / production) llm修复适配器 / llm_fix_adapter<br/>llm修复适配器，把外部接口适配成内部统一格式，主要提供密钥守卫、密钥守卫、llm桥接、llm桥接等功能，是引擎的组成部分<br/>文件: auto_fix_engine/llm_fix_adapter.py"]
    src_zephyr_infrastructure_auto_fix_engine_scaffold_registrar_py["(生产态 / production) 从 script-manifest.yaml 加载已注册脚本 / scaffold_registrar<br/>从 script-manifest.yaml 加载已注册脚本路径集合。<br/>文件: auto_fix_engine/scaffold_registrar.py"]
    src_zephyr_infrastructure_auto_fix_engine_self_heal_agent_py["(生产态 / production) 自heal代理 / self_heal_agent<br/>自heal代理，主要提供最大rounds、熔断阈值、consecutivefailures等功能，供engine.py使用<br/>文件: auto_fix_engine/self_heal_agent.py"]
    src_zephyr_infrastructure_auto_fix_engine_state_machine_py["(生产态 / production) 漂移事件记录——对齐 test状态machine. / state_machine<br/>漂移事件记录——对齐 test_state_machine.，引擎的状态机，管理状态流转。<br/>文件: auto_fix_engine/state_machine.py"]
    src_zephyr_infrastructure_auto_fix_engine_zombie_cleaner_py["(生产态 / production) 移除 content 中指向不存在文件的僵尸引用，返回清理后 / zombie_cleaner<br/>移除 content 中指向不存在文件的僵尸引用，返回清理后的内容。<br/>文件: auto_fix_engine/zombie_cleaner.py"]
    src_zephyr_infrastructure_blueprint_code_sync_py["(生产态 / production) Blueprint-Code Sync — 蓝图-代码索引同步验证。 / blueprint_code_sync<br/>Blueprint-Code Sync — 蓝图-代码索引同步验证。<br/>文件: infrastructure/blueprint_code_sync.py"]
    src_zephyr_infrastructure_budget_enforcement_init_py["(生产态 / production) 预算enforcement 包聚合层。 / __init__<br/>budget_enforcement 包聚合层。<br/>文件: budget_enforcement/__init__.py"]
    src_zephyr_infrastructure_capacity_assurance_budget_forecaster_py["(生产态 / production) 预算forecaster.py — Token 预算预测 (DD120 / budget_forecaster<br/>Token 预算预测 (DD120-extra, TASK-020)<br/>文件: capacity_assurance/budget_forecaster.py"]
    src_zephyr_infrastructure_capacity_assurance_contracts_contract_bus_py["(生产态 / production) ContractBus loader — 加载全部44条容量保障契约的Pydan / contract_bus<br/>ContractBus loader — 加载全部44条容量保障契约的Pydantic v2 Schema（DD-9三批迁移）.<br/>文件: contracts/contract_bus.py"]
    src_zephyr_infrastructure_capacity_assurance_cross_module_integration_py["(生产态 / production) Cross-module integration — CT-1~CT-4 跨模块 / cross_module_integration<br/>Cross-module integration — CT-1~CT-4 跨模块集成契约实现（对标蓝图 §17）.<br/>文件: capacity_assurance/cross_module_integration.py"]
    src_zephyr_infrastructure_capacity_assurance_host_resource_governor_py["(生产态 / production) hostresourcegovernor.py — 主机资源治理 (B17, / host_resource_governor<br/>主机资源治理<br/>文件: capacity_assurance/host_resource_governor.py"]
    src_zephyr_infrastructure_capacity_assurance_kill_switch_py["(生产态 / production) 终止开关 / kill_switch.py -- safety circuit breaker (DD110, TASK-019).<br/>终止开关，基础设施的状态机，管理状态流转。<br/>文件: capacity_assurance/kill_switch.py"]
    src_zephyr_infrastructure_capacity_assurance_risk_mitigation_py["(生产态 / production) Risk mitigation — R1~R16 全量风险缓解实现（对标蓝图 § / risk_mitigation<br/>Risk mitigation — R1~R16 全量风险缓解实现（对标蓝图 §14 风险与缓解 + 多轮盲点审计）.<br/>文件: capacity_assurance/risk_mitigation.py"]
    src_zephyr_infrastructure_capacity_assurance_schema_py["(生产态 / production) SchemaManager — 容量保障体系数据库 Schema 管理器 / schema<br/>SchemaManager — 容量保障体系数据库 Schema 管理器<br/>文件: capacity_assurance/schema.py"]
    src_zephyr_infrastructure_capacity_assurance_sli_instrumentation_py["(生产态 / production) SLI instrumentation — SLI采集插桩点（对标蓝图 §13  / sli_instrumentation<br/>SLI instrumentation — SLI采集插桩点（对标蓝图 §13 SLI Registry CAP-001~CAP-014）.<br/>文件: capacity_assurance/sli_instrumentation.py"]
    src_zephyr_infrastructure_capacity_assurance_tech_stack_py["(生产态 / production) TechStackValidator — 技术栈可用性校验器 / tech_stack<br/>TechStackValidator — 技术栈可用性校验器<br/>文件: capacity_assurance/tech_stack.py"]
    src_zephyr_infrastructure_capacity_assurance_token_budget_py["(生产态 / production) 令牌budget.py — Token 估算工具 SSoT / token_budget<br/>Token 估算工具 SSoT<br/>文件: capacity_assurance/token_budget.py"]
    src_zephyr_infrastructure_cost_tracker_py["(生产态 / production) RI-15 CostTracker — 成本追踪器 / cost_tracker<br/>RI-15 CostTracker — 成本追踪器<br/>文件: infrastructure/cost_tracker.py"]
    src_zephyr_infrastructure_database_service_py["(生产态 / production) DatabaseService: 统一管理数据库的连接池、生命周期、健康检查 / database_service<br/>DatabaseService: 统一管理数据库的连接池、生命周期、健康检查<br/>文件: infrastructure/database_service.py"]
    src_zephyr_infrastructure_dry_run_simulator_py["(生产态 / production) RI-14 DryRunSimulator — 干运行模拟器 / dry_run_simulator<br/>RI-14 DryRunSimulator — 干运行模拟器<br/>文件: infrastructure/dry_run_simulator.py"]
    src_zephyr_infrastructure_event_bus_upgrade_py["(生产态 / production) DEPRECATED: 此文件已废弃。 / event_bus_upgrade<br/>DEPRECATED: 此文件已废弃。<br/>文件: infrastructure/event_bus_upgrade.py"]
    src_zephyr_infrastructure_event_store_py["(生产态 / production) RI-13 EventStore — 事件存储 / event_store<br/>RI-13 EventStore — 事件存储<br/>文件: infrastructure/event_store.py"]
    src_zephyr_infrastructure_events_event_store_py["(生产态 / production) Event Store — 事件持久化存储。 / event_store<br/>Event Store — 事件持久化存储。<br/>文件: events/event_store.py"]
    src_zephyr_infrastructure_finding_task_bridge_py["(生产态 / production) Finding->TaskCard 桥接器 / finding_task_bridge<br/>Finding->TaskCard 桥接器<br/>文件: infrastructure/finding_task_bridge.py"]
    src_zephyr_infrastructure_git_batcher_py["(生产态 / production) gitbatcher.py — Git 命令批量化工具（ARCH-GIT-CA / git_batcher<br/>Git 命令批量化工具（ARCH-GIT-CALL-BUDGET P2.2，2026-07-19）<br/>文件: infrastructure/git_batcher.py"]
    src_zephyr_infrastructure_health_monitor_health_aggregator_py["(生产态 / production) 全系统健康聚合 — checkallsystems() / health_aggregator<br/>全系统健康聚合 — check_all_systems()<br/>文件: health_monitor/health_aggregator.py"]
    src_zephyr_infrastructure_hooks_event_hook_py["(生产态 / production) EventHook — 声明式任务系统事件订阅 / event_hook<br/>EventHook — 声明式任务系统事件订阅<br/>文件: hooks/event_hook.py"]
    src_zephyr_infrastructure_impact_impact_propagator_py["(生产态 / production) Impact Propagator — 变更影响传播分析。 / impact_propagator<br/>Impact Propagator — 变更影响传播分析。<br/>文件: impact/impact_propagator.py"]
    src_zephyr_infrastructure_impact_llm_impact_analyzer_py["(生产态 / production) LLM Impact Analyzer — 语义影响分析器。 / llm_impact_analyzer<br/>LLM Impact Analyzer — 语义影响分析器。<br/>文件: impact/llm_impact_analyzer.py"]
    src_zephyr_infrastructure_infrastructure_base_py["(生产态 / production) 基础设施 — Infrastructure Layer Skeleton / infrastructure_base<br/>基础设施 — Infrastructure Layer Skeleton<br/>文件: infrastructure/infrastructure_base.py"]
    src_zephyr_infrastructure_kill_switch_sim_py["(生产态 / production) 终止开关仿真 / Kill Switch T0 Hardware Simulator<br/>终止开关仿真。Kill Switch T0 Hardware Simulator<br/>文件: infrastructure/kill_switch_sim.py"]
    src_zephyr_infrastructure_lifecycle_scope_guard_py["(生产态 / production) Scope Guard — 范围蔓延检测与阻断。 / scope_guard<br/>Scope Guard — 范围蔓延检测与阻断。<br/>文件: lifecycle/scope_guard.py"]
    src_zephyr_infrastructure_lifecycle_task_lifecycle_manager_py["(生产态 / production) Task Lifecycle Manager — G0-G7 任务生命周期门禁。 / task_lifecycle_manager<br/>Task Lifecycle Manager — G0-G7 任务生命周期门禁。<br/>文件: lifecycle/task_lifecycle_manager.py"]
    src_zephyr_infrastructure_observability_trace_decorator_py["(生产态 / production) 追踪装饰器 / trace_decorator<br/>追踪装饰器，基础设施的核心类，封装TraceSpan相关逻辑。<br/>文件: observability/trace_decorator.py"]
    src_zephyr_infrastructure_pipeline_backpressure_manager_py["(生产态 / production) backpressure管理器 / Pipeline — Backpressure Manager<br/>backpressure管理器。Pipeline — Backpressure Manager<br/>文件: pipeline/backpressure_manager.py"]
    src_zephyr_infrastructure_pipeline_circuit_breaker_manager_py["(生产态 / production) 熔断断路器管理器 / CircuitBreakerManager -- standalone circuit breaker manager <br/>熔断断路器管理器。CircuitBreakerManager -- standalone circuit breaker manager (Netflix Hystrix equivalent).<br/>文件: pipeline/circuit_breaker_manager.py"]
    src_zephyr_infrastructure_pipeline_cost_tracker_py["(生产态 / production) CostTracker —— LLM 调用成本追踪器（SRC-0025） / cost_tracker<br/>CostTracker —— LLM 调用成本追踪器（SRC-0025）<br/>文件: pipeline/cost_tracker.py"]
    src_zephyr_infrastructure_pipeline_dead_letter_queue_py["(生产态 / production) DeadLetterQueue — 死信队列 / dead_letter_queue<br/>DeadLetterQueue — 死信队列<br/>文件: pipeline/dead_letter_queue.py"]
    src_zephyr_infrastructure_pipeline_llm_gateway_py["(生产态 / production) llm网关 / MOD-INF-019: Agent Spec — LLM Gateway<br/>llm网关。MOD-INF-019: Agent Spec — LLM Gateway<br/>文件: pipeline/llm_gateway.py"]
    src_zephyr_infrastructure_pipeline_pipeline_agent_bridge_py["(生产态 / production) Pipeline -> Agent Bridge — 双编排器桥接层 / pipeline_agent_bridge<br/>Pipeline -> Agent Bridge — 双编排器桥接层<br/>文件: pipeline/pipeline_agent_bridge.py"]
    src_zephyr_infrastructure_pipeline_pipeline_lock_py["(生产态 / production) Pipeline Lock — 双管线并发锁 / pipeline_lock<br/>Pipeline Lock — 双管线并发锁<br/>文件: pipeline/pipeline_lock.py"]
    src_zephyr_infrastructure_pipeline_pipeline_roadmap_py["(生产态 / production) Pipeline 未来版本路线图——v0.10.0 -> v0.12.0 规划骨 / pipeline_roadmap<br/>Pipeline 未来版本路线图——v0.10.0 -> v0.12.0 规划骨架。<br/>文件: pipeline/pipeline_roadmap.py"]
    src_zephyr_infrastructure_pipeline_preemption_manager_py["(生产态 / production) PreemptionManager -- 优先级抢占管理器 / preemption_manager<br/>PreemptionManager -- 优先级抢占管理器<br/>文件: pipeline/preemption_manager.py"]
    src_zephyr_infrastructure_pipeline_routing_plugins_py["(生产态 / production) Pipeline Routing Plugin System — K8s Sch / routing_plugins<br/>Pipeline Routing Plugin System — K8s Scheduling Framework 对标<br/>文件: pipeline/routing_plugins.py"]
    src_zephyr_infrastructure_pydantic_v2_migrator_py["(生产态 / production) M-15 PydanticV2Migrator — Pydantic V2 迁移 / pydantic_v2_migrator<br/>M-15 PydanticV2Migrator — Pydantic V2 迁移工具<br/>文件: infrastructure/pydantic_v2_migrator.py"]
    src_zephyr_infrastructure_quality_quality_monitor_py["(生产态 / production) Quality Monitor — 生成代码质量门禁。 / quality_monitor<br/>Quality Monitor — 生成代码质量门禁。<br/>文件: quality/quality_monitor.py"]
    src_zephyr_infrastructure_reliability_circuit_breaker_py["(生产态 / production) Circuit Breaker — 熔断器：连续失败 -> OPEN -> 暂停 / circuit_breaker<br/>Circuit Breaker — 熔断器：连续失败 -> OPEN -> 暂停执行。<br/>文件: reliability/circuit_breaker.py"]
    src_zephyr_infrastructure_reliability_context_guard_py["(生产态 / production) Context Guard — 上下文契约守卫。 / context_guard<br/>Context Guard — 上下文契约守卫。<br/>文件: reliability/context_guard.py"]
    src_zephyr_infrastructure_runtime_concurrency_guard_py["(生产态 / production) concurrencyguard — 回滚操作并发安全守卫。 / concurrency_guard<br/>concurrency_guard — 回滚操作并发安全守卫。<br/>文件: runtime/concurrency_guard.py"]
    src_zephyr_infrastructure_runtime_sandbox_enforcer_py["(生产态 / production) SandboxEnforcer — Agent 沙盒隔离。 / sandbox_enforcer<br/>SandboxEnforcer — Agent 沙盒隔离。<br/>文件: runtime/sandbox_enforcer.py"]
    src_zephyr_infrastructure_runtime_startup_shutdown_py["(生产态 / production) 启动关机 / startup_shutdown<br/>启动关机，运行时的组成部分，依赖包入口工作。<br/>文件: runtime/startup_shutdown.py"]
    src_zephyr_infrastructure_script_system_finding_py["(生产态 / production) Finding Schema — 审计发现标准化数据模型 / finding<br/>Finding Schema — 审计发现标准化数据模型<br/>文件: script_system/finding.py"]
    src_zephyr_infrastructure_script_system_gate_bridge_py["(生产态 / production) Script->Gate 门禁桥接器 — submitfindings() 生 / gate_bridge<br/>Script->Gate 门禁桥接器 — submit_findings() 生产者<br/>文件: script_system/gate_bridge.py"]
    src_zephyr_infrastructure_system_telemetry_auto_bootstrap_py["(生产态 / production) 自动bootstrap — 全自动遥测注入钩子（MOD-INF-015 v / auto_bootstrap<br/>auto_bootstrap — 全自动遥测注入钩子（MOD-INF-015 v2.1.0）<br/>文件: system_telemetry/auto_bootstrap.py"]
    src_zephyr_infrastructure_system_telemetry_logs_init_py["(生产态 / production) logs — 结构化日志流（structlog + JSONL + trace注 / __init__<br/>logs — 结构化日志流（structlog + JSONL + trace注入）（D_SYSTEM_TELEMETRY）<br/>文件: logs/__init__.py"]
    src_zephyr_infrastructure_system_telemetry_metrics_bridge_py["(生产态 / production) TELE->FLE 指标桥接 — emitmetrics() 生产者 / metrics_bridge<br/>TELE->FLE 指标桥接 — emit_metrics() 生产者<br/>文件: system_telemetry/metrics_bridge.py"]
    src_zephyr_infrastructure_warm_hot_gate_py["(生产态 / production) M-14 WarmHotGate — Warm->Hot 阻断门 / warm_hot_gate<br/>M-14 WarmHotGate — Warm->Hot 阻断门<br/>文件: infrastructure/warm_hot_gate.py"]
    src_zephyr_shared_lifecycle_hooks_py["(生产态 / production) hooks.py —— 模块生命周期钩子（Phase 2 新增 / 盲点 B8  / hooks<br/>— 模块生命周期钩子（Phase 2 新增 / 盲点 B8 修复）<br/>文件: lifecycle/hooks.py"]
    src_zephyr_trading_action_dispatcher_py["(生产态 / production) ActionDispatcher --- 大脑的'手' v2.0 (Phase  / action_dispatcher<br/>ActionDispatcher --- 大脑的'手' v2.0 (Phase 2)<br/>文件: trading/action_dispatcher.py"]
    src_zephyr_trading_auto_task_generator_py["(生产态 / production) AutoTaskGenerator — 自动任务生成器 / auto_task_generator<br/>AutoTaskGenerator — 自动任务生成器<br/>文件: trading/auto_task_generator.py"]
    src_zephyr_trading_ports_py["(生产态 / production) ports / Protocol-based interface layer for runtime->pipeline depende<br/>ports，交易的分发器，把任务/事件分发给处理方。<br/>文件: trading/ports.py"]
    src_zephyr_trading_staging_area_py["(生产态 / production) StagingArea — 多AI并发草稿写入+提交+冲突检测模块（CT-SES / staging_area<br/>StagingArea — 多AI并发草稿写入+提交+冲突检测模块（CT-SESSION-CONFLICT-002）<br/>文件: trading/staging_area.py"]
    src_zephyr_trading_task_gate_py["(生产态 / production) TaskGate --- 任务门控 / task_gate<br/>TaskGate --- 任务门控<br/>文件: trading/task_gate.py"]
    src_zephyr_trading_windows_service_py["(生产态 / production) WindowsService — Windows Service 包装器 / windows_service<br/>WindowsService — Windows Service 包装器<br/>文件: trading/windows_service.py"]
    src_zephyr_trading_zombie_scanner_py["(生产态 / production) zombiescanner.py — 僵尸 Python 进程检测与自动处置 / zombie_scanner<br/>僵尸 Python 进程检测与自动处置<br/>文件: trading/zombie_scanner.py"]
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
    src_zephyr_infrastructure_cost_tracker_py ~~~ src_zephyr_infrastructure_database_service_py
    src_zephyr_infrastructure_database_service_py ~~~ src_zephyr_infrastructure_dry_run_simulator_py
    src_zephyr_infrastructure_dry_run_simulator_py ~~~ src_zephyr_infrastructure_event_bus_upgrade_py
    src_zephyr_infrastructure_event_bus_upgrade_py ~~~ src_zephyr_infrastructure_event_store_py
    src_zephyr_infrastructure_event_store_py ~~~ src_zephyr_infrastructure_events_event_store_py
    src_zephyr_infrastructure_events_event_store_py ~~~ src_zephyr_infrastructure_finding_task_bridge_py
    src_zephyr_infrastructure_finding_task_bridge_py ~~~ src_zephyr_infrastructure_git_batcher_py
    src_zephyr_infrastructure_git_batcher_py ~~~ src_zephyr_infrastructure_health_monitor_health_aggregator_py
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
    src_zephyr_infrastructure_asset_inventory_classifier_py["(生产态 / production) AssetClassifier — MOD-INF-026 L2 资产自动分类器 / classifier<br/>AssetClassifier — MOD-INF-026 L2 资产自动分类器<br/>文件: asset_inventory/classifier.py"]
    src_zephyr_infrastructure_asset_inventory_dashboard_py["(生产态 / production) AssetDashboard — MOD-INF-026 资产健康仪表盘生成器 / dashboard<br/>AssetDashboard — MOD-INF-026 资产健康仪表盘生成器<br/>文件: asset_inventory/dashboard.py"]
    src_zephyr_infrastructure_asset_inventory_dependency_py["(生产态 / production) MOD-INF-026 §18 — 资产依赖图。 / dependency<br/>MOD-INF-026 §18 — 资产依赖图。<br/>文件: asset_inventory/dependency.py"]
    src_zephyr_infrastructure_asset_inventory_index_generator_py["(生产态 / production) UnifiedAssetIndex — MOD-INF-026 L3 统一资产索 / index_generator<br/>UnifiedAssetIndex — MOD-INF-026 L3 统一资产索引生成器<br/>文件: asset_inventory/index_generator.py"]
    src_zephyr_infrastructure_asset_inventory_reconciler_py["(生产态 / production) ReconciliationEngine — MOD-INF-026 L4 注册 / reconciler<br/>ReconciliationEngine — MOD-INF-026 L4 注册表 vs 磁盘对账引擎<br/>文件: asset_inventory/reconciler.py"]
    src_zephyr_infrastructure_asset_inventory_registry_adapter_py["(生产态 / production) MOD-INF-026 §17 — 24 个异构注册表统一解析适配器。 / registry_adapter<br/>MOD-INF-026 §17 — 24 个异构注册表统一解析适配器。<br/>文件: asset_inventory/registry_adapter.py"]
    src_zephyr_infrastructure_asset_inventory_scanner_py["(生产态 / production) AssetDiscoveryScanner — MOD-INF-026 L1 全 / scanner<br/>AssetDiscoveryScanner — MOD-INF-026 L1 全量文件系统扫描器<br/>文件: asset_inventory/scanner.py"]
    src_zephyr_infrastructure_asset_inventory_telemetry_py["(生产态 / production) AssetInventoryTelemetry — MOD-INF-026 自监 / telemetry<br/>AssetInventoryTelemetry — MOD-INF-026 自监控指标<br/>文件: asset_inventory/telemetry.py"]
    src_zephyr_infrastructure_auto_fix_engine_engine_py["(生产态 / production) 引擎 / engine<br/>引擎，主要提供安全门禁、级联断路器、修复预算等功能<br/>文件: auto_fix_engine/engine.py"]
    src_zephyr_infrastructure_budget_enforcement_rbac_bridge_py["(生产态 / production) 预算enforcement.rbacbridge — 基础设施层 R / rbac_bridge<br/>budget_enforcement.rbac_bridge — 基础设施层 RBAC 桥接适配器。<br/>文件: budget_enforcement/rbac_bridge.py"]
    src_zephyr_infrastructure_capacity_assurance_contracts_batch1_infra_py["(生产态 / production) Batch1 基础设施层契约 — 15条 Pydantic v2 Schema（ / batch1_infra<br/>Batch1 基础设施层契约 — 15条 Pydantic v2 Schema（SLO/Error Budget/Token Budget/Kill Switch/Sandbox/Graceful Degradation）.<br/>文件: contracts/batch1_infra.py"]
    src_zephyr_infrastructure_capacity_assurance_contracts_batch3_integration_py["(生产态 / production) Batch3 集成层契约 — 14条 Pydantic v2 Schema（OT / batch3_integration<br/>Batch3 集成层契约 — 14条 Pydantic v2 Schema（OTel/W3C/跨模块CT-1~4/DR/容量预测/语义缓存）.<br/>文件: contracts/batch3_integration.py"]
    src_zephyr_infrastructure_config_validator_py["(生产态 / production) M-12 ConfigValidator — 配置参数校验器 / config_validator<br/>M-12 ConfigValidator — 配置参数校验器<br/>文件: infrastructure/config_validator.py"]
    src_zephyr_infrastructure_contract_tester_py["(生产态 / production) M-11 ContractTester — 契约测试框架 / contract_tester<br/>M-11 ContractTester — 契约测试框架<br/>文件: infrastructure/contract_tester.py"]
    src_zephyr_infrastructure_pipeline_backpressure_types_py["(生产态 / production) backpressure类型定义 / backpressure_types.py - Pipeline backpressure signal data ty<br/>backpressure类型定义，管线的功能模块。<br/>文件: pipeline/backpressure_types.py"]
    src_zephyr_infrastructure_pipeline_ct_pipe_routing_py["(生产态 / production) CT-PIPE-ORC-001 — TaskCard -> 管线入口节点路由 / ct_pipe_routing<br/>CT-PIPE-ORC-001 — TaskCard -> 管线入口节点路由<br/>文件: pipeline/ct_pipe_routing.py"]
    src_zephyr_infrastructure_pipeline_model_router_py["(生产态 / production) ModelRouter — 模型路由与降级链管理 / model_router<br/>ModelRouter — 模型路由与降级链管理<br/>文件: pipeline/model_router.py"]
    src_zephyr_infrastructure_queue_task_scheduler_py["(生产态 / production) Task Scheduler — 任务调度器。 / task_scheduler<br/>Task Scheduler — 任务调度器。<br/>文件: queue/task_scheduler.py"]
    src_zephyr_infrastructure_system_telemetry_budget_telemetry_bridge_py["(生产态 / production) 预算遥测桥接 / _budget_telemetry_bridge<br/>预算遥测桥接，基础设施的桥接，连接两个子系统，做数据和调用的转换中转。<br/>文件: system_telemetry/_budget_telemetry_bridge.py"]
    src_zephyr_infrastructure_system_telemetry_contract_metrics_py["(生产态 / production) 契约指标 / ZephyrAlpha — system-telemetry/contract_metrics.py<br/>契约指标，基础设施的记录器，把发生的事件/结果记下来留档。<br/>文件: system_telemetry/contract_metrics.py"]
    src_zephyr_infrastructure_system_telemetry_metrics_blueprint_metrics_py["(生产态 / production) 蓝图metrics — 蓝图使用追踪 instrumentati / blueprint_metrics<br/>blueprint_metrics — 蓝图使用追踪 instrumentation<br/>文件: metrics/blueprint_metrics.py"]
    src_zephyr_trading_main_py["(生产态 / production) python -m zephyr.trading — AutoRuntime C / __main__<br/>python -m zephyr.trading — AutoRuntime Core 入口<br/>文件: trading/__main__.py"]
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
    src_zephyr_infrastructure_contract_tester_py ~~~ src_zephyr_infrastructure_pipeline_backpressure_types_py
    src_zephyr_infrastructure_pipeline_backpressure_types_py ~~~ src_zephyr_infrastructure_pipeline_ct_pipe_routing_py
    src_zephyr_infrastructure_pipeline_ct_pipe_routing_py ~~~ src_zephyr_infrastructure_pipeline_model_router_py
    src_zephyr_infrastructure_pipeline_model_router_py ~~~ src_zephyr_infrastructure_queue_task_scheduler_py
    src_zephyr_infrastructure_queue_task_scheduler_py ~~~ src_zephyr_infrastructure_system_telemetry_budget_telemetry_bridge_py
    src_zephyr_infrastructure_system_telemetry_budget_telemetry_bridge_py ~~~ src_zephyr_infrastructure_system_telemetry_contract_metrics_py
    src_zephyr_infrastructure_system_telemetry_contract_metrics_py ~~~ src_zephyr_infrastructure_system_telemetry_metrics_blueprint_metrics_py
    src_zephyr_infrastructure_system_telemetry_metrics_blueprint_metrics_py ~~~ src_zephyr_trading_main_py
    src_zephyr_infrastructure_asset_inventory_models_py["(生产态 / production) AssetInventoryModels — MOD-INF-026 Pydan / models<br/>AssetInventoryModels — MOD-INF-026 Pydantic V2 共享数据模型<br/>文件: asset_inventory/models.py"]
    src_zephyr_infrastructure_auto_fix_engine_batch_fixer_py["(生产态 / production) 批次修复器 / batch_fixer<br/>批次修复器，主要提供conflict解析器、conflict解析器、idempotency等功能，供engine.py使用<br/>文件: auto_fix_engine/batch_fixer.py"]
    src_zephyr_infrastructure_auto_fix_engine_compliance_auditor_py["(生产态 / production) 合规审计器 / compliance_auditor<br/>合规审计器，提供retentiondays、retentiondays、审计修复、验证evidence等功能，是引擎的组成部分<br/>文件: auto_fix_engine/compliance_auditor.py"]
    src_zephyr_infrastructure_auto_fix_engine_escalation_bridge_py["(生产态 / production) escalation桥接 / escalation_bridge<br/>escalation桥接，连接两个子系统，做数据和调用的转换中转，主要提供escalate、escalatedeadletter、获取escalation历史、enabled等功能，是引擎的组成部分<br/>文件: auto_fix_engine/escalation_bridge.py"]
    src_zephyr_infrastructure_auto_fix_engine_fix_health_check_py["(生产态 / production) 修复健康检查 / fix_health_check<br/>修复健康检查，检查某项条件是否满足，主要提供检查配置、数据库路径、数据库路径、检查数据库等功能，是引擎的组成部分<br/>文件: auto_fix_engine/fix_health_check.py"]
    src_zephyr_infrastructure_auto_fix_engine_fix_pattern_miner_py["(生产态 / production) 修复模式miner / fix_pattern_miner<br/>修复模式miner，提供数据库路径、数据库路径、模式缓存、模式缓存等功能，是引擎的组成部分<br/>文件: auto_fix_engine/fix_pattern_miner.py"]
    src_zephyr_infrastructure_auto_fix_engine_fix_report_py["(生产态 / production) 修复报告 / fix_report<br/>修复报告，按规则生成所需的数据或报告，主要提供历史、历史、生成、生成摘要等功能，是引擎的组成部分<br/>文件: auto_fix_engine/fix_report.py"]
    src_zephyr_infrastructure_auto_fix_engine_fix_safety_py["(生产态 / production) 修复安全 / fix_safety<br/>修复安全，在关键节点检查是否放行，主要提供enabled、enabled、检查等功能，是引擎的组成部分<br/>文件: auto_fix_engine/fix_safety.py"]
    src_zephyr_infrastructure_auto_fix_engine_shadow_workspace_py["(生产态 / production) shadowworkspace / shadow_workspace<br/>shadowworkspace，主要提供运行type检查、运行测试、运行ruff等功能，供engine.py使用<br/>文件: auto_fix_engine/shadow_workspace.py"]
    src_zephyr_infrastructure_pipeline_models_py["(生产态 / production) Pipeline 数据模型 / models<br/>Pipeline 数据模型<br/>文件: pipeline/models.py"]
    src_zephyr_infrastructure_system_telemetry_facade_py["(生产态 / production) Telemetry — 系统遥测门面类（MOD-INF-015 v2.1.0） / facade<br/>Telemetry — 系统遥测门面类（MOD-INF-015 v2.1.0）<br/>文件: system_telemetry/facade.py"]
    src_zephyr_trading_auto_runtime_core_py["(生产态 / production) AutoRuntimeCore — 三层运行时运营中心（系统大脑） / auto_runtime_core<br/>AutoRuntimeCore — 三层运行时运营中心（系统大脑）<br/>文件: trading/auto_runtime_core.py"]
    src_zephyr_infrastructure_asset_inventory_models_py ~~~ src_zephyr_infrastructure_auto_fix_engine_batch_fixer_py
    src_zephyr_infrastructure_auto_fix_engine_batch_fixer_py ~~~ src_zephyr_infrastructure_auto_fix_engine_compliance_auditor_py
    src_zephyr_infrastructure_auto_fix_engine_compliance_auditor_py ~~~ src_zephyr_infrastructure_auto_fix_engine_escalation_bridge_py
    src_zephyr_infrastructure_auto_fix_engine_escalation_bridge_py ~~~ src_zephyr_infrastructure_auto_fix_engine_fix_health_check_py
    src_zephyr_infrastructure_auto_fix_engine_fix_health_check_py ~~~ src_zephyr_infrastructure_auto_fix_engine_fix_pattern_miner_py
    src_zephyr_infrastructure_auto_fix_engine_fix_pattern_miner_py ~~~ src_zephyr_infrastructure_auto_fix_engine_fix_report_py
    src_zephyr_infrastructure_auto_fix_engine_fix_report_py ~~~ src_zephyr_infrastructure_auto_fix_engine_fix_safety_py
    src_zephyr_infrastructure_auto_fix_engine_fix_safety_py ~~~ src_zephyr_infrastructure_auto_fix_engine_shadow_workspace_py
    src_zephyr_infrastructure_auto_fix_engine_shadow_workspace_py ~~~ src_zephyr_infrastructure_pipeline_models_py
    src_zephyr_infrastructure_pipeline_models_py ~~~ src_zephyr_infrastructure_system_telemetry_facade_py
    src_zephyr_infrastructure_system_telemetry_facade_py ~~~ src_zephyr_trading_auto_runtime_core_py
    src_zephyr_infrastructure_auto_fix_engine_fix_budget_py["(生产态 / production) 修复预算 / fix_budget<br/>修复预算，提供daily限制、monthly限制、llm令牌限制、检查等功能，是引擎的组成部分<br/>文件: auto_fix_engine/fix_budget.py"]
    src_zephyr_infrastructure_auto_fix_engine_fix_reliability_py["(生产态 / production) 修复可靠性 / fix_reliability<br/>修复可靠性，拦截不合规的操作，主要提供存活时间、存活时间、检查、记录等功能，是引擎的组成部分<br/>文件: auto_fix_engine/fix_reliability.py"]
    src_zephyr_infrastructure_file_watcher_py["(生产态 / production) 文件watcher / file_watcher<br/>文件watcher，基础设施的类型，定义数据类型和枚举。<br/>文件: infrastructure/file_watcher.py"]
    src_zephyr_infrastructure_queue_task_queue_py["(生产态 / production) Task Queue — 后台任务队列 + 自动 Dispatch。 / task_queue<br/>Task Queue — 后台任务队列 + 自动 Dispatch。<br/>文件: queue/task_queue.py"]
    src_zephyr_infrastructure_system_telemetry_ai_behavior_event_sink_py["(生产态 / production) 遥测 · aibehavior/eventsink — AI 行为遥测事件管 / event_sink<br/>遥测 · ai_behavior/event_sink — AI 行为遥测事件管道。<br/>文件: ai_behavior/event_sink.py"]
    src_zephyr_infrastructure_system_telemetry_archive_cold_stub_py["(生产态 / production) 遥测 · archive/coldstub — 冷存储归档管道。 / cold_stub<br/>遥测 · archive/cold_stub — 冷存储归档管道。<br/>文件: archive/cold_stub.py"]
    src_zephyr_infrastructure_system_telemetry_traces_span_stub_py["(生产态 / production) 遥测 · traces/spanstub — W3C TraceContext / span_stub<br/>遥测 · traces/span_stub — W3C TraceContext 分布式追踪管道。<br/>文件: traces/span_stub.py"]
    src_zephyr_infrastructure_system_telemetry_watchdog_py["(生产态 / production) 三冗余 Watchdog（CT-WATCHDOG-001）——互检+Panic  / watchdog<br/>三冗余 Watchdog（CT-WATCHDOG-001）——互检+Panic Mode+Dead Man's Switch。<br/>文件: system_telemetry/watchdog.py"]
    src_zephyr_trading_auto_integrator_py["(生产态 / production) AutoIntegrator — 自动接入器 / auto_integrator<br/>AutoIntegrator — 自动接入器<br/>文件: trading/auto_integrator.py"]
    src_zephyr_trading_boot_hooks_py["(生产态 / production) 从 TaskRepository 查询 task 的 sou / boot_hooks<br/>从 TaskRepository 查询 task 的 source_blueprint，失败返回空串。<br/>文件: trading/boot_hooks.py"]
    src_zephyr_trading_capability_sync_py["(生产态 / production) 能力同步 / capability_sync<br/>能力同步，主要提供注册表、注册表、同步A2A等功能，供自动运行时co使用<br/>文件: trading/capability_sync.py"]
    src_zephyr_trading_lifecycle_manager_py["(生产态 / production) 生命周期管理器——Boot + Shutdown 序列。 / lifecycle_manager<br/>生命周期管理器——Boot + Shutdown 序列。<br/>文件: trading/lifecycle_manager.py"]
    src_zephyr_trading_status_dashboard_py["(生产态 / production) StatusDashboard — 实时状态面板 / status_dashboard<br/>StatusDashboard — 实时状态面板<br/>文件: trading/status_dashboard.py"]
    src_zephyr_infrastructure_auto_fix_engine_fix_budget_py ~~~ src_zephyr_infrastructure_auto_fix_engine_fix_reliability_py
    src_zephyr_infrastructure_auto_fix_engine_fix_reliability_py ~~~ src_zephyr_infrastructure_file_watcher_py
    src_zephyr_infrastructure_file_watcher_py ~~~ src_zephyr_infrastructure_queue_task_queue_py
    src_zephyr_infrastructure_queue_task_queue_py ~~~ src_zephyr_infrastructure_system_telemetry_ai_behavior_event_sink_py
    src_zephyr_infrastructure_system_telemetry_ai_behavior_event_sink_py ~~~ src_zephyr_infrastructure_system_telemetry_archive_cold_stub_py
    src_zephyr_infrastructure_system_telemetry_archive_cold_stub_py ~~~ src_zephyr_infrastructure_system_telemetry_traces_span_stub_py
    src_zephyr_infrastructure_system_telemetry_traces_span_stub_py ~~~ src_zephyr_infrastructure_system_telemetry_watchdog_py
    src_zephyr_infrastructure_system_telemetry_watchdog_py ~~~ src_zephyr_trading_auto_integrator_py
    src_zephyr_trading_auto_integrator_py ~~~ src_zephyr_trading_boot_hooks_py
    src_zephyr_trading_boot_hooks_py ~~~ src_zephyr_trading_capability_sync_py
    src_zephyr_trading_capability_sync_py ~~~ src_zephyr_trading_lifecycle_manager_py
    src_zephyr_trading_lifecycle_manager_py ~~~ src_zephyr_trading_status_dashboard_py
    src_zephyr_infrastructure_auto_fix_engine_models_py["(生产态 / production) 模型 / models<br/>模型，引擎的功能模块。<br/>文件: auto_fix_engine/models.py"]
    src_zephyr_infrastructure_observability_notifier_py["(生产态 / production) Notifier — 多渠道 Owner 通知。 / notifier<br/>Notifier — 多渠道 Owner 通知。<br/>文件: observability/notifier.py"]
    src_zephyr_infrastructure_runtime_gate_coordinator_py["(生产态 / production) Rollback->Gate 协调器 — freezeall / thawa / gate_coordinator<br/>Rollback->Gate 协调器 — freeze_all / thaw_all<br/>文件: runtime/gate_coordinator.py"]
    src_zephyr_infrastructure_sla_sla_monitor_py["(生产态 / production) SLA Monitor — 服务等级协议 (SLA) 监控 RTO/RPO。 / sla_monitor<br/>SLA Monitor — 服务等级协议 (SLA) 监控 RTO/RPO。<br/>文件: sla/sla_monitor.py"]
    src_zephyr_infrastructure_system_telemetry_health_aggregator_py["(生产态 / production) 健康聚合器（Health Aggregator） / health_aggregator<br/>健康聚合器（Health Aggregator）<br/>文件: system_telemetry/health_aggregator.py"]
    src_zephyr_infrastructure_system_telemetry_logs_structured_sink_py["(生产态 / production) logs/structuredsink — 结构化日志管道（DSYSTEM / structured_sink<br/>logs/structured_sink — 结构化日志管道（D_SYSTEM_TELEMETRY）。<br/>文件: logs/structured_sink.py"]
    src_zephyr_trading_ai_audit_logger_py["(生产态 / production) AiAuditLogger — AI 行为审计日志 / ai_audit_logger<br/>AiAuditLogger — AI 行为审计日志<br/>文件: trading/ai_audit_logger.py"]
    src_zephyr_trading_dream_cycle_py["(生产态 / production) DreamCycle — 知识固化引擎 / dream_cycle<br/>DreamCycle — 知识固化引擎<br/>文件: trading/dream_cycle.py"]
    src_zephyr_trading_finalizer_py["(生产态 / production) Finalizer — 优雅清理器 / finalizer<br/>Finalizer — 优雅清理器<br/>文件: trading/finalizer.py"]
    src_zephyr_trading_health_monitor_py["(生产态 / production) HealthMonitor — 健康监控 + 自愈 / health_monitor<br/>HealthMonitor — 健康监控 + 自愈<br/>文件: trading/health_monitor.py"]
    src_zephyr_trading_integration_registry_py["(生产态 / production) IntegrationRegistry — 集成注册表 / integration_registry<br/>IntegrationRegistry — 集成注册表<br/>文件: trading/integration_registry.py"]
    src_zephyr_trading_night_shift_queue_py["(生产态 / production) NightShiftQueue — 夜班登记表持久化 / night_shift_queue<br/>NightShiftQueue — 夜班登记表持久化<br/>文件: trading/night_shift_queue.py"]
    src_zephyr_trading_orphan_detector_py["(生产态 / production) OrphanDetector — 孤儿检测器 / orphan_detector<br/>OrphanDetector — 孤儿检测器<br/>文件: trading/orphan_detector.py"]
    src_zephyr_trading_runtime_config_py["(生产态 / production) 启动前配置完整性校验（5.71.1 治本）——必填字段/类型 / runtime_config<br/>启动前配置完整性校验（5.71.1 治本）——必填字段/类型/范围，失败 fail-fast。<br/>文件: trading/runtime_config.py"]
    src_zephyr_trading_stop_gate_py["(生产态 / production) StopGate — 质量闸门 / stop_gate<br/>StopGate — 质量闸门<br/>文件: trading/stop_gate.py"]
    src_zephyr_trading_work_orchestrator_py["(生产态 / production) 工作编排子系统——决定什么工作、什么时候、用什么模型、什么顺 / work_orchestrator<br/>工作编排子系统——决定什么工作、什么时候、用什么模型、什么顺序。<br/>文件: trading/work_orchestrator.py"]
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
    src_zephyr_infrastructure_system_telemetry_trace_bridge_py["(生产态 / production) 追踪桥接 / _trace_bridge<br/>追踪桥接，基础设施的桥接，连接两个子系统，做数据和调用的转换中转。<br/>文件: system_telemetry/_trace_bridge.py"]
    src_zephyr_infrastructure_system_telemetry_health_probes_py["(生产态 / production) 三态健康探针协议（Health Probes — CT-HEALTH-001） / health_probes<br/>三态健康探针协议（Health Probes — CT-HEALTH-001）<br/>文件: system_telemetry/health_probes.py"]
    src_zephyr_trading_module_onboarding_scanner_py["(生产态 / production) ModuleOnboardingScanner — 模块接入扫描器 / module_onboarding_scanner<br/>ModuleOnboardingScanner — 模块接入扫描器<br/>文件: trading/module_onboarding_scanner.py"]
    src_zephyr_trading_resource_optimization_py["(生产态 / production) resourceoptimization / resource_optimization.py - MAPE-K autonomic resource optimiz<br/>resourceoptimization，交易的功能模块。<br/>文件: trading/resource_optimization.py"]
    src_zephyr_trading_work_dag_py["(生产态 / production) WorkDAG + WorkItem — 工作编排数据模型 / work_dag<br/>WorkDAG + WorkItem — 工作编排数据模型<br/>文件: trading/work_dag.py"]
    src_zephyr_infrastructure_system_telemetry_trace_bridge_py ~~~ src_zephyr_infrastructure_system_telemetry_health_probes_py
    src_zephyr_infrastructure_system_telemetry_health_probes_py ~~~ src_zephyr_trading_module_onboarding_scanner_py
    src_zephyr_trading_module_onboarding_scanner_py ~~~ src_zephyr_trading_resource_optimization_py
    src_zephyr_trading_resource_optimization_py ~~~ src_zephyr_trading_work_dag_py
    src_zephyr_shared_lifecycle_daemon_registry_py["(生产态 / production) daemon注册表 / daemon_registry.py - unified daemon thread registry + resour<br/>daemon注册表，lifecycle的状态机，管理状态流转。<br/>文件: lifecycle/daemon_registry.py"]
    src_zephyr_shared_lifecycle_lazy_loader_py["(生产态 / production) lazy加载器 / lazy_loader.py - Lazy module loading registry<br/>lazy加载器，lifecycle的功能模块。<br/>文件: lifecycle/lazy_loader.py"]
    src_zephyr_shared_lifecycle_resource_optimization_models_py["(生产态 / production) resourceoptimization模型 / models.py - Pydantic data models for resource optimization e<br/>resourceoptimization模型，lifecycle的功能模块。<br/>文件: lifecycle/resource_optimization_models.py"]
    src_zephyr_trading_capability_registry_py["(生产态 / production) CapabilityRegistry — 能力注册中心 / capability_registry<br/>CapabilityRegistry — 能力注册中心<br/>文件: trading/capability_registry.py"]
    src_zephyr_shared_lifecycle_daemon_registry_py ~~~ src_zephyr_shared_lifecycle_lazy_loader_py
    src_zephyr_shared_lifecycle_lazy_loader_py ~~~ src_zephyr_shared_lifecycle_resource_optimization_models_py
    src_zephyr_shared_lifecycle_resource_optimization_models_py ~~~ src_zephyr_trading_capability_registry_py
    src_zephyr_trading_capability_card_py["(生产态 / production) CapabilityCard — 能力卡片数据模型 / capability_card<br/>CapabilityCard — 能力卡片数据模型<br/>文件: trading/capability_card.py"]
    src_zephyr_infrastructure_warm_hot_gate_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_config_validator_py
    src_zephyr_infrastructure_warm_hot_gate_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_contract_tester_py
    src_zephyr_infrastructure_asset_inventory_dashboard_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_asset_inventory_models_py
    src_zephyr_infrastructure_asset_inventory_classifier_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_asset_inventory_models_py
    src_zephyr_infrastructure_asset_inventory_lifecycle_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_asset_inventory_models_py
    src_zephyr_infrastructure_asset_inventory_index_generator_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_asset_inventory_models_py
    src_zephyr_infrastructure_asset_inventory_registry_adapter_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_asset_inventory_models_py
    src_zephyr_infrastructure_asset_inventory_telemetry_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_system_telemetry_facade_py
    src_zephyr_infrastructure_asset_inventory_scanner_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_asset_inventory_models_py
    src_zephyr_infrastructure_auto_fix_engine_alignment_syncer_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_asset_inventory_reconciler_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_asset_inventory_models_py
    src_zephyr_infrastructure_auto_fix_engine_all_completer_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_asset_inventory_main_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_asset_inventory_dashboard_py
    src_zephyr_infrastructure_asset_inventory_main_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_asset_inventory_dependency_py
    src_zephyr_infrastructure_asset_inventory_main_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_asset_inventory_classifier_py
    src_zephyr_infrastructure_asset_inventory_main_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_asset_inventory_models_py
    src_zephyr_infrastructure_asset_inventory_main_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_asset_inventory_index_generator_py
    src_zephyr_infrastructure_asset_inventory_main_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_asset_inventory_registry_adapter_py
    src_zephyr_infrastructure_asset_inventory_main_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_asset_inventory_telemetry_py
    src_zephyr_infrastructure_asset_inventory_main_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_asset_inventory_scanner_py
    src_zephyr_infrastructure_asset_inventory_main_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_asset_inventory_reconciler_py
    src_zephyr_infrastructure_auto_fix_engine_batch_fixer_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_fix_budget_py
    src_zephyr_infrastructure_auto_fix_engine_batch_fixer_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_fix_reliability_py
    src_zephyr_infrastructure_auto_fix_engine_batch_fixer_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_config_fixer_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_dedup_extractor_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_compliance_auditor_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_engine_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_batch_fixer_py
    src_zephyr_infrastructure_auto_fix_engine_engine_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_compliance_auditor_py
    src_zephyr_infrastructure_auto_fix_engine_engine_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_escalation_bridge_py
    src_zephyr_infrastructure_auto_fix_engine_engine_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_fix_budget_py
    src_zephyr_infrastructure_auto_fix_engine_engine_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_fix_report_py
    src_zephyr_infrastructure_auto_fix_engine_engine_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_fix_safety_py
    src_zephyr_infrastructure_auto_fix_engine_engine_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_fix_health_check_py
    src_zephyr_infrastructure_auto_fix_engine_engine_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_fix_pattern_miner_py
    src_zephyr_infrastructure_auto_fix_engine_engine_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_fix_reliability_py
    src_zephyr_infrastructure_auto_fix_engine_engine_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_engine_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_shadow_workspace_py
    src_zephyr_infrastructure_auto_fix_engine_drift_fixer_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_event_hooks_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_engine_py
    src_zephyr_infrastructure_auto_fix_engine_event_hooks_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_fix_diff_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_dep_version_fixer_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_escalation_bridge_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_fix_budget_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_fix_scheduler_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_fix_report_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_fix_safety_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_fix_health_check_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_import_fixer_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_fix_pattern_miner_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_fix_reliability_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_self_heal_agent_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_llm_fix_adapter_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_fix_safety_py
    src_zephyr_infrastructure_auto_fix_engine_llm_fix_adapter_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_scaffold_registrar_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_budget_enforcement_init_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_budget_enforcement_rbac_bridge_py
    src_zephyr_infrastructure_auto_fix_engine_shadow_workspace_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_main_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_engine_py
    src_zephyr_infrastructure_auto_fix_engine_zombie_cleaner_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_capacity_assurance_contracts_contract_bus_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_capacity_assurance_contracts_batch3_integration_py
    src_zephyr_infrastructure_capacity_assurance_contracts_contract_bus_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_capacity_assurance_contracts_batch1_infra_py
    src_zephyr_infrastructure_pipeline_circuit_breaker_manager_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_pipeline_models_py
    src_zephyr_infrastructure_pipeline_backpressure_manager_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_pipeline_backpressure_types_py
    src_zephyr_infrastructure_pipeline_ct_pipe_routing_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_pipeline_models_py
    src_zephyr_infrastructure_pipeline_dead_letter_queue_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_pipeline_models_py
    src_zephyr_infrastructure_pipeline_cost_tracker_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_pipeline_models_py
    src_zephyr_infrastructure_pipeline_cost_tracker_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_pipeline_model_router_py
    src_zephyr_infrastructure_pipeline_pipeline_agent_bridge_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_pipeline_models_py
    src_zephyr_infrastructure_pipeline_preemption_manager_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_pipeline_models_py
    src_zephyr_infrastructure_pipeline_routing_plugins_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_pipeline_ct_pipe_routing_py
    src_zephyr_infrastructure_pipeline_routing_plugins_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_pipeline_models_py
    src_zephyr_infrastructure_system_telemetry_auto_bootstrap_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_system_telemetry_contract_metrics_py
    src_zephyr_infrastructure_system_telemetry_auto_bootstrap_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_system_telemetry_facade_py
    src_zephyr_infrastructure_system_telemetry_auto_bootstrap_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_system_telemetry_budget_telemetry_bridge_py
    src_zephyr_infrastructure_system_telemetry_auto_bootstrap_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_system_telemetry_metrics_blueprint_metrics_py
    src_zephyr_infrastructure_system_telemetry_health_aggregator_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_system_telemetry_health_probes_py
    src_zephyr_infrastructure_system_telemetry_facade_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_system_telemetry_health_aggregator_py
    src_zephyr_infrastructure_system_telemetry_facade_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_system_telemetry_watchdog_py
    src_zephyr_infrastructure_system_telemetry_facade_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_system_telemetry_ai_behavior_event_sink_py
    src_zephyr_infrastructure_system_telemetry_facade_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_system_telemetry_archive_cold_stub_py
    src_zephyr_infrastructure_system_telemetry_facade_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_system_telemetry_traces_span_stub_py
    src_zephyr_infrastructure_system_telemetry_ai_behavior_event_sink_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_system_telemetry_logs_structured_sink_py
    src_zephyr_infrastructure_system_telemetry_logs_structured_sink_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_system_telemetry_trace_bridge_py
    src_zephyr_infrastructure_system_telemetry_logs_init_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_system_telemetry_logs_structured_sink_py
    src_zephyr_infrastructure_system_telemetry_traces_span_stub_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_system_telemetry_trace_bridge_py
    src_zephyr_trading_action_dispatcher_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_queue_task_scheduler_py
    src_zephyr_trading_auto_integrator_py -->|导入依赖 / import_depends| src_zephyr_trading_capability_registry_py
    src_zephyr_trading_auto_integrator_py -->|导入依赖 / import_depends| src_zephyr_trading_capability_card_py
    src_zephyr_trading_auto_integrator_py -->|导入依赖 / import_depends| src_zephyr_trading_module_onboarding_scanner_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_file_watcher_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_queue_task_queue_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_trading_ai_audit_logger_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_trading_auto_integrator_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_trading_capability_sync_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_trading_capability_registry_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_trading_dream_cycle_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_trading_boot_hooks_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_trading_finalizer_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_trading_night_shift_queue_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_trading_lifecycle_manager_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_trading_module_onboarding_scanner_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_trading_integration_registry_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_trading_health_monitor_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_trading_orphan_detector_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_trading_runtime_config_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_trading_resource_optimization_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_trading_work_dag_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_trading_status_dashboard_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_trading_stop_gate_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_trading_work_orchestrator_py
    src_zephyr_trading_capability_sync_py -->|导入依赖 / import_depends| src_zephyr_trading_capability_registry_py
    src_zephyr_trading_capability_sync_py -->|导入依赖 / import_depends| src_zephyr_trading_capability_card_py
    src_zephyr_trading_capability_registry_py -->|导入依赖 / import_depends| src_zephyr_trading_capability_card_py
    src_zephyr_trading_boot_hooks_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_observability_notifier_py
    src_zephyr_trading_boot_hooks_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_runtime_gate_coordinator_py
    src_zephyr_trading_boot_hooks_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_sla_sla_monitor_py
    src_zephyr_trading_boot_hooks_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_system_telemetry_health_aggregator_py
    src_zephyr_trading_boot_hooks_py -->|导入依赖 / import_depends| src_zephyr_trading_finalizer_py
    src_zephyr_trading_lifecycle_manager_py -->|导入依赖 / import_depends| src_zephyr_trading_ai_audit_logger_py
    src_zephyr_trading_lifecycle_manager_py -->|导入依赖 / import_depends| src_zephyr_trading_capability_registry_py
    src_zephyr_trading_lifecycle_manager_py -->|导入依赖 / import_depends| src_zephyr_trading_dream_cycle_py
    src_zephyr_trading_lifecycle_manager_py -->|导入依赖 / import_depends| src_zephyr_trading_finalizer_py
    src_zephyr_trading_lifecycle_manager_py -->|导入依赖 / import_depends| src_zephyr_trading_night_shift_queue_py
    src_zephyr_trading_lifecycle_manager_py -->|导入依赖 / import_depends| src_zephyr_trading_integration_registry_py
    src_zephyr_trading_lifecycle_manager_py -->|导入依赖 / import_depends| src_zephyr_trading_health_monitor_py
    src_zephyr_trading_lifecycle_manager_py -->|导入依赖 / import_depends| src_zephyr_trading_runtime_config_py
    src_zephyr_trading_lifecycle_manager_py -->|导入依赖 / import_depends| src_zephyr_trading_stop_gate_py
    src_zephyr_trading_lifecycle_manager_py -->|导入依赖 / import_depends| src_zephyr_trading_work_orchestrator_py
    src_zephyr_trading_module_onboarding_scanner_py -->|导入依赖 / import_depends| src_zephyr_trading_capability_registry_py
    src_zephyr_trading_health_monitor_py -->|导入依赖 / import_depends| src_zephyr_trading_resource_optimization_py
    src_zephyr_trading_orphan_detector_py -->|导入依赖 / import_depends| src_zephyr_trading_capability_registry_py
    src_zephyr_trading_orphan_detector_py -->|导入依赖 / import_depends| src_zephyr_trading_module_onboarding_scanner_py
    src_zephyr_trading_resource_optimization_py -->|导入依赖 / import_depends| src_zephyr_shared_lifecycle_daemon_registry_py
    src_zephyr_trading_resource_optimization_py -->|导入依赖 / import_depends| src_zephyr_shared_lifecycle_lazy_loader_py
    src_zephyr_trading_resource_optimization_py -->|导入依赖 / import_depends| src_zephyr_shared_lifecycle_resource_optimization_models_py
    src_zephyr_trading_status_dashboard_py -->|导入依赖 / import_depends| src_zephyr_trading_capability_registry_py
    src_zephyr_trading_status_dashboard_py -->|导入依赖 / import_depends| src_zephyr_trading_night_shift_queue_py
    src_zephyr_trading_status_dashboard_py -->|导入依赖 / import_depends| src_zephyr_trading_health_monitor_py
    src_zephyr_trading_status_dashboard_py -->|导入依赖 / import_depends| src_zephyr_trading_orphan_detector_py
    src_zephyr_trading_status_dashboard_py -->|导入依赖 / import_depends| src_zephyr_trading_work_orchestrator_py
    src_zephyr_trading_windows_service_py -->|导入依赖 / import_depends| src_zephyr_trading_auto_runtime_core_py
    src_zephyr_trading_windows_service_py -->|导入依赖 / import_depends| src_zephyr_trading_runtime_config_py
    src_zephyr_trading_windows_service_py -->|导入依赖 / import_depends| src_zephyr_trading_main_py
    src_zephyr_trading_work_orchestrator_py -->|导入依赖 / import_depends| src_zephyr_trading_capability_registry_py
    src_zephyr_trading_work_orchestrator_py -->|导入依赖 / import_depends| src_zephyr_trading_work_dag_py
    src_zephyr_trading_main_py -->|导入依赖 / import_depends| src_zephyr_trading_auto_runtime_core_py
    src_zephyr_trading_main_py -->|导入依赖 / import_depends| src_zephyr_trading_runtime_config_py
    D_SHARED["(生产态 / production) 共享服务 / Shared Services<br/>共享服务，负责跨域共享的工具、协议和基础服务<br/>跨域节点 / cross-domain"]
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| D_SHARED
    D_SECURITY["(生产态 / production) 对抗验证 / Adversarial Validation<br/>对抗验证，负责系统安全对抗测试、漏洞扫描和攻防验证<br/>跨域节点 / cross-domain"]
    src_zephyr_trading_boot_hooks_py -->|导入依赖 / import_depends| D_SECURITY
    src_zephyr_infrastructure_auto_fix_engine_fix_budget_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_infrastructure_queue_task_scheduler_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_trading_finalizer_py -->|导入依赖 / import_depends| D_SHARED
    D_FEEDBACK_LOOP["(生产态 / production) 反馈循环引擎 / Feedback Loop Engine<br/>反馈循环引擎，负责系统自我改进闭环：异常检测、根因诊断、自动修复和自我进化<br/>跨域节点 / cross-domain"]
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| D_FEEDBACK_LOOP
    src_zephyr_trading_boot_hooks_py -->|导入依赖 / import_depends| D_SHARED
    D_INTELLIGENCE["(生产态 / production) 上下文管理 / Context Management<br/>上下文管理，负责 AI 上下文窗口管理、记忆检索和上下文压缩<br/>跨域节点 / cross-domain"]
    src_zephyr_trading_task_gate_py -->|导入依赖 / import_depends| D_INTELLIGENCE
    D_GOV_RULE["(生产态 / production) 规则治理 / Rule Governance<br/>规则治理，负责规则注册、规则版本和规则依赖管理<br/>跨域节点 / cross-domain"]
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| D_GOV_RULE
    src_zephyr_trading_ai_audit_logger_py -->|导入依赖 / import_depends| D_SHARED
    D_INFRASTRUCTURE["(生产态 / production) 跨层契约基础设施 / Cross-Layer Contract Infrastructure<br/>跨层契约基础设施，负责跨层契约定义、共享契约管理和契约校验<br/>跨域节点 / cross-domain"]
    src_zephyr_trading_health_monitor_py -->|导入依赖 / import_depends| D_INFRASTRUCTURE
    src_zephyr_infrastructure_asset_inventory_main_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_trading_resource_optimization_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_infrastructure_auto_fix_engine_all_completer_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_trading_integration_registry_py -->|导入依赖 / import_depends| D_SHARED
    D_AUTONOMY_CORE["(生产态 / production) 自治核心 / Autonomy Core<br/>自治核心，负责 AI 自治决策、目标分解和执行编排<br/>跨域节点 / cross-domain"]
    D_AUTONOMY_CORE -->|测试依赖 / test_depends| src_zephyr_trading_dream_cycle_py
    D_AUTONOMY_CORE -->|测试依赖 / test_depends| src_zephyr_trading_health_monitor_py
    D_INTELLIGENCE -->|导入依赖 / import_depends| src_zephyr_infrastructure_pipeline_models_py
    D_BACKTEST["(生产态 / production) 回测 / Backtest<br/>回测，负责历史数据回测、回测引擎和回测报告<br/>跨域节点 / cross-domain"]
    D_BACKTEST -->|导入依赖 / import_depends| src_zephyr_infrastructure_database_service_py
    D_GOV_SCRIPTS["(生产态 / production) 脚本治理 / Script Governance<br/>脚本治理，负责脚本生命周期管理和脚本质量门禁<br/>跨域节点 / cross-domain"]
    D_GOV_SCRIPTS -->|导入依赖 / import_depends| src_zephyr_infrastructure_script_system_finding_py
    D_AUTONOMY_CORE -->|导入依赖 / import_depends| src_zephyr_infrastructure_capacity_assurance_token_budget_py
    D_FEEDBACK_LOOP -->|导入依赖 / import_depends| src_zephyr_infrastructure_system_telemetry_metrics_bridge_py
    D_AUTONOMY_CORE -->|测试依赖 / test_depends| src_zephyr_trading_capability_registry_py
    D_INTEGRATION["(生产态 / production) 管线路由 / Pipeline Routing<br/>管线路由，负责跨域数据流路由、管道编排和集成适配<br/>跨域节点 / cross-domain"]
    D_INTEGRATION -->|导入依赖 / import_depends| src_zephyr_infrastructure_pipeline_circuit_breaker_manager_py
    D_INTEGRATION -->|导入依赖 / import_depends| src_zephyr_infrastructure_system_telemetry_facade_py
    D_GOV_SCRIPTS -->|导入依赖 / import_depends| src_zephyr_infrastructure_script_system_finding_py
    D_GOV_SCRIPTS -->|导入依赖 / import_depends| src_zephyr_infrastructure_script_system_finding_py
    D_AUTONOMY_CORE -->|测试依赖 / test_depends| src_zephyr_trading_auto_runtime_core_py
    D_TRADING["(生产态 / production) 交易运营 / Trading Operations<br/>交易运营，负责交易生命周期管理、订单状态和成交处理<br/>跨域节点 / cross-domain"]
    D_TRADING -->|导入依赖 / import_depends| src_zephyr_trading_action_dispatcher_py
    D_AUTONOMY_CORE -->|测试依赖 / test_depends| src_zephyr_infrastructure_pipeline_backpressure_manager_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class docs_01_policies_and_standards_registry_catalogs_infrastructure_registry_yaml_INFRA_DB_001,docs_01_policies_and_standards_registry_catalogs_infrastructure_registry_yaml_INFRA_DB_002,docs_01_policies_and_standards_registry_catalogs_infrastructure_registry_yaml_INFRA_DB_003,docs_01_policies_and_standards_registry_catalogs_infrastructure_registry_yaml_INFRA_DB_006,src_zephyr_infrastructure_asset_inventory_main_py,src_zephyr_infrastructure_asset_inventory_classifier_py,src_zephyr_infrastructure_asset_inventory_dashboard_py,src_zephyr_infrastructure_asset_inventory_dependency_py,src_zephyr_infrastructure_asset_inventory_index_generator_py,src_zephyr_infrastructure_asset_inventory_lifecycle_py,src_zephyr_infrastructure_asset_inventory_mcp_server_py,src_zephyr_infrastructure_asset_inventory_metadata_py,src_zephyr_infrastructure_asset_inventory_models_py,src_zephyr_infrastructure_asset_inventory_reconciler_py,src_zephyr_infrastructure_asset_inventory_registry_adapter_py,src_zephyr_infrastructure_asset_inventory_scanner_py,src_zephyr_infrastructure_asset_inventory_telemetry_py,src_zephyr_infrastructure_asset_inventory_trust_anchor_py,src_zephyr_infrastructure_auto_diagnostics_py,src_zephyr_infrastructure_auto_fix_engine_main_py,src_zephyr_infrastructure_auto_fix_engine_alignment_syncer_py,src_zephyr_infrastructure_auto_fix_engine_all_completer_py,src_zephyr_infrastructure_auto_fix_engine_batch_fixer_py,src_zephyr_infrastructure_auto_fix_engine_compliance_auditor_py,src_zephyr_infrastructure_auto_fix_engine_config_fixer_py,src_zephyr_infrastructure_auto_fix_engine_dedup_extractor_py,src_zephyr_infrastructure_auto_fix_engine_dep_version_fixer_py,src_zephyr_infrastructure_auto_fix_engine_drift_fixer_py,src_zephyr_infrastructure_auto_fix_engine_engine_py,src_zephyr_infrastructure_auto_fix_engine_escalation_bridge_py,src_zephyr_infrastructure_auto_fix_engine_event_hooks_py,src_zephyr_infrastructure_auto_fix_engine_fix_budget_py,src_zephyr_infrastructure_auto_fix_engine_fix_diff_py,src_zephyr_infrastructure_auto_fix_engine_fix_health_check_py,src_zephyr_infrastructure_auto_fix_engine_fix_pattern_miner_py,src_zephyr_infrastructure_auto_fix_engine_fix_reliability_py,src_zephyr_infrastructure_auto_fix_engine_fix_report_py,src_zephyr_infrastructure_auto_fix_engine_fix_safety_py,src_zephyr_infrastructure_auto_fix_engine_fix_scheduler_py,src_zephyr_infrastructure_auto_fix_engine_import_fixer_py,src_zephyr_infrastructure_auto_fix_engine_interrupt_guard_py,src_zephyr_infrastructure_auto_fix_engine_llm_fix_adapter_py,src_zephyr_infrastructure_auto_fix_engine_models_py,src_zephyr_infrastructure_auto_fix_engine_scaffold_registrar_py,src_zephyr_infrastructure_auto_fix_engine_self_heal_agent_py,src_zephyr_infrastructure_auto_fix_engine_shadow_workspace_py,src_zephyr_infrastructure_auto_fix_engine_state_machine_py,src_zephyr_infrastructure_auto_fix_engine_zombie_cleaner_py,src_zephyr_infrastructure_blueprint_code_sync_py,src_zephyr_infrastructure_budget_enforcement_init_py,src_zephyr_infrastructure_budget_enforcement_rbac_bridge_py,src_zephyr_infrastructure_capacity_assurance_budget_forecaster_py,src_zephyr_infrastructure_capacity_assurance_contracts_batch1_infra_py,src_zephyr_infrastructure_capacity_assurance_contracts_batch3_integration_py,src_zephyr_infrastructure_capacity_assurance_contracts_contract_bus_py,src_zephyr_infrastructure_capacity_assurance_cross_module_integration_py,src_zephyr_infrastructure_capacity_assurance_host_resource_governor_py,src_zephyr_infrastructure_capacity_assurance_kill_switch_py,src_zephyr_infrastructure_capacity_assurance_risk_mitigation_py,src_zephyr_infrastructure_capacity_assurance_schema_py,src_zephyr_infrastructure_capacity_assurance_sli_instrumentation_py,src_zephyr_infrastructure_capacity_assurance_tech_stack_py,src_zephyr_infrastructure_capacity_assurance_token_budget_py,src_zephyr_infrastructure_config_validator_py,src_zephyr_infrastructure_contract_tester_py,src_zephyr_infrastructure_cost_tracker_py,src_zephyr_infrastructure_database_service_py,src_zephyr_infrastructure_dry_run_simulator_py,src_zephyr_infrastructure_event_bus_upgrade_py,src_zephyr_infrastructure_event_store_py,src_zephyr_infrastructure_events_event_store_py,src_zephyr_infrastructure_file_watcher_py,src_zephyr_infrastructure_finding_task_bridge_py,src_zephyr_infrastructure_git_batcher_py,src_zephyr_infrastructure_health_monitor_health_aggregator_py,src_zephyr_infrastructure_hooks_event_hook_py,src_zephyr_infrastructure_impact_impact_propagator_py,src_zephyr_infrastructure_impact_llm_impact_analyzer_py,src_zephyr_infrastructure_infrastructure_base_py,src_zephyr_infrastructure_kill_switch_sim_py,src_zephyr_infrastructure_lifecycle_scope_guard_py,src_zephyr_infrastructure_lifecycle_task_lifecycle_manager_py,src_zephyr_infrastructure_observability_notifier_py,src_zephyr_infrastructure_observability_trace_decorator_py,src_zephyr_infrastructure_pipeline_backpressure_manager_py,src_zephyr_infrastructure_pipeline_backpressure_types_py,src_zephyr_infrastructure_pipeline_circuit_breaker_manager_py,src_zephyr_infrastructure_pipeline_cost_tracker_py,src_zephyr_infrastructure_pipeline_ct_pipe_routing_py,src_zephyr_infrastructure_pipeline_dead_letter_queue_py,src_zephyr_infrastructure_pipeline_llm_gateway_py,src_zephyr_infrastructure_pipeline_model_router_py,src_zephyr_infrastructure_pipeline_models_py,src_zephyr_infrastructure_pipeline_pipeline_agent_bridge_py,src_zephyr_infrastructure_pipeline_pipeline_lock_py,src_zephyr_infrastructure_pipeline_pipeline_roadmap_py,src_zephyr_infrastructure_pipeline_preemption_manager_py,src_zephyr_infrastructure_pipeline_routing_plugins_py,src_zephyr_infrastructure_pydantic_v2_migrator_py,src_zephyr_infrastructure_quality_quality_monitor_py,src_zephyr_infrastructure_queue_task_queue_py,src_zephyr_infrastructure_queue_task_scheduler_py,src_zephyr_infrastructure_reliability_circuit_breaker_py,src_zephyr_infrastructure_reliability_context_guard_py,src_zephyr_infrastructure_runtime_concurrency_guard_py,src_zephyr_infrastructure_runtime_gate_coordinator_py,src_zephyr_infrastructure_runtime_sandbox_enforcer_py,src_zephyr_infrastructure_runtime_startup_shutdown_py,src_zephyr_infrastructure_script_system_finding_py,src_zephyr_infrastructure_script_system_gate_bridge_py,src_zephyr_infrastructure_sla_sla_monitor_py,src_zephyr_infrastructure_system_telemetry_budget_telemetry_bridge_py,src_zephyr_infrastructure_system_telemetry_trace_bridge_py,src_zephyr_infrastructure_system_telemetry_ai_behavior_event_sink_py,src_zephyr_infrastructure_system_telemetry_archive_cold_stub_py,src_zephyr_infrastructure_system_telemetry_auto_bootstrap_py,src_zephyr_infrastructure_system_telemetry_contract_metrics_py,src_zephyr_infrastructure_system_telemetry_facade_py,src_zephyr_infrastructure_system_telemetry_health_aggregator_py,src_zephyr_infrastructure_system_telemetry_health_probes_py,src_zephyr_infrastructure_system_telemetry_logs_init_py,src_zephyr_infrastructure_system_telemetry_logs_structured_sink_py,src_zephyr_infrastructure_system_telemetry_metrics_blueprint_metrics_py,src_zephyr_infrastructure_system_telemetry_metrics_bridge_py,src_zephyr_infrastructure_system_telemetry_traces_span_stub_py,src_zephyr_infrastructure_system_telemetry_watchdog_py,src_zephyr_infrastructure_warm_hot_gate_py,src_zephyr_shared_lifecycle_daemon_registry_py,src_zephyr_shared_lifecycle_hooks_py,src_zephyr_shared_lifecycle_lazy_loader_py,src_zephyr_shared_lifecycle_resource_optimization_models_py,src_zephyr_trading_main_py,src_zephyr_trading_action_dispatcher_py,src_zephyr_trading_ai_audit_logger_py,src_zephyr_trading_auto_integrator_py,src_zephyr_trading_auto_runtime_core_py,src_zephyr_trading_auto_task_generator_py,src_zephyr_trading_boot_hooks_py,src_zephyr_trading_capability_card_py,src_zephyr_trading_capability_registry_py,src_zephyr_trading_capability_sync_py,src_zephyr_trading_dream_cycle_py,src_zephyr_trading_finalizer_py,src_zephyr_trading_health_monitor_py,src_zephyr_trading_integration_registry_py,src_zephyr_trading_lifecycle_manager_py,src_zephyr_trading_module_onboarding_scanner_py,src_zephyr_trading_night_shift_queue_py,src_zephyr_trading_orphan_detector_py,src_zephyr_trading_ports_py,src_zephyr_trading_resource_optimization_py,src_zephyr_trading_runtime_config_py,src_zephyr_trading_staging_area_py,src_zephyr_trading_status_dashboard_py,src_zephyr_trading_stop_gate_py,src_zephyr_trading_task_gate_py,src_zephyr_trading_windows_service_py,src_zephyr_trading_work_dag_py,src_zephyr_trading_work_orchestrator_py,src_zephyr_trading_zombie_scanner_py production
    class docs_03_modules_cross_layer_agent_orchestrator_blueprint_md design
    class D_SHARED,D_SECURITY,D_FEEDBACK_LOOP,D_INTELLIGENCE,D_GOV_RULE,D_INFRASTRUCTURE,D_AUTONOMY_CORE,D_BACKTEST,D_GOV_SCRIPTS,D_INTEGRATION,D_TRADING external_prod
```

### 运营态的图（仅 design_maturity=production 的模块和域内依赖）

> 仅展示已上线运行的模块（共 160 个），不含跨域外部节点。跨域依赖见下方跨域依赖章节。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    docs_01_policies_and_standards_registry_catalogs_infrastructure_registry_yaml_INFRA_DB_001["(生产态 / production) 基础设施注册表 / infrastructure_registry<br/>基础设施注册表，基础设施的注册表，登记和查询已注册的条目。<br/>文件: catalogs/infrastructure_registry.yaml#INFRA-DB-001"]
    docs_01_policies_and_standards_registry_catalogs_infrastructure_registry_yaml_INFRA_DB_002["(生产态 / production) 基础设施注册表 / infrastructure_registry<br/>基础设施注册表，基础设施的注册表，登记和查询已注册的条目。<br/>文件: catalogs/infrastructure_registry.yaml#INFRA-DB-002"]
    docs_01_policies_and_standards_registry_catalogs_infrastructure_registry_yaml_INFRA_DB_003["(生产态 / production) 基础设施注册表 / infrastructure_registry<br/>基础设施注册表，基础设施的注册表，登记和查询已注册的条目。<br/>文件: catalogs/infrastructure_registry.yaml#INFRA-DB-003"]
    docs_01_policies_and_standards_registry_catalogs_infrastructure_registry_yaml_INFRA_DB_006["(生产态 / production) 基础设施注册表 / infrastructure_registry<br/>基础设施注册表，基础设施的注册表，登记和查询已注册的条目。<br/>文件: catalogs/infrastructure_registry.yaml#INFRA-DB-006"]
    src_zephyr_infrastructure_asset_inventory_main_py["(生产态 / production) Asset Inventory CLI — MOD-INF-026 蓝图 §31 / __main__<br/>Asset Inventory CLI — MOD-INF-026 蓝图 §31<br/>文件: asset_inventory/__main__.py"]
    src_zephyr_infrastructure_asset_inventory_lifecycle_py["(生产态 / production) AssetLifecycle — MOD-INF-026 L5 ITIL生命周期 / lifecycle<br/>AssetLifecycle — MOD-INF-026 L5 ITIL生命周期自动化管理器<br/>文件: asset_inventory/lifecycle.py"]
    src_zephyr_infrastructure_asset_inventory_mcp_server_py["(生产态 / production) AssetInventory MCP Server — MOD-INF-026  / mcp_server<br/>AssetInventory MCP Server — MOD-INF-026 蓝图 §21<br/>文件: asset_inventory/mcp_server.py"]
    src_zephyr_infrastructure_asset_inventory_metadata_py["(生产态 / production) 多 IDE 规则文件生成器——从 asset-invento / metadata<br/>多 IDE 规则文件生成器——从 asset-inventory 配置生成。<br/>文件: asset_inventory/metadata.py"]
    src_zephyr_infrastructure_asset_inventory_trust_anchor_py["(生产态 / production) 旁路状态——对标 K8s Admission Webhook / trust_anchor<br/>旁路状态——对标 K8s Admission Webhook 的 emergency bypass。<br/>文件: asset_inventory/trust_anchor.py"]
    src_zephyr_infrastructure_auto_diagnostics_py["(生产态 / production) RI-12 AutoDiagnostics — 自动诊断引擎 / auto_diagnostics<br/>RI-12 AutoDiagnostics — 自动诊断引擎<br/>文件: infrastructure/auto_diagnostics.py"]
    src_zephyr_infrastructure_auto_fix_engine_main_py["(生产态 / production) 主入口 / __main__<br/>引擎的命令行入口，可以直接 python -m 跑起来执行主流程。<br/>文件: auto_fix_engine/__main__.py"]
    src_zephyr_infrastructure_auto_fix_engine_alignment_syncer_py["(生产态 / production) alignmentsyncer / alignment_syncer<br/>alignmentsyncer，提供扫描、修复、校验、回滚等功能，是引擎的组成部分<br/>文件: auto_fix_engine/alignment_syncer.py"]
    src_zephyr_infrastructure_auto_fix_engine_all_completer_py["(生产态 / production) allcompleter / all_completer<br/>allcompleter，提供解析all、提取公共symbols、扫描、修复等功能，是引擎的组成部分<br/>文件: auto_fix_engine/all_completer.py"]
    src_zephyr_infrastructure_auto_fix_engine_config_fixer_py["(生产态 / production) 配置修复器 / config_fixer<br/>配置修复器，管理配置项的读取和校验，主要提供修复trailingwhitespace、修复tabs、修复合并conflicts、扫描等功能，是引擎的组成部分<br/>文件: auto_fix_engine/config_fixer.py"]
    src_zephyr_infrastructure_auto_fix_engine_dedup_extractor_py["(生产态 / production) 去重extractor / dedup_extractor<br/>去重extractor，提供归一化代码、最小occurrences、最小occurrences、扫描等功能，是引擎的组成部分<br/>文件: auto_fix_engine/dedup_extractor.py"]
    src_zephyr_infrastructure_auto_fix_engine_dep_version_fixer_py["(生产态 / production) dep版本修复器 / dep_version_fixer<br/>dep版本修复器，主要提供ishigher、扫描、修复等功能，供engine.py使用<br/>文件: auto_fix_engine/dep_version_fixer.py"]
    src_zephyr_infrastructure_auto_fix_engine_drift_fixer_py["(生产态 / production) 漂移修复器 / drift_fixer<br/>漂移修复器，提供扫描、修复、校验、回滚等功能，是引擎的组成部分<br/>文件: auto_fix_engine/drift_fixer.py"]
    src_zephyr_infrastructure_auto_fix_engine_event_hooks_py["(生产态 / production) 订阅 EventBusBackpressure 的 drif / event_hooks<br/>订阅 EventBusBackpressure 的 drift_detected / validation_result 事件。<br/>文件: auto_fix_engine/event_hooks.py"]
    src_zephyr_infrastructure_auto_fix_engine_fix_diff_py["(生产态 / production) 修复差异 / fix_diff<br/>修复差异，提供compute、computetext、reverse等功能，是引擎的组成部分<br/>文件: auto_fix_engine/fix_diff.py"]
    src_zephyr_infrastructure_auto_fix_engine_fix_scheduler_py["(生产态 / production) 修复调度器 / fix_scheduler<br/>修复调度器，引擎的调度器，按时间或优先级安排任务执行。<br/>文件: auto_fix_engine/fix_scheduler.py"]
    src_zephyr_infrastructure_auto_fix_engine_import_fixer_py["(生产态 / production) 导入修复器 / import_fixer<br/>导入修复器，主要提供try修复模块、扫描、修复等功能，供engine.py使用<br/>文件: auto_fix_engine/import_fixer.py"]
    src_zephyr_infrastructure_auto_fix_engine_interrupt_guard_py["(生产态 / production) 中断守卫 / interrupt_guard<br/>中断守卫，拦截不合规的操作，主要提供waldir、waldir、数据库路径、数据库路径等功能，是引擎的组成部分<br/>文件: auto_fix_engine/interrupt_guard.py"]
    src_zephyr_infrastructure_auto_fix_engine_llm_fix_adapter_py["(生产态 / production) llm修复适配器 / llm_fix_adapter<br/>llm修复适配器，把外部接口适配成内部统一格式，主要提供密钥守卫、密钥守卫、llm桥接、llm桥接等功能，是引擎的组成部分<br/>文件: auto_fix_engine/llm_fix_adapter.py"]
    src_zephyr_infrastructure_auto_fix_engine_scaffold_registrar_py["(生产态 / production) 从 script-manifest.yaml 加载已注册脚本 / scaffold_registrar<br/>从 script-manifest.yaml 加载已注册脚本路径集合。<br/>文件: auto_fix_engine/scaffold_registrar.py"]
    src_zephyr_infrastructure_auto_fix_engine_self_heal_agent_py["(生产态 / production) 自heal代理 / self_heal_agent<br/>自heal代理，主要提供最大rounds、熔断阈值、consecutivefailures等功能，供engine.py使用<br/>文件: auto_fix_engine/self_heal_agent.py"]
    src_zephyr_infrastructure_auto_fix_engine_state_machine_py["(生产态 / production) 漂移事件记录——对齐 test状态machine. / state_machine<br/>漂移事件记录——对齐 test_state_machine.，引擎的状态机，管理状态流转。<br/>文件: auto_fix_engine/state_machine.py"]
    src_zephyr_infrastructure_auto_fix_engine_zombie_cleaner_py["(生产态 / production) 移除 content 中指向不存在文件的僵尸引用，返回清理后 / zombie_cleaner<br/>移除 content 中指向不存在文件的僵尸引用，返回清理后的内容。<br/>文件: auto_fix_engine/zombie_cleaner.py"]
    src_zephyr_infrastructure_blueprint_code_sync_py["(生产态 / production) Blueprint-Code Sync — 蓝图-代码索引同步验证。 / blueprint_code_sync<br/>Blueprint-Code Sync — 蓝图-代码索引同步验证。<br/>文件: infrastructure/blueprint_code_sync.py"]
    src_zephyr_infrastructure_budget_enforcement_init_py["(生产态 / production) 预算enforcement 包聚合层。 / __init__<br/>budget_enforcement 包聚合层。<br/>文件: budget_enforcement/__init__.py"]
    src_zephyr_infrastructure_capacity_assurance_budget_forecaster_py["(生产态 / production) 预算forecaster.py — Token 预算预测 (DD120 / budget_forecaster<br/>Token 预算预测 (DD120-extra, TASK-020)<br/>文件: capacity_assurance/budget_forecaster.py"]
    src_zephyr_infrastructure_capacity_assurance_contracts_contract_bus_py["(生产态 / production) ContractBus loader — 加载全部44条容量保障契约的Pydan / contract_bus<br/>ContractBus loader — 加载全部44条容量保障契约的Pydantic v2 Schema（DD-9三批迁移）.<br/>文件: contracts/contract_bus.py"]
    src_zephyr_infrastructure_capacity_assurance_cross_module_integration_py["(生产态 / production) Cross-module integration — CT-1~CT-4 跨模块 / cross_module_integration<br/>Cross-module integration — CT-1~CT-4 跨模块集成契约实现（对标蓝图 §17）.<br/>文件: capacity_assurance/cross_module_integration.py"]
    src_zephyr_infrastructure_capacity_assurance_host_resource_governor_py["(生产态 / production) hostresourcegovernor.py — 主机资源治理 (B17, / host_resource_governor<br/>主机资源治理<br/>文件: capacity_assurance/host_resource_governor.py"]
    src_zephyr_infrastructure_capacity_assurance_kill_switch_py["(生产态 / production) 终止开关 / kill_switch.py -- safety circuit breaker (DD110, TASK-019).<br/>终止开关，基础设施的状态机，管理状态流转。<br/>文件: capacity_assurance/kill_switch.py"]
    src_zephyr_infrastructure_capacity_assurance_risk_mitigation_py["(生产态 / production) Risk mitigation — R1~R16 全量风险缓解实现（对标蓝图 § / risk_mitigation<br/>Risk mitigation — R1~R16 全量风险缓解实现（对标蓝图 §14 风险与缓解 + 多轮盲点审计）.<br/>文件: capacity_assurance/risk_mitigation.py"]
    src_zephyr_infrastructure_capacity_assurance_schema_py["(生产态 / production) SchemaManager — 容量保障体系数据库 Schema 管理器 / schema<br/>SchemaManager — 容量保障体系数据库 Schema 管理器<br/>文件: capacity_assurance/schema.py"]
    src_zephyr_infrastructure_capacity_assurance_sli_instrumentation_py["(生产态 / production) SLI instrumentation — SLI采集插桩点（对标蓝图 §13  / sli_instrumentation<br/>SLI instrumentation — SLI采集插桩点（对标蓝图 §13 SLI Registry CAP-001~CAP-014）.<br/>文件: capacity_assurance/sli_instrumentation.py"]
    src_zephyr_infrastructure_capacity_assurance_tech_stack_py["(生产态 / production) TechStackValidator — 技术栈可用性校验器 / tech_stack<br/>TechStackValidator — 技术栈可用性校验器<br/>文件: capacity_assurance/tech_stack.py"]
    src_zephyr_infrastructure_capacity_assurance_token_budget_py["(生产态 / production) 令牌budget.py — Token 估算工具 SSoT / token_budget<br/>Token 估算工具 SSoT<br/>文件: capacity_assurance/token_budget.py"]
    src_zephyr_infrastructure_cost_tracker_py["(生产态 / production) RI-15 CostTracker — 成本追踪器 / cost_tracker<br/>RI-15 CostTracker — 成本追踪器<br/>文件: infrastructure/cost_tracker.py"]
    src_zephyr_infrastructure_database_service_py["(生产态 / production) DatabaseService: 统一管理数据库的连接池、生命周期、健康检查 / database_service<br/>DatabaseService: 统一管理数据库的连接池、生命周期、健康检查<br/>文件: infrastructure/database_service.py"]
    src_zephyr_infrastructure_dry_run_simulator_py["(生产态 / production) RI-14 DryRunSimulator — 干运行模拟器 / dry_run_simulator<br/>RI-14 DryRunSimulator — 干运行模拟器<br/>文件: infrastructure/dry_run_simulator.py"]
    src_zephyr_infrastructure_event_bus_upgrade_py["(生产态 / production) DEPRECATED: 此文件已废弃。 / event_bus_upgrade<br/>DEPRECATED: 此文件已废弃。<br/>文件: infrastructure/event_bus_upgrade.py"]
    src_zephyr_infrastructure_event_store_py["(生产态 / production) RI-13 EventStore — 事件存储 / event_store<br/>RI-13 EventStore — 事件存储<br/>文件: infrastructure/event_store.py"]
    src_zephyr_infrastructure_events_event_store_py["(生产态 / production) Event Store — 事件持久化存储。 / event_store<br/>Event Store — 事件持久化存储。<br/>文件: events/event_store.py"]
    src_zephyr_infrastructure_finding_task_bridge_py["(生产态 / production) Finding->TaskCard 桥接器 / finding_task_bridge<br/>Finding->TaskCard 桥接器<br/>文件: infrastructure/finding_task_bridge.py"]
    src_zephyr_infrastructure_git_batcher_py["(生产态 / production) gitbatcher.py — Git 命令批量化工具（ARCH-GIT-CA / git_batcher<br/>Git 命令批量化工具（ARCH-GIT-CALL-BUDGET P2.2，2026-07-19）<br/>文件: infrastructure/git_batcher.py"]
    src_zephyr_infrastructure_health_monitor_health_aggregator_py["(生产态 / production) 全系统健康聚合 — checkallsystems() / health_aggregator<br/>全系统健康聚合 — check_all_systems()<br/>文件: health_monitor/health_aggregator.py"]
    src_zephyr_infrastructure_hooks_event_hook_py["(生产态 / production) EventHook — 声明式任务系统事件订阅 / event_hook<br/>EventHook — 声明式任务系统事件订阅<br/>文件: hooks/event_hook.py"]
    src_zephyr_infrastructure_impact_impact_propagator_py["(生产态 / production) Impact Propagator — 变更影响传播分析。 / impact_propagator<br/>Impact Propagator — 变更影响传播分析。<br/>文件: impact/impact_propagator.py"]
    src_zephyr_infrastructure_impact_llm_impact_analyzer_py["(生产态 / production) LLM Impact Analyzer — 语义影响分析器。 / llm_impact_analyzer<br/>LLM Impact Analyzer — 语义影响分析器。<br/>文件: impact/llm_impact_analyzer.py"]
    src_zephyr_infrastructure_infrastructure_base_py["(生产态 / production) 基础设施 — Infrastructure Layer Skeleton / infrastructure_base<br/>基础设施 — Infrastructure Layer Skeleton<br/>文件: infrastructure/infrastructure_base.py"]
    src_zephyr_infrastructure_kill_switch_sim_py["(生产态 / production) 终止开关仿真 / Kill Switch T0 Hardware Simulator<br/>终止开关仿真。Kill Switch T0 Hardware Simulator<br/>文件: infrastructure/kill_switch_sim.py"]
    src_zephyr_infrastructure_lifecycle_scope_guard_py["(生产态 / production) Scope Guard — 范围蔓延检测与阻断。 / scope_guard<br/>Scope Guard — 范围蔓延检测与阻断。<br/>文件: lifecycle/scope_guard.py"]
    src_zephyr_infrastructure_lifecycle_task_lifecycle_manager_py["(生产态 / production) Task Lifecycle Manager — G0-G7 任务生命周期门禁。 / task_lifecycle_manager<br/>Task Lifecycle Manager — G0-G7 任务生命周期门禁。<br/>文件: lifecycle/task_lifecycle_manager.py"]
    src_zephyr_infrastructure_observability_trace_decorator_py["(生产态 / production) 追踪装饰器 / trace_decorator<br/>追踪装饰器，基础设施的核心类，封装TraceSpan相关逻辑。<br/>文件: observability/trace_decorator.py"]
    src_zephyr_infrastructure_pipeline_backpressure_manager_py["(生产态 / production) backpressure管理器 / Pipeline — Backpressure Manager<br/>backpressure管理器。Pipeline — Backpressure Manager<br/>文件: pipeline/backpressure_manager.py"]
    src_zephyr_infrastructure_pipeline_circuit_breaker_manager_py["(生产态 / production) 熔断断路器管理器 / CircuitBreakerManager -- standalone circuit breaker manager <br/>熔断断路器管理器。CircuitBreakerManager -- standalone circuit breaker manager (Netflix Hystrix equivalent).<br/>文件: pipeline/circuit_breaker_manager.py"]
    src_zephyr_infrastructure_pipeline_cost_tracker_py["(生产态 / production) CostTracker —— LLM 调用成本追踪器（SRC-0025） / cost_tracker<br/>CostTracker —— LLM 调用成本追踪器（SRC-0025）<br/>文件: pipeline/cost_tracker.py"]
    src_zephyr_infrastructure_pipeline_dead_letter_queue_py["(生产态 / production) DeadLetterQueue — 死信队列 / dead_letter_queue<br/>DeadLetterQueue — 死信队列<br/>文件: pipeline/dead_letter_queue.py"]
    src_zephyr_infrastructure_pipeline_llm_gateway_py["(生产态 / production) llm网关 / MOD-INF-019: Agent Spec — LLM Gateway<br/>llm网关。MOD-INF-019: Agent Spec — LLM Gateway<br/>文件: pipeline/llm_gateway.py"]
    src_zephyr_infrastructure_pipeline_pipeline_agent_bridge_py["(生产态 / production) Pipeline -> Agent Bridge — 双编排器桥接层 / pipeline_agent_bridge<br/>Pipeline -> Agent Bridge — 双编排器桥接层<br/>文件: pipeline/pipeline_agent_bridge.py"]
    src_zephyr_infrastructure_pipeline_pipeline_lock_py["(生产态 / production) Pipeline Lock — 双管线并发锁 / pipeline_lock<br/>Pipeline Lock — 双管线并发锁<br/>文件: pipeline/pipeline_lock.py"]
    src_zephyr_infrastructure_pipeline_pipeline_roadmap_py["(生产态 / production) Pipeline 未来版本路线图——v0.10.0 -> v0.12.0 规划骨 / pipeline_roadmap<br/>Pipeline 未来版本路线图——v0.10.0 -> v0.12.0 规划骨架。<br/>文件: pipeline/pipeline_roadmap.py"]
    src_zephyr_infrastructure_pipeline_preemption_manager_py["(生产态 / production) PreemptionManager -- 优先级抢占管理器 / preemption_manager<br/>PreemptionManager -- 优先级抢占管理器<br/>文件: pipeline/preemption_manager.py"]
    src_zephyr_infrastructure_pipeline_routing_plugins_py["(生产态 / production) Pipeline Routing Plugin System — K8s Sch / routing_plugins<br/>Pipeline Routing Plugin System — K8s Scheduling Framework 对标<br/>文件: pipeline/routing_plugins.py"]
    src_zephyr_infrastructure_pydantic_v2_migrator_py["(生产态 / production) M-15 PydanticV2Migrator — Pydantic V2 迁移 / pydantic_v2_migrator<br/>M-15 PydanticV2Migrator — Pydantic V2 迁移工具<br/>文件: infrastructure/pydantic_v2_migrator.py"]
    src_zephyr_infrastructure_quality_quality_monitor_py["(生产态 / production) Quality Monitor — 生成代码质量门禁。 / quality_monitor<br/>Quality Monitor — 生成代码质量门禁。<br/>文件: quality/quality_monitor.py"]
    src_zephyr_infrastructure_reliability_circuit_breaker_py["(生产态 / production) Circuit Breaker — 熔断器：连续失败 -> OPEN -> 暂停 / circuit_breaker<br/>Circuit Breaker — 熔断器：连续失败 -> OPEN -> 暂停执行。<br/>文件: reliability/circuit_breaker.py"]
    src_zephyr_infrastructure_reliability_context_guard_py["(生产态 / production) Context Guard — 上下文契约守卫。 / context_guard<br/>Context Guard — 上下文契约守卫。<br/>文件: reliability/context_guard.py"]
    src_zephyr_infrastructure_runtime_concurrency_guard_py["(生产态 / production) concurrencyguard — 回滚操作并发安全守卫。 / concurrency_guard<br/>concurrency_guard — 回滚操作并发安全守卫。<br/>文件: runtime/concurrency_guard.py"]
    src_zephyr_infrastructure_runtime_sandbox_enforcer_py["(生产态 / production) SandboxEnforcer — Agent 沙盒隔离。 / sandbox_enforcer<br/>SandboxEnforcer — Agent 沙盒隔离。<br/>文件: runtime/sandbox_enforcer.py"]
    src_zephyr_infrastructure_runtime_startup_shutdown_py["(生产态 / production) 启动关机 / startup_shutdown<br/>启动关机，运行时的组成部分，依赖包入口工作。<br/>文件: runtime/startup_shutdown.py"]
    src_zephyr_infrastructure_script_system_finding_py["(生产态 / production) Finding Schema — 审计发现标准化数据模型 / finding<br/>Finding Schema — 审计发现标准化数据模型<br/>文件: script_system/finding.py"]
    src_zephyr_infrastructure_script_system_gate_bridge_py["(生产态 / production) Script->Gate 门禁桥接器 — submitfindings() 生 / gate_bridge<br/>Script->Gate 门禁桥接器 — submit_findings() 生产者<br/>文件: script_system/gate_bridge.py"]
    src_zephyr_infrastructure_system_telemetry_auto_bootstrap_py["(生产态 / production) 自动bootstrap — 全自动遥测注入钩子（MOD-INF-015 v / auto_bootstrap<br/>auto_bootstrap — 全自动遥测注入钩子（MOD-INF-015 v2.1.0）<br/>文件: system_telemetry/auto_bootstrap.py"]
    src_zephyr_infrastructure_system_telemetry_logs_init_py["(生产态 / production) logs — 结构化日志流（structlog + JSONL + trace注 / __init__<br/>logs — 结构化日志流（structlog + JSONL + trace注入）（D_SYSTEM_TELEMETRY）<br/>文件: logs/__init__.py"]
    src_zephyr_infrastructure_system_telemetry_metrics_bridge_py["(生产态 / production) TELE->FLE 指标桥接 — emitmetrics() 生产者 / metrics_bridge<br/>TELE->FLE 指标桥接 — emit_metrics() 生产者<br/>文件: system_telemetry/metrics_bridge.py"]
    src_zephyr_infrastructure_warm_hot_gate_py["(生产态 / production) M-14 WarmHotGate — Warm->Hot 阻断门 / warm_hot_gate<br/>M-14 WarmHotGate — Warm->Hot 阻断门<br/>文件: infrastructure/warm_hot_gate.py"]
    src_zephyr_shared_lifecycle_hooks_py["(生产态 / production) hooks.py —— 模块生命周期钩子（Phase 2 新增 / 盲点 B8  / hooks<br/>— 模块生命周期钩子（Phase 2 新增 / 盲点 B8 修复）<br/>文件: lifecycle/hooks.py"]
    src_zephyr_trading_action_dispatcher_py["(生产态 / production) ActionDispatcher --- 大脑的'手' v2.0 (Phase  / action_dispatcher<br/>ActionDispatcher --- 大脑的'手' v2.0 (Phase 2)<br/>文件: trading/action_dispatcher.py"]
    src_zephyr_trading_auto_task_generator_py["(生产态 / production) AutoTaskGenerator — 自动任务生成器 / auto_task_generator<br/>AutoTaskGenerator — 自动任务生成器<br/>文件: trading/auto_task_generator.py"]
    src_zephyr_trading_ports_py["(生产态 / production) ports / Protocol-based interface layer for runtime->pipeline depende<br/>ports，交易的分发器，把任务/事件分发给处理方。<br/>文件: trading/ports.py"]
    src_zephyr_trading_staging_area_py["(生产态 / production) StagingArea — 多AI并发草稿写入+提交+冲突检测模块（CT-SES / staging_area<br/>StagingArea — 多AI并发草稿写入+提交+冲突检测模块（CT-SESSION-CONFLICT-002）<br/>文件: trading/staging_area.py"]
    src_zephyr_trading_task_gate_py["(生产态 / production) TaskGate --- 任务门控 / task_gate<br/>TaskGate --- 任务门控<br/>文件: trading/task_gate.py"]
    src_zephyr_trading_windows_service_py["(生产态 / production) WindowsService — Windows Service 包装器 / windows_service<br/>WindowsService — Windows Service 包装器<br/>文件: trading/windows_service.py"]
    src_zephyr_trading_zombie_scanner_py["(生产态 / production) zombiescanner.py — 僵尸 Python 进程检测与自动处置 / zombie_scanner<br/>僵尸 Python 进程检测与自动处置<br/>文件: trading/zombie_scanner.py"]
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
    src_zephyr_infrastructure_cost_tracker_py ~~~ src_zephyr_infrastructure_database_service_py
    src_zephyr_infrastructure_database_service_py ~~~ src_zephyr_infrastructure_dry_run_simulator_py
    src_zephyr_infrastructure_dry_run_simulator_py ~~~ src_zephyr_infrastructure_event_bus_upgrade_py
    src_zephyr_infrastructure_event_bus_upgrade_py ~~~ src_zephyr_infrastructure_event_store_py
    src_zephyr_infrastructure_event_store_py ~~~ src_zephyr_infrastructure_events_event_store_py
    src_zephyr_infrastructure_events_event_store_py ~~~ src_zephyr_infrastructure_finding_task_bridge_py
    src_zephyr_infrastructure_finding_task_bridge_py ~~~ src_zephyr_infrastructure_git_batcher_py
    src_zephyr_infrastructure_git_batcher_py ~~~ src_zephyr_infrastructure_health_monitor_health_aggregator_py
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
    src_zephyr_infrastructure_asset_inventory_classifier_py["(生产态 / production) AssetClassifier — MOD-INF-026 L2 资产自动分类器 / classifier<br/>AssetClassifier — MOD-INF-026 L2 资产自动分类器<br/>文件: asset_inventory/classifier.py"]
    src_zephyr_infrastructure_asset_inventory_dashboard_py["(生产态 / production) AssetDashboard — MOD-INF-026 资产健康仪表盘生成器 / dashboard<br/>AssetDashboard — MOD-INF-026 资产健康仪表盘生成器<br/>文件: asset_inventory/dashboard.py"]
    src_zephyr_infrastructure_asset_inventory_dependency_py["(生产态 / production) MOD-INF-026 §18 — 资产依赖图。 / dependency<br/>MOD-INF-026 §18 — 资产依赖图。<br/>文件: asset_inventory/dependency.py"]
    src_zephyr_infrastructure_asset_inventory_index_generator_py["(生产态 / production) UnifiedAssetIndex — MOD-INF-026 L3 统一资产索 / index_generator<br/>UnifiedAssetIndex — MOD-INF-026 L3 统一资产索引生成器<br/>文件: asset_inventory/index_generator.py"]
    src_zephyr_infrastructure_asset_inventory_reconciler_py["(生产态 / production) ReconciliationEngine — MOD-INF-026 L4 注册 / reconciler<br/>ReconciliationEngine — MOD-INF-026 L4 注册表 vs 磁盘对账引擎<br/>文件: asset_inventory/reconciler.py"]
    src_zephyr_infrastructure_asset_inventory_registry_adapter_py["(生产态 / production) MOD-INF-026 §17 — 24 个异构注册表统一解析适配器。 / registry_adapter<br/>MOD-INF-026 §17 — 24 个异构注册表统一解析适配器。<br/>文件: asset_inventory/registry_adapter.py"]
    src_zephyr_infrastructure_asset_inventory_scanner_py["(生产态 / production) AssetDiscoveryScanner — MOD-INF-026 L1 全 / scanner<br/>AssetDiscoveryScanner — MOD-INF-026 L1 全量文件系统扫描器<br/>文件: asset_inventory/scanner.py"]
    src_zephyr_infrastructure_asset_inventory_telemetry_py["(生产态 / production) AssetInventoryTelemetry — MOD-INF-026 自监 / telemetry<br/>AssetInventoryTelemetry — MOD-INF-026 自监控指标<br/>文件: asset_inventory/telemetry.py"]
    src_zephyr_infrastructure_auto_fix_engine_engine_py["(生产态 / production) 引擎 / engine<br/>引擎，主要提供安全门禁、级联断路器、修复预算等功能<br/>文件: auto_fix_engine/engine.py"]
    src_zephyr_infrastructure_budget_enforcement_rbac_bridge_py["(生产态 / production) 预算enforcement.rbacbridge — 基础设施层 R / rbac_bridge<br/>budget_enforcement.rbac_bridge — 基础设施层 RBAC 桥接适配器。<br/>文件: budget_enforcement/rbac_bridge.py"]
    src_zephyr_infrastructure_capacity_assurance_contracts_batch1_infra_py["(生产态 / production) Batch1 基础设施层契约 — 15条 Pydantic v2 Schema（ / batch1_infra<br/>Batch1 基础设施层契约 — 15条 Pydantic v2 Schema（SLO/Error Budget/Token Budget/Kill Switch/Sandbox/Graceful Degradation）.<br/>文件: contracts/batch1_infra.py"]
    src_zephyr_infrastructure_capacity_assurance_contracts_batch3_integration_py["(生产态 / production) Batch3 集成层契约 — 14条 Pydantic v2 Schema（OT / batch3_integration<br/>Batch3 集成层契约 — 14条 Pydantic v2 Schema（OTel/W3C/跨模块CT-1~4/DR/容量预测/语义缓存）.<br/>文件: contracts/batch3_integration.py"]
    src_zephyr_infrastructure_config_validator_py["(生产态 / production) M-12 ConfigValidator — 配置参数校验器 / config_validator<br/>M-12 ConfigValidator — 配置参数校验器<br/>文件: infrastructure/config_validator.py"]
    src_zephyr_infrastructure_contract_tester_py["(生产态 / production) M-11 ContractTester — 契约测试框架 / contract_tester<br/>M-11 ContractTester — 契约测试框架<br/>文件: infrastructure/contract_tester.py"]
    src_zephyr_infrastructure_pipeline_backpressure_types_py["(生产态 / production) backpressure类型定义 / backpressure_types.py - Pipeline backpressure signal data ty<br/>backpressure类型定义，管线的功能模块。<br/>文件: pipeline/backpressure_types.py"]
    src_zephyr_infrastructure_pipeline_ct_pipe_routing_py["(生产态 / production) CT-PIPE-ORC-001 — TaskCard -> 管线入口节点路由 / ct_pipe_routing<br/>CT-PIPE-ORC-001 — TaskCard -> 管线入口节点路由<br/>文件: pipeline/ct_pipe_routing.py"]
    src_zephyr_infrastructure_pipeline_model_router_py["(生产态 / production) ModelRouter — 模型路由与降级链管理 / model_router<br/>ModelRouter — 模型路由与降级链管理<br/>文件: pipeline/model_router.py"]
    src_zephyr_infrastructure_queue_task_scheduler_py["(生产态 / production) Task Scheduler — 任务调度器。 / task_scheduler<br/>Task Scheduler — 任务调度器。<br/>文件: queue/task_scheduler.py"]
    src_zephyr_infrastructure_system_telemetry_budget_telemetry_bridge_py["(生产态 / production) 预算遥测桥接 / _budget_telemetry_bridge<br/>预算遥测桥接，基础设施的桥接，连接两个子系统，做数据和调用的转换中转。<br/>文件: system_telemetry/_budget_telemetry_bridge.py"]
    src_zephyr_infrastructure_system_telemetry_contract_metrics_py["(生产态 / production) 契约指标 / ZephyrAlpha — system-telemetry/contract_metrics.py<br/>契约指标，基础设施的记录器，把发生的事件/结果记下来留档。<br/>文件: system_telemetry/contract_metrics.py"]
    src_zephyr_infrastructure_system_telemetry_metrics_blueprint_metrics_py["(生产态 / production) 蓝图metrics — 蓝图使用追踪 instrumentati / blueprint_metrics<br/>blueprint_metrics — 蓝图使用追踪 instrumentation<br/>文件: metrics/blueprint_metrics.py"]
    src_zephyr_trading_main_py["(生产态 / production) python -m zephyr.trading — AutoRuntime C / __main__<br/>python -m zephyr.trading — AutoRuntime Core 入口<br/>文件: trading/__main__.py"]
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
    src_zephyr_infrastructure_contract_tester_py ~~~ src_zephyr_infrastructure_pipeline_backpressure_types_py
    src_zephyr_infrastructure_pipeline_backpressure_types_py ~~~ src_zephyr_infrastructure_pipeline_ct_pipe_routing_py
    src_zephyr_infrastructure_pipeline_ct_pipe_routing_py ~~~ src_zephyr_infrastructure_pipeline_model_router_py
    src_zephyr_infrastructure_pipeline_model_router_py ~~~ src_zephyr_infrastructure_queue_task_scheduler_py
    src_zephyr_infrastructure_queue_task_scheduler_py ~~~ src_zephyr_infrastructure_system_telemetry_budget_telemetry_bridge_py
    src_zephyr_infrastructure_system_telemetry_budget_telemetry_bridge_py ~~~ src_zephyr_infrastructure_system_telemetry_contract_metrics_py
    src_zephyr_infrastructure_system_telemetry_contract_metrics_py ~~~ src_zephyr_infrastructure_system_telemetry_metrics_blueprint_metrics_py
    src_zephyr_infrastructure_system_telemetry_metrics_blueprint_metrics_py ~~~ src_zephyr_trading_main_py
    src_zephyr_infrastructure_asset_inventory_models_py["(生产态 / production) AssetInventoryModels — MOD-INF-026 Pydan / models<br/>AssetInventoryModels — MOD-INF-026 Pydantic V2 共享数据模型<br/>文件: asset_inventory/models.py"]
    src_zephyr_infrastructure_auto_fix_engine_batch_fixer_py["(生产态 / production) 批次修复器 / batch_fixer<br/>批次修复器，主要提供conflict解析器、conflict解析器、idempotency等功能，供engine.py使用<br/>文件: auto_fix_engine/batch_fixer.py"]
    src_zephyr_infrastructure_auto_fix_engine_compliance_auditor_py["(生产态 / production) 合规审计器 / compliance_auditor<br/>合规审计器，提供retentiondays、retentiondays、审计修复、验证evidence等功能，是引擎的组成部分<br/>文件: auto_fix_engine/compliance_auditor.py"]
    src_zephyr_infrastructure_auto_fix_engine_escalation_bridge_py["(生产态 / production) escalation桥接 / escalation_bridge<br/>escalation桥接，连接两个子系统，做数据和调用的转换中转，主要提供escalate、escalatedeadletter、获取escalation历史、enabled等功能，是引擎的组成部分<br/>文件: auto_fix_engine/escalation_bridge.py"]
    src_zephyr_infrastructure_auto_fix_engine_fix_health_check_py["(生产态 / production) 修复健康检查 / fix_health_check<br/>修复健康检查，检查某项条件是否满足，主要提供检查配置、数据库路径、数据库路径、检查数据库等功能，是引擎的组成部分<br/>文件: auto_fix_engine/fix_health_check.py"]
    src_zephyr_infrastructure_auto_fix_engine_fix_pattern_miner_py["(生产态 / production) 修复模式miner / fix_pattern_miner<br/>修复模式miner，提供数据库路径、数据库路径、模式缓存、模式缓存等功能，是引擎的组成部分<br/>文件: auto_fix_engine/fix_pattern_miner.py"]
    src_zephyr_infrastructure_auto_fix_engine_fix_report_py["(生产态 / production) 修复报告 / fix_report<br/>修复报告，按规则生成所需的数据或报告，主要提供历史、历史、生成、生成摘要等功能，是引擎的组成部分<br/>文件: auto_fix_engine/fix_report.py"]
    src_zephyr_infrastructure_auto_fix_engine_fix_safety_py["(生产态 / production) 修复安全 / fix_safety<br/>修复安全，在关键节点检查是否放行，主要提供enabled、enabled、检查等功能，是引擎的组成部分<br/>文件: auto_fix_engine/fix_safety.py"]
    src_zephyr_infrastructure_auto_fix_engine_shadow_workspace_py["(生产态 / production) shadowworkspace / shadow_workspace<br/>shadowworkspace，主要提供运行type检查、运行测试、运行ruff等功能，供engine.py使用<br/>文件: auto_fix_engine/shadow_workspace.py"]
    src_zephyr_infrastructure_pipeline_models_py["(生产态 / production) Pipeline 数据模型 / models<br/>Pipeline 数据模型<br/>文件: pipeline/models.py"]
    src_zephyr_infrastructure_system_telemetry_facade_py["(生产态 / production) Telemetry — 系统遥测门面类（MOD-INF-015 v2.1.0） / facade<br/>Telemetry — 系统遥测门面类（MOD-INF-015 v2.1.0）<br/>文件: system_telemetry/facade.py"]
    src_zephyr_trading_auto_runtime_core_py["(生产态 / production) AutoRuntimeCore — 三层运行时运营中心（系统大脑） / auto_runtime_core<br/>AutoRuntimeCore — 三层运行时运营中心（系统大脑）<br/>文件: trading/auto_runtime_core.py"]
    src_zephyr_infrastructure_asset_inventory_models_py ~~~ src_zephyr_infrastructure_auto_fix_engine_batch_fixer_py
    src_zephyr_infrastructure_auto_fix_engine_batch_fixer_py ~~~ src_zephyr_infrastructure_auto_fix_engine_compliance_auditor_py
    src_zephyr_infrastructure_auto_fix_engine_compliance_auditor_py ~~~ src_zephyr_infrastructure_auto_fix_engine_escalation_bridge_py
    src_zephyr_infrastructure_auto_fix_engine_escalation_bridge_py ~~~ src_zephyr_infrastructure_auto_fix_engine_fix_health_check_py
    src_zephyr_infrastructure_auto_fix_engine_fix_health_check_py ~~~ src_zephyr_infrastructure_auto_fix_engine_fix_pattern_miner_py
    src_zephyr_infrastructure_auto_fix_engine_fix_pattern_miner_py ~~~ src_zephyr_infrastructure_auto_fix_engine_fix_report_py
    src_zephyr_infrastructure_auto_fix_engine_fix_report_py ~~~ src_zephyr_infrastructure_auto_fix_engine_fix_safety_py
    src_zephyr_infrastructure_auto_fix_engine_fix_safety_py ~~~ src_zephyr_infrastructure_auto_fix_engine_shadow_workspace_py
    src_zephyr_infrastructure_auto_fix_engine_shadow_workspace_py ~~~ src_zephyr_infrastructure_pipeline_models_py
    src_zephyr_infrastructure_pipeline_models_py ~~~ src_zephyr_infrastructure_system_telemetry_facade_py
    src_zephyr_infrastructure_system_telemetry_facade_py ~~~ src_zephyr_trading_auto_runtime_core_py
    src_zephyr_infrastructure_auto_fix_engine_fix_budget_py["(生产态 / production) 修复预算 / fix_budget<br/>修复预算，提供daily限制、monthly限制、llm令牌限制、检查等功能，是引擎的组成部分<br/>文件: auto_fix_engine/fix_budget.py"]
    src_zephyr_infrastructure_auto_fix_engine_fix_reliability_py["(生产态 / production) 修复可靠性 / fix_reliability<br/>修复可靠性，拦截不合规的操作，主要提供存活时间、存活时间、检查、记录等功能，是引擎的组成部分<br/>文件: auto_fix_engine/fix_reliability.py"]
    src_zephyr_infrastructure_file_watcher_py["(生产态 / production) 文件watcher / file_watcher<br/>文件watcher，基础设施的类型，定义数据类型和枚举。<br/>文件: infrastructure/file_watcher.py"]
    src_zephyr_infrastructure_queue_task_queue_py["(生产态 / production) Task Queue — 后台任务队列 + 自动 Dispatch。 / task_queue<br/>Task Queue — 后台任务队列 + 自动 Dispatch。<br/>文件: queue/task_queue.py"]
    src_zephyr_infrastructure_system_telemetry_ai_behavior_event_sink_py["(生产态 / production) 遥测 · aibehavior/eventsink — AI 行为遥测事件管 / event_sink<br/>遥测 · ai_behavior/event_sink — AI 行为遥测事件管道。<br/>文件: ai_behavior/event_sink.py"]
    src_zephyr_infrastructure_system_telemetry_archive_cold_stub_py["(生产态 / production) 遥测 · archive/coldstub — 冷存储归档管道。 / cold_stub<br/>遥测 · archive/cold_stub — 冷存储归档管道。<br/>文件: archive/cold_stub.py"]
    src_zephyr_infrastructure_system_telemetry_traces_span_stub_py["(生产态 / production) 遥测 · traces/spanstub — W3C TraceContext / span_stub<br/>遥测 · traces/span_stub — W3C TraceContext 分布式追踪管道。<br/>文件: traces/span_stub.py"]
    src_zephyr_infrastructure_system_telemetry_watchdog_py["(生产态 / production) 三冗余 Watchdog（CT-WATCHDOG-001）——互检+Panic  / watchdog<br/>三冗余 Watchdog（CT-WATCHDOG-001）——互检+Panic Mode+Dead Man's Switch。<br/>文件: system_telemetry/watchdog.py"]
    src_zephyr_trading_auto_integrator_py["(生产态 / production) AutoIntegrator — 自动接入器 / auto_integrator<br/>AutoIntegrator — 自动接入器<br/>文件: trading/auto_integrator.py"]
    src_zephyr_trading_boot_hooks_py["(生产态 / production) 从 TaskRepository 查询 task 的 sou / boot_hooks<br/>从 TaskRepository 查询 task 的 source_blueprint，失败返回空串。<br/>文件: trading/boot_hooks.py"]
    src_zephyr_trading_capability_sync_py["(生产态 / production) 能力同步 / capability_sync<br/>能力同步，主要提供注册表、注册表、同步A2A等功能，供自动运行时co使用<br/>文件: trading/capability_sync.py"]
    src_zephyr_trading_lifecycle_manager_py["(生产态 / production) 生命周期管理器——Boot + Shutdown 序列。 / lifecycle_manager<br/>生命周期管理器——Boot + Shutdown 序列。<br/>文件: trading/lifecycle_manager.py"]
    src_zephyr_trading_status_dashboard_py["(生产态 / production) StatusDashboard — 实时状态面板 / status_dashboard<br/>StatusDashboard — 实时状态面板<br/>文件: trading/status_dashboard.py"]
    src_zephyr_infrastructure_auto_fix_engine_fix_budget_py ~~~ src_zephyr_infrastructure_auto_fix_engine_fix_reliability_py
    src_zephyr_infrastructure_auto_fix_engine_fix_reliability_py ~~~ src_zephyr_infrastructure_file_watcher_py
    src_zephyr_infrastructure_file_watcher_py ~~~ src_zephyr_infrastructure_queue_task_queue_py
    src_zephyr_infrastructure_queue_task_queue_py ~~~ src_zephyr_infrastructure_system_telemetry_ai_behavior_event_sink_py
    src_zephyr_infrastructure_system_telemetry_ai_behavior_event_sink_py ~~~ src_zephyr_infrastructure_system_telemetry_archive_cold_stub_py
    src_zephyr_infrastructure_system_telemetry_archive_cold_stub_py ~~~ src_zephyr_infrastructure_system_telemetry_traces_span_stub_py
    src_zephyr_infrastructure_system_telemetry_traces_span_stub_py ~~~ src_zephyr_infrastructure_system_telemetry_watchdog_py
    src_zephyr_infrastructure_system_telemetry_watchdog_py ~~~ src_zephyr_trading_auto_integrator_py
    src_zephyr_trading_auto_integrator_py ~~~ src_zephyr_trading_boot_hooks_py
    src_zephyr_trading_boot_hooks_py ~~~ src_zephyr_trading_capability_sync_py
    src_zephyr_trading_capability_sync_py ~~~ src_zephyr_trading_lifecycle_manager_py
    src_zephyr_trading_lifecycle_manager_py ~~~ src_zephyr_trading_status_dashboard_py
    src_zephyr_infrastructure_auto_fix_engine_models_py["(生产态 / production) 模型 / models<br/>模型，引擎的功能模块。<br/>文件: auto_fix_engine/models.py"]
    src_zephyr_infrastructure_observability_notifier_py["(生产态 / production) Notifier — 多渠道 Owner 通知。 / notifier<br/>Notifier — 多渠道 Owner 通知。<br/>文件: observability/notifier.py"]
    src_zephyr_infrastructure_runtime_gate_coordinator_py["(生产态 / production) Rollback->Gate 协调器 — freezeall / thawa / gate_coordinator<br/>Rollback->Gate 协调器 — freeze_all / thaw_all<br/>文件: runtime/gate_coordinator.py"]
    src_zephyr_infrastructure_sla_sla_monitor_py["(生产态 / production) SLA Monitor — 服务等级协议 (SLA) 监控 RTO/RPO。 / sla_monitor<br/>SLA Monitor — 服务等级协议 (SLA) 监控 RTO/RPO。<br/>文件: sla/sla_monitor.py"]
    src_zephyr_infrastructure_system_telemetry_health_aggregator_py["(生产态 / production) 健康聚合器（Health Aggregator） / health_aggregator<br/>健康聚合器（Health Aggregator）<br/>文件: system_telemetry/health_aggregator.py"]
    src_zephyr_infrastructure_system_telemetry_logs_structured_sink_py["(生产态 / production) logs/structuredsink — 结构化日志管道（DSYSTEM / structured_sink<br/>logs/structured_sink — 结构化日志管道（D_SYSTEM_TELEMETRY）。<br/>文件: logs/structured_sink.py"]
    src_zephyr_trading_ai_audit_logger_py["(生产态 / production) AiAuditLogger — AI 行为审计日志 / ai_audit_logger<br/>AiAuditLogger — AI 行为审计日志<br/>文件: trading/ai_audit_logger.py"]
    src_zephyr_trading_dream_cycle_py["(生产态 / production) DreamCycle — 知识固化引擎 / dream_cycle<br/>DreamCycle — 知识固化引擎<br/>文件: trading/dream_cycle.py"]
    src_zephyr_trading_finalizer_py["(生产态 / production) Finalizer — 优雅清理器 / finalizer<br/>Finalizer — 优雅清理器<br/>文件: trading/finalizer.py"]
    src_zephyr_trading_health_monitor_py["(生产态 / production) HealthMonitor — 健康监控 + 自愈 / health_monitor<br/>HealthMonitor — 健康监控 + 自愈<br/>文件: trading/health_monitor.py"]
    src_zephyr_trading_integration_registry_py["(生产态 / production) IntegrationRegistry — 集成注册表 / integration_registry<br/>IntegrationRegistry — 集成注册表<br/>文件: trading/integration_registry.py"]
    src_zephyr_trading_night_shift_queue_py["(生产态 / production) NightShiftQueue — 夜班登记表持久化 / night_shift_queue<br/>NightShiftQueue — 夜班登记表持久化<br/>文件: trading/night_shift_queue.py"]
    src_zephyr_trading_orphan_detector_py["(生产态 / production) OrphanDetector — 孤儿检测器 / orphan_detector<br/>OrphanDetector — 孤儿检测器<br/>文件: trading/orphan_detector.py"]
    src_zephyr_trading_runtime_config_py["(生产态 / production) 启动前配置完整性校验（5.71.1 治本）——必填字段/类型 / runtime_config<br/>启动前配置完整性校验（5.71.1 治本）——必填字段/类型/范围，失败 fail-fast。<br/>文件: trading/runtime_config.py"]
    src_zephyr_trading_stop_gate_py["(生产态 / production) StopGate — 质量闸门 / stop_gate<br/>StopGate — 质量闸门<br/>文件: trading/stop_gate.py"]
    src_zephyr_trading_work_orchestrator_py["(生产态 / production) 工作编排子系统——决定什么工作、什么时候、用什么模型、什么顺 / work_orchestrator<br/>工作编排子系统——决定什么工作、什么时候、用什么模型、什么顺序。<br/>文件: trading/work_orchestrator.py"]
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
    src_zephyr_infrastructure_system_telemetry_trace_bridge_py["(生产态 / production) 追踪桥接 / _trace_bridge<br/>追踪桥接，基础设施的桥接，连接两个子系统，做数据和调用的转换中转。<br/>文件: system_telemetry/_trace_bridge.py"]
    src_zephyr_infrastructure_system_telemetry_health_probes_py["(生产态 / production) 三态健康探针协议（Health Probes — CT-HEALTH-001） / health_probes<br/>三态健康探针协议（Health Probes — CT-HEALTH-001）<br/>文件: system_telemetry/health_probes.py"]
    src_zephyr_trading_module_onboarding_scanner_py["(生产态 / production) ModuleOnboardingScanner — 模块接入扫描器 / module_onboarding_scanner<br/>ModuleOnboardingScanner — 模块接入扫描器<br/>文件: trading/module_onboarding_scanner.py"]
    src_zephyr_trading_resource_optimization_py["(生产态 / production) resourceoptimization / resource_optimization.py - MAPE-K autonomic resource optimiz<br/>resourceoptimization，交易的功能模块。<br/>文件: trading/resource_optimization.py"]
    src_zephyr_trading_work_dag_py["(生产态 / production) WorkDAG + WorkItem — 工作编排数据模型 / work_dag<br/>WorkDAG + WorkItem — 工作编排数据模型<br/>文件: trading/work_dag.py"]
    src_zephyr_infrastructure_system_telemetry_trace_bridge_py ~~~ src_zephyr_infrastructure_system_telemetry_health_probes_py
    src_zephyr_infrastructure_system_telemetry_health_probes_py ~~~ src_zephyr_trading_module_onboarding_scanner_py
    src_zephyr_trading_module_onboarding_scanner_py ~~~ src_zephyr_trading_resource_optimization_py
    src_zephyr_trading_resource_optimization_py ~~~ src_zephyr_trading_work_dag_py
    src_zephyr_shared_lifecycle_daemon_registry_py["(生产态 / production) daemon注册表 / daemon_registry.py - unified daemon thread registry + resour<br/>daemon注册表，lifecycle的状态机，管理状态流转。<br/>文件: lifecycle/daemon_registry.py"]
    src_zephyr_shared_lifecycle_lazy_loader_py["(生产态 / production) lazy加载器 / lazy_loader.py - Lazy module loading registry<br/>lazy加载器，lifecycle的功能模块。<br/>文件: lifecycle/lazy_loader.py"]
    src_zephyr_shared_lifecycle_resource_optimization_models_py["(生产态 / production) resourceoptimization模型 / models.py - Pydantic data models for resource optimization e<br/>resourceoptimization模型，lifecycle的功能模块。<br/>文件: lifecycle/resource_optimization_models.py"]
    src_zephyr_trading_capability_registry_py["(生产态 / production) CapabilityRegistry — 能力注册中心 / capability_registry<br/>CapabilityRegistry — 能力注册中心<br/>文件: trading/capability_registry.py"]
    src_zephyr_shared_lifecycle_daemon_registry_py ~~~ src_zephyr_shared_lifecycle_lazy_loader_py
    src_zephyr_shared_lifecycle_lazy_loader_py ~~~ src_zephyr_shared_lifecycle_resource_optimization_models_py
    src_zephyr_shared_lifecycle_resource_optimization_models_py ~~~ src_zephyr_trading_capability_registry_py
    src_zephyr_trading_capability_card_py["(生产态 / production) CapabilityCard — 能力卡片数据模型 / capability_card<br/>CapabilityCard — 能力卡片数据模型<br/>文件: trading/capability_card.py"]
    src_zephyr_infrastructure_warm_hot_gate_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_config_validator_py
    src_zephyr_infrastructure_warm_hot_gate_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_contract_tester_py
    src_zephyr_infrastructure_asset_inventory_dashboard_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_asset_inventory_models_py
    src_zephyr_infrastructure_asset_inventory_classifier_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_asset_inventory_models_py
    src_zephyr_infrastructure_asset_inventory_lifecycle_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_asset_inventory_models_py
    src_zephyr_infrastructure_asset_inventory_index_generator_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_asset_inventory_models_py
    src_zephyr_infrastructure_asset_inventory_registry_adapter_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_asset_inventory_models_py
    src_zephyr_infrastructure_asset_inventory_telemetry_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_system_telemetry_facade_py
    src_zephyr_infrastructure_asset_inventory_scanner_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_asset_inventory_models_py
    src_zephyr_infrastructure_auto_fix_engine_alignment_syncer_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_asset_inventory_reconciler_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_asset_inventory_models_py
    src_zephyr_infrastructure_auto_fix_engine_all_completer_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_asset_inventory_main_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_asset_inventory_dashboard_py
    src_zephyr_infrastructure_asset_inventory_main_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_asset_inventory_dependency_py
    src_zephyr_infrastructure_asset_inventory_main_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_asset_inventory_classifier_py
    src_zephyr_infrastructure_asset_inventory_main_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_asset_inventory_models_py
    src_zephyr_infrastructure_asset_inventory_main_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_asset_inventory_index_generator_py
    src_zephyr_infrastructure_asset_inventory_main_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_asset_inventory_registry_adapter_py
    src_zephyr_infrastructure_asset_inventory_main_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_asset_inventory_telemetry_py
    src_zephyr_infrastructure_asset_inventory_main_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_asset_inventory_scanner_py
    src_zephyr_infrastructure_asset_inventory_main_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_asset_inventory_reconciler_py
    src_zephyr_infrastructure_auto_fix_engine_batch_fixer_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_fix_budget_py
    src_zephyr_infrastructure_auto_fix_engine_batch_fixer_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_fix_reliability_py
    src_zephyr_infrastructure_auto_fix_engine_batch_fixer_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_config_fixer_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_dedup_extractor_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_compliance_auditor_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_engine_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_batch_fixer_py
    src_zephyr_infrastructure_auto_fix_engine_engine_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_compliance_auditor_py
    src_zephyr_infrastructure_auto_fix_engine_engine_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_escalation_bridge_py
    src_zephyr_infrastructure_auto_fix_engine_engine_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_fix_budget_py
    src_zephyr_infrastructure_auto_fix_engine_engine_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_fix_report_py
    src_zephyr_infrastructure_auto_fix_engine_engine_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_fix_safety_py
    src_zephyr_infrastructure_auto_fix_engine_engine_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_fix_health_check_py
    src_zephyr_infrastructure_auto_fix_engine_engine_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_fix_pattern_miner_py
    src_zephyr_infrastructure_auto_fix_engine_engine_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_fix_reliability_py
    src_zephyr_infrastructure_auto_fix_engine_engine_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_engine_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_shadow_workspace_py
    src_zephyr_infrastructure_auto_fix_engine_drift_fixer_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_event_hooks_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_engine_py
    src_zephyr_infrastructure_auto_fix_engine_event_hooks_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_fix_diff_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_dep_version_fixer_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_escalation_bridge_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_fix_budget_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_fix_scheduler_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_fix_report_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_fix_safety_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_fix_health_check_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_import_fixer_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_fix_pattern_miner_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_fix_reliability_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_self_heal_agent_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_llm_fix_adapter_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_fix_safety_py
    src_zephyr_infrastructure_auto_fix_engine_llm_fix_adapter_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_scaffold_registrar_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_budget_enforcement_init_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_budget_enforcement_rbac_bridge_py
    src_zephyr_infrastructure_auto_fix_engine_shadow_workspace_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_auto_fix_engine_main_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_engine_py
    src_zephyr_infrastructure_auto_fix_engine_zombie_cleaner_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_auto_fix_engine_models_py
    src_zephyr_infrastructure_capacity_assurance_contracts_contract_bus_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_capacity_assurance_contracts_batch3_integration_py
    src_zephyr_infrastructure_capacity_assurance_contracts_contract_bus_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_capacity_assurance_contracts_batch1_infra_py
    src_zephyr_infrastructure_pipeline_circuit_breaker_manager_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_pipeline_models_py
    src_zephyr_infrastructure_pipeline_backpressure_manager_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_pipeline_backpressure_types_py
    src_zephyr_infrastructure_pipeline_ct_pipe_routing_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_pipeline_models_py
    src_zephyr_infrastructure_pipeline_dead_letter_queue_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_pipeline_models_py
    src_zephyr_infrastructure_pipeline_cost_tracker_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_pipeline_models_py
    src_zephyr_infrastructure_pipeline_cost_tracker_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_pipeline_model_router_py
    src_zephyr_infrastructure_pipeline_pipeline_agent_bridge_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_pipeline_models_py
    src_zephyr_infrastructure_pipeline_preemption_manager_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_pipeline_models_py
    src_zephyr_infrastructure_pipeline_routing_plugins_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_pipeline_ct_pipe_routing_py
    src_zephyr_infrastructure_pipeline_routing_plugins_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_pipeline_models_py
    src_zephyr_infrastructure_system_telemetry_auto_bootstrap_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_system_telemetry_contract_metrics_py
    src_zephyr_infrastructure_system_telemetry_auto_bootstrap_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_system_telemetry_facade_py
    src_zephyr_infrastructure_system_telemetry_auto_bootstrap_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_system_telemetry_budget_telemetry_bridge_py
    src_zephyr_infrastructure_system_telemetry_auto_bootstrap_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_system_telemetry_metrics_blueprint_metrics_py
    src_zephyr_infrastructure_system_telemetry_health_aggregator_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_system_telemetry_health_probes_py
    src_zephyr_infrastructure_system_telemetry_facade_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_system_telemetry_health_aggregator_py
    src_zephyr_infrastructure_system_telemetry_facade_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_system_telemetry_watchdog_py
    src_zephyr_infrastructure_system_telemetry_facade_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_system_telemetry_ai_behavior_event_sink_py
    src_zephyr_infrastructure_system_telemetry_facade_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_system_telemetry_archive_cold_stub_py
    src_zephyr_infrastructure_system_telemetry_facade_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_system_telemetry_traces_span_stub_py
    src_zephyr_infrastructure_system_telemetry_ai_behavior_event_sink_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_system_telemetry_logs_structured_sink_py
    src_zephyr_infrastructure_system_telemetry_logs_structured_sink_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_system_telemetry_trace_bridge_py
    src_zephyr_infrastructure_system_telemetry_logs_init_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_system_telemetry_logs_structured_sink_py
    src_zephyr_infrastructure_system_telemetry_traces_span_stub_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_system_telemetry_trace_bridge_py
    src_zephyr_trading_action_dispatcher_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_queue_task_scheduler_py
    src_zephyr_trading_auto_integrator_py -->|导入依赖 / import_depends| src_zephyr_trading_capability_registry_py
    src_zephyr_trading_auto_integrator_py -->|导入依赖 / import_depends| src_zephyr_trading_capability_card_py
    src_zephyr_trading_auto_integrator_py -->|导入依赖 / import_depends| src_zephyr_trading_module_onboarding_scanner_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_file_watcher_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_queue_task_queue_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_trading_ai_audit_logger_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_trading_auto_integrator_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_trading_capability_sync_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_trading_capability_registry_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_trading_dream_cycle_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_trading_boot_hooks_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_trading_finalizer_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_trading_night_shift_queue_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_trading_lifecycle_manager_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_trading_module_onboarding_scanner_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_trading_integration_registry_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_trading_health_monitor_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_trading_orphan_detector_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_trading_runtime_config_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_trading_resource_optimization_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_trading_work_dag_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_trading_status_dashboard_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_trading_stop_gate_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_trading_work_orchestrator_py
    src_zephyr_trading_capability_sync_py -->|导入依赖 / import_depends| src_zephyr_trading_capability_registry_py
    src_zephyr_trading_capability_sync_py -->|导入依赖 / import_depends| src_zephyr_trading_capability_card_py
    src_zephyr_trading_capability_registry_py -->|导入依赖 / import_depends| src_zephyr_trading_capability_card_py
    src_zephyr_trading_boot_hooks_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_observability_notifier_py
    src_zephyr_trading_boot_hooks_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_runtime_gate_coordinator_py
    src_zephyr_trading_boot_hooks_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_sla_sla_monitor_py
    src_zephyr_trading_boot_hooks_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_system_telemetry_health_aggregator_py
    src_zephyr_trading_boot_hooks_py -->|导入依赖 / import_depends| src_zephyr_trading_finalizer_py
    src_zephyr_trading_lifecycle_manager_py -->|导入依赖 / import_depends| src_zephyr_trading_ai_audit_logger_py
    src_zephyr_trading_lifecycle_manager_py -->|导入依赖 / import_depends| src_zephyr_trading_capability_registry_py
    src_zephyr_trading_lifecycle_manager_py -->|导入依赖 / import_depends| src_zephyr_trading_dream_cycle_py
    src_zephyr_trading_lifecycle_manager_py -->|导入依赖 / import_depends| src_zephyr_trading_finalizer_py
    src_zephyr_trading_lifecycle_manager_py -->|导入依赖 / import_depends| src_zephyr_trading_night_shift_queue_py
    src_zephyr_trading_lifecycle_manager_py -->|导入依赖 / import_depends| src_zephyr_trading_integration_registry_py
    src_zephyr_trading_lifecycle_manager_py -->|导入依赖 / import_depends| src_zephyr_trading_health_monitor_py
    src_zephyr_trading_lifecycle_manager_py -->|导入依赖 / import_depends| src_zephyr_trading_runtime_config_py
    src_zephyr_trading_lifecycle_manager_py -->|导入依赖 / import_depends| src_zephyr_trading_stop_gate_py
    src_zephyr_trading_lifecycle_manager_py -->|导入依赖 / import_depends| src_zephyr_trading_work_orchestrator_py
    src_zephyr_trading_module_onboarding_scanner_py -->|导入依赖 / import_depends| src_zephyr_trading_capability_registry_py
    src_zephyr_trading_health_monitor_py -->|导入依赖 / import_depends| src_zephyr_trading_resource_optimization_py
    src_zephyr_trading_orphan_detector_py -->|导入依赖 / import_depends| src_zephyr_trading_capability_registry_py
    src_zephyr_trading_orphan_detector_py -->|导入依赖 / import_depends| src_zephyr_trading_module_onboarding_scanner_py
    src_zephyr_trading_resource_optimization_py -->|导入依赖 / import_depends| src_zephyr_shared_lifecycle_daemon_registry_py
    src_zephyr_trading_resource_optimization_py -->|导入依赖 / import_depends| src_zephyr_shared_lifecycle_lazy_loader_py
    src_zephyr_trading_resource_optimization_py -->|导入依赖 / import_depends| src_zephyr_shared_lifecycle_resource_optimization_models_py
    src_zephyr_trading_status_dashboard_py -->|导入依赖 / import_depends| src_zephyr_trading_capability_registry_py
    src_zephyr_trading_status_dashboard_py -->|导入依赖 / import_depends| src_zephyr_trading_night_shift_queue_py
    src_zephyr_trading_status_dashboard_py -->|导入依赖 / import_depends| src_zephyr_trading_health_monitor_py
    src_zephyr_trading_status_dashboard_py -->|导入依赖 / import_depends| src_zephyr_trading_orphan_detector_py
    src_zephyr_trading_status_dashboard_py -->|导入依赖 / import_depends| src_zephyr_trading_work_orchestrator_py
    src_zephyr_trading_windows_service_py -->|导入依赖 / import_depends| src_zephyr_trading_auto_runtime_core_py
    src_zephyr_trading_windows_service_py -->|导入依赖 / import_depends| src_zephyr_trading_runtime_config_py
    src_zephyr_trading_windows_service_py -->|导入依赖 / import_depends| src_zephyr_trading_main_py
    src_zephyr_trading_work_orchestrator_py -->|导入依赖 / import_depends| src_zephyr_trading_capability_registry_py
    src_zephyr_trading_work_orchestrator_py -->|导入依赖 / import_depends| src_zephyr_trading_work_dag_py
    src_zephyr_trading_main_py -->|导入依赖 / import_depends| src_zephyr_trading_auto_runtime_core_py
    src_zephyr_trading_main_py -->|导入依赖 / import_depends| src_zephyr_trading_runtime_config_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class docs_01_policies_and_standards_registry_catalogs_infrastructure_registry_yaml_INFRA_DB_001,docs_01_policies_and_standards_registry_catalogs_infrastructure_registry_yaml_INFRA_DB_002,docs_01_policies_and_standards_registry_catalogs_infrastructure_registry_yaml_INFRA_DB_003,docs_01_policies_and_standards_registry_catalogs_infrastructure_registry_yaml_INFRA_DB_006,src_zephyr_infrastructure_asset_inventory_main_py,src_zephyr_infrastructure_asset_inventory_classifier_py,src_zephyr_infrastructure_asset_inventory_dashboard_py,src_zephyr_infrastructure_asset_inventory_dependency_py,src_zephyr_infrastructure_asset_inventory_index_generator_py,src_zephyr_infrastructure_asset_inventory_lifecycle_py,src_zephyr_infrastructure_asset_inventory_mcp_server_py,src_zephyr_infrastructure_asset_inventory_metadata_py,src_zephyr_infrastructure_asset_inventory_models_py,src_zephyr_infrastructure_asset_inventory_reconciler_py,src_zephyr_infrastructure_asset_inventory_registry_adapter_py,src_zephyr_infrastructure_asset_inventory_scanner_py,src_zephyr_infrastructure_asset_inventory_telemetry_py,src_zephyr_infrastructure_asset_inventory_trust_anchor_py,src_zephyr_infrastructure_auto_diagnostics_py,src_zephyr_infrastructure_auto_fix_engine_main_py,src_zephyr_infrastructure_auto_fix_engine_alignment_syncer_py,src_zephyr_infrastructure_auto_fix_engine_all_completer_py,src_zephyr_infrastructure_auto_fix_engine_batch_fixer_py,src_zephyr_infrastructure_auto_fix_engine_compliance_auditor_py,src_zephyr_infrastructure_auto_fix_engine_config_fixer_py,src_zephyr_infrastructure_auto_fix_engine_dedup_extractor_py,src_zephyr_infrastructure_auto_fix_engine_dep_version_fixer_py,src_zephyr_infrastructure_auto_fix_engine_drift_fixer_py,src_zephyr_infrastructure_auto_fix_engine_engine_py,src_zephyr_infrastructure_auto_fix_engine_escalation_bridge_py,src_zephyr_infrastructure_auto_fix_engine_event_hooks_py,src_zephyr_infrastructure_auto_fix_engine_fix_budget_py,src_zephyr_infrastructure_auto_fix_engine_fix_diff_py,src_zephyr_infrastructure_auto_fix_engine_fix_health_check_py,src_zephyr_infrastructure_auto_fix_engine_fix_pattern_miner_py,src_zephyr_infrastructure_auto_fix_engine_fix_reliability_py,src_zephyr_infrastructure_auto_fix_engine_fix_report_py,src_zephyr_infrastructure_auto_fix_engine_fix_safety_py,src_zephyr_infrastructure_auto_fix_engine_fix_scheduler_py,src_zephyr_infrastructure_auto_fix_engine_import_fixer_py,src_zephyr_infrastructure_auto_fix_engine_interrupt_guard_py,src_zephyr_infrastructure_auto_fix_engine_llm_fix_adapter_py,src_zephyr_infrastructure_auto_fix_engine_models_py,src_zephyr_infrastructure_auto_fix_engine_scaffold_registrar_py,src_zephyr_infrastructure_auto_fix_engine_self_heal_agent_py,src_zephyr_infrastructure_auto_fix_engine_shadow_workspace_py,src_zephyr_infrastructure_auto_fix_engine_state_machine_py,src_zephyr_infrastructure_auto_fix_engine_zombie_cleaner_py,src_zephyr_infrastructure_blueprint_code_sync_py,src_zephyr_infrastructure_budget_enforcement_init_py,src_zephyr_infrastructure_budget_enforcement_rbac_bridge_py,src_zephyr_infrastructure_capacity_assurance_budget_forecaster_py,src_zephyr_infrastructure_capacity_assurance_contracts_batch1_infra_py,src_zephyr_infrastructure_capacity_assurance_contracts_batch3_integration_py,src_zephyr_infrastructure_capacity_assurance_contracts_contract_bus_py,src_zephyr_infrastructure_capacity_assurance_cross_module_integration_py,src_zephyr_infrastructure_capacity_assurance_host_resource_governor_py,src_zephyr_infrastructure_capacity_assurance_kill_switch_py,src_zephyr_infrastructure_capacity_assurance_risk_mitigation_py,src_zephyr_infrastructure_capacity_assurance_schema_py,src_zephyr_infrastructure_capacity_assurance_sli_instrumentation_py,src_zephyr_infrastructure_capacity_assurance_tech_stack_py,src_zephyr_infrastructure_capacity_assurance_token_budget_py,src_zephyr_infrastructure_config_validator_py,src_zephyr_infrastructure_contract_tester_py,src_zephyr_infrastructure_cost_tracker_py,src_zephyr_infrastructure_database_service_py,src_zephyr_infrastructure_dry_run_simulator_py,src_zephyr_infrastructure_event_bus_upgrade_py,src_zephyr_infrastructure_event_store_py,src_zephyr_infrastructure_events_event_store_py,src_zephyr_infrastructure_file_watcher_py,src_zephyr_infrastructure_finding_task_bridge_py,src_zephyr_infrastructure_git_batcher_py,src_zephyr_infrastructure_health_monitor_health_aggregator_py,src_zephyr_infrastructure_hooks_event_hook_py,src_zephyr_infrastructure_impact_impact_propagator_py,src_zephyr_infrastructure_impact_llm_impact_analyzer_py,src_zephyr_infrastructure_infrastructure_base_py,src_zephyr_infrastructure_kill_switch_sim_py,src_zephyr_infrastructure_lifecycle_scope_guard_py,src_zephyr_infrastructure_lifecycle_task_lifecycle_manager_py,src_zephyr_infrastructure_observability_notifier_py,src_zephyr_infrastructure_observability_trace_decorator_py,src_zephyr_infrastructure_pipeline_backpressure_manager_py,src_zephyr_infrastructure_pipeline_backpressure_types_py,src_zephyr_infrastructure_pipeline_circuit_breaker_manager_py,src_zephyr_infrastructure_pipeline_cost_tracker_py,src_zephyr_infrastructure_pipeline_ct_pipe_routing_py,src_zephyr_infrastructure_pipeline_dead_letter_queue_py,src_zephyr_infrastructure_pipeline_llm_gateway_py,src_zephyr_infrastructure_pipeline_model_router_py,src_zephyr_infrastructure_pipeline_models_py,src_zephyr_infrastructure_pipeline_pipeline_agent_bridge_py,src_zephyr_infrastructure_pipeline_pipeline_lock_py,src_zephyr_infrastructure_pipeline_pipeline_roadmap_py,src_zephyr_infrastructure_pipeline_preemption_manager_py,src_zephyr_infrastructure_pipeline_routing_plugins_py,src_zephyr_infrastructure_pydantic_v2_migrator_py,src_zephyr_infrastructure_quality_quality_monitor_py,src_zephyr_infrastructure_queue_task_queue_py,src_zephyr_infrastructure_queue_task_scheduler_py,src_zephyr_infrastructure_reliability_circuit_breaker_py,src_zephyr_infrastructure_reliability_context_guard_py,src_zephyr_infrastructure_runtime_concurrency_guard_py,src_zephyr_infrastructure_runtime_gate_coordinator_py,src_zephyr_infrastructure_runtime_sandbox_enforcer_py,src_zephyr_infrastructure_runtime_startup_shutdown_py,src_zephyr_infrastructure_script_system_finding_py,src_zephyr_infrastructure_script_system_gate_bridge_py,src_zephyr_infrastructure_sla_sla_monitor_py,src_zephyr_infrastructure_system_telemetry_budget_telemetry_bridge_py,src_zephyr_infrastructure_system_telemetry_trace_bridge_py,src_zephyr_infrastructure_system_telemetry_ai_behavior_event_sink_py,src_zephyr_infrastructure_system_telemetry_archive_cold_stub_py,src_zephyr_infrastructure_system_telemetry_auto_bootstrap_py,src_zephyr_infrastructure_system_telemetry_contract_metrics_py,src_zephyr_infrastructure_system_telemetry_facade_py,src_zephyr_infrastructure_system_telemetry_health_aggregator_py,src_zephyr_infrastructure_system_telemetry_health_probes_py,src_zephyr_infrastructure_system_telemetry_logs_init_py,src_zephyr_infrastructure_system_telemetry_logs_structured_sink_py,src_zephyr_infrastructure_system_telemetry_metrics_blueprint_metrics_py,src_zephyr_infrastructure_system_telemetry_metrics_bridge_py,src_zephyr_infrastructure_system_telemetry_traces_span_stub_py,src_zephyr_infrastructure_system_telemetry_watchdog_py,src_zephyr_infrastructure_warm_hot_gate_py,src_zephyr_shared_lifecycle_daemon_registry_py,src_zephyr_shared_lifecycle_hooks_py,src_zephyr_shared_lifecycle_lazy_loader_py,src_zephyr_shared_lifecycle_resource_optimization_models_py,src_zephyr_trading_main_py,src_zephyr_trading_action_dispatcher_py,src_zephyr_trading_ai_audit_logger_py,src_zephyr_trading_auto_integrator_py,src_zephyr_trading_auto_runtime_core_py,src_zephyr_trading_auto_task_generator_py,src_zephyr_trading_boot_hooks_py,src_zephyr_trading_capability_card_py,src_zephyr_trading_capability_registry_py,src_zephyr_trading_capability_sync_py,src_zephyr_trading_dream_cycle_py,src_zephyr_trading_finalizer_py,src_zephyr_trading_health_monitor_py,src_zephyr_trading_integration_registry_py,src_zephyr_trading_lifecycle_manager_py,src_zephyr_trading_module_onboarding_scanner_py,src_zephyr_trading_night_shift_queue_py,src_zephyr_trading_orphan_detector_py,src_zephyr_trading_ports_py,src_zephyr_trading_resource_optimization_py,src_zephyr_trading_runtime_config_py,src_zephyr_trading_staging_area_py,src_zephyr_trading_status_dashboard_py,src_zephyr_trading_stop_gate_py,src_zephyr_trading_task_gate_py,src_zephyr_trading_windows_service_py,src_zephyr_trading_work_dag_py,src_zephyr_trading_work_orchestrator_py,src_zephyr_trading_zombie_scanner_py production
```

### 设计态的图（仅 design_maturity=design 的模块和域内依赖）

> 仅展示蓝图阶段、代码未写的设计态模块（共 1 个），不含跨域外部节点。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    docs_03_modules_cross_layer_agent_orchestrator_blueprint_md["(设计态 / design) 蓝图 / blueprint<br/>蓝图，编排器的功能模块。<br/>文件: agent_orchestrator/blueprint.md"]
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
| 1 | 从 TaskRepository 查询 task 的 sou / boot_hooks (trading/... | → | D_AUTONOMY_CORE 自治核心: 技能freshness扩展 / MOD-INF-019: Agent Spec — Skill Fres... | 导入依赖 / import_depends |
| 2 | 从 TaskRepository 查询 task 的 sou / boot_hooks (trading/... | → | D_AUTONOMY_CORE 自治核心: 技能生命周期 / MOD-INF-019: Agent Spec — Skill Lifecycle... | 导入依赖 / import_depends |
| 3 | DatabaseService: 统一管理数据库的连接池、生命周期、健康检... | → | D_DATA 数据接入层: ClickHouse 连接配置单真源加载器（裁定 #ARCH-CH-017 /  / c... | 导入依赖 / import_depends |
| 4 | AutoRuntimeCore — 三层运行时运营中心（系统大脑） / auto_... | → | D_FEEDBACK_LOOP 反馈循环引擎: 包入口 / Feedback Loop Engine — MOD-FEEDBACK_LOOP. (feed... | 导入依赖 / import_depends |
| 5 | AutoRuntimeCore — 三层运行时运营中心（系统大脑） / auto_... | → | D_FEEDBACK_LOOP 反馈循环引擎: FLE 全链路调度器 —— collect->detect->diagnose- / schedu... | 导入依赖 / import_depends |
| 6 | 生命周期管理器——Boot + Shutdown 序列。 / lifecycle_mana... | → | D_FEEDBACK_LOOP 反馈循环引擎: 包入口 / Feedback Loop Engine — MOD-FEEDBACK_LOOP. (feed... | 导入依赖 / import_depends |
| 7 | AssetDashboard — MOD-INF-026 资产健康仪表盘生成器 / dash... | → | D_GOVERNANCE 生命周期管理: depgraph Schema DDL + 版本化迁移框架 / depgraph_schema (g... | 导入依赖 / import_depends |
| 8 | escalation桥接 / escalation_bridge (auto_fix_engine/escal... | → | D_GOVERNANCE 生命周期管理: Escalation Adapter — MOD-INF-022 统一集成入口. / adapter... | 导入依赖 / import_depends |
| 9 | 预算enforcement.rbacbridge — 基础设施层 R / rbac_bridge ... | → | D_GOVERNANCE 生命周期管理: G-CT-007 契约：Budget -> RBAC 配额限制. / rbac_bridge (ag... | 导入依赖 / import_depends |
| 10 | ContractBus loader — 加载全部44条容量保障契约的Pydan / c... | → | D_GOVERNANCE 生命周期管理: Batch2 治理层契约 — 15条 Pydantic v2 Schema（Pr / batch2... | 导入依赖 / import_depends |
| 11 | DatabaseService: 统一管理数据库的连接池、生命周期、健康检... | → | D_GOVERNANCE 生命周期管理: depgraph Schema DDL + 版本化迁移框架 / depgraph_schema (g... | 导入依赖 / import_depends |
| 12 | DatabaseService: 统一管理数据库的连接池、生命周期、健康检... | → | D_GOVERNANCE 生命周期管理: SQLite 元数据层 Schema DDL + 版本化迁移框架（T-1-02  / sq... | 导入依赖 / import_depends |
| 13 | PreemptionManager -- 优先级抢占管理器 / preemption_manage... | → | D_GOVERNANCE 生命周期管理: TaskRepository — 任务登记表 CRUD + 状态机（T-1-04 / task... | 导入依赖 / import_depends |
| 14 | AutoRuntimeCore — 三层运行时运营中心（系统大脑） / auto_... | → | D_GOVERNANCE 生命周期管理: 模型路由器 / model_router (intelligence_governance/model_... | 导入依赖 / import_depends |
| 15 | AutoRuntimeCore — 三层运行时运营中心（系统大脑） / auto_... | → | D_GOVERNANCE 生命周期管理: TaskRepository — 任务登记表 CRUD + 状态机（T-1-04 / task... | 导入依赖 / import_depends |
| 16 | AutoRuntimeCore — 三层运行时运营中心（系统大脑） / auto_... | → | D_GOVERNANCE 生命周期管理: Escalation Adapter — MOD-INF-022 统一集成入口. / adapter... | 导入依赖 / import_depends |
| 17 | 从 TaskRepository 查询 task 的 sou / boot_hooks (trading/... | → | D_GOVERNANCE 生命周期管理: TaskRepository — 任务登记表 CRUD + 状态机（T-1-04 / task... | 导入依赖 / import_depends |
| 18 | resourceoptimization / resource_optimization.py - MAPE-K ... | → | D_GOVERNANCE 生命周期管理: 容量治理loop / capacity_governance_loop (capacity_governa... | 导入依赖 / import_depends |
| 19 | AssetLifecycle — MOD-INF-026 L5 ITIL生命周期 / lifecycle... | → | D_GOV_AUDIT 审计追踪: 不可变审计写入器——JSONL 追加 + SHA-256 哈 / writer (gov... | 导入依赖 / import_depends |
| 20 | 引擎 / engine (auto_fix_engine/engine.py) | → | D_GOV_AUDIT 审计追踪: 发现模型 / finding_model (gov_audit/finding_model.py) | 导入依赖 / import_depends |
| 21 | resourceoptimization / resource_optimization.py - MAPE-K ... | → | D_GOV_AUDIT 审计追踪: 写入核心审计链——治本（裁定#18 G7 + 5.37.1） / bridge (g... | 导入依赖 / import_depends |
| 22 | 漂移事件记录——对齐 test状态machine. / state_machine (au... | → | D_GOV_DRIFT 漂移检测: Drift Detector 数据模型 — driftmodels.py / drift_models ... | 导入依赖 / import_depends |
| 23 | 契约指标 / ZephyrAlpha — system-telemetry/contract_metri... | → | D_GOV_DRIFT 漂移检测: 契约漂移detector — 契约漂移检测器。 / contract_drift_det... | 导入依赖 / import_depends |
| 24 | 生命周期管理器——Boot + Shutdown 序列。 / lifecycle_mana... | → | D_GOV_DRIFT 漂移检测: 自监控 / self_monitor (gov_audit/self_monitor.py) | 导入依赖 / import_depends |
| 25 | 自动bootstrap — 全自动遥测注入钩子（MOD-INF-015 v / auto... | → | D_GOV_OPS_RESILIENCE 运维弹性治理: Phase Manager — ZephyrAlpha 施工阶段门控引擎. / phase_ma... | 导入依赖 / import_depends |
| 26 | AutoRuntimeCore — 三层运行时运营中心（系统大脑） / auto_... | → | D_GOV_OPS_RESILIENCE 运维弹性治理: Coldstart Manager — v0.7.0 冷启动管理器: escal / coldsta... | 导入依赖 / import_depends |
| 27 | 从 TaskRepository 查询 task 的 sou / boot_hooks (trading/... | → | D_GOV_OPS_RESILIENCE 运维弹性治理: F5BootIntegration — F5 自动启动/关闭集成 (MOD-IN / f5_bo... | 导入依赖 / import_depends |
| 28 | 从 TaskRepository 查询 task 的 sou / boot_hooks (trading/... | → | D_GOV_OPS_RESILIENCE 运维弹性治理: F5ShutdownManager — F5 自动关闭/状态持久化/信号处理 ( / ... | 导入依赖 / import_depends |
| 29 | 预算enforcement 包聚合层。 / __init__ (budget_enforcement... | → | D_GOV_REPAIR 治理修复: 延迟导入 BudgetEngine 避免循环依赖. / budget_enforcement ... | 导入依赖 / import_depends |
| 30 | Task Lifecycle Manager — G0-G7 任务生命周期门禁。 / task... | → | D_GOV_RULE 规则治理: 任务类型定义 / Task Types (rule_enforcement/task_types.py) | 导入依赖 / import_depends |
| 31 | AutoRuntimeCore — 三层运行时运营中心（系统大脑） / auto_... | → | D_GOV_RULE 规则治理: 三方对齐门禁 / Triple Alignment (rule_enforcement/triple_... | 导入依赖 / import_depends |
| 32 | 从 TaskRepository 查询 task 的 sou / boot_hooks (trading/... | → | D_GOV_RULE 规则治理: 三方对齐门禁 / Triple Alignment (rule_enforcement/triple_... | 导入依赖 / import_depends |
| 33 | 工作编排子系统——决定什么工作、什么时候、用什么模型、什... | → | D_GOV_RULE 规则治理: 任务类型定义 / Task Types (rule_enforcement/task_types.py) | 导入依赖 / import_depends |
| 34 | HealthMonitor — 健康监控 + 自愈 / health_monitor (tradin... | → | D_INFRASTRUCTURE 跨层契约基础设施: 遥测emitter / telemetry_emitter (contracts/telemetry_emit... | 导入依赖 / import_depends |
| 35 | AutoRuntimeCore — 三层运行时运营中心（系统大脑） / auto_... | → | D_INFRA_A2A A2A通信: A2A Card Registry — 全局 Agent Card 注册单例 / a2a_card_... | 导入依赖 / import_depends |
| 36 | AutoRuntimeCore — 三层运行时运营中心（系统大脑） / auto_... | → | D_INFRA_A2A A2A通信: A2A 协议网关 — Agent 间请求分发与协议转换 / a2a_protocol... | 导入依赖 / import_depends |
| 37 | 能力同步 / capability_sync (trading/capability_sync.py) | → | D_INFRA_A2A A2A通信: A2A Registry — Agent Card 注册与发现 / a2a_registry (lay... | 导入依赖 / import_depends |
| 38 | 从 TaskRepository 查询 task 的 sou / boot_hooks (trading/... | → | D_INFRA_RECOVERY 回滚恢复: RollbackBootIntegration — 回滚系统自动启动/关闭集成  / r... | 导入依赖 / import_depends |
| 39 | DEPRECATED: 此文件已废弃。 / event_bus_upgrade (infrastru... | → | D_INTEGRATION 管线路由: EventBus 升级策略引擎 / upgrade_strategy (events/upgrade_... | 导入依赖 / import_depends |
| 40 | AutoRuntimeCore — 三层运行时运营中心（系统大脑） / auto_... | → | D_INTEGRATION 管线路由: EmbeddingRouter — MOD-INF-011 双嵌入维度路由 / embedding... | 导入依赖 / import_depends |
| 41 | AutoRuntimeCore — 三层运行时运营中心（系统大脑） / auto_... | → | D_INTEGRATION 管线路由: LocalModelScheduler — L2 本地模型 24/7 调度循环 / local_... | 导入依赖 / import_depends |
| 42 | AutoRuntimeCore — 三层运行时运营中心（系统大脑） / auto_... | → | D_INTEGRATION 管线路由: OllamaChat — 通过 Ollama HTTP API 进行本地 LLM / ollama_... | 导入依赖 / import_depends |
| 43 | AutoRuntimeCore — 三层运行时运营中心（系统大脑） / auto_... | → | D_INTEGRATION 管线路由: PipelineOrchestrator — M1-M11 管线协调器 / pipeline_orch... | 导入依赖 / import_depends |
| 44 | AutoRuntimeCore — 三层运行时运营中心（系统大脑） / auto_... | → | D_INTEGRATION 管线路由: InProcessVectorMemory — MOD-INF-011 VMS  / in_process_ve... | 导入依赖 / import_depends |
| 45 | AutoTaskGenerator — 自动任务生成器 / auto_task_generator... | → | D_INTEGRATION 管线路由: LocalModelScheduler — L2 本地模型 24/7 调度循环 / local_... | 导入依赖 / import_depends |
| 46 | 启动前配置完整性校验（5.71.1 治本）——必填字段/类型 / ru... | → | D_INTEGRATION 管线路由: 运行时类型定义 / runtime_types (contracts/runtime_types.py) | 导入依赖 / import_depends |
| 47 | AutoRuntimeCore — 三层运行时运营中心（系统大脑） / auto_... | → | D_INTELLIGENCE 上下文管理: Results Writer — 持久化 benchmark 结果，支持历史对比 / r... | 导入依赖 / import_depends |
| 48 | AutoRuntimeCore — 三层运行时运营中心（系统大脑） / auto_... | → | D_INTELLIGENCE 上下文管理: ModelTaskMatrix — 任务×模型性能学习引擎 / task_model_le... | 导入依赖 / import_depends |
| 49 | TaskGate --- 任务门控 / task_gate (trading/task_gate.py) | → | D_INTELLIGENCE 上下文管理: CapabilityPassport --- AI 模型能力护照 / capability_passp... | 导入依赖 / import_depends |
| 50 | 从 TaskRepository 查询 task 的 sou / boot_hooks (trading/... | → | D_OPS 反馈循环: 预算引擎 / Budget Enforcer core engine — MOD-INF-024 (op... | 导入依赖 / import_depends |
| 51 | 从 TaskRepository 查询 task 的 sou / boot_hooks (trading/... | → | D_ORCHESTRATOR 代理编排器: Orc->VMS 记忆写入器 / memory_writer (execution/memory_wri... | 导入依赖 / import_depends |
| 52 | AutoRuntimeCore — 三层运行时运营中心（系统大脑） / auto_... | → | D_SECURITY 对抗验证: GenesisBootstrap — RBAC系统启动引导器. / genesis_bootstr... | 导入依赖 / import_depends |
| 53 | 从 TaskRepository 查询 task 的 sou / boot_hooks (trading/... | → | D_SECURITY 对抗验证: GenesisBootstrap — RBAC系统启动引导器. / genesis_bootstr... | 导入依赖 / import_depends |
| 54 | 从 TaskRepository 查询 task 的 sou / boot_hooks (trading/... | → | D_SECURITY 对抗验证: KillSwitch — 熔断器. / kill_switch (access_control/kill_... | 导入依赖 / import_depends |
| 55 | 从 TaskRepository 查询 task 的 sou / boot_hooks (trading/... | → | D_SECURITY 对抗验证: NonRepudiation — 不可抵赖性审计签名. / non_repudiation (... | 导入依赖 / import_depends |
| 56 | 从 TaskRepository 查询 task 的 sou / boot_hooks (trading/... | → | D_SECURITY 对抗验证: CommitTrigger — 事件驱动红蓝对抗触发器 (MOD-INF-030 / co... | 导入依赖 / import_depends |
| 57 | Asset Inventory CLI — MOD-INF-026 蓝图 §31 / __main__ (... | → | D_SHARED 共享服务: 进程池 / process_pool.py - Shared process pool for MCP se... | 导入依赖 / import_depends |
| 58 | Asset Inventory CLI — MOD-INF-026 蓝图 §31 / __main__ (... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 59 | Asset Inventory CLI — MOD-INF-026 蓝图 §31 / __main__ (... | → | D_SHARED 共享服务: serialization.py —— 统一序列化/反序列化基础设施（Phase ... | 导入依赖 / import_depends |
| 60 | AssetClassifier — MOD-INF-026 L2 资产自动分类器 / classi... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 61 | AssetDashboard — MOD-INF-026 资产健康仪表盘生成器 / dash... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 62 | UnifiedAssetIndex — MOD-INF-026 L3 统一资产索 / index_ge... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 63 | AssetLifecycle — MOD-INF-026 L5 ITIL生命周期 / lifecycle... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 64 | AssetInventory MCP Server — MOD-INF-026  / mcp_server (a... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 65 | 多 IDE 规则文件生成器——从 asset-invento / metadata (ass... | → | D_SHARED 共享服务: 进程池 / process_pool.py - Shared process pool for MCP se... | 导入依赖 / import_depends |
| 66 | ReconciliationEngine — MOD-INF-026 L4 注册 / reconciler ... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 67 | MOD-INF-026 §17 — 24 个异构注册表统一解析适配器。 / reg... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 68 | MOD-INF-026 §17 — 24 个异构注册表统一解析适配器。 / reg... | → | D_SHARED 共享服务: SQLite 连接工厂真源（SSoT） / sqlite_factory (io/sqlite_f... | 导入依赖 / import_depends |
| 69 | AssetDiscoveryScanner — MOD-INF-026 L1 全 / scanner (ass... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 70 | AssetInventoryTelemetry — MOD-INF-026 自监 / telemetry (... | → | D_SHARED 共享服务: secrets.py —— Secrets 管理抽象（Phase 7 新增 |  / secre... | 导入依赖 / import_depends |
| 71 | 旁路状态——对标 K8s Admission Webhook / trust_anchor (as... | → | D_SHARED 共享服务: 进程池 / process_pool.py - Shared process pool for MCP se... | 导入依赖 / import_depends |
| 72 | 旁路状态——对标 K8s Admission Webhook / trust_anchor (as... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 73 | alignmentsyncer / alignment_syncer (auto_fix_engine/align... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 74 | allcompleter / all_completer (auto_fix_engine/all_complet... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 75 | 合规审计器 / compliance_auditor (auto_fix_engine/complian... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 76 | 合规审计器 / compliance_auditor (auto_fix_engine/complian... | → | D_SHARED 共享服务: SQLite 连接工厂真源（SSoT） / sqlite_factory (io/sqlite_f... | 导入依赖 / import_depends |
| 77 | 配置修复器 / config_fixer (auto_fix_engine/config_fixer.py) | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 78 | 去重extractor / dedup_extractor (auto_fix_engine/dedup_ex... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 79 | dep版本修复器 / dep_version_fixer (auto_fix_engine/dep_ve... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 80 | 漂移修复器 / drift_fixer (auto_fix_engine/drift_fixer.py) | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 81 | 订阅 EventBusBackpressure 的 drif / event_hooks (auto_fix... | → | D_SHARED 共享服务: EventBus — 事件总线（带背压控制）(M-07) / event_bus (sha... | 导入依赖 / import_depends |
| 82 | 修复预算 / fix_budget (auto_fix_engine/fix_budget.py) | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 83 | 修复预算 / fix_budget (auto_fix_engine/fix_budget.py) | → | D_SHARED 共享服务: SQLite 连接工厂真源（SSoT） / sqlite_factory (io/sqlite_f... | 导入依赖 / import_depends |
| 84 | 修复健康检查 / fix_health_check (auto_fix_engine/fix_heal... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 85 | 修复健康检查 / fix_health_check (auto_fix_engine/fix_heal... | → | D_SHARED 共享服务: SQLite 连接工厂真源（SSoT） / sqlite_factory (io/sqlite_f... | 导入依赖 / import_depends |
| 86 | 修复模式miner / fix_pattern_miner (auto_fix_engine/fix_pa... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 87 | 修复模式miner / fix_pattern_miner (auto_fix_engine/fix_pa... | → | D_SHARED 共享服务: SQLite 连接工厂真源（SSoT） / sqlite_factory (io/sqlite_f... | 导入依赖 / import_depends |
| 88 | 修复可靠性 / fix_reliability (auto_fix_engine/fix_reliabi... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 89 | 修复可靠性 / fix_reliability (auto_fix_engine/fix_reliabi... | → | D_SHARED 共享服务: SQLite 连接工厂真源（SSoT） / sqlite_factory (io/sqlite_f... | 导入依赖 / import_depends |
| 90 | 修复安全 / fix_safety (auto_fix_engine/fix_safety.py) | → | D_SHARED 共享服务: 进程池 / process_pool.py - Shared process pool for MCP se... | 导入依赖 / import_depends |
| 91 | 修复安全 / fix_safety (auto_fix_engine/fix_safety.py) | → | D_SHARED 共享服务: 文件utils.py —— 安全文件操作工具（Phase 3 新增 | 盲 / f... | 导入依赖 / import_depends |
| 92 | 导入修复器 / import_fixer (auto_fix_engine/import_fixer.py) | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 93 | 中断守卫 / interrupt_guard (auto_fix_engine/interrupt_gua... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 94 | llm修复适配器 / llm_fix_adapter (auto_fix_engine/llm_fix_... | → | D_SHARED 共享服务: LLMGatewayProtocol — LLM 网关抽象接口 / llm_gateway_prot... | 导入依赖 / import_depends |
| 95 | 从 script-manifest.yaml 加载已注册脚本 / scaffold_registr... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 96 | shadowworkspace / shadow_workspace (auto_fix_engine/shado... | → | D_SHARED 共享服务: 进程池 / process_pool.py - Shared process pool for MCP se... | 导入依赖 / import_depends |
| 97 | shadowworkspace / shadow_workspace (auto_fix_engine/shado... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 98 | 移除 content 中指向不存在文件的僵尸引用，返回清理后 / zom... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 99 | Risk mitigation — R1~R16 全量风险缓解实现（对标蓝图 § /... | → | D_SHARED 共享服务: SQLite 连接工厂真源（SSoT） / sqlite_factory (io/sqlite_f... | 导入依赖 / import_depends |
| 100 | SchemaManager — 容量保障体系数据库 Schema 管理器 / schem... | → | D_SHARED 共享服务: SQLite 连接工厂真源（SSoT） / sqlite_factory (io/sqlite_f... | 导入依赖 / import_depends |
| 101 | RI-15 CostTracker — 成本追踪器 / cost_tracker (infrastru... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 102 | RI-15 CostTracker — 成本追踪器 / cost_tracker (infrastru... | → | D_SHARED 共享服务: SQLite 连接工厂真源（SSoT） / sqlite_factory (io/sqlite_f... | 导入依赖 / import_depends |
| 103 | DatabaseService: 统一管理数据库的连接池、生命周期、健康检... | → | D_SHARED 共享服务: DatabaseCRUDMixin: 共享的 governance.db + d / database_cr... | 导入依赖 / import_depends |
| 104 | DatabaseService: 统一管理数据库的连接池、生命周期、健康检... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 105 | DEPRECATED: 此文件已废弃。 / event_bus_upgrade (infrastru... | → | D_SHARED 共享服务: EventBus 升级策略引擎 / upgrade_strategy (events/upgrade_... | 导入依赖 / import_depends |
| 106 | RI-13 EventStore — 事件存储 / event_store (infrastructur... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 107 | RI-13 EventStore — 事件存储 / event_store (infrastructur... | → | D_SHARED 共享服务: SQLite 连接工厂真源（SSoT） / sqlite_factory (io/sqlite_f... | 导入依赖 / import_depends |
| 108 | RI-13 EventStore — 事件存储 / event_store (infrastructur... | → | D_SHARED 共享服务: 时间utils.py —— 时间/日期工具（Phase 9 新增 | 盲点 / ti... | 导入依赖 / import_depends |
| 109 | Event Store — 事件持久化存储。 / event_store (events/eve... | → | D_SHARED 共享服务: EventBus — 事件总线（带背压控制）(M-07) / event_bus (sha... | 导入依赖 / import_depends |
| 110 | Event Store — 事件持久化存储。 / event_store (events/eve... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 111 | 文件watcher / file_watcher (infrastructure/file_watcher.py) | → | D_SHARED 共享服务: ZephyrAlpha 蓝图拆解器 / blueprint_decomposer (blueprint_... | 导入依赖 / import_depends |
| 112 | 文件watcher / file_watcher (infrastructure/file_watcher.py) | → | D_SHARED 共享服务: EventBus — 事件总线（带背压控制）(M-07) / event_bus (sha... | 导入依赖 / import_depends |
| 113 | 文件watcher / file_watcher (infrastructure/file_watcher.py) | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 114 | 文件watcher / file_watcher (infrastructure/file_watcher.py) | → | D_SHARED 共享服务: registry — 运行时 DI 容器 / registry (protocols/registry.py) | 导入依赖 / import_depends |
| 115 | Finding->TaskCard 桥接器 / finding_task_bridge (infrastru... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 116 | Finding->TaskCard 桥接器 / finding_task_bridge (infrastru... | → | D_SHARED 共享服务: registry — 运行时 DI 容器 / registry (protocols/registry.py) | 导入依赖 / import_depends |
| 117 | Finding->TaskCard 桥接器 / finding_task_bridge (infrastru... | → | D_SHARED 共享服务: 模式 / schemas (schema/schemas.py) | 导入依赖 / import_depends |
| 118 | Finding->TaskCard 桥接器 / finding_task_bridge (infrastru... | → | D_SHARED 共享服务: 任务types — 任务系统核心类型 re-export 层 / task_types (... | 导入依赖 / import_depends |
| 119 | gitbatcher.py — Git 命令批量化工具（ARCH-GIT-CA / git_ba... | → | D_SHARED 共享服务: 进程池 / process_pool.py - Shared process pool for MCP se... | 导入依赖 / import_depends |
| 120 | 终止开关仿真 / Kill Switch T0 Hardware Simulator (infrast... | → | D_SHARED 共享服务: 时间utils.py —— 时间/日期工具（Phase 9 新增 | 盲点 / ti... | 导入依赖 / import_depends |
| 121 | Notifier — 多渠道 Owner 通知。 / notifier (observability... | → | D_SHARED 共享服务: EventBus — 事件总线（带背压控制）(M-07) / event_bus (sha... | 导入依赖 / import_depends |
| 122 | Notifier — 多渠道 Owner 通知。 / notifier (observability... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 123 | 追踪装饰器 / trace_decorator (observability/trace_decorat... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 124 | backpressure类型定义 / backpressure_types.py - Pipeline b... | → | D_SHARED 共享服务: 追踪上下文 / trace_context (core/trace_context.py) | 导入依赖 / import_depends |
| 125 | CT-PIPE-ORC-001 — TaskCard -> 管线入口节点路由 / ct_pipe... | → | D_SHARED 共享服务: ZephyrAlpha 任务系统核心数据模型 / models (foundation/mod... | 导入依赖 / import_depends |
| 126 | CT-PIPE-ORC-001 — TaskCard -> 管线入口节点路由 / ct_pipe... | → | D_SHARED 共享服务: yamlutils.py — vocabulary YAML 加载公共工具（S / yaml_ut... | 导入依赖 / import_depends |
| 127 | CT-PIPE-ORC-001 — TaskCard -> 管线入口节点路由 / ct_pipe... | → | D_SHARED 共享服务: 模式 / schemas (schema/schemas.py) | 导入依赖 / import_depends |
| 128 | llm网关 / MOD-INF-019: Agent Spec — LLM Gateway (pipelin... | → | D_SHARED 共享服务: constants.py —— 共享枚举 & 常量集中 re-export（Si / con... | 导入依赖 / import_depends |
| 129 | llm网关 / MOD-INF-019: Agent Spec — LLM Gateway (pipelin... | → | D_SHARED 共享服务: 仅在 dev 环境下为 True——生产环境永远 False / env (found... | 导入依赖 / import_depends |
| 130 | llm网关 / MOD-INF-019: Agent Spec — LLM Gateway (pipelin... | → | D_SHARED 共享服务: secrets.py —— Secrets 管理抽象（Phase 7 新增 |  / secre... | 导入依赖 / import_depends |
| 131 | llm网关 / MOD-INF-019: Agent Spec — LLM Gateway (pipelin... | → | D_SHARED 共享服务: 异步utils.py — async/sync 边界桥接（5.12.8  / async_util... | 导入依赖 / import_depends |
| 132 | ModelRouter — 模型路由与降级链管理 / model_router (pipel... | → | D_SHARED 共享服务: ZephyrAlpha 任务系统核心数据模型 / models (foundation/mod... | 导入依赖 / import_depends |
| 133 | Pipeline 数据模型 / models (pipeline/models.py) | → | D_SHARED 共享服务: 模式 / schemas (schema/schemas.py) | 导入依赖 / import_depends |
| 134 | Pipeline 数据模型 / models (pipeline/models.py) | → | D_SHARED 共享服务: 时间utils.py —— 时间/日期工具（Phase 9 新增 | 盲点 / ti... | 导入依赖 / import_depends |
| 135 | Pipeline Lock — 双管线并发锁 / pipeline_lock (pipeline/p... | → | D_SHARED 共享服务: lock.py —— 分布式锁抽象（Phase 10 新增 | 盲点 B23 修 / ... | 导入依赖 / import_depends |
| 136 | PreemptionManager -- 优先级抢占管理器 / preemption_manage... | → | D_SHARED 共享服务: serialization.py —— 统一序列化/反序列化基础设施（Phase ... | 导入依赖 / import_depends |
| 137 | PreemptionManager -- 优先级抢占管理器 / preemption_manage... | → | D_SHARED 共享服务: 任务types — 任务系统核心类型 re-export 层 / task_types (... | 导入依赖 / import_depends |
| 138 | PreemptionManager -- 优先级抢占管理器 / preemption_manage... | → | D_SHARED 共享服务: 时间utils.py —— 时间/日期工具（Phase 9 新增 | 盲点 / ti... | 导入依赖 / import_depends |
| 139 | Pipeline Routing Plugin System — K8s Sch / routing_plugi... | → | D_SHARED 共享服务: yamlutils.py — vocabulary YAML 加载公共工具（S / yaml_ut... | 导入依赖 / import_depends |
| 140 | Task Queue — 后台任务队列 + 自动 Dispatch。 / task_queue... | → | D_SHARED 共享服务: EventBus — 事件总线（带背压控制）(M-07) / event_bus (sha... | 导入依赖 / import_depends |
| 141 | Task Queue — 后台任务队列 + 自动 Dispatch。 / task_queue... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 142 | Task Scheduler — 任务调度器。 / task_scheduler (queue/ta... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 143 | Finding Schema — 审计发现标准化数据模型 / finding (scrip... | → | D_SHARED 共享服务: 模式 / schemas (schema/schemas.py) | 导入依赖 / import_depends |
| 144 | SLA Monitor — 服务等级协议 (SLA) 监控 RTO/RPO。 / sla_mo... | → | D_SHARED 共享服务: EventBus — 事件总线（带背压控制）(M-07) / event_bus (sha... | 导入依赖 / import_depends |
| 145 | SLA Monitor — 服务等级协议 (SLA) 监控 RTO/RPO。 / sla_mo... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 146 | 遥测 · archive/coldstub — 冷存储归档管道。 / cold_stub ... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 147 | 自动bootstrap — 全自动遥测注入钩子（MOD-INF-015 v / auto... | → | D_SHARED 共享服务: serialization.py —— 统一序列化/反序列化基础设施（Phase ... | 导入依赖 / import_depends |
| 148 | 自动bootstrap — 全自动遥测注入钩子（MOD-INF-015 v / auto... | → | D_SHARED 共享服务: SessionContinuity — Session 交接包自动生成与恢复 / sessi... | 导入依赖 / import_depends |
| 149 | Telemetry — 系统遥测门面类（MOD-INF-015 v2.1.0） / facad... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 150 | Telemetry — 系统遥测门面类（MOD-INF-015 v2.1.0） / facad... | → | D_SHARED 共享服务: serialization.py —— 统一序列化/反序列化基础设施（Phase ... | 导入依赖 / import_depends |
| 151 | 健康聚合器（Health Aggregator） / health_aggregator (syst... | → | D_SHARED 共享服务: EventBus — 事件总线（带背压控制）(M-07) / event_bus (sha... | 导入依赖 / import_depends |
| 152 | 三态健康探针协议（Health Probes — CT-HEALTH-001） / heal... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 153 | 蓝图metrics — 蓝图使用追踪 instrumentati / blueprint_met... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 154 | TELE->FLE 指标桥接 — emitmetrics() 生产者 / metrics_brid... | → | D_SHARED 共享服务: registry — 运行时 DI 容器 / registry (protocols/registry.py) | 导入依赖 / import_depends |
| 155 | 遥测 · traces/spanstub — W3C TraceContext / span_stub (... | → | D_SHARED 共享服务: logging.py —— ZephyrAlpha 结构化日志系统（Struct / logg... | 导入依赖 / import_depends |
| 156 | 三冗余 Watchdog（CT-WATCHDOG-001）——互检+Panic  / watch... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 157 | ActionDispatcher --- 大脑的"手" v2.0 (Phase  / action_dis... | → | D_SHARED 共享服务: 进程池 / process_pool.py - Shared process pool for MCP se... | 导入依赖 / import_depends |
| 158 | ActionDispatcher --- 大脑的"手" v2.0 (Phase  / action_dis... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 159 | ActionDispatcher --- 大脑的"手" v2.0 (Phase  / action_dis... | → | D_SHARED 共享服务: serialization.py —— 统一序列化/反序列化基础设施（Phase ... | 导入依赖 / import_depends |
| 160 | ActionDispatcher --- 大脑的"手" v2.0 (Phase  / action_dis... | → | D_SHARED 共享服务: 任务types — 任务系统核心类型 re-export 层 / task_types (... | 导入依赖 / import_depends |
| 161 | AiAuditLogger — AI 行为审计日志 / ai_audit_logger (tradi... | → | D_SHARED 共享服务: serialization.py —— 统一序列化/反序列化基础设施（Phase ... | 导入依赖 / import_depends |
| 162 | AiAuditLogger — AI 行为审计日志 / ai_audit_logger (tradi... | → | D_SHARED 共享服务: 模式 / schemas (schema/schemas.py) | 导入依赖 / import_depends |
| 163 | AiAuditLogger — AI 行为审计日志 / ai_audit_logger (tradi... | → | D_SHARED 共享服务: 时间utils.py —— 时间/日期工具（Phase 9 新增 | 盲点 / ti... | 导入依赖 / import_depends |
| 164 | AutoIntegrator — 自动接入器 / auto_integrator (trading/a... | → | D_SHARED 共享服务: 时间utils.py —— 时间/日期工具（Phase 9 新增 | 盲点 / ti... | 导入依赖 / import_depends |
| 165 | AutoRuntimeCore — 三层运行时运营中心（系统大脑） / auto_... | → | D_SHARED 共享服务: systemconfiguration / system_configuration (core/system_c... | 导入依赖 / import_depends |
| 166 | AutoRuntimeCore — 三层运行时运营中心（系统大脑） / auto_... | → | D_SHARED 共享服务: TaskRepositoryProtocol — TaskRepository  / task_reposito... | 导入依赖 / import_depends |
| 167 | AutoRuntimeCore — 三层运行时运营中心（系统大脑） / auto_... | → | D_SHARED 共享服务: EventBus — 事件总线（带背压控制）(M-07) / event_bus (sha... | 导入依赖 / import_depends |
| 168 | AutoRuntimeCore — 三层运行时运营中心（系统大脑） / auto_... | → | D_SHARED 共享服务: constants.py —— 共享枚举 & 常量集中 re-export（Si / con... | 导入依赖 / import_depends |
| 169 | AutoRuntimeCore — 三层运行时运营中心（系统大脑） / auto_... | → | D_SHARED 共享服务: 进程池 / process_pool.py - Shared process pool for MCP se... | 导入依赖 / import_depends |
| 170 | AutoRuntimeCore — 三层运行时运营中心（系统大脑） / auto_... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 171 | AutoRuntimeCore — 三层运行时运营中心（系统大脑） / auto_... | → | D_SHARED 共享服务: A2A注册表 / A2A Registry and Agent Card contracts — disc... | 导入依赖 / import_depends |
| 172 | AutoTaskGenerator — 自动任务生成器 / auto_task_generator... | → | D_SHARED 共享服务: EventBus — 事件总线（带背压控制）(M-07) / event_bus (sha... | 导入依赖 / import_depends |
| 173 | AutoTaskGenerator — 自动任务生成器 / auto_task_generator... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 174 | 从 TaskRepository 查询 task 的 sou / boot_hooks (trading/... | → | D_SHARED 共享服务: TaskRepositoryProtocol — TaskRepository  / task_reposito... | 导入依赖 / import_depends |
| 175 | 从 TaskRepository 查询 task 的 sou / boot_hooks (trading/... | → | D_SHARED 共享服务: EventBus — 事件总线（带背压控制）(M-07) / event_bus (sha... | 导入依赖 / import_depends |
| 176 | 从 TaskRepository 查询 task 的 sou / boot_hooks (trading/... | → | D_SHARED 共享服务: constants.py —— 共享枚举 & 常量集中 re-export（Si / con... | 导入依赖 / import_depends |
| 177 | 从 TaskRepository 查询 task 的 sou / boot_hooks (trading/... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 178 | 从 TaskRepository 查询 task 的 sou / boot_hooks (trading/... | → | D_SHARED 共享服务: health.py —— ZephyrAlpha 聚合健康检查 / health (lifecyc... | 导入依赖 / import_depends |
| 179 | 从 TaskRepository 查询 task 的 sou / boot_hooks (trading/... | → | D_SHARED 共享服务: 健康discovery / CT-HEALTH-001: System-wide Health Discove... | 导入依赖 / import_depends |
| 180 | 从 TaskRepository 查询 task 的 sou / boot_hooks (trading/... | → | D_SHARED 共享服务: healthcheck服务 / healthcheck_service (lifecycle/healthch... | 导入依赖 / import_depends |
| 181 | 从 TaskRepository 查询 task 的 sou / boot_hooks (trading/... | → | D_SHARED 共享服务: longevity监控 / longevity_monitor (lifecycle/longevity_mo... | 导入依赖 / import_depends |
| 182 | 从 TaskRepository 查询 task 的 sou / boot_hooks (trading/... | → | D_SHARED 共享服务: Autonomy Monitor — AI 自主等级监控与降级。 / autonomy_mo... | 导入依赖 / import_depends |
| 183 | 从 TaskRepository 查询 task 的 sou / boot_hooks (trading/... | → | D_SHARED 共享服务: metrics.py —— 轻量级 Metrics 收集基础设施（Phase 9 / me... | 导入依赖 / import_depends |
| 184 | CapabilityCard — 能力卡片数据模型 / capability_card (tra... | → | D_SHARED 共享服务: 模式 / schemas (schema/schemas.py) | 导入依赖 / import_depends |
| 185 | CapabilityCard — 能力卡片数据模型 / capability_card (tra... | → | D_SHARED 共享服务: 时间utils.py —— 时间/日期工具（Phase 9 新增 | 盲点 / ti... | 导入依赖 / import_depends |
| 186 | CapabilityRegistry — 能力注册中心 / capability_registry ... | → | D_SHARED 共享服务: serialization.py —— 统一序列化/反序列化基础设施（Phase ... | 导入依赖 / import_depends |
| 187 | DreamCycle — 知识固化引擎 / dream_cycle (trading/dream_c... | → | D_SHARED 共享服务: 模式 / schemas (schema/schemas.py) | 导入依赖 / import_depends |
| 188 | DreamCycle — 知识固化引擎 / dream_cycle (trading/dream_c... | → | D_SHARED 共享服务: 时间utils.py —— 时间/日期工具（Phase 9 新增 | 盲点 / ti... | 导入依赖 / import_depends |
| 189 | Finalizer — 优雅清理器 / finalizer (trading/finalizer.py) | → | D_SHARED 共享服务: health.py —— ZephyrAlpha 聚合健康检查 / health (lifecyc... | 导入依赖 / import_depends |
| 190 | Finalizer — 优雅清理器 / finalizer (trading/finalizer.py) | → | D_SHARED 共享服务: metrics.py —— 轻量级 Metrics 收集基础设施（Phase 9 / me... | 导入依赖 / import_depends |
| 191 | HealthMonitor — 健康监控 + 自愈 / health_monitor (tradin... | → | D_SHARED 共享服务: EventBus — 事件总线（带背压控制）(M-07) / event_bus (sha... | 导入依赖 / import_depends |
| 192 | HealthMonitor — 健康监控 + 自愈 / health_monitor (tradin... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 193 | HealthMonitor — 健康监控 + 自愈 / health_monitor (tradin... | → | D_SHARED 共享服务: healthcheck服务 / healthcheck_service (lifecycle/healthch... | 导入依赖 / import_depends |
| 194 | HealthMonitor — 健康监控 + 自愈 / health_monitor (tradin... | → | D_SHARED 共享服务: longevity监控 / longevity_monitor (lifecycle/longevity_mo... | 导入依赖 / import_depends |
| 195 | HealthMonitor — 健康监控 + 自愈 / health_monitor (tradin... | → | D_SHARED 共享服务: metrics.py —— 轻量级 Metrics 收集基础设施（Phase 9 / me... | 导入依赖 / import_depends |
| 196 | HealthMonitor — 健康监控 + 自愈 / health_monitor (tradin... | → | D_SHARED 共享服务: 模式 / schemas (schema/schemas.py) | 导入依赖 / import_depends |
| 197 | HealthMonitor — 健康监控 + 自愈 / health_monitor (tradin... | → | D_SHARED 共享服务: 时间utils.py —— 时间/日期工具（Phase 9 新增 | 盲点 / ti... | 导入依赖 / import_depends |
| 198 | IntegrationRegistry — 集成注册表 / integration_registry ... | → | D_SHARED 共享服务: 模式 / schemas (schema/schemas.py) | 导入依赖 / import_depends |
| 199 | 生命周期管理器——Boot + Shutdown 序列。 / lifecycle_mana... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 200 | NightShiftQueue — 夜班登记表持久化 / night_shift_queue (... | → | D_SHARED 共享服务: serialization.py —— 统一序列化/反序列化基础设施（Phase ... | 导入依赖 / import_depends |
| 201 | NightShiftQueue — 夜班登记表持久化 / night_shift_queue (... | → | D_SHARED 共享服务: 模式 / schemas (schema/schemas.py) | 导入依赖 / import_depends |
| 202 | NightShiftQueue — 夜班登记表持久化 / night_shift_queue (... | → | D_SHARED 共享服务: 时间utils.py —— 时间/日期工具（Phase 9 新增 | 盲点 / ti... | 导入依赖 / import_depends |
| 203 | ports / Protocol-based interface layer for runtime->pipel... | → | D_SHARED 共享服务: 任务types — 任务系统核心类型 re-export 层 / task_types (... | 导入依赖 / import_depends |
| 204 | resourceoptimization / resource_optimization.py - MAPE-K ... | → | D_SHARED 共享服务: 容量calibrator / capacity_calibrator (capacity_governance... | 导入依赖 / import_depends |
| 205 | resourceoptimization / resource_optimization.py - MAPE-K ... | → | D_SHARED 共享服务: 容量digitaltwin / capacity_digital_twin (capacity_governa... | 导入依赖 / import_depends |
| 206 | resourceoptimization / resource_optimization.py - MAPE-K ... | → | D_SHARED 共享服务: 容量fingerprint / capacity_fingerprint (capacity_governan... | 导入依赖 / import_depends |
| 207 | resourceoptimization / resource_optimization.py - MAPE-K ... | → | D_SHARED 共享服务: 容量runbook生成器 / capacity_runbook_generator (capacity_... | 导入依赖 / import_depends |
| 208 | resourceoptimization / resource_optimization.py - MAPE-K ... | → | D_SHARED 共享服务: 模型容量probe / model_capacity_probe (capacity_governance... | 导入依赖 / import_depends |
| 209 | resourceoptimization / resource_optimization.py - MAPE-K ... | → | D_SHARED 共享服务: EventBus — 事件总线（带背压控制）(M-07) / event_bus (sha... | 导入依赖 / import_depends |
| 210 | resourceoptimization / resource_optimization.py - MAPE-K ... | → | D_SHARED 共享服务: 进程池 / process_pool.py - Shared process pool for MCP se... | 导入依赖 / import_depends |
| 211 | resourceoptimization / resource_optimization.py - MAPE-K ... | → | D_SHARED 共享服务: io缓存 / io_cache.py - File-level I/O cache with LRU evic... | 导入依赖 / import_depends |
| 212 | StagingArea — 多AI并发草稿写入+提交+冲突检测模块（CT-SES... | → | D_SHARED 共享服务: lock.py —— 分布式锁抽象（Phase 10 新增 | 盲点 B23 修 / ... | 导入依赖 / import_depends |
| 213 | StatusDashboard — 实时状态面板 / status_dashboard (tradi... | → | D_SHARED 共享服务: 时间utils.py —— 时间/日期工具（Phase 9 新增 | 盲点 / ti... | 导入依赖 / import_depends |
| 214 | StopGate — 质量闸门 / stop_gate (trading/stop_gate.py) | → | D_SHARED 共享服务: 时间utils.py —— 时间/日期工具（Phase 9 新增 | 盲点 / ti... | 导入依赖 / import_depends |
| 215 | WindowsService — Windows Service 包装器 / windows_servic... | → | D_SHARED 共享服务: 进程池 / process_pool.py - Shared process pool for MCP se... | 导入依赖 / import_depends |
| 216 | WorkDAG + WorkItem — 工作编排数据模型 / work_dag (tradin... | → | D_SHARED 共享服务: 模式 / schemas (schema/schemas.py) | 导入依赖 / import_depends |
| 217 | 工作编排子系统——决定什么工作、什么时候、用什么模型、什... | → | D_SHARED 共享服务: serialization.py —— 统一序列化/反序列化基础设施（Phase ... | 导入依赖 / import_depends |
| 218 | 工作编排子系统——决定什么工作、什么时候、用什么模型、什... | → | D_SHARED 共享服务: 时间utils.py —— 时间/日期工具（Phase 9 新增 | 盲点 / ti... | 导入依赖 / import_depends |
| 219 | zombiescanner.py — 僵尸 Python 进程检测与自动处置 / zomb... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 220 | 从 TaskRepository 查询 task 的 sou / boot_hooks (trading/... | → | D_TRADING 交易运营: ide健康daemon.py — TRAE IDE 幽灵窗口守护线程 / ide_healt... | 导入依赖 / import_depends |
| 221 | resourceoptimization / resource_optimization.py - MAPE-K ... | → | D_TRADING 交易运营: GPUmonitor.py — NVIDIA GPU 状态采集器 / gpu_monitor (tra... | 导入依赖 / import_depends |
| 222 | resourceoptimization / resource_optimization.py - MAPE-K ... | → | D_TRADING 交易运营: ide健康daemon.py — TRAE IDE 幽灵窗口守护线程 / ide_healt... | 导入依赖 / import_depends |

### 依赖本域的其他域（入边）/ Depended By

| # | 外部域-源模块 / Source Module | → | 本域模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | D_AUTONOMY_CORE 自治核心: ContextAssembler — 上下文装配、校验、影子留档 / context_... | → | 令牌budget.py — Token 估算工具 SSoT / token_budget (capa... | 导入依赖 / import_depends |
| 2 | D_AUTONOMY_CORE 自治核心: 上下文预算 / TruncationStrategy — TruncationStrategy (co... | → | 令牌budget.py — Token 估算工具 SSoT / token_budget (capa... | 导入依赖 / import_depends |
| 3 | D_AUTONOMY_CORE 自治核心: 上下文预算追踪器 / ContextBudgetTracker: token budget man... | → | 令牌budget.py — Token 估算工具 SSoT / token_budget (capa... | 导入依赖 / import_depends |
| 4 | D_AUTONOMY_CORE 自治核心: 上下文injector / ContextInjector: retrieve and inject rel... | → | 令牌budget.py — Token 估算工具 SSoT / token_budget (capa... | 导入依赖 / import_depends |
| 5 | D_AUTONOMY_CORE 自治核心: 上下文pipeline — Context Engine **四段流水 / context_pip... | → | 令牌budget.py — Token 估算工具 SSoT / token_budget (capa... | 导入依赖 / import_depends |
| 6 | D_AUTONOMY_CORE 自治核心: 上下文管线auto.py — ContextPipeli / context_pipeline_aut... | → | 终止开关 / kill_switch.py -- safety circuit breaker (DD11... | 导入依赖 / import_depends |
| 7 | D_AUTONOMY_CORE 自治核心: PromptRegistry: YAML-driven Prompt 模板注册表 / prompt_re... | → | 令牌budget.py — Token 估算工具 SSoT / token_budget (capa... | 导入依赖 / import_depends |
| 8 | D_AUTONOMY_CORE 自治核心: F1 AutoRuntimeCore 非mock端到端集成测试 / test_auto_runti... | → | AutoRuntimeCore — 三层运行时运营中心（系统大脑） / auto_... | 测试依赖 / test_depends |
| 9 | D_AUTONOMY_CORE 自治核心: F1 AutoRuntimeCore 非mock端到端集成测试 / test_auto_runti... | → | CapabilityRegistry — 能力注册中心 / capability_registry ... | 测试依赖 / test_depends |
| 10 | D_AUTONOMY_CORE 自治核心: F1 AutoRuntimeCore 非mock端到端集成测试 / test_auto_runti... | → | DreamCycle — 知识固化引擎 / dream_cycle (trading/dream_c... | 测试依赖 / test_depends |
| 11 | D_AUTONOMY_CORE 自治核心: F1 AutoRuntimeCore 非mock端到端集成测试 / test_auto_runti... | → | HealthMonitor — 健康监控 + 自愈 / health_monitor (tradin... | 测试依赖 / test_depends |
| 12 | D_AUTONOMY_CORE 自治核心: F1 AutoRuntimeCore 非mock端到端集成测试 / test_auto_runti... | → | 启动前配置完整性校验（5.71.1 治本）——必填字段/类型 / ru... | 测试依赖 / test_depends |
| 13 | D_AUTONOMY_CORE 自治核心: F1 AutoRuntimeCore 非mock端到端集成测试 / test_auto_runti... | → | WorkDAG + WorkItem — 工作编排数据模型 / work_dag (tradin... | 测试依赖 / test_depends |
| 14 | D_AUTONOMY_CORE 自治核心: F1 AutoRuntimeCore 非mock端到端集成测试 / test_auto_runti... | → | 工作编排子系统——决定什么工作、什么时候、用什么模型、什... | 测试依赖 / test_depends |
| 15 | D_AUTONOMY_CORE 自治核心: F14 管线编排/反馈环 — 红蓝对抗端到端极端测试 / test_f14_... | → | backpressure管理器 / Pipeline — Backpressure Manager (pi... | 测试依赖 / test_depends |
| 16 | D_AUTONOMY_CORE 自治核心: F14 管线编排/反馈环 — 红蓝对抗端到端极端测试 / test_f14_... | → | backpressure类型定义 / backpressure_types.py - Pipeline b... | 测试依赖 / test_depends |
| 17 | D_AUTONOMY_CORE 自治核心: F14 管线编排/反馈环 — 红蓝对抗端到端极端测试 / test_f14_... | → | DeadLetterQueue — 死信队列 / dead_letter_queue (pipeline... | 测试依赖 / test_depends |
| 18 | D_AUTONOMY_CORE 自治核心: F14 管线编排/反馈环 — 红蓝对抗端到端极端测试 / test_f14_... | → | Pipeline 数据模型 / models (pipeline/models.py) | 测试依赖 / test_depends |
| 19 | D_AUTONOMY_CORE 自治核心: F1 自动驾驶/运行时大脑 — 红蓝对抗端到端极端测试 / test_f... | → | DreamCycle — 知识固化引擎 / dream_cycle (trading/dream_c... | 测试依赖 / test_depends |
| 20 | D_AUTONOMY_CORE 自治核心: F1 自动驾驶/运行时大脑 — 红蓝对抗端到端极端测试 / test_f... | → | HealthMonitor — 健康监控 + 自愈 / health_monitor (tradin... | 测试依赖 / test_depends |
| 21 | D_AUTONOMY_CORE 自治核心: F1 自动驾驶/运行时大脑 — 红蓝对抗端到端极端测试 / test_f... | → | WorkDAG + WorkItem — 工作编排数据模型 / work_dag (tradin... | 测试依赖 / test_depends |
| 22 | D_AUTONOMY_CORE 自治核心: F1 自动驾驶/运行时大脑 — 红蓝对抗端到端极端测试 / test_f... | → | 工作编排子系统——决定什么工作、什么时候、用什么模型、什... | 测试依赖 / test_depends |
| 23 | D_BACKTEST 回测: 回测数据处理器模块（v1.1.0 扩展：多源化 + ClickHouse 实现... | → | DatabaseService: 统一管理数据库的连接池、生命周期、健康检... | 导入依赖 / import_depends |
| 24 | D_COMPLIANCE 合规: 包入口 / __init__ (behavioral_auditor/__init__.py) | → | 漂移事件记录——对齐 test状态machine. / state_machine (au... | 导入依赖 / import_depends |
| 25 | D_FEEDBACK_LOOP 反馈循环引擎: FLE -> Pipeline 背压桥接（CTR-BP-001~003） / backpressure... | → | backpressure管理器 / Pipeline — Backpressure Manager (pi... | 导入依赖 / import_depends |
| 26 | D_FEEDBACK_LOOP 反馈循环引擎: FLE 持久化写入器 — 写 metrics/alerts/dispatchl / db_writ... | → | TELE->FLE 指标桥接 — emitmetrics() 生产者 / metrics_brid... | 导入依赖 / import_depends |
| 27 | D_FEEDBACK_LOOP 反馈循环引擎: FLE 全链路调度器 —— collect->detect->diagnose- / schedu... | → | TELE->FLE 指标桥接 — emitmetrics() 生产者 / metrics_brid... | 导入依赖 / import_depends |
| 28 | D_GOVERNANCE 生命周期管理: 启动brain.py — ZephyrAlpha 系统大脑一键启动 / start_brai... | → | AutoRuntimeCore — 三层运行时运营中心（系统大脑） / auto_... | 导入依赖 / import_depends |
| 29 | D_GOVERNANCE 生命周期管理: 启动brain.py — ZephyrAlpha 系统大脑一键启动 / start_brai... | → | AutoTaskGenerator — 自动任务生成器 / auto_task_generator... | 导入依赖 / import_depends |
| 30 | D_GOVERNANCE 生命周期管理: Git Guard — 拦截危险 git 命令，防止破坏其他 session 的 /... | → | concurrencyguard — 回滚操作并发安全守卫。 / concurrency_... | 导入依赖 / import_depends |
| 31 | D_GOVERNANCE 生命周期管理: Post-checkout Guard — 事后检测 checkout 是否覆盖 / post_... | → | concurrencyguard — 回滚操作并发安全守卫。 / concurrency_... | 导入依赖 / import_depends |
| 32 | D_GOVERNANCE 生命周期管理: 上下文budget.py —— 上下文预算管理与超预算截断（Phase / ... | → | 令牌budget.py — Token 估算工具 SSoT / token_budget (capa... | 导入依赖 / import_depends |
| 33 | D_GOVERNANCE 生命周期管理: MiniQMT 实盘行情 Provider（Tick + 5档盘口） / miniqmt_pro... | → | DatabaseService: 统一管理数据库的连接池、生命周期、健康检... | 导入依赖 / import_depends |
| 34 | D_GOVERNANCE 生命周期管理: Self-Benchmark (W3-7) — 5 组已知对自验证 + 引擎退化 / se... | → | AssetDiscoveryScanner — MOD-INF-026 L1 全 / scanner (ass... | 导入依赖 / import_depends |
| 35 | D_GOVERNANCE 生命周期管理: DatabaseService 真源收敛（AI-14 审计 P1 修复） / database... | → | DatabaseService: 统一管理数据库的连接池、生命周期、健康检... | 导入依赖 / import_depends |
| 36 | D_GOVERNANCE 生命周期管理: 红蓝对抗极端测试 — gitguard + concurrency守卫 / test_con... | → | concurrencyguard — 回滚操作并发安全守卫。 / concurrency_... | 测试依赖 / test_depends |
| 37 | D_GOV_AUDIT 审计追踪: workspacehygienereconciler.py — 工作区卫生自 / workspace... | → | gitbatcher.py — Git 命令批量化工具（ARCH-GIT-CA / git_ba... | 导入依赖 / import_depends |
| 38 | D_GOV_CODE_QUALITY 代码质量治理: code-dedup-engine CLI——子命令映射+退出码+扫描入口. / cl... | → | AssetDiscoveryScanner — MOD-INF-026 L1 全 / scanner (ass... | 导入依赖 / import_depends |
| 39 | D_GOV_ENFORCEMENT 规则执行: 会话worktree.py — AI 对话 worktree 物理隔 / session_work... | → | gitbatcher.py — Git 命令批量化工具（ARCH-GIT-CA / git_ba... | 导入依赖 / import_depends |
| 40 | D_GOV_OPS_RESILIENCE 运维弹性治理: 熔断断路器 / Circuit Breaker — MOD-INF-022 (resilience_g... | → | Circuit Breaker — 熔断器：连续失败 -> OPEN -> 暂停 / cir... | 导入依赖 / import_depends |
| 41 | D_GOV_RULE 规则治理: 任务完成门禁 / Task Completion Gate (rule_enforcement/tas... | → | Task Lifecycle Manager — G0-G7 任务生命周期门禁。 / task... | 导入依赖 / import_depends |
| 42 | D_GOV_SCRIPTS 脚本治理: 会话simulator — 30 个模拟开发 session 的蓝图 / session_s... | → | 蓝图metrics — 蓝图使用追踪 instrumentati / blueprint_met... | 导入依赖 / import_depends |
| 43 | D_GOV_SCRIPTS 脚本治理: base.py — 审计脚本基类 / base (_shared/base.py) | → | Finding Schema — 审计发现标准化数据模型 / finding (scrip... | 导入依赖 / import_depends |
| 44 | D_GOV_SCRIPTS 脚本治理: 检查注册表consistency — 跨登记表一致性校验。 / check_reg... | → | Finding Schema — 审计发现标准化数据模型 / finding (scrip... | 导入依赖 / import_depends |
| 45 | D_GOV_SCRIPTS 脚本治理: 发现状态machine.py — Finding 全生命周期 / finding_state_... | → | Finding Schema — 审计发现标准化数据模型 / finding (scrip... | 导入依赖 / import_depends |
| 46 | D_GOV_SCRIPTS 脚本治理: 校验紧急bypasslog.py — 应急绕过审 / validate_emergency_b... | → | Finding Schema — 审计发现标准化数据模型 / finding (scrip... | 导入依赖 / import_depends |
| 47 | D_GOV_SCRIPTS 脚本治理: run_all.py — 脚本系统统一入口脚本 / run_all (governance/... | → | Finding->TaskCard 桥接器 / finding_task_bridge (infrastru... | 导入依赖 / import_depends |
| 48 | D_GOV_SCRIPTS 脚本治理: run_all.py — 脚本系统统一入口脚本 / run_all (governance/... | → | Finding Schema — 审计发现标准化数据模型 / finding (scrip... | 导入依赖 / import_depends |
| 49 | D_INFRA_RECOVERY 回滚恢复: RollbackExecutor — 回滚执行器核心封装。 / rollback_execu... | → | concurrencyguard — 回滚操作并发安全守卫。 / concurrency_... | 导入依赖 / import_depends |
| 50 | D_INTEGRATION 管线路由: LocalModelScheduler — L2 本地模型 24/7 调度循环 / local_... | → | resourceoptimization / resource_optimization.py - MAPE-K ... | 导入依赖 / import_depends |
| 51 | D_INTEGRATION 管线路由: ZephyrAlpha MCP Telemetry Server — 系统可观测 / telemetr... | → | Telemetry — 系统遥测门面类（MOD-INF-015 v2.1.0） / facad... | 导入依赖 / import_depends |
| 52 | D_INTEGRATION 管线路由: PipelineOrchestrator — M1-M11 管线协调器 / pipeline_orch... | → | 熔断断路器管理器 / CircuitBreakerManager -- standalone ci... | 导入依赖 / import_depends |
| 53 | D_INTEGRATION 管线路由: PipelineOrchestrator — M1-M11 管线协调器 / pipeline_orch... | → | CostTracker —— LLM 调用成本追踪器（SRC-0025） / cost_tr... | 导入依赖 / import_depends |
| 54 | D_INTEGRATION 管线路由: PipelineOrchestrator — M1-M11 管线协调器 / pipeline_orch... | → | CT-PIPE-ORC-001 — TaskCard -> 管线入口节点路由 / ct_pipe... | 导入依赖 / import_depends |
| 55 | D_INTEGRATION 管线路由: PipelineOrchestrator — M1-M11 管线协调器 / pipeline_orch... | → | DeadLetterQueue — 死信队列 / dead_letter_queue (pipeline... | 导入依赖 / import_depends |
| 56 | D_INTEGRATION 管线路由: PipelineOrchestrator — M1-M11 管线协调器 / pipeline_orch... | → | ModelRouter — 模型路由与降级链管理 / model_router (pipel... | 导入依赖 / import_depends |
| 57 | D_INTEGRATION 管线路由: PipelineOrchestrator — M1-M11 管线协调器 / pipeline_orch... | → | Pipeline 数据模型 / models (pipeline/models.py) | 导入依赖 / import_depends |
| 58 | D_INTEGRATION 管线路由: PipelineOrchestrator — M1-M11 管线协调器 / pipeline_orch... | → | Pipeline -> Agent Bridge — 双编排器桥接层 / pipeline_age... | 导入依赖 / import_depends |
| 59 | D_INTEGRATION 管线路由: PipelineOrchestrator — M1-M11 管线协调器 / pipeline_orch... | → | Pipeline Lock — 双管线并发锁 / pipeline_lock (pipeline/p... | 导入依赖 / import_depends |
| 60 | D_INTEGRATION 管线路由: PipelineOrchestrator — M1-M11 管线协调器 / pipeline_orch... | → | PreemptionManager -- 优先级抢占管理器 / preemption_manage... | 导入依赖 / import_depends |
| 61 | D_INTEGRATION 管线路由: PipelineOrchestrator — M1-M11 管线协调器 / pipeline_orch... | → | Pipeline Routing Plugin System — K8s Sch / routing_plugi... | 导入依赖 / import_depends |
| 62 | D_INTEGRATION 管线路由: PipelineOrchestrator — M1-M11 管线协调器 / pipeline_orch... | → | hooks.py —— 模块生命周期钩子（Phase 2 新增 | 盲点 B8  /... | 导入依赖 / import_depends |
| 63 | D_INTELLIGENCE 上下文管理: ModelTaskMatrix — 任务×模型性能学习引擎 / task_model_le... | → | Pipeline 数据模型 / models (pipeline/models.py) | 导入依赖 / import_depends |
| 64 | D_ORCHESTRATOR 代理编排器: AgentOrchestrator · 多角色 Agent 路由、工具链编排与健 / ... | → | 令牌budget.py — Token 估算工具 SSoT / token_budget (capa... | 导入依赖 / import_depends |
| 65 | D_ORCHESTRATOR 代理编排器: Orc->Script 脚本执行器 — runaudit() 生产者 / script_runn... | → | Script->Gate 门禁桥接器 — submitfindings() 生 / gate_bri... | 导入依赖 / import_depends |
| 66 | D_SECURITY 对抗验证: MCP集成 / mcp_integration (orphan_judge/mcp_integration.py) | → | AssetInventory MCP Server — MOD-INF-026  / mcp_server (a... | 导入依赖 / import_depends |
| 67 | D_SECURITY 对抗验证: [INVARIANTS] 蓝图 §4 文件清单与代码双向对齐 / orphan_det... | → | CapabilityRegistry — 能力注册中心 / capability_registry ... | 导入依赖 / import_depends |
| 68 | D_SECURITY 对抗验证: [INVARIANTS] 蓝图 §4 文件清单与代码双向对齐 / orphan_det... | → | ModuleOnboardingScanner — 模块接入扫描器 / module_onboar... | 导入依赖 / import_depends |
| 69 | D_SHARED 共享服务: ProcessLifecycleGateway — 进程生命周期统一入口 / process... | → | daemon注册表 / daemon_registry.py - unified daemon thread... | 导入依赖 / import_depends |
| 70 | D_SHARED 共享服务: 进程池 / process_pool.py - Shared process pool for MCP se... | → | resourceoptimization模型 / models.py - Pydantic data mode... | 导入依赖 / import_depends |
| 71 | D_SHARED 共享服务: io缓存 / io_cache.py - File-level I/O cache with LRU evic... | → | resourceoptimization模型 / models.py - Pydantic data mode... | 导入依赖 / import_depends |
| 72 | D_SHARED 共享服务: health.py —— ZephyrAlpha 聚合健康检查 / health (lifecyc... | → | hooks.py —— 模块生命周期钩子（Phase 2 新增 | 盲点 B8  /... | 导入依赖 / import_depends |
| 73 | D_TRADING 交易运营: BRAIN 注释块文本编辑器（ActionDispatche / __init__ (actio... | → | Task Scheduler — 任务调度器。 / task_scheduler (queue/ta... | 导入依赖 / import_depends |
| 74 | D_TRADING 交易运营: 注释注解写入器（从 ActionDispatcher.annotatepy / _annotat... | → | ActionDispatcher --- 大脑的"手" v2.0 (Phase  / action_dis... | 导入依赖 / import_depends |
| 75 | D_TRADING 交易运营: 审计日志写入器（从 ActionDispatcher.writetriage / _audit_... | → | ActionDispatcher --- 大脑的"手" v2.0 (Phase  / action_dis... | 导入依赖 / import_depends |
| 76 | D_TRADING 交易运营: 文件生命周期管理器（从 ActionDispatcher.创建fil / _file_l... | → | ActionDispatcher --- 大脑的"手" v2.0 (Phase  / action_dis... | 导入依赖 / import_depends |
| 77 | D_TRADING 交易运营: 搜索替换引擎（从 ActionDispatcher.searchreplac / _search_... | → | ActionDispatcher --- 大脑的"手" v2.0 (Phase  / action_dis... | 导入依赖 / import_depends |
| 78 | D_TRADING 交易运营: ide健康daemon.py — TRAE IDE 幽灵窗口守护线程 / ide_healt... | → | daemon注册表 / daemon_registry.py - unified daemon thread... | 导入依赖 / import_depends |

### 跨域依赖图 / Cross-domain Dependency Diagram

> 本域与 24 个外部域直接连接（出边 222 条 + 入边 78 条 = 300 条）。只显示直接连接的域，不展开具体节点。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
graph LR
    D_INFRA_RUNTIME["D_INFRA_RUNTIME<br/>运行时集成"]
    D_SHARED["D_SHARED<br/>共享服务"]
    D_GOVERNANCE["D_GOVERNANCE<br/>生命周期管理"]
    D_INTEGRATION["D_INTEGRATION<br/>管线路由"]
    D_SECURITY["D_SECURITY<br/>对抗验证"]
    D_GOV_OPS_RESILIENCE["D_GOV_OPS_RESILIENCE<br/>运维弹性治理"]
    D_GOV_RULE["D_GOV_RULE<br/>规则治理"]
    D_GOV_AUDIT["D_GOV_AUDIT<br/>审计追踪"]
    D_FEEDBACK_LOOP["D_FEEDBACK_LOOP<br/>反馈循环引擎"]
    D_INTELLIGENCE["D_INTELLIGENCE<br/>上下文管理"]
    D_TRADING["D_TRADING<br/>交易运营"]
    D_INFRA_A2A["D_INFRA_A2A<br/>A2A通信"]
    D_GOV_DRIFT["D_GOV_DRIFT<br/>漂移检测"]
    D_AUTONOMY_CORE["D_AUTONOMY_CORE<br/>自治核心"]
    D_INFRA_RECOVERY["D_INFRA_RECOVERY<br/>回滚恢复"]
    D_OPS["D_OPS<br/>反馈循环"]
    D_ORCHESTRATOR["D_ORCHESTRATOR<br/>代理编排器"]
    D_INFRASTRUCTURE["D_INFRASTRUCTURE<br/>跨层契约基础设施"]
    D_GOV_REPAIR["D_GOV_REPAIR<br/>治理修复"]
    D_DATA["D_DATA<br/>数据接入层"]
    D_GOV_SCRIPTS["D_GOV_SCRIPTS<br/>脚本治理"]
    D_COMPLIANCE["D_COMPLIANCE<br/>合规"]
    D_BACKTEST["D_BACKTEST<br/>回测"]
    D_GOV_CODE_QUALITY["D_GOV_CODE_QUALITY<br/>代码质量治理"]
    D_GOV_ENFORCEMENT["D_GOV_ENFORCEMENT<br/>规则执行"]
    D_INFRA_RUNTIME -->|163条 导入依赖 / import_depends| D_SHARED
    D_INFRA_RUNTIME -->|12条 导入依赖 / import_depends| D_GOVERNANCE
    D_INFRA_RUNTIME -->|8条 导入依赖 / import_depends| D_INTEGRATION
    D_INFRA_RUNTIME -->|5条 导入依赖 / import_depends| D_SECURITY
    D_INFRA_RUNTIME -->|4条 导入依赖 / import_depends| D_GOV_OPS_RESILIENCE
    D_INFRA_RUNTIME -->|4条 导入依赖 / import_depends| D_GOV_RULE
    D_INFRA_RUNTIME -->|3条 导入依赖 / import_depends| D_GOV_AUDIT
    D_INFRA_RUNTIME -->|3条 导入依赖 / import_depends| D_FEEDBACK_LOOP
    D_INFRA_RUNTIME -->|3条 导入依赖 / import_depends| D_INTELLIGENCE
    D_INFRA_RUNTIME -->|3条 导入依赖 / import_depends| D_TRADING
    D_INFRA_RUNTIME -->|3条 导入依赖 / import_depends| D_INFRA_A2A
    D_INFRA_RUNTIME -->|3条 导入依赖 / import_depends| D_GOV_DRIFT
    D_INFRA_RUNTIME -->|2条 导入依赖 / import_depends| D_AUTONOMY_CORE
    D_INFRA_RUNTIME -->|1条 导入依赖 / import_depends| D_INFRA_RECOVERY
    D_INFRA_RUNTIME -->|1条 导入依赖 / import_depends| D_OPS
    D_INFRA_RUNTIME -->|1条 导入依赖 / import_depends| D_ORCHESTRATOR
    D_INFRA_RUNTIME -->|1条 导入依赖 / import_depends| D_INFRASTRUCTURE
    D_INFRA_RUNTIME -->|1条 导入依赖 / import_depends| D_GOV_REPAIR
    D_INFRA_RUNTIME -->|1条 导入依赖 / import_depends| D_DATA
    D_AUTONOMY_CORE -->|22条 导入依赖 / import_depends, 测试依赖 / test_depends| D_INFRA_RUNTIME
    D_INTEGRATION -->|13条 导入依赖 / import_depends| D_INFRA_RUNTIME
    D_GOVERNANCE -->|9条 导入依赖 / import_depends, 测试依赖 / test_depends| D_INFRA_RUNTIME
    D_GOV_SCRIPTS -->|7条 导入依赖 / import_depends| D_INFRA_RUNTIME
    D_TRADING -->|6条 导入依赖 / import_depends| D_INFRA_RUNTIME
    D_SHARED -->|4条 导入依赖 / import_depends| D_INFRA_RUNTIME
    D_SECURITY -->|3条 导入依赖 / import_depends| D_INFRA_RUNTIME
    D_FEEDBACK_LOOP -->|3条 导入依赖 / import_depends| D_INFRA_RUNTIME
    D_ORCHESTRATOR -->|2条 导入依赖 / import_depends| D_INFRA_RUNTIME
    D_GOV_RULE -->|1条 导入依赖 / import_depends| D_INFRA_RUNTIME
    D_INFRA_RECOVERY -->|1条 导入依赖 / import_depends| D_INFRA_RUNTIME
    D_COMPLIANCE -->|1条 导入依赖 / import_depends| D_INFRA_RUNTIME
    D_INTELLIGENCE -->|1条 导入依赖 / import_depends| D_INFRA_RUNTIME
    D_GOV_AUDIT -->|1条 导入依赖 / import_depends| D_INFRA_RUNTIME
    D_BACKTEST -->|1条 导入依赖 / import_depends| D_INFRA_RUNTIME
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
