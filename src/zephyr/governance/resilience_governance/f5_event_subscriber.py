# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §3
# [MODULE] zephyr.governance.resilience_governance.f5_event_subscriber
# [DOMAIN]
# [DEPENDENCIES]
# [CONSUMERS] zephyr.governance.f5_boot_integration; zephyr.trading.boot_hooks; zephyr.trading.feedback_loop.scheduler
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] subscribe is idempotent; handle_event never raises; unsubscribe_all restores clean state; rule bindings are deterministic
# [MODIFY-GUARD] F5 event topic names must be "f5.deadlock_detected" / "f5.escalation_needed" / "f5.conflict_detected"; rule binding map keys must match RuleCategory enum values
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] returns SubscriptionResult; handle_event swallows all exceptions and logs; never raises during event dispatch
# [TESTS] tests/test_f5_event_startup.py
# [A_module] module_id=MOD-RES_f5_event_subscriber | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
F5EventSubscriber — F5 事件启动机制 (MOD-INF-022 §3).

将 F5 四组件 (EscalationEngine + DelegationEngine + DeadlockDetector + Arbitrator)
接入 EventBus 事件驱动:

1. EventBus 订阅 F5 相关事件:
   - f5.deadlock_detected → 触发 DeadlockDetector.break_deadlock
   - f5.escalation_needed → 触发 EscalationEngine.evaluate
   - f5.conflict_detected → 触发 Arbitrator.arbitrate
2. 规则引擎绑定: RuleCategory → 处理器映射 (deadlock/conflict/escalation)
3. FeedbackLoop 集成: 事件驱动产生 EvolutionProposal
4. A2A Protocol 事件驱动响应: 冲突事件触发仲裁

用法:
    from zephyr.governance.f5_event_subscriber import F5EventSubscriber
    subscriber = F5EventSubscriber()
    subscriber.bind_components(escalation_engine, delegation_engine,
                                deadlock_detector, arbitrator)
    subscriber.subscribe_all()  # 订阅 F5 事件到 EventBus
    # 事件发布后自动触发处理器
    subscriber.unsubscribe_all()  # 清理订阅
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any

from zephyr.shared.events.event_bus import EventBusBackpressure, EventPriority, bus as default_bus

logger = logging.getLogger(__name__)


# ── F5 事件主题常量 ──────────────────────────────────────────────────────

TOPIC_DEADLOCK_DETECTED = "f5.deadlock_detected"
TOPIC_ESCALATION_NEEDED = "f5.escalation_needed"
TOPIC_CONFLICT_DETECTED = "f5.conflict_detected"

F5_EVENT_TOPICS: tuple[str, ...] = (
    TOPIC_DEADLOCK_DETECTED,
    TOPIC_ESCALATION_NEEDED,
    TOPIC_CONFLICT_DETECTED,
)


# ── 数据结构 ─────────────────────────────────────────────────────────────


@dataclass
class SubscriptionResult:
    """订阅操作结果。"""
    success: bool
    topic: str
    handler_name: str
    error: str = ""


@dataclass
class EventHandlerResult:
    """事件处理器执行结果。"""
    handled: bool
    topic: str
    action: str
    success: bool
    details: dict = field(default_factory=dict)
    error: str = ""


@dataclass
class RuleBinding:
    """规则引擎绑定 — RuleCategory → 处理器名称映射。"""
    category: str
    topic: str
    handler_name: str
    priority: EventPriority = EventPriority.HIGH


# 默认规则绑定表 (RuleCategory → F5 事件主题 + 处理器)
DEFAULT_RULE_BINDINGS: list[RuleBinding] = [
    RuleBinding(
        category="deadlock",
        topic=TOPIC_DEADLOCK_DETECTED,
        handler_name="handle_deadlock",
        priority=EventPriority.HIGH,
    ),
    RuleBinding(
        category="custom",
        topic=TOPIC_ESCALATION_NEEDED,
        handler_name="handle_escalation",
        priority=EventPriority.HIGH,
    ),
    RuleBinding(
        category="security_violation",
        topic=TOPIC_CONFLICT_DETECTED,
        handler_name="handle_conflict",
        priority=EventPriority.HIGH,
    ),
]


class F5EventSubscriber:
    """F5 事件订阅器 — 将 F5 组件绑定到 EventBus 事件驱动。

    职责:
    1. 订阅 EventBus 上的 F5 事件主题
    2. 事件到达时调用对应 F5 组件处理器 (规则引擎绑定)
    3. 与 FeedbackLoop 集成产生 EvolutionProposal
    4. A2A Protocol 冲突事件触发 Arbitrator 仲裁

    线程安全: EventBus 自带锁, 本类不需要额外锁。
    """

    def __init__(
        self,
        event_bus: EventBusBackpressure | None = None,
        rule_bindings: list[RuleBinding] | None = None,
    ) -> None:
        self._bus: EventBusBackpressure = event_bus if event_bus is not None else default_bus
        self._rule_bindings: list[RuleBinding] = list(rule_bindings) if rule_bindings else list(DEFAULT_RULE_BINDINGS)
        self._escalation_engine: Any = None
        self._delegation_engine: Any = None
        self._deadlock_detector: Any = None
        self._arbitrator: Any = None
        self._feedback_loop: Any = None
        self._subscribed_topics: set[str] = set()
        self._handler_registry: dict[str, Any] = {}
        self._dispatch_log: list[EventHandlerResult] = []
        self._max_log_entries: int = 200
        self._register_handlers()

    def _register_handlers(self) -> None:
        """注册内部处理器到查找表。"""
        self._handler_registry = {
            TOPIC_DEADLOCK_DETECTED: self.handle_deadlock,
            TOPIC_ESCALATION_NEEDED: self.handle_escalation,
            TOPIC_CONFLICT_DETECTED: self.handle_conflict,
        }

    def bind_components(
        self,
        escalation_engine: Any = None,
        delegation_engine: Any = None,
        deadlock_detector: Any = None,
        arbitrator: Any = None,
    ) -> None:
        """绑定 F5 四组件 (来自 F5BootIntegration.on_startup)。"""
        if escalation_engine is not None:
            self._escalation_engine = escalation_engine
        if delegation_engine is not None:
            self._delegation_engine = delegation_engine
        if deadlock_detector is not None:
            self._deadlock_detector = deadlock_detector
        if arbitrator is not None:
            self._arbitrator = arbitrator
        logger.info(
            "F5EventSubscriber: components bound (esc=%s, del=%s, ddl=%s, arb=%s)",
            self._escalation_engine is not None,
            self._delegation_engine is not None,
            self._deadlock_detector is not None,
            self._arbitrator is not None,
        )

    def bind_feedback_loop(self, feedback_loop: Any) -> None:
        """绑定 FeedbackLoop 用于事件驱动反馈。"""
        self._feedback_loop = feedback_loop
        logger.info("F5EventSubscriber: FeedbackLoop bound")

    def subscribe_all(self) -> list[SubscriptionResult]:
        """订阅所有 F5 事件主题 (幂等)。

        返回每个主题的订阅结果列表。
        """
        results: list[SubscriptionResult] = []
        for binding in self._rule_bindings:
            if binding.topic in self._subscribed_topics:
                results.append(SubscriptionResult(
                    success=True,
                    topic=binding.topic,
                    handler_name=binding.handler_name,
                    error="already_subscribed",
                ))
                continue
            handler = self._handler_registry.get(binding.topic)
            if handler is None:
                results.append(SubscriptionResult(
                    success=False,
                    topic=binding.topic,
                    handler_name=binding.handler_name,
                    error="no_handler_registered",
                ))
                continue
            try:
                self._bus.subscribe(binding.topic, handler)
                self._subscribed_topics.add(binding.topic)
                results.append(SubscriptionResult(
                    success=True,
                    topic=binding.topic,
                    handler_name=binding.handler_name,
                ))
                logger.info("F5EventSubscriber: subscribed to '%s'", binding.topic)
            except Exception as e:
                results.append(SubscriptionResult(
                    success=False,
                    topic=binding.topic,
                    handler_name=binding.handler_name,
                    error=str(e),
                ))
                logger.error("F5EventSubscriber: subscribe failed for '%s': %s", binding.topic, e, exc_info=True)
        return results

    def unsubscribe_all(self) -> int:
        """取消所有 F5 事件订阅。返回取消数量。"""
        count = 0
        for topic in list(self._subscribed_topics):
            handler = self._handler_registry.get(topic)
            if handler is None:
                continue
            try:
                removed = self._bus.unsubscribe(topic, handler)
                if removed:
                    count += 1
            except Exception as e:
                logger.warning("F5EventSubscriber: unsubscribe failed for '%s': %s", topic, e, exc_info=True)
        self._subscribed_topics.clear()
        return count

    def is_subscribed(self, topic: str) -> bool:
        return topic in self._subscribed_topics

    # ── 事件处理器 (规则引擎绑定) ────────────────────────────────────────

    def handle_deadlock(self, event: Any) -> EventHandlerResult:
        """处理死锁事件 — 调用 DeadlockDetector.break_deadlock / preempt_lowest。

        事件 payload 期望字段:
        - node (str): 死锁节点 ID (可选, 缺省用 preempt_lowest)
        - cycle (list[str]): 死锁循环 (可选, 仅记录)
        """
        payload = self._extract_payload(event)
        node = payload.get("node")
        cycle = payload.get("cycle", [])
        result = EventHandlerResult(
            handled=False,
            topic=TOPIC_DEADLOCK_DETECTED,
            action="break_deadlock",
            success=False,
        )
        if self._deadlock_detector is None:
            result.error = "deadlock_detector not bound"
            self._log_dispatch(result)
            return result
        try:
            if node is not None:
                broken = self._deadlock_detector.break_deadlock(node)
                result.success = bool(broken)
                result.details["node"] = node
                result.details["broken"] = broken
            else:
                victim = self._deadlock_detector.preempt_lowest()
                result.success = victim is not None
                result.details["victim"] = victim
            if cycle:
                result.details["cycle"] = list(cycle)
            result.handled = True
            logger.info("F5EventSubscriber: deadlock handled (node=%s, victim=%s)", node, result.details.get("victim"))
        except Exception as e:
            result.error = str(e)
            result.handled = True
            logger.error("F5EventSubscriber: handle_deadlock failed: %s", e, exc_info=True)
        self._log_dispatch(result)
        self._notify_feedback_loop("deadlock", payload, result)
        return result

    def handle_escalation(self, event: Any) -> EventHandlerResult:
        """处理升级事件 — 调用 EscalationEngine.evaluate。

        事件 payload 期望字段:
        - category (str): RuleCategory 值 (默认 "custom")
        - description (str): 升级描述
        - owner_id (str): 责任人 ID
        """
        payload = self._extract_payload(event)
        category_str = payload.get("category", "custom")
        description = payload.get("description", "event-driven escalation")
        owner_id = payload.get("owner_id")
        result = EventHandlerResult(
            handled=False,
            topic=TOPIC_ESCALATION_NEEDED,
            action="evaluate",
            success=False,
        )
        if self._escalation_engine is None:
            result.error = "escalation_engine not bound"
            self._log_dispatch(result)
            return result
        try:
            from zephyr.governance.escalation.escalation_models import RuleCategory
            try:
                category = RuleCategory(category_str)
            except ValueError:
                category = RuleCategory.CUSTOM
            escalation_event = self._escalation_engine.evaluate(
                category=category,
                description=description,
                owner_id=owner_id,
            )
            result.success = escalation_event is not None
            result.details["event_id"] = getattr(escalation_event, "event_id", None)
            result.details["level"] = str(getattr(escalation_event, "level", ""))
            result.details["state"] = str(getattr(escalation_event, "state", ""))
            result.handled = True
            logger.info("F5EventSubscriber: escalation handled (event_id=%s)", result.details.get("event_id"))
        except Exception as e:
            result.error = str(e)
            result.handled = True
            logger.error("F5EventSubscriber: handle_escalation failed: %s", e, exc_info=True)
        self._log_dispatch(result)
        self._notify_feedback_loop("escalation", payload, result)
        return result

    def handle_conflict(self, event: Any) -> EventHandlerResult:
        """处理冲突事件 — 调用 Arbitrator.arbitrate (A2A Protocol 事件驱动响应)。

        事件 payload 期望字段:
        - agent_a (dict): {agent_id, role, session_age_minutes, tasks_completed}
        - agent_b (dict): 同上
        - conflicted_files (list[str]): 冲突文件列表
        """
        payload = self._extract_payload(event)
        agent_a_data = payload.get("agent_a", {})
        agent_b_data = payload.get("agent_b", {})
        conflicted_files = payload.get("conflicted_files", [])
        result = EventHandlerResult(
            handled=False,
            topic=TOPIC_CONFLICT_DETECTED,
            action="arbitrate",
            success=False,
        )
        if self._arbitrator is None:
            result.error = "arbitrator not bound"
            self._log_dispatch(result)
            return result
        try:
            from zephyr.infrastructure.a2a_protocol.layer3_coordination.arbitrator import (
                AgentMeta,
                AgentRole,
            )
            agent_a = self._build_agent_meta(agent_a_data, AgentRole)
            agent_b = self._build_agent_meta(agent_b_data, AgentRole)
            arbitration_result = self._arbitrator.arbitrate(
                agent_a=agent_a,
                agent_b=agent_b,
                conflicted_files=list(conflicted_files),
            )
            result.success = arbitration_result is not None
            result.details["winner"] = getattr(arbitration_result, "winner", None)
            result.details["loser"] = getattr(arbitration_result, "loser", None)
            result.details["tier"] = getattr(arbitration_result, "tier", 0)
            result.details["verdict"] = str(getattr(arbitration_result, "verdict", ""))
            result.details["escalation"] = bool(getattr(arbitration_result, "escalation", False))
            result.handled = True
            logger.info(
                "F5EventSubscriber: conflict handled (winner=%s, tier=%s)",
                result.details.get("winner"),
                result.details.get("tier"),
            )
        except Exception as e:
            result.error = str(e)
            result.handled = True
            logger.error("F5EventSubscriber: handle_conflict failed: %s", e, exc_info=True)
        self._log_dispatch(result)
        self._notify_feedback_loop("conflict", payload, result)
        return result

    @staticmethod
    def _build_agent_meta(data: dict, AgentRole: Any) -> Any:
        """从字典构建 AgentMeta (延迟导入避免循环依赖)。"""
        from zephyr.infrastructure.a2a_protocol.layer3_coordination.arbitrator import AgentMeta
        agent_id = data.get("agent_id", "unknown")
        role_str = data.get("role", "builder")
        try:
            role = AgentRole.from_string(role_str) if hasattr(AgentRole, "from_string") else AgentRole.BUILDER
        except Exception:
            role = AgentRole.BUILDER
        return AgentMeta(
            agent_id=agent_id,
            role=role,
            session_age_minutes=float(data.get("session_age_minutes", 0.0)),
            tasks_completed=int(data.get("tasks_completed", 0)),
            owned_files=list(data.get("owned_files", [])),
        )

    # ── FeedbackLoop 集成 ────────────────────────────────────────────────

    def _notify_feedback_loop(self, event_kind: str, payload: dict, result: EventHandlerResult) -> None:
        """通知 FeedbackLoop 生成 EvolutionProposal (事件驱动反馈)。"""
        if self._feedback_loop is None:
            return
        try:
            pending_entry = {
                "id": f"F5-{event_kind}-{int(time.time())}",
                "module": "f5_event_subscriber",
                "context": f"{event_kind} event: action={result.action} success={result.success}",
            }
            proposals = self._feedback_loop.generate_proposals([pending_entry])
            if proposals:
                for proposal in proposals:
                    self._feedback_loop.apply_proposal(proposal)
                logger.info(
                    "F5EventSubscriber: FeedbackLoop generated %d proposal(s) for '%s'",
                    len(proposals),
                    event_kind,
                )
        except Exception as e:
            logger.warning("F5EventSubscriber: FeedbackLoop notification failed: %s", e, exc_info=True)

    # ── 工具方法 ─────────────────────────────────────────────────────────

    @staticmethod
    def _extract_payload(event: Any) -> dict:
        """从 EventBus Event 或 dict 提取 payload (兼容多种事件格式)。"""
        if event is None:
            return {}
        if isinstance(event, dict):
            return event
        if isinstance(event, dict) is False and hasattr(event, "payload"):
            payload = getattr(event, "payload", None)
            if isinstance(payload, dict):
                return payload
            if payload is None:
                return {}
            try:
                return dict(payload)
            except Exception:
                return {"value": payload}
        try:
            return dict(event)
        except Exception:
            return {}

    def _log_dispatch(self, result: EventHandlerResult) -> None:
        """记录事件派发结果 (环形缓冲)。"""
        self._dispatch_log.append(result)
        if len(self._dispatch_log) > self._max_log_entries:
            self._dispatch_log = self._dispatch_log[-self._max_log_entries:]

    # ── 查询接口 ─────────────────────────────────────────────────────────

    @property
    def subscribed_topics(self) -> set[str]:
        return set(self._subscribed_topics)

    @property
    def rule_bindings(self) -> list[RuleBinding]:
        return list(self._rule_bindings)

    @property
    def dispatch_log(self) -> list[EventHandlerResult]:
        return list(self._dispatch_log)

    @property
    def escalation_engine(self) -> Any:
        return self._escalation_engine

    @property
    def delegation_engine(self) -> Any:
        return self._delegation_engine

    @property
    def deadlock_detector(self) -> Any:
        return self._deadlock_detector

    @property
    def arbitrator(self) -> Any:
        return self._arbitrator

    @property
    def feedback_loop(self) -> Any:
        return self._feedback_loop

    def get_stats(self) -> dict:
        """返回订阅器统计信息。"""
        return {
            "subscribed_topics": list(self._subscribed_topics),
            "rule_bindings_count": len(self._rule_bindings),
            "dispatch_log_count": len(self._dispatch_log),
            "components_bound": {
                "escalation_engine": self._escalation_engine is not None,
                "delegation_engine": self._delegation_engine is not None,
                "deadlock_detector": self._deadlock_detector is not None,
                "arbitrator": self._arbitrator is not None,
                "feedback_loop": self._feedback_loop is not None,
            },
        }

    def emit_deadlock_event(self, node: str | None = None, cycle: list[str] | None = None) -> bool:
        """便捷方法: 发布死锁事件到 EventBus。"""
        return self._bus.emit(
            TOPIC_DEADLOCK_DETECTED,
            {"node": node, "cycle": cycle or []},
            priority=EventPriority.HIGH,
        )

    def emit_escalation_event(
        self,
        category: str = "custom",
        description: str = "",
        owner_id: str | None = None,
    ) -> bool:
        """便捷方法: 发布升级事件到 EventBus。"""
        return self._bus.emit(
            TOPIC_ESCALATION_NEEDED,
            {"category": category, "description": description, "owner_id": owner_id},
            priority=EventPriority.HIGH,
        )

    def emit_conflict_event(
        self,
        agent_a: dict,
        agent_b: dict,
        conflicted_files: list[str] | None = None,
    ) -> bool:
        """便捷方法: 发布冲突事件到 EventBus (A2A Protocol 事件驱动)。"""
        return self._bus.emit(
            TOPIC_CONFLICT_DETECTED,
            {
                "agent_a": agent_a,
                "agent_b": agent_b,
                "conflicted_files": conflicted_files or [],
            },
            priority=EventPriority.HIGH,
        )


def create_f5_event_subscriber(
    escalation_engine: Any = None,
    delegation_engine: Any = None,
    deadlock_detector: Any = None,
    arbitrator: Any = None,
    feedback_loop: Any = None,
    event_bus: EventBusBackpressure | None = None,
) -> F5EventSubscriber:
    """模块级便捷函数: 创建 F5EventSubscriber 并绑定组件。"""
    subscriber = F5EventSubscriber(event_bus=event_bus)
    subscriber.bind_components(
        escalation_engine=escalation_engine,
        delegation_engine=delegation_engine,
        deadlock_detector=deadlock_detector,
        arbitrator=arbitrator,
    )
    if feedback_loop is not None:
        subscriber.bind_feedback_loop(feedback_loop)
    return subscriber


# ── §7.1 外部事件订阅 (DM-2507-C) ──────────────────────────────────────────

_subscribed = False


def subscribe_eventbus() -> None:
    """订阅 EventBusBackpressure 的4个外部事件。

    幂等：重复调用安全。供 boot_hooks 统一调用。
    事件: budget_exceeded / drift_detected / fix_completed / fix_failed
    """
    global _subscribed
    if _subscribed:
        return
    try:
        bus = default_bus
        bus.subscribe("budget_exceeded", _on_budget_exceeded)
        bus.subscribe("drift_detected", _on_drift_detected)
        bus.subscribe("fix_completed", _on_fix_completed)
        bus.subscribe("fix_failed", _on_fix_failed)
        _subscribed = True
        logger.info(
            "F5EventSubscriber: subscribed to 4 external events "
            "(budget_exceeded/drift_detected/fix_completed/fix_failed)"
        )
    except Exception as e:
        logger.warning("F5EventSubscriber: subscribe_eventbus failed: %s", e, exc_info=True)


def _on_budget_exceeded(payload: Any) -> None:
    """budget_exceeded 事件：预算超限触发升级评估。轻量handler。"""
    _dispatch_to_escalation(payload, "budget_exceeded")


def _on_drift_detected(payload: Any) -> None:
    """drift_detected 事件：漂移检测触发升级评估。轻量handler。"""
    _dispatch_to_escalation(payload, "drift_detected")


def _on_fix_completed(payload: Any) -> None:
    """fix_completed 事件：修复完成触发验证/升级。轻量handler。"""
    _dispatch_to_escalation(payload, "custom")


def _on_fix_failed(payload: Any) -> None:
    """fix_failed 事件：修复失败触发升级。轻量handler。"""
    _dispatch_to_escalation(payload, "custom")


def _dispatch_to_escalation(payload: Any, category: str) -> None:
    """将外部事件派发到 escalate_if_needed（已有公开方法）。"""
    try:
        from zephyr.governance.services.adapter import escalate_if_needed

        data = payload if isinstance(payload, dict) else {}
        description = data.get("detail", f"external event: {category}")
        owner_id = data.get("source_function", "")
        escalate_if_needed(
            operation_type=category,
            description=description,
            owner_id=owner_id,
        )
    except Exception as e:
        logger.warning("suppressed error in f5_event_subscriber", exc_info=True)


__all__ = [
    "F5EventSubscriber",
    "SubscriptionResult",
    "EventHandlerResult",
    "RuleBinding",
    "DEFAULT_RULE_BINDINGS",
    "F5_EVENT_TOPICS",
    "TOPIC_DEADLOCK_DETECTED",
    "TOPIC_ESCALATION_NEEDED",
    "TOPIC_CONFLICT_DETECTED",
    "create_f5_event_subscriber",
    "subscribe_eventbus",
]