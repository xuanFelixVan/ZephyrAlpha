#!/usr/bin/env python

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
文档治理自动化检查工具
功能：module_id唯一性检查、职责重叠检测、稀疏目录预警
"""

import os
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path

def check_module_id_uniqueness(root_path):
    """
    检查module_id唯一性
    
    Args:
        root_path: 根目录路径
    
    Returns:
        dict: 检查结果
    """
    module_ids = defaultdict(list)
    
    for root, dirs, files in os.walk(root_path):
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv']]
        
        for file in files:
            if not file.endswith('.md'):
                continue
            
            file_path = os.path.join(root, file)
            
            try:
                with open(file_path, 'r', encoding='utf-8-sig') as f:
                    content = f.read()
                
                # 提取module_id
                match = re.search(r'^module_id:\s*(\S+)', content, re.MULTILINE)
                if match:
                    module_id = match.group(1)
                    module_ids[module_id].append(file_path)
            except Exception as e:
                print(f"  ⚠️ 读取失败: {file_path} - {e}")
    
    # 检查重复
    duplicates = {k: v for k, v in module_ids.items() if len(v) > 1}
    
    return {
        'total_files': sum(len(v) for v in module_ids.values()),
        'unique_ids': len(module_ids),
        'duplicates': duplicates,
        'duplicate_count': len(duplicates)
    }

def check_responsibility_overlap(root_path):
    """
    检查职责重叠
    
    Args:
        root_path: 根目录路径
    
    Returns:
        dict: 检查结果
    """
    responsibilities = []
    
    for root, dirs, files in os.walk(root_path):
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv']]
        
        for file in files:
            if not file.endswith('.md'):
                continue
            
            file_path = os.path.join(root, file)
            
            try:
                with open(file_path, 'r', encoding='utf-8-sig') as f:
                    content = f.read()
                
                # 提取职责描述
                match = re.search(r'\*\*核心职责\*\*:\s*(.+)', content)
                if match:
                    responsibility = match.group(1)
                    responsibilities.append({
                        'file': os.path.relpath(file_path, root_path),
                        'responsibility': responsibility
                    })
            except Exception as e:
                print(f"  ⚠️ 读取失败: {file_path} - {e}")
    
    # 检查重叠（简单关键词匹配）
    overlaps = []
    for i, r1 in enumerate(responsibilities):
        for j, r2 in enumerate(responsibilities[i+1:], i+1):
            # 提取关键词
            keywords1 = set(re.findall(r'[\u4e00-\u9fa5]+', r1['responsibility']))
            keywords2 = set(re.findall(r'[\u4e00-\u9fa5]+', r2['responsibility']))
            
            # 计算重叠度
            overlap = keywords1 & keywords2
            if len(overlap) > 2:  # 超过2个关键词重叠
                overlaps.append({
                    'file1': r1['file'],
                    'file2': r2['file'],
                    'overlap_keywords': list(overlap)
                })
    
    return {
        'total_files': len(responsibilities),
        'overlaps': overlaps,
        'overlap_count': len(overlaps)
    }

def check_sparse_directories(root_path, threshold=3):
    """
    检查稀疏目录
    
    Args:
        root_path: 根目录路径
        threshold: 文件数阈值
    
    Returns:
        dict: 检查结果
    """
    sparse_dirs = []
    
    for root, dirs, files in os.walk(root_path):
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv']]
        
        if root == root_path:
            continue
        
        # 统计.md文件
        md_files = [f for f in files if f.endswith('.md')]
        
        if len(md_files) < threshold and len(md_files) > 0:
            sparse_dirs.append({
                'path': os.path.relpath(root, root_path),
                'file_count': len(md_files),
                'files': md_files
            })
    
    return {
        'threshold': threshold,
        'sparse_dirs': sparse_dirs,
        'sparse_count': len(sparse_dirs)
    }

def generate_report(results, output_path):
    """生成检查报告"""
    report = f"""# 文档治理自动化检查报告

## 📊 检查概要

- **检查时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **检查范围**: Alpha因子层（02_FACTOR_LIBRARY）

---

## 1. module_id唯一性检查

| 指标 | 结果 |
|------|------|
| **总文件数** | {results['module_id']['total_files']} |
| **唯一ID数** | {results['module_id']['unique_ids']} |
| **重复ID数** | {results['module_id']['duplicate_count']} |

"""
    
    if results['module_id']['duplicates']:
        report += "### 🔴 发现重复的module_id\n\n"
        for module_id, files in results['module_id']['duplicates'].items():
            report += f"**{module_id}**:\n"
            for file in files:
                report += f"  - {os.path.relpath(file, r'D:\ZephyrAlpha\docs\02_FACTOR_LIBRARY')}\n"
            report += "\n"
    else:
        report += "✅ 未发现重复的module_id\n\n"
    
    report += f"""---

## 2. 职责重叠检查

| 指标 | 结果 |
|------|------|
| **检查文件数** | {results['responsibility']['total_files']} |
| **发现重叠** | {results['responsibility']['overlap_count']} |

"""
    
    if results['responsibility']['overlaps']:
        report += "### 🟡 发现职责重叠\n\n"
        for overlap in results['responsibility']['overlaps']:
            report += f"**{overlap['file1']}** vs **{overlap['file2']}**\n"
            report += f"重叠关键词: {', '.join(overlap['overlap_keywords'])}\n\n"
    else:
        report += "✅ 未发现职责重叠\n\n"
    
    report += f"""---

## 3. 稀疏目录检查

| 指标 | 结果 |
|------|------|
| **检测阈值** | 文件数 < {results['sparse']['threshold']} |
| **发现稀疏目录** | {results['sparse']['sparse_count']} |

"""
    
    if results['sparse']['sparse_dirs']:
        report += "### ⚠️ 稀疏目录列表\n\n"
        for d in results['sparse']['sparse_dirs']:
            report += f"- **{d['path']}** ({d['file_count']}个文件)\n"
    else:
        report += "✅ 未发现稀疏目录\n"
    
    report += f"""

---

## 📝 变更记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0.0 | {datetime.now().strftime('%Y-%m-%d')} | 初始版本 |
"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    return report

def main():
    """主函数"""
    root_path = r'D:\ZephyrAlpha\docs\02_FACTOR_LIBRARY'
    output_dir = r'D:\ZephyrAlpha\docs\05_IMPLEMENTATION\04_OPERATIONS\audit_state'
    
    print("=" * 80)
    print("文档治理自动化检查")
    print("=" * 80)
    print()
    
    # 1. 检查module_id唯一性
    print("1. 检查module_id唯一性...")
    module_id_result = check_module_id_uniqueness(root_path)
    print(f"  总文件数: {module_id_result['total_files']}")
    print(f"  唯一ID数: {module_id_result['unique_ids']}")
    print(f"  重复ID数: {module_id_result['duplicate_count']}")
    print()
    
    # 2. 检查职责重叠
    print("2. 检查职责重叠...")
    responsibility_result = check_responsibility_overlap(root_path)
    print(f"  检查文件数: {responsibility_result['total_files']}")
    print(f"  发现重叠: {responsibility_result['overlap_count']}")
    print()
    
    # 3. 检查稀疏目录
    print("3. 检查稀疏目录...")
    sparse_result = check_sparse_directories(root_path)
    print(f"  发现稀疏目录: {sparse_result['sparse_count']}")
    print()
    
    # 生成报告
    results = {
        'module_id': module_id_result,
        'responsibility': responsibility_result,
        'sparse': sparse_result
    }
    
    report_path = os.path.join(output_dir, 'DOCUMENT_GOVERNANCE_AUTO_CHECK_REPORT.md')
    generate_report(results, report_path)
    print(f"✅ 报告已生成: {report_path}")
    print()
    print("=" * 80)
    print("检查完成")
    print("=" * 80)

if __name__ == '__main__':
    main()
