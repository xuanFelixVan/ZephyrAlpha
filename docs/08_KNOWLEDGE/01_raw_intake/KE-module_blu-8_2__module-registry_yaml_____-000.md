---
module_id: KE-module_blu-8_2__module-registry_yaml_____-000
title: 8.2 `module-registry.yaml` 扩展（SHOULD）
category: module_blueprint
---

# 8.2 `module-registry.yaml` 扩展（SHOULD）

8.2 `module-registry.yaml` 扩展（SHOULD）

在每条 modules[] 记录的 `blueprint:` 下**新增** `parent_blueprint` 字段：

```yaml
modules:
  - module_id: "MOD-INF-006"
    blueprint:
      status: approved
      file: "blueprint.md"
      parent_blueprint: "MOD-MASTER-001"   # ← 新增
```

---
