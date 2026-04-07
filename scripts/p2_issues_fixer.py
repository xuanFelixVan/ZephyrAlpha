#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
P2级别问题修复脚本
修复索引不完整问题
"""

import os
import re
from pathlib import Path
from datetime import datetime

FACTOR_LIBRARY = Path(r'D:\ZephyrAlpha\docs\02_FACTOR_LIBRARY')

def get_md_files(directory):
    """获取目录下的所有.md文件"""
    md_files = []
    for item in directory.iterdir():
        if item.is_file() and item.suffix == '.md' and item.name != 'INDEX.md':
            md_files.append(item.name)
    return sorted(md_files)

def update_index_file(index_path, md_files):
    """更新INDEX.md文件"""
    try:
        with open(index_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        # 检查是否已有目录结构部分
        if '## 📂 目录结构' in content:
            # 找到目录结构部分
            pattern = r'(## 📂 目录结构\s*\n)(.*?)(\n---|\n##)'
            match = re.search(pattern, content, re.DOTALL)
            
            if match:
                # 生成新的目录列表
                new_list = ""
                for md_file in md_files:
                    file_name = md_file.replace('.md', '')
                    new_list += f"- [{file_name}](./{md_file})\n"
                
                # 替换目录结构部分
                new_content = content[:match.start(2)] + new_list + content[match.end(2):]
                
                with open(index_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                return True
        
        return False
    
    except Exception as e:
        print(f"错误: {index_path} - {e}")
        return False

def fix_incomplete_indexes():
    """修复索引不完整的INDEX.md文件"""
    print("\n修复索引不完整问题...")
    
    fixed_count = 0
    
    # 遍历所有INDEX.md文件
    for index_path in FACTOR_LIBRARY.rglob('INDEX.md'):
        parent_dir = index_path.parent
        md_files = get_md_files(parent_dir)
        
        if md_files:
            if update_index_file(index_path, md_files):
                rel_path = index_path.relative_to(FACTOR_LIBRARY)
                print(f"修复: {rel_path} - 添加{len(md_files)}个文档链接")
                fixed_count += 1
    
    return fixed_count

def main():
    """主函数"""
    print("=" * 80)
    print("P2级别问题修复")
    print("=" * 80)
    print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    fixed_count = fix_incomplete_indexes()
    
    print("\n" + "=" * 80)
    print("修复完成")
    print("=" * 80)
    print(f"修复INDEX文件数: {fixed_count}")

if __name__ == '__main__':
    main()
