---
module_id: KE-1159------------10-001
status: active
title: IRN-010：受保护路径不可写（铁律10）
category: governance
---

# IRN-010：受保护路径不可写（铁律10）

IRN-010：受保护路径不可写（铁律10）

以下路径禁止 AI 直接写入、删除或重命名：

| 路径 | 保护级别 |
|------|:---:|
| `.git/` | 只读——禁止任何操作 |
| `AGENTS.md` | 重大修改须 Owner 审批（小修需在 session log 记录） |
| `docs/01_policies_and_standards/meta/` 下所有 `.md` | 重大修改须 Owner 审批 |
| `docs/02_enterprise_architecture/target_architecture/architecture-model/` | 重大修改须 Owner 审批 |

- 验证方法：写入前检查目标路径是否在受保护清单中（`check_protected_paths.py`——规格占位）
- 违反后果：关键文件被覆盖 → 架构不可恢复
