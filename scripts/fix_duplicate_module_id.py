#!/usr/bin/env python

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
修复module_id重复问题
功能：删除文档中重复的YAML块，保留唯一且正确的module_id
"""

import os
import re
from pathlib import Path

def fix_duplicate_yaml_blocks(file_path):
    """
    修复文件中的重复YAML块
    
    Args:
        file_path: 文件路径
    
    Returns:
        bool: 是否进行了修复
    """
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
    except Exception as e:
        print(f"  ❌ 读取失败: {e}")
        return False
    
    # 检查是否有重复的YAML块
    # 模式：---\n...YAML内容...\n---\n\n[BOM]---\n...YAML内容...\n---
    # 注意：可能有BOM字符（\ufeff）在两个YAML块之间
    pattern = r'^---\s*\n(.*?)\n---\s*\n+\ufeff?---\s*\n(.*?)\n---'
    
    match = re.match(pattern, content, re.DOTALL)
    
    if not match:
        return False
    
    yaml1 = match.group(1)
    yaml2 = match.group(2)
    
    # 提取两个YAML块中的module_id
    module_id1 = re.search(r'module_id:\s*(\S+)', yaml1)
    module_id2 = re.search(r'module_id:\s*(\S+)', yaml2)
    
    if not module_id1 or not module_id2:
        print(f"  ⚠️ 无法提取module_id")
        return False
    
    id1 = module_id1.group(1)
    id2 = module_id2.group(1)
    
    print(f"  发现重复module_id: {id1} vs {id2}")
    
    # 选择保留哪个YAML块
    # 策略：保留第一个YAML块（通常是正确的）
    # 如果两个module_id相同，保留第一个
    # 如果不同，保留更符合命名规范的那个
    
    # 检查哪个更符合命名规范
    # 好的命名：全大写，包含下划线，有意义的名称
    def score_module_id(module_id):
        score = 0
        if module_id.isupper():
            score += 10
        if '_' in module_id:
            score += 5
        if len(module_id) > 10:
            score += 5
        if any(keyword in module_id for keyword in ['INDEX', 'STANDARDS', 'BACKTEST', 'DATA', 'FACTOR', 'RISK', 'MONITORING', 'MANUAL', 'REGISTRY']):
            score += 10
        return score
    
    score1 = score_module_id(id1)
    score2 = score_module_id(id2)
    
    if score1 >= score2:
        selected_yaml = yaml1
        selected_id = id1
    else:
        selected_yaml = yaml2
        selected_id = id2
    
    print(f"  ✅ 保留module_id: {selected_id}")
    
    # 构建新的文件内容
    # 保留第一个YAML块，删除第二个
    new_content = '---\n' + selected_yaml + '\n---\n' + content[match.end():]
    
    # 写回文件
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    except Exception as e:
        print(f"  ❌ 写入失败: {e}")
        return False

def scan_and_fix_directory(root_path):
    """
    扫描目录并修复所有文件
    
    Args:
        root_path: 根目录路径
    """
    print("=" * 80)
    print("修复module_id重复问题")
    print("=" * 80)
    print()
    
    fixed_count = 0
    total_count = 0
    
    # 扫描所有.md文件
    for root, dirs, files in os.walk(root_path):
        # 排除特定目录
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv']]
        
        for file in files:
            if not file.endswith('.md'):
                continue
            
            file_path = os.path.join(root, file)
            total_count += 1
            
            rel_path = os.path.relpath(file_path, root_path)
            
            # 尝试修复
            if fix_duplicate_yaml_blocks(file_path):
                print(f"✅ 已修复: {rel_path}")
                fixed_count += 1
    
    print()
    print("=" * 80)
    print(f"扫描完成")
    print(f"总文件数: {total_count}")
    print(f"修复文件数: {fixed_count}")
    print("=" * 80)

def main():
    """主函数"""
    root_path = r'D:\ZephyrAlpha\docs\02_FACTOR_LIBRARY'
    scan_and_fix_directory(root_path)

if __name__ == '__main__':
    main()
