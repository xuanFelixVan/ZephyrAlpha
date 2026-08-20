# [BLUEPRINT] MOD-SELL-006 | docs/03_modules/_domain_sell_decision/replacement_rebalance_seller/blueprint.md
# [MODULE] zephyr.sell_decision.core.replacement_rebalance_seller
# [DOMAIN] D_SELL_DECISION
# [DEPENDENCIES] zephyr.shared.foundation.errors ; zephyr.sell_decision.core.sell_signal_collector
# [CONSUMERS] MOD-SELL-001(收集器第⑥类信号源) ; MOD-SELL-007(融合引擎)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 再平衡=权重偏离>阈值→被动卖出超配; 置换=候选池有更优标的→卖A买B; confidence∈[0,1]
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidRebalanceInputError
# [TESTS] tests/sell_decision/test_replacement_rebalance_seller.py
# [A_module] module_id=MOD-SELL-006 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


Replacement & Rebalance Seller — 置换与再平衡卖出 (MOD-SELL-006)

两种被动卖出驱动:
    ① 机会成本驱动(置换): 候选池有更优标的 → 卖A买B(REPLACE)
    ② 组合再平衡驱动: 权重偏离 > 阈值 → 被动卖出超配标的(REDUCE)

设计说明:
    - A类基础设施: 纯比较逻辑, 不涉及"候选池怎么排序"(D-FACTOR/D-SELECT 职责)
    - 输入契约: 当前权重 + 目标权重(再平衡) / 当前持仓评分 + 候选池评分(置换)
    - 再平衡阈值: 默认权重偏离 > 5% 触发(可配置)
    - 置换阈值: 默认候选评分高出当前 > 20% 触发(可配置)
    - 输出 ReplacementRebalanceOrder 喂给 SELL-001 收集器第⑥类信号源

依据: D:\临时工作区\依赖图-D-SELL-DECISION-卖出决策域.md §1.2 SELL-06
SSoT: depgraph MOD-SELL-006
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 再平衡评估输入 标量参数
#   fields: symbol标的代码 + current_weight当前权重[0,1] + target_weight目标权重[0,1]
#   code: evaluate_rebalance() L192-196
# - id: I2
#   name: 置换评估输入 标量参数
#   fields: symbol当前持仓(卖A) + current_score当前评分[0,1] + replace_with候选标的(买B) + candidate_score候选评分[0,1]
#   code: evaluate_replacement() L250-255
# - id: I3
#   name: 阈值配置 标量
#   fields: rebalance_threshold权重偏离阈值0.05 + replacement_score_threshold评分差阈值0.20
#   code: __init__ L171-174
# 层: 算法
# - id: A1
#   name_zh: ① 再平衡卖出评估
#   name_en: evaluate_rebalance
#   intro: 当前权重比目标权重超配超过5%就被动减仓
#   desc: drift=current-target; drift>0.05才触发否则None; confidence=min(0.5+drift, 0.9)偏离越大越高; 低配不触发(买入非本模块职责)
#   inputs: I1 I3
#   outputs: REBALANCE/REDUCE卖出指令或None
#   invariant: 再平衡=权重偏离>阈值→被动卖出超配
# - id: A2
#   name_zh: ② 置换卖出评估
#   name_en: evaluate_replacement
#   intro: 候选池里评分高出当前持仓20%就卖A买B
#   desc: score_diff=candidate-current; diff>0.20才触发否则None; confidence=min(0.6+score_diff, 0.9); REPLACEMENT指令必须带replace_with
#   inputs: I2 I3
#   outputs: REPLACEMENT/REPLACE卖出指令或None
#   invariant: 置换=候选池有更优标的→卖A买B; confidence∈[0,1]
# - id: A3
#   name_zh: ③ 指令回调广播
#   name_en: on_order/_notify
#   intro: 卖出指令生成后逐个通知注册的回调且单个回调故障不影响其他
#   desc: on_order注册回调; _notify遍历回调执行, 异常隔离记error日志
#   inputs: A1 A2
#   outputs: 回调事件分发
# 层: 输出
# - id: O1
#   name_zh: 置换/再平衡卖出指令
#   name_en: ReplacementRebalanceOrder
#   intro: 含标的/类型/权重/方向/置信度/置换目标的frozen卖出指令, 即收集器第⑥类信号源
#   invariant: confidence∈[0,1]; REPLACEMENT必须带replace_with
#   downstream: MOD-SELL-001(收集器第⑥类信号源); MOD-SELL-007(融合引擎)
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I3 --> A1
# I2 --> A2
# I3 --> A2
# A1 --> A3
# A2 --> A3
# A1 --> O1
# A2 --> O1
# A3 --> O1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Final

from zephyr.sell_decision.core.sell_signal_collector import SellDirection
from zephyr.shared.foundation.errors import ZephyrBaseError

__all__: Final = [
    "SellOrderType",
    "ReplacementRebalanceOrder",
    "ReplacementRebalanceSeller",
    "InvalidRebalanceInputError",
]

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# 枚举
# ──────────────────────────────────────────────────────────────────────────────


class SellOrderType(str, Enum):
    """置换/再平衡卖出类型。"""

    REPLACEMENT = "REPLACEMENT"  # 置换卖出(卖A买B, 机会成本驱动)
    REBALANCE = "REBALANCE"  # 再平衡卖出(权重偏离驱动)


# ──────────────────────────────────────────────────────────────────────────────
# 错误
# ──────────────────────────────────────────────────────────────────────────────


class InvalidRebalanceInputError(ZephyrBaseError):
    """置换/再平衡输入数据非法(如权重越界、阈值为负)。"""

    error_code = "ZA-SELL-0006"


# ──────────────────────────────────────────────────────────────────────────────
# 数据模型
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class ReplacementRebalanceOrder:
    """置换/再平衡卖出指令 (SELL-06 产出, SELL-01/SELL-07 消费)。

    Attributes:
        symbol: 卖出标的代码
        order_type: 卖出类型(REPLACEMENT/REBALANCE)
        current_weight: 当前权重[0,1]
        target_weight: 目标权重[0,1]
        direction: 卖出方向(REPLACE/REDUCE)
        confidence: 置信度[0,1]
        reason: 人类可读原因
        replace_with: 置换目标标的(仅 REPLACEMENT, 卖A买B的B)
        metadata: 附加数据(偏离幅度/评分差等)
        timestamp: 指令时间
    """

    symbol: str
    order_type: SellOrderType
    current_weight: float
    target_weight: float
    direction: SellDirection
    confidence: float
    reason: str = ""
    replace_with: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not self.symbol:
            raise InvalidRebalanceInputError("symbol must not be empty")
        if not 0.0 <= self.current_weight <= 1.0:
            raise InvalidRebalanceInputError(f"current_weight must be in [0,1], got {self.current_weight}")
        if not 0.0 <= self.target_weight <= 1.0:
            raise InvalidRebalanceInputError(f"target_weight must be in [0,1], got {self.target_weight}")
        if not 0.0 <= self.confidence <= 1.0:
            raise InvalidRebalanceInputError(f"confidence must be in [0,1], got {self.confidence}")
        if self.order_type is SellOrderType.REPLACEMENT and not self.replace_with:
            raise InvalidRebalanceInputError("replace_with must be set for REPLACEMENT order")


# ──────────────────────────────────────────────────────────────────────────────
# 卖出器
# ──────────────────────────────────────────────────────────────────────────────


# 再平衡默认阈值: 权重偏离 > 5% 触发
_DEFAULT_REBALANCE_THRESHOLD: Final = 0.05

# 置换默认阈值: 候选评分高出当前 > 20% 触发
_DEFAULT_REPLACEMENT_SCORE_THRESHOLD: Final = 0.20

# 再平衡置信度: 偏离越大置信度越高
_REBALANCE_BASE_CONFIDENCE: Final = 0.5
_REBALANCE_MAX_CONFIDENCE: Final = 0.9

# 置换置信度: 评分差越大置信度越高
_REPLACEMENT_BASE_CONFIDENCE: Final = 0.6
_REPLACEMENT_MAX_CONFIDENCE: Final = 0.9


class ReplacementRebalanceSeller:
    """置换与再平衡卖出器——机会成本驱动+组合再平衡驱动。

    用法:
        seller = ReplacementRebalanceSeller()
        # 再平衡: 权重偏离>阈值 → 被动卖出
        order = seller.evaluate_rebalance("000001.SZ", 0.12, 0.05)
        # 置换: 候选池有更优标的 → 卖A买B
        order = seller.evaluate_replacement("000001.SZ", 0.60, "600000.SH", 0.85)

    不变量:
        - 再平衡: current_weight - target_weight > threshold → REDUCE(超配卖出)
        - 置换: candidate_score - current_score > score_threshold → REPLACE(卖A买B)
        - 低配(current < target)不触发卖出(需买入, 非本模块职责)
    """

    def __init__(
        self,
        rebalance_threshold: float = _DEFAULT_REBALANCE_THRESHOLD,
        replacement_score_threshold: float = _DEFAULT_REPLACEMENT_SCORE_THRESHOLD,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        if not 0.0 < rebalance_threshold <= 1.0:
            raise InvalidRebalanceInputError(f"rebalance_threshold must be in (0,1], got {rebalance_threshold}")
        if not 0.0 <= replacement_score_threshold <= 1.0:
            raise InvalidRebalanceInputError(
                f"replacement_score_threshold must be in [0,1], got {replacement_score_threshold}"
            )
        self._rebalance_threshold = rebalance_threshold
        self._replacement_score_threshold = replacement_score_threshold
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._order_callbacks: list[Callable[[ReplacementRebalanceOrder], None]] = []

    # ── 再平衡评估 ──

    def evaluate_rebalance(
        self,
        symbol: str,
        current_weight: float,
        target_weight: float,
        now: datetime | None = None,
    ) -> ReplacementRebalanceOrder | None:
        """评估再平衡卖出: 权重偏离 > 阈值 → 被动卖出超配。

        Args:
            symbol: 标的代码
            current_weight: 当前权重[0,1]
            target_weight: 目标权重[0,1]
            now: 时间

        Returns:
            ReplacementRebalanceOrder(REBALANCE, REDUCE) 或 None(未超配)
        """
        if not symbol:
            raise InvalidRebalanceInputError("symbol must not be empty")
        if not 0.0 <= current_weight <= 1.0:
            raise InvalidRebalanceInputError(f"current_weight must be in [0,1], got {current_weight}")
        if not 0.0 <= target_weight <= 1.0:
            raise InvalidRebalanceInputError(f"target_weight must be in [0,1], got {target_weight}")

        now = now or self._clock()
        drift = current_weight - target_weight

        # 超配(当前>目标)且偏离>阈值 → 卖出
        if drift <= self._rebalance_threshold:
            return None  # 未超配或偏离不足

        # 置信度: 偏离越大越高, 上限0.9
        confidence = min(
            _REBALANCE_BASE_CONFIDENCE + drift,
            _REBALANCE_MAX_CONFIDENCE,
        )

        order = ReplacementRebalanceOrder(
            symbol=symbol,
            order_type=SellOrderType.REBALANCE,
            current_weight=current_weight,
            target_weight=target_weight,
            direction=SellDirection.REDUCE,
            confidence=confidence,
            reason=f"权重偏离 {drift:.1%} > 阈值 {self._rebalance_threshold:.1%}, 再平衡减仓",
            metadata={"drift": drift, "threshold": self._rebalance_threshold},
            timestamp=now,
        )
        self._notify(order)
        return order

    # ── 置换评估 ──

    def evaluate_replacement(
        self,
        symbol: str,
        current_score: float,
        replace_with: str,
        candidate_score: float,
        now: datetime | None = None,
    ) -> ReplacementRebalanceOrder | None:
        """评估置换卖出: 候选评分高出当前 > 阈值 → 卖A买B。

        Args:
            symbol: 当前持仓标的(卖A)
            current_score: 当前持仓评分[0,1]
            replace_with: 候选标的(买B)
            candidate_score: 候选标的评分[0,1]
            now: 时间

        Returns:
            ReplacementRebalanceOrder(REPLACEMENT, REPLACE) 或 None(无需置换)
        """
        if not symbol:
            raise InvalidRebalanceInputError("symbol must not be empty")
        if not replace_with:
            raise InvalidRebalanceInputError("replace_with must not be empty")
        if not 0.0 <= current_score <= 1.0:
            raise InvalidRebalanceInputError(f"current_score must be in [0,1], got {current_score}")
        if not 0.0 <= candidate_score <= 1.0:
            raise InvalidRebalanceInputError(f"candidate_score must be in [0,1], got {candidate_score}")

        now = now or self._clock()
        score_diff = candidate_score - current_score

        # 候选评分高出当前 > 阈值 → 置换
        if score_diff <= self._replacement_score_threshold:
            return None  # 候选不够优

        # 置信度: 评分差越大越高, 上限0.9
        confidence = min(
            _REPLACEMENT_BASE_CONFIDENCE + score_diff,
            _REPLACEMENT_MAX_CONFIDENCE,
        )

        order = ReplacementRebalanceOrder(
            symbol=symbol,
            order_type=SellOrderType.REPLACEMENT,
            current_weight=current_score,  # 复用字段存评分
            target_weight=candidate_score,
            direction=SellDirection.REPLACE,
            confidence=confidence,
            reason=f"候选 {replace_with} 评分 {candidate_score:.2f} 高于当前 {current_score:.2f}(差 {score_diff:.2f}), 置换卖出",
            replace_with=replace_with,
            metadata={"score_diff": score_diff, "threshold": self._replacement_score_threshold},
            timestamp=now,
        )
        self._notify(order)
        return order

    # ── 事件回调 ──

    def on_order(self, callback: Callable[[ReplacementRebalanceOrder], None]) -> None:
        """注册卖出指令生成回调。"""
        self._order_callbacks.append(callback)

    def _notify(self, order: ReplacementRebalanceOrder) -> None:
        for cb in self._order_callbacks:
            try:
                cb(order)
            except Exception as exc:  # noqa: BLE001 — 隔离回调故障
                logger.error("Rebalance order callback failed: %s", exc, exc_info=True)
