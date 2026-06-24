#!/usr/bin/env python3
"""
# [BLUEPRINT] MOD-INF-005 | scripts/governance/add_file_headers.py | §7
# [MODULE] scripts.governance.add_file_headers
# [DOMAIN] D-GOVERNANCE
# [DEPENDENCIES] scripts.governance.__init__
# [CONSUMERS] CI pipeline; governance automation
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] --dry-run MUST NOT modify any file; --apply MUST modify files atomically
# [MODIFY-GUARD] file-header-standard.md; frontmatter-field-registry.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] HeaderError; MappingError
# [TESTS] tests/test_add_file_headers.py
"""

import argparse
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

DIR_TO_BLUEPRINT = {
    "src/zephyr/agent-rbac": (
        "MOD-INF-018",
        "docs/03_modules/infrastructure.runtime_integration/agent-rbac/blueprint.md",
    ),
    "src/zephyr/gates": ("MOD-INF-007", "docs/03_modules/_cross_layer/gate-engine/blueprint.md"),
    "src/zephyr/gate_engine": ("MOD-INF-007", "docs/03_modules/_cross_layer/gate-engine/blueprint.md"),
    "src/zephyr/feedback-loop": ("MOD-INF-010", "docs/03_modules/_cross_layer/feedback-loop/blueprint.md"),
    "src/zephyr/kb": ("MOD-KB-001", "docs/03_modules/infrastructure.runtime_integration/knowledge-base/blueprint.md"),
    "src/zephyr/rollback": ("MOD-INF-015", "docs/03_modules/_cross_layer/shared-core/blueprint.md"),
    "src/zephyr/audit-trail": ("MOD-INF-011", "docs/03_modules/_cross_layer/audit-orchestrator/blueprint.md"),
    "src/zephyr/escalation-engine": ("MOD-INF-017", "docs/03_modules/_cross_layer/shared-core/blueprint.md"),
    "src/zephyr/budget-enforcer": (
        "MOD-INF-024",
        "docs/03_modules/infrastructure.runtime_integration/budget-enforcer/blueprint.md",
    ),
    "src/zephyr/llm-security": ("MOD-INF-014", "docs/03_modules/_cross_layer/llm-security/blueprint.md"),
    "src/zephyr/context-engine": ("MOD-INF-008", "docs/03_modules/_cross_layer/context-engine/blueprint.md"),
    "src/zephyr/mcp": ("MOD-INF-013", "docs/03_modules/_cross_layer/mcp-servers/blueprint.md"),
    "src/zephyr/mcp_servers": ("MOD-INF-013", "docs/03_modules/_cross_layer/mcp-servers/blueprint.md"),
    "src/zephyr/pipeline": ("MOD-INF-009", "docs/03_modules/_cross_layer/pipeline/blueprint.md"),
    "src/zephyr/shared": ("MOD-INF-016", "docs/03_modules/_cross_layer/shared-core/blueprint.md"),
    "src/zephyr/orchestrator": ("MOD-INF-035", "docs/03_modules/_cross_layer/auto-runtime-core/blueprint.md"),
    "src/zephyr/runtime": ("MOD-INF-035", "docs/03_modules/_cross_layer/auto-runtime-core/blueprint.md"),
    "src/zephyr/core": ("MOD-INF-035", "docs/03_modules/_cross_layer/auto-runtime-core/blueprint.md"),
    "src/zephyr/db": ("MOD-INF-012", "docs/03_modules/_cross_layer/database/blueprint.md"),
    "src/zephyr/a2a": ("MOD-INF-025", "docs/03_modules/infrastructure.runtime_integration/a2a-protocol/blueprint.md"),
    "src/zephyr/agent-spec": ("MOD-INF-019", "docs/03_modules/_sys-master/blueprint_agent_spec.md"),
    "src/zephyr/asset-inventory": ("MOD-INF-016", "docs/03_modules/_cross_layer/shared-core/blueprint.md"),
    "src/zephyr/behavioral-auditor": ("MOD-INF-011", "docs/03_modules/_cross_layer/behavioral-auditor/blueprint.md"),
    "src/zephyr/capacity-assurance": (
        "MOD-INF-001",
        "docs/03_modules/infrastructure.runtime_integration/capacity-assurance/blueprint.md",
    ),
    "src/zephyr/code_dedup_engine": ("MOD-INF-031", "docs/03_modules/_cross_layer/auto-fix-engine/blueprint.md"),
    "src/zephyr/contracts": ("MOD-INF-016", "docs/03_modules/_cross_layer/shared-core/blueprint.md"),
    "src/zephyr/drift-detector": ("MOD-INF-026", "docs/03_modules/_cross_layer/shared-core/blueprint.md"),
    "src/zephyr/escalation": ("MOD-INF-017", "docs/03_modules/_cross_layer/shared-core/blueprint.md"),
    "src/zephyr/governance": ("DOM-GOV-001", "docs/03_modules/_domain-governance/blueprint.md"),
    "src/zephyr/hooks": ("MOD-INF-035", "docs/03_modules/_cross_layer/auto-runtime-core/blueprint.md"),
    "src/zephyr/infrastructure": (
        "MOD-INF-002",
        "docs/03_modules/infrastructure.runtime_integration/governance-automation/blueprint.md",
    ),
    "src/zephyr/infrastructure/escalation_protocol": (
        "MOD-INF-017",
        "docs/03_modules/_cross_layer/shared-core/blueprint.md",
    ),
    "src/zephyr/data": ("MOD-L00-001", "docs/03_modules/data/datasource-core/blueprint.md"),
    "src/zephyr/infrastructure.runtime_integration": (
        "MOD-INF-002",
        "docs/03_modules/infrastructure.runtime_integration/governance-automation/blueprint.md",
    ),
    "src/zephyr/factor": ("MOD-L02-001", "docs/03_modules/_alpha-signal-domain/blueprint.md"),
    "src/zephyr/signal": ("MOD-L03-001", "docs/03_modules/signal/signal-generation-core/blueprint.md"),
    "src/zephyr/risk": ("MOD-L04-001", "docs/03_modules/risk/risk-management-core/blueprint.md"),
    "src/zephyr/pf_core": ("MOD-L05-001", "docs/03_modules/pf_core/portfolio-core/blueprint.md"),
    "src/zephyr/ex_core": ("MOD-L06-001", "docs/03_modules/ex_core/execution-core/blueprint.md"),
    "src/zephyr/pf_core": ("MOD-L07-001", "docs/03_modules/pf_core/analytics-core/blueprint.md"),
    "src/zephyr/compliance": ("MOD-L10-001", "docs/03_modules/_domain-compliance/compliance-core/blueprint.md"),
    "src/zephyr/ml_train": ("MOD-L11-001", "docs/03_modules/_domain-ml_train/ml-core/blueprint.md"),
    "src/zephyr/integration": ("MOD-L13-001", "docs/03_modules/integration/experiment-core/blueprint.md"),
    "src/zephyr/frontend": (
        "MOD-L08-001",
        "docs/03_modules/infrastructure.runtime_integration/governance-automation/blueprint.md",
    ),
    "src/zephyr/research": (
        "MOD-L09-001",
        "docs/03_modules/infrastructure.runtime_integration/governance-automation/blueprint.md",
    ),
    "src/zephyr/telemetry": ("MOD-INF-027", "docs/03_modules/_cross_layer/shared-core/blueprint.md"),
    "src/zephyr/vector-memory": ("MOD-INF-028", "docs/03_modules/_cross_layer/shared-core/blueprint.md"),
    "tests/agent-rbac": ("MOD-INF-018", "docs/03_modules/infrastructure.runtime_integration/agent-rbac/blueprint.md"),
    "tests/audit-trail": ("MOD-INF-011", "docs/03_modules/_cross_layer/audit-orchestrator/blueprint.md"),
    "tests/budget-enforcer": (
        "MOD-INF-024",
        "docs/03_modules/infrastructure.runtime_integration/budget-enforcer/blueprint.md",
    ),
    "tests/context-engine": ("MOD-INF-008", "docs/03_modules/_cross_layer/context-engine/blueprint.md"),
    "tests/feedback-loop": ("MOD-INF-010", "docs/03_modules/_cross_layer/feedback-loop/blueprint.md"),
    "tests/gate_engine": ("MOD-INF-007", "docs/03_modules/_cross_layer/gate-engine/blueprint.md"),
    "tests/governance": ("DOM-GOV-001", "docs/03_modules/_domain-governance/blueprint.md"),
    "tests/kb": ("MOD-KB-001", "docs/03_modules/infrastructure.runtime_integration/knowledge-base/blueprint.md"),
    "tests/llm-security": ("MOD-INF-014", "docs/03_modules/_cross_layer/llm-security/blueprint.md"),
    "tests/mcp": ("MOD-INF-013", "docs/03_modules/_cross_layer/mcp-servers/blueprint.md"),
    "tests/orchestrator": ("MOD-INF-035", "docs/03_modules/_cross_layer/auto-runtime-core/blueprint.md"),
    "tests/pipeline": ("MOD-INF-009", "docs/03_modules/_cross_layer/pipeline/blueprint.md"),
    "tests/rollback": ("MOD-INF-015", "docs/03_modules/_cross_layer/shared-core/blueprint.md"),
    "tests/shared": ("MOD-INF-016", "docs/03_modules/_cross_layer/shared-core/blueprint.md"),
    "tests/adversarial": ("DOM-GOV-001", "docs/03_modules/_domain-governance/blueprint.md"),
    "tests/integration": ("DOM-GOV-001", "docs/03_modules/_domain-governance/blueprint.md"),
    "tests/e2e": ("DOM-GOV-001", "docs/03_modules/_domain-governance/blueprint.md"),
    "tests": ("DOM-GOV-001", "docs/03_modules/_domain-governance/blueprint.md"),
    "src/zephyr/lifecycle_manager": ("MOD-INF-035", "docs/03_modules/_cross_layer/auto-runtime-core/blueprint.md"),
    "src/zephyr/model-capability-exam": ("MOD-INF-034", "docs/03_modules/_cross_layer/model-profiler/blueprint.md"),
    "src/zephyr/model-profiler": ("MOD-INF-034", "docs/03_modules/_cross_layer/model-profiler/blueprint.md"),
    "src/zephyr/orphan-judge": ("MOD-INF-031", "docs/03_modules/_cross_layer/orphan-judge/blueprint.md"),
    "src/zephyr/red-blue-validator": ("MOD-INF-030", "docs/03_modules/_cross_layer/red-blue-validator/blueprint.md"),
    "src/zephyr/semantic-auditor": ("MOD-INF-011", "docs/03_modules/_cross_layer/semantic-auditor/blueprint.md"),
    "src/zephyr/script_system": (
        "MOD-INF-005",
        "docs/03_modules/infrastructure.runtime_integration/governance-automation/blueprint.md",
    ),
    "src/zephyr/_cross_layer": ("MOD-INF-016", "docs/03_modules/_cross_layer/shared-core/blueprint.md"),
    "scripts": ("MOD-INF-005", "docs/03_modules/infrastructure.runtime_integration/governance-automation/blueprint.md"),
    "config/capacity": (
        "MOD-INF-001",
        "docs/03_modules/infrastructure.runtime_integration/capacity-assurance/blueprint.md",
    ),
    "config/compression": ("GOV-DOC-011", "docs/01_policies_and_standards/rules/trae_030_doc_numbering_metadata.yaml"),
    "config/data": ("MOD-INF-016", "docs/03_modules/_cross_layer/shared-core/blueprint.md"),
    "config": ("MOD-INF-002", "docs/03_modules/infrastructure.runtime_integration/governance-automation/blueprint.md"),
    "data/capability_cards": ("MOD-INF-035", "docs/03_modules/_cross_layer/auto-runtime-core/blueprint.md"),
    "data/work_dags": ("MOD-INF-035", "docs/03_modules/_cross_layer/auto-runtime-core/blueprint.md"),
    "data/security_baselines": (
        "MOD-INF-018",
        "docs/03_modules/infrastructure.runtime_integration/agent-rbac/blueprint.md",
    ),
    "data/health_snapshots": ("MOD-INF-035", "docs/03_modules/_cross_layer/auto-runtime-core/blueprint.md"),
    "data/drift_checkpoints": ("MOD-INF-026", "docs/03_modules/_cross_layer/shared-core/blueprint.md"),
    "data/drift_handoffs": ("MOD-INF-026", "docs/03_modules/_cross_layer/shared-core/blueprint.md"),
    "data/drift_runbooks": ("MOD-INF-026", "docs/03_modules/_cross_layer/shared-core/blueprint.md"),
    "data/feedback_proposals": ("MOD-INF-010", "docs/03_modules/_cross_layer/feedback-loop/blueprint.md"),
    "data/circadian_tasks": ("MOD-INF-035", "docs/03_modules/_cross_layer/auto-runtime-core/blueprint.md"),
    "data/classified": ("MOD-INF-018", "docs/03_modules/infrastructure.runtime_integration/agent-rbac/blueprint.md"),
    "data/dream_archive": ("MOD-INF-035", "docs/03_modules/_cross_layer/auto-runtime-core/blueprint.md"),
    "data/metrics": ("MOD-INF-035", "docs/03_modules/_cross_layer/auto-runtime-core/blueprint.md"),
    "data": ("MOD-INF-035", "docs/03_modules/_cross_layer/auto-runtime-core/blueprint.md"),
}

EXEMPT_DIRS = {
    "__pycache__",
    ".git",
    ".ailocks",
    "node_modules",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "_backups",
    "snapshot_*",
}

EXEMPT_FILE_PATTERNS = {
    "__init__.py",
    ".gitkeep",
    ".gitignore",
}

HEADER_FORMAT_MAP = {
    "code": "A_full",
    "script": "A_full",
    "test": "A_test",
    "gate": "B_yaml",
    "registry": "B_yaml",
    "contract": "B_yaml",
    "config": "B_yaml",
    "data": "B_yaml",
    "doc": "D_md",
    "infra": "E_shell",
}


@dataclass
class ScanResult:
    path: str
    file_category: str
    header_format: str
    has_header: bool = False
    blueprint_id: str = ""
    blueprint_path: str = ""
    status: str = "pending"


def classify_file(rel_path: str) -> str:
    if rel_path.startswith("src/zephyr/gates/") and rel_path.endswith(".yaml"):
        return "gate"
    if rel_path.startswith("src/zephyr/") and rel_path.endswith(".py"):
        if rel_path.startswith("tests/"):
            return "test"
        return "code"
    if rel_path.startswith("scripts/") and rel_path.endswith(".py"):
        return "script"
    if rel_path.startswith("tests/") and rel_path.endswith(".py"):
        return "test"
    if any(p in rel_path for p in ("_registry.yaml", "manifest.yaml")):
        return "registry"
    if rel_path.startswith("data/") and rel_path.endswith(".yaml"):
        return "data"
    if rel_path.startswith("config/") and rel_path.endswith(".yaml"):
        return "config"
    if rel_path.startswith("docs/") and rel_path.endswith(".md"):
        return "doc"
    if rel_path.endswith((".sh", ".ps1", ".mmd")):
        return "infra"
    if rel_path.startswith("src/zephyr/shared/contracts/"):
        return "contract"
    if rel_path.endswith((".yaml", ".yml")):
        return "config"
    if rel_path.endswith(".py"):
        return "code"
    return ""


def find_blueprint(rel_path: str) -> tuple:
    parts = rel_path.replace("\\", "/").split("/")
    for i in range(min(len(parts), 4), 0, -1):
        prefix = "/".join(parts[:i])
        if prefix in DIR_TO_BLUEPRINT:
            return DIR_TO_BLUEPRINT[prefix]
    return ("UNMAPPED", "UNMAPPED")


def check_py_header(filepath: Path) -> bool:
    try:
        with open(filepath, encoding="utf-8", errors="ignore") as f:
            for i, line in enumerate(f):
                if i >= 10:
                    break
                if "[BLUEPRINT]" in line:
                    return True
    except Exception:
        pass
    return False


def check_yaml_header(filepath: Path) -> bool:
    try:
        with open(filepath, encoding="utf-8", errors="ignore") as f:
            for i, line in enumerate(f):
                if i >= 30:
                    break
                if "治理锚定" in line or ("blueprint:" in line and "#" in line):
                    return True
    except Exception:
        pass
    return False


def scan_file(rel_path: str) -> ScanResult | None:
    basename = os.path.basename(rel_path)
    if basename in EXEMPT_FILE_PATTERNS:
        return None
    if any(
        basename.startswith(p)
        for p in ("_temp", "_check", "_fix", "_phase_", "_deep", "_construction", "_rebuild", "_audit")
    ):
        if basename.endswith((".py", ".yaml", ".json")):
            return None
    file_category = classify_file(rel_path)
    if not file_category:
        return None
    header_format = HEADER_FORMAT_MAP.get(file_category, "")
    if not header_format:
        return None
    filepath = PROJECT_ROOT / rel_path
    has_header = False
    if header_format in ("A_full", "A_test"):
        has_header = check_py_header(filepath)
    elif header_format == "B_yaml":
        has_header = check_yaml_header(filepath)
    elif header_format == "E_shell":
        has_header = check_py_header(filepath)
    elif header_format == "D_md":
        has_header = True
    blueprint_id, blueprint_path = find_blueprint(rel_path)
    return ScanResult(
        path=rel_path,
        file_category=file_category,
        header_format=header_format,
        has_header=has_header,
        blueprint_id=blueprint_id,
        blueprint_path=blueprint_path,
    )


def generate_py_header(result: ScanResult) -> str:
    rel = result.path.replace("\\", "/")
    module_path = rel.replace("/", ".").replace(".py", "")
    if result.file_category == "test":
        return (
            f"# [BLUEPRINT] {result.blueprint_id} | {result.blueprint_path} | §\n"
            f"# [MODULE] {module_path}\n"
            f"# [STABILITY] evolving\n"
            f"# [SAFETY] L\n"
            f"# [AI_AUTONOMY] ai_modifiable\n"
            f"# [TESTS] —\n"
        )
    return (
        f"# [BLUEPRINT] {result.blueprint_id} | {result.blueprint_path} | §\n"
        f"# [MODULE] {module_path}\n"
        f"# [DOMAIN] \n"
        f"# [DEPENDENCIES] \n"
        f"# [CONSUMERS] \n"
        f"# [STARTUP] imported\n"
        f"# [MATURITY] production\n"
        f"# [INVARIANTS] \n"
        f"# [MODIFY-GUARD] \n"
        f"# [STABILITY] evolving\n"
        f"# [SAFETY] M\n"
        f"# [AI_AUTONOMY] ai_modifiable\n"
        f"# [ERROR_CONTRACT] \n"
        f"# [TESTS] \n"
    )


def generate_yaml_header(result: ScanResult) -> str:
    return (
        f"# --- 治理锚定 ---\n"
        f"# blueprint: {result.blueprint_id} | {result.blueprint_path} | §\n"
        f"# module_id: {result.blueprint_id}\n"
        f"# change_policy: evolving\n"
        f"# impact_level: M\n"
        f"# modification_permission: ai_modifiable\n"
        f"# --- 治理锚定结束 ---\n"
    )


def generate_shell_header(result: ScanResult) -> str:
    return (
        f"# [BLUEPRINT] {result.blueprint_id} | {result.blueprint_path} | §\n"
        f"# [STABILITY] evolving\n"
        f"# [SAFETY] L\n"
        f"# [AI_AUTONOMY] ai_modifiable\n"
    )


def apply_header(result: ScanResult, dry_run: bool = True) -> str:
    if result.has_header:
        return "SKIP_HAS_HEADER"
    if result.blueprint_id == "UNMAPPED":
        return "SKIP_UNMAPPED"
    filepath = PROJECT_ROOT / result.path
    if not filepath.exists():
        return "SKIP_NOT_FOUND"
    if result.header_format in ("A_full", "A_test"):
        header_block = generate_py_header(result)
    elif result.header_format == "B_yaml":
        header_block = generate_yaml_header(result)
    elif result.header_format == "E_shell":
        header_block = generate_shell_header(result)
    else:
        return "SKIP_UNSUPPORTED_FORMAT"
    if dry_run:
        return f"WOULD_ADD:{result.header_format}:{result.blueprint_id}"
    try:
        with open(filepath, encoding="utf-8", errors="ignore") as f:
            content = f.read()
        if result.header_format == "B_yaml":
            new_content = header_block + content
        else:
            if content.startswith("#!"):
                shebang_end = content.index("\n") + 1
                new_content = content[:shebang_end] + header_block + content[shebang_end:]
            else:
                new_content = header_block + content
        tmp_path = str(filepath) + f".{os.getpid()}.tmp"
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        os.replace(tmp_path, str(filepath))
        result.has_header = True
        result.status = "anchored"
        return f"ADDED:{result.header_format}:{result.blueprint_id}"
    except Exception as e:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
        return f"ERROR:{e}"


def collect_files() -> list:
    files = []
    scan_dirs = [
        PROJECT_ROOT / "src" / "zephyr",
        PROJECT_ROOT / "scripts",
        PROJECT_ROOT / "tests",
        PROJECT_ROOT / "data",
        PROJECT_ROOT / "config",
    ]
    for scan_dir in scan_dirs:
        if not scan_dir.exists():
            continue
        for root, dirs, filenames in os.walk(scan_dir):
            dirs[:] = [d for d in dirs if d not in EXEMPT_DIRS and not d.startswith(".")]
            for fn in filenames:
                fp = Path(root) / fn
                rel = str(fp.relative_to(PROJECT_ROOT)).replace("\\", "/")
                files.append(rel)
    return files


def main():
    parser = argparse.ArgumentParser(description="Batch add file headers per GOV-ENG-002")
    parser.add_argument("--apply", action="store_true", help="Apply changes (default is dry-run)")
    parser.add_argument(
        "--category",
        type=str,
        default="",
        help="Filter by file_category (code,script,test,gate,registry,data,config,infra)",
    )
    parser.add_argument("--blueprint", type=str, default="", help="Filter by blueprint_id (e.g. MOD-INF-005)")
    parser.add_argument("--max-workers", type=int, default=8, help="ThreadPoolExecutor workers")
    parser.add_argument("--json-output", type=str, default="", help="Write results to JSON file")
    args = parser.parse_args()

    dry_run = not args.apply
    print(
        f"[HEADER-BATCH] mode={'DRY-RUN' if dry_run else 'APPLY'} category={args.category or 'ALL'} blueprint={args.blueprint or 'ALL'}"
    )

    all_files = collect_files()
    print(f"[HEADER-BATCH] scanned {len(all_files)} files")

    results = []
    with ThreadPoolExecutor(max_workers=args.max_workers) as pool:
        futures = {pool.submit(scan_file, f): f for f in all_files}
        for fut in as_completed(futures):
            r = fut.result()
            if r is not None:
                results.append(r)

    if args.category:
        results = [r for r in results if r.file_category == args.category]
    if args.blueprint:
        results = [r for r in results if r.blueprint_id == args.blueprint]

    need_header = [r for r in results if not r.has_header]
    already_have = [r for r in results if r.has_header]
    unmapped = [r for r in need_header if r.blueprint_id == "UNMAPPED"]

    by_cat = {}
    for r in need_header:
        by_cat.setdefault(r.file_category, []).append(r)

    print(f"\n{'=' * 60}")
    print("SCAN SUMMARY")
    print(f"{'=' * 60}")
    print(f"Total scanned:       {len(results)}")
    print(f"Already have header: {len(already_have)}")
    print(f"Need header:         {len(need_header)}")
    print(f"Unmapped blueprint:  {len(unmapped)}")
    print("\nBy category:")
    for cat, items in sorted(by_cat.items()):
        print(f"  {cat:12s}: {len(items):4d} need header")

    by_bp = {}
    for r in need_header:
        if r.blueprint_id != "UNMAPPED":
            by_bp.setdefault(r.blueprint_id, []).append(r)
    if by_bp:
        print("\nBy blueprint (top 15):")
        for bp_id, items in sorted(by_bp.items(), key=lambda x: -len(x[1]))[:15]:
            print(f"  {bp_id:20s}: {len(items):4d} files")

    if unmapped:
        print(f"\nUNMAPPED files ({len(unmapped)}):")
        unmapped_dirs = set()
        for r in unmapped:
            d = "/".join(r.path.replace("\\", "/").split("/")[:3])
            unmapped_dirs.add(d)
        for d in sorted(unmapped_dirs)[:20]:
            print(f"  {d}")

    apply_results = {}
    with ThreadPoolExecutor(max_workers=args.max_workers) as pool:
        futures = {pool.submit(apply_header, r, dry_run): r for r in need_header if r.blueprint_id != "UNMAPPED"}
        for fut in as_completed(futures):
            r = futures[fut]
            status = fut.result()
            apply_results[r.path] = status

    added = sum(1 for s in apply_results.values() if s.startswith("ADDED:") or s.startswith("WOULD_ADD:"))
    skipped = sum(1 for s in apply_results.values() if s.startswith("SKIP"))
    errors = sum(1 for s in apply_results.values() if s.startswith("ERROR"))

    print(f"\n{'=' * 60}")
    print(f"{'WOULD ADD' if dry_run else 'APPLIED'}: {added} | SKIPPED: {skipped} | ERRORS: {errors}")
    print(f"{'=' * 60}")

    if args.json_output:
        output = {
            "mode": "dry_run" if dry_run else "apply",
            "total_scanned": len(results),
            "already_have_header": len(already_have),
            "need_header": len(need_header),
            "unmapped": len(unmapped),
            "added_or_would_add": added,
            "by_category": {cat: len(items) for cat, items in by_cat.items()},
            "by_blueprint": {bp: len(items) for bp, items in by_bp.items()},
            "details": [
                {
                    "path": r.path,
                    "category": r.file_category,
                    "format": r.header_format,
                    "blueprint_id": r.blueprint_id,
                    "status": apply_results.get(r.path, "UNMAPPED"),
                }
                for r in need_header
            ],
        }
        tmp = args.json_output + f".{os.getpid()}.tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        os.replace(tmp, args.json_output)
        print(f"\nResults written to {args.json_output}")

    if errors > 0:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
