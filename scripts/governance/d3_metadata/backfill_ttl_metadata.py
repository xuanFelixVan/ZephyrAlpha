# [BLUEPRINT] MOD-INF-005 | scripts/governance/d3_metadata/backfill_ttl_metadata.py | §gate-15
# [MODULE] governance.d3_metadata.backfill_ttl_metadata
# [DOMAIN] D-GOVERNANCE
# [DEPENDENCIES] zephyr.governance._shared.frontmatter; _shared.constants
# [CONSUMERS] manual batch backfill; stage-2 of ttl root-cause fix
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 按 ttl_vocabulary.yaml decision_tree 二元判定 ttl 值；只回填有 frontmatter 但无 ttl 的 .md；原子写入
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] EXIT_PASS=0（无错误）；EXIT_FINDINGS=1（有文件未能回填）；EXIT_ERROR=2（脚本异常）
# [TESTS] 手动测试：dry-run + 全量回填 + GATE-15 校验归零
"""批量回填 frontmatter ttl 字段（GATE-15 存量治理）

对 docs/ 下所有有 frontmatter 但缺 ttl 字段的 .md 文件，
按 ttl_vocabulary.yaml decision_tree 二元判定 ttl 值并注入。

判定口径（与 ttl_vocabulary.yaml decision_tree 完全一致）：
  - 路径在永久区 4 路径下 → permanent
  - 否则 → task_bound

永久区路径：
  - docs/01_policies_and_standards/
  - docs/02_enterprise_architecture/
  - docs/03_modules/
  - docs/08_knowledge/

Usage::

    # dry-run（只报告，不写入）
    python scripts/governance/d3_metadata/backfill_ttl_metadata.py --dry-run

    # 全量回填
    python scripts/governance/d3_metadata/backfill_ttl_metadata.py

    # 限定子目录
    python scripts/governance/d3_metadata/backfill_ttl_metadata.py docs/08_knowledge/01_raw_intake/
"""

from __future__ import annotations

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
from _shared.frontmatter import parse_frontmatter  # noqa: E402
from _shared.yaml_utils import evaluate_ttl, load_decision_tree  # noqa: E402

# ttl 判定树——从 ttl_vocabulary.yaml 动态加载（SSoT 唯一真源，禁止硬编码路径前缀）
# 约束：判定逻辑变更只需改 ttl_vocabulary.yaml decision_tree，本脚本自动同步
_DECISION_TREE = load_decision_tree("ttl_vocabulary.yaml")

# frontmatter 结束符正则（与 _shared/frontmatter.py _FM_END_PATTERN 一致）
_FM_END_PATTERN = re.compile(r"\n---[ \t]*\n?")


def _infer_ttl(rel_path: str, frontmatter: dict | None = None) -> str:
    """按 ttl_vocabulary.yaml decision_tree 判定 ttl 值（机器可读 criteria 消费）。

    向内收：判定逻辑唯一真源为 ttl_vocabulary.yaml decision_tree，本函数零硬编码。
    替换原 _PERMANENT_ZONE_PREFIXES 硬编码路径前缀（治本：changes/等过程文件不再误判 permanent）。

    Args:
        rel_path: 相对 REPO_ROOT 的路径（正斜杠）。
        frontmatter: 文件 frontmatter dict（可选，用于 Q2 doc_type 判定）。

    Returns:
        "permanent" 或 "task_bound"。
    """
    return evaluate_ttl(rel_path, frontmatter, _DECISION_TREE)


def backfill_file(fpath: Path, dry_run: bool = False) -> str:
    """回填单个文件的 ttl 字段。

    Args:
        fpath: .md 文件绝对路径。
        dry_run: True 则只报告不写入。

    Returns:
        "backfilled"（已回填）、"skip_has_ttl"（已有 ttl）、
        "skip_no_fm"（无 frontmatter）、"error"（异常）。
    """
    try:
        text = fpath.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return "error"

    # 无 frontmatter 的文件跳过
    if not text.startswith("---"):
        return "skip_no_fm"

    # 检查是否已有 ttl
    metadata, _ = parse_frontmatter(text)
    if not metadata:
        return "skip_no_fm"
    if metadata.get("ttl"):
        return "skip_has_ttl"

    # 定位 frontmatter 结束符
    fm_end_match = _FM_END_PATTERN.search(text[3:])
    if not fm_end_match:
        # frontmatter 未闭合，跳过（不修复格式问题）
        return "skip_no_fm"

    # 计算插入位置：在闭合 --- 前插入 ttl 行
    # end_pos 指向 \n（最后一个字段行的换行符），end_pos+1 是 --- 的起始位置
    # 在 end_pos+1 处插入 "ttl: <value>\n"，使其成为独立的一行
    end_pos = 3 + fm_end_match.start()
    rel_path = str(fpath.relative_to(REPO_ROOT)).replace("\\", "/")
    ttl_value = _infer_ttl(rel_path)

    # 在最后一个字段行的 \n 之后、--- 之前插入 ttl 行
    new_text = text[: end_pos + 1] + f"ttl: {ttl_value}\n" + text[end_pos + 1 :]

    if dry_run:
        return "backfilled"

    # 原子写入（tmp + os.replace，RULE-ONE 并发安全）
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
        # 清理 tmp 文件
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
        # 限定子目录
        scan_dirs = [(REPO_ROOT / p).resolve() for p in path_args]
    else:
        # 全量扫描 docs/
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
        "skip_has_ttl": 0,
        "skip_no_fm": 0,
        "error": 0,
    }
    ttl_counts = {"permanent": 0, "task_bound": 0}

    for fpath in md_files:
        result = backfill_file(fpath, dry_run=dry_run)
        stats[result] += 1
        if result == "backfilled":
            rel_path = str(fpath.relative_to(REPO_ROOT)).replace("\\", "/")
            ttl_value = _infer_ttl(rel_path)
            ttl_counts[ttl_value] += 1

    # 输出统计报告
    mode_label = "DRY-RUN" if dry_run else "APPLIED"
    print(f"\n{'=' * 60}")
    print(f"ttl Backfill Report ({mode_label})")
    print(f"{'=' * 60}")
    print(f"  Total .md files scanned : {len(md_files)}")
    print(f"  Backfilled              : {stats['backfilled']}")
    print(f"    → permanent           : {ttl_counts['permanent']}")
    print(f"    → task_bound          : {ttl_counts['task_bound']}")
    print(f"  Skipped (already has ttl): {stats['skip_has_ttl']}")
    print(f"  Skipped (no frontmatter) : {stats['skip_no_fm']}")
    print(f"  Errors                   : {stats['error']}")
    print(f"{'=' * 60}")

    if dry_run:
        print("\nDry-run complete. Run without --dry-run to apply changes.")
    else:
        print("\nBackfill complete. Run check_frontmatter_metadata.py to verify.")

    if stats["error"] > 0:
        return EXIT_FINDINGS
    return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
