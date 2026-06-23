---
doc_type: domain_architecture_doc
title: D-KNOWLEDGE knowledge_management架构文档
version: "1.0"
status: active
date: 2026-06-23
owner: auto-generator
ttl: permanent
---

# D-KNOWLEDGE knowledge_management架构文档

> 本文档由 generate_domain_doc.py 从 depgraph.db 自动生成
> 最后更新: 2026-06-23 13:28:28
> 数据源: depgraph.db nodes表 + edges表

## 域概览

| 属性 | 值 |
|------|-----|
| 域ID | D-KNOWLEDGE |
| 域名称 | knowledge_management |
| 架构层 | L2_domain |
| 模块总数 | 160 |
| 设计态模块 | 153 |
| 原型态模块 | 1 |
| 生产态模块 | 0 |
| 容量 | 0/150 (正常) |
| 描述 | 知识管线(ingest/triage/extract/activate/analyze) |

## 模块清单

共 160 个模块（按路径排序，最多显示前 200 个）

| 模块路径 | 蓝图ID | 构建状态 | 设计成熟度 | 入度 | 出度 |
|---------|--------|---------|-----------|:---:|:---:|
| D-KNOWLEDGE/5层记忆架构 5-Layer Memory Architecture |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/AI Auto Knowledge Extractor AI自动知识提取 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/AgentDock AgentDock记忆系统 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/C-016 产业链图谱适配层 Industry Chain Graph Adapter |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/C-016 公司图谱 Company Graph |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Call Graph Incremental Updater 调用图增量更新器 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Cascade Failure Simulator 级联失效仿真器 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Case Library Tag System 案例库标签体系 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Causal Edges 因果边列表 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Causal ML因果推断 Causal ML |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Causal Reasoner 因果推理器 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/ChromaDB 向量索引 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/CoALA CoALA记忆框架 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Colocation Dependency Topology Optimizer 托管依赖拓扑优化器 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Conflict Report 矛盾报告 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Cross-Layer Dependency Analyzer 跨层依赖分析器 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/D-KNOWLEDGE 知识 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/D-KNOWLEDGE-12 知识 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/D-KNOWLEDGE-18 知识 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Data Layer Dependency Modeler 数据层依赖建模器 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Databricks Memory Research Databricks记忆研究 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Decision Layer Dependency Modeler 决策层依赖建模器 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Document-Code Dependency Graph Builder 文档-代码依赖图构建器 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Dynamic KG动态知识图谱 Dynamic Knowledge Graph |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Embedding Model 嵌入模型契约 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Event Impact Knowledge 事件影响知识 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Execution Layer Dependency Modeler 执行层依赖建模器 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/FIX Protocol Dependency Graph Builder FIX协议依赖图构建器 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Factor Knowledge Base因子知识库 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Factor Knowledge 因子知识 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Factor Reuse Recommender 因子复用推荐器 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Faiss GPU 向量检索 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/GNN/Causal ML远期实现 GNN/Causal ML Deferred |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/GNN股票关系建模 GNN Stock Relation Modeling |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Graph+Vector混合RAG Graph+Vector Hybrid RAG |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Graph+Vector混合RAG Hybrid RAG |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/HypothesisAccepted 假设被验证接受 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Industry Chain Knowledge Graph Engine 产业链知识图谱引擎 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/KB Engine知识库引擎 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Knowledge Base Search Engine 知识库搜索引擎 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Knowledge Base 知识库 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Knowledge Classification and Strategy Extraction Layer 知识分类与策略提取层 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Knowledge Cleaning and Structuring Layer 知识清洗与结构化层 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Knowledge Collector 知识采集器 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Knowledge Deduplication and Merge Detector 知识去重与合并检测器 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Knowledge Engine 知识引擎 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Knowledge Feedback Loop 知识反馈循环 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Knowledge Graph Build 知识图谱构建 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Knowledge Graph Engine 知识图谱引擎 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Knowledge Graph Explorer 知识图谱浏览器 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Knowledge Graph Visualizer 知识图谱可视化 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Knowledge Graph 知识图谱引擎 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Knowledge Graph知识图谱 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Knowledge Input Interface AC 知识输入接口(自治域) |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Knowledge Input Interface Factor 知识输入接口(因子域) |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Knowledge Input Interface Infra 知识输入接口(基础设施域) |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Knowledge Input Interface ML 知识输入接口(机器学习域) |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Knowledge Input Interface Research 知识输入接口(研究域) |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Knowledge Input Interface Signal 知识输入接口(信号域) |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Knowledge Output Interface AC 知识输出接口(自治域) |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Knowledge Output Interface All 知识输出接口(全域) |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Knowledge Output Interface Frontend 知识输出接口(前端域) |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Knowledge Output Interface Research 知识输出接口(研究域) |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Knowledge Output Interface Signal 知识输出接口(信号域) |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Knowledge Output Interface Simulation 知识输出接口(仿真域) |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Knowledge Quality Assessor知识质量评估 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Knowledge Reasoner知识推理 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Knowledge Retriever 知识检索器 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Knowledge Source Quality Scorer 知识来源质量评分器 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Knowledge Version Manager 知识版本管理器 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Knowledge Version Manager知识版本管理 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/KnowledgeConflict 知识冲突事件 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/KnowledgeCreated 知识创建事件 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/KnowledgeEntity 知识实体 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/KnowledgeFeedbackLoop 知识反馈闭环 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/KnowledgeGraph Causal Chain Feed 知识图谱因果链供给 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/KnowledgePackageReady 知识包就绪 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/KnowledgeQuery Interface 知识查询接口 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/KnowledgeRetrieved 知识检索事件 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/KnowledgeStale 知识过时事件 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/KnowledgeUpdated 知识更新事件 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/L1 to L2-D Knowledge Graph L1→L2-D知识图谱 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/L2-D 知识图谱与因果推演数据 Knowledge Graph & Causal |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/LangMem LangMem记忆系统 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Lesson Learned Base教训知识库 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Letta Letta记忆系统 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Liquidity Knowledge 流动性知识 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Low-Latency Dependency Critical Path Analyzer 低延迟依赖关键路径分析器 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/MAGMA MAGMA记忆系统 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Market Data Feed Dependency Failover Model 行情数据源依赖故障转移模型 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Market Knowledge Base市场知识库 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Mem0 Mem0记忆系统 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Memory Consolidation & Forgetting 记忆巩固与遗忘 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Memory Graph Database 记忆图数据库 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Meta-Learning and Self-Evolution Layer 元学习与自我进化层 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Methodology Knowledge 方法论知识 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Module Creation and Integration Layer 模块创建与接入层 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Module Mapping Result 模块映射结果 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Module Mapping and Factory Matching Layer 模块映射与工厂匹配层 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Monte Carlo Cascade Simulator 蒙特卡洛级联失效模拟器 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Multimodal Knowledge Collection Layer 多模态知识采集层 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Obsidian Knowledge Base Integrator Obsidian知识库集成器 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Order Lifecycle Dependency State Machine 委托生命周期依赖状态机 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Package Init 包初始化 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Python AST Parser Python AST解析器 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Python Dynamic Call Graph Enhancer Python动态调用图增强器 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/RAG Retriever知识检索 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/RAGPipeline RAG管线 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Research Project Registry & Note Manager 研究项目登记与笔记管理器 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/ResearchDiscovery 研究发现 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Risk Check Dependency Short-Circuit Evaluator 风控检查依赖短路评估器 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Risk Layer Dependency Modeler 风控层依赖建模器 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Risk Management Knowledge 风控知识 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Risk Mitigation Strategy Recommender 风险缓解策略推荐器 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Risk Propagation Modeler 风险传播建模器 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/SQLite FTS5 SQLite FTS5全文检索 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Semantic Interpretation 语义理解结果 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Semantic Memory 语义记忆 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Statistical Analyzer 统计分析器 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Strategy Knowledge Base策略知识库 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Stress Test Integrator 压力测试集成器 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Structured Trading Logic 结构化交易逻辑 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Systemic Risk Assessor 系统性风险评估器 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Systemic Risk Early Warning System 系统性风险早期预警系统 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Trial Operation and Validation Layer 试运行与验证层 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Trial Result 试运行结果 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Type Inference Enhanced Call Graph 类型推断增强调用图 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Vector Memory向量记忆 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/Zep Zep记忆系统 |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/产业图谱 Industry Chain Graph |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/产业图谱优先于宏观因果链 Industry Graph Priority |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/供应链图谱 Supply Chain Graph |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/公司图谱 Company Graph |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/动态图谱 Dynamic Knowledge Graph |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/向量数据库+RAG架构 Vector DB+RAG |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/向量数据库选型ChromaDB+Faiss GPU Vector DB Selection |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/图谱存储用NetworkX而非Neo4j NetworkX over Neo4j |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/图谱类型体系 Knowledge Graph Types |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/地缘政治图谱 Geopolitical Graph |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/宏观因果链 Macro Causal Chain |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/时序KG预测 Temporal KG Forecasting |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/知识图谱 知识图谱 Knowledge Graph |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/知识库 Knowledge Base |  | design_only | design | 0 | 0 |
| D-KNOWLEDGE/金融知识图谱 Financial Knowledge Graph |  | design_only | design | 0 | 0 |
| src/zephyr/knowledge/__init__.py | MOD-KNOWLEDGE | orphan | prototype | 0 | 0 |
| src/zephyr/knowledge/_extensions/__init__.py | MOD-KNOWLEDGE | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/knowledge/api/__init__.py | MOD-KNOWLEDGE | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/knowledge/core/__init__.py | MOD-KNOWLEDGE | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/knowledge/infrastructure/__init__.py | MOD-KNOWLEDGE | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/knowledge/models/__init__.py | MOD-KNOWLEDGE | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/knowledge/services/__init__.py | MOD-KNOWLEDGE | orphan | scaffold_placeholder | 0 | 0 |
| 知识域-AI提取/D-KNOWLEDGE-17 | MOD-KNOWLEDGE | design_only | design | 0 | 0 |
| 知识域-图谱浏览/D-KNOWLEDGE-15 | MOD-KNOWLEDGE | design_only | design | 0 | 0 |
| 知识域-推理/D-KNOWLEDGE-09 | MOD-KNOWLEDGE | design_only | design | 0 | 6 |
| 知识域-搜索/D-KNOWLEDGE-21 | MOD-KNOWLEDGE | design_only | design | 0 | 0 |
| 知识域-案例管理/D-KNOWLEDGE-23 | MOD-KNOWLEDGE | design_only | design | 0 | 0 |
| 知识域-沉淀/D-KNOWLEDGE-25 | MOD-KNOWLEDGE | design_only | design | 0 | 0 |
| 知识域-质量评估/D-KNOWLEDGE-11 | MOD-KNOWLEDGE | design_only | design | 0 | 0 |
| 知识域-金融图谱/D-KNOWLEDGE-13 | MOD-KNOWLEDGE | design_only | design | 0 | 0 |
| 知识域-集成/D-KNOWLEDGE-19 | MOD-KNOWLEDGE | design_only | design | 0 | 0 |

## 跨域依赖

### 本域依赖的其他域（出边）

| 目标域 | 依赖数 | 依赖类型 |
|--------|:---:|---------|
| D-RISK | 29 | contract,data,event,config_depends |
| D-SECURITY | 17 | contract,event,data,config_depends |
| D-MKT_DATA | 11 | contract,data,event |
| D-FACTOR | 11 | contract,event,data,config_depends |
| D-SIGNAL | 10 | contract,config_depends,event,data |
| D-INFRA_RUNTIME | 10 | contract,event,data |
| D-DATA_ENG | 8 | domain_dependency,contract,event,data |
| D-ML_TRAIN | 5 | contract,data |
| D-SHARED | 4 | contract,event,data |
| D-POSITION | 4 | data,contract,config_depends |
| D-ML_SERVE | 3 | config_depends,data,event |
| D-EX_CORE | 3 | event,data,contract |
| D-TRADING | 2 | contract,data |

### 依赖本域的其他域（入边）

| 源域 | 依赖数 | 依赖类型 |
|------|:---:|---------|
| D-COMPLIANCE | 32 | event,data,contract,config_depends |
| D-GOVERNANCE | 19 | contract,data,event |
| D-INTELLIGENCE | 18 | event,config_depends,domain_dependency,contract,data |
| D-INFRA_OPS | 18 | contract,data,event,config_depends |
| D-AUTONOMY_CORE | 17 | contract,event,config_depends,data |
| D-INTEGRATION | 15 | contract,data,event,config_depends |
| D-OPS | 8 | contract,event,data |
| D-AUTONOMY_PERM | 7 | contract,data,event,config_depends |
| D-FRONTEND | 6 | event,data,contract |
| D-PF_CORE | 4 | event,config_depends,contract |
| D-SELL_DECISION | 3 | event,config_depends,data |
| D-PF_ALLOC | 3 | event,contract,config_depends |
| D-DATA_GOV | 3 | data,contract |
| D-SIMULATION | 2 | event,contract |
| D-CROSS_ASSET | 2 | event,config_depends |
| D-ALT_DATA | 2 | contract,event |
| D-REPORTING | 1 | contract |
| D-DATA_SEC | 1 | data |

## 域内依赖图

详见 [d_knowledge_dependency.mmd](d_knowledge_dependency.mmd)
