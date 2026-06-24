---
module_id: KE-2110------dim-discover-001-000
status: active
title: 3.4 发现维度（DIM-DISCOVER-001）
category: module_blueprint
---

# 3.4 发现维度（DIM-DISCOVER-001）

3.4 发现维度（DIM-DISCOVER-001）

```yaml
dimension:
  dim_id: DIM-DISCOVER-001
  name: "全量资产发现与孤儿检测"
  axis: discovery
  description: "枚举全部磁盘文件，对比全部注册表，找出孤儿和僵尸引用"
  target_filter: "all assets"
  checks:
    - check_id: "audit_registration"
      severity: RED
      auto_fixable: false          # 孤儿不能自动注册——需要先判定价值
    - check_id: "zombie_reference"
      severity: RED
      auto_fixable: true           # 僵尸引用可以直接从注册表删除
    - check_id: "missing_all"
      severity: YELLOW
      auto_fixable: true           # 缺 __all__ 可以自动补
  convergence_passes: 1
  max_total_passes: 3
```

---
