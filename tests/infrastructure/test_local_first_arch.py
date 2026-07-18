# [A_test] module_id: SRC-TST-1239 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-404 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.test_local_first_arch
# [INVARIANTS] LOCAL_FIRST.is_local_first() returns True by default
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_local_first_arch.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.infrastructure.a2a_protocol.local_first_arch import (
    LOCAL_FIRST,
    ComputeLocation,
    LocalFirstPolicy,
)


class TestComputeLocation:
    def test_all_locations(self):
        expected = {"LOCAL", "CLOUD_BACKFILL"}
        actual = {l.value for l in ComputeLocation}
        assert actual == expected


class TestLocalFirstPolicy:
    def test_creation_defaults(self):
        policy = LocalFirstPolicy()
        assert policy.all_compute == ComputeLocation.LOCAL
        assert policy.zero_cloud_dep is True

    def test_is_local_first_true(self):
        policy = LocalFirstPolicy()
        assert policy.is_local_first() is True

    def test_is_local_first_false_cloud_compute(self):
        policy = LocalFirstPolicy(all_compute=ComputeLocation.CLOUD_BACKFILL)
        assert policy.is_local_first() is False

    def test_is_local_first_false_cloud_dep(self):
        policy = LocalFirstPolicy(zero_cloud_dep=False)
        assert policy.is_local_first() is False

    def test_websocket_dep_set(self):
        assert LOCAL_FIRST.websocket_dep != ""

    def test_cloud_role_set(self):
        assert LOCAL_FIRST.cloud_role != ""


class TestLocalFirstConstant:
    def test_local_first_is_local_first(self):
        assert LOCAL_FIRST.is_local_first() is True

    def test_local_first_is_policy_instance(self):
        assert isinstance(LOCAL_FIRST, LocalFirstPolicy)


class TestBoundary:
    def test_policy_with_both_false_conditions(self):
        policy = LocalFirstPolicy(all_compute=ComputeLocation.CLOUD_BACKFILL, zero_cloud_dep=False)
        assert policy.is_local_first() is False
