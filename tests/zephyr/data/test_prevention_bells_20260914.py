# -*- coding: utf-8 -*-
"""2026-09-14 防复发三件套单测：920 宇宙并集 / ch_writer 列缓存失效 / DDL 前置校验+日线看门铃。

背景（缺口报告 v2 §七）：
  1. miniqmt kline 车道 sector 仅沪深A股 → 北交所 920 新段缺失静默降级 4 天；
  2. ch_writer 表列缓存改版后不失效 → news_data 死信；
  3. alt_sz 九表数据先行无告警 → local_fallback 积压。
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from zephyr.data import ch_writer
from zephyr.data.implementations.miniqmt_provider import MiniQmtIngestProvider


# ============ 1. 920 宇宙：多板块并集 ============

def _bare_provider() -> MiniQmtIngestProvider:
    """绕过 __init__ 构造最小实例（仅挂 log）。"""
    p = MiniQmtIngestProvider.__new__(MiniQmtIngestProvider)
    p._log = MagicMock()
    return p


def test_kline_capabilities_include_bj_sector():
    """A股 K 线各周期 capability 必须含京市A股板块（920 新段覆盖）。"""
    from zephyr.data.implementations.miniqmt_provider import _KLINE_CAPABILITIES

    for cap in ("kline_daily", "kline_1min", "kline_5min", "kline_15min",
                "kline_30min", "kline_60min"):
        period, sector = _KLINE_CAPABILITIES[cap]
        assert isinstance(sector, tuple), f"{cap} sector 应为多板块元组"
        assert "沪深A股" in sector and "京市A股" in sector, f"{cap} 缺北交所板块: {sector}"


def test_collect_sector_symbols_union_dedup_preserve_order():
    """多板块并集：保序去重，沪深+京市合并。"""
    p = _bare_provider()
    canned = {
        "沪深A股": ["000001.SZ", "600519.SH", "000001.SZ"],
        "京市A股": ["920001.BJ", "830001.BJ", "920001.BJ"],
    }

    def fake_call(policy, fn, sector):
        return list(canned[sector])

    p._call_with_policy = fake_call
    got = p._collect_sector_symbols(policy=None, sector=("沪深A股", "京市A股"))
    assert got == ["000001.SZ", "600519.SH", "920001.BJ", "830001.BJ"]
    assert any(s.startswith("92") for s in got), "京市 920 段必须进宇宙"


def test_collect_sector_symbols_single_sector_compat():
    """单板块字符串入参向后兼容。"""
    p = _bare_provider()

    def fake_call(policy, fn, sector):
        assert sector == "沪深ETF"
        return ["510300.SH"]

    p._call_with_policy = fake_call
    assert p._collect_sector_symbols(policy=None, sector="沪深ETF") == ["510300.SH"]


# ============ 2. ch_writer 列缓存失效 ============

def test_invalidate_table_schema_cache_clears_both():
    """失效函数必须同时清 table_cols_cache 与 table_insertable_cols_cache。"""
    ch_writer.table_cols_cache["c1_market.t1"] = {"a"}
    ch_writer.table_insertable_cols_cache["c1_market.t1"] = {"a"}
    ch_writer.invalidate_table_schema_cache("c1_market.t1")
    assert "c1_market.t1" not in ch_writer.table_cols_cache
    assert "c1_market.t1" not in ch_writer.table_insertable_cols_cache


def test_write_tsv_outcome_http_fail_invalidates_cache(monkeypatch):
    """HTTP 插入失败路径必须触发列缓存失效（news_data 死信根因防线）。"""
    ch_writer.table_cols_cache["c1_market.t2"] = {"a"}
    monkeypatch.setattr(ch_writer, "http_insert", lambda *a, **k: False)
    monkeypatch.setattr(
        ch_writer, "save_fallback", lambda *a, **k: True
    ) if hasattr(ch_writer, "save_fallback") else None
    # create_fallback=False 走 no-fallback 分支（不依赖 local_replay）
    out = ch_writer.write_tsv_outcome(
        "c1_market.t2", "(a)", b"1\n", create_fallback=False)
    assert out.disposition is not None
    assert "c1_market.t2" not in ch_writer.table_cols_cache


# ============ 3. DDL 前置校验 + 日线看门铃 ============

class _FakeScheduler:
    """只挂被测依赖的最小 scheduler 替身。"""

    def __init__(self):
        self._alerter = MagicMock()
        self._warn_if_table_missing = IntegratorSchedulerMixin._warn_if_table_missing.__get__(self)
        self.verify_daily_kline_coverage = (
            IntegratorSchedulerMixin.verify_daily_kline_coverage.__get__(self)
        )


from zephyr.data import scheduler as sched_mod

IntegratorSchedulerMixin = sched_mod.IntegratorScheduler


def test_warn_if_table_missing_alerts_once(monkeypatch):
    """表缺失→告警一次，4h 内去重；表存在→不告警并清去重账。"""
    fs = _FakeScheduler()
    monkeypatch.setattr(sched_mod, "_MISSING_TABLE_ALERT_TS", {})
    monkeypatch.setattr("zephyr.data.ch_writer.query", lambda *a, **k: "0\n")

    fs._warn_if_table_missing("c1_market.na_tbl")
    assert fs._alerter.notify.call_count == 1

    fs._warn_if_table_missing("c1_market.na_tbl")
    assert fs._alerter.notify.call_count == 1, "4h 去重窗口内不得重复告警"

    monkeypatch.setattr("zephyr.data.ch_writer.query", lambda *a, **k: "3\n")
    fs._warn_if_table_missing("c1_market.na_tbl")
    assert fs._alerter.notify.call_count == 1, "表存在后不再告警"


def test_coverage_bell_fires_on_deviation(monkeypatch):
    """当日标的数 vs 近5日中位数偏差>1% → 告警。"""
    fs = _FakeScheduler()
    rows = [
        ("d1", 5550), ("d2", 5549), ("d3", 5549), ("d4", 5550), ("d5", 5549),
        ("d6", 5207),  # 当日静默降级 6%
    ]
    tsv = "\n".join(f"{d}\t{n}" for d, n in rows)
    monkeypatch.setattr("zephyr.data.ch_writer.query", lambda *a, **k: tsv)

    result = fs.verify_daily_kline_coverage()
    assert result["ok"] is False
    assert result["count"] == 5207
    assert fs._alerter.notify.call_count == 1
    assert "疑似标的宇宙缺口" in fs._alerter.notify.call_args.args[1]


def test_coverage_bell_quiet_within_tolerance(monkeypatch):
    """偏差在容差内 → 不告警。"""
    fs = _FakeScheduler()
    rows = [
        ("d1", 5550), ("d2", 5549), ("d3", 5550), ("d4", 5549), ("d5", 5550),
        ("d6", 5549),
    ]
    tsv = "\n".join(f"{d}\t{n}" for d, n in rows)
    monkeypatch.setattr("zephyr.data.ch_writer.query", lambda *a, **k: tsv)

    result = fs.verify_daily_kline_coverage()
    assert result["ok"] is True
    assert fs._alerter.notify.call_count == 0
