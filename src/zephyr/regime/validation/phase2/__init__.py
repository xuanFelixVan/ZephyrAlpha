# [BLUEPRINT] MOD-REGIME_VAL-002 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [MODULE] zephyr.regime.validation.phase2
# [DOMAIN] D_REGIME
# [DEPENDENCIES] zephyr.regime.core.regime_detector; zephyr.regime.regime_feature_builder; numpy; pandas
# [CONSUMERS] scripts.tests.run_phase2_validation; BM-BT-05
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 四验证器(A1/A2/B1/B4)单一职责, 可独立运行也可被 phase2_runner 编排; 任一硬失败=模型不可信
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [TTL] permanent
# [ARCH-REF] #12_regime_phase2_validation §2
"""


Phase 2 模型质量验证（12_regime_phase2_validation）.

四验证器:
  A1 - 样本充足性（稀有态够 HMM 学吗）
  A2 - HMM 过拟合（IS/OOS 一致率）
  B1 - 概率校准度（P=80% 真有 80% 吗）
  B4 - 转换触发准确性（8 转换时点吻合吗）

第一批 MVP: A1 + B4
第二批:     A2 + B1

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: a1_sample_sufficiency 子模块符号 3个
#   fields: A1Report / A1SampleSufficiency / A1StateVerdict
#   code: zephyr.regime.validation.phase2.a1_sample_sufficiency
# - id: I2
#   name: a2_hmm_overfitting 子模块符号 3个
#   fields: A2HmmOverfitting / A2Report / A2Verdict
#   code: zephyr.regime.validation.phase2.a2_hmm_overfitting
# - id: I3
#   name: b1_probability_calibration 子模块符号 3个
#   fields: B1ProbabilityCalibration / B1Report / B1Verdict
#   code: zephyr.regime.validation.phase2.b1_probability_calibration
# - id: I4
#   name: b4_transition_accuracy 子模块符号 3个
#   fields: B4EventMatch / B4Report / B4TransitionAccuracy
#   code: zephyr.regime.validation.phase2.b4_transition_accuracy
# - id: I5
#   name: phase2_runner 子模块符号 2个
#   fields: Phase2Report / Phase2Runner
#   code: zephyr.regime.validation.phase2.phase2_runner
# 层: 算法
# - id: A1
#   name_zh: ① 包级聚合再导出
#   name_en: zephyr.regime.validation.phase2.__init__
#   intro: Phase 2 模型质量验证（12_regime_phase2_validation）.
#   desc: MOD-REGIME_VAL-002 包入口，包级聚合再导出并声明 __all__（14项）
#   inputs: I1 I2 I3 I4 I5
#   outputs: zephyr.regime.validation.phase2 包级公共命名空间
#   invariant: 包级导出以 __all__ 声明为准（14项）
# 层: 输出
# - id: O1
#   name_zh: zephyr.regime.validation.phase2 包公共 API
#   name_en: __all__ 14项
#   intro: Phase 2 模型质量验证（12_regime_phase2_validation）.——对外统一出口
#   downstream: 见蓝图头 [CONSUMERS] 声明
# [/ALGO_FLOW]
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# I5 --> A1
# A1 --> O1
"""

from zephyr.regime.validation.phase2.a1_sample_sufficiency import (
    A1Report,
    A1SampleSufficiency,
    A1StateVerdict,
)
from zephyr.regime.validation.phase2.a2_hmm_overfitting import (
    A2HmmOverfitting,
    A2Report,
    A2Verdict,
)
from zephyr.regime.validation.phase2.b1_probability_calibration import (
    B1ProbabilityCalibration,
    B1Report,
    B1Verdict,
)
from zephyr.regime.validation.phase2.b4_transition_accuracy import (
    B4EventMatch,
    B4Report,
    B4TransitionAccuracy,
)
from zephyr.regime.validation.phase2.phase2_runner import (
    Phase2Report,
    Phase2Runner,
)

__all__ = [
    "A1Report",
    "A1SampleSufficiency",
    "A1StateVerdict",
    "A2HmmOverfitting",
    "A2Report",
    "A2Verdict",
    "B1ProbabilityCalibration",
    "B1Report",
    "B1Verdict",
    "B4EventMatch",
    "B4Report",
    "B4TransitionAccuracy",
    "Phase2Report",
    "Phase2Runner",
]
