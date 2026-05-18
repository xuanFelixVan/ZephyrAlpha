# [BLUEPRINT] DOM-GOV-001 | docs/03_modules/_domain-governance/blueprint.md | §
# [MODULE] tests.governance.test_gct_005_drift_to_rollback
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
"""G-CT-005 — Drift → Rollback 集成测试."""
from __future__ import annotations

import pytest


class TestGCT005DriftToRollback:
    """验证 drift_detector/events.py 的 DriftEvent 可被 rollback/drift_fix.py 处理."""

    def test_drift_event_creatable(self):
        from zephyr.behavioral_auditor.events import DriftEvent
        e = DriftEvent(drift_id="D001", target="test_config")
        assert e.drift_id == "D001"

    def test_drift_fix_handler_accepts_event(self):
        from zephyr.behavioral_auditor.events import DriftEvent
        from zephyr.rollback.drift_fix import DriftFixHandler
        e = DriftEvent(drift_id="D001", target="test_config")
        handler = DriftFixHandler()
        result = handler.on_drift_fix(e)
        assert result is not None

    def test_drift_state_enum(self):
        from zephyr.behavioral_auditor.events import DriftState, DriftType
        assert DriftState.DETECTED is not None
        assert DriftType.CONFIG_DRIFT is not None
