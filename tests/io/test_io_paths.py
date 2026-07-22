# [A_test] module_id: MOD-GOV_io_paths | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §testing

# [MODULE] tests.test_io_paths

# [INVARIANTS] REPO_ROOT包含src/zephyr/integration/zephyr/__init__.py;DB_DIR是REPO_ROOT/data;GATES_DIR存在

# [MODIFY-GUARD] paths.py变更时同步更新

# [CONSUMERS] CI

# [STABILITY] stable

# [SAFETY] L

# [AI_AUTONOMY] human_gated

# [ERROR_CONTRACT] FileNotFoundError

# [TESTS] pytest tests/test_io_paths.py -q
# [TTL] task_bound

from pathlib import Path

from zephyr.shared.io.paths import (
    DB_DIR,
    DB_PATH,
    GATES_DIR,
    MODELS_CACHE_DIR,
    RATIONALE_LOG_PATH,
    REPO_ROOT,
    SNAPSHOTS_DIR,
    VECTOR_INDEX_DIR,
    find_repo_root,
)


class TestFindRepoRoot:
    def test_returns_path(self):
        root = find_repo_root()
        assert isinstance(root, Path)

    def test_root_contains_src_zephyr(self):
        root = find_repo_root()
        assert (root / "src" / "zephyr" / "__init__.py").exists()

    def test_is_absolute(self):
        root = find_repo_root()
        assert root.is_absolute()


class TestRepoRoot:
    def test_is_path(self):
        assert isinstance(REPO_ROOT, Path)

    def test_contains_src(self):
        assert (REPO_ROOT / "src").exists()

    def test_contains_zephyr(self):
        assert (REPO_ROOT / "src" / "zephyr").exists()


class TestDbDir:
    def test_is_under_root(self):
        assert DB_DIR == REPO_ROOT / "data"

    def test_is_path(self):
        assert isinstance(DB_DIR, Path)


class TestDbPath:
    def test_is_path(self):
        assert isinstance(DB_PATH, Path)

    def test_under_data_dir(self):
        assert DB_PATH.parent == DB_DIR


class TestGatesDir:
    def test_is_under_root(self):
        assert GATES_DIR == REPO_ROOT / "src" / "zephyr" / "gates"

    def test_is_path(self):
        assert isinstance(GATES_DIR, Path)


class TestSnapshotsDir:
    def test_is_path(self):
        assert isinstance(SNAPSHOTS_DIR, Path)


class TestRationaleLogPath:
    def test_is_path(self):
        assert isinstance(RATIONALE_LOG_PATH, Path)

    def test_has_md_extension(self):
        assert RATIONALE_LOG_PATH.suffix == ".md"


class TestVectorIndexDir:
    def test_is_path(self):
        assert isinstance(VECTOR_INDEX_DIR, Path)


class TestModelsCacheDir:
    def test_is_path(self):
        assert isinstance(MODELS_CACHE_DIR, Path)
