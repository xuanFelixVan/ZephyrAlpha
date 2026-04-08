#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
文档治理定期检查工具
功能：每周定期检查文档治理状态
"""

import os
import re
import json
from datetime import datetime, timedelta
from pathlib import Path

def check_module_id_uniqueness(root_path):
    """检查module_id唯一性"""
    module_ids = {}
    
    for root, dirs, files in os.walk(root_path):
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv']]
        
        for file in files:
            if not file.endswith('.md'):
                continue
            
            file_path = os.path.join(root, file)
            
            try:
                with open(file_path, 'r', encoding='utf-8-sig') as f:
                    content = f.read()
                
                match = re.search(r'^module_id:\s*(\S+)', content, re.MULTILINE)
                if match:
                    module_id = match.group(1)
                    if module_id in module_ids:
                        module_ids[module_id].append(file_path)
                    else:
                        module_ids[module_id] = [file_path]
            except Exception as e:
                print(f"  ⚠️ 读取失败: {file_path} - {e}")
    
    duplicates = {k: v for k, v in module_ids.items() if len(v) > 1}
    
    return {
        'total_files': sum(len(v) for v in module_ids.values()),
        'unique_ids': len(module_ids),
        'duplicates': duplicates,
        'duplicate_count': len(duplicates)
    }

def check_responsibility_overlap(root_path):
    """检查职责重叠"""
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
                
                match = re.search(r'\*\*核心职责\*\*:\s*(.+)', content)
                if match:
                    responsibility = match.group(1)
                    responsibilities.append({
                        'file': os.path.relpath(file_path, root_path),
                        'responsibility': responsibility
                    })
            except Exception as e:
                print(f"  ⚠️ 读取失败: {file_path} - {e}")
    
    overlaps = []
    for i, r1 in enumerate(responsibilities):
        for j, r2 in enumerate(responsibilities[i+1:], i+1):
            keywords1 = set(re.findall(r'[\u4e00-\u9fa5]+', r1['responsibility']))
            keywords2 = set(re.findall(r'[\u4e00-\u9fa5]+', r2['responsibility']))
            
            overlap = keywords1 & keywords2
            if len(overlap) > 2:
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

def check_blueprint_modules(root_path):
    """检查蓝图模块"""
    blueprint_modules = []
    
    for root, dirs, files in os.walk(root_path):
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv']]
        
        if root == root_path:
            continue
        
        md_files = [f for f in files if f.endswith('.md')]
        
        if 'BLUEPRINT.md' in md_files:
            blueprint_path = os.path.join(root, 'BLUEPRINT.md')
            
            try:
                with open(blueprint_path, 'r', encoding='utf-8-sig') as f:
                    content = f.read()
                
                status_match = re.search(r'^status:\s*(\S+)', content, re.MULTILINE)
                status = status_match.group(1) if status_match else 'Unknown'
                
                blueprint_modules.append({
                    'path': os.path.relpath(root, root_path),
                    'status': status,
                    'file_count': len(md_files)
                })
            except Exception as e:
                print(f"  ⚠️ 读取失败: {blueprint_path} - {e}")
    
    return blueprint_modules

def generate_weekly_report(results, output_path):
    """生成周报"""
    report = f"""# 文档治理周报

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

## 3. 蓝图模块统计

| 状态 | 数量 |
|------|------|
| **Blueprint** | {len([m for m in results['blueprint'] if m['status'] == 'Blueprint'])} |
| **Active** | {len([m for m in results['blueprint'] if m['status'] == 'Active'])} |
| **其他** | {len([m for m in results['blueprint'] if m['status'] not in ['Blueprint', 'Active']])} |

### 蓝图模块列表

"""

    for module in results['blueprint']:
        report += f"- **{module['path']}** ({module['status']}, {module['file_count']}个文件)\n"
    
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

def save_check_history(results, history_path):
    """保存检查历史"""
    history_file = os.path.join(history_path, 'check_history.json')
    
    history = []
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
        except:
            history = []
    
    history.append({
        'timestamp': datetime.now().isoformat(),
        'module_id_duplicates': results['module_id']['duplicate_count'],
        'responsibility_overlaps': results['responsibility']['overlap_count'],
        'blueprint_modules': len(results['blueprint'])
    })
    
    # 只保留最近10次检查记录
    if len(history) > 10:
        history = history[-10:]
    
    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def main():
    """主函数"""
    root_path = r'D:\ZephyrAlpha\docs\02_FACTOR_LIBRARY'
    output_dir = r'D:\ZephyrAlpha\docs\05_IMPLEMENTATION\04_OPERATIONS\audit_state'
    
    print("=" * 80)
    print("文档治理定期检查")
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
    
    # 3. 检查蓝图模块
    print("3. 检查蓝图模块...")
    blueprint_result = check_blueprint_modules(root_path)
    print(f"  蓝图模块数: {len(blueprint_result)}")
    print()
    
    # 生成报告
    results = {
        'module_id': module_id_result,
        'responsibility': responsibility_result,
        'blueprint': blueprint_result
    }
    
    report_path = os.path.join(output_dir, 'DOCUMENT_GOVERNANCE_WEEKLY_REPORT.md')
    generate_weekly_report(results, report_path)
    print(f"✅ 周报已生成: {report_path}")
    
    # 保存检查历史
    save_check_history(results, output_dir)
    print(f"✅ 检查历史已保存")
    print()
    print("=" * 80)
    print("检查完成")
    print("=" * 80)

if __name__ == '__main__':
    main()
