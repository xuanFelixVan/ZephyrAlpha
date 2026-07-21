"""cli 单测（MOD-L00-004 阶段3）。

测试内容：
- _build_parser：7 子命令注册 + 无命令报错
- status：无 task_id（调度器状态 + 最近运行）/ 有 task_id（单任务详情）/ 任务不存在
- list：全部 / 按源过滤
- run：成功 / 失败
- rerun-failed：无失败 / 有失败（部分成功）
- pause/resume：未知源 / 成功 / 幂等（已熔断/未熔断）
- main：异常处理

不测试 start 命令（常驻进程会阻塞）。
"""
from unittest.mock import patch, MagicMock

import pytest

from zephyr.data.cli import main, _build_parser
from zephyr.data.policy_registry import SourcePolicy


# ============== Parser ==============

class TestParser:
    def test_build_parser_has_7_subcommands(self):
        """parser 应注册 7 个子命令。"""
        parser = _build_parser()
        # 找到 subparsers action（choices 属性包含子命令）
        sub_action = None
        for action in parser._actions:
            if hasattr(action, "choices") and isinstance(action.choices, dict):
                sub_action = action
                break
        assert sub_action is not None
        cmds = set(sub_action.choices.keys())
        assert cmds == {"status", "list", "run", "rerun-failed", "pause", "resume", "start"}

    def test_no_command_exits(self):
        """无子命令应 SystemExit（required=True）。"""
        with pytest.raises(SystemExit):
            _build_parser().parse_args([])


# ============== status ==============

class TestStatusCmd:
    def test_status_no_task_id(self, capsys):
        """status 无 task_id：打印调度器状态 + 最近运行记录。"""
        mock_sched = MagicMock()
        mock_sched.get_status.return_value = {
            "started": False,
            "schedules": ["daily_kline", "daily_capital"],
            "task_count": 5,
            "providers": [],
            "task_summary": {},
        }
        mock_sched._progress_store.list_recent_runs.return_value = [
            {"task_id": "t1", "started_at": "2026-07-06 16:30", "finished_at": "2026-07-06 16:31", "status": "SUCCESS", "rows_fetched": 100}
        ]
        with patch("zephyr.data.get_integrator", return_value=mock_sched):
            rc = main(["status"])
        assert rc == 0
        out = capsys.readouterr().out
        assert "调度器状态" in out
        assert "daily_kline" in out
        assert "t1" in out

    def test_status_with_task_id(self, capsys):
        """status <task_id>：打印单任务详情。"""
        mock_sched = MagicMock()
        mock_sched._progress_store.get_task_status.return_value = {
            "task_id": "t1",
            "source": "ifind",
            "last_run_at": "2026-07-06 16:30",
            "last_key": "2026-07-05",
            "last_status": "SUCCESS",
            "rows_total": 100,
        }
        with patch("zephyr.data.get_integrator", return_value=mock_sched):
            rc = main(["status", "t1"])
        assert rc == 0
        out = capsys.readouterr().out
        assert "t1" in out
        assert "ifind" in out
        assert "SUCCESS" in out

    def test_status_task_not_found(self, capsys):
        """status <unknown>：任务无记录返回 1。"""
        mock_sched = MagicMock()
        mock_sched._progress_store.get_task_status.return_value = None
        with patch("zephyr.data.get_integrator", return_value=mock_sched):
            rc = main(["status", "unknown"])
        assert rc == 1


# ============== list ==============

class TestListCmd:
    def test_list_all(self, capsys):
        """list 无过滤：打印所有任务。"""
        mock_sched = MagicMock()
        mock_sched.list_tasks.return_value = [
            {"task_id": "t1", "source": "ifind", "table": "c1_market.kline_daily", "schedule": "daily_kline", "incremental": True},
            {"task_id": "t2", "source": "akshare", "table": "c1_market.fin", "schedule": "daily_kline", "incremental": True},
        ]
        with patch("zephyr.data.get_integrator", return_value=mock_sched):
            rc = main(["list"])
        assert rc == 0
        out = capsys.readouterr().out
        assert "所有任务" in out
        assert "t1" in out
        assert "t2" in out

    def test_list_by_source(self, capsys):
        """list --source ifind：仅打印该源任务。"""
        mock_sched = MagicMock()
        mock_sched.list_tasks.return_value = [
            {"task_id": "t1", "source": "ifind", "table": "c1.kline", "schedule": "daily_kline", "incremental": True},
            {"task_id": "t2", "source": "akshare", "table": "c1.fin", "schedule": "daily_kline", "incremental": True},
        ]
        with patch("zephyr.data.get_integrator", return_value=mock_sched):
            rc = main(["list", "--source", "ifind"])
        assert rc == 0
        out = capsys.readouterr().out
        assert "ifind" in out
        # mock_sched.list_tasks 返回所有，CLI 内部过滤
        assert "t1" in out


# ============== run ==============

class TestRunCmd:
    def test_run_success(self, capsys):
        """run <task_id> 成功返回 0。"""
        mock_sched = MagicMock()
        mock_sched.run_task.return_value = True
        with patch("zephyr.data.get_integrator", return_value=mock_sched):
            rc = main(["run", "t1"])
        assert rc == 0
        out = capsys.readouterr().out
        assert "成功" in out
        mock_sched.run_task.assert_called_once_with("t1")

    def test_run_failure(self, capsys):
        """run <task_id> 失败返回 1。"""
        mock_sched = MagicMock()
        mock_sched.run_task.return_value = False
        with patch("zephyr.data.get_integrator", return_value=mock_sched):
            rc = main(["run", "t1"])
        assert rc == 1
        out = capsys.readouterr().out
        assert "失败" in out


# ============== rerun-failed ==============

class TestRerunFailedCmd:
    def test_rerun_no_failed(self, capsys):
        """无失败任务返回 0。"""
        mock_sched = MagicMock()
        mock_sched._progress_store.list_failed_tasks.return_value = []
        with patch("zephyr.data.get_integrator", return_value=mock_sched):
            rc = main(["rerun-failed"])
        assert rc == 0
        out = capsys.readouterr().out
        assert "无失败任务" in out

    def test_rerun_all_success(self, capsys):
        """失败任务全部重跑成功返回 0。"""
        mock_sched = MagicMock()
        mock_sched._progress_store.list_failed_tasks.return_value = [
            {"task_id": "t1"},
            {"task_id": "t2"},
        ]
        mock_sched.run_task.side_effect = [True, True]
        with patch("zephyr.data.get_integrator", return_value=mock_sched):
            rc = main(["rerun-failed"])
        assert rc == 0
        out = capsys.readouterr().out
        assert "2/2 成功" in out

    def test_rerun_partial_failure(self, capsys):
        """部分重跑失败返回 1。"""
        mock_sched = MagicMock()
        mock_sched._progress_store.list_failed_tasks.return_value = [
            {"task_id": "t1"},
            {"task_id": "t2"},
        ]
        mock_sched.run_task.side_effect = [True, False]
        with patch("zephyr.data.get_integrator", return_value=mock_sched):
            rc = main(["rerun-failed"])
        assert rc == 1
        out = capsys.readouterr().out
        assert "1/2 成功" in out


# ============== pause / resume ==============

class TestPauseResumeCmd:
    def test_pause_unknown_source(self, capsys):
        """pause 未知源返回 1。"""
        mock_registry = MagicMock()
        mock_registry.list_sources.return_value = ["ifind", "akshare"]
        with patch("zephyr.data.cli.get_registry", return_value=mock_registry):
            rc = main(["pause", "unknown"])
        assert rc == 1
        mock_registry.register.assert_not_called()

    def test_pause_success(self, capsys):
        """pause 已知源：register enabled=False。"""
        mock_registry = MagicMock()
        mock_registry.list_sources.return_value = ["ifind"]
        mock_registry.get_policy.return_value = SourcePolicy(rpm=60, enabled=True)
        with patch("zephyr.data.cli.get_registry", return_value=mock_registry):
            rc = main(["pause", "ifind"])
        assert rc == 0
        mock_registry.register.assert_called_once()
        args = mock_registry.register.call_args[0]
        assert args[0] == "ifind"
        assert args[1].enabled is False
        # 其他字段保留
        assert args[1].rpm == 60

    def test_pause_already_paused(self, capsys):
        """pause 已熔断的源：幂等返回 0，不调 register。"""
        mock_registry = MagicMock()
        mock_registry.list_sources.return_value = ["ifind"]
        mock_registry.get_policy.return_value = SourcePolicy(enabled=False)
        with patch("zephyr.data.cli.get_registry", return_value=mock_registry):
            rc = main(["pause", "ifind"])
        assert rc == 0
        mock_registry.register.assert_not_called()

    def test_resume_unknown_source(self, capsys):
        """resume 未知源返回 1。"""
        mock_registry = MagicMock()
        mock_registry.list_sources.return_value = ["ifind"]
        with patch("zephyr.data.cli.get_registry", return_value=mock_registry):
            rc = main(["resume", "unknown"])
        assert rc == 1

    def test_resume_success(self, capsys):
        """resume 已熔断的源：register enabled=True。"""
        mock_registry = MagicMock()
        mock_registry.list_sources.return_value = ["ifind"]
        mock_registry.get_policy.return_value = SourcePolicy(rpm=60, enabled=False)
        with patch("zephyr.data.cli.get_registry", return_value=mock_registry):
            rc = main(["resume", "ifind"])
        assert rc == 0
        mock_registry.register.assert_called_once()
        args = mock_registry.register.call_args[0]
        assert args[0] == "ifind"
        assert args[1].enabled is True
        assert args[1].rpm == 60

    def test_resume_not_paused(self, capsys):
        """resume 未熔断的源：幂等返回 0，不调 register。"""
        mock_registry = MagicMock()
        mock_registry.list_sources.return_value = ["ifind"]
        mock_registry.get_policy.return_value = SourcePolicy(enabled=True)
        with patch("zephyr.data.cli.get_registry", return_value=mock_registry):
            rc = main(["resume", "ifind"])
        assert rc == 0
        mock_registry.register.assert_not_called()


# ============== main 入口 ==============

class TestMainEntry:
    def test_main_handler_exception_returns_1(self, capsys):
        """命令处理异常应捕获并返回 1（不抛异常）。"""
        mock_sched = MagicMock()
        mock_sched.get_status.side_effect = RuntimeError("boom")
        with patch("zephyr.data.get_integrator", return_value=mock_sched):
            rc = main(["status"])
        assert rc == 1
        out = capsys.readouterr().out
        assert "异常" in out

    def test_main_get_integrator_failure_returns_1(self, capsys):
        """get_integrator 失败应返回 1。"""
        with patch("zephyr.data.get_integrator", side_effect=RuntimeError("init failed")):
            rc = main(["status"])
        assert rc == 1
        out = capsys.readouterr().out
        assert "获取调度器失败" in out
