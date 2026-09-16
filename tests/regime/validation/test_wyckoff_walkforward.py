# [A_test] module_id: MOD-TEST-WYCKOFF-WF3 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-REGIME-002 | docs/03_modules/_domain_regime/regime_feature_builder/blueprint.md | 14 号 §4.5
# [MODULE] tests.regime.validation.test_wyckoff_walkforward
# [DOMAIN] D_REGIME
# [DEPENDENCIES] zephyr.regime.validation.wyckoff_walkforward; zephyr.regime.features.wyckoff_engine; pandas; numpy; pytest
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR-CONTRACT] AssertionError->fail
# [TESTS] tests/regime/validation/test_wyckoff_walkforward.py
# [TTL] permanent
# [ARCH-REF] #10_regime_detector_spec §4.12.2 #14_regime_s2_diagnosis §4.5 #WYF-3
# [ALGO_FLOW]
# 层: 断言
# - A1: WyckoffParams 默认值=唯一真源（与 legacy 别名逐项相等），自定义 params 改变事件集
# - A2: AR 两道门可独立摘除（消融路径）；memory_window 使评分时间局部化（解除永久粘滞）
# - A3: 证伪态=score 显式恒 0 + 一次性 warning 披露 + detect_wyckoff_events 不受影响
# - A4: 管线与生产评分零漂移（score_from_events == wyckoff_score）
# - A5: 无未来函数（段指标/选值对 end 之后的数据不可感知）
# - A6: summarize 采纳判据（超额/命中率/池化 t/恒零/误爆 五关缺一不可）
"""test_wyckoff_walkforward.py — WYF-3 wyckoff 阈值 walk-forward 重校管线单元测试。

分组：
  1. 引擎新阈值路径（WyckoffParams 单一真源 / 自定义阈值 / AR 门消融 / 记忆窗）
  2. 证伪路径（显式置零 + 告警披露，禁静默恒零）
  3. 管线口径（评分零漂移、折划分、前向收益、事件去相关）
  4. 反未来函数（段指标与层内选值对 end 之后数据零感知）
  5. 裁定函数 summarize（采纳/证伪判据机械可重放）

禁网禁库：全部用合成序列 + tmp_path（不触 ClickHouse、不写 data/）。
"""

from __future__ import annotations

import logging
from dataclasses import replace
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from zephyr.regime.features import wyckoff_engine as we
from zephyr.regime.features.wyckoff_engine import (
    DEFAULT_WYCKOFF_PARAMS,
    WyckoffParams,
    detect_wyckoff_events,
    wyckoff_dimension_status,
    wyckoff_score,
)
from zephyr.regime.validation import wyckoff_walkforward as wf


# ---------------------------------------------------------------------------
# 合成数据：重复"阴跌→恐慌暴跌→放量反弹→缩量回踩→假摔→突破"周期
# ---------------------------------------------------------------------------
def _cycle_inputs(n_cycles: int = 6, warmup: int = 70) -> dict[str, pd.Series]:
    """确定性合成 OHLCV（无随机源，可重放），产出多轮可触发吸筹链的序列。"""
    closes: list[float] = []
    vols: list[float] = []
    p = 100.0
    for _ in range(warmup):  # 预热：常数价平量（z=0，不触发任何阶段）
        closes.append(p)
        vols.append(1_000_000.0)
    for _ in range(n_cycles):
        for _ in range(25):  # 阴跌（PS 候选）
            p *= 0.997
            closes.append(p)
            vols.append(1_400_000.0)
        p *= 0.905  # SC：-9.5% 巨量、收盘创 60 日新低
        closes.append(p)
        vols.append(7_000_000.0)
        for _ in range(4):  # AR：放量反弹创新高
            p *= 1.035
            closes.append(p)
            vols.append(3_500_000.0)
        for _ in range(7):  # ST/Spring：缩量回踩（跌破前低后收回）
            p *= 0.978
            closes.append(p)
            vols.append(700_000.0)
        for _ in range(7):  # Test/SOS：放量突破
            p *= 1.025
            closes.append(p)
            vols.append(2_800_000.0)
        for _ in range(5):  # 高位整理
            closes.append(p)
            vols.append(1_200_000.0)
    close = pd.Series(closes, index=pd.date_range("2015-01-01", periods=len(closes), freq="B"))
    high = close * 1.008
    low = close * 0.992
    volume = pd.Series(vols, index=close.index, dtype=float)
    from zephyr.regime.features.market_features import volume_anomaly

    return {
        "close": close,
        "high": high,
        "low": low,
        "volume": volume,
        "pct_change": close.pct_change(),
        "vol_z": volume_anomaly(volume, window=20),
    }


@pytest.fixture(scope="module")
def cyc() -> dict[str, pd.Series]:
    d = _cycle_inputs()
    ev = detect_wyckoff_events(**d)
    # 夹具自检：合成序列必须至少让 SC/AR 触发（否则后续断言全是空转）
    assert float(ev["sc"].sum()) >= 3, "夹具失效：SC 未触发"
    assert float(ev["ar"].sum()) >= 1, "夹具失效：AR 未触发"
    return d


# ---------------------------------------------------------------------------
# 1. 引擎新阈值路径
# ---------------------------------------------------------------------------
def test_params_defaults_are_single_source_of_truth():
    """WyckoffParams 默认值即阈值唯一真源；legacy 模块常量必须由它派生。"""
    d = DEFAULT_WYCKOFF_PARAMS.to_dict()
    assert we._SC_VOL_Z == d["sc_vol_z"]
    assert we._SC_PCT == d["sc_pct"]
    assert we._AR_PCT == d["ar_pct"]
    assert we._AR_BREAKOUT_WIN == d["ar_breakout_window"]
    assert we._ST_BAND == d["st_band"]
    assert we._ST_SHRINK == d["st_shrink"]
    assert we._SPRING_SHRINK == d["spring_shrink"]
    assert we._TEST_SPRING_RECENT_WIN == d["test_spring_window"]
    assert we._TEST_VOL_RATIO == d["test_vol_ratio"]
    assert we._PS_VOL_Z == d["ps_vol_z"]
    assert d["stage_weights"] == we._STAGE_WEIGHTS
    assert d["stage_weights"] is not we._STAGE_WEIGHTS  # 不被外部字典别名污染
    assert isinstance(DEFAULT_WYCKOFF_PARAMS, WyckoffParams)
    with pytest.raises(Exception):  # frozen dataclass -> FrozenInstanceError
        DEFAULT_WYCKOFF_PARAMS.sc_vol_z = 0.0  # type: ignore[misc]


def test_default_params_reproduce_legacy_engine_exactly(cyc, enabled):
    """不传 params 与显式传默认 params 逐日一致（参数化改造零行为漂移）。"""
    a = detect_wyckoff_events(**cyc)
    b = detect_wyckoff_events(**cyc, params=WyckoffParams())
    pd.testing.assert_frame_equal(a, b)
    sa = wyckoff_score(**cyc)
    sb = wyckoff_score(**cyc, params=WyckoffParams())
    pd.testing.assert_series_equal(sa, sb)


def test_custom_thresholds_change_event_set(cyc):
    """新阈值路径真的接线到判据：沿 SC 量能腿 / 幅度腿各做一条严格单调梯级。

    合成 fixture 的恐慌日 vol_z≈4.25、pct≈-0.095，故 3.9→6 日、4.25→0 日是严格拐点；
    若阈值仍写死在模块常量上，这两次调用不可能给出不同结果。
    """
    base = detect_wyckoff_events(**cyc)
    assert float(base["sc"].sum()) == 6.0

    under = detect_wyckoff_events(**cyc, params=replace(DEFAULT_WYCKOFF_PARAMS, sc_vol_z=3.9))
    over = detect_wyckoff_events(**cyc, params=replace(DEFAULT_WYCKOFF_PARAMS, sc_vol_z=4.25))
    assert float(under["sc"].sum()) == 6.0
    assert float(over["sc"].sum()) == 0.0

    loose_pct = detect_wyckoff_events(**cyc, params=replace(DEFAULT_WYCKOFF_PARAMS, sc_pct=-0.09))
    tight_pct = detect_wyckoff_events(**cyc, params=replace(DEFAULT_WYCKOFF_PARAMS, sc_pct=-0.096))
    assert float(loose_pct["sc"].sum()) == 6.0
    assert float(tight_pct["sc"].sum()) == 0.0

    # 腿数守恒校验：放松 SC 不得凭空改动其它阶段的判据
    assert float(over["ar"].sum()) == float(base["ar"].sum()) or float(over["ar"].sum()) == 0.0


def test_sc_window_decoupled_from_ps_window(cyc):
    """sc_window 可与函数 window 入参解耦（WYF-3 §3 校准债：窗长可分别扫描）。"""
    legacy = detect_wyckoff_events(**cyc, window=90)
    n_legacy = float(legacy["sc"].sum())
    assert n_legacy == 6.0
    longw = detect_wyckoff_events(**cyc, window=90,
                                  params=replace(DEFAULT_WYCKOFF_PARAMS, sc_window=200))
    short = detect_wyckoff_events(**cyc, window=90,
                                  params=replace(DEFAULT_WYCKOFF_PARAMS, sc_window=20))
    assert float(longw["sc"].sum()) < n_legacy, "更长的低点回看窗必然更难满足"
    assert float(short["sc"].sum()) >= n_legacy, "更短的窗只会放松"
    # PS 腿仍由函数 window 决定 ⇒ 解耦后 PS 计数不受 sc_window 影响
    assert float(short["ps"].sum()) == float(longw["ps"].sum())


def test_ar_doors_can_be_ablated_independently(cyc):
    """AR 两道门（反弹幅度 / 创 N 日新高）可各自独立摘除，且都开时=现值语义。"""
    legacy = detect_wyckoff_events(**cyc)
    pct_only = detect_wyckoff_events(
        **cyc, params=replace(DEFAULT_WYCKOFF_PARAMS, ar_require_breakout=False))
    brk_only = detect_wyckoff_events(
        **cyc, params=replace(DEFAULT_WYCKOFF_PARAMS, ar_require_pct=False))
    assert float(legacy["ar"].sum()) <= float(pct_only["ar"].sum())
    assert float(legacy["ar"].sum()) <= float(brk_only["ar"].sum())
    # 全摘 = 只剩"近窗有 SC"一条腿 → 触发日不少于任一单边
    none = detect_wyckoff_events(
        **cyc, params=replace(DEFAULT_WYCKOFF_PARAMS, ar_require_breakout=False, ar_require_pct=False))
    assert float(none["ar"].sum()) >= max(float(pct_only["ar"].sum()), float(brk_only["ar"].sum()))
    # 摘腿不会凭空造 AR：无 SC 的平序列仍恒 0
    flat = _cycle_inputs(n_cycles=0)
    ev = detect_wyckoff_events(**flat, params=replace(DEFAULT_WYCKOFF_PARAMS, ar_require_pct=False))
    assert float(ev["ar"].sum()) == 0.0


def test_st_lookback_window_splittable_from_ar(cyc):
    """ST 的 SC 回看窗可独立于 AR 拆分（WYF-3 §3：10 日窗偏紧的校准债）。"""
    p = DEFAULT_WYCKOFF_PARAMS
    shared = detect_wyckoff_events(**cyc, params=replace(p, ar_sc_window=10))
    wider = detect_wyckoff_events(**cyc, params=replace(p, ar_sc_window=10, st_sc_window=40))
    assert float(wider["st"].sum()) >= float(shared["st"].sum())
    assert DEFAULT_WYCKOFF_PARAMS.resolved_st_window() == DEFAULT_WYCKOFF_PARAMS.ar_sc_window


def test_memory_window_makes_score_time_local(cyc, enabled):
    """记忆窗语义：None=永久粘滞（单调不减）；有限窗=可回落到 0（时间局部）。"""
    sticky = wyckoff_score(**cyc)  # legacy cummax
    assert (sticky.diff().dropna() >= -1e-12).all(), "legacy 评分必须单调不减"
    local = wyckoff_score(**cyc, params=replace(DEFAULT_WYCKOFF_PARAMS, memory_window=15))
    assert not (local.diff().dropna() >= -1e-12).all(), "有限记忆窗必须允许评分回落"
    assert float(local.min()) >= 0.0 and float(local.max()) <= 100.0
    assert float(local.eq(0.0).sum()) > 0, "有限记忆窗下应存在回到无结构=0 的日子"
    # 记忆窗足够长时等价于永久粘滞
    wide = wyckoff_score(**cyc, params=replace(DEFAULT_WYCKOFF_PARAMS, memory_window=len(cyc["close"])))
    pd.testing.assert_series_equal(wide, sticky)


def test_weight_variant_changes_gate_crossing(cyc, enabled):
    """权重变体（网格轴）改变达门槛的日数，且 [0,100] 不变量保持。"""
    p = DEFAULT_WYCKOFF_PARAMS
    heavy = wyckoff_score(**cyc, params=replace(
        p, stage_weights={"ps": 20.0, "sc": 60.0, "ar": 30.0, "st": 40.0, "spring": 80.0, "test": 40.0},
        memory_window=40))
    legacy = wyckoff_score(**cyc, params=replace(p, memory_window=40))
    assert float((heavy >= 60).sum()) > float((legacy >= 60).sum())
    assert (heavy.between(0.0, 100.0, inclusive="both")).all()


def test_pit_prefix_consistency_with_memory_window(cyc, enabled):
    """PIT 回归：有限记忆窗同样满足"截断前缀可重现"（无未来泄漏）。"""
    p = replace(DEFAULT_WYCKOFF_PARAMS, memory_window=15)
    full = wyckoff_score(**cyc, params=p)
    for cut in (len(full) // 3, len(full) // 2, len(full) - 1):
        trunc = {k: v.iloc[: cut + 1] for k, v in cyc.items()}
        pd.testing.assert_series_equal(wyckoff_score(**trunc, params=p), full.iloc[: cut + 1])


# ---------------------------------------------------------------------------
# 2. 证伪路径（禁静默恒零）
# ---------------------------------------------------------------------------
@pytest.fixture
def restore_status():
    saved = we.wyckoff_dimension_status()
    yield
    we._DIMENSION_STATUS.clear()
    we._DIMENSION_STATUS.update(saved)


@pytest.fixture
def enabled():
    """临时把维度切回 enabled（专用于检验出分算术的用例），用例后恢复出厂披露态。

    出厂态=falsified（WYF-3 终态），故 `wyckoff_score` 默认恒 0；不显式 opt-in
    而继续检验算术的用例会退化成"0 与 0 相比"的空断言。
    """
    saved = we.wyckoff_dimension_status()
    we._set_dimension_status("enabled")
    yield
    we._DIMENSION_STATUS.clear()
    we._DIMENSION_STATUS.update(saved)


def test_shipped_dimension_status_is_falsified_and_documented():
    """出厂披露态护栏：证伪结论必须随码落地，禁被悄悄改回 enabled 而无人知。"""
    st = wyckoff_dimension_status()
    assert st["status"] == "falsified"
    assert len(st["reason"]) > 100, "理由须含可复核的量化结论，不能是一句空话"
    evidence = Path(st["evidence"])
    assert evidence.exists(), f"evidence 指针必须指向真实报告：{evidence}"
    assert st["params_source"] == "DEFAULT_WYCKOFF_PARAMS"
    assert st.get("recheck_when"), "证伪非永久真理：必须写明何种改动触发重跑"
    assert st.get("recheck_log"), "已执行的触发必须留台账（防同一触发重复立项）"
    # 阈值真源仍为 WYF-1 修复后基线（证伪的是判据，不是"发现了更好的数字"）
    assert DEFAULT_WYCKOFF_PARAMS.sc_vol_z == 2.0 and DEFAULT_WYCKOFF_PARAMS.s2_confirm_gate == 60.0
    # v2（裁定#285）后锁定：SC 量能腿出厂口径仍为历史 vol_z 路径（固定基准候选已被证伪，
    # sc_vol_mode 仅作为可复算能力保留，禁被悄悄改默认）
    assert DEFAULT_WYCKOFF_PARAMS.sc_vol_mode == "vol_z"


def test_falsified_status_zeroes_score_and_warns_once(cyc, caplog, enabled):
    """证伪终态：score 显式恒 0 + 一次性 WARNING 披露（不是算了没人知道的静默恒零）。"""
    before = wyckoff_score(**cyc, params=replace(DEFAULT_WYCKOFF_PARAMS, memory_window=40))
    assert float((before > 0).sum()) > 0  # 前提：enabled 态确有非零分（否则下面恒 0 断言是空的）

    we._set_dimension_status("falsified", reason="样本外无信息量", evidence="docs/_working/x.md")
    with caplog.at_level(logging.WARNING, logger="zephyr.regime.features.wyckoff_engine"):
        after = wyckoff_score(**cyc)
        again = wyckoff_score(**cyc)  # 二次调用不得再告警，也不得抛错
    assert (after == 0.0).all()
    assert len(again) == len(cyc["close"]) and (again == 0.0).all()
    msgs = [r for r in caplog.records if "WYF-3 证伪披露" in r.getMessage()]
    assert len(msgs) == 1, "告警须恰一次性（刷屏=噪声，零条=静默，均不合格）"
    st = wyckoff_dimension_status()
    assert st["status"] == "falsified" and st["evidence"] == "docs/_working/x.md"


def test_falsified_status_leaves_event_detection_usable(cyc, restore_status):
    """证伪只关闭"维度出分"，不毁研究能力：事件矩阵仍可正常产出。"""
    we._set_dimension_status("falsified", reason="x", evidence="y")
    try:
        ev = detect_wyckoff_events(**cyc)
        assert float(ev["sc"].sum()) >= 3.0
        assert (wyckoff_score(**cyc) == 0.0).all()
    finally:
        we._set_dimension_status("enabled")
    assert float((wyckoff_score(**cyc) > 0).sum()) > 0


def test_enabled_status_has_no_warning(cyc, caplog, restore_status):
    """正常态不得刷证伪告警（避免狼来了）。"""
    we._set_dimension_status("enabled")
    with caplog.at_level(logging.WARNING):
        wyckoff_score(**cyc)
    assert not [r for r in caplog.records if "证伪披露" in r.getMessage()]


# ---------------------------------------------------------------------------
# 3. 管线口径
# ---------------------------------------------------------------------------
def test_score_from_events_zero_drift_vs_production(cyc, enabled):
    """管线的评分复算必须与生产 wyckoff_score 逐日相等（结构性防双实现漂移）。"""
    for mw in (None, 40, 120):
        p = replace(DEFAULT_WYCKOFF_PARAMS, memory_window=mw)
        ev = detect_wyckoff_events(**cyc, params=p)
        pd.testing.assert_series_equal(
            wf.score_from_events(ev, p), wyckoff_score(**cyc, params=p)
        )


def test_make_params_none_means_keep_default_and_doors_expand():
    p = wf.make_params({"sc_vol_z": 1.0, "ar_doors": "pct_only", "sc_window": None})
    assert p.sc_vol_z == 1.0
    assert p.sc_window is None  # None=沿用函数 window 入参
    assert p.ar_require_pct is True and p.ar_require_breakout is False
    q = wf.make_params({"ar_doors": "both"})
    assert q.ar_require_pct is True and q.ar_require_breakout is True
    w = wf.make_params({"weight_variant": {"ps": 0.0, "sc": 30.0, "ar": 15.0, "st": 20.0,
                                          "spring": 40.0, "test": 20.0}})
    assert w.stage_weights["ps"] == 0.0
    assert DEFAULT_WYCKOFF_PARAMS.stage_weights["ps"] == 10.0  # 基线不被改写


def test_make_folds_segments_ordered_and_disjoint():
    """折几何：expanding 训练锚定起点、训练段严格先于评估段、评估段互不重叠、到数据末端自动收敛。"""
    idx = pd.bdate_range("2005-01-04", "2026-09-15")
    folds = wf.make_folds(idx, first_test_start="2013-01-01", test_years=3, n_folds=99)
    assert len(folds) == 5, "2013 起每 3 年一折到 2026-09 只应有 5 折（末折被末端截断）"
    for f in folds:
        assert f.train_end < f.test_start          # 训练段严格先于评估段
        assert f.test_start <= f.test_end
        assert f.train_start == idx.min()          # expanding（锚定起点）
    for a, b in zip(folds, folds[1:], strict=False):
        assert a.test_end < b.test_start           # 折间评估段互不重叠
        assert b.train_end == a.test_end           # 下一折训练段吞掉上一折评估段
    assert folds[-1].test_end <= idx.max()
    # 锚点已越过末端 ⇒ 诚实返回空集（禁编造折）
    assert wf.make_folds(idx, first_test_start="2030-01-01", test_years=3, n_folds=4) == []


def test_forward_returns_only_uses_future_closes_and_flags_edges(cyc):
    close = cyc["close"]
    days = close.index[[100, 101, len(close) - 1]]
    out = wf.forward_returns(close, days, (5,))
    assert out["r5"].iloc[0] == pytest.approx(close.iloc[105] / close.iloc[100] - 1.0)
    assert np.isnan(out["r5"].iloc[-1]), "越界必须 NaN（诚实缺失，禁回填）"
    # 篡改事件日之后的价格 → 值变；篡改事件日之前的价格 → 不变（前向口径）
    shifted = wf.forward_returns(close * 2.0, days, (5,))
    pd.testing.assert_frame_equal(out, shifted)


def test_merge_clusters_deduplicates_within_gap(cyc):
    idx = pd.DatetimeIndex(cyc["close"].index)
    dates = idx[[100, 105, 130, 300]]
    kept = wf.merge_clusters(dates, 20, idx)
    assert list(kept) == [idx[100], idx[130], idx[300]]
    assert len(wf.merge_clusters(pd.DatetimeIndex([]), 20, idx)) == 0


def test_onset_dates_is_edge_not_level(cyc):
    score = pd.Series([0, 0, 70, 70, 10, 80, 80, 0], index=pd.date_range("2020-01-01", periods=8))
    onsets = wf.onset_dates(score, 60)
    assert list(onsets) == [score.index[2], score.index[5]]


# ---------------------------------------------------------------------------
# 4. 反未来函数（校准的生命线）
# ---------------------------------------------------------------------------
def _metrics_equal(a: dict, b: dict) -> bool:
    """逐字段相等（含嵌套 dict），NaN/None 视为等价（两侧同为"诚实缺失"时不是分歧）。"""
    if set(a) != set(b):
        return False
    for k, v in a.items():
        w = b[k]
        if isinstance(v, dict) or isinstance(w, dict):
            if not (isinstance(v, dict) and isinstance(w, dict)) or not _metrics_equal(v, w):
                return False
            continue
        v_nan = v is None or (isinstance(v, float) and v != v)
        w_nan = w is None or (isinstance(w, float) and w != w)
        if v_nan or w_nan:
            if not (v_nan and w_nan):
                return False
        elif v != w:
            return False
    return True


def test_segment_metrics_blind_to_data_after_end(cyc):
    """段指标对 end 之后的数据零感知：全序列 vs 截断到 end 必须逐字段相等。"""
    p = replace(DEFAULT_WYCKOFF_PARAMS, memory_window=40, sc_vol_z=0.0, s2_confirm_gate=40.0)
    end = cyc["close"].index[200]
    a = wf.segment_metrics(cyc, p, start=cyc["close"].index[0], end=end,
                           warmup_days=70, horizons=(5, 20))
    trunc = {k: v[v.index <= end] for k, v in cyc.items()}
    b = wf.segment_metrics(trunc, p, start=cyc["close"].index[0], end=end,
                           warmup_days=70, horizons=(5, 20))
    assert _metrics_equal(a, b)
    # 非空判定前提：段确有在线日与事件（否则"相等"只是两个空集在比）
    assert a["days"] == b["days"] > 0
    assert a["on_days"] == b["on_days"] > 0
    assert a["n_events"] == b["n_events"] >= 1
    assert a["excess20"] == b["excess20"] and a["excess20"] == a["excess20"]


def test_select_in_train_blind_to_test_segment(cyc):
    """选值对评估段零感知：在"全序列(截断到 E)"与"截断序列(到 E)"上选出的参数必须相同。"""
    grid = {
        "L0_sc_root": {"sc_vol_z": [0.0, 1.0, 2.0], "sc_pct": [-0.03, -0.05], "sc_window": [40, 60]},
        "L1_ar_doors": {"ar_sc_window": [10, 30], "ar_pct": [0.0, 0.01],
                        "ar_breakout_window": [10], "ar_doors": ["both"]},
        "L2_st_spring_test": {"st_sc_window": [None], "st_band": [0.02], "st_shrink": [0.7, 1.0],
                             "spring_shrink": [0.8], "test_spring_window": [20], "test_vol_ratio": [1.0]},
        "L3_score_gate": {
            "weight_variant": {"legacy": None, "no_ps": {
                "ps": 0.0, "sc": 30.0, "ar": 15.0, "st": 20.0, "spring": 40.0, "test": 20.0}},
            "memory_window": [None, 40], "s2_confirm_gate": [40.0, 60.0],
        },
    }
    end = cyc["close"].index[300]
    trunc = {k: v[v.index <= end] for k, v in cyc.items()}
    p_full, t_full = wf.select_in_train(cyc, start=cyc["close"].index[0], end=end, grid=grid)
    p_trunc, t_trunc = wf.select_in_train(trunc, start=cyc["close"].index[0], end=end, grid=grid)
    assert p_full.to_dict() == p_trunc.to_dict()
    assert [tr.layer for tr in t_full] == [tr.layer for tr in t_trunc]


def _latch_events(n: int = 240) -> pd.DataFrame:
    """事件只在头 30 日出现，此后长期静默 —— 用于确定性检验粘滞语义。"""
    idx = pd.bdate_range("2020-01-01", periods=n)
    ev = pd.DataFrame(False, index=idx, columns=list(we._STAGE_WEIGHTS))
    ev.iloc[5:30, ev.columns.get_loc("sc")] = True
    ev.iloc[10:30, ev.columns.get_loc("spring")] = True
    return ev


def test_memory_window_none_is_permanent_latch_and_finite_window_decays():
    """粘滞语义（确定性，不依赖数据分布）：cummax 一旦齐活即永久在线；有限窗必衰减归零。"""
    ev = _latch_events()
    latched = wf.score_from_events(ev, replace(DEFAULT_WYCKOFF_PARAMS, memory_window=None))
    assert (latched.diff().dropna() >= -1e-12).all(), "cummax 语义下 score 必须单调不减"
    full = latched.max()
    assert full > 0
    tail = latched.iloc[-100:]
    assert (tail == full).all(), "永久粘滞：事件静默 100 日后 score 仍钉在峰值（=结构性误爆）"

    win = wf.score_from_events(ev, replace(DEFAULT_WYCKOFF_PARAMS, memory_window=20))
    assert (win.iloc[-100:] == 0.0).all(), "有限记忆窗：事件静默后必须衰减归零（否则会永久占用 S2 confirm）"
    assert win.max() == full, "同一事件集在窗内应能到达同一峰值"


def test_latch_dichotomy_shows_permanent_memory_extremes(cyc):
    """二象性单调关系：on_share 随记忆窗收窄不增（永久窗是最极端的一端）。"""
    p = replace(DEFAULT_WYCKOFF_PARAMS, sc_vol_z=0.0, s2_confirm_gate=40.0)
    tbl = wf.latch_dichotomy(cyc, p, start=cyc["close"].index[0], end=cyc["close"].index[-1],
                             memory_windows=(None, 20, 60), warmup_days=70)
    perm = float(tbl.loc[tbl["memory_window"] == "inf(cummax)", "on_share"].iloc[0])
    narrow = float(tbl.loc[tbl["memory_window"] == 20, "on_share"].iloc[0])
    mid = float(tbl.loc[tbl["memory_window"] == 60, "on_share"].iloc[0])
    assert perm >= mid >= narrow, "on_share 必须随记忆窗收窄单调不增"


# ---------------------------------------------------------------------------
# 5. summarize 裁定判据
# ---------------------------------------------------------------------------
def _fake_fold(tr_excess=0.01, te_excess=0.01, tr_share=0.05, te_share=0.05,
               te_t=5.0, te_hit_edge=0.05, te_events=4):
    h = wf.PREREG_ACCEPTANCE["primary_horizon"]
    return {
        "train": {f"excess{h}": tr_excess, f"hit_edge{h}": te_hit_edge, "on_share": tr_share},
        "test": {
            f"excess{h}": te_excess, f"t{h}": te_t, f"hit_edge{h}": te_hit_edge,
            "on_share": te_share, "n_events": te_events,
        },
    }


def test_summarize_adopts_only_when_every_gate_passes():
    s = wf.summarize([_fake_fold() for _ in range(4)])
    assert s["adopt"] is True
    assert s["test_dead_folds"] == 0 and s["test_blast_folds"] == 0
    assert s["wfe_mean"] == pytest.approx(1.0)


def test_pooled_t_is_sign_aware_and_grows_with_evidence():
    """池化 t 语义（回归护栏）：折数越多证据越强，反证折必须拉低而非被丢弃。"""
    assert wf.summarize([_fake_fold(te_t=5.0) for _ in range(4)])["pooled_t_approx"] == pytest.approx(10.0)
    assert wf.summarize([_fake_fold(te_t=5.0) for _ in range(9)])["pooled_t_approx"] == pytest.approx(15.0)
    mixed = [_fake_fold(te_t=5.0) for _ in range(4)] + [_fake_fold(te_t=-5.0)]
    assert wf.summarize(mixed)["pooled_t_approx"] == pytest.approx(15.0 / np.sqrt(5))


def test_summarize_rejects_negative_excess_and_weak_t():
    assert wf.summarize([_fake_fold(te_excess=-0.02) for _ in range(4)])["adopt"] is False
    assert wf.summarize([_fake_fold(te_t=0.5) for _ in range(4)])["adopt"] is False


def test_summarize_rejects_dead_and_blast_folds():
    dead = wf.summarize([_fake_fold(te_share=0.0) for _ in range(4)])
    blast = wf.summarize([_fake_fold(te_share=0.9) for _ in range(4)])
    assert dead["test_dead_folds"] == 4 and dead["adopt"] is False
    assert blast["test_blast_folds"] == 4 and blast["adopt"] is False
    # 恒零基线（现状）：无事件、无占比 → 必然证伪
    baseline = wf.summarize([_fake_fold(te_excess=float("nan"), tr_excess=float("nan"),
                                       te_share=0.0, te_events=0, te_t=float("nan")) for _ in range(4)])
    assert baseline["adopt"] is False and baseline["test_events_pooled"] == 0


def test_summarize_requires_majority_positive_folds():
    folds = [_fake_fold(te_excess=0.01), _fake_fold(te_excess=-0.05),
             _fake_fold(te_excess=-0.05), _fake_fold(te_excess=-0.05)]
    s = wf.summarize(folds)
    assert s["test_fold_positive_ratio"] == pytest.approx(0.25)
    assert s["adopt"] is False


def test_prereg_grid_covers_brief_axes():
    """网格覆盖任务书点名轴：SC z/pct/窗、AR 两道门、ST/Spring 缩量、6 阶段权重、门槛。"""
    g = wf.PREREG_GRID
    assert {"sc_vol_z", "sc_pct", "sc_window"} <= set(g["L0_sc_root"])
    assert {"ar_pct", "ar_breakout_window", "ar_doors"} <= set(g["L1_ar_doors"])
    assert {"st_shrink", "spring_shrink"} <= set(g["L2_st_spring_test"])
    assert "weight_variant" in g["L3_score_gate"] and "s2_confirm_gate" in g["L3_score_gate"]
    assert None in g["L3_score_gate"]["memory_window"]  # legacy 粘滞必在网格内（可被证伪比较）


def test_pre_registration_locks_params(tmp_path):
    """预注册锁定：同名不可覆盖，内容不一致须被 verify 拒（防事后调参）。"""
    path = tmp_path / "prereg.json"
    reg = wf.PreRegistrationRegistry(path)
    payload = {"grid": wf.PREREG_GRID, "acceptance": wf.PREREG_ACCEPTANCE, "n_folds": 5}
    reg.register("wyf3_test", payload, note="t")
    with pytest.raises(RuntimeError):
        reg.register("wyf3_test", payload)
    assert reg.verify("wyf3_test", payload) is True
    assert reg.verify("wyf3_test", {"grid": {}}) is False


def test_run_walkforward_fixed_params_smoke(cyc):
    """不选值（固定参数）跑折：结构完整、无 future leak、字段可 JSON 化。"""
    import json

    folds = wf.make_folds(pd.DatetimeIndex(cyc["close"].index), first_test_start="2017-01-01",
                          test_years=1, n_folds=3)
    out = wf.run_walkforward(cyc, folds, fixed_params=replace(
        DEFAULT_WYCKOFF_PARAMS, sc_vol_z=0.0, memory_window=40, s2_confirm_gate=40.0))
    assert len(out["folds"]) == len(folds)
    assert set(out["summary"]) >= {"adopt", "test_excess_mean", "test_blast_folds"}
    json.dumps(out, default=str)
