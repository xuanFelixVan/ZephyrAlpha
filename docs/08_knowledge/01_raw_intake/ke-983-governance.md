---
module_id: KE-905
status: active
title: 4.2.3 降级策略
category: governance
ttl: permanent
doc_type: knowledge_entry
---

# 4.2.3 降级策略

4.2.3 降级策略

- **P0 失败** → 状态机回滚；task 返回 `IN_PROGRESS` 并记 `gates.details.failed_checks`
- **`auto_assign` 特例**：G2-C03 缺失 priority 时自动填 P2；记 `events.auto_assigned`
- **`reject` 后的处置**：task 可通过 `transition(FAILED)→transition(RETRY)` 路径重入
