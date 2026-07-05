# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §3
# [MODULE] zephyr.security.access_control.blueprint_fidelity
# [DOMAIN] D_SECURITY
# [DEPENDENCIES]
# [CONSUMERS] tests/agent_rbac/test_crosscut_d.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] field count mismatch always detected; match=True only when expected==actual
# [MODIFY-GUARD] blueprint.md §3
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check_field_count never raises; returns FidelityCheck
# [TESTS] tests/agent_rbac/test_crosscut_d.py
# [A_module] module_id=MOD-SEC_blueprint_fidelity | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""BlueprintFidelity — 蓝图保真度检查.

依据蓝图 MOD-INF-018 §3:
- 检查模块实现与蓝图定义的字段数是否一致
- 检测蓝图漂移
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class FidelityCheck:
    """保真度检查结果."""

    module: str = ""
    expected: int = 0
    actual: int = 0
    match: bool = False


class BlueprintFidelity:
    """蓝图保真度检查器."""

    def check_field_count(self, module: str, expected: int, actual: int) -> FidelityCheck:
        """检查模块字段数是否匹配蓝图定义.

        Args:
            module: 模块名称
            expected: 蓝图定义的期望字段数
            actual: 实际实现的字段数

        Returns:
            FidelityCheck 包含 match 标志
        """
        return FidelityCheck(
            module=module,
            expected=expected,
            actual=actual,
            match=(expected == actual),
        )


__all__ = [
    "BlueprintFidelity",
    "FidelityCheck",
]
