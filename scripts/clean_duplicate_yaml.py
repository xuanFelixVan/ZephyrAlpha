#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理重复YAML头部工具
"""

import re
from pathlib import Path
from datetime import datetime


def clean_duplicate_yaml():
    """清理重复的YAML头部"""
    
    blueprints_dir = Path('docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS')
    
    print('=' * 80)
    print('清理重复YAML头部')
    print('=' * 80)
    
    fixed_count = 0
    
    for md_file in blueprints_dir.glob('*.md'):
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            try:
                with open(md_file, 'r', encoding='gbk') as f:
                    content = f.read()
            except Exception as e:
                print(f'  ❌ 无法读取文件 {md_file.name}: {e}')
                continue
        
        # 检查是否有重复的YAML头部
        yaml_pattern = r'^---\s*\n.*?\n---\s*\n\s*---\s*\n.*?\n---\s*\n'
        
        if re.search(yaml_pattern, content, re.DOTALL):
            # 提取第二个YAML头部（更完整的那个）
            second_yaml_pattern = r'^---\s*\n.*?\n---\s*\n\s*(---\s*\n.*?\n---\s*\n)'
            match = re.search(second_yaml_pattern, content, re.DOTALL)
            
            if match:
                # 保留第二个YAML头部
                second_yaml = match.group(1)
                
                # 移除第一个YAML头部
                content = re.sub(r'^---\s*\n.*?\n---\s*\n\s*', '', content, count=1, flags=re.DOTALL)
                
                # 写回文件
                try:
                    with open(md_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    fixed_count += 1
                    print(f'  ✅ 已修复: {md_file.name}')
                except Exception as e:
                    print(f'  ❌ 无法写入文件 {md_file.name}: {e}')
    
    print('\n' + '=' * 80)
    print(f'清理完成: 修复了{fixed_count}个文件')
    print('=' * 80)


if __name__ == '__main__':
    clean_duplicate_yaml()
