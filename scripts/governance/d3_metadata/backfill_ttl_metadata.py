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
"""批量回填/重判 frontmatter ttl 字段（GATE-15 存量治理 + GATE-VOCAB-CHANGE 纠偏）

对 docs/ 下所有有 frontmatter 的 .md 文件，按 ttl_vocabulary.yaml decision_tree
判定 ttl 值：
  - 默认模式：只回填缺 ttl 字段的文件
  - --rejudge 模式：重判已有 ttl 的文件（词表 decision_tree 变更后纠偏用）

判定口径（与 ttl_vocabulary.yaml decision_tree 完全一致，机器可读 criteria 消费）：
  - Q1: 过程性子目录（_working/changes/reports/09_audit/_archive）→ task_bound
  - Q2: 过程性 doc_type（log/audit_report/operational_rule）→ task_bound
  - Q3: 永久区路径 → permanent；否则 → task_bound

Usage::

    # dry-run（只报告，不写入）
    python scripts/governance/d3_metadata/backfill_ttl_metadata.py --dry-run

    # 全量回填（缺 ttl 的文件）
    python scripts/governance/d3_metadata/backfill_ttl_metadata.py

    # 重判模式（已有 ttl 的文件也重判，词表变更后纠偏）
    python scripts/governance/d3_metadata/backfill_ttl_metadata.py --rejudge

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

# ttl 行正则（匹配 frontmatter 内的 ttl: value 行，用于 rejudge 模式替换）
# 支持 ttl: permanent / ttl: "permanent" / ttl: 'permanent' 格式
_TTL_LINE_PATTERN = re.compile(r'^ttl:\s*["\']?[\w]+["\']?\s*$', re.MULTILINE)


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


def backfill_file(fpath: Path, dry_run: bool = False, rejudge: bool = False) -> str:
    """回填或重判单个文件的 ttl 字段。

    Args:
        fpath: .md 文件绝对路径。
        dry_run: True 则只报告不写入。
        rejudge: True 则重判已有 ttl 的文件（词表 decision_tree 变更后纠偏用）。

    Returns:
        "backfilled"（已回填缺 ttl）、"rejudged"（已重判 ttl）、
        "skip_has_ttl"（已有 ttl 且 rejudge=False）、
        "skip_unchanged"（rejudge=True 但 ttl 无变化）、
        "skip_no_fm"（无 frontmatter）、"error"（异常）。
    """
    try:
        text = fpath.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return "error"

    # 无 frontmatter 的文件跳过
    if not text.startswith("---"):
        return "skip_no_fm"

    metadata, _ = parse_frontmatter(text)
    if not metadata:
        return "skip_no_fm"

    rel_path = str(fpath.relative_to(REPO_ROOT)).replace("\\", "/")
    # 传 metadata 用于 Q2 doc_type 判定（修复原 bug：未传 frontmatter 导致 Q2 失效）
    new_ttl = _infer_ttl(rel_path, metadata)
    current_ttl = metadata.get("ttl")
    current_ttl_str = str(current_ttl).strip().strip('"\'') if current_ttl else ""

    if current_ttl_str:
        # 已有 ttl
        if not rejudge:
            return "skip_has_ttl"
        if current_ttl_str == new_ttl:
            return "skip_unchanged"
        # rejudge 模式：替换 frontmatter 内的 ttl 行（限制在 frontmatter 范围内）
        fm_end_match = _FM_END_PATTERN.search(text[3:])
        if not fm_end_match:
            return "skip_no_fm"
        fm_end = 3 + fm_end_match.start()
        fm_text = text[:fm_end]
        body = text[fm_end:]
        new_fm = _TTL_LINE_PATTERN.sub(f"ttl: {new_ttl}", fm_text, count=1)
        new_text = new_fm + body
        action = "rejudged"
    else:
        # 缺 ttl：注入 ttl 行（在 frontmatter 闭合 --- 前插入）
        fm_end_match = _FM_END_PATTERN.search(text[3:])
        if not fm_end_match:
            return "skip_no_fm"
        end_pos = 3 + fm_end_match.start()
        new_text = text[: end_pos + 1] + f"ttl: {new_ttl}\n" + text[end_pos + 1 :]
        action = "backfilled"

    if dry_run:
        return action

    # 原子写入（tmp + os.replace，RULE-ONE 并发安全）
    _atomic_write(fpath, new_text)
    return action


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
    rejudge = "--rejudge" in args
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
        "rejudged": 0,
        "skip_has_ttl": 0,
        "skip_unchanged": 0,
        "skip_no_fm": 0,
        "error": 0,
    }
    ttl_changes = {"permanent": 0, "task_bound": 0}

    changed_files: list[str] = []
    for fpath in md_files:
        result = backfill_file(fpath, dry_run=dry_run, rejudge=rejudge)
        stats[result] = stats.get(result, 0) + 1
        if result in ("backfilled", "rejudged"):
            rel_path = str(fpath.relative_to(REPO_ROOT)).replace("\\", "/")
            changed_files.append(rel_path)
            metadata, _ = parse_frontmatter(fpath.read_text(encoding="utf-8"))
            ttl_value = _infer_ttl(rel_path, metadata)
            ttl_changes[ttl_value] += 1

    # 输出统计报告
    mode_parts = []
    if dry_run:
        mode_parts.append("DRY-RUN")
    if rejudge:
        mode_parts.append("REJUDGE")
    mode_label = " + ".join(mode_parts) if mode_parts else "APPLIED"
    print(f"\n{'=' * 60}")
    print(f"ttl Backfill/Rejudge Report ({mode_label})")
    print(f"{'=' * 60}")
    print(f"  Total .md files scanned    : {len(md_files)}")
    print(f"  Backfilled (was missing)    : {stats['backfilled']}")
    print(f"  Rejudged (ttl changed)      : {stats['rejudged']}")
    print(f"    → permanent               : {ttl_changes['permanent']}")
    print(f"    → task_bound              : {ttl_changes['task_bound']}")
    print(f"  Skipped (has ttl, no rejudge): {stats['skip_has_ttl']}")
    print(f"  Skipped (unchanged)          : {stats['skip_unchanged']}")
    print(f"  Skipped (no frontmatter)     : {stats['skip_no_fm']}")
    print(f"  Errors                       : {stats['error']}")
    print(f"{'=' * 60}")

    if dry_run:
        print("\nDry-run complete. Run without --dry-run to apply changes.")
    else:
        print("\nBackfill/Rejudge complete. Run check_frontmatter_metadata.py to verify.")

    # 输出修改的文件列表（供 reconciler/手动纠偏提交用，每行一个相对路径）
    if changed_files:
        print(f"\n=== CHANGED FILES ({len(changed_files)}) ===")
        for f in changed_files:
            print(f)

    if stats["error"] > 0:
        return EXIT_FINDINGS
    return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
