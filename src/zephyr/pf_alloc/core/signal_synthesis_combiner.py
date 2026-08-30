# [BLUEPRINT] MOD-PA-002 | docs/03_modules/_domain_portfolio_alloc/signal_synthesis_combiner/blueprint.md
# [MODULE] zephyr.pf_alloc.core.signal_synthesis_combiner
# [DOMAIN] D_PF_ALLOC
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] MOD-PA-003(资金分配) ; D-PF-CORE(TargetPortfolio) ; D-POSITION(仓位裁决)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 合成方向由加权投票决定; 同symbol同方向去重; 反向冲突标记+裁决文本忠实于加权投票方向(#208-⑤,priority仅影响仓位合并截断); 合成置信度∈[0,1]
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidStrategySignalError;PositionCapExceededError
# [TESTS] tests/pf_alloc/test_signal_synthesis_combiner.py
# [A_module] module_id=MOD-PA-002 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""
Signal Synthesis Combiner — 信号合成器 (MOD-PA-002)

多策略信号→重合加权重→输出合成信号给 PF-CORE。

六项功能 (D-PF-ALLOC §1.1 PA-02):
    ① 多策略投票: 综合得分 = Σ(策略权重 × 方向 × 置信度 × 敏感度)
    ② 共振融合: 全部同向→强共振 / 多数同向→中等 / 分歧→弱
    ③ 决策去重: 同标的同方向多策略重复信号→合并为一条指令
    ④ 跨策略仓位合并: 同标的多策略合并→取 sum 不超上限(按策略优先级截断)
    ⑤ 信号冲突检测: 同标的反向信号→语义冲突标记+裁决说明(忠实反映加权投票实际方向, #208-⑤)
    ⑥ 信号置信度校准: 预留 calibrator 接口(Platt/Isotonic, R-96 学习系统后续接入)

设计说明:
    - 输入: 多策略产出的 StrategySignal 列表(每策略每标的一条)
    - 输出: 每标的一条 SynthesizedSignal(合成方向+综合得分+共振级别+冲突标记)
    - 属A类基础设施(投票+共振+去重+冲突检测逻辑明确), 不涉及"策略权重怎么定"(那是PA-01 B类)
    - calibrator 为可选注入, 不注入时直接用原始 confidence

依据: D:\临时工作区\依赖图\06-D-PF-ALLOC-组合分配域.md §1.1 PA-02
SSoT: depgraph MOD-PA-002
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: calibrator 参数
#   fields: 参数 calibrator（无注解）
#   code: signal_synthesis_combiner.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: position_cap 参数
#   fields: 参数 position_cap（无注解）
#   code: signal_synthesis_combiner.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① ConfidenceCalibrator
#   name_en: ConfidenceCalibrator
#   intro: 信号置信度校准器协议 (R-96 学习系统, PA-02 预留接口)。
#   desc: 信号置信度校准器协议 (R-96 学习系统, PA-02 预留接口)。 实现方: Platt Scaling / Isotonic Regression / MC Dropout…；公共方法（定义序）: calibra…
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② SignalSynthesisCombiner
#   name_en: SignalSynthesisCombiner
#   intro: 多策略信号合成器——投票+共振+去重+冲突检测+仓位合并。
#   desc: 多策略信号合成器——投票+共振+去重+冲突检测+仓位合并。 用法: combiner = SignalSynthesisCombiner() results = combiner…；公共方法（定义序）: combine…
#   inputs: calibrator position_cap
#   outputs: 返回值
#   （注：A2 之后另有 6 个公共定义未列入（含 6 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（8 定义）
#   name_en: public defs
#   intro: ConfidenceCalibrator, SignalSynthesisCombiner
#   downstream: MOD-PA-003(资金分配) ; D-PF-CORE(TargetPortfolio) ; D-POSITION(仓位裁决)
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import logging
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Protocol, runtime_checkable

from zephyr.shared.foundation.errors import ZephyrBaseError

__all__ = [
    "SignalDirection",
    "ResonanceLevel",
    "StrategySignal",
    "SynthesizedSignal",
    "ConfidenceCalibrator",
    "SignalSynthesisCombiner",
    "InvalidStrategySignalError",
    "PositionCapExceededError",
]

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# 枚举
# ──────────────────────────────────────────────────────────────────────────────


class SignalDirection(str, Enum):
    """策略信号方向。"""

    LONG = "LONG"  # 看多/买入
    SHORT = "SHORT"  # 看空/卖出
    NEUTRAL = "NEUTRAL"  # 中性/观望

    @property
    def sign(self) -> float:
        """方向数值(+1/-1/0), 用于加权投票。"""
        return {SignalDirection.LONG: 1.0, SignalDirection.SHORT: -1.0, SignalDirection.NEUTRAL: 0.0}[self]


class ResonanceLevel(str, Enum):
    """多策略共振级别 (PA-02 共振融合)。"""

    STRONG = "STRONG"  # 全部同向(最高置信度)
    MODERATE = "MODERATE"  # 多数同向(>=2/3)
    WEAK = "WEAK"  # 分歧(需因子直通裁决)


# ──────────────────────────────────────────────────────────────────────────────
# 错误
# ──────────────────────────────────────────────────────────────────────────────


class InvalidStrategySignalError(ZephyrBaseError):
    """策略信号数据非法。"""

    error_code = "ZA-PA-0001"


class PositionCapExceededError(ZephyrBaseError):
    """跨策略仓位合并超出硬上限。"""

    error_code = "ZA-PA-0002"


# ──────────────────────────────────────────────────────────────────────────────
# 数据模型
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class StrategySignal:
    """单策略对单标的的信号 (PA-02 输入)。

    Attributes:
        strategy_id: 策略ID
        symbol: 标的代码
        direction: 信号方向
        confidence: 置信度[0,1]
        weight: 策略权重(元策略分配, Σ权重=1.0)
        sensitivity: 策略对该信号的敏感度[0,1], 默认1.0
        priority: 策略优先级(数字越大优先级越高, 冲突截断时高优先级先分配), 默认0
        target_weight: 该策略建议的目标仓位权重[0,1], 默认0.0(纯信号无仓位建议)
    """

    strategy_id: str
    symbol: str
    direction: SignalDirection
    confidence: float
    weight: float = 1.0
    sensitivity: float = 1.0
    priority: int = 0
    target_weight: float = 0.0

    def __post_init__(self) -> None:
        if not self.strategy_id or not self.symbol:
            raise InvalidStrategySignalError("strategy_id and symbol must not be empty")
        if not isinstance(self.direction, SignalDirection):
            raise InvalidStrategySignalError(f"direction must be SignalDirection, got {type(self.direction)}")
        for name, val in (
            ("confidence", self.confidence),
            ("weight", self.weight),
            ("sensitivity", self.sensitivity),
            ("target_weight", self.target_weight),
        ):
            if not 0.0 <= val <= 1.0:
                raise InvalidStrategySignalError(f"{name} must be in [0,1], got {val}")


@dataclass(frozen=True)
class SynthesizedSignal:
    """合成信号 (PA-02 输出, 喂给 PA-03 资金分配 / PF-CORE)。

    Attributes:
        symbol: 标的代码
        direction: 合成方向(加权投票决定)
        composite_score: 综合得分(有符号, 正=多头倾向, 负=空头倾向)
        confidence: 合成置信度[0,1](综合得分绝对值归一化)
        resonance: 共振级别
        contributing_strategies: 贡献策略ID列表
        conflict: 是否存在反向冲突
        conflict_resolution: 冲突裁决说明(无冲突时为空)
        merged_position_weight: 合并后目标仓位权重(跨策略合并, 受 cap 截断)
    """

    symbol: str
    direction: SignalDirection
    composite_score: float
    confidence: float
    resonance: ResonanceLevel
    contributing_strategies: list[str] = field(default_factory=list)
    conflict: bool = False
    conflict_resolution: str = ""
    merged_position_weight: float = 0.0


# ──────────────────────────────────────────────────────────────────────────────
# 置信度校准器协议 (R-96 预留)
# ──────────────────────────────────────────────────────────────────────────────


@runtime_checkable
class ConfidenceCalibrator(Protocol):
    """信号置信度校准器协议 (R-96 学习系统, PA-02 预留接口)。

    实现方: Platt Scaling / Isotonic Regression / MC Dropout。
    未注入时 PA-02 直接用原始 confidence。
    """

    def calibrate(self, confidence: float, strategy_id: str, context: dict[str, Any] | None = None) -> float:
        """校准原始置信度为后验置信度。"""
        ...


# ──────────────────────────────────────────────────────────────────────────────
# 信号合成器
# ──────────────────────────────────────────────────────────────────────────────


# 共振判定阈值: 同向比例 >= 此值判为 MODERATE, =1.0 为 STRONG, 否则 WEAK
_MODERATE_THRESHOLD = 2.0 / 3.0


class SignalSynthesisCombiner:
    """多策略信号合成器——投票+共振+去重+冲突检测+仓位合并。

    用法:
        combiner = SignalSynthesisCombiner()
        results = combiner.combine([
            StrategySignal("strat_a", "000001.SZ", SignalDirection.LONG, 0.8, weight=0.5, priority=2),
            StrategySignal("strat_b", "000001.SZ", SignalDirection.LONG, 0.6, weight=0.5, priority=1),
            StrategySignal("strat_a", "600000.SH", SignalDirection.SHORT, 0.7, weight=0.5),
        ])

    Args:
        calibrator: 可选置信度校准器(R-96), 不注入则用原始 confidence
        position_cap: 跨策略仓位合并硬上限(单标的总仓位权重上限), 默认 1.0=不限制
    """

    def __init__(
        self,
        calibrator: ConfidenceCalibrator | None = None,
        position_cap: float = 1.0,
    ) -> None:
        self._calibrator = calibrator
        if not 0.0 < position_cap <= 1.0:
            raise InvalidStrategySignalError(f"position_cap must be in (0,1], got {position_cap}")
        self._position_cap = position_cap

    def combine(self, signals: list[StrategySignal]) -> list[SynthesizedSignal]:
        """合成多策略信号。

        步骤: 按标的分组 → 每标的投票+共振+去重+冲突检测+仓位合并 → 返回合成信号列表。
        """
        grouped: dict[str, list[StrategySignal]] = defaultdict(list)
        for sig in signals:
            grouped[sig.symbol].append(sig)
        results: list[SynthesizedSignal] = []
        for symbol, sigs in grouped.items():
            results.append(self._synthesize_one(symbol, sigs))
        return results

    # ── 单标的合成 ──

    def _synthesize_one(self, symbol: str, sigs: list[StrategySignal]) -> SynthesizedSignal:
        # ① 多策略投票: 综合得分 = Σ(weight × direction.sign × calibrated_confidence × sensitivity)
        composite_score = 0.0
        contributing: list[str] = []
        for sig in sigs:
            conf = self._calibrate(sig)
            composite_score += sig.weight * sig.direction.sign * conf * sig.sensitivity
            contributing.append(sig.strategy_id)

        # ② 共振融合
        long_count = sum(1 for s in sigs if s.direction == SignalDirection.LONG)
        short_count = sum(1 for s in sigs if s.direction == SignalDirection.SHORT)
        directional = long_count + short_count
        resonance = self._resonance(long_count, short_count, directional)

        # 合成方向: 由综合得分符号决定
        direction = self._direction_from_score(composite_score)

        # ⑤ 信号冲突检测 + 裁决说明
        # AI-NIGHT-001 #208-⑤：文本须忠实反映实际合成方向——原实现按 priority 报
        # 胜者，与 composite_score 符号决定的方向可矛盾（priority 仅影响仓位合并
        # 截断顺序，不裁决方向）。direction 须先于文本生成。
        conflict = long_count > 0 and short_count > 0
        conflict_resolution = ""
        if conflict:
            conflict_resolution = self._resolve_conflict(long_count, short_count, direction, composite_score)

        # 合成置信度: 综合得分绝对值归一化到 [0,1] (得分上限=Σweight×1×1×1=Σweight)
        max_score = sum(s.weight for s in sigs) or 1.0
        confidence = min(abs(composite_score) / max_score, 1.0)

        # ③④ 跨策略仓位合并: 同方向 target_weight 取 sum, 受 cap 截断(高优先级优先)
        merged_weight = self._merge_positions(sigs, direction, conflict)

        return SynthesizedSignal(
            symbol=symbol,
            direction=direction,
            composite_score=composite_score,
            confidence=confidence,
            resonance=resonance,
            contributing_strategies=contributing,
            conflict=conflict,
            conflict_resolution=conflict_resolution,
            merged_position_weight=merged_weight,
        )

    def _calibrate(self, sig: StrategySignal) -> float:
        """应用校准器(若注入)。"""
        if self._calibrator is None:
            return sig.confidence
        return self._calibrator.calibrate(sig.confidence, sig.strategy_id)

    @staticmethod
    def _resonance(long_count: int, short_count: int, directional: int) -> ResonanceLevel:
        """共振级别: 全部同向→STRONG / >=2/3同向→MODERATE / 否则WEAK。"""
        if directional == 0:
            return ResonanceLevel.WEAK
        dominant = max(long_count, short_count)
        ratio = dominant / directional
        if ratio >= 1.0:
            return ResonanceLevel.STRONG
        if ratio >= _MODERATE_THRESHOLD:
            return ResonanceLevel.MODERATE
        return ResonanceLevel.WEAK

    @staticmethod
    def _direction_from_score(score: float) -> SignalDirection:
        """综合得分符号→方向(0 视为 NEUTRAL)。"""
        if score > 0:
            return SignalDirection.LONG
        if score < 0:
            return SignalDirection.SHORT
        return SignalDirection.NEUTRAL

    def _merge_positions(self, sigs: list[StrategySignal], direction: SignalDirection, conflict: bool) -> float:
        """跨策略仓位合并: 同方向 target_weight 取 sum, 超 cap 按优先级截断。

        冲突时只合并胜出方向的仓位。
        """
        # 冲突时只取与合成方向一致的同向信号
        relevant = [s for s in sigs if s.direction == direction] if conflict else sigs
        # 按优先级降序(高优先级先分配), 超 cap 部分截断
        ordered = sorted(relevant, key=lambda s: s.priority, reverse=True)
        total = 0.0
        for s in ordered:
            total = min(total + s.target_weight, self._position_cap)
            if total >= self._position_cap:
                logger.info(
                    "Position cap %.2f reached for %s, truncating at strategy %s",
                    self._position_cap,
                    s.symbol,
                    s.strategy_id,
                )
                break
        return total

    @staticmethod
    def _resolve_conflict(
        long_count: int,
        short_count: int,
        direction: SignalDirection,
        composite_score: float,
    ) -> str:
        """冲突裁决说明: 忠实报告加权投票（composite_score 符号）裁决出的实际方向。

        AI-NIGHT-001 #208-⑤：原实现按策略 priority 报"胜者"，与加权得分决定的
        实际合成方向可矛盾（实证 LONG conf0.9/pri1 vs SHORT conf0.5/pri3 →
        文本"priority->SHORT"但实际 direction=LONG）。priority 仅影响仓位合并
        截断顺序（_merge_positions），不参与方向裁决。
        """
        return (
            f"conflict({long_count}L vs {short_count}S) resolved by weighted_vote"
            f"->{direction.value}(score={composite_score:+.4f})"
        )
