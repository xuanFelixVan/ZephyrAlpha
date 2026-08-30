# [BLUEPRINT] MOD-INF-028 | docs/03_modules/_cross_layer/semantic-auditor/blueprint.md
# [MODULE] zephyr.governance.semantic_audit.privacy
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.governance.semantic_audit.__init__
# [CONSUMERS] 见蓝图 §4 接口契约
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 蓝图 §4 文件清单与代码双向对齐
# [MODIFY-GUARD] semantic-auditor/blueprint.md; semantic-auditor/__init__.py __all__
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] SemanticAuditError
# [TESTS] tests/semantic-auditor/
# [A_module] module_id=MOD-INF-028 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
[BLUEPRINT] MOD-INF-028 | docs/03_modules/_cross_layer/semantic-auditor/blueprint.md

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

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: path 参数
#   fields: 参数 path，类型注解 str
#   code: privacy.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① PrivacyGuard
#   name_en: PrivacyGuard
#   intro: class PrivacyGuard 源码 L142-L221
#   desc: 公共方法（定义序）: detect_pii, redact, hash_path；源码 L142-L221
#   inputs: custom_patterns default_policy
#   outputs: 返回值
# - id: A2
#   name_zh: ② hash_path
#   name_en: hash_path
#   intro: hash_path(path) 源码 L224-L227
#   desc: 源码 L224-L227
#   inputs: path
#   outputs: str
#   （注：A2 之后另有 3 个公共定义未列入（含 3 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: str
#   name_en: str
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 见蓝图 §4 接口契约
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import hashlib
import logging
import re
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from zephyr.governance.rule_patterns import (  # SSoT (ARCH-033 Phase 7 修正: 合并进 rule_patterns)
    PII_PATTERNS,
    PIICategory,
)

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
