# [A_test] module_id: MOD-PLAN-009 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-PLAN-009 | 待统筹登记 | 45号 §4 W0 + 缺口总账 GAP-F-07②
# [MODULE] tests.plan_engine.test_scenario_attribution_stats
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] testing
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

"""ScenarioAttributionStats (MOD-PLAN-009) 施工验证测试。

覆盖：
- compute_attribution 纯函数：空输入/单记录/多组聚合；按情景分支×维度×信号源
  三维边际桶 + 三维复合桶命中率口径；确定性排序；非法记录 fail-closed。
- load_attribution_records 读库器：outcome 族契约字段提取（scenario/dimension/
  signal_source/hit）；窗口过滤（默认近 20 日，as_of 可注入）；契约字段缺失/
  类型错 → skipped_invalid 计数不计样本；非 outcome 族行不混入。
- compute_scenario_attribution 组合入口：端到端报告字段+to_dict JSON 可序列化。
全 tmp 库隔离，不触真 governance.db。
"""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import pytest

from zephyr.plan_engine.scenario_attribution_stats import (
    DEFAULT_WINDOW_DAYS,
    AttributionRecord,
    AttributionReport,
    compute_attribution,
    compute_scenario_attribution,
    load_attribution_records,
)
from zephyr.reporting.prediction_calibration_monitor import record_outcome
from zephyr.reporting.prediction_log_writer import (
    ensure_prediction_log_table,
    log_prediction,
)

MODULE = "plan_engine.scenario_planner"
AS_OF = date(2026, 8, 21)


def _iso(d: date) -> str:
    return d.isoformat()


@pytest.fixture
def tmp_db(tmp_path: Path) -> Path:
    db = tmp_path / "governance.db"
    ensure_prediction_log_table(db)
    return db


def _rec(scenario: str, dimension: str, source: str, hit: bool) -> AttributionRecord:
    return AttributionRecord(scenario=scenario, dimension=dimension, signal_source=source, hit=hit)


def _seed_outcome(
    db: Path,
    trade_date: str,
    *,
    hit: bool,
    scenario: str | None = "HIGH_OPEN_REAL_UP",
    dimension: str | None = "prediction",
    source: str | None = "MOD-PLAN-005.scenario_planner",
) -> None:
    payload: dict = {"hit": hit}
    if scenario is not None:
        payload["scenario"] = scenario
    if dimension is not None:
        payload["dimension"] = dimension
    if source is not None:
        payload["signal_source"] = source
    record_outcome(trade_date=trade_date, module=MODULE, outcome_payload=payload, db_path=db)


# ══════════════════════════════════════════════════════════════
# compute_attribution 纯函数
# ══════════════════════════════════════════════════════════════


class TestComputeAttribution:
    def test_empty(self) -> None:
        report = compute_attribution([])
        assert report.sample_size == 0
        assert report.by_scenario == ()
        assert report.by_dimension == ()
        assert report.by_signal_source == ()
        assert report.by_cell == ()

    def test_single_record(self) -> None:
        report = compute_attribution([_rec("HIGH_OPEN_REAL_UP", "prediction", "srcA", True)])
        assert report.sample_size == 1
        assert report.by_scenario[0].key == "HIGH_OPEN_REAL_UP"
        assert report.by_scenario[0].hit_rate == 1.0

    def test_scenario_marginal(self) -> None:
        records = [
            _rec("HIGH_OPEN_REAL_UP", "prediction", "srcA", True),
            _rec("HIGH_OPEN_REAL_UP", "prediction", "srcA", False),
            _rec("LOW_OPEN_WASH", "prediction", "srcA", True),
        ]
        report = compute_attribution(records)
        by_key = {b.key: b for b in report.by_scenario}
        assert by_key["HIGH_OPEN_REAL_UP"].sample_size == 2
        assert by_key["HIGH_OPEN_REAL_UP"].hit_count == 1
        assert by_key["HIGH_OPEN_REAL_UP"].hit_rate == 0.5
        assert by_key["LOW_OPEN_WASH"].hit_rate == 1.0

    def test_dimension_and_source_marginals(self) -> None:
        records = [
            _rec("HIGH_OPEN_REAL_UP", "prediction", "srcA", True),
            _rec("HIGH_OPEN_REAL_UP", "execution", "srcA", False),
            _rec("FLAT_OPEN_WASH", "pnl", "srcB", True),
            _rec("FLAT_OPEN_WASH", "pnl", "srcB", False),
        ]
        report = compute_attribution(records)
        dim = {b.key: b for b in report.by_dimension}
        assert dim["prediction"].hit_rate == 1.0
        assert dim["execution"].hit_rate == 0.0
        assert dim["pnl"].hit_rate == 0.5
        src = {b.key: b for b in report.by_signal_source}
        assert src["srcA"].sample_size == 2
        assert src["srcB"].sample_size == 2

    def test_cell_triple_composite(self) -> None:
        records = [
            _rec("HIGH_OPEN_REAL_UP", "prediction", "srcA", True),
            _rec("HIGH_OPEN_REAL_UP", "prediction", "srcA", False),
            _rec("HIGH_OPEN_REAL_UP", "execution", "srcA", True),
        ]
        report = compute_attribution(records)
        cells = {b.key: b for b in report.by_cell}
        assert cells["HIGH_OPEN_REAL_UP|prediction|srcA"].hit_rate == 0.5
        assert cells["HIGH_OPEN_REAL_UP|execution|srcA"].hit_rate == 1.0
        assert len(cells) == 2

    def test_deterministic_sorting(self) -> None:
        records = [
            _rec("LOW_OPEN_WASH", "pnl", "srcB", True),
            _rec("HIGH_OPEN_REAL_UP", "prediction", "srcA", True),
        ]
        r1 = compute_attribution(records)
        r2 = compute_attribution(list(reversed(records)))
        assert [b.key for b in r1.by_scenario] == [b.key for b in r2.by_scenario]
        assert [b.key for b in r1.by_scenario] == sorted(b.key for b in r1.by_scenario)

    def test_invalid_record_fail_closed(self) -> None:
        with pytest.raises(ValueError):
            compute_attribution([{"scenario": "X"}])  # type: ignore[list-item]

    def test_report_to_dict_jsonable(self) -> None:
        report = compute_attribution(
            [_rec("HIGH_OPEN_REAL_UP", "prediction", "srcA", True)],
            module=MODULE,
            window_days=20,
            window_start="2026-08-01",
            window_end="2026-08-21",
        )
        d = report.to_dict()
        assert d["module"] == MODULE
        assert d["sample_size"] == 1
        assert d["by_scenario"][0]["key"] == "HIGH_OPEN_REAL_UP"
        import json

        json.dumps(d)  # 不抛即可序列化


# ══════════════════════════════════════════════════════════════
# load_attribution_records 读库器
# ══════════════════════════════════════════════════════════════


class TestLoadAttributionRecords:
    def test_load_ok(self, tmp_db: Path) -> None:
        _seed_outcome(tmp_db, _iso(AS_OF), hit=True)
        _seed_outcome(tmp_db, _iso(AS_OF - timedelta(days=1)), hit=False, scenario="LOW_OPEN_WASH")
        records, skipped = load_attribution_records(MODULE, db_path=tmp_db, as_of=AS_OF)
        assert skipped == 0
        assert len(records) == 2
        assert all(isinstance(r, AttributionRecord) for r in records)
        hits = sorted(r.hit for r in records)
        assert hits == [False, True]

    def test_window_filter(self, tmp_db: Path) -> None:
        inside = AS_OF - timedelta(days=DEFAULT_WINDOW_DAYS - 1)
        outside = AS_OF - timedelta(days=DEFAULT_WINDOW_DAYS)
        _seed_outcome(tmp_db, _iso(inside), hit=True)
        _seed_outcome(tmp_db, _iso(outside), hit=False)
        records, _ = load_attribution_records(MODULE, db_path=tmp_db, as_of=AS_OF)
        assert len(records) == 1
        assert records[0].hit is True

    def test_invalid_payload_skipped(self, tmp_db: Path) -> None:
        _seed_outcome(tmp_db, _iso(AS_OF), hit=True)
        _seed_outcome(tmp_db, _iso(AS_OF), hit=True, scenario=None)  # 缺 scenario
        _seed_outcome(tmp_db, _iso(AS_OF), hit=True, dimension=None)  # 缺 dimension
        _seed_outcome(tmp_db, _iso(AS_OF), hit=True, source=None)  # 缺 signal_source
        records, skipped = load_attribution_records(MODULE, db_path=tmp_db, as_of=AS_OF)
        assert len(records) == 1
        assert skipped == 3

    def test_non_outcome_rows_not_mixed(self, tmp_db: Path) -> None:
        _seed_outcome(tmp_db, _iso(AS_OF), hit=True)
        log_prediction(
            trade_date=_iso(AS_OF), module=MODULE, prediction_type="scenario_plan",
            payload={"final_scenario": "HIGH_OPEN_REAL_UP"}, db_path=tmp_db,
        )
        records, skipped = load_attribution_records(MODULE, db_path=tmp_db, as_of=AS_OF)
        assert len(records) == 1
        assert skipped == 0

    def test_module_validation_fail_closed(self, tmp_db: Path) -> None:
        with pytest.raises(ValueError):
            load_attribution_records("", db_path=tmp_db, as_of=AS_OF)
        with pytest.raises(ValueError):
            load_attribution_records(MODULE, window_days=0, db_path=tmp_db, as_of=AS_OF)


# ══════════════════════════════════════════════════════════════
# compute_scenario_attribution 组合入口
# ══════════════════════════════════════════════════════════════


class TestComputeScenarioAttribution:
    def test_end_to_end(self, tmp_db: Path) -> None:
        base = AS_OF - timedelta(days=2)
        _seed_outcome(tmp_db, _iso(base), hit=True, scenario="HIGH_OPEN_REAL_UP")
        _seed_outcome(tmp_db, _iso(base + timedelta(days=1)), hit=False, scenario="HIGH_OPEN_REAL_UP")
        _seed_outcome(tmp_db, _iso(AS_OF), hit=True, scenario="FLAT_OPEN_WASH", dimension="execution")
        report = compute_scenario_attribution(MODULE, db_path=tmp_db, as_of=AS_OF)
        assert isinstance(report, AttributionReport)
        assert report.sample_size == 3
        assert report.window_days == DEFAULT_WINDOW_DAYS
        assert report.window_end == _iso(AS_OF)
        scen = {b.key: b for b in report.by_scenario}
        assert scen["HIGH_OPEN_REAL_UP"].hit_rate == 0.5
        assert scen["FLAT_OPEN_WASH"].hit_rate == 1.0
        dim = {b.key: b for b in report.by_dimension}
        assert dim["prediction"].sample_size == 2
        assert dim["execution"].sample_size == 1

    def test_empty_db(self, tmp_db: Path) -> None:
        report = compute_scenario_attribution(MODULE, db_path=tmp_db, as_of=AS_OF)
        assert report.sample_size == 0
        assert report.by_scenario == ()
