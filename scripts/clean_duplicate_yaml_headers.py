#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
清理重复的YAML头部 - 改进版
"""

import re
from pathlib import Path
from datetime import datetime

FACTOR_LIBRARY = Path(r'D:\ZephyrAlpha\docs\02_FACTOR_LIBRARY')
OUTPUT_DIR = Path(r'D:\ZephyrAlpha\docs\09_AUDIT\STATE')

def clean_duplicate_yaml(file_path):
    """清理重复的YAML头部"""
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        # 查找所有YAML头部的位置
        yaml_starts = []
        yaml_ends = []
        
        lines = content.split('\n')
        in_yaml = False
        yaml_start = -1
        
        for i, line in enumerate(lines):
            if line.strip() == '---':
                if not in_yaml:
                    in_yaml = True
                    yaml_start = i
                else:
                    in_yaml = False
                    yaml_starts.append(yaml_start)
                    yaml_ends.append(i)
        
        if len(yaml_starts) > 1:
            # 有多个YAML头部，保留最后一个
            print(f"\n{file_path.relative_to(FACTOR_LIBRARY)}")
            print(f"  发现{len(yaml_starts)}个YAML头部，清理中...")
            
            # 保留最后一个YAML头部
            last_start = yaml_starts[-1]
            last_end = yaml_ends[-1]
            
            # 构建新内容：从最后一个YAML头部开始
            new_lines = lines[last_start:]
            new_content = '\n'.join(new_lines)
            
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
    print("清理重复的YAML头部")
    print("=" * 80)
    
    # 扫描所有md文件
    all_files = list(FACTOR_LIBRARY.rglob('*.md'))
    print(f"\n扫描文件: {len(all_files)}个")
    
    fixed_count = 0
    
    for file_path in all_files:
        if clean_duplicate_yaml(file_path):
            fixed_count += 1
    
    print("\n" + "=" * 80)
    print("清理完成")
    print("=" * 80)
    print(f"清理文件: {fixed_count}")

if __name__ == '__main__':
    main()
