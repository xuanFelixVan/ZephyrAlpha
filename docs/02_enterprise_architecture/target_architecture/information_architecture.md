---
module_id: VIEW-02-INFORMATION-ARCH
title: Target Architecture — Information Architecture / 目标架构：信息架构
doc_type: architecture_view
status: Active
version: 1.3.0
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
valid_from: 2026-04-17
superseded_by: null
supersedes: null
related_rationale: R26, R27, R28, R29, R30, R44
related_open_questions: []
tags:
- information-architecture
- togaf
- ia
- docs-structure
- document-lifecycle
- drawer-taxonomy
summary: TOGAF Information Architecture 视图。回答：docs/ 有哪些信息资产抽屉、分类依据、抽屉间关系、文档生命周期（workspace→review→canonical）、元数据标准。从原
  target-information_architecture.md §3 完整迁移。v1.2.0：K1 SRE 抽屉转 planned（含激活条件）。
date: '2026-04-22'
ttl: permanent
---

# Target Architecture — Information Architecture （被恢复）
# 目标架构：信息架构（IA View）

---

## 1. Purpose of this view / 本视图的用途

The Information Architecture answers:

信息架构视图回答：

- What information assets exist in `docs/`? (Drawer taxonomy / 抽屉分类体系)
- How are they classified and why? (Classification rationale / 分类依据)
- How do they relate to each other? (Drawer relationships / 抽屉关系)
- How do documents flow through their lifecycle? (Document lifecycle / 文档生命周期)
- What metadata standard governs all documents? (Metadata standard / 元数据标准)

This view is **driven by** the Business Architecture (what capabilities determine what to document) and **drives** the Application Architecture (data distribution determines application boundaries).

本视图由业务架构**驱动**（能力决定记录什么），并**驱动**应用架构（数据分布决定应用边界）。

---

## 2. `docs/` complete drawer taxonomy / `docs/` 完整抽屉体系

> Classification rationale by layer: see §3. Maturity status per drawer: see §5.

> 分类依据分层说明见 §3。每个抽屉的成熟度状态见 §5。

- `00_governance` — Governance control: how the system is managed / 治理总控：系统如何被管理
  - `charters` — Charters and general principles / 宪章与总则
  - `registers` — Registers and canonical source registrations / 注册表与真源登记
  - `playbooks` — Scenario operation manuals / 场景操作手册
  - `policies` — Governance policies / 治理政策
  - `operating-model` — Operating mechanisms and responsibility models / 运行机制与职责模型
- `01_policies_and_standards` — Policies and standards: defines qualified artifact standards / 政策与标准：定义合格产物标准
  - `document-standards` — Document standards / 文档标准
  - `blueprint-standards` — Blueprint standards / 蓝图标准
  - `construction-standards` — Construction standards / 施工标准
  - `metadata-standards` — Metadata standards / 元数据标准
  - `audit-standards` — Audit standards / 审计标准
- `02_enterprise_architecture` — Enterprise architecture: full-system overall architecture canonical source / 企业级架构：全系统总体架构真源
  - `adr` — Architecture Decision Records / 架构决策记录
  - `target-architecture` — Target architecture (this document set) / 目标架构（本文档组）
- `03_domain_architecture` — Domain architecture: business domain boundaries and relationships / 领域架构：各业务域边界与关系
  - `data-domain` — Data domain architecture / 数据域架构
  - `research-domain` — Research domain architecture / 研究域架构
  - `model-domain` — Model domain architecture / 模型域架构
  - `strategy-domain` — Strategy domain architecture / 策略域架构
  - `execution-domain` — Execution domain architecture / 执行域架构
  - `risk-domain` — Risk domain architecture / 风险域架构
  - `reporting-domain` — Reporting domain architecture / 报告域架构
- `03_modules` — Module lifecycle documents: blueprint + construction plan + delivery records / 模块生命周期文档：蓝图+施工图+交付记录
  - `cross-layer` — Cross-layer documents / 跨层文档
  - `data` — L00 blueprints / L00 蓝图
  - `infra_ops` — L01 blueprints / L01 蓝图
  - `factor` — L02 blueprints / L02 蓝图
  - `signal` — L03 blueprints / L03 蓝图
  - `risk` — L04 blueprints / L04 蓝图
  - `pf_core` — L05 blueprints / L05 蓝图
  - `ex_core` — L06 blueprints / L06 蓝图
  - `reporting` — L07 blueprints / L07 蓝图
  - `frontend` — L08 blueprints / L08 蓝图
  - `research` — L09 blueprints / L09 蓝图
  - `compliance` — L10 blueprints / L10 蓝图
  - `ml_train` — L11 documents / L11 文档
  - `infra_ops` — L12 documents / L12 文档
  - `simulation` — L13 documents / L13 文档
- `06_security_and_identity` — Security and identity: permissions, identity, keys and security boundaries / 安全与身份：权限、身份、密钥与安全边界
  - `identity-and-access` — Identity and access control / 身份与访问控制
  - `secret-management` — Secrets and credentials / 密钥与凭证
  - `security-baselines` — Security baselines / 安全基线
  - `threat-models` — Threat models / 威胁模型
  - `security-operations` — Security operations / 安全运营
- `07_sre_and_platform_ops` — SRE and platform ops: stability, monitoring, recovery / SRE 与平台运维：稳定性、监控、恢复与平台运行
  - `runbooks` — Runbooks / 运行手册
  - `observability` — Observability / 可观测性
  - `incident-management` — Incident management / 事故管理
  - `release-management` — Release management / 发布管理
  - `business-continuity` — Business continuity / 业务连续性
- `03_modules/_b_track_interfaces/` — AI engineering and agent ops: agent rules, memory, routing, cost governance / AI 工程与代理运维：Agent 规则、记忆、路由与成本治理（原 07_ai_engineering，v3.2.0 合并至 03_modules）
  - `agent-architecture` — Agent architecture / Agent 架构
  - `memory-and-context` — Memory and context: index layer, distributed storage + centralized index / 记忆与上下文：索引层，分散存储+集中索引
    - `decision-memory` — Decision memory index / 决策记忆索引
    - `operational-memory` — Operational memory index / 操作记忆索引
    - `knowledge-memory` — Knowledge memory index / 知识记忆索引
    - `context-services` — Context services / 上下文服务
    - `memory-governance` — Memory governance / 记忆治理
  - `prompt-and-rules` — Prompts and rules / Prompt 与规则
  - `model-routing-and-cost` — Model routing and cost / 模型路由与成本
  - `agent-observability` — Agent observability / Agent 可观测性
  - `mcp-and-tooling` — MCP and tooling / MCP 与工具体系
  - `handoff-and-onboarding` — Handoff and onboarding / 交接与入职
- `09_data_platform` — Data platform: data ingestion, storage, quality, lineage / 数据平台：数据接入、存储、质量与血缘
  - `data-sources` — Data sources / 数据源
  - `schemas-and-contracts` — Schemas and contracts / Schema 与契约
  - `storage-and-lineage` — Storage and lineage / 存储与血缘
  - `data-quality` — Data quality / 数据质量
  - `data-services` — Data services / 数据服务
- `10_research_and_factor_lab` — Research and factor lab: research frameworks, factor research, experiments / 研究与因子实验室：研究框架、因子研究与实验
  - `research-framework` — Research framework / 研究框架
  - `factor-research` — Factor research / 因子研究
  - `event-studies` — Event studies / 事件研究
  - `experiment-design` — Experiment design / 实验设计
  - `research-notes` — Research notes / 研究笔记
- `11_model_and_ml_platform` — Model and ML platform: model training, deployment, monitoring, versioning / 模型与机器学习平台：模型训练、部署、监控与版本
  - `feature-store` — Feature store / 特征存储
  - `training` — Training / 训练体系
  - `evaluation` — Evaluation / 评估体系
  - `serving` — Serving / 模型服务
  - `model-monitoring` — Model monitoring / 模型监控
  - `model-registry` — Model registry / 模型注册
- `12_strategy_and_portfolio` — Strategy and portfolio: strategy logic, capital allocation, portfolio management / 策略与组合：策略逻辑、资金分配与组合管理
  - `strategy-library` — Strategy library / 策略库
  - `signal-rules` — Signal rules / 信号规则
  - `portfolio-optimization` — Portfolio optimization / 组合优化
  - `rebalancing` — Rebalancing / 再平衡
  - `backtesting` — Backtesting / 回测体系
- `13_execution_and_order_lifecycle` — Execution and order lifecycle: orders, fills, routing / 执行与订单生命周期：委托、成交、路由与执行链路
  - `broker-integration` — Broker integration / 券商接入
  - `order-management` — Order management / 订单管理
  - `execution-routing` — Execution routing / 执行路由
  - `execution-quality` — Execution quality / 执行质量
  - `trade-ledger` — Trade ledger / 交易账本
- `14_reporting_and_distribution` — Reporting and distribution: briefing generation, messaging, delivery / 报告与分发：简报生成、消息推送与结果分发
  - `daily-briefings` — Daily briefings / 每日简报
  - `execution-briefings` — Execution briefings / 执行简报
  - `portfolio-reports` — Portfolio reports / 组合报告
  - `distribution-channels` — Distribution channels / 分发渠道
  - `delivery-logs` — Delivery logs / 发送留痕
- `08_knowledge` — Knowledge base: long-term knowledge assets, AI-driven ingestion pipeline and reusable insights / 知识库：长期知识资产、AI 驱动的采集流水线与可复用认知
  - `_standards` — KMS entry schema and classification standards / KMS 条目 Schema 规范与分类标准
  - `01_raw_intake` — Layer 2 Collection output: raw entries awaiting triage (G1 output) / Layer 2 采集输出：待分拣原始条目（G1 输出）
    - `papers` — Academic papers (arXiv, SSRN, NBER) / 学术论文
    - `opensource` — Open source projects (GitHub, PyPI) / 开源项目
    - `blueprints` — Old-tree blueprints (C workflow batch input) / 旧体系蓝图（C 工作流批量输入）
    - `reports` — Industry research reports / 行业研究报告
    - `practices` — Best practice articles and talks / 最佳实践文章与演讲
    - `operations` — Operational experience from L07 / 来自 L07 的运营经验
    - `_failed` — Failed ingestion records / 采集失败记录
  - `02_triaged` — Layer 3 Triage output: classified entries (G2 output) / Layer 3 分拣输出：已分类条目（G2 输出）
    - `high_value` — High value, ai_triage_score ≥ 0.7, enters deep analysis / 高价值，进入深度分析
    - `archived` — Medium value, archived for reference / 中等价值，归档备查
    - `rejected` — Rejected: low quality, duplicate, or irrelevant / 拒绝：低质/重复/不相关
  - `03_analyzed` — Layer 5 Analysis output: deeply evaluated entries (G3 output) / Layer 5 分析输出：深度评估后条目（G3 输出）
  - `04_future_capabilities` — Future capability library: deferred activation entries and P3 blueprints (C7 input) / 未来能力库：延迟激活条目与 P3 蓝图（C7 输入）
  - `05_active_research` — Active research topics: cross-entry thematic analysis / 在研专题：跨条目横向分析
  - `06_lessons_learned` — Lessons learned from failed activations and operational reviews (G5 failure graduation) / 经验教训：失败激活与运营复盘（G5 失败升格）
  - `07_best_practices` — Validated best practices: entries graduated with empirical evidence (G5 success) / 已验证最佳实践：经实证通过的条目（G5 成功升格）
  - `08_glossary_and_taxonomy` — Quantitative finance glossary and KMS classification taxonomy / 量化金融术语表与 KMS 分类体系
  - `indexes` — Multi-dimension index files (auto-generated by CI) / 多维度索引文件（CI 自动生成）
- `16_compliance_and_legal` — Compliance and legal: regulatory requirements and legal boundaries / 合规与法务：法规要求与法律边界
  - `regulatory-mapping` — Regulatory mapping / 监管映射
  - `compliance-requirements` — Compliance requirements / 合规要求
  - `legal-boundaries` — Legal boundaries / 法律边界
  - `disclosures` — Disclosures / 披露口径
  - `record-retention` — Record retention / 留存要求
- `17_risk_and_controls` — Risk and controls: risk policies and control frameworks / 风险与控制：风险政策与控制框架
  - `risk-policies` — Risk policies / 风险政策
  - `risk-metrics` — Risk metrics / 风险指标
  - `limits-and-thresholds` — Limits and thresholds / 限额与阈值
  - `stress-testing` — Stress testing / 压力测试
  - `control-library` — Control library / 控制库
- `18_audit_and_evidence` — Audit and evidence: inspection results, trails, evidence chains / 审计与证据：检查结果、留痕与证据链
  - `audit-reports` — Audit reports / 审计报告
  - `scan-results` — Scan results / 扫描结果
  - `session_logs` — Session logs / 会话日志
  - `evidence-packs` — Evidence packs / 证据包
  - `state-and-tracking` — State and tracking / 状态与追踪
- `19_development_workspace` — **RETIRED 2026-06-26** / 已退役：原"开发工作区"（持续讨论、任务书、工作草稿与待升格文档）。过程区已统一迁移至 `docs/_working/`（ttl=task_bound）；原目录已删除。下方历史子目录清单仅保留可追溯性，引用均已失效。
  - ~~`taskbooks`~~ / ~~`working-designs`~~ / ~~`structure-and-mapping`~~ / ~~`open-questions`~~ / ~~`review-ready`~~ / ~~`adr-drafts`~~ / ~~`roadmaps`~~ / ~~`risk-registers`~~ / ~~`session_logs`~~ / ~~`archive`~~（共 10 子目录，随父目录退役一并删除）
- `99_archive` — Archive: inactive but retained assets / 归档：非活跃但需保留的资产
  - `retired-docs` — Retired documents / 退役文档
  - `retired-blueprints` — Retired blueprints / 退役蓝图
  - `historical-reports` — Historical reports / 历史报告
  - `legacy-structure` — Legacy structure / 旧结构存档

---

## 3. Drawer classification rationale / 抽屉分类依据

20 top-level directories use **mixed classification by three governance attributes** (Matrix Organization — standard in large enterprises):

20 个顶级目录按**三种治理属性混合分类**（Matrix Organization——大型企业标准做法）：

| Category / 类别 | Directories / 目录编号 | Nature / 性质 |
|----------------|----------------------|--------------|
| **Governance layer / 治理层（横向贯穿）** | `00`, `01`, `16`, `17`, `18` | Cross-domain, governs everything / 跨业务域，管所有东西 |
| **Architecture layer / 架构层（中枢）** | `02`, `03`, `04`, `05` | Architecture design, blueprints, construction / 架构设计、蓝图、施工 |
| **Business domain / 业务域（垂直抽屉）** | `09`, `10`, `11`, `12`, `13`, `14` | Quantitative investment value chain layers / 量化投资价值链各层 |
| **Platform capability / 平台能力层** | `06`, `07`, `08` | Security, SRE, AI engineering (serve all domains) / 安全、SRE、AI 工程（服务所有业务域）|
| **Knowledge layer / 知识沉淀层** | `15` | Cross-time, reusable cognition / 跨时空、可复用的认知 |
| **In-progress / 过程区** | `19` | Discussion, draft, pending / 讨论中、未定稿 |
| **Historical / 历史区** | `99` | Archived, retired / 归档、退役 |

> Why not purely domain-based? Some capabilities (compliance, audit, AI) must act simultaneously across multiple business domains. Pure domain classification scatters compliance docs across 10+ directories, violating single canonical source.
>
> 为什么不纯粹按业务域分？因为有些能力（合规、审计、AI）需要同时作用于多个业务域。纯业务域分类会造成"合规文档分散在 10+ 个目录里"，违反单一真源原则。

---

## 4. Drawer relationship diagram / 抽屉关系图

```
         ┌──────────────── Governance layer / 治理层 ──────────────┐
         │ 00_governance  01_standards                            │
         │ 16_compliance  17_risk  18_audit                      │
         └───────┬─────────────────────────────────────────────┘
                 │ Policies / standards / risk controls
                 │ 政策 / 标准 / 风控
                 ↓
         ┌──────────────── Architecture layer / 架构层 ───────────┐
         │ 02_enterprise  03_domain                              │
         │ 03_modules                                         │
         └───────┬─────────────────────────────────────────────┘
                 │ Blueprints / construction plans / 蓝图 / 施工图
                 ↓
         ┌──────────────── Business value chain / 业务价值链 ──────┐
         │ 09 → 10 → 11 → 12 → 13 → 14                          │ ← Core flow / 核心流动
         │ Data  Research  Model  Strategy  Exec  Report         │
         │ 数据  研究      模型   策略      执行  报告             │
         └───────┬─────────────────────────────────────────────┘
                 │ Runtime support / 运行时支撑
                 ↓
         ┌──────────────── Platform capability / 平台能力层 ───────┐
         │ 06_security  07_sre  08_ai_engineering                │ ← Serves all domains / 服务所有业务域
         └──────────────────────────────────────────────────────┘
                 ↓ Accumulate / 沉淀
         ┌──────────────── Knowledge layer / 知识层 ──────────────┐
         │ 08_knowledge                                     │
         └──────────────────────────────────────────────────────┘
                 ↑ In-progress / 讨论区       ↓ Expired / 过期
              19_workspace               99_archive
```

> **📊 文档拓扑图**：见 [`diagrams/docs_drawer_topology.mmd`](diagrams/docs_drawer_topology.mmd) — docs/ 20 抽屉分类拓扑

---

## 5. Document lifecycle / 文档生命周期

```
┌────────────────────┐     ┌───────────────────┐     ┌──────────────────┐
│ 19_workspace/      │ ──→ │ 19_workspace/     │ ──→ │ 02_enterprise    │
│ working-designs/   │Stabilize│ review-ready/ │Promote│ /03_modules       │
│ taskbooks/         │     │                   │     │ etc.（canonical）│
│ open-questions/    │     │                   │     │                  │
└────────────────────┘     └───────────────────┘     └─────────┬────────┘
                                                               │
                                                               │ Superseded / 失效替代
                                                               ↓
                                                     ┌──────────────────┐
                                                     │ 99_archive/      │
                                                     │ retired-docs/    │
                                                     └──────────────────┘
```

Status machine / 状态机：`draft → in_discussion → review_ready → active/accepted → superseded/deprecated`

Full status machine spec: ~~`19_development_workspace/structure-and-mapping/discussion-document-standard.md §6.3`~~（文件随 `19_development_workspace` 目录于 2026-06-26 退役删除，引用已不可达，标注作废）

完整状态机规范：~~`19_development_workspace/structure-and-mapping/discussion-document-standard.md §6.3`~~（同上，已作废）

---

## 6. Organizational memory system position / 组织记忆系统在全貌中的位置

The organizational memory system belongs to `03_modules/_b_track_interfaces/memory-and-context/`.

组织记忆系统属于 `03_modules/_b_track_interfaces/memory-and-context/`。

Current status: under re-discussion (OQ-001, OQ-002, OQ-010 reopened). Three prerequisite questions pending:

当前状态：重新讨论中（OQ-001、OQ-002、OQ-010 已重新打开）。三个前提问题待定：

1. Where should memory system governance policies live? / 记忆系统的治理政策应该放在哪里？
2. Where should memory system execution code live? / 记忆系统的执行代码应该放在哪里？
3. Where should memory system indexes live? / 记忆系统的索引应该放在哪里？

---

## 7. Current workspace key navigation / 当前工作区关键入口

| File / 文件 | Purpose / 用途 |
|------------|--------------|
| `docs/_working/` | 过程区入口（task_bound）：承接原 `19_development_workspace` 的工作草稿、任务卡、session log 等过程产物 / Process area: working drafts, task cards, session logs (replaces retired workspace) |
| `docs/01_policies_and_standards/_registry/vocabularies/terminology_mapping.yaml` | 术语映射表（正式位置，原表指向 `19_development_workspace/...` 路径已失效）/ Terminology mapping (canonical location) |

> **作废说明 / Obsolete entries (2026-06-26)**：原表 7 项入口全部指向 `19_development_workspace/` 下文件或不存在路径（`architecture-rationale-log.md` 经核实不存在），随目录退役一并失效，仅保留可追溯性：
> ~~`19_development_workspace/index.md`~~ · ~~`19_development_workspace/taskbooks/taskbook.md`~~ · ~~`02_enterprise_architecture/architecture-rationale-log.md`~~ · ~~`19_development_workspace/structure-and-mapping/discussion-document-standard.md`~~ · ~~`19_development_workspace/structure-and-mapping/document-triage-guide.md`~~ · ~~`19_development_workspace/structure-and-mapping/handoff-log.md`~~ · ~~`19_development_workspace/open-questions/open-questions-register.md`~~

---

## 8. Metadata standard / 元数据标准

All documents under `docs/` must comply with `discussion-document-standard.md` v2.0.0:

所有 `docs/` 下文档必须遵守 `discussion-document-standard.md` v2.0.0：

- **Single frontmatter schema** (14 fields) / 单一 frontmatter schema（14 个字段）
- **Phased required fields** (status determines which fields are required) / 分阶段必填（status 决定哪些字段必填）
- **Controlled `doc_type` vocabulary** (10 valid values) / 受控 `doc_type` 词表（10 个合法值）
- **Unified `module_id` naming**: `<DOMAIN>-[<SUBDOMAIN>-]<TYPE>-<NNN>` / 统一 `module_id` 命名
- **Append-only supersedes rule** (no strikethroughs) / Append-only supersedes 规则（禁用删除线）

---

## 9. Drawer maturity status / 目录成熟度状态

| Directory / 目录 | Status / 状态 | Notes / 说明 |
|----------------|--------------|-------------|
| `00_governance` | planned | 当前最简政策已散落各处，待正式整理时激活 |
| `01_policies_and_standards` | **partial** | 仅 `document-standards` 有 v2.0.0（workspace 版） |
| `02_enterprise_architecture` | **partial** | `adr/` 已激活（KBG-0001/0002/0003）；`target_architecture/` 已激活（本文档组）|
| `03_domain_architecture` | planned | 核心业务代码开始实施后激活 |
| `03_modules` | planned | 按业务域激活（优先级对应业务价值链顺序），模块生命周期文档（蓝图含施工指引+交付） |
| `06_security_and_identity` | deferred | 单人独立操作期不激活；接入真实资金或多用户后激活 |
| `07_sre_and_platform_ops` | planned | **K1 (2026-04-19)**：已从 `deferred` 升为 `planned`。**激活条件（任一满足即激活）**：① 接入真实券商 API（Broker API EXT-001 进入生产）；② 系统月可用性需求 > 99.9%（04-TA §5.2 SLO-6 触发）；③ 多 Agent 并发协同 > 3 个同时运行。激活后优先建立：`runbooks/` 基础操作手册 + `observability/` 指标接入（链接 04-TA §10 H14）。|
| `03_modules/_b_track_interfaces/` | **partial** | `handoff-log` 骨架已有；`memory-and-context/` 等 planned（原 07_ai_engineering）|
| `09_data_platform` | planned | 首次接入真实数据源时激活 |
| `10_research_and_factor_lab` | planned | 开始因子研究时激活 |
| `11_model_and_ml_platform` | planned | 引入 ML 模型时激活 |
| `12_strategy_and_portfolio` | planned | 首个完整策略成型时激活 |
| `13_execution_and_order_lifecycle` | planned | 接入券商 API 后激活 |
| `14_reporting_and_distribution` | planned | 产生首个可分发报告时激活 |
| `08_knowledge` | planned | 有跨项目可复用知识时激活 |
| `16_compliance_and_legal` | deferred | 仅个人使用期不激活；对外发行产品时激活 |
| `17_risk_and_controls` | planned | 第一个真实交易前必须激活 |
| `18_audit_and_evidence` | **partial** | 已有 `scripts/governance/` 产物流入；正式登记表待建 |
| `19_development_workspace` | **retired** | 2026-06-26 退役；过程区迁移至 `docs/_working/` |
| `99_archive` | planned | 出现首个退役文档时激活 |

**Status semantics / 状态语义**:

- **`active`** — Frequently written and maintained / 正在频繁写入与维护
- **`partial`** — Directory exists, some subdirectories activated / 目录存在，部分子目录已激活
- **`planned`** — Reserved in IA, activates after business milestone / 在 IA 里已预留，等业务里程碑触发后激活
- **`deferred`** — Confirmed not needed now; revisit when trigger condition is met / 确定现阶段不需要，未来触发条件满足后再评估

---

## 11. Architecture Runway / 架构预留通道

> 以下预留通道为未来 P3 能力激活后的挂载点。本节不实现任何具体逻辑，仅记录
> "将来何处扩展、何条件触发、引用哪个 P3 条目"。
> P3 完整条目索引：`docs/08_knowledge/04_future_capabilities/p3-blueprint-index.md` [待创建]

| ID | 能力描述 | 挂载点 | 激活触发条件 | P3 索引 |
|---|---|---|---|---|
| RW-IA-01 | 多模态因子信息对象 — 将文本/图像/数字融合因子纳入 `10_research_and_factor_lab/` 信息体系，扩展 §3 抽屉定义与文档生命周期规则 | `§3 drawer: 10_research_and_factor_lab/` 子目录扩展 + §5 文档生命周期新增多模态类型 | NLP 因子（P2 L02）生产验证充分 + 图像/另类数据供应商接入完成 | P3-AI-018 [待创建] |
| RW-IA-02 | ESG 因子信息对象 — 在 `10_research_and_factor_lab/` 下建立 ESG 因子专属子目录，定义数据质量与血缘标准 | `§3 drawer: 10_research_and_factor_lab/esg-factors/`（新增子目录规划）| ESG 数据供应商接入（KBG-0005 G5 触发后评估）| P3-STR-008 [待创建] |
| RW-IA-03 | 知识图谱自动构建 — 在 `08_knowledge/` 建立知识图谱子层，定义实体/关系信息架构与 §6 跨抽屉引用规则扩展 | `§3 drawer: 08_knowledge/09_knowledge_graph/`（新增子目录规划）+ §8 元数据标准扩展 | KMS 条目 > 500 条 + 知识图谱基础设施完成（KBG-0005 G5 以上）| P3-AI-015 [待创建] |

---

## 10. Revision history / 修订记录

| Date / 日期 | Description / 说明 |
|------------|-------------------|
| 2026-04-17 | v1.0.0：从 DW-IA-DESIGN-001 §3（完整抽屉体系）+ §3.2（分类依据）+ §3.3（关系图）+ §3.4（生命周期）+ §3.5（记忆系统位置）+ §3.6（工作区导航）+ §3.7（元数据标准）+ §7（成熟度表）完整迁移建立。 |
| 2026-04-18 | v1.1.0：Sprint 3 E5：将 `08_knowledge` 子目录从 5 项（best-practices / lessons-learned / factor-knowledge / strategy-knowledge / terminology）展开为完整 10 层 KMS 目录体系（含 `_standards/` + `01_raw_intake/` 6 个子目录 + `02_triaged/` 3 个子目录 + `03_analyzed/` / `04_future_capabilities/` / `05_active_research/` / `06_lessons_learned/` / `07_best_practices/` / `08_glossary_and_taxonomy/` / `indexes/`），与 E4 创建的物理目录结构对齐。 |
| 2026-04-19 | v1.2.0：K1 — §9 成熟度表 `07_sre_and_platform_ops` 从 `deferred` 升为 `planned`，新增三条激活条件（接入真实券商 API / 月可用性需求 >99.9% / 多 Agent 并发 >3），并链接 04-TA §10 H14 Observability（R44）。 |
| 2026-04-19 | v1.3.0：S3 — 追加 §11 Architecture Runway 预留通道（3 条信息/数据类 P3 预留，含多模态因子、ESG 因子、知识图谱自动构建，R60）。 |
