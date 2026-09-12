# [A_test] module_id: MOD-GOV_cost_tracker | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-002 | docs/03_modules/_domain_infrastructure_runtime/runtime_integration/blueprint.md | §cost_tracker
# [MODULE] tests.test_cost_tracker
# [INVARIANTS] CostTracker.record_usage必须返回UsageRecord; UsageRecord.tokens_total=tokens_in+tokens_out
# [MODIFY-GUARD] 仅当cost_tracker公开API变更时修改
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] import失败→skip; 实例化失败→fail
# [TESTS] pytest tests/test_cost_tracker.py -q
# [TTL] task_bound


from zephyr.infrastructure.cost_tracker import (
    COST_TRACKER_SCHEMA,
    CostReport,
    CostTracker,
    UsageRecord,
)


class TestUsageRecord:
    def test_default_construction(self):
        record = UsageRecord(record_id="UR-001")
        assert record.record_id == "UR-001"
        assert record.model == "unknown"
        assert record.tokens_in == 0
        assert record.tokens_out == 0
        assert record.tokens_total == 0
        assert record.estimated_cost == 0.0
        assert record.metadata == {}

    def test_tokens_total(self):
        record = UsageRecord(record_id="UR-002", tokens_in=1000, tokens_out=500)
        assert record.tokens_total == 1500

    def test_estimated_cost_known_model(self):
        record = UsageRecord(
            record_id="UR-003",
            model="deepseek-chat",
            tokens_in=1000,
            tokens_out=1000,
        )
        cost = record.estimated_cost
        assert cost > 0.0

    def test_estimated_cost_unknown_model(self):
        record = UsageRecord(
            record_id="UR-004",
            model="unknown-model",
            tokens_in=1000,
            tokens_out=1000,
        )
        cost = record.estimated_cost
        assert cost > 0.0

    def test_zero_tokens(self):
        record = UsageRecord(record_id="UR-005", tokens_in=0, tokens_out=0)
        assert record.tokens_total == 0
        assert record.estimated_cost == 0.0


class TestCostReport:
    def test_default_construction(self):
        report = CostReport(report_date="2026-01-01")
        assert report.report_date == "2026-01-01"
        assert report.total_tokens == 0
        assert report.record_count == 0
        assert report.by_model == {}
        assert report.by_component == {}


class TestCostTracker:
    def test_instantiation(self, tmp_path):
        db = tmp_path / "test_data/databases/governance.db"
        tracker = CostTracker(db_path=str(db))
        assert tracker is not None
        tracker.close()

    def test_record_usage(self, tmp_path):
        db = tmp_path / "test_data/databases/governance.db"
        tracker = CostTracker(db_path=str(db))
        record = tracker.record_usage(
            model="deepseek-chat",
            tokens_in=2500,
            tokens_out=1200,
            component="test_component",
        )
        assert isinstance(record, UsageRecord)
        assert record.tokens_in == 2500
        assert record.tokens_out == 1200
        assert record.tokens_total == 3700
        assert record.estimated_cost > 0.0
        tracker.close()

    def test_record_usage_with_metadata(self, tmp_path):
        db = tmp_path / "test_data/databases/governance.db"
        tracker = CostTracker(db_path=str(db))
        record = tracker.record_usage(
            model="deepseek-chat",
            tokens_in=100,
            tokens_out=50,
            metadata={"session": "test-session"},
        )
        assert record.metadata == {"session": "test-session"}
        tracker.close()

    def test_daily_report_empty(self, tmp_path):
        db = tmp_path / "test_data/databases/governance.db"
        tracker = CostTracker(db_path=str(db))
        report = tracker.daily_report()
        assert isinstance(report, CostReport)
        assert report.record_count == 0
        tracker.close()

    def test_daily_report_with_records(self, tmp_path):
        db = tmp_path / "test_data/databases/governance.db"
        tracker = CostTracker(db_path=str(db))
        tracker.record_usage(model="deepseek-chat", tokens_in=1000, tokens_out=500)
        tracker.record_usage(model="claude-sonnet-4-20250514", tokens_in=2000, tokens_out=1000)
        report = tracker.daily_report()
        assert report.record_count == 2
        assert report.total_tokens > 0
        assert report.total_cost > 0
        assert "deepseek-chat" in report.by_model
        assert "claude-sonnet-4-20250514" in report.by_model
        tracker.close()

    def test_check_budget(self, tmp_path):
        db = tmp_path / "test_data/databases/governance.db"
        tracker = CostTracker(db_path=str(db), daily_budget_usd=10.0)
        tracker.record_usage(model="deepseek-chat", tokens_in=1000, tokens_out=500)
        budget = tracker.get_budget_status()
        assert "daily_budget" in budget
        assert "spent" in budget
        assert "remaining" in budget
        assert "pct_used" in budget
        assert "alerts" in budget
        assert budget["pct_used"] < 100
        tracker.close()

    def test_check_budget_over(self, tmp_path):
        db = tmp_path / "test_data/databases/governance.db"
        tracker = CostTracker(db_path=str(db), daily_budget_usd=0.00001)
        tracker.record_usage(model="deepseek-chat", tokens_in=100000, tokens_out=50000)
        budget = tracker.get_budget_status()
        assert len(budget["alerts"]) > 0
        tracker.close()

    def test_schema_is_valid_sql(self):
        assert "CREATE TABLE" in COST_TRACKER_SCHEMA
        assert "usage_records" in COST_TRACKER_SCHEMA

    def test_concurrent_writes(self, tmp_path):
        from concurrent.futures import ThreadPoolExecutor

        db = tmp_path / "test_concurrent.db"
        tracker = CostTracker(db_path=str(db))

        def write_record(i):
            return tracker.record_usage(
                model="deepseek-chat",
                tokens_in=100 * i,
                tokens_out=50 * i,
                component=f"comp_{i}",
            )

        with ThreadPoolExecutor(max_workers=4) as pool:
            list(pool.map(write_record, range(10)))

        report = tracker.daily_report()
        assert report.record_count == 10
        tracker.close()
