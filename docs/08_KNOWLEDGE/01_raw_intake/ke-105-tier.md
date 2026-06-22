---
module_id: KE-096
title: 1.5.2 Tier 2：引用本注册表作为权威依据
category: documentation
---

# 1.5.2 Tier 2：引用本注册表作为权威依据

1.5.2 Tier 2：引用本注册表作为权威依据

以下文件**引用本注册表作为权威依据**，但不硬编码枚举值：

| 文件 | 引用方式 |
|------|---------|
| `.pre-commit-config.yaml` | GATE-15 配置段注释声明"权威依据：metadata_registry.yaml" |
| `scripts/governance/validate_ssot.py` | 使用注册表定义的字段名做校验 |
| `scripts/governance/validate_blueprint_provenance.py` | 校验 doc_type 和 provenance 字段 |
| `scripts/governance/validate_truth_source_cascade.py` | 使用 doc_type 等字段做真源级联校验 |
| `scripts/governance/check_naming_convention.py` | 使用 doc_type 命名规则 |
| `scripts/governance/archive_drafts_zone.py` | 使用 doc_type 和 status 字段 |
| `src/zephyr/hooks/ssot_guard.py` | 检查治理文件与注册表的一致性 |
