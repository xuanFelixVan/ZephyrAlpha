# [BLUEPRINT] MOD-PA-015 | docs/03_modules/_domain_portfolio_alloc/regime_bma_weighting/blueprint.md
# [MODULE] zephyr.pf_alloc.core.regime_bma_weighting
# [DOMAIN] D_PF_ALLOC
# [DEPENDENCIES] 无（权重估计纯内存；信号观测序列/审计回调/时钟全注入）
# [CONSUMERS] 运行时装配批（signal_synthesis_combiner 权重源 / 体制切换审计落库）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 滚动窗口=最近window条观测(默认250); 精度∈[0,1](命中率/IC负值截断0); 后验归一Σ=1(全零证据→均匀先验); 体制切换半衰期混合new_share=1-0.5^(t/half_life); 混合后再归一Σ=1; 权重变更必落审计回调(sink异常不阻断如实记录); 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_portfolio_alloc/regime_bma_weighting/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] RegimeBmaError(占位 ZA-PA-UNREGISTERED-REGIME-BMA)——空regime/空信号集/样本不足/观测非有限/参数非法/未估计先查询时抛
# [TESTS] tests/pf_alloc/test_regime_bma_weighting.py
# [A_module] module_id=MOD-PA-015 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""
RegimeBmaWeighting — 体制条件 BMA 信号权重（MOD-PA-015）。

B11-02963（AUD-DRAFT-001-DIGEST P2 波 P2-W09，CAND-PFALLOC-010，A7）：
regime 条件 BMA（贝叶斯模型平均思想轻量版）权重——

① 按市场体制分组，滚动 250 日（可配）估计各信号历史预测精度
   （命中率 hit_rate / 信息系数 IC 二选一注入）；
② 后验归一：posterior_i = precision_i / Σprecision（Σ=1；全零证据→均匀先验）；
③ 权重变更逐次落审计回调（regime/原始后验/生效权重/混合系数留痕）；
④ 体制切换权重平滑过渡：切换点快照旧权重，按半衰期混合
   new_share = 1 − 0.5^(t/half_life)（t=切换后更新次数），混合后再归一。

查重分工（蓝图 §0）：signal_synthesis_combiner=信号合成投票器（消费权重做
合成），本件=**权重生产侧**（按体制估计并平滑输出权重），不做信号合成。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: window 参数
#   fields: 参数 window（无注解）
#   code: regime_bma_weighting.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: half_life 参数
#   fields: 参数 half_life（无注解）
#   code: regime_bma_weighting.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: min_samples 参数
#   fields: 参数 min_samples（无注解）
#   code: regime_bma_weighting.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: metric 参数
#   fields: 参数 metric（无注解）
#   code: regime_bma_weighting.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① RegimeBmaWeighting
#   name_en: RegimeBmaWeighting
#   intro: 体制条件 BMA 信号权重估计器（纯内存确定性，审计/时钟注入）。
#   desc: 体制条件 BMA 信号权重估计器（纯内存确定性，审计/时钟注入）。；公共方法（定义序）: update, current_regime, current_weights；源码 L160-L282
#   inputs: window half_life min_samples metric audit_sink clock
#   outputs: 返回值
#   （注：A1 之后另有 4 个公共定义未列入（含 4 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（5 定义）
#   name_en: public defs
#   intro: RegimeBmaWeighting
#   downstream: 运行时装配批（signal_synthesis_combiner 权重源 / 体制切换审计落库）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> O1
"""

from __future__ import annotations

import datetime
import logging
import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Final

_log = logging.getLogger(__name__)

__all__: Final = [
    "PrecisionMetric",
    "RegimeBmaError",
    "RegimeBmaWeighting",
    "SignalOutcome",
    "WeightAuditEvent",
]


class RegimeBmaError(Exception):
    """体制条件 BMA 权重输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-PA-UNREGISTERED-REGIME-BMA。
    """


class PrecisionMetric(str, Enum):
    """历史预测精度估计口径。"""

    HIT_RATE = "hit_rate"  # 命中率：sign(forecast)==sign(realized) 占比
    IC = "ic"  # 信息系数：forecast 与 realized 的 Pearson 相关（负值截断 0）


@dataclass(frozen=True)
class SignalOutcome:
    """单条信号观测（预测值/实现值，frozen）。"""

    forecast: float
    realized: float


@dataclass(frozen=True)
class WeightAuditEvent:
    """权重变更审计事件（回调载荷，frozen）。"""

    regime: str
    switched: bool
    updates_in_regime: int
    new_share: float
    raw_posteriors: Mapping[str, float]
    effective_weights: Mapping[str, float]
    raised_at: datetime.datetime


def _sign(value: float) -> int:
    return (value > 0) - (value < 0)


def _hit_rate(series: Sequence[SignalOutcome]) -> float:
    hits = sum(1 for o in series if _sign(o.forecast) == _sign(o.realized))
    return hits / len(series)


def _ic(series: Sequence[SignalOutcome]) -> float:
    n = len(series)
    mean_f = sum(o.forecast for o in series) / n
    mean_r = sum(o.realized for o in series) / n
    cov = sum((o.forecast - mean_f) * (o.realized - mean_r) for o in series)
    var_f = sum((o.forecast - mean_f) ** 2 for o in series)
    var_r = sum((o.realized - mean_r) ** 2 for o in series)
    denom = math.sqrt(var_f * var_r)
    if denom <= 0:
        return 0.0  # 零方差无信息 → 精度 0
    return max(cov / denom, 0.0)


_PRECISION_FN: Final = {
    PrecisionMetric.HIT_RATE: _hit_rate,
    PrecisionMetric.IC: _ic,
}


class RegimeBmaWeighting:
    """体制条件 BMA 信号权重估计器（纯内存确定性，审计/时钟注入）。"""

    def __init__(
        self,
        *,
        window: int = 250,
        half_life: int = 5,
        min_samples: int = 2,
        metric: PrecisionMetric = PrecisionMetric.HIT_RATE,
        audit_sink: Callable[[WeightAuditEvent], None] | None = None,
        clock: Callable[[], datetime.datetime] | None = None,
    ) -> None:
        if isinstance(window, bool) or not isinstance(window, int) or window < 1:
            raise RegimeBmaError(f"window 须为正整数: {window!r}")
        if isinstance(half_life, bool) or not isinstance(half_life, int) or half_life < 1:
            raise RegimeBmaError(f"half_life 须为正整数: {half_life!r}")
        if isinstance(min_samples, bool) or not isinstance(min_samples, int) or min_samples < 1:
            raise RegimeBmaError(f"min_samples 须为正整数: {min_samples!r}")
        if not isinstance(metric, PrecisionMetric):
            raise RegimeBmaError(f"非法精度口径: {metric!r}")
        self._window = window
        self._half_life = half_life
        self._min_samples = min_samples
        self._metric = metric
        self._audit_sink = audit_sink
        self._clock = clock or datetime.datetime.now
        self._regime: str | None = None
        self._weights: dict[str, float] = {}
        self._prev_weights: dict[str, float] | None = None
        self._updates_in_regime = 0

    # ── 内部 ─────────────────────────────────────────────────────────────

    def _posteriors(self, observations: Mapping[str, Sequence[SignalOutcome]]) -> dict[str, float]:
        fn = _PRECISION_FN[self._metric]
        precisions: dict[str, float] = {}
        for signal_id in sorted(observations):
            series = observations[signal_id]
            tail = series[-self._window :] if len(series) > self._window else list(series)
            precisions[signal_id] = fn(tail)
        total = sum(precisions.values())
        n = len(precisions)
        if total <= 0:
            return {sid: 1.0 / n for sid in sorted(precisions)}  # 全零证据→均匀先验
        return {sid: precisions[sid] / total for sid in sorted(precisions)}

    def _audit(self, event: WeightAuditEvent) -> None:
        if self._audit_sink is not None:
            try:
                self._audit_sink(event)
            except Exception:  # noqa: BLE001 — 审计不阻断（蓝图 §1）
                _log.exception("audit_sink 审计失败")

    # ── 估计 ─────────────────────────────────────────────────────────────

    def update(self, *, regime: str, observations: Mapping[str, Sequence[SignalOutcome]]) -> dict[str, float]:
        """按体制更新权重：精度估计→后验归一→切换半衰期平滑→审计留痕。"""
        if not isinstance(regime, str) or not regime:
            raise RegimeBmaError("regime 为空")
        if not observations:
            raise RegimeBmaError("observations 为空（无信号观测）")
        for signal_id, series in observations.items():
            if not signal_id:
                raise RegimeBmaError("signal_id 为空")
            if len(series) < self._min_samples:
                raise RegimeBmaError(f"样本不足: {signal_id!r} 仅 {len(series)} 条 < min_samples={self._min_samples}")
            for o in series:
                if not isinstance(o, SignalOutcome):
                    raise RegimeBmaError(f"观测须为 SignalOutcome: {o!r}")
                if not math.isfinite(o.forecast) or not math.isfinite(o.realized):
                    raise RegimeBmaError(f"观测非有限: {o!r}")

        switched = self._regime is not None and regime != self._regime
        if switched:
            self._prev_weights = dict(self._weights)
            self._updates_in_regime = 0
        if self._regime != regime:
            self._regime = regime
        self._updates_in_regime += 1

        raw = self._posteriors(observations)
        if self._prev_weights is None:
            effective = raw
            new_share = 1.0
        else:
            new_share = 1.0 - 0.5 ** (self._updates_in_regime / self._half_life)
            ids = sorted(set(raw) | set(self._prev_weights))
            blended = {
                sid: new_share * raw.get(sid, 0.0) + (1.0 - new_share) * self._prev_weights.get(sid, 0.0) for sid in ids
            }
            total = sum(blended.values())
            if total <= 0:
                effective = {sid: 1.0 / len(ids) for sid in ids}
            else:
                effective = {sid: blended[sid] / total for sid in ids}
        self._weights = effective
        self._audit(
            WeightAuditEvent(
                regime=regime,
                switched=switched,
                updates_in_regime=self._updates_in_regime,
                new_share=new_share,
                raw_posteriors=dict(raw),
                effective_weights=dict(effective),
                raised_at=self._clock(),
            )
        )
        _log.info("体制BMA权重更新: regime=%s t=%d new_share=%.4f", regime, self._updates_in_regime, new_share)
        return dict(effective)

    # ── 查询 ─────────────────────────────────────────────────────────────

    @property
    def current_regime(self) -> str | None:
        """当前体制（未更新过=None）。"""
        return self._regime

    def current_weights(self) -> dict[str, float]:
        """当前生效权重（未估计 → Fail-Closed）。"""
        if self._regime is None:
            raise RegimeBmaError("尚未估计（无历史 update），权重不可用")
        return dict(self._weights)
