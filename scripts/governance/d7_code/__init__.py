# [BLUEPRINT] MOD-INF-005 | scripts/governance/d7_code/__init__.py | §
# [TTL] permanent
"""D7 代码质量 — Python 代码静态分析与质量合规审计。

检查项：
- 类型注解完整性
- 未使用导入检测
- 导入风格一致性
- 测试覆盖率校验
- docstring 存在性
"""

__all__ = [
    "check_ai_capability_boundary",
    "check_encoding",
    "check_idempotency",
    "check_pit_compliance",
    "detect_absolute_path_hardcoding",
    "detect_direct_llm_calls",
    "detect_missing_encoding",
    "detect_pydantic_any_fields",
    "detect_silent_degradation",
    "validate_contracts_purity",
    "validate_docstring_coverage",
    "validate_fle_action_metadata",
    "validate_fle_imports",
    "validate_import_style",
    "validate_init_all",
    "validate_kb_write_provenance",
    "validate_python_syntax",
    "validate_test_assertion_depth",
    "validate_test_coverage",
    "validate_type_annotation_coverage",
    "validate_unused_imports",
]
