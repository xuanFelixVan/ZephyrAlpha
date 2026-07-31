---
ttl: permanent
doc_type: architecture_view
generator: generate_trading_flow_diagram.py
---

# 四模式开关 + 应急保命降级

## 四模式开关（回测/Paper/Shadow/实盘）

同一套决策代码路径，通过模式开关切换运行形态，保证 sim↔实盘同构：
  - backtest  —— 历史数据回放 + 模拟撮合，验证策略
  - paper     —— 实时数据 + 模拟下单不成交，验证实时链路
  - shadow    —— 实时数据 + 全链路实跑不下单，测量 sim↔live divergence
  - live      —— 实时数据 + 真实下单
模式开关在执行层（execution flow）生效，不影响信号/策略/风控的决策逻辑。
实盘同构铁律：回测引擎必须串入 D_POSITION + D_RISK，不跳过仓位和风控。


| 模式 | 数据源 | 下单方式 |
|---|---|---|
| 回测模式 | 历史回放 | 模拟撮合 |
| Paper 模式 | 实时 | 模拟下单不成交 |
| Shadow 模式 | 实时 | 全链路实跑不下单 |
| 实盘模式 | 实时 | 真实下单 |

## 应急保命降级路径

当模型/策略/信号失效时，系统逐级降级保命：
  - L2 信号失效 → 硬编码均线信号
  - L3 策略失效 → 固定比例仓位
  - L4 风控失效 → 硬编码 10% 单票上限
  - 数据断流   → 仅执行卖出（不买入）
降级触发由 Kill Switch 熔断 + 数据健康监控驱动。


> 数据源：trading_flow_narrative.yaml
