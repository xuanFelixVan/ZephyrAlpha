#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
修复效果验证脚本
验证P2级别问题修复效果
"""

import os
from pathlib import Path
from datetime import datetime

FACTOR_LIBRARY = Path(r'D:\ZephyrAlpha\docs\02_FACTOR_LIBRARY')

def count_files_in_directory(directory):
    """统计目录中的文件数量"""
    count = 0
    for item in directory.iterdir():
        if item.is_file() and item.suffix == '.md':
            count += 1
    return count

def check_index_completeness(index_path, directory):
    """检查INDEX.md是否列出了所有文档"""
    try:
        with open(index_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        # 获取目录下的所有.md文件
        md_files = []
        for item in directory.iterdir():
            if item.is_file() and item.suffix == '.md' and item.name != 'INDEX.md':
                md_files.append(item.name)
        
        # 检查INDEX.md是否包含这些文件
        missing_files = []
        for md_file in md_files:
            if md_file.replace('.md', '') not in content:
                missing_files.append(md_file)
        
        return len(missing_files) == 0, missing_files
    
    except Exception as e:
        return False, [str(e)]

def verify_fix():
    """验证修复效果"""
    print("=" * 80)
    print("修复效果验证")
    print("=" * 80)
    print(f"验证时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    sparse_dirs = []
    incomplete_indexes = []
    
    # 遍历所有子目录
    for subdir in FACTOR_LIBRARY.rglob('*'):
        if subdir.is_dir():
            file_count = count_files_in_directory(subdir)
            
            # 检查稀疏目录（文件数<3）
            if file_count < 3:
                sparse_dirs.append((subdir.relative_to(FACTOR_LIBRARY), file_count))
            
            # 检查索引完整性
            index_path = subdir / 'INDEX.md'
            if index_path.exists():
                is_complete, missing = check_index_completeness(index_path, subdir)
                if not is_complete:
                    incomplete_indexes.append((subdir.relative_to(FACTOR_LIBRARY), missing))
    
    # 输出验证结果
    print("\n" + "=" * 80)
    print("验证结果")
    print("=" * 80)
    
    print(f"\n稀疏目录（文件数<3）: {len(sparse_dirs)}个")
    if sparse_dirs:
        for dir_path, count in sparse_dirs[:10]:  # 只显示前10个
            print(f"  - {dir_path}: {count}个文件")
        if len(sparse_dirs) > 10:
            print(f"  ... 还有{len(sparse_dirs) - 10}个")
    
    print(f"\n索引不完整: {len(incomplete_indexes)}个")
    if incomplete_indexes:
        for dir_path, missing in incomplete_indexes[:10]:  # 只显示前10个
            print(f"  - {dir_path}: 缺失{missing}")
        if len(incomplete_indexes) > 10:
            print(f"  ... 还有{len(incomplete_indexes) - 10}个")
    
    # 总体评估
    print("\n" + "=" * 80)
    print("总体评估")
    print("=" * 80)
    
    if len(sparse_dirs) == 0 and len(incomplete_indexes) == 0:
        print("✅ 所有P2级别问题已修复")
        print("✅ 稀疏目录问题: 已解决")
        print("✅ 索引不完整问题: 已解决")
    else:
        print("⚠️ 仍有部分问题待解决")
        if sparse_dirs:
            print(f"⚠️ 稀疏目录: {len(sparse_dirs)}个")
        if incomplete_indexes:
            print(f"⚠️ 索引不完整: {len(incomplete_indexes)}个")

if __name__ == '__main__':
    verify_fix()
