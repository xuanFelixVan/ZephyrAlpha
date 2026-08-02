---
doc_type: architecture_view
title: 因子域-因子分析
version: "1.0"
status: active
date: 2026-08-02
owner: auto-generator
ttl: permanent
---

# 因子域-因子分析

> 生成时间: 2026-08-02T21:06:13
> 真源: `dataflow_graph_registry.yaml` → PostgreSQL `dataflow_*` 表
> 生成器: `generate_dataflow_diagram.py`（全文自动生成，禁止手工编辑）

> **[可缩放 HTML 版 / Zoomable HTML](http://localhost:8765/docs/02_enterprise_architecture/05_dataflow_architecture/_zoomable_html/d_factor_analysis.html)** — Ctrl+滚轮缩放 ｜ 双击重置 ｜ Ctrl+Shift+D 切换拖动/选择模式

> **域职责 / Responsibility**: 因子分析与评估——IC/IR计算评估、衰减监控、相关性去重、归因、优化、分层回测、多因子合成、三级研判、换手率分析

## 域基本信息 / Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| Dataset 数 | 12 | Datasets | 12 |
| Job 数 | 12 | Jobs | 12 |
| 运营态 Dataset | 11 | Production Datasets | 11 |
| 设计态 Dataset | 1 | Design Datasets | 1 |
| 运营态 Job | 11 | Production Jobs | 11 |
| 设计态 Job | 1 | Design Jobs | 1 |

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

> 展示全部 24 个节点（Dataset 12 + Job 12），含 12 条边。颜色区分运营态（蓝）/设计态（橙虚线）。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'clusterBkg': 'transparent', 'clusterBorder': 'transparent', 'fontSize': '14px'}}}%%
flowchart TD
    DS20879["(生产态 / production) factor_<br/>analysis.correlation_analyzer /<br/>因子间相关系数矩阵<br/>（识别冗余因子）<br/>契约: - · 域: 因子"]
    DS20880["(生产态 / production) factor_<br/>analysis.correlation_dedup / 去重后的因子集合<br/>（移除高相关冗余因子）<br/>契约: - · 域: 因子"]
    DS20881["(生产态 / production) factor_analysis.decay_<br/>monitor / 因子衰减报告<br/>（IC随时间衰减趋势）<br/>契约: - · 域: 因子"]
    DS20882["(生产态 / production) factor_analysis.factor_<br/>attribution / 因子归因报告<br/>（各因子对收益的贡献分解）<br/>契约: - · 域: 因子"]
    DS20883["(生产态 / production) factor_analysis.factor_<br/>optimization / 优化后的因子权重<br/>（最大化IC/最小化相关性）<br/>契约: - · 域: 因子"]
    DS20884["(生产态 / production) factor_analysis.ic_decay<br/>/ IC衰减曲线<br/>（因子预测力随滞后的变化）<br/>契约: - · 域: 因子"]
    DS20885["(生产态 / production) factor_analysis.ic_ir_<br/>calc / IC/IR指标序列<br/>（因子信息系数/信息比率）<br/>契约: - · 域: 因子"]
    DS20886["(生产态 / production) factor_analysis.ic_ir_<br/>evaluator / IC/IR评估报告<br/>（因子有效性评级）<br/>契约: - · 域: 因子"]
    DS20887["(生产态 / production) factor_analysis.layered_<br/>backtest / 分层回测结果<br/>（按因子分层的收益统计）<br/>契约: - · 域: 因子"]
    DS20888["(生产态 / production) factor_<br/>analysis.multifactor_synthesis / 合成因子信号<br/>（多因子加权/截面排名/置信度）<br/>契约: - · 域: 因子"]
    DS20889["(生产态 / production) factor_analysis.three_<br/>level_judgment / 三级研判结果<br/>（因子有效性/稳定性/贡献度评级）<br/>契约: - · 域: 因子"]
    DS11238["(设计态 / design) factor_analysis.turnover_<br/>analyzer / 换手率分析报告<br/>（因子换手成本评估）<br/>契约: - · 域: 因子"]
    JOB969567("(生产态 / production) analyze.correlation_<br/>analyzer / 因子相关性分析<br/>（消费因子信号，产出分析结果）<br/>文件: analysis/correlation_analyzer.py")
    JOB969568("(生产态 / production) analyze.correlation_dedup<br/>/ 因子去重<br/>（消费因子信号，产出分析结果）<br/>文件: analysis/correlation_dedup.py")
    JOB969569("(生产态 / production) analyze.decay_monitor /<br/>因子衰减监控<br/>（消费因子信号，产出分析结果）<br/>文件: analysis/decay_monitor.py")
    JOB969570("(生产态 / production) analyze.factor_<br/>attribution / 因子归因<br/>（消费因子信号，产出分析结果）<br/>文件: analysis/factor_attribution.py")
    JOB969571("(生产态 / production) analyze.factor_<br/>optimization / 因子优化<br/>（消费因子信号，产出分析结果）<br/>文件: analysis/factor_optimization.py")
    JOB969572("(生产态 / production) analyze.ic_decay /<br/>IC衰减分析<br/>（消费因子信号，产出分析结果）<br/>文件: analysis/ic_decay.py")
    JOB969573("(生产态 / production) analyze.ic_ir_calc / IC<br/>/IR计算<br/>（消费因子信号，产出分析结果）<br/>文件: analysis/ic_ir_calc.py")
    JOB969574("(生产态 / production) analyze.ic_ir_evaluator /<br/>IC/IR评估<br/>（消费因子信号，产出分析结果）<br/>文件: analysis/ic_ir_evaluator.py")
    JOB969575("(生产态 / production) analyze.layered_backtest<br/>/ 分层回测<br/>（消费因子信号，产出分析结果）<br/>文件: analysis/layered_backtest.py")
    JOB969576("(生产态 / production) analyze.multifactor_<br/>synthesis / 多因子合成<br/>（消费因子信号，产出分析结果）<br/>文件: analysis/multifactor_synthesis.py")
    JOB969577("(生产态 / production) analyze.three_level_<br/>judgment / 三级研判<br/>（消费因子信号，产出分析结果）<br/>文件: analysis/three_level_judgment.py")
    JOB757602("(设计态 / design) analyze.turnover_analyzer /<br/>换手率分析<br/>（消费因子信号，产出分析结果）<br/>文件: turnover_analyzer/")
    JOB969567 -->|produces / 产出| DS20879
    JOB969568 -->|produces / 产出| DS20880
    JOB969569 -->|produces / 产出| DS20881
    JOB969570 -->|produces / 产出| DS20882
    JOB969571 -->|produces / 产出| DS20883
    JOB969572 -->|produces / 产出| DS20884
    JOB969573 -->|produces / 产出| DS20885
    JOB969574 -->|produces / 产出| DS20886
    JOB969575 -->|produces / 产出| DS20887
    JOB757602 -.->|produces / 产出| DS11238
    JOB969576 -->|produces / 产出| DS20888
    JOB969577 -->|produces / 产出| DS20889
    JOB757602 ~~~ JOB969569
    JOB969569 ~~~ JOB969577
    JOB969577 ~~~ JOB969570
    JOB969570 ~~~ JOB969575
    JOB969575 ~~~ JOB969571
    JOB969571 ~~~ JOB969574
    JOB969574 ~~~ JOB969568
    JOB969568 ~~~ JOB969573
    JOB969573 ~~~ JOB969572
    JOB969572 ~~~ JOB969567
    JOB969567 ~~~ JOB969576
    DS11238 ~~~ DS20881
    DS20881 ~~~ DS20889
    DS20889 ~~~ DS20882
    DS20882 ~~~ DS20887
    DS20887 ~~~ DS20883
    DS20883 ~~~ DS20886
    DS20886 ~~~ DS20880
    DS20880 ~~~ DS20885
    DS20885 ~~~ DS20884
    DS20884 ~~~ DS20879
    DS20879 ~~~ DS20888
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class DS20879,DS20880,DS20881,DS20882,DS20883,DS20884,DS20885,DS20886,DS20887,DS20888,DS20889,JOB969567,JOB969568,JOB969569,JOB969570,JOB969571,JOB969572,JOB969573,JOB969574,JOB969575,JOB969576,JOB969577 production
    class DS11238,JOB757602 design
```

### 运营态的图（仅 design_maturity=production）

> 仅展示已实现稳定运行的节点（运营态：11 datasets / 数据集, 11 jobs / 作业, 11 edges / 边）。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'clusterBkg': 'transparent', 'clusterBorder': 'transparent', 'fontSize': '14px'}}}%%
flowchart TD
    DS20879["(生产态 / production) factor_<br/>analysis.correlation_analyzer /<br/>因子间相关系数矩阵<br/>（识别冗余因子）<br/>契约: - · 域: 因子"]
    DS20880["(生产态 / production) factor_<br/>analysis.correlation_dedup / 去重后的因子集合<br/>（移除高相关冗余因子）<br/>契约: - · 域: 因子"]
    DS20881["(生产态 / production) factor_analysis.decay_<br/>monitor / 因子衰减报告<br/>（IC随时间衰减趋势）<br/>契约: - · 域: 因子"]
    DS20882["(生产态 / production) factor_analysis.factor_<br/>attribution / 因子归因报告<br/>（各因子对收益的贡献分解）<br/>契约: - · 域: 因子"]
    DS20883["(生产态 / production) factor_analysis.factor_<br/>optimization / 优化后的因子权重<br/>（最大化IC/最小化相关性）<br/>契约: - · 域: 因子"]
    DS20884["(生产态 / production) factor_analysis.ic_decay<br/>/ IC衰减曲线<br/>（因子预测力随滞后的变化）<br/>契约: - · 域: 因子"]
    DS20885["(生产态 / production) factor_analysis.ic_ir_<br/>calc / IC/IR指标序列<br/>（因子信息系数/信息比率）<br/>契约: - · 域: 因子"]
    DS20886["(生产态 / production) factor_analysis.ic_ir_<br/>evaluator / IC/IR评估报告<br/>（因子有效性评级）<br/>契约: - · 域: 因子"]
    DS20887["(生产态 / production) factor_analysis.layered_<br/>backtest / 分层回测结果<br/>（按因子分层的收益统计）<br/>契约: - · 域: 因子"]
    DS20888["(生产态 / production) factor_<br/>analysis.multifactor_synthesis / 合成因子信号<br/>（多因子加权/截面排名/置信度）<br/>契约: - · 域: 因子"]
    DS20889["(生产态 / production) factor_analysis.three_<br/>level_judgment / 三级研判结果<br/>（因子有效性/稳定性/贡献度评级）<br/>契约: - · 域: 因子"]
    JOB969567("(生产态 / production) analyze.correlation_<br/>analyzer / 因子相关性分析<br/>（消费因子信号，产出分析结果）<br/>文件: analysis/correlation_analyzer.py")
    JOB969568("(生产态 / production) analyze.correlation_dedup<br/>/ 因子去重<br/>（消费因子信号，产出分析结果）<br/>文件: analysis/correlation_dedup.py")
    JOB969569("(生产态 / production) analyze.decay_monitor /<br/>因子衰减监控<br/>（消费因子信号，产出分析结果）<br/>文件: analysis/decay_monitor.py")
    JOB969570("(生产态 / production) analyze.factor_<br/>attribution / 因子归因<br/>（消费因子信号，产出分析结果）<br/>文件: analysis/factor_attribution.py")
    JOB969571("(生产态 / production) analyze.factor_<br/>optimization / 因子优化<br/>（消费因子信号，产出分析结果）<br/>文件: analysis/factor_optimization.py")
    JOB969572("(生产态 / production) analyze.ic_decay /<br/>IC衰减分析<br/>（消费因子信号，产出分析结果）<br/>文件: analysis/ic_decay.py")
    JOB969573("(生产态 / production) analyze.ic_ir_calc / IC<br/>/IR计算<br/>（消费因子信号，产出分析结果）<br/>文件: analysis/ic_ir_calc.py")
    JOB969574("(生产态 / production) analyze.ic_ir_evaluator /<br/>IC/IR评估<br/>（消费因子信号，产出分析结果）<br/>文件: analysis/ic_ir_evaluator.py")
    JOB969575("(生产态 / production) analyze.layered_backtest<br/>/ 分层回测<br/>（消费因子信号，产出分析结果）<br/>文件: analysis/layered_backtest.py")
    JOB969576("(生产态 / production) analyze.multifactor_<br/>synthesis / 多因子合成<br/>（消费因子信号，产出分析结果）<br/>文件: analysis/multifactor_synthesis.py")
    JOB969577("(生产态 / production) analyze.three_level_<br/>judgment / 三级研判<br/>（消费因子信号，产出分析结果）<br/>文件: analysis/three_level_judgment.py")
    JOB969567 -->|produces / 产出| DS20879
    JOB969568 -->|produces / 产出| DS20880
    JOB969569 -->|produces / 产出| DS20881
    JOB969570 -->|produces / 产出| DS20882
    JOB969571 -->|produces / 产出| DS20883
    JOB969572 -->|produces / 产出| DS20884
    JOB969573 -->|produces / 产出| DS20885
    JOB969574 -->|produces / 产出| DS20886
    JOB969575 -->|produces / 产出| DS20887
    JOB969576 -->|produces / 产出| DS20888
    JOB969577 -->|produces / 产出| DS20889
    JOB969569 ~~~ JOB969577
    JOB969577 ~~~ JOB969570
    JOB969570 ~~~ JOB969575
    JOB969575 ~~~ JOB969571
    JOB969571 ~~~ JOB969574
    JOB969574 ~~~ JOB969568
    JOB969568 ~~~ JOB969573
    JOB969573 ~~~ JOB969572
    JOB969572 ~~~ JOB969567
    JOB969567 ~~~ JOB969576
    DS20881 ~~~ DS20889
    DS20889 ~~~ DS20882
    DS20882 ~~~ DS20887
    DS20887 ~~~ DS20883
    DS20883 ~~~ DS20886
    DS20886 ~~~ DS20880
    DS20880 ~~~ DS20885
    DS20885 ~~~ DS20884
    DS20884 ~~~ DS20879
    DS20879 ~~~ DS20888
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class DS20879,DS20880,DS20881,DS20882,DS20883,DS20884,DS20885,DS20886,DS20887,DS20888,DS20889,JOB969567,JOB969568,JOB969569,JOB969570,JOB969571,JOB969572,JOB969573,JOB969574,JOB969575,JOB969576,JOB969577 production
```

### 设计态的图（仅 design_maturity=design）

> 仅展示蓝图阶段、代码未写的设计态节点（设计态：1 datasets / 数据集, 1 jobs / 作业, 1 edges / 边）。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'clusterBkg': 'transparent', 'clusterBorder': 'transparent', 'fontSize': '14px'}}}%%
flowchart TD
    DS11238["(设计态 / design) factor_analysis.turnover_<br/>analyzer / 换手率分析报告<br/>（因子换手成本评估）<br/>契约: - · 域: 因子"]
    JOB757602("(设计态 / design) analyze.turnover_analyzer /<br/>换手率分析<br/>（消费因子信号，产出分析结果）<br/>文件: turnover_analyzer/")
    JOB757602 -.->|produces / 产出| DS11238
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class DS11238,JOB757602 design
```

## Dataset 清单

| ID | entity_name / 实体名 | scope / 范围 | domain / 域 | design_maturity / 设计成熟度 | module_id / 蓝图 | 功能简述 |
|----|----------------------|--------------|------------|------------------------------|------------------|----------|
| DS-20879 | factor_analysis.correlation_analyzer | production / 生产 | D_FACTOR / 因子 | production / 生产 | MOD-L02-005 | 因子间相关系数矩阵（识别冗余因子） |
| DS-20880 | factor_analysis.correlation_dedup | production / 生产 | D_FACTOR / 因子 | production / 生产 | MOD-L02-006 | 去重后的因子集合（移除高相关冗余因子） |
| DS-20881 | factor_analysis.decay_monitor | production / 生产 | D_FACTOR / 因子 | production / 生产 | MOD-L02-009 | 因子衰减报告（IC随时间衰减趋势） |
| DS-20882 | factor_analysis.factor_attribution | production / 生产 | D_FACTOR / 因子 | production / 生产 | MOD-L02-010 | 因子归因报告（各因子对收益的贡献分解） |
| DS-20883 | factor_analysis.factor_optimization | production / 生产 | D_FACTOR / 因子 | production / 生产 | MOD-L02-012 | 优化后的因子权重（最大化IC/最小化相关性） |
| DS-20884 | factor_analysis.ic_decay | production / 生产 | D_FACTOR / 因子 | production / 生产 | MOD-L02-004 | IC衰减曲线（因子预测力随滞后的变化） |
| DS-20885 | factor_analysis.ic_ir_calc | production / 生产 | D_FACTOR / 因子 | production / 生产 | MOD-L02-002 | IC/IR指标序列（因子信息系数/信息比率） |
| DS-20886 | factor_analysis.ic_ir_evaluator | production / 生产 | D_FACTOR / 因子 | production / 生产 | MOD-L02-003 | IC/IR评估报告（因子有效性评级） |
| DS-20887 | factor_analysis.layered_backtest | production / 生产 | D_FACTOR / 因子 | production / 生产 | MOD-L02-007 | 分层回测结果（按因子分层的收益统计） |
| DS-20888 | factor_analysis.multifactor_synthesis | production / 生产 | D_FACTOR / 因子 | production / 生产 | MOD-L02-011 | 合成因子信号（多因子加权/截面排名/置信度） |
| DS-20889 | factor_analysis.three_level_judgment | production / 生产 | D_FACTOR / 因子 | production / 生产 | MOD-L02-008 | 三级研判结果（因子有效性/稳定性/贡献度评级） |
| DS-11238 | factor_analysis.turnover_analyzer | production / 生产 | D_FACTOR / 因子 | design / 设计 | MOD-L02-001 | 换手率分析报告（因子换手成本评估） |

## Job 清单

| ID | job_name / 作业名 | trigger_type / 触发类型 | design_maturity / 设计成熟度 | module_id / 蓝图 | 功能简述 |
|----|-------------------|----------------------------|------------------------------|------------------|----------|
| JOB-969567 | analyze.correlation_analyzer | manual / 手动 | production / 生产 | MOD-L02-005 | 因子相关性分析（消费因子信号，产出分析结果） |
| JOB-969568 | analyze.correlation_dedup | manual / 手动 | production / 生产 | MOD-L02-006 | 因子去重（消费因子信号，产出分析结果） |
| JOB-969569 | analyze.decay_monitor | manual / 手动 | production / 生产 | MOD-L02-009 | 因子衰减监控（消费因子信号，产出分析结果） |
| JOB-969570 | analyze.factor_attribution | manual / 手动 | production / 生产 | MOD-L02-010 | 因子归因（消费因子信号，产出分析结果） |
| JOB-969571 | analyze.factor_optimization | manual / 手动 | production / 生产 | MOD-L02-012 | 因子优化（消费因子信号，产出分析结果） |
| JOB-969572 | analyze.ic_decay | manual / 手动 | production / 生产 | MOD-L02-004 | IC衰减分析（消费因子信号，产出分析结果） |
| JOB-969573 | analyze.ic_ir_calc | manual / 手动 | production / 生产 | MOD-L02-002 | IC/IR计算（消费因子信号，产出分析结果） |
| JOB-969574 | analyze.ic_ir_evaluator | manual / 手动 | production / 生产 | MOD-L02-003 | IC/IR评估（消费因子信号，产出分析结果） |
| JOB-969575 | analyze.layered_backtest | manual / 手动 | production / 生产 | MOD-L02-007 | 分层回测（消费因子信号，产出分析结果） |
| JOB-969576 | analyze.multifactor_synthesis | manual / 手动 | production / 生产 | MOD-L02-011 | 多因子合成（消费因子信号，产出分析结果） |
| JOB-969577 | analyze.three_level_judgment | manual / 手动 | production / 生产 | MOD-L02-008 | 三级研判（消费因子信号，产出分析结果） |
| JOB-757602 | analyze.turnover_analyzer | manual / 手动 | design / 设计 | MOD-L02-001 | 换手率分析（消费因子信号，产出分析结果） |

[← 返回索引](dataflow_index.md)
