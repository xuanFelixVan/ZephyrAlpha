# [A_test] module_id: SRC-TST-0128 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-285 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.governance.test_gct_005_drift_to_rollback
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""G-CT-005 — Drift → Rollback 集成测试."""

from __future__ import annotations


class TestGCT005DriftToRollback:
    """验证 drift-detector/events.py 的 ManagedDriftEvent 可被 rollback/drift_fix.py 处理."""

    def test_drift_event_creatable(self):
        from zephyr.gov_drift.events import ManagedDriftEvent

        e = ManagedDriftEvent(drift_id="D001", target="test_config")
        assert e.drift_id == "D001"

    def test_drift_fix_handler_accepts_event(self):
        from zephyr.governance.drift_fix import DriftFixHandler
        from zephyr.gov_drift.events import ManagedDriftEvent

        e = ManagedDriftEvent(drift_id="D001", target="test_config")
        handler = DriftFixHandler()
        result = handler.on_drift_fix(e)
        assert result is not None

    def test_drift_state_enum(self):
        from zephyr.gov_drift.events import ManagedDriftState, DriftType

        assert ManagedDriftState.DETECTED is not None
        assert DriftType.CONFIG_DRIFT is not None
