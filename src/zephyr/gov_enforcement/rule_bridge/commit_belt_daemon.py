# [BLUEPRINT] MOD-GOV_GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.rule_bridge.commit_belt_daemon
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] scripts.governance.commit_queue_landing (bootstrap_drain_with_landing); zephyr.shared.infra.process_pool (is_pid_alive)
# [CONSUMERS] CLI python -m zephyr.gov_enforcement.rule_bridge.commit_belt_daemon [--once|--status|stop]
# [STARTUP] manual/daemon（watchdog 事件触发，无常驻轮询——M10 合规）
# [MATURITY] production
# [INVARIANTS] 提交传送带常驻消费端（Owner 2026-09-16 口述设计）：AI 会话快照入袋即返回继续施工，本守护 watchdog 事件驱动（pending/ 目录 file-created）自动自举排空——不占 AI 会话一秒等待；单例锁 .runtime/commit_queue/belt_daemon.lock（PID+TTL 600s+僵尸检测）；lease 被持=正常让位（自举失败不阻断，等下一事件）；pytest 内不 spawn 真守护（对标 write_audit_daemon 先例）；新死信自动登记堵点本 .runtime/audit/bottleneck_ledger.jsonl（专人专事协议：施工 AI 不修基建债，高模型维护班清账）
# [MODIFY-GUARD] 观察目录集=commit_queue 五状态目录 + 队列根（serializer.lease/belt_daemon.lock 事件，R4 租约释放唤醒 st-commitchain-20260922——etcd「过期删除=delete 事件」语义的单机等效实现）；drain 永远经 bootstrap_drain_with_landing（lease 单写者语义不变）
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

# [ALGO_FLOW] external: docs/03_modules/_domain_gov_enforcement/algo_flow/rule_bridge/commit_belt_daemon.yaml
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
# 堵点本阈值（Owner 2026-09-16 晚授权自裁：有用就做）：≥20 条未清账或最老条目
# >24h → 自动写告警行进堵点本+logger.error，供高模型维护班开班信号。
_LEDGER_ALERT_THRESHOLD = 20
_LEDGER_ALERT_AGE_S = 86400.0
# R-06（S18 kimi-audit G2）：堵点本告警冷却窗——同一积压档位在窗口内不重复落盘；
# 档位翻转（积压↑↓跨档）立即落盘。参数化选型=模块常量（与上方阈值常量同处，
# 沿用 Owner 自裁口径；冷却只控"什么时候落盘"，阈值判据与告警内容语义零变化）。
_LEDGER_ALERT_COOLDOWN_S = 1800.0
# 自举连续环境失败升级阈值（债1 serializer 自举循环的可见化）：连续 3 次
# drain 环境异常 → 堵点本 CRITICAL 行（不静默循环）。
_ENV_ABORT_ESCALATE = 3


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
        result = bootstrap_drain_with_landing(repo_root=project_root)
        if isinstance(result, dict) and result.get("skipped"):
            logger.info(
                "[drain_once] skipped: %s（lease 被持=正常让位，租约释放事件将再触发）", result.get("reason", "?")
            )
        return result
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
                fh.write(
                    json.dumps(
                        {
                            "ts": now_utc().isoformat(),
                            "kind": "dead_letter",
                            "qid": item.get("qid"),
                            "session_id": item.get("session_id"),
                            "reason": (item.get("dead_reason") or "")[:200],
                            "protocol": "专人专事：由高模型维护班清账（施工 AI 勿修）",
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )
            n += 1
    except OSError:
        pass
    return n


def _check_ledger_backlog() -> None:
    """堵点本积压自检（阈值告警）：≥_LEDGER_ALERT_THRESHOLD 条或最老 >24h → 告警行。"""
    from datetime import datetime

    if not _LEDGER.exists():
        return
    try:
        lines = _LEDGER.read_text(encoding="utf-8").splitlines()
        if not lines:
            return
        import json as _json

        oldest_ts = None
        n = 0
        for line in lines:
            try:
                rec = _json.loads(line)
            except Exception:  # noqa: BLE001
                continue
            if rec.get("kind") == "alert":
                continue  # 告警行不计积压
            n += 1
            ts = rec.get("ts")
            if ts:
                try:
                    dt = datetime.fromisoformat(ts)
                    oldest_ts = dt if oldest_ts is None or dt < oldest_ts else oldest_ts
                except (ValueError, TypeError):
                    pass
        age_s = (datetime.now().astimezone() - oldest_ts).total_seconds() if oldest_ts else 0.0
        # ── R-06 冷却状态机（S18 kimi-audit G2）────────────────────────────
        # 改前：无状态变化检测，越阈期间每 tick 重写同一事实（取证：1095 行同事实
        # 告警落盘间隔 P50 2.0s）。改后：档位翻转立即落盘；同档位冷却窗内不重复；
        # 冷却期后同档位重报一次并刷新窗口。阈值判据与告警内容语义零变化。
        level = _backlog_alert_level(n, age_s)
        prev_level, prev_ts = _load_backlog_alert_state()
        now = time.time()
        if not level:
            if prev_level:
                _save_backlog_alert_state("", prev_ts)  # 回落清零档位：下次越阈按翻转立即出声
            return
        if level == prev_level and (now - prev_ts) < _LEDGER_ALERT_COOLDOWN_S:
            return  # 同档位冷却窗内：不重复落盘
        from zephyr.shared.utils.time_utils import now_utc  # noqa: PLC0415

        with _LEDGER.open("a", encoding="utf-8") as fh:
            fh.write(
                _json.dumps(
                    {
                        "ts": now_utc().isoformat(),
                        "kind": "alert",
                        "alert": "bottleneck_backlog_threshold",
                        "pending_items": n,
                        "oldest_age_s": round(age_s),
                        "backlog_level": level,
                        "protocol": "维护班开班信号：积压超阈（≥20 条或最老>24h）——由高模型维护班清账",
                    },
                    ensure_ascii=False,
                )
                + chr(10)
            )
        logger.error(
            "belt_daemon: 堵点本积压超阈 items=%d oldest_age_h=%.1f——维护班开班信号已写入",
            n,
            age_s / 3600,
        )
        _save_backlog_alert_state(level, now)
    except OSError:
        pass


def _backlog_alert_level(n: int, age_s: float) -> str:
    """积压档位签名（R-06）：阈值判据不变，只把越阈组合归一为可比状态。

    ""=未越阈；"count"=条数越阈；"age"=账龄越阈；"count+age"=双越阈。
    档位翻转（含 ↑↓ 跨档）= 状态变化 → 立即落盘。
    """
    parts = []
    if n >= _LEDGER_ALERT_THRESHOLD:
        parts.append("count")
    if age_s > _LEDGER_ALERT_AGE_S:
        parts.append("age")
    return "+".join(parts)


def _backlog_alert_state_path() -> Path:
    """冷却状态文件与堵点本同目录（随 _LEDGER 重定位，测试隔离自洽）。"""
    return _LEDGER.with_name("bottleneck_backlog_alert_state.json")


def _load_backlog_alert_state() -> tuple[str, float]:
    """读冷却状态；缺失/损坏=按未知处理（宁可多报不漏报——红线=冷却期漏报翻转）。"""
    try:
        raw = json.loads(_backlog_alert_state_path().read_text(encoding="utf-8"))
        return str(raw.get("level", "")), float(raw.get("last_alert_ts", 0.0))
    except Exception:  # noqa: BLE001
        return "", 0.0


def _save_backlog_alert_state(level: str, last_alert_ts: float) -> None:
    """原子写冷却状态（tmp+os.replace，对齐 drift watchdog 落盘口径）。"""
    try:
        p = _backlog_alert_state_path()
        p.parent.mkdir(parents=True, exist_ok=True)
        tmp = p.with_name(f"{p.stem}.{os.getpid()}.tmp")
        tmp.write_text(
            json.dumps({"level": level, "last_alert_ts": last_alert_ts}, ensure_ascii=False), encoding="utf-8"
        )
        os.replace(tmp, p)
    except OSError:
        pass


def _escalate_env_aborts(counter: dict) -> None:
    """债1 自举循环升级：连续环境失败计数达阈 → 堵点本 CRITICAL 行（禁静默循环）。"""
    counter["env_aborts"] = counter.get("env_aborts", 0) + 1
    if counter["env_aborts"] < _ENV_ABORT_ESCALATE:
        return
    from zephyr.shared.utils.time_utils import now_utc  # noqa: PLC0415

    try:
        _LEDGER.parent.mkdir(parents=True, exist_ok=True)
        import json as _json

        with _LEDGER.open("a", encoding="utf-8") as fh:
            fh.write(
                _json.dumps(
                    {
                        "ts": now_utc().isoformat(),
                        "kind": "alert",
                        "alert": "serializer_env_abort_loop",
                        "consecutive": counter["env_aborts"],
                        "protocol": "债1：Serializer 落地环境连续异常（worktree 自举循环嫌疑）——维护班介入",
                    },
                    ensure_ascii=False,
                )
                + chr(10)
            )
        logger.error("belt_daemon: Serializer 连续环境失败 %d 次——堵点本 CRITICAL 已登记", counter["env_aborts"])
    except OSError:
        pass


# ── 裁定#281①：常驻进程代码纪元自检 + 安全点原地 re-exec（2026-09-17 施工）──
# 病根：本守护 import 门禁模块一次常驻内存，任何门禁治本的生效延迟上限=进程寿命
# （实证：PID 28648 自 07:17 常驻，21:39 落地的 R21 治本对它无效，22:06 仍按旧码
# 挡死 q-…-0017）。治本=每轮 drain 后自检子树纪元（HEAD tree sha），变更即在安全点
# （lease 已释放、两轮 drain 之间）os.execv 原地重启——禁自杀退出（本仓无计划任务
# 重拉本守护，退出即掐断全仓排队落地）。
# 自检范围经 #ARCH-323 扩为"门禁代码 + 判据真源"两子树：只测前者是半个盲区，
# 实证代价=死块判据 21:58 进 scripts/governance/_shared/extractor 而常驻守护按旧码
# 跑，三条图/几何判据静默失效，红蓝实弹两发变异真落地（e10ac5acc4/2924601305）。
_SERIALIZER_LEASE = "serializer.lease"
_REEXEC_ENV_FLAG = "ZEPHYR_BELT_DAEMON_NO_REEXEC"  # 运维逃生：置 1 禁自动 re-exec
_PRIMARY_SUBTREE = "src/zephyr/gov_enforcement"  # 门禁代码子树
_CRITERIA_SUBTREE = "scripts/governance"  # 门禁判据真源子树（extractor/校验器住这里）


def _subtree_epoch(project_root: Path, subtree: str) -> str | None:
    """HEAD 里某子树的 tree sha：对子树内任何文件任何变更敏感且零成本（单次 rev-parse）。

    git 不可达/子树不存在返回 None（该子树按"无证据"处理）；经 run_subprocess_hidden
    （process_pool 正门，禁裸 subprocess——对齐 worktree_drift_watchdog 口径）。
    """
    from zephyr.shared.infra.process_pool import run_subprocess_hidden  # noqa: PLC0415

    try:
        r = run_subprocess_hidden(
            ["git", "rev-parse", f"HEAD:{subtree}"],
            capture_output=True,
            text=True,
            cwd=str(project_root),
            timeout=10,
        )
        if r is not None and r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip()
    except Exception:  # noqa: BLE001 — 环境故障按"纪元未知"处理
        pass
    return None


def _gov_enforcement_epoch(project_root: Path) -> str | None:
    """门禁代码纪元：src/zephyr/gov_enforcement 的 HEAD tree sha。"""
    return _subtree_epoch(project_root, _PRIMARY_SUBTREE)


def _commit_queue_epoch(project_root: Path) -> str | None:
    """commit_queue 判据纪元（R4 配套，st-commitchain-20260922 环节3 E3）。

    scripts/commit_queue.py 是 SerializerLease/drain_queue/FIFO 判据真源，但两棵
    子树（gov_enforcement/scripts.governance）都不含 scripts/ 根——改它不触发换血，
    守护按旧判据常驻（与 #ARCH-323 实证同构的盲区）。单文件 blob sha 对任何变更敏感。
    """
    from zephyr.shared.infra.process_pool import run_subprocess_hidden  # noqa: PLC0415

    try:
        r = run_subprocess_hidden(
            ["git", "rev-parse", "HEAD:scripts/commit_queue.py"],
            capture_output=True,
            text=True,
            cwd=str(project_root),
            timeout=10,
        )
        if r is not None and r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip()
    except Exception:  # noqa: BLE001 — 环境故障按"纪元未知"处理
        pass
    return None


def _gate_code_epoch(project_root: Path) -> str | None:
    """门禁代码 + **判据真源**两个子树的合成纪元（2026-09-17 扩）。

    只测门禁子树是半个盲区：ALGO-FLOW-LINK 这类门的判据真源住在
    `scripts/governance/_shared/`（extractor 的几何/图规则），判据治本往往**只动
    scripts 侧**——旧口径下这类治本对常驻守护永不可见，实证代价=死块判据符号
    21:58 进 extractor 而 07:17 起常驻的守护按旧码跑，红蓝实弹 R1/R3 双双落地。
    单侧无证据不废另一侧（该子树不在 HEAD 里=无代码可陈旧），全无可证才返回 None。
    """
    parts = [
        e
        for e in (
            _gov_enforcement_epoch(project_root),
            _subtree_epoch(project_root, _CRITERIA_SUBTREE),
            _commit_queue_epoch(project_root),
        )
        if e
    ]
    return "|".join(parts) if parts else None


def _serializer_lease_held(qroot: Path) -> bool:
    """Serializer lease 活体判定（serializer.lease：PID 判活；判不了=按持有，保守不重启）。"""
    import zephyr.shared.infra.process_pool as pp  # noqa: PLC0415

    lease = qroot / _SERIALIZER_LEASE
    try:
        if not lease.exists():
            return False
        data = json.loads(lease.read_text(encoding="utf-8"))
        pid = data.get("pid", 0)
        return isinstance(pid, int) and pid > 0 and pp.is_pid_alive(pid)
    except Exception:  # noqa: BLE001 — 保守：lease 态未知=当持有，禁在未知态重启
        return True


def _reexec_self(project_root: Path) -> None:
    """原地 re-exec：先释放单例锁（execv 不跑 finally），再替换进程映像。

    execv=新 import、无孤儿、不依赖外部监管者拉起（裁定#281 原文语义）；
    watchdog 观察者线程随进程映像替换一并消亡，新进程自会重建。
    """
    _release_singleton(_queue_root(project_root))
    logger.warning("belt_daemon: 门禁代码/判据真源纪元变更，安全点原地 re-exec（裁定#281）")
    argv = [sys.executable, str(Path(__file__).resolve()), *sys.argv[1:]]
    os.execv(sys.executable, argv)


def _check_and_reexec(project_root: Path, qroot: Path, state: dict, *, enabled: bool = True) -> bool:
    """纪元自检 → 安全点原地 re-exec。返回 True=已触发 re-exec。

    安全点契约：只在 _drain_once 返回之后调用（lease 已由 bootstrap 释放、两轮
    drain 之间）；serializer lease 活体时不动作（等下一个安全点）；git 不可达
    不动作（无证据不重启）；enabled=False（pytest 上界模式/运维逃生旗）零动作。
    """
    if not enabled or os.environ.get(_REEXEC_ENV_FLAG):
        return False
    epoch = _gate_code_epoch(project_root)
    if epoch is None:
        return False
    prev = state.get("epoch")
    if prev is None:
        state["epoch"] = epoch  # 启动种子：只对运行期间发生的变更反应
        return False
    if epoch == prev:
        return False
    if _serializer_lease_held(qroot):
        logger.info("belt_daemon: 纪元已变更但 serializer lease 被持，等下一个安全点")
        return False
    _reexec_self(project_root)
    return True


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
    _loop_state: dict = {"env_aborts": 0, "epoch": None}
    _ledger_dead_letters(root, seen_dead)  # 启动即登记存量死信（首次全量）
    _check_ledger_backlog()  # 启动即自检积压
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
        # R4 租约释放唤醒（st-commitchain-20260922）：serializer.lease 在队列根，
        # 其 deleted 事件（正常释放/僵尸回收）即刻 poke——封堵「5s 放弃的自举后无
        # 新事件则停摆到下一次入队」的漏唤醒窄缝（etcd delete-event 语义单机等效）。
        observer.schedule(handler, str(qroot), recursive=False)
        observer.start()
        logger.info("belt_daemon 启动：观察 %s（pending/dead 事件驱动）", qroot)
        events = 0
        try:
            while max_events is None or events < max_events:
                if not poke.wait(timeout=30.0):
                    continue  # 30s 心跳窗（非轮询——无事件零动作）
                poke.clear()
                poke.clear()  # 双清防抖（无 sleep——PERM-TRIGGER 合规，事件风暴由单 Event 位自然合并）
                _st = _drain_once(root)
                if isinstance(_st, dict) and _st.get("skipped") and "bootstrap_error" in str(_st.get("reason", "")):
                    _escalate_env_aborts(_loop_state)
                else:
                    _loop_state["env_aborts"] = 0  # 成功即复位
                _ledger_dead_letters(root, seen_dead)
                _check_ledger_backlog()
                events += 1
                # 裁定#281①：drain 已返回=lease 已释放=安全点；纪元变更即原地 re-exec
                # （pytest 上界模式 max_events 非 None=enabled=False，测试零副作用）
                if _check_and_reexec(root, qroot, _loop_state, enabled=max_events is None):
                    return 0
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
        print(
            json.dumps(
                {"lock_exists": lock.exists(), "raw": lock.read_text(encoding="utf-8") if lock.exists() else None}
            )
        )
        return 0
    return run_daemon(root)


if __name__ == "__main__":
    sys.exit(main())
