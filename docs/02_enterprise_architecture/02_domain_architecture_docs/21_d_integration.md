---
doc_type: architecture_view
title: D_INTEGRATION 管线路由架构文档
version: "1.0"
status: active
date: 2026-08-01
owner: auto-generator
ttl: permanent
---

# 21_d_integration / 管线路由域 / Pipeline Routing

> **功能简介 / Overview**: 管线路由，负责跨域数据流路由、管道编排和集成适配

> **文档作用 / Purpose**: 展示 管线路由（D_INTEGRATION）功能域的域内依赖关系、跨域依赖关系，模块信息（成熟度/中英文名/大白话/文件路径）内嵌于 Mermaid 节点，供架构审查和域治理参考。

> 本文档由 generate_domain_doc.py 从 depgraph (PostgreSQL) 自动生成
> 数据源: depgraph (PostgreSQL) nodes表 + edges表

> **[可缩放 HTML 版 / Zoomable HTML](http://localhost:8765/docs/02_enterprise_architecture/02_domain_architecture_docs/_zoomable_html/21_d_integration.html)** — Ctrl+滚轮缩放 ｜ 双击重置 ｜ Ctrl+Shift+D 切换拖动/选择模式

## 域基本信息 / Domain Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 编号 | 21 | Number | 21 |
| 域ID | D_INTEGRATION | Domain ID | D_INTEGRATION |
| 域名称 | 管线路由 | Domain Name | Pipeline Routing |
| 层级 | L1 基础平台层 | Layer | L1 Foundation |
| 模块数 | 71 | Module Count | 71 |
| 域内依赖 | 68 | Internal Dependencies | 68 |
| 跨域入边 | 48 | Cross-domain Incoming | 48 |
| 跨域出边 | 100 | Cross-domain Outgoing | 100 |
| 设计态模块 | 0 | Design Modules | 0 |
| 生产态模块 | 71 | Production Modules | 71 |
| 容量 | 71/150 (正常) | Capacity | 71/150 (正常) |
| 描述 | M1-M11双管线路由 | Description | M1-M11双管线路由 |

## 域内依赖图 / Internal Dependency Diagram

> 依赖图内嵌在本文档中，IDE 可直接渲染；网页版可 Ctrl+滚轮缩放 + 拖动平移查看细节。全景图用颜色区分运营态/设计态，不再分页/拆子图。
>
> **图例说明 / Legend**：
> - 🟦 **蓝色 = 运营态模块**（production，已上线运行）
> - 🟧 **橙色虚线 = 设计态模块**（design，蓝图阶段，代码未写）
> - **实线箭头 = 运营态依赖**（已生效的依赖关系）
> - **虚线箭头 = 非运营态依赖**（计划中/验证中的依赖关系）

### 全景依赖图（全部模块，颜色区分运营态/设计态）

> 展示全部 71 个模块（生产态 71 + 设计态 0），节点含成熟度+中英文名+大白话+文件路径。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    src_zephyr_integration_behavioral_admission_admission_response_py["(生产态 / production)<br/>文件: behavioral_admission/admission_response.py"]
    src_zephyr_integration_budget_enforcer_degradation_spiral_detector_py["(生产态 / production) Degradation Spiral Detector — 模型幻觉-容量正反馈螺旋检测 (盲点 #19, M-29)<br/>Degradation Spiral Detector — 模型幻觉-容量正反馈螺旋检测 (盲点 #19, M-29)<br/>文件: budget_enforcer/degradation_spiral_detector.py"]
    src_zephyr_integration_llm_bridge_py["(生产态 / production) 接收 RED 问题,生成修复文本。LLM 只润色不做判断。不可用时降级为模板生成。<br/>接收 RED 问题,生成修复文本。LLM 只润色不做判断。不可用时降级为模板生成。<br/>文件: integration/llm_bridge.py"]
    src_zephyr_integration_mcp_gateway_server_py["(生产态 / production) MCP Gateway 集中式治理节点（MOD-INF-013 §12 Phase 5）。<br/>MCP Gateway 集中式治理节点（MOD-INF-013 §12 Phase 5）。<br/>文件: mcp/gateway_server.py"]
    src_zephyr_integration_mcp_handoff_auto_loader_py["(生产态 / production) Handoff 自动加载器——从 handoff 包恢复 AI session 上下文（MOD-INF-013 §5.3）。<br/>Handoff 自动加载器——从 handoff 包恢复 AI session 上下文（MOD-INF-013 §5.3）。<br/>文件: mcp/handoff_auto_loader.py"]
    src_zephyr_integration_mcp_prompt_provider_py["(生产态 / production) MCP Prompt 模板提供者（MOD-INF-013 Phase 6 — 关闭 B3）。<br/>MCP Prompt 模板提供者（MOD-INF-013 Phase 6 — 关闭 B3）。<br/>文件: mcp/prompt_provider.py"]
    src_zephyr_integration_mcp_resource_provider_py["(生产态 / production) MCP Resource 提供者（MOD-INF-013 Phase 6 — 关闭 B2/B41）。<br/>MCP Resource 提供者（MOD-INF-013 Phase 6 — 关闭 B2/B41）。<br/>文件: mcp/resource_provider.py"]
    src_zephyr_integration_mcp_rule_discovery_server_py["(生产态 / production) RuleDiscoveryServer — MCP Server for rule discovery（...<br/>RuleDiscoveryServer — MCP Server for rule discovery（...<br/>文件: mcp/rule_discovery_server.py"]
    src_zephyr_integration_mcp_server_py["(生产态 / production) AssetInventory MCP Server — MOD-INF-026 蓝图 §21<br/>AssetInventory MCP Server — MOD-INF-026 蓝图 §21<br/>文件: integration/mcp_server.py"]
    src_zephyr_integration_pipeline_orchestrator_py["(生产态 / production) PipelineOrchestrator — M1-M11 管线协调器<br/>PipelineOrchestrator — M1-M11 管线协调器<br/>文件: integration/pipeline_orchestrator.py"]
    src_zephyr_integration_ports_py["(生产态 / production) Protocol-based interface layer for pipeline->mcp dependency abstraction.<br/>Protocol-based interface layer for pipeline->mcp dependency abstraction.<br/>文件: integration/ports.py"]
    src_zephyr_integration_shared_contracts_errors_contract_violation_error_py["(生产态 / production)<br/>文件: errors/contract_violation_error.py"]
    src_zephyr_integration_shared_contracts_errors_data_quality_error_py["(生产态 / production) CTR-ERR-001: DataQualityError / 行情质量门禁不通过错误<br/>CTR-ERR-001: DataQualityError / 行情质量门禁不通过错误<br/>文件: errors/data_quality_error.py"]
    src_zephyr_integration_shared_contracts_errors_execution_rejection_error_py["(生产态 / production)<br/>文件: errors/execution_rejection_error.py"]
    src_zephyr_integration_shared_contracts_errors_factor_computation_error_py["(生产态 / production) CTR-ERR-002: FactorComputationError / 因子计算失败错误<br/>CTR-ERR-002: FactorComputationError / 因子计算失败错误<br/>文件: errors/factor_computation_error.py"]
    src_zephyr_integration_shared_contracts_errors_risk_limit_violation_error_py["(生产态 / production)<br/>文件: errors/risk_limit_violation_error.py"]
    src_zephyr_integration_shared_contracts_errors_signal_degradation_warning_py["(生产态 / production)<br/>文件: errors/signal_degradation_warning.py"]
    src_zephyr_integration_shared_events_dlq_bridge_py["(生产态 / production) CT-DLQ-001: DeadLetterQueue -> System Event Bus integration bridge.<br/>CT-DLQ-001: DeadLetterQueue -> System Event Bus integration bridge.<br/>文件: events/dlq_bridge.py"]
    src_zephyr_integration_shared_events_event_bus_upgrade_py["(生产态 / production) EventBus Upgrade — 事件总线升级 (M-16)<br/>EventBus Upgrade — 事件总线升级 (M-16)<br/>文件: events/event_bus_upgrade.py"]
    src_zephyr_integration_shared_events_event_schemas_py["(生产态 / production) event_schemas.py —— Observer 事件体 Pydantic V2 Schema（盲点 B6/B10 修复）<br/>event_schemas.py —— Observer 事件体 Pydantic V2 Schema（盲点 B6/B10 修复）<br/>文件: events/event_schemas.py"]
    src_zephyr_integration_shared_events_upgrade_strategy_py["(生产态 / production) EventBus 升级策略引擎<br/>EventBus 升级策略引擎<br/>文件: events/upgrade_strategy.py"]
    src_zephyr_integration_vector_memory_bm25_index_py["(生产态 / production) BM25Index — MOD-INF-011 稀疏检索组件<br/>BM25Index — MOD-INF-011 稀疏检索组件<br/>文件: vector_memory/bm25_index.py"]
    src_zephyr_integration_vector_memory_cache_layer_py["(生产态 / production)<br/>文件: vector_memory/cache_layer.py"]
    src_zephyr_integration_vector_memory_context_ingest_py["(生产态 / production) VMS 上下文注入器 — ingest_context() 消费者<br/>VMS 上下文注入器 — ingest_context() 消费者<br/>文件: vector_memory/context_ingest.py"]
    src_zephyr_integration_vector_memory_cross_collection_retriever_py["(生产态 / production) CrossCollectionRetriever — MOD-INF-011 跨 Collection 联合检索<br/>CrossCollectionRetriever — MOD-INF-011 跨 Collection 联合检索<br/>文件: vector_memory/cross_collection_retriever.py"]
    src_zephyr_integration_vector_memory_delegated_vector_memory_py["(生产态 / production) DelegatedVectorMemory — VectorMemoryBase 的 RI-02 落地适配器<br/>DelegatedVectorMemory — VectorMemoryBase 的 RI-02 落地适配器<br/>文件: vector_memory/delegated_vector_memory.py"]
    src_zephyr_integration_vector_memory_design_principles_py["(生产态 / production)<br/>文件: vector_memory/design_principles.py"]
    src_zephyr_integration_vector_memory_migrate_chroma_to_faiss_py["(生产态 / production) ChromDB -> FAISS + SQLite WAL 数据迁移脚本<br/>ChromDB -> FAISS + SQLite WAL 数据迁移脚本<br/>文件: vector_memory/migrate_chroma_to_faiss.py"]
    src_zephyr_integration_vector_memory_ollama_embedding_py["(生产态 / production)<br/>文件: vector_memory/ollama_embedding.py"]
    src_zephyr_integration_vector_memory_vms_memory_backend_py["(生产态 / production) VMSMemoryBackend — UnifiedMemoryAPI 的 VMS 后端适配器<br/>VMSMemoryBackend — UnifiedMemoryAPI 的 VMS 后端适配器<br/>文件: vector_memory/vms_memory_backend.py"]
    src_zephyr_shared_contracts_approval_types_py["(生产态 / production) G-CT-004 — ApprovalRequest Pydantic V2 BaseModel 审批请求数据结构.<br/>G-CT-004 — ApprovalRequest Pydantic V2 BaseModel 审批请求数据结构.<br/>文件: contracts/approval_types.py"]
    src_zephyr_shared_contracts_rollback_types_py["(生产态 / production) G-CT-003 — RollbackResult Pydantic V2 BaseModel 回滚结果数据结构.<br/>G-CT-003 — RollbackResult Pydantic V2 BaseModel 回滚结果数据结构.<br/>文件: contracts/rollback_types.py"]
    src_zephyr_shared_contracts_runtime_types_py["(生产态 / production)<br/>文件: contracts/runtime_types.py"]
    src_zephyr_shared_evaluation_evals_py["(生产态 / production)<br/>文件: evaluation/evals.py"]
    src_zephyr_shared_resilience_durable_execution_py["(生产态 / production)<br/>文件: resilience/durable_execution.py"]
    src_zephyr_shared_versioning_version_negotiation_py["(生产态 / production)<br/>文件: versioning/version_negotiation.py"]
    src_zephyr_integration_behavioral_admission_admission_response_py ~~~ src_zephyr_integration_budget_enforcer_degradation_spiral_detector_py
    src_zephyr_integration_budget_enforcer_degradation_spiral_detector_py ~~~ src_zephyr_integration_llm_bridge_py
    src_zephyr_integration_llm_bridge_py ~~~ src_zephyr_integration_mcp_gateway_server_py
    src_zephyr_integration_mcp_gateway_server_py ~~~ src_zephyr_integration_mcp_handoff_auto_loader_py
    src_zephyr_integration_mcp_handoff_auto_loader_py ~~~ src_zephyr_integration_mcp_prompt_provider_py
    src_zephyr_integration_mcp_prompt_provider_py ~~~ src_zephyr_integration_mcp_resource_provider_py
    src_zephyr_integration_mcp_resource_provider_py ~~~ src_zephyr_integration_mcp_rule_discovery_server_py
    src_zephyr_integration_mcp_rule_discovery_server_py ~~~ src_zephyr_integration_mcp_server_py
    src_zephyr_integration_mcp_server_py ~~~ src_zephyr_integration_pipeline_orchestrator_py
    src_zephyr_integration_pipeline_orchestrator_py ~~~ src_zephyr_integration_ports_py
    src_zephyr_integration_ports_py ~~~ src_zephyr_integration_shared_contracts_errors_contract_violation_error_py
    src_zephyr_integration_shared_contracts_errors_contract_violation_error_py ~~~ src_zephyr_integration_shared_contracts_errors_data_quality_error_py
    src_zephyr_integration_shared_contracts_errors_data_quality_error_py ~~~ src_zephyr_integration_shared_contracts_errors_execution_rejection_error_py
    src_zephyr_integration_shared_contracts_errors_execution_rejection_error_py ~~~ src_zephyr_integration_shared_contracts_errors_factor_computation_error_py
    src_zephyr_integration_shared_contracts_errors_factor_computation_error_py ~~~ src_zephyr_integration_shared_contracts_errors_risk_limit_violation_error_py
    src_zephyr_integration_shared_contracts_errors_risk_limit_violation_error_py ~~~ src_zephyr_integration_shared_contracts_errors_signal_degradation_warning_py
    src_zephyr_integration_shared_contracts_errors_signal_degradation_warning_py ~~~ src_zephyr_integration_shared_events_dlq_bridge_py
    src_zephyr_integration_shared_events_dlq_bridge_py ~~~ src_zephyr_integration_shared_events_event_bus_upgrade_py
    src_zephyr_integration_shared_events_event_bus_upgrade_py ~~~ src_zephyr_integration_shared_events_event_schemas_py
    src_zephyr_integration_shared_events_event_schemas_py ~~~ src_zephyr_integration_shared_events_upgrade_strategy_py
    src_zephyr_integration_shared_events_upgrade_strategy_py ~~~ src_zephyr_integration_vector_memory_bm25_index_py
    src_zephyr_integration_vector_memory_bm25_index_py ~~~ src_zephyr_integration_vector_memory_cache_layer_py
    src_zephyr_integration_vector_memory_cache_layer_py ~~~ src_zephyr_integration_vector_memory_context_ingest_py
    src_zephyr_integration_vector_memory_context_ingest_py ~~~ src_zephyr_integration_vector_memory_cross_collection_retriever_py
    src_zephyr_integration_vector_memory_cross_collection_retriever_py ~~~ src_zephyr_integration_vector_memory_delegated_vector_memory_py
    src_zephyr_integration_vector_memory_delegated_vector_memory_py ~~~ src_zephyr_integration_vector_memory_design_principles_py
    src_zephyr_integration_vector_memory_design_principles_py ~~~ src_zephyr_integration_vector_memory_migrate_chroma_to_faiss_py
    src_zephyr_integration_vector_memory_migrate_chroma_to_faiss_py ~~~ src_zephyr_integration_vector_memory_ollama_embedding_py
    src_zephyr_integration_vector_memory_ollama_embedding_py ~~~ src_zephyr_integration_vector_memory_vms_memory_backend_py
    src_zephyr_integration_vector_memory_vms_memory_backend_py ~~~ src_zephyr_shared_contracts_approval_types_py
    src_zephyr_shared_contracts_approval_types_py ~~~ src_zephyr_shared_contracts_rollback_types_py
    src_zephyr_shared_contracts_rollback_types_py ~~~ src_zephyr_shared_contracts_runtime_types_py
    src_zephyr_shared_contracts_runtime_types_py ~~~ src_zephyr_shared_evaluation_evals_py
    src_zephyr_shared_evaluation_evals_py ~~~ src_zephyr_shared_resilience_durable_execution_py
    src_zephyr_shared_resilience_durable_execution_py ~~~ src_zephyr_shared_versioning_version_negotiation_py
    src_zephyr_integration_local_model_cache_layer_py["(生产态 / production) CacheLayer — MOD-INF-011 嵌入缓存与查询结果 LRU<br/>CacheLayer — MOD-INF-011 嵌入缓存与查询结果 LRU<br/>文件: local_model/cache_layer.py"]
    src_zephyr_integration_local_model_local_model_scheduler_py["(生产态 / production) LocalModelScheduler — L2 本地模型 24/7 调度循环<br/>LocalModelScheduler — L2 本地模型 24/7 调度循环<br/>文件: local_model/local_model_scheduler.py"]
    src_zephyr_integration_local_model_ollama_embedding_py["(生产态 / production) OllamaEmbedder — 通过 Ollama HTTP API 生成文本嵌入<br/>OllamaEmbedder — 通过 Ollama HTTP API 生成文本嵌入<br/>文件: local_model/ollama_embedding.py"]
    src_zephyr_integration_mcp_audit_logger_py["(生产态 / production) MCP 全量工具调用审计日志（MOD-INF-013 §12 Step 4）。<br/>MCP 全量工具调用审计日志（MOD-INF-013 §12 Step 4）。<br/>文件: mcp/audit_logger.py"]
    src_zephyr_integration_mcp_blueprint_search_server_py["(生产态 / production) BlueprintSearchServer — MCP Server for blueprint discovery<br/>BlueprintSearchServer — MCP Server for blueprint discovery<br/>文件: mcp/blueprint_search_server.py"]
    src_zephyr_integration_mcp_doc_guard_server_py["(生产态 / production) DocGuardServer: 跨会话交接协议服务 MCP Server<br/>DocGuardServer: 跨会话交接协议服务 MCP Server<br/>文件: mcp/doc_guard_server.py"]
    src_zephyr_integration_mcp_gate_engine_server_py["(生产态 / production) GateEngineServer: 门禁裁决服务 MCP Server<br/>GateEngineServer: 门禁裁决服务 MCP Server<br/>文件: mcp/gate_engine_server.py"]
    src_zephyr_integration_mcp_rate_limiter_py["(生产态 / production) MCP Gateway 同步速率限制器（MOD-INF-013 §12 Step 3）。<br/>MCP Gateway 同步速率限制器（MOD-INF-013 §12 Step 3）。<br/>文件: mcp/rate_limiter.py"]
    src_zephyr_integration_mcp_sandbox_server_py["(生产态 / production) MCP sandbox 安全代码执行沙箱（MOD-INF-013 Phase 7 — 关闭 B4）。<br/>MCP sandbox 安全代码执行沙箱（MOD-INF-013 Phase 7 — 关闭 B4）。<br/>文件: mcp/sandbox_server.py"]
    src_zephyr_integration_mcp_sentinel_server_py["(生产态 / production) SentinelServer: 意图路由哨兵 MCP Server<br/>SentinelServer: 意图路由哨兵 MCP Server<br/>文件: mcp/sentinel_server.py"]
    src_zephyr_integration_mcp_task_manager_server_py["(生产态 / production) ZephyrAlpha MCP Task Manager Server<br/>ZephyrAlpha MCP Task Manager Server<br/>文件: mcp/task_manager_server.py"]
    src_zephyr_integration_mcp_telemetry_server_py["(生产态 / production) ZephyrAlpha MCP Telemetry Server — 系统可观测性 MCP 接口<br/>ZephyrAlpha MCP Telemetry Server — 系统可观测性 MCP 接口<br/>文件: mcp/telemetry_server.py"]
    src_zephyr_integration_mcp_vector_memory_server_py["(生产态 / production) VectorMemoryServer: VMS 向量记忆 MCP Server (MOD-INF-011 v0.7.0)<br/>VectorMemoryServer: VMS 向量记忆 MCP Server (MOD-INF-011 v0.7.0)<br/>文件: mcp/vector_memory_server.py"]
    src_zephyr_integration_vector_memory_bridge_layer_py["(生产态 / production) BridgeLayer — MOD-INF-011 kb/ ↔ VMS 过渡桥接<br/>BridgeLayer — MOD-INF-011 kb/ ↔ VMS 过渡桥接<br/>文件: vector_memory/bridge_layer.py"]
    src_zephyr_integration_vector_memory_collection_schemas_py["(生产态 / production)<br/>文件: vector_memory/collection_schemas.py"]
    src_zephyr_integration_vector_memory_faiss_collection_manager_py["(生产态 / production) FAISSCollectionManager — FAISS HNSW/IVF+PQ 8 Collection 全生命周期管理<br/>FAISSCollectionManager — FAISS HNSW/IVF+PQ 8 Collection 全生命周期管理<br/>文件: vector_memory/faiss_collection_manager.py"]
    src_zephyr_integration_vector_memory_hybrid_retriever_py["(生产态 / production) HybridRetriever — MOD-INF-011 混合检索架构<br/>HybridRetriever — MOD-INF-011 混合检索架构<br/>文件: vector_memory/hybrid_retriever.py"]
    src_zephyr_integration_vector_memory_in_memory_fake_vms_py["(生产态 / production) InMemoryFakeVMS — MOD-INF-011 · 零依赖测试双胞胎<br/>InMemoryFakeVMS — MOD-INF-011 · 零依赖测试双胞胎<br/>文件: vector_memory/in_memory_fake_vms.py"]
    src_zephyr_integration_vector_memory_interface_py["(生产态 / production) VMS — Vector Memory Service 接口基类<br/>VMS — Vector Memory Service 接口基类<br/>文件: vector_memory/interface.py"]
    src_zephyr_integration_vector_memory_provenance_enforcer_py["(生产态 / production) ProvenanceEnforcer — MOD-INF-011 写入溯源强制执行<br/>ProvenanceEnforcer — MOD-INF-011 写入溯源强制执行<br/>文件: vector_memory/provenance_enforcer.py"]
    src_zephyr_integration_vector_memory_sqlite_metadata_store_py["(生产态 / production) SQLiteMetadataStore — VMS 元数据存储 (SQLite WAL + FTS5 BM25)<br/>SQLiteMetadataStore — VMS 元数据存储 (SQLite WAL + FTS5 BM25)<br/>文件: vector_memory/sqlite_metadata_store.py"]
    src_zephyr_integration_vector_memory_vms_schemas_py["(生产态 / production) VMS 共享数据模型 — MOD-INF-011 · 蓝图 §6.1 接口契约<br/>VMS 共享数据模型 — MOD-INF-011 · 蓝图 §6.1 接口契约<br/>文件: vector_memory/vms_schemas.py"]
    src_zephyr_shared_contracts_protocols_py["(生产态 / production) Structural Protocol interfaces for cross-module contracts.<br/>Structural Protocol interfaces for cross-module contracts.<br/>文件: contracts/protocols.py"]
    src_zephyr_integration_local_model_cache_layer_py ~~~ src_zephyr_integration_local_model_local_model_scheduler_py
    src_zephyr_integration_local_model_local_model_scheduler_py ~~~ src_zephyr_integration_local_model_ollama_embedding_py
    src_zephyr_integration_local_model_ollama_embedding_py ~~~ src_zephyr_integration_mcp_audit_logger_py
    src_zephyr_integration_mcp_audit_logger_py ~~~ src_zephyr_integration_mcp_blueprint_search_server_py
    src_zephyr_integration_mcp_blueprint_search_server_py ~~~ src_zephyr_integration_mcp_doc_guard_server_py
    src_zephyr_integration_mcp_doc_guard_server_py ~~~ src_zephyr_integration_mcp_gate_engine_server_py
    src_zephyr_integration_mcp_gate_engine_server_py ~~~ src_zephyr_integration_mcp_rate_limiter_py
    src_zephyr_integration_mcp_rate_limiter_py ~~~ src_zephyr_integration_mcp_sandbox_server_py
    src_zephyr_integration_mcp_sandbox_server_py ~~~ src_zephyr_integration_mcp_sentinel_server_py
    src_zephyr_integration_mcp_sentinel_server_py ~~~ src_zephyr_integration_mcp_task_manager_server_py
    src_zephyr_integration_mcp_task_manager_server_py ~~~ src_zephyr_integration_mcp_telemetry_server_py
    src_zephyr_integration_mcp_telemetry_server_py ~~~ src_zephyr_integration_mcp_vector_memory_server_py
    src_zephyr_integration_mcp_vector_memory_server_py ~~~ src_zephyr_integration_vector_memory_bridge_layer_py
    src_zephyr_integration_vector_memory_bridge_layer_py ~~~ src_zephyr_integration_vector_memory_collection_schemas_py
    src_zephyr_integration_vector_memory_collection_schemas_py ~~~ src_zephyr_integration_vector_memory_faiss_collection_manager_py
    src_zephyr_integration_vector_memory_faiss_collection_manager_py ~~~ src_zephyr_integration_vector_memory_hybrid_retriever_py
    src_zephyr_integration_vector_memory_hybrid_retriever_py ~~~ src_zephyr_integration_vector_memory_in_memory_fake_vms_py
    src_zephyr_integration_vector_memory_in_memory_fake_vms_py ~~~ src_zephyr_integration_vector_memory_interface_py
    src_zephyr_integration_vector_memory_interface_py ~~~ src_zephyr_integration_vector_memory_provenance_enforcer_py
    src_zephyr_integration_vector_memory_provenance_enforcer_py ~~~ src_zephyr_integration_vector_memory_sqlite_metadata_store_py
    src_zephyr_integration_vector_memory_sqlite_metadata_store_py ~~~ src_zephyr_integration_vector_memory_vms_schemas_py
    src_zephyr_integration_vector_memory_vms_schemas_py ~~~ src_zephyr_shared_contracts_protocols_py
    src_zephyr_integration_local_model_embedding_router_py["(生产态 / production) EmbeddingRouter — MOD-INF-011 双嵌入维度路由<br/>EmbeddingRouter — MOD-INF-011 双嵌入维度路由<br/>文件: local_model/embedding_router.py"]
    src_zephyr_integration_local_model_ollama_chat_py["(生产态 / production) OllamaChat — 通过 Ollama HTTP API 进行本地 LLM 推理<br/>OllamaChat — 通过 Ollama HTTP API 进行本地 LLM 推理<br/>文件: local_model/ollama_chat.py"]
    src_zephyr_integration_mcp_base_server_py["(生产态 / production) BaseMCPServer: stdio 传输 + JSON-RPC 2.0 协议基类<br/>BaseMCPServer: stdio 传输 + JSON-RPC 2.0 协议基类<br/>文件: mcp/_base_server.py"]
    src_zephyr_integration_vector_memory_collection_manager_py["(生产态 / production) CollectionManager — MOD-INF-011 八大 Collection 全生命周期管理<br/>CollectionManager — MOD-INF-011 八大 Collection 全生命周期管理<br/>文件: vector_memory/collection_manager.py"]
    src_zephyr_integration_vector_memory_in_process_vector_memory_py["(生产态 / production) InProcessVectorMemory — MOD-INF-011 VMS 统一入口<br/>InProcessVectorMemory — MOD-INF-011 VMS 统一入口<br/>文件: vector_memory/in_process_vector_memory.py"]
    src_zephyr_integration_vector_memory_vms_errors_py["(生产态 / production)<br/>文件: vector_memory/vms_errors.py"]
    src_zephyr_integration_local_model_embedding_router_py ~~~ src_zephyr_integration_local_model_ollama_chat_py
    src_zephyr_integration_local_model_ollama_chat_py ~~~ src_zephyr_integration_mcp_base_server_py
    src_zephyr_integration_mcp_base_server_py ~~~ src_zephyr_integration_vector_memory_collection_manager_py
    src_zephyr_integration_vector_memory_collection_manager_py ~~~ src_zephyr_integration_vector_memory_in_process_vector_memory_py
    src_zephyr_integration_vector_memory_in_process_vector_memory_py ~~~ src_zephyr_integration_vector_memory_vms_errors_py
    src_zephyr_integration_mcp_error_codes_py["(生产态 / production) MCP 错误码集中注册（MOD-INF-013 §3.4）。<br/>MCP 错误码集中注册（MOD-INF-013 §3.4）。<br/>文件: mcp/error_codes.py"]
    src_zephyr_integration_vector_memory_chunk_strategy_router_py["(生产态 / production) ChunkStrategyRouter — MOD-INF-011 分块策略调度<br/>ChunkStrategyRouter — MOD-INF-011 分块策略调度<br/>文件: vector_memory/chunk_strategy_router.py"]
    src_zephyr_integration_vector_memory_in_memory_memory_backend_py["(生产态 / production) DegradedVMSBackend — MOD-INF-011 降级兜底<br/>DegradedVMSBackend — MOD-INF-011 降级兜底<br/>文件: vector_memory/in_memory_memory_backend.py"]
    src_zephyr_integration_vector_memory_index_health_monitor_py["(生产态 / production) IndexHealthMonitor — MOD-INF-011 索引健康自检与自动修复<br/>IndexHealthMonitor — MOD-INF-011 索引健康自检与自动修复<br/>文件: vector_memory/index_health_monitor.py"]
    src_zephyr_integration_vector_memory_retrieval_feedback_py["(生产态 / production) RetrievalFeedback — MOD-INF-011 FLE 检索质量消费<br/>RetrievalFeedback — MOD-INF-011 FLE 检索质量消费<br/>文件: vector_memory/retrieval_feedback.py"]
    src_zephyr_integration_vector_memory_vector_bridge_py["(生产态 / production) VectorBridge — MOD-INF-011 CE/KB 外部集成适配器<br/>VectorBridge — MOD-INF-011 CE/KB 外部集成适配器<br/>文件: vector_memory/vector_bridge.py"]
    src_zephyr_integration_vector_memory_chunk_strategy_router_py ~~~ src_zephyr_integration_vector_memory_in_memory_memory_backend_py
    src_zephyr_integration_vector_memory_in_memory_memory_backend_py ~~~ src_zephyr_integration_vector_memory_index_health_monitor_py
    src_zephyr_integration_vector_memory_index_health_monitor_py ~~~ src_zephyr_integration_vector_memory_retrieval_feedback_py
    src_zephyr_integration_vector_memory_retrieval_feedback_py ~~~ src_zephyr_integration_vector_memory_vector_bridge_py
    src_zephyr_integration_pipeline_orchestrator_py -->|导入依赖 / import_depends| src_zephyr_integration_local_model_local_model_scheduler_py
    src_zephyr_integration_pipeline_orchestrator_py -->|导入依赖 / import_depends| src_zephyr_integration_local_model_embedding_router_py
    src_zephyr_integration_pipeline_orchestrator_py -->|导入依赖 / import_depends| src_zephyr_shared_contracts_protocols_py
    src_zephyr_integration_local_model_local_model_scheduler_py -->|导入依赖 / import_depends| src_zephyr_integration_local_model_ollama_chat_py
    src_zephyr_integration_local_model_local_model_scheduler_py -->|导入依赖 / import_depends| src_zephyr_integration_local_model_embedding_router_py
    src_zephyr_integration_local_model_embedding_router_py -->|导入依赖 / import_depends| src_zephyr_integration_local_model_ollama_embedding_py
    src_zephyr_integration_mcp_blueprint_search_server_py -->|导入依赖 / import_depends| src_zephyr_integration_mcp_base_server_py
    src_zephyr_integration_mcp_doc_guard_server_py -->|导入依赖 / import_depends| src_zephyr_integration_mcp_base_server_py
    src_zephyr_integration_mcp_gateway_server_py -->|导入依赖 / import_depends| src_zephyr_integration_mcp_audit_logger_py
    src_zephyr_integration_mcp_gateway_server_py -->|导入依赖 / import_depends| src_zephyr_integration_mcp_blueprint_search_server_py
    src_zephyr_integration_mcp_gateway_server_py -->|导入依赖 / import_depends| src_zephyr_integration_mcp_error_codes_py
    src_zephyr_integration_mcp_gateway_server_py -->|导入依赖 / import_depends| src_zephyr_integration_mcp_doc_guard_server_py
    src_zephyr_integration_mcp_gateway_server_py -->|导入依赖 / import_depends| src_zephyr_integration_mcp_rate_limiter_py
    src_zephyr_integration_mcp_gateway_server_py -->|导入依赖 / import_depends| src_zephyr_integration_mcp_gate_engine_server_py
    src_zephyr_integration_mcp_gateway_server_py -->|导入依赖 / import_depends| src_zephyr_integration_mcp_sandbox_server_py
    src_zephyr_integration_mcp_gateway_server_py -->|导入依赖 / import_depends| src_zephyr_integration_mcp_task_manager_server_py
    src_zephyr_integration_mcp_gateway_server_py -->|导入依赖 / import_depends| src_zephyr_integration_mcp_sentinel_server_py
    src_zephyr_integration_mcp_gateway_server_py -->|导入依赖 / import_depends| src_zephyr_integration_mcp_telemetry_server_py
    src_zephyr_integration_mcp_gateway_server_py -->|导入依赖 / import_depends| src_zephyr_integration_mcp_vector_memory_server_py
    src_zephyr_integration_mcp_gateway_server_py -->|导入依赖 / import_depends| src_zephyr_integration_mcp_base_server_py
    src_zephyr_integration_mcp_gate_engine_server_py -->|导入依赖 / import_depends| src_zephyr_integration_mcp_base_server_py
    src_zephyr_integration_mcp_sandbox_server_py -->|导入依赖 / import_depends| src_zephyr_integration_mcp_base_server_py
    src_zephyr_integration_mcp_sentinel_server_py -->|导入依赖 / import_depends| src_zephyr_integration_mcp_base_server_py
    src_zephyr_integration_mcp_rule_discovery_server_py -->|导入依赖 / import_depends| src_zephyr_integration_mcp_base_server_py
    src_zephyr_integration_mcp_vector_memory_server_py -->|导入依赖 / import_depends| src_zephyr_integration_mcp_base_server_py
    src_zephyr_integration_mcp_vector_memory_server_py -->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_collection_manager_py
    src_zephyr_integration_mcp_vector_memory_server_py -->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_in_process_vector_memory_py
    src_zephyr_integration_mcp_vector_memory_server_py -->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_vms_errors_py
    src_zephyr_integration_mcp_base_server_py -->|导入依赖 / import_depends| src_zephyr_integration_mcp_error_codes_py
    src_zephyr_integration_vector_memory_bridge_layer_py -->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_collection_manager_py
    src_zephyr_integration_vector_memory_cache_layer_py -->|导入依赖 / import_depends| src_zephyr_integration_local_model_cache_layer_py
    src_zephyr_integration_vector_memory_collection_manager_py -->|导入依赖 / import_depends| src_zephyr_integration_local_model_embedding_router_py
    src_zephyr_integration_vector_memory_collection_manager_py -->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_collection_schemas_py
    src_zephyr_integration_vector_memory_context_ingest_py -->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_in_memory_fake_vms_py
    src_zephyr_integration_vector_memory_faiss_collection_manager_py -->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_collection_manager_py
    src_zephyr_integration_vector_memory_delegated_vector_memory_py -->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_interface_py
    src_zephyr_integration_vector_memory_hybrid_retriever_py -->|导入依赖 / import_depends| src_zephyr_integration_local_model_embedding_router_py
    src_zephyr_integration_vector_memory_hybrid_retriever_py -->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_collection_manager_py
    src_zephyr_integration_vector_memory_cross_collection_retriever_py -->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_hybrid_retriever_py
    src_zephyr_integration_vector_memory_index_health_monitor_py -->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_collection_manager_py
    src_zephyr_integration_vector_memory_design_principles_py -->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_collection_schemas_py
    src_zephyr_integration_vector_memory_design_principles_py -->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_provenance_enforcer_py
    src_zephyr_integration_vector_memory_design_principles_py -->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_vms_errors_py
    src_zephyr_integration_vector_memory_design_principles_py -->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_vms_schemas_py
    src_zephyr_integration_vector_memory_retrieval_feedback_py -->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_hybrid_retriever_py
    src_zephyr_integration_vector_memory_retrieval_feedback_py -->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_in_process_vector_memory_py
    src_zephyr_integration_vector_memory_provenance_enforcer_py -->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_collection_manager_py
    src_zephyr_integration_vector_memory_provenance_enforcer_py -->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_vms_schemas_py
    src_zephyr_integration_vector_memory_in_process_vector_memory_py -->|导入依赖 / import_depends| src_zephyr_integration_local_model_cache_layer_py
    src_zephyr_integration_vector_memory_in_process_vector_memory_py -->|导入依赖 / import_depends| src_zephyr_integration_local_model_embedding_router_py
    src_zephyr_integration_vector_memory_in_process_vector_memory_py -->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_bridge_layer_py
    src_zephyr_integration_vector_memory_in_process_vector_memory_py -->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_collection_manager_py
    src_zephyr_integration_vector_memory_in_process_vector_memory_py -->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_chunk_strategy_router_py
    src_zephyr_integration_vector_memory_in_process_vector_memory_py -->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_hybrid_retriever_py
    src_zephyr_integration_vector_memory_in_process_vector_memory_py -->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_index_health_monitor_py
    src_zephyr_integration_vector_memory_in_process_vector_memory_py -->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_in_memory_memory_backend_py
    src_zephyr_integration_vector_memory_in_process_vector_memory_py -->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_retrieval_feedback_py
    src_zephyr_integration_vector_memory_in_process_vector_memory_py -->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_provenance_enforcer_py
    src_zephyr_integration_vector_memory_in_process_vector_memory_py -->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_vector_bridge_py
    src_zephyr_integration_vector_memory_ollama_embedding_py -->|导入依赖 / import_depends| src_zephyr_integration_local_model_ollama_embedding_py
    src_zephyr_integration_vector_memory_vector_bridge_py -->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_in_process_vector_memory_py
    src_zephyr_integration_vector_memory_in_memory_fake_vms_py -->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_collection_manager_py
    src_zephyr_integration_vector_memory_migrate_chroma_to_faiss_py -->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_collection_manager_py
    src_zephyr_integration_vector_memory_migrate_chroma_to_faiss_py -->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_faiss_collection_manager_py
    src_zephyr_integration_vector_memory_migrate_chroma_to_faiss_py -->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_sqlite_metadata_store_py
    src_zephyr_integration_vector_memory_vms_memory_backend_py -->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_bridge_layer_py
    src_zephyr_integration_vector_memory_vms_memory_backend_py -->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_in_process_vector_memory_py
    src_zephyr_integration_vector_memory_sqlite_metadata_store_py -->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_collection_manager_py
    D_SHARED["(生产态 / production) 共享服务 / Shared Services<br/>共享服务，负责跨域共享的工具、协议和基础服务<br/>跨域节点 / cross-domain"]
    src_zephyr_integration_vector_memory_hybrid_retriever_py -->|导入依赖 / import_depends| D_SHARED
    D_INFRA_RUNTIME["(生产态 / production) 运行时集成 / Runtime Integration<br/>运行时集成，负责组件生命周期编排、启动钩子和运行时上下文管理<br/>跨域节点 / cross-domain"]
    src_zephyr_integration_local_model_local_model_scheduler_py -->|导入依赖 / import_depends| D_INFRA_RUNTIME
    src_zephyr_integration_shared_events_upgrade_strategy_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_integration_mcp_vector_memory_server_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_integration_mcp_server_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_integration_pipeline_orchestrator_py -->|导入依赖 / import_depends| D_INFRA_RUNTIME
    D_SECURITY["(生产态 / production) 对抗验证 / Adversarial Validation<br/>对抗验证，负责系统安全对抗测试、漏洞扫描和攻防验证<br/>跨域节点 / cross-domain"]
    src_zephyr_integration_mcp_gateway_server_py -->|导入依赖 / import_depends| D_SECURITY
    D_GOVERNANCE["(生产态 / production) 生命周期管理 / Lifecycle Management<br/>生命周期管理，负责蓝图/模块/任务的声明周期管理和元数据治理<br/>跨域节点 / cross-domain"]
    src_zephyr_integration_mcp_base_server_py -->|导入依赖 / import_depends| D_GOVERNANCE
    src_zephyr_integration_shared_events_dlq_bridge_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_integration_shared_contracts_errors_data_quality_error_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_integration_shared_contracts_errors_signal_degradation_warning_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_integration_shared_contracts_errors_factor_computation_error_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_integration_mcp_doc_guard_server_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_integration_mcp_task_manager_server_py -->|导入依赖 / import_depends| D_SHARED
    D_INTELLIGENCE["(生产态 / production) 上下文管理 / Context Management<br/>上下文管理，负责 AI 上下文窗口管理、记忆检索和上下文压缩<br/>跨域节点 / cross-domain"]
    src_zephyr_integration_vector_memory_vms_memory_backend_py -->|导入依赖 / import_depends| D_INTELLIGENCE
    D_GOV_OPS_RESILIENCE["(生产态 / production) 运维弹性治理 / Ops Resilience Governance<br/>运维弹性治理，负责运维治理、安全治理、弹性治理和升级协议<br/>跨域节点 / cross-domain"]
    D_GOV_OPS_RESILIENCE -->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_bridge_layer_py
    D_FEEDBACK_LOOP["(生产态 / production) 反馈循环引擎 / Feedback Loop Engine<br/>反馈循环引擎，负责系统自我改进闭环：异常检测、根因诊断、自动修复和自我进化<br/>跨域节点 / cross-domain"]
    D_FEEDBACK_LOOP -->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_in_process_vector_memory_py
    D_GOVERNANCE -->|导入依赖 / import_depends| src_zephyr_shared_contracts_protocols_py
    D_GOV_DRIFT["(生产态 / production) 漂移检测 / Drift Detection<br/>漂移检测，负责架构漂移检测和漂移告警<br/>跨域节点 / cross-domain"]
    D_GOV_DRIFT -->|导入依赖 / import_depends| src_zephyr_shared_contracts_protocols_py
    D_GOV_ENFORCEMENT["(生产态 / production) 规则执行 / Rule Enforcement<br/>规则执行，负责治理规则执行和门禁拦截<br/>跨域节点 / cross-domain"]
    D_GOV_ENFORCEMENT -->|导入依赖 / import_depends| src_zephyr_shared_contracts_approval_types_py
    D_AUTONOMY_CORE["(生产态 / production) 自治核心 / Autonomy Core<br/>自治核心，负责 AI 自治决策、目标分解和执行编排<br/>跨域节点 / cross-domain"]
    D_AUTONOMY_CORE -->|导入依赖 / import_depends| src_zephyr_shared_contracts_protocols_py
    D_GOV_OPS_RESILIENCE -->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_collection_manager_py
    D_GOV_OPS_RESILIENCE -->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_collection_manager_py
    D_GOV_OPS_RESILIENCE -->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_in_process_vector_memory_py
    D_GOV_OPS_RESILIENCE -->|导入依赖 / import_depends| src_zephyr_shared_contracts_rollback_types_py
    D_GOV_OPS_RESILIENCE -->|导入依赖 / import_depends| src_zephyr_shared_contracts_rollback_types_py
    D_GOV_OPS_RESILIENCE -->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_index_health_monitor_py
    D_INFRA_RUNTIME -->|导入依赖 / import_depends| src_zephyr_integration_local_model_local_model_scheduler_py
    D_GOV_SCRIPTS["(生产态 / production) 脚本治理 / Script Governance<br/>脚本治理，负责脚本生命周期管理和脚本质量门禁<br/>跨域节点 / cross-domain"]
    D_GOV_SCRIPTS -->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_collection_manager_py
    D_GOVERNANCE -->|导入依赖 / import_depends| src_zephyr_integration_mcp_base_server_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_integration_behavioral_admission_admission_response_py,src_zephyr_integration_budget_enforcer_degradation_spiral_detector_py,src_zephyr_integration_llm_bridge_py,src_zephyr_integration_local_model_cache_layer_py,src_zephyr_integration_local_model_embedding_router_py,src_zephyr_integration_local_model_local_model_scheduler_py,src_zephyr_integration_local_model_ollama_chat_py,src_zephyr_integration_local_model_ollama_embedding_py,src_zephyr_integration_mcp_base_server_py,src_zephyr_integration_mcp_audit_logger_py,src_zephyr_integration_mcp_blueprint_search_server_py,src_zephyr_integration_mcp_doc_guard_server_py,src_zephyr_integration_mcp_error_codes_py,src_zephyr_integration_mcp_gate_engine_server_py,src_zephyr_integration_mcp_gateway_server_py,src_zephyr_integration_mcp_handoff_auto_loader_py,src_zephyr_integration_mcp_prompt_provider_py,src_zephyr_integration_mcp_rate_limiter_py,src_zephyr_integration_mcp_resource_provider_py,src_zephyr_integration_mcp_rule_discovery_server_py,src_zephyr_integration_mcp_sandbox_server_py,src_zephyr_integration_mcp_sentinel_server_py,src_zephyr_integration_mcp_task_manager_server_py,src_zephyr_integration_mcp_telemetry_server_py,src_zephyr_integration_mcp_vector_memory_server_py,src_zephyr_integration_mcp_server_py,src_zephyr_integration_pipeline_orchestrator_py,src_zephyr_integration_ports_py,src_zephyr_integration_shared_contracts_errors_contract_violation_error_py,src_zephyr_integration_shared_contracts_errors_data_quality_error_py,src_zephyr_integration_shared_contracts_errors_execution_rejection_error_py,src_zephyr_integration_shared_contracts_errors_factor_computation_error_py,src_zephyr_integration_shared_contracts_errors_risk_limit_violation_error_py,src_zephyr_integration_shared_contracts_errors_signal_degradation_warning_py,src_zephyr_integration_shared_events_dlq_bridge_py,src_zephyr_integration_shared_events_event_bus_upgrade_py,src_zephyr_integration_shared_events_event_schemas_py,src_zephyr_integration_shared_events_upgrade_strategy_py,src_zephyr_integration_vector_memory_bm25_index_py,src_zephyr_integration_vector_memory_bridge_layer_py,src_zephyr_integration_vector_memory_cache_layer_py,src_zephyr_integration_vector_memory_chunk_strategy_router_py,src_zephyr_integration_vector_memory_collection_manager_py,src_zephyr_integration_vector_memory_collection_schemas_py,src_zephyr_integration_vector_memory_context_ingest_py,src_zephyr_integration_vector_memory_cross_collection_retriever_py,src_zephyr_integration_vector_memory_delegated_vector_memory_py,src_zephyr_integration_vector_memory_design_principles_py,src_zephyr_integration_vector_memory_faiss_collection_manager_py,src_zephyr_integration_vector_memory_hybrid_retriever_py,src_zephyr_integration_vector_memory_in_memory_fake_vms_py,src_zephyr_integration_vector_memory_in_memory_memory_backend_py,src_zephyr_integration_vector_memory_in_process_vector_memory_py,src_zephyr_integration_vector_memory_index_health_monitor_py,src_zephyr_integration_vector_memory_interface_py,src_zephyr_integration_vector_memory_migrate_chroma_to_faiss_py,src_zephyr_integration_vector_memory_ollama_embedding_py,src_zephyr_integration_vector_memory_provenance_enforcer_py,src_zephyr_integration_vector_memory_retrieval_feedback_py,src_zephyr_integration_vector_memory_sqlite_metadata_store_py,src_zephyr_integration_vector_memory_vector_bridge_py,src_zephyr_integration_vector_memory_vms_errors_py,src_zephyr_integration_vector_memory_vms_memory_backend_py,src_zephyr_integration_vector_memory_vms_schemas_py,src_zephyr_shared_contracts_approval_types_py,src_zephyr_shared_contracts_protocols_py,src_zephyr_shared_contracts_rollback_types_py,src_zephyr_shared_contracts_runtime_types_py,src_zephyr_shared_evaluation_evals_py,src_zephyr_shared_resilience_durable_execution_py,src_zephyr_shared_versioning_version_negotiation_py production
    class D_SHARED,D_INFRA_RUNTIME,D_SECURITY,D_GOVERNANCE,D_INTELLIGENCE,D_GOV_OPS_RESILIENCE,D_FEEDBACK_LOOP,D_GOV_DRIFT,D_GOV_ENFORCEMENT,D_AUTONOMY_CORE,D_GOV_SCRIPTS external_prod
```

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

| # | 本域模块 / Source Module | → | 外部域-目标模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | SentinelServer: 意图路由哨兵 MCP Server (mcp/sentinel_ser... | → | D_AUTONOMY_CORE 自治核心: IntentKeywordMapper - Stage 1 of three-stage intent parsi... | 导入依赖 / import_depends |
| 2 | PipelineOrchestrator — M1-M11 管线协调器 (integration/pi... | → | D_AUTONOMY_CORE 自治核心: PipelineSkillBridge — Agent Spec -> Pipeline 双向桥接 (i... | 导入依赖 / import_depends |
| 3 | PipelineOrchestrator — M1-M11 管线协调器 (integration/pi... | → | D_AUTONOMY_CORE 自治核心: MOD-INF-019: Agent Spec — Skill Feedback Loop (skills/sk... | 导入依赖 / import_depends |
| 4 | BaseMCPServer: stdio 传输 + JSON-RPC 2.0 协议基类 (mcp/_b... | → | D_GOVERNANCE 生命周期管理: G-CT-007 契约：Budget -> RBAC 配额限制. (agent_spec/rbac_... | 导入依赖 / import_depends |
| 5 | MCP Gateway 集中式治理节点（MOD-INF-013 §12 Phase 5）。 ... | → | D_GOVERNANCE 生命周期管理: GovernanceServer: 治理域统一MCP入口 (mcp/governance_serve... | 导入依赖 / import_depends |
| 6 | ZephyrAlpha MCP Task Manager Server (mcp/task_manager_ser... | → | D_GOVERNANCE 生命周期管理: PathResolver — 模块路径解析器 (architecture_governance/p... | 导入依赖 / import_depends |
| 7 | PipelineOrchestrator — M1-M11 管线协调器 (integration/pi... | → | D_GOVERNANCE 生命周期管理: G-CT-007 契约：Budget -> RBAC 配额限制. (agent_spec/rbac_... | 导入依赖 / import_depends |
| 8 | 接收 RED 问题,生成修复文本。LLM 只润色不做判断。不可用时... | → | D_GOV_AUDIT 审计追踪: 语义审计管线数据模型 — MOD-INF-028 §4.2 (semantic_audit... | 导入依赖 / import_depends |
| 9 | MCP 全量工具调用审计日志（MOD-INF-013 §12 Step 4）。 (mc... | → | D_GOV_AUDIT 审计追踪: gov_audit/writer.py | 导入依赖 / import_depends |
| 10 | PipelineOrchestrator — M1-M11 管线协调器 (integration/pi... | → | D_GOV_AUDIT 审计追踪: gov_audit/writer.py | 导入依赖 / import_depends |
| 11 | ZephyrAlpha MCP Task Manager Server (mcp/task_manager_ser... | → | D_GOV_RULE 规则治理: 任务类型定义 / Task Types (rule_enforcement/task_types.py) | 导入依赖 / import_depends |
| 12 | Structural Protocol interfaces for cross-module contracts... | → | D_GOV_RULE 规则治理: 门禁类型定义 / Gate Types (rule_enforcement/gate_types.py) | 导入依赖 / import_depends |
| 13 | PipelineOrchestrator — M1-M11 管线协调器 (integration/pi... | → | D_INFRA_RECOVERY 回滚恢复: CT-RBK-GATE-001 集成契约落地——Rollback System Exit Code... | 导入依赖 / import_depends |
| 14 | LocalModelScheduler — L2 本地模型 24/7 调度循环 (local_m... | → | D_INFRA_RUNTIME 运行时集成: resource_optimization.py - MAPE-K autonomic resource opti... | 导入依赖 / import_depends |
| 15 | ZephyrAlpha MCP Telemetry Server — 系统可观测性 MCP 接口... | → | D_INFRA_RUNTIME 运行时集成: Telemetry — 系统遥测门面类（MOD-INF-015 v2.1.0） (system... | 导入依赖 / import_depends |
| 16 | PipelineOrchestrator — M1-M11 管线协调器 (integration/pi... | → | D_INFRA_RUNTIME 运行时集成: CircuitBreakerManager -- standalone circuit breaker manag... | 导入依赖 / import_depends |
| 17 | PipelineOrchestrator — M1-M11 管线协调器 (integration/pi... | → | D_INFRA_RUNTIME 运行时集成: CostTracker —— LLM 调用成本追踪器（SRC-0025） (pipeline... | 导入依赖 / import_depends |
| 18 | PipelineOrchestrator — M1-M11 管线协调器 (integration/pi... | → | D_INFRA_RUNTIME 运行时集成: CT-PIPE-ORC-001 — TaskCard -> 管线入口节点路由 (pipeline... | 导入依赖 / import_depends |
| 19 | PipelineOrchestrator — M1-M11 管线协调器 (integration/pi... | → | D_INFRA_RUNTIME 运行时集成: DeadLetterQueue — 死信队列 (pipeline/dead_letter_queue.py) | 导入依赖 / import_depends |
| 20 | PipelineOrchestrator — M1-M11 管线协调器 (integration/pi... | → | D_INFRA_RUNTIME 运行时集成: ModelRouter — 模型路由与降级链管理 (pipeline/model_route... | 导入依赖 / import_depends |
| 21 | PipelineOrchestrator — M1-M11 管线协调器 (integration/pi... | → | D_INFRA_RUNTIME 运行时集成: Pipeline 数据模型 (pipeline/models.py) | 导入依赖 / import_depends |
| 22 | PipelineOrchestrator — M1-M11 管线协调器 (integration/pi... | → | D_INFRA_RUNTIME 运行时集成: Pipeline -> Agent Bridge — 双编排器桥接层 (pipeline/pipe... | 导入依赖 / import_depends |
| 23 | PipelineOrchestrator — M1-M11 管线协调器 (integration/pi... | → | D_INFRA_RUNTIME 运行时集成: Pipeline Lock — 双管线并发锁 (pipeline/pipeline_lock.py) | 导入依赖 / import_depends |
| 24 | PipelineOrchestrator — M1-M11 管线协调器 (integration/pi... | → | D_INFRA_RUNTIME 运行时集成: PreemptionManager -- 优先级抢占管理器 (pipeline/preemptio... | 导入依赖 / import_depends |
| 25 | PipelineOrchestrator — M1-M11 管线协调器 (integration/pi... | → | D_INFRA_RUNTIME 运行时集成: Pipeline Routing Plugin System — K8s Scheduling Framewor... | 导入依赖 / import_depends |
| 26 | PipelineOrchestrator — M1-M11 管线协调器 (integration/pi... | → | D_INFRA_RUNTIME 运行时集成: hooks.py —— 模块生命周期钩子（Phase 2 新增 | 盲点 B8 修... | 导入依赖 / import_depends |
| 27 | PipelineOrchestrator — M1-M11 管线协调器 (integration/pi... | → | D_INTELLIGENCE 上下文管理: Cross-Encoder 重排序层 — BGE-reranker-v2-m3 (model_evalu... | 导入依赖 / import_depends |
| 28 | PipelineOrchestrator — M1-M11 管线协调器 (integration/pi... | → | D_INTELLIGENCE 上下文管理: ModelProfiler — 核心性能分析引擎 (pipeline_routing/profi... | 导入依赖 / import_depends |
| 29 | PipelineOrchestrator — M1-M11 管线协调器 (integration/pi... | → | D_INTELLIGENCE 上下文管理: Results Writer — 持久化 benchmark 结果，支持历史对比（漂... | 导入依赖 / import_depends |
| 30 | DelegatedVectorMemory — VectorMemoryBase 的 RI-02 落地适... | → | D_INTELLIGENCE 上下文管理: UnifiedMemoryAPI — RI-02 统一记忆 API（M2 跨模块封装） (... | 导入依赖 / import_depends |
| 31 | VMSMemoryBackend — UnifiedMemoryAPI 的 VMS 后端适配器 (v... | → | D_INTELLIGENCE 上下文管理: Backend protocol & shared data classes for the unified me... | 导入依赖 / import_depends |
| 32 | VMS 共享数据模型 — MOD-INF-011 · 蓝图 §6.1 接口契约 (v... | → | D_INTELLIGENCE 上下文管理: UnifiedMemoryAPI — RI-02 统一记忆 API（M2 跨模块封装） (... | 导入依赖 / import_depends |
| 33 | OllamaChat — 通过 Ollama HTTP API 进行本地 LLM 推理 (loc... | → | D_OPS 反馈循环: Budget Enforcer core engine — MOD-INF-024 (ops_governanc... | 导入依赖 / import_depends |
| 34 | PipelineOrchestrator — M1-M11 管线协调器 (integration/pi... | → | D_OPS 反馈循环: Budget Enforcer core engine — MOD-INF-024 (ops_governanc... | 导入依赖 / import_depends |
| 35 | PipelineOrchestrator — M1-M11 管线协调器 (integration/pi... | → | D_OPS 反馈循环: Budget Enforcer data models — MOD-INF-024 (ops_governanc... | 导入依赖 / import_depends |
| 36 | MCP Gateway 集中式治理节点（MOD-INF-013 §12 Phase 5）。 ... | → | D_SECURITY 对抗验证: llm_security/gateway.py | 导入依赖 / import_depends |
| 37 | MCP Gateway 集中式治理节点（MOD-INF-013 §12 Phase 5）。 ... | → | D_SECURITY 对抗验证: llm_security/protocol.py | 导入依赖 / import_depends |
| 38 | PipelineOrchestrator — M1-M11 管线协调器 (integration/pi... | → | D_SECURITY 对抗验证: llm_security/gateway.py | 导入依赖 / import_depends |
| 39 | OllamaChat — 通过 Ollama HTTP API 进行本地 LLM 推理 (loc... | → | D_SHARED 共享服务: constants.py —— 共享枚举 & 常量集中 re-export（Single S... | 导入依赖 / import_depends |
| 40 | OllamaEmbedder — 通过 Ollama HTTP API 生成文本嵌入 (loca... | → | D_SHARED 共享服务: constants.py —— 共享枚举 & 常量集中 re-export（Single S... | 导入依赖 / import_depends |
| 41 | BaseMCPServer: stdio 传输 + JSON-RPC 2.0 协议基类 (mcp/_b... | → | D_SHARED 共享服务: async_utils.py — async/sync 边界桥接（5.12.8 修复） (uti... | 导入依赖 / import_depends |
| 42 | MCP 全量工具调用审计日志（MOD-INF-013 §12 Step 4）。 (mc... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 43 | BlueprintSearchServer — MCP Server for blueprint discove... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 44 | DocGuardServer: 跨会话交接协议服务 MCP Server (mcp/doc_gu... | → | D_SHARED 共享服务: schema/schemas.py | 导入依赖 / import_depends |
| 45 | DocGuardServer: 跨会话交接协议服务 MCP Server (mcp/doc_gu... | → | D_SHARED 共享服务: time_utils.py —— 时间/日期工具（Phase 9 新增 | 盲点 B19... | 导入依赖 / import_depends |
| 46 | GateEngineServer: 门禁裁决服务 MCP Server (mcp/gate_engin... | → | D_SHARED 共享服务: schema/schemas.py | 导入依赖 / import_depends |
| 47 | GateEngineServer: 门禁裁决服务 MCP Server (mcp/gate_engin... | → | D_SHARED 共享服务: time_utils.py —— 时间/日期工具（Phase 9 新增 | 盲点 B19... | 导入依赖 / import_depends |
| 48 | MCP Gateway 集中式治理节点（MOD-INF-013 §12 Phase 5）。 ... | → | D_SHARED 共享服务: async_utils.py — async/sync 边界桥接（5.12.8 修复） (uti... | 导入依赖 / import_depends |
| 49 | MCP Gateway 同步速率限制器（MOD-INF-013 §12 Step 3）。 (... | → | D_SHARED 共享服务: infra/limiter.py | 导入依赖 / import_depends |
| 50 | MCP Resource 提供者（MOD-INF-013 Phase 6 — 关闭 B2/B41）... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 51 | RuleDiscoveryServer — MCP Server for rule discovery（...... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 52 | MCP sandbox 安全代码执行沙箱（MOD-INF-013 Phase 7 — 关闭... | → | D_SHARED 共享服务: process_pool.py - Shared process pool for MCP servers and... | 导入依赖 / import_depends |
| 53 | ZephyrAlpha MCP Task Manager Server (mcp/task_manager_ser... | → | D_SHARED 共享服务: ZephyrAlpha 蓝图拆解器 (blueprint_tools/blueprint_decompo... | 导入依赖 / import_depends |
| 54 | ZephyrAlpha MCP Task Manager Server (mcp/task_manager_ser... | → | D_SHARED 共享服务: ZephyrAlpha 任务系统核心数据模型 (foundation/models.py) | 导入依赖 / import_depends |
| 55 | ZephyrAlpha MCP Task Manager Server (mcp/task_manager_ser... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 56 | ZephyrAlpha MCP Task Manager Server (mcp/task_manager_ser... | → | D_SHARED 共享服务: schema/schemas.py | 导入依赖 / import_depends |
| 57 | ZephyrAlpha MCP Task Manager Server (mcp/task_manager_ser... | → | D_SHARED 共享服务: schema/severity_types.py | 导入依赖 / import_depends |
| 58 | ZephyrAlpha MCP Task Manager Server (mcp/task_manager_ser... | → | D_SHARED 共享服务: time_utils.py —— 时间/日期工具（Phase 9 新增 | 盲点 B19... | 导入依赖 / import_depends |
| 59 | ZephyrAlpha MCP Telemetry Server — 系统可观测性 MCP 接口... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 60 | VectorMemoryServer: VMS 向量记忆 MCP Server (MOD-INF-011 ... | → | D_SHARED 共享服务: ports — D-DATA 服务的 Protocol 定义 (protocols/ports.py) | 导入依赖 / import_depends |
| 61 | AssetInventory MCP Server — MOD-INF-026 蓝图 §21 (integ... | → | D_SHARED 共享服务: EventBus — 事件总线（带背压控制）(M-07) (shared/event_bu... | 导入依赖 / import_depends |
| 62 | AssetInventory MCP Server — MOD-INF-026 蓝图 §21 (integ... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 63 | PipelineOrchestrator — M1-M11 管线协调器 (integration/pi... | → | D_SHARED 共享服务: LLMGatewayProtocol — LLM 网关抽象接口 (contracts/llm_gat... | 导入依赖 / import_depends |
| 64 | PipelineOrchestrator — M1-M11 管线协调器 (integration/pi... | → | D_SHARED 共享服务: TaskRepositoryProtocol — TaskRepository 的 Protocol 接口... | 导入依赖 / import_depends |
| 65 | PipelineOrchestrator — M1-M11 管线协调器 (integration/pi... | → | D_SHARED 共享服务: EventBus — 事件总线（带背压控制）(M-07) (shared/event_bu... | 导入依赖 / import_depends |
| 66 | PipelineOrchestrator — M1-M11 管线协调器 (integration/pi... | → | D_SHARED 共享服务: ZephyrAlpha 任务系统核心数据模型 (foundation/models.py) | 导入依赖 / import_depends |
| 67 | PipelineOrchestrator — M1-M11 管线协调器 (integration/pi... | → | D_SHARED 共享服务: Zero-dependency Observer pattern (subscribe/emit/unsubscr... | 导入依赖 / import_depends |
| 68 | PipelineOrchestrator — M1-M11 管线协调器 (integration/pi... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 69 | PipelineOrchestrator — M1-M11 管线协调器 (integration/pi... | → | D_SHARED 共享服务: ports — D-DATA 服务的 Protocol 定义 (protocols/ports.py) | 导入依赖 / import_depends |
| 70 | PipelineOrchestrator — M1-M11 管线协调器 (integration/pi... | → | D_SHARED 共享服务: task_types — 任务系统核心类型 re-export 层 (schema/task_... | 导入依赖 / import_depends |
| 71 | PipelineOrchestrator — M1-M11 管线协调器 (integration/pi... | → | D_SHARED 共享服务: async_utils.py — async/sync 边界桥接（5.12.8 修复） (uti... | 导入依赖 / import_depends |
| 72 | PipelineOrchestrator — M1-M11 管线协调器 (integration/pi... | → | D_SHARED 共享服务: time_utils.py —— 时间/日期工具（Phase 9 新增 | 盲点 B19... | 导入依赖 / import_depends |
| 73 | errors/contract_violation_error.py | → | D_SHARED 共享服务: core/trace_context.py | 导入依赖 / import_depends |
| 74 | CTR-ERR-001: DataQualityError / 行情质量门禁不通过错误 (e... | → | D_SHARED 共享服务: core/trace_context.py | 导入依赖 / import_depends |
| 75 | errors/execution_rejection_error.py | → | D_SHARED 共享服务: core/trace_context.py | 导入依赖 / import_depends |
| 76 | CTR-ERR-002: FactorComputationError / 因子计算失败错误 (e... | → | D_SHARED 共享服务: core/trace_context.py | 导入依赖 / import_depends |
| 77 | errors/risk_limit_violation_error.py | → | D_SHARED 共享服务: core/trace_context.py | 导入依赖 / import_depends |
| 78 | errors/signal_degradation_warning.py | → | D_SHARED 共享服务: core/trace_context.py | 导入依赖 / import_depends |
| 79 | CT-DLQ-001: DeadLetterQueue -> System Event Bus integrati... | → | D_SHARED 共享服务: dlq.py —— ZephyrAlpha 死信队列（Dead Letter Queue） (ev... | 导入依赖 / import_depends |
| 80 | CT-DLQ-001: DeadLetterQueue -> System Event Bus integrati... | → | D_SHARED 共享服务: Zero-dependency Observer pattern (subscribe/emit/unsubscr... | 导入依赖 / import_depends |
| 81 | event_schemas.py —— Observer 事件体 Pydantic V2 Schema... | → | D_SHARED 共享服务: Zero-dependency Observer pattern (subscribe/emit/unsubscr... | 导入依赖 / import_depends |
| 82 | event_schemas.py —— Observer 事件体 Pydantic V2 Schema... | → | D_SHARED 共享服务: schema/base_config.py | 导入依赖 / import_depends |
| 83 | EventBus 升级策略引擎 (events/upgrade_strategy.py) | → | D_SHARED 共享服务: observer.py —— Re-export wrapper -> canonical: zephyr.s... | 导入依赖 / import_depends |
| 84 | ChunkStrategyRouter — MOD-INF-011 分块策略调度 (vector_m... | → | D_SHARED 共享服务: schema/schemas.py | 导入依赖 / import_depends |
| 85 | CollectionManager — MOD-INF-011 八大 Collection 全生命周... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 86 | CollectionManager — MOD-INF-011 八大 Collection 全生命周... | → | D_SHARED 共享服务: schema/schemas.py | 导入依赖 / import_depends |
| 87 | vector_memory/collection_schemas.py | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 88 | vector_memory/collection_schemas.py | → | D_SHARED 共享服务: schema/schemas.py | 导入依赖 / import_depends |
| 89 | HybridRetriever — MOD-INF-011 混合检索架构 (vector_memor... | → | D_SHARED 共享服务: ports — D-DATA 服务的 Protocol 定义 (protocols/ports.py) | 导入依赖 / import_depends |
| 90 | HybridRetriever — MOD-INF-011 混合检索架构 (vector_memor... | → | D_SHARED 共享服务: schema/schemas.py | 导入依赖 / import_depends |
| 91 | IndexHealthMonitor — MOD-INF-011 索引健康自检与自动修复 ... | → | D_SHARED 共享服务: schema/schemas.py | 导入依赖 / import_depends |
| 92 | ChromDB -> FAISS + SQLite WAL 数据迁移脚本 (vector_memory... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 93 | RetrievalFeedback — MOD-INF-011 FLE 检索质量消费 (vector... | → | D_SHARED 共享服务: schema/schemas.py | 导入依赖 / import_depends |
| 94 | SQLiteMetadataStore — VMS 元数据存储 (SQLite WAL + FTS5 ... | → | D_SHARED 共享服务: SQLite 连接工厂真源（SSoT） (io/sqlite_factory.py) | 导入依赖 / import_depends |
| 95 | VectorBridge — MOD-INF-011 CE/KB 外部集成适配器 (vector_... | → | D_SHARED 共享服务: serialization.py —— 统一序列化/反序列化基础设施（Phase ... | 导入依赖 / import_depends |
| 96 | VMS 共享数据模型 — MOD-INF-011 · 蓝图 §6.1 接口契约 (v... | → | D_SHARED 共享服务: schema/schemas.py | 导入依赖 / import_depends |
| 97 | contracts/runtime_types.py | → | D_SHARED 共享服务: constants.py —— 共享枚举 & 常量集中 re-export（Single S... | 导入依赖 / import_depends |
| 98 | contracts/runtime_types.py | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 99 | contracts/runtime_types.py | → | D_SHARED 共享服务: schema/base_config.py | 导入依赖 / import_depends |
| 100 | behavioral_admission/admission_response.py | → | D_TRADING 交易运营: trading/admission_controller.py | 导入依赖 / import_depends |

### 依赖本域的其他域（入边）/ Depended By

| # | 外部域-源模块 / Source Module | → | 本域模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | D_AUTONOMY_CORE 自治核心: skills/skill_executor.py | → | Structural Protocol interfaces for cross-module contracts... | 导入依赖 / import_depends |
| 2 | D_AUTONOMY_CORE 自治核心: skills/skill_router.py | → | EmbeddingRouter — MOD-INF-011 双嵌入维度路由 (local_mode... | 导入依赖 / import_depends |
| 3 | D_AUTONOMY_CORE 自治核心: MOD-INF-019: Agent Spec — SpecEngine 蓝图->Skill 升级引... | → | Structural Protocol interfaces for cross-module contracts... | 导入依赖 / import_depends |
| 4 | D_AUTONOMY_CORE 自治核心: CE 向量写入器 — vectorize_and_store() 生产者 (vector_mem... | → | VMS 上下文注入器 — ingest_context() 消费者 (vector_memor... | 导入依赖 / import_depends |
| 5 | D_FEEDBACK_LOOP 反馈循环引擎: feedback_loop/protocols.py | → | Structural Protocol interfaces for cross-module contracts... | 导入依赖 / import_depends |
| 6 | D_FEEDBACK_LOOP 反馈循环引擎: FLE 全链路调度器 —— collect->detect->diagnose->act->ver... | → | InProcessVectorMemory — MOD-INF-011 VMS 统一入口 (vector... | 导入依赖 / import_depends |
| 7 | D_GOVERNANCE 生命周期管理: local_layer_daemon.py — L2 本地模型层守护进程（薄包装，D... | → | LocalModelScheduler — L2 本地模型 24/7 调度循环 (local_m... | 导入依赖 / import_depends |
| 8 | D_GOVERNANCE 生命周期管理: start_brain.py — ZephyrAlpha 系统大脑一键启动 (construct... | → | contracts/runtime_types.py | 导入依赖 / import_depends |
| 9 | D_GOVERNANCE 生命周期管理: Ollama 入职考试运行脚本 (scripts/run_ollama_exam.py) | → | OllamaChat — 通过 Ollama HTTP API 进行本地 LLM 推理 (loc... | 导入依赖 / import_depends |
| 10 | D_GOVERNANCE 生命周期管理: G-CT-007 — Audit.record_agent_spec() 记录 Agent Spec 注... | → | Structural Protocol interfaces for cross-module contracts... | 导入依赖 / import_depends |
| 11 | D_GOVERNANCE 生命周期管理: GovernanceServer: 治理域统一MCP入口 (mcp/governance_serve... | → | BaseMCPServer: stdio 传输 + JSON-RPC 2.0 协议基类 (mcp/_b... | 导入依赖 / import_depends |
| 12 | D_GOV_DRIFT 漂移检测: Drift Hotfix Bypass — drift_hotfix_bypass.py (gov_drift/... | → | Structural Protocol interfaces for cross-module contracts... | 导入依赖 / import_depends |
| 13 | D_GOV_ENFORCEMENT 规则执行: G-CT-004 — Backward-compat re-export of ApprovalRequest ... | → | G-CT-004 — ApprovalRequest Pydantic V2 BaseModel 审批请... | 导入依赖 / import_depends |
| 14 | D_GOV_OPS_RESILIENCE 运维弹性治理: G-CT-003 消费端 — Escalation.on_rollback_failure() + G-C... | → | G-CT-003 — RollbackResult Pydantic V2 BaseModel 回滚结果... | 导入依赖 / import_depends |
| 15 | D_GOV_OPS_RESILIENCE 运维弹性治理: G-CT-003 — RollbackResult backward-compat re-export faca... | → | G-CT-003 — RollbackResult Pydantic V2 BaseModel 回滚结果... | 导入依赖 / import_depends |
| 16 | D_GOV_OPS_RESILIENCE 运维弹性治理: PhaseManager->GateEngine 检查注册表桥梁 — 44 个阶段门控... | → | BridgeLayer — MOD-INF-011 kb/ ↔ VMS 过渡桥接 (vector_me... | 导入依赖 / import_depends |
| 17 | D_GOV_OPS_RESILIENCE 运维弹性治理: PhaseManager->GateEngine 检查注册表桥梁 — 44 个阶段门控... | → | CollectionManager — MOD-INF-011 八大 Collection 全生命周... | 导入依赖 / import_depends |
| 18 | D_GOV_OPS_RESILIENCE 运维弹性治理: PhaseManager->GateEngine 检查注册表桥梁 — 44 个阶段门控... | → | InProcessVectorMemory — MOD-INF-011 VMS 统一入口 (vector... | 导入依赖 / import_depends |
| 19 | D_GOV_OPS_RESILIENCE 运维弹性治理: PhaseManager->GateEngine 检查注册表桥梁 — 44 个阶段门控... | → | IndexHealthMonitor — MOD-INF-011 索引健康自检与自动修复 ... | 导入依赖 / import_depends |
| 20 | D_GOV_OPS_RESILIENCE 运维弹性治理: PhaseManager->GateEngine 检查注册表桥梁 — 44 个阶段门控... | → | Structural Protocol interfaces for cross-module contracts... | 导入依赖 / import_depends |
| 21 | D_GOV_OPS_RESILIENCE 运维弹性治理: D-DATA -> ServiceRegistry 注册模块 (ops_governance/servic... | → | CollectionManager — MOD-INF-011 八大 Collection 全生命周... | 导入依赖 / import_depends |
| 22 | D_GOV_OPS_RESILIENCE 运维弹性治理: D-DATA -> ServiceRegistry 注册模块 (ops_governance/servic... | → | InProcessVectorMemory — MOD-INF-011 VMS 统一入口 (vector... | 导入依赖 / import_depends |
| 23 | D_GOV_SCRIPTS 脚本治理: VMS Cron 监控器 — MOD-INF-011 · TASK-INF-0224 (vms_ri/v... | → | CollectionManager — MOD-INF-011 八大 Collection 全生命周... | 导入依赖 / import_depends |
| 24 | D_GOV_SCRIPTS 脚本治理: VMS Cron 监控器 — MOD-INF-011 · TASK-INF-0224 (vms_ri/v... | → | IndexHealthMonitor — MOD-INF-011 索引健康自检与自动修复 ... | 导入依赖 / import_depends |
| 25 | D_GOV_SCRIPTS 脚本治理: VMS Health Check 脚本 — MOD-INF-011 · Phase 3 运维自动... | → | CollectionManager — MOD-INF-011 八大 Collection 全生命周... | 导入依赖 / import_depends |
| 26 | D_GOV_SCRIPTS 脚本治理: VMS Health Check 脚本 — MOD-INF-011 · Phase 3 运维自动... | → | IndexHealthMonitor — MOD-INF-011 索引健康自检与自动修复 ... | 导入依赖 / import_depends |
| 27 | D_GOV_SCRIPTS 脚本治理: VMS Phase 2 数据迁移脚本 — MOD-INF-011 (vms_ri/vms_migra... | → | BridgeLayer — MOD-INF-011 kb/ ↔ VMS 过渡桥接 (vector_me... | 导入依赖 / import_depends |
| 28 | D_GOV_SCRIPTS 脚本治理: VMS Phase 2 数据迁移脚本 — MOD-INF-011 (vms_ri/vms_migra... | → | CollectionManager — MOD-INF-011 八大 Collection 全生命周... | 导入依赖 / import_depends |
| 29 | D_GOV_SCRIPTS 脚本治理: VMS 迁移 dry-run 脚本 — MOD-INF-011 Phase 2 前置检查 (vm... | → | BridgeLayer — MOD-INF-011 kb/ ↔ VMS 过渡桥接 (vector_me... | 导入依赖 / import_depends |
| 30 | D_GOV_SCRIPTS 脚本治理: VMS Cron 监控器 — MOD-INF-011 · TASK-INF-0224 (vms/vms_... | → | CollectionManager — MOD-INF-011 八大 Collection 全生命周... | 导入依赖 / import_depends |
| 31 | D_GOV_SCRIPTS 脚本治理: VMS Cron 监控器 — MOD-INF-011 · TASK-INF-0224 (vms/vms_... | → | IndexHealthMonitor — MOD-INF-011 索引健康自检与自动修复 ... | 导入依赖 / import_depends |
| 32 | D_GOV_SCRIPTS 脚本治理: VMS Health Check 脚本 — MOD-INF-011 · Phase 3 运维自动... | → | CollectionManager — MOD-INF-011 八大 Collection 全生命周... | 导入依赖 / import_depends |
| 33 | D_GOV_SCRIPTS 脚本治理: VMS Health Check 脚本 — MOD-INF-011 · Phase 3 运维自动... | → | IndexHealthMonitor — MOD-INF-011 索引健康自检与自动修复 ... | 导入依赖 / import_depends |
| 34 | D_GOV_SCRIPTS 脚本治理: VMS Phase 2 数据迁移脚本 — MOD-INF-011 (vms/vms_migrate.py) | → | BridgeLayer — MOD-INF-011 kb/ ↔ VMS 过渡桥接 (vector_me... | 导入依赖 / import_depends |
| 35 | D_GOV_SCRIPTS 脚本治理: VMS Phase 2 数据迁移脚本 — MOD-INF-011 (vms/vms_migrate.py) | → | CollectionManager — MOD-INF-011 八大 Collection 全生命周... | 导入依赖 / import_depends |
| 36 | D_GOV_SCRIPTS 脚本治理: VMS 迁移 dry-run 脚本 — MOD-INF-011 Phase 2 前置检查 (vm... | → | BridgeLayer — MOD-INF-011 kb/ ↔ VMS 过渡桥接 (vector_me... | 导入依赖 / import_depends |
| 37 | D_INFRA_RUNTIME 运行时集成: DEPRECATED: 此文件已废弃。 (infrastructure/event_bus_upgr... | → | EventBus 升级策略引擎 (events/upgrade_strategy.py) | 导入依赖 / import_depends |
| 38 | D_INFRA_RUNTIME 运行时集成: AutoRuntimeCore — 三层运行时运营中心（系统大脑） (tradin... | → | EmbeddingRouter — MOD-INF-011 双嵌入维度路由 (local_mode... | 导入依赖 / import_depends |
| 39 | D_INFRA_RUNTIME 运行时集成: AutoRuntimeCore — 三层运行时运营中心（系统大脑） (tradin... | → | LocalModelScheduler — L2 本地模型 24/7 调度循环 (local_m... | 导入依赖 / import_depends |
| 40 | D_INFRA_RUNTIME 运行时集成: AutoRuntimeCore — 三层运行时运营中心（系统大脑） (tradin... | → | OllamaChat — 通过 Ollama HTTP API 进行本地 LLM 推理 (loc... | 导入依赖 / import_depends |
| 41 | D_INFRA_RUNTIME 运行时集成: AutoRuntimeCore — 三层运行时运营中心（系统大脑） (tradin... | → | PipelineOrchestrator — M1-M11 管线协调器 (integration/pi... | 导入依赖 / import_depends |
| 42 | D_INFRA_RUNTIME 运行时集成: AutoRuntimeCore — 三层运行时运营中心（系统大脑） (tradin... | → | InProcessVectorMemory — MOD-INF-011 VMS 统一入口 (vector... | 导入依赖 / import_depends |
| 43 | D_INFRA_RUNTIME 运行时集成: AutoTaskGenerator — 自动任务生成器 (trading/auto_task_ge... | → | LocalModelScheduler — L2 本地模型 24/7 调度循环 (local_m... | 导入依赖 / import_depends |
| 44 | D_INFRA_RUNTIME 运行时集成: trading/runtime_config.py | → | contracts/runtime_types.py | 导入依赖 / import_depends |
| 45 | D_INTELLIGENCE 上下文管理: 模型快速能力画像脚本 (P2 三级模式 Quick 入口)。 (scripts/... | → | OllamaChat — 通过 Ollama HTTP API 进行本地 LLM 推理 (loc... | 导入依赖 / import_depends |
| 46 | D_INTELLIGENCE 上下文管理: UnifiedMemoryAPI — RI-02 统一记忆 API（M2 跨模块封装） (... | → | VMSMemoryBackend — UnifiedMemoryAPI 的 VMS 后端适配器 (v... | 导入依赖 / import_depends |
| 47 | D_ORCHESTRATOR 代理编排器: Orc->VMS 记忆写入器 (execution/memory_writer.py) | → | InMemoryFakeVMS — MOD-INF-011 · 零依赖测试双胞胎 (vecto... | 导入依赖 / import_depends |
| 48 | D_TRADING 交易运营: trading/verdict_engine.py | → | LocalModelScheduler — L2 本地模型 24/7 调度循环 (local_m... | 导入依赖 / import_depends |

### 跨域依赖图 / Cross-domain Dependency Diagram

> 本域与 17 个外部域直接连接（出边 100 条 + 入边 48 条 = 148 条）。只显示直接连接的域，不展开具体节点。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
graph LR
    D_INTEGRATION["D_INTEGRATION<br/>管线路由"]
    D_SHARED["D_SHARED<br/>共享服务"]
    D_INFRA_RUNTIME["D_INFRA_RUNTIME<br/>运行时集成"]
    D_INTELLIGENCE["D_INTELLIGENCE<br/>上下文管理"]
    D_GOVERNANCE["D_GOVERNANCE<br/>生命周期管理"]
    D_AUTONOMY_CORE["D_AUTONOMY_CORE<br/>自治核心"]
    D_GOV_AUDIT["D_GOV_AUDIT<br/>审计追踪"]
    D_OPS["D_OPS<br/>反馈循环"]
    D_SECURITY["D_SECURITY<br/>对抗验证"]
    D_GOV_RULE["D_GOV_RULE<br/>规则治理"]
    D_TRADING["D_TRADING<br/>交易运营"]
    D_INFRA_RECOVERY["D_INFRA_RECOVERY<br/>回滚恢复"]
    D_GOV_SCRIPTS["D_GOV_SCRIPTS<br/>脚本治理"]
    D_GOV_OPS_RESILIENCE["D_GOV_OPS_RESILIENCE<br/>运维弹性治理"]
    D_FEEDBACK_LOOP["D_FEEDBACK_LOOP<br/>反馈循环引擎"]
    D_GOV_ENFORCEMENT["D_GOV_ENFORCEMENT<br/>规则执行"]
    D_GOV_DRIFT["D_GOV_DRIFT<br/>漂移检测"]
    D_ORCHESTRATOR["D_ORCHESTRATOR<br/>代理编排器"]
    D_INTEGRATION -->|61条 导入依赖 / import_depends| D_SHARED
    D_INTEGRATION -->|13条 导入依赖 / import_depends| D_INFRA_RUNTIME
    D_INTEGRATION -->|6条 导入依赖 / import_depends| D_INTELLIGENCE
    D_INTEGRATION -->|4条 导入依赖 / import_depends| D_GOVERNANCE
    D_INTEGRATION -->|3条 导入依赖 / import_depends| D_AUTONOMY_CORE
    D_INTEGRATION -->|3条 导入依赖 / import_depends| D_GOV_AUDIT
    D_INTEGRATION -->|3条 导入依赖 / import_depends| D_OPS
    D_INTEGRATION -->|3条 导入依赖 / import_depends| D_SECURITY
    D_INTEGRATION -->|2条 导入依赖 / import_depends| D_GOV_RULE
    D_INTEGRATION -->|1条 导入依赖 / import_depends| D_TRADING
    D_INTEGRATION -->|1条 导入依赖 / import_depends| D_INFRA_RECOVERY
    D_GOV_SCRIPTS -->|14条 导入依赖 / import_depends| D_INTEGRATION
    D_GOV_OPS_RESILIENCE -->|9条 导入依赖 / import_depends| D_INTEGRATION
    D_INFRA_RUNTIME -->|8条 导入依赖 / import_depends| D_INTEGRATION
    D_GOVERNANCE -->|5条 导入依赖 / import_depends| D_INTEGRATION
    D_AUTONOMY_CORE -->|4条 导入依赖 / import_depends| D_INTEGRATION
    D_FEEDBACK_LOOP -->|2条 导入依赖 / import_depends| D_INTEGRATION
    D_INTELLIGENCE -->|2条 导入依赖 / import_depends| D_INTEGRATION
    D_GOV_ENFORCEMENT -->|1条 导入依赖 / import_depends| D_INTEGRATION
    D_GOV_DRIFT -->|1条 导入依赖 / import_depends| D_INTEGRATION
    D_ORCHESTRATOR -->|1条 导入依赖 / import_depends| D_INTEGRATION
    D_TRADING -->|1条 导入依赖 / import_depends| D_INTEGRATION
```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph (PostgreSQL)` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_doc.py`（G2+G10 合并）
- **维护方式 / Maintenance**: 自动生成，全景图更新时刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}.md`，如 `16_d_trading.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[unknown]`=未知
