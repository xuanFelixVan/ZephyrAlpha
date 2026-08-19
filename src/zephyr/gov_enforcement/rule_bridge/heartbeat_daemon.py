# [BLUEPRINT] MOD-GOV_HEARTBEAT_DAEMON | docs/_archive/ruling_session_worktree_heartbeat.md | §P1-1
# [MODULE] zephyr.gov_enforcement.rule_bridge.heartbeat_daemon
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] zephyr.security.access_control.session_concurrency (SessionRegistry); zephyr.shared.io.paths (REPO_ROOT)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.session_worktree (_spawn_heartbeat_daemon / _kill_heartbeat_daemon)
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] heartbeat 独立进程（DETACHED_PROCESS）——session_worktree 工作流跨多个 python -c 进程，线程无法跨进程存活，必须用 detached subprocess；heartbeat.jsonl 每 30s 追加一条 {ts,pid,status} 审计记录；session 不再在 registry 中时 daemon 退出（返回 0）；worktree 锚点丢失（spawn 传入的 worktree 目录消失=退役/删除）时 daemon 失锚自退（CAND-DAEMON-001 2026-08-17：根治孤儿 daemon 制造假活性，锚点未配置时跳过零行为变更）；idle 超 _MAX_IDLE_SECONDS（=session_concurrency._ACTIVITY_IDLE_TIMEOUT_SECONDS=1800s）时 daemon 退出（#ARCH-HEARTBEAT-002 活性反转治本 2026-07-23：last_activity 为独立活性锚点，heartbeat 不刷新，消除僵尸 daemon 永久保活死 session）；不抛异常（所有错误写 log 后 continue）
# [MODIFY-GUARD] heartbeat_file_path 路径格式；run_daemon 退出条件（registry 不含 sid / worktree 锚点丢失 / idle 超 _MAX_IDLE_SECONDS）；_append_heartbeat_log 字段集
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 文件 IO 失败→log warning 不退出；registry 查询失败→continue 下次循环；signal 中断→写 interrupted 记录后退出
# [TESTS] tests/governance/rule_bridge/test_heartbeat_daemon.py
# [A_module] module_id=MOD-GOV_HEARTBEAT_DAEMON | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] task_bound
# noqa: m10-time-trigger  M10豁免: daemon 循环是 heartbeat 生命周期，非周期触发
# noqa: m11-perm-manual-legitimate  M11豁免: session_worktree 子进程 spawn 的 detached daemon，非独立永久系统
"""

heartbeat_daemon.py — session heartbeat 独立进程（Ruling:100PCT-AI-GOVERNANCE P3-1，2026-07-20）

第一性原理
-----------
session_worktree 工作流跨多个 ``python -c`` 进程：
  - ``session_worktree_start`` 启动一次
  - ``session_worktree_commit`` 调用一次或多次
  - ``session_worktree_merge`` / ``abort`` 收尾

如果 heartbeat 用线程（threading.Thread），start 进程退出后线程死亡，
heartbeat 不再更新——后续 commit/merge 进程无法接续心跳。

治本方案：detached subprocess
-----------------------------
本模块封装 heartbeat daemon 为独立 OS 进程：

  1. ``session_worktree_start`` 调用 ``_spawn_heartbeat_daemon`` 启动 daemon
     （DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP，脱离父进程生命周期）
  2. daemon 每 30s 调用 ``registry.heartbeat(session_id)`` 刷新 registry 时间戳
  3. daemon 每 30s 追加一条 ``heartbeat.jsonl`` 审计记录（{ts, pid, status}）
  4. session 不再在 registry 中时 daemon 自动退出（返回 0）
  4a. worktree 锚点丢失（目录消失=退役/删除）时 daemon 失锚自退（CAND-DAEMON-001）
  5. ``session_worktree_merge`` / ``abort`` 调用 ``_kill_heartbeat_daemon`` 终止 daemon

文件路径
--------
- heartbeat 审计: ``.runtime/sessions/<sid>/heartbeat.jsonl``
- daemon PID: ``.runtime/sessions/<sid>/heartbeat.pid``
- emergency 计数: ``.runtime/sessions/<sid>/emergency_count.json``（由 emergency_commit.py 管理，本模块不读写）

判活逻辑（SessionRegistry._is_session_alive）
----------------------------------------------
- pid=0（逻辑 session）+ heartbeat 新鲜度 > 90s = stale → 返回 False
- pid>0 + PID 死亡 = stale → 返回 False
- 否则 = alive

阻塞窗口
--------
- 旧方案（仅 TTL=3600s）：AI 崩溃后 held_files 阻塞 1 小时
- 新方案（heartbeat 90s + TTL 3600s）：阻塞窗口缩短到 90s（3×30s，容忍 2 次漏跳）

绕过权衡（5.1 审查修复，2026-07-20）
--------------------------------------
``registry.heartbeat(session_id)`` 是公共 API，AI 理论上可直接调用绕过 daemon。
但这是合理设计权衡：
  - daemon 提供**持续**心跳（30s 循环），手动调用 ``registry.heartbeat()`` 只刷新一次
  - 手动刷新一次只能延长 90s 生存期，无法替代 daemon 的持续保活
  - daemon 的核心价值是"AI 崩溃后心跳停止→90s 自动释放"，手动调用无法实现这个崩溃检测语义
因此不限制 ``registry.heartbeat()`` 的访问——它是底层 API，daemon 是封装层。

Usage::

    from zephyr.gov_enforcement.rule_bridge.heartbeat_daemon import (
        heartbeat_file_path, cleanup_heartbeat_file, run_daemon,
    )

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: daemon 启动入参
#   fields: session_id + project_root + interval（默认 30s）+ worktree_path（可选失锚锚点，CAND-DAEMON-001）
#   code: run_daemon(session_id, project_root, interval, worktree_path) L331
# - id: I2
#   name: SessionRegistry session 条目
#   fields: last_activity / start_time 活性锚点（heartbeat 不刷新 last_activity）
#   code: SessionRegistry(project_root).get_session(session_id) L258-280
# 层: 算法
# - id: A1
#   name_zh: ① 心跳主循环
#   name_en: run_daemon
#   intro: 独立进程里每 30 秒刷一次 registry 心跳并追加一条 alive 审计记录，让死 session 90 秒内被识破
#   desc: started 记录 → signal 注册 → 1s 初始延迟 → 循环：registry.heartbeat(sid) + alive 记录 + sleep(30) L281-331；registry 故障退避 5s，连续 >10 次写 fatal 返回 1 L317-327
#   inputs: I1 A2
#   outputs: registry 心跳刷新 + alive 记录
#   invariant: 所有异常写 log 后 continue，不崩溃
# - id: A2
#   name_zh: ② 活性判定与退出
#   name_en: _session_in_registry / _worktree_anchor_alive / _session_idle_seconds
#   intro: session 被注销、worktree 锚点丢失（退役/删除）或闲置超 1800 秒就退出，防僵尸 daemon 永久保活死 session 与孤儿 daemon 假活性
#   desc: session 不在 registry → 写 exited 返回 0；worktree_path 已配置且目录消失 → 写 exited(worktree anchor lost) 返回 0（CAND-DAEMON-001 2026-08-17）；idle=now-last_activity（缺失回退 start_time，绝不回退 last_heartbeat）> _MAX_IDLE_SECONDS(=1800) → 写 exited(idle timeout) 返回 0
#   inputs: I2
#   outputs: 继续心跳 / 退出
#   invariant: 查询失败保守视为存活，不误退出
# - id: A3
#   name_zh: ③ 心跳审计追加
#   name_en: _append_heartbeat_log
#   intro: 往 heartbeat.jsonl 追加一行 {ts, pid, status} 审计记录，IO 失败只告警
#   desc: record={ts: UTC ISO, pid, status[, extra]} → JSONL 追加 L123-143；状态标签 started/alive/exited/interrupted/fatal/error
#   inputs: A1 A4
#   outputs: JSONL 审计行
# - id: A4
#   name_zh: ④ 信号优雅退出
#   name_en: _handle_signal
#   intro: 被 kill 时先写一条 interrupted 审计记录再退出，不留无记录死亡
#   desc: SIGTERM/SIGINT → 从全局变量取 root/sid → 写 interrupted{signal} → sys.exit(0) L226-240；handler 内禁抛异常
#   inputs: I1
#   outputs: interrupted 记录 + 进程退出
# 层: 输出
# - id: O1
#   name_zh: heartbeat.jsonl 审计流
#   name_en: .runtime/sessions/<sid>/heartbeat.jsonl
#   intro: 每 30s 一行的 daemon 生命周期审计（started/alive/exited/interrupted/fatal/error）
#   downstream: session_worktree MOD-GOV_SESSION_WORKTREE（_spawn/_kill_heartbeat_daemon，# [CONSUMERS] 头）
# - id: O2
#   name_zh: registry 心跳时间戳
#   name_en: SessionRegistry.last_heartbeat
#   intro: 供 _is_session_alive 判活的新鲜度锚点——90s 不更新即 stale 释放 held_files
#   downstream: session_concurrency.SessionRegistry 判活逻辑（内部使用）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A2
# A2 --> A1
# A1 --> A3
# I1 --> A4
# A4 --> A3
# A3 --> O1
# A1 --> O2
"""

from __future__ import annotations

__all__ = [
    "heartbeat_file_path",
    "cleanup_heartbeat_file",
    "run_daemon",
]

import json
import logging
import signal
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

# heartbeat 追加间隔（秒）。30s 平衡 IO 开销与新鲜度。
_HEARTBEAT_INTERVAL = 30
# registry 查询失败重试间隔（秒），避免 DB 故障时 daemon busy-loop
_REGISTRY_ERROR_BACKOFF = 5
# daemon 启动后第一次 heartbeat 的延迟（秒），给 start 调用方时间完成 registry.register
_INITIAL_DELAY = 1

# daemon 的 idle 退出上限（#ARCH-HEARTBEAT-002 治本，2026-07-23）：
# daemon 自身是 last_heartbeat 唯一刷新源——若仅以"session 在 registry 中"判活，
# chat 异常关闭（未走 merge/abort）时 daemon 会永久保活死 session（活性反转，
# held_files 永久阻塞；实测 sess-39820/sess-53456 僵尸 daemon）。治本：以
# last_activity（真实治理操作时间戳，heartbeat 不刷新）为独立活性锚点，
# idle 超此上限自动退出 → 90s 后 registry 条目过期 → claim 自动释放。
# 值与 session_concurrency._ACTIVITY_IDLE_TIMEOUT_SECONDS 同源（top-level try-import）。
try:
    from zephyr.security.access_control.session_concurrency import (
        _ACTIVITY_IDLE_TIMEOUT_SECONDS as _MAX_IDLE_SECONDS,
    )
except Exception:  # noqa: BLE001 — 导入失败兜底（daemon 不得因导入失败崩溃）
    _MAX_IDLE_SECONDS = 1800


def heartbeat_file_path(project_root: str | Path, session_id: str) -> Path:
    """返回 heartbeat.jsonl 文件路径。

    路径格式: ``<project_root>/.runtime/sessions/<session_id>/heartbeat.jsonl``
    """
    return Path(project_root) / ".runtime" / "sessions" / session_id / "heartbeat.jsonl"


def _append_heartbeat_log(path: Path, status: str, extra: dict | None = None) -> None:
    """追加一条 heartbeat 审计记录到 JSONL 文件。

    Args:
        path: heartbeat.jsonl 文件路径。
        status: 状态标签（started/alive/exited/interrupted/fatal/error）。
        extra: 附加字段（如 exit_code / signal）。
    """
    record: dict = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "pid": _safe_getpid(),
        "status": status,
    }
    if extra:
        record.update(extra)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError as e:
        logger.warning("heartbeat log append failed: %s (path=%s)", e, path)


def _safe_getpid() -> int:
    """安全获取 PID（兼容极旧 Python 无 os.getpid 的边界场景）。"""
    try:
        import os
        return os.getpid()
    except Exception:  # noqa: BLE001 — 极端兜底，不应发生
        return 0


def cleanup_heartbeat_file(project_root: str | Path, session_id: str) -> bool:
    """清理 heartbeat.jsonl 审计文件（merge/abort 时调用）。

    注意：只删 ``heartbeat.jsonl``，不删 session 目录——
    ``emergency_count.json`` 也存放在该目录，由 emergency_commit.py 管理。

    Args:
        project_root: 项目根目录。
        session_id: session 标识。

    Returns:
        True=清理成功（或文件本就不存在），False=清理失败。
    """
    hb_file = heartbeat_file_path(project_root, session_id)
    if not hb_file.exists():
        return True
    try:
        hb_file.unlink()
        return True
    except Exception as e:  # noqa: BLE001 — best-effort 清理
        logger.warning("heartbeat cleanup failed: %s session=%s", e, session_id)
        return False


def _session_in_registry(session_id: str, project_root: str | Path) -> bool:
    """检查 session 是否仍在 registry 中（用于 daemon 退出判定）。

    daemon 启动后由 _spawn_heartbeat_daemon 持有 session_id + project_root，
    通过查询 registry 决定是否继续心跳。
    """
    try:
        from zephyr.security.access_control.session_concurrency import SessionRegistry
        registry = SessionRegistry(project_root)
        # 2026-08-19 治本：SessionRegistry 只有 get_session（无 .get）——原 .get()
        # 每轮 AttributeError 被 except 吞掉保守返 True，daemon 存在性自退静默失效
        # （12 僵尸 daemon 实证；forged_gw_marker_gate L112 同族先例）
        info = registry.get_session(session_id)
        return info is not None
    except Exception as e:  # noqa: BLE001 — DB 故障时保守返回 True（避免误退出）
        logger.debug("registry query failed (assume alive): %s", e)
        return True


def _session_idle_seconds(session_id: str, project_root: str | Path) -> float | None:
    """返回 session 的 idle 秒数（now - last_activity），用于活性反转治本退出判定。

    last_activity 只由真实治理操作刷新（register/claim_file/register_dependency；
    heartbeat 不刷新），是独立于 daemon 的活性锚点。缺失时（修复前旧条目）回退
    start_time——绝不回退 last_heartbeat（那是 daemon 自己的输出，回退它等于
    重新引入活性反转）。

    Returns: idle 秒数；session 不在 registry / 无锚点 / 查询失败返回 None
        （调用方按现有流程继续，不误退出）。
    """
    try:
        from zephyr.security.access_control.session_concurrency import SessionRegistry
        registry = SessionRegistry(project_root)
        # 同族修复（2026-08-19）：get → get_session，与 _session_in_registry 一致
        info = registry.get_session(session_id)
        if info is None:
            return None
        if isinstance(info, dict):  # 兼容 mock/旧式 dict 返回
            anchor = info.get("last_activity") or info.get("start_time") or 0.0
        else:
            anchor = (getattr(info, "last_activity", 0.0) or 0.0) or (
                getattr(info, "start_time", 0.0) or 0.0
            )
        if not anchor:
            return None
        return time.time() - float(anchor)
    except Exception as e:  # noqa: BLE001 — 查询失败保守返回 None（不退出，对标 _session_in_registry）
        logger.debug("session idle query failed (assume active): %s", e)
        return None


def _worktree_anchor_alive(worktree_path: str | Path | None) -> bool:
    """检查 worktree 锚点是否存活（CAND-DAEMON-001 失锚自退，2026-08-17）。

    daemon 启动时由 _spawn_heartbeat_daemon 传入所属 worktree 路径；
    周期核对路径存活——worktree 目录消失（退役/删除/物理清理）即失锚。

    Args:
        worktree_path: 锚定 worktree 路径；None/空串=未配置锚（旧 spawn 兼容），
            保守视为存活（不引入误退出）。

    Returns:
        True=锚存活或未配置，False=已失锚（调用方应退出）。
    """
    if not worktree_path:
        return True
    try:
        return Path(worktree_path).exists()
    except OSError as e:  # 路径查询异常保守视为存活（对标 _session_in_registry 不误退出）
        logger.debug("worktree anchor check failed (assume alive): %s", e)
        return True


def _handle_signal(signum: int, frame) -> None:  # noqa: ANN001
    """signal handler：写 interrupted 记录后 sys.exit(0)。

    daemon 被 _kill_heartbeat_daemon 终止时收到 SIGTERM（Windows: CTRL_BREAK），
    本 handler 写审计记录后优雅退出。
    """
    try:
        project_root = getattr(frame, "f_globals", {}).get("_HB_PROJECT_ROOT", "")
        session_id = getattr(frame, "f_globals", {}).get("_HB_SESSION_ID", "")
        if project_root and session_id:
            hb_path = heartbeat_file_path(project_root, session_id)
            _append_heartbeat_log(hb_path, "interrupted", {"signal": signum})
    except Exception:  # noqa: BLE001 — signal handler 内禁抛
        pass
    sys.exit(0)


def run_daemon(session_id: str, project_root: str | Path, interval: int = _HEARTBEAT_INTERVAL,
               worktree_path: str | Path | None = None) -> int:
    """heartbeat daemon 主循环（独立进程入口）。

    生命周期：
      1. 写 ``started`` 记录
      2. 注册 signal handler（SIGTERM / SIGINT）
      3. ``_INITIAL_DELAY`` 秒后开始心跳循环
      4. 每 ``interval`` 秒：``registry.heartbeat(sid)`` + 追加 ``alive`` 记录
      5. session 不在 registry 中 → 写 ``exited`` 记录，返回 0
      5a. worktree 锚点丢失（worktree_path 已配置且目录消失=退役/删除）→
          写 ``exited``(reason=worktree anchor lost) 记录，返回 0
          （CAND-DAEMON-001 失锚自退 2026-08-17：根治孤儿 daemon 制造假活性——
          #99 族实证 2 个两天残留 daemon，worktree 早无对象仍空转）
      5b. session idle 超 ``_MAX_IDLE_SECONDS``（last_activity 活性锚点，
          heartbeat 不刷新）→ 写 ``exited``(reason=idle timeout) 记录，返回 0
          （#ARCH-HEARTBEAT-002 活性反转治本：消除僵尸 daemon 永久保活死 session）
      6. 异常 → 写 ``error`` 记录，continue（不退出）
      7. 致命错误 → 写 ``fatal`` 记录，返回 1

    Args:
        session_id: session 标识。
        project_root: 项目根目录。
        interval: 心跳间隔（秒，默认 30）。
        worktree_path: 所属 worktree 锚点路径（可选；None=未配置锚，
            跳过失锚检查——兼容旧 spawn 调用方）。

    Returns:
        0=正常退出，1=致命错误。
    """
    root = Path(project_root).resolve()
    hb_path = heartbeat_file_path(root, session_id)

    # 写入全局变量供 signal handler 读取
    globals()["_HB_PROJECT_ROOT"] = str(root)
    globals()["_HB_SESSION_ID"] = session_id

    # 注册 signal handler
    try:
        signal.signal(signal.SIGTERM, _handle_signal)
        signal.signal(signal.SIGINT, _handle_signal)
    except (ValueError, OSError):
        # 子进程可能无法注册所有 signal（非主线程等），best-effort
        pass

    _append_heartbeat_log(hb_path, "started", {"interval": interval})

    # 初始延迟，给 start 调用方时间完成 registry.register
    time.sleep(_INITIAL_DELAY)

    consecutive_errors = 0
    while True:
        try:
            # 检查 session 是否仍在 registry 中
            if not _session_in_registry(session_id, root):
                _append_heartbeat_log(hb_path, "exited", {"reason": "session not in registry"})
                return 0

            # 失锚自退（CAND-DAEMON-001，2026-08-17）：worktree 目录消失=所属
            # worktree 已退役/删除，daemon 继续心跳即"孤儿假活性"（#99 族实证
            # 2 个两天残留 daemon）。锚点未配置（旧 spawn）时跳过，零行为变更。
            if not _worktree_anchor_alive(worktree_path):
                _append_heartbeat_log(
                    hb_path, "exited",
                    {"reason": "worktree anchor lost", "worktree_path": str(worktree_path)},
                )
                return 0

            # 活性反转治本（2026-07-23）：idle 超 _MAX_IDLE_SECONDS 自动退出。
            # daemon 是 last_heartbeat 唯一刷新源——仅以 registry 存在性判活会让
            # chat 异常关闭（未 merge/abort）的 session 被自己的 daemon 永久保活
            # （held_files 永久阻塞）。以 last_activity（真实治理操作时间戳，
            # heartbeat 不刷新）为独立锚点：空闲超时 → 停止心跳并退出 →
            # 90s 后 registry 条目过期 → held_files 自动释放。
            idle = _session_idle_seconds(session_id, root)
            if idle is not None and idle > _MAX_IDLE_SECONDS:
                _append_heartbeat_log(
                    hb_path, "exited",
                    {
                        "reason": "idle timeout",
                        "idle_seconds": round(idle, 1),
                        "timeout_seconds": _MAX_IDLE_SECONDS,
                    },
                )
                return 0

            # 刷新 registry heartbeat
            try:
                from zephyr.security.access_control.session_concurrency import SessionRegistry
                registry = SessionRegistry(root)
                registry.heartbeat(session_id)
            except Exception as e:  # noqa: BLE001 — DB 故障不退出
                _append_heartbeat_log(hb_path, "error", {"error": str(e)[:200]})
                consecutive_errors += 1
                if consecutive_errors > 10:
                    _append_heartbeat_log(
                        hb_path, "fatal",
                        {"reason": "too many consecutive registry errors", "count": consecutive_errors},
                    )
                    return 1
                time.sleep(_REGISTRY_ERROR_BACKOFF)
                continue

            consecutive_errors = 0
            _append_heartbeat_log(hb_path, "alive")
            time.sleep(interval)

        except SystemExit:
            # signal handler 调 sys.exit，已被 _handle_signal 处理
            return 0
        except Exception as e:  # noqa: BLE001 — 兜底，避免 daemon 崩溃无记录
            _append_heartbeat_log(hb_path, "error", {"error": str(e)[:200]})
            consecutive_errors += 1
            time.sleep(_REGISTRY_ERROR_BACKOFF)


if __name__ == "__main__":  # pragma: no cover
    # 命令行入口：python -m zephyr.gov_enforcement.rule_bridge.heartbeat_daemon <sid> [root] [interval] [worktree_path]
    if len(sys.argv) < 2:
        print("Usage: python -m zephyr.gov_enforcement.rule_bridge.heartbeat_daemon <session_id> [project_root] [interval] [worktree_path]", file=sys.stderr)
        sys.exit(2)
    _sid = sys.argv[1]
    _root = sys.argv[2] if len(sys.argv) > 2 else "."
    _interval = int(sys.argv[3]) if len(sys.argv) > 3 else _HEARTBEAT_INTERVAL
    _wt = sys.argv[4] if len(sys.argv) > 4 else None
    sys.exit(run_daemon(_sid, _root, _interval, worktree_path=_wt))
