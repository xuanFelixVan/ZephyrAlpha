# [A_test] module_id: MOD-DATA-IDXBREADTH | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md | §test
# [MODULE] tests.data.implementations.test_index_breadth_compute
# [TESTS] src/zephyr/data/implementations/index_breadth_compute.py
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TTL] permanent
"""车道 G 广度进料件单测：宇宙聚合→kline_index 整行读-改-写的真源优先/覆盖度防御/自愈窗。

CH 全注入（monkeypatch ch_reader.query 内存替身），禁触网禁写库禁写 data/。
核心不变式回归锚：
  1. 真源优先——只请求 advance_count=0 AND decline_count=0 的现值行（官方存量永不改写）；
  2. 整行回写——OHLC/volume/amount/name/quality_flag 原值保留，仅替换宽度二列；
  3. 不写 ingest_ts——DEFAULT now() 才能令新行成为 ReplacingMergeTree 版本赢家；
  4. 覆盖度防御/无聚合行/自算双零 → 跳过且留痕（禁静默零值）。
"""

from __future__ import annotations

import datetime

import pytest

from zephyr.data.implementations import index_breadth_compute as ibc
from zephyr.data.implementations.index_breadth_compute import (
    INDEX_UNIVERSE,
    MIN_COVERAGE,
    UNIVERSE_PREDICATES,
    WRITE_COLUMNS,
    IndexBreadthComputeProvider,
    agg_column_names,
    build_agg_columns,
    build_fill_rows,
    clean_symbols,
    parse_agg,
    parse_tsv,
    resolve_window,
)
from zephyr.data.provider_base import FetchPayload

_ALL_UNIS = sorted({u for u in INDEX_UNIVERSE.values()})


# ── 测试替身 ────────────────────────────────────────────────────────────


def _zero_row(symbol: str = "399106", d: str = "2026-09-15") -> dict[str, str]:
    return {
        "trade_date": d,
        "symbol": symbol,
        "name": "深证综指",
        "open": "2460.653",
        "high": "2477.8979",
        "low": "2441.312",
        "close": "2444.04",
        "volume": "530714505",
        "amount": "848733889794",
        "advance_count": "0",
        "decline_count": "0",
        "data_source": "miniqmt",
        "quality_flag": "1",
    }


def _zero_tsv(rows: list[dict[str, str]]) -> str:
    return "".join("\t".join(r[c] for c in WRITE_COLUMNS) + "\n" for r in rows)


def _agg_tsv(d: str = "2026-09-15", over: dict[str, tuple[int, int, int]] | None = None) -> str:
    """全宇宙聚合单行 TSV（adv/dec/n 同值，over 按宇宙覆写）。"""
    over = over or {}
    vals: list[str] = [d]
    for u in _ALL_UNIS:
        adv, dec, n = over.get(u, (520, 2354, 2874))
        vals += [str(adv), str(dec), str(n)]
    return "\t".join(vals) + "\n"


def _payload(start=datetime.date(2026, 9, 1), end=datetime.date(2026, 9, 16), extra=None, symbols=None):
    return FetchPayload(
        table="c1_market.kline_index",
        symbols=symbols,
        start=start,
        end=end,
        incremental=False,
        extra=extra if extra is not None else {"capability": "kline_index_breadth"},
    )


def _install_ch(monkeypatch, zero_tsv: str, agg_tsv: str):
    """CH 只读替身：按 SQL 特征分派（记录全部 SQL 供断言）。"""
    calls: list[str] = []

    def _query(sql: str, timeout: int = 30) -> str:
        calls.append(sql)
        if "countIf(ret > 0" in sql:
            return agg_tsv
        if "advance_count = 0 AND decline_count = 0" in sql:
            return zero_tsv
        raise AssertionError(f"未预期 SQL: {sql[:160]}")

    monkeypatch.setattr("zephyr.data.ch_reader.query", _query)
    return calls


def _fetch(payload) -> list:
    p = IndexBreadthComputeProvider()
    p.connect()
    try:
        return list(p.fetch(payload, None))
    finally:
        p.disconnect()


# ── 纯函数 ──────────────────────────────────────────────────────────────


def test_resolve_window_lookback_self_heals_across_month():
    """日频任务即使 scheduler 传月初 start，修复窗也被 lookback 拉早（跨月断档自愈）。"""
    start, end = resolve_window(datetime.date(2026, 9, 1), datetime.date(2026, 9, 16), 120)
    assert end == datetime.date(2026, 9, 16)
    assert start == datetime.date(2026, 5, 19) < datetime.date(2026, 9, 1)


def test_resolve_window_respects_floor():
    """地板 2019-01-01 兜底：显式大 lookback / 更早 start 均不得穿透（kline_daily 覆盖不足）。"""
    assert resolve_window(datetime.date(2026, 9, 1), datetime.date(2026, 9, 16), 20000)[0] == ibc.FLOOR_DATE
    assert resolve_window(datetime.date(2015, 1, 5), datetime.date(2026, 9, 16), 120)[0] == ibc.FLOOR_DATE


def test_clean_symbols_rejects_injection():
    assert clean_symbols(["399106", "1'; DROP TABLE x--", "39910", "399106"]) == ["399106"]


def test_build_agg_columns_unknown_universe_raises():
    with pytest.raises(ValueError, match="未注册宇宙"):
        build_agg_columns(["SZ", "MARS"])


def test_agg_columns_and_names_paired_order():
    """列片段与列名解析顺序严格同构（错位=adv 当 dec 用，必须钉扎）。"""
    unis = ["CY", "SZ"]
    cols = build_agg_columns(unis)
    names = agg_column_names(unis)
    assert names == ["trade_date", "adv_CY", "dec_CY", "n_CY", "adv_SZ", "dec_SZ", "n_SZ"]
    for n in names[1:]:
        assert f"AS {n}" in cols


def test_parse_tsv_short_line_skipped_and_strings_kept():
    rows = parse_tsv("2026-09-15\ta\n2026-09-16\tb", ["trade_date", "symbol"])
    assert rows == [{"trade_date": "2026-09-15", "symbol": "a"}, {"trade_date": "2026-09-16", "symbol": "b"}]
    assert parse_tsv("2026-09-15", ["trade_date", "symbol"]) == []  # 列数不足→丢弃并告警


def test_parse_agg_shapes():
    agg = parse_agg("2026-09-15\t520\t2354\t2874\n", ["SZ"])
    assert agg[("2026-09-15", "SZ")] == {"adv": 520, "dec": 2354, "n": 2874}


def test_build_fill_rows_preserves_official_fields_and_marks_provenance():
    rows, skipped = build_fill_rows([_zero_row()], {("2026-09-15", "SZ"): {"adv": 520, "dec": 2354, "n": 2874}})
    assert skipped == [] and len(rows) == 1
    r = dict(zip(WRITE_COLUMNS, rows[0]))
    assert r["advance_count"] == "520" and r["decline_count"] == "2354"
    assert r["data_source"] == ibc.DATA_SOURCE_MARKER
    orig = _zero_row()
    for col in ("trade_date", "symbol", "name", "open", "high", "low", "close", "volume", "amount", "quality_flag"):
        assert r[col] == orig[col]  # 真表既有值逐字段保留（零精度损失）


def test_write_columns_exclude_ingest_ts_and_materialized():
    """ingest_ts 必须缺省（DEFAULT now() 令新行胜出）；MATERIALIZED 列禁插（Code 44）。"""
    assert "ingest_ts" not in WRITE_COLUMNS
    assert "exchange" not in WRITE_COLUMNS and "symbol_canonical" not in WRITE_COLUMNS
    assert {"advance_count", "decline_count"} <= set(WRITE_COLUMNS)


def test_build_fill_rows_coverage_guard_skips_pipeline_anomaly_day():
    """n 低于宇宙阈值=kline_daily 断档日 → 不写（防半宇宙家数冒充官方全宇宙）。"""
    uni = INDEX_UNIVERSE["399106"]
    floor = MIN_COVERAGE[uni]
    rows, skipped = build_fill_rows(
        [_zero_row()], {(("2026-09-15"), uni): {"adv": 520, "dec": 10, "n": floor - 1}}
    )
    assert rows == [] and "覆盖度防御" in skipped[0]["reason"]


def test_build_fill_rows_skips_missing_agg_and_double_zero():
    rows, skipped = build_fill_rows([_zero_row()], {})
    assert rows == [] and "无 SZ 聚合行" in skipped[0]["reason"]
    rows, skipped = build_fill_rows([_zero_row()], {("2026-09-15", "SZ"): {"adv": 0, "dec": 0, "n": 2874}})
    assert rows == [] and "自算涨跌同为 0" in skipped[0]["reason"]


def test_build_fill_rows_unregistered_symbol_skipped():
    rows, skipped = build_fill_rows([_zero_row(symbol="999999")], {("2026-09-15", "SZ"): {"adv": 1, "dec": 1, "n": 2874}})
    assert rows == [] and "未注册宇宙" in skipped[0]["reason"]


def test_registry_caliber_anchors():
    """注册表锚：探针对拍选型结论钉扎（改口径=改真表数据，须显式动此断言）。"""
    assert INDEX_UNIVERSE["399106"] == "SZ"  # 深证综指=深市 A（corr 0.9999 mag 0.987）
    assert INDEX_UNIVERSE["399107"] == "SZ"  # 深证A指（corr 1.0 mag 1.001）
    assert INDEX_UNIVERSE["000001"] == "SH"
    assert INDEX_UNIVERSE["399006"] == "CY"
    assert "000905" not in INDEX_UNIVERSE  # 中证500 mag 4.088 → 宇宙口径不可复现，落选
    assert "399100" not in INDEX_UNIVERSE  # 新指数 口径无据，落选
    assert set(INDEX_UNIVERSE.values()) <= set(UNIVERSE_PREDICATES)
    assert set(INDEX_UNIVERSE.values()) <= set(MIN_COVERAGE)


# ── Provider（CH 注入） ────────────────────────────────────────────────


def test_fetch_reads_only_double_zero_rows_true_source_first(monkeypatch):
    """真源优先：读现值的 SQL 必须带双零谓词 + 限定注册表标的（官方有值行永不入列）。"""
    calls = _install_ch(monkeypatch, "", _agg_tsv())
    res = _fetch(_payload())
    assert len(res) == 1 and res[0].error is None
    read_sql = next(c for c in calls if "advance_count = 0 AND decline_count = 0" in c)
    assert "FROM c1_market.kline_index FINAL" in read_sql
    for sym in INDEX_UNIVERSE:
        assert f"'{sym}'" in read_sql


def test_fetch_end_to_end_produces_full_rows(monkeypatch):
    calls = _install_ch(monkeypatch, _zero_tsv([_zero_row()]), _agg_tsv())
    out = _fetch(_payload())[0]
    assert out.columns == WRITE_COLUMNS
    assert out.rows_fetched == len(out.rows) == 1
    assert dict(zip(out.columns, out.rows[0]))["advance_count"] == "520"
    assert out.last_key == "2026-09-16"
    agg_sql = next(c for c in calls if "countIf(ret > 0" in c)
    assert "c1_market.kline_daily" in agg_sql
    assert "market_type = 'A_share'" in agg_sql
    assert "lag(adj_close, 1) OVER (PARTITION BY symbol ORDER BY trade_date)" in agg_sql
    assert "isFinite(ret)" in agg_sql  # 组首行无前收→inf 滤除（新股首日不计涨跌）
    assert "advance_count = 0" not in agg_sql  # 聚合只出自算宇宙，不回读宽度列


def test_fetch_deep_lookback_expands_window_to_floor(monkeypatch):
    """回补模式：大 lookback 把窗口起点钉在地板日（历史缺口一次性修复）。"""
    calls = _install_ch(monkeypatch, "", _agg_tsv())
    out = _fetch(_payload(extra={"capability": "kline_index_breadth", "repair_lookback_days": 20000}))[0]
    assert out.error is None and out.rows == []
    agg_sql = next(c for c in calls if "countIf(ret > 0" in c)
    assert f"toDate('{ibc.FLOOR_DATE.isoformat()}')" in agg_sql


def test_fetch_single_symbol_only_queries_its_universe(monkeypatch):
    calls = _install_ch(monkeypatch, "", _agg_tsv(over={"CY": (300, 100, 400)}))
    out = _fetch(_payload(symbols=["399006"]))[0]
    agg_sql = next(c for c in calls if "countIf(ret > 0" in c)
    assert "AS adv_CY" in agg_sql and "AS adv_SZ" not in agg_sql
    assert out.error is None
    read_sql = next(c for c in calls if "advance_count = 0 AND decline_count = 0" in c)
    assert "'399006'" in read_sql and "'399106'" not in read_sql


def test_fetch_ch_failure_returns_error_not_raise(monkeypatch):
    def _boom(sql: str, timeout: int = 30) -> str:
        raise RuntimeError("CH 不可达")

    monkeypatch.setattr("zephyr.data.ch_reader.query", _boom)
    out = _fetch(_payload())[0]
    assert out.rows == [] and "CH 不可达" in (out.error or "")


def test_fetch_empty_agg_errors(monkeypatch):
    """聚合空=数据管道异常，必须以 error 暴露（禁静默 0 行 SUCCESS）。"""
    _install_ch(monkeypatch, "", "")
    out = _fetch(_payload())[0]
    assert out.rows == [] and "宇宙聚合空" in (out.error or "")


def test_fetch_empty_extra_no_crash(monkeypatch):
    """payload.extra=None（非调度器手工调用）不得 AttributeError。"""
    _install_ch(monkeypatch, "", _agg_tsv())
    out = _fetch(_payload(extra=None))[0]
    assert out.error is None
