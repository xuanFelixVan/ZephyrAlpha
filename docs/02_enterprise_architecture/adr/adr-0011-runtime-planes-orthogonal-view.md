---
module_id: ADR-0011
title: Runtime Planes 正交视图（Orthogonal View 方法论首次引入）
doc_type: adr
status: active
version: 1.1.0
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: agent
valid_from: 2026-04-19
superseded_by: null
supersedes: null
related_rationale:
- R69
related_open_questions:
- OQ-083
tags:
- adr
- architecture
- runtime-planes
- hot-path
- warm-path
- cold-path
- orthogonal-view
- control-plane
- execution-plane
- citadel
- jane-street
- two-sigma
- sim-to-real
summary: 采用 Runtime Planes（Hot/Warm/Cold 三平面）作为 ZephyrAlpha 2.0 **第一个正交视图（Orthogonal
  View）**，切片维度为运行时延迟 / 技术栈 / 可中断性 / 部署拓扑，**与 TOGAF 10 视图切片维度正交**（业务分层 What 做什么 × 运行平面
  How 何时以什么延迟跑）。对标 Citadel Securities / Jane Street / Two Sigma / Jump Trading / Renaissance
  五家顶级量化机构"控制面 vs 执行面物理切分"一致做法。同时首次定义**正交视图方法论**（5 条铁律 OV-P1~P5），为未来 04quater 部署拓扑
  / 04quinquies 数据生命周期 / 04sexies 故障域等候选正交视图提供标准范式。本 ADR 对应的视图文件为 `target-architecture/04bis-runtime-planes.md`
  v1.0.0 active。当前 ZephyrAlpha 处于 Warm Path only 阶段（Hot Path NOT_ACTIVATED + Cold
  Path PARTIAL_ACTIVATED），本 ADR 定义终局拓扑 + 三档激活触发器 + 跨面通信协议 + `shared/contracts/runtime_plane_tag.py`
  契约预留，为 Sim-to-Real Gap 问题和未来低延迟交易铺路，当前零代码影响。
date: '2026-04-22'
ttl: permanent
---

# ADR-0011：Runtime Planes 正交视图（Orthogonal View 方法论首次引入）

## 1. 状态（Status）

- **当前状态**：`accepted`
- **提议日期**：2026-04-19（S15-Phase1 J1 批次）
- **拍板日期**：2026-04-19（用户批准"方案 B + 选项 β + 命名 04bis"一次性拍板）
- **被谁取代**：无
- **取代了谁**：无（首次定义 Runtime Planes 正交视图方法论）

## 2. 上下文（Context）

### 2.1 触发原因

S15 Phase 1 J0-sync 交付后，用户提出 **Q1 架构拷问**："不改 14 层业务分层，专业机构的控制面 / 执行面的物理切分，是单开一层吗？如果专业机构是这么做的，我们现在能改吗？增加一层避免后面埋雷？本来现在的目标就是把架构终局全貌画出来，现在改成本最小。"

该问题精准命中 R66 09-GOV + R67 ADR-0009 v1.1.0 14 业务层锁定后的**方法论级盲点**——控制面 vs 执行面切分是业界顶级量化机构标配，但若作为第 15 业务层会污染 03-AA 14 层业务本体。

### 2.2 问题本质

**业务分层（What 做什么）与运行时特征（How 何时以什么延迟在什么硬件上跑）是两把正交尺子**：

- **业务分层**按抽象层切：L00-L13 14 层 + shared，治"做什么业务功能"（数据源 / 因子 / 信号 / 风控 / 组合 / 执行 / ...）
- **运行时特征**按延迟/技术栈/可中断性切：Hot < 10ms C++/Rust 不可中断 / Warm 10ms-1s Python async / Cold > 1s Spark/Dask batch

若强行把运行时特征塞入业务层：
- 破坏业务语义（L06 交易执行同时含 Hot 订单网关 + Warm 下单决策 + Cold 执行分析，若硬加"L-RT 实时层"会分裂 L06 业务完整性）
- 破坏 ACL / OCP / 因子注册表契约（跨层边界模糊）
- 与业界顶级机构一致做法背离（Citadel/Jane Street/Two Sigma/Jump/Renaissance 全部用正交视图切，不用业务层切）

### 2.3 业界对标证据

| 机构 | 公开资料证据 | 做法 |
|------|------------|------|
| **Citadel Securities** | Meetup talks + 官网公开架构图 | 业务分层保持完整（market data / signal / trading），另建 **Execution Plane**（C++ kernel-bypass）与 **Research Plane**（Python）两物理平面 |
| **Jane Street** | Signals & Threads podcast + OCaml 技术栈公开资料 | OCaml 函数式业务逻辑分层 + **Trading Tier**（极速 OCaml + kernel tuning）与 **Research Tier**（Jupyter + Spark）正交 |
| **Two Sigma** | Engineering blog + NeurIPS papers | 业务层按数据/模型/策略/执行分，**Research Platform**（Ray/Spark Cold）/ **Trading Platform**（Warm Python+Rust mixed）/ **Execution Gateway**（Hot C++）三平面物理切分 |
| **Jump Trading** | HFT 相关公开技术文档 + FPGA 招聘 JD | FPGA + kernel-bypass 的 **Exchange Gateway** 作为独立硬件平面，与 Strategy Research（Python Warm）+ Backtest（Cold）正交 |
| **Renaissance** | Books + public talks（有限） | Medallion Fund 的 research/execution 物理切分传闻一致（细节保密，方向对齐） |

**五家一致**：业务分层保留 + 另建运行平面正交切分。

### 2.4 ArchiMate 3.2 + TOGAF 10 方法论支持

- **ArchiMate 3.2** 明确定义 "Viewpoint" 概念，允许按不同 concerns 建多视图切片同一架构事实
- **TOGAF 10** Enterprise Continuum + Architecture Repository 支持多视图并存，不限定视图数量
- 因此，**"正交视图（Orthogonal View）"是标准方法论内建能力**，不是本项目首创概念

## 3. 决策（Decision）

### 3.1 三方案评估

| 方案 | 描述 | 优点 | 缺点 | 评分 |
|------|------|------|------|------|
| **A：新建 L14 实时层** | 在 14 层业务架构之上新增第 15 业务层 | 单尺子简单 | **破坏 14 层业务本体**；违反业界五家做法；污染 ACL/OCP；与 R67 ADR-0009 v1.1.0 冲突 | ❌ 否决 |
| **B：正交视图 04bis**（本 ADR 采纳）| 新建 `04bis-runtime-planes.md` 作为正交视图，按 Hot/Warm/Cold 切分 | 零业务决策变动；对标五家顶级；保留 TOGAF 10 视图方法论；可扩展 04quater/quinquies/sexies | 引入新方法论需团队理解"正交"概念；双标签语法成本 | ✅ **采纳** |
| **C：仅 ADR 预留注释** | 不建视图，在 ADR-0009 加预留注释 | 成本最低 | 架构终局视图缺项；未来读者看不到运行平面全貌；无法机器可读 | ❌ 否决（架构终局阶段要求全貌画出） |

### 3.2 采纳方案 B 的核心定义

**三档 Runtime Plane**：

| Plane | 延迟预算 | 技术栈 | 可中断性 | 典型场景 | 当前激活状态 |
|-------|---------|--------|---------|---------|------------|
| **HOT** | < 10ms 端到端（tick-to-trade）| C++ / Rust + kernel-bypass（DPDK / io_uring / Solarflare OpenOnload）| **不可中断**（不得调用 GC 语言 / 不得阻塞 IO / 不得 async await）| 做市报价、交易所订单网关、行情推送直连 | **NOT ACTIVATED**（T-ENDGAME 顶级机构对标阶段才激活）|
| **WARM** | 10ms - 1s | Python 3.12 + asyncio + uvloop / FastAPI + TanStack Query 前端 | 可中断（协程调度、IO-bound 任务）| 因子计算、策略推理、风控校验、API 请求响应、前端交互 | **UNIQUE ACTIVATED**（ZephyrAlpha 2.0 Warm Path only 阶段）|
| **COLD** | > 1s（批处理）| Spark / Dask / Airflow / Ray cluster + Python 批处理 | 完全可中断（任务级别重试、容错、checkpointing）| 历史回测、模型训练、特征工程批计算、合规报表生成 | **PARTIAL ACTIVATED**（少量 cron + 回测跑在 Warm 进程内同步阻塞，未来分离到独立 cluster）|

### 3.3 Hot-adjacent 特殊子类

**Hot-adjacent**（热邻接）**不是独立平面**，而是 WARM 平面下的一类特殊子类——模块本身运行在 Warm Path，但**对接** Hot Path 的下游数据。

| Hot-adjacent 典型 | 说明 |
|------------------|------|
| 前端 `trading-terminal` 行情组件 | 订阅 L08 `/ws/v1/ticker` Hot Path 推送，前端 Warm 侧需禁用 per-tick setState + Canvas/WebGL 渲染 |
| L08 `api_gateway` 订单端点 | 接收 Hot Path 下单请求，Warm 侧需 Optimistic UI + 快速路径 < 50ms 校验 |
| `data-client` WebSocket 封装 | 单连接多路复用 + 反压机制 + 断线自动重连 |

**硬约束**：浏览器 + React 技术栈**天然不满足 Hot Path 硬门槛**（< 10ms + kernel-bypass + 不可中断），前端所有低延迟需求的上限只能是 Hot-adjacent。

### 3.4 正交视图方法论 5 条铁律（OV-P1 ~ OV-P5）

| # | 铁律 | 含义 |
|---|------|------|
| **OV-P1** | 不污染业务分层本体 | 正交视图是对 TOGAF 视图的标注叠加，不替换也不新增业务层级 |
| **OV-P2** | 命名空间隔离 | 04bis / 04ter / 04quater ... 用 bis/ter/quater 后缀与 TOGAF 主序号（00-10）明确区分 |
| **OV-P3** | SSoT 单一源 | 每个正交视图是其切片维度的 canonical 真源；其他 TOGAF 视图只做引用索引 |
| **OV-P4** | 零业务决策变动 | 引入新正交视图时 TOGAF 10 视图只增加正交标注引用，不改变已有业务决策 |
| **OV-P5** | 起码对标 2 家顶级机构 | 任何新正交视图立项必须至少能对标 2 家业界先行机构公开实践；自创概念禁止入库 |

### 3.5 14 层业务 × 3 Plane 归属矩阵

详见 `04bis-runtime-planes.md §3.3` 全表。关键结论：

- **全部 14 业务层当前主力都在 Warm Path**（Python async 栈）
- **L00 数据源 + L06 交易执行 未来 Hot Path 激活优先级最高**（行情直连 + 订单网关）
- **L09 研究创新 + L11 ML 平台 未来 Cold Path 激活优先级最高**（回测 + 模型训练）
- **L10 合规 + L12 遥测 始终多平面共存**（合规快速路径 Warm + 报表批 Cold；遥测实时 Warm + 归档 Cold）

### 3.6 09-GOV Runtime 层 ≠ 04bis Runtime Plane 铁律澄清

**防漂移核心**：

| 维度 | 09-GOV Runtime 层 | 04bis Runtime Plane |
|------|-------------------|--------------------|
| **切片维度** | 治理维（Policy/Factory/Runtime 三层） | 执行维（Hot/Warm/Cold 三平面）|
| **治什么** | 运行时审计 + 反馈回写 Policy | 什么代码何时以什么延迟在什么硬件上跑 |
| **名字** | Runtime 层 | Runtime Plane |
| **冲突** | **名字都叫 Runtime 但意义完全不同** | |

**硬约束语法**：涉及双维度时必须用双标签 `[GOV:X] × [Plane:Y]` 形式（如 "D-01 AISG [GOV:Full] × [Plane:Warm-main + Hot-adjacent + Cold-factory]"），禁止单独使用"Runtime"一词避免歧义。详见 `09-governance-architecture.md §1.2bis`。

### 3.7 激活触发器三档

| 触发器 | 触发条件（任一命中） | 升级动作 |
|--------|-------------------|---------|
| **T-HOT** Hot Path 激活 | T1 真实资金 > 100 笔/天 OR T-ENDGAME 顶级对标启动 OR C++/Rust kernel-bypass PoC 通过 | ADR 升级 `HOT_PATH_ACTIVATED=True` + L00/L06 关键子模块迁移 Hot Path |
| **T-COLD-SEPARATE** Cold Path 独立 cluster | 回测作业阻塞 Warm 主事件循环 > 5s 连续 7 天 OR 训练任务 GPU 需求浮出 | 独立 Ray / Dask cluster 部署 + L09/L11 Cold 作业迁移 |
| **T-HOT-ADJACENT-UPGRADE** Hot-adjacent 强化 | 前端某组件延迟预算从 100ms 压到 50ms 连续 SLO 违约 | ADR 升级 + 前端侧硬约束强化（WebGL 渲染、单连接多路复用、反压机制）|

### 3.8 Sim-to-Real Gap 消除路径

- **Unified Contract**：`shared/contracts/runtime_plane_tag.py`（本 ADR 同步交付）
- **Champion-Challenger Shadow Validation**：Cold Path 模型训练结果在 Warm Path 影子部署，性能对齐后才切实盘
- **Replay Testing**：Cold Path 回测 + Warm Path 实盘共用同一批行情数据 replay

详见 `04bis-runtime-planes.md §6`。

### 3.9 跨面通信协议

| 通信 | 协议 | 禁止项 |
|------|------|--------|
| Hot ⟷ Warm | shared memory + lock-free ring buffer（nanomsg / ZeroMQ 零拷贝）| 禁止跨面直接同步函数调用 |
| Warm ⟷ Cold | Kafka / Redis Streams 异步队列 | 禁止 Cold 作业阻塞 Warm 主事件循环 |
| Hot ⟷ Cold | **禁止直通** | 必须经 Warm 桥接 |

### 3.10 契约预留：`shared/contracts/runtime_plane_tag.py`

本 ADR 同步交付契约预留文件，定义：

```python
class RuntimePlane(str, Enum):
    HOT = "HOT"
    WARM = "WARM"
    COLD = "COLD"

HOT_PATH_LATENCY_BUDGET_MS: Final[float] = 10.0
WARM_PATH_LATENCY_BUDGET_MS: Final[float] = 1000.0
COLD_PATH_LATENCY_BUDGET_MS: Final[float] = float("inf")
HOT_PATH_ACTIVATED: Final[bool] = False
COLD_PATH_PARTIAL_ACTIVATED: Final[bool] = True
```

**当前仅文档级标注**（模块 `__runtime_plane__` 属性 + docstring 声明），Hot Path 激活时升级为 CI 强制校验。

## 4. 影响（Consequences）

### 4.1 正面影响

- ✅ **架构终局全貌补齐**：Runtime Planes 是顶级量化机构标配，本 ADR 前 ZephyrAlpha 架构缺失这一维度，补齐后全貌完整
- ✅ **零业务决策变动**：03-AA 14 层 + 09-GOV 三层 + 10-FE 4 层 + 所有已有 ADR 不变
- ✅ **为 Sim-to-Real Gap 铺路**：Unified Contract + Champion-Challenger 三件套预留
- ✅ **为低延迟交易激活铺路**：Hot Path 三档触发器 + 跨面通信协议 + 契约预留
- ✅ **正交视图方法论首次落地**：为未来 04quater 部署拓扑 / 04quinquies 数据生命周期 / 04sexies 故障域提供范式

### 4.2 负面影响

- ⚠️ **方法论学习成本**：团队需理解"正交视图"概念（新概念引入）→ 缓解：OV-P1~P5 五条铁律 + `target-architecture/README.md §1ter` 整节方法论说明
- ⚠️ **双标签语法成本**：涉及治理维 × 执行维时需写 `[GOV:X] × [Plane:Y]`（比单标签复杂）→ 缓解：`09-governance-architecture.md §1.2bis` 强制澄清 + `04bis §7` 语法示例
- ⚠️ **"Runtime" 歧义风险**：09 视图有 Runtime 层 + 04bis 有 Runtime Plane → 缓解：禁止单独使用 "Runtime" 一词 + 必须带维度前缀

### 4.3 缓解措施

| 风险 | 缓解 |
|------|------|
| 未来新人读文档不理解正交视图 | README §1ter 方法论整节 + 每份正交视图文件顶部强制"视图性质"声明 |
| Hot Path 激活时代码改造成本 | 契约预留 `runtime_plane_tag.py` + L00/L06 子模块 Hot-adjacent 预留口（ADR-0009 v1.1.0 §3.5）|
| 正交视图通胀 | OV-P5 铁律"起码对标 2 家顶级机构" + 任何新正交视图需独立 ADR 立项 |

## 5. 落地证据（Implementation Evidence）

| 交付物 | 位置 | 状态 |
|-------|------|------|
| 正交视图文件 | `target-architecture/04bis-runtime-planes.md` v1.0.0 active | ✅ 已落盘 |
| 本 ADR | `adr/adr-0011-runtime-planes-orthogonal-view.md` v1.0.0 accepted | ✅ 已落盘 |
| 契约预留 | `src/zephyr/shared/contracts/runtime_plane_tag.py` v1.0.0 | ✅ 已落盘 |
| `__init__.py` 导出 | `src/zephyr/shared/contracts/__init__.py` | ✅ 已更新 |
| 03-AA 索引节 | `03-application-architecture.md` v1.10.0 §4.0 Runtime Plane Attribution Index | ✅ 已更新 |
| 09-GOV 边界铁律 | `09-governance-architecture.md` v1.2.0 §1.2bis + §4.5.1 D 家族 Plane 列 | ✅ 已更新 |
| 10-FE 三平面归属 | `10-frontend-architecture.md` v1.1.0 §7.5 | ✅ 已更新 |
| README 方法论 + 导航 | `target-architecture/README.md` v1.7.0 §1ter + §2 + §4 | ✅ 已更新 |
| OQ-083 即时关闭 | `open-questions/open-questions-register.md` | 🟡 J1 批次 j1-j 任务执行 |
| rationale-log | `architecture-rationale-log.md` v1.30.0 R69 | ✅ 已登记 |

## 6. 相关决策与引用

- **R69**（本 ADR 对应 rationale）
- **OQ-083**（本 ADR 同批关闭）
- **ADR-0009** v1.1.0（src 14 业务层 + shared 深化，本 ADR 不变动）
- **ADR-0010**（治理三层边界 Policy/Factory/Runtime，本 ADR §3.6 铁律澄清其 "Runtime 层" 与本 ADR "Runtime Plane" 正交）
- **R66**（09-GOV v1.0.0 落地，本 ADR 升级至 v1.2.0）
- **R67**（ADR-0009 v1.1.0 accepted，本 ADR 不冲突）
- **R70 / ADR-0012**（Capability Maturity Heatmap 正交视图第二张，本 ADR 同批次 J1 姊妹 ADR）
- **外部对标证据**：Citadel Securities / Jane Street / Two Sigma / Jump Trading / Renaissance 五家公开资料（详见 §2.3）
- **方法论基础**：ArchiMate 3.2 Viewpoint + TOGAF 10 Architecture Repository

## 6bis. 细化决策族（Refinement Cluster）

本 ADR 作为 "Vibe Coding 2.0 运行时骨架" 的**元决策**，被下列 12 条细化决策（Refinement ADRs）具体实现。这些 ADR 通过 frontmatter `refines: [ADR-0011]` 与本 ADR 建立正式关联。

> **命名历史说明（Stage F 2026-04-25 归一化）**：
> 细化决策族原使用嵌套编号 `ADR-011-001 ~ ADR-011-020`（12 个跳号子决策）。
> 经 ADR 社区扁平编号惯例（Michael Nygard / Nat Pryce / AWS / Google 一致）治理，
> **Stage F 批次**将其统一合并续号至主序列 `ADR-0030 ~ ADR-0041`，
> 关联关系改为通过 `refines` 字段表达，编号空间回归扁平。

| 新编号 | 旧编号 | 主题 |
|---|---|---|
| [ADR-0030](./adr-0030-sqlite-task-metadata-store.md) | `ADR-011-001` | SQLite 作为本地元数据存储层 |
| [ADR-0031](./adr-0031-chromadb-vector-retrieval.md) | `ADR-011-002` | ChromaDB 向量检索层（驳回 FAISS/Qdrant/Whoosh/pgvector）|
| [ADR-0032](./adr-0032-agent-orchestration-architecture.md) | `ADR-011-006` | Agent 编排架构（Router + Orchestrator + Health Monitor + 幻觉检测）|
| [ADR-0033](./adr-0033-mcp-protocol-integration.md) | `ADR-011-008` | MCP 协议在 ZephyrAlpha 的规范与集成边界 |
| [ADR-0034](./adr-0034-semi-auto-evolution-architecture.md) | `ADR-011-009` | 半自动进化架构（evolve() + 三层反馈闭环 + 五类进化信号）|
| [ADR-0035](./adr-0035-intent-parsing-three-stage.md) | `ADR-011-010` | 意图解析三阶段演进（keyword → embedding → LLM）|
| [ADR-0036](./adr-0036-deferred-queue-async-workflow.md) | `ADR-011-011` | Deferred Queue 异步工作流调度层 |
| [ADR-0037](./adr-0037-observer-event-bus.md) | `ADR-011-012` | Observer 发布订阅模式（零依赖事件总线）|
| [ADR-0038](./adr-0038-file-as-task-paradigm.md) | `ADR-011-013` | File-as-Task 范式（文件即任务最小单元）|
| [ADR-0039](./adr-0039-cove-hallucination-detection.md) | `ADR-011-018` | Chain-of-Verification 幻觉检测策略 |
| [ADR-0040](./adr-0040-pydantic-v2-structured-contracts.md) | `ADR-011-019` | AI 结构化输出契约采用 Pydantic v2 |
| [ADR-0041](./adr-0041-session-handoff-protocol.md) | `ADR-011-020` | Session Handoff Protocol（跨会话交接协议）|

**职责边界**：本 ADR（0011）定义 Runtime Planes **方法论与顶层骨架**；ADR-0030~0041 定义具体**技术选型与实现机制**。未来新增的运行时骨架细化决策（如 NATS 激活、Docker Sandbox 升级路径等）应继续以 `refines: [ADR-0011]` 关联，统一进入主编号序列，**不再使用嵌套编号**。

## 7. 修订记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-04-19 | 1.0.0 | 初版 accepted。S15-Phase1 J1 批次一次性拍板。用户选"方案 B + 选项 β + 命名 04bis"。正交视图方法论首次在本项目引入，五条铁律 OV-P1~P5 同步落地。零业务决策变动，零代码影响。6 份文件联动：新建 04bis 视图 + 本 ADR + runtime_plane_tag.py 契约 + 更新 03-AA/09-GOV/10-FE/README。|
| 2026-04-25 | 1.1.0 | **Stage F 归一化批次**：新增 §6bis 细化决策族（Refinement Cluster）整节，正式声明 ADR-0030~0041 与本 ADR 的 `refines` 关联关系。同批次事件：ADR 目录全体小写化（34 文件 rename）+ 子系列嵌套编号 `ADR-011-*`（12 个跳号）合并续号至 `ADR-0030~0041` 扁平编号 + `module_id`/`doc_id` frontmatter schema 统一 + `EA-` 前缀全体去除。零业务决策变动，仅命名空间与关联关系规整化。|
