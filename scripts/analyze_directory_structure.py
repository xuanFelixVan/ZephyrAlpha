#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
目录结构分析脚本
分析当前目录结构，识别深层嵌套的目录
"""

import os
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

FACTOR_LIBRARY = Path(r'D:\ZephyrAlpha\docs')
OUTPUT_DIR = Path(r'D:\ZephyrAlpha\docs\09_AUDIT\STATE')

def analyze_directory_structure():
    """分析目录结构"""
    print("=" * 80)
    print("分析目录结构")
    print("=" * 80)
    
    depth_stats = defaultdict(int)
    deep_directories = []
    file_distribution = defaultdict(int)
    
    for item in FACTOR_LIBRARY.rglob('*'):
        if item.is_file() and item.suffix == '.md':
            # 计算深度
            rel_path = item.relative_to(FACTOR_LIBRARY)
            depth = len(rel_path.parts) - 1
            
            depth_stats[depth] += 1
            
            # 记录深层目录（深度>=4）
            if depth >= 4:
                deep_directories.append({
                    'path': str(rel_path),
                    'depth': depth,
                    'parent': str(rel_path.parent)
                })
            
            # 统计文件分布
            if depth > 0:
                top_level = rel_path.parts[0]
                file_distribution[top_level] += 1
    
    print(f"\n深度统计:")
    for depth in sorted(depth_stats.keys()):
        print(f"  深度 {depth}: {depth_stats[depth]} 个文件")
    
    print(f"\n深层目录（深度>=4）: {len(deep_directories)} 个")
    
    print(f"\n文件分布:")
    for top_level, count in sorted(file_distribution.items(), key=lambda x: x[1], reverse=True):
        print(f"  {top_level}: {count} 个文件")
    
    return depth_stats, deep_directories, file_distribution

def generate_refactoring_plan(deep_directories):
    """生成重构方案"""
    print("\n" + "=" * 80)
    print("生成重构方案")
    print("=" * 80)
    
    refactoring_plan = []
    
    # 按父目录分组
    parent_groups = defaultdict(list)
    for item in deep_directories:
        parent_groups[item['parent']].append(item)
    
    print(f"\n需要重构的父目录: {len(parent_groups)} 个")
    
    for parent, items in parent_groups.items():
        # 分析重构策略
        if len(items) >= 3:
            # 如果同一父目录下有3个以上深层文件，建议合并
            refactoring_plan.append({
                'parent': parent,
                'files': [item['path'] for item in items],
                'strategy': 'merge',
                'description': f'合并 {len(items)} 个深层文件到上层目录'
            })
        else:
            # 否则建议移动
            refactoring_plan.append({
                'parent': parent,
                'files': [item['path'] for item in items],
                'strategy': 'move',
                'description': f'移动 {len(items)} 个深层文件到上层目录'
            })
    
    print(f"\n重构方案:")
    for i, plan in enumerate(refactoring_plan[:10], 1):  # 只显示前10个
        print(f"\n{i}. {plan['parent']}")
        print(f"   策略: {plan['strategy']}")
        print(f"   说明: {plan['description']}")
    
    if len(refactoring_plan) > 10:
        print(f"\n... 还有 {len(refactoring_plan) - 10} 个重构方案未显示")
    
    return refactoring_plan

def generate_directory_analysis_report(depth_stats, deep_directories, file_distribution, refactoring_plan):
    """生成目录结构分析报告"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_path = OUTPUT_DIR / f'DIRECTORY_STRUCTURE_ANALYSIS_REPORT_{timestamp}.md'
    
    report_content = f"""---
module_id: DIRECTORY_STRUCTURE_ANALYSIS_REPORT_{timestamp}
version: 1.0.0
status: Active
created_date: {datetime.now().strftime('%Y-%m-%d')}
last_updated: {datetime.now().strftime('%Y-%m-%d')}
owner: 首席文档架构师
standard_type: 分析报告
applicable_scope: 目录结构分析
compliance_level: 专业标准
parent_document: ../INDEX.md
---

# 目录结构分析报告

> **核心职责**: 记录目录结构分析的过程和结果
> **职责边界**: 
> - [OK] 本文档负责：分析记录、重构建议、后续方案
> - [NO] 本文档不负责：重构执行、后续审计执行

---

## 分析概要

**分析时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**分析范围**: 全系统文档目录  
**分析方法**: 自动扫描 + 深度分析  
**分析结论**: 发现部分深层嵌套目录，需要重构

---

## 深度统计

| 深度 | 文件数 | 占比 | 说明 |
|------|--------|------|------|
"""
    
    total_files = sum(depth_stats.values())
    for depth in sorted(depth_stats.keys()):
        count = depth_stats[depth]
        percentage = (count / total_files * 100) if total_files > 0 else 0
        status = '✅ 正常' if depth < 4 else '⚠️ 深层'
        report_content += f"| {depth} | {count} | {percentage:.1f}% | {status} |\n"
    
    report_content += f"""
---

## 深层目录分析

### 深层目录统计

- **总深层目录数**: {len(deep_directories)} 个
- **深层目录定义**: 深度 >= 4 的目录

### 深层目录详情（前20个）

"""
    
    for i, item in enumerate(deep_directories[:20], 1):
        report_content += f"""
**{i}. {item['path']}**
- 深度: {item['depth']}
- 父目录: {item['parent']}

"""
    
    if len(deep_directories) > 20:
        report_content += f"\n... 还有 {len(deep_directories) - 20} 个深层目录未显示\n"
    
    report_content += f"""
---

## 文件分布

### 顶层目录文件分布

| 目录 | 文件数 | 占比 |
|------|--------|------|
"""
    
    for top_level, count in sorted(file_distribution.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total_files * 100) if total_files > 0 else 0
        report_content += f"| {top_level} | {count} | {percentage:.1f}% |\n"
    
    report_content += f"""
---

## 重构方案

### 重构策略

1. **合并策略**: 将同一父目录下的多个深层文件合并到上层目录
2. **移动策略**: 将深层文件移动到上层目录
3. **保留策略**: 保留必要的深层结构

### 重构方案详情（前10个）

"""
    
    for i, plan in enumerate(refactoring_plan[:10], 1):
        report_content += f"""
**{i}. {plan['parent']}**
- 策略: {plan['strategy']}
- 说明: {plan['description']}
- 文件数: {len(plan['files'])}

"""
    
    if len(refactoring_plan) > 10:
        report_content += f"\n... 还有 {len(refactoring_plan) - 10} 个重构方案未显示\n"
    
    report_content += f"""
---

## 后续建议

### 立即行动

1. [ ] 审查重构方案
2. [ ] 制定详细重构计划
3. [ ] 执行重构操作

### 持续改进

1. [ ] 建立目录深度监控机制
2. [ ] 定期检查目录结构
3. [ ] 持续优化目录组织

---

## 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | {datetime.now().strftime('%Y-%m-%d')} | 初始版本，目录结构分析报告 | 首席文档架构师 |
"""
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"\n目录结构分析报告已生成: {report_path}")
    return report_path

if __name__ == '__main__':
    # 分析目录结构
    depth_stats, deep_directories, file_distribution = analyze_directory_structure()
    
    # 生成重构方案
    refactoring_plan = generate_refactoring_plan(deep_directories)
    
    # 生成报告
    report_path = generate_directory_analysis_report(
        depth_stats, deep_directories, file_distribution, refactoring_plan
    )
    
    print("\n" + "=" * 80)
    print("目录结构分析完成")
    print("=" * 80)
    print(f"深层目录: {len(deep_directories)} 个")
    print(f"重构方案: {len(refactoring_plan)} 个")
    print(f"报告位置: {report_path}")
