---
module_id: ARCH_MODULE_INVENTORY
version: '1.0.0'
status: Active
created_date: '2026-04-16'
last_updated: '2026-04-16'
owner: Project Owner
layer: cross_layer
priority: P0
---

# ZephyrAlpha 模块清单 (Module Inventory)

> **真源说明**：本文件是系统架构层（L00-L11）所有模块的权威清单。
> 施工图新增模块、蓝图变更均须同步更新本文件。
> 详细技术规格见：`docs/05_IMPLEMENTATION/05_TECHNICAL_SPECIFICATIONS/module-registry.md`

---

## L00 数据源层 (Data Source Layer)

| 模块 | 职责 | 技术栈 | P | 蓝图入口 | 施工状态 |
|------|------|--------|---|---------|---------|
| AKShare 适配器 | A 股日线 OHLCV 数据 | AKShare, Pydantic | P0 | TBD | 施工图撰写中 |
| 数据验证器 | 数据质量检查 | Pydantic, Great Expectations | P0 | TBD | 待开始 |
| 数据持久化 | 本地存储管理 | DuckDB / Parquet | P0 | TBD | 待开始 |

## L01 基础设施层 (Infrastructure Layer)

| 模块 | 职责 | 技术栈 | P | 蓝图入口 | 施工状态 |
|------|------|--------|---|---------|---------|
| 配置管理 | 系统配置中心 | Pydantic Settings, YAML | P0 | TBD | 待开始 |
| 日志系统 | 结构化日志 | structlog | P0 | TBD | 待开始 |
| 错误处理 | 异常层次 ZephyrBaseError | Python exceptions | P0 | TBD | 待开始 |

## L02 Alpha 因子层 (Alpha Factor Layer)

| 模块 | 职责 | 技术栈 | P | 蓝图入口 | 施工状态 |
|------|------|--------|---|---------|---------|
| 因子计算引擎 | 技术因子、基本面因子 | Pandas, NumPy | P0 | TBD | 待开始 |
| 因子评估框架 | IC、IR、衰减分析 | Alphalens | P0 | TBD | 待开始 |

## L03 舆情分析层 (Sentiment Analysis Layer)

| 模块 | 职责 | 技术栈 | P | 蓝图入口 | 施工状态 |
|------|------|--------|---|---------|---------|
| 短期舆情分析 | 日内情感信号 | NLP, transformers | P1 | `docs/10_AI_WORKFLOW/sentiment-analysis-short-term-technical-specification.md` | 待开始 |
| 中期舆情分析 | 周/月情感趋势 | NLP | P1 | TBD | 待开始 |
| 长期舆情分析 | 季度以上情感 | NLP | P2 | TBD | 待开始 |

## L04 ML 模型层 (ML Model Layer)

| 模块 | 职责 | 技术栈 | P | 蓝图入口 | 施工状态 |
|------|------|--------|---|---------|---------|
| 特征工程 | 特征提取与转换 | scikit-learn, Feature-engine | P0 | TBD | 待开始 |
| 模型训练 | 监督/无监督学习 | LightGBM, XGBoost | P0 | TBD | 待开始 |
| 模型评估 | 交叉验证、OOS 测试 | scikit-learn | P0 | TBD | 待开始 |
| 强化学习 | 策略优化 | RLlib | P2 | TBD | 待开始 |

## L05 策略层 (Strategy Layer)

| 模块 | 职责 | 技术栈 | P | 蓝图入口 | 施工状态 |
|------|------|--------|---|---------|---------|
| 策略引擎 | 信号生成与策略逻辑 | Python | P0 | TBD | 待开始 |
| 回测框架 | 历史回测 | Backtrader / Zipline | P0 | TBD | 待开始 |

## L06 执行层 (Execution Layer)

| 模块 | 职责 | 技术栈 | P | 蓝图入口 | 施工状态 |
|------|------|--------|---|---------|---------|
| 订单管理 | OMS | Python | P0 | TBD | 待开始 |
| 风险控制 | 实时风控 | Python | P0 | TBD | 待开始 |

## L07 AI 报告层 (AI Reporting Layer)

| 模块 | 职责 | 技术栈 | P | 蓝图入口 | 施工状态 |
|------|------|--------|---|---------|---------|
| 绩效分析 | PnL 归因分析 | Pandas, Plotly | P0 | `docs/10_AI_WORKFLOW/performance-analysis-blueprint.md` | 待开始 |
| 交易复盘 | 复盘报告生成 | LLM API | P1 | `docs/10_AI_WORKFLOW/post-trade-review-blueprint.md` | 待开始 |

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

## 变更历史

| 版本 | 日期 | 变更描述 | 变更人 |
|------|------|---------|--------|
| 1.0.0 | 2026-04-16 | 初始创建（骨架，待填充实际蓝图路径） | AI |
