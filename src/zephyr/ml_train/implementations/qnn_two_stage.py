# [BLUEPRINT] MOD-ML-010 | docs/03_modules/_domain_machine_learning_train/qnn_two_stage/blueprint.md
# [MODULE] zephyr.ml_train.implementations.qnn_two_stage
# [DOMAIN] D_ML_TRAIN
# [DEPENDENCIES] zephyr.ml_train.trainer_base; sklearn; numpy
# [CONSUMERS] MOD-ML-DENSITY(密度头消费) ; D_REGIME(体制标签Stage2扩展)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] Stage1 跨标的共性基座(全样本逐分位HGB); Stage2 per-symbol仿射缩放 q_s=m+a_s*(q_base-m)+b_s, OLS闭式估计,子样本不足→degraded(a_s=1,b_s=0); retrain_stage2只重估仿射头(Stage1冻结); 分位数序列单调不交叉(np.maximum.accumulate); build_registry_entry恒candidate禁直改注册表(B-009)
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] TwoStageQnnError(ZA-MLT-0012)
# [TESTS] tests/ml_train/test_qnn_two_stage.py
# [A_module] module_id=MOD-ML-010 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 训练特征 features
#   fields: X(n,d)特征矩阵 + symbol_ids(n,)标的标签 + feature_names(可选)
# - id: I2
#   name: 目标 target
#   fields: (n,) 次日收益
# 层: 算法
# - id: A1
#   name_zh: ① Stage1 共性基座
#   name_en: stage1_commonality
#   intro: 全样本合并池化,逐分位数拟合HGB quantile → q_base(x)
# - id: A2
#   name_zh: ② Stage2 市场缩放头
#   name_en: stage2_scaling_head
#   intro: per-symbol 仿射缩放 OLS估计;子样本不足degraded回退
# - id: A3
#   name_zh: ③ 体制快速重训
#   name_en: retrain_stage2
#   intro: 只重估仿射头,Stage1冻结,分钟级
# - id: A4
#   name_zh: ④ 分位数序列输出
#   name_en: predict_quantiles
#   intro: per-symbol 预测+单调不交叉修正
# 层: 输出
# - id: O1
#   name_zh: 分位数序列预测
#   name_en: dict[quantile, np.ndarray]
#   intro: {q:(n,)}单调不减,下游GAP-F-01消费
#   downstream: MOD-ML-DENSITY密度头; D_REGIME体制标签扩展 ([CONSUMERS] 头)
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I1 --> A2
# I2 --> A1
# I2 --> A2
# A1 --> A2
# A1 --> A4
# A2 --> A4
# I2 --> A3
# A3 --> A4
# A4 --> O1

"""
A2 分位数神经网络两阶段架构 (MOD-ML-010, B10-01408 ★当前即做)。

Stage1 跨标的共性分位数网络 (市场共性剥离、跨标的复用) +
Stage2 市场缩放头 (per-symbol 仿射缩放, 体制切换时几分钟级快速重训)。

查重分工 (W-P1-20 铁律④探查——新模型类,非推倒既有件):
  - density_quantile_trainer (MOD-ML-DENSITY): 单标的逐分位 HGB 轻量密度头;
    本件=两阶段结构新模型类, density trainer 保留不动;
  - conditional_density_predictor (MOD-SIG-043): 信号域条件经验分布法;
    信号层推理件, 非训练架构; 不同层不重叠;
  - trainer_base (MOD-L11-001): 训练器抽象基类; 本件继承实现 train/validate。

依据: construction_backlog_dig.tsv B10-01408 + CAND-MLT-014
SSoT: docs/03_modules/_domain_machine_learning_train/qnn_two_stage/blueprint.md
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: config 参数
#   fields: 参数 config（无注解）
#   code: qnn_two_stage.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① TwoStageQnn
#   name_en: TwoStageQnn
#   intro: 两阶段分位数神经网络训练器 (UBS Quant Hub 2025)。
#   desc: 两阶段分位数神经网络训练器 (UBS Quant Hub 2025)。 Stage1: 共性基座分位数网络 (跨标的复用)。 Stage2: per-symbol 仿射缩放头 (…；公共方法（定义序）: train,…
#   inputs: config
#   outputs: 返回值
#   （注：A1 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（3 定义）
#   name_en: public defs
#   intro: TwoStageQnn
#   downstream: MOD-ML-DENSITY(密度头消费) ; D_REGIME(体制标签Stage2扩展)
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Final

import numpy as np

from zephyr.ml_train.trainer_base import ModelMetadata, ModelTrainerBase

_log = logging.getLogger(__name__)

#: 模型标识
_MODEL_ID: Final[str] = "ML-QNN2S-001"

__all__: Final[list[str]] = [
    "TwoStageQnnConfig",
    "TwoStageQnn",
    "TwoStageQnnError",
]


class TwoStageQnnError(Exception):
    """两阶段 QNN 训练/预测失败。"""

    error_code = "ZA-MLT-0012"  # 待登记, 建议 ZA-MLT-0003


@dataclass(frozen=True)
class TwoStageQnnConfig:
    """两阶段 QNN 配置。"""

    quantiles: tuple[float, ...] = (0.1, 0.25, 0.5, 0.75, 0.9)
    max_iter: int = 200
    learning_rate: float = 0.06
    max_depth: int = 3
    min_samples_leaf: int = 20
    random_state: int = 42
    min_train_samples: int = 30
    min_symbol_samples: int = 20


class TwoStageQnn(ModelTrainerBase):
    """两阶段分位数神经网络训练器 (UBS Quant Hub 2025)。

    Stage1: 共性基座分位数网络 (跨标的复用)。
    Stage2: per-symbol 仿射缩放头 (快速重训)。
    """

    __model_id__ = _MODEL_ID

    def __init__(self, config: TwoStageQnnConfig | None = None) -> None:
        self.config = config or TwoStageQnnConfig()
        self._stage1_models: dict[float, Any] = {}  # {quantile: HGB model}
        self._symbol_scaling: dict[str, tuple[float, float]] = {}  # {symbol: (a, b)}
        self._feature_names: list[str] = []
        self._metadata: ModelMetadata | None = None

    # ── ModelTrainerBase 实现 ────────────────────────────────────────

    def train(
        self,
        features: dict[str, Any],
        target: object,
        idempotency_key: str,
    ) -> dict[str, float]:
        """两阶段训练: Stage1 共性 + Stage2 缩放。"""
        from sklearn.ensemble import HistGradientBoostingRegressor

        x, y, symbol_ids = self._unpack_features(features, target)
        if len(x) < self.config.min_train_samples:
            raise TwoStageQnnError(f"样本不足: n={len(x)} < min={self.config.min_train_samples}")

        self._feature_names = [str(n) for n in features.get("feature_names", [])]

        # ── Stage1: 共性基座 ──
        stage1_models: dict[float, Any] = {}
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
            reg.fit(x, y)
            stage1_models[q] = reg
            preds = reg.predict(x)
            pinballs.append(self._pinball_loss(y, preds, q))
        self._stage1_models = stage1_models

        # ── Stage2: per-symbol 仿射缩放 ──
        scaling: dict[str, tuple[float, float]] = {}
        median_model = stage1_models[0.5]
        q_base_median = median_model.predict(x)
        unique_symbols = np.unique(symbol_ids)
        for sym in unique_symbols:
            mask = symbol_ids == sym
            sym_n = int(np.sum(mask))
            if sym_n < self.config.min_symbol_samples:
                scaling[str(sym)] = (1.0, 0.0)  # degraded
                continue
            q_base_sym = q_base_median[mask]
            y_sym = y[mask]
            a, b = self._fit_affine_scaling(q_base_sym, y_sym)
            scaling[str(sym)] = (a, b)
        self._symbol_scaling = scaling

        metrics = {
            "train_pinball_mean": float(np.mean(pinballs)),
            "n_train": float(len(y)),
            "n_symbols": float(len(unique_symbols)),
        }
        self._metadata = ModelMetadata(
            model_id=self.__model_id__,
            model_version="0.1.0",
            model_type="density_prediction",
            framework="sklearn-HGB-quantile-two-stage",
            features=self._feature_names,
            target="return_1d_quantiles",
            metrics=metrics,
            status="trained",
        )
        _log.info("两阶段QNN训练完成: key=%s metrics=%s", idempotency_key, metrics)
        return metrics

    def retrain_stage2(
        self,
        features: dict[str, Any],
        target: object,
    ) -> dict[str, float]:
        """快速重训 Stage2 (Stage1 冻结), 供体制切换场景。"""
        if not self._stage1_models:
            raise TwoStageQnnError("Stage1 未训练, 先调 train()")
        x, y, symbol_ids = self._unpack_features(features, target)
        median_model = self._stage1_models[0.5]
        q_base_median = median_model.predict(x)
        unique_symbols = np.unique(symbol_ids)
        scaling: dict[str, tuple[float, float]] = {}
        for sym in unique_symbols:
            mask = symbol_ids == sym
            sym_n = int(np.sum(mask))
            if sym_n < self.config.min_symbol_samples:
                scaling[str(sym)] = (1.0, 0.0)
                continue
            a, b = self._fit_affine_scaling(q_base_median[mask], y[mask])
            scaling[str(sym)] = (a, b)
        self._symbol_scaling = scaling
        return {"retrain_stage2": "ok", "n_symbols": float(len(unique_symbols))}

    def validate(self, features: dict[str, Any], target: object) -> dict[str, float]:
        """验证: pinball loss 均值 + q10~q90 区间覆盖率。"""
        x, y, symbol_ids = self._unpack_features(features, target)
        qs = self.predict_quantiles(x, symbol_ids)
        pinballs = [self._pinball_loss(y, qs[q], q) for q in sorted(qs)]
        lower_q, upper_q = min(qs), max(qs)
        coverage = float(np.mean((y >= qs[lower_q]) & (y <= qs[upper_q])))
        return {
            "pinball_mean": float(np.mean(pinballs)),
            "coverage_10_90": coverage,
            "n": float(len(y)),
        }

    # ── 消费接口 ────────────────────────────────────────────

    def predict_quantiles(
        self,
        x: np.ndarray,
        symbol_ids: np.ndarray,
    ) -> dict[float, np.ndarray]:
        """分位数序列输出 (单调不交叉修正)。"""
        if not self._stage1_models:
            raise TwoStageQnnError("模型未训练")
        arr = np.asarray(x, dtype=float)
        sym = np.asarray(symbol_ids)
        raw = np.column_stack([self._stage1_models[q].predict(arr) for q in sorted(self._stage1_models)])
        # Stage2 仿射缩放
        for i, q in enumerate(sorted(self._stage1_models)):
            if q == 0.5:
                continue  # 中位数列在缩放中作为基准 m(x)
            m_col = raw[:, list(sorted(self._stage1_models)).index(0.5)]
            for s_idx, s_val in enumerate(np.unique(sym)):
                mask = sym == s_val
                a, b = self._symbol_scaling.get(str(s_val), (1.0, 0.0))
                raw[mask, i] = m_col[mask] + a * (raw[mask, i] - m_col[mask]) + b
        # 单调不交叉修正
        monotone = np.maximum.accumulate(raw, axis=1)
        return {q: monotone[:, i] for i, q in enumerate(sorted(self._stage1_models))}

    def build_registry_entry(self, metrics: dict[str, float]) -> dict[str, Any]:
        """产出 candidate 草稿 (恒 candidate, 禁直改注册表)。"""
        if not self._stage1_models:
            raise TwoStageQnnError("模型未训练")
        return {
            "model_id": self.__model_id__,
            "name": "Two-Stage Quantile Neural Network",
            "name_zh": "两阶段分位数神经网络",
            "model_type": "density_prediction",
            "architecture": "sklearn HGB quantile two-stage",
            "task": "次日收益分布分位数预测（Stage1共性+Stage2缩放）",
            "target_variable": "return_1d_quantiles",
            "inputs": self._feature_names,
            "eval_metrics": dict(metrics),
            "code_path": "src/zephyr/ml_train/implementations/qnn_two_stage.py",
            "promotion_stage": "candidate",
            "decay_state": "created",
            "serving_mode": "none",
            "status": "candidate",
        }

    # ── 内部 ────────────────────────────────────────────────

    @staticmethod
    def _pinball_loss(y: np.ndarray, pred: np.ndarray, quantile: float) -> float:
        diff = y - pred
        return float(np.mean(np.maximum(quantile * diff, (quantile - 1.0) * diff)))

    @staticmethod
    def _fit_affine_scaling(q_base: np.ndarray, y: np.ndarray) -> tuple[float, float]:
        """OLS 闭式估计 a, b: y ≈ a * q_base + b。"""
        if len(q_base) < 2:
            return 1.0, 0.0
        x_mean = float(np.mean(q_base))
        y_mean = float(np.mean(y))
        cov = float(np.mean((q_base - x_mean) * (y - y_mean)))
        var = float(np.mean((q_base - x_mean) ** 2))
        if var == 0:
            return 1.0, y_mean - x_mean
        a = cov / var
        b = y_mean - a * x_mean
        return a, b

    def _unpack_features(self, features: dict[str, Any], target: object) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        if "X" not in features:
            raise TwoStageQnnError("features['X'] 缺失")
        if "symbol_ids" not in features:
            raise TwoStageQnnError("features['symbol_ids'] 缺失")
        x = np.asarray(features["X"], dtype=float)
        y = np.asarray(target, dtype=float)
        symbol_ids = np.asarray(features["symbol_ids"])
        if x.ndim != 2:
            raise TwoStageQnnError(f"X 需二维矩阵, 实得 ndim={x.ndim}")
        if len(x) != len(y) or len(x) != len(symbol_ids):
            raise TwoStageQnnError("X/target/symbol_ids 长度不齐")
        return x, y, symbol_ids
