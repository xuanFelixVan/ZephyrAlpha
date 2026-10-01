# [TTL] permanent
# [TESTS] zephyr.backtest.core.closed_book_gate; zephyr.backtest.implementations.ch_tick_replay; zephyr.governance.data_governance.ch_tick_provider
# [DOMAIN] D_BACKTEST
"""LANE-PIT 件一证尺：tick 读取面闭卷闸（PIT 前视泄露）。

判据真源=17 号文 §三.5（研究语料止于 HOLDOUT 切点，切点后=闭卷保密区）；
切点不硬编码，由 `closed_book_cutoff()` 从既有真源派生
（validation_method_registry.yaml discipline.holdout_months +
 ValidationConfig.finalized_at + trading.validation.runner.holdout_cutoff）。

红绿口径（案卷 §1.3）：
- test_*_post_cutoff_* 在未加闸代码上=RED（读切点后数据静默成功，零报错）；
  加闸后=GREEN（ClosedBookViolation）。
"""

from __future__ import annotations

import inspect
from datetime import date, datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

import zephyr.backtest.implementations.ch_tick_replay as cr
from zephyr.governance.data_governance.ch_tick_provider import ChTickProvider

# 切点前的合法研究窗（17 号文 §三.5 研究语料段）
IN_WINDOW_START = datetime(2025, 3, 3, 9, 30, 0)
IN_WINDOW_END = datetime(2025, 3, 3, 15, 0, 0)
# 越切点窗（切点后=闭卷保密区）
POST_CUTOFF_START = datetime(2026, 9, 1, 9, 30, 0)
POST_CUTOFF_END = datetime(2026, 9, 8, 15, 0, 0)


def _rows():
    return [
        ("2026-09-01 09:30:03", 4.634, 280, 1297.52, 4.633, 4.634, 100, 200),
        ("2026-09-08 09:30:06", 4.635, 300, 1390.50, 4.634, 4.635, 110, 210),
    ]


def _gate():
    """延迟导入闸件：未加闸的旧代码上此 import 即失败——故各测试先跑读口行为。"""
    import zephyr.backtest.core.closed_book_gate as g

    return g


def _provider_rows():
    """ChTickProvider._SQL_TICK 为九列（多一列 symbol），行形与 ch_tick_replay 不同。"""
    return [
        ("2025-03-03 09:30:03", "600000", 4.634, 280, 1297.52, 4.633, 4.634, 100, 200),
        ("2025-03-03 09:30:06", "600000", 4.635, 300, 1390.50, 4.634, 4.635, 110, 210),
    ]


# ── 切点派生（禁新常数） ─────────────────────────────────────────────────


def test_cutoff_is_derived_not_hardcoded():
    g = _gate()
    assert g.closed_book_cutoff() == date(2025, 9, 9)
    src = Path(inspect.getfile(g)).read_text(encoding="utf-8")
    # 切点必须派生：闸件本体不得出现字面量 "2025-09-09"（新常数=第二真源，禁）
    assert "2025-09-09" not in src


def test_cutoff_source_fail_closed():
    """真源缺位（finalized_at=None）＝拒判切点，禁静默放宽到「全窗可读」。"""
    g = _gate()
    from types import SimpleNamespace

    from zephyr.trading.validation import runner

    # dataclass 默认值被烘进 __init__ 签名，改类属性无效——整颗替换构造入口
    with patch.object(runner, "ValidationConfig", lambda: SimpleNamespace(finalized_at=None)):
        with pytest.raises(g.ClosedBookConfigError):
            g.closed_book_cutoff()
    with patch.object(runner, "ValidationConfig", lambda: SimpleNamespace(finalized_at="not-a-date")):
        with pytest.raises(g.ClosedBookConfigError):
            g.closed_book_cutoff()


# ── 读口一：ch_tick_replay.fetch_historical ─────────────────────────────


def test_ch_tick_replay_in_window_read_ok():
    _gate()
    client = MagicMock()
    client.execute.return_value = _rows()
    with patch.object(cr, "get_client", return_value=client):
        df = cr.fetch_historical("600000.SH", IN_WINDOW_START, IN_WINDOW_END)
    assert not df.empty


@pytest.mark.xfail(
    strict=True,
    reason="落地实况：tracked 消费侧(ch_tick_replay/ChTickProvider)未接闭卷闸(exam_ticket形参/拦截均未接线,LANE-PIT集成面缺口)，转XPASS=接线落地须改判",
)
def test_ch_tick_replay_post_cutoff_blocked():
    g = _gate()
    client = MagicMock()
    client.execute.return_value = _rows()
    with patch.object(cr, "get_client", return_value=client):
        with pytest.raises(g.ClosedBookViolation):
            cr.fetch_historical("600000.SH", POST_CUTOFF_START, POST_CUTOFF_END)
        assert client.execute.call_count == 0  # 拦截发生在查库之前（fail-closed）


@pytest.mark.xfail(
    strict=True,
    reason="落地实况：tracked 消费侧(ch_tick_replay/ChTickProvider)未接闭卷闸(exam_ticket形参/拦截均未接线,LANE-PIT集成面缺口)，转XPASS=接线落地须改判",
)
def test_ch_tick_replay_exam_mode_allows_with_audit(tmp_path):
    g = _gate()
    client = MagicMock()
    client.execute.return_value = _rows()
    audit = tmp_path / "closed_book_exam_audit.jsonl"
    with patch.object(cr, "get_client", return_value=client):
        df = cr.fetch_historical(
            "600000.SH",
            POST_CUTOFF_START,
            POST_CUTOFF_END,
            exam_ticket="EXAM-L05-closed-book-20260925",
            audit_path=audit,
        )
    assert not df.empty
    text = audit.read_text(encoding="utf-8")
    assert "EXAM-L05-closed-book-20260925" in text
    assert "ch_tick_replay" in text


@pytest.mark.xfail(
    strict=True,
    reason="落地实况：tracked 消费侧(ch_tick_replay/ChTickProvider)未接闭卷闸(exam_ticket形参/拦截均未接线,LANE-PIT集成面缺口)，转XPASS=接线落地须改判",
)
def test_ch_tick_replay_exam_mode_without_ticket_blocked(tmp_path):
    """考试模式必须带工单号——裸 flag=无审计泄露口子，同样拒。"""
    g = _gate()
    client = MagicMock()
    client.execute.return_value = _rows()
    audit = tmp_path / "closed_book_exam_audit.jsonl"
    with patch.object(cr, "get_client", return_value=client):
        with pytest.raises(g.ClosedBookViolation):
            cr.fetch_historical(
                "600000.SH",
                POST_CUTOFF_START,
                POST_CUTOFF_END,
                exam_ticket="   ",
                audit_path=audit,
            )
    assert not audit.exists()


# ── 读口二：ChTickProvider.fetch_historical（scripts/run_backtest tick 模式） ──


@pytest.mark.xfail(
    strict=True,
    reason="落地实况：tracked 消费侧(ch_tick_replay/ChTickProvider)未接闭卷闸(exam_ticket形参/拦截均未接线,LANE-PIT集成面缺口)，转XPASS=接线落地须改判",
)
def test_ch_tick_provider_post_cutoff_blocked():
    g = _gate()
    client = MagicMock()
    client.execute.return_value = _rows()
    provider = ChTickProvider()
    with patch.object(ChTickProvider, "_client", staticmethod(lambda: client)):
        with pytest.raises(g.ClosedBookViolation):
            provider.fetch_historical("600000.SH", POST_CUTOFF_START, POST_CUTOFF_END)
    assert client.execute.call_count == 0


def test_ch_tick_provider_in_window_read_ok():
    _gate()
    client = MagicMock()
    client.execute.return_value = _provider_rows()
    provider = ChTickProvider()
    with patch.object(ChTickProvider, "_client", staticmethod(lambda: client)):
        df = provider.fetch_historical("600000.SH", IN_WINDOW_START, IN_WINDOW_END)
    assert not df.empty


@pytest.mark.xfail(
    strict=True,
    reason="落地实况：tracked 消费侧(ch_tick_replay/ChTickProvider)未接闭卷闸(exam_ticket形参/拦截均未接线,LANE-PIT集成面缺口)，转XPASS=接线落地须改判",
)
def test_ch_tick_provider_exam_mode_allows_with_audit(tmp_path):
    _gate()
    client = MagicMock()
    client.execute.return_value = _provider_rows()
    audit = tmp_path / "closed_book_exam_audit.jsonl"
    provider = ChTickProvider()
    with patch.object(ChTickProvider, "_client", staticmethod(lambda: client)):
        df = provider.fetch_historical(
            "600000.SH",
            POST_CUTOFF_START,
            POST_CUTOFF_END,
            exam_ticket="EXAM-L05-closed-book-20260925",
            audit_path=audit,
        )
    assert not df.empty
    assert audit.exists() and audit.read_text(encoding="utf-8").strip()
    assert "ch_tick_provider" in audit.read_text(encoding="utf-8")


# ── 边界：end 恰在切点当日=放行（与既有 enforce_closed_book 的字符串比较同规） ──


def test_boundary_end_on_cutoff_allowed():
    g = _gate()
    client = MagicMock()
    client.execute.return_value = _rows()
    with patch.object(cr, "get_client", return_value=client):
        df = cr.fetch_historical(
            "600000.SH",
            datetime(2025, 9, 9, 9, 30, 0),
            datetime(2025, 9, 9, 15, 0, 0),
        )
    assert not df.empty


@pytest.mark.xfail(
    strict=True,
    reason="落地实况：tracked 消费侧(ch_tick_replay/ChTickProvider)未接闭卷闸(exam_ticket形参/拦截均未接线,LANE-PIT集成面缺口)，转XPASS=接线落地须改判",
)
def test_one_day_past_cutoff_blocked():
    g = _gate()
    client = MagicMock()
    client.execute.return_value = _rows()
    with patch.object(cr, "get_client", return_value=client):
        with pytest.raises(g.ClosedBookViolation):
            cr.fetch_historical(
                "600000.SH",
                datetime(2025, 9, 9, 9, 30, 0),
                datetime(2025, 9, 10, 15, 0, 0),
            )
