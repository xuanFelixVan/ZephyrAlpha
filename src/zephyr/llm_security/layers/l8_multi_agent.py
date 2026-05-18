# [BLUEPRINT] MOD-INF-014 | 03_modules/_cross_layer/llm-security/blueprint.md | §

# [MODULE] zephyr.llm_security.layers.l8_multi_agent

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

import hashlib
import hmac
import threading
import time
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

from pydantic import BaseModel, Field

from zephyr.llm_security.protocol import (
    LLMSecurityProtocol,
    SecurityContext,
    SecurityDecision,
    SecurityResult,
)


class TrustTier(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNTRUSTED = "untrusted"


class Scope(str, Enum):
    READ = "read"
    WRITE = "write"
    DELEGATE = "delegate"
    BROADCAST = "broadcast"
    NONE = "none"


class CrossAgentPermission(BaseModel):
    from_agent_id: str
    to_agent_id: str
    scope: Scope = Scope.READ
    granted: bool = False
    granted_at: float = Field(default_factory=time.time)
    expires_at: float = Field(default_factory=lambda: time.time() + 3600.0)
    trust_tier: TrustTier = TrustTier.LOW

    def is_expired(self) -> bool:
        return time.time() > self.expires_at


class AgentCommunicationItem(BaseModel):
    sender_id: str
    receiver_id: str
    content: str = ""
    token_count: int = 0
    intent: str = ""
    priority: int = 0
    signature: str = ""
    verified: bool = False
    timestamp: float = Field(default_factory=time.time)


class AgentIdentity(BaseModel):
    agent_id: str
    public_key_hash: str = ""
    attestation: str = ""
    verified: bool = False


class TrustScoreCalculator:
    """五维信任评分: 历史/(信息/任务)一致性/(意图/行为)一致性/身份强度/范围最小化."""

    _DIMENSIONS: List[str] = [
        "history",
        "message_consistency",
        "behavior_consistency",
        "identity_strength",
        "scope_minimization",
    ]

    _DEFAULT_WEIGHTS: Dict[str, float] = {
        "history": 0.25,
        "message_consistency": 0.25,
        "behavior_consistency": 0.20,
        "identity_strength": 0.15,
        "scope_minimization": 0.15,
    }

    def __init__(self):
        self._history_scores: Dict[str, List[float]] = {}
        self._lock = threading.Lock()

    def calculate(self, agent_id: str, dimension_scores: Dict[str, float]) -> Dict[str, Any]:
        total = 0.0
        weighted: Dict[str, float] = {}
        for dim in self._DIMENSIONS:
            raw = dimension_scores.get(dim, 0.5)
            weight = self._DEFAULT_WEIGHTS.get(dim, 0.2)
            w = raw * weight
            weighted[dim] = round(w, 3)
            total += w

        with self._lock:
            if agent_id not in self._history_scores:
                self._history_scores[agent_id] = []
            self._history_scores[agent_id].append(total)
            if len(self._history_scores[agent_id]) > 100:
                self._history_scores[agent_id] = self._history_scores[agent_id][-50:]

        tier = (
            TrustTier.HIGH
            if total >= 0.8
            else (TrustTier.MEDIUM if total >= 0.5 else (TrustTier.LOW if total >= 0.3 else TrustTier.UNTRUSTED))
        )

        return {
            "agent_id": agent_id,
            "total_score": round(total, 3),
            "tier": tier.value,
            "dimensions": weighted,
        }

    def get_history(self, agent_id: str) -> List[float]:
        return self._history_scores.get(agent_id, [])


class AgentIdentityResolver:
    """Agent身份验证—— 证明 + 签名验证."""

    def __init__(self, hmac_key: Optional[bytes] = None):
        self._hmac_key = hmac_key or hashlib.sha256(
            f"agent-identity-{time.time()}-{id(self)}".encode()
        ).digest()
        self._known_agents: Dict[str, AgentIdentity] = {}

    def register_agent(self, agent_id: str) -> AgentIdentity:
        identity = AgentIdentity(
            agent_id=agent_id,
            public_key_hash=hashlib.sha256(
                f"{agent_id}:{self._hmac_key.hex()[:16]}".encode()
            ).hexdigest()[:16],
        )
        self._known_agents[agent_id] = identity
        return identity

    def generate_attestation(self, agent_id: str) -> str:
        if agent_id not in self._known_agents:
            self.register_agent(agent_id)
        identity = self._known_agents[agent_id]
        attestation = hmac.new(
            self._hmac_key,
            f"{agent_id}:{identity.public_key_hash}:{int(time.time() // 300)}".encode(),
            hashlib.sha256,
        ).hexdigest()[:16]
        identity.attestation = attestation
        identity.verified = True
        return attestation

    def verify_attestation(self, agent_id: str, attestation: str) -> bool:
        if agent_id not in self._known_agents:
            return False
        identity = self._known_agents[agent_id]
        return hmac.compare_digest(identity.attestation, attestation)

    def sign_message(self, agent_id: str, message: str) -> str:
        return hmac.new(
            self._hmac_key,
            f"{agent_id}:{message}".encode(),
            hashlib.sha256,
        ).hexdigest()[:16]

    def verify_signature(self, agent_id: str, message: str, signature: str) -> bool:
        expected = self.sign_message(agent_id, message)
        return hmac.compare_digest(expected, signature)


class MultiAgentSecurityLayer(LLMSecurityProtocol):
    """L8 多Agent安全层 —— 跨Agent鉴权+通信隔离+身份验证+信任评分."""

    def __init__(self, hmac_key: Optional[bytes] = None):
        self._permissions: Dict[str, CrossAgentPermission] = {}
        self._trust_calculator = TrustScoreCalculator()
        self._identity_resolver = AgentIdentityResolver(hmac_key=hmac_key)
        self._comm_history: List[AgentCommunicationItem] = []
        self._lock = threading.Lock()

    def layer_name(self) -> str:
        return "l8_multi_agent"

    def layer_index(self) -> int:
        return 8

    async def evaluate(self, ctx: SecurityContext) -> SecurityResult:
        from_agent = ctx.metadata.get("from_agent_id", "")
        to_agent = ctx.metadata.get("to_agent_id", "")

        if from_agent and to_agent:
            allowed, reason = self.authenticate_cross_agent(
                from_agent=from_agent,
                to_agent=to_agent,
                scope=ctx.metadata.get("scope", "read"),
                content=ctx.raw_input,
            )
            if not allowed:
                return SecurityResult(
                    decision=SecurityDecision.DENY,
                    reason=reason,
                    layer_name=self.layer_name(),
                    score=0.0,
                )

        return SecurityResult(
            decision=SecurityDecision.ALLOW,
            reason="Cross-agent communication authorized",
            layer_name=self.layer_name(),
            score=0.8,
        )

    def authenticate_cross_agent(
        self,
        from_agent: str,
        to_agent: str,
        scope: str = "read",
        content: str = "",
    ) -> Tuple[bool, str]:
        perm_key = f"{from_agent}->{to_agent}"
        existing = self._permissions.get(perm_key)
        if existing and not existing.is_expired() and existing.granted:
            return True, "Existing permission valid"

        trust = self.evaluate_trust(from_agent, {"history": 0.7, "message_consistency": 0.8, "behavior_consistency": 0.7, "identity_strength": 0.6, "scope_minimization": 0.9})

        if trust["tier"] == TrustTier.UNTRUSTED.value:
            return False, f"Agent {from_agent} untrusted (score={trust['total_score']})"

        perm = CrossAgentPermission(
            from_agent_id=from_agent,
            to_agent_id=to_agent,
            scope=Scope(scope) if scope in [s.value for s in Scope] else Scope.READ,
            granted=True,
            trust_tier=TrustTier(trust["tier"]),
        )
        with self._lock:
            self._permissions[perm_key] = perm

        return True, f"Cross-agent permission granted, tier={trust['tier']}"

    def isolate_agent_communications(
        self, item: AgentCommunicationItem
    ) -> AgentCommunicationItem:
        sig = self._identity_resolver.sign_message(item.sender_id, item.content)
        item.signature = sig
        item.verified = self._identity_resolver.verify_signature(
            item.sender_id, item.content, sig
        )
        with self._lock:
            self._comm_history.append(item)
            if len(self._comm_history) > 1000:
                self._comm_history = self._comm_history[-500:]
        return item

    def evaluate_trust(
        self, agent_id: str, scores: Dict[str, float]
    ) -> Dict[str, Any]:
        return self._trust_calculator.calculate(agent_id, scores)

    @property
    def trust_calculator(self) -> TrustScoreCalculator:
        return self._trust_calculator

    @property
    def identity_resolver(self) -> AgentIdentityResolver:
        return self._identity_resolver

    @property
    def permissions(self) -> Dict[str, CrossAgentPermission]:
        return dict(self._permissions)

    @property
    def comm_history(self) -> List[AgentCommunicationItem]:
        return list(self._comm_history)
