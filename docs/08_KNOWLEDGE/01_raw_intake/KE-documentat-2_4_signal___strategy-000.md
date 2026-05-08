---
module_id: KE-documentat-2_4_signal___strategy-000
title: 2.4 Signal & Strategy 域（信号与策略）
category: documentation
---

# 2.4 Signal & Strategy 域（信号与策略）

2.4 Signal & Strategy 域（信号与策略）

| # | Entity | 描述 / 字段族 | 生命周期 | PIT 敏感 | 典型存储 hint |
|---|--------|--------------|---------|---------|---------------|
| E11 | `Signal` | 策略输出信号（strategy_id, symbol, ts, signal_type, magnitude, lineage_root） | append-only | 🔴 高 | 时序库 |
| E12 | `TargetPosition` | 目标持仓（portfolio_id, symbol, target_weight, ts_decision, lineage_root） | append-only | 🟡 中 | OLTP |
