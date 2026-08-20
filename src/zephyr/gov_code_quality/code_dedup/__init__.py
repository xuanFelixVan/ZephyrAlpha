# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md
# [MODULE] zephyr.gov_code_quality.code_dedup
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.governance.__init__（4处import: blind_spot_tracker/canary_manager/cli/phase_executor）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] MOD-INF-017蓝图模块的唯一物理位置; 新增文件MUST在capability_canonical_file_registry.yaml登记creation_token
# [MODIFY-GUARD] 新增文件需登记capability_canonical_file_registry.yaml的creation_tokens字段
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/governance/code_quality/test_code_dedup_engine.py, tests/governance/code_quality/test_ast_comparator.py, tests/governance/code_quality/test_simplicity_auditor.py
# [A_module] module_id=MOD-INF-017 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

code-dedup-engine 子包 — 重复代码检测与治理引擎.

本子包收录 MOD-INF-017 蓝图下的所有模块，从 governance 根目录迁入以符合
GOV-DOC-018 文件夹容量阈值（根目录 .py 文件 ≤ 60）和 ARCH-031 命名约定
（属于子模块的文件必须放在子目录）.

命名约定（ARCH-031）:
  - 新增文件 MUST 以功能角色前缀命名（如 detector_*/auditor_*/guard_*/tracker_*）
  - 或登记到 capability_canonical_file_registry.yaml 的 creation_tokens 字段
  - 现有文件为 grandfathered（迁移时保留原名）

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 子包内 58 个功能模块 Python源码
#   fields: detector_*/auditor_*/guard_*/tracker_* 等功能角色模块（annotations 到 verifier）
#   code: zephyr/gov_code_quality/code_dedup/ 目录 L32
# 层: 算法
# - id: A1
#   name_zh: ① 子包命名空间聚合导出
#   name_en: __init__ (code_dedup 包初始化)
#   intro: 声明这是 MOD-INF-017 重复代码治理引擎的唯一物理位置，导出58个子模块名单
#   desc: 仅定义 __version__=0.15.0、__module_id__=MOD-INF-017、__all__ 58项导出清单；无任何运行逻辑，import 时只做命名空间登记
#   inputs: I1
#   outputs: code_dedup 子包公共命名空间
#   invariant: MOD-INF-017蓝图模块唯一物理位置；新增文件MUST登记 capability_canonical_file_registry.yaml 的 creation_token
# 层: 输出
# - id: O1
#   name_zh: 子包公共导出清单
#   name_en: __all__ 58项
#   intro: 对外暴露58个重复代码检测/治理子模块供上层 import
#   downstream: zephyr.governance.__init__（4处import: blind_spot_tracker/canary_manager/cli/phase_executor）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

__version__ = "0.15.0"
__module_id__ = "MOD-INF-017"

from typing import Final

__all__: Final = [
    "annotations",
    "ast_comparator",
    "atomic_fixer",
    "auto_fixer",
    "behavioral_sampler",
    "behavioral_trust_checker",
    "cache_manager",
    "canary_manager",
    "canary_register",
    "cli",
    "code_analyzer_runner",
    "code_simulator",
    "config",
    "contract_consistency_checker",
    "cross_boundary_detector",
    "dead_module_detector",
    "debt_projector",
    "decision_auditor",
    "degradation",
    "diff_detector",
    "doom_loop_guard",
    "exit_codes",
    "extraction_safety",
    "false_negative_auditor",
    "fifteen_dimension_auditor",
    "file_creator",
    "function_discovery",
    "grandfather_manager",
    "health_monitor",
    "integration_hub",
    "integrations",
    "micro_clone_detector",
    "mock_duplicate_generator",
    "monoculture_guard",
    "observation_window_guard",
    "path_index_validator",
    "phase_executor",
    "policy_tree_validator",
    "pre_apply_integrity_gate",
    "prioritizer",
    "recovery_manifest_writer",
    "report",
    "risk_mitigator",
    "self_scanner",
    "sensitivity_sweeper",
    "shadow_trust_validator",
    "shadow_verifier",
    "shared_evolver",
    "shared_lifecycle_manager",
    "signature_matcher",
    "simplicity_auditor",
    "ssot_registrar",
    "stale_shared_detector",
    "success_validator",
    "symbol_index",
    "thematic_clusterer",
    "verifier",
]
