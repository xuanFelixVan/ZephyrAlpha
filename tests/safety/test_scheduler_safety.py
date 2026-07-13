# [A_test] module_id: SRC-TST-1531 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §

# [MODULE] tests.test_scheduler_safety

# [INVARIANTS] SafetyGateManager.run_safety_gates returns dict[str, bool]

# [MODIFY-GUARD] none

# [CONSUMERS] none

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] pytest exit 0

# [TESTS] tests/test_scheduler_safety.py
# [TTL] task_bound

from __future__ import annotations

import importlib
import types
from dataclasses import dataclass
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from zephyr.feedback_loop.scheduler_safety import SafetyGateManager


def _make_anomaly(evidence: dict[str, Any] | None = None, anomaly_id: str = "anomaly-001") -> Any:
    @dataclass
    class FakeAnomaly:
        evidence: dict[str, Any]
        anomaly_id: str = "anomaly-001"

    if evidence is None:
        evidence = {"metric_name": "cpu_usage", "value": 0.85}
    return FakeAnomaly(evidence=evidence, anomaly_id=anomaly_id)


def _make_diagnosis() -> Any:
    return MagicMock(spec=["severity", "root_cause"], severity="MEDIUM", root_cause="test")


def _mocked_manager() -> SafetyGateManager:
    mgr = SafetyGateManager.__new__(SafetyGateManager)
    mgr.numerical_guard = MagicMock()
    mgr.temporal_guard = MagicMock()
    mgr.wireheading_prevention = MagicMock()
    mgr.deployment_suppression = MagicMock()
    mgr.config_reload_guard = MagicMock()
    mgr.boot_attestation = MagicMock()
    mgr._fle_gate_cache = {}
    return mgr


def _setup_mocked_guards(mgr: SafetyGateManager) -> None:
    mgr.numerical_guard.validate.return_value = {"classification": "CLEAN"}
    mgr.temporal_guard.validate_timestamp.return_value = {"valid": True}
    mgr.wireheading_prevention.validate_metric.return_value = True
    mgr.deployment_suppression.check.return_value = {"allowed": True}
    mgr.config_reload_guard.check_stale_acks.return_value = []


class TestSafetyGateManagerInstantiation:
    def test_mocked_instantiation_has_all_guard_fields(self):
        mgr = _mocked_manager()
        assert mgr.numerical_guard is not None
        assert mgr.temporal_guard is not None
        assert mgr.wireheading_prevention is not None
        assert mgr.deployment_suppression is not None
        assert mgr.config_reload_guard is not None
        assert mgr.boot_attestation is not None

    def test_fle_gate_cache_initially_empty(self):
        mgr = _mocked_manager()
        assert mgr._fle_gate_cache == {}

    def test_fle_gate_cache_is_dict(self):
        mgr = _mocked_manager()
        assert isinstance(mgr._fle_gate_cache, dict)


class TestRunSafetyGates:
    def test_returns_dict_of_bools_on_clean_inputs(self):
        mgr = _mocked_manager()
        _setup_mocked_guards(mgr)

        with patch.object(mgr, "_dispatch_fle_gates", return_value={}):
            result = mgr.run_safety_gates(_make_anomaly(), _make_diagnosis())

        assert isinstance(result, dict)
        assert all(isinstance(v, bool) for v in result.values())
        assert result["numerical_stability"] is True
        assert result["temporal_integrity"] is True
        assert result["wireheading"] is True
        assert result["deployment_suppression"] is True
        assert result["config_consistency"] is True

    def test_numerical_stability_false_on_non_clean(self):
        mgr = _mocked_manager()
        _setup_mocked_guards(mgr)
        mgr.numerical_guard.validate.return_value = {"classification": "ANOMALY"}

        with patch.object(mgr, "_dispatch_fle_gates", return_value={}):
            result = mgr.run_safety_gates(_make_anomaly(), _make_diagnosis())

        assert result["numerical_stability"] is False

    def test_temporal_integrity_false_on_invalid(self):
        mgr = _mocked_manager()
        _setup_mocked_guards(mgr)
        mgr.temporal_guard.validate_timestamp.return_value = {"valid": False}

        with patch.object(mgr, "_dispatch_fle_gates", return_value={}):
            result = mgr.run_safety_gates(_make_anomaly(), _make_diagnosis())

        assert result["temporal_integrity"] is False

    def test_wireheading_false_when_bool_false(self):
        mgr = _mocked_manager()
        _setup_mocked_guards(mgr)
        mgr.wireheading_prevention.validate_metric.return_value = False

        with patch.object(mgr, "_dispatch_fle_gates", return_value={}):
            result = mgr.run_safety_gates(_make_anomaly(), _make_diagnosis())

        assert result["wireheading"] is False

    def test_wireheading_true_when_non_bool_returned(self):
        mgr = _mocked_manager()
        _setup_mocked_guards(mgr)
        mgr.wireheading_prevention.validate_metric.return_value = {"status": "ok"}

        with patch.object(mgr, "_dispatch_fle_gates", return_value={}):
            result = mgr.run_safety_gates(_make_anomaly(), _make_diagnosis())

        assert result["wireheading"] is True

    def test_deployment_suppression_false_when_not_allowed(self):
        mgr = _mocked_manager()
        _setup_mocked_guards(mgr)
        mgr.deployment_suppression.check.return_value = {"allowed": False}

        with patch.object(mgr, "_dispatch_fle_gates", return_value={}):
            result = mgr.run_safety_gates(_make_anomaly(), _make_diagnosis())

        assert result["deployment_suppression"] is False

    def test_deployment_suppression_true_when_non_dict_returned(self):
        mgr = _mocked_manager()
        _setup_mocked_guards(mgr)
        mgr.deployment_suppression.check.return_value = True

        with patch.object(mgr, "_dispatch_fle_gates", return_value={}):
            result = mgr.run_safety_gates(_make_anomaly(), _make_diagnosis())

        assert result["deployment_suppression"] is True

    def test_config_consistency_false_on_stale_acks(self):
        mgr = _mocked_manager()
        _setup_mocked_guards(mgr)
        mgr.config_reload_guard.check_stale_acks.return_value = ["consumer_a"]

        with patch.object(mgr, "_dispatch_fle_gates", return_value={}):
            result = mgr.run_safety_gates(_make_anomaly(), _make_diagnosis())

        assert result["config_consistency"] is False

    def test_fle_gates_merged_into_result(self):
        mgr = _mocked_manager()
        _setup_mocked_guards(mgr)

        fle_result = {"FLE-CUSTOM-GATE": True, "FLE-OTHER-GATE": False}
        with patch.object(mgr, "_dispatch_fle_gates", return_value=fle_result):
            result = mgr.run_safety_gates(_make_anomaly(), _make_diagnosis())

        assert result["FLE-CUSTOM-GATE"] is True
        assert result["FLE-OTHER-GATE"] is False

    def test_anomaly_evidence_missing_metric_name_defaults_empty(self):
        mgr = _mocked_manager()
        _setup_mocked_guards(mgr)

        anomaly = _make_anomaly(evidence={"value": 1.0})
        with patch.object(mgr, "_dispatch_fle_gates", return_value={}):
            mgr.run_safety_gates(anomaly, _make_diagnosis())

        mgr.numerical_guard.validate.assert_called_once_with("pre_action_", 1.0)

    def test_anomaly_evidence_missing_value_defaults_zero(self):
        mgr = _mocked_manager()
        _setup_mocked_guards(mgr)

        anomaly = _make_anomaly(evidence={"metric_name": "latency"})
        with patch.object(mgr, "_dispatch_fle_gates", return_value={}):
            mgr.run_safety_gates(anomaly, _make_diagnosis())

        mgr.numerical_guard.validate.assert_called_once_with("pre_action_latency", 0.0)


class TestRunSafetyGatesBoundary:
    def test_anomaly_with_empty_evidence(self):
        mgr = _mocked_manager()
        _setup_mocked_guards(mgr)

        anomaly = _make_anomaly(evidence={})
        with patch.object(mgr, "_dispatch_fle_gates", return_value={}):
            result = mgr.run_safety_gates(anomaly, _make_diagnosis())

        assert isinstance(result, dict)
        assert "numerical_stability" in result

    def test_anomaly_with_none_evidence_value(self):
        mgr = _mocked_manager()
        _setup_mocked_guards(mgr)

        anomaly = _make_anomaly(evidence={"metric_name": "test", "value": None})
        with patch.object(mgr, "_dispatch_fle_gates", return_value={}):
            result = mgr.run_safety_gates(anomaly, _make_diagnosis())

        assert isinstance(result, dict)

    def test_numerical_guard_raises_exception_propagates(self):
        mgr = _mocked_manager()
        mgr.numerical_guard.validate.side_effect = RuntimeError("guard failure")

        with pytest.raises(RuntimeError, match="guard failure"):
            mgr.run_safety_gates(_make_anomaly(), _make_diagnosis())

    def test_temporal_guard_raises_exception_propagates(self):
        mgr = _mocked_manager()
        mgr.numerical_guard.validate.return_value = {"classification": "CLEAN"}
        mgr.temporal_guard.validate_timestamp.side_effect = RuntimeError("time failure")

        with pytest.raises(RuntimeError, match="time failure"):
            mgr.run_safety_gates(_make_anomaly(), _make_diagnosis())

    def test_deployment_suppression_check_returns_dict_without_allowed_key(self):
        mgr = _mocked_manager()
        _setup_mocked_guards(mgr)
        mgr.deployment_suppression.check.return_value = {"status": "blocked"}

        with patch.object(mgr, "_dispatch_fle_gates", return_value={}):
            result = mgr.run_safety_gates(_make_anomaly(), _make_diagnosis())

        assert result["deployment_suppression"] is True

    def test_deployment_suppression_check_returns_dict_with_ok_key(self):
        mgr = _mocked_manager()
        _setup_mocked_guards(mgr)
        mgr.deployment_suppression.check.return_value = {"ok": True}

        with patch.object(mgr, "_dispatch_fle_gates", return_value={}):
            result = mgr.run_safety_gates(_make_anomaly(), _make_diagnosis())

        assert result["deployment_suppression"] is True


class TestDispatchFleGates:
    def test_returns_empty_when_registry_missing(self, tmp_path):
        mgr = _mocked_manager()
        anomaly = _make_anomaly()
        diagnosis = _make_diagnosis()

        fake_src = tmp_path / "src" / "zephyr" / "feedback-loop"
        fake_src.mkdir(parents=True)
        fake_file = fake_src / "scheduler_safety.py"
        fake_file.write_text("", encoding="utf-8")

        with patch("zephyr.feedback_loop.scheduler_safety.__file__", str(fake_file)):
            result = mgr._dispatch_fle_gates(anomaly, diagnosis)

        assert result == {}

    def test_returns_empty_on_yaml_parse_exception(self, tmp_path):
        mgr = _mocked_manager()
        anomaly = _make_anomaly()
        diagnosis = _make_diagnosis()

        fake_src = tmp_path / "src" / "zephyr" / "feedback-loop"
        fake_src.mkdir(parents=True)
        fake_file = fake_src / "scheduler_safety.py"
        fake_file.write_text("", encoding="utf-8")

        gates_dir = tmp_path / "src" / "gates"
        gates_dir.mkdir(parents=True)
        registry_file = gates_dir / "_registry.yaml"
        registry_file.write_text("{{invalid yaml content", encoding="utf-8")

        with patch("zephyr.feedback_loop.scheduler_safety.__file__", str(fake_file)):
            result = mgr._dispatch_fle_gates(anomaly, diagnosis)

        assert result == {}

    def test_returns_empty_on_empty_gates_list(self, tmp_path):
        mgr = _mocked_manager()
        anomaly = _make_anomaly()
        diagnosis = _make_diagnosis()

        fake_src = tmp_path / "src" / "zephyr" / "feedback-loop"
        fake_src.mkdir(parents=True)
        fake_file = fake_src / "scheduler_safety.py"
        fake_file.write_text("", encoding="utf-8")

        gates_dir = tmp_path / "src" / "gates"
        gates_dir.mkdir(parents=True)
        registry_file = gates_dir / "_registry.yaml"
        registry_file.write_text("gates: []\n", encoding="utf-8")

        with patch("zephyr.feedback_loop.scheduler_safety.__file__", str(fake_file)):
            result = mgr._dispatch_fle_gates(anomaly, diagnosis)

        assert result == {}

    def test_skips_deployment_suppression_gate(self, tmp_path):
        mgr = _mocked_manager()
        anomaly = _make_anomaly()
        diagnosis = _make_diagnosis()

        fake_src = tmp_path / "src" / "zephyr" / "feedback-loop"
        fake_src.mkdir(parents=True)
        fake_file = fake_src / "scheduler_safety.py"
        fake_file.write_text("", encoding="utf-8")

        gates_dir = tmp_path / "src" / "gates"
        gates_dir.mkdir(parents=True)
        registry_file = gates_dir / "_registry.yaml"
        registry_file.write_text(
            "gates:\n"
            "  - gate_id: FLE-DEPLOYMENT-SUPPRESSION\n"
            "    category: fle_self_defense\n"
            "    file: feedback-loop/gates/deployment_suppression.py\n",
            encoding="utf-8",
        )

        with patch("zephyr.feedback_loop.scheduler_safety.__file__", str(fake_file)):
            result = mgr._dispatch_fle_gates(anomaly, diagnosis)

        assert "FLE-DEPLOYMENT-SUPPRESSION" not in result

    def test_exception_in_invoke_yields_true(self, tmp_path):
        mgr = _mocked_manager()
        anomaly = _make_anomaly()
        diagnosis = _make_diagnosis()

        fake_src = tmp_path / "src" / "zephyr" / "feedback-loop"
        fake_src.mkdir(parents=True)
        fake_file = fake_src / "scheduler_safety.py"
        fake_file.write_text("", encoding="utf-8")

        gates_dir = tmp_path / "src" / "gates"
        gates_dir.mkdir(parents=True)
        registry_file = gates_dir / "_registry.yaml"
        registry_file.write_text(
            "gates:\n"
            "  - gate_id: FLE-TEST-GATE\n"
            "    category: fle_self_defense\n"
            "    file: feedback-loop/gates/test_gate.py\n",
            encoding="utf-8",
        )

        with patch("zephyr.feedback_loop.scheduler_safety.__file__", str(fake_file)):
            with patch.object(mgr, "_invoke_fle_gate", side_effect=RuntimeError("boom")):
                result = mgr._dispatch_fle_gates(anomaly, diagnosis)

        assert result.get("FLE-TEST-GATE") is True

    def test_non_fle_self_defense_gates_ignored(self, tmp_path):
        mgr = _mocked_manager()
        anomaly = _make_anomaly()
        diagnosis = _make_diagnosis()

        fake_src = tmp_path / "src" / "zephyr" / "feedback-loop"
        fake_src.mkdir(parents=True)
        fake_file = fake_src / "scheduler_safety.py"
        fake_file.write_text("", encoding="utf-8")

        gates_dir = tmp_path / "src" / "gates"
        gates_dir.mkdir(parents=True)
        registry_file = gates_dir / "_registry.yaml"
        registry_file.write_text(
            "gates:\n"
            "  - gate_id: FLE-OTHER-CATEGORY\n"
            "    category: deployment\n"
            "    file: feedback-loop/gates/other.py\n",
            encoding="utf-8",
        )

        with patch("zephyr.feedback_loop.scheduler_safety.__file__", str(fake_file)):
            result = mgr._dispatch_fle_gates(anomaly, diagnosis)

        assert result == {}

    def test_gate_without_file_field_ignored(self, tmp_path):
        mgr = _mocked_manager()
        anomaly = _make_anomaly()
        diagnosis = _make_diagnosis()

        fake_src = tmp_path / "src" / "zephyr" / "feedback-loop"
        fake_src.mkdir(parents=True)
        fake_file = fake_src / "scheduler_safety.py"
        fake_file.write_text("", encoding="utf-8")

        gates_dir = tmp_path / "src" / "gates"
        gates_dir.mkdir(parents=True)
        registry_file = gates_dir / "_registry.yaml"
        registry_file.write_text(
            "gates:\n  - gate_id: FLE-NO-FILE\n    category: fle_self_defense\n",
            encoding="utf-8",
        )

        with patch("zephyr.feedback_loop.scheduler_safety.__file__", str(fake_file)):
            result = mgr._dispatch_fle_gates(anomaly, diagnosis)

        assert result == {}


class TestInvokeFleGate:
    def test_cached_gate_reused(self):
        mgr = _mocked_manager()

        class FakeGate:
            def check(self) -> dict:
                return {"allowed": True}

        cached_instance = FakeGate()
        mgr._fle_gate_cache["FLE-CACHED"] = cached_instance

        result = mgr._invoke_fle_gate("FLE-CACHED", "some/file.py", _make_anomaly(), _make_diagnosis())
        assert result is True

    def test_import_error_returns_true(self):
        mgr = _mocked_manager()

        with patch.object(importlib, "import_module", side_effect=ImportError("no module")):
            result = mgr._invoke_fle_gate("FLE-NEW", "nonexistent/module.py", _make_anomaly(), _make_diagnosis())

        assert result is True

    def test_no_matching_class_in_module_returns_true(self):
        mgr = _mocked_manager()
        anomaly = _make_anomaly()
        diagnosis = _make_diagnosis()

        fake_module = types.ModuleType("zephyr.fake_gate_module")

        with patch.object(importlib, "import_module", return_value=fake_module):
            result = mgr._invoke_fle_gate("FLE-NO-CLASS", "some/file.py", anomaly, diagnosis)

        assert result is True

    def test_check_method_with_no_params_returns_allowed(self):
        mgr = _mocked_manager()
        anomaly = _make_anomaly()
        diagnosis = _make_diagnosis()

        class FakeGate:
            def check(self) -> dict:
                return {"allowed": True}

        fake_module = types.ModuleType("zephyr.fake_check_gate")
        fake_module.FakeGate = FakeGate

        with patch.object(importlib, "import_module", return_value=fake_module):
            result = mgr._invoke_fle_gate("FLE-CHECK-GATE", "some/file.py", anomaly, diagnosis)

        assert result is True

    def test_check_method_returns_dict_with_passed_key(self):
        mgr = _mocked_manager()
        anomaly = _make_anomaly()
        diagnosis = _make_diagnosis()

        class FakeGate:
            def check(self) -> dict:
                return {"passed": True}

        fake_module = types.ModuleType("zephyr.fake_passed_gate")
        fake_module.FakeGate = FakeGate

        with patch.object(importlib, "import_module", return_value=fake_module):
            result = mgr._invoke_fle_gate("FLE-PASSED-GATE", "some/file.py", anomaly, diagnosis)

        assert result is True

    def test_check_method_returns_dict_with_ok_key(self):
        mgr = _mocked_manager()
        anomaly = _make_anomaly()
        diagnosis = _make_diagnosis()

        class FakeGate:
            def check(self) -> dict:
                return {"ok": True}

        fake_module = types.ModuleType("zephyr.fake_ok_gate")
        fake_module.FakeGate = FakeGate

        with patch.object(importlib, "import_module", return_value=fake_module):
            result = mgr._invoke_fle_gate("FLE-OK-GATE", "some/file.py", anomaly, diagnosis)

        assert result is True

    def test_check_method_returns_bool_false(self):
        mgr = _mocked_manager()
        anomaly = _make_anomaly()
        diagnosis = _make_diagnosis()

        class FakeGate:
            def check(self) -> bool:
                return False

        fake_module = types.ModuleType("zephyr.fake_bool_gate")
        fake_module.FakeGate = FakeGate

        with patch.object(importlib, "import_module", return_value=fake_module):
            result = mgr._invoke_fle_gate("FLE-BOOL-GATE", "some/file.py", anomaly, diagnosis)

        assert result is False

    def test_gate_method_with_single_param(self):
        mgr = _mocked_manager()
        anomaly = _make_anomaly()
        diagnosis = _make_diagnosis()

        class FakeGate:
            def gate(self, action_type: str) -> bool:
                return False

        fake_module = types.ModuleType("zephyr.fake_gate_single")
        fake_module.FakeGate = FakeGate

        with patch.object(importlib, "import_module", return_value=fake_module):
            result = mgr._invoke_fle_gate("FLE-GATE-SINGLE", "some/file.py", anomaly, diagnosis)

        assert result is False

    def test_method_with_two_or_more_params_returns_true(self):
        mgr = _mocked_manager()
        anomaly = _make_anomaly()
        diagnosis = _make_diagnosis()

        class FakeGate:
            def audit(self, a: str, b: str) -> bool:
                return False

        fake_module = types.ModuleType("zephyr.fake_audit_gate")
        fake_module.FakeGate = FakeGate

        with patch.object(importlib, "import_module", return_value=fake_module):
            result = mgr._invoke_fle_gate("FLE-AUDIT-GATE", "some/file.py", anomaly, diagnosis)

        assert result is True

    def test_method_exception_returns_true(self):
        mgr = _mocked_manager()
        anomaly = _make_anomaly()
        diagnosis = _make_diagnosis()

        class FakeGate:
            def check(self) -> dict:
                raise RuntimeError("gate crash")

        fake_module = types.ModuleType("zephyr.fake_crash_gate")
        fake_module.FakeGate = FakeGate

        with patch.object(importlib, "import_module", return_value=fake_module):
            result = mgr._invoke_fle_gate("FLE-CRASH-GATE", "some/file.py", anomaly, diagnosis)

        assert result is True

    def test_none_anomaly_uses_unknown_action_id(self):
        mgr = _mocked_manager()

        class FakeGate:
            def check(self) -> dict:
                return {"allowed": True}

        fake_module = types.ModuleType("zephyr.fake_null_gate")
        fake_module.FakeGate = FakeGate

        with patch.object(importlib, "import_module", return_value=fake_module):
            result = mgr._invoke_fle_gate("FLE-NULL-ANOMALY", "some/file.py", None, None)

        assert isinstance(result, bool)

    def test_gate_class_instantiation_type_error_uses_class_directly(self):
        mgr = _mocked_manager()
        anomaly = _make_anomaly()
        diagnosis = _make_diagnosis()

        class FakeGate:
            def __init__(self, required_arg: str):
                self.arg = required_arg

            def check(self) -> dict:
                return {"allowed": True}

        fake_module = types.ModuleType("zephyr.fake_typeerr_gate")
        fake_module.FakeGate = FakeGate

        with patch.object(importlib, "import_module", return_value=fake_module):
            result = mgr._invoke_fle_gate("FLE-TYPEERR-GATE", "some/file.py", anomaly, diagnosis)

        assert isinstance(result, bool)

    def test_no_matching_method_on_class_returns_true(self):
        mgr = _mocked_manager()
        anomaly = _make_anomaly()
        diagnosis = _make_diagnosis()

        class FakeGate:
            def some_other_method(self) -> bool:
                return True

        fake_module = types.ModuleType("zephyr.fake_nomethod_gate")
        fake_module.FakeGate = FakeGate

        with patch.object(importlib, "import_module", return_value=fake_module):
            result = mgr._invoke_fle_gate("FLE-NOMETHOD-GATE", "some/file.py", anomaly, diagnosis)

        assert result is True

    def test_gate_result_cached_in_fle_gate_cache(self):
        mgr = _mocked_manager()
        anomaly = _make_anomaly()
        diagnosis = _make_diagnosis()

        class FakeGate:
            def check(self) -> dict:
                return {"allowed": True}

        fake_module = types.ModuleType("zephyr.fake_cache_gate")
        fake_module.FakeGate = FakeGate

        with patch.object(importlib, "import_module", return_value=fake_module):
            mgr._invoke_fle_gate("FLE-CACHE-TEST", "some/file.py", anomaly, diagnosis)

        assert "FLE-CACHE-TEST" in mgr._fle_gate_cache
        assert isinstance(mgr._fle_gate_cache["FLE-CACHE-TEST"], FakeGate)

        with patch.object(importlib, "import_module", side_effect=AssertionError("should not be called")):
            result = mgr._invoke_fle_gate("FLE-CACHE-TEST", "some/file.py", anomaly, diagnosis)

        assert result is True
