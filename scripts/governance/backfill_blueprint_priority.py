# AI-generated: 批量补全蓝图文件中缺失的 priority 字段
"""
Blueprint Priority Backfill Tool

扫描所有活跃蓝图，识别缺失 priority 字段的文件，
根据内容关键词自动推断 P0/P1/P2，并写入 frontmatter。

用法:
    python scripts/governance/backfill_blueprint_priority.py --dry-run   # 只扫描，不修改
    python scripts/governance/backfill_blueprint_priority.py --apply     # 应用修改
    python scripts/governance/backfill_blueprint_priority.py --apply --confirm-each  # 逐个确认

警告:
    --apply 模式会修改文件。建议先用 --dry-run 检查结果，
    commit 当前状态后再执行 --apply。
"""

import os
import sys
import re
import argparse
from pathlib import Path
from typing import Optional


REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# 扫描目录（只处理活跃蓝图目录）
BLUEPRINT_DIRS = [
    "docs/01_FRAMEWORK",
    "docs/10_AI_WORKFLOW",
    "docs/11_STRATEGIC_DECISION",
    "docs/08_HUMAN_AI_INTERFACE",
    "docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS",
]

# 排除归档目录
SKIP_PATH_PATTERNS = [
    "06_ARCHIVE", "09_ARCHIVE", "99_ARCHIVE", ".audit_fix_backup",
]

# P0 关键词（核心交易链路）
P0_KEYWORDS = [
    "order", "risk", "data_source", "execution", "ohlcv", "trade",
    "portfolio", "position", "circuit_breaker", "stop_loss",
    "data-source", "risk-control", "order-management",
    "data-layer", "base-error", "configuration-management",
]

# P1 关键词（专业机构标配）
P1_KEYWORDS = [
    "factor", "backtest", "signal", "performance", "strategy",
    "feature", "model", "sentiment", "alpha", "attribution",
    "monitoring", "reporting", "alert", "scheduler",
]

# P2 关键词（机构级或未来）
P2_KEYWORDS = [
    "reinforcement", "mifid", "compliance", "dark_pool",
    "active_learning", "sor", "smart_order_routing",
    "institutional", "regulation",
]


def infer_priority(filepath: Path, content: str) -> str:
    """根据文件名和内容推断优先级。"""
    name_lower = filepath.stem.lower()
    content_lower = content[:3000].lower()  # 只看前 3000 字

    for kw in P0_KEYWORDS:
        if kw.replace("_", "-") in name_lower or kw in content_lower:
            return "P0"

    for kw in P2_KEYWORDS:
        if kw.replace("_", "-") in name_lower or kw in content_lower:
            return "P2"

    for kw in P1_KEYWORDS:
        if kw.replace("_", "-") in name_lower or kw in content_lower:
            return "P1"

    return "P1"  # 默认 P1


def extract_and_check_frontmatter(filepath: Path) -> tuple[bool, str, dict]:
    """读取文件，返回 (has_priority, content, frontmatter_dict)。"""
    try:
        content = filepath.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return False, "", {}

    if not content.startswith("---"):
        return False, content, {}

    end_idx = content.find("---", 3)
    if end_idx == -1:
        return False, content, {}

    yaml_str = content[3:end_idx]

    # 简单解析 frontmatter（不依赖 yaml 库避免导入问题）
    fm = {}
    for line in yaml_str.split("\n"):
        if ":" in line:
            k, _, v = line.partition(":")
            fm[k.strip()] = v.strip()

    has_priority = "priority" in fm
    return has_priority, content, fm


def add_priority_to_frontmatter(content: str, priority: str) -> str:
    """在 frontmatter 中插入 priority 字段（在 status 字段后）。"""
    # 找到 frontmatter 结束位置
    if not content.startswith("---"):
        return content

    end_idx = content.find("---", 3)
    if end_idx == -1:
        return content

    yaml_part = content[3:end_idx]
    rest = content[end_idx:]

    # 如果已有 priority，跳过
    if "priority:" in yaml_part:
        return content

    # 在 status 行后插入
    lines = yaml_part.split("\n")
    new_lines = []
    inserted = False
    for line in lines:
        new_lines.append(line)
        if line.strip().startswith("status:") and not inserted:
            new_lines.append(f"priority: {priority}")
            inserted = True

    if not inserted:
        # 如果没有 status 行，在末尾插入
        new_lines.append(f"priority: {priority}")

    new_yaml = "\n".join(new_lines)
    return "---" + new_yaml + rest


def process_blueprints(dirs: list[str], apply: bool, confirm_each: bool) -> None:
    """主处理函数。"""
    total = 0
    missing = 0
    fixed = 0
    skipped = 0

    results = []

    for dir_rel in dirs:
        dir_path = REPO_ROOT / dir_rel
        if not dir_path.exists():
            print(f"[SKIP] 目录不存在: {dir_rel}")
            continue

        for md_file in sorted(dir_path.rglob("*.md")):
            if md_file.stem.upper() in ("INDEX", "README", "SITEMAP"):
                continue

            rel = str(md_file.relative_to(REPO_ROOT)).replace("\\", "/")
            if any(skip in rel for skip in SKIP_PATH_PATTERNS):
                continue

            has_priority, content, fm = extract_and_check_frontmatter(md_file)
            if not content or not fm:
                continue

            status = fm.get("status", "")
            if status in ("Retired", "Archived", ""):
                continue

            total += 1

            if has_priority:
                continue

            missing += 1
            inferred = infer_priority(md_file, content)
            results.append((md_file, rel, inferred, content))

    print(f"\n=== Blueprint Priority Backfill ===")
    print(f"Total scanned: {total}")
    print(f"Missing priority: {missing}")
    print(f"Mode: {'APPLY' if apply else 'DRY-RUN'}")
    print()

    for md_file, rel, priority, content in results:
        print(f"  [{priority}] {rel}")
        if apply:
            if confirm_each:
                answer = input(f"    Apply {priority} to {md_file.name}? [y/N/q] ").strip().lower()
                if answer == "q":
                    print("Aborted.")
                    break
                if answer != "y":
                    skipped += 1
                    continue

            new_content = add_priority_to_frontmatter(content, priority)
            if new_content != content:
                md_file.write_text(new_content, encoding="utf-8")
                fixed += 1

    print(f"\nResults:")
    print(f"  Fixed: {fixed}")
    print(f"  Skipped: {skipped}")
    print(f"  Remaining: {missing - fixed - skipped}")

    if not apply:
        print(f"\n[DRY-RUN] No files were modified.")
        print(f"Run with --apply to apply changes.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Backfill 'priority' field in blueprint frontmatters")
    parser.add_argument("--dry-run", action="store_true", help="Only scan, do not modify (default when --apply not set)")
    parser.add_argument("--apply", action="store_true", help="Apply changes to files")
    parser.add_argument("--confirm-each", action="store_true", help="Confirm each file before modifying")
    parser.add_argument("--dirs", nargs="+", default=BLUEPRINT_DIRS, help="Directories to scan")
    args = parser.parse_args()

    apply = args.apply  # --apply 显式指定时才执行写入
    process_blueprints(args.dirs, apply, args.confirm_each)


if __name__ == "__main__":
    main()
