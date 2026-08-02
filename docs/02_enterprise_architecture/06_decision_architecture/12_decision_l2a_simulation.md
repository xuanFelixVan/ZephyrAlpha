---
doc_type: architecture_view
title: simulation（仿真）决策流图
version: "1.0"
status: active
date: 2026-08-01
owner: auto-generator
ttl: permanent
---

# Decision Flow · L2A Functional Domain simulation（仿真）

> 生成时间: 2026-08-01T22:45:17
> 真源: `architecture_model/domain/decision_graph_model.yaml` → PostgreSQL `decision_*` 表（TRAE-061）
> 数据库: depgraph (PostgreSQL)
> 导航: [返回主索引 decision_index.md](decision_index.md) | 模型驱动轨 → L2A → simulation

> **[可缩放 HTML 版 / Zoomable HTML](http://localhost:8765/docs/02_enterprise_architecture/06_decision_architecture/_zoomable_html/12_decision_l2a_simulation.html)** — Ctrl+滚轮缩放 ｜ 双击重置 ｜ Ctrl+Shift+D 切换拖动/选择模式

**所属轨**: 模型驱动轨（`model_driven`） | **所属层**: L2A | **功能域**: `simulation`（仿真）

> **域职责 / Responsibility**: 市场/策略/风控仿真、压力测试、场景生成与历史重放

## 统计

- 决策节点数（全部）: 15
- 运营态节点数（production）: 0
- 设计态节点数（design）: 15
- 域内边数: 14
- 跨域出边: 1（1 个外部域）
- 跨域入边: 1（1 个外部域）

## 域内依赖图 / Internal Dependency Diagram

> **图例说明 / Legend**：
> - 🟦 **蓝色 = 运营态模块**（production，已上线运行）
> - 🟧 **橙色虚线 = 设计态模块**（design，蓝图阶段，代码未写）
> - **实线箭头 `-->` = 运营态依赖**（两端都 production）
> - **虚线箭头 `-.->` = 非运营态依赖**（含 design / 混合）

### 全景图（全部模块，颜色区分运营态/设计态）

> 展示全部 15 个决策节点（运营态 0 + 设计态 15），含跨域依赖外部节点。

> 共 10 层，14 边。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'clusterBkg': 'transparent', 'clusterBorder': 'transparent', 'fontSize': '14px'}}}%%
flowchart TD
    LL0["(生产态 / production) L0 数据接入与预处理层 /<br/>Data Ingestion & Preprocessing<br/>miniQMT + iFind + tushare + 另类数据源 →<br/>事件总线 → 分层时序存储 产出：tick_data / ohlc_<br/>bar / factor_input_data<br/>文件: MOD-MKT_DATA"]
    LL1["(生产态 / production) L1 因子计算层 / Factor<br/>Calculation<br/>因子工厂全生命周期管理 → 盘前全量<br/>/盘中增量双模计算 → 因子池 产出：factor_value<br/>（带 PIT 合规标记）<br/>文件: MOD-L02-001"]
    LL2A["(设计态 / design) L2A 信号层 / Signal Generation<br/>信号工厂 → 多策略投票 → 收益率条件密度预测 →<br/>Transformer/Mamba时序增强 → 共形预测<br/>产出：signal（Insight: direction/confidence<br/>/horizon）<br/>文件: （设计态，暂无代码引用）"]
    N141["(设计态 / design) 市场仿真器 / Market Simulator<br/>模拟市场行情数据生成合成数据流，为策略验证提供可<br/>控的测试环境<br/>文件: decision/simulation/sim_01"]
    LL2A --- N141
    N142["(设计态 / design) 策略仿真器 / Strategy<br/>Simulator<br/>在仿真市场中运行策略逻辑并记录决策轨迹，离线评估<br/>策略表现<br/>文件: decision/simulation/sim_02"]
    LL2A --- N142
    N143["(设计态 / design) 风控仿真器 / Risk Simulator<br/>模拟风控规则在极端行情下的触发行为，验证风控参数<br/>有效性<br/>文件: decision/simulation/sim_03"]
    LL2A --- N143
    N144["(设计态 / design) 压力测试引擎 / Stress Test<br/>Engine<br/>对组合施加极端场景冲击测试生存能力，找出崩盘前的<br/>脆弱点<br/>文件: decision/simulation/sim_04"]
    LL2A --- N144
    N145["(设计态 / design) 场景生成器 / Scenario<br/>Generator<br/>构造历史重放和假设性极端市场场景，为仿真提供多样<br/>化输入<br/>文件: decision/simulation/sim_05"]
    LL2A --- N145
    N146["(设计态 / design) 历史重放引擎 / History Replay<br/>Engine<br/>按时间顺序回放历史行情数据重现过去交易日，支持策<br/>略复盘<br/>文件: decision/simulation/sim_07"]
    LL2A --- N146
    N147["(设计态 / design) 极端事件仿真 / Extreme Event<br/>Simulator<br/>模拟熔断闪崩等极端行情检验系统韧性，确保黑天鹅下<br/>不失控<br/>文件: decision/simulation/sim_10"]
    LL2A --- N147
    N148["(设计态 / design) 依赖图数字孪生 / Dependency<br/>Graph Digital Twin<br/>构建依赖图的数字镜像用于仿真推演，预测架构变更的<br/>连锁影响<br/>文件: decision/simulation/sim_13"]
    LL2A --- N148
    N149["(设计态 / design) 混沌实验自动生成 / Chaos<br/>Experiment Auto-Generator<br/>自动注入故障和延迟测试系统容错能力，发现隐藏的单<br/>点故障<br/>文件: decision/simulation/sim_15"]
    LL2A --- N149
    N150["(设计态 / design) 回测过拟合检测器 / Backtest<br/>Overfitting Detector<br/>检测策略回测是否过度拟合历史数据，防止上线后实盘<br/>失效<br/>文件: decision/simulation/sim_18"]
    LL2A --- N150
    N151["(设计态 / design) Walk-Forward分析器 /<br/>Walk-Forward Analyzer<br/>用滚动窗口前推验证策略稳健性，避免参数只对特定区<br/>间有效<br/>文件: decision/simulation/sim_19"]
    LL2A --- N151
    N152["(设计态 / design) 参数鲁棒性测试器 / Parameter<br/>Robustness Tester<br/>扰动策略参数观察收益稳定性，确认参数非过拟合的临<br/>界值<br/>文件: decision/simulation/sim_21"]
    LL2A --- N152
    N153["(设计态 / design) 验证自动化流水线 / Validation<br/>Automation Pipeline<br/>串联三阶段验证为自动化流水线，降低人工验证成本<br/>文件: decision/simulation/sim_33"]
    LL2A --- N153
    N154["(设计态 / design) 自动化过拟合门禁 / Automated<br/>Overfitting Detector Gate<br/>在 CI 中自动检测过拟合并阻断不合格策略上线，守住<br/>质量门槛<br/>文件: decision/simulation/sim_56"]
    LL2A --- N154
    N155["(设计态 / design) 3阶段决策门控 / IS→WFA→OOS<br/>3-Stage Decision Gate<br/>按样本内训练到样本外测试三阶段门控策略发布，防过<br/>拟合上线<br/>文件: decision/simulation/sim_g1"]
    LL2A --- N155
    LL2B["(设计态 / design) L2B 主力行为层 / Main Force<br/>Behavior Analysis<br/>六阶段识别 + 自迭代推演 + 庄家专项 +<br/>群体博弈模拟 产出：main_force_signal<br/>（主力行为画像）<br/>文件: （设计态，暂无代码引用）"]
    LL2C["(设计态 / design) L2C 市场状态与大盘预测层 /<br/>Market State & Index Prediction<br/>3×3矩阵 + 2叠加态 + 三层大盘预测 +<br/>T+1次日8态走势预测 + 体制转换检测(HMM/变点)<br/>产出：market_state_prediction（大盘方向/波动率<br/>/体制判断）<br/>文件: （设计态，暂无代码引用）"]
    LL2D["(设计态 / design) L2D 知识图谱与因果推演层 /<br/>Knowledge Graph & Causal Inference<br/>六类知识图谱 → 事件影响链分析 → 因果传导推演 →<br/>GNN股票关系建模 → Causal ML 产出：causal_<br/>inference_result（因果推断结果）<br/>文件: （设计态，暂无代码引用）"]
    LL3["(生产态 / production) L3 策略组合层 / Strategy<br/>& Portfolio Combination<br/>多策略信号合成 → 资本分配 → 元策略路由 →<br/>组合构建 产出：portfolio_target<br/>（PortfolioTarget: 目标仓位）<br/>文件: MOD-L05-001"]
    LL4["(生产态 / production) L4 风控层 / Risk Control<br/>Pre/Post-Trade 风控校验 + Kill Switch 熔断 +<br/>止损评估 产出：risk_check（RiskDecision:<br/>approve/veto/adjust）<br/>文件: MOD-L04-001"]
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
    N141 -.->|informing / 告知| N142
    N142 -.->|informing / 告知| N143
    N143 -.->|informing / 告知| N144
    N144 -.->|informing / 告知| N145
    N145 -.->|informing / 告知| N146
    N146 -.->|informing / 告知| N147
    N147 -.->|informing / 告知| N148
    N148 -.->|informing / 告知| N149
    N149 -.->|informing / 告知| N150
    N150 -.->|informing / 告知| N151
    N151 -.->|informing / 告知| N152
    N152 -.->|informing / 告知| N153
    N153 -.->|informing / 告知| N154
    N154 -.->|informing / 告知| N155
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class LL0,LL1,LL3,LL4 production
    class LL2A,N141,N142,N143,N144,N145,N146,N147,N148,N149,N150,N151,N152,N153,N154,N155,LL2B,LL2C,LL2D,LL5,LL6 design
```

### 运营态的图（仅 design_maturity=production 的模块和域内依赖）

> 仅展示已上线运行的决策节点（共 0 个），不含跨域外部节点。跨域依赖见下方跨域依赖章节。

> （无模块 / No modules）

### 设计态的图（仅 design_maturity=design 的模块和域内依赖）

> 仅展示蓝图阶段、代码未写的设计态决策节点（共 15 个），不含跨域外部节点。

> 共 6 层，14 边。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'clusterBkg': 'transparent', 'clusterBorder': 'transparent', 'fontSize': '14px'}}}%%
flowchart TD
    LL2A["(设计态 / design) L2A 信号层 / Signal Generation<br/>信号工厂 → 多策略投票 → 收益率条件密度预测 →<br/>Transformer/Mamba时序增强 → 共形预测<br/>产出：signal（Insight: direction/confidence<br/>/horizon）<br/>文件: （设计态，暂无代码引用）"]
    N141["(设计态 / design) 市场仿真器 / Market Simulator<br/>模拟市场行情数据生成合成数据流，为策略验证提供可<br/>控的测试环境<br/>文件: decision/simulation/sim_01"]
    LL2A --- N141
    N142["(设计态 / design) 策略仿真器 / Strategy<br/>Simulator<br/>在仿真市场中运行策略逻辑并记录决策轨迹，离线评估<br/>策略表现<br/>文件: decision/simulation/sim_02"]
    LL2A --- N142
    N143["(设计态 / design) 风控仿真器 / Risk Simulator<br/>模拟风控规则在极端行情下的触发行为，验证风控参数<br/>有效性<br/>文件: decision/simulation/sim_03"]
    LL2A --- N143
    N144["(设计态 / design) 压力测试引擎 / Stress Test<br/>Engine<br/>对组合施加极端场景冲击测试生存能力，找出崩盘前的<br/>脆弱点<br/>文件: decision/simulation/sim_04"]
    LL2A --- N144
    N145["(设计态 / design) 场景生成器 / Scenario<br/>Generator<br/>构造历史重放和假设性极端市场场景，为仿真提供多样<br/>化输入<br/>文件: decision/simulation/sim_05"]
    LL2A --- N145
    N146["(设计态 / design) 历史重放引擎 / History Replay<br/>Engine<br/>按时间顺序回放历史行情数据重现过去交易日，支持策<br/>略复盘<br/>文件: decision/simulation/sim_07"]
    LL2A --- N146
    N147["(设计态 / design) 极端事件仿真 / Extreme Event<br/>Simulator<br/>模拟熔断闪崩等极端行情检验系统韧性，确保黑天鹅下<br/>不失控<br/>文件: decision/simulation/sim_10"]
    LL2A --- N147
    N148["(设计态 / design) 依赖图数字孪生 / Dependency<br/>Graph Digital Twin<br/>构建依赖图的数字镜像用于仿真推演，预测架构变更的<br/>连锁影响<br/>文件: decision/simulation/sim_13"]
    LL2A --- N148
    N149["(设计态 / design) 混沌实验自动生成 / Chaos<br/>Experiment Auto-Generator<br/>自动注入故障和延迟测试系统容错能力，发现隐藏的单<br/>点故障<br/>文件: decision/simulation/sim_15"]
    LL2A --- N149
    N150["(设计态 / design) 回测过拟合检测器 / Backtest<br/>Overfitting Detector<br/>检测策略回测是否过度拟合历史数据，防止上线后实盘<br/>失效<br/>文件: decision/simulation/sim_18"]
    LL2A --- N150
    N151["(设计态 / design) Walk-Forward分析器 /<br/>Walk-Forward Analyzer<br/>用滚动窗口前推验证策略稳健性，避免参数只对特定区<br/>间有效<br/>文件: decision/simulation/sim_19"]
    LL2A --- N151
    N152["(设计态 / design) 参数鲁棒性测试器 / Parameter<br/>Robustness Tester<br/>扰动策略参数观察收益稳定性，确认参数非过拟合的临<br/>界值<br/>文件: decision/simulation/sim_21"]
    LL2A --- N152
    N153["(设计态 / design) 验证自动化流水线 / Validation<br/>Automation Pipeline<br/>串联三阶段验证为自动化流水线，降低人工验证成本<br/>文件: decision/simulation/sim_33"]
    LL2A --- N153
    N154["(设计态 / design) 自动化过拟合门禁 / Automated<br/>Overfitting Detector Gate<br/>在 CI 中自动检测过拟合并阻断不合格策略上线，守住<br/>质量门槛<br/>文件: decision/simulation/sim_56"]
    LL2A --- N154
    N155["(设计态 / design) 3阶段决策门控 / IS→WFA→OOS<br/>3-Stage Decision Gate<br/>按样本内训练到样本外测试三阶段门控策略发布，防过<br/>拟合上线<br/>文件: decision/simulation/sim_g1"]
    LL2A --- N155
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
    N141 -.->|informing / 告知| N142
    N142 -.->|informing / 告知| N143
    N143 -.->|informing / 告知| N144
    N144 -.->|informing / 告知| N145
    N145 -.->|informing / 告知| N146
    N146 -.->|informing / 告知| N147
    N147 -.->|informing / 告知| N148
    N148 -.->|informing / 告知| N149
    N149 -.->|informing / 告知| N150
    N150 -.->|informing / 告知| N151
    N151 -.->|informing / 告知| N152
    N152 -.->|informing / 告知| N153
    N153 -.->|informing / 告知| N154
    N154 -.->|informing / 告知| N155
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class LL2A,N141,N142,N143,N144,N145,N146,N147,N148,N149,N150,N151,N152,N153,N154,N155,LL2B,LL2C,LL2D,LL5,LL6 design
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
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'clusterBkg': 'transparent', 'clusterBorder': 'transparent', 'fontSize': '14px'}}}%%
flowchart TD
    SELF["(设计态 / design) 仿真 / simulation<br/>市场/策略/风控仿真、压力测试、场景生成与历史重放<br/>跨域节点 / cross-domain"]
    EXT_aut_core["(设计态 / design) 自主核心 / aut_core<br/>自主决策编排——权限守卫、自愈回滚、预算执行、健康<br/>监控、漂移检测、自动修复与 Agent 编排<br/>跨域节点 / cross-domain"]
    SELF -.->|出 1| EXT_aut_core
    EXT_signal["(设计态 / design) 信号 / signal<br/>Alpha 信号合成、优先级路由、LLM 策略 Agent<br/>与尾部风险保护<br/>跨域节点 / cross-domain"]
    EXT_signal -.->|入 1| SELF
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class SELF design
    class EXT_aut_core,EXT_signal external_design
```

