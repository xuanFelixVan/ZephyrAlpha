# [BLUEPRINT] 90_methodology_open_questions.md §9（v2.0.0 裁定）
# [MODULE] zephyr.ml_train.core.sample_weights
# [DOMAIN] D_ML_TRAIN
# [DEPENDENCIES] numpy
# [CONSUMERS] 训练数据加载层（15 号/G01 接线待排期，本批仅交付模块本体）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] w(t)=0.5^(days_ago/(HL×252))；断裂期降权50%保留不剔除；未来日期拒绝
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 未来日期/非正半衰期→ValueError
# [TESTS] tests/ml_train/test_sample_weights.py
# [A_module] module_id=MOD-L11-SW | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""D_ML_TRAIN — 半衰期样本权重（90 号 Phase2 项，#9 数据分层修订采纳）

裁定真源：90_methodology_open_questions.md §9（v2.0.0）：
  ② 权重参数化改半衰期：sample_weight = 0.5 ** (days_ago / (HL*252))，
     HL 默认 2.5 年（与原"近1年=1.0/5年=0.3/10年=0.1"等价但更直观、单参数可调）；
  ③ 结构断裂期（2015 股灾/2018 熊市/2024 微盘崩盘）不剔除——降权 50% 保留，
     并单独作为压力测试集（剔除=丢掉最宝贵的极端 regime 训练信号）；
  断裂期清单配置化。

与 10 层数据留存分层（data_retention_contract，数据治理语义）正交——
留存管"数据存多久"，样本权重管"训练用多重"。

注意：本模块为 90 号 Phase2 交付物，MATURITY=testing；训练数据加载层接线挂起
待 Owner（宪章 B-007 纪律）。
"""

from __future__ import annotations

from datetime import date
from typing import Sequence

import numpy as np

__all__ = [
    "DEFAULT_HALF_LIFE_YEARS",
    "DEFAULT_BREAK_PERIODS",
    "DEFAULT_BREAK_DOWNWEIGHT",
    "compute_sample_weights",
]

#: 默认半衰期（年，90 号 §9 裁定②：HL 2-3 年，取 2.5）
DEFAULT_HALF_LIFE_YEARS: float = 2.5

#: 年化交易日基数（裁定实现式 days_ago/(HL*252)）
_TRADING_DAYS_PER_YEAR: float = 252.0

#: 默认结构断裂期清单（90 号 §9 裁定③：配置化，降权保留不剔除）
#: 2015 股灾（杠杆牛崩盘+2016-01 熔断）/ 2018 熊市（全年单边下行）/ 2024 微盘崩盘（流动性危机）
DEFAULT_BREAK_PERIODS: tuple[tuple[date, date], ...] = (
    (date(2015, 6, 12), date(2016, 2, 29)),
    (date(2018, 1, 24), date(2018, 12, 28)),
    (date(2024, 1, 2), date(2024, 2, 29)),
)

#: 断裂期降权系数（裁定③：降权 50% 保留）
DEFAULT_BREAK_DOWNWEIGHT: float = 0.5


def compute_sample_weights(
    dates: Sequence[date],
    reference_date: date,
    *,
    half_life_years: float = DEFAULT_HALF_LIFE_YEARS,
    break_periods: Sequence[tuple[date, date]] | None = None,
    break_downweight: float = DEFAULT_BREAK_DOWNWEIGHT,
) -> np.ndarray:
    """计算训练样本半衰期权重。

    Args:
        dates: 样本日期序列
        reference_date: 参照日（通常为训练截止日）
        half_life_years: 半衰期（年，默认 2.5）
        break_periods: 断裂期清单 [(start, end), ...]（None=默认三段）
        break_downweight: 断裂期降权系数（默认 0.5）

    Returns:
        np.ndarray 权重序列（与 dates 等长，∈(0,1]）

    Raises:
        ValueError: 样本日期晚于参照日 / 半衰期非正 / 降权系数越界
    """
    if half_life_years <= 0:
        raise ValueError(f"半衰期必须为正，实际 {half_life_years}")
    if not 0 < break_downweight <= 1:
        raise ValueError(f"断裂期降权系数必须在 (0,1]，实际 {break_downweight}")

    periods = DEFAULT_BREAK_PERIODS if break_periods is None else tuple(break_periods)

    ages = np.array([(reference_date - d).days for d in dates], dtype=float)
    if (ages < 0).any():
        raise ValueError("样本日期晚于参照日（未来样本）")

    weights = np.power(0.5, ages / (half_life_years * _TRADING_DAYS_PER_YEAR))

    if periods:
        in_break = np.array(
            [any(start <= d <= end for start, end in periods) for d in dates],
            dtype=bool,
        )
        weights = np.where(in_break, weights * break_downweight, weights)

    return weights
