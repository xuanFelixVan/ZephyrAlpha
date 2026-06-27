# [BLUEPRINT] MOD-INF-028 | docs/03_modules/_cross_layer/semantic-auditor/blueprint.md
# [MODULE] zephyr.governance.semantic_auditor.privacy
# [DOMAIN] D-GOVERNANCE
# [DEPENDENCIES]
# [CONSUMERS] 见蓝图 §4 接口契约
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 蓝图 §4 文件清单与代码双向对齐
# [MODIFY-GUARD] semantic-auditor/blueprint.md; semantic-auditor/__init__.py __all__
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] SemanticAuditError
# [TESTS] tests/semantic-auditor/
# [A_module] module_id=MOD-SEM_privacy | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

"""[BLUEPRINT] MOD-INF-028 | docs/03_modules/_cross_layer/semantic-auditor/blueprint.md

audit-trail.privacy — MOD-INF-020 · PII 检测与脱敏

====================================================

蓝图 D-020-11 · PII 模式检测 + 路径哈希 + 脱敏策略

PII 模式

--------

  - 邮箱地址

  - 电话号码

  - 社会安全号 (SSN)

  - 信用卡号

  - API 密钥

  - 路径哈希/掩码

"""

from __future__ import annotations

import hashlib
import logging
import re
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

_logger = logging.getLogger(__name__)


class PIICategory(str, Enum):
    EMAIL = "email"

    PHONE = "phone"

    SSN = "ssn"

    CREDIT_CARD = "credit_card"

    API_KEY = "api_key"

    IP_ADDRESS = "ip_address"

    CUSTOM = "custom"


class RedactionPolicy(str, Enum):
    MASK = "mask"

    HASH = "hash"

    REMOVE = "remove"

    REPLACE = "replace"


class PIIDetection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    category: PIICategory = PIICategory.EMAIL

    value: str = ""

    start: int = 0

    end: int = 0

    confidence: float = 1.0


class PIIScanResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    has_pii: bool = False

    detections: list[PIIDetection] = Field(default_factory=list)

    scanned_at: str = ""


_PII_PATTERNS: dict[PIICategory, list[re.Pattern[str]]] = {
    PIICategory.EMAIL: [
        re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", re.IGNORECASE),
    ],
    PIICategory.PHONE: [
        re.compile(r"\+?1?\s*[-.(]?\s*\d{3}\s*[-.)]\s*\d{3}\s*[-.]\s*\d{4}"),
        re.compile(r"\+?\d{1,3}[-.\s]?\d{3,4}[-.\s]?\d{3,4}[-.\s]?\d{0,4}"),
    ],
    PIICategory.SSN: [
        re.compile(r"\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b"),
    ],
    PIICategory.CREDIT_CARD: [
        re.compile(r"\b(?:\d{4}[-\s]?){3}\d{4}\b"),
    ],
    PIICategory.API_KEY: [
        re.compile(r"(?:api[_-]?key|token|secret|password|credential)\s*[:=]\s*['\"]?[\w\-]{16,}['\"]?", re.IGNORECASE),
        re.compile(r"\b(?:sk|pk|ghp|gho|glpat|xox[bpas])_[\w\-]{20,}\b"),
    ],
    PIICategory.IP_ADDRESS: [
        re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
    ],
}


_MASK_CHAR = "*"


_HASH_SALT = "zephyr-pii-hash-salt"


class PrivacyGuard:
    def __init__(
        self,
        custom_patterns: dict[PIICategory, list[str]] | None = None,
        default_policy: RedactionPolicy = RedactionPolicy.MASK,
    ) -> None:
        self._default_policy = default_policy

        self._patterns: dict[PIICategory, list[re.Pattern[str]]] = dict(_PII_PATTERNS)

        if custom_patterns:
            for category, pattern_strs in custom_patterns.items():
                if category not in self._patterns:
                    self._patterns[category] = []

                self._patterns[category].extend(re.compile(p) for p in pattern_strs)

    def detect_pii(self, text: str) -> PIIScanResult:
        detections: list[PIIDetection] = []

        for category, patterns in self._patterns.items():
            for pattern in patterns:
                for match in pattern.finditer(text):
                    detections.append(
                        PIIDetection(
                            category=category,
                            value=match.group(),
                            start=match.start(),
                            end=match.end(),
                        )
                    )

        from datetime import UTC, datetime

        return PIIScanResult(
            has_pii=len(detections) > 0,
            detections=detections,
            scanned_at=datetime.now(UTC).isoformat(),
        )

    def redact(
        self,
        text: str,
        policy: RedactionPolicy | None = None,
        replacement: str = "[REDACTED]",
    ) -> str:
        effective_policy = policy or self._default_policy

        result = text

        scan = self.detect_pii(text)

        sorted_detections = sorted(scan.detections, key=lambda d: d.start, reverse=True)

        for detection in sorted_detections:
            original = detection.value

            if effective_policy == RedactionPolicy.MASK:
                replacement_text = (
                    original[:2] + _MASK_CHAR * (len(original) - 4) + original[-2:]
                    if len(original) > 4
                    else _MASK_CHAR * len(original)
                )

            elif effective_policy == RedactionPolicy.HASH:
                replacement_text = f"[HASH:{hash_path(original)}]"

            elif effective_policy == RedactionPolicy.REMOVE:
                replacement_text = ""

            else:
                replacement_text = replacement

            result = result[: detection.start] + replacement_text + result[detection.end :]

        return result

    @staticmethod
    def hash_path(path: str) -> str:
        return hash_path(path)


def hash_path(path: str) -> str:
    digest = hashlib.sha256(f"{_HASH_SALT}:{path}".encode()).hexdigest()

    return digest[:16]
