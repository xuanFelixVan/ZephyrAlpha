# [BLUEPRINT] MOD-INF-018 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [A_module] module_id=MOD-SEC-guards | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# Package marker for *_guard.py modules (ARCH-035 suffix-based grouping)

"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包内子模块公共符号
#   fields: import 再导出符号: Final
#   code: __init__.py import L36
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 Final（共 1 符号）
#   desc: __init__ import L36；__all__ 0 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（1 符号）
#   name_en: __all__
#   intro: Final
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from typing import Final

__all__: Final = [
    "abac_guard",
    "anti_pattern_guard",
    "audit_log_guard",
    "cybersec_2026_guard",
    "input_guard",
    "memory_guard",
    "memory_provenance_guard",
    "native_api_guard",
    "novel_attack_guard",
    "output_guard",
    "path_guard",
    "permission_guard",
    "rbac_guard",
    "replay_attack_guard",
    "rule_injection_guard",
    "sequence_guard",
    "toctou_guard",
    "vibe_coding_guard",
]
