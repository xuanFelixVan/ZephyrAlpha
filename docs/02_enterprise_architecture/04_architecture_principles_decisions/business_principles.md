---
module_id: VIEW-04PRINC-BUSINESS
title: Architecture Principles — Business / 架构原则：业务
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
supersedes: VIEW-01-BUSINESS-ARCH
related_rationale: []
related_open_questions:
- OQ-063
tags:
- business-principles
- togaf
- ba
- capability-map
- value-stream-map
- vsm
- nfr
- slo
- sli
summary: 业务架构永恒原则文档。timeless 方法论——业务能力地图框架（C1-C7 + CC1-CC3 横切）、Value Stream Map 方法论（LT/PT/%C&A、Handoff 治理、精益七浪费）、NFR 定位原则（Non-HFT、市场时段分层、可审计≫可用性）、SLO/SLA/SLI 术语铁律、SLO 升级触发条件。派生数据（全域→能力域映射、阶段指标具体数字、能力成熟度评分）不在本文档，由 capability_heatmap.yaml + 自动化系统维护。
date: '2026-07-19'
ttl: permanent
---

# Architecture Principles — Business
# 架构原则：业务（Business Principles）

---

## §1 定位 / Position

本文档是**业务架构的永恒指导原则**。

**保留内容**：方法论、设计原则、不变约束——业务能力地图框架、VSM 方法论、NFR 定位原则、SLO 术语铁律。

**不保留内容**（派生/动态数据，由各自自动化系统维护）：
- 全域→能力域映射 → `architecture_model/cross_cutting/capability_heatmap.yaml`（真源）
- 能力成熟度评分 → `architecture_model/cross_cutting/capability_heatmap.yaml` + `../01_global_architecture_diagram/global_capability_heatmap.md`（自动派生）
- VSM 阶段指标 + Handoff 契约（含交接物）+ 瓶颈 B1-B6 + SLO 目标值矩阵 + SLA 现实 → `architecture_model/cross_cutting/value_stream_map.yaml`

**与其他原则文档关系**：
- [capability_maturity_principles.md](capability_maturity_principles.md)：能力成熟度方法论
- [data_principles.md](data_principles.md)：数据架构原则
- [security_principles.md](security_principles.md)：安全架构原则
- [integration_principles.md](integration_principles.md)：集成架构原则
- 本文：业务架构原则（能力地图/VSM/NFR/SLO）

---

## §2 Business Capability Map / 业务能力地图框架

### 2.1 能力域划分原则（永恒框架）

ZephyrAlpha 是**量化投资全生命周期管理系统**，覆盖：数据 → 研究 → 模型 → 策略 → 执行 → 报告。

**永恒框架**：**C1-C7（7个业务能力域）+ CC1-CC3（3个横切能力域）= 10个能力域**，映射到各物理域。

### 2.2 业务能力域（C1-C7，永恒分类）

| ID | 能力域 | 说明 |
|---|---|---|
| **C1** | 数据接入 | 市场数据接入、质量门禁、PIT、survivorship、血缘追踪 |
| **C2** | 因子研究 | Alpha因子、情绪、信号提取、因子注册表、IC-IR |
| **C3** | 风险控制 | 事前/事中/事后风控、VaR-CVaR、限额、止损 |
| **C4** | 策略决策 | 优化、再平衡、回测、战略配置 |
| **C5** | 执行交易 | OMS、SOR、执行、归因、TCA、review |
| **C6** | ML平台 | 模型生命周期、训练、serving、实验 |
| **C7** | 回测仿真 | 回测引擎、仿真、数字孪生、执行仿真 |

### 2.3 横切能力域（CC1-CC3，永恒分类）

| ID | 能力域 | 说明 |
|---|---|---|
| **CC1** | 治理合规 | 治理三层、规则执行、审计、漂移、反馈环、代码质量 |
| **CC2** | 安全防护 | 安全、LLM防御、行为审计、数据安全、自治权限 |
| **CC3** | 基础设施 | 基础设施、集成、共享、前端、报告、知识、智能、自治核心、运维、编排 |

### 2.4 能力域→物理域映射（派生数据）

> **注**：C1-C7+CC1-CC3 → 各物理域的具体映射不在本文档硬编码。真源在 `architecture_model/cross_cutting/capability_heatmap.yaml`，可视化见 `../01_global_architecture_diagram/global_capability_heatmap.md`（自动派生）。

---

## §3 Value Stream Map 方法论 / 价值流图方法论

### 3.1 VSM 核心概念（永恒框架）

本节把 §2 的能力域落到**时间维度 + 交接维度 + 浪费维度**的 Value Stream Map（VSM，精益/TOGAF 核心构件）。

**图例（永恒定义）**：
- **LT**（Lead Time）= 工件从到达工序到离开工序的**总耗时**（含等待）
- **PT**（Process Time）= 实际**增值加工**时间（不含等待）
- **%C&A**（Complete & Accurate）= 下游第一次接收就**可用且正确**的比例

### 3.2 标准价值流阶段（永恒序列）

量化投资系统的标准价值流（顺序固定）：

1. **Data Ingest**（C1）→ 原始数据入仓
2. **Factor Research**（C2）→ 因子假设与特征工程
3. **Factor Library**（C2）→ 因子入库与质量断言
4. **Model Train/Deploy**（C6）→ 模型训练与部署
5. **Signal Generation**（C2）→ 信号 payload 发布
6. **Portfolio Construction**（C4）→ 目标仓位
7. **Pre-trade Risk**（C3）→ 风控审批
8. **Order Submission**（C5）→ 券商 ACK
9. **Fill & Reconcile**（C5）→ 成交与对账
10. **Attribution**（C5）→ PnL + 归因报告
11. **Feedback loop**（C2+CC1）→ 研究结论 / KB决策候选

> **注**：各阶段的具体 LT/PT/%C&A 数字是 derived data，由运营态 metrics 自动采集，不在本文档硬编码。

### 3.3 关键交接点 Handoff 治理原则（永恒）

Handoff 是 VSM 中最易产生**信息损失 + 责任真空 + 数据污染**的点，必须显式标注契约。

**永恒 Handoff 列表**：

| # | Handoff | 上游 → 下游 | 风险 | 治理手段 |
|---|---------|------------|------|---------|
| **HO-1** | Vendor → Data Lake（市场数据入仓）| C1 | 字段漂移、survivorship、迟到数据覆盖历史 | ACL + PIT三字段 + immutable append |
| **HO-2** | Research → Factor Library（研究→生产）| C2 | 研究环境灰带代码进生产、look-ahead bias | ACL隔离 + fitness functions + 三断言 |
| **HO-3** | Signal → Pre-trade Risk（信号→风控）| C2→C3 | 信号绕过风控、限额不同步 | 强制性Pre-trade gate + Idempotency Key |
| **HO-4** | Portfolio → Broker（组合→券商）| C4→C5 | **订单重发重复**（量化红线）| 幂等设计 + broker ACK回执持久化 |
| **HO-5** | Fill → Attribution / Feedback（成交→归因→研究）| C5→C2 | 反馈断链（归因洞察没回到因子库）| Decision log + 知识库沉淀 |

> **注**：Handoff 详细契约（含"交接物"列、上游→下游 Stakeholder 映射）见 `architecture_model/cross_cutting/value_stream_map.yaml`（从 business_architecture.md §4.3 迁移）。

### 3.4 精益七浪费识别原则（永恒框架）

按精益七大浪费（等待/返工/过度加工/传输/库存/动作/缺陷）识别 VSM 中的瓶颈与浪费点。

**永恒约束**：每个阶段必须能被映射到至少一种浪费类型，便于持续改进。

> **注**：当前阶段识别的具体瓶颈/浪费实例（B1-B6，含影响阶段、当前状况、改进方向）见 `architecture_model/cross_cutting/value_stream_map.yaml`（从 business_architecture.md §4.4 迁移）。

### 3.5 横向治理贯穿全链（永恒）

- CC1 治理&合规域 — Policy control + KB决策链 + AI Operator registry（预留）
- C3 风控域 — 每阶段的风险控制策略（pre/in/post-trade）
- CC3 基础设施域（含人机交互 D_FRONTEND、知识管理 D_KNOWLEDGE）— 协作知识沉淀（AI会话上下文、prompt资产、经验教训）
- C2 因子&信号域 — 因子库质量门禁、信号注册表贯穿研究→生产

---

## §4 Non-functional Requirements (NFR) 定位原则

### 4.1 三大定位原则（永恒）

**先立边界再定数字**：

1. **Non-HFT 定位**：不追求微秒/毫秒级；延迟单位为**秒/分钟/小时**。若未来接入L1行情或组合规模超阈值（决策快照：当前阈值=$10M），NFR整体需重写。
2. **市场时段 vs 非市场时段分层**：可用性/延迟SLO只在**市场时段（含盘前盘后缓冲；决策快照：当前=30min）**严格执行；非市场时段为best-effort。
3. **可审计 ≫ 可用性**：当前阶段（单人无外部用户）若可用性与可审计冲突，必须选可审计。

### 4.2 NFR 类别框架（永恒分类）

| 类别 | 要求 | 当前阶段定位 |
|------|------|------|
| **Latency / 延迟** | Non-HFT；秒级—分钟级batch；端到端signal→order 具体SLO见 value_stream_map.yaml | 不追求微秒级 |
| **Availability / 可用性** | 市场时段严格 / 非市场时段best-effort；具体SLO见 value_stream_map.yaml | 单人操作，非24/7 |
| **Auditability / 可审计性** | Full decision trail, immutable KB决策, 七维度decision logs | **高优先级**（不可降）|
| **Compliance / 合规性** | Personal-scale；future multi-investor triggers stricter | 当前最简，留扩展口 |
| **Maintainability / 可维护性** | Single operator + AI collab；docs-as-code | 高优先级 |
| **Security / 安全性** | Personal scale；密钥管理、无公开暴露 | 见 security_principles.md |
| **Data Quality / 数据质量** | PIT/survivorship/lineage三断言；完整度/一致性/及时性三维度 | 高优先级（因子与回测可信度的前置）|

> **注**：各类别的具体目标值（如 "p99≤90s"）是 derived data，由 SLO 矩阵维护，不在本文档硬编码。

### 4.3 SLA / SLO / SLI 术语铁律（永恒）

**术语铁律**（永久约束，禁用混用）：

- **SLA**=对外承诺（当前单人，无外部合同→大部分标"internal commitment"）
- **SLO**=内部目标（可量化）
- **SLI**=实际测量指标（可落到metric）

**测量/上报位置**：所有SLI接入可观测性架构（由CC3 基础设施域含可观测性 D_INFRA_TELEMETRY 填充，用 Metrics/Logs/Traces 三支柱）。

### 4.4 SLO 升级触发条件（永恒——何时整体重写）

以下任一条件触发 SLO 表**整体重写**（非局部调整）：

1. 接入L1行情 / portfolio 规模超阈值（决策快照：当前阈值=$10M）→ 整体时延SLO从秒级压缩到毫秒级
2. 合伙人或监管激活 → SLA列从internal转对外承诺
3. 引入实时流架构（事件总线）→ 从batch语义改为streaming语义
4. 任一SLO**连续3个月**未达标 → 触发root-cause KB决策 + 目标值重评

### 4.5 SLO Auditability 铁律（永恒不可降）

| SLO | 定义 | 违约后果 |
|-----|------|---------|
| **SLO-Audit** | KB决策链完整、AI协作决策日志七维度覆盖 | **0容忍**：任何违约阻塞merge |

KB决策 append-only 铁律：100%（永恒不可降）。AI决策日志七维度覆盖率与 Git commit→KB决策双向索引覆盖率为 SLO 目标值，具体数值见 value_stream_map.yaml。

---

## §5 Business constraints / 业务约束与政策红线

> 完整约束真源在 [architecture_principles.md](architecture_principles.md)（R1-R4安全红线 + 准入铁律）。

**永恒约束清单**：

| 约束 | 说明 | 真源 |
|------|------|------|
| **Single canonical source** | `docs/`是唯一真源 | KBG-0001 |
| **Append-only decision records** | 已接受决策只能被supersede，不可删改 | KBG-0002 |
| **Markdown + Git** | 所有文档文本格式，版本化管理 | KBG-0001 |
| **Personal-scale initially** | 初始单账户、个人资金、不对外募资 | — |
| **Deferred activation** | 安全/合规/SRE域 deferred until external investors or live trading | — |

---

## §7 视图边界 / Boundaries

### 7.1 本文档覆盖

- 业务能力地图框架（C1-C7+CC1-CC3）（§2）
- Value Stream Map 方法论（VSM 概念、Handoff 治理、精益七浪费）（§3）
- NFR 定位原则与 SLO/SLA/SLI 术语铁律（§4）
- 业务约束与政策红线（§5）

### 7.2 本文档不覆盖（由其他系统维护）

| 内容 | 真源 |
|------|------|
| 全域→能力域映射 | `architecture_model/cross_cutting/capability_heatmap.yaml` |
| 能力成熟度评分（L0-L5） | `architecture_model/cross_cutting/capability_heatmap.yaml` + `../01_global_architecture_diagram/global_capability_heatmap.md`（自动派生）|
| VSM 阶段指标 + Handoff 契约 + 瓶颈 B1-B6 | `architecture_model/cross_cutting/value_stream_map.yaml` |
| SLO 目标值矩阵（SLO-1~SLO-7）+ SLA 现实 | `architecture_model/cross_cutting/value_stream_map.yaml` |
| 业务约束完整列表 | `architecture_principles.md`（R1-R4）|

### 7.3 与其他原则文档关系

- [capability_maturity_principles.md](capability_maturity_principles.md)：能力成熟度方法论
- [data_principles.md](data_principles.md)：数据架构原则
- [security_principles.md](security_principles.md)：安全架构原则
- [integration_principles.md](integration_principles.md)：集成架构原则
- 本文：业务架构原则（能力地图/VSM/NFR/SLO）

---

> **文档维护原则**：本文档只包含永恒指导原则。任何随 Phase 演进、能力域映射变化、SLO 目标值更新的内容，均不应写入本文档——它们由各自自动化系统维护。
