# [q0213-RESCUE] 本件字节捞回自 q-0213 死袋 blob sha256=e3aac2bba4072f70…（HEAD_MISSING 真孤儿，2026-09-29 车道 st-finaldel-crescue-20260929 落盘）。
# [TTL] task_bound
# [STARTUP] test_collected
# [CONSUMERS] pytest（波 3.3 供数守恒断言红证；CI 侧由 check_wave3_rulers.py --counterfactual 同判据把守）
# [MODULE] tests.governance.data_supply.test_supply_conservation
# [A_module] module_id=TST-GOV-DS-CONS | layer=test | stability=evolving | safety=L | ai_autonomy=ai_modifiable
"""3.3 供数守恒断言测试（EV-03 的病与药搬到数据链）+ 反事实控制组。

守恒式：声明供货日集合 △ 实到供货日集合 必须被 known_data_gaps 已生效申报覆盖；
交集上行数差值不得为负（负＝蒸发）。
"""

from __future__ import annotations

import datetime as dt

# [q0213-RESCUE] 适配：被测生产件 scripts/governance/data_supply/*（supply_conservation/strict_truth_reader/supply_sources）尚未落 HEAD，模块级 importorskip 防收集炸弹，生产件落库后自动恢复实跑
import pytest  # [q0213-RESCUE] 捞回适配新增：原件未顶层导入 pytest，守卫需要

pytest.importorskip("scripts.governance.data_supply.supply_conservation")
pytest.importorskip("scripts.governance.data_supply.strict_truth_reader")
pytest.importorskip("scripts.governance.data_supply.supply_sources")

from scripts.governance.data_supply.strict_truth_reader import StrictTruthReader
from scripts.governance.data_supply.supply_sources import DataSupplyTaskSpec, LedgerRun, SentinelLeg

from scripts.governance.data_supply import supply_conservation as sc

HI = dt.date(2026, 9, 25)
LO = HI - dt.timedelta(days=3)
BIZ = HI - dt.timedelta(days=1)
TABLE = "c1_market.etf_benchmark"

SPECS = {"etf_benchmark_build": DataSupplyTaskSpec("etf_benchmark_build", TABLE, "trade_date", ())}
LEGS = {TABLE: [SentinelLeg(TABLE, "trade_date", 10)]}
RUNS = [
    LedgerRun(
        1,
        "etf_benchmark_build",
        "SUCCESS",
        dt.datetime.combine(BIZ, dt.time(2), tzinfo=dt.timezone.utc),
        dt.datetime.combine(BIZ, dt.time(2, 9), tzinfo=dt.timezone.utc),
        77,
        77,
    )
]


def _reader(arrived: dict[dt.date, int], latest: dt.date | None = BIZ):
    rows = tuple(sorted(arrived.items()))

    def _projection(sql: str):
        if "max(" in sql:
            return ((latest,),)
        return tuple((d, n) for d, n in rows if n > 0)

    return StrictTruthReader(projection=_projection)


def _reds(reader, gaps=None, runs=None):
    reports = sc.evaluate(
        specs=SPECS,
        legs_by_table=LEGS,
        runs=list(RUNS if runs is None else runs),
        reader=reader,
        lo=LO,
        hi=HI,
        gap_index=dict(gaps or {}),
    )
    return reports, sc.red_findings(reports)


def test_control_group_declared_but_absent_must_redden():
    """反事实控制组：回执声明供数、仓库不动 ⇒ 守恒尺必须红（UNDECLARED_EVAPORATION）。"""
    _reports, reds = _reds(_reader({}, None))
    assert {f.code for f in reds} == {"UNDECLARED_EVAPORATION"}


def test_positive_control_conservation_holds_green():
    _reports, reds = _reds(_reader({BIZ: 77}))
    assert reds == []


def test_registered_effective_gap_downgrades_to_warning():
    """同一缺数，若已在 known_data_gaps 申报（status 生效）⇒ 不得再判红，降 WARN。"""
    gaps = {TABLE: [{"table": TABLE, "status": "accepted", "start_date": BIZ.isoformat(), "end_date": None}]}
    reports, reds = _reds(_reader({}, None), gaps)
    assert reds == []
    assert any(f.code == "GAP_DECLARED_MISSING_DAY" for f in reports[0].findings)


def test_completed_gap_does_not_excuse_current_window():
    """completed/resolved 的旧缺口不再背书（否则申报面变成永久放行）。"""
    gaps = {TABLE: [{"table": TABLE, "status": "completed", "start_date": BIZ.isoformat(), "end_date": HI.isoformat()}]}
    _reports, reds = _reds(_reader({}, None), gaps)
    assert {f.code for f in reds} == {"UNDECLARED_EVAPORATION"}


def test_partial_delivery_breaks_magnitude_conservation():
    _reports, reds = _reds(_reader({BIZ: 40}))
    assert {f.code for f in reds} == {"PARTIAL_DELIVERY"}


def test_arrival_without_receipt_is_warn_not_red():
    reports, reds = _reds(_reader({LO: 5}), runs=[])
    codes = {f.code for f in reports[0].findings}
    assert "UNDECLARED_ARRIVAL" in codes
    assert reds == []


def test_counterfactual_helper_reports_both_controls():
    ctrl = sc.run_counterfactual(HI)
    assert ctrl.reddened and ctrl.greened and ctrl.passed
