---
module_id: VIEW-07-INTEGRATION-ARCH
title: Target Architecture — Integration Architecture / 目标架构：集成架构 （被恢复）
doc_type: architecture_view
status: Active
version: 1.1.0
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
valid_from: 2026-04-19
superseded_by: null
supersedes: null
related_rationale: R37
related_open_questions: []
tags:
- integration-architecture
- togaf
- integration-style
- event-driven
- acl
- interface-contract
- anti-corruption-layer
summary: TOGAF Integration Architecture 完整集成视图。描述 ZephyrAlpha 2.0 内外部系统之间的集成风格、集成拓扑、外部集成点清单（EI
  系列）、接口契约治理与 Anti-Corruption Layer 策略。本视图同时承载集成点枚举数据（v1.1.0 合并自原 integration-catalog.md）。
date: '2026-04-22'
ttl: permanent
---

## §1 Purpose / 目的

Integration Architecture（集成架构视图）回答以下问题：

1. **集成风格**：本系统在哪些场景下采用哪种集成模式（批处理 / 流式 / 请求回复 / 事件驱动 / 文件 / 共享库）？
2. **集成拓扑**：内部各层之间以及外部系统之间，谁在和谁通信？通过什么机制？
3. **接口契约治理**：接口版本如何管理？Breaking Change 如何处理？废弃政策是什么？
4. **Anti-Corruption Layer**：外部系统的数据模型如何被隔离，防止污染内部领域模型？

本视图与其他视图的分工：

| 视图 | 负责什么 |
|------|---------|
| `application_architecture.md` | 应用模块的功能职责与层次划分（what is each module）|
| `technology_architecture.md` | 技术栈、基础设施、协议选型（how is it built）|
| **本视图（integration_architecture.md）** | 模块与模块之间、系统与外部之间的**连接方式**（how do they talk）|
| `architecture_model/contracts/cross_layer_contracts.yaml` | 各接口的**契约规格**（数据结构、版本、稳定性等级）|

---

## §2 Integration Styles / 集成风格

### 2.1 六种集成风格定义

| 风格 | 特征 | 典型场景 |
|------|------|---------|
| **Batch（批处理）** | 周期性批量传输数据，延迟从分钟到小时级 | EOD 数据落盘、日终因子计算、报告生成 |
| **Streaming（流式）** | 连续/近实时的数据流传输 | 行情 tick 推送、WebSocket 实时推仓 |
| **Request-Reply（请求回复）** | 同步 / 异步 RPC 或 REST 调用 | LLM API 调用、券商 REST API、查询接口 |
| **Event-Driven（事件驱动）** | 生产者发布事件，消费者订阅响应，解耦 | 内部层间信号传递（FactorSignal → OrderSignal）|
| **File-based（文件传输）** | 通过文件（CSV / Parquet / HDF5）交换数据 | 历史数据导入导出、回测数据集共享 |
| **Shared-DB（共享数据库）** | 多个模块直接读写同一数据库/存储 | ⚠️ 慎用，仅限强一致性场景下本地 SQLite |

### 2.2 ZephyrAlpha 各集成风格采用情况

| 风格 | ZephyrAlpha 采用情况 | 落地位置 |
|------|---------------------|---------|
| Batch | ✅ 主力风格（当前阶段） | 每日 EOD 数据拉取；因子值计算批次；日报生成 |
| Streaming | 🔶 部分启用（dev 环境） | LLM Provider WebSocket；行情 WebSocket（EI-002，planned） |
| Request-Reply | ✅ 活跃使用 | LLM API（EI-003）；Feishu API（EI-004）；Broker REST（EI-001，planned）|
| Event-Driven | 🔶 内部约定，未用 MQ | 层间通过 Python 函数调用 + `shared/contracts/` 传递事件对象（轻量事件驱动）|
| File-based | ✅ 主力存储中间层 | Parquet / HDF5 存历史行情；CSV 存回测结果 |
| Shared-DB | ⚠️ 极限约束使用 | 本地 SQLite（L07 结算分析）；禁止跨层直接写 |

**当前阶段策略**：以 **Batch + File-based** 为主体（适合单人开发、量化研究阶段），Request-Reply 用于外部服务，Event-Driven 以**轻量内部协议**（Python dataclass + 函数调用）代替消息队列（MQ）——MQ 引入时机见 §6。

---

## §3 Integration Topology / 集成拓扑

### 3.1 外部系统集成拓扑

> **📊 外部集成拓扑图**：见 [`diagrams/integration_topology.mmd`](diagrams/integration_topology.mmd)

### 3.2 外部集成点清单（EI 系列）

| ID | Integration / 集成点 | Type / 类型 | Direction / 方向 | Protocol / 协议 | Status / 状态 | ACL 落盘位置 | Notes / 说明 |
|----|---------------------|------------|-----------------|----------------|--------------|-------------|-------------|
| EI-001 | Broker API / 券商 API | Trade execution / 交易执行 | Bidirectional / 双向 | REST / FIX | planned | `ex_core/adapters/` | 接入真实资金时激活 |
| EI-002 | Market data provider / 行情数据源 | Historical + realtime market data / 历史+实时行情 | Inbound / 入站 | REST / WebSocket | planned | `data/connectors/` | 首次数据接入时 |
| EI-003 | LLM providers / LLM 服务商 | AI inference / AI 推理 | Outbound / 出站 | REST (OpenAI-compatible) | in use (dev) | `frontend/` | Cursor/Trae 已接入；生产接入待 OQ-011 |
| EI-004 | Feishu / 飞书 | Notification & report distribution / 通知与报告分发 | Outbound / 出站 | REST (Feishu API) | partial | `frontend/notifications/` | 手动推送已有；自动分发 planned |
| EI-005 | Alternative data providers / 另类数据源 | Sentiment, news, events / 舆情、新闻、事件 | Inbound / 入站 | REST / file | planned | `data/connectors/` | 因子研究阶段激活 |

### 3.3 内部层间数据流（事件驱动轨迹）

量化系统的核心事件流，标注 P0 跨层数据契约 ID（CTR-001~CTR-006）作为架构承重墙：

```
MarketDataTick (raw)
    → [L00 connectors/ ACL 规范化]
    → CTR-001: NormalizedMarketData 🔒
    → [L02 Alpha Factor 计算]
    → CTR-002: FactorSignal 🔒
    → [L04 Risk Management 检查]  [L05 Portfolio Construction 优化]
    → CTR-003: RiskLimits 🔒 + CTR-004: Order 🔓
    → [L06 Trade Execution]
    → CTR-005: Fill 🔒 + CTR-006: PositionSnapshot 🔒
    → [L07 Post-Trade Analytics]
    → PnL Report / Risk Metrics
    → [L12 System Telemetry 监控]
```

**图例**：🔒 = frozen（不可变契约） | 🔓 = mutable（可变契约，含状态机）

所有层间数据对象均在 `src/zephyr/shared/contracts/` 定义（frozen dataclass），见 `architecture_model/contracts/cross_layer_contracts.yaml` 完整规格。

> **📊 跨层契约可视化图表**：
> - [`diagrams/data_flow.mmd`](diagrams/data_flow.mmd) — 核心数据流全景图（14 层体系 + CTR 标注）
> - [`diagrams/integration_topology.mmd`](diagrams/integration_topology.mmd) — 集成拓扑图（含 CTR 标注）
> - [`diagrams/c4_l2_containers.mmd`](diagrams/c4_l2_containers.mmd) — C4-L2 容器图（含 CTR 标注）

> **📊 核心业务时序图**：
> - [`diagrams/seq_order_submit.mmd`](diagrams/seq_order_submit.mmd) — 订单提交端到端时序（含幂等+ACL+熔断）
> - [`diagrams/seq_fill_received.mmd`](diagrams/seq_fill_received.mmd) — 成交回报处理时序
> - [`diagrams/seq_rebalance.mmd`](diagrams/seq_rebalance.mmd) — 组合再平衡时序
> - [`diagrams/seq_risk_trigger.mmd`](diagrams/seq_risk_trigger.mmd) — 风控触发与止损时序

---

## §4 Interface Contract Governance / 接口契约治理

### 4.1 接口版本管理

本项目采用 **Semantic Versioning（语义化版本）** 管理接口契约版本：

| 版本段 | 含义 | 触发条件 |
|--------|------|---------|
| **MAJOR（主版本）** | Breaking Change | 删字段、改字段类型、改字段名、改接口语义 |
| **MINOR（次版本）** | 向后兼容扩展 | 新增可选字段、新增可选方法 |
| **PATCH（补丁版本）** | 修复与内部优化 | 文档更新、性能优化、无接口变更 |

当前阶段所有内部契约为 `v1.0`（见 `application_architecture.md §5`），外部接入（EI-001 Broker、EI-002 行情）尚未激活。

### 4.2 Breaking Change 处理流程

```
发现需要 Breaking Change
    ↓
在 `architecture_model/contracts/cross_layer_contracts.yaml` 中标记 old_version → deprecated
    ↓
新建 new_version 接口，与旧版本共存一个 MINOR 周期（≥1 sprint）
    ↓
所有消费方完成迁移确认（checklist 见 `architecture_model/contracts/cross_layer_contracts.yaml`）
    ↓
废弃旧版本，更新 MAJOR 版本号
    ↓
在 architecture-rationale-log.md 登记理由
```

**单人开发阶段的简化原则**：当消费方仅为本项目内部模块时，Breaking Change 可以在同一 commit 中同步修改所有消费方，无需双版本共存；但必须在 commit message 中注明 "BREAKING: [契约名] v[old] → v[new]"。

### 4.3 废弃政策（Deprecation Policy）

1. 任何外部接口（EI 系列）废弃前，在本视图 §3.2 集成点清单中标记 `status: deprecated`，注明废弃时间和替代方案
2. 内部接口废弃须在 `architecture_model/contracts/cross_layer_contracts.yaml` 中标记 `stability: deprecated`
3. 废弃的接口保留至少 1 个完整的回测周期（当前为 30 天）后移除

---

## §5 Anti-Corruption Layer 策略

### 5.1 当前 ACL 落盘位置

| ACL 位置 | 隔离的外部系统 | 规范输出 |
|---------|--------------|---------|
| `data/connectors/` | 行情 Vendor（AKShare / Tushare / Wind / Bloomberg）| `NormalizedMarketData` canonical schema |
| `ex_core/adapters/` | 券商 API（Broker REST / FIX）| 内部 `Order` / `Fill` 协议 |
| `frontend/` | LLM Provider（OpenAI-compatible REST）| 内部 LLM 调用抽象 |

详细设计见 `application_architecture.md §4.1 L00 connectors/` — 已确立 ACL 的三项职责（格式隔离 / Connector 协议统一 / 格式转换在边界处）。

### 5.2 ACL 选型理由（为何不用 Adapter/Facade）

- **Adapter Pattern**：仅做接口签名转换，无法阻止内部模块直接引用外部 Vendor 的数据模型（如 tushare 的 DataFrame 字段结构）
- **Facade Pattern**：简化调用复杂度，但不防止外部 Vendor 的领域模型污染内部
- **ACL（Anti-Corruption Layer）**：在边界处将外部语义完整翻译为内部 canonical schema，内部任何层绝对不接触 Vendor 原始格式 → **防止领域污染**

### 5.3 未来 ACL 扩展计划（H8 阶段）

`application_architecture.md §4.1` 预留了 H8 阶段的 ACL 增强计划：

- Vendor Registry 统一管理（支持 Stock / ETF / Future / Option / Bond 命名空间）
- 多 Vendor 合并与去重（当同一品种有多个 Vendor 来源时）
- 数据质量断言前置（在 ACL 层完成格式检查，不让脏数据进入 L00 存储）

> **关联任务**：`architecture-finalization-taskbook.md` H8 阶段 / `open-questions-register.md` OQ-043

---

## §6 Event Backbone（Future）/ 事件总线（待规划）

**本节为占位节点（Placeholder），当前阶段不实施。**

### 触发条件（何时引入 Event Backbone）

- 系统需要支持 **实时 Tick 处理**（当前批处理已无法满足延迟要求）
- 多个消费方需要**同时订阅同一事件**，点对点调用变为扇形（fan-out）
- 引入多个**独立部署的微服务**（超出单进程/单节点范围）

### 候选技术方案（待评估）

| 方案 | 特点 | 适用场景 |
|------|------|---------|
| Redis Streams | 轻量、单机、Python 友好 | 单机 tick 缓冲、低延迟推送 |
| Apache Kafka | 高吞吐、持久化、分布式 | 多消费方、高频行情、生产级 |
| ZeroMQ | 极低延迟、无 Broker | 高频交易信号路由 |
| Python asyncio queue | 进程内、无基础设施依赖 | 当前轻量 Event-Driven 实现 |

**当前选择**：Python asyncio queue / 直接函数调用（无 MQ 基础设施），足够单人研究阶段。

> **决策记录**：本节内容将在引入 MQ 时升格为 KB 决策记录。

---

## §7 Link to Catalogs / 关联清单

| 文档 | 内容 | 关系 |
|------|------|------|
| `architecture_model/contracts/cross_layer_contracts.yaml` | 各接口的契约规格（数据结构、版本、稳定性） | 本视图 §4 的**详细数据** |
| `application_architecture.md §7` | 关键集成点叙述（应用架构视角）| 本视图的前置阅读（应用层集成意图）|
| `technology_architecture.md §5` | 集成协议与技术选型（技术架构视角）| 本视图的技术实现背景 |

---

## §8 Relationship to Other Views / 与其他视图的关系

> **📊 视图依赖关系图**：见 [`diagrams/view_dependencies.mmd`](diagrams/view_dependencies.mmd)

**视图定位说明**：
- **本视图上游**：BA（业务流驱动）/ AA（模块边界）/ DA（数据载荷）/ TA（技术协议）
- **本视图下游**：SEC（安全域需知道所有外部接入点） / OPS（运维需监控所有集成健康状态）
- **本视图不覆盖**：具体物理部署（→ TA §6）/ 安全认证机制（→ 06-SEC）/ 运维告警（→ 08-OPS）

---

## Revision History / 修订记录

| Date / 日期 | Description / 说明 |
|------------|-------------------|
| 2026-04-19 | v1.0.0：初版建立（S14-G3，批次 A）。6 种集成风格分析 + 内外部集成拓扑（Mermaid）+ 接口契约版本管理 + Breaking Change 流程 + 废弃政策 + ACL 策略（引用 03-AA J5 已落盘设计）+ Event Backbone 占位 + Catalog 关联 + 视图关系图。R37 登记理由。 |
| 2026-04-21 | v1.1.0：beta 合并 catalogs/integration-catalog.md 的 EI 系列外部集成点枚举数据至 §3.2，新增 ACL 落盘位置列；更新 summary 为"完整集成视图"；§3.2 原内部层间数据流重编号为 §3.3。 |
