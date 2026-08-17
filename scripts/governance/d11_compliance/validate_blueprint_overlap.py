# [A_module] module_id=MOD-GOV_SCRIPTS | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
"""Module docstring — see module-level docstring for details."""
from __future__ import annotations

__manifest__ = """
args: []
description: 蓝图组件重叠检测器——检测多个蓝图草案中组件重叠。
dimensions:
- D11
priority: P2
timeout_seconds: 60
warn_only: false
"""

# [BLUEPRINT] MOD-GOV_SCRIPTS
# [MODULE] scripts.governance.d11_compliance.validate_blueprint_overlap
# [DOMAIN] D_GOV_DRIFT
# [DEPENDENCIES] scripts.governance._shared.frontmatter
# [CONSUMERS] N/A (all consumers verified as phantom — stale references removed)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""蓝图组件重叠检测器.

扫描 drafts 目录下的蓝图草案，提取每个草案的 components 列表，
检测被多个草案引用的组件（重叠）。
"""

from pathlib import Path

DRAFTS_ROOT = (
    Path(__file__).resolve().parent.parent.parent.parent
    / "docs"
    / "03_modules"
    / "_drafts"
)


def extract_components(blueprint_path):
    """从 frontmatter dict 或文件路径提取组件列表."""
    if blueprint_path is None:
        return []
    if isinstance(blueprint_path, dict):
        comps = blueprint_path.get("components")
        if comps is None:
            return []
        if isinstance(comps, list):
            return [str(c).strip() for c in comps if str(c).strip()]
        if isinstance(comps, str):
            return [c.strip() for c in comps.split(",") if c.strip()]
        return []
    from scripts.governance._shared.frontmatter import parse_frontmatter_from_file
    fm = parse_frontmatter_from_file(blueprint_path)
    return extract_components(fm)


def detect_overlaps(component_map=None, path=None):
    """检测组件重叠（出现在多个草案中的组件）."""
    if component_map is None:
        return []
    overlaps = []
    for component, drafts in component_map.items():
        if len(drafts) > 1:
            overlaps.append({
                "component_id": component,
                "draft_count": len(drafts),
                "drafts": drafts,
            })
    return overlaps


def scan_draft_components(path) -> dict:
    """扫描 drafts 目录，返回 {component: [draft_paths]} 映射."""
    from scripts.governance._shared.frontmatter import parse_frontmatter_from_file

    p = Path(path)
    if not p.exists():
        return {}
    result: dict[str, list] = {}
    for md_file in sorted(p.glob("*.md")):
        if md_file.name.upper() == "README.MD":
            continue
        fm = parse_frontmatter_from_file(md_file)
        if not fm:
            continue
        components = extract_components(fm)
        for comp in components:
            result.setdefault(comp, []).append(md_file)
    return result


def run_validation(path=None, verbose=False):
    """运行完整校验，返回 (overlaps, count)."""
    drafts_root = path if path is not None else DRAFTS_ROOT
    if not Path(drafts_root).exists():
        return [], 0
    component_map = scan_draft_components(drafts_root)
    overlaps = detect_overlaps(component_map)
    if verbose and overlaps:
        for o in overlaps:
            print(f"重叠组件: {o['component_id']} 出现在 {o['draft_count']} 个草案中")
    return overlaps, len(component_map)
