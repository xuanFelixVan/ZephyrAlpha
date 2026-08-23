# [BLUEPRINT] MOD-ML-007 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [A_test] module_id: MOD-ML_test_meta_learning_evolution | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.ml_train.test_meta_learning_evolution
# [TESTS] src/zephyr/ml_train/meta_learning_evolution.py
# [TTL] task_bound
"""MOD-ML-007 元学习演进 toy 断言（跨任务经验库，轻量）。"""

from __future__ import annotations

import pytest

from zephyr.ml_train.meta_learning_evolution import (
    MetaLearningStore,
    TaskExperience,
)


def _exp(task: str, score: float, **ctx) -> TaskExperience:
    return TaskExperience(task_id=task, context=ctx, metrics={"score": score})


class TestExperienceStore:
    def test_record_and_recall_by_task(self):
        store = MetaLearningStore()
        store.record(_exp("density", 0.8, regime="trend_up"))
        store.record(_exp("density", 0.6, regime="ranging"))
        got = store.recall(task_id="density")
        assert len(got) == 2

    def test_recall_unknown_task_empty(self):
        store = MetaLearningStore()
        assert store.recall(task_id="ghost") == []


class TestCrossTaskRecommendation:
    def test_recommend_picks_best_context_match(self):
        """轻量经验复用：同 regime 上下文的历史最佳配置应被推荐。"""
        store = MetaLearningStore()
        store.record(_exp("density", 0.9, regime="trend_up", lr=0.05))
        store.record(_exp("density", 0.4, regime="ranging", lr=0.1))
        rec = store.recommend(task_id="density", context={"regime": "trend_up"})
        assert rec is not None
        assert rec.metrics["score"] == 0.9
        assert rec.context["lr"] == 0.05

    def test_recommend_falls_back_to_global_best_when_no_context_match(self):
        store = MetaLearningStore()
        store.record(_exp("density", 0.3, regime="panic"))
        rec = store.recommend(task_id="density", context={"regime": "euphoria"})
        assert rec is not None
        assert rec.metrics["score"] == 0.3  # 无上下文匹配回退全局最佳

    def test_recommend_empty_store_returns_none(self):
        store = MetaLearningStore()
        assert store.recommend(task_id="density", context={}) is None


class TestEvolutionSummary:
    def test_summary_tracks_best_and_trend(self):
        store = MetaLearningStore()
        store.record(_exp("t", 0.5))
        store.record(_exp("t", 0.7))
        store.record(_exp("t", 0.6))
        s = store.evolution_summary("t", metric="score")
        assert s["n_experiences"] == 3
        assert s["best"] == 0.7
        assert s["latest"] == 0.6

    def test_summary_unknown_task_raises(self):
        store = MetaLearningStore()
        with pytest.raises(ValueError, match="无经验"):
            store.evolution_summary("ghost", metric="score")
