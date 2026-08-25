# [BLUEPRINT] MOD-AU-006 | docs/03_modules/_domain_autonomy_core/per_agent_gate/blueprint.md
# [MODULE] zephyr.autonomy_core.per_agent_gate
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] MOD-INF-035(capability_card 规则集宿点) ; MOD-SEC-EVENTBUS(DENY 安全事件)
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] check 纯内存无IO同输入必同输出; 黑名单恒优先于白名单; 未登记agent fail-closed DENY; DENY经event_sink写安全事件且sink异常不阻断; 规则集frozen
# [MODIFY-GUARD] docs/03_modules/_domain_autonomy_core/per_agent_gate/blueprint.md
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] InvalidAgentGateConfigError
# [TESTS] tests/autonomy/test_per_agent_gate.py
# [A_module] module_id=MOD-AU-006 | layer=module | stability=evolving | safety=H | ai_autonomy=human_gated
# [TTL] permanent
"""PerAgentGate — 单 Agent 门控层 (MOD-AU-006)

CAND-AUTONOMYCORE-005（B11-02462）：规则集（允许动作 / 禁止动作 / 限额 / 时段）
内嵌 Agent Card（capability_card，MOD-INF-035），门控为纯内存规则匹配
（<0.1ms 无 IO）；DENY 经 ``event_sink`` 回调写安全事件（安全事件总线
MOD-SEC-EVENTBUS 为持久化委托，本模块不 import）。

与 A2A 检查网关（CAND-INFRAA2A-001）双层分工：本层管单 Agent 自约束，
网关管跨 Agent 通信；与 task_gate/stop_gate（任务级/停止级）互补。

判定序（短路）：①黑名单 DENY → ②白名单未命中 DENY → ③超限额 DENY →
④窗外 DENY → ⑤ALLOW。未登记 agent / 空 action → fail-closed DENY。
"""

from __future__ import annotations

import logging
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from enum import Enum
from typing import Final

from zephyr.shared.foundation.errors import ZephyrBaseError

_logger = logging.getLogger(__name__)

__all__: Final = [
    "AgentGateRuleSet",
    "AgentGateVerdict",
    "GateDecision",
    "InvalidAgentGateConfigError",
    "PerAgentGate",
    "TimeWindow",
]

_MINUTES_PER_DAY: Final[int] = 1440


class InvalidAgentGateConfigError(ZephyrBaseError):
    """Per-Agent Gate 规则集配置非法。"""


@dataclass(frozen=True)
class TimeWindow:
    """日内分钟窗 [start_min, end_min)（0<=start<end<=1440）。"""

    start_min: int
    end_min: int

    def __post_init__(self) -> None:
        if not (0 <= self.start_min < self.end_min <= _MINUTES_PER_DAY):
            raise InvalidAgentGateConfigError(
                f"时段窗非法: [{self.start_min}, {self.end_min})，须满足 0<=start<end<=1440"
            )

    def contains(self, minute: int) -> bool:
        return self.start_min <= minute < self.end_min


@dataclass(frozen=True)
class AgentGateRuleSet:
    """单 Agent 门控规则集（内嵌 Agent Card，不可变）。

    - allow_actions: 白名单（空集=不启用白名单）
    - deny_actions: 黑名单（恒优先于白名单；与白名单交集非空=配置矛盾）
    - max_notional_per_order: 单笔名义限额（None=不限）
    - allowed_windows: 日内分钟窗（空元组=全时段允许）
    """

    agent_id: str
    allow_actions: frozenset[str] = field(default_factory=frozenset)
    deny_actions: frozenset[str] = field(default_factory=frozenset)
    max_notional_per_order: float | None = None
    allowed_windows: tuple[TimeWindow, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.agent_id, str) or not self.agent_id.strip():
            raise InvalidAgentGateConfigError(f"agent_id 必须为非空字符串: {self.agent_id!r}")
        overlap = set(self.allow_actions) & set(self.deny_actions)
        if overlap:
            raise InvalidAgentGateConfigError(f"allow/deny 动作交集矛盾: {sorted(overlap)}")
        if self.max_notional_per_order is not None and self.max_notional_per_order < 0:
            raise InvalidAgentGateConfigError(f"max_notional_per_order 不能为负: {self.max_notional_per_order}")


class GateDecision(str, Enum):
    """门控判定。"""

    ALLOW = "allow"
    DENY = "deny"


@dataclass(frozen=True)
class AgentGateVerdict:
    """单次门控判定结果（不可变）。"""

    agent_id: str
    action: str
    decision: GateDecision
    matched_rule: str  # deny_actions/allow_actions/max_notional_per_order/allowed_windows/unregistered/invalid_input/pass
    reason: str
    fail_closed: bool = False

    @property
    def allowed(self) -> bool:
        return self.decision is GateDecision.ALLOW

    def to_security_event(self) -> dict[str, object]:
        """安全事件 dict（MOD-SEC-EVENTBUS 适配器消费的轻量契约）。"""
        return {
            "event_type": "PER_AGENT_GATE_DENY",
            "source_domain": "autonomy_core",
            "severity": "high",
            "agent_id": self.agent_id,
            "action": self.action,
            "matched_rule": self.matched_rule,
            "reason": self.reason,
            "fail_closed": self.fail_closed,
        }


class PerAgentGate:
    """单 Agent 门控层（纯内存规则匹配核心）。

    Args:
        rulesets: 初始规则集集合。
        event_sink: DENY 安全事件回调；异常不阻断 DENY 判定。
    """

    def __init__(
        self,
        rulesets: Iterable[AgentGateRuleSet] | None = None,
        event_sink: Callable[[dict[str, object]], None] | None = None,
    ) -> None:
        self._rules: dict[str, AgentGateRuleSet] = {}
        self._event_sink = event_sink
        for rs in rulesets or ():
            self.register(rs)

    def register(self, ruleset: AgentGateRuleSet) -> None:
        """登记规则集；重复登记同一 agent_id 拒绝。"""
        if not isinstance(ruleset, AgentGateRuleSet):
            raise InvalidAgentGateConfigError(f"ruleset 必须为 AgentGateRuleSet: {type(ruleset)!r}")
        if ruleset.agent_id in self._rules:
            raise InvalidAgentGateConfigError(f"agent 规则集已登记，禁止重复: {ruleset.agent_id}")
        self._rules[ruleset.agent_id] = ruleset

    def check(
        self,
        agent_id: str,
        action: str,
        *,
        notional: float | None = None,
        minute_of_day: int | None = None,
    ) -> AgentGateVerdict:
        """纯内存规则匹配（无 IO，同输入必同输出）。"""
        if not isinstance(agent_id, str) or not agent_id.strip() or not isinstance(action, str) or not action.strip():
            return self._deny(agent_id, action, "invalid_input", "agent_id/action 必须为非空字符串", fail_closed=True)
        rs = self._rules.get(agent_id)
        if rs is None:
            return self._deny(agent_id, action, "unregistered", "agent 未登记规则集，fail-closed 拦截", fail_closed=True)
        if action in rs.deny_actions:
            return self._deny(agent_id, action, "deny_actions", "动作命中黑名单")
        if rs.allow_actions and action not in rs.allow_actions:
            return self._deny(agent_id, action, "allow_actions", "动作不在白名单")
        if rs.max_notional_per_order is not None and notional is not None and notional > rs.max_notional_per_order:
            return self._deny(
                agent_id, action, "max_notional_per_order",
                f"单笔名义 {notional} 超限额 {rs.max_notional_per_order}",
            )
        if rs.allowed_windows and minute_of_day is not None and not any(w.contains(minute_of_day) for w in rs.allowed_windows):
            return self._deny(agent_id, action, "allowed_windows", f"分钟 {minute_of_day} 不在允许时段窗")
        return AgentGateVerdict(
            agent_id=agent_id, action=action, decision=GateDecision.ALLOW,
            matched_rule="pass", reason="规则全通过",
        )

    def _deny(self, agent_id: str, action: str, rule: str, reason: str, *, fail_closed: bool = False) -> AgentGateVerdict:
        verdict = AgentGateVerdict(
            agent_id=agent_id, action=action, decision=GateDecision.DENY,
            matched_rule=rule, reason=reason, fail_closed=fail_closed,
        )
        if self._event_sink is not None:
            try:
                self._event_sink(verdict.to_security_event())
            except Exception:  # noqa: BLE001 — sink 异常不阻断 DENY（留痕降级）
                _logger.exception("event_sink 异常（已降级，DENY 判定不受影响）")
        return verdict
