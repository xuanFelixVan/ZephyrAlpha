---
module_id: ARCH_SYSTEM_PANORAMA
version: '1.0.0'
status: Active
created_date: '2026-04-16'
last_updated: '2026-04-16'
owner: Project Owner
layer: cross_layer
priority: P0
---

# ZephyrAlpha 系统全景 (System Panorama)

> **用途**：L00-L11 全系统模块全景视图，架构决策时快速定位影响范围。
> 详细模块清单见：`docs/02_ARCHITECTURE/MODULE_INVENTORY.md`
> 技术选型见：`docs/02_ARCHITECTURE/TECH_DECISION_RECORDS.md`
> 子系统注册表见：`docs/subsystem-registry.yaml`

---

## 系统架构层级

```
ZephyrAlpha 量化交易系统
│
├── L00 数据源层 (Data Source Layer)
│   ├── AKShare 适配器（A 股日线 OHLCV）
│   ├── 数据验证器（Pydantic 模型校验）
│   └── 数据持久化（DuckDB/Parquet）
│
├── L01 基础设施层 (Infrastructure Layer)
│   ├── 配置管理（Pydantic Settings）
│   ├── 结构化日志（structlog）
│   └── 错误处理（ZephyrBaseError 层次）
│
├── L02 Alpha 因子层 (Alpha Factor Layer)
│   ├── 技术因子（动量、均值回归等）
│   ├── 基本面因子
│   └── 因子评估框架（IC/IR/衰减）
│
├── L03 舆情分析层 (Sentiment Analysis Layer)
│   ├── 短期舆情（日内情感信号）
│   ├── 中期舆情（周/月情感趋势）
│   └── 长期舆情（季度以上）
│
├── L04 ML 模型层 (ML Model Layer)
│   ├── 特征工程
│   ├── 模型训练（LightGBM/XGBoost）
│   └── 模型评估（OOS 测试）
│
├── L05 策略层 (Strategy Layer)
│   ├── 策略引擎（信号生成）
│   └── 回测框架
│
├── L06 执行层 (Execution Layer)
│   ├── 订单管理（OMS）
│   └── 风险控制（实时止损、仓位控制）
│
├── L07 AI 报告层 (AI Reporting Layer)
│   ├── 绩效分析（PnL 归因）
│   ├── 交易复盘（LLM 生成报告）
│   └── 智能调度系统
│
├── L08 人机交互层 (Human-AI Interface Layer)
│   └── （见 docs/08_HUMAN_AI_INTERFACE/）
│
├── L09 研究创新层 (Research Innovation Layer)
│   └── （见 docs/07_RESEARCH/）
│
├── L10 治理合规层 (Governance & Compliance Layer)
│   └── （见 docs/10_GOVERNANCE_COMPLIANCE/）
│
└── L11 战略决策层 (Strategic Decision Layer)
    └── （见 docs/11_STRATEGIC_DECISION/）
```

---

## 数据流向（核心链路）

```
市场数据（AKShare）
    ↓ L00 数据源层（采集、验证、存储）
    ↓ L02 Alpha 因子层（因子计算）
    ↓ L03 舆情分析层（情感信号）
    ↓ L04 ML 模型层（模型预测）
    ↓ L05 策略层（信号聚合、策略决策）
    ↓ L06 执行层（下单、风控）
    ↓ L07 AI 报告层（绩效分析、复盘）
    ↓ L08 人机交互层（展示给 Owner）
```

---

## 文档目录对应关系

| 系统层 | 蓝图目录 | 代码目录 |
|--------|---------|---------|
| L00 | `docs/01_FRAMEWORK/*data*` | `src/zephyr/l00_data/` |
| L01 | `docs/01_FRAMEWORK/*infra*` | `src/zephyr/l01_infra/` |
| L02 | `docs/02_FACTOR_LIBRARY/` | `src/zephyr/l02_alpha/` |
| L03 | `docs/10_AI_WORKFLOW/sentiment-*` | `src/zephyr/l03_sentiment/` |
| L04 | `docs/01_FRAMEWORK/LAYER4_ML/` | `src/zephyr/l04_ml/` |
| L05 | `docs/03_TRADING_TACTICS/` | `src/zephyr/l05_strategy/` |
| L06 | `docs/04_EXECUTION/` | `src/zephyr/l06_execution/` |
| L07 | `docs/10_AI_WORKFLOW/*blueprint*` | `src/zephyr/l07_reporting/` |
| L08 | `docs/08_HUMAN_AI_INTERFACE/` | `src/zephyr/l08_hci/` |
| L09 | `docs/07_RESEARCH/` | `src/zephyr/l09_research/` |
| L10 | `docs/10_GOVERNANCE_COMPLIANCE/` | `src/zephyr/l10_governance/` |
| L11 | `docs/11_STRATEGIC_DECISION/` | `src/zephyr/l11_strategy/` |

---

## 变更历史

| 版本 | 日期 | 变更描述 | 变更人 |
|------|------|---------|--------|
| 1.0.0 | 2026-04-16 | 初始创建 | AI |
