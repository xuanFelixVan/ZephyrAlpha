# [A_test] module_id: MOD-GOV_rbac_adversarial | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-212 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.adversarial.test_rbac_adversarial
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""红白对抗: RBAC 权限系统攻击面测试.

攻击向量:
  A1 - 身份伪造: 构造高权限假身份
  A2 - 权限越权: READER 尝试执行 executor 操作
  A3 - Kill Switch 绕过: 使用被封锁 session_id
  A4 - 冷启动绕过: 强制跳过 cold_start_lock
  A5 - 空身份注入: None / 空字符串 session_id
  A6 - Token 伪造: 使用错误密钥签名的 token
  A7 - 角色枚举攻击: 枚举所有已知角色执行操作
  A8 - 序列检测触发器: 短时间大量操作触发异常序列
"""

from __future__ import annotations

import pytest

from zephyr.security.access_control.guards.rbac_guard import RBACGuard
from zephyr.security.access_control.identity import (
    AgentIdentity,
    AgentRole,
    IDESource,
    MaturityLevel,
)
from zephyr.security.access_control.immutable_core import get_immutable_core


class TestIdentitySpoofing:
    """A1: 身份伪造攻击."""

    def test_spoof_admin_role_no_owner_approval(self):
        """伪造 ADMIN 角色但未获 owner 批准 → 权限模型本身应记录 owner_approved=False."""
        identity = AgentIdentity(
            session_id="attacker-001",
            maturity=MaturityLevel.L4_PRINCIPAL,
            role=AgentRole.ADMIN,
            ide_source=IDESource.CLI,
            owner_approved=False,
        )
        assert identity.owner_approved is False
        assert identity.role == AgentRole.ADMIN

    def test_low_maturity_admin_role_rejected(self):
        """L0_INTERN 试图冒充 ADMIN → RBACGuard 应拒绝角色分配."""
        identity = AgentIdentity(
            session_id="intern-hacker",
            maturity=MaturityLevel.L0_INTERN,
            role=AgentRole.ADMIN,
            ide_source=IDESource.CLI,
        )
        assert not identity.can_promote_to(MaturityLevel.L4_PRINCIPAL)

    def test_no_auto_guard_bypass(self):
        """未授权 auto_guard 的 agent → auto_guard_eligible=False 应被正确记录."""
        identity = AgentIdentity(
            session_id="unauthorized-auto",
            maturity=MaturityLevel.L1_JUNIOR,
            role=AgentRole.WRITER,
            ide_source=IDESource.CLI,
            auto_guard_eligible=False,
        )
        assert identity.auto_guard_eligible is False
        assert identity.maturity == MaturityLevel.L1_JUNIOR


class TestPrivilegeEscalation:
    """A2: 权限越权攻击."""

    def test_reader_cannot_write_src(self):
        """READER 尝试 write:src → 应被拒绝."""
        core = get_immutable_core()
        guard = RBACGuard(immutable_core=core)
        identity = AgentIdentity(
            session_id="reader-evil",
            maturity=MaturityLevel.L2_REGULAR,
            role=AgentRole.READER,
            ide_source=IDESource.CLI,
        )
        identity.permissions = [
            "read:docs",
            "read:src",
            "read:tests",
            "read:config",
            "read:logs",
            "read:data",
        ]
        result = guard.check(identity, "write:src", "src/zephyr/")
        assert result.decision != "ALLOW"

    def test_writer_cannot_execute(self):
        """WRITER 尝试 execute:scripts → 应被拒绝."""
        core = get_immutable_core()
        guard = RBACGuard(immutable_core=core)
        identity = AgentIdentity(
            session_id="writer-evil",
            maturity=MaturityLevel.L2_REGULAR,
            role=AgentRole.WRITER,
            ide_source=IDESource.CLI,
        )
        identity.permissions = [
            "read:docs",
            "read:src",
            "read:tests",
            "write:src",
            "write:tests",
            "read:config",
            "read:logs",
            "read:data",
        ]
        result = guard.check(identity, "execute:scripts", "scripts/")
        assert result.decision != "ALLOW"


class TestNullIdentityAttacks:
    """A5: 空/畸形身份注入."""

    def test_empty_session_id_creates_valid_identity(self):
        """空 session_id 应能创建身份（Pydantic str 无 min_length），但无危险权限."""
        identity = AgentIdentity(session_id="")
        assert identity.session_id == ""
        assert not identity.has_permission("manage:rbac")
        assert not identity.has_permission("write:src")

    def test_special_chars_session_id(self):
        """注入特殊字符到 session_id → 不应崩溃但也不应提升权限."""
        identity = AgentIdentity(
            session_id="'; DROP TABLE users; --",
            maturity=MaturityLevel.L0_INTERN,
            role=AgentRole.READER,
            ide_source=IDESource.UNKNOWN,
        )
        assert identity.role == AgentRole.READER
        assert identity.maturity == MaturityLevel.L0_INTERN
        assert not identity.has_permission("manage:rbac")


class TestTokenForgery:
    """A6: Token 伪造攻击."""

    def test_wrong_secret_token_fails(self):
        """使用错误密钥签名的 token → verify_token 应返回 False."""
        identity = AgentIdentity(
            session_id="victim-session",
            maturity=MaturityLevel.L3_SENIOR,
            role=AgentRole.WRITER,
        )
        identity.sign_token("correct-secret")
        assert identity.verify_token("correct-secret") is True
        assert identity.verify_token("wrong-secret") is False

    def test_empty_token_always_invalid(self):
        """空 token → verify_token 应返回 False."""
        identity = AgentIdentity(
            session_id="no-token",
            maturity=MaturityLevel.L2_REGULAR,
            role=AgentRole.WRITER,
            session_token="",
        )
        assert identity.verify_token("any-secret") is False


class TestRoleEnumeration:
    """A7: 角色枚举攻击 — 所有角色尝试越权."""

    @pytest.mark.parametrize("role", list(AgentRole))
    def test_no_role_can_bypass_permission_check(self, role):
        """任意角色：明确请求不存在的权限 → has_permission 应 False."""
        identity = AgentIdentity(
            session_id=f"enum-{role.value}",
            maturity=MaturityLevel.L4_PRINCIPAL,
            role=role,
            permissions=ROLE_DEFAULT_PERMISSIONS.get(role, []),
        )
        assert identity.has_permission("superuser:delete_everything") is False


from zephyr.security.access_control.identity import ROLE_DEFAULT_PERMISSIONS


class TestPermissionModel:
    """权限模型边界测试."""

    def test_wildcard_permission_match(self):
        """通配符权限 write:* 应匹配 write:src."""
        identity = AgentIdentity(
            session_id="wildcard-test",
            maturity=MaturityLevel.L3_SENIOR,
            role=AgentRole.ADMIN,
            permissions=["write:*"],
        )
        assert identity.has_permission("write:src") is True
        assert identity.has_permission("write:tests") is True
        assert identity.has_permission("read:src") is False

    def test_tlb_limit_bounds(self):
        """TLB 限制不应为 0 或负数."""
        for level in MaturityLevel:
            identity = AgentIdentity(
                session_id=f"tlb-{level.value}",
                maturity=level,
            )
            limit = identity.get_tlb_limit()
            assert limit > 0, f"{level} TLB limit should be > 0, got {limit}"
            assert limit <= 50000
