# [BLUEPRINT] MOD-INF-037 | docs/02_enterprise_architecture/domain-model-migration-plan.md | §6.3
# [MODULE] scripts.migration.preflight_check
# [INVARIANTS] 检查4项: 目标无冲突/源文件存在/磁盘空间/无活跃锁; 任何失败->exit 1
# [MODIFY-GUARD] 新增检查项需同步更新TC-6-2验收标准
# [CONSUMERS] TC-6-2预检查步骤
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] batch无效->exit 1; mapping文件缺失->exit 1
# [TESTS] tests/test_preflight_check.py
"""搬家预检查——验证搬家可行性。

用法:
    python scripts/migration/preflight_check.py --batch 1
    python scripts/migration/preflight_check.py --batch 1 --dry-run
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys

from _migration_shared import (
    BATCH_TO_GROUP,
    PROJECT_ROOT,
    filter_by_batch,
    load_mapping,
)


def check_target_conflicts(mappings: list[dict]) -> list[str]:
    errors = []
    for m in mappings:
        tp = m.get("target_path", "")
        if not tp:
            continue
        target = PROJECT_ROOT / tp
        if target.exists() and m.get("change_type") == "moved":
            op = m.get("old_path", "")
            if tp != op:
                if target.is_dir():
                    has_files = any(target.iterdir())
                    if not has_files:
                        continue
                else:
                    if target.suffix == ".py":
                        try:
                            content = target.read_text(encoding="utf-8")
                            if content.strip() == "" or content.strip().startswith("#"):
                                continue
                        except (OSError, UnicodeDecodeError):
                            pass
                errors.append(f"CONFLICT: {tp} already exists (old={op})")
    return errors


def check_source_exists(mappings: list[dict]) -> list[str]:
    errors = []
    warnings = []
    skipped_design = 0
    for m in mappings:
        op = m.get("old_path", "")
        if not op:
            continue
        if m.get("change_type") == "new":
            continue
        if m.get("build_status", "built") != "built":
            skipped_design += 1
            continue
        source = PROJECT_ROOT / op
        if not source.exists():
            is_abbreviated = m.get("type") == "sub_module" or (
                m.get("type") == "module"
                and not op.endswith(".py")
                and not op.endswith("/")
                and len(op.split("/")) <= 4
            )
            if is_abbreviated:
                warnings.append(f"SKIP_ABBREVIATED: {op} (abbreviated path, no physical file)")
            else:
                errors.append(f"MISSING: {op} does not exist on disk")
    if skipped_design:
        print(f"  Skipped {skipped_design} design-state modules (build_status != built)")
    if warnings:
        print(f"  {len(warnings)} abbreviated path warnings (will be skipped during move)")
    return errors


def check_disk_space(mappings: list[dict]) -> list[str]:
    errors = []
    total_size = 0
    for m in mappings:
        op = m.get("old_path", "")
        if not op:
            continue
        source = PROJECT_ROOT / op
        if source.is_file():
            total_size += source.stat().st_size
        elif source.is_dir():
            for f in source.rglob("*"):
                if f.is_file():
                    try:
                        total_size += f.stat().st_size
                    except OSError:
                        pass
    disk_usage = shutil.disk_usage(PROJECT_ROOT)
    required = total_size * 2
    if disk_usage.free < required:
        errors.append(f"SPACE: need {required / 1024 / 1024:.0f} MB, available {disk_usage.free / 1024 / 1024:.0f} MB")
    return errors


def check_no_active_locks() -> list[str]:
    errors = []
    lock_script = PROJECT_ROOT / "scripts" / "lock_files.py"
    if not lock_script.exists():
        return errors
    try:
        result = subprocess.run(
            [sys.executable, str(lock_script), "status"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        output = result.stdout + result.stderr
        if "LOCKED" in output or "locked" in output.lower():
            for line in output.splitlines():
                if "locked" in line.lower() or "LOCKED" in line:
                    errors.append(f"LOCK: {line.strip()}")
    except (subprocess.TimeoutExpired, OSError):
        errors.append("LOCK: could not check lock status")
    return errors


def run_preflight(batch: int, dry_run: bool = False) -> int:
    group = BATCH_TO_GROUP.get(batch, "unknown")
    print(f"=== Preflight Check: Batch {batch} ({group}) ===")
    if dry_run:
        print("(dry-run mode)")

    mappings = load_mapping()
    batch_mappings = filter_by_batch(mappings, batch)
    if not batch_mappings:
        print(f"[WARN] No mappings found for batch {batch}")
        return 0

    print(f"Mappings to check: {len(batch_mappings)}")

    all_errors = []

    print("\n--- Check 1: Target path conflicts ---")
    errors1 = check_target_conflicts(batch_mappings)
    all_errors.extend(errors1)
    print(f"  Result: {len(errors1)} conflicts" if errors1 else "  Result: OK")

    print("\n--- Check 2: Source files exist ---")
    errors2 = check_source_exists(batch_mappings)
    all_errors.extend(errors2)
    print(f"  Result: {len(errors2)} missing" if errors2 else "  Result: OK")

    print("\n--- Check 3: Disk space ---")
    errors3 = check_disk_space(batch_mappings)
    all_errors.extend(errors3)
    print(f"  Result: {errors3[0]}" if errors3 else "  Result: OK")

    print("\n--- Check 4: No active locks ---")
    errors4 = check_no_active_locks()
    all_errors.extend(errors4)
    print(f"  Result: {len(errors4)} locks" if errors4 else "  Result: OK")

    print(f"\n=== Summary: {len(all_errors)} total errors ===")
    if all_errors:
        for e in all_errors[:20]:
            print(f"  {e}")
        if len(all_errors) > 20:
            print(f"  ... and {len(all_errors) - 20} more")
        return 1

    print("PREFLIGHT PASSED")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Migration preflight check")
    parser.add_argument("--batch", type=int, required=True, help="Batch number (1-4)")
    parser.add_argument("--dry-run", action="store_true", help="Dry run mode")
    args = parser.parse_args()
    sys.exit(run_preflight(args.batch, args.dry_run))


if __name__ == "__main__":
    main()
