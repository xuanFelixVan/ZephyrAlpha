# [A_test] module_id: SRC-TST-0746 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_diagnosers
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] CI pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exceptions on assertion failure
# [TESTS] tests/test_diagnosers.py
# [TTL] task_bound

from datetime import UTC, datetime

import pytest

from zephyr.feedback_loop.diagnosers.action_composition_health_monitor import ActionCompositionHealthMonitor
from zephyr.feedback_loop.diagnosers.adaptive_param_tuning import AdaptiveParamTuning, TuningMode
from zephyr.feedback_loop.diagnosers.amplification_guard import AmplificationGuard
from zephyr.feedback_loop.diagnosers.api_dependency_metrics import APIDependencyMetrics, DependencyStatusRecord
from zephyr.feedback_loop.diagnosers.auto_diagnosis import AutoDiagnosis
from zephyr.feedback_loop.diagnosers.burn_rate_alerter import BurnRateAlerter
from zephyr.feedback_loop.diagnosers.burnout_alarm import BurnoutAlarm
from zephyr.feedback_loop.diagnosers.capacity_aware_repair import CapacityAwareRepair
from zephyr.feedback_loop.diagnosers.causal_inference_engine import CausalGraph, CausalInferenceEngine
from zephyr.feedback_loop.diagnosers.cognitive_load import CognitiveLoad
from zephyr.feedback_loop.diagnosers.cognitive_load_budget import CognitiveLoadBudget
from zephyr.feedback_loop.diagnosers.cold_start_conservative_mode import ColdStartConservativeMode, ColdStartPhase
from zephyr.feedback_loop.diagnosers.collaborative_learning import CollaborativeLearning
from zephyr.feedback_loop.diagnosers.confidence_decomposer import ConfidenceDecomposer
from zephyr.feedback_loop.diagnosers.context_truncation import ContextTruncation
from zephyr.feedback_loop.diagnosers.context_window_pressure_manager import ContextWindowPressureManager
from zephyr.feedback_loop.diagnosers.timezone_semantic_reasoner import TimezoneSemanticReasoner
from zephyr.feedback_loop.diagnosers.toil_quantification import ActionClass, ToilQuantification
from zephyr.feedback_loop.diagnosers.tone_adapter import ToneAdapter
from zephyr.feedback_loop.diagnosers.tone_adapter_v2 import ToneAdapterV2
from zephyr.feedback_loop.diagnosers.value_added_baseline import ValueAddedBaseline
from zephyr.feedback_loop.diagnosers.vertical_self_assessment import VerticalSelfAssessment
from zephyr.feedback_loop.diagnosers.zombie_fle_detector import CognitiveState, ZombieFLEDetector


class TestAutoDiagnosis:
    def test_default(self):
        ad = AutoDiagnosis()
        assert ad.enabled is True
        assert ad.max_concurrent == 5

    def test_diagnose(self):
        ad = AutoDiagnosis()
        result = ad.diagnose("anomaly-001")
        assert result["anomaly_id"] == "anomaly-001"
        assert result["status"] == "queued"


class TestBurnoutAlarm:
    def test_no_alarm(self):
        ba = BurnoutAlarm(response_latency_avg=100.0, skip_rate=0.1)
        assert ba.alarm is False

    def test_alarm_high_latency(self):
        ba = BurnoutAlarm(response_latency_avg=4000.0, skip_rate=0.0)
        assert ba.alarm is True

    def test_alarm_high_skip_rate(self):
        ba = BurnoutAlarm(response_latency_avg=100.0, skip_rate=0.5)
        assert ba.alarm is True

    def test_boundary_latency(self):
        ba = BurnoutAlarm(response_latency_avg=3600.0, skip_rate=0.0)
        assert ba.alarm is False

    def test_boundary_skip_rate(self):
        ba = BurnoutAlarm(response_latency_avg=0.0, skip_rate=0.3)
        assert ba.alarm is False


class TestBurnRateAlerter:
    def test_default_windows(self):
        bra = BurnRateAlerter()
        assert len(bra.windows) == 3

    def test_record_success(self):
        bra = BurnRateAlerter()
        bra.record(True)
        assert bra.windows[0].total_count == 1
        assert bra.windows[0].error_count == 0

    def test_record_failure(self):
        bra = BurnRateAlerter()
        bra.record(False)
        assert bra.windows[0].error_count == 1

    def test_no_alerts_when_healthy(self):
        bra = BurnRateAlerter()
        for _ in range(10):
            bra.record(True)
        assert bra.alerts() == []

    def test_alerts_on_high_burn(self):
        bra = BurnRateAlerter()
        for _ in range(100):
            bra.record(False)
        alerts = bra.alerts()
        assert len(alerts) > 0


class TestCognitiveLoad:
    def test_update(self):
        cl = CognitiveLoad()
        cl.update(5)
        assert cl.notifications_per_hour == 5
        assert cl.fatigue_score == pytest.approx(0.5)

    def test_fatigue_capped_at_one(self):
        cl = CognitiveLoad()
        cl.update(20)
        assert cl.fatigue_score == 1.0


class TestCognitiveLoadBudget:
    def test_request_allowed(self):
        clb = CognitiveLoadBudget()
        assert clb.request("d1", 5) is True

    def test_request_denied_daily_limit(self):
        clb = CognitiveLoadBudget(max_decisions_per_day=2)
        clb.request("d1", 5)
        clb.request("d2", 5)
        assert clb.request("d3", 5) is False

    def test_fatigue_score_updated(self):
        clb = CognitiveLoadBudget()
        clb.request("d1", 5)
        assert clb.fatigue_score > 0


class TestConfidenceDecomposer:
    def test_decompose(self):
        cd = ConfidenceDecomposer()
        result = cd.decompose(0.9, {"data": 1, "model": 1, "context": 1})
        assert len(result) == 3
        assert all(v == pytest.approx(0.3) for v in result.values())

    def test_decompose_empty_factors(self):
        cd = ConfidenceDecomposer()
        result = cd.decompose(0.9, {})
        assert result == {}


class TestContextTruncation:
    def test_under_limit(self):
        ct = ContextTruncation()
        assert ct.check(5000) is False

    def test_over_limit(self):
        ct = ContextTruncation()
        assert ct.check(10000) is True

    def test_exact_limit(self):
        ct = ContextTruncation()
        assert ct.check(8192) is False

    def test_custom_limit(self):
        ct = ContextTruncation(max_tokens=4096)
        assert ct.check(5000) is True


class TestToilQuantification:
    def test_record_automated(self):
        tq = ToilQuantification()
        ratio = tq.record_action(ActionClass.FULLY_AUTOMATED)
        assert ratio == 0.0

    def test_record_manual(self):
        tq = ToilQuantification()
        ratio = tq.record_action(ActionClass.MANUAL_REQUIRED)
        assert ratio == 1.0

    def test_mixed_actions(self):
        tq = ToilQuantification()
        tq.record_action(ActionClass.FULLY_AUTOMATED)
        tq.record_action(ActionClass.MANUAL_REQUIRED)
        assert tq.current_toil_ratio == 0.5

    def test_is_toil_excessive(self):
        tq = ToilQuantification()
        tq.record_action(ActionClass.MANUAL_REQUIRED)
        assert tq.is_toil_excessive() is True

    def test_not_excessive(self):
        tq = ToilQuantification()
        for _ in range(10):
            tq.record_action(ActionClass.FULLY_AUTOMATED)
        tq.record_action(ActionClass.MANUAL_REQUIRED)
        assert tq.is_toil_excessive() is False


class TestCausalInferenceEngine:
    def test_infer_with_cause(self):
        graph = CausalGraph(nodes={"high_latency": ["db_overload"]})
        engine = CausalInferenceEngine(graph=graph)
        result = engine.infer("high_latency", {})
        assert "db_overload" in result

    def test_infer_no_cause(self):
        engine = CausalInferenceEngine()
        result = engine.infer("unknown_symptom", {})
        assert result == []


class TestCapacityAwareRepair:
    def test_sufficient_headroom(self):
        car = CapacityAwareRepair()
        assert car.check_headroom(10.0, 20.0) is True

    def test_insufficient_headroom(self):
        car = CapacityAwareRepair()
        assert car.check_headroom(10.0, 11.0) is False

    def test_exact_1_2x(self):
        car = CapacityAwareRepair()
        assert car.check_headroom(10.0, 12.0) is True


class TestDependencyStatusRecord:
    def test_risk_level_high_cve(self):
        dsr = DependencyStatusRecord(service="svc", version="1.0", cve_count=2)
        assert dsr.risk_level == "HIGH"

    def test_risk_level_medium_copyleft(self):
        dsr = DependencyStatusRecord(service="svc", version="1.0", license_copyleft=True)
        assert dsr.risk_level == "MEDIUM"

    def test_risk_level_high_sunset(self):
        dsr = DependencyStatusRecord(service="svc", version="1.0", sunset_overdue=True)
        assert dsr.risk_level == "HIGH"

    def test_risk_level_low(self):
        dsr = DependencyStatusRecord(service="svc", version="1.0")
        assert dsr.risk_level == "LOW"


class TestAPIDependencyMetrics:
    def test_register(self):
        adm = APIDependencyMetrics()
        dep = adm.register("service_a", "1.0")
        assert dep.service == "service_a"

    def test_scan_empty(self):
        adm = APIDependencyMetrics()
        result = adm.scan()
        assert result["total"] == 0

    def test_scan_with_deps(self):
        adm = APIDependencyMetrics()
        adm.register("svc_a", "1.0")
        dep = adm.register("svc_b", "2.0")
        dep.cve_count = 3
        result = adm.scan()
        assert result["total"] == 2
        assert result["cve_active"] == 1

    def test_snapshot(self):
        adm = APIDependencyMetrics()
        adm.register("svc_a", "1.0")
        adm.snapshot()
        assert len(adm.history) == 1


class TestColdStartConservativeMode:
    def test_start(self):
        cscm = ColdStartConservativeMode()
        cscm.start()
        assert cscm.phase == ColdStartPhase.COLLECT_ONLY
        assert cscm.current_cycle == 0

    def test_tick_phases(self):
        cscm = ColdStartConservativeMode()
        cscm.start()
        for _ in range(100):
            cscm.tick()
        assert cscm.phase == ColdStartPhase.WITH_DETECT

    def test_is_warm(self):
        cscm = ColdStartConservativeMode()
        assert cscm.is_warm() is False

    def test_action_allowed_collect(self):
        cscm = ColdStartConservativeMode()
        assert cscm.is_action_allowed("COLLECT_metrics") is True

    def test_blocked_action(self):
        cscm = ColdStartConservativeMode()
        assert cscm.is_action_allowed("SELF_UPGRADE") is False

    def test_status_report(self):
        cscm = ColdStartConservativeMode()
        cscm.start()
        report = cscm.status_report()
        assert "phase" in report
        assert "is_warm" in report


class TestAdaptiveParamTuning:
    def test_observe_true_positive(self):
        apt = AdaptiveParamTuning()
        threshold = apt.observe(was_anomaly=True, was_true_positive=True)
        assert isinstance(threshold, float)

    def test_observe_false_positive_increases_threshold(self):
        apt = AdaptiveParamTuning()
        for _ in range(20):
            apt.observe(was_anomaly=False, was_true_positive=False)
        assert apt.current_threshold > 1.0

    def test_lock_mode(self):
        apt = AdaptiveParamTuning()
        apt.lock()
        assert apt.mode == TuningMode.LOCKED
        threshold_before = apt.current_threshold
        apt.observe(was_anomaly=False, was_true_positive=False)
        assert apt.current_threshold == threshold_before

    def test_unlock(self):
        apt = AdaptiveParamTuning()
        apt.lock()
        apt.unlock()
        assert apt.mode == TuningMode.ADAPTIVE


class TestActionCompositionHealthMonitor:
    def test_record_composition(self):
        achm = ActionCompositionHealthMonitor()
        achm.record_composition_outcome("comp1", ("action_a", "action_b"), True)
        assert "comp1" in achm.compositions

    def test_record_independent(self):
        achm = ActionCompositionHealthMonitor()
        achm.record_independent_outcome("action_a", True)
        assert "action_a" in achm.independent_stats

    def test_detect_negative_synergy_insufficient_data(self):
        achm = ActionCompositionHealthMonitor()
        achm.record_composition_outcome("comp1", ("a",), True)
        result = achm.detect_negative_synergy()
        assert result["total_compositions"] == 0


class TestTimezoneSemanticReasoner:
    def test_market_active_during_hours(self):
        tsr = TimezoneSemanticReasoner()
        dt = datetime(2026, 1, 1, 15, 0, tzinfo=UTC)
        assert tsr.is_market_active("NYSE", dt) is True

    def test_market_inactive_outside_hours(self):
        tsr = TimezoneSemanticReasoner()
        dt = datetime(2026, 1, 1, 10, 0, tzinfo=UTC)
        assert tsr.is_market_active("NYSE", dt) is False

    def test_unknown_venue(self):
        tsr = TimezoneSemanticReasoner()
        dt = datetime(2026, 1, 1, 15, 0, tzinfo=UTC)
        assert tsr.is_market_active("UNKNOWN", dt) is False

    def test_active_venues(self):
        tsr = TimezoneSemanticReasoner()
        venues = tsr.active_venues()
        assert isinstance(venues, list)

    def test_next_transition(self):
        tsr = TimezoneSemanticReasoner()
        result = tsr.next_transition("NYSE")
        assert result > 0


class TestContextWindowPressureManager:
    def test_add_entry(self):
        cwpm = ContextWindowPressureManager()
        cwpm.add_entry("test", 1.0, "src", 100)
        assert len(cwpm.entries) == 1

    def test_check_pressure_normal(self):
        cwpm = ContextWindowPressureManager()
        cwpm.add_entry("test", 1.0, "src", 100)
        result = cwpm.check_pressure()
        assert result["status"] == "normal"

    def test_check_pressure_critical(self):
        cwpm = ContextWindowPressureManager()
        cwpm.add_entry("big", 1.0, "src", 7500)
        result = cwpm.check_pressure()
        assert result["status"] in ("pressured", "critical")

    def test_compress(self):
        cwpm = ContextWindowPressureManager()
        for i in range(20):
            cwpm.add_entry(f"e{i}", 0.5, "src", 500)
        removed = cwpm.compress()
        assert isinstance(removed, int)

    def test_get_summary(self):
        cwpm = ContextWindowPressureManager()
        cwpm.add_entry("test", 1.0, "src", 100)
        summary = cwpm.get_summary()
        assert "total_entries" in summary
        assert "total_tokens" in summary


class TestAmplificationGuard:
    def test_within_limit(self):
        ag = AmplificationGuard()
        assert ag.check(0.1, 0.3) is True

    def test_exceeds_limit(self):
        ag = AmplificationGuard()
        assert ag.check(0.01, 0.1) is False

    def test_zero_input_bias(self):
        ag = AmplificationGuard()
        assert ag.check(0.0, 0.0) is True


class TestValueAddedBaseline:
    def test_positive_roi(self):
        vab = ValueAddedBaseline(cost_baseline=100.0, cost_fle=50.0)
        assert vab.roi == pytest.approx(1.0)

    def test_negative_roi(self):
        vab = ValueAddedBaseline(cost_baseline=50.0, cost_fle=100.0)
        assert vab.roi < 0

    def test_zero_cost_fle(self):
        vab = ValueAddedBaseline(cost_baseline=100.0, cost_fle=0.0)
        assert vab.roi == pytest.approx(100.0)


class TestVerticalSelfAssessment:
    def test_assess(self):
        vsa = VerticalSelfAssessment(maturity_level=3)
        assert vsa.assess() == "L3"

    def test_default(self):
        vsa = VerticalSelfAssessment()
        assert vsa.maturity_level == 0


class TestZombieFLEDetector:
    def test_initial_state(self):
        zfd = ZombieFLEDetector()
        assert zfd.state == CognitiveState.ALIVE

    def test_send_test(self):
        zfd = ZombieFLEDetector()
        test = zfd.send_test()
        assert test.test_id == "cog-0"
        assert test.passed is False

    def test_verify_pass(self):
        zfd = ZombieFLEDetector()
        test = zfd.send_test()
        zfd.verify_response(test.test_id, True)
        assert zfd.state == CognitiveState.ALIVE

    def test_verify_fail_becomes_zombie(self):
        zfd = ZombieFLEDetector(max_consecutive_failures=2)
        t1 = zfd.send_test()
        zfd.verify_response(t1.test_id, False)
        t2 = zfd.send_test()
        zfd.verify_response(t2.test_id, False)
        assert zfd.state == CognitiveState.ZOMBIE

    def test_consecutive_fails_reset(self):
        zfd = ZombieFLEDetector(max_consecutive_failures=3)
        t1 = zfd.send_test()
        zfd.verify_response(t1.test_id, False)
        t2 = zfd.send_test()
        zfd.verify_response(t2.test_id, True)
        assert zfd.consecutive_fails == 0


class TestToneAdapter:
    def test_urgent(self):
        ta = ToneAdapter()
        assert ta.adapt(9, 0.0) == "urgent"

    def test_standard(self):
        ta = ToneAdapter()
        assert ta.adapt(5, 0.0) == "standard"


class TestToneAdapterV2:
    def test_high_severity_all_channels(self):
        tav2 = ToneAdapterV2()
        result = tav2.route(9)
        assert len(result) == 3

    def test_low_severity_single_channel(self):
        tav2 = ToneAdapterV2()
        result = tav2.route(5)
        assert len(result) == 1


class TestCollaborativeLearning:
    def test_share(self):
        cl = CollaborativeLearning()
        cl.share("key1", "value1")
        assert cl.shared_knowledge["key1"] == "value1"

    def test_empty(self):
        cl = CollaborativeLearning()
        assert cl.shared_knowledge == {}
