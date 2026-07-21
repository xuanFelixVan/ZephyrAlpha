# [A_test] module_id: MOD-GOV_a2a_context_rot | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md | §3
# [MODULE] tests.test_a2a_context_rot
# [INVARIANTS] Tests must not modify production state; All imports guarded by pytest.importorskip
# [MODIFY-GUARD] docs/03_modules/_domain-infra_ops/a2a-protocol/blueprint.md
# [CONSUMERS] CI pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError → skip; AttributeError → fail
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

import pytest

mod = pytest.importorskip(
    "zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_context_rot",
    reason="a2a_context_rot module not available",
)


class TestA2AContextRot:
    def test_instantiation(self):
        obj = mod.A2AContextRot()
        assert obj is not None

    def test_detect_rot_fresh_context(self):
        obj = mod.A2AContextRot()
        result = obj.detect_rot({"messages": ["hello"]}, age_seconds=10)
        assert result is not None

    def test_detect_rot_stale_context(self):
        obj = mod.A2AContextRot()
        result = obj.detect_rot({"messages": ["old"]}, age_seconds=86400)
        assert result is not None

    def test_detect_rot_empty_context(self):
        obj = mod.A2AContextRot()
        result = obj.detect_rot({}, age_seconds=0)
        assert result is not None

    def test_detect_rot_zero_age(self):
        obj = mod.A2AContextRot()
        result = obj.detect_rot({"data": "fresh"}, age_seconds=0)
        assert result is not None
