---
module_id: KE-1016------t-2-17-003
status: active
title: 7.5 YAML schema 校验工具（T-2-17 配套交付）
category: governance
ttl: permanent
---

# 7.5 YAML schema 校验工具（T-2-17 配套交付）

7.5 YAML schema 校验工具（T-2-17 配套交付）

- **路径**：`scripts/governance/validate_gate_yaml.py`
- **调用**：`python -m scripts.governance.validate_gate_yaml`
- **pre-commit 挂载**：`.pre-commit-config.yaml` 需新增 hook，作用域 `src/zephyr/gates/*.yaml`
- **产物**：`.audit_cache/gate_yaml_validation.json`（`type: generated, ttl: 7d`）

---
