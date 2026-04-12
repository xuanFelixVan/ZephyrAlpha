#!/usr/bin/env python

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
彻底清理重复的YAML头部 - 最终修复版
处理所有情况
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
        
        # 使用正则表达式查找所有完整的YAML块
        # YAML块格式: ---\n...\n---
        yaml_pattern = r'^---\s*\n(.*?)\n---\s*\n'
        matches = list(re.finditer(yaml_pattern, content, re.DOTALL | re.MULTILINE))
        
        if len(matches) >= 1:
            # 检查是否有多个YAML块
            if len(matches) > 1:
                print(f"\n{file_path.relative_to(FACTOR_LIBRARY)}")
                print(f"  发现{len(matches)}个完整YAML头部")
                
                # 保留最后一个YAML头部
                last_match = matches[-1]
                new_content = content[last_match.start():]
                
                # 写入文件
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                return True
            else:
                # 只有一个YAML块，检查是否有未完成的YAML块
                # 查找所有 --- 行
                dash_lines = []
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if line.strip() == '---':
                        dash_lines.append(i)
                
                if len(dash_lines) > 2:
                    print(f"\n{file_path.relative_to(FACTOR_LIBRARY)}")
                    print(f"  发现{len(dash_lines)}个---行，可能有未完成的YAML块")
                    
                    # 保留最后一个完整的YAML块
                    # 找到最后一个完整的YAML块
                    last_yaml_start = dash_lines[-2] if len(dash_lines) >= 2 else dash_lines[-1]
                    
                    # 从最后一个YAML块开始
                    new_content = '\n'.join(lines[last_yaml_start:])
                    
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
