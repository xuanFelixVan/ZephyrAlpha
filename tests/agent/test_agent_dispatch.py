# [A_test] module_id: MOD-GOV_agent_dispatch | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-345 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.test_agent_dispatch
# [INVARIANTS] DISPATCH_TABLE keys must be unique; resolve_domain returns None for unknown
# [MODIFY-GUARD] Changes must sync with agent_dispatch.py
# [CONSUMERS] CI pipeline
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] None
# [TESTS] tests/test_agent_dispatch.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.governance.ops_governance.agent_dispatch import (
    DISPATCH_TABLE,
    DomainDispatch,
    get_dispatch_count,
    list_all_domains,
    resolve_by_keyword,
    resolve_domain,
)


class TestDomainDispatch:
    def test_creation(self):
        d = DomainDispatch(
            domain="test",
            pre_read="readme",
            re_read="blueprint",
            token_budget=500,
        )
        assert d.domain == "test"
        assert d.token_budget == 500

    def test_frozen_dataclass(self):
        d = DomainDispatch(
            domain="test",
            pre_read="r",
            re_read="b",
            token_budget=100,
        )
        try:
            d.domain = "changed"
            assert False, "Should be frozen"
        except AttributeError:
            assert True

    def test_default_blueprint_section(self):
        d = DomainDispatch(
            domain="test",
            pre_read="r",
            re_read="b",
            token_budget=100,
        )
        assert d.blueprint_section == ""


class TestResolveDomain:
    def test_resolve_existing_key(self):
        result = resolve_domain("gate-breaker")
        assert result is not None
        assert result.domain == "门禁/断路器"

    def test_resolve_unknown_key_returns_none(self):
        result = resolve_domain("nonexistent-domain-xyz")
        assert result is None

    def test_resolve_cross_system(self):
        result = resolve_domain("cross-system-integration")
        assert result is not None
        assert result.token_budget == 2000


class TestListAllDomains:
    def test_returns_sorted_list(self):
        domains = list_all_domains()
        assert domains == sorted(domains)

    def test_contains_known_domains(self):
        domains = list_all_domains()
        assert "gate-breaker" in domains
        assert "new-module" in domains

    def test_non_empty(self):
        domains = list_all_domains()
        assert len(domains) > 0


class TestResolveByKeyword:
    def test_keyword_match_domain(self):
        results = resolve_by_keyword("门禁")
        assert len(results) > 0

    def test_keyword_no_match(self):
        results = resolve_by_keyword("zzzzzzz_no_match")
        assert len(results) == 0

    def test_keyword_case_insensitive(self):
        results_lower = resolve_by_keyword("gate")
        results_upper = resolve_by_keyword("GATE")
        assert len(results_lower) == len(results_upper)

    def test_keyword_match_blueprint_section(self):
        results = resolve_by_keyword("§2")
        assert len(results) > 0


class TestGetDispatchCount:
    def test_count_matches_table(self):
        assert get_dispatch_count() == len(DISPATCH_TABLE)

    def test_count_positive(self):
        assert get_dispatch_count() > 0


class TestDispatchTableIntegrity:
    def test_all_entries_have_required_fields(self):
        for key, dispatch in DISPATCH_TABLE.items():
            assert dispatch.domain, f"Missing domain for key {key}"
            assert dispatch.pre_read, f"Missing pre_read for key {key}"
            assert dispatch.re_read, f"Missing re_read for key {key}"
            assert dispatch.token_budget > 0, f"Invalid token_budget for key {key}"

    def test_all_token_budgets_positive(self):
        for key, dispatch in DISPATCH_TABLE.items():
            assert dispatch.token_budget > 0, f"Non-positive budget for {key}"
