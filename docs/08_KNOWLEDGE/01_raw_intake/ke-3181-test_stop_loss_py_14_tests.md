---
module_id: KE-3075
title: test_stop_loss.py（14 tests）
category: session_log
ttl: permanent
---

# test_stop_loss.py（14 tests）

test_stop_loss.py（14 tests）
| 测试类 | 测试数 | 覆盖场景 |
|--------|--------|---------|
| TestEvaluateStopLossFixedPct | 3 | 跌破/未破/边界 |
| TestEvaluateStopLossTrailing | 2 | 从高点回落/未触发 |
| TestEvaluateStopLossTimeBased | 2 | 超时/未超时 |
| TestEvaluateStopLossVolatility | 2 | 波动突破/未突破 |
| TestEvaluateStopLossEdgeCases | 2 | 零价格/未知方法 fallback |
| TestTriggerKillSwitch | 2 | 激活/符号范围 |
| TestResetKillSwitch | 1 | 重置确认 |
