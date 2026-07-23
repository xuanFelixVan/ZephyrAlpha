---
classification: confidential
date: '2026-06-26'
doc_type: index
generated: '2026-06-26'
layer: cross_layer
merged_from: README.md + index.md
module_id: ARCH-006
status: Active
title: Target Architecture — Navigation Guide / 目标架构导航
version: 3.0.0
depends_on:
  - {target: EA-INDEX, at: "§子目录", why: "父级 EA 索引——target_architecture 为其子目录"}
tags:
- index
- navigation
- domain-driven
- depgraph-derived
summary: v3.0.0：基于§2.1裁定，导航改为53域索引+全景图派生视图说明。原14层分区导航废弃。
ttl: permanent
---

# Target Architecture — Navigation Guide （被恢复）
# 目标架构 — 导航指南

---

## 责任声明（Single Responsibility）

本目录只存放：**目标架构视图（TOGAF）— overview 到 dimension-audit-matrix + architecture_model/ + diagrams/**。

---

## 1. What is this document set / 本文档组是什么

This is the **canonical Architecture Description Set** for ZephyrAlpha 2.0.

采用 **ISO 42010 + TOGAF 四视图 + C4 合成方案**：

- **ISO 42010** — 定方法论：Architecture Description 由多个 View 组成
- **TOGAF** — 定四层视图：Business / Information / Application / Technology
- **C4 Model** — 定应用视图的可视化：系统上下文（L1）和容器（L2）

> **v3.0.0变更**：物理代码组织以53域为准（§2.1裁定），14层降级为域属性。结构化数据由depgraph派生。

---

## 2. 域索引（53域，数据源：depgraph）

> 本索引由`scripts/governance/d5_architecture/generators/generate_domain_index.py`派生。
> 完整域清单见`generated/domain_index.md`。

### `L0_infrastructure` (5域)

| 域ID | 域名称 | 节点数 | 描述 |
|------|--------|:---:|------|
| `D_INFRA_A2A` | a2a_communication | 114 | A2A Card注册与发现(card_registry) |
| `D_INFRA_OPS` | resource_optimization | 34 | 资源优化引擎 |
| `D_INFRA_RECOVERY` | rollback_recovery | 107 | 双轨Checkpoint(git commit + DB dump：SQLite JSONL / pg_dump) |
| `D_INFRA_RUNTIME` | runtime_integration | 145 | 运行时集成层 |
| `D_INFRA_TELEMETRY` | observability_profiling | 51 | 系统遥测采集(system_telemetry) |

### `L1_foundation` (15域)

| 域ID | 域名称 | 节点数 | 描述 |
|------|--------|:---:|------|
| `D_ALT_DATA` | 另类数据 | 8 | 另类数据域。负责另类数据源的接入与处理，包括卫星图像、社交媒体情绪、供应链数据、ESG数据。 |
| `D_AUTONOMY_CORE` | agent_communication | 176 | A2A Card注册与发现(card_registry) |
| `D_BEHAVIORAL_AUDIT` | 行为审计 | 79 | 行为审计域(从D_SECURITY拆出,behavioral_auditor) |
| `D_DATA_ENG` | 数据工程(增值+融合+知识) | 7 | 数据工程域。负责数据增值处理、多源数据融合与知识提取，包括ETL管线、特征工程、数据融合引擎、知识图 |
| `D_DATA_GOV` | 数据治理(质量+血缘+参考) | 0 | 数据治理域。负责数据质量管理、数据血缘追踪与参考数据管理，包括数据质量门禁、血缘图谱、主数据管理、数 |
| `D_DATA_SEC` | 数据安全与契约 | 10 | 数据安全与契约域。负责数据安全策略、数据契约定义与执行，包括数据加密、访问控制、数据脱敏、数据契约验 |
| `D_FRONTEND` | 前端 | 23 | Web界面、可视化看板、交互组件。人机交互入口。 |
| `D_INTEGRATION` | pipeline_routing | 296 | M1-M11双管线路由 |
| `D_INTEGRATION_GATEWAY` | mcp_servers | 0 | 11个MCP服务端 + 1 Gateway |
| `D_MKT_DATA` | 行情数据(接入+存储) | 9 | 行情数据接入与存储域。负责市场行情数据的接入、存储与分发，包括实时行情、历史行情、多市场数据源的统一 |
| `D_OPS` | feedback-loop | 433 | 反馈收集器(collectors) |
| `D_REPORTING` | 报告 | 15 | 绩效报告、风险报告、合规报告、自定义报表。数据呈现层。 |
| `D_SECURITY` | adversarial_validation | 244 | 红蓝对抗验证 |
| `D_SECURITY_LLM` | llm_defense | 0 | L0供应链安全(模型验证/依赖扫描) |
| `D_SHARED` | shared_services | 296 | 事件总线(event_bus) |

### `L2_domain` (32域)

| 域ID | 域名称 | 节点数 | 描述 |
|------|--------|:---:|------|
| `D_ASHARE_SIGNAL` | ashare_signal | 7 | A股特色信号生成 |
| `D_AUDITTEST` | audit_test_suite | 152 | 审计单元测试(unit) |
| `D_AUTONOMY_PERM` | escalation | 70 | 规则驱动升级(EscalationEngine) |
| `D_BACKTEST` | 回测 | 7 | 历史回测、参数寻优、过拟合检测、绩效归因。策略验证引擎。 |
| `D_COMPLIANCE` | 合规 | 25 | 合规规则、交易限制、报告合规、监管对接。合规监管防线。 |
| `D_CROSS_ASSET` | 跨资产 | 11 | 跨资产策略与配置 |
| `D_DIGITAL_TWIN` | 数字孪生 | 8 | 数字孪生与虚拟市场仿真 |
| `D_EXEC_SIM` | 执行仿真 | 7 | Split from D_SIMULATION |
| `D_EX_CORE` | 执行核心 | 14 | 执行核心域。负责订单执行核心引擎，包括订单拆分、执行算法(VWAP/TWAP/Iceberg)、执行 |
| `D_EX_SOR` | 执行路由 | 7 | 执行路由域。负责智能订单路由(SOR)，包括多交易通道选择、流动性聚合、最优执行路径规划。 |
| `D_FACTOR` | 因子 | 17 | 因子计算、因子库、因子评价、因子正交化。Alpha挖掘引擎。 |
| `D_FUNDAMENTAL_SIGNAL` | fundamental_signal | 25 | 财务指标信号 |
| `D_GOVERNANCE` | lifecycle_management | 2831 | 模块生命周期钩子(hooks) |
| `D_GOV_AUDIT` | audit-trail | 188 | Merkle小时级完整性(merkle_hourly) |
| `D_GOV_DOCS` | architecture_docs | 127 | 架构模型文档(architecture_model) |
| `D_GOV_DRIFT` | drift_detection | 24 | 39个漂移检测器注册与调度 |
| `D_GOV_ENFORCEMENT` | rule_enforcement | 107 | 门禁引擎流程编排(GatePipeline/GateEngine) |
| `D_GOV_RULE` | rule_governance | 11 | 规则配置管理 |
| `D_GOV_SCRIPTS` | code_dedup | 416 | 代码去重检测 |
| `D_INTELLIGENCE` | context_management | 56 | 上下文预算管理(context_budget/token_budget) |
| `D_KNOWLEDGE` | knowledge_management | 41 | 知识管线(ingest/triage/extract/activate/analyze) |
| `D_ML_SERVE` | 推理 | 7 | 机器学习推理域。负责ML模型推理服务，包括模型部署、在线推理、批推理、模型版本管理、A/B测试。 |
| `D_ML_TRAIN` | model_profiling | 12 | 模型性能画像 |
| `D_PF_ALLOC` | 组合分配 | 11 | 资产组合分配优化 |
| `D_PF_CORE` | 组合核心 | 44 | 组合核心域。负责投资组合核心引擎，包括组合优化器、风险预算分配、基准跟踪、再平衡引擎。 |
| `D_POSITION` | 仓位管理 | 8 | 持仓跟踪、仓位计算、盈亏归因、仓位调整。仓位账本。 |
| `D_RISK` | 风控 | 25 | 风险度量、风险限额、压力测试、实时风控。交易安全阀。 |
| `D_SELL_DECISION` | 卖出决策 | 7 | 卖出决策域。负责卖出时机判断与卖出策略执行，包括止盈止损策略、持仓时间优化、卖出信号聚合。 |
| `D_SIGLEGACY` | siglegacy | 0 | 信号遗留设计态节点（原 D-SIGNAL 拆分后遗留的设计态占位域） |
| `D_SIGQC` | signal_quality | 7 | 信号质量评估 |
| `D_SIMULATION` | 仿真 | 19 | 仿真引擎、场景生成、蒙特卡洛、回测模拟。策略验证沙箱。 |
| `D_TRADING` | 交易运营 | 163 | 交易会话、交易接口、交易日志、交易复盘。交易运营中枢。合规检查由D_GOV_ENFORCEMENT门 |

### `unassigned` (1域)

| 域ID | 域名称 | 节点数 | 描述 |
|------|--------|:---:|------|
| `D_GOV_REPAIR` | rollback | 0 | 双轨Checkpoint(git commit + DB dump：SQLite JSONL / pg_dump) |

---

## 3. 文件清单

| 文件 | 说明 |
|------|------|
| overview.md | 架构总览（v2.0.0：53域+全景图派生）|
| business_architecture.md | BA 业务架构视图 |
| information_principles.md → ../04_architecture_principles_decisions/ | IA 信息架构原则（原 information_architecture.md 已迁移） |
| technology_architecture.md | TA 技术架构视图 |
| capability_heatmap.md | 能力热力图正交视图（v2.0.0：53域×能力域）|
| data_architecture.md | DA 数据架构视图 |
| security_architecture.md | SEC 安全架构视图 |
| operations_architecture.md | OPS 运维架构视图 |
| governance_architecture.md | GOV 治理架构视图 |
| frontend_architecture.md | FE 前端架构视图 |
| dimension_audit_matrix.md | 12维架构质量评分矩阵（score_architecture.py 真源）|
| session_carryover_schema.md | AI会话接续Schema（contract 类型，暂放 target_architecture）|
| revision_history.md | 完整修订历史归档（index.md §10 完整版）|

---

## 4. 派生视图（generated/目录）

> 所有派生视图由`scripts/governance/d5_architecture/generators/`下的生成器从depgraph派生。

| 派生视图 | 生成器 | 数据源 | 说明 |
|---------|--------|--------|------|
| `generated/domain_index.md` | generate_domain_index.py | domains+nodes | 53域总览索引 |
| `generated/cross_domain_matrix.md` | generate_cross_domain_matrix.py | edges | 跨域依赖矩阵 |
| `generated/capacity_report.md` | generate_capacity_report.py | domains | 域容量报告 |
| `generated/design_vs_production.md` | generate_design_vs_production.py | nodes | 设计态vs运营态统计 |
| `generated/constraint_violations.md` | generate_constraint_violations.py | arch_constraints | 架构约束违规报告 |
| `generated/domains/*.md` | generate_domain_doc.py | nodes+edges | 单域架构文档（53个）|
| `generated/domains/*_dependency.mmd` | generate_domain_dependency_diagram.py | nodes+edges | 单域依赖图（53个）|

---

## 5. Document inventory / 文档清单

| File / 文件 | Layer / 层 | Answers / 回答的核心问题 | Primary audience / 主要读者 | Status / 状态 |
|------------|-----------|------------------------|--------------------------|--------------|
| `index.md`（本文） | — | 本文档组是什么？怎么读？ | 所有人 | active |
| `overview.md` | Cross-layer | 整体架构哲学？53域如何组织？ | 架构师、新加入者 | active |
| `business_architecture.md` | BA | 为谁服务？核心业务能力？ | 业务负责人 | active |
| [`information_principles.md`](../04_architecture_principles_decisions/information_principles.md) | IA | `docs/` 有哪些抽屉？ | 文档维护者、AI 协作者 | active |
| `technology_architecture.md` | TA | 用什么技术栈？ | SRE、实施者 | active |
| `capability_heatmap.md` 🔷 **正交视图 2** | Orthogonal | 53域能力成熟度热力图？ | 架构师、决策层 | active |
| `data_architecture.md` | DA | 业务数据对象？ | 量化研究员、数据工程师 | active |
| `security_architecture.md` | SEC | 安全域划分？IAM？ | 安全工程师、合规 | active |
| `operations_architecture.md` | OPS | 运维域全景？ | SRE、运维工程师 | draft |
| `governance_architecture.md` | GOV | 治理体系三层边界？ | 架构师、合规 | active |
| `frontend_architecture.md` | FE | 前端层分层？ | 前端开发者、架构师 | active |
| `dimension_audit_matrix.md` | Cross-layer | 12维架构质量评分 | 架构师、审计 | active |
| `session_carryover_schema.md` | Cross-layer | AI会话接续Schema | AI 协作者、架构师 | active |
| `diagrams/` | All | Mermaid 图源文件 | 所有人 | active |

---

## 6. Reading order / 推荐阅读顺序

**First time / 第一次读（5 分钟）**：`index.md`（本文）→ `overview.md` → `generated/domain_index.md`（53域总览）

**Architect / 架构师**：`overview.md` → `generated/domain_index.md` → 按域读`generated/domains/*.md`

**Developer / 开发者**：`../04_architecture_principles_decisions/application_principles.md` → `generated/domains/<相关域>.md` → `architecture_model/contracts/cross_layer_contracts.yaml`（集成点+接口契约）

**AI collaborator / AI 协作者**：`generated/domain_index.md`（全局索引）→ 按需读取`generated/domains/*.md` → `overview.md`（设计哲学）

---

## 7. View dependencies / 视图依赖关系

> **📊 视图依赖关系总览**：见 [`diagrams/readme_view_dependency_graph.mmd`](diagrams/readme_view_dependency_graph.mmd)

**正交视图说明**：`04ter`（capability_heatmap）是 TOGAF 10 视图之外的正交视图，提供能力成熟度的额外切片标注。原 `04bis` runtime_planes 正交视图已迁移至 [`runtime_planes_principles.md`](../04_architecture_principles_decisions/runtime_planes_principles.md) + [`runtime_planes.yaml`](../../../architecture_model/cross_cutting/runtime_planes.yaml)。

**反向约束**：TA 成本限制 → AA 范围 → IA 范围 → BA 野心。

---

## 8. View vs YAML SSoT — key distinction / 视图与 YAML SSoT 的区别

| Type / 类型 | Style / 风格 | Purpose / 用途 |
|------------|-------------|---------------|
| **View** (00–10) | Narrative: explains **why** | For humans, conveys architectural intent |
| **YAML SSoT** (architecture_model/) | Structured: lists **what** | For machines, AI, and CI gates |
| **派生视图** (generated/) | 派生: 从depgraph生成 | 结构化数据可视化，禁止手编 |

---

## 9. Provenance / 来源说明

本文档组由 `DW-IA-DESIGN-001` 拆分升格而来。v3.0.0 基于§2.1裁定重写为53域索引+全景图派生。

---

## 10. Revision history / 修订记录

> 完整历史见 [revision_history.md](revision_history.md)。本处仅保留最近 3 次修订。

| Date / 日期 | Description / 说明 |
|------------|-------------------|
| 2026-06-26 | **v3.0.0（DM-200912 Phase4-A）**：基于§2.1裁定重写——导航改为53域索引+派生视图说明；新增§2域索引、§4派生视图；废弃14层分区导航。 |
| 2026-05-06 | v2.2.0：双树与 SCOPE/SSoT 地图对齐。 |
| 2026-05-02 | v2.1.0：修复 4 项 SSoT 对齐问题。 |

## 排除规则（不应放入本目录的内容）

- ❌ 治理规范 → `01_policies_and_standards/`
- ❌ KB 决策记录 → KB:decisions namespace

## 父级目录

- 父级：[02_enterprise_architecture](../index.md)
