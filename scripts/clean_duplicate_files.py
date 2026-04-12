#!/usr/bin/env python

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
清理重复文件脚本
功能：检查并清理文件名重复的文件（小写和大写版本）
"""

import os
import re
import json
import filecmp
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path("D:/ZephyrAlpha")
DOCS_DIR = PROJECT_ROOT / "docs"
OUTPUT_DIR = PROJECT_ROOT / "docs/09_AUDIT/STATE"

def find_duplicate_files():
    """查找重复文件（小写和大写版本）"""
    duplicates = []
    
    for root, dirs, files in os.walk(DOCS_DIR):
        # 排除特定目录
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv']]
        
        # 按文件名分组（忽略大小写）
        file_groups = {}
        for file in files:
            if not file.endswith('.md'):
                continue
            
            # 忽略大小写的文件名
            key = file.upper()
            if key not in file_groups:
                file_groups[key] = []
            file_groups[key].append(file)
        
        # 找出重复的文件组
        for key, group in file_groups.items():
            if len(group) > 1:
                # 检查文件内容是否相同
                file_paths = [os.path.join(root, f) for f in group]
                
                # 比较文件内容
                all_same = True
                for i in range(len(file_paths) - 1):
                    if not filecmp.cmp(file_paths[i], file_paths[i + 1], shallow=False):
                        all_same = False
                        break
                
                duplicates.append({
                    'directory': os.path.relpath(root, DOCS_DIR),
                    'files': group,
                    'file_paths': file_paths,
                    'content_same': all_same
                })
    
    return duplicates

def clean_duplicates(duplicates):
    """清理重复文件"""
    cleaned = []
    failed = []
    
    for dup in duplicates:
        files = dup['files']
        file_paths = dup['file_paths']
        
        # 如果内容相同，删除小写版本
        if dup['content_same']:
            # 找出小写版本
            lowercase_files = [f for f in files if f != f.upper()]
            
            for lower_file in lowercase_files:
                lower_path = os.path.join(DOCS_DIR, dup['directory'], lower_file)
                
                try:
                    os.remove(lower_path)
                    cleaned.append({
                        'directory': dup['directory'],
                        'deleted_file': lower_file,
                        'reason': '内容相同，删除小写版本'
                    })
                except Exception as e:
                    failed.append({
                        'directory': dup['directory'],
                        'file': lower_file,
                        'reason': f'删除失败: {str(e)}'
                    })
        else:
            # 内容不同，保留两个文件但记录
            failed.append({
                'directory': dup['directory'],
                'files': files,
                'reason': '内容不同，需要人工处理'
            })
    
    return cleaned, failed

def main():
    """主函数"""
    print("=" * 80)
    print("清理重复文件")
    print("=" * 80)
    print(f"清理时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 查找重复文件
    print("查找重复文件...")
    duplicates = find_duplicate_files()
    print(f"发现 {len(duplicates)} 组重复文件")
    print()
    
    if not duplicates:
        print("✅ 未发现重复文件")
        print()
        print("=" * 80)
        print("清理完成")
        print("=" * 80)
        return
    
    # 显示重复文件
    print("重复文件列表:")
    for i, dup in enumerate(duplicates[:10], 1):
        print(f"{i}. {dup['directory']}")
        for f in dup['files']:
            print(f"   - {f}")
        print(f"   内容相同: {'是' if dup['content_same'] else '否'}")
    
    if len(duplicates) > 10:
        print(f"... 还有 {len(duplicates) - 10} 组重复文件")
    print()
    
    # 清理重复文件
    print("清理重复文件...")
    cleaned, failed = clean_duplicates(duplicates)
    
    print(f"清理完成: 成功 {len(cleaned)} 个, 失败 {len(failed)} 个")
    print()
    
    if cleaned:
        print("成功清理的文件:")
        for i, item in enumerate(cleaned[:10], 1):
            print(f"  {i}. {item['directory']}/{item['deleted_file']}")
        if len(cleaned) > 10:
            print(f"... 还有 {len(cleaned) - 10} 个文件")
        print()
    
    if failed:
        print("清理失败的文件:")
        for i, item in enumerate(failed[:10], 1):
            print(f"  {i}. {item['directory']}/{item.get('files', [item.get('file')])}")
            print(f"     原因: {item['reason']}")
        if len(failed) > 10:
            print(f"... 还有 {len(failed) - 10} 个文件")
        print()
    
    # 保存结果
    json_path = OUTPUT_DIR / f'clean_duplicates_result_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'total_duplicates': len(duplicates),
            'total_cleaned': len(cleaned),
            'total_failed': len(failed),
            'cleaned': cleaned,
            'failed': failed
        }, f, ensure_ascii=False, indent=2)
    
    print(f"结果已保存至: {json_path}")
    print()
    print("=" * 80)
    print("清理完成")
    print("=" * 80)

if __name__ == '__main__':
    main()
