# [TEST] tests/scripts/test_build_consensus_daily.py
# [DOMAIN] D_DATA
# [TARGET] scripts/ch/build_consensus_daily.py::build_consensus_rows / expand_report_slots / rating_score（纯函数核，无 IO）
# [TTL] permanent
"""build_consensus_daily 纯函数核单元测试（消费端 C1，2026-09-12）。

覆盖：PIT 窗口（发布日/窗宽边界）、日历年展开（fy 槽位→forecast_year）、
评级分映射（空值不计入均值）、多机构聚合统计。零 IO 零生产路径。
"""

from __future__ import annotations

import importlib.util
import sys
from datetime import date
from pathlib import Path

import pytest

_SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "ch" / "build_consensus_daily.py"
_spec = importlib.util.spec_from_file_location("build_consensus_daily", _SCRIPT)
_mod = importlib.util.module_from_spec(_spec)
sys.modules.setdefault("build_consensus_daily", _mod)
_spec.loader.exec_module(_mod)

TD = [date(2026, 8, 10), date(2026, 8, 11), date(2026, 8, 12)]


def _rep(symbol: str, pub: str, fy0: int = 2026, eps0: float | None = 1.0, rating: str = "买入", org: str = "A证券") -> dict:
    return {
        "symbol": symbol,
        "publish_date": pub,
        "fy0_year": fy0,
        "eps_fy0": eps0,
        "pe_fy0": 20.0,
        "fy1_year": fy0 + 1,
        "eps_fy1": (eps0 * 1.2) if eps0 is not None else None,
        "pe_fy1": 18.0,
        "fy2_year": 0,
        "eps_fy2": None,
        "pe_fy2": None,
        "org_name": org,
        "rating": rating,
    }


def test_pit_only_visible_reports():
    """trade_date=08-11 时，08-12 发布的研报不可见（防前视）。"""
    reports = [_rep("600519", "2026-08-12", eps0=2.0)]
    rows = _mod.build_consensus_rows(reports, TD, window_days=90)
    assert all(r[0] != "2026-08-11" for r in rows), "08-11 不应包含 08-12 发布的研报"
    rows_12 = [r for r in rows if r[0] == "2026-08-12"]
    assert rows_12, "08-12 当日可见"
    fy0 = next(r for r in rows_12 if r[2] == 2026)
    assert fy0[3] == pytest.approx(2.0)


def test_window_boundary_excludes_stale():
    """窗宽 90 天：91 天前的研报出窗。"""
    reports = [_rep("600519", "2026-05-01", eps0=9.9), _rep("600519", "2026-08-01", eps0=1.5)]
    rows = _mod.build_consensus_rows(reports, [date(2026, 8, 12)], window_days=90)
    fy0 = next(r for r in rows if r[2] == 2026)
    # 2026-05-01 距 2026-08-12 为 103 天 > 90 → 出窗
    assert fy0[3] == pytest.approx(1.5)
    assert fy0[9] == 1


def test_rating_mapping_and_unrated():
    """买入7/增持5 均值=6；空评级只计 n_unrated 不进均值。"""
    reports = [
        _rep("600519", "2026-08-01", rating="买入"),
        _rep("600519", "2026-08-02", rating="增持", org="B证券"),
        _rep("600519", "2026-08-03", rating="", org="C证券"),
    ]
    rows = _mod.build_consensus_rows(reports, [date(2026, 8, 12)], window_days=90)
    fy0 = next(r for r in rows if r[2] == 2026)
    assert fy0[11] == pytest.approx(6.0)
    assert fy0[12] == 1 and fy0[13] == 1 and fy0[16] == 1


def test_year_expansion_slots_to_calendar_years():
    """一份研报的 fy0/fy1 槽位展开为两个日历年行；槽位年 0 丢弃。"""
    reports = [_rep("600519", "2026-08-01", fy0=2026, eps0=1.0)]
    rows = _mod.build_consensus_rows(reports, [date(2026, 8, 12)], window_days=90)
    years = sorted(r[2] for r in rows)
    assert years == [2026, 2027]
    fy1 = next(r for r in rows if r[2] == 2027)
    assert fy1[3] == pytest.approx(1.2)


def test_two_reports_aggregate_mean_and_orgs():
    """两机构研报：均值/中位数/n_orgs 去重。"""
    reports = [
        _rep("600519", "2026-08-01", eps0=1.0, org="A证券"),
        _rep("600519", "2026-08-02", eps0=3.0, org="B证券"),
        _rep("600519", "2026-08-03", eps0=5.0, org="A证券"),
    ]
    rows = _mod.build_consensus_rows(reports, [date(2026, 8, 12)], window_days=90)
    fy0 = next(r for r in rows if r[2] == 2026)
    assert fy0[3] == pytest.approx(3.0)
    assert fy0[4] == pytest.approx(3.0)
    assert fy0[9] == 3
    assert fy0[10] == 2


def test_nan_and_zero_year_slots_dropped():
    """EPS NaN/槽位年 0 的槽位丢弃，不成行。"""
    reports = [_rep("600519", "2026-08-01", fy0=0, eps0=float("nan"))]
    rows = _mod.build_consensus_rows(reports, [date(2026, 8, 12)], window_days=90)
    fy0_rows = [r for r in rows if r[0] == "2026-08-12"]
    assert fy0_rows == [], "无有效槽位→无行（禁前向填充）"


def test_rating_score_map():
    assert _mod.rating_score("买入") == 7
    assert _mod.rating_score("持有") == 3
    assert _mod.rating_score("卖出") == 1
    assert _mod.rating_score("") is None
    assert _mod.rating_score("未知评级") is None
