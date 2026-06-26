---
module_id: KE-962
status: active
title: 5.5 MRS-003：同步后校验
category: governance
ttl: permanent
---

# 5.5 MRS-003：同步后校验

5.5 MRS-003：同步后校验

**规则**：任何触及 MRS-001 矩阵中 ✅ 标记的修改完成后，MUST 立即运行相关校验：

| 校验 | 覆盖 | 何时运行 |
|------|------|---------|
| `check_registry_consistency.py` | 跨登记表共享字段一致性（CR-001~006） | 任何触及 module-registry.yaml / blueprint_registry.yaml / 物理 blueprint.md 的操作后 |
| `check_frontmatter_metadata.py` | frontmatter 字段合法性 | 创建任何文档后 |
| `check_architecture_gates.py` | ADR/模块/架构一致性 | 创建/修改 ADR 或模块后 |
| `validate_directory_registry.py` | 物理目录 vs 登记表漂移 | 创建新目录后 |

- 如果校验脚本不可用（如 Python 环境问题），MUST 手动逐条对照 SSoT 定义验证
- 任何 FAIL 必须在 commit 前修复

---
