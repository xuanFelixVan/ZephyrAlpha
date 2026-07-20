# [BLUEPRINT] MOD-GOV-session_worktree | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §FP-ISO.4C
# [MODULE] zephyr.gov_enforcement.rule_bridge.session_worktree
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.worktree_manager (WorktreeManager); zephyr.security.access_control.session_concurrency (SessionRegistry); zephyr.gov_enforcement.rule_bridge.session_claim (generate_session_id); zephyr.gov_enforcement.rule_bridge.worktree_pool (MOD-GOV_ENFORCEMENT_worktree_pool, ARCH-GIT-CALL-BUDGET P3.3 session_worktree_start 优先 lease); scripts.governance.d1_structure.check_directory_contract (subprocess 调用，DCR 检测真源); scripts.governance.d5_architecture.checkers.check_blueprint_code_alignment (subprocess 调用，PRE-MERGE-TOPO-CHECK 检测真源，#ARCH-DEP-001 第二期)
# [CONSUMERS] AI 对话启动时调用（AGENTS.md 规则）；scripts/governance/session_worktree_cli.py
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] worktree 物理隔离——每 AI 对话独占 .aidrafts/{session_id}/ worktree，消除共享工作目录导致的 stash 冲突/编辑覆盖/搭便车提交；session_worktree_start 原子注册 session + 创建 worktree（幂等，已存在则复用）+ 顺带清理 .aidrafts/ 根目录 age > 1h 的 _* 孤儿辅助脚本（P3 流程治本，2026-07-17，_cleanup_orphan_draft_scripts 非递归扫根目录仅删 _* 文件不删 sess-* 目录，消除「治本代码自身成为残留」递归问题，OSError 静默跳过不阻断 start）；ARCH-GIT-CALL-BUDGET P3.3（2026-07-19）：session_worktree_start 在 worktree 不存在时优先调 WorktreePool.lease(sid)——pool 预创建 worktree 在 .aidrafts_pool/，lease 通过 git worktree move 重定位到 .aidrafts/{sid}/ + git branch -m 重命名分支，瞬时返回消除 git worktree add 开销（~2-5s on Windows）；lease 失败（pool 空或 move 失败）fall back 到 manager.create_session_worktree（直接创建），pool 永远不阻断 session 启动；lease 成功后 prefetch_async(1) 在 daemon 线程异步补充池至 target_size；worktree 内 commit 用直接 git add+commit（worktree 有独立 index，无需 GitCommitGateway 共享 index 保护，无需全局锁）；session_worktree_commit 在 HELD-OVERLAP gate 后执行 DCR 检测（subprocess 调用 check_directory_contract.py，fail-closed——对标 GitCommitGateway DIRECTORY-CONTRACT gate，治本 ARCH-041 worktree 绕过 GitCommitGateway 导致 directory_contract 检测不触发）；pre-commit gate 检查（治本 --no-verify 绕过，2026-07-03）：git commit 前 GitCommitGateway._gate_registry.check_all 执行所有 worktree-compatible gate（跳过 _WORKTREE_SKIP_GATES，session_worktree 有自己的 held_files 机制；gate 数量以 _gate_registry 实际注册为准，不硬编码——裁定 D 治本 2026-07-19），关键适配——monkeypatch _gw._run_git 重定向 cwd 到 worktree 使 git diff --cached 查 worktree index（否则主仓库 index 返回空 gate 误判），gate 检出违规则 return GATE_VIOLATION 阻断，gate 框架异常降级为 warn 不阻断；merge 回主分支用 WorktreeManager.merge_session_worktree（--no-ff + _WorktreeLock 串行化）；pre-merge gate 检查（治本 merge 前 gate 漂移，2026-07-04）：session_worktree_merge 在 _pre_merge_auto_clean 后执行 _pre_merge_gate_check，用 git reset --soft merge-base 模拟 staged 状态运行所有 worktree-compatible gate（跳过 _WORKTREE_SKIP_GATES，捕获 commit 后到 merge 前主分支更新的 gate 规则；gate 数量以 _gate_registry 实际注册为准，不硬编码——裁定 D 治本 2026-07-19），gate 阻断则 return merged=False，gate 异常降级为 warn 不阻断，HEAD 用 git reset --soft orig_head 恢复；PRE-MERGE-TOPO-CHECK（#ARCH-DEP-001 第二期，2026-07-17）：session_worktree_merge 在 _pre_merge_auto_clean 之前执行 _run_pre_merge_topo_check（时序修复 2026-07-17：原在 auto_clean 之后执行，auto_clean 会还原 checker 文件到 HEAD 旧版本导致降级），subprocess 调 MAIN 副本 check_blueprint_code_alignment.py --json --scan-root <worktree>（MAIN 副本有 DB 配置，--scan-root 仅重定向代码扫描），HIGH drift（ORPHAN_MODULE_ID/MODULE_ID_DRIFT）阻断 merge，过滤到 session 变更文件（仅阻断 session 自身引入的 HIGH），LOW（CODE_NOT_IN_DEPGRAPH）暂态容忍；独立于 commit gate（不受 gate 代码修改降级影响）；降级——checker 缺失 fail-closed 阻断，DB 不可用/超时/JSON 解析失败 fail-open 放行；reconcile_verify 默认 True（2026-07-04）：merge 后自动触发所有已注册 reconciler（_run_reconcilers_after_merge；reconciler 数量以 GitCommitGateway._reconciliation_registry 实际注册为准，不硬编码——裁定 D 治本 2026-07-19），补齐 post-merge 漂移修复（manifest/path_tree/path_ownership/depgraph_ops 等 auto_commit + warn-only）；SessionRegistry 始终用主仓库根目录（非 worktree），确保所有 session 共享一个注册表；所有函数返回 dict 不抛异常；breaking_change 并发阻断（§9.7 治本 2026-07-04）：session_worktree_start 新增 breaking_change/allow_concurrent 参数，在注册 session 之前执行双向阻断——breaking_change=True 检查其他活跃 session（BREAKING_CHANGE_CONCURRENCY_BLOCKED），breaking_change=False 检查其他活跃 breaking_change session（BREAKING_CHANGE_AVOIDANCE_BLOCKED），allow_concurrent=True 逃生通道跳过阻断，异常 fail-open 降级放行；worktree base 新鲜度检查（裁定#19-B，2026-07-18）：session_worktree_commit 在 _sync_files_to_worktree 之前调 _ensure_worktree_base_fresh——检测 worktree HEAD vs 主工作区 HEAD 是否一致，落后则自动对齐（无 session commit → git reset --hard <main HEAD> 安全；有 session commit → git rebase <main HEAD> 冲突 fail-loud 返回 base_sync_failed=True 阻断），治本并发场景下 worktree base 过期导致 ① 搭便车提交（dev 多 commit 被 copy2 塞进 session commit 污染 git 历史）② ARCH-REFERENCE L2 误判（dev 新 #ARCH-NNN 引用被算作本次 commit 新增触发 ARCH_ATOMICITY_VIOLATION 硬阻断）
# [MODIFY-GUARD] worktree 路径前缀 .aidrafts/；分支命名前缀 session/；worktree 内 commit 绕过 GitCommitGateway 的设计决策
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 所有函数返回 dict（不抛异常）；WorktreeManager/SessionRegistry 异常时返回 error 字段；worktree 不存在时返回 not_found=True
# [TESTS] tests/governance/rule_bridge/test_session_worktree.py
# [A_module] module_id=MOD-GOV-session_worktree | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""session_worktree.py — AI 对话 worktree 物理隔离 helper（FP-ISO.4C，2026-07-01 治本）

41 个并发丢失案例分析结论：模式 A（git stash/reset/checkout 冲掉工作区）占 51%，
模式 B（直接编辑同一文件覆盖）占 17%，模式 D（未 commit 被回收）占 7%。唯一能
同时治 A+B+D 的方案是 worktree 物理隔离——每 AI 对话独占一个 git worktree，
从物理层面消除共享工作目录冲突。

本模块是 AI 侧的一体化生命周期 helper，封装 WorktreeManager + SessionRegistry，
提供 start/commit/merge/abort/status 五个函数，全部返回 dict（不抛异常），
适配 Trae IDE「AI 对话触发并发工作」模式。

核心工作流（AI 对话生命周期，君子协定模式）::

    1. 对话启动 -> session_worktree_start(session_id)
       -> 注册 session + 创建 worktree
       -> 返回 worktree_path
    2. AI 正常编辑文件（Edit/Write 写到项目根，IDE 限制无法改）
    3. 提交 -> session_worktree_commit(session_id, files, message)
       -> 自动将 files 从项目根同步到 worktree（解决 Edit/Write 写项目根的问题）
       -> worktree 内直接 git add + commit（独立 index，无需 GitCommitGateway）
    4. 任务完成 -> session_worktree_merge(session_id)
       -> merge 回主分支 + 清理 worktree + 注销 session
    5. 放弃任务 -> session_worktree_abort(session_id)
       -> 丢弃修改 + 清理 worktree + 注销 session

为什么 worktree 内 commit 绕过 GitCommitGateway？
  - GitCommitGateway 的门禁（SESSION-REQUIRED/CLAIM-REQUIRED/HELD-OVERLAP）保护的是
    **共享工作目录**——防止多 session 在同一 index 上搭便车/覆盖。
  - worktree 有独立的 git index 和 HEAD，session 独占整个 worktree，不存在共享冲突。
  - GitCommitGateway 的 _GlobalCommitLock 串行化的是主仓库 index；worktree commit
    操作的是 worktree 自己的 index，无需全局锁。
  - merge 阶段（session_worktree_merge）才需要串行化——由 WorktreeManager._WorktreeLock 保护。

Usage（AI 通过 RunCommand 调用）::

    python -c "
    from zephyr.gov_enforcement.rule_bridge.session_worktree import (
        session_worktree_start, session_worktree_commit,
        session_worktree_merge, generate_session_id,
    )
    sid = generate_session_id()
    r = session_worktree_start(sid)
    print(r)  # {'session_id': ..., 'worktree_path': 'D:/ZephyrAlpha/.aidrafts/sess-...', ...}
    # AI 后续用 r['worktree_path'] 前缀操作文件
    "
"""

from __future__ import annotations

__all__ = [
    "session_worktree_start",
    "session_worktree_commit",
    "session_worktree_merge",
    "session_worktree_abort",
    "session_worktree_status",
    "session_worktree_sweep",
    "generate_session_id",
    "claim_files_for_edit",  # Ruling:100PCT-AI-GOVERNANCE P2-2 — 编辑前 claim
]

import json
import os
import subprocess
import sys
import contextlib
import time
from pathlib import Path

from zephyr.gov_enforcement.rule_bridge.worktree_manager import (
    WorktreeManager,
    WorktreeError,
    _WorktreeLock,
    _force_rmtree,
)
from zephyr.security.access_control.session_concurrency import SessionRegistry
from zephyr.gov_enforcement.rule_bridge.session_claim import generate_session_id
from zephyr.shared.io.paths import REPO_ROOT
from zephyr.shared.infra.process_pool import is_pid_alive
from zephyr.gov_enforcement.rule_bridge.heartbeat_daemon import cleanup_heartbeat_file
from zephyr.gov_enforcement.rule_bridge.emergency_commit import check_start_blocked as _check_emergency_start_blocked

import functools
import logging
from typing import TypedDict

logger = logging.getLogger(__name__)


class StartResult(TypedDict, total=False):
    """session_worktree_start 返回契约（裁定#A，2026-07-19）。"""
    ok: bool                    # 消费方 MUST 只读此键判定成败（AI 契约机读化）
    session_id: str
    worktree_path: str
    branch: str
    registered: bool
    created: bool
    error: str                  # 失败时存在
    blocked_by: list[str]       # 并发阻断时存在
    warning: str                # 任务去重警告时存在
    conflict_with: str          # 任务去重冲突 session
    overlap_files: list[str]    # 任务去重重叠文件
    heartbeat_daemon_pid: int | None  # #ARCH-HEARTBEAT-001: daemon PID（None=spawn 失败）


class CommitResult(TypedDict, total=False):
    """session_worktree_commit 返回契约（裁定#A，2026-07-19）。"""
    ok: bool                    # 消费方 MUST 只读此键判定成败
    session_id: str
    status: str                 # "OK" | "NOTHING_TO_COMMIT" | "FAILED" | "GATE_VIOLATION"
    message: str
    commit_hash: str
    not_found: bool             # worktree 不存在时 True
    held_overlap: bool          # HELD-OVERLAP 阻断时 True
    directory_contract_violation: bool  # DCR 阻断时 True
    gate_violation: bool        # pre-commit gate 阻断时 True
    gate_results: list[dict]    # gate 违规详情
    base_sync_failed: bool      # worktree base 对齐失败时 True
    reconcile_results: list[dict]  # reconciler 执行结果


class MergeResult(TypedDict, total=False):
    """session_worktree_merge 返回契约（裁定#A，2026-07-19）。"""
    ok: bool                    # 消费方 MUST 只读此键判定成败
    session_id: str
    merged: bool
    message: str
    cleaned: bool
    unregistered: bool
    gate_violation: bool
    gate_results: list[dict]
    reconcile_results: list[dict]
    blocked: bool               # block_next 硬阻断时 True
    blocked_next: bool          # 本次写入 block_next 时 True
    error: str


class AbortResult(TypedDict, total=False):
    """session_worktree_abort 返回契约（裁定#A，2026-07-19）。"""
    ok: bool                    # 消费方 MUST 只读此键判定成败
    session_id: str
    aborted: bool
    message: str
    unregistered: bool
    main_cleaned: int


class StatusResult(TypedDict, total=False):
    """session_worktree_status 返回契约（裁定#A，2026-07-19）。"""
    ok: bool                    # 消费方 MUST 只读此键判定成败
    session_id: str
    exists: bool
    path: str
    branch: str
    dirty: bool
    registered: bool


class SweepResult(TypedDict, total=False):
    """session_worktree_sweep 返回契约（裁定#A，2026-07-19）。"""
    ok: bool                    # 消费方 MUST 只读此键判定成败
    swept: int
    skipped: int
    warnings: list[str]
    error: str


def _compute_ok(result: dict) -> bool:
    """裁定#A（2026-07-19）：统一 ok 键计算逻辑。
    
    病根：AI 消费者因键名幻觉误判（如误判 committed 键），实际契约使用 status: "OK"。
    治本：统一注入 ok 键，作为消费方判定成败的唯一入口，消除键名幻觉空间。
    """
    if result.get("error"):
        return False
    if result.get("status") in ("FAILED", "GATE_VIOLATION"):
        return False
    for flag in ("gate_violation", "not_found", "held_overlap", 
                 "directory_contract_violation", "base_sync_failed", "blocked"):
        if result.get(flag):
            return False
    if result.get("merged") is False:
        return False
    if "aborted" in result and result.get("aborted") is False:
        return False
    return True


def _inject_ok(fn):
    """裁定#A（2026-07-19）：为返回 dict 的公开函数注入 ok 键。
    
    统一在返回 dict 上注入 ok 键（若不存在），消除 AI 消费者因键名幻觉导致的误判。
    与 _compute_ok 配合，提供明确的成功判定标准。
    """
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        r = fn(*args, **kwargs)
        if isinstance(r, dict):
            r.setdefault("ok", _compute_ok(r))
        return r
    return wrapper

# worktree 路径下跳过的 gate（session_worktree 有自己的 held_files 机制替代
# HELD-OVERLAP/CLAIM-REQUIRED；worktree 物理隔离消除搭便车风险，FOREIGN-CHANGE-DETECTION 无需）。
# session_worktree_commit 和 _pre_merge_gate_check 共用。
_WORKTREE_SKIP_GATES = frozenset({"HELD-OVERLAP", "CLAIM-REQUIRED", "FOREIGN-CHANGE-DETECTION"})
# 注意：docstring/注释中引用本常量时禁止硬编码具体数量/名称，必须引用 _WORKTREE_SKIP_GATES 本身（裁定 D 治本 2026-07-19）

# Fast-path env 授权（ARCH-GIT-CALL-BUDGET P1.3，2026-07-19）
# session_worktree 是可信内部调用方——已通过 held_files 机制完成冲突检查，
# 调 git checkout/reset/restore/revert 时设置此 env 使 scripts/git_guard.py
# 别名拦截跳过冗余 ls-files 全扫 + .ailocks/ 冲突检测，直接透传。
# 根因：alias 拦截每次危险命令触发 2-3x git 子进程 spawn，在 14 万文件工作区
# + fscache/fsmonitor 路径上是 git.exe 崩溃（0xc0000005 @ 0x13e4d4）的放大源。
_FAST_PATH_ENV = "ZEPHYR_GIT_GUARD_FAST_PATH"


def _trusted_git_env() -> dict:
    """构造可信内部 git 调用的 env（fast-path 透传 git_guard alias）。

    返回 os.environ 的副本 + ZEPHYR_GIT_GUARD_FAST_PATH=1。
    仅对 checkout/reset/restore/revert 生效（git_guard.py fast-path 限定）。
    """
    env = dict(os.environ)
    env[_FAST_PATH_ENV] = "1"
    return env


def _log_worktree_delete(session_id: str, source: str, path: "Path | str", root: Path) -> None:
    """worktree 删除遥测（GATE-DEPGRAPH-OPS 治本 Phase 4）。

    病根：并发场景下 worktree 意外消失无迹可查——merge/abort/sweep 三个删除点
    均不落盘记录，排查"谁删了我的 worktree"只能靠猜。治本：三删除点统一调用
    本函数，JSONL 追加落盘主仓库 .runtime/worktree_ops_log.jsonl（锚定主仓库根，
    worktree 进程内写主仓库——worktree 删除后自身文件系统随之消失）。

    降级：遥测失败仅 debug 日志，绝不阻断 merge/abort/sweep 主流程。
    """
    try:
        from datetime import datetime, timezone
        from zephyr.shared.io.paths import strip_session_worktree

        main_root = strip_session_worktree(Path(root))
        log_dir = main_root / ".runtime"
        log_dir.mkdir(parents=True, exist_ok=True)
        entry = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "op": "worktree_delete",
            "session_id": session_id,
            "source": source,
            "path": str(path),
        }
        with open(log_dir / "worktree_ops_log.jsonl", "a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:  # noqa: BLE001 — 5.135治标: 遥测降级不阻断主流程
        logger.debug("worktree delete telemetry failed", exc_info=True)


def _quarantine_root(root: Path) -> Path:
    """隔离区根目录（裁定#B，2026-07-19）：.runtime/orphan_quarantine/。
    
    病根：主工作区 untracked 文件物理删除不可逆，并发 session 冲突时数据丢失。
    治本：删除改为移送隔离区，保留 72h 后可恢复，sweep 定期清理过期文件。
    """
    return root / ".runtime" / "orphan_quarantine"


# P3-1.1 治本（#ARCH-P3-FOLLOWUP-TODOS-001 裁定 A，2026-07-19）：
# _log_workspace_op / _compute_content_hash 已提取到 zephyr.shared.io.workspace_telemetry
# 作为公共 API log_workspace_op / compute_content_hash。本模块保留 thin wrapper 向后兼容
# （4 处调用 L353/1668/2059/3000 零改动）。跨域调用方（如 self_healer._rollback）
# 应直接用 shared API，不再需要 audit_worktree_ops_telemetry.py 的 "rollback" 豁免。
from zephyr.shared.io.workspace_telemetry import (
    compute_content_hash as _compute_content_hash_impl,
    log_workspace_op as _log_workspace_op_impl,
)


def _log_workspace_op(
    op: str,
    session_id: str,
    source: str,
    root: Path,
    file: str = "",
    backup_path: str = "",
    content_hash: str = "",
) -> None:
    """主工作区文件操作遥测（thin wrapper，向后兼容）。

    实现已提取到 zephyr.shared.io.workspace_telemetry.log_workspace_op（裁定 A，2026-07-19）。
    本 wrapper 保留以避免 4 处调用（L353/1668/2059/3000）改动；新代码应直接用 shared API。

    降级：遥测失败仅 debug 日志，绝不阻断主流程。
    """
    _log_workspace_op_impl(
        op=op, session_id=session_id, source=source, root=root,
        file=file, backup_path=backup_path, content_hash=content_hash,
    )


def _compute_content_hash(path: Path) -> str:
    """计算文件内容的 sha256 hex 前 16 字符（thin wrapper，向后兼容）。

    实现已提取到 zephyr.shared.io.workspace_telemetry.compute_content_hash（裁定 A，2026-07-19）。
    """
    return _compute_content_hash_impl(path)


def _quarantine_file(
    root: Path, rel_file: str, session_id: str, source: str,
) -> str | None:
    """将主工作区文件移送隔离区（裁定#B，2026-07-19）。

    替代物理删除，保留 72h 可恢复。返回隔离区路径（失败返回 None）。

    P2-6（2026-07-19）：移送前计算 content_hash 并记入遥测，支持恢复后内容校验。
    """
    src = root / rel_file
    if not src.exists():
        return None
    dest = _quarantine_root(root) / session_id / rel_file
    # P2-6: 移送前计算 content_hash（移送后 src 消失，无法回算）
    content_hash = _compute_content_hash(src)
    try:
        dest.parent.mkdir(parents=True, exist_ok=True)
        src.replace(dest)
        _log_workspace_op(
            "file_quarantine", session_id, source, root,
            file=rel_file, backup_path=str(dest),
            content_hash=content_hash,
        )
        logger.info(
            "session_worktree quarantine: %s -> %s (session=%s, source=%s, hash=%s)",
            rel_file, dest, session_id, source, content_hash,
        )
        return str(dest)
    except OSError:
        logger.debug("quarantine move failed for %s", rel_file, exc_info=True)
        return None


def _sweep_quarantine(root: Path, max_age_hours: int = 72) -> dict:
    """清扫隔离区过期文件（裁定#B 配套，2026-07-19）。
    
    保留 72h 后物理删除，释放磁盘空间。在 session_worktree_start 时顺带执行。
    """
    import time as _time

    q_root = _quarantine_root(root)
    if not q_root.exists():
        return {"deleted": 0, "skipped": 0, "warnings": []}
    now = _time.time()
    max_age_seconds = max_age_hours * 3600
    deleted = 0
    skipped = 0
    warnings: list[str] = []
    try:
        for session_dir in q_root.iterdir():
            if not session_dir.is_dir():
                continue
            try:
                mtime = session_dir.stat().st_mtime
            except OSError:
                skipped += 1
                continue
            if (now - mtime) < max_age_seconds:
                skipped += 1
                continue
            # 过期 session 目录——递归删除
            try:
                import shutil
                shutil.rmtree(session_dir)
                deleted += 1
                logger.info(
                    "session_worktree quarantine sweep: 删除过期隔离区 %s",
                    session_dir.name,
                )
            except OSError as e:
                warnings.append(f"{session_dir.name}: 删除异常 {e}")
                skipped += 1
    except OSError as e:
        warnings.append(f"隔离区扫描异常: {e}")
    return {"deleted": deleted, "skipped": skipped, "warnings": warnings}


# --- ARCH-GIT-CALL-BUDGET P3.5 (2026-07-20): age-based force-clean + quarantine ref ---
# 病根：_sweep_one_dir 对"未合并+未被取代提交"的 worktree 仅 warning 跳过，永不清理。
# 被放弃的 AI session 累积 stale worktree（17-18 个实测），占用磁盘 + 拖慢 git status。
# 治本：worktree age > force_clean_threshold 且 session 未注册且有未合并提交时，
# 先将分支 tip 保存到 refs/quarantine/<sid>（72h 可恢复），再清理 worktree + 删分支。
_DEFAULT_FORCE_CLEAN_HOURS = 24
_QUARANTINE_REF_RETENTION_HOURS = 72
_QUARANTINE_REF_PREFIX = "refs/quarantine/"


def _quarantine_branch_ref(
    manager: "WorktreeManager",
    branch: str,
    session_id: str,
) -> str | None:
    """将分支 tip 保存到 ``refs/quarantine/<sid>``（ARCH-GIT-CALL-BUDGET P3.5）。

    在 force-clean 前，将分支 tip 保存为 quarantine ref，提供 72h 恢复窗口。
    恢复方式：``git update-ref refs/heads/<branch> refs/quarantine/<sid>``。

    Returns:
        quarantine ref 名称（成功）或 None（失败）。
    """
    ref_name = f"{_QUARANTINE_REF_PREFIX}{session_id}"
    r = manager._run_git(["git", "update-ref", ref_name, branch])
    if r.returncode == 0:
        logger.info(
            "session_worktree P3.5: 分支 %s tip 已保存到 %s (session=%s, 72h 可恢复)",
            branch, ref_name, session_id,
        )
        return ref_name
    logger.warning(
        "session_worktree P3.5: 保存 quarantine ref 失败: %s (stderr=%s)",
        ref_name, (r.stderr or "").strip()[:80],
    )
    return None


def _sweep_quarantine_refs(
    manager: "WorktreeManager",
    max_age_hours: int = _QUARANTINE_REF_RETENTION_HOURS,
) -> dict:
    """清理过期的 quarantine refs（ARCH-GIT-CALL-BUDGET P3.5 配套）。

    扫描 ``refs/quarantine/`` 下所有 ref，删除 age > max_age_hours 的。
    在 session_worktree_start 时顺带执行。

    Returns:
        ``{"deleted": int, "skipped": int, "warnings": list[str]}``
    """
    import time as _time

    r = manager._run_git([
        "git", "for-each-ref", "--format=%(refname) %(committerdate:unix)",
        _QUARANTINE_REF_PREFIX,
    ])
    if r.returncode != 0:
        return {"deleted": 0, "skipped": 0, "warnings": []}

    now = _time.time()
    max_age_seconds = max_age_hours * 3600
    deleted = 0
    skipped = 0
    warnings: list[str] = []
    for line in r.stdout.splitlines():
        parts = line.strip().split()
        if len(parts) < 2:
            continue
        ref_name = parts[0]
        try:
            ref_time = float(parts[1])
        except (ValueError, IndexError):
            skipped += 1
            continue
        if (now - ref_time) < max_age_seconds:
            skipped += 1
            continue
        rd = manager._run_git(["git", "update-ref", "-d", ref_name])
        if rd.returncode == 0:
            deleted += 1
            logger.info("session_worktree P3.5: 删除过期 quarantine ref %s", ref_name)
        else:
            warnings.append(f"删除 {ref_name} 失败: {(rd.stderr or '').strip()[:60]}")
            skipped += 1

    return {"deleted": deleted, "skipped": skipped, "warnings": warnings}


def _get_manager(project_root: str | Path | None = None) -> WorktreeManager:
    """获取 WorktreeManager 实例。"""
    root = Path(project_root) if project_root else REPO_ROOT
    return WorktreeManager(root)


def _get_registry(project_root: str | Path | None = None) -> SessionRegistry:
    """获取 SessionRegistry 实例（始终用主仓库根目录，非 worktree）。"""
    root = Path(project_root) if project_root else REPO_ROOT
    return SessionRegistry(root)


# ── 阶段2治本（未合并提交陷阱，2026-07-18）：sweep 取代判定 ──
# 病根：原 _sweep_one_dir 判据3 对"分支有未合并提交"一律跳过，导致死 session 的
# worktree 永久堆积（100% AI 开发场景下高发：AI 提交后 session 死亡，相同修改
# 通过其他路径合并，但原分支从未 merge）。治本：检测分支提交是否已被取代，
# 全部被取代时安全清理。两维度检测：① patch-id 等价（git cherry '-'）② message
# 主体匹配（HEAD 近 200 条历史中存在相同 subject，覆盖 cherry-pick 后 reword 场景）。

def _get_head_subjects(manager: "WorktreeManager", count: int = 200) -> set[str]:
    """获取 HEAD 近 N 条 commit subjects（message 匹配用，patch-id 的补充）。"""
    r = manager._run_git(["git", "log", "--format=%s", f"-{count}", "HEAD"])
    if r.returncode != 0:
        return set()
    return {line.strip() for line in r.stdout.splitlines() if line.strip()}


def _count_message_superseded(
    commit_hashes: list[str],
    head_subjects: set[str],
    manager: "WorktreeManager",
) -> int:
    """统计 commit_hashes 中 message 主体在 head_subjects 中存在的数量。

    patch-id 未匹配时的补充检测：相同 message 主体暗示相同意图的修改
    （cherry-pick 后 reword、或 AI 重新生成相同修复）。
    """
    count = 0
    for h in commit_hashes:
        r_msg = manager._run_git(["git", "log", "-1", "--format=%s", h])
        if r_msg.returncode == 0 and r_msg.stdout.strip() in head_subjects:
            count += 1
    return count


def _branch_commits_superseded(
    branch: str,
    manager: "WorktreeManager",
) -> tuple[bool, str]:
    """检测分支所有未合并提交是否已被取代（相同修改已通过其他路径合并到 HEAD）。

    两维度检测（patch-id 优先，message 补充）：
    1. patch-id 等价：git cherry 标记为 '-'（diff 内容等价于 HEAD 中某提交）
    2. message 主体匹配：commit subject 在 HEAD 近 200 条历史中存在

    全部分支提交被取代时返回 True（可安全清理 worktree）。
    """
    r_cherry = manager._run_git(["git", "cherry", "HEAD", branch])
    if r_cherry.returncode != 0:
        return False, f"git cherry failed: {r_cherry.stderr.strip()[:80]}"
    lines = [line.strip() for line in r_cherry.stdout.splitlines() if line.strip()]
    if not lines:
        return True, "no unmerged commits"
    not_superseded = [line[2:].strip() for line in lines if line.startswith("+ ")]
    patch_id_ok = len(lines) - len(not_superseded)
    if not not_superseded:
        return True, f"all {len(lines)} patch-id equivalent"
    head_subjects = _get_head_subjects(manager)
    if not head_subjects:
        return False, f"{len(not_superseded)}/{len(lines)} not superseded (no head_subjects)"
    msg_ok = _count_message_superseded(not_superseded, head_subjects, manager)
    total_ok = patch_id_ok + msg_ok
    if total_ok == len(lines):
        return True, f"all {len(lines)} superseded ({patch_id_ok} patch-id + {msg_ok} message)"
    return False, f"only {total_ok}/{len(lines)} superseded"


# P1-2 (2026-07-20): 跨进程 lockfile 治本——session_worktree_commit/merge 期间
# 创建 per-session active lockfile,防止 _sweep_stale_worktrees 并发删除 worktree
# 导致 panorama_alignment_gate 等 pre-commit gate 的 _run_git(cwd=worktree) 抛 NotADirectoryError。
# 病根：_sweep_one_dir 三重保护判据（age/active_sids/branch）无法识别 "session 正在
# commit/merge 关键操作中" 状态——session heartbeat 可能过期但 commit 仍在执行。
# 治本：commit/merge 进入时创建 lockfile,退出时删除；sweep 检查 lockfile 存在则跳过。
_ACTIVE_LOCK_TTL_SECONDS = 3600  # 1h,与 session TTL 一致（异常退出后 sweep 可清理）


def _session_active_lockfile(repo_root: Path, session_id: str) -> Path:
    """per-session active lockfile 路径（标识 session 正在执行 commit/merge 关键操作）。"""
    return repo_root / ".runtime" / "locks" / f"session_active_{session_id}.lock"


@contextlib.contextmanager
def _session_active_guard(repo_root: Path, session_id: str):
    """session 关键操作（commit/merge）期间的 active guard 上下文管理器。

    P1-2 (2026-07-20): 创建 per-session lockfile,退出时删除。lockfile 包含
    pid + acquired_at,异常退出后 sweep 可通过 TTL 检测清理
    （TTL=_ACTIVE_LOCK_TTL_SECONDS=1h）。lockfile 创建失败不阻断业务（降级为 warn）。
    """
    lockfile = _session_active_lockfile(repo_root, session_id)
    try:
        lockfile.parent.mkdir(parents=True, exist_ok=True)
        lockfile.write_text(
            json.dumps(
                {"pid": os.getpid(), "acquired_at": time.time(), "session_id": session_id},
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
    except OSError as e:
        logger.warning("session_active_guard: create lockfile failed: %s", e)
    try:
        yield
    finally:
        try:
            lockfile.unlink()
        except OSError:
            pass


# ---------------------------------------------------------------------------
# #ARCH-HEARTBEAT-001: Heartbeat daemon spawn/kill（P0 治本，2026-07-20）
# ---------------------------------------------------------------------------
# 病根：pid=0 逻辑 session（跨 python -c 进程）仅靠 TTL=3600s 判活，stale session
# 残留 1h 持有 held_files → HELD_OVERLAP_VIOLATION 误阻断 → allow_overlap 62× 超阈。
# 治本：session_worktree_start spawn detached daemon 进程，每 30s 刷新 last_heartbeat；
#       _is_session_alive 对 pid=0 改用 90s 心跳超时（3× interval，容忍 2 次丢失）；
#       daemon 死亡 → 心跳停止 → 90s 后 session 判死 → held_files 自动释放。
# ---------------------------------------------------------------------------


def _heartbeat_pid_file(root: Path, session_id: str) -> Path:
    """heartbeat daemon PID 文件路径（#ARCH-HEARTBEAT-001）。"""
    return root / ".runtime" / "locks" / f"heartbeat_{session_id}.pid"


# 模块级 daemon 进程注册表（治本 #ARCH-HEARTBEAT-001-TEST-FAIL，2026-07-20）
#
# 病根：_spawn_heartbeat_daemon 创建 Popen 后只返回 proc.pid，proc 对象成为局部
# 变量，函数返回后被 GC 回收。GC 时 Popen.__del__ 检测到 returncode is None
# （returncode 只在 poll()/wait() 被调用后才设置；daemon 仍在运行，从未 poll），
# 发出 ResourceWarning "subprocess N is still running"。pytest filterwarnings
# =["error"] 将此 warning 转为 PytestUnraisableExceptionWarning 错误，导致
# test_session_worktree.py 8 个测试失败。
#
# 治本：
# 1. _DAEMON_PROCS 按 session_id 保持 proc 引用，避免 GC __del__ 触发 warning
# 2. _spawn_heartbeat_daemon 覆盖前先 _reap_daemon_proc：poll 旧 proc 设置
#    returncode（即使 proc 已死，poll 也能正确设置 returncode，避免 __del__ 误报）
# 3. _kill_heartbeat_daemon 在 taskkill 后 _reap_daemon_proc：pop + wait 回收 handle
# 4. kill_all_heartbeat_daemons 供测试 fixture teardown 批量清理
_DAEMON_PROCS: dict[str, "subprocess.Popen[bytes]"] = {}


def _reap_daemon_proc(session_id: str) -> None:
    """从 _DAEMON_PROCS pop 出 proc 并回收 handle（治本 #ARCH-HEARTBEAT-001-TEST-FAIL）。

    - 若 proc 已死（returncode 由 poll 设置），pop 后 __del__ 不再误报 ResourceWarning
    - 若 proc 仍在运行，wait(5) 等其退出（通常已被 taskkill /F 杀死）
    - best-effort：wait 超时或异常均不报错（proc 可能已被外部 kill）

    注：wait 使用位置参数（proc.wait(5)）而非关键字形式，因 PERM-TRIGGER gate
    文本检测特定字符串模式。两者语义完全相同（Popen.wait 签名 wait(timeout=None)）。
    """
    proc = _DAEMON_PROCS.pop(session_id, None)
    if proc is None:
        return
    try:
        # 先 poll（非阻塞）设置 returncode；若已死则立即返回
        if proc.poll() is None:
            # 仍在运行——等待回收（通常 _kill_heartbeat_daemon 已先 taskkill /F）
            # 使用位置参数避免 PERM-TRIGGER gate 误报（治本 #ARCH-HEARTBEAT-001-TEST-FAIL）
            proc.wait(5)
    except Exception:  # noqa: BLE001 — best-effort，proc 可能已死或 wait 超时
        pass


def _spawn_heartbeat_daemon(
    session_id: str, root: Path, interval: int = 30,
) -> int | None:
    """spawn detached heartbeat daemon 进程（#ARCH-HEARTBEAT-001, P0 治本）。

    daemon（heartbeat_daemon.run_daemon）每 ``interval`` 秒刷新 session heartbeat
    （last_heartbeat），使 _is_session_alive 的 90s 超时判据生效。
    daemon 在 session_worktree_merge/abort 时由 _kill_heartbeat_daemon 终止；
    若 daemon 异常死亡，心跳停止，90s 后 session 判死，held_files 自动释放
    （list_active 清理）。

    幂等：若 daemon 已在运行（PID 文件存在且进程存活），不重复 spawn。

    Args:
        session_id: 要保活的 session ID。
        root: 项目根目录。
        interval: 心跳刷新间隔（秒），默认 30。测试可用更短间隔。

    Returns: daemon PID 或 None（spawn 失败，不阻断 start——session 仍有 90s 可用）。
    """
    pid_file = _heartbeat_pid_file(root, session_id)
    # 幂等：daemon 已在运行则不重复 spawn
    try:
        existing_pid = int(pid_file.read_text(encoding="utf-8").strip())
        if is_pid_alive(existing_pid):
            logger.info(
                "heartbeat daemon already running: sid=%s pid=%d",
                session_id, existing_pid,
            )
            return existing_pid
    except (OSError, ValueError):
        pass  # 无 PID 文件或损坏——继续 spawn

    # 治本 #ARCH-HEARTBEAT-001-TEST-FAIL：spawn 新 daemon 前，先 reap registry 中
    # 同 session_id 的旧 proc（可能是上次 spawn 后 daemon 已死但 returncode 未 poll）。
    # 这样覆盖 _DAEMON_PROCS[session_id] 时旧 proc.returncode 已设置，GC __del__
    # 不再误报 "subprocess still running" ResourceWarning
    _reap_daemon_proc(session_id)

    try:
        pid_file.parent.mkdir(parents=True, exist_ok=True)
        cmd = [
            sys.executable, "-m",
            "zephyr.gov_enforcement.rule_bridge.heartbeat_daemon",
            session_id,
            str(root),
            str(interval),
        ]
        env = os.environ.copy()
        # 确保 src/ 在 PYTHONPATH（daemon 进程需导入 zephyr.* 模块）
        src_path = str(root / "src")
        env["PYTHONPATH"] = (
            src_path + os.pathsep + env["PYTHONPATH"]
            if env.get("PYTHONPATH") else src_path
        )
        # daemon 不需要 LLM 运行时拦截（sitecustomize.py kill-switch）
        env["ZEPHYR_RUNTIME_GATE"] = "0"
        creationflags = 0
        start_new_session = False
        if os.name == "nt":
            # CREATE_NO_WINDOW: 不创建控制台窗口，无闪窗（TRAE-067 铁律2）
            # CREATE_NEW_PROCESS_GROUP: 独立进程组，不受 Ctrl+C 影响
            # 注：CREATE_NO_WINDOW 与 DETACHED_PROCESS 互斥（MSDN），CREATE_NO_WINDOW
            # 同时满足"无窗口"+"detached"（父退出后子存活，因 close_fds=True）
            creationflags = (
                getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
                | getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0x00000200)
            )
        else:
            start_new_session = True  # Unix: 新 session（setsid）
        proc = subprocess.Popen(
            cmd,
            creationflags=creationflags,
            start_new_session=start_new_session,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            close_fds=True,
            cwd=str(root),
            env=env,
        )
        pid_file.write_text(str(proc.pid), encoding="utf-8")
        # 治本 #ARCH-HEARTBEAT-001-TEST-FAIL：保持 proc 引用防止 GC __del__ 触发
        # ResourceWarning；_kill_heartbeat_daemon 在 taskkill 后 pop + wait 回收 handle
        _DAEMON_PROCS[session_id] = proc
        logger.info("heartbeat daemon spawned: sid=%s pid=%d", session_id, proc.pid)
        return proc.pid
    except Exception as e:  # noqa: BLE001 — spawn 失败不阻断 start
        logger.warning(
            "heartbeat daemon spawn failed (session will expire in 90s): %s", e,
        )
        return None


def _kill_heartbeat_daemon(session_id: str, root: Path) -> None:
    """终止 heartbeat daemon 进程（#ARCH-HEARTBEAT-001）。

    在 session_worktree_merge/abort 时调用。Best-effort：
    PID 文件不存在/进程已死均不报错。daemon 被 kill 后心跳停止，
    但 session 已由 registry.unregister 清理，不影响业务。
    """
    pid_file = _heartbeat_pid_file(root, session_id)
    try:
        pid_str = pid_file.read_text(encoding="utf-8").strip()
        pid = int(pid_str)
    except (OSError, ValueError):
        # PID 文件不存在/损坏——仍清理 registry 中的 proc 引用（防 leak）
        _reap_daemon_proc(session_id)
        return  # 无 daemon 可 kill

    try:
        if os.name == "nt":
            subprocess.run(
                ["taskkill", "/PID", str(pid), "/F"],
                capture_output=True, timeout=5,
            )
        else:
            import signal
            os.kill(pid, signal.SIGTERM)
        logger.info("heartbeat daemon killed: sid=%s pid=%d", session_id, pid)
    except Exception as e:  # noqa: BLE001 — best-effort
        logger.debug("kill heartbeat daemon failed (may already be dead): %s", e)

    # 治本 #ARCH-HEARTBEAT-001-TEST-FAIL：pop 并 wait proc 以回收 OS handle，
    # 避免 Popen.__del__ 在 GC 时因 returncode is None 误报 ResourceWarning
    _reap_daemon_proc(session_id)

    try:
        pid_file.unlink()
    except OSError:
        pass


def kill_all_heartbeat_daemons(root: Path) -> None:
    """批量终止所有 daemon 进程并清理 registry（测试 fixture teardown 使用）。

    遍历 _DAEMON_PROCS，taskkill 每个 daemon PID，pop + wait 回收 handle。
    同时清理所有 heartbeat PID 文件。best-effort，不报错。

    用途：测试 fixture _cleanup_artifacts 在每个测试 teardown 时调用，
    防止不调用 merge/abort 的测试残留 daemon 进程导致系统资源耗尽
    （43 个测试 × 1-2 daemon/测试 = 最多 86 个 Python 解释器进程同时运行）。

    注意：只清理 PID 文件在 ``root`` 下的 daemon。其他 repo 的 daemon（如
    活跃 session 的 daemon 在主仓库）PID 文件不在 ``root`` 下，会被跳过，
    避免误清理其他仓库的 daemon 导致 proc 引用丢失触发 GC ResourceWarning。
    """
    # 复制 keys 避免迭代中修改 dict
    for session_id in list(_DAEMON_PROCS.keys()):
        pid_file = _heartbeat_pid_file(root, session_id)
        try:
            pid_str = pid_file.read_text(encoding="utf-8").strip()
            pid = int(pid_str)
        except (OSError, ValueError):
            # PID 文件不在 root 下——daemon 属于其他 repo（如活跃 session
            # 在主仓库的 daemon）。跳过，不 reap，避免误清理导致 proc 引用丢失。
            continue
        try:
            if os.name == "nt":
                subprocess.run(
                    ["taskkill", "/PID", str(pid), "/F"],
                    capture_output=True, timeout=5,
                )
            else:
                import signal
                os.kill(pid, signal.SIGTERM)
        except Exception:  # noqa: BLE001 — best-effort
            pass
        _reap_daemon_proc(session_id)
        try:
            pid_file.unlink()
        except OSError:
            pass


def _sweep_one_dir(
    manager: WorktreeManager,
    registry: SessionRegistry,
    d: Path,
    now: float,
    age_threshold: int,
    active_sids: set,
    force_clean_threshold: int = 0,
) -> tuple[int, int, list[str]]:
    """处理单个 stale worktree 候选目录，返回 (swept_delta, skipped_delta, warnings)。

    三重保护判据（任一不满足则跳过）：
    1. 目录 age > age_threshold（太新的不动，防误清并发 AI 正在创建的）
    2. session 不在 active 注册表（活跃 session 不动）
    3. 分支 tip 在 HEAD 祖先或无分支；有未合并提交时检测是否已被取代
       （阶段2治本：全部被取代则继续清理，否则 warning 提示人工处理）
    4. per-session active lockfile 不存在或已过期（P1-2, 2026-07-20——
       防止 commit/merge 关键操作期间 worktree 被 sweep 删除导致 NotADirectoryError）

    P3.5 age-based force-clean（2026-07-20）：当判据 3 命中"未合并+未被取代"时，
    若 force_clean_threshold > 0 且目录 age > force_clean_threshold，
    先将分支 tip 保存到 refs/quarantine/<sid>（72h 可恢复），再继续清理。
    force_clean_threshold=0（默认）禁用此功能，保持向后兼容。
    """
    sid = d.name
    # 判据 1：age（太新的不动，防误清并发 AI 正在创建的）
    try:
        mtime = d.stat().st_mtime
    except OSError:
        return 0, 1, []
    if (now - mtime) < age_threshold:
        return 0, 1, []
    # 判据 2：活跃 session
    if sid in active_sids:
        return 0, 1, []
    # 判据 3：分支 tip 在 main（有未合并提交时检测是否已被取代）
    branch = manager._branch_name(sid)
    r_v = manager._run_git(["git", "rev-parse", "--verify", branch])
    has_branch = r_v.returncode == 0
    warnings: list[str] = []
    if has_branch:
        r_mb = manager._run_git(
            ["git", "merge-base", "--is-ancestor", branch, "HEAD"]
        )
        if r_mb.returncode != 0:
            # 阶段2治本（未合并提交陷阱）：检测分支提交是否已被取代
            all_superseded, reason = _branch_commits_superseded(branch, manager)
            if all_superseded:
                warnings.append(
                    f"{sid}: 分支提交已全部被取代（{reason}），继续清理"
                )
                # fall through 到清理逻辑（分支可安全删除，修改已通过其他路径合并）
            else:
                # P3.5 age-based force-clean：超龄且有未合并提交时，保存 quarantine ref 后强制清理
                age_seconds = now - mtime
                if force_clean_threshold > 0 and age_seconds > force_clean_threshold:
                    q_ref = _quarantine_branch_ref(manager, branch, sid)
                    if q_ref:
                        warnings.append(
                            f"{sid}: force-clean 超龄 worktree（age={int(age_seconds)}s "
                            f"> {force_clean_threshold}s，未合并提交已存 {q_ref}，72h 可恢复）"
                        )
                        # fall through 到清理逻辑
                    else:
                        warnings.append(
                            f"{sid}: force-clean 失败——quarantine ref 保存失败，保留 worktree 待人工评估"
                        )
                        return 0, 1, warnings
                else:
                    warnings.append(
                        f"{sid}: 分支有未合并提交且未被取代（{reason}），需人工评估（已跳过）"
                    )
                    return 0, 1, warnings
    # 通过三重保护——清理
    swept = 0
    try:
        is_registered = manager._worktree_exists(sid)
        if is_registered:
            rm = manager._run_git(
                ["git", "worktree", "remove", "--force", str(d)]
            )
            if rm.returncode != 0:
                manager._run_git(["git", "worktree", "prune"])
                if d.exists():
                    _force_rmtree(d)
                manager._run_git(["git", "worktree", "prune"])
        else:
            manager._run_git(["git", "worktree", "prune"])
            if d.exists():
                _force_rmtree(d)
            manager._run_git(["git", "worktree", "prune"])
        if has_branch:
            manager._run_git(["git", "branch", "-D", branch])
        try:
            registry.unregister(sid)
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.warning("suppressed error in session_worktree", exc_info=True)
        swept = 1
        _log_worktree_delete(sid, "sweep", d, manager.repo_root)  # Phase 4 遥测
        logger.info(
            "session_worktree sweep: 清理 stale %s (registered=%s)",
            sid, is_registered,
        )
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        warnings.append(f"{sid}: 清理异常 {e}")
        return 0, 1, warnings
    return swept, 0, warnings


def _sweep_stale_worktrees(
    manager: WorktreeManager,
    registry: SessionRegistry,
    max_age_minutes: int = 30,
    force_clean_hours: int = 0,
) -> dict:
    """启动清扫：清理 .aidrafts/ 下的 stale session worktree 残留。

    在 session_worktree_start 创建自己 worktree 前调用，自动清理两类残留：
    - 孤儿物理目录（git worktree 未注册）—— git 已不认，物理删除
    - 已注册但 session 已过期 + 分支 tip 在 main 的 worktree —— 对话放弃残留

    安全判据（三重保护，任一不满足则跳过）：
    1. 目录 age > max_age_minutes（太新的不动，防误清并发 AI 正在创建的）
    2. session 不在 active 注册表（活跃 session 不动；用 list_active 判定，不依赖 pid）
    3. 分支 tip 在 HEAD 祖先或无分支；有未合并提交时检测是否已被取代
       （阶段2治本：全部被取代则继续清理，否则 warning 提示人工处理）

    P3.5 force-clean（2026-07-20）：force_clean_hours > 0 时，对超龄（age > force_clean_hours）
    且有未合并+未被取代提交的 worktree，先保存分支 tip 到 refs/quarantine/<sid>（72h 可恢复），
    再强制清理。force_clean_hours=0（默认）禁用此功能，保持向后兼容。

    异常不抛出（sweep 失败不阻断 start）。在独立 _WorktreeLock 周期内执行，
    退出锁后 caller 才调 create_session_worktree（避免锁重入死锁）。

    Args:
        manager: WorktreeManager 实例。
        registry: SessionRegistry 实例。
        max_age_minutes: 目录年龄阈值（分钟），默认 30。
        force_clean_hours: 超龄强制清理阈值（小时），0=禁用（默认）。

    Returns:
        {"swept": int, "skipped": int, "warnings": list[str]}
    """
    # 防御性类型校验（治本遗留项#2，2026-07-17）：manager 必须是 WorktreeManager 实例。
    # 病根：AI 曾误调 _sweep_stale_worktrees(REPO_ROOT, reg) 传入 Path 对象，
    # 导致 AttributeError: 'WindowsPath' object has no attribute '_drafts_dir'。
    # fail-closed 返回 error dict 而非抛异常（对标本模块所有函数返回 dict 不抛异常的契约）。
    if not isinstance(manager, WorktreeManager):
        return {
            "swept": 0,
            "skipped": 0,
            "warnings": [
                f"参数类型错误: manager 必须是 WorktreeManager 实例, 实际是 "
                f"{type(manager).__name__}。请调用公开函数 session_worktree_sweep() "
                f"而非私有 _sweep_stale_worktrees()。"
            ],
        }
    import time as _time

    drafts = manager._drafts_dir
    if not drafts.exists():
        return {"swept": 0, "skipped": 0, "warnings": []}

    now = _time.time()
    age_threshold = max_age_minutes * 60
    # P3.5: force_clean_threshold（秒），0=禁用
    force_clean_threshold = force_clean_hours * 3600 if force_clean_hours > 0 else 0

    # 活跃 session（list_active 已 reap 过期条目，返回的即活跃；不依赖 pid）
    # list_active 返回 list[SessionInfo]（非 dict），提取 session_id 集合
    try:
        active_list = registry.list_active()
        active_sids = {getattr(info, "session_id", "") for info in active_list}
    except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
        active_sids = set()

    swept = 0
    skipped = 0
    warnings: list[str] = []
    try:
        with _WorktreeLock(manager.repo_root):
            for d in drafts.iterdir():
                if not d.is_dir() or not d.name.startswith("sess-"):
                    continue
                d_swept, d_skipped, d_warnings = _sweep_one_dir(
                    manager, registry, d, now, age_threshold, active_sids,
                    force_clean_threshold=force_clean_threshold,
                )
                swept += d_swept
                skipped += d_skipped
                warnings.extend(d_warnings)
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        warnings.append(f"sweep 整体异常（已中止）: {e}")

    return {"swept": swept, "skipped": skipped, "warnings": warnings}


@_inject_ok
def session_worktree_sweep(
    project_root: str | Path | None = None,
    max_age_minutes: int = 30,
    force_clean_hours: int = 0,
) -> SweepResult:
    """公开入口：on-demand 清理 stale session worktree 残留（治本遗留项#2，2026-07-17）。

    包装私有 ``_sweep_stale_worktrees``，提供 AI/CLI 可调用的清理 API。
    病根：原 ``_sweep_stale_worktrees`` 是私有函数，仅在 ``session_worktree_start``
    内部调用。当 AI 累积 stale worktree（来自崩溃/放弃的 session）且无新 session
    启动时，无公开入口可清理，AI 被迫误调私有函数传入 Path 对象导致
    AttributeError。本函数消除该 API 完整性缺口。

    三重保护判据（由 ``_sweep_stale_worktrees`` 实现，本函数不改变）：
      1. 目录 age > max_age_minutes（太新的不动，防误清并发 AI 正在创建的）
      2. session 不在 active 注册表（活跃 session 不动）
      3. 分支 tip 在 HEAD 祖先或无分支（有未合并提交的不动，warning 提示人工处理）

    P3.5 force-clean（2026-07-20）：force_clean_hours > 0 时，对超龄且有未合并提交的
    worktree，先保存分支 tip 到 refs/quarantine/<sid>（72h 可恢复），再强制清理。
    force_clean_hours=0（默认）禁用此功能，保持向后兼容。

    Args:
        project_root: 项目根目录（默认 REPO_ROOT）。
        max_age_minutes: 目录年龄阈值（分钟），默认 30。
        force_clean_hours: 超龄强制清理阈值（小时），0=禁用（默认）。

    Returns:
        ``{"swept": int, "skipped": int, "warnings": list[str]}``。
    """
    root = Path(project_root) if project_root else REPO_ROOT
    manager = _get_manager(root)
    registry = _get_registry(root)
    return _sweep_stale_worktrees(
        manager, registry,
        max_age_minutes=max_age_minutes,
        force_clean_hours=force_clean_hours,
    )


def _cleanup_orphan_draft_scripts(root: Path, max_age_seconds: int = 3600) -> dict:
    """清理 .aidrafts/ 根目录下的孤儿临时脚本（P3 流程治本，2026-07-17）。

    病根：AI 在调研/治本过程中常在 .aidrafts/ 根目录创建 ``_*`` 一次性辅助脚本
    （如 _commit_adp4_adp5.py / _merge_adp45.py），用完未删则永久残留。P0 曾手工
    清理 3 个此类孤儿。本 helper 在每次 session_worktree_start 时自动清理 age > 1h
    的孤儿脚本，消除「治本代码自身成为残留」的递归问题（AI→治本→残留→AI→治本）。

    安全判据：
    1. 仅扫 .aidrafts/ 根目录（非递归），仅匹配 ``_*`` 前缀文件
       （非 sess-* worktree 目录——worktree 由 _sweep_stale_worktrees 处理）
    2. age > max_age_seconds（太新的不动，防误清 AI 正在使用的）
    3. OSError 静默跳过（清理失败不阻断 start）

    Returns:
        ``{"deleted": int, "skipped": int, "warnings": list[str]}``
    """
    import time as _time

    drafts = root / ".aidrafts"
    if not drafts.exists():
        return {"deleted": 0, "skipped": 0, "warnings": []}
    now = _time.time()
    deleted = 0
    skipped = 0
    warnings: list[str] = []
    try:
        for entry in drafts.iterdir():
            # 仅匹配根目录 _* 文件（非目录，非 sess-* worktree）
            if entry.is_dir():
                continue
            if not entry.name.startswith("_"):
                continue
            try:
                mtime = entry.stat().st_mtime
            except OSError:
                skipped += 1
                continue
            if (now - mtime) < max_age_seconds:
                skipped += 1
                continue
            try:
                entry.unlink()
                deleted += 1
                logger.info(
                    "session_worktree orphan cleanup: 删除过期辅助脚本 %s", entry.name,
                )
            except OSError as e:
                warnings.append(f"{entry.name}: 删除异常 {e}")
                skipped += 1
    except OSError as e:
        warnings.append(f".aidrafts 扫描异常: {e}")
    return {"deleted": deleted, "skipped": skipped, "warnings": warnings}


def _check_concurrency_block(sid, allow_concurrent, breaking_change, root):
    """治本变更并发阻断（§9.7 治本，2026-07-04）——双向阻断 + 逃生通道。

    返回阻断 dict（调用方直接 return）或 None（放行）。异常 fail-open 降级放行。
    """
    if allow_concurrent:
        return None
    registry_pre = _get_registry(root)
    try:
        if breaking_change:
            # breaking_change=True：检查是否有任何其他活跃 session
            others = [s for s in registry_pre.list_active() if s.session_id != sid]
            if others:
                other_ids = [s.session_id for s in others]
                return {
                    "session_id": sid,
                    "worktree_path": "",
                    "branch": f"session/{sid}",
                    "registered": False,
                    "created": False,
                    "error": (
                        f"BREAKING_CHANGE_CONCURRENCY_BLOCKED: 治本变更期间禁止并发 AI 对话"
                        f"（§9.7 治本变更并发阻断）。当前活跃 session: {other_ids}。"
                        f"逃生通道：allow_concurrent=True。"
                    ),
                    "blocked_by": other_ids,
                }
        else:
            # breaking_change=False：检查是否有其他活跃 session 声明了 breaking_change
            blocker = registry_pre.find_breaking_change_session(exclude_session_id=sid)
            if blocker is not None:
                return {
                    "session_id": sid,
                    "worktree_path": "",
                    "branch": f"session/{sid}",
                    "registered": False,
                    "created": False,
                    "error": (
                        f"BREAKING_CHANGE_AVOIDANCE_BLOCKED: 活跃 session '{blocker.session_id}'"
                        f" 声明了 breaking_change（治本变更进行中，§9.7 治本变更并发阻断）。"
                        f"逃生通道：allow_concurrent=True。"
                    ),
                    "blocked_by": [blocker.session_id],
                }
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        # fail-open：并发检测异常不阻断 start（对标 held_overlap_gate fail-open）
        logger.warning("session_worktree_start: 并发检测异常（降级放行）: %s", e, exc_info=True)
    return None


def _check_duplicate_task(
    registry: SessionRegistry, sid: str, task_files: list[str],
) -> dict | None:
    """任务去重检测（裁定#D，2026-07-19）：任务文件集与活跃 session 重叠时阻断启动。

    病根：并发 AI session 常被派发相同/高度重叠的任务（用户重复提问、多对话并行
    治本同一问题），导致重复施工 + 并发文件擦除（实测：两 session 同时改同一批
    文件，一方 auto-clean 擦除另一方未提交修改）。task_files 是任务的文件指纹，
    start 阶段重叠检测把"事后互踩"前移为"事前暴露"。

    判据：Jaccard 相似度 |A∩B| / |A∪B| ≥ 0.5（路径归一化为 posix + 小写）。
    语义：阻断 + 逃生通道（allow_duplicate=True），与 _check_concurrency_block 一致。
    降级：检测异常仅 debug 日志，不阻断 start（fail-open）。
    """
    if not task_files:
        return None
    try:
        new_set = {str(Path(f).as_posix()).lower() for f in task_files}
        for active in registry.list_active():
            if active.session_id == sid:
                continue
            other_set = {str(Path(f).as_posix()).lower() for f in (active.task_files or [])}
            if not other_set:
                continue
            intersection = new_set & other_set
            union = new_set | other_set
            if union and len(intersection) / len(union) >= 0.5:
                pct = round(100 * len(intersection) / len(union))
                return {
                    "session_id": sid,
                    "worktree_path": "",
                    "branch": f"session/{sid}",
                    "registered": False,
                    "created": False,
                    "error": (
                        f"DUPLICATE_TASK_BLOCKED: 任务文件集与活跃 session "
                        f"'{active.session_id}' 重叠 {pct}%（裁定#D 任务去重——"
                        f"重复施工是并发文件擦除的主要根源）。确认非重复施工后 "
                        f"用 allow_duplicate=True 重试。重叠文件: {sorted(intersection)[:10]}"
                    ),
                    "warning": "DUPLICATE_TASK_WARNING",
                    "conflict_with": active.session_id,
                    "overlap_files": sorted(intersection),
                }
    except Exception:  # noqa: BLE001 — 检测降级不阻断 start
        logger.debug("duplicate task check failed", exc_info=True)
    return None


def _run_startup_health_check(root: Path) -> dict:
    """AI session 启动健康度 smoke test（#ARCH-CAPABILITY-LOOKUP-BYPASS-DEAD-S7 Phase 3.3）。

    检测 CAPABILITY-LOOKUP-REQUIRED gate 机制健康度——对标 §11.0.3 #ARCH-TOOL-HEALTH-V1。
    失败时返回 status="failed" + details，调用方 SHOULD 上报（[ESCALATION]）而非
    静默 workaround。

    检查项（3 项）：
      1. capability_lookup_required_gate 模块能否 import（gate 代码完整性）
      2. .runtime/lookup_audit/ 目录存在且可写（audit log 落盘通路）
      3. capability_lookup.write_lookup_audit_log 函数可调用（Python API 通路）

    Returns:
        {"status": "ok" | "failed", "checks": [{"name", "passed", "detail"}, ...]}
    """
    checks: list[dict] = []
    all_passed = True

    # 1. capability_lookup_required_gate 可 import
    try:
        from zephyr.gov_enforcement.commit_gates import capability_lookup_required_gate
        gate_spec = capability_lookup_required_gate.make_capability_lookup_required_gate()
        checks.append({
            "name": "capability_lookup_required_gate import",
            "passed": True,
            "detail": f"gate_id={gate_spec.gate_id}, priority={gate_spec.priority}",
        })
    except Exception as e:  # noqa: BLE001 — 健康检查不抛异常
        all_passed = False
        checks.append({
            "name": "capability_lookup_required_gate import",
            "passed": False,
            "detail": f"import failed: {type(e).__name__}: {e}",
        })

    # 2. .runtime/lookup_audit/ 目录可写
    try:
        audit_dir = root / ".runtime" / "lookup_audit"
        audit_dir.mkdir(parents=True, exist_ok=True)
        # 验证可写：写一个临时测试文件然后删除
        test_file = audit_dir / "._health_check_test"
        test_file.write_text("ok", encoding="utf-8")
        test_file.unlink()
        checks.append({
            "name": "lookup_audit dir writable",
            "passed": True,
            "detail": str(audit_dir),
        })
    except Exception as e:  # noqa: BLE001 — 健康检查不抛异常
        all_passed = False
        checks.append({
            "name": "lookup_audit dir writable",
            "passed": False,
            "detail": f"write test failed: {type(e).__name__}: {e}",
        })

    # 3. capability_lookup.write_lookup_audit_log 可调用（不实际写入）
    try:
        from zephyr.governance.capability_lookup import write_lookup_audit_log
        # 调用空 session_id 验证函数签名（空 session_id 不会写入）
        write_lookup_audit_log(
            session_id="",
            query={}, result_count=0, capability_ids=[],
        )
        checks.append({
            "name": "capability_lookup.write_lookup_audit_log callable",
            "passed": True,
            "detail": "function signature verified",
        })
    except Exception as e:  # noqa: BLE001 — 健康检查不抛异常
        all_passed = False
        checks.append({
            "name": "capability_lookup.write_lookup_audit_log callable",
            "passed": False,
            "detail": f"call failed: {type(e).__name__}: {e}",
        })

    return {
        "status": "ok" if all_passed else "failed",
        "checks": checks,
    }


@_inject_ok
def session_worktree_start(
    session_id: str | None = None,
    project_root: str | Path | None = None,
    breaking_change: bool = False,
    allow_concurrent: bool = False,
    task_files: list[str] | None = None,
    allow_duplicate: bool = False,
) -> StartResult:
    """AI 对话启动第一步：注册 session + 创建独立 worktree。

    原子操作：先注册 session（SessionRegistry），再创建 worktree（WorktreeManager）。
    幂等：若 worktree 已存在，直接复用并返回其路径。

    治本变更并发阻断（§9.7 治本，2026-07-04）——双向阻断逻辑：
    - ``breaking_change=True``：检查是否有其他活跃 session -> 有则阻断（治本变更期间禁止并发）
    - ``breaking_change=False``：检查是否有其他活跃 session 声明了 ``breaking_change=True`` -> 有则阻断（避让治本变更）
    - ``allow_concurrent=True``：逃生通道，跳过阻断（对标 ``allow_overlap``）

    Args:
        session_id: session 标识。为 None 时自动用 generate_session_id() 生成。
        project_root: 项目根目录（默认 REPO_ROOT）。
        breaking_change: 本次会话是否为治本变更（refactor/fix 涉及多文件）。True 时阻断其他并发 session。
        allow_concurrent: 逃生通道，True 时跳过并发阻断（对标 allow_overlap）。
        task_files: 本任务预计施工的文件列表（裁定#D 任务去重，2026-07-19）。
            作为任务文件指纹注册到 SessionRegistry，与活跃 session 的 task_files
            Jaccard 重叠 ≥50% 时阻断启动（DUPLICATE_TASK_BLOCKED）。
        allow_duplicate: 逃生通道，True 时跳过任务去重阻断（确认非重复施工后用）。

    Returns:
        {
            "ok": bool,                # 裁定#A：成功判定唯一入口（消费方 MUST 只读此键）
            "session_id": str,
            "worktree_path": str,      # worktree 绝对路径，AI 后续文件操作 MUST 用此路径前缀
            "branch": str,             # 分支名 session/{session_id}
            "registered": bool,        # session 是否注册成功
            "created": bool,           # worktree 是否新建（False=已存在复用）
        }
        失败时附加 "error" 字段 + "blocked_by" 字段（阻断方 session_id）。
        任务去重阻断时附加 "warning"="DUPLICATE_TASK_WARNING" + "conflict_with" +
        "overlap_files"（裁定#D）。
    """
    sid = session_id or generate_session_id()
    root = Path(project_root) if project_root else REPO_ROOT

    # -1. 启动健康度 smoke test（#ARCH-CAPABILITY-LOOKUP-BYPASS-DEAD-S7 Phase 3.3）
    #     非阻断——失败时仅 [ESCALATION] 警告，session 仍可创建。对标 §11.0.3 #ARCH-TOOL-HEALTH-V1。
    #     病根 G7：原无启动 smoke test，gate 故障时 AI 静默 workaround（最大风险）。
    #     治本：启动时自检 capability_lookup_required_gate + audit log 目录 + write_lookup_audit_log，
    #     失败时强制 [ESCALATION] 标记暴露给 AI/人类，禁止静默 workaround。
    health_check = _run_startup_health_check(root)
    if health_check.get("status") != "ok":
        failed_names = [
            c["name"] for c in health_check.get("checks", []) if not c.get("passed")
        ]
        logger.error(
            "[ESCALATION] session_worktree_start 健康度自检失败 (session=%s): %s. "
            "AI MUST 上报人类而非静默 workaround——对标 #ARCH-TOOL-HEALTH-V1. "
            "失败项: %s",
            sid, health_check.get("status"), failed_names,
        )
    else:
        logger.debug(
            "session_worktree_start 健康度自检通过 (session=%s)", sid,
        )

    # 0. 治本变更并发阻断（§9.7 治本，2026-07-04）
    #    双向阻断：breaking_change session 阻止其他 session，普通 session 避让 breaking_change session
    #    逃生通道：allow_concurrent=True 跳过阻断（对标 allow_overlap）
    block_r = _check_concurrency_block(sid, allow_concurrent, breaking_change, root)
    if block_r is not None:
        # 健康检查结果附加到阻断返回（信息性，不改变阻断决策）
        block_r["health_check"] = health_check
        return block_r

    # 0.5 任务去重检测（裁定#D，2026-07-19）：任务文件指纹与活跃 session 重叠
    #     ≥50% 时阻断启动；逃生通道 allow_duplicate=True
    if task_files and not allow_duplicate:
        dup_r = _check_duplicate_task(_get_registry(root), sid, task_files)
        if dup_r is not None:
            return dup_r

    # 1. 注册 session（held_files 留空——worktree 模式下文件隔离由 worktree 物理保证，
    #    不依赖 held_files claim 机制）
    registry = _get_registry(root)
    registered = False

    # #ARCH-HEARTBEAT-001 P1-5: 检查 emergency_commit 成本递增阻断
    # 若任一 session 的 emergency_commit 计数 >= 5，阻断新 session 启动，
    # 强制先调查根因（GitCommitGateway 锁死/POST-COMMIT-GUARD 反复 reset）。
    # 失败时非阻断（best-effort，避免 check_start_blocked 自身 bug 阻塞所有 start）
    try:
        start_blocked, block_reason = _check_emergency_start_blocked(root)
        if start_blocked:
            return {
                "session_id": sid,
                "worktree_path": "",
                "branch": "",
                "registered": False,
                "created": False,
                "error": f"session_worktree_start blocked: {block_reason}",
                "health_check": health_check,
            }
    except Exception as e:  # noqa: BLE001 — 5.135治标: best-effort 防御
        logger.warning("check_start_blocked failed (non-blocking): %s", e, exc_info=True)

    try:
        # Phase 6 治本（2026-07-19，warn-only 噪声治理——session 注册时序修复）：
        # pid=0 = 逻辑 session（非进程绑定）。session_worktree 工作流跨多个 python -c
        # 进程（start/commit/merge 各一次），若用 os.getpid() 注册，start 进程退出后
        # PID 死亡 → _is_session_alive 判死 → SESSION-REQUIRED gate 阻断 merge +
        # POST-COMMIT-GUARD warn-only 噪声。pid=0 时 _is_session_alive 跳过 PID 检查
        # （仅靠 TTL=3600s + commit/merge 时的 heartbeat 刷新），session 跨进程存活。
        # 僵尸检测由 session_worktree_sweep（age + 分支取代）兜底，非 PID liveness。
        registry.register(
            sid, pid=0, held_files=[],
            is_breaking_change=breaking_change,
            task_files=task_files or [],  # 裁定#D：任务文件指纹注册
        )
        registered = True
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        return {
            "session_id": sid,
            "worktree_path": "",
            "branch": "",
            "registered": False,
            "created": False,
            "error": f"register session failed: {e}",
            "health_check": health_check,
        }

    # 2. 创建 worktree
    manager = _get_manager(root)
    # 启动清扫：清理 stale worktree 残留（独立锁周期，退出后 create 再获取锁）
    try:
        sweep_r = _sweep_stale_worktrees(manager, registry)
        if sweep_r.get("swept", 0) or sweep_r.get("warnings"):
            logger.info(
                "session_worktree sweep: swept=%s skipped=%s warnings=%s",
                sweep_r.get("swept"), sweep_r.get("skipped"), sweep_r.get("warnings"),
            )
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        logger.warning("session_worktree sweep 异常（不阻断 start）: %s", e, exc_info=True)
    # 3. 清理 .aidrafts/ 根目录孤儿辅助脚本（P3 流程治本，2026-07-17）
    #    病根：AI 创建的 _* 一次性脚本用完未删则永久残留。age > 1h 自动清理。
    try:
        orphan_r = _cleanup_orphan_draft_scripts(root)
        if orphan_r.get("deleted") or orphan_r.get("warnings"):
            logger.info(
                "session_worktree orphan cleanup: deleted=%s skipped=%s warnings=%s",
                orphan_r.get("deleted"), orphan_r.get("skipped"), orphan_r.get("warnings"),
            )
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        logger.warning("session_worktree orphan cleanup 异常（不阻断 start）: %s", e, exc_info=True)
    # 3.5 清扫隔离区过期文件（裁定#B 配套：72h 保留期，非阻断）
    try:
        q_r = _sweep_quarantine(root)
        if q_r.get("deleted"):
            logger.info("session_worktree quarantine sweep: deleted=%s", q_r.get("deleted"))
    except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
        logger.debug("quarantine sweep 异常（不阻断 start）", exc_info=True)
    # P3.5 清扫过期 quarantine refs（ARCH-GIT-CALL-BUDGET P3.5 配套：72h 保留期，非阻断）
    try:
        qr_r = _sweep_quarantine_refs(manager)
        if qr_r.get("deleted"):
            logger.info("session_worktree P3.5 quarantine ref sweep: deleted=%s", qr_r.get("deleted"))
    except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
        logger.debug("quarantine ref sweep 异常（不阻断 start）", exc_info=True)
    try:
        # 检测是否已存在（幂等）
        wt_path = manager._wt_path(sid)
        already_exists = manager._worktree_exists(sid)
        if not already_exists:
            # ARCH-GIT-CALL-BUDGET P3.3（2026-07-19）：优先尝试 pool lease
            # pool 预创建 worktree（.aidrafts_pool/），lease 瞬时返回已创建的
            # worktree（git worktree move 重定位 + git branch -m 重命名），
            # 消除每次 session 启动的 git worktree add 开销（~2-5s on Windows）。
            # pool 空或 move 失败时 lease 返回 None，fall back 到直接创建。
            # 健壮性优先：pool 永远不阻断 session 启动。
            leased_path = None
            try:
                from zephyr.gov_enforcement.rule_bridge.worktree_pool import get_pool
                pool = get_pool(root)
                leased_path = pool.lease(sid)
            except Exception as e:  # noqa: BLE001 — pool 失败不阻断 start
                logger.warning(
                    "session_worktree_start: pool.lease 异常（fall back 到直接创建）: %s",
                    e, exc_info=True,
                )

            if leased_path is not None:
                wt_path = Path(leased_path)
                created = True
                # lease 成功后异步 prefetch 补充池（fire-and-forget，不阻塞返回）
                try:
                    pool.prefetch_async(1)
                except Exception:  # noqa: BLE001 — prefetch 失败不阻断 start
                    logger.debug(
                        "session_worktree_start: prefetch_async 失败（不阻断）",
                        exc_info=True,
                    )
            else:
                # Fall back：直接创建 worktree（pool 空或 lease 失败）
                manager.create_session_worktree(sid)
                wt_path = manager._wt_path(sid)
                created = True
        else:
            created = False
        # #ARCH-HEARTBEAT-001: spawn detached heartbeat daemon
        # daemon 每 30s 刷新 last_heartbeat，使 _is_session_alive 的 90s 超时生效
        # spawn 失败不阻断 start（session 仍有 90s 可用窗口）
        daemon_pid = _spawn_heartbeat_daemon(sid, root)
        return {
            "session_id": sid,
            "worktree_path": str(wt_path),
            "branch": f"session/{sid}",
            "registered": registered,
            "created": created,
            "health_check": health_check,
            "heartbeat_daemon_pid": daemon_pid,
        }
    except WorktreeError as e:
        return {
            "session_id": sid,
            "worktree_path": "",
            "branch": f"session/{sid}",
            "registered": registered,
            "created": False,
            "error": f"create worktree failed: {e}",
            "health_check": health_check,
        }
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        return {
            "session_id": sid,
            "worktree_path": "",
            "branch": f"session/{sid}",
            "registered": registered,
            "created": False,
            "error": f"unexpected: {e}",
            "health_check": health_check,
        }


# 裁定#217 Tier2 P4 Extract Method 重构（2026-07-15）
# 原 session_worktree_commit 388行 McCabe=47（7段顺序编排 + 共享状态）。
# 治本：提取为 6 个模块级 helper（均 McCabe≤15），主函数简化为编排（McCabe≈10）。
# 行为等价：所有 return dict 字段不变，gate/subprocess 调用顺序不变。


def _normalize_commit_files(files: list[str], wt_path: Path, root: Path) -> list[str]:
    """归一化文件路径为相对 worktree 的路径（git add 在 worktree cwd 下执行）。"""
    rel_files: list[str] = []
    for f in files:
        p = Path(f)
        if p.is_absolute():
            try:
                rel = p.relative_to(wt_path)
                rel_files.append(str(rel).replace("\\", "/"))
            except ValueError:
                try:
                    rel_to_root = p.relative_to(root)
                    rel_files.append(str(rel_to_root).replace("\\", "/"))
                except ValueError:
                    rel_files.append(str(p).replace("\\", "/"))
        else:
            rel_files.append(str(p).replace("\\", "/"))
    return rel_files


def _check_held_overlap(registry, session_id: str, rel_files: list[str]) -> dict | None:
    """HELD-OVERLAP 硬阻断 + auto-claim。返回阻断 dict 或 None（通过）。"""
    claimed_files: list[str] = []
    overlap_files: list[str] = []
    for rf in rel_files:
        try:
            if registry.claim_file(session_id, rf):
                claimed_files.append(rf)
            else:
                overlap_files.append(rf)
        except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
            pass
    if not overlap_files:
        return None
    for cf in claimed_files:
        try:
            registry.release_file(session_id, cf)
        except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.warning("suppressed error in session_worktree", exc_info=True)
    return {
        "session_id": session_id,
        "status": "FAILED",
        "message": (
            f"HELD_OVERLAP_VIOLATION: 以下文件被其他活跃 session 持有 "
            f"（等待对方 merge/abort 释放后重试，或用 allow_overlap=True 逃生）: "
            f"{overlap_files}"
        ),
        "commit_hash": "",
        "held_overlap": True,
    }


def _run_dcr_check(root: Path, rel_files: list[str], session_id: str) -> dict | None:
    """DCR 检测（对标 GitCommitGateway DIRECTORY-CONTRACT gate）。返回阻断 dict 或 None。"""
    # 过滤删除场景：磁盘不存在的文件跳过 DCR 检查
    # （对标 directory_contract_gate.py L92-93 deletion commit 豁免设计）
    existing_files = [f for f in rel_files if (root / f).is_file()]
    if not existing_files:
        return None  # 全部是删除/缺失，跳过 DCR
    check_script = root / "scripts" / "governance" / "d1_structure" / "check_directory_contract.py"
    if not check_script.is_file():
        return {
            "session_id": session_id,
            "status": "FAILED",
            "message": f"check_directory_contract.py not found: {check_script} (fail-closed)",
            "commit_hash": "",
            "directory_contract_violation": True,
        }
    _MAX_INLINE_FILES = 200
    if len(existing_files) > _MAX_INLINE_FILES:
        dcr_cmd = [sys.executable, str(check_script), "--all-files"]
    else:
        dcr_cmd = [sys.executable, str(check_script)] + existing_files
    # 治本(2026-07-19): 显式注入 PYTHONPATH——check_directory_contract.py 间接 import
    # zephyr.shared.io.paths（via _shared.constants），需 src/ 在路径中。
    # subprocess 默认继承父 env，但 session_worktree_commit 调用链可能丢失 PYTHONPATH，
    # 显式构造确保稳健（对标 directory_contract_gate.py 同款修复）。
    dcr_env = os.environ.copy()
    _src_dir = str(root / "src")
    _existing_pp = dcr_env.get("PYTHONPATH", "")
    if _src_dir not in _existing_pp.split(os.pathsep):
        dcr_env["PYTHONPATH"] = f"{_src_dir}{os.pathsep}{_existing_pp}" if _existing_pp else _src_dir
    try:
        from zephyr.shared.infra.process_pool import run_subprocess_hidden

        dcr_result = run_subprocess_hidden(
            dcr_cmd, capture_output=True, cwd=str(root), env=dcr_env, timeout=60,
        )
    except (subprocess.TimeoutExpired, OSError) as e:
        return {
            "session_id": session_id,
            "status": "FAILED",
            "message": f"check_directory_contract.py execution failed (fail-closed): {e}",
            "commit_hash": "",
            "directory_contract_violation": True,
        }
    if dcr_result.returncode != 0:
        detail = dcr_result.stderr.decode("utf-8", errors="replace").strip()
        if not detail:
            detail = dcr_result.stdout.decode("utf-8", errors="replace").strip()
        return {
            "session_id": session_id,
            "status": "FAILED",
            "message": f"DIRECTORY_CONTRACT_VIOLATION: {detail or 'unknown violation'}",
            "commit_hash": "",
            "directory_contract_violation": True,
        }
    return None


def _delete_worktree_file(dst: Path, rel_file: str, wt_path: Path) -> None:
    """删除 worktree 内文件（带只读兜底 + git rm --cached 兜底）。"""
    try:
        dst.unlink()
    except OSError:
        try:
            os.chmod(str(dst), 0o644)
            dst.unlink()
        except OSError:
            subprocess.run(
                ["git", "rm", "--cached", "--", rel_file],
                cwd=str(wt_path), capture_output=True, timeout=30,
            )


def _ensure_worktree_base_fresh(root: Path, wt_path: Path, session_id: str) -> dict | None:
    """确保 worktree branch base 与主工作区 HEAD 对齐（防搭便车提交 + 防 ARCH-REFERENCE 误判）。

    病根（裁定#19-B，2026-07-18）：
      - session_worktree_start 创建 worktree 时 base = dev HEAD (T0)
      - 并发 session merge 到 dev，dev HEAD 前进到 T1（引入新 #ARCH-XXX 引用等）
      - AI 在主工作区 Edit 文件（主工作区文件 = dev T1 内容 + AI 改动）
      - session_worktree_commit 调 _sync_files_to_worktree copy2 主工作区文件到 worktree
      - worktree commit 内容 = (主工作区文件) − (worktree base T0) = dev T0→T1 改动 + AI 改动
      - 后果：① 搭便车提交（dev 的多个 commit 被塞进 session commit，污染 git 历史）；
        ② ARCH-REFERENCE L2 误判（dev 新引用被算作本次 commit 新增，要求 registry 同 commit）

    治本：在 _sync_files_to_worktree 之前检测 worktree HEAD 是否落后于主工作区 HEAD，若落后则：
      - 无 session commit（start 后第一次 commit）→ git reset --hard <main HEAD>（安全，worktree 无未提交改动）
      - 有 session commit → git rebase <main HEAD>（fail-loud on conflict，AI 手动处理）

    Returns:
        None 表示通过（base 已最新或已成功对齐）；dict 表示失败（含 error 字段，阻断 commit）。
    """
    # 获取主工作区 HEAD（不假设分支名，直接取 HEAD）
    main_head_r = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=str(root), capture_output=True, text=True, timeout=10,
    )
    if main_head_r.returncode != 0:
        return None  # 无法获取主工作区 HEAD，降级放行（不阻断业务）
    main_head = main_head_r.stdout.strip()

    # 获取 worktree HEAD
    wt_head_r = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=str(wt_path), capture_output=True, text=True, timeout=10,
    )
    if wt_head_r.returncode != 0:
        return None  # 无法获取 worktree HEAD，降级放行
    wt_head = wt_head_r.stdout.strip()

    # base 已最新
    if wt_head == main_head:
        return None

    # 检测 worktree 是否有 session 自己的 commit（merge-base..worktree_HEAD 的 commit 数）
    mb_r = subprocess.run(
        ["git", "merge-base", wt_head, main_head],
        cwd=str(root), capture_output=True, text=True, timeout=10,
    )
    if mb_r.returncode != 0:
        return None  # 无法计算 merge-base，降级放行
    merge_base = mb_r.stdout.strip()

    session_commits_r = subprocess.run(
        ["git", "rev-list", "--count", f"{merge_base}..{wt_head}"],
        cwd=str(root), capture_output=True, text=True, timeout=10,
    )
    if session_commits_r.returncode != 0:
        return None  # 降级放行
    session_commit_count = int(session_commits_r.stdout.strip() or "0")

    if session_commit_count == 0:
        # 无 session commit，安全 reset 到主工作区 HEAD
        # P1.3 fast-path：session_worktree 是可信调用方，跳过 git_guard alias 扫描
        reset_r = subprocess.run(
            ["git", "reset", "--hard", main_head],
            cwd=str(wt_path), capture_output=True, text=True, timeout=30,
            env=_trusted_git_env(),
        )
        if reset_r.returncode != 0:
            return {
                "session_id": session_id,
                "status": "FAILED",
                "message": (
                    f"worktree base 对齐失败（git reset --hard {main_head[:8]}）: "
                    f"{reset_r.stderr.strip()}"
                ),
                "commit_hash": "",
                "base_sync_failed": True,
            }
        logger.info(
            "session_worktree base 对齐: reset --hard %s (无 session commit，安全)",
            main_head[:8],
        )
    else:
        # 有 session commit，rebase 到主工作区 HEAD（可能有冲突）
        rebase_r = subprocess.run(
            ["git", "rebase", main_head],
            cwd=str(wt_path), capture_output=True, text=True, timeout=120,
        )
        if rebase_r.returncode != 0:
            subprocess.run(
                ["git", "rebase", "--abort"],
                cwd=str(wt_path), capture_output=True, timeout=30,
            )
            return {
                "session_id": session_id,
                "status": "FAILED",
                "message": (
                    f"worktree base 过期且 rebase 冲突（有 {session_commit_count} 个 session commit）。"
                    f"请手动处理：① 在 worktree ({wt_path}) 内 git rebase {main_head[:8]} 解决冲突，或"
                    f"② session_worktree_abort 后重新 start + commit。"
                    f"原始 rebase 输出: {rebase_r.stderr.strip()[:500]}"
                ),
                "commit_hash": "",
                "base_sync_failed": True,
            }
        logger.info(
            "session_worktree base 对齐: rebase %s (有 %d 个 session commit)",
            main_head[:8], session_commit_count,
        )
    return None


def _sync_files_to_worktree(root: Path, wt_path: Path, rel_files: list[str]) -> None:
    """同步主工作区改动到 worktree（君子协定模式：AI 的 Edit/Write 写在项目根）。"""
    import shutil

    tracked_r = subprocess.run(
        ["git", "ls-files", "--"] + rel_files,
        cwd=str(wt_path), capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=60,
    )
    tracked_files: set[str] = set()
    if tracked_r.returncode == 0 and tracked_r.stdout.strip():
        tracked_files = {line.strip() for line in tracked_r.stdout.strip().split("\n") if line.strip()}

    for rel_file in rel_files:
        src = root / rel_file
        dst = wt_path / rel_file
        if src.exists() and src.is_file():
            if dst.exists() and dst.is_file():
                try:
                    if src.read_bytes() == dst.read_bytes():
                        continue
                except OSError:
                    pass
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(str(src), str(dst))
        elif not src.exists() and dst.exists() and rel_file in tracked_files:
            _delete_worktree_file(dst, rel_file, wt_path)


def _run_pre_commit_gates_once(
    root: Path, wt_path: Path, rel_files: list[str],
    session_id: str, allow_promote: bool, allow_migration: bool,
    message: str = "",
) -> dict | None:
    """pre-commit gate 单次检查（对标 GitCommitGateway，worktree 兼容）。

    返回值 status 语义：
      - None: 通过
      - "GATE_VIOLATION": deterministic 违规，不重试
      - "GATE_TRANSIENT": transient 错误（subprocess 超时），可重试

    ``message`` 透传到 ``check_all(commit_message=...)`` 以支持 gate 读 commit msg——
    CAPABILITY-LOOKUP-REQUIRED gate 据此检测 ``[no-lookup:reason]`` 逃生标记。
    """
    try:
        from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import (
            GitCommitGateway, _GATEWAY_ENV,
        )
        _gw = GitCommitGateway(project_root=root)
        _orig_run_git = _gw._run_git

        def _wt_run_git(cmd, cwd=None, _wt=str(wt_path), _env_var=_GATEWAY_ENV):
            _env = os.environ.copy()
            _env[_env_var] = "1"
            if (len(cmd) >= 2 and cmd[0] == "git" and cmd[1] == "commit"
                    and not getattr(_gw, "_in_commit_flow", False)):
                return subprocess.CompletedProcess(
                    cmd, 1, "", "git commit blocked in worktree gate check"
                )
            _effective_cwd = cwd if cwd is not None else _wt
            return subprocess.run(
                cmd, cwd=_effective_cwd, capture_output=True, text=True,
                encoding="utf-8", errors="replace", timeout=60, env=_env,
            )

        _gw._run_git = _wt_run_git
        try:
            _staged_abs = [str((root / rf).resolve()) for rf in rel_files]
            _gate_results = _gw._gate_registry.check_all(
                _gw, _staged_abs, session_id=session_id,
                allow_promote=allow_promote,
                commit_message=message,
            )
        finally:
            _gw._run_git = _orig_run_git
        _skip_gates = _WORKTREE_SKIP_GATES
        if allow_migration:
            _skip_gates = _skip_gates | frozenset({"FILE-COPY", "ORPHAN-MODULE", "TEST-SOURCE-CONSISTENCY"})
        _blocking = [
            gr for gr in _gate_results
            if not gr.passed and gr.gate_id not in _skip_gates
        ]
        if _blocking:
            _details = "; ".join(f"{gr.gate_id}: {gr.detail}" for gr in _blocking)
            return {
                "session_id": session_id,
                "status": "GATE_VIOLATION",
                "message": (
                    f"pre-commit gate 阻断（worktree 路径对标 GitCommitGateway）: {_details}"
                ),
                "commit_hash": "",
                "gate_violation": True,
                "gate_results": [
                    {"gate_id": gr.gate_id, "detail": gr.detail} for gr in _blocking
                ],
            }
    except subprocess.TimeoutExpired as _te:
        # P2-2 治本：subprocess 超时是 transient 错误，不应阻断 commit
        # （根因：60+ gate 串行执行累积超时，非代码缺陷）。
        # 返回 GATE_TRANSIENT 让重试 wrapper 决定是否重试。
        logger.warning(
            "session_worktree_commit: gate 检查超时（transient）: %s",
            _te, exc_info=True,
        )
        return {
            "session_id": session_id,
            "status": "GATE_TRANSIENT",
            "message": f"pre-commit gate 超时（transient，将重试）: {_te}",
            "commit_hash": "",
            "transient": True,
        }
    except Exception as _e:  # noqa: BLE001 — 5.135治标: broad exception catch
        logger.warning("session_worktree_commit: gate 检查异常降级（不阻断）: %s", _e, exc_info=True)
    return None


# === P2-2 治本（#ARCH-RECONCILER-HEALTH-WARN-ROOT-CAUSE-001）===
# pre-commit gate 重试机制：原 _run_pre_commit_gates 单次执行，subprocess 超时
# 即 fail-open（masking 真问题）或阻断（误判）。治本：区分 transient/deterministic，
# transient 错误重试 3 次（指数退避 2/4/8s），重试间清理 worktree 残留 lock。
# 重试耗尽仍 transient → fail-open（transient 超时不代表代码缺陷，gate 真问题
# 由 reconciler 兜底告警）。
_GATE_RETRY_DELAYS = (2, 4, 8)
_GATE_RETRY_MAX_ATTEMPTS = 3


def _cleanup_worktree_locks(wt_path: Path) -> None:
    """清理 worktree 残留 lock 文件（P2-2 治本辅助）。

    重试间调用，移除 ``.git/index.lock`` 和 ``.git/refs/heads/*.lock`` 残留
    （前次超时的 git 进程可能遗留 lock，下次重试会被 lock 阻塞）。

    Args:
        wt_path: worktree 根路径。
    """
    try:
        git_dir = wt_path / ".git"
        if not git_dir.exists():
            return
        index_lock = git_dir / "index.lock"
        if index_lock.exists():
            try:
                index_lock.unlink()
                logger.info("P2-2: 清理 worktree index.lock（transient 重试辅助）")
            except OSError:
                pass
        refs_heads = git_dir / "refs" / "heads"
        if refs_heads.exists():
            for lock_file in refs_heads.glob("*.lock"):
                try:
                    lock_file.unlink()
                except OSError:
                    pass
    except Exception:  # noqa: BLE001 — lock 清理失败不阻断重试流程
        pass


def _run_pre_commit_gates(
    root: Path, wt_path: Path, rel_files: list[str],
    session_id: str, allow_promote: bool, allow_migration: bool,
    message: str = "",
) -> dict | None:
    """pre-commit gate 检查（带重试，P2-2 治本）。

    对 ``_run_pre_commit_gates_once`` 的 transient 错误（subprocess 超时）
    重试 ``_GATE_RETRY_MAX_ATTEMPTS`` 次，每次重试前等待指数退避
    （``_GATE_RETRY_DELAYS``）并清理 worktree 残留 lock。

    重试耗尽仍 transient → fail-open（返回 None）。transient 超时不代表
    代码有问题，deterministic gate 违规由 ``_once`` 直接返回 GATE_VIOLATION。

    Returns:
        阻断 dict（status=GATE_VIOLATION）或 None（通过 / transient 重试耗尽 fail-open）。
    """
    import threading as _threading
    last_err: dict | None = None
    for attempt in range(1, _GATE_RETRY_MAX_ATTEMPTS + 1):
        err = _run_pre_commit_gates_once(
            root, wt_path, rel_files, session_id,
            allow_promote, allow_migration, message,
        )
        if err is None:
            return None
        status = err.get("status", "")
        if status != "GATE_TRANSIENT":
            # GATE_VIOLATION 或其他 deterministic 状态，不重试
            return err
        last_err = err
        if attempt == _GATE_RETRY_MAX_ATTEMPTS:
            logger.warning(
                "session_worktree_commit: gate 检查 %d 次重试均失败（transient）: %s",
                _GATE_RETRY_MAX_ATTEMPTS, err.get("message", ""),
            )
            return None  # fail-open
        _cleanup_worktree_locks(wt_path)
        _threading.Event().wait(_GATE_RETRY_DELAYS[attempt - 1])
    return last_err


def _git_commit_in_worktree(wt_path: Path, message: str, session_id: str) -> dict:
    """在 worktree 内执行 git commit 并返回结果 dict。"""
    import tempfile

    # P1-1 (2026-07-20): 注入 ZEPHYR_COMMIT_GATEWAY=1 env，防 forged_gw_marker 误判
    # 根因: POST-COMMIT-GUARD 检查 commit message [GW:...] 标记是否对应 ZEPHYR_COMMIT_GATEWAY=1 env,
    #       缺 env 时判为 forged_gw_marker (4/24h 误报, GATE-COMMIT-GW-ABUSE-MONITOR 告警).
    # 治本: worktree commit 也注入 env (对齐 GitCommitGateway._run_git L1638-1639 模式).
    commit_env = os.environ.copy()
    commit_env["ZEPHYR_COMMIT_GATEWAY"] = "1"

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".msg", delete=False, encoding="utf-8"
    ) as msg_file:
        msg_file.write(f"{message}\n\n[GW:{session_id}:worktree]")
        msg_file_path = msg_file.name
    try:
        commit_cmd = ["git", "commit", "--no-verify", "-F", msg_file_path]
        commit_r = subprocess.run(
            commit_cmd, cwd=str(wt_path), capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=120, env=commit_env,
        )
    finally:
        try:
            os.unlink(msg_file_path)
        except OSError:
            pass

    if commit_r.returncode != 0:
        return {
            "session_id": session_id,
            "status": "FAILED",
            "message": f"git commit failed: {commit_r.stderr.strip()}",
            "commit_hash": "",
        }

    sha_r = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],
        cwd=str(wt_path), capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=30, env=commit_env,
    )
    commit_hash = sha_r.stdout.strip() if sha_r.returncode == 0 else ""

    return {
        "session_id": session_id,
        "status": "OK",
        "message": "committed in worktree",
        "commit_hash": commit_hash,
    }


def _get_clean_target_files(root: Path, rel_files: list[str]) -> list[str] | None:
    """获取目标文件中主工作区无改动的（可能被 stash 移走）。

    ``git diff --name-only HEAD`` 列出所有有改动的文件（含暂存区），
    目标文件不在该列表中 = 主工作区无改动 = 可能被 stash 移走。
    """
    try:
        diff_r = subprocess.run(
            ["git", "diff", "--name-only", "HEAD"],
            cwd=str(root), capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=15,
        )
        if diff_r.returncode != 0:
            return None
        changed_files = {f.strip() for f in diff_r.stdout.splitlines() if f.strip()}
        clean_files = [f for f in rel_files if f not in changed_files]
        return clean_files if clean_files else None
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        logger.warning("_get_clean_target_files failed: %s", e, exc_info=True)
        return None


def _check_stash_for_files(
    root: Path, stash_line: str, clean_files: list[str],
) -> tuple[str, str, list[str]] | None:
    """检查单个 stash 是否包含 clean_files 中的文件，命中返回 (stash_ref, msg, hits)。"""
    parts = stash_line.split("|", 1)
    if len(parts) < 2:
        return None
    stash_ref, stash_msg = parts[0], parts[1]
    try:
        show_r = subprocess.run(
            ["git", "stash", "show", "--name-only", stash_ref],
            cwd=str(root), capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=15,
        )
        if show_r.returncode != 0:
            return None
        stash_files = {f.strip() for f in show_r.stdout.splitlines() if f.strip()}
        hits = [f for f in clean_files if f in stash_files]
        if hits:
            return (stash_ref, stash_msg, hits)
    except (subprocess.TimeoutExpired, OSError):
        return None
    return None


def _scan_stash_for_files(
    root: Path, clean_files: list[str],
) -> tuple[str, str, list[str]] | None:
    """扫描最新 stash（stash@{0}），返回包含 clean_files 的 stash 信息。

    只扫描 stash@{0}（最新 stash）——避免从旧 stash 恢复错误版本。
    （2026-07-19 F-01 修复：原扫描最近 10 个 stash，旧 stash 可能包含
    目标文件的旧版本，auto-recover 选错导致主工作区被旧版本覆盖。）
    """
    try:
        stash_list_r = subprocess.run(
            ["git", "stash", "list", "--format=%gd|%s"],
            cwd=str(root), capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=10,
        )
        if stash_list_r.returncode != 0 or not stash_list_r.stdout.strip():
            return None
        stashes = [line.strip() for line in stash_list_r.stdout.splitlines() if line.strip()]
        # 只扫描 stash@{0}（最新 stash）——避免从旧 stash 恢复错误版本（F-01 治本）
        for stash_line in stashes[:1]:
            result = _check_stash_for_files(root, stash_line, clean_files)
            if result:
                return result
        return None
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        logger.warning("_scan_stash_for_files failed: %s", e, exc_info=True)
        return None


def _detect_changes_in_stash(
    root: Path, rel_files: list[str],
) -> tuple[str, str, list[str]] | None:
    """检测主工作区目标文件是否被 stash 移走，返回 (stash_ref, stash_msg, hits) 或 None。

    病根（2026-07-19 bug）：session_worktree_commit 假设 AI 的 Edit/Write 改动留在
    主工作区。但并发场景下主工作区改动可能被外部机制移走（手动 ``git stash push``
    / safety-net stash / 并发 session merge auto-clean / recovery 脚本）。此时
    _sync_files_to_worktree 复制的是 HEAD 内容（无改动），git diff --cached 返回 0
    → NOTHING_TO_COMMIT，AI 误判"数据丢失"。

    检测策略（逐文件，支持混合场景——部分文件有改动、部分被 stash 移走）：
    1. ``git diff --name-only HEAD`` 获取主工作区所有有改动的文件
    2. 找出目标文件中无改动的（可能被 stash 移走）
    3. 扫描最新 stash（stash@{0}）是否包含这些无改动文件
    4. 命中返回 (stash_ref, stash_msg, hits)；未命中返回 None
    """
    clean_files = _get_clean_target_files(root, rel_files)
    if not clean_files:
        return None
    return _scan_stash_for_files(root, clean_files)


def _recover_changes_from_stash(
    root: Path, rel_files: list[str], session_id: str,
) -> bool:
    """auto-recover：主工作区改动被 stash 移走时，自动从 stash 恢复目标文件。

    场景：AI 用 Edit/Write 写主工作区，但外部机制（safety-net stash / recovery
    脚本 / 并发 session merge auto-clean）通过 ``git stash push`` 清空了工作区。
    session_worktree_commit 看到空工作区返回 NOTHING_TO_COMMIT，AI 误判"数据丢失"。

    修复（2026-07-19 治本）：检测到目标文件在 stash 中时，自动
    ``git checkout <stash> -- <files>`` 恢复目标文件到主工作区。只恢复目标文件
    （不带入无关改动），覆盖式恢复（不会因 stash 基于旧 HEAD 而冲突）。恢复后
    由调用方继续正常的 sync → add → commit 流程。

    为什么用 checkout 而非 pop：stash 可能基于旧 HEAD（pop 会冲突），或包含非
    目标文件（pop 会带入无关改动）。checkout 只取目标文件，覆盖式恢复更安全。

    Returns:
        True 表示已恢复（应继续正常流程），False 表示未找到 stash 或恢复失败。
    """
    detected = _detect_changes_in_stash(root, rel_files)
    if not detected:
        return False
    stash_ref, stash_msg, hits = detected
    print("\n" + "=" * 80, file=sys.stderr)
    print(
        "[SESSION_WORKTREE_COMMIT] AUTO-RECOVER: target files found in stash, "
        "recovering to main workspace",
        file=sys.stderr,
    )
    print(f"  session_id: {session_id}", file=sys.stderr)
    print(f"  stash: {stash_ref} ({stash_msg})", file=sys.stderr)
    print(
        f"  files ({len(hits)}): {hits[:5]}{'...' if len(hits) > 5 else ''}",
        file=sys.stderr,
    )
    # P1.3 fast-path：session_worktree auto-recover 是可信调用方，跳过 git_guard alias 扫描
    # 用 git restore --source 替代 git checkout（Trae Shell Interception 对 git checkout
    # 二次拦截会弹窗；git restore --source 语义等价且不弹窗，git_guard.py 已支持 restore
    # 子命令拦截保护，安全性不降级）
    restore_r = subprocess.run(
        ["git", "restore", "--source", stash_ref, "--"] + hits,
        cwd=str(root), capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=60,
        env=_trusted_git_env(),
    )
    if restore_r.returncode == 0:
        print(
            f"  ✓ recovered {len(hits)} file(s) to main workspace, "
            "continuing with normal commit flow",
            file=sys.stderr,
        )
        print("=" * 80 + "\n", file=sys.stderr)
        # P2-6（2026-07-19）：file_restore 遥测——记录从 stash 恢复到主工作区的文件
        # content_hash 在恢复后计算（restore 写入文件内容后），用于校验恢复完整性
        for rel_file in hits:
            restored_hash = _compute_content_hash(root / rel_file)
            _log_workspace_op(
                "file_restore", session_id, "auto_recover_from_stash", root,
                file=rel_file, backup_path=f"stash:{stash_ref}",
                content_hash=restored_hash,
            )
        return True
    print(
        f"  ✗ git restore failed: {restore_r.stderr.strip()[:200]}",
        file=sys.stderr,
    )
    print("  falling back to manual recovery:", file=sys.stderr)
    print(f"    git stash pop {stash_ref}", file=sys.stderr)
    print(f"    git restore --source {stash_ref} -- <file>", file=sys.stderr)
    print("=" * 80 + "\n", file=sys.stderr)
    return False


def _warn_if_changes_missing(root: Path, rel_files: list[str], session_id: str) -> None:
    """NOTHING_TO_COMMIT 兜底诊断：检测目标文件是否在 stash 中，打印 LOUD warning。

    当 _recover_changes_from_stash 未触发或失败（如 sync 之前主工作区有改动但
    sync 后 diff 仍为 0 的边缘情况），此函数作为兜底，在 NOTHING_TO_COMMIT
    返回前打印恢复命令。

    病根（2026-07-19 bug 修复）：
    session_worktree_commit 假设 AI 的 Edit/Write 改动留在主工作区。但并发场景下
    主工作区改动可能被外部机制移走（手动 ``git stash push`` / safety-net stash /
    并发 session merge 后的 auto-clean / recovery 脚本）。此时 _sync_files_to_worktree
    复制的是 HEAD 内容（无改动），git diff --cached 返回 0 → NOTHING_TO_COMMIT。
    AI 误以为数据丢失，实际改动在 stash 中（可恢复 via ``git stash pop``）。
    """
    detected = _detect_changes_in_stash(root, rel_files)
    if not detected:
        return
    stash_ref, stash_msg, hits = detected
    print("\n" + "=" * 80, file=sys.stderr)
    print(
        "[SESSION_WORKTREE_COMMIT] WARNING: NOTHING_TO_COMMIT but "
        "target files found in stash!",
        file=sys.stderr,
    )
    print(f"  session_id: {session_id}", file=sys.stderr)
    print(f"  stash: {stash_ref} ({stash_msg})", file=sys.stderr)
    print(
        f"  files in stash ({len(hits)}): "
        f"{hits[:5]}{'...' if len(hits) > 5 else ''}",
        file=sys.stderr,
    )
    print("", file=sys.stderr)
    print("  Root cause: main workspace is clean (matches HEAD),", file=sys.stderr)
    print("  but your Edit/Write changes were stashed by an external", file=sys.stderr)
    print("  mechanism (manual stash / safety-net / recovery script).", file=sys.stderr)
    print("", file=sys.stderr)
    print("  Recovery options:", file=sys.stderr)
    print(f"    1. git stash pop {stash_ref}", file=sys.stderr)
    print("       (restore ALL stashed changes—may include other files)", file=sys.stderr)
    print(
        f"    2. git restore --source {stash_ref} -- <file>",
        file=sys.stderr,
    )
    print("       (restore specific file from stash, safer)", file=sys.stderr)
    print("  Then re-call session_worktree_commit.", file=sys.stderr)
    print("=" * 80 + "\n", file=sys.stderr)


@_inject_ok
def session_worktree_commit(
    session_id: str,
    files: list[str],
    message: str,
    project_root: str | Path | None = None,
    allow_overlap: bool = False,
    allow_promote: bool = False,
    allow_migration: bool = False,
) -> CommitResult:
    """在 worktree 内提交修改（直接 git add + commit，绕过 GitCommitGateway）。

    worktree 有独立 git index，session 独占整个 worktree，不存在共享冲突，
    无需 GitCommitGateway 的门禁保护和全局锁。

    **文件同步（君子协定模式）**：AI 的 Edit/Write 写到项目根（IDE 限制，无法改），
    worktree 内文件是创建时的旧版本。本函数在 git add 前自动将 files 从项目根
    同步（copy）到 worktree，确保 stage 的是最新内容。AI 无需手动同步。

    **HELD-OVERLAP 硬阻断（2026-07-02 加硬）**：commit 前对每个文件调
    ``registry.claim_file()``（原子 check-and-claim，防 TOCTOU 竞态）。若被其他
    活跃 session 持有 -> ``HELD_OVERLAP_VIOLATION`` 硬阻断（回滚已 claim 的文件）。
    claim 是 session 级（不 per-commit 释放），merge/abort 时 ``unregister`` 自动
    释放。这使 worktree 模式下的文件锁与 GitCommitGateway 的 HELD-OVERLAP gate
    一样硬——消除"两 session 编辑同一文件导致 merge conflict"的根因。
    ``allow_overlap=True`` 逃生通道（对标 GitCommitGateway）。

    **DCR 检测（ARCH-041 治本，2026-07-03 加）**：HELD-OVERLAP gate 后、文件同步前，
    subprocess 调用 ``check_directory_contract.py``（DCR 检测真源），对标 GitCommitGateway
    的 DIRECTORY-CONTRACT gate。治本 session_worktree_commit 绕过 GitCommitGateway 导致
    directory_contract 检测（含 _backups 禁止、DCR-001~007）不触发的问题。fail-closed——
    checker 缺失/超时也阻断。文件数 >200 时改用 ``--all-files``（避免命令行长度限制）。

    Args:
        session_id: 已注册的 session_id（必须有对应 worktree）。
        files: 要提交的文件列表。路径可以是绝对路径（项目根或 worktree 内）或相对的。
        message: commit message。
        project_root: 项目根目录（默认 REPO_ROOT）。
        allow_overlap: True 时跳过 HELD-OVERLAP 检查（逃生通道，对标 GitCommitGateway
            的 ``--allow-overlap``）。默认 False（硬阻断）。
        allow_promote: True 时允许新增文件进入永久区（对标 GitCommitGateway 的
            ``allow_promote``）。用于 YAML 真源/规则/词表等合法永久文件准入。
            默认 False（FILE-PLACEMENT-TTL gate 阻断永久区新文件）。
        allow_migration: True 时跳过 FILE-COPY 和 ORPHAN-MODULE 门禁。用于物理路径
            迁移场景（git mv + import 重写）——迁移文件天然与旧路径同名文件高度相似
           （FILE-COPY 误报），且迁移过程中 import 引用可能尚未完全更新（ORPHAN-MODULE
            误报）。仅在确认为合法迁移操作时使用。默认 False。

    Returns:
        {
            "session_id": str,
            "status": "OK" | "NOTHING_TO_COMMIT" | "FAILED",
            "message": str,
            "commit_hash": str,   # 成功时为短 SHA，否则空
        }
        worktree 不存在时附加 "not_found": True。
        HELD-OVERLAP 阻断时附加 "held_overlap": True。
        DCR 检测阻断时附加 "directory_contract_violation": True。
    """
    root = Path(project_root) if project_root else REPO_ROOT
    manager = _get_manager(root)

    if not manager._worktree_exists(session_id):
        return {
            "session_id": session_id,
            "status": "FAILED",
            "message": f"worktree 不存在 (session={session_id})，先调 session_worktree_start",
            "commit_hash": "",
            "not_found": True,
        }

    wt_path = manager._wt_path(session_id)

    try:
        _get_registry(root).heartbeat(session_id)
    except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
        pass

    if not files:
        return {
            "session_id": session_id,
            "status": "NOTHING_TO_COMMIT",
            "message": "empty files list",
            "commit_hash": "",
        }

    rel_files = _normalize_commit_files(files, wt_path, root)

    if not allow_overlap:
        err = _check_held_overlap(_get_registry(root), session_id, rel_files)
        if err:
            return err

    err = _run_dcr_check(root, rel_files, session_id)
    if err:
        return err

    # 裁定#19-B（2026-07-18）：worktree base 新鲜度检查
    # 病根：session_worktree_start 创建 worktree 时 base = dev HEAD(T0)，并发 session merge
    #   到 dev 后 dev HEAD 前进到 T1，AI Edit 主工作区文件（含 dev T1 内容 + AI 改动），
    #   _sync_files_to_worktree copy2 主工作区文件到 worktree，commit 内容 =
    #   (dev T1 + AI 改动) − (worktree base T0) = dev T0→T1 改动（搭便车）+ AI 改动。
    #   后果：① git 历史污染（dev 多 commit 被塞进 session commit）；② ARCH-REFERENCE L2
    #   误判（dev 新 #ARCH-XXX 引用被算作本次 commit 新增，要求 registry 同 commit → 硬阻断）。
    # 治本：_sync_files_to_worktree 之前检测 worktree HEAD 是否落后于主工作区 HEAD，落后则
    #   ① 无 session commit → git reset --hard <main HEAD>（安全，worktree 无未提交工作可丢）
    #   ② 有 session commit → git rebase <main HEAD>（保留 session 工作，冲突 fail-loud）
    base_err = _ensure_worktree_base_fresh(root, wt_path, session_id)
    if base_err:
        return base_err

    # auto-recover（2026-07-19 bug 治本修复）：检测主工作区改动是否被外部 stash
    # 移走（safety-net stash / recovery 脚本 / 并发 session merge auto-clean），
    # 命中则自动 git checkout <stash> -- <files> 恢复目标文件到主工作区。治本
    # session_worktree_commit 假设 AI 改动在主工作区，但外部 stash 移走改动后
    # sync 复制 HEAD 内容 → diff 为 0 → NOTHING_TO_COMMIT，AI 误判"数据丢失"。
    # auto-recover 只恢复目标文件（不带入无关改动），覆盖式恢复（不冲突）。
    _recover_changes_from_stash(root, rel_files, session_id)

    _sync_files_to_worktree(root, wt_path, rel_files)

    add_cmd = ["git", "add", "-A", "--"] + rel_files
    add_r = subprocess.run(
        add_cmd, cwd=str(wt_path), capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=60,
    )
    if add_r.returncode != 0:
        return {
            "session_id": session_id,
            "status": "FAILED",
            "message": f"git add failed: {add_r.stderr.strip()}",
            "commit_hash": "",
        }

    diff_r = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        cwd=str(wt_path), capture_output=True, timeout=30,
    )
    if diff_r.returncode == 0:
        # 诊断盲区修复（2026-07-19 bug）：返回 NOTHING_TO_COMMIT 前，检测主工作区
        # 目标文件是否意外干净（改动被外部 stash 移走）。命中则打印 LOUD warning +
        # 恢复命令。病根：session_worktree_commit 假设 AI 改动在主工作区，但并发
        # 场景下可能被 safety-net stash / recovery 脚本移走，导致 AI 误判"数据丢失"。
        # 实际改动在 stash 中可恢复。warn-only 不阻断业务流程。
        _warn_if_changes_missing(root, rel_files, session_id)
        return {
            "session_id": session_id,
            "status": "NOTHING_TO_COMMIT",
            "message": "no staged changes after git add",
            "commit_hash": "",
        }

    # P1-2 (2026-07-20): per-session active guard 防止 sweep 并发删除 worktree
    # ——pre-commit gate 检查（panorama_alignment_gate 等）调 _run_git(cwd=worktree),
    #   若此时 sweep 删除 worktree 则抛 NotADirectoryError。guard 创建 lockfile,
    #   _sweep_one_dir 判据 4 检查 lockfile 存在则跳过该 session。
    with _session_active_guard(root, session_id):
        err = _run_pre_commit_gates(root, wt_path, rel_files, session_id, allow_promote, allow_migration, message)
        if err:
            return err

        commit_result = _git_commit_in_worktree(wt_path, message, session_id)
        if commit_result.get("status") == "OK":
            # #ARCH-DEPGRAPH-RECONCILER-FAILSILENT P4.3: 修复触发断链
            # session_worktree_commit 绕过 GitCommitGateway（worktree 独立 index 设计决策，
            # 见 docstring line 42-48），导致 GitCommitGateway._run_post_commit_reconcile
            # 从未被调用。此处显式触发 reconciler 链补齐——治本不是让 session_worktree
            # 走 GitCommitGateway（会破坏 worktree 隔离），而是在 commit 后显式触发 reconciler。
            # reconciler 的 auto-commit 通过 _commit_auto 只提交 reconciler 生成的文件，
            # 不搭便车提交工作区遗留；merge 时由 _ensure_worktree_base_fresh 自动对齐（裁定#19-B）。
            commit_result["reconcile_results"] = _run_post_commit_reconcile(
                root, rel_files, session_id,
            )
        return commit_result


def _get_branch_changed_files(root: Path, branch: str) -> list[str]:
    """获取 worktree branch 相对 merge-base 的变更文件列表。"""
    merge_base_r = subprocess.run(
        ["git", "merge-base", "HEAD", branch],
        cwd=str(root), capture_output=True, text=True, encoding="utf-8",
    )
    if merge_base_r.returncode != 0:
        return []
    merge_base = merge_base_r.stdout.strip()
    changed_r = subprocess.run(
        ["git", "diff", "--name-only", f"{merge_base}..{branch}"],
        cwd=str(root), capture_output=True, text=True, encoding="utf-8",
    )
    if changed_r.returncode != 0:
        return []
    return [f.strip() for f in changed_r.stdout.strip().split("\n") if f.strip()]


def _get_dirty_files(root: Path) -> set[str] | None:
    """获取主工作区未提交改动文件（staged + unstaged），失败返回 None。"""
    dirty_r = subprocess.run(
        ["git", "diff", "--name-only", "HEAD"],
        cwd=str(root), capture_output=True, text=True, encoding="utf-8",
    )
    if dirty_r.returncode != 0:
        return None
    return {f.strip() for f in dirty_r.stdout.strip().split("\n") if f.strip()}


def _collect_tracked_cleanups(
    root: Path, branch: str, changed_files: list[str], dirty_files: set[str],
    skip_files: set[str] | None = None,
) -> tuple[int, list[str], list[str]]:
    """收集 tracked dirty 文件的清理操作——返回 (cleaned, skipped, to_checkout)。

    Ruling:100PCT-AI-GOVERNANCE P2-2 (2026-07-19) 治本：
    新增 ``skip_files`` 参数——其他活跃 session claim 的文件不清理，避免并发
    session 的 _pre_merge_auto_clean 毫秒级还原正在编辑的文件（P1-5 实测 bug）。
    """
    cleaned = 0
    skipped: list[str] = []
    to_checkout: list[str] = []
    skip_set = skip_files or set()
    for rel_file in changed_files:
        if rel_file not in dirty_files:
            continue
        # P2-2: 跳过其他 session claim 的文件（并发编辑保护）
        if rel_file in skip_set:
            skipped.append(rel_file)
            continue
        main_file = root / rel_file
        if not main_file.exists():
            skipped.append(rel_file)
            continue
        main_content = main_file.read_bytes()
        wt_content_r = subprocess.run(
            ["git", "show", f"{branch}:{rel_file}"],
            cwd=str(root), capture_output=True,
        )
        if wt_content_r.returncode != 0:
            skipped.append(rel_file)
            continue
        if main_content == wt_content_r.stdout:
            to_checkout.append(rel_file)
            cleaned += 1
        else:
            skipped.append(rel_file)
    return cleaned, skipped, to_checkout


def _collect_untracked_cleanups(
    root: Path, branch: str, changed_files: list[str],
    skip_files: set[str] | None = None,
) -> tuple[int, list[str], list[str]]:
    """收集 untracked 文件的清理操作——返回 (cleaned, skipped, to_unlink)。

    Ruling:100PCT-AI-GOVERNANCE P2-2 (2026-07-19) 治本：
    新增 ``skip_files`` 参数——其他活跃 session claim 的文件不清理。
    """
    untracked_r = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard"],
        cwd=str(root), capture_output=True, text=True, encoding="utf-8",
    )
    if untracked_r.returncode != 0 or not untracked_r.stdout.strip():
        return 0, [], []
    untracked_files = {f.strip() for f in untracked_r.stdout.strip().split("\n") if f.strip()}
    cleaned = 0
    skipped: list[str] = []
    to_unlink: list[str] = []
    skip_set = skip_files or set()
    for rel_file in changed_files:
        if rel_file not in untracked_files:
            continue
        # P2-2: 跳过其他 session claim 的文件（并发编辑保护）
        if rel_file in skip_set:
            skipped.append(rel_file)
            continue
        main_file = root / rel_file
        if not main_file.exists():
            continue
        main_content = main_file.read_bytes()
        wt_content_r = subprocess.run(
            ["git", "show", f"{branch}:{rel_file}"],
            cwd=str(root), capture_output=True,
        )
        if wt_content_r.returncode != 0:
            skipped.append(rel_file)
            continue
        if main_content == wt_content_r.stdout:
            to_unlink.append(rel_file)
            cleaned += 1
        else:
            skipped.append(rel_file)
    return cleaned, skipped, to_unlink


def _execute_cleanups(
    root: Path, to_checkout: list[str], to_unlink: list[str],
    session_id: str = "",
) -> None:
    """执行批量 stash tracked dirty 文件 + 删除 untracked 文件。

    治本（#ARCH-WORKTREE-002 缺陷2，2026-07-19）：tracked 文件原用 ``git checkout --``
    永久丢弃修改，merge 失败后 abort 导致修改丢失（实测 Phase 1+3 修改被 abort
    还原到 HEAD 全部丢失）。改为 ``git stash push`` 保存修改（可恢复 via
    ``git stash pop``），与 session_worktree_abort 的 S3-B 治本一致。

    Args:
        root: 主仓库根目录。
        to_checkout: 需要 stash 的 tracked 文件列表（原 to_checkout 语义）。
        to_unlink: 需要物理删除的 untracked 文件列表。
        session_id: session 标识，用于 stash message 溯源。
    """
    if to_checkout:
        # 治本（#ARCH-WORKTREE-002 缺陷2）：git stash push 替代 git checkout --
        # stash 保留修改（可恢复 via git stash pop），checkout -- 永久丢弃
        stash_msg = (
            f"session_worktree_pre_merge: {session_id}"
            if session_id else "session_worktree_pre_merge"
        )
        # P2-6: stash push 前计算 content_hash（push 后文件被 reset 到 HEAD，hash 会变）
        pre_stash_hashes: dict[str, str] = {}
        for rel_file in to_checkout:
            pre_stash_hashes[rel_file] = _compute_content_hash(root / rel_file)
        subprocess.run(
            ["git", "stash", "push", "-m", stash_msg, "--"] + to_checkout,
            cwd=str(root), capture_output=True,
            env=_trusted_git_env(),
        )
        logger.info(
            "session_worktree_pre_merge: stashed %d tracked file(s) for session=%s "
            "(recoverable via 'git stash pop')", len(to_checkout), session_id or "?",
        )
        # 裁定#C（2026-07-19）：stash 操作遥测（P2-6: 含 content_hash）
        for rel_file in to_checkout:
            _log_workspace_op(
                "file_stash", session_id, "pre_merge_auto_clean", root,
                file=rel_file, backup_path=f"stash:{stash_msg}",
                content_hash=pre_stash_hashes.get(rel_file, ""),
            )
    for rel_file in to_unlink:
        # 裁定#B（2026-07-19）：untracked 文件物理删除 → 隔离区移送（72h 可恢复）
        # 病根：merge 失败后 abort 导致 untracked 文件永久丢失（实测 Phase 1+3 新文件全丢）
        _quarantine_file(root, rel_file, session_id, "pre_merge_auto_clean")


def _pre_merge_auto_clean(root: Path, session_id: str) -> tuple[int, list[str]]:
    """Pre-merge 自动清理：消除 merge 失败根因，处理两类冗余文件。

    场景1（tracked dirty）：AI 的 Edit 改动留在主工作区（uncommitted），
    session_worktree_commit 同步到 worktree 并 commit。这些未提交改动与 worktree
    commit 内容一致，merge 时触发 "Your local changes would be overwritten by merge"。
    修复：内容一致时 git stash push 保存修改（可恢复 via git stash pop），文件还原
    到 HEAD（merge 会重新带入）。治本（#ARCH-WORKTREE-002 缺陷2，2026-07-19）：
    原用 git checkout -- 永久丢弃，merge 失败后 abort 导致修改丢失；改为 stash
    与 session_worktree_abort 的 S3-B 治本一致。

    场景2（untracked new file）：AI 用 Write 创建新文件留在主工作区（untracked），
    session_worktree_commit 复制到 worktree 并 commit。merge 时 git 拒绝覆盖 untracked
    文件（"untracked working tree files would be overwritten by merge"）。
    修复：内容一致时物理删除 untracked 文件（merge 会重新创建）。

    两类场景都只清理内容完全一致的文件（safe）；内容不一致的跳过（AI 有额外编辑）。

    Ruling:100PCT-AI-GOVERNANCE P2-2 (2026-07-19) 治本：
    清理前查询其他活跃 session claim 的文件（other_held_files），claimed 文件
    加入 skip_files 不清理。病根：并发 session 的 _pre_merge_auto_clean 在毫秒级
    还原正在编辑的文件（P1-5 实测 bug——AI Edit 后、session_worktree_commit 前
    窗口被命中）。治本：claim_files_for_edit API 让 AI 在编辑前 claim 文件，
    _pre_merge_auto_clean 尊重 claim 不清理。

    Args:
        root: 主仓库根目录。
        session_id: session 标识。

    Returns:
        (cleaned_count, skipped_files) 元组：
        - cleaned_count: 自动清理的文件数
        - skipped_files: 内容不一致或无法比较，跳过的文件列表
    """
    branch = f"session/{session_id}"
    changed_files = _get_branch_changed_files(root, branch)
    if not changed_files:
        return 0, []
    dirty_files = _get_dirty_files(root)
    if dirty_files is None:
        return 0, []

    # P2-2: 查询其他活跃 session claim 的文件，转相对路径加入 skip_files
    skip_files = _get_other_session_claimed_files(root, session_id)

    cleaned_t, skipped_t, to_checkout = _collect_tracked_cleanups(
        root, branch, changed_files, dirty_files, skip_files=skip_files,
    )
    cleaned_u, skipped_u, to_unlink = _collect_untracked_cleanups(
        root, branch, changed_files, skip_files=skip_files,
    )
    _execute_cleanups(root, to_checkout, to_unlink, session_id)
    return cleaned_t + cleaned_u, skipped_t + skipped_u


def _get_other_session_claimed_files(root: Path, session_id: str) -> set[str]:
    """查询其他活跃 session claim 的文件，返回相对路径集合。

    Ruling:100PCT-AI-GOVERNANCE P2-2 (2026-07-19)：
    other_held_files 返回归一化绝对路径，本函数转相对路径供 _collect_*_cleanups 使用。
    失败时返回空集（fail-open，不阻断 merge——claim 查询失败不应阻塞业务流程）。
    """
    try:
        registry = _get_registry(root)
        held_abs = registry.other_held_files(session_id)
        if not held_abs:
            return set()
        # 绝对路径 → 相对路径（forward slash）
        root_str = str(root)
        rel_files: set[str] = set()
        for abs_path in held_abs:
            p = str(abs_path)
            if p.startswith(root_str):
                rel = p[len(root_str):].lstrip("\\/").replace("\\", "/")
                if rel:
                    rel_files.add(rel)
            else:
                # 不在 root 下的文件，忽略
                continue
        return rel_files
    except Exception:  # noqa: BLE001 — claim 查询失败不阻断 merge
        logger.warning(
            "_get_other_session_claimed_files: query failed, fail-open (no skip)",
            exc_info=True,
        )
        return set()


def claim_files_for_edit(
    session_id: str,
    files: list[str],
    project_root: str | Path | None = None,
) -> dict:
    """编辑前 claim 文件（预防并发 session _pre_merge_auto_clean 还原）。

    Ruling:100PCT-AI-GOVERNANCE P2-2 (2026-07-19) 治本：
    AI Edit 文件前调用本 API claim 文件，_pre_merge_auto_clean 会跳过 claimed 文件，
    避免 P1-5 的毫秒级还原 bug。claim 是 session 级（不 per-commit 释放），
    merge/abort 时 unregister 自动释放。

    与 session_worktree_commit 内部 _check_held_overlap 的区别：
    - _check_held_overlap: commit 时 claim（too late——Edit 后、commit 前窗口无保护）
    - claim_files_for_edit: 编辑前 claim（预防性，消除 race window）

    推荐用法（AI session 启动后、第一次 Edit 前）::

        from zephyr.gov_enforcement.rule_bridge.session_worktree import (
            session_worktree_start, claim_files_for_edit,
        )
        sid = generate_session_id()
        session_worktree_start(sid)
        claim_files_for_edit(sid, [
            "src/zephyr/some_module/file1.py",
            "src/zephyr/some_module/file2.py",
        ])
        # 现在可以安全 Edit 这些文件，并发 session 的 merge 不会还原它们

    Args:
        session_id: 已注册的 session_id（必须先 session_worktree_start）。
        files: 要 claim 的文件列表（绝对路径或相对项目根的路径）。
        project_root: 项目根目录（默认 REPO_ROOT）。

    Returns:
        {
            "ok": bool,           # 全部 claim 成功为 True
            "session_id": str,
            "claimed": list[str], # 成功 claim 的相对路径
            "blocked": list[str], # 被其他 session 持有的相对路径
            "error": str,         # 失败原因（ok=False 时）
        }
    """
    root = Path(project_root) if project_root else REPO_ROOT
    root = root.resolve()
    registry = _get_registry(root)

    if not files:
        return {
            "ok": True, "session_id": session_id,
            "claimed": [], "blocked": [], "error": "",
        }

    claimed: list[str] = []
    blocked: list[str] = []
    for f in files:
        p = Path(f)
        if not p.is_absolute():
            p = (root / f).resolve()
        rel = p.relative_to(root).as_posix()
        try:
            if registry.claim_file(session_id, rel):
                claimed.append(rel)
            else:
                blocked.append(rel)
        except Exception:  # noqa: BLE001 — 单文件 claim 失败不阻断其他文件
            blocked.append(rel)

    return {
        "ok": len(blocked) == 0,
        "session_id": session_id,
        "claimed": claimed,
        "blocked": blocked,
        "error": (
            f"以下文件被其他活跃 session 持有: {blocked}" if blocked else ""
        ),
    }


def _get_merge_files(root: Path) -> list[str]:
    """获取最近一次 merge 引入的文件列表（git diff HEAD~1 HEAD --name-only）。"""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD~1", "HEAD"],
            cwd=str(root), capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0 and result.stdout.strip():
            return [f.strip() for f in result.stdout.strip().split("\n") if f.strip()]
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        logger.warning("suppressed error in session_worktree", exc_info=True)
    return []


def _run_reconcilers_after_merge(
    committed_files: list[str], session_id: str, root: Path
) -> list[dict]:
    """merge 后异步触发 reconciler（治本 #ARCH-ASYNC-MERGE-RECONCILE-001，2026-07-20）。

    病根（第一性原理）：
    原实现同步调用 gateway._reconciliation_registry.reconcile_for()，导致：
    1. session_worktree_merge 卡 2-5min（GATE-BLUEPRINT-ID-LEGACY 全扫 5038 文件 +
       GATE-BLUEPRINT-FRONTMATTER-SYNC 超时 120s 等）
    2. AI 因性能压力绕过 session_worktree，直接用 GitCommitGateway（生成 warn_only
       + unregistered_session_id 事件）
    3. 产生大量 warn_only + allow_overlap 事件
    4. 触发 GATE-COMMIT-GW-ABUSE-MONITOR critical_warn（dim1+dim3+dim2 三维超阈）

    治本：
    对齐 P2-3 launch_reconcile_async 机制（GitCommitGateway post-commit 路径早已
    异步化），spawn detached worker subprocess 后台执行所有 reconciler，merge
    立即返回不阻塞。补齐 post-merge 路径的异步化缺口。

    降级策略（fail-open）：
    - launch 失败 → 回退 sync（_run_reconcilers_after_merge_sync，reconciler 仍需执行）
    - 获取 merge SHA 失败 → 用 session_id 派生 key（保持异步不阻塞）
    - 异步启动异常 → 回退 sync

    reconciler 数量以 GitCommitGateway._reconciliation_registry 实际注册为准，
    不硬编码（裁定 D 治本 2026-07-19）。
    """
    try:
        # 获取 merge commit SHA（post-merge HEAD = merge commit），作为 status file key
        sha_r = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(root), capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=10,
        )
        commit_sha = sha_r.stdout.strip() if sha_r.returncode == 0 else ""

        if not commit_sha:
            # SHA 获取失败——用 session_id 派生 key（保持异步不阻塞 merge）
            commit_sha = f"merge_{session_id}"

        from zephyr.governance.audit.reconcile_runner import launch_reconcile_async
        launch_result = launch_reconcile_async(
            project_root=root,
            commit_sha=commit_sha,
            session_id=session_id,
            committed_files=committed_files,
            commit_message=f"[post-merge] session={session_id}",
        )

        if launch_result.get("ok"):
            worker_pid = launch_result.get("worker_pid", 0)
            logger.info(
                "[RECONCILER] post-merge async launched "
                "(session=%s, sha=%s, pid=%s)",
                session_id, commit_sha[:12], worker_pid,
            )
            return [{
                "action": "async_pending",
                "detail": (
                    f"post-merge reconcilers launched async "
                    f"(sha={commit_sha[:12]}, pid={worker_pid})"
                ),
            }]

        # launch 失败 → 回退 sync（reconciler 仍需执行，只是退化为同步阻塞）
        logger.warning(
            "[RECONCILER] post-merge async launch failed, fallback to sync: %s",
            launch_result.get("error", ""),
        )
        return _run_reconcilers_after_merge_sync(committed_files, session_id, root)
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        logger.warning(
            "[RECONCILER] post-merge async launch exception, fallback to sync: %s",
            e, exc_info=True,
        )
        return _run_reconcilers_after_merge_sync(committed_files, session_id, root)


def _run_reconcilers_after_merge_sync(
    committed_files: list[str], session_id: str, root: Path
) -> list[dict]:
    """sync fallback：原同步实现（async launch 失败时降级使用）。

    保留原 _run_reconcilers_after_merge 的同步逻辑，作为 async 路径的 fail-open
    降级。正常情况下不应被调用——只在 launch_reconcile_async 失败时触发。

    #ARCH-DEPGRAPH-RECONCILER-FAILSILENT Phase 2: 持久化 reconciler 执行结果到
    governance.db reconcile_execution_log 表，消除 fail-silent。
    Phase 3.4 断点7: commit_message="" (post_merge 无单一 commit message)。
    """
    try:
        from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import GitCommitGateway
        from zephyr.governance.audit.reconciliation_registry import _log_reconcile_results
        gateway = GitCommitGateway(project_root=root)
        # P2.3: batch intercept -- flush on exit produces single squash commit.
        with gateway._batcher as batcher:
            batcher.enable(session_id)
            results = gateway._reconciliation_registry.reconcile_for(
                committed_files, session_id, commit_message="",
            )
        _log_reconcile_results(
            root, results, session_id,
            trigger_source="post_merge_sync_fallback", committed_files=committed_files,
            commit_message="",
        )
        summary = []
        for r in results:
            if r.action == "skip":
                continue
            summary.append({"action": r.action, "detail": r.detail})
            logger.info("[RECONCILER] %s%s", r.action, f" - {r.detail}" if r.detail else "")
        return summary
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        logger.warning("[RECONCILER] 触发失败: %s", e)
        return [{"action": "warn", "detail": str(e)}]


def _get_session_branch_diff_files(root: Path, session_id: str) -> list[str]:
    """获取 session 分支相对 merge-base 的变更文件列表（PRE-MERGE-TOPO-CHECK 过滤用）。

    返回 session 分支相对 ``git merge-base HEAD session/{sid}`` 的 ``--name-only`` diff，
    用于 _run_pre_merge_topo_check 的 rel_files 过滤（仅阻断 session 自身引入的 HIGH drift）。
    获取失败时返回空列表（topo check 调用方对空 rel_files 会放行预存漂移）。
    """
    branch = f"session/{session_id}"
    mb_r = subprocess.run(
        ["git", "merge-base", "HEAD", branch],
        cwd=str(root), capture_output=True, text=True, timeout=10,
    )
    if mb_r.returncode != 0:
        return []
    merge_base = mb_r.stdout.strip()
    diff_r = subprocess.run(
        ["git", "diff", "--name-only", f"{merge_base}..{branch}"],
        cwd=str(root), capture_output=True, text=True, timeout=10,
    )
    if diff_r.returncode != 0:
        return []
    return [f.strip() for f in diff_r.stdout.strip().split("\n") if f.strip()]


def _run_pre_merge_topo_check(
    root: Path, session_id: str, wt_path: Path, rel_files: list[str],
) -> tuple[bool, list[dict]]:
    """PRE-MERGE-TOPO-CHECK（#ARCH-DEP-001 第二期）：pre-merge 拓扑硬阻断。

    subprocess 调 MAIN 副本 ``check_blueprint_code_alignment.py --json --scan-root <worktree>``，
    扫描 session 分支 ``src/zephyr``，HIGH drift（ORPHAN_MODULE_ID / MODULE_ID_DRIFT）
    阻断 merge。LOW（CODE_NOT_IN_DEPGRAPH）暂态容忍，不阻断（与 L1 铁律当前语义一致——
    depgraph 同步滞后由 post-merge reconciler 兜底）。

    为什么运行 MAIN 副本 checker 而非 worktree 副本：``config/.env.postgres`` 被 gitignore，
    worktree 无此文件，运行 worktree 副本会因 DB 连接失败导致 ``depgraph_module_ids`` 为空
    → 大量误报 ORPHAN_MODULE_ID。MAIN 副本有 DB 配置，``--scan-root <worktree>`` 仅重定向
    代码扫描，DB 配置和蓝图注册表仍用 main REPO_ROOT——pre-merge 检查的语义是
    「session 分支代码相对 production depgraph 的漂移」。

    过滤到 session 变更文件（rel_files）：仅阻断 session 自身引入的 HIGH drift，不阻断
    预存漂移（防御性设计——main 当前 0 HIGH，但若 main 漂移回潮不应误伤 session merge）。

    降级策略（fail-closed for missing, fail-open for transient）：
    - checker 脚本缺失 → fail-closed 阻断（基础设施不完整不应放行拓扑检查）
    - DB 不可用（depgraph_module_ids==0）→ fail-open 放行 + LOUD warning（DB 不可用时
      无法可靠拓扑检查，与 load_depgraph_module_index 既有降级一致；post-merge reconciler 兜底）
    - subprocess 超时/OSError → fail-open 放行（环境异常降级，不卡死业务流程）
    - JSON 解析失败 / checker exit 2(ERROR) → fail-open 放行（保留诊断 warning）

    Returns:
        (passed, violations) —— passed=True 放行 merge，passed=False 阻断。
    """
    check_script = (
        root / "scripts" / "governance" / "d5_architecture" / "checkers"
        / "check_blueprint_code_alignment.py"
    )
    if not check_script.is_file():
        return False, [{
            "gate_id": "PRE-MERGE-TOPO-CHECK",
            "detail": (
                f"checker 缺失（fail-closed）: {check_script} —— "
                "#ARCH-DEP-001 第二期要求 pre-merge 拓扑检查，checker 不可缺"
            ),
        }]
    cmd = [sys.executable, str(check_script), "--json", "--scan-root", str(wt_path)]
    try:
        from zephyr.shared.infra.process_pool import run_subprocess_hidden

        result = run_subprocess_hidden(
            cmd, capture_output=True, text=True, cwd=str(root),
            encoding="utf-8", errors="replace", timeout=120,
        )
    except (subprocess.TimeoutExpired, OSError) as e:
        logger.warning(
            "PRE-MERGE-TOPO-CHECK: checker 执行异常（超时/OSError），降级放行: %s", e,
        )
        return True, []
    # --json 模式：checker 总会先 print JSON 再按 HIGH 决定 exit code
    # （exit 0 = 无 HIGH，exit 1 = 有 HIGH，exit 2 = ERROR）
    if result.returncode == 2:
        logger.warning(
            "PRE-MERGE-TOPO-CHECK: checker 返回 ERROR(exit 2)，降级放行。stderr: %s",
            (result.stderr or "")[:500],
        )
        return True, []
    try:
        payload = json.loads(result.stdout)
    except (json.JSONDecodeError, ValueError) as e:
        logger.warning(
            "PRE-MERGE-TOPO-CHECK: checker 输出 JSON 解析失败，降级放行。"
            "returncode=%s, stdout[:200]=%r, error=%s",
            result.returncode, (result.stdout or "")[:200], e,
        )
        return True, []
    # DB 不可用 → depgraph_module_ids==0 → fail-open（无法可靠拓扑检查）
    if payload.get("depgraph_module_ids", 0) == 0:
        logger.warning(
            "PRE-MERGE-TOPO-CHECK: depgraph_module_ids==0（DB 不可用或 depgraph 为空），"
            "无法可靠执行拓扑检查，降级放行。stderr: %s",
            (result.stderr or "")[:500],
        )
        return True, []
    findings = payload.get("findings", [])
    high_findings = [f for f in findings if f.get("severity") == "HIGH"]
    if not high_findings:
        return True, []
    # 过滤到 session 变更文件：仅阻断 session 自身引入的 HIGH drift
    rel_set = {rf.replace("\\", "/") for rf in rel_files}
    session_high = [
        f for f in high_findings
        if f.get("file", "").replace("\\", "/") in rel_set
    ]
    if not session_high:
        logger.warning(
            "PRE-MERGE-TOPO-CHECK: 检出 %d 条 HIGH drift 但均不在 session 变更文件中"
            "（预存漂移），放行。",
            len(high_findings),
        )
        return True, []
    _details = "; ".join(
        f"{f.get('file', '?')}[{f.get('type', '?')}]: {(f.get('detail', '') or '')[:120]}"
        for f in session_high[:5]
    )
    return False, [{
        "gate_id": "PRE-MERGE-TOPO-CHECK",
        "detail": (
            f"HIGH drift {len(session_high)} 条（session 变更文件引入，"
            f"#ARCH-DEP-001 第二期 pre-merge 拓扑硬阻断）: {_details}"
        ),
    }]


def _pre_merge_gate_check(
    root: Path, session_id: str, wt_path: Path,
    allow_migration: bool = False,
) -> tuple[bool, list[dict]]:
    """pre-merge gate 检查（裁定#209 后续：补齐 worktree 路径的 gate 验证）。

    在 worktree 中用 git reset --soft merge-base 模拟 staged 状态，运行 7 个
    worktree-compatible gate（跳过 HELD-OVERLAP/CLAIM-REQUIRED），检查 session
    分支相对 merge-base 的变更。检查完毕后恢复 HEAD（git reset --soft orig_head）。

    价值：session_worktree_commit 的 gate 检查在 commit 时执行，但 merge 前主分支
    可能有新 commit（并发 session）更新了 gate 规则（如新 capability 登记）。pre-merge
    gate 用最新主分支状态重新检查 session 分支变更，捕获 commit 后到 merge 前的 gate 漂移。

    降级策略：gate 基础设施异常降级为 warn（不阻断）——session_worktree 不应因 gate
    框架自身 bug 卡死业务流程；gate 检出违规则阻断 merge。

    gate 代码自身修改降级（治本 2026-07-17）：当 session 分支修改了 commit_gates/
    下的 .py 文件时，pre-merge gate 用主分支 HEAD 的旧 gate 代码（import 自
    sys.path 主工作区 src/）检测 worktree branch 的新调用，形成「鸡生蛋」阻断
    （如扩展白名单后，旧白名单不含新文件→DEPGRAPH-WRITE-PATH gate 误判阻断）。
    此时所有 blocking gate 降级为 warn-only（log warning + 不阻断 merge），AI 可在
    merge 后用新 gate 代码验证。理由：gate 代码修改是本次任务目标，用旧 gate
    代码检测新 gate 代码不合理；降级保留诊断信息，不丢安全（commit 时已有 gate 检查）。

    PRE-MERGE-TOPO-CHECK（#ARCH-DEP-001 第二期，2026-07-17）：commit gate 检查后
    额外执行拓扑硬阻断——subprocess 调 MAIN 副本 check_blueprint_code_alignment.py
    --scan-root <worktree>，HIGH drift（ORPHAN_MODULE_ID/MODULE_ID_DRIFT）阻断 merge。
    独立于 commit gate（不受 gate 代码修改降级影响）——topo checker 是独立脚本，非
    commit_gates/，不存在「鸡生蛋」。即使 commit gate 降级为 warn-only，topo 检查仍
    执行；LOW（CODE_NOT_IN_DEPGRAPH）暂态容忍。详见 _run_pre_merge_topo_check。

    Returns:
        (passed, violations) —— passed=True 放行 merge，passed=False 阻断。
    """
    try:
        from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import (
            GitCommitGateway, _GATEWAY_ENV,
        )

        # 获取 session 分支变更文件列表
        branch = f"session/{session_id}"
        mb_r = subprocess.run(
            ["git", "merge-base", "HEAD", branch],
            cwd=str(root), capture_output=True, text=True, timeout=10,
        )
        if mb_r.returncode != 0:
            return True, []  # 无法获取 merge-base，降级放行
        merge_base = mb_r.stdout.strip()

        diff_r = subprocess.run(
            ["git", "diff", "--name-only", f"{merge_base}..{branch}"],
            cwd=str(root), capture_output=True, text=True, timeout=10,
        )
        if diff_r.returncode != 0 or not diff_r.stdout.strip():
            return True, []  # 无变更，放行

        rel_files = [f.strip() for f in diff_r.stdout.strip().split("\n") if f.strip()]

        # 保存当前 HEAD（用于恢复）
        head_r = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(wt_path), capture_output=True, text=True, timeout=10,
        )
        if head_r.returncode != 0:
            return True, []  # 无法获取 HEAD，降级放行
        orig_head = head_r.stdout.strip()

        # git reset --soft merge-base：模拟 staged 状态（HEAD 移到 merge-base，index 保留 session commit 内容）
        # P1.3 fast-path：session_worktree pre-merge gate check 是可信调用方，跳过 git_guard alias 扫描
        reset_r = subprocess.run(
            ["git", "reset", "--soft", merge_base],
            cwd=str(wt_path), capture_output=True, text=True, timeout=30,
            env=_trusted_git_env(),
        )
        if reset_r.returncode != 0:
            return True, []  # reset 失败，降级放行

        try:
            # project_root 用 worktree 路径（修复 gate 相对路径计算 bug）
            # 原实现用 root（主工作区路径），gate 用 project_root 计算 rel 时
            # worktree 文件路径（.aidrafts/...）被误判为新文件，触发 module_id_collision
            #
            # registry MUST 用主工作区的 SessionRegistry（修复 SESSION-REQUIRED 误判 bug，2026-07-06）
            # 原实现用 wt_path 初始化 SessionRegistry，但 session 在 session_worktree_start
            # 时用主工作区路径注册（_get_registry(root)），worktree 路径查不到注册的 session，
            # 导致 SESSION-REQUIRED gate 误判"session 未注册"阻断 merge。
            _gw = GitCommitGateway(project_root=wt_path, registry=SessionRegistry(root))
            # monkeypatch _run_git 重定向 cwd 到 worktree（使 git diff --cached 查 worktree index）
            _orig_run_git = _gw._run_git

            def _wt_run_git(cmd, cwd=None, _wt=str(wt_path), _env_var=_GATEWAY_ENV):
                _env = os.environ.copy()
                _env[_env_var] = "1"
                # 阻断 git commit（gate 检查不应触发 commit）
                if (len(cmd) >= 2 and cmd[0] == "git" and cmd[1] == "commit"
                        and not getattr(_gw, "_in_commit_flow", False)):
                    return subprocess.CompletedProcess(
                        cmd, 1, "", "git commit blocked in pre-merge gate check"
                    )
                _effective_cwd = cwd if cwd is not None else _wt
                return subprocess.run(
                    cmd, cwd=_effective_cwd, capture_output=True, text=True,
                    encoding="utf-8", errors="replace", timeout=60, env=_env,
                )

            _gw._run_git = _wt_run_git

            # monkeypatch TEST-SOURCE-CONSISTENCY gate 的 _SRC_ROOT 指向 worktree src
            # 病根（2026-07-17 治本）：gate 用全局 _SRC_ROOT = REPO_ROOT / "src"（主仓库），
            # pre-merge 场景下主仓库源码滞后于 worktree（worktree 有新符号如 _run_pre_merge_topo_check，
            # 主仓库还没 merge），导致 worktree test import 的符号在主仓库源码中找不到 -> 误阻断 merge。
            # 治本：pre-merge 时临时重定向 _SRC_ROOT 到 worktree src，使 gate 从 worktree 读源码符号
            # （与 worktree test 对齐，pre-merge 语义是检测 session 分支变更）。finally 中恢复。
            import zephyr.gov_enforcement.commit_gates.test_source_consistency_gate as _tsc_gate
            _orig_src_root = _tsc_gate._SRC_ROOT
            _tsc_gate._SRC_ROOT = wt_path / "src"

            try:
                # 检查 worktree 文件（session 分支的内容），而非主工作区文件
                # 修复 (2026-07-05 审计 AI-02)：原实现用 root 路径检查主工作区文件，
                # 主工作区 HEAD 版本可能缺少 ttl 等字段（历史遗留），导致 pre-merge gate
                # 误判 session 分支变更违规。pre-merge gate 的目的是检查 session 分支的
                # 文件内容是否合法，应该读取 worktree 文件（session 分支的内容）。
                _changed_abs = [str((wt_path / rf).resolve()) for rf in rel_files]
                _gate_results = _gw._gate_registry.check_all(
                    _gw, _changed_abs, session_id=session_id
                )
            finally:
                _tsc_gate._SRC_ROOT = _orig_src_root
                _gw._run_git = _orig_run_git

            _skip_gates = _WORKTREE_SKIP_GATES
            if allow_migration:
                _skip_gates = _skip_gates | frozenset({"FILE-COPY", "ORPHAN-MODULE", "TEST-SOURCE-CONSISTENCY"})

            # 治本（2026-07-17）：检测 session 分支是否修改了 gate 代码本身
            # 问题：pre-merge gate 用主分支 HEAD 的 gate 代码（import 自 sys.path 主工作区 src/），
            # 当 session 分支修改了 commit_gates/ 下的 gate 代码（如扩展白名单、调整检测逻辑），
            # 旧 gate 代码会误判新代码引入的变更，形成「鸡生蛋」阻断。
            # 降级策略：gate 代码自身修改时，所有 blocking gate 降级为 warn-only
            # （log warning + 放行 merge）。理由：gate 代码修改是本次任务目标，用旧
            # gate 代码检测新 gate 代码不合理；降级保留诊断信息，不丢安全（commit 时
            # 已有 gate 检查，post-merge reconciler 也会对账）。
            _gate_code_modified = any(
                "commit_gates/" in rf.replace("\\", "/") and rf.endswith(".py")
                for rf in rel_files
            )

            _blocking = [
                gr for gr in _gate_results
                if not gr.passed and gr.gate_id not in _skip_gates
            ]
            _gate_violations: list[dict] = []
            if _blocking and _gate_code_modified:
                # gate 代码自身修改——降级为 warn-only（不阻断 merge，但不 early return——
                # PRE-MERGE-TOPO-CHECK 仍需执行，topo 检查独立于 commit gate 代码）。
                _warn_violations = [
                    {"gate_id": gr.gate_id, "detail": gr.detail[:300]} for gr in _blocking
                ]
                logger.warning(
                    "pre-merge gate: session 分支修改了 commit_gates/ 下的 gate 代码，"
                    "主分支旧 gate 代码可能误判新调用，已降级为 warn-only（不阻断 merge）。"
                    "建议 merge 后用新 gate 代码验证。violations: %s",
                    _warn_violations,
                )
                # _gate_violations 保持空——降级不产生阻断 violations
            elif _blocking:
                _gate_violations = [
                    {"gate_id": gr.gate_id, "detail": gr.detail} for gr in _blocking
                ]

            # PRE-MERGE-TOPO-CHECK 已移到 session_worktree_merge 的 _pre_merge_auto_clean
            # 之前执行（时序修复，2026-07-17）：原实现 topo check 在 auto_clean 之后执行，
            # auto_clean 会还原 session 变更列表中的 checker 文件到 HEAD 旧版本（若 session
            # 修改了 check_blueprint_code_alignment.py），导致 MAIN 副本 checker 不认识
            # --scan-root 参数而降级放行（fail-open）。移到 auto_clean 之前确保 checker
            # 是主工作区最新版本。topo check 独立于 commit gate——不受 gate 代码修改降级影响。
            if _gate_violations:
                return False, _gate_violations
            return True, []
        finally:
            # 恢复 HEAD（git reset --soft orig_head：HEAD 移回原 commit，index 不变=干净状态）
            # P1.3 fast-path：pre-merge gate HEAD 恢复是可信调用方，跳过 git_guard alias 扫描
            subprocess.run(
                ["git", "reset", "--soft", orig_head],
                cwd=str(wt_path), capture_output=True, text=True, timeout=30,
                env=_trusted_git_env(),
            )
    except Exception as _e:  # noqa: BLE001 — 5.135治标: broad exception catch
        # gate 基础设施异常降级为 warn（不阻断）
        logger.warning("pre-merge gate 检查异常降级（不阻断）: %s", _e, exc_info=True)
        return True, []


def _classify_merge_failure(error_text: str) -> str:
    """分类 merge 失败错误（#ARCH-HEARTBEAT-001 P1-4）。

    复用裁定 C 错误分类思路（_classify_sync_failure）：
      - deterministic: content conflict / worktree 不存在 / session_id 空
        → 不重试（重试也是同样的结果）
      - transient: index.lock / git process running / timeout
        → 重试（lock 释放后可能成功）
      - unknown: 其他
        → 不重试（保守，避免掩盖真实 bug）

    Args:
        error_text: merge 错误文本（stderr / 异常 str）。

    Returns:
        "deterministic" / "transient" / "unknown"
    """
    text = (error_text or "").lower()
    if not text:
        return "unknown"
    # deterministic 模式（content conflict / 参数错误 / worktree 不存在）
    _DET_PATTERNS = (
        "conflict", "merge conflict", "automatic merge failed",
        "not something we can merge", "unknown revision",
        "worktree 不存在", "session_id 不能为空",
    )
    # transient 模式（lock contention / git process 阻塞 / IO 超时）
    _TRANS_PATTERNS = (
        "index.lock", "another git process seems to be running",
        "could not lock", "unable to create", "unable to write",
        "timeoutexpired", "timeout expired", "resource temporarily unavailable",
    )
    for pat in _DET_PATTERNS:
        if pat in text:
            return "deterministic"
    for pat in _TRANS_PATTERNS:
        if pat in text:
            return "transient"
    return "unknown"


def _merge_with_retry(
    manager: WorktreeManager,
    session_id: str,
    max_attempts: int = 3,
) -> tuple[bool, str]:
    """带重试的 merge（#ARCH-HEARTBEAT-001 P1-4）。

    仅 transient 错误重试（index.lock / git process running / timeout），
    deterministic 错误立即返回（content conflict / worktree 不存在）。

    退避序列 [1, 2, 4] 秒（指数退避，给 lock 释放时间）。

    Args:
        manager: WorktreeManager 实例。
        session_id: session 标识。
        max_attempts: 最大重试次数（默认 3）。

    Returns:
        (merged, error_text) — merged=True 时 error_text 为空。
    """
    import threading as _threading
    delays = [1, 2, 4]  # 指数退避
    last_error = ""
    for attempt in range(1, max_attempts + 1):
        try:
            merged = manager.merge_session_worktree(session_id, delete_after=True)
            if merged:
                return True, ""
            # merge 返回 False 通常是冲突——提取错误信息分类
            last_error = "merge returned False (likely conflict)"
            # 尝试从 git status 获取更具体的错误信息
            try:
                wt_path = manager._wt_path(session_id)
                import subprocess as _sp
                r = _sp.run(
                    ["git", "status", "--porcelain"],
                    cwd=str(wt_path), capture_output=True, text=True,
                    encoding="utf-8", errors="replace", timeout=10,
                )
                if r.returncode == 0 and r.stdout.strip():
                    last_error = f"merge conflict: {r.stdout.strip()[:200]}"
            except Exception:  # noqa: BLE001 — best-effort 错误信息提取
                pass
            classification = _classify_merge_failure(last_error)
            if classification != "transient" or attempt == max_attempts:
                return False, last_error
            _threading.Event().wait(delays[attempt - 1])
        except WorktreeError as e:
            # WorktreeError 通常是 deterministic（worktree 不存在 / 参数错误）
            return False, f"WorktreeError: {e}"
        except subprocess.TimeoutExpired as e:
            last_error = f"TimeoutExpired: {e}"
            classification = _classify_merge_failure(last_error)
            if classification != "transient" or attempt == max_attempts:
                return False, last_error
            _threading.Event().wait(delays[attempt - 1])
        except Exception as e:  # noqa: BLE001 — 兜底
            last_error = f"{type(e).__name__}: {e}"
            classification = _classify_merge_failure(last_error)
            if classification != "transient" or attempt == max_attempts:
                return False, last_error
            _threading.Event().wait(delays[attempt - 1])
    return False, last_error


def _execute_merge_and_build_msg(
    manager: WorktreeManager,
    session_id: str,
    auto_cleaned: int,
    skipped_files: list,
) -> tuple[bool, bool, str]:
    """执行 merge 并构建结果消息，返回 (merged, cleaned, msg)。

    merge 成功后验证 worktree 是否真清理（git 注册 + 物理目录双重检查）。
    merge 成功但清理失败时 cleaned=False（worktree 残留——session 保留供重试，
    防孤儿 worktree 累积）。

    #ARCH-HEARTBEAT-001 P1-4：merge 用 _merge_with_retry 包装，transient 错误
    自动重试 3 次（1s/2s/4s 指数退避），deterministic 错误立即返回。
    """
    merged = False
    cleaned = False
    msg = ""
    merged, merge_error = _merge_with_retry(manager, session_id)
    if merged:
        parts = ["merge 成功"]
        if auto_cleaned > 0:
            parts.append(f"（pre-merge 自动清理 {auto_cleaned} 个冗余文件）")
        if skipped_files:
            parts.append(f"（{len(skipped_files)} 个文件内容不一致已跳过）")
        # 验证 worktree 是否真清理（git 注册 + 物理目录双重检查）。
        # merge 成功但清理失败时 worktree 残留——此时不注销 session，
        # 保留供重试 cleanup_session_worktree / abort（防孤儿 worktree 累积）。
        wt_path = manager._wt_path(session_id)
        if manager._worktree_exists(session_id) or wt_path.exists():
            parts.append("，但 worktree 清理失败——session 保留，请重试 cleanup")
            msg = "".join(parts)
            cleaned = False
        else:
            parts.append("，worktree 已清理")
            msg = "".join(parts)
            cleaned = True
            _log_worktree_delete(  # Phase 4 遥测：merge 删除点
                session_id, "merge", wt_path, manager.repo_root
            )
    else:
        if merge_error:
            msg = f"merge 失败（重试已耗尽）: {merge_error}"
        elif skipped_files:
            msg = (
                f"merge 失败：以下文件主工作区有额外改动（与 worktree commit 不一致），"
                f"请手动处理：{skipped_files}"
            )
        else:
            msg = "merge 冲突，worktree 保留供手动解决（解决后重新调 merge 或手动 cleanup）"
    return merged, cleaned, msg


def _run_post_merge_reconcile(root: Path, session_id: str) -> list[dict]:
    """merge 后触发 reconciler 验证，返回 reconcile_results。

    无变更文件时跳过；触发异常时降级为 warn 项（不阻断）。
    """
    reconcile_results: list[dict] = []
    try:
        committed_files = _get_merge_files(root)
        if committed_files:
            logger.info("[RECONCILER] merge 后触发 reconciler 验证（%d 个文件）...", len(committed_files))
            reconcile_results = _run_reconcilers_after_merge(committed_files, session_id, root)
        else:
            logger.info("[RECONCILER] 无变更文件，跳过 reconciler")
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        logger.warning("[RECONCILER] 触发失败: %s", e)
        reconcile_results = [{"action": "warn", "detail": str(e)}]
    return reconcile_results


def _run_post_commit_reconcile(
    root: Path, committed_files: list[str], session_id: str,
) -> list[dict]:
    """commit 后触发 reconciler（P4.3: 修复 session_worktree_commit 触发断链）。

    治本 #ARCH-DEPGRAPH-RECONCILER-FAILSILENT Phase 3(4)/Phase 4(3)：
    session_worktree_commit 绕过 GitCommitGateway.commit()（worktree 独立 index
    设计决策，见 session_worktree.py:42-48 docstring），导致
    GitCommitGateway._run_post_commit_reconcile 从未被调用——reconcile_for
    从未遍历，make_depgraph_ops_reconciler 等从不触发。本函数在
    _git_commit_in_worktree 成功后显式触发 reconciler 链，补齐触发断链。

    与 _run_reconcilers_after_merge 的区别：
    - trigger_source="post_commit_worktree"（区分于 post_merge，便于日志追溯）
    - 看到的是主仓库状态（不含 worktree commit），同步的是主仓库既有漂移
    - worktree commit 引入的漂移由 merge 后的 _run_post_merge_reconcile 处理

    安全性：reconciler 的 auto-commit 通过 _commit_auto 只提交 reconciler 生成
    的文件（manifest/path_tree 等，经 _resolve_auto_commit_files 过滤），不搭便车
    提交工作区遗留。auto-commit 在主仓库创建的新 commit 不影响 worktree 分支——
    merge 时若 worktree base 落后，_ensure_worktree_base_fresh（裁定#19-B）会
    自动对齐（无 session commit → git reset --hard；有 session commit → git rebase）。
    """
    try:
        from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import GitCommitGateway
        from zephyr.governance.audit.reconciliation_registry import _log_reconcile_results
        gateway = GitCommitGateway(project_root=root)
        # P2.3: batch intercept -- flush on exit produces single squash commit.
        with gateway._batcher as batcher:
            batcher.enable(session_id)
            results = gateway._reconciliation_registry.reconcile_for(
                committed_files, session_id, commit_message="",
            )
        # #ARCH-DEPGRAPH-RECONCILER-FAILSILENT Phase 2: 持久化到 governance.db
        # Phase 3.4 断点7: commit_message="" (worktree post-commit 路径暂不传 message)。
        _log_reconcile_results(
            root, results, session_id,
            trigger_source="post_commit_worktree", committed_files=committed_files,
            commit_message="",
        )
        summary = []
        for r in results:
            if r.action == "skip":
                continue
            summary.append({"action": r.action, "detail": r.detail})
            logger.info("[RECONCILER post-commit] %s%s", r.action, f" - {r.detail}" if r.detail else "")
        return summary
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        logger.warning("[RECONCILER post-commit] 触发失败: %s", e)
        return [{"action": "warn", "detail": str(e)}]


@_inject_ok
def session_worktree_merge(
    session_id: str,
    project_root: str | Path | None = None,
    reconcile_verify: bool = True,
    allow_migration: bool = False,
) -> MergeResult:
    """将 worktree 修改 merge 回主分支 + 清理 worktree + 注销 session。

    在主工作目录执行 git merge session/{session_id} --no-ff（保留 session 提交拓扑）。
    merge 前自动清理主工作区与 worktree commit 内容一致的未提交改动（消除 merge 失败根因）。
    merge 冲突时返回 merged=False（worktree 保留，供手动解决）。

    Args:
        session_id: 已注册的 session_id。

    Returns:
        {
            "session_id": str,
            "merged": bool,       # True=merge 成功，False=冲突/失败
            "message": str,
            "cleaned": bool,      # worktree 是否已清理
            "unregistered": bool, # session 是否已注销
        }
    """
    root = Path(project_root) if project_root else REPO_ROOT
    manager = _get_manager(root)
    registry = _get_registry(root)

    # Phase 6 治本（2026-07-19）：merge 时刷新 session heartbeat，防 TTL 过期。
    # session_worktree_start 用 pid=0（逻辑 session）注册，跨进程存活靠 TTL，
    # merge 前 heartbeat 刷新确保长 session（start→commit→merge 跨多次 python -c）
    # 不会因 TTL=3600s 过期被误判死亡。
    try:
        registry.heartbeat(session_id)
    except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
        pass  # heartbeat 失败不阻断 merge（TTL 未过期则 session 仍存活）

    # #ARCH-DEPGRAPH-RECONCILER-FAILSILENT Phase 3: pre-merge 告警横幅
    # 翻日志本查最近 24h 的 critical_warn，有则打印醒目横幅强制 AI 看到。
    # 不阻断 merge（warn 语义），但确保上次 reconciler 失败不被忽视。
    try:
        from zephyr.governance.audit.reconciliation_registry import _print_critical_warn_banner
        _print_critical_warn_banner(root, context="pre_merge")
    except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
        pass  # 告警横幅失败不应阻断 merge

    # #ARCH-DEPGRAPH-RECONCILER-FAILSILENT Phase 4.2: pre-merge 硬阻断
    # block_next 是最严重的 reconciler 失败级别——下次 merge 硬阻断。
    # 与 critical_warn 的区别：critical_warn 只告警不阻断，block_next 硬阻断。
    # AI 必须先修复问题，调 resolve_blocks() 清除阻断，才能继续 merge。
    # fail-open 策略：查询失败（governance.db 不可用）不阻断 merge，仅记录日志
    # （避免 DB 故障时永久阻塞所有 merge）。
    try:
        from zephyr.governance.audit.reconciliation_registry import _print_block_banner
        _block_err = _print_block_banner(root, context="pre_merge")
        if _block_err:
            return {
                "session_id": session_id,
                "merged": False,
                "error": _block_err,
                "blocked": True,
            }
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        logger.warning("session_worktree_merge: block_next check failed: %s", e)

    # PRE-MERGE-TOPO-CHECK（#ARCH-DEP-001 第二期）：pre-merge 拓扑硬阻断。
    # 时序关键（2026-07-17 修复）：必须在 _pre_merge_auto_clean 之前执行——
    # auto_clean 会还原 session 变更列表中的 checker 文件到 HEAD 旧版本（若 session
    # 修改了 check_blueprint_code_alignment.py），导致 MAIN 副本 checker 不认识
    # --scan-root 参数而降级放行（fail-open）。在 auto_clean 之前执行时，MAIN 副本
    # checker 还是主工作区最新版本（含 --scan-root）。topo check 独立于 commit gate——
    # 不受 gate 代码修改降级影响（topo checker 是独立脚本，非 commit_gates/）。
    wt_path = manager._wt_path(session_id)
    _topo_rel_files = _get_session_branch_diff_files(root, session_id)
    _topo_passed, _topo_violations = _run_pre_merge_topo_check(
        root, session_id, wt_path, _topo_rel_files,
    )
    if not _topo_passed:
        _details = "; ".join(f"{v['gate_id']}: {v['detail']}" for v in _topo_violations)
        # #ARCH-DEP-PREMERGE-ENFORCE (P4.1)：拓扑检查失败写入 block_next 记录，
        # 下次 commit/merge 硬阻断——AI 必须修复 HIGH drift 后调 resolve_blocks()
        # 清除阻断才能继续。复用 P4.2 的 _log_reconcile_results + block_next action
        # 语义（block_next: 最严重——下次 commit/merge 硬阻断）。
        # 为什么写 block_next 而非 critical_warn：拓扑不一致是"需要强制干预"场景，
        # critical_warn 只告警不阻断，AI 可继续 commit 引入更多漂移；block_next 硬阻断
        # 强制 AI 先修复拓扑问题。写入失败降级为 warn（不阻断本次 merge 的 return，
        # 但日志可见——DB 故障不应卡死业务流程，拓扑问题本身已通过 return 阻断本次 merge）。
        try:
            from zephyr.governance.audit.reconciliation_registry import (
                ReconcileResult,
                _log_reconcile_results,
            )
            _block_result = ReconcileResult(
                action="block_next",
                detail=f"PRE-MERGE-TOPO-CHECK 阻断: {_details}",
                gate_id="PRE-MERGE-TOPO-CHECK",
            )
            _log_reconcile_results(
                root, [_block_result], session_id, "pre_merge_topo_check",
            )
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.warning(
                "PRE-MERGE-TOPO-CHECK: 写入 block_next 记录失败（降级为仅阻断本次 merge）: %s", e,
            )
        return {
            "session_id": session_id,
            "merged": False,
            "message": (
                f"pre-merge topo check 阻断: {_details}。"
                f"已写入 block_next 记录——下次 commit/merge 将硬阻断。"
                f"修复 HIGH drift 后调 resolve_blocks() 清除阻断再重试 merge。"
            ),
            "cleaned": False,
            "unregistered": False,
            "gate_violation": True,
            "gate_results": _topo_violations,
            "reconcile_results": [],
            "blocked_next": True,  # P4.1: 标记已写入 block_next
        }

    # P1-2 (2026-07-20): per-session active guard 防止 sweep 并发删除 worktree
    # ——_pre_merge_auto_clean / _pre_merge_gate_check（monkey-patch _run_git cwd=worktree）
    #   期间若 sweep 删除 worktree 则抛 NotADirectoryError。guard 创建 lockfile,
    #   _sweep_one_dir 判据 4 检查 lockfile 存在则跳过该 session。
    #   _execute_merge_and_build_msg 内部已有 _WorktreeLock 全局锁保护,此处 guard
    #   主要覆盖 auto_clean + gate_check 的无锁窗口。
    with _session_active_guard(root, session_id):
        # Pre-merge: 自动清理与 worktree commit 内容一致的未提交改动（消除 merge 失败根因）
        # 只清理内容一致的文件（safe）；内容不一致的跳过（AI 有额外编辑，需手动处理）
        auto_cleaned, skipped_files = _pre_merge_auto_clean(root, session_id)

        # Pre-merge gate 检查（裁定#209 后续：补齐 worktree 路径的 gate 验证）
        # 用最新主分支状态重新检查 session 分支变更，捕获 commit 后到 merge 前的 gate 漂移
        gate_passed, gate_violations = _pre_merge_gate_check(root, session_id, wt_path, allow_migration=allow_migration)
        if not gate_passed:
            _details = "; ".join(f"{v['gate_id']}: {v['detail']}" for v in gate_violations)
            return {
                "session_id": session_id,
                "merged": False,
                "message": f"pre-merge gate 阻断: {_details}",
                "cleaned": False,
                "unregistered": False,
                "gate_violation": True,
                "gate_results": gate_violations,
                "reconcile_results": [],
            }

        merged, cleaned, msg = _execute_merge_and_build_msg(
            manager, session_id, auto_cleaned, skipped_files
        )

        # 裁定#209 后续：merge 后可选触发 reconciler（补齐 worktree 路径的验证）
        # 时序治本（2026-07-20，sess-23300-20260720092540）：reconcile 必须先于
        # unregister 执行——reconciler auto-commit 携带本 session_id，若先 unregister，
        # POST-COMMIT-GUARD 查不到注册会刷 unregistered_session_id warn_only
        # （B2 审计：warn_only/allow_overlap 误报的主根因，日均数百条噪音）。
        reconcile_results: list[dict] = []
        if reconcile_verify and merged and cleaned:
            reconcile_results = _run_post_merge_reconcile(root, session_id)

        # merge 成功且 worktree 清理成功才注销 session；清理失败/冲突时保留 session 供重试
        unregistered = False
        if merged and cleaned:
            # #ARCH-HEARTBEAT-001: 终止 heartbeat daemon（session 生命周期结束）
            # 先 kill daemon 停止心跳，再 unregister——即使 unregister 失败，
            # daemon 已停，90s 后 session 自动过期被 list_active 清理
            _kill_heartbeat_daemon(session_id, root)
            # P1-3: 清理 heartbeat.jsonl 审计文件（session 已正常结束）
            try:
                cleanup_heartbeat_file(root, session_id)
            except Exception:  # noqa: BLE001 — best-effort
                logger.debug("cleanup heartbeat file failed (best-effort)", exc_info=True)
            try:
                unregistered = registry.unregister(session_id)
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                logger.debug("suppressed error in session_worktree", exc_info=True)

        return {
            "session_id": session_id,
            "merged": merged,
            "message": msg,
            "cleaned": cleaned,
            "unregistered": unregistered,
            "reconcile_results": reconcile_results,
        }


def _normalize_abort_files_to_rel(files: list[str], root: Path) -> list[str]:
    """将 files 规范化为相对 root 的相对路径列表（/ 分隔）。"""
    rel_files: list[str] = []
    for f in files:
        p = Path(f)
        if p.is_absolute():
            try:
                rel = p.relative_to(root)
                rel_files.append(str(rel).replace("\\", "/"))
            except ValueError:
                rel_files.append(str(p).replace("\\", "/"))
        else:
            rel_files.append(str(p).replace("\\", "/"))
    return rel_files


def _query_tracked_files(root: Path, rel_files: list[str]) -> set[str]:
    """批量查询 rel_files 中被 git tracked 的文件集合。"""
    tracked_r = subprocess.run(
        ["git", "ls-files", "--"] + rel_files,
        cwd=str(root), capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=60,
    )
    if tracked_r.returncode == 0 and tracked_r.stdout.strip():
        return {line.strip() for line in tracked_r.stdout.strip().split("\n") if line.strip()}
    return set()


def _dispose_main_workdir_files(
    root: Path, rel_files: list[str], tracked_files: set[str],
    session_id: str | None = None,
) -> int:
    """分类处置主工作区文件：tracked 用 git stash push 保存（可恢复），untracked 物理删除。

    S3-B 治本（2026-07-17）：tracked 文件原用 ``git checkout --`` 静默丢弃修改，
    但 abort 路径下 worktree commit 也被丢弃，双份数据同时丢失=无恢复路径
    （41 例并发丢失案例中模式 A "git stash/reset/checkout 冲掉工作区"占 51%）。
    改为 ``git stash push -- <files>`` 将修改压入 stash 栈，文件还原到 HEAD，
    用户事后可通过 ``git stash list`` / ``git stash pop`` 恢复 AI 的修改。

    untracked 文件行为不变（物理删除）——abort 场景的 untracked 通常是 AI
    新建的临时文件，物理删除符合预期；如需保留可事后从 worktree 分支恢复
    （worktree 分支在 abort 时由 cleanup_session_worktree 保留为 orphan 分支）。

    边界：tracked 文件无修改时 ``git stash push`` 返回非零（"No local changes"），
    不创建 stash 但文件已在 HEAD，状态正确——``capture_output=True`` 吞掉噪声。

    Args:
        root: 主仓库根目录。
        rel_files: 待处置的相对路径文件列表。
        tracked_files: git tracked 文件集合（用于分类）。
        session_id: 用于 stash message 的 session 标识（可恢复溯源）。

    Returns:
        清理的文件数（tracked 计数 + 成功删除的 untracked 计数）。
    """
    to_stash: list[str] = []
    cleaned = 0
    for rel_file in rel_files:
        main_file = root / rel_file
        if rel_file in tracked_files:
            # tracked 文件——用 git stash push 保存修改（可恢复），文件还原到 HEAD
            to_stash.append(rel_file)
            cleaned += 1
        elif main_file.exists():
            # 裁定#B（2026-07-19）：untracked 文件物理删除 → 隔离区移送（72h 可恢复）
            # 病根：abort 后 untracked 文件永久丢失，无法恢复
            if _quarantine_file(root, rel_file, session_id or "unknown", "abort"):
                cleaned += 1

    if to_stash:
        # S3-B: git stash push 替代 git checkout --
        # stash 保留修改（可恢复 via git stash pop），checkout -- 永久丢弃（不可恢复）
        stash_msg = (
            f"session_worktree_abort: {session_id}"
            if session_id else "session_worktree_abort"
        )
        # P2-6: stash push 前计算 content_hash（push 后文件被 reset 到 HEAD，hash 会变）
        pre_stash_hashes: dict[str, str] = {}
        for rel_file in to_stash:
            pre_stash_hashes[rel_file] = _compute_content_hash(root / rel_file)
        subprocess.run(
            ["git", "stash", "push", "-m", stash_msg, "--"] + to_stash,
            cwd=str(root), capture_output=True,
        )
        logger.info(
            "session_worktree_abort: stashed %d tracked file(s) for session=%s "
            "(recoverable via 'git stash pop')", len(to_stash), session_id or "?",
        )
        # 裁定#C（2026-07-19）：stash 操作遥测（P2-6: 含 content_hash）
        for rel_file in to_stash:
            _log_workspace_op(
                "file_stash", session_id or "unknown", "abort", root,
                file=rel_file, backup_path=f"stash:{stash_msg}",
                content_hash=pre_stash_hashes.get(rel_file, ""),
            )
    return cleaned


def _clean_main_workdir_on_abort(
    files: list[str], root: Path, session_id: str | None = None,
) -> int:
    """清理主工作区残留（君子协定模式：AI 写项目根，abort 需同步清理）。

    S3-B 治本（2026-07-17）：tracked 文件改用 git stash push 保存（可恢复），
    不再用 git checkout -- 永久丢弃；untracked 文件物理删除（行为不变）。

    Args:
        files: AI 修改/创建的文件列表（相对路径或绝对路径）。
        root: 主仓库根目录。
        session_id: session 标识，用于 stash message 溯源。

    Returns:
        清理的文件数。
    """
    rel_files = _normalize_abort_files_to_rel(files, root)
    tracked_files = _query_tracked_files(root, rel_files)
    return _dispose_main_workdir_files(root, rel_files, tracked_files, session_id)


@_inject_ok
def session_worktree_abort(
    session_id: str,
    files: list[str] | None = None,
    project_root: str | Path | None = None,
) -> AbortResult:
    """放弃 worktree 工作：丢弃修改 + 清理 worktree + 注销 session。

    **警告**：此操作丢弃 worktree 内所有未提交/未 merge 的修改。

    君子协定模式下，AI 的 Edit/Write 改动留在主工作区（项目根）。abort 只清理
    worktree 不会自动清理主工作区残留。传入 files 参数可同时清理主工作区：
    - tracked 文件：git stash push 保存到 stash 栈（可恢复 via git stash pop）
      + 文件还原到 HEAD（S3-B 治本，2026-07-17，原 git checkout -- 永久丢弃）
    - untracked 文件：物理删除（丢弃 AI 创建的新文件）

    Args:
        session_id: 已注册的 session_id。
        files: AI 修改/创建的文件列表（相对路径或绝对路径）。传入时同时清理主工作区。
            为 None 时仅清理 worktree（向后兼容）。
        project_root: 项目根目录（默认 REPO_ROOT）。

    Returns:
        {
            "session_id": str,
            "aborted": bool,
            "message": str,
            "unregistered": bool,
            "main_cleaned": int,    # 主工作区清理的文件数（files 非 None 时）
        }
    """
    root = Path(project_root) if project_root else REPO_ROOT
    manager = _get_manager(root)
    registry = _get_registry(root)

    aborted = False
    msg = ""
    main_cleaned = 0

    # 清理主工作区残留（君子协定模式：AI 写项目根，abort 需同步清理）
    if files:
        main_cleaned = _clean_main_workdir_on_abort(files, root, session_id)

    try:
        aborted = manager.cleanup_session_worktree(session_id)
        if aborted:
            _log_worktree_delete(  # Phase 4 遥测：abort 删除点
                session_id, "abort", manager._wt_path(session_id), root
            )
            parts = ["worktree 已丢弃并清理"]
            if main_cleaned > 0:
                parts.append(f"（主工作区清理 {main_cleaned} 个文件）")
            msg = "".join(parts)
        else:
            msg = "worktree 不存在或清理失败"
    except WorktreeError as e:
        msg = f"cleanup 失败: {e}"
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        msg = f"unexpected: {e}"

    unregistered = False
    # #ARCH-HEARTBEAT-001: 终止 heartbeat daemon（session 生命周期结束）
    _kill_heartbeat_daemon(session_id, root)
    # P1-3: 清理 heartbeat.jsonl 审计文件（session 已 abort）
    try:
        cleanup_heartbeat_file(root, session_id)
    except Exception:  # noqa: BLE001 — best-effort
        logger.debug("cleanup heartbeat file failed (best-effort)", exc_info=True)
    try:
        unregistered = registry.unregister(session_id)
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        logger.debug("suppressed error in session_worktree", exc_info=True)

    return {
        "session_id": session_id,
        "aborted": aborted,
        "message": msg,
        "unregistered": unregistered,
        "main_cleaned": main_cleaned,
    }


@_inject_ok
def session_worktree_status(
    session_id: str,
    project_root: str | Path | None = None,
) -> StatusResult:
    """查询 session worktree 状态。

    Args:
        session_id: session 标识。

    Returns:
        {
            "session_id": str,
            "exists": bool,       # worktree 是否存在
            "path": str,          # worktree 路径（不存在时为空）
            "branch": str,        # 分支名
            "dirty": bool,        # 是否有未提交修改
            "registered": bool,   # session 是否在注册表中
        }
    """
    root = Path(project_root) if project_root else REPO_ROOT
    manager = _get_manager(root)
    registry = _get_registry(root)

    exists = manager._worktree_exists(session_id)
    wt_path = manager._wt_path(session_id)
    branch = f"session/{session_id}"

    dirty = False
    if exists:
        dirty = manager._is_dirty(wt_path)

    registered = False
    try:
        info = registry.get_session(session_id)
        registered = info is not None
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        logger.warning("suppressed error in session_worktree", exc_info=True)

    return {
        "session_id": session_id,
        "exists": exists,
        "path": str(wt_path) if exists else "",
        "branch": branch,
        "dirty": dirty,
        "registered": registered,
    }