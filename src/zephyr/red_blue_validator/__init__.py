# [BLUEPRINT] MOD-INF-005 | docs/03_modules/_cross_layer/red-blue-validator/blueprint.md
# [MODULE] zephyr.red_blue_validator
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] zephyr.security.adversarial_validation
# [CONSUMERS] tests/audit/test_audit_red_blue_e2e.py (import_time measurement)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] re-export shim for zephyr.security.adversarial_validation
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError if adversarial_validation unavailable
# [TESTS] tests/audit/test_audit_red_blue_e2e.py
# [A_module] module_id=MOD-SEC-red_blue_validator | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# 治本（裁定#18）：测试契约 (test_audit_red_blue_e2e.TestSteadyStateE2E) 直接调用
# _import_time("zephyr.red_blue_validator")，需要该包可导入。本文件为 re-export shim，
# 从 zephyr.security.adversarial_validation 重新导出关键符号。
"""red_blue_validator — re-export shim for zephyr.security.adversarial_validation.

测试契约 (test_audit_red_blue_e2e.TestSteadyStateE2E::test_import_time_real_measurement)
直接调用 ss._import_time("zephyr.red_blue_validator")，要求该包可导入。
本包从 zephyr.security.adversarial_validation 重新导出关键符号。
"""

from zephyr.security.adversarial_validation.validator import RedBlueValidator  # noqa: F401
from zephyr.security.adversarial_validation.constitution_guard import (  # noqa: F401
    ConstitutionArticle,
    ConstitutionGuard,
    ConstitutionViolationError,
)

__all__ = [
    "RedBlueValidator",
    "ConstitutionArticle",
    "ConstitutionGuard",
    "ConstitutionViolationError",
]
