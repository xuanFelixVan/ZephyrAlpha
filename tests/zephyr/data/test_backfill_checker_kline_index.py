# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [TTL] permanent
"""test_backfill_checker_kline_index.py — backfill_checker kline_index 补下载层单元测试。

覆盖 D1 施工（2026-08-24）：backfill_checker 补下载层扩 kline_index 覆盖——
检测指数表滞后（symbol 级差集）→ 显式日期窗口触发 akshare provider 补下载，
绕开 last_key 超前推进导致的"部分覆盖日补不回"缺口。

测试组：
- TestDetectIndexSymbolGap: symbol 级缺口检测（基线日/差集/全缺失）
- TestBackfillKlineIndex: 显式窗口补下载（复用 akshare provider + ch_writer.write_result）
- TestBackfillKlineIndexTable: 表级编排（缺失检测→触发→记录）
- TestWeekendBackfillKlineIndexRouting: 主循环 kline_index 走专用路径（不经 scheduler.run_task）
"""

from __future__ import annotations

import datetime
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

_SRC = Path(__file__).parent.parent.parent.parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from zephyr.data import backfill_checker as bc  # noqa: E402
from zephyr.data.provider_base import FetchResult  # noqa: E402

_TBL = "c1_market.kline_index"


def _fr(rows, last_key="2026-08-24"):
    return FetchResult(
        table=_TBL,
        columns=["trade_date", "symbol", "name", "open", "high", "low", "close", "volume", "data_source"],
        rows=rows,
        last_key=last_key,
        elapsed_sec=0.1,
    )


class TestDetectIndexSymbolGap:
    """_detect_index_symbol_gap：基线日达标 → 缺失日 symbol 差集。"""

    def test_partial_day_returns_symbol_diff(self):
        """部分覆盖日返回基线差集。"""
        dates = [datetime.date(2026, 8, 21), datetime.date(2026, 8, 24)]
        baseline = {"000300", "000905", "000852"}

        def fake_query(sql, timeout=30):
            if "count()" in sql:
                # 08-21 达标（546 >= 277），08-24 缺失（70 < 277）
                return "546" if "2026-08-21" in sql else "70"
            if "DISTINCT symbol" in sql:
                if "2026-08-21" in sql:
                    return "\n".join(sorted(baseline))
                return "000300"  # 08-24 仅有 1 只
            return ""

        with patch.object(bc.ch_reader, "query", side_effect=fake_query):
            gaps = bc._detect_index_symbol_gap(_TBL, dates, threshold=277)

        assert datetime.date(2026, 8, 21) not in gaps
        assert gaps[datetime.date(2026, 8, 24)] == ["000852", "000905"]

    def test_all_missing_falls_back_to_none(self):
        """全部日期缺失（无基线）→ symbols=None 表示全量清单。"""
        dates = [datetime.date(2026, 8, 21), datetime.date(2026, 8, 24)]

        def fake_query(sql, timeout=30):
            if "count()" in sql:
                return "0"
            return ""

        with patch.object(bc.ch_reader, "query", side_effect=fake_query):
            gaps = bc._detect_index_symbol_gap(_TBL, dates, threshold=277)

        assert gaps[datetime.date(2026, 8, 21)] is None
        assert gaps[datetime.date(2026, 8, 24)] is None

    def test_no_missing_returns_empty(self):
        """全部达标 → 空字典。"""
        dates = [datetime.date(2026, 8, 21)]

        def fake_query(sql, timeout=30):
            if "count()" in sql:
                return "600"
            if "DISTINCT symbol" in sql:
                return "000300"
            return ""

        with patch.object(bc.ch_reader, "query", side_effect=fake_query):
            gaps = bc._detect_index_symbol_gap(_TBL, dates, threshold=277)

        assert gaps == {}


class TestBackfillKlineIndex:
    """backfill_kline_index：复用 akshare provider 显式窗口补下载。"""

    def test_writes_rows_via_write_result(self):
        """provider 产出行经 ch_writer.write_result 落 CH，返回总行数。"""
        provider = MagicMock()
        provider.fetch.return_value = iter([_fr([("2026-08-24", "000905", "中证500", 1, 2, 3, 4, 5, "akshare")] * 3)])

        with (
            patch.object(bc, "_get_index_backfill_provider", return_value=provider),
            patch.object(bc.ch_writer, "write_result", return_value=True) as mock_write,
        ):
            rows = bc.backfill_kline_index(
                [datetime.date(2026, 8, 24)],
                symbols=["000905"],
            )

        assert rows == 3
        assert mock_write.call_count == 1
        payload = provider.fetch.call_args[0][0]
        assert payload.table == _TBL
        assert payload.start == datetime.date(2026, 8, 24)
        assert payload.end == datetime.date(2026, 8, 24)
        assert payload.symbols == ["000905"]
        assert payload.extra.get("capability") == "kline_index"

    def test_window_spans_missing_dates(self):
        """窗口 = [min(missing), max(missing)]，绕开 last_key。"""
        provider = MagicMock()
        provider.fetch.return_value = iter([_fr([])])

        with (
            patch.object(bc, "_get_index_backfill_provider", return_value=provider),
            patch.object(bc.ch_writer, "write_result", return_value=True),
        ):
            rows = bc.backfill_kline_index(
                [datetime.date(2026, 8, 20), datetime.date(2026, 8, 21), datetime.date(2026, 8, 24)],
                symbols=None,
            )

        assert rows == 0
        payload = provider.fetch.call_args[0][0]
        assert payload.start == datetime.date(2026, 8, 20)
        assert payload.end == datetime.date(2026, 8, 24)
        assert payload.symbols is None

    def test_provider_unavailable_returns_zero(self):
        """provider 不可用 → 返回 0（不抛异常）。"""
        with patch.object(bc, "_get_index_backfill_provider", return_value=None):
            rows = bc.backfill_kline_index([datetime.date(2026, 8, 24)], symbols=["000905"])
        assert rows == 0

    def test_empty_dates_returns_zero(self):
        """空缺失列表 → 0，不触碰 provider。"""
        assert bc.backfill_kline_index([], symbols=["000905"]) == 0

    def test_write_failure_not_counted(self):
        """write_result 失败的批次不计入行数。"""
        provider = MagicMock()
        provider.fetch.return_value = iter([_fr([("2026-08-24", "000905", "n", 1, 2, 3, 4, 5, "akshare")] * 2)])

        with (
            patch.object(bc, "_get_index_backfill_provider", return_value=provider),
            patch.object(bc.ch_writer, "write_result", return_value=False),
        ):
            rows = bc.backfill_kline_index([datetime.date(2026, 8, 24)], symbols=["000905"])
        assert rows == 0


class TestBackfillKlineIndexTable:
    """_backfill_kline_index_table：检测→触发→记录编排。"""

    def test_missing_triggers_backfill_and_records(self):
        info = {"table": _TBL, "date_column": "trade_date", "threshold": 277, "task_id": "kline_index_incremental"}
        dates = [datetime.date(2026, 8, 21), datetime.date(2026, 8, 24)]
        all_missing: list[dict] = []

        with (
            patch.object(
                bc,
                "_detect_index_symbol_gap",
                return_value={datetime.date(2026, 8, 24): ["000905"]},
            ),
            patch.object(bc, "backfill_kline_index", return_value=476) as mock_bf,
        ):
            rows = bc._backfill_kline_index_table(info, dates, all_missing)

        assert rows == 476
        mock_bf.assert_called_once()
        call_dates, call_symbols = mock_bf.call_args[0][0], mock_bf.call_args[1].get("symbols", mock_bf.call_args[0][1] if len(mock_bf.call_args[0]) > 1 else None)
        assert call_dates == [datetime.date(2026, 8, 24)]
        assert sorted(set(call_symbols)) == ["000905"]
        assert all_missing[0]["table"] == _TBL
        assert all_missing[0]["missing_dates"] == ["2026-08-24"]
        assert all_missing[0]["rows_backfilled"] == 476

    def test_no_missing_no_record(self):
        info = {"table": _TBL, "date_column": "trade_date", "threshold": 277, "task_id": "kline_index_incremental"}
        all_missing: list[dict] = []

        with (
            patch.object(bc, "_detect_index_symbol_gap", return_value={}),
            patch.object(bc, "backfill_kline_index") as mock_bf,
        ):
            rows = bc._backfill_kline_index_table(info, [datetime.date(2026, 8, 21)], all_missing)

        assert rows == 0
        mock_bf.assert_not_called()
        assert all_missing == []

    def test_zero_threshold_skips(self):
        """threshold=0（静态/业务事件类）不进入本路径。"""
        info = {"table": _TBL, "date_column": "trade_date", "threshold": 0, "task_id": "kline_index_incremental"}
        with patch.object(bc, "_detect_index_symbol_gap") as mock_det:
            rows = bc._backfill_kline_index_table(info, [datetime.date(2026, 8, 21)], [])
        assert rows == 0
        mock_det.assert_not_called()


class TestWeekendBackfillKlineIndexRouting:
    """run_weekend_backfill：kline_index 走专用路径，不经 generic run_task。"""

    def test_kline_index_uses_dedicated_path(self):
        idx_info = {
            "table": _TBL,
            "task_id": "kline_index_incremental",
            "source": "miniqmt",
            "capability": "kline_index",
            "schedule": "daily_kline",
            "date_column": "trade_date",
            "threshold": 277,
        }
        scheduler = MagicMock()

        with (
            patch.object(bc, "get_trade_dates", return_value=[datetime.date(2026, 8, 24)]),
            patch.object(bc, "_discover_backfill_tables", return_value=[idx_info]),
            patch.object(bc, "_backfill_kline_index_table", return_value=100) as mock_ded,
            patch.object(bc, "_backfill_generic_table") as mock_generic,
            patch.object(bc, "_record_backfill_progress"),
            patch.object(bc, "run_known_gap_backfill", return_value={"checked": 0, "still_missing": 0, "backfilled_rows": 0, "details": []}),
        ):
            result = bc.run_weekend_backfill(scheduler, days=1)

        mock_ded.assert_called_once()
        mock_generic.assert_not_called()
        scheduler.run_task.assert_not_called()
        assert result["total_rows"] == 100
        assert result["success"] is True
