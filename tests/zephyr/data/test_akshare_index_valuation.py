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
    _INDEX_VALUATION_COLUMNS,
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


@pytest.fixture(autouse=True)
def _stub_ch_reader(monkeypatch):
    """默认屏蔽 CH 只读探值——写前携带/续跑预查都走 ch_reader，单测禁触库。"""
    from zephyr.data import ch_reader

    monkeypatch.setattr(ch_reader, "query", lambda *a, **k: "")


class TestIndexValuationDailyFetch:
    """index_valuation_daily 采集能力测试（S2 路A 主源）。"""

    def test_normal_mapping(self, monkeypatch):
        """正常行：中证官网历史K线 → PE_TTM/股息率映射。"""
        df = pd.DataFrame(
            {
                "日期": [D(2026, 8, 27), D(2026, 8, 28)],
                "指数代码": ["000300", "000300"],
                "收盘": [4630.28, 4609.18],
                "滚动市盈率": [14.44, 14.42],
                "股息率1": [2.52, 2.52],
            }
        )
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
        df = pd.DataFrame(
            {
                "日期": [D(2010, 1, 4), D(2010, 1, 5)],
                "指数代码": ["000300", "000300"],
                "收盘": [3535.23, 3564.04],
                "滚动市盈率": [None, 15.0],
                "股息率1": [None, 2.0],
            }
        )
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
        df = pd.DataFrame(
            {
                "日期": [D(2026, 8, 28)],
                "指数代码": ["000300"],
                "收盘": [4609.18],
                "滚动市盈率": [14.42],
                "股息率1": [2.52],
            }
        )
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


class TestValuationCarryForward:
    """BRK-034/BRK-043 止血：写前派生值携带 + 断点续跑完成键预查（2026-09-18 datagap 车道）。

    病灶实证：index_valuation_daily 2026-09-13 全史重采 8111 行把 internal_compute 回写的
    cape/分位/ERP 抹成 NULL（无 version 列 ReplacingMergeTree，后到的 None 版本胜出）。
    本组测试是"改回旧行为必红"的钉：删除携带逻辑或改成无条件覆盖都会红。
    """

    def test_parse_tsv_skips_null_sentinels(self):
        from src.zephyr.data.implementations.akshare_provider import _parse_preserved_tsv

        cols = ("cape_5y", "pe_pct")
        null = chr(92) + "N"  # ClickHouse TSV 的 NULL 哨兵（chr(92) 拼写避转义歧义）
        tsv = "\n".join(
            (
                "\t".join(("000300", "2026-08-28", "28.4", "0.91")),
                "\t".join(("000300", "2026-08-27", null, null)),
                "\t".join(("000905", "2026-08-27", "12.1", null)),
            )
        )
        parsed = _parse_preserved_tsv(tsv, cols)
        assert parsed[("000300", "2026-08-28")] == {"cape_5y": "28.4", "pe_pct": "0.91"}
        assert ("000300", "2026-08-27") not in parsed  # 全 NULL 不算既有值
        assert parsed[("000905", "2026-08-27")] == {"cape_5y": "12.1"}

    def test_apply_preserved_keeps_own_non_null_values(self):
        from src.zephyr.data.implementations.akshare_provider import (
            _INDEX_VALUATION_COLUMNS,
            _apply_preserved_values,
        )

        positions = {c: i for i, c in enumerate(_INDEX_VALUATION_COLUMNS)}
        row = [None] * len(_INDEX_VALUATION_COLUMNS)
        row[positions["pe_ttm"]] = 14.42  # 本能力自采值
        row[positions["pb_mrq"]] = 1.11  # 既有非 None 槽位（本批也采到值）
        _apply_preserved_values(
            row, positions, {"cape_5y": "28.4", "pb_mrq": "9.99", "erp": "5.1"}
        )
        assert row[positions["cape_5y"]] == 28.4  # None → 携带
        assert row[positions["erp"]] == 5.1
        assert row[positions["pb_mrq"]] == 1.11  # 已有值不被库中旧值覆盖
        assert row[positions["pe_ttm"]] == 14.42

    def test_full_refresh_carries_forward_computed_columns(self, monkeypatch):
        """全史重采后 cape/pe_pct 必须仍在（旧行为=抹成 None→整表派生列归零）。"""
        from zephyr.data import ch_reader

        df = pd.DataFrame(
            {
                "日期": [D(2026, 8, 27), D(2026, 8, 28)],
                "指数代码": ["000300", "000300"],
                "收盘": [4630.28, 4609.18],
                "滚动市盈率": [14.44, 14.42],
                "股息率1": [2.52, 2.52],
            }
        )
        _mock_ak(monkeypatch, stock_zh_index_hist_csindex=df)
        captured: list[str] = []

        def fake_query(sql: str, timeout: int = 0) -> str:
            captured.append(sql)
            null = chr(92) + "N"
            rows = (
                ("000300", "2026-08-28", "1.62", "31.05", "0.9871", "0.95",
                 null, "5.31", "0.72", null, null),
                ("000300", "2026-08-27", "1.61", "30.90", "0.9860", "0.94",
                 null, "5.28", "0.71", null, null),
            )
            return "\n".join("\t".join(r) for r in rows)

        monkeypatch.setattr(ch_reader, "query", fake_query)
        provider = AkshareIngestProvider()
        results = _call_fetch(
            provider,
            "index_valuation_daily",
            _payload(D(2010, 1, 1), D(2026, 8, 28), symbols=["000300"], incremental=False),
        )
        assert len(results) == 1 and not results[0].error
        rows = results[0].rows
        assert len(rows) == 2
        pos = {c: i for i, c in enumerate(_INDEX_VALUATION_COLUMNS)}
        assert rows[-1][pos["cape_5y"]] == 31.05
        assert rows[-1][pos["cape_5y_pct"]] == 0.9871
        assert rows[-1][pos["pe_pct"]] == 0.95
        assert rows[-1][pos["erp"]] == 5.31
        assert rows[-1][pos["pe_ttm"]] == pytest.approx(14.42)  # 自采值优先
        assert rows[-1][pos["dividend_yield"]] == pytest.approx(2.52)
        assert rows[-1][pos["data_source"]] == "akshare_csindex"
        # 探值 SQL 三要素：FINAL 去双版本 + 只读非默认行 + 按 symbol 收窄
        assert len(captured) == 1
        assert "FINAL" in captured[0]
        assert "cape_5y IS NOT NULL" in captured[0]
        assert "'000300'" in captured[0]

    def test_empty_db_yields_unchanged_rows(self, monkeypatch):
        """库中无可携带值（autouse 桩恒返空串）→ 计算列保持 None，且行为可回退。"""
        df = pd.DataFrame(
            {
                "日期": [D(2026, 8, 28)],
                "指数代码": ["000300"],
                "收盘": [4609.18],
                "滚动市盈率": [14.42],
                "股息率1": [2.52],
            }
        )
        _mock_ak(monkeypatch, stock_zh_index_hist_csindex=df)
        provider = AkshareIngestProvider()
        results = _call_fetch(
            provider,
            "index_valuation_daily",
            _payload(D(2026, 8, 28), D(2026, 8, 28), symbols=["000300"]),
        )
        rows = results[0].rows
        pos = {c: i for i, c in enumerate(_INDEX_VALUATION_COLUMNS)}
        assert rows[0][pos["cape_5y"]] is None
        assert rows[0][pos["pe_ttm"]] == pytest.approx(14.42)

    def test_resume_skip_reads_complete_symbols(self, monkeypatch):
        """续跑预查：TSV 标的名单 → 集合；查询异常 → 空集（降级全量重拉）。"""
        from src.zephyr.data.implementations.akshare_provider import (
            _TBL_DAILY_VALUATION,
        )
        from zephyr.data import ch_reader

        calls: list[str] = []

        def fake_query(sql: str, timeout: int = 0) -> str:
            calls.append(sql)
            return "000001\n000002\n\n600000"

        monkeypatch.setattr(ch_reader, "query", fake_query)
        provider = AkshareIngestProvider()
        done = provider._load_valuation_complete_symbols(
            _TBL_DAILY_VALUATION, "2026-08-01", "2026-09-17"
        )
        assert done == {"000001", "000002", "600000"}
        assert "toFloat64(pe_ttm) > 0" in calls[0]
        assert "max(trade_date)" in calls[0]

        def broken_query(sql: str, timeout: int = 0) -> str:
            raise RuntimeError("CH 不可达")

        monkeypatch.setattr(ch_reader, "query", broken_query)
        assert provider._load_valuation_complete_symbols(_TBL_DAILY_VALUATION, "a", "b") == set()

    def test_preserve_query_failure_degrades(self, monkeypatch):
        """探值读失败=降级为不携带（fail-open 于可用性，但绝不阻断采集）。"""
        from src.zephyr.data.implementations.akshare_provider import (
            _INDEX_VALUATION_PRESERVE_SPEC,
        )
        from zephyr.data import ch_reader

        def broken(sql: str, timeout: int = 0) -> str:
            raise RuntimeError("CH 不可达")

        monkeypatch.setattr(ch_reader, "query", broken)
        provider = AkshareIngestProvider()
        assert provider._load_preserved_valuation_values(
            _INDEX_VALUATION_PRESERVE_SPEC, ["000300"], "2026-08-27", "2026-08-28"
        ) == {}
