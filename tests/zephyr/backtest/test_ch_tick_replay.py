# [BLUEPRINT] MOD-L04-001 | docs/03_modules/_domain_backtest/backtest_engine_blueprint.md
# [TTL] permanent
# [TESTS] zephyr.backtest.implementations.ch_tick_replay
# [DOMAIN] D_DATA
"""ch_tick_replay 单元测试（回测 tick 回放 CH adapter，裁定①）。

覆盖：duck-typed 接口语义（interval 校验/空窗空 DF/symbol 纯码转换）、
1 档降级列完整性（5 档列齐备且 2-5 档为 0）、CH 异常转 CHBackfillReadError。
CH 交互全 mock。
"""

import os
import sys
from datetime import datetime
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src"))

import pandas as pd
import pytest

import zephyr.backtest.implementations.ch_tick_replay as cr
from zephyr.backtest.implementations.ch_tick_replay import (
    CHBackfillReadError,
    fetch_historical,
)

START = datetime(2026, 9, 8, 9, 30, 0)
END = datetime(2026, 9, 8, 15, 0, 0)


def _ch_rows():
    return [
        ("2026-09-08 09:30:03", 4.634, 280, 1297.52, 4.633, 4.634, 100, 200),
        ("2026-09-08 09:30:06", 4.635, 300, 1390.50, 4.634, 4.635, 110, 210),
    ]


class TestFetchHistorical:
    def test_interval_must_be_tick(self):
        with pytest.raises(ValueError):
            fetch_historical("600000.SH", START, END, interval="1m")

    def test_sql_filters_by_bare_symbol_and_window(self):
        client = MagicMock()
        client.execute.return_value = []
        with patch.object(cr, "get_client", return_value=client):
            df = fetch_historical("600000.SH", START, END)
        assert df.empty
        sql = client.execute.call_args[0][0]
        assert "symbol = '600000'" in sql          # 纯码（CH 列形态）
        assert "trade_date BETWEEN '2026-09-08' AND '2026-09-08'" in sql
        assert "ORDER BY timestamp" in sql
        assert "price > 0" in sql

    def test_rows_mapped_with_full_5level_columns(self):
        client = MagicMock()
        client.execute.return_value = _ch_rows()
        with patch.object(cr, "get_client", return_value=client):
            df = fetch_historical("600000.SH", START, END)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2
        # 列契约完整
        for i in range(1, 6):
            assert f"bid_price_{i}" in df.columns
            assert f"ask_price_{i}" in df.columns
            assert f"bid_vol_{i}" in df.columns
            assert f"ask_vol_{i}" in df.columns
        # 1 档真实值
        assert df.iloc[0]["bid_price_1"] == 4.633
        assert df.iloc[0]["ask_price_1"] == 4.634
        # 2-5 档降级填 0
        assert (df["bid_price_5"] == 0).all()
        assert (df["ask_vol_5"] == 0).all()
        # OHLC 降级语义（单快照价）
        assert df.iloc[0]["last_price"] == 4.634
        assert df.iloc[0]["open"] == 4.634

    def test_ch_failure_raises_chbackfillreaderror(self):
        client = MagicMock()
        client.execute.side_effect = RuntimeError("boom")
        with patch.object(cr, "get_client", return_value=client):
            with pytest.raises(CHBackfillReadError):
                fetch_historical("600000.SH", START, END)

    def test_duck_type_matches_replay_engine_expectation(self):
        """TickReplayEngine 调用形态：provider.fetch_historical(symbol=, start=, end=, interval='tick')。"""
        client = MagicMock()
        client.execute.return_value = _ch_rows()
        with patch.object(cr, "get_client", return_value=client):
            df = fetch_historical(symbol="600000.SH", start=START, end=END, interval="tick")
        assert not df.empty
        # _row_to_tick_snapshot 按列名取值——全部所需键存在
        row = df.iloc[0].to_dict()
        for i in range(1, 6):
            assert f"ask_price_{i}" in row
            assert f"bid_price_{i}" in row
            assert f"ask_vol_{i}" in row
            assert f"bid_vol_{i}" in row
        for key in ("timestamp", "last_price", "open", "high", "low", "prev_close",
                    "amount", "volume", "stock_status", "transaction_num"):
            assert key in row
