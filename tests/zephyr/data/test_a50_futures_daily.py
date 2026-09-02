# [BLUEPRINT] MOD-L00-004 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""a50_futures_daily 能力 + 期指 tick 任务 + tasks.yaml 登记一致性单元测试（A22，44号备忘 §9.6 通道1/§9.8 通道2）。

覆盖：
- _fetch_a50_futures_daily 行映射（futures_foreign_hist 列 date/open/high/low/close/volume/position →
  表列序 trade_date/symbol/OHLC/volume/open_interest/data_source）；
- 增量日期窗过滤（payload.start/end）；
- payload.table 为空 → fail-closed error（禁止凭记忆编表名）；
- 接口异常 → FetchResult.error 留痕不抛出；
- tasks.yaml 登记：a50_futures_daily_incremental（pre_market 盘前层）与
  futures_tick_intraday（intraday_realtime 盘中层，IF/IC/IM/IH 主力连续 tick）字段一致性；
- schema DDL 真源文件存在且已注册进 apply_market_tables_ddl 清单。
全部 mock akshare，不触网不触库。
"""

from __future__ import annotations

import datetime
import pathlib
import sys
from unittest.mock import MagicMock

import pandas as pd

from src.zephyr.data.implementations.akshare_provider import (
    _AKSHARE_CAPABILITIES,
    AkshareIngestProvider,
)
from src.zephyr.data.provider_base import FetchPayload

D = datetime.date  # 简写

_CONFIG = pathlib.Path(__file__).resolve().parents[3] / "src" / "zephyr" / "data" / "config"


def _payload(
    table: str = "c1_market.a50_futures_daily",
    start: D = D(2026, 8, 1),
    end: D = D(2026, 8, 29),
) -> FetchPayload:
    return FetchPayload(
        table=table,
        symbols=None,
        start=start,
        end=end,
        incremental=True,
        extra={"capability": "a50_futures_daily"},
    )


def _policy() -> MagicMock:
    return MagicMock(rpm=0, max_retries=1, backoff="fixed", initial_wait=0)


def _hist_df() -> pd.DataFrame:
    """构造 futures_foreign_hist 形态 DataFrame（列名=2026-08-29 实证口径）。"""
    return pd.DataFrame(
        [
            {
                "date": pd.Timestamp("2026-07-31"),
                "open": 14700.0,
                "high": 14750.0,
                "low": 14680.0,
                "close": 14720.0,
                "volume": 280000,
                "position": 780000,
                "s": 0,
            },
            {
                "date": pd.Timestamp("2026-08-28"),
                "open": 14729.0,
                "high": 14795.0,
                "low": 14648.0,
                "close": 14706.0,
                "volume": 295132,
                "position": 781522,
                "s": 0,
            },
            {
                "date": pd.Timestamp("2026-08-29"),
                "open": 14706.0,
                "high": 14738.0,
                "low": 14657.0,
                "close": 14662.0,
                "volume": 52121,
                "position": 781522,
                "s": 0,
            },
        ]
    )


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


class TestA50FuturesDailyFetch:
    def test_row_mapping(self, monkeypatch):
        _mock_ak(monkeypatch, futures_foreign_hist=_hist_df())
        provider = AkshareIngestProvider()
        results = list(provider._fetch_a50_futures_daily(_payload(), _policy()))
        assert len(results) == 1
        res = results[0]
        assert res.error is None
        # 窗口 [2026-08-01, 2026-08-29]：07-31 行被过滤
        assert len(res.rows) == 2
        # 列序 = _A50_FUTURES_COLUMNS: trade_date/symbol/open/high/low/close/volume/open_interest/data_source
        row = res.rows[0]
        assert row[0] == "2026-08-28"
        assert row[1] == "CHA50CFD"
        assert row[2] == 14729.0
        assert row[5] == 14706.0
        assert row[6] == 295132
        assert row[7] == 781522
        assert row[8] == "akshare_sina"

    def test_incremental_window_filter(self, monkeypatch):
        _mock_ak(monkeypatch, futures_foreign_hist=_hist_df())
        provider = AkshareIngestProvider()
        results = list(provider._fetch_a50_futures_daily(_payload(start=D(2026, 8, 29)), _policy()))
        assert len(results[0].rows) == 1
        assert results[0].rows[0][0] == "2026-08-29"

    def test_empty_table_fail_closed(self):
        provider = AkshareIngestProvider()
        results = list(provider._fetch_a50_futures_daily(_payload(table=""), _policy()))
        assert len(results) == 1
        assert results[0].error is not None
        assert "table" in results[0].error

    def test_api_failure_yields_error_not_raise(self, monkeypatch):
        _mock_ak(monkeypatch, futures_foreign_hist=ConnectionError("sina down"))
        provider = AkshareIngestProvider()
        results = list(provider._fetch_a50_futures_daily(_payload(), _policy()))
        assert len(results) == 1
        assert results[0].error is not None
        assert "futures_foreign_hist" in results[0].error


class TestTasksYamlRegistrationA22:
    """A22 两项任务的 tasks.yaml 登记一致性。"""

    def _load_tasks(self) -> list[dict]:
        import yaml

        doc = yaml.safe_load((_CONFIG / "tasks.yaml").read_text(encoding="utf-8"))
        return doc["tasks"]

    def test_futures_tick_intraday_config(self):
        task = next(t for t in self._load_tasks() if t["task_id"] == "futures_tick_intraday")
        assert task["table"] == "c1_market.tick_data"
        assert task["source"] == "miniqmt"
        assert task["schedule"] == "intraday_realtime"
        assert task["capability"] == "tick_data"
        assert task["symbols"] == ["IF00.IF", "IC00.IF", "IM00.IF", "IH00.IF"]
        assert task["incremental"] is True
        assert task["fallback_sources"] == []

    def test_a50_futures_daily_task_fields(self):
        task = next(t for t in self._load_tasks() if t["task_id"] == "a50_futures_daily_incremental")
        assert task["table"] == "c1_market.a50_futures_daily"
        assert task["source"] == "akshare"
        assert task["schedule"] == "pre_market"
        assert task["capability"] == "a50_futures_daily"
        assert task["incremental"] is True
        assert task["fallback_sources"] == []

    def test_schedule_slots_exist(self):
        import yaml

        doc = yaml.safe_load((_CONFIG / "schedule.yaml").read_text(encoding="utf-8"))
        assert "pre_market" in doc["schedules"]
        assert "intraday_realtime" in doc["schedules"]

    def test_capability_route_and_meta(self):
        assert "a50_futures_daily" in _AKSHARE_CAPABILITIES
        caps = {c.capability_id for c in AkshareIngestProvider.meta.capabilities}
        assert "a50_futures_daily" in caps

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
        schema_file = root / "schemas" / "categories" / "market_a50_futures_daily.py"
        assert schema_file.is_file()
        ns: dict = {}
        exec(schema_file.read_text(encoding="utf-8"), ns)  # noqa: S102 — 测试内读取 DDL 常量
        assert ns["TABLE_NAME"] == "a50_futures_daily"
        assert ns["DATABASE"] == "c1_market"
        assert "ReplacingMergeTree" in ns["A50_FUTURES_DAILY_DDL"]
        apply_src = (root / "scripts" / "ch" / "apply_market_tables_ddl.py").read_text(encoding="utf-8")
        assert "A50_FUTURES_DAILY_DDL" in apply_src
        assert '"a50_futures_daily": "ReplacingMergeTree"' in apply_src
