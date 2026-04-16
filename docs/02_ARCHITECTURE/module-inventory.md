---
module_id: ARCH_MODULE_INVENTORY
version: '1.1.0'
status: Active
created_date: '2026-04-16'
last_updated: '2026-04-16'
owner: Project Owner
layer: cross_layer
priority: P0
---

# ZephyrAlpha 模块清单 (Module Inventory)

> **真源说明**：本文件是系统架构层（L00-L11）所有模块的权威清单。
> **施工图链接**：每层的"施工图"列指向 `docs/04_CONSTRUCTION/PLANS/` 下的施工图文件。
> **蓝图入口**：过渡期蓝图在 `docs/01_FRAMEWORK/`，长期目标在 `docs/03_BLUEPRINTS/L{XX}_*/`。
> 详细技术规格见：`docs/05_IMPLEMENTATION/05_TECHNICAL_SPECIFICATIONS/module-registry.md`

---

## L00 数据源层 (Data Source Layer)

**施工图**：[CONSTRUCTION_PLAN_L00_DATA_SOURCE.md](../04_CONSTRUCTION/PLANS/CONSTRUCTION_PLAN_L00_DATA_SOURCE.md) ✅ 初稿已建

| 模块 ID | 模块 | 职责 | 技术栈 | P | 蓝图入口 | 施工状态 |
|---------|------|------|--------|---|---------|---------|
| L00-M1 | AKShare 适配器（ingestion） | A 股日线 OHLCV 数据拉取 | AKShare, Pydantic | P0 | `docs/01_FRAMEWORK/` 查 ingestion | 施工图已建，待实施 |
| L00-M2 | 数据规范化（normalization） | 原始数据→标准 OHLCVBar schema | Pydantic v2 | P0 | `docs/01_FRAMEWORK/` 查 normalization | 待开始 |
| L00-M3 | 数据持久化（persistence） | 时序+元数据落库 | PostgreSQL/TimescaleDB | P0 | `docs/01_FRAMEWORK/` 查 persistence | 待开始 |
| L00-M4 | 热缓存（cache） | Redis 热缓存、PubSub | Redis | P1 | TBD | 待开始 |
| L00-M5 | 标的目录（catalog） | 标的、日历、血缘登记 | PostgreSQL | P0 | TBD | 待开始 |
| L00-M6 | 质量门禁（quality_gate） | 缺失/异常/停牌检测 | Pydantic, Pandas | P0 | TBD | 待开始 |

## L01 基础设施层 (Infrastructure Layer)

**施工图**：[construction-plan-l01-data-processing.md](../04_CONSTRUCTION/PLANS/construction-plan-l01-data-processing.md) ⬜ 待创建

| 模块 | 职责 | 技术栈 | P | 蓝图入口 | 施工状态 |
|------|------|--------|---|---------|---------|
| 配置管理 | 系统配置中心 | Pydantic Settings, YAML | P0 | `docs/01_FRAMEWORK/` | 待开始 |
| 日志系统 | 结构化日志 | structlog（ADR-001） | P0 | `docs/01_FRAMEWORK/` | 待开始 |
| 错误处理 | 异常层次 ZephyrBaseError | Python exceptions（ADR-004） | P0 | `docs/01_FRAMEWORK/` | 待开始 |

## L02 Alpha 因子层 (Alpha Factor Layer)

**施工图**：[construction-plan-l02-feature-engineering.md](../04_CONSTRUCTION/PLANS/construction-plan-l02-feature-engineering.md) ⬜ 待创建

| 模块 | 职责 | 技术栈 | P | 蓝图入口 | 施工状态 |
|------|------|--------|---|---------|---------|
| 因子计算引擎 | 技术因子、基本面因子 | Pandas, NumPy | P0 | `docs/01_FRAMEWORK/` 查 factor | 待开始 |
| 因子评估框架 | IC、IR、衰减分析 | Alphalens | P0 | `docs/01_FRAMEWORK/` 查 factor | 待开始 |

## L03 舆情/信号层 (Signal Generation Layer)

**施工图**：[construction-plan-l03-signal-generation.md](../04_CONSTRUCTION/PLANS/construction-plan-l03-signal-generation.md) ⬜ 待创建（**下一优先**）

| 模块 | 职责 | 技术栈 | P | 蓝图入口 | 施工状态 |
|------|------|--------|---|---------|---------|
| 短期信号 | 日内信号生成 | NLP, transformers | P1 | `docs/10_AI_WORKFLOW/sentiment-analysis-short-term-technical-specification.md` | 待开始 |
| 中期信号 | 周/月信号趋势 | NLP | P1 | TBD | 待开始 |
| 长期信号 | 季度以上信号 | NLP | P2 | TBD | 待开始 |

## L04 风险管理层（Risk Management Layer）

**施工图**：[construction-plan-l04-risk-management.md](../04_CONSTRUCTION/PLANS/construction-plan-l04-risk-management.md) ⬜ 待创建
> **ADR-D1-001**：L04 独立层，L05 不得包含 VaR/CVaR 核心计算与止损引擎。

| 模块 | 职责 | 技术栈 | P | 蓝图入口 | 施工状态 |
|------|------|--------|---|---------|---------|
| 风险度量 | VaR/CVaR 计算 | NumPy, SciPy | P0 | TBD | 待开始 |
| 止损引擎 | 动态止损 | Python | P0 | TBD | 待开始 |
| 限额管理 | 持仓/行业限额 | Python | P0 | TBD | 待开始 |

## L05 组合构建层 (Portfolio Construction Layer)

**施工图**：[construction-plan-l05-portfolio-construction.md](../04_CONSTRUCTION/PLANS/construction-plan-l05-portfolio-construction.md) ⬜ 待创建

| 模块 | 职责 | 技术栈 | P | 蓝图入口 | 施工状态 |
|------|------|--------|---|---------|---------|
| 组合优化器 | 均值方差/风险平价 | cvxpy, PyPortfolioOpt | P0 | TBD | 待开始 |
| 权重分配 | 目标权重计算 | Python | P0 | TBD | 待开始 |
| 回测框架 | 历史回测（ADR-007 待决策） | TBD | P0 | TBD | 待开始 |

## L06 交易执行层 (Trade Execution Layer)

**施工图**：[construction-plan-l06-trade-execution.md](../04_CONSTRUCTION/PLANS/construction-plan-l06-trade-execution.md) ⬜ 待创建
> **ADR-D1-002**：真源蓝图在 `docs/03_BLUEPRINTS/L08_EXECUTION/`，覆盖 QMT/OMS/SOR。

| 模块 | 职责 | 技术栈 | P | 蓝图入口 | 施工状态 |
|------|------|--------|---|---------|---------|
| 订单管理（OMS） | 订单生命周期 | QMT API, Python | P0 | `docs/03_BLUEPRINTS/L08_EXECUTION/INDEX.md` | 待开始 |
| 智能路由（SOR） | 最优执行路径 | Python | P0 | TBD | 待开始 |
| 实时风控 | 委托前风险校验 | Python | P0 | TBD | 待开始 |

## L07 交易后分析层 (Post-Trade Analytics Layer)

**施工图**：[construction-plan-l07-post-trade-analytics.md](../04_CONSTRUCTION/PLANS/construction-plan-l07-post-trade-analytics.md) ⬜ 待创建

| 模块 | 职责 | 技术栈 | P | 蓝图入口 | 施工状态 |
|------|------|--------|---|---------|---------|
| 绩效分析 | PnL 归因分析 | Pandas, Plotly | P0 | `docs/10_AI_WORKFLOW/performance-analysis-blueprint.md` | 待开始 |
| 交易复盘 | 复盘报告生成（ADR-008 待决策） | LLM API | P1 | `docs/10_AI_WORKFLOW/post-trade-review-blueprint.md` | 待开始 |

## L08 人机交互层 (Human-AI Interface Layer)

> 详见 `docs/08_HUMAN_AI_INTERFACE/` 各子模块蓝图

## L09 研究创新层 (Research Innovation Layer)

> 详见 `docs/07_RESEARCH/`

## L10 治理合规层 (Governance & Compliance Layer)

> 详见 `docs/10_GOVERNANCE_COMPLIANCE/`

## L11 战略决策层 (Strategic Decision Layer)

> 详见 `docs/11_STRATEGIC_DECISION/`

---

## Cross-Layer 共享组件

| 模块 | 职责 | 技术栈 | P | 蓝图入口 |
|------|------|--------|---|---------|
| ZephyrBaseError | 统一异常层次 | Python exceptions | P0 | TBD |
| 配置加载器 | 多环境配置管理 | Pydantic Settings | P0 | TBD |
| 结构化日志 | structlog 封装 | structlog | P0 | TBD |

---

## Cross-Layer 施工图

**施工图**：[construction-plan-shared.md](../04_CONSTRUCTION/PLANS/construction-plan-shared.md) ⬜ 待创建

| 模块 | 职责 | 技术栈 | P | 蓝图入口 |
|------|------|--------|---|---------|
| ZephyrBaseError | 统一异常层次（ADR-004） | Python exceptions | P0 | `docs/01_FRAMEWORK/` |
| 配置加载器 | 多环境配置管理 | Pydantic Settings | P0 | `docs/01_FRAMEWORK/` |
| 结构化日志 | structlog 封装（ADR-001） | structlog | P0 | `docs/01_FRAMEWORK/` |
| 公共契约类型 | OHLCVBar / InstrumentMeta / QualityReport | Pydantic v2（ADR-003） | P0 | `docs/04_CONSTRUCTION/PLANS/CONSTRUCTION_PLAN_L00_DATA_SOURCE.md` |

---

## 快速导航

| 资源 | 路径 |
|------|------|
| 施工图全览 | [docs/04_CONSTRUCTION/PLANS/INDEX.md](../04_CONSTRUCTION/PLANS/INDEX.md) |
| 施工主计划 | [docs/04_CONSTRUCTION/PLANS/MASTER_DEVELOPMENT_PLAN.md](../04_CONSTRUCTION/PLANS/MASTER_DEVELOPMENT_PLAN.md) |
| 蓝图注册表 | [docs/02_ARCHITECTURE/BLUEPRINT_DOMAIN_INVENTORY.yaml](BLUEPRINT_DOMAIN_INVENTORY.yaml) |
| 技术决策记录 | [docs/02_ARCHITECTURE/TECH_DECISION_RECORDS.md](TECH_DECISION_RECORDS.md) |
| 蓝图目标目录 | [docs/03_BLUEPRINTS/INDEX.md](../03_BLUEPRINTS/INDEX.md) |

---

## 变更历史

| 版本 | 日期 | 变更描述 |
|------|------|---------|
| 1.0.0 | 2026-04-16 | 初始创建（骨架） |
| 1.1.0 | 2026-04-16 | 添加施工图链接列；补充 L00 模块 ID（L00-M1~M6）；各层标注待创建状态；添加快速导航 |
