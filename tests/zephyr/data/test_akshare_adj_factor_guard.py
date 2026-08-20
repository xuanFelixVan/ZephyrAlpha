# [ALGO_FLOW] #209② adj_factor 写侧守卫测试：miniqmt 已覆盖键查询→解析→逐行跳过
# [ALGO_FLOW] 守卫 fail-open（CH 查询失败/异常→空集不阻塞 fallback 写入）
# [ALGO_FLOW] 自定义目标表（非共享 adj_factor 表）跳过守卫查询
# [MODULE] tests.zephyr.data.test_akshare_adj_factor_guard
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.implementations.akshare_provider
# [TESTS] 本文件
# [TTL] permanent
"""#209② adj_factor 写侧守卫单元测试（不触网不触库，akshare/ch_reader 全 mock）。

背景：adj_factor 表 ReplacingMergeTree(ingest_ts) ORDER BY (symbol, trade_date)
不含 data_source——akshare hfq fallback 与 miniqmt dr 同键写入时后写静默替换
先写。守卫：写共享表前查 miniqmt 已覆盖 (symbol, trade_date) 键并跳过。
"""
from __future__ import annotations

import datetime
import sys
from unittest.mock import MagicMock

import pandas as pd
import pytest

from src.zephyr.data.implementations.akshare_provider import (
    AkshareIngestProvider,
)
from src.zephyr.data.provider_base import FetchPayload

D = datetime.date


def _payload(start: D, end: D, symbols=None, table: str = "") -> FetchPayload:
    return FetchPayload(
        table=table,
        symbols=symbols,
        start=start,
        end=end,
        incremental=False,
        extra={},
    )


def _mock_ak(monkeypatch, **attrs) -> MagicMock:
    mock_ak = MagicMock()
    for name, val in attrs.items():
        child = getattr(mock_ak, name)
        child.__name__ = name
        if isinstance(val, Exception) or callable(val):
            child.side_effect = val
        else:
            child.return_value = val
    monkeypatch.setitem(sys.modules, "akshare", mock_ak)
    return mock_ak


def _call_fetch(provider, payload: FetchPayload) -> list:
    payload.extra = {**(payload.extra or {}), "capability": "adj_factor"}
    policy = MagicMock(rpm=0, max_retries=1, backoff="fixed", initial_wait=0)
    return list(provider.fetch(payload, policy))


class TestCoveredMiniqmtAdjKeys:
    """守卫键查询 helper：TSV 解析 + fail-open 契约。"""

    def test_parses_tsv_keys(self, monkeypatch):
        import zephyr.data.ch_reader as chr_mod

        monkeypatch.setattr(
            chr_mod, "query",
            lambda sql, timeout=None: "600519\t2026-07-05\n000002\t2026-07-06\n",
        )
        p = AkshareIngestProvider()
        covered = p._covered_miniqmt_adj_keys(["600519", "000002"], "2026-07-01", "2026-07-10")
        assert covered == {("600519", "2026-07-05"), ("000002", "2026-07-06")}

    def test_query_exception_returns_empty(self, monkeypatch):
        """CH 查询异常 → fail-open 空集（不阻塞 fallback 写入）。"""
        import zephyr.data.ch_reader as chr_mod

        def _boom(sql, timeout=None):
            raise ConnectionError("CH unreachable")

        monkeypatch.setattr(chr_mod, "query", _boom)
        p = AkshareIngestProvider()
        assert p._covered_miniqmt_adj_keys(["600519"], "2026-07-01", "2026-07-10") == set()

    def test_query_empty_tsv_returns_empty(self, monkeypatch):
        """CH 故障静默返回空串 → 空集。"""
        import zephyr.data.ch_reader as chr_mod

        monkeypatch.setattr(chr_mod, "query", lambda sql, timeout=None: "")
        p = AkshareIngestProvider()
        assert p._covered_miniqmt_adj_keys(["600519"], "2026-07-01", "2026-07-10") == set()

    def test_malformed_lines_skipped(self, monkeypatch):
        import zephyr.data.ch_reader as chr_mod

        monkeypatch.setattr(
            chr_mod, "query",
            lambda sql, timeout=None: "600519\t2026-07-05\nBROKENLINE\n\t2026-07-06\n",
        )
        p = AkshareIngestProvider()
        assert p._covered_miniqmt_adj_keys(["600519"], "2026-07-01", "2026-07-10") == {
            ("600519", "2026-07-05")
        }

    def test_empty_codes_no_query(self, monkeypatch):
        import zephyr.data.ch_reader as chr_mod

        def _boom(sql, timeout=None):
            raise AssertionError("空 codes 不应发起 CH 查询")

        monkeypatch.setattr(chr_mod, "query", _boom)
        p = AkshareIngestProvider()
        assert p._covered_miniqmt_adj_keys([], "2026-07-01", "2026-07-10") == set()


class TestAdjFactorGuardFetch:
    """fetch 级：覆盖键跳过 / fail-open / 自定义表跳过守卫。"""

    def _df(self):
        return pd.DataFrame(
            {
                "date": [D(2026, 7, 5), D(2026, 7, 10)],
                "hfq_factor": [1.05, 1.06],
            }
        )

    def test_covered_key_rows_skipped(self, monkeypatch):
        """miniqmt 已覆盖 (600519, 2026-07-05) → 该键 akshare 行被跳过，其余保留。"""
        _mock_ak(monkeypatch, stock_zh_a_daily=self._df())
        monkeypatch.setattr(
            AkshareIngestProvider,
            "_covered_miniqmt_adj_keys",
            lambda self, codes, s, e: {("600519", "2026-07-05")},
        )
        provider = AkshareIngestProvider()
        results = _call_fetch(provider, _payload(D(2026, 7, 1), D(2026, 7, 10), symbols=["600519.SH"]))
        assert len(results) == 1
        rows = results[0].rows
        assert len(rows) == 1
        assert rows[0][0] == "2026-07-10"
        assert rows[0][3] == "akshare"

    def test_all_covered_yields_zero_rows(self, monkeypatch):
        """全部键已被 miniqmt 覆盖 → 0 行（fallback 完全不写，防静默替换）。"""
        _mock_ak(monkeypatch, stock_zh_a_daily=self._df())
        monkeypatch.setattr(
            AkshareIngestProvider,
            "_covered_miniqmt_adj_keys",
            lambda self, codes, s, e: {("600519", "2026-07-05"), ("600519", "2026-07-10")},
        )
        provider = AkshareIngestProvider()
        results = _call_fetch(provider, _payload(D(2026, 7, 1), D(2026, 7, 10), symbols=["600519.SH"]))
        assert results[-1].rows == []

    def test_custom_table_skips_guard(self, monkeypatch):
        """payload.table 指向非共享表 → 不触发守卫查询（无 ReplacingMergeTree 同键冲突）。"""
        _mock_ak(monkeypatch, stock_zh_a_daily=self._df())

        def _boom(self, codes, s, e):
            raise AssertionError("自定义表不应触发守卫查询")

        monkeypatch.setattr(AkshareIngestProvider, "_covered_miniqmt_adj_keys", _boom)
        provider = AkshareIngestProvider()
        results = _call_fetch(
            provider,
            _payload(D(2026, 7, 1), D(2026, 7, 10), symbols=["600519.SH"], table="c1_market.adj_factor_tmp"),
        )
        assert len(results[0].rows) == 2
