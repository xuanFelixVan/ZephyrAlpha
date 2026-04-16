# AI-generated: 检测 docs/ 下的重复/平行子系统，防止新重复系统静默产生
"""
Subsystem Duplicate Detector

扫描 docs/ 下的所有一级子目录，对比 docs/subsystem-registry.yaml 中的登记状态，
检测：
  1. 磁盘上存在但未在注册表中登记的目录（"幽灵子系统"）
  2. 注册表中标记为 deprecated 但磁盘上仍存在的目录（"残留子系统"）
  3. 新增目录的功能是否与现有 canonical 目录重叠（简单关键词分析）

用法:
    python scripts/governance/scan_subsystem_duplicates.py
    python scripts/governance/scan_subsystem_duplicates.py --verbose
    python scripts/governance/scan_subsystem_duplicates.py --fail-on-ghost  # CI 模式，幽灵目录退出码 1

输出:
    - 控制台报告
    - docs/09_AUDIT/STATE/subsystem-health-{DATE}.md
"""

import os
import sys
import yaml
import argparse
from pathlib import Path
from datetime import datetime


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
REGISTRY_PATH = REPO_ROOT / "docs/subsystem-registry.yaml"
REPORT_DIR = REPO_ROOT / "docs/09_AUDIT/STATE"

# 功能域关键词（用于重叠检测）
DOMAIN_KEYWORDS = {
    "knowledge": ["knowledge", "知识", "factor_lib", "strategy_lib", "best_practice"],
    "archive": ["archive", "archived", "backup", "deprecated", "归档"],
    "audit": ["audit", "审计", "state", "report"],
    "governance": ["governance", "compliance", "治理", "合规"],
    "blueprint": ["blueprint", "蓝图", "framework", "design"],
    "research": ["research", "innovation", "研究", "创新"],
    "construction": ["construction", "implementation", "plan", "施工"],
}


def load_registry(registry_path: Path) -> dict:
    """加载子系统注册表。"""
    if not registry_path.exists():
        print(f"[WARN] Registry not found: {registry_path}", file=sys.stderr)
        return {}
    with open(registry_path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def get_registered_paths(registry: dict) -> tuple[set[str], set[str], set[str]]:
    """从注册表提取 canonical、deprecated、planned 路径集合。"""
    canonical = set()
    deprecated = set()
    planned = set()

    for ss in registry.get("subsystems", []):
        path = ss.get("canonical_path", "").rstrip("/")
        status = ss.get("status", "")
        is_canonical = ss.get("canonical", False)

        if path:
            if status == "active" and is_canonical:
                canonical.add(path)
            elif status in ("deprecated", "planned"):
                if status == "deprecated":
                    deprecated.add(path)
                else:
                    planned.add(path)

        # 也收集 duplicates 中的路径
        for dup in ss.get("duplicates", []):
            dup_path = dup.get("path", "").rstrip("/")
            if dup_path:
                deprecated.add(dup_path)

    return canonical, deprecated, planned


def scan_disk_dirs(docs_dir: Path) -> list[tuple[str, int]]:
    """扫描 docs/ 下的一级子目录，返回 (相对路径, 文件数) 列表。"""
    results = []
    if not docs_dir.exists():
        return results

    for item in sorted(docs_dir.iterdir()):
        if item.is_dir():
            rel = str(item.relative_to(REPO_ROOT)).replace("\\", "/")
            file_count = sum(1 for _ in item.rglob("*") if _.is_file())
            results.append((rel, file_count))

    return results


def detect_domain_overlap(dir_name: str) -> list[str]:
    """检测目录名所属的功能域。"""
    name_lower = dir_name.lower()
    domains = []
    for domain, keywords in DOMAIN_KEYWORDS.items():
        if any(kw in name_lower for kw in keywords):
            domains.append(domain)
    return domains


def generate_report(
    disk_dirs: list[tuple[str, int]],
    canonical: set[str],
    deprecated: set[str],
    planned: set[str],
    verbose: bool,
) -> tuple[list[str], int, int]:
    """生成分析报告，返回 (report_lines, ghost_count, residual_count)。"""
    ghost_dirs = []       # 磁盘有但注册表中无
    residual_dirs = []    # 注册表标记 deprecated 但磁盘仍有
    ok_dirs = []          # 正常

    all_registered = canonical | deprecated | planned

    for rel, count in disk_dirs:
        if rel in canonical:
            ok_dirs.append((rel, count, "canonical"))
        elif rel in deprecated:
            residual_dirs.append((rel, count))
        elif rel in planned:
            ok_dirs.append((rel, count, "planned"))
        else:
            ghost_dirs.append((rel, count))

    lines = [
        f"# Subsystem Health Report - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "## 摘要",
        "",
        f"- 磁盘子目录总数: {len(disk_dirs)}",
        f"- Canonical（已登记活跃）: {len([d for d in ok_dirs if d[2] == 'canonical'])}",
        f"- Planned（规划中）: {len([d for d in ok_dirs if d[2] == 'planned'])}",
        f"- 幽灵子系统（未登记）: {len(ghost_dirs)}",
        f"- 残留子系统（应已清理）: {len(residual_dirs)}",
        "",
    ]

    if ghost_dirs:
        lines += ["## 幽灵子系统（需立即在 subsystem-registry.yaml 中登记或清理）", ""]
        for rel, count in ghost_dirs:
            domains = detect_domain_overlap(rel)
            domain_hint = f"  ← 功能域重叠: {domains}" if domains else ""
            lines.append(f"- `{rel}` ({count} 文件){domain_hint}")
        lines.append("")

    if residual_dirs:
        lines += ["## 残留子系统（已标记 deprecated，但磁盘上仍存在）", ""]
        for rel, count in residual_dirs:
            lines.append(f"- `{rel}` ({count} 文件) — 执行 Phase D 合并/清理")
        lines.append("")

    if verbose:
        lines += ["## 所有已登记 Canonical 子系统", ""]
        for rel, count, status in sorted(ok_dirs):
            lines.append(f"- `{rel}` ({count} 文件) [{status}]")
        lines.append("")

    lines += [
        "## 建议行动",
        "",
        "1. 每个**幽灵子系统**：在 `docs/subsystem-registry.yaml` 中登记（canonical 或 deprecated）",
        "2. 每个**残留子系统**：按 `docs/09_AUDIT/STATE/subsystem-dedup-decisions-20260416.md` 执行合并",
        "3. 新建目录**前**：先查阅注册表确认无功能重叠",
    ]

    return lines, len(ghost_dirs), len(residual_dirs)


def main() -> None:
    parser = argparse.ArgumentParser(description="Detect duplicate/unregistered subsystems")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show all directories")
    parser.add_argument("--fail-on-ghost", action="store_true", help="Exit code 1 if ghost dirs found (CI mode)")
    args = parser.parse_args()

    docs_dir = REPO_ROOT / "docs"

    print(f"Loading registry from: {REGISTRY_PATH}")
    registry = load_registry(REGISTRY_PATH)
    canonical, deprecated, planned = get_registered_paths(registry)
    print(f"Registry: {len(canonical)} canonical, {len(deprecated)} deprecated, {len(planned)} planned")

    print(f"Scanning: {docs_dir}")
    disk_dirs = scan_disk_dirs(docs_dir)
    print(f"Found {len(disk_dirs)} directories on disk")

    report_lines, ghost_count, residual_count = generate_report(
        disk_dirs, canonical, deprecated, planned, args.verbose
    )

    # 打印到控制台
    print()
    for line in report_lines:
        print(line)

    # 保存报告
    date_str = datetime.now().strftime("%Y%m%d")
    report_path = REPORT_DIR / f"subsystem-health-{date_str}.md"
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
    print(f"\n[OK] Report saved: {report_path}")

    # CI 模式退出码
    if args.fail_on_ghost and ghost_count > 0:
        print(f"\n[FAIL] {ghost_count} ghost subsystems found. Please register them.", file=sys.stderr)
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
