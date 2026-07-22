# [A_test] module_id: MOD-GOV_skill_tokenomics | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md | §
# [MODULE] tests.test_skill_tokenomics
# [INVARIANTS] TokenBudget.remaining >= 0; usage_ratio in [0.0, 1.0] for max_tokens > 0
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_skill_tokenomics.py
# [TTL] task_bound

from zephyr.autonomy_core.skills.skill_tokenomics import (
    SkillBudgetPreset,
    SkillTokenomics,
    TokenBudget,
    UsageRecord,
)


class TestSkillBudgetPreset:
    def test_enum_values(self):
        assert SkillBudgetPreset.TIGHT.value == "tight"
        assert SkillBudgetPreset.NORMAL.value == "normal"
        assert SkillBudgetPreset.GENEROUS.value == "generous"


class TestTokenBudget:
    def test_instantiation_defaults(self):
        budget = TokenBudget(max_tokens=1000)
        assert budget.max_tokens == 1000
        assert budget.used == 0
        assert budget.hard_cap is True
        assert budget.warn_threshold == 0.8

    def test_remaining_property(self):
        budget = TokenBudget(max_tokens=1000, used=300)
        assert budget.remaining == 700

    def test_remaining_clamped_at_zero(self):
        budget = TokenBudget(max_tokens=100, used=200)
        assert budget.remaining == 0

    def test_usage_ratio(self):
        budget = TokenBudget(max_tokens=1000, used=500)
        assert budget.usage_ratio == 0.5

    def test_usage_ratio_zero_max(self):
        budget = TokenBudget(max_tokens=0, used=0)
        assert budget.usage_ratio == 1.0

    def test_is_exhausted(self):
        budget = TokenBudget(max_tokens=100, used=100)
        assert budget.is_exhausted is True

    def test_is_not_exhausted(self):
        budget = TokenBudget(max_tokens=100, used=50)
        assert budget.is_exhausted is False

    def test_is_warning(self):
        budget = TokenBudget(max_tokens=100, used=85)
        assert budget.is_warning is True

    def test_is_not_warning(self):
        budget = TokenBudget(max_tokens=100, used=50)
        assert budget.is_warning is False


class TestUsageRecord:
    def test_instantiation(self):
        record = UsageRecord(skill_id="test_skill", tokens=100)
        assert record.skill_id == "test_skill"
        assert record.tokens == 100
        assert record.model == ""
        assert record.purpose == ""

    def test_estimated_cost_known_model(self):
        record = UsageRecord(skill_id="s", tokens=1_000_000, model="DeepSeek")
        cost = record.estimated_cost_usd
        assert cost > 0

    def test_estimated_cost_unknown_model(self):
        record = UsageRecord(skill_id="s", tokens=1_000_000, model="UnknownModel")
        cost = record.estimated_cost_usd
        assert cost > 0

    def test_estimated_cost_zero_tokens(self):
        record = UsageRecord(skill_id="s", tokens=0, model="DeepSeek")
        assert record.estimated_cost_usd == 0.0


class TestSkillTokenomicsInstantiation:
    def test_default_daily_budget(self):
        tk = SkillTokenomics()
        assert tk._daily_budget.max_tokens == 500_000

    def test_custom_daily_budget(self):
        tk = SkillTokenomics(daily_budget_tokens=1_000_000)
        assert tk._daily_budget.max_tokens == 1_000_000


class TestSetBudget:
    def setup_method(self):
        self.tk = SkillTokenomics()

    def test_set_budget_returns_dict(self):
        result = self.tk.set_budget("skill_a", 5000)
        assert result["skill_id"] == "skill_a"
        assert result["max_tokens"] == 5000
        assert result["budget_set"] is True

    def test_set_budget_with_options(self):
        result = self.tk.set_budget("skill_b", 10000, hard_cap=False, warn_threshold=0.9)
        assert result["hard_cap"] is False
        assert result["warn_threshold"] == 0.9

    def test_set_preset_budget_tight(self):
        result = self.tk.set_preset_budget("skill_c", SkillBudgetPreset.TIGHT)
        assert result["max_tokens"] == 4096

    def test_set_preset_budget_normal(self):
        result = self.tk.set_preset_budget("skill_d", SkillBudgetPreset.NORMAL)
        assert result["max_tokens"] == 16384

    def test_set_preset_budget_generous(self):
        result = self.tk.set_preset_budget("skill_e", SkillBudgetPreset.GENEROUS)
        assert result["max_tokens"] == 65536


class TestGetAndResetBudget:
    def setup_method(self):
        self.tk = SkillTokenomics()

    def test_get_budget_none_when_not_set(self):
        assert self.tk.get_budget("nonexistent") is None

    def test_get_budget_after_set(self):
        self.tk.set_budget("skill_a", 5000)
        budget = self.tk.get_budget("skill_a")
        assert budget is not None
        assert budget.max_tokens == 5000

    def test_reset_budget_existing(self):
        self.tk.set_budget("skill_a", 5000)
        self.tk.consume("skill_a", 2000)
        result = self.tk.reset_budget("skill_a")
        assert result["reset"] is True
        budget = self.tk.get_budget("skill_a")
        assert budget.used == 0

    def test_reset_budget_nonexistent(self):
        result = self.tk.reset_budget("nonexistent")
        assert result["reset"] is False

    def test_reset_all(self):
        self.tk.set_budget("a", 1000)
        self.tk.set_budget("b", 2000)
        self.tk.consume("a", 100)
        self.tk.consume("b", 200)
        count = self.tk.reset_all()
        assert count == 2
        assert self.tk.get_budget("a").used == 0
        assert self.tk.get_budget("b").used == 0


class TestConsume:
    def setup_method(self):
        self.tk = SkillTokenomics()

    def test_consume_creates_budget_if_missing(self):
        result = self.tk.consume("new_skill", 500)
        assert result["tokens_consumed"] == 500
        assert result["tokens_used"] == 500

    def test_consume_accumulates(self):
        self.tk.set_budget("skill_a", 10000)
        self.tk.consume("skill_a", 1000)
        result = self.tk.consume("skill_a", 2000)
        assert result["tokens_used"] == 3000

    def test_consume_tracks_remaining(self):
        self.tk.set_budget("skill_a", 5000)
        result = self.tk.consume("skill_a", 2000)
        assert result["remaining"] == 3000

    def test_consume_exhausted_with_hard_cap(self):
        self.tk.set_budget("skill_a", 100, hard_cap=True)
        self.tk.consume("skill_a", 100)
        result = self.tk.consume("skill_a", 50)
        assert result["budget_exhausted"] is True

    def test_consume_warning_threshold(self):
        self.tk.set_budget("skill_a", 1000, warn_threshold=0.8)
        result = self.tk.consume("skill_a", 850)
        assert result["budget_warning"] is True


class TestCheckBeforeConsume:
    def setup_method(self):
        self.tk = SkillTokenomics()

    def test_no_budget_allows(self):
        result = self.tk.evaluate_consumption("no_budget_skill", 100)
        assert result["allowed"] is True

    def test_budget_allows_when_remaining(self):
        self.tk.set_budget("skill_a", 1000)
        result = self.tk.evaluate_consumption("skill_a", 500)
        assert result["allowed"] is True

    def test_budget_blocks_when_exhausted_hard_cap(self):
        self.tk.set_budget("skill_a", 100, hard_cap=True)
        self.tk.consume("skill_a", 100)
        result = self.tk.evaluate_consumption("skill_a", 50)
        assert result["allowed"] is False

    def test_budget_allows_when_exhausted_soft_cap(self):
        self.tk.set_budget("skill_a", 100, hard_cap=False)
        self.tk.consume("skill_a", 100)
        result = self.tk.evaluate_consumption("skill_a", 50)
        assert result["allowed"] is True


class TestSuggestOptimizations:
    def setup_method(self):
        self.tk = SkillTokenomics()

    def test_no_suggestions_when_usage_low(self):
        self.tk.set_budget("skill_a", 10000)
        self.tk.consume("skill_a", 100)
        suggestions = self.tk.suggest_optimizations()
        assert all(s["skill_id"] != "skill_a" for s in suggestions)

    def test_suggestion_when_near_exhausted(self):
        self.tk.set_budget("skill_a", 1000)
        self.tk.consume("skill_a", 950)
        suggestions = self.tk.suggest_optimizations()
        assert any(s["skill_id"] == "skill_a" for s in suggestions)


class TestGetUsageReport:
    def setup_method(self):
        self.tk = SkillTokenomics()

    def test_empty_report(self):
        report = self.tk.get_usage_report()
        assert report["total_tokens"] == 0
        assert report["total_calls"] == 0

    def test_report_for_specific_skill(self):
        self.tk.set_budget("skill_a", 10000)
        self.tk.consume("skill_a", 500, model="DeepSeek")
        report = self.tk.get_usage_report("skill_a")
        assert report["skill_id"] == "skill_a"
        assert report["total_tokens"] == 500
        assert report["total_calls"] == 1

    def test_report_all_skills(self):
        self.tk.consume("a", 100, model="DeepSeek")
        self.tk.consume("b", 200, model="Claude")
        report = self.tk.get_usage_report()
        assert report["total_tokens"] == 300
        assert report["total_calls"] == 2


class TestGetTopConsumers:
    def setup_method(self):
        self.tk = SkillTokenomics()

    def test_empty_top_consumers(self):
        result = self.tk.get_top_consumers()
        assert result == []

    def test_top_consumers_ranked(self):
        self.tk.consume("a", 100)
        self.tk.consume("b", 500)
        self.tk.consume("c", 300)
        result = self.tk.get_top_consumers(n=2)
        assert len(result) == 2
        assert result[0]["skill_id"] == "b"
        assert result[0]["tokens"] == 500


class TestForecastBudget:
    def setup_method(self):
        self.tk = SkillTokenomics()

    def test_forecast_with_no_budget(self):
        result = self.tk.forecast_budget("no_budget", 10, 1000)
        assert result["budget_remaining"] is None
        assert result["hours_until_exhausted"] is None

    def test_forecast_with_budget(self):
        self.tk.set_budget("skill_a", 10000)
        self.tk.consume("skill_a", 2000)
        result = self.tk.forecast_budget("skill_a", 5, 1000)
        assert result["hourly_burn"] == 5000
        assert result["hours_until_exhausted"] is not None

    def test_forecast_zero_calls_per_hour(self):
        self.tk.set_budget("skill_a", 10000)
        result = self.tk.forecast_budget("skill_a", 0, 1000)
        assert result["hours_until_exhausted"] is None
