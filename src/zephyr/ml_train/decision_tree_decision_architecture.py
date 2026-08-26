# [BLUEPRINT] MOD-ML-016 | docs/03_modules/_domain_machine_learning_train/decision_tree_decision_architecture/blueprint.md
# [MODULE] zephyr.ml_train.decision_tree_decision_architecture
# [DOMAIN] D_ML_TRAIN
# [DEPENDENCIES] 无（gbm_trainer/shap_explainer/干预钩子/时钟全注入；未注入降级规则 stump+特征重要性兜底）
# [CONSUMERS] 运行时装配批（决策日志学习/决策解释/人工干预统一注入点装配）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 特征=模块输出向量(dict[str,float] 键集闭合)/标签=事后收益符号; gbm_trainer 未注入降级确定性规则 stump(中位阈值+最大分离度,同输入必同模型); SHAP 未注入降级特征重要性兜底; 人工干预钩子沿决策路径触发(钩子异常 Fail-Closed); 干预全程留痕; RL(PPO)仅离线评估语义不施工; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_machine_learning_train/decision_tree_decision_architecture/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] DecisionTreeArchError(占位 ZA-MLT-UNREGISTERED-DECISION-TREE-ARCH)——空训练集/特征键集不齐/未训练预测/空特征/钩子异常/解释器输出非法时抛
# [TESTS] tests/ml_train/test_decision_tree_decision_architecture.py
# [A_module] module_id=MOD-ML-016 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""DecisionTreeDecisionArchitecture — 决策树交易决策架构（MOD-ML-016）。

B10-01480（AUD-DRAFT-001-DIGEST P2 波 P2-W07，CAND-MLT-022，A1 模块46）：
**GBM 决策树学习历史决策日志**（特征=模块输出向量 / 标签=事后收益符号，
注入 gbm_trainer，未装库**降级确定性规则 stump**）+ **SHAP 解释**（注入
shap_explainer，未注入降级**特征重要性兜底**）+ **关键节点人工干预接口**
（决策路径 + 干预钩子注入，全程留痕）+ RL(PPO) 仅离线评估语义**不施工**。

查重分工（蓝图 §0）：backtest=回测引擎（本件消费其事后收益标签语义，
不回测）；ml_model_factory=模型生命周期编排（本件=决策架构本体，不管
注册晋级）；qnn_two_stage=分位数密度模型（本件=决策符号分类，零交集）。
"""

from __future__ import annotations

import datetime
import logging
import statistics
from dataclasses import dataclass, field
from typing import Any, Callable, Final, Mapping, Sequence

_log = logging.getLogger(__name__)

__all__: Final = [
    "DecisionLogEntry",
    "DecisionTreeArchError",
    "DecisionTreeDecisionArchitecture",
    "InterventionRecord",
    "Prediction",
    "RL_PPO_OFFLINE_ONLY",
    "RuleStump",
]

#: RL(PPO) 仅离线评估语义（本模块不施工在线 RL）
RL_PPO_OFFLINE_ONLY: Final[str] = (
    "RL(PPO) 仅离线评估语义：本架构不施工在线 RL 训练/推理，"
    "离线评估由回测域在 Owner 人工窗口执行"
)


class DecisionTreeArchError(Exception):
    """决策树架构输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-MLT-UNREGISTERED-DECISION-TREE-ARCH。
    """


@dataclass(frozen=True)
class DecisionLogEntry:
    """历史决策日志条目（特征=模块输出向量，标签源=事后收益，frozen）。"""

    decision_id: str
    features: dict[str, float]
    realized_return: float


@dataclass(frozen=True)
class RuleStump:
    """降级规则 stump（单特征中位阈值分裂，确定性，frozen）。"""

    feature: str
    threshold: float
    left_sign: int
    right_sign: int

    def predict_one(self, features: Mapping[str, float]) -> tuple[int, tuple[str, ...]]:
        """单样本预测 + 决策路径。"""
        sign = self.left_sign if features[self.feature] <= self.threshold else self.right_sign
        path = (
            "root",
            f"feature={self.feature}",
            f"threshold={self.threshold:.6f}",
            f"leaf={'long' if sign > 0 else 'short'}",
        )
        return sign, path


@dataclass(frozen=True)
class Prediction:
    """预测结果（信号 + 决策路径 + 干预标记，frozen）。"""

    signal: int
    path: tuple[str, ...]
    intervened: bool
    detail: dict = field(default_factory=dict)


@dataclass(frozen=True)
class InterventionRecord:
    """人工干预留痕（frozen）。"""

    node_key: str
    original_signal: int
    override_signal: int
    intervened_at: datetime.datetime


class DecisionTreeDecisionArchitecture:
    """决策树交易决策架构（GBM 注入 / 规则 stump 降级 + SHAP 注入 / 重要性兜底 + 人工干预钩子）。"""

    def __init__(
        self,
        *,
        gbm_trainer: Callable[[list[dict[str, float]], list[int]], Any] | None = None,
        shap_explainer: Callable[[Any, list[dict[str, float]]], Mapping[str, float]] | None = None,
        clock: Callable[[], datetime.datetime] | None = None,
    ) -> None:
        self._gbm_trainer = gbm_trainer
        self._shap_explainer = shap_explainer
        self._clock = clock or datetime.datetime.now
        self._model: Any = None
        self._stump: RuleStump | None = None
        self._feature_names: list[str] = []
        self._train_rows: list[dict[str, float]] = []
        self._hooks: dict[str, Callable[[Mapping[str, float], int], int | None]] = {}
        self._interventions: list[InterventionRecord] = []

    # ── 内部 ─────────────────────────────────────────────────────────────

    @staticmethod
    def _label_of(realized_return: float) -> int:
        """标签=事后收益符号（0 归多）。"""
        return 1 if realized_return >= 0.0 else -1

    def _check_features(self, features: Mapping[str, float]) -> None:
        if not features:
            raise DecisionTreeArchError("特征向量为空")
        if self._feature_names and sorted(features) != self._feature_names:
            raise DecisionTreeArchError(
                f"特征键集不齐: 期望 {self._feature_names}，实得 {sorted(features)}"
            )

    def _model_predict(self, features: dict[str, float]) -> tuple[int, tuple[str, ...]]:
        if self._stump is not None:
            return self._stump.predict_one(features)
        model = self._model
        if hasattr(model, "predict_one"):
            sign = int(model.predict_one(features))
        elif hasattr(model, "predict"):
            sign = int(model.predict([features])[0])
        elif callable(model):
            sign = int(model(features))
        else:  # pragma: no cover — 防御分支
            raise DecisionTreeArchError("注入模型无 predict/predict_one/可调用接口")
        path = ("root", "gbm_ensemble", f"leaf={'long' if sign > 0 else 'short'}")
        return (1 if sign >= 0 else -1), path

    def _fit_stump(
        self, rows: list[dict[str, float]], labels: list[int]
    ) -> RuleStump:
        """确定性规则 stump：逐特征取中位阈值，选左右均值分离度最大者。"""
        best: tuple[float, str, float, int, int] | None = None
        for feature in self._feature_names:  # 已排序，平局确定
            values = sorted(row[feature] for row in rows)
            threshold = float(statistics.median(values))
            left = [lab for row, lab in zip(rows, labels) if row[feature] <= threshold]
            right = [lab for row, lab in zip(rows, labels) if row[feature] > threshold]
            mean_left = statistics.fmean(left) if left else 0.0
            mean_right = statistics.fmean(right) if right else 0.0
            score = abs(mean_left - mean_right)
            # 分数高者优先；同分按特征名字典序小者优先（确定性平局裁决）
            if best is None or score > best[0] or (score == best[0] and feature < best[1]):
                best = (
                    score,
                    feature,
                    threshold,
                    1 if mean_left >= 0 else -1,
                    1 if mean_right >= 0 else -1,
                )
        assert best is not None  # feature_names 非空（训练校验保证）
        _, feature, threshold, left_sign, right_sign = best
        return RuleStump(
            feature=feature, threshold=threshold, left_sign=left_sign, right_sign=right_sign
        )

    # ── 训练 ──────────────────────────────────────────────────────────────

    def train(self, entries: Sequence[DecisionLogEntry]) -> dict[str, Any]:
        """学习历史决策日志（注入 gbm_trainer；未注入降级规则 stump）。"""
        if not entries:
            raise DecisionTreeArchError("训练日志为空")
        feature_names = sorted(entries[0].features)
        if not feature_names:
            raise DecisionTreeArchError("特征向量为空")
        rows: list[dict[str, float]] = []
        labels: list[int] = []
        for entry in entries:
            if sorted(entry.features) != feature_names:
                raise DecisionTreeArchError(
                    f"特征键集不齐: {entry.decision_id!r} 期望 {feature_names}，"
                    f"实得 {sorted(entry.features)}"
                )
            rows.append(dict(entry.features))
            labels.append(self._label_of(entry.realized_return))
        self._feature_names = feature_names
        self._train_rows = rows

        if self._gbm_trainer is not None:
            try:
                self._model = self._gbm_trainer(rows, labels)
            except Exception as exc:  # noqa: BLE001 — 训练器异常 Fail-Closed
                raise DecisionTreeArchError(f"gbm_trainer 训练异常: {exc}") from exc
            self._stump = None
            model_kind = "gbm_injected"
        else:
            self._stump = self._fit_stump(rows, labels)
            self._model = None
            model_kind = "rule_stump"
            _log.info("gbm_trainer 未注入，降级规则 stump: %s", self._stump)
        metrics = {
            "model_kind": model_kind,
            "n_samples": len(rows),
            "n_features": len(feature_names),
            "pos_ratio": sum(1 for lab in labels if lab > 0) / len(labels),
        }
        _log.info("决策树训练完成: %s", metrics)
        return metrics

    # ── 预测 + 人工干预 ───────────────────────────────────────────────────

    def register_intervention_hook(
        self, node_key: str, hook: Callable[[Mapping[str, float], int], int | None]
    ) -> None:
        """注册关键节点人工干预钩子（node_key 或 "*" 通配）。"""
        if not node_key:
            raise DecisionTreeArchError("node_key 为空")
        self._hooks[node_key] = hook

    def predict(self, features: Mapping[str, float]) -> Prediction:
        """预测决策符号（沿决策路径触发干预钩子；钩子异常 Fail-Closed）。"""
        if self._model is None and self._stump is None:
            raise DecisionTreeArchError("模型未训练（先调 train()）")
        self._check_features(features)
        signal, path = self._model_predict(dict(features))

        intervened = False
        for node_key in path:
            hook = self._hooks.get(node_key) or self._hooks.get("*")
            if hook is None:
                continue
            try:
                override = hook(features, signal)
            except Exception as exc:  # noqa: BLE001 — 人工干预通道异常 Fail-Closed
                raise DecisionTreeArchError(f"干预钩子异常(node={node_key}): {exc}") from exc
            if override is None:
                continue
            override_signal = 1 if int(override) >= 0 else -1
            if override_signal != signal:
                self._interventions.append(InterventionRecord(
                    node_key=node_key,
                    original_signal=signal,
                    override_signal=override_signal,
                    intervened_at=self._clock(),
                ))
                _log.warning(
                    "人工干预: node=%s %d -> %d", node_key, signal, override_signal
                )
                signal = override_signal
                intervened = True
        return Prediction(
            signal=signal, path=path, intervened=intervened,
            detail={"model_kind": "rule_stump" if self._stump is not None else "gbm_injected"},
        )

    # ── 解释 ──────────────────────────────────────────────────────────────

    def explain(self) -> dict[str, float]:
        """特征归因：SHAP 注入优先，未注入降级特征重要性兜底。"""
        if self._model is None and self._stump is None:
            raise DecisionTreeArchError("模型未训练（先调 train()）")
        if self._shap_explainer is not None:
            try:
                values = self._shap_explainer(
                    self._model if self._model is not None else self._stump,
                    [dict(row) for row in self._train_rows],
                )
            except Exception as exc:  # noqa: BLE001 — 解释器异常 Fail-Closed
                raise DecisionTreeArchError(f"shap_explainer 解释异常: {exc}") from exc
            if not isinstance(values, Mapping):
                raise DecisionTreeArchError("shap_explainer 输出非 Mapping（非法）")
            return {str(k): float(v) for k, v in values.items()}
        # 兜底：特征重要性
        model = self._model
        if model is not None and hasattr(model, "feature_importances_"):
            importances = list(model.feature_importances_)
            if len(importances) != len(self._feature_names):
                raise DecisionTreeArchError("feature_importances_ 长度与特征数不符")
            return {name: float(imp) for name, imp in zip(self._feature_names, importances)}
        if self._stump is not None:
            return {
                name: (1.0 if name == self._stump.feature else 0.0)
                for name in self._feature_names
            }
        return {name: 0.0 for name in self._feature_names}  # pragma: no cover — 防御分支

    # ── 查询 ─────────────────────────────────────────────────────────────

    def interventions(self) -> list[InterventionRecord]:
        """人工干预留痕（按发生序）。"""
        return list(self._interventions)

    @property
    def rl_ppo_offline_semantic(self) -> str:
        """RL(PPO) 仅离线评估语义声明（本模块不施工在线 RL）。"""
        return RL_PPO_OFFLINE_ONLY
