---
doc_type: architecture_view
title: 因子域-因子分析
version: "1.0"
status: active
date: 2026-08-01
owner: auto-generator
ttl: permanent
---

# 因子域-因子分析

> 生成时间: 2026-08-01T22:11:49
> 真源: `dataflow_graph_registry.yaml` → PostgreSQL `dataflow_*` 表
> 生成器: `generate_dataflow_diagram.py`（全文自动生成，禁止手工编辑）

> **[可缩放 HTML 版 / Zoomable HTML](http://localhost:8765/docs/02_enterprise_architecture/05_dataflow_architecture/_zoomable_html/d_factor_analysis.html)** — Ctrl+滚轮缩放 ｜ 双击重置 ｜ Ctrl+Shift+D 切换拖动/选择模式

> **域职责 / Responsibility**: 因子分析与评估——IC/IR计算评估、衰减监控、相关性去重、归因、优化、分层回测、多因子合成、三级研判、换手率分析

## 域基本信息 / Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| Dataset 数 | 12 | Datasets | 12 |
| Job 数 | 12 | Jobs | 12 |
| 运营态 Dataset | 0 | Production Datasets | 0 |
| 设计态 Dataset | 12 | Design Datasets | 12 |
| 运营态 Job | 0 | Production Jobs | 0 |
| 设计态 Job | 12 | Design Jobs | 12 |

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
    DS11227["(设计态 / design) factor_analysis.correlation_<br/>analyzer / 因子间相关系数矩阵<br/>（识别冗余因子）<br/>契约: - · 域: 因子"]
    DS11228["(设计态 / design) factor_analysis.correlation_<br/>dedup / 去重后的因子集合<br/>（移除高相关冗余因子）<br/>契约: - · 域: 因子"]
    DS11229["(设计态 / design) factor_analysis.decay_monitor<br/>/ 因子衰减报告<br/>（IC随时间衰减趋势）<br/>契约: - · 域: 因子"]
    DS11230["(设计态 / design) factor_analysis.factor_<br/>attribution / 因子归因报告<br/>（各因子对收益的贡献分解）<br/>契约: - · 域: 因子"]
    DS11231["(设计态 / design) factor_analysis.factor_<br/>optimization / 优化后的因子权重<br/>（最大化IC/最小化相关性）<br/>契约: - · 域: 因子"]
    DS11232["(设计态 / design) factor_analysis.ic_decay /<br/>IC衰减曲线<br/>（因子预测力随滞后的变化）<br/>契约: - · 域: 因子"]
    DS11233["(设计态 / design) factor_analysis.ic_ir_calc /<br/>IC/IR指标序列<br/>（因子信息系数/信息比率）<br/>契约: - · 域: 因子"]
    DS11234["(设计态 / design) factor_analysis.ic_ir_<br/>evaluator / IC/IR评估报告<br/>（因子有效性评级）<br/>契约: - · 域: 因子"]
    DS11235["(设计态 / design) factor_analysis.layered_<br/>backtest / 分层回测结果<br/>（按因子分层的收益统计）<br/>契约: - · 域: 因子"]
    DS11236["(设计态 / design) factor_analysis.multifactor_<br/>synthesis / 合成因子信号<br/>（多因子加权/截面排名/置信度）<br/>契约: - · 域: 因子"]
    DS11237["(设计态 / design) factor_analysis.three_level_<br/>judgment / 三级研判结果<br/>（因子有效性/稳定性/贡献度评级）<br/>契约: - · 域: 因子"]
    DS11238["(设计态 / design) factor_analysis.turnover_<br/>analyzer / 换手率分析报告<br/>（因子换手成本评估）<br/>契约: - · 域: 因子"]
    JOB757591("(设计态 / design) analyze.correlation_analyzer<br/>/ 因子相关性分析<br/>（消费因子信号，产出分析结果）<br/>文件: correlation_analyzer/")
    JOB757592("(设计态 / design) analyze.correlation_dedup /<br/>因子去重<br/>（消费因子信号，产出分析结果）<br/>文件: correlation_dedup/")
    JOB757593("(设计态 / design) analyze.decay_monitor /<br/>因子衰减监控<br/>（消费因子信号，产出分析结果）<br/>文件: decay_monitor/")
    JOB757594("(设计态 / design) analyze.factor_attribution /<br/>因子归因<br/>（消费因子信号，产出分析结果）<br/>文件: factor_attribution/")
    JOB757595("(设计态 / design) analyze.factor_optimization /<br/>因子优化<br/>（消费因子信号，产出分析结果）<br/>文件: factor_optimization/")
    JOB757596("(设计态 / design) analyze.ic_decay / IC衰减分析<br/>（消费因子信号，产出分析结果）<br/>文件: ic_decay/")
    JOB757597("(设计态 / design) analyze.ic_ir_calc / IC/IR计算<br/>（消费因子信号，产出分析结果）<br/>文件: ic_ir_calc/")
    JOB757598("(设计态 / design) analyze.ic_ir_evaluator / IC<br/>/IR评估<br/>（消费因子信号，产出分析结果）<br/>文件: ic_ir_evaluator/")
    JOB757599("(设计态 / design) analyze.layered_backtest /<br/>分层回测<br/>（消费因子信号，产出分析结果）<br/>文件: layered_backtest/")
    JOB757600("(设计态 / design) analyze.multifactor_synthesis<br/>/ 多因子合成<br/>（消费因子信号，产出分析结果）<br/>文件: multifactor_synthesis/")
    JOB757601("(设计态 / design) analyze.three_level_judgment<br/>/ 三级研判<br/>（消费因子信号，产出分析结果）<br/>文件: three_level_judgment/")
    JOB757602("(设计态 / design) analyze.turnover_analyzer /<br/>换手率分析<br/>（消费因子信号，产出分析结果）<br/>文件: turnover_analyzer/")
    JOB757591 -.->|produces / 产出| DS11227
    JOB757592 -.->|produces / 产出| DS11228
    JOB757593 -.->|produces / 产出| DS11229
    JOB757594 -.->|produces / 产出| DS11230
    JOB757595 -.->|produces / 产出| DS11231
    JOB757596 -.->|produces / 产出| DS11232
    JOB757597 -.->|produces / 产出| DS11233
    JOB757598 -.->|produces / 产出| DS11234
    JOB757599 -.->|produces / 产出| DS11235
    JOB757600 -.->|produces / 产出| DS11236
    JOB757601 -.->|produces / 产出| DS11237
    JOB757602 -.->|produces / 产出| DS11238
    JOB757596 ~~~ JOB757597
    JOB757597 ~~~ JOB757602
    JOB757602 ~~~ JOB757595
    JOB757595 ~~~ JOB757594
    JOB757594 ~~~ JOB757591
    JOB757591 ~~~ JOB757598
    JOB757598 ~~~ JOB757600
    JOB757600 ~~~ JOB757592
    JOB757592 ~~~ JOB757593
    JOB757593 ~~~ JOB757599
    JOB757599 ~~~ JOB757601
    DS11232 ~~~ DS11233
    DS11233 ~~~ DS11238
    DS11238 ~~~ DS11231
    DS11231 ~~~ DS11230
    DS11230 ~~~ DS11227
    DS11227 ~~~ DS11234
    DS11234 ~~~ DS11236
    DS11236 ~~~ DS11228
    DS11228 ~~~ DS11229
    DS11229 ~~~ DS11235
    DS11235 ~~~ DS11237
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class DS11227,DS11228,DS11229,DS11230,DS11231,DS11232,DS11233,DS11234,DS11235,DS11236,DS11237,DS11238,JOB757591,JOB757592,JOB757593,JOB757594,JOB757595,JOB757596,JOB757597,JOB757598,JOB757599,JOB757600,JOB757601,JOB757602 design
```

### 运营态的图（仅 design_maturity=production）

> （无模块 / No modules）

### 设计态的图（仅 design_maturity=design）

> 仅展示蓝图阶段、代码未写的设计态节点（设计态：12 datasets / 数据集, 12 jobs / 作业, 12 edges / 边）。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'clusterBkg': 'transparent', 'clusterBorder': 'transparent', 'fontSize': '14px'}}}%%
flowchart TD
    DS11227["(设计态 / design) factor_analysis.correlation_<br/>analyzer / 因子间相关系数矩阵<br/>（识别冗余因子）<br/>契约: - · 域: 因子"]
    DS11228["(设计态 / design) factor_analysis.correlation_<br/>dedup / 去重后的因子集合<br/>（移除高相关冗余因子）<br/>契约: - · 域: 因子"]
    DS11229["(设计态 / design) factor_analysis.decay_monitor<br/>/ 因子衰减报告<br/>（IC随时间衰减趋势）<br/>契约: - · 域: 因子"]
    DS11230["(设计态 / design) factor_analysis.factor_<br/>attribution / 因子归因报告<br/>（各因子对收益的贡献分解）<br/>契约: - · 域: 因子"]
    DS11231["(设计态 / design) factor_analysis.factor_<br/>optimization / 优化后的因子权重<br/>（最大化IC/最小化相关性）<br/>契约: - · 域: 因子"]
    DS11232["(设计态 / design) factor_analysis.ic_decay /<br/>IC衰减曲线<br/>（因子预测力随滞后的变化）<br/>契约: - · 域: 因子"]
    DS11233["(设计态 / design) factor_analysis.ic_ir_calc /<br/>IC/IR指标序列<br/>（因子信息系数/信息比率）<br/>契约: - · 域: 因子"]
    DS11234["(设计态 / design) factor_analysis.ic_ir_<br/>evaluator / IC/IR评估报告<br/>（因子有效性评级）<br/>契约: - · 域: 因子"]
    DS11235["(设计态 / design) factor_analysis.layered_<br/>backtest / 分层回测结果<br/>（按因子分层的收益统计）<br/>契约: - · 域: 因子"]
    DS11236["(设计态 / design) factor_analysis.multifactor_<br/>synthesis / 合成因子信号<br/>（多因子加权/截面排名/置信度）<br/>契约: - · 域: 因子"]
    DS11237["(设计态 / design) factor_analysis.three_level_<br/>judgment / 三级研判结果<br/>（因子有效性/稳定性/贡献度评级）<br/>契约: - · 域: 因子"]
    DS11238["(设计态 / design) factor_analysis.turnover_<br/>analyzer / 换手率分析报告<br/>（因子换手成本评估）<br/>契约: - · 域: 因子"]
    JOB757591("(设计态 / design) analyze.correlation_analyzer<br/>/ 因子相关性分析<br/>（消费因子信号，产出分析结果）<br/>文件: correlation_analyzer/")
    JOB757592("(设计态 / design) analyze.correlation_dedup /<br/>因子去重<br/>（消费因子信号，产出分析结果）<br/>文件: correlation_dedup/")
    JOB757593("(设计态 / design) analyze.decay_monitor /<br/>因子衰减监控<br/>（消费因子信号，产出分析结果）<br/>文件: decay_monitor/")
    JOB757594("(设计态 / design) analyze.factor_attribution /<br/>因子归因<br/>（消费因子信号，产出分析结果）<br/>文件: factor_attribution/")
    JOB757595("(设计态 / design) analyze.factor_optimization /<br/>因子优化<br/>（消费因子信号，产出分析结果）<br/>文件: factor_optimization/")
    JOB757596("(设计态 / design) analyze.ic_decay / IC衰减分析<br/>（消费因子信号，产出分析结果）<br/>文件: ic_decay/")
    JOB757597("(设计态 / design) analyze.ic_ir_calc / IC/IR计算<br/>（消费因子信号，产出分析结果）<br/>文件: ic_ir_calc/")
    JOB757598("(设计态 / design) analyze.ic_ir_evaluator / IC<br/>/IR评估<br/>（消费因子信号，产出分析结果）<br/>文件: ic_ir_evaluator/")
    JOB757599("(设计态 / design) analyze.layered_backtest /<br/>分层回测<br/>（消费因子信号，产出分析结果）<br/>文件: layered_backtest/")
    JOB757600("(设计态 / design) analyze.multifactor_synthesis<br/>/ 多因子合成<br/>（消费因子信号，产出分析结果）<br/>文件: multifactor_synthesis/")
    JOB757601("(设计态 / design) analyze.three_level_judgment<br/>/ 三级研判<br/>（消费因子信号，产出分析结果）<br/>文件: three_level_judgment/")
    JOB757602("(设计态 / design) analyze.turnover_analyzer /<br/>换手率分析<br/>（消费因子信号，产出分析结果）<br/>文件: turnover_analyzer/")
    JOB757591 -.->|produces / 产出| DS11227
    JOB757592 -.->|produces / 产出| DS11228
    JOB757593 -.->|produces / 产出| DS11229
    JOB757594 -.->|produces / 产出| DS11230
    JOB757595 -.->|produces / 产出| DS11231
    JOB757596 -.->|produces / 产出| DS11232
    JOB757597 -.->|produces / 产出| DS11233
    JOB757598 -.->|produces / 产出| DS11234
    JOB757599 -.->|produces / 产出| DS11235
    JOB757600 -.->|produces / 产出| DS11236
    JOB757601 -.->|produces / 产出| DS11237
    JOB757602 -.->|produces / 产出| DS11238
    JOB757596 ~~~ JOB757597
    JOB757597 ~~~ JOB757602
    JOB757602 ~~~ JOB757595
    JOB757595 ~~~ JOB757594
    JOB757594 ~~~ JOB757591
    JOB757591 ~~~ JOB757598
    JOB757598 ~~~ JOB757600
    JOB757600 ~~~ JOB757592
    JOB757592 ~~~ JOB757593
    JOB757593 ~~~ JOB757599
    JOB757599 ~~~ JOB757601
    DS11232 ~~~ DS11233
    DS11233 ~~~ DS11238
    DS11238 ~~~ DS11231
    DS11231 ~~~ DS11230
    DS11230 ~~~ DS11227
    DS11227 ~~~ DS11234
    DS11234 ~~~ DS11236
    DS11236 ~~~ DS11228
    DS11228 ~~~ DS11229
    DS11229 ~~~ DS11235
    DS11235 ~~~ DS11237
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class DS11227,DS11228,DS11229,DS11230,DS11231,DS11232,DS11233,DS11234,DS11235,DS11236,DS11237,DS11238,JOB757591,JOB757592,JOB757593,JOB757594,JOB757595,JOB757596,JOB757597,JOB757598,JOB757599,JOB757600,JOB757601,JOB757602 design
```

## Dataset 清单

| ID | entity_name / 实体名 | scope / 范围 | domain / 域 | design_maturity / 设计成熟度 | module_id / 蓝图 | 功能简述 |
|----|----------------------|--------------|------------|------------------------------|------------------|----------|
| DS-11227 | factor_analysis.correlation_analyzer | production / 生产 | D_FACTOR / 因子 | design / 设计 | MOD-L02-001 | 因子间相关系数矩阵（识别冗余因子） |
| DS-11228 | factor_analysis.correlation_dedup | production / 生产 | D_FACTOR / 因子 | design / 设计 | MOD-L02-001 | 去重后的因子集合（移除高相关冗余因子） |
| DS-11229 | factor_analysis.decay_monitor | production / 生产 | D_FACTOR / 因子 | design / 设计 | MOD-L02-001 | 因子衰减报告（IC随时间衰减趋势） |
| DS-11230 | factor_analysis.factor_attribution | production / 生产 | D_FACTOR / 因子 | design / 设计 | MOD-L02-001 | 因子归因报告（各因子对收益的贡献分解） |
| DS-11231 | factor_analysis.factor_optimization | production / 生产 | D_FACTOR / 因子 | design / 设计 | MOD-L02-001 | 优化后的因子权重（最大化IC/最小化相关性） |
| DS-11232 | factor_analysis.ic_decay | production / 生产 | D_FACTOR / 因子 | design / 设计 | MOD-L02-001 | IC衰减曲线（因子预测力随滞后的变化） |
| DS-11233 | factor_analysis.ic_ir_calc | production / 生产 | D_FACTOR / 因子 | design / 设计 | MOD-L02-001 | IC/IR指标序列（因子信息系数/信息比率） |
| DS-11234 | factor_analysis.ic_ir_evaluator | production / 生产 | D_FACTOR / 因子 | design / 设计 | MOD-L02-001 | IC/IR评估报告（因子有效性评级） |
| DS-11235 | factor_analysis.layered_backtest | production / 生产 | D_FACTOR / 因子 | design / 设计 | MOD-L02-001 | 分层回测结果（按因子分层的收益统计） |
| DS-11236 | factor_analysis.multifactor_synthesis | production / 生产 | D_FACTOR / 因子 | design / 设计 | MOD-L02-001 | 合成因子信号（多因子加权/截面排名/置信度） |
| DS-11237 | factor_analysis.three_level_judgment | production / 生产 | D_FACTOR / 因子 | design / 设计 | MOD-L02-001 | 三级研判结果（因子有效性/稳定性/贡献度评级） |
| DS-11238 | factor_analysis.turnover_analyzer | production / 生产 | D_FACTOR / 因子 | design / 设计 | MOD-L02-001 | 换手率分析报告（因子换手成本评估） |

## Job 清单

| ID | job_name / 作业名 | trigger_type / 触发类型 | design_maturity / 设计成熟度 | module_id / 蓝图 | 功能简述 |
|----|-------------------|----------------------------|------------------------------|------------------|----------|
| JOB-757591 | analyze.correlation_analyzer | manual / 手动 | design / 设计 | MOD-L02-001 | 因子相关性分析（消费因子信号，产出分析结果） |
| JOB-757592 | analyze.correlation_dedup | manual / 手动 | design / 设计 | MOD-L02-001 | 因子去重（消费因子信号，产出分析结果） |
| JOB-757593 | analyze.decay_monitor | manual / 手动 | design / 设计 | MOD-L02-001 | 因子衰减监控（消费因子信号，产出分析结果） |
| JOB-757594 | analyze.factor_attribution | manual / 手动 | design / 设计 | MOD-L02-001 | 因子归因（消费因子信号，产出分析结果） |
| JOB-757595 | analyze.factor_optimization | manual / 手动 | design / 设计 | MOD-L02-001 | 因子优化（消费因子信号，产出分析结果） |
| JOB-757596 | analyze.ic_decay | manual / 手动 | design / 设计 | MOD-L02-001 | IC衰减分析（消费因子信号，产出分析结果） |
| JOB-757597 | analyze.ic_ir_calc | manual / 手动 | design / 设计 | MOD-L02-001 | IC/IR计算（消费因子信号，产出分析结果） |
| JOB-757598 | analyze.ic_ir_evaluator | manual / 手动 | design / 设计 | MOD-L02-001 | IC/IR评估（消费因子信号，产出分析结果） |
| JOB-757599 | analyze.layered_backtest | manual / 手动 | design / 设计 | MOD-L02-001 | 分层回测（消费因子信号，产出分析结果） |
| JOB-757600 | analyze.multifactor_synthesis | manual / 手动 | design / 设计 | MOD-L02-001 | 多因子合成（消费因子信号，产出分析结果） |
| JOB-757601 | analyze.three_level_judgment | manual / 手动 | design / 设计 | MOD-L02-001 | 三级研判（消费因子信号，产出分析结果） |
| JOB-757602 | analyze.turnover_analyzer | manual / 手动 | design / 设计 | MOD-L02-001 | 换手率分析（消费因子信号，产出分析结果） |

[← 返回索引](dataflow_index.md)
