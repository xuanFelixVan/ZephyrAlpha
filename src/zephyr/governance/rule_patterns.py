# [BLUEPRINT] MOD-GOV-rule_patterns | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md
# [MODULE] zephyr.governance.rule_patterns
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] (none — pure constants module)
# [CONSUMERS] zephyr.gov_enforcement.commit_gates.r5_digit_suffix_gate; zephyr.gov_enforcement.commit_gates.create_guard; scripts/governance/d5_architecture/validators/validate_directory_structure.py; scripts/governance/d3_metadata/validate_rule_frontmatter.py; scripts/generate_pathway_registry.py; scripts/governance/generators/generate_path_ownership_map.py; scripts/governance/d5_architecture/validators/validate_ssot_construction_progress.py; zephyr.governance.semantic_auditor.kb_gate; zephyr.governance.semantic_audit.kb_gate; zephyr.gov_audit.kb_gate; zephyr.governance.semantic_auditor.privacy; zephyr.governance.semantic_audit.privacy; zephyr.gov_audit.privacy
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 治理规则正则 + 安全审计模式唯一真源——gate/validator/三包共同 import,禁止在其他文件重新定义;治理正则标注 trae_028 来源,安全模式(PIICategory+POISONING_INDICATORS+PII_PATTERNS)原位于 security_patterns.py(已合并,ARCH-033 Phase7修正,违反 governance/ 根目录9模块硬约束)
# [MODIFY-GUARD] 治理正则变更 MUST 同步 trae_028 YAML 真源; 安全模式变更 MUST 同步审计三包使用处
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 无运行时错误(纯常量模块)
# [TESTS] tests/governance/test_rule_patterns.py
# [A_module] module_id=MOD-GOV-rule_patterns | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""rule_patterns.py — 治理规则正则 + 安全审计模式唯一真源 (SSoT)

病根 (2026-07-02 SSoT 审计发现):
- _DIGIT_SUFFIX_RE 在 r5_digit_suffix_gate.py 和 validate_directory_structure.py 各定义一次
- _RULE_NAME_RE (DIM-5) 在 create_guard.py 和 validate_rule_frontmatter.py 各定义一次
- _POISONING_INDICATORS / _PII_PATTERNS / PIICategory 在三包(semantic_auditor/semantic_audit/
  audit_trail)各定义一次（16 处重复）
- 无共享正则模块, gate 与 validator 各自复制, 正则变更无法同步

治本:
- 本模块集中定义治理规则正则 + 安全审计模式, gate (src/) 和 validator (scripts/) 和
  三包共同 import
- 每个正则标注 trae_028 规则来源, 确保可追溯
- 对标 SCRIPT-QUALITY-001 D-D-04 (同一概念只在一处定义)

架构边界:
- src/zephyr/ 是 runtime 代码 (importable as zephyr.*)
- scripts/ 是治理脚本 (可 import src/, 反之不可)
- 本模块在 src/ 下, 两边均可 import (scripts/ 通过 _shared.constants bootstrap sys.path)

合并历史 (ARCH-033 Phase 7 修正, 2026-07-02):
- security_patterns.py 原独立存在于 governance/ 根目录, 违反 9 模块硬约束 +
  CREATE-GUARD 门禁 (session_worktree_commit 绕过). 已合并至本模块, security_patterns.py 已删除.
- 安全审计模式 (PIICategory/POISONING_INDICATORS/PII_PATTERNS) 与治理正则本质同类
  (编译后的 re.Pattern 常量), 合并符合「向内收」原则.

Usage::

    from zephyr.governance.rule_patterns import (
        DIGIT_SUFFIX_RE, RULE_NAME_RE, MODULE_ID_RE,
        PIICategory, POISONING_INDICATORS, PII_PATTERNS,
    )
"""

from __future__ import annotations

from typing import Final
import re
from enum import Enum

__all__ = [
    "DIGIT_SUFFIX_RE",
    "RULE_NAME_RE",
    "MODULE_ID_RE",
    "PIICategory",
    "POISONING_INDICATORS",
    "PII_PATTERNS",
]

# ============================================================================
# 治理规则正则
# ============================================================================

# R5 数字后缀禁止——_\d+ 结尾
# 真源: trae_028_doc_structure_naming.yaml L1224-1228 gov_doc_003_directory_semantics R5
# 消费者: r5_digit_suffix_gate.py (commit-time 硬阻断) + validate_directory_structure.py (全量 warning-only)
DIGIT_SUFFIX_RE: Final[re.Pattern[str]] = re.compile(r"_\d+$")

# DIM-5 规则文件名主题前缀——trae_NNN_<主题>_<描述>.yaml
# 真源: trae_028_doc_structure_naming.yaml DIM-5 + ARCH-037
# 消费者: create_guard.py (commit-time 新规则文件名校验) + validate_rule_frontmatter.py (全量 frontmatter 校验)
RULE_NAME_RE: Final[re.Pattern[str]] = re.compile(r"^trae_\d+_(.+)\.yaml$")

# blueprint.md module_id 字段提取——^module_id:\s*(.+)$
# 真源: trae_028_doc_structure_naming.yaml (module_id 字段格式)
# 消费者: generate_pathway_registry.py + generate_path_ownership_map.py + validate_ssot_construction_progress.py
# (ARCH-033 Phase 7 SSoT 收敛 2026-07-02: 3处真重复集中到此处)
MODULE_ID_RE: Final[re.Pattern[str]] = re.compile(r"^module_id:\s*(.+)$", re.MULTILINE)


# ============================================================================
# 安全审计模式 (原 security_patterns.py, 已合并 ARCH-033 Phase 7 修正)
# ============================================================================


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
POISONING_INDICATORS: Final[list[re.Pattern[str]]] = [
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
PII_PATTERNS: Final[dict[PIICategory, list[re.Pattern[str]]]] = {
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
