# [BLUEPRINT] MOD-SIG-050 | docs/03_modules/MOD-SIG-050/
# [MODULE] zephyr.signal_ashare.kronos_tsfm_predictor
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] numpy
# [CONSUMERS] （远期：信号层时序预测消费方）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 未训练/未加载权重时 predict 一律 fail-closed（ValueError）；不引 torch 等大模型依赖——真训练/真推理属 B-007 人工闸门；占位基线预测必须显式标记 is_baseline
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 空序列/非有限值/非法 horizon/未训练 predict/权重文件缺失 → ValueError
# [TESTS] tests/signal_ashare/test_kronos_tsfm_predictor.py
# [A_module] module_id=MOD-SIG-050 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Kronos TSFM 时序基础模型预测器（MOD-SIG-050）——接口契约 + 轻量占位实现。

Kronos（K 线时序基础模型）属远期增强候选（44 号 memo §7：重启三条件满足后可评）。
本模块只立接口契约：predict 签名/输入校验/未训练 fail-closed。**不引 torch 等
大模型依赖**——真训练/真推理属 B-007 人工闸门，由生产侧注入真后端。

占位推理路径为 last-value 朴素基线（fit_baseline 后可用），返回值显式标记
``is_baseline=True``，禁止冒充 TSFM 真推理结果消费。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: config 参数
#   fields: 参数 config（无注解）
#   code: kronos_tsfm_predictor.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① KronosTsfmPredictor
#   name_en: KronosTsfmPredictor
#   intro: Kronos TSFM 预测器骨架（接口契约 + 朴素基线占位）。
#   desc: Kronos TSFM 预测器骨架（接口契约 + 朴素基线占位）。；公共方法（定义序）: is_ready, load_checkpoint, fit_baseline, predict；源码 L97-L147
#   inputs: config
#   outputs: 返回值
#   （注：A1 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（3 定义）
#   name_en: public defs
#   intro: KronosTsfmPredictor
#   downstream: （远期：信号层时序预测消费方）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Final

import numpy as np

__all__: Final = [
    "KronosTsfmPredictor",
    "TsfmConfig",
    "TsfmPrediction",
]

_MIN_FIT_SAMPLES: Final[int] = 2


@dataclass(frozen=True)
class TsfmConfig:
    """TSFM 预测配置。"""

    horizon: int = 1
    max_lookback: int = 512

    def __post_init__(self) -> None:
        if self.horizon <= 0:
            raise ValueError(f"horizon 必须为正: {self.horizon}")
        if self.max_lookback <= 0:
            raise ValueError(f"max_lookback 必须为正: {self.max_lookback}")


@dataclass(frozen=True)
class TsfmPrediction:
    """预测输出（is_baseline=True 表示占位基线，非真 TSFM 推理）。"""

    values: np.ndarray
    horizon: int
    lookback_used: int
    is_baseline: bool


class KronosTsfmPredictor:
    """Kronos TSFM 预测器骨架（接口契约 + 朴素基线占位）。"""

    def __init__(self, config: TsfmConfig | None = None) -> None:
        self._config = config or TsfmConfig()
        self._checkpoint_loaded = False
        self._baseline_fitted = False

    @property
    def is_ready(self) -> bool:
        return self._checkpoint_loaded or self._baseline_fitted

    # ── 权重加载（真推理接线位） ─────────────────────────────────────

    def load_checkpoint(self, path: Path) -> None:
        """登记 TSFM 权重文件（真推理属 B-007，本层只校验存在性）。"""
        if not Path(path).exists():
            raise ValueError(f"权重文件不存在: {path}")
        self._checkpoint_loaded = True

    # ── 占位基线 ─────────────────────────────────────────────────────

    def fit_baseline(self, series: np.ndarray) -> None:
        """拟合朴素基线（last-value）。短序列/含非有限值 → ValueError。"""
        arr = np.asarray(series, dtype=float).ravel()
        if arr.size < _MIN_FIT_SAMPLES:
            raise ValueError(f"基线拟合样本不足（≥{_MIN_FIT_SAMPLES}）: {arr.size}")
        if not np.all(np.isfinite(arr)):
            raise ValueError("基线拟合序列含非有限值")
        self._baseline_fitted = True

    # ── 预测接口 ─────────────────────────────────────────────────────

    def predict(self, series: np.ndarray) -> TsfmPrediction:
        """预测未来 horizon 步。未训练 fail-closed（ValueError）。"""
        if not self.is_ready:
            raise ValueError("模型未训练（未加载权重且未拟合基线）——predict fail-closed")
        arr = np.asarray(series, dtype=float).ravel()
        if arr.size == 0:
            raise ValueError("输入序列为空")
        if not np.all(np.isfinite(arr)):
            raise ValueError("输入序列含非有限值")
        lookback = arr[-self._config.max_lookback :]
        last = float(lookback[-1])
        values = np.full(self._config.horizon, last, dtype=float)
        return TsfmPrediction(
            values=values,
            horizon=self._config.horizon,
            lookback_used=int(lookback.size),
            is_baseline=True,
        )
