# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] tests.zephyr.data.test_index_constituent_scd2
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.implementations.akshare_provider
# [CONSUMERS] none
# [STARTUP] pytest
# [MATURITY] production
# [INVARIANTS] mock akshare/ch_reader，不触网不触库；pytest filterwarnings=error 兼容
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 测试失败=GAP-B3-03 SCD-2 闭旧开新逻辑缺陷
# [TESTS] 本文件
# [A_module] module_id=MOD-DAT-akshare_ingest | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""GAP-B3-03 指数成分日快照 SCD-2 闭旧开新（#ARCH-DATA-015/#ARCH-CH-021）单元测试。

缺陷（BTDATA_report §B3 实证 @2026-08-20）：index_member_premarket/postclose 日快照
每日新开版本写入 c1_market.index_constituent，旧版本 valid_to 恒 NULL 从不闭合
→ 同一 (index_code, symbol) 多版本并存（000300.SH @2026-08-20 返回 5 版本×300=1,500 行）。

修复口径（同构 #209④ stock_list 闭旧先例）：新快照写入前查 CH 该指数 open 版本
（valid_to IS NULL 且 trade_date < 新快照生效日），逐行产出同键闭合行
（valid_to=新快照生效日，对齐 pit_query "valid_to > qt=有效" 语义）；
新行不携 valid_to（NULL=开新）。同日盘前/盘后重跑互不闭合；闭旧失败不阻断开新。
全部 mock akshare 与 ch_reader，不触网不触库。
"""

from __future__ import annotations

import datetime
import re
import sys
from unittest.mock import MagicMock

import pandas as pd
import pytest

from src.zephyr.data.implementations.akshare_provider import (
    AkshareIngestProvider,
)
from src.zephyr.data.provider_base import FetchPayload

D = datetime.date  # 简写

_BASE_COLUMNS = ["trade_date", "index_code", "symbol", "weight", "action", "data_source"]


def _payload(start: D, end: D) -> FetchPayload:
    return FetchPayload(
        table="",
        symbols=None,
        start=start,
        end=end,
        incremental=True,
        extra={},
    )


def _cons_df(day: str, codes: list[str]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "日期": [day] * len(codes),
            "指数代码": ["000300"] * len(codes),
            "指数名称": ["X"] * len(codes),
            "成分券代码": codes,
            "成分券名称": ["名"] * len(codes),
            "交易所": ["深圳证券交易所"] * len(codes),
        }
    )


def _mock_ak(monkeypatch, cons_df: pd.DataFrame) -> MagicMock:
    mock_ak = MagicMock()
    mock_ak.index_stock_cons_csindex = MagicMock(return_value=cons_df)
    mock_ak.index_stock_cons_csindex.__name__ = "index_stock_cons_csindex"
    mock_ak.index_stock_cons_weight_csindex = MagicMock(return_value=pd.DataFrame())
    mock_ak.index_stock_cons_weight_csindex.__name__ = "index_stock_cons_weight_csindex"
    monkeypatch.setitem(sys.modules, "akshare", mock_ak)
    return mock_ak


def _patch_provider_ch(monkeypatch, fake_query):
    """patch provider 侧命名空间的 ch_reader.query（不触真实 ClickHouse）。"""
    import zephyr.data.ch_reader as provider_ch_reader

    monkeypatch.setattr(provider_ch_reader, "query", fake_query)


def _call_fetch(provider, payload: FetchPayload) -> list:
    payload.extra = {**(payload.extra or {}), "capability": "index_constituent"}
    policy = MagicMock(rpm=0, max_retries=1, backoff="fixed", initial_wait=0)
    return list(provider.fetch(payload, policy))


class _ConstituentStore:
    """内存 ReplacingMergeTree 仿真：key=(index_code, trade_date, symbol)，同键后写覆盖。

    query(sql) 模拟 ch_reader 对 open 版本的 SELECT（解析 WHERE 中
    index_code/trade_date < toDate(...) 过滤），供两版本连续写入场景复现 SCD-2 语义。
    """

    def __init__(self) -> None:
        self.rows: dict[tuple[str, str, str], dict] = {}

    def query(self, sql: str, timeout: int = 0) -> str:
        m_idx = re.search(r"index_code = '([^']+)'", sql)
        m_dt = re.search(r"trade_date < toDate\('([^']+)'\)", sql)
        assert m_idx and m_dt, f"非预期 SQL: {sql}"
        index_code, as_of = m_idx.group(1), m_dt.group(1)
        out = []
        for (idx, td, sym), r in sorted(self.rows.items()):
            if idx == index_code and r["valid_to"] is None and td < as_of:
                out.append(f"{td}\t{sym}\t{r['weight']}\t{r['action']}\t{r['data_source']}")
        return "\n".join(out) + ("\n" if out else "")

    def apply(self, result) -> None:
        cols = list(result.columns)
        for row in result.rows:
            rec = dict(zip(cols, row))
            key = (rec["index_code"], rec["trade_date"], rec["symbol"])
            rec.setdefault("valid_to", None)
            self.rows[key] = rec

    def open_versions(self, index_code: str, symbol: str) -> list[dict]:
        return [
            r
            for (idx, _td, sym), r in self.rows.items()
            if idx == index_code and sym == symbol and r["valid_to"] is None
        ]


# ============== 闭旧行产出 ==============


class TestClosureRows:
    def test_new_snapshot_closes_old_open_versions(self, monkeypatch):
        """新快照到达：旧 open 版本产出同键闭合行（valid_to=新快照生效日），新行不携 valid_to。"""
        _mock_ak(monkeypatch, _cons_df("2026-08-17", ["000001", "600000"]))
        captured_sql: list[str] = []

        def fake_query(sql: str, timeout: int = 0) -> str:
            captured_sql.append(sql)
            if "000300.SH" in sql:
                # CH 侧 @2026-08-14 旧快照两行 open（valid_to IS NULL）
                return (
                    "2026-08-14\t000001.SZ\t0.4330\t\takshare_csindex\n"
                    "2026-08-14\t600000.SH\t1.2340\t\takshare_csindex\n"
                )
            return ""

        _patch_provider_ch(monkeypatch, fake_query)
        p = AkshareIngestProvider()
        results = _call_fetch(p, _payload(D(2026, 8, 17), D(2026, 8, 17)))

        # 000300.SH：先闭旧批后开新批；其余四指数无 open 旧版本仅开新批
        assert len(results) == 6
        closure, new_batch = results[0], results[1]
        assert closure.error is None
        assert closure.columns == [*_BASE_COLUMNS, "valid_to"]
        assert closure.rows == [
            ("2026-08-14", "000300.SH", "000001.SZ", "0.4330", "", "akshare_csindex", "2026-08-17"),
            ("2026-08-14", "000300.SH", "600000.SH", "1.2340", "", "akshare_csindex", "2026-08-17"),
        ]
        assert new_batch.error is None
        assert new_batch.columns == _BASE_COLUMNS  # 新行不携 valid_to（NULL=开新）
        assert all(row[0] == "2026-08-17" for row in new_batch.rows)
        # 闭旧查询口径：仅 open 且早于新快照生效日（同日/未来版本不闭合）
        assert any("valid_to IS NULL" in s and "trade_date < toDate('2026-08-17')" in s for s in captured_sql)

    def test_two_sequential_snapshots_single_open_version(self, monkeypatch):
        """复现口径：连续两版本写入后，旧版本 valid_to 已闭合且每标的仅一行 open。"""
        store = _ConstituentStore()
        _patch_provider_ch(monkeypatch, store.query)
        p = AkshareIngestProvider()

        # 第一版 @2026-08-14（库空 → 无闭旧，纯开新）
        _mock_ak(monkeypatch, _cons_df("2026-08-14", ["000001"]))
        for r in _call_fetch(p, _payload(D(2026, 8, 14), D(2026, 8, 14))):
            assert not r.error
            store.apply(r)
        assert len(store.open_versions("000300.SH", "000001.SZ")) == 1

        # 第二版 @2026-08-17（闭旧开新）
        _mock_ak(monkeypatch, _cons_df("2026-08-17", ["000001"]))
        for r in _call_fetch(p, _payload(D(2026, 8, 17), D(2026, 8, 17))):
            assert not r.error
            store.apply(r)

        old = store.rows[("000300.SH", "2026-08-14", "000001.SZ")]
        new = store.rows[("000300.SH", "2026-08-17", "000001.SZ")]
        assert old["valid_to"] == "2026-08-17"  # 旧版本已闭合
        assert new["valid_to"] is None  # 新版本 open
        assert len(store.open_versions("000300.SH", "000001.SZ")) == 1  # 仅一行 open

    def test_same_day_rerun_no_closure(self, monkeypatch):
        """同日盘前/盘后重跑：trade_date 相同不满足 < 新快照生效日，互不闭合。"""
        store = _ConstituentStore()
        _patch_provider_ch(monkeypatch, store.query)
        p = AkshareIngestProvider()
        _mock_ak(monkeypatch, _cons_df("2026-08-17", ["000001"]))
        for r in _call_fetch(p, _payload(D(2026, 8, 17), D(2026, 8, 17))):
            store.apply(r)
        # 同日重跑
        results = _call_fetch(p, _payload(D(2026, 8, 17), D(2026, 8, 17)))
        assert all("valid_to" not in r.columns for r in results)  # 无闭旧批
        for r in results:
            store.apply(r)
        assert len(store.open_versions("000300.SH", "000001.SZ")) == 1


# ============== 护栏 ==============


class TestClosureGuards:
    def test_empty_snapshot_no_closure(self, monkeypatch):
        """新快照为空（接口空 DataFrame）→ 不闭旧（无可接续版本，旧版本维持 open）。"""
        _mock_ak(monkeypatch, pd.DataFrame())
        called: list[str] = []

        def fake_query(sql: str, timeout: int = 0) -> str:
            called.append(sql)
            return "2026-08-14\t000001.SZ\t0.4330\t\takshare_csindex\n"

        _patch_provider_ch(monkeypatch, fake_query)
        p = AkshareIngestProvider()
        results = _call_fetch(p, _payload(D(2026, 8, 17), D(2026, 8, 17)))
        assert len(results) == 5
        assert all(not r.error and r.rows == [] for r in results)
        assert all("valid_to" not in r.columns for r in results)
        assert called == []  # 空快照连 open 查询都不应发起

    def test_closure_query_failure_keeps_new_rows(self, monkeypatch):
        """open 版本查询异常 → 跳过闭旧不阻断开新（新行照常产出且无 error）。"""
        _mock_ak(monkeypatch, _cons_df("2026-08-17", ["000001"]))

        def boom(sql: str, timeout: int = 0) -> str:
            raise ConnectionError("CH down")

        _patch_provider_ch(monkeypatch, boom)
        p = AkshareIngestProvider()
        results = _call_fetch(p, _payload(D(2026, 8, 17), D(2026, 8, 17)))
        assert len(results) == 5
        assert all(not r.error for r in results)
        assert all("valid_to" not in r.columns for r in results)
        assert results[0].rows[0][:2] == ("2026-08-17", "000300.SH")
