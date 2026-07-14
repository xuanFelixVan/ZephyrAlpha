# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/checkers/check_dependency_direction.py | §
# [MODULE] scripts.governance.d5_architecture.checkers.check_dependency_direction
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d5_architecture.checkers.__init__
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
"""check_dependency_direction.py — 依赖方向校验（INJ-002/008）

对标：GOV-MOD-ALPHA_SIGNAL_DOMAIN INJ-002（依赖可解析）、INJ-008（依赖方向合法）

检测内容：
- --module: 检查指定模块的 depends_on 是否可解析（目标文件存在）
- --check-cross-layer: 检查跨层依赖方向是否符合 D_DATA→D_FACTOR→D_SIGNAL 单向数据流

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

__manifest__ = """
args:
- {flag: --module, type: str, description: "检查指定 module_id 的依赖可解析性"}
- {flag: --check-cross-layer, type: str, description: "检查指定 module_id 的跨层依赖方向"}
description: >
  依赖方向校验（INJ-002/008）——依赖可解析性 + 跨层依赖方向。
  对标 GOV-MOD-ALPHA_SIGNAL_DOMAIN module-injection-rules-policy.md。
dimensions:
- D5
priority: P1
timeout_seconds: 30
warn_only: false
"""

import argparse
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import EXIT_FINDINGS, EXIT_PASS, REPO_ROOT
from _shared.encoding import ensure_utf8_stdout
from _shared.frontmatter import parse_frontmatter_from_file

ensure_utf8_stdout()

POLICIES_ROOT = REPO_ROOT / "docs" / "01_policies_and_standards"
MODULES_ROOT = REPO_ROOT / "docs" / "03_modules"

LAYER_ORDER = {
    "data": 0,
    "infrastructure_runtime_integration": 1,
    "factor": 2,
    "signal": 3,
    "risk": 4,
    "pf_core": 5,
    "ex_core": 6,
    "pf_core": 7,
    "frontend": 8,
}

ALLOWED_CROSS_LAYER = {
    "cross_layer": -1,
    "L1": 100,
    "L2": 200,
    "L3": 300,
}


def find_module_file(module_id: str) -> Path | None:
    """find_module_file implementation."""
    for root in [POLICIES_ROOT, MODULES_ROOT]:
        for f in root.rglob("*"):
            if f.suffix not in (".md", ".yaml", ".yml"):
                continue
            fm = parse_frontmatter_from_file(f)
            if fm and fm.get("module_id") == module_id:
                return f
    return None


def resolve_module_id(ref: str) -> Path | None:
    """resolve_module_id implementation."""
    fpath = find_module_file(ref)
    if fpath:
        return fpath
    for root in [POLICIES_ROOT, MODULES_ROOT]:
        for f in root.rglob(f"{ref}.md"):
            return f
        for f in root.rglob(f"{ref}.yaml"):
            return f
    return None


def check_dependency_resolvable(module_id: str) -> list[str]:
    """Check compliance and report findings."""
    findings = []
    fpath = find_module_file(module_id)
    if not fpath:
        findings.append(f"INJ-002 FAIL: module '{module_id}' not found in project")
        return findings
    fm = parse_frontmatter_from_file(fpath)
    if not fm:
        return findings
    depends_on = fm.get("depends_on", [])
    if isinstance(depends_on, str):
        depends_on = [depends_on]
    for dep in depends_on:
        dep = dep.strip()
        if not dep:
            continue
        resolved = resolve_module_id(dep)
        if not resolved:
            findings.append(f"INJ-002 FAIL: module '{module_id}' depends_on '{dep}' — target not found in project")
    return findings


def check_cross_layer_direction(module_id: str) -> list[str]:
    """Check compliance and report findings."""
    findings = []
    fpath = find_module_file(module_id)
    if not fpath:
        findings.append(f"INJ-008 FAIL: module '{module_id}' not found in project")
        return findings
    fm = parse_frontmatter_from_file(fpath)
    if not fm:
        return findings
    source_layer = fm.get("layer", "")
    source_order = LAYER_ORDER.get(source_layer, ALLOWED_CROSS_LAYER.get(source_layer, 999))
    depends_on = fm.get("depends_on", [])
    if isinstance(depends_on, str):
        depends_on = [depends_on]
    for dep in depends_on:
        dep = dep.strip()
        if not dep:
            continue
        dep_path = resolve_module_id(dep)
        if not dep_path:
            continue
        dep_fm = parse_frontmatter_from_file(dep_path)
        if not dep_fm:
            continue
        dep_layer = dep_fm.get("layer", "")
        dep_order = LAYER_ORDER.get(dep_layer, ALLOWED_CROSS_LAYER.get(dep_layer, 999))
        if source_order < 999 and dep_order < 999 and source_order < dep_order:
            if dep_layer not in ("cross_layer", "L1", "L2", "L3"):
                findings.append(
                    f"INJ-008 FAIL: module '{module_id}' (layer={source_layer}) depends_on '{dep}' (layer={dep_layer}) — violates D_DATA→D_FACTOR→D_SIGNAL data flow direction"
                )
    return findings


def check_tech_radar(module_id: str = None) -> list[str]:
    """Check compliance and report findings."""
    import ast as ast_mod

    import yaml

    findings = []
    tech_landscape = (
        REPO_ROOT
        / "architecture_model"
        / "technology"
        / "technology_landscape.yaml"
    )
    if not tech_landscape.exists():
        return findings
    with open(tech_landscape, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    allowed_quadrants = {"adopt", "trial", "assess"}
    allowed_techs = set()
    for tech in data.get("technologies", []):
        quadrant = tech.get("quadrant", "").lower()
        if quadrant in allowed_quadrants:
            allowed_techs.add(tech.get("name", "").lower())
            for alias in tech.get("aliases", []):
                allowed_techs.add(alias.lower())
    src_root = REPO_ROOT / "src" / "zephyr"
    scan_dir = src_root
    if module_id:
        mf = find_module_file(module_id)
        if mf:
            scan_dir = mf.parent
    for py_file in scan_dir.rglob("*.py"):
        if py_file.name.startswith("_"):
            continue
        try:
            source = py_file.read_text(encoding="utf-8")
            tree = ast_mod.parse(source, filename=str(py_file))
        except (SyntaxError, UnicodeDecodeError):
            continue
        for node in ast_mod.walk(tree):
            if isinstance(node, ast_mod.Import):
                for alias in node.names:
                    pkg = alias.name.split(".")[0].lower()
                    if pkg in allowed_techs:
                        continue
            if isinstance(node, ast_mod.ImportFrom):
                if node.module:
                    pkg = node.module.split(".")[0].lower()
                    if pkg in allowed_techs:
                        continue
    return findings


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="Dependency direction validation (INJ-002/008)")
    parser.add_argument("--module", type=str, help="Check dependency resolvability for module_id")
    parser.add_argument("--check-cross-layer", type=str, help="Check cross-layer dependency direction for module_id")
    parser.add_argument("--check-tech-radar", action="store_true", help="Check imports against Tech Radar (HC-2)")
    parser.add_argument("--warn-only", action="store_true", help="Only warn, do not fail")
    args = parser.parse_args()

    all_findings: list[str] = []

    if args.module:
        all_findings.extend(check_dependency_resolvable(args.module))

    if args.check_cross_layer:
        all_findings.extend(check_cross_layer_direction(args.check_cross_layer))

    if args.check_tech_radar:
        all_findings.extend(check_tech_radar(args.module))

    if not any([args.module, args.check_cross_layer, args.check_tech_radar]):
        for f in POLICIES_ROOT.rglob("*.md"):
            fm = parse_frontmatter_from_file(f)
            if fm and fm.get("module_id"):
                mid = fm["module_id"]
                all_findings.extend(check_dependency_resolvable(mid))
                all_findings.extend(check_cross_layer_direction(mid))

    for finding in all_findings:
        print(finding)

    if all_findings and not args.warn_only:
        sys.exit(EXIT_FINDINGS)
    sys.exit(EXIT_PASS)


if __name__ == "__main__":
    main()
