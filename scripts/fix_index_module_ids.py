#!/usr/bin/env python

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
优化INDEX文件的module_id命名
"""

import re
from pathlib import Path
from datetime import datetime

FACTOR_LIBRARY = Path(r'D:\ZephyrAlpha\docs\02_FACTOR_LIBRARY')
OUTPUT_DIR = Path(r'D:\ZephyrAlpha\docs\09_AUDIT\STATE')

def generate_module_id(file_path):
    """根据文件路径生成唯一的module_id"""
    rel_path = file_path.relative_to(FACTOR_LIBRARY)
    parts = rel_path.parts[:-1]  # 去掉文件名
    
    if not parts:
        return 'FACTOR_LIBRARY_INDEX'
    
    # 将路径转换为module_id
    # 例如: 01_STANDARDS/INDEX.md -> STANDARDS_INDEX
    # 例如: 04_DATA_SOURCE/CONFIG_MANAGEMENT/INDEX.md -> DATA_SOURCE_CONFIG_MANAGEMENT_INDEX
    
    # 提取有意义的部分
    meaningful_parts = []
    for part in parts:
        # 移除数字前缀
        clean_part = re.sub(r'^\d+_', '', part)
        meaningful_parts.append(clean_part.upper())
    
    return '_'.join(meaningful_parts) + '_INDEX'

def fix_module_id(file_path):
    """修复单个INDEX文件的module_id"""
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        # 生成新的module_id
        new_module_id = generate_module_id(file_path)
        
        # 查找现有的module_id
        match = re.search(r'module_id:\s*(\S+)', content)
        if match:
            old_module_id = match.group(1)
            
            # 如果已经是唯一的，跳过
            if old_module_id != 'INDEX' and old_module_id != 'README' and old_module_id != 'BLUEPRINT':
                return False, old_module_id, new_module_id
            
            # 替换module_id
            content = re.sub(r'module_id:\s*\S+', f'module_id: {new_module_id}', content)
            
            # 写入文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True, old_module_id, new_module_id
        
        return False, None, new_module_id
    
    except Exception as e:
        return False, None, str(e)

def main():
    """主函数"""
    print("=" * 80)
    print("优化INDEX文件的module_id命名")
    print("=" * 80)
    
    # 扫描所有INDEX.md文件
    index_files = list(FACTOR_LIBRARY.rglob('INDEX.md'))
    print(f"\n发现INDEX文件: {len(index_files)}个")
    
    fixed_count = 0
    skipped_count = 0
    
    for file_path in index_files:
        rel_path = file_path.relative_to(FACTOR_LIBRARY)
        
        success, old_id, new_id = fix_module_id(file_path)
        
        if success:
            print(f"\n{rel_path}")
            print(f"  {old_id} -> {new_id}")
            fixed_count += 1
        else:
            skipped_count += 1
    
    print("\n" + "=" * 80)
    print("优化完成")
    print("=" * 80)
    print(f"修复文件: {fixed_count}")
    print(f"跳过文件: {skipped_count}")

if __name__ == '__main__':
    main()
