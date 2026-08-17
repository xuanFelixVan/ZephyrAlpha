# [BLUEPRINT] MOD-TRIG-001 | docs/03_modules/_domain_trading/trigger_registry/blueprint.md
# [MODULE] zephyr.trading.trigger_registry
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.shared.event_bus(EventBus)
# [CONSUMERS] 41_buy_flow(买入触发器); 42_sell_flow(卖出触发器); 40_execution_broker(执行触发器); 35/36/37(风控触发器)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 优先级1-5(1最高); 冲突时高优先级覆盖; 同源去重(condition共享); cooldown防重复派发; 判定逻辑在各自spec域内
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] TriggerRegistrationError(ZA-TRIG-0001); TriggerConflictError(ZA-TRIG-0002)
# [TESTS] tests/trading/test_trigger_registry.py
# [A_module] module_id=MOD-TRIG-001 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


TriggerRegistry — 扳机清单注册与仲裁 (MOD-TRIG-001)

41_buy_flow §3.9 条件触发执行队列。买入/卖出/执行/风控触发器统一注册，
按优先级仲裁冲突、消除重复检测，由事件总线统一派发。

核心设计（41 §3.9）：
    - 注册格式：TriggerEntry(trigger_id/source/condition/action/priority/scope/cooldown)
    - 优先级仲裁：priority 升序取最高，同优先级按 scope（PORTFOLIO>STRATEGY>POSITION）
    - 同源去重：共享 condition 函数只算一次，按 trigger_id 分发到各自 action
    - 冷却期：防同触发器重复派发（默认 60s）

不做什么：不承载触发器判定逻辑（归各自 spec）/ 不引入新算法 /
         不改变三维度解耦（what/how much/how 仍在各自域内）

依据: 41_buy_flow §3.9 扳机清单
SSoT: depgraph MOD-TRIG-001
Version: 1.0.0

# [ALGO_FLOW]
# 输入: TriggerEntry 注册项（trigger_id/source/condition/action/priority/scope/cooldown_sec）
# 特征: 优先级 1-5, scope PORTFOLIO/STRATEGY/POSITION, cooldown_sec 冷却期
# 算法: register(注册) → evaluate_all(全量评估) → _resolve_conflicts(优先级仲裁) → dispatch(事件总线派发)
# 输出: 触发事件列表（按优先级排序），同源去重后分发

"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Callable, Final

# ── 常量（41 §3.9）──

# 默认冷却期（秒）
DEFAULT_COOLDOWN_SEC = 60

# 优先级范围
PRIORITY_MIN = 1  # 最高
PRIORITY_MAX = 5  # 最低

# scope 排序权重（同优先级时 PORTFOLIO > STRATEGY > POSITION）
SCOPE_ORDER: Final = {
    "PORTFOLIO": 0,
    "STRATEGY": 1,
    "POSITION": 2,
}


class TriggerRegistrationError(ValueError):
    """触发器注册错误（ZA-TRIG-0001）——trigger_id 重复或 priority 越界。

    继承 ValueError 保持向后兼容（调用方/测试按 ValueError 捕获仍生效）。
    """

    error_code = "ZA-TRIG-0001"


class TriggerConflictError(ValueError):
    """触发器冲突仲裁错误（ZA-TRIG-0002）——声明的错误契约锚点（供调用方定向捕获）。

    继承 ValueError 保持向后兼容。
    """

    error_code = "ZA-TRIG-0002"


# ── 数据契约（41 §3.9）──


@dataclass(frozen=True)
class TriggerEntry:
    """扳机清单注册项（41 §3.9 注册格式）。

    每个触发器一条注册项，判定逻辑在各自 spec 域内，
    扳机清单只做注册、优先级排序与派发。
    """

    trigger_id: str  # 唯一标识，如 "BUY_BATCH2_RELEASE" / "SELL_ATR_STOP" / "RISK_DRAWDOWN_L2"
    source_module: str  # "41" / "42" / "40" / "35" / "36" / "37"
    condition: Callable  # 判定函数，返回 bool（判定逻辑在各自 spec 内）
    action: str  # 触发动作，如 "PLACE_ORDER" / "CANCEL_BATCH" / "CLOSE_POSITION" / "HALT_NEW_BUY"
    priority: int  # 优先级 1(最高)-5(最低)，冲突时高优先级覆盖
    scope: str  # "POSITION" 单标的 / "STRATEGY" 策略级 / "PORTFOLIO" 组合级
    cooldown_sec: int = DEFAULT_COOLDOWN_SEC  # 冷却期，防同触发器重复派发


# ── 触发事件 ──


@dataclass(frozen=True)
class TriggeredEvent:
    """已触发事件（评估后产出）。"""

    trigger_id: str
    source_module: str
    action: str
    priority: int
    scope: str
    context: dict[str, Any] = field(default_factory=dict)


# ── 扳机清单注册表 ──


class TriggerRegistry:
    """扳机清单注册表（MOD-TRIG-001）。

    统一注册买入/卖出/执行/风控触发器，按优先级仲裁冲突、
    消除重复检测，由事件总线统一派发。

    MVP 阶段可降级为各模块独立轮询（41 §3.9 过度工程审查），
    Phase 2 多策略并发后强制启用。
    """

    def __init__(self) -> None:
        """初始化空注册表。"""
        self._entries: dict[str, TriggerEntry] = {}
        self._last_fired: dict[str, float] = {}  # trigger_id → 上次触发时间戳

    def register(self, entry: TriggerEntry) -> None:
        """注册触发器。

        Args:
            entry: 触发器注册项。

        Raises:
            ValueError: trigger_id 重复或 priority 越界。
        """
        if entry.trigger_id in self._entries:
            msg = f"trigger_id 重复注册: {entry.trigger_id}"
            raise TriggerRegistrationError(msg)
        if not PRIORITY_MIN <= entry.priority <= PRIORITY_MAX:
            msg = f"priority 越界 [{PRIORITY_MIN},{PRIORITY_MAX}]: {entry.priority}"
            raise TriggerRegistrationError(msg)
        self._entries[entry.trigger_id] = entry

    def unregister(self, trigger_id: str) -> None:
        """注销触发器。"""
        self._entries.pop(trigger_id, None)
        self._last_fired.pop(trigger_id, None)

    @property
    def entries(self) -> dict[str, TriggerEntry]:
        """只读访问注册表。"""
        return dict(self._entries)

    def evaluate_all(self, context: dict[str, Any] | None = None) -> list[TriggeredEvent]:
        """全量评估所有已注册触发器，返回触发事件列表（按优先级排序）。

        同源去重：共享 condition 函数的多个 trigger_id 只算一次，
        按 trigger_id 分发到各自 action（41 §3.9 去重规则）。

        Args:
            context: 评估上下文（传递给 condition 函数）。

        Returns:
            list[TriggeredEvent]: 触发事件列表，按优先级升序+scope 排序。
        """
        ctx = context or {}
        now = time.monotonic()
        fired: list[TriggeredEvent] = []
        evaluated_conditions: dict[int, bool] = {}  # id(condition) → result（同源去重）

        for entry in self._entries.values():
            # 冷却期检查
            last = self._last_fired.get(entry.trigger_id, 0.0)
            if now - last < entry.cooldown_sec:
                continue

            # 同源去重：同一 condition 函数只算一次
            cond_key = id(entry.condition)
            if cond_key not in evaluated_conditions:
                evaluated_conditions[cond_key] = entry.condition(ctx)

            if evaluated_conditions[cond_key]:
                fired.append(
                    TriggeredEvent(
                        trigger_id=entry.trigger_id,
                        source_module=entry.source_module,
                        action=entry.action,
                        priority=entry.priority,
                        scope=entry.scope,
                        context=ctx,
                    )
                )
                self._last_fired[entry.trigger_id] = now

        # 优先级仲裁：priority 升序（1最高），同优先级按 scope
        fired.sort(key=lambda e: (e.priority, SCOPE_ORDER.get(e.scope, 99)))
        return fired

    def resolve_conflicts(self, events: list[TriggeredEvent]) -> list[TriggeredEvent]:
        """冲突消解：同一标的同时触发多触发器时，按优先级仲裁。

        规则（41 §3.9）：
        - RISK_KILL_SWITCH（priority=1）无条件覆盖一切
        - SELL_BREAKOUT_FAIL（priority=3）> BUY_BATCH2_RELEASE（priority=5）
        - 止损暂停优先于加仓放行——风险优先原则

        Args:
            events: 触发事件列表。

        Returns:
            list[TriggeredEvent]: 消解后事件列表（含被覆盖事件的标记）。
        """
        if not events:
            return []

        # 检查是否有 priority=1 的 Kill Switch
        kill_switch_events = [e for e in events if e.priority == 1]
        if kill_switch_events:
            # Kill Switch 覆盖一切
            return kill_switch_events

        # 按 priority 升序取最高优先级
        best_priority = min(e.priority for e in events)
        best_events = [e for e in events if e.priority == best_priority]

        # 同优先级按 scope 排序
        best_events.sort(key=lambda e: SCOPE_ORDER.get(e.scope, 99))
        return best_events


# ── MVP 扳机清单（41 §3.9，按优先级排序）──
# 15 条注册项，condition 函数为占位符（判定逻辑在各自 spec 域内）


def _placeholder_condition(ctx: dict[str, Any]) -> bool:
    """占位 condition——实际判定逻辑在各自 spec 域内实现。"""
    return False


MVP_TRIGGER_LIST: Final = [
    # priority=1（最高，覆盖一切）
    {
        "trigger_id": "RISK_KILL_SWITCH",
        "source_module": "35",
        "action": "HALT_ALL",
        "priority": 1,
        "scope": "PORTFOLIO",
        "cooldown_sec": 0,
    },
    {
        "trigger_id": "RISK_DRAWDOWN_L4",
        "source_module": "35",
        "action": "CLOSE_ALL_NEW",
        "priority": 1,
        "scope": "PORTFOLIO",
        "cooldown_sec": 0,
    },
    # priority=2
    {
        "trigger_id": "RISK_DRAWDOWN_L3",
        "source_module": "35",
        "action": "HALT_NEW_BUY",
        "priority": 2,
        "scope": "PORTFOLIO",
        "cooldown_sec": 0,
    },
    {
        "trigger_id": "RISK_LIQUIDITY_CRISIS",
        "source_module": "37",
        "action": "HALT_NEW_BUY",
        "priority": 2,
        "scope": "PORTFOLIO",
        "cooldown_sec": 0,
    },
    {
        "trigger_id": "RISK_VAR_BREACH",
        "source_module": "36",
        "action": "REDUCE_POSITION_20PCT",
        "priority": 2,
        "scope": "PORTFOLIO",
        "cooldown_sec": 0,
    },
    # priority=3
    {
        "trigger_id": "SELL_BREAKOUT_FAIL",
        "source_module": "42→41",
        "action": "CANCEL_BATCH2",
        "priority": 3,
        "scope": "POSITION",
        "cooldown_sec": 60,
    },
    {
        "trigger_id": "SELL_SUPPORT_BREAK",
        "source_module": "42→41",
        "action": "CANCEL_ALL_BATCH",
        "priority": 3,
        "scope": "POSITION",
        "cooldown_sec": 60,
    },
    {
        "trigger_id": "SELL_CIRCUIT_BREAKER",
        "source_module": "42",
        "action": "HALT_STRATEGY",
        "priority": 3,
        "scope": "STRATEGY",
        "cooldown_sec": 300,
    },
    # priority=4
    {
        "trigger_id": "BUY_BREAKOUT_FAIL",
        "source_module": "41",
        "action": "CANCEL_BATCH2",
        "priority": 4,
        "scope": "POSITION",
        "cooldown_sec": 60,
    },
    {
        "trigger_id": "SELL_ATR_STOP",
        "source_module": "42",
        "action": "CLOSE_POSITION",
        "priority": 4,
        "scope": "POSITION",
        "cooldown_sec": 60,
    },
    {
        "trigger_id": "SELL_TRAILING_STOP",
        "source_module": "42",
        "action": "CLOSE_POSITION",
        "priority": 4,
        "scope": "POSITION",
        "cooldown_sec": 60,
    },
    {
        "trigger_id": "SELL_TAKE_PROFIT",
        "source_module": "42",
        "action": "CLOSE_POSITION",
        "priority": 4,
        "scope": "POSITION",
        "cooldown_sec": 60,
    },
    # priority=5（最低）
    {
        "trigger_id": "BUY_BATCH2_RELEASE",
        "source_module": "41",
        "action": "PLACE_ORDER",
        "priority": 5,
        "scope": "POSITION",
        "cooldown_sec": 60,
    },
    {
        "trigger_id": "EXE_MAKE_OR_TAKE",
        "source_module": "40",
        "action": "AMEND_TO_MARKET",
        "priority": 5,
        "scope": "POSITION",
        "cooldown_sec": 30,
    },
    {
        "trigger_id": "EXE_CANCEL_RATE",
        "source_module": "40",
        "action": "THROTTLE_ORDERS",
        "priority": 5,
        "scope": "STRATEGY",
        "cooldown_sec": 300,
    },
]


def create_mvp_registry() -> TriggerRegistry:
    """创建 MVP 扳机清单注册表（15 条，condition 为占位符）。

    实际使用时，各模块需将真实 condition 函数注入注册表。

    Returns:
        TriggerRegistry: 预注册 15 条 MVP 触发器的注册表。
    """
    registry = TriggerRegistry()
    for spec in MVP_TRIGGER_LIST:
        entry = TriggerEntry(
            trigger_id=spec["trigger_id"],
            source_module=spec["source_module"],
            condition=_placeholder_condition,
            action=spec["action"],
            priority=spec["priority"],
            scope=spec["scope"],
            cooldown_sec=spec["cooldown_sec"],
        )
        registry.register(entry)
    return registry
