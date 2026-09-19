# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_domain_shared/algo_flow/io/file_utils.yaml | §test
# [TTL] permanent
# [MODULE] tests.shared.io.test_file_utils_atomic_retry
# [TESTS] src/zephyr/shared/io/file_utils.py
"""MOD-INF-016 单元测试：atomic_write 写入端瞬时锁退避重试（裁定#343 治本）。

病根：Windows AV/索引器瞬时共享锁 → os.replace/unlink 立即 PermissionError
→ .tmp 残留。本文件只验证 replace/tmp 清理两处韧性退避；CAS 语义（stale
拒写/回读校验）真源覆盖在 tests/shared/test_safe_write.py，此处不重复。
锁场景用注入替身（可移植）+ 一条 Windows 真句柄集成用例，不触网不触生产路径。
"""

from __future__ import annotations

import logging
import os
import threading
from pathlib import Path

import pytest

import zephyr.shared.io.file_utils as fu


def _make_perm_error(winerror: int = 32) -> PermissionError:
    return PermissionError(winerror, "transient lock (AV/indexer)")


class FlakyReplace:
    """前 fail_times 次抛瞬时锁，之后放行真 os.replace。"""

    def __init__(self, real: object, fail_times: int) -> None:
        self._real = real
        self._fail_times = fail_times
        self.calls = 0

    def __call__(self, src: object, dst: object) -> None:
        self.calls += 1
        if self.calls <= self._fail_times:
            raise _make_perm_error(32)
        self._real(src, dst)  # type: ignore[operator]


@pytest.fixture()
def fast_retry(monkeypatch: pytest.MonkeyPatch) -> list[float]:
    """替换模块内 sleep 为无延迟替身（file_utils 仅两处 helper 使用 sleep）。"""
    sleeps: list[float] = []
    monkeypatch.setattr(fu, "sleep", sleeps.append)
    return sleeps


@pytest.fixture()
def always_transient(monkeypatch: pytest.MonkeyPatch) -> None:
    """POSIX 上也让替身 PermissionError 被判为瞬时锁（纯逻辑测试可移植）。"""
    monkeypatch.setattr(fu, "_is_transient_lock_error", lambda exc: True)


def test_replace_retry_succeeds_zero_residual(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    fast_retry: list[float],
    always_transient: None,
) -> None:
    """前 2 次锁 → 第 3 次成功：写入生效、按短退避重试、tmp 零残留。"""
    target = tmp_path / "reg.yaml"
    target.write_text("old", encoding="utf-8")
    flaky = FlakyReplace(os.replace, fail_times=2)
    monkeypatch.setattr(os, "replace", flaky)

    out = fu.atomic_write(target, "new-content")

    assert out.read_text(encoding="utf-8") == "new-content"
    assert flaky.calls == 3
    assert fast_retry == [0.2, 0.5]
    assert not list(tmp_path.glob("*.tmp"))


def test_replace_retry_exhausted_raises_and_cleans_tmp(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    fast_retry: list[float],
    always_transient: None,
) -> None:
    """重试耗尽：仍按既有语义抛 AtomicWriteError；tmp 未被锁故清理成功零残留。"""
    target = tmp_path / "reg.yaml"
    calls = {"n": 0}

    def always_locked(src: object, dst: object) -> None:
        calls["n"] += 1
        raise _make_perm_error(32)

    monkeypatch.setattr(os, "replace", always_locked)

    with pytest.raises(fu.AtomicWriteError):
        fu.atomic_write(target, "new-content")

    assert calls["n"] == len(fu.ATOMIC_REPLACE_RETRY_DELAYS) + 1
    assert not list(tmp_path.glob("*.tmp"))


def test_tmp_cleanup_exhausted_warns_and_keeps_tmp(
    tmp_path: Path,
    fast_retry: list[float],
    always_transient: None,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """tmp 清理也被锁：退避重试耗尽 → 留 tmp + warning，不掩盖原异常（不抛）。"""

    class LockedTmp:
        def __init__(self) -> None:
            self.unlink_calls = 0

        def exists(self) -> bool:
            return True

        def unlink(self, missing_ok: bool = False) -> None:
            self.unlink_calls += 1
            raise _make_perm_error(32)

    locked = LockedTmp()
    with caplog.at_level(logging.WARNING, logger="zephyr.shared.io.file_utils"):
        fu._cleanup_tmp_with_retry(locked)  # type: ignore[arg-type]

    assert locked.unlink_calls == len(fu.ATOMIC_TMP_CLEANUP_RETRY_DELAYS) + 1
    assert any("残留" in rec.message for rec in caplog.records)


@pytest.mark.skipif(os.name != "nt", reason="WinError 瞬时锁判定仅 Windows 有意义")
def test_is_transient_lock_error_windows_semantics() -> None:
    def with_winerror(winerror: int) -> PermissionError:
        # 构造器不产 winerror（仅 OS 抛出时携带）——手动挂属性模拟真实形态
        exc = PermissionError(13, "synthetic")
        exc.winerror = winerror  # type: ignore[attr-defined]
        return exc

    assert fu._is_transient_lock_error(with_winerror(32)) is True
    assert fu._is_transient_lock_error(with_winerror(5)) is True
    assert fu._is_transient_lock_error(with_winerror(33)) is True
    assert fu._is_transient_lock_error(with_winerror(2)) is False
    # 无 winerror 的 Windows PermissionError（非 API 来源）按瞬时疑锁保守重试
    assert fu._is_transient_lock_error(PermissionError(13, "no winerror attr")) is True
    assert fu._is_transient_lock_error(ValueError("not os error")) is False


@pytest.mark.skipif(os.name != "nt", reason="真独占句柄锁模拟依赖 Windows 共享语义")
def test_real_transient_lock_retry_success_zero_residual(tmp_path: Path) -> None:
    """真句柄集成用例：独占句柄 0.35s 后释放 → atomic_write 重试穿透，零残留。"""
    target = tmp_path / "reg.yaml"
    target.write_text("old", encoding="utf-8")
    fh = open(target, "rb")  # noqa: SIM115 — Windows 无 FILE_SHARE_DELETE，replace 即被锁
    threading.Timer(0.35, fh.close).start()
    try:
        out = fu.atomic_write(target, "new-content")
        assert out.read_text(encoding="utf-8") == "new-content"
    finally:
        if not fh.closed:
            fh.close()
    assert not list(tmp_path.glob("*.tmp"))
