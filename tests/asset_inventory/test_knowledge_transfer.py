# [A_test] module_id: MOD-GOV_knowledge_transfer | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-232 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.asset_inventory.test_knowledge_transfer
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""Tests for MOD-INF-026 §30 Knowledge Transfer module."""

from pathlib import Path

from zephyr.infrastructure.asset_inventory.dashboard import KnowledgeTransferGate
from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）


class TestKnowledgeTransferGate:
    def test_constructor(self) -> None:
        gate = KnowledgeTransferGate(REPO_ROOT)
        assert gate.root

    def test_generate_summary(self) -> None:
        gate = KnowledgeTransferGate(REPO_ROOT)
        summary = gate.generate_summary()
        assert isinstance(summary, str)
        assert len(summary) > 0

    def test_write_handoff(self, tmp_path) -> None:
        gate = KnowledgeTransferGate(REPO_ROOT)
        path = gate.write_handoff(tmp_path / "_asset_handoff.txt")
        assert path.exists()
        content = path.read_text(encoding="utf-8")
        assert "ZephyrAlpha" in content
