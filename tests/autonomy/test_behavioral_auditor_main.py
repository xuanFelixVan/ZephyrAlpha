# [A_test] module_id: SRC-TST-0421 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-033 | docs/03_modules/_cross_layer/behavioral_auditor/blueprint.md | §
# [MODULE] tests.test_behavioral_auditor_main
# [INVARIANTS] test_cmd_scan_import_error;test_cmd_self_test_pass;test_cmd_budget_allowed
# [MODIFY-GUARD] source-change-only
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest.ExitCode
# [TESTS] test_behavioral_auditor_main.py
# [TTL] task_bound

import argparse
from unittest.mock import MagicMock, patch

import pytest

from zephyr.autonomy_core.__main__ import _cmd_budget, _cmd_list, _cmd_scan, _cmd_self_test, _cmd_status


class TestMainFunction:
    def test_status_command(self):
        with (
            patch(
                "zephyr.gov_drift.drift_engine.load_detector_registry", return_value=[MagicMock(status="active")]
            ),
            patch("zephyr.gov_drift.self_test_verifier.SelfTestVerifier") as mock_cls,
        ):
            mock_inst = MagicMock()
            mock_inst.run_all.return_value = MagicMock(summary="8/8 checks passed")
            mock_cls.return_value = mock_inst
            with patch("zephyr.gov_drift.self_check.bootstrap_self_check", return_value=True):
                with patch("sys.argv", ["prog", "status"]):
                    from zephyr.autonomy_core.__main__ import main

                    result = main()
                    assert result == 0

    def test_scan_command(self):
        with patch("zephyr.autonomy_core.__main__._cmd_scan", return_value=0):
            with patch("sys.argv", ["prog", "scan"]):
                from zephyr.autonomy_core.__main__ import main

                result = main()
                assert result == 0

    def test_no_command_defaults(self):
        with patch("zephyr.autonomy_core.__main__._cmd_status", return_value=0):
            with patch("sys.argv", ["prog"]):
                from zephyr.autonomy_core.__main__ import main

                result = main()
                assert result == 0


class TestCmdScan:
    def test_import_error(self):
        args = argparse.Namespace(level="LIGHT")
        with patch.dict("sys.modules", {"zephyr.gov_drift.drift_engine": None}):
            result = _cmd_scan(args)
            assert result == 1

    def test_scan_success(self):
        args = argparse.Namespace(level="LIGHT")
        mock_result = MagicMock(
            scan_id="SCAN-001",
            detectors_run=5,
            total_drift_events=0,
            storm_mode_triggered=False,
        )
        mock_report = MagicMock(
            top_drift_dimensions=[],
            scan_summary="Clean",
        )
        mock_scan_level = MagicMock()
        mock_scan_level.__getitem__ = MagicMock(return_value=MagicMock())
        with patch("zephyr.gov_drift.drift_engine.ScanLevel", mock_scan_level):
            with patch("zephyr.gov_drift.drift_engine.build_report", return_value=mock_report):
                with patch("zephyr.gov_drift.drift_engine.scan", return_value=mock_result):
                    with patch("zephyr.autonomy_core.__main__.asyncio") as mock_asyncio:
                        mock_loop = MagicMock()
                        mock_loop.run_until_complete.return_value = mock_result
                        mock_asyncio.new_event_loop.return_value = mock_loop
                        result = _cmd_scan(args)
                        assert result == 0

    def test_scan_with_drift(self):
        args = argparse.Namespace(level="STANDARD")
        mock_result = MagicMock(
            scan_id="SCAN-002",
            detectors_run=10,
            total_drift_events=3,
            storm_mode_triggered=True,
        )
        mock_report = MagicMock(
            top_drift_dimensions=["architecture"],
            scan_summary="3 drift events",
        )
        mock_scan_level = MagicMock()
        with patch("zephyr.gov_drift.drift_engine.ScanLevel", mock_scan_level):
            with patch("zephyr.gov_drift.drift_engine.build_report", return_value=mock_report):
                with patch("zephyr.gov_drift.drift_engine.scan", return_value=mock_result):
                    with patch("zephyr.autonomy_core.__main__.asyncio") as mock_asyncio:
                        mock_loop = MagicMock()
                        mock_loop.run_until_complete.return_value = mock_result
                        mock_asyncio.new_event_loop.return_value = mock_loop
                        result = _cmd_scan(args)
                        assert result == 1

    def test_scan_exception(self):
        args = argparse.Namespace(level="LIGHT")
        mock_scan_level = MagicMock()
        with patch("zephyr.gov_drift.drift_engine.ScanLevel", mock_scan_level):
            with patch("zephyr.autonomy_core.__main__.asyncio") as mock_asyncio:
                mock_loop = MagicMock()
                mock_loop.run_until_complete.side_effect = RuntimeError("boom")
                mock_asyncio.new_event_loop.return_value = mock_loop
                result = _cmd_scan(args)
                assert result == 1


class TestCmdSelfTest:
    def test_import_error(self):
        args = argparse.Namespace(json=False)
        with patch.dict("sys.modules", {"zephyr.gov_drift.self_test_verifier": None}):
            result = _cmd_self_test(args)
            assert result == 1

    def test_self_test_pass(self):
        args = argparse.Namespace(json=False)
        mock_verifier = MagicMock()
        mock_result = MagicMock(summary="8/8 checks passed", checks=[])
        mock_verifier.run_all.return_value = mock_result
        with patch("zephyr.gov_drift.self_test_verifier.SelfTestVerifier", return_value=mock_verifier):
            result = _cmd_self_test(args)
            assert result == 0

    def test_self_test_fail(self):
        args = argparse.Namespace(json=False)
        mock_verifier = MagicMock()
        mock_result = MagicMock(summary="5/8 checks passed", checks=[{"check": "test", "status": "FAIL"}])
        mock_verifier.run_all.return_value = mock_result
        with patch("zephyr.gov_drift.self_test_verifier.SelfTestVerifier", return_value=mock_verifier):
            result = _cmd_self_test(args)
            assert result == 1

    def test_self_test_json(self):
        args = argparse.Namespace(json=True)
        mock_verifier = MagicMock()
        mock_result = MagicMock(summary="8/8 checks passed", checks=[])
        mock_verifier.run_all.return_value = mock_result
        with patch("zephyr.gov_drift.self_test_verifier.SelfTestVerifier", return_value=mock_verifier):
            result = _cmd_self_test(args)
            assert result == 0


class TestCmdBudget:
    def test_import_error(self):
        args = argparse.Namespace(module_id=None, tier="P0", json=False)
        with patch.dict("sys.modules", {"zephyr.gov_drift.drift_infrastructure": None}):
            result = _cmd_budget(args)
            assert result == 1

    def test_budget_allowed(self):
        args = argparse.Namespace(module_id="MOD-INF-023", tier="P0", json=False)
        with patch(
            "zephyr.gov_drift.drift_infrastructure.check_budget_for_gate",
            return_value={"allowed": True, "reason": "OK"},
        ):
            result = _cmd_budget(args)
            assert result == 0

    def test_budget_blocked(self):
        args = argparse.Namespace(module_id="MOD-INF-023", tier="P0", json=False)
        with patch(
            "zephyr.gov_drift.drift_infrastructure.check_budget_for_gate",
            return_value={"allowed": False, "reason": "Over budget"},
        ):
            result = _cmd_budget(args)
            assert result == 1

    def test_budget_json(self):
        args = argparse.Namespace(module_id="MOD-INF-023", tier="P0", json=True)
        with patch(
            "zephyr.gov_drift.drift_infrastructure.check_budget_for_gate",
            return_value={"allowed": True, "reason": "OK"},
        ):
            result = _cmd_budget(args)
            assert result == 0

    def test_budget_default_module(self):
        args = argparse.Namespace(module_id=None, tier="P0", json=False)
        with patch(
            "zephyr.gov_drift.drift_infrastructure.check_budget_for_gate",
            return_value={"allowed": True, "reason": "OK"},
        ) as mock_cb:
            result = _cmd_budget(args)
            mock_cb.assert_called_once_with("MOD-INF-023", "P0")


class TestCmdList:
    def test_import_error(self):
        args = argparse.Namespace(json=False)
        with patch.dict("sys.modules", {"zephyr.gov_drift.drift_engine": None}):
            result = _cmd_list(args)
            assert result == 1

    def test_list_text(self):
        args = argparse.Namespace(json=False)
        mock_det = MagicMock(
            id="DD-001", severity=MagicMock(value="HIGH"), category="arch", status="active", auto_fixable=False
        )
        with patch("zephyr.gov_drift.drift_engine.load_detector_registry", return_value=[mock_det]):
            result = _cmd_list(args)
            assert result == 0

    def test_list_json(self):
        args = argparse.Namespace(json=True)
        mock_det = MagicMock(
            id="DD-001",
            drift_dimension="architecture",
            severity=MagicMock(value="HIGH"),
            category="arch",
            status="active",
            auto_fixable=False,
        )
        with patch("zephyr.gov_drift.drift_engine.load_detector_registry", return_value=[mock_det]):
            result = _cmd_list(args)
            assert result == 0

    def test_list_empty(self):
        args = argparse.Namespace(json=False)
        with patch("zephyr.gov_drift.drift_engine.load_detector_registry", return_value=[]):
            result = _cmd_list(args)
            assert result == 0


class TestCmdStatus:
    def test_status_all_ok(self):
        mock_verifier = MagicMock()
        mock_result = MagicMock(summary="8/8 checks passed")
        mock_verifier.run_all.return_value = mock_result
        with (
            patch(
                "zephyr.gov_drift.drift_engine.load_detector_registry", return_value=[MagicMock(status="active")]
            ),
            patch("zephyr.gov_drift.self_test_verifier.SelfTestVerifier", return_value=mock_verifier),
        ):
            with patch("zephyr.gov_drift.self_check.bootstrap_self_check", return_value=True):
                result = _cmd_status(MagicMock())
                assert result == 0

    def test_status_degraded(self):
        mock_verifier = MagicMock()
        mock_result = MagicMock(summary="5/8 checks passed")
        mock_verifier.run_all.return_value = mock_result
        with (
            patch(
                "zephyr.gov_drift.drift_engine.load_detector_registry", return_value=[MagicMock(status="active")]
            ),
            patch("zephyr.gov_drift.self_test_verifier.SelfTestVerifier", return_value=mock_verifier),
        ):
            with patch("zephyr.gov_drift.self_check.bootstrap_self_check", return_value=False):
                result = _cmd_status(MagicMock())
                assert result == 1

    def test_status_registry_fail(self):
        with patch("zephyr.gov_drift.drift_engine.load_detector_registry", side_effect=RuntimeError("fail")):
            with patch("zephyr.gov_drift.self_test_verifier.SelfTestVerifier") as mock_cls:
                mock_inst = MagicMock()
                mock_inst.run_all.return_value = MagicMock(summary="8/8 checks passed")
                mock_cls.return_value = mock_inst
                with patch("zephyr.gov_drift.self_check.bootstrap_self_check", return_value=True):
                    result = _cmd_status(MagicMock())
                    assert result == 1

    @pytest.mark.filterwarnings("ignore::RuntimeWarning")
    @pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
    def test_status_self_test_fail(self):
        mock_verifier = MagicMock()
        mock_result = MagicMock(summary="5/8 checks passed")
        mock_verifier.run_all.return_value = mock_result
        with (
            patch(
                "zephyr.gov_drift.drift_engine.load_detector_registry", return_value=[MagicMock(status="active")]
            ),
            patch("zephyr.gov_drift.self_test_verifier.SelfTestVerifier", return_value=mock_verifier),
        ):
            with patch("zephyr.gov_drift.self_check.bootstrap_self_check", return_value=True):
                result = _cmd_status(MagicMock())
                assert result == 1
