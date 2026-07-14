# [TTL] task_bound
"""test_integrity_checker.py — 数据完整性巡检器单元测试。

测试组：
- TestCheckTableToday: 单表当日数据检查（达标/不达标/跳过）
- TestRunDailyCheck: 巡检主入口（动态发现+告警+记录）
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
        """无日期列 -> 跳过返回 None。"""
        info = {"table": "some_table", "date_column": "", "threshold": 100}
        today = datetime.date(2026, 7, 15)
        result = _check_table_today(info, today)
        assert result is None

    def test_skip_zero_threshold(self):
        """阈值为0 -> 跳过返回 None。"""
        info = {"table": "some_table", "date_column": "trade_date", "threshold": 0}
        today = datetime.date(2026, 7, 15)
        result = _check_table_today(info, today)
        assert result is None

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
        with patch("zephyr.data.integrity_checker._discover_backfill_tables", return_value=tables_info), \
             patch("zephyr.data.integrity_checker.ch_reader.query", return_value="200"):
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

        with patch("zephyr.data.integrity_checker._discover_backfill_tables", return_value=tables_info), \
             patch("zephyr.data.integrity_checker.ch_reader.query", side_effect=mock_query):
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

        with patch("zephyr.data.integrity_checker._discover_backfill_tables", return_value=tables_info), \
             patch("zephyr.data.integrity_checker.ch_reader.query", return_value="50"):
            result = run_daily_check(scheduler=mock_scheduler)

        assert result["success"] is False
        # 验证告警被调用
        mock_scheduler._alerter.notify.assert_called_once()

    def test_empty_tables(self):
        """无表 -> success=True, total=0。"""
        with patch("zephyr.data.integrity_checker._discover_backfill_tables", return_value=[]):
            result = run_daily_check(scheduler=None)
        assert result["success"] is True
        assert result["total"] == 0
