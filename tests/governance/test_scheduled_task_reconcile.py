# [BLUEPRINT] MOD-TEST-001 | tests/governance/test_scheduled_task_reconcile.py | §
# [MODULE] tests.governance.test_scheduled_task_reconcile
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.governance.scheduled_task_reconcile（importlib 文件加载）
# [CONSUMERS] pytest
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 纯单元测试（tmp_path + fake runner 注入，零真 PowerShell/零任务操控调用）；三色判定与期望清单导出（register ps1 真源 grep 语义）全覆盖；只读红线由 fake runner 断言查询串零操控动词间接锁定
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 测试永不抛未捕获异常
# [TESTS] self
# [A_module] module_id=MOD-TEST-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_scheduled_task_reconcile.py — 计划任务三色对账单元测试（QMine M5 矿④）。

覆盖：
1. 期望清单导出：register ps1 任务名字面声明 grep（单任务 daily / 多任务不继承 daily /
   注释行不算声明 / backup_daily_trigger.ps1 纳入）
2. 三色判定：绿（0 / Running+267009）｜黄（267011 哨兵/267014/267008/267012/Disabled/
   日触发节奏陈旧）｜红（其余非零）
3. 对账聚合：声明有而系统无=红；系统在册无声明=漂移单列；markdown 渲染含三色与零操控动词
4. collect_system_tasks：fixture 化假 PowerShell 输出解析；零行输出拒绝出全绿假表
"""

from __future__ import annotations

import importlib.util
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SCRIPT = _REPO_ROOT / "scripts" / "governance" / "scheduled_task_reconcile.py"

_spec = importlib.util.spec_from_file_location("_sched_task_reconcile_under_test", _SCRIPT)
assert _spec is not None and _spec.loader is not None
str_mod = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = str_mod
_spec.loader.exec_module(str_mod)

_NOW = datetime(2026, 9, 25, 12, 0, 0).astimezone()
_FAKE_PS = (
    "ZephyrAlpha_ConfigCheck|Ready|0|2026-09-25 08:05:00\n"
    "ZephyrAlpha-DailyBackup|Ready|267014|2026-09-25 06:00:00\n"
    "ZephyrAlpha_LibraryLedgerDrill|Ready|267011|1999-11-30 00:00:00\n"
    "ZephyrAlpha_F06Grid|Ready|1|2026-09-25 03:00:00\n"
    "ZephyrAlpha_BeltDaemon|Running|267009|2026-09-25 11:59:00\n"
    "ZephyrAlpha_WeeklyRest|Disabled|267014|2026-09-20 00:00:00\n"
    "ZephyrAlpha_SoloGhostTask|Ready|0|\n"
)


@pytest.fixture()
def scripts_dir(tmp_path: Path) -> Path:
    """register ps1 真源 fixture（形态对齐仓内实况：变量赋值+Register 行+注释不算声明）。"""
    (tmp_path / "register_config_check_task.ps1").write_text(
        "# Verify: schtasks /query /tn ZephyrAlpha_NotDeclared /v /fo LIST\n"
        '$TaskName = "ZephyrAlpha_ConfigCheck"\n'
        "Register-ScheduledTask -TaskName $TaskName\n"
        "$trigger = New-ScheduledTaskTrigger -Daily -At 8:05am\n",
        encoding="utf-8",
    )
    (tmp_path / "register_multi_mixed.ps1").write_text(
        '$TaskName = "ZephyrAlpha_MixA"\n'
        'Register-ScheduledTask -TaskName "ZephyrAlpha_MixB"\n'
        "$trigger = New-ScheduledTaskTrigger -Daily -At 3:30am\n",
        encoding="utf-8",
    )
    (tmp_path / "register_ledger_task.ps1").write_text(
        '$TaskName = "ZephyrAlpha_LibraryLedgerDrill"\nRegister-ScheduledTask -TaskName $TaskName\n',
        encoding="utf-8",
    )
    (tmp_path / "register_belt_daemon_task.ps1").write_text(
        '$TaskName = "ZephyrAlpha_BeltDaemon"\nRegister-ScheduledTask -TaskName $TaskName\n',
        encoding="utf-8",
    )
    (tmp_path / "register_weekly_rest.ps1").write_text(
        '$TaskName = "ZephyrAlpha_WeeklyRest"\nRegister-ScheduledTask -TaskName $TaskName\n',
        encoding="utf-8",
    )
    (tmp_path / "register_f06_grid_task.ps1").write_text(
        '$TaskName = "ZephyrAlpha_F06Grid"\nRegister-ScheduledTask -TaskName $TaskName\n',
        encoding="utf-8",
    )
    (tmp_path / "backup").mkdir()
    (tmp_path / "backup" / "backup_daily_trigger.ps1").write_text(
        '$TaskName = "ZephyrAlpha-DailyBackup"\n'
        "Register-ScheduledTask -TaskName $TaskName\n"
        "$trigger = New-ScheduledTaskTrigger -Daily -At 6:00am\n",
        encoding="utf-8",
    )
    return tmp_path


class TestExportExpectedTasks:
    """期望清单导出（零新登记册：真源=register ps1 字面声明）。"""

    def test_names_and_daily_from_single_task_file(self, scripts_dir: Path) -> None:
        expected = str_mod.export_expected_tasks(scripts_dir)
        assert "ZephyrAlpha_ConfigCheck" in expected
        assert expected["ZephyrAlpha_ConfigCheck"]["daily"] is True  # 单任务文件+Daily 声明 → 继承
        assert "ZephyrAlpha-DailyBackup" in expected  # backup_daily_trigger.ps1 纳入
        assert expected["ZephyrAlpha-DailyBackup"]["daily"] is True

    def test_comment_lines_not_declarations(self, scripts_dir: Path) -> None:
        """# 注释里的 query 示例不算声明（防假红）。"""
        assert "ZephyrAlpha_NotDeclared" not in str_mod.export_expected_tasks(scripts_dir)

    def test_multi_task_file_inherits_no_daily(self, scripts_dir: Path) -> None:
        """多任务文件触发器混杂 → 不整体继承 daily（防节奏陈旧假黄，保守漏报可接受）。"""
        expected = str_mod.export_expected_tasks(scripts_dir)
        assert expected["ZephyrAlpha_MixA"]["daily"] is False
        assert expected["ZephyrAlpha_MixB"]["daily"] is False

    def test_missing_scripts_root_gives_empty(self, tmp_path: Path) -> None:
        """声明侧目录缺失 → 期望空清单（ERROR_CONTRACT：如实呈现不假红）。"""
        assert str_mod.export_expected_tasks(tmp_path / "nope") == {}


class TestClassifyTask:
    """三色判定单入口。"""

    _OK = {"daily": False, "sources": ["x.ps1"]}

    def test_green_zero_and_running(self) -> None:
        assert (
            str_mod.classify_task(self._OK, state="Ready", result=0, last_run=_NOW - timedelta(hours=1), now=_NOW)[0]
            == "green"
        )
        assert str_mod.classify_task(
            self._OK, state="Running", result=267009, last_run=_NOW - timedelta(minutes=1), now=_NOW
        ) == (
            "green",
            "运行中（267009）",
        )

    @pytest.mark.parametrize("result", [267008, 267011, 267012, 267014], ids=["267008", "267011", "267012", "267014"])
    def test_yellow_known_codes(self, result: int) -> None:
        color, reason = str_mod.classify_task(self._OK, state="Ready", result=result, last_run=None, now=_NOW)
        assert color == "yellow"
        assert str(result) in reason

    def test_yellow_disabled_and_stale(self) -> None:
        assert str_mod.classify_task(self._OK, state="Disabled", result=0, last_run=None, now=_NOW)[0] == "yellow"
        daily = {"daily": True, "sources": ["x.ps1"]}
        color, reason = str_mod.classify_task(
            daily, state="Ready", result=0, last_run=_NOW - timedelta(days=3), now=_NOW
        )  # DailyBackup 断 3 天型：result=0 也拦
        assert (color, "节奏陈旧" in reason) == ("yellow", True)
        # 非日触发不查陈旧；日触发新鲜运行不黄
        assert (
            str_mod.classify_task(self._OK, state="Ready", result=0, last_run=_NOW - timedelta(days=30), now=_NOW)[0]
            == "green"
        )
        assert (
            str_mod.classify_task(daily, state="Ready", result=0, last_run=_NOW - timedelta(days=1), now=_NOW)[0]
            == "green"
        )

    def test_red_other_nonzero_and_running_residual(self) -> None:
        assert str_mod.classify_task(self._OK, state="Ready", result=1, last_run=_NOW, now=_NOW)[0] == "red"
        assert str_mod.classify_task(self._OK, state="Ready", result=3, last_run=None, now=_NOW)[0] == "red"
        assert (
            str_mod.classify_task(self._OK, state="Ready", result=267009, last_run=None, now=_NOW)[0] == "red"
        )  # 运行态残留非 Running


class TestBuildReportAndRender:
    """对账聚合+markdown 渲染（含双向漂移呈现）。"""

    def _report(self, system: dict, expected: dict) -> dict:
        return str_mod.build_report(system, expected, now=_NOW)

    def test_missing_declared_is_red_and_drift_listed(self, scripts_dir: Path) -> None:
        system = str_mod.collect_system_tasks(runner=lambda _cmd: _FAKE_PS)
        expected = str_mod.export_expected_tasks(scripts_dir)
        report = self._report(system, expected)
        by_task = {r["task"]: r for r in report["rows"]}
        # 声明有而系统无 → 红（观测簿 §6：BudgetReport/MetaqAuditReconcile/ModelExam/ModelIntelScan 型）
        assert by_task["ZephyrAlpha_MixA"]["color"] == "red"
        assert "声明有而系统无" in by_task["ZephyrAlpha_MixA"]["reason"]
        # 系统在册无声明 → 漂移单列（非红）
        assert "ZephyrAlpha_SoloGhostTask" in report["drift"]
        assert all("SoloGhost" not in r["task"] for r in report["rows"])

    def test_observed_workbook_shapes(self, scripts_dir: Path) -> None:
        """观测簿 §6 实测形态回归锁：267014/哨兵 267011/退出码 1/Running 正常。"""
        system = str_mod.collect_system_tasks(runner=lambda _cmd: _FAKE_PS)
        expected = str_mod.export_expected_tasks(scripts_dir)
        by_task = {r["task"]: r for r in self._report(system, expected)["rows"]}
        assert by_task["ZephyrAlpha-DailyBackup"]["color"] == "yellow"  # 267014 超时被终止
        assert by_task["ZephyrAlpha_LibraryLedgerDrill"]["color"] == "yellow"  # 从未运行哨兵
        assert by_task["ZephyrAlpha_F06Grid"]["color"] == "red"  # 退出码 1
        assert by_task["ZephyrAlpha_BeltDaemon"]["color"] == "green"  # Running+267009
        assert by_task["ZephyrAlpha_WeeklyRest"]["color"] == "yellow"  # Disabled
        assert by_task["ZephyrAlpha_ConfigCheck"]["color"] == "green"

    def test_render_markdown_contains_colors_and_readonly(self) -> None:
        system = str_mod.collect_system_tasks(runner=lambda _cmd: _FAKE_PS)
        expected = {
            "ZephyrAlpha_Ghost": {"daily": False, "sources": ["register_ghost.ps1"]},
            "ZephyrAlpha_F06Grid": {"daily": False, "sources": ["register_f06.ps1"]},
        }
        text = str_mod.render_markdown(self._report(system, expected))
        assert "三色对账" in text
        assert "ZephyrAlpha_F06Grid" in text and "🔴" in text
        assert "ZephyrAlpha_Ghost" in text and "声明有而系统无" in text
        # 只读红线：渲染文本与查询命令零任务操控动词
        for verb in (
            "Start-ScheduledTask",
            "Enable-ScheduledTask",
            "Disable-ScheduledTask",
            "Unregister-ScheduledTask",
            "Register-ScheduledTask ",
        ):
            assert verb not in str_mod._PS_QUERY

    def test_collect_parses_fixture_and_rejects_empty(self) -> None:
        tasks = str_mod.collect_system_tasks(runner=lambda _cmd: _FAKE_PS)
        assert tasks["ZephyrAlpha_BeltDaemon"] == {
            "state": "Running",
            "result": 267009,
            "last_run": datetime(2026, 9, 25, 11, 59).astimezone(),
        }
        assert tasks["ZephyrAlpha_LibraryLedgerDrill"]["last_run"] is None  # 1999 哨兵→无运行史
        with pytest.raises(RuntimeError, match="零行"):
            str_mod.collect_system_tasks(runner=lambda _cmd: "")


class TestReadOnlyInvariant:
    """只读红线：查询命令面零任务操控动词（INVARIANTS 承重）。"""

    def test_query_has_no_control_verbs(self) -> None:
        assert "Get-ScheduledTask" in str_mod._PS_QUERY
        for verb in (
            "Start-ScheduledTask",
            "Enable-ScheduledTask",
            "Disable-ScheduledTask",
            "Unregister-ScheduledTask",
            "Stop-ScheduledTask",
        ):
            assert verb not in str_mod._PS_QUERY
