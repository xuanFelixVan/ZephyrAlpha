# [BLUEPRINT] MOD-ML-008 | docs/03_modules/_domain_machine_learning_train/blueprint.md
# [MODULE] zephyr.ml_train.meta_learning_rsi
# [DOMAIN] D_ML_TRAIN
# [DEPENDENCIES] numpy
# [CONSUMERS] （RSI 类信号按 regime 自适应周期消费方）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 无历史记录时推荐 fail-closed 回默认周期；候选周期白名单外拒绝记录；纯内存态无副作用
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] MetaLearningRsiError(ZA-MLT-0011)——非法周期/短序列/白名单外周期/空 regime/非有限 score
# [TESTS] tests/ml_train/test_meta_learning_rsi.py
# [A_module] module_id=MOD-ML-008 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
元学习 RSI（MOD-ML-008）——轻量可单测实现。

两层结构：
1. ``compute_rsi``：标准 Wilder RSI（SMA 种子 + 平滑递推），纯 numpy。
2. ``MetaLearningRsi``：跨任务经验库——按 regime 记录各候选周期的历史表现分
   （如 IC/Sharpe），recommend_period 返回该 regime 历史均分最优周期；
   无记录 regime fail-closed 回默认周期（source="default" 显式标记）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: prices 参数
#   fields: 参数 prices，类型注解 np.ndarray
#   code: meta_learning_rsi.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: period 参数
#   fields: 参数 period（无注解）
#   code: meta_learning_rsi.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① compute_rsi
#   name_en: compute_rsi
#   intro: Wilder RSI。
#   desc: Wilder RSI。返回长度 len(prices)-1，前 period-1 项为 NaN（warmup）。；源码 L89-L120
#   inputs: prices period
#   outputs: np.ndarray
# - id: A2
#   name_zh: ② MetaLearningRsi
#   name_en: MetaLearningRsi
#   intro: RSI 周期元学习（按 regime 推荐历史最优周期）。
#   desc: RSI 周期元学习（按 regime 推荐历史最优周期）。；公共方法（定义序）: record_performance, recommend_period, rsi；源码 L123-L168
#   inputs: candidate_periods default_period
#   outputs: 返回值
#   （注：A2 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: np.ndarray
#   name_en: np.ndarray
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: （RSI 类信号按 regime 自适应周期消费方）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

from typing import Final

import numpy as np

__all__: Final = [
    "MetaLearningRsi",
    "MetaLearningRsiError",
    "compute_rsi",
]

_DEFAULT_CANDIDATE_PERIODS: Final[tuple[int, ...]] = (7, 14, 21)


class MetaLearningRsiError(Exception):
    """ZA-MLT-0011: 元学习 RSI 输入非法。"""

    error_code = "ZA-MLT-0011"


def compute_rsi(prices: np.ndarray, *, period: int = 14) -> np.ndarray:
    """Wilder RSI。返回长度 len(prices)-1，前 period-1 项为 NaN（warmup）。"""
    if period <= 0:
        raise MetaLearningRsiError(f"period 必须为正: {period}")
    p = np.asarray(prices, dtype=float).ravel()
    if p.size <= period:
        raise MetaLearningRsiError(f"序列长度需 > period: {p.size} vs {period}")
    if not np.all(np.isfinite(p)):
        raise MetaLearningRsiError("价格序列含非有限值")

    deltas = np.diff(p)
    gains = np.clip(deltas, 0.0, None)
    losses = np.clip(-deltas, 0.0, None)

    rsi = np.full(deltas.size, np.nan)
    avg_gain = gains[:period].mean()
    avg_loss = losses[:period].mean()

    def _rsi_value(g: float, l: float) -> float:
        if l == 0.0 and g == 0.0:
            return 50.0
        if l == 0.0:
            return 100.0
        rs = g / l
        return 100.0 - 100.0 / (1.0 + rs)

    rsi[period - 1] = _rsi_value(avg_gain, avg_loss)
    for i in range(period, deltas.size):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
        rsi[i] = _rsi_value(avg_gain, avg_loss)
    return rsi


class MetaLearningRsi:
    """RSI 周期元学习（按 regime 推荐历史最优周期）。"""

    def __init__(
        self,
        *,
        candidate_periods: tuple[int, ...] = _DEFAULT_CANDIDATE_PERIODS,
        default_period: int = 14,
    ) -> None:
        if not candidate_periods or any(p <= 0 for p in candidate_periods):
            raise MetaLearningRsiError(f"候选周期非法: {candidate_periods}")
        if default_period <= 0:
            raise MetaLearningRsiError(f"默认周期非法: {default_period}")
        self._candidates = tuple(candidate_periods)
        self._default_period = default_period
        self._records: dict[str, dict[int, list[float]]] = {}

    def record_performance(self, *, period: int, regime: str, score: float) -> None:
        """记录某 regime 下某周期的一次表现分。"""
        if period not in self._candidates:
            raise MetaLearningRsiError(f"周期不在候选白名单: {period}（{self._candidates}）")
        if not regime:
            raise MetaLearningRsiError("regime 不得为空")
        s = float(score)
        if not np.isfinite(s):
            raise MetaLearningRsiError(f"score 必须有限: {score}")
        self._records.setdefault(regime, {}).setdefault(period, []).append(s)

    def recommend_period(self, regime: str) -> dict:
        """推荐 regime 历史均分最优周期；无记录 fail-closed 回默认。"""
        regime_records = self._records.get(regime)
        if not regime_records:
            return {"period": self._default_period, "source": "default", "score": None}
        best_period = None
        best_score = float("-inf")
        for period, scores in sorted(regime_records.items()):
            mean_score = sum(scores) / len(scores)
            if mean_score > best_score:
                best_score = mean_score
                best_period = period
        return {"period": best_period, "source": "meta_learning", "score": best_score}

    def rsi(self, prices: np.ndarray, *, regime: str) -> np.ndarray:
        """按 regime 推荐周期计算 RSI（便捷组合接口）。"""
        period = int(self.recommend_period(regime)["period"])
        return compute_rsi(prices, period=period)
