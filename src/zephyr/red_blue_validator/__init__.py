# [BLUEPRINT] MOD-INF-030 | docs/03_modules/_cross_layer/red_blue_validator/blueprint.md
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
# [A_module] module_id=MOD-INF-030 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# 治本（裁定#18 + 2026-07-18 表头修正）：测试契约 (test_audit_red_blue_e2e.TestSteadyStateE2E)
# 直接调用 ss._import_time("zephyr.red_blue_validator")，需要该包可导入。本文件为 re-export shim，
# 从 zephyr.security.adversarial_validation 重新导出关键符号。
"""

red_blue_validator — re-export shim for zephyr.security.adversarial_validation.

测试契约 (test_audit_red_blue_e2e.TestSteadyStateE2E::test_import_time_real_measurement)
直接调用 ss._import_time("zephyr.red_blue_validator")，要求该包可导入。
本包从 zephyr.security.adversarial_validation 重新导出关键符号。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: adversarial_validation 源模块 符号
#   fields: RedBlueValidator + ConstitutionArticle/ConstitutionGuard/ConstitutionViolationError
#   code: zephyr.security.adversarial_validation.validator L27 / constitution_guard L28
# 层: 算法
# - id: A1
#   name_zh: ① re-export shim 符号转发
#   name_en: __init__ 重导出
#   intro: 原样转发4个符号，保证 zephyr.red_blue_validator 包可导入
#   desc: 从 zephyr.security.adversarial_validation 两个子模块 import 4 符号并列入 __all__，无自有逻辑（L27-39）
#   inputs: I1
#   outputs: 4 个公共符号
#   invariant: re-export shim，不包含任何自有实现
# 层: 输出
# - id: O1
#   name_zh: 红蓝对抗验证公共符号
#   name_en: RedBlueValidator + ConstitutionGuard 等
#   intro: 对外提供红蓝验证器与宪法守卫类
#   downstream: tests/audit/test_audit_red_blue_e2e.py（import_time 测量，# [CONSUMERS] 头）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from zephyr.security.adversarial_validation.constitution_guard import (  # noqa: F401
    ConstitutionArticle,
    ConstitutionGuard,
    ConstitutionViolationError,
)
from zephyr.security.adversarial_validation.validator import RedBlueValidator  # noqa: F401

__all__ = [
    "RedBlueValidator",
    "ConstitutionArticle",
    "ConstitutionGuard",
    "ConstitutionViolationError",
]
