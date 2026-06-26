---
module_id: KE-2967
status: active
title: 交易模式切换（Trading Mode）
category: module_blueprint
ttl: permanent
---

# 交易模式切换（Trading Mode）

交易模式切换（Trading Mode）

```
TradingMode 是整个系统的"全局运行模式"，决定 L04/L05/L06 三层的行为：

NORMAL     — 实盘模式：真实订单→真实broker→真实资金→KillSwitch就绪
PAPER      — 纸交易：订单→模拟broker→模拟资金→AI施工默认模式
BACKTEST   — 回测模式：SimulatedClock+DeterministicRandom+EventStore重放
READ_ONLY  — 只读模式：所有写操作被DryRun拦截→仅记录不执行
KILLED     — 紧急停止：已触发KillSwitch→所有交易活动冻结
            └── 仅Owner可手动切换回NORMAL（需双因子验证）

模式切换路径限制：
  NORMAL ⇄ PAPER（任一方向）
  PAPER → BACKTEST
  BACKTEST → PAPER
  ANY → READ_ONLY（自动：错误率>阈值时）
  ANY → KILLED（Owner手动/自动：特定条件触发）
  KILLED → NORMAL（仅Owner双因子验证）
```
