# [A_test] module_id: SRC-TST-0175 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-332 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.integration.test_phase_f_layers
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""Phase F — L08–L13 非主线层集成测试 + 背压契约

测试范围：
  L08 Human-AI Interface    : 通知/审批生命周期
  L09 Research & Innovation : 回测引擎 + 因子发现
  L10 Compliance            : AI 安全网关 + 合规引擎
  L11 ML Platform           : 模型注册 + 推理服务
  L12 System Telemetry      : SLA 监控 + 契约漂移检测
  L13 Experimentation       : 实验管线 + A/B 测试
  Backpressure (BP)         : Pause/Throttle/Resume 状态机
  P1 Contracts              : CTR-P1-001～CTR-P1-015（与 cross_layer_contracts.yaml 编号对齐）

Phase F | Safety: MEDIUM
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pandas as pd
import pytest

from zephyr.frontend.interface_base import (
    ApprovalAction,
    ApprovalGatewayBase,
    ApprovalRequest,
    DashboardBase,
    Notification,
    NotificationLevel,
    NotificationManagerBase,
)
from zephyr.governance.security_governance.default_security_gateway import DefaultSecurityGateway
from zephyr.governance.security_governance.security_gateway_base import (
    AuditAction,
    AuditDecision,
    ComplianceEngine,
    SecurityGateway,
)
from zephyr.infrastructure.system_telemetry.contract_metrics import (
    ContractMetricsCollector,
    DriftAlert,
    SlaRecord,
    get_contract_metrics,
)
from zephyr.infrastructure.pipeline.backpressure_manager import (
    BackpressureManager,
    BpState,
    emit_pause,
    emit_resume,
    emit_throttle,
)
from zephyr.shared.contracts.core.system_configuration import SystemConfiguration
from zephyr.shared.contracts.telemetry_emitter import TelemetryEmitter
from zephyr.shared.contracts.experiment_result import ExperimentResult
from zephyr.shared.contracts.factor_monitor_report import FactorMonitorReport
from zephyr.shared.contracts.macro_factor_signal import MacroFactorSignal
from zephyr.shared.contracts.model_serving_response import ModelServingResponse
from zephyr.shared.contracts.performance_attribution_report import PerformanceAttributionReport
from zephyr.shared.contracts.strategy_lifecycle_event import StrategyLifecycleEvent
from zephyr.intelligence.model_evaluation.implementations.default_inference_engine import DefaultInferenceEngine
from zephyr.intelligence.model_evaluation.inference_base import (
    InferenceEngineBase,
    ModelMetadata,
    ModelRegistry,
    ModelTrainerBase,
)
from zephyr.pf_core.compliance_rule import ComplianceRule
from zephyr.backtest.core.engine_base import (
    BacktestEngineBase,
    BacktestResult,
    FactorDiscovery,
)
from zephyr.backtest.implementations.vectorized_engine import (
    BacktestConfig,
    DefaultBacktestEngine,
)
from zephyr.simulation.implementations.default_experiment_pipeline import (
    DefaultExperimentPipeline,
)
from zephyr.simulation.pipeline_base import (
    ExperimentConfig,
    ExperimentMetric,
    ExperimentPipelineBase,
    ScoutAgentBase,
)
from zephyr.trading.trading_contracts.execution.capital_allocation_result import CapitalAllocationResult
from zephyr.trading.trading_contracts.execution.execution_report import ExecutionReport
from zephyr.trading.trading_contracts.execution.model_serving_request import ModelServingRequest
from zephyr.shared.contracts.synthesized_signal import SynthesizedSignal
from zephyr.trading.trading_contracts.risk.risk_dashboard_snapshot import RiskDashboardSnapshot
from zephyr.trading.trading_contracts.risk.risk_metrics import RiskMetricsReport


class TestPhaseFL08:
    """L08 — Human-AI Interface: 通知 + 审批"""

    def test_notification_dataclass_frozen(self):
        n = Notification(
            notification_id=f"notif-{uuid.uuid4().hex[:8]}",
            title="Test Alert",
            body="Something happened",
            level=NotificationLevel.INFO,
            source_layer="l04",
        )
        assert n.notification_id.startswith("notif-")
        assert n.title == "Test Alert"
        assert isinstance(n.timestamp, datetime)
        with pytest.raises(Exception):
            n.title = "Changed"

    def test_notification_level_enum(self):
        assert NotificationLevel.INFO.value == "info"
        assert NotificationLevel.WARNING.value == "warning"
        assert NotificationLevel.ERROR.value == "error"
        assert NotificationLevel.CRITICAL.value == "critical"
        assert len(NotificationLevel) == 4

    def test_approval_request_frozen_dataclass(self):
        ar = ApprovalRequest(
            request_id=f"req-{uuid.uuid4().hex[:8]}",
            action="override_risk_limit",
            reason="Manual override for large order",
            requester="trader_01",
            expires_at=datetime.now(UTC) + timedelta(hours=1),
        )
        assert ar.request_id.startswith("req-")
        assert ar.action == "override_risk_limit"
        assert ar.status == "pending"
        with pytest.raises(Exception):
            ar.status = "approved"

    def test_approval_action_enum(self):
        assert ApprovalAction.APPROVE.value == "approve"
        assert ApprovalAction.REJECT.value == "reject"
        assert ApprovalAction.DELEGATE.value == "delegate"
        assert ApprovalAction.ESCALATE.value == "escalate"
        assert len(ApprovalAction) == 4

    def test_dashboard_base_is_abstract(self):
        assert DashboardBase.__abstractmethods__ == frozenset({"render"})
        with pytest.raises(TypeError):
            DashboardBase()

    def test_notification_manager_base_is_abstract(self):
        assert NotificationManagerBase.__abstractmethods__ == frozenset({"send", "channels"})

    def test_approval_gateway_base_is_abstract(self):
        assert ApprovalGatewayBase.__abstractmethods__ == frozenset({"submit", "decide", "pending"})


class TestPhaseFL09:
    """L09 — Research & Innovation: 回测引擎 + 因子发现"""

    def test_backtest_result_resource(self):
        result = BacktestResult(
            strategy_id="test-strat",
            start_date=datetime(2025, 1, 1, tzinfo=UTC),
            end_date=datetime(2025, 6, 30, tzinfo=UTC),
            total_return=0.15,
            annual_return=0.30,
            sharpe_ratio=1.2,
            max_drawdown=0.12,
            win_rate=0.55,
            trades_count=120,
            idempotency_key="test-key-001",
            timestamp=datetime.now(UTC),
        )
        assert result.strategy_id == "test-strat"
        assert result.sharpe_ratio == 1.2
        assert result.max_drawdown == 0.12

    def test_factor_discovery_resource(self):
        fd = FactorDiscovery(
            factor_id="test-factor",
            name="Test Factor",
            ic_mean=0.04,
            ic_ir=0.8,
            t_stat=2.5,
        )
        assert fd.factor_id == "test-factor"
        assert fd.status == "candidate"
        assert fd.ic_mean == 0.04

    def test_default_backtest_engine_runs_with_prices_and_signals(self):
        engine = DefaultBacktestEngine(BacktestConfig())
        dates = pd.date_range("2025-01-01", "2025-03-31", freq="B")

        prices = pd.DataFrame(
            {
                "close": [1800.0 + i * 0.3 for i in range(len(dates))],
                "open": [1795.0 + i * 0.3 for i in range(len(dates))],
                "high": [1805.0 + i * 0.3 for i in range(len(dates))],
                "low": [1790.0 + i * 0.3 for i in range(len(dates))],
                "volume": [1000000.0 for _ in range(len(dates))],
            },
            index=dates,
        )

        signals = pd.DataFrame(
            {"600519": 1.0},
            index=dates,
        )

        result = engine.run(signals=signals, data=prices, strategy_name="test")
        assert isinstance(result, BacktestResult)
        assert result.strategy_id == "test"

    def test_backtest_engine_base_is_abstract(self):
        assert BacktestEngineBase.__abstractmethods__ == frozenset({"run"})


class TestPhaseFL10:
    """L10 — Compliance: AI 安全网关 + 合规引擎"""

    def test_default_security_gateway_blocks_os_system(self):
        gw = DefaultSecurityGateway()
        assert gw.pre_filter("os.system('rm -rf /')", "test")
        risks = gw.security_scan("os.system('rm -rf /')")
        assert "BLOCK:system_call" in risks

        decision = gw.decide(risks, {"source": "test"})
        assert decision.action == AuditAction.BLOCK
        assert decision.rule_id == "AISG-001"

    def test_default_security_gateway_blocks_subprocess(self):
        gw = DefaultSecurityGateway()
        risks = gw.security_scan("subprocess.call(['rm', '-rf', '/'])")
        blocked = [r for r in risks if r.startswith("BLOCK:")]
        assert len(blocked) >= 1

    def test_default_security_gateway_flags_safe_file_write(self):
        gw = DefaultSecurityGateway()
        risks = gw.security_scan("with open('config.txt', 'w') as f: f.write('/etc/hosts')")
        flagged = [r for r in risks if r.startswith("WARN:")]
        assert len(flagged) >= 1

        decision = gw.decide(risks, {"source": "test"})
        assert decision.action == AuditAction.FLAG

    def test_default_security_gateway_allows_clean_code(self):
        gw = DefaultSecurityGateway()
        risks = gw.security_scan("import numpy as np\nx = np.array([1, 2, 3])")
        assert len(risks) == 0

        decision = gw.decide(risks, {"source": "test"})
        assert decision.action == AuditAction.ALLOW

    def test_audit_action_enum(self):
        assert AuditAction.ALLOW.value == "allow"
        assert AuditAction.BLOCK.value == "block"
        assert AuditAction.FLAG.value == "flag"
        assert AuditAction.REDIRECT.value == "redirect"
        assert len(AuditAction) == 4

    def test_audit_decision_frozen(self):
        decision = AuditDecision(
            decision_id="audit-001",
            action=AuditAction.BLOCK,
            rule_id="AISG-001",
            reason="dangerous",
            metadata={"source": "test"},
        )
        assert decision.action == AuditAction.BLOCK
        with pytest.raises(Exception):
            decision.action = AuditAction.ALLOW

    def test_security_gateway_is_abstract(self):
        assert SecurityGateway.__abstractmethods__ == frozenset({"pre_filter", "security-scan", "decide"})

    def test_compliance_engine_is_abstract(self):
        assert ComplianceEngine.__abstractmethods__ == frozenset({"evaluate", "enforce"})


class TestPhaseFL11:
    """L11 — ML Platform: 模型注册 + 推理服务"""

    def test_model_metadata_resource(self):
        mm = ModelMetadata(
            model_id="model-001",
            model_version="v1.0.0",
            model_type="xgboost",
            framework="scikit-learn",
            features=["close", "volume", "mom_20d"],
            target="next_day_return",
            status="active",
        )
        assert mm.model_id == "model-001"
        assert "close" in mm.features
        assert mm.status == "active"

    def test_model_registry_operations(self):
        ModelRegistry.clear()
        assert ModelRegistry._registry == {}

        class TestTrainer(ModelTrainerBase):
            __model_id__ = "test-model"

            def train(self, features, target, idempotency_key):
                return {"r2": 0.85}

            def validate(self, features, target):
                return {"r2": 0.82}

        registered = ModelRegistry.register(TestTrainer)
        assert registered is TestTrainer
        assert ModelRegistry.get("test-model") is TestTrainer

        with pytest.raises(ValueError):
            ModelRegistry.register(TestTrainer)
        ModelRegistry.clear()

    def test_model_registry_requires_model_id(self):
        ModelRegistry.clear()

        class BadTrainer(ModelTrainerBase):
            def train(self, features, target, idempotency_key):
                return {}

            def validate(self, features, target):
                return {}

        with pytest.raises(AttributeError):
            ModelRegistry.register(BadTrainer)
        ModelRegistry.clear()

    def test_default_inference_engine_with_registry_fallback(self):
        engine = DefaultInferenceEngine()
        request = ModelServingRequest(
            request_id=f"req-{uuid.uuid4().hex[:8]}",
            model_id="unknown-model",
            model_version="v1.0",
            input_features={"feature_a": 1.0, "feature_b": 2.0},
            idempotency_key=str(uuid.uuid4()),
        )
        response = engine.predict(request)
        assert isinstance(response, ModelServingResponse)
        assert response.model_id == "unknown-model"
        assert response.confidence == 0.0

    def test_default_inference_engine_list_models_empty(self):
        engine = DefaultInferenceEngine()
        assert engine.list_models() == []

    def test_inference_engine_base_is_abstract(self):
        assert InferenceEngineBase.__abstractmethods__ == frozenset({"predict"})

    def test_model_trainer_base_is_abstract(self):
        assert ModelTrainerBase.__abstractmethods__ == frozenset({"train", "validate"})


class TestPhaseFL12:
    """L12 — System Telemetry: SLA 监控 + 契约漂移"""

    def test_contract_metrics_collector_singleton(self):
        m1 = get_contract_metrics()
        m2 = get_contract_metrics()
        assert m1 is m2

    def test_sla_measurement_records(self):
        collector = ContractMetricsCollector()
        record = collector.measure_sla(
            contract_id="CTR-001",
            trace_id="trace-abc-123",
            latency_us=5000,
            sla_p99_us=10000,
        )
        assert isinstance(record, SlaRecord)
        assert record.passed is True
        assert record.contract_id == "CTR-001"

    def test_sla_measurement_detects_violation(self):
        collector = ContractMetricsCollector()
        collector.enable()
        record = collector.measure_sla(
            contract_id="CTR-003",
            trace_id="trace-slow",
            latency_us=25000,
            sla_p99_us=10000,
        )
        assert record.passed is False

    def test_contract_drift_detection(self):
        collector = ContractMetricsCollector()
        collector._field_baselines["CTR-002:signal_value"] = {"median": 0.01, "std": 0.1}

        alert = collector.detect_contract_drift(
            contract_id="CTR-002",
            field_name="signal_value",
            current_value=1.5,
        )
        assert isinstance(alert, DriftAlert)
        assert alert.contract_id == "CTR-002"
        assert alert.statistic == "z_score"

    def test_contract_drift_no_alert_for_normal_value(self):
        collector = ContractMetricsCollector()
        collector._field_baselines["CTR-002:signal_value"] = {"median": 0.01, "std": 0.1}

        alert = collector.detect_contract_drift(
            contract_id="CTR-002",
            field_name="signal_value",
            current_value=0.02,
        )
        assert alert is None

    def test_violation_counter(self):
        collector = ContractMetricsCollector()
        collector.record_violation("CTR-005")
        collector.record_violation("CTR-005")
        assert collector._violation_counts["CTR-005"] == 2

    def test_metrics_get_stats_empty(self):
        collector = ContractMetricsCollector()
        stats = collector.get_stats()
        assert stats["total_violations"] == 0
        assert stats["active_drift_alerts"] == 0


class TestPhaseFL13:
    """L13 — Experimentation: 实验管线 + A/B"""

    def test_experiment_config_resource(self):
        config = ExperimentConfig(
            experiment_id=f"exp-{uuid.uuid4().hex[:8]}",
            hypothesis="Momentum factor improves Sharpe",
            control_params={"momentum_window": 20},
            treatment_params={"momentum_window": 40},
            metrics=["sharpe_ratio", "max_drawdown"],
            start_date="2025-01-01",
            end_date="2025-06-30",
        )
        assert config.experiment_id.startswith("exp-")
        assert config.status == "registered"
        assert len(config.metrics) == 2

    def test_experiment_metric_resource(self):
        metric = ExperimentMetric(
            experiment_id="exp-test",
            metric_name="sharpe_ratio",
            control_value=1.0,
            treatment_value=1.3,
            effect_size=0.6,
            p_value=0.01,
            is_significant=True,
        )
        assert metric.metric_name == "sharpe_ratio"
        assert metric.effect_size == 0.6
        assert metric.is_significant is True

    def test_default_experiment_pipeline_ab_test(self):
        pipeline = DefaultExperimentPipeline()
        config = ExperimentConfig(
            experiment_id="exp-ab-001",
            hypothesis="Larger window improves Sharpe",
            control_params={"sharpe_ratio": 1.0, "max_drawdown": 0.15},
            treatment_params={"sharpe_ratio": 1.3, "max_drawdown": 0.12},
            metrics=["sharpe_ratio", "max_drawdown"],
            start_date="2025-01-01",
            end_date="2025-03-31",
        )

        results = pipeline.run(config, str(uuid.uuid4()))
        assert len(results) == 2
        assert isinstance(results[0], ExperimentMetric)

        sharpe_result = [r for r in results if r.metric_name == "sharpe_ratio"][0]
        assert sharpe_result.control_value == 1.0
        assert sharpe_result.treatment_value == 1.3
        assert sharpe_result.is_significant is True

        cached = pipeline.get_results("exp-ab-001")
        assert len(cached) == 2

    def test_experiment_pipeline_base_is_abstract(self):
        assert ExperimentPipelineBase.__abstractmethods__ == frozenset({"run"})

    def test_scout_agent_base_is_abstract(self):
        assert ScoutAgentBase.__abstractmethods__ == frozenset({"scout", "archive_to_kms"})


class TestPhaseFBackpressure:
    """Backpressure: CTR-BP-001~003 三态管理"""

    def test_backpressure_manager_pause(self):
        mgr = BackpressureManager()
        state = emit_pause(mgr, "600519", 5000, "Queue full")
        assert state.state == BpState.PAUSED
        assert mgr.is_blocked("600519") is True
        assert len(mgr.get_all_paused()) == 1
        mgr.clear()

    def test_backpressure_manager_throttle(self):
        mgr = BackpressureManager()
        state = emit_throttle(mgr, "000858", 10, "Queue growing")
        assert state.state == BpState.THROTTLED
        assert state.max_rate_per_sec == 10
        assert len(mgr.get_all_throttled()) == 1
        assert mgr.is_blocked("000858") is False
        mgr.clear()

    def test_backpressure_manager_resume_from_pause(self):
        mgr = BackpressureManager()
        emit_pause(mgr, "600519", 5000, "Queue full")
        assert mgr.is_blocked("600519") is True

        state = emit_resume(mgr, "600519", "Queue drained")
        assert state.state == BpState.NORMAL
        assert mgr.is_blocked("600519") is False
        assert len(mgr.get_all_paused()) == 0
        mgr.clear()

    def test_backpressure_manager_resume_from_throttle(self):
        mgr = BackpressureManager()
        emit_throttle(mgr, "000858", 5, "Growing")
        emit_resume(mgr, "000858", "Normalized")
        assert mgr.get_state("000858").state == BpState.NORMAL
        mgr.clear()

    def test_backpressure_manager_multiple_symbols(self):
        mgr = BackpressureManager()
        emit_pause(mgr, "A", 1000, "reason_a")
        emit_pause(mgr, "B", 2000, "reason_b")
        emit_throttle(mgr, "C", 5, "reason_c")

        assert len(mgr.get_all_paused()) == 2
        assert len(mgr.get_all_throttled()) == 1
        assert mgr.is_blocked("A") is True
        assert mgr.is_blocked("B") is True
        assert mgr.is_blocked("C") is False
        assert mgr.is_blocked("D") is False
        mgr.clear()

    def test_backpressure_manager_auto_resume_on_timeout(self):
        mgr = BackpressureManager()
        state = mgr.handle_pause(
            __import__(
                "zephyr.shared.contracts.backpressure.pause", fromlist=["BackpressurePause"]
            ).BackpressurePause(
                signal_id="bp-001",
                symbol="600519",
                duration_ms=1,
                reason="test",
                idempotency_key=str(uuid.uuid4()),
            )
        )
        assert state.state == BpState.PAUSED

        import time

        time.sleep(0.01)

        assert mgr.is_blocked("600519") is False
        mgr.clear()

    def test_backpressure_manager_stats(self):
        mgr = BackpressureManager()
        emit_pause(mgr, "A", 1000, "r1")
        emit_throttle(mgr, "B", 5, "r2")

        stats = mgr.get_stats()
        assert stats["paused_count"] == 1
        assert stats["throttled_count"] == 1
        assert stats["total_events"] == 2
        mgr.clear()

    def test_backpressure_manager_callbacks_fired(self):
        mgr = BackpressureManager()
        events: list[str] = []

        mgr.register_on_pause(lambda s: events.append(f"pause:{s.symbol}"))
        mgr.register_on_resume(lambda s: events.append(f"resume:{s.symbol}"))
        mgr.register_on_throttle(lambda s: events.append(f"throttle:{s.symbol}"))

        emit_pause(mgr, "600519", 1000, "test")
        emit_throttle(mgr, "000858", 5, "test")
        emit_resume(mgr, "600519", "normal")
        emit_resume(mgr, "000858", "recovered")

        assert "pause:600519" in events
        assert "throttle:000858" in events
        assert "resume:600519" in events
        assert "resume:000858" in events
        mgr.clear()


class TestPhaseFP1Contracts:
    """P1 契约显式验证 — 测试方法名与 cross_layer_contracts.yaml 中 CTR-P1-xxx 编号对齐"""

    def test_ctr_p1_001_factor_monitor_report(self):
        rpt = FactorMonitorReport(
            factor_id="momentum_20d",
            evaluation_date="2026-05-01",
            ic_mean=0.02,
            ic_std=0.05,
            ic_ir=0.4,
            rank_ic=0.018,
            is_effective=True,
            decay_alert=False,
            idempotency_key=str(uuid.uuid4()),
        )
        assert isinstance(rpt, FactorMonitorReport)
        assert rpt.factor_id == "momentum_20d"

    def test_ctr_p1_002_macro_factor_signal(self):
        mfs = MacroFactorSignal(
            factor_id="macro.pmi.cn.v1",
            as_of_date="2026-05-01",
            macro_regime="expansion",
            signal_value=0.5,
            data_source="nbs",
            release_lag_days=15,
            idempotency_key=str(uuid.uuid4()),
        )
        assert isinstance(mfs, MacroFactorSignal)
        assert mfs.macro_regime == "expansion"

    def test_ctr_p1_003_capital_allocation_result(self):
        car = CapitalAllocationResult(
            allocation_date=datetime.now(UTC).strftime("%Y-%m-%d"),
            total_allocated_weight=1.0,
            allocation_method="risk_parity",
            strategy_allocations={"600519": 0.4, "000858": 0.3, "601318": 0.3},
            idempotency_key=str(uuid.uuid4()),
        )
        assert isinstance(car, CapitalAllocationResult)
        assert len(car.strategy_allocations) == 3

    def test_ctr_p1_004_model_serving_request(self):
        request = ModelServingRequest(
            request_id=f"msr-{uuid.uuid4().hex[:8]}",
            model_id="model-01",
            model_version="v1.0",
            input_features={"feature_a": 1.0},
            idempotency_key=str(uuid.uuid4()),
        )
        assert isinstance(request, ModelServingRequest)
        assert request.model_id == "model-01"

    def test_ctr_p1_005_model_serving_response(self):
        response = ModelServingResponse(
            request_id=f"msr-resp-{uuid.uuid4().hex[:8]}",
            model_id="model-01",
            prediction=0.75,
            prediction_type="factor_value",
            confidence=0.92,
            inference_ms=15,
            idempotency_key=str(uuid.uuid4()),
        )
        assert isinstance(response, ModelServingResponse)
        assert response.prediction == 0.75
        assert response.confidence == 0.92

    def test_ctr_p1_006_strategy_lifecycle_event(self):
        event = StrategyLifecycleEvent(
            strategy_id="test-strat",
            event_type="activated",
            event_timestamp=datetime.now(UTC).isoformat(),
            triggered_by="scheduler",
            reason="Daily rebalance",
            previous_status="idle",
            new_status="active",
            idempotency_key=str(uuid.uuid4()),
        )
        assert isinstance(event, StrategyLifecycleEvent)

    def test_ctr_p1_007_execution_report(self):
        report = ExecutionReport(
            order_id=f"ord-{uuid.uuid4().hex[:8]}",
            symbol="600519",
            direction="BUY",
            intended_quantity=100,
            actual_quantity=100,
            intended_price=Decimal("100"),
            vwap_price=Decimal("100.5"),
            slippage_bps=5.0,
            commission=Decimal("6"),
            execution_start=datetime.now(UTC).isoformat(),
            execution_end=datetime.now(UTC).isoformat(),
            broker_id="simulation",
            idempotency_key=str(uuid.uuid4()),
        )
        assert isinstance(report, ExecutionReport)

    def test_ctr_p1_008_risk_dashboard_snapshot(self):
        snapshot = RiskDashboardSnapshot(
            snapshot_time=datetime.now(UTC).isoformat(),
            portfolio_id="test-portfolio",
            portfolio_var_1d=50000.0,
            max_drawdown_current=0.05,
            gross_leverage=1.2,
            top_position_concentration=0.15,
            overall_risk_score=0.35,
            idempotency_key=str(uuid.uuid4()),
        )
        assert isinstance(snapshot, RiskDashboardSnapshot)

    def test_ctr_p1_009_performance_attribution_report(self):
        report = PerformanceAttributionReport(
            period_start="2025-01-01",
            period_end="2025-03-31",
            portfolio_id="test-portfolio",
            total_return=0.08,
            allocation_effect=0.03,
            selection_effect=0.04,
            interaction_effect=0.01,
            transaction_cost_drag=0.002,
            idempotency_key=str(uuid.uuid4()),
        )
        assert isinstance(report, PerformanceAttributionReport)
        assert abs(report.total_return - 0.08) < 0.001

    def test_ctr_p1_010_system_configuration(self):
        cfg = SystemConfiguration(
            config_id=f"cfg-{uuid.uuid4().hex[:8]}",
            config_type="risk",
            environment="production",
            version="1.0",
            is_active=True,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            idempotency_key=str(uuid.uuid4()),
        )
        assert isinstance(cfg, SystemConfiguration)

    def test_ctr_p1_011_risk_metrics_report(self):
        report = RiskMetricsReport(
            portfolio_id="test-portfolio",
            as_of_date=datetime.now(UTC),
            var_1d_95=50000.0,
            var_1d_99=75000.0,
            cvar_1d_95=65000.0,
            cvar_1d_99=90000.0,
            sharpe_ratio=1.2,
            sortino_ratio=1.5,
            beta=1.05,
            max_drawdown=0.12,
            current_drawdown=0.03,
            confidence_level=0.95,
            lookback_period=252,
            calculation_method="historical",
            volatility_1d=0.015,
            volatility_1m=0.06,
            idempotency_key=str(uuid.uuid4()),
        )
        assert isinstance(report, RiskMetricsReport)

    def test_ctr_p1_012_compliance_rule(self):
        rule = ComplianceRule(
            rule_id="CMP-001",
            rule_name="禁止内幕交易",
            rule_type="regulatory",
            rule_logic="insider_trading_detection",
            severity="critical",
            description="禁止基于重大非公开信息进行交易",
            enforcement_action="block",
            jurisdiction="cn_a_share",
            is_active=True,
            version="1.0",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            idempotency_key=str(uuid.uuid4()),
        )
        assert isinstance(rule, ComplianceRule)
        assert rule.severity == "critical"
        assert rule.enforcement_action == "block"

    def test_ctr_p1_013_telemetry_emitter(self):
        emitter = TelemetryEmitter(
            emitter_id=f"te-{uuid.uuid4().hex[:8]}",
            emitter_type="metrics",
            metric_name="trade_latency_ms",
            metric_type="gauge",
            metric_value=45.2,
            source_module="l06-trade-execution",
            correlation_id=f"corr-{uuid.uuid4().hex[:8]}",
            timestamp=datetime.now(UTC),
            labels={},
            idempotency_key=str(uuid.uuid4()),
        )
        assert isinstance(emitter, TelemetryEmitter)
        assert emitter.metric_value == 45.2

    def test_ctr_p1_014_experiment_result(self):
        result = ExperimentResult(
            experiment_id=f"er-{uuid.uuid4().hex[:8]}",
            experiment_name="Momentum Window Test",
            experiment_type="factor_ablation",
            hypothesis="40-day momentum outperforms 20-day",
            variant_a_description="20-day window",
            variant_b_description="40-day window",
            variant_b_improvement=0.3,
            conclusion="supported",
            confidence=0.85,
            p_value=0.02,
            sample_size=500,
            start_timestamp=datetime.now(UTC),
            end_timestamp=datetime.now(UTC),
            metrics={"sharpe_diff": 0.3},
            actionable_suggestions=["deploy_variant_b"],
            idempotency_key=str(uuid.uuid4()),
        )
        assert isinstance(result, ExperimentResult)
        assert result.hypothesis == "40-day momentum outperforms 20-day"
        assert result.conclusion == "supported"
        assert result.confidence >= 0.7

    def test_ctr_p1_015_synthesized_signal(self):
        syn = SynthesizedSignal(
            signal_id=f"syn-{uuid.uuid4().hex[:8]}",
            symbol="600519",
            as_of_timestamp=datetime.now(UTC),
            signal_value=0.5,
            signal_direction="LONG",
            confidence=0.8,
            generation_latency_ms=5,
            idempotency_key=str(uuid.uuid4()),
        )
        assert isinstance(syn, SynthesizedSignal)
        assert syn.signal_direction == "LONG"
