# [A_test] module_id: SRC-TST-1747 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_toctou_revalidation
# [INVARIANTS] max_staleness_seconds=5.0; state_tolerance=0.1
# [MODIFY-GUARD] none
# [CONSUMERS] none
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_toctou_revalidation.py
# [TTL] task_bound

from __future__ import annotations

import time

import pytest

from zephyr.feedback_loop.verifiers.toctou_revalidation import (
    TOCTOUResult,
    TOCTOURevalidation,
)


class TestTOCTOURevalidationInstantiation:
    def test_default_construction(self):
        t = TOCTOURevalidation()
        assert t.max_staleness_seconds == pytest.approx(5.0)
        assert t.state_tolerance == pytest.approx(0.1)
        assert t.abort_count == 0

    def test_custom_params(self):
        t = TOCTOURevalidation(max_staleness_seconds=10.0, state_tolerance=0.2)
        assert t.max_staleness_seconds == pytest.approx(10.0)


class TestSnapshotState:
    def test_snapshot_returns_hash(self):
        t = TOCTOURevalidation()
        state = {"cpu": 80.0, "mem": 60.0}
        h = t.snapshot_state(state)
        assert isinstance(h, str)
        assert len(h) > 0

    def test_snapshot_updates_timestamp(self):
        t = TOCTOURevalidation()
        before = t.last_check_at
        t.snapshot_state({"key": "val"})
        assert t.last_check_at > before

    def test_same_state_same_hash(self):
        t = TOCTOURevalidation()
        state = {"cpu": 80.0}
        h1 = t.snapshot_state(state)
        h2 = t.snapshot_state(state)
        assert h1 == h2

    def test_different_state_different_hash(self):
        t = TOCTOURevalidation()
        h1 = t.snapshot_state({"cpu": 80.0})
        h2 = t.snapshot_state({"cpu": 90.0})
        assert h1 != h2

    def test_empty_state(self):
        t = TOCTOURevalidation()
        h = t.snapshot_state({})
        assert isinstance(h, str)


class TestRevalidate:
    def test_fresh_state(self):
        t = TOCTOURevalidation(max_staleness_seconds=60.0)
        state = {"cpu": 80.0}
        t.snapshot_state(state)
        result = t.revalidate(state)
        assert result == TOCTOUResult.FRESH

    def test_stale_state_changed(self):
        t = TOCTOURevalidation(max_staleness_seconds=60.0)
        t.snapshot_state({"cpu": 80.0})
        result = t.revalidate({"cpu": 90.0})
        assert result == TOCTOUResult.STALE_RECHECK
        assert t.abort_count == 1

    def test_stale_by_time(self):
        t = TOCTOURevalidation(max_staleness_seconds=0.001)
        t.snapshot_state({"cpu": 80.0})
        time.sleep(0.01)
        result = t.revalidate({"cpu": 80.0})
        assert result == TOCTOUResult.STALE_ABORT
        assert t.abort_count == 1

    def test_no_snapshot_before_revalidate(self):
        t = TOCTOURevalidation(max_staleness_seconds=60.0)
        result = t.revalidate({"cpu": 80.0})
        assert result == TOCTOUResult.STALE_ABORT
