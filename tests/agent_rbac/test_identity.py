# [A_test] module_id: MOD-GOV_identity | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §
# [MODULE] tests.agent_rbac.test_identity
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
测试 AgentIdentity — 身份模型
"""

from zephyr.security.access_control.identity import (
    ROLE_DEFAULT_PERMISSIONS,
    AgentIdentity,
    AgentRole,
    IDESource,
    MaturityLevel,
)


class TestMaturityLevel:
    def test_five_levels(self):
        levels = list(MaturityLevel)
        assert len(levels) == 5
        expected = ["L0_INTERN", "L1_JUNIOR", "L2_REGULAR", "L3_SENIOR", "L4_PRINCIPAL"]
        assert [l.value for l in levels] == expected

    def test_can_promote_one_level(self):
        agent = AgentIdentity(
            session_id="test-001",
            maturity=MaturityLevel.L0_INTERN,
        )
        assert agent.can_promote_to(MaturityLevel.L1_JUNIOR)

    def test_cannot_promote_two_levels(self):
        agent = AgentIdentity(
            session_id="test-002",
            maturity=MaturityLevel.L0_INTERN,
        )
        assert not agent.can_promote_to(MaturityLevel.L2_REGULAR)

    def test_can_promote_l4_to_l4(self):
        agent = AgentIdentity(
            session_id="test-003",
            maturity=MaturityLevel.L4_PRINCIPAL,
        )
        assert agent.can_promote_to(MaturityLevel.L4_PRINCIPAL)


class TestAgentIdentity:
    def test_default_values(self):
        agent = AgentIdentity(session_id="test-default")
        assert agent.maturity == MaturityLevel.L0_INTERN
        assert agent.role == AgentRole.WRITER
        assert agent.ide_source == IDESource.UNKNOWN
        assert agent.delegation_depth == 0

    def test_token_sign_and_verify(self):
        agent = AgentIdentity(session_id="test-token")
        secret = "test-secret-key"
        agent.sign_token(secret)
        assert agent.session_token
        assert agent.verify_token(secret)

    def test_token_verification_fails_with_wrong_secret(self):
        agent = AgentIdentity(session_id="test-token-2")
        agent.sign_token("secret-a")
        assert not agent.verify_token("secret-b")

    def test_has_permission_exact_match(self):
        agent = AgentIdentity(
            session_id="test-perm",
            permissions=["read:docs", "write:src"],
        )
        assert agent.has_permission("read:docs")
        assert not agent.has_permission("delete:docs")

    def test_has_permission_wildcard(self):
        agent = AgentIdentity(
            session_id="test-wildcard",
            permissions=["read:*"],
        )
        assert agent.has_permission("read:docs")
        assert agent.has_permission("read:src")
        assert not agent.has_permission("write:src")

    def test_get_tlb_limit(self):
        limits = {
            MaturityLevel.L0_INTERN: 100,
            MaturityLevel.L1_JUNIOR: 500,
            MaturityLevel.L2_REGULAR: 2000,
            MaturityLevel.L3_SENIOR: 10000,
            MaturityLevel.L4_PRINCIPAL: 50000,
        }
        for level, expected in limits.items():
            agent = AgentIdentity(
                session_id=f"test-tlb-{level.value}",
                maturity=level,
            )
            assert agent.get_tlb_limit() == expected

    def test_get_auto_guard_timeout(self):
        agent_l0 = AgentIdentity(
            session_id="test-ag-l0",
            maturity=MaturityLevel.L0_INTERN,
        )
        assert agent_l0.get_auto_guard_timeout() == 300


class TestAgentRole:
    def test_role_count(self):
        roles = list(AgentRole)
        # P1-3: Batch 1 合并后 7 成员（security 5 + shared REVIEWER + AUTONOMOUS_AGENT）
        # 回归测试固化历史行为（P1-1 例外②）
        assert len(roles) == 7
        expected_names = {"READER", "WRITER", "EXECUTOR", "ADMIN", "AUDITOR", "REVIEWER", "AUTONOMOUS_AGENT"}
        assert {r.name for r in roles} == expected_names

    def test_reader_has_read_permissions(self):
        perms = ROLE_DEFAULT_PERMISSIONS[AgentRole.READER]
        assert "read:docs" in perms
        assert "write:src" not in perms

    def test_admin_has_management_permissions(self):
        perms = ROLE_DEFAULT_PERMISSIONS[AgentRole.ADMIN]
        assert "manage:rbac" in perms
        assert "manage:kill_switch" in perms

    def test_all_roles_have_permissions_defined(self):
        for role in AgentRole:
            assert role in ROLE_DEFAULT_PERMISSIONS
            assert len(ROLE_DEFAULT_PERMISSIONS[role]) > 0
