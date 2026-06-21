---
module_id: KE-608
status: active
title: 五、Module ID 跨文件一致性
category: documentation
---

# 五、Module ID 跨文件一致性

五、Module ID 跨文件一致性

**权威来源**：`docs/02_enterprise_architecture/target-architecture/architecture-model/module_id_registry.yaml`（Stage D 后统一到 YAML SSoT，替代旧体系 JSON 注册表）

```yaml
protected_field: module_id
authority_file: docs/02_enterprise_architecture/target-architecture/architecture-model/module_id_registry.yaml
check_rules:
  - rule: no_duplicate_active   # 同一 module_id 不得在两个 Active 文件中出现
    severity: P0
  - rule: consistent_layer      # 同一 module_id 在多文件中 layer 字段必须一致
    severity: P1
  - rule: consistent_status     # 同一 module_id 在多文件中 status 不得矛盾
    severity: P1
```

---
