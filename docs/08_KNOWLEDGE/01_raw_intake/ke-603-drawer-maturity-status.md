---
module_id: KE-543
status: active
title: 9. Drawer maturity status / 目录成熟度状态
category: documentation
---

# 9. Drawer maturity status / 目录成熟度状态

9. Drawer maturity status / 目录成熟度状态

| Directory / 目录 | Status / 状态 | Notes / 说明 |
|----------------|--------------|-------------|
| `00_governance` | planned | 当前最简政策已散落各处，待正式整理时激活 |
| `01_policies_and_standards` | **partial** | 仅 `document-standards` 有 v2.0.0（workspace 版） |
| `02_enterprise_architecture` | **partial** | `adr/` 已激活（KBG-0001/0002/0003）；`target-architecture/` 已激活（本文档组）|
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
| `19_development_workspace` | **active** | 当前主要工作区 |
| `99_archive` | planned | 出现首个退役文档时激活 |

**Status semantics / 状态语义**:

- **`active`** — Frequently written and maintained / 正在频繁写入与维护
- **`partial`** — Directory exists, some subdirectories activated / 目录存在，部分子目录已激活
- **`planned`** — Reserved in IA, activates after business milestone / 在 IA 里已预留，等业务里程碑触发后激活
- **`deferred`** — Confirmed not needed now; revisit when trigger condition is met / 确定现阶段不需要，未来触发条件满足后再评估

---
