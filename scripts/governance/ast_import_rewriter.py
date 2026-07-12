# [BLUEPRINT] MOD-INF-GOV | scripts/governance/ | AST import rewriter for directory migration
# [MODULE] scripts.governance.ast_import_rewriter
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] stdlib.ast, stdlib.argparse, stdlib.pathlib
# [CONSUMERS] manual (governance directory migration)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] AST-precise import rewriting; idempotent; dry-run supported; no regex
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [A_config] module_id=SCRIPT-GOV-AST-REWRITER | layer=script | stability=stable | safety=H | ai_autonomy=ai_modifiable
# [TTL] permanent
"""AST-based import rewriter for governance directory migration.

Rewrites ``from zephyr.governance.foo import bar`` → ``from zephyr.governance.subdir.foo import bar``
and ``import zephyr.governance.foo`` → ``import zephyr.governance.subdir.foo``
using Python ``ast`` module for precise location (no regex on import lines).

Usage::

    python scripts/governance/ast_import_rewriter.py \\
        --map .runtime/governance_move_map.yaml --dry-run
    python scripts/governance/ast_import_rewriter.py \\
        --map .runtime/governance_move_map.yaml --apply

The YAML map format::

    moves:
      - old_module: zephyr.governance.foo
        new_module: zephyr.governance.subdir.foo
        old_path: src/zephyr/governance/foo.py
        new_path: src/zephyr/governance/subdir/foo.py
"""

from __future__ import annotations

import argparse
import ast
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parents[2]


@dataclass
class MoveEntry:
    """Single file move: old module path -> new module path."""
    old_module: str
    new_module: str
    old_path: str
    new_path: str


@dataclass
class Change:
    """One replacement in one file."""
    line: int
    col: int
    old_text: str
    new_text: str
    change_type: str  # "ImportFrom" | "Import" | "MODULE_HEADER"


@dataclass
class RewriteResult:
    """Result of rewriting one file."""
    file: str
    changes: list[Change] = field(default_factory=list)

    @property
    def modified(self) -> bool:
        return len(self.changes) > 0


class ImportRewriter:
    """Rewrite import statements based on a move map.

    Uses ``ast`` to locate import nodes precisely, then applies line-level
    string replacements to preserve formatting/comments.
    """

    def __init__(self, moves: list[MoveEntry]) -> None:
        self.moves = moves
        # exact map: old_module -> new_module
        self._exact: dict[str, str] = {m.old_module: m.new_module for m in moves}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def rewrite_file(self, filepath: Path, dry_run: bool = False) -> RewriteResult:
        """Rewrite imports in *filepath*. Returns ``RewriteResult``."""
        result = RewriteResult(file=str(filepath))
        try:
            content = filepath.read_text(encoding="utf-8")
        except Exception:
            return result

        try:
            tree = ast.parse(content)
        except SyntaxError:
            return result

        lines = content.splitlines(keepends=True)
        changes: list[Change] = []

        # --- Collect import-level changes via AST ---
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                new_mod = self._find_replacement(node.module)
                if new_mod:
                    old_seg = f"from {node.module}"
                    new_seg = f"from {new_mod}"
                    self._apply_line_replace(lines, node.lineno, old_seg, new_seg, "ImportFrom", changes)
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    new_name = self._find_replacement(alias.name)
                    if new_name:
                        old_seg = f"import {alias.name}"
                        new_seg = f"import {new_name}"
                        self._apply_line_replace(lines, node.lineno, old_seg, new_seg, "Import", changes)

        # --- Update header fields: [MODULE], [DEPENDENCIES], [CONSUMERS] ---
        # P1 fix (2026-07-13): previously only [MODULE] was rewritten, leaving
        # [DEPENDENCIES] / [CONSUMERS] module-path references stale after migration.
        for i, line in enumerate(lines[:20]):
            # [MODULE] zephyr.foo -> zephyr.new.foo
            m_mod = re.search(r'\[MODULE\]\s*(\S+)', line)
            if m_mod:
                old_mod = m_mod.group(1)
                new_mod = self._find_replacement(old_mod)
                if new_mod:
                    lines[i] = line.replace(old_mod, new_mod)
                    changes.append(Change(i + 1, 0, old_mod, new_mod, "MODULE_HEADER"))
                continue
            # [DEPENDENCIES] / [CONSUMERS]: semicolon-separated list;
            # rewrite items that start with zephyr.* (skip MOD-XXX(ref) entries)
            m_dep = re.search(r'\[(DEPENDENCIES|CONSUMERS)\]\s*(.*)', line)
            if m_dep:
                body = m_dep.group(2)
                items = body.split(';')
                new_items: list[str] = []
                modified = False
                for item in items:
                    stripped = item.strip()
                    if stripped.startswith('zephyr.'):
                        new_mod = self._find_replacement(stripped)
                        if new_mod:
                            lead = item[:len(item) - len(item.lstrip())]
                            new_items.append(lead + new_mod)
                            modified = True
                            continue
                    new_items.append(item)
                if modified:
                    new_body = ';'.join(new_items)
                    lines[i] = line.replace(body, new_body)
                    changes.append(Change(i + 1, 0, body, new_body, "HEADER_FIELD"))

        if not changes:
            return result

        result.changes = changes
        if not dry_run:
            filepath.write_text("".join(lines), encoding="utf-8")
        return result

    def scan_project(self, root: Path, exclude_dirs: set[str] | None = None) -> list[Path]:
        """Return all .py files under *root* that might reference moved modules."""
        import os
        if exclude_dirs is None:
            exclude_dirs = {".git", "__pycache__", ".venv", "site-packages", "node_modules", ".runtime", ".aidrafts", "metadata", "data"}
        py_files: list[Path] = []

        def _on_error(err):
            pass  # skip inaccessible dirs (e.g. Windows system protected)

        for dirpath, dirnames, filenames in os.walk(root, onerror=_on_error):
            # prune excluded dirs in-place for performance
            dirnames[:] = [d for d in dirnames if d not in exclude_dirs]
            for fname in filenames:
                if not fname.endswith(".py"):
                    continue
                py_files.append(Path(dirpath) / fname)
        return py_files

    def rewrite_project(self, root: Path, dry_run: bool = False,
                        progress_fn=None) -> list[RewriteResult]:
        """Rewrite all .py files under *root*."""
        py_files = self.scan_project(root)
        results: list[RewriteResult] = []
        for idx, f in enumerate(py_files):
            r = self.rewrite_file(f, dry_run=dry_run)
            if r.modified:
                results.append(r)
            if progress_fn:
                progress_fn(idx + 1, len(py_files))
        return results

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _find_replacement(self, module: str) -> Optional[str]:
        """Find replacement module path.

        Handles exact match and prefix match:
        - exact: ``zephyr.governance.foo`` → ``zephyr.governance.sub.foo``
        - prefix: ``zephyr.governance.foo.bar`` → ``zephyr.governance.sub.foo.bar``
        """
        # Idempotency guard: already a new module
        if module in self._exact.values():
            return None
        # Exact match
        if module in self._exact:
            return self._exact[module]
        # Prefix match
        for old, new in self._exact.items():
            if module.startswith(old + "."):
                suffix = module[len(old):]
                return new + suffix
        return None

    @staticmethod
    def _apply_line_replace(lines: list[str], lineno: int,
                            old_seg: str, new_seg: str,
                            change_type: str,
                            changes: list[Change]) -> None:
        """Replace *old_seg* with *new_seg* on line *lineno* (1-based).

        Idempotent: if *old_seg* not found (already replaced), skip silently.
        """
        idx = lineno - 1
        if 0 <= idx < len(lines) and old_seg in lines[idx]:
            lines[idx] = lines[idx].replace(old_seg, new_seg)
            changes.append(Change(lineno, 0, old_seg, new_seg, change_type))


# ------------------------------------------------------------------
# YAML map loading
# ------------------------------------------------------------------

def load_move_map(yaml_path: Path) -> list[MoveEntry]:
    """Load move map from YAML. Uses PyYAML if available, else minimal parser."""
    moves: list[MoveEntry] = []
    try:
        import yaml
        data = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
        for entry in data.get("moves", []):
            moves.append(MoveEntry(
                old_module=entry["old_module"],
                new_module=entry["new_module"],
                old_path=entry["old_path"],
                new_path=entry["new_path"],
            ))
        return moves
    except ImportError:
        pass
    # Minimal fallback parser
    text = yaml_path.read_text(encoding="utf-8")
    current: dict[str, str] = {}
    for line in text.splitlines():
        line = line.rstrip()
        if line.strip().startswith("- "):
            if current:
                moves.append(MoveEntry(**current))
                current = {}
            line = line.strip()[2:]
        if ":" in line:
            k, v = line.split(":", 1)
            k = k.strip()
            v = v.strip().strip('"').strip("'")
            if k in ("old_module", "new_module", "old_path", "new_path"):
                current[k] = v
    if current:
        moves.append(MoveEntry(**current))
    return moves


# ------------------------------------------------------------------
# Reporting
# ------------------------------------------------------------------

def print_report(results: list[RewriteResult], dry_run: bool) -> None:
    """Print a human-readable impact report."""
    mode = "DRY-RUN (no files modified)" if dry_run else "APPLIED"
    total_changes = sum(len(r.changes) for r in results)
    print(f"\n{'=' * 60}")
    print(f"  AST Import Rewriter — {mode}")
    print(f"  Files with changes: {len(results)}")
    print(f"  Total replacements: {total_changes}")
    print(f"{'=' * 60}")
    for r in results:
        print(f"\n  {r.file}")
        for c in r.changes:
            print(f"    L{c.line} [{c.change_type}] {c.old_text} → {c.new_text}")


# ------------------------------------------------------------------
# CLI
# ------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="AST-based import rewriter for governance directory migration"
    )
    parser.add_argument("--map", required=True, type=Path,
                        help="Path to YAML move map file")
    parser.add_argument("--dry-run", action="store_true",
                        help="Only report changes, do not modify files")
    parser.add_argument("--apply", action="store_true",
                        help="Apply changes to files")
    parser.add_argument("--root", type=Path, default=REPO_ROOT,
                        help="Project root to scan (default: repo root)")
    parser.add_argument("--quiet", action="store_true",
                        help="Suppress per-file output")
    args = parser.parse_args(argv)

    if not args.dry_run and not args.apply:
        parser.error("Specify either --dry-run or --apply")

    if not args.map.exists():
        print(f"Error: map file not found: {args.map}", file=sys.stderr)
        return 1

    moves = load_move_map(args.map)
    if not moves:
        print("Error: no moves found in map file", file=sys.stderr)
        return 1

    rewriter = ImportRewriter(moves)

    def _progress(done: int, total: int) -> None:
        if not args.quiet and done % 200 == 0:
            print(f"  ... scanned {done}/{total} files", file=sys.stderr)

    results = rewriter.rewrite_project(args.root, dry_run=args.dry_run,
                                       progress_fn=_progress)

    if args.quiet:
        total = sum(len(r.changes) for r in results)
        print(f"{'DRY-RUN' if args.dry_run else 'APPLIED'}: {len(results)} files, {total} replacements")
    else:
        print_report(results, args.dry_run)

    return 0


if __name__ == "__main__":
    sys.exit(main())
