---
doc_type: architecture_view
title: D_ORCHESTRATOR 代理编排器架构文档
version: "1.0"
status: active
date: 2026-08-05
owner: auto-generator
ttl: permanent
---

# 25_d_orchestrator / 代理编排器域 / Agent Orchestrator

> **功能简介 / Overview**: 代理编排器，负责 Agent 任务全生命周期：任务入队、调度、沙箱执行、幻觉检测和收尾归档

> **文档作用 / Purpose**: 展示 代理编排器（D_ORCHESTRATOR）功能域的域内依赖关系、跨域依赖关系，模块信息（成熟度/中英文名/大白话/文件路径）内嵌于 Mermaid 节点，供架构审查和域治理参考。

> 本文档由 generate_domain_doc.py 从 depgraph (PostgreSQL) 自动生成
> 数据源: depgraph (PostgreSQL) nodes表 + edges表

> **[可缩放 HTML 版 / Zoomable HTML](http://localhost:8765/docs/02_enterprise_architecture/02_domain_architecture_docs/_zoomable_html/25_d_orchestrator.html)** — Ctrl+滚轮缩放 ｜ 双击重置 ｜ Ctrl+Shift+D 切换拖动/选择模式

## 域基本信息 / Domain Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 编号 | 25 | Number | 25 |
| 域ID | D_ORCHESTRATOR | Domain ID | D_ORCHESTRATOR |
| 域名称 | 代理编排器 | Domain Name | Agent Orchestrator |
| 层级 | L1 基础平台层 | Layer | L1 Foundation |
| 模块数 | 72 | Module Count | 72 |
| 域内依赖 | 20 | Internal Dependencies | 20 |
| 跨域入边 | 8 | Cross-domain Incoming | 8 |
| 跨域出边 | 55 | Cross-domain Outgoing | 55 |
| 设计态模块 | 2 | Design Modules | 2 |
| 生产态模块 | 70 | Production Modules | 70 |
| 容量 | 70/150 (正常) | Capacity | 70/150 (正常) |
| 描述 | Agent全生命周期编排 | Description | Agent全生命周期编排 |

## 域内依赖图 / Internal Dependency Diagram

> 依赖图内嵌在本文档中，IDE 可直接渲染；网页版可 Ctrl+滚轮缩放 + 拖动平移查看细节。
>
> **图例说明 / Legend**：
> - 🟦 **蓝色 = 运营态模块**（production，已上线运行）
> - 🟧 **橙色虚线 = 设计态模块**（design，蓝图阶段，代码未写）
> - **实线箭头 = 运营态依赖**（已生效的依赖关系）
> - **虚线箭头 = 非运营态依赖**（计划中/验证中的依赖关系）

### 全景图（全部模块，颜色区分运营态/设计态）

> 展示全部 72 个模块（生产态 70 + 设计态 2），含跨域依赖外部节点。节点含成熟度+名称+大白话/简介+文件路径。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    src_zephyr_orchestrator_init_py["zephyr/orchestrator 包入口<br/>管理zephyr.orchestrator子包的加载和懒导入<br/>Init<br/>文件: orchestrator/__init__.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_agent_health_monitor_py["SLO 违规记录模型<br/>AgentHealthMonitor · Agent 健康监控（三态 + 5<br/>项 SLO）<br/>Agent Health Monitor<br/>文件: orchestrator/agent_health_monitor.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_contracts_init_py["orchestrator/contracts 包入口<br/>contracts — orchestrator contracts subpackage.<br/>Init<br/>文件: contracts/__init__.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_contracts_construction_guide_py["Construction Guide<br/>施工指南引擎（Construction Guide）<br/>文件: contracts/construction_guide.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_contracts_contract_router_py["契约路由器<br/>契约路由（Contract Router）<br/>文件: contracts/contract_router.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_contracts_design_decisions_py["Design Decisions<br/>编排/契约包的design_decisions模块<br/>文件: contracts/design_decisions.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_contracts_finding_bridge_py["Finding桥接器<br/>CT-ORC-SCRIPT-001 运行时桥接<br/>Finding Bridge<br/>文件: contracts/finding_bridge.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_contracts_prompt_version_py["—prompt template版本化+部署前diff<br/>AI Prompt 版本控制（CT-PROMPT-VERSION）——prompt<br/>template版本化+部署前diff。<br/>Prompt Version<br/>文件: contracts/prompt_version.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_core_init_py["orchestrator/core 包入口<br/>orchestrator.core — auto-generated package init.<br/>文件: core/__init__.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_deferred_queue_py["WAITING -> READY task scheduler.<br/>DeferredQueue: WAITING -> READY task scheduler.<br/>Deferred Queue<br/>文件: orchestrator/deferred_queue.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_execution_init_py["orchestrator/execution 包入口<br/>execution — orchestrator execution subpackage.<br/>Init<br/>文件: execution/__init__.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_execution_data_lifecycle_py["—8类数据保留策略+每日GC<br/>编排/执行包的data_lifecycle模块<br/>Data Lifecycle<br/>文件: execution/data_lifecycle.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_execution_dispatch_table_py["Dispatch Table<br/>AI Agent 冷启动分派表（Dispatch Table）<br/>文件: execution/dispatch_table.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_execution_dlq_manager_py["只读：messages<br/>DLQ 管理器（Dead Letter Queue Manager —<br/>CT-DLQ-001）<br/>Dlq Manager<br/>文件: execution/dlq_manager.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_execution_phase_executor_py["阶段执行器<br/>Phase 执行引擎（Phase Executor）<br/>文件: execution/phase_executor.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_execution_reconciliation_loop_py["只读：results<br/>编排/执行包的reconciliation_loop模块<br/>Reconciliation Loop<br/>文件: execution/reconciliation_loop.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_execution_trigger_router_py["触发路由审计日志 duck-typed 接口<br/>TriggerRouter — RI-03 触发路由器（M3<br/>跨模块触发分派）<br/>Trigger Router<br/>文件: execution/trigger_router.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_execution_wave_generator_py["Wave生成器<br/>WaveGenerator — 根据 Task 依赖图生成执行 Wave<br/>（T-2-03）<br/>Wave Generator<br/>文件: execution/wave_generator.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_factor_direct_fusion_engine_py["orchestrator/factor_direct_fusion_engine<br/>编排包的factor_direct_fusion_engine模块<br/>文件: orchestrator<br/>/factor_direct_fusion_engine.py<br/>(设计态 / design)"]
    src_zephyr_orchestrator_fault_tolerance_init_py["orchestrator/fault_tolerance 包入口<br/>fault_tolerance — orchestrator fault_tolerance<br/>subpackage.<br/>Init<br/>文件: fault_tolerance/__init__.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_fault_tolerance_canary_manager_py["—权重分流+指标对比+自动回滚<br/>金丝雀发布管理器<br/>（CT-CANARY）——权重分流+指标对比+自动回滚。<br/>Canary Manager<br/>文件: fault_tolerance/canary_manager.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_fault_tolerance_chaos_hooks_py["混沌Hooks<br/>ChaosHook — integrates ChaosEngine with the<br/>orchestrator execution loop.<br/>Chaos Hooks<br/>文件: fault_tolerance/chaos_hooks.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_fault_tolerance_degrade_cascade_py["—降级传播链检测+熔断<br/>编排/fault tolerance包的degrade_cascade模块<br/>Degrade Cascade<br/>文件: fault_tolerance/degrade_cascade.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_fault_tolerance_disk_guard_py["—剩余空间<5%->告警+只读模式<br/>编排/fault tolerance包的disk_guard模块<br/>Disk Guard<br/>文件: fault_tolerance/disk_guard.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_fault_tolerance_network_partition_py["—CAP定理CP优先+脑裂检测+quorum write<br/>网络分区容忍（CT-NETWORK-PARTITION）——CAP定理CP<br/>优先+脑裂检测+quorum write。<br/>Network Partition<br/>文件: fault_tolerance/network_partition.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_governance_init_py["orchestrator/governance 包入口<br/>governance — orchestrator governance subpackage.<br/>Init<br/>文件: governance/__init__.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_governance_capacity_budget_py["只读：budget<br/>全局容量预算控制器（Capacity Budget Controller）<br/>文件: governance/capacity_budget.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_governance_dependency_lock_py["—Python包版本锁定+hash验证+安全审计<br/>外部依赖版本锁（CT-DEPS）——Python包版本锁定+hash<br/>验证+安全审计。<br/>Dependency Lock<br/>文件: governance/dependency_lock.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_governance_model_registry_py["—deepseek/opus/gpt等模型版本+性能基线<br/>编排/治理包的model_registry模块<br/>Model Registry<br/>文件: governance/model_registry.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_governance_path_index_py["—Module->__init__.py->蓝图->任务卡->配置的完整映<br/>射<br/>编排/治理包的path_index模块<br/>Path Index<br/>文件: governance/path_index.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_governance_risk_registry_py["风险注册表<br/>编排/治理包的risk_registry模块<br/>Risk Registry<br/>文件: governance/risk_registry.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_governance_schema_migration_py["—向后兼容迁移+回滚脚本<br/>数据库 Schema 演化契约<br/>（CT-SCHEMA-MIGRATE）——向后兼容迁移+回滚脚本。<br/>Schema Migration<br/>文件: governance/schema_migration.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_governance_version_manifest_py["—各系统版本号+文件路径索引<br/>编排/治理包的version_manifest模块<br/>Version Manifest<br/>文件: governance/version_manifest.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_hallucination_detector_py["Hallucination检测器<br/>HallucinationDetector · Chain-of-Verification<br/>（CoVe）幻觉检测器<br/>Hallucination Detector<br/>文件: orchestrator/hallucination_detector.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_lifecycle_init_py["orchestrator/lifecycle 包入口<br/>lifecycle — orchestrator lifecycle subpackage.<br/>Init<br/>文件: lifecycle/__init__.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_lifecycle_housekeeping_py["—临时文件扫描+日志轮转+废弃目录清理<br/>文件卫生保洁管理器<br/>（CT-HOUSEKEEPING）——临时文件扫描+日志轮转+废弃<br/>目录清理。<br/>文件: lifecycle/housekeeping.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_lifecycle_incident_postmortem_py["—incident记录+timeline+action_items+postmortem<br/>事件复盘管理器（CT-INCIDENT）——incident记录+time<br/>line+action_items+postmortem。<br/>Incident Postmortem<br/>文件: lifecycle/incident_postmortem.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_lifecycle_session_conflict_py["—文件锁+并发session检测+冲突resolution<br/>Session 冲突预防契约<br/>（CT-SESSION-CONFLICT）——文件锁+并发session检测+<br/>冲突res...<br/>Session Conflict<br/>文件: lifecycle/session_conflict.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_lifecycle_startup_sequencer_py["只读：states<br/>编排/lifecycle包的startup_sequencer模块<br/>Startup Sequencer<br/>文件: lifecycle/startup_sequencer.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_lifecycle_state_propagation_py["状态Propagation<br/>全局状态传播链（State Propagation Chain）<br/>文件: lifecycle/state_propagation.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_lifecycle_state_synchronizer_py["构造 alias fallback 集合<br/>StateSynchronizer — 同步 SQLite<br/>状态与文件系统实际状态（T-2-04）<br/>State Synchronizer<br/>文件: lifecycle/state_synchronizer.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_lifecycle_system_transfer_py["—系统Owner变更+配置迁移+密钥轮转+健康验证<br/>系统移交恢复（CT-TRANSFER）——系统Owner变更+配置<br/>迁移+密钥轮转+健康验证。<br/>System Transfer<br/>文件: lifecycle/system_transfer.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_lifecycle_teardown_manager_py["Teardown管理器<br/>编排/lifecycle包的teardown_manager模块<br/>Teardown Manager<br/>文件: lifecycle/teardown_manager.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_quality_agent_quality_py["—task完成质量评分+agent绩效追踪<br/>AI Agent 质量反馈闭环<br/>（CT-AGENT-QUALITY）——task完成质量评分+agent绩效<br/>追踪。<br/>Agent Quality<br/>文件: quality/agent_quality.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_quality_benchmark_runner_py["—13条CT-*基准数据+回归告警<br/>编排/quality包的benchmark_runner模块<br/>Benchmark Runner<br/>文件: quality/benchmark_runner.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_quality_blind_spot_closure_py["—Round 5 B-MOD-301~335 全三批关闭<br/>编排/quality包的blind_spot_closure模块<br/>Blind Spot Closure<br/>文件: quality/blind_spot_closure.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_quality_ke_quality_py["—KE完整性+准确性+时效性三维评分<br/>知识质量评分契约<br/>（CT-KE-QUALITY）——KE完整性+准确性+时效性三维评<br/>分。<br/>Ke Quality<br/>文件: quality/ke_quality.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_quality_knowledge_freshness_py["—KE过期标记+自动失效<br/>知识新鲜度废止管理器<br/>（CT-KNOWLEDGE-FRESHNESS）——KE过期标记+自动失效<br/>。<br/>Knowledge Freshness<br/>文件: quality/knowledge_freshness.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_quality_lean_scanner_py["—三款扫描器+自动化清理建议<br/>死代码/孤儿文件/僵尸引用三扫描<br/>（CT-LEAN）——三款扫描器+自动化清理建议。<br/>Lean Scanner<br/>文件: quality/lean_scanner.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_quality_stability_guard_py["—public API签名锁+breaking change检测<br/>API 稳定性守护（CT-STABILITY）——public<br/>API签名锁+breaking change检测。<br/>Stability Guard<br/>文件: quality/stability_guard.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_resilience_init_py["orchestrator/resilience 包入口<br/>orchestrator.resilience — auto-generated<br/>package init.<br/>文件: resilience/__init__.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_rollback_manager_py["回滚管理器<br/>RollbackManager — 仅调试用途的 DB-state<br/>快照，不用于自动回滚。<br/>Rollback Manager<br/>文件: orchestrator/rollback_manager.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_task_queue_py["任务Queue<br/>ActiveTaskQueue — 后台任务轮询与自动分发<br/>Task Queue<br/>文件: orchestrator/task_queue.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_voting_first_multi_agent_py["orchestrator/voting_first_multi_agent<br/>编排包的voting_first_multi_agent模块<br/>文件: orchestrator/voting_first_multi_agent.py<br/>(设计态 / design)"]
    src_zephyr_orchestrator_init_py ~~~ src_zephyr_orchestrator_agent_health_monitor_py
    src_zephyr_orchestrator_agent_health_monitor_py ~~~ src_zephyr_orchestrator_contracts_init_py
    src_zephyr_orchestrator_contracts_init_py ~~~ src_zephyr_orchestrator_contracts_construction_guide_py
    src_zephyr_orchestrator_contracts_construction_guide_py ~~~ src_zephyr_orchestrator_contracts_contract_router_py
    src_zephyr_orchestrator_contracts_contract_router_py ~~~ src_zephyr_orchestrator_contracts_design_decisions_py
    src_zephyr_orchestrator_contracts_design_decisions_py ~~~ src_zephyr_orchestrator_contracts_finding_bridge_py
    src_zephyr_orchestrator_contracts_finding_bridge_py ~~~ src_zephyr_orchestrator_contracts_prompt_version_py
    src_zephyr_orchestrator_contracts_prompt_version_py ~~~ src_zephyr_orchestrator_core_init_py
    src_zephyr_orchestrator_core_init_py ~~~ src_zephyr_orchestrator_deferred_queue_py
    src_zephyr_orchestrator_deferred_queue_py ~~~ src_zephyr_orchestrator_execution_init_py
    src_zephyr_orchestrator_execution_init_py ~~~ src_zephyr_orchestrator_execution_data_lifecycle_py
    src_zephyr_orchestrator_execution_data_lifecycle_py ~~~ src_zephyr_orchestrator_execution_dispatch_table_py
    src_zephyr_orchestrator_execution_dispatch_table_py ~~~ src_zephyr_orchestrator_execution_dlq_manager_py
    src_zephyr_orchestrator_execution_dlq_manager_py ~~~ src_zephyr_orchestrator_execution_phase_executor_py
    src_zephyr_orchestrator_execution_phase_executor_py ~~~ src_zephyr_orchestrator_execution_reconciliation_loop_py
    src_zephyr_orchestrator_execution_reconciliation_loop_py ~~~ src_zephyr_orchestrator_execution_trigger_router_py
    src_zephyr_orchestrator_execution_trigger_router_py ~~~ src_zephyr_orchestrator_execution_wave_generator_py
    src_zephyr_orchestrator_execution_wave_generator_py ~~~ src_zephyr_orchestrator_factor_direct_fusion_engine_py
    src_zephyr_orchestrator_factor_direct_fusion_engine_py ~~~ src_zephyr_orchestrator_fault_tolerance_init_py
    src_zephyr_orchestrator_fault_tolerance_init_py ~~~ src_zephyr_orchestrator_fault_tolerance_canary_manager_py
    src_zephyr_orchestrator_fault_tolerance_canary_manager_py ~~~ src_zephyr_orchestrator_fault_tolerance_chaos_hooks_py
    src_zephyr_orchestrator_fault_tolerance_chaos_hooks_py ~~~ src_zephyr_orchestrator_fault_tolerance_degrade_cascade_py
    src_zephyr_orchestrator_fault_tolerance_degrade_cascade_py ~~~ src_zephyr_orchestrator_fault_tolerance_disk_guard_py
    src_zephyr_orchestrator_fault_tolerance_disk_guard_py ~~~ src_zephyr_orchestrator_fault_tolerance_network_partition_py
    src_zephyr_orchestrator_fault_tolerance_network_partition_py ~~~ src_zephyr_orchestrator_governance_init_py
    src_zephyr_orchestrator_governance_init_py ~~~ src_zephyr_orchestrator_governance_capacity_budget_py
    src_zephyr_orchestrator_governance_capacity_budget_py ~~~ src_zephyr_orchestrator_governance_dependency_lock_py
    src_zephyr_orchestrator_governance_dependency_lock_py ~~~ src_zephyr_orchestrator_governance_model_registry_py
    src_zephyr_orchestrator_governance_model_registry_py ~~~ src_zephyr_orchestrator_governance_path_index_py
    src_zephyr_orchestrator_governance_path_index_py ~~~ src_zephyr_orchestrator_governance_risk_registry_py
    src_zephyr_orchestrator_governance_risk_registry_py ~~~ src_zephyr_orchestrator_governance_schema_migration_py
    src_zephyr_orchestrator_governance_schema_migration_py ~~~ src_zephyr_orchestrator_governance_version_manifest_py
    src_zephyr_orchestrator_governance_version_manifest_py ~~~ src_zephyr_orchestrator_hallucination_detector_py
    src_zephyr_orchestrator_hallucination_detector_py ~~~ src_zephyr_orchestrator_lifecycle_init_py
    src_zephyr_orchestrator_lifecycle_init_py ~~~ src_zephyr_orchestrator_lifecycle_housekeeping_py
    src_zephyr_orchestrator_lifecycle_housekeeping_py ~~~ src_zephyr_orchestrator_lifecycle_incident_postmortem_py
    src_zephyr_orchestrator_lifecycle_incident_postmortem_py ~~~ src_zephyr_orchestrator_lifecycle_session_conflict_py
    src_zephyr_orchestrator_lifecycle_session_conflict_py ~~~ src_zephyr_orchestrator_lifecycle_startup_sequencer_py
    src_zephyr_orchestrator_lifecycle_startup_sequencer_py ~~~ src_zephyr_orchestrator_lifecycle_state_propagation_py
    src_zephyr_orchestrator_lifecycle_state_propagation_py ~~~ src_zephyr_orchestrator_lifecycle_state_synchronizer_py
    src_zephyr_orchestrator_lifecycle_state_synchronizer_py ~~~ src_zephyr_orchestrator_lifecycle_system_transfer_py
    src_zephyr_orchestrator_lifecycle_system_transfer_py ~~~ src_zephyr_orchestrator_lifecycle_teardown_manager_py
    src_zephyr_orchestrator_lifecycle_teardown_manager_py ~~~ src_zephyr_orchestrator_quality_agent_quality_py
    src_zephyr_orchestrator_quality_agent_quality_py ~~~ src_zephyr_orchestrator_quality_benchmark_runner_py
    src_zephyr_orchestrator_quality_benchmark_runner_py ~~~ src_zephyr_orchestrator_quality_blind_spot_closure_py
    src_zephyr_orchestrator_quality_blind_spot_closure_py ~~~ src_zephyr_orchestrator_quality_ke_quality_py
    src_zephyr_orchestrator_quality_ke_quality_py ~~~ src_zephyr_orchestrator_quality_knowledge_freshness_py
    src_zephyr_orchestrator_quality_knowledge_freshness_py ~~~ src_zephyr_orchestrator_quality_lean_scanner_py
    src_zephyr_orchestrator_quality_lean_scanner_py ~~~ src_zephyr_orchestrator_quality_stability_guard_py
    src_zephyr_orchestrator_quality_stability_guard_py ~~~ src_zephyr_orchestrator_resilience_init_py
    src_zephyr_orchestrator_resilience_init_py ~~~ src_zephyr_orchestrator_rollback_manager_py
    src_zephyr_orchestrator_rollback_manager_py ~~~ src_zephyr_orchestrator_task_queue_py
    src_zephyr_orchestrator_task_queue_py ~~~ src_zephyr_orchestrator_voting_first_multi_agent_py
    src_zephyr_orchestrator_agent_orchestrator_py["代理编排器<br/>AgentOrchestrator · 多角色 Agent<br/>路由、工具链编排与健康监控<br/>Agent Orchestrator<br/>文件: orchestrator/agent_orchestrator.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_contracts_alert_handler_py["Alert处理器<br/>Orc 告警接收器 — handle_alert() 消费者<br/>Alert Handler<br/>文件: contracts/alert_handler.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_contracts_contract_registry_py["契约注册表<br/>集成契约注册表（Contract Registry）<br/>文件: contracts/contract_registry.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_core_task_queue_py["打破 pipeline↔orchestrator 循环依赖的协议接口<br/>ActiveTaskQueue — 后台任务轮询与自动分发<br/>Task Queue<br/>文件: core/task_queue.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_execution_batch_orchestrator_py["多 Worker 批量任务协调器<br/>BatchOrchestrator — 多 Worker 批量任务协调器<br/>（MOD-INF-016）<br/>Batch Orchestrator<br/>文件: execution/batch_orchestrator.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_execution_context_bridge_py["上下文桥接器<br/>Orc->CE 上下文桥接 — request_context() 生产者<br/>Context Bridge<br/>文件: execution/context_bridge.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_execution_memory_writer_py["Orc->VMS 记忆写入器'''<br/>编排/执行包的memory_writer模块<br/>Memory Writer<br/>文件: execution/memory_writer.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_execution_script_runner_py["脚本运行器<br/>Orc->Script 脚本执行器 — run_audit() 生产者<br/>Script Runner<br/>文件: execution/script_runner.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_fault_tolerance_bulkhead_manager_py["—12系统独立资源池<br/>编排/fault tolerance包的bulkhead_manager模块<br/>Bulkhead Manager<br/>文件: fault_tolerance/bulkhead_manager.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_fault_tolerance_chaos_engine_py["—4注入点×月度执行<br/>Chaos 故障注入引擎<br/>（CT-CHAOS-001）——4注入点×月度执行。<br/>Chaos Engine<br/>文件: fault_tolerance/chaos_engine.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_fault_tolerance_fault_types_py["Fault类型定义<br/>Fault type registry and preset templates for<br/>chaos engineering.<br/>Fault Types<br/>文件: fault_tolerance/fault_types.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_file_task_mapper_py["文件任务Mapper<br/>FileTaskMapper — 文件路径 ↔ Task N:N 映射器<br/>（#21 裁定重写）<br/>File Task Mapper<br/>文件: orchestrator/file_task_mapper.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_governance_autonomy_guard_py["—Owner离线->自动降级->最小安全运行<br/>Owner 缺位分级自治<br/>（CT-AUTONOMY）——Owner离线->自动降级->最小安全运<br/>行。<br/>Autonomy Guard<br/>文件: governance/autonomy_guard.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_lifecycle_rolling_upgrade_py["—graceful shutdown+流量摘除+health check wait<br/>零停机滚动升级（CT-DEPLOY）——graceful<br/>shutdown+流量摘除+health check wait。<br/>Rolling Upgrade<br/>文件: lifecycle/rolling_upgrade.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_quality_init_py["orchestrator/quality 包入口<br/>quality — orchestrator quality subpackage.<br/>Init<br/>文件: quality/__init__.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_quality_blueprint_scorer_py["对单条 route 计算匹配分数<br/>BlueprintScorer — 蓝图路由统一打分逻辑<br/>Blueprint Scorer<br/>文件: quality/blueprint_scorer.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_resilience_failure_matcher_py["Failure Matcher<br/>FailurePatternMatcher —<br/>任务失败模式识别与纠正建议<br/>文件: resilience/failure_matcher.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_agent_orchestrator_py ~~~ src_zephyr_orchestrator_contracts_alert_handler_py
    src_zephyr_orchestrator_contracts_alert_handler_py ~~~ src_zephyr_orchestrator_contracts_contract_registry_py
    src_zephyr_orchestrator_contracts_contract_registry_py ~~~ src_zephyr_orchestrator_core_task_queue_py
    src_zephyr_orchestrator_core_task_queue_py ~~~ src_zephyr_orchestrator_execution_batch_orchestrator_py
    src_zephyr_orchestrator_execution_batch_orchestrator_py ~~~ src_zephyr_orchestrator_execution_context_bridge_py
    src_zephyr_orchestrator_execution_context_bridge_py ~~~ src_zephyr_orchestrator_execution_memory_writer_py
    src_zephyr_orchestrator_execution_memory_writer_py ~~~ src_zephyr_orchestrator_execution_script_runner_py
    src_zephyr_orchestrator_execution_script_runner_py ~~~ src_zephyr_orchestrator_fault_tolerance_bulkhead_manager_py
    src_zephyr_orchestrator_fault_tolerance_bulkhead_manager_py ~~~ src_zephyr_orchestrator_fault_tolerance_chaos_engine_py
    src_zephyr_orchestrator_fault_tolerance_chaos_engine_py ~~~ src_zephyr_orchestrator_fault_tolerance_fault_types_py
    src_zephyr_orchestrator_fault_tolerance_fault_types_py ~~~ src_zephyr_orchestrator_file_task_mapper_py
    src_zephyr_orchestrator_file_task_mapper_py ~~~ src_zephyr_orchestrator_governance_autonomy_guard_py
    src_zephyr_orchestrator_governance_autonomy_guard_py ~~~ src_zephyr_orchestrator_lifecycle_rolling_upgrade_py
    src_zephyr_orchestrator_lifecycle_rolling_upgrade_py ~~~ src_zephyr_orchestrator_quality_init_py
    src_zephyr_orchestrator_quality_init_py ~~~ src_zephyr_orchestrator_quality_blueprint_scorer_py
    src_zephyr_orchestrator_quality_blueprint_scorer_py ~~~ src_zephyr_orchestrator_resilience_failure_matcher_py
    src_zephyr_orchestrator_execution_task_context_builder_py["任务上下文构建器<br/>CE 任务上下文构建器 — build_from_task() 消费者<br/>Task Context Builder<br/>文件: execution/task_context_builder.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_agent_health_monitor_py -->|导入依赖 / import_depends| src_zephyr_orchestrator_agent_orchestrator_py
    src_zephyr_orchestrator_init_py -->|导入依赖 / import_depends| src_zephyr_orchestrator_contracts_alert_handler_py
    src_zephyr_orchestrator_init_py -->|导入依赖 / import_depends| src_zephyr_orchestrator_execution_context_bridge_py
    src_zephyr_orchestrator_init_py -->|导入依赖 / import_depends| src_zephyr_orchestrator_execution_memory_writer_py
    src_zephyr_orchestrator_init_py -->|导入依赖 / import_depends| src_zephyr_orchestrator_execution_script_runner_py
    src_zephyr_orchestrator_task_queue_py -->|导入依赖 / import_depends| src_zephyr_orchestrator_core_task_queue_py
    src_zephyr_orchestrator_core_init_py -->|config_depends / config_depends| src_zephyr_orchestrator_core_task_queue_py
    src_zephyr_orchestrator_contracts_contract_router_py -->|导入依赖 / import_depends| src_zephyr_orchestrator_contracts_contract_registry_py
    src_zephyr_orchestrator_execution_context_bridge_py -->|导入依赖 / import_depends| src_zephyr_orchestrator_execution_task_context_builder_py
    src_zephyr_orchestrator_execution_init_py -->|config_depends / config_depends| src_zephyr_orchestrator_execution_batch_orchestrator_py
    src_zephyr_orchestrator_execution_trigger_router_py -->|导入依赖 / import_depends| src_zephyr_orchestrator_quality_blueprint_scorer_py
    src_zephyr_orchestrator_fault_tolerance_chaos_hooks_py -->|导入依赖 / import_depends| src_zephyr_orchestrator_fault_tolerance_chaos_engine_py
    src_zephyr_orchestrator_fault_tolerance_chaos_hooks_py -->|导入依赖 / import_depends| src_zephyr_orchestrator_fault_tolerance_fault_types_py
    src_zephyr_orchestrator_fault_tolerance_init_py -->|config_depends / config_depends| src_zephyr_orchestrator_fault_tolerance_bulkhead_manager_py
    src_zephyr_orchestrator_governance_init_py -->|config_depends / config_depends| src_zephyr_orchestrator_governance_autonomy_guard_py
    src_zephyr_orchestrator_lifecycle_state_synchronizer_py -->|导入依赖 / import_depends| src_zephyr_orchestrator_file_task_mapper_py
    src_zephyr_orchestrator_lifecycle_init_py -->|config_depends / config_depends| src_zephyr_orchestrator_lifecycle_rolling_upgrade_py
    src_zephyr_orchestrator_quality_knowledge_freshness_py -->|config_depends / config_depends| src_zephyr_orchestrator_quality_init_py
    src_zephyr_orchestrator_quality_ke_quality_py -->|config_depends / config_depends| src_zephyr_orchestrator_quality_init_py
    src_zephyr_orchestrator_resilience_init_py -->|导入依赖 / import_depends| src_zephyr_orchestrator_resilience_failure_matcher_py
    D_SHARED["共享服务<br/>共享服务，负责跨域共享的工具、协议和基础服务<br/>Shared Services<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_orchestrator_execution_trigger_router_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_orchestrator_contracts_alert_handler_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_orchestrator_rollback_manager_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_orchestrator_rollback_manager_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_orchestrator_execution_wave_generator_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_orchestrator_hallucination_detector_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_orchestrator_lifecycle_state_synchronizer_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_orchestrator_contracts_alert_handler_py -->|导入依赖 / import_depends| D_SHARED
    D_GOV_DRIFT["漂移检测<br/>漂移检测，负责架构漂移检测和漂移告警<br/>Drift Detection<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_orchestrator_execution_trigger_router_py -->|导入依赖 / import_depends| D_GOV_DRIFT
    D_GOVERNANCE["生命周期管理<br/>生命周期管理，负责蓝图/模块<br/>/任务的声明周期管理和元数据治理<br/>Lifecycle Management<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_orchestrator_contracts_finding_bridge_py -->|导入依赖 / import_depends| D_GOVERNANCE
    src_zephyr_orchestrator_execution_script_runner_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_orchestrator_agent_orchestrator_py -->|导入依赖 / import_depends| D_SHARED
    D_SECURITY["对抗验证<br/>对抗验证，负责系统安全对抗测试、漏洞扫描和攻防验<br/>证<br/>Adversarial Validation<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_orchestrator_agent_orchestrator_py -->|导入依赖 / import_depends| D_SECURITY
    D_AUTONOMY_CORE["自治核心<br/>自治核心，负责 AI 自治决策、目标分解和执行编排<br/>Autonomy Core<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_orchestrator_execution_context_bridge_py -->|导入依赖 / import_depends| D_AUTONOMY_CORE
    src_zephyr_orchestrator_file_task_mapper_py -->|导入依赖 / import_depends| D_SHARED
    D_ML_TRAIN["训练<br/>训练，负责模型训练、特征工程和模型评估<br/>Training<br/>跨域节点 / cross-domain<br/>(设计态 / design)"]
    D_ML_TRAIN -.->|runtime / runtime| src_zephyr_orchestrator_governance_model_registry_py
    D_INFRA_RUNTIME["运行时集成<br/>运行时集成，负责组件生命周期编排、启动钩子和运行<br/>时上下文管理<br/>Runtime Integration<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    D_INFRA_RUNTIME -->|导入依赖 / import_depends| src_zephyr_orchestrator_execution_memory_writer_py
    D_FEEDBACK_LOOP["反馈循环引擎<br/>反馈循环引擎，负责系统自我改进闭环：异常检测、根<br/>因诊断、自动修复和自我进化<br/>Feedback Loop Engine<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    D_FEEDBACK_LOOP -->|导入依赖 / import_depends| src_zephyr_orchestrator_contracts_alert_handler_py
    D_GOV_SCRIPTS["脚本治理<br/>脚本治理，负责脚本生命周期管理和脚本质量门禁<br/>Script Governance<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    D_GOV_SCRIPTS -->|导入依赖 / import_depends| src_zephyr_orchestrator_contracts_contract_registry_py
    D_AUTONOMY_CORE -->|导入依赖 / import_depends| src_zephyr_orchestrator_contracts_init_py
    D_TRADING["交易运营<br/>交易运营，负责交易生命周期管理、订单状态和成交处<br/>理<br/>Trading Operations<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    D_TRADING -->|导入依赖 / import_depends| src_zephyr_orchestrator_execution_context_bridge_py
    D_TRADING -->|导入依赖 / import_depends| src_zephyr_orchestrator_execution_script_runner_py
    D_TRADING -->|导入依赖 / import_depends| src_zephyr_orchestrator_core_task_queue_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_orchestrator_init_py,src_zephyr_orchestrator_agent_health_monitor_py,src_zephyr_orchestrator_agent_orchestrator_py,src_zephyr_orchestrator_contracts_init_py,src_zephyr_orchestrator_contracts_alert_handler_py,src_zephyr_orchestrator_contracts_construction_guide_py,src_zephyr_orchestrator_contracts_contract_registry_py,src_zephyr_orchestrator_contracts_contract_router_py,src_zephyr_orchestrator_contracts_design_decisions_py,src_zephyr_orchestrator_contracts_finding_bridge_py,src_zephyr_orchestrator_contracts_prompt_version_py,src_zephyr_orchestrator_core_init_py,src_zephyr_orchestrator_core_task_queue_py,src_zephyr_orchestrator_deferred_queue_py,src_zephyr_orchestrator_execution_init_py,src_zephyr_orchestrator_execution_batch_orchestrator_py,src_zephyr_orchestrator_execution_context_bridge_py,src_zephyr_orchestrator_execution_data_lifecycle_py,src_zephyr_orchestrator_execution_dispatch_table_py,src_zephyr_orchestrator_execution_dlq_manager_py,src_zephyr_orchestrator_execution_memory_writer_py,src_zephyr_orchestrator_execution_phase_executor_py,src_zephyr_orchestrator_execution_reconciliation_loop_py,src_zephyr_orchestrator_execution_script_runner_py,src_zephyr_orchestrator_execution_task_context_builder_py,src_zephyr_orchestrator_execution_trigger_router_py,src_zephyr_orchestrator_execution_wave_generator_py,src_zephyr_orchestrator_fault_tolerance_init_py,src_zephyr_orchestrator_fault_tolerance_bulkhead_manager_py,src_zephyr_orchestrator_fault_tolerance_canary_manager_py,src_zephyr_orchestrator_fault_tolerance_chaos_engine_py,src_zephyr_orchestrator_fault_tolerance_chaos_hooks_py,src_zephyr_orchestrator_fault_tolerance_degrade_cascade_py,src_zephyr_orchestrator_fault_tolerance_disk_guard_py,src_zephyr_orchestrator_fault_tolerance_fault_types_py,src_zephyr_orchestrator_fault_tolerance_network_partition_py,src_zephyr_orchestrator_file_task_mapper_py,src_zephyr_orchestrator_governance_init_py,src_zephyr_orchestrator_governance_autonomy_guard_py,src_zephyr_orchestrator_governance_capacity_budget_py,src_zephyr_orchestrator_governance_dependency_lock_py,src_zephyr_orchestrator_governance_model_registry_py,src_zephyr_orchestrator_governance_path_index_py,src_zephyr_orchestrator_governance_risk_registry_py,src_zephyr_orchestrator_governance_schema_migration_py,src_zephyr_orchestrator_governance_version_manifest_py,src_zephyr_orchestrator_hallucination_detector_py,src_zephyr_orchestrator_lifecycle_init_py,src_zephyr_orchestrator_lifecycle_housekeeping_py,src_zephyr_orchestrator_lifecycle_incident_postmortem_py,src_zephyr_orchestrator_lifecycle_rolling_upgrade_py,src_zephyr_orchestrator_lifecycle_session_conflict_py,src_zephyr_orchestrator_lifecycle_startup_sequencer_py,src_zephyr_orchestrator_lifecycle_state_propagation_py,src_zephyr_orchestrator_lifecycle_state_synchronizer_py,src_zephyr_orchestrator_lifecycle_system_transfer_py,src_zephyr_orchestrator_lifecycle_teardown_manager_py,src_zephyr_orchestrator_quality_init_py,src_zephyr_orchestrator_quality_agent_quality_py,src_zephyr_orchestrator_quality_benchmark_runner_py,src_zephyr_orchestrator_quality_blind_spot_closure_py,src_zephyr_orchestrator_quality_blueprint_scorer_py,src_zephyr_orchestrator_quality_ke_quality_py,src_zephyr_orchestrator_quality_knowledge_freshness_py,src_zephyr_orchestrator_quality_lean_scanner_py,src_zephyr_orchestrator_quality_stability_guard_py,src_zephyr_orchestrator_resilience_init_py,src_zephyr_orchestrator_resilience_failure_matcher_py,src_zephyr_orchestrator_rollback_manager_py,src_zephyr_orchestrator_task_queue_py production
    class src_zephyr_orchestrator_factor_direct_fusion_engine_py,src_zephyr_orchestrator_voting_first_multi_agent_py design
    class D_SHARED,D_GOV_DRIFT,D_GOVERNANCE,D_SECURITY,D_AUTONOMY_CORE,D_INFRA_RUNTIME,D_FEEDBACK_LOOP,D_GOV_SCRIPTS,D_TRADING external_prod
    class D_ML_TRAIN external_design
```

### 运营态的图（仅 design_maturity=production 的模块和域内依赖）

> 仅展示已上线运行的模块（共 70 个），不含跨域外部节点。跨域依赖见下方跨域依赖章节。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    src_zephyr_orchestrator_init_py["zephyr/orchestrator 包入口<br/>管理zephyr.orchestrator子包的加载和懒导入<br/>Init<br/>文件: orchestrator/__init__.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_agent_health_monitor_py["SLO 违规记录模型<br/>AgentHealthMonitor · Agent 健康监控（三态 + 5<br/>项 SLO）<br/>Agent Health Monitor<br/>文件: orchestrator/agent_health_monitor.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_contracts_init_py["orchestrator/contracts 包入口<br/>contracts — orchestrator contracts subpackage.<br/>Init<br/>文件: contracts/__init__.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_contracts_construction_guide_py["Construction Guide<br/>施工指南引擎（Construction Guide）<br/>文件: contracts/construction_guide.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_contracts_contract_router_py["契约路由器<br/>契约路由（Contract Router）<br/>文件: contracts/contract_router.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_contracts_design_decisions_py["Design Decisions<br/>编排/契约包的design_decisions模块<br/>文件: contracts/design_decisions.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_contracts_finding_bridge_py["Finding桥接器<br/>CT-ORC-SCRIPT-001 运行时桥接<br/>Finding Bridge<br/>文件: contracts/finding_bridge.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_contracts_prompt_version_py["—prompt template版本化+部署前diff<br/>AI Prompt 版本控制（CT-PROMPT-VERSION）——prompt<br/>template版本化+部署前diff。<br/>Prompt Version<br/>文件: contracts/prompt_version.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_core_init_py["orchestrator/core 包入口<br/>orchestrator.core — auto-generated package init.<br/>文件: core/__init__.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_deferred_queue_py["WAITING -> READY task scheduler.<br/>DeferredQueue: WAITING -> READY task scheduler.<br/>Deferred Queue<br/>文件: orchestrator/deferred_queue.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_execution_init_py["orchestrator/execution 包入口<br/>execution — orchestrator execution subpackage.<br/>Init<br/>文件: execution/__init__.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_execution_data_lifecycle_py["—8类数据保留策略+每日GC<br/>编排/执行包的data_lifecycle模块<br/>Data Lifecycle<br/>文件: execution/data_lifecycle.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_execution_dispatch_table_py["Dispatch Table<br/>AI Agent 冷启动分派表（Dispatch Table）<br/>文件: execution/dispatch_table.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_execution_dlq_manager_py["只读：messages<br/>DLQ 管理器（Dead Letter Queue Manager —<br/>CT-DLQ-001）<br/>Dlq Manager<br/>文件: execution/dlq_manager.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_execution_phase_executor_py["阶段执行器<br/>Phase 执行引擎（Phase Executor）<br/>文件: execution/phase_executor.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_execution_reconciliation_loop_py["只读：results<br/>编排/执行包的reconciliation_loop模块<br/>Reconciliation Loop<br/>文件: execution/reconciliation_loop.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_execution_trigger_router_py["触发路由审计日志 duck-typed 接口<br/>TriggerRouter — RI-03 触发路由器（M3<br/>跨模块触发分派）<br/>Trigger Router<br/>文件: execution/trigger_router.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_execution_wave_generator_py["Wave生成器<br/>WaveGenerator — 根据 Task 依赖图生成执行 Wave<br/>（T-2-03）<br/>Wave Generator<br/>文件: execution/wave_generator.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_fault_tolerance_init_py["orchestrator/fault_tolerance 包入口<br/>fault_tolerance — orchestrator fault_tolerance<br/>subpackage.<br/>Init<br/>文件: fault_tolerance/__init__.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_fault_tolerance_canary_manager_py["—权重分流+指标对比+自动回滚<br/>金丝雀发布管理器<br/>（CT-CANARY）——权重分流+指标对比+自动回滚。<br/>Canary Manager<br/>文件: fault_tolerance/canary_manager.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_fault_tolerance_chaos_hooks_py["混沌Hooks<br/>ChaosHook — integrates ChaosEngine with the<br/>orchestrator execution loop.<br/>Chaos Hooks<br/>文件: fault_tolerance/chaos_hooks.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_fault_tolerance_degrade_cascade_py["—降级传播链检测+熔断<br/>编排/fault tolerance包的degrade_cascade模块<br/>Degrade Cascade<br/>文件: fault_tolerance/degrade_cascade.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_fault_tolerance_disk_guard_py["—剩余空间<5%->告警+只读模式<br/>编排/fault tolerance包的disk_guard模块<br/>Disk Guard<br/>文件: fault_tolerance/disk_guard.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_fault_tolerance_network_partition_py["—CAP定理CP优先+脑裂检测+quorum write<br/>网络分区容忍（CT-NETWORK-PARTITION）——CAP定理CP<br/>优先+脑裂检测+quorum write。<br/>Network Partition<br/>文件: fault_tolerance/network_partition.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_governance_init_py["orchestrator/governance 包入口<br/>governance — orchestrator governance subpackage.<br/>Init<br/>文件: governance/__init__.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_governance_capacity_budget_py["只读：budget<br/>全局容量预算控制器（Capacity Budget Controller）<br/>文件: governance/capacity_budget.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_governance_dependency_lock_py["—Python包版本锁定+hash验证+安全审计<br/>外部依赖版本锁（CT-DEPS）——Python包版本锁定+hash<br/>验证+安全审计。<br/>Dependency Lock<br/>文件: governance/dependency_lock.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_governance_model_registry_py["—deepseek/opus/gpt等模型版本+性能基线<br/>编排/治理包的model_registry模块<br/>Model Registry<br/>文件: governance/model_registry.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_governance_path_index_py["—Module->__init__.py->蓝图->任务卡->配置的完整映<br/>射<br/>编排/治理包的path_index模块<br/>Path Index<br/>文件: governance/path_index.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_governance_risk_registry_py["风险注册表<br/>编排/治理包的risk_registry模块<br/>Risk Registry<br/>文件: governance/risk_registry.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_governance_schema_migration_py["—向后兼容迁移+回滚脚本<br/>数据库 Schema 演化契约<br/>（CT-SCHEMA-MIGRATE）——向后兼容迁移+回滚脚本。<br/>Schema Migration<br/>文件: governance/schema_migration.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_governance_version_manifest_py["—各系统版本号+文件路径索引<br/>编排/治理包的version_manifest模块<br/>Version Manifest<br/>文件: governance/version_manifest.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_hallucination_detector_py["Hallucination检测器<br/>HallucinationDetector · Chain-of-Verification<br/>（CoVe）幻觉检测器<br/>Hallucination Detector<br/>文件: orchestrator/hallucination_detector.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_lifecycle_init_py["orchestrator/lifecycle 包入口<br/>lifecycle — orchestrator lifecycle subpackage.<br/>Init<br/>文件: lifecycle/__init__.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_lifecycle_housekeeping_py["—临时文件扫描+日志轮转+废弃目录清理<br/>文件卫生保洁管理器<br/>（CT-HOUSEKEEPING）——临时文件扫描+日志轮转+废弃<br/>目录清理。<br/>文件: lifecycle/housekeeping.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_lifecycle_incident_postmortem_py["—incident记录+timeline+action_items+postmortem<br/>事件复盘管理器（CT-INCIDENT）——incident记录+time<br/>line+action_items+postmortem。<br/>Incident Postmortem<br/>文件: lifecycle/incident_postmortem.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_lifecycle_session_conflict_py["—文件锁+并发session检测+冲突resolution<br/>Session 冲突预防契约<br/>（CT-SESSION-CONFLICT）——文件锁+并发session检测+<br/>冲突res...<br/>Session Conflict<br/>文件: lifecycle/session_conflict.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_lifecycle_startup_sequencer_py["只读：states<br/>编排/lifecycle包的startup_sequencer模块<br/>Startup Sequencer<br/>文件: lifecycle/startup_sequencer.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_lifecycle_state_propagation_py["状态Propagation<br/>全局状态传播链（State Propagation Chain）<br/>文件: lifecycle/state_propagation.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_lifecycle_state_synchronizer_py["构造 alias fallback 集合<br/>StateSynchronizer — 同步 SQLite<br/>状态与文件系统实际状态（T-2-04）<br/>State Synchronizer<br/>文件: lifecycle/state_synchronizer.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_lifecycle_system_transfer_py["—系统Owner变更+配置迁移+密钥轮转+健康验证<br/>系统移交恢复（CT-TRANSFER）——系统Owner变更+配置<br/>迁移+密钥轮转+健康验证。<br/>System Transfer<br/>文件: lifecycle/system_transfer.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_lifecycle_teardown_manager_py["Teardown管理器<br/>编排/lifecycle包的teardown_manager模块<br/>Teardown Manager<br/>文件: lifecycle/teardown_manager.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_quality_agent_quality_py["—task完成质量评分+agent绩效追踪<br/>AI Agent 质量反馈闭环<br/>（CT-AGENT-QUALITY）——task完成质量评分+agent绩效<br/>追踪。<br/>Agent Quality<br/>文件: quality/agent_quality.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_quality_benchmark_runner_py["—13条CT-*基准数据+回归告警<br/>编排/quality包的benchmark_runner模块<br/>Benchmark Runner<br/>文件: quality/benchmark_runner.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_quality_blind_spot_closure_py["—Round 5 B-MOD-301~335 全三批关闭<br/>编排/quality包的blind_spot_closure模块<br/>Blind Spot Closure<br/>文件: quality/blind_spot_closure.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_quality_ke_quality_py["—KE完整性+准确性+时效性三维评分<br/>知识质量评分契约<br/>（CT-KE-QUALITY）——KE完整性+准确性+时效性三维评<br/>分。<br/>Ke Quality<br/>文件: quality/ke_quality.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_quality_knowledge_freshness_py["—KE过期标记+自动失效<br/>知识新鲜度废止管理器<br/>（CT-KNOWLEDGE-FRESHNESS）——KE过期标记+自动失效<br/>。<br/>Knowledge Freshness<br/>文件: quality/knowledge_freshness.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_quality_lean_scanner_py["—三款扫描器+自动化清理建议<br/>死代码/孤儿文件/僵尸引用三扫描<br/>（CT-LEAN）——三款扫描器+自动化清理建议。<br/>Lean Scanner<br/>文件: quality/lean_scanner.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_quality_stability_guard_py["—public API签名锁+breaking change检测<br/>API 稳定性守护（CT-STABILITY）——public<br/>API签名锁+breaking change检测。<br/>Stability Guard<br/>文件: quality/stability_guard.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_resilience_init_py["orchestrator/resilience 包入口<br/>orchestrator.resilience — auto-generated<br/>package init.<br/>文件: resilience/__init__.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_rollback_manager_py["回滚管理器<br/>RollbackManager — 仅调试用途的 DB-state<br/>快照，不用于自动回滚。<br/>Rollback Manager<br/>文件: orchestrator/rollback_manager.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_task_queue_py["任务Queue<br/>ActiveTaskQueue — 后台任务轮询与自动分发<br/>Task Queue<br/>文件: orchestrator/task_queue.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_init_py ~~~ src_zephyr_orchestrator_agent_health_monitor_py
    src_zephyr_orchestrator_agent_health_monitor_py ~~~ src_zephyr_orchestrator_contracts_init_py
    src_zephyr_orchestrator_contracts_init_py ~~~ src_zephyr_orchestrator_contracts_construction_guide_py
    src_zephyr_orchestrator_contracts_construction_guide_py ~~~ src_zephyr_orchestrator_contracts_contract_router_py
    src_zephyr_orchestrator_contracts_contract_router_py ~~~ src_zephyr_orchestrator_contracts_design_decisions_py
    src_zephyr_orchestrator_contracts_design_decisions_py ~~~ src_zephyr_orchestrator_contracts_finding_bridge_py
    src_zephyr_orchestrator_contracts_finding_bridge_py ~~~ src_zephyr_orchestrator_contracts_prompt_version_py
    src_zephyr_orchestrator_contracts_prompt_version_py ~~~ src_zephyr_orchestrator_core_init_py
    src_zephyr_orchestrator_core_init_py ~~~ src_zephyr_orchestrator_deferred_queue_py
    src_zephyr_orchestrator_deferred_queue_py ~~~ src_zephyr_orchestrator_execution_init_py
    src_zephyr_orchestrator_execution_init_py ~~~ src_zephyr_orchestrator_execution_data_lifecycle_py
    src_zephyr_orchestrator_execution_data_lifecycle_py ~~~ src_zephyr_orchestrator_execution_dispatch_table_py
    src_zephyr_orchestrator_execution_dispatch_table_py ~~~ src_zephyr_orchestrator_execution_dlq_manager_py
    src_zephyr_orchestrator_execution_dlq_manager_py ~~~ src_zephyr_orchestrator_execution_phase_executor_py
    src_zephyr_orchestrator_execution_phase_executor_py ~~~ src_zephyr_orchestrator_execution_reconciliation_loop_py
    src_zephyr_orchestrator_execution_reconciliation_loop_py ~~~ src_zephyr_orchestrator_execution_trigger_router_py
    src_zephyr_orchestrator_execution_trigger_router_py ~~~ src_zephyr_orchestrator_execution_wave_generator_py
    src_zephyr_orchestrator_execution_wave_generator_py ~~~ src_zephyr_orchestrator_fault_tolerance_init_py
    src_zephyr_orchestrator_fault_tolerance_init_py ~~~ src_zephyr_orchestrator_fault_tolerance_canary_manager_py
    src_zephyr_orchestrator_fault_tolerance_canary_manager_py ~~~ src_zephyr_orchestrator_fault_tolerance_chaos_hooks_py
    src_zephyr_orchestrator_fault_tolerance_chaos_hooks_py ~~~ src_zephyr_orchestrator_fault_tolerance_degrade_cascade_py
    src_zephyr_orchestrator_fault_tolerance_degrade_cascade_py ~~~ src_zephyr_orchestrator_fault_tolerance_disk_guard_py
    src_zephyr_orchestrator_fault_tolerance_disk_guard_py ~~~ src_zephyr_orchestrator_fault_tolerance_network_partition_py
    src_zephyr_orchestrator_fault_tolerance_network_partition_py ~~~ src_zephyr_orchestrator_governance_init_py
    src_zephyr_orchestrator_governance_init_py ~~~ src_zephyr_orchestrator_governance_capacity_budget_py
    src_zephyr_orchestrator_governance_capacity_budget_py ~~~ src_zephyr_orchestrator_governance_dependency_lock_py
    src_zephyr_orchestrator_governance_dependency_lock_py ~~~ src_zephyr_orchestrator_governance_model_registry_py
    src_zephyr_orchestrator_governance_model_registry_py ~~~ src_zephyr_orchestrator_governance_path_index_py
    src_zephyr_orchestrator_governance_path_index_py ~~~ src_zephyr_orchestrator_governance_risk_registry_py
    src_zephyr_orchestrator_governance_risk_registry_py ~~~ src_zephyr_orchestrator_governance_schema_migration_py
    src_zephyr_orchestrator_governance_schema_migration_py ~~~ src_zephyr_orchestrator_governance_version_manifest_py
    src_zephyr_orchestrator_governance_version_manifest_py ~~~ src_zephyr_orchestrator_hallucination_detector_py
    src_zephyr_orchestrator_hallucination_detector_py ~~~ src_zephyr_orchestrator_lifecycle_init_py
    src_zephyr_orchestrator_lifecycle_init_py ~~~ src_zephyr_orchestrator_lifecycle_housekeeping_py
    src_zephyr_orchestrator_lifecycle_housekeeping_py ~~~ src_zephyr_orchestrator_lifecycle_incident_postmortem_py
    src_zephyr_orchestrator_lifecycle_incident_postmortem_py ~~~ src_zephyr_orchestrator_lifecycle_session_conflict_py
    src_zephyr_orchestrator_lifecycle_session_conflict_py ~~~ src_zephyr_orchestrator_lifecycle_startup_sequencer_py
    src_zephyr_orchestrator_lifecycle_startup_sequencer_py ~~~ src_zephyr_orchestrator_lifecycle_state_propagation_py
    src_zephyr_orchestrator_lifecycle_state_propagation_py ~~~ src_zephyr_orchestrator_lifecycle_state_synchronizer_py
    src_zephyr_orchestrator_lifecycle_state_synchronizer_py ~~~ src_zephyr_orchestrator_lifecycle_system_transfer_py
    src_zephyr_orchestrator_lifecycle_system_transfer_py ~~~ src_zephyr_orchestrator_lifecycle_teardown_manager_py
    src_zephyr_orchestrator_lifecycle_teardown_manager_py ~~~ src_zephyr_orchestrator_quality_agent_quality_py
    src_zephyr_orchestrator_quality_agent_quality_py ~~~ src_zephyr_orchestrator_quality_benchmark_runner_py
    src_zephyr_orchestrator_quality_benchmark_runner_py ~~~ src_zephyr_orchestrator_quality_blind_spot_closure_py
    src_zephyr_orchestrator_quality_blind_spot_closure_py ~~~ src_zephyr_orchestrator_quality_ke_quality_py
    src_zephyr_orchestrator_quality_ke_quality_py ~~~ src_zephyr_orchestrator_quality_knowledge_freshness_py
    src_zephyr_orchestrator_quality_knowledge_freshness_py ~~~ src_zephyr_orchestrator_quality_lean_scanner_py
    src_zephyr_orchestrator_quality_lean_scanner_py ~~~ src_zephyr_orchestrator_quality_stability_guard_py
    src_zephyr_orchestrator_quality_stability_guard_py ~~~ src_zephyr_orchestrator_resilience_init_py
    src_zephyr_orchestrator_resilience_init_py ~~~ src_zephyr_orchestrator_rollback_manager_py
    src_zephyr_orchestrator_rollback_manager_py ~~~ src_zephyr_orchestrator_task_queue_py
    src_zephyr_orchestrator_agent_orchestrator_py["代理编排器<br/>AgentOrchestrator · 多角色 Agent<br/>路由、工具链编排与健康监控<br/>Agent Orchestrator<br/>文件: orchestrator/agent_orchestrator.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_contracts_alert_handler_py["Alert处理器<br/>Orc 告警接收器 — handle_alert() 消费者<br/>Alert Handler<br/>文件: contracts/alert_handler.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_contracts_contract_registry_py["契约注册表<br/>集成契约注册表（Contract Registry）<br/>文件: contracts/contract_registry.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_core_task_queue_py["打破 pipeline↔orchestrator 循环依赖的协议接口<br/>ActiveTaskQueue — 后台任务轮询与自动分发<br/>Task Queue<br/>文件: core/task_queue.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_execution_batch_orchestrator_py["多 Worker 批量任务协调器<br/>BatchOrchestrator — 多 Worker 批量任务协调器<br/>（MOD-INF-016）<br/>Batch Orchestrator<br/>文件: execution/batch_orchestrator.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_execution_context_bridge_py["上下文桥接器<br/>Orc->CE 上下文桥接 — request_context() 生产者<br/>Context Bridge<br/>文件: execution/context_bridge.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_execution_memory_writer_py["Orc->VMS 记忆写入器'''<br/>编排/执行包的memory_writer模块<br/>Memory Writer<br/>文件: execution/memory_writer.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_execution_script_runner_py["脚本运行器<br/>Orc->Script 脚本执行器 — run_audit() 生产者<br/>Script Runner<br/>文件: execution/script_runner.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_fault_tolerance_bulkhead_manager_py["—12系统独立资源池<br/>编排/fault tolerance包的bulkhead_manager模块<br/>Bulkhead Manager<br/>文件: fault_tolerance/bulkhead_manager.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_fault_tolerance_chaos_engine_py["—4注入点×月度执行<br/>Chaos 故障注入引擎<br/>（CT-CHAOS-001）——4注入点×月度执行。<br/>Chaos Engine<br/>文件: fault_tolerance/chaos_engine.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_fault_tolerance_fault_types_py["Fault类型定义<br/>Fault type registry and preset templates for<br/>chaos engineering.<br/>Fault Types<br/>文件: fault_tolerance/fault_types.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_file_task_mapper_py["文件任务Mapper<br/>FileTaskMapper — 文件路径 ↔ Task N:N 映射器<br/>（#21 裁定重写）<br/>File Task Mapper<br/>文件: orchestrator/file_task_mapper.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_governance_autonomy_guard_py["—Owner离线->自动降级->最小安全运行<br/>Owner 缺位分级自治<br/>（CT-AUTONOMY）——Owner离线->自动降级->最小安全运<br/>行。<br/>Autonomy Guard<br/>文件: governance/autonomy_guard.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_lifecycle_rolling_upgrade_py["—graceful shutdown+流量摘除+health check wait<br/>零停机滚动升级（CT-DEPLOY）——graceful<br/>shutdown+流量摘除+health check wait。<br/>Rolling Upgrade<br/>文件: lifecycle/rolling_upgrade.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_quality_init_py["orchestrator/quality 包入口<br/>quality — orchestrator quality subpackage.<br/>Init<br/>文件: quality/__init__.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_quality_blueprint_scorer_py["对单条 route 计算匹配分数<br/>BlueprintScorer — 蓝图路由统一打分逻辑<br/>Blueprint Scorer<br/>文件: quality/blueprint_scorer.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_resilience_failure_matcher_py["Failure Matcher<br/>FailurePatternMatcher —<br/>任务失败模式识别与纠正建议<br/>文件: resilience/failure_matcher.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_agent_orchestrator_py ~~~ src_zephyr_orchestrator_contracts_alert_handler_py
    src_zephyr_orchestrator_contracts_alert_handler_py ~~~ src_zephyr_orchestrator_contracts_contract_registry_py
    src_zephyr_orchestrator_contracts_contract_registry_py ~~~ src_zephyr_orchestrator_core_task_queue_py
    src_zephyr_orchestrator_core_task_queue_py ~~~ src_zephyr_orchestrator_execution_batch_orchestrator_py
    src_zephyr_orchestrator_execution_batch_orchestrator_py ~~~ src_zephyr_orchestrator_execution_context_bridge_py
    src_zephyr_orchestrator_execution_context_bridge_py ~~~ src_zephyr_orchestrator_execution_memory_writer_py
    src_zephyr_orchestrator_execution_memory_writer_py ~~~ src_zephyr_orchestrator_execution_script_runner_py
    src_zephyr_orchestrator_execution_script_runner_py ~~~ src_zephyr_orchestrator_fault_tolerance_bulkhead_manager_py
    src_zephyr_orchestrator_fault_tolerance_bulkhead_manager_py ~~~ src_zephyr_orchestrator_fault_tolerance_chaos_engine_py
    src_zephyr_orchestrator_fault_tolerance_chaos_engine_py ~~~ src_zephyr_orchestrator_fault_tolerance_fault_types_py
    src_zephyr_orchestrator_fault_tolerance_fault_types_py ~~~ src_zephyr_orchestrator_file_task_mapper_py
    src_zephyr_orchestrator_file_task_mapper_py ~~~ src_zephyr_orchestrator_governance_autonomy_guard_py
    src_zephyr_orchestrator_governance_autonomy_guard_py ~~~ src_zephyr_orchestrator_lifecycle_rolling_upgrade_py
    src_zephyr_orchestrator_lifecycle_rolling_upgrade_py ~~~ src_zephyr_orchestrator_quality_init_py
    src_zephyr_orchestrator_quality_init_py ~~~ src_zephyr_orchestrator_quality_blueprint_scorer_py
    src_zephyr_orchestrator_quality_blueprint_scorer_py ~~~ src_zephyr_orchestrator_resilience_failure_matcher_py
    src_zephyr_orchestrator_execution_task_context_builder_py["任务上下文构建器<br/>CE 任务上下文构建器 — build_from_task() 消费者<br/>Task Context Builder<br/>文件: execution/task_context_builder.py<br/>(生产态 / production)"]
    src_zephyr_orchestrator_agent_health_monitor_py -->|导入依赖 / import_depends| src_zephyr_orchestrator_agent_orchestrator_py
    src_zephyr_orchestrator_init_py -->|导入依赖 / import_depends| src_zephyr_orchestrator_contracts_alert_handler_py
    src_zephyr_orchestrator_init_py -->|导入依赖 / import_depends| src_zephyr_orchestrator_execution_context_bridge_py
    src_zephyr_orchestrator_init_py -->|导入依赖 / import_depends| src_zephyr_orchestrator_execution_memory_writer_py
    src_zephyr_orchestrator_init_py -->|导入依赖 / import_depends| src_zephyr_orchestrator_execution_script_runner_py
    src_zephyr_orchestrator_task_queue_py -->|导入依赖 / import_depends| src_zephyr_orchestrator_core_task_queue_py
    src_zephyr_orchestrator_core_init_py -->|config_depends / config_depends| src_zephyr_orchestrator_core_task_queue_py
    src_zephyr_orchestrator_contracts_contract_router_py -->|导入依赖 / import_depends| src_zephyr_orchestrator_contracts_contract_registry_py
    src_zephyr_orchestrator_execution_context_bridge_py -->|导入依赖 / import_depends| src_zephyr_orchestrator_execution_task_context_builder_py
    src_zephyr_orchestrator_execution_init_py -->|config_depends / config_depends| src_zephyr_orchestrator_execution_batch_orchestrator_py
    src_zephyr_orchestrator_execution_trigger_router_py -->|导入依赖 / import_depends| src_zephyr_orchestrator_quality_blueprint_scorer_py
    src_zephyr_orchestrator_fault_tolerance_chaos_hooks_py -->|导入依赖 / import_depends| src_zephyr_orchestrator_fault_tolerance_chaos_engine_py
    src_zephyr_orchestrator_fault_tolerance_chaos_hooks_py -->|导入依赖 / import_depends| src_zephyr_orchestrator_fault_tolerance_fault_types_py
    src_zephyr_orchestrator_fault_tolerance_init_py -->|config_depends / config_depends| src_zephyr_orchestrator_fault_tolerance_bulkhead_manager_py
    src_zephyr_orchestrator_governance_init_py -->|config_depends / config_depends| src_zephyr_orchestrator_governance_autonomy_guard_py
    src_zephyr_orchestrator_lifecycle_state_synchronizer_py -->|导入依赖 / import_depends| src_zephyr_orchestrator_file_task_mapper_py
    src_zephyr_orchestrator_lifecycle_init_py -->|config_depends / config_depends| src_zephyr_orchestrator_lifecycle_rolling_upgrade_py
    src_zephyr_orchestrator_quality_knowledge_freshness_py -->|config_depends / config_depends| src_zephyr_orchestrator_quality_init_py
    src_zephyr_orchestrator_quality_ke_quality_py -->|config_depends / config_depends| src_zephyr_orchestrator_quality_init_py
    src_zephyr_orchestrator_resilience_init_py -->|导入依赖 / import_depends| src_zephyr_orchestrator_resilience_failure_matcher_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_orchestrator_init_py,src_zephyr_orchestrator_agent_health_monitor_py,src_zephyr_orchestrator_agent_orchestrator_py,src_zephyr_orchestrator_contracts_init_py,src_zephyr_orchestrator_contracts_alert_handler_py,src_zephyr_orchestrator_contracts_construction_guide_py,src_zephyr_orchestrator_contracts_contract_registry_py,src_zephyr_orchestrator_contracts_contract_router_py,src_zephyr_orchestrator_contracts_design_decisions_py,src_zephyr_orchestrator_contracts_finding_bridge_py,src_zephyr_orchestrator_contracts_prompt_version_py,src_zephyr_orchestrator_core_init_py,src_zephyr_orchestrator_core_task_queue_py,src_zephyr_orchestrator_deferred_queue_py,src_zephyr_orchestrator_execution_init_py,src_zephyr_orchestrator_execution_batch_orchestrator_py,src_zephyr_orchestrator_execution_context_bridge_py,src_zephyr_orchestrator_execution_data_lifecycle_py,src_zephyr_orchestrator_execution_dispatch_table_py,src_zephyr_orchestrator_execution_dlq_manager_py,src_zephyr_orchestrator_execution_memory_writer_py,src_zephyr_orchestrator_execution_phase_executor_py,src_zephyr_orchestrator_execution_reconciliation_loop_py,src_zephyr_orchestrator_execution_script_runner_py,src_zephyr_orchestrator_execution_task_context_builder_py,src_zephyr_orchestrator_execution_trigger_router_py,src_zephyr_orchestrator_execution_wave_generator_py,src_zephyr_orchestrator_fault_tolerance_init_py,src_zephyr_orchestrator_fault_tolerance_bulkhead_manager_py,src_zephyr_orchestrator_fault_tolerance_canary_manager_py,src_zephyr_orchestrator_fault_tolerance_chaos_engine_py,src_zephyr_orchestrator_fault_tolerance_chaos_hooks_py,src_zephyr_orchestrator_fault_tolerance_degrade_cascade_py,src_zephyr_orchestrator_fault_tolerance_disk_guard_py,src_zephyr_orchestrator_fault_tolerance_fault_types_py,src_zephyr_orchestrator_fault_tolerance_network_partition_py,src_zephyr_orchestrator_file_task_mapper_py,src_zephyr_orchestrator_governance_init_py,src_zephyr_orchestrator_governance_autonomy_guard_py,src_zephyr_orchestrator_governance_capacity_budget_py,src_zephyr_orchestrator_governance_dependency_lock_py,src_zephyr_orchestrator_governance_model_registry_py,src_zephyr_orchestrator_governance_path_index_py,src_zephyr_orchestrator_governance_risk_registry_py,src_zephyr_orchestrator_governance_schema_migration_py,src_zephyr_orchestrator_governance_version_manifest_py,src_zephyr_orchestrator_hallucination_detector_py,src_zephyr_orchestrator_lifecycle_init_py,src_zephyr_orchestrator_lifecycle_housekeeping_py,src_zephyr_orchestrator_lifecycle_incident_postmortem_py,src_zephyr_orchestrator_lifecycle_rolling_upgrade_py,src_zephyr_orchestrator_lifecycle_session_conflict_py,src_zephyr_orchestrator_lifecycle_startup_sequencer_py,src_zephyr_orchestrator_lifecycle_state_propagation_py,src_zephyr_orchestrator_lifecycle_state_synchronizer_py,src_zephyr_orchestrator_lifecycle_system_transfer_py,src_zephyr_orchestrator_lifecycle_teardown_manager_py,src_zephyr_orchestrator_quality_init_py,src_zephyr_orchestrator_quality_agent_quality_py,src_zephyr_orchestrator_quality_benchmark_runner_py,src_zephyr_orchestrator_quality_blind_spot_closure_py,src_zephyr_orchestrator_quality_blueprint_scorer_py,src_zephyr_orchestrator_quality_ke_quality_py,src_zephyr_orchestrator_quality_knowledge_freshness_py,src_zephyr_orchestrator_quality_lean_scanner_py,src_zephyr_orchestrator_quality_stability_guard_py,src_zephyr_orchestrator_resilience_init_py,src_zephyr_orchestrator_resilience_failure_matcher_py,src_zephyr_orchestrator_rollback_manager_py,src_zephyr_orchestrator_task_queue_py production
```

### 设计态的图（仅 design_maturity=design 的模块和域内依赖）

> 仅展示蓝图阶段、代码未写的设计态模块（共 2 个），不含跨域外部节点。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    src_zephyr_orchestrator_factor_direct_fusion_engine_py["orchestrator/factor_direct_fusion_engine<br/>编排包的factor_direct_fusion_engine模块<br/>文件: orchestrator<br/>/factor_direct_fusion_engine.py<br/>(设计态 / design)"]
    src_zephyr_orchestrator_voting_first_multi_agent_py["orchestrator/voting_first_multi_agent<br/>编排包的voting_first_multi_agent模块<br/>文件: orchestrator/voting_first_multi_agent.py<br/>(设计态 / design)"]
    src_zephyr_orchestrator_factor_direct_fusion_engine_py ~~~ src_zephyr_orchestrator_voting_first_multi_agent_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_orchestrator_factor_direct_fusion_engine_py,src_zephyr_orchestrator_voting_first_multi_agent_py design
```

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

| # | 本域模块 / Source Module | → | 外部域-目标模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | 上下文桥接器 / Context Bridge (execution/context_bridge.py) | → | D_AUTONOMY_CORE 自治核心: 向量写入器 / vector_writer (vector_memory/vector_writer.py) | 导入依赖 / import_depends |
| 2 | Orc->VMS 记忆写入器 / Memory Writer (execution/memory_wri... | → | D_AUTONOMY_CORE 自治核心: 向量桥接 / vector_bridge (context/vector_bridge.py) | 导入依赖 / import_depends |
| 3 | 触发路由审计日志 duck-typed 接口 / Trigger Router (execut... | → | D_FEEDBACK_LOOP 反馈循环引擎: 决策引擎 / Feedback Loop Decision Engine (feedback_loop/d... | 导入依赖 / import_depends |
| 4 | Alert处理器 / Alert Handler (contracts/alert_handler.py) | → | D_GOVERNANCE 生命周期管理: sqlite结构 / sqlite_schema (persistence/sqlite_schema.py) | 导入依赖 / import_depends |
| 5 | Alert处理器 / Alert Handler (contracts/alert_handler.py) | → | D_GOVERNANCE 生命周期管理: 任务repo / task_repo (persistence/task_repo.py) | 导入依赖 / import_depends |
| 6 | Finding桥接器 / Finding Bridge (contracts/finding_bridge.py) | → | D_GOVERNANCE 生命周期管理: 任务repo / task_repo (persistence/task_repo.py) | 导入依赖 / import_depends |
| 7 | 触发路由审计日志 duck-typed 接口 / Trigger Router (execut... | → | D_GOV_DRIFT 漂移检测: ``drift_detected`` 触发器恢复入口 / Drift Detector (rule_... | 导入依赖 / import_depends |
| 8 | Failure Matcher (resilience/failure_matcher.py) | → | D_GOV_OPS_RESILIENCE 运维弹性治理: 声明式事件钩子注册表 / Event Hook (ops_governance/event_h... | 导入依赖 / import_depends |
| 9 | 代理编排器 / Agent Orchestrator (orchestrator/agent_orche... | → | D_INFRA_RUNTIME 运行时集成: Token预算 / Token Budget (capacity_assurance/token_budget... | 导入依赖 / import_depends |
| 10 | 脚本运行器 / Script Runner (execution/script_runner.py) | → | D_INFRA_RUNTIME 运行时集成: 门禁桥接器 / Gate Bridge (script_system/gate_bridge.py) | 导入依赖 / import_depends |
| 11 | Orc->VMS 记忆写入器 / Memory Writer (execution/memory_wri... | → | D_INTEGRATION 管线路由: 只读：store_size / In Memory Fake Vms (vector_memory/in_m... | 导入依赖 / import_depends |
| 12 | 代理编排器 / Agent Orchestrator (orchestrator/agent_orche... | → | D_SECURITY 对抗验证: 网关 / Gateway (llm_security/gateway.py) | 导入依赖 / import_depends |
| 13 | 代理编排器 / Agent Orchestrator (orchestrator/agent_orche... | → | D_SECURITY 对抗验证: 输入净化器 / Input Sanitizer (llm_security/input_sanitize... | 导入依赖 / import_depends |
| 14 | SLO 违规记录模型 / Agent Health Monitor (orchestrator/age... | → | D_SHARED 共享服务: 模式定义 / Schemas (schema/schemas.py) | 导入依赖 / import_depends |
| 15 | SLO 违规记录模型 / Agent Health Monitor (orchestrator/age... | → | D_SHARED 共享服务: 注册 datetime/date→sqlite3 str 适配器 / Time Utils (util... | 导入依赖 / import_depends |
| 16 | 代理编排器 / Agent Orchestrator (orchestrator/agent_orche... | → | D_SHARED 共享服务: 从当前文件向上查找项目根目录 / Paths (io/paths.py) | 导入依赖 / import_depends |
| 17 | 代理编排器 / Agent Orchestrator (orchestrator/agent_orche... | → | D_SHARED 共享服务: 序列化/反序列化过程中类型不兼容或格式错误 / Serialization... | 导入依赖 / import_depends |
| 18 | 代理编排器 / Agent Orchestrator (orchestrator/agent_orche... | → | D_SHARED 共享服务: 模式定义 / Schemas (schema/schemas.py) | 导入依赖 / import_depends |
| 19 | 代理编排器 / Agent Orchestrator (orchestrator/agent_orche... | → | D_SHARED 共享服务: async/sync 边界桥接 / Async Utils (utils/async_utils.py) | 导入依赖 / import_depends |
| 20 | 代理编排器 / Agent Orchestrator (orchestrator/agent_orche... | → | D_SHARED 共享服务: 注册 datetime/date→sqlite3 str 适配器 / Time Utils (util... | 导入依赖 / import_depends |
| 21 | Alert处理器 / Alert Handler (contracts/alert_handler.py) | → | D_SHARED 共享服务: D-ORCH / D-GOV / D-RESILIENCE 通过此接口访问任务持久化 / ... | 导入依赖 / import_depends |
| 22 | Alert处理器 / Alert Handler (contracts/alert_handler.py) | → | D_SHARED 共享服务: 蓝图 MOD-TASK_SYSTEM §3.2.2 / Models (foundation/models.py) | 导入依赖 / import_depends |
| 23 | Alert处理器 / Alert Handler (contracts/alert_handler.py) | → | D_SHARED 共享服务: 基础配置 / Base Config (schema/base_config.py) | 导入依赖 / import_depends |
| 24 | Alert处理器 / Alert Handler (contracts/alert_handler.py) | → | D_SHARED 共享服务: 执行模型 / Execution Model (schema/execution_model.py) | 导入依赖 / import_depends |
| 25 | Alert处理器 / Alert Handler (contracts/alert_handler.py) | → | D_SHARED 共享服务: Severity类型定义 / Severity Types (schema/severity_types.py) | 导入依赖 / import_depends |
| 26 | Alert处理器 / Alert Handler (contracts/alert_handler.py) | → | D_SHARED 共享服务: 任务类型定义 / Task Types (schema/task_types.py) | 导入依赖 / import_depends |
| 27 | Finding桥接器 / Finding Bridge (contracts/finding_bridge.py) | → | D_SHARED 共享服务: 蓝图 MOD-TASK_SYSTEM §3.2.2 / Models (foundation/models.py) | 导入依赖 / import_depends |
| 28 | Finding桥接器 / Finding Bridge (contracts/finding_bridge.py) | → | D_SHARED 共享服务: 从当前文件向上查找项目根目录 / Paths (io/paths.py) | 导入依赖 / import_depends |
| 29 | 打破 pipeline↔orchestrator 循环依赖的协议接口 / Task Que... | → | D_SHARED 共享服务: D-ORCH / D-GOV / D-RESILIENCE 通过此接口访问任务持久化 / ... | 导入依赖 / import_depends |
| 30 | Deferred Queue (orchestrator/deferred_queue.py) | → | D_SHARED 共享服务: 观察者 / Observer (infra/observer.py) | 导入依赖 / import_depends |
| 31 | Deferred Queue (orchestrator/deferred_queue.py) | → | D_SHARED 共享服务: 对连接应用 KBG-0030 §4.3 PRAGMA 基线 / Sqlite Factory (i... | 导入依赖 / import_depends |
| 32 | 多 Worker 批量任务协调器 / Batch Orchestrator (execution/... | → | D_SHARED 共享服务: D-ORCH / D-GOV / D-RESILIENCE 通过此接口访问任务持久化 / ... | 导入依赖 / import_depends |
| 33 | 多 Worker 批量任务协调器 / Batch Orchestrator (execution/... | → | D_SHARED 共享服务: 蓝图 MOD-TASK_SYSTEM §3.2.2 / Models (foundation/models.py) | 导入依赖 / import_depends |
| 34 | Orc->VMS 记忆写入器 / Memory Writer (execution/memory_wri... | → | D_SHARED 共享服务: 序列化/反序列化过程中类型不兼容或格式错误 / Serialization... | 导入依赖 / import_depends |
| 35 | 脚本运行器 / Script Runner (execution/script_runner.py) | → | D_SHARED 共享服务: 返回 Windows 无窗口 creationflags；POSIX 返回 0 / Process... | 导入依赖 / import_depends |
| 36 | 任务上下文构建器 / Task Context Builder (execution/task_c... | → | D_SHARED 共享服务: 模式定义 / Schemas (schema/schemas.py) | 导入依赖 / import_depends |
| 37 | 触发路由审计日志 duck-typed 接口 / Trigger Router (execut... | → | D_SHARED 共享服务: 返回 Windows 无窗口 creationflags；POSIX 返回 0 / Process... | 导入依赖 / import_depends |
| 38 | 触发路由审计日志 duck-typed 接口 / Trigger Router (execut... | → | D_SHARED 共享服务: 从当前文件向上查找项目根目录 / Paths (io/paths.py) | 导入依赖 / import_depends |
| 39 | Wave生成器 / Wave Generator (execution/wave_generator.py) | → | D_SHARED 共享服务: 从当前文件向上查找项目根目录 / Paths (io/paths.py) | 导入依赖 / import_depends |
| 40 | Wave生成器 / Wave Generator (execution/wave_generator.py) | → | D_SHARED 共享服务: 确保数据库 schema 已初始化 / Db Utils (utils/db_utils.py) | 导入依赖 / import_depends |
| 41 | 混沌Hooks / Chaos Hooks (fault_tolerance/chaos_hooks.py) | → | D_SHARED 共享服务: 编排协议 / Orchestration Protocol (contracts/orchestratio... | 导入依赖 / import_depends |
| 42 | 文件任务Mapper / File Task Mapper (orchestrator/file_task... | → | D_SHARED 共享服务: 从当前文件向上查找项目根目录 / Paths (io/paths.py) | 导入依赖 / import_depends |
| 43 | 文件任务Mapper / File Task Mapper (orchestrator/file_task... | → | D_SHARED 共享服务: vocabulary YAML 加载公共工具 / Yaml Utils (io/yaml_utils.py) | 导入依赖 / import_depends |
| 44 | 文件任务Mapper / File Task Mapper (orchestrator/file_task... | → | D_SHARED 共享服务: 任务类型定义 / Task Types (schema/task_types.py) | 导入依赖 / import_depends |
| 45 | 文件任务Mapper / File Task Mapper (orchestrator/file_task... | → | D_SHARED 共享服务: 确保数据库 schema 已初始化 / Db Utils (utils/db_utils.py) | 导入依赖 / import_depends |
| 46 | 文件任务Mapper / File Task Mapper (orchestrator/file_task... | → | D_SHARED 共享服务: 注册 datetime/date→sqlite3 str 适配器 / Time Utils (util... | 导入依赖 / import_depends |
| 47 | Hallucination检测器 / Hallucination Detector (orchestrato... | → | D_SHARED 共享服务: 模式定义 / Schemas (schema/schemas.py) | 导入依赖 / import_depends |
| 48 | Hallucination检测器 / Hallucination Detector (orchestrato... | → | D_SHARED 共享服务: 注册 datetime/date→sqlite3 str 适配器 / Time Utils (util... | 导入依赖 / import_depends |
| 49 | 构造 alias fallback 集合 / State Synchronizer (lifecycle/... | → | D_SHARED 共享服务: 从当前文件向上查找项目根目录 / Paths (io/paths.py) | 导入依赖 / import_depends |
| 50 | 构造 alias fallback 集合 / State Synchronizer (lifecycle/... | → | D_SHARED 共享服务: vocabulary YAML 加载公共工具 / Yaml Utils (io/yaml_utils.py) | 导入依赖 / import_depends |
| 51 | 构造 alias fallback 集合 / State Synchronizer (lifecycle/... | → | D_SHARED 共享服务: 确保数据库 schema 已初始化 / Db Utils (utils/db_utils.py) | 导入依赖 / import_depends |
| 52 | 构造 alias fallback 集合 / State Synchronizer (lifecycle/... | → | D_SHARED 共享服务: 注册 datetime/date→sqlite3 str 适配器 / Time Utils (util... | 导入依赖 / import_depends |
| 53 | 回滚管理器 / Rollback Manager (orchestrator/rollback_mana... | → | D_SHARED 共享服务: 从当前文件向上查找项目根目录 / Paths (io/paths.py) | 导入依赖 / import_depends |
| 54 | 回滚管理器 / Rollback Manager (orchestrator/rollback_mana... | → | D_SHARED 共享服务: 确保数据库 schema 已初始化 / Db Utils (utils/db_utils.py) | 导入依赖 / import_depends |
| 55 | 回滚管理器 / Rollback Manager (orchestrator/rollback_mana... | → | D_SHARED 共享服务: 注册 datetime/date→sqlite3 str 适配器 / Time Utils (util... | 导入依赖 / import_depends |

### 依赖本域的其他域（入边）/ Depended By

| # | 外部域-源模块 / Source Module | → | 本域模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | D_AUTONOMY_CORE 自治核心: 上下文assembler / context_assembler (context/context_asse... | → | 包入口 / Init (contracts/__init__.py) | 导入依赖 / import_depends |
| 2 | D_FEEDBACK_LOOP 反馈循环引擎: alert分发器 / alert_dispatcher (feedback_loop/alert_dispa... | → | Alert处理器 / Alert Handler (contracts/alert_handler.py) | 导入依赖 / import_depends |
| 3 | D_GOV_SCRIPTS 脚本治理: 检查HandoffManifests / Check Handoff Manifests (d1_struct... | → | 契约注册表 / Contract Registry (contracts/contract_regist... | 导入依赖 / import_depends |
| 4 | D_INFRA_RUNTIME 运行时集成: 从 TaskRepository 查询 task 的 source_blueprint，失败返回... | → | Orc->VMS 记忆写入器 / Memory Writer (execution/memory_wri... | 导入依赖 / import_depends |
| 5 | D_ML_TRAIN 训练: 训练管道 / Training Pipeline (training_pipeline/) | → | deepseek/opus/gpt等模型版本+性能基线 / Model Registry (go... | runtime / runtime |
| 6 | D_TRADING 交易运营: 执行 TaskCard 并触发整条基础设施管道 / Auto Dispatcher (t... | → | 打破 pipeline↔orchestrator 循环依赖的协议接口 / Task Que... | 导入依赖 / import_depends |
| 7 | D_TRADING 交易运营: 执行 TaskCard 并触发整条基础设施管道 / Auto Dispatcher (t... | → | 上下文桥接器 / Context Bridge (execution/context_bridge.py) | 导入依赖 / import_depends |
| 8 | D_TRADING 交易运营: 执行 TaskCard 并触发整条基础设施管道 / Auto Dispatcher (t... | → | 脚本运行器 / Script Runner (execution/script_runner.py) | 导入依赖 / import_depends |

### 跨域依赖图 / Cross-domain Dependency Diagram

> 本域与 12 个外部域直接连接（出边 55 条 + 入边 8 条 = 63 条）。只显示直接连接的域，不展开具体节点。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
graph LR
    D_ORCHESTRATOR["D_ORCHESTRATOR<br/>代理编排器"]
    D_SHARED["D_SHARED<br/>共享服务"]
    D_GOVERNANCE["D_GOVERNANCE<br/>生命周期管理"]
    D_AUTONOMY_CORE["D_AUTONOMY_CORE<br/>自治核心"]
    D_INFRA_RUNTIME["D_INFRA_RUNTIME<br/>运行时集成"]
    D_SECURITY["D_SECURITY<br/>对抗验证"]
    D_FEEDBACK_LOOP["D_FEEDBACK_LOOP<br/>反馈循环引擎"]
    D_INTEGRATION["D_INTEGRATION<br/>管线路由"]
    D_GOV_DRIFT["D_GOV_DRIFT<br/>漂移检测"]
    D_GOV_OPS_RESILIENCE["D_GOV_OPS_RESILIENCE<br/>运维弹性治理"]
    D_TRADING["D_TRADING<br/>交易运营"]
    D_GOV_SCRIPTS["D_GOV_SCRIPTS<br/>脚本治理"]
    D_ML_TRAIN["D_ML_TRAIN<br/>训练"]
    D_ORCHESTRATOR -->|42条 导入依赖 / import_depends| D_SHARED
    D_ORCHESTRATOR -->|3条 导入依赖 / import_depends| D_GOVERNANCE
    D_ORCHESTRATOR -->|2条 导入依赖 / import_depends| D_AUTONOMY_CORE
    D_ORCHESTRATOR -->|2条 导入依赖 / import_depends| D_INFRA_RUNTIME
    D_ORCHESTRATOR -->|2条 导入依赖 / import_depends| D_SECURITY
    D_ORCHESTRATOR -->|1条 导入依赖 / import_depends| D_FEEDBACK_LOOP
    D_ORCHESTRATOR -->|1条 导入依赖 / import_depends| D_INTEGRATION
    D_ORCHESTRATOR -->|1条 导入依赖 / import_depends| D_GOV_DRIFT
    D_ORCHESTRATOR -->|1条 导入依赖 / import_depends| D_GOV_OPS_RESILIENCE
    D_TRADING -->|3条 导入依赖 / import_depends| D_ORCHESTRATOR
    D_AUTONOMY_CORE -->|1条 导入依赖 / import_depends| D_ORCHESTRATOR
    D_FEEDBACK_LOOP -->|1条 导入依赖 / import_depends| D_ORCHESTRATOR
    D_GOV_SCRIPTS -->|1条 导入依赖 / import_depends| D_ORCHESTRATOR
    D_INFRA_RUNTIME -->|1条 导入依赖 / import_depends| D_ORCHESTRATOR
    D_ML_TRAIN -->|1条 runtime / runtime| D_ORCHESTRATOR
```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph (PostgreSQL)` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_doc.py`（G2+G10 合并）
- **维护方式 / Maintenance**: 自动生成，全景图更新时刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}.md`，如 `16_d_trading.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[unknown]`=未知
