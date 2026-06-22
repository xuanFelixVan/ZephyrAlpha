---
module_id: KE-340------deprecation-policy-001
status: active
title: 4.3 废弃政策（Deprecation Policy）
category: documentation
---

# 4.3 废弃政策（Deprecation Policy）

4.3 废弃政策（Deprecation Policy）

1. 任何外部接口（EI 系列）废弃前，在本视图 §3.2 集成点清单中标记 `status: deprecated`，注明废弃时间和替代方案
2. 内部接口废弃须在 `architecture_model/contracts/cross_layer_contracts.yaml` 中标记 `stability: deprecated`
3. 废弃的接口保留至少 1 个完整的回测周期（当前为 30 天）后移除

---
