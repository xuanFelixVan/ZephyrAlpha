# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] tests.zephyr.data.test_akshare_provider
# [DEPENDENCIES] zephyr.data.implementations.akshare_provider
# [CONSUMERS] none
# [STARTUP] pytest
# [MATURITY] production
# [INVARIANTS] mock akshare，不触网不触库；pytest filterwarnings=error 兼容
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 测试失败=akshare fallback 能力逻辑缺陷
# [TESTS] 本文件
# [A_module] module_id=MOD-DAT-akshare_ingest | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""akshare_provider fallback 9 能力单元测试（2026-08-19 补全）。

覆盖 P1 行情×5 + P2 财报×4：
- adj_factor / kline_index / kline_daily_hfq / kline_cb / kline_hk_daily
- balance_sheet / income_statement / cashflow_statement / financial_indicator

全部 mock akshare，不触网不触库。验证：正常映射、单位换算、
日期过滤、空输入/失败路径、东财→新浪降级路径、capability 路由一致性。
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


def _payload(start: D, end: D, extra: dict | None = None, symbols=None) -> FetchPayload:
    return FetchPayload(
        table="",
        symbols=symbols,
        start=start,
        end=end,
        incremental=False,
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


# ============== P1-1 adj_factor ==============


class TestAdjFactorFetch:
    @pytest.fixture(autouse=True)
    def _no_guard_ch(self, monkeypatch):
        """#209② 写侧守卫引入 CH 覆盖键查询：本类用例与守卫正交，置空集保持不触库。"""
        monkeypatch.setattr(
            AkshareIngestProvider,
            "_covered_miniqmt_adj_keys",
            lambda self, codes, start, end: set(),
        )

    def test_normal_mapping(self, monkeypatch):
        """正常行：hfq_factor 映射 + date 过滤 + 单位保留。"""
        df = pd.DataFrame(
            {
                "date": [D(2026, 7, 5), D(2026, 7, 10)],
                "hfq_factor": [1.05, 1.06],
            }
        )
        _mock_ak(monkeypatch, stock_zh_a_daily=df)
        provider = AkshareIngestProvider()
        results = _call_fetch(
            provider,
            "adj_factor",
            _payload(D(2026, 7, 1), D(2026, 7, 10), symbols=["600519.SH"]),
        )
        assert len(results) == 1
        res = results[0]
        assert res.error is None
        assert len(res.rows) == 2
        assert res.columns == ["trade_date", "symbol", "adj_factor", "data_source"]
        r = res.rows[0]
        assert r[0] == "2026-07-05"
        assert r[1] == "600519"
        assert r[2] == pytest.approx(1.05)
        assert r[3] == "akshare"

    def test_date_range_filter(self, monkeypatch):
        """日期过滤：窗口外的行被剔除。"""
        df = pd.DataFrame(
            {
                "date": [D(2026, 6, 1), D(2026, 7, 15)],
                "hfq_factor": [1.0, 1.1],
            }
        )
        _mock_ak(monkeypatch, stock_zh_a_daily=df)
        provider = AkshareIngestProvider()
        results = _call_fetch(
            provider,
            "adj_factor",
            _payload(D(2026, 7, 1), D(2026, 7, 10), symbols=["000002.SZ"]),
        )
        assert len(results[0].rows) == 0

    def test_invalid_code_skipped(self, monkeypatch):
        """非 6 位数字代码被 _norm_code6 拒绝。"""
        df = pd.DataFrame({"date": [D(2026, 7, 1)], "hfq_factor": [1.0]})
        _mock_ak(monkeypatch, stock_zh_a_daily=df)
        # 阻断全市场 fallback（避免触发真实 CH 查询）
        monkeypatch.setattr(
            AkshareIngestProvider,
            "_get_all_a_symbols",
            lambda self, ak, policy: [],
        )
        provider = AkshareIngestProvider()
        results = _call_fetch(
            provider,
            "adj_factor",
            _payload(D(2026, 7, 1), D(2026, 7, 1), symbols=["INVALID"]),
        )
        assert len(results[0].rows) == 0

    def test_source_failure_yields_empty(self, monkeypatch):
        """源异常 → yield 空 rows（error=None），不向上抛出。"""
        _mock_ak(monkeypatch, stock_zh_a_daily=ConnectionError("timeout"))
        provider = AkshareIngestProvider()
        results = _call_fetch(
            provider,
            "adj_factor",
            _payload(D(2026, 7, 1), D(2026, 7, 10), symbols=["600519.SH"]),
        )
        assert len(results) == 1
        assert results[0].rows == []
        assert results[0].error is None

    def test_capability_routing(self, monkeypatch):
        from src.zephyr.data.implementations import akshare_provider as akp

        assert "adj_factor" in akp._AKSHARE_CAPABILITIES
        provider = AkshareIngestProvider()
        assert "adj_factor" in {c.capability_id for c in provider.meta.capabilities}


# ============== P1-2 kline_index ==============


class TestKlineIndexFetch:
    def test_normal_mapping_and_volume_conversion(self, monkeypatch):
        """正常行：volume 股→手 /100，name 映射，日期过滤。"""
        df_idx = pd.DataFrame(
            {
                "index_code": ["000001", "399001"],
                "display_name": ["上证指数", "深证成指"],
                "publish_date": [D(1991, 7, 15), D(1991, 4, 3)],
            }
        )
        df_k = pd.DataFrame(
            {
                "date": [D(2026, 7, 1), D(2026, 7, 10)],
                "open": [3000.0, 3100.0],
                "high": [3100.0, 3200.0],
                "low": [2900.0, 3000.0],
                "close": [3050.0, 3150.0],
                "volume": [100000000, 200000000],
            }
        )
        _mock_ak(monkeypatch, index_stock_info=df_idx, stock_zh_index_daily=df_k)
        provider = AkshareIngestProvider()
        results = _call_fetch(
            provider,
            "kline_index",
            _payload(D(2026, 7, 1), D(2026, 7, 10), symbols=["000001.SH"]),
        )
        assert len(results) == 1
        res = results[0]
        assert res.error is None
        assert len(res.rows) == 2
        r = res.rows[0]
        assert r[1] == "000001"
        assert r[2] == "上证指数"
        assert r[7] == 1000000  # volume /100 股→手
        assert r[8] == "akshare"

    def test_unsupported_index_code_skipped(self, monkeypatch):
        """csi 系（88/932）跳过，不抛异常。"""
        df_idx = pd.DataFrame(
            {
                "index_code": ["932000"],
                "display_name": ["中证1000"],
                "publish_date": [D(2021, 1, 1)],
            }
        )
        _mock_ak(monkeypatch, index_stock_info=df_idx, stock_zh_index_daily=pd.DataFrame())
        provider = AkshareIngestProvider()
        results = _call_fetch(
            provider,
            "kline_index",
            _payload(D(2026, 7, 1), D(2026, 7, 10), symbols=["932000.CSI"]),
        )
        assert len(results[0].rows) == 0

    def test_capability_routing(self, monkeypatch):
        from src.zephyr.data.implementations import akshare_provider as akp

        assert "kline_index" in akp._AKSHARE_CAPABILITIES


# ============== P1-3 kline_daily_hfq ==============


class TestKlineDailyHfqFetch:
    def test_normal_mapping(self, monkeypatch):
        """正常行：12 列全映射，volume 为手。"""
        df = pd.DataFrame(
            {
                "日期": [D(2026, 7, 1), D(2026, 7, 10)],
                "开盘": [100.0, 110.0],
                "收盘": [105.0, 115.0],
                "最高": [108.0, 118.0],
                "最低": [98.0, 108.0],
                "成交量": [1000, 2000],
                "成交额": [105000.0, 230000.0],
                "振幅": [2.0, 3.0],
                "涨跌幅": [1.0, 2.0],
                "涨跌额": [1.0, 2.0],
                "换手率": [0.5, 1.0],
            }
        )
        _mock_ak(monkeypatch, stock_zh_a_hist=df)
        provider = AkshareIngestProvider()
        results = _call_fetch(
            provider,
            "kline_daily_hfq",
            _payload(D(2026, 7, 1), D(2026, 7, 10), symbols=["600519.SH"]),
        )
        assert len(results) == 1
        res = results[0]
        assert res.error is None
        assert len(res.rows) == 2
        r = res.rows[1]
        assert r[1] == "600519"
        assert r[2] == pytest.approx(110.0)
        assert r[3] == pytest.approx(115.0)
        assert r[6] == 2000
        assert r[7] == pytest.approx(230000.0)
        assert r[12] == "akshare"

    def test_source_failure_yields_empty(self, monkeypatch):
        _mock_ak(monkeypatch, stock_zh_a_hist=ConnectionError("timeout"))
        provider = AkshareIngestProvider()
        results = _call_fetch(
            provider,
            "kline_daily_hfq",
            _payload(D(2026, 7, 1), D(2026, 7, 10), symbols=["600519.SH"]),
        )
        assert results[0].rows == []
        assert results[0].error is None

    def test_capability_routing(self, monkeypatch):
        from src.zephyr.data.implementations import akshare_provider as akp

        assert "kline_daily_hfq" in akp._AKSHARE_CAPABILITIES


# ============== P1-4 kline_cb ==============


class TestKlineCbFetch:
    def test_normal_mapping_and_volume_conversion(self, monkeypatch):
        """正常行：volume 张→手 /10，上市/摘牌过滤。"""
        df_cov = pd.DataFrame(
            {
                "债券代码": ["113001", "128001"],
                "上市日期": [D(2015, 3, 6), D(2014, 1, 1)],
                "摘牌日期": ["", D(2020, 1, 1)],
            }
        )
        df_k = pd.DataFrame(
            {
                "date": [D(2026, 7, 1), D(2026, 7, 10)],
                "open": [100.0, 110.0],
                "high": [108.0, 118.0],
                "low": [98.0, 108.0],
                "close": [105.0, 115.0],
                "volume": [10000, 20000],
            }
        )
        _mock_ak(monkeypatch, bond_zh_cov=df_cov, bond_zh_hs_cov_daily=df_k)
        provider = AkshareIngestProvider()
        results = _call_fetch(
            provider,
            "kline_cb",
            _payload(D(2026, 7, 1), D(2026, 7, 10)),  # symbols=None 取清单
        )
        assert len(results) == 1
        res = results[0]
        assert res.error is None
        # 113001 上市日期在窗口内，128001 已摘牌（<start）被过滤
        assert len(res.rows) == 2
        r = res.rows[0]
        assert r[1] == "113001"
        assert r[6] == 1000  # volume /10 张→手
        assert r[7] == "akshare"

    def test_source_failure_yields_empty(self, monkeypatch):
        _mock_ak(monkeypatch, bond_zh_cov=ConnectionError("timeout"))
        provider = AkshareIngestProvider()
        results = _call_fetch(
            provider,
            "kline_cb",
            _payload(D(2026, 7, 1), D(2026, 7, 10)),
        )
        assert results[0].rows == []
        assert results[0].error is not None

    def test_capability_routing(self, monkeypatch):
        from src.zephyr.data.implementations import akshare_provider as akp

        assert "kline_cb" in akp._AKSHARE_CAPABILITIES


# ============== P2 财报类公共辅助 ==============


def _mock_em_report(monkeypatch, df: pd.DataFrame, api_name: str):
    """mock 东财三大报表接口（symbol 参数格式 SH600519）。"""
    return _mock_ak(monkeypatch, **{api_name: df})


# ============== P2-1 balance_sheet ==============


class TestBalanceSheetFetch:
    def test_normal_mapping(self, monkeypatch):
        df = pd.DataFrame(
            {
                "REPORT_DATE": ["2026-03-31 00:00:00"],
                "NOTICE_DATE": ["2026-04-25 00:00:00"],
                "SHARE_CAPITAL": [100000000.0],
                "MONETARYFUNDS": [5000000.0],
                "ACCOUNTS_RECE": [2000000.0],
                "INVENTORY": [3000000.0],
                "TOTAL_CURRENT_ASSETS": [10000000.0],
                "FIXED_ASSET": [4000000.0],
                "INTANGIBLE_ASSET": [500000.0],
                "GOODWILL": [0.0],
                "TOTAL_NONCURRENT_ASSETS": [5000000.0],
                "TOTAL_ASSETS": [15000000.0],
                "SHORT_LOAN": [1000000.0],
                "LONG_LOAN": [2000000.0],
                "ACCOUNTS_PAYABLE": [1500000.0],
                "TOTAL_CURRENT_LIAB": [3000000.0],
                "TOTAL_NONCURRENT_LIAB": [2000000.0],
                "TOTAL_LIABILITIES": [5000000.0],
                "TOTAL_PARENT_EQUITY": [9000000.0],
                "TOTAL_EQUITY": [10000000.0],
                "CAPITAL_RESERVE": [3000000.0],
                "UNASSIGN_RPOFIT": [4000000.0],
                "SURPLUS_RESERVE": [2000000.0],
            }
        )
        _mock_em_report(monkeypatch, df, "stock_balance_sheet_by_report_em")
        provider = AkshareIngestProvider()
        results = _call_fetch(
            provider,
            "balance_sheet",
            _payload(D(2026, 4, 1), D(2026, 4, 30), symbols=["600519.SH"]),
        )
        assert len(results) == 1
        res = results[0]
        assert res.error is None
        assert len(res.rows) == 1
        r = res.rows[0]
        assert r[0] == "600519"
        assert r[1] == "2026-04-25"
        assert r[2] == "2026-03-31"
        assert r[3] is None  # company_type
        assert r[4] == pytest.approx(100000000.0)
        assert r[25] == "akshare"

    def test_notice_date_filter(self, monkeypatch):
        """NOTICE_DATE 不在窗口内的行被过滤。"""
        df = pd.DataFrame(
            {
                "REPORT_DATE": ["2026-03-31 00:00:00"],
                "NOTICE_DATE": ["2026-03-01 00:00:00"],
                "SHARE_CAPITAL": [100000000.0],
                "MONETARYFUNDS": [5000000.0],
                "ACCOUNTS_RECE": [2000000.0],
                "INVENTORY": [3000000.0],
                "TOTAL_CURRENT_ASSETS": [10000000.0],
                "FIXED_ASSET": [4000000.0],
                "INTANGIBLE_ASSET": [500000.0],
                "GOODWILL": [0.0],
                "TOTAL_NONCURRENT_ASSETS": [5000000.0],
                "TOTAL_ASSETS": [15000000.0],
                "SHORT_LOAN": [1000000.0],
                "LONG_LOAN": [2000000.0],
                "ACCOUNTS_PAYABLE": [1500000.0],
                "TOTAL_CURRENT_LIAB": [3000000.0],
                "TOTAL_NONCURRENT_LIAB": [2000000.0],
                "TOTAL_LIABILITIES": [5000000.0],
                "TOTAL_PARENT_EQUITY": [9000000.0],
                "TOTAL_EQUITY": [10000000.0],
                "CAPITAL_RESERVE": [3000000.0],
                "UNASSIGN_RPOFIT": [4000000.0],
                "SURPLUS_RESERVE": [2000000.0],
            }
        )
        _mock_em_report(monkeypatch, df, "stock_balance_sheet_by_report_em")
        provider = AkshareIngestProvider()
        results = _call_fetch(
            provider,
            "balance_sheet",
            _payload(D(2026, 4, 1), D(2026, 4, 30), symbols=["600519.SH"]),
        )
        assert len(results[0].rows) == 0

    def test_capability_routing(self, monkeypatch):
        from src.zephyr.data.implementations import akshare_provider as akp

        assert "balance_sheet" in akp._AKSHARE_CAPABILITIES


# ============== P2-2 income_statement ==============


class TestIncomeStatementFetch:
    def test_normal_mapping(self, monkeypatch):
        df = pd.DataFrame(
            {
                "REPORT_DATE": ["2026-03-31 00:00:00"],
                "NOTICE_DATE": ["2026-04-25 00:00:00"],
                "TOTAL_OPERATE_INCOME": [100000000.0],
                "OPERATE_INCOME": [95000000.0],
                "TOTAL_OPERATE_COST": [60000000.0],
                "OPERATE_COST": [40000000.0],
                "OPERATE_TAX_ADD": [5000000.0],
                "SALE_EXPENSE": [3000000.0],
                "MANAGE_EXPENSE": [4000000.0],
                "FINANCE_EXPENSE": [2000000.0],
                "RESEARCH_EXPENSE": [1000000.0],
                "OPERATE_PROFIT": [35000000.0],
                "NONBUSINESS_INCOME": [1000000.0],
                "NONBUSINESS_EXPENSE": [500000.0],
                "TOTAL_PROFIT": [36000000.0],
                "INCOME_TAX": [9000000.0],
                "NETPROFIT": [27000000.0],
                "PARENT_NETPROFIT": [25000000.0],
                "MINORITY_INTEREST": [2000000.0],
                "BASIC_EPS": [0.5],
                "DILUTED_EPS": [0.48],
                "TOTAL_COMPRE_INCOME": [28000000.0],
            }
        )
        _mock_em_report(monkeypatch, df, "stock_profit_sheet_by_report_em")
        provider = AkshareIngestProvider()
        results = _call_fetch(
            provider,
            "income_statement",
            _payload(D(2026, 4, 1), D(2026, 4, 30), symbols=["600519.SH"]),
        )
        assert len(results) == 1
        res = results[0]
        assert res.error is None
        assert len(res.rows) == 1
        r = res.rows[0]
        assert r[0] == "600519"
        assert r[1] == "2026-04-25"
        assert r[2] == "2026-04-25"  # actual_announce_date = NOTICE_DATE
        assert r[5] == pytest.approx(100000000.0)  # total_revenue
        assert r[25] == "akshare"

    def test_capability_routing(self, monkeypatch):
        from src.zephyr.data.implementations import akshare_provider as akp

        assert "income_statement" in akp._AKSHARE_CAPABILITIES


# ============== P2-3 cashflow_statement ==============


class TestCashflowStatementFetch:
    def test_normal_mapping(self, monkeypatch):
        df = pd.DataFrame(
            {
                "REPORT_DATE": ["2026-03-31 00:00:00"],
                "NOTICE_DATE": ["2026-04-25 00:00:00"],
                "NETCASH_OPERATE": [10000000.0],
                "SALES_SERVICES": [50000000.0],
                "TOTAL_OPERATE_INFLOW": [60000000.0],
                "TOTAL_OPERATE_OUTFLOW": [50000000.0],
                "NETCASH_INVEST": [-2000000.0],
                "TOTAL_INVEST_INFLOW": [3000000.0],
                "TOTAL_INVEST_OUTFLOW": [5000000.0],
                "NETCASH_FINANCE": [-3000000.0],
                "TOTAL_FINANCE_INFLOW": [10000000.0],
                "TOTAL_FINANCE_OUTFLOW": [13000000.0],
                "CCE_ADD": [5000000.0],
                "END_CCE": [55000000.0],
            }
        )
        _mock_em_report(monkeypatch, df, "stock_cash_flow_sheet_by_report_em")
        provider = AkshareIngestProvider()
        results = _call_fetch(
            provider,
            "cashflow_statement",
            _payload(D(2026, 4, 1), D(2026, 4, 30), symbols=["600519.SH"]),
        )
        assert len(results) == 1
        res = results[0]
        assert res.error is None
        assert len(res.rows) == 1
        r = res.rows[0]
        assert r[0] == "600519"
        assert r[1] == "2026-04-25"
        assert r[3] == pytest.approx(10000000.0)  # ocf_net
        assert r[14] == pytest.approx(55000000.0)  # ending_cash_balance
        assert r[15] is None  # fcff
        assert r[16] == "akshare"

    def test_capability_routing(self, monkeypatch):
        from src.zephyr.data.implementations import akshare_provider as akp

        assert "cashflow_statement" in akp._AKSHARE_CAPABILITIES


# ============== P2-4 financial_indicator ==============


class TestFinancialIndicatorFetch:
    def test_normal_mapping(self, monkeypatch):
        df = pd.DataFrame(
            {
                "日期": [D(2026, 3, 31), D(2026, 6, 30)],
                "加权每股收益(元)": [0.5, 0.6],
                "摊薄每股收益(元)": [0.48, 0.58],
                "净资产收益率(%)": [10.0, 11.0],
                "加权净资产收益率(%)": [9.5, 10.5],
                "总资产净利润率(%)": [8.0, 8.5],
                "销售毛利率(%)": [30.0, 32.0],
                "销售净利率(%)": [15.0, 16.0],
                "资产负债率(%)": [40.0, 38.0],
                "每股净资产_调整后(元)": [5.0, 5.5],
                "每股经营性现金流(元)": [1.0, 1.2],
                "每股未分配利润(元)": [2.0, 2.2],
                "净利润增长率(%)": [5.0, 6.0],
                "主营业务收入增长率(%)": [10.0, 12.0],
                "总资产增长率(%)": [8.0, 9.0],
                "净资产增长率(%)": [7.0, 8.0],
            }
        )
        _mock_ak(monkeypatch, stock_financial_analysis_indicator=df)
        provider = AkshareIngestProvider()
        results = _call_fetch(
            provider,
            "financial_indicator",
            _payload(D(2026, 1, 1), D(2026, 6, 30), symbols=["600519.SH"]),
        )
        assert len(results) == 1
        res = results[0]
        assert res.error is None
        assert len(res.rows) == 2
        r = res.rows[0]
        assert r[0] == "600519"
        assert r[1] == "1970-01-01"  # announce_date 缺失哨兵
        assert r[2] == "2026-03-31"
        assert r[3] == pytest.approx(0.5)  # eps_basic
        assert r[34] == "akshare"

    def test_date_range_filter(self, monkeypatch):
        """report_period > end 的行被过滤。"""
        df = pd.DataFrame(
            {
                "日期": [D(2026, 9, 30)],
                "加权每股收益(元)": [0.7],
            }
        )
        _mock_ak(monkeypatch, stock_financial_analysis_indicator=df)
        provider = AkshareIngestProvider()
        results = _call_fetch(
            provider,
            "financial_indicator",
            _payload(D(2026, 1, 1), D(2026, 6, 30), symbols=["600519.SH"]),
        )
        assert len(results[0].rows) == 0

    def test_capability_routing(self, monkeypatch):
        from src.zephyr.data.implementations import akshare_provider as akp

        assert "financial_indicator" in akp._AKSHARE_CAPABILITIES


# ============== P1-5 kline_hk_daily（东财→新浪降级） ==============


def _hk_em_spot_df() -> pd.DataFrame:
    """东财港股清单（列：代码/名称）。"""
    return pd.DataFrame({"代码": ["00700"], "名称": ["腾讯控股"]})


def _hk_em_hist_df() -> pd.DataFrame:
    """东财港股日K（列：日期/开盘/收盘/最高/最低/成交量/成交额/...）。"""
    return pd.DataFrame(
        {
            "日期": [D(2026, 8, 18)],
            "开盘": [594.0],
            "收盘": [587.0],
            "最高": [596.0],
            "最低": [587.0],
            "成交量": [17590658],
            "成交额": [1.040306e10],
            "振幅": [1.52],
            "涨跌幅": [-0.84],
            "涨跌额": [-5.0],
            "换手率": [0.19],
        }
    )


def _hk_sina_spot_df() -> pd.DataFrame:
    """新浪港股清单（列：代码/中文名称）。"""
    return pd.DataFrame({"代码": ["00700"], "中文名称": ["腾讯控股"]})


def _hk_sina_daily_df() -> pd.DataFrame:
    """新浪港股日K（列：date/open/high/low/close/volume/amount，volume 单位股）。"""
    return pd.DataFrame(
        {
            "date": [D(2026, 8, 18)],
            "open": [444.2],
            "high": [446.2],
            "low": [437.6],
            "close": [442.4],
            "volume": [23218078.0],
            "amount": [1.024250e10],
        }
    )


class TestKlineHkDailyFetch:
    def test_normal_em_mapping(self, monkeypatch):
        """正常路径：东财清单+东财日K，10 列映射 + 日期过滤。"""
        _mock_ak(monkeypatch, stock_hk_spot_em=_hk_em_spot_df(), stock_hk_hist=_hk_em_hist_df())
        provider = AkshareIngestProvider()
        results = _call_fetch(
            provider,
            "kline_hk_daily",
            _payload(D(2026, 8, 18), D(2026, 8, 19)),
        )
        assert len(results) == 1
        res = results[0]
        assert res.error is None
        assert len(res.rows) == 1
        r = res.rows[0]
        assert r[0] == "2026-08-18"
        assert r[1] == "00700.HK"
        assert r[2] == "腾讯控股"
        assert r[3] == pytest.approx(594.0)
        assert r[6] == pytest.approx(587.0)
        assert r[7] == 17590658
        assert r[8] == pytest.approx(1.040306e10)
        assert r[9] == "akshare"

    def test_em_list_fails_fallback_sina(self, monkeypatch):
        """东财清单断连 → 降级新浪清单；东财日K断连 → 降级新浪日K。"""
        _mock_ak(
            monkeypatch,
            stock_hk_spot_em=ConnectionError("RemoteDisconnected"),
            stock_hk_spot=_hk_sina_spot_df(),
            stock_hk_hist=ConnectionError("RemoteDisconnected"),
            stock_hk_daily=_hk_sina_daily_df(),
        )
        provider = AkshareIngestProvider()
        results = _call_fetch(
            provider,
            "kline_hk_daily",
            _payload(D(2026, 8, 18), D(2026, 8, 19)),
        )
        assert len(results) == 1
        res = results[0]
        assert res.error is None
        assert len(res.rows) == 1
        r = res.rows[0]
        assert r[0] == "2026-08-18"
        assert r[1] == "00700.HK"
        assert r[2] == "腾讯控股"
        assert r[3] == pytest.approx(444.2)
        assert r[7] == 23218078  # 新浪 volume 为股，float→int 不换算
        assert r[8] == pytest.approx(1.024250e10)

    def test_em_kline_fails_fallback_sina_kline(self, monkeypatch):
        """东财清单正常但东财日K断连 → 单票降级新浪日K。"""
        _mock_ak(
            monkeypatch,
            stock_hk_spot_em=_hk_em_spot_df(),
            stock_hk_hist=ConnectionError("RemoteDisconnected"),
            stock_hk_daily=_hk_sina_daily_df(),
        )
        provider = AkshareIngestProvider()
        results = _call_fetch(
            provider,
            "kline_hk_daily",
            _payload(D(2026, 8, 18), D(2026, 8, 19)),
        )
        assert len(results) == 1
        res = results[0]
        assert res.error is None
        assert len(res.rows) == 1
        assert res.rows[0][3] == pytest.approx(444.2)

    def test_both_channels_fail_yields_error(self, monkeypatch):
        """清单双通道均失败 → yield error，不抛出。"""
        _mock_ak(
            monkeypatch,
            stock_hk_spot_em=ConnectionError("RemoteDisconnected"),
            stock_hk_spot=ConnectionError("sina down"),
        )
        provider = AkshareIngestProvider()
        results = _call_fetch(
            provider,
            "kline_hk_daily",
            _payload(D(2026, 8, 18), D(2026, 8, 19)),
        )
        assert len(results) == 1
        res = results[0]
        assert res.rows == []
        assert res.error is not None
        assert "stock_hk_spot_em 失败" in res.error
        assert "stock_hk_spot 失败" in res.error

    def test_em_list_empty_fallback_sina(self, monkeypatch):
        """东财清单返回空 → 同样触发降级新浪。"""
        _mock_ak(
            monkeypatch,
            stock_hk_spot_em=pd.DataFrame(),
            stock_hk_spot=_hk_sina_spot_df(),
            stock_hk_hist=ConnectionError("RemoteDisconnected"),
            stock_hk_daily=_hk_sina_daily_df(),
        )
        provider = AkshareIngestProvider()
        results = _call_fetch(
            provider,
            "kline_hk_daily",
            _payload(D(2026, 8, 18), D(2026, 8, 19)),
        )
        assert len(results) == 1
        res = results[0]
        assert res.error is None
        assert len(res.rows) == 1
        assert res.rows[0][2] == "腾讯控股"

    def test_capability_routing(self, monkeypatch):
        from src.zephyr.data.implementations import akshare_provider as akp

        assert "kline_hk_daily" in akp._AKSHARE_CAPABILITIES


# ============== hk_stock_list（东财→新浪降级，全量不截断） ==============


class TestHkStockListFetch:
    def test_normal_em_mapping(self, monkeypatch):
        """正常路径：东财清单，code/name 两列映射。"""
        _mock_ak(monkeypatch, stock_hk_spot_em=_hk_em_spot_df())
        provider = AkshareIngestProvider()
        results = _call_fetch(provider, "hk_stock_list", _payload(D(2026, 8, 18), D(2026, 8, 19)))
        assert len(results) == 1
        res = results[0]
        assert res.error is None
        assert res.rows == [("00700", "腾讯控股")]

    def test_em_fails_fallback_sina_full_list_no_truncation(self, monkeypatch):
        """东财断连→新浪降级；600 只全量保留（不被 kline 场景 500 上限截断），中文名称→name 归一化。"""
        big_sina = pd.DataFrame(
            {
                "代码": [f"{i:05d}" for i in range(1, 601)],
                "中文名称": [f"股票{i}" for i in range(1, 601)],
            }
        )
        _mock_ak(
            monkeypatch,
            stock_hk_spot_em=ConnectionError("RemoteDisconnected"),
            stock_hk_spot=big_sina,
        )
        provider = AkshareIngestProvider()
        results = _call_fetch(provider, "hk_stock_list", _payload(D(2026, 8, 18), D(2026, 8, 19)))
        res = results[0]
        assert res.error is None
        assert len(res.rows) == 600
        assert res.rows[0] == ("00001", "股票1")
        assert res.rows[-1] == ("00600", "股票600")

    def test_em_empty_fallback_sina(self, monkeypatch):
        """东财返空 → 降级新浪。"""
        _mock_ak(
            monkeypatch,
            stock_hk_spot_em=pd.DataFrame(),
            stock_hk_spot=_hk_sina_spot_df(),
        )
        provider = AkshareIngestProvider()
        results = _call_fetch(provider, "hk_stock_list", _payload(D(2026, 8, 18), D(2026, 8, 19)))
        res = results[0]
        assert res.error is None
        assert res.rows == [("00700", "腾讯控股")]

    def test_both_channels_fail_yields_error(self, monkeypatch):
        """双通道均失败 → yield error 聚合两路错误，不抛出。"""
        _mock_ak(
            monkeypatch,
            stock_hk_spot_em=ConnectionError("RemoteDisconnected"),
            stock_hk_spot=ConnectionError("sina down"),
        )
        provider = AkshareIngestProvider()
        results = _call_fetch(provider, "hk_stock_list", _payload(D(2026, 8, 18), D(2026, 8, 19)))
        res = results[0]
        assert res.rows == []
        assert res.error is not None
        assert "stock_hk_spot_em 失败" in res.error
        assert "stock_hk_spot 失败" in res.error

    def test_capability_routing(self, monkeypatch):
        from src.zephyr.data.implementations import akshare_provider as akp

        assert "hk_stock_list" in akp._AKSHARE_CAPABILITIES
