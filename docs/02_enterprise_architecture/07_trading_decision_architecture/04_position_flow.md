---
ttl: permanent
doc_type: architecture_view
generator: generate_trading_flow_diagram.py
flow_stage: position_management
---

# 仓位裁决

> flow_stage: `position_management` | 映射层: ['L3'] | 产出契约: `target_position`

## 大白话讲这个流程

仓位裁决把"想买多少"变成"实际能买多少"。
portfolio_target 进来后，经过多层约束裁决：
  - 单票上限：单只股票不超过总资金的 N%
  - 行业集中度：单行业不超过 M%
  - 总仓位上限：总持仓不超过总资金的 K%
  - 资金可用性：可用资金是否够
  - 持仓冲突：和现有持仓是否冲突
裁决后产出 portfolio_target_adjusted（实际目标仓位）。
仓位裁决是实盘同构的关键——回测引擎必须串入仓位裁决，不能跳过。
D_POSITION 域当前实现率仅 10%，是实盘主链路的关键缺口。


## 流程框图

```
portfolio_target（想买多少）
    │
    ├─ 单票上限约束    ──┐
    ├─ 行业集中度约束  ──┤
    ├─ 总仓位上限约束  ──┼─→ 仓位裁决 → portfolio_target_adjusted（实际能买多少）
    ├─ 资金可用性检查  ──┤
    └─ 持仓冲突检查    ──┘

```

## 运营态节点（实盘主链路）

_（暂无已标定节点，待 Phase B 全量标定）_


## 指挥 AI 提示

改仓位裁决时，先查 decisiongraph 里 flow_stage=position_management 的节点。
常见改动：调上限阈值、加约束规则、改裁决顺序。
实盘同构：回测引擎必须调用仓位裁决，不能跳过（D_POSITION 实现率缺口）。


## 子流程

### 单票上限

单只股票不超过总资金的 N%。

模块锚点: `MOD-L04-001`

### 行业集中度

单行业不超过 M%。

模块锚点: `MOD-L04-001`

### 总仓位上限

总持仓不超过总资金的 K%。

模块锚点: `MOD-L04-001`

## 附录1·待施工（设计态节点）

_（暂无已标定节点，待 Phase B 全量标定）_


## 附录2·未来增强（候选库）

_（Phase C：从 candidate_module_registry.yaml 提取 deferred/rejected 条目，按 panorama_position.decisiongraph.target_layer 归类）_

