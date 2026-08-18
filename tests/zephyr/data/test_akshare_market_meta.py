# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] tests.zephyr.data.test_akshare_market_meta
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
# [ERROR_CONTRACT] 测试失败=JOB-077 五能力逻辑缺陷
# [TESTS] 本文件
# [A_module] module_id=MOD-DAT-akshare_ingest | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""JOB-077 市场元数据与约束接入（DS-081~085）单元测试。

覆盖：板块前缀规则/涨跌停幅度规则/ROUND_HALF_UP 精度/除权修正昨收/
stock_basic 快照/index_constituent 四指数+权重/st_stock_list 科创板扩展/
suspend 东财→百度兜底/K线缺口推导。
全部 mock akshare 与 ch_reader，不触网不触库。
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
        incremental=True, extra=extra or {},
    )


def _mock_ak(monkeypatch, **attrs) -> MagicMock:
    """构造 akshare 模块 mock（绕过真实 SDK 的 pkg_resources 警告）。

    attrs 值三态：DataFrame/list → return_value；Exception → side_effect 抛出；
    callable → side_effect 转发调用（MagicMock side_effect 返回非 DEFAULT 即作为返回值）。
    """
    mock_ak = MagicMock()
    for name, val in attrs.items():
        child = getattr(mock_ak, name)
        child.__name__ = name
        if isinstance(val, Exception):
            child.side_effect = val
        elif callable(val):
            child.side_effect = val
        else:
            child.return_value = val
    monkeypatch.setitem(sys.modules, "akshare", mock_ak)
    return mock_ak


def _patch_provider_ch(monkeypatch, fake_query):
    """patch provider 命名空间的 ch_reader.query。

    关键：provider 内部 `from zephyr.data import ch_reader`（绝对导入，src/ 在
    sys.path 上时解析为 zephyr.data.ch_reader），而本测试文件按仓惯例以
    `src.zephyr...` 导入——两者是不同模块实例，patch 必须打到 provider 侧命名空间。
    """
    import zephyr.data.ch_reader as provider_ch_reader

    monkeypatch.setattr(provider_ch_reader, "query", fake_query)


def _call_fetch(provider, cap: str, payload: FetchPayload) -> list:
    """调用 provider.fetch 路由并收集全部 FetchResult。"""
    payload.extra = {**(payload.extra or {}), "capability": cap}
    policy = MagicMock(rpm=0, max_retries=1, backoff="fixed", initial_wait=0)
    return list(provider.fetch(payload, policy))


# ============== 板块前缀规则 ==============

class TestBoardRules:
    @pytest.mark.parametrize("code,expected", [
        ("600000", "沪主板"), ("601398", "沪主板"),
        ("688001", "科创板"), ("689009", "科创板"),
        ("000001", "深主板"), ("002594", "深主板"),
        ("300750", "创业板"), ("301999", "创业板"),
        ("430047", "北交所"), ("830799", "北交所"),
        ("870199", "北交所"), ("920001", "北交所"),
        ("900901", ""), ("200011", ""), ("110000", ""),
    ])
    def test_board_of_a_share(self, code, expected):
        assert AkshareIngestProvider._board_of_a_share(code) == expected


# ============== 涨跌停幅度规则 ==============

class TestLimitPctRules:
    def test_main_board_normal(self):
        assert AkshareIngestProvider._limit_pct_of("600000", D(2026, 8, 14), False) == 0.10
        assert AkshareIngestProvider._limit_pct_of("000001", D(2026, 8, 14), False) == 0.10

    def test_main_board_st(self):
        assert AkshareIngestProvider._limit_pct_of("600000", D(2026, 8, 14), True) == 0.05
        assert AkshareIngestProvider._limit_pct_of("000001", D(2021, 3, 1), True) == 0.05

    def test_star_market(self):
        # 科创板恒 20%（含ST）
        assert AkshareIngestProvider._limit_pct_of("688001", D(2020, 1, 2), False) == 0.20
        assert AkshareIngestProvider._limit_pct_of("688001", D(2026, 8, 14), True) == 0.20

    def test_chinext_regime_change(self):
        # 创业板 2020-08-24 改革：此前 ST/*ST 5%、非ST 10%，此后 20%（含ST）
        assert AkshareIngestProvider._limit_pct_of("300750", D(2020, 8, 21), False) == 0.10
        assert AkshareIngestProvider._limit_pct_of("300750", D(2020, 8, 21), True) == 0.05
        assert AkshareIngestProvider._limit_pct_of("300750", D(2020, 8, 24), False) == 0.20
        assert AkshareIngestProvider._limit_pct_of("300750", D(2020, 8, 24), True) == 0.20

    def test_bse(self):
        # 北交所 30%（无 ST 5% 规则）
        assert AkshareIngestProvider._limit_pct_of("830799", D(2026, 8, 14), False) == 0.30
        assert AkshareIngestProvider._limit_pct_of("830799", D(2026, 8, 14), True) == 0.30

    def test_unknown_board(self):
        assert AkshareIngestProvider._limit_pct_of("200011", D(2026, 8, 14), False) is None


# ============== stk_limit 计算（mock ch_reader） ==============

class TestFetchStkLimit:
    def _install_ch_mock(self, monkeypatch, days_tsv, bars_tsv, st_tsv):
        def fake_query(sql, timeout=0):
            if "DISTINCT trade_date" in sql:
                return days_tsv
            if "close, adj_factor" in sql:
                return bars_tsv
            if "st_stock_list" in sql:
                return st_tsv
            if "count()" in sql:
                return "100\n"  # 探活（CH 可达标记）
            return ""

        _patch_provider_ch(monkeypatch, fake_query)

    def test_limit_calc_multi_board(self, monkeypatch):
        p = AkshareIngestProvider()
        days = "2026-08-11\n2026-08-12\n"
        # 创业/科创/北交股票需 >5 根历史 bar 逃逸新股无限制期（i<5 规则）；
        # 缓冲窗口 bar 不在 trade_days 内不产出行，仅用于抬高序列索引
        bars = "\n".join([
            "2026-08-10\t600000\t10.00\t1.0",   # 沪主板基准昨收
            "2026-08-11\t600000\t10.10\t1.0",
            "2026-08-12\t600000\t10.20\t1.0",
            "2026-08-10\t600001\t20.00\t1.0",   # ST 沪主板
            "2026-08-11\t600001\t20.50\t1.0",
            "2026-08-12\t600001\t20.60\t1.0",
            "2026-08-03\t300750\t99.00\t1.0",   # 创业板 20%（7 根缓冲 bar）
            "2026-08-04\t300750\t99.10\t1.0",
            "2026-08-05\t300750\t99.20\t1.0",
            "2026-08-06\t300750\t99.30\t1.0",
            "2026-08-07\t300750\t99.40\t1.0",
            "2026-08-08\t300750\t99.50\t1.0",
            "2026-08-10\t300750\t100.00\t1.0",
            "2026-08-11\t300750\t101.00\t1.0",
            "2026-08-12\t300750\t102.00\t1.0",
            "2026-08-03\t688001\t49.00\t1.0",   # 科创板 20%（7 根缓冲 bar）
            "2026-08-04\t688001\t49.10\t1.0",
            "2026-08-05\t688001\t49.20\t1.0",
            "2026-08-06\t688001\t49.30\t1.0",
            "2026-08-07\t688001\t49.40\t1.0",
            "2026-08-08\t688001\t49.50\t1.0",
            "2026-08-10\t688001\t50.00\t1.0",
            "2026-08-11\t688001\t50.50\t1.0",
            "2026-08-12\t688001\t51.00\t1.0",
            "2026-08-03\t830799\t4.90\t1.0",    # 北交所 30%（7 根缓冲 bar）
            "2026-08-04\t830799\t4.91\t1.0",
            "2026-08-05\t830799\t4.92\t1.0",
            "2026-08-06\t830799\t4.93\t1.0",
            "2026-08-07\t830799\t4.94\t1.0",
            "2026-08-08\t830799\t4.95\t1.0",
            "2026-08-10\t830799\t5.00\t1.0",
            "2026-08-11\t830799\t5.05\t1.0",
            "2026-08-12\t830799\t5.10\t1.0",
            "2026-08-10\t600002\t10.00\t1.0",   # 除权日：adj 1.0→0.5
            "2026-08-11\t600002\t10.10\t1.0",
            "2026-08-12\t600002\t5.06\t0.5",
            "2026-08-10\t900901\t9.99\t1.0",    # 未知板块（B股）应被过滤
            "2026-08-11\t900901\t9.99\t1.0",
            "2026-08-12\t900901\t9.99\t1.0",
        ]) + "\n"
        st = "2026-08-11\t600001\n2026-08-12\t600001\n"
        self._install_ch_mock(monkeypatch, days, bars, st)

        results = _call_fetch(p, "stk_limit", _payload(D(2026, 8, 11), D(2026, 8, 12)))
        assert len(results) == 1 and not results[0].error
        rows = results[0].rows
        by = {(r[0], r[1]): r for r in rows}

        # 沪主板 10%：10.00→11.00/9.00（08-11）；10.10→11.11/9.09（08-12）
        assert ("2026-08-11", "600000") in by
        r = by[("2026-08-11", "600000")]
        assert (r[3], r[4], r[5], r[6], r[7]) == (11.00, 9.00, 0.10, 0, "沪主板")
        r = by[("2026-08-12", "600000")]
        assert (r[3], r[4]) == (11.11, 9.09)

        # ST 5%：20.00→21.00/19.00
        r = by[("2026-08-11", "600001")]
        assert (r[3], r[4], r[5], r[6]) == (21.00, 19.00, 0.05, 1)

        # 创业板 20%：100.00→120.00/80.00；科创板 20%：50.00→60.00/40.00
        assert by[("2026-08-11", "300750")][3] == 120.00
        assert by[("2026-08-11", "688001")][3] == 60.00

        # 北交所 30%：5.00→6.50/3.50
        assert by[("2026-08-11", "830799")][3] == 6.50

        # 除权修正：pre_close = 10.10 × (0.5/1.0) = 5.05 → 涨停 5.56（5.055 五入）
        r = by[("2026-08-12", "600002")]
        assert r[2] == 5.05 and r[3] == 5.56 and r[4] == 4.55

        # B股（未知板块）不产出行
        assert not any(sym == "900901" for _, sym in by)

    def test_round_half_up_edge(self, monkeypatch):
        # 10.05×1.1=11.055 → ROUND_HALF_UP 11.06（银行家舍入会得 11.05，防回归）
        p = AkshareIngestProvider()
        days = "2026-08-12\n"
        bars = ("2026-08-11\t600003\t10.05\t1.0\n"
                "2026-08-12\t600003\t10.10\t1.0\n")
        self._install_ch_mock(monkeypatch, days, bars, "")
        results = _call_fetch(p, "stk_limit", _payload(D(2026, 8, 12), D(2026, 8, 12)))
        rows = results[0].rows
        assert len(rows) == 1
        assert rows[0][3] == 11.06  # 涨停 10.05×1.1=11.055 → 五入 11.06
        assert rows[0][4] == 9.05   # 跌停 10.05×0.9=9.045 → 五入 9.05（非银行家舍入）

    def test_new_stock_unlimited_period(self, monkeypatch):
        # 创业板新股上市前 5 个交易日无涨跌幅限制 → limit NULL
        p = AkshareIngestProvider()
        days = "2026-08-11\n2026-08-12\n"
        bars = ("2026-08-11\t301999\t20.00\t1.0\n"   # 上市首日（i=0，不产出行）
                "2026-08-12\t301999\t24.00\t1.0\n")  # i=1 <5 → NULL
        self._install_ch_mock(monkeypatch, days, bars, "")
        results = _call_fetch(p, "stk_limit", _payload(D(2026, 8, 11), D(2026, 8, 12)))
        rows = results[0].rows
        assert len(rows) == 1
        assert rows[0][0] == "2026-08-12" and rows[0][1] == "301999"
        assert rows[0][3] is None and rows[0][4] is None and rows[0][5] is None

    def test_ch_unreachable_yields_error(self, monkeypatch):
        # ch_reader.query 对 CH 故障静默返回空串 → 探活也为空 → 必须显式 error
        _patch_provider_ch(monkeypatch, lambda sql, timeout=0: "")
        p = AkshareIngestProvider()
        results = _call_fetch(p, "stk_limit", _payload(D(2026, 8, 12), D(2026, 8, 12)))
        assert len(results) == 1 and results[0].error
        assert "不可达" in results[0].error


# ============== stock_basic 快照 ==============

class TestFetchStockBasic:
    def test_sh_sz_snapshot(self, monkeypatch):
        def sh_fn(symbol=None, **kw):
            if symbol == "科创板":
                return pd.DataFrame({
                    "证券代码": ["688001"], "证券简称": ["科创示例"],
                    "证券全称": ["科创示例"], "公司全称": ["科创示例股份有限公司"],
                    "上市日期": ["2021-06-01"],
                })
            return pd.DataFrame({
                "证券代码": ["600000"], "证券简称": ["浦发银行"],
                "证券全称": ["浦发银行"], "公司全称": ["上海浦东发展银行股份有限公司"],
                "上市日期": ["1999-11-10"],
            })

        sz_df = pd.DataFrame({
            "板块": ["主板", "创业板"],
            "A股代码": ["000001", "300750"],
            "A股简称": ["平安银行", "宁德时代"],
            "A股上市日期": ["1991-04-03", "2018-06-11"],
            "A股总股本": ["0", "0"],
            "A股流通股本": ["0", "0"],
            "所属行业": ["J 金融业", "C38 电气机械和器材制造业"],
        })
        p = AkshareIngestProvider()
        mock_ak = MagicMock()
        mock_ak.stock_info_sh_name_code = sh_fn
        mock_ak.stock_info_sh_name_code.__name__ = "stock_info_sh_name_code"
        mock_ak.stock_info_sz_name_code = MagicMock(return_value=sz_df)
        mock_ak.stock_info_sz_name_code.__name__ = "stock_info_sz_name_code"
        # 东财行业反查模拟反爬封锁 → industry 留空不致命
        mock_ak.stock_board_industry_name_em = MagicMock(
            side_effect=ConnectionError("em blocked")
        )
        mock_ak.stock_board_industry_name_em.__name__ = "stock_board_industry_name_em"
        monkeypatch.setitem(sys.modules, "akshare", mock_ak)
        results = _call_fetch(p, "stock_basic", _payload(D(2026, 8, 14), D(2026, 8, 14)))
        assert len(results) == 1 and not results[0].error
        rows = results[0].rows
        by = {r[1]: r for r in rows}
        assert len(rows) == 4
        # SH 主板：fullname 有值，industry 封锁期留空
        assert by["600000"][3] == "上海浦东发展银行股份有限公司"
        assert by["600000"][4] == "" and by["600000"][5] == "沪主板"
        assert by["600000"][6] == "1999-11-10"
        # 科创板板块判定
        assert by["688001"][5] == "科创板"
        # SZ：industry 来自交易所清单，board 来自前缀规则
        assert by["000001"][4] == "J 金融业" and by["000001"][5] == "深主板"
        assert by["300750"][5] == "创业板"

    def test_sh_failure_sz_survives(self, monkeypatch):
        # SH 接口全挂时 SZ 数据仍产出（单源失败不致命）
        sz_df = pd.DataFrame({
            "板块": ["主板"], "A股代码": ["000001"], "A股简称": ["平安银行"],
            "A股上市日期": ["1991-04-03"], "A股总股本": ["0"], "A股流通股本": ["0"],
            "所属行业": ["J 金融业"],
        })
        p = AkshareIngestProvider()
        _mock_ak(
            monkeypatch,
            stock_info_sh_name_code=ConnectionError("sh down"),
            stock_info_sz_name_code=sz_df,
            stock_board_industry_name_em=ConnectionError("em blocked"),
        )
        results = _call_fetch(p, "stock_basic", _payload(D(2026, 8, 14), D(2026, 8, 14)))
        assert not results[0].error
        assert [r[1] for r in results[0].rows] == ["000001"]


class TestCninfoIndustryFallback:
    """SH 行业补全二级降级：东财行业反查封锁 → 巨潮个股资料（stock_profile_cninfo）。"""

    def _sh_sz_frames(self):
        def sh_fn(symbol=None, **kw):
            return pd.DataFrame({
                "证券代码": ["600000"], "证券简称": ["浦发银行"],
                "证券全称": ["浦发银行"], "公司全称": ["上海浦东发展银行股份有限公司"],
                "上市日期": ["1999-11-10"],
            })

        sz_df = pd.DataFrame({
            "板块": ["主板"], "A股代码": ["000001"], "A股简称": ["平安银行"],
            "A股上市日期": ["1991-04-03"], "A股总股本": ["0"], "A股流通股本": ["0"],
            "所属行业": ["J 金融业"],
        })
        return sh_fn, sz_df

    def test_em_blocked_cninfo_fills(self, monkeypatch):
        sh_fn, sz_df = self._sh_sz_frames()

        def profile_fn(symbol=None, **kw):
            return pd.DataFrame({"A股代码": [symbol], "所属行业": ["货币金融服务"]})

        p = AkshareIngestProvider()
        _mock_ak(
            monkeypatch,
            stock_info_sh_name_code=sh_fn,
            stock_info_sz_name_code=sz_df,
            stock_board_industry_name_em=ConnectionError("em blocked"),
            stock_profile_cninfo=profile_fn,
        )
        results = _call_fetch(p, "stock_basic", _payload(D(2026, 8, 14), D(2026, 8, 14)))
        assert not results[0].error
        by = {r[1]: r for r in results[0].rows}
        # SH 行业由巨潮降级补全（口径=巨潮/证监会行业）
        assert by["600000"][4] == "货币金融服务"
        # SZ 仍取交易所清单口径，不受影响
        assert by["000001"][4] == "J 金融业"

    def test_both_sources_fail_empty_not_fatal(self, monkeypatch):
        # 东财+巨潮双源均失败 → industry 留空不致命（次日重试回补）
        sh_fn, sz_df = self._sh_sz_frames()
        p = AkshareIngestProvider()
        _mock_ak(
            monkeypatch,
            stock_info_sh_name_code=sh_fn,
            stock_info_sz_name_code=sz_df,
            stock_board_industry_name_em=ConnectionError("em blocked"),
            stock_profile_cninfo=ConnectionError("cninfo blocked"),
        )
        results = _call_fetch(p, "stock_basic", _payload(D(2026, 8, 14), D(2026, 8, 14)))
        assert not results[0].error
        by = {r[1]: r for r in results[0].rows}
        assert by["600000"][4] == ""
        assert by["000001"][4] == "J 金融业"

    def test_cninfo_consecutive_fail_aborts(self, monkeypatch):
        # 巨潮连续失败 3 次即放弃（快速失败模式，对标 _em_push2_blocked）
        calls: list[str] = []

        def profile_fn(symbol=None, **kw):
            calls.append(symbol)
            raise ConnectionError("cninfo blocked")

        p = AkshareIngestProvider()
        m = _mock_ak(monkeypatch, stock_profile_cninfo=profile_fn)
        policy = MagicMock(rpm=0, max_retries=1, backoff="fixed", initial_wait=0)
        result = p._fetch_cninfo_industry_map(m, policy, {"600000", "600001", "600002", "600003"})
        assert result == {}
        assert len(calls) == 3  # 第 3 次失败后熔断，第 4 个代码不再调用


# ============== index_constituent 四指数+权重 ==============

class TestFetchIndexConstituent:
    def test_four_indexes_with_weight(self, monkeypatch):
        cons_calls: list[str] = []

        def make_cons(code):
            return pd.DataFrame({
                "日期": ["2026-08-14", "2026-08-14"],
                "指数代码": [code, code],
                "指数名称": ["X", "X"],
                "成分券代码": ["000001", "600000"],
                "成分券名称": ["平安银行", "浦发银行"],
                "交易所": ["深圳证券交易所", "上海证券交易所"],
            })

        def cons_fn(symbol=None, **kw):
            cons_calls.append(symbol)
            return make_cons(symbol)

        def weight_fn(symbol=None, **kw):
            return pd.DataFrame({
                "日期": ["2026-07-31", "2026-07-31"],
                "成分券代码": ["000001", "600000"],
                "权重": [0.433, 1.234],
            })

        p = AkshareIngestProvider()
        mock_ak = MagicMock()
        mock_ak.index_stock_cons_csindex = cons_fn
        mock_ak.index_stock_cons_csindex.__name__ = "index_stock_cons_csindex"
        mock_ak.index_stock_cons_weight_csindex = weight_fn
        mock_ak.index_stock_cons_weight_csindex.__name__ = "index_stock_cons_weight_csindex"
        monkeypatch.setitem(sys.modules, "akshare", mock_ak)

        results = _call_fetch(p, "index_constituent", _payload(D(2026, 8, 14), D(2026, 8, 14)))
        assert len(results) == 4  # 每指数一批
        assert cons_calls == ["000300", "000905", "000852", "000985"]
        r0 = results[0]
        assert not r0.error and len(r0.rows) == 2
        # (trade_date, index_code, symbol, weight, action, data_source)
        assert r0.rows[0] == ("2026-08-14", "000300.SH", "000001.SZ", 0.433, "", "akshare_csindex")
        assert r0.rows[1] == ("2026-08-14", "000300.SH", "600000.SH", 1.234, "", "akshare_csindex")
        # 权重接口日期(2026-07-31)不覆盖成分日期(2026-08-14)——PIT 以成分生效日为准
        assert all(row[0] == "2026-08-14" for row in r0.rows)

    def test_weight_failure_degrades_to_zero(self, monkeypatch):
        def cons_fn(symbol=None, **kw):
            return pd.DataFrame({
                "日期": ["2026-08-14"], "指数代码": [symbol], "指数名称": ["X"],
                "成分券代码": ["000001"], "成分券名称": ["平安银行"],
                "交易所": ["深圳证券交易所"],
            })

        p = AkshareIngestProvider()
        mock_ak = MagicMock()
        mock_ak.index_stock_cons_csindex = cons_fn
        mock_ak.index_stock_cons_csindex.__name__ = "index_stock_cons_csindex"
        mock_ak.index_stock_cons_weight_csindex = MagicMock(
            side_effect=ConnectionError("weight down")
        )
        mock_ak.index_stock_cons_weight_csindex.__name__ = "index_stock_cons_weight_csindex"
        monkeypatch.setitem(sys.modules, "akshare", mock_ak)

        results = _call_fetch(p, "index_constituent", _payload(D(2026, 8, 14), D(2026, 8, 14)))
        assert len(results) == 4
        assert all(not r.error for r in results)
        assert results[0].rows[0][3] == 0  # weight 降级为 0


# ============== st_stock_list 科创板扩展 ==============

class TestStStockListCoverage:
    def test_star_market_included(self, monkeypatch):
        seen_args: list[str] = []

        def sh_fn(symbol=None, **kw):
            seen_args.append(symbol)
            if symbol == "科创板":
                return pd.DataFrame({
                    "证券代码": ["688999"], "证券简称": ["*ST科创"],
                    "证券全称": ["x"], "公司全称": ["x"], "上市日期": ["2020-01-01"],
                })
            return pd.DataFrame({
                "证券代码": ["600000"], "证券简称": ["浦发银行"],
                "证券全称": ["x"], "公司全称": ["x"], "上市日期": ["1999-11-10"],
            })

        def sz_fn(symbol=None, **kw):
            return pd.DataFrame({
                "板块": ["主板"], "A股代码": ["000002"], "A股简称": ["ST万宝"],
                "A股上市日期": ["1991-01-29"], "A股总股本": ["0"],
                "A股流通股本": ["0"], "所属行业": ["K 房地产"],
            })

        p = AkshareIngestProvider()
        _mock_ak(
            monkeypatch,
            stock_info_sh_name_code=sh_fn,
            stock_info_sz_name_code=sz_fn,
        )
        results = _call_fetch(p, "st_stock_list", _payload(D(2026, 8, 14), D(2026, 8, 14)))
        assert "科创板" in seen_args  # DS-085 扩展点
        rows = results[0].rows
        st_syms = {r[1]: r[3] for r in rows}
        assert st_syms == {"688999": "*ST", "000002": "ST"}


# ============== suspend 快照+推导 ==============

class TestFetchSuspendStatus:
    def test_em_blocked_baidu_fallback(self, monkeypatch):
        # 新鲜公告（公告日期≤30天、未复牌、源站未标跳过）→ 兜底正常产出
        baidu_df = pd.DataFrame({
            "股票代码": ["688536", "301073"],
            "股票简称": ["思瑞浦", "君亭酒店"],
            "交易所代码": ["SH", "SZ"],
            "停牌时间": ["2026-08-13", "2026-08-14"],
            "复牌时间": [None, None],
            "停牌事项说明": ["拟筹划重大资产重组", "重大事项"],
            "市值": [0, 0], "公告日期": ["2026-08-13", "2026-08-14"],
            "公告时间": ["--", "--"], "证券类型": ["stock", "stock"],
            "市场类型": ["ab", "ab"], "是否跳过": [0, 0],
        })
        p = AkshareIngestProvider()
        _mock_ak(
            monkeypatch,
            stock_zh_a_stop_em=ConnectionError("em blocked"),
            news_trade_notify_suspend_baidu=baidu_df,
        )
        results = _call_fetch(p, "suspend_status", _payload(D(2026, 8, 14), D(2026, 8, 14)))
        assert len(results) == 1 and not results[0].error
        rows = results[0].rows
        assert len(rows) == 2
        # (trade_date, symbol, name, suspend_date, resume_date, reason, data_source)
        assert rows[0][1] == "688536" and rows[0][3] == "2026-08-13"
        assert rows[0][5] == "拟筹划重大资产重组" and rows[0][6] == "akshare_baidu"

    def test_baidu_stale_feed_filtered(self, monkeypatch):
        # 2026-08-15 二审实证：百度 feed 冻结于 2025-11-26（全量公告日期陈旧）。
        # 三重过滤各命中一行：源站是否跳过=1 / 复牌日≤快照日 / 公告>30天——
        # 宁可快照空缺，不写假停牌约束（3 行标的当日 K 线正常交易实证）。
        baidu_df = pd.DataFrame({
            "股票代码": ["688536", "600200", "301073"],
            "股票简称": ["思瑞浦", "退市苏吴", "君亭酒店"],
            "交易所代码": ["SH", "SH", "SZ"],
            "停牌时间": ["2025-11-26", "2025-11-26", "2025-11-26"],
            "复牌时间": [None, "2025-12-09", None],
            "停牌事项说明": ["拟筹划重大资产重组", "重要公告", "重大事项"],
            "公告日期": ["2025-11-26", "2025-11-26", "2025-11-26"],
            "是否跳过": [1, 0, 0],
        })
        p = AkshareIngestProvider()
        _mock_ak(
            monkeypatch,
            stock_zh_a_stop_em=ConnectionError("em blocked"),
            news_trade_notify_suspend_baidu=baidu_df,
        )
        results = _call_fetch(p, "suspend_status", _payload(D(2026, 8, 14), D(2026, 8, 14)))
        assert not results[0].error
        assert results[0].rows == []

    def test_hk_stock_excluded(self, monkeypatch):
        # 港股 5 位代码 zfill 后误撞深主板 00 前缀（联调实证 003389/009929 串入）——
        # 交易所代码列+长度双门禁必须排除
        baidu_df = pd.DataFrame({
            "股票代码": ["03389", "688536"],
            "股票简称": ["亨得利", "思瑞浦"],
            "交易所代码": ["HK", "SH"],
            "停牌时间": ["2025-11-26", "2025-11-26"],
            "复牌时间": [None, None],
            "停牌事项说明": ["短暂停止买卖", "拟筹划重大资产重组"],
        })
        p = AkshareIngestProvider()
        _mock_ak(
            monkeypatch,
            stock_zh_a_stop_em=ConnectionError("em blocked"),
            news_trade_notify_suspend_baidu=baidu_df,
        )
        results = _call_fetch(p, "suspend_status", _payload(D(2026, 8, 14), D(2026, 8, 14)))
        rows = results[0].rows
        assert [r[1] for r in rows] == ["688536"]

    def test_both_sources_fail_empty_not_error(self, monkeypatch):
        p = AkshareIngestProvider()
        _mock_ak(
            monkeypatch,
            stock_zh_a_stop_em=ConnectionError("em blocked"),
            news_trade_notify_suspend_baidu=ConnectionError("baidu blocked"),
        )
        results = _call_fetch(p, "suspend_status", _payload(D(2026, 8, 14), D(2026, 8, 14)))
        assert not results[0].error and results[0].rows == []

    def test_derive_from_kline_gap(self, monkeypatch):
        def fake_query(sql, timeout=0):
            if "DISTINCT trade_date" in sql:
                return "2026-08-10\n2026-08-11\n2026-08-12\n2026-08-13\n"
            if "groupArray" in sql:
                # 600000 全勤；600001 缺 08-11/08-12（中段缺口=停牌）；
                # 600002 尾部缺口（退市或持续停牌，不推导）
                return (
                    "600000\t['2026-08-10','2026-08-11','2026-08-12','2026-08-13']\n"
                    "600001\t['2026-08-10','2026-08-13']\n"
                    "600002\t['2026-08-10','2026-08-11']\n"
                )
            return ""

        _patch_provider_ch(monkeypatch, fake_query)
        p = AkshareIngestProvider()
        _mock_ak(monkeypatch)
        payload = _payload(D(2026, 8, 10), D(2026, 8, 13), extra={"derive_from_kline": True})
        results = _call_fetch(p, "suspend_status", payload)
        assert not results[0].error
        rows = results[0].rows
        derived = {(r[0], r[1]) for r in rows}
        assert derived == {("2026-08-11", "600001"), ("2026-08-12", "600001")}
        assert all(r[6] == "derived_kline_gap" for r in rows)


# ============== 路由完整性 ==============

class TestCapabilityRouting:
    def test_new_capabilities_registered(self):
        caps = {c.capability_id for c in AkshareIngestProvider.meta.capabilities}
        assert {"stock_basic", "stk_limit", "suspend_status"} <= caps

    def test_unknown_capability_error(self):
        p = AkshareIngestProvider()
        results = _call_fetch(p, "no_such_cap", _payload(D(2026, 8, 14), D(2026, 8, 14)))
        assert results[0].error and "unsupported capability" in results[0].error


# ============== 日期规范化空值防御（baidu NaN 实证回归） ==============

class TestNormAkshareDate:
    @pytest.mark.parametrize("val", [float("nan"), "nan", "NaN", "NaT", "None", "--", "", None])
    def test_empty_placeholders(self, val):
        assert AkshareIngestProvider._norm_akshare_date(val) == ""

    @pytest.mark.parametrize("val,expected", [
        ("20260815", "2026-08-15"),
        ("2026-08-15", "2026-08-15"),
        (datetime.date(2026, 8, 15), "2026-08-15"),
        (datetime.datetime(2026, 8, 15, 10, 30), "2026-08-15"),
    ])
    def test_valid_dates(self, val, expected):
        assert AkshareIngestProvider._norm_akshare_date(val) == expected


