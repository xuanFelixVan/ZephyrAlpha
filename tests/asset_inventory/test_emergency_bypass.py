# [A_test] module_id: SRC-TST-0071 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-229 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.asset_inventory.test_emergency_bypass
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""Tests for MOD-INF-026 §28 Emergency Bypass module."""

from pathlib import Path

from zephyr.infrastructure.asset_inventory.trust_anchor import BypassManager, BypassState
from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）


class TestBypassState:
    def test_defaults(self) -> None:
        s = BypassState()
        assert not s.enabled
        assert not s.is_expired

    def test_expired(self) -> None:
        s = BypassState(is_expired=True)
        assert s.is_expired


class TestBypassManager:
    def test_constructor(self) -> None:
        bm = BypassManager(REPO_ROOT)
        assert bm._override_path

    def test_not_bypass_when_no_file(self, tmp_path) -> None:
        bm = BypassManager(tmp_path)
        assert not bm.is_bypass_active()

    def test_write_and_remove_override(self, tmp_path) -> None:
        bm = BypassManager(tmp_path)
        path = bm.write_override("testing", "test-session", hours=1)
        assert path.exists()
        assert path.name == "inventory_override.yaml"

        removed = bm.remove_override()
        assert removed
        assert not path.exists()

    def test_get_bypass_state_active_after_write(self, tmp_path) -> None:
        bm = BypassManager(tmp_path)
        bm.write_override("testing", "test", hours=1)
        state = bm.get_bypass_state()
        assert state.enabled

    def test_is_bypass_active_after_write(self, tmp_path) -> None:
        bm = BypassManager(tmp_path)
        bm.write_override("testing", "test", hours=1)
        assert bm.is_bypass_active()
