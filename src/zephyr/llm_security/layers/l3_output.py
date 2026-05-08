import hashlib
import re
import subprocess
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, ValidationError

from zephyr.llm_security.patterns.secrets import scan_secrets
from zephyr.llm_security.protocol import (
    LLMSecurityProtocol,
    SecurityContext,
    SecurityDecision,
    SecurityResult,
)


class RedactionLevel(str, Enum):
    BLOCK = "block"
    MASK = "mask"
    FLAG = "flag"


class SchemaResult(BaseModel):
    valid: bool = True
    errors: List[str] = Field(default_factory=list)
    extra_fields: List[str] = Field(default_factory=list)


class SandboxResult(BaseModel):
    safe: bool = True
    output: str = ""
    stderr: str = ""
    execution_time_ms: float = 0.0
    blocked_reason: str = ""


class RedactResult(BaseModel):
    clean_text: str = ""
    redactions: int = 0
    blocked: bool = False
    redaction_log: List[Dict[str, Any]] = Field(default_factory=list)


class HallucinationResult(BaseModel):
    is_hallucination: bool = False
    confidence: float = 0.0
    reasons: List[str] = Field(default_factory=list)


class SafetyResult(BaseModel):
    safe: bool = True
    violations: List[str] = Field(default_factory=list)


class OutputSecurityLayer(LLMSecurityProtocol):
    """L3 输出安全层 —— Schema验证 / 沙箱执行 / PII脱敏 / 幻觉检测 / 内容安全"""

    def __init__(self):
        self._code_trust_boundary = AIGeneratedCodeTrustBoundary()
        self._public_guard = AgentPublicInteractionGuard()

    def layer_name(self) -> str:
        return "l3_output"

    def layer_index(self) -> int:
        return 3

    async def evaluate(self, ctx: SecurityContext) -> SecurityResult:
        content = ctx.raw_input

        redact = self.redact_sensitive_data(content)
        if redact.blocked:
            return SecurityResult(
                decision=SecurityDecision.DENY,
                reason="Sensitive data detected in output",
                layer_name=self.layer_name(),
                score=0.0,
            )

        hallu = self.detect_hallucination(content, ctx.metadata.get("context", ""))
        if hallu.is_hallucination and hallu.confidence > 0.7:
            return SecurityResult(
                decision=SecurityDecision.FLAG,
                reason=f"Hallucination detected: {hallu.reasons}",
                layer_name=self.layer_name(),
                score=1.0 - hallu.confidence,
            )

        safety = self.check_content_safety(content)
        if not safety.safe:
            return SecurityResult(
                decision=SecurityDecision.DENY,
                reason=f"Safety violations: {safety.violations}",
                layer_name=self.layer_name(),
                score=0.0,
            )

        return SecurityResult(
            decision=SecurityDecision.ALLOW,
            reason="L3 output security passed",
            layer_name=self.layer_name(),
            score=0.92,
            details={
                "redactions": redact.redactions,
                "hallucination_confidence": hallu.confidence,
            },
        )

    def validate_schema(self, data: Dict[str, Any], schema_model: type) -> SchemaResult:
        try:
            instance = schema_model(**data)
            return SchemaResult(valid=True)
        except ValidationError as e:
            errors = [f"{err['loc']}: {err['msg']}" for err in e.errors()]
            extra = [err["loc"][0] for err in e.errors() if err["type"] == "extra_forbidden"]
            return SchemaResult(valid=False, errors=errors, extra_fields=extra)

    def sandbox_execution(self, code: str, timeout: float = 5.0) -> SandboxResult:
        blocked_keywords = [
            "__import__", "eval(", "exec(", "compile(", "os.system",
            "subprocess.", "import os", "import sys", "open('/", "open('C:",
        ]
        for kw in blocked_keywords:
            if kw in code:
                return SandboxResult(
                    safe=False,
                    blocked_reason=f"Blocked keyword: {kw}",
                )

        try:
            result = subprocess.run(
                ["python", "-c", code],
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            return SandboxResult(
                safe=result.returncode == 0,
                output=result.stdout[:2000],
                stderr=result.stderr[:1000],
                execution_time_ms=result.returncode,
            )
        except subprocess.TimeoutExpired:
            return SandboxResult(safe=False, blocked_reason="Execution timeout")
        except Exception as e:
            return SandboxResult(safe=False, blocked_reason=str(e)[:200])

    def redact_sensitive_data(self, content: str) -> RedactResult:
        hits = scan_secrets(content)
        redactions = []
        blocked = False
        clean = content

        for hit in sorted(hits, key=lambda h: h["start"], reverse=True):
            action = hit["action"]
            match_text = hit["match"]
            start = hit["start"]
            end = hit["end"]

            if action == "block":
                blocked = True
                replacement = "[BLOCKED]"
            elif action == "mask":
                if len(match_text) > 8:
                    replacement = match_text[:3] + "***" + match_text[-3:]
                else:
                    replacement = "***"
            else:
                replacement = match_text

            clean = clean[:start] + replacement + clean[end:]
            redactions.append({
                "name": hit["name"],
                "action": action,
                "severity": hit["severity"],
                "original_length": len(match_text),
            })

        return RedactResult(
            clean_text=clean,
            redactions=len(redactions),
            blocked=blocked,
            redaction_log=redactions,
        )

    def detect_hallucination(self, output: str, context: str = "") -> HallucinationResult:
        reasons = []
        confidence = 0.0

        certainty_markers = [
            "I am certain", "definitely", "absolutely sure", "100% confident",
            "without a doubt", "there is no way", "impossible that",
        ]
        for marker in certainty_markers:
            if marker.lower() in output.lower():
                confidence += 0.15
                reasons.append(f"Excessive certainty marker: {marker}")

        if context and len(context) > 50:
            context_words = set(context.lower().split())
            output_words = set(output.lower().split())
            if len(output_words) > 0:
                overlap = len(context_words & output_words) / len(output_words)
                if overlap < 0.1 and len(output) > 100:
                    confidence += 0.3
                    reasons.append("Low semantic overlap with context")

        hallucination_patterns = [
            r"(?i)\b(?:invented|made up|fabricated|fictional)\b",
            r"(?i)\b(?:i don't have access to|i cannot verify|i'm not sure about)\b.*\b(?:but|however)\b.*\b(?:is|are|was|were)\b",
        ]
        for pattern in hallucination_patterns:
            if re.search(pattern, output):
                confidence += 0.2
                reasons.append(f"Hallucination pattern match")

        confidence = min(1.0, confidence)
        return HallucinationResult(
            is_hallucination=confidence > 0.5,
            confidence=confidence,
            reasons=reasons,
        )

    def check_content_safety(self, content: str) -> SafetyResult:
        violations = []
        toxic_patterns = [
            r"(?i)\b(?:kill|murder|assassinate|terrorist|bomb)\b.*\b(?:yourself|himself|herself|someone|people)\b",
            r"(?i)\b(?:how\s+to\s+make|recipe\s+for)\s+(?:a\s+|an\s+|the\s+)?(?:bomb|explosive|poison|drug|meth|cocaine)\b",
            r"(?i)\b(?:child|minor)\b.*\b(?:exploit|abuse|pornographic|sexual)\b",
            r"(?i)\b(?:hack\w*|crack\w*|bypass\w*|exploit\w*)\b.*\b(?:password|firewall|security|authentication|system|network)\b",
            r"(?i)\b(?:step\s+by\s+step\s+)?(?:guide|tutorial|instructions?)\s+(?:to|for|on)\s+(?:hack\w*|crack\w*|bypass\w*|exploit\w*|attack\w*)\b",
            r"(?i)\b(?:how\s+to)\s+(?:hack\w*|crack\w*|steal\w*|exploit\w*|attack\w*|bypass\w*)\b",
        ]
        for pattern in toxic_patterns:
            if re.search(pattern, content):
                violations.append(f"Toxic content pattern: {pattern[:60]}")

        return SafetyResult(safe=len(violations) == 0, violations=violations)


class AIGeneratedCodeTrustBoundary:
    """AI生成代码信任边界审计 —— 6类安全问题检测"""

    def audit(self, code: str) -> Dict[str, Any]:
        issues = []

        dangerous_imports = ["os", "sys", "subprocess", "socket", "urllib", "requests"]
        for imp in dangerous_imports:
            if re.search(rf"(?m)^\s*import\s+{imp}\b|^\s*from\s+{imp}\b", code):
                issues.append({
                    "type": "dangerous_import",
                    "detail": f"Import of {imp} detected",
                    "severity": "medium",
                })

        if re.search(r"(?i)(eval\s*\(|exec\s*\(|compile\s*\(|__import__\s*\()", code):
            issues.append({
                "type": "dynamic_execution",
                "detail": "Dynamic code execution detected",
                "severity": "critical",
            })

        if re.search(r"(?i)(open\s*\(\s*['\"]\s*/|open\s*\(\s*['\"]\s*C:\\|write\s*\(\s*['\"]\s*/)", code):
            issues.append({
                "type": "file_system_access",
                "detail": "Direct file system access detected",
                "severity": "high",
            })

        if re.search(r"(?i)(password|secret|token|key|credential)", code):
            issues.append({
                "type": "credential_handling",
                "detail": "Potential credential handling",
                "severity": "medium",
            })

        if re.search(r"(?i)(while\s+True\s*:|for\s+.*:\s*\n\s*(while\s+True|for\s+))", code):
            issues.append({
                "type": "infinite_loop",
                "detail": "Potential infinite loop pattern",
                "severity": "low",
            })

        if re.search(r"(?i)(socket\.|connect\s*\(|bind\s*\(|listen\s*\()", code):
            issues.append({
                "type": "network_access",
                "detail": "Network socket usage detected",
                "severity": "medium",
            })

        return {
            "safe": len(issues) == 0,
            "issue_count": len(issues),
            "issues": issues,
            "risk_score": min(1.0, len(issues) * 0.15),
        }


class AgentPublicInteractionGuard:
    """Agent公域发言安全检查 —— GitHub/飞书/社区/API四通道自动脱敏+身份声明"""

    _IDENTITY_DISCLAIMER = (
        "\n\n---\n"
        "_This response was generated by an AI agent (ZephyrAlpha LSG). "
        "Please verify critical information before acting._"
    )

    def sanitize_for_github(self, content: str) -> str:
        redact = self._redact_all_secrets(content)
        return redact + self._IDENTITY_DISCLAIMER

    def sanitize_for_feishu(self, content: str) -> str:
        redact = self._redact_all_secrets(content)
        return redact + self._IDENTITY_DISCLAIMER

    def sanitize_for_community(self, content: str) -> str:
        redact = self._redact_all_secrets(content)
        return redact + self._IDENTITY_DISCLAIMER

    def sanitize_for_api(self, content: str) -> str:
        redact = self._redact_all_secrets(content)
        return redact

    def _redact_all_secrets(self, content: str) -> str:
        from zephyr.llm_security.patterns.secrets import scan_secrets
        hits = scan_secrets(content)
        clean = content
        for hit in sorted(hits, key=lambda h: h["start"], reverse=True):
            start = hit["start"]
            end = hit["end"]
            clean = clean[:start] + "[REDACTED]" + clean[end:]
        return clean
