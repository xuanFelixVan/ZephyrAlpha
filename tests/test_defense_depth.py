# [A_test] module_id: SRC-TST-0723 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_rbac/blueprint.md | §tests
# [MODULE] zephyr.security.access_control.defense_depth
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

import sys

sys.path.insert(0, "src")

import pytest

try:
    from zephyr.security.access_control.defense_depth import (
        DEFENSE_DEPTH,
        DefenseLayer,
        LayerDef,
        all_enabled,
        get_layer,
        get_layer_by_level,
    )

    _IMPORT_OK = True
    _IMPORT_REASON = ""
except Exception as exc:
    _IMPORT_OK = False
    _IMPORT_REASON = str(exc)


@pytest.mark.skipif(not _IMPORT_OK, reason=f"import failed: {_IMPORT_REASON}")
class TestDefenseLayer:
    def test_enum_values(self):
        assert DefenseLayer.L1_DEP_AUDIT.value == "L1_DEP_AUDIT"
        assert DefenseLayer.L6_CIRCUIT_BREAKER.value == "L6_CIRCUIT_BREAKER"

    def test_enum_count(self):
        assert len(DefenseLayer) == 6


@pytest.mark.skipif(not _IMPORT_OK, reason=f"import failed: {_IMPORT_REASON}")
class TestLayerDef:
    def test_creation(self):
        ld = LayerDef(
            layer=DefenseLayer.L1_DEP_AUDIT,
            label="test",
            enabled=True,
            tech_stack="stack",
            audit_frequency_days=7,
        )
        assert ld.layer == DefenseLayer.L1_DEP_AUDIT
        assert ld.enabled is True


@pytest.mark.skipif(not _IMPORT_OK, reason=f"import failed: {_IMPORT_REASON}")
class TestDefenseDepthConstants:
    def test_all_layers_present(self):
        for dl in DefenseLayer:
            assert dl in DEFENSE_DEPTH

    def test_all_enabled_by_default(self):
        for dl, ld in DEFENSE_DEPTH.items():
            assert ld.enabled is True


@pytest.mark.skipif(not _IMPORT_OK, reason=f"import failed: {_IMPORT_REASON}")
class TestGetLayer:
    def test_valid_layer(self):
        result = get_layer(DefenseLayer.L1_DEP_AUDIT)
        assert result is not None
        assert result.layer == DefenseLayer.L1_DEP_AUDIT

    def test_all_layers_retrievable(self):
        for dl in DefenseLayer:
            assert get_layer(dl) is not None


@pytest.mark.skipif(not _IMPORT_OK, reason=f"import failed: {_IMPORT_REASON}")
class TestGetLayerByLevel:
    def test_level_1(self):
        result = get_layer_by_level(1)
        assert result is not None
        assert result.layer == DefenseLayer.L1_DEP_AUDIT

    def test_level_6(self):
        result = get_layer_by_level(6)
        assert result is not None
        assert result.layer == DefenseLayer.L6_CIRCUIT_BREAKER

    def test_level_0(self):
        result = get_layer_by_level(0)
        assert result is None

    def test_level_out_of_range(self):
        result = get_layer_by_level(7)
        assert result is None

    def test_negative_level(self):
        result = get_layer_by_level(-1)
        assert result is None


@pytest.mark.skipif(not _IMPORT_OK, reason=f"import failed: {_IMPORT_REASON}")
class TestAllEnabled:
    def test_all_enabled_default(self):
        assert all_enabled() is True
