# [BLUEPRINT] MOD-BT-028 | docs/03_modules/_domain_backtest/strategy_cpcv_matrix/blueprint.md | §test
# [MODULE] tests.backtest.test_strategy_cpcv_matrix
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.backtest.core.strategy_cpcv_matrix
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] test_strategy_cpcv_matrix.py
# [A_test] module_id: MOD-BT-028 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-BT-028 单元测试: 第五层多策略交叉验证（策略级CPCV打分矩阵+交集筛选）。

覆盖: 切分复用组合数与逐折 IS/OOS 均值对齐、稳健秩口径（降序秩均值/策略数）、
交集筛选票数门槛与 30 封顶、空稳健池 degraded 留痕、非法输入 Fail-Closed。
"""

from __future__ import annotations

import math

import pytest

from zephyr.backtest.core.strategy_cpcv_matrix import (
    StrategyCPCVConfig,
    StrategyCPCVError,
    build_score_matrix,
    compute_robust_scores,
    run_strategy_cpcv,
    select_candidates,
)

_SIDS = ["s_a", "s_b", "s_c"]


def _perf() -> list[list[float]]:
    # 3 策略 × 12 样本；s_a 恒强(0.10)，s_b 中等(0.05)，s_c 恒弱(-0.02)
    return [
        [0.10] * 12,
        [0.05] * 12,
        [-0.02] * 12,
    ]


class TestConfig:
    def test_defaults(self) -> None:
        cfg = StrategyCPCVConfig()
        assert cfg.n_groups == 6
        assert cfg.k_test == 2
        assert cfg.robust_threshold == 0.5
        assert cfg.min_votes == 2
        assert cfg.max_candidates == 30

    def test_invalid_threshold_rejected(self) -> None:
        with pytest.raises(StrategyCPCVError):
            StrategyCPCVConfig(robust_threshold=0.0)
        with pytest.raises(StrategyCPCVError):
            StrategyCPCVConfig(robust_threshold=1.5)

    def test_invalid_votes_rejected(self) -> None:
        with pytest.raises(StrategyCPCVError):
            StrategyCPCVConfig(min_votes=0)
        with pytest.raises(StrategyCPCVError):
            StrategyCPCVConfig(max_candidates=0)


class TestBuildScoreMatrix:
    def test_split_count_matches_cpcv_combination(self) -> None:
        scores = build_score_matrix(_perf(), _SIDS, StrategyCPCVConfig())
        assert len(scores) == math.comb(6, 2)

    def test_is_oos_means_align_with_constant_series(self) -> None:
        scores = build_score_matrix(_perf(), _SIDS, StrategyCPCVConfig())
        first = scores[0]
        assert set(first.is_means) == set(_SIDS)
        assert set(first.oos_means) == set(_SIDS)
        assert first.is_means["s_a"] == pytest.approx(0.10)
        assert first.oos_means["s_c"] == pytest.approx(-0.02)

    def test_shape_mismatch_rejected(self) -> None:
        with pytest.raises(StrategyCPCVError):
            build_score_matrix([[0.1] * 12, [0.2] * 11], ["a", "b"], StrategyCPCVConfig())

    def test_non_finite_rejected(self) -> None:
        bad = _perf()
        bad[0][3] = float("nan")
        with pytest.raises(StrategyCPCVError):
            build_score_matrix(bad, _SIDS, StrategyCPCVConfig())

    def test_strategy_id_mismatch_rejected(self) -> None:
        with pytest.raises(StrategyCPCVError):
            build_score_matrix(_perf(), ["only_one"], StrategyCPCVConfig())
        with pytest.raises(StrategyCPCVError):
            build_score_matrix(_perf(), ["a", "a", "b"], StrategyCPCVConfig())


class TestRobustScores:
    def test_rank_order(self) -> None:
        scores = build_score_matrix(_perf(), _SIDS, StrategyCPCVConfig())
        robust = compute_robust_scores(scores)
        # s_a 每折 OOS 最优(秩1/3)、s_b 秩2/3、s_c 秩3/3
        assert robust["s_a"] == pytest.approx(1.0 / 3.0)
        assert robust["s_b"] == pytest.approx(2.0 / 3.0)
        assert robust["s_c"] == pytest.approx(1.0)

    def test_ties_share_average_rank(self) -> None:
        perf = [[0.05] * 12, [0.05] * 12, [0.01] * 12]
        scores = build_score_matrix(perf, _SIDS, StrategyCPCVConfig())
        robust = compute_robust_scores(scores)
        # 同值平均秩 (1+2)/2=1.5 → 1.5/3=0.5
        assert robust["s_a"] == pytest.approx(0.5)
        assert robust["s_b"] == pytest.approx(0.5)
        assert robust["s_c"] == pytest.approx(1.0)


class TestSelectCandidates:
    def test_intersection_min_votes_and_pool_filter(self) -> None:
        robust = {"s_a": 1.0 / 3.0, "s_b": 2.0 / 3.0, "s_c": 1.0}
        votes = {
            "s_a": ["000001.SZ", "000002.SZ", "600000.SH"],
            "s_b": ["000001.SZ", "000002.SZ"],
            "s_c": ["000001.SZ", "999999.SH"],  # s_c 不在稳健池(>0.5)
        }
        report = select_candidates(robust, votes, StrategyCPCVConfig())
        assert report.degraded is False
        assert set(report.robust_pool) == {"s_a"}  # 仅 s_a <=0.5
        # 池内仅 s_a 提名，min_votes=2 → 无候选满足
        assert report.selected_candidates == ()

    def test_intersection_selects_multi_nominated(self) -> None:
        robust = {"s_a": 0.3, "s_b": 0.4, "s_c": 1.0}
        votes = {
            "s_a": ["AAA", "BBB", "CCC"],
            "s_b": ["AAA", "BBB"],
            "s_c": ["ZZZ"],
        }
        report = select_candidates(robust, votes, StrategyCPCVConfig())
        assert [c for c, _ in report.selected_candidates] == ["AAA", "BBB"]
        assert dict(report.selected_candidates)["AAA"] == 2

    def test_max_candidates_cap(self) -> None:
        robust = {"s_a": 0.3, "s_b": 0.4}
        votes = {
            "s_a": [f"C{i:03d}" for i in range(40)],
            "s_b": [f"C{i:03d}" for i in range(40)],
        }
        report = select_candidates(robust, votes, StrategyCPCVConfig())
        assert len(report.selected_candidates) == 30

    def test_empty_pool_degraded(self) -> None:
        robust = {"s_a": 0.9, "s_b": 1.0}
        votes = {"s_a": ["AAA"], "s_b": ["AAA"]}
        report = select_candidates(robust, votes, StrategyCPCVConfig())
        assert report.degraded is True
        assert report.robust_pool == ()
        assert report.selected_candidates == ()

    def test_unknown_strategy_vote_rejected(self) -> None:
        with pytest.raises(StrategyCPCVError):
            select_candidates({"s_a": 0.3}, {"ghost": ["AAA"]}, StrategyCPCVConfig())


class TestRunPipeline:
    def test_end_to_end(self) -> None:
        votes = {
            "s_a": ["AAA", "BBB"],
            "s_b": ["AAA"],
            "s_c": ["CCC"],
        }
        report = run_strategy_cpcv(_perf(), _SIDS, votes, StrategyCPCVConfig(min_votes=1))
        assert len(report.split_scores) == math.comb(6, 2)
        assert report.degraded is False
        picked = dict(report.selected_candidates)
        # s_c 稳健分=1.0 出池 → CCC 落选；AAA 双提名居首
        assert "CCC" not in picked
        assert report.selected_candidates[0][0] == "AAA"
