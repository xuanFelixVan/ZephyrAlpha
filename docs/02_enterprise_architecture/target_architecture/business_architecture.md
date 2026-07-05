---
module_id: VIEW-01-BUSINESS-ARCH
title: Target Architecture — Business Architecture / 目标架构：业务架构
doc_type: architecture_view
status: Active
version: 2.0.0
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
valid_from: 2026-04-17
superseded_by: null
supersedes: null
related_rationale: R29, R30, R41, R42, R43, R59
related_open_questions:
- OQ-063
tags:
- business-architecture
- togaf
- ba
- capability-map
- value-stream-map
- vsm
- nfr
- slo
- sli
summary: TOGAF Business Architecture 视图。v2.0.0：全面重写对齐53域架构——能力地图从C01-C10→C1-C7+CC1-CC3映射53域，VSM/SLO更新路径引用，删除过时的RACI矩阵/人机协同5铁律/抽屉映射/修订记录。回答：为谁服务、核心业务能力、端到端流程、NFR。
date: '2026-07-04'
ttl: permanent
---

## 1. Purpose of this view / 本视图的用途

The Business Architecture answers:

业务架构视图回答：

- **What** capabilities does the business need? (Business Capability Map / 业务能力地图)
- **How** does core value flow? (End-to-end process / 端到端流程)
- **What** are the non-functional requirements? (NFR / 非功能需求)
- **What** are the constraints? (Policies & limits / 政策与红线)

This view **drives** the Information Architecture (what to document), which drives the Application Architecture (what to build), which drives the Technology Architecture (what stack to use).

本视图**驱动**信息架构（需要记录什么），信息架构驱动应用架构（需要构建什么），应用架构驱动技术架构（需要什么技术栈）。

> **v2.0.0 变更**：原 §2 Stakeholder RACI 矩阵（12类利益相关者×18活动）和 §2.3 人机协同5铁律已删除——当前单人开发阶段，RACI 矩阵的 A/R 全部落在同一个人，维护终局态矩阵无实际价值且是污染源。未来引入合伙人/AI Operators 时从 git 历史恢复重建。原 §3 的 docs/ 抽屉映射（08~17编号）已全部失效（docs/ 重组为01/02/03三层+53域），重写为 C1-C7+CC1-CC3 → 53域映射。

---

## 2. Stakeholders / 利益相关者（当前阶段简述）

当前阶段：**单人开发 + AI 协作**（Cursor/Trae 双 IDE）。所有业务角色（架构师/研究员/交易员/风控/合规/数据工程/SRE）物理上由同一人承担。

**AI 协作者职责边界**：仅限 Consulted（提供候选方案、文档草稿、红队质疑），不承担 R/A（Responsible/Accountable）。AI 产出必须由人签字承接才落盘。

**未来扩展口**：
- S9 AI Operators（自治 Agent）—— 接口预留于 `src/zephyr/` 对应域的 `_ai_operator/` 命名空间，激活条件见 [architecture_principles.md](../04_architecture_principles_decisions/architecture_principles.md)
- S11 合伙人 / S12 监管 —— 激活时需重建完整 RACI 矩阵（git 历史可恢复 v1.2.0 版本）

> **详细 RACI 矩阵**（12类Stakeholder×18活动）已删除，git 历史可查（v1.2.0, commit 69fa51dc12~1）。

---

## 3. Business Capability Map / 业务能力地图

ZephyrAlpha 2.0 是**量化投资全生命周期管理系统**，覆盖：数据 → 研究 → 模型 → 策略 → 执行 → 报告。

当前能力域体系为 **C1-C7（7个业务能力域）+ CC1-CC3（3个横切能力域）= 10个**，映射到53域。真源在 [capability_heatmap.yaml](../../../architecture_model/cross_cutting/capability_heatmap.yaml) v3.0.1。

### 3.1 业务能力域（C1-C7）

| ID | 能力域 | 说明 | 主要域（53域） | 蓝图位置 |
|---|---|---|---|---|
| **C1** | 数据能力 | 市场数据接入、质量门禁、PIT、survivorship、血缘追踪 | D_MKT_DATA, D_ALT_DATA, D_DATA_ENG | [`_domain_data/`](../../03_modules/_domain_data/) |
| **C2** | 因子&信号能力 | Alpha因子、情绪、信号提取、因子注册表、IC-IR | D_FACTOR, D_SIGLEGACY, D_FUNDAMENTAL_SIGNAL, D_ASHARE_SIGNAL, D_SIGQC | [`_domain_factor/`](../../03_modules/_domain_factor/), [`_domain_signal/`](../../03_modules/_domain_signal/) |
| **C3** | 风控能力 | 事前/事中/事后风控、VaR-CVaR、限额、止损 | D_RISK | [`_domain_risk/`](../../03_modules/_domain_risk/) |
| **C4** | 组合构建能力 | 优化、再平衡、回测、战略配置、meta-router | D_PF_CORE, D_PF_ALLOC, D_CROSS_ASSET | [`_domain_portfolio_core/`](../../03_modules/_domain_portfolio_core/), [`_domain_backtest/`](../../03_modules/_domain_backtest/) |
| **C5** | 执行&交易后能力 | OMS、SOR、执行、归因、TCA、review | D_EX_CORE, D_EX_SOR, D_TRADING, D_POSITION | [`_domain_execution_core/`](../../03_modules/_domain_execution_core/) |
| **C6** | ML/AI平台能力 | 模型生命周期、训练、serving、scout、实验 | D_ML_TRAIN, D_ML_SERVE | [`_domain_machine_learning_train/`](../../03_modules/_domain_machine_learning_train/) |
| **C7** | 治理&合规能力 | 合规运行时、治理三层、AISG、审计链 | D_COMPLIANCE, D_GOVERNANCE, D_GOV_RULE, D_GOV_AUDIT, D_GOV_DRIFT | [`_domain_compliance/`](../../03_modules/_domain_compliance/), [`_domain_governance/`](../../03_modules/_domain_governance/) |

### 3.2 横切能力域（CC1-CC3）

| ID | 能力域 | 说明 | 主要域 | 蓝图位置 |
|---|---|---|---|---|
| **CC1** | 人机交互&研究 | Human-AI接口、研究notebook、CLI | D_FRONTEND | [`_domain_frontend/`](../../03_modules/_domain_frontend/) |
| **CC2** | 可观测性 | Metrics、logs、traces、ai_behavior | D_OPS | [`_domain_infrastructure_operations/`](../../03_modules/_domain_infrastructure_operations/) |
| **CC3** | AI自治 | D家族系统、ai_operator预留口、决策引擎 | D_AUTONOMY_CORE, D_AUTONOMY_PERM | [`_domain_autonomy_core/`](../../03_modules/_domain_autonomy_core/), [`_domain_autonomy_perm/`](../../03_modules/_domain_autonomy_perm/) |

### 3.3 能力成熟度

> 能力成熟度热力图（53域×10能力域矩阵，L0-L5五档）真源在 [capability_heatmap.yaml](../../../architecture_model/cross_cutting/capability_heatmap.yaml)，可视化见 [global_capability_heatmap.md](../01_global_architecture_diagram/global_capability_heatmap.md)（自动派生）。

当前整体成熟度：**L1（Designed）**，整体评分 1.12。架构蓝图已95%锁定，代码施工刚起步。

---

## 4. End-to-end core process — Value Stream Map / 端到端核心业务流程（价值流图）

本节把 §3 的能力域（C1-C7）落到**时间维度 + 交接维度 + 浪费维度**的 Value Stream Map（VSM，精益/TOGAF 核心构件）。

### 4.1 Canonical value stream / 标准价值流

> **📊 业务价值流图**：见 [`diagrams/business_value_stream.mmd`](diagrams/business_value_stream.mmd)

**图例**：
- **LT**（Lead Time）= 工件从到达工序到离开工序的**总耗时**（含等待）
- **PT**（Process Time）= 实际**增值加工**时间（不含等待）
- **%C&A**（Complete & Accurate）= 下游第一次接收就**可用且正确**的比例

### 4.2 Stage-level metrics / 阶段级指标表

| 阶段 | 能力域 | 核心工件 | Lead Time | Process Time | %C&A | 主要延迟来源 |
|------|--------|---------|----------|-------------|------|-----------|
| ① Data Ingest | C1 | 原始tick/bar + reference data | EOD T+1 | 10-30 min | 98% | iFinD推送延迟、PIT三字段校验 |
| ② Factor Research | C2 | 因子假设 + 特征工程 | 5-20 天 | 2-8 小时 | 70% | 想法→验证的探索回合、PIT数据整备 |
| ② Factor Library | C2 | 因子入库 + 质量断言 | 15-60 min | 10-30 min | 98% | PIT三字段校验、五类质量断言 |
| ③ Model Train/Deploy | C6 | 模型 + 部署manifest | 2-24 小时 | 30 min-4 h | 95% | GPU排队、超参搜索 |
| ③ Signal Generation | C2 | 信号payload | 15-60 min | 5-15 min | 98% | 因子刷新依赖、下游订阅对齐 |
| ④ Portfolio Construction | C4 | 目标仓位 | 5-15 min | 1-5 min | 99% | 约束求解器收敛 |
| ④ Pre-trade Risk | C3 | 风控审批结果 | <1 min | 5-30 s | 99.9% | 限额查询、手工复核（ad-hoc）|
| ⑤ Order Submission | C5 | broker ACK | 1-5 min | 10-60 s | 99.5% | 券商API网络、幂等校验 |
| ⑤ Fill & Reconcile | C5 | 成交单 + 对账记录 | intraday | 1-5 min | 99% | 成交回报到齐、T+0/T+1对账窗口 |
| ⑥ Attribution | C5 | PnL + 归因报告 | T+1 | 10-30 min | 99% | 日终结算数据到齐 |
| ⑦ Feedback loop | C2+C7 | 研究结论 / KB决策候选 | T+1 ~ T+5 | 1-4 h | 85% | 人工复盘、AI辅助分析往返 |

> **注**：LT/PT 数字基于当前"非 HFT、daily/hourly batch"定位（见 §5 NFR）。若未来激活 intraday 高频（触发条件：portfolio ≥ $10M + 接入 L1 行情），本表需整体向秒级压缩重写。

### 4.3 Key handoffs / 关键交接点

Handoff 是 VSM 中最易产生**信息损失 + 责任真空 + 数据污染**的点，必须显式标注契约。

| # | Handoff | 上游 → 下游 | 交接物 | 风险 | 治理手段 |
|---|---------|------------|-------|------|---------|
| **HO-1** | **Vendor → Data Lake**（市场数据入仓）| C1 | 原始tick/bar/reference data | 字段漂移、survivorship、迟到数据覆盖历史 | ACL + PIT三字段（见 [data_architecture.md §4](./data_architecture.md)）+ immutable append |
| **HO-2** | **Research → Factor Library**（研究→生产）| C2 | 因子代码 + metadata + 断言 | 研究环境灰带代码进生产、look-ahead bias | ACL隔离 + fitness functions + 三断言 |
| **HO-3** | **Signal → Pre-trade Risk**（信号→风控）| C2→C3 | signal payload + metadata | 信号绕过风控、限额不同步 | 强制性Pre-trade gate + Idempotency Key |
| **HO-4** | **Portfolio → Broker**（组合→券商）| C4→C5 | 委托单 + client_order_id | **订单重发重复**（量化红线）| 幂等设计 + broker ACK回执持久化 |
| **HO-5** | **Fill → Attribution / Feedback**（成交→归因→研究）| C5→C2 | 成交记录 + PnL分解 + 结论 | 反馈断链（归因洞察没回到因子库）| Decision log + 知识库沉淀 |

### 4.4 Bottlenecks & waste / 瓶颈与浪费点

按精益七大浪费（等待/返工/过度加工/传输/库存/动作/缺陷）识别：

| # | 类型 | 瓶颈/浪费 | 影响阶段 | 当前状况 | 改进方向 |
|---|------|------------|---------|---------|--------------------------------|
| **B1** | **等待** | 市场数据上游窗口（iFinD EOD推送延迟）| ① ② ⑥ | 单Vendor单链路；无备份源 | 接入AKShare/Tushare作fallback |
| **B2** | **等待** | 回测任务排队（单机资源）| ② | `backtest TAT p95 ≤ 30min`（§5 SLO-4）可能超时 | 引入job queue / Airflow |
| **B3** | **等待/返工** | 合规审批（当前手工兜底）| ④ ⑤ ⑦ | 手工，无规则引擎 | C7激活后引入policy-as-code |
| **B4** | **返工** | 因子重算（PIT一致性失败触发全量回补）| ② | fitness function拦截后回补是返工 | 增量回补（只回补被corporate action污染的partition）|
| **B5** | **传输/动作** | 人-AI协作往返在⑦反馈回路占LT 60%+ | ⑦ | 每次AI协作round-trip 15-60 min | Session治理 + prompt资产库沉淀复用 |
| **B6** | **缺陷** | 信号失效未及时发现（factor decay / concept drift）| ② ③ ⑥ | 归因只T+1看结果，drift监控缺失 | champion-challenger在线对照 |

### 4.5 Cross-cutting governance / 横向治理贯穿全链

- C7 治理&合规域 — Policy control + KB决策链 + AI Operator registry（预留）
- C3 风控域 — 每阶段的风险控制策略（pre/in/post-trade）
- CC1 人机交互域 — 协作知识沉淀（AI会话上下文、prompt资产）
- C2 知识管理（D_KNOWLEDGE域）— 因子库/策略库/经验教训

---

## 5. Non-functional requirements (NFR) / 非功能需求

### 5.1 Qualitative NFR summary / 定性 NFR 概览

定位原则（**先立边界再定数字**）：

- **Non-HFT 定位**：不追求微秒/毫秒级；延迟单位为**秒/分钟/小时**。若未来接入L1行情或组合≥$10M，NFR整体需重写。
- **市场时段 vs 非市场时段分层**：可用性/延迟SLO只在**市场时段（含盘前盘后30min缓冲）**严格执行；非市场时段为best-effort。
- **可审计 ≫ 可用性**：当前阶段（单人无外部用户）若可用性与可审计冲突，必须选可审计。

| 类别 | 要求 | 当前阶段目标 |
|------|------|------|
| **Latency / 延迟** | Non-HFT；秒级—分钟级batch；端到端signal→order ≤ 90s（p99）| 不追求微秒级 |
| **Availability / 可用性** | 市场时段99.9% / 非市场时段best-effort | 单人操作，非24/7 |
| **Auditability / 可审计性** | Full decision trail, immutable KB决策, 七维度decision logs | **高优先级**（不可降）|
| **Compliance / 合规性** | Personal-scale；future multi-investor triggers stricter | 当前最简，留扩展口 |
| **Maintainability / 可维护性** | Single operator + AI collab；docs-as-code | 高优先级 |
| **Security / 安全性** | Personal scale；密钥管理、无公开暴露 | 见 [security_architecture.md](./security_architecture.md) |
| **Data Quality / 数据质量** | PIT/survivorship/lineage三断言；完整度/一致性/及时性三维度 | 高优先级（因子与回测可信度的前置）|

### 5.2 SLA / SLO / SLI matrix / 服务等级矩阵

> **术语铁律**：**SLA**=对外承诺（当前单人，无外部合同→大部分标"internal commitment"）。**SLO**=内部目标（可量化）。**SLI**=实际测量指标（可落到metric）。
>
> **测量/上报位置**：所有SLI接入可观测性架构（当前占位，由CC2可观测性域填充，用OpenTelemetry Metrics/Logs/Traces三支柱）。

| # | SLO名称 | 定义与场景 | Target（量化目标） | SLI测量方法 | 违约后果 |
|---|---------|-----------|-------------------|-----------|---------|
| **SLO-1** | **Data Freshness** 数据新鲜度 | 市场时段行情从vendor发布到数据湖可查询的端到端延迟 | 分钟级bar：p50≤15s / p95≤60s / p99≤180s<br/>日度结算：T+1 **11:00 UTC+8**前100%到齐 | `ts_ingest − vendor_release_ts`差值；见 [data_architecture.md §4](./data_architecture.md) PIT三字段 | 触发B1降级 + 阻塞因子刷新（SLO-5）|
| **SLO-2** | **Signal Generation Latency** 信号生成延迟 | 市场数据进入→信号payload发布的端到端p99 | p50≤30s / p95≤60s / p99≤**90s**<br/>EOD策略：p95≤**10min** | OTel分布式trace：`span=signal_generation` | 超限则信号标记`stale=true`，下游降级处理 |
| **SLO-3** | **Order Submission Latency** 下单延迟 | 从信号发布（含pre-trade risk gate）到券商ACK的p99 | p50≤5s / p95≤15s / p99≤**30s** | OTel span：`span=order_submit`；Idempotency Key命中率 | 超限则kill-switch触发，已下订单走幂等回执 |
| **SLO-4** | **Backtest Turnaround** 回测周转TAT | 常规回测（单策略×5年日频全市场）提交到结果可用 | 常规：p50≤10min / p95≤**30min** / p99≤60min<br/>重度：p95≤**4h** | Job执行时长metric：`backtest_duration_seconds{type}` | 触发B2降级，考虑并行调度器 |
| **SLO-5** | **Factor Refresh Window** 因子刷新窗口 | 日度因子与分钟因子的刷新时效 | 日度：EOD T日18:00 + **90min**内100%刷新<br/>分钟（滚动）：每**5min**刷新，p99≤**5min** | `factor_refresh_duration_seconds{cadence,factor_id}` | 下游信号标记`factor_stale=true`；连续2窗口失败告警 |
| **SLO-6** | **System Availability** 系统可用性 | 核心链路在市场时段的月可用性 | 市场时段：**99.9%/month**（≤43.2min停机）<br/>非市场时段：best-effort | Blackbox probe每30s ping核心端点 | 超限触发incident review + KB决策 |
| **SLO-7** | **Data Quality** 数据质量 | PIT/survivorship/lineage三断言 + 完整度/一致性/及时性 | 完整度≥**99.5%** / 一致性≥**99.9%**<br/>F21-F25 fitness functions：**100% pass** | Great Expectations/Soda断言；pytest fitness pass ratio | 任何断言失败阻塞因子上线（HO-2 gate）|
| **SLO-Audit** | **Auditability** 可审计性 | KB决策链完整、AI协作决策日志七维度覆盖 | KB决策append-only：100%<br/>AI决策日志七维度覆盖率：≥**99%**<br/>Git commit→KB决策双向索引：100% | pre-commit hook + CI audit + decision log schema validation | **0容忍**：任何违约阻塞merge |

### 5.3 SLA vs SLO — current phase reality / 当前阶段的SLA现实

| 对手方 | 是否有真实SLA | 说明 |
|-------|-------------|------|
| **iFinD（Vendor）** | ✅ 有合同SLA | 由供应商承诺可用性/限流/字段稳定 |
| **未来合伙人** | ❌ 无（未激活）| 激活后SLO-6/SLO-7需转对外SLA |
| **监管方** | ❌ 无商业SLA（有合规时限）| 监管激活后，合规报告时限转硬性SLA |
| **内部** | ❌ 无（单人）| 当前所有SLO都是"对自己的承诺"，性质接近OKR |

### 5.4 升级触发与 revision trigger / SLO 重写触发条件

以下任一条件触发本表**整体重写**（非局部调整）：

1. 接入L1行情 / portfolio ≥ $10M → 整体时延SLO从秒级压缩到毫秒级
2. 合伙人或监管激活 → SLA列从internal转对外承诺
3. 引入实时流架构（Kafka/Pulsar事件总线）→ 从batch语义改为streaming语义
4. 任一SLO**连续3个月**未达标 → 触发root-cause KB决策 + 目标值重评

### 5.5 与其他视图的边界

- 本节只定义**业务SLO的目标值与定义**；**SLI如何实现**（Metrics/Logs/Traces具体pipeline）见 [technology_architecture.md](./technology_architecture.md) §可观测性（CC2域交付）。
- **Data Quality SLO-7**的技术细节（PIT/Survivorship/Lineage实现与断言）见 [data_architecture.md](./data_architecture.md)。
- **Order Idempotency**（SLO-3的幂等前置）见 [application_architecture.md](./application_architecture.md)。

---

## 6. Business constraints / 业务约束与政策红线

> 完整约束真源在 [architecture_principles.md](../04_architecture_principles_decisions/architecture_principles.md)（R1-R4安全红线 + 准入铁律）。

| 约束 | 说明 | 真源 |
|------|------|------|
| **Single canonical source** | `docs/`是唯一真源 | KBG-0001 |
| **Append-only decision records** | 已接受决策只能被supersede，不可删改 | KBG-0002 |
| **Markdown + Git** | 所有文档文本格式，版本化管理 | KBG-0001 |
| **Personal-scale initially** | 初始单账户、个人资金、不对外募资 | — |
| **Deferred activation** | 安全/合规/SRE域 deferred until external investors or live trading | — |

---

## 7. Architecture Runway / 架构预留通道

> 以下预留通道为未来P3能力激活后的挂载点。本节不实现任何具体逻辑，仅记录"将来何处扩展、何条件触发"。

| ID | 能力描述 | 挂载点 | 激活触发条件 |
|---|---|---|---|
| RW-BA-01 | 投委会支持工具 — 多人协作议事流程、审议记录、AI辅助决策仪表盘 | §2 Stakeholder | 系统从个人扩展到多人协作团队（≥2位基金经理共同管理）|
| RW-BA-02 | 多基金经理协调机制 — 权限分层、策略分配、绩效归因隔离 | §2 | 团队规模扩展到多人管理，R/A出现跨人分裂 |
| RW-BA-03 | 系统化全球宏观策略 — 扩展Value Stream覆盖跨境资产 | §4.1 Value Stream | 全球多市场接入完成（A股+港股+美股）+ 宏观数据库完整 |
| RW-BA-04 | 战略联盟框架 — 多方数据/策略共享治理协议 | §6 Constraints | 系统扩展到多方数据/策略共享，出现对外合作场景 |
| RW-BA-05 | 机构级报告体系 — 投资者报告、监管申报、业绩归因标准化 | §5.3 SLA | 系统管理资金规模 > 1000万 or 接受外部投资人 |

> **激活时**：RW-BA-01/02 激活时需从 git 历史恢复完整 RACI 矩阵（v1.2.0, commit 69fa51dc12~1）。
