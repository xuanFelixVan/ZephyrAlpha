#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复版本号命名混乱
移除文件名中的版本号，保留在YAML头部
"""

import os
import re
from pathlib import Path

def fix_version_naming(file_path):
    """修复单个文件的版本号命名"""
    try:
        # 获取文件名（不含扩展名）
        file_name = file_path.stem
        file_ext = file_path.suffix
        
        # 检查是否包含版本号
        if not re.search(r'_V\d+', file_name):
            return False
        
        # 移除版本号
        new_name = re.sub(r'_V\d+', '', file_name)
        new_path = file_path.parent / (new_name + file_ext)
        
        # 检查新文件名是否已存在
        if new_path.exists():
            print(f"  ⚠️  跳过（目标文件已存在）: {file_path.name}")
            return False
        
        # 重命名文件
        file_path.rename(new_path)
        print(f"  ✅ 重命名: {file_path.name} -> {new_name + file_ext}")
        return True
        
    except Exception as e:
        print(f"  ❌ 错误: {file_path.name} - {e}")
        return False

def main():
    """主函数"""
    docs_dir = Path("D:/ZephyrAlpha/docs")
    
    # 统计
    total_files = 0
    fixed_files = 0
    
    print("=== 开始修复版本号命名 ===\n")
    
    # 遍历所有Markdown文件
    for md_file in docs_dir.rglob("*.md"):
        # 跳过归档目录和审计报告目录
        if any(keyword in str(md_file) for keyword in ['06_ARCHIVE', '09_ARCHIVE', '99_ARCHIVE', 'audit_state', 'REPORTS']):
            continue
        
        # 检查是否包含版本号
        if re.search(r'_V\d+', md_file.name):
            total_files += 1
            if fix_version_naming(md_file):
                fixed_files += 1
    
    print(f"\n=== 修复完成 ===")
    print(f"总文件数: {total_files}")
    print(f"修复文件数: {fixed_files}")
    print(f"修复率: {fixed_files/total_files*100:.2f}%" if total_files > 0 else "修复率: 0%")

if __name__ == "__main__":
    main()
