# Decision Flow · L2A Functional Domain sell（卖出）

> 生成时间: 2026-07-30T20:16:54
> 真源: `architecture_model/domain/decision_graph_model.yaml` → PostgreSQL `decision_*` 表（TRAE-061）
> 数据库: depgraph (PostgreSQL)
> 导航: [返回主索引 decision_index.md](decision_index.md) | 模型驱动轨 → L2A → sell

**所属轨**: 模型驱动轨（`model_driven`） | **所属层**: L2A | **功能域**: `sell`（卖出）

## 统计

- 设计态节点数: 19
- 域内边数: 18
- 跨域出边: 1（1 个外部域）
- 跨域入边: 0（0 个外部域）

## 设计态全景图

> 共 7 层，18 边。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    LL2A["L2A: 信号层<br/>design/planned<br/>信号工厂 → 多策略投票 → 收益率条件密度预测 → Tr…"]
    N1("sell_decision: 卖出决策域入口 Sell Decision Entry")
    LL2A --- N1
    N2("sell_decision: 止盈信号 Take-Profit Signal")
    LL2A --- N2
    N3("sell_decision: 止损信号 Stop-Loss Signal")
    LL2A --- N3
    N4("sell_decision: 移动止损 Trailing Stop")
    LL2A --- N4
    N5("sell_decision: 主力出货信号 Main Force Distribution Signal")
    LL2A --- N5
    N6("sell_decision: 量价背离卖出 Volume-Price Divergence Sell")
    LL2A --- N6
    N7("sell_decision: 突破关键位卖出 Key-Level Breakdown Sell")
    LL2A --- N7
    N8("sell_decision: Watch List 实时卖出 Watch List Realtime Sell")
    LL2A --- N8
    N9("sell_decision: Monitor List 定期扫描 Monitor List Periodic Scan")
    LL2A --- N9
    N10("sell_decision: 卖出信号融合仲裁 Sell Signal Fusion Arbiter")
    LL2A --- N10
    N11("sell_decision: 买卖冲突仲裁 Buy-Sell Conflict Arbiter")
    LL2A --- N11
    N12("sell_decision: 部分卖出vs全部清仓决策 Partial vs Full Sell Decision")
    LL2A --- N12
    N13("sell_decision: D-S证据理论融合 D-S Evidence Theory Fusion")
    LL2A --- N13
    N14("sell_decision: 做T决策协调 T-Trade Coordinator")
    LL2A --- N14
    N15("sell_decision: 黑天鹅强制卖出 Black Swan Forced Sell")
    LL2A --- N15
    N16("sell_decision: Gap开盘决策框架 Gap Opening Decision Framework")
    LL2A --- N16
    N17("sell_decision: 强制清仓信号 Forced Liquidation Signal")
    LL2A --- N17
    N18("sell_decision: 卖出降级模式 Sell Degradation Mode")
    LL2A --- N18
    N19("sell_decision: 卖出决策闭环优化 Sell Decision Closed-Loop")
    LL2A --- N19
    LL2B["L2B: 主力行为层<br/>design/planned<br/>六阶段识别 + 自迭代推演 + 庄家专项 + 群体博弈模拟…"]
    LL2C["L2C: 市场状态与大盘预测层<br/>design/planned<br/>3×3矩阵 + 2叠加态 + 三层大盘预测 + T+1次日…"]
    LL2D["L2D: 知识图谱与因果推演层<br/>design/planned<br/>六类知识图谱 → 事件影响链分析 → 因果传导推演 → G…"]
    LL3["L3: 策略组合层<br/>design/planned<br/>多策略信号合成 → 资本分配 → 元策略路由 → 组合构建…"]
    LL5["L5: 学习层<br/>design/planned<br/>7阶段学习流水线 → 模块工厂 → 知识采集 → 反馈闭环…"]
    LL6["L6: 自评估层<br/>design/planned<br/>LLM 自评估(Judge+交叉验证) + 多模态金融推理…"]
    LL2A -.->|triggering| LL2B
    LL2B -.->|triggering| LL2C
    LL2C -.->|triggering| LL2D
    LL2D -.->|triggering| LL3
    LL3 -.->|triggering| LL5
    LL5 -.->|triggering| LL6
    N1 -->|informing| N2
    N2 -->|informing| N3
    N3 -->|informing| N4
    N4 -->|informing| N5
    N5 -->|informing| N6
    N6 -->|informing| N7
    N7 -->|informing| N8
    N8 -->|informing| N9
    N9 -->|informing| N10
    N10 -->|informing| N11
    N11 -->|informing| N12
    N12 -->|informing| N13
    N13 -->|informing| N14
    N14 -->|informing| N15
    N15 -->|informing| N16
    N16 -->|informing| N17
    N17 -->|informing| N18
    N18 -->|informing| N19
```

## Node 清单

| node_id | layer | type | name | path | module_id | 代码引用 | 成熟度 | build_status |
|---------|-------|------|------|------|-----------|----------|--------|--------------|
| 1 | L2A | sell_decision | 卖出决策域入口 Sell Decision Entry | decision/sell/sell_00 | - | - | design | planned |
| 2 | L2A | sell_decision | 止盈信号 Take-Profit Signal | decision/sell/sell_01 | - | - | design | planned |
| 3 | L2A | sell_decision | 止损信号 Stop-Loss Signal | decision/sell/sell_02 | - | - | design | planned |
| 4 | L2A | sell_decision | 移动止损 Trailing Stop | decision/sell/sell_03 | - | - | design | planned |
| 5 | L2A | sell_decision | 主力出货信号 Main Force Distribution Signal | decision/sell/sell_04 | - | - | design | planned |
| 6 | L2A | sell_decision | 量价背离卖出 Volume-Price Divergence Sell | decision/sell/sell_05 | - | - | design | planned |
| 7 | L2A | sell_decision | 突破关键位卖出 Key-Level Breakdown Sell | decision/sell/sell_06 | - | - | design | planned |
| 8 | L2A | sell_decision | Watch List 实时卖出 Watch List Realtime Sell | decision/sell/sell_07 | - | - | design | planned |
| 9 | L2A | sell_decision | Monitor List 定期扫描 Monitor List Periodic Scan | decision/sell/sell_08 | - | - | design | planned |
| 10 | L2A | sell_decision | 卖出信号融合仲裁 Sell Signal Fusion Arbiter | decision/sell/sell_09 | - | - | design | planned |
| 11 | L2A | sell_decision | 买卖冲突仲裁 Buy-Sell Conflict Arbiter | decision/sell/sell_10 | - | - | design | planned |
| 12 | L2A | sell_decision | 部分卖出vs全部清仓决策 Partial vs Full Sell Decision | decision/sell/sell_11 | - | - | design | planned |
| 13 | L2A | sell_decision | D-S证据理论融合 D-S Evidence Theory Fusion | decision/sell/sell_12 | - | - | design | planned |
| 14 | L2A | sell_decision | 做T决策协调 T-Trade Coordinator | decision/sell/sell_13 | - | - | design | planned |
| 15 | L2A | sell_decision | 黑天鹅强制卖出 Black Swan Forced Sell | decision/sell/sell_14 | - | - | design | planned |
| 16 | L2A | sell_decision | Gap开盘决策框架 Gap Opening Decision Framework | decision/sell/sell_15 | - | - | design | planned |
| 17 | L2A | sell_decision | 强制清仓信号 Forced Liquidation Signal | decision/sell/sell_16 | - | - | design | planned |
| 18 | L2A | sell_decision | 卖出降级模式 Sell Degradation Mode | decision/sell/sell_17 | - | - | design | planned |
| 19 | L2A | sell_decision | 卖出决策闭环优化 Sell Decision Closed-Loop | decision/sell/sell_18 | - | - | design | planned |

## Edge 清单（域内）

| edge_id | from | to | type | condition | track |
|---------|-------|-----|------|-----------|-------|
| 19 | 1 | 2 | informing | L2A层内顺序流 | - |
| 20 | 2 | 3 | informing | L2A层内顺序流 | - |
| 21 | 3 | 4 | informing | L2A层内顺序流 | - |
| 22 | 4 | 5 | informing | L2A层内顺序流 | - |
| 23 | 5 | 6 | informing | L2A层内顺序流 | - |
| 24 | 6 | 7 | informing | L2A层内顺序流 | - |
| 25 | 7 | 8 | informing | L2A层内顺序流 | - |
| 26 | 8 | 9 | informing | L2A层内顺序流 | - |
| 27 | 9 | 10 | informing | L2A层内顺序流 | - |
| 28 | 10 | 11 | informing | L2A层内顺序流 | - |
| 29 | 11 | 12 | informing | L2A层内顺序流 | - |
| 30 | 12 | 13 | informing | L2A层内顺序流 | - |
| 31 | 13 | 14 | informing | L2A层内顺序流 | - |
| 32 | 14 | 15 | informing | L2A层内顺序流 | - |
| 33 | 15 | 16 | informing | L2A层内顺序流 | - |
| 34 | 16 | 17 | informing | L2A层内顺序流 | - |
| 35 | 17 | 18 | informing | L2A层内顺序流 | - |
| 36 | 18 | 19 | informing | L2A层内顺序流 | - |

## 跨域出边（Depends On）

| # | 本域节点 | → | 外部域-目标节点 | type |
|:--:|---------|:--:|---------|---------|
| 1 | decision/sell/sell_18 | → | decision/signal/sg_01 | informing |

## 跨域入边（Depended By）

> （无跨域入边）

## 跨域依赖图（Cross-Domain Dependency Graph）

> 本域与 1 个外部域直接连接 / This domain directly connects to 1 external domain(s).

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart LR
    SELF["sell（卖出）"]
    EXT_signal["signal（信号）"]
    SELF -->|出 1| EXT_signal
```

