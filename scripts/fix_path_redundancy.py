#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
批量修复路径引用冗余
优化相对路径，减少目录层级跳转
"""

import os
import re
from pathlib import Path

def optimize_relative_path(source_file, target_path):
    """
    计算从源文件到目标文件的最优相对路径
    
    Args:
        source_file: 源文件路径（绝对路径）
        target_path: 目标路径（可能是相对路径或绝对路径）
    
    Returns:
        优化后的相对路径
    """
    try:
        # 如果目标路径已经是相对路径，需要解析为绝对路径
        if not os.path.isabs(target_path):
            # 获取源文件所在目录
            source_dir = os.path.dirname(source_file)
            # 解析相对路径为绝对路径
            target_abs = os.path.normpath(os.path.join(source_dir, target_path))
        else:
            target_abs = target_path
        
        # 计算相对路径
        source_dir = os.path.dirname(source_file)
        rel_path = os.path.relpath(target_abs, source_dir)
        
        # 统一使用正斜杠
        rel_path = rel_path.replace('\\', '/')
        
        return rel_path
    except Exception as e:
        print(f"Error optimizing path {target_path}: {e}")
        return target_path

def fix_path_redundancy(file_path):
    """修复单个文件的路径引用冗余"""
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        original_content = content
        
        # 查找所有Markdown链接
        # 格式：[text](path) 或 [text](path "title")
        pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        
        def replace_path(match):
            text = match.group(1)
            path = match.group(2)
            
            # 只处理包含多个../的路径
            if path.count('../') >= 3:
                # 优化路径
                optimized = optimize_relative_path(file_path, path)
                if optimized != path:
                    print(f"  {path} -> {optimized}")
                    return f'[{text}]({optimized})'
            
            return match.group(0)
        
        content = re.sub(pattern, replace_path, content)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8-sig') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """主函数"""
    docs_dir = Path("D:/ZephyrAlpha/docs")
    
    # 统计
    total_files = 0
    fixed_files = 0
    
    # 遍历所有Markdown文件
    for md_file in docs_dir.rglob("*.md"):
        total_files += 1
        print(f"\nProcessing: {md_file.relative_to(docs_dir)}")
        if fix_path_redundancy(md_file):
            fixed_files += 1
    
    print(f"\n=== 修复完成 ===")
    print(f"总文件数: {total_files}")
    print(f"修复文件数: {fixed_files}")
    print(f"修复率: {fixed_files/total_files*100:.2f}%")

if __name__ == "__main__":
    main()
