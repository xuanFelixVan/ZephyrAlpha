# [A_test] module_id: SRC-TST-0951 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_fl_db_bridge
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.db_bridge
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_fl_db_bridge.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.feedback_loop.db_bridge import bulk_record_via_db_contract, record_via_db_contract


class TestRecordViaDbContract:
    def test_records_single_metric(self, tmp_path):
        db_path = str(tmp_path / "test.db")
        result = record_via_db_contract(
            metric_type="gauge",
            metric_name="cpu",
            metric_value=0.75,
            db_path=db_path,
        )
        assert result >= 0

    def test_records_with_tags(self, tmp_path):
        db_path = str(tmp_path / "test.db")
        result = record_via_db_contract(
            metric_type="gauge",
            metric_name="mem",
            metric_value=50.0,
            tags=["host:a"],
            session_id="s1",
            db_path=db_path,
        )
        assert result >= 0

    def test_boundary_zero_value(self, tmp_path):
        db_path = str(tmp_path / "test.db")
        result = record_via_db_contract(
            metric_type="counter",
            metric_name="errors",
            metric_value=0.0,
            db_path=db_path,
        )
        assert result >= 0


class TestBulkRecordViaDbContract:
    def test_bulk_records(self, tmp_path):
        db_path = str(tmp_path / "test.db")
        records = [
            {"metric_type": "gauge", "metric_name": "cpu", "metric_value": 0.5},
            {"metric_type": "gauge", "metric_name": "mem", "metric_value": 80.0},
        ]
        count = bulk_record_via_db_contract(records, db_path=db_path)
        assert count == 2

    def test_bulk_empty_records(self, tmp_path):
        db_path = str(tmp_path / "test.db")
        count = bulk_record_via_db_contract([], db_path=db_path)
        assert count == 0
