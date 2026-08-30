# [BLUEPRINT] MOD-ML-003 | docs/03_modules/_domain_machine_learning_train/blueprint.md
# [MODULE] zephyr.ml_train.training_dataset_manager
# [DOMAIN] D_ML_TRAIN
# [TTL] permanent
# ml_train/training_dataset_manager — MOD-ML-003 训练数据集管理包

"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包内子模块公共符号
#   fields: import 再导出符号: DatasetLineageError, DatasetSnapshot, TrainingDatasetManager
#   code: __init__.py import L37
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 DatasetLineageError, DatasetSnapshot, TrainingDatasetManager（共 3 符号）
#   desc: __init__ import L37；__all__ 3 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（3 符号）
#   name_en: __all__
#   intro: DatasetLineageError, DatasetSnapshot, TrainingDatasetManager
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from zephyr.ml_train.training_dataset_manager.manager import (
    DatasetLineageError,
    DatasetSnapshot,
    TrainingDatasetManager,
)

__all__ = [
    "DatasetLineageError",
    "DatasetSnapshot",
    "TrainingDatasetManager",
]
