#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
批量修复YAML头部格式问题
"""

import re
from pathlib import Path
from datetime import datetime

FACTOR_LIBRARY = Path(r'D:\ZephyrAlpha\docs\02_FACTOR_LIBRARY')
OUTPUT_DIR = Path(r'D:\ZephyrAlpha\docs\09_AUDIT\STATE')

def fix_yaml_format(file_path):
    """修复YAML头部格式问题"""
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        original_content = content
        
        # 1. 修复 --- 在同一行的情况 (如: compliance_level: 专业标准---)
        content = re.sub(r'(\w+:\s*[^\n]+)---', r'\1\n---', content)
        
        # 2. 删除文件开头的单独 ---
        if content.startswith('---\n\n#'):
            # 找到第一个完整的YAML块
            yaml_match = re.search(r'^---\s*\n.*?\n---\s*\n', content, re.DOTALL)
            if yaml_match:
                # 删除第一个 --- 到 YAML块开始之间的内容
                yaml_start = yaml_match.start()
                if yaml_start > 0:
                    content = content[yaml_start:]
        
        # 3. 删除重复的空行
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        if content != original_content:
            print(f"\n{file_path.relative_to(FACTOR_LIBRARY)}")
            
            # 写入文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True
        
        return False
    
    except Exception as e:
        print(f"  错误: {e}")
        return False

def main():
    """主函数"""
    print("=" * 80)
    print("批量修复YAML头部格式问题")
    print("=" * 80)
    
    # 扫描所有md文件
    all_files = list(FACTOR_LIBRARY.rglob('*.md'))
    print(f"\n扫描文件: {len(all_files)}个")
    
    fixed_count = 0
    
    for file_path in all_files:
        if fix_yaml_format(file_path):
            fixed_count += 1
    
    print("\n" + "=" * 80)
    print("修复完成")
    print("=" * 80)
    print(f"修复文件: {fixed_count}")

if __name__ == '__main__':
    main()
