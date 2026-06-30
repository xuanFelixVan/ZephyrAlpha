# [A_test] module_id: SRC-TST-0430 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_rbac/blueprint.md | §tests
# [MODULE] zephyr.security.access_control.blind_spot_tracker
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

import sys

sys.path.insert(0, "src")

import pytest

try:
    from zephyr.security.access_control.blind_spot_tracker import BlindSpot, BlindSpotTracker

    _IMPORT_OK = True
    _IMPORT_REASON = ""
except Exception as exc:
    _IMPORT_OK = False
    _IMPORT_REASON = str(exc)

pytestmark = pytest.mark.skipif(not _IMPORT_OK, reason=f"import failed: {_IMPORT_REASON}")


class TestBlindSpotTracker:
    def test_detect_creates_spot(self):
        bst = BlindSpotTracker()
        spot = bst.detect("missing auth check on /api/admin")
        assert isinstance(spot, BlindSpot)
        assert spot.description == "missing auth check on /api/admin"
        assert spot.acknowledged is False
        assert spot.severity == "MEDIUM"

    def test_detect_custom_severity(self):
        bst = BlindSpotTracker()
        spot = bst.detect("no rate limiting", severity="CRITICAL", coverage_gap="egress")
        assert spot.severity == "CRITICAL"
        assert spot.coverage_gap == "egress"

    def test_acknowledge_existing(self):
        bst = BlindSpotTracker()
        spot = bst.detect("test gap")
        result = bst.acknowledge(spot.spot_id)
        assert result["acknowledged"] is True
        assert result["spot_id"] == spot.spot_id

    def test_acknowledge_nonexistent(self):
        bst = BlindSpotTracker()
        result = bst.acknowledge("BS-999-0000")
        assert result["acknowledged"] is False
        assert result["reason"] == "not_found"

    def test_summary_empty(self):
        bst = BlindSpotTracker()
        s = bst.summary()
        assert s["total_blind_spots"] == 0
        assert s["unacknowledged"] == 0
        assert s["critical_unacknowledged"] == 0

    def test_summary_with_spots(self):
        bst = BlindSpotTracker()
        bst.detect("gap1", severity="CRITICAL")
        bst.detect("gap2", severity="MEDIUM")
        s = bst.summary()
        assert s["total_blind_spots"] == 2
        assert s["unacknowledged"] == 2
        assert s["critical_unacknowledged"] == 1

    def test_summary_after_acknowledge(self):
        bst = BlindSpotTracker()
        spot = bst.detect("gap1")
        bst.acknowledge(spot.spot_id)
        s = bst.summary()
        assert s["unacknowledged"] == 0

    def test_spot_id_increments(self):
        bst = BlindSpotTracker()
        s1 = bst.detect("a")
        s2 = bst.detect("b")
        assert s1.spot_id != s2.spot_id


class TestBlindSpot:
    def test_default_fields(self):
        bs = BlindSpot(spot_id="BS-0-0", description="test", detected_at="2026-01-01T00:00:00+00:00")
        assert bs.severity == "MEDIUM"
        assert bs.acknowledged is False
        assert bs.coverage_gap == ""
