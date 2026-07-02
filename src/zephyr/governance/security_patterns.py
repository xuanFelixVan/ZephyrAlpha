# [BLUEPRINT] MOD-GOV-security_patterns | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md
# [MODULE] zephyr.governance.security_patterns
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] (none — pure constants module)
# [CONSUMERS] zephyr.governance.semantic_auditor.kb_gate; zephyr.governance.semantic_audit.kb_gate; zephyr.governance.audit_trail.kb_gate; zephyr.governance.semantic_auditor.privacy; zephyr.governance.semantic_audit.privacy; zephyr.governance.audit_trail.privacy
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 安全审计模式唯一真源——PIICategory 枚举 + POISONING_INDICATORS + PII_PATTERNS；三包(semantic_auditor/semantic_audit/audit_trail)共同 import，禁止重新定义；模式变更 MUST 同步审计三包使用处
# [MODIFY-GUARD] 模式变更 MUST 同步审计三包使用处
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 无运行时错误(纯常量模块)
# [TESTS] tests/governance/test_security_patterns.py
# [A_module] module_id=MOD-GOV-security_patterns | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""security_patterns.py — 安全审计模式唯一真源 (SSoT)

病根 (2026-07-02 SSoT 审计发现, ARCH-033 Phase 7):
- _POISONING_INDICATORS 在 semantic_auditor/kb_gate.py, semantic_audit/kb_gate.py,
  audit_trail/kb_gate.py 各定义一次（3 处真重复）
- _PII_PATTERNS 在 semantic_auditor/privacy.py, semantic_audit/privacy.py,
  audit_trail/privacy.py 各定义一次（3 处真重复）
- PIICategory 枚举同样三处重复定义
- 根因：三包(semantic_auditor/semantic_audit/audit_trail)未完成合并，各自携带同名
  kb_gate.py/privacy.py，安全审计模式被裸复制

治本:
- 本模块集中定义安全审计模式，三包共同 import
- 对标 SCRIPT-QUALITY-001 D-D-04 (同一概念只在一处定义)
- 三包合并(移动文件/改 blueprint 注册)留作后续独立 ARCH 任务，本轮仅做 SSoT 收敛

架构边界:
- src/zephyr/ 是 runtime 代码 (importable as zephyr.*)
- 本模块在 src/ 下，三包(semantic_auditor/semantic_audit/audit_trail)均可 import

Usage::

    from zephyr.governance.security_patterns import (
        PIICategory,
        POISONING_INDICATORS,
        PII_PATTERNS,
    )
"""

from __future__ import annotations

import re
from enum import Enum

__all__ = [
    "PIICategory",
    "POISONING_INDICATORS",
    "PII_PATTERNS",
]


class PIICategory(str, Enum):
    """PII 类别枚举。"""

    EMAIL = "email"
    PHONE = "phone"
    SSN = "ssn"
    CREDIT_CARD = "credit_card"
    API_KEY = "api_key"
    IP_ADDRESS = "ip_address"
    CUSTOM = "custom"


# KB 投毒检测指标——用于 kb_gate.py 的内容安全扫描
# 消费者: semantic_auditor/kb_gate.py + semantic_audit/kb_gate.py + audit_trail/kb_gate.py
POISONING_INDICATORS: list[re.Pattern[str]] = [
    re.compile(
        r"(ignore|disregard|override|bypass)\s+(all|previous|above|prior)\s*(instructions|rules|guidelines)",
        re.IGNORECASE,
    ),
    re.compile(r"(you\s+are\s+now|act\s+as|pretend\s+to\s+be)\s*a?\s*(system|admin|root|superuser)", re.IGNORECASE),
    re.compile(r"(delete|remove|drop|truncate)\s+(all|every|entire)\s*(file|record|entry|knowledge)", re.IGNORECASE),
    re.compile(r"(inject|insert|plant)\s*(malicious|harmful|backdoor|payload)", re.IGNORECASE),
    re.compile(r"(sudo|chmod|chown|exec|eval|system|subprocess)\s*[\(\[]", re.IGNORECASE),
]


# PII 检测模式——用于 privacy.py 的 PII 扫描与脱敏
# 消费者: semantic_auditor/privacy.py + semantic_audit/privacy.py + audit_trail/privacy.py
PII_PATTERNS: dict[PIICategory, list[re.Pattern[str]]] = {
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
