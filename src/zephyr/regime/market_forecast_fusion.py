# [BLUEPRINT] MOD-REGIME-012 | docs/03_modules/_domain_regime/market_forecast_fusion/blueprint.md
# [MODULE] zephyr.regime.market_forecast_fusion
# [DOMAIN] D_REGIME
# [DEPENDENCIES] zephyr.signal_ashare.next_day_8state_forecast
# [CONSUMERS] 运行时装配批（外部主播信号注入 / log_sink 接 prediction_log_writer）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 融合分布 Σ=1.0; confidence∈[0,1]; 外部信号畸形/配置非法 Fail-Closed; 只出概率分布与置信度不出点位/买卖信号（90号§7裁定）; 写库委托 log_sink 不直连 DB; log_sink 异常不阻断如实记录
# [MODIFY-GUARD] tests/regime/test_market_forecast_fusion.py
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] FusionConfigError+InvalidExternalForecastError(未登记错误码-申请中)
# [TESTS] tests/regime/test_market_forecast_fusion.py
# [A_module] module_id=MOD-REGIME-012 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""C-014 大盘预测三层融合（MOD-REGIME-012）。

真源：construction_backlog_dig.tsv B1-00154（跨域元文档 §功能域模块·D-SIGNAL，
裁定=做 P1）+ CAND-CYCLE-004。

三层融合（TSV 缺口：8 态预测单点 MOD-SIG-037 在，三层融合未成）：
  ① 系统内部模型——MOD-SIG-037 NextDayForecast（8 态分布+置信度，不重造引擎）；
  ② 外部主播信号采集打分——ExternalForecast（source_id+8 态分布+自报置信度），
     采集面归 D_ALT_DATA，本模块只收构造好的信号（注入）；
  ③ 滚动准确率动态加权——RollingAccuracyTracker 按源滚动记录众数态命中，
     weight=max(accuracy, min_weight) 归一；融合分布=Σ w_i×dist_i 再归一。

边界声明（对齐 90 号 §7 裁定与 MOD-SIG-037）：本模块**只输出概率分布与置信度，
不出点位、不出买卖信号**；预测日志经 log_sink 回调委托 MOD-RPT-028
prediction_log_writer 落库（装配批接线），写库异常不阻断融合产出。
"""

from __future__ import annotations

import logging
from collections import deque
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from typing import Final

from zephyr.signal_ashare.next_day_8state_forecast import NextDayForecast, NextDayState

__all__: Final = [
    "INTERNAL_SOURCE_ID",
    "ExternalForecast",
    "FusedForecast",
    "FusionConfigError",
    "InvalidExternalForecastError",
    "MarketForecastFusion",
    "RollingAccuracyTracker",
]

_log = logging.getLogger(__name__)

_STATE_VALUES: Final[tuple[str, ...]] = tuple(s.value for s in NextDayState)
_STATE_SET: Final[frozenset[str]] = frozenset(_STATE_VALUES)
_N_STATES: Final[int] = len(_STATE_VALUES)

#: 内部层信号源 ID（保留字，外部源不可用）
INTERNAL_SOURCE_ID: Final[str] = "internal"

#: 融合产出在 prediction_log 的模块标识与预测类型（MOD-RPT-028 唯一键字段）
_MODULE_ID: Final[str] = "market_forecast_fusion"
_PREDICTION_TYPE: Final[str] = "next_day_8state_fusion"


class FusionConfigError(ValueError):
    """融合配置非法或调用时序非法（Fail-Closed；未登记错误码-申请中）。"""


class InvalidExternalForecastError(ValueError):
    """外部主播信号畸形（Fail-Closed；未登记错误码-申请中）。"""


def _validate_state_distribution(probabilities: Mapping[str, float]) -> dict[str, float]:
    """8 态分布校验 + 归一：态键全集/概率非负/Σ>0（Fail-Closed）。"""
    keys = set(probabilities)
    if keys != _STATE_SET:
        missing = _STATE_SET - keys
        extra = keys - _STATE_SET
        raise InvalidExternalForecastError(
            f"8 态分布键集不齐: 缺 {sorted(missing)} 多 {sorted(extra)}（态真源=MOD-SIG-037）"
        )
    probs = {k: float(v) for k, v in probabilities.items()}
    if any(v < 0.0 for v in probs.values()):
        raise InvalidExternalForecastError(f"存在负概率: {probs}")
    total = sum(probs.values())
    if total <= 0.0:
        raise InvalidExternalForecastError("概率和为 0（无法归一）")
    return {k: v / total for k, v in probs.items()}


@dataclass(frozen=True)
class ExternalForecast:
    """外部主播信号（层2 输入；采集面归 D_ALT_DATA，本模块只收构造好的信号）。

    Attributes:
        source_id: 信号源标识（非空；INTERNAL_SOURCE_ID 为内部层保留字）
        probabilities: 次日 8 态分布（输入自动归一，Σ=1）
        confidence: 源自报置信度 ∈[0,1]（留痕口径，不参与权重——权重由滚动
            准确率唯一决定，防自报虚高抬权）
    """

    source_id: str
    probabilities: dict[str, float]
    confidence: float

    def __post_init__(self) -> None:
        if not self.source_id or not self.source_id.strip():
            raise InvalidExternalForecastError("source_id 为空")
        if self.source_id == INTERNAL_SOURCE_ID:
            raise InvalidExternalForecastError(
                f"source_id={INTERNAL_SOURCE_ID!r} 为内部层保留字"
            )
        if not 0.0 <= self.confidence <= 1.0:
            raise InvalidExternalForecastError(f"confidence 须 ∈[0,1]: {self.confidence}")
        object.__setattr__(
            self, "probabilities", _validate_state_distribution(self.probabilities)
        )


@dataclass(frozen=True)
class FusedForecast:
    """三层融合产出（只出分布与置信度，不出点位/买卖信号）。

    Attributes:
        probabilities: 融合后次日 8 态分布（Σ=1）
        top_state: 众数态（概率最大；并列取态序前者，确定性）
        top_probability: 众数态概率 ∈[0,1]
        confidence: top_probability × 众数态源一致度（权重占比）∈[0,1]
        weights: 各源归一权重（含内部层）
        log_signaled: 预测日志回调已送达（log_sink 异常=False 如实记录）
    """

    probabilities: dict[str, float]
    top_state: str
    top_probability: float
    confidence: float
    weights: dict[str, float]
    log_signaled: bool = False


class RollingAccuracyTracker:
    """滚动准确率动态加权器（层3）。

    按源维护尾部 window 次众数态命中记录；accuracy 用 Beta 先验平滑
    （p0=1/8 八态随机命中率，强度 α=prior_strength——初拟待实盘标定），
    weight = max(accuracy, min_weight)。
    """

    def __init__(
        self,
        window: int = 60,
        prior_strength: float = 16.0,
        min_weight: float = 0.05,
    ) -> None:
        if window < 1:
            raise FusionConfigError(f"window 须 >=1: {window}")
        if prior_strength < 0.0:
            raise FusionConfigError(f"prior_strength 须 >=0: {prior_strength}")
        if not 0.0 < min_weight <= 1.0:
            raise FusionConfigError(f"min_weight 须 ∈(0,1]: {min_weight}")
        self._window = window
        self._prior_hit_rate = 1.0 / _N_STATES
        self._prior_strength = prior_strength
        self._min_weight = min_weight
        self._hits: dict[str, deque[bool]] = {}

    @property
    def window(self) -> int:
        return self._window

    def record(self, source_id: str, predicted_top: str, actual: str) -> None:
        """记录一次预测结算（predicted_top==actual 记命中），窗口尾部滚动。"""
        buf = self._hits.setdefault(source_id, deque(maxlen=self._window))
        buf.append(predicted_top == actual)

    def accuracy(self, source_id: str) -> float:
        """Beta 先验平滑准确率：冷启动=p0=1/8。"""
        buf = self._hits.get(source_id)
        n = len(buf) if buf is not None else 0
        hits = sum(buf) if buf is not None else 0
        denominator = n + self._prior_strength
        if denominator == 0.0:  # prior_strength=0 且无记录 → 冷启动口径
            return self._prior_hit_rate
        return (hits + self._prior_strength * self._prior_hit_rate) / denominator

    def weight(self, source_id: str) -> float:
        """动态权重：max(accuracy, min_weight)（下限防单源归零永不翻身）。"""
        return max(self.accuracy(source_id), self._min_weight)


class MarketForecastFusion:
    """C-014 三层融合判定核心（纯函数 + 回调信号契约，执行体委托装配批）。"""

    def __init__(
        self,
        tracker: RollingAccuracyTracker | None = None,
        log_sink: Callable[[dict], None] | None = None,
    ) -> None:
        self._tracker = tracker or RollingAccuracyTracker()
        self._log_sink = log_sink
        self._pending_tops: dict[str, str] | None = None

    def fuse(
        self,
        internal: NextDayForecast,
        external: Sequence[ExternalForecast] = (),
        *,
        trade_date: str | None = None,
    ) -> FusedForecast:
        """三层融合：内部 8 态分布 + 外部信号 → 动态加权融合分布。

        Args:
            internal: MOD-SIG-037 内部模型产出（层1）。
            external: 外部主播信号序列（层2；可为空）。
            trade_date: 交易日（给定时经 log_sink 上报预测日志，装配批接
                MOD-RPT-028；sink 异常不阻断，log_signaled 如实记录）。
        """
        dists: dict[str, dict[str, float]] = {
            INTERNAL_SOURCE_ID: _validate_state_distribution(
                {s.value: p for s, p in internal.probabilities.items()}
            )
        }
        for ef in external:
            if ef.source_id in dists:
                raise InvalidExternalForecastError(f"source_id 重复: {ef.source_id!r}")
            dists[ef.source_id] = ef.probabilities

        raw_weights = {sid: self._tracker.weight(sid) for sid in dists}
        w_total = sum(raw_weights.values())
        weights = {sid: w / w_total for sid, w in raw_weights.items()}

        fused = {s: 0.0 for s in _STATE_VALUES}
        for sid, dist in dists.items():
            w = weights[sid]
            for state, p in dist.items():
                fused[state] += w * p
        f_total = sum(fused.values())
        fused = {s: p / f_total for s, p in fused.items()}

        top_state = max(_STATE_VALUES, key=lambda s: fused[s])
        top_prob = fused[top_state]
        # 众数态源一致度：各源自身众数态==融合众数态的权重占比
        agreement = 0.0
        tops: dict[str, str] = {}
        for sid, dist in dists.items():
            sid_top = max(_STATE_VALUES, key=lambda s: dist[s])
            tops[sid] = sid_top
            if sid_top == top_state:
                agreement += weights[sid]
        confidence = top_prob * agreement
        self._pending_tops = tops

        log_signaled = False
        if trade_date is not None and self._log_sink is not None:
            payload = self.build_log_payload(
                trade_date,
                FusedForecast(fused, top_state, top_prob, confidence, weights),
            )
            try:
                self._log_sink(payload)
                log_signaled = True
            except Exception as exc:  # noqa: BLE001 — 日志面异常不阻断融合产出
                _log.warning("log_sink 异常（预测日志未送达，融合产出不受影响）: %s", exc)

        return FusedForecast(
            probabilities=fused,
            top_state=top_state,
            top_probability=top_prob,
            confidence=confidence,
            weights=weights,
            log_signaled=log_signaled,
        )

    def settle(self, actual_state: str) -> dict[str, bool]:
        """复盘结算：实际态回写各源滚动准确率（供次日动态加权更新）。

        须先于 fuse 调用（pending 众数态缺失即 Fail-Closed，防时序错乱）；
        返回各源命中报告。
        """
        if actual_state not in _STATE_SET:
            raise FusionConfigError(f"未知 8 态: {actual_state!r}（态真源=MOD-SIG-037）")
        if self._pending_tops is None:
            raise FusionConfigError("settle 前须先 fuse（无待结算众数态）")
        report: dict[str, bool] = {}
        for sid, top in self._pending_tops.items():
            hit = top == actual_state
            self._tracker.record(sid, top, actual_state)
            report[sid] = hit
        self._pending_tops = None
        return report

    @staticmethod
    def build_log_payload(trade_date: str, fused: FusedForecast) -> dict:
        """构造 prediction_log 写入 payload（MOD-RPT-028 log_prediction 契约）。

        唯一键字段（trade_date/module/prediction_type）+ JSON 可序列化 payload；
        写库与 input_hash/幂等语义归 prediction_log_writer，本模块不涉。
        """
        return {
            "trade_date": trade_date,
            "module": _MODULE_ID,
            "prediction_type": _PREDICTION_TYPE,
            "payload": {
                "probabilities": dict(fused.probabilities),
                "top_state": fused.top_state,
                "top_probability": fused.top_probability,
                "confidence": fused.confidence,
                "weights": dict(fused.weights),
            },
        }
