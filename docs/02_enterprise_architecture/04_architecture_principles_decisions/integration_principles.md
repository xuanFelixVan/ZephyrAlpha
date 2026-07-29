---
module_id: VIEW-04PRINC-INTEGRATION
title: Architecture Principles — Integration / 架构原则：集成
doc_type: architecture_view
status: Active
version: 1.0.1
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
valid_from: 2026-07-19
superseded_by: null
supersedes: VIEW-07-INTEGRATION-ARCH
related_rationale: []
related_open_questions: []
tags:
- integration-principles
- togaf
- integration-style
- event-driven
- acl
- interface-contract
- anti-corruption-layer
summary: 集成架构永恒原则文档。timeless 方法论——六种集成风格定义与采用策略、内部层间数据流（CTR 契约）、接口契约治理（Semantic Versioning + Breaking Change + Deprecation）、Anti-Corruption Layer 策略、Event Backbone 触发条件。派生数据（EXT 系列 status、图表引用）不在本文档。
date: '2026-07-19'
ttl: permanent
---

# Architecture Principles — Integration
# 架构原则：集成（Integration Principles）

---

## §1 定位 / Position

本文档是**集成架构的永恒指导原则**。

**保留内容**：方法论、设计原则、不变约束——集成风格、契约治理、ACL 策略、Event Backbone 触发条件。

**不保留内容**（派生/动态数据，由各自自动化系统维护）：
- EXT 系列 status（planned/in use/partial）→ 由集成点注册表维护
- 外部集成拓扑图 → `docs/02_enterprise_architecture/target_architecture/topology_views.md`（内嵌 mermaid，手工维护）
- 接口契约规格 → `architecture_model/contracts/cross_layer_contracts.yaml`（真源）
- 当前阶段所有内部契约版本号 → 由契约文件自身维护

**与其他原则文档关系**：
- [capability_maturity_principles.md](capability_maturity_principles.md)：能力成熟度方法论
- [data_principles.md](data_principles.md)：数据架构原则
- [security_principles.md](security_principles.md)：安全架构原则
- 本文：集成架构原则（集成风格/契约治理/ACL/Event Backbone）

---

## §2 Integration Styles / 集成风格

### 2.1 六种集成风格定义（永恒分类）

| 风格 | 特征 | 典型场景 |
|------|------|---------|
| **Batch（批处理）** | 周期性批量传输数据，延迟从分钟到小时级 | EOD 数据落盘、日终因子计算、报告生成 |
| **Streaming（流式）** | 连续/近实时的数据流传输 | 行情 tick 推送、WebSocket 实时推仓 |
| **Request-Reply（请求回复）** | 同步 / 异步 RPC 或 REST 调用 | LLM API 调用、券商 REST API、查询接口 |
| **Event-Driven（事件驱动）** | 生产者发布事件，消费者订阅响应，解耦 | 内部层间信号传递（FactorSignal → OrderSignal）|
| **File-based（文件传输）** | 通过文件（CSV / Parquet / HDF5）交换数据 | 历史数据导入导出、回测数据集共享 |
| **Shared-DB（共享数据库）** | 多个模块直接读写同一数据库/存储 | ⚠️ 慎用，仅限强一致性场景下本地 SQLite |

### 2.2 集成风格采用策略（永恒原则）

**当前阶段策略**：以 **Batch + File-based** 为主体（适合单人开发、量化研究阶段），Request-Reply 用于外部服务，Event-Driven 以**轻量内部协议**（Python dataclass + 函数调用）代替消息队列（MQ）——MQ 引入时机见 §6。

**永恒约束**：
- Shared-DB 风格⚠️ 极限约束使用：仅限本地 SQLite（D_TRADING/D_REPORTING 结算分析，决策快照）；**禁止跨层直接写**
- Event-Driven 内部约定：层间通过 Python 函数调用 + `shared/contracts/` 传递事件对象（轻量事件驱动，不引入 MQ，决策快照）
- 外部服务调用统一走 Request-Reply（REST，决策快照）

---

## §3 集成拓扑 / Integration Topology

### 3.1 内部层间数据流（永恒事件驱动轨迹）

量化系统的核心事件流，标注 P0 跨层数据契约 ID（CTR-001~CTR-006）作为架构承重墙：

```
MarketDataTick (raw)
    → [D_MKT_DATA/D_DATA_ENG connectors/ ACL 规范化]
    → CTR-001: NormalizedMarketData 🔒
    → [D_FACTOR Alpha Factor 计算]
    → CTR-002: FactorSignal 🔒
    → [D_RISK 检查]  [D_PF_CORE/D_PF_ALLOC 优化]
    → CTR-003: RiskLimits 🔒 + CTR-004: Order 🔓
    → [D_EX_CORE Trade Execution]
    → CTR-005: Fill 🔒 + CTR-006: PositionSnapshot 🔒
    → [D_TRADING/D_REPORTING Post-Trade Analytics]
    → PnL Report / Risk Metrics
    → [D_INFRA_TELEMETRY 监控]
```

**图例**：🔒 = frozen（不可变契约） | 🔓 = mutable（可变契约，含状态机）

**永恒约束**：
- 所有层间数据对象均在 `src/zephyr/shared/contracts/` 定义（frozen dataclass）
- 完整契约规格见 `architecture_model/contracts/cross_layer_contracts.yaml`（真源）
- CTR-001~CTR-006 是 P0 跨层契约，任何 breaking change 必须走 §4.2 流程

### 3.2 外部集成点定义（EXT 系列，永恒 ID）

| ID | Integration / 集成点 | Type / 类型 | Direction / 方向 | Protocol / 协议 | ACL 落盘位置 |
|----|---------------------|------------|-----------------|----------------|-------------|
| EXT-001 | Broker API / 券商 API | Trade execution / 交易执行 | Bidirectional / 双向 | MiniQMT / xttrader | `ex_core/adapters/` |
| EXT-002 | Market data provider / 行情数据源 | Historical + realtime market data / 历史+实时行情 | Inbound / 入站 | REST / WebSocket | `data/implementations/` |
| EXT-003 | LLM providers / LLM 服务商 | AI inference / AI 推理 | Outbound / 出站 | REST (OpenAI-compatible) | `integration/llm_bridge.py` |
| EXT-004 | Feishu / 飞书 | Notification & report distribution / 通知与报告分发 | Outbound / 出站 | REST Webhook | `infrastructure/observability/notifier.py` |
| EXT-005 | Alternative data providers / 另类数据源 | Sentiment, news, events / 舆情、新闻、事件 | Inbound / 入站 | REST / file | `data/implementations/` |

> **注**：各 EXT 的 status（planned/in use/partial）是动态的，由集成点注册表维护，不在本文档硬编码。Protocol 与 ACL 落盘位置均为**决策快照**——Protocol 随真源 `architecture_model/contracts/cross_layer_contracts.yaml` external_contracts 演进；ACL 落盘位置反映当前代码实现（`ex_core/adapters/`、`data/implementations/`、`integration/llm_bridge.py`、`infrastructure/observability/notifier.py`）。

---

## §4 Interface Contract Governance / 接口契约治理

### 4.1 接口版本管理（永恒 Semantic Versioning）

本项目采用 **Semantic Versioning（语义化版本）** 管理接口契约版本：

| 版本段 | 含义 | 触发条件 |
|--------|------|---------|
| **MAJOR（主版本）** | Breaking Change | 删字段、改字段类型、改字段名、改接口语义 |
| **MINOR（次版本）** | 向后兼容扩展 | 新增可选字段、新增可选方法 |
| **PATCH（补丁版本）** | 修复与内部优化 | 文档更新、性能优化、无接口变更 |

### 4.2 Breaking Change 处理流程（永恒）

```
发现需要 Breaking Change
    ↓
在 `architecture_model/contracts/cross_layer_contracts.yaml` 中标记 old_version → deprecated
    ↓
新建 new_version 接口，与旧版本共存一个 MINOR 周期（≥1 sprint，决策快照）
    ↓
所有消费方完成迁移确认（checklist 见契约文件）
    ↓
废弃旧版本，更新 MAJOR 版本号
    ↓
建立 KB 决策记录（KBG 系列）并更新 `architecture_model/contracts/cross_layer_contracts.yaml` 的 schema_version
```

**单人开发阶段的简化原则**（决策快照：随团队规模演进）：当消费方仅为本项目内部模块时，Breaking Change 可以在同一 commit 中同步修改所有消费方，无需双版本共存；但必须在 commit message 中注明 `BREAKING: [契约名] v[old] → v[new]`。

### 4.3 废弃政策（Deprecation Policy，永恒）

1. 任何外部接口（EXT 系列）废弃前，在集成点注册表中标记 `status: deprecated`，注明废弃时间和替代方案
2. 内部接口废弃须在 `architecture_model/contracts/cross_layer_contracts.yaml` 中标记 `stability: deprecated`
3. 废弃的接口保留至少 1 个完整的回测周期（当前为 30 天，决策快照；真源见 `architecture_model/contracts/cross_layer_contracts.yaml` deprecation_flow）后移除

---

## §5 Anti-Corruption Layer 策略

### 5.1 ACL 落盘位置（永恒）

| ACL 位置 | 隔离的外部系统 | 规范输出 |
|---------|--------------|---------|
| `data/implementations/` | 行情 Vendor（AKShare / Baostock / Tushare / TDX / iFinD / MiniQMT）| `NormalizedMarketData` canonical schema |
| `ex_core/adapters/` | 券商 API（MiniQMT / xttrader）| 内部 `Order` / `Fill` 协议 |
| `integration/llm_bridge.py` | LLM Provider（OpenAI-compatible REST）| 内部 LLM 调用抽象 |

### 5.2 ACL 选型理由（永恒——为何不用 Adapter/Facade）

- **Adapter Pattern**：仅做接口签名转换，无法阻止内部模块直接引用外部 Vendor 的数据模型（如 tushare 的 DataFrame 字段结构）
- **Facade Pattern**：简化调用复杂度，但不防止外部 Vendor 的领域模型污染内部
- **ACL（Anti-Corruption Layer）**：在边界处将外部语义完整翻译为内部 canonical schema，内部任何层绝对不接触 Vendor 原始格式 → **防止领域污染**

### 5.3 ACL 核心职责（永恒）

1. **格式隔离**：外部 Vendor 原始格式不进入内部
2. **Connector 协议统一**：多 Vendor 统一为内部 canonical schema
3. **格式转换在边界处**：转换发生在 ACL 层，不在内部模块
4. **数据质量断言前置**：入站数据在 ACL 层完成质量门禁（不让脏数据进入存储）

---

## §6 Event Backbone 触发条件（永恒——何时引入 MQ）

**当前阶段不实施 Event Backbone**（决策快照），使用 Python asyncio queue / 直接函数调用（无 MQ 基础设施）。

### 触发条件（满足任一即应评估引入）

1. 系统需要支持 **实时 Tick 处理**（当前批处理已无法满足延迟要求）
2. 多个消费方需要**同时订阅同一事件**，点对点调用变为扇形（fan-out）
3. 引入多个**独立部署的微服务**（超出单进程/单节点范围）

### 候选技术方案（决策快照，待 MQ 引入时评估）

| 方案 | 特点 | 适用场景 |
|------|------|---------|
| Redis Streams | 轻量、单机、Python 友好 | 单机 tick 缓冲、低延迟推送 |
| Apache Kafka | 高吞吐、持久化、分布式 | 多消费方、高频行情、生产级 |
| ZeroMQ | 极低延迟、无 Broker | 高频交易信号路由 |
| Python asyncio queue | 进程内、无基础设施依赖 | 当前轻量 Event-Driven 实现 |

---

## §7 视图边界 / Boundaries

### 7.1 本文档覆盖

- 六种集成风格定义与采用策略（§2）
- 内部层间数据流与 CTR 契约（§3.1）
- 外部集成点 EXT 系列定义（§3.2，不含 status）
- 接口契约治理（Semantic Versioning + Breaking Change + Deprecation）（§4）
- Anti-Corruption Layer 策略（§5）
- Event Backbone 触发条件（§6）

### 7.2 本文档不覆盖（由其他系统维护）

| 内容 | 真源 |
|------|------|
| 接口契约规格（数据结构、版本、稳定性） | `architecture_model/contracts/cross_layer_contracts.yaml` |
| EXT 系列 status（planned/in use） | 集成点注册表（自动维护） |
| 外部集成拓扑图 | `docs/02_enterprise_architecture/target_architecture/topology_views.md`（内嵌 mermaid，手工维护） |
| 集成协议与技术选型 | `technology_principles.md` |
| 安全认证机制 | `security_principles.md` |
| 运维告警 | `operations_principles.md` |

### 7.3 视图定位

- **本视图上游**：BA（业务流驱动）/ AA（模块边界）/ DA（数据载荷）/ TA（技术协议）
- **本视图下游**：SEC（安全域需知道所有外部接入点）/ OPS（运维需监控所有集成健康状态）

---