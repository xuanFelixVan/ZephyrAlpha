# [BLUEPRINT] MOD-L00-004 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""forex_daily 能力（离岸人民币 USDCNH 日K，GAP-F-23 2026-10-01 挖矿翻案）单元测试。

覆盖：
- parse_sina_forex_day_kline JSONP 解析（mock 样本，禁真连网）；
- 字段序重排：源 (date,open,close,high,low) → 表列 trade_date/symbol/open/high/low/close；
- 离岸码绑定：_FOREX_SINA_SYMBOL_MAP 绑死 fx_susdcnh，未知/在岸 fx_susdcny 拒绝；
- 本地窗口过滤 / payload.table 空 fail-closed / 健康探针失败与抓取失败 error 留痕不抛出；
- check_sina_forex_realtime_health 口径标签+日期容差判定；
- tasks.yaml global_usdcnh_daily_incremental 登记一致性与 foreign_market_coverage 探针接线。
全部 mock requests，不触网不触库。
"""

from __future__ import annotations

import datetime
import pathlib
import sys
from unittest.mock import MagicMock

from src.zephyr.data.foreign_market_coverage import FOREIGN_WATCHLIST
from src.zephyr.data.implementations.akshare_provider import (
    _AKSHARE_CAPABILITIES,
    _FOREX_DAILY_COLUMNS,
    _FOREX_SINA_SYMBOL_MAP,
    AkshareIngestProvider,
    check_sina_forex_realtime_health,
    parse_sina_forex_day_kline,
)
from src.zephyr.data.provider_base import FetchPayload

D = datetime.date  # 简写

_CONFIG = pathlib.Path(__file__).resolve().parents[3] / "src" / "zephyr" / "data" / "config"

_TODAY = D(2026, 10, 1)

# mock JSONP 样本（形态按 2026-10-01 实测：首段表头、记录按 | 分隔、字段序 date,open,close,high,low）
_JSONP_SAMPLE = (
    'var t=("date,open,close,high,low,'
    "|2014-11-07,6.1126,6.1135,6.1153,6.1105,"
    "|2016-01-07,6.5920,6.6587,6.7585,6.5890,"  # CNH 恐慌日（离岸特征行）
    '|2026-09-29,6.7103,6.7080,6.7119,6.7042")'
)

_PROBE_OK = (
    'var hq_str_fx_susdcnh="6.7092,6.7095,6.7089,6.7101,6.7080,6.7102,6.7078,'
    '30614,6.7096,6.7106,2026-10-01,01:55:03,0,1,离岸人民币（香港）,USDCNH,0";'
)


_START_DEFAULT = D(2014, 11, 7)  # B008：默认值禁函数调用，用模块级单例
_END_DEFAULT = D(2026, 9, 29)


def _payload(
    table: str = "c1_market.kline_global",
    start: D = _START_DEFAULT,
    end: D = _END_DEFAULT,
    symbols: list[str] | None = None,
) -> FetchPayload:
    return FetchPayload(
        table=table,
        symbols=symbols,
        start=start,
        end=end,
        incremental=True,
        extra={"capability": "forex_daily"},
    )


def _policy() -> MagicMock:
    return MagicMock(rpm=0, max_retries=1, backoff="fixed", initial_wait=0)


class _FakeResponse:
    def __init__(self, text: str = "", content: bytes | None = None, status: int = 200):
        self._text = text
        self.content = content if content is not None else text.encode("utf-8")
        self.status_code = status

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")

    @property
    def text(self) -> str:
        return self._text


def _mock_requests(monkeypatch, daykline_text: str, probe_content: bytes | None = None):
    """构造 requests 模块 mock：探针走 GBK 字节，日K走 JSONP 文本。"""
    import json

    def fake_get(url, timeout=0, headers=None):  # noqa: ARG001
        if "hq.sinajs.cn" in url:
            return _FakeResponse(content=probe_content if probe_content is not None else _PROBE_OK.encode("gbk"))
        return _FakeResponse(text=daykline_text)

    mock_rq = MagicMock()
    mock_rq.get = fake_get
    mock_rq.exceptions = json.loads  # 占位，避免 MagicMock 属性链报错
    monkeypatch.setitem(sys.modules, "requests", mock_rq)
    return mock_rq


class TestParseSinaForexDayKline:
    def test_jsonp_parse_and_field_order(self):
        records = parse_sina_forex_day_kline(_JSONP_SAMPLE)
        assert len(records) == 3
        # 源字段序 (date,open,close,high,low)：close=6.6587 落 close，high=6.7585 落 high
        panic = records[1]
        assert panic["date"] == "2016-01-07"
        assert panic["open"] == 6.5920
        assert panic["close"] == 6.6587
        assert panic["high"] == 6.7585
        assert panic["low"] == 6.5890

    def test_non_jsonp_garbage_returns_empty(self):
        assert parse_sina_forex_day_kline("Not Found") == []
        assert parse_sina_forex_day_kline("") == []

    def test_bad_records_skipped(self):
        dirty = (
            'var t=("date,open,close,high,low,'
            "|2026-01-05,6.50,6.51,6.52,6.49,"
            "|not-a-date,6.50,6.51,6.52,6.49,"  # 坏日期
            "|2026-01-07,6.50,abc,6.52,6.49"  # 坏数值
            '")'
        )
        records = parse_sina_forex_day_kline(dirty)
        assert [r["date"] for r in records] == ["2026-01-05"]


class TestSinaForexRealtimeHealth:
    def test_probe_ok_offshore_label_and_fresh_date(self):
        assert check_sina_forex_realtime_health(_PROBE_OK, today=_TODAY) is True

    def test_missing_offshore_label_rejected(self):
        text = _PROBE_OK.replace("离岸人民币（香港）", "人民币")
        assert check_sina_forex_realtime_health(text, today=_TODAY) is False

    def test_stale_quote_rejected(self):
        assert check_sina_forex_realtime_health(_PROBE_OK, today=D(2026, 10, 25)) is False

    def test_no_date_rejected(self):
        assert check_sina_forex_realtime_health("离岸人民币（香港）", today=_TODAY) is False


class TestForexDailyFetch:
    def test_row_mapping_and_offshore_symbol_binding(self, monkeypatch):
        _mock_requests(monkeypatch, _JSONP_SAMPLE)
        provider = AkshareIngestProvider()
        results = list(provider._fetch_forex_daily(_payload(), _policy()))
        assert len(results) == 1
        res = results[0]
        assert res.error is None
        assert len(res.rows) == 3
        row = res.rows[0]
        # 列序 = INSERT_COLUMNS 9 列：trade_date/symbol/open/high/low/close/volume/oi/data_source
        assert tuple(_FOREX_DAILY_COLUMNS) == (
            "trade_date",
            "symbol",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "open_interest",
            "data_source",
        )
        assert row[0] == "2014-11-07"
        assert row[1] == "USDCNH"
        assert row[2] == 6.1126  # open
        assert row[3] == 6.1153  # high（源列 4）
        assert row[4] == 6.1105  # low（源列 5）
        assert row[5] == 6.1135  # close（源列 3——重排正确性）
        assert row[6] == 0 and row[7] == 0
        assert row[8] == "sina_forex"
        # 首尾行=全量窗口边界
        assert res.rows[-1][0] == "2026-09-29"

    def test_incremental_window_filter(self, monkeypatch):
        _mock_requests(monkeypatch, _JSONP_SAMPLE)
        provider = AkshareIngestProvider()
        results = list(provider._fetch_forex_daily(_payload(start=D(2016, 1, 1), end=D(2016, 12, 31)), _policy()))
        rows = results[0].rows
        assert [r[0] for r in rows] == ["2016-01-07"]

    def test_unknown_onshore_symbol_rejected(self, monkeypatch):
        _mock_requests(monkeypatch, _JSONP_SAMPLE)
        provider = AkshareIngestProvider()
        results = list(provider._fetch_forex_daily(_payload(symbols=["USDCNY"]), _policy()))
        assert len(results) == 1
        assert results[0].error is not None
        assert "fx_susdcny" in results[0].error
        assert results[0].rows == []

    def test_symbol_map_binds_offshore_code(self):
        assert _FOREX_SINA_SYMBOL_MAP == {"USDCNH": "fx_susdcnh"}
        assert "fx_susdcny" not in _FOREX_SINA_SYMBOL_MAP.values()

    def test_empty_table_fail_closed(self):
        provider = AkshareIngestProvider()
        results = list(provider._fetch_forex_daily(_payload(table=""), _policy()))
        assert len(results) == 1
        assert results[0].error is not None
        assert "table" in results[0].error

    def test_probe_failure_yields_error_not_raise(self, monkeypatch):
        _mock_requests(monkeypatch, _JSONP_SAMPLE, probe_content="人民币".encode("gbk"))  # 缺离岸标签
        provider = AkshareIngestProvider()
        results = list(provider._fetch_forex_daily(_payload(), _policy()))
        assert len(results) == 1
        assert results[0].error is not None
        assert "健康探针" in results[0].error

    def test_daykline_http_failure_yields_error_not_raise(self, monkeypatch):
        def fake_get(url, timeout=0, headers=None):  # noqa: ARG001
            if "hq.sinajs.cn" in url:
                return _FakeResponse(content=_PROBE_OK.encode("gbk"))
            raise ConnectionError("sina down")

        mock_rq = MagicMock()
        mock_rq.get = fake_get
        monkeypatch.setitem(sys.modules, "requests", mock_rq)
        provider = AkshareIngestProvider()
        results = list(provider._fetch_forex_daily(_payload(), _policy()))
        assert len(results) == 1
        assert results[0].error is not None
        assert "getDayKLine" in results[0].error


class TestTasksYamlAndCoverageWiring:
    """tasks.yaml 登记一致性 + foreign_market_coverage 探针接线。"""

    def _load_tasks(self) -> list[dict]:
        import yaml

        doc = yaml.safe_load((_CONFIG / "tasks.yaml").read_text(encoding="utf-8"))
        return doc["tasks"]

    def test_usdcnh_task_fields(self):
        task = next(t for t in self._load_tasks() if t["task_id"] == "global_usdcnh_daily_incremental")
        assert task["table"] == "c1_market.kline_global"
        assert task["source"] == "akshare"
        assert task["schedule"] == "daily_kline"
        assert task["capability"] == "forex_daily"
        assert task["symbols"] == ["USDCNH"]
        assert task["incremental"] is True
        assert task["fallback_sources"] == []
        assert not task.get("extra", {}).get("disabled")  # 2026-10-01 有源后启用

    def test_capability_route_and_meta(self):
        assert "forex_daily" in _AKSHARE_CAPABILITIES
        caps = {c.capability_id for c in AkshareIngestProvider.meta.capabilities}
        assert "forex_daily" in caps

    def test_route_meta_consistency_gate(self):
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

    def test_usdcnh_probe_spec_wired(self):
        target = next(t for t in FOREIGN_WATCHLIST if t.key == "usdcnh")
        assert len(target.probes) == 1
        spec = target.probes[0]
        assert spec.table == "c1_market.kline_global"
        assert spec.symbols == ("USDCNH",)
