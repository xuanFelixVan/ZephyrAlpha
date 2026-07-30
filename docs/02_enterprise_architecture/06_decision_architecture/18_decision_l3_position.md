# Decision Flow · L3 Functional Domain position（持仓）

> 生成时间: 2026-07-30T19:59:19
> 真源: `architecture_model/domain/decision_graph_model.yaml` → PostgreSQL `decision_*` 表（TRAE-061）
> 数据库: depgraph (PostgreSQL)
> 导航: [返回主索引 decision_index.md](decision_index.md) | 模型驱动轨 → L3 → position

**所属轨**: 模型驱动轨（`model_driven`） | **所属层**: L3 | **功能域**: `position`（持仓）

## 统计

- 设计态节点数: 19
- 域内边数: 18
- 跨域出边: 1（1 个外部域）
- 跨域入边: 1（1 个外部域）

## 设计态全景图

> 共 7 层，18 边。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    LL2A["L2A: 信号层<br/>design/planned"]
    LL2B["L2B: 主力行为层<br/>design/planned"]
    LL2C["L2C: 市场状态与大盘预测层<br/>design/planned"]
    LL2D["L2D: 知识图谱与因果推演层<br/>design/planned"]
    LL3["L3: 策略组合层<br/>design/planned"]
    N38("portfolio_target: 仓位唯一裁决中心 C-047 Position Sole Arbiter")
    LL3 --- N38
    N39("portfolio_target: 持仓状态机 Position State Machine")
    LL3 --- N39
    N40("portfolio_target: 仓位漂移监控 Position Drift Monitor")
    LL3 --- N40
    N41("portfolio_target: Kelly仓位决策 Kelly Position Decision")
    LL3 --- N41
    N42("portfolio_target: 风险配额 Risk Quota")
    LL3 --- N42
    N43("portfolio_target: 11种市场状态→仓位上限 Market State Position Cap")
    LL3 --- N43
    N44("portfolio_target: 组合层决策 Portfolio Layer Decision")
    LL3 --- N44
    N45("portfolio_target: 策略层决策 Strategy Layer Decision")
    LL3 --- N45
    N46("portfolio_target: 标层决策 Instrument Layer Decision")
    LL3 --- N46
    N47("portfolio_target: 动态层决策 Dynamic Layer Decision")
    LL3 --- N47
    N48("portfolio_target: 再平衡触发 Rebalance Trigger")
    LL3 --- N48
    N49("portfolio_target: 仓位上限硬约束 Position Cap Hard Constraint")
    LL3 --- N49
    N50("portfolio_target: REDUCING→EXITING状态转换 REDUCING to EXITING")
    LL3 --- N50
    N51("portfolio_target: 风险预算→Kelly决策 Risk Budget to Kelly")
    LL3 --- N51
    N52("portfolio_target: 半Kelly硬上限 Half-Kelly Hard Cap")
    LL3 --- N52
    N53("portfolio_target: 仓位降级 Position Degradation")
    LL3 --- N53
    N54("portfolio_target: 持仓状态→卖出阈值 Position State to Sell Threshold")
    LL3 --- N54
    N55("portfolio_target: 仓位四轨决策 Position Four-Track Decision")
    LL3 --- N55
    N56("portfolio_target: 仓位裁决→执行 Position Arbitration to Execution")
    LL3 --- N56
    LL5["L5: 学习层<br/>design/planned"]
    LL6["L6: 自评估层<br/>design/planned"]
    LL2A -.->|triggering| LL2B
    LL2B -.->|triggering| LL2C
    LL2C -.->|triggering| LL2D
    LL2D -.->|triggering| LL3
    LL3 -.->|triggering| LL5
    LL5 -.->|triggering| LL6
    N38 -->|informing| N39
    N39 -->|informing| N40
    N40 -->|informing| N41
    N41 -->|informing| N42
    N42 -->|informing| N43
    N43 -->|informing| N44
    N44 -->|informing| N45
    N45 -->|informing| N46
    N46 -->|informing| N47
    N47 -->|informing| N48
    N48 -->|informing| N49
    N49 -->|informing| N50
    N50 -->|informing| N51
    N51 -->|informing| N52
    N52 -->|informing| N53
    N53 -->|informing| N54
    N54 -->|informing| N55
    N55 -->|informing| N56
```

## Node 清单

| node_id | layer | type | name | path | module_id | 代码引用 | 成熟度 | build_status |
|---------|-------|------|------|------|-----------|----------|--------|--------------|
| 38 | L3 | portfolio_target | 仓位唯一裁决中心 C-047 Position Sole Arbiter | decision/position/pos_01 | MOD-L05-001 | - | design | planned |
| 39 | L3 | portfolio_target | 持仓状态机 Position State Machine | decision/position/pos_02 | MOD-L05-001 | - | design | planned |
| 40 | L3 | portfolio_target | 仓位漂移监控 Position Drift Monitor | decision/position/pos_03 | MOD-L05-001 | - | design | planned |
| 41 | L3 | portfolio_target | Kelly仓位决策 Kelly Position Decision | decision/position/pos_04 | MOD-L05-001 | - | design | planned |
| 42 | L3 | portfolio_target | 风险配额 Risk Quota | decision/position/pos_05 | MOD-L05-001 | - | design | planned |
| 43 | L3 | portfolio_target | 11种市场状态→仓位上限 Market State Position Cap | decision/position/pos_06 | MOD-L05-001 | - | design | planned |
| 44 | L3 | portfolio_target | 组合层决策 Portfolio Layer Decision | decision/position/pos_07 | MOD-L05-001 | - | design | planned |
| 45 | L3 | portfolio_target | 策略层决策 Strategy Layer Decision | decision/position/pos_08 | MOD-L05-001 | - | design | planned |
| 46 | L3 | portfolio_target | 标层决策 Instrument Layer Decision | decision/position/pos_09 | MOD-L05-001 | - | design | planned |
| 47 | L3 | portfolio_target | 动态层决策 Dynamic Layer Decision | decision/position/pos_10 | MOD-L05-001 | - | design | planned |
| 48 | L3 | portfolio_target | 再平衡触发 Rebalance Trigger | decision/position/pos_11 | MOD-L05-001 | - | design | planned |
| 49 | L3 | portfolio_target | 仓位上限硬约束 Position Cap Hard Constraint | decision/position/pos_12 | MOD-L05-001 | - | design | planned |
| 50 | L3 | portfolio_target | REDUCING→EXITING状态转换 REDUCING to EXITING | decision/position/pos_13 | MOD-L05-001 | - | design | planned |
| 51 | L3 | portfolio_target | 风险预算→Kelly决策 Risk Budget to Kelly | decision/position/pos_14 | MOD-L05-001 | - | design | planned |
| 52 | L3 | portfolio_target | 半Kelly硬上限 Half-Kelly Hard Cap | decision/position/pos_15 | MOD-L05-001 | - | design | planned |
| 53 | L3 | portfolio_target | 仓位降级 Position Degradation | decision/position/pos_16 | MOD-L05-001 | - | design | planned |
| 54 | L3 | portfolio_target | 持仓状态→卖出阈值 Position State to Sell Threshold | decision/position/pos_17 | MOD-L05-001 | - | design | planned |
| 55 | L3 | portfolio_target | 仓位四轨决策 Position Four-Track Decision | decision/position/pos_18 | MOD-L05-001 | - | design | planned |
| 56 | L3 | portfolio_target | 仓位裁决→执行 Position Arbitration to Execution | decision/position/pos_19 | MOD-L05-001 | - | design | planned |

## Edge 清单（域内）

| edge_id | from | to | type | condition | track |
|---------|-------|-----|------|-----------|-------|
| 108 | 38 | 39 | informing | L3层内顺序流 | - |
| 109 | 39 | 40 | informing | L3层内顺序流 | - |
| 110 | 40 | 41 | informing | L3层内顺序流 | - |
| 111 | 41 | 42 | informing | L3层内顺序流 | - |
| 112 | 42 | 43 | informing | L3层内顺序流 | - |
| 113 | 43 | 44 | informing | L3层内顺序流 | - |
| 114 | 44 | 45 | informing | L3层内顺序流 | - |
| 115 | 45 | 46 | informing | L3层内顺序流 | - |
| 116 | 46 | 47 | informing | L3层内顺序流 | - |
| 117 | 47 | 48 | informing | L3层内顺序流 | - |
| 118 | 48 | 49 | informing | L3层内顺序流 | - |
| 119 | 49 | 50 | informing | L3层内顺序流 | - |
| 120 | 50 | 51 | informing | L3层内顺序流 | - |
| 121 | 51 | 52 | informing | L3层内顺序流 | - |
| 122 | 52 | 53 | informing | L3层内顺序流 | - |
| 123 | 53 | 54 | informing | L3层内顺序流 | - |
| 124 | 54 | 55 | informing | L3层内顺序流 | - |
| 125 | 55 | 56 | informing | L3层内顺序流 | - |

## 跨域出边（Depends On）

| # | 本域节点 | → | 外部域-目标节点 | type |
|:--:|---------|:--:|---------|---------|
| 1 | decision/position/pos_19 | → | decision/trading/trd_01 | informing |

## 跨域入边（Depended By）

| # | 外部域-源节点 | → | 本域节点 | type |
|:--:|---------|:--:|---------|---------|
| 1 | decision/pf_core/pc_12 | → | decision/position/pos_01 | informing |

## 跨域依赖图（Cross-Domain Dependency Graph）

> 本域与 2 个外部域直接连接 / This domain directly connects to 2 external domain(s).

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart LR
    SELF["position（持仓）"]
    EXT_trading["trading（交易）"]
    SELF -->|出 1| EXT_trading
    EXT_pf_core["pf_core（组合核心）"]
    EXT_pf_core -->|入 1| SELF
```

