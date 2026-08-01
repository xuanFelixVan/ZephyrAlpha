---
doc_type: architecture_view
title: ex_sor（执行排序）决策流图
version: "1.0"
status: active
date: 2026-07-31
owner: auto-generator
ttl: permanent
---

# Decision Flow · L3 Functional Domain ex_sor（执行排序）

> 生成时间: 2026-07-31T17:21:51
> 真源: `architecture_model/domain/decision_graph_model.yaml` → PostgreSQL `decision_*` 表（TRAE-061）
> 数据库: depgraph (PostgreSQL)
> 导航: [返回主索引 decision_index.md](decision_index.md) | 模型驱动轨 → L3 → ex_sor

> **[可缩放 HTML 版 / Zoomable HTML](http://localhost:8765/docs/02_enterprise_architecture/06_decision_architecture/_zoomable_html/15_decision_l3_ex_sor.html)** — Ctrl+滚轮缩放 ｜ 双击重置 ｜ Ctrl+Shift+D 切换拖动/选择模式

**所属轨**: 模型驱动轨（`model_driven`） | **所属层**: L3 | **功能域**: `ex_sor`（执行排序）

> **域职责 / Responsibility**: 智能订单路由(SOR)——路由决策、通道熔断、Kill-Switch 与熔断器矩阵

## 统计

- 决策节点数（全部）: 5
- 运营态节点数（production）: 0
- 设计态节点数（design）: 5
- 域内边数: 4
- 跨域出边: 2（2 个外部域）
- 跨域入边: 2（1 个外部域）

## 域内依赖图 / Internal Dependency Diagram

> **图例说明 / Legend**：
> - 🟦 **蓝色 = 运营态模块**（production，已上线运行）
> - 🟧 **橙色虚线 = 设计态模块**（design，蓝图阶段，代码未写）
> - **实线箭头 `-->` = 运营态依赖**（两端都 production）
> - **虚线箭头 `-.->` = 非运营态依赖**（含 design / 混合）

### 全景图（全部模块，颜色区分运营态/设计态）

> 展示全部 5 个决策节点（运营态 0 + 设计态 5），含跨域依赖外部节点。

> 共 10 层，6 边。

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
    N72["(设计态 / design) 订单路由决策 / Order Routing<br/>Decision<br/>订单节点·订单路由决策<br/>文件: decision/ex_sor/ex_16"]
    LL3 --- N72
    N73["(设计态 / design) SOR路由决策延迟 / SOR Routing<br/>Latency<br/>订单节点·SOR路由决策延迟<br/>文件: decision/ex_sor/ex_17"]
    LL3 --- N73
    N75["(设计态 / design) 交易通道熔断人工恢复 /<br/>Trading Channel Manual Recovery<br/>订单节点·交易通道熔断人工恢复<br/>文件: decision/ex_sor/ex_19"]
    LL3 --- N75
    N77["(设计态 / design) Kill-Switch四级阶梯 /<br/>Kill-Switch 4-Level Cascade<br/>订单节点·Kill-Switch四级阶梯<br/>文件: decision/ex_sor/ex_21"]
    LL3 --- N77
    N78["(设计态 / design) 熔断器矩阵 / Circuit Breaker<br/>Matrix<br/>订单节点·熔断器矩阵<br/>文件: decision/ex_sor/ex_22"]
    LL3 --- N78
    LL4["(生产态 / production) L4 风控层 / Risk Control<br/>Pre/Post-Trade 风控校验 + Kill Switch 熔断 + …<br/>文件: MOD-L04-001"]
    N74["(设计态 / design) 券商连接熔断+故障转移 /<br/>Broker Circuit Breaker<br/>风控检查节点·券商连接熔断+故障转移<br/>文件: decision/ex_sor/ex_18"]
    LL4 --- N74
    N76["(设计态 / design) Pre-Trade合规检查流水线 /<br/>Pre-Trade Compliance Pipeline<br/>合规检查节点·Pre-Trade合规检查流水线<br/>文件: decision/ex_sor/ex_20"]
    LL4 --- N76
    N79["(设计态 / design) 行为准入门禁 / Behavioral<br/>Admission Gateway<br/>合规检查节点·行为准入门禁<br/>文件: decision/ex_sor/ex_23"]
    LL4 --- N79
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
    N72 -.->|informing / 告知| N73
    N73 -.->|informing / 告知| N75
    N75 -.->|informing / 告知| N77
    N77 -.->|informing / 告知| N78
    N74 -.->|informing / 告知| N76
    N76 -.->|informing / 告知| N79
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class LL0,LL1,LL3,LL4 production
    class LL2A,LL2B,LL2C,LL2D,N72,N73,N75,N77,N78,N74,N76,N79,LL5,LL6 design
```

### 运营态的图（仅 design_maturity=production 的模块和域内依赖）

> 仅展示已上线运行的决策节点（共 0 个），不含跨域外部节点。跨域依赖见下方跨域依赖章节。

> （无模块 / No modules）

### 设计态的图（仅 design_maturity=design 的模块和域内依赖）

> 仅展示蓝图阶段、代码未写的设计态决策节点（共 5 个），不含跨域外部节点。

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
| 72 | L3 | order / 订单节点 | 订单路由决策 Order Routing Decision | decision/ex_sor/ex_16 | MOD-L05-001 | - | design / 设计 | planned / 已规划 |
| 73 | L3 | order / 订单节点 | SOR路由决策延迟 SOR Routing Latency | decision/ex_sor/ex_17 | MOD-L05-001 | - | design / 设计 | planned / 已规划 |
| 75 | L3 | order / 订单节点 | 交易通道熔断人工恢复 Trading Channel Manual Recovery | decision/ex_sor/ex_19 | MOD-L05-001 | - | design / 设计 | planned / 已规划 |
| 77 | L3 | order / 订单节点 | Kill-Switch四级阶梯 Kill-Switch 4-Level Cascade | decision/ex_sor/ex_21 | MOD-L05-001 | - | design / 设计 | planned / 已规划 |
| 78 | L3 | order / 订单节点 | 熔断器矩阵 Circuit Breaker Matrix | decision/ex_sor/ex_22 | MOD-L05-001 | - | design / 设计 | planned / 已规划 |

## Edge 清单（域内）

| edge_id / 边ID | from / 起点 | to / 终点 | type / 类型 | condition / 条件 | track / 轨 |
|---------|-------|-----|------|-----------|-------|
| 85 | 72 | 73 | informing / 告知 | L3层内顺序流 | - |
| 86 | 73 | 75 | informing / 告知 | L3层内顺序流 | - |
| 87 | 75 | 77 | informing / 告知 | L3层内顺序流 | - |
| 88 | 77 | 78 | informing / 告知 | L3层内顺序流 | - |

## 跨域出边（Depends On）

| # | 本域节点 / from | → | 外部域-目标节点 / to | type / 类型 |
|:--:|---------|:--:|---------|---------|
| 1 | decision/ex_sor/ex_22 | → | decision/pf_alloc/pa_01 | informing / 告知 |
| 2 | decision/ex_sor/ex_23 | → | decision/governance/gov_001 | informing / 告知 |

## 跨域入边（Depended By）

| # | 外部域-源节点 / from | → | 本域节点 / to | type / 类型 |
|:--:|---------|:--:|---------|---------|
| 1 | decision/ex_core/ex_15 | → | decision/ex_sor/ex_16 | informing / 告知 |
| 2 | decision/ex_core/ex_14 | → | decision/ex_sor/ex_18 | informing / 告知 |

## 跨域依赖图（Cross-Domain Dependency Graph）

> 本域与 3 个外部域直接连接 / This domain directly connects to 3 external domain(s).

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'clusterBkg': 'transparent', 'clusterBorder': 'transparent', 'fontSize': '14px'}}}%%
flowchart TD
    SELF["(设计态 / design) 执行排序 / ex_sor<br/>智能订单路由(SOR)——路由决策、通道熔断、Kill-Swit<br/>ch 与熔断器矩阵<br/>跨域节点 / cross-domain"]
    EXT_pf_alloc["(设计态 / design) 组合分配 / pf_alloc<br/>组合资本分配——策略分配、风险平价、动态权重、再平<br/>衡与元策略选择<br/>跨域节点 / cross-domain"]
    SELF -.->|出 1| EXT_pf_alloc
    EXT_governance["(设计态 / design) governance / governance<br/>（域职责待补）<br/>跨域节点 / cross-domain"]
    SELF -.->|出 1| EXT_governance
    EXT_ex_core["(设计态 / design) 执行核心 / ex_core<br/>订单执行核心——SLA 保障、Saga<br/>事务、风控检查、下单/成交确认与持仓更新<br/>跨域节点 / cross-domain"]
    EXT_ex_core -.->|入 2| SELF
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class SELF design
    class EXT_pf_alloc,EXT_governance,EXT_ex_core external_design
```

