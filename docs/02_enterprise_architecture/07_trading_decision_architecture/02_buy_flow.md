---
ttl: permanent
doc_type: architecture_view
generator: generate_trading_flow_diagram.py
flow_stage: buy_flow
---

# 买入决策流

> flow_stage: `buy_flow` | 映射层: ['L2A', 'L2B', 'L2C', 'L2D', 'L3'] | 产出契约: `buy_signal`

## 大白话讲这个流程

买入流把候选池里的标的变成"买什么、买多少"的目标仓位。
四轨的信号在这里融合：
  - 模型驱动轨：L2A 信号 + L2B 主力行为 + L2C 大盘预测 + L2D 因果推演
  - 数据驱动轨：端到端 DL 信号补充
  - 人工指令轨：人工买入指令（优先级高）
  - 应急保命轨：降级时硬编码信号
融合后的信号进 L3 策略组合层：
  - 多策略信号合成（多个策略的信号加权/投票）
  - 元策略路由（按市场状态选策略族）
  - 资本分配（总资金分给各策略）
  - 组合构造（产出 portfolio_target：每只股票目标仓位）
portfolio_target 是买入流的终点，下一步进仓位裁决或直接进风控。


## 流程框图

```
候选池 candidate_pool
    │
    ├─→ 模型驱动轨 ──┐
    ├─→ 数据驱动轨 ──┤
    ├─→ 人工指令轨 ──┼─→ 四轨融合 → 信号合成 → 策略路由 → 资本分配 → 组合构造
    └─→ 应急保命轨 ──┘                                              │
                                                                        ▼
                                                              portfolio_target

```

## 运营态节点（实盘主链路）

_（暂无已标定节点，待 Phase B 全量标定）_


## 指挥 AI 提示

改买入流时，先查 decisiongraph 里 flow_stage=buy_flow 的节点。
常见改动：调四轨融合权重、加策略、改资本分配规则。
注意：signal 节点不能直接连 order，必须经 portfolio_target（不变量 DEC-INV-002）。


## 子流程

### 四轨融合

四轨信号按优先级融合，人工 > 模型 > 数据，应急压制其他。

模块锚点: `MOD-L05-001`

### 信号合成

多策略信号加权/投票，产出统一信号。

模块锚点: `MOD-L05-001`

### 元策略路由

按市场状态（L2C 大盘预测）选策略族。

模块锚点: `MOD-L05-001`

### 资本分配

总资金分给各策略/标的。

模块锚点: `MOD-L05-001`

## 附录1·待施工（设计态节点）

| node_id | 决策名称 | 节点类型 | layer | module_id | path |
|---|---|---|---|---|---|
| 177 | Synthesizer 信号合成+权重分配 | signal | L2A | - | `decision/signal/sg_01` |
| 178 | Signal Priority Router 信号优先级路由 | signal | L2A | - | `decision/signal/sg_02` |
| 179 | LLM Strategy Agent LLM策略Agent | signal | L2A | - | `decision/signal/sg_03` |
| 180 | Signal Tail Risk Protector 信号尾部风险保护 | signal | L2A | - | `decision/signal/sg_04` |
| 181 | A-Share Plan Conformity Evaluator A股计划吻合度评估 | signal | L2A | - | `decision/signal/sg_05` |
| 182 | A-Share Emergency Opportunity Evaluator A股应急机会评估 | signal | L2A | - | `decision/signal/sg_06` |
| 183 | A-Share Capital-Force Conflict Arbiter 主力游资冲突仲裁 | signal | L2A | - | `decision/signal/sg_07` |
| 184 | Regime Special Override Priority Manager Regime特殊覆盖优先级 | signal | L2A | - | `decision/signal/sg_08` |
| 185 | Risk-Signal Interaction Sequencer 风控-信号交互时序 | signal | L2A | - | `decision/signal/sg_09` |
| 186 | 36环节决策框架实现器 36-Step Decision Framework | signal | L2A | - | `decision/signal/sg_10` |
| 187 | 策略替换与淘汰决策器 Strategy Replacement Decision | signal | L2A | - | `decision/signal/sg_11` |
| 188 | 信号冲突解决 Signal Conflict Resolution | signal | L2A | - | `decision/signal/sg_12` |
| 189 | 信号融合模块 Signal Fusion Module | signal | L2A | - | `decision/signal/sg_13` |


## 附录2·未来增强（候选库）

_从 candidate_module_registry.yaml 按 target_track 归类到本阶段；基础设施类候选（回测/仿真/灾备/死域）见 [总览](trading_flow_index.md) 跨阶段附录_

_（本阶段暂无候选模块）_

