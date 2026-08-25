# [BLUEPRINT] MOD-ML-DENSITY | docs/03_modules/_domain_machine_learning_train/blueprint.md
# [MODULE] zephyr.ml_train.implementations.density_quantile_trainer
# [DOMAIN] D_ML_TRAIN
# [DEPENDENCIES] zephyr.ml_train.trainer_base; sklearn.ensemble; numpy
# [CONSUMERS] GAP-F-01 情景概率分布模型（W2 矩阵概率输入）；MOD-ML-001 training_pipeline
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 分位数序列单调不交叉（输出前 np.maximum.accumulate 修正）；晋升草稿恒 candidate；禁止实盘生效（B-009）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DensityTrainError(ZA-MLT-0002)——未训练预测/样本不足/特征缺失时抛
# [TESTS] tests/ml_train/test_density_quantile_trainer.py
# [A_module] module_id=MOD-ML-DENSITY | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

"""D_ML_TRAIN — GAP-F-34 密度预测主路线 MVP（ML-DENSITY-001 轻量密度头）。

91 号主路线候选一：轻量密度头。lightgbm 不在项目依赖（2026-08-23 核查 pip show
lightgbm 无结果、pyproject 无声明），按派单降级为 sklearn
``HistGradientBoostingRegressor(loss="quantile")`` 分位数头——零新重依赖。

链路：train（合成/小数据）→ validate（pinball loss + q10~q90 覆盖率）→
``build_registry_entry`` 产出 model_registry 晋升片段草稿（只产出草稿，禁直改
注册表）→ ``predict_quantiles`` 分位数序列接口供 GAP-F-01 情景概率分布消费。

红线：全部产物 testing 封顶，任何参数/模型禁止生效实盘（B-009）。
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Final

import numpy as np

from zephyr.ml_train.trainer_base import ModelMetadata, ModelTrainerBase

_log = logging.getLogger(__name__)

#: 默认分位数网格（q10~q90，对齐 91 号主路线 W2 矩阵消费面）
DEFAULT_QUANTILES: Final[tuple[float, ...]] = (0.1, 0.25, 0.5, 0.75, 0.9)

_MODEL_ID: Final[str] = "ML-DENSITY-001"
_CODE_PATH: Final[str] = "src/zephyr/ml_train/implementations/density_quantile_trainer.py"


class DensityTrainError(Exception):
    """ZA-MLT-0002: 密度头训练/预测失败。"""

    error_code = "ZA-MLT-0002"


@dataclass(frozen=True)
class DensityQuantileConfig:
    """轻量密度头配置（参数 >4 收 dataclass，§5.150）。

    Attributes
    ----------
    quantiles : 分位数网格（默认 q10/q25/q50/q75/q90）。
    max_iter / learning_rate / max_depth / min_samples_leaf : HGB 超参（小数据 MVP 默认值）。
    random_state : 随机种子（可复现）。
    min_train_samples : 最小训练样本数（不足拒绝训练，防空转）。
    focused_loss_enabled / focused_var_quantile / focused_left_tail_weight :
        A1 聚焦贝叶斯损失（CAND-MLT-013）——左尾加权 w(r)=2.0 (r<VaR_5%)，默认开启。
    """

    quantiles: tuple[float, ...] = DEFAULT_QUANTILES
    max_iter: int = 200
    learning_rate: float = 0.06
    max_depth: int = 3
    min_samples_leaf: int = 20
    random_state: int = 42
    min_train_samples: int = 30
    #: A1 聚焦贝叶斯损失开关（CAND-MLT-013，Phase 1 即可用）
    focused_loss_enabled: bool = True
    #: 左尾判定分位（VaR_5%）
    focused_var_quantile: float = 0.05
    #: 左尾样本权重 w(r)=2.0 (r<VaR_5%)
    focused_left_tail_weight: float = 2.0


def _pinball_loss(y: np.ndarray, pred: np.ndarray, quantile: float) -> float:
    """分位数 pinball loss（越小越好）。"""
    diff = y - pred
    return float(np.mean(np.maximum(quantile * diff, (quantile - 1.0) * diff)))


def _focused_sample_weights(
    y: np.ndarray, var_quantile: float, left_tail_weight: float
) -> np.ndarray:
    """A1 聚焦贝叶斯损失左尾权重：w(r)=left_tail_weight (r<VaR)，否则 1.0。

    Duke/Monash 2024：对 VaR_5% 以左样本加倍权重，直接改善尾部校准。
    """
    var_line = float(np.quantile(y, var_quantile))
    return np.where(y < var_line, left_tail_weight, 1.0)


class DensityQuantileTrainer(ModelTrainerBase):
    """轻量密度头训练器（GAP-F-34 MVP）。

    继承 ``ModelTrainerBase``（OCP 扩展点 D_ML_TRAIN-TRN）：
      - ``train()``: 每个分位数拟合一个 HGB quantile 回归器，返回 pinball 指标。
      - ``validate()``: pinball loss + q10~q90 区间覆盖率。
      - ``predict_quantiles()``: 分位数序列输出（单调修正），供 GAP-F-01 消费。
      - ``build_registry_entry()``: model_registry 晋升片段草稿（恒 candidate，
        由治理流程串行合并，本类禁直改注册表）。

    训练数据约定：``features["X"]`` 为 (n, d) 特征矩阵，``target`` 为 (n,) 次日收益。
    """

    __model_id__ = _MODEL_ID

    def __init__(self, config: DensityQuantileConfig | None = None) -> None:
        self.config = config or DensityQuantileConfig()
        self._models: dict[float, Any] = {}
        self._feature_names: list[str] = []
        self._metadata: ModelMetadata | None = None

    # ── ModelTrainerBase 实现 ────────────────────────────────────────

    def train(
        self,
        features: dict[str, Any],
        target: object,
        idempotency_key: str,
    ) -> dict[str, float]:
        """逐分位数拟合 HGB quantile 头。

        Raises
        ------
        DensityTrainError
            特征缺失 / 样本不足 / 特征-目标长度不齐。
        """
        from sklearn.ensemble import HistGradientBoostingRegressor

        if "X" not in features:
            raise DensityTrainError("features['X'] 缺失（需 (n, d) 特征矩阵）")
        x = np.asarray(features["X"], dtype=float)
        y = np.asarray(target, dtype=float)
        if x.ndim != 2:
            raise DensityTrainError(f"features['X'] 需二维矩阵，实得 ndim={x.ndim}")
        if len(x) != len(y):
            raise DensityTrainError(f"特征/目标长度不齐: X={len(x)} y={len(y)}")
        if len(x) < self.config.min_train_samples:
            raise DensityTrainError(
                f"样本不足: n={len(x)} < min_train_samples={self.config.min_train_samples}"
            )

        self._feature_names = [str(n) for n in features.get("feature_names", [])]
        sample_w = (
            _focused_sample_weights(y, self.config.focused_var_quantile, self.config.focused_left_tail_weight)
            if self.config.focused_loss_enabled
            else None
        )
        models: dict[float, Any] = {}
        pinballs: list[float] = []
        for q in self.config.quantiles:
            reg = HistGradientBoostingRegressor(
                loss="quantile",
                quantile=q,
                max_iter=self.config.max_iter,
                learning_rate=self.config.learning_rate,
                max_depth=self.config.max_depth,
                min_samples_leaf=self.config.min_samples_leaf,
                random_state=self.config.random_state,
            )
            reg.fit(x, y, sample_weight=sample_w)
            models[q] = reg
            pinballs.append(_pinball_loss(y, reg.predict(x), q))
        self._models = models

        metrics = {
            "train_pinball_mean": float(np.mean(pinballs)),
            "n_train": float(len(y)),
        }
        if sample_w is not None:
            metrics["focused_tail_ratio"] = float(np.mean(sample_w > 1.0))
        self._metadata = ModelMetadata(
            model_id=self.__model_id__,
            model_version="0.1.0",
            model_type="density_prediction",
            framework="sklearn-HGB-quantile",
            features=self._feature_names,
            target="return_1d_quantiles",
            metrics=metrics,
            status="trained",
        )
        _log.info("密度头训练完成: key=%s metrics=%s", idempotency_key, metrics)
        return metrics

    def validate(self, features: dict[str, Any], target: object) -> dict[str, float]:
        """验证：pinball loss 均值 + q10~q90 区间覆盖率（校准代理指标）。"""
        self._require_trained()
        x = np.asarray(features["X"], dtype=float)
        y = np.asarray(target, dtype=float)
        qs = self.predict_quantiles(x)
        pinballs = [_pinball_loss(y, qs[q], q) for q in sorted(qs)]
        lower_q, upper_q = min(qs), max(qs)
        coverage = float(np.mean((y >= qs[lower_q]) & (y <= qs[upper_q])))
        return {
            "pinball_mean": float(np.mean(pinballs)),
            "coverage_10_90": coverage,
            "n": float(len(y)),
        }

    # ── GAP-F-01 消费接口 ────────────────────────────────────────────

    def predict_quantiles(self, x: Any) -> dict[float, np.ndarray]:
        """分位数序列输出（单调不交叉修正），供 GAP-F-01 情景概率分布消费。

        Returns
        -------
        dict[float, np.ndarray]
            ``{quantile: (n,) 预测序列}``，键为升序分位数。
        """
        self._require_trained()
        arr = np.asarray(x, dtype=float)
        raw = np.column_stack([self._models[q].predict(arr) for q in sorted(self._models)])
        monotone = np.maximum.accumulate(raw, axis=1)  # 分位数交叉修正
        return {q: monotone[:, i] for i, q in enumerate(sorted(self._models))}

    # ── 晋升流程桩（只产草稿，禁直改注册表） ─────────────────────────

    def build_registry_entry(self, metrics: dict[str, float]) -> dict[str, Any]:
        """产出 model_registry 晋升片段草稿（恒 candidate，治理流程串行合并）。"""
        self._require_trained()
        return {
            "model_id": self.__model_id__,
            "name": "Lightweight Density Head",
            "name_zh": "轻量密度头（主路线候选一）",
            "model_type": "density_prediction",
            "architecture": "sklearn HistGradientBoostingRegressor quantile head",
            "task": "次日收益分布分位数预测（q10~q90）",
            "target_variable": "return_1d_quantiles",
            "inputs": self._feature_names,
            "eval_metrics": dict(metrics),
            "code_path": _CODE_PATH,
            "promotion_stage": "candidate",
            "decay_state": "created",
            "serving_mode": "none",
            "status": "candidate",
        }

    def _require_trained(self) -> None:
        if not self._models:
            raise DensityTrainError("模型未训练（先调 train()）")


__all__ = [
    "DEFAULT_QUANTILES",
    "DensityQuantileConfig",
    "DensityQuantileTrainer",
    "DensityTrainError",
]
