# [TTL] task_bound
# [STARTUP] test_collected
# [CONSUMERS] pytest（波 3.2 假绿灯交叉尺红证；CI 侧由 check_wave3_rulers.py --counterfactual 同判据把守）
# [MODULE] tests.governance.data_supply.test_false_green_crosscheck
# [A_module] module_id=TST-GOV-DS-FG | layer=test | stability=evolving | safety=L | ai_autonomy=ai_modifiable
"""3.2 假绿灯交叉尺的判据测试——含 Z-16 要求的反事实控制组。

判据原文（10_wave_plan.md 波 3.2）："自带反事实控制组：喂一行假 SUCCESS 到台账但
目标表不动 ⇒ 尺必须红"。这里同时钉住反面（表随回执动 ⇒ 尺必须绿），
否则"永远喊红"的尺同样是装饰件。
"""

from __future__ import annotations

import datetime as dt

import pytest

from scripts.governance.data_supply import false_green_crosscheck as fg
from scripts.governance.data_supply.strict_truth_reader import StrictTruthReader, TruthReadError
from scripts.governance.data_supply.supply_sources import DataSupplyTaskSpec, LedgerRun, SentinelLeg

AS_OF = dt.date(2026, 9, 25)
BIZ = AS_OF - dt.timedelta(days=1)
TABLE = "c3_fundamental.suspend_status"

SPECS = {
    "suspend_derive": DataSupplyTaskSpec("suspend_derive", TABLE, "trade_date", ()),
    "downstream_consumer": DataSupplyTaskSpec(
        "downstream_consumer", "c3_fundamental.derived_x", "trade_date", ("suspend_derive",)
    ),
}
LEGS = {TABLE: [SentinelLeg(TABLE, "trade_date", 5)]}
DOWNSTREAM = {"suspend_derive": ("downstream_consumer",)}


def _run(rows_written: int = 120, status: str = "SUCCESS") -> LedgerRun:
    lo = dt.datetime.combine(BIZ, dt.time(1, 0), tzinfo=dt.timezone.utc)
    hi = dt.datetime.combine(BIZ, dt.time(1, 5), tzinfo=dt.timezone.utc)
    return LedgerRun(1, "suspend_derive", status, lo, hi, rows_written, rows_written)


def _reader(rows_on_biz: int, latest: dt.date | None):
    def _projection(sql: str):
        if "max(" in sql:
            return ((latest,),)
        return () if rows_on_biz == 0 else ((BIZ, rows_on_biz),)

    return StrictTruthReader(projection=_projection)


def _codes(verdict: fg.CrosscheckVerdict) -> set[str]:
    return {f.code for f in verdict.red}


def test_control_group_untouched_table_must_redden():
    """反事实控制组：假 SUCCESS + 表不动 ⇒ 必红（FAKE_GREEN）。"""
    verdict = fg.evaluate([_run()], SPECS, LEGS, _reader(0, None), as_of=AS_OF, downstream=DOWNSTREAM)
    assert "FAKE_GREEN" in _codes(verdict)
    assert not verdict.ok


def test_control_group_names_downstream_for_downgrade():
    """不符报红并**降级下游**（Z-16 原文）：下游任务/表须被点名。"""
    verdict = fg.evaluate([_run()], SPECS, LEGS, _reader(0, None), as_of=AS_OF, downstream=DOWNSTREAM)
    assert verdict.offending_tasks == ("suspend_derive",)
    assert verdict.downgraded_tasks == ("downstream_consumer",)
    assert "c3_fundamental.derived_x" in verdict.downgraded_tables


def test_positive_control_moving_table_stays_green():
    """正控制：回执 120 行、表侧同业务日确到 120 行 ⇒ 尺必须绿。"""
    verdict = fg.evaluate([_run()], SPECS, LEGS, _reader(120, BIZ), as_of=AS_OF, downstream=DOWNSTREAM)
    assert verdict.ok, verdict.findings


def test_partial_evaporation_is_red():
    verdict = fg.evaluate([_run()], SPECS, LEGS, _reader(30, BIZ), as_of=AS_OF, downstream=DOWNSTREAM)
    assert "RECEIPT_OVERSTATES" in _codes(verdict)


def test_stale_latest_business_date_behind_receipt_is_red():
    """回执 SUCCESS 但最新业务日落后声明阈值 ⇒ 红（新鲜度取业务表 max(date)，不用 system. 面）。"""
    verdict = fg.evaluate(
        [_run()], SPECS, LEGS, _reader(120, AS_OF - dt.timedelta(days=40)), as_of=AS_OF, downstream=DOWNSTREAM
    )
    assert "STALE_BEHIND_RECEIPT" in _codes(verdict)


def test_empty_ledger_window_is_red_not_green():
    """零回执不得被判"无违规即绿"。"""
    verdict = fg.evaluate([], SPECS, LEGS, _reader(1, BIZ), as_of=AS_OF, downstream=DOWNSTREAM)
    assert _codes(verdict) == {"EMPTY_LEDGER"}


def test_unknown_task_receipt_is_red():
    verdict = fg.evaluate(
        [
            LedgerRun(
                2, "ghost_task", "SUCCESS", None, dt.datetime.combine(BIZ, dt.time(3), tzinfo=dt.timezone.utc), 5, 5
            )
        ],
        SPECS,
        LEGS,
        _reader(1, BIZ),
        as_of=AS_OF,
        downstream=DOWNSTREAM,
    )
    assert "UNKNOWN_TASK" in _codes(verdict)


def test_truth_read_failure_propagates_instead_of_faking_zero():
    """W-180 红线：读数失败必抛，禁把失败洗成"真 0 行"从而判 FAKE_GREEN 之外的绿。"""

    def _boom(sql: str):
        raise RuntimeError("connection refused")

    with pytest.raises(TruthReadError):
        fg.evaluate([_run()], SPECS, LEGS, StrictTruthReader(projection=_boom), as_of=AS_OF, downstream=DOWNSTREAM)


def test_counterfactual_helper_reports_both_controls():
    ctrl = fg.run_counterfactual(AS_OF)
    assert ctrl.reddened and ctrl.greened and ctrl.passed
    assert ctrl.downgraded_tasks == ("downstream_consumer",)
