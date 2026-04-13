#!/usr/bin/env python3
"""
低风险目录清理脚本
清理对象: 备份目录、测试目录、空目录
策略: 移动到99_ARCHIVE而非永久删除
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

DOCS_ROOT = Path("d:/ZephyrAlpha/docs")
ARCHIVE_DIR = DOCS_ROOT / "99_ARCHIVE"

# 低风险目录列表
LOW_RISK_DIRS = [
    # 备份目录 (8个)
    "05_-_BAK202604131236",
    "23_Layer_1_BAK202604131236",
    "25_Layer_3__BACKUP_20260413123038",
    "26_Layer_3_BAK202604131236",
    "29_Layer_6_BAK202604131236",
    "31_Layer_7_AI_BAK202604131236",
    "33_Layer_8_BAK202604131236",
    "36_Layer_X_Layer_BAK202604131236",
    # 测试目录 (2个)
    "10_l",
    "11_la",
    # 空目录 (4个)
    "'[Layer]'",
    "00_MANAGEMENT",
    "04_Layer_1_Data_Source",
    "09_DIR_18_",
    "22_layer_1",
    "27_layer_4",
    "28_layer_6",
    "34_layer_9",
    "_QUARANTINE_ZONE_DANGER",
]


def move_to_archive(dir_name: str, dry_run: bool = True) -> bool:
    """将目录移动到归档文件夹"""
    source = DOCS_ROOT / dir_name
    if not source.exists():
        print(f"  [SKIP] 不存在: {dir_name}")
        return True
    
    # 统计文件数
    file_count = len(list(source.rglob("*")))
    
    if dry_run:
        print(f"  [DRY-RUN] 将移动: {dir_name} ({file_count} 个项目)")
        return True
    
    try:
        ARCHIVE_DIR.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        target_name = f"{dir_name}_CLEANED_{timestamp}"
        target = ARCHIVE_DIR / target_name
        
        shutil.move(str(source), str(target))
        print(f"  [OK] 已归档: {dir_name} -> 99_ARCHIVE/{target_name}")
        return True
    except Exception as e:
        print(f"  [ERROR] 失败: {dir_name} - {e}")
        return False


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true", help="实际执行")
    args = parser.parse_args()
    
    dry_run = not args.execute
    mode = "[模拟运行]" if dry_run else "[实际执行]"
    
    print("="*70)
    print(f"低风险目录清理 {mode}")
    print("="*70)
    print(f"目标: 清理 {len(LOW_RISK_DIRS)} 个低风险目录\n")
    
    success_count = 0
    for dir_name in LOW_RISK_DIRS:
        if move_to_archive(dir_name, dry_run):
            success_count += 1
    
    print(f"\n{'='*70}")
    print(f"完成: {success_count}/{len(LOW_RISK_DIRS)}")
    if dry_run:
        print("确认无误后，添加 --execute 参数执行实际清理")
    print("="*70)


if __name__ == "__main__":
    main()
