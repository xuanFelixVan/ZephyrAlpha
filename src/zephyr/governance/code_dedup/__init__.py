# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain-governance/code-dedup-engine/blueprint.md
# [MODULE] zephyr.governance.code_dedup
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.governance.__init__（4处import: blind_spot_tracker/canary_manager/cli/phase_executor）
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] MOD-INF-017蓝图模块的唯一物理位置; 新增文件MUST在capability_canonical_file_registry.yaml登记creation_token
# [MODIFY-GUARD] 新增文件需登记capability_canonical_file_registry.yaml的creation_tokens字段
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/governance/code_quality/test_code_dedup_engine.py, tests/governance/code_quality/test_ast_comparator.py, tests/governance/code_quality/test_simplicity_auditor.py
# [A_module] module_id=MOD-INF-017_code_dedup | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""code-dedup-engine 子包 — 重复代码检测与治理引擎.

本子包收录 MOD-INF-017 蓝图下的所有模块，从 governance 根目录迁入以符合
GOV-DOC-018 文件夹容量阈值（根目录 .py 文件 ≤ 60）和 ARCH-031 命名约定
（属于子模块的文件必须放在子目录）.

命名约定（ARCH-031）:
  - 新增文件 MUST 以功能角色前缀命名（如 detector_*/auditor_*/guard_*/tracker_*）
  - 或登记到 capability_canonical_file_registry.yaml 的 creation_tokens 字段
  - 现有文件为 grandfathered（迁移时保留原名）
"""
