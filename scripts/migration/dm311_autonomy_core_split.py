# [BLUEPRINT] MOD-INF-037 | docs/02_enterprise_architecture/phase_d_full_test_construction_plan.md | §DM-311
# [MODULE] scripts.migration.dm311_autonomy_core_split
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.migration.dm314_infra_ops_split
# [CONSUMERS] DM-311任务卡
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] 剪切粘贴模式(shutil.move); 从migration-registry.yaml读取映射; 按子目录分批; 移动后更新import+头部字段; 更新迁移登记表status; 全局更新外部引用
# [MODIFY-GUARD] migration-registry.yaml格式变更需同步
# [STABILITY] volatile
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] registry缺失->exit1; 源文件缺失->记录失败继续; 目标已存在->跳过
# [TESTS] tests/test_dm311_migration.py
# [TTL] task_bound
"""DM-311: autonomy_core/ 拆分迁移执行脚本。

剪切粘贴模式：shutil.move() 将文件从 autonomy_core/ 移动到各自设计域路径。
移动后原地更新 import 路径和头部 [BLUEPRINT]/[MODULE] 字段。
支持全局更新项目其他文件中的外部引用。

用法:
    python scripts/migration/dm311_autonomy_core_split.py --dry-run
    python scripts/migration/dm311_autonomy_core_split.py --subdir db --move
    python scripts/migration/dm311_autonomy_core_split.py --subdir db --update-imports
    python scripts/migration/dm311_autonomy_core_split.py --subdir db --update-headers
    python scripts/migration/dm311_autonomy_core_split.py --subdir db --fix-external-refs
    python scripts/migration/dm311_autonomy_core_split.py --all --move
    python scripts/migration/dm311_autonomy_core_split.py --update-registry-status --subdir db
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

# bootstrap: 定位 scripts/governance/ 以 import _shared.constants（REPO_ROOT SSoT 真源）
_GOV_DIR = str(Path(__file__).resolve().parent.parent / "governance")
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import REPO_ROOT as PROJECT_ROOT  # noqa: E402

REGISTRY_FILE = PROJECT_ROOT / "docs" / "02_enterprise_architecture" / "migration-registry.yaml"

OLD_PREFIX = "zephyr.autonomy_core."
OLD_PATH_PREFIX = "src/zephyr/autonomy_core/"

SUBDIR_TO_NEW_MODULE_PREFIX = {
    "agent-spec": "zephyr.orchestration.agent_lifecycle.",
    "autopilot": "zephyr.orchestration.runtime_core.",
    "behavioral-admission": "zephyr.orchestration.runtime_core.",
    "context-engine": "zephyr.orchestration.context_management.",
    "core_06": "zephyr.infrastructure.shared_services.",
    "db": "zephyr.data.persistence.",
    "feedback-loop": "zephyr.feedback_loop.",
    "gates": "zephyr.governance.rule_enforcement.",
    "orchestrator": "zephyr.orchestration.runtime_core.orchestrator.",
    "pipeline": "zephyr.orchestration.pipeline_routing.",
    "rollback": "zephyr.resilience.rollback.",
    "runtime": "zephyr.orchestration.runtime_core.",
}

CROSS_REFS = {
    "zephyr.orchestration.agent_lifecycle.": "zephyr.orchestration.agent_lifecycle.",
    "zephyr.orchestration.runtime_core.": "zephyr.orchestration.runtime_core.",
    "zephyr.orchestration.runtime_core.": "zephyr.orchestration.runtime_core.",
    "zephyr.orchestration.context_management.": "zephyr.orchestration.context_management.",
    "zephyr.infrastructure.shared_services.": "zephyr.infrastructure.shared_services.",
    "zephyr.infrastructure.shared_services.": "zephyr.infrastructure.shared_services.",
    "zephyr.data.persistence.": "zephyr.data.persistence.",
    "zephyr.feedback_loop.": "zephyr.feedback_loop.",
    "zephyr.governance.rule_enforcement.": "zephyr.governance.rule_enforcement.",
    "zephyr.orchestration.runtime_core.orchestrator.": "zephyr.orchestration.runtime_core.orchestrator.",
    "zephyr.orchestration.pipeline_routing.": "zephyr.orchestration.pipeline_routing.",
    "zephyr.resilience.rollback.": "zephyr.resilience.rollback.",
    "zephyr.orchestration.runtime_core.": "zephyr.orchestration.runtime_core.",
}

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
}

EXCLUDED_EXTENSIONS = {
    ".pyc",
    ".pyo",
    ".so",
    ".dll",
    ".exe",
    ".png",
    ".jpg",
    ".gif",
    ".ico",
    ".woff",
    ".woff2",
    ".ttf",
    ".eot",
    ".map",
}


def load_registry() -> dict:
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
        print("[ERROR] Invalid YAML structure", file=sys.stderr)
        sys.exit(2)
    return data


def save_registry(data: dict) -> None:
    import yaml

    content = yaml.dump(data, default_flow_style=False, allow_unicode=True, sort_keys=False)
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


def get_autonomy_core_entries(data: dict, subdir: str | None = None) -> list[dict]:
    entries = data.get("entries", [])
    filtered = []
    for e in entries:
        op = e.get("old_path", "")
        if not op.startswith(OLD_PATH_PREFIX):
            continue
        if e.get("status") != "pending":
            continue
        if subdir:
            if not op.startswith(f"{OLD_PATH_PREFIX}{subdir}/") and op != f"{OLD_PATH_PREFIX}{subdir}":
                continue
        filtered.append(e)
    return filtered


def determine_subdir(old_path: str) -> str:
    rel = old_path[len(OLD_PATH_PREFIX) :]
    parts = rel.split("/")
    return parts[0] if parts else ""


def move_file(old_path: str, new_path: str, dry_run: bool = False, force: bool = False) -> dict:
    source = PROJECT_ROOT / old_path
    target = PROJECT_ROOT / new_path

    if not source.exists():
        return {"old": old_path, "new": new_path, "status": "failed", "reason": "source_missing"}

    if not source.is_file():
        return {"old": old_path, "new": new_path, "status": "skipped", "reason": "not_a_file"}

    if target.exists():
        if source.resolve() == target.resolve():
            return {"old": old_path, "new": new_path, "status": "skipped", "reason": "same_path"}
        try:
            if target.stat().st_size == source.stat().st_size:
                if target.read_bytes() == source.read_bytes():
                    if source.resolve() != target.resolve():
                        if not dry_run:
                            source.unlink()
                        return {
                            "old": old_path,
                            "new": new_path,
                            "status": "skipped",
                            "reason": "already_exists_same_content_source_removed",
                        }
                    return {
                        "old": old_path,
                        "new": new_path,
                        "status": "skipped",
                        "reason": "already_exists_same_content",
                    }
        except OSError:
            pass
        if force:
            if dry_run:
                return {
                    "old": old_path,
                    "new": new_path,
                    "status": "would_overwrite",
                    "reason": "target_exists_different_content",
                }
            try:
                shutil.move(str(source), str(target))
                return {"old": old_path, "new": new_path, "status": "overwritten", "reason": ""}
            except OSError as e:
                return {"old": old_path, "new": new_path, "status": "failed", "reason": str(e)}
        return {"old": old_path, "new": new_path, "status": "failed", "reason": "target_exists_different_content"}

    if dry_run:
        return {"old": old_path, "new": new_path, "status": "would_move", "reason": ""}

    target.parent.mkdir(parents=True, exist_ok=True)

    try:
        shutil.move(str(source), str(target))
        return {"old": old_path, "new": new_path, "status": "moved", "reason": ""}
    except OSError as e:
        return {"old": old_path, "new": new_path, "status": "failed", "reason": str(e)}


def update_imports_in_file(new_path: str, subdir: str, dry_run: bool = False) -> dict:
    full_path = PROJECT_ROOT / new_path
    if not full_path.exists() or not full_path.is_file():
        return {"file": new_path, "status": "missing", "changes": 0}

    if subdir not in SUBDIR_TO_NEW_MODULE_PREFIX:
        return {"file": new_path, "status": "skipped", "reason": "no_mapping", "changes": 0}

    try:
        content = full_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        return {"file": new_path, "status": "read_error", "reason": str(e), "changes": 0}

    original = content
    for old_ref, new_ref in CROSS_REFS.items():
        content = content.replace(old_ref, new_ref)

    if content == original:
        return {"file": new_path, "status": "no_change", "changes": 0}

    diff_count = sum(1 for a, b in zip(original.split("\n"), content.split("\n"), strict=False) if a != b)

    if dry_run:
        return {"file": new_path, "status": "would_update", "changes": diff_count}

    tmp_path = f"{full_path}.{os.getpid()}.tmp"
    try:
        Path(tmp_path).write_text(content, encoding="utf-8")
        os.replace(tmp_path, full_path)
        return {"file": new_path, "status": "updated", "changes": diff_count}
    except PermissionError:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
        return {"file": new_path, "status": "write_error", "changes": 0}


def update_headers_in_file(new_path: str, subdir: str, dry_run: bool = False) -> dict:
    full_path = PROJECT_ROOT / new_path
    if not full_path.exists() or not full_path.is_file():
        return {"file": new_path, "status": "missing", "changes": 0}

    if subdir not in SUBDIR_TO_NEW_MODULE_PREFIX:
        return {"file": new_path, "status": "skipped", "reason": "no_mapping", "changes": 0}

    new_module_prefix = SUBDIR_TO_NEW_MODULE_PREFIX[subdir]
    old_module_prefix = f"{OLD_PREFIX}{subdir}."

    try:
        content = full_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        return {"file": new_path, "status": "read_error", "reason": str(e), "changes": 0}

    original = content

    content = re.sub(
        r"# \[MODULE\] " + re.escape(old_module_prefix),
        f"# [MODULE] {new_module_prefix}",
        content,
    )

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


def fix_external_refs(subdir: str | None = None, dry_run: bool = False) -> tuple[int, int]:
    updated = 0
    errors = 0

    refs_to_fix = {}
    if subdir:
        old_ref = f"{OLD_PREFIX}{subdir}."
        new_ref = SUBDIR_TO_NEW_MODULE_PREFIX.get(subdir, "")
        if new_ref:
            refs_to_fix[old_ref] = new_ref
    else:
        refs_to_fix = dict(CROSS_REFS)

    if not refs_to_fix:
        print("  No references to fix.")
        return 0, 0

    scan_dirs = [
        PROJECT_ROOT / "src",
        PROJECT_ROOT / "scripts",
        PROJECT_ROOT / "tests",
    ]
    py_files = []
    for scan_dir in scan_dirs:
        if not scan_dir.exists():
            continue
        for root, dirs, files in os.walk(scan_dir):
            dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
            for f in files:
                if f.endswith(".py"):
                    py_files.append(os.path.join(root, f))

    def _fix_file(filepath: str) -> dict:
        try:
            with open(filepath, encoding="utf-8") as fh:
                content = fh.read()
        except (OSError, UnicodeDecodeError):
            return {"file": filepath, "status": "read_error", "changes": 0}

        original = content
        for old_ref, new_ref in refs_to_fix.items():
            content = content.replace(old_ref, new_ref)

        if content == original:
            return {"file": filepath, "status": "no_change", "changes": 0}

        diff_count = sum(1 for a, b in zip(original.split("\n"), content.split("\n"), strict=False) if a != b)

        if dry_run:
            return {"file": filepath, "status": "would_update", "changes": diff_count}

        tmp_path = f"{filepath}.{os.getpid()}.tmp"
        try:
            Path(tmp_path).write_text(content, encoding="utf-8")
            os.replace(tmp_path, filepath)
            return {"file": filepath, "status": "updated", "changes": diff_count}
        except PermissionError:
            try:
                os.remove(tmp_path)
            except OSError:
                pass
            return {"file": filepath, "status": "write_error", "changes": 0}

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(_fix_file, fp): fp for fp in py_files}
        for future in as_completed(futures):
            result = future.result()
            if result["status"] in ("updated", "would_update"):
                updated += 1
            elif result["status"] == "write_error":
                errors += 1
                print(f"  ERROR: {result['file']}")

    return updated, errors


def execute_move_batch(entries: list[dict], dry_run: bool = False, force: bool = False) -> tuple[int, int, int]:
    success = 0
    failed = 0
    skipped = 0

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {}
        for e in entries:
            old_path = e.get("old_path", "")
            new_path = e.get("new_path", "")
            if not old_path or not new_path:
                continue
            futures[executor.submit(move_file, old_path, new_path, dry_run, force)] = e

        for future in as_completed(futures):
            result = future.result()
            st = result["status"]
            if st == "moved" or st == "would_move" or st == "overwritten" or st == "would_overwrite":
                success += 1
            elif st == "skipped":
                skipped += 1
            else:
                failed += 1
                print(f"  FAILED: {result['old']} -> {result.get('reason', '')}")

    return success, failed, skipped


def execute_import_updates(entries: list[dict], dry_run: bool = False) -> tuple[int, int]:
    updated = 0
    errors = 0

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {}
        for e in entries:
            new_path = e.get("new_path", "")
            subdir = determine_subdir(e.get("old_path", ""))
            if not new_path or not subdir:
                continue
            futures[executor.submit(update_imports_in_file, new_path, subdir, dry_run)] = e

        for future in as_completed(futures):
            result = future.result()
            if result["status"] in ("updated", "would_update"):
                updated += 1
            elif result["status"] == "no_change":
                pass
            else:
                errors += 1

    return updated, errors


def execute_header_updates(entries: list[dict], dry_run: bool = False) -> tuple[int, int]:
    updated = 0
    errors = 0

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {}
        for e in entries:
            new_path = e.get("new_path", "")
            subdir = determine_subdir(e.get("old_path", ""))
            if not new_path or not subdir:
                continue
            futures[executor.submit(update_headers_in_file, new_path, subdir, dry_run)] = e

        for future in as_completed(futures):
            result = future.result()
            if result["status"] in ("updated", "would_update"):
                updated += 1
            elif result["status"] == "no_change":
                pass
            else:
                errors += 1

    return updated, errors


def update_registry_status(entries: list[dict], dry_run: bool = False) -> int:
    if dry_run:
        print(f"  Would update {len(entries)} entries to status: done")
        return 0

    data = load_registry()
    all_entries = data.get("entries", [])
    old_paths_to_mark = {e.get("old_path", "") for e in entries}

    count = 0
    for e in all_entries:
        if e.get("old_path", "") in old_paths_to_mark and e.get("status") == "pending":
            e["status"] = "done"
            count += 1

    save_registry(data)
    print(f"  Updated {count} entries to status: done")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="DM-311: autonomy_core split migration (cut-paste mode)")
    parser.add_argument("--dry-run", action="store_true", help="Dry run - no actual changes")
    parser.add_argument("--subdir", type=str, help="Only process specific subdirectory (e.g., db, gates, rollback)")
    parser.add_argument("--all", action="store_true", help="Process all autonomy_core subdirectories")
    parser.add_argument("--move", action="store_true", help="Execute file moves (shutil.move)")
    parser.add_argument("--update-imports", action="store_true", help="Update import paths in moved files")
    parser.add_argument("--update-headers", action="store_true", help="Update [MODULE] headers in moved files")
    parser.add_argument(
        "--fix-external-refs", action="store_true", help="Fix external references across the whole project"
    )
    parser.add_argument(
        "--update-registry-status", action="store_true", help="Mark entries as done in migration registry"
    )
    parser.add_argument("--force", action="store_true", help="Force overwrite if target exists with different content")
    args = parser.parse_args()

    if not args.subdir and not args.all and not args.fix_external_refs:
        parser.error("Specify --subdir <name>, --all, or --fix-external-refs")

    need_registry = args.move or args.update_imports or args.update_headers or args.update_registry_status
    data = None
    entries = []

    if need_registry:
        data = load_registry()
        entries = get_autonomy_core_entries(data, subdir=args.subdir if args.subdir else None)

    subdirs_found = set()
    for e in entries:
        sd = determine_subdir(e.get("old_path", ""))
        if sd:
            subdirs_found.add(sd)

    print("=== DM-311: autonomy_core Split Migration ===")
    print(f"Entries: {len(entries)}")
    if subdirs_found:
        print(f"Subdirectories: {', '.join(sorted(subdirs_found))}")
    if args.dry_run:
        print("(dry-run mode)")

    if args.move:
        print("\n--- Moving files (cut-paste) ---")
        success, failed, skipped = execute_move_batch(entries, args.dry_run, args.force)
        print(f"  Moved: {success}, Failed: {failed}, Skipped: {skipped}")
        if failed > 0:
            sys.exit(1)

    if args.update_imports:
        print("\n--- Updating imports in moved files ---")
        updated, errors = execute_import_updates(entries, args.dry_run)
        print(f"  Updated: {updated}, Errors: {errors}")
        if errors > 0:
            sys.exit(1)

    if args.update_headers:
        print("\n--- Updating headers ---")
        updated, errors = execute_header_updates(entries, args.dry_run)
        print(f"  Updated: {updated}, Errors: {errors}")
        if errors > 0:
            sys.exit(1)

    if args.fix_external_refs:
        print("\n--- Fixing external references ---")
        subdir_for_refs = args.subdir if args.subdir else None
        updated, errors = fix_external_refs(subdir_for_refs, args.dry_run)
        print(f"  Files updated: {updated}, Errors: {errors}")
        if errors > 0:
            sys.exit(1)

    if args.update_registry_status:
        print("\n--- Updating registry status ---")
        update_registry_status(entries, args.dry_run)

    if not (
        args.move or args.update_imports or args.update_headers or args.fix_external_refs or args.update_registry_status
    ):
        print(
            "\nNo action specified. Use --move, --update-imports, --update-headers, --fix-external-refs, or --update-registry-status"
        )

    print("\nDone.")


if __name__ == "__main__":
    main()
