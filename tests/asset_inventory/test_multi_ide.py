# [A_test] module_id: SRC-TST-0077 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-235 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.asset_inventory.test_multi_ide
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""Tests for MOD-INF-026 §24 Multi-IDE module."""

from pathlib import Path

from zephyr.infrastructure.asset_inventory.metadata import MultiIDERuleGenerator
from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）


class TestMultiIDERuleGenerator:
    def test_constructor(self) -> None:
        gen = MultiIDERuleGenerator(REPO_ROOT)
        assert gen._root

    def test_generate_cursor_rules(self, tmp_path) -> None:
        gen = MultiIDERuleGenerator(REPO_ROOT)
        output = gen.generate_cursor_rules(tmp_path / ".cursorrules")
        assert output.exists()
        content = output.read_text(encoding="utf-8")
        assert "ZephyrAlpha" in content
        assert "cursor" in content.lower()

    def test_generate_trae_rules(self, tmp_path) -> None:
        gen = MultiIDERuleGenerator(REPO_ROOT)
        output = gen.generate_trae_rules(tmp_path / ".trae" / "rules" / "asset_inventory_rules.md")
        assert output.exists()
        content = output.read_text(encoding="utf-8")
        assert "ZephyrAlpha" in content
        assert "trae" in content.lower()

    def test_generate_vscode_rules(self, tmp_path) -> None:
        gen = MultiIDERuleGenerator(REPO_ROOT)
        output = gen.generate_vscode_rules(tmp_path / ".github" / "copilot-instructions.md")
        assert output.exists()
        content = output.read_text(encoding="utf-8")
        assert "ZephyrAlpha" in content
        assert "copilot" in content.lower()

    def test_generate_jetbrains_rules(self, tmp_path) -> None:
        gen = MultiIDERuleGenerator(REPO_ROOT)
        output = gen.generate_jetbrains_rules(tmp_path / ".idea" / "asset-inventory.xml")
        assert output.exists()
        content = output.read_text(encoding="utf-8")
        assert "ZephyrAlpha" in content
        assert "AssetInventoryRules" in content
        assert content.startswith("<?xml")

    def test_generate_all(self, tmp_path) -> None:
        gen = MultiIDERuleGenerator(tmp_path)
        results = gen.generate_all()
        assert "cursor" in results
        assert "trae" in results
        assert "vscode" in results
        assert "jetbrains" in results
        for name, path in results.items():
            assert path.exists(), f"{name} rule file not created"
