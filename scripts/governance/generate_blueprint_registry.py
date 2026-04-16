# AI-generated: 从蓝图文件 frontmatter 自动提取并生成 Blueprint Registry YAML
"""
Blueprint Registry Generator

从所有蓝图文件的 YAML frontmatter 自动提取元数据，生成/更新中央 Blueprint Registry。

用法:
    python scripts/governance/generate_blueprint_registry.py
    python scripts/governance/generate_blueprint_registry.py --output docs/02_ARCHITECTURE/BLUEPRINT_DOMAIN_INVENTORY.yaml
    python scripts/governance/generate_blueprint_registry.py --dirs docs/01_FRAMEWORK docs/10_AI_WORKFLOW
    python scripts/governance/generate_blueprint_registry.py --stats   # 只输出统计摘要

输出:
    - docs/02_ARCHITECTURE/BLUEPRINT_DOMAIN_INVENTORY.yaml  (机器可读注册表)
    - docs/09_AUDIT/STATE/blueprint-registry-report-{DATE}.md  (可读摘要报告)
"""

import os
import sys
import json
import yaml
import re
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional


# ===== 配置 =====
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_BLUEPRINT_DIRS = [
    "docs/01_FRAMEWORK",
    "docs/10_AI_WORKFLOW",
    "docs/11_STRATEGIC_DECISION",
    "docs/08_HUMAN_AI_INTERFACE",
    "docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS",
]
OUTPUT_YAML = REPO_ROOT / "docs/02_ARCHITECTURE/BLUEPRINT_DOMAIN_INVENTORY.yaml"
OUTPUT_REPORT_DIR = REPO_ROOT / "docs/09_AUDIT/STATE"

VALID_STATUSES = {"Draft", "Review", "Active", "Superseded", "Deprecated", "Retired"}
VALID_LAYERS = {f"layer_{str(i).zfill(2)}" for i in range(12)} | {"cross_layer"}
VALID_PRIORITIES = {"P0", "P1", "P2"}

# 排除的目录（不扫描）
SKIP_DIRS = {
    "docs/06_ARCHIVE",
    "docs/09_ARCHIVE",
    "docs/99_ARCHIVE",
    ".git",
    "__pycache__",
    "scripts/ci_audit",
    ".audit_fix_backup",
}


def extract_frontmatter(filepath: Path) -> Optional[dict]:
    """从 Markdown 文件提取 YAML frontmatter。"""
    try:
        content = filepath.read_text(encoding="utf-8", errors="replace")
        if not content.startswith("---"):
            return None
        end_idx = content.find("---", 3)
        if end_idx == -1:
            return None
        yaml_str = content[3:end_idx].strip()
        return yaml.safe_load(yaml_str)
    except Exception:
        return None


def is_blueprint_file(filepath: Path, fm: dict) -> bool:
    """判断文件是否是蓝图文件。"""
    # 通过文件名判断
    name = filepath.name.lower()
    if "blueprint" in name or "technical-specification" in name:
        return True
    # 通过 frontmatter 判断
    if fm and fm.get("standard_type") in ("blueprint", "technical_spec"):
        return True
    if fm and fm.get("module_id"):
        return True
    return False


def normalize_layer(layer_val) -> str:
    """标准化 layer 字段值。"""
    if not layer_val:
        return "unknown"
    layer_str = str(layer_val).lower().strip()
    # 处理各种格式：layer_07、L07、07 等
    match = re.search(r"(\d{1,2})", layer_str)
    if match:
        num = int(match.group(1))
        return f"layer_{num:02d}"
    if "cross" in layer_str:
        return "cross_layer"
    return layer_str


def scan_blueprints(scan_dirs: list[str]) -> list[dict]:
    """扫描所有蓝图目录，提取元数据。"""
    blueprints = []
    seen_module_ids = {}

    for dir_rel in scan_dirs:
        dir_path = REPO_ROOT / dir_rel
        if not dir_path.exists():
            print(f"  [SKIP] 目录不存在: {dir_rel}", file=sys.stderr)
            continue

        for md_file in sorted(dir_path.rglob("*.md")):
            # 跳过 INDEX、README 等
            if md_file.stem.upper() in ("INDEX", "README", "SITEMAP"):
                continue
            # 跳过归档目录
            rel = md_file.relative_to(REPO_ROOT)
            if any(str(rel).startswith(skip) for skip in SKIP_DIRS):
                continue

            fm = extract_frontmatter(md_file)
            if not fm:
                continue
            if not is_blueprint_file(md_file, fm):
                continue

            module_id = fm.get("module_id", "")
            status = fm.get("status", "Unknown")

            # 跳过已归档状态
            if status in ("Retired", "Archived"):
                continue

            # 检测重复 module_id
            rel_path = str(rel).replace("\\", "/")
            if module_id and module_id in seen_module_ids:
                print(f"  [WARN] 重复 module_id '{module_id}':", file=sys.stderr)
                print(f"         已有: {seen_module_ids[module_id]}", file=sys.stderr)
                print(f"         新发现: {rel_path}", file=sys.stderr)

            layer_raw = fm.get("layer", "")
            layer = normalize_layer(layer_raw)

            record = {
                "module_id": module_id or f"UNNAMED_{md_file.stem}",
                "title": fm.get("title", md_file.stem.replace("-", " ").title()),
                "path": rel_path,
                "status": status,
                "layer": layer,
                "layer_raw": str(layer_raw),
                "priority": fm.get("priority", "MISSING"),
                "version": str(fm.get("version", "unknown")),
                "owner": fm.get("owner", "TBD"),
                "created_date": str(fm.get("created_date", "")),
                "last_updated": str(fm.get("last_updated", "")),
                "tags": fm.get("tags", []),
                "depends_on": fm.get("depends_on", []),
                "required_by": fm.get("required_by", []),
                "supersedes": fm.get("supersedes", ""),
                "superseded_by": fm.get("superseded_by", ""),
            }
            blueprints.append(record)

            if module_id:
                seen_module_ids[module_id] = rel_path

    return blueprints


def generate_stats(blueprints: list[dict]) -> dict:
    """生成统计摘要。"""
    total = len(blueprints)
    by_status = {}
    by_layer = {}
    by_priority = {}
    missing_priority = []
    layer_mislabeled = []

    for bp in blueprints:
        # 按状态统计
        status = bp["status"]
        by_status[status] = by_status.get(status, 0) + 1

        # 按层统计
        layer = bp["layer"]
        by_layer[layer] = by_layer.get(layer, 0) + 1

        # priority 覆盖率
        prio = bp["priority"]
        by_priority[prio] = by_priority.get(prio, 0) + 1
        if prio == "MISSING":
            missing_priority.append(bp["module_id"] or bp["path"])

        # 检测 layer 误标（layer_01 在 01_FRAMEWORK 以外）
        if layer == "layer_01" and "01_FRAMEWORK" not in bp["path"]:
            layer_mislabeled.append(bp["path"])
        # 检测路径在 01_FRAMEWORK 但 layer 不是 layer_01（可能正确，也可能是误标）

    priority_coverage = (total - len(missing_priority)) / total * 100 if total > 0 else 0

    return {
        "total": total,
        "by_status": dict(sorted(by_status.items())),
        "by_layer": dict(sorted(by_layer.items())),
        "by_priority": dict(sorted(by_priority.items())),
        "priority_coverage_pct": round(priority_coverage, 1),
        "missing_priority_count": len(missing_priority),
        "missing_priority_sample": missing_priority[:20],
        "layer_mislabeled_count": len(layer_mislabeled),
    }


def save_yaml_registry(blueprints: list[dict], output_path: Path, stats: dict) -> None:
    """保存机器可读的 YAML 注册表。"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    registry = {
        "schema_version": "1.0",
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "stats": stats,
        "blueprints": blueprints,
    }
    with open(output_path, "w", encoding="utf-8") as f:
        yaml.dump(registry, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    print(f"[OK] Registry saved: {output_path}")


def save_markdown_report(blueprints: list[dict], stats: dict, report_dir: Path) -> None:
    """生成可读的 Markdown 报告。"""
    date_str = datetime.now().strftime("%Y%m%d")
    report_path = report_dir / f"blueprint-registry-report-{date_str}.md"

    lines = [
        "---",
        f"generated_at: '{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}'",
        "doc_type: audit_report",
        "---",
        "",
        "# Blueprint Registry Report",
        "",
        "## 统计摘要",
        "",
        f"- **总蓝图数**: {stats['total']}",
        f"- **priority 覆盖率**: {stats['priority_coverage_pct']}%（缺失 {stats['missing_priority_count']} 个）",
        f"- **layer 疑似误标数**: {stats['layer_mislabeled_count']}",
        "",
        "### 按状态分布",
        "",
    ]
    for k, v in stats["by_status"].items():
        lines.append(f"- {k}: {v}")

    lines += ["", "### 按层分布", ""]
    for k, v in stats["by_layer"].items():
        lines.append(f"- {k}: {v}")

    lines += ["", "### 按优先级分布", ""]
    for k, v in stats["by_priority"].items():
        lines.append(f"- {k}: {v}")

    if stats["missing_priority_sample"]:
        lines += ["", "### 缺失 priority 字段的蓝图（前 20 个）", ""]
        for path in stats["missing_priority_sample"]:
            lines.append(f"- `{path}`")

    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"[OK] Report saved: {report_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Blueprint Registry from frontmatter")
    parser.add_argument("--output", default=str(OUTPUT_YAML), help="Output YAML path")
    parser.add_argument("--dirs", nargs="+", default=DEFAULT_BLUEPRINT_DIRS, help="Directories to scan")
    parser.add_argument("--stats", action="store_true", help="Only print stats, don't save files")
    args = parser.parse_args()

    print(f"Scanning blueprint directories...")
    blueprints = scan_blueprints(args.dirs)
    stats = generate_stats(blueprints)

    print(f"\n=== Blueprint Registry Stats ===")
    print(f"Total blueprints found: {stats['total']}")
    print(f"Priority coverage: {stats['priority_coverage_pct']}%")
    print(f"Missing priority: {stats['missing_priority_count']}")
    print(f"By status: {json.dumps(stats['by_status'], ensure_ascii=False)}")
    print(f"By layer (top 5): {dict(list(stats['by_layer'].items())[:5])}")

    if not args.stats:
        save_yaml_registry(blueprints, Path(args.output), stats)
        save_markdown_report(blueprints, stats, OUTPUT_REPORT_DIR)

    if stats["missing_priority_count"] > 0:
        print(f"\n[ACTION NEEDED] {stats['missing_priority_count']} blueprints missing 'priority' field.")
        print("Run: python scripts/governance/backfill_blueprint_priority.py to fix.")

    sys.exit(0)


if __name__ == "__main__":
    main()
