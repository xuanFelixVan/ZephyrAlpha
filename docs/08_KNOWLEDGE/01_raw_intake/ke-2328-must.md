---
module_id: KE-2233---------must-005
status: active
title: 4.3 蓝图文件名约定（MUST）
category: module_blueprint
ttl: permanent
---

# 4.3 蓝图文件名约定（MUST）

4.3 蓝图文件名约定（MUST）

| 蓝图类型 | 文件名 | 示例 |
|------|------|------|
| Level 0 总蓝图 | `system-master-blueprint.md` | `MOD-MASTER_BLUEPRINT` |
| Level 1 域蓝图 | `domain-integration-blueprint.md` | `MOD-DOMAIN-SIG-001` |
| Level 2 模块蓝图 | `blueprint.md`（简洁——目录名已承载模块信息）| `MOD-TASK_SYSTEM/blueprint.md` |

**规则**：
- Level 2 模块蓝图：文件名**统一是 `blueprint.md`**——模块名在目录名中，文件承载蓝图内容
- Level 0/1 蓝图：文件名**描述性命名**——因为这些目录下只有这一份独立蓝图文件，命名要一目了然

---
