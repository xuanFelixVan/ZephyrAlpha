# Decision Flow · L2A Functional Domain sell（卖出）

> 生成时间: 2026-07-30T22:18:45
> 真源: `architecture_model/domain/decision_graph_model.yaml` → PostgreSQL `decision_*` 表（TRAE-061）
> 数据库: depgraph (PostgreSQL)
> 导航: [返回主索引 decision_index.md](decision_index.md) | 模型驱动轨 → L2A → sell

**所属轨**: 模型驱动轨（`model_driven`） | **所属层**: L2A | **功能域**: `sell`（卖出）

> **域职责 / Responsibility**: 卖出信号生成（止盈/止损/移动止损/主力出货/量价背离/突破关键位）

## 统计

- 设计态节点数: 19
- 域内边数: 18
- 跨域出边: 1（1 个外部域）
- 跨域入边: 0（0 个外部域）

## 设计态全景图

> 共 6 层，18 边。

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
    LL5["L5: 学习层<br/>design/planned<br/>7阶段学习流水线 → 模块工厂 → 知识采集 → 反馈闭环…"]
    LL6["L6: 自评估层<br/>design/planned<br/>LLM 自评估(Judge+交叉验证) + 多模态金融推理…"]
    LL2A -.->|triggering / 触发| LL2B
    LL2B -.->|triggering / 触发| LL2C
    LL2C -.->|triggering / 触发| LL2D
    LL2D -.->|triggering / 触发| LL5
    LL5 -.->|triggering / 触发| LL6
    N1 -->|informing / 告知| N2
    N2 -->|informing / 告知| N3
    N3 -->|informing / 告知| N4
    N4 -->|informing / 告知| N5
    N5 -->|informing / 告知| N6
    N6 -->|informing / 告知| N7
    N7 -->|informing / 告知| N8
    N8 -->|informing / 告知| N9
    N9 -->|informing / 告知| N10
    N10 -->|informing / 告知| N11
    N11 -->|informing / 告知| N12
    N12 -->|informing / 告知| N13
    N13 -->|informing / 告知| N14
    N14 -->|informing / 告知| N15
    N15 -->|informing / 告知| N16
    N16 -->|informing / 告知| N17
    N17 -->|informing / 告知| N18
    N18 -->|informing / 告知| N19
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
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart LR
    SELF["sell（卖出）"]
    EXT_signal["signal（信号）"]
    SELF -->|出 1| EXT_signal
```

