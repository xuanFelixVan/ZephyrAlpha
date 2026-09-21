# [MODULE] tests.zephyr.data.test_supply_sentinel
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.supply_sentinel; zephyr.shared.utils.time_utils
# [TESTS] 本文件
# [TTL] permanent
"""断供哨兵**判据维度**的能红测试钉（全流通战役 车道 st-ff-sentinel-20260918）。

被钉住的根因（普查 R-026 第 6 型 / BRK-038 + BRK-040 + N-1 实测）：
    旧哨兵只有"表级 max(date_col) 落后日历日"一条腿，于是
      ① date_col 配成 ingest_ts 时，业务日期停更 323 天照样全绿（因果方向说反）；
      ② 表级 max 被单个维度掩护时，SHFE 仓单停更 305 天照样全绿；
      ③ 行数正常、日期新鲜、关键列全 0 时照样全绿（错数进闭环）。
    本文件对每一条都给出"制造该形态 → 必红"的断言，且**被断言的防线是真对象**
    （只有 CH 传输被替换为脚本化 runner——传输不是被测防线）。
"""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
from typing import Any

import pytest
import yaml

from zephyr.data.supply_sentinel import (
    _SENTINEL_CONFIG_PATH,
    HEARTBEAT_DATE_COLS,
    SupplySentinelError,
    check_tables,
    find_heartbeat_only_blind_spots,
)

_TODAY = date(2026, 9, 18)


class _ScriptedChRunner:
    """按 SQL 片段命中返回预置值（未命中=查询失败，返回空串，同 ch_reader 语义）。"""

    def __init__(self, scripts: dict[str, str], *, default: str = "") -> None:
        self._scripts = scripts
        self._default = default
        self.sqls: list[str] = []

    def __call__(self, sql: str) -> str:
        self.sqls.append(sql)
        for frag, value in self._scripts.items():
            if frag in sql:
                return value
        return self._default


def _write_cfg(tmp_path: Path, entries: list[dict[str, Any]]) -> Path:
    path = tmp_path / "sentinel_cfg.yaml"
    path.write_text(yaml.safe_dump({"tables": entries}, allow_unicode=True), encoding="utf-8")
    return path


def _run(tmp_path: Path, entries: list[dict[str, Any]], runner: _ScriptedChRunner, *, today: date = _TODAY) -> dict:
    return check_tables(_write_cfg(tmp_path, entries), today=today, runner=runner)


# ============ ①心跳腿 vs 业务腿：因果方向必须正过来 ============ #


def test_stale_business_date_alarms_even_when_ingest_leg_is_fresh(tmp_path: Path) -> None:
    """BRK-038/040 本体：ingest 腿 lag=0 全绿时，业务日期腿必须独立报红。"""
    entries = [
        {
            "table": "c1_market.rate_decision_calendar",
            "date_col": "ingest_ts",
            "max_lag_days": 2,
            "past_only": False,
            "heartbeat_leg": True,
        },
        {
            "table": "c1_market.rate_decision_calendar",
            "date_col": "decision_date",
            "max_lag_days": 75,
            "past_only": False,
        },
    ]
    runner = _ScriptedChRunner({"max(ingest_ts)": "2026-09-18 10:04:15.000", "max(decision_date)": "2025-10-30"})
    summary = _run(tmp_path, entries, runner)
    assert summary["breached"] == 1, "业务日停更 323 天未被点亮 = 判据维度仍是假的"
    red = [r for r in summary["results"] if r["breached"]][0]
    assert red["date_col"] == "decision_date"
    assert red["lag_days"] == 323


def test_heartbeat_only_coverage_is_reported_as_blind_spot(tmp_path: Path) -> None:
    """只有心跳腿的表=配置形态级盲点，必须出声（禁"配了行=覆盖了"的错觉）。"""
    entries = [
        {"table": "c1_market.rate_decision_calendar", "date_col": "ingest_ts", "max_lag_days": 2, "heartbeat_leg": True}
    ]
    runner = _ScriptedChRunner({"max(ingest_ts)": "2026-09-18 10:04:15.000"})
    summary = _run(tmp_path, entries, runner)
    assert summary["blind_spots"] == ["c1_market.rate_decision_calendar"]
    assert summary["ok"] is False, "盲点不影响 ok = 盲点永远无人追（就是本轮普查的失效路径）"


def test_business_leg_clears_the_blind_spot_flag(tmp_path: Path) -> None:
    entries = [
        {"table": "t.a", "date_col": "ingest_ts", "max_lag_days": 2, "heartbeat_leg": True},
        {"table": "t.a", "date_col": "trade_date", "max_lag_days": 5},
    ]
    runner = _ScriptedChRunner({"max(ingest_ts)": "2026-09-18", "max(trade_date)": "2026-09-17"})
    assert _run(tmp_path, entries, runner)["blind_spots"] == []


def test_heartbeat_column_as_date_col_requires_explicit_declaration(tmp_path: Path) -> None:
    """心跳列裸用作 date_col 而不声明 heartbeat_leg = 配置报错（不静默放行）。"""
    with pytest.raises(SupplySentinelError, match="heartbeat_leg"):
        _run(tmp_path, [{"table": "t.a", "date_col": "ingest_ts", "max_lag_days": 2}], _ScriptedChRunner({}))


def test_all_heartbeat_columns_are_guarded() -> None:
    """心跳列集合非空且含 ingest_ts（本簇三个活例都栽在它上面）。"""
    assert "ingest_ts" in HEARTBEAT_DATE_COLS
    assert find_heartbeat_only_blind_spots([{"table": "t.a", "date_col": "ingest_ts", "heartbeat_leg": True}]) == [
        "t.a"
    ]


# ============ ②维度切片：单维停更不再被表级 max 掩护 ============ #


def test_row_filter_leg_detects_single_exchange_outage(tmp_path: Path) -> None:
    """BRK-039 型：表级 max=今日全绿，SHFE 维度腿必须单独报红。"""
    entries = [
        {
            "table": "c1_market.futures_warehouse_receipt",
            "date_col": "trade_date",
            "max_lag_days": 10,
            "past_only": True,
        },
        {
            "table": "c1_market.futures_warehouse_receipt",
            "date_col": "trade_date",
            "max_lag_days": 10,
            "past_only": True,
            "row_filter": "exchange = 'SHFE'",
            "leg_name": "SHFE",
        },
    ]
    runner = _ScriptedChRunner(
        {"(exchange = 'SHFE')": "2025-11-17"},
        default="2026-09-18",
    )
    summary = _run(tmp_path, entries, runner)
    assert summary["breached"] == 1
    red = [r for r in summary["results"] if r["breached"]][0]
    assert red["leg"] == "SHFE" and red["lag_days"] == 305


def test_row_filter_rejects_statement_escape(tmp_path: Path) -> None:
    with pytest.raises(SupplySentinelError, match="row_filter"):
        _run(
            tmp_path,
            [
                {
                    "table": "t.a",
                    "date_col": "trade_date",
                    "max_lag_days": 1,
                    "row_filter": "1=1; DROP TABLE c1_market.kline_daily",
                }
            ],
            _ScriptedChRunner({}),
        )


# ============ ③交易日口径：合法滞后不造新噪音，也不必把尺子掰宽 ============ #


class _FakeTradingCalendar:
    """协作方（交易日历）替身：只喂交易日，不 patch 判据本体。"""

    def __init__(self, days: list[date]) -> None:
        self._days = days

    def trading_days_in_range(self, start: date, end: date) -> list[date]:
        return [d for d in self._days if start <= d <= end]


def test_trading_day_basis_absorbs_holiday_gap(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """国庆+中秋 9 个日历日停更在交易日口径下=2 个交易日，不该误报。"""
    entry = {
        "table": "t.a",
        "date_col": "trade_date",
        "max_lag_days": 2,
        "past_only": True,
        "lag_basis": "trading_days",
    }
    runner = _ScriptedChRunner({"max(trade_date)": "2026-09-30"})
    monkeypatch.setattr(
        "zephyr.data.supply_sentinel._default_calendar",
        lambda: _FakeTradingCalendar([date(2026, 10, 8), date(2026, 10, 9)]),
    )
    summary = _run(tmp_path, [entry], runner, today=date(2026, 10, 9))
    assert summary["breached"] == 0, "交易日口径未生效（按 9 个日历日判）= 用放宽阈值造噪音的旧路"


def test_trading_day_basis_still_alarms_on_real_gap(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """真断供 20 个交易日仍须报红——放宽只买节假日，不买断供。"""
    entry = {
        "table": "t.a",
        "date_col": "trade_date",
        "max_lag_days": 2,
        "past_only": True,
        "lag_basis": "trading_days",
    }
    monkeypatch.setattr(
        "zephyr.data.supply_sentinel._default_calendar",
        lambda: _FakeTradingCalendar([_TODAY - timedelta(days=i) for i in range(1, 60)]),
    )
    summary = _run(tmp_path, [entry], _ScriptedChRunner({"max(trade_date)": "2026-06-01"}))
    assert summary["breached"] == 1 and summary["results"][0]["lag_days"] > 20


def test_calendar_failure_degrades_to_stricter_calendar_days(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """日历不可用 → 降级方向必须是更严（日历日），不是放行。"""

    def _boom() -> None:
        raise RuntimeError("日历不可用")

    monkeypatch.setattr("zephyr.data.supply_sentinel._default_calendar", _boom)
    entry = {
        "table": "t.a",
        "date_col": "trade_date",
        "max_lag_days": 2,
        "past_only": True,
        "lag_basis": "trading_days",
    }
    summary = _run(tmp_path, [entry], _ScriptedChRunner({"max(trade_date)": "2026-09-01"}))
    assert summary["breached"] == 1 and summary["results"][0]["lag_days"] == 17


# ============ ④一次性回填/全量刷新表：换一档判据而非日频判据 ============ #


def test_static_backfill_cadence_uses_row_floor_not_date_lag(tmp_path: Path) -> None:
    entry = {
        "table": "t.hist",
        "date_col": "end_date",
        "max_lag_days": 5,
        "cadence": "static_backfill",
        "min_rows_in_window": {"window_days": 0, "min_rows": 1000},
    }
    runner = _ScriptedChRunner({"max(end_date)": "2019-11-20", "count() FROM t.hist": "5000"})
    assert _run(tmp_path, [entry], runner)["breached"] == 0, "回填表被日频判据误伤=新噪音"


def test_static_backfill_zero_output_still_alarms(tmp_path: Path) -> None:
    entry = {
        "table": "t.hist",
        "date_col": "end_date",
        "max_lag_days": 5,
        "cadence": "static_backfill",
        "min_rows_in_window": {"window_days": 0, "min_rows": 1000},
    }
    runner = _ScriptedChRunner({"max(end_date)": "2019-11-20", "count() FROM t.hist": "12"})
    summary = _run(tmp_path, [entry], runner)
    assert summary["breached"] == 1, "回填表刷新成 0 行/12 行不报红 = 地板判据是假的"


def test_source_row_floor_detects_synth_only_window(tmp_path: Path) -> None:
    """synth_* 冒充真值型：真值源窗口内行数掉到地板以下即红（行数总量照常全绿）。"""
    entry = {
        "table": "c1_market.kline_sector_intraday",
        "date_col": "trade_date",
        "max_lag_days": 5,
        "past_only": True,
        "row_filter": "data_source = 'tdx'",
        "min_rows_in_window": {"window_days": 5, "min_rows": 1000},
        "leg_name": "tdx 真值",
    }
    runner = _ScriptedChRunner({"max(trade_date)": "2026-09-10", "count() FROM": "0"})
    summary = _run(tmp_path, [entry], runner)
    assert summary["breached"] == 1
    kinds = {c["kind"] for c in summary["results"][0]["checks"]}
    assert "row_floor" in kinds


# ============ ⑤关键列填充率（N-1 型）============ #


def test_fill_ratio_flags_all_zero_key_columns(tmp_path: Path) -> None:
    """N-1 形态：259238 行、日期新鲜，但 close/amount/turnover 非零命中 0 行 → 必红。"""
    entry = {
        "table": "c1_market.daily_valuation",
        "date_col": "trade_date",
        "max_lag_days": 5,
        "past_only": True,
        "column_fill_ratio": {"cols": ["close", "amount", "turnover"], "min_ratio": 0.95, "window_days": 10},
    }
    runner = _ScriptedChRunner(
        {"max(trade_date)": "2026-09-17", "SELECT count(), countIf(ifNull(close, 0) != 0)": "259238\t0\t0\t0"}
    )
    summary = _run(tmp_path, [entry], runner)
    assert summary["breached"] == 1, "非 Nullable 列把无值写成 0 不被度量 = 错数静默进闭环"
    leg = summary["results"][0]["checks"][0]
    assert leg["ratios"]["close"] == 0.0


def test_fill_ratio_passes_when_columns_are_filled(tmp_path: Path) -> None:
    entry = {
        "table": "t.a",
        "date_col": "trade_date",
        "max_lag_days": 5,
        "column_fill_ratio": {"cols": ["close"], "min_ratio": 0.95, "window_days": 10},
    }
    runner = _ScriptedChRunner({"max(trade_date)": "2026-09-17", "SELECT count(), countIf": "100\t99"})
    assert _run(tmp_path, [entry], runner)["breached"] == 0


def test_fill_ratio_notnull_mode_for_computed_columns(tmp_path: Path) -> None:
    """计算列全 NULL 型（index_valuation_daily 实测 8125/8125 NULL）：非空口径判据。"""
    entry = {
        "table": "t.iv",
        "date_col": "trade_date",
        "max_lag_days": 7,
        "column_fill_ratio": {
            "cols": ["cape_5y", "erp"],
            "min_ratio": 0.9,
            "window_days": 0,
            "treat_zero_as_missing": False,
        },
    }
    runner = _ScriptedChRunner({"max(trade_date)": "2026-09-17", "SELECT count(), countIf(isNotNull": "8125\t0\t0"})
    summary = _run(tmp_path, [entry], runner)
    assert summary["breached"] == 1
    assert "cape_5y" in summary["results"][0]["checks"][0]["detail"]


def test_fill_ratio_short_response_counts_as_violation(tmp_path: Path) -> None:
    """返回列数与请求不符（列不存在等静默降级）= 该腿未生效，禁当干净。"""
    entry = {
        "table": "t.a",
        "date_col": "trade_date",
        "max_lag_days": 5,
        "column_fill_ratio": {"cols": ["close", "amount"], "min_ratio": 0.95},
    }
    runner = _ScriptedChRunner({"max(trade_date)": "2026-09-17", "SELECT count(), countIf": "100\t100"})
    summary = _run(tmp_path, [entry], runner)
    assert summary["breached"] == 1 and "error" in summary["results"][0]["detail"]


# ============ ⑥配置 fail-closed：拼错的阈值名不许静默空转 ============ #


def test_unknown_field_fails_closed(tmp_path: Path) -> None:
    with pytest.raises(SupplySentinelError, match="未知字段"):
        _run(
            tmp_path,
            [{"table": "t.a", "date_col": "trade_date", "max_lag_days": 5, "max_lag_dayz": 9}],
            _ScriptedChRunner({}),
        )


def test_bad_enum_and_ratio_value_domains_fail_closed(tmp_path: Path) -> None:
    bad = [
        {"table": "t.a", "date_col": "d", "max_lag_days": 1, "lag_basis": "lunar_days"},
        {"table": "t.a", "date_col": "d", "max_lag_days": 1, "cadence": "sometimes"},
        {"table": "t.a", "date_col": "d", "max_lag_days": 1, "column_fill_ratio": {"cols": ["x"], "min_ratio": 0}},
        {
            "table": "t.a",
            "date_col": "d",
            "max_lag_days": 1,
            "min_rows_in_window": {"window_days": "yesterday", "min_rows": 1},
        },
        {"table": "t.a", "date_col": "d", "max_lag_days": 1, "column_fill_ratio": {"cols": ["a;drop"]}},
    ]
    for entry in bad:
        with pytest.raises(SupplySentinelError):
            _run(tmp_path, [entry], _ScriptedChRunner({}))


# ============ ⑦出厂配置自查：本轮点亮的盲点不许被掰回宽松 ============ #


def _shipped_entries() -> list[dict[str, Any]]:
    return yaml.safe_load(_SENTINEL_CONFIG_PATH.read_text(encoding="utf-8"))["tables"]


def test_shipped_config_has_business_leg_for_the_four_measured_blind_spots() -> None:
    """四例实测盲点必须各有业务日期腿（防"改完又回潮"）。"""
    entries = _shipped_entries()
    business_cols = {
        "c1_market.rate_decision_calendar": "decision_date",
        "c1_market.alt_sz_reservoir_level": "tdate",
        "c1_market.futures_warehouse_receipt": "trade_date",
        "c1_market.daily_valuation": "trade_date",
    }
    for table, col in business_cols.items():
        legs = [e for e in entries if e["table"] == table and e["date_col"] == col]
        assert legs, f"{table} 缺 {col} 业务日期腿"
        assert all(not e.get("heartbeat_leg") for e in legs)
    # 表级（非维度切片）腿必须存在且唯一——变异 μ1 实测抓到第一版断言咬不住：
    # 把 decision_date 表级腿改名后，pboc 维度腿仍能满足"有 date_col=decision_date 的腿"。
    table_level = [
        e
        for e in entries
        if e["table"] == "c1_market.rate_decision_calendar"
        and e["date_col"] == "decision_date"
        and not e.get("row_filter")
    ]
    assert len(table_level) == 1, "议息日历必须恰有一条表级业务日期腿"
    assert int(table_level[0]["max_lag_days"]) == 75
    assert find_heartbeat_only_blind_spots(entries) == []


def test_shipped_config_daily_tables_are_not_loosened_past_ten_days() -> None:
    """日频表（实测近 6 个月每月 28-31 个业务日）阈值必须留在日频档，禁为降噪掰宽。"""
    daily = {
        "c1_market.alt_sz_reservoir_level",
        "c1_market.daily_valuation",
        "c1_market.index_valuation_daily",
        "c1_market.kline_sector_intraday",
        "c1_market.auction_snapshot",
    }
    for entry in _shipped_entries():
        if entry["table"] in daily and entry["date_col"] != "ingest_ts":
            assert int(entry["max_lag_days"]) <= 10, f"{entry['table']} 阈值被放宽到日频档之外"


def test_shipped_config_covers_every_measured_table_with_a_row_floor_or_fill_leg() -> None:
    """N-1 型（值全 0）与源冒充型必须各有一项附加腿在册（机制需求落地留痕）。"""
    entries = _shipped_entries()
    by_table = {e["table"]: e for e in entries}
    dv = by_table["c1_market.daily_valuation"].get("column_fill_ratio") or {}
    # 2026-09-20 WO-1 更正（本测试随之收口，原钉死三列系陈旧断言）：turnover 拆出——
    # 数据源 kline_daily 本身近窗非零率 0.9%（miniqmt/EM 日K 不带换手率），保留它=
    # 结构性永久红腿=告警疲劳必被拔线（BRK-046 同型）；close/amount 足以锚定行情腿
    # 非零判据本意（对齐 data_supply_sentinel.yaml 同批注释与 gaps 册工单登记）。
    # 变异 μ3 守卫意图保留：仍钉死精确列集，禁「有 column_fill_ratio 即可」的粗断言。
    assert sorted(dv.get("cols") or []) == ["amount", "close"], (
        "填充率腿必须钉住实测全 0 的行情列本身（close/amount）——变异 μ3 实测：换成 "
        "pe_ttm/pb_mrq 也能过「有 column_fill_ratio」这种粗断言，等于把 N-1 型重新放走"
    )
    iv = by_table["c1_market.index_valuation_daily"].get("column_fill_ratio") or {}
    assert sorted(iv.get("cols") or []) == ["cape_5y", "erp", "pe_pct"]
    floored = [e for e in entries if e["table"] == "c1_market.kline_sector_intraday" and e.get("min_rows_in_window")]
    assert floored and floored[0]["row_filter"] == "data_source = 'tdx'", (
        "行数地板腿必须切在真值源上，否则 synth_* 合成行自己就能把地板填满而过关"
    )
