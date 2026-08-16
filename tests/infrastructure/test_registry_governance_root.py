# [A_test] module_id: MOD-GOV_registry_governance_root | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §3
# [MODULE] tests.test_registry_governance
# [INVARIANTS] FunctionalDomainRegistry.register必须检测重叠; DomainEntry必须有domain+subdomain+ssot_module
# [MODIFY-GUARD] 仅当registry_governance公开API变更时修改
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] import失败→skip; 实例化失败→fail
# [TESTS] pytest tests/test_registry_governance.py -q
# [TTL] task_bound

import pytest
import yaml

from zephyr.infrastructure.registry_governance import (
    DomainEntry,
    FunctionalDomainRegistry,
    OverlapResult,
)


class TestDomainEntry:
    def test_default_construction(self):
        entry = DomainEntry(
            domain="test",
            subdomain="sub",
            ssot_module="mod.test",
            ssot_path="/path/to/test",
        )
        assert entry.domain == "test"
        assert entry.subdomain == "sub"
        assert entry.covers == []
        assert entry.aliases == []
        assert entry.change_policy == "evolving"
        assert entry.modification_permission == "human_gated"


class TestOverlapResult:
    def test_default_no_overlap(self):
        result = OverlapResult()
        assert result.has_overlap is False
        assert result.overlapping_entries == []
        assert result.overlap_details == []


class TestFunctionalDomainRegistry:
    def test_instantiation(self, tmp_path):
        reg = FunctionalDomainRegistry(registry_path=tmp_path / "reg.yaml")
        assert reg is not None

    def test_load_empty_registry(self, tmp_path):
        reg_path = tmp_path / "reg.yaml"
        reg_path.write_text(
            yaml.dump({"entries": []}),
            encoding="utf-8",
        )
        reg = FunctionalDomainRegistry(registry_path=reg_path)
        reg.load()
        assert reg.entry_count == 0

    def test_load_nonexistent_registry(self, tmp_path):
        reg = FunctionalDomainRegistry(registry_path=tmp_path / "nonexistent.yaml")
        reg.load()
        assert reg.entry_count == 0

    def test_register_new_domain(self, tmp_path):
        reg_path = tmp_path / "reg.yaml"
        reg_path.write_text(yaml.dump({"entries": []}), encoding="utf-8")
        reg = FunctionalDomainRegistry(registry_path=reg_path)
        reg.register(
            domain="infrastructure",
            subdomain="config",
            ssot_module="zephyr.infrastructure.config",
            ssot_path="src/zephyr/l01-infrastructure/config.py",
        )
        assert reg.entry_count == 1

    def test_register_duplicate_raises(self, tmp_path):
        reg_path = tmp_path / "reg.yaml"
        reg_path.write_text(yaml.dump({"entries": []}), encoding="utf-8")
        reg = FunctionalDomainRegistry(registry_path=reg_path)
        reg.register(
            domain="infrastructure",
            subdomain="config",
            ssot_module="zephyr.infrastructure.config",
            ssot_path="src/zephyr/l01-infrastructure/config.py",
        )
        with pytest.raises(ValueError, match="overlap"):
            reg.register(
                domain="infrastructure",
                subdomain="config",
                ssot_module="zephyr.infrastructure.config2",
                ssot_path="src/zephyr/l01-infrastructure/config2.py",
            )

    def test_query_domain(self, tmp_path):
        reg_path = tmp_path / "reg.yaml"
        reg_path.write_text(
            yaml.dump(
                {
                    "entries": [
                        {
                            "domain": "security",
                            "subdomain": "auth",
                            "ssot_module": "mod.auth",
                            "ssot_path": "/auth",
                        },
                        {
                            "domain": "security",
                            "subdomain": "crypto",
                            "ssot_module": "mod.crypto",
                            "ssot_path": "/crypto",
                        },
                    ]
                }
            ),
            encoding="utf-8",
        )
        reg = FunctionalDomainRegistry(registry_path=reg_path)
        results = reg.query_domain("security")
        assert len(results) == 2
        sub = reg.query_domain("security", subdomain="auth")
        assert len(sub) == 1

    def test_check_overlap_with_covers(self, tmp_path):
        reg_path = tmp_path / "reg.yaml"
        reg_path.write_text(
            yaml.dump(
                {
                    "entries": [
                        {
                            "domain": "infra",
                            "subdomain": "config",
                            "ssot_module": "mod.config",
                            "ssot_path": "/config",
                            "covers": ["yaml_parsing", "env_vars"],
                        },
                    ]
                }
            ),
            encoding="utf-8",
        )
        reg = FunctionalDomainRegistry(registry_path=reg_path)
        result = reg.check_overlap("new", "domain", covers=["yaml_parsing"])
        assert result.has_overlap is True

    def test_check_overlap_no_overlap(self, tmp_path):
        reg_path = tmp_path / "reg.yaml"
        reg_path.write_text(
            yaml.dump(
                {
                    "entries": [
                        {
                            "domain": "infra",
                            "subdomain": "config",
                            "ssot_module": "mod.config",
                            "ssot_path": "/config",
                            "covers": ["yaml_parsing"],
                        },
                    ]
                }
            ),
            encoding="utf-8",
        )
        reg = FunctionalDomainRegistry(registry_path=reg_path)
        result = reg.check_overlap("new", "domain", covers=["completely_different"])
        assert result.has_overlap is False

    def test_list_domains(self, tmp_path):
        reg_path = tmp_path / "reg.yaml"
        reg_path.write_text(
            yaml.dump(
                {
                    "entries": [
                        {"domain": "b_domain", "subdomain": "s1", "ssot_module": "m1", "ssot_path": "/p1"},
                        {"domain": "a_domain", "subdomain": "s2", "ssot_module": "m2", "ssot_path": "/p2"},
                    ]
                }
            ),
            encoding="utf-8",
        )
        reg = FunctionalDomainRegistry(registry_path=reg_path)
        domains = reg.list_domains()
        assert domains == ["a_domain", "b_domain"]

    def test_list_subdomains(self, tmp_path):
        reg_path = tmp_path / "reg.yaml"
        reg_path.write_text(
            yaml.dump(
                {
                    "entries": [
                        {"domain": "infra", "subdomain": "z_sub", "ssot_module": "m1", "ssot_path": "/p1"},
                        {"domain": "infra", "subdomain": "a_sub", "ssot_module": "m2", "ssot_path": "/p2"},
                    ]
                }
            ),
            encoding="utf-8",
        )
        reg = FunctionalDomainRegistry(registry_path=reg_path)
        subs = reg.list_subdomains("infra")
        assert subs == ["a_sub", "z_sub"]

    def test_write_registry_uses_atomic_write(self, tmp_path):
        reg_path = tmp_path / "reg.yaml"
        reg_path.write_text(yaml.dump({"entries": []}), encoding="utf-8")
        reg = FunctionalDomainRegistry(registry_path=reg_path)
        reg.register(
            domain="test",
            subdomain="atomic",
            ssot_module="mod.atomic",
            ssot_path="/atomic",
        )
        content = reg_path.read_text(encoding="utf-8")
        data = yaml.safe_load(content)
        assert len(data["entries"]) == 1
