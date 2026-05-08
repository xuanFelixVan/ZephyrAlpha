---
module_id: KE-documentat-2_7-001
title: 2.7 实体上下游关系（一句话叙事）
category: documentation
---

# 2.7 实体上下游关系（一句话叙事）

2.7 实体上下游关系（一句话叙事）

```
Tick / OrderBookSnapshot → (聚合) → Bar
       Bar + Security + CorporateAction → (PIT 复权) → AdjustedBar (虚拟视图)
              AdjustedBar + IndexConstituent → (因子计算 asof) → FactorValue
                     FactorValue → FeatureSet → (策略) → Signal
                                                Signal → TargetPosition
                                                       → Order(CTR-004) → Fill(CTR-005) → Position(CTR-006)
                                                                          → PnL / RiskMetric
```

> **与跨层数据契约的对齐**：上述 `Order`/`Fill`/`Position` 分别对应 P0 跨层数据契约 **CTR-004** (Order, mutable)、**CTR-005** (Fill, frozen)、**CTR-006** (PositionSnapshot, frozen)。
> 契约真源：`architecture-model/contracts/cross-layer-contracts.yaml`。

每一条 → 都对应 §6 的一条**血缘边**（lineage edge），有 `lineage_root` 字段在实体里显式登记。

---
