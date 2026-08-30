# [A_test] module_id: MOD-PLAN-016 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-PLAN-016 | 待统筹登记 | 44号 §9.3 + 92号 §8.7
# [MODULE] tests.plan_engine.test_similar_day_evaluator
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] testing
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

"""SimilarDayEvaluator（MOD-PLAN-016）施工验证测试。

覆盖：
- walk-forward 命中率计算（滚动窗口，防前视）；
- Brier 校准（confidence_scale × hit）；
- 启用/停用建议（命中率 <55% → 停用；样本不足 → 默认启用）；
- 零样本 → 默认启用 + walkforward_hit_rate=None；
- 输入校验 fail-closed。
纯内存夹具（tmp 库 + 手工 prediction_log 行），不触真 governance.db。
"""

from __future__ import annotations

from pathlib import Path

import pytest

from zephyr.plan_engine.similar_day_evaluator import (
    SimilarDayEvalConfig,
    evaluate_similar_day_hit_rate,
)
from zephyr.reporting.prediction_log_writer import (
    ensure_prediction_log_table,
    log_prediction,
)


@pytest.fixture
def tmp_db(tmp_path: Path) -> Path:
    db = tmp_path / "governance.db"
    ensure_prediction_log_table(db)
    return db


def _log_plan(db: Path, trade_date: str, scenario: str, confidence: float = 1.0) -> int:
    return log_prediction(
        trade_date=trade_date,
        module="plan_engine.scenario_planner",
        prediction_type="scenario_plan",
        payload={"final_scenario": scenario, "confidence_scale": confidence},
        db_path=db,
    )


def _log_outcome(db: Path, trade_date: str, hit: bool, actual: str = "HIGH_OPEN_REAL_UP") -> int:
    return log_prediction(
        trade_date=trade_date,
        module="plan_engine.scenario_planner",
        prediction_type="outcome",
        payload={"hit": hit, "actual_scenario": actual, "trend_source": "kline_etf_1min"},
        db_path=db,
    )


def test_zero_samples_default_enabled(tmp_db: Path):
    """零样本 → 默认启用，walkforward_hit_rate=None。"""
    report = evaluate_similar_day_hit_rate("2026-08-30", db_path=tmp_db)
    assert report.suggested_enabled is True
    assert report.walkforward_hit_rate is None
    assert report.latest is None
    assert len(report.series) == 0


def test_hit_rate_below_floor_suggests_disable(tmp_db: Path):
    """命中率 <55% 且样本 ≥10 → 建议停用。"""
    # 10 样本，4 命中 → 40% < 55%
    for i in range(10):
        td = f"2026-08-{20 + i:02d}"
        _log_plan(tmp_db, td, "HIGH_OPEN_REAL_UP", confidence=1.0)
        _log_outcome(tmp_db, td, hit=(i < 4))
    report = evaluate_similar_day_hit_rate("2026-08-30", db_path=tmp_db)
    assert report.suggested_enabled is False
    assert report.walkforward_hit_rate == pytest.approx(0.4)
    assert report.latest is not None
    assert "停用" in report.latest.reason


def test_hit_rate_above_floor_suggests_enable(tmp_db: Path):
    """命中率 ≥55% → 建议启用。"""
    # 10 样本，6 命中 → 60% ≥ 55%
    for i in range(10):
        td = f"2026-08-{20 + i:02d}"
        _log_plan(tmp_db, td, "HIGH_OPEN_REAL_UP", confidence=0.8)
        _log_outcome(tmp_db, td, hit=(i < 6))
    report = evaluate_similar_day_hit_rate("2026-08-30", db_path=tmp_db)
    assert report.suggested_enabled is True
    assert report.walkforward_hit_rate == pytest.approx(0.6)
    assert report.latest is not None
    assert "维持启用" in report.latest.reason


def test_insufficient_samples_default_enabled(tmp_db: Path):
    """样本 < min_samples → 默认启用（不阻塞）。"""
    for i in range(5):
        td = f"2026-08-{20 + i:02d}"
        _log_plan(tmp_db, td, "HIGH_OPEN_REAL_UP")
        _log_outcome(tmp_db, td, hit=False)
    report = evaluate_similar_day_hit_rate("2026-08-30", db_path=tmp_db)
    assert report.suggested_enabled is True
    assert report.latest is not None
    assert "样本不足" in report.latest.reason


def test_walkforward_no_lookahead(tmp_db: Path):
    """防前视：评估日当日样本不参与自身评估。"""
    # 2026-08-25 之前全错，当天全对 → 25 日评估仍用旧样本（命中率低）
    for i in range(10):
        td = f"2026-08-{10 + i:02d}"
        _log_plan(tmp_db, td, "HIGH_OPEN_REAL_UP")
        _log_outcome(tmp_db, td, hit=False)
    # 25 日当天：预测+ outcome 全对（但 walk-forward 评估 25 日时不应包含 26 日样本）
    _log_plan(tmp_db, "2026-08-25", "HIGH_OPEN_REAL_UP")
    _log_outcome(tmp_db, "2026-08-25", hit=True)

    report = evaluate_similar_day_hit_rate("2026-08-26", db_path=tmp_db)
    # 最新评估点应为 2026-08-25，其样本窗口含 25 日（<=25），但不含 26 日
    # 10 错 + 1 对 = 11 样本，1 命中 → 9.1% < 55% → 停用
    assert report.suggested_enabled is False
    assert report.walkforward_hit_rate == pytest.approx(1 / 11)


def test_brier_computed_with_sufficient_samples(tmp_db: Path):
    """样本 ≥3 时 Brier 非 None。"""
    for i in range(5):
        td = f"2026-08-{20 + i:02d}"
        _log_plan(tmp_db, td, "HIGH_OPEN_REAL_UP", confidence=0.7)
        _log_outcome(tmp_db, td, hit=(i % 2 == 0))
    report = evaluate_similar_day_hit_rate("2026-08-30", db_path=tmp_db)
    assert report.latest is not None
    assert report.latest.brier is not None
    assert 0.0 <= report.latest.brier <= 1.0


def test_invalid_eval_date_fail_closed(tmp_db: Path):
    """eval_date 非法 → ValueError。"""
    with pytest.raises(ValueError):
        evaluate_similar_day_hit_rate("not-a-date", db_path=tmp_db)


def test_custom_config_threshold(tmp_db: Path):
    """自定义阈值：60% 命中率在 floor=0.70 下应停用。"""
    for i in range(10):
        td = f"2026-08-{20 + i:02d}"
        _log_plan(tmp_db, td, "HIGH_OPEN_REAL_UP")
        _log_outcome(tmp_db, td, hit=(i < 6))
    cfg = SimilarDayEvalConfig(hit_rate_floor=0.70, min_samples=5)
    report = evaluate_similar_day_hit_rate("2026-08-30", config=cfg, db_path=tmp_db)
    assert report.suggested_enabled is False
    assert report.walkforward_hit_rate == pytest.approx(0.6)


def test_to_dict_json_serializable(tmp_db: Path):
    """报告 JSON 可序列化。"""
    import json

    _log_plan(tmp_db, "2026-08-20", "HIGH_OPEN_REAL_UP")
    _log_outcome(tmp_db, "2026-08-20", hit=True)
    report = evaluate_similar_day_hit_rate("2026-08-30", db_path=tmp_db)
    payload = json.loads(json.dumps(report.to_dict(), ensure_ascii=False))
    assert payload["module"] == "plan_engine.scenario_planner"
    assert payload["suggested_enabled"] is True
