# [BLUEPRINT] MOD-ML-018 | docs/03_modules/_domain_machine_learning_train/continual_learning_antiforget/blueprint.md | §test
# [A_module] module_id=MOD-ML-018 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [A_test] module_id: MOD-ML-018 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.ml_train.test_continual_learning_antiforget
# [TESTS] src/zephyr/ml_train/continual_learning_antiforget.py
"""MOD-ML-018 单元测试：continual_learning_antiforget 持续学习抗遗忘框架。

蓝图验收（B10-01881/CAND-MLT-025，A1 §29.35）：
EWC 正则（Fisher 盘后批处理注入+权重缓存）+ 经验回放（每市场状态≤上限硬约束，
regime 标注注入）+ 微调后旧状态验证（降≤5% 门禁）+ 参数快照回滚。
fisher 估计器/时钟全注入内存替身，不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.ml_train.continual_learning_antiforget",
    reason="continual_learning_antiforget not importable",
)

from zephyr.ml_train.continual_learning_antiforget import (  # noqa: E402
    ContinualLearnError,
    ContinualLearningAntiForget,
)

_T0 = datetime.datetime(2026, 8, 25, 15, 0, 0)
_PARAMS = {"w1": 1.0, "w2": -0.5}


def _fw(**kw) -> ContinualLearningAntiForget:
    kw.setdefault("fisher_estimator", lambda p: {k: 2.0 for k in p})
    kw.setdefault("clock", lambda: _T0)
    return ContinualLearningAntiForget(**kw)


# ──────────────────────────────────────────────────────────────────────────────
# EWC：Fisher 注入计算 + 重要性权重缓存
# ──────────────────────────────────────────────────────────────────────────────


class TestImportance:
    def test_compute_ok_and_cached(self) -> None:
        fw = _fw()
        out = fw.compute_importance(_PARAMS)
        assert out == {"w1": 2.0, "w2": 2.0}
        assert fw.importance_weights() == out  # 权重已缓存

    def test_estimator_not_injected_fail_closed(self) -> None:
        fw = ContinualLearningAntiForget(clock=lambda: _T0)
        with pytest.raises(ContinualLearnError):
            fw.compute_importance(_PARAMS)

    def test_empty_params_raise(self) -> None:
        fw = _fw()
        with pytest.raises(ContinualLearnError):
            fw.compute_importance({})
        with pytest.raises(ContinualLearnError):
            fw.compute_importance({"w1": "x"})  # 非数值

    def test_fisher_missing_param_raise(self) -> None:
        fw = _fw(fisher_estimator=lambda p: {"w1": 1.0})  # 缺 w2
        with pytest.raises(ContinualLearnError):
            fw.compute_importance(_PARAMS)

    def test_fisher_unknown_or_negative_raise(self) -> None:
        fw = _fw(fisher_estimator=lambda p: {**{k: 1.0 for k in p}, "ghost": 1.0})
        with pytest.raises(ContinualLearnError):
            fw.compute_importance(_PARAMS)
        fw2 = _fw(fisher_estimator=lambda p: {k: -1.0 for k in p})
        with pytest.raises(ContinualLearnError):
            fw2.compute_importance(_PARAMS)

    def test_importance_before_compute_raise(self) -> None:
        fw = _fw()
        with pytest.raises(ContinualLearnError):
            fw.importance_weights()


# ──────────────────────────────────────────────────────────────────────────────
# EWC 正则惩罚
# ──────────────────────────────────────────────────────────────────────────────


class TestEwcPenalty:
    def test_zero_at_anchor(self) -> None:
        fw = _fw()
        fw.compute_importance(_PARAMS)
        assert fw.ewc_penalty(_PARAMS) == 0.0

    def test_positive_after_drift_deterministic(self) -> None:
        fw = _fw()
        fw.compute_importance(_PARAMS)
        new = {"w1": 2.0, "w2": -0.5}
        # 2.0*(2-1)^2 + 2.0*0 = 2.0
        assert fw.ewc_penalty(new) == pytest.approx(2.0)
        assert fw.ewc_penalty(new) == fw.ewc_penalty(new)  # 同输入必同输出

    def test_before_importance_raise(self) -> None:
        fw = _fw()
        with pytest.raises(ContinualLearnError):
            fw.ewc_penalty(_PARAMS)

    def test_param_set_mismatch_raise(self) -> None:
        fw = _fw()
        fw.compute_importance(_PARAMS)
        with pytest.raises(ContinualLearnError):
            fw.ewc_penalty({"w1": 1.0, "w3": 0.0})


# ──────────────────────────────────────────────────────────────────────────────
# 经验回放（每市场状态代表样本硬约束）
# ──────────────────────────────────────────────────────────────────────────────


class TestReplay:
    def test_add_and_deterministic_order(self) -> None:
        fw = _fw()
        fw.add_replay_sample("s2", "bull", {"x": 2})
        fw.add_replay_sample("s1", "bull", {"x": 1})
        out = fw.replay_samples("bull")
        assert [s.sample_id for s in out] == ["s1", "s2"]  # 同刻按 id 排序
        assert out[0].payload == {"x": 1}

    def test_empty_fields_raise(self) -> None:
        fw = _fw()
        with pytest.raises(ContinualLearnError):
            fw.add_replay_sample("", "bull", {})
        with pytest.raises(ContinualLearnError):
            fw.add_replay_sample("s1", "", {})  # regime 标注必须注入

    def test_duplicate_sample_id_raise_globally(self) -> None:
        fw = _fw()
        fw.add_replay_sample("s1", "bull", {})
        with pytest.raises(ContinualLearnError):
            fw.add_replay_sample("s1", "bear", {})  # 跨 regime 也判重

    def test_per_regime_hard_cap(self) -> None:
        fw = _fw(max_replay_per_regime=2)
        fw.add_replay_sample("s1", "bull", {})
        fw.add_replay_sample("s2", "bull", {})
        with pytest.raises(ContinualLearnError):
            fw.add_replay_sample("s3", "bull", {})  # bull 已满
        fw.add_replay_sample("s3", "bear", {})  # 其他 regime 不受影响
        assert fw.replay_size("bull") == 2
        assert fw.replay_size("bear") == 1

    def test_unknown_regime_empty_view(self) -> None:
        fw = _fw()
        fw.add_replay_sample("s1", "bull", {})
        assert fw.replay_samples("ghost") == ()
        assert fw.replay_size("ghost") == 0
        with pytest.raises(ContinualLearnError):
            fw.replay_size("")


# ──────────────────────────────────────────────────────────────────────────────
# 参数快照 / 回滚
# ──────────────────────────────────────────────────────────────────────────────


class TestSnapshotRollback:
    def test_snapshot_ids_deterministic_and_isolated(self) -> None:
        fw = _fw()
        params = dict(_PARAMS)
        s1 = fw.snapshot_params(params, tag="t1")
        s2 = fw.snapshot_params({"w1": 9.0}, tag="t2")
        assert (s1.snapshot_id, s2.snapshot_id) == ("snap-0001", "snap-0002")
        params["w1"] = 999.0  # 入参后续变异不影响快照（不可变副本）
        assert fw.rollback_to("snap-0001") == {"w1": 1.0, "w2": -0.5}

    def test_rollback_unknown_raise(self) -> None:
        fw = _fw()
        with pytest.raises(ContinualLearnError):
            fw.rollback_to("ghost")

    def test_latest_snapshot_empty_raise(self) -> None:
        fw = _fw()
        with pytest.raises(ContinualLearnError):
            fw.latest_snapshot()
        with pytest.raises(ContinualLearnError):
            fw.snapshot_params({"w1": True})  # bool 非数值参数


# ──────────────────────────────────────────────────────────────────────────────
# 微调后旧状态验证 + 门禁回滚
# ──────────────────────────────────────────────────────────────────────────────


class TestGate:
    def test_validate_pass_within_5pct(self) -> None:
        fw = _fw()
        results = fw.validate_old_regimes({"bull": 1.0}, {"bull": 0.96})
        assert results[0].passed is True
        assert results[0].drop_ratio == pytest.approx(0.04)
        # 性能提升（负降幅）同样通过
        assert fw.validate_old_regimes({"bull": 1.0}, {"bull": 1.2})[0].passed is True

    def test_validate_fail_over_5pct(self) -> None:
        fw = _fw()
        results = fw.validate_old_regimes({"bull": 1.0, "bear": 2.0}, {"bull": 0.9, "bear": 2.0})
        assert [r.regime for r in results] == ["bear", "bull"]  # 确定性排序
        assert results[1].passed is False
        assert results[1].drop_ratio == pytest.approx(0.1)

    def test_validate_missing_new_metric_raise(self) -> None:
        fw = _fw()
        with pytest.raises(ContinualLearnError):
            fw.validate_old_regimes({"bull": 1.0}, {"bear": 1.0})

    def test_validate_non_positive_baseline_raise(self) -> None:
        fw = _fw()
        with pytest.raises(ContinualLearnError):
            fw.validate_old_regimes({"bull": 0.0}, {"bull": 0.0})

    def test_gate_accept(self) -> None:
        fw = _fw()
        new = {"w1": 1.1, "w2": -0.5}
        decision = fw.finetune_gate(new, {"bull": 1.0}, {"bull": 0.99})
        assert decision.accepted is True
        assert decision.active_params == new
        assert decision.rolled_back_to is None

    def test_gate_rollback_on_fail(self) -> None:
        fw = _fw()
        fw.snapshot_params(_PARAMS, tag="基线")
        decision = fw.finetune_gate({"w1": 5.0, "w2": 0.0}, {"bull": 1.0}, {"bull": 0.8})
        assert decision.accepted is False
        assert decision.rolled_back_to == "snap-0001"
        assert decision.active_params == {"w1": 1.0, "w2": -0.5}  # 回滚快照参数

    def test_gate_fail_without_snapshot_fail_closed(self) -> None:
        fw = _fw()
        with pytest.raises(ContinualLearnError):
            fw.finetune_gate({"w1": 5.0, "w2": 0.0}, {"bull": 1.0}, {"bull": 0.8})
