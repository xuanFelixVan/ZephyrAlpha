---
doc_type: domain_architecture_diagram
title: D-KNOWLEDGE 知识管理架构图
version: "1.0"
status: active
date: 2026-06-24
owner: auto-generator
ttl: permanent
---

# 30_d_knowledge / 知识管理 架构图

> **文档作用 / Purpose**: 以ASCII art可视化展示知识管理（D-KNOWLEDGE）功能域的模块分层架构和依赖关系。

> 本文档由 generate_domain_architecture_diagram.py 从 depgraph.db 自动生成
> 最后更新 / Last Updated: 2026-06-24 21:40:10
> 数据源 / Data Source: depgraph.db nodes表 + edges表

## 架构全景图 / Architecture Overview

> 按 architecture_layer 分层显示 知识管理（D-KNOWLEDGE）的模块分布。共 194 个模块 / 194 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│            L1 基础层 / Foundation Layer (50 modules)             │
├──────────────────────────────────────────────────────────────────┤
│   architecture_model/layers/b_vector_memory.yaml  [production]   │
│   docs__03_modules___domain_knowledge__knowledge_base__bluepr... │
│   docs__03_modules___domain_knowledge__vector_memory__bluepri... │
│   src/zephyr/governance/vector_memory/__init__.py  [prototype]   │
│   src/zephyr/governance/vector_memory/bm25_index.py  [prototype] │
│   src/zephyr/governance/vector_memory/bridge_layer.py  [proto... │
│   src/zephyr/governance/vector_memory/cache_layer.py  [protot... │
│   src/zephyr/governance/vector_memory/chunk_strategy_router.p... │
│   src/zephyr/governance/vector_memory/collection_manager.py  ... │
│   src/zephyr/governance/vector_memory/collection_schemas.py  ... │
│   src/zephyr/governance/vector_memory/context_ingest.py  [pro... │
│   src/zephyr/governance/vector_memory/cross_collection_retrie... │
│   src/zephyr/governance/vector_memory/delegated_vector_memory... │
│   src/zephyr/governance/vector_memory/design_principles.py  [... │
│   src/zephyr/governance/vector_memory/faiss_collection_manage... │
│   src/zephyr/governance/vector_memory/hybrid_retriever.py  [p... │
│   src/zephyr/governance/vector_memory/in_memory_fake_vms.py  ... │
│   src/zephyr/governance/vector_memory/in_memory_memory_backen... │
│   ...还有 32 个模块 / 32 more modules                            │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│               未分类 / Unclassified (144 modules)                │
├──────────────────────────────────────────────────────────────────┤
│   5层记忆架构 5-Layer Memory Architecture  [design]              │
│   AI Auto Knowledge Extractor AI自动知识提取  [design]           │
│   AgentDock AgentDock记忆系统  [design]                          │
│   C-016 产业链图谱适配层 Industry Chain Graph Adapter  [design]  │
│   C-016 公司图谱 Company Graph  [design]                         │
│   Call Graph Incremental Updater 调用图增量更新器  [design]      │
│   Cascade Failure Simulator 级联失效仿真器  [design]             │
│   Case Library Tag System 案例库标签体系  [design]               │
│   Causal Edges 因果边列表  [design]                              │
│   Causal ML因果推断 Causal ML  [design]                          │
│   Causal Reasoner 因果推理器  [design]                           │
│   ChromaDB 向量索引  [design]                                    │
│   CoALA CoALA记忆框架  [design]                                  │
│   Colocation Dependency Topology Optimizer 托管依赖拓扑优化器... │
│   Conflict Report 矛盾报告  [design]                             │
│   Cross-Layer Dependency Analyzer 跨层依赖分析器  [design]       │
│   D-KNOWLEDGE 知识  [design]                                     │
│   D-KNOWLEDGE-12 知识  [design]                                  │
│   ...还有 126 个模块 / 126 more modules                          │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 194 个模块 / 194 modules）。

### L1 基础层 / Foundation Layer (50 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | architecture_model/layers/b_vector_memory.yaml | architecture_model/layers/b_vector_me... | production | orphan |
| 2 | docs/03_modules/_domain_knowledge/knowledge_base/blueprin... | docs__03_modules___domain_knowledge__... | design | design_only |
| 3 | docs/03_modules/_domain_knowledge/vector_memory/blueprint.md | docs__03_modules___domain_knowledge__... | design | design_only |
| 4 | src/zephyr/governance/vector_memory/__init__.py | src/zephyr/governance/vector_memory/_... | prototype | draft |
| 5 | src/zephyr/governance/vector_memory/bm25_index.py | src/zephyr/governance/vector_memory/b... | prototype | draft |
| 6 | src/zephyr/governance/vector_memory/bridge_layer.py | src/zephyr/governance/vector_memory/b... | prototype | draft |
| 7 | src/zephyr/governance/vector_memory/cache_layer.py | src/zephyr/governance/vector_memory/c... | prototype | draft |
| 8 | src/zephyr/governance/vector_memory/chunk_strategy_router.py | src/zephyr/governance/vector_memory/c... | prototype | draft |
| 9 | src/zephyr/governance/vector_memory/collection_manager.py | src/zephyr/governance/vector_memory/c... | prototype | draft |
| 10 | src/zephyr/governance/vector_memory/collection_schemas.py | src/zephyr/governance/vector_memory/c... | prototype | draft |
| 11 | src/zephyr/governance/vector_memory/context_ingest.py | src/zephyr/governance/vector_memory/c... | prototype | draft |
| 12 | src/zephyr/governance/vector_memory/cross_collection_retr... | src/zephyr/governance/vector_memory/c... | prototype | draft |
| 13 | src/zephyr/governance/vector_memory/delegated_vector_memo... | src/zephyr/governance/vector_memory/d... | prototype | draft |
| 14 | src/zephyr/governance/vector_memory/design_principles.py | src/zephyr/governance/vector_memory/d... | prototype | draft |
| 15 | src/zephyr/governance/vector_memory/faiss_collection_mana... | src/zephyr/governance/vector_memory/f... | prototype | draft |
| 16 | src/zephyr/governance/vector_memory/hybrid_retriever.py | src/zephyr/governance/vector_memory/h... | prototype | draft |
| 17 | src/zephyr/governance/vector_memory/in_memory_fake_vms.py | src/zephyr/governance/vector_memory/i... | prototype | draft |
| 18 | src/zephyr/governance/vector_memory/in_memory_memory_back... | src/zephyr/governance/vector_memory/i... | prototype | draft |
| 19 | src/zephyr/governance/vector_memory/in_process_vector_mem... | src/zephyr/governance/vector_memory/i... | prototype | draft |
| 20 | src/zephyr/governance/vector_memory/index_health_monitor.py | src/zephyr/governance/vector_memory/i... | prototype | draft |
| 21 | src/zephyr/governance/vector_memory/interface.py | src/zephyr/governance/vector_memory/i... | prototype | draft |
| 22 | src/zephyr/governance/vector_memory/local_model_scheduler.py | src/zephyr/governance/vector_memory/l... | prototype | draft |
| 23 | src/zephyr/governance/vector_memory/migrate_chroma_to_fai... | src/zephyr/governance/vector_memory/m... | prototype | draft |
| 24 | src/zephyr/governance/vector_memory/ollama_chat.py | src/zephyr/governance/vector_memory/o... | prototype | draft |
| 25 | src/zephyr/governance/vector_memory/ollama_embedding.py | src/zephyr/governance/vector_memory/o... | prototype | draft |
| 26 | src/zephyr/governance/vector_memory/provenance_enforcer.py | src/zephyr/governance/vector_memory/p... | prototype | draft |
| 27 | src/zephyr/governance/vector_memory/retrieval_feedback.py | src/zephyr/governance/vector_memory/r... | prototype | draft |
| 28 | src/zephyr/governance/vector_memory/sqlite_metadata_store.py | src/zephyr/governance/vector_memory/s... | prototype | draft |
| 29 | src/zephyr/governance/vector_memory/vms_errors.py | src/zephyr/governance/vector_memory/v... | prototype | draft |
| 30 | src/zephyr/governance/vector_memory/vms_schemas.py | src/zephyr/governance/vector_memory/v... | prototype | draft |
| 31 | src/zephyr/knowledge/__init__.py | src/zephyr/knowledge/__init__.py | prototype | orphan |
| 32 | src/zephyr/knowledge/_extensions/__init__.py | src/zephyr/knowledge/_extensions/__in... | scaffold_placeholder | orphan |
| 33 | src/zephyr/knowledge/api/__init__.py | src/zephyr/knowledge/api/__init__.py | scaffold_placeholder | orphan |
| 34 | src/zephyr/knowledge/core/__init__.py | src/zephyr/knowledge/core/__init__.py | scaffold_placeholder | orphan |
| 35 | src/zephyr/knowledge/infrastructure/__init__.py | src/zephyr/knowledge/infrastructure/_... | scaffold_placeholder | orphan |
| 36 | src/zephyr/knowledge/models/__init__.py | src/zephyr/knowledge/models/__init__.py | scaffold_placeholder | orphan |
| 37 | src/zephyr/knowledge/services/__init__.py | src/zephyr/knowledge/services/__init_... | scaffold_placeholder | orphan |
| 38 | tests/test_skill_knowledge_base.py | tests/test_skill_knowledge_base.py | prototype | draft |
| 39 | tests/test_vector_memory_root.py | tests/test_vector_memory_root.py | prototype | orphan |
| 40 | tests/unit/vector_memory/__init__.py | tests/unit/vector_memory/__init__.py | prototype | orphan |
| 41 | tests/unit/vector_memory/test_vector_memory.py | tests/unit/vector_memory/test_vector_... | prototype | draft |
| 42 | 知识域-AI提取/D-KNOWLEDGE-17 | AI Auto Knowledge Extractor | design | design_only |
| 43 | 知识域-图谱浏览/D-KNOWLEDGE-15 | Knowledge Graph Explorer | design | design_only |
| 44 | 知识域-推理/D-KNOWLEDGE-09 | Knowledge Reasoner | design | design_only |
| 45 | 知识域-搜索/D-KNOWLEDGE-21 | Knowledge Base Search Engine | design | design_only |
| 46 | 知识域-案例管理/D-KNOWLEDGE-23 | Case Library Tag System | design | design_only |
| 47 | 知识域-沉淀/D-KNOWLEDGE-25 | Research Knowledge Precipitator | design | design_only |
| 48 | 知识域-质量评估/D-KNOWLEDGE-11 | Knowledge Quality Assessor | design | design_only |
| 49 | 知识域-金融图谱/D-KNOWLEDGE-13 | Financial Knowledge Graph | design | design_only |
| 50 | 知识域-集成/D-KNOWLEDGE-19 | Obsidian Knowledge Base Integrator | design | design_only |

### 未分类 / Unclassified (144 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | D-KNOWLEDGE/5层记忆架构 5-Layer Memory Architecture | 5层记忆架构 5-Layer Memory Architecture | design | design_only |
| 2 | D-KNOWLEDGE/AI Auto Knowledge Extractor AI自动知识提取 | AI Auto Knowledge Extractor AI自动知... | design | design_only |
| 3 | D-KNOWLEDGE/AgentDock AgentDock记忆系统 | AgentDock AgentDock记忆系统 | design | design_only |
| 4 | D-KNOWLEDGE/C-016 产业链图谱适配层 Industry Chain Graph A... | C-016 产业链图谱适配层 Industry Chain... | design | design_only |
| 5 | D-KNOWLEDGE/C-016 公司图谱 Company Graph | C-016 公司图谱 Company Graph | design | design_only |
| 6 | D-KNOWLEDGE/Call Graph Incremental Updater 调用图增量更新器 | Call Graph Incremental Updater 调用图... | design | design_only |
| 7 | D-KNOWLEDGE/Cascade Failure Simulator 级联失效仿真器 | Cascade Failure Simulator 级联失效仿真器 | design | design_only |
| 8 | D-KNOWLEDGE/Case Library Tag System 案例库标签体系 | Case Library Tag System 案例库标签体系 | design | design_only |
| 9 | D-KNOWLEDGE/Causal Edges 因果边列表 | Causal Edges 因果边列表 | design | design_only |
| 10 | D-KNOWLEDGE/Causal ML因果推断 Causal ML | Causal ML因果推断 Causal ML | design | design_only |
| 11 | D-KNOWLEDGE/Causal Reasoner 因果推理器 | Causal Reasoner 因果推理器 | design | design_only |
| 12 | D-KNOWLEDGE/ChromaDB 向量索引 | ChromaDB 向量索引 | design | design_only |
| 13 | D-KNOWLEDGE/CoALA CoALA记忆框架 | CoALA CoALA记忆框架 | design | design_only |
| 14 | D-KNOWLEDGE/Colocation Dependency Topology Optimizer 托管... | Colocation Dependency Topology Optimi... | design | design_only |
| 15 | D-KNOWLEDGE/Conflict Report 矛盾报告 | Conflict Report 矛盾报告 | design | design_only |
| 16 | D-KNOWLEDGE/Cross-Layer Dependency Analyzer 跨层依赖分析器 | Cross-Layer Dependency Analyzer 跨层... | design | design_only |
| 17 | D-KNOWLEDGE/D-KNOWLEDGE 知识 | D-KNOWLEDGE 知识 | design | design_only |
| 18 | D-KNOWLEDGE/D-KNOWLEDGE-12 知识 | D-KNOWLEDGE-12 知识 | design | design_only |
| 19 | D-KNOWLEDGE/D-KNOWLEDGE-18 知识 | D-KNOWLEDGE-18 知识 | design | design_only |
| 20 | D-KNOWLEDGE/Data Layer Dependency Modeler 数据层依赖建模器 | Data Layer Dependency Modeler 数据层... | design | design_only |
| 21 | D-KNOWLEDGE/Databricks Memory Research Databricks记忆研究 | Databricks Memory Research Databricks... | design | design_only |
| 22 | D-KNOWLEDGE/Decision Layer Dependency Modeler 决策层依赖... | Decision Layer Dependency Modeler 决... | design | design_only |
| 23 | D-KNOWLEDGE/Document-Code Dependency Graph Builder 文档-... | Document-Code Dependency Graph Builde... | design | design_only |
| 24 | D-KNOWLEDGE/Dynamic KG动态知识图谱 Dynamic Knowledge Graph | Dynamic KG动态知识图谱 Dynamic Knowle... | design | design_only |
| 25 | D-KNOWLEDGE/Embedding Model 嵌入模型契约 | Embedding Model 嵌入模型契约 | design | design_only |
| 26 | D-KNOWLEDGE/Event Impact Knowledge 事件影响知识 | Event Impact Knowledge 事件影响知识 | design | design_only |
| 27 | D-KNOWLEDGE/Execution Layer Dependency Modeler 执行层依赖... | Execution Layer Dependency Modeler 执... | design | design_only |
| 28 | D-KNOWLEDGE/FIX Protocol Dependency Graph Builder FIX协议... | FIX Protocol Dependency Graph Builder... | design | design_only |
| 29 | D-KNOWLEDGE/Factor Knowledge Base因子知识库 | Factor Knowledge Base因子知识库 | design | design_only |
| 30 | D-KNOWLEDGE/Factor Knowledge 因子知识 | Factor Knowledge 因子知识 | design | design_only |
| 31 | D-KNOWLEDGE/Factor Reuse Recommender 因子复用推荐器 | Factor Reuse Recommender 因子复用推荐器 | design | design_only |
| 32 | D-KNOWLEDGE/Faiss GPU 向量检索 | Faiss GPU 向量检索 | design | design_only |
| 33 | D-KNOWLEDGE/GNN/Causal ML远期实现 GNN/Causal ML Deferred | GNN/Causal ML远期实现 GNN/Causal ML D... | design | design_only |
| 34 | D-KNOWLEDGE/GNN股票关系建模 GNN Stock Relation Modeling | GNN股票关系建模 GNN Stock Relation Mo... | design | design_only |
| 35 | D-KNOWLEDGE/Graph+Vector混合RAG Graph+Vector Hybrid RAG | Graph+Vector混合RAG Graph+Vector Hybr... | design | design_only |
| 36 | D-KNOWLEDGE/Graph+Vector混合RAG Hybrid RAG | Graph+Vector混合RAG Hybrid RAG | design | design_only |
| 37 | D-KNOWLEDGE/HypothesisAccepted 假设被验证接受 | HypothesisAccepted 假设被验证接受 | design | design_only |
| 38 | D-KNOWLEDGE/Industry Chain Knowledge Graph Engine 产业链... | Industry Chain Knowledge Graph Engine... | design | design_only |
| 39 | D-KNOWLEDGE/KB Engine知识库引擎 | KB Engine知识库引擎 | design | design_only |
| 40 | D-KNOWLEDGE/Knowledge Base Search Engine 知识库搜索引擎 | Knowledge Base Search Engine 知识库搜... | design | design_only |
| 41 | D-KNOWLEDGE/Knowledge Base 知识库 | Knowledge Base 知识库 | design | design_only |
| 42 | D-KNOWLEDGE/Knowledge Classification and Strategy Extract... | Knowledge Classification and Strategy... | design | design_only |
| 43 | D-KNOWLEDGE/Knowledge Cleaning and Structuring Layer 知识... | Knowledge Cleaning and Structuring La... | design | design_only |
| 44 | D-KNOWLEDGE/Knowledge Collector 知识采集器 | Knowledge Collector 知识采集器 | design | design_only |
| 45 | D-KNOWLEDGE/Knowledge Deduplication and Merge Detector 知... | Knowledge Deduplication and Merge Det... | design | design_only |
| 46 | D-KNOWLEDGE/Knowledge Engine 知识引擎 | Knowledge Engine 知识引擎 | design | design_only |
| 47 | D-KNOWLEDGE/Knowledge Feedback Loop 知识反馈循环 | Knowledge Feedback Loop 知识反馈循环 | design | design_only |
| 48 | D-KNOWLEDGE/Knowledge Graph Build 知识图谱构建 | Knowledge Graph Build 知识图谱构建 | design | design_only |
| 49 | D-KNOWLEDGE/Knowledge Graph Engine 知识图谱引擎 | Knowledge Graph Engine 知识图谱引擎 | design | design_only |
| 50 | D-KNOWLEDGE/Knowledge Graph Explorer 知识图谱浏览器 | Knowledge Graph Explorer 知识图谱浏览器 | design | design_only |
| 51 | D-KNOWLEDGE/Knowledge Graph Visualizer 知识图谱可视化 | Knowledge Graph Visualizer 知识图谱可... | design | design_only |
| 52 | D-KNOWLEDGE/Knowledge Graph 知识图谱引擎 | Knowledge Graph 知识图谱引擎 | design | design_only |
| 53 | D-KNOWLEDGE/Knowledge Graph知识图谱 | Knowledge Graph知识图谱 | design | design_only |
| 54 | D-KNOWLEDGE/Knowledge Input Interface AC 知识输入接口(自... | Knowledge Input Interface AC 知识输入... | design | design_only |
| 55 | D-KNOWLEDGE/Knowledge Input Interface Factor 知识输入接口... | Knowledge Input Interface Factor 知识... | design | design_only |
| 56 | D-KNOWLEDGE/Knowledge Input Interface Infra 知识输入接口(... | Knowledge Input Interface Infra 知识... | design | design_only |
| 57 | D-KNOWLEDGE/Knowledge Input Interface ML 知识输入接口(机... | Knowledge Input Interface ML 知识输入... | design | design_only |
| 58 | D-KNOWLEDGE/Knowledge Input Interface Research 知识输入接... | Knowledge Input Interface Research 知... | design | design_only |
| 59 | D-KNOWLEDGE/Knowledge Input Interface Signal 知识输入接口... | Knowledge Input Interface Signal 知识... | design | design_only |
| 60 | D-KNOWLEDGE/Knowledge Output Interface AC 知识输出接口(自... | Knowledge Output Interface AC 知识输... | design | design_only |
| 61 | D-KNOWLEDGE/Knowledge Output Interface All 知识输出接口(... | Knowledge Output Interface All 知识输... | design | design_only |
| 62 | D-KNOWLEDGE/Knowledge Output Interface Frontend 知识输出... | Knowledge Output Interface Frontend ... | design | design_only |
| 63 | D-KNOWLEDGE/Knowledge Output Interface Research 知识输出... | Knowledge Output Interface Research ... | design | design_only |
| 64 | D-KNOWLEDGE/Knowledge Output Interface Signal 知识输出接... | Knowledge Output Interface Signal 知... | design | design_only |
| 65 | D-KNOWLEDGE/Knowledge Output Interface Simulation 知识输... | Knowledge Output Interface Simulation... | design | design_only |
| 66 | D-KNOWLEDGE/Knowledge Quality Assessor知识质量评估 | Knowledge Quality Assessor知识质量评估 | design | design_only |
| 67 | D-KNOWLEDGE/Knowledge Reasoner知识推理 | Knowledge Reasoner知识推理 | design | design_only |
| 68 | D-KNOWLEDGE/Knowledge Retriever 知识检索器 | Knowledge Retriever 知识检索器 | design | design_only |
| 69 | D-KNOWLEDGE/Knowledge Source Quality Scorer 知识来源质量... | Knowledge Source Quality Scorer 知识... | design | design_only |
| 70 | D-KNOWLEDGE/Knowledge Version Manager 知识版本管理器 | Knowledge Version Manager 知识版本管理器 | design | design_only |
| 71 | D-KNOWLEDGE/Knowledge Version Manager知识版本管理 | Knowledge Version Manager知识版本管理 | design | design_only |
| 72 | D-KNOWLEDGE/KnowledgeConflict 知识冲突事件 | KnowledgeConflict 知识冲突事件 | design | design_only |
| 73 | D-KNOWLEDGE/KnowledgeCreated 知识创建事件 | KnowledgeCreated 知识创建事件 | design | design_only |
| 74 | D-KNOWLEDGE/KnowledgeEntity 知识实体 | KnowledgeEntity 知识实体 | design | design_only |
| 75 | D-KNOWLEDGE/KnowledgeFeedbackLoop 知识反馈闭环 | KnowledgeFeedbackLoop 知识反馈闭环 | design | design_only |
| 76 | D-KNOWLEDGE/KnowledgeGraph Causal Chain Feed 知识图谱因果... | KnowledgeGraph Causal Chain Feed 知识... | design | design_only |
| 77 | D-KNOWLEDGE/KnowledgePackageReady 知识包就绪 | KnowledgePackageReady 知识包就绪 | design | design_only |
| 78 | D-KNOWLEDGE/KnowledgeQuery Interface 知识查询接口 | KnowledgeQuery Interface 知识查询接口 | design | design_only |
| 79 | D-KNOWLEDGE/KnowledgeRetrieved 知识检索事件 | KnowledgeRetrieved 知识检索事件 | design | design_only |
| 80 | D-KNOWLEDGE/KnowledgeStale 知识过时事件 | KnowledgeStale 知识过时事件 | design | design_only |
| 81 | D-KNOWLEDGE/KnowledgeUpdated 知识更新事件 | KnowledgeUpdated 知识更新事件 | design | design_only |
| 82 | D-KNOWLEDGE/L1 to L2-D Knowledge Graph L1→L2-D知识图谱 | L1 to L2-D Knowledge Graph L1→L2-D知... | design | design_only |
| 83 | D-KNOWLEDGE/L2-D 知识图谱与因果推演数据 Knowledge Graph &... | L2-D 知识图谱与因果推演数据 Knowledge... | design | design_only |
| 84 | D-KNOWLEDGE/LangMem LangMem记忆系统 | LangMem LangMem记忆系统 | design | design_only |
| 85 | D-KNOWLEDGE/Lesson Learned Base教训知识库 | Lesson Learned Base教训知识库 | design | design_only |
| 86 | D-KNOWLEDGE/Letta Letta记忆系统 | Letta Letta记忆系统 | design | design_only |
| 87 | D-KNOWLEDGE/Liquidity Knowledge 流动性知识 | Liquidity Knowledge 流动性知识 | design | design_only |
| 88 | D-KNOWLEDGE/Low-Latency Dependency Critical Path Analyzer... | Low-Latency Dependency Critical Path ... | design | design_only |
| 89 | D-KNOWLEDGE/MAGMA MAGMA记忆系统 | MAGMA MAGMA记忆系统 | design | design_only |
| 90 | D-KNOWLEDGE/Market Data Feed Dependency Failover Model 行... | Market Data Feed Dependency Failover ... | design | design_only |
| 91 | D-KNOWLEDGE/Market Knowledge Base市场知识库 | Market Knowledge Base市场知识库 | design | design_only |
| 92 | D-KNOWLEDGE/Mem0 Mem0记忆系统 | Mem0 Mem0记忆系统 | design | design_only |
| 93 | D-KNOWLEDGE/Memory Consolidation & Forgetting 记忆巩固与遗忘 | Memory Consolidation & Forgetting 记... | design | design_only |
| 94 | D-KNOWLEDGE/Memory Graph Database 记忆图数据库 | Memory Graph Database 记忆图数据库 | design | design_only |
| 95 | D-KNOWLEDGE/Meta-Learning and Self-Evolution Layer 元学习... | Meta-Learning and Self-Evolution Laye... | design | design_only |
| 96 | D-KNOWLEDGE/Methodology Knowledge 方法论知识 | Methodology Knowledge 方法论知识 | design | design_only |
| 97 | D-KNOWLEDGE/Module Creation and Integration Layer 模块创... | Module Creation and Integration Layer... | design | design_only |
| 98 | D-KNOWLEDGE/Module Mapping Result 模块映射结果 | Module Mapping Result 模块映射结果 | design | design_only |
| 99 | D-KNOWLEDGE/Module Mapping and Factory Matching Layer 模... | Module Mapping and Factory Matching L... | design | design_only |
| 100 | D-KNOWLEDGE/Monte Carlo Cascade Simulator 蒙特卡洛级联失... | Monte Carlo Cascade Simulator 蒙特卡... | design | design_only |
| 101 | D-KNOWLEDGE/Multimodal Knowledge Collection Layer 多模态... | Multimodal Knowledge Collection Layer... | design | design_only |
| 102 | D-KNOWLEDGE/Obsidian Knowledge Base Integrator Obsidian知... | Obsidian Knowledge Base Integrator Ob... | design | design_only |
| 103 | D-KNOWLEDGE/Order Lifecycle Dependency State Machine 委托... | Order Lifecycle Dependency State Mach... | design | design_only |
| 104 | D-KNOWLEDGE/Package Init 包初始化 | Package Init 包初始化 | design | design_only |
| 105 | D-KNOWLEDGE/Python AST Parser Python AST解析器 | Python AST Parser Python AST解析器 | design | design_only |
| 106 | D-KNOWLEDGE/Python Dynamic Call Graph Enhancer Python动态... | Python Dynamic Call Graph Enhancer Py... | design | design_only |
| 107 | D-KNOWLEDGE/RAG Retriever知识检索 | RAG Retriever知识检索 | design | design_only |
| 108 | D-KNOWLEDGE/RAGPipeline RAG管线 | RAGPipeline RAG管线 | design | design_only |
| 109 | D-KNOWLEDGE/Research Project Registry & Note Manager 研究... | Research Project Registry & Note Mana... | design | design_only |
| 110 | D-KNOWLEDGE/ResearchDiscovery 研究发现 | ResearchDiscovery 研究发现 | design | design_only |
| 111 | D-KNOWLEDGE/Risk Check Dependency Short-Circuit Evaluator... | Risk Check Dependency Short-Circuit E... | design | design_only |
| 112 | D-KNOWLEDGE/Risk Layer Dependency Modeler 风控层依赖建模器 | Risk Layer Dependency Modeler 风控层... | design | design_only |
| 113 | D-KNOWLEDGE/Risk Management Knowledge 风控知识 | Risk Management Knowledge 风控知识 | design | design_only |
| 114 | D-KNOWLEDGE/Risk Mitigation Strategy Recommender 风险缓解... | Risk Mitigation Strategy Recommender ... | design | design_only |
| 115 | D-KNOWLEDGE/Risk Propagation Modeler 风险传播建模器 | Risk Propagation Modeler 风险传播建模器 | design | design_only |
| 116 | D-KNOWLEDGE/SQLite FTS5 SQLite FTS5全文检索 | SQLite FTS5 SQLite FTS5全文检索 | design | design_only |
| 117 | D-KNOWLEDGE/Semantic Interpretation 语义理解结果 | Semantic Interpretation 语义理解结果 | design | design_only |
| 118 | D-KNOWLEDGE/Semantic Memory 语义记忆 | Semantic Memory 语义记忆 | design | design_only |
| 119 | D-KNOWLEDGE/Statistical Analyzer 统计分析器 | Statistical Analyzer 统计分析器 | design | design_only |
| 120 | D-KNOWLEDGE/Strategy Knowledge Base策略知识库 | Strategy Knowledge Base策略知识库 | design | design_only |
| 121 | D-KNOWLEDGE/Stress Test Integrator 压力测试集成器 | Stress Test Integrator 压力测试集成器 | design | design_only |
| 122 | D-KNOWLEDGE/Structured Trading Logic 结构化交易逻辑 | Structured Trading Logic 结构化交易逻辑 | design | design_only |
| 123 | D-KNOWLEDGE/Systemic Risk Assessor 系统性风险评估器 | Systemic Risk Assessor 系统性风险评估器 | design | design_only |
| 124 | D-KNOWLEDGE/Systemic Risk Early Warning System 系统性风险... | Systemic Risk Early Warning System 系... | design | design_only |
| 125 | D-KNOWLEDGE/Trial Operation and Validation Layer 试运行与... | Trial Operation and Validation Layer ... | design | design_only |
| 126 | D-KNOWLEDGE/Trial Result 试运行结果 | Trial Result 试运行结果 | design | design_only |
| 127 | D-KNOWLEDGE/Type Inference Enhanced Call Graph 类型推断增... | Type Inference Enhanced Call Graph 类... | design | design_only |
| 128 | D-KNOWLEDGE/Vector Memory向量记忆 | Vector Memory向量记忆 | design | design_only |
| 129 | D-KNOWLEDGE/Zep Zep记忆系统 | Zep Zep记忆系统 | design | design_only |
| 130 | D-KNOWLEDGE/产业图谱 Industry Chain Graph | 产业图谱 Industry Chain Graph | design | design_only |
| 131 | D-KNOWLEDGE/产业图谱优先于宏观因果链 Industry Graph Priority | 产业图谱优先于宏观因果链 Industry Gra... | design | design_only |
| 132 | D-KNOWLEDGE/供应链图谱 Supply Chain Graph | 供应链图谱 Supply Chain Graph | design | design_only |
| 133 | D-KNOWLEDGE/公司图谱 Company Graph | 公司图谱 Company Graph | design | design_only |
| 134 | D-KNOWLEDGE/动态图谱 Dynamic Knowledge Graph | 动态图谱 Dynamic Knowledge Graph | design | design_only |
| 135 | D-KNOWLEDGE/向量数据库+RAG架构 Vector DB+RAG | 向量数据库+RAG架构 Vector DB+RAG | design | design_only |
| 136 | D-KNOWLEDGE/向量数据库选型ChromaDB+Faiss GPU Vector DB Se... | 向量数据库选型ChromaDB+Faiss GPU Vect... | design | design_only |
| 137 | D-KNOWLEDGE/图谱存储用NetworkX而非Neo4j NetworkX over Neo4j | 图谱存储用NetworkX而非Neo4j NetworkX ... | design | design_only |
| 138 | D-KNOWLEDGE/图谱类型体系 Knowledge Graph Types | 图谱类型体系 Knowledge Graph Types | design | design_only |
| 139 | D-KNOWLEDGE/地缘政治图谱 Geopolitical Graph | 地缘政治图谱 Geopolitical Graph | design | design_only |
| 140 | D-KNOWLEDGE/宏观因果链 Macro Causal Chain | 宏观因果链 Macro Causal Chain | design | design_only |
| 141 | D-KNOWLEDGE/时序KG预测 Temporal KG Forecasting | 时序KG预测 Temporal KG Forecasting | design | design_only |
| 142 | D-KNOWLEDGE/知识图谱 知识图谱 Knowledge Graph | 知识图谱 知识图谱 Knowledge Graph | design | design_only |
| 143 | D-KNOWLEDGE/知识库 Knowledge Base | 知识库 Knowledge Base | design | design_only |
| 144 | D-KNOWLEDGE/金融知识图谱 Financial Knowledge Graph | 金融知识图谱 Financial Knowledge Graph | design | design_only |

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 150 条 / 150 edges）。按依赖类型分组，使用 → 表示方向。

```

┌──────────────────────────────────────────────────────────────────┐
│      依赖关系图 / Dependency Graph (共 150 条 / 150 edges)       │
├──────────────────────────────────────────────────────────────────┤
│   依赖类型数 / Dependency Types: 6                               │
│   [import_depends]: 116 条 / edges                               │
│   [contract]: 15 条 / edges                                      │
│   [event]: 9 条 / edges                                          │
│   [config_depends]: 5 条 / edges                                 │
│   [runtime]: 4 条 / edges                                        │
│   [data]: 1 条 / edges                                           │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                [import_depends] (116 条 / edges)                 │
├──────────────────────────────────────────────────────────────────┤
│   Knowledge Graph 知识图谱引擎 → 动态图谱 Dynamic Knowledg...    │
│   D-KNOWLEDGE 知识 → Knowledge Graph知识图谱                     │
│   Knowledge Graph知识图谱 → Factor Knowledge Base因子...         │
│   Factor Knowledge Base因子... → Strategy Knowledge Base策...    │
│   Strategy Knowledge Base策... → Lesson Learned Base教训知...    │
│   Lesson Learned Base教训知... → Market Knowledge Base市场...    │
│   Market Knowledge Base市场... → KB Engine知识库引擎             │
│   KB Engine知识库引擎 → Vector Memory向量记忆                    │
│   Vector Memory向量记忆 → RAG Retriever知识检索                  │
│   RAG Retriever知识检索 → Knowledge Reasoner知识推理             │
│   RAG Retriever知识检索 → AgentDock AgentDock记忆系统            │
│   Knowledge Reasoner知识推理 → Knowledge Version Manager...      │
│   Knowledge Version Manager... → Knowledge Quality Assesso...    │
│   Knowledge Version Manager... → LangMem LangMem记忆系统         │
│   Knowledge Quality Assesso... → AI Auto Knowledge Extract...    │
│   Knowledge Quality Assesso... → Structured Trading Logic ...    │
│   AI Auto Knowledge Extract... → D-KNOWLEDGE-12 知识             │
│   D-KNOWLEDGE-12 知识 → D-KNOWLEDGE-18 知识                      │
│   D-KNOWLEDGE-18 知识 → ChromaDB 向量索引                        │
│   ChromaDB 向量索引 → Faiss GPU 向量检索                         │
│   ChromaDB 向量索引 → 向量数据库+RAG架构 Vector...               │
│   Faiss GPU 向量检索 → L2-D 知识图谱与因果推演数...              │
│   Faiss GPU 向量检索 → Methodology Knowledge 方...               │
│   L2-D 知识图谱与因果推演数... → Graph+Vector混合RAG Hybri...    │
│   Graph+Vector混合RAG Hybri... → 图谱类型体系 Knowledge Gr...    │
│   图谱类型体系 Knowledge Gr... → 公司图谱 Company Graph          │
│   图谱类型体系 Knowledge Gr... → Letta Letta记忆系统             │
│   公司图谱 Company Graph → 产业图谱 Industry Chain G...          │
│   公司图谱 Company Graph → CoALA CoALA记忆框架                   │
│   产业图谱 Industry Chain G... → 供应链图谱 Supply Chain G...    │
│   产业图谱 Industry Chain G... → Conflict Report 矛盾报告        │
│   供应链图谱 Supply Chain G... → 宏观因果链 Macro Causal C...    │
│   供应链图谱 Supply Chain G... → Zep Zep记忆系统                 │
│   宏观因果链 Macro Causal C... → 地缘政治图谱 Geopolitical...    │
│   地缘政治图谱 Geopolitical... → GNN股票关系建模 GNN Stock...    │
│   GNN股票关系建模 GNN Stock... → Causal ML因果推断 Causal ML     │
│   Causal ML因果推断 Causal ML → 动态图谱 Dynamic Knowledg...     │
│   动态图谱 Dynamic Knowledg... → Industry Chain Knowledge ...    │
│   Graph+Vector混合RAG Graph... → Dynamic KG动态知识图谱 Dy...    │
│   Industry Chain Knowledge ... → C-016 产业链图谱适配层 In...    │
│   Industry Chain Knowledge ... → Module Mapping Result 模...     │
│   C-016 产业链图谱适配层 In... → C-016 公司图谱 Company Graph    │
│   C-016 产业链图谱适配层 In... → Memory Graph Database 记...     │
│   C-016 公司图谱 Company Graph → Knowledge Base 知识库           │
│   Knowledge Base 知识库 → Risk Propagation Modeler ...           │
│   Knowledge Base 知识库 → Causal Edges 因果边列表                │
│   Risk Propagation Modeler ... → Systemic Risk Assessor 系...    │
│   Systemic Risk Assessor 系... → Knowledge Graph Explorer ...    │
│   Knowledge Graph Explorer ... → Knowledge Feedback Loop ...     │
│   ...还有 67 条 / 67 more edges                                  │
└──────────────────────────────────────────────────────────────────┘

**[contract]** (15 条 / edges) — 已达显示上限，省略 / limit reached

**[event]** (9 条 / edges) — 已达显示上限，省略 / limit reached

**[config_depends]** (5 条 / edges) — 已达显示上限，省略 / limit reached

**[runtime]** (4 条 / edges) — 已达显示上限，省略 / limit reached

**[data]** (1 条 / edges) — 已达显示上限，省略 / limit reached

> (最多显示前 50 条依赖边，共 150 条)

```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_architecture_diagram.py`
- **维护方式 / Maintenance**: 自动生成，depgraph.db 变更时 CI 自动刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}_architecture.md`，如 `30_d_knowledge_architecture.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
