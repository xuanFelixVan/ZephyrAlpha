---
doc_type: architecture_view
title: trading（交易）决策流图
version: "1.0"
status: active
date: 2026-08-01
owner: auto-generator
ttl: permanent
---

# Decision Flow · L3 Functional Domain trading（交易）

> 生成时间: 2026-08-01T22:22:08
> 真源: `architecture_model/domain/decision_graph_model.yaml` → PostgreSQL `decision_*` 表（TRAE-061）
> 数据库: depgraph (PostgreSQL)
> 导航: [返回主索引 decision_index.md](decision_index.md) | 模型驱动轨 → L3 → trading

> **[可缩放 HTML 版 / Zoomable HTML](http://localhost:8765/docs/02_enterprise_architecture/06_decision_architecture/_zoomable_html/19_decision_l3_trading.html)** — Ctrl+滚轮缩放 ｜ 双击重置 ｜ Ctrl+Shift+D 切换拖动/选择模式

**所属轨**: 模型驱动轨（`model_driven`） | **所属层**: L3 | **功能域**: `trading`（交易）

> **域职责 / Responsibility**: 交易管理——结算、公司行动、保证金、多账户、微信枢纽与交易纪律执行

## 统计

- 决策节点数（全部）: 11
- 运营态节点数（production）: 0
- 设计态节点数（design）: 11
- 域内边数: 10
- 跨域出边: 1（1 个外部域）
- 跨域入边: 1（1 个外部域）

## 域内依赖图 / Internal Dependency Diagram

> **图例说明 / Legend**：
> - 🟦 **蓝色 = 运营态模块**（production，已上线运行）
> - 🟧 **橙色虚线 = 设计态模块**（design，蓝图阶段，代码未写）
> - **实线箭头 `-->` = 运营态依赖**（两端都 production）
> - **虚线箭头 `-.->` = 非运营态依赖**（含 design / 混合）

### 全景图（全部模块，颜色区分运营态/设计态）

> 展示全部 11 个决策节点（运营态 0 + 设计态 11），含跨域依赖外部节点。

> 共 10 层，10 边。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'clusterBkg': 'transparent', 'clusterBorder': 'transparent', 'fontSize': '14px'}}}%%
flowchart TD
    LL0["(生产态 / production) L0 数据接入与预处理层 /<br/>Data Ingestion & Preprocessing<br/>miniQMT + iFind + tushare + 另类数据源 → 事件总…<br/>文件: MOD-MKT_DATA"]
    LL1["(生产态 / production) L1 因子计算层 / Factor<br/>Calculation<br/>因子工厂全生命周期管理 → 盘前全量<br/>/盘中增量双模计算 → 因子池 产出：fa…<br/>文件: MOD-L02-001"]
    LL2A["(设计态 / design) L2A 信号层 / Signal Generation<br/>信号工厂 → 多策略投票 → 收益率条件密度预测 →<br/>Transformer/…<br/>文件: （设计态，暂无代码引用）"]
    LL2B["(设计态 / design) L2B 主力行为层 / Main Force<br/>Behavior Analysis<br/>六阶段识别 + 自迭代推演 + 庄家专项 +<br/>群体博弈模拟 产出：main_f…<br/>文件: （设计态，暂无代码引用）"]
    LL2C["(设计态 / design) L2C 市场状态与大盘预测层 /<br/>Market State & Index Prediction<br/>3×3矩阵 + 2叠加态 + 三层大盘预测 +<br/>T+1次日8态走势预测 + 体…<br/>文件: （设计态，暂无代码引用）"]
    LL2D["(设计态 / design) L2D 知识图谱与因果推演层 /<br/>Knowledge Graph & Causal Inference<br/>六类知识图谱 → 事件影响链分析 → 因果传导推演 →<br/>GNN股票关系建模 →…<br/>文件: （设计态，暂无代码引用）"]
    LL3["(生产态 / production) L3 策略组合层 / Strategy<br/>& Portfolio Combination<br/>多策略信号合成 → 资本分配 → 元策略路由 →<br/>组合构建 产出：portfo…<br/>文件: MOD-L05-001"]
    N102["(设计态 / design) 外部订单观察者 / External<br/>Order Watcher<br/>订单节点·外部订单观察者<br/>文件: decision/trading/trd_01"]
    LL3 --- N102
    N103["(设计态 / design) 结算引擎 / Settlement Engine<br/>订单节点·结算引擎<br/>文件: decision/trading/trd_02"]
    LL3 --- N103
    N104["(设计态 / design) 公司行动 / Corporate Action<br/>订单节点·公司行动<br/>文件: decision/trading/trd_03"]
    LL3 --- N104
    N105["(设计态 / design) 保证金管理 / Margin Manager<br/>订单节点·保证金管理<br/>文件: decision/trading/trd_04"]
    LL3 --- N105
    N106["(设计态 / design) 多账户 / Multi-Account<br/>订单节点·多账户<br/>文件: decision/trading/trd_05"]
    LL3 --- N106
    N107["(设计态 / design) 微信枢纽 / WeChat Hub<br/>订单节点·微信枢纽<br/>文件: decision/trading/trd_06"]
    LL3 --- N107
    N108["(设计态 / design) C-013 4级优先级 / C-013<br/>4-Level Priority<br/>订单节点·C-013 4级优先级<br/>文件: decision/trading/trd_07"]
    LL3 --- N108
    N109["(设计态 / design) A股交易纪律四项必做 / A-Share<br/>Trading 4-Do<br/>订单节点·A股交易纪律四项必做<br/>文件: decision/trading/trd_08"]
    LL3 --- N109
    N110["(设计态 / design) A股交易纪律四项严禁 / A-Share<br/>Trading 4-Forbidden<br/>订单节点·A股交易纪律四项严禁<br/>文件: decision/trading/trd_09"]
    LL3 --- N110
    N111["(设计态 / design) 监管报送 / Regulatory<br/>Reporting<br/>订单节点·监管报送<br/>文件: decision/trading/trd_10"]
    LL3 --- N111
    N112["(设计态 / design) 盘中即时反应决策引擎 /<br/>Intraday Instant Reaction Decision Engine<br/>订单节点·盘中即时反应决策引擎<br/>文件: decision/trading/trd_11"]
    LL3 --- N112
    LL4["(生产态 / production) L4 风控层 / Risk Control<br/>Pre/Post-Trade 风控校验 + Kill Switch 熔断 + …<br/>文件: MOD-L04-001"]
    LL5["(设计态 / design) L5 学习层 / Learning &<br/>Optimization<br/>7阶段学习流水线 → 模块工厂 → 知识采集 →<br/>反馈闭环 产出：learni…<br/>文件: （设计态，暂无代码引用）"]
    LL6["(设计态 / design) L6 自评估层 / Self Evaluation<br/>LLM 自评估(Judge+交叉验证) + 多模态金融推理 +<br/>VeNRA零幻…<br/>文件: （设计态，暂无代码引用）"]
    LL0 -->|triggering / 触发| LL1
    LL1 -.->|triggering / 触发| LL2A
    LL2A -.->|triggering / 触发| LL2B
    LL2B -.->|triggering / 触发| LL2C
    LL2C -.->|triggering / 触发| LL2D
    LL2D -.->|triggering / 触发| LL3
    LL3 -->|triggering / 触发| LL4
    LL4 -.->|triggering / 触发| LL5
    LL5 -.->|triggering / 触发| LL6
    N102 -.->|informing / 告知| N103
    N103 -.->|informing / 告知| N104
    N104 -.->|informing / 告知| N105
    N105 -.->|informing / 告知| N106
    N106 -.->|informing / 告知| N107
    N107 -.->|informing / 告知| N108
    N108 -.->|informing / 告知| N109
    N109 -.->|informing / 告知| N110
    N110 -.->|informing / 告知| N111
    N111 -.->|informing / 告知| N112
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class LL0,LL1,LL3,LL4 production
    class LL2A,LL2B,LL2C,LL2D,N102,N103,N104,N105,N106,N107,N108,N109,N110,N111,N112,LL5,LL6 design
```

### 运营态的图（仅 design_maturity=production 的模块和域内依赖）

> 仅展示已上线运行的决策节点（共 0 个），不含跨域外部节点。跨域依赖见下方跨域依赖章节。

> （无模块 / No modules）

### 设计态的图（仅 design_maturity=design 的模块和域内依赖）

> 仅展示蓝图阶段、代码未写的设计态决策节点（共 11 个），不含跨域外部节点。

> 共 6 层，0 边。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'clusterBkg': 'transparent', 'clusterBorder': 'transparent', 'fontSize': '14px'}}}%%
flowchart TD
    LL2A["(设计态 / design) L2A 信号层 / Signal Generation<br/>信号工厂 → 多策略投票 → 收益率条件密度预测 →<br/>Transformer/…<br/>文件: （设计态，暂无代码引用）"]
    LL2B["(设计态 / design) L2B 主力行为层 / Main Force<br/>Behavior Analysis<br/>六阶段识别 + 自迭代推演 + 庄家专项 +<br/>群体博弈模拟 产出：main_f…<br/>文件: （设计态，暂无代码引用）"]
    LL2C["(设计态 / design) L2C 市场状态与大盘预测层 /<br/>Market State & Index Prediction<br/>3×3矩阵 + 2叠加态 + 三层大盘预测 +<br/>T+1次日8态走势预测 + 体…<br/>文件: （设计态，暂无代码引用）"]
    LL2D["(设计态 / design) L2D 知识图谱与因果推演层 /<br/>Knowledge Graph & Causal Inference<br/>六类知识图谱 → 事件影响链分析 → 因果传导推演 →<br/>GNN股票关系建模 →…<br/>文件: （设计态，暂无代码引用）"]
    LL5["(设计态 / design) L5 学习层 / Learning &<br/>Optimization<br/>7阶段学习流水线 → 模块工厂 → 知识采集 →<br/>反馈闭环 产出：learni…<br/>文件: （设计态，暂无代码引用）"]
    LL6["(设计态 / design) L6 自评估层 / Self Evaluation<br/>LLM 自评估(Judge+交叉验证) + 多模态金融推理 +<br/>VeNRA零幻…<br/>文件: （设计态，暂无代码引用）"]
    LL2A -.->|triggering / 触发| LL2B
    LL2B -.->|triggering / 触发| LL2C
    LL2C -.->|triggering / 触发| LL2D
    LL2D -.->|triggering / 触发| LL5
    LL5 -.->|triggering / 触发| LL6
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class LL2A,LL2B,LL2C,LL2D,LL5,LL6 design
```

## Node 清单

| node_id / 节点ID | layer / 层 | type / 类型 | name / 名称 | path / 路径 | module_id / 模块 | 代码引用 / ref | maturity / 成熟度 | build_status / 构建状态 |
|---------|-------|------|------|------|-----------|----------|--------|--------------|
| 102 | L3 | order / 订单节点 | 外部订单观察者 External Order Watcher | decision/trading/trd_01 | MOD-L05-001 | - | design / 设计 | planned / 已规划 |
| 103 | L3 | order / 订单节点 | 结算引擎 Settlement Engine | decision/trading/trd_02 | MOD-L05-001 | - | design / 设计 | planned / 已规划 |
| 104 | L3 | order / 订单节点 | 公司行动 Corporate Action | decision/trading/trd_03 | MOD-L05-001 | - | design / 设计 | planned / 已规划 |
| 105 | L3 | order / 订单节点 | 保证金管理 Margin Manager | decision/trading/trd_04 | MOD-L05-001 | - | design / 设计 | planned / 已规划 |
| 106 | L3 | order / 订单节点 | 多账户 Multi-Account | decision/trading/trd_05 | MOD-L05-001 | - | design / 设计 | planned / 已规划 |
| 107 | L3 | order / 订单节点 | 微信枢纽 WeChat Hub | decision/trading/trd_06 | MOD-L05-001 | - | design / 设计 | planned / 已规划 |
| 108 | L3 | order / 订单节点 | C-013 4级优先级 C-013 4-Level Priority | decision/trading/trd_07 | MOD-L05-001 | - | design / 设计 | planned / 已规划 |
| 109 | L3 | order / 订单节点 | A股交易纪律四项必做 A-Share Trading 4-Do | decision/trading/trd_08 | MOD-L05-001 | - | design / 设计 | planned / 已规划 |
| 110 | L3 | order / 订单节点 | A股交易纪律四项严禁 A-Share Trading 4-Forbidden | decision/trading/trd_09 | MOD-L05-001 | - | design / 设计 | planned / 已规划 |
| 111 | L3 | order / 订单节点 | 监管报送 Regulatory Reporting | decision/trading/trd_10 | MOD-L05-001 | - | design / 设计 | planned / 已规划 |
| 112 | L3 | order / 订单节点 | 盘中即时反应决策引擎 Intraday Instant Reaction Decision Engine | decision/trading/trd_11 | MOD-L05-001 | - | design / 设计 | planned / 已规划 |

## Edge 清单（域内）

| edge_id / 边ID | from / 起点 | to / 终点 | type / 类型 | condition / 条件 | track / 轨 |
|---------|-------|-----|------|-----------|-------|
| 127 | 102 | 103 | informing / 告知 | L3层内顺序流 | - |
| 128 | 103 | 104 | informing / 告知 | L3层内顺序流 | - |
| 129 | 104 | 105 | informing / 告知 | L3层内顺序流 | - |
| 130 | 105 | 106 | informing / 告知 | L3层内顺序流 | - |
| 131 | 106 | 107 | informing / 告知 | L3层内顺序流 | - |
| 132 | 107 | 108 | informing / 告知 | L3层内顺序流 | - |
| 133 | 108 | 109 | informing / 告知 | L3层内顺序流 | - |
| 134 | 109 | 110 | informing / 告知 | L3层内顺序流 | - |
| 135 | 110 | 111 | informing / 告知 | L3层内顺序流 | - |
| 136 | 111 | 112 | informing / 告知 | L3层内顺序流 | - |

## 跨域出边（Depends On）

| # | 本域节点 / from | → | 外部域-目标节点 / to | type / 类型 |
|:--:|---------|:--:|---------|---------|
| 1 | decision/trading/trd_11 | → | decision/aut_core/ac_02 | informing / 告知 |

## 跨域入边（Depended By）

| # | 外部域-源节点 / from | → | 本域节点 / to | type / 类型 |
|:--:|---------|:--:|---------|---------|
| 1 | decision/position/pos_19 | → | decision/trading/trd_01 | informing / 告知 |

## 跨域依赖图（Cross-Domain Dependency Graph）

> 本域与 2 个外部域直接连接 / This domain directly connects to 2 external domain(s).

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'clusterBkg': 'transparent', 'clusterBorder': 'transparent', 'fontSize': '14px'}}}%%
flowchart TD
    SELF["(设计态 / design) 交易 / trading<br/>交易管理——结算、公司行动、保证金、多账户、微信枢<br/>纽与交易纪律执行<br/>跨域节点 / cross-domain"]
    EXT_aut_core["(设计态 / design) 自主核心 / aut_core<br/>自主决策编排——权限守卫、自愈回滚、预算执行、健康<br/>监控、漂移检测、自动修复与 Agent 编排<br/>跨域节点 / cross-domain"]
    SELF -.->|出 1| EXT_aut_core
    EXT_position["(设计态 / design) 持仓 / position<br/>持仓管理——仓位唯一裁决、状态机、漂移监控、Kelly<br/>决策与市场状态仓位上限<br/>跨域节点 / cross-domain"]
    EXT_position -.->|入 1| SELF
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class SELF design
    class EXT_aut_core,EXT_position external_design
```

