# [A_test] module_id: SRC-TST-0315 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md | §
# [MODULE] tests.test_annotations
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
import pytest

from zephyr.governance import annotations as ann_mod
from zephyr.gov_code_quality.code_dedup.annotations import (
    get_known_duplicates,
    get_shared_registry,
    intentional,
    known_dup,
    shared,
)


@pytest.fixture
def clean_registry():
    ann_mod.SHARED_FUNCTIONS.clear()
    ann_mod.KNOWN_DUPLICATES.clear()
    ann_mod.INTENTIONAL_DUPLICATES.clear()
    yield
    ann_mod.SHARED_FUNCTIONS.clear()
    ann_mod.KNOWN_DUPLICATES.clear()
    ann_mod.INTENTIONAL_DUPLICATES.clear()


class TestAnnotations:
    def test_shared_decorator_registers_function(self, clean_registry):
        @shared(module="test_mod")
        def my_func():
            return 42

        assert "test_mod::my_func" in get_shared_registry()

    def test_known_dup_decorator_registers(self, clean_registry):
        @known_dup(group_id="grp-1", confidence=0.9)
        def dup_func():
            return 1

        assert "grp-1" in get_known_duplicates()
        assert "dup_func" in get_known_duplicates()["grp-1"]

    def test_intentional_decorator_registers(self, clean_registry):
        @intentional(reason="design pattern")
        def int_func():
            return 2

        assert "int_func" in ann_mod.INTENTIONAL_DUPLICATES

    def test_get_shared_registry_returns_dict(self, clean_registry):
        reg = get_shared_registry()
        assert isinstance(reg, dict)

    def test_get_known_duplicates_returns_dict(self, clean_registry):
        dups = get_known_duplicates()
        assert isinstance(dups, dict)
