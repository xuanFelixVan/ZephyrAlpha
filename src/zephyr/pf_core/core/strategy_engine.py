# [BLUEPRINT] MOD-PF-001 | docs/03_modules/_domain_portfolio_core/strategy_engine/blueprint.md
# [MODULE] zephyr.pf_core.core.strategy_engine
# [DOMAIN] D_PF_CORE
# [DEPENDENCIES] zephyr.governance.strategies.strategy_base(OCP-002); zephyr.shared.contracts.strategy_lifecycle_event(CTR-P1-006); zephyr.shared.foundation.errors
# [CONSUMERS] MOD-PF-002(Portfolio Optimizer,消费 target_weights) ; MOD-PF-010(Performance Attribution,消费决策+IC)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 生命周期单调推进(DEPRECATED不可复活);冷启动期权重×0.3;target_weights归一化;幂等键防重复生命周期事件
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] StrategyLifecycleError;ColdStartViolationError;StrategyNotFoundError
# [TESTS] tests/pf_core/test_strategy_engine.py
# [A_module] module_id=MOD-PF-001 | layer=module | stability=evolving | safety=H | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""


Strategy Engine — 策略引擎 (MOD-PF-001)

D-PF-CORE §1.2 L2 组合构建核心模块。策略生命周期管理 + 冷启动协议 + 四维决策聚合。
作为 OCP-002 扩展点的运行时宿主: 策略实现(StrategyBase 子类)是 B 类策略输入,
本引擎提供 A 类基础设施(状态机/冷启动/版本控制/决策聚合), 不做任何策略判断。

核心职责:
    1. 生命周期状态机: registered → testing → active → deprecated (单调推进, 不可复活)
    2. 冷启动协议: 新晋 active 策略在 cold_start_days 内仓位上限 = 正常 × cold_start_factor(0.3)
    3. 版本控制: 策略版本变更触发重新走生命周期
    4. 四维决策聚合: 选股(selection) + 买入(buy) + 卖出(sell) + 仓位(position) → StrategyDecision
    5. 策略退化检测: IC 衰减 > 50% → 自动降级(权重归 0 / 转 DEPRECATED)

属 A 类纯基础设施(状态机+协议+聚合框架), 策略逻辑由 StrategyBase 子类(B 类)注入。
依据: D:\临时工作区\依赖图-D-PF-CORE-组合核心域.md §1.2 PC-01, §3.3 OCP-002
SSoT: depgraph MOD-PF-001
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 策略实现 StrategyBase 子类（B 类策略逻辑）
#   fields: meta() 提供 StrategyMeta（strategy_id/version）；generate_target_weights(universe, signals, constraints) 产出原始权重
#   code: strategy_engine.py L315 register / L483 evaluate 调用
# - id: I2
#   name: 生命周期转换请求
#   fields: strategy_id + to 目标状态 + reason + performance_snapshot 绩效快照
#   code: strategy_engine.py L368-373 transition 参数
# - id: I3
#   name: 决策输入
#   fields: universe 选股宇宙 + signals {symbol: strength}（正买负卖）+ constraints 透传约束
#   code: strategy_engine.py L441-446 evaluate 参数
# - id: I4
#   name: IC 历史序列 ic_history
#   fields: list[float] 旧→新，退化检测用
#   code: strategy_engine.py L546 detect_degradation 参数
# - id: I5
#   name: 引擎配置 StrategyEngineConfig
#   fields: cold_start_factor=0.3 / cold_start_days=7 / max_strategies=20 / min_testing_days=7 / ic_decay_threshold=0.5 / 归一容差 1e-6
#   code: strategy_engine.py L125-143 StrategyEngineConfig
# 层: 算法
# - id: A1
#   name_zh: ① 策略注册与版本控制
#   name_en: register
#   intro: 注册新策略为 REGISTERED，同 ID 换版本就把旧版本归档废弃
#   desc: L315-366 取 meta（实例 _meta 优先）；同 ID 同版本报错；版本变更→旧记录 _archive_record 转 DEPRECATED；活跃数≥max_strategies 拒绝
#   inputs: I1 I5
#   outputs: 注册生命周期事件 + StrategyRecord
# - id: A2
#   name_zh: ② 生命周期状态机
#   name_en: transition
#   intro: 六条合法边单调推进状态，DEPRECATED 是终态不可复活
#   desc: L267-274 _VALID_TRANSITIONS 六条转换边；L368-426 跳级/复活抛 StrategyLifecycleError；TESTING→ACTIVE 须满 min_testing_days(7) 门禁；同状态幂等 no-op
#   inputs: I2 I5
#   outputs: 新状态 + 生命周期事件
#   invariant: 生命周期单调推进，DEPRECATED 不可复活
# - id: A3
#   name_zh: ③ 冷启动判定
#   name_en: _in_cold_start
#   intro: ACTIVE 且激活未满 7 天就算冷启动期
#   desc: L631-640 status==ACTIVE 且 activated_at 非空且 now-activated_at < cold_start_days(7)
#   inputs: A2 I5
#   outputs: cold_start 布尔
# - id: A4
#   name_zh: ④ 四维决策聚合
#   name_en: evaluate
#   intro: 调策略算权重→冷启动打三折→归一化→拆买卖信号，汇总成决策
#   desc: L440-539 可运行校验(TESTING/ACTIVE)→strategy.generate_target_weights→滤宇宙外/非正→冷启动×0.3→_normalize_weights(Σw=1，全零返空)→direction>0 买/<0 卖→StrategyDecision+uuid 幂等键
#   inputs: I1 I3 A3 I5
#   outputs: StrategyDecision
#   invariant: 冷启动期权重×0.3；target_weights 归一化 Σw=1
# - id: A5
#   name_zh: ⑤ 策略退化检测（IC 衰减）
#   name_en: detect_degradation
#   intro: 前半段平均 IC 相比最新 IC 衰减过半就判退化
#   desc: L543-576 baseline=前 len//2 段均值；decay=(baseline-recent)/baseline；>ic_decay_threshold(0.5)→True；baseline≤0 或样本<2 → False
#   inputs: I4 I5
#   outputs: degraded 布尔
# - id: A6
#   name_zh: ⑥ 自动降级
#   name_en: auto_degrade
#   intro: 退化且还在 ACTIVE 的策略自动转 DEPRECATED 并记事件
#   desc: L578-599 detect_degradation=True 且 status==ACTIVE→transition(DEPRECATED, snapshot={ic_decay})；否则返回 None
#   inputs: A5
#   outputs: 生命周期事件或 None
# 层: 输出
# - id: O1
#   name_zh: 策略决策 StrategyDecision
#   name_en: StrategyDecision
#   intro: 目标权重+选股宇宙+买/卖信号列表+冷启动标记+幂等键
#   invariant: 幂等键防重复；冷启动权重已打折
#   downstream: MOD-PF-002 Portfolio Optimizer 消费 target_weights；MOD-PF-010 Performance Attribution 消费决策+IC（[CONSUMERS] 头）
# - id: O2
#   name_zh: 生命周期事件 StrategyLifecycleEvent
#   name_en: StrategyLifecycleEvent (CTR-P1-006)
#   intro: 注册/转换/降级/归档全量审计事件，进 lifecycle_log 只读视图
#   invariant: 幂等键防重复生命周期事件
#   downstream: lifecycle_log 审计；MOD-PF-010 消费（[CONSUMERS] 头）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I5 --> A1
# I2 --> A2
# I5 --> A2
# A1 --> A2
# A2 --> A3
# I5 --> A3
# I1 --> A4
# I3 --> A4
# A3 --> A4
# I5 --> A4
# I4 --> A5
# I5 --> A5
# A5 --> A6
# A4 --> O1
# A1 --> O2
# A2 --> O2
# A6 --> O2
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Callable

from zephyr.governance.strategies.strategy_base import StrategyBase, StrategyMeta
from zephyr.shared.contracts.strategy_lifecycle_event import StrategyLifecycleEvent
from zephyr.shared.foundation.errors import ZephyrBaseError

__all__ = [
    "StrategyStatus",
    "DecisionDimension",
    "StrategySignal",
    "StrategyRecord",
    "StrategyDecision",
    "StrategyEngineConfig",
    "StrategyEngine",
    "StrategyLifecycleError",
    "ColdStartViolationError",
    "StrategyNotFoundError",
]

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# 枚举
# ──────────────────────────────────────────────────────────────────────────────


class StrategyStatus(str, Enum):
    """策略生命周期状态 (单调推进, DEPRECATED 为终态不可复活)。"""

    REGISTERED = "registered"  # 已注册, 未测试
    TESTING = "testing"  # 模拟盘测试中
    ACTIVE = "active"  # 已激活 (可能处冷启动期)
    DEPRECATED = "deprecated"  # 已废弃 (终态)

    @property
    def is_terminal(self) -> bool:
        return self == StrategyStatus.DEPRECATED

    @property
    def is_runnable(self) -> bool:
        """是否可参与决策 (TESTING 可跑模拟, ACTIVE 可跑实盘)。"""
        return self in (StrategyStatus.TESTING, StrategyStatus.ACTIVE)


class DecisionDimension(str, Enum):
    """策略四维决策维度。"""

    SELECTION = "selection"  # 选股: 标的选择
    BUY = "buy"  # 买入: 买入信号
    SELL = "sell"  # 卖出: 卖出信号
    POSITION = "position"  # 仓位: 目标权重


# ──────────────────────────────────────────────────────────────────────────────
# 错误
# ──────────────────────────────────────────────────────────────────────────────


class StrategyLifecycleError(ZephyrBaseError):
    """非法生命周期转换 (如 DEPRECATED→ACTIVE 复活, 跳级转换)。"""

    error_code = "ZA-PF-0011"


class ColdStartViolationError(ZephyrBaseError):
    """冷启动协议违反 (如冷启动期内权重超限)。"""

    error_code = "ZA-PF-0012"


class StrategyNotFoundError(ZephyrBaseError):
    """策略未注册或已删除。"""

    error_code = "ZA-PF-0013"


# ──────────────────────────────────────────────────────────────────────────────
# 配置
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class StrategyEngineConfig:
    """策略引擎配置 (设计真源 §1.2 PC-01, §3.6 学习注入路径)。

    Attributes:
        cold_start_factor: 冷启动仓位系数, 默认 0.3 (新策略仓位=正常×30%)
        cold_start_days: 冷启动持续天数, 默认 7
        max_strategies: 最大并发策略数, 默认 20
        min_testing_days: 最短测试期(天), TESTING→ACTIVE 前须满足, 默认 7
        ic_decay_threshold: IC 衰减阈值, >此值判定策略退化, 默认 0.5
        target_weight_tolerance: 权重归一化容差, 默认 1e-6
    """

    cold_start_factor: float = 0.3
    cold_start_days: int = 7
    max_strategies: int = 20
    min_testing_days: int = 7
    ic_decay_threshold: float = 0.5
    target_weight_tolerance: float = 1e-6

    def __post_init__(self) -> None:
        if not 0 < self.cold_start_factor <= 1:
            raise ColdStartViolationError(f"cold_start_factor must be in (0,1], got {self.cold_start_factor}")
        if self.cold_start_days < 0:
            raise ColdStartViolationError(f"cold_start_days must be >=0, got {self.cold_start_days}")
        if self.max_strategies < 1:
            raise StrategyLifecycleError(f"max_strategies must be >=1, got {self.max_strategies}")
        if self.min_testing_days < 0:
            raise StrategyLifecycleError(f"min_testing_days must be >=0, got {self.min_testing_days}")
        if not 0 < self.ic_decay_threshold <= 1:
            raise StrategyLifecycleError(f"ic_decay_threshold must be in (0,1], got {self.ic_decay_threshold}")


# ──────────────────────────────────────────────────────────────────────────────
# 数据模型
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class StrategySignal:
    """策略四维决策的单条信号。

    Attributes:
        symbol: 标的代码
        dimension: 决策维度 (选股/买入/卖出/仓位)
        direction: 方向 (+1=买/多, -1=卖/空, 0=持有)
        strength: 信号强度 [0, 1]
        weight: 目标权重 (POSITION 维度用, 其余为 0)
    """

    symbol: str
    dimension: DecisionDimension
    direction: float
    strength: float = 0.0
    weight: float = 0.0


@dataclass
class StrategyRecord:
    """引擎内部策略登记记录 (可变, 引擎维护)。

    Attributes:
        strategy_id: 策略 ID
        meta: 策略元数据 (StrategyMeta)
        status: 当前生命周期状态
        version: 当前版本
        registered_at: 注册时间
        status_since: 进入当前状态的时间 (冷启动起点用)
        activated_at: 最近一次进入 ACTIVE 的时间 (None=从未激活)
        performance_snapshot: 最新绩效快照 (IC/胜率等)
    """

    strategy_id: str
    meta: StrategyMeta
    status: StrategyStatus
    version: str
    registered_at: datetime
    status_since: datetime
    activated_at: datetime | None = None
    performance_snapshot: dict[str, float] = field(default_factory=dict)


@dataclass(frozen=True)
class StrategyDecision:
    """策略决策产出 (PC-01 → PC-02)。

    Attributes:
        strategy_id: 来源策略 ID
        target_weights: 目标权重 {symbol: weight} (冷启动期已 ×cold_start_factor)
        selection_universe: 选股宇宙
        buy_signals: 买入信号列表
        sell_signals: 卖出信号列表
        cold_start_active: 本次决策是否受冷启动约束
        lifecycle_event: 触发的生命周期事件 (无则 None)
        timestamp: 决策时间
        idempotency_key: 幂等键
    """

    strategy_id: str
    target_weights: dict[str, float]
    selection_universe: list[str]
    buy_signals: list[StrategySignal]
    sell_signals: list[StrategySignal]
    cold_start_active: bool
    lifecycle_event: StrategyLifecycleEvent | None
    timestamp: datetime
    idempotency_key: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "strategy_id": self.strategy_id,
            "target_weights": dict(self.target_weights),
            "selection_universe": list(self.selection_universe),
            "buy_signals": len(self.buy_signals),
            "sell_signals": len(self.sell_signals),
            "cold_start_active": self.cold_start_active,
            "has_lifecycle_event": self.lifecycle_event is not None,
            "idempotency_key": self.idempotency_key,
        }


# ──────────────────────────────────────────────────────────────────────────────
# 策略引擎
# ──────────────────────────────────────────────────────────────────────────────


# 合法生命周期转换 (单调推进, DEPRECATED 终态)
_VALID_TRANSITIONS: dict[tuple[StrategyStatus, StrategyStatus], str] = {
    (StrategyStatus.REGISTERED, StrategyStatus.TESTING): "promote_to_testing",
    (StrategyStatus.TESTING, StrategyStatus.ACTIVE): "promote_to_active",
    (StrategyStatus.TESTING, StrategyStatus.DEPRECATED): "fail_testing",
    (StrategyStatus.ACTIVE, StrategyStatus.DEPRECATED): "deprecate",
    (StrategyStatus.ACTIVE, StrategyStatus.TESTING): "demote_to_testing",
    (StrategyStatus.REGISTERED, StrategyStatus.DEPRECATED): "abandon",
}


class StrategyEngine:
    """策略引擎——生命周期状态机 + 冷启动协议 + 四维决策聚合。

    用法 (注册+激活+决策):
        engine = StrategyEngine()
        engine.register(my_strategy)                 # → REGISTERED
        engine.transition("s1", StrategyStatus.TESTING)   # → TESTING
        engine.transition("s1", StrategyStatus.ACTIVE)    # → ACTIVE (冷启动开始)
        decision = engine.evaluate("s1", universe, signals, constraints)
        # decision.target_weights (冷启动期已 ×0.3)

    Args:
        config: 引擎配置
        clock: 可选时间源 (测试注入)
    """

    def __init__(
        self,
        config: StrategyEngineConfig | None = None,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._config = config or StrategyEngineConfig()
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._records: dict[str, StrategyRecord] = {}
        self._strategies: dict[str, StrategyBase] = {}
        self._lifecycle_log: list[StrategyLifecycleEvent] = []

    @property
    def config(self) -> StrategyEngineConfig:
        return self._config

    @property
    def lifecycle_log(self) -> list[StrategyLifecycleEvent]:
        """生命周期事件审计日志 (只读视图)。"""
        return list(self._lifecycle_log)

    # ── 注册 / 生命周期 ──

    def register(self, strategy: StrategyBase) -> StrategyLifecycleEvent:
        """注册新策略 (状态=REGISTERED)。

        策略元数据 (StrategyMeta) 由 strategy.meta() 提供。
        同 ID 不同版本 → 触发重新注册 (旧记录归档为 DEPRECATED)。

        Raises:
            StrategyLifecycleError: 超过 max_strategies / 元数据缺失
        """
        meta = self._get_meta(strategy)
        now = self._clock()

        existing = self._records.get(meta.strategy_id)
        if existing is not None:
            if existing.version == meta.version:
                raise StrategyLifecycleError(f"strategy {meta.strategy_id} v{meta.version} already registered")
            # 版本变更: 旧版本归档为 DEPRECATED
            self._archive_record(existing, reason="version_bump", now=now)

        if len(self._records) >= self._config.max_strategies and meta.strategy_id not in self._records:
            active_count = sum(1 for r in self._records.values() if not r.status.is_terminal)
            if active_count >= self._config.max_strategies:
                raise StrategyLifecycleError(f"max_strategies ({self._config.max_strategies}) reached")

        record = StrategyRecord(
            strategy_id=meta.strategy_id,
            meta=meta,
            status=StrategyStatus.REGISTERED,
            version=meta.version,
            registered_at=now,
            status_since=now,
        )
        self._records[meta.strategy_id] = record
        self._strategies[meta.strategy_id] = strategy

        event = self._make_event(
            strategy_id=meta.strategy_id,
            previous="(none)",
            new=StrategyStatus.REGISTERED.value,
            reason="register",
            now=now,
            snapshot={},
        )
        self._lifecycle_log.append(event)
        logger.info("StrategyEngine: registered %s v%s", meta.strategy_id, meta.version)
        return event

    def transition(
        self,
        strategy_id: str,
        to: StrategyStatus,
        reason: str = "",
        performance_snapshot: dict[str, float] | None = None,
    ) -> StrategyLifecycleEvent:
        """转换策略生命周期状态 (单调推进)。

        Raises:
            StrategyNotFoundError: 策略未注册
            StrategyLifecycleError: 非法转换 (跳级/复活/未满足测试期)
        """
        record = self._require(strategy_id)
        current = record.status
        if current == to:
            # 幂等: 同状态转换视为 no-op, 仍记录事件
            logger.debug("StrategyEngine: %s already %s (idempotent)", strategy_id, to.value)
        elif (current, to) not in _VALID_TRANSITIONS:
            raise StrategyLifecycleError(
                f"illegal transition {current.value} -> {to.value} for {strategy_id}"
                f" (valid: {[t[1].value for t in _VALID_TRANSITIONS if t[0] == current]})"
            )

        # TESTING → ACTIVE 门禁: 须满足 min_testing_days
        if (
            current == StrategyStatus.TESTING
            and to == StrategyStatus.ACTIVE
            and not self._testing_period_satisfied(record)
        ):
            raise StrategyLifecycleError(
                f"cannot promote {strategy_id}: testing period ({self._config.min_testing_days}d) not satisfied"
            )

        now = self._clock()
        prev_status = current.value
        record.status = to
        record.status_since = now
        record.performance_snapshot = performance_snapshot or record.performance_snapshot
        if to == StrategyStatus.ACTIVE:
            record.activated_at = now

        event = self._make_event(
            strategy_id=strategy_id,
            previous=prev_status,
            new=to.value,
            reason=reason or _VALID_TRANSITIONS.get((current, to), "transition"),
            now=now,
            snapshot=record.performance_snapshot,
        )
        self._lifecycle_log.append(event)
        logger.info(
            "StrategyEngine: %s %s -> %s (%s)",
            strategy_id,
            prev_status,
            to.value,
            reason or "",
        )
        return event

    # ── 选择 / 决策 ──

    def select_active(self) -> list[StrategyRecord]:
        """返回所有 ACTIVE 策略记录 (PC-02 消费其 target_weights)。"""
        return [r for r in self._records.values() if r.status == StrategyStatus.ACTIVE]

    def select_runnable(self) -> list[StrategyRecord]:
        """返回所有可运行策略 (TESTING + ACTIVE, 含模拟盘)。"""
        return [r for r in self._records.values() if r.status.is_runnable]

    def evaluate(
        self,
        strategy_id: str,
        universe: list[str],
        signals: dict[str, float],
        constraints: dict[str, Any] | None = None,
        now: datetime | None = None,
    ) -> StrategyDecision:
        """执行策略四维决策聚合, 产出 StrategyDecision。

        流程:
            1. 校验策略可运行 (TESTING/ACTIVE)
            2. 调用 StrategyBase.generate_target_weights() (B 类策略逻辑)
            3. 冷启动约束: 若处冷启动期, target_weights × cold_start_factor
            4. 归一化 target_weights
            5. 拆分 buy/sell 信号 (direction > 0 / < 0)
            6. 聚合为 StrategyDecision

        Args:
            strategy_id: 策略 ID
            universe: 选股宇宙
            signals: 信号 {symbol: strength}
            constraints: 约束 (透传给策略)
            now: 时间戳

        Returns:
            StrategyDecision

        Raises:
            StrategyNotFoundError: 策略未注册
            StrategyLifecycleError: 策略不可运行 (REGISTERED/DEPRECATED)
        """
        record = self._require(strategy_id)
        if not record.status.is_runnable:
            raise StrategyLifecycleError(f"strategy {strategy_id} not runnable (status={record.status.value})")

        now = now or self._clock()
        strategy = self._strategies[strategy_id]
        constraints = constraints or {}

        # 1. 调用策略生成目标权重 (B 类逻辑)
        raw_weights = strategy.generate_target_weights(universe, signals, constraints)

        # 2. 过滤宇宙外 + 非正权重
        target_weights = {sym: float(w) for sym, w in raw_weights.items() if sym in universe and float(w) > 0}

        # 3. 冷启动约束
        cold_start_active = self._in_cold_start(record, now)
        if cold_start_active:
            factor = self._config.cold_start_factor
            target_weights = {s: w * factor for s, w in target_weights.items()}

        # 4. 归一化 (Σw = 1, 容差内)
        target_weights = self._normalize_weights(target_weights)

        # 5. 拆分 buy/sell 信号
        buy_signals: list[StrategySignal] = []
        sell_signals: list[StrategySignal] = []
        for sym, strength in signals.items():
            if sym not in universe:
                continue
            direction = float(strength)
            if direction > 0:
                buy_signals.append(
                    StrategySignal(
                        symbol=sym,
                        dimension=DecisionDimension.BUY,
                        direction=direction,
                        strength=abs(direction),
                        weight=target_weights.get(sym, 0.0),
                    )
                )
            elif direction < 0:
                sell_signals.append(
                    StrategySignal(
                        symbol=sym,
                        dimension=DecisionDimension.SELL,
                        direction=direction,
                        strength=abs(direction),
                        weight=0.0,  # 卖出无目标权重
                    )
                )

        return StrategyDecision(
            strategy_id=strategy_id,
            target_weights=target_weights,
            selection_universe=list(universe),
            buy_signals=buy_signals,
            sell_signals=sell_signals,
            cold_start_active=cold_start_active,
            lifecycle_event=None,
            timestamp=now,
            idempotency_key=str(uuid.uuid4()),
        )

    # ── 退化检测 ──

    def detect_degradation(
        self,
        strategy_id: str,
        ic_history: list[float],
    ) -> bool:
        """策略退化检测: IC 衰减 > 阈值 → 退化。

        IC 衰减 = (历史均值 IC - 最近 IC) / 历史均值 IC。
        衰减 > ic_decay_threshold(0.5) → 判定退化。

        Args:
            strategy_id: 策略 ID
            ic_history: IC 时间序列 (旧→新)

        Returns:
            True=已退化
        """
        self._require(strategy_id)
        if len(ic_history) < 2:
            return False
        baseline = sum(ic_history[: max(1, len(ic_history) // 2)]) / max(1, len(ic_history) // 2)
        recent = ic_history[-1]
        if baseline <= 0:
            return False
        decay = (baseline - recent) / baseline
        degraded = decay > self._config.ic_decay_threshold
        if degraded:
            logger.warning(
                "StrategyEngine: %s degraded (IC decay=%.2f > %.2f)",
                strategy_id,
                decay,
                self._config.ic_decay_threshold,
            )
        return degraded

    def auto_degrade(
        self,
        strategy_id: str,
        ic_history: list[float],
        reason: str = "ic_decay",
    ) -> StrategyLifecycleEvent | None:
        """退化检测 + 自动降级 (ACTIVE→DEPRECATED)。

        Returns:
            生命周期事件 (未退化返回 None)
        """
        if not self.detect_degradation(strategy_id, ic_history):
            return None
        record = self._records.get(strategy_id)
        if record and record.status == StrategyStatus.ACTIVE:
            return self.transition(
                strategy_id,
                StrategyStatus.DEPRECATED,
                reason=reason,
                performance_snapshot={"ic_decay": self._compute_decay(ic_history)},
            )
        return None

    # ── 查询 ──

    def get_record(self, strategy_id: str) -> StrategyRecord | None:
        return self._records.get(strategy_id)

    def list_all(self) -> list[StrategyRecord]:
        return list(self._records.values())

    def count(self) -> int:
        return len(self._records)

    # ── 内部 ──

    def _require(self, strategy_id: str) -> StrategyRecord:
        record = self._records.get(strategy_id)
        if record is None:
            raise StrategyNotFoundError(f"strategy {strategy_id!r} not registered")
        return record

    def _get_meta(self, strategy: StrategyBase) -> StrategyMeta:
        # 优先实例级 _meta (允许实例覆盖, 测试/动态注入用), 其次类级 meta() classmethod
        m = getattr(strategy, "_meta", None)
        if m is None:
            m = strategy.meta()
        if m is None:
            raise StrategyLifecycleError(f"strategy {type(strategy).__name__} has no StrategyMeta")
        return m

    def _in_cold_start(self, record: StrategyRecord, now: datetime) -> bool:
        """判定策略是否处冷启动期 (ACTIVE 且距激活未满 cold_start_days)。"""
        if record.status != StrategyStatus.ACTIVE:
            return False
        if record.activated_at is None:
            return False
        if self._config.cold_start_days <= 0:
            return False
        elapsed = now - record.activated_at
        return elapsed < timedelta(days=self._config.cold_start_days)

    def _testing_period_satisfied(self, record: StrategyRecord) -> bool:
        """TESTING→ACTIVE 门禁: 测试期 ≥ min_testing_days。"""
        if self._config.min_testing_days <= 0:
            return True
        now = self._clock()
        elapsed = now - record.status_since
        return elapsed >= timedelta(days=self._config.min_testing_days)

    def _normalize_weights(self, weights: dict[str, float]) -> dict[str, float]:
        """归一化权重 (Σw=1); 全零返回空。"""
        total = sum(weights.values())
        if total <= self._config.target_weight_tolerance:
            return {}
        return {s: w / total for s, w in weights.items()}

    @staticmethod
    def _compute_decay(ic_history: list[float]) -> float:
        if len(ic_history) < 2:
            return 0.0
        baseline = sum(ic_history[: max(1, len(ic_history) // 2)]) / max(1, len(ic_history) // 2)
        if baseline <= 0:
            return 0.0
        return (baseline - ic_history[-1]) / baseline

    def _archive_record(self, record: StrategyRecord, reason: str, now: datetime) -> None:
        """版本变更时归档旧记录为 DEPRECATED (不复活)。"""
        prev = record.status.value
        record.status = StrategyStatus.DEPRECATED
        record.status_since = now
        event = self._make_event(
            strategy_id=record.strategy_id,
            previous=prev,
            new=StrategyStatus.DEPRECATED.value,
            reason=reason,
            now=now,
            snapshot=record.performance_snapshot,
        )
        self._lifecycle_log.append(event)

    def _make_event(
        self,
        strategy_id: str,
        previous: str,
        new: str,
        reason: str,
        now: datetime,
        snapshot: dict[str, float],
    ) -> StrategyLifecycleEvent:
        return StrategyLifecycleEvent(
            event_timestamp=now.isoformat(),
            event_type="lifecycle_transition",
            idempotency_key=str(uuid.uuid4()),
            new_status=new,
            previous_status=previous,
            reason=reason,
            strategy_id=strategy_id,
            triggered_by="strategy_engine",
            performance_snapshot=dict(snapshot) if snapshot else None,
            schema_version="1.0",
        )
