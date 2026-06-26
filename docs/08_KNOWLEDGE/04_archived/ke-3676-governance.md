---
module_id: KE-3676
title: 2.2 三层物理位置速查
category: governance
ttl: permanent
doc_type: knowledge_entry
---

# 2.2 三层物理位置速查

2.2 三层物理位置速查

> **详细路径清单** → See `architecture_model/scripts/scripts_model.yaml`（governance/arch_guard/quality 三域）

| 层 | 关键物理位置 | 代表产物 |
|---|---|---|
| **Policy** | `docs/01_policies_and_standards/` · KB:decisions namespace · `.cursor/rules/` · `.trae/rules/` · `AGENTS.md` | 规则文档、KBG-0001~0041（33 VERIFIED）、AI 协作规则 |
| **Factory** | `scripts/arch_guard/` · `scripts/governance/` · `scripts/quality/` · `pyproject.toml` | 25 条 F 函数、import_linter、ruff.toml/mypy.ini/bandit.yaml |
| **Runtime** | `.pre-commit-config.yaml` · `.github/workflows/` · `src/zephyr/compliance/` · `scripts/governance/audit_log/` · `scripts/governance/opa/` · `.metadata/` | pre-commit hooks、CI Gate、kill_switch、OPA policies |
