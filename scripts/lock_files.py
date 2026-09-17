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
  python scripts/lock_files.py cleanup                                       # 清理死锁 + R-10 死会话遗物自动回收（--no-salvage 关闭）
  python scripts/lock_files.py salvage sess-001 [--dry-run]                  # R-10 死会话遗物回收（双证判死→merge abort+stash归档+释放claim）

AI 施工铁律：
  任何文件修改操作前 MUST 执行 check → 被锁则拒绝操作
  任何文件修改操作前 MUST 执行 acquire → 获取失败则拒绝操作
  任何文件修改完成后 MUST 执行 release → 释放锁给他人

并发安全（65 memo §7.28）：
  registry.json 所有 read-modify-write 经 Windows 全局命名 Mutex
  （Global\\ZephyrLockFilesRegistry，5s 超时）串行化；写入先落 tmp（flush+fsync）
  再 os.replace 原子替换，防崩溃半成品。

SSoT: quality_standard.md 维度 D-A 编码安全（扩展）
Version: 2.3.0
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


def cmd_cleanup(repo_root: str | Path | None = None, auto_salvage: bool = True) -> int:
    _ensure_lock_root()
    with _registry_mutex() as acquired:
        if not acquired:
            print("DENIED — registry 互斥锁超时（5s），请重试")
            return 1
        registry = _load_registry()
        locks = registry.get("locks", {})
        # R-10：候选=清扫前全部锁的持有者（须在清理循环前捕获——刚清掉的死锁
        # 所属会话同样可能有 MERGE_HEAD/staged 遗物待回收）。死会话判定与 git
        # 回收操作在 Mutex 外做（回收含 git 子进程，5s Mutex 临界区放不下；
        # 判证失败=零副作用跳过）
        salvage_candidates = sorted(
            {str(info.get("owner_id")) for info in locks.values() if isinstance(info, dict) and info.get("owner_id")}
        )
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

    # R-10 死会话遗物自动回收（lane G1，2026-09-18）：cleanup 是同族家务位
    # （RULE-GUARDIAN 班前必跑）。双证判死在 salvage_dead_session 内部——
    # 活会话/证据不足/归属不明一律跳过，cleanup 语义不因回收失败而改变。
    if auto_salvage:
        root = Path(repo_root) if repo_root else REPO_ROOT
        candidates = set(salvage_candidates)
        try:
            # 注册表侧死会话一并扫描（覆盖「零 claim 纯 MERGE_HEAD 晾置」遗物形态）
            if str(_SRC_ROOT) not in sys.path:
                sys.path.insert(0, str(_SRC_ROOT))
            from zephyr.security.access_control.session_concurrency import (
                SessionInfo,
                SessionRegistry,
                _is_session_alive,
            )

            data = SessionRegistry(root).load()
            now = time.time()
            for sid, d in data.items():
                try:
                    if not _is_session_alive(SessionInfo.from_dict(d), now):
                        candidates.add(sid)
                except Exception:
                    continue
        except Exception:
            pass  # registry 不可达——claim 侧候选仍处理（降级不阻断 cleanup）
        for sid in sorted(candidates):
            try:
                r = salvage_dead_session(sid, repo_root=root)
            except Exception as e:  # noqa: BLE001 — 单个候选回收异常不拖累其余
                print(f"SALVAGE-ERROR — {sid}: {type(e).__name__}: {e}")
                continue
            if r.dead_confirmed:
                print(
                    f"SALVAGED — 死会话 {sid} 遗物已回收"
                    f"（merge={r.merge_abort}, stash={len(r.stashed_paths)}件, "
                    f"释放claim={len(r.released_locks)}+.ailocks/{len(r.released_session_files)}.registry）"
                )
                for note in r.notes:
                    print(f"  注意: {note}")

    return 0


# ══════════════════════════════════════════════════════════════════════════════
# R-10 死会话遗物回收 + R-04 失败 claim TTL 收窄
# （lane G1，2026-09-18；真源 docs/_working/kimi_audit/S18_提交链路根因表.md R-10/R-04 行）
#
# R-10 病灶：会话死亡无遗物回收——merge 状态/staged/claim 三件套无托管
# （e19bc24c 实证：并发会话 merge 到一半死亡，MERGE_HEAD 晾置阻塞全部提交）。
# 治本：双证判死（①SessionRegistry 心跳/注册表证死 ②该会话全部 claim TTL 过期，
# 缺一不动——防误收活会话，S18 R-10 反例红线），证死后三件套一并回收：
#   ① 主区 MERGE_HEAD 归属该死会话 → git merge --abort（被并分支内容零损失）
#   ② 其 claim 路径的 staged/WIP 改动 → git stash push 归档（禁丢弃，可 pop 恢复）
#   ③ 释放其全部 claim（.ailocks + SessionRegistry 两登记处，T10 教训：两处都要放）
# 触发位选择：cleanup 自动扫描（同族家务，班前必跑）+ salvage 显式子命令——
# 不进 gateway pre-commit：门禁链 P50 已 46.4s（S18 R-03），回收是低频家务，
# 不该让每笔提交为它付墙钟。
#
# R-04 配套：shorten_claim_ttl——claim 释放从「finally 无条件」改为「成功才释放、
# 失败保留」后，原「失败释放防锁尸」动机由收窄 TTL（默认 300s，git_commit.py
# --failed-claim-ttl 参数化）+ 既有 stale 回收 + 本条 R-10 回收三层接管。
# ══════════════════════════════════════════════════════════════════════════════

SALVAGE_MERGE_GRACE_SECONDS = 300.0  # MERGE_HEAD mtime 归属窗口宽限（会话活动窗 ±5min）


class SalvageResult:
    """R-10 死会话回收结果（机读 to_dict + CLI 打印两用）。"""

    def __init__(self, session_id: str) -> None:
        self.session_id = session_id
        self.dead_confirmed = False
        self.evidence1 = ""  # ①心跳/注册表证死
        self.evidence2 = ""  # ②全部 claim TTL 过期
        self.merge_abort = "skipped"  # aborted | skipped | not_attributed | failed | dry-run
        self.merge_head_sha = ""
        self.stash_ref = ""
        self.stashed_paths: list[str] = []
        self.released_locks: list[str] = []
        self.released_session_files: list[str] = []
        self.notes: list[str] = []

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "dead_confirmed": self.dead_confirmed,
            "evidence1": self.evidence1,
            "evidence2": self.evidence2,
            "merge_abort": self.merge_abort,
            "merge_head_sha": self.merge_head_sha,
            "stash_ref": self.stash_ref,
            "stashed_paths": self.stashed_paths,
            "released_locks": self.released_locks,
            "released_session_files": self.released_session_files,
            "notes": self.notes,
        }


def _salvage_audit(record: dict[str, Any]) -> None:
    """回收审计落盘（.ailocks/salvage_audit.jsonl，fail-open 不阻断回收）。"""
    try:
        audit_path = LOCK_ROOT / "salvage_audit.jsonl"
        audit_path.parent.mkdir(parents=True, exist_ok=True)
        with open(audit_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + chr(10))
    except Exception:
        pass


def _session_claims(session_id: str) -> dict[str, dict[str, Any]]:
    """.ailocks registry 中该持有者全部 claim（归一化路径 → 条目）。"""
    return {
        fp: info
        for fp, info in _load_registry().get("locks", {}).items()
        if isinstance(info, dict) and info.get("owner_id") == session_id
    }


def _raw_session_entry(repo_root: Path, session_id: str) -> tuple[Any | None, bool]:
    """读 SessionRegistry 原始条目（绕过 get_session「死即 None」语义——
    回收恰恰要区分「条目在但已死」与「查无此会话」）。

    Returns:
        (SessionInfo | None, 条目是否存在)。registry 不可读 → (None, False)。
    """
    try:
        if str(_SRC_ROOT) not in sys.path:
            sys.path.insert(0, str(_SRC_ROOT))
        from zephyr.security.access_control.session_concurrency import (
            SessionInfo,
            SessionRegistry,
        )

        data = SessionRegistry(repo_root).load()
        if session_id not in data:
            return None, False
        return SessionInfo.from_dict(data[session_id]), True
    except Exception:
        return None, False


def _alive_sessions(repo_root: Path) -> list[Any] | None:
    """只读列出存活 SessionInfo（raw load + _is_session_alive 过滤，无 list_active 写副作用）。

    Returns:
        None=registry 不可读（归属判定按「未知」处理——拒绝 abort，防误收活会话）。
    """
    try:
        if str(_SRC_ROOT) not in sys.path:
            sys.path.insert(0, str(_SRC_ROOT))
        from zephyr.security.access_control.session_concurrency import (
            SessionInfo,
            SessionRegistry,
            _is_session_alive,
        )

        data = SessionRegistry(repo_root).load()
        now = time.time()
        return [info for info in (SessionInfo.from_dict(d) for d in data.values()) if _is_session_alive(info, now)]
    except Exception:
        return None


def _death_evidence(
    session_id: str,
    claims: dict[str, dict[str, Any]],
    repo_root: Path,
    now: float,
) -> tuple[bool, str, str, Any | None]:
    """双证判死（缺一不回收——S18 R-10 反例红线：误收活会话）。

    证据①（心跳/注册表证死）：
      - registry 有条目且 _is_session_alive=False（心跳超 90s / PID 亡 / TTL 超）→ 成立
      - registry 无条目 → 进程证据兜底：≥1 条 claim 且全部 claim PID 死/零才成立
        （零 claim 且无条目=无任何死亡证据 → 不成立）
    证据②（全部 claim TTL 过期）：
      - 有 .ailocks claim：全部 expires_at < now 才成立（任一未过期 → 不回收——
        会话可能处于心跳间隙但 claim 新鲜，正在干活）
      - 无 .ailocks claim：SessionRegistry held_files 无 TTL，仅当证据①是
        「registry 条目证死」时成立（裁定#252 锁存活=会话存活：条目死 → 持有可释放）

    Returns:
        (双证齐全, 证据①描述, 证据②描述, SessionInfo|None)
    """
    info, present = _raw_session_entry(repo_root, session_id)
    ev1 = False
    ev1_desc = ""
    if present and info is not None:
        try:
            if str(_SRC_ROOT) not in sys.path:
                sys.path.insert(0, str(_SRC_ROOT))
            from zephyr.security.access_control.session_concurrency import _is_session_alive

            ev1 = not _is_session_alive(info, now)
        except Exception:
            ev1 = False  # 判活设施异常=无法证死（fail-closed，方向=防误收）
        ev1_desc = f"registry:{'dead' if ev1 else 'alive'}"
    else:
        pids = [c.get("pid", 0) for c in claims.values()]
        if claims and all((not p) or int(p) <= 0 or not is_pid_alive(int(p)) for p in pids):
            ev1 = True
            ev1_desc = "registry-absent:all-claim-pids-dead"
        else:
            ev1_desc = "registry-absent:no-process-evidence"

    if claims:
        unexpired = [fp for fp, c in claims.items() if float(c.get("expires_at") or 0.0) >= now]
        ev2 = not unexpired
        ev2_desc = f"claims:{len(claims) - len(unexpired)}/{len(claims)} expired"
    else:
        held = list(getattr(info, "held_files", None) or []) if info is not None else []
        ev2 = (not held) or (ev1 and ev1_desc == "registry:dead")
        ev2_desc = "claims:none" if not held else f"session-held:{len(held)} releasable={ev2}"
    return ev1 and ev2, ev1_desc, ev2_desc, info


def _main_merge_head_path(repo_root: Path) -> Path:
    """主区 MERGE_HEAD 路径（回收面只覆盖主区——worktree 物理隔离，各自收尾）。"""
    return repo_root / ".git" / "MERGE_HEAD"


def _merge_head_attributed_to(
    repo_root: Path,
    session_id: str,
    info: Any | None,
    claims: dict[str, dict[str, Any]],
    now: float,
) -> tuple[bool, str]:
    """主区 MERGE_HEAD 归属判定（保守——任一不确定即不归属、拒绝 abort）。

    双条件：
      a) 无「发起时间先于 MERGE_HEAD」的存活会话——班后 cleanup 的当前会话
         start_time 晚于晾置 MERGE_HEAD mtime，天然不挡道；而 merge 进行中
         的会话 start_time 必早于 mtime → 挡住 abort（防误收）。
      b) 死会话活动窗覆盖 MERGE_HEAD mtime
         （start_time-grace ≤ mtime ≤ max(last_heartbeat, last_activity)+grace）。
    """
    mh = _main_merge_head_path(repo_root)
    if not mh.is_file():
        return False, "no-merge-head"
    try:
        mtime = mh.stat().st_mtime
    except OSError:
        return False, "merge-head-stat-failed"
    alive = _alive_sessions(repo_root)
    if alive is None:
        return False, "registry-unreadable"
    grace = SALVAGE_MERGE_GRACE_SECONDS
    owners = [s for s in alive if float(getattr(s, "start_time", 0.0) or 0.0) <= mtime + grace]
    if owners:
        return False, f"alive-sessions-predate-merge:{[s.session_id for s in owners][:5]}"
    if info is not None:
        t0 = float(getattr(info, "start_time", 0.0) or 0.0)
        t1 = max(
            float(getattr(info, "last_heartbeat", 0.0) or 0.0),
            float(getattr(info, "last_activity", 0.0) or 0.0),
        )
    else:
        t0 = min((float(c.get("timestamp", now)) for c in claims.values()), default=now)
        t1 = max(
            (float(c.get("timestamp", 0.0)) + float(c.get("ttl_s", 0.0)) for c in claims.values()),
            default=0.0,
        )
    if t0 and mtime < t0 - grace:
        return False, f"merge-head-predates-session(mtime<{t0:.0f})"
    if t1 and mtime > t1 + grace:
        return False, f"merge-head-after-session-activity(mtime>{t1:.0f})"
    return True, "attributed"


def _stash_claimed_paths(repo_root: Path, session_id: str, rel_paths: list[str]) -> tuple[str, list[str]]:
    """死会话 claim 路径的 staged/WIP 改动归档 stash。

    pathspec 限定——只动该会话名下文件，禁全量 stash 误卷他人 WIP；
    归档不丢弃（禁 git stash drop），stash 可用 pop/apply 恢复。
    无实际改动=幂等跳过（返回空 ref）。

    Returns:
        (stash_ref, 实际有改动被归档的路径)。
    """
    try:
        st = run_subprocess_hidden(
            ["git", "status", "--porcelain", "--", *rel_paths],
            cwd=str(repo_root),
            timeout=60,
        )
        if st.returncode != 0:
            return "", []
        changed = [ln[3:].strip().strip('"') for ln in st.stdout.splitlines() if ln.strip()]
        if not changed:
            return "", []
        msg = f"dead-session salvage {session_id}"
        r = run_subprocess_hidden(
            ["git", "stash", "push", "-m", msg, "--", *rel_paths],
            cwd=str(repo_root),
            timeout=120,
        )
        if r.returncode != 0 or "No local changes" in (r.stdout or ""):
            return "", []
        ref = run_subprocess_hidden(
            ["git", "rev-parse", "-q", "--verify", "refs/stash"],
            cwd=str(repo_root),
            timeout=30,
        )
        return (ref.stdout.strip() if ref.returncode == 0 else "refs/stash"), changed
    except Exception:
        return "", []


def _force_release_locks(session_id: str, rel_paths: list[str]) -> list[str]:
    """释放该持有者全部 .ailocks 锁（锁目录 + registry 条目，摘除走 Mutex 临界区）。

    死会话专用——绕过 _release_prepare 的归属校验（持有者已死，无法自释）。
    """
    released: list[str] = []
    for fp in rel_paths:
        shutil.rmtree(_lock_dir(fp), ignore_errors=True)
        released.append(_normalize_path(fp))
    if released:
        _remove_many_from_registry(released)
    return released


def _force_release_session_registry(repo_root: Path, session_id: str, info: Any | None) -> list[str]:
    """释放 SessionRegistry 侧持有并注销死会话条目（第二登记处——T10 教训两处都要放）。"""
    try:
        if str(_SRC_ROOT) not in sys.path:
            sys.path.insert(0, str(_SRC_ROOT))
        from zephyr.security.access_control.session_concurrency import SessionRegistry

        registry = SessionRegistry(repo_root)
        held = list(getattr(info, "held_files", None) or [])
        if held:
            registry.release_files_batch(session_id, held)
        registry.unregister(session_id)
        return held
    except Exception:
        return []


def salvage_dead_session(
    session_id: str,
    *,
    repo_root: str | Path | None = None,
    now: float | None = None,
    dry_run: bool = False,
) -> SalvageResult:
    """R-10 死会话遗物回收主入口：双证判死 → 三件套回收，全程审计。

    三件套：①主区归属该会话的 MERGE_HEAD → git merge --abort（被并分支零损失）；
    ②其 claim 路径 staged/WIP → git stash push 归档（禁丢弃，可 pop）；
    ③释放全部 claim（.ailocks + SessionRegistry 两登记处）。
    双证缺一 → 整体不动；MERGE_HEAD 归属不明 → 仅跳过 abort，claim 释放照常
    （锁体系证据独立成立；git 状态保守留给人工）。
    dry_run=True 只判证与归因，不动 git/锁。
    """
    res = SalvageResult(session_id)
    root = Path(repo_root) if repo_root else REPO_ROOT
    now = time.time() if now is None else now
    claims = _session_claims(session_id)

    confirmed, ev1, ev2, info = _death_evidence(session_id, claims, root, now)
    res.evidence1, res.evidence2 = ev1, ev2
    if not confirmed:
        res.notes.append("双证不齐全，不回收（防误收活会话）")
        _salvage_audit({"ts": now, "action": "salvage-skip", **res.to_dict()})
        return res
    res.dead_confirmed = True

    # ① MERGE_HEAD abort（归属不明/abort 失败均如实记录，绝不误动）
    mh = _main_merge_head_path(root)
    if mh.is_file():
        try:
            res.merge_head_sha = mh.read_text(encoding="utf-8", errors="replace").strip()[:40]
        except OSError:
            pass
        attributed, why = _merge_head_attributed_to(root, session_id, info, claims, now)
        if not attributed:
            res.merge_abort = "not_attributed"
            res.notes.append(f"MERGE_HEAD 归属不明（{why}），保留待人工处置——禁误 abort 活会话 merge")
        elif dry_run:
            res.merge_abort = "dry-run"
        else:
            try:
                r = run_subprocess_hidden(["git", "merge", "--abort"], cwd=str(root), timeout=60)
                if r.returncode == 0 or not mh.is_file():
                    res.merge_abort = "aborted"
                else:
                    res.merge_abort = "failed"
                    res.notes.append(f"merge --abort rc={r.returncode}: {(r.stderr or '')[:200]}")
            except Exception as e:  # noqa: BLE001 — 回收动作异常不阻断 claim 释放
                res.merge_abort = "failed"
                res.notes.append(f"merge --abort 异常: {type(e).__name__}: {e}")

    # ② stash 归档（merge 存续且未 abort 时跳过——merge index 神圣，禁 stash 搅动）
    paths = sorted(claims)
    if paths and not _main_merge_head_path(root).is_file():
        if dry_run:
            res.stashed_paths = paths
        else:
            res.stash_ref, res.stashed_paths = _stash_claimed_paths(root, session_id, paths)
            if not res.stashed_paths:
                res.notes.append("claim 路径无 staged/WIP 改动，stash 幂等跳过")
    elif paths:
        res.notes.append("merge 存续未 abort——staged 归档跳过（merge index 神圣）")

    # ③ 释放 claim（双登记处；dry-run 不动）
    if not dry_run:
        res.released_locks = _force_release_locks(session_id, paths)
        res.released_session_files = _force_release_session_registry(root, session_id, info)

    _salvage_audit({"ts": now, "action": "salvage", "dry_run": dry_run, **res.to_dict()})
    return res


def cmd_salvage(session_id: str, *, dry_run: bool = False, repo_root: str | Path | None = None) -> int:
    """CLI：salvage <session_id> [--dry-run]——R-10 死会话遗物显式回收。"""
    _ensure_lock_root()
    res = salvage_dead_session(session_id, dry_run=dry_run, repo_root=repo_root)
    print(json.dumps(res.to_dict(), ensure_ascii=False, indent=2))
    if dry_run:
        return 0
    return 0 if res.dead_confirmed else 1


def shorten_claim_ttl(owner_id: str, file_paths: list[str], ttl_s: float) -> list[str]:
    """R-04 治本①配套（lane G1）：提交失败保留 claim 的 TTL 收窄兜底。

    claim 释放语义切换为「成功才释放、失败保留」后，原「失败释放防锁尸」动机由
    本函数接管：把该持有者对清单内文件的 claim 过期点收窄为 now+ttl_s（建议 300s，
    git_commit.py --failed-claim-ttl / ZEPHYR_FAILED_CLAIM_TTL_S 参数化）——
    会话死亡/放弃时过期即走既有 stale 回收通道（_is_stale + reclaim 审计），
    锁尸有兜底；存活会话重试通常在 TTL 内完成，互不影响。

    Returns:
        实际收窄的归一化路径列表（仅该持有者名下且锁存在的件；他人 claim 不动）。
    """
    now = time.time()
    rewritten: list[str] = []
    for fp in file_paths:
        lock_dir = _lock_dir(fp)
        owner = _read_owner(lock_dir)
        if owner is None or owner.get("owner_id") != owner_id:
            continue
        owner["expires_at"] = now + ttl_s
        owner["retention"] = "commit-failed-retained"  # 审计标记：区别于常规 acquire TTL
        try:
            _owner_file(lock_dir).write_text(json.dumps(owner, ensure_ascii=False, indent=2), encoding="utf-8")
            rewritten.append(_normalize_path(fp))
        except OSError:
            pass
    if rewritten:
        with _registry_mutex() as acquired:
            if acquired:
                registry = _load_registry()
                locks = registry.get("locks", {})
                for fp in rewritten:
                    if fp in locks:
                        locks[fp]["expires_at"] = now + ttl_s
                        locks[fp]["retention"] = "commit-failed-retained"
                _save_registry(registry)
    return rewritten


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
    print("  cleanup [--no-salvage]    清理所有死锁（TTL过期/PID已死）+ R-10 死会话遗物自动回收")
    print("  salvage <session_id> [--dry-run]  R-10 死会话遗物显式回收（双证判死→merge abort+stash归档+释放claim）")
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
        return cmd_cleanup(auto_salvage=("--no-salvage" not in args))

    if cmd == "salvage" and len(args) >= 2:
        return cmd_salvage(args[1], dry_run=("--dry-run" in args))

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
