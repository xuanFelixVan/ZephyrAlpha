# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.docs.cold_start_manual
# [DOMAIN] D_OPS
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_cold_start_manual | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Cold Start Manual — v0.8.0 R96

Blindspot: FLE starts with empty KB; first 100 anomalies misdiagnosed.
Risk: R96 — Cold start period produces maximum false positives.
"""

COLD_START_GUIDE = """
FLE Cold Start Protocol:
1. First 24h: OBSERVE_ONLY (autonomy_max_level=0)
2. 24h-72h: NOTIFY_OWNER for all anomalies
3. 72h+: Graduated autonomy based on precision@k > 0.7
"""
