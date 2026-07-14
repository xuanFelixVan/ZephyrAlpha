# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/syncers/archive_rationale_log.py | §
# [MODULE] scripts.governance.d5_architecture.syncers.archive_rationale_log
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d5_architecture.syncers.__init__
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
# [TTL] task_bound
"""对标 HDEBT-01：rationale-log.md 体积 >150KB / 行数 >300 时，
将已完成 Stage 移至 archive/ 子目录，主文件仅保留最近 3 个 Stage。

用法:
  python scripts/governance/d5_architecture/archive_rationale_log.py [--dry-run]

  --dry-run: 仅显示将执行的操作，不实际修改文件
"""

from __future__ import annotations

import os

__manifest__ = """
dimensions: [D5]
priority: P2
timeout_seconds: 30
args:
  - {flag: --dry-run, type: bool, description: "仅预览，不修改文件"}
  - {flag: --warn-only, type: bool, description: "仅警告模式"}
warn_only: false
description: architecture-rationale-log.md 按 Stage 归档拆分——控制单文件体积
"""

import re
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import EXIT_ERROR, EXIT_PASS, REPO_ROOT
from _shared.encoding import ensure_utf8_stdout
from _shared.file_utils import atomic_write_safe  # noqa: E402  治本(ARCH-036 P1-1): 收敛本地 tmp+replace 样板→共享 SSoT

ensure_utf8_stdout()

RATIONALE_LOG = REPO_ROOT / "docs" / "02_enterprise_architecture" / "architecture-rationale-log.md"
ARCHIVE_DIR = REPO_ROOT / "docs" / "02_enterprise_architecture" / "archive" / "rationale-log"
MAX_STAGES_IN_MAIN = 3
LINE_THRESHOLD = 300  # noqa: gate-vocab  治本(ARCH-036 P3-A5): 归档日志行数阈值，脚本专用


def parse_stages(content: str) -> list[tuple[str, int, int]]:
    """parse_stages implementation."""
    stages = []
    for m in re.finditer(r"^## (Stage \d+[^\n]*)", content, re.MULTILINE):
        stages.append((m.group(1), m.start(), m.end()))
    return stages


def archive_old_stages(dry_run: bool = False) -> int:
    """archive_old_stages implementation."""
    if not RATIONALE_LOG.is_file():
        print("rationale-log.md 不存在")
        return EXIT_ERROR
    content = RATIONALE_LOG.read_text(encoding="utf-8")
    total_lines = content.count("\n") + 1
    print(f"rationale-log.md: {total_lines} 行")

    if total_lines <= LINE_THRESHOLD:
        print(f"行数未超过阈值 ({LINE_THRESHOLD})，无需归档")
        return EXIT_PASS
    stages = parse_stages(content)
    if len(stages) <= MAX_STAGES_IN_MAIN:
        print(f"Stage 数量 ({len(stages)}) 未超过保留阈值 ({MAX_STAGES_IN_MAIN})，无需归档")
        return EXIT_PASS
    stages_to_archive = stages[:-MAX_STAGES_IN_MAIN]
    print(f"将归档 {len(stages_to_archive)} 个旧 Stage，保留最近 {MAX_STAGES_IN_MAIN} 个")

    frontmatter_end = 0
    fm_match = re.search(r"^---\s*\n.*?\n---\s*\n", content, re.DOTALL)
    if fm_match:
        frontmatter_end = fm_match.end()

    for stage_title, start, _ in stages_to_archive:
        stage_num_match = re.search(r"Stage (\d+)", stage_title)
        stage_num = stage_num_match.group(1) if stage_num_match else "unknown"
        archive_filename = f"rationale-log-stage-{stage_num}.md"
        archive_path = ARCHIVE_DIR / archive_filename

        next_stage_idx = stages.index((stage_title, start, _)) + 1
        if next_stage_idx < len(stages):
            stage_content = content[start : stages[next_stage_idx][1]]
        else:
            stage_content = content[start:]

        if dry_run:
            print(f"  [DRY-RUN] 归档: {stage_title} → {archive_path.relative_to(REPO_ROOT)}")
        else:
            ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
            atomic_write_safe(archive_path, f"# {stage_title}\n\n{stage_content}")
            print(f"  归档: {stage_title} → {archive_path.relative_to(REPO_ROOT)}")

    if not dry_run:
        last_keep_start = stages[-MAX_STAGES_IN_MAIN][1]
        new_content = (
            content[:frontmatter_end]
            + "\n> 历史归档：旧 Stage 已移至 archive/rationale-log/\n\n"
            + content[last_keep_start:]
        )
        atomic_write_safe(RATIONALE_LOG, new_content)
        print(f"主文件已精简：{new_content.count(chr(10)) + 1} 行")

    return EXIT_PASS


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    dry_run = "--dry-run" in sys.argv
    return archive_old_stages(dry_run)


if __name__ == "__main__":
    sys.exit(main())
