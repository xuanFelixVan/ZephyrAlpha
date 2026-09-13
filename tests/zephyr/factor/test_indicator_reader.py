# [BLUEPRINT] MOD-L02-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""技术指标 PIT 读取 API 测试（批 7 块 A，2026-09-14）。

测试内容：
- 白名单：非法列名/非法 period → ValueError（防拼错列名静默空返回）
- PIT：end>as_of 硬拒；as_of 在未来拒
- SQL 构造：symbol/period/日期条件注入正确（monkeypatch ch_reader.query 捕获）
- TSV 解析：正常路径与空结果路径
- 真实 CH 冒烟：skipif 不可达（读测试不写生产路径）
"""

from __future__ import annotations

from unittest.mock import patch

import pandas as pd
import pytest

from zephyr.factor import indicator_reader
from zephyr.factor.indicator_reader import read_indicator

_TSV = (
    "2026-09-01\t2026-09-01 00:00:00\t000852\tdaily\t2.5\t55.1\n"
    "2026-09-02\t2026-09-02 00:00:00\t000852\tdaily\t2.7\t61.3\n"
)


class TestWhitelist:
    def test_illegal_column_raises(self):
        with pytest.raises(ValueError, match="白名单"):
            read_indicator("000852.SZ", columns=["not_a_column"])

    def test_illegal_period_raises(self):
        with pytest.raises(ValueError, match="period"):
            read_indicator("000852.SZ", period="7min")

    def test_empty_symbol_raises(self):
        with pytest.raises(ValueError, match="symbol"):
            read_indicator("")

    def test_valid_columns_pass(self):
        with patch.object(indicator_reader.ch_reader, "query", return_value=""):
            df = read_indicator("000852.SZ", columns=["atr_14", "rsi_6"])
        assert df.empty


class TestPit:
    def test_end_after_asof_rejected(self):
        with pytest.raises(ValueError, match="PIT"):
            read_indicator("000852.SZ", start="2026-01-01", end="2026-09-10", as_of="2026-09-01")

    def test_asof_in_future_rejected(self):
        with pytest.raises(ValueError, match="未来"):
            read_indicator("000852.SZ", end="2099-01-01", as_of="2099-01-02")

    def test_end_equal_asof_allowed(self):
        with patch.object(indicator_reader.ch_reader, "query", return_value=""):
            df = read_indicator("000852.SZ", end="2026-09-01", as_of="2026-09-01")
        assert df.empty


class TestSqlConstruction:
    def test_where_and_columns(self):
        captured = {}

        def fake_query(sql, **kwargs):
            captured["sql"] = sql
            return _TSV

        with patch.object(indicator_reader.ch_reader, "query", side_effect=fake_query):
            df = read_indicator(
                "000852", period="daily", columns=["atr_14", "rsi_6"],
                start="2026-08-01", end="2026-09-10", as_of="2026-09-11",
            )
        assert "period = 'daily'" in captured["sql"]
        assert "symbol = '000852'" in captured["sql"]
        assert "format" not in captured["sql"].lower()  # FORMAT 由 ch_writer 强制 TSV
        assert "trade_date >= '2026-08-01'" in captured["sql"]
        assert "trade_date <= '2026-09-10'" in captured["sql"]
        # FINAL 由 ch_reader.query 内部注入——验证注入器对本 SQL 生效（ReplacingMergeTree 去重）
        assert " final" in indicator_reader.ch_reader.inject_final(captured["sql"]).lower()
        assert "atr_14" in captured["sql"] and "rsi_6" in captured["sql"]
        assert len(df) == 2
        assert df["rsi_6"].iloc[1] == pytest.approx(61.3)

    def test_empty_tsv_returns_empty_frame(self):
        with patch.object(indicator_reader.ch_reader, "query", return_value=""):
            df = read_indicator("000852.SZ", columns=["atr_14"])
        assert list(df.columns) == ["trade_date", "trade_time", "symbol", "period", "atr_14"]


class TestRealSmoke:
    """真实 CH 冒烟（只读；CH 不可达时跳过）。"""

    def test_real_read_daily_atr(self):
        try:
            df = read_indicator(
                "000852", period="daily", columns=["atr_14", "rsi_6"],
                start="2026-08-01", end="2026-09-01",
            )
        except Exception as e:  # noqa: BLE001
            pytest.skip(f"CH 不可达: {e}")
        assert not df.empty, "000852 daily 2026-08 应有数据（增量任务在跑）"
        assert df["atr_14"].notna().any()
