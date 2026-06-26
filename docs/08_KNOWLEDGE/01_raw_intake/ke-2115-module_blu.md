---
module_id: KE-2024
status: active
title: 3. 接口契约
category: module_blueprint
ttl: permanent
---

# 3. 接口契约

3. 接口契约

> ⚠️ 完整升级方案——6 个子节。强制 Pydantic V2 BaseModel（KBG-0040）。
>
> **模型层级**：`shared/schemas.py` `Task`（**语义 28 + 追踪 3 = 31 字段**，metadata_registry.yaml §7.1~§7.1.1）→ 本蓝图 TaskCard 继承 `Task` 并扩展 Vibe Coding 执行层字段（§3.2.1）。
