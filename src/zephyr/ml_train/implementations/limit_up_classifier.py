# [BLUEPRINT] MOD-ML-001 | docs/03_modules/_domain_machine_learning_train/blueprint.md
# [MODULE] zephyr.ml_train.implementations.limit_up_classifier
# [DOMAIN] D_ML_TRAIN
# [DEPENDENCIES] zephyr.ml_train.trainer_base; zephyr.ml_train.services.sentiment_sft_entry; numpy
# [CONSUMERS] MOD-ML-001 training_pipeline（编排位预留）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 骨架态禁真训练（train 恒抛 ZA-MLT-0003）；特征接口校验可用；B-007 人工闸门未批前不得启用
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CandidateTrainDisabledError(ZA-MLT-0003)——骨架态 train 调用即抛；特征缺失→ValueError
# [TESTS] tests/ml_train/test_gap_f35_candidate_skeletons.py
# [A_module] module_id=MOD-ML-CLS1 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

"""D_ML_TRAIN — GAP-F-35 打板涨停概率分类器骨架（ML-CLS-001）。

model_registry 既有候选条目 ML-CLS-001（首板/连板次日涨停概率，LightGBM 架构）。
本模块只落训练管线骨架 + 数据接口位：

- ``LIMIT_UP_FEATURES``：数据接口位（封单比/首封时间/开板次数等，对齐 GAP-F-13
  limit_up_pool 明细字段规划）。
- ``check_feature_interface()``：特征 schema 校验（训练前置门）。
- ``train()``：骨架态恒抛 ``CandidateTrainDisabledError``（ZA-MLT-0003）——
  禁真训练，待 B-007 人工闸门批准 + 数据源就绪后实现。
"""

from __future__ import annotations

import logging
from typing import Any, Final

from zephyr.ml_train.services.sentiment_sft_entry import CandidateTrainDisabledError
from zephyr.ml_train.trainer_base import ModelTrainerBase

_log = logging.getLogger(__name__)

#: 打板分类器特征接口位（对齐 limit_up_pool 明细字段，GAP-F-13 依赖）
LIMIT_UP_FEATURES: Final[tuple[str, ...]] = (
    "seal_ratio",  # 封单比（封单额/成交额）
    "first_seal_minutes",  # 首次封板距开盘分钟数
    "open_board_count",  # 开板次数
    "seal_duration_minutes",  # 封住时长
    "turnover_rate",  # 换手率
    "sector_limit_up_count",  # 同板块涨停家数（梯队语境）
)

_MODEL_ID: Final[str] = "ML-CLS-001"


class LimitUpClassifierSkeleton(ModelTrainerBase):
    """打板涨停概率分类器骨架（禁真训练）。

    数据接口：``features["X"]`` 为 dict[str, array-like]，键必须覆盖
    ``LIMIT_UP_FEATURES``；``target`` 为次日是否涨停 0/1 序列。
    """

    __model_id__ = _MODEL_ID

    def check_feature_interface(self, features: dict[str, Any]) -> bool:
        """训练前置门：特征 schema 校验（缺特征即 ValueError，指明缺哪个）。"""
        x = features.get("X")
        if not isinstance(x, dict):
            raise ValueError("features['X'] 需为 dict[str, array]（特征名→序列）")
        missing = [name for name in LIMIT_UP_FEATURES if name not in x]
        if missing:
            raise ValueError(f"特征缺失: {missing}（需覆盖 LIMIT_UP_FEATURES）")
        return True

    def train(
        self,
        features: dict[str, Any],
        target: object,
        idempotency_key: str,
    ) -> dict[str, float]:
        """骨架态禁真训练——校验特征接口后恒抛 ZA-MLT-0003。"""
        self.check_feature_interface(features)
        _log.warning("ML-CLS-001 骨架态禁真训练（key=%s），待 B-007 人工闸门", idempotency_key)
        raise CandidateTrainDisabledError(
            "ML-CLS-001 打板分类器为骨架态，真训练待 Owner 批准（B-007）+ 数据源就绪"
        )

    def validate(self, features: dict[str, Any], target: object) -> dict[str, float]:
        """骨架态无验证指标——校验特征接口后恒抛 ZA-MLT-0003。"""
        self.check_feature_interface(features)
        raise CandidateTrainDisabledError("ML-CLS-001 骨架态无 validate（模型未训练）")


__all__ = [
    "LIMIT_UP_FEATURES",
    "LimitUpClassifierSkeleton",
]
