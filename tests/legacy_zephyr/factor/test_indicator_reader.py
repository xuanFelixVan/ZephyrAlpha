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
                "000852",
                period="daily",
                columns=["atr_14", "rsi_6"],
                start="2026-08-01",
                end="2026-09-10",
                as_of="2026-09-11",
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
                "000852",
                period="daily",
                columns=["atr_14", "rsi_6"],
                start="2026-08-01",
                end="2026-09-01",
            )
        except Exception as e:  # noqa: BLE001
            pytest.skip(f"CH 不可达: {e}")
        assert not df.empty, "000852 daily 2026-08 应有数据（增量任务在跑）"
        assert df["atr_14"].notna().any()


class TestRowVersionDedupe:
    """读侧按 ingest_ts 去重（2026-10-09 第三条路）的契约尺。

    为什么必须有：technical_indicator=ReplacingMergeTree 且 ORDER BY 无版本列，
    合并前同键多版并存（实测 daily 2026 全年 38.4% 的键值互不相同、最多 6 版；
    重复键里约 12-15% 是"最早版≠最新版"），旧 SQL 非 FINAL 直读会把同一 bar 返回多行。
    """

    def _sql_of(self, monkeypatch):
        from zephyr.data import ch_writer

        seen = {}

        def fake(sql, timeout=600):
            seen["sql"] = sql
            return ""

        monkeypatch.setattr(ch_writer, "query", fake)
        import zephyr.factor.indicator_reader as ir

        ir.read_indicator(symbol="000001", period="daily", columns=["atr_14"], start="2026-09-01", end="2026-09-10")
        return seen.get("sql", "")

    def test_groups_by_table_key_and_uses_argmax(self, monkeypatch):
        sql = self._sql_of(monkeypatch)
        assert "GROUP BY symbol, period, trade_time" in sql
        assert "argMax(" in sql and "ingest_ts" in sql

    def test_no_alias_colliding_with_where(self, monkeypatch):
        """红证：别名若与 WHERE 引用列同名，CH 报 Code 184 ILLEGAL_AGGREGATION。"""
        sql = self._sql_of(monkeypatch)
        assert "AS trade_date" not in sql and "AS atr_14" not in sql, "别名撞名会直接查询失败"

    def test_row_shape_preserved_for_tsv_mapping(self, monkeypatch):
        """TSV 无表头按顺序映射 ⇒ SELECT 顺序必须逐一等于 frame_cols 的投影（键列直取、
        其余按 ingest_ts 取最新版）。用括号感知切分，勿按 ", " 切（argMax(a, b) 会被切断）。"""
        import zephyr.factor.indicator_reader as ir

        sql = self._sql_of(monkeypatch)
        body = sql.split(" FROM ", 1)[0].replace("SELECT ", "", 1)
        parts, depth, cur = [], 0, ""
        for ch in body:
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
            if ch == "," and depth == 0:
                parts.append(cur.strip())
                cur = ""
            else:
                cur += ch
        if cur.strip():
            parts.append(cur.strip())
        expected = [ir._projection(c) for c in ["trade_date", "trade_time", "symbol", "period", "atr_14"]]
        assert parts == expected
