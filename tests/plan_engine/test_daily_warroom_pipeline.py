# [A_test] module_id: MOD-PLAN-018 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-PLAN-018 | 待统筹登记 | 45号 §4 W0/W6 验证闭环 + 清单 P1-7 日常编排
# [MODULE] tests.plan_engine.test_daily_warroom_pipeline
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] testing
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

"""DailyWarroomPipeline (MOD-PLAN-018) 施工验证测试。

覆盖：
- resolve_next_trading_day：market_trade_calendar 次交易日解析（is_open=1/
  严格大于/LIMIT 1 口径）；无次交易日/通道异常 fail-open 返 None；非法日期
  fail-closed（错误消息不含 session_id）。
- 盘前段：target_date=次交易日 → compute_and_record 落 scenario_plan 族
  （trade_date=次交易日）；同日重跑幂等保首条（行数=1、row_id 相同）；
  无次交易日 skipped:no_next_trading_day；phase=premarket 不跑盘后段。
- 盘后段：writeback_scenario_outcome 回写（有预测行+mock 行情 → ok + outcome
  落库）；无预测行 skipped:no_prediction；同日重跑 outcome 幂等保首条。
- both 段：盘前+盘后一次跑通；phase/data_date 非法 fail-closed；
  结果契约 to_dict JSON 可序列化。
全 mock CH + tmp 库隔离，不触真 governance.db 与真 ClickHouse。
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from zephyr.plan_engine.daily_warroom_pipeline import (
    PHASE_BOTH,
    PHASE_POSTMARKET,
    PHASE_PREMARKET,
    DailyWarroomPipeline,
    DailyWarroomPipelineResult,
    resolve_next_trading_day,
    run_daily_warroom_pipeline,
)
from zephyr.plan_engine.scenario_plan_recorder import (
    MODULE_LOG_NAME,
    PREDICTION_TYPE_SCENARIO_PLAN,
)
from zephyr.reporting.prediction_log_writer import (
    ensure_prediction_log_table,
    query_predictions,
)

DATA_DATE = "2026-08-21"  # 数据日（周五）
NEXT_DATE = "2026-08-24"  # 次交易日（周一）


# ══════════════════════════════════════════════════════════════
# 构造辅助
# ══════════════════════════════════════════════════════════════


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


def _rising_etf_rows() -> str:
    """30 根上行分钟线聚合：vwap≈4.05，末收 4.100 → trend≈+1.2%（高走）。"""
    vol_sum = 30 * 10000.0
    amt_sum = 30 * 10000.0 * 4.05
    return _etf_minute_tsv(amt_sum, vol_sum, 4.100, 30)


def _make_ch(
    calendar_dates: list[str] | None = None,
    index_tsv: str = "",
    etf_tsv: str = "",
    raise_on: str | None = None,
    capture: list[str] | None = None,
):
    """路由式假 CH 客户端：按表名标记分派；raise_on 指定通道抛异常；capture 收集 SQL。"""

    def _ch(sql: str) -> str:
        if capture is not None:
            capture.append(sql)
        if "trade_calendar" in sql:
            if raise_on == "calendar":
                raise RuntimeError("calendar boom")
            return "\n".join(calendar_dates or [])
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


def _flat_index_tsv(trade_date: str = DATA_DATE) -> str:
    """平开+高走指数两日：open_pct≈0（平开）→ 配合高走 ETF 得 FLAT_OPEN_REAL_UP。"""
    return _index_tsv([(trade_date, 4000.0, 4010.0), ("2026-08-20", 3990.0, 4000.0)])


# ══════════════════════════════════════════════════════════════
# resolve_next_trading_day：次交易日解析
# ══════════════════════════════════════════════════════════════


class TestResolveNextTradingDay:
    def test_returns_next_open_day(self) -> None:
        ch = _make_ch(calendar_dates=[NEXT_DATE, "2026-08-25"])
        assert resolve_next_trading_day(DATA_DATE, ch_client=ch) == NEXT_DATE

    def test_sql_guards(self) -> None:
        """SQL 口径：is_open=1 过滤 + 严格大于数据日 + LIMIT 1（防全表扫）。"""
        captured: list[str] = []
        ch = _make_ch(calendar_dates=[NEXT_DATE], capture=captured)
        resolve_next_trading_day(DATA_DATE, ch_client=ch)
        assert len(captured) == 1
        sql = captured[0]
        assert "is_open = 1" in sql
        assert f"cal_date > '{DATA_DATE}'" in sql
        assert "LIMIT 1" in sql

    def test_no_next_day_returns_none(self) -> None:
        ch = _make_ch(calendar_dates=[])
        assert resolve_next_trading_day(DATA_DATE, ch_client=ch) is None

    def test_channel_error_failopen(self) -> None:
        ch = _make_ch(raise_on="calendar")
        assert resolve_next_trading_day(DATA_DATE, ch_client=ch) is None

    def test_invalid_date_failclosed(self) -> None:
        with pytest.raises(ValueError, match="data_date"):
            resolve_next_trading_day("2026-13-01", ch_client=_make_ch())
        with pytest.raises(ValueError, match="data_date"):
            resolve_next_trading_day(20260821, ch_client=_make_ch())  # type: ignore[arg-type]

    def test_error_message_no_session_id(self) -> None:
        try:
            resolve_next_trading_day("not-a-date", ch_client=_make_ch())
        except ValueError as exc:
            assert "session_id" not in str(exc)
        else:  # pragma: no cover
            raise AssertionError("应抛 ValueError")


# ══════════════════════════════════════════════════════════════
# 盘前段：compute_and_record 编排
# ══════════════════════════════════════════════════════════════


class TestPremarketPhase:
    def test_ok_and_persist(self, tmp_db: Path) -> None:
        ch = _make_ch(calendar_dates=[NEXT_DATE])
        result = run_daily_warroom_pipeline(
            DATA_DATE, phase=PHASE_PREMARKET, ch_client=ch, db_path=tmp_db,
        )
        assert result.premarket_status == "ok"
        assert result.target_date == NEXT_DATE
        assert result.premarket_row_id is not None and result.premarket_row_id > 0
        # 落库实证：scenario_plan 族，trade_date=次交易日
        rows = query_predictions(
            trade_date=NEXT_DATE,
            module=MODULE_LOG_NAME,
            prediction_type=PREDICTION_TYPE_SCENARIO_PLAN,
            db_path=tmp_db,
        )
        assert len(rows) == 1
        payload = json.loads(rows[0]["payload_json"])
        assert payload["date"] == NEXT_DATE

    def test_idempotent_rerun(self, tmp_db: Path) -> None:
        """同日重跑幂等保首条：行数=1 且 row_id 相同（prediction_log UNIQUE 键）。"""
        ch = _make_ch(calendar_dates=[NEXT_DATE])
        r1 = run_daily_warroom_pipeline(
            DATA_DATE, phase=PHASE_PREMARKET, ch_client=ch, db_path=tmp_db,
        )
        r2 = run_daily_warroom_pipeline(
            DATA_DATE, phase=PHASE_PREMARKET, ch_client=ch, db_path=tmp_db,
        )
        assert r1.premarket_status == "ok" and r2.premarket_status == "ok"
        assert r1.premarket_row_id == r2.premarket_row_id
        rows = query_predictions(
            trade_date=NEXT_DATE,
            module=MODULE_LOG_NAME,
            prediction_type=PREDICTION_TYPE_SCENARIO_PLAN,
            db_path=tmp_db,
        )
        assert len(rows) == 1

    def test_no_next_trading_day_skips(self, tmp_db: Path) -> None:
        ch = _make_ch(calendar_dates=[])
        result = run_daily_warroom_pipeline(
            DATA_DATE, phase=PHASE_PREMARKET, ch_client=ch, db_path=tmp_db,
        )
        assert result.premarket_status == "skipped:no_next_trading_day"
        assert result.target_date is None
        assert result.premarket_row_id is None
        rows = query_predictions(
            module=MODULE_LOG_NAME,
            prediction_type=PREDICTION_TYPE_SCENARIO_PLAN,
            db_path=tmp_db,
        )
        assert rows == []

    def test_calendar_channel_error_skips(self, tmp_db: Path) -> None:
        ch = _make_ch(raise_on="calendar")
        result = run_daily_warroom_pipeline(
            DATA_DATE, phase=PHASE_PREMARKET, ch_client=ch, db_path=tmp_db,
        )
        assert result.premarket_status == "skipped:no_next_trading_day"

    def test_premarket_phase_skips_postmarket(self, tmp_db: Path) -> None:
        ch = _make_ch(calendar_dates=[NEXT_DATE])
        result = run_daily_warroom_pipeline(
            DATA_DATE, phase=PHASE_PREMARKET, ch_client=ch, db_path=tmp_db,
        )
        assert result.postmarket_status == "skipped:phase"
        assert result.outcome_verdict is None


# ══════════════════════════════════════════════════════════════
# 盘后段：writeback_scenario_outcome 编排
# ══════════════════════════════════════════════════════════════


class TestPostmarketPhase:
    def _seed_prediction(self, tmp_db: Path, trade_date: str = DATA_DATE) -> None:
        """造当日预测行（盘前段落库，供盘后段回写消费）。"""
        ch = _make_ch(calendar_dates=[trade_date])
        seeded = run_daily_warroom_pipeline(
            "2026-08-20", phase=PHASE_PREMARKET, ch_client=ch, db_path=tmp_db,
        )
        assert seeded.premarket_status == "ok"

    def test_ok_and_outcome_persist(self, tmp_db: Path) -> None:
        self._seed_prediction(tmp_db)
        ch = _make_ch(index_tsv=_flat_index_tsv(), etf_tsv=_rising_etf_rows())
        result = run_daily_warroom_pipeline(
            DATA_DATE, phase=PHASE_POSTMARKET, ch_client=ch, db_path=tmp_db,
        )
        assert result.postmarket_status == "ok"
        assert result.outcome_verdict is not None
        assert result.outcome_verdict.status == "ok"
        assert result.outcome_verdict.actual_scenario == "FLAT_OPEN_REAL_UP"
        # outcome 族落库实证
        outcomes = query_predictions(
            trade_date=DATA_DATE,
            module=MODULE_LOG_NAME,
            prediction_type="outcome",
            db_path=tmp_db,
        )
        assert len(outcomes) == 1
        payload = json.loads(outcomes[0]["payload_json"])
        assert payload["dimension"] == "prediction"
        assert payload["actual_scenario"] == "FLAT_OPEN_REAL_UP"

    def test_no_prediction_skips(self, tmp_db: Path) -> None:
        ch = _make_ch(index_tsv=_flat_index_tsv(), etf_tsv=_rising_etf_rows())
        result = run_daily_warroom_pipeline(
            DATA_DATE, phase=PHASE_POSTMARKET, ch_client=ch, db_path=tmp_db,
        )
        assert result.postmarket_status == "skipped:no_prediction"
        assert result.outcome_verdict is not None
        assert result.outcome_verdict.status == "skipped:no_prediction"

    def test_idempotent_rerun(self, tmp_db: Path) -> None:
        """同日重跑 outcome 幂等保首条（行数=1）。"""
        self._seed_prediction(tmp_db)
        ch = _make_ch(index_tsv=_flat_index_tsv(), etf_tsv=_rising_etf_rows())
        r1 = run_daily_warroom_pipeline(
            DATA_DATE, phase=PHASE_POSTMARKET, ch_client=ch, db_path=tmp_db,
        )
        r2 = run_daily_warroom_pipeline(
            DATA_DATE, phase=PHASE_POSTMARKET, ch_client=ch, db_path=tmp_db,
        )
        assert r1.postmarket_status == "ok" and r2.postmarket_status == "ok"
        assert (
            r1.outcome_verdict is not None
            and r2.outcome_verdict is not None
            and r1.outcome_verdict.outcome_row_id == r2.outcome_verdict.outcome_row_id
        )
        outcomes = query_predictions(
            trade_date=DATA_DATE,
            module=MODULE_LOG_NAME,
            prediction_type="outcome",
            db_path=tmp_db,
        )
        assert len(outcomes) == 1

    def test_postmarket_phase_skips_premarket(self, tmp_db: Path) -> None:
        ch = _make_ch()
        result = run_daily_warroom_pipeline(
            DATA_DATE, phase=PHASE_POSTMARKET, ch_client=ch, db_path=tmp_db,
        )
        assert result.premarket_status == "skipped:phase"
        assert result.target_date is None


# ══════════════════════════════════════════════════════════════
# both 段 + 编排留痕
# ══════════════════════════════════════════════════════════════


class TestBothPhase:
    def test_both_phases_run(self, tmp_db: Path) -> None:
        # 先造 data_date 当日预测行（供盘后段消费）
        seed_ch = _make_ch(calendar_dates=[DATA_DATE])
        run_daily_warroom_pipeline(
            "2026-08-20", phase=PHASE_PREMARKET, ch_client=seed_ch, db_path=tmp_db,
        )
        ch = _make_ch(
            calendar_dates=[NEXT_DATE],
            index_tsv=_flat_index_tsv(),
            etf_tsv=_rising_etf_rows(),
        )
        result = run_daily_warroom_pipeline(
            DATA_DATE, phase=PHASE_BOTH, ch_client=ch, db_path=tmp_db,
        )
        assert result.premarket_status == "ok"
        assert result.target_date == NEXT_DATE
        assert result.postmarket_status == "ok"
        assert result.outcome_verdict is not None
        # 两族各一行：scenario_plan(2026-08-21 + 2026-08-24) + outcome(2026-08-21)
        plans = query_predictions(
            module=MODULE_LOG_NAME,
            prediction_type=PREDICTION_TYPE_SCENARIO_PLAN,
            db_path=tmp_db,
        )
        outcomes = query_predictions(
            module=MODULE_LOG_NAME, prediction_type="outcome", db_path=tmp_db,
        )
        assert {r["trade_date"] for r in plans} == {DATA_DATE, NEXT_DATE}
        assert len(outcomes) == 1

    def test_default_phase_is_both(self, tmp_db: Path) -> None:
        ch = _make_ch(calendar_dates=[NEXT_DATE])
        result = run_daily_warroom_pipeline(DATA_DATE, ch_client=ch, db_path=tmp_db)
        assert result.phase == PHASE_BOTH

    def test_result_contract_json_serializable(self, tmp_db: Path) -> None:
        ch = _make_ch(calendar_dates=[NEXT_DATE])
        result = run_daily_warroom_pipeline(DATA_DATE, ch_client=ch, db_path=tmp_db)
        assert isinstance(result, DailyWarroomPipelineResult)
        json.dumps(result.to_dict())  # 不抛即契约满足
        d = result.to_dict()
        assert d["data_date"] == DATA_DATE
        assert d["target_date"] == NEXT_DATE


# ══════════════════════════════════════════════════════════════
# 输入校验（fail-closed）
# ══════════════════════════════════════════════════════════════


class TestValidation:
    def test_invalid_phase(self, tmp_db: Path) -> None:
        with pytest.raises(ValueError, match="phase"):
            run_daily_warroom_pipeline(
                DATA_DATE, phase="midday", ch_client=_make_ch(), db_path=tmp_db,
            )

    def test_invalid_data_date(self, tmp_db: Path) -> None:
        with pytest.raises(ValueError, match="data_date"):
            run_daily_warroom_pipeline(
                "2026-02-30", phase=PHASE_BOTH, ch_client=_make_ch(), db_path=tmp_db,
            )
        with pytest.raises(ValueError, match="data_date"):
            run_daily_warroom_pipeline(
                None, phase=PHASE_BOTH, ch_client=_make_ch(), db_path=tmp_db,  # type: ignore[arg-type]
            )

    def test_error_message_no_session_id(self, tmp_db: Path) -> None:
        for bad_kwargs in (
            {"data_date": "bad", "phase": PHASE_BOTH},
            {"data_date": DATA_DATE, "phase": "nope"},
        ):
            try:
                run_daily_warroom_pipeline(
                    ch_client=_make_ch(), db_path=tmp_db, **bad_kwargs,
                )
            except ValueError as exc:
                assert "session_id" not in str(exc)
            else:  # pragma: no cover
                raise AssertionError("应抛 ValueError")

    def test_pipeline_class_entry(self, tmp_db: Path) -> None:
        """类入口等价函数入口（编排器复用口径）。"""
        ch = _make_ch(calendar_dates=[NEXT_DATE])
        pipe = DailyWarroomPipeline(ch_client=ch, db_path=tmp_db)
        result = pipe.run(DATA_DATE, phase=PHASE_PREMARKET)
        assert result.premarket_status == "ok"
        assert pipe.resolve_next_trading_day(DATA_DATE) == NEXT_DATE
