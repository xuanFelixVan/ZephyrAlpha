---
doc_type: architecture_view
title: D_ASHARE_SIGNAL A股特色信号架构文档
version: "1.0"
status: active
date: 2026-08-03
owner: auto-generator
ttl: permanent
---

# 32_d_ashare_signal / A股特色信号域 / A-Share Signal

> **功能简介 / Overview**: A 股特色信号，负责 A 股市场特色交易信号的生成和管理

> **文档作用 / Purpose**: 展示 A股特色信号（D_ASHARE_SIGNAL）功能域的域内依赖关系、跨域依赖关系，模块信息（成熟度/中英文名/大白话/文件路径）内嵌于 Mermaid 节点，供架构审查和域治理参考。

> 本文档由 generate_domain_doc.py 从 depgraph (PostgreSQL) 自动生成
> 数据源: depgraph (PostgreSQL) nodes表 + edges表

> **[可缩放 HTML 版 / Zoomable HTML](http://localhost:8765/docs/02_enterprise_architecture/02_domain_architecture_docs/_zoomable_html/32_d_ashare_signal.html)** — Ctrl+滚轮缩放 ｜ 双击重置 ｜ Ctrl+Shift+D 切换拖动/选择模式

## 域基本信息 / Domain Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 编号 | 32 | Number | 32 |
| 域ID | D_ASHARE_SIGNAL | Domain ID | D_ASHARE_SIGNAL |
| 域名称 | A股特色信号 | Domain Name | A-Share Signal |
| 层级 | L2 业务域层 | Layer | L2 Domain |
| 模块数 | 18 | Module Count | 18 |
| 域内依赖 | 7 | Internal Dependencies | 7 |
| 跨域入边 | 1 | Cross-domain Incoming | 1 |
| 跨域出边 | 0 | Cross-domain Outgoing | 0 |
| 设计态模块 | 2 | Design Modules | 2 |
| 生产态模块 | 16 | Production Modules | 16 |
| 容量 | 16/150 (正常) | Capacity | 16/150 (正常) |
| 描述 | A股特色信号生成 | Description | A股特色信号生成 |

## 域内依赖图 / Internal Dependency Diagram

> 依赖图内嵌在本文档中，IDE 可直接渲染；网页版可 Ctrl+滚轮缩放 + 拖动平移查看细节。
>
> **图例说明 / Legend**：
> - 🟦 **蓝色 = 运营态模块**（production，已上线运行）
> - 🟧 **橙色虚线 = 设计态模块**（design，蓝图阶段，代码未写）
> - **实线箭头 = 运营态依赖**（已生效的依赖关系）
> - **虚线箭头 = 非运营态依赖**（计划中/验证中的依赖关系）

### 全景图（全部模块，颜色区分运营态/设计态）

> 展示全部 18 个模块（生产态 16 + 设计态 2），含跨域依赖外部节点。节点含成熟度+名称+大白话/简介+文件路径。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    src_zephyr_signal_ashare_init_py["zephyr/signal_ashare 包入口<br/>signal ashare 包入口，整合signal<br/>ashare相关子模块导出<br/>文件: signal_ashare/__init__.py<br/>(生产态 / production)"]
    src_zephyr_signal_ashare_extensions_init_py["signal_ashare/_extensions 包入口<br/>signal ashare 扩展<br/>包入口，整合扩展相关子模块导出<br/>文件: _extensions/__init__.py<br/>(生产态 / production)"]
    src_zephyr_signal_ashare_api_init_py["signal_ashare/api 包入口<br/>signal ashare 接口<br/>包入口，整合接口相关子模块导出<br/>文件: api/__init__.py<br/>(生产态 / production)"]
    src_zephyr_signal_ashare_core_init_py["signal_ashare/core 包入口<br/>signal ashare 核心<br/>包入口，整合核心相关子模块导出<br/>文件: core/__init__.py<br/>(生产态 / production)"]
    src_zephyr_signal_ashare_dual_engine_fusion_decision_engine_py["双引擎融合决策引擎<br/>信号的引擎，执行核心逻辑的处理引擎（dual engine<br/>fusion decision）<br/>dual_engine_fusion_decision_engine<br/>文件: signal_ashare<br/>/dual_engine_fusion_decision_engine.py<br/>(生产态 / production)"]
    src_zephyr_signal_ashare_infrastructure_init_py["signal_ashare/infrastructure 包入口<br/>signal ashare 基础设施<br/>包入口，整合基础设施相关子模块导出<br/>文件: infrastructure/__init__.py<br/>(生产态 / production)"]
    src_zephyr_signal_ashare_market_sentiment_analyzer_py["市场情绪分析器<br/>信号的分析器，分析数据找出问题或规律（market<br/>sentiment）<br/>market_sentiment_analyzer<br/>文件: signal_ashare/market_sentiment_analyzer.py<br/>(生产态 / production)"]
    src_zephyr_signal_ashare_market_state_sensor_py["市场状态传感器<br/>实时检测A股市场状态（牛市/熊市<br/>/震荡等），为策略切换提供状态依据。<br/>文件: signal_ashare/market_state_sensor.py<br/>(设计态 / design)"]
    src_zephyr_signal_ashare_models_init_py["signal_ashare/models 包入口<br/>signal ashare 模型<br/>包入口，整合模型相关子模块导出<br/>文件: models/__init__.py<br/>(生产态 / production)"]
    src_zephyr_signal_ashare_next_day_8state_forecast_py["次日8态预测器<br/>预测下一个交易日的8种市场状态概率分布，为次日交<br/>易策略提供前瞻性参考。<br/>文件: signal_ashare/next_day_8state_forecast.py<br/>(设计态 / design)"]
    src_zephyr_signal_ashare_sector_analyzer_py["板块分析器<br/>信号的分析器，分析数据找出问题或规律（sector）<br/>sector_analyzer<br/>文件: signal_ashare/sector_analyzer.py<br/>(生产态 / production)"]
    src_zephyr_signal_ashare_services_init_py["signal_ashare/services 包入口<br/>signal ashare 服务<br/>包入口，整合服务相关子模块导出<br/>文件: services/__init__.py<br/>(生产态 / production)"]
    src_zephyr_signal_ashare_short_term_stock_selector_py["短期股票选择器<br/>信号的选择器，按条件选择最优项<br/>short_term_stock_selector<br/>文件: signal_ashare/short_term_stock_selector.py<br/>(生产态 / production)"]
    src_zephyr_signal_ashare_init_py ~~~ src_zephyr_signal_ashare_extensions_init_py
    src_zephyr_signal_ashare_extensions_init_py ~~~ src_zephyr_signal_ashare_api_init_py
    src_zephyr_signal_ashare_api_init_py ~~~ src_zephyr_signal_ashare_core_init_py
    src_zephyr_signal_ashare_core_init_py ~~~ src_zephyr_signal_ashare_dual_engine_fusion_decision_engine_py
    src_zephyr_signal_ashare_dual_engine_fusion_decision_engine_py ~~~ src_zephyr_signal_ashare_infrastructure_init_py
    src_zephyr_signal_ashare_infrastructure_init_py ~~~ src_zephyr_signal_ashare_market_sentiment_analyzer_py
    src_zephyr_signal_ashare_market_sentiment_analyzer_py ~~~ src_zephyr_signal_ashare_market_state_sensor_py
    src_zephyr_signal_ashare_market_state_sensor_py ~~~ src_zephyr_signal_ashare_models_init_py
    src_zephyr_signal_ashare_models_init_py ~~~ src_zephyr_signal_ashare_next_day_8state_forecast_py
    src_zephyr_signal_ashare_next_day_8state_forecast_py ~~~ src_zephyr_signal_ashare_sector_analyzer_py
    src_zephyr_signal_ashare_sector_analyzer_py ~~~ src_zephyr_signal_ashare_services_init_py
    src_zephyr_signal_ashare_services_init_py ~~~ src_zephyr_signal_ashare_short_term_stock_selector_py
    src_zephyr_signal_ashare_intraday_buy_sell_point_analyzer_py["日内买卖点分析器<br/>信号的分析器，分析数据找出问题或规律（intraday<br/>buy sell point）<br/>intraday_buy_sell_point_analyzer<br/>文件: signal_ashare<br/>/intraday_buy_sell_point_analyzer.py<br/>(生产态 / production)"]
    src_zephyr_signal_ashare_quant_short_term_strength_engine_py["量化短期强度引擎<br/>信号的引擎，执行核心逻辑的处理引擎（quant short<br/>term strength）<br/>quant_short_term_strength_engine<br/>文件: signal_ashare<br/>/quant_short_term_strength_engine.py<br/>(生产态 / production)"]
    src_zephyr_signal_ashare_youzi_relay_emotion_engine_py["游资中继情绪引擎<br/>信号的引擎，执行核心逻辑的处理引擎（youzi relay<br/>emotion）<br/>youzi_relay_emotion_engine<br/>文件: signal_ashare<br/>/youzi_relay_emotion_engine.py<br/>(生产态 / production)"]
    src_zephyr_signal_ashare_intraday_buy_sell_point_analyzer_py ~~~ src_zephyr_signal_ashare_quant_short_term_strength_engine_py
    src_zephyr_signal_ashare_quant_short_term_strength_engine_py ~~~ src_zephyr_signal_ashare_youzi_relay_emotion_engine_py
    src_zephyr_signal_ashare_capital_flow_pattern_analyzer_py["资本流模式分析器<br/>信号的分析器，分析数据找出问题或规律（capital<br/>flow pattern）<br/>capital_flow_pattern_analyzer<br/>文件: signal_ashare<br/>/capital_flow_pattern_analyzer.py<br/>(生产态 / production)"]
    src_zephyr_signal_ashare_institutional_behavior_analyzer_py["机构行为分析器<br/>信号的分析器，分析数据找出问题或规律<br/>（institutional behavior）<br/>institutional_behavior_analyzer<br/>文件: signal_ashare<br/>/institutional_behavior_analyzer.py<br/>(生产态 / production)"]
    src_zephyr_signal_ashare_capital_flow_pattern_analyzer_py ~~~ src_zephyr_signal_ashare_institutional_behavior_analyzer_py
    src_zephyr_signal_ashare_intraday_buy_sell_point_analyzer_py -->|import / import| src_zephyr_signal_ashare_capital_flow_pattern_analyzer_py
    src_zephyr_signal_ashare_intraday_buy_sell_point_analyzer_py -->|import / import| src_zephyr_signal_ashare_institutional_behavior_analyzer_py
    src_zephyr_signal_ashare_dual_engine_fusion_decision_engine_py -->|runtime / runtime| src_zephyr_signal_ashare_quant_short_term_strength_engine_py
    src_zephyr_signal_ashare_dual_engine_fusion_decision_engine_py -->|导入依赖 / import_depends| src_zephyr_signal_ashare_quant_short_term_strength_engine_py
    src_zephyr_signal_ashare_dual_engine_fusion_decision_engine_py -->|导入依赖 / import_depends| src_zephyr_signal_ashare_youzi_relay_emotion_engine_py
    src_zephyr_signal_ashare_dual_engine_fusion_decision_engine_py -->|runtime / runtime| src_zephyr_signal_ashare_youzi_relay_emotion_engine_py
    src_zephyr_signal_ashare_init_py -->|config_depends / config_depends| src_zephyr_signal_ashare_intraday_buy_sell_point_analyzer_py
    D_FUNDAMENTAL_SIGNAL["基本面信号<br/>基本面信号，负责基于财务数据的基本面信号生成<br/>Fundamental Signal<br/>跨域节点 / cross-domain<br/>(设计态 / design)"]
    D_FUNDAMENTAL_SIGNAL -.->|event / event| src_zephyr_signal_ashare_institutional_behavior_analyzer_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_signal_ashare_init_py,src_zephyr_signal_ashare_extensions_init_py,src_zephyr_signal_ashare_api_init_py,src_zephyr_signal_ashare_capital_flow_pattern_analyzer_py,src_zephyr_signal_ashare_core_init_py,src_zephyr_signal_ashare_dual_engine_fusion_decision_engine_py,src_zephyr_signal_ashare_infrastructure_init_py,src_zephyr_signal_ashare_institutional_behavior_analyzer_py,src_zephyr_signal_ashare_intraday_buy_sell_point_analyzer_py,src_zephyr_signal_ashare_market_sentiment_analyzer_py,src_zephyr_signal_ashare_models_init_py,src_zephyr_signal_ashare_quant_short_term_strength_engine_py,src_zephyr_signal_ashare_sector_analyzer_py,src_zephyr_signal_ashare_services_init_py,src_zephyr_signal_ashare_short_term_stock_selector_py,src_zephyr_signal_ashare_youzi_relay_emotion_engine_py production
    class src_zephyr_signal_ashare_market_state_sensor_py,src_zephyr_signal_ashare_next_day_8state_forecast_py design
    class D_FUNDAMENTAL_SIGNAL external_design
```

### 运营态的图（仅 design_maturity=production 的模块和域内依赖）

> 仅展示已上线运行的模块（共 16 个），不含跨域外部节点。跨域依赖见下方跨域依赖章节。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    src_zephyr_signal_ashare_init_py["zephyr/signal_ashare 包入口<br/>signal ashare 包入口，整合signal<br/>ashare相关子模块导出<br/>文件: signal_ashare/__init__.py<br/>(生产态 / production)"]
    src_zephyr_signal_ashare_extensions_init_py["signal_ashare/_extensions 包入口<br/>signal ashare 扩展<br/>包入口，整合扩展相关子模块导出<br/>文件: _extensions/__init__.py<br/>(生产态 / production)"]
    src_zephyr_signal_ashare_api_init_py["signal_ashare/api 包入口<br/>signal ashare 接口<br/>包入口，整合接口相关子模块导出<br/>文件: api/__init__.py<br/>(生产态 / production)"]
    src_zephyr_signal_ashare_core_init_py["signal_ashare/core 包入口<br/>signal ashare 核心<br/>包入口，整合核心相关子模块导出<br/>文件: core/__init__.py<br/>(生产态 / production)"]
    src_zephyr_signal_ashare_dual_engine_fusion_decision_engine_py["双引擎融合决策引擎<br/>信号的引擎，执行核心逻辑的处理引擎（dual engine<br/>fusion decision）<br/>dual_engine_fusion_decision_engine<br/>文件: signal_ashare<br/>/dual_engine_fusion_decision_engine.py<br/>(生产态 / production)"]
    src_zephyr_signal_ashare_infrastructure_init_py["signal_ashare/infrastructure 包入口<br/>signal ashare 基础设施<br/>包入口，整合基础设施相关子模块导出<br/>文件: infrastructure/__init__.py<br/>(生产态 / production)"]
    src_zephyr_signal_ashare_market_sentiment_analyzer_py["市场情绪分析器<br/>信号的分析器，分析数据找出问题或规律（market<br/>sentiment）<br/>market_sentiment_analyzer<br/>文件: signal_ashare/market_sentiment_analyzer.py<br/>(生产态 / production)"]
    src_zephyr_signal_ashare_models_init_py["signal_ashare/models 包入口<br/>signal ashare 模型<br/>包入口，整合模型相关子模块导出<br/>文件: models/__init__.py<br/>(生产态 / production)"]
    src_zephyr_signal_ashare_sector_analyzer_py["板块分析器<br/>信号的分析器，分析数据找出问题或规律（sector）<br/>sector_analyzer<br/>文件: signal_ashare/sector_analyzer.py<br/>(生产态 / production)"]
    src_zephyr_signal_ashare_services_init_py["signal_ashare/services 包入口<br/>signal ashare 服务<br/>包入口，整合服务相关子模块导出<br/>文件: services/__init__.py<br/>(生产态 / production)"]
    src_zephyr_signal_ashare_short_term_stock_selector_py["短期股票选择器<br/>信号的选择器，按条件选择最优项<br/>short_term_stock_selector<br/>文件: signal_ashare/short_term_stock_selector.py<br/>(生产态 / production)"]
    src_zephyr_signal_ashare_init_py ~~~ src_zephyr_signal_ashare_extensions_init_py
    src_zephyr_signal_ashare_extensions_init_py ~~~ src_zephyr_signal_ashare_api_init_py
    src_zephyr_signal_ashare_api_init_py ~~~ src_zephyr_signal_ashare_core_init_py
    src_zephyr_signal_ashare_core_init_py ~~~ src_zephyr_signal_ashare_dual_engine_fusion_decision_engine_py
    src_zephyr_signal_ashare_dual_engine_fusion_decision_engine_py ~~~ src_zephyr_signal_ashare_infrastructure_init_py
    src_zephyr_signal_ashare_infrastructure_init_py ~~~ src_zephyr_signal_ashare_market_sentiment_analyzer_py
    src_zephyr_signal_ashare_market_sentiment_analyzer_py ~~~ src_zephyr_signal_ashare_models_init_py
    src_zephyr_signal_ashare_models_init_py ~~~ src_zephyr_signal_ashare_sector_analyzer_py
    src_zephyr_signal_ashare_sector_analyzer_py ~~~ src_zephyr_signal_ashare_services_init_py
    src_zephyr_signal_ashare_services_init_py ~~~ src_zephyr_signal_ashare_short_term_stock_selector_py
    src_zephyr_signal_ashare_intraday_buy_sell_point_analyzer_py["日内买卖点分析器<br/>信号的分析器，分析数据找出问题或规律（intraday<br/>buy sell point）<br/>intraday_buy_sell_point_analyzer<br/>文件: signal_ashare<br/>/intraday_buy_sell_point_analyzer.py<br/>(生产态 / production)"]
    src_zephyr_signal_ashare_quant_short_term_strength_engine_py["量化短期强度引擎<br/>信号的引擎，执行核心逻辑的处理引擎（quant short<br/>term strength）<br/>quant_short_term_strength_engine<br/>文件: signal_ashare<br/>/quant_short_term_strength_engine.py<br/>(生产态 / production)"]
    src_zephyr_signal_ashare_youzi_relay_emotion_engine_py["游资中继情绪引擎<br/>信号的引擎，执行核心逻辑的处理引擎（youzi relay<br/>emotion）<br/>youzi_relay_emotion_engine<br/>文件: signal_ashare<br/>/youzi_relay_emotion_engine.py<br/>(生产态 / production)"]
    src_zephyr_signal_ashare_intraday_buy_sell_point_analyzer_py ~~~ src_zephyr_signal_ashare_quant_short_term_strength_engine_py
    src_zephyr_signal_ashare_quant_short_term_strength_engine_py ~~~ src_zephyr_signal_ashare_youzi_relay_emotion_engine_py
    src_zephyr_signal_ashare_capital_flow_pattern_analyzer_py["资本流模式分析器<br/>信号的分析器，分析数据找出问题或规律（capital<br/>flow pattern）<br/>capital_flow_pattern_analyzer<br/>文件: signal_ashare<br/>/capital_flow_pattern_analyzer.py<br/>(生产态 / production)"]
    src_zephyr_signal_ashare_institutional_behavior_analyzer_py["机构行为分析器<br/>信号的分析器，分析数据找出问题或规律<br/>（institutional behavior）<br/>institutional_behavior_analyzer<br/>文件: signal_ashare<br/>/institutional_behavior_analyzer.py<br/>(生产态 / production)"]
    src_zephyr_signal_ashare_capital_flow_pattern_analyzer_py ~~~ src_zephyr_signal_ashare_institutional_behavior_analyzer_py
    src_zephyr_signal_ashare_intraday_buy_sell_point_analyzer_py -->|import / import| src_zephyr_signal_ashare_capital_flow_pattern_analyzer_py
    src_zephyr_signal_ashare_intraday_buy_sell_point_analyzer_py -->|import / import| src_zephyr_signal_ashare_institutional_behavior_analyzer_py
    src_zephyr_signal_ashare_dual_engine_fusion_decision_engine_py -->|runtime / runtime| src_zephyr_signal_ashare_quant_short_term_strength_engine_py
    src_zephyr_signal_ashare_dual_engine_fusion_decision_engine_py -->|导入依赖 / import_depends| src_zephyr_signal_ashare_quant_short_term_strength_engine_py
    src_zephyr_signal_ashare_dual_engine_fusion_decision_engine_py -->|导入依赖 / import_depends| src_zephyr_signal_ashare_youzi_relay_emotion_engine_py
    src_zephyr_signal_ashare_dual_engine_fusion_decision_engine_py -->|runtime / runtime| src_zephyr_signal_ashare_youzi_relay_emotion_engine_py
    src_zephyr_signal_ashare_init_py -->|config_depends / config_depends| src_zephyr_signal_ashare_intraday_buy_sell_point_analyzer_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_signal_ashare_init_py,src_zephyr_signal_ashare_extensions_init_py,src_zephyr_signal_ashare_api_init_py,src_zephyr_signal_ashare_capital_flow_pattern_analyzer_py,src_zephyr_signal_ashare_core_init_py,src_zephyr_signal_ashare_dual_engine_fusion_decision_engine_py,src_zephyr_signal_ashare_infrastructure_init_py,src_zephyr_signal_ashare_institutional_behavior_analyzer_py,src_zephyr_signal_ashare_intraday_buy_sell_point_analyzer_py,src_zephyr_signal_ashare_market_sentiment_analyzer_py,src_zephyr_signal_ashare_models_init_py,src_zephyr_signal_ashare_quant_short_term_strength_engine_py,src_zephyr_signal_ashare_sector_analyzer_py,src_zephyr_signal_ashare_services_init_py,src_zephyr_signal_ashare_short_term_stock_selector_py,src_zephyr_signal_ashare_youzi_relay_emotion_engine_py production
```

### 设计态的图（仅 design_maturity=design 的模块和域内依赖）

> 仅展示蓝图阶段、代码未写的设计态模块（共 2 个），不含跨域外部节点。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    src_zephyr_signal_ashare_market_state_sensor_py["市场状态传感器<br/>实时检测A股市场状态（牛市/熊市<br/>/震荡等），为策略切换提供状态依据。<br/>文件: signal_ashare/market_state_sensor.py<br/>(设计态 / design)"]
    src_zephyr_signal_ashare_next_day_8state_forecast_py["次日8态预测器<br/>预测下一个交易日的8种市场状态概率分布，为次日交<br/>易策略提供前瞻性参考。<br/>文件: signal_ashare/next_day_8state_forecast.py<br/>(设计态 / design)"]
    src_zephyr_signal_ashare_market_state_sensor_py ~~~ src_zephyr_signal_ashare_next_day_8state_forecast_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_signal_ashare_market_state_sensor_py,src_zephyr_signal_ashare_next_day_8state_forecast_py design
```

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

无跨域出边依赖 / No cross-domain outgoing dependencies

### 依赖本域的其他域（入边）/ Depended By

| # | 外部域-源模块 / Source Module | → | 本域模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | D_FUNDAMENTAL_SIGNAL 基本面信号: 信号冲突解决器 / Signal Conflict Resolver (router/signal_... | → | 机构行为分析器 / institutional_behavior_analyzer (signal_... | event / event |

### 跨域依赖图 / Cross-domain Dependency Diagram

> 本域与 1 个外部域直接连接（出边 0 条 + 入边 1 条 = 1 条）。只显示直接连接的域，不展开具体节点。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
graph LR
    D_ASHARE_SIGNAL["D_ASHARE_SIGNAL<br/>A股特色信号"]
    D_FUNDAMENTAL_SIGNAL["D_FUNDAMENTAL_SIGNAL<br/>基本面信号"]
    D_FUNDAMENTAL_SIGNAL -->|1条 event / event| D_ASHARE_SIGNAL
```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph (PostgreSQL)` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_doc.py`（G2+G10 合并）
- **维护方式 / Maintenance**: 自动生成，全景图更新时刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}.md`，如 `16_d_trading.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[unknown]`=未知
