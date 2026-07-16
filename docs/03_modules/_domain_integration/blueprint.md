---
module_id: MOD-INF-042
submodule_path: src/zephyr/integration/local_model
title: MOD-INF-042 — Local Model 蓝图 — 本地模型推理基础设施·BGE-M3嵌入+Ollama推理+调度+缓存
summary: 本地模型推理基础设施——BGE-M3文本嵌入+Ollama本地推理+调度+缓存，为KB向量检索和LLM调用提供本地化推理能力。
version: 0.1.0
status: Active
layer: L0_infrastructure
date: "2026-06-23"
last_updated: "2026-07-16"
generation: 1
belongs_to: "MOD-MASTER_BLUEPRINT"
construction_progress: scaffold
actual_disk_path: src/zephyr/integration/local_model/
functional_domain: infra
stability: stable
safety_level: M
ai_autonomy: ai_modifiable
depends_on:
  must: []
  optional:
  - MOD-INF-011
  - MOD-INF-009
  - MOD-INF-019
tags:
- local-model
- embedding
- bge-m3
- ollama
- inference
- infrastructure
ssot_declarations:
- content: 嵌入维度与Collection Schema映射
  source: MOD-INF-011 blueprint §3.1
  sync_rule: MOD-INF-011变更维度时MUST同步更新本蓝图§4
- content: Ollama API契约
  source: runtime_config.py ollama_base_url
  sync_rule: 运行时配置变更时MUST同步
ttl: permanent
doc_type: blueprint
responsibility_domain: 
build_status: generated
design_maturity: prototype
---
## §0 代码对齐验证 {temporal_type=permanent}

> **架构归属SSoT**：见 AGENTS.md §7「代码规范」（depgraph SSoT 真源唯一指针）
> **完整文件清单SSoT**：`python scripts/governance/extract_depgraph.py --modules MOD-INF-042`
> **代码头部规范**：`[BLUEPRINT]/[MODULE]/[INVARIANTS]/[MODIFY-GUARD]/[CONSUMERS]/[STABILITY]/[SAFETY]/[AI_AUTONOMY]/[ERROR_CONTRACT]/[TESTS]` — 见防幻觉十八条

### §0.1 代码文件清单

| # | 文件名 | 蓝图章节 | 职责 | 实现状态 | 归属 |
|---|--------|---------|------|:-------:|------|
| 1 | embedding_router.py | §3.1 | 双后端嵌入路由 | 已实现 | 本模块 |
| 2 | ollama_embedding.py | §3.2 | Ollama嵌入客户端 | 已实现 | 本模块 |
| 3 | ollama_chat.py | §3.3 | Ollama聊天客户端 | 已实现 | 本模块 |
| 4 | local_model_scheduler.py | §3.4 | 本地模型调度守护 | 已实现 | 本模块 |
| 5 | cache_layer.py | §3.5 | 嵌入memoization缓存 | 已实现 | 本模块 |
| 6 | __init__.py | §2 | 包入口 | 已实现 | 本模块 |

### §0.4 SSoT与责任唯一性声明

| # | 声明维度 | 本蓝图是真源 | 真源在别处（委托） | 委托目标 |
|---|---------|:----------:|:---------------:|---------|
| 1 | 嵌入路由架构（双后端+降级链） | ✅ | ❌ | — |
| 2 | Ollama HTTP API 契约 | ❌ | ✅ | runtime_config.py |
| 3 | 嵌入维度与Collection映射 | ❌ | ✅ | MOD-INF-011 blueprint §3.1 |
| 4 | BGE-M3 模型权重文件 | ✅ | ❌ | models/bge-m3/ |

### §0.5 代码目录唯一性声明

| # | 声明项 | 值 |
|---|--------|-----|
| 1 | 主代码目录 | `src/zephyr/integration/local-model/` |
| 2 | 已知副本目录 | `src/zephyr/vector_memory/`（re-export兼容层） |
| 3 | 副本处置状态 | 兼容层保留至所有消费者迁移完毕 |

## §1 设计背景与目标 {temporal_type=permanent}

| 维度 | 内容 |
|------|------|
| 核心职责 | 全系统本地模型推理基础设施——嵌入生成+LLM推理+调度+缓存 |
| 设计动机 | 1500模块规模下，嵌入模型是基础设施，不应埋在VMS内部 |
| 当前态 | EmbeddingRouter等5个文件在vector_memory/中，agent_spec/pipeline/runtime依赖VMS只为嵌入 |
| 目标态 | 独立模块，精确依赖，VMS/agent-spec/pipeline/runtime均依赖local_model |

### 1.6 差距分析

| # | 差距 | 当前态 | 目标态 | 处置 |
|---|------|--------|--------|------|
| 1 | 代码已迁移 | ✅ 完成 | — | — |
| 2 | vector_memory re-export兼容层 | 存在 | 全部消费者迁移后删除 | 等待 |
| 3 | ONNX推理优化 | PyTorch后端 | ONNX后端（2-3x加速） | 待施工 |

## §2 模块边界 {temporal_type=permanent}

| # | 包含 | 职责 |
|---|------|------|
| 1 | ✅ 包含 | 嵌入路由（BGE-M3/bge-small/Ollama双后端+降级链） |
| 2 | ✅ 包含 | Ollama HTTP API客户端（嵌入+聊天） |
| 3 | ✅ 包含 | 本地模型调度（守护线程+任务分派） |
| 4 | ✅ 包含 | 嵌入缓存（memoization） |
| 5 | ❌ 排除 | 向量存储（MOD-INF-011 VMS负责） |
| 6 | ❌ 排除 | 混合检索（MOD-INF-011 VMS负责） |
| 7 | ❌ 排除 | L3 API调用（MOD-INF-009 Pipeline负责） |

### 职责唯一性声明

| 声明项 | 无重叠模块 | 验证方式 |
|--------|-----------|---------|
| 嵌入路由 | [MOD-INF-011] | audit_registration.py |
| Ollama客户端 | [MOD-INF-011] | audit_registration.py |
| 本地模型调度 | [] | audit_registration.py |

## §3 架构设计 {temporal_type=permanent}

### 3.1 EmbeddingRouter

| 维度 | 内容 |
|------|------|
| 职责 | 双后端嵌入路由——local(SentenceTransformer)+ollama(HTTP API) |
| 路由规则 | decisions/code_context/lessons/knowledge/rules→BGE-M3(1024d)；blueprints/session_snapshots/execution_traces→bge-small(512d) |
| 降级链 | BGE-M3→bge-small-zh→InMemoryBackend(零向量) |
| 接口 | `embed(text, collection)` → `np.ndarray`；`embed_batch(texts, collection)` → `np.ndarray` |

### 3.2 OllamaEmbedder

| 维度 | 内容 |
|------|------|
| 职责 | Ollama嵌入生成客户端 |
| API | `POST http://localhost:11434/api/embed` |
| 模型 | `BGE-M3:latest` |
| 健康检查 | `quick_alive()` → `GET /api/tags` |

### 3.3 OllamaChat

| 维度 | 内容 |
|------|------|
| 职责 | Ollama聊天推理客户端 |
| API | `POST http://localhost:11434/api/chat` |
| 模型 | `qwen3:8b` |
| 用途 | task_classification/tag_completion/summary_extraction |

### 3.4 LocalModelScheduler

| 维度 | 内容 |
|------|------|
| 职责 | 本地模型调度守护线程 |
| 任务分派 | vector_embedding→EmbeddingRouter；task_classification等→OllamaChat |
| 自动初始化 | `ensure_models()` 启动时warmup |

### 3.5 CacheLayer

| 维度 | 内容 |
|------|------|
| 职责 | 嵌入memoization缓存 |
| 策略 | SHA256(text+model)→embedding |
| 存储 | 内存字典 |

### 3.6 数据流

```
消费者(agent-spec/pipeline/runtime/VMS)
  └── EmbeddingRouter.embed(text, collection)
        ├── backend=local → SentenceTransformer("models/bge-m3") → np.ndarray(1024,)
        └── backend=ollama → OllamaEmbedder → HTTP API → np.ndarray(1024,)
  └── LocalModelScheduler.dispatch(task_type, payload)
        ├── vector_embedding → EmbeddingRouter
        └── task_classification → OllamaChat
```

## §4 接口契约 {temporal_type=permanent}

### 4.1 公共API

| 类 | 方法 | 输入 | 输出 | 契约ID |
|----|------|------|------|--------|
| EmbeddingRouter | `embed(text, collection)` | str, str | np.ndarray | CT-042-001 |
| EmbeddingRouter | `embed_batch(texts, collection)` | List[str], str | np.ndarray | CT-042-002 |
| EmbeddingRouter | `warmup()` | — | None | CT-042-003 |
| OllamaEmbedder | `embed(text)` | str | np.ndarray | CT-042-004 |
| OllamaChat | `chat(prompt)` | str | str | CT-042-005 |
| LocalModelScheduler | `dispatch(task_type, payload)` | str, dict | dict | CT-042-006 |
| CacheLayer | `get(key)` / `set(key, value)` | str, np.ndarray | Optional[np.ndarray] | CT-042-007 |

### 4.2 嵌入维度映射

| Collection | 嵌入模型 | 维度 | 用途 |
|-----------|---------|:---:|------|
| decisions | BGE-M3 | 1024d | 决策记录 |
| code_context | BGE-M3 | 1024d | 代码上下文 |
| lessons | BGE-M3 | 1024d | 经验教训 |
| knowledge | BGE-M3 | 1024d | 知识条目 |
| rules | BGE-M3 | 1024d | 规则 |
| blueprints | bge-small-zh | 512d | 蓝图 |
| session_snapshots | bge-small-zh | 512d | 会话快照 |
| execution_traces | bge-small-zh | 512d | 执行轨迹 |

> ⚠️ 维度映射 SSoT 在 MOD-INF-011 blueprint §3.1。本表为只读副本，变更MUST同步。

## §5 约束条件 {temporal_type=permanent}

| # | 约束 | 值 | 原因 |
|---|------|-----|------|
| 1 | BGE-M3 模型路径 | `models/bge-m3/` | SentenceTransformer加载路径 |
| 2 | bge-small 模型路径 | `models/bge-small-zh-v1.5/` | 降级备选 |
| 3 | Ollama 默认地址 | `http://localhost:11434` | runtime_config.py |
| 4 | 嵌入缓存目录 | `data/vector_db/_embedding_cache/` | 与VMS共享 |
| 5 | 单次嵌入超时 | 30s | 防阻塞 |
| 6 | 批量嵌入最大数 | 64 | 内存保护 |

### 5.5 自动化触发机制

| 操作 | 触发方式 | 调度策略 | 当前状态 |
|------|---------|---------|---------|
| 模型warmup | auto_boot | 系统启动时 | ✅已实现 |
| 嵌入缓存命中 | on_demand | CacheLayer | ✅已实现 |
| Ollama健康检查 | auto_scheduled | 每次调用前 | ✅已实现 |
| 降级链切换 | auto_event | 模型加载失败时 | ✅已实现 |

## §6 错误处理 {temporal_type=permanent}

| # | 异常场景 | 处置 | 降级 |
|---|---------|------|------|
| 1 | BGE-M3加载失败 | 日志WARNING | 降级到bge-small |
| 2 | bge-small也失败 | 日志WARNING | 降级到InMemoryBackend(零向量) |
| 3 | Ollama不可达 | 日志WARNING | 切换到local后端 |
| 4 | 嵌入超时 | 日志ERROR | 返回零向量 |
| 5 | 模型文件损坏 | 日志ERROR | 降级到下一级 |

## §10 依赖关系 {temporal_type=permanent}

### 10.1 依赖声明

| module_id | 必须/可选 | 用途 | 契约ID | 蓝图路径 |
|-----------|:-------:|------|--------|---------|
| MOD-INF-011 | 可选 | VMS消费嵌入服务 | CT-042-001 | `docs/03_modules/_domain_knowledge/vector_memory/blueprint.md` |
| MOD-INF-009 | 可选 | Pipeline消费嵌入+rerank | CT-042-001 | `docs/03_modules/_cross_layer/pipeline/blueprint.md` |
| MOD-INF-019 | 可选 | Agent Spec语义路由 | CT-042-001 | `docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md` |

### 10.5 概念重叠声明

| # | 重叠概念 | 重叠维度 | 对方模块 | 委托关系 | 处置状态 |
|---|---------|---------|---------|---------|---------|
| 1 | 嵌入维度映射 | Collection→维度 | MOD-INF-011 | SSoT在011 | 已处置——本蓝图§4.2为只读副本 |

### 10.6 依赖链风险评级

| # | 依赖链 | 深度 | 风险等级 | 熔断机制 | 处置状态 |
|---|--------|:---:|---------|---------|---------|
| 1 | 042→无外部依赖 | 0 | L0 | 不适用 | 不适用 |

## §11 产出物存放目录 {temporal_type=permanent}

| 产出类型 | 路径 | consumer_min |
|---------|------|-------------|
| 代码 | `src/zephyr/local-model/` | agent-spec, pipeline, runtime, vector_memory |
| 测试 | `tests/` | CI |
| 模型权重 | `models/bge-m3/`, `models/bge-small-zh-v1.5/` | EmbeddingRouter |
| 缓存 | `data/vector_db/_embedding_cache/` | CacheLayer |

## §12 集成目标 {temporal_type=permanent}

| # | 集成目标 | 契约ID | 当前状态 |
|---|---------|--------|:-------:|
| 1 | MOD-INF-011 VMS | CT-042-001 | ✅已集成 |
| 2 | MOD-INF-009 Pipeline | CT-042-001 | ✅已集成 |
| 3 | MOD-INF-019 Agent Spec | CT-042-001 | ✅已集成 |
| 4 | MOD-INF-002 Runtime | CT-042-003 | ✅已集成 |

## §16 施工指引 {temporal_type=construction_temporary}

### 16.1 施工状态

| Phase | 内容 | 状态 |
|:-----:|------|:----:|
| 0 | 从MOD-INF-011拆分+代码迁移+注册 | ✅完成 |
| 1 | ONNX推理优化（2-3x加速） | 📋Backlog |
| 2 | vector_memory re-export兼容层清理 | 📋Backlog |

### 16.5 施工完成标准

| # | 标准 | 状态 |
|---|------|:----:|
| 1 | `from zephyr.local_model import EmbeddingRouter` 成功 | ✅ |
| 2 | `from zephyr.vector_memory import EmbeddingRouter` 兼容 | ✅ |
| 3 | agent_spec语义路由正常 | ✅ |
| 4 | VMS嵌入正常 | ✅ |
| 5 | 0循环依赖 | ✅ |

## §18 决策记录 {temporal_type=permanent}

| 决策ID | 决策 | 理由 | 日期 |
|--------|------|------|------|
| D-039-01 | 从MOD-INF-011拆分为独立模块 | 1500模块规模下嵌入是基础设施，不应埋在VMS | 2026-05-18 |
| D-039-02 | local后端为主，ollama为降级 | 语义路由是高频操作，不能依赖外部服务可用性 | 2026-05-18 |
| D-039-03 | 保留vector_memory re-export兼容层 | 渐进迁移，避免破坏现有消费者 | 2026-05-18 |

## 自检与闭合清单 {temporal_type=permanent}

| # | 检查项 | 状态 |
|---|--------|:----:|
| 1 | 蓝图-代码双向对齐 | ✅ |
| 2 | SSoT声明完整 | ✅ |
| 3 | 依赖声明完整 | ✅ |
| 4 | 概念重叠声明 | ✅ |
| 5 | 依赖链风险评级 | ✅ |
| 6 | 代码目录唯一性 | ✅ |
| 7 | 注册表注册 | ✅ |
| 8 | 端到端验证 | ✅ |


## Consumers
- zephyr.local_model (internal)
