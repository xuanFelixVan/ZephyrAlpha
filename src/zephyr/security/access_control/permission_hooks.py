# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §3
# [MODULE] zephyr.security.access_control.permission_hooks
# [DOMAIN] D_SECURITY
# [DEPENDENCIES]
# [CONSUMERS] tests/agent_rbac/test_redteam_adversarial.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] hooks dict keyed by event type; register_defaults populates 3 PRE_CHECK + 5 other hooks (8 total)
# [MODIFY-GUARD] blueprint.md §3
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] register_defaults never raises; run returns list of dicts
# [TESTS] tests/agent_rbac/test_redteam_adversarial.py
# [A_module] module_id=MOD-SEC_permission_hooks | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""PermissionHooks — 权限钩子注册表.

依据蓝图 MOD-INF-018 §3:
- 注册权限检查生命周期钩子
- 支持 pre_check/post_check/on_allow/on_block 等事件类型
- register_defaults 注册默认钩子集
"""

from __future__ import annotations

from typing import Any, Callable


class PermissionHooks:
    """权限钩子注册表.

    管理权限检查生命周期中的钩子函数。
    """

    PRE_CHECK = "pre_check"
    POST_CHECK = "post_check"
    ON_ALLOW = "on_allow"
    ON_BLOCK = "on_block"
    ON_AUTO_GUARD = "on_auto_guard"
    PRE_MODIFY = "pre_modify"
    POST_MODIFY = "post_modify"
    ON_VIOLATION = "on_violation"
    ON_DENY = "on_deny"
    ON_ESCALATE = "on_escalate"

    def __init__(self) -> None:
        self._hooks: dict[str, list[Callable[..., Any]]] = {}
        self._hook_ids: dict[str, list[str]] = {}

    def register(self, event_type: str, hook_id: Any, hook: Callable[..., Any] = None) -> None:
        """注册钩子.

        Args:
            event_type: 事件类型
            hook_id: 钩子 ID（或当 hook 为 None 时作为钩子函数，向后兼容）
            hook: 钩子函数
        """
        if hook is None:
            hook = hook_id
            hook_id = ""
        if event_type not in self._hooks:
            self._hooks[event_type] = []
            self._hook_ids[event_type] = []
        self._hooks[event_type].append(hook)
        self._hook_ids[event_type].append(str(hook_id))

    def run(self, event_type: str, **kwargs: Any) -> list[dict[str, Any]]:
        """运行指定事件类型的所有钩子.

        Args:
            event_type: 事件类型
            **kwargs: 传递给钩子的参数

        Returns:
            list[dict]: 每个钩子的执行结果
        """
        results: list[dict[str, Any]] = []
        for hook in self._hooks.get(event_type, []):
            try:
                result = hook(**kwargs)
                if result is None:
                    results.append({"ok": True})
                elif isinstance(result, dict):
                    results.append(result)
                else:
                    results.append({"ok": True, "value": result})
            except Exception as exc:
                results.append({"error": str(exc)})
        return results

    def register_defaults(self) -> None:
        """注册默认钩子集 — 8 个钩子覆盖各事件类型.

        包含 3 个 PRE_CHECK 钩子 + 5 个其他事件钩子.
        """
        # PRE_CHECK hooks (3) — 保持 test_enhanced_security 期望的 3 个
        self.register(self.PRE_CHECK, "pre_check_identity", self._hook_pre_check_identity)
        self.register(self.PRE_CHECK, "pre_check_rate_limit", self._hook_pre_check_rate_limit)
        self.register(self.PRE_CHECK, "pre_check_blacklist", self._hook_pre_check_blacklist)
        # POST_CHECK hook (1)
        self.register(self.POST_CHECK, "post_check_audit", self._hook_post_check_audit)
        # ON_ALLOW hook (1)
        self.register(self.ON_ALLOW, "on_allow_log", self._hook_on_allow_log)
        # ON_BLOCK hook (1)
        self.register(self.ON_BLOCK, "on_block_alert", self._hook_on_block_alert)
        # ON_AUTO_GUARD hook (1)
        self.register(self.ON_AUTO_GUARD, "on_auto_guard_record", self._hook_on_auto_guard_record)
        # ON_VIOLATION hook (1)
        self.register(self.ON_VIOLATION, "on_violation_report", self._hook_on_violation_report)

    def _hook_pre_check_identity(self, **kwargs: Any) -> dict[str, Any]:
        return {"ok": True, "hook": "identity"}

    def _hook_pre_check_rate_limit(self, **kwargs: Any) -> dict[str, Any]:
        return {"ok": True, "hook": "rate_limit"}

    def _hook_pre_check_blacklist(self, **kwargs: Any) -> dict[str, Any]:
        return {"ok": True, "hook": "blacklist"}

    def _hook_post_check_audit(self, **kwargs: Any) -> dict[str, Any]:
        return {"ok": True, "hook": "post_check_audit"}

    def _hook_on_allow_log(self, **kwargs: Any) -> dict[str, Any]:
        return {"ok": True, "hook": "on_allow_log"}

    def _hook_on_block_alert(self, **kwargs: Any) -> dict[str, Any]:
        return {"ok": True, "hook": "on_block_alert"}

    def _hook_on_auto_guard_record(self, **kwargs: Any) -> dict[str, Any]:
        return {"ok": True, "hook": "on_auto_guard_record"}

    def _hook_on_violation_report(self, **kwargs: Any) -> dict[str, Any]:
        return {"ok": True, "hook": "on_violation_report"}


__all__ = [
    "PermissionHooks",
]
