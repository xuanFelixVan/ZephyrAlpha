# [BLUEPRINT] MOD-REGIME-002 | docs/03_modules/_domain_regime/regime_feature_builder/blueprint.md | §4.12 Phase2c
# [MODULE] zephyr.regime.features.wyckoff_engine
# [DOMAIN] D_REGIME
# [DEPENDENCIES] numpy; pandas
# [CONSUMERS] MOD-REGIME-002(OverlaySignalsConstructor消费s2_wyckoff_score→S2 confirm)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] score∈[0,100]; 无结构=0(平时不干预); PIT严格(只用历史事件,ffill传播已发生阶段); PIT由调用方shift(1)
# [MODIFY-GUARD] blueprint=docs/03_modules/_domain_regime/regime_feature_builder/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] —
# [TESTS] tests/regime/test_wyckoff_engine.py
# [A_module] module_id=MOD-REGIME-002 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #10_regime_detector_spec §4.12 #MOD-REGIME-002 #Phase2c
"""Wyckoff 吸筹 FSM 6 阶段识别 + 评分（MOD-REGIME-002 Phase 2c）。

把 OHLCV + 量能 z-score 映射成 Wyckoff 吸筹理论的 6 阶段事件 + 累加评分（0-100），
供 OverlaySignalsConstructor 组装 s2_wyckoff_score 维度喂 RegimeDetector S2 confirm。

Wyckoff 吸筹理论（10_regime_detector_spec §4.12.2）：
    PS(初步支撑) → SC(抛售高潮) → AR(自动反弹) → ST(二次测试)
    → Spring(震仓) → Test/SOS(强势信号)

每个阶段一旦出现，向后填充"已发生"（cummax 传播），加权累加：
    PS=10 / SC=30 / AR=15 / ST=20 / Spring=40 / Test=20（总分135，cap 100）

设计原则：
  - **PIT 铁律**：事件标记用 rolling+shift（严格历史）；sc_low/ar_high 用
    where(events).ffill() 传播（只用已发生事件的价位，不引入未来信息）。
    调用方 _precompute 末尾统一 shift(1) 再做最终 PIT 隔离。
  - **无结构 = 0**：无任何阶段出现 → score=0 → S2 confirm 不触发（C1 不退化前提）。
  - **Spring 是关键转折**：Spring 出现（+40）→ 累计至少 60+（过 S2 confirm 门槛 60）。

依据: 10_regime_detector_spec v1.3.1 §4.12.2 / Phase 2c 计划 §任务3
Version: 0.1.0
"""

from __future__ import annotations

import numpy as np
import pandas as pd

__all__ = ["detect_wyckoff_events", "wyckoff_score"]


# Wyckoff 6 阶段权重（10_regime_detector_spec §4.12.2）
_STAGE_WEIGHTS: dict[str, float] = {
    "ps": 10.0,
    "sc": 30.0,
    "ar": 15.0,
    "st": 20.0,
    "spring": 40.0,
    "test": 20.0,
}


def detect_wyckoff_events(
    close: pd.Series,
    high: pd.Series,
    low: pd.Series,
    volume: pd.Series,
    pct_change: pd.Series,
    vol_z: pd.Series,
    window: int = 60,
) -> pd.DataFrame:
    """识别 Wyckoff 6 阶段事件点，返回 DataFrame[ps,sc,ar,st,spring,test]（0/1 flag）。

    所有事件标记用 rolling + shift（严格历史），PIT 由调用方 shift(1) 二次保证。

    Parameters
    ----------
    close, high, low : OHLC 序列（市场代理）。
    volume : 成交量序列。
    pct_change : 日涨跌幅序列（close.pct_change()）。
    vol_z : 量能异动 z-score（volume_anomaly，复用 HMM F5）。
    window : rolling 回看窗口（默认 60 日）。

    Returns
    -------
    pd.DataFrame，index 同 close，列 [ps, sc, ar, st, spring, test]，值 0.0/1.0。
    """
    events = pd.DataFrame(index=close.index)
    c = close.ffill()
    h = high.ffill()
    l = low.ffill()
    v = volume.fillna(0.0)
    pct = pct_change.fillna(0.0)
    z = vol_z.fillna(0.0)

    rolling_min = l.rolling(window).min()
    rolling_max = h.rolling(window).max()

    # ── PS 初步支撑：下跌中放量但不再创新低 ──
    # vol_z>1（放量）& low>rolling_min.shift(1)（不再创新低）& pct<0（下跌趋势中）
    not_new_low = l > rolling_min.shift(1)
    events["ps"] = ((z > 1.0) & not_new_low & (pct < 0)).astype(float)

    # ── SC 抛售高潮：巨量暴跌收最低 ──
    # vol_z>2 & pct<-4% & close<=rolling_min（收在区间最低）
    sc_condition = (z > 2.0) & (pct < -0.04) & (c <= rolling_min + 1e-8)
    events["sc"] = sc_condition.astype(float)

    # ── AR 自动反弹：SC 后 10 日内创新高 ──
    # 近10日有SC & 当日high创近10日新高 & pct>1%（反弹）
    sc_recent = events["sc"].rolling(10).max() > 0
    high_breakout = h >= h.rolling(10).max()
    events["ar"] = (sc_recent & high_breakout & (pct > 0.01)).astype(float)

    # SC 低点 forward fill（只用已发生的 SC 事件的 low，PIT 安全）
    sc_low = l.where(events["sc"] > 0).ffill()
    # AR 后的均量（AR 事件日的 volume 滚动均值，缩量判定基准）
    ar_vol_avg = v.where(events["ar"] > 0).rolling(10).mean()
    # AR 高点 forward fill（只用已发生的 AR 事件的 high）
    ar_high = h.where(events["ar"] > 0).ffill()

    # ── ST 二次测试：回落至 SC 区域 + 缩量 ──
    # low 接近 sc_low（±2%）& volume < AR均量×0.7（缩量）& 近期有 SC
    in_sc_zone = (l <= sc_low * 1.02) & (l >= sc_low * 0.98)
    shrink_vol = v < (ar_vol_avg * 0.7)
    events["st"] = (in_sc_zone & shrink_vol & sc_recent).astype(float)

    # ── Spring 震仓：跌破 sc_low 但收回 + 缩量 ──
    # low<sc_low（跌破）& close>sc_low（收回）& volume<AR均量×0.8（缩量）
    broke_sc = l < sc_low
    recovered = c > sc_low
    spring_shrink = v < (ar_vol_avg * 0.8)
    events["spring"] = (broke_sc & recovered & spring_shrink).astype(float)

    # ── Test/SOS 强势信号：Spring 后上突 AR 高点 + 放量 ──
    # 近20日有Spring & close>ar_high（突破AR高点）& 放量（>20日均量）
    spring_recent = events["spring"].rolling(20).max() > 0
    vol_expanding = v > v.rolling(20).mean()
    events["test"] = (spring_recent & (c > ar_high) & vol_expanding).astype(float)

    return events.fillna(0.0)


def wyckoff_score(
    close: pd.Series,
    high: pd.Series,
    low: pd.Series,
    volume: pd.Series,
    pct_change: pd.Series,
    vol_z: pd.Series,
    window: int = 60,
) -> pd.Series:
    """Wyckoff 吸筹评分 → 0-100（累加已出现阶段分数，cap 100）。

    每个阶段一旦出现，后续日期都算"已发生"（cummax 传播），加权累加。
    映射（对齐 S2 confirm 门槛 wyckoff>=60）：
      Spring 出现（PS+SC+AR+ST+Spring ≥ 60）→ 至少 60+（过 confirm 门槛）
      SC+AR+ST 完整（无 Spring，+65）→ 65（过门槛）
      仅 PS+SC（+40）→ 40（未达门槛）
      仅 PS（+10）→ 10
      无任何阶段 → 0

    Parameters
    ----------
    同 detect_wyckoff_events。

    Returns
    -------
    pd.Series，值 ∈ [0, 100]。
    """
    events = detect_wyckoff_events(close, high, low, volume, pct_change, vol_z, window)
    # 每阶段一旦出现，后续日期都算"已发生"（cummax 传播，PIT 安全：只用历史事件）
    occurred = events.cummax()
    score = pd.Series(0.0, index=close.index)
    for stage, weight in _STAGE_WEIGHTS.items():
        score += occurred[stage] * weight
    # cap 到 100（实际最高 135，但 score 维度 ∈ [0,100] INVARIANTS）
    return score.clip(upper=100.0).fillna(0.0)
