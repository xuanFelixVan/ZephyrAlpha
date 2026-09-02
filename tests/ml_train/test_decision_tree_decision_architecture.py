# [BLUEPRINT] MOD-ML-016 | docs/03_modules/_domain_machine_learning_train/decision_tree_decision_architecture/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-ML-016 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.ml_train.test_decision_tree_decision_architecture
# [TESTS] src/zephyr/ml_train/decision_tree_decision_architecture.py
"""MOD-ML-016 单元测试：decision_tree_decision_architecture 决策树交易决策架构。

蓝图验收（B10-01480/CAND-MLT-022，A1 模块46）：
GBM 学习决策日志（注入 trainer，未注入降级确定性规则 stump）+ SHAP 注入
（未注入降级特征重要性兜底）+ 人工干预钩子（决策路径触发+留痕，钩子异常
Fail-Closed）+ RL(PPO) 仅离线语义。trainer/explainer/钩子全内存替身。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.ml_train.decision_tree_decision_architecture",
    reason="decision_tree_decision_architecture not importable",
)

from zephyr.ml_train.decision_tree_decision_architecture import (  # noqa: E402
    DecisionLogEntry,
    DecisionTreeArchError,
    DecisionTreeDecisionArchitecture,
    RL_PPO_OFFLINE_ONLY,
)

_T0 = datetime.datetime(2026, 8, 26, 9, 30, 0)

#: 强可分样本：momentum 大→涨，小→跌
_ENTRIES = [
    DecisionLogEntry("d1", {"momentum": 0.9, "vol": 0.2}, 0.05),
    DecisionLogEntry("d2", {"momentum": 0.8, "vol": 0.3}, 0.03),
    DecisionLogEntry("d3", {"momentum": 0.1, "vol": 0.2}, -0.04),
    DecisionLogEntry("d4", {"momentum": 0.2, "vol": 0.4}, -0.02),
]


class _FakeGbm:
    """内存 GBM 替身（predict + feature_importances_）。"""

    feature_importances_ = [0.7, 0.3]

    def __init__(self) -> None:
        self.rows: list[dict] = []
        self.labels: list[int] = []

    def fit(self, rows: list[dict], labels: list[int]) -> "_FakeGbm":
        self.rows, self.labels = rows, labels
        return self

    def predict(self, batch: list[dict]) -> list[int]:
        return [1 if row["momentum"] >= 0.5 else -1 for row in batch]


def _fake_trainer(rows: list[dict], labels: list[int]) -> _FakeGbm:
    return _FakeGbm().fit(rows, labels)


def _arch(**kwargs) -> DecisionTreeDecisionArchitecture:
    kwargs.setdefault("clock", lambda: _T0)
    return DecisionTreeDecisionArchitecture(**kwargs)


# ──────────────────────────────────────────────────────────────────────────────
# 训练（GBM 注入 / stump 降级）
# ──────────────────────────────────────────────────────────────────────────────


class TestTrain:
    def test_train_with_gbm_injected(self) -> None:
        arch = _arch(gbm_trainer=_fake_trainer)
        metrics = arch.train(_ENTRIES)
        assert metrics["model_kind"] == "gbm_injected"
        assert metrics["n_samples"] == 4
        assert metrics["n_features"] == 2
        assert metrics["pos_ratio"] == 0.5

    def test_train_fallback_rule_stump(self) -> None:
        arch = _arch()
        metrics = arch.train(_ENTRIES)
        assert metrics["model_kind"] == "rule_stump"

    def test_train_empty_entries_rejected(self) -> None:
        with pytest.raises(DecisionTreeArchError):
            _arch().train([])

    def test_train_empty_features_rejected(self) -> None:
        with pytest.raises(DecisionTreeArchError):
            _arch().train([DecisionLogEntry("d0", {}, 0.01)])

    def test_train_mismatched_feature_keys_rejected(self) -> None:
        bad = _ENTRIES + [DecisionLogEntry("d5", {"momentum": 0.5}, 0.01)]
        with pytest.raises(DecisionTreeArchError):
            _arch().train(bad)

    def test_trainer_exception_fail_closed(self) -> None:
        def _boom(rows, labels):
            raise RuntimeError("lightgbm 崩溃")

        with pytest.raises(DecisionTreeArchError):
            _arch(gbm_trainer=_boom).train(_ENTRIES)

    def test_stump_deterministic(self) -> None:
        a1, a2 = _arch(), _arch()
        a1.train(_ENTRIES)
        a2.train(_ENTRIES)
        f = {"momentum": 0.9, "vol": 0.2}
        assert a1.predict(f).signal == a2.predict(f).signal


# ──────────────────────────────────────────────────────────────────────────────
# 预测 + 决策路径
# ──────────────────────────────────────────────────────────────────────────────


class TestPredict:
    def test_predict_before_train_rejected(self) -> None:
        with pytest.raises(DecisionTreeArchError):
            _arch().predict({"momentum": 0.9, "vol": 0.2})

    def test_stump_predict_long_and_short(self) -> None:
        arch = _arch()
        arch.train(_ENTRIES)
        assert arch.predict({"momentum": 0.95, "vol": 0.2}).signal == 1
        assert arch.predict({"momentum": 0.05, "vol": 0.2}).signal == -1

    def test_gbm_predict_uses_injected_model(self) -> None:
        arch = _arch(gbm_trainer=_fake_trainer)
        arch.train(_ENTRIES)
        pred = arch.predict({"momentum": 0.9, "vol": 0.9})
        assert pred.signal == 1
        assert "gbm_ensemble" in pred.path
        assert pred.detail["model_kind"] == "gbm_injected"

    def test_stump_path_structure(self) -> None:
        arch = _arch()
        arch.train(_ENTRIES)
        path = arch.predict({"momentum": 0.9, "vol": 0.2}).path
        assert path[0] == "root"
        assert path[1].startswith("feature=")
        assert path[-1].startswith("leaf=")

    def test_predict_feature_key_mismatch_rejected(self) -> None:
        arch = _arch()
        arch.train(_ENTRIES)
        with pytest.raises(DecisionTreeArchError):
            arch.predict({"momentum": 0.9})
        with pytest.raises(DecisionTreeArchError):
            arch.predict({})


# ──────────────────────────────────────────────────────────────────────────────
# 人工干预钩子
# ──────────────────────────────────────────────────────────────────────────────


class TestIntervention:
    def test_hook_overrides_signal_with_trail(self) -> None:
        arch = _arch()
        arch.train(_ENTRIES)
        arch.register_intervention_hook("root", lambda f, s: -1)
        pred = arch.predict({"momentum": 0.95, "vol": 0.2})
        assert pred.signal == -1
        assert pred.intervened is True
        trail = arch.interventions()
        assert len(trail) == 1
        assert trail[0].original_signal == 1
        assert trail[0].override_signal == -1
        assert trail[0].intervened_at == _T0

    def test_hook_none_keeps_signal(self) -> None:
        arch = _arch()
        arch.train(_ENTRIES)
        arch.register_intervention_hook("*", lambda f, s: None)
        pred = arch.predict({"momentum": 0.95, "vol": 0.2})
        assert pred.signal == 1
        assert pred.intervened is False
        assert arch.interventions() == []

    def test_wildcard_hook_fires_on_any_node(self) -> None:
        arch = _arch()
        arch.train(_ENTRIES)
        calls: list[int] = []
        arch.register_intervention_hook("*", lambda f, s: calls.append(s) or None)
        arch.predict({"momentum": 0.95, "vol": 0.2})
        assert calls  # 至少触发一次

    def test_hook_exception_fail_closed(self) -> None:
        arch = _arch()
        arch.train(_ENTRIES)

        def _boom(f, s):
            raise RuntimeError("人工台掉线")

        arch.register_intervention_hook("root", _boom)
        with pytest.raises(DecisionTreeArchError):
            arch.predict({"momentum": 0.95, "vol": 0.2})

    def test_register_empty_node_key_rejected(self) -> None:
        with pytest.raises(DecisionTreeArchError):
            _arch().register_intervention_hook("", lambda f, s: None)


# ──────────────────────────────────────────────────────────────────────────────
# 解释（SHAP 注入 / 重要性兜底）
# ──────────────────────────────────────────────────────────────────────────────


class TestExplain:
    def test_shap_injected_preferred(self) -> None:
        arch = _arch(
            gbm_trainer=_fake_trainer,
            shap_explainer=lambda m, rows: {"momentum": 0.6, "vol": 0.4},
        )
        arch.train(_ENTRIES)
        assert arch.explain() == {"momentum": 0.6, "vol": 0.4}

    def test_fallback_feature_importances_from_model(self) -> None:
        arch = _arch(gbm_trainer=_fake_trainer)
        arch.train(_ENTRIES)
        assert arch.explain() == {"momentum": 0.7, "vol": 0.3}

    def test_fallback_stump_importance(self) -> None:
        arch = _arch()
        arch.train(_ENTRIES)
        importance = arch.explain()
        assert set(importance) == {"momentum", "vol"}
        assert importance["momentum"] == 1.0  # stump 选中特征
        assert importance["vol"] == 0.0

    def test_explain_before_train_rejected(self) -> None:
        with pytest.raises(DecisionTreeArchError):
            _arch().explain()

    def test_shap_exception_fail_closed(self) -> None:
        def _boom(m, rows):
            raise RuntimeError("shap 崩溃")

        arch = _arch(gbm_trainer=_fake_trainer, shap_explainer=_boom)
        arch.train(_ENTRIES)
        with pytest.raises(DecisionTreeArchError):
            arch.explain()

    def test_shap_non_mapping_output_rejected(self) -> None:
        arch = _arch(gbm_trainer=_fake_trainer, shap_explainer=lambda m, rows: [0.5, 0.5])
        arch.train(_ENTRIES)
        with pytest.raises(DecisionTreeArchError):
            arch.explain()


# ──────────────────────────────────────────────────────────────────────────────
# RL 仅离线语义
# ──────────────────────────────────────────────────────────────────────────────


class TestRlOfflineSemantic:
    def test_rl_offline_note(self) -> None:
        assert "离线" in RL_PPO_OFFLINE_ONLY
        assert _arch().rl_ppo_offline_semantic == RL_PPO_OFFLINE_ONLY
