# [A_module] module_id=MOD-INF_layer2_communication | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain-infra_ops/a2a-protocol/blueprint.md
# [MODULE] zephyr.infrastructure.a2a_protocol.layer2_communication
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS] 
# [ERROR_CONTRACT] 
# [TESTS] 
"""Layer 2: 通信+任务 — Task 状态机, Message/Part Schema, 上下文包"""
from zephyr.shared.protocols.a2a.a2a_schemas import (  # noqa: F401
    A2AMessage, A2AMessagePart, PartType,
    A2ATask, A2ATaskStatus, A2AStateMachine,
    ContextPackage,
    HandoffRecord, HandoffManagerProtocol, MessageRouterProtocol, PushNotifierProtocol,
)
from . import streaming  # noqa: F401
from . import a2a_schemas, a2a_state, context_package, handoff_manager  # noqa: F401
from . import push_notifier, trigger_monitor  # noqa: F401


def __getattr__(name):
    """Lazy import to avoid circular dependency."""
    _LAZY_IMPORTS = {
        'MessageRouter': ('.message_router', 'MessageRouter'),
        'HandoffManager': ('.handoff_manager', 'HandoffManager'),
        'PushNotifier': ('.push_notifier', 'PushNotifier'),
        'message_router': (None, 'message_router'),
    }
    if name in _LAZY_IMPORTS:
        mod_path, attr = _LAZY_IMPORTS[name]
        if mod_path is None:
            from . import message_router as _mr
            return _mr
        import importlib
        mod = importlib.import_module(mod_path, __package__)
        return getattr(mod, attr)
    raise AttributeError(f'module {__name__!r} has no attribute {name!r}')

__all__ = [
    'A2AMessage', 'A2AMessagePart', 'PartType',
    'A2ATask', 'A2ATaskStatus', 'A2AStateMachine',
    'MessageRouter',
    'ContextPackage',
    'HandoffRecord', 'HandoffManager',
    'PushNotifier',
    'a2a_schemas', 'a2a_state', 'context_package', 'handoff_manager',
    'message_router', 'push_notifier', 'streaming', 'trigger_monitor',
]

__version__ = "0.10.0"
