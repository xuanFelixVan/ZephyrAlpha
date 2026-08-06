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
# [ARCH-REF] #discussion_003 §2
"""Phase 2 模型质量验证（discussion_003）.

四验证器:
  A1 - 样本充足性（稀有态够 HMM 学吗）
  A2 - HMM 过拟合（IS/OOS 一致率）
  B1 - 概率校准度（P=80% 真有 80% 吗）
  B4 - 转换触发准确性（8 转换时点吻合吗）

第一批 MVP: A1 + B4
第二批:     A2 + B1
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
