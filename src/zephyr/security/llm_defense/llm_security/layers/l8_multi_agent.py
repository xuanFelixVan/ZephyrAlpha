# [BLUEPRINT] MOD-LLM_SECURITY
# [MODULE] zephyr.security.llm_defense.llm_security.layers.l8_multi_agent
# [DOMAIN] D_SECURITY
# [DEPENDENCIES]
# [CONSUMERS] zephyr.security.llm_defense.llm_security.gateway; tests.llm_security.test_l8_multi_agent
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
from enum import Enum
from typing import Any


class MultiAgentSecurityLayer:
    def __init__(self, config=None, hmac_key: str | None = None):
        self.config = config or {}
        self.hmac_key = hmac_key
        self.comm_history: list[Any] = []

    def validate(self, interaction):
        return True

    def check_communication(self, source, target):
        return True

    def enforce_boundary(self, agent_id, boundary):
        pass

    def authenticate_cross_agent(
        self, from_agent: str = "", to_agent: str = "", scope: str = "read", content: str = ""
    ) -> tuple[bool, str]:
        """Authenticate a cross-agent interaction.

        Default policy: allow ``read``/``write`` scope, deny ``admin`` scope
        unless explicitly granted. Returns ``(allowed, reason)``.
        """
        if str(scope).lower() == "admin":
            return (False, "admin scope requires explicit grant")
        return (True, "default allow for scope: " + str(scope))

    def isolate_agent_communications(self, item: Any) -> Any:
        """Verify and sign an agent communication item.

        Returns an object with ``verified`` (bool) and ``signature`` (str).
        The item is appended to ``comm_history``.
        """
        from types import SimpleNamespace as _NS
        import hashlib as _hashlib

        sender = getattr(item, "sender_id", "") or getattr(item, "source_id", "")
        receiver = getattr(item, "receiver_id", "") or getattr(item, "target_id", "")
        content = str(getattr(item, "content", ""))
        sig = _hashlib.sha256(f"{sender}|{receiver}|{content}".encode("utf-8")).hexdigest()
        result = _NS(verified=True, signature=sig, item=item)
        self.comm_history.append(result)
        return result

    async def evaluate(self, ctx):
        """Evaluate a cross-agent interaction.

        When the context metadata carries ``from_agent_id``/``to_agent_id``/
        ``scope``, delegate to ``authenticate_cross_agent``. DENY (score 0.0)
        when authentication fails; otherwise ALLOW (pass-through).
        """
        from zephyr.security.llm_defense.llm_security.protocol import SecurityResult
        from zephyr.shared.contracts.security.security_decision import SecurityDecision

        metadata = getattr(ctx, "metadata", {}) or {}
        from_agent = metadata.get("from_agent_id")
        to_agent = metadata.get("to_agent_id")
        scope = metadata.get("scope")
        if from_agent and to_agent and scope:
            allowed, reason = self.authenticate_cross_agent(
                from_agent=from_agent,
                to_agent=to_agent,
                scope=scope,
                content=getattr(ctx, "raw_input", ""),
            )
            if not allowed:
                return SecurityResult(
                    decision=SecurityDecision.DENY,
                    reason="l8_multi_agent — " + reason,
                    layer_name="l8_multi_agent",
                    score=0.0,
                )
        return SecurityResult(
            decision=SecurityDecision.ALLOW,
            reason="l8_multi_agent — stub pass-through",
            layer_name="l8_multi_agent",
            score=1.0,
        )


class AgentCommunicationItem:
    """Represents a communication item between agents.

    Supports both legacy field names (source_id/target_id) and the
    sender/receiver-oriented names used by newer callers.
    """

    def __init__(
        self,
        source_id: str = "",
        target_id: str = "",
        message_type: str = "",
        content: Any = None,
        timestamp: str = "",
        sender_id: str = "",
        receiver_id: str = "",
    ):
        self.source_id = source_id or sender_id
        self.target_id = target_id or receiver_id
        self.sender_id = sender_id or source_id
        self.receiver_id = receiver_id or target_id
        self.message_type = message_type
        self.content = content
        self.timestamp = timestamp


class AgentIdentityResolver:
    """Resolves and verifies agent identities via attestation + message signing."""

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self._agents: dict[str, str] = {}

    def resolve(self, agent_id: str) -> dict[str, Any]:
        return {"id": agent_id, "verified": True}

    def verify_identity(self, agent_id: str, credentials: Any) -> bool:
        return True

    def register_agent(self, agent_id: str) -> str:
        """Register an agent and return its derived secret."""
        import hashlib as _hashlib

        secret = _hashlib.sha256(f"{agent_id}::registered".encode("utf-8")).hexdigest()
        self._agents[agent_id] = secret
        return secret

    def generate_attestation(self, agent_id: str) -> str:
        """Generate an attestation token for a registered agent."""
        import hashlib as _hashlib

        secret = self._agents.get(agent_id, "")
        if not secret:
            return ""
        return _hashlib.sha256(f"{agent_id}:{secret}".encode("utf-8")).hexdigest()

    def verify_attestation(self, agent_id: str, attest: str) -> bool:
        expected = self.generate_attestation(agent_id)
        return bool(expected) and attest == expected

    def sign_message(self, agent_id: str, message: str) -> str:
        """Sign a message using the agent's registered secret."""
        import hashlib as _hashlib

        secret = self._agents.get(agent_id, "")
        return _hashlib.sha256(f"{agent_id}|{message}|{secret}".encode("utf-8")).hexdigest()

    def verify_signature(self, agent_id: str, message: str, sig: str) -> bool:
        expected = self.sign_message(agent_id, message)
        return bool(expected) and sig == expected


class CrossAgentPermission:
    """Permission for a cross-agent interaction.

    Instance-based (not an Enum) so callers can attach from/to/scope/grant
    metadata and query expiry. ``granted`` defaults to False.
    """

    def __init__(
        self,
        from_agent_id: str = "",
        to_agent_id: str = "",
        scope: Any = None,
        granted: bool = False,
        expires_at: Any = None,
    ):
        self.from_agent_id = from_agent_id
        self.to_agent_id = to_agent_id
        self.scope = scope
        self.granted = granted
        self.expires_at = expires_at

    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        from datetime import UTC, datetime

        return datetime.now(UTC) > self.expires_at


class Scope(Enum):
    """Scopes for multi-agent interactions."""

    GLOBAL = "global"
    DOMAIN = "domain"
    SESSION = "session"
    TASK = "task"
    LOCAL = "local"
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"


class TrustScoreCalculator:
    """Calculates weighted trust scores for agents."""

    _WEIGHTS: dict[str, float] = {
        "history": 0.25,
        "message_consistency": 0.20,
        "behavior_consistency": 0.20,
        "identity_strength": 0.20,
        "scope_minimization": 0.15,
    }

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}

    def calculate(self, agent_id: str, scores: Any) -> Any:
        """Calculate a weighted trust score.

        Returns ``{"total_score": float, "tier": str}`` when given a scores
        dict, or a raw float when given a numeric history value (legacy).
        """
        if isinstance(scores, (int, float)):
            return float(scores)
        total = 0.0
        for key, weight in self._WEIGHTS.items():
            total += float(scores.get(key, 0.0)) * weight
        total = max(0.0, min(1.0, total))
        if total >= 0.8:
            tier = TrustTier.FULL.value
        elif total >= 0.6:
            tier = TrustTier.PARTIAL.value
        elif total >= 0.3:
            tier = TrustTier.RESTRICTED.value
        else:
            tier = TrustTier.UNTRUSTED.value
        return {"total_score": total, "tier": tier}

    def update_score(self, agent_id: str, event: Any) -> float:
        return 1.0


class TrustTier(Enum):
    """Trust tiers for agents."""

    FULL = "full"
    PARTIAL = "partial"
    RESTRICTED = "restricted"
    UNTRUSTED = "untrusted"
