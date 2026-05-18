# [BLUEPRINT] MOD-INF-014 | 03_modules/_cross_layer/llm-security/blueprint.md | §

# [MODULE] zephyr.llm_security.layers.l4_agent

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
import re
import time
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

from pydantic import BaseModel, Field, field_validator

from zephyr.llm_security.protocol import (
    LLMSecurityProtocol,
    SecurityContext,
    SecurityDecision,
    SecurityResult,
)


class AgentPermission(str, Enum):
    READ_ONLY = "read_only"
    WRITE_SAFE = "write_safe"
    WRITE_CRITICAL = "write_critical"
    ADMIN = "admin"


class RiskLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ApprovalOutcome(str, Enum):
    APPROVED = "approved"
    DENIED = "denied"
    PENDING = "pending"


class FJThreat(str, Enum):
    FJ1_INSIDER_TRADING = "insider_trading"
    FJ2_CONFIRMATION_BIAS = "confirmation_bias"
    FJ3_MARKET_HALLUCINATION = "market_hallucination"
    FJ4_MARKET_INJECTION = "market_injection"
    FJ5_MARKET_TIMING = "market_timing"
    FJ6_CASCADING_ERROR = "cascading_error"


class ToolCallAuthorization(BaseModel):
    tool_name: str
    permission_required: AgentPermission
    granted: bool = False
    risk: RiskLevel = RiskLevel.LOW
    reason: str = ""
    session_id: str = ""
    params_snapshot: Dict[str, Any] = Field(default_factory=dict)
    timestamp: float = Field(default_factory=time.time)

    @field_validator("granted", mode="before")
    @classmethod
    def coerce_granted(cls, v: Any) -> bool:
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes")
        return bool(v)


class ApprovalRequest(BaseModel):
    request_id: str
    tool_name: str
    params: Dict[str, Any] = Field(default_factory=dict)
    risk: RiskLevel
    justification: str = ""
    outcome: ApprovalOutcome = ApprovalOutcome.PENDING
    requested_at: float = Field(default_factory=time.time)
    resolved_at: Optional[float] = None


_TOOL_RISK_MAP: Dict[str, Tuple[AgentPermission, RiskLevel]] = {
    "read_file": (AgentPermission.READ_ONLY, RiskLevel.LOW),
    "list_directory": (AgentPermission.READ_ONLY, RiskLevel.LOW),
    "search_codebase": (AgentPermission.READ_ONLY, RiskLevel.LOW),
    "grep": (AgentPermission.READ_ONLY, RiskLevel.LOW),
    "glob": (AgentPermission.READ_ONLY, RiskLevel.LOW),
    "web_search": (AgentPermission.READ_ONLY, RiskLevel.MEDIUM),
    "web_fetch": (AgentPermission.READ_ONLY, RiskLevel.MEDIUM),
    "write_file": (AgentPermission.WRITE_SAFE, RiskLevel.MEDIUM),
    "search_replace": (AgentPermission.WRITE_SAFE, RiskLevel.MEDIUM),
    "delete_file": (AgentPermission.WRITE_CRITICAL, RiskLevel.HIGH),
    "run_command": (AgentPermission.WRITE_CRITICAL, RiskLevel.HIGH),
    "git_commit": (AgentPermission.WRITE_CRITICAL, RiskLevel.HIGH),
    "git_push": (AgentPermission.WRITE_CRITICAL, RiskLevel.HIGH),
    "deploy_service": (AgentPermission.ADMIN, RiskLevel.HIGH),
    "modify_config": (AgentPermission.ADMIN, RiskLevel.HIGH),
    "grant_permission": (AgentPermission.ADMIN, RiskLevel.HIGH),
}

_FINANCIAL_KEYWORDS: Dict[FJThreat, List[str]] = {
    FJThreat.FJ1_INSIDER_TRADING: [
        "insider", "non-public", "material information", "before earnings",
        "before announcement", "confidential", "未公开", "内幕", "内线",
        "重大非公开", "提前知道",
    ],
    FJThreat.FJ2_CONFIRMATION_BIAS: [
        "confirm my bias", "prove my investment", "justify my position",
        "validate my thesis", "support my view", "确认我的", "证明我的投资",
    ],
    FJThreat.FJ3_MARKET_HALLUCINATION: [
        "stock price prediction", "guaranteed return", "risk-free",
        "market forecast", "price target", "guarantee", "股票预测",
        "保证收益", "无风险", "绝对涨",
    ],
    FJThreat.FJ4_MARKET_INJECTION: [
        "fake news about", "pump", "dump", "short squeeze",
        "manipulate", "distort", "假新闻", "操纵市场", "拉高出货",
    ],
    FJThreat.FJ5_MARKET_TIMING: [
        "best time to buy", "best time to sell", "market top",
        "market bottom", "timing the market", "最佳买入", "最佳卖出",
        "抄底", "逃顶", "精准时机",
    ],
    FJThreat.FJ6_CASCADING_ERROR: [
        "chain reaction", "domino effect", "automated trading cascade",
        "recursive trade", "连锁反应", "多米诺", "自动交易链",
        "递归交易",
    ],
}

_CRITICAL_PARAM_PATTERNS: List[Tuple[str, re.Pattern]] = [
    ("system_command", re.compile(r"\b(rm\s+-rf|del\s+/[fsq]|format\s+|mkfs\.)")),
    ("path_traversal", re.compile(r"(\.\.[/\\]|~[/\\]|/etc/passwd|C:\\Windows)")),
    ("url_redirect", re.compile(r"(redirect|forward).*?(http|ftp|//)")),
    ("code_injection", re.compile(r"(eval|exec|subprocess|os\.system|__import__)\s*\(")),
]


class FinancialComplianceGate:
    """FJ1-FJ6 金融合规六类威胁门禁."""

    _FLAG_WEIGHTS: Dict[FJThreat, float] = {
        FJThreat.FJ1_INSIDER_TRADING: 1.0,
        FJThreat.FJ2_CONFIRMATION_BIAS: 0.6,
        FJThreat.FJ3_MARKET_HALLUCINATION: 0.9,
        FJThreat.FJ4_MARKET_INJECTION: 1.0,
        FJThreat.FJ5_MARKET_TIMING: 0.7,
        FJThreat.FJ6_CASCADING_ERROR: 0.8,
    }

    def scan(self, text: str) -> Dict[str, Any]:
        findings: Dict[str, List[str]] = {}
        total_score = 0.0
        text_lower = text.lower()
        for threat, keywords in _FINANCIAL_KEYWORDS.items():
            matches: List[str] = []
            for kw in keywords:
                if kw.lower() in text_lower:
                    matches.append(kw)
            if matches:
                findings[threat.value] = matches
                total_score += self._FLAG_WEIGHTS.get(threat, 0.5) * len(matches)

        violation_count = len(findings)
        blocked = total_score >= 0.9 or violation_count >= 1
        return {
            "blocked": blocked,
            "score": round(total_score, 2),
            "violations": violation_count,
            "findings": findings,
        }


class LongHorizonAgentDefender:
    """长时期Agent执行攻击防御."""

    def __init__(self, decay_threshold: float = 0.3, max_tool_chain_length: int = 20):
        self._decay_threshold = decay_threshold
        self._max_tool_chain_length = max_tool_chain_length
        self._intent_history: List[Tuple[str, float]] = []
        self._tool_chain: List[str] = []
        self._session_start: float = time.time()

    def check_intent_consistency(self, current_intent: str) -> Dict[str, Any]:
        if not self._intent_history:
            self._intent_history.append((current_intent, time.time()))
            return {"consistent": True, "drift": 0.0}

        last_intent, _ = self._intent_history[-1]
        common = len(set(current_intent.split()) & set(last_intent.split()))
        total = max(len(set(current_intent.split())), 1)
        drift = 1.0 - (common / total)

        self._intent_history.append((current_intent, time.time()))
        if len(self._intent_history) > 50:
            self._intent_history = self._intent_history[-50:]

        return {"consistent": drift < 0.6, "drift": round(drift, 3)}

    def check_tool_chaining_anomaly(self, tool_name: str) -> Dict[str, Any]:
        self._tool_chain.append(tool_name)
        if len(self._tool_chain) > self._max_tool_chain_length:
            return {
                "anomaly": True,
                "reason": f"Tool chain length {len(self._tool_chain)} exceeds max {self._max_tool_chain_length}",
            }

        recent = self._tool_chain[-10:]
        if len(recent) >= 5 and len(set(recent)) == 1:
            return {
                "anomaly": True,
                "reason": f"Repetitive tool calls: {recent[0]} repeated {len(recent)} times",
            }

        return {"anomaly": False, "reason": ""}

    def check_objective_drift(
        self, original_objective: str, current_action: str
    ) -> Dict[str, Any]:
        orig_words = set(original_objective.lower().split())
        curr_words = set(current_action.lower().split())
        if not orig_words:
            return {"drift": False, "overlap": 1.0}

        overlap = len(orig_words & curr_words) / len(orig_words)
        significant_drift = overlap < 0.15
        return {"drift": significant_drift, "overlap": round(overlap, 3)}

    def check_safety_decay_curve(self) -> Dict[str, Any]:
        elapsed_hours = (time.time() - self._session_start) / 3600.0
        safety_ratio = max(
            self._decay_threshold,
            1.0 - (elapsed_hours / 24.0),
        )
        critical = safety_ratio <= self._decay_threshold
        return {
            "elapsed_hours": round(elapsed_hours, 2),
            "safety_ratio": round(safety_ratio, 3),
            "critical": critical,
        }

    def reset(self) -> None:
        self._intent_history.clear()
        self._tool_chain.clear()
        self._session_start = time.time()


class AgentImpersonationDefender:
    """Agent-to-Human 冒充防御."""

    _HMAC_KEY_LENGTH = 32

    def __init__(self, hmac_key: Optional[bytes] = None):
        self._hmac_key = hmac_key or hashlib.sha256(
            f"zephyr-agent-{time.time()}-{id(self)}".encode()
        ).digest()

    def generate_unforgeable_marker(self, agent_id: str, context: str = "") -> str:
        message = f"{agent_id}:{context}:{int(time.time() // 60)}"
        sig = hmac.new(
            self._hmac_key, message.encode(), hashlib.sha256
        ).hexdigest()[:16]
        return f"zephyr-ag|{agent_id}|{sig}"

    def verify_marker(self, marker: str, expected_agent_id: str) -> bool:
        if not marker.startswith("zephyr-ag|"):
            return False
        parts = marker.split("|")
        if len(parts) != 3:
            return False
        if parts[1] != expected_agent_id:
            return False
        return True

    def user_verification_layer(self, message: str) -> Dict[str, Any]:
        agent_indicators = [
            r"(?i)\b(?:I am|this is|speaking as)\s+(?:an?\s+)?(?:AI|agent|bot|automated)",
            r"(?i)\b(?:as an AI|as a language model|as an artificial intelligence)\b",
            r"(?i)\b(?:generated by|produced by|written by)(?:\s+an?\s+)?(?:AI|model|algorithm)\b",
        ]
        agent_self_disclosure = False
        for pattern in agent_indicators:
            if re.search(pattern, message):
                agent_self_disclosure = True
                break

        needs_confirmation_label = not agent_self_disclosure
        return {
            "needs_agent_label": needs_confirmation_label,
            "has_self_disclosure": agent_self_disclosure,
            "recommendation": (
                "append_agent_marker" if needs_confirmation_label else "pass"
            ),
        }


class AgentSecurityLayer(LLMSecurityProtocol):
    """L4 Agent安全层 —— 权限最小化 + HITL审批 + 工具注入 + 金融合规 + 长时域 + 冒充防御."""

    def __init__(
        self,
        hmac_key: Optional[bytes] = None,
        max_permission: AgentPermission = AgentPermission.WRITE_SAFE,
    ):
        self._max_permission = max_permission
        self._financial_gate = FinancialComplianceGate()
        self._long_horizon_defender = LongHorizonAgentDefender()
        self._impersonation_defender = AgentImpersonationDefender(hmac_key=hmac_key)
        self._approval_log: List[ApprovalRequest] = []
        self._approval_auto_mode: bool = False

    def layer_name(self) -> str:
        return "l4_agent"

    def layer_index(self) -> int:
        return 4

    async def evaluate(self, ctx: SecurityContext) -> SecurityResult:
        tool_name = ctx.metadata.get("tool_name", "unknown")
        params = ctx.metadata.get("tool_params", {})
        intent = ctx.metadata.get("intent", "")
        objective = ctx.metadata.get("objective", "")
        has_agent_context = ctx.metadata.get("tool_name") is not None

        if has_agent_context:
            auth = self.authorize_tool_call(tool_name, ctx.metadata)
            if not auth.granted:
                return SecurityResult(
                    decision=SecurityDecision.DENY,
                    reason=f"Tool '{tool_name}' not authorized: {auth.reason}",
                    layer_name=self.layer_name(),
                    score=0.0,
                    details={"auth": auth.model_dump()},
                )

            params_valid, params_error = self.validate_tool_params(tool_name, params)
            if not params_valid:
                return SecurityResult(
                    decision=SecurityDecision.DENY,
                    reason=f"Invalid parameters for '{tool_name}': {params_error}",
                    layer_name=self.layer_name(),
                    score=0.0,
                )

            if (
                auth.risk in (RiskLevel.HIGH, RiskLevel.MEDIUM)
                and not self._approval_auto_mode
            ):
                approval = self.request_human_approval(
                    tool_name=tool_name,
                    params=params,
                    risk=auth.risk,
                    justification=f"Tool requires human approval: risk={auth.risk.value}",
                )
                if approval.outcome == ApprovalOutcome.DENIED:
                    return SecurityResult(
                        decision=SecurityDecision.DENY,
                        reason=f"Human approval denied for '{tool_name}'",
                        layer_name=self.layer_name(),
                        score=0.0,
                    )
        else:
            auth = None

        fin_result = self._financial_gate.scan(ctx.raw_input)
        if fin_result["blocked"]:
            return SecurityResult(
                decision=SecurityDecision.DENY,
                reason=f"Financial compliance blocked: {fin_result['violations']} violations",
                layer_name=self.layer_name(),
                score=0.0,
                details={"financial": fin_result},
            )

        if intent:
            intent_ok = self._long_horizon_defender.check_intent_consistency(intent)
            tool_ok = self._long_horizon_defender.check_tool_chaining_anomaly(
                tool_name
            )
            decay = self._long_horizon_defender.check_safety_decay_curve()
            if not intent_ok["consistent"] or tool_ok["anomaly"] or decay["critical"]:
                return SecurityResult(
                    decision=SecurityDecision.DENY,
                    reason="Long-horizon anomaly detected",
                    layer_name=self.layer_name(),
                    score=0.1,
                    details={
                        "intent_consistency": intent_ok,
                        "tool_chaining": tool_ok,
                        "safety_decay": decay,
                    },
                )

            if objective:
                drift = self._long_horizon_defender.check_objective_drift(
                    objective, tool_name
                )
                if drift["drift"]:
                    return SecurityResult(
                        decision=SecurityDecision.DENY,
                        reason="Objective drift detected",
                        layer_name=self.layer_name(),
                        score=0.2,
                        details={"objective_drift": drift},
                    )

        agent_id = ctx.metadata.get("agent_id", "")
        if agent_id:
            self._impersonation_defender.generate_unforgeable_marker(agent_id)

        if auth is not None:
            self.audit_tool_execution(
                tool_name=tool_name,
                granted=auth.granted,
                risk=auth.risk.value,
                outcome="executed",
            )

        if has_agent_context:
            return SecurityResult(
                decision=SecurityDecision.ALLOW,
                reason=f"Agent tool '{tool_name}' authorized",
                layer_name=self.layer_name(),
                score=0.8,
                details={
                    "auth": auth.model_dump(),
                    "financial": fin_result,
                },
            )
        else:
            return SecurityResult(
                decision=SecurityDecision.ALLOW,
                reason="L4 passed: no agent context, financial/content checks only",
                layer_name=self.layer_name(),
                score=0.9,
                details={"financial": fin_result},
            )

    def authorize_tool_call(
        self, tool_name: str, metadata: Optional[Dict[str, Any]] = None
    ) -> ToolCallAuthorization:
        meta = metadata or {}
        entry = _TOOL_RISK_MAP.get(tool_name)
        if entry is None:
            return ToolCallAuthorization(
                tool_name=tool_name,
                permission_required=AgentPermission.WRITE_CRITICAL,
                granted=False,
                risk=RiskLevel.HIGH,
                reason=f"Unknown tool '{tool_name}' — denied by default",
                session_id=meta.get("session_id", ""),
                params_snapshot=meta.get("tool_params", {}),
            )

        perm_required, risk = entry
        perm_values = {
            AgentPermission.READ_ONLY: 0,
            AgentPermission.WRITE_SAFE: 1,
            AgentPermission.WRITE_CRITICAL: 2,
            AgentPermission.ADMIN: 3,
        }
        granted = perm_values[perm_required] <= perm_values[self._max_permission]

        return ToolCallAuthorization(
            tool_name=tool_name,
            permission_required=perm_required,
            granted=granted,
            risk=risk,
            reason="Authorized" if granted else f"Requires {perm_required.value}, max={self._max_permission.value}",
            session_id=meta.get("session_id", ""),
            params_snapshot=meta.get("tool_params", {}),
        )

    def validate_tool_params(
        self, tool_name: str, params: Dict[str, Any]
    ) -> Tuple[bool, str]:
        for label, pattern in _CRITICAL_PARAM_PATTERNS:
            for key, value in params.items():
                if isinstance(value, str) and pattern.search(value):
                    return False, f"{label} detected in param '{key}'"
                if key == "command" and isinstance(value, str):
                    if pattern.search(value):
                        return False, f"{label} detected in command param"
        return True, ""

    def request_human_approval(
        self,
        tool_name: str,
        params: Dict[str, Any],
        risk: RiskLevel,
        justification: str = "",
    ) -> ApprovalRequest:
        request = ApprovalRequest(
            request_id=f"HITL-{int(time.time() * 1000)}-{hash(tool_name) & 0xFFFF:04x}",
            tool_name=tool_name,
            params=params,
            risk=risk,
            justification=justification,
        )
        if risk == RiskLevel.LOW:
            request.outcome = ApprovalOutcome.APPROVED
            request.resolved_at = time.time()
        self._approval_log.append(request)
        if len(self._approval_log) > 500:
            self._approval_log = self._approval_log[-500:]
        return request

    def approve_request(self, request_id: str) -> Optional[ApprovalRequest]:
        for req in self._approval_log:
            if req.request_id == request_id:
                req.outcome = ApprovalOutcome.APPROVED
                req.resolved_at = time.time()
                return req
        return None

    def deny_request(self, request_id: str) -> Optional[ApprovalRequest]:
        for req in self._approval_log:
            if req.request_id == request_id:
                req.outcome = ApprovalOutcome.DENIED
                req.resolved_at = time.time()
                return req
        return None

    def set_approval_auto_mode(self, enabled: bool) -> None:
        self._approval_auto_mode = enabled

    def set_max_permission(self, permission: AgentPermission) -> None:
        self._max_permission = permission

    def audit_tool_execution(
        self,
        tool_name: str,
        granted: bool,
        risk: str,
        outcome: str,
    ) -> Dict[str, Any]:
        record = {
            "timestamp": time.time(),
            "tool_name": tool_name,
            "granted": granted,
            "risk": risk,
            "outcome": outcome,
        }
        return record

    def reset_long_horizon_state(self) -> None:
        self._long_horizon_defender.reset()

    @property
    def approval_log(self) -> List[ApprovalRequest]:
        return list(self._approval_log)

    @property
    def financial_gate(self) -> FinancialComplianceGate:
        return self._financial_gate

    @property
    def impersonation_defender(self) -> AgentImpersonationDefender:
        return self._impersonation_defender
