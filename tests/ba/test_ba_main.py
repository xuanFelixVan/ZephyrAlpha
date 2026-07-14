# [A_test] module_id: SRC-TST-0402 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-033 | docs/03_modules/_cross_layer/behavioral_auditor/blueprint.md | §
# [MODULE] tests.test_ba_main
# [INVARIANTS] CLI入口不可修改
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [CONSUMERS] CI
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

import argparse
import sys
from unittest.mock import MagicMock, patch

from zephyr.autonomy_core.__main__ import (
    _cmd_budget,
    _cmd_list,
    _cmd_scan,
    _cmd_self_test,
    _cmd_status,
    main,
)


class TestCmdScan:
    def test_returns_1_on_import_error(self):
        args = argparse.Namespace(level="LIGHT")
        with patch.dict("sys.modules", {"zephyr.gov_drift.drift_engine": None}):
            result = _cmd_scan(args)
        assert result == 1


class TestCmdSelfTest:
    def test_returns_1_on_import_error(self):
        args = argparse.Namespace(json=False)
        with patch.dict("sys.modules", {"zephyr.gov_drift.self_test_verifier": None}):
            result = _cmd_self_test(args)
        assert result == 1

    def test_json_output_mode(self, capsys):
        args = argparse.Namespace(json=True)
        mock_result = MagicMock()
        mock_result.summary = "8/8 checks passed"
        mock_result.checks = [{"check": "c1", "status": "PASS", "detail": ""}]
        with patch("zephyr.gov_drift.self_test_verifier.SelfTestVerifier") as MockVerifier:
            MockVerifier.return_value.run_all.return_value = mock_result
            result = _cmd_self_test(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "8/8" in captured.out or "PASS" in captured.out

    def test_returns_1_when_not_all_passed(self):
        args = argparse.Namespace(json=False)
        mock_result = MagicMock()
        mock_result.summary = "6/8 checks passed"
        mock_result.checks = [{"check": "c1", "status": "FAIL", "detail": ""}]
        with patch("zephyr.gov_drift.self_test_verifier.SelfTestVerifier") as MockVerifier:
            MockVerifier.return_value.run_all.return_value = mock_result
            result = _cmd_self_test(args)
        assert result == 1


class TestCmdBudget:
    def test_returns_1_on_import_error(self):
        args = argparse.Namespace(module_id="MOD-INF-023", tier="P0", json=False)
        with patch.dict("sys.modules", {"zephyr.gov_drift.drift_infrastructure": None}):
            result = _cmd_budget(args)
        assert result == 1

    def test_returns_0_when_allowed(self):
        args = argparse.Namespace(module_id="MOD-INF-023", tier="P0", json=False)
        with patch(
            "zephyr.gov_drift.drift_infrastructure.check_budget_for_gate",
            return_value={"allowed": True, "reason": "within budget"},
        ):
            result = _cmd_budget(args)
        assert result == 0

    def test_returns_1_when_blocked(self):
        args = argparse.Namespace(module_id="MOD-INF-023", tier="P0", json=False)
        with patch(
            "zephyr.gov_drift.drift_infrastructure.check_budget_for_gate",
            return_value={"allowed": False, "reason": "budget exhausted"},
        ):
            result = _cmd_budget(args)
        assert result == 1


class TestCmdList:
    def test_returns_1_on_import_error(self):
        args = argparse.Namespace(json=False)
        with patch.dict("sys.modules", {"zephyr.gov_drift.drift_engine": None}):
            result = _cmd_list(args)
        assert result == 1

    def test_returns_0_on_success(self):
        args = argparse.Namespace(json=False)
        mock_det = MagicMock()
        mock_det.id = "det1"
        mock_det.drift_dimension = "schema"
        mock_det.severity = MagicMock()
        mock_det.severity.value = "HIGH"
        mock_det.category = "structure"
        mock_det.status = "active"
        mock_det.auto_fixable = False
        with patch(
            "zephyr.gov_drift.drift_engine.load_detector_registry",
            return_value=[mock_det],
        ):
            result = _cmd_list(args)
        assert result == 0


class TestCmdStatus:
    def test_returns_0_when_healthy(self, capsys):
        with (
            patch(
                "zephyr.gov_drift.drift_engine.load_detector_registry",
                return_value=[],
            ),
            patch("zephyr.gov_drift.self_test_verifier.SelfTestVerifier") as MockSTV,
            patch(
                "zephyr.gov_drift.self_check.bootstrap_self_check",
                return_value=True,
            ),
        ):
            mock_stv_result = MagicMock()
            mock_stv_result.summary = "8/8 checks passed"
            MockSTV.return_value.run_all.return_value = mock_stv_result
            result = _cmd_status(argparse.Namespace())
        assert result == 0

    def test_returns_1_when_degraded(self, capsys):
        with patch(
            "zephyr.gov_drift.drift_engine.load_detector_registry",
            side_effect=Exception("fail"),
        ):
            result = _cmd_status(argparse.Namespace())
        assert result == 1


class TestMainParser:
    def test_no_command_runs_status(self):
        with (
            patch.object(sys, "argv", ["__main__.py"]),
            patch("zephyr.autonomy_core.__main__._cmd_status", return_value=0) as mock,
        ):
            result = main()
            mock.assert_called_once()

    def test_scan_command(self):
        with (
            patch.object(sys, "argv", ["__main__.py", "scan"]),
            patch("zephyr.autonomy_core.__main__._cmd_scan", return_value=0) as mock,
        ):
            result = main()
            mock.assert_called_once()

    def test_self_test_command(self):
        with (
            patch.object(sys, "argv", ["__main__.py", "self-test"]),
            patch("zephyr.autonomy_core.__main__._cmd_self_test", return_value=0) as mock,
        ):
            result = main()
            mock.assert_called_once()

    def test_budget_command(self):
        with (
            patch.object(sys, "argv", ["__main__.py", "budget"]),
            patch("zephyr.autonomy_core.__main__._cmd_budget", return_value=0) as mock,
        ):
            result = main()
            mock.assert_called_once()

    def test_list_command(self):
        with (
            patch.object(sys, "argv", ["__main__.py", "list"]),
            patch("zephyr.autonomy_core.__main__._cmd_list", return_value=0) as mock,
        ):
            result = main()
            mock.assert_called_once()

    def test_status_command(self):
        with (
            patch.object(sys, "argv", ["__main__.py", "status"]),
            patch("zephyr.autonomy_core.__main__._cmd_status", return_value=0) as mock,
        ):
            result = main()
            mock.assert_called_once()
