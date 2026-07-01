#!/usr/bin/env python3
# [BLUEPRINT] MOD-INF-005 | scripts/ops/upgrade_headers_to_14fields.py | §
# [MODULE] scripts.ops.upgrade_headers_to_14fields
# [DOMAIN] D_GOVERNANCE
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
# [TTL] task_bound
"""
Upgrade A_full file headers to 14 fields per TRAE-047 v1.1.0.

Handles three input cases:
  1. Existing 10-field canonical header → upgrade to 14-field (add DOMAIN/DEPENDENCIES/STARTUP/MATURITY)
  2. Only [A_module] old format → replace with 14-field header (parse A_module for stability/safety/ai_autonomy)
  3. No header at all → insert full 14-field header at top (after shebang if present)

New fields (sourced from depgraph):
  [DOMAIN]       — nodes.domain_id
  [DEPENDENCIES] — edges table (from_node_id → to_node_id paths)
  [CONSUMERS]    — edges table (reverse: who imports this file)
  [STARTUP]      — inferred (imported default; manual if __main__ block)
  [MATURITY]     — nodes.design_maturity
  [BLUEPRINT]    — nodes.blueprint_id + blueprint_registry.yaml path lookup

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
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# 一次性 bootstrap：定位 scripts/governance/ 以 import _shared.constants（SSoT 真源）。
# 先例：scripts/governance/_shared/constants.py、scripts/git_commit.py 均已 bootstrap。
_GOV_DIR = str(Path(__file__).resolve().parent.parent / "governance")  # scripts/ops/ -> scripts/governance/
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

# REPO_ROOT 真源为 zephyr.shared.io.paths（project_memory 钦定唯一真源）。
from zephyr.shared.io.paths import REPO_ROOT  # noqa: E402
from zephyr.shared.io.yaml_utils import load_vocabulary_values  # noqa: E402
from _shared.frontmatter import PY_HEADER_PATTERN  # noqa: E402
from _shared.constants import get_depgraph_pg_connection  # noqa: E402

# PROJECT_ROOT 作为 REPO_ROOT 的向后兼容别名，供本文件现有代码引用（最小改动）。
PROJECT_ROOT = REPO_ROOT
# 治本（2026-06-27）：删除 DB_PATH = .../depgraph.db 常量（路径污染源）。
# P2 迁移后 depgraph 已迁至 PostgreSQL，连接入口 get_depgraph_pg_connection()，无文件路径概念。

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

# Required fields per verify_header_completeness.py (12 of 14; ERROR_CONTRACT and TESTS are optional)
REQUIRED_FIELDS_SET = {
    "BLUEPRINT", "MODULE", "DOMAIN", "DEPENDENCIES",
    "CONSUMERS", "STARTUP", "MATURITY",
    "INVARIANTS", "MODIFY-GUARD",
    "STABILITY", "SAFETY", "AI_AUTONOMY",
}

# Fields that are new in v1.1.0 (were absent in v1.0.x 10-field format)
NEW_FIELDS = {"DOMAIN", "DEPENDENCIES", "STARTUP", "MATURITY"}

# Valid enum values 动态加载自 vocabulary YAML（SSoT 唯一真源，禁止硬编码——红蓝发现3 治本）
# 原硬编码含废弃值 scheduled 漏网（GATE-VOCAB 检测模式不覆盖 STARTUP 后缀），现改为动态加载
VALID_STARTUP = load_vocabulary_values("startup_vocabulary.yaml")
VALID_MATURITY = load_vocabulary_values("maturity_vocabulary.yaml")

MAIN_BLOCK_PATTERN = re.compile(r'^if\s+__name__\s*==\s*["\']__main__["\']\s*:', re.MULTILINE)
A_MODULE_PATTERN = re.compile(
    r"^#\s*\[A_module\]\s*module_id=([^|]+?)\s*\|.*?stability=(\w+).*?safety=(\w+).*?ai_autonomy=(\w+)"
)

# Fallback directory-to-blueprint mapping for files without depgraph nodes
# (proxy modules and other unmapped files)
DIR_TO_BLUEPRINT_FALLBACK = {
    "src/zephyr/governance": ("MOD-GOVERNANCE", "docs/03_modules/_domain-governance/blueprint.md"),
    "src/zephyr/integration": ("MOD-L13-001", "docs/03_modules/integration/experiment-core/blueprint.md"),
    "src/zephyr/ops": ("MOD-INF-027", "docs/03_modules/_cross_layer/shared-core/blueprint.md"),
    "src/zephyr/shared": ("MOD-INF-016", "docs/03_modules/_cross_layer/shared-core/blueprint.md"),
    "src/zephyr/data": ("MOD-L00-001", "docs/03_modules/data/datasource-core/blueprint.md"),
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
    "_archive",
}
EXEMPT_FILES = {"__init__.py", "conftest.py"}


def load_blueprint_registry() -> dict[str, str]:
    """Load blueprint_registry.yaml and return module_id -> blueprint_path mapping."""
    import yaml

    registry_path = PROJECT_ROOT / "docs" / "03_modules" / "blueprint_registry.yaml"
    if not registry_path.exists():
        return {}
    try:
        with open(registry_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except Exception:
        return {}
    mapping: dict[str, str] = {}
    for bp in data.get("blueprints", []):
        mid = bp.get("module_id", "")
        fp = bp.get("file_path", "")
        if mid and fp:
            full_path = f"docs/03_modules/{fp}"
            mapping[mid] = full_path
    return mapping


def find_blueprint_fallback(rel_path: str) -> tuple[str, str]:
    """Find blueprint_id and path from directory prefix (fallback for unmapped files)."""
    parts = rel_path.replace("\\", "/").split("/")
    for i in range(min(len(parts), 4), 0, -1):
        prefix = "/".join(parts[:i])
        if prefix in DIR_TO_BLUEPRINT_FALLBACK:
            return DIR_TO_BLUEPRINT_FALLBACK[prefix]
    return ("", "")


@dataclass
class NodeInfo:
    node_id: str = ""
    domain_id: str = ""
    design_maturity: str = ""
    change_policy: str = ""
    impact_level: str = ""
    modification_permission: str = ""
    blueprint_id: str = ""
    belongs_to: str = ""


@dataclass
class UpgradeResult:
    path: str
    status: str  # UPGRADED | SKIPPED_14FIELD | SKIPPED_NO_HEADER | SKIPPED_EXEMPT | ERROR
    detail: str = ""
    matched_node: bool = False
    new_fields_added: list = field(default_factory=list)


class DepgraphLoader:
    """Load node info and edges from depgraph (PostgreSQL) into memory lookups.

    治本（2026-06-27）：删除 db_path 实例属性（路径污染源，P2 PG 迁移后无文件路径概念）。
    """

    def __init__(self, db_path: Path | None = None) -> None:
        # db_path 参数保留仅为向后兼容签名，PG 模式下不使用。
        self.nodes_by_path: dict[str, NodeInfo] = {}
        self.node_id_to_path: dict[str, str] = {}
        self.edges_from: dict[str, list[str]] = {}  # from_node_id -> [to_path, ...]
        self.consumers_of: dict[str, list[str]] = {}  # to_node_id -> [from_path, ...]
        self._load()

    def _load(self) -> None:
        # P2迁移后：depgraph 已迁移到 PostgreSQL，不再依赖文件路径存在性检查。
        conn = get_depgraph_pg_connection(autocommit=True)
        try:
            # Load nodes
            cursor = conn.execute(
                "SELECT node_id, path, domain_id, design_maturity, "
                "change_policy, impact_level, modification_permission, "
                "blueprint_id, belongs_to "
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
                    blueprint_id=row["blueprint_id"] or "",
                    belongs_to=row["belongs_to"] or "",
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
                from_path = self.node_id_to_path.get(from_id, from_id)
                self.edges_from.setdefault(from_id, []).append(to_path)
                self.consumers_of.setdefault(to_id, []).append(from_path)
        finally:
            conn.close()

        print(
            f"[DEPGRAPH] Loaded {len(self.nodes_by_path)} nodes, "
            f"{sum(len(v) for v in self.edges_from.values())} edges"
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

    def get_consumers(self, node_id: str) -> list[str]:
        """Return list of consumer module paths (files that import this node)."""
        if not node_id:
            return []
        consumers = self.consumers_of.get(node_id, [])
        short = []
        for c in consumers:
            if c.endswith(".py"):
                c = c[:-3]
            c = c.replace("src/zephyr/", "zephyr.").replace("scripts/", "scripts.")
            c = c.replace("/", ".")
            short.append(c)
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
        m = PY_HEADER_PATTERN.match(stripped)
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


def parse_a_module(lines: list[str]) -> dict[str, str]:
    """Extract fields from [A_module] line if present.

    Returns dict with keys: module_id, stability, safety, ai_autonomy (or empty dict).
    """
    for line in lines[:30]:
        m = A_MODULE_PATTERN.match(line.rstrip("\n"))
        if m:
            return {
                "module_id": m.group(1).strip(),
                "stability": m.group(2).strip(),
                "safety": m.group(3).strip(),
                "ai_autonomy": m.group(4).strip(),
            }
    return {}


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


def _derive_module_path(filepath: Path) -> str:
    """Derive dotted module path from file path."""
    rel = str(filepath.relative_to(PROJECT_ROOT)).replace("\\", "/")
    if rel.endswith(".py"):
        rel = rel[:-3]
    # Strip 'src/' prefix for src/zephyr/ files → zephyr.xxx (not src.zephyr.xxx)
    if rel.startswith("src/zephyr/"):
        rel = rel[5:]  # remove "src/"
    return rel.replace("/", ".")


def build_header_block(
    fields: dict[str, str], node: NodeInfo | None, deps: list[str],
    consumers: list[str], a_module: dict[str, str], filepath: Path, content: str,
    blueprint_registry: dict[str, str],
) -> dict[str, str]:
    """Build canonical 14-field values, filling defaults from depgraph or conventions.

    Returns an ordered dict of FIELD -> value (value may be empty string).
    """
    # --- [BLUEPRINT] ---
    blueprint_val = fields.get("BLUEPRINT", "")
    if not blueprint_val:
        bp_id = ""
        bp_path = ""
        if node and node.blueprint_id:
            bp_id = node.blueprint_id
            bp_path = blueprint_registry.get(bp_id, "")
        if not bp_id:
            # Fallback to directory-based lookup
            rel = str(filepath.relative_to(PROJECT_ROOT)).replace("\\", "/")
            fb_id, fb_path = find_blueprint_fallback(rel)
            bp_id = fb_id
            bp_path = fb_path
        if bp_id and bp_path:
            blueprint_val = f"{bp_id} | {bp_path}"
        elif bp_id:
            blueprint_val = bp_id
        elif a_module.get("module_id"):
            blueprint_val = a_module["module_id"]

    # --- [DOMAIN] ---
    domain_val = fields.get("DOMAIN", "")
    if not domain_val and node and node.domain_id:
        domain_val = node.domain_id

    # --- [DEPENDENCIES] ---
    deps_val = fields.get("DEPENDENCIES", "")
    if not deps_val:
        deps_val = "; ".join(deps) if deps else ""

    # --- [CONSUMERS] ---
    consumers_val = fields.get("CONSUMERS", "")
    if not consumers_val:
        consumers_val = "; ".join(consumers) if consumers else ""

    # --- [STARTUP] ---
    startup_val = fields.get("STARTUP", "")
    if not startup_val or startup_val not in VALID_STARTUP:
        startup_val = infer_startup(filepath, content)

    # --- [MATURITY] ---
    maturity_val = fields.get("MATURITY", "")
    if not maturity_val or maturity_val not in VALID_MATURITY:
        if node and node.design_maturity in VALID_MATURITY:
            maturity_val = node.design_maturity
        else:
            maturity_val = "production"

    # --- [MODULE] ---
    module_val = fields.get("MODULE", "")
    if not module_val:
        module_val = _derive_module_path(filepath)

    # --- [STABILITY] ---
    stability_val = fields.get("STABILITY", "")
    if not stability_val:
        # Prefer [A_module] value, then depgraph, then default
        if a_module.get("stability"):
            stability_val = a_module["stability"]
        elif node and node.change_policy:
            stability_val = node.change_policy
        else:
            stability_val = "evolving"

    # --- [SAFETY] ---
    safety_val = fields.get("SAFETY", "")
    if not safety_val:
        if a_module.get("safety"):
            safety_val = a_module["safety"]
        elif node and node.impact_level:
            safety_val = node.impact_level
        else:
            safety_val = "L"

    # --- [AI_AUTONOMY] ---
    autonomy_val = fields.get("AI_AUTONOMY", "")
    if not autonomy_val:
        if a_module.get("ai_autonomy"):
            autonomy_val = a_module["ai_autonomy"]
        elif node and node.modification_permission:
            autonomy_val = node.modification_permission
        else:
            autonomy_val = "ai_modifiable"

    # Assemble ordered values
    return {
        "BLUEPRINT": blueprint_val,
        "MODULE": module_val,
        "DOMAIN": domain_val,
        "DEPENDENCIES": deps_val,
        "CONSUMERS": consumers_val,
        "STARTUP": startup_val,
        "MATURITY": maturity_val,
        "INVARIANTS": fields.get("INVARIANTS", ""),
        "MODIFY-GUARD": fields.get("MODIFY-GUARD", ""),
        "STABILITY": stability_val,
        "SAFETY": safety_val,
        "AI_AUTONOMY": autonomy_val,
        "ERROR_CONTRACT": fields.get("ERROR_CONTRACT", ""),
        "TESTS": fields.get("TESTS", ""),
    }


def render_header(values: dict[str, str]) -> str:
    """Render ordered field values into comment-line header block."""
    lines = []
    for fname in CANONICAL_FIELDS:
        val = values.get(fname, "")
        if val:
            lines.append(f"# [{fname}] {val}")
        else:
            lines.append(f"# [{fname}]")
    return "\n".join(lines) + "\n"


# Global blueprint registry (loaded once in main, read-only during parallel processing)
_BLUEPRINT_REGISTRY: dict[str, str] = {}


def upgrade_file(filepath: Path, loader: DepgraphLoader, dry_run: bool) -> UpgradeResult:
    """Upgrade a single file's header to 14 fields.

    Handles three cases:
    1. Has canonical header fields → rebuild to 14-field (existing behavior)
    2. Only has [A_module] → replace [A_module] with 14-field header
    3. No header at all → insert 14-field header at top (after shebang)
    """
    rel = str(filepath.relative_to(PROJECT_ROOT)).replace("\\", "/")

    # Skip exempt files
    if filepath.name in EXEMPT_FILES:
        return UpgradeResult(path=rel, status="SKIPPED_EXEMPT")

    try:
        # utf-8-sig：读取时自动剥离行首 UTF-8 BOM (\ufeff)，避免 BOM 导致
        # PY_HEADER_PATTERN 的 ^# 锚点失配（Bug 1：BOM 使 14 字段文件被误判需升级）
        with open(filepath, encoding="utf-8-sig") as f:
            content = f.read()
    except Exception as e:
        return UpgradeResult(path=rel, status="ERROR", detail=str(e))

    # 豁免 codegen 自动生成文件（BEGIN CODGEN 标记）——
    # 这些文件由 generate_contracts.py 从 cross_layer_contracts.yaml 重新生成，
    # 手动添加的 14 字段头部会在下次 codegen 时被覆盖，故跳过（Bug 2）。
    # codegen 模板本身已补 14 字段头部（见维护项5），无需本脚本介入。
    if "BEGIN CODGEN" in content:
        return UpgradeResult(
            path=rel, status="SKIPPED_EXEMPT", detail="codegen file (BEGIN CODGEN)"
        )

    lines = content.splitlines(keepends=True)
    fields, header_lines, extra_lines = parse_header(lines)
    a_module = parse_a_module(lines)

    # Skip files that already have all 12 required fields (already complete per verify_header_completeness.py)
    if REQUIRED_FIELDS_SET.issubset(set(fields.keys())):
        return UpgradeResult(path=rel, status="SKIPPED_14FIELD", detail="already has all required fields")

    # Get depgraph node info
    node = loader.get_node(rel)
    deps = loader.get_dependencies(node.node_id) if node else []
    consumers = loader.get_consumers(node.node_id) if node else []

    # Build new header (always rebuild to canonical 14-field with defaults filled)
    values = build_header_block(
        fields, node, deps, consumers, a_module, filepath, content, _BLUEPRINT_REGISTRY
    )
    new_header = render_header(values)

    if header_lines:
        # Case 1: Has canonical header fields → replace header region
        # Preserve extra (non-standard) fields after canonical block
        if extra_lines:
            extra_str = "\n".join(raw for _, raw in extra_lines)
            new_header = new_header.rstrip("\n") + "\n" + extra_str + "\n"

        start, end = find_header_region(lines, header_lines, extra_lines)
        if start < 0:
            return UpgradeResult(path=rel, status="ERROR", detail="cannot locate header region")

        before = "".join(lines[:start])
        after = "".join(lines[end + 1 :])
        new_content = before + new_header + after

    elif a_module:
        # Case 2: Only has [A_module] → replace [A_module] line(s) with 14-field header
        # Find the [A_module] line index
        a_module_indices = [idx for idx, raw in extra_lines if "[A_module]" in raw]
        if a_module_indices:
            start = min(a_module_indices)
            end = max(a_module_indices)
            before = "".join(lines[:start])
            after = "".join(lines[end + 1 :])
            new_content = before + new_header + after
        else:
            new_content = new_header + content

    else:
        # Case 3: No header at all → insert at top (after shebang if present)
        if content.startswith("#!"):
            shebang_end = content.index("\n") + 1
            new_content = content[:shebang_end] + new_header + content[shebang_end:]
        else:
            new_content = new_header + content

    # Idempotent: skip if no change needed
    if new_content == content:
        return UpgradeResult(path=rel, status="SKIPPED_14FIELD", detail="already canonical")

    # Determine which new fields were added (for reporting)
    missing_new = NEW_FIELDS - set(fields.keys())
    if not missing_new:
        missing_new = sorted(NEW_FIELDS)

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
    parser = argparse.ArgumentParser(description="Upgrade A_full headers to 14 fields (TRAE-047 v1.1.0)")
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

    # Load blueprint registry (global, read-only during parallel processing)
    global _BLUEPRINT_REGISTRY
    _BLUEPRINT_REGISTRY = load_blueprint_registry()
    print(f"[UPGRADE] loaded {len(_BLUEPRINT_REGISTRY)} blueprint paths from registry")

    # Load depgraph data
    loader = DepgraphLoader()

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
    skipped_ex = [r for r in results if r.status == "SKIPPED_EXEMPT"]
    errors = [r for r in results if r.status == "ERROR"]

    matched = sum(1 for r in upgraded if r.matched_node)
    unmatched = len(upgraded) - matched

    print("\n" + "=" * 70)
    print("UPGRADE SUMMARY (→ 14-field)")
    print("=" * 70)
    print(f"Total files scanned:      {len(results)}")
    print(f"Upgraded:                 {len(upgraded)}")
    print(f"  matched depgraph node:  {matched}")
    print(f"  unmatched (defaults):   {unmatched}")
    print(f"Already 14-field:         {len(skipped_14)}")
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
