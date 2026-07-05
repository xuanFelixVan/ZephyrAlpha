# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §
# [MODULE] zephyr.governance.audit_trail.privacy
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GOV_privacy | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
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

from zephyr.governance.rule_patterns import PIICategory, PII_PATTERNS  # SSoT (ARCH-033 Phase 7 修正: 合并进 rule_patterns)

_logger = logging.getLogger(__name__)


# PIICategory 已迁移到 zephyr.governance.rule_patterns（ARCH-033 Phase 7 修正: 合并进 rule_patterns）


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


# _PII_PATTERNS 已迁移到 zephyr.governance.rule_patterns（ARCH-033 Phase 7 修正: 合并进 rule_patterns）

_MASK_CHAR = "*"
_HASH_SALT = "zephyr-pii-hash-salt"


class PrivacyGuard:
    def __init__(
        self,
        custom_patterns: dict[PIICategory, list[str]] | None = None,
        default_policy: RedactionPolicy = RedactionPolicy.MASK,
    ) -> None:
        self._default_policy = default_policy
        self._patterns: dict[PIICategory, list[re.Pattern[str]]] = dict(PII_PATTERNS)
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
            if effective_policy is RedactionPolicy.MASK:
                replacement_text = (
                    original[:2] + _MASK_CHAR * (len(original) - 4) + original[-2:]
                    if len(original) > 4
                    else _MASK_CHAR * len(original)
                )
            elif effective_policy is RedactionPolicy.HASH:
                replacement_text = f"[HASH:{hash_path(original)}]"
            elif effective_policy is RedactionPolicy.REMOVE:
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
