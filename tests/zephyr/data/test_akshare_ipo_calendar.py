# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] tests.zephyr.data.test_akshare_ipo_calendar
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.implementations.akshare_provider
# [CONSUMERS] none
# [STARTUP] pytest
# [MATURITY] production
# [INVARIANTS] mock akshare，不触网不触库；pytest filterwarnings=error 兼容
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 测试失败=ipo_calendar 能力逻辑缺陷
# [TESTS] 本文件
# [A_module] module_id=MOD-DAT-akshare_ingest | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""ipo_calendar 能力单元测试（tracker #114 / 37号 §3.2a，DS-105）。

覆盖：正常字段映射与单位派生（万股→股、募资亿元）/ NaT+NaN 防御（未定档
list_date=None、未定价 raise_amount=None）/ 代码防御（非法代码跳过）/
源失败容错（异常→空结果不抛出）/ PIT 快照锚定（trade_date=payload.end）。
全部 mock akshare，不触网不触库。
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

D = datetime.date  # 简写


def _payload(start: D, end: D, extra: dict | None = None) -> FetchPayload:
    return FetchPayload(
        table="", symbols=None, start=start, end=end,
        incremental=False, extra=extra or {},
    )


def _mock_ak(monkeypatch, **attrs) -> MagicMock:
    """构造 akshare 模块 mock（绕过真实 SDK 的 pkg_resources 警告）。"""
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


def _call_fetch(provider, cap: str, payload: FetchPayload) -> list:
    """调用 provider.fetch 路由并收集全部 FetchResult。"""
    payload.extra = {**(payload.extra or {}), "capability": cap}
    policy = MagicMock(rpm=0, max_retries=1, backoff="fixed", initial_wait=0)
    return list(provider.fetch(payload, policy))


def _ipo_df(rows: list[dict]) -> pd.DataFrame:
    """构造 stock_new_ipo_cninfo 形态 DataFrame。"""
    return pd.DataFrame(rows)


class TestIpoCalendarFetch:
    def test_normal_mapping_and_unit_derivation(self, monkeypatch):
        """正常行：字段映射 + 万股→股 + 募资规模（亿元）派生口径。"""
        df = _ipo_df([
            {
                "证劵代码": "688825", "证券简称": "长鑫科技",
                "上市日期": datetime.date(2026, 7, 27),
                "申购日期": datetime.date(2026, 7, 17),
                "发行价": 90.0, "总发行数量": 74000.0,  # 万股
                "发行市盈率": 45.5,
            },
        ])
        _mock_ak(monkeypatch, stock_new_ipo_cninfo=df)
        provider = AkshareIngestProvider()
        results = _call_fetch(provider, "ipo_calendar", _payload(D(2026, 7, 20), D(2026, 7, 20)))

        assert len(results) == 1
        res = results[0]
        assert res.table == "c1_market.ipo_calendar"
        assert res.error is None
        assert len(res.rows) == 1
        r = res.rows[0]
        assert r[0] == "2026-07-20"          # trade_date = payload.end（PIT 快照锚）
        assert r[1] == "688825"              # symbol
        assert r[2] == "长鑫科技"             # name
        assert r[3] == "2026-07-27"          # list_date
        assert r[4] == "2026-07-17"          # subscribe_date
        assert r[5] == 90.0                  # issue_price
        assert r[6] == 740000000             # total_shares（万股×1e4→股）
        # raise_amount = 90 × 74000万 / 10000 = 666.0 亿元（37号 §3.2a 长鑫实证口径）
        assert r[7] == pytest.approx(666.0)
        assert r[8] == 45.5                  # pe_ratio
        assert r[9] == "akshare_cninfo"      # data_source

    def test_nat_nan_defense(self, monkeypatch):
        """未定档（list_date=NaT）+ 未定价（发行价 NaN）→ None，不炸不脏库。"""
        df = _ipo_df([
            {
                "证劵代码": "301688", "证券简称": "格林生物",
                "上市日期": pd.NaT,
                "申购日期": datetime.date(2026, 8, 20),
                "发行价": float("nan"), "总发行数量": 3333.3334,
                "发行市盈率": float("nan"),
            },
        ])
        _mock_ak(monkeypatch, stock_new_ipo_cninfo=df)
        provider = AkshareIngestProvider()
        results = _call_fetch(provider, "ipo_calendar", _payload(D(2026, 8, 17), D(2026, 8, 17)))

        assert len(results) == 1
        r = results[0].rows[0]
        assert r[1] == "301688"
        assert r[3] is None                   # list_date NaT→None（未定档）
        assert r[4] == "2026-08-20"           # subscribe_date 正常
        assert r[5] is None                   # issue_price NaN→None（未定价）
        assert r[6] == 33333334               # total_shares 仍可派生
        assert r[7] is None                   # raise_amount 未定价→None
        assert r[8] is None                   # pe_ratio NaN→None

    def test_invalid_code_skipped(self, monkeypatch):
        """非法代码（空/非数字/超长）跳过，合法行保留。"""
        df = _ipo_df([
            {"证劵代码": "", "证券简称": "空码", "上市日期": pd.NaT,
             "申购日期": pd.NaT, "发行价": 1.0, "总发行数量": 100.0, "发行市盈率": 1.0},
            {"证劵代码": "ABC123", "证券简称": "非数字", "上市日期": pd.NaT,
             "申购日期": pd.NaT, "发行价": 1.0, "总发行数量": 100.0, "发行市盈率": 1.0},
            {"证劵代码": "12345678", "证券简称": "超长", "上市日期": pd.NaT,
             "申购日期": pd.NaT, "发行价": 1.0, "总发行数量": 100.0, "发行市盈率": 1.0},
            {"证劵代码": "600000", "证券简称": "浦发银行", "上市日期": datetime.date(1999, 11, 10),
             "申购日期": pd.NaT, "发行价": 10.0, "总发行数量": 40000.0, "发行市盈率": 20.0},
        ])
        _mock_ak(monkeypatch, stock_new_ipo_cninfo=df)
        provider = AkshareIngestProvider()
        results = _call_fetch(provider, "ipo_calendar", _payload(D(2026, 8, 17), D(2026, 8, 17)))

        rows = results[0].rows
        assert len(rows) == 1
        assert rows[0][1] == "600000"

    def test_source_failure_yields_empty_not_raise(self, monkeypatch):
        """源异常 → yield 空 rows FetchResult（error=None），不向上抛出。"""
        _mock_ak(monkeypatch, stock_new_ipo_cninfo=ConnectionError("cninfo 不可达"))
        provider = AkshareIngestProvider()
        results = _call_fetch(provider, "ipo_calendar", _payload(D(2026, 8, 17), D(2026, 8, 17)))

        assert len(results) == 1
        assert results[0].rows == []
        assert results[0].error is None

    def test_empty_source_yields_empty(self, monkeypatch):
        """源返回空 DataFrame → 空结果。"""
        _mock_ak(monkeypatch, stock_new_ipo_cninfo=pd.DataFrame())
        provider = AkshareIngestProvider()
        results = _call_fetch(provider, "ipo_calendar", _payload(D(2026, 8, 17), D(2026, 8, 17)))

        assert len(results) == 1
        assert results[0].rows == []

    def test_trade_date_defaults_today(self, monkeypatch):
        """payload.end=None 时 trade_date 锚定今日（快照语义）。"""
        df = _ipo_df([
            {"证劵代码": "600000", "证券简称": "浦发银行",
             "上市日期": datetime.date(1999, 11, 10), "申购日期": pd.NaT,
             "发行价": 10.0, "总发行数量": 40000.0, "发行市盈率": 20.0},
        ])
        _mock_ak(monkeypatch, stock_new_ipo_cninfo=df)
        provider = AkshareIngestProvider()
        payload = _payload(D(2026, 8, 17), D(2026, 8, 17))
        payload.end = None
        results = _call_fetch(provider, "ipo_calendar", payload)

        assert results[0].rows[0][0] == D.today().isoformat()

    def test_capability_routing_and_contract(self, monkeypatch):
        """路由：ipo_calendar 在 akshare 路由集与 meta 契约内（capability_validator 一致性）。"""
        from src.zephyr.data.implementations import akshare_provider as akp

        provider = AkshareIngestProvider()
        assert "ipo_calendar" in akp._AKSHARE_CAPABILITIES
        caps = {c.capability_id for c in provider.meta.capabilities}
        assert "ipo_calendar" in caps
