#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
彻底清理重复的YAML头部 - 最终版
"""

import re
from pathlib import Path
from datetime import datetime

FACTOR_LIBRARY = Path(r'D:\ZephyrAlpha\docs\02_FACTOR_LIBRARY')
OUTPUT_DIR = Path(r'D:\ZephyrAlpha\docs\09_AUDIT\STATE')

def clean_yaml_headers(file_path):
    """彻底清理重复的YAML头部"""
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        # 使用正则表达式找到所有YAML块
        yaml_pattern = r'^---\s*\n(.*?)\n---\s*'
        matches = list(re.finditer(yaml_pattern, content, re.DOTALL | re.MULTILINE))
        
        if len(matches) > 1:
            print(f"\n{file_path.relative_to(FACTOR_LIBRARY)}")
            print(f"  发现{len(matches)}个YAML头部")
            
            # 保留最后一个YAML头部
            last_match = matches[-1]
            
            # 删除之前的所有YAML头部
            new_content = content[last_match.start():]
            
            # 清理开头的空白行
            new_content = new_content.lstrip()
            
            # 写入文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            return True
        
        return False
    
    except Exception as e:
        print(f"  错误: {e}")
        return False

def main():
    """主函数"""
    print("=" * 80)
    print("彻底清理重复的YAML头部")
    print("=" * 80)
    
    # 扫描所有md文件
    all_files = list(FACTOR_LIBRARY.rglob('*.md'))
    print(f"\n扫描文件: {len(all_files)}个")
    
    fixed_count = 0
    
    for file_path in all_files:
        if clean_yaml_headers(file_path):
            fixed_count += 1
    
    print("\n" + "=" * 80)
    print("清理完成")
    print("=" * 80)
    print(f"清理文件: {fixed_count}")

if __name__ == '__main__':
    main()
