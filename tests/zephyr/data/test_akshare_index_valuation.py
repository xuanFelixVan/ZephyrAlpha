# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] tests.zephyr.data.test_akshare_index_valuation
# [DEPENDENCIES] zephyr.data.implementations.akshare_provider
# [CONSUMERS] none
# [STARTUP] pytest
# [MATURITY] production
# [INVARIANTS] mock akshare，不触网不触库；pytest filterwarnings=error 兼容
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 测试失败=akshare 指数估值采集逻辑缺陷
# [TESTS] 本文件
# [A_module] module_id=MOD-DAT-akshare_ingest | layer=test | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""akshare_provider 指数估值采集能力单元测试（S2 路A 管道，2026-08-28）。

覆盖：
- _fetch_index_valuation_daily 正常映射（中证官网历史K线 → PE_TTM/股息率）
- 全历史回填模式（incremental=False → start=2010-01-01）
- 空输入/失败路径降级
- capability 路由一致性
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


def _payload(start: D, end: D, extra: dict | None = None, symbols=None, incremental=True) -> FetchPayload:
    return FetchPayload(
        table="",
        symbols=symbols,
        start=start,
        end=end,
        incremental=incremental,
        extra=extra or {},
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


class TestIndexValuationDailyFetch:
    """index_valuation_daily 采集能力测试（S2 路A 主源）。"""

    def test_normal_mapping(self, monkeypatch):
        """正常行：中证官网历史K线 → PE_TTM/股息率映射。"""
        df = pd.DataFrame({
            "日期": [D(2026, 8, 27), D(2026, 8, 28)],
            "指数代码": ["000300", "000300"],
            "收盘": [4630.28, 4609.18],
            "滚动市盈率": [14.44, 14.42],
            "股息率1": [2.52, 2.52],
        })
        _mock_ak(monkeypatch, stock_zh_index_hist_csindex=df)
        provider = AkshareIngestProvider()
        results = _call_fetch(
            provider,
            "index_valuation_daily",
            _payload(D(2026, 8, 27), D(2026, 8, 28), symbols=["000300"]),
        )
        assert len(results) == 1
        assert results[0].error is None
        rows = results[0].rows
        assert len(rows) == 2
        # 列顺序：trade_date/symbol/pe_ttm/pb_mrq/dividend_yield/cape_5y/cape_5y_pct/pe_pct/pb_pct/erp/erp_pct/broken_net_ratio/buffett_ratio/data_source
        assert rows[0][0] == "2026-08-27"  # trade_date
        assert rows[0][1] == "000300"  # symbol
        assert rows[0][2] == 14.44  # pe_ttm
        assert rows[0][3] is None  # pb_mrq（一期暂缺）
        assert rows[0][4] == 2.52  # dividend_yield
        assert rows[0][13] == "akshare_csindex"  # data_source

    def test_full_refresh_start_2010(self, monkeypatch):
        """全量回填模式：incremental=False → start=2010-01-01。"""
        df = pd.DataFrame({
            "日期": [D(2010, 1, 4), D(2010, 1, 5)],
            "指数代码": ["000300", "000300"],
            "收盘": [3535.23, 3564.04],
            "滚动市盈率": [None, 15.0],
            "股息率1": [None, 2.0],
        })
        mock_ak = _mock_ak(monkeypatch, stock_zh_index_hist_csindex=df)
        provider = AkshareIngestProvider()
        results = _call_fetch(
            provider,
            "index_valuation_daily",
            _payload(D(2026, 8, 27), D(2026, 8, 28), symbols=["000300"], incremental=False),
        )
        assert len(results) == 1
        # 验证调用参数 start_date="20100101"
        call_kwargs = mock_ak.stock_zh_index_hist_csindex.call_args
        assert call_kwargs is not None
        assert call_kwargs[1]["start_date"] == "20100101"

    def test_empty_input(self, monkeypatch):
        """空输入：akshare 返回空 DataFrame → 空 rows + error 留痕，不抛错。"""
        _mock_ak(monkeypatch, stock_zh_index_hist_csindex=pd.DataFrame())
        provider = AkshareIngestProvider()
        results = _call_fetch(
            provider,
            "index_valuation_daily",
            _payload(D(2026, 8, 27), D(2026, 8, 28), symbols=["000300"]),
        )
        assert len(results) == 1
        assert results[0].rows == []
        assert results[0].error is not None  # 空数据留痕
        assert "000300" in results[0].error

    def test_akshare_failure(self, monkeypatch):
        """akshare 异常 → FetchResult(error=...) 不抛出。"""
        _mock_ak(monkeypatch, stock_zh_index_hist_csindex=RuntimeError("网络超时"))
        provider = AkshareIngestProvider()
        results = _call_fetch(
            provider,
            "index_valuation_daily",
            _payload(D(2026, 8, 27), D(2026, 8, 28), symbols=["000300"]),
        )
        assert len(results) == 1
        assert results[0].error is not None
        assert "000300" in results[0].error

    def test_default_symbols(self, monkeypatch):
        """symbols=None → 默认核心指数（000300/000905/399006）。"""
        df = pd.DataFrame({
            "日期": [D(2026, 8, 28)],
            "指数代码": ["000300"],
            "收盘": [4609.18],
            "滚动市盈率": [14.42],
            "股息率1": [2.52],
        })
        mock_ak = _mock_ak(monkeypatch, stock_zh_index_hist_csindex=df)
        provider = AkshareIngestProvider()
        results = _call_fetch(
            provider,
            "index_valuation_daily",
            _payload(D(2026, 8, 28), D(2026, 8, 28), symbols=None),
        )
        # 3 只指数各 yield 一次（含空结果）
        assert len(results) >= 1
        # 验证调用了 3 次（000300/000905/399006）
        assert mock_ak.stock_zh_index_hist_csindex.call_count == 3
