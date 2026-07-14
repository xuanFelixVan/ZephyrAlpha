# [BLUEPRINT] MOD-INF-005 | scripts/governance/d3_metadata/backfill_doctype_metadata.py | §gate-15
# [MODULE] governance.d3_metadata.backfill_doctype_metadata
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] zephyr.governance._shared.frontmatter; _shared.constants; _shared.encoding
# [CONSUMERS] manual batch backfill; stage-2 of doc_type root-cause fix
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 只回填有 frontmatter 但无 doc_type 的 .md；路径判定仅用无歧义规则；原子写入
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] EXIT_PASS=0（无错误）；EXIT_FINDINGS=1（有文件异常）；EXIT_ERROR=2（脚本异常）
# [TESTS] 手动测试：dry-run + 全量回填 + 抽样验证
# [TTL] task_bound
"""批量回填 frontmatter doc_type 字段（doc_type 存量治理 Stage 2.1）

对有 frontmatter 但缺 doc_type 字段的 .md 文件，按无歧义路径规则注入 doc_type。
歧义路径（如 03_blueprints/ 下的 blueprint/design/construction_plan 三选一）跳过，
留给 Stage 2.3 AI 内容判定。

判定口径（源自 doc_type_governance_plan.md 第 5 节无歧义路径规则表）：
  - 文件名 index.md → index（文件名固定绑定）
  - 文件名 README.md → readme（文件名固定绑定）
  - docs/08_knowledge/ 下 → knowledge_entry（目录强绑定，99.6% 是 ke 文件）
  - _registry/vocabularies/ → vocabulary（目录强绑定）
  - _registry/schemas/ → schema（目录强绑定）
  - _registry/contracts/ → contract（目录强绑定）
  - 其余 → skip_ambiguous（路径无法无歧义判定，走 2.3 内容判定）

GATE-15 当前只校验 ttl 不校验 doc_type（实测 check_frontmatter_metadata.py:71-97），
因此回填 doc_type 不会被门禁阻断。doc_type 校验属 Stage 3 工作。

Usage::

    # dry-run（只报告，不写入）
    python scripts/governance/d3_metadata/backfill_doctype_metadata.py --dry-run

    # 全量回填
    python scripts/governance/d3_metadata/backfill_doctype_metadata.py

    # 限定子目录
    python scripts/governance/d3_metadata/backfill_doctype_metadata.py docs/08_knowledge/01_raw_intake/
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 批量回填 frontmatter doc_type 字段（doc_type 存量治理 Stage 2.1）
dimensions:
- D3
priority: P2
timeout_seconds: 60
warn_only: false
"""


import os
import re
import sys
from pathlib import Path

# ── 路径设置 ──
_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import EXIT_FINDINGS, EXIT_PASS, REPO_ROOT  # noqa: E402
from _shared.encoding import ensure_utf8_stdout  # noqa: E402
from _shared.frontmatter import _FM_END_PATTERN, parse_frontmatter  # noqa: E402  # SSoT 治本 2026-07-02 (ARCH-033 Phase 7)

ensure_utf8_stdout()

# _FM_END_PATTERN 已改为从 _shared.frontmatter import（SSoT 治本 2026-07-02, ARCH-033 Phase 7）


def _infer_doctype(rel_path: str, filename: str) -> str | None:
    """按无歧义路径规则判定 doc_type 值。

    Args:
        rel_path: 相对 REPO_ROOT 的路径（正斜杠）。
        filename: 文件名（如 "index.md"）。

    Returns:
        doc_type 值（如 "vocabulary"），或 None 表示路径有歧义。
        规则按特异性排序：文件名绑定优先于目录绑定。
    """
    # 文件名固定绑定（最高优先级，任何目录下都成立）
    if filename == "index.md":
        return "index"
    if filename == "README.md":
        return "index"

    # 目录强绑定
    if rel_path.startswith("docs/08_knowledge/"):
        return "vocabulary"
    if "_registry/vocabularies/" in rel_path:
        return "vocabulary"
    if "_registry/schemas/" in rel_path:
        return "gate"  # v3.0.0: schema 已废弃，合并到 gate
    if "_registry/contracts/" in rel_path:
        return "gate"

    # 路径有歧义——无法无歧义判定
    return None


def backfill_file(fpath: Path, dry_run: bool = False) -> str:
    """回填单个文件的 doc_type 字段。

    Args:
        fpath: .md 文件绝对路径。
        dry_run: True 则只报告不写入。

    Returns:
        "backfilled"（已回填）、"skip_has_doctype"（已有 doc_type）、
        "skip_no_fm"（无 frontmatter）、"skip_ambiguous"（路径有歧义）、
        "error"（异常）。
    """
    try:
        text = fpath.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return "error"

    # 无 frontmatter 的文件跳过
    if not text.startswith("---"):
        return "skip_no_fm"

    # 检查是否已有 doc_type
    metadata, _ = parse_frontmatter(text)
    if not metadata:
        return "skip_no_fm"
    if metadata.get("doc_type"):
        return "skip_has_doctype"

    # 路径判定
    rel_path = str(fpath.relative_to(REPO_ROOT)).replace("\\", "/")
    doctype_value = _infer_doctype(rel_path, fpath.name)
    if doctype_value is None:
        return "skip_ambiguous"

    # 定位 frontmatter 结束符
    fm_end_match = _FM_END_PATTERN.search(text[3:])
    if not fm_end_match:
        # frontmatter 未闭合，跳过（不修复格式问题）
        return "skip_no_fm"

    # 在闭合 --- 前插入 doc_type 行
    end_pos = 3 + fm_end_match.start()
    new_text = text[: end_pos + 1] + f"doc_type: {doctype_value}\n" + text[end_pos + 1 :]

    if dry_run:
        return "backfilled"

    # 原子写入（tmp + os.replace，并发安全）
    _atomic_write(fpath, new_text)
    return "backfilled"


def _atomic_write(fpath: Path, content: str) -> None:
    """原子写入文件（tmp + os.replace）。

    确保并发安全：写入过程中崩溃不会留下半截文件。
    """
    tmp_path = fpath.with_suffix(fpath.suffix + ".tmp")
    try:
        tmp_path.write_text(content, encoding="utf-8", newline="\n")
        os.replace(tmp_path, fpath)
    except Exception:
        if tmp_path.exists():
            try:
                tmp_path.unlink()
            except OSError:
                pass
        raise


def main() -> int:
    # 解析参数
    args = sys.argv[1:]
    dry_run = "--dry-run" in args
    path_args = [a for a in args if not a.startswith("-")]

    # 确定扫描范围
    if path_args:
        scan_dirs = [(REPO_ROOT / p).resolve() for p in path_args]
    else:
        scan_dirs = [REPO_ROOT / "docs"]

    # 收集所有 .md 文件
    md_files: list[Path] = []
    for scan_dir in scan_dirs:
        if scan_dir.is_file() and scan_dir.suffix == ".md":
            md_files.append(scan_dir)
        elif scan_dir.is_dir():
            md_files.extend(scan_dir.rglob("*.md"))

    if not md_files:
        print("OK: no .md files to backfill")
        return EXIT_PASS

    # 统计
    stats = {
        "backfilled": 0,
        "skip_has_doctype": 0,
        "skip_no_fm": 0,
        "skip_ambiguous": 0,
        "error": 0,
    }
    doctype_counts: dict[str, int] = {}

    for fpath in md_files:
        result = backfill_file(fpath, dry_run=dry_run)
        stats[result] += 1
        if result == "backfilled":
            rel_path = str(fpath.relative_to(REPO_ROOT)).replace("\\", "/")
            dt = _infer_doctype(rel_path, fpath.name)
            if dt:
                doctype_counts[dt] = doctype_counts.get(dt, 0) + 1

    # 输出统计报告
    mode_label = "DRY-RUN" if dry_run else "APPLIED"
    print(f"\n{'=' * 60}")
    print(f"doc_type Backfill Report ({mode_label})")
    print(f"{'=' * 60}")
    print(f"  Total .md files scanned    : {len(md_files)}")
    print(f"  Backfilled                 : {stats['backfilled']}")
    for dt, count in sorted(doctype_counts.items(), key=lambda x: -x[1]):
        print(f"    → {dt:<20} : {count}")
    print(f"  Skipped (already has doc_type): {stats['skip_has_doctype']}")
    print(f"  Skipped (no frontmatter)       : {stats['skip_no_fm']}")
    print(f"  Skipped (path ambiguous)       : {stats['skip_ambiguous']}")
    print(f"  Errors                         : {stats['error']}")
    print(f"{'=' * 60}")

    if dry_run:
        print("\nDry-run complete. Run without --dry-run to apply changes.")
    else:
        print("\nBackfill complete.")

    if stats["error"] > 0:
        return EXIT_FINDINGS
    return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
