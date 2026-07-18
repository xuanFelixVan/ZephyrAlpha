# [A_test] module_id: SRC-TST-0718 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-376 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.test_decision_fatigue_cli
# [INVARIANTS] build_parser returns ArgumentParser; main runs without error
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_decision_fatigue_cli.py
# [TTL] task_bound

from __future__ import annotations

import argparse

from zephyr.governance.resilience_governance.decision_fatigue_cli import build_parser


class TestBuildParser:
    def test_returns_argument_parser(self):
        parser = build_parser()
        assert isinstance(parser, argparse.ArgumentParser)

    def test_parser_prog(self):
        parser = build_parser()
        assert parser.prog == "zephyr-priorities"

    def test_filter_default(self):
        parser = build_parser()
        args = parser.parse_args([])
        assert args.filter == "ALL"

    def test_filter_p0(self):
        parser = build_parser()
        args = parser.parse_args(["--filter", "P0"])
        assert args.filter == "P0"

    def test_filter_p1(self):
        parser = build_parser()
        args = parser.parse_args(["--filter", "P1"])
        assert args.filter == "P1"

    def test_filter_p2(self):
        parser = build_parser()
        args = parser.parse_args(["--filter", "P2"])
        assert args.filter == "P2"

    def test_filter_p3(self):
        parser = build_parser()
        args = parser.parse_args(["--filter", "P3"])
        assert args.filter == "P3"


class TestMain:
    def test_main_runs_all(self, capsys):
        import sys

        from zephyr.governance.resilience_governance.decision_fatigue_cli import main

        original_argv = sys.argv
        sys.argv = ["zephyr-priorities"]
        try:
            main()
        finally:
            sys.argv = original_argv
        captured = capsys.readouterr()
        assert "P0:" in captured.out

    def test_main_runs_filtered(self, capsys):
        import sys

        from zephyr.governance.resilience_governance.decision_fatigue_cli import main

        original_argv = sys.argv
        sys.argv = ["zephyr-priorities", "--filter", "P0"]
        try:
            main()
        finally:
            sys.argv = original_argv
        captured = capsys.readouterr()
        assert "T01" in captured.out


class TestBoundary:
    def test_main_unknown_filter(self, capsys):
        import sys

        from zephyr.governance.resilience_governance.decision_fatigue_cli import main

        original_argv = sys.argv
        sys.argv = ["zephyr-priorities", "--filter", "INVALID"]
        try:
            main()
        finally:
            sys.argv = original_argv
        captured = capsys.readouterr()
        assert "Unknown filter" in captured.out
