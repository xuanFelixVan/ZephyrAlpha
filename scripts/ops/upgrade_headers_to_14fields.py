#!/usr/bin/env python3
# [BLUEPRINT] MOD-INF-005 | scripts/ops/upgrade_headers_to_14fields.py | §
# [MODULE] scripts.ops.upgrade_headers_to_14fields
# [DOMAIN] D-GOVERNANCE
# [DEPENDENCIES] depgraph_schema; lock_files; concurrent.futures
# [CONSUMERS] governance automation; CI pipeline
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] --dry-run MUST NOT modify files; --apply MUST use atomic writes (PID-tmp + os.replace); idempotent — re-running on 14-field files is a no-op
# [MODIFY-GUARD] trae_047_engineering_file_header.yaml; align_header_ten_fields.py; verify_header_completeness.py
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] prints ERROR lines to stderr; exit 1 if any write fails; exit 0 on success
# [TESTS] tests/test_upgrade_headers_to_14fields.py
"""
Upgrade A_full file headers from 10 fields to 14 fields per TRAE-047 v1.1.0.

New fields (sourced from depgraph.db):
  [DOMAIN]       — nodes.domain_id
  [DEPENDENCIES] — edges table (from_node_id → to_node_id paths)
  [STARTUP]      — inferred (imported default; manual if __main__ block)
  [MATURITY]     — nodes.design_maturity

Canonical 14-field order:
  [BLUEPRINT]/[MODULE]/[DOMAIN]/[DEPENDENCIES]/[CONSUMERS]/[STARTUP]/[MATURITY]/
  [INVARIANTS]/[MODIFY-GUARD]/[STABILITY]/[SAFETY]/[AI_AUTONOMY]/[ERROR_CONTRACT]/[TESTS]

Usage:
  python scripts/ops/upgrade_headers_to_14fields.py --dry-run              # assess scope
  python scripts/ops/upgrade_headers_to_14fields.py --apply                 # upgrade all
  python scripts/ops/upgrade_headers_to_14fields.py --apply --dir src/zephyr # filter by dir
"""

from __future__ import annotations

import argparse
import os
import re
import sqlite3
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DB_PATH = PROJECT_ROOT / "data" / "databases" / "depgraph.db"

# Canonical 14-field order per TRAE-047 v1.1.0
CANONICAL_FIELDS = [
    "BLUEPRINT",
    "MODULE",
    "DOMAIN",
    "DEPENDENCIES",
    "CONSUMERS",
    "STARTUP",
    "MATURITY",
    "INVARIANTS",
    "MODIFY-GUARD",
    "STABILITY",
    "SAFETY",
    "AI_AUTONOMY",
    "ERROR_CONTRACT",
    "TESTS",
]
CANONICAL_SET = set(CANONICAL_FIELDS)

# Fields that are new in v1.1.0 (were absent in v1.0.x 10-field format)
NEW_FIELDS = {"DOMAIN", "DEPENDENCIES", "STARTUP", "MATURITY"}

# Valid enum values per TRAE-047
VALID_STARTUP = {"auto_start", "event_driven", "scheduled", "manual", "imported"}
VALID_MATURITY = {"design", "prototype", "production", "legacy"}

HEADER_PATTERN = re.compile(r"^#\s*\[([\w-]+)\]\s?(.*)")
MAIN_BLOCK_PATTERN = re.compile(r'^if\s+__name__\s*==\s*["\']__main__["\']\s*:', re.MULTILINE)

EXEMPT_DIRS = {
    "__pycache__",
    ".git",
    ".ailocks",
    "node_modules",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "_backups",
    "_archive",
}
EXEMPT_FILES = {"__init__.py", "__main__.py", "conftest.py"}


@dataclass
class NodeInfo:
    node_id: str = ""
    domain_id: str = ""
    design_maturity: str = ""
    change_policy: str = ""
    impact_level: str = ""
    modification_permission: str = ""


@dataclass
class UpgradeResult:
    path: str
    status: str  # UPGRADED | SKIPPED_14FIELD | SKIPPED_NO_HEADER | SKIPPED_EXEMPT | ERROR
    detail: str = ""
    matched_node: bool = False
    new_fields_added: list = field(default_factory=list)


class DepgraphLoader:
    """Load node info and edges from depgraph.db into memory lookups."""

    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.nodes_by_path: dict[str, NodeInfo] = {}
        self.node_id_to_path: dict[str, str] = {}
        self.edges_from: dict[str, list[str]] = {}  # from_node_id -> [to_path, ...]
        self._load()

    def _load(self) -> None:
        if not self.db_path.exists():
            print(f"WARNING: depgraph.db not found at {self.db_path}", file=sys.stderr)
            return
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            # Load nodes
            cursor = conn.execute(
                "SELECT node_id, path, domain_id, design_maturity, "
                "change_policy, impact_level, modification_permission "
                "FROM nodes WHERE path IS NOT NULL AND path != ''"
            )
            for row in cursor:
                path = self._normalize_path(row["path"])
                if not path:
                    continue
                info = NodeInfo(
                    node_id=row["node_id"] or "",
                    domain_id=row["domain_id"] or "",
                    design_maturity=row["design_maturity"] or "",
                    change_policy=row["change_policy"] or "",
                    impact_level=row["impact_level"] or "",
                    modification_permission=row["modification_permission"] or "",
                )
                self.nodes_by_path[path] = info
                if info.node_id:
                    self.node_id_to_path[info.node_id] = path

            # Load edges (from_node_id -> to_node_id, resolve to to_path)
            cursor = conn.execute(
                "SELECT from_node_id, to_node_id FROM edges WHERE from_node_id IS NOT NULL AND to_node_id IS NOT NULL"
            )
            for row in cursor:
                from_id = row["from_node_id"]
                to_id = row["to_node_id"]
                to_path = self.node_id_to_path.get(to_id, to_id)
                self.edges_from.setdefault(from_id, []).append(to_path)
        finally:
            conn.close()

        print(
            f"[DEPGRAPH] Loaded {len(self.nodes_by_path)} nodes, {sum(len(v) for v in self.edges_from.values())} edges"
        )

    @staticmethod
    def _normalize_path(p: str) -> str:
        """Normalize to forward-slash relative path without leading ./"""
        p = p.replace("\\", "/").strip()
        if p.startswith("./"):
            p = p[2:]
        return p

    def get_node(self, rel_path: str) -> NodeInfo | None:
        norm = self._normalize_path(rel_path)
        return self.nodes_by_path.get(norm)

    def get_dependencies(self, node_id: str) -> list[str]:
        if not node_id:
            return []
        deps = self.edges_from.get(node_id, [])
        # Convert paths to short module names for readability
        short = []
        for d in deps:
            # e.g. "src/zephyr/trading/autopilot.py" -> "zephyr.trading.autopilot"
            if d.endswith(".py"):
                d = d[:-3]
            d = d.replace("src/zephyr/", "zephyr.").replace("scripts/", "scripts.")
            d = d.replace("/", ".")
            short.append(d)
        # Deduplicate preserving order
        seen = set()
        unique = []
        for s in short:
            if s not in seen:
                seen.add(s)
                unique.append(s)
        return unique


def parse_header(lines: list[str]) -> tuple[dict[str, str], list[tuple[int, str, str]], list[tuple[int, str]]]:
    """Parse header fields from file lines.

    Returns:
        fields: dict of FIELD_NAME -> value
        header_lines: list of (line_idx, field_name, raw_line) for recognized fields
        extra_lines: list of (line_idx, raw_line) for unrecognized # [...] lines
    """
    fields: dict[str, str] = {}
    header_lines: list[tuple[int, str, str]] = []
    extra_lines: list[tuple[int, str]] = []

    # Scan first 30 lines for header fields (comment lines with [FIELD])
    for i, line in enumerate(lines[:30]):
        stripped = line.rstrip("\n")
        m = HEADER_PATTERN.match(stripped)
        if m:
            field_name = m.group(1)
            value = m.group(2).strip()
            if field_name in CANONICAL_SET:
                fields[field_name] = value
                header_lines.append((i, field_name, stripped))
            else:
                # Non-standard field like [A_module] — preserve
                extra_lines.append((i, stripped))

    return fields, header_lines, extra_lines


def find_header_region(
    lines: list[str], header_lines: list[tuple[int, str, str]], extra_lines: list[tuple[int, str]]
) -> tuple[int, int]:
    """Find the start and end line indices of the header region.

    The header region is the contiguous block of comment lines containing [FIELD]
    markers, starting from the first such line.
    """
    all_header_indices = sorted([idx for idx, _, _ in header_lines] + [idx for idx, _ in extra_lines])
    if not all_header_indices:
        return (-1, -1)

    start = all_header_indices[0]
    # End = last header line index (the region to replace)
    end = all_header_indices[-1]
    return (start, end)


def infer_startup(filepath: Path, content: str) -> str:
    """Infer startup mode from file content."""
    if MAIN_BLOCK_PATTERN.search(content):
        return "manual"
    # Scripts with argparse are typically manual
    rel = str(filepath.relative_to(PROJECT_ROOT)).replace("\\", "/")
    if rel.startswith("scripts/") and "argparse" in content:
        return "manual"
    return "imported"


def build_header_block(
    fields: dict[str, str], node: NodeInfo | None, deps: list[str], filepath: Path, content: str
) -> str:
    """Build the canonical 14-field header block, preserving existing values."""
    rel = str(filepath.relative_to(PROJECT_ROOT)).replace("\\", "/")

    # Derive values for new fields
    domain_val = fields.get("DOMAIN", "")
    if not domain_val and node and node.domain_id:
        domain_val = node.domain_id

    deps_val = fields.get("DEPENDENCIES", "")
    if not deps_val:
        deps_val = "; ".join(deps) if deps else ""

    startup_val = fields.get("STARTUP", "")
    if not startup_val or startup_val not in VALID_STARTUP:
        startup_val = infer_startup(filepath, content)

    maturity_val = fields.get("MATURITY", "")
    if not maturity_val or maturity_val not in VALID_MATURITY:
        if node and node.design_maturity in VALID_MATURITY:
            maturity_val = node.design_maturity
        else:
            maturity_val = "production"

    # Build canonical 14-field block
    lines = []
    for fname in CANONICAL_FIELDS:
        if fname == "DOMAIN":
            val = domain_val
        elif fname == "DEPENDENCIES":
            val = deps_val
        elif fname == "STARTUP":
            val = startup_val
        elif fname == "MATURITY":
            val = maturity_val
        else:
            val = fields.get(fname, "")
        if val:
            lines.append(f"# [{fname}] {val}")
        else:
            lines.append(f"# [{fname}]")
    return "\n".join(lines) + "\n"


def upgrade_file(filepath: Path, loader: DepgraphLoader, dry_run: bool) -> UpgradeResult:
    """Upgrade a single file's header to 14 fields."""
    rel = str(filepath.relative_to(PROJECT_ROOT)).replace("\\", "/")

    # Skip exempt files
    if filepath.name in EXEMPT_FILES:
        return UpgradeResult(path=rel, status="SKIPPED_EXEMPT")

    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        return UpgradeResult(path=rel, status="ERROR", detail=str(e))

    lines = content.splitlines(keepends=True)
    fields, header_lines, extra_lines = parse_header(lines)

    # No header at all — skip (use add_file_headers.py for those)
    if not header_lines:
        return UpgradeResult(path=rel, status="SKIPPED_NO_HEADER")

    # Already has all 14 fields — skip (idempotent)
    missing_new = NEW_FIELDS - set(fields.keys())
    if not missing_new:
        return UpgradeResult(path=rel, status="SKIPPED_14FIELD", detail="already 14 fields")

    # Get depgraph node info
    node = loader.get_node(rel)
    deps = loader.get_dependencies(node.node_id) if node else []

    # Find header region to replace
    start, end = find_header_region(lines, header_lines, extra_lines)
    if start < 0:
        return UpgradeResult(path=rel, status="ERROR", detail="cannot locate header region")

    # Build new header
    new_header = build_header_block(fields, node, deps, filepath, content)

    # Preserve extra (non-standard) fields after canonical block
    if extra_lines:
        extra_str = "\n".join(raw for _, raw in extra_lines)
        new_header = new_header.rstrip("\n") + "\n" + extra_str + "\n"

    # Reconstruct file: lines[:start] + new_header + lines[end+1:]
    before = "".join(lines[:start])
    after = "".join(lines[end + 1 :])
    new_content = before + new_header + after

    if new_content == content:
        return UpgradeResult(path=rel, status="SKIPPED_14FIELD", detail="no change needed")

    if dry_run:
        return UpgradeResult(
            path=rel,
            status="UPGRADED",
            detail=f"would add: {', '.join(sorted(missing_new))}",
            matched_node=node is not None,
            new_fields_added=sorted(missing_new),
        )

    # Atomic write (RULE-ONE)
    tmp_path = str(filepath) + f".{os.getpid()}.tmp"
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        os.replace(tmp_path, str(filepath))
    except PermissionError:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
        return UpgradeResult(path=rel, status="ERROR", detail="permission denied")
    except Exception as e:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
        return UpgradeResult(path=rel, status="ERROR", detail=str(e))

    return UpgradeResult(
        path=rel,
        status="UPGRADED",
        detail=f"added: {', '.join(sorted(missing_new))}",
        matched_node=node is not None,
        new_fields_added=sorted(missing_new),
    )


def collect_py_files(dir_filter: str) -> list[Path]:
    """Collect .py files from src/zephyr/ and scripts/, optionally filtered."""
    scan_dirs = [PROJECT_ROOT / "src" / "zephyr", PROJECT_ROOT / "scripts"]
    if dir_filter:
        norm_filter = dir_filter.replace("\\", "/")
        scan_dirs = [d for d in scan_dirs if norm_filter in str(d).replace("\\", "/")]

    files = []
    for scan_dir in scan_dirs:
        if not scan_dir.exists():
            continue
        for root, dirs, filenames in os.walk(scan_dir):
            dirs[:] = [d for d in dirs if d not in EXEMPT_DIRS and not d.startswith(".")]
            for fn in filenames:
                if not fn.endswith(".py"):
                    continue
                files.append(Path(root) / fn)
    return sorted(files)


def main() -> None:
    parser = argparse.ArgumentParser(description="Upgrade A_full headers from 10 to 14 fields (TRAE-047 v1.1.0)")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", default=True, help="Assess scope without modifying (default)")
    mode.add_argument("--apply", action="store_true", help="Apply upgrades (atomic writes)")
    parser.add_argument("--dir", type=str, default="", help="Filter by directory (e.g. src/zephyr or scripts)")
    parser.add_argument("--max-workers", type=int, default=8, help="ThreadPoolExecutor workers")
    args = parser.parse_args()

    dry_run = not args.apply
    print(
        f"[UPGRADE] mode={'DRY-RUN' if dry_run else 'APPLY'} "
        f"dir_filter={args.dir or 'ALL'} max_workers={args.max_workers}"
    )

    # Load depgraph data
    loader = DepgraphLoader(DB_PATH)

    # Collect files
    py_files = collect_py_files(args.dir)
    print(f"[UPGRADE] collected {len(py_files)} .py files")

    # Process in parallel
    results: list[UpgradeResult] = []
    with ThreadPoolExecutor(max_workers=args.max_workers) as pool:
        futures = {pool.submit(upgrade_file, fp, loader, dry_run): fp for fp in py_files}
        for fut in as_completed(futures):
            results.append(fut.result())

    # Summary
    upgraded = [r for r in results if r.status == "UPGRADED"]
    skipped_14 = [r for r in results if r.status == "SKIPPED_14FIELD"]
    skipped_no = [r for r in results if r.status == "SKIPPED_NO_HEADER"]
    skipped_ex = [r for r in results if r.status == "SKIPPED_EXEMPT"]
    errors = [r for r in results if r.status == "ERROR"]

    matched = sum(1 for r in upgraded if r.matched_node)
    unmatched = len(upgraded) - matched

    print("\n" + "=" * 70)
    print("UPGRADE SUMMARY (10-field → 14-field)")
    print("=" * 70)
    print(f"Total files scanned:      {len(results)}")
    print(f"Upgraded:                 {len(upgraded)}")
    print(f"  matched depgraph node:  {matched}")
    print(f"  unmatched (defaults):   {unmatched}")
    print(f"Already 14-field:         {len(skipped_14)}")
    print(f"No header (skip):         {len(skipped_no)}")
    print(f"Exempt (__init__/etc):    {len(skipped_ex)}")
    print(f"Errors:                   {len(errors)}")
    print()

    # New field coverage stats
    field_counts: dict[str, int] = {f: 0 for f in NEW_FIELDS}
    for r in upgraded:
        for f in r.new_fields_added:
            field_counts[f] = field_counts.get(f, 0) + 1
    print("New fields added:")
    for f in ["DOMAIN", "DEPENDENCIES", "STARTUP", "MATURITY"]:
        print(f"  [{f}]{'':<13} {field_counts.get(f, 0):>5} files")
    print()

    if errors:
        print("ERRORS:")
        for r in errors[:20]:
            print(f"  {r.path}: {r.detail}")
        if len(errors) > 20:
            print(f"  ... and {len(errors) - 20} more")
        print()

    if dry_run and upgraded:
        print("Sample upgrades (first 10):")
        for r in upgraded[:10]:
            print(f"  {r.path}")
            print(f"    -> {r.detail}")
            print(f"    node_match={r.matched_node}")
        if len(upgraded) > 10:
            print(f"  ... and {len(upgraded) - 10} more")
        print()

    print("=" * 70)
    if errors:
        print(f"RESULT: {len(errors)} ERRORS — fix before proceeding")
        sys.exit(1)
    elif dry_run:
        print(f"RESULT: {len(upgraded)} files would be upgraded (dry-run)")
    else:
        print(f"RESULT: {len(upgraded)} files upgraded successfully")
    print("=" * 70)


if __name__ == "__main__":
    main()
