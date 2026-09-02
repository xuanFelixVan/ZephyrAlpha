# [BLUEPRINT] MOD-SIG-088 | docs/03_modules/_domain_signal/capital_behavior_orchestrator/blueprint.md
# [MODULE] zephyr.signal_ashare.capital_behavior_orchestrator
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] zephyr.signal_ashare.institutional_behavior_analyzer（MOD-SIG-021 BehaviorPhase 枚举复用，prod）
# [CONSUMERS] （候选：C-014 大盘预测后续波次、盘前计划编排）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 七类主力封闭集；六阶段推演不可跳跃（沿 MOD-SIG-021 主链）；校准偏置限幅±0.5 且仅经 review 调整；frozen dataclass asdict JSON 可序列化；纯内存不直连 DB
# [MODIFY-GUARD] AUD-DRAFT-001 深挖批 B1-00152 行 + 候选注册表 CAND-TESTB-003
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 空 symbol/观测占比或置信度越界 → ValueError（fail-closed）；空观测 → NEUTRAL 合力（非异常）
# [TESTS] tests/signal_ashare/test_capital_behavior_orchestrator.py
# [A_module] module_id=MOD-SIG-088 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""C-011 资金行为分析（MOD-SIG-088，B1-00152）。

主力行为分析单点已在（MOD-SIG-021 六阶段识别），七类画像+动态推演+自迭代修正
未成体系（深挖裁定理由）。本模块收口四件事：

1. **七类主力画像**：北向/公募/私募/游资/量化/散户/产业资本（封闭枚举），
   观测（净流入/参与占比/置信度）→ 画像（方向+强度+类偏置）。
2. **六阶段推演状态机**：复用 MOD-SIG-021 BehaviorPhase 主链，按合力方向推演
   下一阶段（做多沿链进一步、末端保持；做空自拉升向出货；NEUTRAL 保持；
   UNKNOWN+做多→建仓）——推演不跳跃。
3. **预测-复盘自迭代修正**：review(预测合力, 实际方向) → 预测错时对每类主力
   偏置做 EMA 修正（alpha 可配，限幅 ±0.5），后续 analyze 打分自动带偏置；
   预测命中不调整（无负激励扭曲）。
4. **合力方向输出**：CapitalConsensus（方向/强度/画像明细/当前+推演阶段），
   供 C-014 大盘预测（后续波次）消费。

合力强度口径（文档化 MVP 初拍值，待标定批替换）：
    strength = Σ(sign(net)×|net|×conf×(1+bias)) / Σ(|net|×conf)
    方向 = strength≥long_threshold→LONG / ≤short_threshold→SHORT / 其间 NEUTRAL

不做什么：不重写六阶段识别算法（MOD-SIG-021 职责）、不直连资金流/龙虎榜数据源
（观测由上游注入）、不荐股。

依据: AUD-DRAFT-001 深挖批 B1-00152（裁定=做 P1）；蓝图 §0 边界
SSoT: depgraph blueprint_id=MOD-SIG-088
Version: 0.1.0

# [ALGO_FLOW]
# 输入: symbol + list[CapitalObservation]（类/净流入/占比/置信度）+ 当前 BehaviorPhase
# 特征: 各类带符号加权净流入 + 类校准偏置
# 算法: 画像打分 → 合力聚合 → 六阶段推演 → （复盘）EMA 偏置修正
# 输出: CapitalConsensus（direction/strength/profiles/phase/expected_next_phase/notes）
"""

from __future__ import annotations

import logging
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Final

from zephyr.signal_ashare.institutional_behavior_analyzer import BehaviorPhase

logger = logging.getLogger(__name__)

__all__: Final = [
    "CalibrationReport",
    "CapitalBehaviorConfig",
    "CapitalBehaviorOrchestrator",
    "CapitalClass",
    "CapitalConsensus",
    "CapitalObservation",
    "CapitalProfile",
    "ForceDirection",
]

#: 校准偏置限幅（±0.5 = 类打分最多放大/缩小 50%）
_BIAS_LIMIT: Final = 0.5


class CapitalClass(str, Enum):
    """七类主力画像（封闭集）。"""

    NORTHBOUND = "北向"
    PUBLIC_FUND = "公募"
    PRIVATE_FUND = "私募"
    HOT_MONEY = "游资"
    QUANT = "量化"
    RETAIL = "散户"
    INDUSTRIAL = "产业资本"


class ForceDirection(str, Enum):
    """合力方向（封闭集）。"""

    LONG = "做多"
    SHORT = "做空"
    NEUTRAL = "中性"


#: 六阶段主链（对齐 MOD-SIG-021 不可跳跃序）
_PHASE_CHAIN: Final = (
    BehaviorPhase.BUILDING,
    BehaviorPhase.WASHING,
    BehaviorPhase.TESTING,
    BehaviorPhase.RE_WASHING,
    BehaviorPhase.PULLING,
    BehaviorPhase.DISTRIBUTING,
)


@dataclass(frozen=True, slots=True)
class CapitalObservation:
    """单类主力观测（上游资金流/龙虎榜件注入）。"""

    capital_class: CapitalClass
    net_inflow: float  # 净流入（正=买入，口径随上游，仅相对比较）
    participation: float  # 成交占比 0~1
    confidence: float = 1.0  # 观测置信度 0~1

    def __post_init__(self) -> None:
        if not isinstance(self.capital_class, CapitalClass):
            raise ValueError(f"capital_class 非法: {self.capital_class}")
        if not 0.0 <= self.participation <= 1.0:
            raise ValueError(f"participation 须∈[0,1]: {self.participation}")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"confidence 须∈[0,1]: {self.confidence}")


@dataclass(frozen=True, slots=True)
class CapitalBehaviorConfig:
    """资金行为分析配置（MVP 初拍值，全可配）。"""

    long_threshold: float = 0.15  # 合力强度≥此值→做多
    short_threshold: float = -0.15  # 合力强度≤此值→做空
    calibration_alpha: float = 0.3  # 复盘偏置 EMA 修正率

    def __post_init__(self) -> None:
        if not -1.0 <= self.short_threshold < self.long_threshold <= 1.0:
            raise ValueError(f"阈值非法: short={self.short_threshold} long={self.long_threshold}")
        if not 0.0 < self.calibration_alpha <= 1.0:
            raise ValueError(f"calibration_alpha 须∈(0,1]: {self.calibration_alpha}")


@dataclass(frozen=True, slots=True)
class CapitalProfile:
    """单类主力画像。"""

    capital_class: CapitalClass
    direction: ForceDirection
    strength: float  # 0~1（类内归一：|net|/Σ|net|）
    net_inflow: float
    calibrated_bias: float  # 复盘累积偏置（±0.5）

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["capital_class"] = self.capital_class.value
        d["direction"] = self.direction.value
        return d


@dataclass(frozen=True, slots=True)
class CapitalConsensus:
    """资金合力输出（C-014 候选消费契约）。"""

    symbol: str
    direction: ForceDirection
    strength: float  # -1~1 带符号合力强度
    phase: BehaviorPhase
    expected_next_phase: BehaviorPhase
    profiles: tuple[CapitalProfile, ...] = ()
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["direction"] = self.direction.value
        d["phase"] = self.phase.value
        d["expected_next_phase"] = self.expected_next_phase.value
        return d


@dataclass(frozen=True, slots=True)
class CalibrationReport:
    """预测-复盘校准报告。"""

    symbol: str
    predicted: ForceDirection
    actual: ForceDirection
    hit: bool
    adjusted: tuple[CapitalClass, ...] = ()  # 本次被调整偏置的类

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["predicted"] = self.predicted.value
        d["actual"] = self.actual.value
        d["adjusted"] = tuple(c.value for c in self.adjusted)
        return d


def _infer_next_phase(current: BehaviorPhase, direction: ForceDirection) -> BehaviorPhase:
    """六阶段推演（不可跳跃）：做多沿链进一步/末端保持；做空自拉升向出货；其余保持。"""
    if current is BehaviorPhase.UNKNOWN:
        return BehaviorPhase.BUILDING if direction is ForceDirection.LONG else current
    if direction is ForceDirection.LONG:
        idx = _PHASE_CHAIN.index(current)
        return _PHASE_CHAIN[min(idx + 1, len(_PHASE_CHAIN) - 1)]
    if direction is ForceDirection.SHORT and current is BehaviorPhase.PULLING:
        return BehaviorPhase.DISTRIBUTING
    return current


class CapitalBehaviorOrchestrator:
    """C-011 资金行为分析收口：画像→合力→推演→自迭代校准。"""

    def __init__(self, config: CapitalBehaviorConfig | None = None) -> None:
        self._cfg = config or CapitalBehaviorConfig()
        self._bias: dict[CapitalClass, float] = {c: 0.0 for c in CapitalClass}

    def analyze(
        self,
        symbol: str,
        observations: list[CapitalObservation] | tuple[CapitalObservation, ...],
        *,
        phase: BehaviorPhase = BehaviorPhase.UNKNOWN,
    ) -> CapitalConsensus:
        """观测→画像→合力方向+六阶段推演。"""
        if not symbol:
            raise ValueError("symbol 不能为空")
        cfg = self._cfg
        total_weight = sum(abs(o.net_inflow) * o.confidence for o in observations)

        profiles: list[CapitalProfile] = []
        signed_sum = 0.0
        for o in observations:
            bias = self._bias[o.capital_class]
            adj = o.net_inflow * o.confidence * (1.0 + bias)
            signed_sum += adj
            cls_dir = ForceDirection.LONG if adj > 0 else ForceDirection.SHORT if adj < 0 else ForceDirection.NEUTRAL
            cls_strength = abs(o.net_inflow) * o.confidence / total_weight if total_weight > 0 else 0.0
            profiles.append(
                CapitalProfile(
                    capital_class=o.capital_class,
                    direction=cls_dir,
                    strength=cls_strength,
                    net_inflow=o.net_inflow,
                    calibrated_bias=bias,
                )
            )

        strength = signed_sum / total_weight if total_weight > 0 else 0.0
        if strength >= cfg.long_threshold:
            direction = ForceDirection.LONG
        elif strength <= cfg.short_threshold:
            direction = ForceDirection.SHORT
        else:
            direction = ForceDirection.NEUTRAL

        expected = _infer_next_phase(phase, direction)
        notes: tuple[str, ...] = ()
        if not observations:
            notes = ("空观测，合力按 NEUTRAL 输出",)
        return CapitalConsensus(
            symbol=symbol,
            direction=direction,
            strength=strength,
            phase=phase,
            expected_next_phase=expected,
            profiles=tuple(profiles),
            notes=notes,
        )

    def review(
        self,
        consensus: CapitalConsensus,
        actual_direction: ForceDirection,
    ) -> CalibrationReport:
        """预测-复盘自迭代：预测错→参与类偏置 EMA 修正（限幅±0.5）。"""
        if not isinstance(actual_direction, ForceDirection):
            raise ValueError(f"actual_direction 非法: {actual_direction}")
        hit = consensus.direction is actual_direction
        adjusted: list[CapitalClass] = []
        if not hit and consensus.direction is not ForceDirection.NEUTRAL:
            alpha = self._cfg.calibration_alpha
            for p in consensus.profiles:
                if p.direction is ForceDirection.NEUTRAL:
                    continue
                # 类方向与实际方向的符号误差：同向不罚、反向罚
                err = 0.0 if p.direction is actual_direction else -alpha * p.strength
                if err == 0.0:
                    continue
                new_bias = max(-_BIAS_LIMIT, min(_BIAS_LIMIT, self._bias[p.capital_class] + err))
                if new_bias != self._bias[p.capital_class]:
                    self._bias[p.capital_class] = new_bias
                    adjusted.append(p.capital_class)
        logger.info(
            "资金行为复盘: %s 预测=%s 实际=%s 命中=%s 调整=%s",
            consensus.symbol,
            consensus.direction.value,
            actual_direction.value,
            hit,
            [c.value for c in adjusted],
        )
        return CalibrationReport(
            symbol=consensus.symbol,
            predicted=consensus.direction,
            actual=actual_direction,
            hit=hit,
            adjusted=tuple(adjusted),
        )
