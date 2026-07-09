# [A_test] module_id: SRC-TST-1441 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-026 | docs/03_modules/_domain_infrastructure_operations/asset_inventory/blueprint.md | §
# [MODULE] tests.test_registry_adapter
# [INVARIANTS] RegistryAdapter subclasses parse raw content into list[RegistryEntry]
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RegistryParseError on invalid YAML
# [TESTS] tests/test_registry_adapter_root.py
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.infrastructure.asset_inventory.models import ClassifiedAsset, RegistryEntry
from zephyr.infrastructure.asset_inventory.registry_adapter import (
    CsvAdapter,
    FrontmatterAdapter,
    MarkdownTableAdapter,
    RegistryManager,
    RegistryParseError,
    TomlAdapter,
    YamlDictAdapter,
    YamlListAdapter,
)


class TestYamlListAdapterInstantiation:
    def test_default(self):
        a = YamlListAdapter("REG-TEST", "test.yaml")
        assert a.registry_id == "REG-TEST"

    def test_can_handle(self):
        a = YamlListAdapter("REG-TEST", "test.yaml")
        assert a.can_handle("path/to/test.yaml") is True
        assert a.can_handle("path/to/other.json") is False


class TestYamlListAdapterParse:
    def test_parse_list(self):
        yaml_content = """
- relative_path: src/a.py
  module_id: MOD-001
- relative_path: src/b.py
  module_id: MOD-002
"""
        a = YamlListAdapter("REG-TEST", "test.yaml")
        entries = a.parse(yaml_content)
        assert len(entries) == 2
        assert entries[0].entry_path == "src/a.py"

    def test_parse_empty(self):
        a = YamlListAdapter("REG-TEST", "test.yaml")
        entries = a.parse("")
        assert entries == []

    def test_parse_dict_with_tiers(self):
        yaml_content = """
tiers:
  - registries:
      - physical_path: src/zephyr/governance/rule_enforcement/_registry.yaml
        registry_id: REG-GATE-001
      - physical_path: scripts/script-manifest.yaml
        registry_id: REG-SCRIPT-001
"""
        a = YamlListAdapter("REG-TIER", "registry.yaml", asset_key="physical_path")
        entries = a.parse(yaml_content)
        assert len(entries) == 2
        assert entries[0].entry_path == "src/zephyr/governance/rule_enforcement/_registry.yaml"

    def test_parse_invalid_yaml(self):
        a = YamlListAdapter("REG-TEST", "test.yaml")
        with pytest.raises(RegistryParseError):
            a.parse(":\n  :\n    - [invalid")


class TestYamlDictAdapterInstantiation:
    def test_default(self):
        a = YamlDictAdapter("REG-TEST", "test.yaml")
        assert a.registry_id == "REG-TEST"


class TestYamlDictAdapterParse:
    def test_parse_script_manifest(self):
        yaml_content = """
scripts:
  - path: scripts/scan.py
    name: scan
  - path: scripts/check.py
    name: check
"""
        a = YamlDictAdapter("REG-SCRIPT-001", "script-manifest.yaml")
        entries = a.parse(yaml_content)
        assert len(entries) >= 2

    def test_parse_empty(self):
        a = YamlDictAdapter("REG-TEST", "test.yaml")
        entries = a.parse("")
        assert entries == []

    def test_parse_dict_with_physical_path(self):
        yaml_content = """
item1:
  physical_path: src/zephyr/mod.py
  version: "1.0"
"""
        a = YamlDictAdapter("REG-TEST", "test.yaml")
        entries = a.parse(yaml_content)
        assert len(entries) >= 1


class TestMarkdownTableAdapterInstantiation:
    def test_default(self):
        a = MarkdownTableAdapter("REG-TEST", "test.md", path_column=0)
        assert a.registry_id == "REG-TEST"

    def test_can_handle(self):
        a = MarkdownTableAdapter("REG-TEST", "_index.yaml")
        assert a.can_handle("docs/_index.yaml") is True
        assert a.can_handle("docs/other.md") is False


class TestMarkdownTableAdapterParse:
    def test_parse_table(self):
        content = """| Path | Type | Status |
|------|------|--------|
| src/a.py | module | active |
| src/b.py | module | stale |
"""
        a = MarkdownTableAdapter("REG-TEST", "test.md", path_column=0)
        entries = a.parse(content)
        assert len(entries) == 2
        assert entries[0].entry_path == "src/a.py"

    def test_parse_empty(self):
        a = MarkdownTableAdapter("REG-TEST", "test.md")
        entries = a.parse("")
        assert entries == []


class TestFrontmatterAdapterInstantiation:
    def test_default(self):
        a = FrontmatterAdapter("REG-TEST", "test.md")
        assert a.registry_id == "REG-TEST"


class TestFrontmatterAdapterParse:
    def test_parse_frontmatter(self):
        content = """---
module_id: MOD-INF-026
physical_path: src/zephyr/asset-inventory
---
# Content here
"""
        a = FrontmatterAdapter("REG-TEST", "test.md")
        entries = a.parse(content)
        assert len(entries) >= 1

    def test_parse_no_frontmatter(self):
        content = "Just regular markdown\nNo frontmatter here"
        a = FrontmatterAdapter("REG-TEST", "test.md")
        entries = a.parse(content)
        assert entries == []


class TestCsvAdapterInstantiation:
    def test_default(self):
        a = CsvAdapter("REG-TEST")
        assert a.registry_id == "REG-TEST"

    def test_can_handle(self):
        a = CsvAdapter("REG-TEST")
        assert a.can_handle("data.csv") is True
        assert a.can_handle("data.yaml") is False


class TestCsvAdapterParse:
    def test_parse_csv(self):
        content = "path,type,status\nsrc/a.py,module,active\nsrc/b.py,script,active\n"
        a = CsvAdapter("REG-TEST", path_column="path")
        entries = a.parse(content)
        assert len(entries) == 2
        assert entries[0].entry_path == "src/a.py"

    def test_parse_empty_csv(self):
        a = CsvAdapter("REG-TEST")
        entries = a.parse("")
        assert entries == []


class TestTomlAdapterInstantiation:
    def test_default(self):
        a = TomlAdapter("REG-TEST")
        assert a.registry_id == "REG-TEST"

    def test_can_handle(self):
        a = TomlAdapter("REG-TEST")
        assert a.can_handle("config.toml") is True
        assert a.can_handle("config.yaml") is False


class TestTomlAdapterParse:
    def test_parse_toml_list(self):
        content = """
[[assets]]
relative_path = "src/a.py"
type = "module"

[[assets]]
relative_path = "src/b.py"
type = "script"
"""
        a = TomlAdapter("REG-TEST", key="assets")
        entries = a.parse(content)
        assert len(entries) == 2

    def test_parse_empty(self):
        a = TomlAdapter("REG-TEST")
        entries = a.parse("")
        assert entries == []


class TestRegistryManagerInstantiation:
    def test_default(self, tmp_path):
        mgr = RegistryManager(project_root=tmp_path)
        assert mgr._root == tmp_path

    def test_known_adapters_initialized(self, tmp_path):
        mgr = RegistryManager(project_root=tmp_path)
        assert len(mgr._known) > 0


class TestRegistryManagerCrossMatch:
    def test_match_found(self, tmp_path):
        mgr = RegistryManager(project_root=tmp_path)
        asset = ClassifiedAsset(
            relative_path="src/zephyr/test.py",
            asset_type="module",
            size_bytes=100,
            mtime_utc="2026-01-01T00:00:00Z",
            sha256="abc",
        )
        entries = [RegistryEntry(registry_id="REG-TEST", registry_path="", entry_path="src/zephyr/test.py")]
        assert mgr.cross_match_asset(asset, entries) is True

    def test_no_match(self, tmp_path):
        mgr = RegistryManager(project_root=tmp_path)
        asset = ClassifiedAsset(
            relative_path="src/zephyr/missing.py",
            asset_type="module",
            size_bytes=100,
            mtime_utc="2026-01-01T00:00:00Z",
            sha256="abc",
        )
        entries = [RegistryEntry(registry_id="REG-TEST", registry_path="", entry_path="src/zephyr/other.py")]
        assert mgr.cross_match_asset(asset, entries) is False
