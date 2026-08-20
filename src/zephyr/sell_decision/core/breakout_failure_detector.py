# [BLUEPRINT] MOD-SELL-003 | docs/03_modules/_domain_sell_decision/breakout_failure_detector/blueprint.md
# [MODULE] zephyr.sell_decision.core.breakout_failure_detector
# [DOMAIN] D_SELL_DECISION
# [DEPENDENCIES] zephyr.shared.foundation.errors ; zephyr.sell_decision.core.sell_signal_collector
# [CONSUMERS] MOD-SELL-001(收集器第⑧类信号源) ; D-POSITION(持有/加仓信号)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 突破成功=价格确认突破压力位; 突破失败=触及压力位但回落; K>=3次失败→强制清仓(最高优先级); confidence∈[0,1]
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidBreakoutInputError
# [TESTS] tests/sell_decision/test_breakout_failure_detector.py
# [A_module] module_id=MOD-SELL-003 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


Breakout Failure Detector — 突破成败检测器 (MOD-SELL-003)

消费 L1 因子层压力位计算结果, 判定突破成功/失败, 产出 BreakoutResult:
    - 突破成功 → 持有/加仓信号(输出至 D-POSITION)
    - 突破失败 → 止损卖出信号(喂给 SELL-001 收集器第⑧类信号)
    - 第 K 次挑战失败(K≥3) → 强制清仓信号(最高优先级)

设计说明:
    - A类基础设施: 纯检测逻辑, 不涉及"压力位怎么算"(那是 D-FACTOR/D-SIGNAL 的职责)
    - 输入契约: 压力位 + 当前价格 + 历史挑战失败次数(由调用方维护)
    - 突破确认: 默认单根确认(当前价>压力位即成功), 可配置多根确认
    - 强制清仓阈值: 默认 K≥3 (设计文档 §1.1 SELL-03), 可配置
    - 输出 BreakoutResult 含 direction: SUCCESS→无卖出 / FAILURE→REDUCE / FORCED_CLEAR→CLEAR

依据: D:\临时工作区\依赖图-D-SELL-DECISION-卖出决策域.md §1.1 SELL-03
SSoT: depgraph MOD-SELL-003
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 压力位 resistance_level float
#   fields: L1 因子层算好的压力位价格（必须>0，本模块不负责计算）
#   code: detect(resistance_level) L205
# - id: I2
#   name: 当前价格 current_price float
#   fields: 最新成交价（必须>0）
#   code: detect(current_price) L205
# - id: I3
#   name: 历史挑战失败次数 challenge_count int
#   fields: 本次检测前累计挑战压力位失败次数（>=0，调用方维护）
#   code: detect(challenge_count) L205
# - id: I4
#   name: 检测器配置 2项
#   fields: forced_clear_threshold=3（第K次失败强平）/ success_confidence=0.8
#   code: __init__ L178（_DEFAULT_FORCED_CLEAR_THRESHOLD L145）
# 层: 算法
# - id: A1
#   name_zh: ① 输入合法性校验
#   name_en: detect 前置校验
#   intro: 先检查标的价格次数合不合法，不合法直接抛错
#   desc: symbol 非空 / resistance_level>0 / current_price>0 / challenge_count>=0，任一违反抛 InvalidBreakoutInputError(ZA-SELL-0003)
#   inputs: I1 I2 I3
#   outputs: 合法输入四元组
# - id: A2
#   name_zh: ② 突破成败三态判定
#   name_en: detect
#   intro: 价过压力位算突破成功，冲不上去累计到第3次就强制清仓
#   desc: 价>压力位→SUCCESS（conf=0.8，direction=REPLACE占位持有，metadata 记 breakout_pct=(C-R)/R）；价≤压力位且 challenge_count+1>=K→FORCED_CLEAR（conf=1.0 CLEAR）；否则→FAILURE（conf=min(0.5+(n-1)*0.1, 0.9) REDUCE，失败次数+1）
#   inputs: A1 I4
#   outputs: BreakoutResult（status/confidence/direction/challenge_count）
#   invariant: K>=3次失败→强制清仓（最高优先级 conf=1.0）；confidence∈[0,1]
# - id: A3
#   name_zh: ③ 检测完成事件回调
#   name_en: _notify
#   intro: 检测出结果后通知所有订阅回调，单个回调挂不影响主流程
#   desc: 遍历 on_detected 注册的回调逐个调用；回调异常隔离记日志
#   inputs: A2
#   outputs: BreakoutResult 事件通知
#   invariant: 回调异常隔离不阻断
# 层: 输出
# - id: O1
#   name_zh: 突破检测结果 BreakoutResult
#   name_en: BreakoutResult
#   intro: 三态结论：成功持有/失败减仓/强平清仓，含置信度与原因
#   invariant: 不可变 frozen dataclass；direction∈REPLACE/REDUCE/CLEAR
#   downstream: MOD-SELL-001 收集器第⑧类信号源 / D-POSITION 持有加仓信号（CONSUMERS 头）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# A1 --> A2
# I4 --> A2
# A2 --> A3
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
    "BreakoutStatus",
    "BreakoutResult",
    "BreakoutFailureDetector",
    "InvalidBreakoutInputError",
]

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# 枚举
# ──────────────────────────────────────────────────────────────────────────────


class BreakoutStatus(str, Enum):
    """突破成败状态。"""

    SUCCESS = "SUCCESS"  # 突破成功(价格确认突破压力位)
    FAILURE = "FAILURE"  # 突破失败(触及压力位但回落)
    FORCED_CLEAR = "FORCED_CLEAR"  # 强制清仓(第K次挑战失败 K≥3)


# ──────────────────────────────────────────────────────────────────────────────
# 错误
# ──────────────────────────────────────────────────────────────────────────────


class InvalidBreakoutInputError(ZephyrBaseError):
    """突破检测输入数据非法(如压力位≤0、挑战次数<0)。"""

    error_code = "ZA-SELL-0003"


# ──────────────────────────────────────────────────────────────────────────────
# 数据模型
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class BreakoutResult:
    """突破检测结果 (SELL-03 产出, SELL-01/D-POSITION 消费)。

    不可变值对象——一旦创建不可修改, 便于安全传递。

    Attributes:
        symbol: 标的代码
        status: 突破状态(SUCCESS/FAILURE/FORCED_CLEAR)
        resistance_level: 压力位价格
        current_price: 当前价格
        challenge_count: 历史挑战失败次数(含本次)
        confidence: 置信度[0,1], 强制清仓=1.0(最高优先级)
        direction: 卖出方向(SUCCESS→无卖出, 用 REPLACE 占位表示持有;
                            FAILURE→REDUCE; FORCED_CLEAR→CLEAR)
        reason: 人类可读的检测原因
        timestamp: 检测时间
    """

    symbol: str
    status: BreakoutStatus
    resistance_level: float
    current_price: float
    challenge_count: int
    confidence: float
    direction: SellDirection
    reason: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not self.symbol:
            raise InvalidBreakoutInputError("BreakoutResult.symbol must not be empty")
        if self.resistance_level <= 0:
            raise InvalidBreakoutInputError(f"resistance_level must be > 0, got {self.resistance_level}")
        if self.current_price <= 0:
            raise InvalidBreakoutInputError(f"current_price must be > 0, got {self.current_price}")
        if self.challenge_count < 0:
            raise InvalidBreakoutInputError(f"challenge_count must be >= 0, got {self.challenge_count}")
        if not 0.0 <= self.confidence <= 1.0:
            raise InvalidBreakoutInputError(f"confidence must be in [0,1], got {self.confidence}")


# ──────────────────────────────────────────────────────────────────────────────
# 检测器
# ──────────────────────────────────────────────────────────────────────────────


# 强制清仓阈值: K≥3 (设计文档 §1.1 SELL-03)
_DEFAULT_FORCED_CLEAR_THRESHOLD: Final = 3

# 突破成功默认置信度
_SUCCESS_CONFIDENCE: Final = 0.8

# 突破失败默认置信度(随挑战次数递增)
_FAILURE_BASE_CONFIDENCE: Final = 0.5
_FAILURE_PER_CHALLENGE_BOOST: Final = 0.1

# 强制清仓置信度(最高优先级)
_FORCED_CLEAR_CONFIDENCE: Final = 1.0


class BreakoutFailureDetector:
    """突破成败检测器——消费压力位+价格+挑战次数, 产出 BreakoutResult。

    用法:
        detector = BreakoutFailureDetector()
        result = detector.detect(
            symbol="000001.SZ",
            resistance_level=10.50,
            current_price=10.30,
            challenge_count=2,
        )
        # result.status == BreakoutStatus.FORCED_CLEAR (第3次失败→强制清仓)

    不变量:
        - 价格 > 压力位 → SUCCESS(突破成功, 持有/加仓)
        - 价格 ≤ 压力位 且 challenge_count+1 < 阈值 → FAILURE(突破失败, 减仓)
        - 价格 ≤ 压力位 且 challenge_count+1 ≥ 阈值 → FORCED_CLEAR(强制清仓)
        - 强制清仓 confidence=1.0(最高优先级)
    """

    def __init__(
        self,
        forced_clear_threshold: int = _DEFAULT_FORCED_CLEAR_THRESHOLD,
        success_confidence: float = _SUCCESS_CONFIDENCE,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        """
        Args:
            forced_clear_threshold: 强制清仓阈值(默认3, 即第3次失败触发)
            success_confidence: 突破成功的置信度(默认0.8)
            clock: 时钟函数(测试注入用), 默认 utcnow
        """
        if forced_clear_threshold < 1:
            raise InvalidBreakoutInputError(f"forced_clear_threshold must be >= 1, got {forced_clear_threshold}")
        if not 0.0 <= success_confidence <= 1.0:
            raise InvalidBreakoutInputError(f"success_confidence must be in [0,1], got {success_confidence}")
        self._threshold = forced_clear_threshold
        self._success_confidence = success_confidence
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._detected_callbacks: list[Callable[[BreakoutResult], None]] = []

    # ── 检测 ──

    def detect(
        self,
        symbol: str,
        resistance_level: float,
        current_price: float,
        challenge_count: int,
        now: datetime | None = None,
    ) -> BreakoutResult:
        """检测突破成败。

        Args:
            symbol: 标的代码
            resistance_level: 压力位价格(必须>0)
            current_price: 当前价格(必须>0)
            challenge_count: 历史挑战失败次数(本次检测前的累计, 必须>=0)
            now: 检测时间(默认 utcnow)

        Returns:
            BreakoutResult: SUCCESS/FAILURE/FORCED_CLEAR

        Raises:
            InvalidBreakoutInputError: 输入非法
        """
        if not symbol:
            raise InvalidBreakoutInputError("symbol must not be empty")
        if resistance_level <= 0:
            raise InvalidBreakoutInputError(f"resistance_level must be > 0, got {resistance_level}")
        if current_price <= 0:
            raise InvalidBreakoutInputError(f"current_price must be > 0, got {current_price}")
        if challenge_count < 0:
            raise InvalidBreakoutInputError(f"challenge_count must be >= 0, got {challenge_count}")

        now = now or self._clock()
        new_challenge_count = challenge_count + 1 if current_price <= resistance_level else challenge_count

        # 判定状态
        if current_price > resistance_level:
            # 突破成功: 价格确认突破压力位
            result = BreakoutResult(
                symbol=symbol,
                status=BreakoutStatus.SUCCESS,
                resistance_level=resistance_level,
                current_price=current_price,
                challenge_count=challenge_count,  # 成功不累计
                confidence=self._success_confidence,
                direction=SellDirection.REPLACE,  # 占位: 持有(不卖出)
                reason=f"价格 {current_price} 突破压力位 {resistance_level}, 突破成功",
                metadata={"breakout_pct": (current_price - resistance_level) / resistance_level},
                timestamp=now,
            )
        elif new_challenge_count >= self._threshold:
            # 强制清仓: 第K次挑战失败 K≥阈值
            result = BreakoutResult(
                symbol=symbol,
                status=BreakoutStatus.FORCED_CLEAR,
                resistance_level=resistance_level,
                current_price=current_price,
                challenge_count=new_challenge_count,
                confidence=_FORCED_CLEAR_CONFIDENCE,
                direction=SellDirection.CLEAR,
                reason=f"第 {new_challenge_count} 次挑战压力位 {resistance_level} 失败(≥{self._threshold}), 强制清仓",
                metadata={"forced_clear": True, "threshold": self._threshold},
                timestamp=now,
            )
        else:
            # 突破失败: 触及压力位但回落, 累计挑战次数未达阈值
            confidence = min(
                _FAILURE_BASE_CONFIDENCE + (new_challenge_count - 1) * _FAILURE_PER_CHALLENGE_BOOST,
                0.9,
            )
            result = BreakoutResult(
                symbol=symbol,
                status=BreakoutStatus.FAILURE,
                resistance_level=resistance_level,
                current_price=current_price,
                challenge_count=new_challenge_count,
                confidence=confidence,
                direction=SellDirection.REDUCE,
                reason=f"价格 {current_price} 未突破压力位 {resistance_level}(第 {new_challenge_count} 次失败), 减仓",
                metadata={"failure_count": new_challenge_count, "threshold": self._threshold},
                timestamp=now,
            )

        self._notify(result)
        return result

    # ── 事件回调 ──

    def on_detected(self, callback: Callable[[BreakoutResult], None]) -> None:
        """注册检测完成回调(用于事件发布)。"""
        self._detected_callbacks.append(callback)

    def _notify(self, result: BreakoutResult) -> None:
        for cb in self._detected_callbacks:
            try:
                cb(result)
            except Exception as exc:  # noqa: BLE001 — 隔离回调故障
                logger.error("Breakout detected callback failed: %s", exc, exc_info=True)
