---
module_id: KE-922
status: active
title: 4.4.4 降级策略
category: governance
ttl: permanent
doc_type: knowledge_entry
---

# 4.4.4 降级策略

4.4.4 降级策略

- **G4-C01 依赖缺失** → `defer`（唯一非 `reject` 的 P0 路径）；task 状态进 `WAITING`，`waiting_for` 字段记录缺失依赖 ID 列表
- **G4-C02 冲突** → `flag` 而非 `reject`；task 进 `BLOCKED`，必须 Owner 合并后 `BLOCKED→READY`
- **其他 P0** → `reject`；task 进 `FAILED`
