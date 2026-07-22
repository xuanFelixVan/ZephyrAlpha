# [A_test] module_id: MOD-GOV_memory_bank_root | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_cross_layer/context_engine/blueprint.md | §tests
# [MODULE] zephyr.autonomy_core.memory_bank
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
    from zephyr.autonomy_core.context.memory_bank import BANK_FILES, MemoryBank
except Exception as _exc:
    pytestmark = pytest.mark.skip(reason=f"import failed: {_exc}")


class TestMemoryBank:
    def test_init_creates_bank_files(self, tmp_path):
        bank = MemoryBank(root_dir=str(tmp_path / "mb"))
        for fname in BANK_FILES:
            assert (bank.root_dir / fname).exists()

    def test_write_and_read_section(self, tmp_path):
        bank = MemoryBank(root_dir=str(tmp_path / "mb"))
        bank.write_section("decision_log", "KBG-001", "Approved ONNX int8")
        content = bank.read_file("decision_log")
        assert "KBG-001" in content
        assert "Approved ONNX int8" in content

    def test_write_section_with_md_extension(self, tmp_path):
        bank = MemoryBank(root_dir=str(tmp_path / "mb"))
        bank.write_section("decision_log.md", "KBG-002", "Use Redis")
        content = bank.read_file("decision_log.md")
        assert "KBG-002" in content

    def test_list_all_returns_all_files(self, tmp_path):
        bank = MemoryBank(root_dir=str(tmp_path / "mb"))
        listing = bank.list_all()
        assert len(listing) == len(BANK_FILES)
        for fname in BANK_FILES:
            key = fname.replace(".md", "")
            assert key in listing
            assert listing[key] > 0

    def test_export_json(self, tmp_path):
        bank = MemoryBank(root_dir=str(tmp_path / "mb"))
        bank.write_section("active_context", "Task-1", "In progress")
        exported = bank.export_json()
        assert "active_context" in exported
        assert "Task-1" in exported["active_context"]

    def test_validate_filename_invalid(self):
        with pytest.raises(ValueError, match="Invalid bank file"):
            MemoryBank._validate_filename("nonexistent_file")

    def test_validate_filename_valid_without_extension(self):
        MemoryBank._validate_filename("decision_log")

    def test_validate_filename_valid_with_extension(self):
        MemoryBank._validate_filename("decision_log.md")

    def test_root_dir_property(self, tmp_path):
        bank = MemoryBank(root_dir=str(tmp_path / "mb"))
        assert bank.root_dir.exists()
        assert bank.root_dir.is_dir()

    def test_read_file_non_bank_raises(self, tmp_path):
        bank = MemoryBank(root_dir=str(tmp_path / "mb"))
        with pytest.raises(ValueError):
            bank.read_file("invalid_file")

    def test_write_section_appends(self, tmp_path):
        bank = MemoryBank(root_dir=str(tmp_path / "mb"))
        bank.write_section("progress_tracker", "M1", "Done")
        bank.write_section("progress_tracker", "M2", "In progress")
        content = bank.read_file("progress_tracker")
        assert "M1" in content
        assert "M2" in content
