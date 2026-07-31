---
doc_type: architecture_view
title: 数据域-数据采集管理
version: "1.0"
status: active
date: 2026-07-31
owner: auto-generator
ttl: permanent
---

# 数据域-数据采集管理

> 生成时间: 2026-07-31T17:03:35
> 真源: `dataflow_graph_registry.yaml` → PostgreSQL `dataflow_*` 表
> 生成器: `generate_dataflow_diagram.py`（全文自动生成，禁止手工编辑）

> **域职责 / Responsibility**: 数据采集与管理——特征存储/K线重采样/实时推送管理/板块快照采集/Tick数据管理

## 数据流图（全景：设计态+运营态合并）

> 节点数: 5 datasets / 数据集, 5 jobs / 作业, 5 edges / 边
>
> **图例**：🟦 蓝色 = 运营态（已实现）/ 🟧 橙色虚线 = 设计态（未实现）

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart LR
    DS11253["[design]data.feature_store<br/>特征数据集<br/>（特征值/特征元数据/版本管理）"]
    DS11256["[design]data.kline_resampler<br/>重采样K线数据<br/>（多周期K线/自定义周期重采样）"]
    DS11254["[design]data.realtime_push_manager<br/>实时推送数据流<br/>（实时行情/交易推送）"]
    DS11257["[design]data.sector_snapshot_collector<br/>板块快照数据<br/>（板块成分/权重/涨跌统计）"]
    DS11255["[design]data.tick_data_manager<br/>Tick数据管理记录<br/>（Tick数据生命周期/清理）"]
    JOB757617("[design]data.feature_store<br/>特征存储管理<br/>（数据采集/管理服务）")
    JOB757620("[design]data.kline_resampler<br/>K线重采样<br/>（数据采集/管理服务）")
    JOB757618("[design]data.realtime_push_manager<br/>实时推送管理<br/>（数据采集/管理服务）")
    JOB757621("[design]data.sector_snapshot_collector<br/>板块快照采集<br/>（数据采集/管理服务）")
    JOB757619("[design]data.tick_data_manager<br/>Tick数据管理<br/>（数据采集/管理服务）")
    JOB757617 -->|produces / 产出| DS11253
    JOB757618 -->|produces / 产出| DS11254
    JOB757619 -->|produces / 产出| DS11255
    JOB757620 -->|produces / 产出| DS11256
    JOB757621 -->|produces / 产出| DS11257
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    class DS11253,DS11256,DS11254,DS11257,DS11255,JOB757617,JOB757620,JOB757618,JOB757621,JOB757619 design
```

## 数据流图（设计态）

> 节点数: 5 datasets / 数据集, 5 jobs / 作业, 5 edges / 边

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    DS11253["[design]data.feature_store<br/>特征数据集<br/>（特征值/特征元数据/版本管理）"]
    DS11256["[design]data.kline_resampler<br/>重采样K线数据<br/>（多周期K线/自定义周期重采样）"]
    DS11254["[design]data.realtime_push_manager<br/>实时推送数据流<br/>（实时行情/交易推送）"]
    DS11257["[design]data.sector_snapshot_collector<br/>板块快照数据<br/>（板块成分/权重/涨跌统计）"]
    DS11255["[design]data.tick_data_manager<br/>Tick数据管理记录<br/>（Tick数据生命周期/清理）"]
    JOB757617("[design]data.feature_store<br/>特征存储管理<br/>（数据采集/管理服务）")
    JOB757620("[design]data.kline_resampler<br/>K线重采样<br/>（数据采集/管理服务）")
    JOB757618("[design]data.realtime_push_manager<br/>实时推送管理<br/>（数据采集/管理服务）")
    JOB757621("[design]data.sector_snapshot_collector<br/>板块快照采集<br/>（数据采集/管理服务）")
    JOB757619("[design]data.tick_data_manager<br/>Tick数据管理<br/>（数据采集/管理服务）")
    JOB757617 -->|produces / 产出| DS11253
    JOB757618 -->|produces / 产出| DS11254
    JOB757619 -->|produces / 产出| DS11255
    JOB757620 -->|produces / 产出| DS11256
    JOB757621 -->|produces / 产出| DS11257
    DS11253 ~~~ JOB757620
    DS11256 ~~~ JOB757618
    DS11254 ~~~ JOB757621
    DS11257 ~~~ JOB757619
```

## Dataset 清单

| ID | entity_name / 实体名 | scope / 范围 | domain / 域 | design_maturity / 设计成熟度 | module_id / 蓝图 | 功能简述 |
|----|----------------------|--------------|------------|------------------------------|------------------|----------|
| DS-11253 | data.feature_store | production / 生产 | D_DATA | design / 设计 | MOD-L00-004 | 特征数据集（特征值/特征元数据/版本管理） |
| DS-11256 | data.kline_resampler | production / 生产 | D_DATA | design / 设计 | MOD-L00-004 | 重采样K线数据（多周期K线/自定义周期重采样） |
| DS-11254 | data.realtime_push_manager | production / 生产 | D_DATA | design / 设计 | MOD-L00-004 | 实时推送数据流（实时行情/交易推送） |
| DS-11257 | data.sector_snapshot_collector | production / 生产 | D_DATA | design / 设计 | MOD-L00-004 | 板块快照数据（板块成分/权重/涨跌统计） |
| DS-11255 | data.tick_data_manager | production / 生产 | D_DATA | design / 设计 | MOD-L00-004 | Tick数据管理记录（Tick数据生命周期/清理） |

## Job 清单

| ID | job_name / 作业名 | trigger_type / 触发类型 | design_maturity / 设计成熟度 | module_id / 蓝图 | 功能简述 |
|----|-------------------|----------------------------|------------------------------|------------------|----------|
| JOB-757617 | data.feature_store | scheduled / 定时 | design / 设计 | MOD-L00-004 | 特征存储管理（数据采集/管理服务） |
| JOB-757620 | data.kline_resampler | scheduled / 定时 | design / 设计 | MOD-L00-004 | K线重采样（数据采集/管理服务） |
| JOB-757618 | data.realtime_push_manager | scheduled / 定时 | design / 设计 | MOD-L00-004 | 实时推送管理（数据采集/管理服务） |
| JOB-757621 | data.sector_snapshot_collector | scheduled / 定时 | design / 设计 | MOD-L00-004 | 板块快照采集（数据采集/管理服务） |
| JOB-757619 | data.tick_data_manager | scheduled / 定时 | design / 设计 | MOD-L00-004 | Tick数据管理（数据采集/管理服务） |

[← 返回索引](dataflow_index.md)
