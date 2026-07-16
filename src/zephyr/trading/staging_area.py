# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md
# [MODULE] zephyr.trading.staging_area
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.trading.__init__
# [CONSUMERS] zephyr.integration.mcp.task_manager_server; scripts/lock_files.py
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] draft files live under .aidrafts/; commit is atomic via os.replace; conflict detection via mtime+hash; cross-process lock via _CrossProcessLock (os.open O_CREAT|O_EXCL in .ailocks/); _COMMIT_LOCK (threading.Lock) 仅作进程内线程安全辅助锁，跨进程互斥由 _CrossProcessLock 负责
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] StagingError on all failures; CONFLICT raised when file modified by another session
# [TESTS] tests/test_staging_area.py
# [A_module] module_id=MOD-ORC_staging_area | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m10-time-trigger  M10豁免: _CrossProcessLock.__enter__的while True+time.sleep是跨进程文件锁获取等待循环,非周期触发(与_GlobalCommitLock同类)
"""
StagingArea — 多AI并发草稿写入+提交+冲突检测模块（CT-SESSION-CONFLICT-002）

设计原则
--------
- 草稿隔离：每个 AI session 写到 .aidrafts/{session_id}/ 下，互不干扰
- 提交时锁：草稿阶段不需要排他锁，提交时才获取锁+搬入
- 冲突检测：提交前对比原文件 mtime+hash，若已被其他 session 修改则返回 CONFLICT
- 自动合并：简单冲突（非重叠区域修改）自动 rebase；复杂冲突返回 CONFLICT_NEEDS_OWNER
- 原子写入：提交使用 temp-file + os.replace() 保证原子性

Usage::

    from zephyr.trading.staging_area import StagingArea

    sa = StagingArea(project_root="/path/to/project")
    sa.write_draft("session-001", "src/zephyr/foo.py", "new content")
    result = sa.commit("session-001", "src/zephyr/foo.py")
    if result.status == CommitStatus.OK:
        print("committed")
    elif result.status == CommitStatus.CONFLICT:
        print("conflict detected")
"""

from __future__ import annotations

__all__ = [
    "CommitResult",
    "CommitStatus",
    "ConflictInfo",
    "StagingArea",
    "StagingError",
]

import hashlib
import logging
import os
import random
import threading
import time
import uuid
from collections.abc import Sequence
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_COMMIT_LOCK = threading.Lock()  # 5.12.11 修复：仅进程内线程安全辅助锁；跨进程互斥由 _CrossProcessLock(os.open O_CREAT|O_EXCL) 负责


def _atomic_replace(tmp: Path, target: Path, max_retries: int = 5) -> None:
    base_delay = 0.01
    for attempt in range(max_retries):
        try:
            os.replace(tmp, target)
            return
        except PermissionError:
            if attempt == max_retries - 1:
                raise
            delay = base_delay * (2**attempt) + random.uniform(0, 0.01)
            time.sleep(delay)


class CommitStatus(str, Enum):
    OK = "OK"
    CONFLICT = "CONFLICT"
    CONFLICT_NEEDS_OWNER = "CONFLICT_NEEDS_OWNER"
    NO_DRAFT = "NO_DRAFT"
    MERGED = "MERGED"


class StagingError(RuntimeError):
    """StagingArea 操作错误。

    5.99.20 修复：文件路径移至 details 字段，不暴露在消息中。
    """

    error_code = "ZA-TR-0004"

    def __init__(self, message: str, *, details: dict[str, Any] | None = None, error_code: str | None = None) -> None:
        super().__init__(message)
        self.details: dict[str, Any] = details or {}
        if error_code is not None:
            self.error_code = error_code


class _CrossProcessLock:
    """跨进程文件锁（os.open O_CREAT|O_EXCL 原子创建）。

    根因: threading.Lock 只保护单进程内线程，多进程（Trae 多对话窗口）下无效。
    本锁通过 os.open(O_CREAT|O_EXCL) 原子操作实现跨进程互斥。

    用文件锁而非目录锁: Windows NTFS 目录删除（rmtree）有延迟，Defender 扫描期间
    立即 mkdir 会失败；文件删除（os.remove）更可靠。

    锁文件: .ailocks/staging_commit_{hash}.lock
    TTL: 30 分钟（防进程崩溃死锁，与 lock_files.py 一致）
    """

    _TTL_SECONDS = 1800

    def __init__(self, project_root: Path, file_path: str, timeout: float = 30.0, poll_interval: float = 0.05) -> None:
        name_hash = hashlib.sha256(file_path.encode("utf-8")).hexdigest()[:16]
        self._lock_file = project_root / ".ailocks" / f"staging_commit_{name_hash}.lock"
        self._lock_file.parent.mkdir(parents=True, exist_ok=True)
        self._file_path = file_path
        self._timeout = timeout
        self._poll_interval = poll_interval
        self._acquired = False

    def __enter__(self) -> _CrossProcessLock:
        import json

        deadline = time.monotonic() + self._timeout
        while True:
            try:
                fd = os.open(str(self._lock_file), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                try:
                    os.write(
                        fd,
                        json.dumps(
                            {"pid": os.getpid(), "acquired_at": time.time(), "file": self._file_path},
                            ensure_ascii=False,
                        ).encode("utf-8"),
                    )
                finally:
                    os.close(fd)
                self._acquired = True
                return self
            except FileExistsError:
                try:
                    data = json.loads(self._lock_file.read_text(encoding="utf-8"))
                    # 红蓝对抗修复：类型检查，防止锁文件篡改导致 TypeError 崩溃
                    acquired_at = data.get("acquired_at", 0)
                    if not isinstance(acquired_at, (int, float)):
                        acquired_at = 0
                    if time.time() - acquired_at > self._TTL_SECONDS:
                        try:
                            os.remove(self._lock_file)
                        except OSError:
                            pass
                        continue
                except (OSError, ValueError, TypeError):
                    pass
                if time.monotonic() >= deadline:
                    raise StagingError(
                        f"Cannot acquire cross-process lock (timeout {self._timeout}s)— another session is committing this file",
                        details={"file_path": str(self._file_path)},
                    )
                time.sleep(self._poll_interval)

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        if self._acquired:
            try:
                os.remove(self._lock_file)
            except OSError as e:
                logger.warning("_CrossProcessLock.__exit__: failed to remove lock file %s (%s: %s)", self._lock_file, type(e).__name__, e)
            self._acquired = False
        return False


@dataclass
class ConflictInfo:
    file_path: str
    draft_mtime: str
    current_mtime: str
    draft_hash: str
    current_hash: str
    diff_lines: list[str] = field(default_factory=list)


@dataclass
class CommitResult:
    status: CommitStatus
    file_path: str
    conflict: ConflictInfo | None = None
    message: str = ""


def _read_file_robust(path: Path, mode: str = "r", max_retries: int = 5) -> str:
    base_delay = 0.01
    for attempt in range(max_retries):
        try:
            with open(path, mode, encoding="utf-8") as f:
                return f.read()
        except PermissionError:
            if attempt == max_retries - 1:
                raise
            delay = base_delay * (2**attempt) + random.uniform(0, 0.01)
            time.sleep(delay)
    raise PermissionError(f"Cannot read file after {max_retries} retries (permission denied)")


def _file_hash(path: Path) -> str:
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
    except FileNotFoundError:
        return ""
    except PermissionError:
        return _file_hash_retry(path)
    return h.hexdigest()


def _file_hash_retry(path: Path, max_retries: int = 5) -> str:
    base_delay = 0.01
    for attempt in range(max_retries):
        try:
            h = hashlib.sha256()
            with open(path, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    h.update(chunk)
            return h.hexdigest()
        except PermissionError:
            if attempt == max_retries - 1:
                return ""
            delay = base_delay * (2**attempt) + random.uniform(0, 0.01)
            time.sleep(delay)
    return ""


def _file_mtime(path: Path) -> str:
    try:
        return str(os.path.getmtime(path))
    except OSError:
        return "0"


def _compute_diff_lines(old_lines: Sequence[str], new_lines: Sequence[str]) -> list[str]:
    from difflib import SequenceMatcher

    sm = SequenceMatcher(None, old_lines, new_lines)
    diff: list[str] = []
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            continue
        elif op == "replace":
            for i in range(i1, i2):
                diff.append(f"- {old_lines[i].rstrip()}")
            for j in range(j1, j2):
                diff.append(f"+ {new_lines[j].rstrip()}")
        elif op == "delete":
            for i in range(i1, i2):
                diff.append(f"- {old_lines[i].rstrip()}")
        elif op == "insert":
            for j in range(j1, j2):
                diff.append(f"+ {new_lines[j].rstrip()}")
    return diff


def _check_overlap(old_lines: Sequence[str], new_lines: Sequence[str]) -> bool:
    from difflib import SequenceMatcher

    sm = SequenceMatcher(None, old_lines, new_lines)
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "replace":
            return True
    return False


def _write_atomic_or_raise(target: Path, content: str, error_message: str) -> None:
    """原子写入 target；PermissionError 转为 StagingError。"""
    tmp = target.with_suffix(target.suffix + f".{uuid.uuid4().hex}.tmp")
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(content)
        _atomic_replace(tmp, target)
    except PermissionError:
        try:
            os.remove(tmp)
        except OSError:
            pass
        raise StagingError(error_message, details={"target_path": str(target)})


def _build_conflict_result(
    file_path: str,
    draft: Path,
    locked_mtime: str,
    locked_hash: str,
    current_lines: list[str],
    draft_lines: list[str],
    message: str,
) -> CommitResult:
    """构造 CONFLICT_NEEDS_OWNER 的 CommitResult。"""
    return CommitResult(
        status=CommitStatus.CONFLICT_NEEDS_OWNER,
        file_path=file_path,
        conflict=ConflictInfo(
            file_path=file_path,
            draft_mtime=_file_mtime(draft),
            current_mtime=locked_mtime,
            draft_hash=_file_hash(draft),
            current_hash=locked_hash,
            diff_lines=_compute_diff_lines(current_lines, draft_lines),
        ),
        message=message,
    )


def _apply_three_way_merge(
    local_baseline: list[str],
    draft_lines: list[str],
    current_lines: list[str],
    current_vs_baseline_overlap: bool,
) -> tuple[list[str], bool]:
    """三方合并：将 draft 相对 baseline 的改动 rebase 到 current。

    返回 (merged_lines, has_conflict)。has_conflict=True 表示遇到
    replace+overlap，需要 owner 介入（此时 merged_lines 为空占位）。
    """
    from difflib import SequenceMatcher

    sm = SequenceMatcher(None, local_baseline, draft_lines)
    merged: list[str] = list(current_lines)
    offset = 0
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            continue
        elif op == "insert":
            insert_pos = i1 + offset
            for j in range(j1, j2):
                merged.insert(insert_pos, draft_lines[j])
                offset += 1
        elif op == "delete":
            del merged[i1 + offset : i2 + offset]
            offset -= i2 - i1
        elif op == "replace":
            if current_vs_baseline_overlap:
                return [], True
            replace_pos = i1 + offset
            del merged[replace_pos : i2 + offset]
            for j in range(j1, j2):
                merged.insert(replace_pos, draft_lines[j])
                replace_pos += 1
            offset += j2 - j1 - (i2 - i1)
    return merged, False


class StagingArea:
    """多AI并发草稿写入+提交+冲突检测模块。"""

    DRAFTS_DIR = ".aidrafts"

    def __init__(self, project_root: str | Path) -> None:
        self._root = Path(project_root).resolve()
        self._drafts_root = self._root / self.DRAFTS_DIR

    def _validate_path(self, file_path: str) -> str:
        """5.86.3 修复：净化 file_path 防止路径穿越。

        - 禁止空路径、绝对路径、null byte
        - 禁止 `..` 路径穿越（resolve 后必须在项目根下）
        - 净化反斜杠/正斜杠开头的路径
        """
        if not file_path or not file_path.strip():
            raise StagingError("file_path must not be empty")
        if "\x00" in file_path:
            raise StagingError("file_path must not contain null byte")
        # 禁止绝对路径（Windows 与 POSIX）
        if Path(file_path).is_absolute():
            raise StagingError(
                "file_path must be relative",
                details={"file_path": file_path},
            )
        # 解析后必须位于项目根下
        resolved = (self._root / file_path).resolve()
        try:
            resolved.relative_to(self._root)
        except ValueError as exc:
            raise StagingError(
                "file_path escapes project root",
                details={"file_path": file_path, "resolved": str(resolved)},
            ) from exc
        return file_path

    def _draft_path(self, session_id: str, file_path: str) -> Path:
        safe_session = session_id.replace("/", "_").replace("\\", "_")
        validated = self._validate_path(file_path)
        return self._drafts_root / safe_session / validated

    def _target_path(self, file_path: str) -> Path:
        validated = self._validate_path(file_path)
        return self._root / validated

    def write_draft(self, session_id: str, file_path: str, content: str, baseline_content: str | None = None) -> Path:
        """将内容写到草稿区 .aidrafts/{session_id}/{file_path}。

        同时记录原文件的 mtime+hash 作为基线，用于提交时冲突检测。
        若提供 baseline_content，用它作为基线内容（避免重新读取文件时状态已变化）；
        否则从目标文件读取当前内容作为基线。
        """
        draft = self._draft_path(session_id, file_path)
        draft.parent.mkdir(parents=True, exist_ok=True)

        target = self._target_path(file_path)
        if baseline_content is not None:
            original_text = baseline_content
            mtime = _file_mtime(target)
            fhash = _file_hash(target) if target.exists() else hashlib.sha256(original_text.encode("utf-8")).hexdigest()
        elif target.exists():
            original_text = _read_file_robust(target)
            mtime = _file_mtime(target)
            fhash = _file_hash(target)
        else:
            original_text = ""
            mtime = "0"
            fhash = ""

        tmp = draft.with_suffix(draft.suffix + f".{uuid.uuid4().hex}.tmp")
        try:
            with open(tmp, "w", encoding="utf-8") as f:
                f.write(content)
            _atomic_replace(tmp, draft)
        except PermissionError:
            try:
                os.remove(tmp)
            except OSError:
                pass
            raise StagingError(
                "Cannot write draft",
                details={"draft_path": str(draft)},
            )

        baseline = draft.with_suffix(draft.suffix + ".baseline")
        baseline_data = f"{mtime}\n{fhash}\n"
        baseline_tmp = baseline.with_suffix(baseline.suffix + f".{uuid.uuid4().hex}.tmp")
        try:
            with open(baseline_tmp, "w", encoding="utf-8") as f:
                f.write(baseline_data)
            _atomic_replace(baseline_tmp, baseline)
        except PermissionError:
            try:
                os.remove(baseline_tmp)
            except OSError:
                pass
            raise StagingError(
                "Cannot write baseline",
                details={"baseline_path": str(baseline)},
            )

        baseline_content_file = draft.with_suffix(draft.suffix + ".baseline_content")
        baseline_content_tmp = baseline_content_file.with_suffix(
            baseline_content_file.suffix + f".{uuid.uuid4().hex}.tmp"
        )
        try:
            with open(baseline_content_tmp, "w", encoding="utf-8") as f:
                f.write(original_text)
            _atomic_replace(baseline_content_tmp, baseline_content_file)
        except PermissionError:
            try:
                os.remove(baseline_content_tmp)
            except OSError:
                pass
            raise StagingError(
                "Cannot write baseline content",
                details={"baseline_content_path": str(baseline_content_file)},
            )

        return draft

    def commit(self, session_id: str, file_path: str) -> CommitResult:
        """将草稿搬入最终位置（原子写入）。

        提交前检查原文件 mtime+hash——若已被修改则返回 CONFLICT。
        """
        draft = self._draft_path(session_id, file_path)
        if not draft.exists():
            return CommitResult(status=CommitStatus.NO_DRAFT, file_path=file_path, message="draft not found")

        target = self._target_path(file_path)
        baseline = draft.with_suffix(draft.suffix + ".baseline")

        _orig_mtime: str | None = None
        _orig_hash: str | None = None

        if baseline.exists():
            baseline_data = baseline.read_text(encoding="utf-8").strip().split("\n")
            if len(baseline_data) >= 2:
                _orig_mtime, _orig_hash = baseline_data[0], baseline_data[1]
                curr_mtime = _file_mtime(target)
                curr_hash = _file_hash(target)
                if curr_mtime != _orig_mtime or curr_hash != _orig_hash:
                    draft_lines = draft.read_text(encoding="utf-8").splitlines(keepends=True)
                    current_lines = (
                        target.read_text(encoding="utf-8").splitlines(keepends=True) if target.exists() else []
                    )
                    diff_lines = _compute_diff_lines(current_lines, draft_lines)
                    return CommitResult(
                        status=CommitStatus.CONFLICT,
                        file_path=file_path,
                        conflict=ConflictInfo(
                            file_path=file_path,
                            draft_mtime=_file_mtime(draft),
                            current_mtime=curr_mtime,
                            draft_hash=_file_hash(draft),
                            current_hash=curr_hash,
                            diff_lines=diff_lines,
                        ),
                        message="file modified by another session since draft was created",
                    )

        target.parent.mkdir(parents=True, exist_ok=True)
        draft_content = _read_file_robust(draft)

        with _COMMIT_LOCK, _CrossProcessLock(self._root, file_path):
            if _orig_mtime is not None:
                pre_replace_mtime = _file_mtime(target)
                pre_replace_hash = _file_hash(target)
                if pre_replace_mtime != _orig_mtime or pre_replace_hash != _orig_hash:
                    return CommitResult(
                        status=CommitStatus.CONFLICT,
                        file_path=file_path,
                        message="file changed between check and commit by another session",
                    )

            tmp = target.with_suffix(target.suffix + f".{uuid.uuid4().hex}.tmp")
            try:
                with open(tmp, "w", encoding="utf-8") as f:
                    f.write(draft_content)
                _atomic_replace(tmp, target)
            except PermissionError:
                try:
                    os.remove(tmp)
                except OSError:
                    pass
                raise StagingError(
                    "Cannot commit draft",
                    details={"target_path": str(target)},
                )

        self._cleanup_draft(session_id, file_path)
        return CommitResult(status=CommitStatus.OK, file_path=file_path, message="committed successfully")

    def try_auto_merge(self, session_id: str, file_path: str) -> CommitResult:
        """尝试自动合并草稿与当前文件。

        简单冲突（非重叠区域修改）自动 rebase 成功。
        复杂冲突（重叠区域修改）返回 CONFLICT_NEEDS_OWNER。
        """
        draft = self._draft_path(session_id, file_path)
        if not draft.exists():
            return CommitResult(status=CommitStatus.NO_DRAFT, file_path=file_path, message="draft not found")

        target = self._target_path(file_path)
        baseline = draft.with_suffix(draft.suffix + ".baseline")

        if not baseline.exists():
            return self.commit(session_id, file_path)

        baseline_data = baseline.read_text(encoding="utf-8").strip().split("\n")
        if len(baseline_data) < 2:
            return self.commit(session_id, file_path)

        orig_mtime, orig_hash = baseline_data[0], baseline_data[1]
        curr_mtime = _file_mtime(target)
        curr_hash = _file_hash(target)

        if curr_mtime == orig_mtime and curr_hash == orig_hash:
            return self.commit(session_id, file_path)

        if not target.exists():
            return self.commit(session_id, file_path)

        baseline_content = self._read_baseline_content(draft, orig_hash)
        draft_lines = draft.read_text(encoding="utf-8").splitlines(keepends=True)

        with _COMMIT_LOCK, _CrossProcessLock(self._root, file_path):
            current_lines = _read_file_robust(target).splitlines(keepends=True)

            locked_mtime = _file_mtime(target)
            locked_hash = _file_hash(target)
            if locked_mtime == orig_mtime and locked_hash == orig_hash:
                draft_text = draft.read_text(encoding="utf-8")
                _write_atomic_or_raise(target, draft_text, "Cannot auto-merge")
                self._cleanup_draft(session_id, file_path)
                return CommitResult(status=CommitStatus.OK, file_path=file_path, message="committed successfully")

            local_baseline = baseline_content
            if local_baseline is None:
                local_baseline = current_lines

            draft_vs_baseline_overlap = _check_overlap(local_baseline, draft_lines)
            current_vs_baseline_overlap = _check_overlap(local_baseline, current_lines)

            if draft_vs_baseline_overlap and current_vs_baseline_overlap:
                return _build_conflict_result(
                    file_path, draft, locked_mtime, locked_hash,
                    current_lines, draft_lines,
                    "overlapping changes — needs owner resolution",
                )

            merged, has_conflict = _apply_three_way_merge(
                local_baseline, draft_lines, current_lines, current_vs_baseline_overlap
            )
            if has_conflict:
                return _build_conflict_result(
                    file_path, draft, locked_mtime, locked_hash,
                    current_lines, draft_lines,
                    "overlapping replace — needs owner resolution",
                )

            merged_content = "".join(merged)
            _write_atomic_or_raise(target, merged_content, "Cannot auto-merge")

        self._cleanup_draft(session_id, file_path)
        return CommitResult(status=CommitStatus.MERGED, file_path=file_path, message="auto-merged successfully")

    def _read_baseline_content(self, draft: Path, orig_hash: str) -> list[str] | None:
        content_file = draft.with_suffix(draft.suffix + ".baseline_content")
        if content_file.exists():
            return _read_file_robust(content_file).splitlines(keepends=True)
        return None

    def list_drafts(self, session_id: str) -> list[str]:
        """列出当前会话的所有草稿文件路径。"""
        safe_session = session_id.replace("/", "_").replace("\\", "_")
        session_dir = self._drafts_root / safe_session
        if not session_dir.exists():
            return []
        drafts: list[str] = []
        for f in session_dir.rglob("*"):
            if f.is_file() and not f.name.endswith((".baseline", ".baseline_content")):
                rel = f.relative_to(session_dir)
                drafts.append(str(rel).replace("\\", "/"))
        return sorted(drafts)

    def discard(self, session_id: str, file_path: str) -> bool:
        """丢弃草稿。返回 True 表示成功，False 表示草稿不存在。"""
        draft = self._draft_path(session_id, file_path)
        baseline = draft.with_suffix(draft.suffix + ".baseline")
        baseline_content = draft.with_suffix(draft.suffix + ".baseline_content")
        removed = False
        for p in (draft, baseline, baseline_content):
            if p.exists():
                p.unlink()
                removed = True
        return removed

    def get_conflict(self, session_id: str, file_path: str) -> ConflictInfo | None:
        """返回冲突详情（如果存在）。"""
        draft = self._draft_path(session_id, file_path)
        if not draft.exists():
            return None
        baseline = draft.with_suffix(draft.suffix + ".baseline")
        target = self._target_path(file_path)
        if not baseline.exists():
            return None
        baseline_data = baseline.read_text(encoding="utf-8").strip().split("\n")
        if len(baseline_data) < 2:
            return None
        orig_mtime, orig_hash = baseline_data[0], baseline_data[1]
        curr_mtime = _file_mtime(target)
        curr_hash = _file_hash(target)
        if curr_mtime == orig_mtime and curr_hash == orig_hash:
            return None
        draft_lines = draft.read_text(encoding="utf-8").splitlines(keepends=True)
        current_lines = target.read_text(encoding="utf-8").splitlines(keepends=True) if target.exists() else []
        diff_lines = _compute_diff_lines(current_lines, draft_lines)
        return ConflictInfo(
            file_path=file_path,
            draft_mtime=_file_mtime(draft),
            current_mtime=curr_mtime,
            draft_hash=_file_hash(draft),
            current_hash=curr_hash,
            diff_lines=diff_lines,
        )

    def _cleanup_draft(self, session_id: str, file_path: str) -> None:
        draft = self._draft_path(session_id, file_path)
        baseline = draft.with_suffix(draft.suffix + ".baseline")
        baseline_content = draft.with_suffix(draft.suffix + ".baseline_content")
        for p in (draft, baseline, baseline_content):
            try:
                if p.exists():
                    p.unlink()
            except OSError:
                pass
        session_dir = self._draft_path(session_id, "").parent
        try:
            if session_dir.exists() and not any(session_dir.iterdir()):
                session_dir.rmdir()
        except OSError:
            pass
