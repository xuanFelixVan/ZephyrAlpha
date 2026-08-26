# [BLUEPRINT] MOD-SHARED-003 | docs/03_modules/_domain_shared/api_cost_governor/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-SHARED-003 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.shared.capacity_governance.test_api_cost_governor
# [TESTS] src/zephyr/shared/capacity_governance/api_cost_governor.py
"""MOD-SHARED-003 单元测试：api_cost_governor 外部API成本治理器。

蓝图验收（B1-00308/CAND-SHARED-001，C2 C-044）：
按源计量（成本单价表）+ 日/月预算注册与超预算自动降级标记 +
按预算剩余比例动态调速率的令牌桶（注入时钟）+ 全内存确定性。
时钟全注入可变替身，不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.shared.capacity_governance.api_cost_governor",
    reason="api_cost_governor not importable",
)

from zephyr.shared.capacity_governance.api_cost_governor import (  # noqa: E402
    ApiCostGovernor,
    ApiCostGovernorError,
    BudgetPeriod,
)

_T0 = datetime.datetime(2026, 8, 25, 9, 30, 0)


class _Clock:
    """可变注入时钟（测试替身）。"""

    def __init__(self, now: datetime.datetime = _T0) -> None:
        self.now = now

    def __call__(self) -> datetime.datetime:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += datetime.timedelta(seconds=seconds)


def _gov(clock: _Clock | None = None) -> ApiCostGovernor:
    return ApiCostGovernor(clock=clock or _Clock())


def _registered(gov: ApiCostGovernor, source: str = "tushare") -> ApiCostGovernor:
    gov.register_source(source, unit_cost=0.01, base_qps=10.0)
    return gov


# ──────────────────────────────────────────────────────────────────────────────
# 源注册
# ──────────────────────────────────────────────────────────────────────────────


class TestRegisterSource:
    def test_register_ok(self) -> None:
        gov = _registered(_gov())
        assert gov.sources() == ("tushare",)

    def test_register_invalid_params_raise(self) -> None:
        gov = _gov()
        with pytest.raises(ApiCostGovernorError):
            gov.register_source("", unit_cost=0.01, base_qps=10.0)   # 空 source_id
        with pytest.raises(ApiCostGovernorError):
            gov.register_source("s", unit_cost=-0.1, base_qps=10.0)  # 负单价
        with pytest.raises(ApiCostGovernorError):
            gov.register_source("s", unit_cost=0.01, base_qps=0.0)   # 非正基准QPS

    def test_register_same_params_idempotent(self) -> None:
        gov = _registered(_gov())
        gov.register_source("tushare", unit_cost=0.01, base_qps=10.0)  # 幂等不抛
        assert gov.sources() == ("tushare",)

    def test_register_conflicting_params_raises(self) -> None:
        gov = _registered(_gov())
        with pytest.raises(ApiCostGovernorError):
            gov.register_source("tushare", unit_cost=0.02, base_qps=10.0)


# ──────────────────────────────────────────────────────────────────────────────
# 预算注册
# ──────────────────────────────────────────────────────────────────────────────


class TestRegisterBudget:
    def test_register_daily_and_monthly(self) -> None:
        gov = _registered(_gov())
        gov.register_budget("tushare", BudgetPeriod.DAILY, 10.0)
        gov.register_budget("tushare", BudgetPeriod.MONTHLY, 200.0)
        budgets = gov.budget_of("tushare")
        assert budgets == {BudgetPeriod.DAILY: 10.0, BudgetPeriod.MONTHLY: 200.0}

    def test_register_budget_unknown_source_raises(self) -> None:
        with pytest.raises(ApiCostGovernorError):
            _gov().register_budget("ghost", BudgetPeriod.DAILY, 10.0)

    def test_register_budget_invalid_args_raise(self) -> None:
        gov = _registered(_gov())
        with pytest.raises(ApiCostGovernorError):
            gov.register_budget("tushare", BudgetPeriod.DAILY, 0.0)      # 非正限额
        with pytest.raises(ApiCostGovernorError):
            gov.register_budget("tushare", "weekly", 10.0)  # type: ignore[arg-type]  # 词表外周期

    def test_register_budget_duplicate_period_raises(self) -> None:
        gov = _registered(_gov())
        gov.register_budget("tushare", BudgetPeriod.DAILY, 10.0)
        with pytest.raises(ApiCostGovernorError):
            gov.register_budget("tushare", BudgetPeriod.DAILY, 20.0)


# ──────────────────────────────────────────────────────────────────────────────
# 计量与降级
# ──────────────────────────────────────────────────────────────────────────────


class TestRecordCall:
    def test_record_accumulates(self) -> None:
        gov = _registered(_gov())
        assert gov.record_call("tushare") is False
        gov.record_call("tushare", units=4)
        usage = gov.usage("tushare")
        assert usage.total_calls == 5
        assert usage.total_cost == pytest.approx(0.05)
        assert usage.degraded is False

    def test_record_invalid_args_raise(self) -> None:
        gov = _registered(_gov())
        with pytest.raises(ApiCostGovernorError):
            gov.record_call("ghost")                       # 未注册源
        with pytest.raises(ApiCostGovernorError):
            gov.record_call("tushare", units=0)            # 非正计量单位

    def test_period_costs_keyed_by_day_and_month(self) -> None:
        clock = _Clock()
        gov = _registered(_gov(clock))
        gov.register_budget("tushare", BudgetPeriod.DAILY, 100.0)
        gov.register_budget("tushare", BudgetPeriod.MONTHLY, 1000.0)
        gov.record_call("tushare", units=10)  # 成本 0.10
        usage = gov.usage("tushare")
        assert dict(usage.period_costs) == {"2026-08": 0.10, "2026-08-25": 0.10}

    def test_exceed_budget_auto_degrades(self) -> None:
        gov = _registered(_gov())
        gov.register_budget("tushare", BudgetPeriod.DAILY, 0.03)
        assert gov.record_call("tushare", units=3) is False  # 0.03 未超
        assert gov.record_call("tushare", units=1) is True   # 0.04 超预算
        assert gov.is_degraded("tushare") is True

    def test_degraded_is_sticky_within_period(self) -> None:
        clock = _Clock()
        gov = _registered(_gov(clock))
        gov.register_budget("tushare", BudgetPeriod.MONTHLY, 0.02)
        gov.record_call("tushare", units=3)  # 0.03 超月预算
        clock.advance(86400 * 3)             # 跨日不跨月
        assert gov.is_degraded("tushare") is True  # 月键未变，降级保持

    def test_period_key_rolls_on_new_day(self) -> None:
        clock = _Clock()
        gov = _registered(_gov(clock))
        gov.register_budget("tushare", BudgetPeriod.DAILY, 100.0)
        gov.record_call("tushare")
        clock.advance(86400)
        gov.record_call("tushare")
        keys = dict(gov.usage("tushare").period_costs)
        assert keys == {"2026-08-25": 0.01, "2026-08-26": 0.01}


# ──────────────────────────────────────────────────────────────────────────────
# 动态令牌桶
# ──────────────────────────────────────────────────────────────────────────────


class TestTokenBucket:
    def test_full_bucket_at_start(self) -> None:
        gov = _registered(_gov())
        view = gov.bucket_view("tushare")
        assert view.tokens == pytest.approx(10.0)
        assert view.capacity == pytest.approx(10.0)
        assert view.effective_rate == pytest.approx(10.0)  # 无预算=全额速率

    def test_acquire_consumes_tokens(self) -> None:
        gov = _registered(_gov())
        assert gov.try_acquire("tushare", tokens=6) is True
        assert gov.try_acquire("tushare", tokens=6) is False  # 剩 4 不够
        assert gov.bucket_view("tushare").tokens == pytest.approx(4.0)

    def test_refill_with_injected_clock(self) -> None:
        clock = _Clock()
        gov = _registered(_gov(clock))
        gov.try_acquire("tushare", tokens=10)  # 清空
        clock.advance(0.5)                     # 10 qps × 0.5s = 5 令牌
        assert gov.try_acquire("tushare", tokens=5) is True

    def test_rate_scales_with_remaining_budget(self) -> None:
        clock = _Clock()
        gov = _registered(_gov(clock))
        gov.register_budget("tushare", BudgetPeriod.DAILY, 0.10)
        gov.record_call("tushare", units=5)  # 用掉 0.05 → 剩余 50%
        view = gov.bucket_view("tushare")
        assert view.effective_rate == pytest.approx(5.0)  # 10 × 0.5

    def test_degraded_freezes_bucket(self) -> None:
        clock = _Clock()
        gov = _registered(_gov(clock))
        gov.register_budget("tushare", BudgetPeriod.DAILY, 0.01)
        gov.try_acquire("tushare", tokens=10)  # 清空
        gov.record_call("tushare", units=2)    # 0.02 超预算 → 降级
        clock.advance(10.0)
        assert gov.try_acquire("tushare", tokens=1) is False  # 速率 0 不补充
        assert gov.bucket_view("tushare").effective_rate == pytest.approx(0.0)

    def test_acquire_invalid_args_raise(self) -> None:
        gov = _registered(_gov())
        with pytest.raises(ApiCostGovernorError):
            gov.try_acquire("ghost")                   # 未注册源
        with pytest.raises(ApiCostGovernorError):
            gov.try_acquire("tushare", tokens=0)       # 非正令牌数

    def test_clock_rewind_raises(self) -> None:
        clock = _Clock()
        gov = _registered(_gov(clock))
        gov.try_acquire("tushare")
        clock.advance(-1.0)  # 回拨
        with pytest.raises(ApiCostGovernorError):
            gov.try_acquire("tushare")


# ──────────────────────────────────────────────────────────────────────────────
# 确定性
# ──────────────────────────────────────────────────────────────────────────────


class TestDeterminism:
    def test_same_inputs_same_outputs(self) -> None:
        def _run() -> tuple:
            clock = _Clock()
            gov = _registered(_gov(clock))
            gov.register_budget("tushare", BudgetPeriod.DAILY, 0.05)
            gov.record_call("tushare", units=3)
            gov.try_acquire("tushare", tokens=7)
            clock.advance(0.2)
            acquired = gov.try_acquire("tushare", tokens=4)
            usage = gov.usage("tushare")
            view = gov.bucket_view("tushare")
            return (acquired, usage, view)

        assert _run() == _run()

    def test_sources_sorted(self) -> None:
        gov = _gov()
        for name in ("sina", "akshare", "tushare"):
            gov.register_source(name, unit_cost=0.01, base_qps=5.0)
        assert gov.sources() == ("akshare", "sina", "tushare")
