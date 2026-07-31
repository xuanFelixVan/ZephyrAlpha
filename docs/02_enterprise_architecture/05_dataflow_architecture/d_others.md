---
doc_type: architecture_view
title: 其他域-ML训练+风控+交易
version: "1.0"
status: active
date: 2026-07-31
owner: auto-generator
ttl: permanent
---

# 其他域-ML训练+风控+交易

> 生成时间: 2026-07-31T17:03:35
> 真源: `dataflow_graph_registry.yaml` → PostgreSQL `dataflow_*` 表
> 生成器: `generate_dataflow_diagram.py`（全文自动生成，禁止手工编辑）

> **域职责 / Responsibility**: ML训练+风控+交易——AI操作员决策/训练流水线 + 回撤跟踪 + PnL计算

## 数据流图（全景：设计态+运营态合并）

> 节点数: 5 datasets / 数据集, 5 jobs / 作业, 5 edges / 边
>
> **图例**：🟦 蓝色 = 运营态（已实现）/ 🟧 橙色虚线 = 设计态（未实现）

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart LR
    DS11271["[design]ml.ai_operator_decisions<br/>AI操作员决策记录<br/>（模型推理/决策建议/置信度）"]
    DS11272["[design]ml.training_dataset<br/>训练数据集<br/>（特征/标签/样本/版本管理）"]
    DS11273["[design]risk.drawdown_metric<br/>回撤指标序列<br/>（最大回撤/当前回撤/恢复时间）"]
    DS11660["[production]risk.limits<br/>风险限额<br/>（max_position/max_drawdown/exposure_limits）"]
    DS11274["[design]trading.pnl<br/>盈亏序列<br/>（已实现/未实现盈亏/总盈亏）"]
    JOB784146("[production]check.risk_limits<br/>风险限额检查<br/>（持仓/回撤/暴露度）")
    JOB757635("[design]ml_train.ai_operator<br/>AI操作员决策<br/>（消费信号，产出AI辅助决策）")
    JOB757636("[design]ml_train.training_pipeline<br/>ML训练流水线<br/>（消费因子数据，产出训练数据集）")
    JOB757637("[design]risk.track_drawdown<br/>回撤跟踪<br/>（消费持仓快照，产出回撤指标）")
    JOB757638("[design]trading.calc_pnl<br/>PnL计算<br/>（消费成交数据，产出盈亏）")
    JOB784146 -->|produces / 产出| DS11660
    JOB757635 -->|produces / 产出| DS11271
    JOB757636 -->|produces / 产出| DS11272
    JOB757637 -->|produces / 产出| DS11273
    JOB757638 -->|produces / 产出| DS11274
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    class DS11271,DS11272,DS11273,DS11274,JOB757635,JOB757636,JOB757637,JOB757638 design
    class DS11660,JOB784146 production
```

## 数据流图（设计态）

> 节点数: 4 datasets / 数据集, 4 jobs / 作业, 4 edges / 边

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    DS11271["[design]ml.ai_operator_decisions<br/>AI操作员决策记录<br/>（模型推理/决策建议/置信度）"]
    DS11272["[design]ml.training_dataset<br/>训练数据集<br/>（特征/标签/样本/版本管理）"]
    DS11273["[design]risk.drawdown_metric<br/>回撤指标序列<br/>（最大回撤/当前回撤/恢复时间）"]
    DS11274["[design]trading.pnl<br/>盈亏序列<br/>（已实现/未实现盈亏/总盈亏）"]
    JOB757635("[design]ml_train.ai_operator<br/>AI操作员决策<br/>（消费信号，产出AI辅助决策）")
    JOB757636("[design]ml_train.training_pipeline<br/>ML训练流水线<br/>（消费因子数据，产出训练数据集）")
    JOB757637("[design]risk.track_drawdown<br/>回撤跟踪<br/>（消费持仓快照，产出回撤指标）")
    JOB757638("[design]trading.calc_pnl<br/>PnL计算<br/>（消费成交数据，产出盈亏）")
    JOB757635 -->|produces / 产出| DS11271
    JOB757636 -->|produces / 产出| DS11272
    JOB757637 -->|produces / 产出| DS11273
    JOB757638 -->|produces / 产出| DS11274
    DS11271 ~~~ JOB757636
    DS11272 ~~~ JOB757637
    DS11273 ~~~ JOB757638
```

## 数据流图（运营态）

> 节点数: 1 datasets / 数据集, 1 jobs / 作业, 1 edges / 边

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    DS11660["[production]risk.limits<br/>风险限额<br/>（max_position/max_drawdown/exposure_limits）"]
    JOB784146("[production]check.risk_limits<br/>风险限额检查<br/>（持仓/回撤/暴露度）")
    JOB784146 -->|produces / 产出| DS11660
```

## Dataset 清单

| ID | entity_name / 实体名 | scope / 范围 | domain / 域 | design_maturity / 设计成熟度 | module_id / 蓝图 | 功能简述 |
|----|----------------------|--------------|------------|------------------------------|------------------|----------|
| DS-11271 | ml.ai_operator_decisions | production / 生产 | D_ML_TRAIN | design / 设计 | MOD-ML-002 | AI操作员决策记录（模型推理/决策建议/置信度） |
| DS-11272 | ml.training_dataset | production / 生产 | D_ML_TRAIN | design / 设计 | MOD-ML-001 | 训练数据集（特征/标签/样本/版本管理） |
| DS-11273 | risk.drawdown_metric | production / 生产 | D_RISK / 风险 | design / 设计 | MOD-RISK-001 | 回撤指标序列（最大回撤/当前回撤/恢复时间） |
| DS-11660 | risk.limits / 风险.限额 | production / 生产 | D_RISK / 风险 | production / 生产 | MOD-L04-001 | 风险限额（max_position/max_drawdown/exposure_limits），CTR-003 RiskLimits |
| DS-11274 | trading.pnl | production / 生产 | D_TRADING | design / 设计 | MOD-TRADING-002 | 盈亏序列（已实现/未实现盈亏/总盈亏） |

## Job 清单

| ID | job_name / 作业名 | trigger_type / 触发类型 | design_maturity / 设计成熟度 | module_id / 蓝图 | 功能简述 |
|----|-------------------|----------------------------|------------------------------|------------------|----------|
| JOB-784146 | check.risk_limits / 检查.风险限额 | event_driven / 事件驱动 | production / 生产 | MOD-L04-001 | 风险限额检查（持仓/回撤/暴露度），产出DS-006 risk.limits |
| JOB-757635 | ml_train.ai_operator | event_driven / 事件驱动 | design / 设计 | MOD-ML-002 | AI操作员决策（消费信号，产出AI辅助决策） |
| JOB-757636 | ml_train.training_pipeline | scheduled / 定时 | design / 设计 | MOD-ML-001 | ML训练流水线（消费因子数据，产出训练数据集） |
| JOB-757637 | risk.track_drawdown | event_driven / 事件驱动 | design / 设计 | MOD-RISK-001 | 回撤跟踪（消费持仓快照，产出回撤指标） |
| JOB-757638 | trading.calc_pnl | event_driven / 事件驱动 | design / 设计 | MOD-TRADING-002 | PnL计算（消费成交数据，产出盈亏） |

[← 返回索引](dataflow_index.md)
