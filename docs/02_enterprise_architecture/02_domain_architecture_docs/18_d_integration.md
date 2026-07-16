---
doc_type: architecture_view
title: D_INTEGRATION 管线路由架构文档
version: "1.0"
status: active
date: 2026-07-17
owner: auto-generator
ttl: permanent
---

# 18_d_integration / pipeline_routing / 管线路由 / Pipeline Routing

> **功能简介 / Overview**: 管线路由，负责跨域数据流路由、管道编排和集成适配

> **文档作用 / Purpose**: 展示 管线路由（D_INTEGRATION）功能域的模块清单、域内依赖关系、跨域依赖关系、架构分层视图，供架构审查和域治理参考。

> 本文档由 generate_domain_doc.py 从 depgraph (PostgreSQL) 自动生成
> 最后更新: 2026-07-17 03:03:26
> 数据源: depgraph (PostgreSQL) nodes表 + edges表

## 域基本信息 / Domain Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 编号 | 18 | Number | 18 |
| 域ID | D_INTEGRATION | Domain ID | D_INTEGRATION |
| 域名称 | 管线路由 | Domain Name | Pipeline Routing |
| 层级 | L1 基础平台层 | Layer | L1 Foundation |
| 模块数 | 92 | Module Count | 92 |
| 域内依赖 | 98 | Internal Dependencies | 98 |
| 跨域入边 | 141 | Cross-domain Incoming | 141 |
| 跨域出边 | 112 | Cross-domain Outgoing | 112 |
| 设计态模块 | 0 | Design Modules | 0 |
| 原型态模块 | 39 | Prototype Modules | 39 |
| 生产态模块 | 53 | Production Modules | 53 |
| 容量 | 53/150 (正常) | Capacity | 53/150 (正常) |
| 描述 | M1-M11双管线路由 | Description | M1-M11双管线路由 |

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 92 个模块 / 92 modules）。

### L0 基础设施层 / Infrastructure Layer (4 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name (功能简介 / Description) | 成熟度 / Maturity | 蓝图 / Blueprint |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/shared/evaluation/evals.py | evals.py | 生产态 / production | [MOD-GOVERNANCE](../../03_modules/_domain_governance/blueprint.md) |
| 2 | src/zephyr/shared/knowledge/kg_interface.py | kg_interface.py | 生产态 / production | [MOD-GOVERNANCE](../../03_modules/_domain_governance/blueprint.md) |
| 3 | src/zephyr/shared/resilience/durable_execution.py | durable_execution.py | 生产态 / production | [MOD-GOVERNANCE](../../03_modules/_domain_governance/blueprint.md) |
| 4 | src/zephyr/shared/versioning/version_negotiation.py | version_negotiation.py | 生产态 / production | [MOD-GOVERNANCE](../../03_modules/_domain_governance/blueprint.md) |

### L1 基础层 / Foundation Layer (83 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name (功能简介 / Description) | 成熟度 / Maturity | 蓝图 / Blueprint |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/integration/__init__.py | __init__.py | 原型态 / prototype | [MOD-GOVERNANCE](../../03_modules/_domain_governance/blueprint.md) |
| 2 | src/zephyr/integration/behavioral_admission/__init__.py | __init__.py | 原型态 / prototype | [MOD-GOVERNANCE](../../03_modules/_domain_governance/blueprint.md) |
| 3 | src/zephyr/integration/behavioral_admission/admission_res... | admission_response.py | 生产态 / production | [MOD-GOVERNANCE](../../03_modules/_domain_governance/blueprint.md) |
| 4 | src/zephyr/integration/budget_enforcer/__init__.py | __init__.py | 原型态 / prototype | [MOD-INF-001](../../03_modules/_domain_infrastructure_operations/capacity_assurance/blueprint.md) |
| 5 | src/zephyr/integration/budget_enforcer/degradation_spiral... | Degradation Spiral Detector — 模型幻觉-容量正... | 原型态 / prototype | [MOD-INF-001](../../03_modules/_domain_infrastructure_operations/capacity_assurance/blueprint.md) |
| 6 | src/zephyr/integration/llm_bridge.py | 接收 RED 问题,生成修复文本。LLM 只润色不做判断... | 原型态 / prototype | [MOD-INF-028](../../03_modules/_cross_layer/semantic_auditor/blueprint.md) |
| 7 | src/zephyr/integration/local_model/__init__.py | __init__.py | 原型态 / prototype | [MOD-INF-042](../../03_modules/_domain_integration/blueprint.md) |
| 8 | src/zephyr/integration/local_model/cache_layer.py | CacheLayer — MOD-INF-011 嵌入缓存与查询结果 LRU | 生产态 / production | [MOD-INF-042](../../03_modules/_domain_integration/blueprint.md) |
| 9 | src/zephyr/integration/local_model/deepseek_chat.py | DeepSeekChat — 通过 DeepSeek API 进行 LLM 推理... | 生产态 / production | [MOD-INF-042](../../03_modules/_domain_integration/blueprint.md) |
| 10 | src/zephyr/integration/local_model/embedding_router.py | EmbeddingRouter — MOD-INF-011 双嵌入维度路由 | 生产态 / production | [MOD-INF-042](../../03_modules/_domain_integration/blueprint.md) |
| 11 | src/zephyr/integration/local_model/local_model_scheduler.py | LocalModelScheduler — L2 本地模型 24/7 调度循环 | 生产态 / production | [MOD-INF-042](../../03_modules/_domain_integration/blueprint.md) |
| 12 | src/zephyr/integration/local_model/ollama_chat.py | OllamaChat — 通过 Ollama HTTP API 进行本地 LLM... | 生产态 / production | [MOD-INF-042](../../03_modules/_domain_integration/blueprint.md) |
| 13 | src/zephyr/integration/local_model/ollama_embedding.py | OllamaEmbedder — 通过 Ollama HTTP API 生成文本嵌入 | 原型态 / prototype | [MOD-INF-042](../../03_modules/_domain_integration/blueprint.md) |
| 14 | src/zephyr/integration/mcp/_base_server.py | BaseMCPServer: stdio 传输 + JSON-RPC 2.0 协议基类 | 生产态 / production | [MOD-INF-013](../../03_modules/_cross_layer/model_context_protocol_servers/blueprint.md) |
| 15 | src/zephyr/integration/mcp/audit_logger.py | MCP 全量工具调用审计日志（MOD-INF-013 §12 Step... | 生产态 / production | [MOD-INF-013](../../03_modules/_cross_layer/model_context_protocol_servers/blueprint.md) |
| 16 | src/zephyr/integration/mcp/blueprint_search_server.py | BlueprintSearchServer — MCP Server for bluepri... | 生产态 / production | [MOD-INF-013](../../03_modules/_cross_layer/model_context_protocol_servers/blueprint.md) |
| 17 | src/zephyr/integration/mcp/doc_guard_server.py | DocGuardServer: 跨会话交接协议服务 MCP Server | 生产态 / production | [MOD-INF-013](../../03_modules/_cross_layer/model_context_protocol_servers/blueprint.md) |
| 18 | src/zephyr/integration/mcp/error_codes.py | MCP 错误码集中注册（MOD-INF-013 §3.4）。 | 生产态 / production | [MOD-INF-013](../../03_modules/_cross_layer/model_context_protocol_servers/blueprint.md) |
| 19 | src/zephyr/integration/mcp/gate_engine_server.py | GateEngineServer: 门禁裁决服务 MCP Server | 生产态 / production | [MOD-INF-013](../../03_modules/_cross_layer/model_context_protocol_servers/blueprint.md) |
| 20 | src/zephyr/integration/mcp/gateway_server.py | MCP Gateway 集中式治理节点（MOD-INF-013 §12 Ph... | 生产态 / production | [MOD-INF-013](../../03_modules/_cross_layer/model_context_protocol_servers/blueprint.md) |
| 21 | src/zephyr/integration/mcp/handoff_auto_loader.py | Handoff 自动加载器——从 handoff 包恢复 AI sess... | 原型态 / prototype | [MOD-INF-013](../../03_modules/_cross_layer/model_context_protocol_servers/blueprint.md) |
| 22 | src/zephyr/integration/mcp/knowledge_base_server.py | KnowledgeBaseServer: 知识库语义检索 MCP Server | 生产态 / production | [MOD-INF-013](../../03_modules/_cross_layer/model_context_protocol_servers/blueprint.md) |
| 23 | src/zephyr/integration/mcp/prompt_provider.py | MCP Prompt 模板提供者（MOD-INF-013 Phase 6 — ... | 原型态 / prototype | [MOD-INF-013](../../03_modules/_cross_layer/model_context_protocol_servers/blueprint.md) |
| 24 | src/zephyr/integration/mcp/rate_limiter.py | MCP Gateway 同步速率限制器（MOD-INF-013 §12 St... | 生产态 / production | [MOD-INF-013](../../03_modules/_cross_layer/model_context_protocol_servers/blueprint.md) |
| 25 | src/zephyr/integration/mcp/resource_provider.py | MCP Resource 提供者（MOD-INF-013 Phase 6 — 关... | 原型态 / prototype | [MOD-INF-013](../../03_modules/_cross_layer/model_context_protocol_servers/blueprint.md) |
| 26 | src/zephyr/integration/mcp/sandbox_server.py | MCP sandbox 安全代码执行沙箱（MOD-INF-013 Phase... | 原型态 / prototype | [MOD-INF-013](../../03_modules/_cross_layer/model_context_protocol_servers/blueprint.md) |
| 27 | src/zephyr/integration/mcp/sentinel_server.py | SentinelServer: 意图路由哨兵 MCP Server | 生产态 / production | [MOD-INF-013](../../03_modules/_cross_layer/model_context_protocol_servers/blueprint.md) |
| 28 | src/zephyr/integration/mcp/task_manager_server.py | ZephyrAlpha MCP Task Manager Server | 生产态 / production | [MOD-INF-013](../../03_modules/_cross_layer/model_context_protocol_servers/blueprint.md) |
| 29 | src/zephyr/integration/mcp/telemetry_server.py | ZephyrAlpha MCP Telemetry Server — 系统可观测... | 生产态 / production | [MOD-INF-013](../../03_modules/_cross_layer/model_context_protocol_servers/blueprint.md) |
| 30 | src/zephyr/integration/mcp/vector_memory_server.py | VectorMemoryServer: VMS 向量记忆 MCP Server (MO... | 原型态 / prototype | [MOD-INF-013](../../03_modules/_cross_layer/model_context_protocol_servers/blueprint.md) |
| 31 | src/zephyr/integration/mcp_server.py | AssetInventory MCP Server — MOD-INF-026 蓝图 §21 | 原型态 / prototype | [MOD-INF-026](../../03_modules/_domain_infrastructure_operations/asset_inventory/blueprint.md) |
| 32 | src/zephyr/integration/pipeline_orchestrator.py | PipelineOrchestrator — M1-M11 管线协调器 | 生产态 / production | [MOD-INF-009](../../03_modules/_cross_layer/pipeline/blueprint.md) |
| 33 | src/zephyr/integration/ports.py | Protocol-based interface layer for pipeline->mc... | 原型态 / prototype | [MOD-INF-009](../../03_modules/_cross_layer/pipeline/blueprint.md) |
| 34 | src/zephyr/integration/shared/contracts/errors/__init__.py | Auto-generated contracts package — errors | 原型态 / prototype |  |
| 35 | src/zephyr/integration/shared/contracts/errors/contract_v... | contract_violation_error.py | 原型态 / prototype |  |
| 36 | src/zephyr/integration/shared/contracts/errors/data_quali... | CTR-ERR-001: DataQualityError / 行情质量门禁不... | 原型态 / prototype |  |
| 37 | src/zephyr/integration/shared/contracts/errors/execution_... | execution_rejection_error.py | 原型态 / prototype |  |
| 38 | src/zephyr/integration/shared/contracts/errors/factor_com... | CTR-ERR-002: FactorComputationError / 因子计算... | 原型态 / prototype |  |
| 39 | src/zephyr/integration/shared/contracts/errors/risk_limit... | risk_limit_violation_error.py | 原型态 / prototype |  |
| 40 | src/zephyr/integration/shared/contracts/errors/signal_deg... | signal_degradation_warning.py | 原型态 / prototype |  |
| 41 | src/zephyr/integration/shared/events/__init__.py | __init__.py | 原型态 / prototype | [MOD-INF-016](../../03_modules/_cross_layer/shared_core/blueprint.md) |
| 42 | src/zephyr/integration/shared/events/dlq.py | dlq.py —— ZephyrAlpha 死信队列（Dead Letter Q... | 原型态 / prototype | [MOD-INF-016](../../03_modules/_cross_layer/shared_core/blueprint.md) |
| 43 | src/zephyr/integration/shared/events/dlq_bridge.py | CT-DLQ-001: DeadLetterQueue -> System Event Bus... | 原型态 / prototype | [MOD-INF-016](../../03_modules/_cross_layer/shared_core/blueprint.md) |
| 44 | src/zephyr/integration/shared/events/event_bus_upgrade.py | EventBus Upgrade — 事件总线升级 (M-16) | 原型态 / prototype | [MOD-INF-016](../../03_modules/_cross_layer/shared_core/blueprint.md) |
| 45 | src/zephyr/integration/shared/events/event_schemas.py | event_schemas.py —— Observer 事件体 Pydantic ... | 原型态 / prototype | [MOD-INF-016](../../03_modules/_cross_layer/shared_core/blueprint.md) |
| 46 | src/zephyr/integration/shared/events/upgrade_strategy.py | EventBus 升级策略引擎 | 生产态 / production | [MOD-INF-016](../../03_modules/_cross_layer/shared_core/blueprint.md) |
| 47 | src/zephyr/integration/shared/schema/__init__.py | shared.schema — auto-generated package init. | 原型态 / prototype | [MOD-INF-016](../../03_modules/_cross_layer/shared_core/blueprint.md) |
| 48 | src/zephyr/integration/shared/schema/base_config.py | base_config.py | 生产态 / production | [MOD-INF-016](../../03_modules/_cross_layer/shared_core/blueprint.md) |
| 49 | src/zephyr/integration/shared/schema/execution_model.py | execution_model.py | 生产态 / production | [MOD-INF-016](../../03_modules/_cross_layer/shared_core/blueprint.md) |
| 50 | src/zephyr/integration/shared/schema/schema_registry.py | schema_registry.py | 生产态 / production | [MOD-INF-016](../../03_modules/_cross_layer/shared_core/blueprint.md) |
| 51 | src/zephyr/integration/shared/schema/schemas.py | schemas.py | 生产态 / production | [MOD-INF-016](../../03_modules/_cross_layer/shared_core/blueprint.md) |
| 52 | src/zephyr/integration/shared/schema/severity_types.py | severity_types.py | 生产态 / production | [MOD-INF-016](../../03_modules/_cross_layer/shared_core/blueprint.md) |
| 53 | src/zephyr/integration/vector_memory/__init__.py | Vector Memory Service (VMS) — MOD-INF-011 · v0.7.0 | 生产态 / production | [MOD-INF-011](../../03_modules/_domain_knowledge/vector_memory/blueprint.md) |
| 54 | src/zephyr/integration/vector_memory/bm25_index.py | BM25Index — MOD-INF-011 稀疏检索组件 | 生产态 / production | [MOD-INF-028](../../03_modules/_cross_layer/semantic_auditor/blueprint.md) |
| 55 | src/zephyr/integration/vector_memory/bridge_layer.py | BridgeLayer — MOD-INF-011 kb/ ↔ VMS 过渡桥接 | 生产态 / production | [MOD-INF-011](../../03_modules/_domain_knowledge/vector_memory/blueprint.md) |
| 56 | src/zephyr/integration/vector_memory/cache_layer.py | cache_layer.py | 生产态 / production | [MOD-INF-039](../../03_modules/_cross_layer/agent_orchestrator/blueprint.md) |
| 57 | src/zephyr/integration/vector_memory/chunk_strategy_route... | ChunkStrategyRouter — MOD-INF-011 分块策略调度 | 生产态 / production | [MOD-INF-011](../../03_modules/_domain_knowledge/vector_memory/blueprint.md) |
| 58 | src/zephyr/integration/vector_memory/collection_manager.py | CollectionManager — MOD-INF-011 八大 Collectio... | 生产态 / production | [MOD-INF-011](../../03_modules/_domain_knowledge/vector_memory/blueprint.md) |
| 59 | src/zephyr/integration/vector_memory/collection_schemas.py | collection_schemas.py | 生产态 / production | [MOD-INF-011](../../03_modules/_domain_knowledge/vector_memory/blueprint.md) |
| 60 | src/zephyr/integration/vector_memory/context_ingest.py | VMS 上下文注入器 — ingest_context() 消费者 | 原型态 / prototype | [MOD-INF-011](../../03_modules/_domain_knowledge/vector_memory/blueprint.md) |
| 61 | src/zephyr/integration/vector_memory/cross_collection_ret... | CrossCollectionRetriever — MOD-INF-011 跨 Coll... | 原型态 / prototype | [MOD-INF-011](../../03_modules/_domain_knowledge/vector_memory/blueprint.md) |
| 62 | src/zephyr/integration/vector_memory/delegated_vector_mem... | DelegatedVectorMemory — VectorMemoryBase 的 RI... | 原型态 / prototype | [MOD-INF-011](../../03_modules/_domain_knowledge/vector_memory/blueprint.md) |
| 63 | src/zephyr/integration/vector_memory/design_principles.py | design_principles.py | 生产态 / production | [MOD-INF-011](../../03_modules/_domain_knowledge/vector_memory/blueprint.md) |
| 64 | src/zephyr/integration/vector_memory/faiss_collection_man... | FAISSCollectionManager — FAISS HNSW/IVF+PQ 8 C... | 生产态 / production | [MOD-INF-011](../../03_modules/_domain_knowledge/vector_memory/blueprint.md) |
| 65 | src/zephyr/integration/vector_memory/hybrid_retriever.py | HybridRetriever — MOD-INF-011 混合检索架构 | 生产态 / production | [MOD-INF-011](../../03_modules/_domain_knowledge/vector_memory/blueprint.md) |
| 66 | src/zephyr/integration/vector_memory/in_memory_fake_vms.py | InMemoryFakeVMS — MOD-INF-011 · 零依赖测试双胞胎 | 生产态 / production | [MOD-INF-011](../../03_modules/_domain_knowledge/vector_memory/blueprint.md) |
| 67 | src/zephyr/integration/vector_memory/in_memory_memory_bac... | InMemoryMemoryBackend — MOD-INF-011 降级兜底 | 生产态 / production | [MOD-INF-011](../../03_modules/_domain_knowledge/vector_memory/blueprint.md) |
| 68 | src/zephyr/integration/vector_memory/in_process_vector_me... | InProcessVectorMemory — MOD-INF-011 VMS 统一入口 | 生产态 / production | [MOD-INF-011](../../03_modules/_domain_knowledge/vector_memory/blueprint.md) |
| 69 | src/zephyr/integration/vector_memory/index_health_monitor.py | IndexHealthMonitor — MOD-INF-011 索引健康自检... | 生产态 / production | [MOD-INF-011](../../03_modules/_domain_knowledge/vector_memory/blueprint.md) |
| 70 | src/zephyr/integration/vector_memory/interface.py | VMS — Vector Memory Service 接口基类 | 生产态 / production | [MOD-INF-011](../../03_modules/_domain_knowledge/vector_memory/blueprint.md) |
| 71 | src/zephyr/integration/vector_memory/migrate_chroma_to_fa... | ChromDB -> FAISS + SQLite WAL 数据迁移脚本 | 原型态 / prototype | [MOD-INF-011](../../03_modules/_domain_knowledge/vector_memory/blueprint.md) |
| 72 | src/zephyr/integration/vector_memory/ollama_embedding.py | ollama_embedding.py | 原型态 / prototype | [MOD-INF-039](../../03_modules/_cross_layer/agent_orchestrator/blueprint.md) |
| 73 | src/zephyr/integration/vector_memory/provenance_enforcer.py | ProvenanceEnforcer — MOD-INF-011 写入溯源强制执行 | 生产态 / production | [MOD-INF-011](../../03_modules/_domain_knowledge/vector_memory/blueprint.md) |
| 74 | src/zephyr/integration/vector_memory/retrieval_feedback.py | RetrievalFeedback — MOD-INF-011 FLE 检索质量消费 | 生产态 / production | [MOD-INF-011](../../03_modules/_domain_knowledge/vector_memory/blueprint.md) |
| 75 | src/zephyr/integration/vector_memory/sqlite_metadata_stor... | SQLiteMetadataStore — VMS 元数据存储 (SQLite W... | 生产态 / production | [MOD-INF-011](../../03_modules/_domain_knowledge/vector_memory/blueprint.md) |
| 76 | src/zephyr/integration/vector_memory/vector_bridge.py | VectorBridge — MOD-INF-011 CE/KB 外部集成适配器 | 原型态 / prototype | [MOD-INF-011](../../03_modules/_domain_knowledge/vector_memory/blueprint.md) |
| 77 | src/zephyr/integration/vector_memory/vms_config.yaml | vms_config.yaml | 生产态 / production | [MOD-INF-017](../../03_modules/_domain_governance/code_dedup_engine/blueprint.md) |
| 78 | src/zephyr/integration/vector_memory/vms_errors.py | vms_errors.py | 生产态 / production | [MOD-INF-011](../../03_modules/_domain_knowledge/vector_memory/blueprint.md) |
| 79 | src/zephyr/integration/vector_memory/vms_schemas.py | VMS 共享数据模型 — MOD-INF-011 · 蓝图 §6.1 ... | 生产态 / production | [MOD-INF-011](../../03_modules/_domain_knowledge/vector_memory/blueprint.md) |
| 80 | src/zephyr/shared/contracts/approval_types.py | G-CT-004 — ApprovalRequest Pydantic V2 BaseMod... | 生产态 / production | [MOD-INF-016](../../03_modules/_cross_layer/shared_core/blueprint.md) |
| 81 | src/zephyr/shared/contracts/protocols.py | Structural Protocol interfaces for cross-module... | 原型态 / prototype | [MOD-INF-016](../../03_modules/_cross_layer/shared_core/blueprint.md) |
| 82 | src/zephyr/shared/contracts/rollback_types.py | G-CT-003 — RollbackResult Pydantic V2 BaseMode... | 生产态 / production | [MOD-INF-016](../../03_modules/_cross_layer/shared_core/blueprint.md) |
| 83 | src/zephyr/shared/contracts/runtime_types.py | runtime_types.py | 生产态 / production | [MOD-INF-035](../../03_modules/_cross_layer/auto_runtime_core/blueprint.md) |

### L2 领域层 / Domain Layer (5 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name (功能简介 / Description) | 成熟度 / Maturity | 蓝图 / Blueprint |
|:--:|---------|---------|:---:|:---:|
| 1 | tests/external/test_external_health.py | test_external_health.py | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 2 | tests/external/test_external_merkle_proof.py | test_external_merkle_proof.py | 原型态 / prototype | [MOD-INF-021](../../03_modules/_domain_autonomy_core/rollback_system/blueprint.md) |
| 3 | tests/external/test_external_tool_audit.py | test_external_tool_audit.py | 原型态 / prototype | [MOD-INF-020](../../03_modules/_domain_governance/audit_trail/blueprint.md) |
| 4 | tests/external/test_external_validation_checkpoint.py | test_external_validation_checkpoint.py | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 5 | tests/external/test_external_verifier.py | test_external_verifier.py | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |

## 域内依赖图 / Internal Dependency Diagram

> 依赖图内嵌在本文档中，IDE 可直接渲染显示。参考 decision_index.md 设计，分四个视图：合并全景图、运营态子图、设计态子图、原型态子图（按 design_maturity 实际值拆分）。
>
> **图例说明 / Legend**：
> - **实线边框 = 运营态模块**（production，已上线运行）
> - **虚线边框 = 设计态模块**（design，蓝图阶段，代码未写）
> - **虚线边框 = 原型态模块**（prototype，代码已写，验证中未稳定上线）
> - **实线箭头 = 运营态依赖**（已生效的依赖关系）
> - **虚线箭头 = 非运营态依赖**（计划中/验证中的依赖关系）

### 合并全景图（全部模块，标签标注成熟度）

> 展示全部 92 个模块（生产态 53 + 设计态 0 + 原型态 39），标签标注成熟度。

#### 第 1 页 / 共 4 页

```mermaid
graph TD
    subgraph D_INTEGRATION["D_INTEGRATION 管线路由"]
        src_zephyr_integration_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_integration_behavioral_admission_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_integration_behavioral_admission_admission_response_py["(生产态 / production) admission_response.py"]
        src_zephyr_integration_budget_enforcer_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_integration_budget_enforcer_degradation_spiral_detector_py["(原型态 / prototype) Degradation Spiral Detector — 模型幻觉-容量正...<br/>文件: degradation_spiral_detector.py"]
        src_zephyr_integration_llm_bridge_py["(原型态 / prototype) 接收 RED 问题,生成修复文本。LLM 只润色不做判断...<br/>文件: llm_bridge.py"]
        src_zephyr_integration_local_model_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_integration_local_model_cache_layer_py["(生产态 / production) CacheLayer — MOD-INF-011 嵌入缓存与查询结果 LRU<br/>文件: cache_layer.py"]
        src_zephyr_integration_local_model_deepseek_chat_py["(生产态 / production) DeepSeekChat — 通过 DeepSeek API 进行 LLM 推理...<br/>文件: deepseek_chat.py"]
        src_zephyr_integration_local_model_embedding_router_py["(生产态 / production) EmbeddingRouter — MOD-INF-011 双嵌入维度路由<br/>文件: embedding_router.py"]
        src_zephyr_integration_local_model_local_model_scheduler_py["(生产态 / production) LocalModelScheduler — L2 本地模型 24/7 调度循环<br/>文件: local_model_scheduler.py"]
        src_zephyr_integration_local_model_ollama_chat_py["(生产态 / production) OllamaChat — 通过 Ollama HTTP API 进行本地 LLM...<br/>文件: ollama_chat.py"]
        src_zephyr_integration_local_model_ollama_embedding_py["(原型态 / prototype) OllamaEmbedder — 通过 Ollama HTTP API 生成文本嵌入<br/>文件: ollama_embedding.py"]
        src_zephyr_integration_mcp_base_server_py["(生产态 / production) BaseMCPServer: stdio 传输 + JSON-RPC 2.0 协议基类<br/>文件: _base_server.py"]
        src_zephyr_integration_mcp_audit_logger_py["(生产态 / production) MCP 全量工具调用审计日志（MOD-INF-013 §12 Step...<br/>文件: audit_logger.py"]
        src_zephyr_integration_mcp_blueprint_search_server_py["(生产态 / production) BlueprintSearchServer — MCP Server for bluepri...<br/>文件: blueprint_search_server.py"]
        src_zephyr_integration_mcp_doc_guard_server_py["(生产态 / production) DocGuardServer: 跨会话交接协议服务 MCP Server<br/>文件: doc_guard_server.py"]
        src_zephyr_integration_mcp_error_codes_py["(生产态 / production) MCP 错误码集中注册（MOD-INF-013 §3.4）。<br/>文件: error_codes.py"]
        src_zephyr_integration_mcp_gate_engine_server_py["(生产态 / production) GateEngineServer: 门禁裁决服务 MCP Server<br/>文件: gate_engine_server.py"]
        src_zephyr_integration_mcp_gateway_server_py["(生产态 / production) MCP Gateway 集中式治理节点（MOD-INF-013 §12 Ph...<br/>文件: gateway_server.py"]
        src_zephyr_integration_mcp_handoff_auto_loader_py["(原型态 / prototype) Handoff 自动加载器——从 handoff 包恢复 AI sess...<br/>文件: handoff_auto_loader.py"]
        src_zephyr_integration_mcp_knowledge_base_server_py["(生产态 / production) KnowledgeBaseServer: 知识库语义检索 MCP Server<br/>文件: knowledge_base_server.py"]
        src_zephyr_integration_mcp_prompt_provider_py["(原型态 / prototype) MCP Prompt 模板提供者（MOD-INF-013 Phase 6 — ...<br/>文件: prompt_provider.py"]
        src_zephyr_integration_mcp_rate_limiter_py["(生产态 / production) MCP Gateway 同步速率限制器（MOD-INF-013 §12 St...<br/>文件: rate_limiter.py"]
        src_zephyr_integration_mcp_resource_provider_py["(原型态 / prototype) MCP Resource 提供者（MOD-INF-013 Phase 6 — 关...<br/>文件: resource_provider.py"]
        src_zephyr_integration_mcp_sandbox_server_py["(原型态 / prototype) MCP sandbox 安全代码执行沙箱（MOD-INF-013 Phase...<br/>文件: sandbox_server.py"]
        src_zephyr_integration_mcp_sentinel_server_py["(生产态 / production) SentinelServer: 意图路由哨兵 MCP Server<br/>文件: sentinel_server.py"]
        src_zephyr_integration_mcp_task_manager_server_py["(生产态 / production) ZephyrAlpha MCP Task Manager Server<br/>文件: task_manager_server.py"]
        src_zephyr_integration_mcp_telemetry_server_py["(生产态 / production) ZephyrAlpha MCP Telemetry Server — 系统可观测...<br/>文件: telemetry_server.py"]
        src_zephyr_integration_mcp_vector_memory_server_py["(原型态 / prototype) VectorMemoryServer: VMS 向量记忆 MCP Server (MO...<br/>文件: vector_memory_server.py"]
    end
    src_zephyr_integration_init_py -.->|导入依赖 / import_depends| src_zephyr_integration_llm_bridge_py
    src_zephyr_integration_behavioral_admission_init_py -.->|config_depends / config_depends| src_zephyr_integration_behavioral_admission_admission_response_py
    src_zephyr_integration_budget_enforcer_degradation_spiral_detector_py -.->|config_depends / config_depends| src_zephyr_integration_budget_enforcer_init_py
    src_zephyr_integration_local_model_embedding_router_py -.->|导入依赖 / import_depends| src_zephyr_integration_local_model_ollama_embedding_py
    src_zephyr_integration_local_model_local_model_scheduler_py -->|导入依赖 / import_depends| src_zephyr_integration_local_model_embedding_router_py
    src_zephyr_integration_local_model_local_model_scheduler_py -->|导入依赖 / import_depends| src_zephyr_integration_local_model_ollama_chat_py
    src_zephyr_integration_local_model_init_py -.->|导入依赖 / import_depends| src_zephyr_integration_local_model_cache_layer_py
    src_zephyr_integration_local_model_init_py -.->|导入依赖 / import_depends| src_zephyr_integration_local_model_deepseek_chat_py
    src_zephyr_integration_local_model_init_py -.->|导入依赖 / import_depends| src_zephyr_integration_local_model_embedding_router_py
    src_zephyr_integration_local_model_init_py -.->|导入依赖 / import_depends| src_zephyr_integration_local_model_local_model_scheduler_py
    src_zephyr_integration_local_model_init_py -.->|导入依赖 / import_depends| src_zephyr_integration_local_model_ollama_embedding_py
    src_zephyr_integration_local_model_init_py -.->|导入依赖 / import_depends| src_zephyr_integration_local_model_ollama_chat_py
    src_zephyr_integration_mcp_blueprint_search_server_py -->|导入依赖 / import_depends| src_zephyr_integration_mcp_base_server_py
    src_zephyr_integration_mcp_doc_guard_server_py -->|导入依赖 / import_depends| src_zephyr_integration_mcp_base_server_py
    src_zephyr_integration_mcp_gate_engine_server_py -->|导入依赖 / import_depends| src_zephyr_integration_mcp_base_server_py
    src_zephyr_integration_mcp_knowledge_base_server_py -->|导入依赖 / import_depends| src_zephyr_integration_mcp_base_server_py
    src_zephyr_integration_mcp_gateway_server_py -->|导入依赖 / import_depends| src_zephyr_integration_mcp_audit_logger_py
    src_zephyr_integration_mcp_gateway_server_py -->|导入依赖 / import_depends| src_zephyr_integration_mcp_blueprint_search_server_py
    src_zephyr_integration_mcp_gateway_server_py -->|导入依赖 / import_depends| src_zephyr_integration_mcp_doc_guard_server_py
    src_zephyr_integration_mcp_gateway_server_py -->|导入依赖 / import_depends| src_zephyr_integration_mcp_error_codes_py
    src_zephyr_integration_mcp_gateway_server_py -->|导入依赖 / import_depends| src_zephyr_integration_mcp_gate_engine_server_py
    src_zephyr_integration_mcp_gateway_server_py -->|导入依赖 / import_depends| src_zephyr_integration_mcp_knowledge_base_server_py
    src_zephyr_integration_mcp_gateway_server_py -->|导入依赖 / import_depends| src_zephyr_integration_mcp_rate_limiter_py
    src_zephyr_integration_mcp_gateway_server_py -->|导入依赖 / import_depends| src_zephyr_integration_mcp_telemetry_server_py
    src_zephyr_integration_mcp_gateway_server_py -->|导入依赖 / import_depends| src_zephyr_integration_mcp_sentinel_server_py
    src_zephyr_integration_mcp_gateway_server_py -.->|导入依赖 / import_depends| src_zephyr_integration_mcp_vector_memory_server_py
    src_zephyr_integration_mcp_gateway_server_py -->|导入依赖 / import_depends| src_zephyr_integration_mcp_task_manager_server_py
    src_zephyr_integration_mcp_gateway_server_py -->|导入依赖 / import_depends| src_zephyr_integration_mcp_base_server_py
    src_zephyr_integration_mcp_sandbox_server_py -.->|导入依赖 / import_depends| src_zephyr_integration_mcp_base_server_py
    src_zephyr_integration_mcp_sentinel_server_py -->|导入依赖 / import_depends| src_zephyr_integration_mcp_base_server_py
    src_zephyr_integration_mcp_vector_memory_server_py -.->|导入依赖 / import_depends| src_zephyr_integration_mcp_base_server_py
    src_zephyr_integration_mcp_base_server_py -->|导入依赖 / import_depends| src_zephyr_integration_mcp_error_codes_py
    D_GOVERNANCE["(生产态 / production) D_GOVERNANCE"]
    src_zephyr_integration_mcp_task_manager_server_py -->|导入依赖 / import_depends| D_GOVERNANCE
    D_OPS["(生产态 / production) D_OPS"]
    src_zephyr_integration_local_model_deepseek_chat_py -->|导入依赖 / import_depends| D_OPS
    D_GOV_AUDIT["(生产态 / production) D_GOV_AUDIT"]
    src_zephyr_integration_llm_bridge_py -.->|导入依赖 / import_depends| D_GOV_AUDIT
    D_INFRA_RUNTIME["(原型态 / prototype) D_INFRA_RUNTIME"]
    src_zephyr_integration_mcp_telemetry_server_py -.->|导入依赖 / import_depends| D_INFRA_RUNTIME
    src_zephyr_integration_mcp_gateway_server_py -->|导入依赖 / import_depends| D_GOVERNANCE
    D_SECURITY["(生产态 / production) D_SECURITY"]
    src_zephyr_integration_mcp_gateway_server_py -->|导入依赖 / import_depends| D_SECURITY
    D_SHARED["(生产态 / production) D_SHARED"]
    src_zephyr_integration_mcp_task_manager_server_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_integration_local_model_ollama_embedding_py -.->|导入依赖 / import_depends| D_SHARED
    D_GOV_RULE["(生产态 / production) D_GOV_RULE"]
    src_zephyr_integration_mcp_task_manager_server_py -->|导入依赖 / import_depends| D_GOV_RULE
    src_zephyr_integration_mcp_blueprint_search_server_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_integration_local_model_deepseek_chat_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_integration_mcp_task_manager_server_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_integration_mcp_resource_provider_py -.->|导入依赖 / import_depends| D_SHARED
    src_zephyr_integration_mcp_knowledge_base_server_py -.->|导入依赖 / import_depends| D_SHARED
    src_zephyr_integration_mcp_task_manager_server_py -->|导入依赖 / import_depends| D_SHARED
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_integration_init_py
    D_GOV_SCRIPTS["(原型态 / prototype) D_GOV_SCRIPTS"]
    D_GOV_SCRIPTS -.->|导入依赖 / import_depends| src_zephyr_integration_init_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_integration_init_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_integration_init_py
    D_GOV_SCRIPTS -.->|导入依赖 / import_depends| src_zephyr_integration_init_py
    D_AUTONOMY_CORE["(原型态 / prototype) D_AUTONOMY_CORE"]
    D_AUTONOMY_CORE -.->|测试依赖 / test_depends| src_zephyr_integration_local_model_cache_layer_py
    D_AUTONOMY_CORE -.->|测试依赖 / test_depends| src_zephyr_integration_local_model_embedding_router_py
    D_AUTONOMY_CORE -->|导入依赖 / import_depends| src_zephyr_integration_local_model_embedding_router_py
    D_AUTONOMY_CORE -.->|测试依赖 / test_depends| src_zephyr_integration_local_model_embedding_router_py
    D_INFRA_RUNTIME -->|导入依赖 / import_depends| src_zephyr_integration_local_model_local_model_scheduler_py
    D_INFRA_RUNTIME -->|导入依赖 / import_depends| src_zephyr_integration_local_model_local_model_scheduler_py
    D_AUTONOMY_CORE -.->|测试依赖 / test_depends| src_zephyr_integration_local_model_local_model_scheduler_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_integration_local_model_local_model_scheduler_py
    D_INTELLIGENCE["(原型态 / prototype) D_INTELLIGENCE"]
    D_INTELLIGENCE -.->|导入依赖 / import_depends| src_zephyr_integration_local_model_ollama_chat_py
    D_INTEGRATION_GATEWAY["(原型态 / prototype) D_INTEGRATION_GATEWAY"]
    D_INTEGRATION_GATEWAY -.->|导入依赖 / import_depends| src_zephyr_integration_mcp_gate_engine_server_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_integration_behavioral_admission_admission_response_py,src_zephyr_integration_local_model_cache_layer_py,src_zephyr_integration_local_model_deepseek_chat_py,src_zephyr_integration_local_model_embedding_router_py,src_zephyr_integration_local_model_local_model_scheduler_py,src_zephyr_integration_local_model_ollama_chat_py,src_zephyr_integration_mcp_base_server_py,src_zephyr_integration_mcp_audit_logger_py,src_zephyr_integration_mcp_blueprint_search_server_py,src_zephyr_integration_mcp_doc_guard_server_py,src_zephyr_integration_mcp_error_codes_py,src_zephyr_integration_mcp_gate_engine_server_py,src_zephyr_integration_mcp_gateway_server_py,src_zephyr_integration_mcp_knowledge_base_server_py,src_zephyr_integration_mcp_rate_limiter_py,src_zephyr_integration_mcp_sentinel_server_py,src_zephyr_integration_mcp_task_manager_server_py,src_zephyr_integration_mcp_telemetry_server_py production
    class src_zephyr_integration_init_py,src_zephyr_integration_behavioral_admission_init_py,src_zephyr_integration_budget_enforcer_init_py,src_zephyr_integration_budget_enforcer_degradation_spiral_detector_py,src_zephyr_integration_llm_bridge_py,src_zephyr_integration_local_model_init_py,src_zephyr_integration_local_model_ollama_embedding_py,src_zephyr_integration_mcp_handoff_auto_loader_py,src_zephyr_integration_mcp_prompt_provider_py,src_zephyr_integration_mcp_resource_provider_py,src_zephyr_integration_mcp_sandbox_server_py,src_zephyr_integration_mcp_vector_memory_server_py design
    class D_GOVERNANCE,D_OPS,D_GOV_AUDIT,D_SECURITY,D_SHARED,D_GOV_RULE external_prod
    class D_INFRA_RUNTIME,D_GOV_SCRIPTS,D_AUTONOMY_CORE,D_INTELLIGENCE,D_INTEGRATION_GATEWAY external_design
```

#### 第 2 页 / 共 4 页

```mermaid
graph TD
    subgraph D_INTEGRATION["D_INTEGRATION 管线路由"]
        src_zephyr_integration_mcp_server_py["(原型态 / prototype) AssetInventory MCP Server — MOD-INF-026 蓝图 §21<br/>文件: mcp_server.py"]
        src_zephyr_integration_pipeline_orchestrator_py["(生产态 / production) PipelineOrchestrator — M1-M11 管线协调器<br/>文件: pipeline_orchestrator.py"]
        src_zephyr_integration_ports_py["(原型态 / prototype) Protocol-based interface layer for pipeline->mc...<br/>文件: ports.py"]
        src_zephyr_integration_shared_contracts_errors_init_py["(原型态 / prototype) Auto-generated contracts package — errors<br/>文件: __init__.py"]
        src_zephyr_integration_shared_contracts_errors_contract_violation_error_py["(原型态 / prototype) contract_violation_error.py"]
        src_zephyr_integration_shared_contracts_errors_data_quality_error_py["(原型态 / prototype) CTR-ERR-001: DataQualityError / 行情质量门禁不...<br/>文件: data_quality_error.py"]
        src_zephyr_integration_shared_contracts_errors_execution_rejection_error_py["(原型态 / prototype) execution_rejection_error.py"]
        src_zephyr_integration_shared_contracts_errors_factor_computation_error_py["(原型态 / prototype) CTR-ERR-002: FactorComputationError / 因子计算...<br/>文件: factor_computation_error.py"]
        src_zephyr_integration_shared_contracts_errors_risk_limit_violation_error_py["(原型态 / prototype) risk_limit_violation_error.py"]
        src_zephyr_integration_shared_contracts_errors_signal_degradation_warning_py["(原型态 / prototype) signal_degradation_warning.py"]
        src_zephyr_integration_shared_events_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_integration_shared_events_dlq_py["(原型态 / prototype) dlq.py —— ZephyrAlpha 死信队列（Dead Letter Q...<br/>文件: dlq.py"]
        src_zephyr_integration_shared_events_dlq_bridge_py["(原型态 / prototype) CT-DLQ-001: DeadLetterQueue -> System Event Bus...<br/>文件: dlq_bridge.py"]
        src_zephyr_integration_shared_events_event_bus_upgrade_py["(原型态 / prototype) EventBus Upgrade — 事件总线升级 (M-16)<br/>文件: event_bus_upgrade.py"]
        src_zephyr_integration_shared_events_event_schemas_py["(原型态 / prototype) event_schemas.py —— Observer 事件体 Pydantic ...<br/>文件: event_schemas.py"]
        src_zephyr_integration_shared_events_upgrade_strategy_py["(生产态 / production) EventBus 升级策略引擎<br/>文件: upgrade_strategy.py"]
        src_zephyr_integration_shared_schema_init_py["(原型态 / prototype) shared.schema — auto-generated package init.<br/>文件: __init__.py"]
        src_zephyr_integration_shared_schema_base_config_py["(生产态 / production) base_config.py"]
        src_zephyr_integration_shared_schema_execution_model_py["(生产态 / production) execution_model.py"]
        src_zephyr_integration_shared_schema_schema_registry_py["(生产态 / production) schema_registry.py"]
        src_zephyr_integration_shared_schema_schemas_py["(生产态 / production) schemas.py"]
        src_zephyr_integration_shared_schema_severity_types_py["(生产态 / production) severity_types.py"]
        src_zephyr_integration_vector_memory_init_py["(生产态 / production) Vector Memory Service (VMS) — MOD-INF-011 · v0.7.0<br/>文件: __init__.py"]
        src_zephyr_integration_vector_memory_bm25_index_py["(生产态 / production) BM25Index — MOD-INF-011 稀疏检索组件<br/>文件: bm25_index.py"]
        src_zephyr_integration_vector_memory_bridge_layer_py["(生产态 / production) BridgeLayer — MOD-INF-011 kb/ ↔ VMS 过渡桥接<br/>文件: bridge_layer.py"]
        src_zephyr_integration_vector_memory_cache_layer_py["(生产态 / production) cache_layer.py"]
        src_zephyr_integration_vector_memory_chunk_strategy_router_py["(生产态 / production) ChunkStrategyRouter — MOD-INF-011 分块策略调度<br/>文件: chunk_strategy_router.py"]
        src_zephyr_integration_vector_memory_collection_manager_py["(生产态 / production) CollectionManager — MOD-INF-011 八大 Collectio...<br/>文件: collection_manager.py"]
        src_zephyr_integration_vector_memory_collection_schemas_py["(生产态 / production) collection_schemas.py"]
        src_zephyr_integration_vector_memory_context_ingest_py["(原型态 / prototype) VMS 上下文注入器 — ingest_context() 消费者<br/>文件: context_ingest.py"]
    end
    src_zephyr_integration_shared_contracts_errors_init_py -.->|导入依赖 / import_depends| src_zephyr_integration_shared_contracts_errors_contract_violation_error_py
    src_zephyr_integration_shared_contracts_errors_init_py -.->|导入依赖 / import_depends| src_zephyr_integration_shared_contracts_errors_data_quality_error_py
    src_zephyr_integration_shared_contracts_errors_init_py -.->|导入依赖 / import_depends| src_zephyr_integration_shared_contracts_errors_factor_computation_error_py
    src_zephyr_integration_shared_contracts_errors_init_py -.->|导入依赖 / import_depends| src_zephyr_integration_shared_contracts_errors_execution_rejection_error_py
    src_zephyr_integration_shared_contracts_errors_init_py -.->|导入依赖 / import_depends| src_zephyr_integration_shared_contracts_errors_risk_limit_violation_error_py
    src_zephyr_integration_shared_contracts_errors_init_py -.->|导入依赖 / import_depends| src_zephyr_integration_shared_contracts_errors_signal_degradation_warning_py
    src_zephyr_integration_shared_events_dlq_bridge_py -.->|导入依赖 / import_depends| src_zephyr_integration_shared_events_dlq_py
    src_zephyr_integration_shared_events_event_schemas_py -.->|导入依赖 / import_depends| src_zephyr_integration_shared_schema_base_config_py
    src_zephyr_integration_shared_events_init_py -.->|导入依赖 / import_depends| src_zephyr_integration_shared_events_dlq_py
    src_zephyr_integration_shared_events_init_py -.->|导入依赖 / import_depends| src_zephyr_integration_shared_events_dlq_bridge_py
    src_zephyr_integration_shared_events_init_py -.->|导入依赖 / import_depends| src_zephyr_integration_shared_events_event_bus_upgrade_py
    src_zephyr_integration_shared_events_init_py -.->|导入依赖 / import_depends| src_zephyr_integration_shared_events_event_schemas_py
    src_zephyr_integration_shared_events_init_py -.->|导入依赖 / import_depends| src_zephyr_integration_shared_events_upgrade_strategy_py
    src_zephyr_integration_shared_schema_init_py -.->|config_depends / config_depends| src_zephyr_integration_shared_schema_base_config_py
    src_zephyr_integration_shared_schema_schemas_py -->|导入依赖 / import_depends| src_zephyr_integration_shared_schema_base_config_py
    src_zephyr_integration_shared_schema_schemas_py -->|导入依赖 / import_depends| src_zephyr_integration_shared_schema_execution_model_py
    src_zephyr_integration_shared_schema_schemas_py -->|导入依赖 / import_depends| src_zephyr_integration_shared_schema_severity_types_py
    src_zephyr_integration_vector_memory_bridge_layer_py -->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_collection_manager_py
    D_OPS["(生产态 / production) D_OPS"]
    src_zephyr_integration_pipeline_orchestrator_py -->|导入依赖 / import_depends| D_OPS
    D_INFRA_RUNTIME["(生产态 / production) D_INFRA_RUNTIME"]
    src_zephyr_integration_pipeline_orchestrator_py -->|导入依赖 / import_depends| D_INFRA_RUNTIME
    src_zephyr_integration_pipeline_orchestrator_py -->|导入依赖 / import_depends| D_INFRA_RUNTIME
    src_zephyr_integration_pipeline_orchestrator_py -->|导入依赖 / import_depends| D_INFRA_RUNTIME
    src_zephyr_integration_pipeline_orchestrator_py -->|导入依赖 / import_depends| D_INFRA_RUNTIME
    src_zephyr_integration_pipeline_orchestrator_py -->|导入依赖 / import_depends| D_INFRA_RUNTIME
    D_INTELLIGENCE["(生产态 / production) D_INTELLIGENCE"]
    src_zephyr_integration_pipeline_orchestrator_py -->|导入依赖 / import_depends| D_INTELLIGENCE
    src_zephyr_integration_pipeline_orchestrator_py -->|导入依赖 / import_depends| D_INTELLIGENCE
    D_SECURITY["(生产态 / production) D_SECURITY"]
    src_zephyr_integration_pipeline_orchestrator_py -->|导入依赖 / import_depends| D_SECURITY
    D_SHARED["(生产态 / production) D_SHARED"]
    src_zephyr_integration_shared_events_dlq_py -.->|导入依赖 / import_depends| D_SHARED
    src_zephyr_integration_pipeline_orchestrator_py -->|导入依赖 / import_depends| D_INFRA_RUNTIME
    src_zephyr_integration_mcp_server_py -.->|导入依赖 / import_depends| D_SHARED
    src_zephyr_integration_pipeline_orchestrator_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_integration_shared_contracts_errors_data_quality_error_py -.->|导入依赖 / import_depends| D_SHARED
    D_INFRASTRUCTURE["(原型态 / prototype) D_INFRASTRUCTURE"]
    src_zephyr_integration_pipeline_orchestrator_py -.->|导入依赖 / import_depends| D_INFRASTRUCTURE
    D_INFRA_RUNTIME -->|导入依赖 / import_depends| src_zephyr_integration_pipeline_orchestrator_py
    D_INTELLIGENCE -.->|测试依赖 / test_depends| src_zephyr_integration_pipeline_orchestrator_py
    D_INTELLIGENCE -.->|测试依赖 / test_depends| src_zephyr_integration_pipeline_orchestrator_py
    D_SECURITY -.->|导入依赖 / import_depends| src_zephyr_integration_shared_schema_execution_model_py
    D_AUTONOMY_CORE["(原型态 / prototype) D_AUTONOMY_CORE"]
    D_AUTONOMY_CORE -.->|测试依赖 / test_depends| src_zephyr_integration_shared_schema_execution_model_py
    D_GOVERNANCE["(原型态 / prototype) D_GOVERNANCE"]
    D_GOVERNANCE -.->|测试依赖 / test_depends| src_zephyr_integration_shared_schema_execution_model_py
    D_ORCHESTRATOR["(原型态 / prototype) D_ORCHESTRATOR"]
    D_ORCHESTRATOR -.->|导入依赖 / import_depends| src_zephyr_integration_shared_schema_base_config_py
    D_GOV_AUDIT["(原型态 / prototype) D_GOV_AUDIT"]
    D_GOV_AUDIT -.->|导入依赖 / import_depends| src_zephyr_integration_shared_schema_base_config_py
    D_GOV_RULE["(生产态 / production) D_GOV_RULE"]
    D_GOV_RULE -->|导入依赖 / import_depends| src_zephyr_integration_shared_schema_base_config_py
    D_SECURITY -.->|导入依赖 / import_depends| src_zephyr_integration_shared_schema_severity_types_py
    D_GOVERNANCE -.->|测试依赖 / test_depends| src_zephyr_integration_shared_schema_severity_types_py
    D_GOVERNANCE -->|导入依赖 / import_depends| src_zephyr_integration_shared_schema_severity_types_py
    D_SHARED -.->|测试依赖 / test_depends| src_zephyr_integration_shared_schema_severity_types_py
    D_SECURITY_LLM["(原型态 / prototype) D_SECURITY_LLM"]
    D_SECURITY_LLM -.->|测试依赖 / test_depends| src_zephyr_integration_shared_schema_severity_types_py
    D_AUTONOMY_CORE -.->|测试依赖 / test_depends| src_zephyr_integration_shared_schema_severity_types_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_integration_pipeline_orchestrator_py,src_zephyr_integration_shared_events_upgrade_strategy_py,src_zephyr_integration_shared_schema_base_config_py,src_zephyr_integration_shared_schema_execution_model_py,src_zephyr_integration_shared_schema_schema_registry_py,src_zephyr_integration_shared_schema_schemas_py,src_zephyr_integration_shared_schema_severity_types_py,src_zephyr_integration_vector_memory_init_py,src_zephyr_integration_vector_memory_bm25_index_py,src_zephyr_integration_vector_memory_bridge_layer_py,src_zephyr_integration_vector_memory_cache_layer_py,src_zephyr_integration_vector_memory_chunk_strategy_router_py,src_zephyr_integration_vector_memory_collection_manager_py,src_zephyr_integration_vector_memory_collection_schemas_py production
    class src_zephyr_integration_mcp_server_py,src_zephyr_integration_ports_py,src_zephyr_integration_shared_contracts_errors_init_py,src_zephyr_integration_shared_contracts_errors_contract_violation_error_py,src_zephyr_integration_shared_contracts_errors_data_quality_error_py,src_zephyr_integration_shared_contracts_errors_execution_rejection_error_py,src_zephyr_integration_shared_contracts_errors_factor_computation_error_py,src_zephyr_integration_shared_contracts_errors_risk_limit_violation_error_py,src_zephyr_integration_shared_contracts_errors_signal_degradation_warning_py,src_zephyr_integration_shared_events_init_py,src_zephyr_integration_shared_events_dlq_py,src_zephyr_integration_shared_events_dlq_bridge_py,src_zephyr_integration_shared_events_event_bus_upgrade_py,src_zephyr_integration_shared_events_event_schemas_py,src_zephyr_integration_shared_schema_init_py,src_zephyr_integration_vector_memory_context_ingest_py design
    class D_OPS,D_INFRA_RUNTIME,D_INTELLIGENCE,D_SECURITY,D_SHARED,D_GOV_RULE external_prod
    class D_INFRASTRUCTURE,D_AUTONOMY_CORE,D_GOVERNANCE,D_ORCHESTRATOR,D_GOV_AUDIT,D_SECURITY_LLM external_design
```

#### 第 3 页 / 共 4 页

```mermaid
graph TD
    subgraph D_INTEGRATION["D_INTEGRATION 管线路由"]
        src_zephyr_integration_vector_memory_cross_collection_retriever_py["(原型态 / prototype) CrossCollectionRetriever — MOD-INF-011 跨 Coll...<br/>文件: cross_collection_retriever.py"]
        src_zephyr_integration_vector_memory_delegated_vector_memory_py["(原型态 / prototype) DelegatedVectorMemory — VectorMemoryBase 的 RI...<br/>文件: delegated_vector_memory.py"]
        src_zephyr_integration_vector_memory_design_principles_py["(生产态 / production) design_principles.py"]
        src_zephyr_integration_vector_memory_faiss_collection_manager_py["(生产态 / production) FAISSCollectionManager — FAISS HNSW/IVF+PQ 8 C...<br/>文件: faiss_collection_manager.py"]
        src_zephyr_integration_vector_memory_hybrid_retriever_py["(生产态 / production) HybridRetriever — MOD-INF-011 混合检索架构<br/>文件: hybrid_retriever.py"]
        src_zephyr_integration_vector_memory_in_memory_fake_vms_py["(生产态 / production) InMemoryFakeVMS — MOD-INF-011 · 零依赖测试双胞胎<br/>文件: in_memory_fake_vms.py"]
        src_zephyr_integration_vector_memory_in_memory_memory_backend_py["(生产态 / production) InMemoryMemoryBackend — MOD-INF-011 降级兜底<br/>文件: in_memory_memory_backend.py"]
        src_zephyr_integration_vector_memory_in_process_vector_memory_py["(生产态 / production) InProcessVectorMemory — MOD-INF-011 VMS 统一入口<br/>文件: in_process_vector_memory.py"]
        src_zephyr_integration_vector_memory_index_health_monitor_py["(生产态 / production) IndexHealthMonitor — MOD-INF-011 索引健康自检...<br/>文件: index_health_monitor.py"]
        src_zephyr_integration_vector_memory_interface_py["(生产态 / production) VMS — Vector Memory Service 接口基类<br/>文件: interface.py"]
        src_zephyr_integration_vector_memory_migrate_chroma_to_faiss_py["(原型态 / prototype) ChromDB -> FAISS + SQLite WAL 数据迁移脚本<br/>文件: migrate_chroma_to_faiss.py"]
        src_zephyr_integration_vector_memory_ollama_embedding_py["(原型态 / prototype) ollama_embedding.py"]
        src_zephyr_integration_vector_memory_provenance_enforcer_py["(生产态 / production) ProvenanceEnforcer — MOD-INF-011 写入溯源强制执行<br/>文件: provenance_enforcer.py"]
        src_zephyr_integration_vector_memory_retrieval_feedback_py["(生产态 / production) RetrievalFeedback — MOD-INF-011 FLE 检索质量消费<br/>文件: retrieval_feedback.py"]
        src_zephyr_integration_vector_memory_sqlite_metadata_store_py["(生产态 / production) SQLiteMetadataStore — VMS 元数据存储 (SQLite W...<br/>文件: sqlite_metadata_store.py"]
        src_zephyr_integration_vector_memory_vector_bridge_py["(原型态 / prototype) VectorBridge — MOD-INF-011 CE/KB 外部集成适配器<br/>文件: vector_bridge.py"]
        src_zephyr_integration_vector_memory_vms_config_yaml["(生产态 / production) vms_config.yaml"]
        src_zephyr_integration_vector_memory_vms_errors_py["(生产态 / production) vms_errors.py"]
        src_zephyr_integration_vector_memory_vms_schemas_py["(生产态 / production) VMS 共享数据模型 — MOD-INF-011 · 蓝图 §6.1 ...<br/>文件: vms_schemas.py"]
        src_zephyr_shared_contracts_approval_types_py["(生产态 / production) G-CT-004 — ApprovalRequest Pydantic V2 BaseMod...<br/>文件: approval_types.py"]
        src_zephyr_shared_contracts_protocols_py["(原型态 / prototype) Structural Protocol interfaces for cross-module...<br/>文件: protocols.py"]
        src_zephyr_shared_contracts_rollback_types_py["(生产态 / production) G-CT-003 — RollbackResult Pydantic V2 BaseMode...<br/>文件: rollback_types.py"]
        src_zephyr_shared_contracts_runtime_types_py["(生产态 / production) runtime_types.py"]
        src_zephyr_shared_evaluation_evals_py["(生产态 / production) evals.py"]
        src_zephyr_shared_knowledge_kg_interface_py["(生产态 / production) kg_interface.py"]
        src_zephyr_shared_resilience_durable_execution_py["(生产态 / production) durable_execution.py"]
        src_zephyr_shared_versioning_version_negotiation_py["(生产态 / production) version_negotiation.py"]
        tests_external_test_external_health_py["(原型态 / prototype) test_external_health.py"]
        tests_external_test_external_merkle_proof_py["(原型态 / prototype) test_external_merkle_proof.py"]
        tests_external_test_external_tool_audit_py["(原型态 / prototype) test_external_tool_audit.py"]
    end
    src_zephyr_integration_vector_memory_delegated_vector_memory_py -.->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_interface_py
    src_zephyr_integration_vector_memory_cross_collection_retriever_py -.->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_hybrid_retriever_py
    src_zephyr_integration_vector_memory_design_principles_py -->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_provenance_enforcer_py
    src_zephyr_integration_vector_memory_design_principles_py -->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_vms_errors_py
    src_zephyr_integration_vector_memory_design_principles_py -->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_vms_schemas_py
    src_zephyr_integration_vector_memory_migrate_chroma_to_faiss_py -.->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_faiss_collection_manager_py
    src_zephyr_integration_vector_memory_migrate_chroma_to_faiss_py -.->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_sqlite_metadata_store_py
    src_zephyr_integration_vector_memory_provenance_enforcer_py -->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_vms_schemas_py
    src_zephyr_integration_vector_memory_vector_bridge_py -.->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_in_process_vector_memory_py
    src_zephyr_integration_vector_memory_retrieval_feedback_py -->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_hybrid_retriever_py
    src_zephyr_integration_vector_memory_retrieval_feedback_py -->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_in_process_vector_memory_py
    src_zephyr_integration_vector_memory_in_process_vector_memory_py -->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_hybrid_retriever_py
    src_zephyr_integration_vector_memory_in_process_vector_memory_py -->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_index_health_monitor_py
    src_zephyr_integration_vector_memory_in_process_vector_memory_py -->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_in_memory_memory_backend_py
    src_zephyr_integration_vector_memory_in_process_vector_memory_py -->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_provenance_enforcer_py
    src_zephyr_integration_vector_memory_in_process_vector_memory_py -.->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_vector_bridge_py
    src_zephyr_integration_vector_memory_in_process_vector_memory_py -->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_retrieval_feedback_py
    D_GOV_KB["(原型态 / prototype) D_GOV_KB"]
    src_zephyr_integration_vector_memory_delegated_vector_memory_py -.->|导入依赖 / import_depends| D_GOV_KB
    D_INFRA_RECOVERY["(生产态 / production) D_INFRA_RECOVERY"]
    tests_external_test_external_merkle_proof_py -.->|测试依赖 / test_depends| D_INFRA_RECOVERY
    D_FBL_DETECTORS["(生产态 / production) D_FBL_DETECTORS"]
    tests_external_test_external_health_py -.->|测试依赖 / test_depends| D_FBL_DETECTORS
    D_SHARED["(生产态 / production) D_SHARED"]
    src_zephyr_integration_vector_memory_migrate_chroma_to_faiss_py -.->|导入依赖 / import_depends| D_SHARED
    src_zephyr_integration_vector_memory_vector_bridge_py -.->|导入依赖 / import_depends| D_SHARED
    src_zephyr_integration_vector_memory_sqlite_metadata_store_py -.->|导入依赖 / import_depends| D_SHARED
    src_zephyr_shared_contracts_runtime_types_py -.->|导入依赖 / import_depends| D_SHARED
    src_zephyr_integration_vector_memory_index_health_monitor_py -.->|导入依赖 / import_depends| D_SHARED
    src_zephyr_integration_vector_memory_retrieval_feedback_py -.->|导入依赖 / import_depends| D_SHARED
    src_zephyr_integration_vector_memory_hybrid_retriever_py -.->|导入依赖 / import_depends| D_SHARED
    src_zephyr_shared_contracts_runtime_types_py -.->|导入依赖 / import_depends| D_SHARED
    src_zephyr_shared_contracts_runtime_types_py -->|导入依赖 / import_depends| D_SHARED
    D_GOV_RULE["(生产态 / production) D_GOV_RULE"]
    src_zephyr_shared_contracts_protocols_py -.->|导入依赖 / import_depends| D_GOV_RULE
    D_GOV_AUDIT["(生产态 / production) D_GOV_AUDIT"]
    tests_external_test_external_tool_audit_py -.->|测试依赖 / test_depends| D_GOV_AUDIT
    src_zephyr_integration_vector_memory_vms_schemas_py -.->|导入依赖 / import_depends| D_SHARED
    D_AUTONOMY_CORE["(原型态 / prototype) D_AUTONOMY_CORE"]
    D_AUTONOMY_CORE -.->|测试依赖 / test_depends| src_zephyr_integration_vector_memory_in_memory_fake_vms_py
    D_ORCHESTRATOR["(原型态 / prototype) D_ORCHESTRATOR"]
    D_ORCHESTRATOR -.->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_in_memory_fake_vms_py
    D_INTELLIGENCE["(原型态 / prototype) D_INTELLIGENCE"]
    D_INTELLIGENCE -.->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_in_memory_fake_vms_py
    D_AUTONOMY_CORE -.->|测试依赖 / test_depends| src_zephyr_integration_vector_memory_hybrid_retriever_py
    D_AUTONOMY_CORE -.->|测试依赖 / test_depends| src_zephyr_integration_vector_memory_retrieval_feedback_py
    D_FEEDBACK_LOOP["(生产态 / production) D_FEEDBACK_LOOP"]
    D_FEEDBACK_LOOP -->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_in_process_vector_memory_py
    D_GOV_ENFORCEMENT["(生产态 / production) D_GOV_ENFORCEMENT"]
    D_GOV_ENFORCEMENT -->|导入依赖 / import_depends| src_zephyr_shared_contracts_approval_types_py
    D_GOV_DRIFT["(生产态 / production) D_GOV_DRIFT"]
    D_GOV_DRIFT -.->|导入依赖 / import_depends| src_zephyr_shared_contracts_protocols_py
    D_GOVERNANCE["(原型态 / prototype) D_GOVERNANCE"]
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_shared_contracts_protocols_py
    D_AUTONOMY_CORE -.->|测试依赖 / test_depends| src_zephyr_shared_contracts_rollback_types_py
    D_INFRA_RUNTIME["(生产态 / production) D_INFRA_RUNTIME"]
    D_INFRA_RUNTIME -->|导入依赖 / import_depends| src_zephyr_shared_contracts_runtime_types_py
    D_AUTONOMY_CORE -.->|测试依赖 / test_depends| src_zephyr_shared_contracts_rollback_types_py
    D_AUTONOMY_CORE -.->|测试依赖 / test_depends| src_zephyr_integration_vector_memory_index_health_monitor_py
    D_GOVERNANCE -.->|测试依赖 / test_depends| src_zephyr_shared_contracts_approval_types_py
    D_AUTONOMY_CORE -.->|测试依赖 / test_depends| src_zephyr_integration_vector_memory_in_process_vector_memory_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_integration_vector_memory_design_principles_py,src_zephyr_integration_vector_memory_faiss_collection_manager_py,src_zephyr_integration_vector_memory_hybrid_retriever_py,src_zephyr_integration_vector_memory_in_memory_fake_vms_py,src_zephyr_integration_vector_memory_in_memory_memory_backend_py,src_zephyr_integration_vector_memory_in_process_vector_memory_py,src_zephyr_integration_vector_memory_index_health_monitor_py,src_zephyr_integration_vector_memory_interface_py,src_zephyr_integration_vector_memory_provenance_enforcer_py,src_zephyr_integration_vector_memory_retrieval_feedback_py,src_zephyr_integration_vector_memory_sqlite_metadata_store_py,src_zephyr_integration_vector_memory_vms_config_yaml,src_zephyr_integration_vector_memory_vms_errors_py,src_zephyr_integration_vector_memory_vms_schemas_py,src_zephyr_shared_contracts_approval_types_py,src_zephyr_shared_contracts_rollback_types_py,src_zephyr_shared_contracts_runtime_types_py,src_zephyr_shared_evaluation_evals_py,src_zephyr_shared_knowledge_kg_interface_py,src_zephyr_shared_resilience_durable_execution_py,src_zephyr_shared_versioning_version_negotiation_py production
    class src_zephyr_integration_vector_memory_cross_collection_retriever_py,src_zephyr_integration_vector_memory_delegated_vector_memory_py,src_zephyr_integration_vector_memory_migrate_chroma_to_faiss_py,src_zephyr_integration_vector_memory_ollama_embedding_py,src_zephyr_integration_vector_memory_vector_bridge_py,src_zephyr_shared_contracts_protocols_py,tests_external_test_external_health_py,tests_external_test_external_merkle_proof_py,tests_external_test_external_tool_audit_py design
    class D_INFRA_RECOVERY,D_FBL_DETECTORS,D_SHARED,D_GOV_RULE,D_GOV_AUDIT,D_FEEDBACK_LOOP,D_GOV_ENFORCEMENT,D_GOV_DRIFT,D_INFRA_RUNTIME external_prod
    class D_GOV_KB,D_AUTONOMY_CORE,D_ORCHESTRATOR,D_INTELLIGENCE,D_GOVERNANCE external_design
```

#### 第 4 页 / 共 4 页

```mermaid
graph TD
    subgraph D_INTEGRATION["D_INTEGRATION 管线路由"]
        tests_external_test_external_validation_checkpoint_py["(原型态 / prototype) test_external_validation_checkpoint.py"]
        tests_external_test_external_verifier_py["(原型态 / prototype) test_external_verifier.py"]
    end
    D_FEEDBACK_LOOP["(生产态 / production) D_FEEDBACK_LOOP"]
    tests_external_test_external_verifier_py -.->|测试依赖 / test_depends| D_FEEDBACK_LOOP
    D_FBL_DETECTORS["(生产态 / production) D_FBL_DETECTORS"]
    tests_external_test_external_validation_checkpoint_py -.->|测试依赖 / test_depends| D_FBL_DETECTORS
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class tests_external_test_external_validation_checkpoint_py,tests_external_test_external_verifier_py design
    class D_FEEDBACK_LOOP,D_FBL_DETECTORS external_prod
```

### 运营态子图（仅 design_maturity=production 的模块和依赖）

> 仅展示已上线运行的模块（共 53 个，53 条域内依赖）。

```mermaid
graph TD
    subgraph D_INTEGRATION["D_INTEGRATION 管线路由"]
        src_zephyr_integration_behavioral_admission_admission_response_py["(生产态 / production) admission_response.py"]
        src_zephyr_integration_local_model_cache_layer_py["(生产态 / production) CacheLayer — MOD-INF-011 嵌入缓存与查询结果 LRU<br/>文件: cache_layer.py"]
        src_zephyr_integration_local_model_deepseek_chat_py["(生产态 / production) DeepSeekChat — 通过 DeepSeek API 进行 LLM 推理...<br/>文件: deepseek_chat.py"]
        src_zephyr_integration_local_model_embedding_router_py["(生产态 / production) EmbeddingRouter — MOD-INF-011 双嵌入维度路由<br/>文件: embedding_router.py"]
        src_zephyr_integration_local_model_local_model_scheduler_py["(生产态 / production) LocalModelScheduler — L2 本地模型 24/7 调度循环<br/>文件: local_model_scheduler.py"]
        src_zephyr_integration_local_model_ollama_chat_py["(生产态 / production) OllamaChat — 通过 Ollama HTTP API 进行本地 LLM...<br/>文件: ollama_chat.py"]
        src_zephyr_integration_mcp_base_server_py["(生产态 / production) BaseMCPServer: stdio 传输 + JSON-RPC 2.0 协议基类<br/>文件: _base_server.py"]
        src_zephyr_integration_mcp_audit_logger_py["(生产态 / production) MCP 全量工具调用审计日志（MOD-INF-013 §12 Step...<br/>文件: audit_logger.py"]
        src_zephyr_integration_mcp_blueprint_search_server_py["(生产态 / production) BlueprintSearchServer — MCP Server for bluepri...<br/>文件: blueprint_search_server.py"]
        src_zephyr_integration_mcp_doc_guard_server_py["(生产态 / production) DocGuardServer: 跨会话交接协议服务 MCP Server<br/>文件: doc_guard_server.py"]
        src_zephyr_integration_mcp_error_codes_py["(生产态 / production) MCP 错误码集中注册（MOD-INF-013 §3.4）。<br/>文件: error_codes.py"]
        src_zephyr_integration_mcp_gate_engine_server_py["(生产态 / production) GateEngineServer: 门禁裁决服务 MCP Server<br/>文件: gate_engine_server.py"]
        src_zephyr_integration_mcp_gateway_server_py["(生产态 / production) MCP Gateway 集中式治理节点（MOD-INF-013 §12 Ph...<br/>文件: gateway_server.py"]
        src_zephyr_integration_mcp_knowledge_base_server_py["(生产态 / production) KnowledgeBaseServer: 知识库语义检索 MCP Server<br/>文件: knowledge_base_server.py"]
        src_zephyr_integration_mcp_rate_limiter_py["(生产态 / production) MCP Gateway 同步速率限制器（MOD-INF-013 §12 St...<br/>文件: rate_limiter.py"]
        src_zephyr_integration_mcp_sentinel_server_py["(生产态 / production) SentinelServer: 意图路由哨兵 MCP Server<br/>文件: sentinel_server.py"]
        src_zephyr_integration_mcp_task_manager_server_py["(生产态 / production) ZephyrAlpha MCP Task Manager Server<br/>文件: task_manager_server.py"]
        src_zephyr_integration_mcp_telemetry_server_py["(生产态 / production) ZephyrAlpha MCP Telemetry Server — 系统可观测...<br/>文件: telemetry_server.py"]
        src_zephyr_integration_pipeline_orchestrator_py["(生产态 / production) PipelineOrchestrator — M1-M11 管线协调器<br/>文件: pipeline_orchestrator.py"]
        src_zephyr_integration_shared_events_upgrade_strategy_py["(生产态 / production) EventBus 升级策略引擎<br/>文件: upgrade_strategy.py"]
        src_zephyr_integration_shared_schema_base_config_py["(生产态 / production) base_config.py"]
        src_zephyr_integration_shared_schema_execution_model_py["(生产态 / production) execution_model.py"]
        src_zephyr_integration_shared_schema_schema_registry_py["(生产态 / production) schema_registry.py"]
        src_zephyr_integration_shared_schema_schemas_py["(生产态 / production) schemas.py"]
        src_zephyr_integration_shared_schema_severity_types_py["(生产态 / production) severity_types.py"]
        src_zephyr_integration_vector_memory_init_py["(生产态 / production) Vector Memory Service (VMS) — MOD-INF-011 · v0.7.0<br/>文件: __init__.py"]
        src_zephyr_integration_vector_memory_bm25_index_py["(生产态 / production) BM25Index — MOD-INF-011 稀疏检索组件<br/>文件: bm25_index.py"]
        src_zephyr_integration_vector_memory_bridge_layer_py["(生产态 / production) BridgeLayer — MOD-INF-011 kb/ ↔ VMS 过渡桥接<br/>文件: bridge_layer.py"]
        src_zephyr_integration_vector_memory_cache_layer_py["(生产态 / production) cache_layer.py"]
        src_zephyr_integration_vector_memory_chunk_strategy_router_py["(生产态 / production) ChunkStrategyRouter — MOD-INF-011 分块策略调度<br/>文件: chunk_strategy_router.py"]
        src_zephyr_integration_vector_memory_collection_manager_py["(生产态 / production) CollectionManager — MOD-INF-011 八大 Collectio...<br/>文件: collection_manager.py"]
        src_zephyr_integration_vector_memory_collection_schemas_py["(生产态 / production) collection_schemas.py"]
        src_zephyr_integration_vector_memory_design_principles_py["(生产态 / production) design_principles.py"]
        src_zephyr_integration_vector_memory_faiss_collection_manager_py["(生产态 / production) FAISSCollectionManager — FAISS HNSW/IVF+PQ 8 C...<br/>文件: faiss_collection_manager.py"]
        src_zephyr_integration_vector_memory_hybrid_retriever_py["(生产态 / production) HybridRetriever — MOD-INF-011 混合检索架构<br/>文件: hybrid_retriever.py"]
        src_zephyr_integration_vector_memory_in_memory_fake_vms_py["(生产态 / production) InMemoryFakeVMS — MOD-INF-011 · 零依赖测试双胞胎<br/>文件: in_memory_fake_vms.py"]
        src_zephyr_integration_vector_memory_in_memory_memory_backend_py["(生产态 / production) InMemoryMemoryBackend — MOD-INF-011 降级兜底<br/>文件: in_memory_memory_backend.py"]
        src_zephyr_integration_vector_memory_in_process_vector_memory_py["(生产态 / production) InProcessVectorMemory — MOD-INF-011 VMS 统一入口<br/>文件: in_process_vector_memory.py"]
        src_zephyr_integration_vector_memory_index_health_monitor_py["(生产态 / production) IndexHealthMonitor — MOD-INF-011 索引健康自检...<br/>文件: index_health_monitor.py"]
        src_zephyr_integration_vector_memory_interface_py["(生产态 / production) VMS — Vector Memory Service 接口基类<br/>文件: interface.py"]
        src_zephyr_integration_vector_memory_provenance_enforcer_py["(生产态 / production) ProvenanceEnforcer — MOD-INF-011 写入溯源强制执行<br/>文件: provenance_enforcer.py"]
        src_zephyr_integration_vector_memory_retrieval_feedback_py["(生产态 / production) RetrievalFeedback — MOD-INF-011 FLE 检索质量消费<br/>文件: retrieval_feedback.py"]
        src_zephyr_integration_vector_memory_sqlite_metadata_store_py["(生产态 / production) SQLiteMetadataStore — VMS 元数据存储 (SQLite W...<br/>文件: sqlite_metadata_store.py"]
        src_zephyr_integration_vector_memory_vms_config_yaml["(生产态 / production) vms_config.yaml"]
        src_zephyr_integration_vector_memory_vms_errors_py["(生产态 / production) vms_errors.py"]
        src_zephyr_integration_vector_memory_vms_schemas_py["(生产态 / production) VMS 共享数据模型 — MOD-INF-011 · 蓝图 §6.1 ...<br/>文件: vms_schemas.py"]
        src_zephyr_shared_contracts_approval_types_py["(生产态 / production) G-CT-004 — ApprovalRequest Pydantic V2 BaseMod...<br/>文件: approval_types.py"]
        src_zephyr_shared_contracts_rollback_types_py["(生产态 / production) G-CT-003 — RollbackResult Pydantic V2 BaseMode...<br/>文件: rollback_types.py"]
        src_zephyr_shared_contracts_runtime_types_py["(生产态 / production) runtime_types.py"]
        src_zephyr_shared_evaluation_evals_py["(生产态 / production) evals.py"]
        src_zephyr_shared_knowledge_kg_interface_py["(生产态 / production) kg_interface.py"]
        src_zephyr_shared_resilience_durable_execution_py["(生产态 / production) durable_execution.py"]
        src_zephyr_shared_versioning_version_negotiation_py["(生产态 / production) version_negotiation.py"]
    end
    src_zephyr_integration_local_model_local_model_scheduler_py -->|导入依赖 / import_depends| src_zephyr_integration_local_model_embedding_router_py
    src_zephyr_integration_local_model_local_model_scheduler_py -->|导入依赖 / import_depends| src_zephyr_integration_local_model_ollama_chat_py
    src_zephyr_integration_mcp_blueprint_search_server_py -->|导入依赖 / import_depends| src_zephyr_integration_mcp_base_server_py
    src_zephyr_integration_mcp_doc_guard_server_py -->|导入依赖 / import_depends| src_zephyr_integration_mcp_base_server_py
    src_zephyr_integration_mcp_gate_engine_server_py -->|导入依赖 / import_depends| src_zephyr_integration_mcp_base_server_py
    src_zephyr_integration_pipeline_orchestrator_py -->|导入依赖 / import_depends| src_zephyr_integration_local_model_embedding_router_py
    src_zephyr_integration_pipeline_orchestrator_py -->|导入依赖 / import_depends| src_zephyr_integration_local_model_local_model_scheduler_py
    src_zephyr_integration_mcp_knowledge_base_server_py -->|导入依赖 / import_depends| src_zephyr_integration_mcp_base_server_py
    src_zephyr_integration_mcp_knowledge_base_server_py -->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_in_process_vector_memory_py
    src_zephyr_integration_mcp_gateway_server_py -->|导入依赖 / import_depends| src_zephyr_integration_mcp_audit_logger_py
    src_zephyr_integration_mcp_gateway_server_py -->|导入依赖 / import_depends| src_zephyr_integration_mcp_blueprint_search_server_py
    src_zephyr_integration_mcp_gateway_server_py -->|导入依赖 / import_depends| src_zephyr_integration_mcp_doc_guard_server_py
    src_zephyr_integration_mcp_gateway_server_py -->|导入依赖 / import_depends| src_zephyr_integration_mcp_error_codes_py
    src_zephyr_integration_mcp_gateway_server_py -->|导入依赖 / import_depends| src_zephyr_integration_mcp_gate_engine_server_py
    src_zephyr_integration_mcp_gateway_server_py -->|导入依赖 / import_depends| src_zephyr_integration_mcp_knowledge_base_server_py
    src_zephyr_integration_mcp_gateway_server_py -->|导入依赖 / import_depends| src_zephyr_integration_mcp_rate_limiter_py
    src_zephyr_integration_mcp_gateway_server_py -->|导入依赖 / import_depends| src_zephyr_integration_mcp_telemetry_server_py
    src_zephyr_integration_mcp_gateway_server_py -->|导入依赖 / import_depends| src_zephyr_integration_mcp_sentinel_server_py
    src_zephyr_integration_mcp_gateway_server_py -->|导入依赖 / import_depends| src_zephyr_integration_mcp_task_manager_server_py
    src_zephyr_integration_mcp_gateway_server_py -->|导入依赖 / import_depends| src_zephyr_integration_mcp_base_server_py
    src_zephyr_integration_mcp_sentinel_server_py -->|导入依赖 / import_depends| src_zephyr_integration_mcp_base_server_py
    src_zephyr_integration_mcp_base_server_py -->|导入依赖 / import_depends| src_zephyr_integration_mcp_error_codes_py
    src_zephyr_integration_shared_schema_schemas_py -->|导入依赖 / import_depends| src_zephyr_integration_shared_schema_base_config_py
    src_zephyr_integration_shared_schema_schemas_py -->|导入依赖 / import_depends| src_zephyr_integration_shared_schema_execution_model_py
    src_zephyr_integration_shared_schema_schemas_py -->|导入依赖 / import_depends| src_zephyr_integration_shared_schema_severity_types_py
    src_zephyr_integration_vector_memory_bridge_layer_py -->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_collection_manager_py
    src_zephyr_integration_vector_memory_cache_layer_py -->|导入依赖 / import_depends| src_zephyr_integration_local_model_cache_layer_py
    src_zephyr_integration_vector_memory_collection_manager_py -->|导入依赖 / import_depends| src_zephyr_integration_local_model_embedding_router_py
    src_zephyr_integration_vector_memory_index_health_monitor_py -->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_collection_manager_py
    src_zephyr_integration_vector_memory_in_memory_fake_vms_py -->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_collection_manager_py
    src_zephyr_integration_vector_memory_design_principles_py -->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_collection_schemas_py
    src_zephyr_integration_vector_memory_design_principles_py -->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_provenance_enforcer_py
    src_zephyr_integration_vector_memory_design_principles_py -->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_vms_errors_py
    src_zephyr_integration_vector_memory_design_principles_py -->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_vms_schemas_py
    src_zephyr_integration_vector_memory_faiss_collection_manager_py -->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_collection_manager_py
    src_zephyr_integration_vector_memory_provenance_enforcer_py -->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_collection_manager_py
    src_zephyr_integration_vector_memory_provenance_enforcer_py -->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_vms_schemas_py
    src_zephyr_integration_vector_memory_sqlite_metadata_store_py -->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_collection_manager_py
    src_zephyr_integration_vector_memory_retrieval_feedback_py -->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_hybrid_retriever_py
    src_zephyr_integration_vector_memory_retrieval_feedback_py -->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_in_process_vector_memory_py
    src_zephyr_integration_vector_memory_in_process_vector_memory_py -->|导入依赖 / import_depends| src_zephyr_integration_local_model_cache_layer_py
    src_zephyr_integration_vector_memory_in_process_vector_memory_py -->|导入依赖 / import_depends| src_zephyr_integration_local_model_embedding_router_py
    src_zephyr_integration_vector_memory_in_process_vector_memory_py -->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_bridge_layer_py
    src_zephyr_integration_vector_memory_in_process_vector_memory_py -->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_chunk_strategy_router_py
    src_zephyr_integration_vector_memory_in_process_vector_memory_py -->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_collection_manager_py
    src_zephyr_integration_vector_memory_in_process_vector_memory_py -->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_hybrid_retriever_py
    src_zephyr_integration_vector_memory_in_process_vector_memory_py -->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_index_health_monitor_py
    src_zephyr_integration_vector_memory_in_process_vector_memory_py -->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_in_memory_memory_backend_py
    src_zephyr_integration_vector_memory_in_process_vector_memory_py -->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_provenance_enforcer_py
    src_zephyr_integration_vector_memory_in_process_vector_memory_py -->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_retrieval_feedback_py
    src_zephyr_integration_vector_memory_init_py -->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_interface_py
    src_zephyr_integration_vector_memory_init_py -->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_in_process_vector_memory_py
    src_zephyr_integration_vector_memory_vms_config_yaml -->|config_depends / config_depends| src_zephyr_integration_vector_memory_init_py
    D_GOVERNANCE["(生产态 / production) D_GOVERNANCE"]
    src_zephyr_integration_mcp_task_manager_server_py -->|导入依赖 / import_depends| D_GOVERNANCE
    D_OPS["(生产态 / production) D_OPS"]
    src_zephyr_integration_local_model_deepseek_chat_py -->|导入依赖 / import_depends| D_OPS
    src_zephyr_integration_pipeline_orchestrator_py -->|导入依赖 / import_depends| D_OPS
    D_INFRA_RUNTIME["(生产态 / production) D_INFRA_RUNTIME"]
    src_zephyr_integration_pipeline_orchestrator_py -->|导入依赖 / import_depends| D_INFRA_RUNTIME
    src_zephyr_integration_pipeline_orchestrator_py -->|导入依赖 / import_depends| D_INFRA_RUNTIME
    src_zephyr_integration_pipeline_orchestrator_py -->|导入依赖 / import_depends| D_INFRA_RUNTIME
    src_zephyr_integration_pipeline_orchestrator_py -->|导入依赖 / import_depends| D_INFRA_RUNTIME
    src_zephyr_integration_pipeline_orchestrator_py -->|导入依赖 / import_depends| D_INFRA_RUNTIME
    src_zephyr_integration_mcp_telemetry_server_py -.->|导入依赖 / import_depends| D_INFRA_RUNTIME
    src_zephyr_integration_mcp_gateway_server_py -->|导入依赖 / import_depends| D_GOVERNANCE
    D_INTELLIGENCE["(生产态 / production) D_INTELLIGENCE"]
    src_zephyr_integration_pipeline_orchestrator_py -->|导入依赖 / import_depends| D_INTELLIGENCE
    src_zephyr_integration_pipeline_orchestrator_py -->|导入依赖 / import_depends| D_INTELLIGENCE
    D_SECURITY["(生产态 / production) D_SECURITY"]
    src_zephyr_integration_mcp_gateway_server_py -->|导入依赖 / import_depends| D_SECURITY
    src_zephyr_integration_pipeline_orchestrator_py -->|导入依赖 / import_depends| D_SECURITY
    src_zephyr_integration_pipeline_orchestrator_py -->|导入依赖 / import_depends| D_INFRA_RUNTIME
    D_AUTONOMY_CORE["(原型态 / prototype) D_AUTONOMY_CORE"]
    D_AUTONOMY_CORE -.->|测试依赖 / test_depends| src_zephyr_integration_local_model_cache_layer_py
    D_AUTONOMY_CORE -.->|测试依赖 / test_depends| src_zephyr_integration_local_model_embedding_router_py
    D_AUTONOMY_CORE -->|导入依赖 / import_depends| src_zephyr_integration_local_model_embedding_router_py
    D_AUTONOMY_CORE -.->|测试依赖 / test_depends| src_zephyr_integration_local_model_embedding_router_py
    D_INFRA_RUNTIME -->|导入依赖 / import_depends| src_zephyr_integration_local_model_local_model_scheduler_py
    D_INFRA_RUNTIME -->|导入依赖 / import_depends| src_zephyr_integration_local_model_local_model_scheduler_py
    D_AUTONOMY_CORE -.->|测试依赖 / test_depends| src_zephyr_integration_local_model_local_model_scheduler_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_integration_local_model_local_model_scheduler_py
    D_INTELLIGENCE -.->|导入依赖 / import_depends| src_zephyr_integration_local_model_ollama_chat_py
    D_INTEGRATION_GATEWAY["(原型态 / prototype) D_INTEGRATION_GATEWAY"]
    D_INTEGRATION_GATEWAY -.->|导入依赖 / import_depends| src_zephyr_integration_mcp_gate_engine_server_py
    D_INFRA_RUNTIME -->|导入依赖 / import_depends| src_zephyr_integration_pipeline_orchestrator_py
    D_INTELLIGENCE -.->|测试依赖 / test_depends| src_zephyr_integration_pipeline_orchestrator_py
    D_INTELLIGENCE -.->|测试依赖 / test_depends| src_zephyr_integration_pipeline_orchestrator_py
    D_INTEGRATION_GATEWAY -.->|导入依赖 / import_depends| src_zephyr_integration_mcp_telemetry_server_py
    D_INTEGRATION_GATEWAY -.->|导入依赖 / import_depends| src_zephyr_integration_mcp_sentinel_server_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_integration_behavioral_admission_admission_response_py,src_zephyr_integration_local_model_cache_layer_py,src_zephyr_integration_local_model_deepseek_chat_py,src_zephyr_integration_local_model_embedding_router_py,src_zephyr_integration_local_model_local_model_scheduler_py,src_zephyr_integration_local_model_ollama_chat_py,src_zephyr_integration_mcp_base_server_py,src_zephyr_integration_mcp_audit_logger_py,src_zephyr_integration_mcp_blueprint_search_server_py,src_zephyr_integration_mcp_doc_guard_server_py,src_zephyr_integration_mcp_error_codes_py,src_zephyr_integration_mcp_gate_engine_server_py,src_zephyr_integration_mcp_gateway_server_py,src_zephyr_integration_mcp_knowledge_base_server_py,src_zephyr_integration_mcp_rate_limiter_py,src_zephyr_integration_mcp_sentinel_server_py,src_zephyr_integration_mcp_task_manager_server_py,src_zephyr_integration_mcp_telemetry_server_py,src_zephyr_integration_pipeline_orchestrator_py,src_zephyr_integration_shared_events_upgrade_strategy_py,src_zephyr_integration_shared_schema_base_config_py,src_zephyr_integration_shared_schema_execution_model_py,src_zephyr_integration_shared_schema_schema_registry_py,src_zephyr_integration_shared_schema_schemas_py,src_zephyr_integration_shared_schema_severity_types_py,src_zephyr_integration_vector_memory_init_py,src_zephyr_integration_vector_memory_bm25_index_py,src_zephyr_integration_vector_memory_bridge_layer_py,src_zephyr_integration_vector_memory_cache_layer_py,src_zephyr_integration_vector_memory_chunk_strategy_router_py,src_zephyr_integration_vector_memory_collection_manager_py,src_zephyr_integration_vector_memory_collection_schemas_py,src_zephyr_integration_vector_memory_design_principles_py,src_zephyr_integration_vector_memory_faiss_collection_manager_py,src_zephyr_integration_vector_memory_hybrid_retriever_py,src_zephyr_integration_vector_memory_in_memory_fake_vms_py,src_zephyr_integration_vector_memory_in_memory_memory_backend_py,src_zephyr_integration_vector_memory_in_process_vector_memory_py,src_zephyr_integration_vector_memory_index_health_monitor_py,src_zephyr_integration_vector_memory_interface_py,src_zephyr_integration_vector_memory_provenance_enforcer_py,src_zephyr_integration_vector_memory_retrieval_feedback_py,src_zephyr_integration_vector_memory_sqlite_metadata_store_py,src_zephyr_integration_vector_memory_vms_config_yaml,src_zephyr_integration_vector_memory_vms_errors_py,src_zephyr_integration_vector_memory_vms_schemas_py,src_zephyr_shared_contracts_approval_types_py,src_zephyr_shared_contracts_rollback_types_py,src_zephyr_shared_contracts_runtime_types_py,src_zephyr_shared_evaluation_evals_py,src_zephyr_shared_knowledge_kg_interface_py,src_zephyr_shared_resilience_durable_execution_py,src_zephyr_shared_versioning_version_negotiation_py production
    class D_GOVERNANCE,D_OPS,D_INFRA_RUNTIME,D_INTELLIGENCE,D_SECURITY external_prod
    class D_AUTONOMY_CORE,D_INTEGRATION_GATEWAY external_design
```

### 设计态子图（仅 design_maturity=design 的模块和依赖）

> 仅展示蓝图阶段、代码未写的设计态模块（共 0 个，0 条域内依赖）。

> （无设计态模块 / No design modules）

### 原型态子图（仅 design_maturity=prototype 的模块和依赖）

> 仅展示代码已写、验证中未稳定上线的原型态模块（共 39 个，17 条域内依赖）。

```mermaid
graph TD
    subgraph D_INTEGRATION["D_INTEGRATION 管线路由"]
        src_zephyr_integration_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_integration_behavioral_admission_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_integration_budget_enforcer_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_integration_budget_enforcer_degradation_spiral_detector_py["(原型态 / prototype) Degradation Spiral Detector — 模型幻觉-容量正...<br/>文件: degradation_spiral_detector.py"]
        src_zephyr_integration_llm_bridge_py["(原型态 / prototype) 接收 RED 问题,生成修复文本。LLM 只润色不做判断...<br/>文件: llm_bridge.py"]
        src_zephyr_integration_local_model_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_integration_local_model_ollama_embedding_py["(原型态 / prototype) OllamaEmbedder — 通过 Ollama HTTP API 生成文本嵌入<br/>文件: ollama_embedding.py"]
        src_zephyr_integration_mcp_handoff_auto_loader_py["(原型态 / prototype) Handoff 自动加载器——从 handoff 包恢复 AI sess...<br/>文件: handoff_auto_loader.py"]
        src_zephyr_integration_mcp_prompt_provider_py["(原型态 / prototype) MCP Prompt 模板提供者（MOD-INF-013 Phase 6 — ...<br/>文件: prompt_provider.py"]
        src_zephyr_integration_mcp_resource_provider_py["(原型态 / prototype) MCP Resource 提供者（MOD-INF-013 Phase 6 — 关...<br/>文件: resource_provider.py"]
        src_zephyr_integration_mcp_sandbox_server_py["(原型态 / prototype) MCP sandbox 安全代码执行沙箱（MOD-INF-013 Phase...<br/>文件: sandbox_server.py"]
        src_zephyr_integration_mcp_vector_memory_server_py["(原型态 / prototype) VectorMemoryServer: VMS 向量记忆 MCP Server (MO...<br/>文件: vector_memory_server.py"]
        src_zephyr_integration_mcp_server_py["(原型态 / prototype) AssetInventory MCP Server — MOD-INF-026 蓝图 §21<br/>文件: mcp_server.py"]
        src_zephyr_integration_ports_py["(原型态 / prototype) Protocol-based interface layer for pipeline->mc...<br/>文件: ports.py"]
        src_zephyr_integration_shared_contracts_errors_init_py["(原型态 / prototype) Auto-generated contracts package — errors<br/>文件: __init__.py"]
        src_zephyr_integration_shared_contracts_errors_contract_violation_error_py["(原型态 / prototype) contract_violation_error.py"]
        src_zephyr_integration_shared_contracts_errors_data_quality_error_py["(原型态 / prototype) CTR-ERR-001: DataQualityError / 行情质量门禁不...<br/>文件: data_quality_error.py"]
        src_zephyr_integration_shared_contracts_errors_execution_rejection_error_py["(原型态 / prototype) execution_rejection_error.py"]
        src_zephyr_integration_shared_contracts_errors_factor_computation_error_py["(原型态 / prototype) CTR-ERR-002: FactorComputationError / 因子计算...<br/>文件: factor_computation_error.py"]
        src_zephyr_integration_shared_contracts_errors_risk_limit_violation_error_py["(原型态 / prototype) risk_limit_violation_error.py"]
        src_zephyr_integration_shared_contracts_errors_signal_degradation_warning_py["(原型态 / prototype) signal_degradation_warning.py"]
        src_zephyr_integration_shared_events_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_integration_shared_events_dlq_py["(原型态 / prototype) dlq.py —— ZephyrAlpha 死信队列（Dead Letter Q...<br/>文件: dlq.py"]
        src_zephyr_integration_shared_events_dlq_bridge_py["(原型态 / prototype) CT-DLQ-001: DeadLetterQueue -> System Event Bus...<br/>文件: dlq_bridge.py"]
        src_zephyr_integration_shared_events_event_bus_upgrade_py["(原型态 / prototype) EventBus Upgrade — 事件总线升级 (M-16)<br/>文件: event_bus_upgrade.py"]
        src_zephyr_integration_shared_events_event_schemas_py["(原型态 / prototype) event_schemas.py —— Observer 事件体 Pydantic ...<br/>文件: event_schemas.py"]
        src_zephyr_integration_shared_schema_init_py["(原型态 / prototype) shared.schema — auto-generated package init.<br/>文件: __init__.py"]
        src_zephyr_integration_vector_memory_context_ingest_py["(原型态 / prototype) VMS 上下文注入器 — ingest_context() 消费者<br/>文件: context_ingest.py"]
        src_zephyr_integration_vector_memory_cross_collection_retriever_py["(原型态 / prototype) CrossCollectionRetriever — MOD-INF-011 跨 Coll...<br/>文件: cross_collection_retriever.py"]
        src_zephyr_integration_vector_memory_delegated_vector_memory_py["(原型态 / prototype) DelegatedVectorMemory — VectorMemoryBase 的 RI...<br/>文件: delegated_vector_memory.py"]
        src_zephyr_integration_vector_memory_migrate_chroma_to_faiss_py["(原型态 / prototype) ChromDB -> FAISS + SQLite WAL 数据迁移脚本<br/>文件: migrate_chroma_to_faiss.py"]
        src_zephyr_integration_vector_memory_ollama_embedding_py["(原型态 / prototype) ollama_embedding.py"]
        src_zephyr_integration_vector_memory_vector_bridge_py["(原型态 / prototype) VectorBridge — MOD-INF-011 CE/KB 外部集成适配器<br/>文件: vector_bridge.py"]
        src_zephyr_shared_contracts_protocols_py["(原型态 / prototype) Structural Protocol interfaces for cross-module...<br/>文件: protocols.py"]
        tests_external_test_external_health_py["(原型态 / prototype) test_external_health.py"]
        tests_external_test_external_merkle_proof_py["(原型态 / prototype) test_external_merkle_proof.py"]
        tests_external_test_external_tool_audit_py["(原型态 / prototype) test_external_tool_audit.py"]
        tests_external_test_external_validation_checkpoint_py["(原型态 / prototype) test_external_validation_checkpoint.py"]
        tests_external_test_external_verifier_py["(原型态 / prototype) test_external_verifier.py"]
    end
    src_zephyr_integration_ports_py -.->|config_depends / config_depends| src_zephyr_integration_init_py
    src_zephyr_integration_init_py -.->|导入依赖 / import_depends| src_zephyr_integration_llm_bridge_py
    src_zephyr_integration_init_py -.->|导入依赖 / import_depends| src_zephyr_integration_mcp_server_py
    src_zephyr_integration_budget_enforcer_degradation_spiral_detector_py -.->|config_depends / config_depends| src_zephyr_integration_budget_enforcer_init_py
    src_zephyr_integration_local_model_init_py -.->|导入依赖 / import_depends| src_zephyr_integration_local_model_ollama_embedding_py
    src_zephyr_integration_shared_contracts_errors_init_py -.->|导入依赖 / import_depends| src_zephyr_integration_shared_contracts_errors_contract_violation_error_py
    src_zephyr_integration_shared_contracts_errors_init_py -.->|导入依赖 / import_depends| src_zephyr_integration_shared_contracts_errors_data_quality_error_py
    src_zephyr_integration_shared_contracts_errors_init_py -.->|导入依赖 / import_depends| src_zephyr_integration_shared_contracts_errors_factor_computation_error_py
    src_zephyr_integration_shared_contracts_errors_init_py -.->|导入依赖 / import_depends| src_zephyr_integration_shared_contracts_errors_execution_rejection_error_py
    src_zephyr_integration_shared_contracts_errors_init_py -.->|导入依赖 / import_depends| src_zephyr_integration_shared_contracts_errors_risk_limit_violation_error_py
    src_zephyr_integration_shared_contracts_errors_init_py -.->|导入依赖 / import_depends| src_zephyr_integration_shared_contracts_errors_signal_degradation_warning_py
    src_zephyr_integration_shared_events_dlq_bridge_py -.->|导入依赖 / import_depends| src_zephyr_integration_shared_events_dlq_py
    src_zephyr_integration_shared_events_init_py -.->|导入依赖 / import_depends| src_zephyr_integration_shared_events_dlq_py
    src_zephyr_integration_shared_events_init_py -.->|导入依赖 / import_depends| src_zephyr_integration_shared_events_dlq_bridge_py
    src_zephyr_integration_shared_events_init_py -.->|导入依赖 / import_depends| src_zephyr_integration_shared_events_event_bus_upgrade_py
    src_zephyr_integration_shared_events_init_py -.->|导入依赖 / import_depends| src_zephyr_integration_shared_events_event_schemas_py
    src_zephyr_integration_vector_memory_ollama_embedding_py -.->|导入依赖 / import_depends| src_zephyr_integration_local_model_ollama_embedding_py
    D_FEEDBACK_LOOP["(生产态 / production) D_FEEDBACK_LOOP"]
    tests_external_test_external_verifier_py -.->|测试依赖 / test_depends| D_FEEDBACK_LOOP
    D_GOV_AUDIT["(生产态 / production) D_GOV_AUDIT"]
    src_zephyr_integration_llm_bridge_py -.->|导入依赖 / import_depends| D_GOV_AUDIT
    D_GOV_KB["(原型态 / prototype) D_GOV_KB"]
    src_zephyr_integration_vector_memory_delegated_vector_memory_py -.->|导入依赖 / import_depends| D_GOV_KB
    D_INFRA_RECOVERY["(生产态 / production) D_INFRA_RECOVERY"]
    tests_external_test_external_merkle_proof_py -.->|测试依赖 / test_depends| D_INFRA_RECOVERY
    D_FBL_DETECTORS["(生产态 / production) D_FBL_DETECTORS"]
    tests_external_test_external_health_py -.->|测试依赖 / test_depends| D_FBL_DETECTORS
    D_SHARED["(生产态 / production) D_SHARED"]
    src_zephyr_integration_shared_events_dlq_py -.->|导入依赖 / import_depends| D_SHARED
    src_zephyr_integration_mcp_server_py -.->|导入依赖 / import_depends| D_SHARED
    src_zephyr_integration_shared_contracts_errors_data_quality_error_py -.->|导入依赖 / import_depends| D_SHARED
    src_zephyr_integration_local_model_ollama_embedding_py -.->|导入依赖 / import_depends| D_SHARED
    src_zephyr_integration_shared_events_event_schemas_py -.->|导入依赖 / import_depends| D_SHARED
    src_zephyr_integration_mcp_server_py -.->|导入依赖 / import_depends| D_SHARED
    src_zephyr_integration_vector_memory_migrate_chroma_to_faiss_py -.->|导入依赖 / import_depends| D_SHARED
    src_zephyr_integration_mcp_resource_provider_py -.->|导入依赖 / import_depends| D_SHARED
    src_zephyr_integration_vector_memory_vector_bridge_py -.->|导入依赖 / import_depends| D_SHARED
    src_zephyr_integration_shared_events_dlq_bridge_py -.->|导入依赖 / import_depends| D_SHARED
    D_GOVERNANCE["(原型态 / prototype) D_GOVERNANCE"]
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_integration_init_py
    D_GOV_SCRIPTS["(原型态 / prototype) D_GOV_SCRIPTS"]
    D_GOV_SCRIPTS -.->|导入依赖 / import_depends| src_zephyr_integration_init_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_integration_init_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_integration_init_py
    D_GOV_SCRIPTS -.->|导入依赖 / import_depends| src_zephyr_integration_init_py
    D_INTEGRATION_GATEWAY["(原型态 / prototype) D_INTEGRATION_GATEWAY"]
    D_INTEGRATION_GATEWAY -.->|导入依赖 / import_depends| src_zephyr_integration_mcp_prompt_provider_py
    D_INTEGRATION_GATEWAY -.->|导入依赖 / import_depends| src_zephyr_integration_mcp_sandbox_server_py
    D_INTEGRATION_GATEWAY -.->|导入依赖 / import_depends| src_zephyr_integration_mcp_vector_memory_server_py
    D_AUTONOMY_CORE["(原型态 / prototype) D_AUTONOMY_CORE"]
    D_AUTONOMY_CORE -.->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_context_ingest_py
    D_INTEGRATION_GATEWAY -.->|导入依赖 / import_depends| src_zephyr_integration_mcp_handoff_auto_loader_py
    D_GOV_DRIFT["(生产态 / production) D_GOV_DRIFT"]
    D_GOV_DRIFT -.->|导入依赖 / import_depends| src_zephyr_shared_contracts_protocols_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_shared_contracts_protocols_py
    D_INTEGRATION_GATEWAY -.->|导入依赖 / import_depends| src_zephyr_integration_mcp_resource_provider_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_integration_init_py
    D_AUTONOMY_CORE -.->|导入依赖 / import_depends| src_zephyr_shared_contracts_protocols_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_integration_init_py,src_zephyr_integration_behavioral_admission_init_py,src_zephyr_integration_budget_enforcer_init_py,src_zephyr_integration_budget_enforcer_degradation_spiral_detector_py,src_zephyr_integration_llm_bridge_py,src_zephyr_integration_local_model_init_py,src_zephyr_integration_local_model_ollama_embedding_py,src_zephyr_integration_mcp_handoff_auto_loader_py,src_zephyr_integration_mcp_prompt_provider_py,src_zephyr_integration_mcp_resource_provider_py,src_zephyr_integration_mcp_sandbox_server_py,src_zephyr_integration_mcp_vector_memory_server_py,src_zephyr_integration_mcp_server_py,src_zephyr_integration_ports_py,src_zephyr_integration_shared_contracts_errors_init_py,src_zephyr_integration_shared_contracts_errors_contract_violation_error_py,src_zephyr_integration_shared_contracts_errors_data_quality_error_py,src_zephyr_integration_shared_contracts_errors_execution_rejection_error_py,src_zephyr_integration_shared_contracts_errors_factor_computation_error_py,src_zephyr_integration_shared_contracts_errors_risk_limit_violation_error_py,src_zephyr_integration_shared_contracts_errors_signal_degradation_warning_py,src_zephyr_integration_shared_events_init_py,src_zephyr_integration_shared_events_dlq_py,src_zephyr_integration_shared_events_dlq_bridge_py,src_zephyr_integration_shared_events_event_bus_upgrade_py,src_zephyr_integration_shared_events_event_schemas_py,src_zephyr_integration_shared_schema_init_py,src_zephyr_integration_vector_memory_context_ingest_py,src_zephyr_integration_vector_memory_cross_collection_retriever_py,src_zephyr_integration_vector_memory_delegated_vector_memory_py,src_zephyr_integration_vector_memory_migrate_chroma_to_faiss_py,src_zephyr_integration_vector_memory_ollama_embedding_py,src_zephyr_integration_vector_memory_vector_bridge_py,src_zephyr_shared_contracts_protocols_py,tests_external_test_external_health_py,tests_external_test_external_merkle_proof_py,tests_external_test_external_tool_audit_py,tests_external_test_external_validation_checkpoint_py,tests_external_test_external_verifier_py design
    class D_FEEDBACK_LOOP,D_GOV_AUDIT,D_INFRA_RECOVERY,D_FBL_DETECTORS,D_SHARED,D_GOV_DRIFT external_prod
    class D_GOV_KB,D_GOVERNANCE,D_GOV_SCRIPTS,D_INTEGRATION_GATEWAY,D_AUTONOMY_CORE external_design
```

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

| # | 本域模块 / Source Module | → | 外部域-目标模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | SentinelServer: 意图路由哨兵 MCP Server (sentin... | → | D_AUTONOMY_CORE 自治核心: IntentKeywordMapper - Stage 1 of three-stage in... | 导入依赖 / import_depends |
| 2 | PipelineOrchestrator — M1-M11 管线协调器 (pipe... | → | D_AUTONOMY_CORE 自治核心: PipelineSkillBridge — Agent Spec -> Pipeline .... | 导入依赖 / import_depends |
| 3 | PipelineOrchestrator — M1-M11 管线协调器 (pipe... | → | D_AUTONOMY_CORE 自治核心: MOD-INF-019: Agent Spec — Skill Feedback Loop ... | 导入依赖 / import_depends |
| 4 | test_external_health.py | → | D_FBL_DETECTORS: External Health Monitor — v0.14.0 R193 (extern... | 测试依赖 / test_depends |
| 5 | test_external_validation_checkpoint.py | → | D_FBL_DETECTORS: R524: ExternalValidationCheckpoint (external_va... | 测试依赖 / test_depends |
| 6 | test_external_verifier.py | → | D_FEEDBACK_LOOP 反馈循环引擎: External Verifier — v0.15.0 R203 (external_ver... | 测试依赖 / test_depends |
| 7 | BaseMCPServer: stdio 传输 + JSON-RPC 2.0 协议基... | → | D_GOVERNANCE 生命周期管理: G-CT-007 契约：Budget -> RBAC 配额限制. (rbac_b... | 导入依赖 / import_depends |
| 8 | MCP Gateway 集中式治理节点（MOD-INF-013 §12 Ph... | → | D_GOVERNANCE 生命周期管理: GovernanceServer: 治理域统一MCP入口 (governance... | 导入依赖 / import_depends |
| 9 | ZephyrAlpha MCP Task Manager Server (task_manag... | → | D_GOVERNANCE 生命周期管理: PathResolver — 模块路径解析器 (path_resolver.py) | 导入依赖 / import_depends |
| 10 | PipelineOrchestrator — M1-M11 管线协调器 (pipe... | → | D_GOVERNANCE 生命周期管理: G-CT-007 契约：Budget -> RBAC 配额限制. (rbac_b... | 导入依赖 / import_depends |
| 11 | 接收 RED 问题,生成修复文本。LLM 只润色不做判断.... | → | D_GOV_AUDIT 审计追踪: 语义审计管线数据模型 — MOD-INF-028 §4.2 (mode... | 导入依赖 / import_depends |
| 12 | MCP 全量工具调用审计日志（MOD-INF-013 §12 Step... | → | D_GOV_AUDIT 审计追踪: writer.py | 导入依赖 / import_depends |
| 13 | PipelineOrchestrator — M1-M11 管线协调器 (pipe... | → | D_GOV_AUDIT 审计追踪: writer.py | 导入依赖 / import_depends |
| 14 | test_external_tool_audit.py | → | D_GOV_AUDIT 审计追踪: external_tool_audit.py | 测试依赖 / test_depends |
| 15 | KnowledgeBaseServer: 知识库语义检索 MCP Server ... | → | D_GOV_KB 知识库治理: SRC-0042: Re-export shim -> 真源在 kb/storage/u... | 导入依赖 / import_depends |
| 16 | Vector Memory Service (VMS) — MOD-INF-011 · v... | → | D_GOV_KB 知识库治理: SRC-0042: Re-export shim -> 真源在 kb/storage/u... | 导入依赖 / import_depends |
| 17 | DelegatedVectorMemory — VectorMemoryBase 的 RI... | → | D_GOV_KB 知识库治理: SRC-0042: Re-export shim -> 真源在 kb/storage/u... | 导入依赖 / import_depends |
| 18 | ZephyrAlpha MCP Task Manager Server (task_manag... | → | D_GOV_RULE 规则治理: task_types.py | 导入依赖 / import_depends |
| 19 | Structural Protocol interfaces for cross-module... | → | D_GOV_RULE 规则治理: gate_types.py | 导入依赖 / import_depends |
| 20 | PipelineOrchestrator — M1-M11 管线协调器 (pipe... | → | D_INFRASTRUCTURE: __init__.py | 导入依赖 / import_depends |
| 21 | PipelineOrchestrator — M1-M11 管线协调器 (pipe... | → | D_INFRA_RECOVERY 回滚恢复: CT-RBK-GATE-001 集成契约落地——Rollback System... | 导入依赖 / import_depends |
| 22 | test_external_merkle_proof.py | → | D_INFRA_RECOVERY 回滚恢复: External Merkle Proof — 外部可验证回滚完整性证... | 测试依赖 / test_depends |
| 23 | LocalModelScheduler — L2 本地模型 24/7 调度循... | → | D_INFRA_RUNTIME 运行时集成: resource_optimization.py - MAPE-K autonomic res... | 导入依赖 / import_depends |
| 24 | ZephyrAlpha MCP Telemetry Server — 系统可观测.... | → | D_INFRA_RUNTIME 运行时集成: Telemetry — 系统遥测门面类（MOD-INF-015 v2.1.0... | 导入依赖 / import_depends |
| 25 | PipelineOrchestrator — M1-M11 管线协调器 (pipe... | → | D_INFRA_RUNTIME 运行时集成: CircuitBreakerManager -- standalone circuit bre... | 导入依赖 / import_depends |
| 26 | PipelineOrchestrator — M1-M11 管线协调器 (pipe... | → | D_INFRA_RUNTIME 运行时集成: CostTracker —— LLM 调用成本追踪器（SRC-0025）... | 导入依赖 / import_depends |
| 27 | PipelineOrchestrator — M1-M11 管线协调器 (pipe... | → | D_INFRA_RUNTIME 运行时集成: CT-PIPE-ORC-001 — TaskCard -> 管线入口节点路由... | 导入依赖 / import_depends |
| 28 | PipelineOrchestrator — M1-M11 管线协调器 (pipe... | → | D_INFRA_RUNTIME 运行时集成: DeadLetterQueue — 死信队列 (dead_letter_queue.py) | 导入依赖 / import_depends |
| 29 | PipelineOrchestrator — M1-M11 管线协调器 (pipe... | → | D_INFRA_RUNTIME 运行时集成: ModelRouter — 模型路由与降级链管理 (model_rout... | 导入依赖 / import_depends |
| 30 | PipelineOrchestrator — M1-M11 管线协调器 (pipe... | → | D_INFRA_RUNTIME 运行时集成: Pipeline 数据模型 (models.py) | 导入依赖 / import_depends |
| 31 | PipelineOrchestrator — M1-M11 管线协调器 (pipe... | → | D_INFRA_RUNTIME 运行时集成: Pipeline -> Agent Bridge — 双编排器桥接层 (pip... | 导入依赖 / import_depends |
| 32 | PipelineOrchestrator — M1-M11 管线协调器 (pipe... | → | D_INFRA_RUNTIME 运行时集成: Pipeline Lock — 双管线并发锁 (pipeline_lock.py) | 导入依赖 / import_depends |
| 33 | PipelineOrchestrator — M1-M11 管线协调器 (pipe... | → | D_INFRA_RUNTIME 运行时集成: PreemptionManager -- 优先级抢占管理器 (preempti... | 导入依赖 / import_depends |
| 34 | PipelineOrchestrator — M1-M11 管线协调器 (pipe... | → | D_INFRA_RUNTIME 运行时集成: Pipeline Routing Plugin System — K8s Schedulin... | 导入依赖 / import_depends |
| 35 | PipelineOrchestrator — M1-M11 管线协调器 (pipe... | → | D_INFRA_RUNTIME 运行时集成: hooks.py —— 模块生命周期钩子（Phase 2 新增 | ... | 导入依赖 / import_depends |
| 36 | PipelineOrchestrator — M1-M11 管线协调器 (pipe... | → | D_INFRA_RUNTIME 运行时集成: A2A Layer3 Coordination — shared Protocol inte... | 导入依赖 / import_depends |
| 37 | PipelineOrchestrator — M1-M11 管线协调器 (pipe... | → | D_INTELLIGENCE 上下文管理: Cross-Encoder 重排序层 — BGE-reranker-v2-m3（T... | 导入依赖 / import_depends |
| 38 | PipelineOrchestrator — M1-M11 管线协调器 (pipe... | → | D_INTELLIGENCE 上下文管理: ModelProfiler — 核心性能分析引擎 (profiler.py) | 导入依赖 / import_depends |
| 39 | PipelineOrchestrator — M1-M11 管线协调器 (pipe... | → | D_INTELLIGENCE 上下文管理: Results Writer — 持久化 benchmark 结果，支持历... | 导入依赖 / import_depends |
| 40 | DeepSeekChat — 通过 DeepSeek API 进行 LLM 推理... | → | D_OPS 反馈循环: Budget Enforcer core engine — MOD-INF-024 (bud... | 导入依赖 / import_depends |
| 41 | OllamaChat — 通过 Ollama HTTP API 进行本地 LLM... | → | D_OPS 反馈循环: Budget Enforcer core engine — MOD-INF-024 (bud... | 导入依赖 / import_depends |
| 42 | PipelineOrchestrator — M1-M11 管线协调器 (pipe... | → | D_OPS 反馈循环: Budget Enforcer core engine — MOD-INF-024 (bud... | 导入依赖 / import_depends |
| 43 | PipelineOrchestrator — M1-M11 管线协调器 (pipe... | → | D_OPS 反馈循环: Budget Enforcer data models — MOD-INF-024 (bud... | 导入依赖 / import_depends |
| 44 | MCP Gateway 集中式治理节点（MOD-INF-013 §12 Ph... | → | D_SECURITY 对抗验证: gateway.py | 导入依赖 / import_depends |
| 45 | MCP Gateway 集中式治理节点（MOD-INF-013 §12 Ph... | → | D_SECURITY 对抗验证: protocol.py | 导入依赖 / import_depends |
| 46 | PipelineOrchestrator — M1-M11 管线协调器 (pipe... | → | D_SECURITY 对抗验证: gateway.py | 导入依赖 / import_depends |
| 47 | DeepSeekChat — 通过 DeepSeek API 进行 LLM 推理... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of... | 导入依赖 / import_depends |
| 48 | DeepSeekChat — 通过 DeepSeek API 进行 LLM 推理... | → | D_SHARED 共享服务: secrets.py —— Secrets 管理抽象（Phase 7 新增 ... | 导入依赖 / import_depends |
| 49 | OllamaChat — 通过 Ollama HTTP API 进行本地 LLM... | → | D_SHARED 共享服务: constants.py —— 共享枚举 & 常量集中 re-export... | 导入依赖 / import_depends |
| 50 | OllamaEmbedder — 通过 Ollama HTTP API 生成文本... | → | D_SHARED 共享服务: constants.py —— 共享枚举 & 常量集中 re-export... | 导入依赖 / import_depends |
| 51 | BaseMCPServer: stdio 传输 + JSON-RPC 2.0 协议基... | → | D_SHARED 共享服务: async_utils.py — async/sync 边界桥接（5.12.8 .... | 导入依赖 / import_depends |
| 52 | MCP 全量工具调用审计日志（MOD-INF-013 §12 Step... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of... | 导入依赖 / import_depends |
| 53 | BlueprintSearchServer — MCP Server for bluepri... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of... | 导入依赖 / import_depends |
| 54 | DocGuardServer: 跨会话交接协议服务 MCP Server (... | → | D_SHARED 共享服务: schemas.py | 导入依赖 / import_depends |
| 55 | DocGuardServer: 跨会话交接协议服务 MCP Server (... | → | D_SHARED 共享服务: time_utils.py —— 时间/日期工具（Phase 9 新增 ... | 导入依赖 / import_depends |
| 56 | GateEngineServer: 门禁裁决服务 MCP Server (gate... | → | D_SHARED 共享服务: schemas.py | 导入依赖 / import_depends |
| 57 | GateEngineServer: 门禁裁决服务 MCP Server (gate... | → | D_SHARED 共享服务: time_utils.py —— 时间/日期工具（Phase 9 新增 ... | 导入依赖 / import_depends |
| 58 | MCP Gateway 集中式治理节点（MOD-INF-013 §12 Ph... | → | D_SHARED 共享服务: async_utils.py — async/sync 边界桥接（5.12.8 .... | 导入依赖 / import_depends |
| 59 | KnowledgeBaseServer: 知识库语义检索 MCP Server ... | → | D_SHARED 共享服务: yaml_utils.py — vocabulary YAML 加载公共工具（... | 导入依赖 / import_depends |
| 60 | KnowledgeBaseServer: 知识库语义检索 MCP Server ... | → | D_SHARED 共享服务: ports — D-DATA 服务的 Protocol 定义 (ports.py) | 导入依赖 / import_depends |
| 61 | MCP Resource 提供者（MOD-INF-013 Phase 6 — 关.... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of... | 导入依赖 / import_depends |
| 62 | ZephyrAlpha MCP Task Manager Server (task_manag... | → | D_SHARED 共享服务: ZephyrAlpha 蓝图拆解器 (blueprint_decomposer.py) | 导入依赖 / import_depends |
| 63 | ZephyrAlpha MCP Task Manager Server (task_manag... | → | D_SHARED 共享服务: ZephyrAlpha 任务系统核心数据模型 (models.py) | 导入依赖 / import_depends |
| 64 | ZephyrAlpha MCP Task Manager Server (task_manag... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of... | 导入依赖 / import_depends |
| 65 | ZephyrAlpha MCP Task Manager Server (task_manag... | → | D_SHARED 共享服务: schemas.py | 导入依赖 / import_depends |
| 66 | ZephyrAlpha MCP Task Manager Server (task_manag... | → | D_SHARED 共享服务: severity_types.py | 导入依赖 / import_depends |
| 67 | ZephyrAlpha MCP Task Manager Server (task_manag... | → | D_SHARED 共享服务: time_utils.py —— 时间/日期工具（Phase 9 新增 ... | 导入依赖 / import_depends |
| 68 | ZephyrAlpha MCP Telemetry Server — 系统可观测.... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of... | 导入依赖 / import_depends |
| 69 | VectorMemoryServer: VMS 向量记忆 MCP Server (MO... | → | D_SHARED 共享服务: ports — D-DATA 服务的 Protocol 定义 (ports.py) | 导入依赖 / import_depends |
| 70 | AssetInventory MCP Server — MOD-INF-026 蓝图 ... | → | D_SHARED 共享服务: EventBus — 事件总线（带背压控制）(M-07) (event... | 导入依赖 / import_depends |
| 71 | AssetInventory MCP Server — MOD-INF-026 蓝图 ... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of... | 导入依赖 / import_depends |
| 72 | PipelineOrchestrator — M1-M11 管线协调器 (pipe... | → | D_SHARED 共享服务: LLMGatewayProtocol — LLM 网关抽象接口 (llm_gat... | 导入依赖 / import_depends |
| 73 | PipelineOrchestrator — M1-M11 管线协调器 (pipe... | → | D_SHARED 共享服务: TaskRepositoryProtocol — TaskRepository 的 Pro... | 导入依赖 / import_depends |
| 74 | PipelineOrchestrator — M1-M11 管线协调器 (pipe... | → | D_SHARED 共享服务: EventBus — 事件总线（带背压控制）(M-07) (event... | 导入依赖 / import_depends |
| 75 | PipelineOrchestrator — M1-M11 管线协调器 (pipe... | → | D_SHARED 共享服务: ZephyrAlpha 任务系统核心数据模型 (models.py) | 导入依赖 / import_depends |
| 76 | PipelineOrchestrator — M1-M11 管线协调器 (pipe... | → | D_SHARED 共享服务: Zero-dependency Observer pattern (subscribe/emi... | 导入依赖 / import_depends |
| 77 | PipelineOrchestrator — M1-M11 管线协调器 (pipe... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of... | 导入依赖 / import_depends |
| 78 | PipelineOrchestrator — M1-M11 管线协调器 (pipe... | → | D_SHARED 共享服务: ports — D-DATA 服务的 Protocol 定义 (ports.py) | 导入依赖 / import_depends |
| 79 | PipelineOrchestrator — M1-M11 管线协调器 (pipe... | → | D_SHARED 共享服务: task_types — 任务系统核心类型 re-export 层 (ta... | 导入依赖 / import_depends |
| 80 | PipelineOrchestrator — M1-M11 管线协调器 (pipe... | → | D_SHARED 共享服务: async_utils.py — async/sync 边界桥接（5.12.8 .... | 导入依赖 / import_depends |
| 81 | PipelineOrchestrator — M1-M11 管线协调器 (pipe... | → | D_SHARED 共享服务: time_utils.py —— 时间/日期工具（Phase 9 新增 ... | 导入依赖 / import_depends |
| 82 | contract_violation_error.py | → | D_SHARED 共享服务: trace_context.py | 导入依赖 / import_depends |
| 83 | CTR-ERR-001: DataQualityError / 行情质量门禁不.... | → | D_SHARED 共享服务: trace_context.py | 导入依赖 / import_depends |
| 84 | execution_rejection_error.py | → | D_SHARED 共享服务: trace_context.py | 导入依赖 / import_depends |
| 85 | CTR-ERR-002: FactorComputationError / 因子计算.... | → | D_SHARED 共享服务: trace_context.py | 导入依赖 / import_depends |
| 86 | risk_limit_violation_error.py | → | D_SHARED 共享服务: trace_context.py | 导入依赖 / import_depends |
| 87 | signal_degradation_warning.py | → | D_SHARED 共享服务: trace_context.py | 导入依赖 / import_depends |
| 88 | dlq.py —— ZephyrAlpha 死信队列（Dead Letter Q... | → | D_SHARED 共享服务: Zero-dependency Observer pattern (subscribe/emi... | 导入依赖 / import_depends |
| 89 | dlq.py —— ZephyrAlpha 死信队列（Dead Letter Q... | → | D_SHARED 共享服务: serialization.py —— 统一序列化/反序列化基础设... | 导入依赖 / import_depends |
| 90 | dlq.py —— ZephyrAlpha 死信队列（Dead Letter Q... | → | D_SHARED 共享服务: SQLite 连接工厂真源（SSoT） (sqlite_factory.py) | 导入依赖 / import_depends |
| 91 | CT-DLQ-001: DeadLetterQueue -> System Event Bus... | → | D_SHARED 共享服务: Zero-dependency Observer pattern (subscribe/emi... | 导入依赖 / import_depends |
| 92 | event_schemas.py —— Observer 事件体 Pydantic ... | → | D_SHARED 共享服务: Zero-dependency Observer pattern (subscribe/emi... | 导入依赖 / import_depends |
| 93 | EventBus 升级策略引擎 (upgrade_strategy.py) | → | D_SHARED 共享服务: observer.py —— Re-export wrapper -> canonical... | 导入依赖 / import_depends |
| 94 | schema_registry.py | → | D_SHARED 共享服务: __version__.py —— ZephyrAlpha Shared 模块版本... | 导入依赖 / import_depends |
| 95 | schema_registry.py | → | D_SHARED 共享服务: errors.py —— ZephyrAlpha 统一错误层次（Tradit... | 导入依赖 / import_depends |
| 96 | severity_types.py | → | D_SHARED 共享服务: severity_types.py | 导入依赖 / import_depends |
| 97 | ChunkStrategyRouter — MOD-INF-011 分块策略调度... | → | D_SHARED 共享服务: schemas.py | 导入依赖 / import_depends |
| 98 | CollectionManager — MOD-INF-011 八大 Collectio... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of... | 导入依赖 / import_depends |
| 99 | CollectionManager — MOD-INF-011 八大 Collectio... | → | D_SHARED 共享服务: schemas.py | 导入依赖 / import_depends |
| 100 | collection_schemas.py | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of... | 导入依赖 / import_depends |
| 101 | collection_schemas.py | → | D_SHARED 共享服务: schemas.py | 导入依赖 / import_depends |
| 102 | HybridRetriever — MOD-INF-011 混合检索架构 (hy... | → | D_SHARED 共享服务: schemas.py | 导入依赖 / import_depends |
| 103 | IndexHealthMonitor — MOD-INF-011 索引健康自检.... | → | D_SHARED 共享服务: schemas.py | 导入依赖 / import_depends |
| 104 | ChromDB -> FAISS + SQLite WAL 数据迁移脚本 (mig... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of... | 导入依赖 / import_depends |
| 105 | RetrievalFeedback — MOD-INF-011 FLE 检索质量消... | → | D_SHARED 共享服务: schemas.py | 导入依赖 / import_depends |
| 106 | SQLiteMetadataStore — VMS 元数据存储 (SQLite W... | → | D_SHARED 共享服务: SQLite 连接工厂真源（SSoT） (sqlite_factory.py) | 导入依赖 / import_depends |
| 107 | VectorBridge — MOD-INF-011 CE/KB 外部集成适配... | → | D_SHARED 共享服务: serialization.py —— 统一序列化/反序列化基础设... | 导入依赖 / import_depends |
| 108 | VMS 共享数据模型 — MOD-INF-011 · 蓝图 §6.1 .... | → | D_SHARED 共享服务: schemas.py | 导入依赖 / import_depends |
| 109 | runtime_types.py | → | D_SHARED 共享服务: constants.py —— 共享枚举 & 常量集中 re-export... | 导入依赖 / import_depends |
| 110 | runtime_types.py | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of... | 导入依赖 / import_depends |
| 111 | runtime_types.py | → | D_SHARED 共享服务: base_config.py | 导入依赖 / import_depends |
| 112 | admission_response.py | → | D_TRADING 交易运营: admission_controller.py | 导入依赖 / import_depends |

### 依赖本域的其他域（入边）/ Depended By

| # | 外部域-源模块 / Source Module | → | 本域模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | D_AUTONOMY_CORE 自治核心: ContextAssembler — 上下文装配、校验、影子留档 ... | → | schemas.py | 导入依赖 / import_depends |
| 2 | D_AUTONOMY_CORE 自治核心: ContextInjector: retrieve and inject relevant k... | → | schemas.py | 导入依赖 / import_depends |
| 3 | D_AUTONOMY_CORE 自治核心: context_pipeline — Context Engine **四段流水线... | → | schemas.py | 导入依赖 / import_depends |
| 4 | D_AUTONOMY_CORE 自治核心: PromptRegistry: YAML-driven Prompt 模板注册表 (... | → | schemas.py | 导入依赖 / import_depends |
| 5 | D_AUTONOMY_CORE 自治核心: skill_executor.py | → | Structural Protocol interfaces for cross-module... | 导入依赖 / import_depends |
| 6 | D_AUTONOMY_CORE 自治核心: skill-registry.py —— Skill 注册基座（Phase 14... | → | schemas.py | 导入依赖 / import_depends |
| 7 | D_AUTONOMY_CORE 自治核心: skill_router.py | → | EmbeddingRouter — MOD-INF-011 双嵌入维度路由 (... | 导入依赖 / import_depends |
| 8 | D_AUTONOMY_CORE 自治核心: MOD-INF-019: Agent Spec — SpecEngine 蓝图->Ski... | → | Structural Protocol interfaces for cross-module... | 导入依赖 / import_depends |
| 9 | D_AUTONOMY_CORE 自治核心: PatternLibrary · 成功模式库（KB refactor 后独.... | → | schemas.py | 导入依赖 / import_depends |
| 10 | D_AUTONOMY_CORE 自治核心: IntentKeywordMapper - Stage 1 of three-stage in... | → | schemas.py | 导入依赖 / import_depends |
| 11 | D_AUTONOMY_CORE 自治核心: IntentParser · 意图三阶段级联解析器（V-09） (i... | → | schemas.py | 导入依赖 / import_depends |
| 12 | D_AUTONOMY_CORE 自治核心: CE 向量写入器 — vectorize_and_store() 生产者 (... | → | VMS 上下文注入器 — ingest_context() 消费者 (co... | 导入依赖 / import_depends |
| 13 | D_AUTONOMY_CORE 自治核心: test_auto_runtime_core.py | → | DeepSeekChat — 通过 DeepSeek API 进行 LLM 推理... | 测试依赖 / test_depends |
| 14 | D_AUTONOMY_CORE 自治核心: test_auto_runtime_core.py | → | EmbeddingRouter — MOD-INF-011 双嵌入维度路由 (... | 测试依赖 / test_depends |
| 15 | D_AUTONOMY_CORE 自治核心: test_auto_runtime_core.py | → | LocalModelScheduler — L2 本地模型 24/7 调度循... | 测试依赖 / test_depends |
| 16 | D_AUTONOMY_CORE 自治核心: test_auto_runtime_core.py | → | OllamaChat — 通过 Ollama HTTP API 进行本地 LLM... | 测试依赖 / test_depends |
| 17 | D_AUTONOMY_CORE 自治核心: test_auto_split.py | → | execution_model.py | 测试依赖 / test_depends |
| 18 | D_AUTONOMY_CORE 自治核心: test_auto_split.py | → | severity_types.py | 测试依赖 / test_depends |
| 19 | D_AUTONOMY_CORE 自治核心: test_escalation_contracts.py | → | G-CT-003 — RollbackResult Pydantic V2 BaseMode... | 测试依赖 / test_depends |
| 20 | D_AUTONOMY_CORE 自治核心: test_escalation_gov_contracts.py | → | G-CT-003 — RollbackResult Pydantic V2 BaseMode... | 测试依赖 / test_depends |
| 21 | D_AUTONOMY_CORE 自治核心: DM-202208 红蓝对抗-知识污染与检索劫持测试 (test... | → | HybridRetriever — MOD-INF-011 混合检索架构 (hy... | 测试依赖 / test_depends |
| 22 | D_AUTONOMY_CORE 自治核心: VMS 红蓝对抗测试 — 向量注入与投毒检测 (test_vm... | → | EmbeddingRouter — MOD-INF-011 双嵌入维度路由 (... | 测试依赖 / test_depends |
| 23 | D_AUTONOMY_CORE 自治核心: VMS 红蓝对抗测试 — 向量注入与投毒检测 (test_vm... | → | InMemoryFakeVMS — MOD-INF-011 · 零依赖测试双... | 测试依赖 / test_depends |
| 24 | D_AUTONOMY_CORE 自治核心: VMS 红蓝对抗测试 — 向量注入与投毒检测 (test_vm... | → | ProvenanceEnforcer — MOD-INF-011 写入溯源强制... | 测试依赖 / test_depends |
| 25 | D_AUTONOMY_CORE 自治核心: VMS 红蓝对抗测试 — 向量注入与投毒检测 (test_vm... | → | VMS 共享数据模型 — MOD-INF-011 · 蓝图 §6.1 .... | 测试依赖 / test_depends |
| 26 | D_AUTONOMY_CORE 自治核心: DM-202210 自动化机制-事件触发与定时任务测试 (te... | → | CacheLayer — MOD-INF-011 嵌入缓存与查询结果 LR... | 测试依赖 / test_depends |
| 27 | D_AUTONOMY_CORE 自治核心: DM-202210 自动化机制-事件触发与定时任务测试 (te... | → | CollectionManager — MOD-INF-011 八大 Collectio... | 测试依赖 / test_depends |
| 28 | D_AUTONOMY_CORE 自治核心: DM-202210 自动化机制-事件触发与定时任务测试 (te... | → | InProcessVectorMemory — MOD-INF-011 VMS 统一入... | 测试依赖 / test_depends |
| 29 | D_AUTONOMY_CORE 自治核心: DM-202210 自动化机制-事件触发与定时任务测试 (te... | → | IndexHealthMonitor — MOD-INF-011 索引健康自检.... | 测试依赖 / test_depends |
| 30 | D_AUTONOMY_CORE 自治核心: DM-202210 自动化机制-事件触发与定时任务测试 (te... | → | RetrievalFeedback — MOD-INF-011 FLE 检索质量消... | 测试依赖 / test_depends |
| 31 | D_AUTONOMY_CORE 自治核心: DM-202209 自动化机制-启动与关闭生命周期测试 (te... | → | EmbeddingRouter — MOD-INF-011 双嵌入维度路由 (... | 测试依赖 / test_depends |
| 32 | D_AUTONOMY_CORE 自治核心: DM-202209 自动化机制-启动与关闭生命周期测试 (te... | → | InMemoryFakeVMS — MOD-INF-011 · 零依赖测试双... | 测试依赖 / test_depends |
| 33 | D_AUTONOMY_CORE 自治核心: DM-202209 自动化机制-启动与关闭生命周期测试 (te... | → | InProcessVectorMemory — MOD-INF-011 VMS 统一入... | 测试依赖 / test_depends |
| 34 | D_AUTONOMY_CORE 自治核心: test_task_types.py | → | base_config.py | 测试依赖 / test_depends |
| 35 | D_AUTONOMY_CORE 自治核心: test_task_types.py | → | severity_types.py | 测试依赖 / test_depends |
| 36 | D_DATA: test_mcp_task_claim.py | → | ZephyrAlpha MCP Task Manager Server (task_manag... | 测试依赖 / test_depends |
| 37 | D_FEEDBACK_LOOP 反馈循环引擎: FLE->Orc 告警分派器 — dispatch() 生产者 (alert... | → | Structural Protocol interfaces for cross-module... | runtime / runtime |
| 38 | D_FEEDBACK_LOOP 反馈循环引擎: FeedbackLoop core — 反馈闭环核心类。 (core.py) | → | schemas.py | 导入依赖 / import_depends |
| 39 | D_FEEDBACK_LOOP 反馈循环引擎: FeedbackCollector: collect task execution feedb... | → | schemas.py | 导入依赖 / import_depends |
| 40 | D_FEEDBACK_LOOP 反馈循环引擎: FLE 全链路调度器 —— collect->detect->diagnose... | → | InProcessVectorMemory — MOD-INF-011 VMS 统一入... | 导入依赖 / import_depends |
| 41 | D_GOVERNANCE 生命周期管理: A2A Protocol 全链路满分验证脚本 (a2a_full_verif... | → | __init__.py | 导入依赖 / import_depends |
| 42 | D_GOVERNANCE 生命周期管理: 初始化任务系统数据库 + 创建任务系统自身的施工任... | → | __init__.py | 导入依赖 / import_depends |
| 43 | D_GOVERNANCE 生命周期管理: A2A 协议协调任务演示 (demo_a2a_coordination.py) | → | __init__.py | 导入依赖 / import_depends |
| 44 | D_GOVERNANCE 生命周期管理: C-track 端到端演示 —— 全流水线一次性运行 (dem... | → | __init__.py | 导入依赖 / import_depends |
| 45 | D_GOVERNANCE 生命周期管理: finalize_tasks.py | → | __init__.py | 导入依赖 / import_depends |
| 46 | D_GOVERNANCE 生命周期管理: local_layer_daemon.py — L2 本地模型层守护进程.... | → | LocalModelScheduler — L2 本地模型 24/7 调度循... | 导入依赖 / import_depends |
| 47 | D_GOVERNANCE 生命周期管理: start_brain.py — ZephyrAlpha 系统大脑一键启动 ... | → | runtime_types.py | 导入依赖 / import_depends |
| 48 | D_GOVERNANCE 生命周期管理: test_event_hook.py | → | __init__.py | 导入依赖 / import_depends |
| 49 | D_GOVERNANCE 生命周期管理: Ollama 入职考试运行脚本 (run_ollama_exam.py) | → | OllamaChat — 通过 Ollama HTTP API 进行本地 LLM... | 导入依赖 / import_depends |
| 50 | D_GOVERNANCE 生命周期管理: G-CT-007 — Audit.record_agent_spec() 记录 Agen... | → | Structural Protocol interfaces for cross-module... | 导入依赖 / import_depends |
| 51 | D_GOVERNANCE 生命周期管理: TaskRepository — 任务登记表 CRUD + 状态机（T-1... | → | severity_types.py | 导入依赖 / import_depends |
| 52 | D_GOVERNANCE 生命周期管理: GovernanceServer: 治理域统一MCP入口 (governance... | → | BaseMCPServer: stdio 传输 + JSON-RPC 2.0 协议基... | 导入依赖 / import_depends |
| 53 | D_GOVERNANCE 生命周期管理: test_approval.py | → | G-CT-004 — ApprovalRequest Pydantic V2 BaseMod... | 测试依赖 / test_depends |
| 54 | D_GOVERNANCE 生命周期管理: test_schema_schema_registry.py | → | schema_registry.py | 测试依赖 / test_depends |
| 55 | D_GOVERNANCE 生命周期管理: test_schema_schemas.py | → | schemas.py | 测试依赖 / test_depends |
| 56 | D_GOVERNANCE 生命周期管理: test_schema_schemas.py | → | severity_types.py | 测试依赖 / test_depends |
| 57 | D_GOVERNANCE 生命周期管理: test_boot_hooks_unlock.py | → | execution_model.py | 测试依赖 / test_depends |
| 58 | D_GOVERNANCE 生命周期管理: test_boot_hooks_unlock.py | → | severity_types.py | 测试依赖 / test_depends |
| 59 | D_GOV_AUDIT 审计追踪: finding_model.py | → | base_config.py | 导入依赖 / import_depends |
| 60 | D_GOV_AUDIT 审计追踪: pipeline_runner.py | → | base_config.py | 导入依赖 / import_depends |
| 61 | D_GOV_AUDIT 审计追踪: text_to_finding_adapter.py | → | base_config.py | 导入依赖 / import_depends |
| 62 | D_GOV_DOCS 架构文档治理: blueprint.md | → | Handoff 自动加载器——从 handoff 包恢复 AI sess... | runtime / runtime |
| 63 | D_GOV_DOCS 架构文档治理: blueprint.md | → | Handoff 自动加载器——从 handoff 包恢复 AI sess... | contract / contract |
| 64 | D_GOV_DRIFT 漂移检测: Drift Hotfix Bypass — drift_hotfix_bypass.py (... | → | Structural Protocol interfaces for cross-module... | 导入依赖 / import_depends |
| 65 | D_GOV_DRIFT 漂移检测: EN-002 — Enforcement Mode Validator (en_002_en... | → | schemas.py | 导入依赖 / import_depends |
| 66 | D_GOV_ENFORCEMENT 规则执行: G-CT-004 — Backward-compat re-export of Approv... | → | G-CT-004 — ApprovalRequest Pydantic V2 BaseMod... | 导入依赖 / import_depends |
| 67 | D_GOV_ENFORCEMENT 规则执行: test_gate_types.py | → | schemas.py | 测试依赖 / test_depends |
| 68 | D_GOV_KB 知识库治理: EmbeddingMigrate · Embedding 版本管理 + 迁移管... | → | schemas.py | 导入依赖 / import_depends |
| 69 | D_GOV_KB 知识库治理: KB 五阶段门禁 evaluate 用的最小合法 Task（对齐 ... | → | severity_types.py | 导入依赖 / import_depends |
| 70 | D_GOV_KB 知识库治理: VMSMemoryBackend — UnifiedMemoryAPI 的 VMS 后.... | → | BridgeLayer — MOD-INF-011 kb/ ↔ VMS 过渡桥接 ... | 导入依赖 / import_depends |
| 71 | D_GOV_KB 知识库治理: VMSMemoryBackend — UnifiedMemoryAPI 的 VMS 后.... | → | InProcessVectorMemory — MOD-INF-011 VMS 统一入... | 导入依赖 / import_depends |
| 72 | D_GOV_OPS_RESILIENCE 运维弹性治理: G-CT-003 消费端 — Escalation.on_rollback_failu... | → | G-CT-003 — RollbackResult Pydantic V2 BaseMode... | 导入依赖 / import_depends |
| 73 | D_GOV_OPS_RESILIENCE 运维弹性治理: G-CT-003 — RollbackResult backward-compat re-e... | → | G-CT-003 — RollbackResult Pydantic V2 BaseMode... | 导入依赖 / import_depends |
| 74 | D_GOV_OPS_RESILIENCE 运维弹性治理: PhaseManager->GateEngine 检查注册表桥梁 — 44 .... | → | BridgeLayer — MOD-INF-011 kb/ ↔ VMS 过渡桥接 ... | 导入依赖 / import_depends |
| 75 | D_GOV_OPS_RESILIENCE 运维弹性治理: PhaseManager->GateEngine 检查注册表桥梁 — 44 .... | → | CollectionManager — MOD-INF-011 八大 Collectio... | 导入依赖 / import_depends |
| 76 | D_GOV_OPS_RESILIENCE 运维弹性治理: PhaseManager->GateEngine 检查注册表桥梁 — 44 .... | → | InProcessVectorMemory — MOD-INF-011 VMS 统一入... | 导入依赖 / import_depends |
| 77 | D_GOV_OPS_RESILIENCE 运维弹性治理: PhaseManager->GateEngine 检查注册表桥梁 — 44 .... | → | IndexHealthMonitor — MOD-INF-011 索引健康自检.... | 导入依赖 / import_depends |
| 78 | D_GOV_OPS_RESILIENCE 运维弹性治理: D-DATA -> ServiceRegistry 注册模块 (service_reg... | → | CollectionManager — MOD-INF-011 八大 Collectio... | 导入依赖 / import_depends |
| 79 | D_GOV_OPS_RESILIENCE 运维弹性治理: D-DATA -> ServiceRegistry 注册模块 (service_reg... | → | InProcessVectorMemory — MOD-INF-011 VMS 统一入... | 导入依赖 / import_depends |
| 80 | D_GOV_RULE 规则治理: ContractTemplateManager: manage MCP tool contra... | → | schemas.py | 导入依赖 / import_depends |
| 81 | D_GOV_RULE 规则治理: gate_types.py | → | schemas.py | 导入依赖 / import_depends |
| 82 | D_GOV_RULE 规则治理: task_types.py | → | base_config.py | 导入依赖 / import_depends |
| 83 | D_GOV_RULE 规则治理: task_types.py | → | execution_model.py | 导入依赖 / import_depends |
| 84 | D_GOV_RULE 规则治理: task_types.py | → | severity_types.py | 导入依赖 / import_depends |
| 85 | D_GOV_SCRIPTS 脚本治理: task_self_check.py — 任务系统自身健康检查 (tas... | → | __init__.py | 导入依赖 / import_depends |
| 86 | D_GOV_SCRIPTS 脚本治理: create_task_from_finding.py — Finding → 任务.... | → | __init__.py | 导入依赖 / import_depends |
| 87 | D_GOV_SCRIPTS 脚本治理: validate_gate_engine_external.py — Gate Engine... | → | __init__.py | 导入依赖 / import_depends |
| 88 | D_INFRA_RUNTIME 运行时集成: DEPRECATED: 此文件已废弃。 (event_bus_upgrade.py) | → | EventBus 升级策略引擎 (upgrade_strategy.py) | 导入依赖 / import_depends |
| 89 | D_INFRA_RUNTIME 运行时集成: Finding->TaskCard 桥接器 (finding_task_bridge.py) | → | schemas.py | 导入依赖 / import_depends |
| 90 | D_INFRA_RUNTIME 运行时集成: Finding Schema — 审计发现标准化数据模型 (findi... | → | schemas.py | 导入依赖 / import_depends |
| 91 | D_INFRA_RUNTIME 运行时集成: AiAuditLogger — AI 行为审计日志 (ai_audit_logg... | → | schemas.py | 导入依赖 / import_depends |
| 92 | D_INFRA_RUNTIME 运行时集成: AutoRuntimeCore — 三层运行时运营中心（系统大脑... | → | DeepSeekChat — 通过 DeepSeek API 进行 LLM 推理... | 导入依赖 / import_depends |
| 93 | D_INFRA_RUNTIME 运行时集成: AutoRuntimeCore — 三层运行时运营中心（系统大脑... | → | EmbeddingRouter — MOD-INF-011 双嵌入维度路由 (... | 导入依赖 / import_depends |
| 94 | D_INFRA_RUNTIME 运行时集成: AutoRuntimeCore — 三层运行时运营中心（系统大脑... | → | LocalModelScheduler — L2 本地模型 24/7 调度循... | 导入依赖 / import_depends |
| 95 | D_INFRA_RUNTIME 运行时集成: AutoRuntimeCore — 三层运行时运营中心（系统大脑... | → | OllamaChat — 通过 Ollama HTTP API 进行本地 LLM... | 导入依赖 / import_depends |
| 96 | D_INFRA_RUNTIME 运行时集成: AutoRuntimeCore — 三层运行时运营中心（系统大脑... | → | PipelineOrchestrator — M1-M11 管线协调器 (pipe... | 导入依赖 / import_depends |
| 97 | D_INFRA_RUNTIME 运行时集成: AutoRuntimeCore — 三层运行时运营中心（系统大脑... | → | InProcessVectorMemory — MOD-INF-011 VMS 统一入... | 导入依赖 / import_depends |
| 98 | D_INFRA_RUNTIME 运行时集成: AutoTaskGenerator — 自动任务生成器 (auto_task_... | → | LocalModelScheduler — L2 本地模型 24/7 调度循... | 导入依赖 / import_depends |
| 99 | D_INFRA_RUNTIME 运行时集成: CapabilityCard — 能力卡片数据模型 (capability_... | → | schemas.py | 导入依赖 / import_depends |
| 100 | D_INFRA_RUNTIME 运行时集成: DreamCycle — 知识固化引擎 (dream_cycle.py) | → | schemas.py | 导入依赖 / import_depends |
| 101 | D_INFRA_RUNTIME 运行时集成: HealthMonitor — 健康监控 + 自愈 (health_monito... | → | schemas.py | 导入依赖 / import_depends |
| 102 | D_INFRA_RUNTIME 运行时集成: IntegrationRegistry — 集成注册表 (integration_... | → | schemas.py | 导入依赖 / import_depends |
| 103 | D_INFRA_RUNTIME 运行时集成: NightShiftQueue — 夜班登记表持久化 (night_shif... | → | schemas.py | 导入依赖 / import_depends |
| 104 | D_INFRA_RUNTIME 运行时集成: runtime_config.py | → | runtime_types.py | 导入依赖 / import_depends |
| 105 | D_INFRA_RUNTIME 运行时集成: WorkDAG + WorkItem — 工作编排数据模型 (work_da... | → | schemas.py | 导入依赖 / import_depends |
| 106 | D_INTEGRATION_GATEWAY 集成网关: ZephyrAlpha MCP (Model Context Protocol) 子包。... | → | BaseMCPServer: stdio 传输 + JSON-RPC 2.0 协议基... | 导入依赖 / import_depends |
| 107 | D_INTEGRATION_GATEWAY 集成网关: ZephyrAlpha MCP (Model Context Protocol) 子包。... | → | BlueprintSearchServer — MCP Server for bluepri... | 导入依赖 / import_depends |
| 108 | D_INTEGRATION_GATEWAY 集成网关: ZephyrAlpha MCP (Model Context Protocol) 子包。... | → | DocGuardServer: 跨会话交接协议服务 MCP Server (... | 导入依赖 / import_depends |
| 109 | D_INTEGRATION_GATEWAY 集成网关: ZephyrAlpha MCP (Model Context Protocol) 子包。... | → | GateEngineServer: 门禁裁决服务 MCP Server (gate... | 导入依赖 / import_depends |
| 110 | D_INTEGRATION_GATEWAY 集成网关: ZephyrAlpha MCP (Model Context Protocol) 子包。... | → | Handoff 自动加载器——从 handoff 包恢复 AI sess... | 导入依赖 / import_depends |
| 111 | D_INTEGRATION_GATEWAY 集成网关: ZephyrAlpha MCP (Model Context Protocol) 子包。... | → | KnowledgeBaseServer: 知识库语义检索 MCP Server ... | 导入依赖 / import_depends |
| 112 | D_INTEGRATION_GATEWAY 集成网关: ZephyrAlpha MCP (Model Context Protocol) 子包。... | → | MCP Prompt 模板提供者（MOD-INF-013 Phase 6 — .... | 导入依赖 / import_depends |
| 113 | D_INTEGRATION_GATEWAY 集成网关: ZephyrAlpha MCP (Model Context Protocol) 子包。... | → | MCP Resource 提供者（MOD-INF-013 Phase 6 — 关.... | 导入依赖 / import_depends |
| 114 | D_INTEGRATION_GATEWAY 集成网关: ZephyrAlpha MCP (Model Context Protocol) 子包。... | → | MCP sandbox 安全代码执行沙箱（MOD-INF-013 Phase... | 导入依赖 / import_depends |
| 115 | D_INTEGRATION_GATEWAY 集成网关: ZephyrAlpha MCP (Model Context Protocol) 子包。... | → | SentinelServer: 意图路由哨兵 MCP Server (sentin... | 导入依赖 / import_depends |
| 116 | D_INTEGRATION_GATEWAY 集成网关: ZephyrAlpha MCP (Model Context Protocol) 子包。... | → | ZephyrAlpha MCP Task Manager Server (task_manag... | 导入依赖 / import_depends |
| 117 | D_INTEGRATION_GATEWAY 集成网关: ZephyrAlpha MCP (Model Context Protocol) 子包。... | → | ZephyrAlpha MCP Telemetry Server — 系统可观测.... | 导入依赖 / import_depends |
| 118 | D_INTEGRATION_GATEWAY 集成网关: ZephyrAlpha MCP (Model Context Protocol) 子包。... | → | VectorMemoryServer: VMS 向量记忆 MCP Server (MO... | 导入依赖 / import_depends |
| 119 | D_INTELLIGENCE 上下文管理: 模型快速能力画像脚本 (P2 三级模式 Quick 入口)。... | → | OllamaChat — 通过 Ollama HTTP API 进行本地 LLM... | 导入依赖 / import_depends |
| 120 | D_INTELLIGENCE 上下文管理: KB->VMS 同步引擎 — sync_to_vms() 生产者 (sync_... | → | InMemoryFakeVMS — MOD-INF-011 · 零依赖测试双... | 导入依赖 / import_depends |
| 121 | D_INTELLIGENCE 上下文管理: DM-202010: PipelineOrchestrator 自动启动/周期运... | → | PipelineOrchestrator — M1-M11 管线协调器 (pipe... | 测试依赖 / test_depends |
| 122 | D_INTELLIGENCE 上下文管理: test_pipeline_orchestrator_root.py | → | PipelineOrchestrator — M1-M11 管线协调器 (pipe... | 测试依赖 / test_depends |
| 123 | D_ORCHESTRATOR 代理编排器: AgentHealthMonitor · Agent 健康监控（三态 + 5 ... | → | schemas.py | 导入依赖 / import_depends |
| 124 | D_ORCHESTRATOR 代理编排器: AgentOrchestrator · 多角色 Agent 路由、工具链.... | → | schemas.py | 导入依赖 / import_depends |
| 125 | D_ORCHESTRATOR 代理编排器: Orc 告警接收器 — handle_alert() 消费者 (alert_... | → | base_config.py | 导入依赖 / import_depends |
| 126 | D_ORCHESTRATOR 代理编排器: Orc 告警接收器 — handle_alert() 消费者 (alert_... | → | execution_model.py | 导入依赖 / import_depends |
| 127 | D_ORCHESTRATOR 代理编排器: Orc 告警接收器 — handle_alert() 消费者 (alert_... | → | severity_types.py | 导入依赖 / import_depends |
| 128 | D_ORCHESTRATOR 代理编排器: Orc->VMS 记忆写入器 (memory_writer.py) | → | InMemoryFakeVMS — MOD-INF-011 · 零依赖测试双... | 导入依赖 / import_depends |
| 129 | D_ORCHESTRATOR 代理编排器: CE 任务上下文构建器 — build_from_task() 消费者... | → | schemas.py | 导入依赖 / import_depends |
| 130 | D_ORCHESTRATOR 代理编排器: HallucinationDetector · Chain-of-Verification.... | → | schemas.py | 导入依赖 / import_depends |
| 131 | D_SECURITY 对抗验证: defense_runner.py | → | execution_model.py | 导入依赖 / import_depends |
| 132 | D_SECURITY 对抗验证: defense_runner.py | → | severity_types.py | 导入依赖 / import_depends |
| 133 | D_SECURITY_LLM LLM防御: test_cross_module_integration_llm_security.py | → | MCP Gateway 集中式治理节点（MOD-INF-013 §12 Ph... | 测试依赖 / test_depends |
| 134 | D_SECURITY_LLM LLM防御: test_cross_module_integration_llm_security.py | → | PipelineOrchestrator — M1-M11 管线协调器 (pipe... | 测试依赖 / test_depends |
| 135 | D_SECURITY_LLM LLM防御: test_db.py | → | base_config.py | 测试依赖 / test_depends |
| 136 | D_SECURITY_LLM LLM防御: test_db.py | → | execution_model.py | 测试依赖 / test_depends |
| 137 | D_SECURITY_LLM LLM防御: test_db.py | → | severity_types.py | 测试依赖 / test_depends |
| 138 | D_SHARED 共享服务: test_utils_testing.py | → | schemas.py | 测试依赖 / test_depends |
| 139 | D_SHARED 共享服务: test_utils_testing.py | → | severity_types.py | 测试依赖 / test_depends |
| 140 | D_TRADING 交易运营: verdict_engine.py | → | LocalModelScheduler — L2 本地模型 24/7 调度循... | 导入依赖 / import_depends |
| 141 | D_TRADING 交易运营: test_lifecycle_manager.py | → | runtime_types.py | 测试依赖 / test_depends |

### 跨域依赖图 / Cross-domain Dependency Diagram

> 本域与 24 个外部域直接连接（出边 112 条 + 入边 141 条 = 253 条）。只显示直接连接的域，不展开具体节点。

```mermaid
graph LR
    D_INTEGRATION["D_INTEGRATION<br/>管线路由"]
    D_SHARED["D_SHARED<br/>共享服务"]
    D_INFRA_RUNTIME["D_INFRA_RUNTIME<br/>运行时集成"]
    D_OPS["D_OPS<br/>反馈循环"]
    D_GOVERNANCE["D_GOVERNANCE<br/>生命周期管理"]
    D_GOV_AUDIT["D_GOV_AUDIT<br/>审计追踪"]
    D_SECURITY["D_SECURITY<br/>对抗验证"]
    D_AUTONOMY_CORE["D_AUTONOMY_CORE<br/>自治核心"]
    D_GOV_KB["D_GOV_KB<br/>知识库治理"]
    D_INTELLIGENCE["D_INTELLIGENCE<br/>上下文管理"]
    D_FBL_DETECTORS["D_FBL_DETECTORS"]
    D_GOV_RULE["D_GOV_RULE<br/>规则治理"]
    D_INFRA_RECOVERY["D_INFRA_RECOVERY<br/>回滚恢复"]
    D_TRADING["D_TRADING<br/>交易运营"]
    D_FEEDBACK_LOOP["D_FEEDBACK_LOOP<br/>反馈循环引擎"]
    D_INFRASTRUCTURE["D_INFRASTRUCTURE"]
    D_INTEGRATION_GATEWAY["D_INTEGRATION_GATEWAY<br/>集成网关"]
    D_GOV_OPS_RESILIENCE["D_GOV_OPS_RESILIENCE<br/>运维弹性治理"]
    D_ORCHESTRATOR["D_ORCHESTRATOR<br/>代理编排器"]
    D_SECURITY_LLM["D_SECURITY_LLM<br/>LLM防御"]
    D_GOV_SCRIPTS["D_GOV_SCRIPTS<br/>脚本治理"]
    D_GOV_ENFORCEMENT["D_GOV_ENFORCEMENT<br/>规则执行"]
    D_GOV_DRIFT["D_GOV_DRIFT<br/>漂移检测"]
    D_GOV_DOCS["D_GOV_DOCS<br/>架构文档治理"]
    D_DATA["D_DATA"]
    D_INTEGRATION -->|65条 导入依赖 / import_depends| D_SHARED
    D_INTEGRATION -->|14条 导入依赖 / import_depends| D_INFRA_RUNTIME
    D_INTEGRATION -->|4条 导入依赖 / import_depends| D_OPS
    D_INTEGRATION -->|4条 导入依赖 / import_depends| D_GOVERNANCE
    D_INTEGRATION -->|4条 导入依赖 / import_depends, 测试依赖 / test_depends| D_GOV_AUDIT
    D_INTEGRATION -->|3条 导入依赖 / import_depends| D_SECURITY
    D_INTEGRATION -->|3条 导入依赖 / import_depends| D_AUTONOMY_CORE
    D_INTEGRATION -->|3条 导入依赖 / import_depends| D_GOV_KB
    D_INTEGRATION -->|3条 导入依赖 / import_depends| D_INTELLIGENCE
    D_INTEGRATION -->|2条 测试依赖 / test_depends| D_FBL_DETECTORS
    D_INTEGRATION -->|2条 导入依赖 / import_depends| D_GOV_RULE
    D_INTEGRATION -->|2条 导入依赖 / import_depends, 测试依赖 / test_depends| D_INFRA_RECOVERY
    D_INTEGRATION -->|1条 导入依赖 / import_depends| D_TRADING
    D_INTEGRATION -->|1条 测试依赖 / test_depends| D_FEEDBACK_LOOP
    D_INTEGRATION -->|1条 导入依赖 / import_depends| D_INFRASTRUCTURE
    D_AUTONOMY_CORE -->|35条 导入依赖 / import_depends, 测试依赖 / test_depends| D_INTEGRATION
    D_GOVERNANCE -->|18条 导入依赖 / import_depends, 测试依赖 / test_depends| D_INTEGRATION
    D_INFRA_RUNTIME -->|18条 导入依赖 / import_depends| D_INTEGRATION
    D_INTEGRATION_GATEWAY -->|13条 导入依赖 / import_depends| D_INTEGRATION
    D_GOV_OPS_RESILIENCE -->|8条 导入依赖 / import_depends| D_INTEGRATION
    D_ORCHESTRATOR -->|8条 导入依赖 / import_depends| D_INTEGRATION
    D_GOV_RULE -->|5条 导入依赖 / import_depends| D_INTEGRATION
    D_SECURITY_LLM -->|5条 测试依赖 / test_depends| D_INTEGRATION
    D_GOV_KB -->|4条 导入依赖 / import_depends| D_INTEGRATION
    D_FEEDBACK_LOOP -->|4条 导入依赖 / import_depends, runtime / runtime| D_INTEGRATION
    D_INTELLIGENCE -->|4条 导入依赖 / import_depends, 测试依赖 / test_depends| D_INTEGRATION
    D_GOV_SCRIPTS -->|3条 导入依赖 / import_depends| D_INTEGRATION
    D_GOV_AUDIT -->|3条 导入依赖 / import_depends| D_INTEGRATION
    D_GOV_ENFORCEMENT -->|2条 导入依赖 / import_depends, 测试依赖 / test_depends| D_INTEGRATION
    D_SECURITY -->|2条 导入依赖 / import_depends| D_INTEGRATION
    D_TRADING -->|2条 导入依赖 / import_depends, 测试依赖 / test_depends| D_INTEGRATION
    D_GOV_DRIFT -->|2条 导入依赖 / import_depends| D_INTEGRATION
    D_GOV_DOCS -->|2条 contract / contract, runtime / runtime| D_INTEGRATION
    D_SHARED -->|2条 测试依赖 / test_depends| D_INTEGRATION
    D_DATA -->|1条 测试依赖 / test_depends| D_INTEGRATION
```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph (PostgreSQL)` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_doc.py`（G2+G10 合并）
- **维护方式 / Maintenance**: 自动生成，全景图更新时刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}.md`，如 `16_d_trading.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
