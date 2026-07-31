# Decision Flow · L3 Functional Domain position（持仓）

> 生成时间: 2026-07-30T22:18:45
> 真源: `architecture_model/domain/decision_graph_model.yaml` → PostgreSQL `decision_*` 表（TRAE-061）
> 数据库: depgraph (PostgreSQL)
> 导航: [返回主索引 decision_index.md](decision_index.md) | 模型驱动轨 → L3 → position

**所属轨**: 模型驱动轨（`model_driven`） | **所属层**: L3 | **功能域**: `position`（持仓）

> **域职责 / Responsibility**: 持仓管理——仓位唯一裁决、状态机、漂移监控、Kelly 决策与市场状态仓位上限

## 统计

- 设计态节点数: 19
- 域内边数: 18
- 跨域出边: 1（1 个外部域）
- 跨域入边: 1（1 个外部域）

## 设计态全景图

> 共 6 层，0 边。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    LL2A["L2A: 信号层<br/>design/planned<br/>信号工厂 → 多策略投票 → 收益率条件密度预测 → Tr…"]
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
```

## Node 清单

| node_id / 节点ID | layer / 层 | type / 类型 | name / 名称 | path / 路径 | module_id / 模块 | 代码引用 / ref | maturity / 成熟度 | build_status / 构建状态 |
|---------|-------|------|------|------|-----------|----------|--------|--------------|
| 38 | L3 | portfolio_target / 组合目标节点 | 仓位唯一裁决中心 C-047 Position Sole Arbiter | decision/position/pos_01 | MOD-L05-001 | - | design / 设计 | planned / 已规划 |
| 39 | L3 | portfolio_target / 组合目标节点 | 持仓状态机 Position State Machine | decision/position/pos_02 | MOD-L05-001 | - | design / 设计 | planned / 已规划 |
| 40 | L3 | portfolio_target / 组合目标节点 | 仓位漂移监控 Position Drift Monitor | decision/position/pos_03 | MOD-L05-001 | - | design / 设计 | planned / 已规划 |
| 41 | L3 | portfolio_target / 组合目标节点 | Kelly仓位决策 Kelly Position Decision | decision/position/pos_04 | MOD-L05-001 | - | design / 设计 | planned / 已规划 |
| 42 | L3 | portfolio_target / 组合目标节点 | 风险配额 Risk Quota | decision/position/pos_05 | MOD-L05-001 | - | design / 设计 | planned / 已规划 |
| 43 | L3 | portfolio_target / 组合目标节点 | 11种市场状态→仓位上限 Market State Position Cap | decision/position/pos_06 | MOD-L05-001 | - | design / 设计 | planned / 已规划 |
| 44 | L3 | portfolio_target / 组合目标节点 | 组合层决策 Portfolio Layer Decision | decision/position/pos_07 | MOD-L05-001 | - | design / 设计 | planned / 已规划 |
| 45 | L3 | portfolio_target / 组合目标节点 | 策略层决策 Strategy Layer Decision | decision/position/pos_08 | MOD-L05-001 | - | design / 设计 | planned / 已规划 |
| 46 | L3 | portfolio_target / 组合目标节点 | 标层决策 Instrument Layer Decision | decision/position/pos_09 | MOD-L05-001 | - | design / 设计 | planned / 已规划 |
| 47 | L3 | portfolio_target / 组合目标节点 | 动态层决策 Dynamic Layer Decision | decision/position/pos_10 | MOD-L05-001 | - | design / 设计 | planned / 已规划 |
| 48 | L3 | portfolio_target / 组合目标节点 | 再平衡触发 Rebalance Trigger | decision/position/pos_11 | MOD-L05-001 | - | design / 设计 | planned / 已规划 |
| 49 | L3 | portfolio_target / 组合目标节点 | 仓位上限硬约束 Position Cap Hard Constraint | decision/position/pos_12 | MOD-L05-001 | - | design / 设计 | planned / 已规划 |
| 50 | L3 | portfolio_target / 组合目标节点 | REDUCING→EXITING状态转换 REDUCING to EXITING | decision/position/pos_13 | MOD-L05-001 | - | design / 设计 | planned / 已规划 |
| 51 | L3 | portfolio_target / 组合目标节点 | 风险预算→Kelly决策 Risk Budget to Kelly | decision/position/pos_14 | MOD-L05-001 | - | design / 设计 | planned / 已规划 |
| 52 | L3 | portfolio_target / 组合目标节点 | 半Kelly硬上限 Half-Kelly Hard Cap | decision/position/pos_15 | MOD-L05-001 | - | design / 设计 | planned / 已规划 |
| 53 | L3 | portfolio_target / 组合目标节点 | 仓位降级 Position Degradation | decision/position/pos_16 | MOD-L05-001 | - | design / 设计 | planned / 已规划 |
| 54 | L3 | portfolio_target / 组合目标节点 | 持仓状态→卖出阈值 Position State to Sell Threshold | decision/position/pos_17 | MOD-L05-001 | - | design / 设计 | planned / 已规划 |
| 55 | L3 | portfolio_target / 组合目标节点 | 仓位四轨决策 Position Four-Track Decision | decision/position/pos_18 | MOD-L05-001 | - | design / 设计 | planned / 已规划 |
| 56 | L3 | portfolio_target / 组合目标节点 | 仓位裁决→执行 Position Arbitration to Execution | decision/position/pos_19 | MOD-L05-001 | - | design / 设计 | planned / 已规划 |

## Edge 清单（域内）

| edge_id / 边ID | from / 起点 | to / 终点 | type / 类型 | condition / 条件 | track / 轨 |
|---------|-------|-----|------|-----------|-------|
| 108 | 38 | 39 | informing / 告知 | L3层内顺序流 | - |
| 109 | 39 | 40 | informing / 告知 | L3层内顺序流 | - |
| 110 | 40 | 41 | informing / 告知 | L3层内顺序流 | - |
| 111 | 41 | 42 | informing / 告知 | L3层内顺序流 | - |
| 112 | 42 | 43 | informing / 告知 | L3层内顺序流 | - |
| 113 | 43 | 44 | informing / 告知 | L3层内顺序流 | - |
| 114 | 44 | 45 | informing / 告知 | L3层内顺序流 | - |
| 115 | 45 | 46 | informing / 告知 | L3层内顺序流 | - |
| 116 | 46 | 47 | informing / 告知 | L3层内顺序流 | - |
| 117 | 47 | 48 | informing / 告知 | L3层内顺序流 | - |
| 118 | 48 | 49 | informing / 告知 | L3层内顺序流 | - |
| 119 | 49 | 50 | informing / 告知 | L3层内顺序流 | - |
| 120 | 50 | 51 | informing / 告知 | L3层内顺序流 | - |
| 121 | 51 | 52 | informing / 告知 | L3层内顺序流 | - |
| 122 | 52 | 53 | informing / 告知 | L3层内顺序流 | - |
| 123 | 53 | 54 | informing / 告知 | L3层内顺序流 | - |
| 124 | 54 | 55 | informing / 告知 | L3层内顺序流 | - |
| 125 | 55 | 56 | informing / 告知 | L3层内顺序流 | - |

## 跨域出边（Depends On）

| # | 本域节点 / from | → | 外部域-目标节点 / to | type / 类型 |
|:--:|---------|:--:|---------|---------|
| 1 | decision/position/pos_19 | → | decision/trading/trd_01 | informing / 告知 |

## 跨域入边（Depended By）

| # | 外部域-源节点 / from | → | 本域节点 / to | type / 类型 |
|:--:|---------|:--:|---------|---------|
| 1 | decision/pf_core/pc_12 | → | decision/position/pos_01 | informing / 告知 |

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

