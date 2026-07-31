---
ttl: permanent
doc_type: architecture_view
generator: generate_trading_flow_diagram.py
flow_stage: sell_flow
---

# 卖出决策流

> flow_stage: `sell_flow` | 映射层: ['L2A', 'L3'] | 产出契约: `sell_signal`

## 大白话讲这个流程

卖出流决定"持仓里的哪只该卖、为什么卖、什么时候卖"。
卖出信号来源多，需要融合仲裁：
  ① 止损信号——跌破止损线
  ② 止盈信号——达到止盈目标
  ③ 信号反转——买入信号消失或反向
  ④ 风控触发——持仓触及风控红线
  ⑤ 主力行为——主力出货信号（L2B）
  ⑥ 大盘预警——大盘走弱需减仓（L2C）
  ⑦ 时间到期——持仓时间到上限
  ⑧ 人工卖出——人工指令
多源卖出信号融合仲裁，产出 sell_decision（卖/不卖/部分卖）。
卖出流和买入流共享信号源（共享信号注入层），但仲裁逻辑独立。


## 流程框图

```
持仓 position
    │
    ├─→ 止损信号     ──┐
    ├─→ 止盈信号     ──┤
    ├─→ 信号反转     ──┤
    ├─→ 风控触发     ──┤
    ├─→ 主力出货     ──┼─→ 卖出信号融合仲裁 → sell_decision（卖/不卖/部分卖）
    ├─→ 大盘预警     ──┤
    ├─→ 时间到期     ──┤
    └─→ 人工卖出     ──┘

```

## 运营态节点（实盘主链路）

_（暂无已标定节点，待 Phase B 全量标定）_


## 指挥 AI 提示

改卖出流时，先查 decisiongraph 里 flow_stage=sell_flow 的节点（sell_decision 类型）。
常见改动：调止损/止盈阈值、加卖出触发源、改融合仲裁权重。
注意：sell_decision 节点不能直接连 order，必须经 portfolio_target（不变量 DEC-INV-002）。


## 子流程

### 止损信号

跌破止损线触发卖出。

模块锚点: `MOD-L04-001`

### 止盈信号

达到止盈目标触发卖出。

模块锚点: `MOD-L05-001`

### 信号反转

买入信号消失或反向触发卖出。

模块锚点: `MOD-L05-001`

### 卖出信号融合仲裁

多源卖出信号融合，产出 sell_decision。

模块锚点: `MOD-L05-001`

## 附录1·待施工（设计态节点）

_（暂无已标定节点，待 Phase B 全量标定）_


## 附录2·未来增强（候选库）

_（Phase C：从 candidate_module_registry.yaml 提取 deferred/rejected 条目，按 panorama_position.decisiongraph.target_layer 归类）_

