#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
彻底清理重复的YAML头部 - 修复版
处理缺少换行符的情况
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
        
        # 查找所有YAML头部的位置
        yaml_blocks = []
        i = 0
        while i < len(content):
            # 查找 ---
            if content[i:i+3] == '---':
                # 检查是否是YAML块开始
                if i == 0 or content[i-1] == '\n':
                    # 查找结束的 ---
                    end_pos = content.find('\n---', i + 3)
                    if end_pos > i:
                        # 找到结束的 ---
                        yaml_content = content[i:end_pos+4]
                        yaml_blocks.append({
                            'start': i,
                            'end': end_pos + 4,
                            'content': yaml_content
                        })
                        i = end_pos + 4
                    else:
                        i += 1
                else:
                    i += 1
            else:
                i += 1
        
        if len(yaml_blocks) > 1:
            print(f"\n{file_path.relative_to(FACTOR_LIBRARY)}")
            print(f"  发现{len(yaml_blocks)}个YAML头部")
            
            # 保留最后一个YAML头部
            last_block = yaml_blocks[-1]
            
            # 删除之前的所有YAML头部
            new_content = content[last_block['start']:]
            
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
