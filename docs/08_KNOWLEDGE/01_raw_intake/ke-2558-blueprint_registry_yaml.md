---
module_id: KE-2463---002
status: active
title: 8.1 `blueprint_registry.yaml` 扩展（MUST）
category: module_blueprint
---

# 8.1 `blueprint_registry.yaml` 扩展（MUST）

8.1 `blueprint_registry.yaml` 扩展（MUST）

在每条 blueprints[] 记录中**新增** `blueprint_level` 字段：

```yaml
blueprints:
  - module_id: "MOD-MASTER-001"
    name: "master-blueprint"
    blueprint_level: "domain"     # ← 新增：SYSTEM / DOMAIN / MODULE
```

| `blueprint_level` | 含义 | 对应 ID 前缀 |
|:--|------|------|
| `system` | Level 0 全系统总蓝图 | `SYS-MASTER` 或 `MOD-MASTER`（1 变体）|
| `domain` | Level 1 功能域集成蓝图 | `MOD-DOMAIN` 或 `MOD-MASTER`（1 变体）|
| `module` | Level 2 单模块蓝图 | `MOD-{LAYER/DOMAIN}` |
