# [A_test] module_id: SRC-TST-1280 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md | §
# [MODULE] tests.test_mock_duplicate_generator
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
from zephyr.gov_code_quality.code_dedup.mock_duplicate_generator import (
    DuplicateType,
    GeneratedDuplicate,
    MockDuplicateGenerator,
)


class TestMockDuplicateGenerator:
    def test_instantiation(self):
        gen = MockDuplicateGenerator()
        assert gen is not None

    def test_generate_exact(self):
        gen = MockDuplicateGenerator()
        result = gen.generate(DuplicateType.EXACT)
        assert isinstance(result, GeneratedDuplicate)
        assert result.dup_type == DuplicateType.EXACT

    def test_generate_renamed(self):
        gen = MockDuplicateGenerator()
        result = gen.generate(DuplicateType.RENAMED)
        assert isinstance(result, GeneratedDuplicate)
        assert result.dup_type == DuplicateType.RENAMED

    def test_generate_reordered(self):
        gen = MockDuplicateGenerator()
        result = gen.generate(DuplicateType.REORDERED)
        assert isinstance(result, GeneratedDuplicate)

    def test_generate_near_miss(self):
        gen = MockDuplicateGenerator()
        result = gen.generate(DuplicateType.NEAR_MISS)
        assert isinstance(result, GeneratedDuplicate)

    def test_generate_appends_to_output(self):
        gen = MockDuplicateGenerator()
        gen.generate(DuplicateType.EXACT)
        gen.generate(DuplicateType.RENAMED)
        assert len(gen.output) == 2
