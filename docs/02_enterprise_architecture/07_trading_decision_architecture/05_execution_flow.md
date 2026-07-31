---
ttl: permanent
doc_type: architecture_view
generator: generate_trading_flow_diagram.py
flow_stage: execution
---

# 执行

> flow_stage: `execution` | 映射层: ['L3', 'L4'] | 产出契约: `executed_order`

## 大白话讲这个流程

执行把目标仓位变成真实成交。
流程：portfolio_target_adjusted → 风控审批 → 订单生成 → 智能路由 → 撮合 → 成交。
风控一票否决铁律：order 节点必须有至少一条 approving 入边来自 risk_check
（不变量 DEC-INV-001）。风控不批，订单不下。
订单生命周期状态机：
  submit → ack → partial_fill → fill → complete
           │
           └→ cancel（撤单）
智能路由（SOR）决定订单发到哪个渠道（miniqmt/akshare 等）。
四模式开关在这一层生效：backtest 模拟撮合、paper 不成交、shadow 不下单、live 真实下单。


## 流程框图

```
portfolio_target_adjusted
    │
    ▼
risk_check（风控审批，一票否决）
    │ approving
    ▼
order 生成 ──→ SOR 智能路由 ──→ 撮合引擎
                                    │
    ┌───────────────────────────────┘
    ▼
submit → ack → partial_fill → fill → complete
             │
             └→ cancel
（模式开关：backtest/paper/shadow/live 在此层切换）

```

## 运营态节点（实盘主链路）

_（暂无已标定节点，待 Phase B 全量标定）_


## 指挥 AI 提示

改执行流时，先查 decisiongraph 里 flow_stage=execution 的节点（order/risk_check 类型）。
常见改动：加风控规则、改订单生命周期、调 SOR 路由逻辑、加模式开关分支。
注意：order 节点必须有 risk_check 的 approving 入边（不变量 DEC-INV-001）。


## 子流程

### Pre-Trade 风控

下单前风控审批，一票否决。

模块锚点: `MOD-L04-001`

### 订单生成

从 portfolio_target 生成订单指令。

模块锚点: `MOD-L05-001`

### 智能路由

订单发到哪个渠道（miniqmt/akshare）。

模块锚点: `MOD-MKT_DATA`

### 订单生命周期

submit→ack→partial_fill→fill→complete/cancel 状态机。

模块锚点: `MOD-L04-001`

## 附录1·待施工（设计态节点）

_（暂无已标定节点，待 Phase B 全量标定）_


## 附录2·未来增强（候选库）

_（Phase C：从 candidate_module_registry.yaml 提取 deferred/rejected 条目，按 panorama_position.decisiongraph.target_layer 归类）_

