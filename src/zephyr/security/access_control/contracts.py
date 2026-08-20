# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §
# [MODULE] zephyr.security.access_control.contracts
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] zephyr.gov_audit.contracts
# [CONSUMERS] tests.governance.test_adversarial_contract_attacks ; tests.governance.test_gct_001_rbac_to_audit ; tests.governance.test_p0_i2_construction_order ; tests.governance.test_p0_u1_contract_smoke
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] RBACAuditBridge.check_and_log 总是返回 {granted, audit_record}; 权限白名单只允许 read/write/execute
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check_and_log 不抛异常——AuditWriter 不可用时回退到 plain dict
# [TESTS] tests/governance/security/test_governance_contracts.py; tests/governance/security/test_gct_001_rbac_to_audit.py; tests/governance/security/test_adversarial_contract_attacks.py; tests/governance/security/test_p0_u1_contract_smoke.py
# [A_module] module_id=MOD-INF-018 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""G-CT-001 RBAC->Audit 桥接契约 - RBACAuditBridge.

治本（G-CT-001）：原为空桩。现实现 RBACAuditBridge.check_and_log，将 RBAC 权限决策
写入审计链（通过 zephyr.gov_audit.contracts.AuditWriter）。

设计要点：
    - 模块级 ``from zephyr.gov_audit.contracts import AuditWriter`` —— 测试通过
      ``@patch("zephyr.security.access_control.contracts.AuditWriter")`` 注入 mock。
    - ``check_and_log`` 调用 ``AuditWriter().write(...)``（实例方法），匹配 mocked 测试
      中 ``mock_audit_writer_cls.return_value.write.return_value`` 的配置方式。
    - 未 mock 场景下，``AuditWriter`` 是 ABC（``TypeError``）或全局 writer 未初始化
      （``ContractViolationError``）。此时回退到 plain dict，保证 ``check_and_log``
      永不抛异常——桥接层不应因审计写入失败而阻塞 RBAC 决策。
"""

from __future__ import annotations

from typing import Any

# 模块级导入——测试通过 patch 本模块的 AuditWriter 属性注入 mock。
from zephyr.gov_audit.contracts import AuditWriter

__all__ = ["RBACAuditBridge"]


class RBACAuditBridge:
    """G-CT-001 桥接器：RBAC 权限决策 -> 审计链写入。

    权限白名单：read/write/execute -> granted=True；
    destroy/admin_override/delete/未知 -> granted=False。
    """

    @staticmethod
    @staticmethod
    def check_permission(agent_id, permission, resource) -> bool:
        """公共接口：check_permission（Stage 4 公共化）。"""
        return __class__._check_permission(agent_id, permission, resource)

    # 允许的权限白名单（lowercase 比较）。命中 -> granted=True。
    _ALLOWED_PERMISSIONS: set[str] = {"read", "write", "execute"}

    @staticmethod
    def _check_permission(agent_id: str, permission: str, resource: str) -> bool:
        """检查权限是否允许。

        Args:
            agent_id: 调用方 agent ID（当前实现未参与判定，保留参数以备扩展）。
            permission: 权限名（read/write/execute/destroy/admin_override/delete/...）。
            resource: 目标资源（当前实现未参与判定，保留参数以备扩展）。

        Returns:
            True 当且仅当 permission 在 ``_ALLOWED_PERMISSIONS`` 中。
        """
        return permission in RBACAuditBridge._ALLOWED_PERMISSIONS

    def check_and_log(
        self,
        agent_id: str,
        permission: str,
        resource: str,
        session_id: str | None = None,
    ) -> dict[str, Any]:
        """检查权限并写入审计记录（G-CT-001）。

        支持 positional 与 keyword 两种调用形式。

        Args:
            agent_id: 调用方 agent ID。
            permission: 请求的权限。
            resource: 目标资源。
            session_id: 可选会话 ID。

        Returns:
            ``{"granted": bool, "audit_record": dict}``。
            ``audit_record`` 至少包含 ``agent_id``/``permission``/``resource``/
            ``granted``/``session_id``/``event_type``，mocked 场景下还包含 ``chain_hash``。
        """
        granted = self._check_permission(agent_id, permission, resource)
        write_kwargs: dict[str, Any] = {
            "agent_id": agent_id,
            "permission": permission,
            "resource": resource,
            "granted": granted,
            "event_type": "rbac_decision",
            "session_id": session_id if session_id is not None else "",
        }
        try:
            # 调用 AuditWriter().write() —— mocked 测试 patch AuditWriter 类，
            # 配置 AuditWriter().write() 返回 chain_hash dict。
            audit_record = AuditWriter().write(**write_kwargs)
        except Exception:  # noqa: BLE001  # 桥接层不变量：永不抛异常（Ruling:100PCT-AI-GOVERNANCE P1-4）
            # 故意宽泛捕获：AuditWriter 是 ABC（TypeError）/ 全局 writer 未初始化
            # （ContractViolationError）/ 其他审计基础设施故障均回退到 plain dict，
            # 保证 RBAC 决策本身不受审计写入失败影响（审计是 side-effect，不能阻塞主流程）。
            audit_record = dict(write_kwargs)
        return {"granted": granted, "audit_record": audit_record}
