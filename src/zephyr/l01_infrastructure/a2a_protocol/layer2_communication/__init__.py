"""Layer 2: 通信+任务 — Task 状态机, Message/Part Schema, 上下文包"""

from .a2a_schemas import A2AMessage, A2AMessagePart, PartType
from .a2a_state import A2ATask, A2ATaskStatus, A2AStateMachine
from .message_router import MessageRouter
from .context_package import ContextPackage
from .handoff_manager import HandoffRecord, HandoffManager
from .push_notifier import PushNotifier

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