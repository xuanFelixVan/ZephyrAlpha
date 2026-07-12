# [BLUEPRINT] MOD-GOV-session_worktree | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §FP-ISO.4C
# [MODULE] zephyr.governance.rule_bridge.session_worktree
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] zephyr.governance.rule_bridge.worktree_manager (WorktreeManager); zephyr.security.access_control.session_concurrency (SessionRegistry); zephyr.governance.rule_bridge.session_claim (generate_session_id); scripts.governance.d1_structure.check_directory_contract (subprocess 调用，DCR 检测真源)
# [CONSUMERS] AI 对话启动时调用（AGENTS.md 规则）；scripts/governance/session_worktree_cli.py
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] worktree 物理隔离——每 AI 对话独占 .aidrafts/{session_id}/ worktree，消除共享工作目录导致的 stash 冲突/编辑覆盖/搭便车提交；session_worktree_start 原子注册 session + 创建 worktree（幂等，已存在则复用）；worktree 内 commit 用直接 git add+commit（worktree 有独立 index，无需 GitCommitGateway 共享 index 保护，无需全局锁）；session_worktree_commit 在 HELD-OVERLAP gate 后执行 DCR 检测（subprocess 调用 check_directory_contract.py，fail-closed——对标 GitCommitGateway DIRECTORY-CONTRACT gate，治本 ARCH-041 worktree 绕过 GitCommitGateway 导致 directory_contract 检测不触发）；pre-commit gate 检查（治本 --no-verify 绕过，2026-07-03）：git commit 前 GitCommitGateway._gate_registry.check_all 执行 7 个 worktree-compatible gate（跳过 HELD-OVERLAP/CLAIM-REQUIRED，session_worktree 有自己的 held_files 机制），关键适配——monkeypatch _gw._run_git 重定向 cwd 到 worktree 使 git diff --cached 查 worktree index（否则主仓库 index 返回空 gate 误判），gate 检出违规则 return GATE_VIOLATION 阻断，gate 框架异常降级为 warn 不阻断；merge 回主分支用 WorktreeManager.merge_session_worktree（--no-ff + _WorktreeLock 串行化）；pre-merge gate 检查（治本 merge 前 gate 漂移，2026-07-04）：session_worktree_merge 在 _pre_merge_auto_clean 后执行 _pre_merge_gate_check，用 git reset --soft merge-base 模拟 staged 状态运行 7 个 worktree-compatible gate（捕获 commit 后到 merge 前主分支更新的 gate 规则），gate 阻断则 return merged=False，gate 异常降级为 warn 不阻断，HEAD 用 git reset --soft orig_head 恢复；reconcile_verify 默认 True（2026-07-04）：merge 后自动触发 17 个 reconciler（_run_reconcilers_after_merge），补齐 post-merge 漂移修复（manifest/path_tree/path_ownership/depgraph_ops 等 auto_commit + warn-only）；SessionRegistry 始终用主仓库根目录（非 worktree），确保所有 session 共享一个注册表；所有函数返回 dict 不抛异常；breaking_change 并发阻断（§9.7 治本 2026-07-04）：session_worktree_start 新增 breaking_change/allow_concurrent 参数，在注册 session 之前执行双向阻断——breaking_change=True 检查其他活跃 session（BREAKING_CHANGE_CONCURRENCY_BLOCKED），breaking_change=False 检查其他活跃 breaking_change session（BREAKING_CHANGE_AVOIDANCE_BLOCKED），allow_concurrent=True 逃生通道跳过阻断，异常 fail-open 降级放行
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
    from zephyr.governance.rule_bridge.session_worktree import (
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
    "generate_session_id",
]

import os
import subprocess
import sys
from pathlib import Path

from zephyr.governance.rule_bridge.worktree_manager import (
    WorktreeManager,
    WorktreeError,
    _WorktreeLock,
    _force_rmtree,
)
from zephyr.security.access_control.session_concurrency import SessionRegistry
from zephyr.governance.rule_bridge.session_claim import generate_session_id
from zephyr.shared.io.paths import REPO_ROOT

import logging

logger = logging.getLogger(__name__)

# worktree 路径下跳过的 gate（session_worktree 有自己的 held_files 机制替代
# HELD-OVERLAP/CLAIM-REQUIRED；worktree 物理隔离消除搭便车风险，FOREIGN-CHANGE-DETECTION 无需）。
# session_worktree_commit 和 _pre_merge_gate_check 共用。
_WORKTREE_SKIP_GATES = frozenset({"HELD-OVERLAP", "CLAIM-REQUIRED", "FOREIGN-CHANGE-DETECTION"})


def _get_manager(project_root: str | Path | None = None) -> WorktreeManager:
    """获取 WorktreeManager 实例。"""
    root = Path(project_root) if project_root else REPO_ROOT
    return WorktreeManager(root)


def _get_registry(project_root: str | Path | None = None) -> SessionRegistry:
    """获取 SessionRegistry 实例（始终用主仓库根目录，非 worktree）。"""
    root = Path(project_root) if project_root else REPO_ROOT
    return SessionRegistry(root)


def _sweep_stale_worktrees(
    manager: WorktreeManager,
    registry: SessionRegistry,
    max_age_minutes: int = 30,
) -> dict:
    """启动清扫：清理 .aidrafts/ 下的 stale session worktree 残留。

    在 session_worktree_start 创建自己 worktree 前调用，自动清理两类残留：
    - 孤儿物理目录（git worktree 未注册）—— git 已不认，物理删除
    - 已注册但 session 已过期 + 分支 tip 在 main 的 worktree —— 对话放弃残留

    安全判据（三重保护，任一不满足则跳过）：
    1. 目录 age > max_age_minutes（太新的不动，防误清并发 AI 正在创建的）
    2. session 不在 active 注册表（活跃 session 不动；用 list_active 判定，不依赖 pid）
    3. 分支 tip 在 HEAD 祖先或无分支（有未合并提交的不动，warning 提示人工处理）

    异常不抛出（sweep 失败不阻断 start）。在独立 _WorktreeLock 周期内执行，
    退出锁后 caller 才调 create_session_worktree（避免锁重入死锁）。

    Args:
        manager: WorktreeManager 实例。
        registry: SessionRegistry 实例。
        max_age_minutes: 目录年龄阈值（分钟），默认 30。

    Returns:
        {"swept": int, "skipped": int, "warnings": list[str]}
    """
    import time as _time

    swept = 0
    skipped = 0
    warnings: list[str] = []
    drafts = manager._drafts_dir
    if not drafts.exists():
        return {"swept": 0, "skipped": 0, "warnings": []}

    now = _time.time()
    age_threshold = max_age_minutes * 60

    # 活跃 session（list_active 已 reap 过期条目，返回的即活跃；不依赖 pid）
    # list_active 返回 list[SessionInfo]（非 dict），提取 session_id 集合
    try:
        active_list = registry.list_active()
        active_sids = {getattr(info, "session_id", "") for info in active_list}
    except Exception:
        active_sids = set()

    try:
        with _WorktreeLock(manager.repo_root):
            for d in drafts.iterdir():
                if not d.is_dir() or not d.name.startswith("sess-"):
                    continue
                sid = d.name
                # 判据 1：age（太新的不动，防误清并发 AI 正在创建的）
                try:
                    mtime = d.stat().st_mtime
                except OSError:
                    skipped += 1
                    continue
                if (now - mtime) < age_threshold:
                    skipped += 1
                    continue
                # 判据 2：活跃 session
                if sid in active_sids:
                    skipped += 1
                    continue
                # 判据 3：分支 tip 在 main（有未合并提交的不动）
                branch = manager._branch_name(sid)
                r_v = manager._run_git(["git", "rev-parse", "--verify", branch])
                has_branch = r_v.returncode == 0
                if has_branch:
                    r_mb = manager._run_git(
                        ["git", "merge-base", "--is-ancestor", branch, "HEAD"]
                    )
                    if r_mb.returncode != 0:
                        warnings.append(
                            f"{sid}: 分支有未合并提交，需人工评估（已跳过）"
                        )
                        skipped += 1
                        continue
                # 通过三重保护——清理
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
                    except Exception as e:
                        logger.warning("suppressed error in session_worktree", exc_info=True)
                    swept += 1
                    logger.info(
                        "session_worktree sweep: 清理 stale %s (registered=%s)",
                        sid, is_registered,
                    )
                except Exception as e:
                    warnings.append(f"{sid}: 清理异常 {e}")
                    skipped += 1
    except Exception as e:
        warnings.append(f"sweep 整体异常（已中止）: {e}")

    return {"swept": swept, "skipped": skipped, "warnings": warnings}


def session_worktree_start(
    session_id: str | None = None,
    project_root: str | Path | None = None,
    breaking_change: bool = False,
    allow_concurrent: bool = False,
) -> dict:
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

    Returns:
        {
            "session_id": str,
            "worktree_path": str,      # worktree 绝对路径，AI 后续文件操作 MUST 用此路径前缀
            "branch": str,             # 分支名 session/{session_id}
            "registered": bool,        # session 是否注册成功
            "created": bool,           # worktree 是否新建（False=已存在复用）
        }
        失败时附加 "error" 字段 + "blocked_by" 字段（阻断方 session_id）。
    """
    sid = session_id or generate_session_id()
    root = Path(project_root) if project_root else REPO_ROOT

    # 0. 治本变更并发阻断（§9.7 治本，2026-07-04）
    #    双向阻断：breaking_change session 阻止其他 session，普通 session 避让 breaking_change session
    #    逃生通道：allow_concurrent=True 跳过阻断（对标 allow_overlap）
    if not allow_concurrent:
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
                            f"（AGENTS.md L391/L394）。当前活跃 session: {other_ids}。"
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
                            f" 声明了 breaking_change（治本变更进行中，AGENTS.md L391/L394）。"
                            f"逃生通道：allow_concurrent=True。"
                        ),
                        "blocked_by": [blocker.session_id],
                    }
        except Exception as e:
            # fail-open：并发检测异常不阻断 start（对标 held_overlap_gate fail-open）
            logger.warning("session_worktree_start: 并发检测异常（降级放行）: %s", e, exc_info=True)

    # 1. 注册 session（held_files 留空——worktree 模式下文件隔离由 worktree 物理保证，
    #    不依赖 held_files claim 机制）
    registry = _get_registry(root)
    registered = False
    try:
        registry.register(sid, pid=os.getpid(), held_files=[], is_breaking_change=breaking_change)
        registered = True
    except Exception as e:
        return {
            "session_id": sid,
            "worktree_path": "",
            "branch": "",
            "registered": False,
            "created": False,
            "error": f"register session failed: {e}",
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
    except Exception as e:
        logger.warning("session_worktree sweep 异常（不阻断 start）: %s", e, exc_info=True)
    try:
        # 检测是否已存在（幂等）
        wt_path = manager._wt_path(sid)
        already_exists = manager._worktree_exists(sid)
        if not already_exists:
            manager.create_session_worktree(sid)
            created = True
        else:
            created = False
        return {
            "session_id": sid,
            "worktree_path": str(wt_path),
            "branch": f"session/{sid}",
            "registered": registered,
            "created": created,
        }
    except WorktreeError as e:
        return {
            "session_id": sid,
            "worktree_path": "",
            "branch": f"session/{sid}",
            "registered": registered,
            "created": False,
            "error": f"create worktree failed: {e}",
        }
    except Exception as e:
        return {
            "session_id": sid,
            "worktree_path": "",
            "branch": f"session/{sid}",
            "registered": registered,
            "created": False,
            "error": f"unexpected: {e}",
        }


def session_worktree_commit(
    session_id: str,
    files: list[str],
    message: str,
    project_root: str | Path | None = None,
    allow_overlap: bool = False,
    allow_promote: bool = False,
    allow_migration: bool = False,
) -> dict:
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

    # 检测 worktree 是否存在
    if not manager._worktree_exists(session_id):
        return {
            "session_id": session_id,
            "status": "FAILED",
            "message": f"worktree 不存在 (session={session_id})，先调 session_worktree_start",
            "commit_hash": "",
            "not_found": True,
        }

    wt_path = manager._wt_path(session_id)

    # 心跳续期（commit 时顺带续期，防 TTL 过期）
    try:
        _get_registry(root).heartbeat(session_id)
    except Exception:
        pass  # 心跳失败不阻断 commit

    # git add（在 worktree 内执行）
    if not files:
        return {
            "session_id": session_id,
            "status": "NOTHING_TO_COMMIT",
            "message": "empty files list",
            "commit_hash": "",
        }

    # 归一化文件路径为相对 worktree 的路径（git add 在 worktree cwd 下执行）
    rel_files: list[str] = []
    for f in files:
        p = Path(f)
        if p.is_absolute():
            try:
                rel = p.relative_to(wt_path)
                rel_files.append(str(rel).replace("\\", "/"))
            except ValueError:
                # 不在 worktree 内的绝对路径——可能是主仓库路径，转换为 worktree 内等价路径
                try:
                    rel_to_root = p.relative_to(root)
                    rel_files.append(str(rel_to_root).replace("\\", "/"))
                except ValueError:
                    rel_files.append(str(p).replace("\\", "/"))
        else:
            rel_files.append(str(p).replace("\\", "/"))

    # HELD-OVERLAP 硬阻断 + auto-claim（2026-07-02 加硬）
    # 对标 GitCommitGateway 的 HELD-OVERLAP gate，使 worktree 模式下的文件锁一样硬。
    # 原子 check-and-claim（claim_file 内部加锁，防 TOCTOU 竞态）：
    #   - 文件被其他活跃 session 持有 -> claim_file 返回 False -> 硬阻断
    #   - 文件未被持有或已被自己持有 -> claim_file 返回 True -> claim 成功
    # claim 是 session 级（不 per-commit 释放），merge/abort 时 unregister 自动释放。
    # allow_overlap=True 时跳过检查（逃生通道，对标 GitCommitGateway --allow-overlap）。
    if not allow_overlap:
        registry = _get_registry(root)
        claimed_files: list[str] = []  # 已成功 claim（失败时回滚）
        overlap_files: list[str] = []  # 被其他 session 持有的文件
        for rf in rel_files:
            try:
                if registry.claim_file(session_id, rf):
                    claimed_files.append(rf)
                else:
                    overlap_files.append(rf)
            except Exception:
                pass  # claim 异常时 best-effort 继续（不阻断）

        if overlap_files:
            # 回滚已 claim 的文件（避免 dangling claim 阻塞其他 session）
            for cf in claimed_files:
                try:
                    registry.release_file(session_id, cf)
                except Exception as e:
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

    # ── DCR 检测（对标 GitCommitGateway 的 DIRECTORY-CONTRACT gate）──────────
    # 治本(ARCH-041): session_worktree_commit 绕过 GitCommitGateway，导致 directory_contract
    # 检测（含 _backups 禁止、DCR-001~007）不触发。此处补强，subprocess 调用真源
    # check_directory_contract.py，fail-closed（checker 缺失/超时也阻断）。
    # 与 directory_contract_gate.py L78-137 保持一致（复用真源，禁止复制 DCR 逻辑）。
    check_script = root / "scripts" / "governance" / "d1_structure" / "check_directory_contract.py"
    if not check_script.is_file():
        return {
            "session_id": session_id,
            "status": "FAILED",
            "message": f"check_directory_contract.py not found: {check_script} (fail-closed)",
            "commit_hash": "",
            "directory_contract_violation": True,
        }
    # 文件数过多时改用 --all-files（避免 WinError 206 命令行长度限制）
    _MAX_INLINE_FILES = 200
    if len(rel_files) > _MAX_INLINE_FILES:
        dcr_cmd = [sys.executable, str(check_script), "--all-files"]
    else:
        dcr_cmd = [sys.executable, str(check_script)] + rel_files
    try:
        dcr_result = subprocess.run(
            dcr_cmd, capture_output=True, cwd=str(root), timeout=60,
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
    # ── DCR 检测结束 ──────────────────────────────────────────────────────

    # 同步主工作区改动到 worktree（君子协定模式：AI 的 Edit/Write 写在项目根，
    # worktree 内文件是创建时的旧版本，需同步才能 stage 到最新内容）
    # 覆盖三种场景：文件修改/新增（copy2 同步）+ 文件删除（unlink 同步删除）
    # + 直接写入 worktree 的新文件（未跟踪，不删除）
    import shutil

    # 批量查询哪些 rel_file 是 git 跟踪的（区分"跟踪文件被删除"vs"直接写入 worktree 的新文件"）
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
                # 内容比较——治本(2026-07-05): 替代 mtime 比较逻辑
                # 原因：mtime 比较依赖文件系统元数据，受 copy2 保留 mtime/touch/git checkout
                # 影响，导致同步缺失 bug（commit 1877f8df06 仅 L6 入库，L1/L15 丢失）。
                # 内容比较 100% 可靠，代码文件 <100KB 时 I/O <1ms 可忽略。
                # 设计依据：AGENTS.md L392"Edit/Write 工作区固定为项目根"——
                # AI 不会直接编辑 worktree，mtime 保护场景在设计上不存在。
                try:
                    if src.read_bytes() == dst.read_bytes():
                        continue  # 内容相同，无需复制
                except OSError:
                    pass  # 读取失败则走默认 copy2（安全降级）
            # dst 不存在 或 内容不同——同步最新内容到 worktree（正常情况：AI 写项目根）
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(str(src), str(dst))
        elif not src.exists() and dst.exists() and rel_file in tracked_files:
            # 文件在主工作区被删除且被 git 跟踪——同步删除到 worktree（物理删除，
            # 后续 git add -A 会 stage 删除操作）
            # 排除直接写入 worktree 的未跟踪新文件（src 不存在但 dst 存在且未跟踪）
            try:
                dst.unlink()
            except OSError:
                try:
                    # 只读文件兜底：清除只读位后重试
                    os.chmod(str(dst), 0o644)
                    dst.unlink()
                except OSError:
                    # gitlink/special file 无法 unlink，用 git rm --cached stage 删除
                    subprocess.run(
                        ["git", "rm", "--cached", "--", rel_file],
                        cwd=str(wt_path), capture_output=True, timeout=30,
                    )

    # git add -A 同时 stage 新增/修改/删除（替代原 git add，确保文件删除被 stage）
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

    # 检查是否有 staged 改动
    diff_r = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        cwd=str(wt_path), capture_output=True, timeout=30,
    )
    if diff_r.returncode == 0:
        # 无 staged 改动
        return {
            "session_id": session_id,
            "status": "NOTHING_TO_COMMIT",
            "message": "no staged changes after git add",
            "commit_hash": "",
        }

    # ── pre-commit gate 检查（治本 --no-verify 绕过，对标 GitCommitGateway）──
    # session_worktree 用 --no-verify 绕过 git pre-commit hook，且绕过 GitCommitGateway。
    # 但文件内容/路径类 gate 不能绕过——在 commit 前执行 7 个 worktree-compatible gate。
    # 跳过 HELD-OVERLAP/CLAIM-REQUIRED（session_worktree 有自己的 held_files 机制，见 L332-337）。
    #
    # 关键适配：gate 的 git 命令（git diff --cached 等）默认在主仓库 root 执行，但
    # worktree 模式下文件 staged 在 worktree index——主仓库 git diff --cached 返回空，
    # gate 误判无新文件。修复：临时 monkeypatch _run_git 重定向 cwd 到 worktree，
    # 使 git 命令查 worktree index；文件路径操作仍用 gateway.project_root（主仓库路径）。
    #
    # 降级策略：gate 基础设施异常降级为 warn（不卡死 commit）；gate 检出违规则阻断。
    # 治本第1期前置依赖（architecture_debt_registry.md §六 第1期）：确保新 AST 门禁
    # 注册到 commit_gate_registry 后，worktree 路径也生效，不被 --no-verify 绕过。
    try:
        from zephyr.governance.rule_bridge.git_commit_gateway import (
            GitCommitGateway, _GATEWAY_ENV,
        )
        _gw = GitCommitGateway(project_root=root)
        # 临时让 git 命令在 worktree 内执行（查 worktree index 的 staged 状态）
        _orig_run_git = _gw._run_git

        def _wt_run_git(cmd, cwd=None, _wt=str(wt_path), _env_var=_GATEWAY_ENV):
            _env = os.environ.copy()
            _env[_env_var] = "1"
            # 阻断 git commit（同 _run_git 守卫，gate 检查不应触发 commit）
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
            )
        finally:
            _gw._run_git = _orig_run_git
        _skip_gates = _WORKTREE_SKIP_GATES
        if allow_migration:
            # P14 fix (2026-07-13): 迁移场景跳过 FILE-COPY（迁移文件天然与旧路径
            # 同名文件高度相似）、ORPHAN-MODULE（迁移过程中 import 引用可能尚未
            # 完全更新）和 TEST-SOURCE-CONSISTENCY（worktree 环境下模块路径检测
            # 误报）。仅限合法迁移操作使用。
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
    except Exception as _e:
        # gate 基础设施异常降级为 warn（不阻断）——session_worktree 不应因 gate 框架
        # 自身 bug 卡死业务流程；gate 检出违规则由上方 return 阻断。
        logger.warning("session_worktree_commit: gate 检查异常降级（不阻断）: %s", _e, exc_info=True)

    # git commit（用 -F 从临时文件读 message，避免 PowerShell 特殊字符问题，对标 RULE-TWENTY 裁定2）
    # --no-verify: 绕过 git pre-commit hooks（hook 已由上方 commit_gate_registry 检查替代）。
    import tempfile
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".msg", delete=False, encoding="utf-8"
    ) as msg_file:
        msg_file.write(f"{message}\n\n[GW:{session_id}:worktree]")
        msg_file_path = msg_file.name
    try:
        commit_cmd = ["git", "commit", "--no-verify", "-F", msg_file_path]
        commit_r = subprocess.run(
            commit_cmd, cwd=str(wt_path), capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=120,
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

    # 获取 commit SHA
    sha_r = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],
        cwd=str(wt_path), capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=30,
    )
    commit_hash = sha_r.stdout.strip() if sha_r.returncode == 0 else ""

    return {
        "session_id": session_id,
        "status": "OK",
        "message": "committed in worktree",
        "commit_hash": commit_hash,
    }


def _pre_merge_auto_clean(root: Path, session_id: str) -> tuple[int, list[str]]:
    """Pre-merge 自动清理：消除 merge 失败根因，处理两类冗余文件。

    场景1（tracked dirty）：AI 的 Edit 改动留在主工作区（uncommitted），
    session_worktree_commit 同步到 worktree 并 commit。这些未提交改动与 worktree
    commit 内容一致，merge 时触发 "Your local changes would be overwritten by merge"。
    修复：内容一致时 git checkout -- 还原到 HEAD（merge 会重新带入）。

    场景2（untracked new file）：AI 用 Write 创建新文件留在主工作区（untracked），
    session_worktree_commit 复制到 worktree 并 commit。merge 时 git 拒绝覆盖 untracked
    文件（"untracked working tree files would be overwritten by merge"）。
    修复：内容一致时物理删除 untracked 文件（merge 会重新创建）。

    两类场景都只清理内容完全一致的文件（safe）；内容不一致的跳过（AI 有额外编辑）。

    Args:
        root: 主仓库根目录。
        session_id: session 标识。

    Returns:
        (cleaned_count, skipped_files) 元组：
        - cleaned_count: 自动清理的文件数
        - skipped_files: 内容不一致或无法比较，跳过的文件列表
    """
    branch = f"session/{session_id}"

    # 1. 获取 worktree branch 相对 merge-base 的变更文件列表
    merge_base_r = subprocess.run(
        ["git", "merge-base", "HEAD", branch],
        cwd=str(root), capture_output=True, text=True, encoding="utf-8",
    )
    if merge_base_r.returncode != 0:
        return 0, []
    merge_base = merge_base_r.stdout.strip()

    changed_r = subprocess.run(
        ["git", "diff", "--name-only", f"{merge_base}..{branch}"],
        cwd=str(root), capture_output=True, text=True, encoding="utf-8",
    )
    if changed_r.returncode != 0:
        return 0, []
    changed_files = [f.strip() for f in changed_r.stdout.strip().split("\n") if f.strip()]

    if not changed_files:
        return 0, []

    # 2. 获取主工作区有未提交改动的文件（staged + unstaged，相对 HEAD）
    dirty_r = subprocess.run(
        ["git", "diff", "--name-only", "HEAD"],
        cwd=str(root), capture_output=True, text=True, encoding="utf-8",
    )
    if dirty_r.returncode != 0:
        return 0, []
    dirty_files = set(f.strip() for f in dirty_r.stdout.strip().split("\n") if f.strip())

    # 3. 对同时在 changed_files 和 dirty_files 中的文件，比较内容
    cleaned = 0
    skipped: list[str] = []
    to_checkout: list[str] = []

    for rel_file in changed_files:
        if rel_file not in dirty_files:
            continue  # 主工作区没有未提交改动，无需清理

        main_file = root / rel_file
        if not main_file.exists():
            # 文件在主工作区被删除——无法比较内容，跳过（删除同步由 commit 处理）
            skipped.append(rel_file)
            continue

        # 比较主工作区内容与 worktree branch HEAD 内容
        main_content = main_file.read_bytes()
        wt_content_r = subprocess.run(
            ["git", "show", f"{branch}:{rel_file}"],
            cwd=str(root), capture_output=True,
        )
        if wt_content_r.returncode != 0:
            # worktree branch 中没有该文件——跳过
            skipped.append(rel_file)
            continue

        if main_content == wt_content_r.stdout:
            # 内容一致——安全 checkout（discard 冗余的未提交改动）
            to_checkout.append(rel_file)
            cleaned += 1
        else:
            # 内容不一致——AI 可能做了额外编辑，不自动清理
            skipped.append(rel_file)

    # 3b. 处理 untracked 文件（worktree branch 新增的文件在主工作区可能作为 untracked 存在）
    # 场景：AI 用 Write 创建新文件 -> session_worktree_commit 复制到 worktree 并 commit
    # -> 主工作区文件仍为 untracked -> merge 时 git 拒绝覆盖 untracked 文件
    # 修复：untracked 文件内容与 worktree branch 一致时，物理删除让 merge 可以创建
    untracked_r = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard"],
        cwd=str(root), capture_output=True, text=True, encoding="utf-8",
    )
    to_unlink: list[str] = []
    if untracked_r.returncode == 0 and untracked_r.stdout.strip():
        untracked_files = {f.strip() for f in untracked_r.stdout.strip().split("\n") if f.strip()}
        for rel_file in changed_files:
            if rel_file not in untracked_files:
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

    # 4. 批量 checkout tracked dirty 文件 + 删除 untracked 文件
    if to_checkout:
        subprocess.run(
            ["git", "checkout", "--"] + to_checkout,
            cwd=str(root), capture_output=True,
        )
    for rel_file in to_unlink:
        try:
            (root / rel_file).unlink()
        except OSError:
            try:
                os.chmod(str(root / rel_file), 0o644)
                (root / rel_file).unlink()
            except OSError:
                pass  # 尽力而为

    return cleaned, skipped


def _get_merge_files(root: Path) -> list[str]:
    """获取最近一次 merge 引入的文件列表（git diff HEAD~1 HEAD --name-only）。"""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD~1", "HEAD"],
            cwd=str(root), capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0 and result.stdout.strip():
            return [f.strip() for f in result.stdout.strip().split("\n") if f.strip()]
    except Exception as e:
        logger.warning("suppressed error in session_worktree", exc_info=True)
    return []


def _run_reconcilers_after_merge(
    committed_files: list[str], session_id: str, root: Path
) -> list[dict]:
    """merge 后触发 reconciler（补齐 worktree 路径的 reconciler 验证）。

    创建临时 GitCommitGateway 实例，调用 reconcile_for 触发默认 17 个 reconciler。
    reconciler 的 auto-commit 通过 gateway._commit_auto 处理（防递归已内置）。
    """
    try:
        from zephyr.governance.rule_bridge.git_commit_gateway import GitCommitGateway
        gateway = GitCommitGateway(project_root=root)
        results = gateway._reconciliation_registry.reconcile_for(committed_files, session_id)
        summary = []
        for r in results:
            if r.action == "skip":
                continue
            summary.append({"action": r.action, "detail": r.detail})
            print(f"[RECONCILER] {r.action}" + (f" - {r.detail}" if r.detail else ""))
        return summary
    except Exception as e:
        print(f"[RECONCILER] 触发失败: {e}")
        return [{"action": "warn", "detail": str(e)}]


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

    Returns:
        (passed, violations) —— passed=True 放行 merge，passed=False 阻断。
    """
    try:
        from zephyr.governance.rule_bridge.git_commit_gateway import (
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
        reset_r = subprocess.run(
            ["git", "reset", "--soft", merge_base],
            cwd=str(wt_path), capture_output=True, text=True, timeout=30,
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
                _gw._run_git = _orig_run_git

            _skip_gates = _WORKTREE_SKIP_GATES
            if allow_migration:
                _skip_gates = _skip_gates | frozenset({"FILE-COPY", "ORPHAN-MODULE", "TEST-SOURCE-CONSISTENCY"})
            _blocking = [
                gr for gr in _gate_results
                if not gr.passed and gr.gate_id not in _skip_gates
            ]
            if _blocking:
                return False, [
                    {"gate_id": gr.gate_id, "detail": gr.detail} for gr in _blocking
                ]
            return True, []
        finally:
            # 恢复 HEAD（git reset --soft orig_head：HEAD 移回原 commit，index 不变=干净状态）
            subprocess.run(
                ["git", "reset", "--soft", orig_head],
                cwd=str(wt_path), capture_output=True, text=True, timeout=30,
            )
    except Exception as _e:
        # gate 基础设施异常降级为 warn（不阻断）
        logger.warning("pre-merge gate 检查异常降级（不阻断）: %s", _e, exc_info=True)
        return True, []


def session_worktree_merge(
    session_id: str,
    project_root: str | Path | None = None,
    reconcile_verify: bool = True,
    allow_migration: bool = False,
) -> dict:
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

    # Pre-merge: 自动清理与 worktree commit 内容一致的未提交改动（消除 merge 失败根因）
    # 只清理内容一致的文件（safe）；内容不一致的跳过（AI 有额外编辑，需手动处理）
    auto_cleaned, skipped_files = _pre_merge_auto_clean(root, session_id)

    # Pre-merge gate 检查（裁定#209 后续：补齐 worktree 路径的 gate 验证）
    # 用最新主分支状态重新检查 session 分支变更，捕获 commit 后到 merge 前的 gate 漂移
    wt_path = manager._wt_path(session_id)
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

    merged = False
    cleaned = False
    msg = ""

    try:
        merged = manager.merge_session_worktree(session_id, delete_after=True)
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
        else:
            if skipped_files:
                msg = (
                    f"merge 失败：以下文件主工作区有额外改动（与 worktree commit 不一致），"
                    f"请手动处理：{skipped_files}"
                )
            else:
                msg = "merge 冲突，worktree 保留供手动解决（解决后重新调 merge 或手动 cleanup）"
    except WorktreeError as e:
        msg = f"merge 失败: {e}"
    except Exception as e:
        msg = f"unexpected: {e}"

    # merge 成功且 worktree 清理成功才注销 session；清理失败/冲突时保留 session 供重试
    unregistered = False
    if merged and cleaned:
        try:
            unregistered = registry.unregister(session_id)
        except Exception as e:
            logger.debug("suppressed error in session_worktree", exc_info=True)

    # 裁定#209 后续：merge 后可选触发 reconciler（补齐 worktree 路径的验证）
    reconcile_results: list[dict] = []
    if reconcile_verify and merged and cleaned:
        try:
            committed_files = _get_merge_files(root)
            if committed_files:
                print(f"[RECONCILER] merge 后触发 reconciler 验证（{len(committed_files)} 个文件）...")
                reconcile_results = _run_reconcilers_after_merge(committed_files, session_id, root)
            else:
                print("[RECONCILER] 无变更文件，跳过 reconciler")
        except Exception as e:
            print(f"[RECONCILER] 触发失败: {e}")
            reconcile_results = [{"action": "warn", "detail": str(e)}]

    return {
        "session_id": session_id,
        "merged": merged,
        "message": msg,
        "cleaned": cleaned,
        "unregistered": unregistered,
        "reconcile_results": reconcile_results,
    }


def session_worktree_abort(
    session_id: str,
    files: list[str] | None = None,
    project_root: str | Path | None = None,
) -> dict:
    """放弃 worktree 工作：丢弃修改 + 清理 worktree + 注销 session。

    **警告**：此操作丢弃 worktree 内所有未提交/未 merge 的修改。

    君子协定模式下，AI 的 Edit/Write 改动留在主工作区（项目根）。abort 只清理
    worktree 不会自动清理主工作区残留。传入 files 参数可同时清理主工作区：
    - tracked 文件：git checkout -- 恢复到 HEAD（丢弃 AI 的修改）
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

        # 批量查询 tracked 文件
        tracked_r = subprocess.run(
            ["git", "ls-files", "--"] + rel_files,
            cwd=str(root), capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=60,
        )
        tracked_files: set[str] = set()
        if tracked_r.returncode == 0 and tracked_r.stdout.strip():
            tracked_files = {line.strip() for line in tracked_r.stdout.strip().split("\n") if line.strip()}

        to_checkout: list[str] = []
        for rel_file in rel_files:
            main_file = root / rel_file
            if rel_file in tracked_files:
                # tracked 文件——用 git checkout 恢复到 HEAD（仅当有改动时才需要）
                to_checkout.append(rel_file)
                main_cleaned += 1
            elif main_file.exists():
                # untracked 文件——物理删除
                try:
                    main_file.unlink()
                    main_cleaned += 1
                except OSError:
                    try:
                        os.chmod(str(main_file), 0o644)
                        main_file.unlink()
                        main_cleaned += 1
                    except OSError:
                        pass  # 尽力而为

        if to_checkout:
            subprocess.run(
                ["git", "checkout", "--"] + to_checkout,
                cwd=str(root), capture_output=True,
            )

    try:
        aborted = manager.cleanup_session_worktree(session_id)
        if aborted:
            parts = ["worktree 已丢弃并清理"]
            if main_cleaned > 0:
                parts.append(f"（主工作区清理 {main_cleaned} 个文件）")
            msg = "".join(parts)
        else:
            msg = "worktree 不存在或清理失败"
    except WorktreeError as e:
        msg = f"cleanup 失败: {e}"
    except Exception as e:
        msg = f"unexpected: {e}"

    unregistered = False
    try:
        unregistered = registry.unregister(session_id)
    except Exception as e:
        logger.debug("suppressed error in session_worktree", exc_info=True)

    return {
        "session_id": session_id,
        "aborted": aborted,
        "message": msg,
        "unregistered": unregistered,
        "main_cleaned": main_cleaned,
    }


def session_worktree_status(
    session_id: str,
    project_root: str | Path | None = None,
) -> dict:
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
    except Exception as e:
        logger.warning("suppressed error in session_worktree", exc_info=True)

    return {
        "session_id": session_id,
        "exists": exists,
        "path": str(wt_path) if exists else "",
        "branch": branch,
        "dirty": dirty,
        "registered": registered,
    }