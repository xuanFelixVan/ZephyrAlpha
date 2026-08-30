# [BLUEPRINT] MOD-GOV_DRIFT_WATCHDOG | docs/_working/reports/2026-08-27-authz-writeaudit-adjudication.md | §裁定B
# [MODULE] zephyr.gov_enforcement.rule_bridge.write_audit_daemon
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] zephyr.shared.infra.process_pool (spawn_python_hidden/is_pid_alive); zephyr.shared.io.paths (anchor_main_root); zephyr.shared.io.audit_jsonl_writer (append_audit_jsonl); watchdog.observers (RDCW); psutil
# [CONSUMERS] worktree_drift_watchdog (recent_events_for 告警联动); CLI python -m ... [--daemon|--once-scan|--status]
# [STARTUP] manual / ensure_daemon
# [MATURITY] production
# [INVARIANTS] 锚主仓工作区（anchor_main_root）；只观测不拦截（fail-open 不干扰主流程）；审计写 .runtime/（永不回 tracked 区）；只监视热目录集（不做全盘监控）；事件五要素落盘=ts/path/op/前后hash/归因；归因分层=session_registry(PID→session_id)+进程快照；单实例锁防堆积
# [MODIFY-GUARD] 热目录集 _WATCH_SPECS；write_audit.jsonl 记录格式；归因快照过滤 _INTERESTING_PROCS
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] watchdog/psutil 不可用→降级退出码 2 并落 lifecycle log；单事件处理异常不中断监听循环
# [TESTS] tests/governance/rule_bridge/test_write_audit_daemon.py
# [A_module] module_id=MOD-GOV_DRIFT_WATCHDOG | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
write_audit_daemon.py — WriteAudit PID 级写删审计守护（#ARCH-279 裁定B，#ARCH-264 O3-P1 施工化）

第一性原理
----------
护栏是"路由内仪表化"——走 guard_* 通道的删除全留痕；但带外通道（终端直删、
IDE 直写）天然绕开一切路由内机制（#ARCH-264 O4 quarantine 带外裸删实证：
ops_guard 全审计窗口零命中）。对带外通道，Windows 无内核驱动不可拦截，
**唯一防御是观测+归因**：

  1. 事件层：ReadDirectoryChangesW（watchdog 包）监视热目录集——文件变了
     （create/write/delete/rename）亚秒级可见；
  2. 进程层：事件时刻进程快照（psutil，同用户零权限）——谁在场；
  3. 会话层：PID → .runtime/session_registry.json → session_id——**仓内独有**，
     直接回答"哪个 AI 会话"，比通用进程级归因高一级（#ARCH-264 三要素之可归因）。

边界（防洪峰纪律）：只监视热目录集（_registry/catalogs/、design_memos/、
仓根平铺、.runtime/quarantine）——全部历史事故面；不做全盘监控。
Restart Manager 句柄级归因留作后续增强（MVP 以快照+会话映射为主，
热目录候选写者任一时刻个位数进程，近似归因工程上已够定凶）。

Usage::

    python -m zephyr.gov_enforcement.rule_bridge.write_audit_daemon <root> --daemon
    python -m zephyr.gov_enforcement.rule_bridge.write_audit_daemon <root> --once-scan
    python -m zephyr.gov_enforcement.rule_bridge.write_audit_daemon <root> --status

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: handler 参数
#   fields: 参数 handler，类型注解 WriteAuditHandler
#   code: write_audit_daemon.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: path 参数
#   fields: 参数 path，类型注解 str
#   code: write_audit_daemon.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: seconds 参数
#   fields: 参数 seconds，类型注解 float
#   code: write_audit_daemon.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: root 参数
#   fields: 参数 root，类型注解 str | Path
#   code: write_audit_daemon.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① WriteAuditHandler
#   name_en: WriteAuditHandler
#   intro: 热目录文件系统事件 → write_audit.jsonl（五要素+三层归因）。
#   desc: 热目录文件系统事件 → write_audit.jsonl（五要素+三层归因）。 不依赖 watchdog 包事件对象也可直接调用 record()（单测友好）； 经 make_…；公共方法（定义序）: record；…
#   inputs: root
#   outputs: 返回值
# - id: A2
#   name_zh: ② make_watchdog_handler
#   name_en: make_watchdog_handler
#   intro: 把 WriteAuditHandler 包装成 watchdog.events.FileSystemEventHand…
#   desc: 把 WriteAuditHandler 包装成 watchdog.events.FileSystemEventHandler。；源码 L374-L397
#   inputs: handler
#   outputs: 返回值
# - id: A3
#   name_zh: ③ recent_events_for
#   name_en: recent_events_for
#   intro: 读 write_audit.jsonl 尾部，返回指定路径近 seconds 秒的事件（新→旧）。
#   desc: 读 write_audit.jsonl 尾部，返回指定路径近 seconds 秒的事件（新→旧）。 drift 告警联动（ 裁定B2）：告警从"有人动了"升级为"谁动的"—— 调…；源码 L405-L439
#   inputs: path seconds root limit
#   outputs: list[dict[str, Any]]
# - id: A4
#   name_zh: ④ suspect_summary
#   name_en: suspect_summary
#   intro: 裁定B2 告警联动：指定路径近 seconds 秒的 WriteAudit 嫌疑摘要。
#   desc: 裁定B2 告警联动：指定路径近 seconds 秒的 WriteAudit 嫌疑摘要。 返回紧凑单行（drift 告警 detail 直接拼接）： - 有会话命中：`sess-x…；源码 L442-L467
#   inputs: path root seconds limit
#   outputs: str
# - id: A5
#   name_zh: ⑤ ensure_daemon
#   name_en: ensure_daemon
#   intro: 确保 WriteAudit daemon 在跑（幂等；pytest 内不 spawn 真守护——对标 drift wa…
#   desc: 确保 WriteAudit daemon 在跑（幂等；pytest 内不 spawn 真守护——对标 drift watchdog）。；源码 L510-L549
#   inputs: project_root
#   outputs: bool
# - id: A6
#   name_zh: ⑥ run_daemon
#   name_en: run_daemon
#   intro: 守护主循环：RDCW 监听热目录集，事件落 write_audit.jsonl。
#   desc: 守护主循环：RDCW 监听热目录集，事件落 write_audit.jsonl。；源码 L552-L598
#   inputs: project_root
#   outputs: int
# - id: A7
#   name_zh: ⑦ main
#   name_en: main
#   intro: main(argv) 源码 L623-L642
#   desc: 源码 L623-L642
#   inputs: argv
#   outputs: int
# 层: 输出
# - id: O1
#   name_zh: list[dict[str, Any]]
#   name_en: list[dict[str, Any]]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: worktree_drift_watchdog (recent_events_for 告警联动); CLI python -m ... [--daemon|-…
# - id: O2
#   name_zh: str
#   name_en: str
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: worktree_drift_watchdog (recent_events_for 告警联动); CLI python -m ... [--daemon|-…
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
# A7 --> O1
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import signal
import sys
import time
from pathlib import Path
from typing import Any, Final

logger = logging.getLogger(__name__)

__all__: Final = [
    "WriteAuditHandler",
    "ensure_daemon",
    "recent_events_for",
    "run_daemon",
    "suspect_summary",
]

_AUDIT_DIR: Final = ".runtime/audit"
_AUDIT_FILE: Final = "write_audit.jsonl"
_STATE_DIR: Final = ".runtime/write_audit"
_SESSION_REGISTRY: Final = ".runtime/session_registry.json"

# 热目录集（#ARCH-279 裁定B1：全部历史事故面；相对仓根，recursive 标记）
_WATCH_SPECS: Final = (
    ("docs/01_policies_and_standards/_registry/catalogs", True),
    ("docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos", True),
    (".runtime/quarantine", True),
    ("", False),  # 仓根平铺（AGENTS.md 等热文件，非递归）
)

# 归因快照关注的进程名（同用户零权限可见；AI 会话/终端/IDE 族）
_INTERESTING_PROCS: Final = frozenset(
    {
        "python.exe",
        "pythonw.exe",
        "cmd.exe",
        "powershell.exe",
        "pwsh.exe",
        "node.exe",
        "trae.exe",
        "trae-cn.exe",
    }
)

_HEARTBEAT_STALE_SECONDS: Final = 300  # session_registry 心跳超此值视为不活跃（仅标注不剔除）


# ---------------------------------------------------------------------------
# 基础助手
# ---------------------------------------------------------------------------


def _sha256_file(path: Path) -> str | None:
    """文件内容 sha256（前 16  hex）；不存在/不可读返回 None。"""
    try:
        h = hashlib.sha256()
        with open(path, "rb") as fh:
            for chunk in iter(lambda: fh.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()[:16]
    except OSError:
        return None


def _rel(path: str | Path, root: Path) -> str:
    """绝对路径 → 仓根相对（正斜杠）；仓外原样返回。"""
    try:
        return Path(path).resolve().relative_to(root).as_posix()
    except (ValueError, OSError):
        return str(path)


def _load_session_map(root: Path) -> dict[int, dict[str, Any]]:
    """读 session_registry.json → {pid: {session_id, last_heartbeat, stale}}。

    仓内独有归因资产（#ARCH-279 裁定B1 会话层）：全 AI 会话心跳注册表，
    PID 命中即回答"哪个 AI 会话"。注册表缺失/损坏降级空映射（不阻断事件落盘）。
    """
    reg_path = root / _SESSION_REGISTRY
    try:
        data = json.loads(reg_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    now = time.time()
    out: dict[int, dict[str, Any]] = {}
    if not isinstance(data, dict):
        return out
    for session_id, info in data.items():
        if not isinstance(info, dict):
            continue
        pid = info.get("pid")
        if not isinstance(pid, int):
            continue
        hb = info.get("last_heartbeat") or info.get("last_activity") or 0
        out[pid] = {
            "session_id": session_id,
            "heartbeat_age_s": round(now - float(hb), 1) if hb else None,
            "stale": bool(hb and now - float(hb) > _HEARTBEAT_STALE_SECONDS),
        }
    return out


def _snapshot_processes() -> list[dict[str, Any]]:
    """事件时刻在场进程快照（psutil，过滤 AI 会话/终端/IDE 族）。

    Returns:
        [{pid, name, cmdline}]——cmdline 截断 200 字符（取证定位够用，防超长行）。
        psutil 不可用/枚举失败降级空清单（事件其余字段照落）。
    """
    try:
        import psutil  # noqa: PLC0415 — 延迟 import：模块导入期不硬依赖
    except ImportError:
        return []
    snapshot: list[dict[str, Any]] = []
    try:
        for proc in psutil.process_iter(["pid", "name", "cmdline"]):
            try:
                name = (proc.info.get("name") or "").lower()
                if name not in _INTERESTING_PROCS:
                    continue
                cmdline = " ".join(proc.info.get("cmdline") or [])[:200]
                snapshot.append({"pid": proc.info["pid"], "name": name, "cmdline": cmdline})
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    except Exception:  # noqa: BLE001 — 快照失败不阻断事件落盘
        return []
    return snapshot


def _attribute_sessions(snapshot: list[dict[str, Any]], session_map: dict[int, dict[str, Any]]) -> list[dict[str, Any]]:
    """进程快照 × session_registry → 命中会话清单（归因核心产出）。"""
    hits: list[dict[str, Any]] = []
    for proc in snapshot:
        match = session_map.get(proc["pid"])
        if match:
            hits.append(
                {
                    "pid": proc["pid"],
                    "session_id": match["session_id"],
                    "stale": match["stale"],
                    "heartbeat_age_s": match["heartbeat_age_s"],
                    "cmdline": proc["cmdline"],
                }
            )
    return hits


# ---------------------------------------------------------------------------
# 事件处理器
# ---------------------------------------------------------------------------


class WriteAuditHandler:
    """热目录文件系统事件 → write_audit.jsonl（五要素+三层归因）。

    不依赖 watchdog 包事件对象也可直接调用 record()（单测友好）；
    经 make_watchdog_handler() 包装后接入 watchdog.observers.Observer。
    """

    def __init__(self, root: Path) -> None:
        self.root = root
        self._hash_cache: dict[str, str | None] = {}
        self._audit_dir = root / _AUDIT_DIR
        self._prime_cache()

    def _prime_cache(self) -> None:
        """启动基准扫描：热目录集全量 hash 入缓存（before-hash 真源）。"""
        for spec, recursive in _WATCH_SPECS:
            base = self.root / spec if spec else self.root
            if not base.is_dir():
                continue
            if recursive:
                for dirpath, _dirnames, filenames in os.walk(base):
                    for name in filenames:
                        p = Path(dirpath) / name
                        self._hash_cache[_rel(p, self.root)] = _sha256_file(p)
            else:
                for child in base.iterdir():
                    if child.is_file():
                        self._hash_cache[_rel(child, self.root)] = _sha256_file(child)

    def record(self, op: str, path: str | Path, *, dest_path: str | Path | None = None) -> dict[str, Any]:
        """记录一个写删事件（op=create|write|delete|rename）。

        落盘字段：ts/path/op/hash_before/hash_after/processes(在场快照)/
        sessions(PID→session_id 命中)/exact_attribution=False（SACL 精确层
        开启后由采集器补 True 记录）。
        """
        rel = _rel(path, self.root)
        p = self.root / rel
        hash_before = self._hash_cache.get(rel)
        hash_after = _sha256_file(p) if op != "delete" else None
        if op == "delete":
            self._hash_cache.pop(rel, None)
        else:
            self._hash_cache[rel] = hash_after

        snapshot = _snapshot_processes()
        session_map = _load_session_map(self.root)
        record: dict[str, Any] = {
            "ts": round(time.time(), 3),
            "path": rel,
            "op": op,
            "hash_before": hash_before,
            "hash_after": hash_after,
            "processes": snapshot,
            "sessions": _attribute_sessions(snapshot, session_map),
            "exact_attribution": False,
            "pid": os.getpid(),
        }
        if dest_path is not None:
            record["dest_path"] = _rel(dest_path, self.root)
            self._hash_cache[record["dest_path"]] = _sha256_file(self.root / record["dest_path"])
        self._append(record)
        return record

    def _append(self, record: dict[str, Any]) -> None:
        """落盘（50MB 轮转复用 audit_jsonl_writer；失败仅计数不阻断监听）。"""
        try:
            from zephyr.shared.io.audit_jsonl_writer import (  # noqa: PLC0415
                append_audit_jsonl,
            )

            self._audit_dir.mkdir(parents=True, exist_ok=True)
            append_audit_jsonl(self._audit_dir, _AUDIT_FILE, record)
        except Exception:  # noqa: BLE001 — 审计落盘失败不中断监听（fail-open 纪律）
            logger.warning("write_audit append failed", exc_info=True)


def make_watchdog_handler(handler: WriteAuditHandler):
    """把 WriteAuditHandler 包装成 watchdog.events.FileSystemEventHandler。"""
    from watchdog.events import (  # noqa: PLC0415 — 仅 daemon 路径需要
        FileSystemEventHandler,
    )

    class _Handler(FileSystemEventHandler):
        def on_created(self, event):  # noqa: ANN001, ANN202
            if not event.is_directory:
                handler.record("create", event.src_path)

        def on_modified(self, event):  # noqa: ANN001, ANN202
            if not event.is_directory:
                handler.record("write", event.src_path)

        def on_deleted(self, event):  # noqa: ANN001, ANN202
            if not event.is_directory:
                handler.record("delete", event.src_path)

        def on_moved(self, event):  # noqa: ANN001, ANN202
            if not event.is_directory:
                handler.record("rename", event.src_path, dest_path=event.dest_path)

    return _Handler()


# ---------------------------------------------------------------------------
# B2 告警联动（worktree_drift_watchdog 调用点）
# ---------------------------------------------------------------------------


def recent_events_for(
    path: str,
    seconds: float,
    root: str | Path,
    *,
    limit: int = 5,
) -> list[dict[str, Any]]:
    """读 write_audit.jsonl 尾部，返回指定路径近 seconds 秒的事件（新→旧）。

    drift 告警联动（#ARCH-279 裁定B2）：告警从"有人动了"升级为"谁动的"——
    调用方把返回事件的 sessions 字段附进告警即完成嫌疑清单归因。
    jsonl 缺失/损坏降级空清单（不阻断告警主流程）。
    """
    audit_file = Path(root) / _AUDIT_DIR / _AUDIT_FILE
    try:
        lines = audit_file.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return []
    cutoff = time.time() - seconds
    hits: list[dict[str, Any]] = []
    for line in reversed(lines[-2000:]):  # 尾部窗口足够覆盖热文件近事件
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(rec, dict):
            continue
        if rec.get("path") != path and rec.get("dest_path") != path:
            continue
        if float(rec.get("ts", 0)) < cutoff:
            break  # 时间倒序，越界即停
        hits.append(rec)
        if len(hits) >= limit:
            break
    return hits


def suspect_summary(path: str, root: str | Path, *, seconds: float = 120.0, limit: int = 3) -> str:
    """#ARCH-279 裁定B2 告警联动：指定路径近 seconds 秒的 WriteAudit 嫌疑摘要。

    返回紧凑单行（drift 告警 detail 直接拼接）：
    - 有会话命中：`sess-x(pid=100,write); sess-y(pid=200,delete)`
    - 无会话命中但有进程快照：`无会话命中[write/在场:python.exe,cmd.exe]`
    - 无事件/守护未跑：空串（调用方不拼接，告警主流程零干扰）。
    """
    try:
        events = recent_events_for(path, seconds, root, limit=limit)
    except Exception:  # noqa: BLE001 — 联动失败不阻断告警主流程
        return ""
    suspects: list[str] = []
    for ev in events:
        op = ev.get("op", "?")
        sessions = ev.get("sessions") or []
        if sessions:
            for s in sessions[:2]:
                stale_mark = ",stale" if s.get("stale") else ""
                suspects.append(f"{s.get('session_id')}(pid={s.get('pid')},{op}{stale_mark})")
        else:
            procs = ev.get("processes") or []
            names = sorted({p.get("name") for p in procs[:6] if p.get("name")})
            if names:
                suspects.append(f"无会话命中[{op}/在场:{','.join(names)}]")
    return "; ".join(suspects[:4])


# ---------------------------------------------------------------------------
# daemon 生命周期
# ---------------------------------------------------------------------------


def _pid_path(root: Path) -> Path:
    return root / _STATE_DIR / "write_audit.pid"


def _lifecycle_log(root: Path, action: str, extra: dict[str, Any] | None = None) -> None:
    rec: dict[str, Any] = {"ts": time.time(), "action": action, "pid": os.getpid()}
    if extra:
        rec.update(extra)
    try:
        d = root / _STATE_DIR
        d.mkdir(parents=True, exist_ok=True)
        with open(d / "lifecycle.jsonl", "a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except OSError:
        pass


def _acquire_single_instance_lock(root: Path):
    """单实例互斥锁（对标 worktree_drift_watchdog #99 模式：防连环拉起堆积）。"""
    import msvcrt  # noqa: PLC0415 — Windows 专用字节锁（本项目运行环境=Windows）

    lock_path = root / _STATE_DIR / "write_audit.lock"
    try:
        (root / _STATE_DIR).mkdir(parents=True, exist_ok=True)
        fh = open(lock_path, "a+b")  # noqa: SIM115 — 句柄须随进程生命周期持有
        try:
            msvcrt.locking(fh.fileno(), msvcrt.LK_NBLCK, 1)
        except OSError:
            fh.close()
            return None
        return fh
    except OSError:
        return None


def ensure_daemon(project_root: str | Path) -> bool:
    """确保 WriteAudit daemon 在跑（幂等；pytest 内不 spawn 真守护——对标 drift watchdog）。"""
    if os.environ.get("PYTEST_CURRENT_TEST"):
        logger.debug("write_audit ensure_daemon: pytest env, skip real daemon spawn")
        return True
    from zephyr.shared.infra.process_pool import (  # noqa: PLC0415
        is_pid_alive,
        spawn_python_hidden,
    )
    from zephyr.shared.io.paths import anchor_main_root  # noqa: PLC0415

    root = anchor_main_root(Path(str(project_root)).resolve())
    pid_file = _pid_path(root)
    try:
        if pid_file.is_file():
            pid = int(pid_file.read_text(encoding="utf-8").strip())
            if is_pid_alive(pid):
                return True
    except (OSError, ValueError):
        pass
    log_path = str(root / _STATE_DIR / "write_audit_stdout.log")
    (root / _STATE_DIR).mkdir(parents=True, exist_ok=True)
    proc = spawn_python_hidden(
        [
            sys.executable,
            "-m",
            "zephyr.gov_enforcement.rule_bridge.write_audit_daemon",
            str(root),
            "--daemon",
        ],
        cwd=str(root),
        stdout_path=log_path,
        stderr_path=log_path,
    )
    try:
        pid_file.write_text(str(proc.pid), encoding="utf-8")
    except OSError:
        pass
    _lifecycle_log(root, "spawned", {"pid": proc.pid})
    return True


def run_daemon(project_root: str | Path) -> int:
    """守护主循环：RDCW 监听热目录集，事件落 write_audit.jsonl。"""
    from zephyr.shared.io.paths import anchor_main_root  # noqa: PLC0415

    root = anchor_main_root(Path(str(project_root)).resolve())

    try:
        from watchdog.observers import Observer  # noqa: PLC0415
    except ImportError:
        _lifecycle_log(root, "abort", {"reason": "watchdog package unavailable"})
        return 2

    _lock_fh = _acquire_single_instance_lock(root)
    if _lock_fh is None:
        _lifecycle_log(root, "skipped", {"reason": "another instance already running"})
        return 0
    globals()["_WA_LOCK_FH"] = _lock_fh  # 防 GC 释放锁

    def _on_signal(signum, frame):  # noqa: ANN001, ANN202
        _lifecycle_log(root, "interrupted", {"signal": signum})
        sys.exit(0)

    for sig in (signal.SIGTERM, signal.SIGINT):
        try:
            signal.signal(sig, _on_signal)
        except (ValueError, OSError):
            pass

    handler = WriteAuditHandler(root)
    observer = Observer()
    wd_handler = make_watchdog_handler(handler)
    watched: list[str] = []
    for spec, recursive in _WATCH_SPECS:
        base = root / spec if spec else root
        if not base.is_dir():
            continue
        observer.schedule(wd_handler, str(base), recursive=recursive)
        watched.append(spec or "<root-flat>")
    observer.start()
    _lifecycle_log(root, "started", {"watched": watched})
    try:
        while True:
            time.sleep(1)
    finally:
        observer.stop()
        observer.join(timeout=5)
        _lifecycle_log(root, "stopped", {})


def _status(root: Path) -> dict[str, Any]:
    """--status：守护存活状态+审计规模（IDE 健康面板/运维探测用）。"""
    from zephyr.shared.infra.process_pool import is_pid_alive  # noqa: PLC0415

    pid_file = _pid_path(root)
    alive = False
    pid: int | None = None
    try:
        if pid_file.is_file():
            pid = int(pid_file.read_text(encoding="utf-8").strip())
            alive = is_pid_alive(pid)
    except (OSError, ValueError):
        pass
    audit_file = root / _AUDIT_DIR / _AUDIT_FILE
    return {
        "alive": alive,
        "pid": pid,
        "audit_file": str(audit_file),
        "audit_bytes": audit_file.stat().st_size if audit_file.is_file() else 0,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="WriteAudit PID 级写删审计守护（#ARCH-279 裁定B）")
    parser.add_argument("root", help="仓库根路径")
    parser.add_argument("--daemon", action="store_true", help="守护模式（RDCW 常驻监听）")
    parser.add_argument("--once-scan", action="store_true", help="仅基准扫描建 hash 缓存后退出")
    parser.add_argument("--status", action="store_true", help="守护存活状态")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    if args.status:
        print(json.dumps(_status(root), ensure_ascii=False))
        return 0
    if args.once_scan:
        handler = WriteAuditHandler(root)
        _lifecycle_log(root, "once_scan", {"cached": len(handler._hash_cache)})
        return 0
    if args.daemon:
        return run_daemon(root)
    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
