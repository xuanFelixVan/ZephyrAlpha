# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md
# [MODULE] zephyr.gov_code_quality.code_dedup.trackers
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_code_quality.code_dedup
# [CONSUMERS] zephyr.governance.__init__（blind_spot_tracker->BlindSpotStatus）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] tracker族子包; 新增文件MUST在capability_canonical_file_registry.yaml登记creation_token
# [MODIFY-GUARD] 新增文件需登记creation_tokens字段
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/governance/observability/test_hotspot_tracker.py等
# [A_module] module_id=MOD-INF-017 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
tracker 族子包 — 风险/盲点/热点跟踪器集合.

从 code_dedup/ 根目录迁入以符合 GOV-DOC-018 阈值（根目录 ≤ 60）.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包内子模块公共符号
#   fields: import 再导出符号: Final
#   code: __init__.py import L49
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 Final（共 1 符号）
#   desc: __init__ import L49；__all__ 0 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（1 符号）
#   name_en: __all__
#   intro: Final
#   downstream: zephyr.governance.__init__（blind_spot_tracker->BlindSpotStatus）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from typing import Final

__all__: Final = [
    "blind_spot_tracker",
    "consequence_tracker",
    "hotspot_tracker",
    "import_surface_tracker",
    "question_tracker",
    "risk_mitigation_tracker",
]
