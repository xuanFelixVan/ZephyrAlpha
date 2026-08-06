# [BLUEPRINT] MOD-REGIME-002 | docs/03_modules/_domain_regime/regime_feature_builder/blueprint.md | §features_pkg
# [MODULE] zephyr.regime.features
# [DOMAIN] D_REGIME
# [DEPENDENCIES] —
# [CONSUMERS] MOD-REGIME-002(RegimeFeatureBuilder 消费 #12 筹码结构 / #5 空间位置 / S2 底部筹码 / 13 风险参数系数)
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] regime 特征管道包——RegimeFeatures/OverlaySignals/RiskSignalInputs 的生成入口
# [MODIFY-GUARD] blueprint=docs/03_modules/_domain_regime/regime_feature_builder/blueprint.md
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] —
# [TESTS] tests/regime/test_chip_distribution_engine.py; tests/regime/test_risk_signal_builder.py; tests/regime/test_overlay_signals_builder.py
# [A_module] module_id=PKG-regime-features | layer=package | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""regime.features — regime 特征管道包（MOD-REGIME-002 子包）。

RegimeFeatureBuilder 生成的特征（RegimeFeatures / OverlaySignals / RiskSignalInputs）
所属包。当前含：
  - chip_distribution_engine（MOD-REGIME-005，筹码分布引擎）
  - market_features（HMM 6 特征之 F1/F3/F4/F5 市场级特征）
  - trend_features（HMM 6 特征之 F2a/F2b 趋势特征）
  - risk_features（Phase 2a，13 风险参数系数映射纯函数）
  - overlay_features（Phase 2b，8 转换评分/标志纯函数）
"""
