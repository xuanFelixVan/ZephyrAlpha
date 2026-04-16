#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
审计状态目录 (docs/09_AUDIT/STATE/) 自动化清理脚本 v2.0。

清理逻辑：
1. 永久保留 (PERMANENT)：文件名含 TRIAGE, RESOLUTION, DECISION, CANONICAL, REASONING, MASTER, SITEMAP, INDEX。
2. 核心快照 (LATEST)：每种类型的最新一份文件始终保留（基于前缀）。
3. 过期清理：
   - 临时扫描 (SCAN, SNAPSHOT, ORPHAN, INDEX_HEALTH, SENTINEL_L1, CHECKLIST): 超过 7 天删除。
   - 修复日志 (FIX_REPORT, REPLACEMENT_LOG, MIGRATION, BATCH_FIX, SUPPLEMENT_REPORT): 超过 30 天删除。
   - 审计报告 (AUDIT_REPORT, DEEP_AUDIT): 超过 30 天删除（除非是最新版）。
4. 废弃路径清理：清理 docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/。
"""

import os
import re
import shutil
from datetime import datetime
from pathlib import Path

# 配置
REPO_ROOT = Path(__file__).resolve().parents[2]
STATE_DIR = REPO_ROOT / "docs" / "09_AUDIT" / "STATE"
DEPRECATED_DIR = REPO_ROOT / "docs" / "05_IMPLEMENTATION" / "04_OPERATIONS" / "audit_state"

# 规则定义
PERMANENT_KEYWORDS = ["TRIAGE", "RESOLUTION", "DECISION", "CANONICAL", "REASONING", "MASTER", "SITEMAP", "INDEX"]
SHORT_TERM_DAYS = 30
SHORT_TERM_KEYWORDS = ["FIX_REPORT", "REPLACEMENT_LOG", "MIGRATION", "BATCH_FIX", "SUPPLEMENT_REPORT", "AUDIT_REPORT", "DEEP_AUDIT"]
TEMPORARY_DAYS = 7
TEMPORARY_KEYWORDS = ["SCAN", "SNAPSHOT", "ORPHAN", "INDEX_HEALTH", "SENTINEL_L1", "CHECKLIST", "COLLISIONS", "METADATA_SUPPLEMENT"]

def get_file_date(path: Path) -> datetime:
    # 尝试从文件名提取日期 YYYYMMDD 或 YYYY-MM-DD
    match = re.search(r"(\d{4}-?\d{2}-?\d{2})", path.name)
    if match:
        date_str = match.group(1).replace("-", "")
        try:
            return datetime.strptime(date_str, "%Y%m%d")
        except ValueError:
            pass
    # 否则使用修改时间
    return datetime.fromtimestamp(path.stat().st_mtime)

def get_type_prefix(name: str) -> str:
    # 移除日期后缀和扩展名，提取类型前缀
    # 如 alpha-factor-fix-report-20260407-145855.md -> alpha-factor-fix-report
    # 如 SENTINEL_L1_SCAN_20260416.json -> SENTINEL_L1_SCAN
    name = name.upper()
    name = re.sub(r"_\d{8}.*$", "", name)
    name = re.sub(r"-\d{8}.*$", "", name)
    name = re.sub(r"\.\w+$", "", name)
    return name

def cleanup():
    now = datetime.now()
    deleted_count = 0
    kept_count = 0
    freed_space = 0

    print(f"开始清理审计状态目录: {STATE_DIR}")
    print(f"当前日期: {now.strftime('%Y-%m-%d')}")
    print("-" * 50)

    if not STATE_DIR.exists():
        print("错误: 审计状态目录不存在。")
        return

    # 1. 扫描所有文件并按类型分组以保留最新版
    all_files = [p for p in STATE_DIR.rglob("*") if p.is_file() and p.name != "INDEX.md"]
    files_by_type = {} # type_prefix -> [Path]
    
    for p in all_files:
        prefix = get_type_prefix(p.stem)
        if prefix not in files_by_type:
            files_by_type[prefix] = []
        files_by_type[prefix].append(p)

    # 2. 确定每种类型的最新文件
    latest_files = set()
    for prefix, paths in files_by_type.items():
        latest = max(paths, key=get_file_date)
        latest_files.add(latest)

    # 3. 执行清理逻辑
    for p in all_files:
        file_name = p.name.upper()
        file_date = get_file_date(p)
        age_days = (now - file_date).days
        
        # 核心保留规则
        keep = False
        reason = ""

        if p in latest_files:
            keep = True
            reason = "LATEST"
        elif any(k in file_name for k in PERMANENT_KEYWORDS):
            keep = True
            reason = "PERMANENT"
        elif any(k in file_name for k in SHORT_TERM_KEYWORDS):
            if age_days <= SHORT_TERM_DAYS:
                keep = True
                reason = f"SHORT_TERM (<{SHORT_TERM_DAYS}d)"
        elif any(k in file_name for k in TEMPORARY_KEYWORDS):
            if age_days <= TEMPORARY_DAYS:
                keep = True
                reason = f"TEMPORARY (<{TEMPORARY_DAYS}d)"
        elif age_days <= 30: # 默认保留30天
            keep = True
            reason = "DEFAULT (<30d)"

        if keep:
            kept_count += 1
            # print(f"保留 [{reason}]: {p.name}")
        else:
            freed_space += p.stat().st_size
            # print(f"删除: {p.name} (年龄: {age_days}天)")
            p.unlink()
            deleted_count += 1

    # 4. 清理废弃目录
    if DEPRECATED_DIR.exists():
        print(f"清理废弃目录: {DEPRECATED_DIR}")
        shutil.rmtree(DEPRECATED_DIR)
        print("废弃目录已移除。")

    print("-" * 50)
    print(f"清理完成!")
    print(f"删除文件数: {deleted_count}")
    print(f"保留文件数: {kept_count}")
    print(f"释放空间: {freed_space / 1024 / 1024:.2f} MB")

if __name__ == "__main__":
    cleanup()
