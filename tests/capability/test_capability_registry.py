# [A_test] module_id: MOD-GOV_capability_registry | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §
# [MODULE] tests.test_capability_registry
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_capability_registry.py
# [TTL] task_bound

from __future__ import annotations

import yaml

from zephyr.trading.capability_card import CapabilityCard, CapabilityCategory
from zephyr.trading.capability_registry import CapabilityRegistry


def _make_card(
    capability_id: str = "test-card",
    name: str = "Test Card",
    category: CapabilityCategory = CapabilityCategory.INFRA,
    description: str = "A test card",
    tags: list[str] | None = None,
    status: str = "ACTIVE",
) -> CapabilityCard:
    return CapabilityCard(
        capability_id=capability_id,
        name=name,
        category=category,
        description=description,
        tags=tags or [],
        status=status,
    )


class TestCapabilityRegistryInit:
    def test_init_no_dir(self):
        reg = CapabilityRegistry()
        assert reg.count() == 0
        assert reg._card_dir is None

    def test_init_with_dir(self, tmp_path):
        reg = CapabilityRegistry(card_dir=tmp_path)
        assert reg._card_dir == tmp_path


class TestCapabilityRegistryRegister:
    def test_register_card(self, tmp_path):
        reg = CapabilityRegistry(card_dir=tmp_path)
        card = _make_card("c1")
        reg.register(card)
        assert reg.count() == 1
        assert reg.get("c1") is not None

    def test_register_duplicate_ignored(self, tmp_path):
        reg = CapabilityRegistry(card_dir=tmp_path)
        card = _make_card("c1")
        reg.register(card)
        reg.register(card)
        assert reg.count() == 1

    def test_register_persists_to_disk(self, tmp_path):
        reg = CapabilityRegistry(card_dir=tmp_path)
        card = _make_card("persist-test")
        reg.register(card)
        yaml_file = tmp_path / "persist-test.yaml"
        assert yaml_file.exists()
        data = yaml.safe_load(yaml_file.read_text(encoding="utf-8"))
        assert data["capability_id"] == "persist-test"

    def test_register_no_dir_no_persist(self):
        reg = CapabilityRegistry()
        card = _make_card("no-dir")
        reg.register(card)
        assert reg.count() == 1


class TestCapabilityRegistryUnregister:
    def test_unregister_existing(self, tmp_path):
        reg = CapabilityRegistry(card_dir=tmp_path)
        card = _make_card("c1")
        reg.register(card)
        reg.unregister("c1")
        assert reg.count() == 0
        assert reg.get("c1") is None

    def test_unregister_nonexistent(self, tmp_path):
        reg = CapabilityRegistry(card_dir=tmp_path)
        reg.unregister("nonexistent")
        assert reg.count() == 0


class TestCapabilityRegistryDiscover:
    def test_discover_by_name(self, tmp_path):
        reg = CapabilityRegistry(card_dir=tmp_path)
        reg.register(_make_card("c1", name="Embedding Router"))
        reg.register(_make_card("c2", name="Health Monitor"))
        results = reg.discover("embedding")
        assert len(results) == 1
        assert results[0].capability_id == "c1"

    def test_discover_by_description(self, tmp_path):
        reg = CapabilityRegistry(card_dir=tmp_path)
        reg.register(_make_card("c1", description="Handles data processing"))
        reg.register(_make_card("c2", description="Manages security"))
        results = reg.discover("security")
        assert len(results) == 1
        assert results[0].capability_id == "c2"

    def test_discover_case_insensitive(self, tmp_path):
        reg = CapabilityRegistry(card_dir=tmp_path)
        reg.register(_make_card("c1", name="Embedding Router"))
        results = reg.discover("EMBEDDING")
        assert len(results) == 1

    def test_discover_no_match(self, tmp_path):
        reg = CapabilityRegistry(card_dir=tmp_path)
        reg.register(_make_card("c1", name="Test"))
        results = reg.discover("nonexistent")
        assert len(results) == 0

    def test_discover_empty_query(self, tmp_path):
        reg = CapabilityRegistry(card_dir=tmp_path)
        reg.register(_make_card("c1"))
        results = reg.discover("")
        assert len(results) == 1


class TestCapabilityRegistryFindByTags:
    def test_find_by_tags_match(self, tmp_path):
        reg = CapabilityRegistry(card_dir=tmp_path)
        reg.register(_make_card("c1", tags=["security", "audit"]))
        reg.register(_make_card("c2", tags=["infra", "monitoring"]))
        results = reg.find_by_tags(["security"])
        assert len(results) == 1
        assert results[0].capability_id == "c1"

    def test_find_by_tags_partial_match(self, tmp_path):
        reg = CapabilityRegistry(card_dir=tmp_path)
        reg.register(_make_card("c1", tags=["security", "audit"]))
        results = reg.find_by_tags(["audit", "nonexistent"])
        assert len(results) == 1

    def test_find_by_tags_no_match(self, tmp_path):
        reg = CapabilityRegistry(card_dir=tmp_path)
        reg.register(_make_card("c1", tags=["security"]))
        results = reg.find_by_tags(["infra"])
        assert len(results) == 0

    def test_find_by_tags_case_insensitive(self, tmp_path):
        reg = CapabilityRegistry(card_dir=tmp_path)
        reg.register(_make_card("c1", tags=["Security"]))
        results = reg.find_by_tags(["SECURITY"])
        assert len(results) == 1


class TestCapabilityRegistryListAll:
    def test_list_all_empty(self, tmp_path):
        reg = CapabilityRegistry(card_dir=tmp_path)
        assert reg.list_all() == []

    def test_list_all_returns_all(self, tmp_path):
        reg = CapabilityRegistry(card_dir=tmp_path)
        reg.register(_make_card("c1"))
        reg.register(_make_card("c2"))
        assert len(reg.list_all()) == 2


class TestCapabilityRegistryHealthCheckAll:
    def test_health_check_all_active(self, tmp_path):
        reg = CapabilityRegistry(card_dir=tmp_path)
        reg.register(_make_card("c1", status="ACTIVE"))
        reg.register(_make_card("c2", status="ACTIVE"))
        result = reg.health_check_all()
        assert result == {"c1": True, "c2": True}

    def test_health_check_all_mixed(self, tmp_path):
        reg = CapabilityRegistry(card_dir=tmp_path)
        reg.register(_make_card("c1", status="ACTIVE"))
        reg.register(_make_card("c2", status="DEGRADED"))
        result = reg.health_check_all()
        assert result["c1"] is True
        assert result["c2"] is False

    def test_health_check_all_empty(self, tmp_path):
        reg = CapabilityRegistry(card_dir=tmp_path)
        assert reg.health_check_all() == {}


class TestCapabilityRegistryDumpSnapshot:
    def test_dump_snapshot(self, tmp_path):
        reg = CapabilityRegistry(card_dir=tmp_path)
        reg.register(_make_card("c1", name="Snap"))
        snapshot = reg.dump_snapshot()
        assert "c1" in snapshot
        assert snapshot["c1"]["name"] == "Snap"

    def test_dump_snapshot_empty(self, tmp_path):
        reg = CapabilityRegistry(card_dir=tmp_path)
        assert reg.dump_snapshot() == {}


class TestCapabilityRegistryLoadFromDir:
    def test_load_from_dir(self, tmp_path):
        card_data = {
            "capability_id": "loaded-card",
            "name": "Loaded Card",
            "category": "infra",
            "description": "loaded from disk",
        }
        yaml_file = tmp_path / "loaded-card.yaml"
        yaml_file.write_text(yaml.dump(card_data, allow_unicode=True), encoding="utf-8")

        reg = CapabilityRegistry(card_dir=tmp_path)
        count = reg.load_from_dir()
        assert count == 1
        assert reg.get("loaded-card") is not None

    def test_load_from_dir_no_dir(self):
        reg = CapabilityRegistry(card_dir=None)
        assert reg.load_from_dir() == 0

    def test_load_from_dir_nonexistent(self, tmp_path):
        reg = CapabilityRegistry(card_dir=tmp_path / "nonexistent")
        assert reg.load_from_dir() == 0

    def test_load_from_dir_skips_invalid_yaml(self, tmp_path):
        bad_file = tmp_path / "bad.yaml"
        bad_file.write_text("{{invalid yaml", encoding="utf-8")
        good_data = {
            "capability_id": "good-card",
            "name": "Good",
            "category": "infra",
            "description": "good",
        }
        good_file = tmp_path / "good-card.yaml"
        good_file.write_text(yaml.dump(good_data, allow_unicode=True), encoding="utf-8")

        reg = CapabilityRegistry(card_dir=tmp_path)
        count = reg.load_from_dir()
        assert count == 1
        assert reg.get("good-card") is not None

    def test_load_from_dir_no_duplicate(self, tmp_path):
        card_data = {
            "capability_id": "dup-card",
            "name": "Dup",
            "category": "infra",
            "description": "dup",
        }
        yaml_file = tmp_path / "dup-card.yaml"
        yaml_file.write_text(yaml.dump(card_data, allow_unicode=True), encoding="utf-8")

        reg = CapabilityRegistry(card_dir=tmp_path)
        reg.register(_make_card("dup-card", name="Dup"))
        count = reg.load_from_dir()
        assert count == 1
        assert reg.count() == 1


class TestCapabilityRegistryCount:
    def test_count_empty(self, tmp_path):
        reg = CapabilityRegistry(card_dir=tmp_path)
        assert reg.count() == 0

    def test_count_after_register(self, tmp_path):
        reg = CapabilityRegistry(card_dir=tmp_path)
        reg.register(_make_card("c1"))
        reg.register(_make_card("c2"))
        assert reg.count() == 2
