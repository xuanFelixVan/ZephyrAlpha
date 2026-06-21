# [A_test] module_id: SRC-TST-1217 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-009 | docs/03_modules/_cross_layer/pipeline/blueprint.md | §
# [MODULE] tests.test_layer_consumer_registry
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] pytest tests/test_layer_consumer_registry.py

from __future__ import annotations

import pytest

from zephyr.integration.layer_consumer_registry import (
    _REGISTRY_DEFINITION,
    get_registry_summary,
    register_all_consumers,
    register_for_layer,
)
from zephyr.integration.layer_router import LayerDataRouter, LayerRouteMap, RouteEntry


_EMPTY_ROUTE_MAP = LayerRouteMap(
    routes=(),
    by_source={},
    by_target={},
    by_contract={},
    layers=tuple(f"l{i:02d}" for i in range(14)),
    loaded_at="",
    source_path="",
)


class TestRegistryDefinition:
    def test_has_expected_layer_keys(self):
        expected_keys = {f"l{i:02d}" for i in range(13)}
        actual_keys = set(_REGISTRY_DEFINITION.keys())
        assert actual_keys == expected_keys

    def test_each_value_is_list_of_tuples(self):
        for layer_id, entries in _REGISTRY_DEFINITION.items():
            assert isinstance(entries, list), f"{layer_id} value is not a list"
            for entry in entries:
                assert isinstance(entry, tuple), f"{layer_id} entry is not a tuple: {entry}"
                assert len(entry) == 2, f"{layer_id} entry does not have 2 elements: {entry}"
                assert isinstance(entry[0], str), f"{layer_id} contract_id is not str"

    def test_l13_not_in_registry(self):
        assert "l13" not in _REGISTRY_DEFINITION

    def test_l12_is_last_layer(self):
        assert "l12" in _REGISTRY_DEFINITION

    def test_l00_has_backpressure_contracts(self):
        l00_contracts = [cid for cid, _ in _REGISTRY_DEFINITION["l00"]]
        for cid in l00_contracts:
            assert cid.startswith("CTR-BP-"), f"l00 should only have BP contracts, got {cid}"

    def test_l05_is_largest_consumer(self):
        counts = {layer: len(entries) for layer, entries in _REGISTRY_DEFINITION.items()}
        assert counts["l05"] == max(counts.values()), "l05 should have the most consumers"


class TestRegisterAllConsumers:
    def test_returns_dict_with_counts(self):
        router = LayerDataRouter(route_map=_EMPTY_ROUTE_MAP)
        result = register_all_consumers(router)
        assert isinstance(result, dict)
        assert len(result) > 0
        for layer_id, count in result.items():
            assert isinstance(count, int)
            assert count >= 0

    def test_counts_match_registry_definition(self):
        router = LayerDataRouter(route_map=_EMPTY_ROUTE_MAP)
        result = register_all_consumers(router)
        for layer_id, count in result.items():
            assert count == len(_REGISTRY_DEFINITION[layer_id])

    def test_total_registered_equals_registry_total(self):
        router = LayerDataRouter(route_map=_EMPTY_ROUTE_MAP)
        result = register_all_consumers(router)
        total_registered = sum(result.values())
        total_expected = sum(len(v) for v in _REGISTRY_DEFINITION.values())
        assert total_registered == total_expected

    def test_with_none_router_uses_default(self):
        result = register_all_consumers(None)
        assert isinstance(result, dict)
        assert len(result) > 0


class TestRegisterForLayer:
    def test_known_layer_returns_count(self):
        router = LayerDataRouter(route_map=_EMPTY_ROUTE_MAP)
        count = register_for_layer(router, "l02")
        assert isinstance(count, int)
        assert count == len(_REGISTRY_DEFINITION["l02"])
        assert count > 0

    def test_unknown_layer_returns_zero(self):
        router = LayerDataRouter(route_map=_EMPTY_ROUTE_MAP)
        count = register_for_layer(router, "l99")
        assert count == 0

    def test_l05_registers_all_consumers(self):
        router = LayerDataRouter(route_map=_EMPTY_ROUTE_MAP)
        count = register_for_layer(router, "l05")
        assert count == len(_REGISTRY_DEFINITION["l05"])


class TestGetRegistrySummary:
    def test_returns_dict_with_required_keys(self):
        summary = get_registry_summary()
        assert "total_contracts_registered" in summary
        assert "total_layers" in summary
        assert "layers" in summary

    def test_total_contracts_registered(self):
        summary = get_registry_summary()
        expected = sum(len(v) for v in _REGISTRY_DEFINITION.values())
        assert summary["total_contracts_registered"] == expected

    def test_total_layers(self):
        summary = get_registry_summary()
        assert summary["total_layers"] == len(_REGISTRY_DEFINITION)

    def test_layers_dict_has_all_layer_ids(self):
        summary = get_registry_summary()
        for layer_id in _REGISTRY_DEFINITION:
            assert layer_id in summary["layers"]

    def test_layer_entry_has_breakdown(self):
        summary = get_registry_summary()
        for layer_id, info in summary["layers"].items():
            assert "total" in info
            assert "P0_data" in info
            assert "P1_extension" in info
            assert "error" in info
            assert "backpressure" in info
            assert info["total"] == info["P0_data"] + info["P1_extension"] + info["error"] + info["backpressure"]
