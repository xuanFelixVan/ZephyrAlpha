# [A_test] module_id: MOD-GOV_registry_adapter_asset_inventory | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-238 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.asset_inventory.test_registry_adapter
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""Tests for MOD-INF-026 §17 RegistryAdapter module."""

from datetime import UTC
from pathlib import Path

from zephyr.infrastructure.asset_inventory.models import RegistryEntry
from zephyr.infrastructure.asset_inventory.registry_adapter import (
    CsvAdapter,
    MarkdownTableAdapter,
    RegistryManager,
    RegistryParseError,
    YamlListAdapter,
)
from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）

_YAML_LIST = """\
- id: entry-1
  relative_path: src/module_a.py
- id: entry-2
  relative_path: src/module_b.py
"""

_YAML_DICT = """\
entry-1:
  physical_path: src/module_a.py
  status: active
entry-2:
  physical_path: src/module_b.py
  status: deprecated
"""

_YAML_TIERS = """\
tiers:
  - registries:
    - registry_id: REG-A
      physical_path: path/to/reg.yaml
    - registry_id: REG-B
      physical_path: path/to/reg2.yaml
"""

_CSV = """\
path,name,status
src/a.py,Alpha,active
src/b.py,Beta,stale
"""

_MD_TABLE = """\
| File | Status | Notes |
|------|--------|-------|
| src/mod.py | active | ok |
| tests/test.py | active | test |
"""


class TestYamlListAdapter:
    def test_parse_list_format(self) -> None:
        ad = YamlListAdapter("REG-TEST", "*.yaml", asset_key="relative_path")
        entries = ad.parse(_YAML_LIST)
        assert len(entries) == 2
        assert entries[0].registry_id == "REG-TEST"
        assert entries[0].entry_path == "src/module_a.py"

    def test_parse_dict_format(self) -> None:
        ad = YamlListAdapter("REG-TEST", "*.yaml", asset_key="physical_path")
        entries = ad.parse(_YAML_DICT)
        assert len(entries) == 2
        assert entries[1].entry_path == "src/module_b.py"

    def test_parse_tiers_format(self) -> None:
        ad = YamlListAdapter("REG-TEST", "*.yaml")
        entries = ad.parse(_YAML_TIERS)
        assert len(entries) == 2
        assert entries[0].entry_path == "path/to/reg.yaml"

    def test_parse_empty(self) -> None:
        ad = YamlListAdapter("REG-TEST", "*.yaml")
        entries = ad.parse("null")
        assert entries == []

    def test_parse_invalid_yaml(self) -> None:
        ad = YamlListAdapter("REG-TEST", "*.yaml")
        try:
            ad.parse(":: invalid yaml ::")
        except RegistryParseError:
            return
        assert False, "Expected RegistryParseError"

    def test_can_handle(self) -> None:
        ad = YamlListAdapter("REG-TEST", "_registry.yaml")
        assert ad.can_handle("src/gates/_registry.yaml")
        assert not ad.can_handle("src/gates/gate.md")


class TestCsvAdapter:
    def test_parse_csv(self) -> None:
        ad = CsvAdapter("REG-CSV", path_column="path")
        entries = ad.parse(_CSV)
        assert len(entries) == 2
        assert entries[0].entry_path == "src/a.py"

    def test_can_handle_csv(self) -> None:
        ad = CsvAdapter("REG-CSV")
        assert ad.can_handle("report.csv")
        assert not ad.can_handle("report.yaml")


class TestMarkdownTableAdapter:
    def test_parse_md_table(self) -> None:
        ad = MarkdownTableAdapter("REG-MD", "registry.md", path_column=0)
        entries = ad.parse(_MD_TABLE)
        assert len(entries) == 2
        assert entries[0].entry_path == "src/mod.py"


class TestRegistryManager:
    def test_constructor(self) -> None:
        mgr = RegistryManager(REPO_ROOT)
        assert mgr.known

    def test_find_adapter_known(self) -> None:
        mgr = RegistryManager(REPO_ROOT)
        ad = mgr.find_adapter(str(REPO_ROOT / "docs/03_modules/module-registry.yaml"))
        assert ad is not None
        assert ad.registry_id == "REG-MOD-ALPHA_SIGNAL_DOMAIN"

    def test_find_adapter_csv_fallback(self) -> None:
        mgr = RegistryManager(REPO_ROOT)
        ad = mgr.find_adapter(str(REPO_ROOT / "data/export.csv"))
        assert ad is not None
        assert isinstance(ad, CsvAdapter)

    def test_cross_match_asset(self) -> None:
        from datetime import datetime

        from zephyr.infrastructure.asset_inventory.models import AssetStatus, AssetType, ClassifiedAsset

        asset = ClassifiedAsset(
            relative_path="src/matched.py",
            asset_type=AssetType.MODULE,
            status=AssetStatus.ACTIVE,
            size_bytes=100,
            mtime_utc=datetime.now(UTC),
            sha256="a" * 64,
        )
        registry_entries = [
            RegistryEntry(registry_id="R1", registry_path="", entry_path="src/other.py"),
            RegistryEntry(registry_id="R2", registry_path="", entry_path="src/matched.py"),
        ]

        mgr = RegistryManager(REPO_ROOT)
        assert mgr.cross_match_asset(asset, registry_entries)
