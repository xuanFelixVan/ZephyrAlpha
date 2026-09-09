# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [TTL] permanent
# [TESTS] zephyr.data.implementations.ch_tick_kline
# [DOMAIN] D_DATA
"""ch_tick_kline 单元测试（tick→分钟K 自拼，裁定③方案 b）。

覆盖：SQL 构建正确性（目标表/周期/幂等条件/Δ窗口函数/5min 来源过滤）、
防误覆盖门（#QMT-DAY-0908-OVERWRITE：1min 窗口已有数据默认拒绝）、
非法周期 ValueError。CH 交互全 mock，不依赖真实 ClickHouse。
"""

import os
import sys
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src"))

import pytest

import zephyr.data.implementations.ch_tick_kline as ck
from zephyr.data.implementations.ch_tick_kline import (
    _build_delete_sql,
    _build_synth_sql,
    synth_tick_kline,
)


class TestBuildSql:
    def test_1min_delete_targets_window(self):
        sql = _build_delete_sql("1min", "2026-09-08", "2026-09-09")
        assert "c1_market.kline_1min" in sql
        assert "trade_date BETWEEN '2026-09-08' AND '2026-09-09'" in sql
        assert "mutations_sync = 2" in sql

    def test_5min_delete_filters_synth_tick_only(self):
        """5min 幂等 DELETE 只删 synth_tick 行（官方历史零触碰）。"""
        sql = _build_delete_sql("5min", "2026-09-08", "2026-09-09")
        assert "c1_market.kline_5min" in sql
        assert "data_source = 'synth_tick'" in sql
        assert "trade_time BETWEEN" in sql

    def test_1min_synth_ohlc_aggregation(self):
        sql = _build_synth_sql("1min", "2026-09-08", "2026-09-08")
        # OHLC 口径铁律
        assert "argMin(price, timestamp) AS open" in sql
        assert "argMax(price, timestamp) AS close" in sql
        assert "max(price) AS high" in sql
        assert "min(price) AS low" in sql
        # Δ 增量口径 + 正差过滤
        assert "sumIf(d_vol, d_vol > 0)" in sql
        assert "lagInFrame(volume, 1)" in sql
        assert "toStartOfMinute(timestamp) AS window_start" in sql
        # 双源同表
        assert "data_source IN ('miniqmt', 'qmt_bridge')" in sql
        # 1min 表补列
        assert "0 AS pct_change" in sql
        assert "0 AS amplitude" in sql

    def test_5min_synth_window_and_source_tag(self):
        sql = _build_synth_sql("5min", "2026-09-08", "2026-09-08")
        assert "toStartOfFiveMinute(timestamp) AS window_start" in sql
        assert "'synth_tick' AS data_source" in sql
        assert "c1_market.kline_5min" in sql

    def test_illegal_period_raises(self):
        with pytest.raises(ValueError):
            _build_synth_sql("15min", "2026-09-08", "2026-09-08")
        with pytest.raises(ValueError):
            _build_delete_sql("daily", "2026-09-08", "2026-09-08")


class TestOverwriteGuard:
    def test_1min_refuses_existing_window(self):
        """1min 目标窗口已有数据且未显式放行 → RuntimeError 拒绝（事故防线）。"""
        client = MagicMock()
        client.execute.side_effect = [
            [(12345,)],  # 已有行数检查
        ]
        with patch.object(ck, "get_client", return_value=client):
            with pytest.raises(RuntimeError, match="allow_official_overwrite"):
                synth_tick_kline("1min", "2026-09-08", "2026-09-08")
        # 只执行了 count 查询，未执行 DELETE
        assert client.execute.call_count == 1

    def test_1min_proceeds_on_empty_window(self):
        """1min 窗口空 → 正常 DELETE+INSERT（幂等空跑）。"""
        client = MagicMock()
        client.execute.side_effect = lambda sql, *a, **kw: [[0]] if sql.startswith("SELECT count()") else []
        with patch.object(ck, "get_client", return_value=client):
            n = synth_tick_kline("1min", "2026-09-08", "2026-09-08")
        assert n == 0
        # count + DELETE + INSERT + count = 4 次 execute
        assert client.execute.call_count == 4

    def test_1min_explicit_overwrite_allows(self):
        """显式 allow_official_overwrite=True → 放行（调用方承担三步验证责任）。"""
        client = MagicMock()
        client.execute.side_effect = lambda sql, *a, **kw: [[0]] if sql.startswith("SELECT count()") else []
        with patch.object(ck, "get_client", return_value=client):
            n = synth_tick_kline("1min", "2026-09-08", "2026-09-08", allow_official_overwrite=True)
        assert n == 0
        # 无 count 前置检查：DELETE + INSERT + count = 3 次
        assert client.execute.call_count == 3

    def test_5min_has_no_gate_but_filtered_delete(self):
        """5min 不做窗口检查（DELETE 自带 synth_tick 过滤，官方数据天然安全）。"""
        client = MagicMock()
        client.execute.side_effect = lambda sql, *a, **kw: [[0]] if sql.startswith("SELECT count()") else []
        with patch.object(ck, "get_client", return_value=client):
            n = synth_tick_kline("5min", "2026-09-08", "2026-09-08")
        assert n == 0
        del_sql = client.execute.call_args_list[0][0][0]
        assert "data_source = 'synth_tick'" in del_sql
