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
    MAIN_REPO_ROOT,
    MODELS_CACHE_DIR,
    RATIONALE_LOG_PATH,
    REPO_ROOT,
    SNAPSHOTS_DIR,
    VECTOR_INDEX_DIR,
    anchor_main_root,
    find_repo_root,
    is_session_worktree_root,
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

    def test_anchored_main_repo_root(self):
        """#ARCH-WORKTREE-DB-SPLIT-001：governance.db 锚定主仓根（worktree 进程
        与主仓进程读写同一份，消灭双副本分裂振荡）。主仓上下文 MAIN==REPO 等价。"""
        assert DB_PATH == MAIN_REPO_ROOT / "data" / "databases" / "governance.db"

    def test_parent_under_main_data_dir(self):
        assert DB_PATH.parent == MAIN_REPO_ROOT / "data" / "databases"


class TestSessionWorktreeAnchor:
    """is_session_worktree_root / anchor_main_root（父目录结构判定，嵌套 tmp 安全）。"""

    def test_real_worktree_root_detected(self, tmp_path):
        wt = tmp_path / ".worktrees" / "AI-X-001"
        wt.mkdir(parents=True)
        assert is_session_worktree_root(wt)
        assert anchor_main_root(wt) == tmp_path

    def test_aidrafts_root_detected(self, tmp_path):
        wt = tmp_path / ".aidrafts" / "sess-x"
        wt.mkdir(parents=True)
        assert is_session_worktree_root(wt)
        assert anchor_main_root(wt) == tmp_path

    def test_main_root_not_worktree(self, tmp_path):
        assert not is_session_worktree_root(tmp_path)
        assert anchor_main_root(tmp_path) == tmp_path

    def test_nested_tmp_repo_not_misjudged(self, tmp_path):
        """宿主 worktree 内嵌套 pytest tmp 库：段含 .worktrees 但父目录非之→不误判。"""
        host_wt = tmp_path / ".worktrees" / "AI-HOST"
        nested = host_wt / ".runtime" / "tmp" / "pytest_1" / "tmp_repo"
        nested.mkdir(parents=True)
        assert not is_session_worktree_root(nested)
        assert anchor_main_root(nested) == nested


class TestGatesDir:
    def test_is_under_root(self):
        # 断言对齐 paths.py 现状定义（真源 gov_enforcement/rule_enforcement）。
        # #61 裁定（2026-08-20）：孤儿值 governance/rule_enforcement 已由 AI-AUDIT11
        # 治本（6f1c2d71b4），本用例同步对齐并补 exists() 看守防第三次漂移。
        assert GATES_DIR == REPO_ROOT / "src" / "zephyr" / "gov_enforcement" / "rule_enforcement"
        assert GATES_DIR.exists()

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
