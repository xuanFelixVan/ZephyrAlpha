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
  python scripts/lock_files.py acquire-batch conv-abc --files-from .runtime/tmp/files.txt --session conv-abc  # 批量加锁（一次 Mutex）
  python scripts/lock_files.py release src/main.py conv-abc                   # 释放
  python scripts/lock_files.py release-batch conv-abc --files-from .runtime/tmp/files.txt --no-warn  # 批量释放
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

SSoT: quality_standard.md 维度 D-A 编码安全（扩展）
Version: 2.2.0
"""

from __future__ import annotations

import contextlib
import ctypes
import json
import os
import shutil
import subprocess
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

from check_naming_convention import check_file as _check_naming  # noqa: E402

from zephyr.shared.infra.process_pool import (
    is_pid_alive,  # noqa: E402  僵尸锁检测真源唯一（TRAE-001 is_pid_alive 真源声明，禁止本地重复定义）
)
from zephyr.shared.infra.process_pool import (  # noqa: E402
    run_subprocess_hidden,  # trae_067 铁律2 统一无窗口 subprocess 入口（B5③ _is_git_tracked 用）
)
from zephyr.shared.io.paths import REPO_ROOT  # noqa: E402

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
    # 裁定#252（2026-09-14，F2 上游治本）：锁存活=会话存活——owner.json 含 session_id
    # 时，活体探针从「领取锁的瞬时 CLI 进程 PID」切换为「SessionRegistry 会话判活」
    # （_is_session_alive：pid>0 双判活 / pid=0 心跳 90s）。瞬时进程退出不再触发僵尸
    # 清理（红蓝 v4 F2/v4.5 实弹：acquire 后锁即被自清理，防线永不命中）。无
    # session_id 的旧格式锁维持原 PID+TTL 语义（向后兼容零破坏）。会话已死则 TTL
    # 兜底仍适用（防会话僵而不沂的锁永久占用）。
    session_id = owner.get("session_id")
    if session_id:
        try:
            import sys as _sys

            if str(_SRC_ROOT) not in _sys.path:
                _sys.path.insert(0, str(_SRC_ROOT))
            from zephyr.security.access_control.session_concurrency import (
                SessionRegistry,
                _is_session_alive,
            )

            registry = SessionRegistry(REPO_ROOT)
            info = registry.get_session(str(session_id))
            if info is not None:
                import time as _time

                if _is_session_alive(info, _time.time()):
                    # 会话存活 → 锁有效（裁定#252 语义：锁的生死=会话的生死；PID 判定
                    # 不适用——瞬时 PID 必死会误杀活锁）。但 claim 自身 expires_at 已过
                    # 且会话静默超窗（T10 治本 2026-09-17）→ 回收，治"acquire 对 TTL
                    # 完全不敏感"的交接班互挡。
                    if _claim_expired_and_idle(owner, info):
                        return True
                    return False
                return True  # 会话已死（心跳超时/PID 亡/TTL 超）→ 锁 stale
            # info is None（registry 无此会话条目）：退化旧语义继续判定
        except Exception:
            pass  # registry 不可达时退回 PID+TTL 语义（fail-open，不误清活锁）
    # PID 已死 → 立即判 stale（零窗口期，治本 2026-06-30：TRAE-001 is_pid_alive 真源唯一）
    # 仅对无 session_id 的旧格式锁生效（裁定#252：带 session_id 的锁在上方已提前返回）
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


# T10 治本（2026-09-17）：裁定#252"锁存活=会话存活"短路了 claim 自身 expires_at，
# 实测会话存活+claim 过期时 acquire 恒 DENIED（对 TTL 完全不敏感，交接班互挡）。
# 对齐交接纪律 §5 三查（claim expires_at + pid 存活 + 最近是否还在 commit）：
# 过期 + 会话静默（last_activity 超 _CLAIM_IDLE_RECLAIM_SECONDS，heartbeat 不刷新
# last_activity）才可回收；过期 + 活跃仍 DENIED（它随时会重 claim，禁抢）。
_CLAIM_IDLE_RECLAIM_SECONDS = 1800.0


def _claim_expired_and_idle(owner: dict[str, Any], info: Any) -> bool:
    """claim 自身已过期且其会话超静默窗无真实治理活动 → 可回收。"""
    expires_at = owner.get("expires_at")
    if expires_at is None or time.time() <= float(expires_at):
        return False
    last_activity = float(getattr(info, "last_activity", 0.0) or 0.0)
    return (time.time() - last_activity) > _CLAIM_IDLE_RECLAIM_SECONDS


def _audit_claim_reclaim(normalized: str, prev_owner: dict[str, Any], lines: list[str]) -> None:
    """回收过期 claim 留审计（jsonl 追加 + 输出行），禁静默夺锁。"""
    reason = "expired+idle" if prev_owner.get("session_id") else "expired"
    lines.append(
        f"RECLAIMED — {normalized} 原 {prev_owner.get('owner_id', '?')} 的过期 claim 已回收"
        f"（{reason}，静默窗 {_CLAIM_IDLE_RECLAIM_SECONDS / 60:.0f}min）"
    )
    try:
        audit_path = LOCK_ROOT / "reclaim_audit.jsonl"
        audit_path.parent.mkdir(parents=True, exist_ok=True)
        with open(audit_path, "a", encoding="utf-8") as f:
            f.write(
                json.dumps(
                    {
                        "ts": time.time(),
                        "file": normalized,
                        "prev_owner": prev_owner.get("owner_id", "?"),
                        "reason": reason,
                        "by": os.environ.get("ZEPHYR_SESSION_ID", ""),
                    },
                    ensure_ascii=False,
                )
                + chr(10)
            )
    except Exception:
        pass  # 审计盘写失败不阻断回收（输出行已留痕）


def _read_owner(lock_dir: Path) -> dict[str, Any] | None:
    of = _owner_file(lock_dir)
    if not of.is_file():
        return None
    try:
        return json.loads(of.read_text(encoding="utf-8"))
    except Exception:
        return None


def _write_owner(
    lock_dir: Path,
    owner_id: str,
    task: str = "",
    ttl_s: float = DEFAULT_TTL_S,
    session_id: str = "",
) -> None:
    lock_dir.mkdir(parents=True, exist_ok=True)
    now = time.time()
    payload: dict[str, Any] = {
        "owner_id": owner_id,
        "pid": os.getpid(),
        "timestamp": now,
        "ttl_s": ttl_s,
        "expires_at": now + ttl_s,
        "task": task,
        "hostname": os.environ.get("COMPUTERNAME", "unknown"),
    }
    if session_id:
        # 裁定#252：锁存活=会话存活（owner.json 带 session_id 时 _is_stale 走会话判活）
        payload["session_id"] = session_id
    _owner_file(lock_dir).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


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


def _is_git_tracked(file_path: str) -> bool:
    """判断文件是否已被 git 跟踪（存量文件判定，B5③ 2026-09-14）。

    锁侧命名门禁只应拦"新引入的文件名违规"：存量已跟踪文件的文件名在
    创建/提交时已被提交侧裁决（check_new_files_full 对修改文件做 HEAD/工作区
    差集的历史豁免），锁侧重跑全量命名检查只会误拒存量合法文件
    （N-11/N-13 误拒实证：gate_tracked_write_allowlist.yaml 被 acquire 拒绝）。

    fail-open=False：git 不可用/异常时返回 False（视为未跟踪）→ 仍走全量命名
    检查。锁侧早期反馈成本低，宁可误拒存量也不放过新文件命名违规——与提交侧
    fail-open（不阻断 commit）方向相反是有意设计。
    """
    rel = _normalize_path(file_path)
    try:
        result = run_subprocess_hidden(
            ["git", "ls-files", "--error-unmatch", rel],
            cwd=str(REPO_ROOT),
            timeout=10,
        )
        return result.returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


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


class AcquireOptions:
    """cmd_acquire 参数包（裁定#252 同批重构，治 NO-LONG-PARAM-LIST）。

    Attributes:
        task: 锁任务描述（审计可见）
        skip_naming_check: 命名规范门禁逃生口（历史命名文件）
        ttl_minutes: 锁 TTL（分钟；None=默认 30）
        session_id: 会话绑定（裁定#252：非空时锁存活=会话存活）
    """

    def __init__(
        self,
        task: str = "",
        skip_naming_check: bool = False,
        ttl_minutes: float | None = None,
        session_id: str = "",
    ) -> None:
        self.task = task
        self.skip_naming_check = skip_naming_check
        self.ttl_minutes = ttl_minutes
        self.session_id = session_id


def _ttl_seconds(opts: AcquireOptions) -> float:
    return (opts.ttl_minutes * 60.0) if opts.ttl_minutes is not None else DEFAULT_TTL_S


def _acquire_prepare(
    file_path: str,
    owner_id: str,
    opts: AcquireOptions,
    *,
    tracked: bool | None = None,
) -> tuple[int, str, list[str], bool]:
    """加锁前半程：命名门禁 + 原子目录创建，**不碰 registry**（登记交调用方）。

    registry 侧是整表 read-modify-write + fsync + 全局 Mutex，逐件登记把 476 件
    claim 推到 ~10 分钟（P2-1 出仓战役实证）；前半程单独成函数后，批量入口可
    共享一次 Mutex 与一次 git tracked 判定。

    Args:
        tracked: 预取的"是否 git 跟踪"判定（None=自查；批量入口传共享结果）。

    Returns:
        (退出码, 归一化相对路径, 输出行, 本次是否新建锁目录)——重入不新建。
    """
    normalized = _normalize_path(file_path)
    lock_dir = _lock_dir(file_path)
    ttl_s = _ttl_seconds(opts)
    lines: list[str] = []

    # 命名规范门禁：写入前校验文件名合规性（可跳过，用于历史命名文件）
    # B5③(2026-09-14)：存量已跟踪文件跳过——文件名在创建/提交时已裁决，提交侧
    # 对修改文件本有历史豁免，锁侧重跑全量检查只会误拒存量合法文件
    # （N-11/N-13 误拒实证）。未跟踪新文件仍全量检查（早期反馈，无冤案）。
    # skip_naming_check 保留（显式逃生口，测试与特殊场景已在使用）。
    if tracked is None:
        tracked = _is_git_tracked(normalized)
    if not opts.skip_naming_check and not tracked:
        naming_violations = _check_naming(
            normalized, Path(REPO_ROOT / normalized) if (REPO_ROOT / normalized).exists() else None, REPO_ROOT
        )
        if naming_violations:
            lines.append(f"NAMING VIOLATION — {normalized} 命名不合规，拒绝写入：")
            for v in naming_violations:
                lines.append(f"  [{v.rule}] {v.message}")
            return 1, normalized, lines, False

    if lock_dir.is_dir():
        if _is_stale(lock_dir):
            prev_owner = _read_owner(lock_dir)
            _cleanup_stale(lock_dir)
            if prev_owner:
                _audit_claim_reclaim(normalized, prev_owner, lines)
        else:
            owner = _read_owner(lock_dir)
            existing_owner = owner.get("owner_id", "unknown") if owner else "unknown"
            if existing_owner == owner_id:
                lines.append(f"OK — {normalized} 已被你持有（重入）")
                return 0, normalized, lines, False
            if owner and owner.get("expires_at") is not None and time.time() > float(owner["expires_at"]):
                # T10 治本：DENIED 也要给三查实情——claim 已过期但会话仍活跃（未达
                # 静默窗），禁抢但如实告知可回收条件，禁一条 DENIED 走天下
                lines.append(
                    f"DENIED — {normalized} 已被 {existing_owner} 锁定"
                    f"（claim 已过期 {max(0, int((time.time() - float(owner['expires_at'])) / 60))}min，"
                    f"但会话仍活跃（最后活动 <{_CLAIM_IDLE_RECLAIM_SECONDS / 60:.0f}min）——"
                    "过期+静默才可回收，等其重 claim 或协调）"
                )
            else:
                lines.append(f"DENIED — {normalized} 已被 {existing_owner} 锁定")
            existing_task = owner.get("task", "") if owner else ""
            if existing_task:
                lines.append(f"  对方任务: {existing_task}")
            lines.append("  请等待对方释放或协调后重试")
            return 1, normalized, lines, False

    try:
        os.makedirs(lock_dir, exist_ok=False)
        _write_owner(lock_dir, owner_id, opts.task, ttl_s, opts.session_id)
    except FileExistsError:
        if _is_stale(lock_dir):
            _cleanup_stale(lock_dir)
            try:
                os.makedirs(lock_dir, exist_ok=False)
                _write_owner(lock_dir, owner_id, opts.task, ttl_s, opts.session_id)
            except FileExistsError:
                owner = _read_owner(lock_dir)
                existing_owner = owner.get("owner_id", "unknown") if owner else "unknown"
                lines.append(f"DENIED — {normalized} 已被 {existing_owner} 锁定（并发冲突）")
                return 1, normalized, lines, False
        else:
            owner = _read_owner(lock_dir)
            existing_owner = owner.get("owner_id", "unknown") if owner else "unknown"
            lines.append(f"DENIED — {normalized} 已被 {existing_owner} 锁定")
            return 1, normalized, lines, False

    lines.append(f"ACQUIRED — {normalized} 已锁定")
    lines.append(f"  持有者: {owner_id}")
    if opts.session_id:
        lines.append(f"  会话绑定: {opts.session_id}（裁定#252：锁存活=会话存活）")
    lines.append(f"  TTL: {ttl_s / 60.0:g} 分钟（到期自动过期）")
    if opts.task:
        lines.append(f"  任务: {opts.task}")
    return 0, normalized, lines, True


def cmd_acquire(
    file_path: str,
    owner_id: str,
    options: AcquireOptions | None = None,
) -> int:
    opts = options or AcquireOptions()
    _ensure_lock_root()
    rc, normalized, lines, created = _acquire_prepare(file_path, owner_id, opts)

    if created and not _add_to_registry(file_path, owner_id, opts.task, _ttl_seconds(opts)):
        # §7.28 Mutex 超时——回滚锁目录，避免 owner.json 存在但 registry 漏登记的半锁状态
        shutil.rmtree(_lock_dir(file_path), ignore_errors=True)
        print(f"DENIED — {normalized} registry 互斥锁超时（5s），请重试")
        return 1
    for ln in lines:
        print(ln)
    return rc


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


def _release_prepare(file_path: str, owner_id: str, *, warn: bool = True) -> tuple[int, str, list[str], bool]:
    """释放锁前半程：归属判定 + 锁目录清理（registry 摘除交调用方批量完成）。

    Returns:
        (退出码, 归一化相对路径, 输出行, 是否需从 registry 摘除)。
        未被锁定/孤儿锁已清理同样返回需摘除（幂等，摘不存在的路径无害）。
    """
    normalized = _normalize_path(file_path)
    lock_dir = _lock_dir(file_path)
    lines: list[str] = []

    if not lock_dir.is_dir():
        lines.append(f"NOT FOUND — {normalized} 未被锁定")
        return 0, normalized, lines, False

    owner = _read_owner(lock_dir)
    if owner is None:
        shutil.rmtree(lock_dir, ignore_errors=True)
        lines.append(f"RELEASED — {normalized} （孤儿锁，已清理）")
        return 0, normalized, lines, True

    if owner.get("owner_id") != owner_id:
        lines.append(f"DENIED — {normalized} 被 {owner.get('owner_id')} 持有，你不能释放")
        return 1, normalized, lines, False

    # DM-202919: 释放锁前检查未提交修改（仅警告，不阻止）
    if warn:
        _warn_if_uncommitted(file_path)

    shutil.rmtree(lock_dir, ignore_errors=True)
    lines.append(f"RELEASED — {normalized} 已释放")
    return 0, normalized, lines, True


def cmd_release(file_path: str, owner_id: str) -> int:
    _ensure_lock_root()
    rc, _normalized, lines, purge = _release_prepare(file_path, owner_id)
    if purge and not _remove_from_registry(file_path):
        print(f"DENIED — {file_path} registry 互斥锁超时（5s），请重试")
        return 1
    for ln in lines:
        print(ln)
    return rc


def _tracked_paths_batch(paths: list[str]) -> set[str]:
    """git ls-files 分片批量判定"已跟踪"子集（返回归一化相对路径）。

    逐件 ``--error-unmatch`` 每件一个子进程，千件级 claim 因此落到分钟级。
    git 不可用/异常时退回逐件 ``_is_git_tracked``（宁可误拒存量也不放过命名违规，
    与 B5③ 判定方向一致）。
    """
    tracked: set[str] = set()
    chunk = 200
    for i in range(0, len(paths), chunk):
        sub = [_normalize_path(p) for p in paths[i : i + chunk]]
        try:
            result = run_subprocess_hidden(
                ["git", "ls-files", "--", *sub],
                cwd=str(REPO_ROOT),
                timeout=60,
            )
        except (OSError, subprocess.SubprocessError):
            result = None
        if result is None or result.returncode != 0:
            for p in sub:
                if _is_git_tracked(p):
                    tracked.add(p)
            continue
        tracked.update(_normalize_path(ln) for ln in result.stdout.splitlines() if ln.strip())
    return tracked


def cmd_acquire_batch(
    owner_id: str,
    file_paths: list[str],
    options: AcquireOptions | None = None,
) -> int:
    """批量加锁：一次 git tracked 判定 + 一次 registry 临界区登记。

    Args:
        owner_id: 持有者标识。
        file_paths: 待锁文件（相对仓库根；重复项去重后处理）。
        options: 与单件 acquire 同义（task/ttl/session_id/skip_naming_check）。

    Returns:
        0=全部获得（含重入）；1=存在 DENIED/登记失败（件级行已逐条打印）。
    """
    opts = options or AcquireOptions()
    _ensure_lock_root()
    paths = list(dict.fromkeys(_normalize_path(p) for p in file_paths if p.strip()))
    if not paths:
        print("ERROR — 批量加锁清单为空")
        return 1

    tracked = _tracked_paths_batch(paths)
    ok_paths: list[str] = []
    created: list[str] = []
    denied = 0
    for p in paths:
        rc, _norm, lines, is_new = _acquire_prepare(p, owner_id, opts, tracked=(p in tracked))
        for ln in lines:
            print(ln)
        if rc == 0:
            ok_paths.append(p)
            if is_new:
                created.append(p)
        else:
            denied += 1

    if created and not _add_many_to_registry(created, owner_id, opts.task, _ttl_seconds(opts)):
        # Mutex 超时——回滚本次新建的全部锁目录，避免半锁状态
        for p in created:
            shutil.rmtree(_lock_dir(p), ignore_errors=True)
        print(f"DENIED — registry 互斥锁超时（5s），本次 {len(created)} 个新锁已回滚")
        return 1

    print(f"BATCH-SUMMARY — acquired={len(ok_paths)} denied={denied} total={len(paths)}")
    return 1 if denied else 0


def cmd_release_batch(owner_id: str, file_paths: list[str], *, warn: bool = True) -> int:
    """批量释放：件级清理 + 一次 registry 临界区摘除。

    warn=False 跳过逐件 git status 未提交检查（千件级释放该项本身就是分钟级）。
    """
    _ensure_lock_root()
    paths = list(dict.fromkeys(_normalize_path(p) for p in file_paths if p.strip()))
    if not paths:
        print("ERROR — 批量释放清单为空")
        return 1

    purge: list[str] = []
    denied = 0
    for p in paths:
        rc, _norm, lines, need_purge = _release_prepare(p, owner_id, warn=warn)
        for ln in lines:
            print(ln)
        if rc == 0:
            if need_purge:
                purge.append(p)
        else:
            denied += 1

    if purge and not _remove_many_from_registry(purge):
        print(f"DENIED — registry 互斥锁超时（5s），本次 {len(purge)} 个摘除未落")
        return 1

    print(f"BATCH-SUMMARY — released={len(paths) - denied} denied={denied} total={len(paths)}")
    return 1 if denied else 0


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


def _add_many_to_registry(file_paths: list[str], owner_id: str, task: str = "", ttl_s: float = DEFAULT_TTL_S) -> bool:
    """批量登记锁进 registry：一次 Mutex + 一次整表写回（§7.28 临界区内 RMW）。

    逐件调用时整表重写 N 次——千件级 claim 因此落到分钟级；批量入口共享本函数
    的一次临界区。超时/失败返回 False（调用方负责回滚已建的锁目录）。
    """
    with _registry_mutex() as acquired:
        if not acquired:
            return False
        registry = _load_registry()
        locks = registry.setdefault("locks", {})
        now = time.time()
        for file_path in file_paths:
            normalized = _normalize_path(file_path)
            locks[normalized] = {
                "owner_id": owner_id,
                "task": task,
                "timestamp": now,
                "ttl_s": ttl_s,
                "expires_at": now + ttl_s,
                "pid": os.getpid(),
            }
        _save_registry(registry)
        return True


def _remove_many_from_registry(file_paths: list[str]) -> bool:
    """批量从 registry 移除锁（一次 Mutex 临界区）。超时/失败返回 False。"""
    with _registry_mutex() as acquired:
        if not acquired:
            return False
        registry = _load_registry()
        locks = registry.get("locks", {})
        for file_path in file_paths:
            locks.pop(_normalize_path(file_path), None)
        _save_registry(registry)
        return True


def _add_to_registry(file_path: str, owner_id: str, task: str = "", ttl_s: float = DEFAULT_TTL_S) -> bool:
    """登记锁进 registry（§7.28 Mutex 临界区内 RMW）。超时/失败返回 False。"""
    return _add_many_to_registry([file_path], owner_id, task, ttl_s)


def _remove_from_registry(file_path: str) -> bool:
    """从 registry 移除锁（§7.28 Mutex 临界区内 RMW）。超时/失败返回 False。"""
    return _remove_many_from_registry([file_path])


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
    rc = cmd_acquire(file_path, session_id, AcquireOptions(task=task))
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

    rc = cmd_acquire(file_path, session_id, AcquireOptions(task=task))
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
    print("  acquire-batch <owner> --files-from <清单> | --files a,b  批量加锁（一次 Mutex+一次 git 判定）")
    print("            [--task <desc>] [--ttl <分钟>] [--session <sid>] [--skip-naming-check]")
    print("  release   <file> <owner>  释放文件锁")
    print("  release-batch <owner> --files-from <清单> [--no-warn]   批量释放（一次 Mutex 摘除）")
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


_VALUE_OPTS = ("--task", "--ttl", "--session", "--files", "--files-from")


def _parse_ttl_opt(args: list[str]) -> tuple[float | None, bool]:
    """解析 --ttl（分钟）。返回 (ttl_minutes|None, 是否出错)；出错已打印原因。"""
    ttl_raw = _parse_opt(args, "--ttl")
    if ttl_raw is None:
        return None, False
    try:
        ttl_minutes = float(ttl_raw)
    except ValueError:
        print(f"ERROR — --ttl 必须为正数（分钟），收到: {ttl_raw}")
        return None, True
    if ttl_minutes <= 0:
        print(f"ERROR — --ttl 必须为正数（分钟），收到: {ttl_raw}")
        return None, True
    return ttl_minutes, False


def _collect_path_args(args: list[str]) -> list[str] | None:
    """收集批量子命令的文件清单：--files-from <每行一路径> + --files <逗号分隔> + 位置参数。

    Returns:
        路径列表；参数误用（选项串错位/清单文件不可读）时返回 None（已打印原因）。
    """
    paths: list[str] = []
    i = 0
    while i < len(args):
        tok = args[i]
        if tok == "--files-from":
            i += 1
            if i >= len(args):
                print("ERROR — --files-from 缺少清单文件路径")
                return None
            try:
                lines = Path(args[i]).read_text(encoding="utf-8").splitlines()
            except OSError as e:
                print(f"ERROR — --files-from 清单读取失败: {e}")
                return None
            paths.extend(ln.strip() for ln in lines if ln.strip() and not ln.strip().startswith("#"))
            i += 1
            continue
        if tok == "--files":
            i += 1
            if i >= len(args):
                print("ERROR — --files 缺少逗号分隔清单")
                return None
            paths.extend(p.strip() for p in args[i].split(",") if p.strip())
            i += 1
            continue
        if tok in _VALUE_OPTS:
            i += 2  # 跳过取值型选项
            continue
        if tok.startswith("--"):
            i += 1  # 布尔型开关（--skip-naming-check / --no-warn）
            continue
        f = _validate_file_arg(tok)
        if f is None:
            return None
        paths.append(f)
        i += 1
    return paths


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
        ttl_minutes, ttl_err = _parse_ttl_opt(args)
        if ttl_err:
            return 1
        # 裁定#252：--session 绑定锁存活=会话存活（owner.json 写 session_id，
        # _is_stale 走 SessionRegistry 会话判活；缺省退化旧 PID+TTL 语义）
        bind_session = _parse_opt(args, "--session") or ""
        f = _validate_file_arg(args[1])
        if f is None:
            return 1
        return cmd_acquire(f, args[2], AcquireOptions(task=task, skip_naming_check=skip_naming, ttl_minutes=ttl_minutes, session_id=bind_session))

    if cmd == "acquire-batch" and len(args) >= 2:
        ttl_minutes_b, err = _parse_ttl_opt(args)
        if err:
            return 1
        paths = _collect_path_args(args[2:])
        if paths is None:
            return 1
        return cmd_acquire_batch(
            args[1],
            paths,
            AcquireOptions(
                task=_parse_opt(args, "--task") or "",
                skip_naming_check="--skip-naming-check" in args,
                ttl_minutes=ttl_minutes_b,
                session_id=_parse_opt(args, "--session") or "",
            ),
        )

    if cmd == "release-batch" and len(args) >= 2:
        paths = _collect_path_args(args[2:])
        if paths is None:
            return 1
        return cmd_release_batch(args[1], paths, warn=("--no-warn" not in args))

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
