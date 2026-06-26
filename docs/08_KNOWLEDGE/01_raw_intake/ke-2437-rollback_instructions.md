---
module_id: KE-2342
status: active
title: 6. Rollback Instructions
category: module_blueprint
ttl: permanent
---

# 6. Rollback Instructions

6. Rollback Instructions

1. 删除 `src/zephyr/context-engine/` 目录下所有 TASK-001 新建的文件
2. 恢复 `blueprint_registry.yaml` 中 MOD-CONTEXT_ENGINE 条目至此前状态
3. 恢复 `blueprint.md` 的 `construction_progress` 字段（如改过）
