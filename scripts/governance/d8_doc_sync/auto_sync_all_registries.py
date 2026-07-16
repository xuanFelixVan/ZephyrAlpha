# [BLUEPRINT] MOD-INF-005 | scripts/governance/auto_sync_all_registries.py | §
# [MODULE] scripts.governance.auto_sync_all_registries
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
# [TTL] permanent
"""全自动注册表同步器
=====================================
扫描变更→更新所有相关注册表→零孤儿

RULE-TWO/RULE-FOUR/RULE-EIGHT 自动化执行器。
一人开发+AI 维护: 每次 session 结束前运行 --all。
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 全自动注册表同步器
dimensions:
- D1
priority: P2
timeout_seconds: 60
warn_only: false
"""


import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

import argparse
import ast
import logging
import os
import re
import sys
from pathlib import Path

from _shared.constants import EXIT_FINDINGS, EXIT_PASS, REPO_ROOT
from _shared.file_utils import atomic_write_safe  # noqa: E402  治本(ARCH-036 P1-1): 收敛本地 tmp+replace 样板→共享 SSoT

logger = logging.getLogger(__name__)

PROJECT_ROOT = REPO_ROOT

REGISTRIES = {
    "module": PROJECT_ROOT / "docs/03_modules/module-registry.yaml",
    "blueprint": PROJECT_ROOT / "docs/03_modules/blueprint_registry.yaml",
    "gate": PROJECT_ROOT / "src/zephyr/gov_enforcement/rule_enforcement/_registry.yaml",
    "cross_dep": PROJECT_ROOT
    / "docs/01_policies_and_standards/_registry/catalogs/cross-module-dependency-registry.yaml",
}

# ARCH-036: 路径修正 — 真实物理路径为 src/zephyr/feedback_loop/（下划线，已从 trading/ 迁出至顶层）；
# 旧路径 src/zephyr/feedback-loop/（短横线）从未存在，导致 _discover_fle_gates 静默返回空列表。
FLE_GATES_DIR = PROJECT_ROOT / "src" / "zephyr" / "feedback_loop" / "gates"
FLE_BLUEPRINT = PROJECT_ROOT / "docs" / "03_modules" / "_cross_layer" / "feedback_loop" / "blueprint.md"
FEEDBACK_LOOP_DIR = PROJECT_ROOT / "src" / "zephyr" / "feedback_loop"

FLE_GATE_CATEGORY = "fle_self_defense"
FLE_MODULE_ID = "MOD-FEEDBACK_LOOP"


def _load_yaml(path: Path) -> dict | None:
    """_load_yaml implementation."""
    try:
        import yaml

        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error("Failed to load YAML %s: %s", path, e)
        return None


def _save_yaml(path: Path, data: dict, dry_run: bool = False) -> bool:
    """_save_yaml implementation."""
    try:
        import yaml

        content = yaml.dump(data, allow_unicode=True, default_flow_style=False, sort_keys=False)
        if dry_run:
            logger.info("[DRY-RUN] Would write %d bytes to %s", len(content), path)
            return True
        if atomic_write_safe(path, content):
            logger.info("Written %s", path)
            return True
        logger.error("Failed to save YAML %s: atomic_write_safe returned False", path)
        return False
    except Exception as e:
        logger.error("Failed to save YAML %s: %s", path, e)
        return False


def _discover_fle_gates() -> list[dict]:
    """_discover_fle_gates implementation."""
    gates = []
    # ARCH-036: 静默失效修正 — 旧代码 if not exists: return 静默吞掉路径错误，
    # 改为打印 stderr 警告（与 audit_registration.py GATES_DIR 处理一致）。
    if not FLE_GATES_DIR.is_dir():
        print(f"[WARN] FLE_GATES_DIR not found: {FLE_GATES_DIR} — FLE gate discovery skipped", file=sys.stderr)
        return gates
    for py_file in sorted(FLE_GATES_DIR.glob("*.py")):
        if py_file.name == "__init__.py":
            continue
        stem = py_file.stem
        gate_id = f"FLE-{stem.upper().replace('_', '-')[:28]}"
        title = _read_class_docstring(py_file) or stem.replace("_", " ").title()
        gates.append(
            {
                "gate_id": gate_id,
                "gate_name": stem,
                "title": f"{gate_id} {title}",
                "category": FLE_GATE_CATEGORY,
                # ARCH-036: 相对路径基准为 _registry.yaml 所在的 rule_enforcement/，
                # 到 feedback_loop/gates/ 需上溯两级再进入 feedback_loop/。
                "file": f"../../feedback_loop/gates/{py_file.name}",
                "status": "active",
                "scope": "fle",
                "execution_plane": "warm",
                "note": f"Auto-registered by auto_sync_all_registries.py — FLE self-defense gate (physical: src/zephyr/feedback_loop/gates/{py_file.name})",
            }
        )
    return gates


def _read_class_docstring(py_file: Path) -> str | None:
    """_read_class_docstring implementation."""
    try:
        with open(py_file, encoding="utf-8") as f:
            tree = ast.parse(f.read())
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.ClassDef):
                doc = ast.get_docstring(node)
                if doc:
                    return doc.split("\n")[0].strip()
        doc = ast.get_docstring(tree)
        if doc:
            return doc.split("\n")[0].strip()
    except Exception:
        pass
    return None


def _extract_blueprint_version(blueprint_path: Path) -> str | None:
    """_extract_blueprint_version implementation."""
    if not blueprint_path.exists():
        return None
    try:
        with open(blueprint_path, encoding="utf-8") as f:
            content = f.read()
        m = re.search(r'^\s*version\s*:\s*"?([\d.]+)"?\s*$', content, re.MULTILINE)
        if m:
            return m.group(1)
        m = re.search(r'^\s*-\s*version\s*:\s*"?([\d.]+)"?\s*$', content, re.MULTILINE)
        if m:
            return m.group(1)
    except Exception:
        pass
    return None


def sync_fle_gates(dry_run: bool = False) -> int:
    """Synchronize target with source of truth."""
    logger.info("=== Syncing FLE gates to gate registry ===")
    gate_registry = _load_yaml(REGISTRIES["gate"])
    if not gate_registry:
        return EXIT_FINDINGS

    existing_ids = {g["gate_id"] for g in gate_registry.get("gates", [])}
    fle_gates = _discover_fle_gates()
    new_count = 0

    for fg in fle_gates:
        if fg["gate_id"] in existing_ids:
            logger.debug("Gate %s already registered, skipping", fg["gate_id"])
            continue
        gate_registry.setdefault("gates", []).append(fg)
        existing_ids.add(fg["gate_id"])
        new_count += 1

    if new_count == 0:
        logger.info("No new FLE gates to register")
        return EXIT_PASS

    gate_registry["last_updated"] = "2026-05-08"
    summary = gate_registry.setdefault("summary", {})
    summary["total"] = len(gate_registry["gates"])
    cats = summary.setdefault("by_category", {})
    cats[FLE_GATE_CATEGORY] = new_count + cats.get(FLE_GATE_CATEGORY, 0)
    stats = summary.setdefault("by_status", {})
    stats["active"] = stats.get("active", 0) + new_count

    if _save_yaml(REGISTRIES["gate"], gate_registry, dry_run):
        logger.info("Registered %d new FLE gates", new_count)
        return EXIT_PASS
    return EXIT_FINDINGS


def sync_versions(dry_run: bool = False) -> int:
    """Synchronize target with source of truth."""
    logger.info("=== Syncing blueprint/module versions ===")
    bp_version = _extract_blueprint_version(FLE_BLUEPRINT)
    if not bp_version:
        logger.warning("Could not extract version from %s", FLE_BLUEPRINT)
        return EXIT_FINDINGS

    errors = 0

    module_reg = _load_yaml(REGISTRIES["module"])
    if module_reg:
        for mod in module_reg.get("modules", []):
            if mod.get("module_id") == FLE_MODULE_ID:
                old = mod.get("blueprint", {}).get("version", "?")
                if old != bp_version:
                    mod.setdefault("blueprint", {})["version"] = bp_version
                    logger.info("module-registry: %s %s -> %s", FLE_MODULE_ID, old, bp_version)
                break
        module_reg["last_updated"] = "2026-05-08"
        if not _save_yaml(REGISTRIES["module"], module_reg, dry_run):
            errors += 1

    bp_reg = _load_yaml(REGISTRIES["blueprint"])
    if bp_reg:
        for bp in bp_reg.get("blueprints", []):
            if bp.get("module_id") == FLE_MODULE_ID:
                old = bp.get("version", "?")
                if old != bp_version:
                    bp["version"] = bp_version
                    logger.info("blueprint-registry: %s %s -> %s", FLE_MODULE_ID, old, bp_version)
                break
        bp_reg["registry"]["last_updated"] = "2026-05-08"
        if not _save_yaml(REGISTRIES["blueprint"], bp_reg, dry_run):
            errors += 1

    return errors


def _extract_dependencies(py_file: Path) -> list[dict]:
    """_extract_dependencies implementation."""
    deps = []
    try:
        with open(py_file, encoding="utf-8") as f:
            tree = ast.parse(f.read())
    except Exception:
        return deps

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                deps.append({"module": alias.name, "alias": alias.asname})
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                deps.append({"module": node.module, "level": node.level})

    return deps


def sync_dependencies(dry_run: bool = False) -> int:
    """Synchronize target with source of truth."""
    logger.info("=== Syncing cross-module dependencies ===")
    dep_registry = _load_yaml(REGISTRIES["cross_dep"])
    if not dep_registry:
        return EXIT_FINDINGS

    existing_sources = set()
    for d in dep_registry.get("dependencies", []):
        if d.get("source") == FLE_MODULE_ID:
            existing_sources.add(d.get("target", ""))

    scheduler_file = FEEDBACK_LOOP_DIR / "scheduler.py"
    if not scheduler_file.exists():
        logger.warning("scheduler.py not found")
        return EXIT_FINDINGS

    raw_deps = _extract_dependencies(scheduler_file)
    new_count = 0
    max_dep_id = 0
    for d in dep_registry.get("dependencies", []):
        try:
            num = int(d["dep_id"].replace("DEP-", ""))
            if num > max_dep_id:
                max_dep_id = num
        except (ValueError, KeyError):
            pass

    for dep in raw_deps:
        mod_name = dep["module"]
        if not mod_name.startswith("zephyr.feedback_loop"):
            continue
        target = mod_name.replace("zephyr.feedback_loop.", "").split(".")[0]
        target_id = f"fle-{target}"
        if target_id in existing_sources:
            continue

        max_dep_id += 1
        dep_entry = {
            "dep_id": f"DEP-{max_dep_id:03d}",
            "source": FLE_MODULE_ID,
            "source_name": "feedback-loop",
            "target": target_id,
            "target_name": target,
            "type": "runtime",
            "strength": "hard",
            "description": f"FLE scheduler imports from feedback-loop.{target}",
            "direction": "downstream",
            "valid_since": "2026-05-08",
        }
        dep_registry.setdefault("dependencies", []).append(dep_entry)
        existing_sources.add(target_id)
        new_count += 1

    dep_registry["last_updated"] = "2026-05-08"
    dep_registry["total_dependencies"] = len(dep_registry["dependencies"])
    summary = dep_registry.setdefault("summary", {})
    summary["total_dependencies"] = len(dep_registry["dependencies"])

    if new_count == 0:
        logger.info("No new dependencies to register")
        return EXIT_PASS

    if _save_yaml(REGISTRIES["cross_dep"], dep_registry, dry_run):
        logger.info("Registered %d new dependencies", new_count)
        return EXIT_PASS
    return EXIT_FINDINGS


def verify_init_all(dry_run: bool = False) -> int:
    """verify_init_all implementation."""
    logger.info("=== Verifying __init__.py __all__ completeness ===")
    errors = 0
    for pkg_dir in FEEDBACK_LOOP_DIR.iterdir():
        if not pkg_dir.is_dir() or pkg_dir.name.startswith("_") or pkg_dir.name.startswith("."):
            continue
        if pkg_dir.name in ("tests", "docs"):
            continue
        init_file = pkg_dir / "__init__.py"
        if not init_file.exists():
            logger.warning("Missing __init__.py in %s", pkg_dir)
            errors += 1
            continue

        py_files = {f.stem for f in pkg_dir.glob("*.py") if f.name != "__init__.py"}
        try:
            with open(init_file, encoding="utf-8") as f:
                tree = ast.parse(f.read())
        except Exception:
            logger.error("Failed to parse %s", init_file)
            errors += 1
            continue

        all_list = None
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "__all__":
                        if isinstance(node.value, ast.List):
                            all_list = [e.value for e in node.value.elts if isinstance(e, ast.Constant)]
                        elif isinstance(node.value, (ast.ListComp, ast.Tuple)):
                            pass

        if all_list is None:
            logger.warning("%s: no __all__ found", init_file)
            errors += 1
            continue

        missing = py_files - set(all_list)
        extra = set(all_list) - py_files
        if missing:
            logger.info("%s: missing from __all__: %s", pkg_dir.name, sorted(missing))
        if extra:
            logger.debug("%s: extra in __all__ (no file): %s", pkg_dir.name, sorted(extra))

    return 1 if errors else 0


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="Auto-sync all registries from source files")
    parser.add_argument("--sync-gates", action="store_true", help="Register FLE gates in gate registry")
    parser.add_argument("--sync-versions", action="store_true", help="Sync blueprint versions across registries")
    parser.add_argument("--sync-deps", action="store_true", help="Sync cross-module dependencies")
    parser.add_argument("--verify-all", action="store_true", help="Verify __init__.py __all__ completeness")
    parser.add_argument("--all", action="store_true", help="Run all sync operations")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing")
    parser.add_argument("--warn-only", action="store_true", help="Exit 0 even on errors")
    args = parser.parse_args()

    run_all = args.all
    if not any([args.sync_gates, args.sync_versions, args.sync_deps, args.verify_all, args.all]):
        parser.print_help()
        sys.exit(EXIT_PASS)

    total_errors = 0

    if run_all or args.sync_gates:
        total_errors += sync_fle_gates(dry_run=args.dry_run)
    if run_all or args.sync_versions:
        total_errors += sync_versions(dry_run=args.dry_run)
    if run_all or args.sync_deps:
        total_errors += sync_dependencies(dry_run=args.dry_run)
    if run_all or args.verify_all:
        total_errors += verify_init_all(dry_run=args.dry_run)

    if args.dry_run:
        logger.info("[DRY-RUN] Complete — %d errors would occur", total_errors)
    elif total_errors == 0:
        logger.info("All registries synced successfully")
    else:
        logger.warning("Completed with %d errors", total_errors)

    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(1 if total_errors else 0)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    main()
