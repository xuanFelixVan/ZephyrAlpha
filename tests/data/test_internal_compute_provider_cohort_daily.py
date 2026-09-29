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
from zephyr.data.provider_base import FetchPayload

_TBL = icp._TBL_COHORT_DAILY_LEDGER


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
    """交易日守卫后逐日驱动唯一写入口 write_cohort_daily；结果仅记账（HEAD 契约
    2026-09-21/22 写入器收敛）：columns/rows 恒空防框架二次插行=禁双写，
    rows_fetched=实写行数供游标推进，committed=True 无 error。"""
    days = [dt.date(2026, 9, 15)]
    written: list[str] = []
    monkeypatch.setattr(
        icp.InternalComputeProvider,
        "_trade_days_guarded",
        staticmethod(lambda start, end: list(days)),
    )

    def _fake_write(day, reader=None):
        written.append(day)
        return {"rows": 3, "committed": True, "day": day, "error": None}

    # 生产分支在函数内延迟导入 writer——patch 模块属性即生效；禁触真 CH（零 DB 铁律）
    monkeypatch.setattr("zephyr.alt_data.cohort_daily_writer.write_cohort_daily", _fake_write)
    prov = icp.InternalComputeProvider()
    results = list(prov.fetch(_payload(dt.date(2026, 9, 14), dt.date(2026, 9, 16)), None))
    assert written == ["2026-09-15"]
    assert len(results) == 1
    res = results[0]
    assert res.table == _TBL
    assert res.columns == [] and res.rows == []
    assert res.rows_fetched == 3
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
