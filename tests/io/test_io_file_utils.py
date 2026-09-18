# [A_test] module_id: MOD-GOV_io_file_utils | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §testing

# [MODULE] tests.test_io_file_utils

# [INVARIANTS] atomic_write原子性;safe_read校验SHA-256;backup_and_rollback异常回滚

# [MODIFY-GUARD] file_utils.py变更时同步更新

# [CONSUMERS] CI

# [STABILITY] stable

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] AtomicWriteError

# [TESTS] pytest tests/test_io_file_utils.py -q
# [TTL] task_bound

import hashlib
from pathlib import Path

import pytest

from zephyr.shared.io.file_utils import (
    ATOMIC_TMP_PREFIX_TEMPLATE,
    ATOMIC_TMP_RAND_LEN,
    ATOMIC_TMP_SUFFIX,
    AtomicWriteError,
    atomic_tmp_glob,
    atomic_tmp_to_canonical,
    atomic_write,
    backup_and_rollback,
    backup_file,
    restore_backup,
    safe_read,
)


class TestAtomicWrite:
    def test_creates_file(self, tmp_path):
        target = tmp_path / "test.txt"
        atomic_write(target, "hello world")
        assert target.read_text(encoding="utf-8") == "hello world"

    def test_overwrites_existing(self, tmp_path):
        target = tmp_path / "test.txt"
        atomic_write(target, "first")
        atomic_write(target, "second")
        assert target.read_text(encoding="utf-8") == "second"

    def test_creates_parent_dirs(self, tmp_path):
        target = tmp_path / "sub" / "dir" / "test.txt"
        atomic_write(target, "nested")
        assert target.read_text(encoding="utf-8") == "nested"

    def test_with_auto_backup(self, tmp_path):
        target = tmp_path / "test.txt"
        atomic_write(target, "original")
        atomic_write(target, "updated", auto_backup=True)
        assert target.read_text(encoding="utf-8") == "updated"
        bak_files = list(tmp_path.glob("test.txt.bak.*"))
        assert len(bak_files) >= 1

    def test_returns_path(self, tmp_path):
        target = tmp_path / "test.txt"
        result = atomic_write(target, "content")
        assert result == target

    def test_utf8_encoding(self, tmp_path):
        target = tmp_path / "test.txt"
        atomic_write(target, "中文内容 🎉")
        assert target.read_text(encoding="utf-8") == "中文内容 🎉"


class TestSafeRead:
    def test_reads_content(self, tmp_path):
        target = tmp_path / "test.txt"
        target.write_text("hello", encoding="utf-8")
        content = safe_read(target)
        assert content == "hello"

    def test_sha256_verification_pass(self, tmp_path):
        target = tmp_path / "test.txt"
        target.write_text("verify", encoding="utf-8")
        sha = hashlib.sha256(b"verify").hexdigest()
        content = safe_read(target, verify_sha256=sha)
        assert content == "verify"

    def test_sha256_verification_fail(self, tmp_path):
        target = tmp_path / "test.txt"
        target.write_text("verify", encoding="utf-8")
        with pytest.raises(ValueError, match="SHA-256 mismatch"):
            safe_read(target, verify_sha256="badhash")

    def test_file_not_found(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            safe_read(tmp_path / "nonexistent.txt")


class TestBackupFile:
    def test_creates_backup(self, tmp_path):
        target = tmp_path / "test.txt"
        target.write_text("content", encoding="utf-8")
        bak = backup_file(target)
        assert bak is not None
        assert bak.exists()
        assert bak.read_text(encoding="utf-8") == "content"

    def test_nonexistent_returns_none(self, tmp_path):
        result = backup_file(tmp_path / "nonexistent.txt")
        assert result is None

    def test_max_backups_cleanup(self, tmp_path):
        target = tmp_path / "test.txt"
        for i in range(7):
            target.write_text(f"version-{i}", encoding="utf-8")
            backup_file(target, max_backups=3)
        bak_files = sorted(tmp_path.glob("test.txt.bak.*"))
        assert len(bak_files) <= 3


class TestRestoreBackup:
    def test_restore(self, tmp_path):
        target = tmp_path / "test.txt"
        target.write_text("original", encoding="utf-8")
        backup_file(target)
        target.write_text("modified", encoding="utf-8")
        restore_backup(target)
        assert target.read_text(encoding="utf-8") == "original"

    def test_missing_backup_raises(self, tmp_path):
        target = tmp_path / "test.txt"
        with pytest.raises(FileNotFoundError, match="Backup not found"):
            restore_backup(target)


class TestBackupAndRollback:
    def test_success_no_rollback(self, tmp_path):
        target = tmp_path / "test.txt"
        target.write_text("original", encoding="utf-8")
        with backup_and_rollback(target) as path:
            atomic_write(path, "modified")
        assert target.read_text(encoding="utf-8") == "modified"

    def test_exception_triggers_rollback(self, tmp_path):
        target = tmp_path / "test.txt"
        target.write_text("original", encoding="utf-8")
        with pytest.raises(RuntimeError), backup_and_rollback(target) as path:
            atomic_write(path, "modified")
            raise RuntimeError("fail")
        assert target.read_text(encoding="utf-8") == "original"


class TestAtomicWriteError:
    def test_inherits_os_error(self):
        assert issubclass(AtomicWriteError, OSError)


class TestAtomicTmpNamingSSOT:
    """.tmp 半成品命名的真源锁：命名 pattern 与反解析必须由 file_utils 单点导出。

    红证：改坏 ATOMIC_TMP_RAND_LEN（或把反解改成 rsplit("_")）⇒ 第 1/2 条即失败。
    清扫脚本侧的"复用同一函数对象"恒等锁随其换源改动同批落地（本批只出真源）。
    """

    def test_glob_is_derived_from_constants(self):
        assert atomic_tmp_glob("x.yaml") == ".x.yaml_" + "?" * ATOMIC_TMP_RAND_LEN + ATOMIC_TMP_SUFFIX
        assert atomic_tmp_glob() == ".*_" + "?" * ATOMIC_TMP_RAND_LEN + ATOMIC_TMP_SUFFIX

    def test_mkstemp_produced_name_round_trips(self, tmp_path):
        import fnmatch
        import os
        import tempfile

        target_name = "probe_registry.yaml"
        fd, made = tempfile.mkstemp(
            suffix=ATOMIC_TMP_SUFFIX,
            prefix=ATOMIC_TMP_PREFIX_TEMPLATE.format(name=target_name),
            dir=str(tmp_path),
        )
        os.close(fd)
        name = Path(made).name
        try:
            assert fnmatch.fnmatch(name, atomic_tmp_glob())
            assert atomic_tmp_to_canonical(name) == target_name
        finally:
            Path(made).unlink()

    def test_human_named_tmp_is_not_matched(self):
        # tempfile 随机表含下划线 ⇒ 只能按定长剥尾；人工命名不得被当成本半成品族
        import fnmatch

        assert not fnmatch.fnmatch(".foo_bar.tmp", atomic_tmp_glob())
