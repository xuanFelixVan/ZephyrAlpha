# [A_test] module_id: MOD-GOV_phase_e_layers | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-330 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.integration.test_phase_e_layers
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""Phase E — Remaining Layer Integration Tests

L01/L02/L08/L12 四层集成测试——补齐 Phase D 未覆盖的层。

Phase E | Safety: MEDIUM
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest


class TestL01Infrastructure:
    """L01 Infrastructure — config + kill switch"""

    def test_appconfig_default_creation(self):
        from zephyr.infrastructure.config import AppConfig

        cfg = AppConfig()
        assert cfg.env == "dev"
        assert cfg.log_level == "INFO"
        assert "akshare" in cfg.data_source_priority

    def test_appconfig_frozen(self):
        from zephyr.infrastructure.config import AppConfig

        cfg = AppConfig(env="prod", log_level="WARN")
        with pytest.raises(Exception):
            cfg.env = "dev"  # type: ignore[misc]

    def test_load_config_returns_appconfig(self):
        from zephyr.infrastructure.config import AppConfig, load_config

        cfg = load_config()
        assert isinstance(cfg, AppConfig)

    def test_reload_config_returns_appconfig(self):
        from zephyr.infrastructure.config import AppConfig, reload_config

        cfg = reload_config()
        assert isinstance(cfg, AppConfig)

    def test_kill_switch_simulator_trigger(self):
        from zephyr.infrastructure.kill_switch_sim import KillSwitchSimulator

        sim = KillSwitchSimulator(target_ms=1.0)
        probe = sim.trigger()
        assert probe is not None
        assert probe.latency_us >= 0
        assert probe.hardware_model == "T0_SIMULATOR"

    def test_kill_switch_simulator_health_check(self):
        from zephyr.infrastructure.kill_switch_sim import KillSwitchSimulator

        sim = KillSwitchSimulator(target_ms=1000.0)
        ok = sim.health_check()
        assert ok is True

    def test_kill_switch_simulator_ack_callback(self):
        from zephyr.infrastructure.kill_switch_sim import KillSwitchSimulator

        sim = KillSwitchSimulator()

        called = []
        sim.register_ack_callback(lambda: called.append(True))
        sim.trigger()
        assert len(called) == 1


class TestL02AlphaFactor:
    """L02 Alpha Factor — registry + meta + autodiscover"""

    def test_factor_meta_creation(self):
        from zephyr.factor.factor_base import FactorMeta

        meta = FactorMeta(
            factor_id="test_momentum",
            name="Test Momentum",
            domain="technical",
        )
        assert meta.factor_id == "test_momentum"
        assert meta.domain == "technical"
        assert meta.version == "1.0.0"
        assert isinstance(meta.tags, list)

    def test_factor_registry_register_and_get(self):
        from zephyr.factor.factor_base import (
            FactorBase,
            FactorMeta,
            FactorRegistry,
        )

        FactorRegistry.clear()

        @FactorRegistry.register
        class TestFactor(FactorBase):
            meta = FactorMeta(
                factor_id="test_factor_001",
                name="Test Factor",
                domain="technical",
            )

            def compute(self, data, **kwargs):
                import pandas as pd

                return pd.Series([1.0, 2.0], name=data.index[:2])

        assert len(FactorRegistry.registry) >= 1
        cls = FactorRegistry.get("test_factor_001")
        assert cls is TestFactor
        FactorRegistry.clear()

    def test_factor_registry_list_all(self):
        from zephyr.factor.factor_base import (
            FactorBase,
            FactorMeta,
            FactorRegistry,
        )

        FactorRegistry.clear()

        @FactorRegistry.register
        class FactorA(FactorBase):
            meta = FactorMeta(factor_id="factor_a", name="A", domain="technical")

            def compute(self, data, **kwargs):
                import pandas as pd

                return pd.Series(name=data.index[:1])

        @FactorRegistry.register
        class FactorB(FactorBase):
            meta = FactorMeta(factor_id="factor_b", name="B", domain="fundamental")

            def compute(self, data, **kwargs):
                import pandas as pd

                return pd.Series(name=data.index[:1])

        all_meta = FactorRegistry.list_all()
        assert len(all_meta) == 2

        tech = FactorRegistry.list_by_domain("technical")
        assert len(tech) == 1
        assert tech[0].factor_id == "factor_a"

        FactorRegistry.clear()

    def test_factor_registry_duplicate_raises(self):
        from zephyr.factor.factor_base import (
            FactorBase,
            FactorMeta,
            FactorRegistry,
        )

        FactorRegistry.clear()

        @FactorRegistry.register
        class FactorX(FactorBase):
            meta = FactorMeta(factor_id="dup_factor", name="X", domain="technical")

            def compute(self, data, **kwargs):
                import pandas as pd

                return pd.Series(name=data.index[:1])

        with pytest.raises(ValueError):

            @FactorRegistry.register
            class FactorY(FactorBase):
                meta = FactorMeta(factor_id="dup_factor", name="Y", domain="technical")

                def compute(self, data, **kwargs):
                    import pandas as pd

                    return pd.Series(name=data.index[:1])

        FactorRegistry.clear()

    def test_factor_registry_missing_meta_raises(self):
        from zephyr.factor.factor_base import FactorBase, FactorRegistry

        FactorRegistry.clear()

        with pytest.raises(AttributeError):

            @FactorRegistry.register
            class BadFactor(FactorBase):
                def compute(self, data, **kwargs):
                    import pandas as pd

                    return pd.Series(name=data.index[:1])

        FactorRegistry.clear()

    def test_autodiscover_factors_runs(self):
        from zephyr.factor.factor_base import autodiscover_factors

        autodiscover_factors()


class TestL08HumanAIInterface:
    """L08 Human-AI Interface — notifications + approvals"""

    def test_notification_level_enum(self):
        from zephyr.frontend.interface_base import NotificationLevel

        assert NotificationLevel.INFO.value == "info"
        assert NotificationLevel.WARNING.value == "warning"
        assert NotificationLevel.ERROR.value == "error"
        assert NotificationLevel.CRITICAL.value == "critical"

    def test_approval_action_enum(self):
        from zephyr.frontend.interface_base import ApprovalAction

        assert ApprovalAction.APPROVE.value == "approve"
        assert ApprovalAction.REJECT.value == "reject"
        assert ApprovalAction.DELEGATE.value == "delegate"
        assert ApprovalAction.ESCALATE.value == "escalate"

    def test_notification_creation(self):
        from zephyr.frontend.interface_base import (
            Notification,
            NotificationLevel,
        )

        notif = Notification(
            notification_id="notif-001",
            title="Risk Alert",
            body="Position limit exceeded for 600519",
            level=NotificationLevel.WARNING,
            source_layer="L04",
        )
        assert notif.notification_id == "notif-001"
        assert notif.level == NotificationLevel.WARNING
        assert notif.source_layer == "L04"

    def test_approval_request_creation(self):
        from zephyr.frontend.interface_base import ApprovalRequest

        req = ApprovalRequest(
            request_id="req-001",
            action="override_position_limit",
            reason="Client request",
            requester="trader_001",
            context={"symbol": "600519", "target_weight": 0.15},
        )
        assert req.request_id == "req-001"
        assert req.status == "pending"
        assert req.action == "override_position_limit"
        assert "symbol" in req.context

    def test_approval_request_expiry(self):
        from zephyr.frontend.interface_base import ApprovalRequest

        expiry = datetime.now(UTC) + timedelta(hours=1)
        req = ApprovalRequest(
            request_id="req-002",
            action="approve_large_order",
            reason="Institutional flow",
            requester="system",
            expires_at=expiry,
        )
        assert req.expires_at is not None
        assert req.expires_at > datetime.now(UTC)
        assert req.status == "pending"


class TestL12SystemTelemetry:
    """L12 System Telemetry — contract metrics collector"""

    def test_sla_record_creation(self):
        from zephyr.infrastructure.system_telemetry.contract_metrics import SlaRecord

        record = SlaRecord(
            contract_id="CTR-001",
            trace_id="trace-abc123",
            latency_us=500,
            start_span_id="span-start",
            end_span_id="span-end",
            passed=True,
        )
        assert record.contract_id == "CTR-001"
        assert record.latency_us == 500
        assert record.passed is True
        assert record.recorded_at is not None

    def test_drift_alert_creation(self):
        from zephyr.infrastructure.system_telemetry.contract_metrics import DriftAlert

        alert = DriftAlert(
            contract_id="CTR-002",
            field_name="signal_value",
            statistic="z_score",
            current_value=7.0,
            baseline_value=1.2,
            deviation_pct=483.3,
        )
        assert alert.contract_id == "CTR-002"
        assert alert.field_name == "signal_value"
        assert alert.deviation_pct > 100
        assert alert.detected_at is not None

    def test_collector_measure_sla_passed(self):
        from zephyr.infrastructure.system_telemetry.contract_metrics import (
            ContractMetricsCollector,
        )

        collector = ContractMetricsCollector()
        collector.enable()
        record = collector.measure_sla(
            contract_id="CTR-004",
            trace_id="trace-xyz",
            latency_us=2000,
            sla_p99_us=5000,
        )
        assert record.passed is True
        assert record.contract_id == "CTR-004"

    def test_collector_measure_sla_failed(self):
        from zephyr.infrastructure.system_telemetry.contract_metrics import (
            ContractMetricsCollector,
        )

        collector = ContractMetricsCollector()
        collector.enable()
        record = collector.measure_sla(
            contract_id="CTR-005",
            trace_id="trace-fail",
            latency_us=15000,
            sla_p99_us=5000,
        )
        assert record.passed is False

    def test_collector_record_violation(self):
        from zephyr.infrastructure.system_telemetry.contract_metrics import (
            ContractMetricsCollector,
        )

        collector = ContractMetricsCollector()
        collector.record_violation("CTR-001")
        collector.record_violation("CTR-001")
        stats = collector.get_stats()
        assert stats["total_violations"] == 2

    def test_collector_detect_drift_with_explicit_baseline(self):
        from zephyr.infrastructure.system_telemetry.contract_metrics import (
            ContractMetricsCollector,
        )

        collector = ContractMetricsCollector()
        collector.enable()
        alert = collector.detect_contract_drift(
            contract_id="CTR-003",
            field_name="momentum",
            current_value=50.0,
            baseline_median=10.0,
            baseline_std=2.0,
        )
        assert alert is not None
        assert alert.contract_id == "CTR-003"
        assert alert.deviation_pct > 100

    def test_collector_get_stats_defaults(self):
        from zephyr.infrastructure.system_telemetry.contract_metrics import get_contract_metrics

        collector = get_contract_metrics()
        stats = collector.get_stats()
        assert "sla_p99_pass_rate_100" in stats
        assert "total_violations" in stats
        assert "active_drift_alerts" in stats
        assert "tracked_contracts" in stats

    def test_get_contract_metrics_singleton(self):
        from zephyr.infrastructure.system_telemetry.contract_metrics import get_contract_metrics

        c1 = get_contract_metrics()
        c2 = get_contract_metrics()
        assert c1 is c2
