# [BLUEPRINT] MOD-LLM_SECURITY | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [A_module] module_id=MOD-SEC_SELF_PROTECTION | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable

"""
# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: __init__.py
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 AccessPattern, AccessRule, AdversarialMutator, CodeIntegrityGuard, FileInte…
#   desc: __init__ import L0；__all__ 25 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（25 符号）
#   name_en: __all__
#   intro: AccessPattern, AccessRule, AdversarialMutator, CodeIntegrityGuard, FileIntegrit…
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

__all__ = [
    "AccessPattern",
    "AccessRule",
    "AdversarialMutator",
    "CodeIntegrityGuard",
    "FileIntegrityRecord",
    "IntegrityStatus",
    "IsolationAuditEntry",
    "IsolationLevel",
    "IsolationPolicy",
    "LSGIsolation",
    "MutatedPayload",
    "MutationReport",
    "MutationResult",
    "MutationTechnique",
    "PayloadResult",
    "RedTeamScanner",
    "ScanMode",
    "ScanReport",
    "ScanTarget",
    "ValidationLayer",
    "adversarial_mutator",
    "code_integrity",
    "isolation",
    "l7_validation",
    "red_team_scanner",
]
