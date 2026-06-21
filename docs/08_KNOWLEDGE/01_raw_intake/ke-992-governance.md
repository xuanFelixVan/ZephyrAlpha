---
module_id: KE-914
status: active
title: 4.3.4 降级策略
category: governance
---

# 4.3.4 降级策略

4.3.4 降级策略

- **P0 失败** → task 降档到 `FAILED`，可进入 `RETRY` 重评，或由 Owner 手动裁定 `CANCELLED`
- **P1 相似度过高** → 记 `dedup_candidate` 事件；不阻断，但该文档在 G4 阶段必须挂载 `merge_policy` 元数据
