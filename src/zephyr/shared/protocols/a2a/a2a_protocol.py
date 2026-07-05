# [BLUEPRINT] MOD-SHARED-001 | docs/03_modules/_domain-shared/protocols/blueprint.md
# [MODULE] zephyr.shared.protocols.a2a.a2a_protocol
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS] zephyr.shared.protocols.a2a; zephyr.infrastructure.a2a_protocol
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] no imports from zephyr.infrastructure or zephyr.trading; Protocol interfaces only
# [MODIFY-GUARD] interface changes require consumer audit
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] Protocol violations caught at type-check time
# [TESTS] tests/test_shared_protocols.py
# [A_module] module_id=MOD-SHR_a2a_protocol | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Core A2A Protocol interface and governance data contracts.

Defines the A2ACommunicationProtocol (typing.Protocol) for agent-to-agent
communication and the associated Pydantic data models for governance records.
"""

from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from typing import Any, Protocol, runtime_checkable

from pydantic import BaseModel, Field


class MessageType(str, Enum):
    QUERY = "QUERY"
    COMMAND = "COMMAND"
    NOTIFY = "NOTIFY"
    DELEGATE = "DELEGATE"
    RESPONSE = "RESPONSE"


class A2ACommunication(BaseModel):
    a2a_id: str
    from_agent_id: str
    to_agent_id: str
    message_type: MessageType = MessageType.QUERY
    payload_size: int = 0
    transfer_token_count: int = 0
    timestamp: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    status: str = "PENDING"


class SecurityContext:
    def __init__(self, agent_id: str = "", permissions: list[str] | None = None, security_level: int = 0):
        self.agent_id = agent_id
        self.permissions = permissions or []
        self.security_level = security_level


class SecurityDecision:
    def __init__(self, allowed: bool = True, reason: str = "", confidence: float = 1.0, policy: str = ""):
        self.allowed = allowed
        self.reason = reason
        self.confidence = confidence
        self.policy = policy


class SecurityResult:
    def __init__(
        self,
        decision: SecurityDecision | None = None,
        violations: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ):
        self.decision = decision
        self.violations = violations or []
        self.metadata = metadata or {}


@runtime_checkable
class A2ACommunicationProtocol(Protocol):
    """Protocol interface for A2A communication handlers.

    Any class that implements send_message and receive_message
    satisfies this protocol and can be used wherever A2A communication
    is required.
    """

    def send_message(self, message: A2ACommunication) -> bool: ...

    def receive_message(self, a2a_id: str) -> A2ACommunication | None: ...

    def get_status(self, a2a_id: str) -> str: ...
