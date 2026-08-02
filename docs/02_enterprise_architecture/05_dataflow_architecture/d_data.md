---
doc_type: architecture_view
title: 数据域-数据采集管理
version: "1.0"
status: active
date: 2026-08-02
owner: auto-generator
ttl: permanent
---

# 数据域-数据采集管理

> 生成时间: 2026-08-02T21:06:13
> 真源: `dataflow_graph_registry.yaml` → PostgreSQL `dataflow_*` 表
> 生成器: `generate_dataflow_diagram.py`（全文自动生成，禁止手工编辑）

> **[可缩放 HTML 版 / Zoomable HTML](http://localhost:8765/docs/02_enterprise_architecture/05_dataflow_architecture/_zoomable_html/d_data.html)** — Ctrl+滚轮缩放 ｜ 双击重置 ｜ Ctrl+Shift+D 切换拖动/选择模式

> **域职责 / Responsibility**: 数据采集与管理——特征存储/K线重采样/实时推送管理/板块快照采集/Tick数据管理

## 域基本信息 / Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| Dataset 数 | 5 | Datasets | 5 |
| Job 数 | 5 | Jobs | 5 |
| 运营态 Dataset | 0 | Production Datasets | 0 |
| 设计态 Dataset | 5 | Design Datasets | 5 |
| 运营态 Job | 0 | Production Jobs | 0 |
| 设计态 Job | 5 | Design Jobs | 5 |

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

> 展示全部 10 个节点（Dataset 5 + Job 5），含 5 条边。颜色区分运营态（蓝）/设计态（橙虚线）。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'clusterBkg': 'transparent', 'clusterBorder': 'transparent', 'fontSize': '14px'}}}%%
flowchart TD
    DS11253["(设计态 / design) data.feature_store /<br/>特征数据集<br/>（特征值/特征元数据/版本管理）<br/>契约: - · 域: 数据接入层"]
    DS11256["(设计态 / design) data.kline_resampler /<br/>重采样K线数据<br/>（多周期K线/自定义周期重采样）<br/>契约: - · 域: 数据接入层"]
    DS11254["(设计态 / design) data.realtime_push_manager /<br/>实时推送数据流<br/>（实时行情/交易推送）<br/>契约: - · 域: 数据接入层"]
    DS11257["(设计态 / design) data.sector_snapshot_<br/>collector / 板块快照数据<br/>（板块成分/权重/涨跌统计）<br/>契约: - · 域: 数据接入层"]
    DS11255["(设计态 / design) data.tick_data_manager /<br/>Tick数据管理记录<br/>（Tick数据生命周期/清理）<br/>契约: - · 域: 数据接入层"]
    JOB757617("(设计态 / design) data.feature_store /<br/>特征存储管理<br/>（数据采集/管理服务）<br/>文件: feature_store/")
    JOB757620("(设计态 / design) data.kline_resampler /<br/>K线重采样<br/>（数据采集/管理服务）<br/>文件: zephyr.data.kline_resampler")
    JOB757618("(设计态 / design) data.realtime_push_manager /<br/>实时推送管理<br/>（数据采集/管理服务）<br/>文件: realtime_push_manager/")
    JOB757621("(设计态 / design) data.sector_snapshot_<br/>collector / 板块快照采集<br/>（数据采集/管理服务）<br/>文件: zephyr.data.sector_snapshot_collector")
    JOB757619("(设计态 / design) data.tick_data_manager /<br/>Tick数据管理<br/>（数据采集/管理服务）<br/>文件: tick_data_manager/")
    JOB757617 -.->|produces / 产出| DS11253
    JOB757618 -.->|produces / 产出| DS11254
    JOB757619 -.->|produces / 产出| DS11255
    JOB757620 -.->|produces / 产出| DS11256
    JOB757621 -.->|produces / 产出| DS11257
    JOB757617 ~~~ JOB757620
    JOB757620 ~~~ JOB757618
    JOB757618 ~~~ JOB757621
    JOB757621 ~~~ JOB757619
    DS11253 ~~~ DS11256
    DS11256 ~~~ DS11254
    DS11254 ~~~ DS11257
    DS11257 ~~~ DS11255
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class DS11253,DS11256,DS11254,DS11257,DS11255,JOB757617,JOB757620,JOB757618,JOB757621,JOB757619 design
```

### 运营态的图（仅 design_maturity=production）

> （无模块 / No modules）

### 设计态的图（仅 design_maturity=design）

> 仅展示蓝图阶段、代码未写的设计态节点（设计态：5 datasets / 数据集, 5 jobs / 作业, 5 edges / 边）。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'clusterBkg': 'transparent', 'clusterBorder': 'transparent', 'fontSize': '14px'}}}%%
flowchart TD
    DS11253["(设计态 / design) data.feature_store /<br/>特征数据集<br/>（特征值/特征元数据/版本管理）<br/>契约: - · 域: 数据接入层"]
    DS11256["(设计态 / design) data.kline_resampler /<br/>重采样K线数据<br/>（多周期K线/自定义周期重采样）<br/>契约: - · 域: 数据接入层"]
    DS11254["(设计态 / design) data.realtime_push_manager /<br/>实时推送数据流<br/>（实时行情/交易推送）<br/>契约: - · 域: 数据接入层"]
    DS11257["(设计态 / design) data.sector_snapshot_<br/>collector / 板块快照数据<br/>（板块成分/权重/涨跌统计）<br/>契约: - · 域: 数据接入层"]
    DS11255["(设计态 / design) data.tick_data_manager /<br/>Tick数据管理记录<br/>（Tick数据生命周期/清理）<br/>契约: - · 域: 数据接入层"]
    JOB757617("(设计态 / design) data.feature_store /<br/>特征存储管理<br/>（数据采集/管理服务）<br/>文件: feature_store/")
    JOB757620("(设计态 / design) data.kline_resampler /<br/>K线重采样<br/>（数据采集/管理服务）<br/>文件: zephyr.data.kline_resampler")
    JOB757618("(设计态 / design) data.realtime_push_manager /<br/>实时推送管理<br/>（数据采集/管理服务）<br/>文件: realtime_push_manager/")
    JOB757621("(设计态 / design) data.sector_snapshot_<br/>collector / 板块快照采集<br/>（数据采集/管理服务）<br/>文件: zephyr.data.sector_snapshot_collector")
    JOB757619("(设计态 / design) data.tick_data_manager /<br/>Tick数据管理<br/>（数据采集/管理服务）<br/>文件: tick_data_manager/")
    JOB757617 -.->|produces / 产出| DS11253
    JOB757618 -.->|produces / 产出| DS11254
    JOB757619 -.->|produces / 产出| DS11255
    JOB757620 -.->|produces / 产出| DS11256
    JOB757621 -.->|produces / 产出| DS11257
    JOB757617 ~~~ JOB757620
    JOB757620 ~~~ JOB757618
    JOB757618 ~~~ JOB757621
    JOB757621 ~~~ JOB757619
    DS11253 ~~~ DS11256
    DS11256 ~~~ DS11254
    DS11254 ~~~ DS11257
    DS11257 ~~~ DS11255
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class DS11253,DS11256,DS11254,DS11257,DS11255,JOB757617,JOB757620,JOB757618,JOB757621,JOB757619 design
```

## Dataset 清单

| ID | entity_name / 实体名 | scope / 范围 | domain / 域 | design_maturity / 设计成熟度 | module_id / 蓝图 | 功能简述 |
|----|----------------------|--------------|------------|------------------------------|------------------|----------|
| DS-11253 | data.feature_store | production / 生产 | D_DATA / 数据接入层 | design / 设计 | MOD-L00-004 | 特征数据集（特征值/特征元数据/版本管理） |
| DS-11256 | data.kline_resampler | production / 生产 | D_DATA / 数据接入层 | design / 设计 | MOD-L00-004 | 重采样K线数据（多周期K线/自定义周期重采样） |
| DS-11254 | data.realtime_push_manager | production / 生产 | D_DATA / 数据接入层 | design / 设计 | MOD-L00-004 | 实时推送数据流（实时行情/交易推送） |
| DS-11257 | data.sector_snapshot_collector | production / 生产 | D_DATA / 数据接入层 | design / 设计 | MOD-L00-004 | 板块快照数据（板块成分/权重/涨跌统计） |
| DS-11255 | data.tick_data_manager | production / 生产 | D_DATA / 数据接入层 | design / 设计 | MOD-L00-004 | Tick数据管理记录（Tick数据生命周期/清理） |

## Job 清单

| ID | job_name / 作业名 | trigger_type / 触发类型 | design_maturity / 设计成熟度 | module_id / 蓝图 | 功能简述 |
|----|-------------------|----------------------------|------------------------------|------------------|----------|
| JOB-757617 | data.feature_store | scheduled / 定时 | design / 设计 | MOD-L00-004 | 特征存储管理（数据采集/管理服务） |
| JOB-757620 | data.kline_resampler | scheduled / 定时 | design / 设计 | MOD-L00-004 | K线重采样（数据采集/管理服务） |
| JOB-757618 | data.realtime_push_manager | scheduled / 定时 | design / 设计 | MOD-L00-004 | 实时推送管理（数据采集/管理服务） |
| JOB-757621 | data.sector_snapshot_collector | scheduled / 定时 | design / 设计 | MOD-L00-004 | 板块快照采集（数据采集/管理服务） |
| JOB-757619 | data.tick_data_manager | scheduled / 定时 | design / 设计 | MOD-L00-004 | Tick数据管理（数据采集/管理服务） |

[← 返回索引](dataflow_index.md)
