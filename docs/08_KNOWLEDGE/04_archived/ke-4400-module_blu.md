---
module_id: KE-4236-----------------3-003
title: 9.2 交叉覆盖矩阵（目标：每文件 ≥ 3 维度）
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 9.2 交叉覆盖矩阵（目标：每文件 ≥ 3 维度）

9.2 交叉覆盖矩阵（目标：每文件 ≥ 3 维度）

| 文件示例 | DISCOVER | TYPE | DIR | FIELD | RULE | DUP | SSoT | SEMANTIC | 覆盖 |
|---------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `scripts/governance/audit_registration.py` | ✅ | ✅001 | ✅001 | | | ✅001 | | | 4 |
| `src/zephyr/gates/_registry.yaml` | ✅ | ✅002 | | ✅001 | ✅001 | | ✅001 | | 5 |
| `project_rules.md` | ✅ | ✅003 | | | ✅001 | | | ✅001 | 4 |
| `docs/registry_of_registries.yaml` | ✅ | ✅003 | | ✅001 | ✅001 | | ✅001 | ✅001 | 6 |
| `src/zephyr/core/models.py` | ✅ | ✅001 | | | | ✅001 | | | 3 |

---
