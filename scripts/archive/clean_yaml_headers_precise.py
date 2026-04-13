#!/usr/bin/env python

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
彻底清理重复的YAML头部 - 精确版
只保留最后一个完整的YAML块
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
        
        lines = content.split('\n')
        
        # 找到所有 --- 行的位置
        dash_positions = []
        for i, line in enumerate(lines):
            if line.strip() == '---':
                dash_positions.append(i)
        
        # 需要至少2个 --- 才能构成一个YAML块
        if len(dash_positions) < 2:
            return False
        
        # 找到最后一个完整的YAML块
        # YAML块: --- ... ---
        # 找到最后两个 --- 之间的内容
        last_yaml_end = dash_positions[-1]
        
        # 找到对应的开始 ---
        # 从后往前找，找到第一个 --- 作为开始
        yaml_start = None
        for i in range(len(dash_positions) - 2, -1, -1):
            # 检查这个 --- 和下一个 --- 之间是否构成YAML块
            potential_start = dash_positions[i]
            potential_end = dash_positions[i + 1]
            
            # 检查是否有YAML内容（包含module_id等）
            yaml_content = '\n'.join(lines[potential_start:potential_end + 1])
            if 'module_id:' in yaml_content or 'version:' in yaml_content:
                yaml_start = potential_start
                break
        
        if yaml_start is None:
            # 没有找到有效的YAML块，使用最后两个 ---
            yaml_start = dash_positions[-2]
        
        # 保留从YAML开始到文件结束的内容
        new_content = '\n'.join(lines[yaml_start:])
        
        # 检查是否有变化
        if new_content == content:
            return False
        
        print(f"\n{file_path.relative_to(FACTOR_LIBRARY)}")
        print(f"  清理重复的YAML头部")
        
        # 写入文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return True
    
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
