# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §3
# [MODULE] zephyr.security.access_control.exceptions
# [DOMAIN] D_SECURITY
# [DEPENDENCIES]
# [CONSUMERS] tests/agent_rbac/test_exceptions_agent_rbac.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] all errors inherit AgentRbacError; layer/rule_id have sensible defaults
# [MODIFY-GUARD] blueprint.md §3
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] construction never raises; all fields have defaults
# [TESTS] tests/agent_rbac/test_exceptions_agent_rbac.py
# [A_module] module_id=MOD-SEC_exceptions | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""AgentRbac 异常类型.

依据蓝图 MOD-INF-018 §3:
- AgentRbacError: 基类
- PermissionDeniedError: 权限拒绝
- ColdStartLockedError: 冷启动锁定
- OverrideTokenExpiredError: 覆盖令牌过期
- KillSwitchTrippedError: 紧急开关触发
- DegradationBlockedError: 降级阻断
"""

from __future__ import annotations


class AgentRbacError(Exception):
    """Agent RBAC 异常基类."""

    error_code = "ZA-SC-0023"

    def __init__(self, *args, error_code: str | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        if error_code is not None:
            self.error_code = error_code


class PermissionDeniedError(AgentRbacError):
    """权限拒绝异常.

    Attributes:
        operation: 被拒绝的操作
        layer: 检查层
        rule_id: 触发的规则 ID
    """

    error_code = "ZA-SC-0024"

    def __init__(
        self,
        message: str = "",
        *,
        operation: str = "",
        layer: str = "",
        rule_id: str = "",
        error_code: str | None = None,
    ) -> None:
        super().__init__(message)
        self.operation = operation
        self.layer = layer
        self.rule_id = rule_id
        if error_code is not None:
            self.error_code = error_code


class ColdStartLockedError(AgentRbacError):
    """冷启动锁定异常.

    Attributes:
        layer: 检查层
        rule_id: 触发的规则 ID
    """

    error_code = "ZA-SC-0025"

    def __init__(
        self,
        message: str = "",
        *,
        layer: str = "L1",
        rule_id: str = "CSL-001",
        error_code: str | None = None,
    ) -> None:
        super().__init__(message)
        self.layer = layer
        self.rule_id = rule_id
        if error_code is not None:
            self.error_code = error_code


class OverrideTokenExpiredError(AgentRbacError):
    """覆盖令牌过期异常.

    Attributes:
        issued_at: 令牌签发时间
        layer: 检查层
    """

    error_code = "ZA-SC-0026"

    def __init__(
        self,
        message: str = "",
        *,
        issued_at: float = 0.0,
        layer: str = "L1",
        error_code: str | None = None,
    ) -> None:
        super().__init__(message)
        self.issued_at = issued_at
        self.layer = layer
        if error_code is not None:
            self.error_code = error_code


class KillSwitchTrippedError(AgentRbacError):
    """紧急开关触发异常.

    Attributes:
        trigger: 触发原因
        layer: 检查层
    """

    error_code = "ZA-SC-0027"

    def __init__(
        self,
        message: str = "",
        *,
        trigger: str = "",
        layer: str = "L0",
        error_code: str | None = None,
    ) -> None:
        super().__init__(message)
        self.trigger = trigger
        self.layer = layer
        if error_code is not None:
            self.error_code = error_code


class DegradationBlockedError(AgentRbacError):
    """降级阻断异常.

    Attributes:
        layer: 检查层
        rule_id: 触发的规则 ID
    """

    error_code = "ZA-SC-0028"

    def __init__(
        self,
        message: str = "",
        *,
        layer: str = "L0",
        rule_id: str = "DEG-001",
        error_code: str | None = None,
    ) -> None:
        super().__init__(message)
        self.layer = layer
        self.rule_id = rule_id
        if error_code is not None:
            self.error_code = error_code


__all__ = [
    "AgentRbacError",
    "ColdStartLockedError",
    "DegradationBlockedError",
    "KillSwitchTrippedError",
    "OverrideTokenExpiredError",
    "PermissionDeniedError",
]
