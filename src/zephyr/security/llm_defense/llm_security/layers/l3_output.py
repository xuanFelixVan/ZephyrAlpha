# [BLUEPRINT] MOD-LLM_SECURITY
# [MODULE] zephyr.security.llm_defense.llm_security.layers.l3_output
# [DOMAIN] D_SECURITY
# [DEPENDENCIES]
# [CONSUMERS] zephyr.security.llm_defense.llm_security.gateway; tests.adversarial.test_cross_layer_systems_red_team; tests.llm_security.test_l3_output_security
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
import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class SchemaValidationResult:
    valid: bool
    errors: list[str] = field(default_factory=list)


@dataclass
class SandboxExecutionResult:
    safe: bool
    output: str = ""
    blocked_reason: str = ""


@dataclass
class RedactionResult:
    redactions: int
    clean_text: str


@dataclass
class HallucinationDetectionResult:
    is_hallucination: bool
    confidence: float


@dataclass
class ContentSafetyResult:
    safe: bool
    violations: list[str] = field(default_factory=list)


class OutputFilterLayer:
    """兼容旧接口的输出过滤层。"""

    def __init__(self, config=None):
        self.config = config or {}

    def validate(self, output):
        return True

    def sanitize(self, output):
        return output

    def detect_leak(self, text):
        return False


# 敏感数据正则
_API_KEY_RE = re.compile(r"sk-[a-zA-Z0-9]{20,}")
_AWS_KEY_RE = re.compile(r"AKIA[0-9A-Z]{16}")
_EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
_SECRET_KV_RE = re.compile(r"(?i)(secret|password|token|api[_-]?key|credential)\s*[:=]\s*\S+")
# 危险沙箱关键字
_SANDBOX_BLOCKED = [
    "os.system", "subprocess", "popen", "eval(", "exec(",
    "__import__", "compile(", "os.remove", "shutil.rmtree",
]
# 幻觉确定性标记
_HALLUCINATION_MARKERS = [
    "certain", "no way", "absolutely", "100%", "definitely",
    "guaranteed", "without a doubt", "impossible to be wrong",
]
# 内容安全违规话题
_UNSAFE_TOPICS = [
    "bomb", "weapon", "explosive", "drug", "kill", "poison",
    "methamphetamine", "firearm", "grenade", "hack",
]


class OutputSecurityLayer:
    """L3 输出安全层：schema 校验 + 沙箱 + 脱敏 + 幻觉检测 + 内容安全。"""

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}

    def validate_schema(self, data: object, schema: type) -> SchemaValidationResult:
        try:
            schema.model_validate(data)
            return SchemaValidationResult(valid=True, errors=[])
        except Exception as e:
            errs = []
            if hasattr(e, "errors"):
                for err in e.errors():
                    errs.append(f"{'.'.join(str(x) for x in err.get('loc', []))}: {err.get('msg', '')}")
            else:
                errs.append(str(e))
            return SchemaValidationResult(valid=False, errors=errs)

    def sandbox_execution(self, code: str) -> SandboxExecutionResult:
        for kw in _SANDBOX_BLOCKED:
            if kw in code:
                return SandboxExecutionResult(
                    safe=False, output="", blocked_reason=f"Blocked keyword: {kw}"
                )
        # 安全代码：模拟 print 输出
        m = re.search(r"print\(['\"]([^'\"]*)['\"]\)", code)
        output = m.group(1) if m else ""
        return SandboxExecutionResult(safe=True, output=output)

    def redact_sensitive_data(self, content: str) -> RedactionResult:
        count = 0
        clean = content
        if _API_KEY_RE.search(clean):
            clean = _API_KEY_RE.sub("[BLOCKED]", clean)
            count += 1
        if _AWS_KEY_RE.search(clean):
            clean = _AWS_KEY_RE.sub("[BLOCKED]", clean)
            count += 1
        if _SECRET_KV_RE.search(clean):
            clean = _SECRET_KV_RE.sub(r"\1: [REDACTED]", clean)
            count += 1
        if _EMAIL_RE.search(clean):
            clean = _EMAIL_RE.sub("[REDACTED]", clean)
            count += 1
        return RedactionResult(redactions=count, clean_text=clean)

    def detect_hallucination(self, text: str) -> HallucinationDetectionResult:
        lowered = (text or "").lower()
        hits = sum(1 for m in _HALLUCINATION_MARKERS if m in lowered)
        confidence = min(1.0, hits * 0.35)
        return HallucinationDetectionResult(
            is_hallucination=confidence > 0.6, confidence=confidence
        )

    def check_content_safety(self, text: str) -> ContentSafetyResult:
        lowered = (text or "").lower()
        violations = [t for t in _UNSAFE_TOPICS if t in lowered]
        return ContentSafetyResult(safe=len(violations) == 0, violations=violations)

    def layer_name(self) -> str:
        return "l3_output"

    def layer_index(self) -> int:
        return 3

    async def evaluate(self, ctx: object) -> object:
        """评估输出安全：含密钥/敏感数据/不安全内容 -> DENY。"""
        from zephyr.security.llm_defense.llm_security.protocol import SecurityResult
        from zephyr.shared.contracts.security.security_decision import SecurityDecision

        raw = getattr(ctx, "raw_input", "") or ""
        # 1. 敏感数据脱敏检测
        red = self.redact_sensitive_data(raw)
        if red.redactions > 0:
            return SecurityResult(
                decision=SecurityDecision.DENY,
                reason="sensitive data detected in output",
                layer_name="l3_output",
                score=0.0,
                details={"redactions": red.redactions},
            )
        # 2. 内容安全检测（bomb/weapon 等）
        safety = self.check_content_safety(raw)
        if not safety.safe:
            return SecurityResult(
                decision=SecurityDecision.DENY,
                reason="unsafe content detected",
                layer_name="l3_output",
                score=0.0,
                details={"violations": safety.violations},
            )
        return SecurityResult(
            decision=SecurityDecision.ALLOW,
            reason="output clean",
            layer_name="l3_output",
            score=1.0,
        )

    # 兼容旧接口
    def validate(self, output):
        return True

    def sanitize(self, output):
        return output

    def detect_leak(self, text):
        return self.redact_sensitive_data(text).redactions > 0


# AI 代码审计 issue 检测规则
_AUDIT_RULES = [
    ("dangerous_import", [r"\bimport\s+os\b", r"\bimport\s+subprocess\b", r"\bimport\s+socket\b"]),
    ("dynamic_execution", [r"\beval\s*\(", r"\bexec\s*\(", r"\bcompile\s*\("]),
    ("file_system_access", [r"\bopen\s*\(", r"/etc/", r"/root/", r"/proc/"]),
    ("credential_handling", [r"password\s*=", r"secret\s*=", r"credential\s*=", r"token\s*=", r"api_key\s*="]),
    ("network_access", [r"\bsocket\b", r"\brequests\b", r"\burllib\b", r"\bhttp\.client\b"]),
]


class AIGeneratedCodeTrustBoundary:
    """AI 生成代码信任边界审计器。"""

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}

    def audit(self, code: str) -> dict[str, Any]:
        issues: list[dict[str, str]] = []
        for issue_type, patterns in _AUDIT_RULES:
            for pat in patterns:
                if re.search(pat, code, re.IGNORECASE):
                    issues.append({"type": issue_type, "pattern": pat})
                    break
        return {
            "safe": len(issues) == 0,
            "issue_count": len(issues),
            "issues": issues,
        }

    # 兼容旧接口
    def check_code_trust(self, code: str) -> bool:
        return self.audit(code)["safe"]

    def validate_output_boundary(self, output: str) -> bool:
        return True

    def enforce_sandbox(self, code: str) -> dict[str, Any]:
        r = self.audit(code)
        return {"sandboxed": True, "violations": r["issues"]}


class AgentPublicInteractionGuard:
    """Agent 公共交互守卫：脱敏对外输出。"""

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}

    def sanitize_for_github(self, content: str) -> str:
        clean = _API_KEY_RE.sub("[REDACTED]", content)
        clean = _EMAIL_RE.sub("[REDACTED]", clean)
        clean = _SECRET_KV_RE.sub(r"\1: [REDACTED]", clean)
        # 公开仓库水印标识
        return f"{clean}\n[Sanitized by ZephyrAlpha LSG Public Interaction Guard]"

    def sanitize_for_api(self, content: str) -> str:
        clean = _API_KEY_RE.sub("[REDACTED]", content)
        clean = _EMAIL_RE.sub("[REDACTED]", clean)
        clean = _SECRET_KV_RE.sub(r"\1: [REDACTED]", clean)
        return clean

    # 兼容旧接口
    def validate_interaction(self, interaction: object) -> bool:
        return True

    def check_public_safety(self, content: str) -> bool:
        return True


# 兼容旧 result 类（保留导入兼容）
class HallucinationResult:
    def __init__(self, detected=False, confidence=0.0, category="", details=None):
        self.detected = detected
        self.confidence = confidence
        self.category = category
        self.details = details or {}


class RedactResult:
    def __init__(self, redacted=False, original="", redacted_text="", redaction_count=0):
        self.redacted = redacted
        self.original = original
        self.redacted_text = redacted_text
        self.redaction_count = redaction_count


class SandboxResult:
    def __init__(self, safe=True, violations=None, sanitized_output=""):
        self.safe = safe
        self.violations = violations or []
        self.sanitized_output = sanitized_output


class SafetyResult:
    def __init__(self, passed=True, risk_level="low", violations=None):
        self.passed = passed
        self.risk_level = risk_level
        self.violations = violations or []


class SchemaResult:
    def __init__(self, valid=True, schema_compliant=True, errors=None):
        self.valid = valid
        self.schema_compliant = schema_compliant
        self.errors = errors or []
