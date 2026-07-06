# [A_test] module_id: SRC-TST-0084 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-242 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.asset_inventory.test_trust_anchor
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""Tests for MOD-INF-026 §26 Trust Anchor module."""

from datetime import datetime
from pathlib import Path

from zephyr.infrastructure.asset_inventory.trust_anchor import (
    TripleTrustAnchorGate,
    TrustAnchorResult,
    TrustLevel,
)
from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）


class TestTrustLevel:
    def test_values(self) -> None:
        assert TrustLevel.FULL == "FULL"
        assert TrustLevel.PARTIAL == "PARTIAL"
        assert TrustLevel.BROKEN == "BROKEN"

    def test_comparison(self) -> None:
        assert TrustLevel.FULL != TrustLevel.BROKEN


class TestTrustAnchorResult:
    def test_defaults(self) -> None:
        r = TrustAnchorResult()
        assert not r.git_ok
        assert r.trust_level == TrustLevel.BROKEN

    def test_checked_at_auto(self) -> None:
        r = TrustAnchorResult()
        assert isinstance(r.checked_at, datetime)


class TestTripleTrustAnchorGate:
    def test_constructor(self) -> None:
        gate = TripleTrustAnchorGate(REPO_ROOT)
        assert gate._root

    def test_calculate_trust_full(self) -> None:
        assert TripleTrustAnchorGate._calculate_trust({"git_ok": True, "test_ok": True, "audit_ok": True}) == TrustLevel.FULL

    def test_calculate_trust_partial(self) -> None:
        assert TripleTrustAnchorGate._calculate_trust({"git_ok": True, "test_ok": True, "audit_ok": False}) == TrustLevel.PARTIAL

    def test_calculate_trust_broken(self) -> None:
        assert TripleTrustAnchorGate._calculate_trust({"git_ok": False, "test_ok": False, "audit_ok": True}) == TrustLevel.BROKEN

    def test_recommend_full(self) -> None:
        msg = TripleTrustAnchorGate._recommend(TrustLevel.FULL)
        assert "完全可信" in msg

    def test_recommend_broken(self) -> None:
        msg = TripleTrustAnchorGate._recommend(TrustLevel.BROKEN)
        assert "不可信" in msg

    def test_verify_returns_result(self) -> None:
        gate = TripleTrustAnchorGate(REPO_ROOT)
        result = gate.verify()
        assert isinstance(result, TrustAnchorResult)
        assert result.trust_level in (TrustLevel.FULL, TrustLevel.PARTIAL, TrustLevel.BROKEN)

    def test_cache_returns_same(self) -> None:
        gate = TripleTrustAnchorGate(REPO_ROOT)
        r1 = gate.verify()
        r2 = gate.verify()
        assert r1.checked_at == r2.checked_at
