#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
批量修复YAML头部格式
删除重复的YAML分隔符
"""

import os
import re
from pathlib import Path

def fix_yaml_format(file_path):
    """修复单个文件的YAML格式"""
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        original_content = content
        
        # 修复YAML头部双重分隔符
        # 模式：---\n--- 或 ---\n\n---
        content = re.sub(r'^---\s*\n---', '---', content)
        content = re.sub(r'^---\s*\n\n---', '---', content)
        
        # 修复YAML结尾的双重分隔符
        content = re.sub(r'---\s*\n---\s*$', '---', content)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8-sig') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """主函数"""
    docs_dir = Path("D:/ZephyrAlpha/docs")
    
    # 统计
    total_files = 0
    fixed_files = 0
    
    # 遍历所有Markdown文件
    for md_file in docs_dir.rglob("*.md"):
        total_files += 1
        if fix_yaml_format(md_file):
            fixed_files += 1
            print(f"Fixed: {md_file.relative_to(docs_dir)}")
    
    print(f"\n=== 修复完成 ===")
    print(f"总文件数: {total_files}")
    print(f"修复文件数: {fixed_files}")
    print(f"修复率: {fixed_files/total_files*100:.2f}%")

if __name__ == "__main__":
    main()
