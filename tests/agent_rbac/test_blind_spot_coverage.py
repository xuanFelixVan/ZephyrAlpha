# [BLUEPRINT] MOD-INF-018 | docs/03_modules/l01_infrastructure/agent-rbac/blueprint.md | §
# [MODULE] tests.agent_rbac.test_blind_spot_coverage
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
"""盲点覆盖测试."""
from __future__ import annotations

import pytest
from zephyr.agent_rbac.blind_spot_tracker import BlindSpotTracker


class TestBlindSpotCoverage:
    def test_detect_blind_spot(self):
        tracker = BlindSpotTracker()
        spot = tracker.detect("No coverage for agent-to-agent file transfer permission")
        assert spot.spot_id.startswith("BS-")
        assert spot.severity == "MEDIUM"

    def test_summary(self):
        tracker = BlindSpotTracker()
        tracker.detect("gap_1")
        tracker.detect("gap_2")
        summary = tracker.summary()
        assert summary["total_blind_spots"] == 2
        assert summary["unacknowledged"] == 2

    def test_acknowledge(self):
        tracker = BlindSpotTracker()
        spot = tracker.detect("need_review")
        result = tracker.acknowledge(spot.spot_id)
        assert result["acknowledged"] is True

        summary = tracker.summary()
        assert summary["unacknowledged"] == 0
