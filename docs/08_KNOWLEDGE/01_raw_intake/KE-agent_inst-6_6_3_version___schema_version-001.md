---
module_id: KE-agent_inst-6_6_3_version___schema_version-001
title: 6.6.3 version 与 schema_version 规范
category: agent_instruction
---

# 6.6.3 version 与 schema_version 规范

6.6.3 version 与 schema_version 规范

- YAML 登记表可以有 `schema_version` 作为版本字段
- `validate_architecture.py` 会自动将 `schema_version` 映射为 `version` 进行格式校验
- `version` 必须是 semver 格式（`X.Y.Z`），禁止使用 `X.Y` 格式
