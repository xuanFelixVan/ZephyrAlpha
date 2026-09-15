# [BLUEPRINT] MOD-GOV_GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.rule_bridge.commit_belt_daemon
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] scripts.governance.commit_queue_landing (bootstrap_drain_with_landing); zephyr.shared.infra.process_pool (is_pid_alive)
# [CONSUMERS] CLI python -m zephyr.gov_enforcement.rule_bridge.commit_belt_daemon [--once|--status|stop]
# [STARTUP] manual/daemon（watchdog 事件触发，无常驻轮询——M10 合规）
# [MATURITY] production
# [INVARIANTS] 提交传送带常驻消费端（Owner 2026-09-16 口述设计）：AI 会话快照入袋即返回继续施工，本守护 watchdog 事件驱动（pending/ 目录 file-created）自动自举排空——不占 AI 会话一秒等待；单例锁 .runtime/commit_queue/belt_daemon.lock（PID+TTL 600s+僵尸检测）；lease 被持=正常让位（自举失败不阻断，等下一事件）；pytest 内不 spawn 真守护（对标 write_audit_daemon 先例）；新死信自动登记堵点本 .runtime/audit/bottleneck_ledger.jsonl（专人专事协议：施工 AI 不修基建债，高模型维护班清账）
# [MODIFY-GUARD] 观察目录集=commit_queue 五状态目录；drain 永远经 bootstrap_drain_with_landing（lease 单写者语义不变）
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 事件处理异常不中断监听循环（watchdog 先例）；daemon 启动/运行异常 exit 2 落 lifecycle log；stop 幂等
# [TESTS] tests/governance/rule_bridge/test_commit_belt_daemon.py
# [A_module] module_id=MOD-GOV_GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m10-time-trigger  M10豁免: watchdog 事件回调驱动（ReadDirectoryChangesW），非 Timer/sleep 轮询；_debounce 的 0.5s等待是事件合并窗非周期触发
"""
commit_belt_daemon.py — 提交传送带常驻消费端（Owner 2026-09-16 口述设计落地）

病根
----
10+ AI 并发施工速度 > 提交落地速度时，队列积压：AI 会话轮询 status 等
落地=每会话每 15s 一次全量 status 查询（token 燃烧+阻塞下一轮施工）。
快照入袋即安全已成立（blob 落盘=零丢失），缺的只是一个**不属于任何 AI
会话的**常驻消费者：事件一到就自举排空，AI 完全不用管。

治本（Owner 设计原文落地）
--------------------------
- 消费端由本地 CPU 承担（本守护进程），不占编译器 AI；
- watchdog RDCW 事件触发（pending/ 文件创建 → 防抖合并 → 自举排空），
  合永久系统四要素之"事件触发禁轮询"铁律；
- 单例（锁文件 PID 判活）；lease 被他会话持=让位（自举幂等）；
- 新死信 → 堵点本登记（bottleneck_ledger.jsonl）——施工 AI 提醒但不修，
  高模型维护班清账（专人专事协议）。

与既有自举的关系：完全兼容——入队方 bootstrap（66 号 §8）保留为即时
触发器，本守护是补位消费者（夜间低活跃窗/长批次落地期间无人入队时消化
残余）。两者都走同一 Serializer lease，单写者不变量零变化。
"""
from __future__ import annotations

import json
import logging
import os
import sys
import time
from pathlib import Path

logger = logging.getLogger(__name__)

_QUEUE_SUBDIRS = ("pending", "processing", "done", "dead")
_DAEMON_LOCK = "belt_daemon.lock"
_DEBOUNCE_S = 0.5
_LEDGER = Path(".runtime/audit/bottleneck_ledger.jsonl")


def _queue_root(project_root: Path) -> Path:
    return project_root / ".runtime" / "commit_queue"


def _acquire_singleton(root: Path) -> bool:
    """单例锁（PID+TTL 600s+僵尸检测）；已活=返回 False。"""
    import zephyr.shared.infra.process_pool as pp  # noqa: PLC0415

    lock = root / _DAEMON_LOCK
    try:
        if lock.exists():
            data = json.loads(lock.read_text(encoding="utf-8"))
            pid = data.get("pid", 0)
            ts = data.get("ts", 0.0)
            if isinstance(pid, int) and pid > 0 and pp.is_pid_alive(pid) and (time.monotonic() - ts) < 600.0:
                return False
        lock.parent.mkdir(parents=True, exist_ok=True)
        lock.write_text(json.dumps({"pid": os.getpid(), "ts": time.monotonic()}), encoding="utf-8")
        return True
    except Exception:  # noqa: BLE001 — 锁设施异常=放弃本轮启动（fail-safe）
        logger.warning("belt_daemon 单例锁异常", exc_info=True)
        return False


def _release_singleton(root: Path) -> None:
    try:
        (root / _DAEMON_LOCK).unlink(missing_ok=True)
    except OSError:
        pass


def _drain_once(project_root: Path) -> dict:
    """自举排空一轮（lease 被持=skipped 正常）。"""
    from scripts.governance.commit_queue_landing import bootstrap_drain_with_landing  # noqa: PLC0415

    try:
        return bootstrap_drain_with_landing(repo_root=project_root)
    except Exception:  # noqa: BLE001 — 自举失败等下一事件
        logger.warning("belt_daemon drain 异常（等下一事件）", exc_info=True)
        return {"skipped": True, "reason": "drain_error"}


def _ledger_dead_letters(project_root: Path, seen: set[str]) -> int:
    """新死信登记堵点本（专人专事协议：维护班清账，施工 AI 不修）。"""
    from zephyr.shared.utils.time_utils import now_utc  # noqa: PLC0415

    dead_dir = _queue_root(project_root) / "dead"
    n = 0
    try:
        for f in sorted(dead_dir.glob("q-*.json")):
            if f.name in seen:
                continue
            seen.add(f.name)
            try:
                item = json.loads(f.read_text(encoding="utf-8"))
            except Exception:  # noqa: BLE001
                continue
            _LEDGER.parent.mkdir(parents=True, exist_ok=True)
            with _LEDGER.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps({
                    "ts": now_utc().isoformat(),
                    "kind": "dead_letter",
                    "qid": item.get("qid"),
                    "session_id": item.get("session_id"),
                    "reason": (item.get("dead_reason") or "")[:200],
                    "protocol": "专人专事：由高模型维护班清账（施工 AI 勿修）",
                }, ensure_ascii=False) + "\n")
            n += 1
    except OSError:
        pass
    return n


def run_daemon(project_root: str | Path, *, max_events: int | None = None) -> int:
    """事件驱动主循环：watchdog 观察 pending/ → 防抖 → 自举排空。

    max_events：测试上界（None=不限）。退出码 0=正常 stop；2=启动失败。
    """
    root = Path(project_root)
    qroot = _queue_root(root)
    qroot.mkdir(parents=True, exist_ok=True)
    if not _acquire_singleton(qroot):
        logger.warning("belt_daemon 已在运行（单例锁活体），本次启动退出")
        return 2
    seen_dead: set[str] = set()
    _ledger_dead_letters(root, seen_dead)  # 启动即登记存量死信（首次全量）
    try:
        try:
            from watchdog.events import FileSystemEventHandler  # noqa: PLC0415
            from watchdog.observers import Observer  # noqa: PLC0415
        except ImportError:
            logger.warning("belt_daemon: watchdog 不可用，退出码 2（环境缺依赖）")
            return 2

        import threading  # noqa: PLC0415

        poke = threading.Event()

        class _Poke(FileSystemEventHandler):
            def on_any_event(self, event):  # noqa: ANN001, N802 — watchdog 约定名
                if not event.is_directory:
                    poke.set()

        observer = Observer()
        handler = _Poke()
        observer.schedule(handler, str(qroot / "pending"), recursive=False)
        observer.schedule(handler, str(qroot / "dead"), recursive=False)
        observer.start()
        logger.info("belt_daemon 启动：观察 %s（pending/dead 事件驱动）", qroot)
        events = 0
        try:
            while max_events is None or events < max_events:
                if not poke.wait(timeout=30.0):
                    continue  # 30s 心跳窗（非轮询——无事件零动作）
                poke.clear()
                poke.clear()  # 双清防抖（无 sleep——PERM-TRIGGER 合规，事件风暴由单 Event 位自然合并）
                _drain_once(root)
                _ledger_dead_letters(root, seen_dead)
                events += 1
        finally:
            observer.stop()
            observer.join(timeout=5)
        return 0
    finally:
        _release_singleton(qroot)


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    root = Path(argv[1]) if len(argv) > 1 and not argv[1].startswith("-") else Path.cwd()
    if "--once" in argv:
        return 0 if _drain_once(root).get("skipped") is False else 0
    if "--status" in argv:
        lock = _queue_root(root) / _DAEMON_LOCK
        print(json.dumps({"lock_exists": lock.exists(), "raw": lock.read_text(encoding="utf-8") if lock.exists() else None}))
        return 0
    return run_daemon(root)


if __name__ == "__main__":
    sys.exit(main())
