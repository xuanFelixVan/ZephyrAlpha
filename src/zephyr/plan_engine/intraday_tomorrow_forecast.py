# [BLUEPRINT] MOD-PLAN-025 | docs/03_modules/_domain_plan_engine/intraday_tomorrow_forecast/blueprint.md
# [MODULE] zephyr.plan_engine.intraday_tomorrow_forecast
# [DOMAIN] D_PLAN
# [DEPENDENCIES] zephyr.signal_ashare.next_day_8state_forecast（NextDayState 枚举；先验分布由调用方经 forecast_next_day 产出后注入）
# [CONSUMERS] TDM-E-L0-04（明日情绪盘中滚动预测）；L0-02 偏离监控（downgrade_warning 消费，待接线）；L3-06 环境开关（情绪档输入，待接线）
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 纯函数核零 IO（三零件产出由调用方注入，对齐 thesis_survival 模式）; 相似日非 KNN 真路径（enabled=False 或 fallback_used=True）不参与合成（fallback 转移先验与 8 态先验同源，参与=先验双计）; Brier 缺数据=权重中性 1.0（连错降权需证据，无罪推定）; 融合分布恒归一且非负; 悲观档位表固定序（GAP_UP_UP 最乐观→GAP_DOWN_DOWN 最悲观，蓝图 §2）; 预警判据=融合最可能态悲观档−先验最可能态悲观档 ≥ 1（argmax 平票偏悲观；期望档差仅作诊断——凸组合下期望档最大移动 w×tilt≈0.6 档，判据不可达）; 同输入必同输出（frozen+纯函数）
# [MODIFY-GUARD] 地图节点 TDM-E-L0-04
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 输入非法（先验缺态/负值/不归一/三档不归一/NaN）→ TomorrowForecastInputError（fail-closed）
# [TESTS] tests/plan_engine/test_intraday_tomorrow_forecast.py
# [TTL] permanent
"""IntradayTomorrowForecast — 明日情绪盘中滚动预测组合器（MOD-PLAN-025，TDM-E-L0-04，C13）。

盘中 10:00/11:00/13:30/14:30 四时点滚动合成"明天情绪概率"（施工清单 C13，
晨审 st-tdm-review-20260911 D6 批准升施工批）：

    昨晚 8 态转移先验（next_day_8state_forecast, MOD-SIG-037，调用方注入）
      + 相似日推理修正（similar_day_inference, MOD-SIG-063，三档情景→悲观档倾斜）
      + Brier 校准连错降权（brier_calibration, MOD-PLAN-010，差输入低权重）
      → 融合 8 态分布 → 比盘前先验悲观一档以上 = 明日降档预警（喂 L0-02）

本件只做合成数学，零 IO——先验/三档/校准报告一律由调用方注入；
tomorrow_boundary_planner 不变量"不读盘中实时数据"，故盘中断链由本件补位。
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Final, Mapping

from zephyr.signal_ashare.next_day_8state_forecast import NextDayState

_N_STATES: Final = len(NextDayState)

#: 盘中滚动四时点（地图节点口径）
INTRADAY_POINTS: Final = ("10:00", "11:00", "13:30", "14:30")

#: 悲观档位序（下标=档位，越大越悲观；设计先验见蓝图 §2，proposed 待实盘标定）
PESSIMISM_ORDER: Final[tuple[NextDayState, ...]] = (
    NextDayState.GAP_UP_UP,  # 0 高开高走（最乐观）
    NextDayState.GAP_DOWN_UP,  # 1 低开高走（V 型修复）
    NextDayState.FLAT_UP,  # 2 平开高走
    NextDayState.FLAT_CLOSE,  # 3 震荡收平（中性）
    NextDayState.VIOLENT,  # 4 剧烈震荡（情绪不稳）
    NextDayState.FLAT_DOWN,  # 5 平开低走（阴跌）
    NextDayState.GAP_UP_DOWN,  # 6 高开低走（诱多套人，比阴跌更伤情绪）
    NextDayState.GAP_DOWN_DOWN,  # 7 低开低走（最悲观）
)
_TIER_OF: Final[dict[NextDayState, int]] = {s: i for i, s in enumerate(PESSIMISM_ORDER)}
_STATE_AT: Final[dict[int, NextDayState]] = {i: s for i, s in enumerate(PESSIMISM_ORDER)}

#: 融合基础权重（proposed）
BASE_W_PRIOR: Final = 0.7
BASE_W_SIMILAR: Final = 0.3
#: 二值 Brier 瞎猜参考（uniform 瞎猜的期望 Brier=0.5）
BRIER_RANDOM_REF: Final = 0.5
#: 可靠度下限（Brier 差于瞎猜也不清零，保分布良定义）
RELIABILITY_FLOOR: Final = 0.1
#: 相似日极端情景（全弱/全强）最大倾斜档数
TILT_MAX_TIERS: Final = 2.0
#: 明日降档预警阈值：融合最可能态悲观档 − 先验最可能态悲观档 ≥ 此值（整数档；
#: 期望档差作为诊断字段随输出透出，凸组合下期望档最大移动 w×tilt≈0.6 档，不适合作判据）
DOWNGRADE_TIER_THRESHOLD: Final = 1
#: 概率归一容差
_SUM_TOL: Final = 1e-6


class TomorrowForecastInputError(ValueError):
    """输入非法（先验缺态/负值/不归一、三档不归一、NaN）——fail-closed。"""


@dataclass(frozen=True)
class SourceCalibration:
    """单输入源校准摘要（brier_calibration.compute_calibration 产出后注入）。

    brier=None=无校准数据（预测日志空窗/模块未回填）→ 可靠度中性 1.0。
    """

    module: str
    brier: float | None = None


@dataclass(frozen=True)
class SimilarDayScenario:
    """相似日三档情景摘要（similar_day_inference.SimilarDayInference 的冻结镜像）。

    与真源字段一一对应（enabled/fallback_used/prob_strong/prob_flat/prob_weak），
    冻结镜像避免引入对可变输出对象的持有；调用方可用 ``from_inference`` 转换。
    """

    enabled: bool
    fallback_used: bool
    prob_strong: float
    prob_flat: float
    prob_weak: float

    @classmethod
    def from_inference(cls, obj) -> SimilarDayScenario:
        """从 similar_day_inference.SimilarDayInference 实例鸭型转换（零 import 依赖）。"""
        return cls(
            enabled=bool(obj.enabled),
            fallback_used=bool(obj.fallback_used),
            prob_strong=float(obj.prob_strong),
            prob_flat=float(obj.prob_flat),
            prob_weak=float(obj.prob_weak),
        )


@dataclass(frozen=True)
class TomorrowForecast:
    """明日情绪滚动合成输出（JSON 可序列化经 to_dict）。"""

    distribution: dict[str, float]  # 8 态融合概率（key=NextDayState.value）
    expected_tier_prior: float  # 先验期望悲观档（诊断）
    expected_tier_fused: float  # 融合期望悲观档（诊断）
    dominant_state: str  # 融合分布 argmax 态（平票取档位更悲观者，不编方向）
    dominant_tier_prior: int  # 先验最可能态悲观档（预警基准）
    dominant_tier_fused: int  # 融合最可能态悲观档
    downgrade_warning: bool  # 明日降档预警：dominant_tier_fused − dominant_tier_prior ≥ 1（喂 L0-02）
    weights: dict[str, float]  # 归一后有效权重 {prior, similar}
    notes: list[str] = field(default_factory=list)
    intraday_point: str | None = None  # 触发时点（10:00/11:00/13:30/14:30）

    def to_dict(self) -> dict:
        """全基本类型字典（json.dumps 直序列化）。"""
        return {
            "distribution": dict(self.distribution),
            "expected_tier_prior": self.expected_tier_prior,
            "expected_tier_fused": self.expected_tier_fused,
            "dominant_state": self.dominant_state,
            "dominant_tier_prior": self.dominant_tier_prior,
            "dominant_tier_fused": self.dominant_tier_fused,
            "downgrade_warning": self.downgrade_warning,
            "weights": dict(self.weights),
            "notes": list(self.notes),
            "intraday_point": self.intraday_point,
        }


def _validate_distribution(prior: Mapping[NextDayState, float], what: str) -> dict[NextDayState, float]:
    """8 态分布契约校验：全态齐/非负/有限/归一（容差内原样，超容差 fail-closed）。"""
    missing = [s for s in NextDayState if s not in prior]
    if missing:
        raise TomorrowForecastInputError(f"{what} 缺态: {[s.value for s in missing]}")
    values: dict[NextDayState, float] = {}
    for s in NextDayState:
        v = float(prior[s])
        if not math.isfinite(v):
            raise TomorrowForecastInputError(f"{what} 态 {s.value} 概率非有限: {v}")
        if v < 0.0:
            raise TomorrowForecastInputError(f"{what} 态 {s.value} 概率为负: {v}")
        values[s] = v
    total = sum(values.values())
    if abs(total - 1.0) > 1e-3:
        raise TomorrowForecastInputError(f"{what} 概率不归一: sum={total!r}")
    return values


def expected_pessimism_tier(dist: Mapping[NextDayState, float]) -> float:
    """期望悲观档 = Σ p_i × tier_i（档位序见 PESSIMISM_ORDER）。"""
    return sum(float(p) * _TIER_OF[s] for s, p in dist.items())


def reliability_from_brier(brier: float | None) -> float:
    """Brier → 可靠度权重系数：clamp(1 − brier/0.5, 0.1, 1)；None=1.0 中性。"""
    if brier is None:
        return 1.0
    if not math.isfinite(float(brier)) or brier < 0.0:
        raise TomorrowForecastInputError(f"校准 Brier 非法: {brier!r}")
    return max(RELIABILITY_FLOOR, min(1.0, 1.0 - float(brier) / BRIER_RANDOM_REF))


def scenario_tilt(scenario: SimilarDayScenario | None) -> float | None:
    """三档情景 → 悲观档倾斜量（档）。

    tilt = (P弱 − P强) × TILT_MAX_TIERS，正值=调悲观。
    返回 None = 本输入不参与合成（未启用 / fallback 兜底分支——先验双计防线）。
    """
    if scenario is None:
        return None
    if not scenario.enabled:
        return None
    if scenario.fallback_used:
        return None
    trio = (scenario.prob_strong, scenario.prob_flat, scenario.prob_weak)
    if any(not math.isfinite(v) or v < 0.0 for v in trio):
        raise TomorrowForecastInputError(f"三档情景概率非法: {trio}")
    total = sum(trio)
    if abs(total - 1.0) > 1e-3:
        raise TomorrowForecastInputError(f"三档情景概率不归一: sum={total!r}")
    return (scenario.prob_weak - scenario.prob_strong) * TILT_MAX_TIERS


def tilt_prior_along_pessimism(
    prior: Mapping[NextDayState, float], tilt: float
) -> dict[NextDayState, float]:
    """沿悲观档轴平移概率质量：档位 x 的质量线性落至 x+tilt 的 floor/ceil 两端，边界截停。

    档位↔状态一一对应（8 态全序），故平移后仍是合法 8 态分布。
    tilt=0 → 原分布；tilt>0 → 调悲观；tilt<0 → 调乐观。
    """
    if not math.isfinite(tilt):
        raise TomorrowForecastInputError(f"倾斜量非有限: {tilt!r}")
    tier_mass = [0.0] * _N_STATES
    for s in NextDayState:
        tier_mass[_TIER_OF[s]] += float(prior[s])
    shifted = [0.0] * _N_STATES
    for i, mass in enumerate(tier_mass):
        if mass == 0.0:
            continue
        x = i + tilt
        if x <= 0.0:  # 越乐观端截停：质量全部留在最乐观档
            shifted[0] += mass
            continue
        if x >= _N_STATES - 1:  # 越悲观端截停
            shifted[_N_STATES - 1] += mass
            continue
        lo = math.floor(x)
        frac = x - lo
        shifted[lo] += mass * (1.0 - frac)
        shifted[lo + 1] += mass * frac
    out: dict[NextDayState, float] = {}
    for i in range(_N_STATES):
        out[_STATE_AT[i]] = max(0.0, shifted[i])
    total = sum(out.values())
    if total <= 0.0:
        raise TomorrowForecastInputError("倾斜后分布全零（先验为空？）")
    return {s: p / total for s, p in out.items()}


def fuse(
    prior: Mapping[NextDayState, float],
    scenario: SimilarDayScenario | None,
    calibration_prior: SourceCalibration | None = None,
    calibration_similar: SourceCalibration | None = None,
    intraday_point: str | None = None,
) -> TomorrowForecast:
    """组合主入口：先验打底 + 相似日倾斜 + Brier 降权 → 融合分布与降档预警。

    Args:
        prior: 昨晚 8 态先验（forecast_next_day 产出，调用方注入）。
        scenario: 相似日三档（infer_remaining_session 产出摘要；None=本时点无输入）。
        calibration_prior: 8 态源历史 Brier 摘要（None=无数据，权重中性）。
        calibration_similar: 相似日源历史 Brier 摘要（None=无数据，权重中性）。
        intraday_point: 触发时点标签（应取 INTRADAY_POINTS 之一，仅透传不校验业务含义）。

    Returns:
        TomorrowForecast（frozen，含 notes 诊断）。

    Raises:
        TomorrowForecastInputError: 任一输入违反契约（fail-closed）。
    """
    prior_v = _validate_distribution(prior, "先验分布")
    e_prior = expected_pessimism_tier(prior_v)

    notes: list[str] = []
    w_prior = BASE_W_PRIOR * reliability_from_brier(
        calibration_prior.brier if calibration_prior is not None else None
    )
    tilt = scenario_tilt(scenario)
    if tilt is None:
        w_similar = 0.0
        if scenario is not None and not scenario.enabled:
            notes.append("相似日停用（walk-forward 命中率未达纪律线）→ 不参与合成")
        elif scenario is not None and scenario.fallback_used:
            notes.append("相似日退化兜底分支（转移先验同源）→ 不参与合成，防先验双计")
        else:
            notes.append("本时点无相似日输入 → 仅先验")
    else:
        w_similar = BASE_W_SIMILAR * reliability_from_brier(
            calibration_similar.brier if calibration_similar is not None else None
        )

    if w_similar <= 0.0:
        fused = dict(prior_v)
        weights = {"prior": 1.0, "similar": 0.0}
    else:
        total_w = w_prior + w_similar
        weights = {"prior": w_prior / total_w, "similar": w_similar / total_w}
        tilted = tilt_prior_along_pessimism(prior_v, tilt)
        fused = {s: weights["prior"] * prior_v[s] + weights["similar"] * tilted[s] for s in NextDayState}
        notes.append(
            f"相似日倾斜 {tilt:+.3f} 档（弱 {scenario.prob_weak:.2f}/强 {scenario.prob_strong:.2f}）"
        )

    e_fused = expected_pessimism_tier(fused)
    # argmax 平票取档位更悲观者：降序迭代使 max 平票命中先见到的更悲观态（风险方向保守）
    dominant_prior = max(sorted(NextDayState, key=lambda s: _TIER_OF[s], reverse=True), key=lambda s: prior_v[s])
    dominant_fused = max(sorted(NextDayState, key=lambda s: _TIER_OF[s], reverse=True), key=lambda s: fused[s])
    tier_gap = _TIER_OF[dominant_fused] - _TIER_OF[dominant_prior]
    warning = tier_gap >= DOWNGRADE_TIER_THRESHOLD
    if warning:
        notes.append(
            f"融合最可能态 {dominant_fused.value}（档 {_TIER_OF[dominant_fused]}）比先验 "
            f"{dominant_prior.value}（档 {_TIER_OF[dominant_prior]}）悲观 ≥ {DOWNGRADE_TIER_THRESHOLD} 档 → 明日降档预警"
        )
    return TomorrowForecast(
        distribution={s.value: float(fused[s]) for s in NextDayState},
        expected_tier_prior=e_prior,
        expected_tier_fused=e_fused,
        dominant_state=dominant_fused.value,
        dominant_tier_prior=_TIER_OF[dominant_prior],
        dominant_tier_fused=_TIER_OF[dominant_fused],
        downgrade_warning=warning,
        weights=weights,
        notes=notes,
        intraday_point=intraday_point,
    )


if __name__ == "__main__":  # noqa: m11-perm-manual-legitimate  M11豁免: 永久模块最小自检入口（分布融合冒烟），主体经 zephyr 导入消费（正式消费方=warroom W0 接线中）
    import argparse

    _ap = argparse.ArgumentParser(description="明日预告分布融合自检（无副作用冒烟）")
    _ap.add_argument("--selfcheck", action="store_true", help="跑一次空分布融合冒烟")
    _args = _ap.parse_args()
    if _args.selfcheck:
        from zephyr.plan_engine.intraday_tomorrow_forecast import fuse  # 自引用冒烟
        print("intraday_tomorrow_forecast selfcheck: fuse 可用")
