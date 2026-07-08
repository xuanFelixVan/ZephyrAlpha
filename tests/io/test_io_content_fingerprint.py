# [A_test] module_id: SRC-TST-1151 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §testing

# [MODULE] tests.test_io_content_fingerprint

# [INVARIANTS] SHA-256确定性;FileNotFoundError→FingerprintNotFoundError;bulk跳过错误

# [MODIFY-GUARD] content_fingerprint.py变更时同步更新

# [CONSUMERS] CI

# [STABILITY] stable

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] FingerprintNotFoundError;FingerprintPermissionError

# [TESTS] pytest tests/test_io_content_fingerprint.py -q
# [TTL] task_bound


import pytest

from zephyr.shared.io.content_fingerprint import (
    FingerprintError,
    FingerprintNotFoundError,
    compute_bulk,
    compute_hash,
    verify_hash,
)


class TestComputeHash:
    def test_deterministic(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("hello world", encoding="utf-8")
        h1 = compute_hash(f)
        h2 = compute_hash(f)
        assert h1 == h2

    def test_sha256_length(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("content", encoding="utf-8")
        h = compute_hash(f)
        assert len(h) == 64

    def test_different_content_different_hash(self, tmp_path):
        f1 = tmp_path / "a.txt"
        f2 = tmp_path / "b.txt"
        f1.write_text("aaa", encoding="utf-8")
        f2.write_text("bbb", encoding="utf-8")
        assert compute_hash(f1) != compute_hash(f2)

    def test_file_not_found(self):
        with pytest.raises(FingerprintNotFoundError):
            compute_hash("/nonexistent/path/file.txt")

    def test_accepts_string_path(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("ok", encoding="utf-8")
        h = compute_hash(str(f))
        assert len(h) == 64


class TestVerifyHash:
    def test_correct_hash(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("verify me", encoding="utf-8")
        h = compute_hash(f)
        assert verify_hash(f, h) is True

    def test_wrong_hash(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("verify me", encoding="utf-8")
        assert verify_hash(f, "0000000000000000") is False

    def test_case_insensitive(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("data", encoding="utf-8")
        h = compute_hash(f)
        assert verify_hash(f, h.upper()) is True


class TestComputeBulk:
    def test_multiple_files(self, tmp_path):
        f1 = tmp_path / "a.txt"
        f2 = tmp_path / "b.txt"
        f1.write_text("aaa", encoding="utf-8")
        f2.write_text("bbb", encoding="utf-8")
        results = compute_bulk([f1, f2])
        assert results[str(f1)] is not None
        assert results[str(f2)] is not None

    def test_missing_file_returns_none(self, tmp_path):
        f1 = tmp_path / "exists.txt"
        f1.write_text("ok", encoding="utf-8")
        f2 = tmp_path / "missing.txt"
        results = compute_bulk([f1, f2])
        assert results[str(f1)] is not None
        assert results[str(f2)] is None


class TestFingerprintErrors:
    def test_not_found_inherits_base(self):
        assert issubclass(FingerprintNotFoundError, FingerprintError)

    def test_base_inherits_exception(self):
        assert issubclass(FingerprintError, Exception)
