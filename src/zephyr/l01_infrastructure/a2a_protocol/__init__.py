# [BLUEPRINT] MOD-INF-025 | 03_modules/l01_infrastructure/a2a-protocol/blueprint.md | §
"""
L01 Infrastructure — A2A Protocol 模块 (MOD-INF-025)

三层五协议总架构:
  Layer 1 (发现+身份): Agent Card, AGENTS.md 注册, JWT 身份
  Layer 2 (通信+任务): Task 状态机, Message/Part Schema, 上下文包
  Layer 3 (协调+仲裁): Coordinator, Living Spec, 死锁防护
"""

from . import layer1_discovery
from . import layer2_communication
from . import layer3_coordination

from .a2a_card_registry import card_registry, A2ARegistry
from .multi_agent import (
    AgentCard,
    AgentRole,
    DispatchedTask,
    MergeStrategy,
    ResultMerge,
    TaskDispatch,
    TaskStatus,
)

__all__ = [
    'A2ARegistry',
    'AgentCard',
    'AgentRole',
    'DispatchedTask',
    'MergeStrategy',
    'ResultMerge',
    'TaskDispatch',
    'TaskStatus',
    'a2a_card_registry',
    'card_registry',
    'layer1_discovery',
    'layer2_communication',
    'layer3_coordination',
    'legacy_auditor',
    'legacy_governance_adapter',
    'legacy_protocol',
    'local_first_arch',
    'market_data_pipeline',
    'migration_strategy',
    'multi_agent',
    'MultiAgent',
    'multi_model_consensus',
    'offline_autonomy',
    'offline_resilience',
    'phase_hold',
    'prompt_lifecycle',
    'realtime_streaming',
]

__version__ = "0.10.0"