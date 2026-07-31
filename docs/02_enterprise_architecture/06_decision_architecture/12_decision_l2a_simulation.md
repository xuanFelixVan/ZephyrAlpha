# Decision Flow · L2A Functional Domain simulation（仿真）

> 生成时间: 2026-07-30T22:18:45
> 真源: `architecture_model/domain/decision_graph_model.yaml` → PostgreSQL `decision_*` 表（TRAE-061）
> 数据库: depgraph (PostgreSQL)
> 导航: [返回主索引 decision_index.md](decision_index.md) | 模型驱动轨 → L2A → simulation

**所属轨**: 模型驱动轨（`model_driven`） | **所属层**: L2A | **功能域**: `simulation`（仿真）

> **域职责 / Responsibility**: 市场/策略/风控仿真、压力测试、场景生成与历史重放

## 统计

- 设计态节点数: 15
- 域内边数: 14
- 跨域出边: 1（1 个外部域）
- 跨域入边: 1（1 个外部域）

## 设计态全景图

> 共 6 层，14 边。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    LL2A["L2A: 信号层<br/>design/planned<br/>信号工厂 → 多策略投票 → 收益率条件密度预测 → Tr…"]
    N141("signal: 市场仿真器 Market Simulator")
    LL2A --- N141
    N142("signal: 策略仿真器 Strategy Simulator")
    LL2A --- N142
    N143("signal: 风控仿真器 Risk Simulator")
    LL2A --- N143
    N144("signal: 压力测试引擎 Stress Test Engine")
    LL2A --- N144
    N145("signal: 场景生成器 Scenario Generator")
    LL2A --- N145
    N146("signal: 历史重放引擎 History Replay Engine")
    LL2A --- N146
    N147("signal: 极端事件仿真 Extreme Event Simulator")
    LL2A --- N147
    N148("signal: 依赖图数字孪生 Dependency Graph Digital Twin")
    LL2A --- N148
    N149("signal: 混沌实验自动生成 Chaos Experiment Auto-Generator")
    LL2A --- N149
    N150("signal: 回测过拟合检测器 Backtest Overfitting Detector")
    LL2A --- N150
    N151("signal: Walk-Forward分析器 Walk-Forward Analyzer")
    LL2A --- N151
    N152("signal: 参数鲁棒性测试器 Parameter Robustness Tester")
    LL2A --- N152
    N153("signal: 验证自动化流水线 Validation Automation Pipeline")
    LL2A --- N153
    N154("signal: 自动化过拟合门禁 Automated Overfitting Detector Gate")
    LL2A --- N154
    N155("signal: 3阶段决策门控 IS→WFA→OOS 3-Stage Decision Gate")
    LL2A --- N155
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
    N141 -->|informing / 告知| N142
    N142 -->|informing / 告知| N143
    N143 -->|informing / 告知| N144
    N144 -->|informing / 告知| N145
    N145 -->|informing / 告知| N146
    N146 -->|informing / 告知| N147
    N147 -->|informing / 告知| N148
    N148 -->|informing / 告知| N149
    N149 -->|informing / 告知| N150
    N150 -->|informing / 告知| N151
    N151 -->|informing / 告知| N152
    N152 -->|informing / 告知| N153
    N153 -->|informing / 告知| N154
    N154 -->|informing / 告知| N155
```

## Node 清单

| node_id / 节点ID | layer / 层 | type / 类型 | name / 名称 | path / 路径 | module_id / 模块 | 代码引用 / ref | maturity / 成熟度 | build_status / 构建状态 |
|---------|-------|------|------|------|-----------|----------|--------|--------------|
| 141 | L2A | signal / 信号节点 | 市场仿真器 Market Simulator | decision/simulation/sim_01 | - | - | design / 设计 | planned / 已规划 |
| 142 | L2A | signal / 信号节点 | 策略仿真器 Strategy Simulator | decision/simulation/sim_02 | - | - | design / 设计 | planned / 已规划 |
| 143 | L2A | signal / 信号节点 | 风控仿真器 Risk Simulator | decision/simulation/sim_03 | - | - | design / 设计 | planned / 已规划 |
| 144 | L2A | signal / 信号节点 | 压力测试引擎 Stress Test Engine | decision/simulation/sim_04 | - | - | design / 设计 | planned / 已规划 |
| 145 | L2A | signal / 信号节点 | 场景生成器 Scenario Generator | decision/simulation/sim_05 | - | - | design / 设计 | planned / 已规划 |
| 146 | L2A | signal / 信号节点 | 历史重放引擎 History Replay Engine | decision/simulation/sim_07 | - | - | design / 设计 | planned / 已规划 |
| 147 | L2A | signal / 信号节点 | 极端事件仿真 Extreme Event Simulator | decision/simulation/sim_10 | - | - | design / 设计 | planned / 已规划 |
| 148 | L2A | signal / 信号节点 | 依赖图数字孪生 Dependency Graph Digital Twin | decision/simulation/sim_13 | - | - | design / 设计 | planned / 已规划 |
| 149 | L2A | signal / 信号节点 | 混沌实验自动生成 Chaos Experiment Auto-Generator | decision/simulation/sim_15 | - | - | design / 设计 | planned / 已规划 |
| 150 | L2A | signal / 信号节点 | 回测过拟合检测器 Backtest Overfitting Detector | decision/simulation/sim_18 | - | - | design / 设计 | planned / 已规划 |
| 151 | L2A | signal / 信号节点 | Walk-Forward分析器 Walk-Forward Analyzer | decision/simulation/sim_19 | - | - | design / 设计 | planned / 已规划 |
| 152 | L2A | signal / 信号节点 | 参数鲁棒性测试器 Parameter Robustness Tester | decision/simulation/sim_21 | - | - | design / 设计 | planned / 已规划 |
| 153 | L2A | signal / 信号节点 | 验证自动化流水线 Validation Automation Pipeline | decision/simulation/sim_33 | - | - | design / 设计 | planned / 已规划 |
| 154 | L2A | signal / 信号节点 | 自动化过拟合门禁 Automated Overfitting Detector Gate | decision/simulation/sim_56 | - | - | design / 设计 | planned / 已规划 |
| 155 | L2A | signal / 信号节点 | 3阶段决策门控 IS→WFA→OOS 3-Stage Decision Gate | decision/simulation/sim_g1 | - | - | design / 设计 | planned / 已规划 |

## Edge 清单（域内）

| edge_id / 边ID | from / 起点 | to / 终点 | type / 类型 | condition / 条件 | track / 轨 |
|---------|-------|-----|------|-----------|-------|
| 51 | 141 | 142 | informing / 告知 | L2A层内顺序流 | - |
| 52 | 142 | 143 | informing / 告知 | L2A层内顺序流 | - |
| 53 | 143 | 144 | informing / 告知 | L2A层内顺序流 | - |
| 54 | 144 | 145 | informing / 告知 | L2A层内顺序流 | - |
| 55 | 145 | 146 | informing / 告知 | L2A层内顺序流 | - |
| 56 | 146 | 147 | informing / 告知 | L2A层内顺序流 | - |
| 57 | 147 | 148 | informing / 告知 | L2A层内顺序流 | - |
| 58 | 148 | 149 | informing / 告知 | L2A层内顺序流 | - |
| 59 | 149 | 150 | informing / 告知 | L2A层内顺序流 | - |
| 60 | 150 | 151 | informing / 告知 | L2A层内顺序流 | - |
| 61 | 151 | 152 | informing / 告知 | L2A层内顺序流 | - |
| 62 | 152 | 153 | informing / 告知 | L2A层内顺序流 | - |
| 63 | 153 | 154 | informing / 告知 | L2A层内顺序流 | - |
| 64 | 154 | 155 | informing / 告知 | L2A层内顺序流 | - |

## 跨域出边（Depends On）

| # | 本域节点 / from | → | 外部域-目标节点 / to | type / 类型 |
|:--:|---------|:--:|---------|---------|
| 1 | decision/simulation/sim_g1 | → | decision/aut_core/ac_01 | informing / 告知 |

## 跨域入边（Depended By）

| # | 外部域-源节点 / from | → | 本域节点 / to | type / 类型 |
|:--:|---------|:--:|---------|---------|
| 1 | decision/signal/sg_13 | → | decision/simulation/sim_01 | informing / 告知 |

## 跨域依赖图（Cross-Domain Dependency Graph）

> 本域与 2 个外部域直接连接 / This domain directly connects to 2 external domain(s).

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart LR
    SELF["simulation（仿真）"]
    EXT_aut_core["aut_core（自主核心）"]
    SELF -->|出 1| EXT_aut_core
    EXT_signal["signal（信号）"]
    EXT_signal -->|入 1| SELF
```

