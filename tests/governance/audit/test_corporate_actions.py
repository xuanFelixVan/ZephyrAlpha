# [A_test] module_id: SRC-TST-0628 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §
# [MODULE] tests.test_corporate_actions
# [INVARIANTS] CorporateActionPipeline transform produces AdjFactor; priority mapping
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass; exit non-zero on fail
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

from zephyr.gov_audit.corporate_actions import (
    CAPIPELINE_SOURCES,
    CORPORATE_ACTION_PRIORITY,
    DAILY_PRE_CHECK_ITEMS,
    AdjFactor,
    CorporateActionEvent,
    CorporateActionPipeline,
    CorporateActionType,
)


class TestCorporateActionType:
    def test_enum_values(self):
        assert CorporateActionType.CASH_DIV == "CASH_DIV"
        assert CorporateActionType.STOCK_SPLIT == "STOCK_SPLIT"
        assert CorporateActionType.BONUS_SHARE == "BONUS_SHARE"
        assert CorporateActionType.MERGER == "MERGER"
        assert CorporateActionType.DELIST == "DELIST"
        assert CorporateActionType.SYMBOL_CHANGE == "SYMBOL_CHANGE"
        assert CorporateActionType.GICS_CHANGE == "GICS_CHANGE"


class TestCorporateActionPriority:
    def test_cash_div_is_p0(self):
        assert CORPORATE_ACTION_PRIORITY[CorporateActionType.CASH_DIV] == "P0"

    def test_merger_is_p1(self):
        assert CORPORATE_ACTION_PRIORITY[CorporateActionType.MERGER] == "P1"

    def test_all_types_have_priority(self):
        for ct in CorporateActionType:
            assert ct in CORPORATE_ACTION_PRIORITY


class TestCorporateActionEvent:
    def test_creation(self):
        event = CorporateActionEvent(
            action_type=CorporateActionType.CASH_DIV,
            symbol="AAPL",
            effective_date="2026-05-22",
            details={"amount": 0.82},
        )
        assert event.action_type == CorporateActionType.CASH_DIV
        assert event.symbol == "AAPL"
        assert event.details == {"amount": 0.82}

    def test_default_details(self):
        event = CorporateActionEvent(
            action_type=CorporateActionType.STOCK_SPLIT,
            symbol="TSLA",
            effective_date="2026-06-01",
        )
        assert event.details == {}


class TestAdjFactor:
    def test_creation(self):
        factor = AdjFactor(symbol="AAPL", date="2026-05-22", bwd_adj_factor=0.95, fwd_adj_factor=1.05)
        assert factor.symbol == "AAPL"
        assert factor.bwd_adj_factor == 0.95
        assert factor.fwd_adj_factor == 1.05

    def test_default_factors(self):
        factor = AdjFactor(symbol="AAPL", date="2026-05-22")
        assert factor.bwd_adj_factor == 1.0
        assert factor.fwd_adj_factor == 1.0


class TestCorporateActionPipeline:
    def test_instantiation(self):
        pipeline = CorporateActionPipeline()
        assert pipeline.events == []
        assert pipeline.adj_factors == []

    def test_source_filters_by_symbol(self):
        pipeline = CorporateActionPipeline()
        pipeline.events = [
            CorporateActionEvent(action_type=CorporateActionType.CASH_DIV, symbol="AAPL", effective_date="2026-05-22"),
            CorporateActionEvent(action_type=CorporateActionType.CASH_DIV, symbol="GOOG", effective_date="2026-05-22"),
        ]
        result = pipeline.source("AAPL")
        assert len(result) == 1
        assert result[0].symbol == "AAPL"

    def test_source_empty(self):
        pipeline = CorporateActionPipeline()
        result = pipeline.source("AAPL")
        assert result == []

    def test_validate_returns_empty_list(self):
        pipeline = CorporateActionPipeline()
        events = [
            CorporateActionEvent(action_type=CorporateActionType.CASH_DIV, symbol="AAPL", effective_date="2026-05-22"),
        ]
        result = pipeline.validate(events)
        assert result == []

    def test_transform_produces_adj_factors(self):
        pipeline = CorporateActionPipeline()
        events = [
            CorporateActionEvent(action_type=CorporateActionType.CASH_DIV, symbol="AAPL", effective_date="2026-05-22"),
            CorporateActionEvent(
                action_type=CorporateActionType.STOCK_SPLIT, symbol="TSLA", effective_date="2026-06-01"
            ),
        ]
        factors = pipeline.transform(events)
        assert len(factors) == 2
        assert all(isinstance(f, AdjFactor) for f in factors)

    def test_transform_skips_non_adjustable_types(self):
        pipeline = CorporateActionPipeline()
        events = [
            CorporateActionEvent(action_type=CorporateActionType.MERGER, symbol="X", effective_date="2026-05-22"),
            CorporateActionEvent(action_type=CorporateActionType.GICS_CHANGE, symbol="Y", effective_date="2026-05-22"),
        ]
        factors = pipeline.transform(events)
        assert len(factors) == 0

    def test_apply_sets_adj_factors(self):
        pipeline = CorporateActionPipeline()
        factors = [AdjFactor(symbol="AAPL", date="2026-05-22")]
        pipeline.apply(factors)
        assert pipeline.adj_factors == factors

    def test_verify_returns_true(self):
        pipeline = CorporateActionPipeline()
        assert pipeline.verify() is True


class TestConstants:
    def test_capipline_sources(self):
        assert "akshare" in CAPIPELINE_SOURCES
        assert "baostock" in CAPIPELINE_SOURCES

    def test_daily_pre_check_items(self):
        assert len(DAILY_PRE_CHECK_ITEMS) > 0
