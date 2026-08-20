# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.services.adapter
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__; zephyr.shared.event_bus
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-022 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""

Escalation Adapter — MOD-INF-022 统一集成入口.

Provides a single import point for any module to integrate with the escalation protocol.
Handles: level determination, circuit breaker, economic guard, delegation, audit.

Blueprint: docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md §2

Usage:
    from zephyr.governance.services.adapter import escalate_if_needed, check_operation

    result = escalate_if_needed(
        operation_type="security_violation",
        description="rm -rf /critical/path",
        owner_id="session-20260508-013",
    )
    if result.should_block:
        raise EscalationBlocked(result.reason)

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 升级评估参数（函数入参 str）
#   fields: operation_type 操作类型 + description 描述 + owner_id 责任人 + source_event_id 来源事件
#   code: adapter.py L119-124 escalate_if_needed 签名
# - id: I2
#   name: 操作审查参数（函数入参 str）
#   fields: operation 操作字符串 + target_path 目标路径 + session_id 会话
#   code: adapter.py L174-178 check_operation 签名
# - id: I3
#   name: EventBus 治理事件（事件对象）
#   fields: GATE_FAILED / SCOPE_DRIFT / TASK_FAILED 三类事件的 event_type + task_id + payload
#   code: adapter.py L206-210 事件映射表 + L244 订阅
# 层: 算法
# - id: A1
#   name_zh: ① 升级引擎评估与决策组装
#   name_en: escalate_if_needed
#   intro: 把一次操作交给升级引擎定级，折算成「阻不阻塞/要不要升级/委不委派」的决定
#   desc: 带锁懒加载 EscalationEngine 缓存（get_engine L94-111）→ OperationType 映射 RuleCategory（L136-137）→ engine.evaluate 定级 → 等级映射 should_block(L3/L4)/should_escalate/should_delegate(L2-L4)（L141-143）→ 拼 reason 含熔断与经济守卫状态（L148-152）→ 组装 EscalationDecision；引擎缺失或异常时透传不阻塞（L126-131, L165-171）
#   inputs: I1 A2 A3
#   outputs: EscalationDecision
#   invariant: 引擎不可用/评估异常时 should_block=False 透传放行
# - id: A2
#   name_zh: ② 危险操作模式匹配归类
#   name_en: check_operation
#   intro: 扫操作字符串里的危险关键词，先归类操作类型再转交引擎评估
#   desc: 12 条危险模式子串匹配（rm -rf/DROP/force_push/deadlock/budget:/timeout 等 L180-193），命中即归类 OperationType 否则 CUSTOM（L194-197），再调 escalate_if_needed（L199-203）
#   inputs: I2
#   outputs: 归类后转 A1 评估
# - id: A3
#   name_zh: ③ 事件总线自动订阅
#   name_en: auto_subscribe_eventbus
#   intro: 挂上 EventBus，3 类治理事件自动转成升级评估
#   desc: 订阅 GATE_FAILED/SCOPE_DRIFT/TASK_FAILED（L244-245）→ 回调按映射表转 OperationType（L230-232）→ 取 payload.description 调 escalate_if_needed（L236-240）；一次性订阅防重（_auto_subscribed L217-218）；EventBus 缺失时静默跳过（L249-252）
#   inputs: I3
#   outputs: 事件订阅注册 + 转 A1 评估
# 层: 输出
# - id: O1
#   name_zh: 升级决策结果
#   name_en: EscalationDecision
#   intro: 告诉调用方这个操作该不该拦、该不该升级给人审、建议委派给谁
#   invariant: 引擎不可用或评估异常时 should_block=False 透传放行
#   downstream: 治理域任意模块按需集成（MOD-INF-022 统一入口；文件头 [CONSUMERS] 为空）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A2
# I3 --> A3
# A2 --> A1
# A3 --> A1
# A1 --> O1
"""

from __future__ import annotations

import logging
import threading
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

_logger = logging.getLogger(__name__)


class OperationType(str, Enum):
    SECURITY_VIOLATION = "security_violation"
    DEADLOCK = "deadlock"
    BUDGET_EXCEEDED = "budget_exceeded"
    TIMEOUT = "timeout"
    AUTO_GUARD_FAILURE = "auto_guard_failure"
    DRIFT_DETECTED = "drift_detected"
    QUALITY_DEGRADATION = "quality_degradation"
    OWNER_ABSENT = "owner_absent"
    CASCADE_FAILURE = "cascade_failure"
    CUSTOM = "custom"


@dataclass
class EscalationDecision:
    operation: str
    should_block: bool = False
    should_escalate: bool = False
    should_delegate: bool = False
    escalation_level: str = "L0_SELF_HEAL"
    reason: str = ""
    suggested_delegate: str = ""
    economic_status: dict[str, Any] = field(default_factory=dict)
    circuit_state: str = "CLOSED"


_OPERATION_TO_CATEGORY = {
    OperationType.SECURITY_VIOLATION: "SECURITY_VIOLATION",
    OperationType.DEADLOCK: "DEADLOCK",
    OperationType.BUDGET_EXCEEDED: "BUDGET_EXCEEDED",
    OperationType.TIMEOUT: "TIMEOUT",
    OperationType.AUTO_GUARD_FAILURE: "AUTO_GUARD_FAILURE",
    OperationType.DRIFT_DETECTED: "DRIFT_DETECTED",
    OperationType.QUALITY_DEGRADATION: "QUALITY_DEGRADATION",
    OperationType.OWNER_ABSENT: "OWNER_ABSENT",
    OperationType.CASCADE_FAILURE: "CASCADE_FAILURE",
    OperationType.CUSTOM: "CUSTOM",
}

BLOCK_LEVELS = {"L3_CRITICAL", "L4_EMERGENCY"}
DELEGATE_LEVELS = {"L2_HUMAN_REVIEW", "L3_CRITICAL", "L4_EMERGENCY"}

_engine_cache: dict[str, Any] = {}
_cache_lock: threading.Lock | None = None


def get_engine(name: str = "adapter") -> object:
    global _cache_lock
    if name in _engine_cache:
        return _engine_cache[name]

    try:
        from threading import Lock

        from zephyr.governance.escalation.escalation_engine import EscalationEngine

        if _cache_lock is None:
            _cache_lock = Lock()
        with _cache_lock:
            if name not in _engine_cache:
                _engine_cache[name] = EscalationEngine(name)
        return _engine_cache[name]
    except ImportError:
        return None


def _get_engine(name: str = "adapter") -> object:
    """Backward-compatible thin wrapper; prefer :func:`get_engine`."""
    return get_engine(name)


def escalate_if_needed(
    operation_type: str,
    description: str,
    owner_id: str = "",
    source_event_id: str = "",
) -> EscalationDecision:
    engine = get_engine()
    if engine is None:
        return EscalationDecision(
            operation=operation_type,
            should_block=False,
            reason="Escalation engine not available — pass-through",
        )

    try:
        from zephyr.governance.escalation.escalation_models import RuleCategory

        cat_name = _OPERATION_TO_CATEGORY.get(OperationType(operation_type), "CUSTOM")
        category = getattr(RuleCategory, cat_name, RuleCategory.CUSTOM)

        ev = engine.evaluate(category, description, owner_id, source_event_id)
        level_name = ev.level.name
        should_block = level_name in BLOCK_LEVELS
        should_escalate = ev.level.value > 0 or ev.state.name == "REJECTED"
        should_delegate = level_name in DELEGATE_LEVELS

        economic = engine.get_economic_status()
        circuit = engine.get_circuit_state().name

        reason = f"Level={level_name}"
        if ev.circuit_breaker_triggered:
            reason += " | circuit_breaker=TRIGGERED"
        if not ev.economic_guard_passed:
            reason += " | economic_guard=FAILED"

        return EscalationDecision(
            operation=operation_type,
            should_block=should_block,
            should_escalate=should_escalate,
            should_delegate=should_delegate,
            escalation_level=level_name,
            reason=reason,
            economic_status=economic,
            circuit_state=circuit,
        )

    except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
        _logger.warning("escalation check failed: %s", exc, exc_info=True)
        return EscalationDecision(
            operation=operation_type,
            should_block=False,
            reason=f"Escalation check error: {exc} — pass-through",
        )


def check_operation(
    operation: str,
    target_path: str = "",
    session_id: str = "",
) -> EscalationDecision:
    op_type = OperationType.CUSTOM
    dangerous_patterns = [
        ("rm -rf", OperationType.SECURITY_VIOLATION),
        ("DROP", OperationType.SECURITY_VIOLATION),
        ("force_push", OperationType.SECURITY_VIOLATION),
        ("delete_from", OperationType.SECURITY_VIOLATION),
        ("shutdown", OperationType.SECURITY_VIOLATION),
        ("deadlock", OperationType.DEADLOCK),
        ("circular", OperationType.DEADLOCK),
        ("budget:", OperationType.BUDGET_EXCEEDED),
        ("timeout", OperationType.TIMEOUT),
        ("stuck", OperationType.TIMEOUT),
        ("owner absent", OperationType.OWNER_ABSENT),
        ("cascade", OperationType.CASCADE_FAILURE),
    ]
    for pattern, ot in dangerous_patterns:
        if pattern.lower() in operation.lower():
            op_type = ot
            break

    return escalate_if_needed(
        operation_type=op_type.value,
        description=f"{operation} | path={target_path}",
        owner_id=session_id,
    )


_EVENT_TYPE_TO_OPERATION = {
    "GATE_FAILED": OperationType.AUTO_GUARD_FAILURE,
    "SCOPE_DRIFT": OperationType.DRIFT_DETECTED,
    "TASK_FAILED": OperationType.CASCADE_FAILURE,
}

_auto_subscribed = False


def auto_subscribe_eventbus() -> None:
    global _auto_subscribed
    if _auto_subscribed:
        return

    try:
        from zephyr.shared.event_bus import EventBus, EventType

        bus = EventBus.get_instance()

        def _on_event(event: object) -> None:
            try:
                etype = getattr(event, "event_type", None)
                if etype is None:
                    return
                op_type = _EVENT_TYPE_TO_OPERATION.get(etype.name if hasattr(etype, "name") else str(etype))
                if op_type is None:
                    return
                task_id = getattr(event, "task_id", "unknown")
                payload = getattr(event, "payload", {})
                description = payload.get("description", f"EventBus auto: {etype}")
                escalate_if_needed(
                    operation_type=op_type.value,
                    description=description,
                    owner_id=task_id,
                )
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                _logger.warning(
                    "auto_subscribe_eventbus._on_event: event handling failed (%s: %s)",
                    type(e).__name__,
                    e,
                    exc_info=True,
                )

        for et in (EventType.GATE_FAILED, EventType.SCOPE_DRIFT, EventType.TASK_FAILED):
            bus.subscribe(et, _on_event)

        _auto_subscribed = True
        _logger.info("EscalationEngine auto-subscribed to EventBus (GATE_FAILED, SCOPE_DRIFT, TASK_FAILED)")
    except ImportError:
        _logger.debug("EventBus not available — escalation auto-subscribe skipped")
    except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
        _logger.debug("EventBus auto-subscribe failed — escalation remains manual", exc_info=True)
