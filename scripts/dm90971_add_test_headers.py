# [BLUEPRINT] MOD-GOV-SCRIPTS
# [MODULE] scripts.dm90971_add_test_headers
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.__init__
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
# [TTL] permanent
"""DM-90971: Batch add module_id scope prefix + governance anchor headers to test files.

Usage:
  python scripts/dm90971_add_test_headers.py --dry-run     # Preview changes
  python scripts/dm90971_add_test_headers.py --apply        # Apply changes

Design:
  - Deterministic sequential module_id: SRC-TST-0001 through SRC-TST-N
  - Files sorted by relative path for stable, collision-free numbering
  - Changes module_id= → module_id: (colon format for N-06 checker)
  - Adds scope prefix SRC-TST- to all module_id values
  - Adds 6-field [A_test] header to __init__.py files that lack it

RULE-SEVEN: ThreadPoolExecutor(max_workers=8) for parallel I/O.
RULE-ONE: temp-file + atomic rename for all writes.
RULE-FIVE: zero residue after completion.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

# bootstrap: 定位 scripts/governance/ 以 import _shared.constants（REPO_ROOT SSoT 真源）
_GOV_DIR = str(Path(__file__).resolve().parent / "governance")
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import REPO_ROOT  # noqa: E402

_MAX_WORKERS = 8
PROJECT_ROOT = REPO_ROOT
TESTS_DIR = PROJECT_ROOT / "tests"

# ---------------------------------------------------------------------------
# Pattern definitions
# ---------------------------------------------------------------------------

_A_TEST_RE = re.compile(r"^#\s*\[A_test\]\s+")
_BLUEPRINT_RE = re.compile(r"^#\s*\[BLUEPRINT\]\s+")
_MODULE_ID_ASSIGN_RE = re.compile(r"module_id=(\S+)")

# N-06 compliant scope — SRC (Source) + TST (Test) domain
_SCOPE_PREFIX = "SRC-TST"


def _build_a_test_header(seq_num: int) -> str:
    """Build a 6-field governance anchor header for [A_test].

    Format:
      # [A_test] module_id: SRC-TST-NNNN | layer=test | stability=volatile |
      # safety=L | ai_autonomy=ai_modifiable | error_contract=ImportError→skip
    """
    mid = f"{_SCOPE_PREFIX}-{seq_num:04d}"
    return (
        f"# [A_test] module_id: {mid} | layer=test | stability=volatile | "
        f"safety=L | ai_autonomy=ai_modifiable | "
        f"error_contract=ImportError→skip"
    )


def _make_scope_mid(seq_num: int) -> str:
    """Return scope-prefixed module_id for a given sequence number."""
    return f"{_SCOPE_PREFIX}-{seq_num:04d}"


# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------


def _analyze_file(filepath: Path) -> dict | None:
    """Analyze a single test .py file."""
    try:
        content = filepath.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return None

    rel_path = str(filepath.relative_to(PROJECT_ROOT)).replace("\\", "/")
    lines = content.split("\n")
    first_line = lines[0] if lines else ""
    header_block = "\n".join(lines[:25])

    has_a_test = bool(_A_TEST_RE.search(first_line))
    has_blueprint = bool(_BLUEPRINT_RE.search(content[:600]))
    mid_eq = _MODULE_ID_ASSIGN_RE.search(first_line) if first_line.startswith("# [A_test]") else None

    existing_mid = mid_eq.group(1) if mid_eq else None

    # Check if existing mid already has a valid scope prefix
    valid_scopes = {
        "ADR",
        "CP",
        "KE",
        "STD",
        "DW",
        "SRC",
        "OPS",
        "MOD",
        "PSP",
        "GOV",
        "ARCH",
        "VIEW",
        "DOM",
        "PS",
        "SYS",
        "KBG",
        "REG",
        "IDX",
        "CFG",
        "PHASE",
        "TPL",
        "IRN",
    }
    mid_has_scope = False
    if existing_mid:
        parts = existing_mid.split("-")
        if parts and parts[0] in valid_scopes:
            mid_has_scope = True

    needs_a_test = not has_a_test
    needs_scope_prefix = has_a_test and not mid_has_scope
    needs_change = needs_a_test or needs_scope_prefix

    return {
        "rel_path": rel_path,
        "has_a_test": has_a_test,
        "has_blueprint": has_blueprint,
        "existing_mid": existing_mid,
        "mid_has_scope": mid_has_scope,
        "needs_a_test": needs_a_test,
        "needs_scope_prefix": needs_scope_prefix,
        "needs_change": needs_change,
    }


# ---------------------------------------------------------------------------
# Build mapping: rel_path → seq_num (deterministic, sorted order)
# ---------------------------------------------------------------------------


def _build_seq_map(results: list[dict]) -> dict[str, int]:
    """Assign sequential IDs in sorted rel_path order, stable across runs."""
    all_rel_paths = sorted(r["rel_path"] for r in results)
    return {rel: idx for idx, rel in enumerate(all_rel_paths, start=1)}


# ---------------------------------------------------------------------------
# Dry-run
# ---------------------------------------------------------------------------


def _print_dry_run(results: list[dict], seq_map: dict[str, int]) -> None:
    """Print dry-run preview."""
    add_a_test = [r for r in results if r["needs_a_test"]]
    add_scope = [r for r in results if r["needs_scope_prefix"]]
    no_change = [r for r in results if not r["needs_change"]]

    print("=" * 72)
    print("  DM-90971 DRY-RUN PREVIEW")
    print("=" * 72)
    print(f"  Total .py files in tests/:    {len(results)}")
    print(f"  Add [A_test] header (new):    {len(add_a_test)}")
    print(f"  Add scope prefix to module_id: {len(add_scope)}")
    print(f"  No change needed:             {len(no_change)}")
    print(f"  module_id scheme:             {_SCOPE_PREFIX}-0001..{_SCOPE_PREFIX}-{len(results):04d}")
    print()

    if add_a_test:
        print(f"  --- Files getting NEW [A_test] header ({len(add_a_test)}) ---")
        for r in add_a_test[:10]:
            seq = seq_map[r["rel_path"]]
            mid = _make_scope_mid(seq)
            print(f"    {r['rel_path']}")
            print(f"      → module_id: {mid}")
        if len(add_a_test) > 10:
            print(f"    ... and {len(add_a_test) - 10} more")
        print()

    if add_scope:
        print(f"  --- Files getting scope prefix ({len(add_scope)}) ---")
        for r in add_scope[:10]:
            seq = seq_map[r["rel_path"]]
            old_mid = r["existing_mid"]
            new_mid = _make_scope_mid(seq)
            print(f"    {r['rel_path']}")
            print(f"      old: {old_mid} → new: {new_mid}")
        if len(add_scope) > 10:
            print(f"    ... and {len(add_scope) - 10} more")
        print()

    print("  Run with --apply to execute these changes.")
    print("=" * 72)


# ---------------------------------------------------------------------------
# Apply
# ---------------------------------------------------------------------------


def _apply_one_file(result: dict, seq_num: int) -> tuple[str, bool, str]:
    """Apply changes to one file. Returns (rel_path, success, message)."""
    rel_path = result["rel_path"]
    filepath = PROJECT_ROOT / rel_path

    if not result["needs_change"]:
        return (rel_path, True, "no change needed")

    try:
        content = filepath.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return (rel_path, False, f"read error: {e}")

    lines = content.split("\n")
    new_mid = _make_scope_mid(seq_num)

    if result["needs_a_test"]:
        # Insert [A_test] header as NEW first line
        a_test_line = _build_a_test_header(seq_num)
        new_lines = [a_test_line] + list(lines)
    else:
        # Replace module_id=T-XXX → module_id: SRC-TST-NNNN on first line
        new_lines = list(lines)
        first_line = new_lines[0]
        new_first = _MODULE_ID_ASSIGN_RE.sub(f"module_id: {new_mid}", first_line, count=1)
        new_lines[0] = new_first

    new_content = "\n".join(new_lines)

    # RULE-ONE: temp-file + atomic rename
    tmp_path = str(filepath) + f".{os.getpid()}.tmp"
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        os.replace(tmp_path, str(filepath))
        return (rel_path, True, f"updated (mid={new_mid})")
    except PermissionError:
        _cleanup_tmp(tmp_path)
        return (rel_path, False, "permission denied")
    except Exception as e:
        _cleanup_tmp(tmp_path)
        return (rel_path, False, str(e))


def _cleanup_tmp(tmp_path: str) -> None:
    """Safely remove a temp file."""
    try:
        os.remove(tmp_path)
    except OSError:
        pass


def _apply_all(results: list[dict], seq_map: dict[str, int]) -> dict:
    """Apply changes in parallel with ThreadPoolExecutor (RULE-SEVEN)."""
    to_modify = [(r, seq_map[r["rel_path"]]) for r in results if r["needs_change"]]

    stats = {"total": len(results), "attempted": len(to_modify), "success": 0, "failed": 0, "errors": []}

    with ThreadPoolExecutor(max_workers=_MAX_WORKERS) as executor:
        futures = {executor.submit(_apply_one_file, r, seq): r for r, seq in to_modify}
        for future in as_completed(futures):
            path, ok, msg = future.result()
            if ok:
                stats["success"] += 1
            else:
                stats["failed"] += 1
                stats["errors"].append(f"{path}: {msg}")

    return stats


def _print_apply_report(stats: dict) -> None:
    """Print apply summary."""
    print()
    print("=" * 72)
    print("  DM-90971 APPLY REPORT")
    print("=" * 72)
    print(f"  Total files:      {stats['total']}")
    print(f"  Files modified:   {stats['attempted']}")
    print(f"  Success:          {stats['success']}")
    print(f"  Failed:           {stats['failed']}")
    if stats["errors"]:
        print("  Errors:")
        for e in stats["errors"][:30]:
            print(f"    {e}")
        if len(stats["errors"]) > 30:
            print(f"    ... and {len(stats['errors']) - 30} more")
    print("=" * 72)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description="DM-90971: Add governance anchor headers to test files")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true", help="Preview changes without applying")
    group.add_argument("--apply", action="store_true", help="Apply changes to test files")
    args = parser.parse_args()

    print("Scanning tests/ directory...")
    py_files = sorted(TESTS_DIR.rglob("*.py"))
    print(f"Found {len(py_files)} .py files")

    # Phase 1: Analyze all files (parallel)
    print(f"Analyzing files with {_MAX_WORKERS} workers...")
    all_results: list[dict] = []
    with ThreadPoolExecutor(max_workers=_MAX_WORKERS) as executor:
        futures = {executor.submit(_analyze_file, f): f for f in py_files}
        for future in as_completed(futures):
            r = future.result()
            if r:
                all_results.append(r)

    # Sort results by rel_path for deterministic ordering
    all_results.sort(key=lambda r: r["rel_path"])
    print(f"Analysis complete: {len(all_results)} files analyzed")

    # Build sequential mapping (deterministic, collision-free)
    seq_map = _build_seq_map(all_results)

    if args.dry_run:
        _print_dry_run(all_results, seq_map)
        return 0

    if args.apply:
        stats = _apply_all(all_results, seq_map)
        _print_apply_report(stats)
        return 0 if stats["failed"] == 0 else 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
