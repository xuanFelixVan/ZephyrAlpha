# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md
# [MODULE] zephyr.governance.code_dedup.trackers
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.code_dedup
# [CONSUMERS] zephyr.governance.__init__（blind_spot_tracker→BlindSpotStatus）
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] tracker族子包; 新增文件MUST在capability_canonical_file_registry.yaml登记creation_token
# [MODIFY-GUARD] 新增文件需登记creation_tokens字段
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/governance/observability/test_hotspot_tracker.py等
# [A_module] module_id=MOD-INF-017_trackers | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""tracker 族子包 — 风险/盲点/热点跟踪器集合.

从 code_dedup/ 根目录迁入以符合 GOV-DOC-018 阈值（根目录 ≤ 60）.
"""

__all__ = ['blind_spot_tracker', 'consequence_tracker', 'hotspot_tracker', 'import_surface_tracker', 'question_tracker', 'risk_mitigation_tracker']

