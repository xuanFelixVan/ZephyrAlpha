# [BLUEPRINT] MOD-INF-005 | scripts/rollback.py | §
# [MODULE] scripts.rollback
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__; zephyr.infrastructure.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""
Rollback System CLI — MOD-INF-021 v0.10.0 Git-native+SQLite Checkpoint 操作入口。

用法:
    python scripts/rollback.py full_revert <commit_sha> [--dry-run]
    python scripts/rollback.py partial_revert <commit_sha> <file_globs...> [--dry-run]
    python scripts/rollback.py discard <files...> [--force]
    python scripts/rollback.py hard_reset <commit_sha> <token>
    python scripts/rollback.py preview <commit_sha>
    python scripts/rollback.py preflight
    python scripts/rollback.py status
    python scripts/rollback.py forward_fix_evaluate <commit_sha>
    python scripts/rollback.py dependency_impact <commit_sha>
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from zephyr.infrastructure.rollback.rollback_executor import RollbackExecutor

from zephyr.infrastructure.rollback.rollback_verifier import RollbackVerifier


def _executor() -> RollbackExecutor:
    return RollbackExecutor(project_root=Path.cwd())


def _verifier() -> RollbackVerifier:
    return RollbackVerifier(project_root=Path.cwd())


def cmd_full_revert(args: argparse.Namespace) -> int:
    executor = _executor()
    result = executor.full_revert(args.commit_sha, dry_run=args.dry_run, audit_session="rollback_cli")
    _print_result(result)
    return 0 if result.success else 1


def cmd_partial_revert(args: argparse.Namespace) -> int:
    executor = _executor()
    result = executor.partial_revert(
        args.commit_sha, file_globs=args.file_globs, dry_run=args.dry_run, audit_session="rollback_cli"
    )
    _print_result(result)
    return 0 if result.success else 1


def cmd_discard(args: argparse.Namespace) -> int:
    executor = _executor()
    discard_result = executor.discard_changes(args.files, force=args.force, audit_session="rollback_cli")
    print(
        json.dumps(
            {
                "success": discard_result.success,
                "files_discarded": discard_result.files_discarded,
                "files_blocked": discard_result.files_blocked,
                "decision": discard_result.decision.value,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if discard_result.success else 1


def cmd_hard_reset(args: argparse.Namespace) -> int:
    executor = _executor()
    result = executor.hard_reset(args.commit_sha, token=args.token, audit_session="rollback_cli")
    _print_result(result)
    return 0 if result.success else 1


def cmd_preview(args: argparse.Namespace) -> int:
    executor = _executor()
    preview = executor.preview(args.commit_sha)
    print(
        json.dumps(
            {
                "changed_files": preview.changed_files,
                "conflict_risk": preview.conflict_risk,
                "estimated_change_bytes": preview.estimated_change_bytes,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def cmd_preflight(args: argparse.Namespace) -> int:
    executor = _executor()
    pf = executor.preflight_check()
    print(
        json.dumps(
            {
                "passed": pf.passed,
                "working_tree_clean": pf.working_tree_clean,
                "not_detached_head": pf.not_detached_head,
                "remote_not_ahead": pf.remote_not_ahead,
                "not_in_rebase": pf.not_in_rebase,
                "not_in_merge": pf.not_in_merge,
                "errors": pf.errors,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if pf.passed else 1


def cmd_status(args: argparse.Namespace) -> int:
    executor = _executor()

    uncommitted = executor.get_uncommitted_files()
    staged = executor.get_staged_uncommitted_files()

    verifier = _verifier()
    try:
        g0 = verifier.g0_verify()
        g0_serializable = _safe_serialize(g0)
    except Exception as e:
        g0_serializable = {"error": str(e), "all_pass": False}

    pf = executor.preflight_check()

    status_data = {
        "preflight": _safe_serialize(pf),
        "working_tree": {
            "uncommitted_files": uncommitted,
            "staged_uncommitted_files": staged,
        },
        "g0_verify": g0_serializable,
    }

    print(json.dumps(status_data, ensure_ascii=False, indent=2))
    return 0 if pf.passed and g0_serializable.get("all_pass", False) else 1


def cmd_forward_fix_evaluate(args: argparse.Namespace) -> int:
    executor = _executor()
    eligible = executor.forward_fix_evaluate(args.commit_sha)
    print(json.dumps({"commit_sha": args.commit_sha, "forward_fix_eligible": eligible}))
    return 0


def cmd_dependency_impact(args: argparse.Namespace) -> int:
    executor = _executor()
    impact = executor.dependency_impact_analysis(args.commit_sha)
    print(json.dumps(impact, ensure_ascii=False, indent=2))
    return 0


def _safe_serialize(obj) -> dict:
    if hasattr(obj, "__dict__"):
        return {k: v for k, v in obj.__dict__.items() if not k.startswith("_")}
    if isinstance(obj, dict):
        return {k: _safe_serialize(v) if hasattr(v, "__dict__") else v for k, v in obj.items()}
    return obj


def _print_result(result) -> None:
    print(
        json.dumps(
            {
                "success": result.success,
                "operation": result.operation.value if hasattr(result.operation, "value") else str(result.operation),
                "commit_sha": result.commit_sha,
                "files_reverted": result.files_reverted,
                "db_tables_restored": result.db_tables_restored,
                "db_rows_restored": result.db_rows_restored,
                "execution_id": getattr(result, "execution_id", ""),
                "errors": result.errors,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Rollback System CLI — MOD-INF-021 v0.10.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    p_full = subparsers.add_parser("full_revert", help="git revert 全部 commit + SQLite dump restore")
    p_full.add_argument("commit_sha", help="目标 commit SHA")
    p_full.add_argument("--dry-run", action="store_true", help="预览模式，不实际执行")

    p_partial = subparsers.add_parser("partial_revert", help="按 file_globs 选择性 revert")
    p_partial.add_argument("commit_sha", help="目标 commit SHA")
    p_partial.add_argument("file_globs", nargs="+", help="要 revert 的文件 glob 列表")
    p_partial.add_argument("--dry-run", action="store_true", help="预览模式，不实际执行")

    p_discard = subparsers.add_parser("discard", help="丢弃未提交变更")
    p_discard.add_argument("files", nargs="+", help="要丢弃的文件列表")
    p_discard.add_argument("--force", action="store_true", help="强制丢弃，绕过 owner 检测")

    p_hard = subparsers.add_parser("hard_reset", help="git reset --hard (需 BREAK_GLASS token)")
    p_hard.add_argument("commit_sha", help="目标 commit SHA")
    p_hard.add_argument("token", help="BREAK_GLASS token")

    p_preview = subparsers.add_parser("preview", help="预览回滚影响范围")
    p_preview.add_argument("commit_sha", help="目标 commit SHA")

    subparsers.add_parser("preflight", help="Git 状态七维安全预检")

    subparsers.add_parser("status", help="综合状态报告 (preflight + working_tree + g0_verify)")

    p_ff = subparsers.add_parser("forward_fix_evaluate", help="评估是否适合 forward-fix 而非 revert")
    p_ff.add_argument("commit_sha", help="目标 commit SHA")

    p_dep = subparsers.add_parser("dependency_impact", help="分析回滚对模块依赖的影响")
    p_dep.add_argument("commit_sha", help="目标 commit SHA")

    args = parser.parse_args()

    _COMMANDS = {
        "full_revert": cmd_full_revert,
        "partial_revert": cmd_partial_revert,
        "discard": cmd_discard,
        "hard_reset": cmd_hard_reset,
        "preview": cmd_preview,
        "preflight": cmd_preflight,
        "status": cmd_status,
        "forward_fix_evaluate": cmd_forward_fix_evaluate,
        "dependency_impact": cmd_dependency_impact,
    }

    handler = _COMMANDS.get(args.command)
    if handler is None:
        parser.print_help()
        sys.exit(2)

    try:
        exit_code = handler(args)
        sys.exit(exit_code)
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}, ensure_ascii=False, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
