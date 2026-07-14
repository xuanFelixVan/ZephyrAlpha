#!/usr/bin/env python3
# [BLUEPRINT] MOD-GOV-SCRIPTS
# [MODULE] scripts.governance.verify_rule_yaml_migration
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.__init__
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
"""verify_rule_yaml_migration.py - 6-dimensional verification of rule YAML migration.

NOTE: MD→YAML migration is complete. source_files field has been removed from
all rule YAML files (D56 ruling: YAML is the sole SSoT). Checks 1 and 2 are
deprecated and now SKIP. Checks 3/4/5/6 verify YAML self-consistency.

Checks:
  1. --check-coverage:     [DEPRECATED] MD→YAML coverage — migration complete
  2. --check-hash:         [DEPRECATED] SHA256 hash — source_files removed
  3. --check-traceability: YAML provenance exists (extracted_at/extracted_by)
  4. --check-references:   All references.rule_ids point to existing YAML files
  5. --check-no-orphan:    No YAML files without rule_id (was: without provenance)
  6. --check-no-duplicate: No duplicate scope+severity YAML files
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

import yaml
from _shared.constants import REPO_ROOT

PROJECT_ROOT = REPO_ROOT
DEFAULT_SOURCE_DIR = "docs/01_policies_and_standards/"
DEFAULT_TARGET_DIR = "docs/01_policies_and_standards/rules/"
MANIFEST_PATH = PROJECT_ROOT / "data" / "databases" / "governance_metadata" / "extraction_manifest.json"


def load_yaml(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_json(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def collect_yaml_files(target_dir: Path, exclude_underscore: bool = False) -> list[Path]:
    if not target_dir.exists():
        return []
    files = sorted(target_dir.glob("*.yaml"))
    if exclude_underscore:
        files = [f for f in files if not f.name.startswith("_")]
    return files


def resolve_source_path(source_ref: str, source_dir: Path) -> Path:
    """Resolve a source file reference to an absolute path.

    provenance.source_files[].path may be:
      - relative to project root (e.g. '.trae/rules/project_rules.md')
      - relative to source_dir (e.g. 'domains/L00_data_source/governance/...')
      - a directory path (e.g. 'docs/01_policies_and_standards/rules')
    """
    candidate = PROJECT_ROOT / source_ref
    if candidate.exists():
        return candidate
    candidate = source_dir / source_ref
    if candidate.exists():
        return candidate
    return candidate


# ---------------------------------------------------------------------------
# Check 1: MD→YAML coverage [DEPRECATED]
# ---------------------------------------------------------------------------
def check_coverage(source_dir: Path, target_dir: Path) -> bool:
    print("\n=== CHECK 1: MD→YAML Coverage [DEPRECATED] ===")
    print("  SKIP: MD→YAML migration is complete (D56 ruling).")
    print("        source_files field removed from all rule YAML files.")
    print("        Coverage check is no longer applicable.")
    return True


# ---------------------------------------------------------------------------
# Check 2: SHA256 hash consistency [DEPRECATED]
# ---------------------------------------------------------------------------
def check_hash(target_dir: Path) -> bool:
    print("\n=== CHECK 2: SHA256 Hash Consistency [DEPRECATED] ===")
    print("  SKIP: source_files field (containing hash) has been removed.")
    print("        YAML files are now the sole SSoT (D56 ruling).")
    print("        Hash verification against original .md files is no longer applicable.")
    return True


# ---------------------------------------------------------------------------
# Check 3: YAML provenance exists (extracted_at/extracted_by)
# ---------------------------------------------------------------------------
def check_traceability(target_dir: Path) -> bool:
    print("\n=== CHECK 3: YAML Provenance Exists ===")
    yaml_files = collect_yaml_files(target_dir, exclude_underscore=True)

    total = 0
    with_provenance = 0
    without_provenance = []

    for yf in yaml_files:
        try:
            data = load_yaml(yf)
        except Exception:
            without_provenance.append(yf.name)
            total += 1
            continue
        if not data:
            without_provenance.append(yf.name)
            total += 1
            continue

        total += 1
        prov = data.get("provenance", {})
        # provenance is valid if it exists and has extracted_at or extracted_by
        if prov and ("extracted_at" in prov or "extracted_by" in prov):
            with_provenance += 1
        else:
            without_provenance.append(yf.name)

    if total == 0:
        print("  SKIP: No YAML files found")
        return True

    pct = with_provenance / total * 100
    passed = pct == 100.0
    status = "PASS" if passed else "FAIL"
    print(f"  {status}: YAML with provenance = {with_provenance}/{total} ({pct:.1f}%)")
    if without_provenance:
        print(f"  YAML without provenance ({len(without_provenance)}):")
        for w in without_provenance[:20]:
            print(f"    - {w}")
    return passed


# ---------------------------------------------------------------------------
# Check 4: References integrity
# ---------------------------------------------------------------------------
def check_references(target_dir: Path) -> bool:
    print("\n=== CHECK 4: References Integrity ===")
    yaml_files = collect_yaml_files(target_dir)

    # Build set of existing rule_ids from YAML files
    existing_rule_ids = set()
    yaml_data_map = {}
    for yf in yaml_files:
        try:
            data = load_yaml(yf)
        except Exception:
            continue
        if not data:
            continue
        rid = data.get("rule_id", "")
        if rid:
            existing_rule_ids.add(rid)
        # Also collect aliases
        for alias in data.get("aliases", []):
            existing_rule_ids.add(alias)
        yaml_data_map[yf.name] = data

    broken_refs = []
    total_refs = 0

    for yf_name, data in yaml_data_map.items():
        refs = data.get("references", {})
        rule_ids = refs.get("rule_ids", [])
        for ref_id in rule_ids:
            total_refs += 1
            if ref_id not in existing_rule_ids:
                broken_refs.append(f"  {yf_name}: references.rule_id '{ref_id}' not found in any YAML")

    passed = len(broken_refs) == 0
    status = "PASS" if passed else "FAIL"
    print(f"  {status}: total references={total_refs}, broken={len(broken_refs)}")
    if broken_refs:
        for b in broken_refs[:20]:
            print(b)
        if len(broken_refs) > 20:
            print(f"  ... and {len(broken_refs) - 20} more broken references")
    return passed


# ---------------------------------------------------------------------------
# Check 5: No orphan YAML (no rule_id)
# ---------------------------------------------------------------------------
def check_no_orphan(target_dir: Path) -> bool:
    print("\n=== CHECK 5: No Orphan YAML (missing rule_id) ===")
    yaml_files = collect_yaml_files(target_dir, exclude_underscore=True)

    orphans = []
    for yf in yaml_files:
        try:
            data = load_yaml(yf)
        except Exception:
            orphans.append(yf.name)
            continue
        if not data:
            orphans.append(yf.name)
            continue

        # YAML is orphan if it has no rule_id
        rule_id = data.get("rule_id", "")
        if not rule_id:
            orphans.append(yf.name)

    passed = len(orphans) == 0
    status = "PASS" if passed else "FAIL"
    print(f"  {status}: orphan YAML files (no rule_id) = {len(orphans)}")
    if orphans:
        for o in orphans:
            print(f"    - {o}")
    return passed


# ---------------------------------------------------------------------------
# Check 6: No duplicate scope+severity
# ---------------------------------------------------------------------------
def check_no_duplicate(target_dir: Path) -> bool:
    print("\n=== CHECK 6: No Duplicate scope+severity ===")
    yaml_files = collect_yaml_files(target_dir)

    scope_sev_map = {}  # (scope, severity) -> list of yaml names
    for yf in yaml_files:
        try:
            data = load_yaml(yf)
        except Exception:
            continue
        if not data:
            continue

        scope = data.get("scope", "")
        severity = data.get("severity", "")
        key = (scope, severity)
        if key not in scope_sev_map:
            scope_sev_map[key] = []
        scope_sev_map[key].append(yf.name)

    duplicates = []
    for key, names in scope_sev_map.items():
        if len(names) > 1:
            duplicates.append((key, names))

    passed = len(duplicates) == 0
    status = "PASS" if passed else "FAIL"
    print(f"  {status}: duplicate scope+severity groups = {len(duplicates)}")
    if duplicates:
        for (scope, severity), names in duplicates:
            print(f"    scope='{scope}', severity='{severity}': {', '.join(names)}")
    return passed


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="6-dimensional verification of rule YAML migration")
    parser.add_argument(
        "--check-coverage", action="store_true", help="[DEPRECATED] MD→YAML coverage — migration complete"
    )
    parser.add_argument("--check-hash", action="store_true", help="[DEPRECATED] SHA256 hash — source_files removed")
    parser.add_argument(
        "--check-traceability", action="store_true", help="YAML provenance exists (extracted_at/extracted_by)"
    )
    parser.add_argument(
        "--check-references", action="store_true", help="All references.rule_ids point to existing YAML"
    )
    parser.add_argument("--check-no-orphan", action="store_true", help="No YAML without rule_id")
    parser.add_argument("--check-no-duplicate", action="store_true", help="No duplicate scope+severity YAML")
    parser.add_argument("--all", action="store_true", help="Run all 6 checks")
    parser.add_argument(
        "--source-dir",
        default=DEFAULT_SOURCE_DIR,
        help=f"Source MD directory (default: {DEFAULT_SOURCE_DIR})",
    )
    parser.add_argument(
        "--target-dir",
        default=DEFAULT_TARGET_DIR,
        help=f"Target YAML directory (default: {DEFAULT_TARGET_DIR})",
    )
    args = parser.parse_args()

    source_dir = PROJECT_ROOT / args.source_dir
    target_dir = PROJECT_ROOT / args.target_dir

    if args.all:
        args.check_coverage = True
        args.check_hash = True
        args.check_traceability = True
        args.check_references = True
        args.check_no_orphan = True
        args.check_no_duplicate = True

    if not any(
        [
            args.check_coverage,
            args.check_hash,
            args.check_traceability,
            args.check_references,
            args.check_no_orphan,
            args.check_no_duplicate,
        ]
    ):
        parser.print_help()
        print("\nError: at least one check flag is required")
        sys.exit(1)

    print(f"Project root: {PROJECT_ROOT}")
    print(f"Source dir:   {source_dir}")
    print(f"Target dir:   {target_dir}")

    results = {}

    if args.check_coverage:
        results["coverage"] = check_coverage(source_dir, target_dir)

    if args.check_hash:
        results["hash"] = check_hash(target_dir)

    if args.check_traceability:
        results["traceability"] = check_traceability(target_dir)

    if args.check_references:
        results["references"] = check_references(target_dir)

    if args.check_no_orphan:
        results["no_orphan"] = check_no_orphan(target_dir)

    if args.check_no_duplicate:
        results["no_duplicate"] = check_no_duplicate(target_dir)

    # Summary
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    all_passed = True
    for name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"  {name:20s} {status}")
        if not passed:
            all_passed = False

    print("=" * 50)
    if all_passed:
        print("ALL CHECKS PASSED")
        sys.exit(0)
    else:
        print("SOME CHECKS FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()
