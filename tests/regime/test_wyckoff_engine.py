# [A_test] module_id: MOD-TEST-WYCKOFF-ENG | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-REGIME-002 | docs/03_modules/_domain_regime/regime_feature_builder/blueprint.md | §4.12 Phase2c
# [MODULE] tests.regime.test_wyckoff_engine
# [DOMAIN] D_REGIME
# [DEPENDENCIES] zephyr.regime.features.wyckoff_engine; pandas
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR-CONTRACT] AssertionError->fail
# [TESTS] tests/regime/test_wyckoff_engine.py
# [A_module] module_id: MOD-TEST-WYCKOFF-ENG | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #MOD-REGIME-002 #10_regime_detector_spec §4.12 #Phase2c #WYF-1 #WYF-2
"""test_wyckoff_engine.py — Wyckoff 吸筹 FSM 6 阶段引擎（MOD-REGIME-002 Phase 2c）单元测试。

覆盖（WYF-1/WYF-2 修复批，2026-09-15）：
  - 6 阶段各至少一个触发场景（合成 OHLCV：历史挖坑→放量下跌→暴跌巨量 SC→
    反弹 AR→缩量回踩 ST→跌破收回 Spring→放量突破 AR 高点 Test/SOS）
  - Bug1 回归（WYF-1）：low < close 的正常暴跌日 SC 可触发
    （旧实现用 low 的滚动最低判"收在区间最低"，low<=close 恒成立 → 数学不可达）
  - Bug2 回归（WYF-1）：单 AR 日后 ar_vol_avg 非 NaN，ST/Spring 缩量条件可成立；
    AR 发生前基准为 NaN（PIT 安全），同形态日不触发
    （旧实现对稀疏 AR 事件 rolling(10) 恒 NaN → ST/Spring 永不触发）
  - score 累加路径（10→40→55→75→cap 100）/ cap 100 / 无结构=0
  - PIT 粗检：截断序列到事件日，事件与评分与全量序列前缀严格一致

依据: 10_regime_detector_spec v1.3.1 §4.12.2 / S11 挖矿节点 wyckoff_vix_mining.md §1-2
"""

from __future__ import annotations

import pandas as pd
from typing import Final

from zephyr.regime.features.wyckoff_engine import detect_wyckoff_events, wyckoff_score

# ---------------------------------------------------------------------------
# 合成 OHLCV 场景构造
# ---------------------------------------------------------------------------

_BAR_COLUMNS: Final[list[str]] = ["open", "high", "low", "close", "volume", "vol_z"]

# 基准平静日：close=100 / high=101 / low=99 / 平量 / 无量异动
_FLAT = (100.0, 101.0, 99.0, 100.0, 1_000_000.0, 0.0)
# 历史挖坑日：给 PS 的"不再创新低"留出空间（60 日 low 最低=95）
_DIP = (99.0, 99.5, 95.0, 96.0, 1_000_000.0, 0.0)
# SC 抛售高潮日：巨量暴跌，low(90) < close(91) —— Bug1 回归前提（正常暴跌日）
_SC = (94.0, 95.0, 90.0, 91.0, 3_000_000.0, 3.5)
# AR 自动反弹日：放量收复，high 创 10 日新高
_AR = (92.0, 102.5, 91.5, 101.0, 2_500_000.0, 0.0)

# 完整吸筹链场景的事件日绝对索引（基准 80 日后）
_I_PS, _I_SC, _I_AR, _I_ST, _I_SPRING, _I_TEST = 80, 83, 84, 88, 92, 98


def _flat_bars(n: int) -> list[tuple[float, float, float, float, float, float]]:
    return [_FLAT] * n


def _absorption_bars() -> list[tuple[float, float, float, float, float, float]]:
    """完整吸筹链：PS→SC→AR→ST→Spring→Test 六阶段各恰一个触发日的合成序列。

    共 104 日：0-79 基准（40 为挖坑日 low=95），80 PS，81-82 整理，
    83 SC（sc_low=90），84 AR（ar_high=102.5，量能基准 2.5M），
    85-87 缩量前回踩，88 ST（low 落回 sc_low±2% 带内 + 缩量），
    89-91 整理（low 避开 ST 带），92 Spring（low=88 跌破 90 但 close 收回，缩量），
    93-97 反弹，98 Test（放量收盘突破 ar_high=102.5），99-103 高位整理。
    """
    bars = _flat_bars(80)
    bars[40] = _DIP
    bars += [
        # PS：下跌放量（z=1.5>1）但 low=98.2 高于 60 日 low 最低 95（不创新低）
        (99.0, 99.4, 98.2, 98.5, 1_200_000.0, 1.5),  # 80
        (98.5, 99.0, 98.0, 98.5, 1_000_000.0, 0.0),  # 81
        (98.5, 99.0, 98.0, 98.5, 1_000_000.0, 0.0),  # 82
        _SC,                                         # 83 SC, sc_low=90
        _AR,                                         # 84 AR, ar_high=102.5
        (97.0, 99.0, 95.0, 96.0, 1_000_000.0, 0.0),   # 85
        (95.5, 96.5, 93.5, 94.0, 1_000_000.0, 0.0),   # 86
        (93.5, 94.5, 92.2, 93.0, 1_000_000.0, 0.0),   # 87（low 避开 ST 带）
        # ST：low=90.5 ∈ [88.2, 91.8] + 缩量（0.9M < 2.5M×0.7）+ 近 10 日有 SC
        (92.0, 92.5, 90.5, 90.8, 900_000.0, 0.0),     # 88
        (91.2, 92.3, 91.9, 92.0, 1_000_000.0, 0.0),   # 89
        (92.0, 92.8, 91.95, 92.4, 1_000_000.0, 0.0),  # 90
        (92.4, 93.0, 92.0, 91.2, 1_000_000.0, 0.0),   # 91
        # Spring：low=88 跌破 sc_low=90 但 close=90.8 收回 + 缩量（0.8M < 2.5M×0.8）
        (91.0, 91.2, 88.0, 90.8, 800_000.0, 0.0),     # 92
        (91.0, 93.0, 90.9, 92.5, 1_000_000.0, 0.0),   # 93
        (92.5, 95.0, 92.0, 94.5, 1_000_000.0, 0.0),   # 94
        (94.5, 97.0, 94.0, 96.5, 1_000_000.0, 0.0),   # 95
        (96.5, 99.5, 96.0, 99.0, 1_000_000.0, 0.0),   # 96
        (99.0, 102.0, 98.5, 101.5, 1_000_000.0, 0.0),  # 97
        # Test/SOS：close=104 > ar_high=102.5 + 放量（2.2M > 近 20 日均量 ~1.23M）
        (102.2, 104.5, 101.8, 104.0, 2_200_000.0, 0.0),  # 98
        (104.0, 104.5, 103.5, 104.0, 1_000_000.0, 0.0),  # 99
        (104.0, 104.5, 103.5, 104.0, 1_000_000.0, 0.0),  # 100
        (104.0, 104.5, 103.5, 104.0, 1_000_000.0, 0.0),  # 101
        (104.0, 104.5, 103.5, 104.0, 1_000_000.0, 0.0),  # 102
        (104.0, 104.5, 103.5, 104.0, 1_000_000.0, 0.0),  # 103
    ]
    return bars


def _inputs_from_bars(bars: list[tuple[float, float, float, float, float, float]]):
    """bars → detect_wyckoff_events/wyckoff_score 六参数 dict（pct/vol_z 由序列派生）。"""
    df = pd.DataFrame(bars, columns=_BAR_COLUMNS)
    df.index = pd.date_range("2020-01-01", periods=len(bars), freq="D")
    return {
        "close": df["close"],
        "high": df["high"],
        "low": df["low"],
        "volume": df["volume"],
        "pct_change": df["close"].pct_change().fillna(0.0),
        "vol_z": df["vol_z"],
    }


def _run_engine(bars):
    inputs = _inputs_from_bars(bars)
    events = detect_wyckoff_events(**inputs)
    score = wyckoff_score(**inputs)
    return events, score, inputs


# ---------------------------------------------------------------------------
# 6 阶段触发场景
# ---------------------------------------------------------------------------


def test_full_absorption_chain_all_six_stages_fire():
    """完整吸筹链：PS/SC/AR/ST/Spring/Test 各在预定日恰触发一次。"""
    events, _, _ = _run_engine(_absorption_bars())
    assert events["ps"].iloc[_I_PS] == 1.0
    assert events["sc"].iloc[_I_SC] == 1.0
    assert events["ar"].iloc[_I_AR] == 1.0
    assert events["st"].iloc[_I_ST] == 1.0
    assert events["spring"].iloc[_I_SPRING] == 1.0
    assert events["test"].iloc[_I_TEST] == 1.0


def test_ps_fires_on_down_day_above_prior_low():
    """PS 初步支撑：下跌放量但不创 60 日新低。"""
    bars = _flat_bars(70)
    bars[30] = _DIP  # 历史挖坑：60 日 low 最低=95
    bars.append((99.0, 99.4, 98.2, 98.5, 1_200_000.0, 1.5))  # 下跌放量不创新低
    inputs = _inputs_from_bars(bars)
    events = detect_wyckoff_events(**inputs)
    assert inputs["pct_change"].iloc[-1] < 0  # 场景前提：下跌日
    row = events.iloc[-1]
    assert row["ps"] == 1.0
    assert row.drop("ps").eq(0.0).all()  # 该日只有 PS，不串其他阶段


def test_sc_fires_on_normal_crash_day_low_below_close():
    """Bug1（WYF-1）回归：low < close 的正常暴跌日 SC 必须可触发。

    旧实现 `c <= l.rolling(60).min()`：low<=close 恒成立 → min(low)<=当日low<
    当日close，仅光脚收盘畸形日可触发（数学不可达）。修复后按 close 对 close
    的滚动最低（含当日）判定"收盘创 window 日新低"。
    """
    bars = _flat_bars(70)
    bars.append(_SC)  # low=90 < close=91
    inputs = _inputs_from_bars(bars)
    events = detect_wyckoff_events(**inputs)
    assert inputs["low"].iloc[-1] < inputs["close"].iloc[-1]  # 场景前提：非光脚收盘
    assert events["sc"].iloc[-1] == 1.0
    assert events["ps"].iloc[-1] == 0.0  # 创新低暴跌日不是 PS（not_new_low 排除）


def test_ar_fires_on_rebound_after_sc():
    """AR 自动反弹：SC 后 10 日内放量收复创 10 日新高。"""
    bars = _flat_bars(70)
    bars.append(_SC)
    bars.append(_AR)
    events, _, _ = _run_engine(bars)
    assert events["ar"].iloc[-1] == 1.0
    assert events["ar"].iloc[-2] == 0.0  # SC 当日不可能是 AR（pct 方向互斥）


def test_st_and_spring_fire_only_after_ar_baseline_exists():
    """Bug2（WYF-1）回归：单 AR 日后 ar_vol_avg 非 NaN，ST/Spring 缩量条件可成立。

    旧实现 `v.where(ar>0).rolling(10).mean()`：AR 事件日稀疏 → 窗口非 NaN 凑不满
    min_periods=10 → 恒 NaN → ST/Spring 缩量条件恒 False（永不触发）。修复后
    ffill 传播最近 AR 日量能基准再滚动。本场景同时验证 PIT 安全：首个 AR 发生
    之前基准为 NaN，同形态日（回踩带内缩量/跌破收回缩量）不触发。
    """
    bars = _flat_bars(70)
    bars.append(_SC)                                            # 70 SC, sc_low=90
    bars.append((91.5, 92.0, 90.5, 91.0, 900_000.0, 0.0))       # 71 ST 形态但 AR 未发生
    bars.append((91.0, 91.2, 88.0, 90.8, 800_000.0, 0.0))       # 72 Spring 形态但 AR 未发生
    bars.append(_AR)                                            # 73 AR（单个 AR 日）
    bars.append((91.5, 92.0, 90.5, 91.0, 900_000.0, 0.0))       # 74 ST：缩量回踩 sc_low 带
    bars.append((91.0, 91.2, 88.0, 90.8, 800_000.0, 0.0))       # 75 Spring：跌破收回+缩量
    events, _, _ = _run_engine(bars)
    assert events["st"].iloc[71] == 0.0      # AR 基准 NaN → 缩量条件不成立
    assert events["spring"].iloc[72] == 0.0  # 同上
    assert events["ar"].iloc[73] == 1.0
    assert events["st"].iloc[74] == 1.0      # 单 AR 日后基准=2.5M → 0.9M<1.75M 成立
    assert events["spring"].iloc[75] == 1.0  # 0.8M<2.0M 成立


def test_test_sos_fires_on_volume_breakout_after_spring():
    """Test/SOS：Spring 后 20 日内放量收盘突破 AR 高点。

    突破日须距 SC >10 日（sc_recent 出窗）：否则突破日自身先触发 AR，
    ar_high 吸收当日 high → c > ar_high 不成立，Test 被同日 AR 抑制。
    """
    bars = _flat_bars(70)
    bars.append(_SC)                                            # 70 SC
    bars.append(_AR)                                            # 71 AR, ar_high=102.5
    bars.append((91.0, 91.2, 88.0, 90.8, 800_000.0, 0.0))       # 72 Spring
    # 73-80 整理爬升：low>=92 避开 ST 带（sc_recent 仍真 + 缩量会误触 ST），
    # pct<1% 且 high<102.5 不触 AR
    bars += [
        (92.0, 92.6, 92.0, 92.3, 1_000_000.0, 0.0),   # 73
        (92.3, 92.9, 92.1, 92.6, 1_000_000.0, 0.0),   # 74
        (92.6, 93.2, 92.4, 92.9, 1_000_000.0, 0.0),   # 75
        (92.9, 93.5, 92.7, 93.2, 1_000_000.0, 0.0),   # 76
        (93.2, 93.8, 93.0, 93.5, 1_000_000.0, 0.0),   # 77
        (93.5, 94.1, 93.3, 93.8, 1_000_000.0, 0.0),   # 78
        (93.8, 94.4, 93.6, 94.1, 1_000_000.0, 0.0),   # 79
        (94.1, 94.7, 93.9, 94.4, 1_000_000.0, 0.0),   # 80（sc_recent 出窗）
    ]
    bars.append((101.0, 104.0, 100.5, 103.5, 2_200_000.0, 0.0))  # 81 放量突破 ar_high
    events, _, _ = _run_engine(bars)
    assert events["test"].iloc[81] == 1.0
    assert events["test"].iloc[72] == 0.0  # Spring 当日 close 未破 ar_high
    assert events["ar"].iloc[81] == 0.0    # sc_recent 已出窗，突破日不再触发 AR


# ---------------------------------------------------------------------------
# 评分语义
# ---------------------------------------------------------------------------


def test_score_accumulates_by_cummax_and_caps_at_100():
    """score 累加路径 10→40→55→75→cap 100（Spring 日 raw=115 被 cap）。"""
    _, score, _ = _run_engine(_absorption_bars())
    assert score.iloc[_I_PS - 1] == 0.0            # PS 之前无结构
    assert score.iloc[_I_PS] == 10.0               # +PS
    assert score.iloc[_I_SC] == 40.0               # +SC（cummax 粘滞 PS）
    assert score.iloc[_I_AR] == 55.0               # +AR
    assert score.iloc[_I_ST] == 75.0               # +ST
    assert score.iloc[_I_SPRING] == 100.0          # +Spring=115 → cap 100
    assert score.iloc[_I_TEST] == 100.0            # +Test 仍被 cap
    assert score.iloc[-1] == 100.0
    assert (score >= 0.0).all() and (score <= 100.0).all()


def test_no_structure_gives_zero_events_and_zero_score():
    """无结构 = 0：平静序列（pct=0、z=0）6 阶段全不触发，score 恒 0（C1 不退化前提）。"""
    bars = _flat_bars(90)
    events, score, _ = _run_engine(bars)
    assert (events == 0.0).all().all()
    assert (score == 0.0).all()


# ---------------------------------------------------------------------------
# PIT 粗检
# ---------------------------------------------------------------------------


def test_pit_prefix_consistency_at_event_days():
    """截断序列到各事件日（含一个非事件日），事件/评分与全量序列前缀严格一致。

    全部滚动窗口向后（含当日）、ffill 只向右传播已发生事件 → 行 t 只依赖 ≤t
    的输入，前缀可重现性是 PIT 无未来泄漏的粗粒度充分检查。
    """
    full_events, full_score, inputs = _run_engine(_absorption_bars())
    cuts = (_I_PS, _I_SC, _I_AR, _I_ST, _I_SPRING, _I_TEST, _I_ST + 2)
    for cut in cuts:
        cut_inputs = {k: v.iloc[: cut + 1] for k, v in inputs.items()}
        trunc_events = detect_wyckoff_events(**cut_inputs)
        trunc_score = wyckoff_score(**cut_inputs)
        pd.testing.assert_frame_equal(trunc_events, full_events.iloc[: cut + 1])
        pd.testing.assert_series_equal(trunc_score, full_score.iloc[: cut + 1])


# ---------------------------------------------------------------------------
# WYF-3 锁值与阈值精确边界（裁定#264：阈值维持现值，防静默漂移）
# ---------------------------------------------------------------------------


def test_threshold_constants_locked_to_ruling_264():
    """WYF-3 终态（裁定#264）：预注册协议网格内无合格替代值，阈值锁死为现值。

    锁值依据=docs/_working/wyf3/wyf3_recalibration_report.md §3 新旧对照表
    （终态全部"不动"）。任何值变化必须先登记新裁定并更新本断言。
    """
    from zephyr.regime.features import wyckoff_engine as we

    assert we._PS_VOL_Z == 1.0
    assert we._SC_VOL_Z == 2.0
    assert we._SC_PCT == -0.04
    assert we._AR_SC_RECENT_WIN == 10
    assert we._AR_PCT == 0.01
    assert we._AR_BREAKOUT_WIN == 10
    assert we._ST_BAND == 0.02
    assert we._ST_SHRINK == 0.7
    assert we._SPRING_SHRINK == 0.8
    assert we._TEST_SPRING_RECENT_WIN == 20
    assert we._TEST_VOL_RATIO == 1.0
    # 权重表同锁（S2 confirm 门槛 60 的累加语义真源）
    assert we._STAGE_WEIGHTS == {
        "ps": 10.0, "sc": 30.0, "ar": 15.0, "st": 20.0, "spring": 40.0, "test": 20.0,
    }


def _sc_boundary_inputs(close: float, vol_z: float, explicit_pct: float | None = None):
    """构造 SC 边界场景：70 日 flat(close=100) 后接单日暴跌候选（close 创 60 日收盘新低）。

    explicit_pct 显式钉死 pct（消除 96.0/100-1 的浮点累差）——边界测试要求输入
    精确等于阈值常量的双精度表示。
    """
    bars = _flat_bars(70)
    bars.append((close * 1.01, close * 1.02, close - 1.0, close, 3_000_000.0, vol_z))
    inputs = _inputs_from_bars(bars)
    if explicit_pct is not None:
        inputs["pct_change"].iloc[-1] = explicit_pct
    return inputs


def test_sc_threshold_exact_equality_does_not_fire():
    """SC 阈值严格不等式边界（WYF-3 锁值回归）。

    判定条件为 z > 2.0 且 pct < -0.04（严格）：恰在等值点（z=2.0 整 / pct=-0.04
    双精度字面量）均不得触发；仅双侧同时越界才触发。防未来把严格不等式改成
    >=（静默放宽）。
    """
    # 恰等值：pct=-0.04 字面量 + vol_z=2.0 整 → 不触发
    inputs = _sc_boundary_inputs(close=96.0, vol_z=2.0, explicit_pct=-0.04)
    assert inputs["pct_change"].iloc[-1] == -0.04
    assert inputs["vol_z"].iloc[-1] == 2.0
    events = detect_wyckoff_events(**inputs)
    assert events["sc"].iloc[-1] == 0.0
    # 单侧越界（z 过线 pct 恰等值）→ 不触发
    events = detect_wyckoff_events(**_sc_boundary_inputs(close=96.0, vol_z=2.5, explicit_pct=-0.04))
    assert events["sc"].iloc[-1] == 0.0
    # 单侧越界（pct 过线 z 恰等值）→ 不触发
    events = detect_wyckoff_events(**_sc_boundary_inputs(close=95.9, vol_z=2.0, explicit_pct=-0.0401))
    assert inputs["pct_change"].iloc[-1] != 0.0
    assert events["sc"].iloc[-1] == 0.0
    # 双侧越界 + 收盘创 60 日新低 + 非光脚收盘 → 触发（Bug1 语义保持）
    events = detect_wyckoff_events(**_sc_boundary_inputs(close=95.9, vol_z=2.5, explicit_pct=-0.0401))
    assert events["sc"].iloc[-1] == 1.0


def test_ar_pct_exact_equality_does_not_fire():
    """AR 阈值严格不等式边界：SC 后反弹日 pct 恰 +1% 不触发，+1.1% 触发。"""
    bars = _flat_bars(70)
    bars.append(_SC)  # 70 SC
    # AR 候选日：high 创 10 日新高，pct 显式钉死
    ar_bar = (91.5, 102.5, 91.5, 100.0, 2_500_000.0, 0.0)
    bars.append(ar_bar)  # 71
    inputs = _inputs_from_bars(bars)
    pct = inputs["pct_change"]
    pct.iloc[-1] = 0.01  # 恰 +1%（严格 > 下不触发）
    events = detect_wyckoff_events(**inputs)
    assert events["ar"].iloc[-1] == 0.0
    pct.iloc[-1] = 0.0101  # 越界触发
    events = detect_wyckoff_events(**inputs)
    assert events["ar"].iloc[-1] == 1.0


def test_st_band_boundary_inside_outside():
    """ST 回踩带宽边界（±2%）：low 恰落在带沿内触发、恰带外不触发。

    sc_low=90（SC 日 low）：带=[88.2, 91.8]。low=91.8（恰 1.02×sc_low）在带内，
    low=91.9 出带 → ST 不触发（缺带内腿，缩量/近期SC 另配齐）。
    """
    bars = _flat_bars(70)
    bars.append(_SC)                                            # 70 SC, sc_low=90
    bars.append(_AR)                                            # 71 AR（供 ar_vol_avg 基准）
    bars.append((91.0, 92.0, 91.8, 91.0, 900_000.0, 0.0))       # 72 low 恰带沿 91.8=90×1.02
    bars.append((91.0, 92.0, 91.9, 91.2, 900_000.0, 0.0))       # 73 low 出带
    inputs = _inputs_from_bars(bars)
    events = detect_wyckoff_events(**inputs)
    assert events["st"].iloc[72] == 1.0  # 恰带沿（<= 上带）在带内
    assert events["st"].iloc[73] == 0.0  # 出带不触发
