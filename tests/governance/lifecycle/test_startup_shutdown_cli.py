# [A_test] module_id: MOD-GOV_startup_shutdown_cli | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain-infra_ops/rollback-system/blueprint.md
# [MODULE] tests.test_startup_shutdown_cli
# [INVARIANTS] CLI argparser build;phase range parsing;command dispatch
# [MODIFY-GUARD] src/zephyr/rollback/startup_shutdown_cli.py
# [CONSUMERS] CI
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_startup_shutdown_cli.py
# [TTL] task_bound

from __future__ import annotations

from unittest.mock import patch

import pytest

from zephyr.governance.ops_governance.startup_shutdown_cli import (
    build_argparser,
    main,
    parse_phase_range,
)


class TestBuildArgparser:
    def test_returns_parser(self) -> None:
        parser = build_argparser()
        assert parser is not None
        assert parser.prog == "zephyr"

    def test_start_command(self) -> None:
        parser = build_argparser()
        args = parser.parse_args(["start"])
        assert args.command == "start"
        assert args.phases == "1-6"

    def test_start_custom_phases(self) -> None:
        parser = build_argparser()
        args = parser.parse_args(["start", "--phases", "1-3"])
        assert args.command == "start"
        assert args.phases == "1-3"

    def test_stop_command(self) -> None:
        parser = build_argparser()
        args = parser.parse_args(["stop"])
        assert args.command == "stop"
        assert args.phases == "6-1"

    def test_stop_custom_phases(self) -> None:
        parser = build_argparser()
        args = parser.parse_args(["stop", "--phases", "3-1"])
        assert args.command == "stop"
        assert args.phases == "3-1"

    def test_status_command(self) -> None:
        parser = build_argparser()
        args = parser.parse_args(["status"])
        assert args.command == "status"

    def test_no_command_raises(self) -> None:
        parser = build_argparser()
        with pytest.raises(SystemExit):
            parser.parse_args([])


class TestParsePhaseRange:
    def test_ascending_range(self) -> None:
        result = parse_phase_range("1-6")
        assert result == [1, 2, 3, 4, 5, 6]

    def test_descending_range(self) -> None:
        result = parse_phase_range("6-1")
        assert result == [6, 5, 4, 3, 2, 1]

    def test_single_step_ascending(self) -> None:
        result = parse_phase_range("1-3")
        assert result == [1, 2, 3]

    def test_single_step_descending(self) -> None:
        result = parse_phase_range("3-1")
        assert result == [3, 2, 1]

    def test_same_start_end(self) -> None:
        result = parse_phase_range("2-2")
        assert result == [2]

    def test_invalid_format_no_dash(self) -> None:
        result = parse_phase_range("123")
        assert result == []

    def test_invalid_format_multiple_dashes(self) -> None:
        result = parse_phase_range("1-2-3")
        assert result == []

    def test_invalid_non_numeric(self) -> None:
        result = parse_phase_range("a-b")
        assert result == []

    def test_empty_string(self) -> None:
        result = parse_phase_range("")
        assert result == []

    def test_partial_numeric(self) -> None:
        result = parse_phase_range("1-a")
        assert result == []


class TestMain:
    def test_main_start(self, capsys: pytest.CaptureFixture[str]) -> None:
        with patch("sys.argv", ["zephyr", "start", "--phases", "1-2"]):
            main()
        captured = capsys.readouterr()
        assert "zephyr-start" in captured.out
        assert "[1, 2]" in captured.out

    def test_main_stop(self, capsys: pytest.CaptureFixture[str]) -> None:
        with patch("sys.argv", ["zephyr", "stop", "--phases", "6-4"]):
            main()
        captured = capsys.readouterr()
        assert "zephyr-stop" in captured.out
        assert "[6, 5, 4]" in captured.out

    def test_main_status(self, capsys: pytest.CaptureFixture[str]) -> None:
        with patch("sys.argv", ["zephyr", "status"]):
            main()
        captured = capsys.readouterr()
        assert "zephyr-status" in captured.out
        assert "OK" in captured.out

    def test_main_start_default_phases(self, capsys: pytest.CaptureFixture[str]) -> None:
        with patch("sys.argv", ["zephyr", "start"]):
            main()
        captured = capsys.readouterr()
        assert "zephyr-start" in captured.out
        assert "[1, 2, 3, 4, 5, 6]" in captured.out
