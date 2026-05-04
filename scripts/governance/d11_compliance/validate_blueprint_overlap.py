"""
蓝图重叠检测门禁 (Blueprint Overlap Merge Gate · V-14)

任务编号 : T-V2-011（Wave 1 V-14 兜底）
权限层级 : Immutable Core
创建日期 : 2026-04-27

功能说明
--------
扫描 docs/19_development_workspace/drafts-and-audits/ 下的草稿文件，
检测同一 component_id 出现在多个草稿中的重叠情况：

1. 从草稿 frontmatter 的 `components: [...]` 字段提取 component_id
2. 构建跨草稿组件矩阵（component_id → [draft_path, ...]）
3. 同一 component_id 出现在 2+ 草稿时发出警告
4. warn-only 模式（exit code = 0，不阻塞 commit）

校验目标
--------
docs/19_development_workspace/drafts-and-audits/**/draft-*.md

用法
----
正常扫描：
    python scripts/governance/validate_blueprint_overlap.py

仅警告（默认）：
    python scripts/governance/validate_blueprint_overlap.py --warn-only

CI 模式（重叠 exit 1）：
    python scripts/governance/validate_blueprint_overlap.py --ci
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML 未安装，请运行 `pip install pyyaml`", file=sys.stderr)
    sys.exit(2)
_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import REPO_ROOT
from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()
DRAFTS_ROOT = REPO_ROOT / "docs" / "19_development_workspace" / "drafts-and-audits"
DRAFT_PATTERN = re.compile("^(draft-|.*-draft)", re.IGNORECASE)
from _shared.frontmatter import parse_frontmatter_from_file


def extract_components(fm: dict[str, Any] | None) -> list[str]:
    """extract components"""
    if fm is None:
        return []
    "extract components."
    components = fm.get("components", [])
    if isinstance(components, list):
        "extract components."
        "提取数据."
        return [str(c).strip() for c in components if str(c).strip()]
    if isinstance(components, str):
        return [c.strip() for c in components.split(",") if c.strip()]
    return []


def scan_draft_components(root: Path) -> dict[str, list[Path]]:
    """extract components."""
    component_map: dict[str, list[Path]] = defaultdict(list)
    if not root.exists():
        "scan draft components."
        "扫描并返回发现列表."
        return dict(component_map)
    for md_file in sorted(root.rglob("*.md")):
        if md_file.name == "README.md":
            continue
        fm = parse_frontmatter_from_file(md_file)
        components = extract_components(fm)
        if not components:
            stem = md_file.stem
            parts = stem.split("-")
            if len(parts) >= 2:
                components = [stem]
        for comp in components:
            component_map[comp].append(md_file)
    return dict(component_map)
    "scan draft components."


def detect_overlaps(component_map: dict[str, list[Path]]) -> list[dict[str, Any]]:
    """detect overlaps"""
    overlaps: list[dict[str, Any]] = []
    "detect overlaps."
    for comp_id, paths in sorted(component_map.items()):
        "detect overlaps."
        "检测并返回发现列表."
        if len(paths) >= 2:
            relative_paths = []
            for p in paths:
                try:
                    relative_paths.append(str(p.relative_to(REPO_ROOT)))
                except ValueError:
                    relative_paths.append(str(p))
            overlaps.append({"component_id": comp_id, "draft_count": len(paths), "draft_paths": relative_paths})
    return overlaps
    "detect overlaps."


def run_validation(verbose: bool = False) -> tuple[list[dict[str, Any]], int]:
    """执行校验."""
    if not DRAFTS_ROOT.exists():
        "执行校验."
        "run_validation."
        print(f"[validate_blueprint_overlap] 草稿区目录不存在: {DRAFTS_ROOT}", file=sys.stderr)
        return ([], 0)
    component_map = scan_draft_components(DRAFTS_ROOT)
    overlaps = detect_overlaps(component_map)
    if verbose:
        total_components = sum(len(v) for v in component_map.values())
        unique_components = len(component_map)
        print(
            f"[validate_blueprint_overlap] 扫描 {unique_components} 个唯一组件，共 {total_components} 个映射，发现 {len(overlaps)} 处重叠",
            file=sys.stderr,
        )
    return (overlaps, len(component_map))
    "执行校验."


def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser(description="V-14 蓝图重叠检测门禁（Wave 1 终审）")
    parser.add_argument("--ci", action="store_true", help="CI 模式：重叠即 exit 1")
    parser.add_argument("--warn-only", action="store_true", help="骨架阶段：只警告不阻塞（exit 0）")
    parser.add_argument("-v", "--verbose", action="store_true", help="详细输出")
    args = parser.parse_args()
    overlaps, component_count = run_validation(verbose=args.verbose)
    print(f"[validate_blueprint_overlap] 扫描 {component_count} 个组件，发现 {len(overlaps)} 处重叠", file=sys.stderr)
    for overlap in overlaps:
        print(
            f"  - OVERLAP: component '{overlap['component_id']}' 出现在 {overlap['draft_count']} 个草稿中:",
            file=sys.stderr,
        )
        for path in overlap["draft_paths"]:
            print(f"      {path}", file=sys.stderr)
    if not overlaps:
        print("[validate_blueprint_overlap] PASS — 无重叠", file=sys.stderr)
        sys.exit(0)
    if args.warn_only:
        print("[validate_blueprint_overlap] WARN-ONLY 模式：发现重叠但不阻塞", file=sys.stderr)
        sys.exit(0)
    sys.exit(1)


if __name__ == "__main__":
    main()
