# [A_test] module_id: SRC-TST-1944 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-561 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.shared.test_cost_budget
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
单元测试：src/zephyr/shared/cost_budget.py
============================================
覆盖矩阵：
  PricingTier：
    - 构造 & 属性 × 2
  CostBudget 初始化：
    - 默认值 × 2
    - 自定义 hard_limit / warning_ratio × 2
  CostBudget.set_pricing：
    - 注册定价 × 2
    - 覆盖已有定价 × 1
  CostBudget.get_cost：
    - 已知 provider/model cost × 2（含 cached input）
    - 未知 provider/model 返回 0.0 × 1
  CostBudget.assert_budget：
    - 预算内通过 × 1
    - 超出 hard_limit 抛 CostBudgetExceededError × 1
    - 刚好临界（>=）抛异常 × 1
  CostBudget.check_budget_or_warn：
    - 预算内无警告 × 1
    - 超出 warning_ratio 返回警告 × 1
    - 超出 hard_limit 抛异常 × 1
  CostBudget.record_usage：
    - 记录后累计 cost 增加 × 1
    - call_count 递增 × 1
    - 返回本次成本 × 1
  CostBudget 属性：
    - remaining × 2
    - usage_ratio × 2
  CostBudget.reset：
    - 重置清零 × 1
  CostBudgetExceededError：
    - 属性完整性 × 1
    - 消息格式 × 1
  线程安全：
    - 并发 record_usage × 1

Safety: HIGH（成本熔断是经济安全边界）
"""

import threading

import pytest

from zephyr.governance.ops_governance.cost_budget import (
    CostBudget,
    CostBudgetExceededError,
    PricingTier,
)


class TestPricingTier:
    def test_construction(self):
        tier = PricingTier(
            model="gpt-4o",
            input_price_per_1k=0.0025,
            output_price_per_1k=0.0100,
        )
        assert tier.model == "gpt-4o"
        assert tier.input_price_per_1k == 0.0025
        assert tier.output_price_per_1k == 0.0100
        assert tier.cached_input_price_per_1k is None

    def test_with_cached_input(self):
        tier = PricingTier(
            model="gpt-4o",
            input_price_per_1k=0.0025,
            output_price_per_1k=0.0100,
            cached_input_price_per_1k=0.00125,
        )
        assert tier.cached_input_price_per_1k == 0.00125


class TestCostBudgetInit:
    def test_default_values(self):
        b = CostBudget()
        assert b.hard_limit == 10.00
        assert b.warning_ratio == 0.80
        assert b.cumulative_cost == 0.0
        assert b.call_count == 0

    def test_custom_hard_limit(self):
        b = CostBudget(hard_limit=5.00)
        assert b.hard_limit == 5.00
        assert b.warning_ratio == 0.80

    def test_custom_warning_ratio(self):
        b = CostBudget(hard_limit=10.00, warning_ratio=0.50)
        assert b.warning_ratio == 0.50


class TestSetPricing:
    def test_register_new_pricing(self):
        b = CostBudget()
        b.set_pricing("openai", "gpt-4o", input_1k=0.0025, output_1k=0.0100)
        tier = b.provider_pricing["openai"]["gpt-4o"]
        assert tier.input_price_per_1k == 0.0025
        assert tier.output_price_per_1k == 0.0100

    def test_register_multiple_providers(self):
        b = CostBudget()
        b.set_pricing("openai", "gpt-4o", input_1k=0.0025, output_1k=0.0100)
        b.set_pricing("anthropic", "claude-opus", input_1k=0.0150, output_1k=0.0750)
        assert "openai" in b.provider_pricing
        assert "anthropic" in b.provider_pricing

    def test_overwrite_existing_pricing(self):
        b = CostBudget()
        b.set_pricing("openai", "gpt-4o", input_1k=0.0025, output_1k=0.0100)
        b.set_pricing("openai", "gpt-4o", input_1k=0.0030, output_1k=0.0120)
        tier = b.provider_pricing["openai"]["gpt-4o"]
        assert tier.input_price_per_1k == 0.0030


class TestGetCost:
    def test_known_pricing(self):
        b = CostBudget()
        b.set_pricing("openai", "gpt-4o", input_1k=0.0025, output_1k=0.0100)
        cost = b.get_cost("openai", "gpt-4o", input_tokens=1000, output_tokens=500)
        assert cost == pytest.approx(0.0025 + 0.0050)

    def test_with_cached_input(self):
        b = CostBudget()
        b.set_pricing(
            "openai",
            "gpt-4o",
            input_1k=0.0025,
            output_1k=0.0100,
            cached_input_1k=0.00125,
        )
        cost = b.get_cost("openai", "gpt-4o", input_tokens=0, output_tokens=0, cached_input_tokens=2000)
        assert cost == pytest.approx(0.0025)

    def test_unknown_provider_returns_zero(self):
        b = CostBudget()
        cost = b.get_cost("unknown", "unknown-model", input_tokens=1000, output_tokens=500)
        assert cost == 0.0

    def test_zero_tokens_returns_zero(self):
        b = CostBudget()
        b.set_pricing("openai", "gpt-4o", input_1k=0.0025, output_1k=0.0100)
        cost = b.get_cost("openai", "gpt-4o", input_tokens=0, output_tokens=0)
        assert cost == 0.0


class TestAssertBudget:
    def test_within_budget(self):
        b = CostBudget(hard_limit=10.00)
        b.assert_budget("openai", "gpt-4o")

    def test_exceeded_raises_error(self):
        b = CostBudget(hard_limit=0.01)
        b.cumulative_cost = 0.02
        with pytest.raises(CostBudgetExceededError) as exc:
            b.assert_budget("openai", "gpt-4o")
        assert exc.value.current == 0.02
        assert exc.value.limit == 0.01
        assert exc.value.provider == "openai"
        assert exc.value.model == "gpt-4o"

    def test_exactly_at_limit_raises(self):
        b = CostBudget(hard_limit=5.00)
        b.cumulative_cost = 5.00
        with pytest.raises(CostBudgetExceededError):
            b.assert_budget("openai", "gpt-4o")


class TestCheckBudgetOrWarn:
    def test_within_budget_no_warning(self):
        b = CostBudget(hard_limit=10.00)
        b.cumulative_cost = 1.00
        assert b.check_budget_or_warn() is None

    def test_above_warning_ratio_returns_warning(self):
        b = CostBudget(hard_limit=10.00, warning_ratio=0.50)
        b.cumulative_cost = 6.00
        warn = b.check_budget_or_warn()
        assert warn is not None
        assert "Cost budget warning" in warn
        assert "$6.0000" in warn

    def test_above_hard_limit_raises(self):
        b = CostBudget(hard_limit=10.00)
        b.cumulative_cost = 11.00
        with pytest.raises(CostBudgetExceededError):
            b.check_budget_or_warn()


class TestRecordUsage:
    def test_increases_cumulative_cost(self):
        b = CostBudget(hard_limit=10.00)
        b.set_pricing("openai", "gpt-4o", input_1k=0.0025, output_1k=0.0100)
        b.record_usage("openai", "gpt-4o", input_tokens=2000, output_tokens=1000)
        assert b.cumulative_cost == pytest.approx(0.0050 + 0.0100)

    def test_increments_call_count(self):
        b = CostBudget(hard_limit=10.00)
        b.set_pricing("openai", "gpt-4o", input_1k=0.0025, output_1k=0.0100)
        b.record_usage("openai", "gpt-4o", input_tokens=100, output_tokens=50)
        b.record_usage("openai", "gpt-4o", input_tokens=200, output_tokens=100)
        assert b.call_count == 2

    def test_returns_cost(self):
        b = CostBudget(hard_limit=10.00)
        b.set_pricing("openai", "gpt-4o", input_1k=0.0025, output_1k=0.0100)
        cost = b.record_usage("openai", "gpt-4o", input_tokens=1000, output_tokens=500)
        assert cost == pytest.approx(0.0075)

    def test_unknown_provider_zero_cost(self):
        b = CostBudget(hard_limit=10.00)
        cost = b.record_usage("unknown", "model", input_tokens=1000, output_tokens=500)
        assert cost == 0.0
        assert b.call_count == 1


class TestBudgetProperties:
    def test_remaining(self):
        b = CostBudget(hard_limit=10.00)
        b.cumulative_cost = 3.50
        assert b.remaining == 6.50

    def test_remaining_floors_at_zero(self):
        b = CostBudget(hard_limit=10.00)
        b.cumulative_cost = 15.00
        assert b.remaining == 0.0

    def test_usage_ratio(self):
        b = CostBudget(hard_limit=10.00)
        b.cumulative_cost = 3.00
        assert b.usage_ratio == 0.3

    def test_usage_ratio_capped_at_one(self):
        b = CostBudget(hard_limit=10.00)
        b.cumulative_cost = 20.00
        assert b.usage_ratio == 1.0

    def test_usage_ratio_zero_hard_limit(self):
        b = CostBudget(hard_limit=0)
        assert b.usage_ratio == 1.0


class TestReset:
    def test_reset_clears_accumulated(self):
        b = CostBudget(hard_limit=10.00)
        b.set_pricing("openai", "gpt-4o", input_1k=0.0025, output_1k=0.0100)
        b.record_usage("openai", "gpt-4o", input_tokens=1000, output_tokens=500)
        b.record_usage("openai", "gpt-4o", input_tokens=1000, output_tokens=500)
        b.reset()
        assert b.cumulative_cost == 0.0
        assert b.call_count == 0


class TestCostBudgetExceededError:
    def test_attributes(self):
        err = CostBudgetExceededError(
            current=15.00,
            limit=10.00,
            provider="openai",
            model="gpt-4o",
        )
        assert err.current == 15.00
        assert err.limit == 10.00
        assert err.provider == "openai"
        assert err.model == "gpt-4o"

    def test_message_format(self):
        err = CostBudgetExceededError(
            current=12.3456,
            limit=10.00,
            provider="openai",
            model="gpt-4o",
        )
        msg = str(err)
        assert "$12.3456" in msg
        assert "$10.0000" in msg
        assert "gpt-4o" in msg


class TestThreadSafety:
    def test_concurrent_record_usage(self):
        b = CostBudget(hard_limit=100.00)
        b.set_pricing("openai", "gpt-4o", input_1k=0.0025, output_1k=0.0100)

        errors = []

        def worker():
            try:
                for _ in range(100):
                    b.record_usage("openai", "gpt-4o", input_tokens=10, output_tokens=5)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=worker) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        assert b.call_count == 1000
