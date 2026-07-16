# [A_test] module_id: SRC-TST-1933 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-552 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.resource_optimization.test_self_healing
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
from __future__ import annotations

"""
test_self_healing.py - Self-healing + config + EventBus + Audit integration tests
==================================================================================

TASK-INF-0143 Phase 5 verification.
"""


import time
from unittest.mock import MagicMock, patch

import yaml

from zephyr.trading.resource_optimization import (
    OptimizationStrategy,
    PressureLevel,
    ResourceOptimizationEngine,
    ResourceSnapshot,
)


class TestConfigLoad:
    def setup_method(self):
        ResourceOptimizationEngine.reset()

    def teardown_method(self):
        ResourceOptimizationEngine.reset()

    def test_load_config_from_file(self, tmp_path):
        cfg = {
            "pressure_thresholds": {
                "memory_warning_percent": 70.0,
                "memory_critical_percent": 80.0,
                "memory_emergency_percent": 90.0,
            },
            "hysteresis": {"confirmation_count": 3, "cooldown_seconds": 30.0},
            "self_healing": {"enabled": True, "max_retries": 5},
        }
        cfg_path = tmp_path / "resource_optimization.yaml"
        cfg_path.write_text(yaml.dump(cfg), encoding="utf-8")

        engine = ResourceOptimizationEngine()
        engine._config_path = str(cfg_path)
        engine._apply_config(str(cfg_path))

        assert engine._thresholds.memory_warning_percent == 70.0
        assert engine._thresholds.memory_critical_percent == 80.0
        assert engine._hysteresis.confirmation_count == 3
        assert engine._self_healing_max_retries == 5

    def test_config_hot_reload(self, tmp_path):
        cfg_v1 = {"pressure_thresholds": {"memory_warning_percent": 70.0}}
        cfg_path = tmp_path / "resource_optimization.yaml"
        cfg_path.write_text(yaml.dump(cfg_v1), encoding="utf-8")

        engine = ResourceOptimizationEngine()
        engine._config_path = str(cfg_path)
        engine._apply_config(str(cfg_path))
        assert engine._thresholds.memory_warning_percent == 70.0

        time.sleep(0.05)
        cfg_v2 = {"pressure_thresholds": {"memory_warning_percent": 60.0}}
        cfg_path.write_text(yaml.dump(cfg_v2), encoding="utf-8")

        engine._check_config_reload()
        assert engine._thresholds.memory_warning_percent == 60.0

    def test_config_missing_file_no_crash(self):
        engine = ResourceOptimizationEngine()
        engine._config_path = "/nonexistent/path.yaml"
        engine._check_config_reload()


class TestSelfHealing:
    def setup_method(self):
        ResourceOptimizationEngine.reset()

    def teardown_method(self):
        ResourceOptimizationEngine.reset()

    def test_self_heal_disabled(self):
        engine = ResourceOptimizationEngine()
        engine._self_healing_enabled = False
        result = engine._self_heal_cycle(ResourceSnapshot(memory_percent=90.0, pressure=PressureLevel.CRITICAL))
        assert result is None

    def test_self_heal_normal_pressure_skipped(self):
        engine = ResourceOptimizationEngine()
        result = engine._self_heal_cycle(ResourceSnapshot(pressure=PressureLevel.NORMAL))
        assert result is None

    def test_select_healing_strategy(self):
        engine = ResourceOptimizationEngine()
        assert engine._select_healing_strategy(PressureLevel.EMERGENCY) == OptimizationStrategy.MEMORY_COMPACT
        assert engine._select_healing_strategy(PressureLevel.CRITICAL) == OptimizationStrategy.MEMORY_COMPACT
        assert engine._select_healing_strategy(PressureLevel.WARNING) == OptimizationStrategy.SCHEDULE_ADAPT

    @patch.object(ResourceOptimizationEngine, "optimize")
    @patch.object(ResourceOptimizationEngine, "snapshot")
    def test_self_heal_succeeds_on_first_try(self, mock_snap, mock_opt):
        engine = ResourceOptimizationEngine()
        engine._self_healing_verification_delay_s = 0.0

        from zephyr.shared.lifecycle.resource_optimization_models import OptimizationResult

        mock_opt.return_value = OptimizationResult(
            strategy=OptimizationStrategy.MEMORY_COMPACT,
            success=True,
            snapshot_before=ResourceSnapshot(memory_percent=90.0, pressure=PressureLevel.CRITICAL),
            snapshot_after=ResourceSnapshot(memory_percent=70.0, pressure=PressureLevel.WARNING),
            actions_taken=["gc.collect()"],
        )

        critical_snap = ResourceSnapshot(memory_percent=90.0, pressure=PressureLevel.CRITICAL)
        warning_snap = ResourceSnapshot(memory_percent=70.0, pressure=PressureLevel.WARNING)
        mock_snap.return_value = warning_snap

        result = engine._self_heal_cycle(critical_snap)
        assert result is not None
        assert result.success is True

    @patch.object(ResourceOptimizationEngine, "optimize")
    @patch.object(ResourceOptimizationEngine, "snapshot")
    def test_self_heal_retries_on_failure(self, mock_snap, mock_opt):
        engine = ResourceOptimizationEngine()
        engine._self_healing_verification_delay_s = 0.0
        engine._self_healing_max_retries = 2

        mock_opt.return_value = MagicMock(success=False)
        mock_snap.return_value = ResourceSnapshot(memory_percent=90.0, pressure=PressureLevel.CRITICAL)

        result = engine._self_heal_cycle(mock_snap.return_value)
        assert result is None
        assert mock_opt.call_count == 2


class TestEventBusIntegration:
    def setup_method(self):
        ResourceOptimizationEngine.reset()

    def teardown_method(self):
        ResourceOptimizationEngine.reset()

    def test_emit_skipped_when_disabled(self):
        engine = ResourceOptimizationEngine()
        engine._eventbus_enabled = False
        engine._emit_pressure_event(ResourceSnapshot(pressure=PressureLevel.WARNING))

    def test_emit_skipped_when_same_level(self):
        engine = ResourceOptimizationEngine()
        engine._last_pressure_level = PressureLevel.WARNING
        engine._emit_pressure_event(ResourceSnapshot(pressure=PressureLevel.WARNING))

    @patch("zephyr.infrastructure.shared_services.lifecycle.resource_optimization_engine.get_bus", create=True)
    def test_emit_on_pressure_change(self, mock_get_bus):
        engine = ResourceOptimizationEngine()
        engine._eventbus_enabled = True
        engine._last_pressure_level = PressureLevel.NORMAL

        mock_bus = MagicMock()
        mock_get_bus.return_value = mock_bus

        with patch.dict("sys.modules", {"zephyr.shared.event_bus": MagicMock(get_bus=mock_get_bus)}):
            engine._emit_pressure_event(
                ResourceSnapshot(
                    pressure=PressureLevel.WARNING,
                    memory_percent=80.0,
                    cpu_percent=50.0,
                    process_count=30,
                )
            )


class TestAuditIntegration:
    def setup_method(self):
        ResourceOptimizationEngine.reset()

    def teardown_method(self):
        ResourceOptimizationEngine.reset()

    def test_audit_skipped_when_disabled(self):
        engine = ResourceOptimizationEngine()
        engine._audit_enabled = False
        from zephyr.shared.lifecycle.resource_optimization_models import OptimizationRecord

        record = OptimizationRecord(
            trigger=PressureLevel.WARNING,
            strategy=OptimizationStrategy.MEMORY_COMPACT,
        )
        engine._audit_optimization(record)

    @patch("zephyr.infrastructure.shared_services.lifecycle.resource_optimization_engine.write_to_core", create=True)
    def test_audit_called_when_enabled(self, mock_write):
        engine = ResourceOptimizationEngine()
        engine._audit_enabled = True

        from zephyr.shared.lifecycle.resource_optimization_models import OptimizationRecord

        record = OptimizationRecord(
            trigger=PressureLevel.WARNING,
            strategy=OptimizationStrategy.MEMORY_COMPACT,
            actions_taken=["gc.collect()"],
            success=True,
        )

        with patch.dict("sys.modules", {"zephyr.gov_audit.bridge": MagicMock(write_to_core=mock_write)}):
            engine._audit_optimization(record)
