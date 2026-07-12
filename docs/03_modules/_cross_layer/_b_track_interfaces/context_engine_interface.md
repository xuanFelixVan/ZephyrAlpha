---
module_id: MOD-CONTEXT_ENGINE
title: Context Engine Interface / 上下文引擎接口规范
doc_type: architecture_view
status: Active
version: "1.0.2"
layer: L1_foundation
owner: ZephyrAlpha-Owner
classification: internal
language: zh
created_by: Claude-Opus-4.7
created_date: "2026-04-24"
last_updated: "2026-05-06"
ttl: permanent
template_source: "vector_memory-service-interface.md v1.2.0 (B-a-1 定稿模板)"
truth_source:
  - "03_modules/_cross_layer/context_engine/blueprint.md（MOD-CONTEXT_ENGINE — 详细设计与 CT 锚点；Phase 5 真源）"
  - "architecture_model/layers/b_context_engine.yaml（Context Engine YAML SSoT）"
supersedes:
  - "docs/03_modules/_cross_layer/_b_track_interfaces/context-interface-contract.md (will archive in B-b)"
related_kb:
  - "KBG-0015 Context Engine 架构与技术选型（pending B-e）"
integration_points:
  - "Vector Memory Service (upstream, 主数据源)"
  - "Agent Orchestrator (downstream consumer)"
  - "Feedback Loop Engine (upstream signal, adjust strategy)"
  - "MCP Servers (Cursor / Trae / Claude-Desktop) - 注入通道"
tags:
  - context_engine
  - mcp
  - entity-graph
  - rrf-retrieval
  - vibe-coding-infrastructure
depends_on:
  - target: AI-ENG-VMS-001
    at: "§3"
    why: "Vector Memory Service — 上下文数据主源"
mod_master_blueprint: "MOD-MASTER_BLUEPRINT"
mod_master_contracts:
  - "CT-ORC-CE-001"
  - "CT-CE-VMS-001"
  - "CT-CE-LSG-001"
responsibility_domain: 
design_maturity: design
build_status: planned
---

# Context Engine Interface / 上下文引擎接口规范

> **定位**：Vibe Coding 2.0 基础设施五大核心服务之一。AI 编码的"中枢神经"——接收任务请求，从 VMS / entity-graph / 源码目录三源汇聚上下文，压缩到 token budget 内，注入到 MCP 通道让 AI IDE 消费。
>

---

## 0. 读者指南

### 0.1 本文档是什么

| 章节 | 内容 | 主要读者 |
|:-:|------|---------|
| §1 | 服务定位与实施策略（Protocol 抽象基类） | 架构师 |
| §2 | 技术选型表 | 架构师、运维 |
| §3 | 核心数据模型（ContextRequest / ContextBundle / Slot） | 开发者 |
| §4 | API 设计（`build/compress/validate/inject` 四段 + `adjust_strategy` 反馈入口） | 集成方 |
| §5 | MCP 通道能力矩阵与兼容策略（Cursor / Trae / Claude-Desktop） | 集成方 |
| §6 | 前置条件与依赖 | 开发者 |
| §7 | 文件清单与落位 | 开发者 |
| §8 | 集成点 | 架构师 |
| §9 | 渐进路线 | 所有人 |
| §10 | 错误码与降级策略（DEGRADE-001~003） | 集成方 |
| §11 | 性能 SLO（含冷启动） | 运维 |
| §12 | 测试用例（P0） | 开发者、QA |
| §13 | 修订记录 | 所有人 |

### 0.2 本文档**不是**

- ❌ **VMS 使用教程**——见 `vector_memory-service-interface.md`
- ❌ **MCP 协议规范**——见 Anthropic MCP 官方文档（https://modelcontextprotocol.io）
- ❌ **具体 Prompt 模板库**——见 `prompt_templates/`（experimental 产物，另出）
- ❌ **Agent 任务状态机**——见 `agent_orchestrator_interface.md`（B-a-3）
- ❌ **IDE 插件开发手册**——本规范只描述 Context Engine 如何注入，不描述 IDE 如何渲染
- ❌ **生产部署运维手册**——beta+ 服务化时另出 SRE 文档

---

## 1. 服务定位与实施策略

### 1.1 缺口 → 原因 → 解法

**缺口**：AI Agent 执行任务时，或者上下文爆炸（token 超限、延迟飙升、hallucination 增加），或者上下文饥饿（找不到相关 KB 决策记录/接口/教训），两难症导致编码质量不稳定。

**原因**：
1. 老方案让人工维护 `context-spec.md` 预拼上下文——规模一旦超过 10 个任务就不可维护
2. Prompt 拼接没有 token budget 概念，超限靠截断，关键信息反而被裁掉
3. MCP 协议三家 IDE 能力不一（Cursor 支持 tools、Trae 侧重 resources、Claude-Desktop 强 prompts），老方案用单一通道导致部分 IDE 只能降级
4. 没有闭环反馈——某类上下文（例如 `lessons`）经常不被 AI 使用就该降权，但无机制

**解法**：
- **build-compress-validate-inject 四段流水**——每段可独立度量与替换
- **entity-graph + VMS + 文件系统三源**——结构化依赖 + 语义检索 + 精确兜底
- **MCP 能力矩阵**——探测 IDE 能力后多路注入，不支持的能力降级到 `prompts` 单通道
- **Feedback Loop 反馈通道（Protocol 引用）**——异常信号驱动策略调参

### 1.2 职责边界

| Yes | No |
|-----|----|
| ✅ 接收 `ContextRequest` 构建 `ContextBundle` | ❌ 决定"任务是什么"（Orchestrator 职责） |
| ✅ 调 VMS `multi_search` 做语义检索 | ❌ 向量入库（VMS 职责） |
| ✅ 维护 entity-graph（代码依赖 / 任务依赖 / 文档引用） | ❌ 持久化知识内容（VMS 职责） |
| ✅ 本地 LLM / 规则压缩到 token budget | ❌ 跑主力 Agent（Orchestrator + 外部 LLM 职责） |
| ✅ 按 IDE 能力注入 MCP 通道 | ❌ 定义 MCP 协议本身 |
| ✅ 接收 Feedback Loop 异常信号调整策略 | ❌ 异常检测（Feedback Loop 职责） |

### 1.3 实施策略：Protocol + 双实现（库化优先，按需服务化）

```python
# src/zephyr/infrastructure/runtime_integration/a2a_protocol/governance/protocol.py (experimental 产出)

from typing import Protocol, Literal

class ContextEngineProtocol(Protocol):
    """业务层永远依赖此 Protocol。"""

    async def build(self, request: ContextRequest) -> ContextBundle: ...
    async def compress(self, bundle: ContextBundle, token_budget: int) -> ContextBundle: ...
    async def validate(self, bundle: ContextBundle) -> ValidationReport: ...
    async def inject(self, bundle: ContextBundle, channel: IDEChannel) -> InjectResult: ...

    # 反馈通道（遗漏 #5）—— Feedback Loop Engine 用 FeedbackAction Protocol 调用此接口
    async def adjust_strategy(self, task_id: str, signal: FeedbackSignal) -> AdjustResult: ...

    # 辅助
    async def probe_ide_capabilities(self, ide_id: str) -> IDECapabilities: ...
    async def stats(self) -> CEStats: ...

class InProcessContextEngine:
    """experimental（当前目标）：进程内调用，直接依赖 VectorMemoryProtocol + NetworkX。"""

class RemoteContextEngine:
    """beta+（按需启用）：HTTP/gRPC Client。"""
```

| Phase | 实施形态 | 运行方式 | 触发升级条件 |
|:-:|---------|---------|-------------|
| **experimental** | **`InProcessContextEngine`（Python 库，当前目标）** | `from zephyr.context_engine import get_ce` | - |
| beta | `RemoteContextEngine`（HTTP 服务） | `POST /v1/*` FastAPI | ≥1 触发：① 多 IDE 实例并发 build ≥ 3；② entity-graph > 10k 节点不宜多进程加载 |
| stable | gRPC | 按需 | RPS > 200 |

**所有 API 均为 `async`**。进程内锁用 `asyncio.Lock`（事件循环友好），跨进程锁用 `filelock.FileLock`。**严禁 `threading.Lock`**。

---

## 2. 技术选型表（真源锁定）

| 组件 | 首选 | 备选 | 不推荐 | 选型理由 | 升级触发 | 相关 KB 决策记录 |
|------|----------------|------|-------|---------|---------|----------|
| entity-graph 存储 | **NetworkX + JSON** | Neo4j 社区版 | Neptune / Dgraph | 纯 Python、节点 < 10k 场景内存足够 | 节点 > 10k 或需多进程共享 | KBG-0015 |
| 向量检索入口 | **VMS `multi_search`（ChromaDB 后端）** | - | 直接调 ChromaDB（破坏分层） | 分层合约，VMS 降级时本层自动感知 | - | KBG-0015 / 0016 |
| 文本压缩引擎 | **本地 LLM (llama.cpp + Qwen2.5-3B-Instruct)** | 规则-based 摘要（fallback） | OpenAI API（外部依赖） | 零外部依赖，Qwen2.5-3B 中文摘要够用 | 压缩质量不足 → Qwen2.5-7B | KBG-0015 |
| 压缩降级 | **规则-based 摘要（LLM 挂时自动启用）** | 简单截断 | 丢弃 | LLM 挂也能产可用上下文 | - | KBG-0015 |
| token 计数 | **tiktoken（cl100k_base）** | transformers 本地 tokenizer | 字符数粗估 | tiktoken 对 GPT / Claude 近似度高 | 目标模型非 OpenAI/Anthropic 系时换 transformers | - |
| MCP 通道路由 | **能力矩阵 + 多通道并发注入** | 单 prompts 通道 | 硬编码 Cursor | 三家 IDE 能力不一，能力探测后按需注入 | 新增 IDE 直接加一行矩阵 | KBG-0015 |
| 进程内并发 | **`asyncio.Lock`** | - | `threading.Lock`（阻塞事件循环） | 项目全异步栈 | 服务化后废除 | - |
| 跨进程并发 | **`filelock.FileLock`** | - | 全局单例 | pytest 并发 + 多 Agent | 服务化后废除 | - |

---

## 3. 核心数据模型

### 3.1 Slot 概念（上下文槽位）

`ContextBundle` 不是一个扁平 prompt 串，而是**按语义分槽**的结构化容器。MCP 注入时按通道能力分发到不同槽位。

| Slot | 含义 | 典型内容来源 | 默认 token 预算占比 |
|------|------|-------------|---------------------|
| `task_spec` | 任务本身规格 | task card yaml 渲染 | 10% |
| `architecture` | 架构决策 / KB 决策记录 / 接口契约 | VMS `decisions` collection | 25% |
| `code_refs` | 相关代码片段 / blueprints | VMS `code_context` + 文件系统兜底 | 30% |
| `task_history` | 历史相似任务执行记录 | VMS `task_history` | 15% |
| `lessons` | 经验教训 / 反模式 | VMS `lessons` | 10% |
| `runtime_state` | 运行时上下文（分支名、失败的 CI、最近 commit） | git + 运行时状态 | 5% |
| `guardrails` | 规则与约束 | `.cursor/rules/*` + `AGENTS.md` 片段 | 5% |

预算占比可被 `FeedbackSignal` 动态调整（例如 `lessons` 长期低命中 → 降至 5%，腾给 `code_refs`）。

### 3.2 IDE 能力矩阵

```python
# src/zephyr/orchestration/context_management/ide_capabilities.py (experimental 产出)

from enum import Enum

class IDEChannel(str, Enum):
    TOOLS = "tools"
    RESOURCES = "resources"
    PROMPTS = "prompts"
    SAMPLING = "sampling"

class IDEID(str, Enum):
    CURSOR = "cursor"
    TRAE = "trae"
    CLAUDE_DESKTOP = "claude_desktop"
    GENERIC_MCP = "generic_mcp"

# 遗漏 #4 补充：三家 IDE MCP 兼容矩阵（基于 2026-04 主流版本实测）
IDE_CAPABILITY_MATRIX: dict[IDEID, dict[IDEChannel, str]] = {
    IDEID.CURSOR: {
        IDEChannel.TOOLS:     "full",       # Cursor 主力通道，AI 主动调用
        IDEChannel.RESOURCES: "read_only",  # 可读但不主动订阅更新
        IDEChannel.PROMPTS:   "full",       # system prompt 注入
        IDEChannel.SAMPLING:  "experimental",
    },
    IDEID.TRAE: {
        IDEChannel.TOOLS:     "partial",    # 支持有限 tool schema
        IDEChannel.RESOURCES: "full",       # Trae 主力通道，强资源感知
        IDEChannel.PROMPTS:   "full",
        IDEChannel.SAMPLING:  "none",
    },
    IDEID.CLAUDE_DESKTOP: {
        IDEChannel.TOOLS:     "full",
        IDEChannel.RESOURCES: "full",
        IDEChannel.PROMPTS:   "full",       # Claude-Desktop 强 prompts
        IDEChannel.SAMPLING:  "full",
    },
    IDEID.GENERIC_MCP: {
        IDEChannel.TOOLS:     "unknown",
        IDEChannel.RESOURCES: "unknown",
        IDEChannel.PROMPTS:   "full",       # 最小公倍数兜底
        IDEChannel.SAMPLING:  "unknown",
    },
}

# 通道能力级别：
#   full         - 完全支持，注入首选
#   partial      - 部分支持，注入时需降级 schema
#   read_only    - 只读不订阅，静态资源 OK
#   experimental - 实验性，可选注入
#   none / unknown - 不支持，必须降级
```

### 3.3 Pydantic Schemas

```python
# src/zephyr/integration/shared/schema/schemas.py (experimental 产出)

from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime

class ContextRequest(BaseModel):
    task_id: str
    task_kind: Literal["feature", "refactor", "bugfix", "review", "architecture", "research"]
    target_files: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    token_budget: int = Field(default=16000, ge=2000, le=200000)
    ide_id: IDEID = IDEID.GENERIC_MCP
    slot_overrides: dict[str, float] | None = Field(
        default=None,
        description="动态覆盖默认 slot 预算占比，如 {'code_refs': 0.45, 'lessons': 0.05}")

class SlotContent(BaseModel):
    slot: str
    items: list[dict]
    token_count: int
    source_traces: list[str] = Field(description="可追溯源，如 ['vms://decisions/KBG-0016', 'file://src/...']")
    degraded_sources: list[str] = Field(default_factory=list, description="本 slot 遇到的降级源")

class ContextBundle(BaseModel):
    request_id: str
    task_id: str
    slots: dict[str, SlotContent]
    total_token_count: int
    token_budget: int
    compression_ratio: Optional[float] = None
    built_at: datetime
    bundle_hash: str = Field(description="sha256(序列化 slots)，用于 inject 幂等")
    degraded: bool = Field(default=False, description="任一 slot 触发降级则为 True")
    degrade_reasons: list[str] = Field(default_factory=list)

class ValidationReport(BaseModel):
    passed: bool
    token_within_budget: bool
    all_citations_resolvable: bool
    no_stale_references: bool
    violations: list[str] = Field(default_factory=list)

class InjectResult(BaseModel):
    channels_used: list[IDEChannel]
    channels_skipped: list[tuple[IDEChannel, str]] = Field(description="[(channel, skip_reason)]")
    injected_at: datetime
    ack_received: bool

# 遗漏 #5：Feedback Loop → Context Engine 反馈通道 schema
class FeedbackSignal(BaseModel):
    task_id: str
    anomaly_type: Literal[
        "hallucination_spike",        # 幻觉率飙升
        "test_failure_pattern",       # 测试失败模式
        "irrelevant_context_cited",   # 引用了不相关上下文
        "context_insufficient",       # 上下文不足反复追问
        "token_overflow",             # 实际调用时 token 超限
    ]
    confidence: float = Field(ge=0.0, le=1.0)
    suggested_action: Literal[
        "downweight_slot",            # 降权某 slot
        "upweight_slot",              # 升权某 slot
        "invalidate_cache",           # 失效缓存
        "switch_compression_strategy", # 切换压缩策略
    ]
    target_slot: Optional[str] = None
    adjustment_magnitude: float = Field(default=0.1, description="权重调整幅度，0.1 = ±10%")
    observed_at: datetime

class AdjustResult(BaseModel):
    applied: bool
    new_slot_budgets: dict[str, float]
    effective_from: datetime
    ttl_minutes: int = Field(default=60, description="调整生效时长，到期回默认")
```

---

## 4. API 设计

### 4.1 Python 库 API（experimental 主用，`InProcessContextEngine`）

```python
# src/zephyr/orchestration/context_management/in_process.py (experimental 产出)

class InProcessContextEngine:  # implements ContextEngineProtocol
    """所有方法均为 async。依赖 VectorMemoryProtocol + NetworkX + tiktoken + llama.cpp。"""

    def __init__(
        self,
        config: CEConfig,
        vm: VectorMemoryProtocol,          # 从 get_vm() 注入
        entity_graph_path: str,
    ) -> None: ...

    # ───── 主流水（build → compress → validate → inject）─────
    async def build(self, request: ContextRequest) -> ContextBundle:
        """
        从三源汇聚：
          1. VMS multi_search（merge_strategy='rrf'）拉 decisions/code_context/task_history/lessons
          2. NetworkX entity-graph 查 target_files 的直接依赖节点（深度 ≤ 2）
          3. 文件系统兜底：VMS 降级时用 rg/grep 按 tags/target_files 检索（DEGRADE-001）
        按 slot_overrides 或默认比例分配 token 预算。
        """

    async def compress(
        self,
        bundle: ContextBundle,
        token_budget: int,
        strategy: Literal["llm_summary", "rule_based", "truncate"] = "llm_summary",
    ) -> ContextBundle:
        """
        压缩到 token_budget 以内：
          - 'llm_summary'：本地 Qwen2.5-3B 分 slot 摘要（首选）
          - 'rule_based'：按优先级 + 首尾 N 行 + 去 boilerplate（LLM 挂时降级）
          - 'truncate'：简单截断（最后降级）
        保留 source_traces 完整性，不丢引用链。
        """

    async def validate(self, bundle: ContextBundle) -> ValidationReport:
        """
        验证：
          - token_count ≤ budget
          - 所有 source_traces 可解析（vms:// 可 get_by_id，file:// 存在）
          - 无 stale references（超过 updated_at 阈值的 KB 决策记录 标 stale）
        失败时 violations 列出具体原因，不修正。
        """

    async def inject(
        self,
        bundle: ContextBundle,
        ide_id: IDEID,
    ) -> InjectResult:
        """
        按 IDE_CAPABILITY_MATRIX 多通道注入：
          - slot 'task_spec' / 'runtime_state' → prompts（所有 IDE full）
          - slot 'code_refs' / 'architecture' → resources（Trae/Claude-Desktop full，Cursor read_only）
          - slot 'guardrails' → tools schema descriptions（Cursor/Claude-Desktop full，Trae partial）
        不支持的通道自动降级到 prompts 单通道，InjectResult.channels_skipped 记录原因。
        """

    # ───── 反馈通道（遗漏 #5 补充）─────
    async def adjust_strategy(
        self,
        task_id: str,
        signal: FeedbackSignal,
    ) -> AdjustResult:
        """
        Feedback Loop Engine 的 FeedbackAction Protocol 调用此接口。
        不硬编码依赖 FLE，只接收符合 FeedbackSignal schema 的信号。
        调整在 ttl_minutes 内生效，到期自动回默认权重。
        """

    # ───── 辅助 ─────
    async def probe_ide_capabilities(self, ide_id: str) -> IDECapabilities:
        """
        运行时探测 IDE 能力（查 MCP initialize handshake 的 capabilities 字段）。
        探测失败回退到 IDE_CAPABILITY_MATRIX 静态值。
        """

    async def stats(self) -> CEStats: ...
    async def clear_cache(self, task_id: str | None = None) -> None: ...
```

### 4.2 HTTP API（beta 按需启用，预留骨架）

| Method + Path | 对应库方法 |
|---------------|-----------|
| `POST /v1/context/build` | `build()` |
| `POST /v1/context/compress` | `compress()` |
| `POST /v1/context/validate` | `validate()` |
| `POST /v1/context/inject` | `inject()` |
| `POST /v1/context/adjust_strategy` | `adjust_strategy()` |
| `GET /v1/context/ide_capabilities/{ide_id}` | `probe_ide_capabilities()` |
| `GET /v1/stats` | `stats()` |

---

## 5. MCP 通道能力矩阵与兼容策略（遗漏 #4 重点章节）

### 5.1 为什么需要矩阵

老方案假设所有 IDE 都支持"prompt 注入"单一通道，但 MCP 协议演进后：

- **Cursor**：偏 tools-centric，Agent 主动 `tools/call`，resources 只读不订阅
- **Trae**：偏 resources-centric，强资源订阅与实时更新，tools 支持有限
- **Claude-Desktop**：全通道都强，特别是 prompts 和 sampling
- **其他 MCP 兼容 IDE**：能力未知，必须探测

单通道注入会导致：Cursor 下 `resources` 没效果；Trae 下 `tools` 注入被忽略。

### 5.2 路由策略

```
slot 优先级 = 内容价值密度 × 通道稳定性
```

| Slot | Cursor 首选 | Trae 首选 | Claude-Desktop 首选 | 通用 fallback |
|------|------------|----------|---------------------|---------------|
| `task_spec` | prompts | prompts | prompts | prompts |
| `architecture` | tools (read KB 决策记录 tool) | resources (adr-graph) | resources + prompts | prompts |
| `code_refs` | resources (read_only) | resources | resources | prompts（截断到 2000 tok） |
| `task_history` | prompts | resources | prompts | prompts |
| `lessons` | prompts | prompts | prompts | prompts |
| `runtime_state` | prompts | resources (live) | resources | prompts |
| `guardrails` | tools schema | prompts | tools schema | prompts |

### 5.3 降级路径

```
IDE 能力未知 / 探测失败
  → 回落到 IDE_CAPABILITY_MATRIX 静态表
    → 若静态表也 unknown
      → 全部 slot 串入 prompts 单通道
        → 若 prompts 超 token budget
          → 触发 compress(strategy='rule_based') 再串入
            → 若仍超
              → 丢低优先级 slot（lessons → runtime_state → task_history）
                → 返回 InjectResult.ack_received=False + 记录降级日志
```

---

## 6. 前置条件与依赖

### 6.1 前置组件（必须先完成）

| 前置项 | 状态 | 所在任务 |
|-------|:----:|---------|
| `src/zephyr/vector_memory/` 包 | ⏳ 待建 | VMS experimental T-1-XX |
| `src/zephyr/context_engine/` 包创建 | ⏳ 待建 | experimental T-1-XX |
| Qwen2.5-3B-Instruct GGUF 下载到 `.models/qwen2.5-3b/` | ⏳ 待建 | experimental T-1-XX |
| llama.cpp Python 绑定（`llama-cpp-python`） | ⏳ 待建 | experimental T-1-XX |
| KBG-0015 批准 | ⏳ pending | B-e 阶段 |

### 6.2 Python 依赖

```toml
[project.optional-dependencies]
context_engine = [
    "networkx>=3.2,<4.0",
    "llama-cpp-python>=0.2.70",
    "tiktoken>=0.6",
    "filelock>=3.13",
    "pydantic>=2.5,<3.0",
]
```

### 6.3 运行时依赖

- **Vector Memory Service**（必须，通过 Protocol）
- **MCP Server 实现**（下游消费，beta 重构 `knowledge_base_server.py`）
- **Feedback Loop Engine**（可选，通过 Protocol 单向推送 `FeedbackSignal`）

---

## 7. 文件清单与落位（不留 placeholder）

```

├── src/zephyr/
│   ├── context_engine/                             # ⏳ experimental 新建
│   │   ├── __init__.py                             # 导出 get_ce() 工厂
│   │   ├── protocol.py                             # ContextEngineProtocol 抽象
│   │   ├── in_process.py                           # experimental 实现
│   │   ├── remote.py                               # beta+ 占位
│   │   ├── schemas.py                              # Pydantic schemas（§3.3）
│   │   ├── ide_capabilities.py                     # IDE_CAPABILITY_MATRIX（§3.2）
│   │   ├── builders/
│   │   │   ├── vms_builder.py                      # 调用 VMS multi_search
│   │   │   ├── entity_graph_builder.py             # NetworkX 查询
│   │   │   └── filesystem_fallback.py              # rg/grep DEGRADE-001 fallback
│   │   ├── compressors/
│   │   │   ├── llm_summary.py                      # llama.cpp + Qwen2.5-3B
│   │   │   ├── rule_based.py                       # 规则压缩（LLM 降级时用）
│   │   │   └── truncate.py                         # 最后降级
│   │   ├── injectors/
│   │   │   ├── router.py                           # 按能力矩阵路由
│   │   │   ├── prompts_channel.py
│   │   │   ├── resources_channel.py
│   │   │   └── tools_channel.py
│   │   ├── validators.py
│   │   ├── entity_graph.py                         # NetworkX 加载 + 查询 + 增量更新
│   │   └── config.py                               # CEConfig
│   └── config/
│       └── context_engine.yaml                     # ⏳ 新建
│
├── .runtime/
│   ├── context_engine/
│   │   ├── entity_graph.json                       # NetworkX 持久化
│   │   ├── cache/                                  # build 结果缓存（bundle_hash key）
│   │   └── adjust_state.json                       # adjust_strategy 动态权重状态
│   └── logs/
│       ├── ce_degrade.log                          # DEGRADE-001/002/003 触发日志
│       └── ce_feedback.log                         # adjust_strategy 审计
│
├── .models/
│   └── qwen2.5-3b/                                 # GGUF (~2GB)
│
├── tests/
│   ├── test_build.py
│   ├── test_compress_llm.py
│   ├── test_compress_rule_based.py
│   ├── test_validate.py
│   ├── test_inject_cursor.py
│   ├── test_inject_trae.py
│   ├── test_inject_claude_desktop.py
│   ├── test_adjust_strategy.py
│   ├── test_cold_start.py
│   └── test_degrade_paths.py
│
└── .gitignore                                      # 已追加 .runtime/ + .models/
```

---

## 8. 集成点

### 8.1 上游依赖

| 上游 | 关系 | 调用 |
|------|------|------|
| **VMS**（主数据源） | 必须 | `await vm.multi_search(query, [decisions, code_context, task_history, lessons], merge_strategy='rrf')` |
| NetworkX entity-graph | 必须 | 本地加载 `.runtime/context_engine/entity_graph.json` |
| **Feedback Loop Engine** | 可选（通过 Protocol） | FLE 调 `await ce.adjust_strategy(task_id, signal)` |
| 文件系统（降级源） | 必须（DEGRADE-001） | `rg`/`grep` 在项目根扫描 |

### 8.2 下游消费者

| 下游 | 关系 | 调用姿态 |
|------|------|---------|
| **Agent Orchestrator**（主消费者） | 必须 | 执行任务前 `bundle = await ce.build(req); await ce.inject(bundle, ide)` |
| MCP Server `knowledge_base_server.py` | beta 重构 | MCP 工具暴露 `/context/build` 给 IDE 主动查询 |
| Dashboard `context_overview.py` | 可选 | `await ce.stats()` 可视化 |

### 8.3 Feedback Loop 单向依赖（Protocol 引用，不硬编码）

```python
# src/zephyr/observability/feedback_loop/actions.py（FLE 侧，不在本文档实现）

from typing import Protocol

class ContextAdjustAction(Protocol):
    """FLE 只知道这个 Protocol，不 import ContextEngine 具体实现。"""
    async def adjust_strategy(self, task_id: str, signal: FeedbackSignal) -> AdjustResult: ...

# 注入时：
#   fle = FeedbackLoopEngine(context_adjust=get_ce())
```

**为什么用 Protocol**：避免 FLE → CE 的硬编码 import 形成循环依赖（CE 未来可能也订阅 FLE 的 metrics 作为 `runtime_state` 输入）。

---

## 9. 渐进路线

| Phase | 范围 | 验收标准 |
|:-:|------|---------|
| **scaffold**（当前） | 接口规范定稿 | KBG-0015 Active + 本规范 Active |
| **experimental** | `InProcessContextEngine` 实现 + 默认权重 + Cursor 注入 | ① §12 P0 用例通过<br>② build 端到端 ≤ 1.5s（VMS 稳态）<br>③ Cursor 下 inject 成功率 ≥ 99% |
| **beta** | Trae / Claude-Desktop 通道适配 + Feedback Loop 接入 | 多 IDE 切换零重写 + `adjust_strategy` 动态生效 |
| **beta** | 服务化 `RemoteContextEngine` | 多 IDE 实例并发 build ≥ 3 时触发 |
| **stable** | 自适应 slot 预算（强化学习） | Feedback 数据量 > 10k 次 |

---

## 10. 错误码与降级策略

### 10.1 异常层级

```python
class CEError(Exception): ...                        # 基类
class CEConfigError(CEError): ...                    # 配置 / 模型路径错误
class CEVMSError(CEError): ...                       # VMS 调用失败（通常 catch 后降级）
class CECompressionError(CEError): ...               # LLM 压缩失败
class CEValidationError(CEError): ...                # validate() 失败（不影响 build 成功）
class CEInjectionError(CEError): ...                 # inject() 彻底失败
class CEDegradedError(CEError): ...                  # 降级标记用，通常不抛
```

### 10.2 P0 级降级条款（3 条）

> **核心原则**：Context Engine 是 AI 编码的"中枢"，挂了整个 Vibe Coding 系统瘫痪——因此降级必须优雅，**宁可上下文粗糙，也不能阻塞**。

**DEGRADE-001：VMS 不可用时降级到文件系统**

触发场景：
- VMS `multi_search` 返回 `degraded=True`
- VMS 完全无法连接（beta+ HTTP 模式）
- ChromaDB 持久化文件损坏

降级动作：

```python
vms_result = await vm.multi_search(query, collections)
if vms_result.degraded:
    # 降级到 filesystem_fallback.py
    fs_hits = await rg_search(
        pattern=derive_regex(request.tags + request.target_files),
        scopes=["docs/02_enterprise_architecture", "src/", "docs/03_modules/_domain_infrastructure_runtime/task_system/changes"],
        max_results_per_slot=20,
    )
    bundle.degraded = True
    bundle.degrade_reasons.append("DEGRADE-001: VMS unavailable, fs_fallback used")
    # 继续走 compress / validate / inject 流水
```

**调用方强制契约**：上游（Orchestrator）必须检查 `bundle.degraded`，在 `lessons` 槽缺失时不追究——不阻塞任务启动。

**DEGRADE-002：本地 LLM 压缩失败时降级到规则压缩**

触发场景：
- Qwen2.5-3B 模型未下载 / 加载失败
- llama.cpp OOM
- 压缩超时（> 3s）

降级动作：

```python
try:
    compressed = await self._compress_with_llm(bundle, budget)
except (CECompressionError, asyncio.TimeoutError):
    compressed = await self._compress_with_rules(bundle, budget)
    compressed.degrade_reasons.append("DEGRADE-002: LLM compress fallback to rule_based")
    if compressed.total_token_count > budget:
        compressed = await self._compress_with_truncate(compressed, budget)
        compressed.degrade_reasons.append("DEGRADE-002b: rule_based still over budget, truncated")
```

**DEGRADE-003：MCP 通道全部不可用时降级到纯 prompts 单通道 + 丢 slot**

触发场景：
- IDE 能力探测全 `none` / `unknown`
- `resources` / `tools` 注入超时或被 IDE 拒绝

降级动作：

```
按优先级保留 slot：task_spec > architecture > code_refs > guardrails > runtime_state > task_history > lessons
    全部串入 prompts，超 budget 时按反向优先级丢弃最低优先级 slot，直到塞得下
    InjectResult.channels_used = [PROMPTS], channels_skipped 记录被丢 slot 及原因
```

**上游强制契约**：Orchestrator 检查 `InjectResult.ack_received`，False 时允许降级重试但不阻塞任务（超时后放行执行）。

### 10.3 降级条件速查表

| 触发条件 | 降级动作 | 上游感知 |
|---------|---------|---------|
| VMS degraded=True | fs 兜底，bundle.degraded=True | **DEGRADE-001** |
| Qwen2.5-3B 加载失败 | 规则压缩 | **DEGRADE-002** |
| 压缩仍超 budget | 简单截断 | **DEGRADE-002b** |
| IDE 能力未知 | 静态矩阵 | 透明，无需上游处理 |
| MCP `resources`/`tools` 通道失败 | 降级到 prompts | **DEGRADE-003** |
| prompts 超 budget | 丢低优先级 slot | **DEGRADE-003b** |
| entity-graph 加载失败 | 跳过依赖图槽，仍能跑 | 日志告警，不阻塞 |

所有降级必须写入 `logs/ce_degrade.log`（结构化 JSON：触发原因 / 时间戳 / task_id / 降级码）。

---

## 11. 性能 SLO

### 11.1 稳态 SLO（experimental，VMS 健康前提下）

| 指标 | 目标 | 测试条件 |
|------|------|---------|
| `build()` p50 | ≤ 1500 ms | token_budget=16000，4 个 Collection 各 top_k=5 |
| `build()` p95 | ≤ 3000 ms | 同上 |
| `compress()` LLM p50 | ≤ 800 ms | 输入 24k 压到 16k |
| `compress()` LLM p95 | ≤ 2000 ms | 同上 |
| `compress()` 规则降级 p95 | ≤ 100 ms | 纯规则压缩 |
| `validate()` p95 | ≤ 50 ms | 缓存内源解析 |
| `inject()` p95 | ≤ 300 ms | 多通道并发 |
| `adjust_strategy()` p95 | ≤ 20 ms | 本地状态写入 |
| 端到端（build+compress+validate+inject） p50 | ≤ 2500 ms | - |
| 端到端 p95 | ≤ 5000 ms | - |

### 11.2 冷启动 SLO（每天开电脑第一次启动）

| 指标 | 目标 | 说明 |
|------|------|------|
| 进程 import 耗时 | ≤ 2 s | 仅 import `zephyr.context_engine` |
| entity-graph 加载 | ≤ 1 s | NetworkX 从 JSON 反序列化（节点 < 5k） |
| Qwen2.5-3B 首次加载 | ≤ 8 s | llama.cpp 加载 GGUF（懒加载，首次 compress 触发） |
| 首次 `build()` 延迟 | ≤ 3 s | 含 VMS 冷启动 + entity-graph 加载 |
| 首次端到端（含 LLM 首次加载） | ≤ 12 s | - |
| **总冷启动到首次可用** | **≤ 10 s**（不含 LLM 首次加载）/ **≤ 18 s**（含） | 约定 Qwen 懒加载，首次 build 不走 LLM 压缩 |

**冷启动优化要求**：
- Qwen2.5-3B 懒加载（首次 compress 才触发，首次 build 走规则压缩）
- entity-graph 懒加载（首次 build 需要时才读）
- 启动完成写 `logs/ce_startup.log`

---

## 12. 测试用例（P0，experimental 必须通过）

### 12.1 Build P0

| # | 用例 | 前置 | 动作 | 预期 |
|:-:|------|------|------|------|
| P0-B1 | 四源合并基本通路 | VMS 有数据 + entity-graph 存在 | `await ce.build(request)` | slots 7 个非空，total_tokens ≤ budget×1.3（未压缩） |
| P0-B2 | slot_overrides 生效 | 同上 | request.slot_overrides={'code_refs':0.5} | code_refs.token_count/total ≈ 0.5 ±5% |
| P0-B3 | VMS degraded 降级 | mock VMS 返回 degraded=True | build | bundle.degraded=True，fs_fallback 激活（DEGRADE-001） |
| P0-B4 | entity-graph 缺失不阻塞 | 删除 entity_graph.json | build | 相关 slot 空但不抛异常，其他 slot 正常 |

### 12.2 Compress P0

| # | 用例 | 前置 | 动作 | 预期 |
|:-:|------|------|------|------|
| P0-C1 | LLM 压缩正常 | Qwen2.5-3B 加载成功 | compress(bundle, 8000, 'llm_summary') | total_tokens ≤ 8000，source_traces 不丢 |
| P0-C2 | LLM 失败降级规则 | mock llama.cpp 抛异常 | compress | 自动用 rule_based，degrade_reasons 记录 DEGRADE-002 |
| P0-C3 | 规则仍超 budget 降级截断 | 设置极小 budget=500 | compress | 自动 truncate，degrade_reasons 有 DEGRADE-002b |
| P0-C4 | 压缩比报告正确 | 输入 24k | compress(..., 8000) | compression_ratio ≈ 8000/24000 |

### 12.3 Validate & Inject P0

| # | 用例 | 前置 | 动作 | 预期 |
|:-:|------|------|------|------|
| P0-V1 | token 超 budget 时 violations | 手构造超限 bundle | validate | passed=False, violations 含 "token_overflow" |
| P0-V2 | stale reference 检测 | bundle 含 30 天前 KB 决策记录 source_trace | validate | violations 含 "stale_reference:..." |
| P0-I1 | Cursor 多通道注入 | ide_id=CURSOR | inject | channels_used 含 prompts + tools + resources |
| P0-I2 | Trae 偏 resources | ide_id=TRAE | inject | channels_used 优先 resources + prompts |
| P0-I3 | Claude-Desktop 全通道 | ide_id=CLAUDE_DESKTOP | inject | channels_used 含 prompts + tools + resources + sampling |
| P0-I4 | 未知 IDE 兜底 prompts | ide_id=GENERIC_MCP | inject | channels_used=[PROMPTS]，channels_skipped 含未支持通道 |
| P0-I5 | 所有通道失败 DEGRADE-003 | mock 所有 channel 注入失败 | inject | ack_received=False，自动丢低优先级 slot |

### 12.4 Adjust Strategy P0（遗漏 #5）

| # | 用例 | 前置 | 动作 | 预期 |
|:-:|------|------|------|------|
| P0-A1 | downweight_slot 生效 | 默认权重 lessons=0.1 | adjust(signal downweight lessons magnitude 0.05) | 新权重 lessons=0.05，ttl 60min |
| P0-A2 | ttl 到期回默认 | 上一步后 | sleep(ttl+1)，再 build | lessons 权重回 0.1 |
| P0-A3 | 总预算守恒 | 任意 signal | adjust | Σ slot_budgets = 1.0 ±0.001（其他 slot 按比例吸收） |
| P0-A4 | 审计日志落盘 | 任意 adjust | 检查 `logs/ce_feedback.log` | 含 task_id/signal/effective_from/new_budgets |

### 12.5 冷启动 P0（§11.2 对应）

| # | 用例 | 前置 | 动作 | 预期 |
|:-:|------|------|------|------|
| P0-S1 | 冷启动 import ≤ 2s | 清 Python 缓存 | `import zephyr.context_engine` | ≤ 2s |
| P0-S2 | Qwen 懒加载 | 冷启动后 | 仅 build 不 compress | Qwen 未加载（内存 < 500MB） |
| P0-S3 | 总冷启动端到端 ≤ 10s（不含 LLM） | VMS 已 warmup | 首次 build+validate+inject（规则压缩） | ≤ 10s |

### 12.6 降级路径 P0

| # | 用例 | 前置 | 动作 | 预期 |
|:-:|------|------|------|------|
| P0-D1 | DEGRADE-001 触发 | mock VMS degraded | build | fs_fallback 激活，ce_degrade.log 记录 |
| P0-D2 | DEGRADE-002 触发 | 删除 Qwen 模型 | compress | 规则降级，ce_degrade.log 记录 |
| P0-D3 | DEGRADE-003 触发 | mock 所有 MCP 通道失败 | inject | 降级 prompts + 丢 slot，ce_degrade.log 记录 |

---

## 13. 修订记录

| 日期 | 版本 | 说明 |
|------|:-:|------|
| 2026-05-05 | 1.0.2 | 蓝图 v0.4.1 第三轮同步。新增 7 项深水区盲点已补齐（context poisoning OWASP ASI06 / compressor hallucination validator / memory echo detector / context curator "less docs same tokens" / relevance validator 门槛过滤 / active memory CRUD / typed memory router）。蓝图完整度 93→100/100（25项盲点全覆盖）。本接口规范在 experimental 施工前需与蓝图 v0.4.1 重新对轨——尤其 attention: poison_detect/compressor_validate/relevance_threshold 三条新增流水线节点在接口侧尚无对应 slot。 |
| 2026-04-24 | 1.0.0 | 初版（B-a-2）。基于 VMS v1.2 模板。重点：① §5 MCP 能力矩阵（遗漏 #4）解决 Cursor/Trae/Claude-Desktop 差异；② §4.1 `adjust_strategy` + §3.3 `FeedbackSignal`（遗漏 #5）通过 Protocol 单向依赖接收 FLE 反馈；③ 三条 P0 降级 DEGRADE-001~003。 |
