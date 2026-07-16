# [BLUEPRINT] MOD-INF-005 | scripts/governance/cleanup_stash.py | §git-stash-governance
# [MODULE] scripts.governance.cleanup_stash
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] stash 数量 ≤ MAX_STASHES（默认5）；超过时 WARNING；超过 CRITICAL_STASHES（10）时建议清理
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GOV-cleanup_stash | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""cleanup_stash.py — git stash 堆积治理（OPS-2026062501 治本）

对标：OPS-2026062501 病根3（stash 堆积无清理机制）

功能：
- --check: 检查 stash 数量，超过阈值时告警（不阻断，exit=0）
- --cleanup: 清理过期 stash，保留最近 N 个（默认 KEEP_COUNT=3）
- --archive: 导出 stash 列表到归档文件

设计原则（对标专业机构实践）：
- GitHub/Linux：stash 是临时栈，不鼓励长期堆积
- AI 开发社区：commit-early strategy 避免累积，stash 仅临时隔离
- 本脚本：定期检查 + 超阈值清理，防止 stash 堆积

exit codes: 0=pass/warn, 1=cleanup_needed, 2=error
"""

from __future__ import annotations
from _shared.constants import REPO_ROOT

__manifest__ = """
args:
- {flag: --check, description: "检查 stash 数量，超过阈值时告警"}
- {flag: --cleanup, description: "清理过期 stash，保留最近 N 个"}
- {flag: --archive, description: "导出 stash 列表到归档文件"}
- {flag: --keep, type: int, default: 3, description: "保留最近 N 个 stash"}
- {flag: --max, type: int, default: 5, description: "告警阈值"}
- {flag: --critical, type: int, default: 10, description: "严重阈值，建议清理"}
description: >
  git stash 堆积治理——检查/清理/归档 stash。
  对标 OPS-2026062501 病根3（stash 堆积无清理机制）。
dimensions:
- D7
priority: P2
timeout_seconds: 30
warn_only: true
"""

import argparse
import subprocess
import sys
from pathlib import Path

_REPO_ROOT = REPO_ROOT

# 阈值常量
MAX_STASHES = 5  # 超过时 WARNING
CRITICAL_STASHES = 10  # 超过时建议清理
KEEP_COUNT = 3  # 清理时保留最近 N 个
# 归档目录：stash 归档快照是本地运行时产物（git stash 设计为本地临时栈），
# 不应入库 VCS。落在 .runtime/ 下（已被 .gitignore 排除）。
# 历史：原路径 docs/19_development_workspace/ 已于 2026-06-26 退役删除。
ARCHIVE_DIR = _REPO_ROOT / ".runtime" / "stash_archive"


def get_stash_list() -> list[str]:
    """获取 stash 列表，返回每行一个 stash 的列表。"""
    result = subprocess.run(
        ["git", "stash", "list", "--format=%gd|%ci|%gs"],
        cwd=str(_REPO_ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        return []
    output = result.stdout.strip()
    if not output:
        return []
    return output.split("\n")


def archive_stashes(archive_path: Path | None = None) -> Path:
    """导出 stash 列表到归档文件。"""
    if archive_path is None:
        archive_path = ARCHIVE_DIR / "stash_archive_latest.csv"

    archive_path.parent.mkdir(parents=True, exist_ok=True)
    stash_list = get_stash_list()

    with open(archive_path, "w", encoding="utf-8") as f:
        f.write("stash_ref|date|message\n")
        for line in stash_list:
            f.write(line + "\n")

    return archive_path


def cleanup_stashes(keep: int = KEEP_COUNT) -> int:
    """清理过期 stash，保留最近 N 个。返回删除数量。"""
    stash_list = get_stash_list()
    total = len(stash_list)

    if total <= keep:
        return 0

    delete_count = total - keep
    deleted = 0

    for i in range(delete_count):
        # 每次删除 stash@{keep}，删除后后面的 stash 索引前移
        result = subprocess.run(
            ["git", "stash", "drop", f"stash@{{{keep}}}"],
            cwd=str(_REPO_ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if result.returncode == 0:
            deleted += 1
        else:
            print(f"[ERROR] Failed to drop stash@{{{keep}}}: {result.stderr}", file=sys.stderr)

    return deleted


def check_stashes(max_threshold: int = MAX_STASHES, critical_threshold: int = CRITICAL_STASHES) -> int:
    """检查 stash 数量，返回 exit code。

    exit codes:
        0 = 正常（stash 数 ≤ max_threshold）
        1 = 需要清理（stash 数 > critical_threshold）
    """
    stash_list = get_stash_list()
    count = len(stash_list)

    if count <= max_threshold:
        print(f"[OK] stash count = {count} (<= {max_threshold})")
        return 0
    elif count <= critical_threshold:
        print(f"[WARNING] stash count = {count} (> {max_threshold}) — consider cleanup")
        for line in stash_list:
            print(f"  {line}")
        return 0
    else:
        print(f"[CRITICAL] stash count = {count} (> {critical_threshold}) — cleanup needed!")
        for line in stash_list:
            print(f"  {line}")
        return 1


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="git stash 堆积治理（OPS-2026062501）")
    parser.add_argument("--check", action="store_true", help="检查 stash 数量")
    parser.add_argument("--cleanup", action="store_true", help="清理过期 stash")
    parser.add_argument("--archive", action="store_true", help="导出 stash 列表归档")
    parser.add_argument("--keep", type=int, default=KEEP_COUNT, help=f"保留最近 N 个（默认 {KEEP_COUNT}）")
    parser.add_argument("--max", type=int, default=MAX_STASHES, help=f"告警阈值（默认 {MAX_STASHES}）")
    parser.add_argument("--critical", type=int, default=CRITICAL_STASHES, help=f"严重阈值（默认 {CRITICAL_STASHES}）")
    args = parser.parse_args()

    if not any([args.check, args.cleanup, args.archive]):
        print("Usage: cleanup_stash.py --check | --cleanup | --archive [--keep N] [--max M] [--critical C]")
        sys.exit(2)

    if args.archive:
        archive_path = archive_stashes()
        print(f"[OK] Archive saved to: {archive_path}")

    if args.check:
        exit_code = check_stashes(args.max, args.critical)
        sys.exit(exit_code)

    if args.cleanup:
        # 先归档
        archive_path = archive_stashes()
        print(f"[OK] Archive saved to: {archive_path}")

        # 清理
        deleted = cleanup_stashes(args.keep)
        print(f"[OK] Deleted {deleted} stashes (kept latest {args.keep})")

        # 验证
        remaining = get_stash_list()
        print(f"[INFO] Remaining stash count: {len(remaining)}")
        for line in remaining:
            print(f"  {line}")

    sys.exit(0)


if __name__ == "__main__":
    main()
