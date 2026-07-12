# [A_test] module_id: SRC-TST-0550 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_collectors
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] CI pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exceptions on assertion failure
# [TESTS] tests/test_collectors.py
# [TTL] task_bound

import time

import pytest

from zephyr.feedback_loop.collectors.calendar_adapter import CalendarAdapter
from zephyr.feedback_loop.collectors.config_timeline import ConfigTimeline
from zephyr.feedback_loop.collectors.data_quality_validator import DataQualityValidator
from zephyr.feedback_loop.collectors.financial_stratification import FinancialStratification
from zephyr.feedback_loop.collectors.kb_provenance import KBProvenance
from zephyr.feedback_loop.collectors.knowledge_capture import KnowledgeCapture
from zephyr.feedback_loop.collectors.knowledge_freshness import KnowledgeFreshness
from zephyr.feedback_loop.collectors.knowledge_injection import KnowledgeInjection
from zephyr.feedback_loop.collectors.knowledge_packaging import KnowledgePackaging
from zephyr.feedback_loop.collectors.known_unknown_registry import (
    KnownUnknownRegistry,
    KnownUnknownState,
)
from zephyr.feedback_loop.collectors.llm_cost_accounting import LLMCostAccounting
from zephyr.feedback_loop.collectors.market_calendar import MarketCalendar
from zephyr.feedback_loop.collectors.market_event_integrator import (
    MarketEventIntegrator,
    MarketMode,
)
from zephyr.feedback_loop.collectors.notification_feedback import NotificationFeedback
from zephyr.feedback_loop.collectors.schema_evolution import SchemaEvolution
from zephyr.feedback_loop.collectors.schema_migration import (
    MigrationStatus,
    MigrationStep,
    SchemaMigration,
)
from zephyr.feedback_loop.collectors.temporal_event_store import TemporalEventStore
from zephyr.feedback_loop.collectors.token_finops import TokenFinOps
from zephyr.feedback_loop.feedback_collector import (
    ActionResult,
    FeedbackChannel,
    FeedbackCollector,
    OwnerAck,
    OwnerResponse,
)
from zephyr.feedback_loop.metrics_collector import EMABaseline, MetricsCollector, MetricSnapshot


class TestMetricSnapshot:
    def test_create(self):
        s = MetricSnapshot(
            timestamp=1.0,
            system_cpu=50.0,
            memory_usage_pct=60.0,
            disk_io_wait=5.0,
            network_errors_count=0,
            detection_latency_ms=10.0,
        )
        assert s.system_cpu == 50.0
        assert s.network_errors_count == 0


class TestEMABaseline:
    def test_default_values(self):
        ema = EMABaseline()
        assert ema.window == 100
        assert ema.alpha == 0.1
        assert ema.cpu_ema == 0.0

    def test_update_single_snapshot(self):
        ema = EMABaseline()
        s = MetricSnapshot(
            timestamp=1.0,
            system_cpu=50.0,
            memory_usage_pct=60.0,
            disk_io_wait=5.0,
            network_errors_count=2,
            detection_latency_ms=10.0,
        )
        ema.update(s)
        assert ema.cpu_ema == pytest.approx(5.0)
        assert len(ema.history) == 1

    def test_update_multiple_snapshots(self):
        ema = EMABaseline()
        for i in range(5):
            s = MetricSnapshot(
                timestamp=float(i),
                system_cpu=50.0,
                memory_usage_pct=60.0,
                disk_io_wait=5.0,
                network_errors_count=0,
                detection_latency_ms=10.0,
            )
            ema.update(s)
        assert len(ema.history) == 5
        assert ema.cpu_var >= 0


class TestMetricsCollector:
    def test_instantiation(self):
        mc = MetricsCollector()
        assert mc.baseline is not None

    def test_collect_first_snapshot(self):
        mc = MetricsCollector()
        s = MetricSnapshot(
            timestamp=1.0,
            system_cpu=50.0,
            memory_usage_pct=60.0,
            disk_io_wait=5.0,
            network_errors_count=0,
            detection_latency_ms=10.0,
        )
        result = mc.collect(s)
        assert "z_scores" in result
        assert "anomaly_triggered" in result
        assert result["snapshot"] is s

    def test_collect_z_scores_computed(self):
        mc = MetricsCollector()
        s = MetricSnapshot(
            timestamp=1.0,
            system_cpu=50.0,
            memory_usage_pct=60.0,
            disk_io_wait=5.0,
            network_errors_count=0,
            detection_latency_ms=10.0,
        )
        result = mc.collect(s)
        assert "z_scores" in result
        assert "system_cpu" in result["z_scores"]

    def test_collect_anomaly_triggered_field_present(self):
        mc = MetricsCollector()
        s = MetricSnapshot(
            timestamp=1.0,
            system_cpu=50.0,
            memory_usage_pct=60.0,
            disk_io_wait=5.0,
            network_errors_count=0,
            detection_latency_ms=10.0,
        )
        result = mc.collect(s)
        assert isinstance(result["anomaly_triggered"], bool)

    def test_z_threshold_constant(self):
        assert MetricsCollector.Z_THRESHOLD == 2.5


class TestFeedbackChannelEnum:
    def test_values(self):
        assert FeedbackChannel.ACTION_RESULT.value == "action_result"
        assert FeedbackChannel.OWNER_ACK.value == "owner_ack"


class TestOwnerResponseEnum:
    def test_values(self):
        assert OwnerResponse.ACK.value == "ack"
        assert OwnerResponse.OVERRIDE.value == "override"
        assert OwnerResponse.IGNORE.value == "ignore"


class TestActionResult:
    def test_delta_calculated(self):
        ar = ActionResult(
            action_type="repair", anomaly_id="a1", pre_value=10.0, post_value=8.0, success_flag=True, timestamp=1.0
        )
        assert ar.delta == -2.0

    def test_delta_zero(self):
        ar = ActionResult(
            action_type="repair", anomaly_id="a1", pre_value=10.0, post_value=10.0, success_flag=True, timestamp=1.0
        )
        assert ar.delta == 0.0


class TestFeedbackCollector:
    def test_instantiation(self):
        fc = FeedbackCollector()
        assert len(fc.action_results) == 0
        assert len(fc.owner_acks) == 0

    def test_collect_action_result(self):
        fc = FeedbackCollector()
        ar = ActionResult(
            action_type="repair", anomaly_id="a1", pre_value=10.0, post_value=8.0, success_flag=True, timestamp=100.0
        )
        fc.collect_action_result(ar)
        assert len(fc.action_results) == 1

    def test_repair_failure_rate_all_success(self):
        fc = FeedbackCollector()
        fc.collect_action_result(ActionResult("r", "a1", 10.0, 8.0, True, 100.0))
        fc.collect_action_result(ActionResult("r", "a2", 10.0, 8.0, True, 100.0))
        assert fc.repair_failure_rate() == 0.0

    def test_repair_failure_rate_mixed(self):
        fc = FeedbackCollector()
        fc.collect_action_result(ActionResult("r", "a1", 10.0, 8.0, True, 100.0))
        fc.collect_action_result(ActionResult("r", "a2", 10.0, 12.0, False, 100.0))
        assert fc.repair_failure_rate() == 0.5

    def test_repair_failure_rate_empty(self):
        fc = FeedbackCollector()
        assert fc.repair_failure_rate() == 0.0

    def test_owner_override_rate(self):
        fc = FeedbackCollector()
        fc.collect_owner_ack(OwnerAck("a1", OwnerResponse.ACK, 100.0))
        fc.collect_owner_ack(OwnerAck("a2", OwnerResponse.OVERRIDE, 100.0))
        assert fc.owner_override_rate() == 0.5

    def test_owner_override_rate_empty(self):
        fc = FeedbackCollector()
        assert fc.owner_override_rate() == 0.0


class TestDataQualityValidator:
    def test_valid_numeric_data(self):
        dv = DataQualityValidator()
        assert dv.validate({"a": 1, "b": 2.5}) is True

    def test_invalid_string_data(self):
        dv = DataQualityValidator()
        assert dv.validate({"a": "bad"}) is False

    def test_empty_dict_valid(self):
        dv = DataQualityValidator()
        assert dv.validate({}) is True

    def test_mixed_types(self):
        dv = DataQualityValidator()
        assert dv.validate({"a": 1, "b": "bad"}) is False


class TestTokenFinOps:
    def test_track_single(self):
        tf = TokenFinOps()
        tf.track("subsystem_a", 100)
        assert tf.usage["subsystem_a"] == 100

    def test_track_accumulates(self):
        tf = TokenFinOps()
        tf.track("subsystem_a", 100)
        tf.track("subsystem_a", 50)
        assert tf.usage["subsystem_a"] == 150

    def test_track_multiple_subsystems(self):
        tf = TokenFinOps()
        tf.track("a", 100)
        tf.track("b", 200)
        assert tf.usage["a"] == 100
        assert tf.usage["b"] == 200

    def test_empty_usage(self):
        tf = TokenFinOps()
        assert tf.usage == {}


class TestKnownUnknownRegistry:
    def test_register(self):
        reg = KnownUnknownRegistry()
        item = reg.register("KU-001", "trading", "Unknown market impact model")
        assert item.id == "KU-001"
        assert item.state == KnownUnknownState.OPEN
        assert len(reg.items) == 1

    def test_open_count(self):
        reg = KnownUnknownRegistry()
        reg.register("KU-001", "trading", "desc1")
        reg.register("KU-002", "infra", "desc2")
        assert reg.open_count() == 2

    def test_open_count_with_mitigated(self):
        reg = KnownUnknownRegistry()
        item = reg.register("KU-001", "trading", "desc1")
        item.state = KnownUnknownState.MITIGATED
        assert reg.open_count() == 0

    def test_by_domain(self):
        reg = KnownUnknownRegistry()
        reg.register("KU-001", "trading", "desc1")
        reg.register("KU-002", "infra", "desc2")
        reg.register("KU-003", "trading", "desc3")
        trading = reg.by_domain("trading")
        assert len(trading) == 2

    def test_empty_registry(self):
        reg = KnownUnknownRegistry()
        assert reg.open_count() == 0
        assert reg.by_domain("x") == []


class TestKnowledgeFreshness:
    def test_fresh_entry(self):
        kf = KnowledgeFreshness()
        score = kf.score("e1", time.time())
        assert score > 0.9

    def test_old_entry(self):
        kf = KnowledgeFreshness()
        score = kf.score("e1", time.time() - 180 * 86400)
        assert score == 0.0

    def test_90_day_entry(self):
        kf = KnowledgeFreshness()
        score = kf.score("e1", time.time() - 90 * 86400)
        assert score == pytest.approx(0.0, abs=0.01)

    def test_45_day_entry(self):
        kf = KnowledgeFreshness()
        score = kf.score("e1", time.time() - 45 * 86400)
        assert 0.4 < score < 0.6


class TestKnowledgeCapture:
    def test_capture(self):
        kc = KnowledgeCapture()
        kc.capture({"diagnosis": "cpu_spike"})
        assert len(kc.captured) == 1

    def test_capture_multiple(self):
        kc = KnowledgeCapture()
        kc.capture({"diagnosis": "a"})
        kc.capture({"diagnosis": "b"})
        assert len(kc.captured) == 2

    def test_empty(self):
        kc = KnowledgeCapture()
        assert kc.captured == []


class TestKnowledgeInjection:
    def test_inject(self):
        ki = KnowledgeInjection()
        ki.inject({"topic": "trading", "insight": "volatility clusters"})
        assert len(ki.injected) == 1

    def test_inject_multiple(self):
        ki = KnowledgeInjection()
        ki.inject({"a": 1})
        ki.inject({"b": 2})
        assert len(ki.injected) == 2


class TestKnowledgePackaging:
    def test_package(self):
        kp = KnowledgePackaging()
        result = kp.package({"topic": "test"})
        assert result["packaged"] is True
        assert result["topic"] == "test"

    def test_package_empty(self):
        kp = KnowledgePackaging()
        result = kp.package({})
        assert result["packaged"] is True


class TestKBProvenance:
    def test_default_values(self):
        p = KBProvenance()
        assert p.source == "unknown"
        assert p.reliability == 0.5

    def test_custom_values(self):
        p = KBProvenance(source="expert", reliability=0.9)
        assert p.source == "expert"
        assert p.reliability == 0.9


class TestFinancialStratification:
    def test_default(self):
        fs = FinancialStratification()
        assert fs.asset_class == "EQUITY"

    def test_custom(self):
        fs = FinancialStratification(asset_class="FX")
        assert fs.asset_class == "FX"


class TestNotificationFeedback:
    def test_record(self):
        nf = NotificationFeedback()
        nf.record("n1", "acknowledged")
        assert len(nf.responses) == 1
        assert nf.responses[0]["id"] == "n1"

    def test_record_multiple(self):
        nf = NotificationFeedback()
        nf.record("n1", "ack")
        nf.record("n2", "ignore")
        assert len(nf.responses) == 2

    def test_empty(self):
        nf = NotificationFeedback()
        assert nf.responses == []


class TestMarketEventIntegrator:
    def test_default_mode(self):
        mei = MarketEventIntegrator()
        assert mei.current_mode == MarketMode.NORMAL

    def test_circuit_breaker(self):
        mei = MarketEventIntegrator()
        mei.on_circuit_breaker("NYSE")
        assert mei.current_mode == MarketMode.EMERGENCY
        assert len(mei.events) == 1
        assert mei.events[0].event_type == "CIRCUIT_BREAKER"

    def test_fomc(self):
        mei = MarketEventIntegrator()
        mei.on_fomc()
        assert mei.current_mode == MarketMode.CAUTION
        assert mei.events[0].event_type == "FOMC"

    def test_holiday(self):
        mei = MarketEventIntegrator()
        mei.on_holiday("Christmas")
        assert mei.current_mode == MarketMode.HOLIDAY
        assert "Christmas" in mei.events[0].description

    def test_suppress_anomaly_holiday(self):
        mei = MarketEventIntegrator()
        mei.on_holiday("New Year")
        assert mei.should_suppress_anomaly("missing_data") is True
        assert mei.should_suppress_anomaly("cpu_spike") is False

    def test_suppress_anomaly_emergency(self):
        mei = MarketEventIntegrator()
        mei.on_circuit_breaker("NYSE")
        assert mei.should_suppress_anomaly("high_volatility") is True
        assert mei.should_suppress_anomaly("missing_data") is False

    def test_suppress_anomaly_normal(self):
        mei = MarketEventIntegrator()
        assert mei.should_suppress_anomaly("missing_data") is False


class TestMarketCalendar:
    def test_trading_day(self):
        mc = MarketCalendar()
        assert mc.is_trading_day("2026-01-05") is True

    def test_holiday(self):
        mc = MarketCalendar(holidays={"2026-01-01"})
        assert mc.is_trading_day("2026-01-01") is False

    def test_empty_holidays(self):
        mc = MarketCalendar()
        assert mc.is_trading_day("2026-01-01") is True


class TestLLMCostAccounting:
    def test_record(self):
        la = LLMCostAccounting()
        la.record("gpt-4", 1000)
        assert la.total_cost == pytest.approx(0.01)

    def test_accumulates(self):
        la = LLMCostAccounting()
        la.record("gpt-4", 1000)
        la.record("gpt-4", 1000)
        assert la.total_cost == pytest.approx(0.02)

    def test_default_zero(self):
        la = LLMCostAccounting()
        assert la.total_cost == 0.0


class TestCalendarAdapter:
    def test_default(self):
        ca = CalendarAdapter()
        assert ca.is_weekend is False

    def test_weekend(self):
        ca = CalendarAdapter(is_weekend=True)
        assert ca.is_weekend is True


class TestConfigTimeline:
    def test_record(self):
        ct = ConfigTimeline()
        ct.record({"key": "threshold", "old": 5, "new": 10})
        assert len(ct.changes) == 1

    def test_empty(self):
        ct = ConfigTimeline()
        assert ct.changes == []


class TestSchemaEvolution:
    def test_default(self):
        se = SchemaEvolution()
        assert se.version == 1

    def test_custom(self):
        se = SchemaEvolution(version=3)
        assert se.version == 3


class TestSchemaMigration:
    def test_add_step(self):
        sm = SchemaMigration()
        step = MigrationStep(id="s1", description="add column", forward_sql="ALTER", rollback_sql="DROP")
        sm.add_step(step)
        assert len(sm.steps) == 1

    def test_dry_run_ok(self):
        sm = SchemaMigration()
        sm.add_step(MigrationStep(id="s1", description="add", forward_sql="A", rollback_sql="B"))
        result = sm.dry_run("s1")
        assert result == MigrationStatus.DRY_RUN_OK
        assert sm.steps[0].status == MigrationStatus.DRY_RUN_OK

    def test_dry_run_fail_missing(self):
        sm = SchemaMigration()
        result = sm.dry_run("nonexistent")
        assert result == MigrationStatus.DRY_RUN_FAIL

    def test_apply(self):
        sm = SchemaMigration()
        sm.add_step(MigrationStep(id="s1", description="add", forward_sql="A", rollback_sql="B"))
        sm.apply("s1")
        assert sm.steps[0].status == MigrationStatus.APPLIED

    def test_rollback(self):
        sm = SchemaMigration()
        sm.add_step(MigrationStep(id="s1", description="add", forward_sql="A", rollback_sql="B"))
        sm.apply("s1")
        sm.rollback("s1")
        assert sm.steps[0].status == MigrationStatus.ROLLED_BACK

    def test_migration_id(self):
        sm = SchemaMigration(migration_id="M001")
        assert sm.migration_id == "M001"


class TestTemporalEventStore:
    def test_append(self):
        tes = TemporalEventStore()
        tes.append({"type": "anomaly", "ts": 1.0})
        assert len(tes.events) == 1

    def test_multiple_appends(self):
        tes = TemporalEventStore()
        tes.append({"type": "a"})
        tes.append({"type": "b"})
        assert len(tes.events) == 2

    def test_empty(self):
        tes = TemporalEventStore()
        assert tes.events == []
