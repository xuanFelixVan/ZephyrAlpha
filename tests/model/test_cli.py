# [A_test] module_id: MOD-GOV_cli | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-034 | docs/03_modules/_cross_layer/model_profiler/blueprint.md | §3
# [MODULE] tests.test_cli
# [INVARIANTS] test_cli完整性
# [MODIFY-GUARD] none
# [CONSUMERS] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

import sys
from unittest.mock import MagicMock, patch

from zephyr.intelligence.model_profiling.cli import (
    cmd_discover,
    cmd_drift,
    cmd_history,
    cmd_quick,
    main,
)


class TestMainNoArgs:
    def test_prints_docstring(self, capsys):
        sys.argv = ["cli"]
        main()
        captured = capsys.readouterr()
        from zephyr.ex_core.src.zephyr import cli as _cli

        assert captured.out.startswith(_cli.__doc__)


class TestMainDiscover:
    @patch("zephyr.intelligence.model_profiling.cli.cmd_discover")
    def test_dispatches_discover(self, mock_discover):
        sys.argv = ["cli", "discover"]
        main()
        mock_discover.assert_called_once()


class TestMainQuickWithoutModel:
    def test_prints_usage(self, capsys):
        sys.argv = ["cli", "quick"]
        main()
        captured = capsys.readouterr()
        assert "用法" in captured.out
        assert "quick" in captured.out
        assert "<model_name>" in captured.out


class TestMainDriftWithoutModel:
    def test_prints_usage(self, capsys):
        sys.argv = ["cli", "drift"]
        main()
        captured = capsys.readouterr()
        assert "用法" in captured.out
        assert "drift" in captured.out
        assert "<model_name>" in captured.out


class TestMainUnknownCommand:
    def test_prints_error(self, capsys):
        sys.argv = ["cli", "foobar"]
        main()
        captured = capsys.readouterr()
        assert "未知命令" in captured.out
        assert "foobar" in captured.out


class TestCmdHistoryNoDataDir:
    def test_prints_no_history_message(self, capsys, monkeypatch):
        fake_path = MagicMock()
        fake_path.exists.return_value = False
        monkeypatch.setattr("zephyr.intelligence.model_profiling.cli.Path", lambda *a, **kw: fake_path)
        cmd_history()
        captured = capsys.readouterr()
        assert "暂无" in captured.out


class TestCmdDiscoverOllamaUnavailable:
    @patch("zephyr.ex_core.src.zephyr.ModelDiscovery")
    def test_prints_unavailable_message(self, MockDiscovery, capsys):
        instance = MockDiscovery.return_value
        instance.ollama_available.return_value = False
        cmd_discover()
        captured = capsys.readouterr()
        assert "Ollama" in captured.out
        assert "未运行" in captured.out


class TestCmdQuickUnavailableModel:
    @patch("zephyr.ex_core.src.zephyr.ModelProfiler")
    def test_prints_unavailable_message(self, MockProfiler, capsys):
        instance = MockProfiler.return_value
        instance.quick_profile.return_value = None
        cmd_quick("nonexistent:model")
        captured = capsys.readouterr()
        assert "无法测试模型" in captured.out
        assert "nonexistent:model" in captured.out

    @patch("zephyr.ex_core.src.zephyr.ModelProfiler")
    def test_prints_unavailable_when_zero_tests(self, MockProfiler, capsys):
        instance = MockProfiler.return_value
        profile = MagicMock()
        profile.total_tests = 0
        instance.quick_profile.return_value = profile
        cmd_quick("empty:model")
        captured = capsys.readouterr()
        assert "无法测试模型" in captured.out


class TestCmdDriftInsufficientHistory:
    @patch("zephyr.intelligence.model_profiling.results_writer.load_benchmark_history")
    def test_prints_insufficient_message(self, mock_load, capsys):
        mock_load.return_value = [MagicMock()]
        cmd_drift("qwen3:8b")
        captured = capsys.readouterr()
        assert "历史数据不足" in captured.out
        assert "仅 1 条记录" in captured.out

    @patch("zephyr.intelligence.model_profiling.results_writer.load_benchmark_history")
    def test_prints_insufficient_when_empty(self, mock_load, capsys):
        mock_load.return_value = []
        cmd_drift("qwen3:8b")
        captured = capsys.readouterr()
        assert "历史数据不足" in captured.out
        assert "仅 0 条记录" in captured.out


class TestMainQuickWithModel:
    @patch("zephyr.intelligence.model_profiling.cli.cmd_quick")
    def test_dispatches_quick_with_model_name(self, mock_quick):
        sys.argv = ["cli", "quick", "qwen3:8b"]
        main()
        mock_quick.assert_called_once_with("qwen3:8b")


class TestMainDriftWithModel:
    @patch("zephyr.intelligence.model_profiling.cli.cmd_drift")
    def test_dispatches_drift_with_model_name(self, mock_drift):
        sys.argv = ["cli", "drift", "qwen3:8b"]
        main()
        mock_drift.assert_called_once_with("qwen3:8b")


class TestMainBenchmark:
    @patch("zephyr.intelligence.model_profiling.cli.cmd_benchmark")
    def test_dispatches_benchmark(self, mock_benchmark):
        sys.argv = ["cli", "benchmark"]
        main()
        mock_benchmark.assert_called_once()


class TestMainBest:
    @patch("zephyr.intelligence.model_profiling.cli.cmd_best")
    def test_dispatches_best(self, mock_best):
        sys.argv = ["cli", "best"]
        main()
        mock_best.assert_called_once()


class TestMainHistory:
    @patch("zephyr.intelligence.model_profiling.cli.cmd_history")
    def test_dispatches_history(self, mock_history):
        sys.argv = ["cli", "history"]
        main()
        mock_history.assert_called_once()
