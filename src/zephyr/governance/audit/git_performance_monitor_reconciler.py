# [BLUEPRINT] MOD-GOV_GIT_PERFORMANCE_MONITOR | docs/03_modules/_domain_governance/blueprint.md | §ARCH-GIT-CALL-BUDGET P3.5
# [MODULE] zephyr.governance.audit.git_performance_monitor_reconciler
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.governance.audit.reconciliation_registry (ReconcileResult, ReconcilerSpec); stdlib (subprocess, time, json, logging, pathlib, datetime, collections)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] post-commit 事件触发（任何 commit 都触发，性能监控是全局关注）；reconciler 永不抛异常（异常降级为 warn）；测量失败不阻断 commit（warn-only）
# [MODIFY-GUARD] GATE_ID / PRIORITY / 阈值常量
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] reconcile 永不抛异常——测量失败降级为 ReconcileResult(action="warn")
# [TESTS] tests/governance/audit/test_git_performance_monitor_reconciler.py
# [A_module] module_id=MOD-GOV_GIT_PERFORMANCE_MONITOR | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m10-time-trigger  M10豁免: reconciler 是 commit 事件触发(非 cron/manual)
"""

git_performance_monitor_reconciler.py — git 性能持续监控 + 早期预警（ARCH-GIT-CALL-BUDGET P3.5，2026-07-19）。

post-commit 事件触发，测量 git status 计时并记录到 ``.runtime/git_performance_log.jsonl``。
当性能退化或 stale worktree 累积超阈值时返回 ``ReconcileResult(action="warn")``。

治本动机（第一性原理）
--------------------
``git_health_smoke.py`` 只在 AI session 启动时跑一次，无法捕获 commit 间的性能退化。
100% AI 开发场景下 commit 是高频操作，每次 commit 后测一次 git status 可建立性能基线，
持续追踪退化趋势。同时监控 stale worktree 累积（P3.5 配套——age-based force-clean 的
早期预警，在 worktree 堆积到影响性能前提示清理）。

设计裁定（对标 trae_064 三原则）
--------------------------------
- **原则①能现成不创造**：复用 ReconciliationRegistry 框架 + git_health_smoke.py 阈值
  （warn=10s, fail=30s），不重新实现检测逻辑
- **原则②创造必全自动**：post-commit 事件触发（非 cron/manual），自动测量+记录+告警
- **原则③第一性原理**：质疑"性能问题应事后排查"——事实是持续监控才能捕获渐进退化

三重预警维度
------------
1. **绝对阈值**：git status 耗时 > 10s（warn）或 > 30s（fail）——对标 git_health_smoke.py
2. **退化趋势**：最近 N 次计时连续递增——捕获渐进退化（如 index 膨胀、worktree 堆积）
3. **stale worktree 累积**：``.aidrafts/`` 下 sess-* 目录数 > 阈值——P3.5 配套预警

日志格式
--------
``.runtime/git_performance_log.jsonl``（追加写，JSONL 格式）::

    {"ts": "2026-07-19T...", "session_id": "sess-...", "commit_sha": "abc123",
     "elapsed_s": 0.42, "status_rc": 0, "stale_worktree_count": 3}

priority: 870（晚于 runtime_violation_snapshot(850)，早于 remediation_progress(900)）

Usage
-----
::

    from zephyr.governance.audit.git_performance_monitor_reconciler import (
        make_git_performance_monitor_reconciler,
    )

    registry.register(make_git_performance_monitor_reconciler(gateway))

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: git status --short 子进程
#   fields: 工作区状态命令（cwd=repo_root，超时 120s）
#   code: measure_git_status L107
# - id: I2
#   name: .aidrafts/ worktree 目录
#   fields: sess-* 前缀的 session worktree 目录
#   code: count_stale_worktrees L135
# - id: I3
#   name: 历史性能日志
#   fields: .runtime/git_performance_log.jsonl 最近条目
#   code: read_recent_perf_entries L168
# 层: 算法
# - id: A1
#   name_zh: ① git status 计时测量
#   name_en: measure_git_status
#   intro: 用 monotonic 钟测 git status 耗时并截取错误摘要
#   desc: 返回 (elapsed_s, returncode, stderr[:120])；超时/异常也返回实测耗时，rc=-1/-2 不阻断
#   inputs: I1
#   outputs: (elapsed, rc, stderr 摘要)
# - id: A2
#   name_zh: ② stale worktree 计数
#   name_en: count_stale_worktrees
#   intro: 数 .aidrafts 下 sess-* 目录个数作为堆积预警信号
#   desc: 只计数不清理（清理由 session_worktree_sweep 负责）；OSError 归 0
#   inputs: I2
#   outputs: stale_worktree_count
# - id: A3
#   name_zh: ③ 性能日志追加
#   name_en: append_perf_log
#   intro: 把本次测量结果追加写进 JSONL 性能日志
#   desc: 条目含 ts/session_id/commit_sha/elapsed_s/status_rc/stale_worktree_count；写失败仅记日志
#   inputs: A1 A2
#   outputs: 性能日志条目
# - id: A4
#   name_zh: ④ 退化趋势检测
#   name_en: detect_degradation_trend
#   intro: 最近 3 次计时连续严格递增就判定性能退化趋势
#   desc: 取最近 N+1 条日志（含本次刚写条目），times[i+1]>times[i] 全成立 → is_degrading；deque(maxlen) 避免读大文件
#   inputs: I3 A3
#   outputs: (is_degrading, recent_times)
# - id: A5
#   name_zh: ⑤ 三重预警判定与 auto-sweep
#   name_en: _reconcile
#   intro: 绝对阈值+stale 堆积+退化趋势三个维度任一命中即 warn
#   desc: rc!=0 或 elapsed>30s fail 阈 / >10s warn 阈 → warn；stale>10 → 触发 session_worktree_sweep 自动清理；趋势退化 → warn；异常降级 warn 永不抛出
#   inputs: A1 A2 A4
#   outputs: ReconcileResult(clean/warn)
#   invariant: reconciler 永不抛异常；测量失败不阻断 commit
# 层: 输出
# - id: O1
#   name_zh: 对账结果 ReconcileResult
#   name_en: ReconcileResult
#   intro: warn=性能退化/stale 堆积预警（gate_id=GATE-GIT-PERFORMANCE-MONITOR），clean=正常
#   downstream: GitCommitGateway MOD-INF-035
# - id: O2
#   name_zh: 性能日志条目
#   name_en: git_performance_log.jsonl 条目
#   intro: 每次 commit 的性能采样落盘，供趋势追踪与退化检测自消费
#   downstream: .runtime/git_performance_log.jsonl（本模块 A4 自消费读回）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A2
# A1 --> A3
# A2 --> A3
# A3 --> O2
# I3 --> A4
# A3 --> A4
# A1 --> A5
# A2 --> A5
# A4 --> A5
# A5 --> O1
"""

from __future__ import annotations

import json
import logging
import subprocess
import time
from collections import deque
from datetime import datetime, timezone
from pathlib import Path

from zephyr.governance.audit.reconciliation_registry import (
    ReconcileResult,
    ReconcilerSpec,
)
from zephyr.shared.infra.process_pool import run_subprocess_hidden

logger = logging.getLogger(__name__)

GATE_ID = "GATE-GIT-PERFORMANCE-MONITOR"
# priority=870: 晚于 runtime_violation_snapshot(850)，早于 remediation_progress(900)
PRIORITY = 870

# 阈值（对标 git_health_smoke.py，单一真源原则——两边一致）
STATUS_WARN_SECONDS = 10.0
STATUS_FAIL_SECONDS = 30.0

# stale worktree 累积预警阈值——超过此数提示运行 session_worktree_sweep()
STALE_WORKTREE_WARN_THRESHOLD = 10

# 性能日志路径（相对 repo root）
PERF_LOG_SUBPATH = ".runtime" + "/" + "git_performance_log.jsonl"

# 退化趋势检测：连续 N 次计时递增视为退化趋势
DEGRADATION_TREND_COUNT = 3

# 单次 git status 超时（秒）
_STATUS_TIMEOUT = 120.0


def _perf_log_path(repo_root: Path) -> Path:
    """性能日志文件路径：.runtime/git_performance_log.jsonl。"""
    return repo_root / Path(PERF_LOG_SUBPATH)


def measure_git_status(repo_root: Path) -> tuple[float, int, str]:
    """测量 git status --short 耗时。

    Returns:
        ``(elapsed_seconds, returncode, stderr_snippet)``。
        失败时 elapsed 仍为实测时间，returncode 非 0。
    """
    start = time.monotonic()
    try:
        r = run_subprocess_hidden(
            ["git", "status", "--short"],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=_STATUS_TIMEOUT,
        )
        elapsed = time.monotonic() - start
        return elapsed, r.returncode, (r.stderr or "").strip()[:120]
    except subprocess.TimeoutExpired:
        elapsed = time.monotonic() - start
        return elapsed, -1, f"timeout after {_STATUS_TIMEOUT}s"
    except Exception as e:  # noqa: BLE001 — 测量失败不阻断 reconciler
        elapsed = time.monotonic() - start
        return elapsed, -2, str(e)[:120]


def count_stale_worktrees(repo_root: Path) -> int:
    """统计 .aidrafts/ 下的 sess-* worktree 目录数。

    这些是潜在的 stale worktree——session_worktree_sweep 会根据 age + 注册状态 +
    分支取代情况清理。本函数仅计数用于预警，不做清理（清理由 sweep 负责）。
    """
    drafts = repo_root / ".aidrafts"
    if not drafts.exists():
        return 0
    count = 0
    try:
        for d in drafts.iterdir():
            if d.is_dir() and d.name.startswith("sess-"):
                count += 1
    except OSError:
        pass  # 计数失败不阻断
    return count


def append_perf_log(repo_root: Path, entry: dict) -> None:
    """追加性能日志条目到 .runtime/git_performance_log.jsonl。

    降级：写入失败仅 debug 日志，绝不阻断 reconciler 主流程。
    """
    log_path = _perf_log_path(repo_root)
    try:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError as e:
        logger.warning("git_performance_monitor: log write failed: %s", e)


def read_recent_perf_entries(repo_root: Path, count: int) -> list[dict]:
    """读取最近 N 条性能日志条目（用 deque 避免读整个大文件）。

    fail-open：读取失败返回空列表（退化趋势检测降级为不触发）。
    """
    log_path = _perf_log_path(repo_root)
    if not log_path.exists():
        return []
    try:
        with open(log_path, "r", encoding="utf-8") as fh:
            recent_lines = list(deque(fh, maxlen=count))
        entries: list[dict] = []
        for line in recent_lines:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue  # 跳过损坏行
        return entries
    except OSError as e:
        logger.warning("git_performance_monitor: log read failed: %s", e)
        return []


def detect_degradation_trend(recent_entries: list[dict]) -> tuple[bool, list[float]]:
    """检测最近 N 条计时是否呈递增趋势（连续 N 次增加）。

    Returns:
        ``(is_degrading, recent_times)``——``recent_times`` 为参与判定的计时列表
        （供告警消息展示）。无足够数据时返回 ``(False, [])``。
    """
    if len(recent_entries) < DEGRADATION_TREND_COUNT:
        return False, []
    recent = recent_entries[-DEGRADATION_TREND_COUNT:]
    times = [float(e.get("elapsed_s", 0)) for e in recent]
    # 连续递增：每对相邻元素后者严格大于前者
    is_increasing = all(times[i + 1] > times[i] for i in range(len(times) - 1))
    return is_increasing, times


def make_git_performance_monitor_reconciler(gateway: "object") -> ReconcilerSpec:
    """构造 GATE-GIT-PERFORMANCE-MONITOR post-commit 性能监控 reconciler。

    Args:
        gateway: GitCommitGateway 实例（仅用其 project_root + _run_git）。

    Returns:
        ReconcilerSpec(gate_id=GATE_ID, priority=PRIORITY)。
        trigger 永远返回 True（任何 commit 都触发性能测量）。
    """
    project_root = gateway.project_root

    def _trigger(committed_files: list[str]) -> bool:
        # 任何 commit 都触发——性能监控是全局关注，不限文件类型
        return True

    def _reconcile(committed_files: list[str], session_id: str) -> ReconcileResult:
        try:
            # 1. 测量 git status 耗时
            elapsed, status_rc, status_err = measure_git_status(project_root)

            # 2. 统计 stale worktree
            stale_count = count_stale_worktrees(project_root)

            # 3. 获取 commit sha（用于日志关联）
            commit_sha = ""
            try:
                sha_result = gateway.run_git(["git", "rev-parse", "HEAD"])
                if sha_result.returncode == 0:
                    commit_sha = sha_result.stdout.strip()[:12]
            except Exception:  # noqa: BLE001 — sha 非关键
                pass

            # 4. 记录性能日志（追加写 JSONL）
            entry = {
                "ts": datetime.now(timezone.utc).isoformat(),
                "session_id": session_id,
                "commit_sha": commit_sha,
                "elapsed_s": round(elapsed, 3),
                "status_rc": status_rc,
                "stale_worktree_count": stale_count,
            }
            append_perf_log(project_root, entry)

            # 5. 三重预警维度判定
            warnings: list[str] = []

            # 维度 1：绝对阈值（对标 git_health_smoke.py）
            if status_rc != 0:
                warnings.append(
                    f"git status 失败(rc={status_rc}): {status_err}"
                )
            elif elapsed > STATUS_FAIL_SECONDS:
                warnings.append(
                    f"git status 耗时 {elapsed:.1f}s > {STATUS_FAIL_SECONDS}s fail 阈值"
                    f"——index 缓存可能损坏，建议 git gc 或排查 worktree 堆积"
                )
            elif elapsed > STATUS_WARN_SECONDS:
                warnings.append(
                    f"git status 耗时 {elapsed:.1f}s > {STATUS_WARN_SECONDS}s warn 阈值"
                    f"——index 缓存需刷新或 worktree 数过多"
                )

            # 维度 2：stale worktree 累积（P3.5 配套预警）
            # #ARCH-WORKTREE-AUTO-SWEEP-001 Phase 1（2026-07-21）：
            # 从 warn-only 升级为 auto-sweep——sweep 三重保护保证安全
            # （不会清理活跃 session 或有未合并提交的 worktree）
            if stale_count > STALE_WORKTREE_WARN_THRESHOLD:
                try:
                    from zephyr.gov_enforcement.rule_bridge.session_worktree import (
                        session_worktree_sweep,
                    )
                    sweep_result = session_worktree_sweep(
                        project_root,
                        max_age_minutes=30,
                        force_clean_hours=0,
                    )
                    warnings.append(
                        f"stale worktree {stale_count} > {STALE_WORKTREE_WARN_THRESHOLD} 阈值，"
                        f"auto-sweep 触发: swept={sweep_result.get('swept', 0)}, "
                        f"skipped={sweep_result.get('skipped', 0)}, "
                        f"warnings={len(sweep_result.get('warnings', []))}"
                    )
                except Exception as sweep_err:  # noqa: BLE001 — sweep 失败降级为 warn
                    warnings.append(
                        f"stale worktree {stale_count} > {STALE_WORKTREE_WARN_THRESHOLD} 阈值，"
                        f"auto-sweep 失败（降级为手动）: {sweep_err}——"
                        f"建议手动运行 session_worktree_sweep()"
                    )

            # 维度 3：退化趋势检测（连续 N 次计时递增）
            # 读最近 N+1 条（含本次刚写的）——但本次刚写未刷盘前读不到，
            # 所以读 N 条历史 + 本次内存中 entry 共 N+1 个数据点
            recent = read_recent_perf_entries(project_root, DEGRADATION_TREND_COUNT + 1)
            # 包含本次 entry（recent 末尾应已包含，因 append_perf_log 已写盘）
            is_degrading, trend_times = detect_degradation_trend(recent)
            if is_degrading:
                warnings.append(
                    f"git status 计时连续 {DEGRADATION_TREND_COUNT} 次递增："
                    f"{[round(t, 2) for t in trend_times]}s——性能退化趋势，"
                    f"建议排查 index 缓存或运行 session_worktree_sweep()"
                )

            if warnings:
                return ReconcileResult(
                    action="warn",
                    detail=(
                        "; ".join(warnings)
                        + f" (elapsed={elapsed:.2f}s, stale_wt={stale_count})"
                    ),
                    gate_id=GATE_ID,
                )
            return ReconcileResult(
                action="clean",
                detail=(
                    f"git status {elapsed:.2f}s, stale_worktrees={stale_count} "
                    f"(warn阈值={STATUS_WARN_SECONDS}s, "
                    f"stale阈值={STALE_WORKTREE_WARN_THRESHOLD})"
                ),
                gate_id=GATE_ID,
            )
        except Exception as e:  # noqa: BLE001 — reconciler 永不抛异常
            logger.warning("git_performance_monitor reconciler failed: %s", e)
            return ReconcileResult(
                action="warn",
                detail=f"monitor failed: {e}",
                gate_id=GATE_ID,
            )

    return ReconcilerSpec(
        gate_id=GATE_ID,
        trigger=_trigger,
        reconcile=_reconcile,
        priority=PRIORITY,
        file_ops=frozenset({"read", "write"}),
    )

# === Reverse-hierarchy backward-compat aliases (R5 private-assert elimination) ===
# Public names above are the primary API. These _-prefixed aliases are kept
# for backward compatibility with any external importer that still references them.
_DEGRADATION_TREND_COUNT = DEGRADATION_TREND_COUNT
_GATE_ID = GATE_ID
_PERF_LOG_SUBPATH = PERF_LOG_SUBPATH
_PRIORITY = PRIORITY
_STALE_WORKTREE_WARN_THRESHOLD = STALE_WORKTREE_WARN_THRESHOLD
_STATUS_FAIL_SECONDS = STATUS_FAIL_SECONDS
_STATUS_WARN_SECONDS = STATUS_WARN_SECONDS
_measure_git_status = measure_git_status
_count_stale_worktrees = count_stale_worktrees
_detect_degradation_trend = detect_degradation_trend
_append_perf_log = append_perf_log
_read_recent_perf_entries = read_recent_perf_entries
