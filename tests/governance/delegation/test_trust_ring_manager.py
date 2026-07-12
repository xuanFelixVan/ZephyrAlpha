# [A_test] module_id: SRC-TST-1771 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain_autonomy_perm/budget_enforcer/blueprint.md | §
# [MODULE] tests.test_trust_ring_manager
# [INVARIANTS] R0 has grant_trust/revoke_trust; R3 has view_summary only
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.gov_audit.trust_ring_manager import (
    PREMISSION_MAP,
    RING_LABELS,
    RingLevel,
    TrustRingManager,
    TrustSignature,
)


@pytest.fixture
def tmp_key_file(tmp_path, monkeypatch):
    key_path = str(tmp_path / ".zephyr_secure" / "trust_keys.json")
    monkeypatch.setattr(TrustRingManager, "_KEY_FILE", key_path)
    return key_path


@pytest.fixture
def manager(tmp_key_file):
    return TrustRingManager()


class TestRingLevel:
    def test_ring_values(self):
        assert RingLevel.R0_OWNER == 0
        assert RingLevel.R1_ADMIN == 1
        assert RingLevel.R2_AGENT == 2
        assert RingLevel.R3_OBSERVER == 3

    def test_ring_labels(self):
        assert RING_LABELS[RingLevel.R0_OWNER] == "owner"
        assert RING_LABELS[RingLevel.R3_OBSERVER] == "observer"


class TestPermissionMap:
    def test_owner_has_grant_trust(self):
        assert "grant_trust" in PREMISSION_MAP[RingLevel.R0_OWNER]

    def test_owner_has_revoke_trust(self):
        assert "revoke_trust" in PREMISSION_MAP[RingLevel.R0_OWNER]

    def test_admin_no_grant_trust(self):
        assert "grant_trust" not in PREMISSION_MAP[RingLevel.R1_ADMIN]

    def test_agent_permissions(self):
        assert "view_own" in PREMISSION_MAP[RingLevel.R2_AGENT]
        assert "use_model" in PREMISSION_MAP[RingLevel.R2_AGENT]

    def test_observer_minimal(self):
        assert "view_summary" in PREMISSION_MAP[RingLevel.R3_OBSERVER]


class TestTrustRingManager:
    def test_instantiation(self, manager):
        assert isinstance(manager, TrustRingManager)

    def test_register_identity(self, manager):
        key_hash = manager.register_identity("test-user", RingLevel.R2_AGENT)
        assert isinstance(key_hash, str)
        assert len(key_hash) == 64
        assert manager.get_ring("test-user") == RingLevel.R2_AGENT

    def test_can_owner_grant_trust(self, manager):
        manager.register_identity("owner", RingLevel.R0_OWNER)
        assert manager.can("owner", "grant_trust") is True

    def test_can_agent_no_grant_trust_directly(self, manager):
        manager.register_identity("agent", RingLevel.R2_AGENT)
        assert "grant_trust" not in PREMISSION_MAP[RingLevel.R2_AGENT]

    def test_can_escalation_allows_higher_ring_actions(self, manager):
        manager.register_identity("agent", RingLevel.R2_AGENT)
        assert manager.can("agent", "grant_trust") is True

    def test_can_owner_all_actions(self, manager):
        manager.register_identity("owner", RingLevel.R0_OWNER)
        assert manager.can("owner", "modify_budget") is True
        assert manager.can("owner", "view_all") is True
        assert manager.can("owner", "audit_all") is True

    def test_grant_by_owner(self, manager):
        manager.register_identity("owner", RingLevel.R0_OWNER)
        sig = manager.grant("owner", "new-agent", RingLevel.R2_AGENT)
        assert sig is not None
        assert isinstance(sig, TrustSignature)
        assert manager.get_ring("new-agent") == RingLevel.R2_AGENT

    def test_grant_by_admin_to_lower_ring(self, manager):
        manager.register_identity("admin", RingLevel.R1_ADMIN)
        sig = manager.grant("admin", "someone", RingLevel.R2_AGENT)
        assert sig is not None
        assert manager.get_ring("someone") == RingLevel.R2_AGENT

    def test_grant_to_higher_ring_fails(self, manager):
        manager.register_identity("admin", RingLevel.R1_ADMIN)
        sig = manager.grant("admin", "intruder", RingLevel.R0_OWNER)
        assert sig is None

    def test_revoke_by_owner(self, manager):
        manager.register_identity("owner", RingLevel.R0_OWNER)
        manager.register_identity("target", RingLevel.R2_AGENT)
        result = manager.revoke("owner", "target")
        assert result is True
        assert manager.get_ring("target") == RingLevel.R3_OBSERVER

    def test_revoke_owner_fails(self, manager):
        manager.register_identity("owner", RingLevel.R0_OWNER)
        manager.register_identity("super-owner", RingLevel.R0_OWNER)
        result = manager.revoke("super-owner", "owner")
        assert result is False

    def test_revoke_by_admin_succeeds_via_escalation(self, manager):
        manager.register_identity("admin", RingLevel.R1_ADMIN)
        manager.register_identity("target", RingLevel.R2_AGENT)
        result = manager.revoke("admin", "target")
        assert result is True

    def test_get_ring_unknown_identity(self, manager):
        assert manager.get_ring("unknown") == RingLevel.R3_OBSERVER

    def test_verify_returns_signature(self, manager):
        manager.register_identity("agent", RingLevel.R2_AGENT)
        sig = manager.verify("agent", "execute")
        assert sig is not None
        assert sig.identity == "agent"
        assert sig.action == "execute"

    def test_verify_empty_action_returns_none(self, manager):
        manager.register_identity("agent", RingLevel.R2_AGENT)
        sig = manager.verify("agent", "")
        assert sig is None

    def test_recent_grants(self, manager):
        manager.register_identity("owner", RingLevel.R0_OWNER)
        manager.grant("owner", "user1", RingLevel.R2_AGENT)
        manager.grant("owner", "user2", RingLevel.R1_ADMIN)
        grants = manager.recent_grants()
        assert len(grants) >= 2

    def test_active_identities(self, manager):
        manager.register_identity("user-a", RingLevel.R2_AGENT)
        manager.register_identity("user-b", RingLevel.R1_ADMIN)
        identities = manager.active_identities()
        assert "user-a" in identities
        assert "user-b" in identities


class TestBoundaryCases:
    def test_can_unknown_identity(self, manager):
        assert manager.can("unknown", "view_summary") is True

    def test_can_unknown_modify_budget_via_escalation(self, manager):
        assert manager.can("unknown", "modify_budget") is True

    def test_register_same_identity_overwrites(self, manager):
        manager.register_identity("user", RingLevel.R2_AGENT)
        manager.register_identity("user", RingLevel.R1_ADMIN)
        assert manager.get_ring("user") == RingLevel.R1_ADMIN

    def test_grant_nonexistent_granter(self, manager):
        sig = manager.grant("nonexistent", "target", RingLevel.R2_AGENT)
        assert sig is None
