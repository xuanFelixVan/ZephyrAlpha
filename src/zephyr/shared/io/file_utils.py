# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.io.file_utils
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
file_utils.py —— 安全文件操作工具（Phase 3 新增 | 盲点 #15 修复）

痛点修复：此前 AI 直接 write/overwrite 文件——
  1. 写入中途崩溃 -> 文件损坏（无原子写保护）
  2. 改错了无法回滚（无自动备份）
  3. 多个地方实现同样的 safe_write 逻辑

设计对标：
  - PostgreSQL WAL（Write-Ahead Log）-> 先写临时文件，再 rename
  - Git object store -> content-addressed 写入
  - POSIX atomic rename 语义

设计原则：
  - 原子写：先写 .tmp 文件 -> flush -> rename（POSIX 保证 rename 是原子的）
  - 自动备份：写入前自动创建 .bak（保留最近 N 个版本）
  - 校验读：读取后可选校验 SHA-256（防静默损坏）

AI 施工约定：
  - 所有文件写入操作 MUST 使用 atomic_write，禁止裸 open().write()
  - feedback-loop 自进化修改代码时 MUST 启用 auto_backup
  - 批量修改时 MUST 使用 backup_and_rollback 上下文

SSoT: MOD-INF-016 §2.11 shared-file-utils
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: filepath 参数
#   fields: 参数 filepath，类型注解 Path | str
#   code: file_utils.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: content 参数
#   fields: 参数 content，类型注解 str
#   code: file_utils.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: encoding 参数
#   fields: 参数 encoding（无注解）
#   code: file_utils.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: auto_backup 参数
#   fields: 参数 auto_backup（无注解）
#   code: file_utils.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① atomic_write
#   name_en: atomic_write
#   intro: 原子写入文件——先写临时文件，再 rename 到目标路径。
#   desc: 原子写入文件——先写临时文件，再 rename 到目标路径。 流程： 1. 在同一目录创建 .tmp 文件 2. 写入全部内容 + flush + fsync 3. os.rep…；源码 L225-L282
#   inputs: filepath content encoding auto_backup max_backups newline
#   outputs: Path
# - id: A2
#   name_zh: ② safe_read
#   name_en: safe_read
#   intro: 安全读取文件，可选校验 SHA-256。
#   desc: 安全读取文件，可选校验 SHA-256。 Args: filepath: 文件路径。 encoding: 文件编码。 verify_sha256: 可选，期望的 SHA-256…；源码 L285-L313
#   inputs: filepath encoding verify_sha256
#   outputs: str
# - id: A3
#   name_zh: ③ backup_file
#   name_en: backup_file
#   intro: 创建文件备份，并清理超量的旧备份。
#   desc: 创建文件备份，并清理超量的旧备份。 备份命名：{filename}.bak.0, {filename}.bak.1, ... Args: filepath: 要备份的文件路径。…；源码 L316-L356
#   inputs: filepath max_backups
#   outputs: Path | None
# - id: A4
#   name_zh: ④ restore_backup
#   name_en: restore_backup
#   intro: 从备份恢复文件。
#   desc: 从备份恢复文件。 Args: filepath: 要恢复的目标文件路径。 backup_index: 备份序号（0 = 最新）。 Returns: 恢复后的目标文件 Path。…；源码 L359-L383
#   inputs: filepath backup_index
#   outputs: Path
# - id: A5
#   name_zh: ⑤ backup_and_rollback
#   name_en: backup_and_rollback
#   intro: 上下文管理器——操作前后自动备份，异常时自动回滚。
#   desc: 上下文管理器——操作前后自动备份，异常时自动回滚。 Usage:: with backup_and_rollback("config/settings.yaml") as pat…；源码 L387-L419
#   inputs: filepath max_backups
#   outputs: Generator[Path, None, None]
# - id: A6
#   name_zh: ⑥ content_sha256
#   name_en: content_sha256
#   intro: UTF-8 语义内容 hash（调用方读文件后计算，作为 expected_base 传入）。
#   desc: UTF-8 语义内容 hash（调用方读文件后计算，作为 expected_base 传入）。；源码 L474-L476
#   inputs: text
#   outputs: str
# - id: A7
#   name_zh: ⑦ is_hot_file
#   name_en: is_hot_file
#   intro: 热文件判定（公开接口——commit gate / 注册表写者共用，防第二真源）。
#   desc: 热文件判定（公开接口——commit gate / 注册表写者共用，防第二真源）。；源码 L489-L495
#   inputs: path repo_root
#   outputs: bool
# - id: A8
#   name_zh: ⑧ safe_write_text
#   name_en: safe_write_text
#   intro: CAS 语义写文本文件：base 校验→原子写→回读校验→审计。
#   desc: CAS 语义写文本文件：base 校验→原子写→回读校验→审计。 Args: path: 目标文件。 content: 新内容。 expected_base_sha256: 调用…；源码 L501-L575
#   inputs: path content expected_base_sha256 repo_root encoding newline
#   outputs: SafeWriteResult
# - id: A9
#   name_zh: ⑨ assert_safe_rmtree_target
#   name_en: assert_safe_rmtree_target
#   intro: rmtree 删除前硬断言三件套（CAND-GOVSEC-001 ①）。
#   desc: rmtree 删除前硬断言三件套（CAND-GOVSEC-001 ①）。 ① resolve 后必须**严格**落在 allowed_prefix 之内（等于前缀本身亦拒绝——…；源码 L610-L646
#   inputs: path allowed_prefix
#   outputs: Path
# - id: A10
#   name_zh: ⑩ safe_rmtree
#   name_en: safe_rmtree
#   intro: 硬断言通过后执行删除（CAND-GOVSEC-001 ① 一站式入口）。
#   desc: 硬断言通过后执行删除（CAND-GOVSEC-001 ① 一站式入口）。 目录走 ``shutil.rmtree``（透传 ignore_errors/onerror），单文件走…；源码 L649-L681
#   inputs: path allowed_prefix ignore_errors onerror
#   outputs: bool
#   （注：A10 之后另有 6 个公共定义未列入（含 6 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: Path
#   name_en: Path
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 见模块头 [CONSUMERS]
# - id: O2
#   name_zh: str
#   name_en: str
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> A5
# A5 --> A6
# A6 --> A7
# A7 --> A8
# A8 --> A9
# A9 --> A10
# A10 --> O1
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import shutil
import tempfile
from collections.abc import Callable, Generator
from contextlib import contextmanager, nullcontext
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Final, Protocol, runtime_checkable

logger = logging.getLogger(__name__)


@runtime_checkable
class AtomicWriteFn(Protocol):
    """5.12.2#1 修复：atomic_write 签名 Protocol——统一3处漂移实现。

    canonical 真源：file_utils.atomic_write（本模块）。
    变体（fix_safety.WriteSafety / forensic.ForensicWriter）应委托本真源。
    """

    def __call__(self, filepath: Path | str, content: str, **kwargs: object) -> Path: ...


__all__: Final = [
    "AtomicWriteError",
    "AtomicWriteFn",
    "DEFAULT_HOT_FILES",
    "SafeWriteResult",
    "StaleWriteRefused",
    "UnsafeDeleteRefused",
    "WriteVerificationError",
    "assert_safe_rmtree_target",
    "atomic_write",
    "backup_and_rollback",
    "backup_file",
    "content_sha256",
    "is_hot_file",
    "restore_backup",
    "safe_read",
    "safe_rmtree",
    "safe_write_text",
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
    newline: str | None = None,
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
        newline: 行尾策略（透传 TextIOWrapper）。None=平台默认（Windows 会把
            ``\\n`` 翻成 ``\\r\\n``）；注册表 YAML 等 .gitattributes 钉 LF 的
            热文件必须显式传 ``newline="\\n"`` 保字节级行尾约定。

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
        with os.fdopen(fd, "w", encoding=encoding, newline=newline) as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())

        os.replace(str(tmp_path), str(target))
    except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
        if tmp_path.exists():
            tmp_path.unlink(missing_ok=True)
        raise AtomicWriteError("atomic_write failed") from None

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
    except BaseException:  # noqa: BLE001 — 5.135治标: broad exception catch
        # 5.163.3 修复: except Exception -> BaseException,确保 Ctrl+C/SystemExit 时
        # 也执行 restore_backup,避免文件停留在半修改状态。
        restore_backup(target, backup_index=0)
        raise


# ── CAS 热文件写入（#ARCH-WORKTREE-WRITE-INTEGRITY-001 P2）────────────────────
# 把 #75 治愈路径（base-hash 校验+写后回读+即时提交）从"纪律"升级为"工具"：
# 写前必须证明读过当前内容（陈旧缓冲区拒写防吞改），写后回读校验防"修改已生效"
# 假象，全程审计落 .runtime/audit/（永不回 tracked 区）。内部复用 atomic_write。

# 热文件词表（高频 contested——lost-update/吞写事故全部出自这类文件）：
# 相对仓根路径，正斜杠。新增热文件在此追加。
DEFAULT_HOT_FILES: Final = frozenset(
    {
        "AGENTS.md",
        "docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml",
        "docs/01_policies_and_standards/_registry/catalogs/candidate_module_registry.yaml",
        "docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml",
        "docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml",
        "docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/construction_progress_tracker.md",
        "docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/00_index_trading_decision.md",
        # AI-DRIFT-001（2026-08-26）：94号当日连遭 4 起并发覆写事故（frontmatter 回滚/
        # 候选表行丢失/秒级反复覆写），扩列纳入 CAS 写前读新+commit base 新鲜度门禁覆盖。
        "docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/94_crypto_quant_expansion.md",
    }
)

_SAFE_WRITE_AUDIT_REL = ".runtime/audit/safe_write.jsonl"


class StaleWriteRefused(RuntimeError):
    """热文件未声明 base-hash，或 base-hash 与磁盘内容不符（陈旧缓冲区）。

    路径/哈希等细节入 details 字段（MSG-EXPOSURE 合规：消息文本不含敏感信息）。
    """

    def __init__(self, message: str, *, details: dict | None = None):
        super().__init__(message)
        self.details = details or {}


class WriteVerificationError(RuntimeError):
    """写后回读校验失败——落盘内容与预期不符（details 字段承载路径/哈希）。"""

    def __init__(self, message: str, *, details: dict | None = None):
        super().__init__(message)
        self.details = details or {}


@dataclass
class SafeWriteResult:
    path: str
    written: bool
    before_sha256: str
    after_sha256: str


def content_sha256(text: str) -> str:
    """UTF-8 语义内容 hash（调用方读文件后计算，作为 expected_base 传入）。"""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _safe_write_audit(repo_root: Path, record: dict) -> None:
    try:
        p = repo_root / _SAFE_WRITE_AUDIT_REL
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError as e:
        logger.warning("safe_write audit append failed: %s", e)


def is_hot_file(path: Path, repo_root: Path) -> bool:
    """热文件判定（公开接口——commit gate / 注册表写者共用，防第二真源）。"""
    try:
        rel = path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return False  # 仓外文件不按热文件约束
    return rel in DEFAULT_HOT_FILES


_is_hot_file = is_hot_file  # 向后兼容别名（模块内既有调用）


def safe_write_text(
    path: str | Path,
    content: str,
    *,
    expected_base_sha256: str | None = None,
    repo_root: str | Path | None = None,
    encoding: str = "utf-8",
    newline: str | None = None,
) -> SafeWriteResult:
    """CAS 语义写文本文件：base 校验→原子写→回读校验→审计。

    Args:
        path: 目标文件。
        content: 新内容。
        expected_base_sha256: 调用方读到的原内容 hash（content_sha256 计算）。
            热文件必填；非热文件可选（给了就校验）。
        repo_root: 仓根（热文件判定/审计锚定）；None 时经 paths.REPO_ROOT 解析。
        encoding: 读写编码。
        newline: 行尾策略（透传 atomic_write）；.gitattributes 钉 LF 的注册表
            热文件传 ``"\\n"`` 保字节级行尾约定。

    Raises:
        StaleWriteRefused: 热文件未带 base，或 base 与磁盘不符（拒写，不落盘）。
        WriteVerificationError: 回读校验失败（落盘内容≠预期）。
    """
    from zephyr.shared.io.paths import REPO_ROOT  # noqa: PLC0415

    root = Path(str(repo_root)) if repo_root else REPO_ROOT
    target = Path(path)
    hot = _is_hot_file(target, root)

    before_hash = ""
    if target.exists():
        before_hash = content_sha256(target.read_text(encoding=encoding))

    base_record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "file": str(target),
        "hot": hot,
        "pid": os.getpid(),
        "session": os.environ.get("ZEPHYR_SESSION_ID", ""),
        "expected_base": expected_base_sha256 or "",
        "before_sha256": before_hash,
    }

    # ① 热文件必须声明 base（强制 read-before-write）
    if hot and not expected_base_sha256:
        _safe_write_audit(root, {**base_record, "event": "refused", "reason": "hot_file_without_base"})
        raise StaleWriteRefused(
            "热文件未声明 expected_base_sha256，拒写",
            details={"path": str(target)},
        )
    # ② base 与磁盘不符=陈旧缓冲区，拒写（防吞写）
    if expected_base_sha256 and target.exists() and expected_base_sha256 != before_hash:
        _safe_write_audit(root, {**base_record, "event": "refused", "reason": "stale_base"})
        raise StaleWriteRefused(
            "base-hash 与磁盘不符（磁盘已被他人推进），拒写",
            details={"path": str(target), "expected": expected_base_sha256[:12], "disk": before_hash[:12]},
        )

    # ③ 原子写（复用本模块 atomic_write 真源）
    atomic_write(target, content, encoding=encoding, newline=newline)

    # ④ 写后回读校验（防"修改已生效"假象）
    after_hash = content_sha256(target.read_text(encoding=encoding))
    expected_after = content_sha256(content)
    if after_hash != expected_after:
        _safe_write_audit(root, {**base_record, "event": "verify_failed", "after_sha256": after_hash})
        raise WriteVerificationError(
            "写后回读校验失败（落盘内容与预期不符）",
            details={"path": str(target), "expect": expected_after[:12], "disk": after_hash[:12]},
        )

    _safe_write_audit(root, {**base_record, "event": "written", "after_sha256": after_hash})
    return SafeWriteResult(path=str(target), written=True, before_sha256=before_hash, after_sha256=after_hash)


# ── 删除硬断言（CAND-GOVSEC-001 ①，2026-08-23 src 误删防复发）─────────────────
# 第一性：观测护栏只覆盖仪表化通道，AI 会话可随时开未仪表化通道 → 破坏性
# 操作必须在执行点物理阻断（让坏事做不成），而非仅事后审计（做了被发现）。
# 三件套：resolve 后严格落在允许前缀内（'../src' 逃逸/junction 指向仓内均被
# resolve 后前缀判定拦住）+ 目标树自顶向下拒绝 reparse point（Windows
# shutil.rmtree 穿透 junction 删目标内容）+ 删除动作必须经本断言（硬阻断）。

FILE_ATTRIBUTE_REPARSE_POINT: Final = 0x400


class UnsafeDeleteRefused(RuntimeError):
    """删除目标硬断言失败——路径越出允许前缀，或目标树内含 reparse point。

    路径等细节入 details 字段（MSG-EXPOSURE 合规：消息文本不含敏感标识）。
    """

    def __init__(self, message: str, *, details: dict | None = None):
        super().__init__(message)
        self.details = details or {}


def _is_reparse_point(path: Path) -> bool:
    """reparse point（junction/symlink）检测；POSIX 退化为 is_symlink。"""
    try:
        if os.name == "nt":
            attrs = getattr(os.lstat(path), "st_file_attributes", 0)
            return bool(attrs & FILE_ATTRIBUTE_REPARSE_POINT)
        return path.is_symlink()
    except OSError:
        return False


def assert_safe_rmtree_target(path: str | Path, *, allowed_prefix: str | Path) -> Path:
    """rmtree 删除前硬断言三件套（CAND-GOVSEC-001 ①）。

    ① resolve 后必须**严格**落在 allowed_prefix 之内（等于前缀本身亦拒绝——
       本助手的语义是删前缀下的内容，不是删前缀）；
    ② 目标树自顶向下拒绝任何 reparse point——Windows ``shutil.rmtree`` 会穿透
       junction 删除其目标内容（2026-08-23 src 误删同型隐患③）。

    Args:
        path: 待删除目标。
        allowed_prefix: 允许删除的前缀目录（如 ``.aidrafts/``、queue_root）。

    Returns:
        resolve 后的目标路径——调用方应删除本返回值而非原始入参。

    Raises:
        UnsafeDeleteRefused: 任一断言失败。硬阻断，不降级为告警。
    """
    prefix = Path(allowed_prefix).resolve()
    resolved = Path(path).resolve()
    if resolved == prefix or not resolved.is_relative_to(prefix):
        raise UnsafeDeleteRefused(
            "删除目标越出允许前缀，硬断言拒绝",
            details={"target": str(resolved), "allowed_prefix": str(prefix)},
        )
    if resolved.is_dir():
        # os.walk top-down：dirnames 先于下降产出，检出即在下降前阻断，
        # 不会跟随 junction 走入目标树。
        for dirpath, dirnames, _filenames in os.walk(resolved):
            for name in dirnames:
                child = Path(dirpath) / name
                if _is_reparse_point(child):
                    raise UnsafeDeleteRefused(
                        "删除目标树内含 reparse point，硬断言拒绝",
                        details={"target": str(resolved), "reparse": str(child)},
                    )
    return resolved


def safe_rmtree(
    path: str | Path,
    *,
    allowed_prefix: str | Path,
    ignore_errors: bool = False,
    onerror: Callable[..., None] | None = None,
) -> bool:
    """硬断言通过后执行删除（CAND-GOVSEC-001 ① 一站式入口）。

    目录走 ``shutil.rmtree``（透传 ignore_errors/onerror），单文件走 unlink。
    目标不存在返回 False（幂等短路）。

    Raises:
        UnsafeDeleteRefused: 硬断言失败（不执行任何删除）。
    """
    resolved = assert_safe_rmtree_target(path, allowed_prefix=allowed_prefix)
    if not resolved.exists():
        return False
    # 硬断言通过=授权完成：直通 in-process 删除补丁（若装），防授权通道被自家
    # 补丁拦截（批5b 翻硬拦配套——.worktrees/.aidrafts 等保护区内合法清理走
    # 本通道；裸 shutil.rmtree 无断言仍由补丁判定）。scripts.* 不可导入环境
    # （WMI spawn 子进程）降级为不直通，补丁维持正常判定。
    try:
        from scripts.ops_guard import bulk_delete_approved as _approved
    except Exception:  # noqa: BLE001 — 见上注释，降级不阻断删除主链路
        _approved = nullcontext
    with _approved():
        if resolved.is_dir():
            shutil.rmtree(resolved, ignore_errors=ignore_errors, onerror=onerror)
        else:
            resolved.unlink()
    _audit_safe_rmtree(resolved, allowed_prefix)
    return True


def _audit_safe_rmtree(resolved: Path, allowed_prefix: str | Path) -> None:
    """授权删除留痕（批5c，2026-08-26）。

    safe_rmtree 直通期间 in-process 补丁审计短路（_BULK_APPROVED 直接 return），
    本层补落"谁经授权通道删了什么"——删除必有痕原则不缺口；落盘经统一写入
    助手（50MB 轮转）。审计文件 .runtime/gate_audit/safe_rmtree.jsonl。
    失败静默（留痕缺口不反转已完成的删除）。
    """
    try:
        from scripts.ops_guard import _get_project_root
        from zephyr.shared.io.audit_jsonl_writer import append_audit_jsonl

        append_audit_jsonl(
            _get_project_root() / ".runtime" / "gate_audit",
            "safe_rmtree.jsonl",
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "event": "safe_rmtree",
                "target": str(resolved),
                "allowed_prefix": str(allowed_prefix),
                "pid": os.getpid(),
            },
        )
    except Exception:  # noqa: BLE001 — 留痕失败不阻断删除主链路
        pass
