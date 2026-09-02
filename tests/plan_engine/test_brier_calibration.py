# [A_test] module_id: MOD-PLAN-010 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-PLAN-010 | 待统筹登记 | 45号 §4 W0 + 缺口总账 GAP-F-07③
# [MODULE] tests.plan_engine.test_brier_calibration
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] testing
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

"""BrierCalibration (MOD-PLAN-010) 施工验证测试。

覆盖：
- brier_score 纯函数：完美预测 0 / 全错 1 / 0.5 预测 0.25 经典值；批量均值；
  bool/int/float outcome 兼容；非法（p 越界/outcome 非 0|1/空序列/NaN）fail-closed。
- brier_score_multiclass 纯函数：9 格 one-hot 语义（完美 0/部分概率质量）；
  分布和≠1/索引越界 fail-closed。
- calibration_bins 纯函数：分桶边界（左闭右开+末桶含 1.0）；桶内均值/经验频率/
  校准差；空桶 None；ECE 加权和。
- load_confidence_pairs / compute_calibration 读库组合：probability 字段优先、
  predicted_confidence 兜底；hit→0/1；窗口过滤；非法行 skipped；报告 JSON 可序列化。
全 tmp 库隔离，不触真 governance.db。
"""

from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

import pytest

from zephyr.plan_engine.brier_calibration import (
    CalibrationReport,
    brier_score,
    brier_score_multiclass,
    calibration_bins,
    compute_calibration,
    expected_calibration_error,
    load_confidence_pairs,
)
from zephyr.reporting.prediction_calibration_monitor import record_outcome
from zephyr.reporting.prediction_log_writer import ensure_prediction_log_table

MODULE = "plan_engine.scenario_planner"
AS_OF = date(2026, 8, 21)


@pytest.fixture
def tmp_db(tmp_path: Path) -> Path:
    db = tmp_path / "governance.db"
    ensure_prediction_log_table(db)
    return db


def _seed_outcome(
    db: Path, trade_date: str, *, hit: bool, prob: float | None = None, conf: float | None = None
) -> None:
    payload: dict = {"hit": hit}
    if prob is not None:
        payload["probability"] = prob
    if conf is not None:
        payload["predicted_confidence"] = conf
    record_outcome(trade_date=trade_date, module=MODULE, outcome_payload=payload, db_path=db)


# ══════════════════════════════════════════════════════════════
# brier_score 纯函数
# ══════════════════════════════════════════════════════════════


class TestBrierScore:
    def test_perfect_zero(self) -> None:
        assert brier_score([(1.0, 1), (0.0, 0)]) == 0.0

    def test_worst_one(self) -> None:
        assert brier_score([(1.0, 0), (0.0, 1)]) == 1.0

    def test_coin_flip(self) -> None:
        assert brier_score([(0.5, 1)]) == 0.25

    def test_batch_mean(self) -> None:
        # ((0.7-1)^2 + (0.3-0)^2) / 2 = (0.09+0.09)/2
        assert brier_score([(0.7, 1), (0.3, 0)]) == pytest.approx(0.09)

    def test_outcome_type_compatibility(self) -> None:
        assert brier_score([(0.9, True), (0.1, False)]) == pytest.approx(0.01)
        assert brier_score([(0.9, 1.0)]) == pytest.approx(0.01)

    def test_invalid_fail_closed(self) -> None:
        with pytest.raises(ValueError):
            brier_score([])  # 空序列
        with pytest.raises(ValueError):
            brier_score([(1.2, 1)])  # p 越界
        with pytest.raises(ValueError):
            brier_score([(-0.1, 0)])
        with pytest.raises(ValueError):
            brier_score([(0.5, 2)])  # outcome 非 0|1
        with pytest.raises(ValueError):
            brier_score([(float("nan"), 1)])


# ══════════════════════════════════════════════════════════════
# brier_score_multiclass 纯函数（9 格概率分布，供 GAP-F-01 消费）
# ══════════════════════════════════════════════════════════════


class TestBrierScoreMulticlass:
    def test_perfect_zero(self) -> None:
        assert brier_score_multiclass([([1.0, 0.0, 0.0], 0)]) == 0.0

    def test_partial_mass(self) -> None:
        # (0.5-1)^2 + 0.5^2 + 0^2 = 0.5
        assert brier_score_multiclass([([0.5, 0.5, 0.0], 0)]) == pytest.approx(0.5)

    def test_wrong_cell(self) -> None:
        # 全部概率押 0 格实际中 1 格：(0-1)^2+(1-0)^2+0 = 2
        assert brier_score_multiclass([([1.0, 0.0, 0.0], 1)]) == pytest.approx(2.0)

    def test_nine_cell(self) -> None:
        dist = [0.0] * 9
        dist[3] = 1.0
        assert brier_score_multiclass([(dist, 3)]) == 0.0

    def test_invalid_fail_closed(self) -> None:
        with pytest.raises(ValueError):
            brier_score_multiclass([])  # 空序列
        with pytest.raises(ValueError):
            brier_score_multiclass([([0.5, 0.4], 0)])  # 分布和≠1
        with pytest.raises(ValueError):
            brier_score_multiclass([([0.5, 0.5], 2)])  # outcome 索引越界
        with pytest.raises(ValueError):
            brier_score_multiclass([([1.1, -0.1], 0)])  # p 越界
        with pytest.raises(ValueError):
            brier_score_multiclass([([], 0)])  # 空分布


# ══════════════════════════════════════════════════════════════
# calibration_bins / expected_calibration_error 纯函数
# ══════════════════════════════════════════════════════════════


class TestCalibrationBins:
    def test_bin_assignment(self) -> None:
        pairs = [(0.05, 0), (0.15, 1), (0.95, 1), (1.0, 1)]
        bins = calibration_bins(pairs, n_bins=10)
        assert len(bins) == 10
        assert bins[0].count == 1
        assert bins[0].mean_predicted == pytest.approx(0.05)
        assert bins[0].empirical_freq == 0.0
        assert bins[1].count == 1
        assert bins[1].empirical_freq == 1.0
        assert bins[9].count == 2  # 0.95 与 1.0 同落末桶（末桶含 1.0）
        assert bins[9].mean_predicted == pytest.approx(0.975)
        assert bins[9].empirical_freq == 1.0

    def test_empty_bin_none(self) -> None:
        bins = calibration_bins([(0.55, 1)], n_bins=10)
        assert bins[0].count == 0
        assert bins[0].mean_predicted is None
        assert bins[0].empirical_freq is None
        assert bins[0].calibration_gap is None

    def test_calibration_gap(self) -> None:
        # 预测 0.8 实际全中 → gap = 0.8-1.0 = -0.2（系统性低估）
        bins = calibration_bins([(0.8, 1), (0.8, 1)], n_bins=10)
        assert bins[8].calibration_gap == pytest.approx(-0.2)

    def test_ece(self) -> None:
        # 两个桶各 1 样本：|0.1-0|×1/2 + |0.9-1|×1/2 = 0.1
        ece = expected_calibration_error([(0.1, 0), (0.9, 1)], n_bins=10)
        assert ece == pytest.approx(0.1)

    def test_invalid_fail_closed(self) -> None:
        with pytest.raises(ValueError):
            calibration_bins([], n_bins=10)  # 空序列
        with pytest.raises(ValueError):
            calibration_bins([(0.5, 1)], n_bins=0)
        with pytest.raises(ValueError):
            calibration_bins([(1.5, 1)], n_bins=10)


# ══════════════════════════════════════════════════════════════
# 读库组合：load_confidence_pairs / compute_calibration
# ══════════════════════════════════════════════════════════════


class TestLoadAndCompute:
    def test_probability_field_priority(self, tmp_db: Path) -> None:
        _seed_outcome(tmp_db, AS_OF.isoformat(), hit=True, prob=0.8, conf=0.25)
        pairs, skipped = load_confidence_pairs(MODULE, db_path=tmp_db, as_of=AS_OF)
        assert skipped == 0
        assert pairs == [(0.8, 1)]  # probability 优先于 predicted_confidence

    def test_confidence_fallback(self, tmp_db: Path) -> None:
        _seed_outcome(tmp_db, AS_OF.isoformat(), hit=False, conf=0.5)
        pairs, _ = load_confidence_pairs(MODULE, db_path=tmp_db, as_of=AS_OF)
        assert pairs == [(0.5, 0)]

    def test_missing_prob_skipped(self, tmp_db: Path) -> None:
        _seed_outcome(tmp_db, AS_OF.isoformat(), hit=True)  # 双字段皆缺
        pairs, skipped = load_confidence_pairs(MODULE, db_path=tmp_db, as_of=AS_OF)
        assert pairs == []
        assert skipped == 1

    def test_window_filter(self, tmp_db: Path) -> None:
        _seed_outcome(tmp_db, (AS_OF - timedelta(days=19)).isoformat(), hit=True, conf=0.9)
        _seed_outcome(tmp_db, (AS_OF - timedelta(days=20)).isoformat(), hit=True, conf=0.9)
        pairs, _ = load_confidence_pairs(MODULE, db_path=tmp_db, as_of=AS_OF)
        assert len(pairs) == 1

    def test_compute_calibration_report(self, tmp_db: Path) -> None:
        base = AS_OF - timedelta(days=1)
        _seed_outcome(tmp_db, base.isoformat(), hit=True, conf=1.0)
        _seed_outcome(tmp_db, base.isoformat(), hit=False, conf=1.0)
        _seed_outcome(tmp_db, AS_OF.isoformat(), hit=True, conf=0.25)
        report = compute_calibration(MODULE, db_path=tmp_db, as_of=AS_OF, n_bins=4)
        assert isinstance(report, CalibrationReport)
        assert report.sample_size == 3
        # brier = (0 + 1 + (0.25-1)^2)/3 = (1+0.5625)/3
        assert report.brier == pytest.approx(1.5625 / 3)
        assert len(report.bins) == 4
        assert report.window_end == AS_OF.isoformat()
        json.dumps(report.to_dict())  # JSON 可序列化

    def test_empty_db_fail_closed(self, tmp_db: Path) -> None:
        with pytest.raises(ValueError):
            compute_calibration(MODULE, db_path=tmp_db, as_of=AS_OF)  # 零样本不可算

    def test_module_validation_fail_closed(self, tmp_db: Path) -> None:
        with pytest.raises(ValueError):
            load_confidence_pairs("  ", db_path=tmp_db, as_of=AS_OF)
