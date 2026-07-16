# [BLUEPRINT] MOD-INF-GOV | scripts/migration/ | governance root split orchestrator (ARCH-031)
# [MODULE] scripts.migration.governance_root_split
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.governance.ast_import_rewriter, stdlib.shutil, stdlib.argparse, stdlib.concurrent.futures
# [CONSUMERS] ARCH-031 task card (docs/03_modules/_domain_governance/arch_031_governance_root_split_task_card.md)
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] orchestrator pattern; delegates import rewrite to ast_import_rewriter (inward convergence); cut-paste via shutil.move (delete source); idempotent; dry-run supported; atomic write (tmp + os.replace)
# [MODIFY-GUARD] migration_registry.yaml format changes require sync with ast_import_rewriter.MoveEntry fields
# [STABILITY] volatile
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] registry missing -> exit 1; source missing -> record failure continue; target exists -> skip (unless --force)
# [TESTS] tests/governance/test_governance_root_split.py
# [TTL] task_bound
"""ARCH-031: governance/ root flat-files split migration orchestrator.

Orchestrator that delegates import rewriting to ``ast_import_rewriter.py``
(inward convergence: reuse existing AST engine, do NOT build a new libcst tool).

Cut-paste mode: ``shutil.move()`` moves files from ``src/zephyr/governance/<root>.py``
to ``src/zephyr/governance/<subdir>/<root>.py``. After move:
  - import rewrite + [MODULE] header update: delegated to ast_import_rewriter
  - [BLUEPRINT] path update: handled locally via re.sub
  - registry status update: mark entries as ``done`` in migration_registry.yaml

Usage::

    # Dry-run single subdir batch
    python scripts/migration/governance_root_split.py --dry-run --batch escalation --move

    # Apply move + rewrite + headers + registry for one subdir
    python scripts/migration/governance_root_split.py --batch escalation \\
        --move --rewrite-imports --update-headers --update-registry-status

    # Fix external refs across whole project (consumers of moved modules)
    python scripts/migration/governance_root_split.py --fix-external-refs

Registry format (``docs/02_enterprise_architecture/migration_registry.yaml``)::

    entries:
      - old_module: zephyr.governance.escalation_api
        new_module: zephyr.governance.escalation.escalation_api
        old_path: src/zephyr/governance/escalation_api.py
        new_path: src/zephyr/governance/escalation/escalation_api.py
        subdir: escalation
        status: pending
        classification_method: module_frontmatter
"""

from __future__ import annotations

import argparse
import importlib.util
import os
import re
import shutil
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# REPO_ROOT: locate without importing _shared.constants to avoid import-chain
# breakage when governance/ files are mid-migration.
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[2]

REGISTRY_FILE = REPO_ROOT / "docs" / "02_enterprise_architecture" / "migration_registry.yaml"

OLD_PATH_PREFIX = "src/zephyr/governance/"

EXCLUDED_DIRS = {
    ".git",
    "__pycache__",
    ".ailocks",
    ".aidrafts",
    "node_modules",
    ".trae",
    ".mypy_cache",
    ".pytest_cache",
    ".tox",
    ".venv",
    "site-packages",
    ".runtime",
}


# ---------------------------------------------------------------------------
# Load ast_import_rewriter via importlib.util to avoid package-name collision
# between scripts/governance/ and src/zephyr/governance/.
# Pattern mirrors tests/governance/test_ast_import_rewriter.py L17-25.
# ---------------------------------------------------------------------------
_AST_REWRITER_PATH = REPO_ROOT / "scripts" / "governance" / "ast_import_rewriter.py"
_spec = importlib.util.spec_from_file_location(
    "ast_import_rewriter", _AST_REWRITER_PATH
)
assert _spec is not None and _spec.loader is not None, (
    f"Failed to load ast_import_rewriter spec from {_AST_REWRITER_PATH}"
)
ast_import_rewriter = importlib.util.module_from_spec(_spec)
sys.modules["ast_import_rewriter"] = ast_import_rewriter  # required by @dataclass
_spec.loader.exec_module(ast_import_rewriter)

MoveEntry = ast_import_rewriter.MoveEntry
ImportRewriter = ast_import_rewriter.ImportRewriter
RewriteResult = ast_import_rewriter.RewriteResult


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class MigrationEntry:
    """One file migration: old module/path -> new module/path + metadata."""
    old_module: str
    new_module: str
    old_path: str
    new_path: str
    subdir: str
    status: str = "pending"
    classification_method: str = "module_frontmatter"

    def to_move_entry(self) -> MoveEntry:
        """Convert to ast_import_rewriter.MoveEntry."""
        return MoveEntry(
            old_module=self.old_module,
            new_module=self.new_module,
            old_path=self.old_path,
            new_path=self.new_path,
        )


# ---------------------------------------------------------------------------
# Registry load / save
# ---------------------------------------------------------------------------

def load_registry() -> dict:
    """Load migration_registry.yaml. Exit on missing/invalid."""
    try:
        import yaml
    except ImportError:
        print("[ERROR] PyYAML not installed.", file=sys.stderr)
        sys.exit(2)
    if not REGISTRY_FILE.exists():
        print(f"[ERROR] Registry not found: {REGISTRY_FILE}", file=sys.stderr)
        sys.exit(1)
    with open(REGISTRY_FILE, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        print("[ERROR] Invalid YAML structure (expected dict)", file=sys.stderr)
        sys.exit(2)
    return data


def save_registry(data: dict) -> None:
    """Atomically save registry (tmp + os.replace)."""
    import yaml
    content = yaml.dump(
        data, default_flow_style=False, allow_unicode=True, sort_keys=False
    )
    tmp_path = f"{REGISTRY_FILE}.{os.getpid()}.tmp"
    try:
        Path(tmp_path).write_text(content, encoding="utf-8")
        os.replace(tmp_path, REGISTRY_FILE)
    except PermissionError:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
        raise


def get_entries(data: dict, subdir: Optional[str] = None) -> list[MigrationEntry]:
    """Filter registry entries by OLD_PATH_PREFIX and optional subdir."""
    raw_entries = data.get("entries", [])
    result: list[MigrationEntry] = []
    for e in raw_entries:
        old_path = e.get("old_path", "")
        if not old_path.startswith(OLD_PATH_PREFIX):
            continue
        if e.get("status") != "pending":
            continue
        entry_subdir = e.get("subdir", "")
        if subdir and entry_subdir != subdir:
            continue
        result.append(MigrationEntry(
            old_module=e["old_module"],
            new_module=e["new_module"],
            old_path=e["old_path"],
            new_path=e["new_path"],
            subdir=entry_subdir,
            status=e.get("status", "pending"),
            classification_method=e.get("classification_method", "module_frontmatter"),
        ))
    return result


# ---------------------------------------------------------------------------
# move_file: cut-paste via shutil.move (mirrors dm314 L200-257)
# ---------------------------------------------------------------------------

def move_file(old_path: str, new_path: str, dry_run: bool = False,
              force: bool = False) -> dict:
    """Move file from old_path to new_path. Returns status dict."""
    source = REPO_ROOT / old_path
    target = REPO_ROOT / new_path

    if not source.exists():
        return {"old": old_path, "new": new_path, "status": "failed",
                "reason": "source_missing"}
    if not source.is_file():
        return {"old": old_path, "new": new_path, "status": "skipped",
                "reason": "not_a_file"}

    if target.exists():
        if source.resolve() == target.resolve():
            return {"old": old_path, "new": new_path, "status": "skipped",
                    "reason": "same_path"}
        try:
            if target.stat().st_size == source.stat().st_size and \
               target.read_bytes() == source.read_bytes():
                if source.resolve() != target.resolve():
                    if not dry_run:
                        source.unlink()
                    return {"old": old_path, "new": new_path, "status": "skipped",
                            "reason": "already_exists_same_content_source_removed"}
                return {"old": old_path, "new": new_path, "status": "skipped",
                        "reason": "already_exists_same_content"}
        except OSError:
            pass
        if force:
            if dry_run:
                return {"old": old_path, "new": new_path, "status": "would_overwrite",
                        "reason": "target_exists_different_content"}
            try:
                shutil.move(str(source), str(target))
                return {"old": old_path, "new": new_path, "status": "overwritten",
                        "reason": ""}
            except OSError as e:
                return {"old": old_path, "new": new_path, "status": "failed",
                        "reason": str(e)}
        return {"old": old_path, "new": new_path, "status": "failed",
                "reason": "target_exists_different_content"}

    if dry_run:
        return {"old": old_path, "new": new_path, "status": "would_move",
                "reason": ""}

    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        shutil.move(str(source), str(target))
        return {"old": old_path, "new": new_path, "status": "moved", "reason": ""}
    except OSError as e:
        return {"old": old_path, "new": new_path, "status": "failed",
                "reason": str(e)}


# ---------------------------------------------------------------------------
# update_blueprint_header: re.sub [BLUEPRINT] path (mirrors dm314 L299-359)
# NOTE: [MODULE] header is handled by ast_import_rewriter.rewrite_file, so this
# function ONLY updates [BLUEPRINT] path references.
# ---------------------------------------------------------------------------

def update_blueprint_header(new_path: str, subdir: str,
                            dry_run: bool = False,
                            old_path: str = "") -> dict:
    """Update [BLUEPRINT] path references in moved file's frontmatter.

    In dry-run mode, if new_path does not exist (file not yet moved), falls
    back to analyzing old_path to report whether an update would occur.
    """
    full_path = REPO_ROOT / new_path
    if not full_path.exists() or not full_path.is_file():
        if dry_run and old_path:
            # File not yet moved; analyze source to predict if update needed
            src = REPO_ROOT / old_path
            if src.exists() and src.is_file():
                return {"file": new_path, "status": "would_update", "changes": 1}
        return {"file": new_path, "status": "missing", "changes": 0}

    try:
        content = full_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        return {"file": new_path, "status": "read_error", "reason": str(e),
                "changes": 0}

    original = content
    # Update [BLUEPRINT] path: src/zephyr/governance/<file> -> src/zephyr/governance/<subdir>/<file>
    # Only replace in the first 5 lines (frontmatter) to avoid false matches in body.
    lines = content.split("\n")
    changed = False
    for i, line in enumerate(lines[:5]):
        if line.startswith("# [BLUEPRINT]"):
            # Replace OLD_PATH_PREFIX + bare filename with OLD_PATH_PREFIX + subdir + "/"
            # Pattern: src/zephyr/governance/  ->  src/zephyr/governance/<subdir>/
            # But only if not already containing subdir (idempotency).
            old_pattern = OLD_PATH_PREFIX
            new_pattern = f"{OLD_PATH_PREFIX}{subdir}/"
            if old_pattern in line and new_pattern not in line:
                lines[i] = line.replace(old_pattern, new_pattern, 1)
                changed = True
            break

    if not changed:
        return {"file": new_path, "status": "no_change", "changes": 0}

    content = "\n".join(lines)
    if content == original:
        return {"file": new_path, "status": "no_change", "changes": 0}

    if dry_run:
        return {"file": new_path, "status": "would_update", "changes": 1}

    tmp_path = f"{full_path}.{os.getpid()}.tmp"
    try:
        Path(tmp_path).write_text(content, encoding="utf-8")
        os.replace(tmp_path, full_path)
        return {"file": new_path, "status": "updated", "changes": 1}
    except PermissionError:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
        return {"file": new_path, "status": "write_error", "changes": 0}


# ---------------------------------------------------------------------------
# rewrite_imports_project: delegate to ast_import_rewriter.ImportRewriter
# Scans whole project: updates both moved files' [MODULE] header and
# consumers' import statements (ImportFrom / Import).
# ---------------------------------------------------------------------------

def rewrite_imports_project(entries: list[MigrationEntry],
                            dry_run: bool = False,
                            quiet: bool = False) -> dict:
    """Rewrite imports across whole project using ast_import_rewriter.

    Returns dict with keys: files_modified, total_replacements, results.
    """
    if not entries:
        return {"files_modified": 0, "total_replacements": 0, "results": []}

    moves = [e.to_move_entry() for e in entries]
    rewriter = ImportRewriter(moves)
    results = rewriter.rewrite_project(REPO_ROOT, dry_run=dry_run)
    total_changes = sum(len(r.changes) for r in results)
    if not quiet:
        mode = "DRY-RUN" if dry_run else "APPLIED"
        print(f"  [{mode}] {len(results)} files modified, "
              f"{total_changes} replacements")
    return {
        "files_modified": len(results),
        "total_replacements": total_changes,
        "results": results,
    }


# ---------------------------------------------------------------------------
# update_registry_status: mark entries as done (mirrors dm314 L517-534)
# ---------------------------------------------------------------------------

def update_registry_status(entries: list[MigrationEntry],
                           dry_run: bool = False) -> int:
    """Mark given entries as status=done in registry."""
    if dry_run:
        print(f"  Would update {len(entries)} entries to status: done")
        return 0

    data = load_registry()
    all_entries = data.get("entries", [])
    old_paths_to_mark = {e.old_path for e in entries}

    count = 0
    for e in all_entries:
        if e.get("old_path", "") in old_paths_to_mark and \
           e.get("status") == "pending":
            e["status"] = "done"
            count += 1

    save_registry(data)
    print(f"  Updated {count} entries to status: done")
    return 0


# ---------------------------------------------------------------------------
# Batch executors (ThreadPoolExecutor, mirrors dm314 L439-514)
# ---------------------------------------------------------------------------

def execute_move_batch(entries: list[MigrationEntry],
                       dry_run: bool = False,
                       force: bool = False) -> tuple[int, int, int]:
    """Execute moves in parallel. Returns (success, failed, skipped)."""
    success = 0
    failed = 0
    skipped = 0
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {}
        for e in entries:
            futures[executor.submit(
                move_file, e.old_path, e.new_path, dry_run, force
            )] = e
        for future in as_completed(futures):
            result = future.result()
            st = result["status"]
            if st in ("moved", "would_move", "overwritten", "would_overwrite"):
                success += 1
            elif st == "skipped":
                skipped += 1
            else:
                failed += 1
                print(f"  FAILED: {result['old']} -> {result.get('reason', '')}")
    return success, failed, skipped


def execute_header_updates(entries: list[MigrationEntry],
                           dry_run: bool = False) -> tuple[int, int]:
    """Execute [BLUEPRINT] header updates in parallel. Returns (updated, errors)."""
    updated = 0
    errors = 0
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {}
        for e in entries:
            futures[executor.submit(
                update_blueprint_header, e.new_path, e.subdir, dry_run,
                e.old_path
            )] = e
        for future in as_completed(futures):
            result = future.result()
            if result["status"] in ("updated", "would_update"):
                updated += 1
            elif result["status"] == "no_change":
                pass
            else:
                errors += 1
    return updated, errors


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="ARCH-031: governance/ root split migration orchestrator "
                    "(delegates import rewrite to ast_import_rewriter)"
    )
    parser.add_argument("--dry-run", action="store_true",
                        help="Dry run - report changes, do not modify files")
    parser.add_argument("--batch", type=str,
                        help="Process single subdir batch (e.g., escalation, budget)")
    parser.add_argument("--all", action="store_true",
                        help="Process all pending entries (all subdirs)")
    parser.add_argument("--move", action="store_true",
                        help="Execute file moves (shutil.move, cut-paste)")
    parser.add_argument("--rewrite-imports", action="store_true",
                        help="Rewrite imports across whole project via "
                             "ast_import_rewriter (also updates [MODULE] header)")
    parser.add_argument("--update-headers", action="store_true",
                        help="Update [BLUEPRINT] path in moved files' frontmatter "
                             "([MODULE] handled by --rewrite-imports)")
    parser.add_argument("--fix-external-refs", action="store_true",
                        help="Fix external references across whole project "
                             "(equivalent to --rewrite-imports; kept for "
                             "task-card CLI parity)")
    parser.add_argument("--update-registry-status", action="store_true",
                        help="Mark entries as done in migration_registry.yaml")
    parser.add_argument("--force", action="store_true",
                        help="Force overwrite if target exists with different content")
    parser.add_argument("--quiet", action="store_true",
                        help="Suppress per-file progress output")
    args = parser.parse_args(argv)

    # --fix-external-refs is an alias for --rewrite-imports
    do_rewrite = args.rewrite_imports or args.fix_external_refs

    if not args.batch and not args.all and not do_rewrite:
        parser.error("Specify --batch <subdir>, --all, or --fix-external-refs")

    need_registry = (args.move or args.rewrite_imports or
                     args.update_headers or args.update_registry_status)

    entries: list[MigrationEntry] = []
    if need_registry:
        data = load_registry()
        entries = get_entries(data, subdir=args.batch if args.batch else None)

    subdirs_found = sorted({e.subdir for e in entries if e.subdir})

    print("=== ARCH-031: governance/ Root Split Migration ===")
    print(f"Entries: {len(entries)}")
    if subdirs_found:
        print(f"Subdirectories: {', '.join(subdirs_found)}")
    if args.dry_run:
        print("(dry-run mode)")

    # --- --move ---
    if args.move:
        print("\n--- Moving files (cut-paste) ---")
        success, failed, skipped = execute_move_batch(
            entries, args.dry_run, args.force
        )
        print(f"  Moved: {success}, Failed: {failed}, Skipped: {skipped}")
        if failed > 0:
            return 1

    # --- --rewrite-imports / --fix-external-refs ---
    if do_rewrite:
        print("\n--- Rewriting imports (ast_import_rewriter) ---")
        result = rewrite_imports_project(entries, dry_run=args.dry_run,
                                         quiet=args.quiet)
        if result["files_modified"] == 0 and entries:
            print("  (no imports needed rewriting — may indicate already done)")

    # --- --update-headers ([BLUEPRINT] only; [MODULE] by ast_import_rewriter) ---
    if args.update_headers:
        print("\n--- Updating [BLUEPRINT] headers ---")
        updated, errors = execute_header_updates(entries, args.dry_run)
        print(f"  Updated: {updated}, Errors: {errors}")
        if errors > 0:
            return 1

    # --- --update-registry-status ---
    if args.update_registry_status:
        print("\n--- Updating registry status ---")
        update_registry_status(entries, args.dry_run)

    if not (args.move or do_rewrite or args.update_headers or
            args.update_registry_status):
        print("\nNo action specified. Use --move, --rewrite-imports, "
              "--update-headers, --fix-external-refs, or --update-registry-status")

    print("\nDone.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
