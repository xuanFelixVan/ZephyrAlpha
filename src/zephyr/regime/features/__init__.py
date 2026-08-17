# [BLUEPRINT] MOD-REGIME-002 | docs/03_modules/_domain_regime/regime_feature_builder/blueprint.md | §features_pkg
# [MODULE] zephyr.regime.features
# [DOMAIN] D_REGIME
# [DEPENDENCIES] —
# [CONSUMERS] MOD-REGIME-002(RegimeFeatureBuilder 消费 #12 筹码结构 / #5 空间位置 / S2 底部筹码 / 13 风险参数系数)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] regime 特征管道包——RegimeFeatures/OverlaySignals/RiskSignalInputs 的生成入口
# [MODIFY-GUARD] blueprint=docs/03_modules/_domain_regime/regime_feature_builder/blueprint.md
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] —
# [TESTS] tests/regime/test_chip_distribution_engine.py; tests/regime/test_risk_signal_builder.py; tests/regime/test_overlay_signals_builder.py
# [A_module] module_id=PKG-regime-features | layer=package | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

regime.features — regime 特征管道包（MOD-REGIME-002 子包）。

RegimeFeatureBuilder 生成的特征（RegimeFeatures / OverlaySignals / RiskSignalInputs）
所属包。当前含：
  - chip_distribution_engine（MOD-REGIME-005，筹码分布引擎）
  - market_features（HMM 6 特征之 F1/F3/F4/F5 市场级特征）
  - trend_features（HMM 6 特征之 F2a/F2b 趋势特征）
  - risk_features（Phase 2a，13 风险参数系数映射纯函数）
  - overlay_features（Phase 2b，8 转换评分/标志纯函数）

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 市场行情原始数据（由子模块消费）
#   fields: 指数收盘价 / 成交量 / 涨跌家数 / 筹码分布数据
#   code: 子模块 market_features / trend_features / chip_distribution_engine
# 层: 算法
# - id: A1
#   name_zh: ① 特征管道包入口
#   name_en: zephyr.regime.features 包命名空间
#   intro: 仅文档与命名空间聚合，本文件无执行逻辑，实际计算在 5 个子模块
#   desc: HMM 6 特征之市场级 F1/F3/F4/F5（market_features）+ 趋势 F2a/F2b（trend_features）+ 13 风险参数系数映射（risk_features）+ 8 转换评分/标志（overlay_features）+ 筹码分布引擎（chip_distribution_engine MOD-REGIME-005）
#   inputs: I1
#   outputs: 特征生成子模块命名空间
#   invariant: 本包是 RegimeFeatures / OverlaySignals / RiskSignalInputs 的生成入口（[INVARIANTS] 头）
# 层: 输出
# - id: O1
#   name_zh: regime 特征产物
#   name_en: RegimeFeatures / OverlaySignals / RiskSignalInputs
#   intro: 筹码结构 #12 / 空间位置 #5 / 底部筹码 S2 / 13 风险参数系数等特征产物
#   downstream: RegimeFeatureBuilder MOD-REGIME-002（[CONSUMERS] 头）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

__all__: list[str] = ["chip_distribution_engine", "market_features", "overlay_features", "regime_data_loader", "risk_features", "synthetic_vix", "trend_features", "wyckoff_engine"]
