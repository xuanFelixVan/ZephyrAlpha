# [BLUEPRINT] MOD-SELL-009 | docs/03_modules/_domain_sell_decision/sell_urgency_scorer/blueprint.md
# [MODULE] zephyr.sell_decision.core.sell_urgency_scorer
# [DOMAIN] D_SELL_DECISION
# [DEPENDENCIES] zephyr.shared.foundation.errors ; zephyr.sell_decision.core.sell_signal_collector ; zephyr.sell_decision.core.sell_conflict_arbitrator
# [CONSUMERS] D-EX-CORE(执行策略) ; MOD-SELL-007(融合引擎,后建) ; D-POSITION
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 最紧急决定原则(多信号取最大); 紧迫度∈[0,1]; 风控→1.0; 强冲突增强≥0.9; 执行策略三档匹配
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidUrgencyInputError
# [TESTS] tests/sell_decision/test_sell_urgency_scorer.py
# [A_module] module_id=MOD-SELL-009 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


Sell Urgency Scorer — 卖出紧迫度评分器 (MOD-SELL-009)

基于卖出信号来源类型映射紧迫度(0~1), 匹配执行策略, 消费 SELL-08 仲裁结果做冲突增强。

紧迫度分级 (D-SELL-DECISION §1.4 SELL-09):
    - 紧急(URGENT, 1.0): 风控触发/主力弃庄/第K次挑战失败K≥3 → 市价单快速执行
    - 中等(MODERATE, 0.6): 技术面/相对强弱/量价背离/基本面 → 限价单+时间限制
    - 从容(RELAXED, 0.3): 止盈/置换/时间止损 → 限价单+耐心等待

执行策略:
    - urgency > 0.8  → MARKET_FAST (市价单快速执行)
    - 0.5 < urgency ≤ 0.8 → LIMITED_TIME (限价单+时间限制)
    - urgency ≤ 0.5 → PATIENT_LIMIT (限价单+耐心等待)

设计说明:
    - 消费 SELL-01 的 SellSignal(含 signal_type) → 映射紧迫度
    - 消费 SELL-08 的 ArbitrationResult → 强冲突(STRONG)增强紧迫度至≥0.9
    - 多信号取最大紧迫度(最紧急决定原则)
    - 属A类基础设施(类型→紧迫度映射+策略匹配, 逻辑明确)

依据: D:\临时工作区\依赖图-D-SELL-DECISION-卖出决策域.md §1.4 SELL-09
SSoT: depgraph MOD-SELL-009
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 卖出信号列表 SellSignal
#   fields: symbol + signal_type(8类) + source + metadata(risk_force)
#   code: sell_signals: list[SellSignal] 来自 MOD-SELL-001
# - id: I2
#   name: 仲裁结果列表 ArbitrationResult
#   fields: symbol + conflict_level(STRONG等)
#   code: arbitration_results 来自 MOD-SELL-008 可选
# - id: I3
#   name: 评分时间 clock 时间源
#   fields: now 或注入 clock 可测试替换
#   code: now / clock 参数
# 层: 算法
# - id: A1
#   name_zh: ① 按标的分组与仲裁索引
#   name_en: SellUrgencyScorer.score
#   intro: 把信号按股票分组，仲裁结果也按股票建好索引，逐标的评分且单标的异常隔离
#   desc: defaultdict按symbol分组信号 + arb_by_symbol索引仲裁结果 + 逐标的_score_one 异常仅记日志
#   inputs: I1 I2 I3
#   outputs: 每标的一条SellUrgencyScore(按symbol排序)
# - id: A2
#   name_zh: ② 单信号紧迫度映射
#   name_en: _signal_urgency / _is_risk_forced
#   intro: 风控来源的信号直接给1.0，其他按8类信号类型查表映射紧迫度
#   desc: source含RISK或metadata.risk_force→1.0; 否则_urgency_map[signal_type](主力弃庄/挑战失败1.0 技术基本面0.6 止盈时间止损0.3) 未知默认0.5
#   inputs: I1
#   outputs: 单信号urgency ∈[0,1]
#   invariant: 风控→1.0
# - id: A3
#   name_zh: ③ 最紧急决定与强冲突增强
#   name_en: _score_one
#   intro: 同标的多个信号取最大紧迫度，遇到SELL-08强冲突仲裁就抬到0.9以上
#   desc: max(各信号urgency)取主导信号; 仲裁conflict_level=STRONG且urgency<0.9 → 提升至0.9 conflict_enhanced=True
#   inputs: A1 A2
#   outputs: 标的最终urgency + 主导信号类型
#   invariant: 最紧急决定原则(多信号取最大); 强冲突增强≥0.9
# - id: A4
#   name_zh: ④ 紧迫度等级与执行策略匹配
#   name_en: _urgency_to_level / _urgency_to_strategy
#   intro: 把紧迫度数值翻译成三档等级和三档执行策略
#   desc: urgency≥0.8→URGENT ≥0.5→MODERATE 否则RELAXED; >0.8→MARKET_FAST市价 >0.5→LIMITED_TIME限价限时 否则PATIENT_LIMIT耐心等待
#   inputs: A3
#   outputs: UrgencyLevel + ExecutionStrategy
#   invariant: 紧迫度∈[0,1]; 执行策略三档匹配
# 层: 输出
# - id: O1
#   name_zh: 卖出紧迫度评分 SellUrgencyScore 列表
#   name_en: list[SellUrgencyScore]
#   intro: 每标的含urgency/level/strategy/主导信号/冲突增强标记/理由，喂给执行域定下单方式
#   invariant: urgency∈[0,1]
#   downstream: D-EX-CORE(执行策略) ; MOD-SELL-007(融合引擎,后建) ; D-POSITION
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I1 --> A2
# A1 --> A3
# A2 --> A3
# A3 --> A4
# A4 --> O1
"""

from __future__ import annotations

import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Callable

from zephyr.sell_decision.core.sell_conflict_arbitrator import ArbitrationResult, ConflictLevel
from zephyr.sell_decision.core.sell_signal_collector import SellSignal, SellSignalType
from zephyr.shared.foundation.errors import ZephyrBaseError

__all__ = [
    "UrgencyLevel",
    "ExecutionStrategy",
    "SellUrgencyScore",
    "SellUrgencyScorer",
    "InvalidUrgencyInputError",
]

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# 枚举
# ──────────────────────────────────────────────────────────────────────────────


class UrgencyLevel(str, Enum):
    """紧迫度等级 (D-SELL §1.4 SELL-09)。"""

    URGENT = "URGENT"  # 紧急清仓(1.0)
    MODERATE = "MODERATE"  # 中等(0.6)
    RELAXED = "RELAXED"  # 从容(0.3)


class ExecutionStrategy(str, Enum):
    """执行策略 (紧迫度→执行方式匹配)。"""

    MARKET_FAST = "MARKET_FAST"  # 市价单快速执行(urgency>0.8)
    LIMITED_TIME = "LIMITED_TIME"  # 限价单+时间限制(0.5<urgency≤0.8)
    PATIENT_LIMIT = "PATIENT_LIMIT"  # 限价单+耐心等待(urgency≤0.5)


# ──────────────────────────────────────────────────────────────────────────────
# 错误
# ──────────────────────────────────────────────────────────────────────────────


class InvalidUrgencyInputError(ZephyrBaseError):
    """紧迫度评分输入数据非法(如空信号列表)。"""

    error_code = "ZA-SELL-0009"


# ──────────────────────────────────────────────────────────────────────────────
# 数据模型
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class SellUrgencyScore:
    """卖出紧迫度评分 (SELL-009 产出, 喂给 D-EX-CORE / D-POSITION)。

    Attributes:
        symbol: 标的代码
        urgency: 紧迫度[0,1], 0=最从容, 1=最紧急
        level: 紧迫度等级(URGENT/MODERATE/RELAXED)
        strategy: 执行策略(MARKET_FAST/LIMITED_TIME/PATIENT_LIMIT)
        dominant_signal_type: 主导信号类型(最紧急的信号)
        contributing_count: 贡献信号数
        conflict_enhanced: 是否经 SELL-08 仲裁冲突增强
        reason: 人类可读评分理由
        timestamp: 评分时间
    """

    symbol: str
    urgency: float
    level: UrgencyLevel
    strategy: ExecutionStrategy
    dominant_signal_type: SellSignalType
    contributing_count: int
    conflict_enhanced: bool = False
    reason: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


# ──────────────────────────────────────────────────────────────────────────────
# 紧迫度评分器
# ──────────────────────────────────────────────────────────────────────────────


# 默认 signal_type → 紧迫度映射 (D-SELL §1.4 SELL-09)
_DEFAULT_URGENCY_MAP: dict[SellSignalType, float] = {
    SellSignalType.MAIN_FORCE_DISTRIBUTION: 1.0,  # 主力弃庄→紧急
    SellSignalType.BREAKOUT_FAILURE: 1.0,  # 第K次挑战失败→强制清仓
    SellSignalType.FUNDAMENTAL: 0.6,  # 基本面恶化→中等
    SellSignalType.TECHNICAL: 0.6,  # 技术面→中等
    SellSignalType.VOLUME_PRICE_DIVERGENCE: 0.6,  # 量价背离→中等
    SellSignalType.RELATIVE_STRENGTH: 0.6,  # 相对强弱→中等
    SellSignalType.OPPORTUNITY_COST: 0.3,  # 止盈/置换→从容
    SellSignalType.TIME_STOP: 0.3,  # 时间止损→从容
}

# 风控来源标识
_DEFAULT_RISK_MARKER = "RISK"

# 强冲突增强阈值(STRONG 仲裁结果 → urgency 至少此值)
_CONFLICT_ENHANCE_FLOOR = 0.9

# 执行策略阈值
_MARKET_THRESHOLD = 0.8  # > 此值 → MARKET_FAST
_LIMITED_THRESHOLD = 0.5  # > 此值 → LIMITED_TIME, 否则 PATIENT_LIMIT


class SellUrgencyScorer:
    """卖出紧迫度评分器——信号类型→紧迫度+执行策略+冲突增强。

    用法:
        scorer = SellUrgencyScorer()
        scores = scorer.score(
            sell_signals=[SellSignal("000001.SZ", SellSignalType.MAIN_FORCE_DISTRIBUTION, ...)],
            arbitration_results=arb_results,  # 来自 SELL-08, 可选
        )
        for s in scores:
            if s.strategy is ExecutionStrategy.MARKET_FAST:
                # 市价单快速执行

    Args:
        urgency_map: signal_type → 紧迫度映射(默认8类设计值)
        risk_source_marker: 风控来源标识(source 含此子串 → 紧迫度1.0)
        conflict_enhance_floor: 强冲突增强下限(默认0.9)
        clock: 可选时间源(测试注入)
    """

    def __init__(
        self,
        urgency_map: dict[SellSignalType, float] | None = None,
        risk_source_marker: str = _DEFAULT_RISK_MARKER,
        conflict_enhance_floor: float = _CONFLICT_ENHANCE_FLOOR,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._urgency_map = dict(urgency_map) if urgency_map is not None else dict(_DEFAULT_URGENCY_MAP)
        self._risk_marker = risk_source_marker.upper()
        self._enhance_floor = conflict_enhance_floor
        self._clock = clock or (lambda: datetime.now(timezone.utc))

    # ── 评分主入口 ──

    def score(
        self,
        sell_signals: list[SellSignal],
        arbitration_results: list[ArbitrationResult] | None = None,
        now: datetime | None = None,
    ) -> list[SellUrgencyScore]:
        """对卖出信号评分紧迫度+匹配执行策略。

        步骤: 按标的分组 → 每标的取最大紧迫度信号 → 冲突增强 → 匹配策略。

        Args:
            sell_signals: 卖出信号列表(来自 SELL-01)
            arbitration_results: SELL-08 仲裁结果(可选, 用于冲突增强)
            now: 评分时间(默认 clock())

        Returns:
            每个有卖出信号的标的一条 SellUrgencyScore(按 symbol 排序)
        """
        if not sell_signals:
            raise InvalidUrgencyInputError("sell_signals must not be empty")
        now = now or self._clock()

        # 按标的分组
        by_symbol: dict[str, list[SellSignal]] = defaultdict(list)
        for sig in sell_signals:
            by_symbol[sig.symbol].append(sig)

        # 仲裁结果按标的索引(用于冲突增强)
        arb_by_symbol: dict[str, ArbitrationResult] = {}
        if arbitration_results:
            for r in arbitration_results:
                arb_by_symbol[r.symbol] = r

        results: list[SellUrgencyScore] = []
        for symbol in sorted(by_symbol.keys()):
            try:
                score = self._score_one(
                    symbol,
                    by_symbol[symbol],
                    arb_by_symbol.get(symbol),
                    now,
                )
                results.append(score)
            except Exception as exc:  # noqa: BLE001 — 单标的异常隔离
                logger.error("Urgency scoring failed for %s: %s", symbol, exc, exc_info=True)
        return results

    # ── 单标的评分 ──

    def _score_one(
        self,
        symbol: str,
        sigs: list[SellSignal],
        arb: ArbitrationResult | None,
        now: datetime,
    ) -> SellUrgencyScore:
        # 每信号算紧迫度, 取最大(最紧急决定)
        scored = [(sig, self._signal_urgency(sig)) for sig in sigs]
        dominant_sig, base_urgency = max(scored, key=lambda x: x[1])

        # 冲突增强: 强冲突 → urgency 提升至下限
        conflict_enhanced = False
        if arb is not None and arb.conflict_level is ConflictLevel.STRONG:
            if base_urgency < self._enhance_floor:
                base_urgency = self._enhance_floor
                conflict_enhanced = True

        level = self._urgency_to_level(base_urgency)
        strategy = self._urgency_to_strategy(base_urgency)

        reason_parts = [
            f"{dominant_sig.signal_type.value}→urgency {base_urgency:.2f}",
        ]
        if conflict_enhanced:
            reason_parts.append(f"conflict-enhanced to {self._enhance_floor:.2f} (STRONG)")
        reason_parts.append(f"strategy={strategy.value}")

        return SellUrgencyScore(
            symbol=symbol,
            urgency=base_urgency,
            level=level,
            strategy=strategy,
            dominant_signal_type=dominant_sig.signal_type,
            contributing_count=len(sigs),
            conflict_enhanced=conflict_enhanced,
            reason="; ".join(reason_parts),
            timestamp=now,
        )

    # ── 单信号紧迫度 ──

    def _signal_urgency(self, sig: SellSignal) -> float:
        """单信号紧迫度: 风控→1.0, 否则按 signal_type 映射。"""
        if self._is_risk_forced(sig):
            return 1.0
        return self._urgency_map.get(sig.signal_type, 0.5)  # 未知类型默认中等

    def _is_risk_forced(self, sig: SellSignal) -> bool:
        """风控强制卖出判定: source 含风险标识 或 metadata 标记 risk_force。"""
        if sig.source and self._risk_marker in sig.source.upper():
            return True
        return bool(sig.metadata.get("risk_force", False))

    # ── 等级/策略映射 ──

    @staticmethod
    def _urgency_to_level(urgency: float) -> UrgencyLevel:
        if urgency >= 0.8:
            return UrgencyLevel.URGENT
        if urgency >= 0.5:
            return UrgencyLevel.MODERATE
        return UrgencyLevel.RELAXED

    @staticmethod
    def _urgency_to_strategy(urgency: float) -> ExecutionStrategy:
        if urgency > _MARKET_THRESHOLD:
            return ExecutionStrategy.MARKET_FAST
        if urgency > _LIMITED_THRESHOLD:
            return ExecutionStrategy.LIMITED_TIME
        return ExecutionStrategy.PATIENT_LIMIT
