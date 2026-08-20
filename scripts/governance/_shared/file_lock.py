# [BLUEPRINT] MOD-INF-005 | scripts/governance/_shared/file_lock.py | §
# [MODULE] scripts.governance._shared.file_lock
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] filelock (第三方库，可选；不可用时 fail-open)
# [CONSUMERS] blueprint_frontmatter_reconciler._write_frontmatter_updates; sync_blueprint_code_index._process_blueprint; reconciliation_registry._auto_fix_gate_inventory
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] fail-open 设计（锁获取失败时 warn 并放行，不阻断写操作）;锁文件存放于 .runtime/locks/（.gitignore 忽略）
# [MODIFY-GUARD] blueprint_write_lock 为对外唯一入口;锁文件名=blueprint 相对路径 SHA-256 前 16 字符
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] filelock 不可用→yield False (fail-open); 锁超时→yield False (fail-open); 锁成功→yield True
# [TESTS]
# [A_module] module_id=MOD-INF-005 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #ARCH-RECONCILER-TOCTOU-CLOBBER-001
"""file_lock.py — blueprint.md 跨进程 advisory lock（#ARCH-RECONCILER-TOCTOU-CLOBBER-001 P0 止血）

问题：多个 reconciler（frontmatter_sync、code_index_sync、inventory_sync）对同一
blueprint.md 进行无锁整文件读写，跨 commit/session 并发时后写者覆盖前写者内容（clobber）。

止血方案：提供 blueprint_write_lock 上下文管理器，对整文件 READ-MODIFY-WRITE 操作
加跨进程 advisory lock（filelock 库），串行化并发写。

设计原则：
  - fail-open：锁获取失败时 warn 并放行（不阻断写操作），避免锁基础设施故障导致整个
    reconciler 管线卡死。clobber 风险通过 skip-if-recent 机制进一步收窄。
  - 锁文件存放于 .runtime/locks/（.gitignore 忽略，不进 git）
  - 锁文件名 = blueprint.md 的相对路径 SHA-256 哈希前 16 字符（避免路径特殊字符问题）

用法::

    from _shared.file_lock import blueprint_write_lock

    with blueprint_write_lock(bp_path):
        content = bp_path.read_text()
        # ... 修改 content ...
        bp_path.write_text(new_content)
"""

from __future__ import annotations

import hashlib
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

try:
    from filelock import FileLock, Timeout
except ImportError:
    FileLock = None  # type: ignore[assignment,misc]
    Timeout = None  # type: ignore[assignment,misc]

_REPO_ROOT = Path(__file__).resolve().parents[3]
_DEFAULT_LOCK_DIR = _REPO_ROOT / ".runtime" / "locks"


def _lock_file_for(bp_path: Path, lock_dir: Path | None = None) -> Path:
    """为指定 blueprint 路径生成锁文件路径。

    锁文件名 = ``blueprint_<sha256[:16]>.lock``，用相对路径哈希避免特殊字符问题。
    """
    base = lock_dir or _DEFAULT_LOCK_DIR
    base.mkdir(parents=True, exist_ok=True)
    try:
        rel = bp_path.resolve().relative_to(_REPO_ROOT)
    except ValueError:
        rel = bp_path
    digest = hashlib.sha256(str(rel).encode("utf-8")).hexdigest()[:16]
    return base / f"blueprint_{digest}.lock"


@contextmanager
def blueprint_write_lock(
    bp_path: Path,
    timeout: float = 30.0,
    lock_dir: Path | None = None,
) -> Iterator[bool]:
    """获取 blueprint.md 写锁（跨进程 advisory lock）。

    fail-open 设计：锁获取失败时 warn 并放行，不阻断写操作。

    Args:
        bp_path: blueprint.md 文件路径
        timeout: 锁获取超时秒数（默认 30s）
        lock_dir: 锁文件目录（默认 .runtime/locks/）

    Yields:
        bool: True=锁获取成功，False=fail-open（锁不可用或超时）
    """
    if FileLock is None:
        print("[WARN] filelock not available, fail-open write", file=sys.stderr)
        yield False
        return

    lock_file = _lock_file_for(bp_path, lock_dir)
    lock = FileLock(str(lock_file))
    try:
        lock.acquire(timeout=timeout)
    except Timeout:
        print(
            f"[WARN] blueprint_write_lock timeout ({timeout}s), fail-open: {bp_path}",
            file=sys.stderr,
        )
        yield False
        return
    try:
        yield True
    finally:
        try:
            lock.release()
        except Exception:
            pass
