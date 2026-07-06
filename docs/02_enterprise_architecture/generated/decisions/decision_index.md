# 决策流图（decisiongraph）索引

> 生成时间: 2026-07-06T11:52:03
> 真源: `architecture_model/domain/decision_graph_model.yaml` → PostgreSQL `decision_*` 表（TRAE-061）
> 数据库: depgraph (PostgreSQL)

## 概述

决策流图（decisiongraph）是与依赖图（depgraph）、数据流图（dataflowgraph）正交的第三维度全景图。
- depgraph 表达"谁依赖谁"（模块依赖，静态）
- dataflowgraph 表达"数据从哪流到哪"（数据流向，动态）
- decisiongraph 表达"决策如何产生"（决策流，动态）
- 三图通过 `module_id` 关联：决策节点 → 实现模块（depgraph）→ 数据流作业（dataflowgraph）

## 统计

| 类型 | 数量 |
|------|------|
| Track（轨） | 4 |
| Layer（层） | 10 |
| Node（节点） | 0 |
| Edge（边） | 0 |

## Mermaid 图表

### 全景图（L0-L6 层级 + 四轨并行）
- [decision_overview.mmd](decision_overview.mmd)

### 层级详情图（10 层卡片 + 频率/状态）
- [decision_layers.mmd](decision_layers.mmd)

### 不变量图（6 节点类型 + 5 承重墙不变量）
- [decision_invariants.mmd](decision_invariants.mmd)

## Track 清单（四轨）

| track_id | 名称 | 英文名 | 优先级 | 激活条件 |
|----------|------|--------|--------|----------|
| model_driven | 模型驱动轨 | Model-Driven Track | 1 | 正常运行时 |
| data_driven | 数据驱动轨 | Data-Driven Track | 2 | 模型驱动轨信号不足时补充 |
| human_override | 人工指令轨 | Human Override Track | 3 | 人工干预时 |
| emergency | 应急保命轨 | Emergency Track | 4 | 所有模型/策略/信号失效时 |

## Layer 清单（L0-L6）

| layer_id | 名称 | 英文名 | 所属轨 | 决策频率 | 成熟度 | build_status |
|----------|------|--------|--------|----------|--------|--------------|
| L0 | 数据接入与预处理层 | Data Ingestion & Preprocessing | model_driven | tick | production | stable |
| L1 | 因子计算层 | Factor Calculation | model_driven | daily | production | stable |
| L2A | 信号层 | Signal Generation | model_driven | daily | design | planned |
| L2B | 主力行为层 | Main Force Behavior Analysis | model_driven | daily | design | planned |
| L2C | 市场状态与大盘预测层 | Market State & Index Prediction | model_driven | daily | design | planned |
| L2D | 知识图谱与因果推演层 | Knowledge Graph & Causal Inference | model_driven | daily | design | planned |
| L3 | 策略组合层 | Strategy & Portfolio Combination | model_driven | daily | design | planned |
| L4 | 风控层 | Risk Control | model_driven | realtime | production | stable |
| L5 | 学习层 | Learning & Optimization | model_driven | weekly | design | planned |
| L6 | 自评估层 | Self Evaluation | model_driven | weekly | design | planned |
