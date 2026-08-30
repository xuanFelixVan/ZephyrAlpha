# [BLUEPRINT] MOD-SIG-053 | docs/03_modules/MOD-SIG-053/
# [MODULE] zephyr.signal_ashare.xlstm_long_memory
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] numpy
# [CONSUMERS] （远期：长记忆时序特征消费方）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 未训练时 predict 一律 fail-closed（ValueError）；不引 torch 等大模型依赖——真训练/真推理属 B-007 人工闸门；decay ∈ (0,1]
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 短序列/非有限值/非法 horizon/非法 decay/未训练 predict → ValueError
# [TESTS] tests/signal_ashare/test_xlstm_long_memory.py
# [A_module] module_id=MOD-SIG-053 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
xLSTM 长记忆（MOD-SIG-053）——接口契约 + 轻量占位实现。

xLSTM（扩展 LSTM 长程记忆架构）属远期增强候选。本模块只立接口契约：predict
签名/输入校验/未训练 fail-closed。**不引 torch 等大模型依赖**——真训练/真推理
属 B-007 人工闸门。

占位记忆路径：fit_baseline 以 EMA 衰减积累长程记忆状态（level/trend），predict
按 trend 阻尼外推 horizon 步——朴素可测，禁止冒充 xLSTM 真推理结果消费。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: decay 参数
#   fields: 参数 decay（无注解）
#   code: xlstm_long_memory.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① XLstmLongMemory
#   name_en: XLstmLongMemory
#   intro: xLSTM 长记忆骨架（EMA level/trend 占位）。
#   desc: xLSTM 长记忆骨架（EMA level/trend 占位）。；公共方法（定义序）: is_fitted, fit_baseline, predict, memory_summary；源码 L66-L121
#   inputs: decay
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: XLstmLongMemory
#   downstream: （远期：长记忆时序特征消费方）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from typing import Final

import numpy as np

__all__: Final = ["XLstmLongMemory"]

_MIN_FIT_SAMPLES: Final[int] = 2


class XLstmLongMemory:
    """xLSTM 长记忆骨架（EMA level/trend 占位）。"""

    def __init__(self, *, decay: float = 0.95) -> None:
        if not 0.0 < decay <= 1.0:
            raise ValueError(f"decay 必须 ∈ (0,1]: {decay}")
        self._decay = decay
        self._level: float | None = None
        self._trend: float = 0.0

    @property
    def is_fitted(self) -> bool:
        return self._level is not None

    def fit_baseline(self, series: np.ndarray) -> None:
        """拟合 EMA 长程记忆（level/trend）。短序列/非有限值 → ValueError。"""
        arr = np.asarray(series, dtype=float).ravel()
        if arr.size < _MIN_FIT_SAMPLES:
            raise ValueError(f"基线拟合样本不足（≥{_MIN_FIT_SAMPLES}）: {arr.size}")
        if not np.all(np.isfinite(arr)):
            raise ValueError("基线拟合序列含非有限值")
        level = float(arr[0])
        trend = 0.0
        d = self._decay
        for i in range(1, arr.size):
            prev = level
            level = d * level + (1.0 - d) * float(arr[i])
            trend = d * trend + (1.0 - d) * (level - prev)
        self._level = level
        self._trend = trend

    def predict(self, series: np.ndarray, *, horizon: int = 1) -> np.ndarray:
        """按记忆 trend 阻尼外推 horizon 步。未训练 fail-closed。"""
        if not self.is_fitted:
            raise ValueError("模型未训练——predict fail-closed")
        if horizon <= 0:
            raise ValueError(f"horizon 必须为正: {horizon}")
        arr = np.asarray(series, dtype=float).ravel()
        if arr.size == 0:
            raise ValueError("输入序列为空")
        if not np.all(np.isfinite(arr)):
            raise ValueError("输入序列含非有限值")
        # 以最新观测刷新 level（记忆滚动一步）
        d = self._decay
        level = d * float(self._level) + (1.0 - d) * float(arr[-1])
        steps = np.arange(1, horizon + 1, dtype=float)
        damping = (1.0 - d**steps) / (1.0 - d) if d < 1.0 else steps
        return level + self._trend * damping

    def memory_summary(self) -> dict:
        return {
            "fitted": self.is_fitted,
            "decay": self._decay,
            "level": self._level,
            "trend": self._trend,
        }
