# [BLUEPRINT] MOD-INF-028 | docs/03_modules/_cross_layer/semantic_auditor/blueprint.md | §0.1
# [MODULE] zephyr.governance.semantic_audit.privacy
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.gov_audit.privacy
# [CONSUMERS] zephyr.governance.semantic_audit.__init__(lazy re-export)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] re-export shim; canonical implementation at zephyr.gov_audit.privacy (MOD-INF-020); no own logic
# [MODIFY-GUARD] semantic_auditor/blueprint.md; semantic_auditor/__init__.py __all__
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError if gov_audit.privacy unavailable
# [TESTS] tests/governance/audit/test_privacy.py; tests/semantic_auditor/test_semantic_auditor.py
# [A_module] module_id=MOD-INF-028 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
privacy — re-export shim for zephyr.gov_audit.privacy (MOD-INF-020 canonical).

治本（AI-AUDIT12 双真源收敛，2026-09-05）：本文件与 zephyr.gov_audit/privacy.py
自 587b569942 起为同一功能的双份承载（PII 检测/脱敏；gov_audit 版为超集，另含
Stage 4 公共化 properties），违反真源唯一。收敛裁定：gov_audit 版（超集）为唯一
实现真源；本文件降级为 re-export shim（red_blue_validator 既有范式）。
蓝图 §0.1 本行标注"挂靠自 MOD-INF-020"，本收敛使物理事实与蓝图声明一致。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: gov_audit.privacy 公共符号
#   fields: PIIDetection/PIIScanResult/PrivacyGuard/RedactionPolicy/hash_path
#   code: zephyr.gov_audit.privacy
# 层: 算法
# - id: A1
#   name_zh: ① 符号转发
#   name_en: re-export
#   intro: 原样转发 5 个公共符号，保证本模块导入路径兼容
#   desc: 单条 from-import + __all__，无自有逻辑
#   inputs: I1
#   outputs: 5 个公共符号
#   invariant: re-export shim，不包含任何自有实现
# 层: 输出
# - id: O1
#   name_zh: 隐私检查公共符号
#   name_en: public symbols
#   downstream: zephyr.governance.semantic_audit.__init__
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from zephyr.gov_audit.privacy import (  # noqa: F401
    PIICategory,
    PIIDetection,
    PII_PATTERNS,
    PIIScanResult,
    PrivacyGuard,
    RedactionPolicy,
    hash_path,
)

__all__ = [
    "PIICategory",
    "PIIDetection",
    "PII_PATTERNS",
    "PIIScanResult",
    "PrivacyGuard",
    "RedactionPolicy",
    "hash_path",
]
