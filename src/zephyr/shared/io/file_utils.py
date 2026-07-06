# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.io.file_utils
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-SHR_file_utils | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
file_utils.py —— 安全文件操作工具（Phase 3 新增 | 盲点 #15 修复）

痛点修复：此前 AI 直接 write/overwrite 文件——
  1. 写入中途崩溃 → 文件损坏（无原子写保护）
  2. 改错了无法回滚（无自动备份）
  3. 多个地方实现同样的 safe_write 逻辑

设计对标：
  - PostgreSQL WAL（Write-Ahead Log）→ 先写临时文件，再 rename
  - Git object store → content-addressed 写入
  - POSIX atomic rename 语义

设计原则：
  - 原子写：先写 .tmp 文件 → flush → rename（POSIX 保证 rename 是原子的）
  - 自动备份：写入前自动创建 .bak（保留最近 N 个版本）
  - 校验读：读取后可选校验 SHA-256（防静默损坏）

AI 施工约定：
  - 所有文件写入操作 MUST 使用 atomic_write，禁止裸 open().write()
  - feedback-loop 自进化修改代码时 MUST 启用 auto_backup
  - 批量修改时 MUST 使用 backup_and_rollback 上下文

SSoT: MOD-INF-016 §2.11 shared-file-utils
Version: 0.1.0
"""

from __future__ import annotations

import hashlib
import os
import shutil
import tempfile
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
from typing import Protocol, runtime_checkable


@runtime_checkable
class AtomicWriteFn(Protocol):
    """5.12.2#1 修复：atomic_write 签名 Protocol——统一3处漂移实现。

    canonical 真源：file_utils.atomic_write（本模块）。
    变体（fix_safety.WriteSafety / forensic.ForensicWriter）应委托本真源。
    """

    def __call__(self, filepath: Path | str, content: str, **kwargs: object) -> Path: ...


__all__ = [
    "AtomicWriteError",
    "AtomicWriteFn",
    "atomic_write",
    "backup_and_rollback",
    "backup_file",
    "restore_backup",
    "safe_read",
]


class AtomicWriteError(OSError):
    """原子写入失败——临时文件写入或 rename 异常。"""
    error_code = "ZA-SH-0037"

    def __init__(self, *args, error_code: str | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        if error_code is not None:
            self.error_code = error_code


def atomic_write(
    filepath: Path | str,
    content: str,
    *,
    encoding: str = "utf-8",
    auto_backup: bool = False,
    max_backups: int = 5,
) -> Path:
    """原子写入文件——先写临时文件，再 rename 到目标路径。

    流程：
      1. 在同一目录创建 .tmp 文件
      2. 写入全部内容 + flush + fsync
      3. os.replace(临时文件, 目标文件)  ← POSIX 原子操作

    Args:
        filepath: 目标文件路径。
        content: 要写入的文本内容。
        encoding: 文件编码。
        auto_backup: 是否在写入前自动备份原文件。
        max_backups: 最多保留的备份版本数。

    Returns:
        写入后的目标文件 Path。

    Raises:
        AtomicWriteError: 写入过程异常。
    """
    target = Path(filepath)
    target.parent.mkdir(parents=True, exist_ok=True)

    if auto_backup and target.exists():
        backup_file(target, max_backups=max_backups)

    fd, tmp_path_str = tempfile.mkstemp(
        suffix=".tmp",
        prefix=f".{target.name}_",
        dir=str(target.parent),
    )
    tmp_path = Path(tmp_path_str)

    try:
        with os.fdopen(fd, "w", encoding=encoding) as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())

        os.replace(str(tmp_path), str(target))
    except Exception:
        if tmp_path.exists():
            tmp_path.unlink(missing_ok=True)
        raise AtomicWriteError("atomic_write failed")

    return target


def safe_read(
    filepath: Path | str,
    *,
    encoding: str = "utf-8",
    verify_sha256: str | None = None,
) -> str:
    """安全读取文件，可选校验 SHA-256。

    Args:
        filepath: 文件路径。
        encoding: 文件编码。
        verify_sha256: 可选，期望的 SHA-256 哈希（hex digest）。

    Returns:
        文件内容字符串。

    Raises:
        FileNotFoundError: 文件不存在。
        ValueError: SHA-256 校验不通过。
    """
    filepath = Path(filepath)
    content = filepath.read_text(encoding=encoding)

    if verify_sha256:
        actual = hashlib.sha256(content.encode(encoding)).hexdigest()
        if actual != verify_sha256:
            raise ValueError(f"SHA-256 mismatch: expected {verify_sha256[:16]}..., got {actual[:16]}...")

    return content


def backup_file(
    filepath: Path | str,
    *,
    max_backups: int = 5,
) -> Path | None:
    """创建文件备份，并清理超量的旧备份。

    备份命名：{filename}.bak.0, {filename}.bak.1, ...

    Args:
        filepath: 要备份的文件路径。
        max_backups: 最多保留的备份数（超出时删除最旧的）。

    Returns:
        备份文件 Path，若源文件不存在则返回 None。
    """
    source = Path(filepath)
    if not source.exists():
        return None

    bak_template = f"{source.name}.bak"

    bak_files = sorted(
        source.parent.glob(f"{bak_template}.*"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )

    while len(bak_files) >= max_backups:
        oldest = bak_files.pop()
        oldest.unlink(missing_ok=True)

    rotation = 0
    while True:
        bak_path = source.parent / f"{bak_template}.{rotation}"
        if not bak_path.exists():
            break
        rotation += 1

    shutil.copy2(source, bak_path)
    return bak_path


def restore_backup(
    filepath: Path | str,
    *,
    backup_index: int = 0,
) -> Path:
    """从备份恢复文件。

    Args:
        filepath: 要恢复的目标文件路径。
        backup_index: 备份序号（0 = 最新）。

    Returns:
        恢复后的目标文件 Path。

    Raises:
        FileNotFoundError: 指定序号的备份不存在。
    """
    target = Path(filepath)
    bak_path = target.parent / f"{target.name}.bak.{backup_index}"

    if not bak_path.exists():
        raise FileNotFoundError("Backup not found")

    shutil.copy2(bak_path, target)
    return target


@contextmanager
def backup_and_rollback(
    filepath: Path | str,
    *,
    max_backups: int = 3,
) -> Generator[Path, None, None]:
    """上下文管理器——操作前后自动备份，异常时自动回滚。

    Usage::

        with backup_and_rollback("config/settings.yaml") as path:
            content = path.read_text()
            content = content.replace("old", "new")
            atomic_write(path, content)

    如果 with 块内抛异常，自动从备份恢复。

    Args:
        filepath: 要保护的文件路径。
        max_backups: 最多备份数。

    Yields:
        目标文件 Path。
    """
    target = Path(filepath)
    backup_file(target, max_backups=max_backups)

    try:
        yield target
    except BaseException:
        # 5.163.3 修复: except Exception → BaseException,确保 Ctrl+C/SystemExit 时
        # 也执行 restore_backup,避免文件停留在半修改状态。
        restore_backup(target, backup_index=0)
        raise
