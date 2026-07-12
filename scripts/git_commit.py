# [BLUEPRINT] MOD-INF-005 | scripts/git_commit.py | §ghost-commit-gateway-cli
# [MODULE] scripts.git_commit
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.governance.__init__; zephyr.gov_enforcement.rule_bridge.git_commit_gateway
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] 全项目唯一合法 git commit CLI 入口；封装 GitCommitGateway；禁止裸 git commit（GATE-COMMIT-GW 门禁）
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exit 0=commit成功; exit 1=commit失败/无变更; exit 2=锁超时/stash冲突; exit 3=永久区晋升阻断; exit 4=SSOT违规; exit 5=搭便车防护阻断(HELD_OVERLAP_VIOLATION); exit 6=claim_files前置检查阻断(CLAIM_REQUIRED_VIOLATION); exit 7=claim-only部分文件被其他session持有(冲突跳过)
# [TESTS] tests/test_git_commit_gateway.py
# [A_module] module_id=MOD-GOV-git_commit_cli | layer=script | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""git_commit.py — GitCommitGateway CLI 封装（OPS-2026062512）

全项目唯一合法 git commit 命令行入口。封装 GitCommitGateway，串行化所有 commit。

用法::

    python scripts/git_commit.py --session <id> --files <f1,f2> --message <msg>
    python scripts/git_commit.py --session sess-001 --files src/a.py,src/b.py --message "feat: add"

    # 含中文/特殊字符的 message——用 --message-file 避免 PowerShell 编码问题（治本）：
    python scripts/git_commit.py --session sess-001 --files src/a.py --message-file .runtime/_commit_msg.txt

对标: scripts/git_guard.py（git 命令透传封装），区别：
- git_guard.py 透传 git 子命令（绕过 Trae 弹窗）
- git_commit.py 强制走 GitCommitGateway（串行锁+stash 隔离+GW 标记）

exit codes: 0=commit成功, 1=commit失败/无变更, 2=锁超时/stash冲突, 5=搭便车防护阻断, 6=claim_files前置检查阻断, 7=claim-only部分冲突
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import (  # noqa: E402
    CommitStatus,
    GitCommitGateway,
)

logger = logging.getLogger(__name__)

# commit 结果状态查表：CommitStatus → (exit_code, line_template, help_text, to_stdout)
# line_template 使用 {message}/{commit_hash}/{stash_ref} 占位符；
# 未列出的状态走 _COMMIT_RESULT_DEFAULT（exit 1, FAILED）。
_COMMIT_RESULT_MAP: dict[CommitStatus, tuple[int, str, str | None, bool]] = {
    CommitStatus.OK: (0, "OK: {message} (hash={commit_hash})", None, True),
    CommitStatus.NOTHING_TO_COMMIT: (1, "SKIP: {message}", None, True),
    CommitStatus.LOCK_TIMEOUT: (2, "LOCK_TIMEOUT: {message}", None, False),
    CommitStatus.STASH_CONFLICT: (
        2,
        "STASH_CONFLICT: {message}",
        "  stash_ref={stash_ref} (数据保留在 stash，未丢失)",
        False,
    ),
    CommitStatus.PROMOTION_BLOCKED: (
        3,
        "PROMOTION_BLOCKED: {message}",
        "  如确认晋升到永久区，请在终端手动添加 --allow-promote 重新执行。",
        False,
    ),
    CommitStatus.SSOT_VIOLATION: (
        4,
        "SSOT_VIOLATION: {message}",
        "  新增文件声明了已有 module_path——请扩展已有文件而非新建。",
        False,
    ),
    CommitStatus.HELD_OVERLAP_VIOLATION: (
        5,
        "HELD_OVERLAP_VIOLATION: {message}",
        "  目标文件被其他活跃 session 持有（搭便车防护）。"
        "  如确认需提交，请在终端手动添加 --allow-overlap 重新执行。",
        False,
    ),
    CommitStatus.CLAIM_REQUIRED_VIOLATION: (
        6,
        "CLAIM_REQUIRED_VIOLATION: {message}",
        "  session 已注册但目标文件未 claim_files（红蓝对抗红攻1治本）。"
        "  commit 前 MUST 调 claim_files 声明工作范围（AGENTS.md §8 L284）。"
        "  如确认需提交，请在终端手动添加 --allow-overlap 重新执行。",
        False,
    ),
}
# 默认 fallback：COMMIT_FAILED / METADATA_VIOLATION / NAMING_VIOLATION / 等
_COMMIT_RESULT_DEFAULT: tuple[int, str, str | None, bool] = (1, "FAILED: {message}", None, False)


def _format_commit_result(result) -> int:
    """查表分发 commit 结果状态 → 统一 print + return exit_code。

    替代原 main() 中 9 路 if/elif 状态分发（L340-386），复杂度 5。
    """
    exit_code, line_template, help_text, to_stdout = _COMMIT_RESULT_MAP.get(
        result.status, _COMMIT_RESULT_DEFAULT
    )
    out = sys.stdout if to_stdout else sys.stderr
    line = line_template.format(
        message=result.message,
        commit_hash=(result.commit_hash[:8] if result.commit_hash else ""),
        stash_ref=getattr(result, "stash_ref", ""),
    )
    print(line, file=out)
    if help_text:
        print(
            help_text.format(stash_ref=getattr(result, "stash_ref", "")),
            file=out,
        )
    return exit_code


def _parse_files(files_arg: str) -> list[str]:
    """解析逗号分隔的文件列表，归一化为绝对路径。"""
    if not files_arg:
        return []
    parts = [f.strip() for f in files_arg.split(",") if f.strip()]
    # 归一化为绝对路径（相对路径基于 cwd 解析）
    # 注意：用 abspath 而非 resolve()——resolve() 在 Windows 上会规范化为
    # 物理目录的真实大小写，当 on-disk 与 git index 大小写不一致时（如 09_audit vs 09_AUDIT）
    # 会导致后续 git add/commit 的 pathspec 不匹配。abspath 保留传入路径大小写。
    return [os.path.abspath(f) for f in parts]


def _check_staged_delete_fallback(
    files: list[str], project_root: str
) -> tuple[list[str], list[str]]:
    """校验文件存在性，允许 staged delete（git rm）场景回退校验。

    覆盖两种删除场景：
      (A) unstaged delete: 文件仍在 index，``git ls-files --error-unmatch`` 命中
      (B) staged delete (git rm): 文件已从 index 移除但仍在 HEAD，
          ``git ls-files`` 失败，需回退 ``git ls-files --with-tree=HEAD`` 校验

    integrity_anchors: 本函数含 staged delete 回退校验（--with-tree=HEAD），
    禁止删除回退逻辑，否则 staged delete 提交会被误拦（commit 05e7510f 治本）。

    Args:
        files: 待提交文件绝对路径列表
        project_root: 项目根目录

    Returns:
        (truly_missing, tracked_but_deleted) 元组：
        - truly_missing: 文件不存在且未被 git 跟踪（应阻断）
        - tracked_but_deleted: 文件不存在但被 git 跟踪（staged delete，应放行）
    """
    missing = [f for f in files if not os.path.isfile(f)]
    if not missing:
        return [], []

    import subprocess as _sp
    truly_missing: list[str] = []
    for f in missing:
        rel = os.path.relpath(f, project_root)
        # :(icase) 与 GitCommitGateway._is_git_tracked 保持一致——
        # Windows 文件系统大小写不敏感但 git pathspec 默认大小写敏感，
        # 不加 :(icase) 会导致 on-disk 路径大小写与 git index 不一致时误报"未跟踪"
        chk = _sp.run(
            ["git", "ls-files", "--error-unmatch", "--", f":(icase){rel}"],
            capture_output=True, cwd=project_root,
        )
        if chk.returncode != 0:
            # 场景 B: staged delete (git rm) — 文件已从 index 移除，
            # 回退检查 HEAD 是否仍跟踪该文件
            chk2 = _sp.run(
                ["git", "ls-files", "--error-unmatch", "--with-tree=HEAD",
                 "--", f":(icase){rel}"],
                capture_output=True, cwd=project_root,
            )
            if chk2.returncode != 0:
                truly_missing.append(f)
    return truly_missing, missing


def _validate_reconciler_verify(
    args, is_pure_claim: bool, message: str, project_root: str
) -> tuple[int | None, str]:
    """reconciler-verify 模式前置校验（豁免 worktree 君子协定的三重防护）。

    提取自原 main() L246-299，复杂度 10。

    Returns:
        (exit_code, message) — exit_code 非 None 时 main 应立即 return；
        message 为可能追加 [RECONCILER-VERIFY] 标记后的新 message。
    """
    if not args.reconciler_verify:
        return None, message

    # 裁定 2026-07-02：reconciler 操作主分支数据无法在 worktree 内运行，验证场景豁免君子协定，
    # 但须三重防护覆盖搭便车风险：干净环境 + 单 session + claim_files 全部成功。
    # 互斥校验：reconciler-verify 是 commit 场景，与 claim-only/release-only 互斥
    if is_pure_claim:
        print("ERROR: --reconciler-verify 与 --claim-only/--release-only 互斥", file=sys.stderr)
        return 1, message
    # 条件1：主工作区必须 clean（无搭便车窗口——共享 index 下 dirty 工作区有污染风险）
    import subprocess as _rv_sp
    status_r = _rv_sp.run(
        ["git", "status", "--short"],
        capture_output=True, text=True, cwd=project_root,
        encoding="utf-8", errors="replace",
    )
    if status_r.returncode != 0:
        print(f"ERROR: --reconciler-verify: git status 检查失败: {status_r.stderr.strip()}",
              file=sys.stderr)
        return 1, message
    if status_r.stdout.strip():
        print(
            "ERROR: --reconciler-verify: 主工作区不 clean（有未提交改动），存在搭便车风险。\n"
            "请先 commit/stash 其他改动或等待其他 session 完成。\n"
            f"git status --short 输出:\n{status_r.stdout.strip()}",
            file=sys.stderr,
        )
        return 1, message
    # 条件2：无其他活跃 session（除非 --allow-concurrent 逃生通道）
    if not args.allow_concurrent:
        try:
            from zephyr.security.access_control.session_concurrency import SessionRegistry
            _rv_reg = SessionRegistry(project_root)
            _rv_active = _rv_reg.list_active()
            # list_active 返回 list[SessionInfo]（dataclass），用属性而非 dict.get
            _rv_others = [s for s in _rv_active if s.pid != os.getpid()]
            if _rv_others:
                print(
                    f"ERROR: --reconciler-verify: 检测到 {len(_rv_others)} 个其他活跃 session，"
                    f"违反单 session 诊断场景约束。sessions: "
                    f"{[s.session_id for s in _rv_others]}\n"
                    "如确认需并发验证，用 --allow-concurrent 逃生通道。",
                    file=sys.stderr,
                )
                return 1, message
        except Exception as e:
            print(f"WARN: --reconciler-verify: session 检查异常（降级放行）: {e}", file=sys.stderr)
    # 条件3：--allow-overlap 与 reconciler-verify 互斥（claim_files 必须全部成功）
    if args.allow_overlap:
        print(
            "ERROR: --reconciler-verify 与 --allow-overlap 互斥——验证场景 claim_files 必须全部成功，"
            "不允许搭便车逃生通道。",
            file=sys.stderr,
        )
        return 1, message
    # 自动追加 [RECONCILER-VERIFY] 标记（供 GATE-COMMIT-GW-AUDIT 事后审计追溯豁免通道使用，
    # 不依赖人手动加——形成"事前三重校验 + 事后审计追溯"闭环）
    message = f"{message} [RECONCILER-VERIFY]"
    return None, message


def _handle_pure_claim(gw, args, files: list[str]) -> int | None:
    """claim-only / release-only 快速路径（claim 前移协议，不进入 commit 流程）。

    提取自原 main() L301-315，复杂度 4。

    Returns:
        exit_code — 非 None 时 main 应立即 return；None 表示非快速路径，继续标准流程。
    """
    if args.release_only:
        gw.release_files(args.session, files)
        print(f"RELEASED: {len(files)} files (session={args.session})")
        return 0
    if args.claim_only:
        claimed = gw.claim_files(args.session, files)
        conflicts = [f for f in files if f not in claimed]
        if conflicts:
            print(f"CONFLICT: {len(conflicts)} files held by other session: {conflicts}", file=sys.stderr)
            print(f"CLAIMED: {len(claimed)}/{len(files)} files (session={args.session})")
            return 7
        print(f"CLAIMED: {len(claimed)}/{len(files)} files (session={args.session})")
        return 0
    return None


def _parse_message(args) -> tuple[int | None, str, bool]:
    """解析 commit message（claim-only/release-only 时不需要 message）。

    提取自原 main() message 解析段，复杂度 7。

    Returns:
        (exit_code, message, is_pure_claim) — exit_code 非 None 时 main 应立即 return。
    """
    is_pure_claim = args.claim_only or args.release_only
    if is_pure_claim:
        return None, "", True
    if args.message_file:
        try:
            return None, Path(args.message_file).read_text(encoding="utf-8"), False
        except (OSError, UnicodeDecodeError) as e:
            print(f"ERROR: --message-file 读取失败: {e}", file=sys.stderr)
            return 1, "", False
    if args.message:
        message = args.message
    else:
        print("ERROR: 必须提供 --message 或 --message-file", file=sys.stderr)
        return 1, "", False
    if not message.strip():
        print("ERROR: message 不能为空", file=sys.stderr)
        return 1, "", False
    return None, message, False


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="git_commit.py",
        description="GitCommitGateway CLI——全项目唯一合法 git commit 入口（串行锁+stash隔离+GW标记）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "示例:\n"
            '  python scripts/git_commit.py --session sess-001 --files src/a.py,src/b.py --message "feat: add"\n'
            "\n"
            "对标 git_guard.py: git_guard 透传 git 子命令；本脚本强制走 GitCommitGateway。\n"
            "exit codes: 0=成功, 1=失败/无变更, 2=锁超时/stash冲突, 3=永久区晋升阻断, 4=SSoT违规, 5=搭便车防护阻断, 6=claim_files前置检查阻断, 7=claim-only部分冲突"
        ),
    )
    parser.add_argument(
        "--session",
        required=True,
        help="AI session 标识（用于 GW 标记 + stash message）",
    )
    parser.add_argument(
        "--files",
        required=True,
        help="本次 commit 的文件列表，逗号分隔（相对路径基于 cwd 解析）",
    )
    parser.add_argument(
        "--message",
        help="commit message（不含 GW 标记，自动追加 [GW:<session>]）。"
             "含中文/特殊字符时推荐用 --message-file 避免 shell 编码问题",
    )
    parser.add_argument(
        "--message-file",
        help="从 UTF-8 文件读取 commit message（治本 PowerShell 中文编码问题）。"
             "提供时优先于 --message。文件内容原样作为 message（不含 GW 标记）",
    )
    parser.add_argument(
        "--project-root",
        default=str(_PROJECT_ROOT),
        help="项目根目录（默认: 脚本所在仓库根）",
    )
    parser.add_argument(
        "--allow-promote",
        action="store_true",
        default=False,
        help="批准新文件晋升到永久区（docs/01_policies/、02_enterprise_architecture/、"
             "03_modules/、08_knowledge/）。AI 不得自行使用——须用户终端手动指定。",
    )
    parser.add_argument(
        "--allow-overlap",
        action="store_true",
        default=False,
        help="搭便车防护逃生通道——目标文件被其他活跃 session 持有时放行"
             "（HELD_OVERLAP_VIOLATION）。commit message 追加 [GW:<sid>:overlap] 标记"
             "供审计追踪。AI 不得自行使用——须用户终端手动指定。",
    )
    parser.add_argument(
        "--claim-only",
        action="store_true",
        default=False,
        help="仅 claim_files 声明持有，不 commit（claim 前移协议：Edit 前调用）。"
             "exit 0=全部 claim 成功, exit 7=部分文件被其他 session 持有（冲突跳过）",
    )
    parser.add_argument(
        "--release-only",
        action="store_true",
        default=False,
        help="仅 release_files 释放持有，不 commit（claim 前移协议：Edit 中断/结束时调用）",
    )
    parser.add_argument(
        "--reconciler-verify",
        action="store_true",
        default=False,
        help="reconciler 实弹验证专用通道（豁免 worktree 君子协定）。前置条件："
             "(1) 主工作区 clean (2) 无其他活跃 session（或用 --allow-concurrent 逃生）"
             "(3) claim_files 全部成功（--allow-overlap 自动禁用）。"
             "豁免理由：reconciler 操作主分支数据无法在 worktree 内运行，且验证为单 session 诊断场景，"
             "搭便车风险由 claim_files+串行锁+干净环境三重防护覆盖。详见 AGENTS.md RULE-WORKTREE 豁免条款。",
    )
    parser.add_argument(
        "--allow-concurrent",
        action="store_true",
        default=False,
        help="reconciler-verify 模式下放行其他活跃 session 检查（逃生通道）。"
             "默认硬阻断——验证前必须无其他活跃 session，确保单 session 诊断场景无搭便车窗口。",
    )
    args = parser.parse_args()

    # message 解析（claim-only / release-only 时不需要 message）
    msg_exit, message, is_pure_claim = _parse_message(args)
    if msg_exit is not None:
        return msg_exit

    files = _parse_files(args.files)
    if not files:
        print("ERROR: --files 不能为空", file=sys.stderr)
        return 1

    # 校验文件存在性（允许 staged delete 回退——见 _check_staged_delete_fallback）
    truly_missing, tracked_but_deleted = _check_staged_delete_fallback(
        files, args.project_root
    )
    if truly_missing:
        print(f"ERROR: 文件不存在且未被 git 跟踪: {truly_missing}", file=sys.stderr)
        return 1
    if tracked_but_deleted:
        logger.info("以下文件已跟踪但工作区已删除（将作为删除提交）: %s", tracked_but_deleted)

    try:
        gw = GitCommitGateway(project_root=args.project_root)
    except Exception as e:
        print(f"ERROR: GitCommitGateway 初始化失败: {e}", file=sys.stderr)
        return 2

    # reconciler-verify 模式前置校验（豁免 worktree 君子协定的三重防护）
    rv_exit, message = _validate_reconciler_verify(
        args, is_pure_claim, message, args.project_root
    )
    if rv_exit is not None:
        return rv_exit

    # claim-only / release-only 快速路径（claim 前移协议，不进入 commit 流程）
    pc_exit = _handle_pure_claim(gw, args, files)
    if pc_exit is not None:
        return pc_exit

    # 标准路径：claim → commit → release（claim 前移协议下 Edit 前已 claim，此处幂等）
    claimed = gw.claim_files(args.session, files)
    # reconciler-verify 模式：claim_files 必须全部成功（无搭便车逃生通道）
    if args.reconciler_verify and len(claimed) != len(files):
        conflicts = [f for f in files if f not in claimed]
        gw.release_files(args.session, claimed)
        print(
            f"ERROR: --reconciler-verify: claim_files 部分失败，{len(conflicts)} 个文件被其他 session 持有: {conflicts}\n"
            "验证场景不允许搭便车窗口，等待对方释放后重试。",
            file=sys.stderr,
        )
        return 1
    try:
        result = gw.commit(
            session_id=args.session,
            files=files,
            message=message,
            allow_promote=args.allow_promote,
            allow_overlap=args.allow_overlap,
        )
    finally:
        gw.release_files(args.session, claimed)

    return _format_commit_result(result)


if __name__ == "__main__":
    sys.exit(main())
