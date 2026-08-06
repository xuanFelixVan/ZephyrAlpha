# [BLUEPRINT] MOD-REGIME-VAL-002 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [MODULE] zephyr.regime.validation
# [DOMAIN] D_REGIME
# [DEPENDENCIES] zephyr.regime.core.regime_detector; zephyr.regime.regime_feature_builder
# [CONSUMERS] scripts.tests.run_phase2_validation(real模式); BM-BT-05(HMM模型质量验证)
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] Phase2 验证器只消费 detector/builder 输出, 不修改其内部状态(OCP)
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [TTL] permanent
"""regime 验证层 —— Phase 1 C1 (Shrinkage 节流) + Phase 2 (模型质量).

Phase 1: src/zephyr/backtest/regime_validation/c1_comparator.py (Shrinkage 开/关对比)
Phase 2: src/zephyr/regime/validation/phase2/ (A1/A2/B1/B4 模型质量)
"""
