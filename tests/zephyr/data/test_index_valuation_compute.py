# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] tests.zephyr.data.test_index_valuation_compute
# [DEPENDENCIES] zephyr.data.implementations.index_valuation_compute
# [CONSUMERS] none
# [STARTUP] pytest
# [MATURITY] production
# [INVARIANTS] mock ch_reader，不触库；pytest filterwarnings=error 兼容
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 测试失败=指数估值计算逻辑缺陷
# [TESTS] 本文件
# [A_module] module_id=MOD-DAT-idxval | layer=test | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""IndexValuationComputeProvider 单元测试（S2 路A 管道，2026-08-28）。

覆盖：
- CAPE 真计算（5 年通胀调整，非 PE 中位平滑近似）
- 全历史扩展窗分位（expanding percentile）
- ERP 计算（1/PE - 10Y 国债）
- 降级路径（CPI/10Y 缺失）
- 行结构契约（与 INSERT_COLUMNS 对齐）
"""

from __future__ import annotations

import datetime
import sys
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest

from zephyr.data.implementations.index_valuation_compute import (
    IndexValuationComputeProvider,
    _CAPE_MIN_PERIODS,
    _CAPE_WINDOW,
)
from zephyr.data.provider_base import FetchPayload

D = datetime.date


def _payload(start: D, end: D, symbols=None) -> FetchPayload:
    return FetchPayload(
        table="c1_market.index_valuation_daily",
        symbols=symbols,
        start=start,
        end=end,
        incremental=False,
        extra={},
    )


def _mock_ch_reader_tsv(data: dict[str, list]) -> str:
    """构造 ch_reader.query 返回的 TSV 字符串。"""
    lines = []
    cols = list(data.keys())
    n = len(data[cols[0]])
    for i in range(n):
        lines.append("\t".join(str(data[c][i]) for c in cols))
    return "\n".join(lines)


class TestIndexValuationComputeProvider:
    """IndexValuationComputeProvider 核心计算逻辑测试。"""

    def test_cape_5y_nominal_without_cpi(self):
        """CPI 缺失时退化为名义 CAPE（5 年盈利均值）。"""
        provider = IndexValuationComputeProvider()
        provider.connect()

        # 构造 1000 日数据：close 从 3000 涨到 4000，PE 恒定 15
        n = 1000
        dates = pd.bdate_range(start="2020-01-01", periods=n)
        close = np.linspace(3000, 4000, n)
        pe = np.full(n, 15.0)
        df = pd.DataFrame({"close": close, "pe_ttm": pe}, index=dates)

        # CPI 缺失
        cpi_series = pd.Series(dtype=float)
        cape = provider._compute_cape_5y(df, cpi_series)

        # 名义 CAPE = close / mean(近5年 earnings)
        # earnings = close / pe，PE 恒定 → earnings 与 close 成正比
        # CAPE 应接近 PE（15），因为 mean(earnings) ≈ earnings_t（线性增长下）
        assert cape.notna().sum() > n - _CAPE_WINDOW, "CAPE 非空行数应 > n-window"
        # 验证最后几日的 CAPE 在合理范围（10~25 之间）
        tail_cape = cape.dropna().tail(10)
        assert tail_cape.between(10, 25).all(), f"CAPE 尾值应在 10~25 之间，实际 {tail_cape.values}"

    def test_cape_5y_with_cpi(self):
        """CPI 在位时真 CAPE（通胀调整）。"""
        provider = IndexValuationComputeProvider()
        provider.connect()

        n = 1000
        dates = pd.bdate_range(start="2020-01-01", periods=n)
        close = np.linspace(3000, 4000, n)
        pe = np.full(n, 15.0)
        # df 需含 trade_date 列（与 _compute_one_symbol 构造的 DataFrame 一致）
        df = pd.DataFrame({
            "trade_date": dates,
            "close": close,
            "pe_ttm": pe,
        })

        # CPI 月度序列：月增 0.2%（年化 ~2.4%）
        cpi_dates = pd.date_range(start="2020-01-01", periods=48, freq="MS")
        cpi_values = np.full(48, 0.2)
        cpi_series = pd.Series(cpi_values, index=cpi_dates, name="cpi")

        cape = provider._compute_cape_5y(df, cpi_series)
        # 真 CAPE 应略低于名义 CAPE（通胀调整后历史盈利更"贵"）
        assert cape.notna().sum() > 0, "真 CAPE 应有非空值"

    def test_expanding_percentile(self):
        """全历史扩展窗分位：单调递增序列分位应接近 1。"""
        provider = IndexValuationComputeProvider()
        series = pd.Series(np.linspace(10, 20, 100))
        pct = provider._expanding_percentile(series)
        # 最后一个值是全历史最大值 → 分位 = 1.0
        assert pct.iloc[-1] == pytest.approx(1.0, abs=0.01)
        # 第一个值是全历史最小值 → 分位 ≈ 0.01
        assert pct.iloc[0] == pytest.approx(0.01, abs=0.01)

    def test_erp_calculation(self):
        """ERP = 1/PE - 10Y（百分数口径）。"""
        provider = IndexValuationComputeProvider()
        pe = pd.Series([15.0, 20.0, 25.0])
        bond = pd.Series([2.5, 3.0, 3.5], index=pe.index)  # 2.5%/3.0%/3.5%
        erp = provider._compute_erp(pe, bond)
        # 1/15 - 0.025 = 0.0667 - 0.025 = 0.0417
        assert erp.iloc[0] == pytest.approx(1 / 15 - 0.025, abs=1e-4)
        # 1/25 - 0.035 = 0.04 - 0.035 = 0.005
        assert erp.iloc[2] == pytest.approx(1 / 25 - 0.035, abs=1e-4)

    def test_erp_nan_without_bond(self):
        """10Y 国债缺失时 ERP 为 NaN。"""
        provider = IndexValuationComputeProvider()
        pe = pd.Series([15.0, 20.0])
        bond = pd.Series(dtype=float)
        erp = provider._compute_erp(pe, bond)
        assert erp.isna().all()

    def test_fetch_structure_contract(self):
        """fetch 返回 FetchResult 结构契约：列数与 INSERT_COLUMNS 对齐。"""
        provider = IndexValuationComputeProvider()
        provider.connect()

        # mock ch_reader.query 返回空（无数据）
        with patch("zephyr.data.ch_reader.query", return_value=""):
            payload = _payload(D(2020, 1, 1), D(2020, 12, 31), symbols=["000300"])
            results = list(provider.fetch(payload, MagicMock()))
            # 无数据时 yield 空结果（不抛错）
            assert len(results) == 1
            assert results[0].rows == []
            assert results[0].error is None

    def test_fetch_with_mock_data(self):
        """mock CH 数据 → 验证输出行结构（14 列）。"""
        provider = IndexValuationComputeProvider()
        provider.connect()

        # mock PE 数据（TSV）
        pe_tsv = _mock_ch_reader_tsv({
            "trade_date": ["2020-01-02", "2020-01-03"],
            "pe_ttm": ["15.0", "15.5"],
            "dividend_yield": ["2.5", "2.5"],
        })
        # mock close 数据
        close_tsv = _mock_ch_reader_tsv({
            "trade_date": ["2020-01-02", "2020-01-03"],
            "close": ["3000.0", "3050.0"],
        })
        # mock CPI（空 → 降级名义 CAPE）
        # mock 10Y（空 → ERP NaN）

        def _mock_query(sql, **kwargs):
            if "index_valuation_daily" in sql:
                return pe_tsv
            if "kline_index" in sql:
                return close_tsv
            return ""

        with patch("zephyr.data.ch_reader.query", side_effect=_mock_query):
            payload = _payload(D(2020, 1, 1), D(2020, 12, 31), symbols=["000300"])
            results = list(provider.fetch(payload, MagicMock()))
            assert len(results) == 1
            rows = results[0].rows
            assert len(rows) == 2  # 2 个交易日
            # 验证列数 = 14（INSERT_COLUMNS 列数）
            assert len(rows[0]) == 14
            # 验证 trade_date/symbol
            assert rows[0][1] == "000300"
            # data_source = internal_compute
            assert rows[0][13] == "internal_compute"
