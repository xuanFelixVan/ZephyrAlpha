#!/usr/bin/env python3
"""
阶段一：低风险清理脚本
清理对象：.bak 文件、空目录、日志文件
策略：移动到归档目录，非永久删除
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path("d:/ZephyrAlpha")
ARCHIVE_ROOT = PROJECT_ROOT / "99_ARCHIVE" / f"PHASE1_CLEANUP_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

def ensure_archive_dir():
    """确保归档目录存在"""
    ARCHIVE_ROOT.mkdir(parents=True, exist_ok=True)
    return ARCHIVE_ROOT

def cleanup_bak_files(dry_run=True):
    """清理 .bak 文件"""
    print("\n" + "="*70)
    print("[PHASE 1.1] 清理 .bak 备份文件")
    print("="*70)

    bak_files = list(PROJECT_ROOT.rglob("*.bak"))
    print(f"[INFO] 发现 {len(bak_files)} 个 .bak 文件")

    if not bak_files:
        print("[OK] 没有 .bak 文件需要清理")
        return 0

    archived = 0
    errors = 0
    total_size = 0

    for bak_file in bak_files:
        try:
            size = bak_file.stat().st_size
            total_size += size

            if dry_run:
                print(f"  [DRY-RUN] {bak_file.relative_to(PROJECT_ROOT)} ({size/1024:.1f} KB)")
            else:
                # 保持目录结构
                rel_path = bak_file.relative_to(PROJECT_ROOT)
                dest_dir = ARCHIVE_ROOT / "bak_files" / rel_path.parent
                dest_dir.mkdir(parents=True, exist_ok=True)
                dest_file = dest_dir / bak_file.name

                shutil.move(str(bak_file), str(dest_file))
                print(f"  [OK] 已归档: {rel_path}")
                archived += 1
        except Exception as e:
            print(f"  [ERROR] {bak_file}: {e}")
            errors += 1

    print(f"\n[SUMMARY] .bak 文件: {archived} 个归档, {errors} 个错误")
    print(f"          总大小: {total_size/(1024*1024):.2f} MB")
    return archived

def cleanup_empty_dirs(dry_run=True):
    """清理空目录"""
    print("\n" + "="*70)
    print("[PHASE 1.2] 清理空目录")
    print("="*70)

    empty_dirs = []
    ignore_dirs = {".git", ".venv", "__pycache__", "99_ARCHIVE"}

    for dir_path in PROJECT_ROOT.rglob("*"):
        if not dir_path.is_dir():
            continue
        if any(ignore in str(dir_path) for ignore in ignore_dirs):
            continue

        try:
            items = list(dir_path.iterdir())
            # 只保留 .gitkeep 也算空目录
            non_gitkeep = [i for i in items if i.name != ".gitkeep"]
            if not non_gitkeep:
                empty_dirs.append(dir_path)
        except:
            pass

    print(f"[INFO] 发现 {len(empty_dirs)} 个空目录")

    if not empty_dirs:
        print("[OK] 没有空目录需要清理")
        return 0

    removed = 0
    errors = 0

    for empty_dir in sorted(empty_dirs, key=lambda x: len(str(x)), reverse=True):
        try:
            if dry_run:
                print(f"  [DRY-RUN] {empty_dir.relative_to(PROJECT_ROOT)}")
            else:
                # 对于空目录，直接删除（因为无内容）
                empty_dir.rmdir()
                print(f"  [OK] 已删除: {empty_dir.relative_to(PROJECT_ROOT)}")
                removed += 1
        except Exception as e:
            print(f"  [ERROR] {empty_dir}: {e}")
            errors += 1

    print(f"\n[SUMMARY] 空目录: {removed} 个删除, {errors} 个错误")
    return removed

def cleanup_log_files(dry_run=True):
    """清理日志文件"""
    print("\n" + "="*70)
    print("[PHASE 1.3] 清理日志文件")
    print("="*70)

    log_files = [
        PROJECT_ROOT / "logs" / "quick_audit.log",
        PROJECT_ROOT / "logs" / "standard_audit.log",
    ]

    # 添加审计日志
    audit_logs = list((PROJECT_ROOT / "docs" / "09_AUDIT" / "STATE" / "overnight_runs").rglob("*.log"))
    log_files.extend(audit_logs)

    log_files = [f for f in log_files if f.exists()]
    print(f"[INFO] 发现 {len(log_files)} 个日志文件")

    if not log_files:
        print("[OK] 没有日志文件需要清理")
        return 0

    archived = 0
    errors = 0
    total_size = 0

    for log_file in log_files:
        try:
            size = log_file.stat().st_size
            total_size += size

            if dry_run:
                print(f"  [DRY-RUN] {log_file.relative_to(PROJECT_ROOT)} ({size/1024:.1f} KB)")
            else:
                rel_path = log_file.relative_to(PROJECT_ROOT)
                dest_dir = ARCHIVE_ROOT / "logs" / rel_path.parent
                dest_dir.mkdir(parents=True, exist_ok=True)
                dest_file = dest_dir / log_file.name

                shutil.move(str(log_file), str(dest_file))
                print(f"  [OK] 已归档: {rel_path}")
                archived += 1
        except Exception as e:
            print(f"  [ERROR] {log_file}: {e}")
            errors += 1

    print(f"\n[SUMMARY] 日志文件: {archived} 个归档, {errors} 个错误")
    print(f"          总大小: {total_size/1024:.1f} KB")
    return archived

def main():
    import argparse
    parser = argparse.ArgumentParser(description="阶段一：低风险清理")
    parser.add_argument("--dry-run", action="store_true", help="模拟执行")
    parser.add_argument("--execute", action="store_true", help="实际执行")
    parser.add_argument("--bak-only", action="store_true", help="仅清理.bak")
    parser.add_argument("--empty-only", action="store_true", help="仅清理空目录")
    parser.add_argument("--logs-only", action="store_true", help="仅清理日志")

    args = parser.parse_args()

    dry_run = not args.execute
    mode = "[DRY-RUN]" if dry_run else "[EXECUTE]"

    print("="*70)
    print(f"阶段一：低风险清理 {mode}")
    print("="*70)

    if not dry_run:
        ensure_archive_dir()
        print(f"[INFO] 归档目录: {ARCHIVE_ROOT}")

    total_archived = 0

    # 执行清理
    if args.bak_only or (not args.empty_only and not args.logs_only):
        total_archived += cleanup_bak_files(dry_run)

    if args.empty_only or (not args.bak_only and not args.logs_only):
        total_archived += cleanup_empty_dirs(dry_run)

    if args.logs_only or (not args.bak_only and not args.empty_only):
        total_archived += cleanup_log_files(dry_run)

    # 总结
    print("\n" + "="*70)
    print("清理完成")
    print("="*70)

    if dry_run:
        print("\n[NOTE] 以上为模拟执行，实际执行请添加 --execute 参数")
        print("      确认无误后运行: python scripts/execute_phase1_cleanup.py --execute")
    else:
        print(f"\n[OK] 共归档 {total_archived} 个项目")
        print(f"[INFO] 归档位置: {ARCHIVE_ROOT}")

    print("="*70)

if __name__ == "__main__":
    main()
