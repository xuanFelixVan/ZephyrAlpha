# [A_test] module_id: SRC-TST-1186 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain-autonomy_core/agent-rbac/blueprint.md | §tests
# [MODULE] zephyr.security.access_control.key_hierarchy
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self

import sys

sys.path.insert(0, "src")

import pytest

try:
    from zephyr.security.access_control.key_hierarchy import KeyHierarchy
except Exception as exc:
    pytest.skip(f"Cannot import key_hierarchy: {exc}", allow_module_level=True)


class TestKeyHierarchy:
    def test_generate_root(self):
        kh = KeyHierarchy()
        root = kh.generate_root()
        assert root.startswith("ROOT-")
        assert len(root) > 10

    def test_derive_from_root(self):
        kh = KeyHierarchy()
        kh.generate_root()
        signing = kh.derive("SIGNING", "ROOT")
        assert len(signing) == 32
        assert signing != kh.get("ROOT")

    def test_derive_missing_parent(self):
        kh = KeyHierarchy()
        with pytest.raises(ValueError, match="Parent key"):
            kh.derive("SIGNING", "ROOT")

    def test_derive_invalid_level(self):
        kh = KeyHierarchy()
        kh.generate_root()
        with pytest.raises(ValueError, match="Unknown level"):
            kh.derive("INVALID", "ROOT")

    def test_get_missing_key(self):
        kh = KeyHierarchy()
        assert kh.get("ROOT") is None

    def test_get_existing_key(self):
        kh = KeyHierarchy()
        kh.generate_root()
        assert kh.get("ROOT") is not None

    def test_verify_chain_empty(self):
        kh = KeyHierarchy()
        result = kh.verify_chain()
        assert result["intact"] is False
        assert len(result["issues"]) == 4

    def test_verify_chain_partial(self):
        kh = KeyHierarchy()
        kh.generate_root()
        result = kh.verify_chain()
        assert result["intact"] is False
        assert result["levels_present"] == 1

    def test_verify_chain_full(self):
        kh = KeyHierarchy()
        kh.generate_root()
        kh.derive("SIGNING", "ROOT")
        kh.derive("TRANSPORT", "SIGNING")
        kh.derive("AUDIT", "TRANSPORT")
        result = kh.verify_chain()
        assert result["intact"] is True
        assert result["levels_present"] == 4

    def test_levels_constant(self):
        assert KeyHierarchy.LEVELS == ["ROOT", "SIGNING", "TRANSPORT", "AUDIT"]

    def test_derive_produces_unique_keys(self):
        kh = KeyHierarchy()
        kh.generate_root()
        k1 = kh.derive("SIGNING", "ROOT")
        kh2 = KeyHierarchy()
        kh2.generate_root()
        k2 = kh2.derive("SIGNING", "ROOT")
        assert k1 != k2
