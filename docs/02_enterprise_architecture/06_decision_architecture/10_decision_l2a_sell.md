---
doc_type: architecture_view
title: sell（卖出）决策流图
version: "1.0"
status: active
date: 2026-07-31
owner: auto-generator
ttl: permanent
---

# Decision Flow · L2A Functional Domain sell（卖出）

> 生成时间: 2026-07-31T17:21:51
> 真源: `architecture_model/domain/decision_graph_model.yaml` → PostgreSQL `decision_*` 表（TRAE-061）
> 数据库: depgraph (PostgreSQL)
> 导航: [返回主索引 decision_index.md](decision_index.md) | 模型驱动轨 → L2A → sell

> **[可缩放 HTML 版 / Zoomable HTML](http://localhost:8765/docs/02_enterprise_architecture/06_decision_architecture/_zoomable_html/10_decision_l2a_sell.html)** — Ctrl+滚轮缩放 ｜ 双击重置 ｜ Ctrl+Shift+D 切换拖动/选择模式

**所属轨**: 模型驱动轨（`model_driven`） | **所属层**: L2A | **功能域**: `sell`（卖出）

> **域职责 / Responsibility**: 卖出信号生成（止盈/止损/移动止损/主力出货/量价背离/突破关键位）

## 统计

- 决策节点数（全部）: 19
- 运营态节点数（production）: 0
- 设计态节点数（design）: 19
- 域内边数: 18
- 跨域出边: 1（1 个外部域）
- 跨域入边: 0（0 个外部域）

## 域内依赖图 / Internal Dependency Diagram

> **图例说明 / Legend**：
> - 🟦 **蓝色 = 运营态模块**（production，已上线运行）
> - 🟧 **橙色虚线 = 设计态模块**（design，蓝图阶段，代码未写）
> - **实线箭头 `-->` = 运营态依赖**（两端都 production）
> - **虚线箭头 `-.->` = 非运营态依赖**（含 design / 混合）

### 全景图（全部模块，颜色区分运营态/设计态）

> 展示全部 19 个决策节点（运营态 0 + 设计态 19），含跨域依赖外部节点。

> 共 10 层，18 边。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'clusterBkg': 'transparent', 'clusterBorder': 'transparent', 'fontSize': '14px'}}}%%
flowchart TD
    LL0["(生产态 / production) L0 数据接入与预处理层 /<br/>Data Ingestion & Preprocessing<br/>miniQMT + iFind + tushare + 另类数据源 → 事件总…<br/>文件: MOD-MKT_DATA"]
    LL1["(生产态 / production) L1 因子计算层 / Factor<br/>Calculation<br/>因子工厂全生命周期管理 → 盘前全量<br/>/盘中增量双模计算 → 因子池 产出：fa…<br/>文件: MOD-L02-001"]
    LL2A["(设计态 / design) L2A 信号层 / Signal Generation<br/>信号工厂 → 多策略投票 → 收益率条件密度预测 →<br/>Transformer/…<br/>文件: （设计态，暂无代码引用）"]
    N1["(设计态 / design) 卖出决策域入口 / Sell<br/>Decision Entry<br/>卖出决策节点·卖出决策域入口<br/>文件: decision/sell/sell_00"]
    LL2A --- N1
    N2["(设计态 / design) 止盈信号 / Take-Profit Signal<br/>卖出决策节点·止盈信号<br/>文件: decision/sell/sell_01"]
    LL2A --- N2
    N3["(设计态 / design) 止损信号 / Stop-Loss Signal<br/>卖出决策节点·止损信号<br/>文件: decision/sell/sell_02"]
    LL2A --- N3
    N4["(设计态 / design) 移动止损 / Trailing Stop<br/>卖出决策节点·移动止损<br/>文件: decision/sell/sell_03"]
    LL2A --- N4
    N5["(设计态 / design) 主力出货信号 / Main Force<br/>Distribution Signal<br/>卖出决策节点·主力出货信号<br/>文件: decision/sell/sell_04"]
    LL2A --- N5
    N6["(设计态 / design) 量价背离卖出 / Volume-Price<br/>Divergence Sell<br/>卖出决策节点·量价背离卖出<br/>文件: decision/sell/sell_05"]
    LL2A --- N6
    N7["(设计态 / design) 突破关键位卖出 / Key-Level<br/>Breakdown Sell<br/>卖出决策节点·突破关键位卖出<br/>文件: decision/sell/sell_06"]
    LL2A --- N7
    N8["(设计态 / design) Watch List 实时卖出 / Watch<br/>List Realtime Sell<br/>卖出决策节点·Watch List 实时卖出<br/>文件: decision/sell/sell_07"]
    LL2A --- N8
    N9["(设计态 / design) Monitor List 定期扫描 /<br/>Monitor List Periodic Scan<br/>卖出决策节点·Monitor List 定期扫描<br/>文件: decision/sell/sell_08"]
    LL2A --- N9
    N10["(设计态 / design) 卖出信号融合仲裁 / Sell<br/>Signal Fusion Arbiter<br/>卖出决策节点·卖出信号融合仲裁<br/>文件: decision/sell/sell_09"]
    LL2A --- N10
    N11["(设计态 / design) 买卖冲突仲裁 / Buy-Sell<br/>Conflict Arbiter<br/>卖出决策节点·买卖冲突仲裁<br/>文件: decision/sell/sell_10"]
    LL2A --- N11
    N12["(设计态 / design) 部分卖出vs全部清仓决策 /<br/>Partial vs Full Sell Decision<br/>卖出决策节点·部分卖出vs全部清仓决策<br/>文件: decision/sell/sell_11"]
    LL2A --- N12
    N13["(设计态 / design) D-S证据理论融合 / D-S<br/>Evidence Theory Fusion<br/>卖出决策节点·D-S证据理论融合<br/>文件: decision/sell/sell_12"]
    LL2A --- N13
    N14["(设计态 / design) 做T决策协调 / T-Trade<br/>Coordinator<br/>卖出决策节点·做T决策协调<br/>文件: decision/sell/sell_13"]
    LL2A --- N14
    N15["(设计态 / design) 黑天鹅强制卖出 / Black Swan<br/>Forced Sell<br/>卖出决策节点·黑天鹅强制卖出<br/>文件: decision/sell/sell_14"]
    LL2A --- N15
    N16["(设计态 / design) Gap开盘决策框架 / Gap Opening<br/>Decision Framework<br/>卖出决策节点·Gap开盘决策框架<br/>文件: decision/sell/sell_15"]
    LL2A --- N16
    N17["(设计态 / design) 强制清仓信号 / Forced<br/>Liquidation Signal<br/>卖出决策节点·强制清仓信号<br/>文件: decision/sell/sell_16"]
    LL2A --- N17
    N18["(设计态 / design) 卖出降级模式 / Sell<br/>Degradation Mode<br/>卖出决策节点·卖出降级模式<br/>文件: decision/sell/sell_17"]
    LL2A --- N18
    N19["(设计态 / design) 卖出决策闭环优化 / Sell<br/>Decision Closed-Loop<br/>卖出决策节点·卖出决策闭环优化<br/>文件: decision/sell/sell_18"]
    LL2A --- N19
    LL2B["(设计态 / design) L2B 主力行为层 / Main Force<br/>Behavior Analysis<br/>六阶段识别 + 自迭代推演 + 庄家专项 +<br/>群体博弈模拟 产出：main_f…<br/>文件: （设计态，暂无代码引用）"]
    LL2C["(设计态 / design) L2C 市场状态与大盘预测层 /<br/>Market State & Index Prediction<br/>3×3矩阵 + 2叠加态 + 三层大盘预测 +<br/>T+1次日8态走势预测 + 体…<br/>文件: （设计态，暂无代码引用）"]
    LL2D["(设计态 / design) L2D 知识图谱与因果推演层 /<br/>Knowledge Graph & Causal Inference<br/>六类知识图谱 → 事件影响链分析 → 因果传导推演 →<br/>GNN股票关系建模 →…<br/>文件: （设计态，暂无代码引用）"]
    LL3["(生产态 / production) L3 策略组合层 / Strategy<br/>& Portfolio Combination<br/>多策略信号合成 → 资本分配 → 元策略路由 →<br/>组合构建 产出：portfo…<br/>文件: MOD-L05-001"]
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
    N1 -.->|informing / 告知| N2
    N2 -.->|informing / 告知| N3
    N3 -.->|informing / 告知| N4
    N4 -.->|informing / 告知| N5
    N5 -.->|informing / 告知| N6
    N6 -.->|informing / 告知| N7
    N7 -.->|informing / 告知| N8
    N8 -.->|informing / 告知| N9
    N9 -.->|informing / 告知| N10
    N10 -.->|informing / 告知| N11
    N11 -.->|informing / 告知| N12
    N12 -.->|informing / 告知| N13
    N13 -.->|informing / 告知| N14
    N14 -.->|informing / 告知| N15
    N15 -.->|informing / 告知| N16
    N16 -.->|informing / 告知| N17
    N17 -.->|informing / 告知| N18
    N18 -.->|informing / 告知| N19
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class LL0,LL1,LL3,LL4 production
    class LL2A,N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15,N16,N17,N18,N19,LL2B,LL2C,LL2D,LL5,LL6 design
```

### 运营态的图（仅 design_maturity=production 的模块和域内依赖）

> 仅展示已上线运行的决策节点（共 0 个），不含跨域外部节点。跨域依赖见下方跨域依赖章节。

> （无模块 / No modules）

### 设计态的图（仅 design_maturity=design 的模块和域内依赖）

> 仅展示蓝图阶段、代码未写的设计态决策节点（共 19 个），不含跨域外部节点。

> 共 6 层，18 边。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'clusterBkg': 'transparent', 'clusterBorder': 'transparent', 'fontSize': '14px'}}}%%
flowchart TD
    LL2A["(设计态 / design) L2A 信号层 / Signal Generation<br/>信号工厂 → 多策略投票 → 收益率条件密度预测 →<br/>Transformer/…<br/>文件: （设计态，暂无代码引用）"]
    N1["(设计态 / design) 卖出决策域入口 / Sell<br/>Decision Entry<br/>卖出决策节点·卖出决策域入口<br/>文件: decision/sell/sell_00"]
    LL2A --- N1
    N2["(设计态 / design) 止盈信号 / Take-Profit Signal<br/>卖出决策节点·止盈信号<br/>文件: decision/sell/sell_01"]
    LL2A --- N2
    N3["(设计态 / design) 止损信号 / Stop-Loss Signal<br/>卖出决策节点·止损信号<br/>文件: decision/sell/sell_02"]
    LL2A --- N3
    N4["(设计态 / design) 移动止损 / Trailing Stop<br/>卖出决策节点·移动止损<br/>文件: decision/sell/sell_03"]
    LL2A --- N4
    N5["(设计态 / design) 主力出货信号 / Main Force<br/>Distribution Signal<br/>卖出决策节点·主力出货信号<br/>文件: decision/sell/sell_04"]
    LL2A --- N5
    N6["(设计态 / design) 量价背离卖出 / Volume-Price<br/>Divergence Sell<br/>卖出决策节点·量价背离卖出<br/>文件: decision/sell/sell_05"]
    LL2A --- N6
    N7["(设计态 / design) 突破关键位卖出 / Key-Level<br/>Breakdown Sell<br/>卖出决策节点·突破关键位卖出<br/>文件: decision/sell/sell_06"]
    LL2A --- N7
    N8["(设计态 / design) Watch List 实时卖出 / Watch<br/>List Realtime Sell<br/>卖出决策节点·Watch List 实时卖出<br/>文件: decision/sell/sell_07"]
    LL2A --- N8
    N9["(设计态 / design) Monitor List 定期扫描 /<br/>Monitor List Periodic Scan<br/>卖出决策节点·Monitor List 定期扫描<br/>文件: decision/sell/sell_08"]
    LL2A --- N9
    N10["(设计态 / design) 卖出信号融合仲裁 / Sell<br/>Signal Fusion Arbiter<br/>卖出决策节点·卖出信号融合仲裁<br/>文件: decision/sell/sell_09"]
    LL2A --- N10
    N11["(设计态 / design) 买卖冲突仲裁 / Buy-Sell<br/>Conflict Arbiter<br/>卖出决策节点·买卖冲突仲裁<br/>文件: decision/sell/sell_10"]
    LL2A --- N11
    N12["(设计态 / design) 部分卖出vs全部清仓决策 /<br/>Partial vs Full Sell Decision<br/>卖出决策节点·部分卖出vs全部清仓决策<br/>文件: decision/sell/sell_11"]
    LL2A --- N12
    N13["(设计态 / design) D-S证据理论融合 / D-S<br/>Evidence Theory Fusion<br/>卖出决策节点·D-S证据理论融合<br/>文件: decision/sell/sell_12"]
    LL2A --- N13
    N14["(设计态 / design) 做T决策协调 / T-Trade<br/>Coordinator<br/>卖出决策节点·做T决策协调<br/>文件: decision/sell/sell_13"]
    LL2A --- N14
    N15["(设计态 / design) 黑天鹅强制卖出 / Black Swan<br/>Forced Sell<br/>卖出决策节点·黑天鹅强制卖出<br/>文件: decision/sell/sell_14"]
    LL2A --- N15
    N16["(设计态 / design) Gap开盘决策框架 / Gap Opening<br/>Decision Framework<br/>卖出决策节点·Gap开盘决策框架<br/>文件: decision/sell/sell_15"]
    LL2A --- N16
    N17["(设计态 / design) 强制清仓信号 / Forced<br/>Liquidation Signal<br/>卖出决策节点·强制清仓信号<br/>文件: decision/sell/sell_16"]
    LL2A --- N17
    N18["(设计态 / design) 卖出降级模式 / Sell<br/>Degradation Mode<br/>卖出决策节点·卖出降级模式<br/>文件: decision/sell/sell_17"]
    LL2A --- N18
    N19["(设计态 / design) 卖出决策闭环优化 / Sell<br/>Decision Closed-Loop<br/>卖出决策节点·卖出决策闭环优化<br/>文件: decision/sell/sell_18"]
    LL2A --- N19
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
    N1 -.->|informing / 告知| N2
    N2 -.->|informing / 告知| N3
    N3 -.->|informing / 告知| N4
    N4 -.->|informing / 告知| N5
    N5 -.->|informing / 告知| N6
    N6 -.->|informing / 告知| N7
    N7 -.->|informing / 告知| N8
    N8 -.->|informing / 告知| N9
    N9 -.->|informing / 告知| N10
    N10 -.->|informing / 告知| N11
    N11 -.->|informing / 告知| N12
    N12 -.->|informing / 告知| N13
    N13 -.->|informing / 告知| N14
    N14 -.->|informing / 告知| N15
    N15 -.->|informing / 告知| N16
    N16 -.->|informing / 告知| N17
    N17 -.->|informing / 告知| N18
    N18 -.->|informing / 告知| N19
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class LL2A,N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15,N16,N17,N18,N19,LL2B,LL2C,LL2D,LL5,LL6 design
```

## Node 清单

| node_id / 节点ID | layer / 层 | type / 类型 | name / 名称 | path / 路径 | module_id / 模块 | 代码引用 / ref | maturity / 成熟度 | build_status / 构建状态 |
|---------|-------|------|------|------|-----------|----------|--------|--------------|
| 1 | L2A | sell_decision / 卖出决策节点 | 卖出决策域入口 Sell Decision Entry | decision/sell/sell_00 | - | - | design / 设计 | planned / 已规划 |
| 2 | L2A | sell_decision / 卖出决策节点 | 止盈信号 Take-Profit Signal | decision/sell/sell_01 | - | - | design / 设计 | planned / 已规划 |
| 3 | L2A | sell_decision / 卖出决策节点 | 止损信号 Stop-Loss Signal | decision/sell/sell_02 | - | - | design / 设计 | planned / 已规划 |
| 4 | L2A | sell_decision / 卖出决策节点 | 移动止损 Trailing Stop | decision/sell/sell_03 | - | - | design / 设计 | planned / 已规划 |
| 5 | L2A | sell_decision / 卖出决策节点 | 主力出货信号 Main Force Distribution Signal | decision/sell/sell_04 | - | - | design / 设计 | planned / 已规划 |
| 6 | L2A | sell_decision / 卖出决策节点 | 量价背离卖出 Volume-Price Divergence Sell | decision/sell/sell_05 | - | - | design / 设计 | planned / 已规划 |
| 7 | L2A | sell_decision / 卖出决策节点 | 突破关键位卖出 Key-Level Breakdown Sell | decision/sell/sell_06 | - | - | design / 设计 | planned / 已规划 |
| 8 | L2A | sell_decision / 卖出决策节点 | Watch List 实时卖出 Watch List Realtime Sell | decision/sell/sell_07 | - | - | design / 设计 | planned / 已规划 |
| 9 | L2A | sell_decision / 卖出决策节点 | Monitor List 定期扫描 Monitor List Periodic Scan | decision/sell/sell_08 | - | - | design / 设计 | planned / 已规划 |
| 10 | L2A | sell_decision / 卖出决策节点 | 卖出信号融合仲裁 Sell Signal Fusion Arbiter | decision/sell/sell_09 | - | - | design / 设计 | planned / 已规划 |
| 11 | L2A | sell_decision / 卖出决策节点 | 买卖冲突仲裁 Buy-Sell Conflict Arbiter | decision/sell/sell_10 | - | - | design / 设计 | planned / 已规划 |
| 12 | L2A | sell_decision / 卖出决策节点 | 部分卖出vs全部清仓决策 Partial vs Full Sell Decision | decision/sell/sell_11 | - | - | design / 设计 | planned / 已规划 |
| 13 | L2A | sell_decision / 卖出决策节点 | D-S证据理论融合 D-S Evidence Theory Fusion | decision/sell/sell_12 | - | - | design / 设计 | planned / 已规划 |
| 14 | L2A | sell_decision / 卖出决策节点 | 做T决策协调 T-Trade Coordinator | decision/sell/sell_13 | - | - | design / 设计 | planned / 已规划 |
| 15 | L2A | sell_decision / 卖出决策节点 | 黑天鹅强制卖出 Black Swan Forced Sell | decision/sell/sell_14 | - | - | design / 设计 | planned / 已规划 |
| 16 | L2A | sell_decision / 卖出决策节点 | Gap开盘决策框架 Gap Opening Decision Framework | decision/sell/sell_15 | - | - | design / 设计 | planned / 已规划 |
| 17 | L2A | sell_decision / 卖出决策节点 | 强制清仓信号 Forced Liquidation Signal | decision/sell/sell_16 | - | - | design / 设计 | planned / 已规划 |
| 18 | L2A | sell_decision / 卖出决策节点 | 卖出降级模式 Sell Degradation Mode | decision/sell/sell_17 | - | - | design / 设计 | planned / 已规划 |
| 19 | L2A | sell_decision / 卖出决策节点 | 卖出决策闭环优化 Sell Decision Closed-Loop | decision/sell/sell_18 | - | - | design / 设计 | planned / 已规划 |

## Edge 清单（域内）

| edge_id / 边ID | from / 起点 | to / 终点 | type / 类型 | condition / 条件 | track / 轨 |
|---------|-------|-----|------|-----------|-------|
| 19 | 1 | 2 | informing / 告知 | L2A层内顺序流 | - |
| 20 | 2 | 3 | informing / 告知 | L2A层内顺序流 | - |
| 21 | 3 | 4 | informing / 告知 | L2A层内顺序流 | - |
| 22 | 4 | 5 | informing / 告知 | L2A层内顺序流 | - |
| 23 | 5 | 6 | informing / 告知 | L2A层内顺序流 | - |
| 24 | 6 | 7 | informing / 告知 | L2A层内顺序流 | - |
| 25 | 7 | 8 | informing / 告知 | L2A层内顺序流 | - |
| 26 | 8 | 9 | informing / 告知 | L2A层内顺序流 | - |
| 27 | 9 | 10 | informing / 告知 | L2A层内顺序流 | - |
| 28 | 10 | 11 | informing / 告知 | L2A层内顺序流 | - |
| 29 | 11 | 12 | informing / 告知 | L2A层内顺序流 | - |
| 30 | 12 | 13 | informing / 告知 | L2A层内顺序流 | - |
| 31 | 13 | 14 | informing / 告知 | L2A层内顺序流 | - |
| 32 | 14 | 15 | informing / 告知 | L2A层内顺序流 | - |
| 33 | 15 | 16 | informing / 告知 | L2A层内顺序流 | - |
| 34 | 16 | 17 | informing / 告知 | L2A层内顺序流 | - |
| 35 | 17 | 18 | informing / 告知 | L2A层内顺序流 | - |
| 36 | 18 | 19 | informing / 告知 | L2A层内顺序流 | - |

## 跨域出边（Depends On）

| # | 本域节点 / from | → | 外部域-目标节点 / to | type / 类型 |
|:--:|---------|:--:|---------|---------|
| 1 | decision/sell/sell_18 | → | decision/signal/sg_01 | informing / 告知 |

## 跨域入边（Depended By）

> （无跨域入边）

## 跨域依赖图（Cross-Domain Dependency Graph）

> 本域与 1 个外部域直接连接 / This domain directly connects to 1 external domain(s).

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'clusterBkg': 'transparent', 'clusterBorder': 'transparent', 'fontSize': '14px'}}}%%
flowchart TD
    SELF["(设计态 / design) 卖出 / sell<br/>卖出信号生成（止盈/止损/移动止损/主力出货<br/>/量价背离/突破关键位）<br/>跨域节点 / cross-domain"]
    EXT_signal["(设计态 / design) 信号 / signal<br/>Alpha 信号合成、优先级路由、LLM 策略 Agent<br/>与尾部风险保护<br/>跨域节点 / cross-domain"]
    SELF -.->|出 1| EXT_signal
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class SELF design
    class EXT_signal external_design
```

