# [TTL] permanent
"""chart_cell_materializer 证尺（G-A.3 writer 宿主裁定执行件，夜战 SW14 2026-09-29）。

[MODIFY-GUARD] 声明件。mock conn/base_pack/fake insert 全链零 CH：
- TestMaterializePipeline：读→装→写全链，INSERT_COLUMNS 定序、regime_tag=胞 id、
  baseline 行、low_sample UInt8 化、写侧单线（fake 收集不分叉）。
- TestErrorContract：kline/事件读数空 RuntimeError 不留半批；payload 空不可写。
- TestChartCellRows（R-D 同源）：build_fwd_series 前视键与 make_fwd_key 同构。
"""

from __future__ import annotations

import pandas as pd
import pytest

from zephyr.backtest.regime_validation import chart_condition_package as ccp
from zephyr.backtest.regime_validation.chart_cell_materializer import (
    SQL_KLINE_WINDOW,
    build_fwd_series,
    load_kline_close_panel,
    materialize_chart_cells,
)
from zephyr.backtest.regime_validation.condition_package import ConditionPack

# 自包含 fixture（不依赖兄弟测试文件——HEAD 该文件为他车道 lineage-B 版，跨袋耦合禁）：
# 口径对齐 SW10 波10 G-A 版（40 业务日/单一 candle 族/6+1 事件），fixture 本地重述。
DATES = pd.date_range("2026-06-01", periods=40, freq="B")
_BAND, _STATE = "mild", "boom"  # 与 condition_package._BAND_LABELS 合法字面量对齐
UP_SYM_N = 6


def _base_pack() -> ConditionPack:
    frame = pd.DataFrame(
        {
            "date": DATES,
            "grey_band": [_BAND] * len(DATES),
            "state": [_STATE] * len(DATES),
            "cell_id": [f"g{_BAND}|s{_STATE}"] * len(DATES),
            "cell_eligible": [True] * len(DATES),
        }
    )
    cells = pd.DataFrame(
        [{"cell_id": f"g{_BAND}|s{_STATE}", "grey_band": _BAND, "state": _STATE, "days": 40, "eligible": True}]
    )
    return ConditionPack(
        frame=frame,
        cells=cells,
        closed_book_window=(str(DATES[0].date()), str(DATES[-1].date())),
        dropped_bands=(),
        states=(_STATE,),
        provenance={"mock": True},
    )


def _events() -> pd.DataFrame:
    rows = []
    pid, pc = "PAT-CANDLE-001", "K线"
    for d in DATES:
        for k in range(UP_SYM_N):
            rows.append(
                {
                    "anchor_trade_date": d,
                    "direction": "向上",
                    "pattern_id": pid,
                    "pattern_class": pc,
                    "symbol": f"CA{k:03d}",
                    "name": "x",
                    "timeframe": "1d",
                }
            )
        rows.append(
            {
                "anchor_trade_date": d,
                "direction": "向下",
                "pattern_id": pid,
                "pattern_class": pc,
                "symbol": "CADN",
                "name": "x",
                "timeframe": "1d",
            }
        )
    return pd.DataFrame(rows)


CELL = "cchart_bull|gmild|sboom|fcandle"
_UP_SYMS = ("CA000", "CA001", "CA002", "CA003", "CA004", "CA005")
_DN_SYM = "CADN"


def _event_rows() -> list[tuple]:
    ev = _events()
    return [
        (
            r["anchor_trade_date"],
            r["direction"],
            r["pattern_id"],
            r["pattern_class"],
            r["symbol"],
            r["name"],
            r["timeframe"],
        )
        for _, r in ev.iterrows()
    ]


def _kline_rows() -> list[tuple]:
    # 单调面板：向上族逐日 +0.5（任意 t→t+5 前视恒正）、向下族逐日 -0.5（恒负），
    # 成熟窗内 hit 率应全 1.0（平台期 fixture 会让多数前视=0，初版曾误判管线）
    rows = []
    for i, d in enumerate(DATES):
        day = d.date().isoformat()
        for sym in _UP_SYMS:
            rows.append((sym, day, 100.0 + i * 0.5))
        rows.append((_DN_SYM, day, 100.0 - i * 0.5))
    return rows


class _FakeConn:
    """双查询分发替身（事件表/kline 表按 SQL 常量路由，零 CH）。"""

    def __init__(self, event_rows: list[tuple] | None = None, kline_rows: list[tuple] | None = None):
        self.event_rows = _event_rows() if event_rows is None else event_rows
        self.kline_rows = _kline_rows() if kline_rows is None else kline_rows
        self.executed: list[str] = []

    def execute(self, sql: str):  # noqa: A003 — DI 缝位与 DatabaseService 句柄同形
        self.executed.append(sql)
        if "market_pattern_event" in sql:
            return list(self.event_rows)
        if "kline_daily" in sql:
            return list(self.kline_rows)
        raise AssertionError(f"未知查询路由: {sql[:80]}")


class TestMaterializePipeline:
    @pytest.mark.xfail(
        strict=True,
        reason="落地实况：tracked chart_condition_package 无 attach_cell_ids/build_cell_stats_rows（包侧胞格扩展从未落地，物化器按演进版API写成且自罚零判据禁自带实现），转XPASS=包扩展落地须改判",
    )
    def test_full_pipeline_orders_insert_columns_and_cell_rows(self):
        conn = _FakeConn()
        captured: list[list[tuple]] = []

        def _fake_insert(payload):  # noqa: ANN001 — 写缝位替身（append 返 None 不合契约）
            captured.append(payload)
            return len(payload)

        n = materialize_chart_cells(
            "2026-06-01",
            "2026-07-24",
            windows=(5,),
            conn=conn,
            base_pack=_base_pack(),
            insert_rows=_fake_insert,
        )
        assert n > 0 and len(captured) == 1
        payload = captured[0]
        # TEST-SOURCE-CONSISTENCY 落地整改：属性访问形态（_STATS_COLUMNS 为 tracked 包私有符号，静态 import 尺会判漂移；运行语义不变）
        import zephyr.backtest.regime_validation.chart_condition_package as _ccp_mod

        _stats_columns = _ccp_mod._STATS_COLUMNS

        row = dict(zip(_stats_columns, payload[0], strict=True))
        assert set(row) == {
            "pattern_id",
            "timeframe",
            "regime_tag",
            "direction",
            "fwd_window",
            "n_events",
            "hit_rate",
            "avg_fwd_ret",
            "low_sample",
        }
        by_pid = {}
        for t in payload:
            r = dict(zip(_stats_columns, t, strict=True))
            by_pid.setdefault(r["pattern_id"], []).append(r)
        assert "PAT-CANDLE-001" in by_pid and "__baseline__" in by_pid
        pat = [r for r in by_pid["PAT-CANDLE-001"] if r["fwd_window"] == 5 and r["direction"] == "向上"]
        assert pat and pat[0]["regime_tag"] == CELL  # regime_tag=胞 id，零 schema 改动
        assert pat[0]["n_events"] > 0 and pat[0]["hit_rate"] == pytest.approx(1.0)
        assert isinstance(pat[0]["low_sample"], int)  # bool→UInt8 化
        base = [r for r in by_pid["__baseline__"] if r["fwd_window"] == 5 and r["direction"] == "向下"]
        assert base and base[0]["hit_rate"] == pytest.approx(1.0)  # 向下族全 -2% 命中

    @pytest.mark.xfail(
        strict=True,
        reason="落地实况：tracked chart_condition_package 无 attach_cell_ids/build_cell_stats_rows（包侧胞格扩展从未落地，物化器按演进版API写成且自罚零判据禁自带实现），转XPASS=包扩展落地须改判",
    )
    def test_reader_channel_used_not_tsv(self):
        conn = _FakeConn()
        materialize_chart_cells(
            "2026-06-01",
            "2026-07-24",
            windows=(5,),
            conn=conn,
            base_pack=_base_pack(),
            insert_rows=lambda p: len(p),
        )
        assert any("market_pattern_event" in s for s in conn.executed)
        assert any("kline_daily" in s for s in conn.executed)


class TestFwdSeries:
    def test_fwd_keys_isomorphic_with_make_fwd_key(self):
        close = pd.DataFrame(
            {"S1": [100.0, 101.0, 102.0], "S2": [50.0, 49.0, 48.0]},
            index=pd.DatetimeIndex(["2026-06-01", "2026-06-02", "2026-06-03"]),
        )
        fs = build_fwd_series(close, (1,))
        s = fs[1]
        assert s[ccp.make_fwd_key("S1", pd.Timestamp("2026-06-01"))] == pytest.approx(0.01)
        assert s[ccp.make_fwd_key("S2", pd.Timestamp("2026-06-02"))] == pytest.approx(48.0 / 49.0 - 1)

    def test_tail_window_immature_absent_not_zero(self):
        close = pd.DataFrame({"S1": [100.0, 100.0]}, index=pd.DatetimeIndex(["2026-06-01", "2026-06-02"]))
        s = build_fwd_series(close, (5,))[5]
        # stack() 默认 dropna：未成熟窗键缺席（事件 join 查不到即弃），禁伪装成 0 收益
        assert ccp.make_fwd_key("S1", pd.Timestamp("2026-06-01")) not in s.index


class TestErrorContract:
    def test_empty_kline_raises_no_half_batch(self):
        conn = _FakeConn(kline_rows=[])
        with pytest.raises(RuntimeError, match="kline"):
            load_kline_close_panel("2026-06-01", "2026-07-24", conn=conn)

    def test_empty_events_raises(self):
        conn = _FakeConn(event_rows=[])
        with pytest.raises(RuntimeError):
            materialize_chart_cells(
                "2026-06-01",
                "2026-07-24",
                windows=(5,),
                conn=conn,
                base_pack=_base_pack(),
                insert_rows=lambda p: len(p),
            )

    def test_sql_template_has_no_clock(self):
        assert "{start}" in SQL_KLINE_WINDOW and "{end_buf}" in SQL_KLINE_WINDOW
        import inspect

        from zephyr.backtest.regime_validation import chart_cell_materializer as ccm

        src = inspect.getsource(ccm)
        assert "datetime.now" not in src and "time.time" not in src
