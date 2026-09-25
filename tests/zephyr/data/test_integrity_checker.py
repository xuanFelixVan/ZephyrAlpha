# [BLUEPRINT] MOD-L00-004 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [TTL] task_bound
"""test_integrity_checker.py — 数据完整性巡检器单元测试。

测试组：
- TestCheckTableToday: 单表当日数据检查（达标/不达标/跳过）
- TestRunDailyCheck: 巡检主入口（动态发现+告警+记录）
- TestT1LagJudgedTable: T+1 披露族滞后判警口径（DU-03 案：margin_trading 正常/滞后/降级）
"""

from __future__ import annotations

import datetime
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

_SRC = Path(__file__).parent.parent.parent.parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from zephyr.data.integrity_checker import (  # noqa: E402
    _check_table_today,
    run_daily_check,
)


class TestCheckTableToday:
    """单表当日数据检查。"""

    def test_healthy_table(self):
        """行数 >= 阈值 -> healthy=True。"""
        info = {"table": "kline_daily", "date_column": "trade_date", "threshold": 100}
        today = datetime.date(2026, 7, 15)
        with patch("zephyr.data.integrity_checker.ch_reader.query", return_value="500"):
            result = _check_table_today(info, today)
        assert result is not None
        assert result["healthy"] is True
        assert result["count"] == 500
        assert result["threshold"] == 100

    def test_unhealthy_table(self):
        """行数 < 阈值 -> healthy=False。"""
        info = {"table": "kline_daily", "date_column": "trade_date", "threshold": 1000}
        today = datetime.date(2026, 7, 15)
        with patch("zephyr.data.integrity_checker.ch_reader.query", return_value="50"):
            result = _check_table_today(info, today)
        assert result is not None
        assert result["healthy"] is False
        assert result["count"] == 50

    def test_skip_no_date_column(self):
        """无日期列 -> 标记 skipped=True（Phase 3-B 治本修复：不再静默返回 None）。"""
        info = {"table": "some_table", "date_column": "", "threshold": 100}
        today = datetime.date(2026, 7, 15)
        result = _check_table_today(info, today)
        assert result is not None
        assert result["skipped"] is True
        assert result["healthy"] is True

    def test_skip_zero_threshold(self):
        """阈值为0 -> 标记 skipped=True（Phase 3-B 治本修复：不再静默返回 None）。"""
        info = {"table": "some_table", "date_column": "trade_date", "threshold": 0}
        today = datetime.date(2026, 7, 15)
        result = _check_table_today(info, today)
        assert result is not None
        assert result["skipped"] is True
        assert result["healthy"] is True

    def test_ch_query_failure_returns_zero(self):
        """CH查询失败 -> count=0, healthy=False。"""
        info = {"table": "kline_daily", "date_column": "trade_date", "threshold": 100}
        today = datetime.date(2026, 7, 15)
        with patch("zephyr.data.integrity_checker.ch_reader.query", return_value=""):
            result = _check_table_today(info, today)
        assert result is not None
        assert result["count"] == 0
        assert result["healthy"] is False


class TestRunDailyCheck:
    """巡检主入口。"""

    def test_all_healthy(self):
        """全部达标 -> success=True。"""
        tables_info = [
            {"table": "kline_daily", "date_column": "trade_date", "threshold": 100},
            {"table": "money_flow", "date_column": "trade_date", "threshold": 50},
        ]
        with (
            patch("zephyr.data.integrity_checker.discover_backfill_tables", return_value=tables_info),
            patch("zephyr.data.integrity_checker.ch_reader.query", return_value="200"),
        ):
            result = run_daily_check(scheduler=None)
        assert result["success"] is True
        assert result["total"] == 2
        assert result["healthy_count"] == 2
        assert result["unhealthy_tables"] == []

    def test_some_unhealthy(self):
        """部分不达标 -> success=False。"""
        tables_info = [
            {"table": "kline_daily", "date_column": "trade_date", "threshold": 100},
            {"table": "money_flow", "date_column": "trade_date", "threshold": 500},
        ]

        def mock_query(sql):
            if "money_flow" in sql:
                return "50"
            return "200"

        with (
            patch("zephyr.data.integrity_checker.discover_backfill_tables", return_value=tables_info),
            patch("zephyr.data.integrity_checker.ch_reader.query", side_effect=mock_query),
        ):
            result = run_daily_check(scheduler=None)
        assert result["success"] is False
        assert result["total"] == 2
        assert result["healthy_count"] == 1
        assert len(result["unhealthy_tables"]) == 1
        assert result["unhealthy_tables"][0]["table"] == "money_flow"

    def test_with_scheduler_alerts(self):
        """有 scheduler 时发送告警。"""
        tables_info = [
            {"table": "kline_daily", "date_column": "trade_date", "threshold": 1000},
        ]
        mock_scheduler = MagicMock()
        mock_scheduler._alerter = MagicMock()

        with (
            patch("zephyr.data.integrity_checker.discover_backfill_tables", return_value=tables_info),
            patch("zephyr.data.integrity_checker.ch_reader.query", return_value="50"),
        ):
            result = run_daily_check(scheduler=mock_scheduler)

        assert result["success"] is False
        # 验证告警被调用
        mock_scheduler._alerter.notify.assert_called_once()

    def test_empty_tables(self):
        """无表 -> success=True, total=0。"""
        with patch("zephyr.data.integrity_checker.discover_backfill_tables", return_value=[]):
            result = run_daily_check(scheduler=None)
        assert result["success"] is True
        assert result["total"] == 0


_MARGIN = "c1_market.margin_trading"
_TODAY = datetime.date(2026, 7, 15)
# 参照双腿表名走模块全局缓存补丁，测试不依赖 business_data_categories.yaml
_REF_TABLES_PATCH = patch(
    "zephyr.data.integrity_checker._T1_REF_TABLES",
    ("c1_market.trade_calendar", "c1_market.kline_index"),
)


def _t1_mock_query(margin_max="2026-07-14", kline_max="2026-07-15", calendar_last="2026-07-15",
                   open_days="1", today_count="0"):
    """按 SQL 形态路由的 ch_reader.query mock（needle 顺序即优先级）。

    开市日数 SQL 同时含 "cal_date >" 与 "cal_date <="，故 ">" 必须排在 "<=" 之前。
    """
    responses = [
        (f"max(trade_date) FROM {_MARGIN}", margin_max),
        ("FROM c1_market.kline_index", kline_max),
        ("cal_date >", open_days),
        ("cal_date <=", calendar_last),
        (f"count() FROM {_MARGIN}", today_count),
    ]

    def mock_query(sql):
        for needle, value in responses:
            if needle in sql:
                return value
        return ""

    return mock_query


class TestT1LagJudgedTable:
    """T+1 披露族滞后判警口径（12 号文 DU-03 案，判据=滞后 ≥2 开市日）。"""

    def test_normal_t1_disclosure_healthy(self):
        """正常 T+1 披露：当日行数 0 但 max(trade_date)=T-1、滞后 1 开市日 -> healthy（旧口径必误报）。"""
        info = {"table": _MARGIN, "date_column": "trade_date", "threshold": 2052}
        with _REF_TABLES_PATCH, patch(
            "zephyr.data.integrity_checker.ch_reader.query",
            side_effect=_t1_mock_query(margin_max="2026-07-14", open_days="1", today_count="0"),
        ):
            result = _check_table_today(info, _TODAY)
        assert result is not None
        assert result["healthy"] is True
        assert result["count"] == 0  # 行数下限保留为次要参考列
        assert result["lag_trading_days"] == 1
        assert result["lag_basis"] == "trading_days"
        assert result["reference_day"] == "2026-07-15"
        assert "alert_message" not in result

    def test_lag_2_open_days_alerts(self):
        """真断：max(trade_date)=T-2、滞后 2 开市日 -> healthy=False（DU-03 4 日断供第 2 日即鸣笛）。"""
        info = {"table": _MARGIN, "date_column": "trade_date", "threshold": 2052}
        with _REF_TABLES_PATCH, patch(
            "zephyr.data.integrity_checker.ch_reader.query",
            side_effect=_t1_mock_query(margin_max="2026-07-13", open_days="2", today_count="0"),
        ):
            result = _check_table_today(info, _TODAY)
        assert result["healthy"] is False
        assert result["lag_trading_days"] == 2
        assert "滞后" in result["alert_message"]
        assert "0 < 2052" in result["alert_message"] or "仅参考" in result["alert_message"]

    def test_zero_history_alerts(self):
        """全史零行（CH 空集返回 1970-01-01 零值）-> 判断供，healthy=False。"""
        info = {"table": _MARGIN, "date_column": "trade_date", "threshold": 2052}
        with _REF_TABLES_PATCH, patch(
            "zephyr.data.integrity_checker.ch_reader.query",
            side_effect=_t1_mock_query(margin_max="1970-01-01"),
        ):
            result = _check_table_today(info, _TODAY)
        assert result["healthy"] is False
        assert result["last_date"] is None
        assert "断供" in result["alert_message"]

    def test_calendar_leg_down_degrades_to_kline(self):
        """日历腿故障 -> 参照日降级 kline_index 腿，判定不受影响。"""
        info = {"table": _MARGIN, "date_column": "trade_date", "threshold": 2052}
        with _REF_TABLES_PATCH, patch(
            "zephyr.data.integrity_checker.ch_reader.query",
            side_effect=_t1_mock_query(calendar_last="", open_days="1"),
        ):
            result = _check_table_today(info, _TODAY)
        assert result["healthy"] is True
        assert result["reference_day"] == "2026-07-15"
        assert result["lag_trading_days"] == 1

    def test_both_legs_down_degrades_to_rowcount_unhealthy(self):
        """参照日双腿全废 -> fail-soft 降级行数口径：当日 0 行 < 阈值 -> healthy=False。"""
        info = {"table": _MARGIN, "date_column": "trade_date", "threshold": 2052}
        with _REF_TABLES_PATCH, patch(
            "zephyr.data.integrity_checker.ch_reader.query",
            side_effect=_t1_mock_query(kline_max="", calendar_last="", today_count="0"),
        ):
            result = _check_table_today(info, _TODAY)
        assert result["healthy"] is False
        assert result["lag_basis"] == "degraded_rowcount"
        assert "降级" in result["alert_message"]

    def test_both_legs_down_rowcount_ok_stays_healthy(self):
        """参照日双腿全废 + 当日行数达标 -> 降级口径下不告警（fail-soft 不假红）。"""
        info = {"table": _MARGIN, "date_column": "trade_date", "threshold": 2052}
        with _REF_TABLES_PATCH, patch(
            "zephyr.data.integrity_checker.ch_reader.query",
            side_effect=_t1_mock_query(kline_max="", calendar_last="", today_count="3000"),
        ):
            result = _check_table_today(info, _TODAY)
        assert result["healthy"] is True
        assert result["lag_basis"] == "degraded_rowcount"

    def test_scheduler_alert_uses_lag_message(self):
        """有 scheduler 时 T+1 族走滞后文案，普通表保持原文案（判警行为零改动对照）。"""
        tables_info = [
            {"table": _MARGIN, "date_column": "trade_date", "threshold": 2052},
            {"table": "kline_daily", "date_column": "trade_date", "threshold": 100},
        ]

        def mock_query(sql):
            # margin+参照腿走 T+1 路由；kline_daily 未命中 -> "" -> 当日 0 行 < 100（原口径不达标）
            return _t1_mock_query(margin_max="2026-07-13", open_days="2", today_count="0")(sql)

        mock_scheduler = MagicMock()
        mock_scheduler._alerter = MagicMock()
        with (
            _REF_TABLES_PATCH,
            patch("zephyr.data.integrity_checker.discover_backfill_tables", return_value=tables_info),
            patch("zephyr.data.integrity_checker.ch_reader.query", side_effect=mock_query),
        ):
            result = run_daily_check(scheduler=mock_scheduler)
        assert result["success"] is False
        assert mock_scheduler._alerter.notify.call_count == 2
        messages = " | ".join(str(c.args[1]) for c in mock_scheduler._alerter.notify.call_args_list)
        assert "T+1披露滞后" in messages
        assert "当日数据不达标: 0 < 100" in messages  # 普通表文案不变

    def test_normal_table_result_has_no_lag_fields(self):
        """普通表结果不含滞后字段（其他表判警行为零改动的结构保证）。"""
        info = {"table": "kline_daily", "date_column": "trade_date", "threshold": 100}
        with patch("zephyr.data.integrity_checker.ch_reader.query", return_value="50"):
            result = _check_table_today(info, _TODAY)
        assert result["healthy"] is False
        assert "lag_trading_days" not in result
        assert "alert_message" not in result
