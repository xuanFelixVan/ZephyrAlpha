# [A_test] module_id: SRC-TST-0160 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §
# [TTL] task_bound
"""
[BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §9
[MODULE] tests.infrastructure.test_registry_governance
[INVARIANTS] 功能域注册表是功能域声明的唯一真源;SSoT门禁检查不可跳过
[MODIFY-GUARD] docs/03_modules/_domain-governance/registry-governance/blueprint.md
[CONSUMERS] None
[STABILITY] evolving
[SAFETY] L
[AI_AUTONOMY] ai_modifiable
[ERROR_CONTRACT] AssertionError→测试失败
[TESTS] self
"""

import pytest
import yaml

from zephyr.infrastructure.registry_governance import (
    FunctionalDomainRegistry,
)


@pytest.fixture
def sample_registry(tmp_path):
    data = {
        "registry_id": "REG-FUNC-DOMAIN-001",
        "entries": [
            {
                "domain": "governance",
                "subdomain": "gate_engine",
                "ssot_module": "MOD-GATE_ENGINE",
                "ssot_path": "src/zephyr/gov_enforcement/rule_enforcement/",
                "covers": ["rule_checking", "admission_control"],
                "aliases": ["gate", "门禁", "admission"],
                "stability": "stable",
                "ai_autonomy": "human_gated",
            },
            {
                "domain": "resilience",
                "subdomain": "circuit_breaker",
                "ssot_module": "MOD-INF-016",
                "ssot_path": "src/zephyr/shared/resilience/",
                "covers": ["circuit_breaker", "half_open", "error_budget"],
                "aliases": ["熔断器", "circuit breaker", "cb"],
                "stability": "stable",
                "ai_autonomy": "ai_modifiable",
            },
        ],
    }
    path = tmp_path / "test-registry.yaml"
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    return path


class TestFunctionalDomainRegistryLoad:
    def test_load_valid_registry(self, sample_registry):
        r = FunctionalDomainRegistry(registry_path=sample_registry)
        r.load()
        assert r.entry_count == 2

    def test_load_nonexistent_registry(self, tmp_path):
        r = FunctionalDomainRegistry(registry_path=tmp_path / "nonexistent.yaml")
        r.load()
        assert r.entry_count == 0

    def test_load_empty_registry(self, tmp_path):
        path = tmp_path / "empty.yaml"
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump({"entries": []}, f)
        r = FunctionalDomainRegistry(registry_path=path)
        r.load()
        assert r.entry_count == 0


class TestFunctionalDomainRegistryQuery:
    def test_query_existing_domain(self, sample_registry):
        r = FunctionalDomainRegistry(registry_path=sample_registry)
        r.load()
        results = r.query_domain("governance")
        assert len(results) == 1
        assert results[0].ssot_module == "MOD-GATE_ENGINE"

    def test_query_with_subdomain(self, sample_registry):
        r = FunctionalDomainRegistry(registry_path=sample_registry)
        r.load()
        results = r.query_domain("governance", subdomain="gate_engine")
        assert len(results) == 1
        assert results[0].subdomain == "gate_engine"

    def test_query_nonexistent_domain(self, sample_registry):
        r = FunctionalDomainRegistry(registry_path=sample_registry)
        r.load()
        results = r.query_domain("nonexistent")
        assert len(results) == 0

    def test_list_domains(self, sample_registry):
        r = FunctionalDomainRegistry(registry_path=sample_registry)
        r.load()
        domains = r.list_domains()
        assert "governance" in domains
        assert "resilience" in domains

    def test_list_subdomains(self, sample_registry):
        r = FunctionalDomainRegistry(registry_path=sample_registry)
        r.load()
        subs = r.list_subdomains("governance")
        assert "gate_engine" in subs


class TestFunctionalDomainRegistryOverlap:
    def test_exact_domain_overlap(self, sample_registry):
        r = FunctionalDomainRegistry(registry_path=sample_registry)
        r.load()
        result = r.check_overlap(domain="governance", subdomain="gate_engine")
        assert result.has_overlap is True
        assert len(result.overlapping_entries) >= 1

    def test_covers_overlap(self, sample_registry):
        r = FunctionalDomainRegistry(registry_path=sample_registry)
        r.load()
        result = r.check_overlap(
            domain="new_domain",
            subdomain="new_sub",
            covers=["circuit_breaker", "half_open"],
        )
        assert result.has_overlap is True

    def test_alias_match(self, sample_registry):
        r = FunctionalDomainRegistry(registry_path=sample_registry)
        r.load()
        result = r.check_overlap(
            domain="new_domain",
            subdomain="new_sub",
            name="熔断器保护",
            description="circuit breaker protection",
        )
        assert result.has_overlap is True

    def test_no_overlap(self, sample_registry):
        r = FunctionalDomainRegistry(registry_path=sample_registry)
        r.load()
        result = r.check_overlap(
            domain="quantum",
            subdomain="scheduler",
            covers=["quantum_scheduling"],
            name="quantum scheduler",
            description="量子任务调度",
        )
        assert result.has_overlap is False


class TestFunctionalDomainRegistryRegister:
    def test_register_new_entry(self, sample_registry):
        r = FunctionalDomainRegistry(registry_path=sample_registry)
        r.load()
        r.register(
            domain="intelligence",
            subdomain="embedding",
            ssot_module="MOD-INF-011",
            ssot_path="src/zephyr/embedding/",
            covers=["embedding_model", "vector_search"],
            aliases=["嵌入", "embedding"],
        )
        assert r.entry_count == 3
        results = r.query_domain("intelligence")
        assert len(results) == 1

    def test_register_overlap_raises(self, sample_registry):
        r = FunctionalDomainRegistry(registry_path=sample_registry)
        r.load()
        with pytest.raises(ValueError, match="Functional domain overlap"):
            r.register(
                domain="governance",
                subdomain="gate_engine",
                ssot_module="MOD-INF-999",
                ssot_path="src/zephyr/fake/",
            )

    def test_register_persists_to_file(self, sample_registry):
        r = FunctionalDomainRegistry(registry_path=sample_registry)
        r.load()
        r.register(
            domain="testing",
            subdomain="red_blue",
            ssot_module="MOD-INF-030",
            ssot_path="src/zephyr/red-blue-validator/",
        )
        r2 = FunctionalDomainRegistry(registry_path=sample_registry)
        r2.load()
        assert r2.entry_count == 3
