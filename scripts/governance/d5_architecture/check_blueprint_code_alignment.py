# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/check_blueprint_code_alignment.py | §
# [MODULE] scripts.governance.d5_architecture.check_blueprint_code_alignment
# [DOMAIN] D-GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
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
"""
[BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain-autonomy_perm/budget-enforcer/blueprint.md | S10.2
[MODULE] scripts.governance.d5_architecture.check_blueprint_code_alignment
[INVARIANTS] blueprint-code alignment check cannot be skipped; drift must be reported
[MODIFY-GUARD] docs/03_modules/infrastructure_runtime_integration/budget-enforcer/blueprint.md
[CONSUMERS] CI pipeline; gct_024 gate; CircadianScheduler
[STABILITY] evolving
[SAFETY] L
[AI_AUTONOMY] ai_modifiable
[ERROR_CONTRACT] exit 0=ALIGNED; exit 1=DRIFT_DETECTED; exit 2=CRITICAL
[TESTS] tests/governance/test_check_blueprint_code_alignment.py
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
BLUEPRINT_PATH = (
    REPO_ROOT / "docs" / "03_modules" / "infrastructure_runtime_integration" / "budget-enforcer" / "blueprint.md"
)
CODE_DIR = REPO_ROOT / "src" / "zephyr" / "budget-enforcer"


def parse_frontmatter(content: str) -> dict:
    if not content.startswith("---"):
        return {}
    end = content.find("---", 3)
    if end < 0:
        return {}
    fm_text = content[3:end].strip()
    result: dict = {}
    current_key = None
    current_list: list = []
    in_list = False
    for line in fm_text.split("\n"):
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("- ") and in_list and current_key:
            current_list.append(stripped[2:].strip())
            continue
        if in_list and current_key:
            result[current_key] = current_list
            in_list = False
        if ":" in stripped and not stripped.startswith("-"):
            key, _, val = stripped.partition(":")
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            if val:
                result[key] = val
            else:
                current_key = key
                current_list = []
                in_list = True
    if in_list and current_key:
        result[current_key] = current_list
    return result


def extract_table_after(content: str, marker: str, col_count: int = 0) -> list[dict]:
    lines = content.split("\n")
    start_idx = None
    for i, line in enumerate(lines):
        if marker in line:
            start_idx = i
            break
    if start_idx is None:
        return []
    header_idx = None
    for i in range(start_idx, min(start_idx + 30, len(lines))):
        if "|" in lines[i] and "---" not in lines[i]:
            header_idx = i
            break
    if header_idx is None:
        return []
    sep_idx = header_idx + 1
    if sep_idx >= len(lines) or not lines[sep_idx].strip().startswith("|"):
        return []
    cols = [c.strip() for c in lines[header_idx].split("|") if c.strip()]
    rows: list[dict] = []
    for i in range(sep_idx + 1, min(sep_idx + 100, len(lines))):
        line = lines[i].strip()
        if not line.startswith("|"):
            break
        cells = [c.strip() for c in line.split("|") if c.strip()]
        if len(cells) >= len(cols):
            row = {}
            for j, col in enumerate(cols):
                row[col] = cells[j]
            rows.append(row)
    return rows


def check_file_list_alignment(content: str) -> dict:
    rows = extract_table_after(content, "\u00a70.1")
    if not rows:
        return {"check": "file_list_alignment", "status": "CRITICAL", "detail": "\u00a70.1 table not found"}
    listed_files: set[str] = set()
    for row in rows:
        for key in row:
            val = row[key].strip("`")
            if val.endswith(".py") and len(val) < 50:
                listed_files.add(val)
                break
    actual_files: set[str] = set()
    if CODE_DIR.exists():
        for f in CODE_DIR.iterdir():
            if f.suffix == ".py":
                actual_files.add(f.name)
    missing_on_disk = listed_files - actual_files
    missing_in_blueprint = actual_files - listed_files
    if not missing_on_disk and not missing_in_blueprint:
        return {"check": "file_list_alignment", "status": "PASS", "detail": f"{len(listed_files)} files aligned"}
    details = []
    if missing_on_disk:
        details.append(f"listed but missing on disk: {sorted(missing_on_disk)}")
    if missing_in_blueprint:
        details.append(f"on disk but missing in blueprint: {sorted(missing_in_blueprint)}")
    return {"check": "file_list_alignment", "status": "DRIFT", "detail": "; ".join(details)}


def check_api_signature_alignment(content: str) -> dict:
    drifts: list[str] = []
    if "PreFlightResult" in content:
        drifts.append("S4 still references PreFlightResult (should be GateResult)")
    if "PreFlightVerdict" in content:
        drifts.append("S4 still references PreFlightVerdict (should be GateDecision)")
    try:
        from zephyr.governance.budget_enforcement.budget_models import GateDecision, GateResult
    except ImportError:
        drifts.append("GateResult/GateDecision not importable from code")
    if not drifts:
        return {"check": "api_signature_alignment", "status": "PASS", "detail": "GateResult/GateDecision aligned"}
    return {"check": "api_signature_alignment", "status": "DRIFT", "detail": "; ".join(drifts)}


def check_dependency_registry_alignment(content: str) -> dict:
    declared_deps: set[str] = set()
    for match in re.finditer(r"target:\s*MOD-INF-(\d+)", content):
        pass
    dep_section_match = re.search(r"10\.1\s+依赖声明\s*\n(.*?)(?=\n###|\n---|\n## )", content, re.DOTALL)
    if dep_section_match:
        for match in re.finditer(r"(MOD-INF-\d+)", dep_section_match.group(1)):
            declared_deps.add(match.group(1))
    if not declared_deps:
        return {"check": "dependency_registry_alignment", "status": "WARN", "detail": "S10.1 no deps found"}
    registry_path = (
        REPO_ROOT
        / "docs"
        / "01_policies_and_standards"
        / "_registry"
        / "catalogs"
        / "cross-module-dependency-registry.yaml"
    )
    if not registry_path.exists():
        return {"check": "dependency_registry_alignment", "status": "WARN", "detail": "registry file not found"}
    registry_text = registry_path.read_text(encoding="utf-8")
    registered_targets: set[str] = set()
    block_starts = [m.start() for m in re.finditer(r"source:\s*MOD-INF-024", registry_text)]
    for start in block_starts:
        block = registry_text[start : start + 500]
        target_match = re.search(r"target:\s*(MOD-INF-\d+)", block)
        if target_match:
            registered_targets.add(target_match.group(1))
    missing_in_registry = declared_deps - registered_targets
    if not missing_in_registry:
        return {
            "check": "dependency_registry_alignment",
            "status": "PASS",
            "detail": f"{len(declared_deps)} deps all registered",
        }
    return {
        "check": "dependency_registry_alignment",
        "status": "DRIFT",
        "detail": f"missing in registry: {sorted(missing_in_registry)}",
    }


def check_version_alignment(content: str) -> dict:
    fm = parse_frontmatter(content)
    blueprint_version = fm.get("version", "unknown")
    registry_path = REPO_ROOT / "docs" / "03_modules" / "blueprint-registry.yaml"
    if not registry_path.exists():
        return {"check": "version_alignment", "status": "WARN", "detail": "registry not found"}
    registry_text = registry_path.read_text(encoding="utf-8")
    match = re.search(r"module_id:\s*MOD-INF-024[\s\S]*?version:\s*['\"]?([0-9.]+)", registry_text)
    if not match:
        return {"check": "version_alignment", "status": "WARN", "detail": "MOD-INF-024 not found in registry"}
    registry_version = match.group(1)
    if blueprint_version == registry_version:
        return {"check": "version_alignment", "status": "PASS", "detail": f"v{blueprint_version} aligned"}
    return {
        "check": "version_alignment",
        "status": "DRIFT",
        "detail": f"blueprint={blueprint_version}, registry={registry_version}",
    }


def check_ssot_claims(content: str) -> dict:
    fm = parse_frontmatter(content)
    ssot_claims = fm.get("ssot_claims", [])
    if not ssot_claims:
        return {"check": "ssot_claims", "status": "WARN", "detail": "no ssot_claims in frontmatter"}
    return {"check": "ssot_claims", "status": "PASS", "detail": f"{len(ssot_claims)} claims declared"}


def check_temporal_content(content: str) -> dict:
    issues: list[str] = []
    if "| 已执行 |" in content:
        issues.append("executed migration entry still present in S5.3")
    if not issues:
        return {"check": "temporal_content", "status": "PASS", "detail": "no stale temporal content"}
    return {"check": "temporal_content", "status": "DRIFT", "detail": "; ".join(issues[:3])}


CHECKS = [
    check_file_list_alignment,
    check_api_signature_alignment,
    check_dependency_registry_alignment,
    check_version_alignment,
    check_ssot_claims,
    check_temporal_content,
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Blueprint-Code alignment check for MOD-INF-024")
    parser.add_argument("--warn-only", action="store_true", help="Exit 0 even on DRIFT")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument("--blueprint", type=str, default=str(BLUEPRINT_PATH), help="Blueprint path")
    args = parser.parse_args()

    bp_path = Path(args.blueprint)
    if not bp_path.exists():
        print(f"CRITICAL: blueprint not found: {bp_path}")
        sys.exit(2)

    content = bp_path.read_text(encoding="utf-8")
    results = []
    for check_fn in CHECKS:
        results.append(check_fn(content))

    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        for r in results:
            icon = (
                "PASS"
                if r["status"] == "PASS"
                else ("DRIFT" if r["status"] == "DRIFT" else ("WARN" if r["status"] == "WARN" else "CRITICAL"))
            )
            print(f"  [{icon}] {r['check']}: {r['detail']}")

    has_critical = any(r["status"] == "CRITICAL" for r in results)
    has_drift = any(r["status"] == "DRIFT" for r in results)

    if has_critical:
        print("\nResult: CRITICAL")
        sys.exit(2)
    if has_drift and not args.warn_only:
        print("\nResult: DRIFT_DETECTED")
        sys.exit(1)
    print("\nResult: ALIGNED")
    sys.exit(0)


if __name__ == "__main__":
    main()
