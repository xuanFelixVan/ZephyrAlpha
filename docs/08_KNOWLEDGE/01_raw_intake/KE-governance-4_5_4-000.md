---
module_id: KE-governance-4_5_4-000
title: 4.5.4 降级策略
category: governance
---

# 4.5.4 降级策略

4.5.4 降级策略

- **`auto_assign` / `auto_scope`** → 记 `events.auto_filled`，继续
- **G5-C02 路径冲突** → `flag` 等待 Owner 在 commit trailer 设 `gate-exempt: G5-C02 | reason: ... | valid_until: ...`
- **P0 失败** → `reject`，task 进 `FAILED` 并清理临时产物

---
