# [A_test] module_id: SRC-TST-0910 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md | §
# [MODULE] tests.test_file_creator
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
from zephyr.gov_code_quality.code_dedup.file_creator import FileCreator


class TestFileCreator:
    def test_instantiation_default(self):
        fc = FileCreator()
        assert fc is not None

    def test_instantiation_with_dirs(self, tmp_path):
        fc = FileCreator(
            package_dir=str(tmp_path / "pkg"),
            test_dir=str(tmp_path / "tests"),
            data_dir=str(tmp_path / "data"),
        )
        assert fc is not None

    def test_verify_all(self, tmp_path):
        fc = FileCreator(
            package_dir=str(tmp_path / "pkg"),
            test_dir=str(tmp_path / "tests"),
            data_dir=str(tmp_path / "data"),
        )
        result = fc.verify_all()
        assert isinstance(result, (list, dict))
