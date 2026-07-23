---
module_id: VIEW-01-BUSINESS-ARCH
title: Target Architecture — Business Architecture / 目标架构：业务架构 （被恢复）
doc_type: architecture_view
status: Active
version: 1.2.0
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
- stakeholders
- raci
- capability-map
- value-stream-map
- vsm
- nfr
- sla
- slo
- sli
summary: TOGAF Business Architecture 视图。回答：ZephyrAlpha 2.0 为谁服务、核心业务能力是什么、端到端业务流程、非功能需求（NFR）与业务约束。为
  IA / AA / TA 三层提供业务依据。v1.1.0：补齐 RACI / Value Stream / SLA 三大 TOGAF 核心构件（R41/R42/R43）。
date: '2026-04-22'
ttl: permanent
---

## 1. Purpose of this view / 本视图的用途

The Business Architecture answers:

业务架构视图回答：

- **Who** do we serve? (Stakeholders / 利益相关者)
- **What** capabilities does the business need? (Business Capability Map / 业务能力地图)
- **How** does core value flow? (End-to-end process / 端到端流程)
- **What** are the non-functional requirements? (NFR / 非功能需求)
- **What** are the constraints? (Policies & limits / 政策与红线)

This view **drives** the Information Architecture (what to document), which drives the Application Architecture (what to build), which drives the Technology Architecture (what stack to use).

本视图**驱动**信息架构（需要记录什么），信息架构驱动应用架构（需要构建什么），应用架构驱动技术架构（需要什么技术栈）。

---

## 2. Stakeholders / 利益相关者

### 2.1 Stakeholder Roster / 利益相关者清单

专业量化机构的 Stakeholder 画像在"单人 + AI 协同"阶段**物理上由同一个人承担多个角色**，但**架构语义上必须拆开**——否则未来引入合伙人 / 外部投资人 / 多 AI Operator 时会出现责任真空。下表 8 类为终局形态，当前阶段的角色归属见 §2.2 注脚。

| # | Stakeholder / 利益相关者 | Role / 角色 | Primary concerns / 主要关注点 | 当前阶段归属 |
|---|-------------------------|------------|------------------------------|------------|
| S1 | **Architect / 架构师** | 系统设计、视图一致性、KB 决策记录 决策 | 架构完整性、TOGAF 8 视图对齐、技术债可控 | you |
| S2 | **Quant researcher / 策略研究员** | 策略研发、因子构造、假设检验 | Alpha 质量、PIT 一致性、回测可信度 | you |
| S3 | **Trader / 交易员** | 下单执行、成交监控、异常处置 | 执行滑点、成交质量、下单延迟 | you |
| S4 | **Risk officer / 风控官** | 事前限额、事中监控、事后审查 | 仓位限额、回撤止损、幂等红线 | you |
| S5 | **Compliance officer / 合规官** | 合规审查、监管留痕、报告披露 | 交易记录留痕、KB 决策记录 审计链、合规触发 | you（deferred，`16_compliance_and_legal/` 激活后独立）|
| S6 | **Data engineer / 数据工程师** | 数据接入、质量门禁、血缘追踪 | Data Freshness、Quality 断言、血缘完整 | you |
| S7 | **SRE / Ops / 运维** | 部署、监控、容量、成本、DR | 可用性、Runbook 可演练、成本可控 | you（deferred，`operations_architecture.md` skeleton 激活后独立）|
| S8 | **AI collaborators / AI 协作者** | Kimi（diverge 发散）+ Cursor/Opus（converge 收敛）| 文档可读性、上下文质量、结构一致性 | Kimi / Cursor-Opus / Sonnet / GLM / Qwen |
| S9 | **AI Operators / AI 代理人**（预留，`OQ-063` AC-1/2/3 + C-1/2/3）| 未来承担日常执行类职责的自治 Agent（如 factor-refresh-operator / rebalancer-operator）| 决策日志完整、可审计、红线不越界 | **未激活**；激活前接口位于 `src/zephyr/layers/{L}/_ai_operator/` + `META_GOVERNANCE/ai_operators_registry.md` |
| S10 | **External data vendor / 外部数据供应商** | 同花顺 iFinD（已采购）+ 未来 Bloomberg / Wind / 交易所直连 | 契约 SLA、API 限流、计费、字段稳定 | iFinD（合同 + API key，1 条 Vendor Registry 记录）|
| S11 | **Future partners / 未来合伙人** | 潜在合作者 / 外部投资人 | 策略透明度、合规记录、绩效归因可验证 | **未激活**（personal-scale initially）|
| S12 | **Regulators / 监管方** | 证监 / 交易所 / 银行监管 | 交易记录留痕、合规报告、风险披露 | **未激活**（external investors or live trading 前 deferred）|

### 2.2 Responsibility Assignment Matrix (RACI) / 责任分配矩阵

> **标记含义**：**R**=Responsible 执行者，**A**=Accountable 最终问责人（**每行有且仅有一个 A**，TOGAF/PMI 铁律），**C**=Consulted 需要协商，**I**=Informed 需要知会。空白=无关。

| # | Activity / 关键活动 | 归属能力域 | S1 Arch | S2 Quant | S3 Trade | S4 Risk | S5 Comp | S6 Data | S7 SRE | S8 AI-collab | S9 AI-Op | S10 Vendor | S11 Partner | S12 Reg |
|---|---------------------|----------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| A01 | 架构 KB 决策记录 决策与终审 | C01-C10 | **A/R** | C | C | C | C | C | C | C | I | | I | |
| A02 | 策略假设与研发 | C02/C04 | C | **A/R** | | C | | C | | C | | | I | |
| A03 | 因子构造与上线 | C02 | C | **A/R** | | C | | R | | C | | | | |
| A04 | 因子日度/分钟刷新执行 | C02 | I | A | | I | | R | R | | R（未来）| I | | |
| A05 | 回测验证与报告 | C02/C04 | | **A/R** | | C | | C | | C | | | I | |
| A06 | 模型训练与部署 | C03 | C | R | | | | R | **A** | C | R（未来）| | | |
| A07 | 信号生成与发布 | C04 | | **A/R** | I | C | | C | I | | R（未来）| | | |
| A08 | 组合构建与再平衡 | C04 | | R | I | C | | | I | C | **A**→R（未来）| | | |
| A09 | 事前风控审批（下单前门）| C08 | I | I | I | **A/R** | C | | I | | | | | |
| A10 | 下单执行与订单生命周期 | C05 | | | **A/R** | C | I | | I | | R（未来）| R | | |
| A11 | 成交回报与对账 | C05/C06 | | I | R | I | I | R | I | | R（未来）| R | | |
| A12 | 事中仓位/回撤监控 | C08 | I | I | I | **A/R** | I | | R | | | | | |
| A13 | 异常处置与 kill-switch | C05/C08 | I | I | R | **A/R** | I | I | R | | | | | I |
| A14 | 绩效归因与交易后分析 | C06 | I | R | I | C | | C | | C | | | I | |
| A15 | 数据接入（Vendor SLA 维护）| C01 | I | I | | | | **A/R** | C | | | R | | |
| A16 | 数据质量断言与血缘 | C01 | C | I | | | I | **A/R** | I | | | | | |
| A17 | 合规审查与留痕归档 | C09 | I | I | I | C | **A/R**（deferred）| | I | | I | | | I |
| A18 | 运维部署 / 容量 / 成本 | C04-C05/cross | C | I | | | | I | **A/R**（deferred）| | | | | |

### 2.3 "Single operator + AI" 人机协同特例 / 单人 + AI 协同的 R/A 重合处理

在当前阶段（single operator，多 AI 协作，`ai_operators_registry.md` 尚未激活），上表的 R/A 在物理上大量重合到**同一个人（you）**，这是真实场景，但**必须显式说明**，否则未来引入合伙人 / AI Operators 时责任真空会浮现。

**协同规则（本视图的铁律）**：

1. **A（Accountable）不可委托**：即使 AI 生成了 KB 决策记录、回测报告、甚至下单代码，最终 **A 仍是 you**（S1-S7 物理合一）。AI 不承担问责，只承担 R/C。
2. **R（Responsible）可以渐进迁移到 AI**：当前 R 大量落在 you；**未来 AI Operators 激活后**，A04 / A06 / A07 / A08 / A10 / A11 的 R 列会从 you 迁移到 S9（标注 "R（未来）"的列）；A 列永远不变。
3. **AI collaborators (S8) 的职责边界**：仅限 **C（Consulted）**——提供候选方案、文档草稿、红队质疑。**不进入 R/A**。AI 产出必须由 you 的某个物理角色（S1-S7）签字承接才落盘。
4. **人机协同日志**：所有 R=you + C=S8 的活动，其决策日志按 `OQ-063` 七维度字段（身份/触发/输入/推理/决策/执行/审计）完整记录到 `META_GOVERNANCE/`，未来审计可溯源。
5. **升级触发**：当 S11（合伙人）或 S12（监管）激活时，本表必须重新评审 A 列（当前由 you 兜底的 A 可能需要拆给专职角色）；由 `OQ-063` 同级 OQ 管理升级流程。

### 2.4 与 other views 的边界 / 与其他视图的边界

- 本 §2 是**业务层** Stakeholder & RACI；**应用层**的系统 Actor 与模块 Owner 映射见 `application_architecture.md`；**数据层**的数据 Owner/Steward 见 `../04_architecture_principles_decisions/data_principles.md §5 MDM`；**治理层** AI Operator 架构见 `META_GOVERNANCE/ai_operators_registry.md`（预留）。
- S9 AI Operators 的物理落地位置（`_ai_operator/` 命名空间）由 `OQ-063 AC-1/2/3 + C-1/2/3 + D-1/2/3 + F-1/2/3` 管理；本视图只登记**业务角色占位**，不展开技术实现。

---

## 3. Business Capability Map / 业务能力地图

ZephyrAlpha 2.0 is a **quantitative investment system** covering the full lifecycle: Data → Research → Model → Strategy → Execution → Reporting.

ZephyrAlpha 2.0 是**量化投资全生命周期管理系统**，覆盖：数据 → 研究 → 模型 → 策略 → 执行 → 报告。

Core capability domains / 核心能力域：

| # | Capability domain / 能力域 | Description / 说明 | `docs/` mapping / 对应抽屉 |
|---|--------------------------|-------------------|--------------------------|
| C01 | Data acquisition & quality / 数据接入与质量 | 市场数据标准化接入、质量门禁、血缘追踪 | `09_data_platform/` |
| C02 | Research & factor engineering / 研究与因子工程 | Alpha 因子研究、事件研究、实验设计 | `10_research_and_factor_lab/` |
| C03 | Model & ML platform / 模型与机器学习平台 | 模型训练、评估、部署、注册与监控 | `11_model_and_ml_platform/` |
| C04 | Strategy & portfolio construction / 策略与组合构建 | 策略逻辑、回测、组合优化、再平衡 | `12_strategy_and_portfolio/` |
| C05 | Trade execution / 交易执行 | OMS、SOR、委托执行、执行前风控 | `13_execution_and_order_lifecycle/` |
| C06 | Post-trade analytics & reporting / 交易后分析与报告 | 绩效归因、简报生成、分发渠道 | `14_reporting_and_distribution/` |
| C07 | AI engineering & agent ops / AI 工程与代理运维 | Agent 规则、记忆、上下文、模型路由、成本治理 | `03_modules/_b_track_interfaces/` |
| C08 | Risk & controls / 风险与控制 | 风险政策、限额、压力测试、控制库 | `17_risk_and_controls/` |
| C09 | Compliance & legal / 合规与法务 | 监管映射、合规要求、留存要求 | `16_compliance_and_legal/` |
| C10 | Knowledge management / 知识管理 | 最佳实践、经验教训、因子/策略知识库 | `08_knowledge/` |

Detailed capability entries: → `architecture_model/cross-cutting/capability_heatmap.yaml`

详细能力条目：→ `architecture_model/cross-cutting/capability_heatmap.yaml`

---

## 4. End-to-end core process — Value Stream Map / 端到端核心业务流程（价值流图）

本节把 §3 的业务能力域（C01-C10）落到**时间维度 + 交接维度 + 浪费维度**的 Value Stream Map（VSM，精益/TOGAF 核心构件）。目的：让瓶颈、浪费、返工点可见，才能被治理。

### 4.1 Canonical value stream / 标准价值流（Mermaid VSM）

> **📊 业务价值流图**：见 [`diagrams/business_value_stream.mmd`](diagrams/business_value_stream.mmd)

**图例**：
- **LT**（Lead Time）= 工件从到达工序到离开工序的**总耗时**（含等待）
- **PT**（Process Time）= 实际**增值加工**时间（不含等待）
- **%C&A**（Complete & Accurate）= 下游第一次接收就**可用且正确**的比例
- 橙色节点 = Handoff（交接点，详见 §4.3）；虚线 = 反馈回路或横向治理

### 4.2 Stage-level metrics / 阶段级指标表

| 阶段 | 核心工件 | Owner | Lead Time | Process Time | %C&A | 主要延迟来源 |
|------|---------|-------|----------|-------------|------|-----------|
| ② Factor Research | 因子假设 + 特征工程 | S2 | 5-20 天 | 2-8 小时 | 70% | 想法→验证的探索回合、PIT 数据整备 |
| ② Factor Library | 因子入库 + 质量断言 | S2 + S6 | 15-60 min | 10-30 min | 98% | PIT 三字段校验、五类质量断言 |
| ③ Model Train/Deploy | 模型 + 部署 manifest | S7（未来）| 2-24 小时 | 30 min-4 h | 95% | GPU 排队、超参搜索 |
| ③ Signal Generation | 信号 payload | S2 | 15-60 min | 5-15 min | 98% | 因子刷新依赖、下游订阅对齐 |
| ④ Portfolio Construction | 目标仓位 | S2 → S9（未来）| 5-15 min | 1-5 min | 99% | 约束求解器收敛 |
| ④ Pre-trade Risk | 风控审批结果 | S4 | &lt;1 min | 5-30 s | 99.9% | 限额查询、手工复核（ad-hoc）|
| ⑤ Order Submission | broker ACK | S3 | 1-5 min | 10-60 s | 99.5% | 券商 API 网络、Idempotency 校验（H10 红线）|
| ⑤ Fill &amp; Reconcile | 成交单 + 对账记录 | S3 + S6 | intraday | 1-5 min | 99% | 成交回报到齐、T+0/T+1 对账窗口 |
| ⑥ Attribution | PnL + 归因报告 | S2 | T+1 | 10-30 min | 99% | 日终结算数据到齐 |
| ⑦ Feedback loop | 研究结论 / KB 决策记录 候选 | S1 + S2 | T+1 ~ T+5 | 1-4 h | 85% | 人工复盘、AI 辅助分析往返 |

> **注**：LT/PT 数字基于当前"非 HFT、daily/hourly batch"定位（见 §5 NFR）。若未来激活 intraday 高频（触发条件：portfolio ≥ $10M + 接入 L1 行情），本表需整体向秒级压缩重写。

### 4.3 Key handoffs / 关键交接点

Handoff 是 VSM 中最易产生**信息损失 + 责任真空 + 数据污染**的点，必须显式标注契约。

| # | Handoff | 上游 → 下游 | 交接物 | 风险 | 治理手段 |
|---|---------|------------|-------|------|---------|
| **HO-1** | **Vendor → Data Lake**（市场数据入仓）| S10 → S6 | 原始 tick / bar / reference data | 字段漂移、survivorship、迟到数据覆盖历史 | ACL（`03-AA H8`）+ PIT 三字段（`05-DA §4`）+ immutable append |
| **HO-2** | **Research → Factor Library**（研究→生产）| S2 → (S2+S6) | 因子代码 + metadata + 断言 | 研究环境灰带代码进生产、look-ahead bias | H8 ACL 隔离 + F21-F25 fitness functions + `OQ-075` 三断言 |
| **HO-3** | **Signal → Pre-trade Risk**（信号→风控）| S2 → S4 | signal payload + metadata | 信号绕过风控、限额不同步 | 强制性 Pre-trade gate（A09）+ Idempotency Key（`03-AA H10`）|
| **HO-4** | **Portfolio → Broker**（组合→券商）| S3 → S10 | 委托单 + client_order_id | **订单重发重复**（量化红线）| H10 幂等设计 + broker ACK 回执持久化 |
| **HO-5** | **Fill → Attribution / Feedback**（成交→归因→研究）| (S3+S6) → S2 → S1 | 成交记录 + PnL 分解 + 结论 | 反馈断链（归因洞察没回到因子库）| Decision log 七维度（`OQ-063`）+ `08_knowledge/` 沉淀 |

### 4.4 Bottlenecks &amp; waste / 瓶颈与浪费点

按精益七大浪费（等待 / 返工 / 过度加工 / 传输 / 库存 / 动作 / 缺陷）识别：

| # | 类型 | 瓶颈 / 浪费 | 影响阶段 | 当前状况 | 改进方向（deferred 到具体 sprint）|
|---|------|------------|---------|---------|--------------------------------|
| **B1** | **等待**（Wait）| 市场数据上游窗口（iFinD EOD 推送延迟，下游结算数据 T+1 到齐）| ① ② ⑥ | 单 Vendor 单链路；无备份源 | 接入 AKShare / Tushare 作 fallback（OSS Catalog X3）|
| **B2** | **等待**（Wait）| 回测任务排队（单机资源、无任务调度器）| ② | `backtest TAT p95 ≤ 30min`（§5 H3 SLO）可能因串行回测超时 | H14 Observability 后加 job queue；或引入 Airflow / Prefect |
| **B3** | **等待 / 返工**（Rework）| 合规审批等待（当前合规 S5 deferred 由 you 手工兜底）| ④ ⑤ ⑦ | 手工，无规则引擎 | S5 激活后引入 policy-as-code（`16_compliance_and_legal/`）|
| **B4** | **返工**（Rework）| 因子重算（PIT 一致性失败触发全量回补）| ② | F21-F25 fitness function 会拦截；但"拦截后回补"本身是返工 | 增量回补（只回补被 corporate action 污染的 partition）|
| **B5** | **传输 / 动作**（Motion）| 人-AI 协作往返（prompt → 草稿 → 审核 → 修订）在 ⑦ 反馈回路中占 LT 60%+ | ⑦ | 每次 AI 协作 round-trip 15-60 min | VIB-1 Session 治理 + prompt 资产库（VIB-4）沉淀复用 |
| **B6** | **缺陷**（Defect）| 信号失效未及时发现（factor decay / concept drift）| ② ③ ⑥ | 归因只 T+1 看结果，drift 监控缺失 | L13 experiment_pipeline 激活后 champion-challenger 在线对照 |

### 4.5 Cross-cutting governance / 横向治理贯穿全链

与 §4.1 图中 `GOV` 节点对应：

- `00_governance/` + `META_GOVERNANCE/` — **Policy control + KB 决策记录 链 + AI Operator registry**（预留）
- `17_risk_and_controls/` — 每阶段的风险控制策略（pre/in/post-trade）
- `03_modules/_b_track_interfaces/memory-and-context/` — 协作知识沉淀（AI 会话上下文、prompt 资产）
- `08_knowledge/` — 因子库 / 策略库 / 经验教训

---

## 5. Non-functional requirements (NFR) / 非功能需求

### 5.1 Qualitative NFR summary / 定性 NFR 概览

本节的定位原则（**先立边界再定数字**）：

- **Non-HFT 定位**：不追求微秒/毫秒级；延迟单位为**秒 / 分钟 / 小时**。若未来接入 L1 行情或组合 ≥ $10M，NFR 整体需重写。
- **市场时段 vs 非市场时段分层**：可用性/延迟 SLO 只在**市场时段（含盘前盘后 30 min 缓冲）**严格执行；非市场时段为 best-effort。
- **可审计 ≫ 可用性**：当前阶段（单人无外部用户）若可用性与可审计冲突，必须选可审计。

| Category / 类别 | Requirement / 要求 | Current phase target / 当前阶段目标 | 量化 SLO 见 |
|----------------|-------------------|-----------------------------------|-----------|
| **Latency / 延迟** | Non-HFT；秒级—分钟级 batch；端到端 signal→order ≤ 90s（p99）| 不追求微秒级 | §5.2 SLO-2 / SLO-3 |
| **Availability / 可用性** | 市场时段 99.9% / 非市场时段 best-effort | 单人操作，非 24/7 | §5.2 SLO-6 |
| **Auditability / 可审计性** | Full decision trail, immutable KB 决策记录, seven-dimension decision logs | **高优先级**（不可降）| §5.2 SLO-Audit |
| **Compliance / 合规性** | Personal-scale；future multi-investor triggers stricter | 当前最简，留扩展口 | §5.2 SLO-Audit |
| **Maintainability / 可维护性** | Single operator + AI collab；docs-as-code | 高优先级 | — |
| **Extensibility / 可扩展性** | 平台模块（Gateway / Memory Pipeline）deferred 但预留接口 | 架构预留 | — |
| **Security / 安全性** | Personal scale；密钥管理、无公开暴露 | `security_architecture.md` skeleton，激活条件见其 §8 | — |
| **Data Quality / 数据质量** | PIT / survivorship / lineage 三断言；完整度 / 一致性 / 及时性三维度 | 高优先级（因子与回测可信度的前置）| §5.2 SLO-7 |

### 5.2 SLA / SLO / SLI matrix / 服务等级矩阵

> **术语铁律**：**SLA**（Service Level Agreement）= 对外承诺（当前单人，无外部合同 → 大部分 SLA 列标 "internal commitment"，仅 Vendor 契约列真实 SLA）。**SLO**（Service Level Objective）= 内部目标（可量化）。**SLI**（Service Level Indicator）= 实际测量指标（可落到 metric）。
>
> **测量 / 上报位置**：所有 SLI 均接入 `technology_principles.md §7 Observability`（永恒三支柱框架）+ `dr_bcp_matrix.yaml`（具体指标目录，当前为占位，由批次 C 任务 5.3 H14 填充，用 OpenTelemetry Metrics/Logs/Traces 三支柱）。完成前以 **"📌 → technology_principles.md §7 (TODO)"** 标注引用锚。

| # | SLO 名称 | 定义与场景 | Target (quant)<br/>目标值 | SLI 测量方法 | 上报位置 | 违约后果 |
|---|---------|-----------|-----------------------|-----------|---------|---------|
| **SLO-1** | **Data Freshness**<br/>数据新鲜度 | 市场时段行情从 vendor 发布到数据湖可查询的端到端延迟 | 分钟级 bar：p50 ≤ 15 s / p95 ≤ 60 s / p99 ≤ 180 s<br/>日度结算：T+1 **11:00 UTC+8** 前 100% 到齐（p99）<br/>Reference 数据（证券主数据 / 交易日历）：T 日 **18:00 UTC+8** 前到齐 | `ts_ingest − vendor_release_ts` 差值（见 `05-DA §4` PIT 三字段）；histogram export to Prometheus | 📌 → technology_principles.md §7 (TODO)<br/>Prom metric：`data_freshness_seconds{dataset,vendor}` | 触发 B1 降级 + 阻塞因子刷新（SLO-5）|
| **SLO-2** | **Signal Generation Latency**<br/>信号生成端到端延迟 | 市场数据进入 → 信号 payload 发布的端到端 p99（intraday batch 场景）| p50 ≤ 30 s / p95 ≤ 60 s / p99 ≤ **90 s**<br/>EOD 策略：p95 ≤ **10 min** | OTel 分布式 trace：`span=signal_generation`，端点 = data ingress timestamp → signal publish timestamp | 📌 → technology_principles.md §7 (TODO)<br/>OTel trace + `signal_latency_seconds` histogram | 超限则信号标记 `stale=true`，下游 portfolio 降级处理 |
| **SLO-3** | **Order Submission Latency**<br/>下单提交延迟 | 从信号发布（含通过 pre-trade risk gate）到券商 broker ACK 的 p99 | p50 ≤ 5 s / p95 ≤ 15 s / p99 ≤ **30 s**<br/>（含 A09 pre-trade risk p99 ≤ 1 s + 券商网络）| OTel span：`span=order_submit`，起点 `signal.published_at`，终点 `broker_ack_at`；Idempotency Key 命中率一并记录 | 📌 → technology_principles.md §7 (TODO)<br/>`order_submit_latency_seconds` + `idempotency_hit_total` | 超限则 kill-switch 触发（A13），已下订单走 H10 幂等回执 |
| **SLO-4** | **Backtest Turnaround**<br/>回测周转 TAT | 常规回测（单策略 × 5 年日频全市场）提交到结果可用的 end-to-end | 常规：p50 ≤ 10 min / p95 ≤ **30 min** / p99 ≤ 60 min<br/>重度（因子扫描 / 参数网格）：p95 ≤ **4 h** | Job 执行时长 metric：`backtest_duration_seconds{type}`；队列等待单独记 `backtest_queue_wait_seconds` | 📌 → technology_principles.md §7 (TODO) | 触发 B2 降级，考虑并行调度器（Airflow/Prefect）|
| **SLO-5** | **Factor Refresh Window**<br/>因子刷新窗口 | 日度因子与分钟因子的刷新时效 | 日度因子：EOD T 日 18:00 + **90 min** 内 100% 刷新完成（p99）<br/>分钟因子（滚动）：每 **5 min** 刷新一次，p99 完成时间 ≤ **5 min** | `factor_refresh_duration_seconds{cadence,factor_id}` + 完成率 `factor_refresh_success_ratio` | 📌 → technology_principles.md §7 (TODO) | 下游信号标记 `factor_stale=true`；连续 2 个窗口失败告警 |
| **SLO-6** | **System Availability**<br/>系统可用性 | 核心链路（data ingest + signal gen + order submit）在市场时段的月可用性 | 市场时段：**99.9% / month**（单月允许停机 ≤ **43.2 min**）<br/>非市场时段：best-effort（无承诺）| Blackbox probe 每 30 s ping 核心端点；SLI = `1 − downtime_min / market_hours_min` | 📌 → technology_principles.md §7 (TODO)<br/>`availability_ratio{component}` | 超限触发事后 incident review + KB 决策记录（可审计链）|
| **SLO-7** | **Data Quality**<br/>数据质量 | PIT / survivorship / lineage 三断言 + 完整度 / 一致性 / 及时性三维度 | 完整度（Completeness）：≥ **99.5%**（缺失率 ≤ 0.5%）<br/>一致性（Consistency，PIT 铁律不被破坏）：≥ **99.9%**<br/>及时性（Timeliness，同 SLO-1）：见 SLO-1<br/>F21-F25 fitness functions（`OQ-027` + `OQ-075` 三自研断言）：**100% pass**（任何失败阻塞上线）| Great Expectations / Soda 断言结果；pytest fitness function pass ratio；自研 `test_no_lookahead_bias.py` / `test_no_survivorship_bias.py` / `test_lineage_completeness.py` | 📌 → technology_principles.md §7 (TODO)<br/>`data_quality_assertion_pass_ratio{assertion,dataset}` | 任何断言失败阻塞因子上线（HO-2 handoff gate）|
| **SLO-Audit** | **Auditability**<br/>可审计性 | KB 决策记录 决策链完整、AI 协作决策日志七维度覆盖、factor/strategy 变更均可回溯 | KB 决策记录 append-only：100%（不可变）<br/>AI 决策日志七维度（`OQ-063`）覆盖率：≥ **99%**（允许 &lt; 1% extensions 兜底）<br/>Git commit → KB 决策记录 双向索引完整度：100% | pre-commit hook + CI audit（`scripts/ci_audit/`）+ decision log schema validation | 📌 → technology_principles.md §7 (TODO)<br/>`adr_append_only_violations_total` / `decision_log_coverage_ratio` | **0 容忍**：任何违约阻塞 merge |

### 5.3 SLA vs SLO — current phase reality / 当前阶段的 SLA 现实

| 对手方 | 是否有真实 SLA | 说明 |
|-------|-------------|------|
| **S10 iFinD（Vendor）** | ✅ 有合同 SLA | 由供应商承诺可用性 / 限流 / 字段稳定，登记在 `integration-catalog.md` Vendor Registry |
| **S11 Future partners** | ❌ 无（未激活）| S11 激活后，本表 SLO-6 / SLO-7 需转为对合伙人的 SLA |
| **S12 Regulators** | ❌ 无商业 SLA（但有合规时限）| 监管激活后，合规报告时限（如成交回报 T+1）转为硬性 SLA |
| **内部** | ❌ 无（单人）| 当前所有 SLO 都是"对自己的承诺"，性质接近 OKR；仍必须量化、否则无法治理 |

### 5.4 升级触发与 revision trigger / SLO 重写触发条件

以下任一条件触发本表**整体重写**（非局部调整）：

1. 接入 L1 行情 / portfolio ≥ $10M → 整体时延 SLO 从秒级压缩到毫秒级
2. S11 合伙人或 S12 监管激活 → SLA 列从 internal 转对外承诺
3. 引入实时流架构（Kafka/Pulsar 事件总线，见 `OQ-021` L12 + `03-AA B1` 盲点）→ 从 batch 语义改为 streaming 语义
4. 任一 SLO **连续 3 个月** 未达标 → 触发 root-cause KB 决策记录 + 目标值重评

### 5.5 与其他视图的边界 / 边界

- 本节只定义**业务 SLO 的目标值与定义**；**SLI 如何实现**（Metrics/Logs/Traces 具体 pipeline）见 `technology_principles.md §7 Observability`（永恒框架）+ `dr_bcp_matrix.yaml`（具体指标目录，H14 任务交付，当前占位）。
- **Data Quality SLO-7** 的技术细节（PIT / Survivorship / Lineage 实现与断言）见 `../04_architecture_principles_decisions/data_principles.md §2/§3/§4/§6`。
- **Availability SLO-6** 的 DR/BCP 细化（RTO/RPO）见 `technology_principles.md §5`（永恒框架）+ `dr_bcp_matrix.yaml`（域名级 RTO/RPO 矩阵，H15 任务交付，当前占位）。
- **Order Idempotency（SLO-3 的幂等前置）** 见 `application_architecture.md §9`（H10 任务交付，当前占位）。

---

## 6. Business constraints / 业务约束与政策红线

| Constraint / 约束 | Description / 说明 |
|------------------|-------------------|
| **Single canonical source** | KBG-0001: `docs/` is the only truth source / 唯一真源 |
| **Append-only decision records** | KBG-0002: status changes only, no deletion of accepted decisions / 已接受决策只能被 supersede，不可删改 |
| **Markdown + Git** | All docs in text format, version-controlled / 所有文档文本格式，版本化管理 |
| **Personal-scale initially** | Single account, personal capital, no external fund management at launch / 初始单账户、个人资金、不对外募资 |
| **Deferred activation** | `06_security`, `07_sre`, `16_compliance` deferred until external investors or live trading / 外部投资人或真实交易前不激活 |

---

## 8. Architecture Runway / 架构预留通道

> 以下预留通道为未来 P3 能力激活后的挂载点。本节不实现任何具体逻辑，仅记录
> "将来何处扩展、何条件触发、引用哪个 P3 条目"。
> P3 完整条目索引：`docs/08_knowledge/04_future_capabilities/p3-blueprint-index.md` [待创建]
> **季度 Review 规则**：每季度对照 §6 激活监控清单检查触发条件是否满足；满足后将 activation_status 从 `deferred` 改为 `ready`，等待人工拍板。

| ID | 能力描述 | 挂载点 | 激活触发条件 | P3 索引 |
|---|---|---|---|---|
| RW-BA-01 | 投委会支持工具 — 为多人协作场景提供议事流程、审议记录、AI 辅助决策仪表盘 | `§2 Stakeholder S1-S12` + `ml_train/` | 系统从个人扩展到多人协作团队（≥2 位基金经理共同管理）| P3-STR-002 [待创建] |
| RW-BA-02 | 多基金经理协调机制 — 权限分层、策略分配、绩效归因隔离 | `§2.2 RACI 矩阵` 新增 S13+ 行 | 团队规模扩展到多人管理，RACI 中 R/A 出现跨人分裂 | P3-STR-011 [待创建] |
| RW-BA-03 | 系统化全球宏观策略 — 扩展 Value Stream §4 覆盖跨境资产 | `§4.1 Value Stream Map`（阶段 2-3 扩展节点）| 全球多市场接入完成（A股+港股+美股）+ 宏观数据库完整 | P3-STR-012 [待创建] |
| RW-BA-04 | 战略联盟框架 — 多方数据/策略共享治理协议、联合投研协议 | `§6 Business Constraints` 新增联盟约束行 | 系统扩展到多方数据/策略共享，出现对外合作场景 | P3-GOV-004 [待创建] |
| RW-BA-05 | 机构级报告体系 — 投资者报告、监管申报、业绩归因报告标准化 | `§5.3 SLA` 新增 external SLA 行 + `§5.2` SLO-3 重写触发 | 系统管理资金规模 > 1000 万 or 接受外部投资人 | P3-STR-003 [待创建] |

---

## 7. Revision history / 修订记录

| Date / 日期 | Description / 说明 |
|------------|-------------------|
| 2026-04-17 | v1.0.0：从 DW-IA-DESIGN-001 §2 骨架 + §3 抽屉体系映射拆分升格建立。覆盖利益相关者、业务能力地图、端到端流程、NFR 与业务约束。 |
| 2026-04-19 | v1.1.0：补齐 RACI / Value Stream / SLA 三大 TOGAF 核心构件（S14-beta 批次 B，H4/H1/H3）。§2 升级：Stakeholder 从 4 行扩展为 12 行（S1-S12，含 AI Operators S9 预留与 Vendor/Partner/Regulator），新增 §2.2 RACI 矩阵（18 活动 × 12 Stakeholder，每行唯一 A 的 TOGAF 铁律）+ §2.3 "单人+AI 协同"人机协同 5 条铁律 + §2.4 其他视图边界（R41）。§4 升级：从纯文本链升格为完整 VSM（§4.1 Mermaid 7 阶段 10 节点 + 反馈回路 + 横向治理）+ §4.2 Stage-level 10 行 LT/PT/%C&A 指标表 + §4.3 5 个 Handoff 点契约 + §4.4 6 个瓶颈/浪费点（精益七大浪费分类）+ §4.5 横向治理（R42）。§5 升级：新增 §5.1 3 条边界原则 + §5.2 SLA/SLO/SLI 矩阵（SLO-1 至 SLO-7 + SLO-Audit 共 8 行量化指标，每条标测量方法 + 上报位置引用 04-TA §10 Observability H14）+ §5.3 SLA 现实（仅 iFinD 真合同）+ §5.4 4 条重写触发 + §5.5 与其他视图边界（R43）。 |
| 2026-04-19 | v1.2.0：S2 — 追加 §8 Architecture Runway 预留通道（5 条业务侧/战略侧 P3 预留，R59）。 |
