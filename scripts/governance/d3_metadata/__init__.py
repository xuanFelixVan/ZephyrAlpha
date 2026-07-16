# [BLUEPRINT] MOD-INF-005 | scripts/governance/d3_metadata/__init__.py | §
# [TTL] permanent
"""D3 元数据合规 — Markdown/YAML 文档元数据（frontmatter）合规性审计。

检查项：
- YAML frontmatter 必填字段（doc_type / status / version / title）
- 命名规范一致性校验
- 版本号 semver 格式 + 状态受控词表校验
- 登记表/注册表与索引文件一致性
"""

__all__ = [
    "assign_module_id",
    "check_frontmatter_metadata",
    "check_naming_convention",
    "check_registry_consistency",
    "deep_content_scanner",
    "detect_deprecated_overdue",
    "detect_skip_active_status",
    "detect_stale_version",
    "fix_dm411_bare_relative_imports",
    "fix_dm413_duplicate_test_names",
    "fix_n06_module_id_prefix",
    "fix_n12_ke_naming",
    "fix_n15_blueprint_path",
    "generate_derived_files",
    "generate_rule_catalog",
    "scan_deep_content",
    "validate_architecture",
    "validate_blueprint_provenance",
    "validate_blueprint_registry",
    "validate_cross_module_dependencies",
    "validate_derived_from",
    "validate_enum_consistency",
    "validate_frontmatter_values",
    "validate_module_id",
    "validate_no_duplicate_files",
    "validate_registry_master_index",
    "validate_ssot_status",
    "validate_superseded_by",
]
