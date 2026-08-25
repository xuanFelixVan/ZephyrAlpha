# [BLUEPRINT] MOD-L02-001 | docs/03_modules/_domain_factor/blueprint.md
# [MODULE] zephyr.factor.analysis.bma_signal_weighter
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] 无 zephyr import（纯函数核；IC/ICIR 语义源自 MOD-L02-002 ic_ir_calc、IC 衰减语义源自 MOD-L02-004 ic_decay、体制条件源自 MOD-REGIME-001 regime_detector——均为注入数据不 import）
# [CONSUMERS] （候选：决策编排上游信号合成层/多因子叠加择时 B10-01482 装配批）
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 权重 Σ=1 且各维 ≥0；IC≤0.03 出局 / IC 衰减>50% 权重降0 / ICIR<0.5 降权不出局 / 体制条件IC≤0 出局；平滑 α=0.9 后重归一；一致性低+无主导信号（双低）→ NO_TRADE；纯函数无副作用
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 输入非法（空 id/方向非±1/衰减∉[0,1]/非有限数）→ ValueError（fail-closed）；空输入/全出局 → NO_TRADE 不抛错
# [TESTS] tests/factor/test_bma_signal_weighter.py
# [A_module] module_id=MOD-L02-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ALGO_FLOW]
# I1: 各信号评估 SignalEvaluation(ic/icir/ic_decay_ratio/direction/regime_ic?)
# A1: 预测力门禁——ic≤0.03 出局；decay>0.5 出局；icir<0.5 得分×0.5 降权；regime_ic≤0 出局
# A2: BMA 后验权重——softmax(κ·ic·icir) 伪似然（Hoeting 1999 BIC 近似轻量替代），Σ=1
# A3: 平滑——w_t=α·w_prev+(1-α)·w_raw（α=0.9），出局信号权重归 0 后重归一
# A4: 一致性置信度——方向加权多数派占比 agreement；双低（agreement<0.6 且 top_weight<0.5）→ NO_TRADE
# O1: BmaWeightReport(weights/gated_out/direction/agreement/confidence/decision)
# [/ALGO_FLOW]
"""模块48 动态信号权重模型（Bayesian Model Averaging，CAND-FAC-013 / B10-01481）。

多信号动态加权：以 BMA 后验模型权重替代静态等权/经验权重——每个信号视为一个
"预测模型"，按其伪似然（IC×ICIR，效果×稳定性）softmax 归一为后验权重，体制条件
IC 作硬过滤，时间平滑 α=0.9 防权重跳变，方向一致性+主导性双低时不操作。

工程裁定（MVP 落地形态，标定批可替换）：
  - Hoeting(1999) BMA 的 BIC 近似后验 w_i∝exp(-BIC_i/2) 轻量落地为
    softmax(κ·ic_i·icir_i)：icir=ic/std(ic) 即逐期 t 统计量代理，ic·icir 单调于
    伪似然，softmax 有界可归一；κ=1.0 为初拍标定值。
  - 门禁语义（候选注册表 problem 字段既定）：IC>0.03 有效（≤出局）、
    IC 衰减>50% 权重降0（出局）、ICIR>0.5 稳定（<0.5 降权 ×0.5 不出局）、
    体制条件 IC≤0 出局（当前体制无预测力）。
  - 平滑 α=0.9（TSV 既定）：w_t=0.9·w_{t-1}+0.1·w_raw，抑制单日权重跳变；
    出局信号残影权重归 0 后对留存信号重归一（Σ=1 不变量）。
  - 一致性置信度=方向加权多数派占比 agreement∈[0.5,1]；不操作裁定（TSV
    "低+低=不操作"）：agreement<0.6（一致性低）且 top_weight<0.5（无主导
    信号，权重分散）→ NO_TRADE。

查重裁定（不重复既有件）：
  - strength_ic_weight_calibrator（21 号 memo）：单一合成信号内部 6 维子分数的
    IC 加权校准，非跨信号 BMA 后验权重；输入/输出/消费者均不同。
  - 场内 grep 无 signal_weight_enhancer/signal_confidence_enhancer/BMA 既有件；
    atr_stop_engine 的 Bayesian 为风控 ATR 参数优化（D_RISK），域与职能均不同。

依据: A1交易决策架构 §9 模块48；construction_backlog_dig.tsv B10-01481。
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Final, Iterable, Mapping

__all__: Final = [
    "BmaSignalWeighter",
    "BmaWeightReport",
    "BmaWeighterConfig",
    "SignalEvaluation",
    "compute_bma_weights",
]

#: 决策枚举（字符串封闭集，避免 enum 序列化负担）
DECISION_TRADE: Final = "TRADE"
DECISION_NO_TRADE: Final = "NO_TRADE"

_GATE_IC_FLOOR: Final = "ic_below_floor"
_GATE_DECAY: Final = "ic_decay_exceeded"
_GATE_REGIME: Final = "regime_ic_nonpositive"


@dataclass(frozen=True)
class SignalEvaluation:
    """单信号预测力评估输入（IC/ICIR/IC 衰减/体制条件 IC + 方向）。

    Attributes:
        signal_id: 信号唯一 ID（非空）。
        ic: 信息系数（>0.03 为有效线，与因子库有效线一致）。
        icir: IC 稳定度（ic/std(ic)，>0.5 为稳定线）。
        ic_decay_ratio: IC 衰减比例 ∈[0,1]（>0.5 权重降 0）。
        direction: 信号方向（+1 多 / -1 空）。
        regime_ic: 当前体制条件 IC（可选；提供且 ≤0 → 出局）。
    """

    signal_id: str
    ic: float
    icir: float
    ic_decay_ratio: float
    direction: int
    regime_ic: float | None = None

    def __post_init__(self) -> None:
        if not self.signal_id:
            raise ValueError("signal_id 不能为空")
        for name in ("ic", "icir"):
            if not math.isfinite(getattr(self, name)):
                raise ValueError(f"{name} 必须为有限数: {getattr(self, name)!r}")
        if not 0.0 <= self.ic_decay_ratio <= 1.0:
            raise ValueError(f"ic_decay_ratio 必须 ∈[0,1]: {self.ic_decay_ratio!r}")
        if self.direction not in (1, -1):
            raise ValueError(f"direction 必须为 +1/-1: {self.direction!r}")
        if self.regime_ic is not None and not math.isfinite(self.regime_ic):
            raise ValueError(f"regime_ic 必须为有限数: {self.regime_ic!r}")


@dataclass(frozen=True)
class BmaWeighterConfig:
    """权重器参数（阈值全显式，不硬编码在判定体内）。

    Attributes:
        ic_floor: IC 有效线（≤出局）。
        icir_floor: ICIR 稳定线（<降权）。
        decay_drop_ratio: IC 衰减出局线（>出局）。
        unstable_discount: 不稳定信号得分降权系数。
        softmax_kappa: softmax 温度 κ（伪似然缩放，标定批替换）。
        smoothing_alpha: 时间平滑系数 α=0.9（TSV 既定）。
        agreement_floor: 一致性下限（低于=一致性低）。
        top_weight_floor: 主导权重下限（低于=无主导信号）。
    """

    ic_floor: float = 0.03
    icir_floor: float = 0.5
    decay_drop_ratio: float = 0.5
    unstable_discount: float = 0.5
    softmax_kappa: float = 1.0
    smoothing_alpha: float = 0.9
    agreement_floor: float = 0.6
    top_weight_floor: float = 0.5

    def __post_init__(self) -> None:
        if not 0.0 <= self.smoothing_alpha < 1.0:
            raise ValueError(f"smoothing_alpha 必须 ∈[0,1): {self.smoothing_alpha!r}")
        if self.softmax_kappa <= 0.0:
            raise ValueError(f"softmax_kappa 必须 >0: {self.softmax_kappa!r}")
        if not 0.0 <= self.unstable_discount <= 1.0:
            raise ValueError(f"unstable_discount 必须 ∈[0,1]: {self.unstable_discount!r}")


@dataclass(frozen=True)
class BmaWeightReport:
    """BMA 权重输出报告（不可变）。

    Attributes:
        weights: 归一化 BMA 动态权重 {signal_id: w}（Σ=1，空输入为 {}）。
        gated_out: 出局信号及理由 {signal_id: reason}。
        direction: 加权多数派方向（+1/-1；无信号为 0）。
        agreement: 方向一致性（多数派方向权重占比，无信号为 0.0）。
        confidence: 一致性置信度（=agreement，标定批可演进为复合分）。
        decision: TRADE / NO_TRADE。
    """

    weights: Mapping[str, float] = field(default_factory=dict)
    gated_out: Mapping[str, str] = field(default_factory=dict)
    direction: int = 0
    agreement: float = 0.0
    confidence: float = 0.0
    decision: str = DECISION_NO_TRADE

    def __post_init__(self) -> None:
        object.__setattr__(self, "weights", MappingProxyType(dict(self.weights)))
        object.__setattr__(self, "gated_out", MappingProxyType(dict(self.gated_out)))


def _gate(ev: SignalEvaluation, cfg: BmaWeighterConfig) -> str | None:
    """预测力门禁：返回出局理由（留存为 None）。"""
    if ev.ic <= cfg.ic_floor:
        return _GATE_IC_FLOOR
    if ev.ic_decay_ratio > cfg.decay_drop_ratio:
        return _GATE_DECAY
    if ev.regime_ic is not None and ev.regime_ic <= 0.0:
        return _GATE_REGIME
    return None


def _raw_scores(evaluations: Iterable[SignalEvaluation], cfg: BmaWeighterConfig) -> dict[str, float]:
    """softmax(κ·ic·icir) 伪似然得分（不稳定信号先 ×unstable_discount）。"""
    scores: dict[str, float] = {}
    for ev in evaluations:
        stability = ev.icir if ev.icir >= cfg.icir_floor else ev.icir * cfg.unstable_discount
        scores[ev.signal_id] = math.exp(cfg.softmax_kappa * ev.ic * stability)
    return scores


def _normalize(scores: Mapping[str, float]) -> dict[str, float]:
    total = sum(scores.values())
    if total <= 0.0:
        return {}
    return {sid: s / total for sid, s in scores.items()}


def _smooth(
    raw: Mapping[str, float],
    prev: Mapping[str, float],
    alpha: float,
) -> dict[str, float]:
    """时间平滑：w=α·prev+(1-α)·raw（prev 中已出局信号权重归 0），后重归一。"""
    if not raw:
        return {}
    blended = {
        sid: alpha * float(prev.get(sid, 0.0)) + (1.0 - alpha) * w
        for sid, w in raw.items()
    }
    return _normalize(blended)


def _agreement_and_direction(weights: Mapping[str, float], directions: Mapping[str, int]) -> tuple[float, int]:
    """方向一致性=多数派方向权重占比；方向=加权票和符号。"""
    long_w = sum(w for sid, w in weights.items() if directions[sid] > 0)
    short_w = sum(w for sid, w in weights.items() if directions[sid] < 0)
    total = long_w + short_w
    if total <= 0.0:
        return 0.0, 0
    if long_w >= short_w:
        return long_w / total, 1
    return short_w / total, -1


def compute_bma_weights(
    evaluations: Iterable[SignalEvaluation],
    *,
    config: BmaWeighterConfig | None = None,
    prev_weights: Mapping[str, float] | None = None,
) -> BmaWeightReport:
    """BMA 动态权重纯函数：门禁 → 伪似然后验 → 平滑 → 一致性置信度/不操作裁定。

    Args:
        evaluations: 各信号预测力评估（IC/ICIR/IC 衰减/体制条件 IC/方向）。
        config: 权重器参数（缺省默认阈值组）。
        prev_weights: 上一轮权重（时间平滑用；None=首轮不平滑）。

    Returns:
        BmaWeightReport（权重 Σ=1；空输入/全出局 → NO_TRADE + 空权重）。
    """
    cfg = config or BmaWeighterConfig()
    evs = list(evaluations)
    gated_out: dict[str, str] = {}
    survivors: list[SignalEvaluation] = []
    for ev in evs:
        reason = _gate(ev, cfg)
        if reason is None:
            survivors.append(ev)
        else:
            gated_out[ev.signal_id] = reason
    if not survivors:
        return BmaWeightReport(weights={}, gated_out=gated_out)

    raw = _normalize(_raw_scores(survivors, cfg))
    weights = _smooth(raw, prev_weights or {}, cfg.smoothing_alpha)
    directions = {ev.signal_id: ev.direction for ev in survivors}
    agreement, direction = _agreement_and_direction(weights, directions)
    top_weight = max(weights.values(), default=0.0)
    consistency_low = agreement < cfg.agreement_floor
    conviction_low = top_weight < cfg.top_weight_floor
    decision = DECISION_NO_TRADE if (consistency_low and conviction_low) else DECISION_TRADE
    return BmaWeightReport(
        weights=weights,
        gated_out=gated_out,
        direction=direction,
        agreement=round(agreement, 6),
        confidence=round(agreement, 6),
        decision=decision,
    )


class BmaSignalWeighter:
    """BMA 动态信号权重器（TSV 核心类）：跨轮次时间平滑状态载体。

    Args:
        config: 权重器参数（缺省 BmaWeighterConfig()）。
    """

    def __init__(self, *, config: BmaWeighterConfig | None = None) -> None:
        self._config = config or BmaWeighterConfig()
        self._prev_weights: dict[str, float] = {}

    @property
    def prev_weights(self) -> Mapping[str, float]:
        """上一轮权重快照（只读）。"""
        return MappingProxyType(dict(self._prev_weights))

    def update(self, evaluations: Iterable[SignalEvaluation]) -> BmaWeightReport:
        """摄入新一轮信号评估 → 平滑 BMA 权重报告；内部滚动 prev_weights。"""
        report = compute_bma_weights(evaluations, config=self._config, prev_weights=self._prev_weights)
        self._prev_weights = dict(report.weights)
        return report
