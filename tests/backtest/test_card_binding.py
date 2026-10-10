# [BLUEPRINT] MOD-BT-248 | docs/03_modules/_domain_backtest/blueprint.md
# [TESTS] tests/backtest/test_card_binding.py
# [TTL] permanent
# 测试隔离：卡件/绑定册/分数册全在 tmp_path；信号面用 monkeypatch 合成（零 CH、零生产路径写）。
"""绑定层红蓝双向：分类拒绑口径/绑定册引句自闸/CH 让路钟闸/位置协议解析。

判别力声明（在册教训：判通过的脚本须先证明能红）——本文件里 CH 让路闸、
prose_quote 校验、缺 data_binding 拒绑三处都写了"应当拒"的正例，任何一条被写成恒过都会红。
"""

from __future__ import annotations

import datetime as dt
from pathlib import Path

import pandas as pd
import pytest
import yaml

from scripts.backtest.fexam import card_binding as cb


def _card(**kw) -> dict:
    base = {
        "schema_version": "1.0",
        "card_id": "TDM-E-TEST/calibration/02_x",
        "node_id": "TDM-E-TEST",
        "family": "calibration",
        "status": "preregistered",
        "signal_kind": "series",
        "window": {
            "in_sample": ["2020-01-01", "2023-12-31"],
            "oos": ["2024-01-01", "2025-06-30"],
            "regimes": {"bull": "2020-01-01..2021-12-31"},
        },
        "oos_window_ref": ["2024-01-01", "2025-06-30"],
        "buckets": {"type": "quantile_decile", "on": "当日信号值", "min_obs_per_bucket": 60},
        "pillars": {"ic_floor": "IC>=0.02"},
        "pillars_numeric": {
            "mono_spearman_min": 0.6,
            "ic_mean_min": 0.02,
            "ic_ir_min": 0.3,
            "regime_same_sign": True,
            "oos_same_sign": True,
        },
        "target": {"primary": "next_day_index_return（CSI300 次日收益）"},
        "hypothesis": "测试假设",
    }
    base.update(kw)
    return base


def _binding(**kw) -> dict:
    base = {
        "signal_table": "c1_market.kline_index",
        "signal_column": "close",
        "signal_derivation": "收盘水平（示例）",
        "target_source": "next_day_index_return",
        "data_window_evidence": "实测在案",
    }
    base.update(kw)
    return base


def test_missing_data_binding_is_class_U():
    r = cb.classify_card(_card())
    assert r["cls"] == "U" and r["reason"] == "no_data_binding_section"


def test_target_face_not_index_next_day_is_class_C():
    c = _card(data_binding=_binding(target_source="daily_net_returns → NAV → window_metrics"))
    assert cb.classify_card(c)["cls"] == "C"


def test_multi_day_horizon_refused_not_silently_examined():
    c = _card(data_binding=_binding(), target={"primary": "next_20day_sector_return"})
    r = cb.classify_card(c)
    assert r["cls"] == "C" and "horizon" in r["reason"]


def test_panel_deferred_and_unregistered_table_refused():
    p = _card(signal_kind="panel", data_binding=_binding())
    assert cb.classify_card(p)["cls"] == "B"
    t = _card(data_binding=_binding(signal_table="c1_market.technical_indicator"))
    r = cb.classify_card(t)
    assert r["cls"] == "A?" and "table_not_in_recipe_book" in r["reason"]


def test_local_csv_only_binds_on_exact_signal_column(tmp_path, monkeypatch):
    """回归用例：曾把 margin_flow 卡按全文关键词误牵到连板分布序列＝误绑出分形态。"""
    fake = tmp_path / "series"
    fake.mkdir()
    (fake / "streak_distribution.csv").write_text("trade_date,value\n2024-01-02,3\n", encoding="utf-8")
    (fake / "max_streak_height.csv").write_text("trade_date,value\n2024-01-02,3\n", encoding="utf-8")
    monkeypatch.setattr(cb, "SERIES_DIR", fake)
    good = _card(
        data_binding=_binding(
            signal_table="c1_market.limit_up_pool",
            signal_column="max_streak_height",
            signal_derivation="连板最高高度日度序列",
        )
    )
    bad = _card(
        card_id="TDM-E-TEST/calibration/07_margin",
        data_binding=_binding(
            signal_table="c1_market.margin_trading",
            signal_column="margin_balance",
            signal_derivation="余额变化与连板无关，仅文内出现 streak 字样",
        ),
    )
    assert cb.classify_card(good)["cls"] == "D"
    assert cb.classify_card(bad)["cls"] != "D"


def test_binding_book_refuses_prose_quote_absent_from_card():
    """反自造绿：绑定册引句不在卡面原文里即拒绑（算子不得替卡面说话）。"""
    c = _card(data_binding=_binding(signal_derivation="收盘水平（示例）"))
    entry = {"op": "downside_deviation_250_pctile", "prose_quote": "下行半偏差 = sqrt(244", "args": {}}
    with pytest.raises(ValueError, match="prose_quote_not_found_on_card"):
        cb.run_binding_book(c, entry)


def test_binding_book_refuses_unknown_op():
    c = _card(data_binding=_binding())
    with pytest.raises(ValueError, match="op_not_in_ops_book"):
        cb.run_binding_book(c, {"op": "made_up_op", "prose_quote": "收盘水平", "args": {}})


@pytest.mark.parametrize(
    ("stamp", "expect_refused"),
    [
        (dt.datetime(2026, 10, 10, 21, 0), True),
        (dt.datetime(2026, 10, 10, 22, 29), True),
        (dt.datetime(2026, 10, 10, 22, 30), False),
        (dt.datetime(2026, 10, 10, 23, 59), False),
        (dt.datetime(2026, 10, 11, 1, 0), True),
        (dt.datetime(2026, 10, 11, 3, 59), True),
        (dt.datetime(2026, 10, 11, 4, 0), False),
    ],
)
def test_ch_yield_window_clock_gate(stamp, expect_refused):
    got = cb._in_ch_yield_window(stamp)
    assert (got is not None) is expect_refused


def test_norm_handles_positional_protocol_and_null_empty_strings():
    df = pd.DataFrame({"c1": ["2024-01-02", "2024-01-03", "2024-01-03"], "c2": ["1.5", "", "2.5"]})
    s = cb._norm(df, 0, 1)
    assert list(s.index) == [pd.Timestamp("2024-01-02"), pd.Timestamp("2024-01-03")]
    assert float(s.iloc[0]) == 1.5 and float(s.iloc[1]) == 2.5  # 同日均值取末版，空串归 NaN 后被 drop


def test_rolling_pctile_warmup_is_nan_and_range_valid():
    s = pd.Series(range(30), index=pd.bdate_range("2024-01-01", periods=30), dtype=float)
    out = cb._rolling_pctile(s, 20)
    assert out.iloc[:19].isna().all()
    assert out.dropna().between(0.0, 1.0).all()


def test_run_one_skips_cards_not_in_approve_list(tmp_path):
    card = _card(data_binding=_binding())
    p = tmp_path / "c.yaml"
    p.write_text(yaml.safe_dump(card, allow_unicode=True), encoding="utf-8")
    r = cb.run_one(p, {"other"}, tmp_path / "scores.yaml", "t", True)
    assert r["skipped"] == "not_in_approve_list"


def test_limit_up_panel_sql_carries_card_frozen_face():
    """SQL 底座必须逐字承载卡 05/06 冻结式（自创口径=替卡面拍数，禁）：
    比值分母=lag(close)、缺前一交易日取哨兵永不判、limit_pct 缺失（无涨跌幅限制）永不判、
    is_lu_{t-1} 由 lag(lu) 给出、溢价截面=avgIf(ret_close, lu_prev=1)、容差走 {tol} 占位。"""
    s = cb.SQL_LIMIT_UP_PANEL
    assert "FINAL" in s
    assert "ifNull(limit_pct, 9.9)" in s
    assert "lagInFrame(k.c, 1, 0)" in s
    assert "if(lag_c > 0" in s
    assert "lagInFrame(lu, 1, 0)" in s
    assert "avgIf(ret_close, lu_prev = 1)" in s
    assert "{tol}" in s


def _panel() -> pd.DataFrame:
    idx = pd.to_datetime(["2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05"])
    return pd.DataFrame(
        {
            "n_lu": [0, 40, 50, 30],
            "n_lu_prev": [0, 0, 40, 25],
            "n_promo": [0, 0, 12, 10],
            "prem_close": [float("nan"), float("nan"), 0.02, 0.03],
            "prem_open": [float("nan"), float("nan"), 0.01, 0.015],
            "n_rows": [100, 200, 300, 400],
        },
        index=idx,
    )


def test_promotion_rate_den_is_prev_board_not_universe():
    """判别力正例：分母=昨板家数 40 ⇒ 12/40=0.30；若误取当日在市家数 300 ⇒ 0.04（涨停占比形）。"""
    rate, ev = cb.promotion_rate_from_panel(_panel(), 20)
    assert rate.loc[pd.Timestamp("2024-01-04")] == pytest.approx(12 / 40)
    assert rate.loc[pd.Timestamp("2024-01-04")] != pytest.approx(12 / 300)
    assert ev["days_below_set_floor"] == 2


def test_set_floor_drops_small_cross_section_and_counts_missing():
    """卡面「|S_{t-1}|<20 的日置 NaN」＋「停牌股不入截面均值并计缺失数」两面都要出数：
    2024-01-05 在架 25 < 在册昨板 50 ⇒ 缺失 25 票·日；分母 <20 的两日必须被剔掉。"""
    ser, ev = cb._apply_set_floor(_panel(), "prem_close", 20)
    assert [str(x.date()) for x in ser.index] == ["2024-01-04", "2024-01-05"]
    assert ev["suspended_missing_symbol_days"] == 25
    assert ev["days_below_set_floor"] == 2
    assert ev["rows_kept"] == 2


@pytest.mark.parametrize(
    ("op", "card_file"),
    [
        (
            "limit_up_premium_close_mean",
            "entry_flow/L1/TDM-E-L1-S3__calibration__05_limit_up_premium_derived.yaml",
        ),
        (
            "promotion_rate_from_limit_panel",
            "entry_flow/L1/TDM-E-L1-S3__calibration__06_promotion_rate_derived.yaml",
        ),
    ],
)
def test_ops_default_quote_is_verbatim_on_the_real_card(op, card_file):
    """反假绿：算子缺省引句必须是真卡 data_binding 原文子串（改引句/改卡面即红）。"""
    path = cb.CARDS_DIR / card_file
    card = yaml.safe_load(path.read_text(encoding="utf-8"))
    q = cb.OPS[op]["quote_key"]
    assert q.replace(" ", "") in cb._card_text(card).replace(" ", "")


def _vocab_cards(tmp_path):
    d = tmp_path / "cards"
    d.mkdir()
    (d / "a.yaml").write_text(
        yaml.safe_dump(
            {
                "card_id": "T-A",
                "family": "calibration",
                "status": "preregistered",
                "signal_kind": "series",
                "pillars_numeric": {"mono_spearman_min": 0.6, "car_t_stat_min": 2.0},
                "pillars": {"lag_profile": "x"},
            },
            allow_unicode=True,
        ),
        encoding="utf-8",
    )
    (d / "b.yaml").write_text(
        yaml.safe_dump(
            {
                "card_id": "T-B",
                "family": "comparison",
                "status": "preregistered",
                "signal_kind": "panel",
                "pillars_numeric": {"sharpe_delta_min": 0.1, "mono_spearman_min": 0.6},
            }
        ),
        encoding="utf-8",
    )
    (d / "c.yaml").write_text(
        yaml.safe_dump({"card_id": "T-C", "family": "calibration", "status": "empty"}), encoding="utf-8"
    )
    (d / "e.yaml").write_text(
        yaml.safe_dump(
            {
                "card_id": "T-E",
                "family": "comparison",
                "status": "preregistered",
                "signal_kind": "panel",
                "pillars_numeric": {"sharpe_delta_min": 0.1, "tail_ratio_min": 0.3},
            }
        ),
        encoding="utf-8",
    )
    (d / "not_a_card.md").write_text("x", encoding="utf-8")
    return d


def test_vocab_census_is_machine_generated_and_zero_write(tmp_path):
    """普查件四钉：①按 pillars_route 分侧取词表（a 卡走校准判官→car_t_stat_min 列外）；
    ②裁定①并集词表后，混形卡（b 卡：NAV 柱＋校准柱）走双臂判官且校准柱已在词表内＝不再列越表
    ——这条断言就是"另一侧门柱从此有判官接手"的可执行证明；
    ③两侧都不认的越表柱（e 卡 tail_ratio_min）在双臂判官下仍须点名，证明并集没把闸放宽；
    ④无机判面卡单独计数不编造＋discipline 三面零（阈值/卡件/CH 全 0，普查只列键名不改值）。"""
    out = cb.build_vocab_census(_vocab_cards(tmp_path))
    assert out["card_total"] == 4
    assert out["cards_without_numeric_face"] == 1
    by_id = {r["card_id"]: r for r in out["rows"]}
    assert by_id["T-A"]["keys_outside_route_vocab"] == ["car_t_stat_min"]
    assert by_id["T-A"]["route"] == "series"
    assert by_id["T-A"]["prose_pillar_keys"] == ["lag_profile"]
    assert "T-B" not in by_id
    assert by_id["T-E"]["route"] == "dual_arm"
    assert by_id["T-E"]["keys_outside_route_vocab"] == ["tail_ratio_min"]
    assert out["unique_keys_outside_vocab"] == 2
    assert out["discipline"]["threshold_values_written"] == 0
    assert out["discipline"]["cards_modified"] == 0
    assert out["discipline"]["ch_queries"] == 0


def test_vocab_census_vocab_sources_read_from_core_constants():
    """词表两侧必须直读执行核常量（复制定义=普查与判决漂移，改一处即红）。"""
    from fexam.calibration_exam import _CALIBRATION_JUDGED_KEYS, _UNION_PILLAR_KEYS

    out = cb.build_vocab_census(cb.CARDS_DIR)
    assert set(out["vocab_sources"]["series"]) == set(_CALIBRATION_JUDGED_KEYS)
    assert set(out["vocab_sources"]["dual_arm"]) == set(_UNION_PILLAR_KEYS)


def _fake_csv(monkeypatch, vals, start="2020-01-01"):
    idx = pd.bdate_range(start, periods=len(vals))
    ser = pd.Series(vals, index=idx)
    monkeypatch.setattr(cb, "_load_csv_series", lambda name: ser)
    return ser


def test_event_flag_excludes_warmup_and_is_binary(monkeypatch):
    """滚动分位底座：暖机段（min_periods 未满）必须无读数，不得用前期值冒充事件日；输出只允许 {0,1}。"""
    ser = _fake_csv(monkeypatch, list(range(400)))
    card = {"data_binding": {"signal_column": "x_event_flag"}}
    flag, ev = cb.op_event_flag_rolling_pctile(card, {"base_csv": "x.csv", "pctile_window": 60, "pct_threshold": 0.9})
    assert ev["warmup_dropped_days"] == 59
    assert set(flag.unique()) <= {0.0, 1.0}
    assert ev["n_event_days"] == int((flag > 0).sum()) and ev["n_event_days"] > 0
    assert ev["pit_statement"].startswith("事件判定只用 t 及以前")


def test_event_flag_is_pit_invariant_to_future_values(monkeypatch):
    """判别力正例（反未来函数）：改动 t 之后的基序列取值，t 及之前的事件标记必须一字不变。
    若实现用了全样本分位（用未来定过去门槛），本支必红。"""
    vals = [float(v % 37) for v in range(300)]
    ser = _fake_csv(monkeypatch, vals)
    card = {"data_binding": {"signal_column": "x_event_flag"}}
    args = {"base_csv": "x.csv", "pctile_window": 50, "pct_threshold": 0.8}
    f1, _ = cb.op_event_flag_rolling_pctile(card, args)
    cut = ser.index[180]
    bumped = ser.copy()
    bumped.loc[bumped.index >= cut] = 999.0
    monkeypatch.setattr(cb, "_load_csv_series", lambda name: bumped)
    f2, _ = cb.op_event_flag_rolling_pctile(card, args)
    common = f1.index.intersection(f2.index)
    before = common[common <= cut]
    assert (f1.loc[before] == f2.loc[before]).all(), "未来值改动了过去的事件标记＝全样本分位（事后挪门柱形态）"


def test_event_flag_base_selection_fail_closed():
    """底座二选一硬闸：base_op 与 base_csv 同时给或同时不给 ⇒ 直接拒（禁第三条取数路静默生效）；
    base_op 不在算子册 ⇒ 点名拒（防绑到不存在的算子上冒充分数）。"""
    card = {"data_binding": {"signal_column": "x"}}
    for args in (
        {"pctile_window": 50, "pct_threshold": 0.9},
        {"base_csv": "a.csv", "base_op": "daily_agg_series", "pctile_window": 50, "pct_threshold": 0.9},
    ):
        with pytest.raises(ValueError):
            cb.op_event_flag_rolling_pctile(card, args)
    with pytest.raises(ValueError) as ei:
        cb.op_event_flag_rolling_pctile(card, {"base_op": "no_such_op", "pctile_window": 50, "pct_threshold": 0.9})
    assert "base_op_not_in_ops_book" in str(ei.value)
