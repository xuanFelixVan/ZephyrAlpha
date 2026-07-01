# [BLUEPRINT] MOD-GOV-session_worktree | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §FP-ISO.4C
# [MODULE] zephyr.governance.rule_bridge.session_worktree
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.rule_bridge.worktree_manager (WorktreeManager); zephyr.security.access_control.session_concurrency (SessionRegistry); zephyr.governance.rule_bridge.session_claim (generate_session_id)
# [CONSUMERS] AI 对话启动时调用（AGENTS.md 规则）；scripts/governance/session_worktree_cli.py
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] worktree 物理隔离——每 AI 对话独占 .aidrafts/{session_id}/ worktree，消除共享工作目录导致的 stash 冲突/编辑覆盖/搭便车提交；session_worktree_start 原子注册 session + 创建 worktree（幂等，已存在则复用）；worktree 内 commit 用直接 git add+commit（worktree 有独立 index，无需 GitCommitGateway 共享 index 保护，无需全局锁）；merge 回主分支用 WorktreeManager.merge_session_worktree（--no-ff + _WorktreeLock 串行化）；SessionRegistry 始终用主仓库根目录（非 worktree），确保所有 session 共享一个注册表；所有函数返回 dict 不抛异常
# [MODIFY-GUARD] worktree 路径前缀 .aidrafts/；分支命名前缀 session/；worktree 内 commit 绕过 GitCommitGateway 的设计决策
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 所有函数返回 dict（不抛异常）；WorktreeManager/SessionRegistry 异常时返回 error 字段；worktree 不存在时返回 not_found=True
# [TESTS] tests/governance/rule_enforcement/test_session_worktree.py
# [A_module] module_id=MOD-GOV-session_worktree | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""session_worktree.py — AI 对话 worktree 物理隔离 helper（FP-ISO.4C，2026-07-01 治本）

41 个并发丢失案例分析结论：模式 A（git stash/reset/checkout 冲掉工作区）占 51%，
模式 B（直接编辑同一文件覆盖）占 17%，模式 D（未 commit 被回收）占 7%。唯一能
同时治 A+B+D 的方案是 worktree 物理隔离——每 AI 对话独占一个 git worktree，
从物理层面消除共享工作目录冲突。

本模块是 AI 侧的一体化生命周期 helper，封装 WorktreeManager + SessionRegistry，
提供 start/commit/merge/abort/status 五个函数，全部返回 dict（不抛异常），
适配 Trae IDE「AI 对话触发并发工作」模式。

核心工作流（AI 对话生命周期）::

    1. 对话启动 → session_worktree_start(session_id)
       → 注册 session + 创建 worktree
       → 返回 worktree_path，AI 后续所有文件操作 MUST 用此路径下的绝对路径
    2. 在 worktree 内编辑文件（Read/Edit/Write 用 worktree_path 前缀）
    3. 提交 → session_worktree_commit(session_id, files, message)
       → worktree 内直接 git add + commit（独立 index，无需 GitCommitGateway）
    4. 任务完成 → session_worktree_merge(session_id)
       → merge 回主分支 + 清理 worktree + 注销 session
    5. 放弃任务 → session_worktree_abort(session_id)
       → 丢弃修改 + 清理 worktree + 注销 session

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
from pathlib import Path

from zephyr.governance.rule_bridge.worktree_manager import WorktreeManager, WorktreeError
from zephyr.security.access_control.session_concurrency import SessionRegistry
from zephyr.governance.rule_bridge.session_claim import generate_session_id
from zephyr.shared.io.paths import REPO_ROOT


def _get_manager(project_root: str | Path | None = None) -> WorktreeManager:
    """获取 WorktreeManager 实例。"""
    root = Path(project_root) if project_root else REPO_ROOT
    return WorktreeManager(root)


def _get_registry(project_root: str | Path | None = None) -> SessionRegistry:
    """获取 SessionRegistry 实例（始终用主仓库根目录，非 worktree）。"""
    root = Path(project_root) if project_root else REPO_ROOT
    return SessionRegistry(root)


def session_worktree_start(
    session_id: str | None = None,
    project_root: str | Path | None = None,
) -> dict:
    """AI 对话启动第一步：注册 session + 创建独立 worktree。

    原子操作：先注册 session（SessionRegistry），再创建 worktree（WorktreeManager）。
    幂等：若 worktree 已存在，直接复用并返回其路径。

    Args:
        session_id: session 标识。为 None 时自动用 generate_session_id() 生成。
        project_root: 项目根目录（默认 REPO_ROOT）。

    Returns:
        {
            "session_id": str,
            "worktree_path": str,      # worktree 绝对路径，AI 后续文件操作 MUST 用此路径前缀
            "branch": str,             # 分支名 session/{session_id}
            "registered": bool,        # session 是否注册成功
            "created": bool,           # worktree 是否新建（False=已存在复用）
        }
        失败时附加 "error" 字段。
    """
    sid = session_id or generate_session_id()
    root = Path(project_root) if project_root else REPO_ROOT

    # 1. 注册 session（held_files 留空——worktree 模式下文件隔离由 worktree 物理保证，
    #    不依赖 held_files claim 机制）
    registry = _get_registry(root)
    registered = False
    try:
        registry.register(sid, pid=os.getpid(), held_files=[])
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
) -> dict:
    """在 worktree 内提交修改（直接 git add + commit，绕过 GitCommitGateway）。

    worktree 有独立 git index，session 独占整个 worktree，不存在共享冲突，
    无需 GitCommitGateway 的门禁保护和全局锁。

    Args:
        session_id: 已注册的 session_id（必须有对应 worktree）。
        files: 要提交的文件列表。路径可以是绝对的（worktree 内）或相对 worktree 的。
        message: commit message。
        project_root: 项目根目录（默认 REPO_ROOT）。

    Returns:
        {
            "session_id": str,
            "status": "OK" | "NOTHING_TO_COMMIT" | "FAILED",
            "message": str,
            "commit_hash": str,   # 成功时为短 SHA，否则空
        }
        worktree 不存在时附加 "not_found": True。
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

    add_cmd = ["git", "add", "--"] + rel_files
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

    # git commit（用 -F 从临时文件读 message，避免 PowerShell 特殊字符问题，对标 RULE-TWENTY 裁定2）
    # --no-verify: 绕过 pre-commit hooks（与 GitCommitGateway 一致）。
    # worktree 有独立 index 无共享冲突，gate 检查在 merge 回主分支时生效。
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


def session_worktree_merge(
    session_id: str,
    project_root: str | Path | None = None,
) -> dict:
    """将 worktree 修改 merge 回主分支 + 清理 worktree + 注销 session。

    在主工作目录执行 git merge session/{session_id} --no-ff（保留 session 提交拓扑）。
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

    merged = False
    cleaned = False
    msg = ""

    try:
        merged = manager.merge_session_worktree(session_id, delete_after=True)
        if merged:
            msg = "merge 成功，worktree 已清理"
            cleaned = True
        else:
            msg = "merge 冲突，worktree 保留供手动解决（解决后重新调 merge 或手动 cleanup）"
    except WorktreeError as e:
        msg = f"merge 失败: {e}"
    except Exception as e:
        msg = f"unexpected: {e}"

    # merge 成功才注销 session；冲突时保留 session 供重试
    unregistered = False
    if merged:
        try:
            unregistered = registry.unregister(session_id)
        except Exception:
            pass

    return {
        "session_id": session_id,
        "merged": merged,
        "message": msg,
        "cleaned": cleaned,
        "unregistered": unregistered,
    }


def session_worktree_abort(
    session_id: str,
    project_root: str | Path | None = None,
) -> dict:
    """放弃 worktree 工作：丢弃修改 + 清理 worktree + 注销 session。

    **警告**：此操作丢弃 worktree 内所有未提交/未 merge 的修改。

    Args:
        session_id: 已注册的 session_id。

    Returns:
        {
            "session_id": str,
            "aborted": bool,
            "message": str,
            "unregistered": bool,
        }
    """
    root = Path(project_root) if project_root else REPO_ROOT
    manager = _get_manager(root)
    registry = _get_registry(root)

    aborted = False
    msg = ""

    try:
        aborted = manager.cleanup_session_worktree(session_id)
        if aborted:
            msg = "worktree 已丢弃并清理"
        else:
            msg = "worktree 不存在或清理失败"
    except WorktreeError as e:
        msg = f"cleanup 失败: {e}"
    except Exception as e:
        msg = f"unexpected: {e}"

    unregistered = False
    try:
        unregistered = registry.unregister(session_id)
    except Exception:
        pass

    return {
        "session_id": session_id,
        "aborted": aborted,
        "message": msg,
        "unregistered": unregistered,
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
    except Exception:
        pass

    return {
        "session_id": session_id,
        "exists": exists,
        "path": str(wt_path) if exists else "",
        "branch": branch,
        "dirty": dirty,
        "registered": registered,
    }
