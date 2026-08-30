# [BLUEPRINT] MOD-SIG-134 | docs/03_modules/_domain_signal/strategy_vote_integrator/blueprint.md
# [MODULE] zephyr.signal_ashare.strategy_vote_integrator
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] zephyr.shared.foundation.errors（纯函数核，不 import 三零件实现只消费其输出契约）
# [CONSUMERS] 运行时装配批（统一注入点装配）；候选：第六层组合优化 B10-01505 W-P1-21
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 权重三调整序固定(衰减→相关性惩罚→同向 tally);相关性惩罚每策略至多一次且罚权重较小侧;弃权(direction=0)不计入分母;≥2/3同向权重占比才放行;A股无做空——净方向<0输出EXIT非SHORT;同输入必同输出
# [MODIFY-GUARD] tests/signal_ashare/test_strategy_vote_integrator.py
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] StrategyVoteIntegratorError(ZA-SIG-0134)——空symbol/重复strategy_id/非法direction/负权重/置信度越界/负龄期/非法配置时抛(Fail-Closed)
# [TESTS] tests/signal_ashare/test_strategy_vote_integrator.py
# [A_module] module_id=MOD-SIG-134 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent

"""StrategyVoteIntegrator — 多策略投票加权整合器（MOD-SIG-134，CAND-SIG-004）。

整合口径单件：聚合三零件输出 → 相关性惩罚 → ≥2/3 同向阈值 → 统一决策信号契约
（标的/方向/强度/置信度/参与策略明细）：

  - IC 加权：输入 weight 即 MOD-SIG-131 SignalWeightAdjuster.current_weight
    （滚动 IC 三指标调节产出的现行权重），本件不重复调权只做消费
  - 衰减自适应：weight × 0.5^(age_days / half_life)（信号龄期越久权重越低）
  - 相关性惩罚：两两相关 |ρ| ≥ 阈值的策略对，权重较小侧降权 ×penalty
    （防同源策略重复计票），每策略至多被罚一次（不叠加复利式惩罚）
  - 同向阈值：多数方向权重占比 ≥ 2/3 才放行，否则分歧否决（NONE）
  - 冲突语义对齐 MOD-SIG-010：A股无做空，净方向 <0 输出 EXIT 非 SHORT

与三零件分工：MOD-SIG-109=三席投票漏斗（票仓结构）；MOD-SIG-131=权重调节
（权重真源）；MOD-SIG-010=同标的矛盾裁定（规则链）；本件=整合口径（单件输出）。

SSoT: depgraph blueprint_id=MOD-SIG-134 | CAND-SIG-004
Version: 0.1.0
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass
from typing import Final, Mapping

from zephyr.shared.foundation.errors import ZephyrBaseError

_log = logging.getLogger(__name__)

__all__: Final = [
    "IntegratedDecision",
    "ParticipantDetail",
    "StrategyVoteSignal",
    "StrategyVoteIntegratorError",
    "VoteIntegratorConfig",
    "integrate_strategy_votes",
]


class StrategyVoteIntegratorError(ZephyrBaseError):
    """策略投票整合输入非法（Fail-Closed）。"""

    error_code = "ZA-SIG-0134"


#: 决策方向词表（A股无做空，净空方向输出 EXIT）
DIRECTION_LONG: Final = "LONG"
DIRECTION_EXIT: Final = "EXIT"
DIRECTION_NONE: Final = "NONE"


@dataclass(frozen=True)
class StrategyVoteSignal:
    """单策略投票输入（聚合三零件输出的最小契约）。

    Attributes:
        strategy_id: 策略标识（对应 MOD-SIG-131 的 signal_id）
        direction: 投票方向（1=做多 / -1=退出回避 / 0=弃权，弃权不计入分母）
        weight: IC 加权现行权重（MOD-SIG-131 current_weight，≥0）
        confidence: 置信度 ∈ [0,1]
    """

    strategy_id: str
    direction: int
    weight: float
    confidence: float = 1.0


@dataclass(frozen=True)
class VoteIntegratorConfig:
    """整合器配置（C 类参数可调）。

    Attributes:
        correlation_threshold: 两两相关 |ρ| ≥ 此值触发降权（默认 0.7）
        correlation_penalty: 降权系数（调整后权重 × 此值，默认 0.5）
        decay_half_life_days: 信号衰减半衰期（交易日，默认 20）
        min_agreement_ratio: 同向放行阈值（多数方向权重占比，默认 2/3）
        min_effective_weight: 调整后权重低于此值视为退出投票（默认 1e-6）
    """

    correlation_threshold: float = 0.7
    correlation_penalty: float = 0.5
    decay_half_life_days: float = 20.0
    min_agreement_ratio: float = 2.0 / 3.0
    min_effective_weight: float = 1e-6

    def __post_init__(self) -> None:
        if not 0.0 < self.correlation_threshold <= 1.0:
            raise StrategyVoteIntegratorError(
                f"correlation_threshold 须 ∈ (0,1]: {self.correlation_threshold}"
            )
        if not 0.0 < self.correlation_penalty < 1.0:
            raise StrategyVoteIntegratorError(f"correlation_penalty 须 ∈ (0,1): {self.correlation_penalty}")
        if not math.isfinite(self.decay_half_life_days) or self.decay_half_life_days <= 0:
            raise StrategyVoteIntegratorError(
                f"decay_half_life_days 须为正有限值: {self.decay_half_life_days}"
            )
        if not 0.5 < self.min_agreement_ratio <= 1.0:
            raise StrategyVoteIntegratorError(
                f"min_agreement_ratio 须 ∈ (0.5,1]: {self.min_agreement_ratio}"
            )
        if not 0.0 < self.min_effective_weight < 1.0:
            raise StrategyVoteIntegratorError(
                f"min_effective_weight 须 ∈ (0,1): {self.min_effective_weight}"
            )


@dataclass(frozen=True)
class ParticipantDetail:
    """参与策略明细（调整后留痕）。

    Attributes:
        strategy_id: 策略标识
        direction: 投票方向（1/-1/0）
        raw_weight: 原始 IC 权重
        adjusted_weight: 衰减+相关性惩罚后的有效权重
        decay_factor: 衰减系数（0.5^(age/half_life)）
        penalized: 是否被相关性惩罚降权
        confidence: 置信度（透传输入，供净分/置信度合成）
    """

    strategy_id: str
    direction: int
    raw_weight: float
    adjusted_weight: float
    decay_factor: float
    penalized: bool
    confidence: float


@dataclass(frozen=True)
class IntegratedDecision:
    """统一决策信号契约（整合输出）。

    Attributes:
        symbol: 标的代码
        direction: LONG / EXIT / NONE（NONE=分歧否决或无有效投票）
        strength: 信号强度 = |净加权分| ∈ [0,1]
        confidence: 决策置信度 = 同向占比 × 多数派加权平均置信度
        approved: 是否通过 ≥2/3 同向阈值
        agreement_ratio: 多数方向权重占比
        participants: 参与策略明细（含弃权者，按 strategy_id 升序）
        reason: 人类可读裁定理由
    """

    symbol: str
    direction: str
    strength: float
    confidence: float
    approved: bool
    agreement_ratio: float
    participants: tuple[ParticipantDetail, ...]
    reason: str


# ── 内部：校验 / 衰减 / 相关性惩罚 / 同向 tally ──────────────────────


def _validate_signals(symbol: str, signals: list[StrategyVoteSignal] | tuple[StrategyVoteSignal, ...]) -> None:
    """输入校验（Fail-Closed）。"""
    if not symbol or not symbol.strip():
        raise StrategyVoteIntegratorError("symbol 不可为空")
    seen: set[str] = set()
    for s in signals:
        if not s.strategy_id or not s.strategy_id.strip():
            raise StrategyVoteIntegratorError("strategy_id 不可为空")
        if s.strategy_id in seen:
            raise StrategyVoteIntegratorError(f"重复 strategy_id: {s.strategy_id}")
        seen.add(s.strategy_id)
        if s.direction not in (-1, 0, 1):
            raise StrategyVoteIntegratorError(f"direction 须 ∈ {{-1,0,1}}: {s.direction} ({s.strategy_id})")
        if not math.isfinite(s.weight) or s.weight < 0:
            raise StrategyVoteIntegratorError(f"weight 须为 ≥0 有限值: {s.weight} ({s.strategy_id})")
        if not 0.0 <= s.confidence <= 1.0:
            raise StrategyVoteIntegratorError(f"confidence 须 ∈ [0,1]: {s.confidence} ({s.strategy_id})")


def _apply_decay(
    signals: list[StrategyVoteSignal] | tuple[StrategyVoteSignal, ...],
    signal_age_days: Mapping[str, float],
    cfg: VoteIntegratorConfig,
) -> list[ParticipantDetail]:
    """衰减自适应：weight × 0.5^(age/half_life)。"""
    out: list[ParticipantDetail] = []
    for s in signals:
        age = signal_age_days.get(s.strategy_id, 0.0)
        if not math.isfinite(age) or age < 0:
            raise StrategyVoteIntegratorError(f"信号龄期须为 ≥0 有限值: {age} ({s.strategy_id})")
        decay = 0.5 ** (age / cfg.decay_half_life_days)
        out.append(
            ParticipantDetail(
                strategy_id=s.strategy_id,
                direction=s.direction,
                raw_weight=s.weight,
                adjusted_weight=s.weight * decay,
                decay_factor=decay,
                penalized=False,
                confidence=s.confidence,
            )
        )
    return out


def _apply_correlation_penalty(
    participants: list[ParticipantDetail],
    correlation_pairs: Mapping[tuple[str, str], float],
    cfg: VoteIntegratorConfig,
) -> list[ParticipantDetail]:
    """相关性惩罚：|ρ|≥阈值 的策略对，权重较小侧降权 ×penalty（每策略至多一次）。

    平局（权重相等）罚 strategy_id 字典序较大者——保证确定性。
    """
    by_id = {p.strategy_id: p for p in participants}
    penalized_ids: set[str] = set()
    normalized: list[tuple[str, str, float]] = []
    for (a, b), rho in correlation_pairs.items():
        if a == b or a not in by_id or b not in by_id:
            continue  # 自配对/未知策略忽略
        na, nb = (a, b) if a < b else (b, a)
        normalized.append((na, nb, rho))
    for a, b, rho in sorted(normalized):
        if not -1.0 <= rho <= 1.0:
            raise StrategyVoteIntegratorError(f"相关系数须 ∈ [-1,1]: {rho} ({a},{b})")
        if abs(rho) < cfg.correlation_threshold:
            continue
        pa, pb = by_id[a], by_id[b]
        weaker = a if (pa.adjusted_weight, a) <= (pb.adjusted_weight, b) else b
        if weaker in penalized_ids:
            continue
        penalized_ids.add(weaker)
        pw = by_id[weaker]
        by_id[weaker] = ParticipantDetail(
            strategy_id=pw.strategy_id,
            direction=pw.direction,
            raw_weight=pw.raw_weight,
            adjusted_weight=pw.adjusted_weight * cfg.correlation_penalty,
            decay_factor=pw.decay_factor,
            penalized=True,
            confidence=pw.confidence,
        )
    return [by_id[p.strategy_id] for p in participants]


def _tally(
    symbol: str,
    participants: list[ParticipantDetail],
    cfg: VoteIntegratorConfig,
) -> IntegratedDecision:
    """同向 tally：弃权/权重过低剔除 → 多数派占比 ≥2/3 放行。"""
    detail = tuple(sorted(participants, key=lambda p: p.strategy_id))
    effective = [
        p for p in participants if p.direction != 0 and p.adjusted_weight >= cfg.min_effective_weight
    ]
    if not effective:
        return IntegratedDecision(
            symbol=symbol,
            direction=DIRECTION_NONE,
            strength=0.0,
            confidence=0.0,
            approved=False,
            agreement_ratio=0.0,
            participants=detail,
            reason="无有效投票（全弃权或权重过低）",
        )

    total_w = sum(p.adjusted_weight for p in effective)
    long_w = sum(p.adjusted_weight for p in effective if p.direction == 1)
    exit_w = total_w - long_w
    majority_long = long_w >= exit_w
    majority_w = long_w if majority_long else exit_w
    agreement = majority_w / total_w
    net = sum(p.adjusted_weight * p.direction * p.confidence for p in effective) / total_w
    strength = min(1.0, abs(net))
    majority_conf = (
        sum(p.adjusted_weight * p.confidence for p in effective if (p.direction == 1) == majority_long)
        / majority_w
    )

    if agreement >= cfg.min_agreement_ratio:
        direction = DIRECTION_LONG if majority_long else DIRECTION_EXIT
        return IntegratedDecision(
            symbol=symbol,
            direction=direction,
            strength=strength,
            confidence=agreement * majority_conf,
            approved=True,
            agreement_ratio=agreement,
            participants=detail,
            reason=f"{direction} 通过: 同向占比 {agreement:.4f} ≥ {cfg.min_agreement_ratio:.4f}",
        )
    return IntegratedDecision(
        symbol=symbol,
        direction=DIRECTION_NONE,
        strength=strength,
        confidence=agreement * majority_conf,
        approved=False,
        agreement_ratio=agreement,
        participants=detail,
        reason=f"分歧否决: 同向占比 {agreement:.4f} < {cfg.min_agreement_ratio:.4f}",
    )


# ── 主入口 ────────────────────────────────────────────────────────────


def integrate_strategy_votes(
    symbol: str,
    signals: list[StrategyVoteSignal] | tuple[StrategyVoteSignal, ...],
    *,
    correlation_pairs: Mapping[tuple[str, str], float] | None = None,
    signal_age_days: Mapping[str, float] | None = None,
    config: VoteIntegratorConfig | None = None,
) -> IntegratedDecision:
    """多策略投票加权整合——三零件输出 → 相关性惩罚 → ≥2/3 同向 → 统一决策信号。

    调整序固定（乱序即算法断裂）：
      1. 衰减自适应（信号龄期半衰降权）
      2. 相关性惩罚（同源策略对权重较小侧降权）
      3. 同向 tally（弃权不计分母，多数派权重占比 ≥2/3 放行）

    Args:
        symbol: 标的代码
        signals: 各策略投票（weight 来自 MOD-SIG-131 现行权重）
        correlation_pairs: 策略两两相关系数 {(sid_a, sid_b): ρ}（键序无关，内部归一）
        signal_age_days: 各策略信号龄期（交易日，缺省 0=不衰减）
        config: 整合器配置（默认 VoteIntegratorConfig()）

    Returns:
        IntegratedDecision（标的/方向/强度/置信度/参与策略明细）

    Raises:
        StrategyVoteIntegratorError: 输入非法（Fail-Closed）
    """
    cfg = config or VoteIntegratorConfig()
    _validate_signals(symbol, signals)
    if not signals:
        return IntegratedDecision(
            symbol=symbol,
            direction=DIRECTION_NONE,
            strength=0.0,
            confidence=0.0,
            approved=False,
            agreement_ratio=0.0,
            participants=(),
            reason="空投票列表",
        )
    decayed = _apply_decay(signals, signal_age_days or {}, cfg)
    adjusted = _apply_correlation_penalty(decayed, correlation_pairs or {}, cfg)
    decision = _tally(symbol, adjusted, cfg)
    _log.info(
        "Strategy votes integrated: symbol=%s direction=%s approved=%s agreement=%.4f strength=%.4f",
        symbol,
        decision.direction,
        decision.approved,
        decision.agreement_ratio,
        decision.strength,
    )
    return decision
