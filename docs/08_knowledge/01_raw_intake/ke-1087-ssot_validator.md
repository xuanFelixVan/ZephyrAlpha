---
module_id: KE-1002---ssot-validator-000
status: active
title: 7.1 与 SSoT Validator 的关系
category: governance
ttl: permanent
doc_type: knowledge_entry
---

# 7.1 与 SSoT Validator 的关系

7.1 与 SSoT Validator 的关系

`validate_ssot.py`（scaffold 产出）是 `validate_phase_*.py` 的底层工具：

```
validate_phase_transition.py
  ├── 内部调用 validate_ssot.py --check conflicts  （SSoT 矛盾检测）
  ├── 内部调用 validate_ssot.py --check phase_schema （frontmatter schema 检测）
  └── 独立实现的 criterion 评估器（runner for validator 字段）
```
