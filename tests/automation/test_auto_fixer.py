# [A_test] module_id: SRC-TST-0375 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md | §
# [MODULE] tests.test_auto_fixer
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_auto_fixer.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.gov_code_quality.code_dedup.auto_fixer import (
    AutoFixer,
    FixLevel,
    FixParams,
    SafetyTier,
)


class TestSafetyTier:
    def test_values(self):
        assert SafetyTier.ALWAYS == "always"
        assert SafetyTier.REVIEW == "review"
        assert SafetyTier.NEVER == "never"

    def test_is_string_enum(self):
        assert isinstance(SafetyTier.ALWAYS, str)


class TestFixLevel:
    def test_values(self):
        assert FixLevel.TRIVIAL == "trivial"
        assert FixLevel.SIMPLE == "simple"
        assert FixLevel.MODERATE == "moderate"
        assert FixLevel.COMPLEX == "complex"


class TestFixParams:
    def test_default_values(self):
        fp = FixParams()
        assert fp.safety_tier == SafetyTier.ALWAYS
        assert fp.level == FixLevel.SIMPLE
        assert fp.caller_count == 7
        assert fp.blast_radius == 50
        assert fp.grandfather is False

    def test_custom_values(self):
        fp = FixParams(
            safety_tier=SafetyTier.REVIEW,
            level=FixLevel.COMPLEX,
            caller_count=3,
            blast_radius=10,
            grandfather=True,
        )
        assert fp.safety_tier == SafetyTier.REVIEW
        assert fp.level == FixLevel.COMPLEX


class TestAutoFixer:
    def test_instantiation_default(self):
        af = AutoFixer()
        assert af.fix_count == 0
        assert af.params.safety_tier == SafetyTier.ALWAYS

    def test_instantiation_custom_params(self):
        params = FixParams(level=FixLevel.COMPLEX, caller_count=3)
        af = AutoFixer(params=params)
        assert af.params.level == FixLevel.COMPLEX

    def test_can_fix_normal(self):
        af = AutoFixer()
        assert af.can_fix(similarity=0.95, caller_count=5, blast_radius=30, is_grandfathered=False) is True

    def test_can_fix_too_many_callers(self):
        af = AutoFixer()
        assert af.can_fix(similarity=0.95, caller_count=100, blast_radius=30, is_grandfathered=False) is False

    def test_can_fix_blast_radius_too_large(self):
        af = AutoFixer()
        assert af.can_fix(similarity=0.95, caller_count=5, blast_radius=100, is_grandfathered=False) is False

    def test_can_fix_grandfathered(self):
        af = AutoFixer(params=FixParams(grandfather=True))
        assert af.can_fix(similarity=0.95, caller_count=5, blast_radius=30, is_grandfathered=True) is False

    def test_can_fix_grandfathered_not_flagged(self):
        af = AutoFixer(params=FixParams(grandfather=True))
        assert af.can_fix(similarity=0.95, caller_count=5, blast_radius=30, is_grandfathered=False) is True

    def test_can_fix_complex_level_low_similarity(self):
        af = AutoFixer(params=FixParams(level=FixLevel.COMPLEX))
        assert af.can_fix(similarity=0.90, caller_count=5, blast_radius=30, is_grandfathered=False) is False

    def test_can_fix_complex_level_high_similarity(self):
        af = AutoFixer(params=FixParams(level=FixLevel.COMPLEX))
        assert af.can_fix(similarity=0.99, caller_count=5, blast_radius=30, is_grandfathered=False) is True

    def test_fix_success(self):
        af = AutoFixer()
        result = af.fix(
            source="a.py", target="b.py", similarity=0.95, caller_count=5, blast_radius=30, is_grandfathered=False
        )
        assert result["fixed"] is True
        assert result["source"] == "a.py"
        assert result["target"] == "b.py"
        assert af.fix_count == 1

    def test_fix_blocked(self):
        af = AutoFixer()
        result = af.fix(
            source="a.py", target="b.py", similarity=0.95, caller_count=100, blast_radius=30, is_grandfathered=False
        )
        assert result["fixed"] is False
        assert result["reason"] == "safety_constraint_blocked"
        assert af.fix_count == 0

    def test_fix_count_increments(self):
        af = AutoFixer()
        af.fix(source="a.py", target="b.py", similarity=0.95, caller_count=5, blast_radius=30, is_grandfathered=False)
        af.fix(source="c.py", target="d.py", similarity=0.95, caller_count=5, blast_radius=30, is_grandfathered=False)
        assert af.fix_count == 2

    def test_fix_returns_similarity(self):
        af = AutoFixer()
        result = af.fix(
            source="a.py", target="b.py", similarity=0.88, caller_count=5, blast_radius=30, is_grandfathered=False
        )
        assert result["similarity"] == 0.88
