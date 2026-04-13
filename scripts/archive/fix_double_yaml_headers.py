#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
"""
修复双YAML头问题
删除第一个错误的YAML头，保留第二个正确的YAML头
"""

import os
import re
from pathlib import Path

def fix_double_yaml_header(file_path):
    """修复双YAML头"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否有双YAML头
    if content.count('---') < 4:
        return False
    
    # 找到第一个YAML头的结束位置
    first_end = content.find('---', 3)
    if first_end == -1:
        return False
    
    # 找到第二个YAML头的开始位置
    second_start = content.find('---', first_end + 3)
    if second_start == -1:
        return False
    
    # 找到第二个YAML头的结束位置
    second_end = content.find('---', second_start + 3)
    if second_end == -1:
        return False
    
    # 提取第二个YAML头的内容
    second_yaml_content = content[second_start+3:second_end].strip()
    
    # 构建新的文件内容
    new_content = '---\n' + second_yaml_content + '\n---\n' + content[second_end+3:]
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return True

def main():
    blueprints_dir = Path(r'd:\ZephyrAlpha\docs\05_IMPLEMENTATION\06_CONSTRUCTION_DOCS\01_BLUEPRINTS')
    
    fixed_count = 0
    
    for md_file in blueprints_dir.glob('*.md'):
        if md_file.name == 'INDEX.md':
            continue
        
        if fix_double_yaml_header(md_file):
            print(f'Fixed: {md_file.name}')
            fixed_count += 1
    
    print(f'\nTotal fixed: {fixed_count} files')

if __name__ == '__main__':
    main()
