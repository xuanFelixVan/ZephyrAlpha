---
module_id: KE-491
status: active
title: 7.2 跨层数据流路径
category: documentation
---

# 7.2 跨层数据流路径

7.2 跨层数据流路径

> 下图标注了 P0 跨层数据契约 ID（CTR-001~CTR-006）作为架构承重墙。
> 可视化版本 → [`diagrams/data_flow.mmd`](diagrams/data_flow.mmd)

```
L00 ──[CTR-001: NormalizedMarketData 🔒]──→ L02 ──[CTR-002: FactorSignal 🔒]──→ L03/L04/L05
L04 ──[CTR-003: RiskLimits 🔒]──→ L05 ──[CTR-004: Order 🔓]──→ L06 ──[CTR-005: Fill 🔒]──→ L07
L06 ──[CTR-006: PositionSnapshot 🔒]──→ L04 (Risk Monitor) / L11 (Strategic)
L07 ──[CTR-006: PositionSnapshot 🔒]──→ L04 (Risk Monitor) / L11 (Strategic)
```

**图例**：🔒 = frozen（不可变契约） | 🔓 = mutable（可变契约，含状态机）
