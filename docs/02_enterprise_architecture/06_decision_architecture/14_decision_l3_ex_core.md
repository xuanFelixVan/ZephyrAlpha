---
doc_type: architecture_view
title: ex_core（执行核心）决策流图
version: "1.0"
status: active
date: 2026-08-02
owner: auto-generator
ttl: permanent
---

# Decision Flow · L3 Functional Domain ex_core（执行核心）

> 生成时间: 2026-08-02T22:07:21
> 真源: `architecture_model/domain/decision_graph_model.yaml` → PostgreSQL `decision_*` 表（TRAE-061）
> 数据库: depgraph (PostgreSQL)
> 导航: [返回主索引 decision_index.md](decision_index.md) | 模型驱动轨 → L3 → ex_core

> **[可缩放 HTML 版 / Zoomable HTML](http://localhost:8765/docs/02_enterprise_architecture/06_decision_architecture/_zoomable_html/14_decision_l3_ex_core.html)** — Ctrl+滚轮缩放 ｜ 双击重置 ｜ Ctrl+Shift+D 切换拖动/选择模式

**所属轨**: 模型驱动轨（`model_driven`） | **所属层**: L3 | **功能域**: `ex_core`（执行核心）

> **域职责 / Responsibility**: 订单执行核心——SLA 保障、Saga 事务、风控检查、下单/成交确认与持仓更新

## 统计

- 决策节点数（全部）: 9
- 运营态节点数（production）: 0
- 设计态节点数（design）: 9
- 域内边数: 8
- 跨域出边: 2（1 个外部域）
- 跨域入边: 2（2 个外部域）

## 域内依赖图 / Internal Dependency Diagram

> **图例说明 / Legend**：
> - 🟦 **蓝色 = 运营态模块**（production，已上线运行）
> - 🟧 **橙色虚线 = 设计态模块**（design，蓝图阶段，代码未写）
> - **实线箭头 `-->` = 运营态依赖**（两端都 production）
> - **虚线箭头 `-.->` = 非运营态依赖**（含 design / 混合）

### 全景图（全部模块，颜色区分运营态/设计态）

> 展示全部 9 个决策节点（运营态 0 + 设计态 9），含跨域依赖外部节点。

> 共 10 层，13 边。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'clusterBkg': 'transparent', 'clusterBorder': 'transparent', 'fontSize': '14px'}}}%%
flowchart TD
    LL0["(生产态 / production) L0 数据接入与预处理层 /<br/>Data Ingestion & Preprocessing<br/>miniQMT + iFind + tushare + 另类数据源 →<br/>事件总线 → 分层时序存储 产出：tick_data / ohlc_<br/>bar / factor_input_data<br/>文件: MOD-MKT_DATA"]
    LL1["(生产态 / production) L1 因子计算层 / Factor<br/>Calculation<br/>因子工厂全生命周期管理 → 盘前全量<br/>/盘中增量双模计算 → 因子池 产出：factor_value<br/>（带 PIT 合规标记）<br/>文件: MOD-L02-001"]
    LL2A["(设计态 / design) L2A 信号层 / Signal Generation<br/>信号工厂 → 多策略投票 → 收益率条件密度预测 →<br/>Transformer/Mamba时序增强 → 共形预测<br/>产出：signal（Insight: direction/confidence<br/>/horizon）<br/>文件: （设计态，暂无代码引用）"]
    LL2B["(设计态 / design) L2B 主力行为层 / Main Force<br/>Behavior Analysis<br/>六阶段识别 + 自迭代推演 + 庄家专项 +<br/>群体博弈模拟 产出：main_force_signal<br/>（主力行为画像）<br/>文件: （设计态，暂无代码引用）"]
    LL2C["(设计态 / design) L2C 市场状态与大盘预测层 /<br/>Market State & Index Prediction<br/>3×3矩阵 + 2叠加态 + 三层大盘预测 +<br/>T+1次日8态走势预测 + 体制转换检测(HMM/变点)<br/>产出：market_state_prediction（大盘方向/波动率<br/>/体制判断）<br/>文件: （设计态，暂无代码引用）"]
    LL2D["(设计态 / design) L2D 知识图谱与因果推演层 /<br/>Knowledge Graph & Causal Inference<br/>六类知识图谱 → 事件影响链分析 → 因果传导推演 →<br/>GNN股票关系建模 → Causal ML 产出：causal_<br/>inference_result（因果推断结果）<br/>文件: （设计态，暂无代码引用）"]
    LL3["(生产态 / production) L3 策略组合层 / Strategy<br/>& Portfolio Combination<br/>多策略信号合成 → 资本分配 → 元策略路由 →<br/>组合构建 产出：portfolio_target<br/>（PortfolioTarget: 目标仓位）<br/>文件: MOD-L05-001"]
    N59["(设计态 / design) 50ms SLA Fail-Closed 50ms SLA<br/>Fail-Closed<br/>执行链路50毫秒超时即失败关闭，保证执行延迟可控不<br/>堆积<br/>文件: decision/ex_core/ex_03"]
    LL3 --- N59
    N60["(设计态 / design) Saga编排式事务 / Saga<br/>Orchestrated Transaction<br/>用 Saga 模式编排分布式交易事务，保证跨服务最终一<br/>致性<br/>文件: decision/ex_core/ex_04"]
    LL3 --- N60
    N61["(设计态 / design) 风控检查 / Risk Check<br/>下单前的风控校验环节，拦截不合格订单<br/>文件: decision/ex_core/ex_05"]
    LL3 --- N61
    N62["(设计态 / design) 信号确认 / Signal Confirmation<br/>下单前最后确认信号有效性，防止过期或错误信号成交<br/>文件: decision/ex_core/ex_06"]
    LL3 --- N62
    N63["(设计态 / design) 下单提交 / Order Submit<br/>向券商接口提交订单指令，完成实际下单动作<br/>文件: decision/ex_core/ex_07"]
    LL3 --- N63
    N64["(设计态 / design) 成交确认 / Fill Confirmation<br/>接收券商回报确认成交结果，更新订单状态<br/>文件: decision/ex_core/ex_08"]
    LL3 --- N64
    N65["(设计态 / design) 持仓更新 / Position Update<br/>成交后更新持仓记录，保证持仓数据实时准确<br/>文件: decision/ex_core/ex_09"]
    LL3 --- N65
    N66["(设计态 / design) 报告生成 / Report Generation<br/>生成交易执行报告供审计和分析，记录交易全流程<br/>文件: decision/ex_core/ex_10"]
    LL3 --- N66
    N71["(设计态 / design) 流动性螺旋3阶段 / Liquidity<br/>Spiral 3-Phase<br/>识别流动性螺旋的三个阶段并应对，防止流动性枯竭时<br/>踩踏<br/>文件: decision/ex_core/ex_15"]
    LL3 --- N71
    LL4["(生产态 / production) L4 风控层 / Risk Control<br/>Pre/Post-Trade 风控校验 + Kill Switch 熔断 +<br/>止损评估 产出：risk_check（RiskDecision:<br/>approve/veto/adjust）<br/>文件: MOD-L04-001"]
    N57["(设计态 / design) Pre-Trade主链6项检查 /<br/>Pre-Trade Main Chain 6 Checks<br/>下单前主链路六项必检项目的合规检查，拦截不合规订<br/>单<br/>文件: decision/ex_core/ex_01"]
    LL4 --- N57
    N58["(设计态 / design) Kill Switch 5层防御 / Kill<br/>Switch 5-Layer Defense<br/>五层防御的急停开关体系，多层级保障紧急停止能力<br/>文件: decision/ex_core/ex_02"]
    LL4 --- N58
    N67["(设计态 / design) Kill Switch AI自动激活 / Kill<br/>Switch AI Auto Trigger<br/>AI 检测到异常时自动激活急停开关，比人工更快响应<br/>危机<br/>文件: decision/ex_core/ex_11"]
    LL4 --- N67
    N68["(设计态 / design) Kill Switch人工激活 / Kill<br/>Switch Manual Trigger<br/>人工一键激活急停开关，作为自动激活的兜底手段<br/>文件: decision/ex_core/ex_12"]
    LL4 --- N68
    N69["(设计态 / design) Kill Switch定时激活 / Kill<br/>Switch Timer Trigger<br/>按预设时间自动激活急停开关，如收盘前强制平仓<br/>文件: decision/ex_core/ex_13"]
    LL4 --- N69
    N70["(设计态 / design) Kill Switch外部信号激活 /<br/>Kill Switch External Signal<br/>外部系统信号触发急停开关，支持跨系统联动急停<br/>文件: decision/ex_core/ex_14"]
    LL4 --- N70
    LL5["(设计态 / design) L5 学习层 / Learning &<br/>Optimization<br/>7阶段学习流水线 → 模块工厂 → 知识采集 →<br/>反馈闭环 产出：learning_feedback（策略优化建议）<br/>文件: （设计态，暂无代码引用）"]
    LL6["(设计态 / design) L6 自评估层 / Self Evaluation<br/>LLM 自评估(Judge+交叉验证) + 多模态金融推理 +<br/>VeNRA零幻觉锚定 产出：self_evaluation<br/>（决策质量评估）<br/>文件: （设计态，暂无代码引用）"]
    LL0 -->|triggering / 触发| LL1
    LL1 -.->|triggering / 触发| LL2A
    LL2A -.->|triggering / 触发| LL2B
    LL2B -.->|triggering / 触发| LL2C
    LL2C -.->|triggering / 触发| LL2D
    LL2D -.->|triggering / 触发| LL3
    LL3 -->|triggering / 触发| LL4
    LL4 -.->|triggering / 触发| LL5
    LL5 -.->|triggering / 触发| LL6
    N59 -.->|informing / 告知| N60
    N60 -.->|informing / 告知| N61
    N61 -.->|informing / 告知| N62
    N62 -.->|informing / 告知| N63
    N63 -.->|informing / 告知| N64
    N64 -.->|informing / 告知| N65
    N65 -.->|informing / 告知| N66
    N66 -.->|informing / 告知| N71
    N57 -.->|informing / 告知| N58
    N58 -.->|informing / 告知| N67
    N67 -.->|informing / 告知| N68
    N68 -.->|informing / 告知| N69
    N69 -.->|informing / 告知| N70
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class LL0,LL1,LL3,LL4 production
    class LL2A,LL2B,LL2C,LL2D,N59,N60,N61,N62,N63,N64,N65,N66,N71,N57,N58,N67,N68,N69,N70,LL5,LL6 design
```

### 运营态的图（仅 design_maturity=production 的模块和域内依赖）

> 仅展示已上线运行的决策节点（共 0 个），不含跨域外部节点。跨域依赖见下方跨域依赖章节。

> （无模块 / No modules）

### 设计态的图（仅 design_maturity=design 的模块和域内依赖）

> 仅展示蓝图阶段、代码未写的设计态决策节点（共 9 个），不含跨域外部节点。

> 共 6 层，0 边。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'clusterBkg': 'transparent', 'clusterBorder': 'transparent', 'fontSize': '14px'}}}%%
flowchart TD
    LL2A["(设计态 / design) L2A 信号层 / Signal Generation<br/>信号工厂 → 多策略投票 → 收益率条件密度预测 →<br/>Transformer/Mamba时序增强 → 共形预测<br/>产出：signal（Insight: direction/confidence<br/>/horizon）<br/>文件: （设计态，暂无代码引用）"]
    LL2B["(设计态 / design) L2B 主力行为层 / Main Force<br/>Behavior Analysis<br/>六阶段识别 + 自迭代推演 + 庄家专项 +<br/>群体博弈模拟 产出：main_force_signal<br/>（主力行为画像）<br/>文件: （设计态，暂无代码引用）"]
    LL2C["(设计态 / design) L2C 市场状态与大盘预测层 /<br/>Market State & Index Prediction<br/>3×3矩阵 + 2叠加态 + 三层大盘预测 +<br/>T+1次日8态走势预测 + 体制转换检测(HMM/变点)<br/>产出：market_state_prediction（大盘方向/波动率<br/>/体制判断）<br/>文件: （设计态，暂无代码引用）"]
    LL2D["(设计态 / design) L2D 知识图谱与因果推演层 /<br/>Knowledge Graph & Causal Inference<br/>六类知识图谱 → 事件影响链分析 → 因果传导推演 →<br/>GNN股票关系建模 → Causal ML 产出：causal_<br/>inference_result（因果推断结果）<br/>文件: （设计态，暂无代码引用）"]
    LL5["(设计态 / design) L5 学习层 / Learning &<br/>Optimization<br/>7阶段学习流水线 → 模块工厂 → 知识采集 →<br/>反馈闭环 产出：learning_feedback（策略优化建议）<br/>文件: （设计态，暂无代码引用）"]
    LL6["(设计态 / design) L6 自评估层 / Self Evaluation<br/>LLM 自评估(Judge+交叉验证) + 多模态金融推理 +<br/>VeNRA零幻觉锚定 产出：self_evaluation<br/>（决策质量评估）<br/>文件: （设计态，暂无代码引用）"]
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
| 59 | L3 | order / 订单节点 | 50ms SLA Fail-Closed 50ms SLA Fail-Closed | decision/ex_core/ex_03 | MOD-L05-001 | - | design / 设计 | planned / 已规划 |
| 60 | L3 | order / 订单节点 | Saga编排式事务 Saga Orchestrated Transaction | decision/ex_core/ex_04 | MOD-L05-001 | - | design / 设计 | planned / 已规划 |
| 61 | L3 | order / 订单节点 | 风控检查 Risk Check | decision/ex_core/ex_05 | MOD-L05-001 | - | design / 设计 | planned / 已规划 |
| 62 | L3 | order / 订单节点 | 信号确认 Signal Confirmation | decision/ex_core/ex_06 | MOD-L05-001 | - | design / 设计 | planned / 已规划 |
| 63 | L3 | order / 订单节点 | 下单提交 Order Submit | decision/ex_core/ex_07 | MOD-L05-001 | - | design / 设计 | planned / 已规划 |
| 64 | L3 | order / 订单节点 | 成交确认 Fill Confirmation | decision/ex_core/ex_08 | MOD-L05-001 | - | design / 设计 | planned / 已规划 |
| 65 | L3 | order / 订单节点 | 持仓更新 Position Update | decision/ex_core/ex_09 | MOD-L05-001 | - | design / 设计 | planned / 已规划 |
| 66 | L3 | order / 订单节点 | 报告生成 Report Generation | decision/ex_core/ex_10 | MOD-L05-001 | - | design / 设计 | planned / 已规划 |
| 71 | L3 | order / 订单节点 | 流动性螺旋3阶段 Liquidity Spiral 3-Phase | decision/ex_core/ex_15 | MOD-L05-001 | - | design / 设计 | planned / 已规划 |

## Edge 清单（域内）

| edge_id / 边ID | from / 起点 | to / 终点 | type / 类型 | condition / 条件 | track / 轨 |
|---------|-------|-----|------|-----------|-------|
| 76 | 59 | 60 | informing / 告知 | L3层内顺序流 | - |
| 77 | 60 | 61 | informing / 告知 | L3层内顺序流 | - |
| 78 | 61 | 62 | informing / 告知 | L3层内顺序流 | - |
| 79 | 62 | 63 | informing / 告知 | L3层内顺序流 | - |
| 80 | 63 | 64 | informing / 告知 | L3层内顺序流 | - |
| 81 | 64 | 65 | informing / 告知 | L3层内顺序流 | - |
| 82 | 65 | 66 | informing / 告知 | L3层内顺序流 | - |
| 83 | 66 | 71 | informing / 告知 | L3层内顺序流 | - |

## 跨域出边（Depends On）

| # | 本域节点 / from | → | 外部域-目标节点 / to | type / 类型 |
|:--:|---------|:--:|---------|---------|
| 1 | decision/ex_core/ex_15 | → | decision/ex_sor/ex_16 | informing / 告知 |
| 2 | decision/ex_core/ex_14 | → | decision/ex_sor/ex_18 | informing / 告知 |

## 跨域入边（Depended By）

| # | 外部域-源节点 / from | → | 本域节点 / to | type / 类型 |
|:--:|---------|:--:|---------|---------|
| 1 | decision/aut_core/ac_24 | → | decision/ex_core/ex_03 | informing / 告知 |
| 2 | decision/compliance/cmp_11 | → | decision/ex_core/ex_01 | informing / 告知 |

## 跨域依赖图（Cross-Domain Dependency Graph）

> 本域与 3 个外部域直接连接 / This domain directly connects to 3 external domain(s).

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'clusterBkg': 'transparent', 'clusterBorder': 'transparent', 'fontSize': '14px'}}}%%
flowchart TD
    SELF["(设计态 / design) 执行核心 / ex_core<br/>订单执行核心——SLA 保障、Saga<br/>事务、风控检查、下单/成交确认与持仓更新<br/>跨域节点 / cross-domain"]
    EXT_ex_sor["(设计态 / design) 执行排序 / ex_sor<br/>智能订单路由(SOR)——路由决策、通道熔断、Kill-Swit<br/>ch 与熔断器矩阵<br/>跨域节点 / cross-domain"]
    SELF -.->|出 2| EXT_ex_sor
    EXT_aut_core["(设计态 / design) 自主核心 / aut_core<br/>自主决策编排——权限守卫、自愈回滚、预算执行、健康<br/>监控、漂移检测、自动修复与 Agent 编排<br/>跨域节点 / cross-domain"]
    EXT_aut_core -.->|入 1| SELF
    EXT_compliance["(设计态 / design) compliance / compliance<br/>（域职责待补）<br/>跨域节点 / cross-domain"]
    EXT_compliance -.->|入 1| SELF
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class SELF design
    class EXT_ex_sor,EXT_aut_core,EXT_compliance external_design
```

