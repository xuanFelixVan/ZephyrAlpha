# [BLUEPRINT] MOD-INF-005 | scripts/lock_files.py | §
# [MODULE] scripts.lock_files
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-005 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
lock_files.py —— AI 对话文件锁协议（硬规则执行工具）

痛点：多个 AI 对话同时修改同一文件 → 编码损坏、修改丢失、竞态条件
解决：基于原子目录创建的跨进程文件锁 + 锁注册表

对标：
  - K8s ResourceQuota（资源互斥）
  - etcd 分布式锁（TTL + 租约续期）
  - Git pre_commit hooks（门禁阻断）

设计原则：
  - 原子目录创建（os.makedirs exist_ok=False）→ 互斥保证
  - TTL + PID 检测 → 死锁自动清理
  - 零外部依赖 → 纯标准库
  - CLI 友好 → 一条命令完成所有操作

锁目录结构：
  .ailocks/
  ├── registry.json          # 锁注册表（人类+机器可读）
  └── {sanitized_path}.lock/ # 每个文件的锁目录
      └── owner.json         # {owner_id, pid, timestamp, task}

使用：
  python scripts/lock_files.py status                    # 查看所有锁
  python scripts/lock_files.py check src/main.py         # 检查某文件是否被锁
  python scripts/lock_files.py acquire src/main.py conv-abc --task "重构认证" [--ttl 30]  # 加锁（--ttl 分钟）
  python scripts/lock_files.py release src/main.py conv-abc                   # 释放
  python scripts/lock_files.py release-all conv-abc                           # 批量释放
  python scripts/lock_files.py list [--session conv-abc]                      # 列出锁（可按持有者过滤）
  python scripts/lock_files.py cleanup                                       # 清理死锁

AI 施工铁律：
  任何文件修改操作前 MUST 执行 check → 被锁则拒绝操作
  任何文件修改操作前 MUST 执行 acquire → 获取失败则拒绝操作
  任何文件修改完成后 MUST 执行 release → 释放锁给他人

并发安全（65 memo §7.28）：
  registry.json 所有 read-modify-write 经 Windows 全局命名 Mutex
  （Global\\ZephyrLockFilesRegistry，5s 超时）串行化；写入先落 tmp（flush+fsync）
  再 os.replace 原子替换，防崩溃半成品。

SSoT: AGENTS.md §4 编码安全（扩展）
Version: 2.1.0
"""

from __future__ import annotations

import contextlib
import ctypes
import json
import os
import shutil
import sys
import time
from pathlib import Path
from typing import Any

_PROJECT_ROOT = Path(__file__).resolve().parent.parent  # bootstrap: scripts/ -> root
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))
_SRC_ROOT = _PROJECT_ROOT / "src"
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))
sys.path.insert(0, str(_PROJECT_ROOT / "scripts" / "governance" / "d3_metadata"))

from zephyr.shared.io.paths import REPO_ROOT  # noqa: E402
from zephyr.shared.infra.process_pool import is_pid_alive  # noqa: E402  僵尸锁检测真源唯一（AGENTS.md §8 is_pid_alive 真源声明，禁止本地重复定义）
from check_naming_convention import check_file as _check_naming  # noqa: E402

LOCK_ROOT = REPO_ROOT / ".ailocks"
# TTL 真源：trae_001_file_operation_security.yaml ttl_design section
# 文件锁 TTL=1800s（AI 对话级锁，30min）；session TTL=3600s（session 生命周期，差异化设计合理，禁止统一）
DEFAULT_TTL_S = 1800.0  # 30 分钟——超时未释放视为死锁（AI 对话级锁）
REGISTRY_PATH = LOCK_ROOT / "registry.json"

# ── §7.28 registry.json 并发安全：Windows 全局命名 Mutex ──
# 26 session 并发 read-modify-write registry.json 必丢锁（§3.12 grite C2 实证）。
# 所有 RMW 路径必须进 _registry_mutex() 临界区；超时返回 False → 调用方 DENIED。
_REGISTRY_MUTEX_NAME = r"Global\ZephyrLockFilesRegistry"
_REGISTRY_MUTEX_TIMEOUT_MS = 5000

try:
    _kernel32 = ctypes.windll.kernel32  # type: ignore[attr-defined]
except AttributeError:  # 非 Windows 平台：退化为直通（本仓施工平台为 Windows，见 65 memo §5.3）
    _kernel32 = None  # type: ignore[assignment]


@contextlib.contextmanager
def _registry_mutex():
    """全局命名 Mutex 串行化 registry RMW。yield True=获得锁，False=超时/失败。"""
    if _kernel32 is None:
        yield True
        return
    handle = _kernel32.CreateMutexW(None, False, _REGISTRY_MUTEX_NAME)
    if not handle:
        yield False
        return
    acquired = False
    try:
        rc = _kernel32.WaitForSingleObject(handle, _REGISTRY_MUTEX_TIMEOUT_MS)
        # WAIT_OBJECT_0(0x0) 获得；WAIT_ABANDONED(0x80) 前持有者崩溃未释放，所有权转移给本进程
        acquired = rc in (0x0, 0x80)
        yield acquired
    finally:
        if acquired:
            _kernel32.ReleaseMutex(handle)
        _kernel32.CloseHandle(handle)


def _ensure_lock_root() -> None:
    LOCK_ROOT.mkdir(parents=True, exist_ok=True)


def _sanitize_path(file_path: str) -> str:
    rel = Path(file_path)
    if rel.is_absolute():
        try:
            rel = rel.relative_to(REPO_ROOT)
        except ValueError:
            pass
    sanitized = str(rel).replace("\\", ".").replace("/", ".").replace("..", "_dotdot_")
    sanitized = "".join(c for c in sanitized if c.isalnum() or c in "._-")
    return sanitized.lower()[:120]


def _lock_dir(file_path: str) -> Path:
    return LOCK_ROOT / (_sanitize_path(file_path) + ".lock")


def _owner_file(lock_dir: Path) -> Path:
    return lock_dir / "owner.json"


def _is_stale(lock_dir: Path) -> bool:
    owner = _read_owner(lock_dir)
    if owner is None:
        # owner.json 不存在 — 锁可能正在创建中（makedirs 成功但 _write_owner 还没执行）
        # 不判定为 stale，避免误清理正在创建的锁（race condition 修复）
        return False
    # PID 已死 → 立即判 stale（零窗口期，治本 2026-06-30：AGENTS.md §8 L273 is_pid_alive 真源唯一）
    # 不靠 TTL 30min 过期——进程崩溃时锁文件残留，PID 已死立即清理
    pid = owner.get("pid", 0)
    if pid and not is_pid_alive(pid):
        return True
    # TTL 判定：优先 expires_at（v2.1.0 --ttl 扩展），旧格式锁回退 timestamp+DEFAULT_TTL_S
    expires_at = owner.get("expires_at")
    if expires_at is not None:
        return time.time() > expires_at
    ts = owner.get("timestamp", 0.0)
    if time.time() - ts > DEFAULT_TTL_S:
        return True
    return False


def _read_owner(lock_dir: Path) -> dict[str, Any] | None:
    of = _owner_file(lock_dir)
    if not of.is_file():
        return None
    try:
        return json.loads(of.read_text(encoding="utf-8"))
    except Exception:
        return None


def _write_owner(lock_dir: Path, owner_id: str, task: str = "", ttl_s: float = DEFAULT_TTL_S) -> None:
    lock_dir.mkdir(parents=True, exist_ok=True)
    now = time.time()
    _owner_file(lock_dir).write_text(
        json.dumps(
            {
                "owner_id": owner_id,
                "pid": os.getpid(),
                "timestamp": now,
                "ttl_s": ttl_s,
                "expires_at": now + ttl_s,
                "task": task,
                "hostname": os.environ.get("COMPUTERNAME", "unknown"),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def _cleanup_stale(lock_dir: Path) -> bool:
    try:
        shutil.rmtree(lock_dir, ignore_errors=True)
        return True
    except Exception:
        return False


def _load_registry() -> dict[str, Any]:
    _ensure_lock_root()
    if REGISTRY_PATH.is_file():
        try:
            return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"version": "1.0.0", "locks": {}}


def _save_registry(registry: dict[str, Any]) -> None:
    _ensure_lock_root()
    registry["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    tmp_path = f"{REGISTRY_PATH}.{os.getpid()}.tmp"
    try:
        # §7.28 原子写：tmp 文件 flush+fsync 落盘后再 os.replace（Windows 原子替换），防崩溃半成品
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(json.dumps(registry, ensure_ascii=False, indent=2))
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, REGISTRY_PATH)
    except PermissionError:
        try:
            os.remove(tmp_path)
        except OSError:
            pass


def _normalize_path(file_path: str) -> str:
    p = Path(file_path)
    if p.is_absolute():
        try:
            return str(p.relative_to(REPO_ROOT)).replace("\\", "/")
        except ValueError:
            return str(p).replace("\\", "/")
    return str(p).replace("\\", "/")


def cmd_status() -> int:
    _ensure_lock_root()
    registry = _load_registry()
    locks = registry.get("locks", {})

    if not locks:
        print("CLEAN — 当前无任何文件锁")
        return 0

    print(f"LOCKED — {len(locks)} 个文件被锁定：\n")
    for file_path, info in sorted(locks.items()):
        owner = info.get("owner_id", "unknown")
        task = info.get("task", "")
        ts = info.get("timestamp", 0)
        age = time.time() - ts
        age_str = f"{age:.0f}s" if age < 60 else f"{age / 60:.1f}m"
        task_str = f" [{task}]" if task else ""
        print(f"  {file_path}")
        print(f"    持有者: {owner}{task_str}")
        print(f"    已锁定: {age_str}")

    return 0


def cmd_check(file_path: str) -> int:
    _ensure_lock_root()
    normalized = _normalize_path(file_path)
    lock_dir = _lock_dir(file_path)

    if not lock_dir.is_dir():
        print(f"FREE — {normalized} 未被锁定")
        return 0

    if _is_stale(lock_dir):
        _cleanup_stale(lock_dir)
        _remove_from_registry(file_path)
        print(f"FREE — {normalized} 的死锁已被自动清理")
        return 0

    owner = _read_owner(lock_dir)
    if owner is None:
        print(f"FREE — {normalized} 未被锁定")
        return 0

    print(f"LOCKED — {normalized}")
    print(f"  持有者: {owner.get('owner_id', 'unknown')}")
    task = owner.get("task", "")
    if task:
        print(f"  任务: {task}")
    ts = owner.get("timestamp", 0)
    age = time.time() - ts
    age_str = f"{age:.0f}s" if age < 60 else f"{age / 60:.1f}m"
    print(f"  已锁定: {age_str}")
    return 1


def cmd_acquire(
    file_path: str,
    owner_id: str,
    task: str = "",
    skip_naming_check: bool = False,
    ttl_minutes: float | None = None,
) -> int:
    _ensure_lock_root()
    normalized = _normalize_path(file_path)
    lock_dir = _lock_dir(file_path)
    ttl_s = (ttl_minutes * 60.0) if ttl_minutes is not None else DEFAULT_TTL_S

    # 命名规范门禁：写入前校验文件名合规性（可跳过，用于历史命名文件）
    if not skip_naming_check:
        naming_violations = _check_naming(
            normalized, Path(REPO_ROOT / normalized) if (REPO_ROOT / normalized).exists() else None, REPO_ROOT
        )
        if naming_violations:
            print(f"NAMING VIOLATION — {normalized} 命名不合规，拒绝写入：")
            for v in naming_violations:
                print(f"  [{v.rule}] {v.message}")
            return 1

    if lock_dir.is_dir():
        if _is_stale(lock_dir):
            _cleanup_stale(lock_dir)
        else:
            owner = _read_owner(lock_dir)
            existing_owner = owner.get("owner_id", "unknown") if owner else "unknown"
            if existing_owner == owner_id:
                print(f"OK — {normalized} 已被你持有（重入）")
                return 0
            print(f"DENIED — {normalized} 已被 {existing_owner} 锁定")
            existing_task = owner.get("task", "") if owner else ""
            if existing_task:
                print(f"  对方任务: {existing_task}")
            print("  请等待对方释放或协调后重试")
            return 1

    try:
        os.makedirs(lock_dir, exist_ok=False)
        _write_owner(lock_dir, owner_id, task, ttl_s)
    except FileExistsError:
        if _is_stale(lock_dir):
            _cleanup_stale(lock_dir)
            try:
                os.makedirs(lock_dir, exist_ok=False)
                _write_owner(lock_dir, owner_id, task, ttl_s)
            except FileExistsError:
                owner = _read_owner(lock_dir)
                existing_owner = owner.get("owner_id", "unknown") if owner else "unknown"
                print(f"DENIED — {normalized} 已被 {existing_owner} 锁定（并发冲突）")
                return 1
        else:
            owner = _read_owner(lock_dir)
            existing_owner = owner.get("owner_id", "unknown") if owner else "unknown"
            print(f"DENIED — {normalized} 已被 {existing_owner} 锁定")
            return 1

    if not _add_to_registry(file_path, owner_id, task, ttl_s):
        # §7.28 Mutex 超时——回滚锁目录，避免 owner.json 存在但 registry 漏登记的半锁状态
        shutil.rmtree(lock_dir, ignore_errors=True)
        print(f"DENIED — {normalized} registry 互斥锁超时（5s），请重试")
        return 1
    print(f"ACQUIRED — {normalized} 已锁定")
    print(f"  持有者: {owner_id}")
    print(f"  TTL: {ttl_s / 60.0:g} 分钟（到期自动过期）")
    if task:
        print(f"  任务: {task}")
    return 0


def _warn_if_uncommitted(file_path: str) -> None:
    """DM-202919: 释放锁前检查文件是否有未提交修改，有则打印WARNING。

    不阻止释放，仅警告。防止AI释放锁后不提交导致修改丢失。
    检查范围: 工作区修改未暂存 / 暂存未提交 / 未跟踪文件。
    """
    import subprocess

    abs_path = Path(file_path).resolve()
    if not abs_path.exists():
        return  # 文件不存在（可能已删除），跳过检查

    try:
        result = subprocess.run(
            ["git", "status", "--porcelain", "--", str(abs_path)],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=str(abs_path.parent),
        )
    except (subprocess.SubprocessError, OSError):
        return  # git 命令失败（可能不在git仓库），跳过检查

    if result.returncode != 0:
        return  # git 命令失败，跳过检查

    output = result.stdout.strip()
    if output:
        print(f"WARNING — 文件有未提交修改，请先 git commit：{file_path}")
        for line in output.splitlines():
            print(f"  git status: {line}")


def cmd_release(file_path: str, owner_id: str) -> int:
    _ensure_lock_root()
    normalized = _normalize_path(file_path)
    lock_dir = _lock_dir(file_path)

    if not lock_dir.is_dir():
        print(f"NOT FOUND — {normalized} 未被锁定")
        return 0

    owner = _read_owner(lock_dir)
    if owner is None:
        shutil.rmtree(lock_dir, ignore_errors=True)
        _remove_from_registry(file_path)
        print(f"RELEASED — {normalized} （孤儿锁，已清理）")
        return 0

    if owner.get("owner_id") != owner_id:
        print(f"DENIED — {normalized} 被 {owner.get('owner_id')} 持有，你不能释放")
        return 1

    # DM-202919: 释放锁前检查未提交修改（仅警告，不阻止）
    _warn_if_uncommitted(file_path)

    shutil.rmtree(lock_dir, ignore_errors=True)
    _remove_from_registry(file_path)
    print(f"RELEASED — {normalized} 已释放")
    return 0


def cmd_release_all(owner_id: str) -> int:
    _ensure_lock_root()
    # 警告检查（git status 慢操作）在 Mutex 外做，缩短临界区
    candidates = [fp for fp, info in _load_registry().get("locks", {}).items() if info.get("owner_id") == owner_id]
    for fp in candidates:
        _warn_if_uncommitted(fp)  # DM-202919: 释放锁前检查未提交修改（仅警告，不阻止）

    with _registry_mutex() as acquired:
        if not acquired:
            print("DENIED — registry 互斥锁超时（5s），请重试")
            return 1
        registry = _load_registry()  # 临界区内重读，防竞态
        locks = registry.get("locks", {})
        released = []
        for file_path, info in list(locks.items()):
            if info.get("owner_id") == owner_id:
                shutil.rmtree(_lock_dir(file_path), ignore_errors=True)
                del locks[file_path]
                released.append(file_path)
        if released:
            registry["locks"] = locks
            _save_registry(registry)

    if released:
        print(f"RELEASED — {len(released)} 个锁已释放：")
        for fp in released:
            print(f"  {fp}")
    else:
        print(f"CLEAN — {owner_id} 没有持有任何锁")

    return 0


def cmd_cleanup() -> int:
    _ensure_lock_root()
    with _registry_mutex() as acquired:
        if not acquired:
            print("DENIED — registry 互斥锁超时（5s），请重试")
            return 1
        registry = _load_registry()
        locks = registry.get("locks", {})
        cleaned = []
        for file_path in list(locks.keys()):
            lock_dir = _lock_dir(file_path)
            if not lock_dir.is_dir() or _is_stale(lock_dir):
                shutil.rmtree(lock_dir, ignore_errors=True)
                del locks[file_path]
                cleaned.append(file_path)
        if cleaned:
            registry["locks"] = locks
            _save_registry(registry)

    if cleaned:
        print(f"CLEANED — {len(cleaned)} 个死锁已清理：")
        for fp in cleaned:
            print(f"  {fp}")
    else:
        print("CLEAN — 无死锁需要清理")

    return 0


def cmd_list(session_id: str | None = None) -> int:
    """§11.2.2 五命令之 list：列出活跃锁，可按持有者过滤。"""
    _ensure_lock_root()
    locks = _load_registry().get("locks", {})
    if session_id is not None:
        locks = {fp: info for fp, info in locks.items() if info.get("owner_id") == session_id}

    scope = f"持有者 {session_id} " if session_id else ""
    if not locks:
        print(f"CLEAN — {scope}无任何文件锁")
        return 0

    print(f"LOCKED — {scope}{len(locks)} 个文件锁：\n")
    now = time.time()
    for file_path, info in sorted(locks.items()):
        owner = info.get("owner_id", "unknown")
        task = info.get("task", "")
        task_str = f" [{task}]" if task else ""
        expires_at = info.get("expires_at")
        if expires_at is not None:
            remain = expires_at - now
            ttl_str = f"剩余 {remain / 60.0:.1f}m" if remain > 0 else "已过期（待 cleanup）"
        else:
            ts = info.get("timestamp", 0)
            ttl_str = f"已锁定 {(now - ts) / 60.0:.1f}m（旧格式无 expires_at）"
        print(f"  {file_path}")
        print(f"    持有者: {owner}{task_str} | {ttl_str}")

    return 0


def _add_to_registry(file_path: str, owner_id: str, task: str = "", ttl_s: float = DEFAULT_TTL_S) -> bool:
    """登记锁进 registry（§7.28 Mutex 临界区内 RMW）。超时/失败返回 False。"""
    with _registry_mutex() as acquired:
        if not acquired:
            return False
        registry = _load_registry()
        normalized = _normalize_path(file_path)
        now = time.time()
        registry.setdefault("locks", {})[normalized] = {
            "owner_id": owner_id,
            "task": task,
            "timestamp": now,
            "ttl_s": ttl_s,
            "expires_at": now + ttl_s,
            "pid": os.getpid(),
        }
        _save_registry(registry)
        return True


def _remove_from_registry(file_path: str) -> bool:
    """从 registry 移除锁（§7.28 Mutex 临界区内 RMW）。超时/失败返回 False。"""
    with _registry_mutex() as acquired:
        if not acquired:
            return False
        registry = _load_registry()
        normalized = _normalize_path(file_path)
        registry.get("locks", {}).pop(normalized, None)
        _save_registry(registry)
        return True


class FileLockedError(Exception):
    """文件被其他session锁定时抛出。"""

    def __init__(self, file_path: str, owner_id: str, task: str = ""):
        self.file_path = file_path
        self.owner_id = owner_id
        self.task = task
        msg = f"RULE-ZERO 违规: {file_path} 被 {owner_id} 锁定"
        if task:
            msg += f"（任务: {task}）"
        super().__init__(msg)


def pre_write_guard(file_path: str, session_id: str, task: str = "") -> None:
    """写前自动门禁：check + acquire 原子操作。

    文件未被锁 → 自动获取锁，调用方必须在写完后调用 cmd_release()。
    文件已被他人锁 → 抛出 FileLockedError。
    文件已被自己锁 → 静默通过（重入）。

    用法（AI工具调用链集成）:
        from lock_files import pre_write_guard, FileLockedError
        try:
            pre_write_guard("src/main.py", "session-20260611-001", "重构认证")
            # ... 执行写入 ...
        except FileLockedError as e:
            print(e)  # 报告用户，拒绝写入
        finally:
            cmd_release("src/main.py", "session-20260611-001")
    """
    rc = cmd_acquire(file_path, session_id, task)
    if rc != 0:
        lock_dir = _lock_dir(file_path)
        owner = _read_owner(lock_dir)
        owner_id = owner.get("owner_id", "unknown") if owner else "unknown"
        owner_task = owner.get("task", "") if owner else ""
        raise FileLockedError(_normalize_path(file_path), owner_id, owner_task)


class LockGuard:
    """Context manager：自动获取/释放文件锁。

    用法:
        from lock_files import LockGuard, FileLockedError
        try:
            with LockGuard("src/main.py", "session-20260611-001", "重构认证"):
                # ... 执行写入 ...
                pass
        except FileLockedError as e:
            print(e)  # 报告用户，拒绝写入
    """

    def __init__(self, file_path: str, session_id: str, task: str = ""):
        self.file_path = file_path
        self.session_id = session_id
        self.task = task
        self._acquired = False

    def __enter__(self) -> LockGuard:
        pre_write_guard(self.file_path, self.session_id, self.task)
        self._acquired = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._acquired:
            cmd_release(self.file_path, self.session_id)
            self._acquired = False


def cmd_guard_write(file_path: str, session_id: str, task: str = "") -> int:
    """CLI入口：写前自动锁检查+获取。成功exit 0，冲突exit 1。"""
    _ensure_lock_root()
    normalized = _normalize_path(file_path)
    lock_dir = _lock_dir(file_path)

    if lock_dir.is_dir() and not _is_stale(lock_dir):
        owner = _read_owner(lock_dir)
        existing_owner = owner.get("owner_id", "unknown") if owner else "unknown"
        if existing_owner != session_id:
            existing_task = owner.get("task", "") if owner else ""
            print(f"BLOCKED — {normalized} 被 {existing_owner} 锁定")
            if existing_task:
                print(f"  对方任务: {existing_task}")
            ts = owner.get("timestamp", 0) if owner else 0
            age = time.time() - ts
            age_str = f"{age:.0f}s" if age < 60 else f"{age / 60:.1f}m"
            print(f"  已锁定: {age_str}")
            return 1

    rc = cmd_acquire(file_path, session_id, task)
    if rc == 0:
        print(f"GUARD-OK — {normalized} 写前门禁通过，锁已获取")
        print(f"  写完后请执行: python scripts/lock_files.py release {normalized} {session_id}")
    return rc


def _print_help() -> None:
    print(__doc__)
    print("\n子命令：")
    print("  status                    查看所有活跃锁")
    print("  check     <file>          检查文件是否被锁（exit 0=free, 1=locked）")
    print("  acquire   <file> <owner> [--task <desc>] [--ttl <分钟>]  锁定文件（默认 30 分钟）")
    print("  release   <file> <owner>  释放文件锁")
    print("  release-all <owner>       释放该持有者的所有锁")
    print("  list      [--session <owner>]  列出活跃锁（可按持有者过滤）")
    print("  cleanup                   清理所有死锁（TTL过期/PID已死）")
    print("  guard-write <file> <session> [--task <desc>]  写前自动门禁（check+acquire原子操作）")


def _parse_opt(args: list[str], flag: str) -> str | None:
    """解析 --flag <value> 形式的可选参数，未提供返回 None。"""
    if flag in args:
        i = args.index(flag)
        if i + 1 < len(args):
            return args[i + 1]
    return None


def _validate_file_arg(arg: str) -> str | None:
    """防呆：文件参数以 -- 开头必为误用（如把 list 的 --session 写法带到 acquire）。
    仓库内合法路径不会以 -- 开头——拒绝落锁并提示正确用法（#120，AI-POT-001
    字面量 --session 垃圾锁实证）。
    """
    if arg.startswith("--"):
        print(f"ERROR — 文件参数非法（以 -- 开头，疑选项串错位）: {arg}")
        print("  正确用法: acquire <file> <owner> [--task <desc>] [--ttl <分钟>]；查锁用 list [--session <owner>]")
        return None
    return arg


def main() -> int:
    args = sys.argv[1:]

    if not args:
        _print_help()
        return 0

    cmd = args[0].lower()

    if cmd == "status":
        return cmd_status()

    if cmd == "check" and len(args) >= 2:
        f = _validate_file_arg(args[1])
        return 1 if f is None else cmd_check(f)

    if cmd == "acquire" and len(args) >= 3:
        task = _parse_opt(args, "--task") or ""
        skip_naming = "--skip-naming-check" in args
        ttl_raw = _parse_opt(args, "--ttl")
        ttl_minutes: float | None = None
        if ttl_raw is not None:
            try:
                ttl_minutes = float(ttl_raw)
                if ttl_minutes <= 0:
                    raise ValueError
            except ValueError:
                print(f"ERROR — --ttl 必须为正数（分钟），收到: {ttl_raw}")
                return 1
        f = _validate_file_arg(args[1])
        if f is None:
            return 1
        return cmd_acquire(f, args[2], task, skip_naming, ttl_minutes)

    if cmd == "release" and len(args) >= 3:
        f = _validate_file_arg(args[1])
        return 1 if f is None else cmd_release(f, args[2])

    if cmd == "release-all" and len(args) >= 2:
        return cmd_release_all(args[1])

    if cmd == "list":
        return cmd_list(_parse_opt(args, "--session"))

    if cmd == "cleanup":
        return cmd_cleanup()

    if cmd == "guard-write" and len(args) >= 3:
        task = _parse_opt(args, "--task") or ""
        f = _validate_file_arg(args[1])
        return 1 if f is None else cmd_guard_write(f, args[2], task)

    if cmd in ("help", "--help", "-h"):
        _print_help()
        return 0

    print(f"未知命令: {cmd}")
    _print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())

# ── Stage 4 公共化（2026-07-29）：public wrapper ──
def warn_if_uncommitted(file_path) -> None:
    """公共接口：warn_if_uncommitted（Stage 4 公共化）。"""
    return _warn_if_uncommitted(file_path)


# ── Stage 4 公共化（2026-07-29）：public wrapper ──
def ensure_lock_root() -> None:
    """公共接口：ensure_lock_root（Stage 4 公共化）。"""
    return _ensure_lock_root()

