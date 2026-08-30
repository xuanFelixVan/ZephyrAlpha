# [BLUEPRINT] MOD-ML-009 | docs/03_modules/_domain_machine_learning_train/blueprint.md
# [MODULE] zephyr.ml_train.learning_effect_feedback
# [DOMAIN] D_ML_TRAIN
# [DEPENDENCIES] numpy
# [CONSUMERS] MOD-ML-007 meta_learning_evolution（经验回写位）；MOD-ML-002 ai_operator（巡检效果输入）
# [STARTUP] event_driven
# [MATURITY] production
# [INVARIANTS] 回喂只产信号不触发真训练（triggered_training 恒 False，B-007）；IC=Spearman 秩相关；衰减=baseline_ic-ic
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] FeedbackSignalError(ZA-MLT-0008)——预测/实际长度不齐或样本对不足时抛
# [TESTS] tests/ml_train/test_learning_effect_feedback.py
# [A_module] module_id=MOD-ML-009 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
D_ML_TRAIN — MOD-ML-009 学习效果反馈回喂。

闭环语义：模型上线（含影子）后，预测 vs 实际计算 Spearman IC 与 IC 衰减
（相对 baseline），衰减超阈值产出 retrain 回喂信号。**红线**：信号只回喂
登记（供 MOD-ML-007 经验库/MOD-ML-002 巡检消费），``triggered_training``
恒 False——真训练触发权属 Owner（B-007），AI 不得自动重启训练。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: decay_threshold 参数
#   fields: 参数 decay_threshold（无注解）
#   code: learning_effect_feedback.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: min_pairs 参数
#   fields: 参数 min_pairs（无注解）
#   code: learning_effect_feedback.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① LearningEffectFeedback
#   name_en: LearningEffectFeedback
#   intro: 学习效果反馈回喂器（MOD-ML-009）。
#   desc: 学习效果反馈回喂器（MOD-ML-009）。 Parameters ---------- decay_threshold : IC 衰减阈值（超过则推荐重训）。 min_pair…；公共方法（定义序）: compute…
#   inputs: decay_threshold min_pairs
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: LearningEffectFeedback
#   downstream: MOD-ML-007 meta_learning_evolution（经验回写位）；MOD-ML-002 ai_operator（巡检效果输入）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> O1
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

import numpy as np

_log = logging.getLogger(__name__)


class FeedbackSignalError(Exception):
    """ZA-MLT-0008: 效果反馈计算失败。"""

    error_code = "ZA-MLT-0008"


def _spearman_ic(predictions: np.ndarray, actuals: np.ndarray) -> float:
    """Spearman 秩相关（对单调性鲁棒，免 scipy 依赖）。"""
    pr = np.argsort(np.argsort(predictions)).astype(float)
    ar = np.argsort(np.argsort(actuals)).astype(float)
    pr -= pr.mean()
    ar -= ar.mean()
    denom = float(np.sqrt((pr**2).sum() * (ar**2).sum()))
    if denom <= 0.0:
        return 0.0
    return float((pr * ar).sum() / denom)


class LearningEffectFeedback:
    """学习效果反馈回喂器（MOD-ML-009）。

    Parameters
    ----------
    decay_threshold : IC 衰减阈值（超过则推荐重训）。
    min_pairs : 最小预测-实际样本对数。
    """

    def __init__(self, decay_threshold: float = 0.2, min_pairs: int = 10) -> None:
        self._decay_threshold = float(decay_threshold)
        self._min_pairs = int(min_pairs)
        self._signals: dict[str, list[dict[str, Any]]] = {}

    # ── 效果计算 ─────────────────────────────────────────────────────

    def compute_effect(
        self,
        model_id: str,
        predictions: Any,
        actuals: Any,
        baseline_ic: float,
    ) -> dict[str, float]:
        """计算 IC / IC 衰减。

        Raises
        ------
        FeedbackSignalError
            长度不齐 / 样本对不足。
        """
        pred = np.asarray(predictions, dtype=float)
        act = np.asarray(actuals, dtype=float)
        if pred.shape != act.shape:
            raise FeedbackSignalError(f"预测/实际长度不齐: {pred.shape} vs {act.shape}")
        if pred.size < self._min_pairs:
            raise FeedbackSignalError(f"样本对不足: n={pred.size} < {self._min_pairs}")
        ic = _spearman_ic(pred, act)
        return {
            "ic": ic,
            "baseline_ic": float(baseline_ic),
            "ic_decay": float(baseline_ic) - ic,
            "n_pairs": float(pred.size),
        }

    # ── 回喂 ─────────────────────────────────────────────────────────

    def feedback(
        self,
        model_id: str,
        predictions: Any,
        actuals: Any,
        baseline_ic: float,
    ) -> dict[str, Any]:
        """产回喂信号（retrain_recommended + triggered_training=False）。"""
        effect = self.compute_effect(model_id, predictions, actuals, baseline_ic)
        signal: dict[str, Any] = {
            "model_id": model_id,
            **effect,
            "retrain_recommended": effect["ic_decay"] > self._decay_threshold,
            "triggered_training": False,  # B-007：AI 不自动触发真训练
            "at": datetime.now(timezone.utc).isoformat(),
        }
        self._signals.setdefault(model_id, []).append(signal)
        _log.info(
            "效果回喂: %s ic=%.3f decay=%.3f retrain=%s",
            model_id,
            effect["ic"],
            effect["ic_decay"],
            signal["retrain_recommended"],
        )
        return signal

    def history(self, model_id: str) -> list[dict[str, Any]]:
        """回喂信号史（未知模型返回空表）。"""
        return list(self._signals.get(model_id, []))


__all__ = [
    "FeedbackSignalError",
    "LearningEffectFeedback",
]
