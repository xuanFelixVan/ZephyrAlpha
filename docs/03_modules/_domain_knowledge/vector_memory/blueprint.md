---
module_id: MOD-INF-011
submodule_path: src/zephyr/integration/vector_memory
title: "Vector Memory Service 蓝图+施工图 — ChromaDB 8 Collection 统一向量持久化"
doc_type: blueprint
status: Active
version: "0.12.1"
layer: L1_foundation
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-05"
valid_from: "2026-05-05"
ttl: permanent
construction_progress: partially_implemented
belongs_to: "MOD-MASTER_BLUEPRINT"
actual_disk_path: "src/zephyr/integration/vector_memory/"
last_updated: "2026-05-18"
last_verified: "2026-05-18"
generation: 1
functional_domain: data
layer_name: "infra_ops"
summary: "VMS 蓝图——ChromaDB 0.6 + 双嵌入维度（BGE-M3 1024d + bge-small-zh-v1.5 512d）本地推理。8大Collection。Phase 0-3 完成，Phase 4 待施工。四轮80盲点全维度覆盖。v0.12.0 MOD-INF-039拆分对齐+SSoT修正+测试修复。"
template_for: blueprint
tags: [vector_memory, vms, chromadb, bge-m3, embedding, vector-db, collections, infrastructure, hybrid-search, provenance]
priority: P0
runtime_plane: hot
parent_module: ""
rule_form: structural
scope: global
stability: stable
verifiability: hybrid
codification_level: L2
ssot_claims:
  - {claim: "全系统统一向量存储与检索", scope: "global"}
  - {claim: "8 Collection Schema定义", scope: "global"}
  - {claim: "混合检索(Vector+BM25+RRF)算法", scope: "module"}
  - {claim: "WriteTrace provenance校验", scope: "module"}
depends_on:
  - {target: "MOD-MASTER_BLUEPRINT", at: "§2.6", why: "CT-CE-VMS-001 集成契约——CE→VMS向量检索"}
  - {target: "MOD-KB-001", at: "§1.5", why: "知识库——beta VMS整合目标"}
  - {target: "MOD-CONTEXT_ENGINE", at: "§2.1", why: "CE——VMS的主要消费方"}
  - {target: "MOD-INF-039", at: "§2.1", why: "本地模型推理——嵌入路由/缓存/Ollama/调度已拆分至MOD-INF-039"}
  - {target: "architecture_model/layers/b_vector_memory.yaml", at: "全篇", why: "VMS YAML 派生格式——本蓝图为真源，YAML 为机器可读派生"}
  - {target: "KBG-0016", at: "§3", why: "VMS生产级嵌入与分块契约——BGE-M3真源"}
  - {target: "KBG-0031", at: "§4.2", why: "Phase 2 ChromaDB基线选型——kb/ 4 Collection现有实现依据"}
references:
  - {id: "MOD-FEEDBACK_LOOP", at: "§3.1", why: "FLE 消费检索反馈——仅存 references，断开 depends_on DAG 环"}
  - {id: "MOD-INF-020", at: "§12", why: "VMS→线3审计追踪链输出嵌入结果——仅存 references，VMS不依赖Audit Trail运行"}
responsibility_domain: 
design_maturity: design
build_status: planned
---

<!--
COMPLIANCE_CHECKLIST — 机器可解析合规清单
蓝图 MUST 包含以下所有标题（精确匹配关键词）。缺一 = 不合规。
脚本：python scripts/governance/check_blueprint_compliance.py <蓝图路径>
-->

<!--
REQUIRED_SECTIONS:
  overview: "概述"
  §0: "代码对齐验证"
  §0.1: "代码文件清单"
  §0.2: "对齐验证矩阵"
  §0.3: "版本-代码映射"
  §1: "设计背景与目标"
  §1.1: "背景"
  §1.2: "目标范围"
  §1.4: "运行场景约束"
  §1.5: "利益相关者"
  §2: "模块边界"
  §2.1: "职责边界"
  §3: "架构设计"
  §3.1: "组件架构"
  §3.2: "数据流"
  §3.3: "状态生命周期"
  §4: "接口契约"
  §4.1: "公共 API"
  §4.2: "数据模型"
  §4.3: "输入契约"
  §4.4: "输出契约"
  §4.6: "契约版本"
  §4.7: "OCP 扩展点"
  §5: "约束条件"
  §5.1: "技术约束"
  §5.2: "容量估算"
  §5.3: "迁移"
  §5.4: "非功能需求与服务水平"
  §5.7: "禁止模式与导入约束"
  §6: "错误处理"
  §6.1: "可观测性"
  §6.2: "退化矩阵"
  §6.3: "业务连续性"
  §6.4: "级联失效"
  §8: "安全考量"
  §9: "测试策略"
  §10: "依赖关系"
  §11: "产出物"
  §12: "集成目标"
  §13: "需要更新"
  §14: "风险"
  §16: "施工指引"
  §17: "容量升级"
  §18: "决策记录"
  glossary: "术语表"
  blindspots: "已知问题"
  checklist: "自检与闭合清单"
  maturity: "成熟度"
  roadmap: "版本演进路线图"
  pre_1: "Vibe Coding"
  pre_2: "安全删除"
  pre_3: "必备链接"
  pre_4: "已有类似功能"
  pre_5: "涉及的文件范围"
END_REQUIRED_SECTIONS
-->

# Vector Memory Service 蓝图+施工图 — ChromaDB 8 Collection 统一向量持久化

> **module_id**: MOD-INF-011 | **version**: 0.12.1 | **status**: active | **layer**: cross_layer
> **actual_disk_path**: `src/zephyr/integration/vector_memory/` | **generation**: 1 | **construction_progress**: partially_implemented

## 概述

VMS 是全系统统一向量记忆体——所有系统（Orc、KB、CE、FLE）产出的需要语义检索的内容最终都写入 VMS。核心架构：ChromaDB 0.6 + 双嵌入维度（BGE-M3 1024d 主路径 + bge-small-zh-v1.5 512d 轻量路径）+ 8 大 Collection + 混合检索（Vector+BM25+RRF）。设计哲学：可审计（WriteTrace provenance 强制）、可自愈（IndexHealthMonitor 自动修复）、可持续（TTL+compaction+检索质量闭环）。Phase 0-3 已完成，Phase 4 运维自动化待施工。上游依赖 CE（主要消费方）和 KB（整合目标），下游被 Orc、FLE、Governance 消费。

**线2（AI认知线）流水线位置**：上下文需求 → MOD-CONTEXT_ENGINE(CE) → MOD-KB-001(KB) → **MOD-INF-011(VMS)** → MOD-LLM_SECURITY(LLM安全网关) → MOD-INF-034(模型检测器) → MOD-INF-036(AI入职考试) → LLM响应+路由决策。VMS 向线3审计追踪链输出嵌入结果。C轨域：VMS → D_FACTOR(Alpha因子层) 因子语义检索 + VMS → D_ML_TRAIN(ML平台层) 模型语义检索。

> **标准锚点（防幻觉）**——本蓝图必须严格遵循以下标准：
> - 蓝图+施工图模板：[blueprint-construction-template.md](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/templates/blueprint-construction-template.md)
> - AI 压缩工作流标准：[trae_030_doc_numbering_metadata.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_030_doc_numbering_metadata.yaml)
> - 代码头部标准：[code-construction-standards.md §7](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/governance/engineering/code-construction-standards.md)
> - 优化规则：先 Layer 1（蓝图模板合规）→ 后 Layer 2（规格化砍削）

> **真源声明**：本蓝图是 VMS 架构设计、接口契约、施工指引的唯一真源。[b_vector_memory.yaml](file:///D:/ZephyrAlpha/architecture_model/layers/b_vector_memory.yaml) 是本蓝图的 YAML 派生格式。

| `bm25_index.py` |
| `bridge_layer.py` |
| `cache_layer.py` |
| `chunk_strategy_router.py` |
| `collection_manager.py` |
| `collection_schemas.py` |
| `cross_collection_retriever.py` |
| `delegated_vector_memory.py` |
| `design_principles.py` |
| `embedding_router.py` |
| `faiss_collection_manager.py` |
| `hybrid_retriever.py` |
| `in_memory_fake_vms.py` |
| `in_memory_memory_backend.py` |
| `in_process_vector_memory.py` |
| `index_health_monitor.py` |
| `interface.py` |
| `local_model_scheduler.py` |
| `migrate_chroma_to_faiss.py` |
| `ollama_chat.py` |
| `ollama_embedding.py` |
| `provenance_enforcer.py` |
| `retrieval_feedback.py` |
| `sqlite_metadata_store.py` |
| `vector_bridge.py` |
| `vms_errors.py` |
| `vms_schemas.py` |
| `bm25_index.py` |
---

## §0 代码对齐验证

### §0.1 代码文件清单

> **架构归属SSoT**：见 AGENTS.md §7「代码规范」（depgraph SSoT 真源唯一指针）
> **代码头部规范**：`[BLUEPRINT]/[MODULE]/[DOMAIN]/[DEPENDENCIES]/[CONSUMERS]/[STARTUP]/[MATURITY]/[INVARIANTS]/[MODIFY-GUARD]/[STABILITY]/[SAFETY]/[AI_AUTONOMY]/[ERROR_CONTRACT]/[TESTS]/[TTL]` — 见防幻觉十八条

> **完整文件清单SSoT**：`python scripts/governance/extract_depgraph.py --modules MOD-INF-011`

| # | 文件名 | 对应蓝图章节 | 职责 | 存在性 | 阻塞原因 |
|---|--------|------------|------|:-----:|---------|
| 1 | in_process_vector_memory.py | §4 | 8 Collection 核心入口 | 已实现 | |
| 2 | embedding_router.py | §3.1 | 双维度路由 | 已迁移 | MOD-INF-039 |
| 3 | chunk_strategy_router.py | §3.1 | 分块策略路由 | 已实现 | |
| 4 | hybrid_retriever.py | §3.2 | 混合检索 | 已实现 | |
| 5 | provenance_enforcer.py | §4 | WriteTrace 强制 | 已实现 | |
| 6 | index_health_monitor.py | §4 | 自检+自动修复 | 已实现 | |
| 7 | cache_layer.py | §3.1 | Embedding memoization | 已迁移 | MOD-INF-039 |
| 8 | bridge_layer.py | §5.3 | kb/ 双向桥接 | 已实现 | |
| 9 | vector_bridge.py | §12 | CE/KB 外部集成 | 已实现 | |
| 10 | retrieval_feedback.py | §4 | FLE 检索质量反馈 | 已实现 | |
| 11 | cross_collection_retriever.py | §3.2 | 跨 Collection 联合检索 | 已实现 | |
| 12 | collection_manager.py | §4 | Collection 管理 | 已实现 | |
| 13 | vms_schemas.py | §4.2 | 数据模型 | 已实现 | |
| 14 | interface.py | §4 | VMS 接口基类 | 已实现 | |
| 15 | delegated_vector_memory.py | §4 | RI-02 落地适配器 | 已实现 | |
| 16 | in_memory_memory_backend.py | §6.2 | 降级兜底 | 已实现 | |
| 17 | in_memory_fake_vms.py | §9 | InMemoryFakeVMS 测试替身 | 已实现 | |
| 18 | faiss_collection_manager.py | §17 | FAISS HNSW/IVF+PQ 管理 | 已实现 | |
| 19 | sqlite_metadata_store.py | §3.2 | SQLite WAL+FTS5 BM25 | 已实现 | |
| 20 | ollama_embedding.py | §3.1 | Ollama 嵌入生成 | 已迁移 | MOD-INF-039 |
| 21 | ollama_chat.py | §17 | Ollama 本地 LLM 推理 | 已迁移 | MOD-INF-039 |
| 22 | local_model_scheduler.py | §17 | 本地模型调度循环 | 已迁移 | MOD-INF-039 |
| 23 | migrate_chroma_to_faiss.py | §17 | ChromaDB→FAISS 迁移 | 已实现 | |
| 24 | vms_config.yaml | §5.1 | VMS 环境配置 Schema | 已实现 | |
| 25 | __init__.py | §2 | VMS 架构归属+8 Collection docstring | 已实现 | |
| 26 | bm25_index.py | §3.2 | BM25 稀疏检索索引 | 已实现 | |
| 27 | vms_errors.py | §6 | 异常层级 SSoT | 已实现 | |
| 28 | design_principles.py | §5 | 设计原则校验 SSoT | 已实现 | |

### §0.2 对齐验证矩阵

| 验证项 | 验证方法 | 结果 |
|--------|---------|:---:|
| construction_progress = completed → 代码文件清单100%存在 | `ls src/zephyr/integration/vector_memory/` 逐文件核对 | ☐ |
| 蓝图描述的类/函数名 = 代码中的类/函数名 | `grep "class\|def" *.py` | ☐ |
| 8 Collection Schema 与代码 COLLECTION_SCHEMAS 一致 | `grep "COLLECTION_SCHEMAS" *.py` | ☐ |
| 双嵌入维度路由与代码 EmbeddingRouter 一致 | `grep "embedding_model" *.py` | ☐ |
| 代码 [BLUEPRINT] 头部指向 = 本蓝图 module_id | `grep "\[BLUEPRINT\]" *.py` 核对 module_id | ☐ |
| §4.2 每个数据模型的 SSoT 文件中确实存在该模型 | `grep "class {ModelName}" {ssot_file}.py` 逐模型核对 | ☐ |
| §0.1 每个文件的职责与其他文件无重叠 | 交叉比对职责列 | ☐ |
| §5.5 自动化触发机制状态列与代码实现一致 | `python scripts/governance/d5_architecture/checkers/check_blueprint_automation_sync.py --blueprint docs/03_modules/_domain_knowledge/vector_memory/blueprint.md` | ✅ |

### §0.3 版本-代码映射

| 蓝图版本 | 代码覆盖范围 | 缺失组件 | 缺失原因 |
|---------|------------|---------|---------|
| v0.8.0 (基线) | 25 个 .py + 1 个 .yaml 全部已实现 | Phase 4 运维自动化脚本 | 待施工 |

### §0.4 SSoT 与责任唯一性声明

| # | 声明维度 | 本蓝图是真源 | 真源在别处（委托） | 委托目标 |
|---|---------|:----------:|:---------------:|---------|
| 1 | 向量存储与检索架构 | ✅ | ❌ | — |
| 2 | 8 Collection Schema 定义 | ✅ | ❌ | — |
| 3 | 双嵌入维度路由规则 | ✅ | ❌ | — |
| 4 | 混合检索算法(Vector+BM25+RRF) | ✅ | ❌ | — |
| 5 | WriteTrace provenance 校验 | ✅ | ❌ | — |
| 6 | 索引健康自检与自愈 | ✅ | ❌ | — |
| 7 | 嵌入模型训练/微调 | ❌ | ✅ | ML团队 |
| 8 | 知识条目生命周期(G1-G5) | ❌ | ✅ | MOD-KB-001 §2 |
| 9 | 上下文装配与注入 | ❌ | ✅ | MOD-CONTEXT_ENGINE §4 |
| 10 | VMS YAML 规范 | ❌ | ✅ | b_vector_memory.yaml |

### §0.5 代码目录唯一性声明

| # | 声明项 | 值 |
|---|--------|-----|
| 1 | 主代码目录 | `src/zephyr/integration/vector_memory/` |
| 2 | 已知副本目录 | `src/zephyr/kb/` — 原因：过渡期遗留，4 旧 Collection 仍在 kb/ 中；`src/zephyr/local-model/` — 原因：MOD-INF-039 拆分后 5 个文件在两目录存在副本 |
| 3 | 副本处置状态 | kb/：迁移中(3/7已完成)；local_model/：VMS 侧为 re-export 兼容层，消费者逐步迁移至 `from zephyr.local_model import ...` |

---

## §1 设计背景与目标

### §1.1 背景

ZephyrAlpha 的 AI 治理框架需要一个统一的向量记忆体来支撑语义检索——AI session 的决策质量直接取决于它能检索到多少相关历史记忆。v0.7.0 之前，向量能力分散在 `kb/chromadb_init.py`（4+1 Collection）和 `kb/unified_memory_api.py`（WriteTrace），缺少统一入口、混合检索和检索质量闭环。

### §1.2 目标范围

| # | 类型 | 内容 | 标准/原因 |
|---|:----:|------|----------|
| G1 | ✅ 包含 | 统一 8 Collection 向量记忆体 | 所有系统通过 VMS 单一入口读写 |
| G2 | ✅ 包含 | 双嵌入维度按需分配 | BGE-M3 1024d（精度域）+ bge-small 512d（体量域） |
| G3 | ✅ 包含 | 混合检索质量 > 纯向量 | Vector+BM25+RRF top-5 精度 benchmark |
| G4 | ✅ 包含 | WriteTrace provenance 强制 | 每条写入可追溯到 origin+audit_chain |
| G5 | ✅ 包含 | 自愈索引 | IndexHealthMonitor 自动检测+修复 |
| 1 | ❌ 排除 | 分布式向量数据库（Milvus/Qdrant） | 单机部署，ChromaDB 本地嵌入式足够 |
| 2 | ❌ 排除 | 实时向量流处理 | VMS 是批处理+按需检索，非流式 |
| 3 | ❌ 排除 | 多模态嵌入（图像/音频） | 当前仅文本嵌入 |

### §1.4 运行场景约束

| 约束 | 影响 |
|------|------|
| 施工轨道：T轨可施工（Phase 0-3 已完成），Phase 4 C轨（解除条件：Phase 3 验收通过） | Phase 4 运维自动化需 Phase 3 验收后才可施工 |
| 单机部署，ChromaDB PersistentClient 本地嵌入式 | 无分布式需求，但需防范多进程 SQLite 写入冲突 |
| 双嵌入模型内存占用 ~800MB（BGE-M3 ~2GB + bge-small ~300MB） | 低内存环境自动降级到 bge-small 或 InMemory |

### §1.5 利益相关者映射

| 角色 | 关注点 | 参与阶段 | 约束 |
|------|--------|---------|------|
| Owner | 架构决策、Collection Schema 审批 | 设计+施工 | human-gated Collection 需审批 |
| CE (MOD-CONTEXT_ENGINE) | 检索延迟、结果质量 | 集成 | search() p95 < 200ms |
| KB (MOD-KB-001) | 数据迁移、同步写入 | 迁移 | BridgeLayer 双读过渡 |
| FLE (MOD-FEEDBACK_LOOP) | 检索反馈闭环 | 集成 | RetrievalFeedback 接口 |
| Orchestrator | 决策写入 | 集成 | decisions Collection 写入 |

### §1.6 当前态/目标态差距

| 维度 | 当前态 | 目标态 | 差距 | 优先级 |
|------|--------|--------|------|:------:|
| 向量存储 | 8 Collection 已实现，ChromaDB PersistentClient | 8 Collection + FAISS HNSW/IVF+PQ | FAISS 迁移待施工 | P1 |
| 嵌入模型 | BGE-M3 1024d + bge-small 512d 双路径 | 双路径 + 领域微调评估 | 领域微调未验证(F1) | P0 |
| 检索质量 | Vector+BM25+RRF 混合检索 | 混合检索 + reranker + benchmark | 无 benchmark + 无 reranker | P0 |
| 运维自动化 | _maintenance_loop 基础调度 | 完整 Phase 4 运维自动化 | Phase 4 待施工 | P2 |
| KB 迁移 | 3/7 完成，3/7 部分完成，1/7 未完成 | 全部 7/7 完成 + kb/ 冻结 | FLE 未接入 VMS | P1 |
| 安全 | CBAC + ProvenanceEnforcer + input_sanitizer | + 对抗性投毒检测 + PII 扫描 | 投毒检测未实现(F5) | P0 |

### §1.7 典型场景

| 场景 | 触发 | 处理流程 | 输出 |
|------|------|---------|------|
| CE 语义检索 | CE Build 阶段需要上下文 | ①CE→VMS.search(query, collections) → ②HybridRetriever.search() → ③RRF融合+time_decay → ④返回ScoredHit list | CE context_assembler 装配上下文 |
| 决策写入 | Orchestrator 完成任务决策 | ①Orc→VMS.write('decisions', text, metadata) → ②ProvenanceEnforcer.validate → ③EmbeddingRouter.embed → ④CollectionManager.write_with_provenance | 向量 ID |
| FLE 反馈 | FLE 检测到检索结果有用/无用 | ①FLE→RetrievalFeedback.record(hit_id, was_useful) → ②写入 feedback_log → ③影响后续检索排序 | FeedbackEntry |
| KB 迁移 | 知识条目入库 | ①KB→VMS.write('knowledge', ke_content, metadata) → ②BridgeLayer 双读过渡 | VMS knowledge Collection 更新 |
| 索引自愈 | IndexHealthMonitor 检测到 unhealthy | ①check_all() → ②detect_drift() → ③auto_repair() | HealthReport |
| 降级 | BGE-M3 加载失败 | ①EmbeddingRouter.warmup() 失败 → ②降级为 bge-small 512d → ③再失败降级为 InMemory | Degraded 状态运行 |

---

## §2 模块边界

### §2.1 职责边界

| # | 类型 | 职责 | 详情 | 负责方 |
|---|:----:|------|------|--------|
| 1 | ✅ 包含 | 8 Collection 向量存储 | decisions/code_context/lessons/knowledge/rules/blueprints/session_snapshots/execution_traces | 本模块 |
| 2 | ✅ 包含 | 双嵌入维度路由 | BGE-M3 1024d + bge-small 512d 按 Collection 路由 | MOD-INF-039（VMS 消费 MOD-INF-039 的 EmbeddingRouter） |
| 3 | ✅ 包含 | 混合检索 | Vector(HNSW) + BM25 + RRF 融合 + 时间衰减 | 本模块 |
| 4 | ✅ 包含 | WriteTrace provenance 强制 | origin/audit_chain/arbitration 三字段校验 | 本模块 |
| 5 | ✅ 包含 | 索引健康自检与自愈 | 漂移检测+TTL过期+自动修复 | 本模块 |
| 6 | ✅ 包含 | 检索质量反馈闭环 | FLE→VMS 反馈信号记录 | 本模块 |
| 7 | ❌ 排除 | 嵌入模型训练/微调 | 领域微调模型由外部提供 | ML团队 |
| 8 | ❌ 排除 | 分布式向量数据库运维 | 单机部署 | — |

#### 职责唯一性声明

| 声明项 | 无重叠模块 | 验证方式 |
|--------|-----------|---------|
| 统一向量存储与检索 | [MOD-KB-001(过渡期)] | KB 蓝图 §2.1 声明"向量语义检索为过渡期保留职责" |
| 8 Collection Schema | 无 | 全局唯一 |
| 双嵌入维度路由 | 无 | 全局唯一 |
| 混合检索算法 | [MOD-KB-001(过渡期)] | KB reranker.py 为兼容层 |

### 八大 Collection Schema

| Collection | 写入方 | 读取方 | 存储内容 | 嵌入维度 | 分块策略 | TTL | 预估规模 | 数据来源 | AI自治级别 |
|-----------|:-----:|:-----:|---------|:------:|---------|:---:|:------:|---------|:--------:|
| **decisions** | Orchestrator | CE、FLE | 任务决策记录 | 1024d | semantic 500-800 token | permanent | 1000-5000 | 新建 | supervised |
| **code_context** | Script System、Orc | CE | 代码上下文片段（AST-aware） | 1024d | ast_aware function/class | 90d | 500-2000 | 新建 | autonomous |
| **lessons** | FLE、Script System | CE、KB | 经验教训（失败模式+修正） | 1024d | paragraph 300-500 token | permanent | 100-500 | 继承 failure_patterns | autonomous |
| **knowledge** | KB | CE | 知识条目（KE全文向量） | 1024d | heading_aware 500-800 token | permanent | 100-1000 | 继承 ke_entries | supervised |
| **rules** | Governance | CE、Orc | 治理规则（单条rule整存，42条） | 1024d | rule_level 整条存储 | permanent | 200-500 | 继承 vibe_rules | human-gated |
| **blueprints** | Doc System | CE、Orc | 蓝图文档（按§节拆分） | 512d | section_aware 按§拆分 | permanent | 10000-30000 | 继承 blueprints | supervised |
| **session_snapshots** | SessionManager | CE | 会话压缩摘要 | 512d | session_level 单摘要 | 90d | 50-200 | 新建 | autonomous |
| **execution_traces** | All systems | FLE、CE | 运行时任务执行语义摘要 | 512d | time_window 1min窗口 | 30d | 1000-5000 | 新建（替代 runtime_logs） | autonomous |

> **继承标记**：`failure_patterns` → `lessons`，`ke_entries` → `knowledge`，`vibe_rules` → `rules`，`blueprints` → `blueprints`。Phase 2 执行数据迁移 + 重命名。

### Collection 设计原则

| 原则 | 说明 |
|------|------|
| 按访问模式分，不按数据来源分 | 高频热数据（rules/decisions）与低频冷数据（blueprints/execution_traces）分离索引 |
| 嵌入维度按精度需求分配 | 1024d 用于精确语义匹配，512d 用于量大体 |
| 分块策略 Collection 级差异化 | 代码用 AST-aware，文档用 heading-aware，日志用 time-window——不可混用 |
| TTL 强制（冷数据自动过期） | execution_traces 30d、code_context 和 session_snapshots 90d 自动清理 |
| Provenance 每条必带 | origin / audit_chain / arbitration 三位一体 |

---

## §3 架构设计

### §3.1 组件架构

| # | 组件 | 职责 | 依赖 | 交互方式 |
|---|------|------|------|---------|
| 1 | InProcessVectorMemory | 8 Collection 统一入口 | CollectionManager, EmbeddingRouter, HybridRetriever, ProvenanceEnforcer | 同步调用（CE→VMS数据流协议为async） |
| 2 | CollectionManager | 8 Collection 生命周期管理 | ChromaDB PersistentClient | 同步调用 |
| 3 | EmbeddingRouter | 双模型路由（BGE-M3/bge-small）——已迁移至MOD-INF-039 | SentenceTransformer / OllamaEmbedder | 同步调用 |
| 4 | ChunkStrategyRouter | 分块策略调度 | — | 同步调用 |
| 5 | HybridRetriever | Vector+BM25+RRF 混合检索 | EmbeddingRouter, CollectionManager | 同步调用 |
| 6 | ProvenanceEnforcer | WriteTrace 强制+CBAC 校验 | vms_schemas.WriteTrace | 同步调用 |
| 7 | IndexHealthMonitor | 自检+自动修复+漂移检测 | CollectionManager | 同步调用 |
| 8 | CacheLayer | Embedding memoization——已迁移至MOD-INF-039 | — | 同步调用 |
| 9 | BridgeLayer | kb/ ↔ VMS 双向桥接 | CollectionManager | 同步调用 |
| 10 | VectorBridge | CE/KB 外部集成适配器 | InProcessVectorMemory | 同步调用 |
| 11 | RetrievalFeedback | FLE 检索质量反馈闭环 | InProcessVectorMemory | 同步调用 |
| 12 | CrossCollectionRetriever | 跨 Collection 联合检索 | HybridRetriever | 同步调用 |
| 13 | InMemoryMemoryBackend | 降级兜底（零向量） | — | 同步调用 |

### §3.2 数据流

| # | 上游 | 处理逻辑 | 下游 | 数据格式 | 转换规则 |
|---|------|---------|------|---------|---------|
| 1 | CE/Orc/FLE/KB | ①ProvenanceEnforcer.validate → ②EmbeddingRouter.embed → ③CollectionManager.write_with_provenance | ChromaDB | dict→ndarray→ChromaDB upsert | content→embedding→(id, vector, metadata) |
| 2 | CE 检索请求 | ①EmbeddingRouter.embed(query) → ②HybridRetriever.search(dense+sparse+RRF) → ③score filter → top-k | CE context_assembler | str→RetrievalTrace | query→(dense_hits, sparse_hits)→RRF融合→ScoredHit list |
| 3 | FLE 反馈信号 | ①RetrievalFeedback.record → ②写入 feedback_log | lessons Collection | (hit_id, was_useful)→FeedbackEntry | bool→rating(1.0/0.0) |
| 4 | KB 迁移 | ①BridgeLayer.migrate_collection → ②逐条读旧Collection → ③写入新Collection | VMS Collection | ChromaDB get()→VMS write() | 旧schema→新schema映射 |

### §3.3 状态生命周期

| 当前状态 | 触发事件 | 目标状态 | 守卫条件 |
|---------|---------|---------|---------|
| NotStarted | start() 调用 | Running | ChromaDB 路径可写 |
| Running | shutdown() 调用 | Stopped | 无进行中的写入 |
| Running | BGE-M3 加载失败 | Degraded_BgeSmall | bge-small 可用 |
| Running | 双模型均不可用 | Degraded_InMemory | InMemoryBackend 可用 |
| Degraded_BgeSmall | BGE-M3 恢复可用 | Running | warmup() 成功 |
| Degraded_InMemory | 任一模型恢复 | Degraded_BgeSmall | warmup() 成功 |

---

## §4 接口契约

> 强制 **Pydantic V2 BaseModel**（KBG-0040），禁止 `@dataclass`。

### §4.1 公共 API

#### InProcessVectorMemory（统一入口）

```python
class InProcessVectorMemory:
    def start(self) -> None: ...
    def shutdown(self) -> None: ...
    def init_all_collections(self) -> list[CollectionInfo]: ...
    def list_collections(self) -> list[CollectionInfo]: ...
    def get_collection(self, name: str) -> Any: ...
    def create_collection(self, name: str, dim: int = 1024, chunk_strategy: str = "semantic", ttl_days: int = 0, ai_autonomy: str = "supervised") -> CollectionInfo: ...
    def write(self, collection_name: str, content: str, metadata: dict[str, Any] | None = None) -> str: ...
    def search(self, collection_name: str, query: str, k: int = 5) -> list[dict[str, Any]]: ...
    def recall(self, collection_name: str, k: int = 5) -> list[dict[str, Any]]: ...
    def health_check(self) -> dict[str, Any]: ...
    def clear_all(self) -> None: ...
```

| 方法 | 执行流程 | 关键决策点 |
|------|---------|-----------|
| `start()` | ①禁用ChromaDB遥测 → ②创建persist_dir → ③EmbeddingRouter.warmup() → ④初始化HybridRetriever/IndexHealthMonitor/BridgeLayer/VectorBridge/InMemoryBackend → ⑤check_all()健康基线 | warmup失败→降级模式 |
| `write()` | ①DesignPrinciplesEnforcer.validate_provenance → ②CollectionManager.write_with_provenance | provenance缺失→ProvenanceMissingError |
| `search()` | ①HybridRetriever.search() → ②失败→降级EmbeddingRouter直接检索 → ③再失败→ChromaDB query_texts | HybridRetriever异常→降级 |
| `health_check()` | ①list_collections → ②EmbeddingRouter.health_check → ③IndexHealthMonitor.check_all | 任一组件异常→status=unhealthy |

#### EmbeddingRouter（双嵌入路由）

```python
class EmbeddingRouter:
    def embed(self, text: str, collection_name: str) -> np.ndarray: ...
    def embed_batch(self, texts: list[str], collection_name: str) -> np.ndarray: ...
    def warmup(self) -> None: ...
    def health_check(self) -> dict[str, Any]: ...
    def shutdown(self) -> None: ...
```

| 方法 | 执行流程 | 关键决策点 |
|------|---------|-----------|
| `embed()` | ①collection∈BGE_M3_COLLECTIONS?→embed_bge_m3 : ②collection∈BGE_SMALL_COLLECTIONS?→embed_bge_small : ③raise KeyError | BGE-M3不可用→降级bge-small |
| `warmup()` | ①_load_bge_m3 → ②_load_bge_small → ③预热推理"hello world" → ④验证维度+无NaN | 双模型均不可用→fallback_mode=in_memory |

#### HybridRetriever（混合检索）

```python
class HybridRetriever:
    def search(self, query: str, collection_name: str, k: int = 5, timeout_ms: int = 2000) -> RetrievalTrace: ...
    def search_with_rerank(self, query: str, collection_name: str, k: int = 5, reranker: Any = None) -> RetrievalTrace: ...
    def invalidate_bm25(self, collection_name: str) -> None: ...
```

| 方法 | 执行流程 | 关键决策点 |
|------|---------|-----------|
| `search()` | ①dense_search(k*3) → ②sparse_search(k*3) → ③RRF融合(k=60) → ④time_decay → ⑤score_filter(≥0.6) → top-k | 超时→partial=True |
| `search_with_rerank()` | ①search(k*2) → ②reranker.predict(pairs) → ③重排序 → top-k | reranker异常→返回原始排序 |

#### ProvenanceEnforcer（写入溯源）

```python
class ProvenanceEnforcer:
    @staticmethod
    def validate(trace: WriteTrace) -> bool: ...
    @staticmethod
    def attach(metadata: dict[str, Any], provenance: dict[str, Any]) -> dict[str, Any]: ...
    @staticmethod
    def cbau_check(collection: str, operation: str, ai_session: Any = None) -> bool: ...
    @staticmethod
    def ai_autonomy_gate(collection: str, session_type: str) -> bool: ...
```

#### IndexHealthMonitor（索引健康）

```python
class IndexHealthMonitor:
    def check_all(self) -> HealthReport: ...
    def detect_drift(self) -> DriftReport: ...
    def check_ttl_expiry(self) -> list[TTLExpiryReport]: ...
    def auto_repair(self, collection_name: str) -> bool: ...
```

#### CollectionManager（Collection 生命周期）

```python
class CollectionManager:
    def create_collection(self, name: str, dim: int = 1024, chunk_strategy: str = "semantic", ttl_days: int = 0, ai_autonomy: str = "supervised", strict: bool = True) -> CollectionInfo: ...
    def get_collection(self, name: str) -> Any: ...
    def list_collections(self) -> list[CollectionInfo]: ...
    def migrate_collection(self, from_name: str, to_name: str) -> CollectionInfo: ...
    def archive_collection(self, name: str) -> None: ...
    def write_with_provenance(self, collection_name: str, content: str, metadata: dict[str, Any], doc_id: str | None = None) -> str: ...
    def init_all_collections(self) -> list[CollectionInfo]: ...
    def purge_expired(self) -> dict[str, int]: ...
```

#### VectorBridge（外部集成适配器）

```python
class VectorBridge:
    def search_for_ce(self, query: str, collections: list[str] | None = None, k: int = 5) -> list[dict[str, Any]]: ...
    def sync_knowledge(self, ke_id: str, content: str, metadata: dict[str, Any] | None = None) -> str: ...
    def sync_rules(self, rule_id: str, content: str) -> str: ...
    def write_decision(self, task_id: str, decision_text: str) -> str: ...
    def write_session_summary(self, session_id: str, summary: str) -> str: ...
    def audit_operation(self, operation: str, details: dict[str, Any]) -> None: ...
    def write_failure_pattern(self, pattern_text: str) -> str: ...
```

#### RetrievalFeedback（检索质量反馈）

```python
class RetrievalFeedback:
    def record(self, hit_id: str, was_useful: bool, task_id: str = "", collection: str = "") -> FeedbackEntry: ...
    def log_feedback(self, trace: Any, user_rating: float) -> None: ...
    def track_hit_rates(self) -> dict[str, float]: ...
    def sample_for_quality_monitor(self, sample_size: int = 10) -> list[FeedbackEntry]: ...
```

### §4.2 数据模型

```python
class Provenance(BaseModel):
    origin: str = ""
    audit_chain: list[str] = Field(default_factory=list)
    arbitration: str = ""

class ScoredHit(BaseModel):
    content: str = ""
    score: float = 0.0
    score_breakdown: dict[str, float] = Field(default_factory=dict)
    why_top: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)
    provenance: Provenance | None = None
    partial: bool = False

class RetrievalTrace(BaseModel):
    hits: list[ScoredHit] = Field(default_factory=list)
    collection: str = ""
    query: str = ""
    elapsed_ms: float = 0.0
    partial: bool = False
    why_top: str = ""

class WriteTrace(BaseModel):
    origin: str = ""
    audit_chain: list[str] = Field(default_factory=list)
    arbitration: str = ""
    content_hash: str = ""
    timestamp: str = ""

class CollectionInfo(BaseModel):
    name: str
    dimension: int = 0
    chunk_strategy: str = ""
    ttl_days: int = 0
    ai_autonomy_level: str = ""
    embedding_model: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)
    exists: bool = False

class HealthReport(BaseModel):
    status: str = "unknown"
    collections_healthy: int = 0
    collections_unhealthy: int = 0
    drift_detected: bool = False
    issues: list[str] = Field(default_factory=list)
    checked_at: str = ""

class DriftReport(BaseModel):
    drift_detected: bool = False
    extra_collections: list[str] = Field(default_factory=list)
    missing_collections: list[str] = Field(default_factory=list)
    detail: str = ""

class FeedbackEntry(BaseModel):
    collection: str
    query: str
    hit_count: int
    rating: float | None = None
    timestamp: str = ""
```

> ⚠️ 数据模型 SSoT 声明——每个模型 MUST 从 SSoT 文件导入。

| 模型名 | SSoT文件 | 其他定义位置 | 状态 |
|--------|---------|------------|------|
| Provenance | vms_schemas.py | — | ✅ |
| ScoredHit | vms_schemas.py | hybrid_retriever.py(import), sqlite_metadata_store.py(import) | ✅ 已统一 |
| RetrievalTrace | vms_schemas.py | hybrid_retriever.py(import) | ✅ 已统一 |
| CollectionHealthReport | vms_schemas.py | — | ✅ |
| SystemHealthReport | vms_schemas.py | index_health_monitor.py(import) | ✅ 已统一 |
| PositionalChunk | vms_schemas.py | — | ✅ |
| StrategyChunk | vms_schemas.py | chunk_strategy_router.py(import as Chunk) | ✅ 已统一 |
| WriteTrace | vms_schemas.py | — | ✅ |
| CollectionMetadata | vms_schemas.py | — | ✅ |
| FeedbackEntry | retrieval_feedback.py | — | ✅ |

### §4.3 输入契约

| 接口 | 输入字段 | 必填 | 约束 |
|------|---------|:---:|------|
| `write()` | `collection_name` | ✅ | MUST ∈ COLLECTION_NAMES |
| `write()` | `content` | ✅ | 非空字符串 |
| `write()` | `metadata` | ✅ | MUST 含 origin 或 provenance 字段 |
| `search()` | `collection_name` | ✅ | MUST ∈ COLLECTION_NAMES |
| `search()` | `query` | ✅ | 非空字符串 |
| `search()` | `k` | ❌ | 默认 5，1-100 |
| `create_collection()` | `name` | ✅ | MUST ∈ COLLECTION_NAMES |
| `create_collection()` | `dim` | ❌ | MUST ∈ {512, 1024} |
| `create_collection()` | `ai_autonomy` | ❌ | MUST ∈ {supervised, autonomous, human-gated} |

### §4.4 输出契约

| 接口 | 成功输出 | 失败输出 |
|------|---------|---------|
| `write()` | `str`（向量 ID） | `ProvenanceMissingError` / `DimensionError` / `KeyError` |
| `search()` | `list[dict]`（ScoredHit 列表） | `[]`（Collection 为空）/ `KeyError`（Collection 不存在） |
| `health_check()` | `dict`（含 status/embedding/collections/index_health） | — |
| `check_all()` | `HealthReport` | — |
| `detect_drift()` | `DriftReport` | — |

### §4.6 契约版本

| 契约部分 | 兼容性 | 说明 |
|---------|:---:|------|
| 新增 Collection | ✅ 向后兼容 | 不影响已有消费者 |
| 删除/重命名 Collection | ❌ 破坏性 | 需 Owner 审批 + 迁移方案 |
| 新增 ScoredHit 字段 | ✅ 向后兼容 | 不破坏已有逻辑 |
| search() 返回值结构变更 | ❌ 破坏性 | 需 Owner 审批 |
| 新增 Provenance 字段 | ✅ 向后兼容 | 不破坏已有逻辑 |

**变更通知**：破坏性变更→Owner审批+蓝图minor+1。兼容性变更→AI自主+patch+1。

### §4.5 MCP 接口

> VMS 通过 `src/zephyr/integration/mcp/vector_memory_server.py` 暴露 MCP Tool。

**Tools**：

| Tool | API | 输入 | 输出 |
|------|-----|------|------|
| `vms_search` | `InProcessVectorMemory.search()` | `{collection_name: str, query: str, k: int}` | `{hits: list[ScoredHit]}` |
| `vms_write` | `InProcessVectorMemory.write()` | `{collection_name: str, content: str, metadata: dict}` | `{id: str}` |
| `vms_health` | `InProcessVectorMemory.health_check()` | `{}` | `{status: dict}` |
| `vms_recall` | `InProcessVectorMemory.recall()` | `{collection_name: str, k: int}` | `{hits: list[dict]}` |

**错误码**：`PROVENANCE_MISSING(400)` — 缺少 provenance / `COLLECTION_NOT_FOUND(404)` — Collection 不存在 / `DIMENSION_ERROR(400)` — 维度不匹配

### §4.7 OCP 扩展点

| 扩展点 | 基类/接口 | 默认实现 | 扩展契约 | 注册方式 |
|--------|----------|---------|---------|---------|
| 嵌入后端 | EmbeddingRouter | SentenceTransformer (local) | MUST 实现 embed()->ndarray + warmup() + shutdown() | 构造函数 backend 参数 |
| Reranker | HybridRetriever.search_with_rerank | None（无 reranker） | MUST 实现 predict(pairs)->scores | search_with_rerank() 参数注入 |
| 降级后端 | InMemoryMemoryBackend | 零向量返回 | MUST 实现 write()/search()/health_check() | InProcessVectorMemory 构造 |

---

## §5 约束条件

### §5.1 技术约束

| # | 约束 | 值 |
|---|------|-----|
| 1 | Python 版本 | ≥ 3.12 |
| 2 | 向量数据库 | ChromaDB 0.6 |
| 3 | 主嵌入模型 | BGE-M3 ONNX 1024d |
| 4 | 轻量嵌入模型 | bge-small-zh-v1.5 512d |
| 5 | 推理方式 | ONNX Runtime / Ollama HTTP API |
| 6 | 批量大小 | 16（1024d）/ 32（512d） |
| 7 | 距离度量 | cosine |
| 8 | 混合检索 | Vector(HNSW) + BM25 + RRF融合(k=60) |
| 9 | 配置入口 | vms_config.yaml（禁止硬编码） |
| 10 | ChromaDB 遥测 | MUST 禁用（CHROMA_TELEMETRY_IMPL=none） |

### §5.2 容量估算

| 维度 | 当前规模 | 峰值需求 | 系统极限 | 是否够用 | 扩展方案 |
|------|:------:|:------:|:------:|:------:|---------|
| 向量总数 | ~5,000 | 50,000 | 100,000 | ✅ | FAISS HNSW/IVF+PQ 迁移 |
| 存储空间 | ~200MB | 2GB | 10GB | ✅ | 量化压缩（Scalar Quantization int8） |
| GPU VRAM 总占用 | ~4GB | ~4GB | ~4GB(RTX 3090) | ⚠️ | ChromaDB索引~4GB；BGE-M3模型VRAM已归MOD-INF-039；GPU排队策略(单卡RTX 3090约束，优先级RT最高) |
| 嵌入模型内存 | ~800MB(CPU) | ~2GB | ~2GB | ⚠️ | 按需加载+降级策略 |
| 检索延迟 p95 | ~50ms | 100ms | 200ms | ✅ | 并行检索+结果缓存 |
| 写入延迟 p95 | ~100ms | 200ms | 500ms | ✅ | 批量嵌入+异步队列 |

### §5.3 迁移/废弃方案

> [时态:临时] 迁移完成后删除本节。当前状态：3/7已完成，3/7部分完成，1/7未完成。

| # | 废弃/迁移对象 | 当前位置 | 目标位置 | 处理方式 | 引用更新方案 | 迁移状态 |
|---|-------------|---------|---------|---------|------------|:-------:|
| 1 | kb/chromadb_init.py | `src/zephyr/kb/` | 冻结（deprecated） | 标记 deprecated，不再新增写入 | BridgeLayer 双读过渡 | ✅已完成 |
| 2 | kb/unified_memory_api.py | `src/zephyr/kb/` | 冻结（deprecated） | 功能已指向VMS(prefer_vms=True)，缺显式deprecated标记 | VMS write() 替代 | ⚠️部分完成 |
| 3 | ke_entries Collection | kb/ 旧 Collection | VMS knowledge | BridgeLayer.migrate_collection | CE 检索指向 VMS | ⚠️部分完成(CE间接用VMS) |
| 4 | vibe_rules Collection | kb/ 旧 Collection | VMS rules | BridgeLayer.migrate_collection | CE 检索指向 VMS | ⚠️部分完成 |
| 5 | failure_patterns Collection | kb/ 旧 Collection | VMS lessons | BridgeLayer.migrate_collection | FLE 写入指向 VMS | ❌未完成(FLE未接入VMS) |
| 6 | blueprints Collection | kb/ 旧 Collection | VMS blueprints | BridgeLayer.migrate_collection | CE 检索指向 VMS | ⚠️部分完成 |
| 7 | unified_memory Collection | kb/ 单 Collection | 按 topic 拆分到多个 VMS Collection | 拆分脚本 dry-run→Owner审核→执行 | 全项目 Grep 更新引用 | ✅已完成(VMS侧) |

### §5.4 非功能需求与服务水平

| 维度 | NFR指标 | NFR目标 | 测量方式 | SLI | SLO | Error Budget | 告警阈值 |
|------|--------|--------|---------|-----|-----|-------------|---------|
| 可用性 | 检索可用率 | 99.9% | health_check() | search() 成功率 | 99.9% | 每月允许失败 43min | 连续3次失败→P1 |
| 性能-检索 | 延迟 p99 | <200ms | HybridRetriever.elapsed_ms | search() 延迟 | p99<200ms | — | p99>200ms→P2 |
| 性能-写入 | 延迟 p95 | <100ms | write() 计时 | write() 延迟 | p95<100ms | — | p95>100ms→P2 |
| 检索质量 | 召回率 | >90% | benchmark 测试集 | recall@5 | ≥0.9 | — | recall@5<0.8→P1 |
| 可维护性 | MTTR | <30min | 故障记录 | — | — | — | — |

**知识检索三角**：KB查询(MOD-KB-001) → 向量化检索(MOD-INF-011 BGE-M3+ChromaDB) → 上下文装配(MOD-CONTEXT_ENGINE 五级预算) → 注入Agent。SSoT：向量索引 = MOD-INF-011。

### §5.5 自动化触发机制

| 操作 | 触发方式 | 调度策略 | 当前状态 |
|------|---------|---------|---------|
| VMS启动 | auto_boot | AutoRuntimeCore.boot() → VMS.start() | ✅已实现 |
| 8 Collection初始化 | auto_boot | VMS.start() → init_all_collections() | ✅已实现 |
| 嵌入模型warmup | auto_boot | VMS.start() → EmbeddingRouter.warmup() | ✅已实现 |
| 启动时健康检查 | auto_boot | VMS.start() → check_all() | ✅已实现 |
| 启动时漂移检测 | auto_boot | VMS.start() → detect_drift() | ✅已实现 |
| 语义检索 | auto_event | CE/MCP查询触发 | ✅已实现 |
| 写入(决策/知识/规则/会话/审计) | auto_event | 各系统写入时触发 | ✅已实现 |
| TTL过期清理 | auto_scheduled | _maintenance_loop()每24h调用CollectionManager.purge_expired() | ✅已实现 |
| 定时健康检查 | auto_scheduled | _maintenance_loop()每60s调用IndexHealthMonitor.check_all() | ✅已实现 |
| 定时漂移检测 | auto_scheduled | check_all()含drift检测(非独立定时) | ⚠️部分实现 |
| 自动修复 | auto_event | _maintenance_loop()中check_all()检测unhealthy时触发auto_repair() | ✅已实现 |
| 检索缓存 | auto_event | search()/write()时CacheLayer自动缓存 | ✅已实现 |
| 检索反馈收集 | auto_event | start()中注入RetrievalFeedback | ✅已实现 |
| 模型版本变更清缓存 | auto_event | CacheLayer.invalidate_all_on_model_change() | ⚠️部分实现(方法存在但未自动触发) |

### §5.7 禁止模式与导入约束

| # | 类型 | 禁止项 | 替代/允许项 | 原因 |
|---|:----:|--------|-----------|------|
| 1 | 编码模式 | 同一 Collection 内混用维度 | Collection 创建时锁定维度 | 检索不可比 |
| 2 | 编码模式 | 跳过 WriteTrace 直接写入 | MUST 通过 write() → ProvenanceEnforcer | 审计链断裂 |
| 3 | 编码模式 | AI 擅自变更 Collection Schema | 须经 Owner 审批 + 更新蓝图 §2 | 治理失控 |
| 4 | 编码模式 | 硬编码配置 | vms_config.yaml | 配置漂移 |
| 5 | 编码模式 | ChromaDB 遥测开启 | MUST 禁用 | 隐私合规 |
| 6 | 导入源 | zephyr.vector_memory 导入 zephyr.kb.* | 通过 BridgeLayer 间接访问 | 分层约束 |

---

## §6 错误处理

| # | 异常场景 | 检测方式 | 恢复策略 | 影响范围 |
|---|---------|---------|---------|---------|
| 1 | Provenance 缺失 | ProvenanceEnforcer.validate() | 抛出 ProvenanceMissingError，拒绝写入 | 写入方 |
| 2 | 嵌入维度不匹配 | DesignPrinciplesEnforcer.validate_dimension() | 抛出 DimensionError | Collection 创建 |
| 3 | 分块策略违规 | DesignPrinciplesEnforcer.validate_chunk_strategy() | 抛出 HotColdSeparationError | Collection 创建 |
| 4 | TTL 违规 | DesignPrinciplesEnforcer.validate_ttl() | 抛出 TTLError | Collection 创建 |
| 5 | BGE-M3 加载失败 | EmbeddingRouter.warmup() | 降级为 bge-small | 所有 1024d Collection |
| 6 | 双模型均不可用 | EmbeddingRouter.warmup() | 降级为 InMemory（零向量） | 全部检索 |
| 7 | ChromaDB SQLite 锁冲突 | write() 异常 | 重试 3 次 + 指数退避 | 写入操作 |
| 8 | 混合检索超时 | HybridRetriever timeout_ms | 返回 partial=True + 当前最佳结果 | 检索操作 |
| 9 | 蓝图漂移 | IndexHealthMonitor.detect_drift() | 告警 + 写入 drift 登记 | 全系统 |
| 10 | 索引损坏 | IndexHealthMonitor.check_all() | auto_repair()（R4 由 ChromaDB SQLite ACID+WAL 防断电） | 受损 Collection |

**异常层级**：`VMSError` → `DesignPrincipleError`（子类: `DimensionError`, `ChunkStrategyError`, `TTLError`, `HotColdSeparationError`）/ `ProvenanceMissingError`

### §6.1 可观测性

| 指标名 | 类型 | 采集方式 | 告警阈值 | 告警级别 |
|--------|------|---------|---------|---------|
| vms_search_latency_ms | Histogram | HybridRetriever.elapsed_ms | p99>200ms | P2 |
| vms_write_latency_ms | Histogram | write() 计时 | p95>100ms | P2 |
| vms_embedding_available | Gauge | EmbeddingRouter.health_check() | 双模型均不可用 | P1 |
| vms_drift_detected | Gauge | IndexHealthMonitor.detect_drift() | drift_detected=True | P1 |
| vms_collection_count | Gauge | list_collections() | 与蓝图不一致 | P2 |
| vms_ttl_expired_count | Gauge | check_ttl_expiry() | 过期未清理>0 | P2 |
| vms_gpu_available | Gauge | GPU设备检测（待施工） | GPU不可用 | P1 |
| vms_gpu_vram_bytes | Gauge | VRAM使用量（待施工） | VRAM<4GB | P1 |

### §6.2 退化矩阵

| 组件 | 失败后可用功能 | 不可用功能 | 降级策略 | 恢复条件 |
|------|-------------|-----------|---------|---------|
| BGE-M3 | bge-small 512d 检索 | 1024d 精确检索 | 降级为 bge-small | BGE-M3 恢复可用 |
| 双嵌入模型 | InMemory 零向量检索 | 语义检索 | 零向量返回 + degraded=True | 任一模型恢复 |
| ChromaDB | — | 全部读写 | 启动失败，VMS 不可用 | ChromaDB 恢复 |
| HybridRetriever | 原始 ChromaDB query | 混合检索+RRF | 降级为纯向量检索 | HybridRetriever 恢复 |
| IndexHealthMonitor | VMS 正常读写 | 健康检查+漂移检测 | 跳过健康检查 | Monitor 恢复 |

**退化级别**：L0 正常 → L1 降 k 值 → L2 仅 bge-small → L3 仅 InMemory

**CPU fallback 路径**：GPU 不可用时，嵌入推理降级到 CPU（ONNX Runtime CPU provider），延迟增加 5-10x 但功能完整。

### §6.3 业务连续性

| 维度 | 目标 | 当前实现 | 缺口 |
|------|------|---------|------|
| RTO | 30s | InProcessVectorMemory.start() 冷启动 ~10s | ✅ 满足 |
| RPO | 1min | ChromaDB PersistentClient 实时持久化 | ✅ 满足 |
| SPOF | RTX 3090 | GPU 故障→CPU fallback | ✅ 有降级路径 |
| 降级策略 | CPU fallback + 本地模型降级 | §6.2 退化矩阵 L0→L3 | ✅ 已定义 |

### §6.4 级联失效

| 失效源 | 失效模式 | 影响范围 | 降级策略 |
|--------|---------|---------|---------|
| ChromaDB QPS 爆 | 写入/检索延迟飙升 | 全部 VMS 读写降质 | 写入队列 + 限流 + 降级为只读 |
| GPU VRAM 不足 | 嵌入推理 OOM | 1024d Collection 不可用 | 降级为 bge-small 512d + CPU fallback |
| ChromaDB 数据损坏 | 索引不一致 | 受损 Collection 不可检索 | auto_repair()（R4 由 ChromaDB SQLite ACID+WAL 防断电） |

---

## §8 安全考量

| # | 威胁 | 影响 | 缓解措施 | 验证方式 |
|---|------|------|---------|---------|
| 1 | PII/敏感信息写入向量索引（V-VMS-420） | 高 | 写入前 input_sanitizer 扫描 secrets patterns | 扫描器单元测试 |
| 2 | AI 越权操作 Collection（R10） | 致命 | CBAC 与 Collection 操作绑定——human-gated 规则不可 AI 修改 | ProvenanceEnforcer.cbau_check() |
| 3 | ChromaDB Telemetry 隐私泄露（V-VMS-503） | 中 | 启动时显式禁用 + 网络层面验证无外连 | 环境变量检查 |
| 4 | 对抗性检索投毒（F5） | 致命 | 写入时检测异常接近向量(similarity>0.99)→标记 suspicious + 来源交叉验证 | 投毒检测单元测试 |
| 5 | 敏感数据泄露到向量索引（R12） | 致命 | 写入前 input_sanitizer 扫描 + rules/knowledge 人类审查后才能写入 | 扫描器+审查流程 |

---

## §9 测试策略

| # | 测试类型 | 覆盖范围 | 关键测试用例 | 通过标准 |
|---|---------|---------|------------|---------|
| 1 | 单元测试 | InProcessVectorMemory/EmbeddingRouter/HybridRetriever/ProvenanceEnforcer/IndexHealthMonitor/CollectionManager | `tests/vector_memory/test_vector_memory.py` | 覆盖率 > 80% |
| 2 | 集成测试 | VMS→CE 检索链路 | CE build 阶段成功检索 KE 条目 | 端到端通过 |
| 3 | 测试替身 | InMemoryFakeVMS（in_memory_fake_vms.py） | 消费方（CE/Orc/FLE）单元测试独立于 VMS 状态 | InMemoryFakeVMS 接口与 InProcessVectorMemory 一致 |
| 4 | 确定性嵌入 | DeterministicEmbedder（基于 content_hash 生成固定伪向量） | 测试环境下嵌入结果稳定可复现 | 相同输入→相同向量 |
| 5 | 语义搜索 CI | 30-50 条基准查询+标准答案 | recall@5 ≥ 0.8 | CI 每次 PR/变更运行 |

---

## §10 依赖关系

### 10.1 依赖声明

| 依赖模块 | 依赖类型 | 依赖内容 | 版本要求 | 蓝图路径 |
|---------|---------|---------|---------|---------|
| MOD-MASTER_BLUEPRINT | 必须 | CT-CE-VMS-001 集成契约 | — | `D:\ZephyrAlpha\docs\03_modules\_system_master\blueprint.md` |
| MOD-KB-001 | 可选 | 知识库——beta VMS整合目标 | — | `D:\ZephyrAlpha\docs\03_modules\_domain_knowledge\knowledge_base\blueprint.md` |
| MOD-CONTEXT_ENGINE | 必须 | CE——VMS的主要消费方 | — | `D:\ZephyrAlpha\docs\03_modules\_domain_knowledge\context_engine\blueprint.md` |
| MOD-INF-039 | 必须 | 本地模型推理——嵌入路由/缓存/Ollama/调度 | — | `D:\ZephyrAlpha\docs\03_modules\_domain_knowledge\local-model\blueprint.md` |
| MOD-FEEDBACK_LOOP | 可选 | FLE 消费检索反馈 | — | `D:\ZephyrAlpha\docs\03_modules\_domain_knowledge\feedback_loop\blueprint.md` |
| D_FACTOR-Alpha因子层 | 可选 | C轨域：因子语义检索 | — | `D:\ZephyrAlpha\docs\03_modules\l02_factor\blueprint.md` |
| D_ML_TRAIN-ML平台层 | 可选 | C轨域：模型语义检索 | — | `D:\ZephyrAlpha\docs\03_modules\_domain_machine_learning_train\blueprint.md` |
| KBG-0016 | 必须 | VMS生产级嵌入与分块契约 | — | `D:\ZephyrAlpha\docs\02_enterprise_architecture\adr\adr-0016-vms-embedding-contract.md` |
| KBG-0031 | 必须 | Phase 2 ChromaDB基线选型 | — | `D:\ZephyrAlpha\docs\02_enterprise_architecture\adr\adr-0031-chromadb-vector-retrieval.md` |
| MOD-INF-039 | 必须 | 嵌入服务——EmbeddingRouter/CacheLayer/OllamaEmbedding已迁移至local_model | — | `D:\ZephyrAlpha\docs\03_modules\_domain_knowledge\local-model\blueprint.md` |

### 10.2 依赖图对齐声明

| # | 对齐项 | 对齐方式 | 对齐状态 | 验证命令 |
|---|--------|---------|:-------:|---------|
| 1 | §10.1 依赖声明 ↔ cross-module-dependency-registry.yaml | 蓝图声明的每个依赖在 registry 中有对应条目 | 已对齐 | `python scripts/governance/d5_architecture/validators/validate_path_alignment.py --blueprint MOD-INF-011` |
| 2 | §11 产出物路径 ↔ 依赖图 path_mappings | 路径一致 | 已对齐 | 同上 |
| 3 | §0.1 代码文件清单 ↔ 依赖图节点 code_path | 节点存在 | 已对齐 | `python scripts/governance/d5_architecture/validators/validate_dependency_graph_template.py` |

### 10.3 内部依赖图

#### 执行顺序依赖

| 上游脚本 | 下游脚本 | 依赖内容 | 验证方式 |
|---------|---------|---------|---------|
| collection_manager.py | in_process_vector_memory.py | CollectionManager 是 VMS 入口的前置 | import 成功 |
| embedding_router.py | hybrid_retriever.py | EmbeddingRouter 是 HybridRetriever 的前置 | import 成功 |
| migrate_chroma_to_faiss.py | faiss_collection_manager.py | 迁移脚本依赖 FAISS 管理器 | import 成功 |

#### 数据流依赖

| 生产者 | 消费者 | 数据类型 | 传输方式 |
|--------|--------|---------|---------|
| EmbeddingRouter | HybridRetriever | 嵌入向量 ndarray | 函数调用 |
| ProvenanceEnforcer | InProcessVectorMemory | WriteTrace 校验结果 | 函数调用 |
| IndexHealthMonitor | InProcessVectorMemory | HealthReport | 函数调用 |
| BridgeLayer | InProcessVectorMemory | kb/ 旧 Collection 数据 | 函数调用 |
| RetrievalFeedback | HybridRetriever | 检索质量信号 | 函数调用 |
| VectorBridge | Context Engine | 检索结果 ScoredHit | 函数调用 |
| VectorBridge | Audit Trail (线3) | 嵌入结果 | 函数调用 |
| VectorBridge | Alpha因子层 (D_FACTOR) | 因子语义检索结果 | 函数调用 |
| VectorBridge | ML平台层 (D_ML_TRAIN) | 模型语义检索结果 | 函数调用 |

### 10.4 自动化规格

| # | 自动化项 | 是否需要 | 理由 | 实现方式 | 现有工具 | 缺口 | 触发方式 | 触发条件 |
|---|---------|:-------:|------|---------|---------|------|---------|---------|
| 1 | 依赖图自动生成 | 是 | 388 脚本需自动追踪 | AST解析import + manifest字段 | — | 不覆盖scripts/目录 | CI | 文件变更时 |
| 2 | 依赖对齐自动验证 | 是 | 防漂移 | CI门禁 | validate_path_alignment.py | 无 | CI门禁 | PR提交时 |
| 3 | 临时时态内容自动清理 | 是 | 零残留 | 压缩工作流脚本 | — | 需新建 | 手动 | 压缩工作流执行时 |
| 4 | 施工步骤完成度自动检测 | 是 | 防止跳步 | pytest+mypy+ruff | — | 无 | CI pipeline | 代码提交时 |

### 10.5 概念重叠声明

| # | 重叠概念 | 重叠维度 | 对方模块 | 委托关系 | 处置状态 |
|---|---------|---------|---------|---------|---------|
| 1 | 向量存储与检索 | 存储层+嵌入+检索 | MOD-KB-001 | KB 委托本模块——KB 过渡期保留 4 旧 Collection，迁移完成后向量能力全部归 VMS | 迁移中(3/7完成) |
| 2 | 混合检索(BM25+RRF) | 检索逻辑 | MOD-KB-001 | KB 委托本模块——KB reranker.py 为过渡期兼容层 | 待废弃 |
| 3 | 语义缓存 | ChromaDB 复用 | MOD-RESOURCE_OPTIMIZATION_ENGINE | 本模块提供基础设施，容量保证模块复用 | 已协调 |
| 4 | 嵌入版本追踪 | 版本锁定 | MOD-CONTEXT_ENGINE | CE 追踪注入上下文的嵌入版本，VMS 拥有嵌入执行 | 已协调 |

### 10.6 依赖链风险评级

| # | 依赖链 | 链深度 | 风险等级 | 熔断机制 | 处置状态 |
|---|--------|:-----:|---------|---------|---------|
| 1 | VMS→ChromaDB→SQLite | 2 | L1 | ChromaDB 不可用→InMemoryBackend 降级 | 已有熔断 |
| 2 | VMS→BGE-M3→ONNX Runtime | 2 | L1 | BGE-M3 不可用→bge-small 降级 | 已有熔断 |
| 3 | CE→VMS→ChromaDB | 3 | L2 | VMS 降级→CE 检索结果为空但不崩溃 | 需 CE 侧降级策略 |
| 4 | KB→VMS→ChromaDB(迁移期) | 3 | L2 | BridgeLayer 双读→VMS 不可用时回退 kb/ | 已有降级 |

---

## §11 产出物存放目录

| 产出物类型 | 存放完整绝对路径 | 说明 |
|----------|---------------|------|
| 蓝图文件 | `D:\ZephyrAlpha\docs\03_modules\_domain_knowledge\vector_memory\blueprint.md` | 本文件 |
| 业务代码 | `D:\ZephyrAlpha\src\zephyr\integration\vector_memory\` | VMS 源码（25 个 .py + 1 个 .yaml） |
| 过渡期代码 | `D:\ZephyrAlpha\src\zephyr\kb\chromadb_init.py` + `unified_memory_api.py` | 现有实现——Phase 2 后冻结 |
| 测试代码 | `D:\ZephyrAlpha\tests\unit\vector_memory\` | 单元测试 |
| ChromaDB 数据 | `D:\ZephyrAlpha\data\vector_db\` | ChromaDB 持久化目录 |
| 嵌入模型缓存 | `D:\ZephyrAlpha\models\bge-m3\` | BGE-M3 ONNX 模型文件 |
| 轻量模型缓存 | `D:\ZephyrAlpha\models\bge-small-zh-v1.5\` | 512d 轻量嵌入模型 |
| 嵌入缓存 | `D:\ZephyrAlpha\data\vector_db\_embedding_cache\` | Embedding memoization 持久化 |

---

## §12 集成目标

| 集成目标系统 | 集成方式 | 集成点 | 验证方法 |
|------------|---------|--------|---------|
| Context Engine (MOD-CONTEXT_ENGINE) | CE→VMS 向量检索 | `context_assembler.py` → `InProcessVectorMemory.search()` | CE build 阶段成功检索 KE 条目 |
| Knowledge Base (MOD-KB-001) | KB→VMS 写入 | KE 入库时同步写入 `knowledge` Collection | KE 入库后 VMS 可检索 |
| Feedback Loop (MOD-FEEDBACK_LOOP) | FLE→VMS 双向 | 失败模式写入 `lessons`；检索质量反馈读出 | FLE detect 后 VMS 可检索失败模式 |
| Orchestrator (MOD-TASK_SYSTEM) | Orc→VMS 写入 | 任务决策写入 `decisions` | Orc 完成 task 后 VMS 可检索决策 |
| SessionManager | Session→VMS 写入 | session 结束时压缩摘要写入 `session_snapshots` | 新 session 冷启动检索到上一 session |
| Audit Trail (MOD-INF-020) | VMS→线3审计追踪链 | 嵌入结果输出到审计追踪链 + 每次 VMS 读写写入审计日志 | 审计日志包含 VMS 操作记录 + WriteTrace + 嵌入结果 |
| Alpha因子层 (D_FACTOR) | VMS→D_FACTOR 因子语义检索 | 因子IC/衰减/退役等语义检索 | 因子检索结果可被Alpha策略消费 |
| ML平台层 (D_ML_TRAIN) | VMS→D_ML_TRAIN 模型语义检索 | 模型性能/回测结果等语义检索 | 模型检索结果可被ML实验平台消费 |

---

## §13 需要更新的相关内容

| # | 需更新的文件 | 完整绝对路径 | 更新内容 | 更新原因 |
|---|------------|------------|---------|---------|
| 1 | 蓝图注册表 | `D:\ZephyrAlpha\docs\03_modules\blueprint_registry.yaml` | 版本号 0.9.0 + P0 | 蓝图 status → active |
| 2 | 模块 ID 注册表 | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture_model\module_id_registry.yaml` | VMS 模块状态 active | 蓝图已定稿 |
| 3 | CE 蓝图依赖 | `D:\ZephyrAlpha\docs\03_modules\_domain_knowledge\context_engine\blueprint.md` | CT-CE-VMS-001 集成状态 active | VMS 接口已定义 |
| 4 | b_vector_memory.yaml SSoT | `D:\ZephyrAlpha\architecture_model\layers\b_vector_memory.yaml` | 8 Collection + 双嵌入维度 + Phase 0-4 | SSoT 反向同步 |
| 5 | KBG-0031 状态 | `D:\ZephyrAlpha\docs\02_enterprise_architecture\adr\adr-0031-chromadb-vector-retrieval.md` | 添加"已通向 VMS v0.9.0 8 Collection"注释 | 避免 KB 决策记录 与蓝图不一致 |
| 6 | Tech Stack | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture_model\technology\vibe_coding_infrastructure_tech_stack.yaml` | TECH-04/TECH-05 更新双嵌入维度 | 新增 bge-small-zh-v1.5 轻量路径 |

---

## §14 已知风险与缓解

| # | 风险/负面后果 | 概率 | 影响 | 缓解策略 | 类型 |
|---|-------------|------|------|---------|------|
| R0 | 蓝图漂移——蓝图声称的 Collection 与磁盘实际不一致 | 高 | 🔴 致命 | IndexHealthMonitor.detect_drift()：比对蓝图 §2 与 client.list_collections() | 风险 |
| R1 | ChromaDB 单进程写入瓶颈——多 IDE 并发写入冲突 | 中 | 高 | ChromaDB WAL mode + 写入队列 + 写入幂等 | 风险 |
| R2 | BGE-M3 ONNX 模型加载慢——首次启动延迟 > 10s | 高 | 中 | 模型预热 + 懒加载 + 512d 快速路径先行 + CacheLayer | 风险 |
| R3 | 向量检索质量不足——BGE-M3 对中文领域术语理解有限 | 中 | 高 | 混合检索 + RRF 融合 + Phase 3 reranker + 嵌入模型版本追踪 | 风险 |
| R4 | ChromaDB 数据损坏——断电导致向量索引不一致 | 低 | 🔴 致命 | ChromaDB SQLite ACID+WAL 防断电 + auto_repair() 尝试修复（snapshot 备份已删除——R4 被 ACID+WAL 覆盖，零消费方，30GB递归bug根因） | 风险 |
| R5 | 8 Collection 数据量膨胀——长期运行后检索变慢 | 中 | 中 | TTL 机制 + 热冷数据分离 + Auto-compaction | 风险 |
| R6 | 嵌入模型升级后新旧向量混合 | 低 | 高 | 每个向量记录 embedding_model_version；升级时全量重嵌入 | 风险 |
| R7 | 嵌入缓存不一致——CacheLayer 返回过期 embedding | 低 | 中 | content fingerprint(sha256) 为缓存 key；模型版本变更→自动 invalidate | 风险 |
| R8 | 冷数据未被 TTL 清理——HealthMonitor 异常 | 中 | 中 | HealthMonitor cron 每日检查 TTL 过期记录数；过期未清理→告警 | 风险 |
| R9 | 检索结果无 trace——AI 无法判断可信度 | 低 | 高 | 每次检索返回 RetrievalTrace（含 score_breakdown + why_top） | 风险 |
| R10 | AI 越权操作 Collection——未经授权删除/修改核心 Collection | 中 | 🔴 致命 | AI 自治级别绑定到 Collection + CBAC 校验 | 风险 |
| R11 | 多 IDE 各持 ChromaDB client——SQLite 文件锁冲突 | 中 | 高 | 统一通过 InProcessVectorMemory 单例访问 | 风险 |
| R12 | 敏感数据泄露到向量索引中 | 低 | 🔴 致命 | 写入前 input_sanitizer 扫描 + rules/knowledge 人类审查 | 风险 |
| R13 | Collection 数量失控膨胀 | 中 | 中 | 新增 Collection 须经 Owner 审批 + 更新蓝图 §2 | 风险 |
| R14 | 迁移期间数据不一致 | 高 | 高 | BridgeLayer 双读阶段；迁移完成后 kb/ 标记 deprecated | 风险 |
| NC1 | ChromaDB + BGE-M3 + bge-small 三依赖——部署复杂度增加 | 高 | 中 | 统一安装脚本 + vms_config.yaml 校验 | 负面后果 |
| NC2 | 向量检索不确定性——语义相似 ≠ 语义相同 | 中 | 中 | 混合检索 + RRF 缓解 | 负面后果 |
| NC3 | 双模型增加资源占用（~2GB+300MB） | 高 | 中 | 按需加载 + 降级策略 | 负面后果 |

---

## §16 施工指引

### ⚠️ AI 施工前检查清单

| # | 检查项 | 确认方式 | 状态 |
|---|--------|---------|:----:|
| 1 | 已读取本蓝图全部内容 | 逐节确认 | ☐ |
| 2 | 已读取必备链接中所有真源文件 | 逐个打开确认 | ☐ |
| 3 | §0 代码对齐验证已填写且与实际代码一致 | 逐项核对 | ☐ |
| 4 | 每个施工步骤都对应明确的蓝图接口契约（§4） | 逐步骤追溯 | ☐ |

### 16.1 施工策略

| 项目 | 内容 |
|------|------|
| 施工阶段数 | 4 个 Phase（Phase 0-3 已完成） |
| 施工模式 | 继承+新建——继承 kb/ 现有能力，在 VMS 中扩展 |
| 核心风险 | ChromaDB 与 BGE-M3 双模型集成兼容性 / 迁移期间数据一致性 |
| 目标 generation | 1 — 基线版本 |

### 16.2 前置条件

| # | 依赖项 | 依赖类型 | 当前状态 | 是否满足 |
|---|--------|---------|:---:|:---:|
| 1 | ChromaDB 安装 | hard | ✅ (kb/ 已在使用) | ✅ |
| 2 | bge-small-zh-v1.5 模型已下载 | hard | ✅ (kb/ 已在使用) | ✅ |
| 3 | BGE-M3 ONNX 模型下载 | hard | ✅ | ✅ |
| 4 | CE 蓝图 §2.1 Build 阶段已定义 | soft | ✅ | ✅ |
| 5 | unified_memory_api.py WriteTrace 契约理解 | soft | ✅ (代码已具备) | ✅ |

### 16.3 实施步骤

#### Phase 1：基础设施对齐（✅ 已完成）

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4 ProvenanceEnforcer / EmbeddingRouter / ChunkStrategyRouter / IndexHealthMonitor / CacheLayer / BridgeLayer |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\integration\vector_memory\` 下 6 个模块文件 |
| 验收标准 | ProvenanceEnforcer 可校验 WriteTrace；EmbeddingRouter 可按 Collection 路由；BridgeLayer 可双读 |

**创建文件清单**：

| 文件名 | 核心内容 | 必须包含 |
|--------|---------|---------|
| provenance_enforcer.py | WriteTrace 校验 + CBAC 校验 + AI 自治门控 | validate()/attach()/cbau_check()/ai_autonomy_gate() |
| embedding_router.py | 双模型路由 BGE-M3/bge-small + warmup + 降级——已迁移至MOD-INF-039 | embed()/embed_batch()/warmup()/health_check() |
| chunk_strategy_router.py | 8 种分块策略路由 | route()/validate_strategy() |
| index_health_monitor.py | 自检+自动修复+漂移检测 | check_all()/detect_drift()/auto_repair() |
| cache_layer.py | Embedding memoization + 模型版本变更清缓存——已迁移至MOD-INF-039 | put()/get()/invalidate_collection()/invalidate_all_on_model_change() |
| bridge_layer.py | kb/ ↔ VMS 双向桥接 | migrate_collection()/双读逻辑 |

#### Phase 2：8 Collection 落地（✅ 已完成）

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §2 八大 Collection + §5.3 迁移映射 |
| 产出位置 | `in_process_vector_memory.py`（InProcessVectorMemory 统一入口） |
| 验收标准 | 8 个 Collection 可创建/写入/检索/删除；迁移 4 旧 Collection 数据无损 |
| 迁移顺序 | 1.先建 rules/blueprints/knowledge/lessons——从现有Collection迁移数据 2.再建 decisions/code_context/session_snapshots/execution_traces——全新创建 3.BridgeLayer双读期间保持兼容 4.迁移完成后冻结kb/chromadb_init.py |

**创建文件清单**：

| 文件名 | 核心内容 | 必须包含 |
|--------|---------|---------|
| in_process_vector_memory.py | 8 Collection 统一入口 + _maintenance_loop | start()/shutdown()/write()/search()/recall()/health_check() |
| collection_manager.py | 8 Collection 生命周期管理 | create_collection()/write_with_provenance()/purge_expired() |
| vms_schemas.py | Pydantic V2 数据模型 SSoT | Provenance/ScoredHit/RetrievalTrace/WriteTrace/CollectionInfo/HealthReport |
| collection_schemas.py | 8 Collection Schema 定义 | COLLECTION_NAMES/COLLECTION_SCHEMAS/BGE_M3_COLLECTIONS/BGE_SMALL_COLLECTIONS |
| interface.py | VMS 接口基类 | VectorMemoryBase/MemoryEntry/EmbeddingEngineBase |
| delegated_vector_memory.py | RI-02 落地适配器 | VectorMemoryBase→UnifiedMemoryAPI 映射 |
| vms_errors.py | 异常层级 SSoT | VMSError/DesignPrincipleError/ProvenanceMissingError/DimensionError |
| design_principles.py | 设计原则校验 SSoT | validate_dimension()/validate_provenance()/validate_chunk_strategy()/validate_ttl() |
| vms_config.yaml | VMS 环境配置 Schema | persist_dir/model_dir/telemetry/batch_size |

#### Phase 3：检索质量闭环（✅ 已完成）

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §3.2 混合检索 + §12 FLE集成 |
| 产出位置 | `hybrid_retriever.py` / `retrieval_feedback.py` / `cross_collection_retriever.py` |
| 验收标准 | 混合检索 top-5 精度 > 纯向量 top-5；FLE 可记录检索反馈 |

**创建文件清单**：

| 文件名 | 核心内容 | 必须包含 |
|--------|---------|---------|
| hybrid_retriever.py | Vector+BM25+RRF 混合检索 + time_decay | search()/search_with_rerank()/invalidate_bm25() |
| bm25_index.py | BM25 稀疏检索索引 | tokenize()/index()/search() |
| retrieval_feedback.py | FLE 检索质量反馈闭环 | record()/log_feedback()/track_hit_rates()/sample_for_quality_monitor() |
| cross_collection_retriever.py | 跨 Collection 联合检索 | search_across() |

**Phase 3 额外文件**（v0.7.1 补入）：

| 文件名 | 核心内容 |
|--------|---------|
| in_memory_memory_backend.py | 降级兜底（零向量），VMS 完全不可用时最后防线 |
| in_memory_fake_vms.py | InMemoryFakeVMS 测试替身，消费方单元测试隔离 |
| faiss_collection_manager.py | FAISS HNSW/IVF+PQ 8 Collection 管理（替代 ChromaDB） |
| sqlite_metadata_store.py | SQLite WAL+FTS5 BM25 元数据持久化+全文检索 |
| ollama_embedding.py | Ollama 嵌入生成（BGE-M3 via Ollama HTTP API）——已迁移至MOD-INF-039 |
| ollama_chat.py | Ollama 本地 LLM 推理（query_rewrite/tag_completion） |
| local_model_scheduler.py | 本地模型 24/7 调度循环——已迁移至MOD-INF-039 |
| migrate_chroma_to_faiss.py | ChromaDB→FAISS+SQLite WAL 数据迁移脚本 |

#### Phase 4：运维自动化（📋 Backlog）

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §6 可观测性 + §6.2 退化矩阵 + §17 容量升级 |
| 产出位置 | `scripts/governance/vms_health_check.py`（cron 脚本） |
| 验收标准 | 每日自动 TTL 清理 + compaction + 异常告警 |
| G7 检查项 | 30 天无手动维护，系统自愈率 > 95%？ |

### 16.4 回滚方案

| 步骤 | 如果出问题 | 回滚操作 |
|------|----------|---------|
| Phase 1 | 某模块集成失败 | 该模块降级为 skip（noop），其他模块继续 |
| Phase 2 | 迁移数据损坏 | 从 kb/ 旧 Collection 重新迁移；BridgeLayer 回退到仅读 kb/ |
| Phase 3 | 混合检索精度低于纯向量 | 切换为纯向量模式 + score threshold 收紧 |
| Phase 4 | HealthMonitor 错误清除了活跃数据 | auto_repair() 尝试修复；失败则从上游源头重写（audit_chain 回放重写未实现） |

### 16.5 施工完成与生产就绪标准

| # | 检查项 | 通过标准 | 类型 | 状态 |
|---|--------|---------|:----:|:----:|
| 1 | InProcessVectorMemory 存在 | `ls` exit 0 | 完成 | ✅ |
| 2 | EmbeddingRouter 存在 | `ls` exit 0 | 完成 | ✅ |
| 3 | HybridRetriever 存在 | `ls` exit 0 | 完成 | ✅ |
| 4 | ProvenanceEnforcer 存在 | `ls` exit 0 | 完成 | ✅ |
| 5 | IndexHealthMonitor 存在 | `ls` exit 0 | 完成 | ✅ |
| 6 | SLO 已定义且可测量 | §5.4 每项 SLI 有测量方式 | 就绪 | ☐ |
| 7 | 监控指标已埋点 | §6.1 每项指标有采集实现 | 就绪 | ☐ |
| 8 | 退化策略已实现 | §6.2 每个组件有降级逻辑 | 就绪 | ✅ |
| 9 | 回滚方案已验证 | §16.4 回滚操作可执行 | 就绪 | ☐ |
| 10 | 集成测试已通过 | §12 每个集成点有测试 | 就绪 | ☐ |

### 16.6 施工状态

| 字段 | 值 | 填写者 |
|------|-----|-------|
| construction_status | completed (Phase 0-3) | 施工者 |
| verification_status | passed | 审计者 |
| code_alignment_verified | yes | 审计者 |

### 16.7 参考实现规格

| # | 规格名称 | 类型 | 规格内容 | 对应代码 |
|---|---------|------|---------|---------|
| 1 | RRF 融合算法 | 算法 | `score = Σ 1/(k+rank+1) * time_decay`，k=60，decay=e^(-rate*age_days) | hybrid_retriever.py |
| 2 | 双嵌入路由规则 | 协议 | decisions/code_context/lessons/knowledge/rules → BGE-M3 1024d；blueprints/session_snapshots/execution_traces → bge-small 512d | embedding_router.py |
| 3 | WriteTrace 校验 | 协议 | MUST 含 origin + audit_chain(≥1) + arbitration 三字段 | provenance_enforcer.py |
| 4 | Collection 维度白名单 | 约束 | dim MUST ∈ {512, 1024} | collection_manager.py |

### 16.8 施工参考卡

| # | 类型 | 名称 | 用途/说明 | 参数/字段 | 输出/约束 |
|---|:----:|------|----------|----------|----------|
| 1 | 命令 | `python -m zephyr.vector_memory` | VMS 模块入口 | — | — |
| 2 | 配置 | `vms_config.yaml` | VMS 环境配置 | persist_dir/model_dir/telemetry | MUST 在启动时校验 |

### 16.10 故障与操作手册

| # | 阶段 | 场景 | 触发条件 | 诊断/操作 | 恢复/产出 | 验证/回退 |
|---|:----:|------|---------|----------|----------|----------|
| 1 | 运行 | BGE-M3 加载失败 | 模型文件损坏/缺失 | 检查 models/bge-m3/ 目录 | 降级为 bge-small | health_check() 确认 |
| 2 | 运行 | ChromaDB SQLite 锁冲突 | 多进程同时写入 | 检查是否有多个 VMS 实例 | 统一为单例访问 | write() 成功 |
| 3 | 运行 | 索引漂移 | 蓝图与磁盘 Collection 不一致 | detect_drift() | auto_repair() 或手动同步 | check_all() 确认 |
| 4 | 运行 | TTL 过期未清理 | HealthMonitor 异常 | check_ttl_expiry() | purge_expired() | 过期记录数=0 |

### 16.12 并发操作模型

| 冲突场景 | 检测方式 | 解决策略 | 合并规则 |
|---------|---------|---------|---------|
| 同 Collection 并发写入 | ChromaDB SQLite WAL 锁 | 写入队列 + 重试 3 次 + 指数退避 | 后写者重试 |
| 同向量 ID 重复写入 | content SHA256 指纹判重 | 幂等写入（upsert） | 保留最新版本 |

---

## §17 容量升级附录

### §17.1 容量基线

| 资源 | 当前基线 | 测量方式 |
|------|---------|---------|
| 向量总数 | ~5,000 | CollectionManager.list_collections() → count |
| 存储空间 | ~200MB | data/vector_db/ 目录大小 |
| 嵌入模型内存 | ~800MB（BGE-M3+bge-small） | 进程内存监控 |
| 检索延迟 p95 | ~50ms（单Collection） | HybridRetriever.elapsed_ms |
| 写入延迟 p95 | ~100ms（含嵌入） | write() 计时 |

### §17.2 缺口清单

| 缺口ID | 当前瓶颈 | 升级方案 | 优先级 | 触发阈值 | 目标版本 | 状态 |
|--------|---------|---------|:------:|---------|---------|:----:|
| GAP-1 | ChromaDB SQLite 单写入者瓶颈 | FAISS + SQLite WAL 优化 | P1 | 并发写入>10/s | v2.0.0 | 待施工 |
| GAP-2 | BGE-M3 嵌入延迟 | 批量嵌入 batch_size=32 + 异步队列 | P1 | 批量写入>100条 | v2.0.0 | 待施工 |
| GAP-3 | 向量存储膨胀 | 量化压缩（Scalar Quantization int8）→ 4x 压缩 | P2 | blueprints>50,000条 | v2.0.0 | 待施工 |
| GAP-4 | HNSW 索引内存 | 按需加载 Collection + 冷热分离 | P2 | 总向量>100,000 | v2.0.0 | 待施工 |
| GAP-5 | 混合检索延迟 | 并行检索 + 结果缓存 | P2 | 跨 Collection p95>500ms | v2.0.0 | 待施工 |
| GAP-6 | GPU 排队策略（单卡 RTX 3090 约束） | 优先级队列 RT>Online>Batch + 低优先级排队等待 + 超时降级CPU推理 | P1 | 多模块竞争GPU | v1.0.0 | 待施工 |

### §17.3 升级版本矩阵

| 版本 | generation | 升级类型 | 核心变更 | 代码覆盖 |
|------|:---:|---------|---------|:---:|
| v0.9.0 | 1 | 基线 | 8 Collection + 双嵌入 + 混合检索 | ✅ |
| v2.0.0 | 2 | 容量升级 | FAISS HNSW/IVF+PQ + 量化压缩 | ⚠️ |

### 升级组件清单

| 组件名 | 对应缺口 | 代码文件 | 施工Phase | 状态 |
|--------|---------|---------|----------|:---:|
| FAISS CollectionManager | GAP-1/GAP-3 | faiss_collection_manager.py | Phase 4+ | 已存在 |
| SQLite Metadata Store | GAP-5 | sqlite_metadata_store.py | Phase 4+ | 已存在 |
| 领域微调模型 | F1 致命漏洞 | — | 待验证 | 待施工 |

---

## §18 决策记录

| # | 决策ID | 决策 | 选项 | 选中 | 依据 | 日期 |
|---|--------|------|------|------|------|------|
| 1 | D-VMS-01 | ChromaDB 作为向量数据库 | ChromaDB/FAISS/Milvus/Qdrant | ChromaDB | 本地嵌入式+Python原生+零运维；FAISS需自建元数据层 | 2026-05-05 |
| 2 | D-VMS-02 | BGE-M3 1024d + bge-small 512d 双路径 | 统一1024d/统一512d/双路径 | 双路径 | 精度域需1024d，体量域512d节省3×资源 | 2026-05-05 |
| 3 | D-VMS-03 | 8 Collection 按语义域划分 | 3-5 Collection/8 Collection | 8 Collection | 治理规则需独立高优检索；混合存储=检索噪音 | 2026-05-05 |
| 4 | D-VMS-04 | 混合检索 Vector+BM25+RRF | 纯向量/纯BM25/混合 | 混合 | 中文领域术语需BM25补充；RRF融合精度>纯向量 | 2026-05-05 |
| 5 | D-VMS-05 | WriteTrace provenance 强制 | 可选provenance/强制 | 强制 | 单人+AI维护=无provenance则无审计底线 | 2026-05-05 |
| 6 | D-VMS-06 | ChromaDB→FAISS迁移（Phase 2后） | 保持ChromaDB/迁移FAISS | 迁移FAISS | FAISS HNSW/IVF+PQ性能+量化优势 | 2026-05-05 |
| 7 | D-VMS-07 | Ollama HTTP API 复用嵌入推理 | 直接ONNX Runtime/Ollama | Ollama | 复用Ollama基础设施+模型管理 | 2026-05-05 |

---

## 术语表

| 术语 | 精确定义 | 易混淆术语 | 区别 |
|------|---------|-----------|------|
| VMS | Vector Memory Service——统一向量记忆体 | KB（知识库） | VMS 存向量+嵌入，KB 存结构化知识条目 |
| WriteTrace | 写入溯源记录（origin+audit_chain+arbitration） | Provenance | WriteTrace 是完整溯源记录，Provenance 是其中三字段 |
| RRF | Reciprocal Rank Fusion——倒数排名融合 | 加权求和 | RRF 基于排名位置融合，加权求和基于分数融合 |
| CBAC | Collection-Based Access Control——基于 Collection 的访问控制 | RBAC | CBAC 绑定到 Collection 级别，RBAC 绑定到角色 |
| Collection | ChromaDB 中的向量集合（类比数据库表） | Index | Collection 包含向量+元数据+文档，Index 仅索引 |
| HybridRetriever | 混合检索器（Vector+BM25+RRF） | EmbeddingRouter | HybridRetriever 做检索融合，EmbeddingRouter 做嵌入路由 |
| Hot Collection | 高频热数据 Collection（decisions/rules/lessons/knowledge） | Cold Collection | Hot 用 1024d + 高频分块策略，Cold 用 512d + 低频策略 |
| TTL | Time-To-Live——数据自动过期时间 | permanent | TTL>0 的数据到期自动清理，permanent 永不过期 |

---

## 已知问题与盲点登记

> 四轮审计共 80 盲点。以下为压缩版——保留 ID+标题+RPN+优先级。详细描述见 git 历史。

### 盲点汇总表

| 轮次 | 维度数 | 盲点数 | P0 | P1 | P2 | RPN≥48 |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| R1(v0.4.0) | 10 | 33 | 12 | 12 | 9 | 8 |
| R2(v0.5.0) | 8 | 22 | 13 | 7 | 2 | 8 |
| R3(v0.6.0) | 6 | 19 | 8 | 8 | 3 | 5 |
| R4(v0.7.0) | 1 | 6 | 3 | 3 | 0 | 4 |
| **合计** | **25** | **80** | **36** | **30** | **14** | **25** |

### P0 盲点列表

| ID | 标题 | RPN | 状态 |
|----|------|:---:|------|
| V401 | 无检索质量评估 Benchmark | 48 | ❌待实现 |
| V402 | 无 MMR 检索结果多样性控制 | 36 | ❌待实现 |
| V405 | 无向量量化压缩策略 | 36 | ❌待实现 |
| V409 | 无向量去重策略 | 48 | ❌待实现 |
| V411 | 无向量与源文档的"过时检测" | 64 | ❌待实现 |
| V416 | 无"按 Session 成熟度"检索预算 | 64 | ❌待实现 |
| V417 | 无检索结果的"时间衰减"权重 | 36 | ✅已实现 |
| V419 | 无跨 Collection 联合检索 | 48 | ✅已实现 |
| V420 | 无向量嵌入中的 PII/敏感信息检测 | 32 | ❌待实现 |
| V423 | 无"VMS 一键健康检查" | 45 | ✅已实现 |
| V424 | 无 ChromaDB SQLite 自动维护调度 | 36 | ✅已实现 |
| V425 | 无"Owner离开后VMS状态恢复"摘要 | 36 | ❌待实现 |
| V501 | 无 ChromaDB 双重 Client 实例冲突防护 | 48 | ❌待实现 |
| V502 | 无 ChromaDB 版本升级的兼容性闸门 | 32 | ❌待实现 |
| V504 | 无 SQLite WAL 文件无限增长防护 | 48 | ❌待实现 |
| V505 | 无 Token 溢出截断策略 | 48 | ❌待实现 |
| V507 | 无 ONNX 模型首次推理冷启动策略 | 36 | ✅已实现 |
| V511 | 无查询超时与取消机制 | 64 | ✅已实现 |
| V514 | 无检索结果的"可信度衰减"标记 | 48 | ❌待实现 |
| V515 | 无"VMS 检索结果与 AI 最终决策"的可追溯闭环 | 48 | ❌待实现 |
| V517 | 无 VMS 级"紧急只读模式" | 60 | ❌待实现 |
| V518 | 无"优雅劣化"策略 | 48 | ✅已实现 |
| V519 | 无"全量数据丢失后的最小恢复路径" | 50 | ❌待实现 |
| V520 | 无"VMS 自我实现预言"防护 | 48 | ❌待实现 |
| V521 | 无"上下文污染"检测 | 64 | ❌待实现 |
| V601 | 无 VMS 公共 API 版本化承诺 | 48 | ❌待实现 |
| V602 | 无同步/异步接口的明确设计决策 | 48 | ❌待实现 |
| V605 | 无"向量检视器"交互工具 | 45 | ❌待实现 |
| V608 | 无中英混合语料的嵌入质量验证 | 36 | ❌待实现 |
| V609 | 无极端短文本嵌入质量对策 | 36 | ❌待实现 |
| V615 | 无 VMS 环境配置的显式 Schema 校验 | 48 | ✅已实现 |
| V618 | 无 VMS 异常分层体系 | 48 | ✅已实现 |
| F1 | 嵌入质量领域假设未经实证验证 | 致命 | ❌待验证 |
| F2 | 无检索降级逃生舱 | 致命 | ✅已实现 |
| F5 | 无对抗性检索投毒评估 | 致命 | ❌待实现 |

### R4 致命漏洞

| ID | 标题 | 级别 | 状态 |
|----|------|------|------|
| F1 | 嵌入质量领域假设未经实证验证 | ☠️ 致命 | ❌待验证 |
| F2 | 无检索降级逃生舱 | ☠️ 致命 | ✅已实现 |
| F3 | 无部署/迁移前后回归金丝雀验证 | ⚠️ 严重 | ❌待实现 |
| F4 | 知识衰减速率非领域感知 | ⚠️ 严重 | ❌待实现 |
| F5 | 无对抗性检索投毒评估 | ☠️ 致命 | ❌待实现 |
| F6 | 无系统自解释与继承能力 | ⚠️ 严重 | ❌待实现 |

---

## 自检与闭合清单

| # | 阶段 | 检查项 | 确认方式 | 状态 |
|---|:----:|--------|---------|:----:|
| 1 | 设计 | §3 每个组件在 §4 有对应接口 | 逐组件核对 | ☐ |
| 2 | 设计 | §4 每个接口在 §16 有对应施工步骤 | 逐接口核对 | ☐ |
| 3 | 设计 | §5 每个约束在 §9 有对应测试 | 逐约束核对 | ☐ |
| 4 | 设计 | §0.1 每个代码文件在 §11 有对应产出物路径 | 逐文件核对 | ☐ |
| 5 | 设计 | §10 每个依赖在 cross-module-dependency-registry.yaml 有对应条目 | 逐依赖核对 | ☐ |
| 6 | 前 | 已读取蓝图全文 | 逐节确认 | ☐ |
| 7 | 前 | 术语表中每个术语含义已理解 | 能回答区别 | ☐ |
| 8 | 前 | 成熟度声明中 volatile/evolving 的部分已标记 | 知道哪些可改 | ☐ |
| 9 | 前 | 已知问题登记中未解决的问题已知晓 | 知道哪些坑不能踩 | ☐ |
| 10 | 中 | 每步施工后执行验证命令 | exit 0 才进下一步 | ☐ |
| 11 | 中 | 新代码文件头部十五字段完整 | 逐文件核对 | ☐ |
| 12 | 中 | 修改接口契约后检查 §18 决策记录 | 决策ID+依据已更新 | ☐ |
| 13 | 后 | §0 代码对齐验证已更新 | construction_progress 与实际一致 | ☐ |
| 14 | 后 | 临时时态内容已清理 | 迁移方案已执行→删除 | ☐ |

---

## 成熟度声明

| 设计维度 | 成熟度 | 信心 | 升级标准 | 说明 |
|---------|:------:|:---:|---------|------|
| 核心架构 | frozen | 高 | — | 8 Collection + 双嵌入 + 混合检索已验证 |
| 接口契约 | stable | 高 | Phase 4 验收通过 | §4 公共 API 已实现 |
| 数据模型 | stable | 高 | — | Pydantic V2 模型已实现 |
| Collection Schema | frozen | 高 | — | 8 Collection Schema 与代码一致 |
| 检索质量评估 | evolving | 中 | benchmark 建立后 | V401 待实现 |
| 运维自动化 | volatile | 低 | Phase 4 完成 | Phase 4 待施工 |

---

## 版本演进路线图

| 版本 | 核心变更 | 前置版本 | 施工状态 |
|------|---------|---------|:-------:|
| v0.3.0 | 蓝图 SSoT 重建 + 8 Collection 对齐 | — | 已完成 |
| v0.5.0 | R2 审计 22 盲点注入 | v0.4.0 | 已完成 |
| v0.6.0 | R3 审计 19 盲点注入 | v0.5.0 | 已完成 |
| v0.7.0 | R4 终审 6 致命漏洞 | v0.6.0 | 已完成 |
| v0.8.0 | v3.6 模板升级+压缩工作流 | v0.7.0 | 已完成 |
| v0.9.0 | 模板合规+压缩+回填（本版） | v0.8.0 | 已完成 |
| v0.11.0 | 审查回填+压缩：§0.4/§0.5/§1.6/§1.7/§4.5/§10.5/§10.6/§16.3创建文件清单+真源修正+ssot_claims+codification_level | v0.9.0 | 已完成 |
| v0.12.0 | MOD-INF-039拆分对齐：§0.1迁移标注+§0.4 SSoT委托+§0.5副本声明+§2.1负责方修正+§10.1/§10.5新增MOD-INF-039+ssot_claims移除双嵌入+测试修复 | v0.11.0 | 已完成 |
| v1.0.0 | Phase 4 运维自动化 + benchmark 建立 | v0.12.0 | 待施工 |
| v2.0.0 | FAISS 迁移 + 量化压缩 | v1.0.0 | 待施工 |

---

## ⚠️ Vibe Coding 蓝图编写铁律

| # | 铁律 | 违反后果 |
|---|------|---------|
| 1 | **蓝图 SSoT 不可绕过**——修改 VMS 设计必须先改蓝图，再改代码 | 蓝图-代码漂移 |
| 2 | **8 Collection Schema 不可 AI 擅自变更**——新增/删除/重命名 Collection 须经 Owner 审批 | 治理失控 |
| 3 | **WriteTrace 不可省略**——每条向量写入必须携带 provenance | 审计链断裂 |
| 4 | **双嵌入维度不可混用**——同一 Collection 内维度必须一致 | 检索不可比 |
| 5 | **TTL 不可跳过**——execution_traces 30d / code_context+session_snapshots 90d | 磁盘膨胀 |
| 6 | **CBAC 校验不可绕过**——AI 自治级别绑定到 Collection | 越权操作 |
| 7 | **混合检索不可降级为纯向量**——除非 RRF 融合精度低于纯向量（需 benchmark 证据） | 检索质量退化 |
| 8 | **IndexHealthMonitor 不可禁用**——启动时漂移检测 + 定期健康检查 | 漂移无感知 |
| 9 | **vms_config.yaml 是唯一配置入口**——禁止硬编码配置 | 配置漂移 |
| 10 | **迁移脚本必须 dry-run**——先输出映射表 → Owner 审核 → 执行 | 数据损坏 |
| 11 | **construction_progress 必须与代码实际状态一致** | 重复造轮子或跳过施工 |
| 12 | **actual_disk_path 必须与 §11 产出物路径一致** | 搜索失败、导入错误 |
| 13 | **已实现代码不在蓝图中重复**——§0.1 标记`已实现`的模块，蓝图只保留接口签名（§4） | 双源漂移 |
| 14 | **临时时态内容执行完毕后从蓝图删除** | 蓝图膨胀 |
| 15 | **蓝图内容拆分判定**——职责不同→拆分独立蓝图；职责相同→原地升级 | 跨模块影响无法追踪 |
| 16 | **术语表不可省略** | 术语理解漂移 |

---

## 蓝图拆分判定标准

> 铁律 #15 的操作定义。

| 判定条件 | 结果 | 操作 |
|---------|------|------|
| 服务对象相同 + 变更频率同步 + 依赖关系重叠 | 原地升级 | 在 §17 容量升级附录中增量记录 |
| 有独立 module_id 前缀 | 拆分 | 创建子蓝图，belongs_to=本蓝图 |
| 有独立 Phase 路线图和交付节奏 | 拆分 | 同上 |
| 有独立依赖关系图（与主体 depends_on 交集<50%） | 拆分 | 同上 |
| 内容超100行且与主体无直接数据流 | 拆分 | 同上 |
| 拆分后 | MUST验证 | 子蓝图有独立frontmatter+概述+§0~§18；本蓝图§10新增引用；blueprint_registry.yaml同步更新 |

**当前判定**：审计盲点 R1-R4 服务对象相同 + 变更频率同步 + 依赖关系完全重叠 → 原地保留（已压缩）。

---

## ⚠️ 安全删除协议

| # | 铁律 | 原因 |
|---|------|------|
| 1 | 删除 Collection 前 MUST 确认无消费者（Grep 全项目引用） | 引用断裂 |
| 2 | 删除代码文件前 MUST 运行 `python scripts/governance/d5_architecture/pre_write_gate.py <文件> --delete` | 不可逆 |
| 3 | 删除蓝图章节前 MUST 确认无其他章节引用该章节编号 | 信息丢失 |
| 4 | 任何删除 MUST 在 §18 决策记录中登记 | 无追溯 |
| 5 | 物理删除只能在对 stable 阶段执行，deprecated 至少保持1个Phase | 缓冲期 |
| 6 | 物理删除必须人类确认 | AI 不得自行决定删除文件 |

---

## 必备链接

| # | 文件 | module_id | 完整绝对路径 | 编写时用途 |
|---|------|-----------|------------|----------|
| 1 | VMS YAML SSoT | — | `D:\ZephyrAlpha\architecture_model\layers\b_vector_memory.yaml` | 蓝图真源 |
| 2 | KBG-0016 嵌入契约 | — | `D:\ZephyrAlpha\docs\02_enterprise_architecture\adr\adr-0016-vms-embedding-contract.md` | 嵌入规格 |
| 3 | KBG-0031 ChromaDB选型 | — | `D:\ZephyrAlpha\docs\02_enterprise_architecture\adr\adr-0031-chromadb-vector-retrieval.md` | 选型依据 |
| 4 | CE 蓝图 | MOD-CONTEXT_ENGINE | `D:\ZephyrAlpha\docs\03_modules\_domain_knowledge\context_engine\blueprint.md` | 集成目标 |
| 5 | KB 蓝图 | MOD-KB-001 | `D:\ZephyrAlpha\docs\03_modules\_domain_knowledge\knowledge_base\blueprint.md` | 整合目标 |
| 6 | 蓝图注册表 | — | `D:\ZephyrAlpha\docs\03_modules\blueprint_registry.yaml` | 注册 |
| 7 | 代码构建标准 | GOV-ENG-001 | `D:\ZephyrAlpha\docs\01_policies_and_standards\governance\engineering\code-construction-standards.md` | 代码规范 |
| 8 | AI 压缩工作流标准 | GOV-DOC-011 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_030_doc_numbering_metadata.yaml` | 压缩规则 |
| 9 | 元数据注册表 | PS-STD-001 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_043_meta_rule_metadata.yaml` | 编号规则 |
| 10 | 模块ID注册表 | — | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture_model\module_id_registry.yaml` | 编号注册 |

---

## 项目中已有类似功能

| # | 已有模块/文件 | 完整绝对路径 | 功能重叠点 | 为什么不能复用 |
|---|-------------|------------|----------|-------------|
| 1 | kb/chromadb_init.py | `D:\ZephyrAlpha\src\zephyr\kb\chromadb_init.py` | 4+1 Collection 创建 | VMS 8 Collection + 双嵌入 + FAISS；已冻结 |
| 2 | kb/unified_memory_api.py | `D:\ZephyrAlpha\src\zephyr\kb\unified_memory_api.py` | WriteTrace + CBAC | VMS 扩展版 WriteTrace；已冻结 |

---

## 涉及的文件范围

| # | 文件/目录 | 完整绝对路径 | 关系 | 变更类型 |
|---|---------|------------|------|---------|
| 1 | VMS 源码 | `D:\ZephyrAlpha\src\zephyr\integration\vector_memory\` | 修改 | 接口实现 |
| 2 | kb/ 遗留 | `D:\ZephyrAlpha\src\zephyr\kb\` | 读取 | 迁移源 |
| 3 | 单元测试 | `D:\ZephyrAlpha\tests\unit\vector_memory\` | 修改 | 测试覆盖 |
| 4 | 配置 | `D:\ZephyrAlpha\src\zephyr\integration\vector_memory\vms_config.yaml` | 读取 | 配置校验 |
| 5 | 嵌入模型 | `D:\ZephyrAlpha\models\bge-m3\` + `models\bge-small-zh-v1.5\` | 读取 | 模型加载 |
| 6 | 向量数据 | `D:\ZephyrAlpha\data\vector_db\` | 修改 | 持久化 |
| 7 | 蓝图 | `D:\ZephyrAlpha\docs\03_modules\_domain_knowledge\vector_memory\` | 修改 | 本文件 |

---

## 1. 已实现代码完整路径索引

> **AGENTS.md §6.14 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> 向量记忆——仅目录+__init__.py docstring

### 1.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/integration/vector_memory/bm25_index.py` | ✅ 已实现 | |
| `src/zephyr/integration/vector_memory/bridge_layer.py` | ✅ 已实现 | |
| `src/zephyr/integration/vector_memory/cache_layer.py` | ⚠️ 骨架 | |
| `src/zephyr/integration/vector_memory/chunk_strategy_router.py` | ✅ 已实现 | |
| `src/zephyr/integration/vector_memory/collection_manager.py` | ✅ 已实现 | |
| `src/zephyr/integration/vector_memory/collection_schemas.py` | ✅ 已实现 | |
| `src/zephyr/integration/vector_memory/cross_collection_retriever.py` | ✅ 已实现 | |
| `src/zephyr/integration/vector_memory/delegated_vector_memory.py` | ✅ 已实现 | |
| `src/zephyr/integration/vector_memory/design_principles.py` | ✅ 已实现 | |
| `src/zephyr/integration/vector_memory/embedding_router.py` | ⚠️ 骨架 | |
| `src/zephyr/integration/vector_memory/faiss_collection_manager.py` | ✅ 已实现 | |
| `src/zephyr/integration/vector_memory/hybrid_retriever.py` | ✅ 已实现 | |
| `src/zephyr/integration/vector_memory/in_memory_fake_vms.py` | ✅ 已实现 | |
| `src/zephyr/integration/vector_memory/in_memory_memory_backend.py` | ✅ 已实现 | |
| `src/zephyr/integration/vector_memory/in_process_vector_memory.py` | ✅ 已实现 | |
| `src/zephyr/integration/vector_memory/index_health_monitor.py` | ✅ 已实现 | |
| `src/zephyr/integration/vector_memory/interface.py` | ✅ 已实现 | |
| `src/zephyr/integration/vector_memory/local_model_scheduler.py` | ⚠️ 骨架 | |
| `src/zephyr/integration/vector_memory/migrate_chroma_to_faiss.py` | ✅ 已实现 | |
| `src/zephyr/integration/vector_memory/ollama_chat.py` | ⚠️ 骨架 | |
| `src/zephyr/integration/vector_memory/ollama_embedding.py` | ⚠️ 骨架 | |
| `src/zephyr/integration/vector_memory/provenance_enforcer.py` | ✅ 已实现 | |
| `src/zephyr/integration/vector_memory/retrieval_feedback.py` | ✅ 已实现 | |
| `src/zephyr/integration/vector_memory/sqlite_metadata_store.py` | ✅ 已实现 | |
| `src/zephyr/integration/vector_memory/vector_bridge.py` | ✅ 已实现 | |
| `src/zephyr/integration/vector_memory/vms_config.yaml` | ✅ 已实现 | |
| `src/zephyr/integration/vector_memory/vms_errors.py` | ✅ 已实现 | |
| `src/zephyr/integration/vector_memory/vms_schemas.py` | ✅ 已实现 | |

### 1.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §1（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下

---

## 治理信息

### SSoT 声明

| 内容 | 真源 | 非真源 |
|------|------|--------|
| VMS 核心架构设计 | **本文档 §1-§10** | 旧蓝图/旧文档 |
| VMS 接口契约 | **本文档 §4** | — |
| VMS 施工步骤 | **本文档 §16** | 旧施工图 |
| 代码文件清单与对齐状态 | **本文档 §0** | blueprint_registry.yaml（派生） |
| 容量升级方案 | **本文档 §17** | 独立升级文档 |
| VMS YAML 规范 | **b_vector_memory.yaml** | 本蓝图（YAML 是本蓝图的派生格式） |

**任何与本蓝图冲突的定义，以本蓝图为准。**

### 消费者注册表

| Tier | 消费者 | 依赖内容 |
|:----:|--------|---------|
| Tier 1 | CE 蓝图 (MOD-CONTEXT_ENGINE) | §4 接口契约、§10 依赖关系 |
| Tier 1 | KB 蓝图 (MOD-KB-001) | §12 集成点、§5.3 迁移方案 |
| Tier 2 | FLE (MOD-FEEDBACK_LOOP) | §4 RetrievalFeedback 接口 |
| Tier 2 | Orchestrator (MOD-TASK_SYSTEM) | §4 VectorBridge.write_decision() |
| Tier 3 | tests/ | §4 数据模型、§11 产出物路径 |

### 变更审批与同步规则

| 变更类型 | 审批要求 | Tier 1 同步 | Tier 2 同步 |
|---------|---------|------------|------------|
| 接口契约新增/修改（§4） | 需 Owner 审批 + 通知所有消费者 | 下游检查接口兼容性 | 检查集成点兼容性 |
| Collection Schema 修改（§2） | 需 Owner 审批 | 下游更新依赖声明 | 更新集成路由 |
| construction_progress 变更 | 需 §0 对齐验证通过 | 下游更新依赖状态 | 更新集成测试 |
| 施工步骤微调 | AI 可自主修改 | 下游更新产出物引用 | 更新配置文件 |
| 容量升级方案新增（§17） | 需 Owner 审批 | 下游评估影响 | 更新容量预算 |

---

## 蓝图特有章节

> 超出模板下限的内容 MUST 写在本章节内 + 标注三要素。

### 蓝图特有：混合检索时间衰减参数

| 要素 | 内容 |
|------|------|
| 来源 | R2 审计 V417/V514 + R4 F4 |
| 仅本蓝图 | VMS 特有的 Collection 级衰减率 |
| 不可砍 | 砍掉→AI 不知道各 Collection 的衰减率→统衰减破坏领域差异 |

| Collection | decay_rate (/day) | 依据 |
|-----------|:-----------------:|------|
| decisions | 0.003 | 架构决策缓慢衰减 |
| lessons | 0.005 | 经验中等衰减 |
| knowledge | 0.02 | 市场数据快速衰减 |
| rules | 0.0001 | 治理规则几乎不衰减 |
| code_context | 0.01 | 代码上下文中等衰减 |
| blueprints | 0.001 | 蓝图缓慢衰减 |
| session_snapshots | 0.005 | 会话摘要中等衰减 |
| execution_traces | 0.02 | 执行轨迹快速衰减 |

### 蓝图特有：过渡期 Collection 映射

| 要素 | 内容 |
|------|------|
| 来源 | Phase 2 迁移方案 |
| 仅本蓝图 | VMS 特有的 kb/→VMS 迁移映射 |
| 不可砍 | 砍掉→AI 不知道旧 Collection 映射到哪个新 Collection |

| kb/ 旧 Collection | VMS 新 Collection | 迁移方式 |
|-------------------|------------------|---------|
| ke_entries | knowledge | BridgeLayer.migrate_collection |
| vibe_rules | rules | BridgeLayer.migrate_collection |
| blueprints | blueprints | BridgeLayer.migrate_collection |
| failure_patterns | lessons | BridgeLayer.migrate_collection |
| unified_memory | 按 topic 拆分到多个 VMS Collection | 拆分脚本 dry-run→Owner审核→执行 |

> kb/ 过渡期路径：`.audit_cache/vector_index/` → VMS 投产路径 `data/vector_db/` → BridgeLayer 负责迁移。
