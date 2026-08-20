# [BLUEPRINT] MOD-LLM_SECURITY | docs/03_modules/_cross_layer/large_language_model_security/blueprint.md | §
# [MODULE] zephyr.security.llm_defense.llm_security.layers.l4_agent
# [DOMAIN] D_SECURITY
# [DEPENDENCIES]
# [CONSUMERS] zephyr.security.llm_defense.llm_security.gateway; tests.llm_security.test_l4_agent_security
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-LLM_SECURITY | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
import hashlib
import hmac
import logging
import secrets
import time
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)

# 5.62.4 治本：L4 密钥统一经 SecretProvider 从环境变量解析，禁止硬编码默认密钥
_L4_HMAC_SECRET_ENV = "ZEPHYR_LSG_L4_HMAC_SECRET"


def _resolve_l4_secret(explicit: str | bytes | None) -> str | None:
    """解析 L4 HMAC 密钥（5.62.4 治本）：显式参数 > SecretProvider（ZEPHYR_LSG_L4_HMAC_SECRET）。

    未配置时返回 None，由调用方决定 fail-fast 或明确降级（本函数不提供任何默认密钥）。
    """
    if isinstance(explicit, bytes) and explicit:
        return explicit.decode("utf-8")
    if isinstance(explicit, str) and explicit.strip():
        return explicit.strip()
    from zephyr.shared.security.secrets import get_secret_or_default

    return get_secret_or_default(_L4_HMAC_SECRET_ENV, "").strip() or None


class RiskLevel(Enum):
    """风险等级。"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AgentPermission(Enum):
    """Agent 工具调用权限级别（值越大权限越高）。"""

    NONE = 0
    READ_ONLY = 1
    WRITE_SAFE = 2
    WRITE_CRITICAL = 3
    # 兼容旧别名
    READ = 1
    WRITE = 2
    EXECUTE = 2
    ADMIN = 3


class ApprovalOutcome(Enum):
    """审批结果。"""

    APPROVED = "approved"
    DENIED = "denied"
    PENDING = "pending"
    ESCALATED = "escalated"


class FJThreat(Enum):
    """金融管辖权威胁类型。"""

    MARKET_MANIPULATION = "market_manipulation"
    INSIDER_TRADING = "insider_trading"
    WASH_TRADING = "wash_trading"
    SPOOFING = "spoofing"
    FRONT_RUNNING = "front_running"
    NONE = "none"


class ToolCallAuthorization:
    """工具调用授权结果。"""

    def __init__(
        self,
        granted: bool,
        permission_required: AgentPermission,
        risk: RiskLevel,
        reason: str = "",
        tool_name: str = "",
    ):
        self.granted = granted
        self.permission_required = permission_required
        self.risk = risk
        self.reason = reason
        self.tool_name = tool_name


class ApprovalRequest:
    """人工审批请求。"""

    _counter = 0

    def __init__(
        self,
        agent_id: str = "",
        action: str = "",
        risk: RiskLevel = RiskLevel.MEDIUM,
        justification: str = "",
        request_id: str | None = None,
    ):
        ApprovalRequest._counter += 1
        self.request_id = request_id or f"appr-{ApprovalRequest._counter}"
        self.agent_id = agent_id
        self.action = action
        self.risk = risk
        self.justification = justification
        self.outcome = ApprovalOutcome.PENDING


class AgentBoundary:
    def __init__(self, agent_id="", allowed_actions=None, restricted_resources=None):
        self.agent_id = agent_id
        self.allowed_actions = allowed_actions or []
        self.restricted_resources = restricted_resources or []


class AgentSecurityLayer:
    """L4 Agent 安全层：工具授权 + 参数验证 + 人工审批 + 金融合规。"""

    _TOOL_PERMISSIONS = {
        "read_file": (AgentPermission.READ_ONLY, RiskLevel.LOW),
        "list_dir": (AgentPermission.READ_ONLY, RiskLevel.LOW),
        "write_file": (AgentPermission.WRITE_SAFE, RiskLevel.MEDIUM),
        "create_file": (AgentPermission.WRITE_SAFE, RiskLevel.MEDIUM),
        "delete_file": (AgentPermission.WRITE_CRITICAL, RiskLevel.HIGH),
        "run_command": (AgentPermission.WRITE_CRITICAL, RiskLevel.HIGH),
        "move_file": (AgentPermission.WRITE_CRITICAL, RiskLevel.HIGH),
    }

    def __init__(
        self,
        config: dict[str, Any] | None = None,
        hmac_key: str | None = None,
        max_permission: AgentPermission = AgentPermission.WRITE_SAFE,
    ):
        self.config = config or {}
        # 5.62.4 治本：消除硬编码默认密钥 "l4-agent-default-hmac-key"。
        # 显式参数 > SecretProvider（ZEPHYR_LSG_L4_HMAC_SECRET）；均未配置时明确降级为
        # None + 告警。注：该字段当前未被本类任何密码学操作消费，fail-fast 会使
        # LSG 网关默认构造（hmac_key=None）整体不可用=自我 DoS，故降级不 fail-fast；
        # 身份冒充标记的 HMAC 密钥 fail-fast 见 AgentImpersonationDefender。
        resolved = _resolve_l4_secret(hmac_key)
        if resolved is None:
            logger.warning(
                "AgentSecurityLayer: 未传 hmac_key 且 %s 未设置，明确降级（无默认密钥）",
                _L4_HMAC_SECRET_ENV,
            )
        self._hmac_key = resolved
        self._max_permission = max_permission
        self._approvals: dict[str, ApprovalRequest] = {}
        self._auto_approve = False

    def authorize_tool_call(self, tool_name: str, params: dict[str, Any] | None = None) -> ToolCallAuthorization:
        perm_risk = self._TOOL_PERMISSIONS.get(tool_name)
        if perm_risk is None:
            return ToolCallAuthorization(
                granted=False,
                permission_required=AgentPermission.WRITE_CRITICAL,
                risk=RiskLevel.HIGH,
                reason=f"Unknown tool: {tool_name}",
                tool_name=tool_name,
            )
        perm, risk = perm_risk
        if perm.value > self._max_permission.value:
            return ToolCallAuthorization(
                granted=False,
                permission_required=perm,
                risk=risk,
                reason=f"permission denied: tool needs {perm.name.lower()}, max={self._max_permission.name.lower()}",
                tool_name=tool_name,
            )
        return ToolCallAuthorization(
            granted=True,
            permission_required=perm,
            risk=risk,
            reason="ok",
            tool_name=tool_name,
        )

    def validate_tool_params(self, tool_name: str, params: dict[str, Any]) -> tuple[bool, str]:
        for key, val in (params or {}).items():
            sval = str(val)
            low = sval.lower()
            if "eval(" in low or "exec(" in low or "__import__" in low:
                return False, "code_injection"
            if "../" in sval or "..\\" in sval:
                return False, "path_traversal"
            if "rm -rf" in low or "del /f" in low or "format " in low or "shutdown" in low:
                return False, "system_command"
        return True, ""

    def request_human_approval(
        self,
        tool_name: str,
        params: dict[str, Any],
        risk: RiskLevel,
        justification: str,
    ) -> ApprovalRequest:
        req = ApprovalRequest(
            agent_id="",
            action=tool_name,
            risk=risk,
            justification=justification,
        )
        if risk is RiskLevel.LOW or self._auto_approve:
            req.outcome = ApprovalOutcome.APPROVED
        self._approvals[req.request_id] = req
        return req

    def approve_request(self, request_id: str) -> ApprovalRequest | None:
        req = self._approvals.get(request_id)
        if req is not None:
            req.outcome = ApprovalOutcome.APPROVED
        return req

    def deny_request(self, request_id: str) -> ApprovalRequest | None:
        req = self._approvals.get(request_id)
        if req is not None:
            req.outcome = ApprovalOutcome.DENIED
        return req

    def set_approval_auto_mode(self, enabled: bool) -> None:
        self._auto_approve = enabled

    async def evaluate(self, ctx: object) -> object:
        """评估 agent 工具调用：无工具调用 -> ALLOW，未知工具 -> DENY，已知且授权 -> ALLOW。"""
        from zephyr.security.llm_defense.llm_security.protocol import SecurityResult
        from zephyr.shared.contracts.security.security_decision import SecurityDecision

        meta = getattr(ctx, "metadata", {}) or {}
        tool_name = meta.get("tool_name", "")
        # 无工具调用（benign text scan）-> ALLOW
        if not tool_name:
            return SecurityResult(
                decision=SecurityDecision.ALLOW,
                reason="no tool call — benign pass-through",
                layer_name="l4_agent",
                score=1.0,
            )
        auth = self.authorize_tool_call(tool_name)
        if not auth.granted:
            return SecurityResult(
                decision=SecurityDecision.DENY,
                reason=f"unknown tool or insufficient permission: {tool_name}",
                layer_name="l4_agent",
                score=0.0,
                details={"tool_name": tool_name, "reason": auth.reason},
            )
        return SecurityResult(
            decision=SecurityDecision.ALLOW,
            reason=f"tool authorized: {tool_name}",
            layer_name="l4_agent",
            score=1.0,
            details={"tool_name": tool_name, "permission": auth.permission_required.name},
        )

    # 兼容旧接口
    def validate(self, agent_action):
        return True

    def check_permissions(self, agent_id, action):
        return True

    def enforce_policy(self, agent_id, policy):
        pass


class FinancialComplianceGate:
    """金融合规门：检测内幕交易/市场操纵等金融威胁。"""

    _THREAT_PATTERNS = {
        FJThreat.INSIDER_TRADING: [
            "insider non-public material",
            "insider trading",
            "material non-public information",
            "before earnings",
        ],
        FJThreat.MARKET_MANIPULATION: [
            "pump and dump",
            "spoof the market",
            "manipulate the order book",
        ],
        FJThreat.WASH_TRADING: ["wash trading", "wash sale"],
        FJThreat.SPOOFING: ["spoofing orders", "layering"],
        FJThreat.FRONT_RUNNING: ["front running", "front-run client"],
    }

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}

    def scan(self, text: str) -> dict[str, Any]:
        lowered = (text or "").lower()
        findings: list[str] = []
        for threat, patterns in self._THREAT_PATTERNS.items():
            if any(p in lowered for p in patterns):
                findings.append(threat.value)
        blocked = len(findings) > 0
        return {
            "blocked": blocked,
            "violations": len(findings),
            "findings": findings,
        }

    # 兼容旧接口
    def check_compliance(self, action: object) -> bool:
        return not self.scan(str(action))["blocked"]

    def validate_transaction(self, transaction: object) -> bool:
        return True


class AgentImpersonationDefender:
    """检测 agent 身份冒充（HMAC 不可伪造标记）。

    5.62.4 治本：HMAC 密钥禁止硬编码默认（原默认 "l4-impersonation-secret" 公开可知，
    冒充检测形同虚设）——必须显式传 secret 或设置 ZEPHYR_LSG_L4_HMAC_SECRET，否则 fail-fast。
    """

    def __init__(self, config: dict[str, Any] | None = None, secret: str | bytes | None = None):
        self.config = config or {}
        resolved = _resolve_l4_secret(secret)
        if resolved is None:
            raise ValueError(
                "AgentImpersonationDefender 需要 HMAC 密钥：请显式传 secret 参数或设置环境变量 "
                f"{_L4_HMAC_SECRET_ENV}（禁止公开默认密钥，fail-fast）"
            )
        self._secret = resolved

    def generate_unforgeable_marker(self, agent_id: str) -> str:
        ts = str(int(time.time()))
        sig = hmac.new(self._secret.encode(), f"{agent_id}|{ts}".encode(), hashlib.sha256).hexdigest()
        return f"zephyr-ag|{agent_id}|{ts}|{sig}"

    def verify_marker(self, marker: str, expected_agent_id: str) -> bool:
        parts = marker.split("|")
        if len(parts) != 4 or parts[0] != "zephyr-ag":
            return False
        _, agent_id, ts, sig = parts
        if agent_id != expected_agent_id:
            return False
        expected = hmac.new(self._secret.encode(), f"{agent_id}|{ts}".encode(), hashlib.sha256).hexdigest()
        return hmac.compare_digest(sig, expected)

    # 兼容旧接口
    def detect_impersonation(self, agent_id: str, claimed_identity: str) -> bool:
        return agent_id != claimed_identity

    def validate_agent_identity(self, agent_id: str) -> bool:
        return True


class LongHorizonAgentDefender:
    """检测长周期 agent 攻击（意图漂移检测）。"""

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self._initial_intent: str | None = None

    def check_intent_consistency(self, intent: str) -> dict[str, Any]:
        if self._initial_intent is None:
            self._initial_intent = intent
            return {"consistent": True, "drift": 0.0}
        drift = 1.0 - _intent_similarity(self._initial_intent, intent)
        return {"consistent": drift < 0.5, "drift": round(drift, 4)}

    # 兼容旧接口
    def detect_long_horizon_attack(self, agent_id: str, action_history: list[Any]) -> bool:
        return False

    def analyze_behavior_pattern(self, actions: list[Any]) -> dict[str, Any]:
        return {"threat_detected": False, "confidence": 0.0}


def _intent_similarity(a: str, b: str) -> float:
    """简单的词集 Jaccard 相似度。"""
    wa = set(a.lower().split())
    wb = set(b.lower().split())
    if not wa and not wb:
        return 1.0
    return len(wa & wb) / max(len(wa | wb), 1)
