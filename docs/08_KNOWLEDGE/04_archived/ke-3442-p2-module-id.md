---
module_id: KE-3312-------module-id--28-004
title: 4.6 P2 级：缺少 `module_id`（28 个文件）
category: documentation
---

# 4.6 P2 级：缺少 `module_id`（28 个文件）

4.6 P2 级：缺少 `module_id`（28 个文件）

| 集中目录 | 数量 | 说明 |
|---------|------|------|
| `01_policies_and_standards/` | 18 | 标准文档普遍缺失 module_id |
| `02_enterprise_architecture/target_architecture/architecture-model/` | 3 | 使用旧版 `doc_id` 而非 `module_id` |
| `01_policies_and_standards/governance/ai/` | 3 | AI 治理策略文档 |
| 其他 | 4 | migration-declaration.md、session log、index 等 |

**使用旧版 `doc_id` 的文件**（应改为 `module_id`）：

| 文件 | 当前 doc_id | 应改为 module_id |
|------|-----------|-----------------|
| `architecture-model/ssot-authority-map.md` | `ARCH-SSOT-001` | `STD-SSOT-AUTHORITY-MAP`（已在新版中使用） |
| `architecture-model/architecture_endgame_locked.md` | `ARCH-ENDGAME-001` | 待分配 |
| `architecture-model/dependency-graph-framework.md` | `ARCH-DEP-001` | 待分配 |
| `01_policies_and_standards/operational/devops/pre-commit-simplification-plan.md` | `GOV-PRECOMMIT-001` | 待分配 |
