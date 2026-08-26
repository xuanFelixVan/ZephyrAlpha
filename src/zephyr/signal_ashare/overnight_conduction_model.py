# [BLUEPRINT] MOD-SIG-117 | docs/03_modules/_domain_signal/overnight_conduction_model/blueprint.md
# [MODULE] zephyr.signal_ashare.overnight_conduction_model
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] 无（协议核心纯内存；回归器/历史事件库/时钟全注入，不 import zephyr 内部件）
# [CONSUMERS] 运行时装配批（统一注入点装配：隔夜传导评分层 / 开盘缺口预判消费方）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 事件四分类词表闭合(policy|geopolitical|data|black_swan)×预期内外二分；回归器未注入Fail-Closed不旁路；30分钟衰减=分段|收益|贡献比（总位移为0时贡献比全0）；影响评分∈[0,100]权重归一；同输入必同输出（确定性）
# [MODIFY-GUARD] docs/03_modules/_domain_signal/overnight_conduction_model/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] OvernightConductionError(占位 ZA-SIG-UNREGISTERED-OVERNIGHT-CONDUCTION)——样本不足/回归器缺失或异常/非有限读数/非法配置/未知事件类型时抛
# [TESTS] tests/signal_ashare/test_overnight_conduction_model.py
# [A_module] module_id=MOD-SIG-117 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""OvernightConductionModel — 隔夜全球传导评估模型（MOD-SIG-117）。

B10-01375（AUD-DRAFT-001-DIGEST P2 波 P2-W05，CAND-TESTB-037，A1 模块21）：
隔夜 β 传导系数（外盘收益 → A股开盘缺口，注入回归器）+ 30 分钟衰减检验
（开盘后分段收益贡献比）+ 事件四分类（政策/地缘/数据/黑天鹅）× 预期内外
影响时长统计表（历史事件库注入）+ 影响评分输出。

纯内存/DI 设计：回归器/事件库/时钟全注入；不触网、不触盘、无 subprocess。
同输入必同输出。非法输入 Fail-Closed 抛 OvernightConductionError。
"""

from __future__ import annotations

import datetime
import logging
import math
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Final, Mapping, Sequence

_log = logging.getLogger(__name__)

__all__: Final = [
    "ConductionReport",
    "EventExpectation",
    "EventImpactStat",
    "GapSample",
    "ImpactLevel",
    "IntradaySegments",
    "OvernightConductionConfig",
    "OvernightConductionError",
    "OvernightConductionModel",
    "OvernightEvent",
    "OvernightEventType",
    "RegressionResult",
]


class OvernightConductionError(Exception):
    """隔夜传导评估输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-SIG-UNREGISTERED-OVERNIGHT-CONDUCTION。
    """


class OvernightEventType(str, Enum):
    """隔夜事件四分类（词表闭合）。"""

    POLICY = "policy"
    GEOPOLITICAL = "geopolitical"
    DATA = "data"
    BLACK_SWAN = "black_swan"


class EventExpectation(str, Enum):
    """事件预期内外（词表闭合）。"""

    EXPECTED = "expected"
    UNEXPECTED = "unexpected"


class ImpactLevel(str, Enum):
    """影响评分档位（词表闭合）。"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


#: 事件基础严重度（评分用，词表闭合映射）
_EVENT_BASE_SEVERITY: Final[dict["OvernightEventType", float]] = {
    OvernightEventType.POLICY: 0.6,
    OvernightEventType.GEOPOLITICAL: 0.7,
    OvernightEventType.DATA: 0.4,
    OvernightEventType.BLACK_SWAN: 1.0,
}

#: 预期内外乘子（预期外全额，预期内打折）
_EXPECTATION_MULTIPLIER: Final[dict["EventExpectation", float]] = {
    EventExpectation.EXPECTED: 0.6,
    EventExpectation.UNEXPECTED: 1.0,
}


def _check_finite(name: str, v: float) -> None:
    if isinstance(v, bool) or not math.isfinite(v):
        raise OvernightConductionError(f"{name} 非有限数: {v!r}")


@dataclass(frozen=True)
class GapSample:
    """隔夜样本：外盘收益 → A股开盘缺口（frozen）。"""

    foreign_return: float
    opening_gap: float

    def __post_init__(self) -> None:
        _check_finite("foreign_return", self.foreign_return)
        _check_finite("opening_gap", self.opening_gap)


@dataclass(frozen=True)
class IntradaySegments:
    """开盘后分段收益（首段=30分钟段；≥1段，全有限）。"""

    segment_returns: tuple[float, ...]

    def __post_init__(self) -> None:
        if not self.segment_returns:
            raise OvernightConductionError("segment_returns 为空")
        for r in self.segment_returns:
            _check_finite("segment_return", r)


@dataclass(frozen=True)
class OvernightEvent:
    """历史事件库条目（frozen；影响时长 ≥0）。"""

    event_type: OvernightEventType
    expectation: EventExpectation
    impact_hours: float

    def __post_init__(self) -> None:
        if not isinstance(self.event_type, OvernightEventType):
            raise OvernightConductionError(f"未知事件类型: {self.event_type!r}")
        if not isinstance(self.expectation, EventExpectation):
            raise OvernightConductionError(f"未知预期分类: {self.expectation!r}")
        _check_finite("impact_hours", self.impact_hours)
        if self.impact_hours < 0:
            raise OvernightConductionError(f"impact_hours 不可为负: {self.impact_hours}")


@dataclass(frozen=True)
class RegressionResult:
    """注入回归器返回契约（frozen；slope/intercept/r_squared 全有限）。"""

    slope: float
    intercept: float
    r_squared: float

    def __post_init__(self) -> None:
        _check_finite("slope", self.slope)
        _check_finite("intercept", self.intercept)
        _check_finite("r_squared", self.r_squared)


@dataclass(frozen=True)
class EventImpactStat:
    """事件四分类×预期内外单元格统计（frozen）。"""

    event_type: OvernightEventType
    expectation: EventExpectation
    sample_count: int
    mean_impact_hours: float
    max_impact_hours: float


@dataclass(frozen=True)
class OvernightConductionConfig:
    """传导评估配置（frozen）。"""

    min_samples: int = 5
    decay_segment_index: int = 0
    decay_concentration_threshold: float = 0.5
    beta_scale: float = 2.0
    beta_weight: float = 0.35
    r2_weight: float = 0.25
    decay_weight: float = 0.20
    event_weight: float = 0.20
    high_threshold: float = 60.0
    medium_threshold: float = 30.0

    def __post_init__(self) -> None:
        if isinstance(self.min_samples, bool) or self.min_samples < 2:
            raise OvernightConductionError(f"min_samples 必须 ≥2: {self.min_samples!r}")
        if isinstance(self.decay_segment_index, bool) or self.decay_segment_index < 0:
            raise OvernightConductionError(
                f"decay_segment_index 必须 ≥0: {self.decay_segment_index!r}"
            )
        for name in (
            "decay_concentration_threshold", "beta_scale",
            "beta_weight", "r2_weight", "decay_weight", "event_weight",
            "high_threshold", "medium_threshold",
        ):
            _check_finite(name, getattr(self, name))
        if not (0.0 < self.decay_concentration_threshold <= 1.0):
            raise OvernightConductionError(
                f"decay_concentration_threshold 须在 (0,1]: {self.decay_concentration_threshold}"
            )
        if self.beta_scale <= 0:
            raise OvernightConductionError(f"beta_scale 必须为正: {self.beta_scale}")
        weights = (self.beta_weight, self.r2_weight, self.decay_weight, self.event_weight)
        if any(w < 0 for w in weights) or sum(weights) <= 0:
            raise OvernightConductionError(f"评分权重须非负且和为正: {weights!r}")
        if not (0 < self.medium_threshold < self.high_threshold <= 100.0):
            raise OvernightConductionError(
                f"档位阈值须 0<medium<high≤100: {self.medium_threshold}/{self.high_threshold}"
            )


@dataclass(frozen=True)
class ConductionReport:
    """隔夜传导评估报告（frozen）。"""

    beta: float
    r_squared: float
    segment_contributions: tuple[float, ...]
    decay_ratio: float
    decay_concentrated: bool
    event_stats: tuple[EventImpactStat, ...]
    score: float
    level: ImpactLevel
    generated_at: datetime.datetime


class OvernightConductionModel:
    """隔夜全球传导评估模型（β 回归 + 30分钟衰减 + 事件统计表 + 影响评分）。"""

    def __init__(
        self,
        *,
        config: OvernightConductionConfig | None = None,
        regressor: Callable[[tuple[float, ...], tuple[float, ...]], RegressionResult] | None = None,
        clock: Callable[[], datetime.datetime] | None = None,
    ) -> None:
        self._config = config or OvernightConductionConfig()
        self._regressor = regressor
        self._clock = clock or datetime.datetime.now

    # ── 事件影响时长统计表 ────────────────────────────────────────────────

    def event_impact_table(
        self, events: Sequence[OvernightEvent]
    ) -> tuple[EventImpactStat, ...]:
        """四分类×预期内外全 8 格统计（枚举定义序，确定性）。"""
        events = tuple(events)
        for e in events:
            if not isinstance(e, OvernightEvent):
                raise OvernightConductionError(f"非 OvernightEvent 元素: {type(e)!r}")
        out: list[EventImpactStat] = []
        for et in OvernightEventType:
            for ex in EventExpectation:
                cell = [
                    e.impact_hours for e in events
                    if e.event_type is et and e.expectation is ex
                ]
                n = len(cell)
                out.append(EventImpactStat(
                    event_type=et,
                    expectation=ex,
                    sample_count=n,
                    mean_impact_hours=(sum(cell) / n) if n else 0.0,
                    max_impact_hours=max(cell) if cell else 0.0,
                ))
        return tuple(out)

    # ── 主入口 ────────────────────────────────────────────────────────────

    def evaluate(
        self,
        samples: Sequence[GapSample],
        segments: IntradaySegments,
        events: Sequence[OvernightEvent] = (),
    ) -> ConductionReport:
        """评估隔夜传导：β 回归 → 30分钟衰减 → 事件统计 → 影响评分。"""
        if self._regressor is None:
            raise OvernightConductionError("回归器未注入（Fail-Closed，禁止旁路拟合）")
        samples = tuple(samples)
        if len(samples) < self._config.min_samples:
            raise OvernightConductionError(
                f"隔夜样本不足: {len(samples)} < min_samples={self._config.min_samples}"
            )
        for s in samples:
            if not isinstance(s, GapSample):
                raise OvernightConductionError(f"非 GapSample 元素: {type(s)!r}")
        if not isinstance(segments, IntradaySegments):
            raise OvernightConductionError(f"非 IntradaySegments: {type(segments)!r}")

        xs = tuple(s.foreign_return for s in samples)
        ys = tuple(s.opening_gap for s in samples)
        try:
            result = self._regressor(xs, ys)
        except OvernightConductionError:
            raise
        except Exception as exc:  # noqa: BLE001 — 回归器异常统一包装 Fail-Closed
            raise OvernightConductionError(f"注入回归器异常: {exc!r}") from exc
        if not isinstance(result, RegressionResult):
            raise OvernightConductionError(f"回归器返回非法类型: {type(result)!r}")

        beta = result.slope
        r2 = result.r_squared

        # 30分钟衰减：分段 |收益| 贡献比
        seg = tuple(segments.segment_returns)
        total = sum(abs(r) for r in seg)
        if total > 0:
            contributions = tuple(abs(r) / total for r in seg)
        else:
            contributions = tuple(0.0 for _ in seg)
        idx = self._config.decay_segment_index
        decay_ratio = contributions[idx] if idx < len(contributions) else 0.0
        decay_concentrated = total > 0 and decay_ratio >= self._config.decay_concentration_threshold

        stats = self.event_impact_table(events)

        # 影响评分（权重归一，满分 100）
        cfg = self._config
        beta_component = min(abs(beta) / cfg.beta_scale, 1.0)
        r2_component = min(max(r2, 0.0), 1.0)
        decay_component = decay_ratio
        event_component = 0.0
        for e in events:
            sev = _EVENT_BASE_SEVERITY[e.event_type] * _EXPECTATION_MULTIPLIER[e.expectation]
            if sev > event_component:
                event_component = sev
        wsum = cfg.beta_weight + cfg.r2_weight + cfg.decay_weight + cfg.event_weight
        score = 100.0 * (
            cfg.beta_weight * beta_component
            + cfg.r2_weight * r2_component
            + cfg.decay_weight * decay_component
            + cfg.event_weight * event_component
        ) / wsum
        if score >= cfg.high_threshold:
            level = ImpactLevel.HIGH
        elif score >= cfg.medium_threshold:
            level = ImpactLevel.MEDIUM
        else:
            level = ImpactLevel.LOW

        report = ConductionReport(
            beta=beta,
            r_squared=r2,
            segment_contributions=contributions,
            decay_ratio=decay_ratio,
            decay_concentrated=decay_concentrated,
            event_stats=stats,
            score=score,
            level=level,
            generated_at=self._clock(),
        )
        _log.debug(
            "隔夜传导: beta=%.4f r2=%.4f decay=%.4f score=%.2f level=%s",
            beta, r2, decay_ratio, score, level.value,
        )
        return report
