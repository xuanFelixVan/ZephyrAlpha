# [A_test] module_id: MOD-GOV-decision_chain_sentinel_test | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV | docs/_working/decision_map_campaign/links/L09_review/SKEL.md §四
# [MODULE] tests.governance.test_decision_chain_sentinel
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts/governance/decision_chain_sentinel.py（importlib 按路径加载, 同 test_audit_worktree_ops_telemetry.py 先例）
# [INVARIANTS] mock 连接三例（正常/滞后超限/DB 异常）+ 降级与边界例; 测试禁写生产路径（宪法§9.6）,
#   告警 jsonl 一律落 tmp_path fixture; 不触真实 DB（FakeExecutor 全注入）。
# [TESTS] self
# [A_module] module_id=MOD-GOV-decision_chain_sentinel_test | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""决策链哨兵单测——mock 连接三例（正常/滞后超限/DB 异常）+ 参照日取小/单腿降级/阈值边界。"""

from __future__ import annotations

import importlib.util
import json
from datetime import date
from pathlib import Path

import pytest

_SCRIPT_PATH = Path(__file__).resolve().parents[2] / "scripts" / "governance" / "decision_chain_sentinel.py"


def _load_module():
    """按路径加载哨兵脚本为模块（scripts/ 非包, 同族测试先例）。"""
    spec = importlib.util.spec_from_file_location("_decision_chain_sentinel_under_test", _SCRIPT_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class FakeExecutor:
    """CH 只读执行器替身：按 SQL 里的表名/谓词路由（与脚本 SQL 常量耦合=契约测试）。

    治尺后新增两腿：`min(cal_date)`=期望交易日腿（真源=日历, 故本替身由测试直接给 E）；
    `WHERE trade_date <= toDate(...)`=带上界的实评日腿（超前行被上界挡掉, 与裸 max 区分）。
    """

    def __init__(
        self,
        *,
        decision_max: date | None = None,
        decision_dates: list[date] | None = None,
        calendar_max: date | None = None,
        calendar_first_open: date | None = None,
        kline_max: date | None = None,
        open_days_after: int = 0,
        fail_predicate: str | None = None,
        fail_message: str = "connection refused",
    ):
        self.decision_max = decision_max
        self.decision_dates = decision_dates
        self.calendar_max = calendar_max
        self.calendar_first_open = calendar_first_open
        self.kline_max = kline_max
        self.open_days_after = open_days_after
        self.fail_predicate = fail_predicate
        self.fail_message = fail_message
        self.executed: list[str] = []

    def _pool(self) -> list[date]:
        if self.decision_dates is not None:
            return list(self.decision_dates)
        return [self.decision_max] if self.decision_max is not None else []

    def execute(self, sql: str) -> list:
        if self.fail_predicate and self.fail_predicate in sql:
            raise RuntimeError(self.fail_message)
        self.executed.append(sql)
        if "decision_daily" in sql:
            if "WHERE trade_date <= toDate(" in sql:  # 带上界实评日腿（_SQL_DECISION_MAX_DATE_NOT_AFTER）
                bound = date.fromisoformat(sql.split("WHERE trade_date <= toDate('")[1][:10])
                pool = [d for d in self._pool() if d <= bound]
                return [[max(pool) if pool else None]]
            return [[self.decision_max if self.decision_dates is None else max(self._pool())]]  # 裸 max（超前行可见性）
        if "kline_index" in sql:
            return [[self.kline_max]]
        if "min(cal_date)" in sql:  # 期望日腿（_SQL_CALENDAR_FIRST_OPEN_ON_OR_AFTER）——须先于 "cal_date >" 判
            return [[self.calendar_first_open if self.calendar_first_open is not None else self.calendar_max]]
        if "cal_date >" in sql:  # 开市日计数腿（_SQL_OPEN_DAYS_AFTER）
            return [[self.open_days_after]]
        return [[self.calendar_max]]  # 日历最近开市日腿（_SQL_CALENDAR_LAST_OPEN）


@pytest.fixture()
def sent():
    return _load_module()


# ============== 例 1：正常（滞后 < N）==============


def test_ok_below_threshold_no_alert_file(sent, tmp_path: Path):
    ex = FakeExecutor(
        decision_max=date(2026, 9, 24),
        calendar_max=date(2026, 9, 24),
        kline_max=date(2026, 9, 24),
        open_days_after=0,
    )
    alert_log = tmp_path / "decision_chain_alert.jsonl"
    record = sent.run_sentinel(ex, ref_date=date(2026, 9, 24), alert_log=alert_log)
    assert record["type"] == "ok"
    assert record["lag_trading_days"] == 0
    assert record["last_decision_date"] == "2026-09-24"
    assert record["reference_basis"] == "min_calendar_kline"
    assert not alert_log.exists(), "正常巡检禁写告警文件（jsonl 只收 alert/error 行）"


def test_ok_via_main_exit_zero(sent, tmp_path: Path, monkeypatch):
    ex = FakeExecutor(
        decision_max=date(2026, 9, 24),
        calendar_max=date(2026, 9, 24),
        kline_max=date(2026, 9, 24),
        open_days_after=0,
    )
    monkeypatch.setattr(sent, "_default_executor", lambda: ex)
    alert_log = tmp_path / "alert.jsonl"
    code = sent.main(
        [
            "--ref-date",
            "2026-09-24",
            "--alert-log",
            str(alert_log),
        ]
    )
    assert code == sent._EXIT_OK
    assert not alert_log.exists()


# ============== 例 2：滞后超限（>= N 即告警）==============


def test_lag_over_threshold_alerts(sent, tmp_path: Path):
    # last=09-16, 参照日=09-18, (09-16, 09-18] 开市日=09-17/09-18 共 2 日 >= N=2 → 告警
    ex = FakeExecutor(
        decision_max=date(2026, 9, 16),
        calendar_max=date(2026, 9, 18),
        kline_max=date(2026, 9, 18),
        open_days_after=2,
    )
    alert_log = tmp_path / "decision_chain_alert.jsonl"
    record = sent.run_sentinel(ex, ref_date=date(2026, 9, 18), alert_log=alert_log)
    assert record["type"] == "alert"
    assert record["lag_trading_days"] == 2
    assert record["lag_basis"] == "trading_days"
    assert "断供" in record["detail"] or "滞后" in record["detail"]
    lines = alert_log.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1, "告警恰好落一行 jsonl"
    persisted = json.loads(lines[0])
    assert persisted["type"] == "alert"
    assert persisted["last_decision_date"] == "2026-09-16"
    assert persisted["reference_day"] == "2026-09-18"
    assert persisted["threshold_lag_days"] == 2
    assert persisted["generated_at_utc"]  # RULE-SCHEMA-TZ 时间戳在案


def test_lag_over_threshold_main_exit_four(sent, tmp_path: Path, monkeypatch, caplog):
    ex = FakeExecutor(
        decision_max=date(2026, 9, 16),
        calendar_max=date(2026, 9, 18),
        kline_max=date(2026, 9, 18),
        open_days_after=2,
    )
    monkeypatch.setattr(sent, "_default_executor", lambda: ex)
    alert_log = tmp_path / "alert.jsonl"
    with caplog.at_level("WARNING"):
        code = sent.main(
            [
                "--ref-date",
                "2026-09-18",
                "--lag-days",
                "2",
                "--alert-log",
                str(alert_log),
            ]
        )
    assert code == sent._EXIT_ALERT == 4
    assert json.loads(alert_log.read_text(encoding="utf-8").strip())["type"] == "alert"


def test_lag_boundary_equals_threshold_alerts_below_passes(sent, tmp_path: Path):
    """--lag-days 阈值语义仍在位：日历"期望日腿"不可用而降级到参照日口径时，lag==N 鸣、lag<N 放行。

    主判据（期望日在位/缺行）不看阈值——"该有而没有"是当日无计划，压它=自毁哨兵；
    阈值继续管降级路径，故这里打挂 min(cal_date) 腿走参照日口径。
    """
    alert_log = tmp_path / "alert.jsonl"
    for open_days, expect_alert in ((2, True), (1, False)):
        ex = FakeExecutor(
            decision_max=date(2026, 9, 16),
            calendar_max=date(2026, 9, 18),
            kline_max=date(2026, 9, 18),
            open_days_after=open_days,
            fail_predicate="min(cal_date)",
        )
        record = sent.run_sentinel(ex, ref_date=date(2026, 9, 18), alert_log=alert_log)
        assert record["ruler"] == "reference_day_degraded", "期望日腿打挂必降级且留痕"
        assert record["expected_trade_date"] is None
        assert (record["type"] == "alert") is expect_alert, f"open_days={open_days}"
    assert len(alert_log.read_text(encoding="utf-8").strip().splitlines()) == 1


# ============== 例 3：DB 异常（fail-soft → error 记录 + exit 8，禁抛栈）==============


def test_db_error_fail_soft_exit_eight(sent, tmp_path: Path, monkeypatch):
    ex = FakeExecutor(fail_predicate="decision_daily", fail_message="connection refused")
    monkeypatch.setattr(sent, "_default_executor", lambda: ex)
    alert_log = tmp_path / "alert.jsonl"
    code = sent.main(
        [
            "--ref-date",
            "2026-09-24",
            "--alert-log",
            str(alert_log),
        ]
    )
    assert code == sent._EXIT_ERROR == 8
    persisted = json.loads(alert_log.read_text(encoding="utf-8").strip())
    assert persisted["type"] == "error"
    assert persisted["error_type"] == "RuntimeError"
    assert "connection refused" in persisted["error_message"]
    assert "\n" not in persisted["error_message"], "错误消息单行化（禁裸奔抛栈）"


def test_db_error_no_traceback_in_log(sent, tmp_path: Path, monkeypatch, caplog):
    ex = FakeExecutor(fail_predicate="kline_index")
    monkeypatch.setattr(sent, "_default_executor", lambda: ex)
    with caplog.at_level("ERROR"):
        code = sent.main(["--ref-date", "2026-09-24", "--alert-log", str(tmp_path / "alert.jsonl")])
    assert code == 8
    assert "Traceback" not in caplog.text
    assert "fail-soft" in caplog.text


# ============== 补充：断供形态 / 参照日取小 / 单腿降级 / 参数校验 ==============


def test_empty_decision_table_alerts_as_supply_break(sent, tmp_path: Path):
    ex = FakeExecutor(decision_max=None, calendar_max=date(2026, 9, 24), kline_max=date(2026, 9, 24))
    record = sent.run_sentinel(ex, ref_date=date(2026, 9, 24), alert_log=tmp_path / "alert.jsonl")
    assert record["type"] == "alert"
    assert record["last_decision_date"] is None
    assert record["lag_trading_days"] is None
    assert "全史零行" in record["detail"]


def test_reference_day_takes_min_of_calendar_and_kline(sent, tmp_path: Path):
    # 日历超前于数据面（T 早盘 kline 尚未落 T 日）→ 取小不虚计滞后
    ex = FakeExecutor(
        decision_max=date(2026, 9, 25),
        calendar_max=date(2026, 9, 25),
        kline_max=date(2026, 9, 24),
        open_days_after=0,
    )
    record = sent.run_sentinel(ex, ref_date=date(2026, 9, 25), alert_log=tmp_path / "alert.jsonl")
    assert record["reference_day"] == "2026-09-24"
    assert record["reference_basis"] == "min_calendar_kline"
    assert record["type"] == "ok", "决策行(生效日=T)领先参照日=健康"


def test_calendar_leg_degraded_falls_back_to_kline(sent, tmp_path: Path):
    ex = FakeExecutor(
        decision_max=date(2026, 9, 24),
        calendar_max=date(2026, 9, 24),
        kline_max=date(2026, 9, 24),
        fail_predicate="trade_calendar",
    )
    record = sent.run_sentinel(ex, ref_date=date(2026, 9, 24), alert_log=tmp_path / "alert.jsonl")
    assert record["calendar_day"] is None
    assert record["reference_basis"] == "kline_only"
    assert record["type"] == "ok"


def test_lag_count_degraded_uses_calendar_day_diff_basis(sent, tmp_path: Path):
    # lag 计数腿失败 → 降级日历日差（保守偏大口径, 记录里必须标注）
    ex = FakeExecutor(
        decision_max=date(2026, 9, 16),
        calendar_max=date(2026, 9, 18),
        kline_max=date(2026, 9, 18),
        open_days_after=0,
        fail_predicate="cal_date >",
    )
    record = sent.run_sentinel(ex, ref_date=date(2026, 9, 18), alert_log=tmp_path / "alert.jsonl")
    assert record["lag_trading_days"] == 2
    assert record["lag_basis"] == "calendar_days"
    assert record["type"] == "alert"


def test_both_reference_legs_dead_is_error_path(sent, tmp_path: Path, monkeypatch):
    ex = FakeExecutor(
        decision_max=date(2026, 9, 24),
        calendar_max=date(2026, 9, 24),
        kline_max=date(2026, 9, 24),
        fail_predicate="trade_calendar",
    )
    # kline 腿也死：把 kline 查询一并打挂（fail_predicate 单串不够, 用二次包装）
    origin = ex.execute

    def execute(sql):
        if "kline_index" in sql:
            raise RuntimeError("kline down")
        return origin(sql)

    ex.execute = execute
    monkeypatch.setattr(sent, "_default_executor", lambda: ex)
    code = sent.main(["--ref-date", "2026-09-24", "--alert-log", str(tmp_path / "alert.jsonl")])
    assert code == 8
    assert json.loads((tmp_path / "alert.jsonl").read_text(encoding="utf-8").strip())["type"] == "error"


def test_invalid_lag_days_config_error_exit_eight(sent, tmp_path: Path, monkeypatch):
    monkeypatch.setattr(sent, "_default_executor", lambda: FakeExecutor())
    alert_log = tmp_path / "alert.jsonl"
    code = sent.main(["--ref-date", "2026-09-24", "--lag-days", "0", "--alert-log", str(alert_log)])
    assert code == 8
    assert json.loads(alert_log.read_text(encoding="utf-8").strip())["error_type"] == "ValueError"


def test_table_names_resolved_from_true_sources(sent):
    """表名三真源零硬编码（DDL TABLE_NAME + TableRegistry 品类）。"""
    assert sent._TBL_DECISION_DAILY == "c1_backtest.decision_daily"
    assert sent._TBL_TRADE_CALENDAR == "c1_market.trade_calendar"
    assert sent._TBL_KLINE_INDEX == "c1_market.kline_index"


# ============== 治尺证尺（DAY §②）：旧 max 尺哑火 vs 新期望日尺报警 ==============


def _legacy_max_ruler(
    *,
    decision_dates: list[date],
    calendar_last_open: date,
    kline_max: date,
    threshold: int,
    open_days_after: int,
) -> tuple[str, int]:
    """治尺**前**判据的忠实复述（源=git HEAD 版 run_sentinel：last=裸 max(trade_date) 无上界、
    ref=min(日历最近开市日, kline max)、仅 ref>last 时才查缺勤）。

    只用于把"旧尺对跳日哑火"钉成回归事实，不参与生产判定（生产里不留旧尺副本=零第二真源）。
    """
    last = max(decision_dates) if decision_dates else None
    ref = min(calendar_last_open, kline_max)
    if last is None:
        return "alert", 0
    lag = open_days_after if ref > last else 0
    return ("alert" if lag >= threshold else "ok"), lag


def test_tail_skipped_trading_day_alerts_while_legacy_max_ruler_was_silent(sent, tmp_path: Path):
    """合成场景（交案形状）：日历说 09-25 开市，台账有 09-22/23/24 加超前的 09-28，独缺 09-25。

    新尺：期望日 09-25 缺行 ⇒ 报警（缺即告警，lag=1 记账）。
    旧尺：同一批事实 ⇒ max=09-28 > ref=09-24 ⇒ lag=0 报平安 —— 哑火实锤，本例即红证。
    """
    decision_dates = [
        date(2026, 9, 22),
        date(2026, 9, 23),
        date(2026, 9, 24),
        date(2026, 9, 28),  # 超前于期望日的行（合法形态：09-25 晨批产出次开市日 09-28）
    ]
    ex = FakeExecutor(
        decision_dates=decision_dates,
        calendar_max=date(2026, 9, 25),  # <=ref 的最近开市日
        calendar_first_open=date(2026, 9, 25),  # >=ref 的首个开市日 = 期望日 E
        kline_max=date(2026, 9, 24),
        open_days_after=1,
    )
    alert_log = tmp_path / "decision_chain_alert.jsonl"
    record = sent.run_sentinel(ex, ref_date=date(2026, 9, 25), alert_log=alert_log)

    assert record["ruler"] == "expected_open_day"
    assert record["expected_trade_date"] == "2026-09-25"
    assert record["type"] == "alert"
    assert record["lag_trading_days"] == 1
    assert record["lag_basis"] == "trading_days"
    assert record["last_decision_date"] == "2026-09-24", "带上界 ⇒ 09-28 超前行不参与判据"
    assert record["decision_max_unclamped"] == "2026-09-28"
    assert record["rows_beyond_axis"] is True
    assert "2026-09-25" in record["detail"]
    assert json.loads(alert_log.read_text(encoding="utf-8").strip())["type"] == "alert"

    assert _legacy_max_ruler(
        decision_dates=decision_dates,
        calendar_last_open=date(2026, 9, 25),
        kline_max=date(2026, 9, 24),
        threshold=2,
        open_days_after=1,
    ) == ("ok", 0), "旧尺在同一批事实上报平安=被掩盖，故此件必须报警"


def test_holiday_gap_expected_day_jumps_to_next_open_day_and_stays_green(sent, tmp_path: Path):
    """2026-09-25 实测形态（中秋休市）：期望日自动跳到次开市日 09-28 且行在 ⇒ 绿，不误鸣。

    钉两件事：①节假日口径由日历真源给出，不靠人肉判"今天是不是交易日"；
    ②上一轮"09-28=未来日异常"的误判不再可能——它是期望日本身，rows_beyond_axis=False。
    """
    ex = FakeExecutor(
        decision_dates=[
            date(2026, 9, 21),
            date(2026, 9, 22),
            date(2026, 9, 23),
            date(2026, 9, 24),
            date(2026, 9, 28),
        ],
        calendar_max=date(2026, 9, 24),
        calendar_first_open=date(2026, 9, 28),
        kline_max=date(2026, 9, 24),
        open_days_after=0,
    )
    alert_log = tmp_path / "alert.jsonl"
    record = sent.run_sentinel(ex, ref_date=date(2026, 9, 25), alert_log=alert_log)
    assert record["expected_trade_date"] == "2026-09-28"
    assert record["type"] == "ok"
    assert record["lag_trading_days"] == 0
    assert record["rows_beyond_axis"] is False
    assert not alert_log.exists(), "休市日跳档不得写告警行"


def test_expected_day_axis_comes_from_calendar_true_source(sent, tmp_path: Path):
    """期望日必须问日历真源（表名=TableRegistry 品类），且件内零节假日硬编码副本。"""
    ex = FakeExecutor(
        decision_dates=[date(2026, 9, 28)],
        calendar_max=date(2026, 9, 24),
        calendar_first_open=date(2026, 9, 28),
        kline_max=date(2026, 9, 24),
        open_days_after=0,
    )
    sent.run_sentinel(ex, ref_date=date(2026, 9, 25), alert_log=tmp_path / "alert.jsonl")
    axis_sql = [s for s in ex.executed if "min(cal_date)" in s]
    assert axis_sql, "期望日腿必须真问日历"
    assert sent._TBL_TRADE_CALENDAR in axis_sql[0]
    assert "is_open = 1" in axis_sql[0]
    for banned in ("_HOLIDAYS", "_HOLIDAY_DATES", "_CLOSED_DAYS", "holiday_list"):
        assert not hasattr(sent, banned), f"日历真源之外禁立第二份节假日真源: {banned}"
