# [BLUEPRINT] MOD-ML-001 | docs/03_modules/_domain_machine_learning_train/blueprint.md
# [MODULE] zephyr.ml_train.implementations.seat_pattern_classifier
# [DOMAIN] D_ML_TRAIN
# [DEPENDENCIES] zephyr.ml_train.trainer_base; zephyr.ml_train.services.sentiment_sft_entry; numpy
# [CONSUMERS] MOD-ML-001 training_pipeline（编排位预留）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 骨架态禁真训练（train 恒抛 ZA-MLT-0003）；前提=JOB-076 龙虎榜管道+3 个月数据积累（CAND-SEAT-001）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CandidateTrainDisabledError(ZA-MLT-0003)——骨架态 train 调用即抛；特征缺失→ValueError
# [TESTS] tests/ml_train/test_gap_f35_candidate_skeletons.py
# [A_module] module_id=MOD-ML-CLS2 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
D_ML_TRAIN — GAP-F-35 席位形态分类器骨架（ML-CLS-002）。

model_registry 既有候选条目 ML-CLS-002（席位上榜组合→次日溢价概率，
LightGBM/规则混合架构；前提：JOB-076 龙虎榜管道 + 3 个月数据积累）。
本模块只落训练管线骨架 + 数据接口位，train() 恒抛 ZA-MLT-0003 禁真训练。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: seat_pattern_classifier.py
# 层: 算法
# - id: A1
#   name_zh: ① SeatPatternClassifierSkeleton
#   name_en: SeatPatternClassifierSkeleton
#   intro: 席位形态分类器骨架（禁真训练）。
#   desc: 席位形态分类器骨架（禁真训练）。 数据接口：``features["X"]`` 为 dict[str, array-like]，键必须覆盖 ``SEAT_FEATURES``；`…；公共方法（定义序）: check_f…
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: SeatPatternClassifierSkeleton
#   downstream: MOD-ML-001 training_pipeline（编排位预留）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import logging
from typing import Any, Final

from zephyr.ml_train.services.sentiment_sft_entry import CandidateTrainDisabledError
from zephyr.ml_train.trainer_base import ModelTrainerBase

_log = logging.getLogger(__name__)

#: 席位形态特征接口位（对齐龙虎榜管道字段规划，DS-080）
SEAT_FEATURES: Final[tuple[str, ...]] = (
    "seat_net_buy_ratio",  # 席位净买入占成交比
    "top_seat_count",  # 知名席位上榜数
    "seat_concentration",  # 买一~买五集中度
    "institution_net_flag",  # 机构专用席位净买/净卖标记
    "hot_money_seat_flag",  # 游资席位标记
    "prior_seat_win_rate",  # 同席位组合历史次日溢价胜率
)

_MODEL_ID: Final[str] = "ML-CLS-002"


class SeatPatternClassifierSkeleton(ModelTrainerBase):
    """席位形态分类器骨架（禁真训练）。

    数据接口：``features["X"]`` 为 dict[str, array-like]，键必须覆盖
    ``SEAT_FEATURES``；``target`` 为次日溢价 0/1 序列。
    """

    __model_id__ = _MODEL_ID

    def check_feature_interface(self, features: dict[str, Any]) -> bool:
        """训练前置门：特征 schema 校验（缺特征即 ValueError，指明缺哪个）。"""
        x = features.get("X")
        if not isinstance(x, dict):
            raise ValueError("features['X'] 需为 dict[str, array]（特征名→序列）")
        missing = [name for name in SEAT_FEATURES if name not in x]
        if missing:
            raise ValueError(f"特征缺失: {missing}（需覆盖 SEAT_FEATURES）")
        return True

    def train(
        self,
        features: dict[str, Any],
        target: object,
        idempotency_key: str,
    ) -> dict[str, float]:
        """骨架态禁真训练——校验特征接口后恒抛 ZA-MLT-0003。"""
        self.check_feature_interface(features)
        _log.warning("ML-CLS-002 骨架态禁真训练（key=%s），待数据积累+B-007 闸门", idempotency_key)
        raise CandidateTrainDisabledError(
            "ML-CLS-002 席位分类器为骨架态，真训练待 JOB-076 数据积累 + Owner 批准（B-007）"
        )

    def validate(self, features: dict[str, Any], target: object) -> dict[str, float]:
        """骨架态无验证指标——校验特征接口后恒抛 ZA-MLT-0003。"""
        self.check_feature_interface(features)
        raise CandidateTrainDisabledError("ML-CLS-002 骨架态无 validate（模型未训练）")


__all__ = [
    "SEAT_FEATURES",
    "SeatPatternClassifierSkeleton",
]
