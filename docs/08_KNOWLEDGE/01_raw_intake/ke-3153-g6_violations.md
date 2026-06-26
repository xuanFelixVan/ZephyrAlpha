---
module_id: KE-3047
status: active
title: G6 Violations 明细
category: session_log
ttl: permanent
---

# G6 Violations 明细

G6 Violations 明细

**2x 自造数据类型（HIGH）：**
- L04 risk_limits.py:29 — self-creates RiskLimits
- L04 risk_manager.py:32 — self-creates RiskLimits

Root cause: Phase B skeleton 阶段在层内定义了 RiskLimits 作为本地 dataclass。
Resolution: 在 Phase D 实施时迁移至 shared/contracts/risk_limits.py。

**18x float-in-money-fields（HIGH）：**
- L00 quality_gate.py: 7 处 — open_price/high/low/close/volume/price/prev_close
- L03 signal_synthesizer.py: 2 处 — signal_value/value
- L03 capital_allocator.py: 1 处 — rebalance_threshold
- L04 risk_limits.py: 1 处 — total_nav
- L04 risk_manager.py: 2 处 — limit_value/actual_value
- L04 risk_validator.py: 3 处 — limit_value/actual_value/total_nav
- L04 risk_manager_base.py: 2 处 — limit_value/actual_value

Root cause: Phase A/B skeleton 使用了 float 保持结构清晰。
Resolution: 在 Phase D 实施时全量迁移至 Decimal（CTR 全域强制）。
