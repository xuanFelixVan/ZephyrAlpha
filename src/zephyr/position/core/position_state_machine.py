# [BLUEPRINT] MOD-POS-002 | docs/03_modules/_domain_position/position_state_machine/blueprint.md
# [MODULE] zephyr.position.core.position_state_machine
# [DOMAIN] D_POSITION
# [DEPENDENCIES] zephyr.shared.lifecycle.state_machine
# [CONSUMERS] MOD-POS-003(漂移监控) ; MOD-POS-009(审计) ; MOD-POS-016(卖仓联动) ; D-SELL-DECISION(仓位状态反馈)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 状态转换必须合法;OBSERVING期间禁止新买入;CLOSED冷却期内禁止重新建仓;灰度阶段只能单调推进
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidTransitionError;TransitionGuardError;ObservingPeriodViolationError;CooldownPeriodError;GraduationRegressionError
# [TESTS] tests/position/test_position_state_machine.py
# [A_module] module_id=MOD-POS-002 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""


Position State Machine — 仓位状态机 (MOD-POS-002)

仓位裁决中心的状态根——管理单标的仓位生命周期状态转换。

状态机:
    NONE → BUILDING → ACTIVE → OBSERVING → REDUCING → EXITING → CLOSED
                                                ↑                ↓
                                                └────── (冷却期后可重建) ──┘

关键业务规则 (依据 D-POSITION §1.1 POS-02):
    - OBSERVING 观察期: 软止损/异常开盘/暴跌触发, 收盘前15min确认执行或解除, 期间禁止新买入
    - CLOSED 冷却期: 平仓后N个交易日最小重仓间隔, 期间禁止重新建仓
    - 灰度发布4阶段: BUILDING期间 5%→20%→50%→100%, 每阶段N天验证

输入→输出:
    输入: 仓位状态变更事件 (建仓指令/软止损触发/异常开盘/暴跌/平仓指令等)
    输出: E-POS-05 StateChanged 事件

设计说明:
    - 复用共享 StateMachine[S] 基类 (MOD-INF-038) 管状态转换合法性
    - 业务规则(观察期/冷却期/灰度)在业务层包装, 不污染共享基类
    - 时间通过 now 参数注入, 状态机不耦合具体日历/数据源 (便于测试)
    - 配置参数(observing_confirm_minutes/cooldown_days/graduation_stage_days)为可调默认值,
      属C类(框架AI建, 参数用户校准)

依据: D:\临时工作区\依赖图-D-POSITION-仓位管理域.md §1.1 POS-02, §4 E-POS-05
SSoT: depgraph MOD-POS-002
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 仓位状态变更指令 方法调用事件
#   fields: 指令类型(建仓/观察/减仓/清仓/平仓) + 时间戳now + 观察原因ObservingReason
#   code: start_building/enter_observing/start_reducing/start_exiting/close 方法入参
# - id: I2
#   name: 状态机可调配置 PositionStateMachineConfig
#   fields: observing_confirm_minutes=15 + cooldown_trading_days=5 + graduation_stage_days=5
#   code: PositionStateMachineConfig L162
# 层: 算法
# - id: A1
#   name_zh: ① 转换合法性校验
#   name_en: StateMachine.transition
#   intro: 复用共享状态机基类，用转换矩阵拦截非法状态跳转
#   desc: 7状态15条合法转换 NONE→BUILDING→ACTIVE→OBSERVING→REDUCING→EXITING→CLOSED，非法抛InvalidTransitionError
#   inputs: I1
#   outputs: 合法的新状态
#   invariant: 状态转换必须合法
# - id: A2
#   name_zh: ② 观察期管理
#   name_en: enter_observing/exit_observing
#   intro: 软止损/异常开盘/暴跌触发观察期，15分钟确认窗口内决定执行或解除
#   desc: 记录observing_since/reason/confirm_by=now+15min；confirm=True→REDUCING，False→ACTIVE
#   inputs: I1 I2
#   outputs: OBSERVING状态及确认截止时间
#   invariant: OBSERVING期间禁止新买入 can_buy=False
# - id: A3
#   name_zh: ③ 冷却期管理
#   name_en: close/can_rebuild
#   intro: 平仓后N个交易日内禁止重新建仓
#   desc: close写cooldown_until(缺省now+5日)；can_rebuild判断now>=cooldown_until
#   inputs: I1 I2
#   outputs: cooldown_until冷却截止时间
#   invariant: CLOSED冷却期内禁止重新建仓
# - id: A4
#   name_zh: ④ 灰度发布推进
#   name_en: advance_graduation
#   intro: 建仓期按5%→20%→50%→100%四阶段单调放量
#   desc: 每阶段需持满graduation_stage_days=5天；满仓STAGE_4_100PCT自动转ACTIVE
#   inputs: I1 I2
#   outputs: 灰度权重0.05→1.0
#   invariant: 灰度阶段只能单调推进
# 层: 输出
# - id: O1
#   name_zh: 状态变更事件 E-POS-05
#   name_en: StateChangedEvent
#   intro: 每次状态转换广播from/to状态、原因和上下文快照
#   downstream: MOD-POS-003漂移监控 MOD-POS-009审计 MOD-POS-016卖仓联动 D-SELL-DECISION
# - id: O2
#   name_zh: 仓位上下文只读查询
#   name_en: PositionContext
#   intro: 对外提供can_buy/can_rebuild/graduation_weight/is_in_cooldown等查询
#   downstream: MOD-POS-016卖仓联动 内部使用
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I1 --> A2
# I1 --> A3
# I1 --> A4
# I2 --> A2
# I2 --> A3
# I2 --> A4
# A1 --> A2
# A1 --> A3
# A1 --> A4
# A2 --> O1
# A3 --> O1
# A4 --> O1
# A1 --> O2
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Callable

from zephyr.shared.foundation.errors import ZephyrBaseError
from zephyr.shared.lifecycle.state_machine import (
    InvalidTransitionError,
    StateDefinition,
    StateMachine,
    StateMachineConfig,
    Transition,
)

__all__ = [
    "PositionState",
    "ObservingReason",
    "GraduationStage",
    "PositionStateMachineConfig",
    "PositionContext",
    "StateChangedEvent",
    "PositionStateMachine",
    "ObservingPeriodViolationError",
    "CooldownPeriodError",
    "GraduationRegressionError",
]

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# 枚举
# ──────────────────────────────────────────────────────────────────────────────


class PositionState(str, Enum):
    """仓位生命周期状态 (D-POSITION §1.1 POS-02)。"""

    NONE = "NONE"  # 无持仓
    BUILDING = "BUILDING"  # 建仓中(含灰度发布4阶段)
    ACTIVE = "ACTIVE"  # 持仓就绪
    OBSERVING = "OBSERVING"  # 观察期(软止损/异常开盘/暴跌, 禁止新买入)
    REDUCING = "REDUCING"  # 减仓中
    EXITING = "EXITING"  # 清仓中
    CLOSED = "CLOSED"  # 已平仓(进入冷却期)


class ObservingReason(str, Enum):
    """进入观察期的原因 (POS-02 OBSERVING)。"""

    SOFT_STOP = "SOFT_STOP"  # 软止损触发
    ABNORMAL_OPEN = "ABNORMAL_OPEN"  # 异常开盘(高开/低开异常)
    PLUNGE = "PLUNGE"  # 暴跌


class GraduationStage(str, Enum):
    """灰度发布4阶段 (POS-02 建仓期逐步放量)。"""

    NONE = "NONE"  # 非建仓期
    STAGE_1_5PCT = "STAGE_1_5PCT"  # 第一阶段 5%
    STAGE_2_20PCT = "STAGE_2_20PCT"  # 第二阶段 20%
    STAGE_3_50PCT = "STAGE_3_50PCT"  # 第三阶段 50%
    STAGE_4_100PCT = "STAGE_4_100PCT"  # 第四阶段 100% (满仓, 转ACTIVE)


# 灰度阶段→目标权重比例
_GRADUATION_WEIGHTS: dict[GraduationStage, float] = {
    GraduationStage.STAGE_1_5PCT: 0.05,
    GraduationStage.STAGE_2_20PCT: 0.20,
    GraduationStage.STAGE_3_50PCT: 0.50,
    GraduationStage.STAGE_4_100PCT: 1.00,
}

# 灰度阶段单调推进顺序
_GRADUATION_ORDER: list[GraduationStage] = [
    GraduationStage.STAGE_1_5PCT,
    GraduationStage.STAGE_2_20PCT,
    GraduationStage.STAGE_3_50PCT,
    GraduationStage.STAGE_4_100PCT,
]


# ──────────────────────────────────────────────────────────────────────────────
# 错误
# ──────────────────────────────────────────────────────────────────────────────


class ObservingPeriodViolationError(ZephyrBaseError):
    """观察期规则违反(如观察期内尝试新买入)。"""

    # 2026-08-17 改号 ZA-POS-0001→ZA-POS-0011：与 position_sizing_engine(MOD-POS-001)
    # 重码，按 #ARCH-ERRCODE-001「后引入者改号」裁定（canonical=MOD-POS-001，本模块 MOD-POS-002）
    error_code = "ZA-POS-0011"


class CooldownPeriodError(ZephyrBaseError):
    """冷却期规则违反(如冷却期内尝试重新建仓)。"""

    # 2026-08-17 改号 ZA-POS-0002→ZA-POS-0012（同上裁定）
    error_code = "ZA-POS-0012"


class GraduationRegressionError(ZephyrBaseError):
    """灰度阶段回退违反(灰度阶段只能单调推进)。"""

    # 2026-08-17 改号 ZA-POS-0003→ZA-POS-0013（同上裁定）
    error_code = "ZA-POS-0013"


# ──────────────────────────────────────────────────────────────────────────────
# 配置与上下文
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class PositionStateMachineConfig:
    """仓位状态机可调参数 (C类: 框架默认值, 用户可校准)。

    所有时间单位为分钟/天, 由调用方结合交易日历换算后传入。
    状态机自身不耦合日历。
    """

    observing_confirm_minutes: int = 15
    """观察期确认窗口(分钟)——收盘前15min确认执行或解除 (POS-02 设计值)。"""

    cooldown_trading_days: int = 5
    """CLOSED后最小重仓间隔(交易日)——设计文档"N天"未定具体值, 默认5日可调。"""

    graduation_stage_days: int = 5
    """灰度发布每阶段最短验证天数 (5%→20%→50%→100% 各阶段)。"""


@dataclass
class PositionContext:
    """单标的仓位状态上下文 (聚合根的值对象)。"""

    symbol: str
    state: PositionState = PositionState.NONE

    # 灰度发布
    graduation_stage: GraduationStage = GraduationStage.NONE
    stage_started_at: datetime | None = None

    # 观察期
    observing_since: datetime | None = None
    observing_reason: ObservingReason | None = None
    observing_confirm_by: datetime | None = None

    # 冷却期
    cooldown_until: datetime | None = None

    # 时间戳
    entered_state_at: datetime | None = None

    @property
    def graduation_weight(self) -> float:
        """当前灰度阶段对应的目标权重比例 (0.0~1.0)。"""
        return _GRADUATION_WEIGHTS.get(self.graduation_stage, 0.0)


@dataclass(frozen=True)
class StateChangedEvent:
    """E-POS-05 StateChanged 事件 (D-POSITION §4)。"""

    symbol: str
    from_state: PositionState
    to_state: PositionState
    timestamp: datetime
    reason: str = ""
    context_snapshot: dict[str, Any] = field(default_factory=dict)


# ──────────────────────────────────────────────────────────────────────────────
# 状态机定义
# ──────────────────────────────────────────────────────────────────────────────


def _build_state_machine_config() -> StateMachineConfig[PositionState]:
    """构建仓位状态机的共享 StateMachineConfig (转换合法性矩阵)。"""
    states = [
        StateDefinition(PositionState.NONE, is_terminal=False),
        StateDefinition(PositionState.BUILDING, is_terminal=False),
        StateDefinition(PositionState.ACTIVE, is_terminal=False),
        StateDefinition(PositionState.OBSERVING, is_terminal=False),
        StateDefinition(PositionState.REDUCING, is_terminal=False),
        StateDefinition(PositionState.EXITING, is_terminal=False),
        StateDefinition(PositionState.CLOSED, is_terminal=False),
    ]
    transitions = [
        # NONE → BUILDING (开始建仓, 业务层校验冷却期)
        Transition(PositionState.NONE, PositionState.BUILDING),
        # BUILDING → ACTIVE (灰度4阶段完成)
        Transition(PositionState.BUILDING, PositionState.ACTIVE),
        # BUILDING → EXITING (建仓中直接清仓)
        Transition(PositionState.BUILDING, PositionState.EXITING),
        # BUILDING → OBSERVING (建仓期触发观察)
        Transition(PositionState.BUILDING, PositionState.OBSERVING),
        # ACTIVE → OBSERVING (软止损/异常开盘/暴跌)
        Transition(PositionState.ACTIVE, PositionState.OBSERVING),
        # ACTIVE → REDUCING (开始减仓)
        Transition(PositionState.ACTIVE, PositionState.REDUCING),
        # ACTIVE → EXITING (直接清仓)
        Transition(PositionState.ACTIVE, PositionState.EXITING),
        # OBSERVING → ACTIVE (观察期解除, 风险解除)
        Transition(PositionState.OBSERVING, PositionState.ACTIVE),
        # OBSERVING → REDUCING (观察期确认减仓)
        Transition(PositionState.OBSERVING, PositionState.REDUCING),
        # OBSERVING → EXITING (观察期确认清仓)
        Transition(PositionState.OBSERVING, PositionState.EXITING),
        # REDUCING → ACTIVE (减仓完成, 回到活跃)
        Transition(PositionState.REDUCING, PositionState.ACTIVE),
        # REDUCING → EXITING (减仓转清仓)
        Transition(PositionState.REDUCING, PositionState.EXITING),
        # EXITING → CLOSED (清仓完成, 进入冷却期)
        Transition(PositionState.EXITING, PositionState.CLOSED),
        # CLOSED → BUILDING (冷却期过后重新建仓, 业务层校验冷却期)
        Transition(PositionState.CLOSED, PositionState.BUILDING),
        # CLOSED → NONE (放弃该标的)
        Transition(PositionState.CLOSED, PositionState.NONE),
    ]
    return StateMachineConfig(
        fsm_id="position_state_machine",
        states=states,
        transitions=transitions,
        initial=PositionState.NONE,
        owner_module="MOD-POS-002",
    )


class PositionStateMachine:
    """单标的仓位状态机——管理仓位生命周期+观察期+冷却期+灰度发布。

    用法:
        fsm = PositionStateMachine("000001.SZ")
        fsm.start_building(now=t0)              # NONE → BUILDING (灰度阶段1)
        fsm.advance_graduation(now=t0+6d)       # 灰度阶段1 → 2
        fsm.activate(now=t0+21d)                # BUILDING → ACTIVE (灰度满仓)
        fsm.enter_observing(ObservingReason.SOFT_STOP, now=t1)  # → OBSERVING
        fsm.exit_observing(confirm=True, now=t1+10min)         # → REDUCING
        fsm.start_exiting(now=t2)               # → EXITING
        fsm.close(cooldown_until=t2+5d, now=t2) # → CLOSED (进入冷却期)

    Args:
        symbol: 标的代码
        config: 可调参数 (默认值见 PositionStateMachineConfig)
        clock: 可选时间源 (测试注入), 默认用 datetime.now(timezone.utc)
    """

    def __init__(
        self,
        symbol: str,
        config: PositionStateMachineConfig | None = None,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._symbol = symbol
        self._config = config or PositionStateMachineConfig()
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._fsm = StateMachine[PositionState](_build_state_machine_config())
        self._ctx = PositionContext(symbol=symbol, state=PositionState.NONE, entered_state_at=self._clock())
        self._listeners: list[Callable[[StateChangedEvent], None]] = []

    # ── 只读属性 ──

    @property
    def symbol(self) -> str:
        return self._symbol

    @property
    def state(self) -> PositionState:
        return self._ctx.state

    @property
    def context(self) -> PositionContext:
        return self._ctx

    @property
    def graduation_stage(self) -> GraduationStage:
        return self._ctx.graduation_stage

    @property
    def graduation_weight(self) -> float:
        return self._ctx.graduation_weight

    @property
    def is_observing(self) -> bool:
        return self._ctx.state == PositionState.OBSERVING

    @property
    def is_in_cooldown(self) -> bool:
        """当前是否处于冷却期(CLOSED状态且冷却未到期)。"""
        if self._ctx.state != PositionState.CLOSED:
            return False
        now = self._clock()
        return self._ctx.cooldown_until is not None and now < self._ctx.cooldown_until

    @property
    def history(self) -> list[tuple[PositionState, PositionState, dict[str, Any] | None]]:
        return self._fsm.history

    # ── 业务规则查询 ──

    def can_buy(self) -> bool:
        """是否允许新买入 (OBSERVING期间禁止新买入, POS-02 不变量)。"""
        if self._ctx.state == PositionState.OBSERVING:
            return False
        return True

    def can_rebuild(self, now: datetime | None = None) -> bool:
        """是否允许重新建仓 (冷却期已过)。"""
        if self._ctx.state != PositionState.CLOSED:
            return self._ctx.state == PositionState.NONE
        now = now or self._clock()
        if self._ctx.cooldown_until is None:
            return True
        return now >= self._ctx.cooldown_until

    # ── 状态转换业务方法 ──

    def start_building(self, now: datetime | None = None) -> StateChangedEvent:
        """NONE/CLOSED → BUILDING, 开始建仓并进入灰度阶段1。

        Raises:
            CooldownPeriodError: 冷却期未过
            InvalidTransitionError: 当前状态不允许建仓
        """
        now = now or self._clock()
        if self._ctx.state == PositionState.CLOSED and not self.can_rebuild(now):
            raise CooldownPeriodError(
                f"[{self._symbol}] cooldown not expired, cannot rebuild until {self._ctx.cooldown_until}"
            )
        # 先进入灰度阶段1, 再转换状态——事件快照需反映转换后的完整上下文
        self._enter_graduation(GraduationStage.STAGE_1_5PCT, now)
        event = self._transition(PositionState.BUILDING, now=now, reason="start_building")
        return event

    def advance_graduation(self, now: datetime | None = None) -> StateChangedEvent:
        """灰度阶段单调推进 5%→20%→50%→100%。

        需满足当前阶段最短验证天数。满仓(STAGE_4_100PCT)完成后自动转 ACTIVE。

        Raises:
            GraduationRegressionError: 不在BUILDING状态或已是满仓阶段
        """
        now = now or self._clock()
        if self._ctx.state != PositionState.BUILDING:
            raise GraduationRegressionError(f"[{self._symbol}] cannot advance graduation in state {self._ctx.state}")
        if self._ctx.graduation_stage == GraduationStage.STAGE_4_100PCT:
            raise GraduationRegressionError(f"[{self._symbol}] already at full graduation stage")
        # 校验当前阶段最短持续天数
        if self._ctx.stage_started_at is not None:
            elapsed = now - self._ctx.stage_started_at
            required = timedelta(days=self._config.graduation_stage_days)
            if elapsed < required:
                raise GraduationRegressionError(
                    f"[{self._symbol}] graduation stage {self._ctx.graduation_stage} "
                    f"held {elapsed}, required {required}"
                )
        current_idx = _GRADUATION_ORDER.index(self._ctx.graduation_stage)
        next_stage = _GRADUATION_ORDER[current_idx + 1]
        self._enter_graduation(next_stage, now)
        logger.info(
            "[%s] graduation %s → %s (weight=%.2f)",
            self._symbol,
            _GRADUATION_ORDER[current_idx].value,
            next_stage.value,
            _GRADUATION_WEIGHTS[next_stage],
        )
        # 满仓阶段完成 → 自动转 ACTIVE (不作为单独 StateChanged, 同步切换)
        if next_stage == GraduationStage.STAGE_4_100PCT:
            return self._transition(PositionState.ACTIVE, now=now, reason="graduation_complete")
        # 推进不产生 StateChanged (状态仍是 BUILDING), 返回一个同态事件便于审计
        return StateChangedEvent(
            symbol=self._symbol,
            from_state=PositionState.BUILDING,
            to_state=PositionState.BUILDING,
            timestamp=now,
            reason=f"graduation:{_GRADUATION_ORDER[current_idx].value}->{next_stage.value}",
            context_snapshot=self._snapshot(),
        )

    def activate(self, now: datetime | None = None) -> StateChangedEvent:
        """BUILDING → ACTIVE (建仓完成, 满仓就绪)。"""
        now = now or self._clock()
        # 激活时确保灰度已满仓
        if self._ctx.graduation_stage != GraduationStage.STAGE_4_100PCT:
            self._enter_graduation(GraduationStage.STAGE_4_100PCT, now)
        return self._transition(PositionState.ACTIVE, now=now, reason="activate")

    def enter_observing(self, reason: ObservingReason, now: datetime | None = None) -> StateChangedEvent:
        """ACTIVE/BUILDING → OBSERVING, 进入观察期。

        观察期确认窗口 = observing_confirm_minutes (默认15min)。
        期间禁止新买入 (can_buy() 返回 False)。
        """
        now = now or self._clock()
        event = self._transition(PositionState.OBSERVING, now=now, reason=f"observing:{reason.value}")
        self._ctx.observing_since = now
        self._ctx.observing_reason = reason
        self._ctx.observing_confirm_by = now + timedelta(minutes=self._config.observing_confirm_minutes)
        return event

    def exit_observing(self, *, confirm: bool, now: datetime | None = None) -> StateChangedEvent:
        """退出观察期。

        Args:
            confirm: True=确认执行(减仓/清仓, 视后续调用) → REDUCING;
                     False=风险解除 → ACTIVE
            now: 时间戳

        Raises:
            InvalidTransitionError: 当前不在OBSERVING状态
        """
        now = now or self._clock()
        target = PositionState.REDUCING if confirm else PositionState.ACTIVE
        reason = "observing_confirmed" if confirm else "observing_cleared"
        event = self._transition(target, now=now, reason=reason)
        self._ctx.observing_since = None
        self._ctx.observing_reason = None
        self._ctx.observing_confirm_by = None
        return event

    def start_reducing(self, now: datetime | None = None) -> StateChangedEvent:
        """ACTIVE/OBSERVING → REDUCING (开始减仓)。"""
        now = now or self._clock()
        return self._transition(PositionState.REDUCING, now=now, reason="start_reducing")

    def start_exiting(self, now: datetime | None = None) -> StateChangedEvent:
        """→ EXITING (开始清仓)。"""
        now = now or self._clock()
        return self._transition(PositionState.EXITING, now=now, reason="start_exiting")

    def close(
        self,
        *,
        cooldown_until: datetime | None = None,
        now: datetime | None = None,
    ) -> StateChangedEvent:
        """EXITING → CLOSED, 清仓完成进入冷却期。

        Args:
            cooldown_until: 冷却期到期时间(由调用方按交易日历计算 N 个交易日后)。
                            若不传, 默认 cooldown_trading_days 个自然日后(简易模式)。
            now: 时间戳
        """
        now = now or self._clock()
        if cooldown_until is None:
            cooldown_until = now + timedelta(days=self._config.cooldown_trading_days)
        event = self._transition(PositionState.CLOSED, now=now, reason="close")
        self._ctx.cooldown_until = cooldown_until
        self._ctx.graduation_stage = GraduationStage.NONE
        self._ctx.stage_started_at = None
        return event

    def reset(self, now: datetime | None = None) -> StateChangedEvent:
        """→ NONE, 重置为无持仓状态(不含冷却期, 用于强制清理)。"""
        now = now or self._clock()
        self._fsm.reset(PositionState.NONE)
        self._ctx = PositionContext(symbol=self._symbol, state=PositionState.NONE, entered_state_at=now)
        event = StateChangedEvent(
            symbol=self._symbol,
            from_state=PositionState.NONE,
            to_state=PositionState.NONE,
            timestamp=now,
            reason="reset",
            context_snapshot=self._snapshot(),
        )
        self._emit(event)
        return event

    # ── 事件订阅 ──

    def on_state_changed(self, listener: Callable[[StateChangedEvent], None]) -> None:
        """订阅 E-POS-05 StateChanged 事件。"""
        self._listeners.append(listener)

    # ── 内部实现 ──

    def _transition(self, target: PositionState, *, now: datetime, reason: str) -> StateChangedEvent:
        """执行底层状态转换并产出 E-POS-05 事件。"""
        from_state = self._ctx.state
        self._fsm.transition(target, context={"reason": reason, "now": now.isoformat()})
        self._ctx.state = target
        self._ctx.entered_state_at = now
        event = StateChangedEvent(
            symbol=self._symbol,
            from_state=from_state,
            to_state=target,
            timestamp=now,
            reason=reason,
            context_snapshot=self._snapshot(),
        )
        self._emit(event)
        return event

    def _enter_graduation(self, stage: GraduationStage, now: datetime) -> None:
        """进入指定灰度阶段 (内部, 不校验单调性, 由调用方保证)。"""
        self._ctx.graduation_stage = stage
        self._ctx.stage_started_at = now

    def _snapshot(self) -> dict[str, Any]:
        """生成上下文快照(用于事件审计)。"""
        return {
            "symbol": self._ctx.symbol,
            "state": self._ctx.state.value,
            "graduation_stage": self._ctx.graduation_stage.value,
            "graduation_weight": self._ctx.graduation_weight,
            "observing_reason": self._ctx.observing_reason.value if self._ctx.observing_reason else None,
            "is_in_cooldown": self.is_in_cooldown,
        }

    def _emit(self, event: StateChangedEvent) -> None:
        """分发事件给订阅者 (异常不阻断主流程, 仅记录)。"""
        for listener in self._listeners:
            try:
                listener(event)
            except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
                logger.error("[%s] state changed listener error: %s", self._symbol, exc, exc_info=True)
