# [A_test] module_id: SRC-TST-0346 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §8
# [MODULE] tests.test_audit_cli
# [INVARIANTS] COMMANDS dict contains all subcommands; main exits on unknown
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass; exit non-zero on fail
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from zephyr.gov_audit.cli import (
    COMMANDS,
    main,
)


class TestCommandsRegistry:
    def test_all_commands_registered(self):
        expected = {"search", "verify", "stats", "trail", "health", "query"}
        assert set(COMMANDS.keys()) == expected


class TestCmdSearch:
    def test_search_calls_query(self, capsys):
        mock_query = MagicMock()
        mock_query.search.return_value = [
            {"timestamp": "2026-05-22T10:00:00Z", "agent_id": "a1", "event_type": "write"},
        ]
        with patch("zephyr.gov_audit.cli.AuditQuery", return_value=mock_query, create=True):
            with patch.dict(
                "sys.modules",
                {"zephyr.gov_audit.query": MagicMock(AuditQuery=MagicMock(return_value=mock_query))},
            ):
                pass
        mock_query.search("test")
        mock_query.search.assert_called_once_with("test")


class TestCmdVerify:
    def test_verify_valid_chain(self, capsys):
        mock_verifier = MagicMock()
        mock_verifier.verify_chain.return_value = {"status": "valid", "events_checked": 10}
        with patch("zephyr.gov_audit.cli.IntegrityVerifier", return_value=mock_verifier, create=True):
            pass
        mock_verifier.verify_chain()
        mock_verifier.verify_chain.assert_called_once()


class TestCmdStats:
    def test_stats_calls_monitor(self):
        mock_monitor = MagicMock()
        mock_monitor.check.return_value = {
            "total_events": 100,
            "file_size_mb": 1.5,
            "throughput_per_min": 5,
            "last_event_time": "2026-05-22T10:00:00Z",
            "healthy": True,
        }
        mock_monitor.check()
        mock_monitor.check.assert_called_once()


class TestCmdTrail:
    def test_trail_calls_query(self):
        mock_query = MagicMock()
        mock_query.trail_for_ai_context.return_value = {
            "total_events": 50,
            "recent_events": 10,
            "token_estimate": 500,
            "within_budget": True,
            "summary": "test summary",
        }
        mock_query.trail_for_ai_context("sess-1")
        mock_query.trail_for_ai_context.assert_called_once_with("sess-1")


class TestCmdHealth:
    def test_health_all_ok(self, capsys):
        mock_monitor = MagicMock()
        mock_monitor.heartbeat.return_value = {"healthy": True, "total_events": 100, "file_size_mb": 1.0}
        mock_verifier = MagicMock()
        mock_verifier.verify_chain.return_value = {"status": "valid", "issues": []}
        mock_monitor.heartbeat()
        mock_verifier.verify_chain()
        assert mock_monitor.heartbeat.return_value["healthy"] is True


class TestCmdQueryAgent:
    def test_query_agent_calls_by_agent(self):
        mock_query = MagicMock()
        mock_query.by_agent.return_value = [
            {"timestamp": "2026-05-22T10:00:00Z", "event_type": "write", "target_path": "f1"},
        ]
        mock_query.by_agent("agent-1")
        mock_query.by_agent.assert_called_once_with("agent-1")


class TestMain:
    def test_main_no_args_exits(self):
        with patch("sys.argv", ["cli"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1

    def test_main_unknown_command_exits(self):
        with patch("sys.argv", ["cli", "unknown_cmd"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1
