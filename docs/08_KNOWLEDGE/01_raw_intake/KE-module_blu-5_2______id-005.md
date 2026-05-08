---
module_id: KE-module_blu-5_2______id-005
title: 5.2 既存蓝图 ID 兼容性
category: module_blueprint
---

# 5.2 既存蓝图 ID 兼容性

5.2 既存蓝图 ID 兼容性

现有 19 份蓝图（创建于 PS-STD-005 发布之前）的 module_id **保持不动**——这是一个相容性规则：

| 既存 ID | 蓝图层级（新分类）| 兼容性说明 |
|------|:---:|------|
| `MOD-MASTER-001` | Level 1（当前）→ Level 0（beta 升级后）| 当前它承担 L01 域集成蓝图职责。beta 后升级为全系统总蓝图或降级为 DOMAIN-L01。兼容期内 ID 不动 |
| `MOD-INF-001~017` | Level 2 MODULE | ✅ 不涉及不兼容 |
| `MOD-KB-001` | Level 2 MODULE | ✅ 不涉及不兼容 |
| `MOD-INF-003`（deprecated）| Level 2 MODULE | ✅ 已废弃，兼容性不适用 |
| `MOD-INF-004`（deprecated）| Level 2 MODULE | ✅ 已废弃，兼容性不适用 |

> **既存蓝图不强制改名**——新标准只要求新增蓝图遵循 ID 体系。
> 既存蓝图在第一份该层的 experimental 升级**蓝图时，自然迁移**。

---
