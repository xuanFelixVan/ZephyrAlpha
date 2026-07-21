# [A_test] module_id: MOD-GOV_memory_bank_context_engine | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-471 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.context_engine.test_memory_bank
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""Tests for memory_bank.py (TASK-014 beta c)."""

import tempfile

from zephyr.autonomy_core.context.memory_bank import BANK_FILES, MemoryBank


class TestMemoryBank:
    def test_create_creates_all_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            bank = MemoryBank(root_dir=tmpdir)
            listing = bank.list_all()
            for fname in BANK_FILES:
                key = fname.replace(".md", "")
                assert key in listing

    def test_read_write_section(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            bank = MemoryBank(root_dir=tmpdir)
            bank.write_section("decision_log", "ADR-TEST", "Test decision content")
            content = bank.read_file("decision_log")
            assert "ADR-TEST" in content
            assert "Test decision content" in content

    def test_invalid_filename(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            bank = MemoryBank(root_dir=tmpdir)
            try:
                bank.read_file("nonexistent.md")
                assert False, "Should have raised ValueError"
            except ValueError:
                pass

    def test_export_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            bank = MemoryBank(root_dir=tmpdir)
            bank.write_section("project_brief", "Test", "Hello")
            exported = bank.export_json()
            assert "project_brief" in exported
            assert "Hello" in exported["project_brief"]

    def test_list_all_sizes(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            bank = MemoryBank(root_dir=tmpdir)
            bank.write_section("active_context", "Section", "Content here")
            listing = bank.list_all()
            assert listing["active_context"] > 0
