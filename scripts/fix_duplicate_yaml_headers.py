#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复重复YAML头部问题
删除第一个YAML头部，保留第二个YAML头部
"""

import os
import re
from pathlib import Path

def fix_duplicate_yaml_headers(file_path):
    """
    修复重复的YAML头部
    保留第二个YAML头部，删除第一个
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否有重复的YAML头部
        # 模式：---\n...内容...\n---\n\n﻿---\n...内容...\n---
        pattern = r'^---\r?\n(.*?)\r?\n---\r?\n\r?\n﻿---\r?\n(.*?)\r?\n---\r?\n'
        
        match = re.match(pattern, content, re.DOTALL)
        
        if match:
            # 提取第二个YAML头部的内容
            second_yaml_content = match.group(2)
            
            # 构建新的文件内容：保留第二个YAML头部
            new_content = '---\n' + second_yaml_content + '\n---\n' + content[match.end():]
            
            # 写回文件
            with open(file_path, 'w', encoding='utf-8', newline='\n') as f:
                f.write(new_content)
            
            return True, "已修复重复YAML头部"
        else:
            return False, "未发现重复YAML头部"
    
    except Exception as e:
        return False, f"处理失败: {str(e)}"

def main():
    """主函数"""
    # 数据源层目录
    data_source_dir = Path(r'D:\ZephyrAlpha\docs\02_FACTOR_LIBRARY\04_DATA_SOURCE')
    
    # 统计信息
    total_files = 0
    fixed_files = 0
    skipped_files = 0
    error_files = 0
    
    print("=" * 80)
    print("开始修复重复YAML头部...")
    print("=" * 80)
    
    # 遍历所有Markdown文件
    for md_file in data_source_dir.rglob('*.md'):
        total_files += 1
        file_path = str(md_file)
        
        # 尝试修复
        fixed, message = fix_duplicate_yaml_headers(file_path)
        
        if fixed:
            fixed_files += 1
            print(f"✅ [{fixed_files}] {md_file.relative_to(data_source_dir)}: {message}")
        elif "未发现" in message:
            skipped_files += 1
        else:
            error_files += 1
            print(f"❌ {md_file.relative_to(data_source_dir)}: {message}")
    
    # 输出统计信息
    print("\n" + "=" * 80)
    print("修复完成！")
    print("=" * 80)
    print(f"总文件数: {total_files}")
    print(f"已修复: {fixed_files}")
    print(f"无需修复: {skipped_files}")
    print(f"处理失败: {error_files}")
    print(f"修复率: {fixed_files/total_files*100:.1f}%")

if __name__ == '__main__':
    main()
