# [A_test] module_id: MOD-PLAN-008 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-PLAN-008 | 待统筹登记 | 45号 §4 W0/W6 + 缺口总账 GAP-F-07①
# [MODULE] tests.plan_engine.test_scenario_plan_recorder
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] testing
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

"""ScenarioPlanRecorder (MOD-PLAN-008) 施工验证测试。

覆盖：
- determine_actual_scenario 纯函数：开盘桶（±2%）×走势桶（容忍带）→ 9 情景全映射；
  非法输入 fail-closed（None/NaN/超界容忍带配置）。
- record_plan 落库：ScenarioPlan → prediction_log（module/prediction_type 口径）；
  幂等（同计划重复写=同行 id）；表缺失 fail-open 返回 -1 不抛；非 ScenarioPlan 拒收。
- writeback_outcome 回写链路：无预测行跳过；有预测+mock 指数日线/ETF 分钟线
  → outcome 行落库（hit 判定/dimension/scenario/signal_source/predicted_confidence
  契约字段齐全）；分钟数据缺失走 daily_proxy 留痕或按配置跳过；开盘数据缺失跳过；
  CH 异常 fail-open 不炸；同日同内容重复回写幂等。
全 mock CH + tmp 库隔离，不触真 governance.db 与真 ClickHouse。
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from zephyr.plan_engine.premarket_constraint_loader import SCENARIO_LIST
from zephyr.plan_engine.scenario_plan_recorder import (
    DIMENSION_PREDICTION,
    MODULE_LOG_NAME,
    PREDICTION_TYPE_SCENARIO_PLAN,
    SIGNAL_SOURCE,
    ScenarioPlanRecorder,
    ScenarioRecorderConfig,
    compute_and_record_scenario_plan,
    determine_actual_scenario,
    record_scenario_plan,
    writeback_scenario_outcome,
)
from zephyr.plan_engine.scenario_planner import ScenarioPlan
from zephyr.reporting.prediction_log_writer import (
    ensure_prediction_log_table,
    query_predictions,
)

TRADE_DATE = "2026-08-21"
PREV_DATE = "2026-08-20"


# ══════════════════════════════════════════════════════════════
# 构造辅助
# ══════════════════════════════════════════════════════════════


def _plan(final_scenario: str = "HIGH_OPEN_REAL_UP", confidence: float = 1.0) -> ScenarioPlan:
    return ScenarioPlan(
        date=TRADE_DATE,
        three_scenarios=[],
        auction_verification=None,
        final_scenario=final_scenario,
        confidence_scale=confidence,
        degraded=False,
        reasons=["测试预案"],
        trace={"channels": {}},
    )


@pytest.fixture
def tmp_db(tmp_path: Path) -> Path:
    db = tmp_path / "governance.db"
    ensure_prediction_log_table(db)
    return db


def _index_tsv(rows: list[tuple]) -> str:
    """指数日线行：(trade_date, open, close)。"""
    return "\n".join("\t".join(str(c) for c in row) for row in rows)


def _etf_minute_tsv(amt_sum: float, vol_sum: float, last_close: float, n: int) -> str:
    """ETF 分钟聚合行：(amt_sum, vol_sum, last_close, n)。"""
    return f"{amt_sum}\t{vol_sum}\t{last_close}\t{n}"


def _make_ch(index_tsv: str = "", etf_tsv: str = "", raise_on: str | None = None):
    """路由式假 CH 客户端：按表名标记分派；raise_on 指定通道抛异常。"""

    def _ch(sql: str) -> str:
        if "kline_etf_1min" in sql:
            if raise_on == "etf":
                raise RuntimeError("etf boom")
            return etf_tsv
        if "kline_index" in sql:
            if raise_on == "index":
                raise RuntimeError("index boom")
            return index_tsv
        return ""

    return _ch


def _rising_etf_rows() -> str:
    """30 根上行分钟线聚合：vwap≈4.05，末收 4.100 → trend≈+1.2%（高走）。"""
    vol_sum = 30 * 10000.0
    amt_sum = 30 * 10000.0 * 4.05
    return _etf_minute_tsv(amt_sum, vol_sum, 4.100, 30)


def _falling_etf_rows() -> str:
    """30 根下行分钟线聚合：vwap≈4.05，末收 4.000 → trend≈-1.2%（低走）。"""
    vol_sum = 30 * 10000.0
    amt_sum = 30 * 10000.0 * 4.05
    return _etf_minute_tsv(amt_sum, vol_sum, 4.000, 30)


# ══════════════════════════════════════════════════════════════
# determine_actual_scenario 纯函数：9 格映射
# ══════════════════════════════════════════════════════════════


class TestDetermineActualScenario:
    @pytest.mark.parametrize(
        ("open_pct", "trend_pct", "expected"),
        [
            (0.025, 0.01, "HIGH_OPEN_REAL_UP"),
            (0.02, 0.002, "HIGH_OPEN_REAL_UP"),  # 开盘桶边界含等号
            (0.03, -0.01, "HIGH_OPEN_FAKE_UP"),
            (0.025, 0.0, "HIGH_OPEN_WASH"),
            (-0.025, -0.01, "LOW_OPEN_REAL_DOWN"),
            (-0.03, 0.01, "LOW_OPEN_FAKE_DOWN"),
            (-0.025, 0.0005, "LOW_OPEN_WASH"),
            (0.005, 0.01, "FLAT_OPEN_REAL_UP"),
            (-0.005, -0.01, "FLAT_OPEN_REAL_DOWN"),
            (0.0, 0.0, "FLAT_OPEN_WASH"),
        ],
    )
    def test_grid_mapping(self, open_pct: float, trend_pct: float, expected: str) -> None:
        assert determine_actual_scenario(open_pct, trend_pct) == expected
        assert expected in SCENARIO_LIST

    def test_trend_tolerance_boundary(self) -> None:
        # 容忍带内（含等值）=平走；严格超带=方向
        assert determine_actual_scenario(0.0, 0.0009) == "FLAT_OPEN_WASH"
        assert determine_actual_scenario(0.0, 0.001) == "FLAT_OPEN_WASH"
        assert determine_actual_scenario(0.0, 0.0011) == "FLAT_OPEN_REAL_UP"

    def test_custom_thresholds(self) -> None:
        assert determine_actual_scenario(0.015, 0.01, open_threshold=0.01) == "HIGH_OPEN_REAL_UP"

    def test_invalid_input_fail_closed(self) -> None:
        with pytest.raises(ValueError):
            determine_actual_scenario(None, 0.01)  # type: ignore[arg-type]
        with pytest.raises(ValueError):
            determine_actual_scenario(0.01, float("nan"))
        with pytest.raises(ValueError):
            determine_actual_scenario(0.01, 0.01, open_threshold=-0.02)
        with pytest.raises(ValueError):
            determine_actual_scenario(0.01, 0.01, trend_tolerance=-0.1)


# ══════════════════════════════════════════════════════════════
# record_plan 落库
# ══════════════════════════════════════════════════════════════


class TestRecordPlan:
    def test_write_and_query(self, tmp_db: Path) -> None:
        row_id = record_scenario_plan(_plan(), db_path=tmp_db)
        assert row_id > 0
        rows = query_predictions(
            trade_date=TRADE_DATE,
            module=MODULE_LOG_NAME,
            prediction_type=PREDICTION_TYPE_SCENARIO_PLAN,
            db_path=tmp_db,
        )
        assert len(rows) == 1
        payload = json.loads(rows[0]["payload_json"])
        assert payload["final_scenario"] == "HIGH_OPEN_REAL_UP"
        assert payload["confidence_scale"] == 1.0

    def test_idempotent_same_plan(self, tmp_db: Path) -> None:
        rid1 = record_scenario_plan(_plan(), db_path=tmp_db)
        rid2 = record_scenario_plan(_plan(), db_path=tmp_db)
        assert rid1 == rid2
        rows = query_predictions(module=MODULE_LOG_NAME, db_path=tmp_db)
        assert len(rows) == 1

    def test_distinct_plans_distinct_rows(self, tmp_db: Path) -> None:
        rid1 = record_scenario_plan(_plan("HIGH_OPEN_REAL_UP"), db_path=tmp_db)
        rid2 = record_scenario_plan(_plan("LOW_OPEN_WASH"), db_path=tmp_db)
        assert rid1 != rid2

    def test_missing_table_fail_open(self, tmp_path: Path) -> None:
        empty_db = tmp_path / "no_table.db"  # 不建表
        row_id = record_scenario_plan(_plan(), db_path=empty_db)
        assert row_id == -1  # fail-open：不抛

    def test_invalid_plan_fail_closed(self, tmp_db: Path) -> None:
        with pytest.raises(ValueError):
            record_scenario_plan({"not": "a plan"}, db_path=tmp_db)  # type: ignore[arg-type]

    def test_compute_and_record_composition(self, tmp_db: Path) -> None:
        ch = _make_ch()  # 全空 → scenario_planner 内部降级不炸
        plan, row_id = compute_and_record_scenario_plan(
            TRADE_DATE,
            ch_client=ch,
            db_path=tmp_db,
        )
        assert isinstance(plan, ScenarioPlan)
        assert row_id > 0


# ══════════════════════════════════════════════════════════════
# writeback_outcome 回写链路
# ══════════════════════════════════════════════════════════════


class TestWritebackOutcome:
    def _seed_prediction(self, db: Path, final_scenario: str = "HIGH_OPEN_REAL_UP") -> None:
        record_scenario_plan(_plan(final_scenario), db_path=db)

    def test_no_prediction_skipped(self, tmp_db: Path) -> None:
        verdict = writeback_scenario_outcome(TRADE_DATE, ch_client=_make_ch(), db_path=tmp_db)
        assert verdict.status == "skipped:no_prediction"
        assert verdict.hit is None
        assert verdict.outcome_row_id is None

    def test_hit_writeback_ok(self, tmp_db: Path) -> None:
        self._seed_prediction(tmp_db, "HIGH_OPEN_REAL_UP")
        ch = _make_ch(
            index_tsv=_index_tsv([(TRADE_DATE, 3900.0, 3890.0), (PREV_DATE, 3810.0, 3800.0)]),
            etf_tsv=_rising_etf_rows(),
        )
        verdict = writeback_scenario_outcome(TRADE_DATE, ch_client=ch, db_path=tmp_db)
        assert verdict.status == "ok"
        assert verdict.hit is True
        assert verdict.predicted_scenario == "HIGH_OPEN_REAL_UP"
        assert verdict.actual_scenario == "HIGH_OPEN_REAL_UP"
        assert verdict.trend_source == "kline_etf_1min"
        assert verdict.outcome_row_id is not None and verdict.outcome_row_id > 0
        # open_pct = (3900-3800)/3800 ≈ +2.63%
        assert verdict.open_pct == pytest.approx(100.0 / 3800.0, rel=1e-6)

        rows = query_predictions(
            trade_date=TRADE_DATE,
            module=MODULE_LOG_NAME,
            prediction_type="outcome",
            db_path=tmp_db,
        )
        assert len(rows) == 1
        payload = json.loads(rows[0]["payload_json"])
        assert payload["hit"] is True
        assert payload["dimension"] == DIMENSION_PREDICTION
        assert payload["scenario"] == "HIGH_OPEN_REAL_UP"
        assert payload["actual_scenario"] == "HIGH_OPEN_REAL_UP"
        assert payload["signal_source"] == SIGNAL_SOURCE
        assert payload["predicted_confidence"] == 1.0

    def test_miss_writeback(self, tmp_db: Path) -> None:
        self._seed_prediction(tmp_db, "HIGH_OPEN_REAL_UP")
        ch = _make_ch(
            index_tsv=_index_tsv([(TRADE_DATE, 3700.0, 3650.0), (PREV_DATE, 3810.0, 3800.0)]),
            etf_tsv=_falling_etf_rows(),
        )
        verdict = writeback_scenario_outcome(TRADE_DATE, ch_client=ch, db_path=tmp_db)
        assert verdict.status == "ok"
        assert verdict.hit is False
        assert verdict.actual_scenario == "LOW_OPEN_REAL_DOWN"

    def test_minute_missing_daily_proxy(self, tmp_db: Path) -> None:
        self._seed_prediction(tmp_db, "HIGH_OPEN_REAL_UP")
        # 指数日线：开 3900 收 3920（日内上行）→ daily_proxy 趋势=高走
        ch = _make_ch(
            index_tsv=_index_tsv([(TRADE_DATE, 3900.0, 3920.0), (PREV_DATE, 3810.0, 3800.0)]),
            etf_tsv="",
        )
        verdict = writeback_scenario_outcome(TRADE_DATE, ch_client=ch, db_path=tmp_db)
        assert verdict.status == "ok"
        assert verdict.trend_source == "daily_proxy"
        assert verdict.actual_scenario == "HIGH_OPEN_REAL_UP"
        assert verdict.hit is True

    def test_minute_missing_proxy_disabled_skips(self, tmp_db: Path) -> None:
        self._seed_prediction(tmp_db)
        cfg = ScenarioRecorderConfig(allow_daily_proxy=False)
        ch = _make_ch(
            index_tsv=_index_tsv([(TRADE_DATE, 3900.0, 3890.0), (PREV_DATE, 3810.0, 3800.0)]),
            etf_tsv="",
        )
        verdict = writeback_scenario_outcome(
            TRADE_DATE,
            ch_client=ch,
            db_path=tmp_db,
            config=cfg,
        )
        assert verdict.status == "skipped:no_trend_data"
        rows = query_predictions(
            trade_date=TRADE_DATE,
            module=MODULE_LOG_NAME,
            prediction_type="outcome",
            db_path=tmp_db,
        )
        assert rows == []

    def test_open_data_missing_skipped(self, tmp_db: Path) -> None:
        self._seed_prediction(tmp_db)
        verdict = writeback_scenario_outcome(TRADE_DATE, ch_client=_make_ch(), db_path=tmp_db)
        assert verdict.status == "skipped:no_open_data"
        assert verdict.hit is None

    def test_ch_error_fail_open(self, tmp_db: Path) -> None:
        self._seed_prediction(tmp_db)
        ch = _make_ch(raise_on="index")
        # CH 通道异常 fail-open：降级为空数据→skipped，不外抛
        verdict = writeback_scenario_outcome(TRADE_DATE, ch_client=ch, db_path=tmp_db)
        assert verdict.status == "skipped:no_open_data"
        assert verdict.hit is None

    def test_writeback_idempotent(self, tmp_db: Path) -> None:
        self._seed_prediction(tmp_db, "HIGH_OPEN_REAL_UP")
        ch = _make_ch(
            index_tsv=_index_tsv([(TRADE_DATE, 3900.0, 3890.0), (PREV_DATE, 3810.0, 3800.0)]),
            etf_tsv=_rising_etf_rows(),
        )
        v1 = writeback_scenario_outcome(TRADE_DATE, ch_client=ch, db_path=tmp_db)
        v2 = writeback_scenario_outcome(TRADE_DATE, ch_client=ch, db_path=tmp_db)
        assert v1.outcome_row_id == v2.outcome_row_id
        rows = query_predictions(
            trade_date=TRADE_DATE,
            module=MODULE_LOG_NAME,
            prediction_type="outcome",
            db_path=tmp_db,
        )
        assert len(rows) == 1

    def test_recorder_class_injection(self, tmp_db: Path) -> None:
        recorder = ScenarioPlanRecorder(ch_client=_make_ch(), db_path=tmp_db)
        rid = recorder.record_plan(_plan())
        assert rid > 0
        verdict = recorder.writeback_outcome(TRADE_DATE)
        # 无指数数据 → skipped:no_open_data（注入的空 ch 生效）
        assert verdict.status == "skipped:no_open_data"

    def test_invalid_trade_date_fail_closed(self, tmp_db: Path) -> None:
        with pytest.raises(ValueError):
            writeback_scenario_outcome("2026-13-99", ch_client=_make_ch(), db_path=tmp_db)
