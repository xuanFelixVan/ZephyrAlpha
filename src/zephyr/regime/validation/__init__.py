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
"""

regime 验证层 —— Phase 1 C1 (Shrinkage 节流) + Phase 2 (模型质量).

Phase 1: src/zephyr/backtest/regime_validation/c1_comparator.py (Shrinkage 开/关对比)
Phase 2: src/zephyr/regime/validation/phase2/ (A1/A2/B1/B4 模型质量)

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: RegimeDetector 输出（7维灰度概率/置信度/Shrinkage）
#   fields: 灰度概率分布 + 置信度 + 风险节流因子
#   code: zephyr.regime.core.regime_detector
# - id: I2
#   name: RegimeFeatureBuilder 特征输出
#   fields: regime 输入特征（波动率/趋势/相关性等）
#   code: zephyr.regime.regime_feature_builder
# 层: 算法
# - id: A1
#   name_zh: ① 验证层包入口（Phase1 C1 + Phase2 模型质量路由说明）
#   name_en: zephyr.regime.validation __init__
#   intro: regime 验证层包说明，把验证职责路由到 Phase1 C1 对比器和 Phase2 A1/A2/B1/B4 验证器
#   desc: 纯包文档模块：声明 Phase1=backtest/regime_validation/c1_comparator.py(Shrinkage开/关对比)，Phase2=regime/validation/phase2/(A1/A2/B1/B4 模型质量)，只消费 detector/builder 输出不改内部状态
#   inputs: I1 I2
#   outputs: 验证入口约定（指向 C1 对比器与 Phase2 验证器）
#   invariant: Phase2 验证器只消费 detector/builder 输出, 不修改其内部状态(OCP)
# 层: 输出
# - id: O1
#   name_zh: regime 验证结果（Phase2 验证报告）
#   name_en: phase2 validation results
#   intro: 供 Phase2 实模式验证脚本与 HMM 模型质量验证基准使用的验证产出
#   downstream: scripts.tests.run_phase2_validation(real模式); BM-BT-05(HMM模型质量验证)
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> O1
"""

__all__: list[str] = []
