# [BLUEPRINT] MOD-CMP-007 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""MOD-CMP-001 四项必做清单完成度检测 单元测试（43 号 §3，BM-BUY-08-A）。"""

from __future__ import annotations

from datetime import date, datetime, time

from zephyr.compliance.compliance_log import ComplianceLogger
from zephyr.compliance.discipline_must_do_checker import (
    REQUIRED_ITEMS,
    ChecklistAction,
    ChecklistCheckpoint,
    ChecklistCompletionChecker,
)

_TD = date(2026, 8, 14)  # 周五交易日
_ALL = {cp: set(items) for cp, items in REQUIRED_ITEMS.items()}


def _provider(done: dict[ChecklistCheckpoint, set[str]]):
    return lambda cp, td: done.get(cp, set())


def _checker(done, tmp_path, **kw):
    return ChecklistCompletionChecker(_provider(done), ComplianceLogger(tmp_path / "c.jsonl"), **kw)


def test_all_complete_action_none(tmp_path):
    v = _checker(_ALL, tmp_path).check_checkpoint(ChecklistCheckpoint.PRE_MARKET, datetime(2026, 8, 14, 7, 50))
    assert v.complete and v.action is ChecklistAction.NONE


def test_pre_market_missing_before_deadline_no_action(tmp_path):
    """08:00 前缺失=正常进行中，不告警。"""
    v = _checker({}, tmp_path).check_checkpoint(ChecklistCheckpoint.PRE_MARKET, datetime(2026, 8, 14, 7, 30))
    assert not v.complete and v.action is ChecklistAction.NONE
    assert set(v.missing_items) == _ALL[ChecklistCheckpoint.PRE_MARKET]


def test_pre_market_missing_after_deadline_warning(tmp_path):
    v = _checker({}, tmp_path).check_checkpoint(ChecklistCheckpoint.PRE_MARKET, datetime(2026, 8, 14, 8, 1))
    assert v.action is ChecklistAction.WARNING


def test_intraday_missing_hard_block(tmp_path):
    """盘中执行=唯一 Hard Block 项（§3.3）。"""
    v = _checker({}, tmp_path).check_checkpoint(ChecklistCheckpoint.INTRADAY, datetime(2026, 8, 14, 10, 0))
    assert v.action is ChecklistAction.HARD_BLOCK


def test_intraday_partial_missing_hard_block(tmp_path):
    done = {ChecklistCheckpoint.INTRADAY: {"signal_compliance_check", "risk_param_confirm"}}
    v = _checker(done, tmp_path).check_checkpoint(ChecklistCheckpoint.INTRADAY, datetime(2026, 8, 14, 10, 0))
    assert v.action is ChecklistAction.HARD_BLOCK
    assert v.missing_items == ("position_limit_verify",)


def test_post_market_same_day_evening_not_overdue(tmp_path):
    """盘后清单截止=次日 09:15，当日 20:00 检测不超时。"""
    v = _checker({}, tmp_path).check_checkpoint(
        ChecklistCheckpoint.POST_MARKET, datetime(2026, 8, 14, 20, 0), trade_date=_TD
    )
    assert v.action is ChecklistAction.NONE


def test_post_market_next_morning_overdue_warning(tmp_path):
    """次日 09:20 仍未完成 → Warning（trade_date 传前一交易日）。"""
    v = _checker({}, tmp_path).check_checkpoint(
        ChecklistCheckpoint.POST_MARKET, datetime(2026, 8, 15, 9, 20), trade_date=_TD
    )
    assert v.action is ChecklistAction.WARNING


def test_provider_failure_intraday_fail_closed(tmp_path):
    """信号源失效 + 盘中 → Fail-Closed 拒单（§1.3/§3.3）。"""

    def boom(cp, td):
        raise RuntimeError("artifact store down")

    c = ChecklistCompletionChecker(boom, ComplianceLogger(tmp_path / "c.jsonl"))
    v = c.check_checkpoint(ChecklistCheckpoint.INTRADAY, datetime(2026, 8, 14, 10, 0))
    assert v.action is ChecklistAction.HARD_BLOCK
    assert "Fail-Closed" in v.detail


def test_provider_failure_non_intraday_degrade_warning(tmp_path):
    """信号源失效 + 非盘中 → 降级人工 checklist，Warning 不阻断。"""

    def boom(cp, td):
        raise RuntimeError("down")

    c = ChecklistCompletionChecker(boom, ComplianceLogger(tmp_path / "c.jsonl"))
    v = c.check_checkpoint(ChecklistCheckpoint.EVENING, datetime(2026, 8, 14, 22, 0))
    assert v.action is ChecklistAction.WARNING


def test_verdict_logged(tmp_path):
    log = ComplianceLogger(tmp_path / "c.jsonl")
    ChecklistCompletionChecker(_provider(_ALL), log).check_checkpoint(
        ChecklistCheckpoint.PRE_MARKET, datetime(2026, 8, 14, 7, 50)
    )
    records = log.read_all()
    assert len(records) == 1
    assert records[0].event_type == "CHECKLIST_VERDICT"
    assert records[0].payload["checkpoint"] == "PRE_MARKET"


def test_custom_deadline_override(tmp_path):
    """截止时间可注入覆盖。"""
    c = _checker({}, tmp_path, pre_market_deadline=time(7, 0))
    v = c.check_checkpoint(ChecklistCheckpoint.PRE_MARKET, datetime(2026, 8, 14, 7, 30))
    assert v.action is ChecklistAction.WARNING
