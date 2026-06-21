# [A_module] module_id=MOD-SHR_a2a_registry | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-SHARED-001 | docs/03_modules/_domain-shared/protocols/blueprint.md
# [MODULE] zephyr.shared.protocols.a2a.a2a_registry
# [INVARIANTS] no imports from zephyr.infrastructure or zephyr.orchestration; Protocol interfaces and data contracts only
# [MODIFY-GUARD] interface changes require consumer audit
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS] zephyr.orchestration.agent_communication; zephyr.infrastructure.a2a_protocol
# [ERROR_CONTRACT] Protocol violations caught at type-check time; Pydantic validation on AgentCard
# [TESTS] tests/test_shared_protocols.py

"""A2A Registry and Agent Card contracts — discovery and identity interfaces.

Defines AgentCard (Pydantic data model), AgentCapability enum,
and Protocol interfaces for A2ARegistry and IdentityVerifier.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Protocol, runtime_checkable

from pydantic import BaseModel, Field


class AgentCapability(str, Enum):
    READ = "read"
    GREP = "grep"
    GLOB = "glob"
    WRITE = "write"
    BASH = "bash"
    SEARCH = "search"
    RECALL = "recall"


class AgentCard(BaseModel):
    agent_id: str = Field(..., pattern=r"^agent-[a-z0-9_-]+$")
    name: str
    description: str
    version: str = "0.1.0"
    capabilities: List[AgentCapability] = []
    skill_ids: List[str] = []
    model_preferences: List[str] = ["deepseek"]
    max_tasks: int = 5
    endpoint: Optional[str] = None
    public_key: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, str] = {}


@runtime_checkable
class A2ARegistryProtocol(Protocol):
    """Protocol interface for Agent Card registries.

    Any class that provides register, discover, get, and unregister
    satisfies this protocol.
    """

    def register(self, card: AgentCard) -> AgentCard:
        ...

    def discover(self, capability: Optional[str] = None) -> List[AgentCard]:
        ...

    def get(self, agent_id: str) -> Optional[AgentCard]:
        ...

    def unregister(self, agent_id: str) -> bool:
        ...


@runtime_checkable
class IdentityVerifierProtocol(Protocol):
    """Protocol interface for A2A identity verification.

    Any class that provides sign, verify, and generate_challenge
    satisfies this protocol.
    """

    def sign(self, agent_id: str, payload: Dict) -> str:
        ...

    def verify(self, agent_id: str, payload: Dict, signature: str) -> bool:
        ...

    def generate_challenge(self) -> str:
        ...
