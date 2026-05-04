---
module_id: ADR-0016
doc_type: adr
title: Vector Memory Service — ChromaDB 0.6 + BGE-M3 ONNX + 递归字符分块
version: 1.0.0
status: active
date: '2026-04-24'
owner: ZephyrAlpha-Owner
ttl: permanent
related_adrs:
- ADR-0005
- ADR-0015
- ADR-0021
priority: P0
phase: Phase-1
tech_refs:
- TECH-04
- TECH-05
- TECH-06
supersedes_doc: archive/reorg-2026-04-24/08_ai_engineering/memory-interface-contract.md
layer: L12
classification: confidential
language: zh
created_by: agent
valid_from: '2026-04-24'
superseded_by: null
supersedes: [ADR-0005]
related_rationale: []
related_open_questions: []
tags: [adr, vibe-coding]
summary: "**Vibe Coding 2.0 核心服务** Vector Memory Service（ChromaDB 0.6 + BGE-M3 ONNX + 递归分块 + 5 Collection + 级联 4 场景）| accepted"
---

# ADR-0016: Vector Memory Service — ChromaDB 0.6 + BGE-M3 ONNX + 递归字符分块

**状态**：Accepted
**日期**：2026-04-24
**决策者**：ZephyrAlpha-Owner
**优先级**：P0
**阶段**：Phase 1 首批上线

---

## 1. 状态（Status）

- **当前状态**：`accepted`
- **提议日期**：2026-04-24
- **拍板日期**：2026-04-24

## 2. 背景与问题（Context）

### 2.1 问题陈述

ADR-0005 定义的"六层 KMS 架构"在 Phase 1 重整中被识别为**空壳体系**（模块名齐全但无实现），无法承载：

- ADR / 知识条目 / 代码上下文 / 历史教训 / 用户意图 5 大 Collection 的**语义检索**
- Context Engine (ADR-0015) 的**动态上下文装配**
- Feedback Loop Engine (ADR-0019) 的**历史模式回溯**

2026-04-24 的 `vibe-coding-audit-merged.md §Kimi 7.5.2` 结论：**用 Vector Memory Service (VMS) 取代 KMS 六层**，以向量存储为核心、库化先行、按需服务化。

### 2.2 设计目标

- **零外部依赖**：本地可运行（离线优先）
- **库化优先**：Phase 1 作为 Python 库嵌入；Phase 3+ 升级为独立服务（Protocol 共享签名零业务层改动）
- **5 个 Collection**：decisions / knowledge / code_context / lessons / user_intent
- **增量同步**：git hook 触发，不要求全量 rebuild
- **级联语义**：supersede / reorder / delete / merge 四场景必须覆盖

### 2.3 参考真源

- `vibe-coding-audit-merged.md §Kimi 7.5.2 Vector Memory Service`
- `vibe-coding-audit-merged.md §Qwen 选型表 #4-6`
- `vector-memory-service-interface.md v1.2.0`（773 行，B-a-1 模板）

---

## 3. 考虑过的方案（Options Considered）

### 方案 A：ChromaDB 0.6 + BGE-M3 ONNX + 递归分块 ✅

- **优点**：
  - ChromaDB 0.6 嵌入式模式，SQLite 后端，无独立服务
  - BGE-M3 多语言 + 8K 上下文 + MIT 兼容 + 1024 维合理成本
  - ONNX int8 量化 ~500MB，CPU 可跑（300ms/文档）
  - 递归字符分块是 LangChain/LlamaIndex 生态事实标准
- **缺点**：
  - ChromaDB 单机上限约 1M 向量，Phase 3+ 可能需迁移
  - BGE-M3 ONNX 质量较 OpenAI `text-embedding-3-small` 低约 5-10%

### 方案 B：Qdrant 独立服务 + text-embedding-3-small + 语义分块

- **优点**：Qdrant 性能好；OpenAI embedding 质量领先
- **缺点**：
  - Qdrant 需独立运行（Docker / 二进制），违反 Phase 1 "单进程" 原则
  - OpenAI embedding API 破坏离线 + 调用费用
  - 语义分块依赖 spaCy，模型大 + 召回提升 < 5%
- **结论**：**否决**

### 方案 C：Weaviate Cloud + Cohere embed

- **优点**：托管服务，无运维
- **缺点**：网络依赖 + 数据上云（合规风险 + 量化策略外泄风险）
- **结论**：**否决**

---

## 4. 决策（Decision）

**最终选择：方案 A — ChromaDB 0.6 + BGE-M3 ONNX int8 + 递归字符分块**

### 4.1 关键决策点

| 决策点 | 首选 | 备选 | 升级触发条件 |
|-------|------|------|-------------|
| **向量库** | ChromaDB 0.6（嵌入式）| Qdrant 本地模式 | 持久化大小 > 500MB（TECH-04 watchboard）|
| **Embedding 模型** | BAAI/bge-m3 ONNX int8 | text-embedding-3-small | 本地质量 < API 质量 20% 持续 14 天（TECH-05）|
| **分块策略** | 递归字符分块（500/100）| 语义分块 spaCy | 召回率 @10 < 80%（TECH-06）|
| **并发** | `asyncio.Lock` + `filelock.FileLock` | — | — |
| **持久化路径** | `.runtime/chromadb/` | 通过 `vibe_config.yaml::runtime_root` 覆盖 | — |
| **部署模式** | Phase 1: In-process; Phase 3+: HTTP Server | — | 并发请求 > 50/s 或 RAM > 4GB |

### 4.2 Collection 设计（5 个）

| Collection | 写入方 | 读取方 | 元数据关键字段 |
|-----------|-------|-------|---------------|
| `decisions` | ADR commit hook | Context Engine / FLE | `adr_id` / `status` / `superseded_by` |
| `knowledge` | 知识库 commit hook | Context Engine | `doc_id` / `layer` / `tags` |
| `code_context` | Agent 任务完成 | Context Engine / Orc | `file_path` / `l_layer` / `task_id` |
| `lessons` | Post-mortem | Context Engine / FLE | `incident_id` / `severity` |
| `user_intent` | Session start | Context Engine | `session_id` / `intent_hash` |

### 4.3 级联语义表（关键创新）

| 级联场景 | 触发 | 动作 | search_weight |
|---------|------|------|:-------------:|
| `supersede` | 新 ADR 替代旧 ADR | 旧条目 `metadata.superseded_by = 新ID` | 0.1（降级）|
| `reorder` | 任务依赖变更 | 相关条目 `metadata.task_deps` 更新 | 1.0 |
| `delete` | `git rm` 源文件 | 所有 Collection 物理删除 | 0 |
| `merge` | 去重检测发现相似条目 | 旧条目 `metadata.merged_into = 新ID` | 0 |

---

## 5. 后果（Consequences）

### 5.1 正面后果

- **KMS 六层空壳清零**：ADR-0005 的 KMS 架构被本 ADR **增量取代**（不废弃 ADR-0005，但实施路径切换）
- **Phase 1 可落地**：2-3 人日 MVP（含 5 Collection + bulk_bootstrap + multi_search）
- **离线友好**：单人系统首要诉求
- **增量同步**：git hook `sync_document()` 支持 add/modify/delete

### 5.2 负面后果

- **ChromaDB 0.6 相对 young**：2024 Q3 发布，生态成熟度 < Qdrant / Weaviate
- **BGE-M3 中文质量虽佳但英文弱于 OpenAI**：需接受
- **单机上限**：~1M 向量后性能退化

### 5.3 未来重新评估触发条件

- **TECH-04**：ChromaDB 持久化 > 500MB → Qdrant 独立服务
- **TECH-05**：BGE-M3 召回 @10 < 80% 持续 14 天 → 切 text-embedding-3-small 或 BGE-M3 v2
- **TECH-06**：分块导致 context 截断率 > 15% → 语义分块 + 重叠加大
- Phase 3 引入外部用户 → 必须升级为服务模式 + 多租户隔离

---

## 6. 落地动作（Implementation）

| # | 动作 | 物理位置 | 估时 |
|---|------|---------|:----:|
| 1 | `VectorMemoryProtocol` 抽象基类 | `src/zephyr/vector_memory/protocol.py` | 0.5 天 |
| 2 | `InProcessVectorMemory`（ChromaDB SDK）| `src/zephyr/vector_memory/in_process.py` | 1 天 |
| 3 | BGE-M3 ONNX 推理封装 | `src/zephyr/vector_memory/embedder.py` | 0.5 天 |
| 4 | 递归分块器 | `src/zephyr/vector_memory/chunker.py` | 0.5 天 |
| 5 | 5 Collection schema + bootstrap | `src/zephyr/vector_memory/collections.py` | 0.5 天 |
| 6 | `bulk_bootstrap` + `sync_document` | `src/zephyr/vector_memory/sync.py` | 1 天 |
| 7 | `multi_search` (RRF) | `src/zephyr/vector_memory/multi_search.py` | 0.5 天 |
| 8 | 降级路径：文件系统 grep fallback | `src/zephyr/vector_memory/fallback.py` | 0.5 天 |
| 9 | P0 测试组（冷启动 + 级联 + 降级）| `tests/vector_memory/test_p0.py` | 1 天 |

**总工时**：约 6 人日

---

## 7. 参考

- **真源**：`vibe-coding-audit-merged.md §Kimi 7.5.2` + `§Qwen 选型表 #4-6`
- **接口规范**：[`vector-memory-service-interface.md v1.2.0`](../../03_modules/_b_track_interfaces/vector-memory-service-interface.md)（5 接口文档共享模板）
- **归档旧契约**：`archive/reorg-2026-04-24/08_ai_engineering/memory-interface-contract.md`
- **架构位置**：[`03-application-architecture.md §4A.1`](../target-architecture/03-application-architecture.md) + [`04-technology-architecture.md §2.1B`](../target-architecture/04-technology-architecture.md)
- **技术选型**：[`technology-landscape.yaml TECH-04/05/06`](../target-architecture/architecture-model/technology/technology-landscape.yaml)
- **相关 ADR**：ADR-0005（KMS，增量取代）/ ADR-0015（CE 消费者）/ ADR-0021（SSoT 前置）
- **外部**：[ChromaDB docs](https://docs.trychroma.com/) / [BGE-M3 paper](https://huggingface.co/BAAI/bge-m3)

---

## 8. 修订记录

| 日期 | 说明 |
|------|------|
| 2026-04-24 | v1.0.0 初版：ChromaDB 0.6 + BGE-M3 ONNX + 递归分块；5 Collection + 级联 4 场景；B-e-3 产出。 |
