#!/usr/bin/env python

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
修复重复的module_id
"""

import re
from pathlib import Path
from datetime import datetime

FACTOR_LIBRARY = Path(r'D:\ZephyrAlpha\docs\02_FACTOR_LIBRARY')

def generate_unique_module_id(file_path, existing_ids):
    """生成唯一的module_id"""
    rel_path = file_path.relative_to(FACTOR_LIBRARY)
    parts = rel_path.parts[:-1]  # 去掉文件名
    file_name = file_path.stem
    
    # 基于路径生成module_id
    if not parts:
        base_id = 'FACTOR_LIBRARY'
    else:
        # 提取有意义的部分
        meaningful_parts = []
        for part in parts:
            # 移除数字前缀
            clean_part = re.sub(r'^\d+_', '', part)
            meaningful_parts.append(clean_part.upper())
        
        base_id = '_'.join(meaningful_parts)
    
    # 添加文件名
    if file_name.upper() in ['INDEX', 'README', 'SITEMAP']:
        file_suffix = file_name.upper()
    else:
        # 使用文件名的大写形式
        file_suffix = re.sub(r'[^A-Z0-9]', '_', file_name.upper())
        file_suffix = re.sub(r'_+', '_', file_suffix).strip('_')
    
    # 组合base_id和file_suffix
    if file_suffix:
        module_id = f"{base_id}_{file_suffix}"
    else:
        module_id = base_id
    
    # 确保唯一性
    original_id = module_id
    counter = 1
    while module_id in existing_ids:
        module_id = f"{original_id}_{counter:03d}"
        counter += 1
    
    return module_id

def fix_module_ids():
    """修复重复的module_id"""
    print("=" * 80)
    print("修复重复的module_id")
    print("=" * 80)
    print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 扫描所有文件，收集现有的module_id
    all_files = list(FACTOR_LIBRARY.rglob('*.md'))
    print(f"\n扫描文件: {len(all_files)}个")
    
    # 收集所有module_id
    module_id_map = {}  # module_id -> [file_paths]
    
    for file_path in all_files:
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            
            # 提取module_id
            match = re.search(r'module_id:\s*(\S+)', content)
            if match:
                module_id = match.group(1)
                if module_id not in module_id_map:
                    module_id_map[module_id] = []
                module_id_map[module_id].append(file_path)
        except:
            pass
    
    # 找出重复的module_id
    duplicates = {k: v for k, v in module_id_map.items() if len(v) > 1}
    
    print(f"\n发现重复module_id: {len(duplicates)}个")
    
    # 修复重复的module_id
    fixed_count = 0
    existing_ids = set(module_id_map.keys())
    
    for module_id, file_paths in duplicates.items():
        print(f"\n处理module_id: {module_id}")
        print(f"  重复次数: {len(file_paths)}")
        
        # 保留第一个文件的module_id，修改其他文件
        for i, file_path in enumerate(file_paths[1:], 1):
            try:
                with open(file_path, 'r', encoding='utf-8-sig') as f:
                    content = f.read()
                
                # 生成新的module_id
                new_module_id = generate_unique_module_id(file_path, existing_ids)
                
                # 替换module_id
                new_content = re.sub(
                    r'module_id:\s*\S+',
                    f'module_id: {new_module_id}',
                    content
                )
                
                # 写入文件
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                print(f"  {file_path.relative_to(FACTOR_LIBRARY)}: {module_id} -> {new_module_id}")
                
                existing_ids.add(new_module_id)
                fixed_count += 1
            
            except Exception as e:
                print(f"  错误: {e}")
    
    print("\n" + "=" * 80)
    print("修复完成")
    print("=" * 80)
    print(f"修复文件: {fixed_count}")

if __name__ == '__main__':
    fix_module_ids()
