# [A_test] module_id: MOD-L00-004_internal_compute_provider | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md | §test
# [MODULE] tests.data.test_internal_compute_provider_cohort_daily
# [DEPENDENCIES]
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme;零DB零时钟（fake 注入隔离全部 IO，禁触生产 CH）;反串台断言不得弱化（技术指标默认分支必须零命中）
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass, non-zero on fail
# [TESTS] tests/data/test_internal_compute_provider_cohort_daily.py
# [TTL] task_bound
"""cohort_daily_ledger 调度路由测试（TC-08 步骤3/WORK-ORDER-5 接线收口）。

覆盖（全 fake IO / 零 DB / 零时钟）：
- 路由分派：payload.extra["capability"]=cohort_daily_ledger 命中 _fetch_cohort_daily，
  **绝不**落入 _fetch_technical_indicator 默认分支（反串台锁，daban_load 同一把尺子）
- 逐交易日驱动：_trade_days_guarded 周末守卫后逐日调 build_cohort_daily
- 行元组对齐：dict 行按 schemas INSERT_COLUMNS 序转元组（列序即 insert 契约）
- 整日构建异常 fail-visible：FetchResult.error 非空且 rows=[]，不伪造空成功
"""

from __future__ import annotations

import datetime as dt

import pytest

import zephyr.alt_data.cohort_daily_ledger as cdl
import zephyr.data.implementations.internal_compute_provider as icp
from schemas.categories.cohort_daily_ledger import INSERT_COLUMNS
from zephyr.data.provider_base import FetchPayload

_TBL = icp._TBL_COHORT_DAILY_LEDGER
_FAKE_REC = {
    "trade_date": "2026-09-15",
    "cohort_id": "retail",
    "metric_id": "discount_rate_avg",
    "metric_value": 0.1,
    "state": "ok",
    "proxy_source": "test",
    "bias_note": "",
    "detail": "{}",
}


def _payload(start: dt.date, end: dt.date) -> FetchPayload:
    return FetchPayload(
        table=_TBL,
        symbols=None,
        start=start,
        end=end,
        incremental=True,
        extra={"capability": "cohort_daily_ledger"},
    )


def test_route_dispatch_never_falls_through_to_indicator(monkeypatch):
    """cohort 请求绝不可落入技术指标默认分支——串台即静默污染指标表。"""

    def _boom(*a, **kw):
        raise AssertionError("落入 _fetch_technical_indicator：cohort_daily_ledger 路由失效")

    monkeypatch.setattr(icp.InternalComputeProvider, "_fetch_technical_indicator", _boom)
    monkeypatch.setattr(
        icp.InternalComputeProvider,
        "_trade_days_guarded",
        staticmethod(lambda start, end: []),
    )
    prov = icp.InternalComputeProvider()
    results = list(prov.fetch(_payload(dt.date(2026, 9, 14), dt.date(2026, 9, 16)), None))
    assert len(results) == 1 and results[0].rows == []


def test_route_builds_per_trading_day_and_aligns_columns(monkeypatch):
    """交易日守卫后逐日驱动 builder，行元组严格按 INSERT_COLUMNS 序。"""
    days = [dt.date(2026, 9, 15)]
    built: list[str] = []
    monkeypatch.setattr(
        icp.InternalComputeProvider,
        "_trade_days_guarded",
        staticmethod(lambda start, end: list(days)),
    )

    def _fake_build(day, reader=None):
        built.append(day)
        return [dict(_FAKE_REC)]

    monkeypatch.setattr(cdl, "build_cohort_daily", _fake_build)
    prov = icp.InternalComputeProvider()
    results = list(prov.fetch(_payload(dt.date(2026, 9, 14), dt.date(2026, 9, 16)), None))
    assert built == ["2026-09-15"]
    assert len(results) == 1
    res = results[0]
    assert res.table == _TBL
    assert res.columns == [c.strip() for c in INSERT_COLUMNS.strip("()").split(",")]
    assert len(res.rows) == 1
    assert res.rows[0][0] == "2026-09-15" and res.rows[0][1] == "retail"
    assert res.error is None and res.last_key == "2026-09-16"


def test_builder_failure_is_fail_visible(monkeypatch):
    """整日构建异常必须写 error 且 rows=[]——禁吞成空成功（daban CH 不可达同款契约）。"""
    monkeypatch.setattr(
        icp.InternalComputeProvider,
        "_trade_days_guarded",
        staticmethod(lambda start, end: [dt.date(2026, 9, 15)]),
    )

    def _boom(day, reader=None):
        raise RuntimeError("CH 不可达")

    monkeypatch.setattr(cdl, "build_cohort_daily", _boom)
    prov = icp.InternalComputeProvider()
    results = list(prov.fetch(_payload(dt.date(2026, 9, 15), dt.date(2026, 9, 15)), None))
    assert len(results) == 1
    res = results[0]
    assert res.rows == [] and res.error is not None and "RuntimeError" in res.error
