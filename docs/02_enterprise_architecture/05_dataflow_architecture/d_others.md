---
doc_type: architecture_view
title: 其他域-ML训练+风控+交易
version: "1.0"
status: active
date: 2026-08-03
owner: auto-generator
ttl: permanent
---

# 其他域-ML训练+风控+交易

> 生成时间: 2026-08-03T12:37:17
> 真源: `dataflow_graph_registry.yaml` → PostgreSQL `dataflow_*` 表
> 生成器: `generate_dataflow_diagram.py`（全文自动生成，禁止手工编辑）

> **[可缩放 HTML 版 / Zoomable HTML](http://localhost:8765/docs/02_enterprise_architecture/05_dataflow_architecture/_zoomable_html/d_others.html)** — Ctrl+滚轮缩放 ｜ 双击重置 ｜ Ctrl+Shift+D 切换拖动/选择模式

> **域职责 / Responsibility**: ML训练+风控+交易——AI操作员决策/训练流水线 + 回撤跟踪 + PnL计算

## 域基本信息 / Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| Dataset 数 | 5 | Datasets | 5 |
| Job 数 | 5 | Jobs | 5 |
| 运营态 Dataset | 1 | Production Datasets | 1 |
| 设计态 Dataset | 4 | Design Datasets | 4 |
| 运营态 Job | 1 | Production Jobs | 1 |
| 设计态 Job | 4 | Design Jobs | 4 |
| 跨域外部 Dataset | 1 | Cross-domain Datasets | 1 |

## 数据流图

> **图例说明 / Legend**：
>
> - 🟦 **蓝色 = 运营态节点**（production，已上线运行）
> - 🟧 **橙色虚线 = 设计态节点**（design，蓝图阶段，代码未写）
> - 🟦更浅蓝 = 跨域外部 Dataset（external_prod/external_design）
> - **实线箭头 ``-->`` = 运营态数据流**（两端均 production）
> - **虚线箭头 ``-.->`` = 非运营态数据流**（含 design、混合）
> - 矩形 = Dataset（数据集）/ 圆角矩形 = Job（作业）
> - ``JOB -->|produces / 产出| DS`` = Job 产出 Dataset
> - ``DS -->|consumed by / 被消费于| JOB`` = Job 消费 Dataset

### 全景图（全部模块，颜色区分运营态/设计态）

> 展示全部 10 个节点（Dataset 5 + Job 5），含 5 条边，含 1 个跨域外部 Dataset。颜色区分运营态（蓝）/设计态（橙虚线）。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'clusterBkg': 'transparent', 'clusterBorder': 'transparent', 'fontSize': '14px'}}}%%
flowchart TD
    DS11271["(设计态 / design) ml.ai_operator_decisions /<br/>AI操作员决策记录<br/>（模型推理/决策建议/置信度）<br/>契约: - · 域: 训练"]
    DS11272["(设计态 / design) ml.training_dataset /<br/>训练数据集<br/>（特征/标签/样本/版本管理）<br/>契约: - · 域: 训练"]
    DS11273["(设计态 / design) risk.drawdown_metric /<br/>回撤指标序列<br/>（最大回撤/当前回撤/恢复时间）<br/>契约: - · 域: 风控"]
    DS22756["(生产态 / production) risk.limits / 风险.限额<br/>风险限额（max_position/max_drawdown/exposure_<br/>limits），CTR-003 RiskLimits<br/>契约: CTR-003 · 域: 风控"]
    DS11274["(设计态 / design) trading.pnl / 盈亏序列<br/>（已实现/未实现盈亏/总盈亏）<br/>契约: - · 域: 交易运营"]
    JOB1023259("(生产态 / production) check.risk_limits /<br/>检查.风险限额<br/>风险限额检查（持仓/回撤/暴露度），产出DS-006<br/>risk.limits<br/>文件: risk/risk_checker.py")
    JOB757635("(设计态 / design) ml_train.ai_operator /<br/>AI操作员决策<br/>（消费信号，产出AI辅助决策）<br/>文件: ai_operator/")
    JOB757636("(设计态 / design) ml_train.training_pipeline /<br/>ML训练流水线<br/>（消费因子数据，产出训练数据集）<br/>文件: training_pipeline/")
    JOB757637("(设计态 / design) risk.track_drawdown / 回撤跟踪<br/>（消费持仓快照，产出回撤指标）<br/>文件: drawdown_tracker/")
    JOB757638("(设计态 / design) trading.calc_pnl / PnL计算<br/>（消费成交数据，产出盈亏）<br/>文件: pnl_calculator/")
    DS22755["(生产态 / production) signal.composite /<br/>信号.合成信号<br/>合成交易信号（多因子加权/截面排名<br/>/置信度），CTR-P1-015 SynthesizedSignal<br/>契约: CTR-P1-015 · 域: 信号遗留设计态<br/>跨域节点 / cross-domain"]
    JOB757635 -.->|produces / 产出| DS11271
    JOB757636 -.->|produces / 产出| DS11272
    JOB757637 -.->|produces / 产出| DS11273
    JOB757638 -.->|produces / 产出| DS11274
    JOB1023259 -->|produces / 产出| DS22756
    DS22755 -.->|consumed by / 被消费于| JOB1023259
    JOB757636 ~~~ JOB757638
    JOB757638 ~~~ JOB1023259
    JOB1023259 ~~~ JOB757635
    JOB757635 ~~~ JOB757637
    DS11272 ~~~ DS11274
    DS11274 ~~~ DS22756
    DS22756 ~~~ DS11271
    DS11271 ~~~ DS11273
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class DS22756,JOB1023259 production
    class DS11271,DS11272,DS11273,DS11274,JOB757635,JOB757636,JOB757637,JOB757638 design
    class DS22755 external_prod
```

### 运营态的图（仅 design_maturity=production）

> 仅展示已实现稳定运行的节点（运营态：1 datasets / 数据集, 1 jobs / 作业, 1 edges / 边）。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'clusterBkg': 'transparent', 'clusterBorder': 'transparent', 'fontSize': '14px'}}}%%
flowchart TD
    DS22756["(生产态 / production) risk.limits / 风险.限额<br/>风险限额（max_position/max_drawdown/exposure_<br/>limits），CTR-003 RiskLimits<br/>契约: CTR-003 · 域: 风控"]
    JOB1023259("(生产态 / production) check.risk_limits /<br/>检查.风险限额<br/>风险限额检查（持仓/回撤/暴露度），产出DS-006<br/>risk.limits<br/>文件: risk/risk_checker.py")
    JOB1023259 -->|produces / 产出| DS22756
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class DS22756,JOB1023259 production
```

### 设计态的图（仅 design_maturity=design）

> 仅展示蓝图阶段、代码未写的设计态节点（设计态：4 datasets / 数据集, 4 jobs / 作业, 4 edges / 边）。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'clusterBkg': 'transparent', 'clusterBorder': 'transparent', 'fontSize': '14px'}}}%%
flowchart TD
    DS11271["(设计态 / design) ml.ai_operator_decisions /<br/>AI操作员决策记录<br/>（模型推理/决策建议/置信度）<br/>契约: - · 域: 训练"]
    DS11272["(设计态 / design) ml.training_dataset /<br/>训练数据集<br/>（特征/标签/样本/版本管理）<br/>契约: - · 域: 训练"]
    DS11273["(设计态 / design) risk.drawdown_metric /<br/>回撤指标序列<br/>（最大回撤/当前回撤/恢复时间）<br/>契约: - · 域: 风控"]
    DS11274["(设计态 / design) trading.pnl / 盈亏序列<br/>（已实现/未实现盈亏/总盈亏）<br/>契约: - · 域: 交易运营"]
    JOB757635("(设计态 / design) ml_train.ai_operator /<br/>AI操作员决策<br/>（消费信号，产出AI辅助决策）<br/>文件: ai_operator/")
    JOB757636("(设计态 / design) ml_train.training_pipeline /<br/>ML训练流水线<br/>（消费因子数据，产出训练数据集）<br/>文件: training_pipeline/")
    JOB757637("(设计态 / design) risk.track_drawdown / 回撤跟踪<br/>（消费持仓快照，产出回撤指标）<br/>文件: drawdown_tracker/")
    JOB757638("(设计态 / design) trading.calc_pnl / PnL计算<br/>（消费成交数据，产出盈亏）<br/>文件: pnl_calculator/")
    JOB757635 -.->|produces / 产出| DS11271
    JOB757636 -.->|produces / 产出| DS11272
    JOB757637 -.->|produces / 产出| DS11273
    JOB757638 -.->|produces / 产出| DS11274
    JOB757636 ~~~ JOB757638
    JOB757638 ~~~ JOB757635
    JOB757635 ~~~ JOB757637
    DS11272 ~~~ DS11274
    DS11274 ~~~ DS11271
    DS11271 ~~~ DS11273
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class DS11271,DS11272,DS11273,DS11274,JOB757635,JOB757636,JOB757637,JOB757638 design
```

## Dataset 清单

| ID | entity_name / 实体名 | scope / 范围 | domain / 域 | design_maturity / 设计成熟度 | module_id / 蓝图 | 功能简述 |
|----|----------------------|--------------|------------|------------------------------|------------------|----------|
| DS-11271 | ml.ai_operator_decisions | production / 生产 | D_ML_TRAIN / 训练 | design / 设计 | MOD-ML-002 | AI操作员决策记录（模型推理/决策建议/置信度） |
| DS-11272 | ml.training_dataset | production / 生产 | D_ML_TRAIN / 训练 | design / 设计 | MOD-ML-001 | 训练数据集（特征/标签/样本/版本管理） |
| DS-11273 | risk.drawdown_metric | production / 生产 | D_RISK / 风控 | design / 设计 | MOD-RISK-001 | 回撤指标序列（最大回撤/当前回撤/恢复时间） |
| DS-22756 | risk.limits / 风险.限额 | production / 生产 | D_RISK / 风控 | production / 生产 | MOD-L04-001 | 风险限额（max_position/max_drawdown/exposure_limits），CTR-003 RiskLimits |
| DS-11274 | trading.pnl | production / 生产 | D_TRADING / 交易运营 | design / 设计 | MOD-TRADING-002 | 盈亏序列（已实现/未实现盈亏/总盈亏） |

## Job 清单

| ID | job_name / 作业名 | trigger_type / 触发类型 | design_maturity / 设计成熟度 | module_id / 蓝图 | 功能简述 |
|----|-------------------|----------------------------|------------------------------|------------------|----------|
| JOB-1023259 | check.risk_limits / 检查.风险限额 | event_driven / 事件驱动 | production / 生产 | MOD-L04-001 | 风险限额检查（持仓/回撤/暴露度），产出DS-006 risk.limits |
| JOB-757635 | ml_train.ai_operator | event_driven / 事件驱动 | design / 设计 | MOD-ML-002 | AI操作员决策（消费信号，产出AI辅助决策） |
| JOB-757636 | ml_train.training_pipeline | scheduled / 定时 | design / 设计 | MOD-ML-001 | ML训练流水线（消费因子数据，产出训练数据集） |
| JOB-757637 | risk.track_drawdown | event_driven / 事件驱动 | design / 设计 | MOD-RISK-001 | 回撤跟踪（消费持仓快照，产出回撤指标） |
| JOB-757638 | trading.calc_pnl | event_driven / 事件驱动 | design / 设计 | MOD-TRADING-002 | PnL计算（消费成交数据，产出盈亏） |

## 跨域依赖 / Cross-domain Dependencies

### 依赖本域的外部 Dataset（入边）/ Consumed From

| 外部 Dataset | 域 | 成熟度 | 被本域 Job 消费 |
|-------------|------|--------|----------------|
| signal.composite | D_SIGLEGACY / 信号遗留设计态 | production / 生产 | check.risk_limits |

[← 返回索引](dataflow_index.md)
