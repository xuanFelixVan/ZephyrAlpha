# [BLUEPRINT] MOD-H1_REDIS_HOT | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""us_futures_intraday 能力 + tasks.yaml 登记一致性单元测试（92号清单 §7.1/§7.2，44号备忘 §9.8 通道2/3）。

覆盖：
- 合成新浪 hf 载荷解析（字段映射=评估报告 §五 + akshare futures_hq_sina.py:152-167 交叉确认口径）；
- 主源 3 次连续失败自动切东财兜底（degraded=1 / bid/ask 置 None / data_source=eastmoney_em）；
- 主源+兜底双失败 → FetchResult.error 留痕不抛出；异常/残缺载荷不炸（空行跳过）；
- payload.table 为空 → fail-closed error（禁止凭记忆编表名）；
- tasks.yaml 登记：futures_kline_qmt_incremental 盘中层+主力连续 symbols、
  us_futures_intraday_snapshot 任务字段/schedule 槽位存在/capability 路由+meta 一致。
全部 mock 网络层（_request_sina_hf_quotes / akshare），不触网不触库。
"""

from __future__ import annotations

import datetime
import pathlib
import sys
from unittest.mock import MagicMock

import pandas as pd
import pytest
import yaml

from src.zephyr.data.implementations.akshare_provider import (
    _AKSHARE_CAPABILITIES,
    AkshareIngestProvider,
    parse_sina_hf_futures_quotes,
)
from src.zephyr.data.provider_base import FetchPayload

D = datetime.date  # 简写

# 评估报告 §二实证原始载荷（2026-08-22 周六冻结态）
_SINA_PAYLOAD = (
    'var hq_str_hf_ES="7689.850,,7687.500,7688.000,7714.000,7661.250,04:59:59,7662.500,7669.000,0,37,33,2026-08-22,标普500指数期货,0";\n'
    'var hq_str_hf_NQ="29361.680,,29373.000,29374.000,29539.000,29220.000,04:59:59,29300.500,29327.000,0,1,1,2026-08-22,纳斯达克指数期货,0";\n'
    'var hq_str_hf_CHA50CFD="14824.560,,14818.000,14826.000,14849.000,14808.000,05:05:26,14843.000,14843.000,800082,7,1,2026-08-22,富时中国A50期货,55250";'
)

_CONFIG = pathlib.Path(__file__).resolve().parents[3] / "src" / "zephyr" / "data" / "config"


def _payload(symbols: list[str] | None = None, table: str = "c1_market.us_futures_intraday") -> FetchPayload:
    return FetchPayload(
        table=table,
        symbols=symbols,
        start=D(2026, 8, 22),
        end=D(2026, 8, 22),
        incremental=True,
        extra={"capability": "us_futures_intraday"},
    )


def _policy() -> MagicMock:
    return MagicMock(rpm=0, max_retries=1, backoff="fixed", initial_wait=0)


@pytest.fixture()
def provider(monkeypatch):
    """零等待重试（生产常量 2s×2，测试提速）。"""
    monkeypatch.setattr(
        "src.zephyr.data.implementations.akshare_provider._US_FUTURES_RETRY_WAIT_SEC",
        0,
    )
    return AkshareIngestProvider()


def _mock_ak(monkeypatch, **attrs) -> MagicMock:
    """构造 akshare 模块 mock。"""
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


def _em_spot_df() -> pd.DataFrame:
    """构造 futures_global_spot_em 形态 DataFrame（列名=akshare futures_hf_em.py 实证）。"""
    return pd.DataFrame(
        [
            {"代码": "ES00Y", "名称": "小型标普500当月连续", "最新价": 7690.86, "今开": 7669.0, "最高": 7714.0, "最低": 7661.25, "昨结": 7662.5, "持仓量": 0},
            {"代码": "NQ00Y", "名称": "小型纳指当月连续", "最新价": 29358.83, "今开": 29327.0, "最高": 29539.0, "最低": 29220.0, "昨结": 29300.5, "持仓量": 0},
            {"代码": "CN00Y", "名称": "A50期指当月连续", "最新价": 14826.0, "今开": 14843.0, "最高": 14849.0, "最低": 14808.0, "昨结": 14843.0, "持仓量": 800082},
            {"代码": "CL00Y", "名称": "WTI原油当月连续", "最新价": 86.64, "今开": 86.0, "最高": 87.0, "最低": 85.5, "昨结": 86.1, "持仓量": 100},
        ]
    )


class TestSinaHfParse:
    def test_field_mapping(self):
        quotes = parse_sina_hf_futures_quotes(_SINA_PAYLOAD)
        assert set(quotes) == {"ES", "NQ", "CHA50CFD"}
        es = quotes["ES"]
        assert es["last_price"] == 7689.85
        assert es["bid"] == 7687.5
        assert es["ask"] == 7688.0
        assert es["high"] == 7714.0
        assert es["low"] == 7661.25
        assert es["quote_time"] == "04:59:59"
        assert es["prev_settle"] == 7662.5
        assert es["open"] == 7669.0
        assert es["open_interest"] == 0
        assert es["quote_date"] == "2026-08-22"
        assert es["name_cn"] == "标普500指数期货"
        assert quotes["CHA50CFD"]["open_interest"] == 800082

    def test_malformed_lines_skipped(self):
        # 空串 / 无等号行 / 字段不足 14 列行 / 空载荷 hf_CHA50（评估报告 §二：hf_CHA50 返回空串）
        text = (
            'var hq_str_hf_CHA50="";\n'
            "garbage line without equals\n"
            'var hq_str_hf_ES="7689.850,,7687.500,7688.000,7714.000,7661.250,04:59:59,7662.500,7669.000,0,37,33,2026-08-22,标普500指数期货,0";'
        )
        quotes = parse_sina_hf_futures_quotes(text)
        assert set(quotes) == {"ES"}

    def test_empty_payload(self):
        assert parse_sina_hf_futures_quotes("") == {}
        assert parse_sina_hf_futures_quotes("\n\n;") == {}


class TestUsFuturesIntradayFetch:
    def test_main_source_rows(self, provider, monkeypatch):
        monkeypatch.setattr(provider, "_request_sina_hf_quotes", lambda symbols: parse_sina_hf_futures_quotes(_SINA_PAYLOAD))
        results = list(provider._fetch_us_futures_intraday(_payload(), _policy()))
        assert len(results) == 1
        res = results[0]
        assert res.error is None
        assert len(res.rows) == 3
        es = next(r for r in res.rows if r[2] == "ES")
        # 列序 = _US_FUTURES_COLUMNS: trade_date/timestamp/symbol/last_price/bid/ask/open/high/low/prev_settle/open_interest/name_cn/data_source/degraded
        assert es[0] == "2026-08-22"
        assert es[1] == "2026-08-22 04:59:59"
        assert es[3] == 7689.85
        assert es[4] == 7687.5 and es[5] == 7688.0
        assert es[9] == 7662.5
        assert es[12] == "sina_hf"
        assert es[13] == 0

    def test_fallback_after_3_failures(self, provider, monkeypatch):
        calls = {"n": 0}

        def _raise(symbols):
            calls["n"] += 1
            raise ConnectionError("sina hf unreachable")

        monkeypatch.setattr(provider, "_request_sina_hf_quotes", _raise)
        _mock_ak(monkeypatch, futures_global_spot_em=_em_spot_df())
        results = list(provider._fetch_us_futures_intraday(_payload(), _policy()))
        assert calls["n"] == 3  # 连续 3 次失败才切兜底
        assert len(results) == 1
        res = results[0]
        assert res.error is None
        assert len(res.rows) == 3  # CL00Y 不在默认品种表，被过滤
        for r in res.rows:
            assert r[12] == "eastmoney_em"
            assert r[13] == 1  # degraded 标记
            assert r[4] is None and r[5] is None  # 东财买卖盘为量非价，bid/ask 置 None
        es = next(r for r in res.rows if r[2] == "ES")
        assert es[3] == 7690.86
        assert es[9] == 7662.5

    def test_double_failure_yields_error_not_raise(self, provider, monkeypatch):
        monkeypatch.setattr(
            provider,
            "_request_sina_hf_quotes",
            MagicMock(side_effect=ConnectionError("sina down")),
        )
        _mock_ak(monkeypatch, futures_global_spot_em=ConnectionError("em down"))
        results = list(provider._fetch_us_futures_intraday(_payload(), _policy()))
        assert len(results) == 1
        assert results[0].error is not None
        assert "双失败" in results[0].error

    def test_unparseable_main_source_counts_as_failure(self, provider, monkeypatch):
        # 主源返回残缺载荷（无可解析行）→ 计失败；3 次后切兜底
        monkeypatch.setattr(provider, "_request_sina_hf_quotes", lambda symbols: {})
        _mock_ak(monkeypatch, futures_global_spot_em=_em_spot_df())
        results = list(provider._fetch_us_futures_intraday(_payload(), _policy()))
        assert results[0].rows[0][13] == 1

    def test_empty_table_fail_closed(self, provider):
        results = list(provider._fetch_us_futures_intraday(_payload(table=""), _policy()))
        assert len(results) == 1
        assert results[0].error is not None
        assert "table" in results[0].error

    def test_default_symbols_when_null(self, provider, monkeypatch):
        captured = {}

        def _capture(symbols):
            captured["symbols"] = symbols
            return parse_sina_hf_futures_quotes(_SINA_PAYLOAD)

        monkeypatch.setattr(provider, "_request_sina_hf_quotes", _capture)
        list(provider._fetch_us_futures_intraday(_payload(symbols=None), _policy()))
        assert captured["symbols"] == ["ES", "NQ", "CHA50CFD"]


class TestTasksYamlRegistration:
    def _load_tasks(self) -> list[dict]:
        doc = yaml.safe_load((_CONFIG / "tasks.yaml").read_text(encoding="utf-8"))
        return doc["tasks"]

    def test_futures_kline_qmt_intraday_config(self):
        task = next(t for t in self._load_tasks() if t["task_id"] == "futures_kline_qmt_incremental")
        assert task["schedule"] == "intraday_realtime"
        assert task["symbols"] == ["IF00.IF", "IC00.IF", "IM00.IF", "IH00.IF"]
        assert task["capability"] == "futures_kline_qmt"

    def test_us_futures_task_fields(self):
        task = next(t for t in self._load_tasks() if t["task_id"] == "us_futures_intraday_snapshot")
        assert task["table"] == "c1_market.us_futures_intraday"
        assert task["source"] == "akshare"
        assert task["schedule"] == "intraday_realtime"
        assert task["capability"] == "us_futures_intraday"
        assert task["incremental"] is True

    def test_schedule_slot_exists(self):
        doc = yaml.safe_load((_CONFIG / "schedule.yaml").read_text(encoding="utf-8"))
        assert "intraday_realtime" in doc["schedules"]

    def test_capability_route_and_meta(self):
        assert "us_futures_intraday" in _AKSHARE_CAPABILITIES
        caps = {c.capability_id for c in AkshareIngestProvider.meta.capabilities}
        assert "us_futures_intraday" in caps

    def test_route_meta_consistency_gate(self):
        """commit gate 同款校验：fetch 路由能力集与 meta.capabilities 声明集一致。"""
        from src.zephyr.data.capability_validator import check_route_meta_consistency

        provider_path = (
            pathlib.Path(__file__).resolve().parents[3]
            / "src"
            / "zephyr"
            / "data"
            / "implementations"
            / "akshare_provider.py"
        )
        assert check_route_meta_consistency(provider_path) == []

    def test_ddl_schema_registered_in_apply_script(self):
        """新表 DDL 真源文件存在且已注册进 apply_market_tables_ddl 表清单。"""
        root = pathlib.Path(__file__).resolve().parents[3]
        schema_file = root / "schemas" / "categories" / "market_us_futures_intraday.py"
        assert schema_file.is_file()
        ns: dict = {}
        exec(schema_file.read_text(encoding="utf-8"), ns)  # noqa: S102 — 测试内读取 DDL 常量
        assert ns["TABLE_NAME"] == "us_futures_intraday"
        assert ns["DATABASE"] == "c1_market"
        assert "ReplacingMergeTree" in ns["US_FUTURES_INTRADAY_DDL"]
        apply_src = (root / "scripts" / "ch" / "apply_market_tables_ddl.py").read_text(encoding="utf-8")
        assert "us_futures_intraday" in apply_src
