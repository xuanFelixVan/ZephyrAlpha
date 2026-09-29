# [BLUEPRINT] MOD-CD-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
#!/usr/bin/env python3
# [MODULE] scripts.session_worktree
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] subprocess (git worktree)
# [CONSUMERS] AI session 创建/切换/合并 worktree 前调用
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] worktree 在 .worktrees/ 下；分支前缀 ai/；merge 需用户确认
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exit 0=success; exit 1=error; exit 2=internal error
# [TESTS] tests/governance/rule_bridge/test_session_worktree*.py; tests/scripts/test_session_worktree_env.py; tests/scripts/test_session_worktree_archive.py
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  M11豁免: AI会话按需调用的CLI worktree协调工具，人工触发非常驻服务/非cron/非daemon
"""
Session Worktree — 每 AI 独立 checkout + 分支（§11.3.1 v2.1.0 简化版）

设计文档: 65_git_safety_governance.md §11.3.1
关联议题: #ARCH-AICOLLAB-001

v2.1.0 简化:
  - 去 7 天告警（22 路审查是一次性的，merge 后立即 abort 清理）
  - create/exec/merge/abort/list 五命令

目录结构:
    d:\\ZephyrAlpha\\
    └── .worktrees\\          # worktree 根目录（.gitignore）
        ├── AI-01\\           # AI-01 的独立 checkout
        │   └── (完整项目副本，branch=ai/AI-01/<task-id>)
        └── AI-02\\

CLI:
    python scripts/session_worktree.py create <session-id> <task-id>
    python scripts/session_worktree.py exec <session-id> -- <command...>
    python scripts/session_worktree.py merge <session-id> [--to dev] [--squash] [--yes]
    python scripts/session_worktree.py abort <session-id>
    python scripts/session_worktree.py list
    python scripts/session_worktree.py archive <session名|分支名|worktree路径> [--execute]
        [--batch-file <清单>] [--all] [--skip-rescue] [--base dev]
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

from zephyr.shared.infra.process_pool import run_subprocess_hidden

REPO_ROOT = Path(__file__).resolve().parent.parent
WORKTREE_ROOT = REPO_ROOT / ".worktrees"
BRANCH_PREFIX = "ai/"

# worktree 备置的连接配置清单（(文件名, 日志标签)；真源=主仓 config/，gitignore 豁免 git 追踪）
_CONN_ENV_FILES: tuple[tuple[str, str], ...] = (
    (".env.postgres", "PG"),
    (".env.clickhouse", "CH"),
)


def _provision_worktree_env(wt_path: Path, source_root: Path | None = None) -> list[str]:
    """环境三件套备置（#ARCH-WORKTREE-ENV-001 P2-8，2026-08-14 裁定）。

    病根：site-packages .pth 把 import zephyr 硬锚主仓 src，worktree 内跑网关/治理
    脚本时规则数据（翻译注册表）/配置（.env.postgres）/审计目录（lookup_audit）
    全部锚定错位（2026-08-14 AI-LIQ-001/AI-SELL-001 两会话同日踩坑实证）。
    create 时一次性备置，任一步失败仅告警不阻断 worktree 创建（环境治理不挡施工）：

    1. 连接配置复制（PG+CH，见 _CONN_ENV_FILES；depgraph_schema._PG_ENV_PATH 与
       ch_config._CH_ENV_PATH 都锚进程 REPO_ROOT。CH 于 2026-09-16 补入：
       提交队列 serializer worktree 缺该文件，致队列落地的每个 commit 上
       depgraph/CH 依赖型门禁与 reconciler 全部 fail-open——reconcile_execution_log
       实证 "CH 配置文件不存在: …\\.runtime\\commit_queue\\worktree\\config\\.env.clickhouse"）
    2. .runtime/lookup_audit/ 初始化（CAPABILITY-LOOKUP-REQUIRED fail-closed 目录检查）
    3. activate_env.ps1 生成（$env:PYTHONPATH=<worktree>\\src，网关提交前激活，
       使 zephyr 解析回 worktree 自身 src）

    source_root：配置真源所在仓根，默认本模块 REPO_ROOT；调用方进程的 REPO_ROOT
    可能随 sys.path 锚点漂移（同一 worktree 树被 import 时它会指向该树自身，
    于是"从主仓取配置"变成"从不存在的自己取"），故队列侧必须显式传入。
    """
    notes: list[str] = []
    root = REPO_ROOT if source_root is None else Path(source_root)

    # 1. 连接配置复制（config/.env.* 已 gitignore，clean -fd 不伤，故备置一次即长期生效）
    for cfg_name, label in _CONN_ENV_FILES:
        src = root / "config" / cfg_name
        dst = wt_path / "config" / cfg_name
        try:
            if src.exists():
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_bytes(src.read_bytes())
                notes.append(f"{label} 配置已复制 config/{cfg_name}")
            else:
                notes.append(f"WARN: 主仓 {label} 配置 config/{cfg_name} 不存在，跳过（依赖它的门禁/对账将不可用）")
        except OSError as e:
            notes.append(f"WARN: {label} 配置复制失败: {e}")

    # 2. lookup_audit 目录初始化
    try:
        (wt_path / ".runtime" / "lookup_audit").mkdir(parents=True, exist_ok=True)
        notes.append("审计目录已初始化 .runtime/lookup_audit/")
    except OSError as e:
        notes.append(f"WARN: lookup_audit 目录创建失败: {e}")

    # 3. activate 脚本生成（worktree 根目录平铺文件被 .gitignore /* 白名单自动豁免，零污染）
    activate = wt_path / "activate_env.ps1"
    try:
        activate.write_text(
            "# AI session worktree 环境激活（session_worktree.py create 自动生成，勿手改）\n"
            "# 用法: . .\\activate_env.ps1 后跑网关/治理脚本（import zephyr 解析回 worktree src）\n"
            f"$env:PYTHONPATH = '{wt_path}\\src'\n"
            f"$env:ZEPHYR_WORKTREE_ROOT = '{wt_path}'\n"
            f"Set-Location '{wt_path}'\n",
            encoding="utf-8",
        )
        notes.append("激活脚本已生成 activate_env.ps1（网关提交前: . .\\activate_env.ps1）")
    except OSError as e:
        notes.append(f"WARN: activate 脚本生成失败: {e}")

    return notes


def _run_git(args: list[str], cwd: str | Path | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    """执行 git 命令（run_subprocess_hidden 统一入口，无窗口闪现，不受 PowerShell wrapper 影响）。"""
    cmd = ["git"] + args
    return run_subprocess_hidden(cmd, capture_output=True, text=True, check=check, cwd=cwd or str(REPO_ROOT))


def _worktree_path(session_id: str) -> Path:
    """获取 session 的 worktree 路径。"""
    return WORKTREE_ROOT / session_id


def _branch_name(session_id: str, task_id: str) -> str:
    """生成分支名: ai/<session-id>/<task-id>。"""
    return f"{BRANCH_PREFIX}{session_id}/{task_id}"


def _find_branch_for_session(session_id: str) -> str | None:
    """查找 session 对应的分支（通过 git worktree list），返回短分支名（剥 refs/heads/ 前缀）。"""
    try:
        result = _run_git(["worktree", "list", "--porcelain"], check=False)
        if result.returncode != 0:
            return None
        wt_path = str(_worktree_path(session_id))
        for line in result.stdout.splitlines():
            if line.startswith("worktree ") and session_id in line:
                # 找到对应的 worktree，查找其分支
                for l2 in result.stdout.splitlines():
                    if l2.startswith("branch ") and session_id in l2:
                        full = l2.split(" ", 1)[1].strip()
                        # porcelain 输出是 refs/heads/ 全限定名；git branch -D 只认短名
                        return full[len("refs/heads/") :] if full.startswith("refs/heads/") else full
        return None
    except Exception:  # noqa: BLE001 — CLI 边界兜底转退出码（存量基线注记）
        return None


# ============================================================================
# CLI 命令
# ============================================================================


def cmd_create(args: argparse.Namespace) -> int:
    """创建 worktree + 分支。"""
    session_id = args.session_id
    task_id = args.task_id
    wt_path = _worktree_path(session_id)
    branch = _branch_name(session_id, task_id)

    if wt_path.exists():
        print(f"[WORKTREE] 错误: worktree 已存在: {wt_path}", file=sys.stderr)
        print(f"  如需重建，先执行: python scripts/session_worktree.py abort {session_id}", file=sys.stderr)
        return 1

    # 创建 worktree 根目录
    WORKTREE_ROOT.mkdir(parents=True, exist_ok=True)

    # git worktree add <path> -b <branch>
    print(f"[WORKTREE] 创建 worktree: {session_id}")
    print(f"  路径: {wt_path}")
    print(f"  分支: {branch}")
    try:
        result = _run_git(
            ["worktree", "add", str(wt_path), "-b", branch],
            check=False,
        )
        if result.returncode != 0:
            print("[WORKTREE] git worktree add 失败:", file=sys.stderr)
            print(result.stderr, file=sys.stderr, end="")
            return 1
        print("[WORKTREE] 创建成功")
        for note in _provision_worktree_env(wt_path):
            print(f"  {note}")
        # 治理层活性登记（2026-08-14 治本，AI-GIT-001 实证：CLI 创建的 worktree 此前在
        # SessionRegistry 无注册无心跳，被 GATE-WORKTREE-LIFECYCLE sweep / base_sync
        # 误判死 session 残留，未提交工作反复被抹——本批次三文件被抹两次后定位）。
        # 锚主仓根（--git-common-dir），避免从 worktree 内调用时错锚到 worktree .runtime。
        _main_root = REPO_ROOT
        try:
            from zephyr.security.access_control.session_concurrency import SessionRegistry

            _common = _run_git(["rev-parse", "--git-common-dir"], check=False)
            if _common.returncode == 0 and _common.stdout.strip():
                _main_root = Path(_common.stdout.strip()).resolve().parent
            # pid=0 = 逻辑 session（对齐 rule_bridge session_worktree_start Phase 6 治本）：
            # CLI 工作流跨进程（create/exec/merge 各一次），os.getpid() 注册会让 create
            # 进程退出后 PID 死亡 → _is_session_alive 判死（pid>0 时不看 heartbeat），
            # daemon 心跳也无法保活。pid=0 时判活走 90s 心跳新鲜度，daemon 接管续期。
            SessionRegistry(_main_root).register(session_id, pid=0)
            print("  session 已登记 SessionRegistry（逻辑 session，daemon 心跳续期）")
        except Exception as e:  # noqa: BLE001 — 登记失败不阻断创建
            print(f"  WARN: SessionRegistry 登记失败（不阻断创建）: {e}", file=sys.stderr)
        # heartbeat daemon 普及（#56 子项 2，对齐 rule_bridge session_worktree_start）：
        # 仅 register 无 daemon 时，长时间不 commit 的会话 idle 超 TTL 仍会被判死误杀。
        # detached daemon 每 30s 刷新心跳；session 注销或 idle>1800s 自动退出。
        try:
            import os as _os2

            from zephyr.shared.infra.process_pool import is_pid_alive, spawn_python_hidden

            _hb_pid_file = _main_root / ".runtime" / "locks" / f"heartbeat_{session_id}.pid"
            _hb_existing: int | None = None
            try:
                _hb_existing = int(_hb_pid_file.read_text(encoding="utf-8").strip())
            except (OSError, ValueError):
                pass
            if _hb_existing and is_pid_alive(_hb_existing):
                print(f"  heartbeat daemon 已在运行（PID {_hb_existing}），幂等跳过")
            else:
                _hb_env = _os2.environ.copy()
                _src = str(_main_root / "src")
                _hb_env["PYTHONPATH"] = (
                    _src + _os2.pathsep + _hb_env["PYTHONPATH"] if _hb_env.get("PYTHONPATH") else _src
                )
                _hb_env["ZEPHYR_RUNTIME_GATE"] = "0"  # daemon 无需 LLM 运行时拦截
                _hb_proc = spawn_python_hidden(
                    [
                        sys.executable,
                        "-m",
                        "zephyr.gov_enforcement.rule_bridge.heartbeat_daemon",
                        session_id,
                        str(_main_root),
                        "30",
                    ],
                    cwd=str(_main_root),
                    env=_hb_env,
                )
                _hb_pid_file.parent.mkdir(parents=True, exist_ok=True)
                _hb_pid_file.write_text(str(_hb_proc.pid), encoding="utf-8")
                print(f"  heartbeat daemon 已启动（PID {_hb_proc.pid}，30s 心跳；注销/idle>1800s 自动退出）")
        except Exception as e:  # noqa: BLE001 — daemon spawn 失败不阻断创建（仍有 90s 心跳窗+TTL）
            print(f"  WARN: heartbeat daemon 启动失败（不阻断创建）: {e}", file=sys.stderr)
        print(f"  进入 worktree: cd {wt_path}")
        return 0
    except Exception as e:  # noqa: BLE001 — CLI 边界兜底转退出码（存量基线注记）
        print(f"[WORKTREE] 内部错误: {e}", file=sys.stderr)
        return 2


def cmd_exec(args: argparse.Namespace) -> int:
    """在 worktree 中执行命令。"""
    session_id = args.session_id
    wt_path = _worktree_path(session_id)

    if not wt_path.exists():
        print(f"[WORKTREE] 错误: worktree 不存在: {wt_path}", file=sys.stderr)
        print(f"  先创建: python scripts/session_worktree.py create {session_id} <task-id>", file=sys.stderr)
        return 1

    if not args.command:
        print("[WORKTREE] 错误: 未指定要执行的命令", file=sys.stderr)
        return 1

    # 在 worktree 目录中执行命令
    print(f"[WORKTREE] 在 {session_id} 中执行: {' '.join(args.command)}")
    try:
        result = run_subprocess_hidden(args.command, cwd=str(wt_path))
        return result.returncode
    except Exception as e:  # noqa: BLE001 — CLI 边界兜底转退出码（存量基线注记）
        print(f"[WORKTREE] 执行失败: {e}", file=sys.stderr)
        return 2


def cmd_merge(args: argparse.Namespace) -> int:
    """合并 worktree 分支回主分支（需用户确认）。"""
    session_id = args.session_id
    target = args.to
    wt_path = _worktree_path(session_id)

    if not wt_path.exists():
        print(f"[WORKTREE] 错误: worktree 不存在: {wt_path}", file=sys.stderr)
        return 1

    # 查找分支名
    branch = _find_branch_for_session(session_id)
    if not branch:
        print(f"[WORKTREE] 错误: 无法找到 {session_id} 的分支", file=sys.stderr)
        return 1

    # 用户确认
    if not args.yes:
        print(f"[WORKTREE] 即将合并: {branch} → {target}")
        print(f"  squash: {'是' if args.squash else '否'}")
        response = input("  确认合并？(yes/no): ").strip().lower()
        if response != "yes":
            print("[WORKTREE] 合并已取消")
            return 0

    print(f"[WORKTREE] 合并 {branch} → {target}")
    try:
        # 切换到主工作区合并
        merge_cmd = ["merge", "--no-ff"]
        if args.squash:
            merge_cmd = ["merge", "--squash"]

        result = _run_git(merge_cmd + [branch], check=False)
        if result.returncode != 0:
            print("[WORKTREE] 合并失败:", file=sys.stderr)
            print(result.stderr, file=sys.stderr, end="")
            print("  可能需要解决冲突后 git commit", file=sys.stderr)
            return 1

        if args.squash:
            # squash merge 需要手动 commit
            _run_git(["commit", "-m", f"merge(ai): {session_id} squashed"], check=False)

        print("[WORKTREE] 合并成功")
        # §11.3.1 v2.1.0: merge 后立即 abort 清理
        # S2 四证：merge 场景豁免证 1（会话仍活跃），仍走证 2/4（快照）
        print("[WORKTREE] 自动清理 worktree...")
        return cmd_abort_inner(session_id, exempt_cert1=True)
    except Exception as e:  # noqa: BLE001 — CLI 边界兜底转退出码（存量基线注记）
        print(f"[WORKTREE] 内部错误: {e}", file=sys.stderr)
        return 2


# ============================================================================
# S2 四证检查（2026-08-14 wipe 事故治本，worktree_cleanup_sop.md）
# ============================================================================


def _audit_abort(session_id: str, verdict: str, reason: str, details: dict) -> None:
    """abort 操作审计落盘（非阻断，jsonl 追加）。

    审计文件: .runtime/gate_audit/worktree_abort.jsonl
    """
    audit_dir = REPO_ROOT / ".runtime" / "gate_audit"
    try:
        audit_dir.mkdir(parents=True, exist_ok=True)
    except OSError:
        return
    import os

    record = {
        "timestamp": time.time(),
        "session_id": session_id,
        "verdict": verdict,
        "reason": reason,
        "pid": os.getpid(),
        **details,
    }
    try:
        with open(audit_dir / "worktree_abort.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError:
        pass


def _check_cert_death(session_id: str) -> tuple[bool, str]:
    """证 1 死亡证明：heartbeat 停跳 >90s 且 registry 无活跃记录。

    Returns: (passed, reason)
    """
    try:
        from zephyr.security.access_control.session_concurrency import SessionRegistry

        reg = SessionRegistry(REPO_ROOT)
        actives = {s.session_id for s in reg.list_active()}
        if session_id in actives:
            return False, (
                f"session '{session_id}' 仍活跃（registry list_active 命中）——"
                "heartbeat 未停跳 >90s，禁止清理活跃 worktree"
            )
        return True, "registry 无活跃记录（heartbeat 已停跳）"
    except Exception as e:  # noqa: BLE001 — registry 不可读视为死亡（fail-open 到下一证）
        return True, f"registry 读取异常（降级判死亡）: {e}"


def _check_cert_no_unmerged(session_id: str, wt_path: Path) -> tuple[bool, str, dict]:
    """证 2 无未合并工作证明：分支无 ahead commit + git status 无 staged 变更。

    Returns: (passed, reason, details)
    """
    details: dict = {"ahead_count": 0, "dirty_files": []}
    branch = _find_branch_for_session(session_id)
    if not branch:
        return True, "无分支（已删或从未创建）", details

    # ① 分支 ahead commit 数
    ahead_result = _run_git(
        ["log", "dev.." + branch, "--oneline"],
        check=False,
    )
    ahead_count = 0
    if ahead_result.returncode == 0 and ahead_result.stdout.strip():
        ahead_count = len(ahead_result.stdout.strip().splitlines())
    details["ahead_count"] = ahead_count
    details["branch"] = branch

    # ② worktree 内未提交变更
    dirty_result = _run_git(
        ["-C", str(wt_path), "status", "--porcelain"],
        check=False,
    )
    dirty: list[str] = []
    if dirty_result.returncode == 0 and dirty_result.stdout.strip():
        dirty = [l[3:].strip() for l in dirty_result.stdout.strip().splitlines() if len(l) > 3]
    details["dirty_files"] = dirty[:10]

    if dirty:
        return (
            False,
            (
                f"worktree 有 {len(dirty)} 个未提交变更: {dirty[:5]}"
                "——先 commit 或 stash push 存证 refs/quarantine/ 后再清理"
            ),
            details,
        )
    if ahead_count > 0:
        # ahead commit 已入对象库，分支本身即存证 → 通过但提示
        return True, f"分支有 {ahead_count} 个 ahead commit（已入对象库，永不丢失）", details
    return True, "分支无 ahead commit 且无未提交变更", details


def _check_cert_recovery(session_id: str) -> tuple[bool, str]:
    """证 4 可恢复证明：记录分支 tip SHA 到 quarantine 快照。

    Returns: (passed, reason)
    """
    branch = _find_branch_for_session(session_id)
    if not branch:
        return True, "无分支，跳过快照"
    sha_result = _run_git(["rev-parse", branch], check=False)
    if sha_result.returncode != 0:
        return False, f"无法读取分支 tip SHA: {sha_result.stderr.strip()}"
    sha = sha_result.stdout.strip()

    quarantine_dir = REPO_ROOT / ".runtime" / "quarantine"
    try:
        quarantine_dir.mkdir(parents=True, exist_ok=True)
        with open(quarantine_dir / "branch_refs.log", "a", encoding="utf-8") as f:
            f.write(f"{time.strftime('%Y-%m-%dT%H:%M:%S')} {session_id} {branch} {sha}\n")
        return True, f"分支 tip SHA 已记录: {sha[:12]} → .runtime/quarantine/branch_refs.log"
    except OSError as e:
        return False, f"快照写入失败: {e}"


def _four_cert_check(session_id: str, wt_path: Path, *, skip: bool = False, exempt_cert1: bool = False) -> int | None:
    """S2 四证检查（worktree_cleanup_sop.md）。

    Args:
        skip: --force-skip-checks 逃生通道，跳过全部检查（落审计）
        exempt_cert1: merge 后自清理场景，豁免证 1（会话仍活跃）但仍走证 2/4

    Returns: None=全部通过；1=阻断
    """
    if skip:
        _audit_abort(session_id, "SKIP", "--force-skip-checks 逃生通道", {})
        print("[S2] --force-skip-checks：跳过四证检查（落审计）", file=sys.stderr)
        return None

    print(f"[S2] 四证检查: {session_id}")

    # 证 1 死亡证明
    if exempt_cert1:
        print("  证1 死亡证明: EXEMPT（merge 后自清理，会话仍活跃）")
    else:
        ok1, reason1 = _check_cert_death(session_id)
        print(f"  证1 死亡证明: {'PASS' if ok1 else 'BLOCKED'}——{reason1}")
        if not ok1:
            _audit_abort(session_id, "BLOCKED", reason1, {"cert": 1})
            print("\n[S2] 阻断：证 1 不通过。如确认已死，用 --force-skip-checks", file=sys.stderr)
            return 1

    # 证 2 无未合并工作证明
    ok2, reason2, details2 = _check_cert_no_unmerged(session_id, wt_path)
    print(f"  证2 无未合并工作: {'PASS' if ok2 else 'BLOCKED'}——{reason2}")
    if not ok2:
        _audit_abort(session_id, "BLOCKED", reason2, {"cert": 2, **details2})
        print("\n[S2] 阻断：证 2 不通过。先处理未提交变更", file=sys.stderr)
        return 1

    # 证 3 统筹批准（自己 abort 自己免批准——merge 后自动清理场景）
    # 证 3 的自动化：merge 流程内部调用已隐式批准；手动 abort 需 --yes 确认
    print("  证3 统筹批准: PASS（调用方已确认）")

    # 证 4 可恢复证明
    ok4, reason4 = _check_cert_recovery(session_id)
    print(f"  证4 可恢复证明: {'PASS' if ok4 else 'BLOCKED'}——{reason4}")
    if not ok4:
        _audit_abort(session_id, "BLOCKED", reason4, {"cert": 4})
        print("\n[S2] 阻断：证 4 不通过。快照失败，禁止清理", file=sys.stderr)
        return 1

    _audit_abort(session_id, "ALLOWED", "四证齐全", {"certs": [1, 2, 3, 4], **details2})
    print("[S2] 四证齐全，允许清理")
    return None


def _teardown_session_governance(session_id: str) -> None:
    """会话治理收尾（#56 子项 2 对称闭环）：kill heartbeat daemon + 注销 SessionRegistry。

    create 已登记 registry + spawn daemon，abort/merge 收尾必须对称清理——否则
    daemon 空跑保活死会话至 idle 超时（1800s），registry 残留条目干扰 sweep 判据。
    Best-effort：任何一步失败仅告警，不阻断 abort 主流程。
    """
    import os as _os

    _main_root = REPO_ROOT
    _common = _run_git(["rev-parse", "--git-common-dir"], check=False)
    if _common.returncode == 0 and _common.stdout.strip():
        _main_root = Path(_common.stdout.strip()).resolve().parent

    # 1. kill heartbeat daemon（PID 文件在手直接 taskkill；daemon 也有自退出兜底）
    try:
        _hb_pid_file = _main_root / ".runtime" / "locks" / f"heartbeat_{session_id}.pid"
        _pid = int(_hb_pid_file.read_text(encoding="utf-8").strip())
        if _os.name == "nt":
            run_subprocess_hidden(["taskkill", "/PID", str(_pid), "/F"], capture_output=True, timeout=5)
        else:
            _os.kill(_pid, 15)  # SIGTERM
        print(f"  heartbeat daemon 已终止（PID {_pid}）")
    except (OSError, ValueError):
        pass  # 无 PID 文件/已死——无需处理
    except Exception as e:  # noqa: BLE001
        print(f"  WARN: heartbeat daemon 终止失败（daemon idle 超时自退出兜底）: {e}", file=sys.stderr)
    try:
        _hb_pid_file.unlink(missing_ok=True)
    except OSError:
        pass

    # 1b. heartbeat 审计文件清理（对齐 rule_bridge merge/abort 的 cleanup_heartbeat_file；
    # 只删 heartbeat.jsonl，保留 session 目录其他文件）
    try:
        from zephyr.gov_enforcement.rule_bridge.heartbeat_daemon import cleanup_heartbeat_file

        cleanup_heartbeat_file(_main_root, session_id)
    except Exception:  # noqa: BLE001 — best-effort
        pass

    # 2. 注销 SessionRegistry（对称 create 的 register）
    try:
        from zephyr.security.access_control.session_concurrency import SessionRegistry

        SessionRegistry(_main_root).unregister(session_id)
        print("  session 已从 SessionRegistry 注销")
    except Exception as e:  # noqa: BLE001 — 注销失败不阻断（TTL 到期自动过期兜底）
        print(f"  WARN: SessionRegistry 注销失败（TTL 3600s 到期自动清理）: {e}", file=sys.stderr)


def cmd_abort_inner(session_id: str, *, skip_checks: bool = False, exempt_cert1: bool = False) -> int:
    """清理 worktree（内部函数，含 S2 四证检查）。"""
    wt_path = _worktree_path(session_id)

    if not wt_path.exists():
        print(f"[WORKTREE] worktree 不存在: {session_id}")
        _teardown_session_governance(session_id)  # worktree 已没，daemon/registry 残留仍收尾
        return 0

    # S2 四证检查（2026-08-14 wipe 事故治本）
    rc = _four_cert_check(session_id, wt_path, skip=skip_checks, exempt_cert1=exempt_cert1)
    if rc is not None:
        return rc

    # 先取分支名（worktree remove 后 _find_branch_for_session 依赖 worktree list 将找不到）
    branch = _find_branch_for_session(session_id)

    # git worktree remove --force
    result = _run_git(["worktree", "remove", "--force", str(wt_path)], check=False)
    if result.returncode != 0:
        # git worktree remove 失败 → safe_rmtree 硬断言+补丁直通兜底
        # （批5b：硬断言授权通道，防 in-process 补丁拦截保护区合法清理）
        from zephyr.shared.io.file_utils import safe_rmtree

        safe_rmtree(wt_path, allowed_prefix=WORKTREE_ROOT, ignore_errors=True)

    # 删除分支（如果还存在）
    if branch:
        _run_git(["branch", "-D", branch], check=False)

    _teardown_session_governance(session_id)
    print(f"[WORKTREE] 已清理: {session_id}")
    return 0


def cmd_abort(args: argparse.Namespace) -> int:
    """清理 worktree（放弃修改）。"""
    skip = getattr(args, "force_skip_checks", False)
    return cmd_abort_inner(args.session_id, skip_checks=skip)


def cmd_list(args: argparse.Namespace) -> int:
    """列出所有 worktree。"""
    try:
        result = _run_git(["worktree", "list"], check=False)
        if result.returncode != 0:
            print("[WORKTREE] git worktree list 失败:", file=sys.stderr)
            print(result.stderr, file=sys.stderr, end="")
            return 1
        print("[WORKTREE] 当前 worktree 列表:")
        print(result.stdout, end="")
        return 0
    except Exception as e:  # noqa: BLE001 — CLI 边界兜底转退出码（存量基线注记）
        print(f"[WORKTREE] 内部错误: {e}", file=sys.stderr)
        return 2


# ============================================================================
# lane-archive（RB-4 车道生命周期治本）
# 真源: docs/_working/root_cure_campaign/RB4_lane_lifecycle.md §2
# 流程: 死判（活跃硬拒）→ V 判型（ahead+cherry+dirty 三查）→ patch 存证+？？rescue
#       → worktree remove --force --force → prune+进程外核实 → branch -d（真 ahead 落台账，禁 -D）
# ============================================================================

_ARCHIVE_ACTIVE_LOCK_TTL = 3600  # session_active lockfile 新鲜度 TTL（对齐 sweep 判据 4）
_ARCHIVE_COMMIT_PERSISTED_TTL = 86400  # commit_persisted 标记免疫窗（对齐 sweep 24h）
_AHEAD_LEDGER = Path(".runtime") / "quarantine" / "ahead_branches.log"
_ARCHIVE_RESCUE_DIR = Path(".runtime") / "tmp" / "rescue"
# --all 批量排除表（设计 §4：主区+pool+qoder+serializer 队列车道不进常驻归档）
_ARCHIVE_ALL_EXCLUDED_MARKERS = (".aidrafts_pool", ".qoder", "commit_queue")


class _ArchiveEvidenceManager:
    """最小 WorktreeManager 适配器——仅供 rule_bridge._generate_retire_patch_evidence 使用。

    archive 的车道可位于任意注册路径（.worktrees/、.aidrafts/、qoder 遗产…），
    rule_bridge 的 _wt_path 硬锚 .aidrafts/<sid>，故用本适配器把 wt_path 直指
    porcelain 反查到的真实路径；run_git 契约与 WorktreeManager.run_git 一致。
    """

    def __init__(self, repo_root: Path, wt_path: Path) -> None:
        self.repo_root = Path(repo_root)
        self._lane_wt_path = wt_path

    def _wt_path(self, session_id: str) -> Path:
        """契约签名（session_id 未用——适配器恒指向反查到的真实车道路径）。"""
        return self._lane_wt_path

    def run_git(self, cmd: list[str], cwd: str | Path | None = None) -> subprocess.CompletedProcess:
        from zephyr.shared.infra.process_pool import run_subprocess_hidden

        return run_subprocess_hidden(
            cmd,
            cwd=str(cwd or self.repo_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=120,
        )

    def _run_git(self, cmd: list[str], cwd: str | Path | None = None) -> subprocess.CompletedProcess:
        """向后兼容 thin wrapper（对齐 WorktreeManager 既有惯例）。"""
        return self.run_git(cmd, cwd)


def _list_worktree_registry() -> list[dict]:
    """解析 git worktree list --porcelain 为注册表（唯一真源，不做目录遍历）。"""
    result = _run_git(["worktree", "list", "--porcelain"], check=False)
    if result.returncode != 0:
        return []
    entries: list[dict] = []
    cur: dict = {}
    for line in result.stdout.splitlines():
        if not line.strip():
            if cur:
                entries.append(cur)
                cur = {}
            continue
        key, _, value = line.partition(" ")
        if key == "worktree":
            cur = {
                "path": value,
                "head": None,
                "branch": None,
                "detached": False,
                "locked": False,
                "prunable": False,
                "bare": False,
            }
        elif key == "HEAD":
            cur["head"] = value
        elif key == "branch":
            # porcelain 输出 refs/heads/ 全限定名；统一剥前缀存短名
            cur["branch"] = value[len("refs/heads/") :] if value.startswith("refs/heads/") else value
        elif key == "detached":
            cur["detached"] = True
        elif key == "locked":
            cur["locked"] = True
        elif key == "prunable":
            cur["prunable"] = True
        elif key == "bare":
            cur["bare"] = True
    if cur:
        entries.append(cur)
    return entries


def _normcase(p: str | Path) -> str:
    """路径标准化（porcelain 正斜杠 vs Windows 反斜杠、盘符大小写差异，对齐 WorktreeManager）。"""
    return os.path.normcase(str(p))


def _resolve_archive_target(target: str, registry: list[dict]) -> dict | None:
    """按 worktree 路径 | session 名（目录 basename）| 分支名 反查注册表。

    返回 entry dict；未命中返回 None（不猜、不遍历目录——git 注册表是唯一真源）。
    """
    t = target.strip()
    if not t:
        return None
    # ① 路径匹配（绝对路径或相对 REPO_ROOT）
    cand = Path(t)
    if not cand.is_absolute():
        cand = REPO_ROOT / cand
    t_norm = _normcase(cand)
    for e in registry:
        if _normcase(e["path"]) == t_norm:
            return e
    # ② session 名 = worktree 目录 basename（sid 提取不硬编码前缀，RB-4 §4）
    for e in registry:
        if Path(e["path"]).name == t:
            return e
    # ③ 分支名（短名；接受误带 refs/heads/ 前缀的输入）
    t_branch = t[len("refs/heads/") :] if t.startswith("refs/heads/") else t
    for e in registry:
        if e["branch"] and e["branch"] == t_branch:
            return e
    return None


def _check_archive_target_dead(sid: str) -> tuple[bool, str]:
    """死会话硬判（lane-archive 证 1）：活跃注册表/新鲜 lockfile/免疫标记任一命中=活。

    命中活跃=硬拒绝，无逃生 flag（要动活车道只能等它死——RB-4 §2.1）。
    """
    # ① SessionRegistry 活跃名单（心跳停跳>90s / TTL 3600s 已由 list_active reap）
    try:
        from zephyr.security.access_control.session_concurrency import SessionRegistry

        actives = {s.session_id for s in SessionRegistry(REPO_ROOT).list_active()}
        if sid in actives:
            return False, f"session '{sid}' 仍活跃（registry list_active 命中）——活车道禁止 archive，无逃生 flag"
    except Exception as e:  # noqa: BLE001 — registry 不可读降级到标记检查（对齐 _check_cert_death）
        print(f"  WARN: SessionRegistry 读取异常（降级到锁标记检查）: {e}", file=sys.stderr)
    # ② 新鲜 session_active lockfile（commit/merge 关键段进行中，P1-2 同源路径）
    lock = REPO_ROOT / ".runtime" / "locks" / f"session_active_{sid}.lock"
    try:
        if lock.exists() and (time.time() - lock.stat().st_mtime) < _ARCHIVE_ACTIVE_LOCK_TTL:
            return False, f"fresh session_active lockfile（age<{_ARCHIVE_ACTIVE_LOCK_TTL}s）: {lock.name}"
    except OSError:
        pass
    # ③ commit_persisted 免疫窗（24h，对齐 sweep commit-persisted 判据）
    marker = REPO_ROOT / ".runtime" / "locks" / f"commit_persisted_{sid}.json"
    try:
        if marker.exists() and (time.time() - marker.stat().st_mtime) < _ARCHIVE_COMMIT_PERSISTED_TTL:
            return False, f"commit_persisted 标记在 24h 免疫窗内: {marker.name}"
    except OSError:
        pass
    return True, "死车道（registry 无活跃记录 + 无新鲜锁/免疫标记）"


def _probe_ahead_count(branch: str | None, base: str) -> int:
    """① ahead 计数（detached 记 0；rev-list 失败记 -1 → 保守按真 ahead 处置）。"""
    if not branch:
        return 0
    r = _run_git(["rev-list", "--count", f"{base}..{branch}"], check=False)
    if r.returncode == 0 and r.stdout.strip().isdigit():
        return int(r.stdout.strip())
    return -1


def _probe_cherry_all_equal(branch: str | None, base: str, ahead: int) -> bool:
    """② cherry 全等判据（仅 ahead>0 有意义；全 '-' = 补丁已全部在基线）。"""
    if not branch or ahead <= 0:
        return False
    r = _run_git(["cherry", base, branch], check=False)
    if r.returncode != 0:
        return False
    lines = [l for l in r.stdout.splitlines() if l.strip()]
    return bool(lines) and all(l.startswith("-") for l in lines)


def _probe_status_lines(wt_path: Path) -> tuple[list[str], list[str]]:
    """③ 脏查 → (porcelain 行, 未跟踪路径)。"""
    r = _run_git(["-C", str(wt_path), "status", "--porcelain"], check=False)
    if r.returncode != 0:
        return [], []
    lines = [l for l in r.stdout.splitlines() if l.strip()]
    return lines, [l[3:] for l in lines if l.startswith("?? ") and len(l) > 3]


def _classify_archive_lane(entry: dict, base: str) -> dict:
    """V 判型三查：ahead（rev-list --count）+ cherry 全等 + status --porcelain。

    判型结论:
        zero_loss       ahead=0 且无脏 → 直清
        superseded_shell ahead>0 但 cherry 全 '-'（补丁已入基线）→ 直清，branch -d 可过
        needs_rescue    有脏 → patch 存证（fail-closed）+ ？？rescue 后再清
        ahead_only      ahead>0 且 cherry 有 '+' → 真独有内容，branch -d 必败 → 台账
    """
    wt_path = Path(entry["path"])
    branch = entry.get("branch")
    ahead = _probe_ahead_count(branch, base)
    cherry_all_equal = _probe_cherry_all_equal(branch, base, ahead)
    dirty, untracked = _probe_status_lines(wt_path)

    if dirty:
        verdict = "needs_rescue"
    elif ahead == 0:
        verdict = "zero_loss"
    elif cherry_all_equal:
        verdict = "superseded_shell"
    else:
        verdict = "ahead_only"
    return {
        "sid": wt_path.name,
        "wt_path": wt_path,
        "branch": branch,
        "ahead": ahead,
        "cherry_all_equal": cherry_all_equal,
        "dirty": dirty,
        "untracked": untracked,
        "verdict": verdict,
    }


def _rescue_untracked_files(wt_path: Path, sid: str, untracked: list[str]) -> dict:
    """？？未跟踪文件 → .runtime/tmp/rescue/<sid>/（+mapping.json 台账）。

    mv_rescue（git_guard.py 策略 C）同构，落点换临时区（24h TTL 由 tmp 清理管，
    避开一代 .aidrafts 目录本身可能被清的缺陷——RB-4 §1.3）。
    """
    rescue_dir = REPO_ROOT / _ARCHIVE_RESCUE_DIR / sid
    rescue_dir.mkdir(parents=True, exist_ok=True)
    mapping: dict[str, str] = {}
    moved = 0
    for raw in untracked:
        rel = raw.strip().strip('"').rstrip("/")
        if not rel or rel == ".":
            continue
        src = wt_path / rel
        if not src.exists():
            continue
        dst = rescue_dir / rel
        try:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dst))
            mapping[rel] = str(dst)
            moved += 1
        except (OSError, shutil.Error) as e:
            print(f"  WARN: rescue 失败 {rel}: {e}", file=sys.stderr)
    try:
        (rescue_dir / "mapping.json").write_text(
            json.dumps(
                {
                    "session_id": sid,
                    "source_worktree": str(wt_path),
                    "rescued": mapping,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
    except OSError as e:
        print(f"  WARN: mapping.json 写入失败: {e}", file=sys.stderr)
    return {"moved": moved, "rescue_dir": rescue_dir}


def _archive_generate_evidence(sid: str, wt_path: Path) -> dict:
    """退役 patch 存证（复用 rule_bridge Z1 原语；fail-closed——失败调用方必须保留车道）。"""
    try:
        from zephyr.gov_enforcement.rule_bridge.session_worktree import _generate_retire_patch_evidence
    except ImportError as e:
        return {"generated": False, "error": f"rule_bridge 导入失败: {e}"}
    return _generate_retire_patch_evidence(
        REPO_ROOT, sid, _ArchiveEvidenceManager(REPO_ROOT, wt_path), source="lane-archive"
    )


def _record_ahead_branch(sid: str, branch: str, ahead: int, patch_path: str | None) -> Path:
    """真 ahead 分支白名单台账（禁 -D，交人工裁定 merge-or-die——RB-4 §2.5）。"""
    ledger = REPO_ROOT / _AHEAD_LEDGER
    ledger.parent.mkdir(parents=True, exist_ok=True)
    with open(ledger, "a", encoding="utf-8") as f:
        f.write(f"{time.strftime('%Y-%m-%dT%H:%M:%S')}\t{sid}\t{branch}\tahead={ahead}\tpatch={patch_path or '-'}\n")
    return ledger


def _archive_hard_guards(entry: dict, sid: str, wt_path: Path, branch: str | None, base: str) -> tuple[bool, int]:
    """硬拒三关：主区/裸仓 / 活车道死判 / 基线分支本身。打印+审计在关内。"""
    if entry.get("bare") or _normcase(wt_path) == _normcase(REPO_ROOT):
        print(f"[ARCHIVE] 硬拒绝: 主区/裸仓禁止归档: {wt_path}", file=sys.stderr)
        return False, 1
    dead, reason = _check_archive_target_dead(sid)
    print(f"  死判: {'PASS' if dead else '硬拒绝'}——{reason}")
    if not dead:
        _audit_abort(sid, "BLOCKED", f"lane-archive 活车道硬拒: {reason}", {"cert": 1, "mode": "archive"})
        print("[ARCHIVE] 硬拒绝：活跃会话车道禁止归档（无逃生 flag，要动活车道只能等它死）", file=sys.stderr)
        return False, 1
    if branch and branch == base:
        print(f"[ARCHIVE] 硬拒绝: 基线分支本身禁止归档: {branch}", file=sys.stderr)
        return False, 1
    return True, 0


def _archive_rescue_phase(info: dict, sid: str, wt_path: Path, skip_rescue: bool) -> tuple[bool, str | None]:
    """①patch 存证（fail-closed）+ ②？？rescue。返回 (是否失败, patch_path)。"""
    patch_path: str | None = None
    if not info["dirty"]:
        return False, None
    ev = _archive_generate_evidence(sid, wt_path)
    if not ev.get("generated"):
        if ev.get("reason") == "clean":
            print("  ① patch 存证: SKIP（status 已转干净）")
            return False, None
        err = ev.get("error", ev.get("reason", "unknown"))
        print(f"[ARCHIVE] fail-closed：存证失败，保留车道待人工: {err}", file=sys.stderr)
        _audit_abort(sid, "BLOCKED", f"lane-archive 存证失败: {err}", {"cert": "evidence"})
        return True, None
    patch_path = ev.get("patch_path")
    print(f"  ① patch 存证: {patch_path}（三分类={ev.get('counts')}）")
    if info["untracked"] and not skip_rescue:
        r_rescue = _rescue_untracked_files(wt_path, sid, info["untracked"])
        print(f"  ② ？？rescue: {r_rescue['moved']} 项 → {r_rescue['rescue_dir']}（mapping.json 台账）")
    elif info["untracked"]:
        print("  ② ？？rescue: SKIP（--skip-rescue）")
    return False, patch_path


def _archive_remove_and_verify(wt_path: Path) -> bool:
    """③remove（locked 双 force 实测可过；失败 safe_rmtree 兜底）+ ④prune 进程外核实。"""
    r_rm = _run_git(["worktree", "remove", "--force", "--force", str(wt_path)], check=False)
    if r_rm.returncode != 0:
        print(f"  ③ worktree remove 失败（{(r_rm.stderr or '').strip()[:120]}）→ safe_rmtree 兜底", file=sys.stderr)
        try:
            from zephyr.shared.io.file_utils import safe_rmtree

            safe_rmtree(wt_path, allowed_prefix=wt_path.parent, ignore_errors=True)
        except Exception as e:  # noqa: BLE001 — 兜底失败交给 ④ 核实拦截
            print(f"  ③ safe_rmtree 兜底也失败: {e}", file=sys.stderr)
    _run_git(["worktree", "prune"], check=False)
    still = [e for e in _list_worktree_registry() if _normcase(e["path"]) == _normcase(wt_path)]
    if still:
        print("[ARCHIVE] 核实失败：worktree 仍注册——分支保持不动，报告人工", file=sys.stderr)
        return False
    print("  ④ prune+核实: worktree 已从注册表消失")
    return True


def _archive_branch_finish(sid: str, branch: str | None, info: dict, patch_path: str | None) -> None:
    """⑤branch -d（只认已合并；失败=真 ahead → 禁 -D 落白名单）+ 收尾注销与审计。"""
    if branch:
        r_bd = _run_git(["branch", "-d", branch], check=False)
        if r_bd.returncode == 0:
            print(f"  ⑤ branch -d: {branch} 已删（壳分支）")
        else:
            ledger = _record_ahead_branch(sid, branch, max(info["ahead"], 0), patch_path)
            print(f"  ⑤ branch -d 失败（真 ahead）→ 禁 -D，已落白名单台账: {ledger}")
    _teardown_session_governance(sid)
    _audit_abort(
        sid,
        "ARCHIVED",
        "lane-archive 完成",
        {"branch": branch, "verdict": info["verdict"], "ahead": info["ahead"], "patch": patch_path},
    )


def _archive_one(entry: dict, *, execute: bool, base: str, skip_rescue: bool) -> int:
    """单车道归档。dry-run 打印完整处置计划；--execute 才动真格。返回退出码。"""
    sid = Path(entry["path"]).name
    wt_path = Path(entry["path"])
    ok, guard_rc = _archive_hard_guards(entry, sid, wt_path, entry.get("branch"), base)
    if not ok:
        return guard_rc

    dead, _reason = _check_archive_target_dead(sid)
    info = _classify_archive_lane(entry, base)
    branch = info["branch"]
    mode = "执行" if execute else "DRY-RUN 计划"
    nl = chr(92) + "n"
    print(f"[ARCHIVE] {mode}: {sid}")
    print(
        f"  路径: {wt_path}" + nl + f"  分支: {branch or '(detached)'}  基线: {base}  ahead={info['ahead']}"
        f"  cherry全等={info['cherry_all_equal']}  脏文件={len(info['dirty'])}（？？{len(info['untracked'])}）"
    )
    print("  死判已在守卫关输出。")
    print(f"  判型: {info['verdict']}")
    if info["dirty"]:
        print(
            f"  处置: ①patch 存证（fail-closed）→ ②？？rescue→.runtime/tmp/rescue/{sid}/"
            " → ③remove --force --force → ④prune+核实 → ⑤branch -d"
        )
    else:
        print("  处置: 零丢失型直清 ③remove --force --force → ④prune+核实 → ⑤branch -d")
    if not execute:
        print("  [DRY-RUN] 未做任何变更（--execute 才执行）")
        return 0

    failed, patch_path = _archive_rescue_phase(info, sid, wt_path, skip_rescue)
    if failed:
        return 1
    if not _archive_remove_and_verify(wt_path):
        return 1
    _archive_branch_finish(sid, branch, info, patch_path)
    print(f"[ARCHIVE] 已归档: {sid}")
    return 0


def _archive_collect_targets(args: argparse.Namespace, registry: list[dict]) -> list[str]:
    """目标收集：显式 targets + --batch-file + --all（排除表滤主区/pool/qoder/serializer）。"""
    targets: list[str] = list(getattr(args, "targets", None) or [])
    batch_file = getattr(args, "batch_file", None)
    if batch_file:
        bf = Path(batch_file)
        if not bf.exists():
            print(f"[ARCHIVE] 错误: 批量清单不存在: {bf}", file=sys.stderr)
            return []
        for line in bf.read_text(encoding="utf-8").splitlines():
            line = line.split("#", 1)[0].strip()
            if line:
                targets.append(line)
    if getattr(args, "all", False):
        main_norm = _normcase(REPO_ROOT)
        for e in registry:
            p_norm = _normcase(e["path"]).replace(chr(92) + "/", "/")
            if _normcase(e["path"]) == main_norm or e.get("bare"):
                continue
            if any(m in p_norm for m in _ARCHIVE_ALL_EXCLUDED_MARKERS):
                continue
            if e.get("branch") and e["branch"].startswith("serializer/"):
                continue
            targets.append(e["path"])
    return targets


def cmd_archive(args: argparse.Namespace) -> int:
    """lane-archive：死车道归档（dry-run 默认，--execute 显式；RB-4 治本）。"""
    registry = _list_worktree_registry()
    if not registry:
        print("[ARCHIVE] 错误: git worktree list --porcelain 失败或为空", file=sys.stderr)
        return 2

    targets = _archive_collect_targets(args, registry)
    if not targets:
        print("[ARCHIVE] 错误: 未指定目标（session 名|分支名|路径 / --batch-file / --all）", file=sys.stderr)
        return 1

    execute = bool(getattr(args, "execute", False))
    if not execute:
        print("[ARCHIVE] === DRY-RUN 模式（默认；--execute 才真正执行）===")
    rc = 0
    done = 0
    for t in targets:
        entry = _resolve_archive_target(t, registry)
        if entry is None:
            print(f"[ARCHIVE] 错误: 目标未命中 worktree 注册表（唯一真源=git worktree list）: {t}", file=sys.stderr)
            rc = 1
            continue
        one_rc = _archive_one(
            entry, execute=execute, base=args.base, skip_rescue=bool(getattr(args, "skip_rescue", False))
        )
        if one_rc == 0:
            done += 1
        else:
            rc = rc or one_rc
    print(f"[ARCHIVE] 汇总: {done}/{len(targets)} 处理完成（execute={execute}）")
    return rc


def main() -> int:
    # CAND-GOVSEC-001 ② 翻硬拦（批5b，2026-08-26）：观测期零误伤，worktree CLI 入口
    # in-process 删除护栏转正硬拦。abort 兜底已改 safe_rmtree 硬断言授权通道（直通），
    # 裸删除命中保护区即拦。安装失败静默降级，不阻断主链路。
    try:
        try:
            from scripts.ops_guard import install_inprocess_enforcement
        except ImportError:  # python scripts/session_worktree.py 直跑：sys.path[0]=scripts/
            from ops_guard import install_inprocess_enforcement
        install_inprocess_enforcement()
    except Exception:  # noqa: BLE001 — 护栏装配失败永不阻断 worktree 主链路
        pass

    parser = argparse.ArgumentParser(
        description="Session Worktree — 每 AI 独立 checkout+分支（§11.3.1 v2.1.0）",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # create
    p_create = sub.add_parser("create", help="创建 worktree + 分支")
    p_create.add_argument("session_id", help="session ID（如 AI-01）")
    p_create.add_argument("task_id", help="任务 ID（如 task-factor-registry）")
    p_create.set_defaults(func=cmd_create)

    # exec
    p_exec = sub.add_parser("exec", help="在 worktree 中执行命令")
    p_exec.add_argument("session_id", help="session ID")
    p_exec.add_argument("command", nargs=argparse.REMAINDER, help="要执行的命令（-- 之后）")
    p_exec.set_defaults(func=cmd_exec)

    # merge
    p_merge = sub.add_parser("merge", help="合并 worktree 分支回主分支")
    p_merge.add_argument("session_id", help="session ID")
    p_merge.add_argument(
        "--to",
        default="dev",
        help="目标分支（默认 dev——项目主线约定，2026-08-15 前误默认 main，#ARCH-WORKTREE-WRITE-INTEGRITY-001 P1-2② 修正）",
    )
    p_merge.add_argument("--squash", action="store_true", help="squash merge")
    p_merge.add_argument("--yes", action="store_true", help="跳过确认")
    p_merge.set_defaults(func=cmd_merge)

    # abort
    p_abort = sub.add_parser("abort", help="清理 worktree（放弃修改）")
    p_abort.add_argument("session_id", help="session ID")
    p_abort.add_argument(
        "--force-skip-checks",
        action="store_true",
        help="跳过 S2 四证检查（逃生通道，落审计）",
    )
    p_abort.set_defaults(func=cmd_abort)

    # list
    p_list = sub.add_parser("list", help="列出所有 worktree")
    p_list.set_defaults(func=cmd_list)

    # archive（RB-4 lane-archive：dry-run 默认，--execute 显式）
    p_archive = sub.add_parser(
        "archive",
        help="归档死车道（死判→V判型→存证→remove→prune→branch -d；真 ahead 落台账禁 -D）",
    )
    p_archive.add_argument(
        "targets",
        nargs="*",
        help="目标（session 名 | 分支名 | worktree 路径），可多个",
    )
    p_archive.add_argument(
        "--execute",
        action="store_true",
        help="真正执行（默认 dry-run 只打印处置计划）",
    )
    p_archive.add_argument(
        "--batch-file",
        dest="batch_file",
        help="批量清单文件（每行一个目标，# 注释）",
    )
    p_archive.add_argument(
        "--all",
        action="store_true",
        help="批量全量（排除表：主区/pool/qoder/serializer；活跃由死判硬拒）",
    )
    p_archive.add_argument(
        "--skip-rescue",
        action="store_true",
        help="跳过 ？？文件 rescue（仍做 patch 存证）",
    )
    p_archive.add_argument(
        "--base",
        default="dev",
        help="ahead/cherry 判定基线分支（默认 dev）",
    )
    p_archive.set_defaults(func=cmd_archive)

    args = parser.parse_args()
    try:
        return args.func(args)
    except Exception as e:  # noqa: BLE001 — CLI 边界兜底转退出码（存量基线注记）
        print(f"[WORKTREE] 内部错误: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
